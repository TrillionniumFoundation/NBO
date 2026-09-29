"""Generic neural training in a dense nonlinear multi-capital economy.

Neither Riccati/Lyapunov solves nor manufactured solution labels are used.
The trace-product runs actually optimize independent Gaussian HVP banks.
Held-out diagnostics and Monte Carlo estimates are not uniform certificates.
"""
from __future__ import annotations
import argparse, copy, json, math, platform, resource, sys, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-28/code'))
from nbo_core import jet
OUT=Path(__file__).resolve().parents[1]/'results'
torch.set_default_dtype(torch.float64);torch.set_num_threads(1)
P=dict(T=1.,discount=.04,productivity=.10,coupling=.15,idiosyncratic_sigma=.15,common_sigma=.10,adjustment=.2,lower=.02,upper=2.)

def coupling(d):
    rng=np.random.default_rng(401+d);b=rng.normal(size=(d,d));b/=np.linalg.norm(b,axis=1,keepdims=True)
    return torch.tensor(b)

def terminal(y):
    # Cross-sectional dispersion and a dense nonlinear production externality.
    return y.mean(dim=1,keepdim=True)-.03*((y-y.mean(dim=1,keepdim=True))**2).mean(dim=1,keepdim=True)

class Net(nn.Module):
    def __init__(self,d,outputs,width=32):
        super().__init__();self.layers=nn.Sequential(nn.Linear(d+1,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh(),nn.Linear(width,outputs))
    def forward(self,tx):return self.layers(tx)
class Critic(nn.Module):
    def __init__(self,d,width=32):super().__init__();self.net=Net(d,1,width)
    def forward(self,tx):return terminal(tx[:,1:])+(1-tx[:,:1])*self.net(tx)
class Actor(nn.Module):
    def __init__(self,d,width=32):super().__init__();self.net=Net(d,d,width)
    def forward(self,tx):return P['lower']+(P['upper']-P['lower'])*torch.sigmoid(self.net(tx))

def drift(y,m,B):
    return P['productivity']+P['coupling']*torch.tanh(y@B.T)-m-.5*(P['idiosyncratic_sigma']**2+P['common_sigma']**2)
def flow(y,m):
    return (torch.log(m)+y).mean(dim=1,keepdim=True)-.5*P['adjustment']*m.mean(dim=1,keepdim=True)**2

def maximizing_action(p):
    """Unique global maximizer; scalar monotone consistency equation for mean m."""
    d=p.shape[1];lo=torch.full_like(p[:,:1],P['lower']);hi=torch.full_like(lo,P['upper'])
    for _ in range(44):
        mean=(lo+hi)/2;den=d*p+P['adjustment']*mean
        m=torch.where(den>0,1/den.clamp_min(1e-30),torch.full_like(den,P['upper'])).clamp(P['lower'],P['upper'])
        low=m.mean(dim=1,keepdim=True)>mean;lo=torch.where(low,mean,lo);hi=torch.where(low,hi,mean)
    den=d*p+P['adjustment']*(lo+hi)/2
    return torch.where(den>0,1/den.clamp_min(1e-30),torch.full_like(den,P['upper'])).clamp(P['lower'],P['upper'])

def exact_trace(hess):
    return P['idiosyncratic_sigma']**2*torch.diagonal(hess,dim1=1,dim2=2).sum(dim=1,keepdim=True)+P['common_sigma']**2*hess.sum(dim=(1,2))[:,None]

def first_jet(value,tx):
    tx=tx.detach().requires_grad_(True);v=value(tx);dv=torch.autograd.grad(v.sum(),tx,create_graph=True)[0]
    return tx,v,dv[:,:1],dv[:,1:]

def hvp_trace(p,tx,probes,generator):
    d=p.shape[1];traces=[]
    for _ in range(probes):
        z=torch.randn(len(tx),d+1,dtype=tx.dtype,generator=generator)
        direction=P['idiosyncratic_sigma']*z[:,:d]+P['common_sigma']*z[:,d:]
        hp=torch.autograd.grad((p*direction).sum(),tx,create_graph=True,retain_graph=True)[0][:,1:]
        traces.append((hp*direction).sum(dim=1,keepdim=True))
    return torch.stack(traces).mean(dim=0)

def diagnostics(value,actor,d,B,states):
    tx,v,vt,p,hess=jet(value,states);m=actor(tx) if actor is not None else maximizing_action(p.detach())
    H=flow(tx[:,1:],m)+(drift(tx[:,1:],m,B)*p).sum(dim=1,keepdim=True)+.5*exact_trace(hess)-P['discount']*v
    best=maximizing_action(p.detach());gain=flow(tx[:,1:],best)-flow(tx[:,1:],m)+((m-best)*p).sum(dim=1,keepdim=True)
    r=(-vt-H).detach().numpy().ravel();g=gain.detach().numpy().ravel()
    return dict(residual_rms=float(np.sqrt(np.mean(r*r))),residual_max=float(np.max(abs(r))),action_gap_max=float(max(0,np.max(g))),action_gap_mean=float(np.mean(g))),dict(states=states.numpy(),residual=r,gap=g,value=v.detach().numpy().ravel())

def simulate(value,actor,d,B,steps=80,paths=2048,seed=922):
    """Euler policy payoff, common seed across methods; no continuous-payoff claim."""
    gen=torch.Generator().manual_seed(seed+d);y=torch.zeros(paths,d);total=torch.zeros(paths,1);h=1/steps
    for n in range(steps):
        tx=torch.cat([torch.full((paths,1),n*h),y],axis=1)
        if actor is None:
            tx,v,vt,p=first_jet(value,tx);m=maximizing_action(p.detach()).detach()
        else:
            with torch.no_grad():m=actor(tx)
        with torch.no_grad():
            total+=math.exp(-P['discount']*n*h)*h*flow(y,m)
            z=torch.randn(paths,d+1,generator=gen)
            y=y+drift(y,m,B)*h+math.sqrt(h)*(P['idiosyncratic_sigma']*z[:,:d]+P['common_sigma']*z[:,d:])
    total+=math.exp(-P['discount'])*terminal(y);a=total.numpy().ravel()
    return dict(steps=steps,paths=paths,mean=float(a.mean()),standard_error=float(a.std(ddof=1)/math.sqrt(paths)),initial_critic=float(value(torch.zeros(1,d+1)).detach().item())),a

def train(d,seed,method='nbo_exact',steps=600,width=32,lower=-.5):
    if method not in ['nbo_exact','direct','nbo_product','nbo_single']:raise ValueError(method)
    torch.manual_seed(seed);value=Critic(d,width);actor=Actor(d,width);B=coupling(d)
    optimizer=torch.optim.Adam(value.parameters(),lr=.002);opta=torch.optim.Adam(actor.parameters(),lr=.003)
    samplegen=torch.Generator().manual_seed(seed+888);probegen=torch.Generator().manual_seed(seed+1800)
    heldgen=torch.Generator().manual_seed(781+d)
    held=torch.cat([torch.rand(512,1,generator=heldgen),lower+(.5-lower)*torch.rand(512,d,generator=heldgen)],axis=1)
    history=[];start=time.perf_counter();negative=0;numloss=0;failure=None;first_pass=None
    target=dict(residual_rms=.025,action_gap_max=.01)
    try:
        for k in range(steps):
            tx=torch.cat([torch.rand(128,1,generator=samplegen),lower+(.5-lower)*torch.rand(128,d,generator=samplegen)],axis=1)
            optimizer.zero_grad(set_to_none=True)
            if method in ['nbo_exact','direct']:
                tx,v,vt,p,hess=jet(value,tx);tr=exact_trace(hess)
            else:tx,v,vt,p=first_jet(value,tx)
            if method=='direct':m=maximizing_action(p.detach())
            else:
                with torch.no_grad():m=actor(tx)
            deterministic=-vt-flow(tx[:,1:],m)-(drift(tx[:,1:],m,B)*p).sum(dim=1,keepdim=True)+P['discount']*v
            if method in ['nbo_exact','direct']:loss=(deterministic-.5*tr).square().mean()
            elif method=='nbo_product':
                r1=deterministic-.5*hvp_trace(p,tx,2,probegen);r2=deterministic-.5*hvp_trace(p,tx,2,probegen)
                loss=(r1*r2).mean()
            else:loss=(deterministic-.5*hvp_trace(p,tx,4,probegen)).square().mean()
            if not torch.isfinite(loss):raise FloatingPointError('nonfinite training loss')
            negative+=int(float(loss.detach())<0);numloss+=1;loss.backward();optimizer.step()
            if method!='direct':
                opta.zero_grad(set_to_none=True);m=actor(tx.detach());pp=p.detach()
                la=-((drift(tx[:,1:].detach(),m,B)*pp).sum(dim=1,keepdim=True)+flow(tx[:,1:].detach(),m)).mean()
                la.backward();opta.step()
            if (k+1)%100==0 or k==steps-1:
                diag,_=diagnostics(value,None if method=='direct' else actor,d,B,held)
                row=dict(step=k+1,seconds=time.perf_counter()-start,loss=float(loss.detach()),**diag);history.append(row)
                if first_pass is None and diag['residual_rms']<=target['residual_rms'] and diag['action_gap_max']<=target['action_gap_max']:first_pass=row.copy()
    except Exception as exc:failure=f'{type(exc).__name__}: {exc}'
    elapsed=time.perf_counter()-start;diag,arrays=diagnostics(value,None if method=='direct' else actor,d,B,held)
    sims=[];mc={}
    for n in [40,80]:
        sim,payoff=simulate(value,None if method=='direct' else actor,d,B,steps=n);sims.append(sim);mc[f'payoff_n{n}']=payoff
    name=f'coupled_{method}_d{d}_s{seed}_steps{steps}'+('_wide' if lower!=-.5 else '')
    result=dict(model_id=name,parameters=P,dimension=d,brownian_rank=d+1,seed=seed,method=method,width=width,depth=2,steps=steps,batch=128,
      heldout_domain=f't in [0,1], every log capital in [{lower},.5]; 512 fixed random states',
      actual_state_domain='R^d; positive capital by log coordinates; no lateral truncation',
      coupling_matrix=B.numpy().tolist(),seconds=elapsed,peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      trace_probes=(4 if method in ['nbo_product','nbo_single'] else None),negative_batch_loss_fraction=negative/max(1,numloss),
      failure=failure,diagnostic_target=target,first_observed_target=first_pass,diagnostic_pass=diag['residual_rms']<=target['residual_rms'] and diag['action_gap_max']<=target['action_gap_max'],
      diagnostics=diag,terminal_error=0.,simulations=sims,history=history,continuous_domain_certificate=None,
      unchecked=['uniform residual outside sampled states','continuous-time payoff discretization','high-dimensional optimal value reference'])
    torch.save(dict(critic=value.state_dict(),actor=actor.state_dict(),B=B),OUT/f'{name}_weights.pt')
    np.savez_compressed(OUT/f'{name}.npz',**arrays,**mc);(OUT/f'{name}.json').write_text(json.dumps(result,indent=2))
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suite',choices=['smoke','primary','trace','coverage'],default='primary');a=parser.parse_args();OUT.mkdir(exist_ok=True,parents=True)
    if a.suite=='smoke':cases=[(2,11,'nbo_exact',200),(2,11,'direct',200)]
    elif a.suite=='primary':cases=[(d,s,m,600) for d in [2,5,10,20] for s in [11,29,47] for m in ['nbo_exact','direct']]
    elif a.suite=='coverage':cases=[(d,s,m,1000,32,-1.5) for d in [10,20] for s in [11,29,47] for m in ['nbo_exact','direct']]
    else:cases=[(10,s,m,600) for s in [11,29,47] for m in ['nbo_product','nbo_single']]
    records=[]
    for case in cases:
        r=train(*case);records.append(r);print(json.dumps({k:v for k,v in r.items() if k not in ['coupling_matrix','history']}),flush=True)
        (OUT/f'coupled_{a.suite}.json').write_text(json.dumps(records,indent=2))
if __name__=='__main__':main()
