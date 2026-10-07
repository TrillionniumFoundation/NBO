"""Execute the predeclared catalogue once; completed records are never overwritten."""
from pathlib import Path
import hashlib,itertools,json,os,subprocess,sys,time
import witness as w
R=w.R

def main():
    result=R/'results'
    if result.exists():raise FileExistsError('Use a fresh checkout/output tree for a NEW study: '+str(result))
    result.mkdir();(result/'services').mkdir();(R/'audit').mkdir(exist_ok=True)
    expected={'witness.py':'3c56bbb6fd3f7612b3f089fd0351c6a8af12a55b0bfaaf856e0aef4af6ecae65',
              'tests.py':'8e9ce06f193c4260c3faab26a86495018358998161f63f80cf73c7f5073d49f7'}
    for n,h in expected.items():
        assert hashlib.sha256((R/'code'/n).read_bytes()).hexdigest()==h,n
    sources={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'code').glob('*.py'))}
    freeze={'source_commit':os.environ.get('GITHUB_SHA','local-execution'),'workflow_run':os.environ.get('GITHUB_RUN_ID'),
            'protocol_commit':'62506d4c67b80fe0709d7493775cf555c111315b','source_sha256':sources,
            'ordering':'For each repetition and economy rotate the three methods by (repetition+economy_index) modulo 3.',
            'planned_services':36,'planned_rungs':216,'study_randomness':'none; repetitions measure clocks, not economic draws'}
    w.old.write_new(R/'audit/EXECUTION_FREEZE.json',freeze)
    completed=[]
    for rep in range(3):
        for cell,(T,p) in enumerate(itertools.product((2,4),(1,4))):
            offset=(rep+cell)%3;methods=w.METHODS[offset:]+w.METHODS[:offset]
            for method in methods:
                key=f'{method}-T{T}-p{p}-r{rep}'
                cmd=[sys.executable,str(R/'code/witness.py'),'--method',method,'--horizon',str(T),'--price',str(p),'--repeat',str(rep),'--out',str(result/'services'/key)]
                start=time.perf_counter()
                with (result/(key+'.log')).open('x') as log:
                    proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=os.environ.copy())
                record={'key':key,'returncode':proc.returncode,'process_seconds':time.perf_counter()-start}
                w.old.write_new(result/(key+'.process.json'),record);completed.append(record)
                if proc.returncode:
                    w.old.write_new(R/'audit/EXECUTION_FAILURE.json',{'failed':record,'completed':completed})
                    raise RuntimeError(key)
    w.old.write_new(R/'audit/EXECUTION_COMPLETE.json',{'services':len(completed),'processes':completed})
    print('Completed all 36 services and 216 rungs.',flush=True)

if __name__=='__main__':main()
