"""Execute the fixed R47 protocol without overwriting observations."""
from pathlib import Path
import hashlib,itertools,json,os,subprocess,sys,time
import constrained as z
R=z.R

def run(cmd,log):
    start=time.perf_counter()
    with log.open('x') as f:result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=os.environ.copy())
    rec={'command':cmd,'returncode':result.returncode,'process_seconds':time.perf_counter()-start}
    z.c.write_new(log.with_suffix('.process.json'),rec)
    if result.returncode:raise RuntimeError('Inspect '+str(log))
    return rec

def main():
    if (R/'results').exists():raise FileExistsError('Use a new study directory; results are immutable')
    for name,digest in json.loads((R/'SOURCE_SHA256.json').read_text()).items():
        assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
    (R/'results').mkdir();(R/'results/constrained').mkdir();(R/'audit').mkdir(exist_ok=True)
    freeze={'protocol_commit':'7d2329406b53047eb6fa35fe366d94f2fcb37a12',
            'source_commit':os.environ.get('GITHUB_SHA','local-pinned-source'),
            'workflow_run':os.environ.get('GITHUB_RUN_ID'),'source_sha256':json.loads((R/'SOURCE_SHA256.json').read_text()),
            'new_training_services':24,'new_training_rungs':72,'direct_groups':40,'direct_contrasts':120,
            'raw_prior_results_modified':False}
    z.c.write_new(R/'audit/EXECUTION_FREEZE.json',freeze)
    completed=[]
    run([sys.executable,str(R/'code/tests.py')],R/'results/tests.log')
    for rep in range(3):
        for cell,(T,p) in enumerate(itertools.product((2,3),(1,4))):
            methods=z.METHODS if (rep+cell)%2==0 else z.METHODS[::-1]
            for method in methods:
                key=f'{method}-T{T}-p{p}-r{rep}'
                cmd=[sys.executable,str(R/'code/constrained.py'),'--method',method,'--horizon',str(T),'--price',str(p),'--repeat',str(rep),'--out',str(R/'results/constrained'/key)]
                completed.append(run(cmd,R/'results'/(key+'.log')))
    run([sys.executable,str(R/'code/deployment.py')],R/'results/deployment.log')
    run([sys.executable,str(R/'code/direct.py')],R/'results/direct.log')
    z.c.write_new(R/'audit/EXECUTION_COMPLETE.json',{'services':len(completed),'records':completed,'direct_groups':40,'direct_contrasts':120})
    print('All declared R47 executions completed.',flush=True)
if __name__=='__main__':main()
