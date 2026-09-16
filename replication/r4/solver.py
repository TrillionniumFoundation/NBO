#!/usr/bin/env python3
"""R4 killed-diffusion Bellman reference and separated neural implementation.
States=(u,X), actions=(c,theta,pi). No historical data or R3 routines imported.
"""
from __future__ import annotations
import itertools, math, time
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import torch
from torch import nn

torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)
LO=np.array([1.2,.5]); HI=np.array([2.8,2.])
ALO=np.array([.05,-.2,-.5]); AHI=np.array([.8,.2,.8])
SIGNS=np.array(list(itertools.product([-1.,1.],repeat=2)))

@dataclass(frozen=True)
class Model:
    rho:float=.04
    r:float=.02
    excess:float=.06
    sigma_u:float=.05
    sigma_x:float=.2
    correlation:float=-.25
    k:float=2.
    horizon:float=1.


def terminal(s):
    return -.02*(s[...,0]-2.)**2+.1*np.log(s[...,1])


def grid(nu,nx):
    states=np.stack(np.meshgrid(np.linspace(LO[0],HI[0],nu),np.linspace(LO[1],HI[1],nx),indexing='ij'),-1)
    bd=np.zeros((nu,nx),bool);bd[[0,-1],:]=True;bd[:,[0,-1]]=True
    return states,bd


def interpolate(v,s):
    size=np.array(v.shape)-1;z=(s-LO)/(HI-LO)*size
    ij=np.minimum(np.maximum(np.floor(z).astype(int),0),size-1);f=z-ij
    i,j=ij[...,0],ij[...,1];p,q=f[...,0],f[...,1]
    return (1-p)*(1-q)*v[i,j]+p*(1-q)*v[i+1,j]+(1-p)*q*v[i,j+1]+p*q*v[i+1,j+1]


def transition(s,a,h,m):
    """Four covariance-matching weak Euler branches, killed at first line exit.
    Killed paths obtain payoff at the hit, never an interior continuation.
    The linearly interpolated random-walk exit approximates Brownian exit.
    """
    c,th,pi=np.moveaxis(a,-1,0)
    drift=np.stack(np.broadcast_arrays(th,(m.r+m.excess*pi)*s[...,1]-c),-1)
    zu=SIGNS[:,0];zx=m.correlation*zu+math.sqrt(1-m.correlation**2)*SIGNS[:,1]
    noise=np.stack(np.broadcast_arrays(m.sigma_u*zu,m.sigma_x*pi[...,None]*s[...,1,None]*zx),-1)
    d=h*drift[...,None,:]+math.sqrt(h)*noise
    with np.errstate(divide='ignore',invalid='ignore'):
        ratios=np.where(d>0,(HI-s[...,None,:])/d,np.where(d<0,(LO-s[...,None,:])/d,np.inf))
    alpha=np.minimum(1.,ratios.min(-1)).clip(0,1)
    on_boundary=np.any((s<=LO)|(s>=HI),axis=-1)
    alpha=np.where(on_boundary[...,None],0.,alpha);live=alpha>=1.
    y=np.minimum(np.maximum(s[...,None,:]+alpha[...,None]*d,LO),HI)
    disc=np.exp(-m.rho*h*alpha);ann=-np.expm1(-m.rho*h*alpha)/m.rho
    reward=c**(1-s[...,0])/(1-s[...,0])-.5*m.k*th**2
    return y,live,disc,ann*reward[...,None],ann*.5*th[...,None]**2,d,alpha


def backup(v,s,a,h,m,effort=None):
    y,live,disc,flow,cost,_,alpha=transition(s,a,h,m)
    val=np.mean(flow+disc*np.where(live,interpolate(v,y),terminal(y)),-1)
    e=None if effort is None else np.mean(cost+disc*live*interpolate(effort,y),-1)
    return val,e,np.mean(~live,-1),np.mean(1-alpha,-1)


def action_mesh(counts=(5,5,7)):
    return np.array(list(itertools.product(*[np.linspace(a,b,n) for a,b,n in zip(ALO,AHI,counts)])))


def solve_grid(nu=17,nx=25,steps=8,counts=(5,5,7),m=Model(),frozen=None):
    start=time.perf_counter();s,bd=grid(nu,nx);sf=s.reshape(-1,2);h=m.horizon/steps
    values=[None]*(steps+1);efforts=[None]*(steps+1);policies=[None]*steps
    values[-1]=terminal(s);efforts[-1]=np.zeros((nu,nx));acts=action_mesh(counts);exits=[]
    for n in range(steps-1,-1,-1):
        if frozen is None:
            best=np.full(len(sf),-np.inf);pol=np.zeros((len(sf),3))
            for aa in np.array_split(acts,math.ceil(len(acts)/32)):
                q,_,_,_=backup(values[n+1],sf[:,None,:],aa[None,:,:],h,m)
                j=q.argmax(1);g=q[np.arange(len(sf)),j];use=g>best
                best[use]=g[use];pol[use]=aa[j[use]]
        else:pol=frozen(n,sf)
        val,eff,ex,_=backup(values[n+1],sf,pol,h,m,efforts[n+1])
        val=val.reshape(nu,nx);eff=eff.reshape(nu,nx)
        val[bd]=terminal(s)[bd];eff[bd]=0
        values[n]=val;efforts[n]=eff;policies[n]=pol.reshape(nu,nx,3)
        exits.append(float(ex[~bd.ravel()].mean()))
    return dict(values=values,efforts=efforts,policies=policies,elapsed=time.perf_counter()-start,
                mean_branch_exit=float(np.mean(exits)),grid=[nu,nx],steps=steps,counts=list(counts))


def torch_terminal(s):return -.02*(s[...,0]-2.)**2+.1*torch.log(s[...,1])


def torch_backup(nxt,s,a,h,m):
    lo=torch.as_tensor(LO);hi=torch.as_tensor(HI);c,th,pi=a.unbind(-1)
    drift=torch.stack((th,(m.r+m.excess*pi)*s[:,1]-c),-1);z=torch.as_tensor(SIGNS)
    zx=m.correlation*z[:,0]+math.sqrt(1-m.correlation**2)*z[:,1]
    du=m.sigma_u*z[:,0].expand(len(s),-1);dx=m.sigma_x*pi[:,None]*s[:,1,None]*zx
    d=h*drift[:,None,:]+math.sqrt(h)*torch.stack((du,dx),-1)
    safe=torch.where(d.abs()>1e-14,d,torch.ones_like(d))
    ratios=torch.where(d>1e-14,(hi-s[:,None,:])/safe,
             torch.where(d < -1e-14,(lo-s[:,None,:])/safe,torch.full_like(d,1e20)))
    alpha=ratios.amin(-1).clamp(0,1)
    on_boundary=((s<=lo)|(s>=hi)).any(-1)
    alpha=torch.where(on_boundary[:,None],torch.zeros_like(alpha),alpha)
    y=(s[:,None,:]+alpha[...,None]*d).clamp(lo,hi)
    cont=nxt(y.reshape(-1,2)).reshape(len(s),4)
    cont=torch.where(alpha>=1,cont,torch_terminal(y))
    ann=-torch.expm1(-m.rho*h*alpha)/m.rho
    reward=c.pow(1-s[:,0])/(1-s[:,0])-.5*m.k*th.square()
    return (ann*reward[:,None]+torch.exp(-m.rho*h*alpha)*cont).mean(-1)


class Net(nn.Module):
    def __init__(self,out=1,width=32):
        super().__init__();self.layers=nn.Sequential(nn.Linear(2,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh(),nn.Linear(width,out))
    def forward(self,s):return self.layers(2*(s-torch.as_tensor(LO))/torch.as_tensor(HI-LO)-1)

class Actor(Net):
    def __init__(self,width=32):super().__init__(3,width)
    def forward(self,s):return torch.as_tensor(ALO)+torch.as_tensor(AHI-ALO)*torch.sigmoid(super().forward(s))

class Critic(Net):
    def __init__(self,width=32,remaining=1.):super().__init__(1,width);self.remaining=remaining
    def forward(self,s):
        z=(s-torch.as_tensor(LO))/torch.as_tensor(HI-LO)
        mask=(torch.tanh(z/.06)*torch.tanh((1-z)/.06)).prod(-1)
        return torch_terminal(s)+self.remaining*mask*super().forward(s).squeeze(-1)


def fit_lbfgs(net,loss_fn,iterations=160):
    opt=torch.optim.LBFGS(net.parameters(),lr=.8,max_iter=iterations,tolerance_grad=1e-9,
                         tolerance_change=1e-11,history_size=25,line_search_fn='strong_wolfe')
    def closure():
        opt.zero_grad(set_to_none=True);loss=loss_fn()
        if not torch.isfinite(loss):raise FloatingPointError('nonfinite training loss')
        loss.backward();return loss
    opt.step(closure)
    state=opt.state[next(iter(net.parameters()))]
    fit_lbfgs.last_stats={k:int(state.get(k,0)) for k in ['n_iter','func_evals']}
    return float(loss_fn().detach())


def solve_neural(seed=101,steps=8,width=32,train_size=1024,actor_iters=160,critic_iters=260,m=Model(),outdir=None):
    start=time.perf_counter();torch.manual_seed(seed);rng=np.random.default_rng(seed)
    actors=[None]*steps;critics=[None]*(steps+1);critics[-1]=torch_terminal;logs=[]
    s=torch.as_tensor(rng.uniform(LO,HI,(train_size,2)));h=m.horizon/steps
    for n in range(steps-1,-1,-1):
        actor=Actor(width);critic=Critic(width,(steps-n)/steps)
        if n+1<steps:
            actor.load_state_dict(actors[n+1].state_dict());critic.load_state_dict(critics[n+1].state_dict())
        nxt=critics[n+1]
        if isinstance(nxt,nn.Module):
            for p in nxt.parameters():p.requires_grad_(False);p.grad=None
        # Freeze critic parameters, not its input derivatives through the transition.
        al=fit_lbfgs(actor,lambda:-torch_backup(nxt,s,actor(s),h,m).mean(),actor_iters)
        actor_stats=fit_lbfgs.last_stats.copy()
        assert not isinstance(nxt,nn.Module) or all(p.grad is None for p in nxt.parameters())
        with torch.no_grad():target=torch_backup(nxt,s,actor(s),h,m)
        cl=fit_lbfgs(critic,lambda:(critic(s)-target).square().mean(),critic_iters)
        for p in actor.parameters():p.requires_grad_(False);p.grad=None
        actors[n]=actor;critics[n]=critic
        logs.append(dict(date=n,actor_objective=al,critic_training_mse=cl,actor_optimizer=actor_stats,critic_optimizer=fit_lbfgs.last_stats.copy()))
        print(f'NBO seed={seed} n={n} critic_mse={cl:.5g}',flush=True)
    def frozen(n,x):
        with torch.no_grad():return actors[n](torch.as_tensor(x)).numpy()
    evaluated=solve_grid(33,49,steps=steps,m=m,frozen=frozen)
    held,bd=grid(33,49);test=held.reshape(-1,2)
    pred=critics[0](torch.as_tensor(test)).detach().numpy().reshape(33,49)
    error=abs(pred-evaluated['values'][0]);gaps=[];residuals=[];actions=action_mesh((7,7,11))
    for n in range(steps):
        pol=frozen(n,test);qpi,_,_,_=backup(evaluated['values'][n+1],test,pol,h,m);best=qpi.copy()
        for aa in np.array_split(actions,math.ceil(len(actions)/32)):
            q,_,_,_=backup(evaluated['values'][n+1],test[:,None,:],aa[None,:,:],h,m);best=np.maximum(best,q.max(1))
        gaps.append(float(np.max((best-qpi)[~bd.ravel()])))
        cv=critics[n](torch.as_tensor(test)).detach().numpy()
        nv=terminal(held) if n+1==steps else critics[n+1](torch.as_tensor(test)).detach().numpy().reshape(33,49)
        qb,_,_,_=backup(nv,test,pol,h,m);residuals.append(float(np.max(abs(cv-qb)[~bd.ravel()])))
    if outdir is not None:
        payload={}
        for typ,nets in [('actor',actors),('critic',critics[:-1])]:
            for n,net in enumerate(nets):
                for name,val in net.state_dict().items():payload[f'{typ}.{n}.{name}']=val.numpy()
        np.savez_compressed(Path(outdir)/f'weights_seed_{seed}.npz',**payload)
        np.savez_compressed(Path(outdir)/f'neural_policy_seed_{seed}.npz',values=np.array(evaluated['values']),policies=np.array(evaluated['policies']))
    return dict(seed=seed,steps=steps,width=width,train_size=train_size,actor_iters=actor_iters,critic_iters=critic_iters,
                logs=logs,critic_vs_policy_max=float(error.max()),critic_vs_policy_rmse=float(np.sqrt(np.mean(error**2))),
                boundary_error=float(error[bd].max()),sampled_feasible_gain_max=max(gaps),gain_by_date=gaps,
                heldout_evaluation_residual_max=max(residuals),elapsed=time.perf_counter()-start,evaluated=evaluated,
                initial_value=float(interpolate(evaluated['values'][0],np.array([[2.,1.25]]))[0]))
