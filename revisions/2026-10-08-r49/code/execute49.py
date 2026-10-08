"""Sequential source-frozen construction and conditional direct-cost study."""
from __future__ import annotations
import itertools,subprocess,time
from service49 import *
import direct49

def main():
    if (HERE/'results').exists():raise FileExistsError('A fresh result directory is required')
    if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    freeze=read(HERE/'SOURCE_SHA256.json')
    for name,digest in freeze.items():assert H(HERE/name)==digest,name
    (HERE/'results').mkdir();(HERE/'audit').mkdir(exist_ok=True);ledger=[];start=time.perf_counter()
    def run(args,identity):
        begin=time.perf_counter();p=subprocess.run([sys.executable,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        with (HERE/'audit/execution.log').open('a') as f:f.write(p.stdout);f.flush();os.fsync(f.fileno())
        row={**identity,'process_seconds':time.perf_counter()-begin,'returncode':p.returncode};ledger.append(row);print(json.dumps(row),flush=True)
        if p.returncode:raise RuntimeError(p.stdout[-6000:])
    for rep in range(3):
        for cell,(T,p) in enumerate(itertools.product((2,3),(1,4))):
            order=METHODS[(cell+rep)%3:]+METHODS[:(cell+rep)%3]
            for method in order:
                key=f'{method}-d2-T{T}-p{p}-r{rep}'
                run([str(HERE/'code/service49.py'),'--method',method,'--T',str(T),'--p',str(p),'--repeat',str(rep),'--d','2','--out',str(HERE/'results/services'/key)],{'kind':'construction','key':key})
    for dd,T,rep in itertools.product((3,4),(2,3),range(3)):
        methods=METHODS[:2] if rep%2==0 else METHODS[:2][::-1]
        for method in methods:
            key=f'{method}-d{dd}-T{T}-p1-r{rep}'
            run([str(HERE/'code/service49.py'),'--method',method,'--T',str(T),'--p','1','--repeat',str(rep),'--d',str(dd),'--out',str(HERE/'results/services'/key)],{'kind':'dimension','key':key})
    specs=direct49.catalogue()
    for i,spec in enumerate(specs):run([str(HERE/'code/direct49.py'),'--index',str(i)],{'kind':spec['kind'],'key':spec['key']})
    hashes={str(p.relative_to(HERE)):H(p) for p in sorted((HERE/'results').rglob('*.json'))}
    save(HERE/'audit/EXECUTION_COMPLETE.json',{'source_commit':os.environ.get('GITHUB_SHA','local'),'workflow_run':os.environ.get('GITHUB_RUN_ID'),'protocol_commit':'2e544bfadb91e125c6b7ae9cbc49d70a0be7bb62','source_hashes':freeze,'result_hashes':hashes,'jobs':ledger,'total_seconds':time.perf_counter()-start})
if __name__=='__main__':main()
