"""A genuinely trained NBO on a nonhomothetic stopped consumption economy.

The old generic differential core is imported, not reimplemented. The reference
is a separate monotone upwind policy-iteration solver. No reference values or
reference policies enter neural training. All optimizers use CPU float64.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, os, platform, resource, sys, time
from pathlib import Path
import numpy as np
import scipy
from scipy.linalg import solve_banded
import torch
from torch import nn
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'revisions/2026-09-28/code'))
from nbo_core import jet, critic_loss, actor_loss
OUT = Path(__file__).resolve().parents[1] / 'results'
torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)
P = dict(lower=.5, upper=2.5, discount=.08, interest=.02,
         income=.12, volatility=.15, c_lower=.02, c_upper=.6)

def bequest(x):
    """Value of an outside retirement annuity, a specified stopping payoff."""
    return np.log(P['income'] + P['discount'] * np.asarray(x)) / P['discount']

class MLP(nn.Module):
    def __init__(self, width=16, depth=2, outputs=1):
        super().__init__()
        layers = [nn.Linear(1, width), nn.Tanh()]
        for _ in range(depth - 1): layers += [nn.Linear(width, width), nn.Tanh()]
        layers.append(nn.Linear(width, outputs))
        self.layers = nn.Sequential(*layers)
    def forward(self, x): return self.layers(x)

class Value(nn.Module):
    def __init__(self, width=16, depth=2):
        super().__init__(); self.network = MLP(width, depth)
    def forward(self, tx):
        x = tx[:, 1:2]; l, u = P['lower'], P['upper']
        z = 2 * (x - l) / (u - l) - 1
        g0, g1 = map(float, bequest([l,u]))
        return g0 + (g1-g0)*(x-l)/(u-l) + (x-l)*(u-x)*self.network(z)

class Actor(nn.Module):
    def __init__(self, width=16, depth=2):
        super().__init__(); self.network = MLP(width, depth)
    def forward(self, tx):
        z = 2 * (tx[:,1:2] - P['lower']) / (P['upper'] - P['lower']) - 1
        return P['c_lower'] + (P['c_upper']-P['c_lower'])*torch.sigmoid(self.network(z))

def maximize(p):
    """Global maximizer of log(c)-c*p, including both binding bounds."""
    if isinstance(p, torch.Tensor):
        return torch.where(p > 0, 1 / p.clamp_min(1e-300),
                           torch.full_like(p, P['c_upper'])).clamp(P['c_lower'],P['c_upper'])
    p = np.asarray(p)
    return np.clip(1/np.maximum(p,1e-300),P['c_lower'],P['c_upper'])

def hamiltonian(tx, c, v, vx, vxx):
    x = tx[:,1:2]
    return (torch.log(c) + (P['income']+P['interest']*x-c)*vx
            + .5*P['volatility']**2*x*x*vxx[:,0,0:1] - P['discount']*v)

def reference(intervals=1280):
    """Continuous-action monotone Markov-chain approximation (not central drift).

    Each upwind region is concave in consumption, so its endpoints and its
    clipped first-order optimum exhaust the feasible global maximum.
    """
    start=time.perf_counter(); x=np.linspace(P['lower'],P['upper'],intervals+1)
    dx=x[1]-x[0]; xi=x[1:-1]; drift0=P['income']+P['interest']*xi
    D=.5*P['volatility']**2*xi**2/dx**2
    g=bequest(x[[0,-1]]); c=np.full(len(xi),.2); previous=None
    for iteration in range(200):
        b=drift0-c; up=D+np.maximum(b,0)/dx; down=D+np.maximum(-b,0)/dx
        ab=np.zeros((3,len(xi))); ab[1]=P['discount']+up+down
        ab[0,1:]=-up[:-1]; ab[2,:-1]=-down[1:]
        rhs=np.log(c); rhs[0]+=down[0]*g[0]; rhs[-1]+=up[-1]*g[1]
        v=np.r_[g[0],solve_banded((1,1),ab,rhs),g[1]]
        dp=(v[2:]-v[1:-1])/dx; dm=(v[1:-1]-v[:-2])/dx
        cut=np.clip(drift0,P['c_lower'],P['c_upper'])
        candidates=np.stack([np.full_like(xi,P['c_lower']),np.full_like(xi,P['c_upper']),cut,
            np.minimum(maximize(dp),cut),np.maximum(maximize(dm),cut)],axis=1)
        bb=drift0[:,None]-candidates
        q=np.log(candidates)+np.where(bb>=0,bb*dp[:,None],bb*dm[:,None])
        new=candidates[np.arange(len(xi)),q.argmax(axis=1)]
        gap=np.max(q.max(axis=1)-(np.log(c)+np.where(b>=0,b*dp,b*dm)))
        if gap<1e-12: break
        if previous is not None and np.max(abs(new-c))<1e-13: break
        previous=c; c=new
    else: raise RuntimeError('reference policy iteration did not converge')
    p=np.gradient(v,dx,edge_order=2); pp=np.gradient(p,dx,edge_order=2)
    c_all=maximize(p); c_all[1:-1]=c
    residual=P['discount']*v[1:-1]-np.log(c)-up*(v[2:]-v[1:-1])-down*(v[:-2]-v[1:-1])
    return dict(x=x,value=v,policy=c_all,gradient=p,hessian=pp,
        iterations=iteration+1,seconds=time.perf_counter()-start,
        discrete_residual=float(np.max(abs(residual))),action_gap=float(max(0,gap)))

def evaluate(v,a,x):
    tx=torch.tensor(np.c_[np.zeros(len(x)),x]); tx,vv,vt,vx,vxx=jet(v,tx)
    c=a(tx) if a is not None else maximize(vx)
    r=-hamiltonian(tx,c,vv,vx,vxx); best=maximize(vx)
    gap=torch.log(best)-best*vx-(torch.log(c)-c*vx)
    return dict(value=vv.detach().numpy().ravel(),policy=c.detach().numpy().ravel(),
        gradient=vx.detach().numpy().ravel(),hessian=vxx.detach().numpy().ravel(),
        residual=r.detach().numpy().ravel(),gap=gap.detach().numpy().ravel())

def export_model(model):
    return [dict(weight=m.weight.detach().numpy().tolist(),bias=m.bias.detach().numpy().tolist())
            for m in model.network.layers if isinstance(m,nn.Linear)]

def train(method,seed,width=16,depth=2,rounds=8,critic_steps=60,actor_steps=40):
    if method not in ('nbo','direct','joint'): raise ValueError(method)
    torch.manual_seed(seed); rng=np.random.default_rng(seed)
    value=Value(width,depth); actor=Actor(width,depth)
    # Equal prespecified cap on LBFGS inner iterations, not equal achieved time.
    total_cap=rounds*(critic_steps+actor_steps)
    nodes=(np.arange(256)+rng.uniform(.1,.9,256))/256
    x=P['lower']+(P['upper']-P['lower'])*nodes
    tx=torch.tensor(np.c_[np.zeros(len(x)),x]); history=[]; counts=dict(critic=0,actor=0,joint=0)
    start=time.perf_counter(); failure=None
    def optimize(parameters,fn,steps,kind):
        optimizer=torch.optim.LBFGS(list(parameters),lr=.8,max_iter=steps,
                                   tolerance_grad=1e-10,tolerance_change=1e-13,
                                   line_search_fn='strong_wolfe')
        def closure():
            optimizer.zero_grad(set_to_none=True); loss=fn()
            if not torch.isfinite(loss): raise FloatingPointError('nonfinite objective')
            loss.backward(); counts[kind]+=1
            return loss
        optimizer.step(closure)
    try:
        for k in range(rounds):
            if method=='nbo':
                optimize(value.parameters(),lambda:critic_loss(value,actor,tx,hamiltonian),critic_steps,'critic')
                optimize(actor.parameters(),lambda:actor_loss(value,actor,tx,hamiltonian),actor_steps,'actor')
            elif method=='direct':
                def loss():
                    z,v,vt,vx,vxx=jet(value,tx); c=maximize(vx).detach()
                    return (-hamiltonian(z,c,v,vx,vxx)).square().mean()
                optimize(value.parameters(),loss,critic_steps+actor_steps,'critic')
            else:
                def joint():
                    z,v,vt,vx,vxx=jet(value,tx); h=hamiltonian(z,actor(z),v,vx,vxx)
                    return h.square().mean()-h.mean()
                optimize(list(value.parameters())+list(actor.parameters()),joint,critic_steps+actor_steps,'joint')
            e=evaluate(value,None if method=='direct' else actor,np.linspace(.5,2.5,513))
            history.append(dict(round=k+1,seconds=time.perf_counter()-start,
                 residual_rms=float(np.sqrt(np.mean(e['residual']**2))),
                 residual_max=float(np.max(abs(e['residual']))),gap_max=float(max(0,np.max(e['gap'])))))
    except Exception as exc:
        failure=f'{type(exc).__name__}: {exc}'
    elapsed=time.perf_counter()-start
    name=f'consumption_{method}_s{seed}_w{width}_d{depth}_r{rounds}_c{critic_steps}_a{actor_steps}'
    model=dict(model_id=name,parameters=P,method=method,seed=seed,width=width,depth=depth,
        boundary_values=bequest([P['lower'],P['upper']]).tolist(),value=export_model(value),actor=None if method=='direct' else export_model(actor),
        collocation_states=x.tolist(),failure=failure,history=history,closure_counts=counts,
        lbfgs_inner_iteration_cap=total_cap,seconds=elapsed,
        peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (OUT/f'{name}.json').write_text(json.dumps(model,indent=2))
    dense=np.linspace(.5,2.5,2561); e=evaluate(value,None if method=='direct' else actor,dense)
    ref=reference(2560); er={k: e[k]-ref[k] for k in ['value','policy','gradient','hessian']}
    interior=slice(4,-4)
    summary=dict(model_id=name,method=method,seed=seed,width=width,depth=depth,
        seconds=elapsed,peak_process_rss_kib=model['peak_process_rss_kib'],failure=failure,
        residual_rms=float(np.sqrt(np.mean(e['residual']**2))),
        residual_max=float(np.max(abs(e['residual']))),gap_max=float(max(0,np.max(e['gap']))),
        value_error_max=float(np.max(abs(er['value']))),value_error_rms=float(np.sqrt(np.mean(er['value']**2))),
        policy_error_max=float(np.max(abs(er['policy'][interior]))),
        gradient_error_max=float(np.max(abs(er['gradient'][interior]))),
        hessian_error_max=float(np.max(abs(er['hessian'][interior]))),
        boundary_lower_error=float(abs(er['value'][0])),boundary_upper_error=float(abs(er['value'][-1])),
        # This is explicitly a diagnostic threshold until interval verification.
        diagnostic_pass=bool(failure is None and np.max(abs(e['residual']))<.01 and np.max(e['gap'])<.002),
        closure_counts=counts,lbfgs_inner_iteration_cap=total_cap,
        certificate=None)
    np.savez_compressed(OUT/f'{name}.npz',x=dense,**e,reference_value=ref['value'],reference_policy=ref['policy'])
    np.savetxt(OUT/f'{name}_trace.csv',np.array([[z[k] for k in ['round','seconds','residual_rms','residual_max','gap_max']] for z in history]),delimiter=',',header='round,seconds,residual_rms,residual_max,gap_max',comments='')
    return summary

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--suite',choices=['primary','sensitivity','smoke'],default='primary')
    args=parser.parse_args(); OUT.mkdir(exist_ok=True,parents=True)
    records=[]
    if args.suite=='primary': cases=[(m,s,16,2,8,60,40) for m in ['nbo','direct','joint'] for s in [11,29,47]]
    elif args.suite=='smoke': cases=[('nbo',11,16,2,4,40,30),('direct',11,16,2,4,40,30)]
    else: cases=[('nbo',11,w,d,8,c,a) for w,d,c,a in [(8,2,60,40),(32,2,60,40),(16,1,60,40),(16,3,60,40),(16,2,80,20),(16,2,40,60)]]
    for case in cases:
        record=train(*case);records.append(record);print(json.dumps(record),flush=True)
        (OUT/f'consumption_{args.suite}.json').write_text(json.dumps(dict(parameters=P,
          environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,cpu_threads=1,platform=platform.platform()),runs=records),indent=2))
    refs=[]
    for n in [320,640,1280,2560]:
        r=reference(n);np.savez_compressed(OUT/f'consumption_reference_n{n}.npz',**r)
        refs.append({k:v for k,v in r.items() if not isinstance(v,np.ndarray)}|{'intervals':n,'value_center':float(r['value'][n//2])})
    (OUT/'consumption_reference.json').write_text(json.dumps(refs,indent=2))
if __name__=='__main__': main()
