"""Execute the preregistered R20 study, retaining every proposal and decision."""
from pathlib import Path
import argparse,copy,hashlib,json,time,platform,resource,sys
import numpy as np
import torch
from torch import nn
from scipy.optimize import minimize
from proposal import Actor,setup
from certify_stochastic import certify,I,Q,upper
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r20'
PROTOCOL='238ecc0052dc418e1fe6fd06c3daa4a93da1a335'
CORNERS=[(1.98,1.24),(1.98,1.26),(2.02,1.24),(2.02,1.26)]
WORK=(0,100,400,1000)
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frozen(net,d,path,metadata):
 layers={k:v.detach().cpu().tolist() for k,v in net.state_dict().items()}
 npth=path.with_name(path.name.replace('actor','network'))
 write(npth,{'architecture':'1-16-16-3 tanh; logistic self-financing decoder','parameters':layers,**metadata})
 d={**d,**metadata,'network_file':str(npth.relative_to(ROOT)),'network_sha256':digest(npth),'deployment':'Exact serialized dyadic coefficients; neural compilation occurs once; hedge defined by conditional price derivative.'}
 write(path,d);return d

def neural(seed):
 out=REV/'results/neural'/f'seed{seed}';records=[];whole=time.perf_counter()
 for vertex,(u,x) in enumerate(CORNERS):
  torch.manual_seed(seed);net=Actor();objective=setup(u,x);opt=torch.optim.Adam(net.parameters(),lr=.005)
  start=time.perf_counter();checks=0.;inc=None;saved=None;decisions=[]
  for step in range(WORK[-1]+1):
   if step in WORK:
    d=objective(net,True);path=out/f'vertex{vertex}'/f'actor_{step:04d}.json'
    meta={'seed':seed,'vertex':vertex,'step':step,'protocol_commit':PROTOCOL,'generation_seconds':time.perf_counter()-start-checks,'timestamp_unix':time.time()}
    d=frozen(net,d,path,meta);cs=time.perf_counter();checked=certify(d);checks+=time.perf_counter()-cs
    cp=path.with_name(path.name.replace('actor','certificate'));write(cp,checked)
    accepted=inc is None or checked['value_interval'][0]>inc['value_interval'][1]
    margin=None if inc is None else float((I(checked['value_interval'][0])-I(inc['value_interval'][1])).lo)
    row={**meta,**checked,'actor_path':str(path.relative_to(ROOT)),'actor_sha256':digest(path),'certificate_path':str(cp.relative_to(ROOT)),
      'accepted':accepted,'gain_over_incumbent_lower':margin,'check_complete_before_next_update':True,'verification_cumulative_seconds':checks}
    records.append(row);decisions.append({k:row[k] for k in ['step','accepted','gain_over_incumbent_lower','actor_sha256','check_complete_before_next_update']})
    write(out/'records.json',records);write(out/f'vertex{vertex}'/'decisions.json',decisions)
    if accepted:inc=checked;saved=(copy.deepcopy(net.state_dict()),copy.deepcopy(opt.state_dict()))
    else:net.load_state_dict(saved[0]);opt.load_state_dict(saved[1])
    print('NEURAL',seed,vertex,step,checked['regret_upper'],accepted,flush=True)
   if step<WORK[-1]:opt.zero_grad();loss=-objective(net);loss.backward();opt.step()
 write(out/'resources.json',{'wall_seconds':time.perf_counter()-whole,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'python':platform.python_version(),'numpy':np.__version__,'torch':torch.__version__,'threads':1,'protocol_commit':PROTOCOL})
 return records

class Slab(nn.Module):
 def __init__(self):
  super().__init__();self.coeff=nn.Parameter(torch.tensor([[0.,-1.,-1.]]*16))
 def forward(self,t):return self.coeff

def classical():
 out=REV/'results/classical_stochastic';rows=[];whole=time.perf_counter();targets=(0,10,50,200)
 for vertex,(u,x) in enumerate(CORNERS):
  net=Slab();objective=setup(u,x);start=time.perf_counter();checktime=0.;nfev=0;laststep=0
  def evaluate(step,converged=False):
   nonlocal checktime,laststep
   d=objective(net,True);p=out/f'vertex{vertex}'/f'actor_{step:04d}.json'
   d.update({'algorithm':'L-BFGS-B direct 16-slab stochastic controls; no hidden neural layers','vertex':vertex,'step':step,'protocol_commit':PROTOCOL,
     'generation_seconds':time.perf_counter()-start-checktime,'objective_calls':nfev,'optimizer_converged':converged})
   write(p,d);st=time.perf_counter();c=certify(d);checktime+=time.perf_counter()-st
   cp=p.with_name(p.name.replace('actor','certificate'));write(cp,c)
   rows.append({**d,**c,'actor_path':str(p.relative_to(ROOT)),'actor_sha256':digest(p),'certificate_path':str(cp.relative_to(ROOT)),
                'verification_cumulative_seconds':checktime})
   write(out/'records.json',rows);laststep=step;print('CLASSICAL',vertex,step,c['regret_upper'],flush=True)
  def fun(a):
   nonlocal nfev
   with torch.no_grad():net.coeff.copy_(torch.tensor(a).reshape(16,3))
   net.zero_grad();loss=-objective(net);loss.backward();nfev+=1
   return float(loss.detach()),net.coeff.grad.detach().numpy().ravel().copy()
  iteration=0
  def callback(a):
   nonlocal iteration
   iteration+=1
   with torch.no_grad():net.coeff.copy_(torch.tensor(a).reshape(16,3))
   if iteration in targets:evaluate(iteration)
  evaluate(0)
  r=minimize(fun,net.coeff.detach().numpy().ravel().copy(),method='L-BFGS-B',jac=True,callback=callback,
       options={'maxiter':200,'maxls':40,'ftol':1e-13,'gtol':1e-8})
  with torch.no_grad():net.coeff.copy_(torch.tensor(r.x).reshape(16,3))
  if laststep!=r.nit:evaluate(int(r.nit),bool(r.success))
  write(out/f'vertex{vertex}'/'optimizer.json',{'success':bool(r.success),'message':str(r.message),'iterations':int(r.nit),'function_calls':int(r.nfev),'final_step':int(r.nit)})
 write(out/'resources.json',{'wall_seconds':time.perf_counter()-whole,'threads':1,'python':platform.python_version(),'torch':torch.__version__})
 return rows

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int);p.add_argument('--classical',action='store_true');a=p.parse_args()
 torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
 if a.classical:classical()
 else:
  for seed in ([a.seed] if a.seed else range(20100,20105)):neural(seed)
