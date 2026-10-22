"""Restore exact F243 native bytes from immutable F; never execute economics."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, subprocess, time, traceback
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
F='2f483615c8bc0037e43ec01a16cce05c724f8c60'
MANIFEST='revisions/2026-10-20-r122/SOURCE_FREEZE122.json'
MANIFEST_SHA='eba26439a799392b7553d06fea5f17828c8988b9f72f4e049058771985ac8b0f'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();assert out.is_relative_to(ROOT) and not out.exists();out.mkdir(parents=True)
    tick=time.perf_counter()
    receipt=dict(status='started',source_commit_F=F,source_manifest_sha256=MANIFEST_SHA,reader_sha256=sha(Path(__file__)),started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),stages=[],records=[],new_economic_evaluations=0,new_training=0,new_states=0,new_timing_observations=0,historical_ref_changed=False)
    def save():
        (out/'FROZEN_NATIVE_READBACK122.json').write_text(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+'\n')
    save()
    try:
        data=(REPO/MANIFEST).read_bytes();assert hashlib.sha256(data).hexdigest()==MANIFEST_SHA and data==git('show',F+':'+MANIFEST)
        manifest=json.loads(data);identity=manifest['scientific_files'];assert len(identity)==manifest['source_file_count']==243
        tree={}
        for line in git('ls-tree','-r',F,'--',*sorted(identity)).decode().splitlines():
            meta,name=line.split('\t')
            if name not in identity:continue
            mode,typ,blob=meta.split();assert mode=='100644' and typ=='blob';tree[name]=dict(path=name,git_blob=blob,sha256=identity[name])
        assert set(tree)==set(identity) and manifest['source_bytes']==2900819
        unique=sorted({r['git_blob'] for r in tree.values()});env=dict(os.environ,GIT_NO_LAZY_FETCH='1')
        checked=subprocess.run(['git','cat-file','--batch-check'],cwd=REPO,env=env,input=''.join(x+'\n' for x in unique),capture_output=True,text=True,check=True)
        missing=[line.split()[0] for line in checked.stdout.splitlines() if line.endswith(' missing')]
        receipt['missing_git_blobs_before']=len(missing);save()
        if missing:
            t=time.perf_counter();log=out/'fetch-exact-frozen-blobs.log'
            with log.open('xb') as stream:
                fetched=subprocess.run(['git','fetch','--no-tags','--no-write-fetch-head','--filter=blob:none','origin','--stdin'],cwd=REPO,input=''.join(x+'\n' for x in missing).encode(),stdout=stream,stderr=subprocess.STDOUT)
            receipt['stages'].append(dict(label='fetch_exact_F_blobs',objects=len(missing),exit_code=fetched.returncode,elapsed_seconds=time.perf_counter()-t,log_sha256=sha(log)));save();assert fetched.returncode==0
        sized=subprocess.run(['git','cat-file','--batch-check'],cwd=REPO,env=env,input=''.join(x+'\n' for x in unique),capture_output=True,text=True,check=True)
        sizes={}
        for line in sized.stdout.splitlines():
            blob,typ,size=line.split();assert typ=='blob';sizes[blob]=int(size)
        for row in tree.values():row['bytes']=sizes[row['git_blob']]
        assert sum(r['bytes'] for r in tree.values())==manifest['source_bytes']==2900819
        proc=subprocess.Popen(['git','cat-file','--batch'],cwd=REPO,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        restored=0;identical=0
        for name,row in sorted(tree.items()):
            pure=PurePosixPath(name);assert not pure.is_absolute() and '..' not in pure.parts and pure.as_posix()==name
            target=REPO/name;assert target.resolve().is_relative_to(REPO) and not target.is_symlink()
            proc.stdin.write((row['git_blob']+'\n').encode());proc.stdin.flush();assert proc.stdout.readline().decode().split()==[row['git_blob'],'blob',str(row['bytes'])]
            raw=proc.stdout.read(row['bytes']);assert len(raw)==row['bytes'] and proc.stdout.read(1)==b'\n'
            assert hashlib.sha256(raw).hexdigest()==row['sha256'] and hashlib.sha1(b'blob '+str(row['bytes']).encode()+b'\0'+raw).hexdigest()==row['git_blob']
            if target.exists():assert target.is_file() and target.read_bytes()==raw;identical+=1
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as stream:stream.write(raw)
                restored+=1
            assert sha(target)==row['sha256'];receipt['records'].append(row)
        proc.stdin.close();assert proc.wait()==0
        for row in receipt['records']:assert (REPO/row['path']).stat().st_size==row['bytes'] and sha(REPO/row['path'])==row['sha256']
        receipt.update(status='verified_complete_frozen_native_source',files=len(tree),bytes=sum(r['bytes'] for r in tree.values()),restored_native_files=restored,already_identical_files=identical,all_native_bytes_match_immutable_F=True,scope='New ordinary-byte restoration after the upload/runtime reset; no lost earlier receipt or clock is relabeled.')
    except BaseException:
        receipt.update(status='failed',traceback=traceback.format_exc());raise
    finally:
        receipt.update(finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-tick,cost_clock_components=[dict(category='frozen_source_byte_readback',clock_fields=[['elapsed_seconds']],scope='Actual entire current F243 byte recovery and checking; enclosed fetch clock is not additional.',partial_lower_bound_only=False,overlaps_counted_parent=False)]);save()
    print(json.dumps({k:receipt[k] for k in ['status','files','bytes','restored_native_files','already_identical_files','elapsed_seconds']},sort_keys=True))
if __name__=='__main__':main()
