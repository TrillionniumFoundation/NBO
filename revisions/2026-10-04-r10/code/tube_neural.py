"""Block NBO and matched direct HJB fits in the unchanged capital economy.

The actor is an actual multilayer network, without policy labels or online
search. Its structural tube is certified independently of training success.
"""
from __future__ import annotations
import argparse, hashlib, json, math, resource, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from tube_certificate import P, CHI, coupling

torch.set_default_dtype(torch.float64);torch.set_num_threads(1)
OUT=Path(__file__).resolve().parents[1]/'results'

def schedule(t):
    e=torch.exp(-P['discount']*(P['T']-t));w=(1-e)/P['discount']+e
    return 2/(w+torch.sqrt(w*w+4*P['adjustment']))

def terminal(y):
    mean=y.mean(dim=1,keepdim=True)
    return mean-CHI*((y-mean)**2).mean(dim=1,keepdim=True)

def flow(y,m):
    return (torch.log(m)+y).mean(dim=1,keepdim=True)-P['adjustment']/2*m.mean(dim=1,keepdim=True)**2

def drift(y,m,B):
    return P['productivity']+P['coupling']*torch.tanh(y@B.T)-m-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2

class Net(nn.Module):
    def __init__(self,d,outputs,width=32):
        super().__init__();self.layers=nn.Sequential(nn.Linear(d+1,width),nn.Tanh(),nn.Linear(width,width),nn.Tanh(),nn.Linear(width,outputs))
        nn.init.zeros_(self.layers[-1].weight);nn.init.zeros_(self.layers[-1].bias)
    def forward(self,x):return self.layers(x)

class Critic(nn.Module):
    def __init__(self,d,width=32):super().__init__();self.net=Net(d,1,width)
    def forward(self,tx):
        t=tx[:,:1];y=tx[:,1:];tau=P['T']-t;e=torch.exp(-P['discount']*tau)
        w=(1-e)/P['discount']+e;mean=y.mean(dim=1,keepdim=True)
        return w*mean-CHI*e*((y-mean)**2).mean(dim=1,keepdim=True)+tau*self.net(tx)

class Actor(nn.Module):
    def __init__(self,d,width=32,epsilon=.1):
        super().__init__();self.net=Net(d,d,width);self.epsilon=epsilon
    def forward(self,tx):
        # Clamping is only overflow protection for network inputs; it does not
        # truncate the economic state process or the certificate domain.
        safe=torch.cat([tx[:,:1],tx[:,1:].clamp(-100.,100.)],dim=1)
        return schedule(tx[:,:1])+self.epsilon*torch.tanh(self.net(safe))

def first_jet(critic,states):
    x=states.detach().requires_grad_(True);v=critic(x)
    dv=torch.autograd.grad(v.sum(),x,create_graph=True)[0]
    return x,v,dv[:,:1],dv[:,1:]

def trace_probe(p,x,gen,probes=2):
    terms=[];d=p.shape[1]
    for _ in range(probes):
        z=torch.randn(len(x),d+1,generator=gen)
        q=P['idiosyncratic_sigma']*z[:,:d]+P['common_sigma']*z[:,d:]
        hq=torch.autograd.grad((p*q).sum(),x,create_graph=True,retain_graph=True)[0][:,1:]
        terms.append((hq*q).sum(dim=1,keepdim=True))
    return torch.stack(terms).mean(dim=0)

def greedy(p,t,epsilon=None):
    d=p.shape[1]
    if epsilon is None:low=torch.full_like(t,P['lower']);high=torch.full_like(t,P['upper'])
    else:low=schedule(t)-epsilon;high=schedule(t)+epsilon
    a,b=low.clone(),high.clone()
    for _ in range(44):
        mean=(a+b)/2;den=d*p+P['adjustment']*mean
        m=torch.where(den>0,1/den.clamp_min(1e-30),high.expand_as(p))
        m=torch.maximum(low,torch.minimum(high,m));left=m.mean(dim=1,keepdim=True)>mean
        a=torch.where(left,mean,a);b=torch.where(left,b,mean)
    den=d*p+P['adjustment']*(a+b)/2
    m=torch.where(den>0,1/den.clamp_min(1e-30),high.expand_as(p))
    return torch.maximum(low,torch.minimum(high,m))

def draw_states(gen,d,n):
    return torch.cat([torch.rand(n,1,generator=gen),-1.5+2*torch.rand(n,d,generator=gen)],dim=1)

def action(critic,actor,x,method,epsilon=.1):
    if method=='anchor':return schedule(x[:,:1]).expand(-1,x.shape[1]-1)
    if method=='actor':
        with torch.no_grad():return actor(x)
    xx,_,_,p=first_jet(critic,x)
    return greedy(p.detach(),xx[:,:1].detach(),epsilon if method=='direct_tube' else None).detach()

def diagnostics(critic,actor,method,d,B,epsilon):
    gen=torch.Generator().manual_seed(7881+d);states=draw_states(gen,d,128)
    x,v,vt,p=first_jet(critic,states);hdiag=[]
    for j in range(d):
        h=torch.autograd.grad(p[:,j].sum(),x,create_graph=False,retain_graph=True)[0][:,1:]
        hdiag.append(h)
    h=torch.stack(hdiag,dim=1)
    tr=P['idiosyncratic_sigma']**2*torch.diagonal(h,dim1=1,dim2=2).sum(1,keepdim=True)+P['common_sigma']**2*h.sum((1,2))[:,None]
    m=action(critic,actor,states,method,epsilon)
    r=-vt-flow(x[:,1:],m)-(drift(x[:,1:],m,B)*p).sum(1,keepdim=True)-tr/2+P['discount']*v
    best=greedy(p.detach(),x[:,:1].detach())
    gap=flow(x[:,1:],best)-flow(x[:,1:],m)+((m-best)*p).sum(1,keepdim=True)
    r=r.detach().numpy().ravel();gap=gap.detach().numpy().ravel()
    return dict(residual_rms=float(np.sqrt(np.mean(r*r))),sample_residual_max=float(abs(r).max()),
                sample_full_action_gap_max=float(max(0,gap.max())),terminal_error=0.,
                sampled_action_deviation=float((m-schedule(states[:,:1])).abs().max()),
                scope='128 held-out states; diagnostic only, not used in the continuous certificate'),dict(states=states.numpy(),residual=r,action_gap=gap)

def train(d,seed,method,steps=600,width=32,epsilon=.1):
    if method not in ['actor','direct_tube','direct_full']:raise ValueError(method)
    torch.manual_seed(seed);critic=Critic(d,width);actor=Actor(d,width,epsilon);B=torch.tensor(coupling(d))
    opt=torch.optim.Adam(critic.parameters(),lr=.0015);opta=torch.optim.Adam(actor.parameters(),lr=.002)
    samples=torch.Generator().manual_seed(seed+888);probes=torch.Generator().manual_seed(seed+1800)
    history=[];negative=0;failure=None;start=time.perf_counter();done=0
    try:
        for k in range(steps):
            states=draw_states(samples,d,128);opt.zero_grad(set_to_none=True);opta.zero_grad(set_to_none=True)
            x,v,vt,p=first_jet(critic,states)
            if method=='actor':
                with torch.no_grad():m=actor(x)
            else:m=greedy(p.detach(),x[:,:1].detach(),epsilon if method=='direct_tube' else None).detach()
            det=-vt-flow(x[:,1:],m)-(drift(x[:,1:],m,B)*p).sum(1,keepdim=True)+P['discount']*v
            r1=det-trace_probe(p,x,probes)/2;r2=det-trace_probe(p,x,probes)/2
            loss=(r1*r2).mean()
            if not torch.isfinite(loss):raise FloatingPointError('nonfinite critic loss')
            negative+=int(loss.detach()<0);loss.backward();opt.step()
            if method=='actor':
                opta.zero_grad(set_to_none=True);mm=actor(states)
                la=-(flow(states[:,1:],mm)+(drift(states[:,1:],mm,B)*p.detach()).sum(1,keepdim=True)).mean()
                if not torch.isfinite(la):raise FloatingPointError('nonfinite actor loss')
                la.backward();opta.step()
            done=k+1
            if done%100==0 or done==steps:
                history.append(dict(step=done,seconds=time.perf_counter()-start,critic_loss=float(loss.detach())))
    except Exception as exc:failure=f'{type(exc).__name__}: {exc}'
    training_seconds=time.perf_counter()-start
    finite=all(torch.isfinite(p).all() for p in list(critic.parameters())+list(actor.parameters()))
    if not finite:raise FloatingPointError('nonfinite weights cannot define an admissible saved policy')
    diag,raw=diagnostics(critic,actor,method,d,B,epsilon)
    ident=f'{method}_d{d}_s{seed}';OUT.mkdir(parents=True,exist_ok=True)
    weights=OUT/f'{ident}.pt'
    torch.save(dict(critic=critic.state_dict(),actor=actor.state_dict(),B=B,dimension=d,width=width,epsilon=epsilon,method=method),weights)
    np.savez_compressed(OUT/f'{ident}_diagnostics.npz',**raw)
    # Online timing includes the critic gradient and all bisection iterations
    # for direct policies; inference requires no optimizer for actor/anchor.
    gen=torch.Generator().manual_seed(9001+d);online=draw_states(gen,d,256)
    for _ in range(3):action(critic,actor,online,method,epsilon)
    ts=time.perf_counter()
    for _ in range(30):action(critic,actor,online,method,epsilon)
    online_seconds=(time.perf_counter()-ts)/30
    result=dict(id=ident,method=method,dimension=d,seed=seed,steps=done,requested_steps=steps,width=width,depth=2,batch=128,epsilon=epsilon,
                training_seconds=training_seconds,diagnostics=diag,history=history,failure=failure,
                independent_trace_banks=2,probes_per_bank=2,negative_loss_batches=negative,
                training_state_samples=done*128,greedy_bisection_iterations=done*44 if method!='actor' else 0,
                online_batch_256_seconds=online_seconds,online_action_search=(method!='actor'),
                actor_parameter_count=sum(p.numel() for p in actor.parameters()) if method=='actor' else 0,
                critic_parameter_count=sum(p.numel() for p in critic.parameters()),
                peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                weights_sha256=hashlib.sha256(weights.read_bytes()).hexdigest(),
                structural_certificate_applicable=(method!='direct_full'),
                training_guarantee='none; the architectural regret bound already holds at initialization',
                benchmark='same critic, states, initialization seeds, update count and trace banks; wall time and online costs are separately recorded')
    (OUT/f'{ident}.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ['id','training_seconds','failure','diagnostics']}),flush=True)
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--dimension',type=int,default=10);a.add_argument('--seed',type=int,default=11);a.add_argument('--method',default='actor');a.add_argument('--steps',type=int,default=600);v=a.parse_args()
    train(v.dimension,v.seed,v.method,v.steps)
