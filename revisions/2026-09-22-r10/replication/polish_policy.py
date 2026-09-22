"""Polish the inherited feasible time-control policy; no critic or optimal labels.
Training quadrature is deliberately separate from the inherited interval audit.
"""
from __future__ import annotations
import json,pathlib,sys,time
import numpy as np
import torch
from scipy.optimize import minimize
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r9/replication'))
from original_actor import BudgetProjection
from bernstein import I,iv,bounds
OUT=ROOT/'revisions/2026-09-22-r10/results'
torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
def run(k):
 start=time.perf_counter();old=json.loads((ROOT/f'revisions/2026-09-22-r9/results/actor_k{k:g}.json').read_text());n=16
 tg,tw=leggauss(20);zg,zw=hermgauss(40);ts=(np.arange(n)[:,None]+(tg+1)[None,:]/2)/n
 t=torch.tensor(ts);weights=torch.tensor(tw/(2*n));z=torch.tensor(zg);wz=torch.tensor(zw/np.sqrt(np.pi))
 edges=torch.linspace(0,1,n+1);dw=(torch.exp(-.02*edges[:-1])-torch.exp(-.02*edges[1:]))/.02
 budget=torch.tensor(1.25-.5*np.exp(-.02)-1e-8)
 def fun(a):
  a=torch.tensor(a,requires_grad=True);c=BudgetProjection.apply(a[:n],dw,budget);theta=a[n:]
  mu=2+(torch.cumsum(theta,0)-theta)[:,None]/n+theta[:,None]*(t-edges[:-1,None])
  u=mu[:,:,None]+.05*torch.sqrt(2*t)[:,:,None]*z
  running=(c[:,None,None]**(1-u)/(1-u)*wz).sum(-1)-.5*k*theta[:,None]**2
  terminal=np.exp(-.04)*(-.02*((theta.sum()/n)**2+.0025)+.1*torch.log(torch.tensor(.5)+np.exp(.02)*1e-8))
  val=(torch.exp(-.04*t)*running*weights).sum()+terminal
  g=torch.autograd.grad(-val,a)[0]
  return -float(val.detach()),g.detach().numpy()
 c=np.array(old['c']);theta=np.array(old['theta']);raw=np.log((c-.05)/(.8-c))
 opt=minimize(fun,np.r_[raw,theta],jac=True,method='L-BFGS-B',bounds=[(-15,15)]*n+[(0,.2)]*n,options={'ftol':1e-15,'gtol':1e-10,'maxiter':3000,'maxls':50})
 with torch.no_grad(): c=BudgetProjection.apply(torch.tensor(opt.x[:n]),dw,budget).numpy()
 c=np.clip(c,np.nextafter(.05,np.inf),np.nextafter(.8,-np.inf))
 theta=np.clip(opt.x[n:],0,np.nextafter(.2,-np.inf));debt=I(0)
 for j in range(n):debt+=I(float(c[j]))*(iv.exp(-I('.02')*j/n)-iv.exp(-I('.02')*(j+1)/n))/I('.02')
 xt=iv.exp(I('.02'))*(I('1.25')-debt);assert bounds(xt)[0]>.5
 result={'k':k,'restricted':False,'slabs':n,'c':c.tolist(),'theta':theta.tolist(),'p':[0.]*n,'original_payoff':True,'initial':[0,2,1.25],
 'parent_policy':f'revisions/2026-09-22-r9/results/actor_k{k:g}.json','algorithm':'L-BFGS-B output polishing with exact differentiable budget projection',
 'polishing_seconds':time.perf_counter()-start,'optimizer_success':bool(opt.success),'optimizer_message':str(opt.message),'iterations':int(opt.nit),'training_value':-opt.fun,
 'terminal_wealth_interval':bounds(xt),'deployment':'binary64 controls held constant on sixteen prescribed time slabs; exact continuous stopped economy',
 'training_scope':'finite time-control class; output polishing is not a claim of Adam convergence',
 'inward_rounding':'Frozen controls lie inside the exact decimal action bounds, not merely their binary64 approximations' }
 (OUT/f'actor_k{k:g}.json').write_text(json.dumps(result,indent=2)+'\n');print(k,-opt.fun,opt.success,opt.nit,result['polishing_seconds'],flush=True)
 return result
if __name__=='__main__':
 import original_policy_certificate as audit
 audit.OUT=OUT
 for k in [.5,2,8]:run(k);audit.run(f'k{k:g}',resolutions=(64,256,1024))
