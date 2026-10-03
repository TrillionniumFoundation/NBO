"""Post-R7-review matched comparisons on the unchanged finite economies.

The gated critic is a DGM-style architecture fitted to finite Bellman targets,
not a claim to implement a mesh-free DGM differential-residual solver. The
Chebyshev comparator exploits the same two-state geometry. Both use exhaustive
finite actions, whose costs are charged. Historical evidence is read-only.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,time,resource
from pathlib import Path
import numpy as np
import torch
from torch import nn
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-10-03-r7/code'))
from finite_study import Net,NDU,Game,fit_critic,finite_certificate,put_weights
from numpy.polynomial.chebyshev import chebvander2d
OUT=Path(__file__).resolve().parents[1]/'results'

class Gated(nn.Module):
    def __init__(self,width=32,layers=2):
        super().__init__();self.initial=nn.Linear(2,width)
        self.x=nn.ModuleList([nn.Linear(2,4*width) for _ in range(layers)])
        self.s=nn.ModuleList([nn.Linear(width,3*width) for _ in range(layers)])
        self.h=nn.ModuleList([nn.Linear(width,width) for _ in range(layers)])
        self.final=nn.Linear(width,1)
    def forward(self,x):
        s=torch.tanh(self.initial(x))
        for xx,ss,hh in zip(self.x,self.s,self.h):
            xz,xg,xr,xh=xx(x).chunk(4,dim=1);sz,sg,sr=ss(s).chunk(3,dim=1)
            z=torch.sigmoid(xz+sz);g=torch.sigmoid(xg+sg);r=torch.sigmoid(xr+sr)
            h=torch.tanh(xh+hh(s*r));s=(1-g)*h+z*s
        return self.final(s)

def save(tag,report,arrays):
    OUT.mkdir(exist_ok=True,parents=True);p=OUT/f'{tag}.npz';np.savez_compressed(p,**arrays)
    report.update(raw_file=p.name,raw_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (OUT/f'{tag}.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report),flush=True);return report

def ndu(seed=11,method='gated',degree=10):
    torch.manual_seed(seed);begin=time.perf_counter();m=NDU();construction=time.perf_counter()-begin
    xx=np.c_[(m.points[:,0]-2.1)/.9,2*(m.points[:,1]-m.ys[0])/(m.ys[-1]-m.ys[0])-1];x=torch.tensor(xx)
    lift=(m.points[:,1]-m.ys[0])*(m.ys[-1]-m.points[:,1]);rows=np.arange(m.N)
    net=Gated() if method=='gated' else None
    if method=='chebyshev':
        design=lift[:,None]*chebvander2d(xx[:,0],xx[:,1],[degree,degree]);inverse=np.linalg.pinv(design,rcond=1e-12)
    v=np.empty((m.steps+1,m.N));v[-1]=m.g;pi=np.empty((m.steps,m.N),int);snap={};history=[]
    counters=dict(actor_gradients=0,critic_gradients=0,critic_closures=0,polish_rollbacks=0)
    times=dict(all_action_oracle=0.,critic=0.,verification=0.,classical_reference=0.)
    begin=time.perf_counter()
    for t in range(m.steps-1,-1,-1):
        s=time.perf_counter();q=m.Q(v[t+1]);pi[t]=q.argmax(axis=1);target=q[rows,pi[t]];times['all_action_oracle']+=time.perf_counter()-s
        s=time.perf_counter()
        if net is not None:
            v[t]=fit_critic(net,x,m.g,lift,target,480,300,counters);put_weights(snap,net,f'critic_t{t}_')
        else:
            coef=inverse@(target-m.g);v[t]=m.g+design@coef;snap[f'coefficients_t{t}']=coef
        times['critic']+=time.perf_counter()-s;history.append(dict(t=t,residual=float(np.max(abs(v[t]-target)))))
    training=time.perf_counter()-begin
    s=time.perf_counter();cert,env=finite_certificate(m,pi);times['verification']=time.perf_counter()-s
    s=time.perf_counter();ref,refpol,_=m.reference();times['classical_reference']=time.perf_counter()-s
    return save(f'comparison_ndu_{method}_s{seed}'+(f'_d{degree}' if method=='chebyshev' else ''),dict(
        study='ndu_comparator',method=method,seed=seed,degree=degree if method=='chebyshev' else None,
        state_grid=[m.nu,m.nx],steps=m.steps,actions=m.A,construction_seconds=construction,
        training_seconds=training,timings=times,training_all_action_backups=m.steps,
        training_action_queries=m.steps*m.N*m.A,certificate=cert,
        value_error=float(np.max(abs(v-ref))),target=.1,target_pass=max(cert['payoff_loss_upper'])<=.1,
        counters=counters,history=history,continuous_state_action_time_error=None,
        parameter_count=sum(p.numel() for p in net.parameters()) if net is not None else (degree+1)**2,
        architecture_scope='gated finite Bellman regression, not differential DGM' if net is not None else 'tensor Chebyshev least squares with hard wealth boundary'),
        dict(values=v,policy=pi,reference=ref,**env,**snap))

def game(seed=11,market=1.,method='direct'):
    torch.manual_seed(seed);begin=time.perf_counter();m=Game(market=market);construction=time.perf_counter()-begin
    x=torch.tensor(2*(m.points-m.grid[0])/(m.grid[-1]-m.grid[0])-1)
    one=4*(m.points-m.grid[0])*(m.grid[-1]-m.points)/(m.grid[-1]-m.grid[0])**2;lift=one.prod(axis=1)
    critics=[Net(1),Net(1)];rows=np.arange(m.N);v=np.empty((m.steps+1,m.N,2));v[-1]=m.g
    pi=np.empty((m.steps,m.N,2),int);snap={};history=[]
    counters=dict(actor_gradients=0,critic_gradients=0,critic_closures=0,polish_rollbacks=0)
    times=dict(all_action_oracle=0.,critic=0.,verification=0.);begin=time.perf_counter()
    for t in range(m.steps-1,-1,-1):
        s=time.perf_counter();q=[m.Q(v[t+1,:,i],i) for i in [0,1]]
        gaps=[q[0].max(axis=1,keepdims=True)-q[0],q[1].max(axis=2,keepdims=True)-q[1]]
        joint=np.maximum(*gaps);pure=joint<=1e-11;exists=pure.any(axis=(1,2))
        index=np.where(exists,pure.reshape(m.N,-1).argmax(axis=1),joint.reshape(m.N,-1).argmin(axis=1))
        pi[t]=np.c_[index//m.A,index%m.A];times['all_action_oracle']+=time.perf_counter()-s
        s=time.perf_counter()
        for i in [0,1]:
            target=q[i][rows,pi[t,:,0],pi[t,:,1]]
            if method=='direct':
                v[t,:,i]=fit_critic(critics[i],x,m.g[:,i],lift,target,480,300,counters)
                put_weights(snap,critics[i],f'critic{i}_t{t}_')
            elif method=='classical':v[t,:,i]=target
            else:raise ValueError(method)
        times['critic']+=time.perf_counter()-s
        history.append(dict(t=t,missing_pure=int((~exists).sum()),stage_defect=float(joint[rows,pi[t,:,0],pi[t,:,1]].max())))
    training=time.perf_counter()-begin;s=time.perf_counter();cert,env=finite_certificate(m,pi,True);times['verification']=time.perf_counter()-s
    return save(f'comparison_game_{method}_M{market:g}_s{seed}',dict(study='game_comparator',method=method,market=market,seed=seed,
        construction_seconds=construction,training_seconds=training,timings=times,counters=counters,
        grid=m.n,steps=m.steps,actions_per_player=m.A,training_action_queries=2*m.steps*m.N*m.A*m.A,
        certificate=cert,target=.1,target_pass=max(cert['payoff_loss_upper'])<=.1,history=history,
        missing_pure_stages=sum(h['missing_pure'] for h in history),continuous_equilibrium_error=None),
        dict(values=v,policy=pi,**env,**snap))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('study',choices=['ndu','game']);p.add_argument('--method',default='gated');p.add_argument('--seed',type=int,default=11);p.add_argument('--market',type=float,default=1.);p.add_argument('--degree',type=int,default=10)
    a=p.parse_args();ndu(a.seed,a.method,a.degree) if a.study=='ndu' else game(a.seed,a.market,a.method)
