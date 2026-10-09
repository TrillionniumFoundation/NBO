"""Sequential isolated timing repetitions; all targets decided prospectively."""
from pathlib import Path
import argparse,json,os,platform,subprocess,sys,time
import prospective55 as p
R=p.R

def main(d,T):
    frozen=p.verify();started=time.perf_counter();folder=R/'results55';folder.mkdir(exist_ok=True)
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
                with log.open('w') as out:
                    proc=subprocess.run([sys.executable,str(R/'code/prospective55.py'),'--d',str(d),'--T',str(T),'--kind',method,'--target',str(target),'--repeat',str(repeat)],cwd=R,stdout=out,stderr=subprocess.STDOUT,check=False)
                    out.flush();os.fsync(out.fileno())
                seconds=time.perf_counter()-begin
                service=folder/'services'/key
                rows.append(dict(key=key,returncode=proc.returncode,whole_process_seconds=seconds,
                    serialized_bytes=sum(x.stat().st_size for x in service.rglob('*') if x.is_file()),
                    log_sha256=p.old.digest(log),log=str(log.relative_to(R))))
                p.save(folder/f'process-clocks-d{d}-T{T}.json',dict(d=d,T=T,source_freeze_sha256=frozen,platform=platform.platform(),runs=rows,cohort_seconds_through_last_process=time.perf_counter()-started,frequency_controlled=False,processes_sequential=True))
                print(json.dumps(rows[-1]),flush=True)
                if proc.returncode:print(log.read_text()[-3000:],flush=True)
    bad=[r for r in rows if r['returncode']]
    if bad:raise RuntimeError(f'{len(bad)} executions failed; all partial files and logs retained')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--d',type=int,required=True);parser.add_argument('--T',type=int,required=True);args=parser.parse_args();main(args.d,args.T)
