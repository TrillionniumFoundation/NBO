"""Run fixed jobs in isolated processes; persist every exit status."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse, json, os, subprocess, sys, time
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=3);a=p.parse_args()
jobs=[]
for seed in [11,29,47]:
 for method in ['guarded_nbo','direct']:
  jobs.append((f'ndu_{method}_s{seed}',['ndu','--seed',str(seed),'--method',method]))
 for market in [1,2]:
  jobs.append((f'game_M{market}_s{seed}',['game','--seed',str(seed),'--market',str(market)]))
(R/'logs').mkdir(parents=True,exist_ok=True)
def run(job):
 name,args=job;start=time.perf_counter()
 with (R/'logs'/f'{name}.log').open('w') as log:
  result=subprocess.run([sys.executable,str(R/'code/finite_study.py'),*args],stdout=log,stderr=subprocess.STDOUT,
      env=os.environ|{'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 record=dict(job=name,returncode=result.returncode,seconds=time.perf_counter()-start)
 print(json.dumps(record),flush=True);return record
with ThreadPoolExecutor(max_workers=a.workers) as pool:records=list(pool.map(run,jobs))
(R/'results/finite_execution.json').write_text(json.dumps(records,indent=2)+'\n')
if any(r['returncode'] for r in records):raise SystemExit(1)
