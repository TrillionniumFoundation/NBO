"""Absolute continuous-LQ error of exact stored sample-and-hold actor outputs.
The Riccati reference and interval moment verifier are independent constructions.
"""
from __future__ import annotations
import argparse,hashlib,json,math,pathlib,platform,time
import mpmath as mp
import numpy as np
import torch
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r11'
mp.iv.dps=60;torch.set_num_threads(1)
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def iv(x):return mp.iv.mpf(float(x))
def bounds(x):return [float(np.nextafter(float(x.a),-np.inf)),float(np.nextafter(float(x.b),np.inf))]
def inputs():
 proto=json.loads((REV/'protocol.json').read_text());out=[]
 keys=['a','b','q','r','sigma','terminal_weight','initial_centered']
 for c in proto['exact_accuracy_suite']['cases']:
  d=c['d'];v={'name':c['name'],'d':d}
  if c['name']=='ill_conditioned':
   vals=[np.linspace(-1,.5,d),np.linspace(.5,2,d),np.linspace(.1,2,d),np.geomspace(.1,4,d),np.linspace(.15,.65,d),np.linspace(.5,2,d),np.linspace(-1,1,d)]
   for k,z in zip(keys,vals):v[k]=z.tolist()
  else:
   for k in keys:v[k]=(np.ones(d)*c[k][0]).tolist()
  out.append(v)
 return out

def reference(case):
 total=iv(0);parts=[]
 for j in range(case['d']):
  a,b,q,r,s,w,x=[iv(case[k][j]) for k in ['a','b','q','r','sigma','terminal_weight','initial_centered']]
  c=b*b/r;lam=mp.iv.sqrt(a*a+c*q)
  if case['a'][j]==0 and case['q'][j]==0:C=iv(1);S=iv(1)
  else:C=(mp.iv.exp(lam)+mp.iv.exp(-lam))/2;S=(mp.iv.exp(lam)-mp.iv.exp(-lam))/(2*lam)
  X=C+S*(-a+c*w);Y=w*C+S*(q+a*w);assert float(X.a)>0
  P=Y/X;integral=(mp.iv.ln(X)+a)/c;z=P*x*x+s*s*integral;total+=z;parts.append(bounds(z))
 return total/case['d'],parts

def constants(case,n,interval=False):
 conv=iv if interval else float;h=conv(1)/n;out=[]
 for j in range(case['d']):
  a,b,q,r,s,w,x=[conv(case[k][j]) for k in ['a','b','q','r','sigma','terminal_weight','initial_centered']]
  exp=mp.iv.exp if interval else math.exp
  if case['a'][j]==0:E=conv(1);I=h;I2=h;B=h*h/2;C=h*h*h/3;D=h*h/2
  else:E=exp(a*h);I=(E-1)/a;I2=(exp(2*a*h)-1)/(2*a);B=(I2-I)/a;C=(I2-2*I+h)/(a*a);D=(I2-h)/(2*a)
  out.append((E,I,I2,B,C,D,b,q,r,s,w,x,h))
 return out

def improve(case,n):
 cc=constants(case,n);gain=np.zeros((n,case['d']))
 for j,(E,I,A,B,C,D,b,q,r,s,w,x,h) in enumerate(cc):
  p=w
  for i in range(n-1,-1,-1):
   den=q*b*b*C+r*h+p*b*b*I*I;num=q*b*B+p*E*b*I;gain[i,j]=num/den;p=q*A+p*E*E-num*num/den
 return gain

def certificate(case,gain):
 n,d=gain.shape;assert d==case['d'] and np.isfinite(gain).all();cc=constants(case,n,True);cost=iv(0)
 for j,(E,I,A,B,C,D,b,q,r,s,w,x,h) in enumerate(cc):
  moment=x*x;value=iv(0)
  for i in range(n):
   K=iv(gain[i,j]);stage=q*(A-2*b*K*B+b*b*K*K*C)+r*h*K*K
   value+=stage*moment+q*s*s*D;moment=(E-b*K*I)**2*moment+s*s*A
  cost+=value+w*moment
 cost/=d;ref,parts=reference(case);gap=cost-ref
 assert float(gap.b)>=0 and all(math.isfinite(x) for x in bounds(cost)+bounds(ref)+bounds(gap))
 return {'policy_cost':bounds(cost),'optimal_value':bounds(ref),'absolute_regret':bounds(gap),'reference_coordinates':parts,'rounding':'60-decimal mpmath.iv; exact binary64 inputs; float endpoints enlarged one ulp','policy_sha256':hashlib.sha256(gain.astype('<f8').tobytes()).hexdigest()}

def torch_cost(case,gain):
 n,d=gain.shape;cc=constants(case,n);cc=[torch.tensor([z[i] for z in cc],dtype=torch.float64) for i in range(13)]
 E,I,A,B,C,D,b,q,r,s,w,x,h=cc;moment=x*x;value=torch.zeros(d,dtype=torch.float64)
 for i in range(n):
  K=gain[i];value=value+(q*(A-2*b*K*B+b*b*K*K*C)+r*h*K*K)*moment+q*s*s*D;moment=(E-b*K*I)**2*moment+s*s*A
 return (value+w*moment).mean()

def run(out):
 proto=json.loads((REV/'protocol.json').read_text());cases=inputs();spec={'cases':cases,'adam':{'lr':.05,'betas':[.9,.999],'eps':1e-8,'N':32,'initial_gains':0,'updates':[0,25,100,400]},'protocol_sha256':hashlib.sha256((REV/'protocol.json').read_bytes()).hexdigest()}
 dump(out/'instances_and_optimizer.json',spec);rows=[];tests=[]
 for case in cases:
  caseout=out/case['name'];exact_clock=0.;adam_clock=0.
  for n in proto['exact_accuracy_suite']['slabs']:
   t=time.perf_counter();gain=improve(case,n);gen=time.perf_counter()-t;t=time.perf_counter();cert=certificate(case,gain);verify=time.perf_counter()-t;exact_clock+=gen+verify
   rec={'case':case['name'],'method':'quadratic_Bellman','slabs':n,'generation_seconds':gen,'verification_seconds':verify,'cumulative_seconds':exact_clock,**cert}
   dump(caseout/f'bellman_N{n}_gains.json',gain.tolist());dump(caseout/f'bellman_N{n}.json',rec);rows.append(rec)
   tv=float(torch_cost(case,torch.tensor(gain,dtype=torch.float64)));assert cert['policy_cost'][0]-2e-12<tv<cert['policy_cost'][1]+2e-12
  gain=torch.nn.Parameter(torch.zeros((32,case['d']),dtype=torch.float64));opt=torch.optim.Adam([gain],lr=.05,betas=(.9,.999),eps=1e-8);previous=0
  for step in [0,25,100,400]:
   t=time.perf_counter()
   for _ in range(step-previous):opt.zero_grad();loss=torch_cost(case,gain);loss.backward();opt.step()
   gen=time.perf_counter()-t;g=gain.detach().numpy().copy();t=time.perf_counter();cert=certificate(case,g);verify=time.perf_counter()-t;adam_clock+=gen+verify
   rec={'case':case['name'],'method':'Adam_gain','slabs':32,'updates':step,'incremental_generation_seconds':gen,'verification_seconds':verify,'cumulative_seconds':adam_clock,**cert}
   dump(caseout/f'adam_{step}_gains.json',g.tolist());dump(caseout/f'adam_{step}.json',rec);rows.append(rec);previous=step
  tests.append({'case':case['name'],'torch_vs_interval_check':'PASS','reference_width':bounds(reference(case)[0])[1]-bounds(reference(case)[0])[0]})
 frontiers=[]
 for case in cases:
  for method in ['quadratic_Bellman','Adam_gain']:
   rr=[r for r in rows if r['case']==case['name'] and r['method']==method]
   for target in proto['exact_accuracy_suite']['thresholds']:
    success=[r for r in rr if r['absolute_regret'][1]<=target];frontiers.append({'case':case['name'],'method':method,'target':target,'attained':bool(success),'first':success[0] if success else None})
 summary={'status':'PASS','environment':{'python':platform.python_version(),'numpy':np.__version__,'torch':torch.__version__,'mpmath':mp.__version__,'platform':platform.platform(),'threads':torch.get_num_threads()},'instance_sha256':hashlib.sha256((out/'instances_and_optimizer.json').read_bytes()).hexdigest(),'rows':rows,'matched_accuracy_frontier':frontiers,'tests':tests,'claims':'Deterministic absolute original-LQ-cost enclosures, not an external SOC-versus-tanh-NBO accuracy ranking. Exact held-action deployment. Setup and one-time optimizer construction excluded; generation and verifier clocks separately reported.'}
 dump(out/'summary.json',summary);print(json.dumps({'status':summary['status'],'last_bellman':[(r['case'],r['absolute_regret']) for r in rows if r['method']=='quadratic_Bellman' and r['slabs']==128],'last_adam':[(r['case'],r['absolute_regret']) for r in rows if r.get('updates')==400]},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,default=REV/'results/accuracy');args=p.parse_args();run(args.out)
