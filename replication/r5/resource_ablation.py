#!/usr/bin/env python3
"""Same-checkpoint actor ablation, convex-quadratic comparator, query workload.
Every accuracy observation uses a full nonanticipative tree and a fresh convex
reference. Timings are local medians, not hardware-independent complexity claims.
"""
from __future__ import annotations
import argparse, json, math, sys, time, hashlib
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'replication/r4'))
import coupled_resource as r4
from solver import fit_lbfgs
OUT=ROOT/'replication/r5/output'

class Quadratic:
    """Full convex quadratic; projected least squares over a PSD Hessian."""
    def __init__(self,d,terminal=False):
        self.d=d;self.terminal=terminal;self.H=np.zeros((d,d));self.lin=np.zeros(d);self.const=0.
    def value(self,x):
        z=x-1
        return r4.qcost(x)+self.const+z@self.lin+np.einsum('bi,ij,bj->b',z,self.H,z)
    def grad(self,x):return r4.qgrad(x)+self.lin+2*(x-1)@self.H
    def lipschitz(self):
        return float(np.linalg.eigvalsh(2/self.d*np.eye(self.d)+.4/self.d**2*np.ones((self.d,self.d))+2*self.H)[-1])
    def fit(self,x,target,max_iter=5000):
        z=x-1;d=self.d
        D=np.c_[np.ones(len(x)),z,np.einsum('bi,bj->bij',z,z).reshape(len(x),-1)]
        y=target-r4.qcost(x);ridge=1e-8
        gram=D.T@D/len(x)+ridge*np.eye(D.shape[1]);rhs=D.T@y/len(x)
        L=float(np.linalg.eigvalsh(gram)[-1]);v=np.zeros(D.shape[1]);w=v.copy();t=1.
        def project(a):
            a=a.copy();H=a[d+1:].reshape(d,d);eig,U=np.linalg.eigh((H+H.T)/2)
            a[d+1:]=((U*np.maximum(eig,0))@U.T).ravel();return a
        for it in range(max_iter):
            new=project(w-(gram@w-rhs)/L);tn=(1+math.sqrt(1+4*t*t))/2
            w=new+(t-1)/tn*(new-v);v=new;t=tn
            if it%50==0:
                pg=float(np.linalg.norm(v-project(v-(gram@v-rhs)/L))*L)
                if pg<1e-8:break
        self.const=float(v[0]);self.lin=v[1:d+1];self.H=v[d+1:].reshape(d,d)
        assert np.linalg.eigvalsh(self.H).min()>-1e-10
        return dict(iterations=it+1,projected_gradient=pg,mse=float(np.mean((self.value(x)-target)**2)),min_eigenvalue=float(np.linalg.eigvalsh(self.H).min()))

def load(d,seed):
    rng=np.random.default_rng(seed);A,shock,B=r4.primitives(d)
    terminal=r4.Critic(d,rng,True);x=rng.uniform(-.25,1.65,(1024,d))
    saved=np.load(ROOT/f'replication/r4/output/resource_weights_{d}_{seed}.npz')
    critics=[None]*3+[terminal];actors=[None]*3
    for n in range(2,-1,-1):
        c=r4.Critic(d,rng)
        for key in ('W','b','c','lin','const'):setattr(c,key,saved[f'critic.{n}.{key}'])
        critics[n]=c;a=r4.Actor(d,B)
        a.load_state_dict({key:torch.tensor(saved[f'actor.{n}.{key}']) for key in a.state_dict()})
        a.eval();actors[n]=a
    test=rng.uniform(0,1.2,(32,d))
    deposited=json.loads((ROOT/f'replication/r4/output/resource_results_{d}_{seed}.json').read_text())
    assert np.max(abs(test-np.array(deposited['raw']['test_states'])))<1e-14
    return critics,actors,x,test,deposited

def evaluate(critics,actors,x,start_mode):
    d=x.shape[1];A,shock,B=r4.primitives(d);states=x[:,None,:];cost=np.zeros(len(x))
    actor_time=0.;solve_time=0.;steps=[];gaps=[];begin=time.perf_counter()
    for n in range(3):
        flat=states.reshape(-1,d);tm=time.perf_counter()
        if start_mode=='actor':
            with torch.no_grad():start=actors[n](torch.tensor(flat)).numpy()
        else:start=np.zeros_like(flat)
        actor_time+=time.perf_counter()-tm;tm=time.perf_counter()
        a,_,gap,it=r4.greedy(critics[n+1],flat,start,A,shock,B)
        solve_time+=time.perf_counter()-tm;steps.append(it);gaps.append(float(gap.max()))
        u=a.reshape(states.shape);cost+=(r4.qcost(states)+.1*np.mean(u*u,axis=-1)).mean(1)
        states=((states@A.T+u)[:,:,None,:]+shock[None,None,:,:]).reshape(len(x),-1,d)
    cost+=r4.qcost(states).mean(1)
    return dict(cost=cost,seconds=time.perf_counter()-begin,initialization_seconds=actor_time,
                optimizer_seconds=solve_time,iterations=steps,surrogate_gap_max=max(gaps))

def timed_evaluate(critics,actors,x,mode,repeats=3):
    runs=[evaluate(critics,actors,x,mode) for _ in range(repeats)]
    for key in ('seconds','initialization_seconds','optimizer_seconds'):
        runs[0][key]=float(np.median([r[key] for r in runs]))
    return runs[0]

def actor_training(critics,x,d,seed):
    torch.manual_seed(seed);A,shock,B=r4.primitives(d);logs=[];total=0.
    for n in range(2,-1,-1):
        # The target construction is common to actor-free and actor policies.
        labels,_,_,_=r4.greedy(critics[n+1],x,np.zeros_like(x),A,shock,B)
        a=r4.Actor(d,B);xx=torch.tensor(x);yy=torch.tensor(labels);tm=time.perf_counter()
        loss=fit_lbfgs(a,lambda:((a(xx)-yy)**2).mean(),160);elapsed=time.perf_counter()-tm
        total+=elapsed;logs.append(dict(date=n,seconds=elapsed,mse=loss,optimizer=fit_lbfgs.last_stats.copy()))
    return dict(seconds=total,logs=logs)

def train_critics(d,seed,representation):
    rng=np.random.default_rng(seed);A,shock,B=r4.primitives(d)
    term=r4.Critic(d,rng,True);x=rng.uniform(-.25,1.65,(1024,d))
    critics=[None]*3+[term];logs=[];tm=time.perf_counter()
    for n in range(2,-1,-1):
        _,target,gap,it=r4.greedy(critics[n+1],x,np.zeros_like(x),A,shock,B)
        c=r4.Critic(d,rng) if representation=='relu' else Quadratic(d)
        fit=c.fit(x,target);critics[n]=c;logs.append(dict(date=n,fit=fit,greedy_iterations=it,gap=float(gap.max())))
    return critics,dict(seconds=time.perf_counter()-tm,logs=logs)

def run_case(d,seed):
    print('CASE',d,seed,flush=True)
    critics,actors,x,test,original=load(d,seed);A,shock,B=r4.primitives(d)
    # Exact same immutable checkpoints in both deployment arms.
    actor=timed_evaluate(critics,actors,test,'actor');zero=timed_evaluate(critics,actors,test,'zero')
    ref=r4.reference(test,A,shock,B,tol=1e-7)
    assert ref['gap'].max()<1e-7
    for rr in (actor,zero):
        rr['loss_upper_max']=float(np.max(rr['cost']-ref['cost']+ref['gap']))
        rr['loss_mean']=float(np.mean(rr['cost']-ref['cost']))
        rr['target_pass']=rr['loss_upper_max']<1e-3
    assert np.max(abs(actor['cost']-np.array(original['raw']['neural_cost'])))<2e-8
    ad=actor_training(critics,x,d,seed)
    relu,training=train_critics(d,seed,'relu')
    replay=0.
    for n in range(3):
        replay=max(replay,float(np.max(abs(relu[n].value(test)-critics[n].value(test)))))
    training['independent_retraining_value_error']=replay
    assert replay<1e-9, 'critic-only timing must correspond to the deployed continuation' 
    quadratic,qtrain=train_critics(d,seed,'quadratic')
    quad=timed_evaluate(quadratic,None,test,'zero')
    quad['loss_upper_max']=float(np.max(quad['cost']-ref['cost']+ref['gap']))
    quad['target_pass']=quad['loss_upper_max']<1e-3
    saving=zero['seconds']-actor['seconds']
    threshold=(math.ceil(ad['seconds']/saving)*32 if saving>0 else None)
    row=dict(d=d,seed=seed,queries=32,actor=actor,zero=zero,quadratic=quad,
        actor_cost_difference_max=float(np.max(abs(actor['cost']-zero['cost']))),
        isolated_actor_training=ad,critic_only_training=training,quadratic_training=qtrain,
        actor_break_even_queries_linear_batch_projection=threshold,
        reference_gap=float(ref['gap'].max()),reference_cost=ref['cost'].tolist(),
        original_actor_check_max_error=float(np.max(abs(actor['cost']-np.array(original['raw']['neural_cost'])))))
    for obj in (row['actor'],row['zero'],row['quadratic']):obj['cost']=obj['cost'].tolist()
    (OUT/f'resource_{d}_{seed}.json').write_text(json.dumps(row,indent=2)+'\n')
    print('DONE',d,seed,'zero',zero['loss_upper_max'],'quadratic',quad['loss_upper_max'],flush=True)
    return row

def workloads():
    d=4;seed=101;critics,actors,_,_,_=load(d,seed);A,shock,B=r4.primitives(d)
    rng=np.random.default_rng(541021);points=rng.uniform(0,1.2,(2048,d));rows=[]
    trained=json.loads((OUT/'resource_4_101.json').read_text())['critic_only_training']['seconds']
    for count in (32,128,512,2048):
        x=points[:count];zero=timed_evaluate(critics,None,x,'zero',3)
        ref=r4.reference(x,A,shock,B,tol=1e-7)
        matched_runs=[r4.reference(x,A,shock,B,tol=1e-3) for _ in range(3)]
        matched=matched_runs[0];seconds=float(np.median([r['seconds'] for r in matched_runs]))
        upper=zero['cost']-ref['cost']+ref['gap']
        r=dict(d=d,seed=seed,queries=count,held_out_seed=541021,complete_terminal_paths_per_query=64,
            loss_upper_max=float(upper.max()),loss_upper_mean=float(upper.mean()),target_pass=bool(upper.max()<1e-3),
            policy_query_seconds=zero['seconds'],critic_training_seconds=trained,
            total_neural_seconds=trained+zero['seconds'],matched_reference_seconds=seconds,
            reference_matched_gap_max=float(matched['gap'].max()),validation_reference_gap_max=float(ref['gap'].max()),
            reuse_only_speed_ratio=seconds/zero['seconds'],end_to_end_speed_ratio=seconds/(trained+zero['seconds']),
            raw=dict(initial_states=x.tolist(),policy_cost=zero['cost'].tolist(),reference_cost=ref['cost'].tolist(),reference_gap=ref['gap'].tolist()))
        rows.append(r);print('WORKLOAD',count,r['loss_upper_max'],r['end_to_end_speed_ratio'],flush=True)
    (OUT/'resource_workloads.json').write_text(json.dumps(rows,indent=2)+'\n')
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workload-only',action='store_true');args=ap.parse_args()
    if args.workload_only:
        work=workloads();summary=json.loads((OUT/'resource_ablation.json').read_text());summary['workloads']=work;summary['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();(OUT/'resource_ablation.json').write_text(json.dumps(summary,indent=2)+'\n');return
    OUT.mkdir(parents=True,exist_ok=True);rows=[]
    for d in (4,8,16):
        for seed in (101,202,303):rows.append(run_case(d,seed))
    work=workloads();summary=dict(cases=rows,workloads=work,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          timing='Median of three serial complete-tree policy evaluations; single CPU thread. Actor training measured separately; offline targets and critic training not charged twice.',
          interpretation='The actor affects initialization, not asymptotic surrogate accuracy. Convex quadratic is globally projected least squares, not a grid straw-man.')
    (OUT/'resource_ablation.json').write_text(json.dumps(summary,indent=2)+'\n')
if __name__=='__main__':main()
