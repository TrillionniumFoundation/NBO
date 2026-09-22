"""R12 adapter: new original-economy price, inherited independent certifiers.
Only declared source substitutions change input/output locations and the price
loop. The exact inherited algorithms and substitution hashes are retained.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, json, os, pathlib, sys, time, traceback, types
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3]
R10=ROOT/'revisions/2026-09-22-r10'
sys.path[:0]=[str(R10/'replication'),str(ROOT/'revisions/2026-09-22-r9/replication')]
import original_policy_certificate as policy
import flexible_dual as dual

def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def replace_once(text,old,new):
 if text.count(old)!=1:raise ValueError('Inherited source contract changed: '+old)
 return text.replace(old,new)

def run(k,out,resolution=256):
 if not np.isfinite(k) or not .5<=k<=8:raise ValueError('Price outside the declared interval')
 out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 if not out.is_relative_to(ROOT/'revisions/2026-09-22-r12'):raise ValueError('Output must be isolated in R12')
 rec={'k':k,'price_hex':float(k).hex(),'status':'running','source_commit':os.environ.get('R12_SOURCE_COMMIT','local-development')}
 dump(out/'status.json',rec);clock=time.perf_counter()
 try:
  with (out/'execution.log').open('w') as log,contextlib.redirect_stdout(log):
   # This is an input warm start, not an optimal-value or policy label.
   seed=min((.5,2.,8.),key=lambda p:abs(p-k));seed_path=R10/f'results/actor_k{seed:g}.json'
   pth=R10/'replication/polish_policy.py';source=pth.read_text()
   source=replace_once(source,"old=json.loads((ROOT/f'revisions/2026-09-22-r9/results/actor_k{k:g}.json').read_text())","old=json.loads(SEED_PATH.read_text())")
   source=replace_once(source,"'parent_policy':f'revisions/2026-09-22-r9/results/actor_k{k:g}.json'","'parent_policy':str(SEED_PATH.relative_to(ROOT))")
   module=types.ModuleType('r12_polish');module.__file__=str(pth);module.SEED_PATH=seed_path
   exec(compile(source,str(pth),'exec'),module.__dict__);module.OUT=out;actor=module.run(k)
   pth2=R10/'replication/dual_pilot.py';fit=pth2.read_text()
   fit=replace_once(fit,'for k in [.5,2,8]:','for k in [PRICE]:')
   fit=replace_once(fit,"root/f'revisions/2026-09-22-r9/results/actor_k{k:g}.json'","OUT/f'actor_k{k:g}.json'")
   fit=replace_once(fit,"root/f'revisions/2026-09-22-r10/results/dual_pilot_k{k:g}.json'","OUT/f'dual_pilot_k{k:g}.json'")
   fit_clock=time.perf_counter();exec(compile(fit,str(pth2),'exec'),{'__file__':str(pth2),'PRICE':k,'OUT':out})
   rec['dual_fitting_seconds']=time.perf_counter()-fit_clock
   rec['inherited_sources']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [pth,pth2,pathlib.Path(policy.__file__),pathlib.Path(dual.__file__)]}
   rec['adapted_source_sha256']={'polish':hashlib.sha256(source.encode()).hexdigest(),'dual_fit':hashlib.sha256(fit.encode()).hexdigest()}
   policy.OUT=out;dual.OUT=out
   cert=policy.run(f'k{k:g}',resolutions=(1024,))
   upper=dual.run(k,resolutions=((resolution//16,resolution),))
  lo=cert['records'][-1]['policy_value_interval'][0];up=upper['records'][-1]['optimal_value_upper']
  rec.update(status='success',L=lo,U=up,B=cert['adjustment_budget_interval'],regret_upper=float(np.nextafter(up-lo,np.inf)),resolution=resolution,actor_path=str((out/f'actor_k{k:g}.json').relative_to(ROOT)))
  if not all(np.isfinite([lo,up,*rec['B']])) or lo>up:raise ValueError('Invalid certificate')
 except Exception as exc:
  rec.update(status='failed',exception=str(exc));(out/'exception.txt').write_text(traceback.format_exc());raise
 finally:
  rec['seconds']=time.perf_counter()-clock
  rec['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name not in {'status.json','process.log'}}
  dump(out/'status.json',rec)
 return rec
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--k',required=True,type=float);p.add_argument('--out',required=True,type=pathlib.Path);p.add_argument('--resolution',default=256,type=int);a=p.parse_args()
 print(json.dumps(run(a.k,a.out,a.resolution)),flush=True)
