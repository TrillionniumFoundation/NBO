#!/usr/bin/env python3
"""Reload deposited neural weights; reproduce actions and full scenario-tree costs.
No training or historical code is used. NDU checks interior points at two dates;
resource checks all stored initial states and all stochastic branches.
"""
import argparse,json
from pathlib import Path
import numpy as np
import torch
from solver import Actor,Critic,Model,grid,torch_terminal
from safeguard import select
import coupled_resource as cr


def restore(net,z,prefix):
    state={k:torch.tensor(z[prefix+k]) for k in net.state_dict()}
    net.load_state_dict(state)
    for p in net.parameters():p.requires_grad_(False)
    return net


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='replication/r4/output');a=ap.parse_args();out=Path(a.out);rows=[]
    ss,bd=grid(33,49);ij=np.argwhere(~bd)[::31];states=torch.tensor(ss[ij[:,0],ij[:,1]])
    for seed in [101,202,303]:
        z=np.load(out/f'safe_weights_{seed}.npz');saved=np.load(out/f'safe_policy_{seed}.npz')['policies'];errors=[]
        for n in [0,7]:
            actor=restore(Actor(32),z,f'actor.{n}.')
            nxt=torch_terminal if n==7 else restore(Critic(64,(8-n-1)/8),z,f'critic.{n+1}.')
            pol=select(nxt,states,actor(states),1/8,Model())[0].numpy()
            errors.append(float(abs(pol-saved[n,ij[:,0],ij[:,1]]).max()))
        assert max(errors)<1e-10
        rows.append(dict(kind='ndu_checkpoint',seed=seed,dates=[0,7],points=len(ij),policy_max_difference=max(errors)))
    for d in [4,8,16]:
        for seed in [101,202,303]:
            r=json.loads((out/f'resource_results_{d}_{seed}.json').read_text());z=np.load(out/f'resource_weights_{d}_{seed}.npz')
            A,shock,B=cr.primitives(d);rng=np.random.default_rng(0);critics=[];actors=[]
            for n in range(3):
                critic=cr.Critic(d,rng)
                for key in ['W','b','c','lin','const']:setattr(critic,key,z[f'critic.{n}.{key}'])
                critics.append(critic);actors.append(restore(cr.Actor(d,B),z,f'actor.{n}.'))
            critics.append(cr.Critic(d,rng,True));states=np.asarray(r['raw']['test_states'])[:,None,:];cost=np.zeros(len(states))
            for n in range(3):
                flat=states.reshape(-1,d)
                with torch.no_grad():prop=actors[n](torch.tensor(flat)).numpy()
                u=cr.greedy(critics[n+1],flat,prop,A,shock,B)[0].reshape(states.shape)
                cost+=(cr.qcost(states)+.1*(u*u).mean(-1)).mean(1)
                states=((states@A.T+u)[:,:,None,:]+shock[None,None,:,:]).reshape(len(cost),-1,d)
            cost+=cr.qcost(states).mean(1);err=float(abs(cost-np.asarray(r['raw']['neural_cost'])).max());assert err<1e-10
            rows.append(dict(kind='resource_checkpoint',d=d,seed=seed,initial_states=len(cost),terminal_branches=64,cost_max_difference=err))
    result=dict(execution_status='completed',tests=rows,tolerance=1e-10,scope='Saved-weight replay; not an independent re-estimation of optimality.')
    (out/'replay_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
