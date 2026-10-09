"""Corrected execution controller; scientific sources and protocol unchanged.

The initial controller attempted to rewrite an immutable cumulative JSON file.
This controller writes one new checkpoint after each process and one final
aggregate. It never changes training, acceptance, inference or stopping rules.
"""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,tempfile,time
import prospective55 as p
R=p.R

def checkpoint(folder,d,T,frozen,rows,started):
    record=dict(d=d,T=T,source_freeze_sha256=frozen,
        controller_freeze_sha256=p.old.digest(R/'audit/CONTROLLER_FREEZE55B.json'),
        platform=platform.platform(),runs=list(rows),cohort_seconds_through_last_process=time.perf_counter()-started,frequency_controlled=False,processes_sequential=True)
    p.save(folder/f'process-checkpoints-d{d}-T{T}'/f'{len(rows):03d}.json',record)
    return record

def verify():
    frozen=p.verify();record=json.loads((R/'audit/CONTROLLER_FREEZE55B.json').read_text())
    if record['science_freeze_sha256']!=frozen:raise AssertionError('Scientific freeze mismatch')
    for name,h in record['controller_sha256'].items():
        if p.old.digest(R/name)!=h:raise AssertionError('Controller changed: '+name)
    return frozen

def selftest():
    global R
    original=R
    with tempfile.TemporaryDirectory() as tmp:
        R=Path(tmp);(R/'audit').mkdir();p.save(R/'audit/CONTROLLER_FREEZE55B.json',{'test':True})
        started=time.perf_counter();folder=R/'results55';rows=[]
        for i in range(3):
            rows.append(dict(key=f'test-{i}',returncode=0));record=checkpoint(folder,2,1,'test',rows,started)
        p.save(folder/'process-clocks-d2-T1.json',record)
        for i in range(1,4):
            saved=json.loads((folder/'process-checkpoints-d2-T1'/f'{i:03d}.json').read_text())
            if len(saved['runs'])!=i:raise AssertionError('Checkpoint overwritten')
        if len(json.loads((folder/'process-clocks-d2-T1.json').read_text())['runs'])!=3:raise AssertionError('Aggregate incomplete')
    R=original;print('Three immutable clock checkpoints and one final aggregate: passed')

def main(d,T):
    frozen=verify();started=time.perf_counter();folder=R/'results55';folder.mkdir(exist_ok=True)
    logdir=folder/f'logs-d{d}-T{T}';logdir.mkdir(exist_ok=True)
    methods=list(p.KINDS)
    if d==2:methods+=['compiled-witness','tensor-fvi']
    rows=[]
    for repeat in range(p.REPEATS):
        ordered=methods[repeat%len(methods):]+methods[:repeat%len(methods)]
        for target in p.TARGETS:
            for method in ordered:
                key=f'{method}-d{d}-T{T}-q{target.numerator}_{target.denominator}-r{repeat}'
                begin=time.perf_counter();log=logdir/(key+'.log')
                with log.open('x') as out:
                    proc=subprocess.run([sys.executable,str(R/'code/prospective55.py'),'--d',str(d),'--T',str(T),'--kind',method,'--target',str(target),'--repeat',str(repeat)],cwd=R,stdout=out,stderr=subprocess.STDOUT,check=False)
                    out.flush();os.fsync(out.fileno())
                seconds=time.perf_counter()-begin;service=folder/'services'/key
                rows.append(dict(key=key,returncode=proc.returncode,whole_process_seconds=seconds,
                    serialized_bytes=sum(x.stat().st_size for x in service.rglob('*') if x.is_file()),
                    log_sha256=p.old.digest(log),log=str(log.relative_to(R))))
                record=checkpoint(folder,d,T,frozen,rows,started)
                print(json.dumps(rows[-1]),flush=True)
                if proc.returncode:print(log.read_text()[-3000:],flush=True)
    p.save(folder/f'process-clocks-d{d}-T{T}.json',record)
    bad=[r for r in rows if r['returncode']]
    if bad:raise RuntimeError(f'{len(bad)} executions failed; all partial files and logs retained')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--d',type=int);parser.add_argument('--T',type=int);parser.add_argument('--test',action='store_true');args=parser.parse_args()
    if args.test:selftest()
    else:main(args.d,args.T)
