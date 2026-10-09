"""Amended cohort recorder for the unchanged frozen R60 service.

The first run called an exclusive-create writer twice on process-clocks.json.
All individual service methods, algorithms, inference rules and seeds remain
unchanged. This driver uses distinct checkpoints and writes the final ledger
once. The original driver and its attempted outputs are preserved.
"""
from pathlib import Path
import argparse,json,os,random,subprocess,sys,time
import services60 as original
R=original.R;p=original.p;u=original.u;st=original.st

def freeze():
    f=R/'audit/SOURCE_FREEZE60B.json'
    if f.exists():return verify()
    parent=original.verify();files=('code/services60b.py','RECORDING_AMENDMENT60.md')
    st.save(f,dict(parent_freeze_sha256=parent,files_sha256={name:u.digest(R/name) for name in files},scope='Only the parent recorder changes; original mathematical service and fixed design are unchanged. Initial failed attempts retained in attempts/R60-first-run.',utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    return u.digest(f)
def verify():
    path=R/'audit/SOURCE_FREEZE60B.json';v=original.read(path)
    if original.verify()!=v['parent_freeze_sha256']:raise AssertionError('Original R60 freeze changed')
    for name,h in v['files_sha256'].items():
        if u.digest(R/name)!=h:raise AssertionError('Amended recorder changed: '+name)
    return u.digest(path)
def cohort(worker):
    fz=verify();root=original.directory(worker);root.mkdir(parents=True,exist_ok=False);rows=[];rng=random.Random(60733+worker);start=time.perf_counter()
    setup=dict(compilation=original.read(R/'audit/NATIVE_COMPILE60.json'),environment=st.environment())
    for d,T in original.TASKS:
        for seed in original.SEEDS:
            for target in original.TARGETS:
                order=list(original.MODES);rng.shuffle(order)
                for mode in order:
                    name=original.key(mode,d,T,target,seed);log=root/'logs'/(name+'.log');log.parent.mkdir(exist_ok=True);begin=time.perf_counter()
                    with log.open('x') as output:
                        process=subprocess.run([sys.executable,str(R/'code/services60.py'),'--worker',str(worker),'--service','--d',str(d),'--T',str(T),'--mode',mode,'--target',str(target),'--seed',str(seed)],cwd=R,stdout=output,stderr=subprocess.STDOUT,check=False);output.flush();os.fsync(output.fileno())
                    child=time.perf_counter()-begin
                    record=dict(key=name,returncode=process.returncode,process_and_log_seconds=child,log_sha256=u.digest(log),serialized_bytes=sum(f.stat().st_size for f in (root/'services'/name).rglob('*') if f.is_file()),order=order)
                    receipt=root/'receipts'/(name+'.json');p.save(receipt,record);elapsed=time.perf_counter()-begin
                    record.update(complete_return_seconds=elapsed,parent_receipt_seconds=elapsed-child,receipt_sha256=u.digest(receipt),cold_compile_seconds=setup['compilation']['seconds'] if mode in ('relu-native','quadratic-native') else 0.)
                    record['cold_return_seconds']=elapsed+record['cold_compile_seconds'];rows.append(record)
                    p.save(root/'checkpoints'/f'{len(rows):03d}.json',dict(worker=worker,runs=list(rows),source_freeze_sha256=fz))
                    print(json.dumps(record),flush=True)
                    if process.returncode:raise RuntimeError(log.read_text()[-4000:])
                original.paired(worker,d,T,target,seed)
    p.save(root/'process-clocks.json',dict(worker=worker,runs=rows,source_freeze_sha256=fz))
    p.save(root/'cohort.json',dict(status='passed',worker=worker,services=len(rows),source_freeze_sha256=fz,runs=rows,seconds_before_final_ledger=time.perf_counter()-start,compile_record=setup['compilation'],environment=setup['environment'],scope='Original frozen service unchanged. Complete child/log/first-parent-receipt boundary preserved. Exclusive checkpoints avoid overwritten evidence. Two worker executions repeat mathematical objects and are not new independent samples.'))
if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('--freeze',action='store_true');q.add_argument('--worker',type=int,default=0);a=q.parse_args()
    if a.freeze:print(freeze())
    else:cohort(a.worker)
