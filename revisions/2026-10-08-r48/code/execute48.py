"""One-host sequential source-frozen catalogue executor."""
from __future__ import annotations
import itertools, subprocess, time
from common import *

def main():
    if (R/'results').exists():raise FileExistsError('Use a fresh output directory, never overwrite observations')
    if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    freeze=read(R/'SOURCE_SHA256.json')
    for name,digest in freeze.items():assert H(R/name)==digest,name
    (R/'results').mkdir();(R/'audit').mkdir(exist_ok=True)
    log=R/'audit/execution.log';ledger=[];begin=time.perf_counter()
    def run(args,identity):
        start=time.perf_counter();p=subprocess.run([sys.executable,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        with log.open('a') as f:f.write(p.stdout);f.flush();os.fsync(f.fileno())
        entry={**identity,'process_seconds':time.perf_counter()-start,'returncode':p.returncode};ledger.append(entry)
        print(json.dumps(entry),flush=True)
        if p.returncode:raise RuntimeError(p.stdout[-5000:])
    methods=('compiled-witness','tensor-fvi','adaptive-fvi')
    for rep in range(3):
        for cell,(T,p) in enumerate(itertools.product((2,3),(1,4))):
            order=methods[(cell+rep)%3:]+methods[:(cell+rep)%3]
            for method in order:
                key=f'{method}-d2-T{T}-p{p}-r{rep}';args=[str(R/'code/service.py'),'--method',method,'--d','2','--T',str(T),'--p',str(p),'--repeat',str(rep),'--out',str(R/'results/services'/key)]
                run(args,{'kind':'construction','key':key})
    for d,T,method in itertools.product((3,4),(2,3),methods[:2]):
        key=f'{method}-d{d}-T{T}-p1-r0';run([str(R/'code/service.py'),'--method',method,'--d',str(d),'--T',str(T),'--p','1','--repeat','0','--out',str(R/'results/services'/key)],{'kind':'dimension-stress','key':key})
    for T,p,law,bits in itertools.product((2,3),(1,4),('uniform','1/8','1/2','7/8'),(0,6,10)):
        key=f'T{T}-p{p}-law{law.replace("/","_")}-bits{bits}'
        run([str(R/'code/direct48.py'),'--T',str(T),'--p',str(p),'--law',law,'--bits',str(bits),'--out',str(R/'results/direct'/(key+'.json'))],{'kind':'direct-comparison','key':key})
    run([str(R/'code/diagnostics.py')],{'kind':'diagnostics','key':'compiler-sensors-historical-frontier'})
    hashes={str(p.relative_to(R)):H(p) for p in sorted((R/'results').rglob('*.json'))}
    save(R/'audit/EXECUTION_COMPLETE.json',{'source_commit':os.environ.get('SOURCE_MATERIALIZED_COMMIT',os.environ.get('GITHUB_SHA','local')),'workflow_run':os.environ.get('GITHUB_RUN_ID'),'protocol_commit':'ce166e6feb49796bbc60670bcc36201eec07837b','jobs':ledger,'total_seconds':time.perf_counter()-begin,'result_hashes':hashes,'source_hashes':freeze})
    run([str(R/'code/audit48.py')],{'kind':'audit','key':'reconstruct'})
if __name__=='__main__':main()
