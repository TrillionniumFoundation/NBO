"""Train all hidden affine weights of a nonquadratic ReLU continuation.

The certified spline construction supplies deterministic Bellman training data
and the independent verification bracket. Its complete cost is charged to this
neural service. No SGD convergence or neural work advantage is assumed.
"""
from __future__ import annotations
import os
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np
import time
from nonlinear import I, construct, qvalues, lipschitz, up, own_value


def fit_values(knots,values,width=31,steps=300,seed=17):
    import torch
    torch.set_num_threads(1);torch.manual_seed(seed)
    dtype=torch.float64
    small=np.linspace(0,1,width+2);v=np.interp(small,knots,values)
    slopes=np.diff(v)/np.diff(small)
    pars=[torch.nn.Parameter(torch.ones(width,dtype=dtype)),
          torch.nn.Parameter(torch.tensor(-small[1:-1],dtype=dtype)),
          torch.nn.Parameter(torch.tensor(np.diff(slopes),dtype=dtype)),
          torch.nn.Parameter(torch.tensor(slopes[0],dtype=dtype)),
          torch.nn.Parameter(torch.tensor(v[0],dtype=dtype))]
    init=[p.detach().clone() for p in pars]
    x=torch.tensor(knots,dtype=dtype);y=torch.tensor(values,dtype=dtype)
    optimizer=torch.optim.Adam(pars,lr=0.0002)
    for _ in range(steps):
        optimizer.zero_grad()
        w,b,c,l,a=pars
        prediction=a+l*x+(torch.relu(x[:,None]*w+b)*c).sum(dim=1)
        loss=((prediction-y)**2).mean();loss.backward();optimizer.step()
    out=dict(zip(('w','b','c','linear','intercept'),[p.detach().numpy().copy() for p in pars]))
    out.update(width=width,optimizer_steps=steps,seed=seed,
        hidden_weight_max_change=float(max((pars[i]-init[i]).abs().max().item() for i in (0,1))),
        training_loss=float(loss.detach()))
    return out


def evaluate(net,x):
    x=np.asarray(x,dtype=float)
    return net['intercept']+net['linear']*x+(np.maximum(x[...,None]*net['w']+net['b'],0)*net['c']).sum(axis=-1)


def enclosed(net,x):
    out=I.point(net['intercept'])+I.point(net['linear'])*I.point(x)
    for w,b,c in zip(net['w'],net['b'],net['c']):
        z=I.point(w)*I.point(x)+b
        z=I(np.maximum(0,z.lo),np.maximum(0,z.hi))
        out=out+c*z
    return out


def uniform_difference(net,knots,values):
    diff=enclosed(net,knots)-I.point(values)
    node=float(np.max(np.maximum(abs(diff.lo),abs(diff.hi))))
    nl=I.point(abs(float(net['linear'])))
    for w,c in zip(net['w'],net['c']):nl=nl+I.point(abs(float(w)))*abs(float(c))
    bound=(I.point(node)+(nl+lipschitz(knots,values))/(len(knots)-1)/2).hi
    return dict(uniform_error_upper=float(bound),network_lipschitz_upper=float(nl.hi),
                nodal_error_upper=node,off_grid_enclosed=True)


def neural_service(N=256,A=128,T=4,theta=1.,price=1.,width=31,steps=300):
    start=time.perf_counter();base=construct(N,A,T,theta,price)
    knots=base['knots'];actions=np.linspace(0,.25,A+1)
    nets=[fit_values(knots,v,width,steps,17+t) for t,v in enumerate(base['values'])]
    errors=[uniform_difference(n,knots,v) for n,v in zip(nets,base['values'])]
    records=[];actors=[]
    for t in range(T):
        L=lipschitz(knots,base['values'][t+1]);nodal=[];pol=[]
        for i in range(0,N+1,64):
            x=knots[i:i+64,None];a=actions[None,:]
            xp=np.clip(.8125*x[...,None]+a[...,None]+.0625*x[...,None]*(1-x[...,None])+np.array([-.0625,0,.0625]),0,1)
            vf=evaluate(nets[t+1],xp)
            if theta==0:ce=(vf*np.array([.25,.5,.25])).sum(axis=-1)
            else:ce=np.log((np.exp(theta*vf)*np.array([.25,.5,.25])).sum(axis=-1))/theta
            stage=(x-.6875)**2+price*a*a+4*a**4+2*np.maximum(.375-x,0)**2
            idx=np.argmin(stage+.9375*ce,axis=1)
            # Floating selection is only a proposal. The actual selected action
            # is certified against an independent interval Bellman bracket.
            q=qvalues(x[:,0],actions,knots,base['values'][t+1],theta,price,L)
            nodal.extend(up(q.hi[np.arange(len(idx)),idx]-np.min(q.lo,axis=1)))
            pol.extend(actions[idx])
        record=base['records'][t].copy()
        record['actor_allowance']=float((I.point(max(nodal))+I.point(record['bellman_state_lipschitz'])/N+record['action_mesh_allowance']).hi)
        records.append(record);actors.append(np.array(pol))
    total=I.point(0);disc=I.point(1)
    for rec in records:
        total=total+disc*(I.point(rec['residual_upper'])-rec['residual_lower']+rec['actor_allowance']);disc=disc*.9375
    total=total+disc*2*base['terminal_error']
    candidate={**base,'actors':actors,'records':records,'policy_gap_upper':float(total.hi)}
    vals=own_value(candidate,[.125,.25,.5,.75])
    return dict(candidate=candidate,networks=nets,uniform_network_checks=errors,
        own_policy_values=dict(states=[.125,.25,.5,.75],lower=vals.lo,upper=vals.hi),
        full_service_seconds=time.perf_counter()-start,
        spline_baseline_seconds=base['construction_seconds'],
        spline_baseline_policy_bound=base['policy_gap_upper'],
        hidden_training_verified=all(n['hidden_weight_max_change']>0 for n in nets),
        training_data='Deterministic certified Bellman nodal values, not iid observations',
        cost_boundary='Reference construction, all training, interval verification and own-policy evaluation included',
        certificate='Independent residual bracket plus actual neural-selected actor allowances; no assumed training convergence')
