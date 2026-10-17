"""Continuum enclosures, all-action witnesses, and paid strict tail cuts."""
from __future__ import annotations
import numpy as np
from interval94 import I,as_i,stack,expand,up,down
from investment94 import *
from representations94 import Fit

def shock_mesh(n):
    if n<2 or n&(n-1):raise ValueError('Power-of-two innovation cover required')
    edges=np.linspace(-RADIUS,RADIUS,n+1)
    return (edges[:-1]+edges[1:])/2,edges

def query(x,a,alpha,fit:Fit|None,n=128):
    """Enclose original Q and retain one globally valid action minorant.

None is the conventional one-date risk-DP continuation. Its lower affine
supports are independently feasible Lagrangian witnesses, not optimal labels.
"""
    x=as_i(x);a=as_i(a);d=x.lo.shape[-1];b,s=exposures(d);mids,edges=shock_mesh(n)
    y=transition(x,a,I(mids));count('original_transition_points',int(np.prod(y.lo.shape[:-1])))
    if fit is not None:
        values,slopes=fit.interval(y,True)
        # Convexity: interval maxima at bin endpoints bound every innovation.
        ve=fit.interval(transition(x,a,I(edges)))
        upper=I(np.maximum(ve.lo[...,:-1],ve.lo[...,1:]),np.maximum(ve.hi[...,:-1],ve.hi[...,1:]))
        lower_values=values
    else:
        rec=terminal_certificate(y,alpha)
        lower_values=I(rec['lower']);values=I(rec['lower'],rec['upper']);slopes=rec['slope']
        # V1 is convex and 15/d-Lipschitz. The actual terminal policy is
        # pointwise within TERMINAL_TOL, including its stated acquisition pad.
        pad=I(15)*RADIUS/n
        upper=I(rec['upper'])+pad+TERMINAL_TOL
    q=tail_weights(values.mid(),alpha)
    witness=S(x)+action_cost(a)+BETA*weighted_sum(lower_values,q)
    p=action_grad(a)+BETA*weighted_sum((slopes*b).sum(),q)
    lb=quadratic_minimum_lower(I(witness.lo),p,a,capacity(x))
    ur=discrete_avar_interval(upper,alpha).hi
    uq=(S(x)+action_cost(a)+BETA*I(ur)).hi
    count('all_action_lower_witnesses',np.size(lb));count('continuum_bins',np.size(q))
    return dict(lower=lb,upper=uq,gap=up(uq-lb),witness=witness,gradient=p,tail_weights=q,n=n)

def float_query(x,a,alpha,fit,n=128):
    mids,_=shock_mesh(n);d=x.shape[-1];b,s=exposures(d);xn=np.roll(x,-1,axis=-1)
    c=1/16+x/2+xn/8+x*(1-xn)/16+a[...,None]*b
    y=c[...,None,:]+mids[:,None]*s
    if fit is None:
        val,gr=terminal_float_value_slope(y,alpha)
        gd=np.sum(gr*b,axis=-1)
    else:
        val,gr=fit.float_eval(y,True);gd=np.sum(gr*b,axis=-1)
    q=tail_weights(val,alpha)
    return _float_state_public(x)+a*a+4*a**4+BETA*np.sum(q*val,axis=-1),2*a+16*a**3+BETA*np.sum(q*gd,axis=-1)

# Explicit imports keep proposal helpers separate from interval certificate API.
from investment94 import _float_terminal as _terminal_float_public,_float_S as _float_state_public

def actor(x,alpha,fit,n=128,iterations=16):
    x=np.asarray(x);cap=.125+np.mean(x,axis=-1)/8
    lo=np.zeros_like(cap);hi=cap.copy()
    _,p0=float_query(x,lo,alpha,fit,n);_,pc=float_query(x,hi,alpha,fit,n)
    for _ in range(iterations):
        mid=(lo+hi)/2;_,p=float_query(x,mid,alpha,fit,n)
        lo=np.where(p<0,mid,lo);hi=np.where(p>=0,mid,hi)
    a=np.where(p0>=0,0,np.where(pc<=0,cap,(lo+hi)/2))
    return np.minimum(np.floor(a*2**30)/2**30,np.floor(capacity(I(x)).lo*2**30)/2**30)

def certify_actor(x,alpha,fit,tolerance=1/64):
    # The numerical proposal mesh is fixed; certification can refine only its
    # integration enclosure, as prespecified. Failed actors remain failures.
    a=actor(x,alpha,fit)
    attempts=[]
    for n in (128,256,512,1024,2048,4096):
        r=query(I(x),I(a),alpha,fit,n)
        ok=r['gap']<=tolerance
        attempts.append(dict(n=n,maximum_gap=float(np.max(r['gap'])),failed=int(np.sum(~ok))))
        if np.all(ok):return a,r,attempts
    return a,r,attempts

def policy_cost(x,a,alpha,n=128):
    """Nested original-risk cost, not average realized cash cost."""
    x=as_i(x);a=as_i(a);mids,_=shock_mesh(n)
    rec=terminal_certificate(transition(x,a,I(mids)),alpha)
    pad=I(15)*RADIUS/n
    lower=I(rec['lower'])-pad
    upper=I(rec['upper'])+pad+TERMINAL_TOL
    risk=discrete_avar_interval(I(lower.lo,upper.hi),alpha)
    out=S(x)+action_cost(a)+BETA*risk
    count('independent_initial_cost_enclosures',np.size(a.lo));return out.checked()

def uniform_residual(fit,alpha,n=32):
    """Whole-square residual bound from original primitive affine supports.

No probability law is replaced by a state grid. Four-vertex inequalities
qualify every point in every cell; this grid is a certificate cover only.
"""
    if fit.directions.shape[1]!=2:raise ValueError('Primary state-cover implementation is two-dimensional')
    grid=np.linspace(0,1,n+1);x=np.stack(np.meshgrid(grid,grid,indexing='ij'),-1).reshape(-1,2)
    r=terminal_certificate(I(x),alpha);hv,hg=fit.interval(I(x),True)
    l=np.inf;u=-np.inf
    for j in range(n):
        ids=np.array([[j*(n+1)+k,j*(n+1)+k+1,(j+1)*(n+1)+k,(j+1)*(n+1)+k+1] for k in range(n)])
        vertices=x[ids];lower_candidates=[];upper_candidates=[]
        for anchor in range(4):
            ia=ids[:,anchor];delta=I(vertices)-I(x[ia,None,:])
            Lv=I(r['lower'][ia,None])+(expand(r['slope'][ia],1)*delta).sum()
            Lh=I(hv.lo[ia,None])+(expand(hg[ia],1)*delta).sum()
            lower_candidates.append(np.min((Lv-I(hv.hi[ids])).lo,axis=-1))
            upper_candidates.append(np.max((I(r['upper'][ids])-Lh).hi,axis=-1))
        l=min(l,float(np.min(np.maximum.reduce(lower_candidates))))
        u=max(u,float(np.max(np.minimum.reduce(upper_candidates))))
    count('uniform_state_cells',n*n)
    return dict(lower=l,upper=u,span=float(up(u-l)),state_cells=n*n,state_nodes=len(x),cover_method='convex interpolation versus global affine supports; entire square',sampling_rows=0)

def strict_tail_cuts(lower,upper,alpha):
    """Safe whole-bin zero-risk-mass screen. Equality is retained."""
    lower=np.asarray(lower);upper=np.asarray(upper)
    if lower.shape!=upper.shape or np.any(lower>upper) or not np.all(np.isfinite(lower)) or not np.all(np.isfinite(upper)):
        raise ValueError('Invalid unpruned continuum error set')
    n=lower.shape[-1];need=int(np.ceil(n*(1-alpha)))
    # The kth largest lower endpoint is a uniform upper-tail threshold.
    threshold=np.partition(lower,n-need,axis=-1)[...,n-need]
    return upper<threshold[...,None]
