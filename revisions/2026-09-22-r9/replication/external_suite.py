"""R9 frozen holdout comparison. The pinned SOC-MartNet solver is unmodified.
Learning-rate trials, initial weights, clocks, deployment and seeds are explicit.
All costs are policy-performance estimates; the independent lower bound is separate.
"""
from __future__ import annotations
import argparse,contextlib,copy,hashlib,io,json,math,os,pathlib,platform,sys,time
import numpy as np
from scipy.stats import binomtest,t as student_t
import torch
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r8/replication'))
import external_comparison as r8
OUT=ROOT/'revisions/2026-09-22-r9/results/external';OUT.mkdir(parents=True,exist_ok=True)
PIN='991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a'
torch.set_num_threads(1)

class LQ(torch.nn.Module):
 def forward(self,t,x):return torch.clamp(-2*(x-.5)/(1+4*(1-t)),-1,1)

def train_nbo(a,v,d,seconds,mult):
 oa=torch.optim.Adam(a.parameters(),lr=.003*mult);ov=torch.optim.Adam(v.parameters(),lr=.003*mult)
 start=time.perf_counter();steps=0;history=[]
 while time.perf_counter()-start<seconds:
  for _ in range(3):
   t=torch.randint(0,16,(256,1))*r8.DT;x=r8.SIGMA*torch.sqrt(t)*torch.randn(256,d)
   with torch.no_grad():
    aa=a(t,x);xn=x[:,None,:]+2*aa[:,None,:]*r8.DT+r8.SIGMA*math.sqrt(r8.DT)*torch.randn(256,4,d)
    target=r8.cost(aa)*r8.DT+v(t[:,None,:]+r8.DT,xn).mean(1)
   loss=(v(t,x)-target).square().mean();ov.zero_grad();loss.backward();ov.step()
  t=torch.randint(0,16,(256,1))*r8.DT;x=r8.SIGMA*torch.sqrt(t)*torch.randn(256,d)
  ov.zero_grad(set_to_none=True)
  for p in v.parameters():p.requires_grad_(False)
  aa=a(t,x);xn=x[:,None,:]+2*aa[:,None,:]*r8.DT+r8.SIGMA*math.sqrt(r8.DT)*torch.randn(256,4,d)
  objective=(r8.cost(aa)*r8.DT+v(t[:,None,:]+r8.DT,xn).mean(1)).mean()
  oa.zero_grad();objective.backward();oa.step()
  assert all(p.grad is None for p in v.parameters())
  for p in v.parameters():p.requires_grad_(True)
  steps+=1
  if steps%100==0:history.append([steps,float(loss.detach()),float(objective.detach())])
 a.eval();v.eval();return {'training_seconds':time.perf_counter()-start,'outer_updates':steps,'history':history},{}

def train_soc(a,v,d,seconds,mult,source):
 sys.path.insert(0,str(source/'code/SOCMartNet-v3-refactored'))
 from socmartnet.solver import SOCMartNet
 from socmartnet.networks import test_net
 rho=test_net(d,600)
 opts=[torch.optim.RMSprop(a.parameters(),lr=.003*mult/math.sqrt(d)),
       torch.optim.RMSprop(v.parameters(),lr=.003*mult/math.sqrt(d)),
       torch.optim.RMSprop(rho.parameters(),lr=.01)]
 def H(t,x,u,val,vx,vxx):return 2*(u*vx.squeeze(-2)).sum(-1,keepdim=True)+r8.cost(u)
 solver=SOCMartNet(torch.tensor(r8.DT),lambda t,x:torch.zeros_like(x),lambda t,x:r8.SIGMA*torch.ones_like(x),H,r8.terminal,d,t0=torch.tensor(0.))
 start=time.perf_counter();budget=r8.Budget(start,seconds);log=io.StringIO()
 with contextlib.redirect_stdout(log):
  try:
   solver.train((a,v,rho),opts,(None,None,budget),10**9,torch.zeros(1024,d),[64],rank=0,lam0=10,N=16,
      err_func=lambda:torch.tensor(float('nan')),log_gap=1000,J=2,K=1,delta4=10,lam_bar=1000,renew_frac=0)
  except r8.BudgetStop:pass
 a.eval();v.eval();rho.eval()
 return {'training_seconds':time.perf_counter()-start,'outer_updates':budget.steps,'log':log.getvalue()}, {'adversary':rho.state_dict()}

def fit(method,d,seed,seconds,mult,source,initial=None):
 torch.manual_seed(seed);a0=r8.Net(d,True);v0=r8.Net(d,False)
 if initial is not None:a0,v0=initial
 initial_hash={'actor':r8.digest(a0),'critic':r8.digest(v0)}
 torch.manual_seed(seed+100000);a=copy.deepcopy(a0);v=copy.deepcopy(v0)
 start=time.perf_counter()
 info,extra=train_nbo(a,v,d,seconds,mult) if method=='nbo' else train_soc(a,v,d,seconds,mult,source)
 info.update({'setup_and_training_seconds':time.perf_counter()-start,'learning_rate_multiplier':mult,
  'initial_hash':initial_hash,'actor_parameters':sum(p.numel() for p in a.parameters()),'critic_parameters':sum(p.numel() for p in v.parameters())})
 if not all(torch.isfinite(p).all() for p in a.parameters()):raise ValueError('Nonfinite actor; run must be recorded as failed')
 return a,v,info,extra

def warm(d,source):
 times={}
 for method in ['nbo','soc']:
  s=time.perf_counter();fit(method,d,599,.02,1.,source);times[method]=time.perf_counter()-s
 return times

def noise(d,seed,paths):
 g=torch.Generator().manual_seed(seed)
 return torch.randn(128,paths,d,generator=g)/math.sqrt(128)

def tune(d,source):
 warmup=warm(d,source);rows=[]
 for mult in [1/3,1.,3.]:
  for seed in [600,601]:
   order=['nbo','soc'];np.random.default_rng(seed+d).shuffle(order)
   z=noise(d,910000+seed,1024)
   for method in order:
    a,v,info,_=fit(method,d,seed,10.,mult,source)
    score=float(r8.rollout(a,z).mean(dtype=np.float64))
    rows.append({'method':method,'multiplier':mult,'seed':seed,'validation_mean':score,**info})
 selected={}
 for method in ['nbo','soc']:
  selected[method]=min([1/3,1.,3.],key=lambda m:(np.mean([r['validation_mean'] for r in rows if r['method']==method and r['multiplier']==m]),m))
 payload={'dimension':d,'selected':selected,'rows':rows,'warmup_seconds':warmup,'source_commit':os.getenv('GITHUB_SHA'),'author_commit':PIN,
  'selection':'minimum mean validation cost across seeds 600,601; tie goes to lower multiplier; same six 10-second trials per method'}
 (OUT/f'tuning_d{d}.json').write_text(json.dumps(payload,indent=2)+'\n');print('tuned',d,selected,flush=True)

def run(d,seconds,source):
 tuning=json.loads((OUT/f'tuning_d{d}.json').read_text());warmup=warm(d,source)
 for seed in range(720,732):
  torch.manual_seed(seed);initial=(r8.Net(d,True),r8.Net(d,False));order=['nbo','soc'];np.random.default_rng(970000+d+seed).shuffle(order)
  models={'lq':LQ()};infos={};prefix=f'd{d}_b{int(seconds)}_s{seed}'
  for method in order:
   a,v,info,extra=fit(method,d,seed,seconds,tuning['selected'][method],source,initial)
   models[method]=a;infos[method]=info
   torch.save({'actor':a.state_dict(),'critic':v.state_dict(),**extra},OUT/f'{prefix}_{method}.pt')
  start=time.perf_counter();z=noise(d,980000+seed,4096);arrays={}
  for method,model in models.items():
   for n,coarse in [(128,False),(64,True)]:arrays[f'{method}_{n}']=r8.rollout(model,z,coarse)
  for method in ['nbo','soc','lq']:
   infos.setdefault(method,{})
   q=arrays[method+'_128'].astype(float)
   infos[method].update({'mean_cost':float(q.mean()),'path_se':float(q.std(ddof=1)/64),
       'sample_hold_128_minus_64':float(q.mean()-arrays[method+'_64'].mean(dtype=np.float64))})
  np.savez_compressed(OUT/f'{prefix}_paths.npz',**arrays)
  diff=arrays['nbo_128'].astype(float)-arrays['soc_128'].astype(float)
  payload={'dimension':d,'budget_seconds':seconds,'seed':seed,'order':order,'methods':infos,
   'paired_difference':float(diff.mean()),'paired_path_se':float(diff.std(ddof=1)/64),
   'audit_seconds':time.perf_counter()-start,'warmup_seconds':warmup,'author_commit':PIN,
   'source_commit':os.getenv('GITHUB_SHA'),'python':platform.python_version(),'torch':torch.__version__,
   'scope':'Cost under admissible sample-and-hold controls in the unchanged continuous model; floating-point Monte Carlo, not a deterministic optimality certificate'}
  (OUT/f'{prefix}.json').write_text(json.dumps(payload,indent=2)+'\n');print(prefix,payload['paired_difference'],flush=True)

def summarize():
 rows=[]
 for d in [8,16,32]:
  for budget in [10,30]:
   records=[json.loads((OUT/f'd{d}_b{budget}_s{s}.json').read_text()) for s in range(720,732)]
   for r in records:
    assert r['methods']['nbo']['initial_hash']==r['methods']['soc']['initial_hash']
    assert r['author_commit']==PIN
   diff=np.array([r['paired_difference'] for r in records]);n=len(diff);half=float(student_t.ppf(.975,n-1)*diff.std(ddof=1)/math.sqrt(n))
   p=float(binomtest(int((diff<0).sum()),n,.5,alternative='greater').pvalue)
   rows.append({'dimension':d,'budget_seconds':budget,'seeds':n,'raw_differences':diff.tolist(),
    'mean_difference':float(diff.mean()),'median_difference':float(np.median(diff)),
    'difference_IQR':np.quantile(diff,[.25,.75]).tolist(),'descriptive_t95':[float(diff.mean()-half),float(diff.mean()+half)],
    'one_sided_sign_p':p,'bonferroni_six_panels_p':min(1.,6*p),
    'means':{m:float(np.mean([r['methods'][m]['mean_cost'] for r in records])) for m in ['nbo','soc','lq']},
    'training_clock_means':{m:float(np.mean([r['methods'][m]['training_seconds'] for r in records])) for m in ['nbo','soc']},
    'max_paired_path_se':max(r['paired_path_se'] for r in records)})
 payload={'rows':rows,'scope':'Frozen holdout seeds; sign inference concerns the joint training-and-audit pipeline under independent seed draws. Student intervals are descriptive; audit and arithmetic errors are not rigorous enclosures. One benchmark family is not a multi-problem generality result.'}
 (OUT/'summary.json').write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps(rows,indent=2))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['tune','run','summarize']);ap.add_argument('--dimension',type=int,default=8);ap.add_argument('--seconds',type=int,default=10);ap.add_argument('--source',type=pathlib.Path,default=pathlib.Path('martnet-author'));a=ap.parse_args()
 if a.mode=='tune':tune(a.dimension,a.source)
 elif a.mode=='run':run(a.dimension,a.seconds,a.source)
 else:summarize()
