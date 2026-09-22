"""Execute all predeclared paired runs; preserve subprocess logs and exit codes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,os,json,time
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'results';OUT.mkdir(exist_ok=True)
def one(seed,face):
    dest=OUT/f'{"allface" if face else "accessible"}/seed{seed}';dest.parent.mkdir(exist_ok=True)
    cmd=['python',str(HERE/'guided_neural.py'),'--seed',str(seed),'--width',str(16 if seed%2==0 else 32),'--out',str(dest)]
    if face:cmd+=['--all-faces']
    st=time.perf_counter()
    with open(dest.with_suffix('.log'),'w') as f:
        p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
    r={'seed':seed,'all_faces':face,'exitcode':p.returncode,'wall_including_startup':time.perf_counter()-st,'path':str(dest.relative_to(OUT))}
    print(json.dumps(r),flush=True);return r
if __name__=='__main__':
    start=time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as ex:r=list(ex.map(lambda q:one(*q),[(s,f) for s in range(17100,17110) for f in [False,True]]))
    (OUT/'suite_execution.json').write_text(json.dumps({'runs':r,'parallel_workers':4,'elapsed_wall_seconds':time.perf_counter()-start},indent=2)+'\n')
    if any(x['exitcode'] for x in r):raise SystemExit(1)
