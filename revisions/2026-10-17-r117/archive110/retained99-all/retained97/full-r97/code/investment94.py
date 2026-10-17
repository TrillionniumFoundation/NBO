"""Original continuous investment primitives and nested-AVaR certificates.

The terminal risk integral is enclosed analytically. Optimizers propose
feasible dyadic actions; interval-supported lower witnesses certify the
whole original action interval. The original shock has NOT become discrete.
"""
from __future__ import annotations
import numpy as np
from interval94 import I,as_i,stack,roll,expand,down,up
BETA=15/16
RADIUS=1/32
TERMINAL_TOL=2**-20
COUNTS={}
def count(key,n=1): COUNTS[key]=COUNTS.get(key,0)+int(n)
def exposures(d):
    if d<2 or d%2: raise ValueError('An even dimension at least two is required')
    return np.where(np.arange(d)%2==0,.5,.25),np.where(np.arange(d)%2==0,1.,-1.)
def capacity(x):
    x=as_i(x);return I(1/8)+x.sum()/ (8*x.lo.shape[-1])
def S(x,terminal=False):
    x=as_i(x);d=x.lo.shape[-1]
    return (x-5/8).square().sum()*(4 if terminal else 2)/d+(x-roll(x,-1)).square().sum()/(4*d)+(I(.5)-x.sum()*2/d).positive().square()*2

def gradS(x,terminal=False):
    x=as_i(x);d=x.lo.shape[-1]
    return (x-5/8)*(8 if terminal else 4)/d+(x*2-roll(x,-1)-roll(x,1))/(2*d)-expand((I(.5)-x.sum()*2/d).positive()*8/d,-1)

def action_cost(a):
    a=as_i(a);return a.square()+a.square().square()*4

def action_grad(a):
    a=as_i(a);return a*2+a.square()*a*16

def center(x,a):
    x=as_i(x);a=as_i(a);b,_=exposures(x.lo.shape[-1]);xn=roll(x,-1)
    return I(1/16)+x/2+xn/8+x*(1-xn)/16+expand(a,-1)*b

def transition(x,a,z):
    m=center(x,a);_,s=exposures(m.lo.shape[-1]);z=as_i(z)
    return expand(m,-2)+expand(z,-1)*s

def tail_moments(s,alpha):
    s=as_i(s);L=alpha/16;tail=(1-alpha)/16
    ez=-(s*2+L)*L/(2*tail)
    ez2=(I(2*RADIUS**3)-L*(s.square()*3+s*(3*L)+L*L))/(3*tail)
    return ez,ez2

def terminal_details(x,a,alpha):
    if alpha not in (.5,.75):raise ValueError('Frozen risk levels only')
    x=as_i(x);a=as_i(a);d=x.lo.shape[-1];b,sgn=exposures(d)
    m=center(x,a);C=S(m,True);D=(m*sgn).sum()*10/d
    slo=-D/10-alpha/32
    sexact=slo.clamp(-RADIUS,RADIUS-alpha/16)
    ez,ez2=tail_moments(sexact,alpha)
    risk=C+D*ez+ez2*5
    # A dyadic, exactly feasible tail set supplies a lower risk witness.
    sp=np.clip(np.rint(sexact.mid()*2**40)/2**40,-RADIUS,RADIUS-alpha/16)
    mz,mz2=tail_moments(I(sp),alpha)
    W=S(x)+action_cost(a)+BETA*(C+D*mz+5*mz2)
    gm=gradS(m,True)+expand(mz,-1)*sgn*10/d
    pa=action_grad(a)+(gm*b).sum()*BETA
    # Derivative of F_j w.r.t. x_j and of F_{j-1} w.r.t. x_j.
    px=gradS(x)+BETA*(gm*(I(.5)+(1-roll(x,-1))/16)+roll(gm,1)*(I(1/8)-roll(x,1)/16))
    count('terminal_original_risk_queries',np.size(a.lo))
    return S(x)+action_cost(a)+BETA*risk,W,px,pa,sp

def _float_S(x,terminal=False):
    d=x.shape[-1]
    return ((4 if terminal else 2)/d*np.sum((x-.625)**2,axis=-1)+np.sum((x-np.roll(x,-1,axis=-1))**2,axis=-1)/(4*d)+2*np.maximum(.5-2*np.mean(x,axis=-1),0)**2)

def _float_terminal(x,a,alpha):
    d=x.shape[-1];b,s=exposures(d);xn=np.roll(x,-1,axis=-1)
    m=1/16+x/2+xn/8+x*(1-xn)/16+a[...,None]*b
    D=10/d*np.sum(m*s,axis=-1);L=alpha/16;tail=(1-alpha)/16
    cut=np.clip(-D/10-L/2,-RADIUS,RADIUS-L)
    mz=-L*(2*cut+L)/(2*tail)
    mz2=(2*RADIUS**3-L*(3*cut**2+3*cut*L+L*L))/(3*tail)
    gm=8/d*(m-.625)+(2*m-np.roll(m,-1,axis=-1)-np.roll(m,1,axis=-1))/(2*d)-8/d*np.maximum(.5-2*np.mean(m,axis=-1),0)[...,None]
    pa=2*a+16*a**3+BETA*np.sum((gm+10/d*mz[...,None]*s)*b,axis=-1)
    val=_float_S(x)+a*a+4*a**4+BETA*(_float_S(m,True)+D*mz+5*mz2)
    count('terminal_proposal_queries',np.size(a))
    return val,pa

def terminal_proposal(x,alpha,iterations=24):
    x=np.asarray(x);cap=.125+np.mean(x,axis=-1)/8
    zero=np.zeros_like(cap);_,p0=_float_terminal(x,zero,alpha);_,pc=_float_terminal(x,cap,alpha)
    lo=zero.copy();hi=cap.copy()
    for _ in range(iterations):
        a=(lo+hi)/2;_,p=_float_terminal(x,a,alpha)
        lo=np.where(p<0,a,lo);hi=np.where(p>=0,a,hi)
    a=np.where(p0>=0,0,np.where(pc<=0,cap,(lo+hi)/2))
    return np.floor(a*2**38)/2**38

def terminal_certificate(x,alpha):
    """A global affine minorant of V1, a feasible upper value and action.

Its state slope is an interval containing one valid global affine slope.
The action multiplier residual is paid using action strong convexity 2.
"""
    x=as_i(x).checked();cap=capacity(x);a=np.minimum(terminal_proposal(x.mid(),alpha),cap.lo)
    a=np.maximum(0,np.floor(a*2**38)/2**38)
    true,W,px,pa,cut=terminal_details(x,I(a),alpha)
    at_upper=(cap.lo-a<2**-36);at_lower=(a==0)
    lam=np.where(at_upper,np.maximum(-pa.mid(),0),0)
    nu=np.where(at_lower,np.maximum(pa.mid(),0),0)
    e=pa+lam-nu
    lower=W+I(lam)*(I(a)-cap)-I(nu)*a-e.square()/4
    slope=px-expand(I(lam)/(8*x.lo.shape[-1]),-1)
    gap=up(true.hi-lower.lo)
    if np.any(gap>TERMINAL_TOL):
        raise ArithmeticError('Terminal certificate failed; maximum gap '+str(float(np.max(gap))))
    return dict(lower=lower.lo,upper=true.hi,action=a,slope=slope,gap=gap,tail=cut)

def quadratic_minimum_lower(intercept,gradient,a,cap):
    """inf of b+g*(u-a)+(u-a)^2 on [0,cap], with outward inputs."""
    intercept=as_i(intercept);gradient=as_i(gradient);a=as_i(a);cap=as_i(cap)
    bounds=[]
    left=I(-a.hi);right=I(up(cap.hi-a.lo))
    for g in (gradient.lo,gradient.hi):
        optimum=-I(g)/2
        distance=np.maximum.reduce([np.zeros_like(optimum.lo),(left-optimum).lo,(optimum-right).lo])
        # Complete the square, with every operation outward. The domain is
        # enlarged first, so interval clipping cannot create a false lower bound.
        val=intercept-I(g).square()/4+I(distance).square()
        bounds.append(val.lo)
    # The exact minimum is concave in g: endpoint slopes cover the interval.
    return np.minimum.reduce(bounds)

def weighted_sum(x,q):
    return (as_i(x)*I(q)).sum()

def tail_weights(v,alpha):
    v=np.asarray(v);n=v.shape[-1];k=int(n*(1-alpha))
    if k<1 or k!=n*(1-alpha):raise ValueError('Dyadic whole-bin tail required')
    order=np.argsort(v,axis=-1,kind='stable');q=np.zeros_like(v)
    np.put_along_axis(q,order[...,-k:],1/k,axis=-1)
    count('risk_sort_calls',int(np.prod(v.shape[:-1])));count('risk_sort_items',v.size)
    return q

def discrete_avar_interval(v,alpha):
    v=as_i(v);ql=tail_weights(v.lo,alpha);qu=tail_weights(v.hi,alpha)
    return I(weighted_sum(I(v.lo),ql).lo,weighted_sum(I(v.hi),qu).hi)


def terminal_float_value_slope(x,alpha):
    """Conventional optimizer/envelope proposal only; never a certificate."""
    x=np.asarray(x);d=x.shape[-1];b,sgn=exposures(d)
    a=terminal_proposal(x,alpha,iterations=18)
    val,pa=_float_terminal(x,a,alpha)
    m=1/16+x/2+np.roll(x,-1,axis=-1)/8+x*(1-np.roll(x,-1,axis=-1))/16+a[...,None]*b
    D=10/d*np.sum(m*sgn,axis=-1);L=alpha/16;tail=(1-alpha)/16
    cut=np.clip(-D/10-L/2,-RADIUS,RADIUS-L);mz=-L*(2*cut+L)/(2*tail)
    def gs(y,term=False):
        return (8 if term else 4)/d*(y-.625)+(2*y-np.roll(y,-1,axis=-1)-np.roll(y,1,axis=-1))/(2*d)-8/d*np.maximum(.5-2*np.mean(y,axis=-1),0)[...,None]
    gm=gs(m,True)+10/d*mz[...,None]*sgn
    px=gs(x)+BETA*(gm*(.5+(1-np.roll(x,-1,axis=-1))/16)+np.roll(gm,1,axis=-1)*(.125-np.roll(x,1,axis=-1)/16))
    cap=.125+np.mean(x,axis=-1)/8
    lam=np.where(cap-a<2**-30,np.maximum(-pa,0),0)
    return val,px-lam[...,None]/(8*d)
