"""Certified nonquadratic NBO on a continuous, constrained capital economy.

Learned spline continuations have an exact ReLU representation. Nonlinear
transitions and finite innovations replace Gaussian quadratic integration.
Every elementary operation is outward enclosed; exp/log use Taylor bounds.
Off-knot states and all continuous feasible actions enter the policy bound.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from pathlib import Path
import json,math,time,hashlib,os


def dn(x):
    y=np.nextafter(np.asarray(x,dtype=float),-np.inf)
    if not np.isfinite(y).all():raise ArithmeticError('Nonfinite lower endpoint')
    return y

def up(x):
    y=np.nextafter(np.asarray(x,dtype=float),np.inf)
    if not np.isfinite(y).all():raise ArithmeticError('Nonfinite upper endpoint')
    return y

@dataclass
class I:
    lo: np.ndarray
    hi: np.ndarray
    def __post_init__(self):
        self.lo=np.asarray(self.lo,dtype=float);self.hi=np.asarray(self.hi,dtype=float)
        if np.any(self.lo>self.hi) or not np.isfinite(self.lo).all() or not np.isfinite(self.hi).all():
            raise ArithmeticError('Invalid interval')
    @classmethod
    def point(cls,x):return cls(np.asarray(x,dtype=float),np.asarray(x,dtype=float))
    def __add__(self,o):
        o=o if isinstance(o,I) else I.point(o);return I(dn(self.lo+o.lo),up(self.hi+o.hi))
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,o):return self+(-(o if isinstance(o,I) else I.point(o)))
    def __rsub__(self,o):return I.point(o)+(-self)
    def __mul__(self,o):
        o=o if isinstance(o,I) else I.point(o)
        products=[self.lo*o.lo,self.lo*o.hi,self.hi*o.lo,self.hi*o.hi]
        return I(dn(np.minimum.reduce(products)),up(np.maximum.reduce(products)))
    __rmul__=__mul__
    def __truediv__(self,o):
        o=o if isinstance(o,I) else I.point(o)
        if np.any((o.lo<=0)&(o.hi>=0)):raise ArithmeticError('Division interval contains zero')
        return self*I(dn(1/o.hi),up(1/o.lo))
    def square(self):
        lo=np.where((self.lo<=0)&(self.hi>=0),0,np.minimum(self.lo*self.lo,self.hi*self.hi))
        hi=np.maximum(self.lo*self.lo,self.hi*self.hi)
        return I(np.maximum(0,dn(lo)),up(hi))
    def clip(self,a,b):return I(np.clip(self.lo,a,b),np.clip(self.hi,a,b))
    def width(self):return up(self.hi-self.lo)
    def midpoint(self):return self.lo+(self.hi-self.lo)*.5


def exp_bound(x:I):
    if np.any(x.lo < -16) or np.any(x.hi > 16):raise ArithmeticError('Exponential range exceeded')
    y=x/256
    p=I.point(1)/math.factorial(14)
    for k in range(13,-1,-1):p=p*y+I.point(1)/math.factorial(k)
    # exp(|y|)<2 and |y|<=1/16, including rational coefficient errors.
    err=I.point(2)/math.factorial(15)
    for _ in range(15):err=err/16
    p=p+I(-err.hi,err.hi)
    for _ in range(8):p=p.square()
    return p


def log_series(m:I,terms=24):
    y=(m-1)/(m+1);y2=y.square();term=y;s=I.point(0.)
    for k in range(terms):
        s=s+term/(2*k+1);term=term*y2
    a=np.maximum(np.abs(y.lo),np.abs(y.hi))
    if np.any(a>=.334):raise ArithmeticError('Logarithm reduction failed')
    b=I.point(a);tail=I.point(2)
    for _ in range(2*terms+1):tail=tail*b
    tail=tail/((2*terms+1)*(I.point(1)-b.square()))
    return 2*s+I(-tail.hi,tail.hi)

_LOG2=log_series(I.point(2.),32)

def log_point(x):
    x=np.asarray(x,dtype=float)
    if np.any(x<=0):raise ArithmeticError('Nonpositive logarithm')
    f,e=np.frexp(x);m=2*f;e=e-1
    return log_series(I.point(m))+I.point(e)*_LOG2

def log_bound(x:I):
    return I(log_point(x.lo).lo,log_point(x.hi).hi)


def risk(v:I,theta):
    if theta==0:
        return .25*I(v.lo[...,0],v.hi[...,0])+.5*I(v.lo[...,1],v.hi[...,1])+.25*I(v.lo[...,2],v.hi[...,2])
    z=exp_bound(theta*v)
    q=.25*I(z.lo[...,0],z.hi[...,0])+.5*I(z.lo[...,1],z.hi[...,1])+.25*I(z.lo[...,2],z.hi[...,2])
    return log_bound(q)/theta


def lipschitz(knots,values):
    slopes=(I.point(values[1:])-I.point(values[:-1]))/(I.point(knots[1:])-I.point(knots[:-1]))
    return float(np.max(np.maximum(abs(slopes.lo),abs(slopes.hi))))


def spline(x:I,knots,values,L=None):
    c=np.clip(x.midpoint(),0,1)
    j=np.clip(np.searchsorted(knots,c,side='right')-1,0,len(knots)-2)
    z=(I.point(c)-I.point(knots[j]))/(I.point(knots[j+1])-I.point(knots[j]))
    v=(1-z)*I.point(values[j])+z*I.point(values[j+1])
    if L is None:L=lipschitz(knots,values)
    rad=np.maximum(up(c-x.lo),up(x.hi-c))
    err=I.point(L)*I.point(rad)
    return v+I(-err.hi,err.hi)


def transition(x:I,a:I):
    z=np.array([-.0625,0,.0625])
    base=.8125*x+a+.0625*x*(1-x)
    return (I(base.lo[...,None],base.hi[...,None])+I.point(z)).clip(0.,1.)


def cost(x:I,a:I,price=1.):
    return (x-.6875).square()+price*a.square()+4*a.square().square()+2*(.375-x).clip(0,1).square()


def terminal(x:I):return 2*(x-.6875).square()+2*(.375-x).clip(0,1).square()


def qvalues(x,a,knots,v,theta,price,L):
    xi=I.point(np.asarray(x)[:,None]);ai=I.point(np.asarray(a)[None,:])
    xp=transition(xi,ai)
    return cost(xi,ai,price)+.9375*risk(spline(xp,knots,v,L),theta)


def construct(N=256,A=128,T=6,theta=1.,price=1.,batch=64):
    begin=time.perf_counter()
    knots=np.linspace(0,1,N+1);actions=np.linspace(0,.25,A+1)
    tv=terminal(I.point(knots));v=tv.midpoint()
    terminal_lip=4.25
    terminal_error=float((I.point(terminal_lip)/N/2+I.point(np.max(tv.width()))).hi)
    Vs=[None]*T+[v];As=[None]*T;records=[]
    for t in range(T-1,-1,-1):
        L=lipschitz(knots,v)
        Lx=float((I.point(2.875)+.9375*.875*I.point(L)).hi)
        La=float((.5*I.point(price)+.25+.9375*I.point(L)).hi)
        action_error=float((I.point(La)*.25/A/2).hi)
        lows=[];highs=[];new=[];pol=[];greedy=[];widths=[]
        for j in range(0,N+1,batch):
            x=knots[j:j+batch];q=qvalues(x,actions,knots,v,theta,price,L)
            lower=np.min(q.lo,axis=1);upper=np.min(q.hi,axis=1)
            nodal=lower+(upper-lower)*.5
            idx=np.argmin(q.hi,axis=1);sel=q.hi[np.arange(len(x)),idx]
            lows.extend(dn(nodal-upper));highs.extend(up(nodal-lower+action_error))
            greedy.extend(up(sel-lower));widths.extend(up(upper-lower))
            new.extend(nodal);pol.extend(actions[idx])
        herror=float((I.point(Lx)/N/2).hi)
        lower=float(dn(min(lows)-herror));upper=float(up(max(highs)+herror))
        actor_error=float((I.point(max(greedy))+I.point(Lx)/N+action_error).hi)
        records.append(dict(date=t,continuation_lipschitz=L,bellman_state_lipschitz=Lx,
            action_lipschitz=La,residual_lower=lower,residual_upper=upper,
            residual_oscillation=float(up(upper-lower)),actor_allowance=actor_error,
            action_mesh_allowance=action_error,off_grid_actor_allowance=float((I.point(Lx)/N).hi),
            nodal_rounding_width=max(widths)))
        v=np.array(new);Vs[t]=v;As[t]=np.array(pol)
    records.sort(key=lambda x:x['date'])
    total=I.point(0);discount=I.point(1)
    for r in records:
        total=total+discount*(I.point(r['residual_upper'])-I.point(r['residual_lower'])+r['actor_allowance'])
        discount=discount*.9375
    total=total+discount*(2*I.point(terminal_error))
    lower_shift=I.point(0);disc=I.point(1)
    for r in records:
        lower_shift=lower_shift+disc*r['residual_upper'];disc=disc*.9375
    lower_shift=lower_shift+disc*terminal_error
    return dict(N=N,A=A,T=T,theta=theta,price=price,knots=knots,values=Vs,actors=As,
        records=records,policy_gap_upper=float(total.hi),terminal_error=terminal_error,
        lower_value_shift=float(lower_shift.hi),construction_seconds=time.perf_counter()-begin,
        bellman_transition_evaluations=int(T*(N+1)*(A+1)*3),
        network_hidden_units_per_date=N-1,network_knots_trainable=False,
        arithmetic='outward binary64 intervals; certified Taylor exp/log',
        policy='nearest-knot feasible actor on [0,1]; all controls in [0,1/4] compared',
        representation='learned nodal values; exact ReLU-spline identity; nonquadratic approximation bias charged')


def action(policy,t,x):
    k=policy['knots'];idx=np.searchsorted(k,x)
    idx=np.clip(idx,1,len(k)-1);idx=np.where(np.abs(x-k[idx-1])<=np.abs(x-k[idx]),idx-1,idx)
    return policy['actors'][t][idx]


def own_value(policy,x0,price=None,theta=None):
    """Enclose the complete finite shock tree for the stored nearest-knot rule."""
    price=policy['price'] if price is None else price;theta=policy['theta'] if theta is None else theta
    beta=.9375
    def rec(t,x):
        if t==policy['T']:return terminal(x)
        knots=policy['knots'];cuts=(knots[1:]+knots[:-1])*.5
        il=np.searchsorted(cuts,x.lo,side='left')
        ih=np.searchsorted(cuts,x.hi,side='right')
        values=policy['actors'][t]
        aa=values[il].copy();bb=aa.copy()
        for offset in range(1,int(np.max(ih-il))+1):
            active=il+offset<=ih;candidate=values[np.minimum(il+offset,len(values)-1)]
            aa=np.where(active,np.minimum(aa,candidate),aa)
            bb=np.where(active,np.maximum(bb,candidate),bb)
        a=I(aa,bb)
        xp=transition(x,a)
        future=rec(t+1,xp)
        return cost(x,a,price)+beta*risk(future,theta)
    return rec(0,I.point(np.asarray(x0,dtype=float)))


def network_coefficients(knots,v):
    slopes=np.diff(v)/np.diff(knots)
    return dict(intercept=float(v[0]),linear=float(slopes[0]),
        hidden_biases=(-knots[1:-1]).tolist(),output_weights=np.diff(slopes).tolist(),
        note='Float conversion of the exact mathematical identity; spline path is the certified evaluator. Dense ReLU execution needs its own arithmetic allowance.')


def encode(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)
