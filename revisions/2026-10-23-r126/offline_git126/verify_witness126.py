#!/usr/bin/env python3
"""Test the offline witness in a fresh repository-layout directory, zero fits."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
F='769e3eb3ac08beaa7bb6778c1676f15e1f8d6d2b'
OUT=ROOT/'offline_git126'
start=time.perf_counter()
m=json.loads((OUT/'WITNESS_MANIFEST126.json').read_text())
test=Path(tempfile.mkdtemp(prefix='nbo-r126-offline-check-',dir='/dev/shm' if Path('/dev/shm').is_dir() else None))
revision=test/ROOT.relative_to(REPO)
for row in m['gate_files']:
    p=test/row['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REPO/row['path'],p)
transport=revision/'offline_git126';transport.mkdir()
for name in ('bootstrap126.py','WITNESS_MANIFEST126.json','F126_GATE_OBJECTS.pack'):
    shutil.copyfile(OUT/name,transport/name)
receipts=[]
for index in (1,2):
    p=subprocess.run([sys.executable,str(transport/'bootstrap126.py')],check=True,capture_output=True,text=True,cwd=test)
    report=json.loads(p.stdout);assert report['git_show_files_verified']==184
    assert report['created_repository_identity']==(index==1)
    assert report['existing_refs_HEAD_and_worktree_index_unchanged']
    (OUT/f'BOOTSTRAP_TEST_{index:02d}126.json').write_text(p.stdout)
    receipts.append({'path':f'offline_git126/BOOTSTRAP_TEST_{index:02d}126.json','sha256':hashlib.sha256(p.stdout.encode()).hexdigest()})
modulepath=revision/'code126/independent_fit126.py'
spec=importlib.util.spec_from_file_location('independent_fit126_offline_gate_only',modulepath)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.REPO==test
readback=module.source_gate(F);assert len(readback['verified_files'])==184
assert all(x not in sys.modules for x in ('numpy','scipy'))
(OUT/'FROZEN_GATE_OFFLINE_READBACK126.json').write_text(json.dumps(readback,indent=2,sort_keys=True)+'\n')
remote=subprocess.check_output(['git','-C',str(test),'remote']).decode();assert remote==''
result={'schema':'r126-offline-path-witness-verification-v1','status':'passed','source_commit':F,'fresh_test_repository':str(test),
 'bootstrap_initialization_passed':True,'existing_repository_second_install_passed':True,'both_installations_preserved_refs_HEAD_index':True,
 'exact_git_show_reads_per_installation':184,'actual_frozen_source_gate_reads':184,'frozen_gate_assertions':module.COUNTS,
 'objects':m['object_count'],'pack_bytes':m['pack']['bytes'],'pack_sha256':m['pack']['sha256'],
 'test_repository_remotes':[],'network_used':False,'numerical_libraries_imported':False,'fits':0,'economic_evaluations':0,
 'minimal_witness_not_full_clone':True,'receipts':receipts,'seconds':time.perf_counter()-start,
 'git_version':subprocess.check_output(['git','--version']).decode().strip(),'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT/'OFFLINE_VERIFICATION126.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result))
