"""Primitive own-future proposal services for the fixed R62 catalogue.
Scalar actions use the retained exact R61 native solver. The two-control
SLSQP proposal is explicitly approximate and never supplies its own proof.
"""
from __future__ import annotations
import itertools,time
from fractions import Fraction as F
import numpy as np
from scipy.optimize import minimize
import core62 as c
import search60 as exact
n=c.n

def point_stage(x,a,terminal=False):
    state=n.primitive_point(x,np.zeros(len(x)),terminal=terminal)
    if terminal:return state
    return state+np.sum(a*a+4*a**4,axis=1)+(a[:,0]*a[:,1]/4 if a.shape[1]==2 else 0)

def expected_two(critic,x,a):
    y=n.next_point(x,a[:,0]);y=y+a[:,1,None]*np.array([.25,.5])
    # This is a fixed fitting/proposal quadrature, never the original-law
    # certification calculation. Its approximation is not called exact.
    vals=np.zeros(len(x))
    for i,j in itertools.product(range(4),repeat=2):
        z=-1/32+(i+.5)/64;w=-1/64+(j+.5)/128
        vals+=critic.point(y+np.array([z,-z])+w)
    return vals/16

def train_two(kind,T,seed):
    rng=np.random.default_rng(seed);critics=[None]*T+[n.Critic.terminal(2)];logs=[]
    for t in reversed(range(T)):
        x=rng.random((512,2));cap=c.cap_points(x);labels=np.full(512,np.inf)
        for frac in c.fractions_menu(2,8):
            a=cap[:,None]*np.array(frac);labels=np.minimum(labels,point_stage(x,a)+.75*expected_two(critics[t+1],x,a))
        start=time.perf_counter();critics[t]=n.fit(kind,x,labels,seed+100+t,width=32,epochs=120)
        logs.append(dict(date=t,training_seed=seed,fitting_seed=seed+100+t,training_states=x.tolist(),training_labels=labels.tolist(),fit_seconds=time.perf_counter()-start,training_mse=float(np.mean((critics[t].point(x)-labels)**2)),label_action_simplex_subdivisions=8,label_shock_midpoints_per_component=4,scope='own-future approximate training labels; not a value certificate'))
    return critics,logs

def make(kind,d,m,T,seed):
    start=time.perf_counter();part=n.Partition(d,32,551)
    if m==1:
        critics,logs=n.train(kind,d,T,512,seed);before=time.perf_counter()
        _,indices,records,work=exact.proposals(critics,part);actions=indices[:,:,None]/4096
        witness=dict(kind='R61 exact rational scalar recovery',records=records,work=work,seconds=time.perf_counter()-before)
    else:
        c.need(d==2,'Two-control cell fixed at d=2');critics,logs=train_two(kind,T,seed)
        before=time.perf_counter();actions=np.empty((T,32,2));records=[]
        for t in range(T):
            for leaf,x in enumerate(part.centers):
                cap=int(part.capindex[leaf])/4096
                def objective(a):return float(point_stage(x[None,:],np.asarray(a)[None,:])[0]+.75*expected_two(critics[t+1],x[None,:],np.asarray(a)[None,:])[0])
                starts=((0.,0.),(cap,0.),(0.,cap),(cap/3,cap/3));candidates=list(starts);runs=[]
                for a0 in starts:
                    fit=minimize(objective,np.array(a0),method='SLSQP',bounds=((0.,cap),(0.,cap)),constraints=[{'type':'ineq','fun':lambda a,cap=cap:cap-float(np.sum(a))}],options={'ftol':1e-12,'maxiter':100})
                    proposal=np.clip(fit.x,0,cap)
                    if proposal.sum()>cap:proposal*=cap/proposal.sum()
                    if np.isfinite(proposal).all():candidates.append(tuple(proposal))
                    runs.append(dict(success=bool(fit.success),status=int(fit.status),message=str(fit.message),iterations=int(fit.nit),function_evaluations=int(fit.nfev)))
                chosen=min(candidates,key=lambda a:(objective(a),a));ix=np.floor(np.array(chosen)*4096).astype(int)
                c.need(ix.sum()<=part.capindex[leaf] and np.all(ix>=0),'Constrained proposal failed exact feasibility')
                actions[t,leaf]=ix/4096;records.append(dict(date=t,leaf=leaf,index=ix.tolist(),objective_approx=objective(ix/4096),solves=runs))
        witness=dict(kind='conventional multistart SLSQP with exact dyadic feasibility repair and separate Bellman certification',records=records,seconds=time.perf_counter()-before)
    record=dict(kind=kind,d=d,m=m,T=T,seed=seed,training=logs,critics=[h.payload() for h in critics],partition=part.payload(),actions=actions.tolist(),witness=witness,seconds=time.perf_counter()-start)
    return dict(partition=part,actions=actions),record
