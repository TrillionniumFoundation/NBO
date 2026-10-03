"""R11 block Bellman policy evaluation with rollout-value and costate targets.

Uses the unchanged R10 capital model. No optimal-policy labels or online
search are used by the actor. Direct-policy and linear methods are explicit
comparison algorithms, not re-labelled NBO computations.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, resource, sys, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r10/code'))
from tube_neural import Actor, Critic, P, CHI, coupling, schedule, terminal, flow, drift, first_jet, greedy
R=Path(__file__).resolve().parents[1]
torch.set_default_dtype(torch.float64); torch.set_num_threads(1)

class LinearActor(nn.Module):
    def __init__(self,d,epsilon=.1):
        super().__init__(); self.net=nn.Linear(d+1,d); self.epsilon=epsilon
        nn.init.zeros_(self.net.weight); nn.init.zeros_(self.net.bias)
    def forward(self,x):
        return schedule(x[:,:1])+self.epsilon*torch.tanh(self.net(torch.cat([x[:,:1],x[:,1:].clamp(-100,100)],1)))

def initial_states(d,n,generator,random_time=True):
    t=torch.rand(n,1,generator=generator) if random_time else torch.zeros(n,1)
    y=-1.5+2*torch.rand(n,d,generator=generator)
    near=-.7*t+.2*torch.randn(n,d,generator=generator)
    y=torch.where(torch.rand(n,1,generator=generator)<.5,near,y)
    return torch.cat([t,y],1)

def rollout(actor,x,B,generator,steps=32,return_gradient=False):
    """Positive-time Euler Bellman evaluation of one frozen feasible policy."""
    start=x.detach().clone().requires_grad_(return_gradient)
    t=start[:,:1]; y=start[:,1:]; h=(P['T']-t)/steps
    reward=torch.zeros(len(x),1); visits=0
    for k in range(steps):
        clock=t+k*h; xx=torch.cat([clock,y],1); m=actor(xx)
        reward=reward+torch.exp(-P['discount']*k*h)*h*flow(y,m)
        z=torch.randn(len(x),B.shape[0]+1,generator=generator)
        noise=P['idiosyncratic_sigma']*z[:,:-1]+P['common_sigma']*z[:,-1:]
        y=y+h*drift(y,m,B)+torch.sqrt(h)*noise;visits+=len(x)
    reward=reward+torch.exp(-P['discount']*(P['T']-t))*terminal(y)
    if return_gradient:
        p=torch.autograd.grad(reward.sum(),start,create_graph=False)[0][:,1:]
        return reward.detach(),p.detach(),visits
    return reward,visits

def validation(actor,d,B,seed,paths=128,steps=64):
    g=torch.Generator().manual_seed(seed);x=torch.zeros(paths,d+1)
    with torch.no_grad(): val,_=rollout(actor,x,B,g,steps)
    return float(val.mean())

def train(d:int,seed:int,method:str,iterations:int=120,epsilon:float=.1,width:int=32,out:Path|None=None,tag:str=''):
    if method not in ['nbo','dpo','linear']:raise ValueError(method)
    out=out or R/'results';out.mkdir(parents=True,exist_ok=True)
    ident=f'{method}_d{d}_s{seed}'+tag
    torch.manual_seed(seed)
    actor=LinearActor(d,epsilon) if method=='linear' else Actor(d,width,epsilon)
    critic=Critic(d,width);B=torch.tensor(coupling(d))
    oa=torch.optim.Adam(actor.parameters(),lr=.003);oc=torch.optim.Adam(critic.parameters(),lr=.002)
    gs=torch.Generator().manual_seed(50000+seed);gb=torch.Generator().manual_seed(90000+seed)
    start=time.perf_counter();history=[];visits=0;critic_updates=0;actor_updates=0
    best=None;bestval=-math.inf;failure=None;validation_seed=610000+seed+d
    for it in range(1,iterations+1):
        try:
            if method=='nbo':
                frozen=copy.deepcopy(actor).eval()
                for p in frozen.parameters():p.requires_grad_(False)
                states=initial_states(d,128,gs)
                value,target,used=rollout(frozen,states,B,gb,32,True);visits+=used
                for _ in range(5):
                    oc.zero_grad(set_to_none=True);xx,v,_,p=first_jet(critic,states)
                    lv=(v-value).square().mean();lg=(d*(p-target)).square().mean();loss=.05*lv+lg
                    if not torch.isfinite(loss):raise FloatingPointError('nonfinite evaluation objective')
                    loss.backward();oc.step();critic_updates+=1
                _,_,_,p=first_jet(critic,states);p=p.detach()
                for _ in range(5):
                    oa.zero_grad(set_to_none=True);m=actor(states)
                    la=-(torch.log(m).mean(1,keepdim=True)-P['adjustment']/2*m.mean(1,keepdim=True).square()-(m*p).sum(1,keepdim=True)).mean()
                    if not torch.isfinite(la):raise FloatingPointError('nonfinite actor objective')
                    la.backward();oa.step();actor_updates+=1
                lossval=float(lv.detach());lossgrad=float(lg.detach())
            else:
                oa.zero_grad(set_to_none=True);states=initial_states(d,128,gs)
                ret,used=rollout(actor,states,B,gb,32,False);visits+=used;loss=-ret.mean()
                if not torch.isfinite(loss):raise FloatingPointError('nonfinite direct return')
                loss.backward();oa.step();actor_updates+=1;lossval=float(loss.detach());lossgrad=None
            if it%20==0 or it==iterations:
                score=validation(actor,d,B,validation_seed)
                history.append(dict(iteration=it,seconds=time.perf_counter()-start,validation_return=score,value_loss=lossval,costate_loss=lossgrad,simulation_state_visits=visits,critic_updates=critic_updates,actor_updates=actor_updates))
                snap=dict(actor=copy.deepcopy(actor.state_dict()),critic=copy.deepcopy(critic.state_dict()))
                torch.save(dict(**snap,dimension=d,method=method,width=width,epsilon=epsilon,iteration=it),out/f'{ident}_k{it}.pt')
                if score>bestval:bestval=score;best=(it,snap)
        except Exception as exc:failure=f'{type(exc).__name__}: {exc}';break
    if best is None:
        row=dict(id=ident,dimension=d,seed=seed,method=method,history=history,failure=failure or 'no checkpoint',weights_sha256=None,requested_iterations=iterations)
        (out/f'{ident}.json').write_text(json.dumps(row,indent=2)+'\n');return row
    it,snap=best;path=out/f'{ident}.pt'
    torch.save(dict(**snap,dimension=d,method=method,width=width,epsilon=epsilon,iteration=it),path)
    row=dict(id=ident,dimension=d,seed=seed,method=method,requested_iterations=iterations,selected_iteration=it,epsilon=epsilon,width=width,history=history,failure=failure,seconds=time.perf_counter()-start,validation_seed=validation_seed,
             validation_rule='highest fixed 128-path validation return among every-20-iteration checkpoints; final-test shocks unused',simulation_state_visits=visits,critic_updates=critic_updates,actor_updates=actor_updates,weights_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,training_scope='Euler Bellman policy evaluation; no optimizer convergence or continuous-time accuracy assertion')
    (out/f'{ident}.json').write_text(json.dumps(row,indent=2,allow_nan=False)+'\n');print(json.dumps(row),flush=True);return row

class GreedyPolicy(nn.Module):
    """Validation-tuned, projected critic greedification; not a neural actor."""
    def __init__(self,critic,mode='direct_tube',mix=1.,epsilon=.1):
        super().__init__();self.critic=critic;self.mode=mode;self.mix=mix;self.epsilon=epsilon
    def forward(self,x):
        with torch.enable_grad():
            xx=x.detach().requires_grad_(True);v=self.critic(xx)
            p=torch.autograd.grad(v.sum(),xx,create_graph=False)[0][:,1:].detach()
        center=schedule(x[:,:1].detach())
        m=greedy(p,x[:,:1].detach(),self.epsilon if self.mode=='direct_tube' else None)
        return (center+(self.mix*(m-center)).clamp(-self.epsilon,self.epsilon)).detach()

def load(path:Path):
    state=torch.load(path,map_location='cpu',weights_only=True);d=state['dimension']
    c=Critic(d,state['width']);c.load_state_dict(state['critic']);c.eval()
    if state['method']=='greedy':a=GreedyPolicy(c,state['mode'],state['mix'],state['epsilon'])
    else:
        a=LinearActor(d,state['epsilon']) if state['method']=='linear' else Actor(d,state['width'],state['epsilon']);a.load_state_dict(state['actor'])
    a.eval();return a,c,state

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dimension',type=int,default=10);p.add_argument('--seed',type=int,default=2027);p.add_argument('--method',default='nbo');p.add_argument('--iterations',type=int,default=120);p.add_argument('--development',action='store_true')
    a=p.parse_args();train(a.dimension,a.seed,a.method,a.iterations,out=R/'development' if a.development else None)
