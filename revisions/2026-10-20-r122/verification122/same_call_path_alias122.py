"""Administrative same-process legacy-path alias for unchanged R122 reporting.

This helper does not edit frozen science, recorded paths, or report adapters.
It preserves an identified task-owned old mirror before replacing that path
with a symlink, then launches the supplied frozen outer launcher as argv.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, resource, shutil, stat
import subprocess, sys, time, traceback, uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PHYSICAL=Path('/dev/shm/nbo-r122-411f2ee67342/NBO')
LEGACY=Path('/workspace/scratch/411f2ee67342/NBO')
REVISION=Path('revisions/2026-10-20-r122')
F='2f483615c8bc0037e43ec01a16cce05c724f8c60'
MANIFEST_SHA='eba26439a799392b7553d06fea5f17828c8988b9f72f4e049058771985ac8b0f'
LAUNCH_SHA='c212ba4c50e890e2875ea4e57461366ccd62938624e3dcfbd0691205e09fc742'

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def write(path,obj):
 with Path(path).open('x') as f:json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')

def inventory(base):
 records=[]
 for path in sorted(base.rglob('*')):
  relative=path.relative_to(base)
  if not (relative==Path('revisions') or relative==REVISION or relative.is_relative_to(REVISION)):
   raise ValueError('Legacy mirror contains an unrelated path: '+str(relative))
  mode=path.lstat().st_mode
  if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
   raise ValueError('Legacy mirror has a symlink or special file: '+str(relative))
  if stat.S_ISREG(mode):
   records.append({'path':str(relative),'bytes':path.stat().st_size,'sha256':sha(path)})
 return records

def check_task_mirror(base):
 if sha(base/REVISION/'SOURCE_FREEZE122.json')!=MANIFEST_SHA or sha(base/REVISION/'code122/launch122.py')!=LAUNCH_SHA:
  raise ValueError('Legacy directory does not match this task source identity')
 records=inventory(base)
 manifest=json.loads((ROOT/'SOURCE_FREEZE122.json').read_text())['scientific_files']
 for row in records:
  if row['path'] in manifest and row['sha256']!=manifest[row['path']]:
   raise ValueError('Legacy mirror contains altered frozen source: '+row['path'])
 return records

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--receipt',required=True,type=Path)
 parser.add_argument('--validate-only',action='store_true')
 parser.add_argument('command',nargs=argparse.REMAINDER)
 a=parser.parse_args();command=a.command[1:] if a.command and a.command[0]=='--' else a.command
 if a.validate_only==bool(command):raise ValueError('Use either --validate-only or one explicit frozen launcher command')
 if REPO!=PHYSICAL or Path.cwd().resolve()!=ROOT:raise ValueError('Run this helper from the canonical physical R122 directory')
 if sha(ROOT/'SOURCE_FREEZE122.json')!=MANIFEST_SHA or sha(ROOT/'code122/launch122.py')!=LAUNCH_SHA:
  raise ValueError('Canonical source gate differs')
 if command:
  if len(command)<6 or Path(command[1]).as_posix()!='code122/launch122.py' or '--' not in command:
   raise ValueError('Exact outer launcher argv required')
  child=command[command.index('--')+1:]
  if len(child)<2 or child[1] not in ('code122/report122.py','verification122/report_protocol_adapter122.py'):
   raise ValueError('This administrative alias is scoped to the declared R122 report commands')
  if '--source-commit' not in child or child[child.index('--source-commit')+1]!=F:
   raise ValueError('Reporting must retain the original F identity')
 out=a.receipt.resolve()
 if not out.is_relative_to(ROOT/'results122'):raise ValueError('Administrative receipt must stay in R122/results122')
 out.mkdir(parents=True,exist_ok=False);tick=time.perf_counter()
 initial={'source_commit_F':F,'helper_sha256':sha(__file__),'helper_path':str(Path(__file__).resolve().relative_to(REPO)),
  'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'physical_repo':str(REPO),'legacy_repo':str(LEGACY),
  'actual_command':command,'validation_only':a.validate_only,'frozen_scientific_files_changed':False,
  'recorded_scientific_paths_changed':False,'clock_scope':'administrative setup and child launcher; helper interpreter startup excluded; nested clocks are not additive'}
 write(out/'START_PATH_ALIAS122.json',initial)
 backup=None;records=[];child_seconds=0.0;checks=0;violations=[];code=None;error=None;status='failed'
 try:
  if LEGACY.is_symlink():
   if LEGACY.resolve()!=REPO:raise ValueError('Refuse to replace an unrelated existing symlink')
  elif LEGACY.exists():
   if not LEGACY.is_dir():raise ValueError('Refuse to replace a non-directory legacy path')
   records=check_task_mirror(LEGACY)
   write(out/'DISPLACED_MIRROR_MANIFEST122.json',{'files':records,'files_count':len(records),'bytes':sum(z['bytes'] for z in records),'all_paths_within_task_revision':True})
   backup=REPO.parent/('recovery-alias-preserved-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex)
   if backup.exists():raise ValueError('Unique recovery destination unexpectedly exists')
   # Move only the fully enumerated task mirror; no other workspace path is touched.
   if inventory(LEGACY)!=records:raise ValueError('Legacy mirror changed during inventory')
   shutil.move(str(LEGACY),str(backup))
   if inventory(backup)!=records:raise ValueError('Preserved mirror byte census differs')
   write(out/'PRESERVED_MIRROR122.json',{'backup_path':str(backup),'files_count':len(records),'bytes':sum(z['bytes'] for z in records),'all_file_hashes_rechecked':True})
  if not LEGACY.exists() and not LEGACY.is_symlink():LEGACY.symlink_to(REPO,target_is_directory=True)
  if not LEGACY.is_symlink() or LEGACY.resolve()!=REPO:raise ValueError('Same-call alias does not resolve to canonical repository')
  checks+=1
  if command:
   child_tick=time.perf_counter()
   with (out/'child_stdout.log').open('x') as log:
    child_process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    while True:
     ok=LEGACY.is_symlink() and LEGACY.resolve()==REPO;checks+=1
     if not ok:violations.append({'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'resolved':str(LEGACY.resolve())})
     code=child_process.poll()
     if code is not None:break
     time.sleep(0.2)
   child_seconds=time.perf_counter()-child_tick
   if violations:raise ValueError('Legacy alias changed while the frozen report child was running; child outputs retained')
  else:code=0
  if LEGACY.resolve()!=REPO:raise ValueError('Alias does not resolve after child completion')
  checks+=1;status='executed' if code==0 else 'child_failed'
 except BaseException:
  error=traceback.format_exc()
 finally:
  elapsed=time.perf_counter()-tick
  result=dict(initial,status=status,exit_code=code,error=error,ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
   helper_seconds=elapsed,child_launcher_seconds=child_seconds,administrative_seconds_excluding_child=elapsed-child_seconds,
   child_clock_nested_in_helper_clock=True,helper_clock_not_additive_with_child_clock=True,
   alias_checks=checks,alias_violations=violations,backup_path=None if backup is None else str(backup),
   displaced_files=len(records),displaced_bytes=sum(z['bytes'] for z in records),
   max_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
   scientific_calls_by_helper=0,all_child_outputs_retained=True)
  write(out/'PATH_ALIAS122.json',result)
  print(json.dumps({k:result[k] for k in ('status','exit_code','helper_seconds','child_launcher_seconds','backup_path','alias_checks')},sort_keys=True),flush=True)
 if status!='executed':raise SystemExit(code if isinstance(code,int) and code>0 else 1)

if __name__=='__main__':main()
