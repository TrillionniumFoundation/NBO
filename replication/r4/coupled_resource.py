#!/usr/bin/env python3
"""Coupled stochastic resource allocation with binding simplex constraints.
A convex random-feature neural critic, a neural proposal actor, and a convex
pointwise improvement safeguard are compared with an independently optimized
nonanticipative scenario tree. Frank--Wolfe gaps certify finite-tree references.
"""
import argparse,json,time,math,hashlib
from pathlib import Path
import numpy as np
import torch
from torch import nn
from scipy.optimize import lsq_linear
from solver import fit_lbfgs


def primitives(d):
    A=.8*np.eye(d)+.04*(np.eye(d,k=1)+np.eye(d,k=-1))
    load=np.stack([np.ones(d)*.06,np.linspace(-.04,.04,d)],0)
    signs=np.array([[-1,-1],[-1,1],[1,-1],[1,1]])
    return A,signs@load,.25*d


def project(x,B):
    z=np.maximum(x,0);active=z.sum(-1)>B
    if np.any(active):
        v=np.sort(x[active],axis=-1)[:,::-1];cs=v.cumsum(-1)-B;j=np.arange(1,x.shape[-1]+1)
        rho=(v-cs/j>0).sum(-1)-1;tau=cs[np.arange(len(v)),rho]/(rho+1)
        z[active]=np.maximum(x[active]-tau[:,None],0)
    return z


def fw_gap(x,g,B):
    # min <g,v> over v>=0, sum v<=B.
    return (x*g).sum(-1)-B*np.minimum(g.min(-1),0)


def qcost(x):
    z=x-1;return (z*z).mean(-1)+.2*z.mean(-1)**2


def qgrad(x):
    d=x.shape[-1];z=x-1;return 2*z/d+.4*z.mean(-1)[...,None]/d


class Critic:
    def __init__(self,d,rng,terminal=False):
        self.d=d;self.terminal=terminal
        dirs=np.concatenate([np.eye(d),-np.eye(d),np.ones((1,d))/math.sqrt(d),-np.ones((1,d))/math.sqrt(d),rng.normal(size=(32,d))/math.sqrt(d)])
        self.W=np.repeat(dirs,3,axis=0);self.b=np.tile([-.5,0,.5],len(dirs));self.c=np.zeros(len(self.b));self.lin=np.zeros(d);self.const=0.
    def features(self,x):return np.maximum((x-1)@self.W.T+self.b,0)**2
    def value(self,x):
        return qcost(x) if self.terminal else qcost(x)+(x-1)@self.lin+self.const+self.features(x)@self.c
    def grad(self,x):
        return qgrad(x) if self.terminal else qgrad(x)+self.lin+(2*np.maximum((x-1)@self.W.T+self.b,0)*self.c)@self.W
    def lipschitz(self):
        h=2/self.d*np.eye(self.d)+.4/self.d**2*np.ones((self.d,self.d))
        if not self.terminal:h+=2*self.W.T@(self.c[:,None]*self.W)
        return np.linalg.eigvalsh(h)[-1]
    def fit(self,x,target):
        feat=np.concatenate([np.ones((len(x),1)),x-1,self.features(x)],1);y=target-qcost(x)
        ridge=1e-5;aug=np.vstack([feat,math.sqrt(ridge)*np.eye(feat.shape[1])]);yy=np.r_[y,np.zeros(feat.shape[1])]
        lower=np.r_[np.full(self.d+1,-np.inf),np.zeros(len(self.c))]
        fit=lsq_linear(aug,yy,bounds=(lower,np.full(len(lower),np.inf)),tol=1e-8,max_iter=150,method='bvls')
        self.const=fit.x[0];self.lin=fit.x[1:self.d+1];self.c=np.maximum(fit.x[self.d+1:],0)
        return dict(mse=float(np.mean((self.value(x)-target)**2)),ls_status=int(fit.status),optimality=float(fit.optimality))


def greedy(nxt,x,start,A,shock,B,steps=400,tol=1e-8):
    d=x.shape[-1];L=.2/d+nxt.lipschitz();a=project(start,B);y=a.copy();t=1.
    for it in range(steps):
        z=(x@A.T+y)[:,None,:]+shock[None,:,:]
        g=.2*y/d+nxt.grad(z.reshape(-1,d)).reshape(len(x),4,d).mean(1)
        an=project(y-g/L,B);tn=(1+math.sqrt(1+4*t*t))/2;y=an+(t-1)/tn*(an-a);a=an;t=tn
        if it%20==0 or it==steps-1:
            zz=(x@A.T+a)[:,None,:]+shock[None,:,:]
            gg=.2*a/d+nxt.grad(zz.reshape(-1,d)).reshape(len(x),4,d).mean(1)
            gap=fw_gap(a,gg,B)
            if gap.max()<tol:break
    value=qcost(x)+.1*(a*a).mean(-1)+nxt.value(((x@A.T+a)[:,None,:]+shock).reshape(-1,d)).reshape(len(x),4).mean(1)
    return a,value,gap,it+1


def tree_cost_grad(x0,controls,A,shock,gradient=True):
    batch,d=x0.shape;xs=[x0[:,None,:]];total=np.zeros(batch)
    for u in controls:
        x=xs[-1];total+=(qcost(x)+.1*(u*u).mean(-1)).mean(1)
        y=(x@A.T+u)[:,:,None,:]+shock[None,None,:,:]
        xs.append(y.reshape(batch,-1,d))
    total+=qcost(xs[-1]).mean(1)
    if not gradient:return total
    lam=qgrad(xs[-1])/xs[-1].shape[1];gs=[]
    for n in range(len(controls)-1,-1,-1):
        child=lam.reshape(batch,controls[n].shape[1],4,d).sum(2)
        gs.append(.2*controls[n]/(d*controls[n].shape[1])+child)
        lam=qgrad(xs[n])/xs[n].shape[1]+child@A
    return total,gs[::-1]


def reference(x,A,shock,B,N=3,tol=1e-7,max_iter=5000):
    start=time.perf_counter();d=x.shape[1];controls=[np.zeros((len(x),4**n,d)) for n in range(N)];y=[a.copy() for a in controls];t=1.
    # An explicit Euclidean Hessian bound: ||A||<=1, T=3, min control weight positive.
    L=(.2+2.4*sum((n+1)**2 for n in range(N)))/d
    for it in range(max_iter):
        val,grads=tree_cost_grad(x,y,A,shock)
        new=[project((a-g/L).reshape(-1,d),B).reshape(a.shape) for a,g in zip(y,grads)]
        tn=(1+math.sqrt(1+4*t*t))/2;y=[b+(t-1)/tn*(b-a) for a,b in zip(controls,new)];controls=new;t=tn
        if it%50==0 or it==max_iter-1:
            val,g=tree_cost_grad(x,controls,A,shock);gap=sum(fw_gap(a,gg,B).sum(1) for a,gg in zip(controls,g))
            if gap.max()<tol:break
    return dict(cost=val,gap=gap,iterations=it+1,seconds=time.perf_counter()-start,controls=controls)


class Actor(nn.Module):
    def __init__(self,d,B):
        super().__init__();self.net=nn.Sequential(nn.Linear(d,32),nn.Tanh(),nn.Linear(32,d+1));self.B=B
    def forward(self,x):return self.B*torch.softmax(self.net(x),-1)[...,:-1]


def run(d,seed=101,N=3,out=Path('replication/r4/output')):
    rng=np.random.default_rng(seed);torch.manual_seed(seed);A,shock,B=primitives(d);critics=[None]*(N+1);critics[-1]=Critic(d,rng,True);actors=[None]*N;logs=[]
    x=rng.uniform(-.25,1.65,(1024,d));start=time.perf_counter()
    for n in range(N-1,-1,-1):
        pol,target,gap,it=greedy(critics[n+1],x,np.zeros_like(x),A,shock,B)
        actor=Actor(d,B);xx=torch.tensor(x);yy=torch.tensor(pol)
        loss=fit_lbfgs(actor,lambda:((actor(xx)-yy)**2).mean(),160)
        critic=Critic(d,rng);fit=critic.fit(x,target)
        critics[n]=critic;actors[n]=actor
        logs.append(dict(date=n,critic=fit,actor_distillation_mse=loss,actor_optimizer=fit_lbfgs.last_stats.copy(),actor_candidate_gap_max=float(gap.max()),greedy_iterations=it))
    train=time.perf_counter()-start;test=rng.uniform(0,1.2,(32,d));states=test[:,None,:];cost=np.zeros(len(test));allgaps=[];binding=[];feasibility=[]
    for n in range(N):
        flat=states.reshape(-1,d)
        with torch.no_grad():proposal=actors[n](torch.tensor(flat)).numpy()
        pol,_,gap,it=greedy(critics[n+1],flat,proposal,A,shock,B)
        allgaps.append(float(gap.max()));binding.append(float(np.mean(abs(pol.sum(1)-B)<1e-5)))
        feasibility.append(float(max(np.maximum(-pol,0).max(),np.maximum(pol.sum(1)-B,0).max())))
        u=pol.reshape(states.shape);cost+=(qcost(states)+.1*(u*u).mean(-1)).mean(1)
        states=((states@A.T+u)[:,:,None,:]+shock[None,None,:,:]).reshape(len(test),-1,d)
    cost+=qcost(states).mean(1);neural_end=time.perf_counter()-start
    # Matched deployment ablation: the very same proposal networks, no polishing.
    raw_states=test[:,None,:];raw_cost=np.zeros(len(test))
    for n in range(N):
        with torch.no_grad():uu=actors[n](torch.tensor(raw_states.reshape(-1,d))).numpy().reshape(raw_states.shape)
        raw_cost+=(qcost(raw_states)+.1*(uu*uu).mean(-1)).mean(1)
        raw_states=((raw_states@A.T+uu)[:,:,None,:]+shock[None,None,:,:]).reshape(len(test),-1,d)
    raw_cost+=qcost(raw_states).mean(1)
    matched=reference(test,A,shock,B,N,tol=1e-3)
    ref=reference(test,A,shock,B,N);excess=cost-ref['cost'];upper=excess+ref['gap']
    # With a convex objective, the computed reference is within its FW gap.
    assert excess.min()>-1e-6 and min(upper)>=-1e-6
    payload={}
    for n,c in enumerate(critics[:-1]):
        for key in ['W','b','c','lin','const']:payload[f'critic.{n}.{key}']=np.asarray(getattr(c,key))
        for key,val in actors[n].state_dict().items():payload[f'actor.{n}.{key}']=val.numpy()
    np.savez_compressed(out/f'resource_weights_{d}_{seed}.npz',**payload)
    result=dict(d=d,seed=seed,horizon=N,shock_branches=4,budget=B,initial_distribution='uniform [0,1.2]^d, 32 held-out states',training_distribution='uniform [-.25,1.65]^d, 1024 states',
                architecture='convex squared-ReLU feature critic; 32-tanh proposal actor with slack-softmax; convex improvement safeguard',
                train_seconds=train,neural_end_to_end_seconds=neural_end,reference_seconds=ref['seconds'],reference_iterations=ref['iterations'],
                reference_gap_max=float(ref['gap'].max()),reference_tolerance_passed=bool(ref['gap'].max()<1e-7),
                common_accuracy_target=1e-3,neural_target_passed=bool(upper.max()<1e-3),matched_reference_seconds=matched['seconds'],
                matched_reference_gap_max=float(matched['gap'].max()),matched_reference_target_passed=bool(matched['gap'].max()<1e-3),
                proposal_only_cost_excess_mean=float((raw_cost-ref['cost']).mean()),proposal_only_cost_excess_upper_max=float((raw_cost-ref['cost']+ref['gap']).max()),
                ablation='Same trained proposal actors; improvement safeguard removed only at deployment.',cost_excess_mean=float(excess.mean()),cost_excess_max=float(excess.max()),cost_excess_upper_max=float(upper.max()),
                mean_reference_cost=float(ref['cost'].mean()),binding_frequency_by_date=binding,constraint_violation_max=max(feasibility),actor_surrogate_gap_by_date=allgaps,
                raw=dict(test_states=test.tolist(),neural_cost=cost.tolist(),proposal_only_cost=raw_cost.tolist(),reference_cost=ref['cost'].tolist(),reference_gap=ref['gap'].tolist()),logs=logs,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),evidence_class='constrained_coupled_stochastic_neural_control_with_convex_scenario_tree_reference')
    (out/f'resource_results_{d}_{seed}.json').write_text(json.dumps(result,indent=2)+'\n');print('RESOURCE', {k:v for k,v in result.items() if k not in ['raw','logs']},flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--dimensions',default='4,8,16');ap.add_argument('--seeds',default='101,202,303');ap.add_argument('--out',default='replication/r4/output');a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for d in map(int,a.dimensions.split(',')):
        for seed in map(int,a.seeds.split(',')):run(d,seed,out=out)
