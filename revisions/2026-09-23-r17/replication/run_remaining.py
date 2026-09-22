"""Complete remaining original-action comparator and fixed-object audits."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,os,json,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE.parent/'results';env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
def job(cmd,log):
    start=time.perf_counter()
    with open(log,'w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env)
    return {'command':cmd,'returncode':p.returncode,'seconds':time.perf_counter()-start}
def main():
    tasks=[];out=OUT/'unrestricted';out.mkdir(exist_ok=True)
    for method in ['markov_chain','semi_lagrangian']:
        for n,nt,c in [(9,64,[3,3,4]),(17,128,[5,5,6]),(25,256,[7,7,8])]:
            if (out/f'{method}_{n}_complete.json').exists():continue
            tasks.append((['python',str(HERE/'unrestricted_baselines.py'),'--method',method,'--n',str(n),'--nt',str(nt),'--counts',*map(str,c),'--out',str(out)],out/f'{method}_{n}.log'))
    with ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(lambda p:job(*p),tasks))
    (OUT/'remaining_execution.json').write_text(json.dumps(rows,indent=2)+'\n')
    if any(r['returncode'] for r in rows):raise SystemExit(1)
if __name__=='__main__':main()
