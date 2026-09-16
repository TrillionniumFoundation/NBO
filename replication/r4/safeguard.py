#!/usr/bin/env python3
"""Candidate-safeguarded separated NBO; neural actor remains an evaluated proposal.
No reference values or reference policies enter training. Candidate actions improve
against the frozen neural continuation; the independent grid is only an evaluator.
"""
import argparse,json,hashlib,time,resource
from pathlib import Path
import numpy as np
import torch
from torch import nn
from solver import *


def select(nxt,s,proposal,h,m,counts=(5,5,7),chunk=16384):
    """Select the best feasible candidate including the learned actor proposal."""
    with torch.no_grad():
        best=torch_backup(nxt,s,proposal,h,m);pol=proposal.clone()
        # Batched actions: cap memory without changing the deterministic maximand.
        acts=torch.as_tensor(action_mesh(counts))
        ac=max(1,chunk//len(s))
        for aa in acts.split(ac):
            ss=s[:,None,:].expand(-1,len(aa),-1).reshape(-1,2)
            aaa=aa[None,:,:].expand(len(s),-1,-1).reshape(-1,3)
            qq=torch_backup(nxt,ss,aaa,h,m).reshape(len(s),len(aa))
            v,j=qq.max(1);use=v>best
            pol[use]=aa[j[use]];best=torch.maximum(best,v)
        return pol,best


def train(seed,steps=8,width=64,train_size=2048,actor_iters=160,critic_iters=1000,out=None):
    start=time.perf_counter();torch.manual_seed(seed);m=Model();h=1/steps
    rng=np.random.default_rng(seed);s=torch.tensor(rng.uniform(LO,HI,(train_size,2)))
    actors=[None]*steps;critics=[None]*(steps+1);critics[-1]=torch_terminal;logs=[]
    for n in range(steps-1,-1,-1):
        actor=Actor(32);critic=Critic(width,(steps-n)/steps)
        if n+1<steps:
            actor.load_state_dict(actors[n+1].state_dict());critic.load_state_dict(critics[n+1].state_dict())
        nxt=critics[n+1]
        if isinstance(nxt,nn.Module):
            for p in nxt.parameters():p.requires_grad_(False);p.grad=None
        al=fit_lbfgs(actor,lambda:-torch_backup(nxt,s,actor(s),h,m).mean(),actor_iters)
        actor_stats=fit_lbfgs.last_stats.copy()
        assert not isinstance(nxt,nn.Module) or all(p.grad is None for p in nxt.parameters())
        with torch.no_grad():proposal=actor(s);before=torch_backup(nxt,s,proposal,h,m)
        chosen,target=select(nxt,s,proposal,h,m)
        cl=fit_lbfgs(critic,lambda:(critic(s)-target).square().mean(),critic_iters)
        for net in [actor,critic]:
            for p in net.parameters():p.requires_grad_(False);p.grad=None
        actors[n]=actor;critics[n]=critic
        row=dict(date=n,actor_objective=al,critic_mse=cl,actor_optimizer=actor_stats,critic_optimizer=fit_lbfgs.last_stats.copy(),candidate_gain_mean=float((target-before).mean()),candidate_gain_max=float((target-before).max()))
        logs.append(row);print('safe',seed,row,flush=True)
    training_seconds=time.perf_counter()-start
    held,bd=grid(33,49);test=torch.tensor(held.reshape(-1,2));pols=[]
    for n in range(steps):pols.append(select(critics[n+1],test,actors[n](test),h,m)[0].numpy())
    evaluated=solve_grid(33,49,steps=steps,m=m,frozen=lambda n,x:pols[n])
    pred=critics[0](test).numpy().reshape(33,49);diff=pred-evaluated['values'][0]
    gaps=[];residuals=[];aa=action_mesh((7,7,11));sf=test.numpy()
    for n in range(steps):
        qpi=backup(evaluated['values'][n+1],sf,pols[n],h,m)[0];best=qpi.copy()
        for a in np.array_split(aa,math.ceil(len(aa)/32)):
            q=backup(evaluated['values'][n+1],sf[:,None,:],a[None,:,:],h,m)[0];best=np.maximum(best,q.max(1))
        gaps.append(float((best-qpi)[~bd.ravel()].max()))
        nv=terminal(held) if n+1==steps else critics[n+1](test).numpy().reshape(33,49)
        qb=backup(nv,sf,pols[n],h,m)[0]
        residuals.append(float(abs(critics[n](test).numpy()-qb)[~bd.ravel()].max()))
    center=np.array([[2.,1.25]]);points=torch.tensor(center)
    initial_policy=select(critics[1],points,actors[0](points),h,m)[0].numpy()[0]
    payload={}
    for typ,nets in [('actor',actors),('critic',critics[:-1])]:
        for n,net in enumerate(nets):
            for key,val in net.state_dict().items():payload[f'{typ}.{n}.{key}']=val.numpy()
    np.savez_compressed(out/f'safe_weights_{seed}.npz',**payload)
    np.savez_compressed(out/f'safe_policy_{seed}.npz',values=np.array(evaluated['values']),policies=np.array(evaluated['policies']))
    row=dict(seed=seed,evidence_class='neural_training_and_independent_policy_evaluation',steps=steps,width=width,actor_width=32,train_size=train_size,
        actor_iters=actor_iters,critic_iters=critic_iters,candidate_counts=[5,5,7],logs=logs,training_seconds=training_seconds,
        end_to_end_seconds=time.perf_counter()-start,initial_value=float(interpolate(evaluated['values'][0],center)[0]),initial_policy=initial_policy.tolist(),
        initial_effort=float(interpolate(evaluated['efforts'][0],center)[0]),critic_vs_policy_rmse=float(np.sqrt(np.mean(diff**2))),
        critic_vs_policy_max=float(abs(diff).max()),boundary_error=float(abs(diff[bd]).max()),sampled_feasible_gain_max=max(gaps),gain_by_date=gaps,
        heldout_evaluation_residual_max=max(residuals),source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))},
        global_error_certificate=None,global_error_certificate_reason='Held-out grid and finite candidate search do not bound a continuum supremum.',
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (out/f'safe_results_{seed}.json').write_text(json.dumps(row,indent=2)+'\n');print('RESULT',row,flush=True)
    return row

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',default='101,202,303');ap.add_argument('--out',default='replication/r4/output');a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for seed in map(int,a.seeds.split(',')):train(seed,out=out)
