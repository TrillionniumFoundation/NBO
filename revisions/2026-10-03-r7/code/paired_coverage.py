"""Paired multilevel payoff/coverage audit of frozen R6 policies.

The same finest-grid Brownian increments generate every resolution and method.
Sampling intervals do not include discretization or optimal-value error.
"""
from __future__ import annotations
import hashlib, json, math, sys, time
from pathlib import Path
import numpy as np
import torch
from scipy.stats import norm, t as student
ROOT=Path(__file__).resolve().parents[3]
R6=ROOT/'revisions/2026-09-29-r6';OUT=Path(__file__).resolve().parents[1]/'results'
sys.path.insert(0,str(R6/'code'))
import coupled_diffusion as c
torch.set_default_dtype(torch.float64);torch.set_num_threads(1)

def summary(x):
    x=np.asarray(x,dtype=float);n=len(x);se=float(x.std(ddof=1)/math.sqrt(n));mean=float(x.mean())
    radius=float(student.ppf(.975,n-1))*se
    return dict(mean=mean,standard_error=se,confidence_interval=[mean-radius,mean+radius],paths=n,
                confidence='pointwise 95 percent Student t; Monte Carlo error only')

def all_policy_exit_bound(d,lower=-3.,upper=1.,T=1.):
    p=c.P;nu=math.sqrt(p['idiosyncratic_sigma']**2+p['common_sigma']**2)
    bmin=p['productivity']-p['coupling']-p['upper']-nu**2/2
    bmax=p['productivity']+p['coupling']-p['lower']-nu**2/2
    dl=-lower+min(0.,bmin*T);du=upper-max(0.,bmax*T)
    bound=min(1.,2*d*(norm.sf(dl/(nu*math.sqrt(T)))+norm.sf(du/(nu*math.sqrt(T))))) if min(dl,du)>0 else 1.
    return dict(dimension=d,initial_log_capital=0.,domain=[lower,upper],horizon=T,
                drift_interval=[bmin,bmax],marginal_brownian_volatility=nu,exit_probability_upper_analytic=float(bound),
                scope='any admissible bounded control from the origin; union bound allows correlated coordinates',
                numerical_evaluation='SciPy normal survival function; not outward-rounded probability arithmetic',
                not_implied=['uniform PDE residual inside the box','optimal-value accuracy','zero tail payoff'])

def evaluate(d,seed,method,wide,paths=512):
    steps=1000 if wide else 600
    tag=f'coupled_{method}_d{d}_s{seed}_steps{steps}'+('_wide' if wide else '')
    weights=R6/'results'/f'{tag}_weights.pt'; state=torch.load(weights,map_location='cpu',weights_only=True)
    critic=c.Critic(d);critic.load_state_dict(state['critic']);actor=None
    if method!='direct':actor=c.Actor(d);actor.load_state_dict(state['actor'])
    B=state['B'];fine=160;generator=torch.Generator().manual_seed(20261003+d)
    increments=torch.randn(fine,paths,d+1,generator=generator)/math.sqrt(fine)
    boxes=[(-.5,.5),(-1.5,.5),(-3.,.5),(-3.,1.)]
    rows=[];raw={};start=time.perf_counter()
    initial=float(critic(torch.zeros(1,d+1)).detach().item())
    for nsteps in [40,80,160]:
        dw=increments.reshape(nsteps,fine//nsteps,paths,d+1).sum(dim=1)
        h=1/nsteps;y=torch.zeros(paths,d);payoff=torch.zeros(paths,1)
        exits=np.zeros((len(boxes),paths),bool);occupancy=np.zeros((len(boxes),paths),int)
        for n in range(nsteps):
            tx=torch.cat([torch.full((paths,1),n*h),y],dim=1)
            if actor is None:
                _,_,_,grad=c.first_jet(critic,tx);m=c.maximizing_action(grad.detach()).detach()
            else:
                with torch.no_grad():m=actor(tx)
            with torch.no_grad():
                yy=y.numpy()
                for j,(lo,hi) in enumerate(boxes):
                    outside=np.any((yy<lo)|(yy>hi),axis=1);occupancy[j]+=outside;exits[j]|=outside
                payoff+=math.exp(-c.P['discount']*n*h)*h*c.flow(y,m)
                y+=c.drift(y,m,B)*h+c.P['idiosyncratic_sigma']*dw[n,:,:d]+c.P['common_sigma']*dw[n,:,d:]
        with torch.no_grad():payoff+=math.exp(-c.P['discount'])*c.terminal(y)
        for j,(lo,hi) in enumerate(boxes):exits[j]|=np.any((y.numpy()<lo)|(y.numpy()>hi),axis=1)
        z=payoff.numpy().ravel();raw[f'payoff_{nsteps}']=z;raw[f'exits_{nsteps}']=exits
        raw[f'occupancy_counts_{nsteps}']=occupancy;raw[f'terminal_states_{nsteps}']=y.numpy()
        rows.append(dict(steps=nsteps,payoff=summary(z),initial_critic=initial,critic_minus_payoff=initial-float(z.mean()),
                         observed_exit_frequency=exits.mean(axis=1).tolist(),
                         mean_fraction_grid_times_outside=(occupancy/nsteps).mean(axis=1).tolist()))
    report=dict(source_model=tag,source_weights_sha256=hashlib.sha256(weights.read_bytes()).hexdigest(),
        dimension=d,seed=seed,method=method,wide=wide,boxes=boxes,finest_brownian_seed=20261003+d,
        resolutions=rows,paired_step_differences={f'{b}_minus_{a}':summary(raw[f'payoff_{b}']-raw[f'payoff_{a}']) for a,b in [(40,80),(80,160)]},
        seconds=time.perf_counter()-start,continuous_time_bias_bound=None,global_optimal_value_bound=None,
        all_policy_coverage=all_policy_exit_bound(d))
    OUT.mkdir(parents=True,exist_ok=True);np.savez_compressed(OUT/f'coverage_{tag}.npz',**raw)
    (OUT/f'coverage_{tag}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(model=tag,seconds=report['seconds'],finest=rows[-1])),flush=True)
    return report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--dimension',type=int);p.add_argument('--seed',type=int);p.add_argument('--method');p.add_argument('--wide',action='store_true');a=p.parse_args()
    if a.dimension: evaluate(a.dimension,a.seed or 11,a.method or 'nbo_exact',a.wide)
    else:
        reports=[evaluate(d,s,m,w) for d in [10,20] for s in [11,29,47] for m in ['nbo_exact','direct'] for w in [False,True]]
        (OUT/'coverage_execution.json').write_text(json.dumps([dict(source_model=r['source_model'],seconds=r['seconds']) for r in reports],indent=2)+'\n')
