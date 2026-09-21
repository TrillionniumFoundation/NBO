"""Nonquadratic, cyclically coupled Brownian control: NBO versus PINN-PI.
Both methods use exactly the same nonlinear value class, collocation law,
fixed-policy PDE loss, number of evaluation updates, and initialization.
The PINN-PI comparator uses its analytic greedy action (-2 grad v), whereas NBO
fits a distinct d-output neural actor against a detached value jet. This is our
implementation of the policy-iteration principle, not a run of another author's
software. An independent Cole--Hopf quadrature supplies reference values.
"""
from __future__ import annotations
import argparse, copy, json, math, resource, time
from pathlib import Path
import numpy as np
from scipy.special import ndtri, logsumexp
from scipy.stats import qmc
import torch
from torch import nn
OUT=Path(__file__).resolve().parents[1]/'results'
torch.set_num_threads(1)

def terminal_parts(x):
    d=x.shape[-1]; m=x.sum(-1)/math.sqrt(d); pair=x+torch.roll(x,-1,-1)
    h=.25*torch.cos(m)+.1*torch.sin(pair).sum(-1)
    grad=-.25*torch.sin(m)[:,None]/math.sqrt(d)+.1*(torch.cos(pair)+torch.roll(torch.cos(pair),1,-1))
    lap=-.25*torch.cos(m)-.2*torch.sin(pair).sum(-1)
    return h,grad,lap

class Value(nn.Module):
    """Shallow smooth network with an exact, cheap analytical Laplacian.
    The quadratic part is an explicit common control variate, not the solution:
    cyclic sine interactions and the aggregate cosine remain to be learned.
    """
    def __init__(self,d,width=192):
        super().__init__(); self.d=d
        self.input=nn.Linear(d+1,width); self.output=nn.Linear(width,1)
        nn.init.zeros_(self.output.weight); nn.init.zeros_(self.output.bias)
    def jet(self,t,x):
        tau=1-t; den=1+.4*tau; r2=(x*x).sum(-1); d=self.d
        h,hx,hl=terminal_parts(x)
        z=torch.cat([t[:,None],x],-1); th=self.input(z).tanh(); sp=1-th*th
        w=self.output.weight[0]; wx=self.input.weight[:,1:]; wt=self.input.weight[:,0]
        f=(th*w).sum(-1)+self.output.bias[0]
        ft=(sp*w*wt).sum(-1); fx=(sp*w)@wx
        fl=(-2*th*sp*w*(wx*wx).sum(-1)).sum(-1)
        val=.5*d*den.log()+.1*r2/den+h+tau*f
        vt=-.2*d/den+.04*r2/(den*den)-f+tau*ft
        grad=.2*x/den[:,None]+hx+tau[:,None]*fx
        lap=.2*d/den+hl+tau*fl
        return val,vt,grad,lap
    def forward(self,t,x): return self.jet(t,x)[0]

class Actor(nn.Module):
    def __init__(self,d,width=192):
        super().__init__(); self.net=nn.Sequential(nn.Linear(d+1,width),nn.Tanh(),nn.Linear(width,d))
        nn.init.zeros_(self.net[-1].weight); nn.init.zeros_(self.net[-1].bias)
    def forward(self,t,x):
        return -.4*x/(1+.4*(1-t))[:,None]+self.net(torch.cat([t[:,None],x],-1))

def reference(x,t=0.,powers=(12,14),scrambles=4):
    """Independent NumPy tilted-Gaussian Cole--Hopf integration, no network."""
    x=np.atleast_2d(x); d=x.shape[-1]; tau=1-t; den=1+.4*tau
    rows=[]
    for power in powers:
        reps=[]
        for seed in range(scrambles):
            z=ndtri(qmc.Sobol(d,scramble=True,seed=8800+seed).random_base2(power).clip(1e-14,1-1e-14))
            vals=[]
            for xx in x:
                y=xx/den+math.sqrt(2*tau/den)*z
                h=.25*np.cos(y.sum(-1)/math.sqrt(d))+.1*np.sin(y+np.roll(y,-1,-1)).sum(-1)
                log_expect=logsumexp(-h)-math.log(len(y))
                vals.append(.5*d*math.log(den)+.1*np.sum(xx*xx)/den-log_expect)
            reps.append(vals)
        ar=np.array(reps)
        rows.append(dict(power=power,replicates=ar.tolist(),mean=ar.mean(0).tolist(),
                         scramble_se=(ar.std(0,ddof=1)/math.sqrt(scrambles)).tolist()))
    return rows

def train(d,seed,method,width=192,outer=4,evaluation_steps=800,actor_steps=400,lr=.003):
    torch.manual_seed(seed); value=Value(d,width); actor=Actor(d,width)
    old=None; history=[]; start=time.perf_counter();
    for iteration in range(outer):
        opt=torch.optim.Adam(value.parameters(),lr=lr)
        for step in range(evaluation_steps):
            t=torch.rand(512); x=torch.randn(512,d)*1.25
            with torch.no_grad():
                a=actor(t,x) if method=='nbo' or old is None else -2*old.jet(t,x)[2]
            _,vt,grad,lap=value.jet(t,x)
            residual=vt+lap+(a*grad).sum(-1)+.25*(a*a).sum(-1)
            opt.zero_grad(set_to_none=True); loss=(residual**2).mean(); loss.backward(); opt.step()
        if method=='nbo':
            for p in value.parameters(): p.requires_grad_(False); p.grad=None
            op=torch.optim.Adam(actor.parameters(),lr=lr)
            for step in range(actor_steps):
                t=torch.rand(512); x=torch.randn(512,d)*1.25
                with torch.no_grad(): target=-2*value.jet(t,x)[2]
                a=actor(t,x); loss=(a-target).square().mean()
                op.zero_grad(set_to_none=True); loss.backward(); op.step()
            leak=any(p.grad is not None for p in value.parameters())
            for p in value.parameters(): p.requires_grad_(True)
        else:
            old=copy.deepcopy(value).eval()
            for p in old.parameters(): p.requires_grad_(False)
            leak=False
        with torch.no_grad():
            t=torch.rand(2048); x=torch.randn(2048,d)*1.25
            a=actor(t,x) if method=='nbo' else -2*value.jet(t,x)[2]
            val,vt,grad,lap=value.jet(t,x); residual=vt+lap+(a*grad).sum(-1)+.25*(a*a).sum(-1)
            history.append(dict(iteration=iteration,heldout_residual_rmse=float(residual.square().mean().sqrt()),
                actor_gradient_gap_rmse=float((a+2*grad).square().mean().sqrt()),critic_gradient_leak=leak))
    return value.eval(),actor.eval(),history,time.perf_counter()-start

@torch.no_grad()
def policy_audit(value,actor,method,d,steps=128,paths=4096,seed=9921):
    """Fresh Gaussian rollouts, plus Itô residual control-variate evaluation.
    Both are biased by time discretization; doubling studies report that error
    separately from a Monte Carlo standard error. No uniform PDE bound is inferred.
    """
    gen=torch.Generator().manual_seed(seed); x=torch.zeros(paths,d); dt=1/steps
    cost=torch.zeros(paths); residual_integral=torch.zeros(paths)
    v0=float(value(torch.zeros(1),torch.zeros(1,d))[0])
    for n in range(steps):
        t=torch.full((paths,),n*dt)
        a=actor(t,x) if method=='nbo' else -2*value.jet(t,x)[2]
        _,vt,grad,lap=value.jet(t,x)
        residual_integral += dt*(vt+lap+(a*grad).sum(-1)+.25*a.square().sum(-1))
        cost += dt*.25*a.square().sum(-1)
        x += dt*a+math.sqrt(2*dt)*torch.randn(paths,d,generator=gen)
    cost += .1*x.square().sum(-1)+terminal_parts(x)[0]
    cv=v0+residual_integral
    return dict(steps=steps,paths=paths,value_prediction=v0,objective_mc_mean=float(cost.mean()),
        objective_mc_se=float(cost.std()/math.sqrt(paths)),ito_cv_mean=float(cv.mean()),
        ito_cv_se=float(cv.std()/math.sqrt(paths)),seed=seed), cost.numpy(), cv.numpy()

def main():
    p=argparse.ArgumentParser(); p.add_argument('--d',type=int,default=8); p.add_argument('--seed',type=int,default=30)
    p.add_argument('--method',choices=['nbo','pinnpi'],default='nbo'); p.add_argument('--outer',type=int,default=4)
    p.add_argument('--steps',type=int,default=800); p.add_argument('--actor-steps',type=int,default=400)
    p.add_argument('--width',type=int,default=192); a=p.parse_args(); OUT.mkdir(exist_ok=True)
    tag=f'nonlinear_d{a.d}_s{a.seed}_{a.method}_o{a.outer}_e{a.steps}_a{a.actor_steps}_w{a.width}'
    v,actor,hist,sec=train(a.d,a.seed,a.method,a.width,a.outer,a.steps,a.actor_steps)
    start=time.perf_counter(); refs=reference(np.zeros((1,a.d)))
    checks=[]; raw={}
    for n in (32,64,128):
        check,cost,cv=policy_audit(v,actor,a.method,a.d,n)
        check['loss_estimate_vs_reference']=check['ito_cv_mean']-refs[-1]['mean'][0]
        check['sampling_upper_95']=check['loss_estimate_vs_reference']+1.96*math.sqrt(check['ito_cv_se']**2+refs[-1]['scramble_se'][0]**2)
        checks.append(check); raw[f'cost_{n}']=cost; raw[f'cv_{n}']=cv
    result=dict(tag=tag,dimension=a.d,seed=a.seed,method=a.method,initial_state=[0.]*a.d,
        configuration=vars(a),history=hist,training_seconds=sec,audit_seconds=time.perf_counter()-start,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        reference=refs,policy_audits=checks,terminal_error=0.,
        model='dX=a dt+sqrt(2)dW; minimize E[integral |a|^2/4 dt+g(X_1)]',
        terminal='g(x)=.1|x|^2+.25 cos(sum(x)/sqrt(d))+.1 sum_i sin(x_i+x_(i+1)), cyclic',
        comparator_provenance='in-house PINN policy-iteration implementation with analytic greedy action; not the authors code',
        certificate_status='sampling uncertainty and discretization diagnostics, not uniform continuous policy certification')
    (OUT/(tag+'.json')).write_text(json.dumps(result,indent=2)); np.savez_compressed(OUT/(tag+'.npz'),**raw)
    torch.save(dict(config=vars(a),value=v.state_dict(),actor=actor.state_dict()),OUT/(tag+'.pt'))
    print(json.dumps(result),flush=True)
if __name__=='__main__': main()
