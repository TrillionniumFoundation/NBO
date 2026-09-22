"""Original-payoff neural time-control actor, with exact self-financing projection.
Policy learning uses Gaussian quadrature, not optimal actions/value labels. The
independent verifier uses a different polynomial-moment and interval method.
"""
from __future__ import annotations
import pathlib,json,time,argparse,hashlib
import numpy as np
import torch
from torch import nn
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss
from bernstein import I,iv,bounds
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'revisions/2026-09-22-r9/results'
torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
class BudgetProjection(torch.autograd.Function):
 @staticmethod
 def forward(ctx,raw,w,budget):
  lo=raw.new_tensor(-50.);hi=raw.new_tensor(50.)
  for _ in range(80):
   lam=(lo+hi)/2;c=.05+.75*torch.sigmoid(raw+lam)
   if (w*c).sum()>budget:hi=lam
   else:lo=lam
  c=.05+.75*torch.sigmoid(raw+(lo+hi)/2);s=(c-.05)*(.8-c)/.75
  ctx.save_for_backward(s,w);return c
 @staticmethod
 def backward(ctx,g):
  s,w=ctx.saved_tensors
  return s*(g-w*(g*s).sum()/(w*s).sum()),None,None
class Actor(nn.Module):
 def __init__(self):
  super().__init__();self.net=nn.Sequential(nn.Linear(1,12),nn.Tanh(),nn.Linear(12,2))
 def forward(self,t,w,budget):
  raw=self.net(t);c=BudgetProjection.apply(raw[:,0],w,budget)
  th=.2*torch.sigmoid(raw[:,1]);return c,th

def run(k,seed=901,n=16,steps=2500,restricted=False):
 start=time.perf_counter();torch.manual_seed(seed);model=Actor();opt=torch.optim.Adam(model.parameters(),lr=.015)
 edges=torch.linspace(0,1,n+1);left=edges[:-1];t=(left+.5/n)[:,None]
 w=(torch.exp(-.02*left)-torch.exp(-.02*edges[1:]))/.02
 budget=torch.tensor(1.25-.5*np.exp(-.02)-1e-8)
 xg,xw=leggauss(12);zg,zw=hermgauss(20)
 ts=left[:,None]+torch.tensor((xg+1)/(2*n))[None,:]
 tw=torch.tensor(xw/(2*n));zg=torch.tensor(zg);zw=torch.tensor(zw/np.sqrt(np.pi))
 hist=[]
 for it in range(steps):
  c,th=model(t,w,budget)
  if restricted:th=th*0
  mleft=torch.cumsum(th/n,0)-th/n
  m=2+mleft[:,None]+th[:,None]*(ts-left[:,None])
  u=m[:,:,None]+.05*torch.sqrt(2*ts)[:,:,None]*zg
  running=c[:,None,None].pow(1-u)/(1-u)-.5*k*th[:,None,None]**2
  er=(running*zw).sum(-1)
  terminal=-.02*((th/n).sum()**2+.0025)+.1*torch.log(torch.tensor(.5)+torch.exp(torch.tensor(.02))*1e-8)
  value=(torch.exp(-.04*ts)*er*tw).sum()+np.exp(-.04)*terminal
  loss=-value;opt.zero_grad();loss.backward();opt.step()
  if it%250==0:hist.append([it,float(value.detach())])
 with torch.no_grad():c,th=model(t,w,budget)
 c=c.numpy();th=th.numpy()*(0 if restricted else 1)
 # Deployment constants are binary64 and are audited below as exact reals.
 # Budget is deliberately slack; reject rather than silently clipping a path.
 S=I(0)
 for j in range(n):S+=I(float(c[j]))*(iv.exp(-I('.02')*j/n)-iv.exp(-I('.02')*(j+1)/n))/I('.02')
 xT=iv.exp(I('.02'))*(I('1.25')-S)
 assert bounds(xT)[0]>.5
 assert c.min()>=.05 and c.max()<=.8 and th.min()>=0 and th.max()<=.2
 tag='restricted' if restricted else f'k{k:g}'
 state={a:v.detach().numpy().tolist() for a,v in model.state_dict().items()}
 payload={'k':k,'restricted':restricted,'seed':seed,'slabs':n,'steps':steps,'c':c.tolist(),'theta':th.tolist(),'p':[0.]*n,
  'network_state':state,'network_architecture':'1-12(tanh)-2 with sigmoid theta and differentiable global budget projection',
  'terminal_wealth_interval':bounds(xT),'training_history':hist,'training_seconds':time.perf_counter()-start,
  'original_payoff':True,'initial':[0,2,1.25],
  'deployment':'network at fixed time nodes; frozen piecewise-constant controls; continuous Brownian state and exact exit',
  'training_scope':'quadrature optimization in a time-only neural policy class, not a full feedback optimizer'}
 (OUT/f'actor_{tag}.json').write_text(json.dumps(payload,indent=2)+'\n')
 print(tag,payload['training_seconds'],hist[-1],'xT',bounds(xT),'theta',th.tolist(),flush=True)
 return payload
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--k',type=float,default=2);ap.add_argument('--restricted',action='store_true');ap.add_argument('--steps',type=int,default=2500);a=ap.parse_args();run(a.k,steps=a.steps,restricted=a.restricted)
