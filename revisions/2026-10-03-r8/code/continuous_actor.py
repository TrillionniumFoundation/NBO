"""R8 continuous-action NDU: train without an exhaustive action oracle.

The underlying economic specification, stopping rule and positive cubature
are inherited from R6. Only the action representation becomes continuous.
The actor receives gradients of its own Bellman payoff, never argmax labels.
The direct comparator optimizes independent statewise actions, not an actor.
All reference maximization is performed AFTER the learned policy is frozen.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, resource, sys, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-29-r6/code'))
sys.path.insert(0,str(ROOT/'revisions/2026-10-03-r7/code'))
from ndu_neural import NDU, model_spec
from finite_study import Net, fit_critic, put_weights
OUT=Path(__file__).resolve().parents[1]/'results'
torch.set_default_dtype(torch.float64);torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)
LO=np.array([.02,0.,-.45]);HI=np.array([.3,1.5,.45])

class Model:
    """No action mesh is constructed by this training-side model."""
    def __init__(self,nu=17,nx=25,steps=20,cost=1.,wealth=(.5,2.)):
        self.nu,self.nx,self.steps,self.cost=nu,nx,steps,cost
        self.us=np.linspace(1.2,3.,nu);self.ys=np.linspace(math.log(wealth[0]),math.log(wealth[1]),nx)
        U,Y=np.meshgrid(self.us,self.ys,indexing='ij');self.points=np.c_[U.ravel(),Y.ravel()]
        self.N=len(self.points);self.h=1/steps;self.q=math.exp(-.04*self.h)
        self.g=np.exp((1-self.points[:,0])*self.points[:,1])/(1-self.points[:,0])
        self.boundary=(self.points[:,1]==self.ys[0])|(self.points[:,1]==self.ys[-1])
        self.x=torch.tensor(self.points);self.active=torch.tensor(~self.boundary)
        self.norm=torch.tensor(np.c_[(self.points[:,0]-2.1)/.9,2*(self.points[:,1]-self.ys[0])/(self.ys[-1]-self.ys[0])-1])
        self.lift=(self.points[:,1]-self.ys[0])*(self.ys[-1]-self.points[:,1])
        self.queries=0
    def qvalue(self,v,actions,count=True):
        # actions (N,3) or (N,K,3); the latter is the direct restart dimension.
        if actions.ndim==2:actions=actions[:,None,:];squeeze=True
        else:squeeze=False
        if actions.shape[0]!=self.N or actions.shape[-1]!=3:raise ValueError('action shape')
        if count:self.queries+=int(np.prod(actions.shape[:-1]))
        u=self.x[:,0,None];y=self.x[:,1,None];m,p,theta=actions.unbind(dim=-1)
        value=self.h*(torch.exp((1-u)*(m.log()+y))/(1-u)-.5*self.cost*theta.square())
        continuation=torch.zeros_like(value)
        for z1,z2 in [(math.sqrt(2),0),(-math.sqrt(2),0),(0,math.sqrt(2)),(0,-math.sqrt(2))]:
            un=u+theta*self.h+.08*math.sqrt(self.h)*z1
            z=(un-self.us[0])%(2*(self.us[-1]-self.us[0]))
            un=self.us[0]+torch.minimum(z,2*(self.us[-1]-self.us[0])-z)
            yn=y+(.02+.06*p-m-.02*p.square())*self.h+.2*p*math.sqrt(self.h)*(-.3*z1+math.sqrt(.91)*z2)
            outside=(yn<self.ys[0])|(yn>self.ys[-1]);yn=yn.clamp(float(self.ys[0]),float(self.ys[-1]))
            fu=(un-self.us[0])/(self.us[1]-self.us[0]);fy=(yn-self.ys[0])/(self.ys[1]-self.ys[0])
            iu=fu.floor().long().clamp(0,self.nu-2);iy=fy.floor().long().clamp(0,self.nx-2)
            wu=(fu-iu).clamp(0,1);wy=(fy-iy).clamp(0,1)
            interp=((1-wu)*(1-wy)*v[iu*self.nx+iy]+wu*(1-wy)*v[(iu+1)*self.nx+iy]
                    +(1-wu)*wy*v[iu*self.nx+iy+1]+wu*wy*v[(iu+1)*self.nx+iy+1])
            terminal=torch.exp((1-un)*yn)/(1-un)
            continuation+=torch.where(outside,terminal,interp)/4
        result=value+self.q*continuation
        result=torch.where(torch.tensor(self.boundary)[:,None],torch.tensor(self.g)[:,None],result)
        return result[:,0] if squeeze else result
    def evaluate(self,actions):
        values=np.empty((self.steps+1,self.N));values[-1]=self.g
        with torch.no_grad():
            for t in range(self.steps-1,-1,-1):values[t]=self.qvalue(torch.tensor(values[t+1]),torch.tensor(actions[t]),False).numpy()
        return values

def bounded(z):return torch.tensor(LO)+(torch.tensor(HI-LO))*(1+torch.tanh(z))/2

def pattern_improve(m, continuation, initial):
    """Continuous local search, with eight corner restarts, no action mesh.

    The corners are merely starting proposals. The algorithm does not provide
    a global bound. Every query, including rejected moves, is counted.
    """
    import itertools
    with torch.no_grad():
        corners=torch.tensor(list(itertools.product([0.,1.],repeat=3)))
        corners=torch.tensor(LO)+torch.tensor(HI-LO)*corners
        candidates=torch.cat([initial[:,None,:],corners[None,:,:].expand(m.N,-1,-1)],dim=1)
        q=m.qvalue(continuation,candidates);pick=q.argmax(dim=1);rows=torch.arange(m.N)
        best=candidates[rows,pick];bestq=q[rows,pick]
        directions=torch.cat([torch.eye(3),-torch.eye(3)],dim=0)
        for step in [.25,.125,.0625,.03125,.015625,.0078125,.00390625,.001953125]:
            for _ in range(2):
                candidates=best[:,None,:]+step*directions[None,:,:]*torch.tensor(HI-LO)
                candidates=torch.maximum(torch.tensor(LO),torch.minimum(torch.tensor(HI),candidates))
                q=m.qvalue(continuation,candidates);pick=q.argmax(dim=1);score=q[rows,pick]
                better=score>bestq;best=torch.where(better[:,None],candidates[rows,pick],best)
                bestq=torch.maximum(score,bestq)
        return best,bestq

def solve(seed=11,method='actor',smoke=False,actor_steps=160,critic_steps=320,polish=300,restarts=8,heads=1,fresh=False,search=False):
    if method not in ['actor','direct']:raise ValueError(method)
    torch.manual_seed(seed);m=Model(9,13,5) if smoke else Model()
    if smoke:actor_steps,critic_steps,polish=25,40,40
    actor=Net(3*heads);critic=Net(1);rows=torch.arange(m.N)
    values=np.empty((m.steps+1,m.N));values[-1]=m.g
    policies=np.empty((m.steps,m.N,3));raw_policies=np.empty_like(policies);saved={};history=[]
    counters=dict(actor_gradients=0,critic_gradients=0,critic_closures=0,polish_rollbacks=0)
    timings=dict(action_optimization=0.,local_search=0.,critic_optimization=0.,reference=0.,policy_evaluation=0.)
    start=time.perf_counter();direct_logits=None
    for t in range(m.steps-1,-1,-1):
        cont=torch.tensor(values[t+1]);begin=time.perf_counter();q0=m.queries
        if method=='actor':
            if fresh:
                nn.init.normal_(actor.f[-1].weight, std=.03)
                with torch.no_grad():
                    actor.f[-1].bias.copy_(torch.linspace(-1.,1.,heads)[:,None].repeat(1,3).reshape(-1))
            opt=torch.optim.Adam(actor.parameters(),lr=.012)
            for step in range(actor_steps):
                opt.zero_grad(set_to_none=True);val=m.qvalue(cont,bounded(actor(m.norm).reshape(m.N,heads,3)))
                loss=-(val[m.active]/(1+torch.tensor(abs(m.g[~m.boundary])))[:,None]).mean()
                if not torch.isfinite(loss):raise FloatingPointError('nonfinite actor objective')
                loss.backward();opt.step();counters['actor_gradients']+=1
            with torch.no_grad():
                choices=bounded(actor(m.norm).reshape(m.N,heads,3));qa=m.qvalue(cont,choices)
                idx=qa.argmax(dim=1);actions=choices[rows,idx];target=qa[rows,idx]
            put_weights(saved,actor,f'actor_t{t}_')
        else:
            # Independent bounded controls at every state: same payoff oracle,
            # same iterations per restart; NO supervised actor is fitted.
            init=torch.randn(m.N,restarts,3)*.8 if direct_logits is None else direct_logits.clone()
            z=nn.Parameter(init);opt=torch.optim.Adam([z],lr=.08)
            for step in range(actor_steps):
                opt.zero_grad(set_to_none=True);val=m.qvalue(cont,bounded(z))
                loss=-(val[m.active]/(1+torch.tensor(abs(m.g[~m.boundary])))[:,None]).mean()
                if not torch.isfinite(loss):raise FloatingPointError('nonfinite direct objective')
                loss.backward();opt.step()
            with torch.no_grad():
                a=bounded(z);q=m.qvalue(cont,a);idx=q.argmax(dim=1);actions=a[rows,idx];target=q[rows,idx]
                direct_logits=z.detach().clone()
        timings['action_optimization']+=time.perf_counter()-begin
        raw_policies[t]=actions.detach().numpy()
        if search:
            begin=time.perf_counter();actions,target=pattern_improve(m,cont,actions)
            timings['local_search']+=time.perf_counter()-begin
        policies[t]=actions.detach().numpy();queries=m.queries-q0
        begin=time.perf_counter()
        values[t]=fit_critic(critic,m.norm,m.g,m.lift,target.detach().numpy(),critic_steps,polish,counters)
        timings['critic_optimization']+=time.perf_counter()-begin
        put_weights(saved,critic,f'critic_t{t}_')
        history.append(dict(t=t,action_queries=queries,training_seconds=time.perf_counter()-start,
            critic_residual=float(abs(values[t]-target.numpy()).max()),**counters))
    training=time.perf_counter()-start
    # Training is now over. References cannot enter the graph above.
    begin=time.perf_counter();pv=m.evaluate(policies);raw_pv=m.evaluate(raw_policies);timings['policy_evaluation']=time.perf_counter()-begin
    begin=time.perf_counter();refmodel=NDU(m.nu,m.nx,m.steps);ref,refpol,classical=refmodel.reference()
    timings['reference']=time.perf_counter()-begin
    # Compare against ALL deviations on the inherited finite grid and the
    # continuous proposal itself; this is a lower bound on continuous regret,
    # not a claimed upper bound on the continuous optimum.
    best=refmodel.g.copy();br=np.empty_like(pv);br[-1]=best
    for t in range(m.steps-1,-1,-1):
        with torch.no_grad():qa=m.qvalue(torch.tensor(best),torch.tensor(policies[t]),False).numpy()
        best=np.maximum(refmodel.Q(best).max(axis=1),qa);br[t]=best
    active=policies[:,~m.boundary];bounds=np.c_[LO,HI]
    report=dict(study='continuous_ndu',seed=seed,method=method,smoke=smoke,
        state_grid=[m.nu,m.nx],steps=m.steps,action_bounds=bounds.tolist(),cost=m.cost,
        actor_steps=actor_steps,critic_steps=critic_steps,polish=polish,restarts=restarts if method=='direct' else 1,heads=heads,fresh=fresh,search=search,
        training_seconds=training,timings=timings,counters=counters,training_action_queries=m.queries,
        exact_argmax_training_labels=0,training_all_action_backups=0,
        reference_value_range=[float(ref[0].min()),float(ref[0].max())],
        finite_reference_minus_policy_max=float(np.max(ref-pv)),
        raw_finite_reference_minus_policy_max=float(np.max(ref-raw_pv)),
        local_search_changed_fraction=float(np.mean(np.any(abs(policies[:,~m.boundary]-raw_policies[:,~m.boundary])>1e-8,axis=-1))),
        augmented_grid_deviation_max=float(np.max(br-pv)),
        own_policy_value_fit_error=float(np.max(abs(values-pv))),
        value_vs_finite_reference_max=float(np.max(abs(values-ref))),
        lower_bound_frequency=np.mean(np.isclose(active,LO,rtol=0,atol=1e-4),axis=(0,1)).tolist(),
        upper_bound_frequency=np.mean(np.isclose(active,HI,rtol=0,atol=1e-4),axis=(0,1)).tolist(),
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        continuous_action_regret_upper=None,continuous_state_time_error=None,history=history,
        diagnostic_target=.1,diagnostic_target_pass=bool(np.max(br-pv)<=.1),
        scope='continuous actions on inherited finite state/time model; finite augmented deviations are lower bounds on continuous regret')
    OUT.mkdir(parents=True,exist_ok=True);tag=f'continuous_{method}_s{seed}'+(f'_steps{actor_steps}' if actor_steps not in [160,25] else '')+(f'_h{heads}_fresh{int(fresh)}' if heads!=1 or fresh else '')+('_search' if search else '')+('_smoke' if smoke else '')
    raw=OUT/f'{tag}.npz';np.savez_compressed(raw,values=values,policy=policies,policy_values=pv,raw_policy=raw_policies,raw_policy_values=raw_pv,
        finite_reference=ref,finite_reference_policy=refpol,augmented_best_response=br,**saved)
    report['raw_sha256']=hashlib.sha256(raw.read_bytes()).hexdigest();report['raw_file']=raw.name
    (OUT/f'{tag}.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='history'},allow_nan=False),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=11);p.add_argument('--method',choices=['actor','direct'],default='actor');p.add_argument('--smoke',action='store_true');p.add_argument('--actor-steps',type=int,default=160)
    p.add_argument('--heads',type=int,default=1);p.add_argument('--fresh',action='store_true');p.add_argument('--search',action='store_true')
    a=p.parse_args();solve(a.seed,a.method,a.smoke,actor_steps=a.actor_steps,heads=a.heads,fresh=a.fresh,search=a.search)
