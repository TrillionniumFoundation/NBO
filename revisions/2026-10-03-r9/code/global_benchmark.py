"""Global continuous-economy bounds for the original dense capital model.

These bounds cover every admissible control on R^d. They do not use a neural
residual, a state-space mesh, Riccati structure, or sampled maxima. The lower
bound is attained or improved by an explicit feasible common-consumption
schedule. Historical learned-policy payoffs retain their Euler-bias caveat.
"""
from __future__ import annotations
import hashlib,json,math,sys,time
from pathlib import Path
import numpy as np
import torch
from action_cover import ROOT,OUT,I,exp_i,log_i,down,up
sys.path.insert(0,str(ROOT/'revisions/2026-10-03-r7/code'))
from paired_coverage import summary
import coupled_diffusion as model


def sqrt_i(x):
    if np.any(x.lo<0):raise ValueError('negative square-root argument')
    lo=down(np.sqrt(x.lo));hi=up(np.sqrt(x.hi));lo=np.maximum(lo,0)
    for _ in range(8):
        badlo=I(lo).square().hi>x.lo;badhi=I(hi).square().lo<x.hi
        if not (badlo.any() or badhi.any()):break
        lo=np.where(badlo,np.maximum(down(lo),0),lo);hi=np.where(badhi,up(hi),hi)
    if np.any(I(lo).square().hi>x.lo) or np.any(I(hi).square().lo<x.hi):
        raise ArithmeticError('failed square-root inclusion check')
    return I(lo,hi)


def relaxation(d,panels=16384):
    """Outward rectangle quadrature, not SciPy quadrature with a tolerance."""
    p=model.P;T=I(p['T']);rho=I(p['discount']);k=I(p['coupling']);eta=I(p['adjustment'])
    nodes=np.linspace(0,p['T'],panels+1);t=I(nodes[:-1],nodes[1:]);dt=I(nodes[1:])-I(nodes[:-1])
    e=exp_i(-rho*(T-t));w=(1-e)/rho+e
    m=2/(w+sqrt_i(w.square()+4*eta));m=I(np.clip(m.lo,p['lower'],p['upper']),np.clip(m.hi,p['lower'],p['upper']))
    b0=I(p['productivity'])-(I(p['idiosyncratic_sigma']).square()+I(p['common_sigma']).square())/2
    common=log_i(m)-eta*m.square()/2-w*m
    factor=exp_i(-rho*t)
    upper_integrand=factor*(common+w*(b0+k));lower_integrand=factor*(common+w*(b0-k))
    def integrate(f):
        z=f*dt
        while len(z.lo)>1:
            n=len(z.lo);pad=n%2
            lo=np.r_[z.lo,0.] if pad else z.lo;hi=np.r_[z.hi,0.] if pad else z.hi
            z=I(lo[::2],hi[::2])+I(lo[1::2],hi[1::2])
        return I(z.lo[0],z.hi[0])
    upper=integrate(upper_integrand);lower=integrate(lower_integrand)
    disp=(k*T+I(p['idiosyncratic_sigma'])*sqrt_i((1-I(1)/d)*T)).square()
    lower=lower-I(.03)*exp_i(-rho*T)*disp
    return dict(dimension=d,initial_state='every log capital equals zero',horizon=p['T'],panels=panels,
      global_optimal_upper=float(upper.hi),feasible_schedule_lower=float(lower.lo),
      optimal_value_enclosure=[float(lower.lo),float(upper.hi)],quadrature_upper_bracket=[float(upper.lo),float(upper.hi)],
      width=float((upper-lower).hi),terminal_dispersion_upper=float(disp.hi),
      scope='continuous-time original nonlinear dense economy on R^d, all admissible controls; not a tight neural-policy regret certificate',
      arithmetic='outward elementary arithmetic and polynomial exp/log; square roots checked by interval squaring')


def schedule(t):
    p=model.P;w=(1-math.exp(-p['discount']*(p['T']-t)))/p['discount']+math.exp(-p['discount']*(p['T']-t))
    m=2/(w+math.sqrt(w*w+4*p['adjustment']))
    return max(p['lower'],min(p['upper'],m))


def simulate_schedule(d,paths=512):
    p=model.P;fine=160;B=model.coupling(d);gen=torch.Generator().manual_seed(20261003+d)
    inc=torch.randn(fine,paths,d+1,generator=gen)/math.sqrt(fine);raw={};records=[];start=time.perf_counter()
    for nt in [40,80,160]:
        dw=inc.reshape(nt,fine//nt,paths,d+1).sum(dim=1);h=1/nt;y=torch.zeros(paths,d);pv=torch.zeros(paths,1)
        for n in range(nt):
            m=torch.full_like(y,schedule(n*h))
            pv+=math.exp(-p['discount']*n*h)*h*model.flow(y,m)
            y+=model.drift(y,m,B)*h+p['idiosyncratic_sigma']*dw[n,:,:d]+p['common_sigma']*dw[n,:,d:]
        pv+=math.exp(-p['discount'])*model.terminal(y);a=pv.numpy().ravel();raw[f'payoff_{nt}']=a
        records.append(dict(steps=nt,**summary(a)))
    comparisons=[]
    for method in ['nbo_exact','direct']:
      for seed in [11,29,47]:
        for wide in [False,True]:
            steps=1000 if wide else 600
            name=f'coverage_coupled_{method}_d{d}_s{seed}_steps{steps}'+('_wide' if wide else '')
            src=ROOT/'revisions/2026-10-03-r7/results'/f'{name}.npz'
            z=np.load(src)
            comparisons.append(dict(method=method,seed=seed,wide=wide,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                learned_minus_schedule=summary(z['payoff_160']-raw['payoff_160']),
                interpretation='paired Euler-grid payoff difference; discretization bias not included'))
    return dict(dimension=d,paths=paths,brownian_seed=20261003+d,seconds=time.perf_counter()-start,
      records=records,comparisons=comparisons,continuous_policy_evaluation_error=None),raw


def run():
    bounds=[];sims=[];arrays={};start=time.perf_counter()
    for d in [10,20]:
        for n in [4096,16384]:bounds.append(relaxation(d,n))
        sim,raw=simulate_schedule(d);sims.append(sim);arrays.update({f'd{d}_{k}':v for k,v in raw.items()})
    path=OUT/'GLOBAL_CAPITAL_BENCHMARK.npz';np.savez_compressed(path,**arrays)
    result=dict(bounds=bounds,simulations=sims,seconds=time.perf_counter()-start,raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),parameters=model.P)
    (OUT/'GLOBAL_CAPITAL_BENCHMARK.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
