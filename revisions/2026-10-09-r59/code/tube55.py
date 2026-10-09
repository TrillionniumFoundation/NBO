"""Signed derivative tubes for a smooth installed reference, not jumping actors.

This is a separately frozen extension. It never changes the original R55
cache/protocol. If the complete incumbent is not zero, the generic verified
cache is used without assuming that the acquired actor is differentiable.
"""
from __future__ import annotations
from fractions import Fraction as F
import numpy as np
import neural55 as n


def monotone_next(x:n.I,a:n.I,z:n.I)->n.I:
    lo=n.o.deterministic_next(n.I.point(x.lo),n.I.point(a.lo))
    hi=n.o.deterministic_next(n.I.point(x.hi),n.I.point(a.hi))
    deterministic=n.I(lo.lo,hi.hi)
    sign=np.where(np.arange(x.lo.shape[-1])%2==0,1.,-1.)
    noise=n.I(z.lo[:,None],z.hi[:,None])*sign
    return (deterministic+noise).clip(0,1)


def gradient_tube(x:n.I,remaining:int,counter:dict|None=None)->n.I:
    """Uniform interval for grad J^0 with remaining stage costs and terminal g."""
    if remaining<0:raise ValueError('Negative remaining horizon')
    d=x.lo.shape[-1];N=len(x.lo);states=[x]
    zero=n.I.point(np.zeros(N));noise=n.I(np.full(N,-1/32),np.full(N,1/32))
    for t in range(remaining):states.append(monotone_next(states[-1],zero,noise))
    g=n.gradient_cost(states[-1],True)
    for t in reversed(range(remaining)):
        xx=states[t];columns=[]
        for j in range(d):
            prev=(j-1)%d;nxt=(j+1)%d
            columns.append(n.s.col(g,j)*(F(1,2)+(1-n.s.col(xx,nxt))/16)
                +n.s.col(g,prev)*(F(1,8)-n.s.col(xx,prev)/16))
        g=n.gradient_cost(xx)+float(n.BETA)*n.s.stack(columns)
    if counter is not None:
        counter['tube_state_rows']=counter.get('tube_state_rows',0)+N*(remaining+1)
        counter['tube_jacobian_coordinates']=counter.get('tube_jacobian_coordinates',0)+N*d*remaining
    return g


def signed_zero_advantage(x:n.I,a:n.I,remaining:int,q:int,counter=None)->n.I:
    N=len(a.lo);d=x.lo.shape[-1]
    if np.any(a.lo<0):raise ValueError('This specialization covers nonnegative actions')
    segment=n.I(np.zeros(N),a.hi);projection=n.I.point(np.zeros(N))
    gamma=np.where(np.arange(d)%2==0,.5,.25)
    for j in range(q):
        z=n.I(np.full(N,-1/32+j/(16*q)),np.full(N,-1/32+(j+1)/(16*q)))
        y=monotone_next(x,segment,z)
        projection=projection+n.dot(gradient_tube(y,remaining,counter),gamma)
    return a*a*(1+4*a*a)+float(n.BETA)*a*(projection/q)


class TubeCache(n.Cache):
    def __init__(self,critics,part,policy,q=8):
        self.zero_reference=bool(np.all(policy==0));self.tube_work={};self.trace={}
        super().__init__(critics,part,policy,q)
    def advantage(self,t,x,a,b):
        base=super().advantage(t,x,a,b)
        enabled=self.zero_reference and t<self.T-1
        if enabled:
            if np.any(b.lo!=0) or np.any(b.hi!=0):raise AssertionError('Tube reference is not zero')
            tube=signed_zero_advantage(x,a,self.T-t-1,self.q,self.tube_work)
            final=n.I(np.maximum(base.lo,tube.lo),np.minimum(base.hi,tube.hi))
            same=(a.lo==0)&(a.hi==0);final.lo[same]=final.hi[same]=0
            if np.any(final.lo>final.hi):raise AssertionError('Tube and residual-cache intervals disagree')
        else:tube=base;final=base
        self.trace.setdefault(t,[]).append((base,tube,final,enabled))
        return final
    def sweep(self,proposals=None):
        new,report,raw=super().sweep(proposals)
        for t,items in self.trace.items():
            for k,(base,tube,final,enabled) in enumerate(items):
                raw[f't{t}_comparison{k}_base_lo']=base.lo
                raw[f't{t}_comparison{k}_base_hi']=base.hi
                raw[f't{t}_comparison{k}_tube_lo']=tube.lo
                raw[f't{t}_comparison{k}_tube_hi']=tube.hi
            count=10 if proposals is not None else 9
            report[t]['tube_enabled']=items[0][3]
            report[t]['extra_strict_candidate_comparisons']=sum(int(np.count_nonzero((b.hi>=0)&(f.hi<0))) for b,h,f,e in items[:count])
            report[t]['base_candidate_width_max']=max(float(v[0].width().max()) for v in items[:count])
            report[t]['intersected_candidate_width_max']=max(float(v[2].width().max()) for v in items[:count])
        return new,report,raw
