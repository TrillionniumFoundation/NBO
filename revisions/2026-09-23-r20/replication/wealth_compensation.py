"""Budget-financed compensation from the fixed learned consumption shapes.
This deterministic consequence is separate from the predeclared random study.
No policy is retrained: a single budget intercept changes with initial wealth.
"""
from pathlib import Path
from decimal import Decimal
import json,hashlib,time
import numpy as np
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss
from scipy.special import expit
from certify_stochastic import certify,ROOT,upper,I
R=ROOT/'revisions/2026-09-23-r20'
DELTA=Decimal('.002')

def compensate(d):
 n=len(d['b']);tg,tw=leggauss(16);zg,zw=hermgauss(40)
 t=(np.arange(n)[:,None]+(tg+1)/2)/n;wt=tw/(2*n)
 L=.065*t[:,:,None]+.3*np.sqrt(2*t)[:,:,None]*zg
 b=np.asarray(d['b'])[:,None,None];s=np.asarray(d['s'])[:,None,None]
 newx=Decimal(str(d['x0']))+DELTA;target=float(newx)-.50001*np.exp(-.02)
 def price(a):return float(np.sum(np.exp(-.02*t)*wt*np.sum((.5+.3*expit(b+a-s*L))*zw/np.sqrt(np.pi),axis=-1)))
 lo,hi=0.,2.
 assert price(lo)<target<price(hi)
 for _ in range(60):
  mid=(lo+hi)/2
  if price(mid)>target:hi=mid
  else:lo=mid
 offset=(lo+hi)/2
 return {**d,'b':(np.asarray(d['b'])+offset).tolist(),'x0':float(newx),'compensation':str(DELTA),
  'uncompensated_initial_wealth':d['x0'],'budget_offset':offset,
  'construction':'same learned slope/preference shapes; budget-financed intercept shift and residual riskless reserve; no retraining'}

def run():
 out=R/'results/wealth';out.mkdir(parents=True,exist_ok=True);rows=[]
 for seed in range(20100,20105):
  for vertex in range(4):
   source=R/f'results/neural/seed{seed}/vertex{vertex}/actor_1000.json';d=json.loads(source.read_text())
   a=compensate(d);ap=out/f'actor_seed{seed}_vertex{vertex}.json';ap.write_text(json.dumps(a,indent=2)+'\n')
   c=certify(a);ref=upper(d['u0'],d['x0'])
   c.update({'seed':seed,'vertex':vertex,'uncompensated_optimal_upper':ref,
      'compensated_policy_minus_original_optimum_lower':float((I(c['value_interval'][0])-I(ref)).lo),
      'wealth_increment':str(DELTA),'source_actor_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'compensated_actor_sha256':hashlib.sha256(ap.read_bytes()).hexdigest(),'actor_path':str(ap.relative_to(ROOT))})
   rows.append(c);(out/f'certificate_seed{seed}_vertex{vertex}.json').write_text(json.dumps(c,indent=2)+'\n')
   (out/'records.json').write_text(json.dumps(rows,indent=2)+'\n')
   print('WEALTH',seed,vertex,c['compensated_policy_minus_original_optimum_lower'],flush=True)
if __name__=='__main__':run()
