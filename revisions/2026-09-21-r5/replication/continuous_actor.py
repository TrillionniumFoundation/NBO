"""R5 label-free continuous proposals and independently evaluated safeguards.
Training never enumerates finite actions and never receives optimal labels.
R4 primitives and transition functions are imported unchanged. The finite audit
uses A_h plus the frozen proposal at each state/date; it is not a continuum audit.
"""
from __future__ import annotations
import sys, json, time, math, resource
from pathlib import Path
from dataclasses import asdict
import numpy as np
import torch
from torch import nn
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-21-r4/replication'))
import solver as old
OUT=Path(__file__).resolve().parents[1]/'results'
torch.set_num_threads(1)

class ContinuousActor(old.MLP):
    def __init__(self,width=48): super().__init__(3,width)
    def forward(self,s):
        return s.new_tensor([.05,-.2,-.5])+s.new_tensor([.75,.4,1.3])*super().forward(s).sigmoid()

def q_direct(s,a,vg,t,cfg):
    """Differentiable target: one continuous action, four shocks per state."""
    z=s.new_tensor([[-1.,-1.],[-1.,1.],[1.,-1.],[1.,1.]])
    ss=s[:,None,:]; c,th,p=[a[:,j,None] for j in range(3)]
    du=th*cfg.dt+cfg.su*math.sqrt(cfg.dt)*z[:,0]
    dx=((cfg.r+cfg.excess*p)*ss[...,1]-c)*cfg.dt
    dx=dx+cfg.sx*p*ss[...,1]*math.sqrt(cfg.dt)*(cfg.corr*z[:,0]+math.sqrt(1-cfg.corr**2)*z[:,1])
    inc=torch.stack([du,dx],-1); y=ss+inc; tau=torch.ones_like(dx)
    for j,lo,hi in [(0,cfg.ulo,cfg.uhi),(1,cfg.xlo,cfg.xhi)]:
        d=inc[...,j]; safe=torch.where(d.abs()>1e-12,d,torch.ones_like(d))
        frac=torch.where(y[...,j]<lo,(lo-ss[...,j])/safe,
             torch.where(y[...,j]>hi,(hi-ss[...,j])/safe,torch.ones_like(d)))
        tau=torch.minimum(tau,frac)
    tau=tau.clamp(0,1); hit=ss+tau[...,None]*inc
    f=(hit-hit.new_tensor([cfg.ulo,cfg.xlo]))/hit.new_tensor([cfg.uhi-cfg.ulo,cfg.xhi-cfg.xlo])
    f=f*hit.new_tensor([cfg.nu-1,cfg.nx-1]); idx=f.floor().long()
    iu=idx[...,0].clamp(0,cfg.nu-2); ix=idx[...,1].clamp(0,cfg.nx-2)
    wu=(f[...,0]-iu).clamp(0,1); wx=(f[...,1]-ix).clamp(0,1); v=vg.reshape(cfg.nu,cfg.nx)
    cont=(1-wu)*((1-wx)*v[iu,ix]+wx*v[iu,ix+1])+wu*((1-wx)*v[iu+1,ix]+wx*v[iu+1,ix+1])
    settle=-.02*(hit[...,0]-2)**2+.1*hit[...,1].log()-cfg.fee*(cfg.T-t-cfg.dt*tau)
    cont=torch.where(tau>=1-1e-7,cont,settle)
    flow=c**(1-ss[...,0])/(1-ss[...,0])-.5*cfg.k*th**2
    disc=torch.exp(-cfg.rho*cfg.dt*tau)
    return (-torch.expm1(-cfg.rho*cfg.dt*tau)/cfg.rho*flow+disc*cont).mean(-1)

def evaluate(cfg,policy):
    """O(N*S*4) policy evaluation; no optimal action search."""
    ss,bd=old.states(cfg); V=np.empty((cfg.n+1,len(ss))); V[-1]=old.settlement(cfg.T,ss,cfg)
    for n in reversed(range(cfg.n)):
        V[n]=old.q_numpy(ss,policy[n],V[n+1],n*cfg.dt,cfg)
        V[n,bd]=old.settlement(n*cfg.dt,ss[bd],cfg)
    return V

def audit(cfg,policy,proposals,V=None):
    """Advantage envelope. No optimal value is an input."""
    ss,bd=old.states(cfg); aa=old.actions(cfg); V=evaluate(cfg,policy) if V is None else V
    pre=old.transition_numpy(ss[:,None,:],aa[None,:,:],cfg)
    greedy=np.empty_like(policy); gaps=np.zeros_like(V[:-1]); scalar=0.; upper=np.zeros_like(V)
    discount=math.exp(-cfg.rho*cfg.dt)
    for n in reversed(range(cfg.n)):
        q=old.q_numpy(ss[:,None,:],aa[None,:,:],V[n+1],n*cfg.dt,cfg,pre)
        ind=q.argmax(-1); best=q[np.arange(len(ss)),ind]
        qp=old.q_numpy(ss,proposals[n],V[n+1],n*cfg.dt,cfg)
        greedy[n]=np.where((qp>best)[:,None],proposals[n],aa[ind])
        gaps[n]=np.maximum(np.maximum(best,qp)-V[n],0); gaps[n,bd]=0
        scalar=float(gaps[n].max())+discount*scalar
        hit,frac,_=pre
        pu=np.mean((frac>=1-1e-12)*old.interp(upper[n+1],hit,cfg),axis=-1).max(-1)
        hp,fp,_=old.transition_numpy(ss,proposals[n],cfg)
        pup=np.mean((fp>=1-1e-12)*old.interp(upper[n+1],hp,cfg),axis=-1)
        upper[n]=gaps[n]+discount*np.maximum(pu,pup); upper[n,bd]=0
    return dict(V=V,gaps=gaps,greedy=greedy,uniform=scalar,localized=upper)

def safeguard(cfg,proposals,target=.05):
    """Positive-gain policy correction, terminated by the envelope, not V*."""
    policy=proposals.copy(); history=[]; ss,bd=old.states(cfg); start=time.perf_counter()
    for k in range(cfg.n+1):
        aud=audit(cfg,policy,proposals); b=float(aud['localized'][0].max())
        history.append(dict(sweep=k,uniform_bound=aud['uniform'],localized_bound=b,
            max_one_step_gain=float(aud['gaps'].max()),
            overridden_fraction=float(np.any(abs(policy[:,~bd]-proposals[:,~bd])>1e-10,axis=-1).mean())))
        if b<=target+1e-10: break
        bad=aud['gaps']>1e-12
        policy=np.where(bad[...,None],aud['greedy'],policy)
    return policy,aud,history,time.perf_counter()-start

def independent_optimum(cfg,proposals):
    """Only called AFTER termination, to audit the certificate independently."""
    ss,bd=old.states(cfg); aa=old.actions(cfg); V=np.empty((cfg.n+1,len(ss)))
    V[-1]=old.settlement(cfg.T,ss,cfg); pre=old.transition_numpy(ss[:,None,:],aa[None,:,:],cfg)
    for n in reversed(range(cfg.n)):
        q=old.q_numpy(ss[:,None,:],aa[None,:,:],V[n+1],n*cfg.dt,cfg,pre).max(-1)
        qp=old.q_numpy(ss,proposals[n],V[n+1],n*cfg.dt,cfg)
        V[n]=np.maximum(q,qp); V[n,bd]=old.settlement(n*cfg.dt,ss[bd],cfg)
    return V

def train(cfg,seed=0,width=48,actor_steps=600,critic_steps=800,lr=.004,tag=None):
    torch.manual_seed(seed); ss,bd=old.states(cfg); st=torch.tensor(ss[~bd],dtype=torch.float32)
    sg=torch.tensor(ss,dtype=torch.float32); nxt=old.Terminal(); actors=[None]*cfg.n; critics=[None]*cfg.n
    logs=[]; start=time.perf_counter()
    for n in reversed(range(cfg.n)):
        for p in nxt.parameters(): p.requires_grad_(False); p.grad=None
        with torch.no_grad(): vg=nxt(sg).detach()
        actor=ContinuousActor(width)
        if n<cfg.n-1: actor.load_state_dict(actors[n+1].state_dict())
        opt=torch.optim.Adam(actor.parameters(),lr=lr)
        for it in range(actor_steps):
            opt.zero_grad(set_to_none=True); loss=-q_direct(st,actor(st),vg,n*cfg.dt,cfg).mean()
            loss.backward(); opt.step()
        with torch.no_grad(): target=q_direct(st,actor(st),vg,n*cfg.dt,cfg).detach()
        crit=old.Critic(n*cfg.dt,cfg,width)
        if n<cfg.n-1: crit.net.load_state_dict(critics[n+1].net.state_dict())
        opt=torch.optim.Adam(crit.parameters(),lr=lr)
        for it in range(critic_steps):
            opt.zero_grad(set_to_none=True); loss=(crit(st)-target).square().mean(); loss.backward(); opt.step()
        opt=torch.optim.LBFGS(crit.parameters(),lr=.8,max_iter=120,line_search_fn='strong_wolfe')
        def closure():
            opt.zero_grad(set_to_none=True); loss=(crit(st)-target).square().mean(); loss.backward(); return loss
        opt.step(closure)
        with torch.no_grad(): rmse=float((crit(st)-target).square().mean().sqrt())
        logs.append(dict(date=n,critic_rmse=rmse,critic_gradient_leak=any(p.grad is not None for p in nxt.parameters())))
        actors[n]=actor; critics[n]=crit; nxt=crit
    train_seconds=time.perf_counter()-start
    with torch.no_grad(): proposal=np.stack([a(sg).numpy() for a in actors]).astype(float)
    rawV=evaluate(cfg,proposal); policy,aud,history,audit_seconds=safeguard(cfg,proposal)
    ts=time.perf_counter(); optimal=independent_optimum(cfg,proposal); oracle_seconds=time.perf_counter()-ts
    met=dict(tag=tag or f'n{cfg.n}_s{seed}_w{width}_a{actor_steps}_c{critic_steps}_lr{lr:g}',
       seed=seed,config=asdict(cfg),width=width,actor_steps=actor_steps,critic_steps=critic_steps,learning_rate=lr,
       training_seconds=train_seconds,audit_seconds=audit_seconds,oracle_seconds=oracle_seconds,
       training_action_enumerations=0,actor_outputs=3,training_optimal_labels=0,
       candidate_economy='R4 state/transition model; A_h union each frozen continuous proposal',
       raw_policy_loss_t0=float((optimal[0]-rawV[0]).max()),raw_uniform_bound=history[0]['uniform_bound'],
       raw_localized_bound=history[0]['localized_bound'],certified_bound_t0=float(aud['localized'][0].max()),
       certified_policy_loss_t0=float((optimal[0]-aud['V'][0]).max()),target=.05,
       safeguard_sweeps=history[-1]['sweep'],overridden_fraction=history[-1]['overridden_fraction'],
       raw_pass=history[0]['localized_bound']<=.05,safeguarded_pass=history[-1]['localized_bound']<=.05,
       gradient_leak=any(x['critic_gradient_leak'] for x in logs),completed=True,
       continuum_certificate=None,float_arithmetic='float64 audit, not interval arithmetic',
       peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    assert met['certified_policy_loss_t0']<=met['certified_bound_t0']+1e-8
    assert not met['gradient_leak']
    OUT.mkdir(parents=True,exist_ok=True); stem=met['tag']
    (OUT/(stem+'.json')).write_text(json.dumps(met,indent=2))
    (OUT/(stem+'_history.json')).write_text(json.dumps(dict(training=logs,safeguard=history),indent=2))
    np.savez_compressed(OUT/(stem+'.npz'),proposal=proposal,policy=policy,raw_value=rawV,
        policy_value=aud['V'],optimal_value=optimal,local_bound=aud['localized'],gaps=aud['gaps'])
    torch.save(dict(config=asdict(cfg),width=width,actors=[a.state_dict() for a in actors],
        critics=[c.state_dict() for c in critics]),OUT/(stem+'.pt'))
    print(json.dumps(met),flush=True); return met

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--seed',type=int,default=0); p.add_argument('--n',type=int,default=6)
    p.add_argument('--actor-steps',type=int,default=600); p.add_argument('--critic-steps',type=int,default=800)
    p.add_argument('--width',type=int,default=48); p.add_argument('--lr',type=float,default=.004)
    a=p.parse_args(); train(old.Config(n=a.n),a.seed,a.width,a.actor_steps,a.critic_steps,a.lr)
