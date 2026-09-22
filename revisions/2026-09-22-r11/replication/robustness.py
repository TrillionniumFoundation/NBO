"""Prospectively specified, method-specific tuning; immutable R9 data are untouched."""
from __future__ import annotations
import argparse,contextlib,copy,hashlib,io,json,math,os,pathlib,platform,sys,time,traceback
import numpy as np
import torch
from scipy.stats import binomtest
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r8/replication'))
import external_comparison as old
PIN='991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a'
torch.set_num_threads(1)

def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def configs(method):
 base={'mult':1.,'eval_steps':3,'particles':4} if method=='nbo' else {'mult':1.,'rho_lr':.01,'rho_width':600,'J':2,'K':1,'lam0':10,'delta4':10}
 out=[dict(base,mult=m) for m in [1/3,1.,3.,9.,27.]]
 changes=([{'mult':1.,'eval_steps':1},{'mult':3.,'eval_steps':1},{'mult':9.,'eval_steps':6},{'mult':3.,'eval_steps':6,'particles':8},{'mult':9.,'particles':8},{'mult':3.,'particles':2},{'mult':9.,'eval_steps':1,'particles':8}] if method=='nbo' else [{'mult':3.,'rho_lr':.001},{'mult':9.,'rho_lr':.1},{'mult':3.,'rho_width':128},{'mult':9.,'J':1},{'mult':3.,'J':4,'K':2},{'mult':9.,'lam0':1,'delta4':1},{'mult':3.,'lam0':30,'delta4':30}])
 return out+[dict(base,**c) for c in changes]
def fit(method,d,seed,seconds,cfg,source):
 torch.manual_seed(seed);a=old.Net(d,True);v=old.Net(d,False)
 ih={'actor':old.digest(a),'critic':old.digest(v)}
 torch.manual_seed(seed+2100000);setup=time.perf_counter();log=io.StringIO();extra={}
 if method=='nbo':
  oa=torch.optim.Adam(a.parameters(),lr=.003*cfg['mult']);ov=torch.optim.Adam(v.parameters(),lr=.003*cfg['mult'])
  start=time.perf_counter();steps=0;history=[]
  while time.perf_counter()-start<seconds:
   for _ in range(cfg['eval_steps']):
    t=torch.randint(0,16,(256,1))*old.DT;x=old.SIGMA*torch.sqrt(t)*torch.randn(256,d)
    with torch.no_grad():
     u=a(t,x);xn=x[:,None,:]+2*u[:,None,:]*old.DT+old.SIGMA*math.sqrt(old.DT)*torch.randn(256,cfg['particles'],d)
     target=old.cost(u)*old.DT+v(t[:,None,:]+old.DT,xn).mean(1)
    loss=(v(t,x)-target).square().mean();ov.zero_grad();loss.backward();ov.step()
   t=torch.randint(0,16,(256,1))*old.DT;x=old.SIGMA*torch.sqrt(t)*torch.randn(256,d)
   ov.zero_grad(set_to_none=True)
   for p in v.parameters():p.requires_grad_(False)
   u=a(t,x);xn=x[:,None,:]+2*u[:,None,:]*old.DT+old.SIGMA*math.sqrt(old.DT)*torch.randn(256,cfg['particles'],d)
   obj=(old.cost(u)*old.DT+v(t[:,None,:]+old.DT,xn).mean(1)).mean()
   oa.zero_grad();obj.backward();oa.step()
   for p in v.parameters():p.requires_grad_(True)
   steps+=1
   if steps%100==0:history.append([steps,float(loss.detach()),float(obj.detach())])
 else:
  sys.path.insert(0,str(source/'code/SOCMartNet-v3-refactored'))
  from socmartnet.solver import SOCMartNet
  from socmartnet.networks import test_net
  rho=test_net(d,cfg['rho_width'])
  opts=[torch.optim.RMSprop(a.parameters(),lr=.003*cfg['mult']/math.sqrt(d)),torch.optim.RMSprop(v.parameters(),lr=.003*cfg['mult']/math.sqrt(d)),torch.optim.RMSprop(rho.parameters(),lr=cfg['rho_lr'])]
  def H(t,x,u,val,vx,vxx):return 2*(u*vx.squeeze(-2)).sum(-1,keepdim=True)+old.cost(u)
  solver=SOCMartNet(torch.tensor(old.DT),lambda t,x:torch.zeros_like(x),lambda t,x:old.SIGMA*torch.ones_like(x),H,old.terminal,d,t0=torch.tensor(0.))
  start=time.perf_counter();budget=old.Budget(start,seconds)
  with contextlib.redirect_stdout(log):
   try:solver.train((a,v,rho),opts,(None,None,budget),10**9,torch.zeros(1024,d),[64],rank=0,lam0=cfg['lam0'],N=16,err_func=lambda:torch.tensor(float('nan')),log_gap=1000,J=cfg['J'],K=cfg['K'],delta4=cfg['delta4'],lam_bar=1000,renew_frac=0)
   except old.BudgetStop:pass
  steps=budget.steps;history=[];extra={'adversary':rho.state_dict()}
 a.eval();v.eval()
 for model in (a,v):
  if not all(torch.isfinite(p).all() for p in model.parameters()):raise ValueError('Nonfinite network')
 return a,v,{'initial_hash':ih,'training_seconds':time.perf_counter()-start,'setup_and_training_seconds':time.perf_counter()-setup,'outer_updates':steps,'history':history,'log':log.getvalue(),'config':cfg},extra

def noise(d,seed,paths):return torch.randn(128,paths,d,generator=torch.Generator().manual_seed(seed))/math.sqrt(128)
class LQ(torch.nn.Module):
 def forward(self,t,x):return torch.clamp(-2*(x-.5)/(1+4*(1-t)),-1,1)

def tune(d,source,out):
 rows=[];selected={};failures=[]
 for m in ['nbo','soc']:fit(m,d,1599,.02,configs(m)[1],source)
 grids={m:configs(m) for m in ['nbo','soc']}
 def score(m,i):
  r=[v for v in rows if v['method']==m and v['candidate']==i]
  return sum(v['validation_mean'] for v in r)/2 if len(r)==2 and all(v['status']=='success' for v in r) else float('inf')
 for i in range(14):
  if i>=12:
   for m in grids:
    best=min(range(i),key=lambda j:(score(m,j),j));cfg=copy.deepcopy(grids[m][best]);mults=[c['mult'] for c in grids[m]]
    if cfg['mult']==max(mults):cfg['mult']*=3
    elif cfg['mult']==min(mults):cfg['mult']/=3
    elif m=='nbo':cfg['particles']=[16,32][i-12]
    else:cfg['rho_lr']=[.003,.03][i-12]
    grids[m].append(cfg)
  for seed in [1600,1601]:
   order=['nbo','soc'];np.random.default_rng(2600000+d+seed+i).shuffle(order)
   for m in order:
    rec={'candidate':i,'method':m,'seed':seed,'config':grids[m][i],'status':'started'};clock=time.perf_counter()
    try:
     a,v,info,_=fit(m,d,seed,5.,grids[m][i],source)
     val=old.rollout(a,noise(d,2610000+seed,1024)).astype(float)
     if not np.isfinite(val).all():raise ValueError('Nonfinite validation costs')
     rec.update(info,validation_mean=float(val.mean()),status='success')
    except Exception as exc:
     rec.update(status='failed',exception=str(exc),traceback=traceback.format_exc());failures.append([m,i,seed])
    rec['all_in_seconds']=time.perf_counter()-clock;rows.append(rec);dump(out/f'tune_{m}_{i}_{seed}.json',rec)
  dump(out/'tuning_progress.json',{'dimension':d,'completed_candidates':i+1,'rows':rows})
 for m in grids:
  best=min(range(14),key=lambda j:(score(m,j),j))
  if not math.isfinite(score(m,best)):raise ValueError('Every configuration failed for '+m)
  selected[m]={'candidate':best,'config':grids[m][best],'score':score(m,best),'multiplier_at_boundary':grids[m][best]['mult'] in [min(c['mult'] for c in grids[m]),max(c['mult'] for c in grids[m])]}
 result={'dimension':d,'selected':selected,'rows':rows,'failures':failures,'nominal_training_seconds_per_method':140,'source_commit':os.environ['R11_SOURCE_COMMIT'],'author_commit':PIN,'status':'success'}
 dump(out/'tuning.json',result);return result

def holdout(d,source,out,tuning):
 selected=tuning['selected'];records=[]
 for seed in range(1820,1832):
  start=time.perf_counter();rec={'dimension':d,'seed':seed,'budget_seconds':10,'status':'started','methods':{},'source_commit':os.environ['R11_SOURCE_COMMIT'],'author_commit':PIN}
  dump(out/f'seed_{seed}.json',rec)
  try:
   models={'lq':LQ()};order=['nbo','soc'];np.random.default_rng(2700000+d+seed).shuffle(order);rec['order']=order
   for m in order:
    a,v,info,extra=fit(m,d,seed,10.,selected[m]['config'],source);models[m]=a;rec['methods'][m]=info
    torch.save({'actor':a.state_dict(),'critic':v.state_dict(),**extra},out/f'seed_{seed}_{m}.pt')
   assert rec['methods']['nbo']['initial_hash']==rec['methods']['soc']['initial_hash']
   z=noise(d,2810000+seed,4096);arrays={}
   for m in ['nbo','soc','lq']:
    arrays[m]=old.rollout(models[m],z).astype(float)
    if not np.isfinite(arrays[m]).all():raise ValueError('Nonfinite audit')
    rec['methods'].setdefault(m,{})
    rec['methods'][m].update(mean_cost=float(arrays[m].mean()),path_se=float(arrays[m].std(ddof=1)/64))
   np.savez_compressed(out/f'seed_{seed}_paths.npz',**arrays)
   diff=arrays['nbo']-arrays['soc'];rec.update(paired_difference=float(diff.mean()),paired_path_se=float(diff.std(ddof=1)/64),status='success')
  except Exception as exc:rec.update(status='failed',exception=str(exc),traceback=traceback.format_exc())
  rec['all_in_seconds']=time.perf_counter()-start;dump(out/f'seed_{seed}.json',rec);records.append(rec)
  print(d,seed,rec['status'],rec.get('paired_difference'),flush=True)
 return records

def run(d,source,out):
 out.mkdir(parents=True,exist_ok=True)
 status={'dimension':d,'source_commit':os.environ['R11_SOURCE_COMMIT'],'status':'started','planned_holdout_seeds':list(range(1820,1832)),'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__}
 dump(out/'status.json',status)
 try:
  tuning=tune(d,source,out/'tuning');records=holdout(d,source,out/'holdout',tuning)
  status['status']='success' if all(r['status']=='success' for r in records) else 'failed'
 except Exception as exc:status.update(status='failed',exception=str(exc),traceback=traceback.format_exc())
 finally:dump(out/'status.json',status)
 if status['status']!='success':raise RuntimeError('Retained incomplete cell')

def collect(downloads,dest):
 import shutil
 dest.mkdir(parents=True,exist_ok=True);cells=[];rows=[]
 for d in [8,16,32]:
  src=downloads/f'r11-d{d}';target=dest/f'd{d}'
  if src.exists():shutil.copytree(src,target,dirs_exist_ok=True)
  try:
   status=json.loads((target/'status.json').read_text());assert status['status']=='success'
   rr=[json.loads((target/f'holdout/seed_{s}.json').read_text()) for s in range(1820,1832)]
   assert all(r['status']=='success' and r['source_commit']==os.environ['R11_SOURCE_COMMIT'] for r in rr)
   diff=np.array([r['paired_difference'] for r in rr]);assert np.isfinite(diff).all()
   p=float(binomtest(int((diff<0).sum()),12,.5,alternative='greater').pvalue)
   tuning=json.loads((target/'tuning/tuning.json').read_text())
   rows.append({'dimension':d,'raw_differences':diff.tolist(),'nbo_wins':int((diff<0).sum()),'mean_difference':float(diff.mean()),'median_difference':float(np.median(diff)),'sign_p':p,'bonferroni_three_p':min(1.,3*p),'means':{m:float(np.mean([r['methods'][m]['mean_cost'] for r in rr])) for m in ['nbo','soc','lq']},'selected':tuning['selected'],'tuning_failed_trials':len(tuning['failures']),'training_clock_means':{m:float(np.mean([r['methods'][m]['training_seconds'] for r in rr])) for m in ['nbo','soc']}})
   cells.append({'dimension':d,'status':'success'})
  except Exception as exc:cells.append({'dimension':d,'status':'failed_or_missing','exception':str(exc)})
 result={'status':'PASS' if len(rows)==3 else 'FAIL','planned_cells':cells,'rows':rows,'source_commit':os.environ['R11_SOURCE_COMMIT'],'scope':'New fixed-configuration holdout, conditional on prospectively declared adaptive tuning. No distribution-free coverage for sampled costs and no universal tuning-optimality assertion.'}
 dump(dest/'summary.json',result)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','collect']);p.add_argument('--dimension',type=int);p.add_argument('--source',type=pathlib.Path,default=pathlib.Path('martnet-author'));p.add_argument('--out',type=pathlib.Path,required=True);p.add_argument('--downloads',type=pathlib.Path);a=p.parse_args()
 if a.mode=='run':run(a.dimension,a.source,a.out)
 else:collect(a.downloads,a.out)
