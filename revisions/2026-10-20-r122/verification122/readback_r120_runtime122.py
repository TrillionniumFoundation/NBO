"""Restore and hash the complete published R120 baseline; no scientific execution."""
import argparse, datetime as dt, hashlib, json, os, subprocess, time, traceback
from pathlib import Path
R = Path(__file__).resolve().parents[1]
REPO = R.parents[1]
V = 'f06f220aea525088e82228e8e9be4947fb81b1ca'
OLD = R / 'verification_runs122/baseline-r120-recovery01/BASELINE_R120_READBACK122.json'

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter(); old=json.loads(OLD.read_text()); records=old['records']; identity={r['path']:r for r in records}
    receipt={'schema':'nbo.r122.runtime-r120-readback.v1','status':'started','source_commit':V,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'reader_sha256':sha(Path(__file__)),'retained_receipt':str(OLD.relative_to(REPO)),'retained_receipt_sha256':sha(OLD),'stages':[],'records':[],'new_economic_evaluations':0,'new_states':0,'historical_ref_changed':False}
    def save(): (out/'BASELINE_R120_READBACK122.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    save()
    try:
        assert len(identity)==len(records)==1139 and sum(r['bytes'] for r in records)==496525331
        raw=subprocess.check_output(['git','ls-tree','-rl',V,'--','revisions/2026-10-19-r120'],cwd=REPO,text=True)
        tree={}
        for line in raw.splitlines():
            meta,path=line.split('\t');mode,typ,blob,size=meta.split();assert typ=='blob' and mode=='100644';tree[path]={'git_blob':blob,'bytes':int(size)}
        assert set(tree)==set(identity)
        for p,r in identity.items(): assert tree[p]=={k:r[k] for k in ('git_blob','bytes')}
        unique=sorted({r['git_blob'] for r in records});p=subprocess.run(['git','cat-file','--batch-check'],cwd=REPO,input=''.join(x+'\n' for x in unique),capture_output=True,text=True,env=dict(os.environ,GIT_NO_LAZY_FETCH='1'),check=True)
        missing=[line.split()[0] for line in p.stdout.splitlines() if line.endswith(' missing')]
        receipt.update(tree_sha=subprocess.check_output(['git','rev-parse',V+':revisions/2026-10-19-r120'],cwd=REPO,text=True).strip(),missing_git_blobs_before=len(missing))
        save()
        if missing:
            t=time.perf_counter();log=out/'fetch-missing-blobs.log'
            with log.open('xb') as f:
                p=subprocess.run(['git','fetch','--no-tags','--no-write-fetch-head','--filter=blob:none','origin','--stdin'],cwd=REPO,input=''.join(x+'\n' for x in missing).encode(),stdout=f,stderr=subprocess.STDOUT)
            receipt['stages'].append({'stage':'fetch_exact_missing_objects','objects':len(missing),'exit_code':p.returncode,'elapsed_seconds':time.perf_counter()-t,'log_sha256':sha(log)});save();assert p.returncode==0
        proc=subprocess.Popen(['git','cat-file','--batch'],cwd=REPO,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=dict(os.environ,GIT_NO_LAZY_FETCH='1'))
        restored=0; identical=0
        for i,row in enumerate(records):
            name=row['path'];target=REPO/name;assert target.is_relative_to(REPO) and not target.is_symlink()
            proc.stdin.write((row['git_blob']+'\n').encode());proc.stdin.flush();header=proc.stdout.readline().decode().split();assert header==[row['git_blob'],'blob',str(row['bytes'])]
            h=hashlib.sha256();g=hashlib.sha1(b'blob '+str(row['bytes']).encode()+b'\0');remaining=row['bytes'];tmp=None;native=None
            if target.exists():
                assert target.is_file() and target.stat().st_size==row['bytes'];native=target.open('rb');identical+=1
            else:
                target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.r122-recovery-temporary');assert not tmp.exists();native=tmp.open('xb');restored+=1
            try:
                while remaining:
                    b=proc.stdout.read(min(1<<20,remaining));assert b;remaining-=len(b);h.update(b);g.update(b)
                    if tmp is None: assert native.read(len(b))==b
                    else: native.write(b)
                assert proc.stdout.read(1)==b'\n';assert h.hexdigest()==row['sha256'] and g.hexdigest()==row['git_blob']
            finally: native.close()
            if tmp is not None:tmp.rename(target)
            assert sha(target)==row['sha256'];receipt['records'].append(dict(row))
            if (i+1)%100==0:save();print(json.dumps({'verified_files':i+1,'elapsed_seconds':time.perf_counter()-start}),flush=True)
        proc.stdin.close();assert proc.wait()==0
        receipt.update(status='verified_complete_native_baseline',files=len(records),bytes=sum(r['bytes'] for r in records),restored_native_files=restored,already_identical_files=identical,all_native_bytes_match_git=True,scope='Fresh complete ordinary native-byte readback of every file in actual immutable R120 delivery tree. Preserved earlier receipt is a separate earlier execution, not relabeled recovery.')
    except BaseException:
        receipt.update(status='failed',traceback=traceback.format_exc());raise
    finally:
        receipt.update(ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-start,cost_clock_components=[{'category':'baseline_byte_readback','clock_fields':[['elapsed_seconds']],'scope':'Actual entire read-only restoration and verification invocation; subordinate fetch stage is included, never counted again.','partial_lower_bound_only':False,'overlaps_counted_parent':False}]);save()
    print(json.dumps({k:receipt[k] for k in ('status','files','bytes','restored_native_files','already_identical_files','elapsed_seconds')}),flush=True)
if __name__=='__main__':main()
