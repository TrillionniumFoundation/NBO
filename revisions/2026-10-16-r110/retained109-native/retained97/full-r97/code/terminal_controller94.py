"""Explicit acquired terminal policy, with an independent exact fallback path."""
from __future__ import annotations
import numpy as np
from interval94 import I
from investment94 import count,exposures,terminal_certificate


def rational_terminal_action(observed,alpha):
    """Exact fallback for a 40-bit acquired state; no independent-audit import.

The implementation uses the production analytical tail formula in Fraction
arithmetic. The independent checker instead reconstructs and integrates the
primitive polynomial. Every returned action pays its exact all-action gap.
"""
    from fractions import Fraction as Q
    y=[Q(float(v)) for v in observed];d=len(y);al=Q(float(alpha));R=Q(1,32)
    cap=Q(1,8)+sum(y)/Q(8*d);B=[Q(1,2) if j%2==0 else Q(1,4) for j in range(d)];s=[1 if j%2==0 else -1 for j in range(d)]
    def state_cost(z,terminal=False):
        return Q(4 if terminal else 2,d)*sum((v-Q(5,8))**2 for v in z)+sum((z[j]-z[(j+1)%d])**2 for j in range(d))/Q(4*d)+2*max(Q(0),Q(1,2)-2*sum(z)/d)**2
    def value_slope(a):
        m=[Q(1,16)+y[j]/2+y[(j+1)%d]/8+y[j]*(1-y[(j+1)%d])/16+B[j]*a for j in range(d)]
        D=Q(10,d)*sum(m[j]*s[j] for j in range(d));L=2*R*al;tail=2*R*(1-al)
        u=max(-R,min(R-L,-D/10-L/2));ez=-L*(2*u+L)/(2*tail);ez2=(2*R**3-L*(3*u*u+3*u*L+L*L))/(3*tail)
        value=state_cost(y)+a*a+4*a**4+Q(15,16)*(state_cost(m,True)+D*ez+5*ez2)
        gm=[Q(8,d)*(m[j]-Q(5,8))+(2*m[j]-m[(j-1)%d]-m[(j+1)%d])/Q(2*d)-Q(8,d)*max(Q(0),Q(1,2)-2*sum(m)/d)+Q(10,d)*ez*s[j] for j in range(d)]
        derivative=2*a+16*a**3+Q(15,16)*sum(gm[j]*B[j] for j in range(d))
        return value,derivative
    lo=Q(0);hi=cap;_,gl=value_slope(lo);_,gh=value_slope(hi)
    for step in range(128):
        proposed=lo if gl>=0 else hi if gh<=0 else (lo+hi)/2
        a=Q((proposed*2**38).numerator//(proposed*2**38).denominator,2**38)
        val,g=value_slope(a);delta=max(-a,min(cap-a,-g/2));gap=-(g*delta+delta*delta)
        count('terminal_rational_fallback_steps')
        if gap<=Q(1,2**21):return float(a)
        mid=(lo+hi)/2;_,gm=value_slope(mid)
        if gm<0:lo=mid
        else:hi=mid
    raise ArithmeticError('Exact terminal fallback failed its all-action gap')


def terminal_policy(observed,alpha):
    """Complete terminal controller for states acquired downward at 40 bits.

The caller supplies the exact dyadic observation y<=x, ||x-y||_1<=d*2^-40.
The verified gap at y is at most 2^-21. Original-state transfer costs less
than 30*2^-40, hence the full controller is uniformly within 2^-20 of V1.
"""
    y=np.asarray(observed,dtype=float);d=y.shape[-1];exposures(d)
    if not np.all(np.isfinite(y)) or np.any(y<0) or np.any(y>1) or np.any(y*2**40!=np.floor(y*2**40)):
        raise ValueError('The terminal policy requires a finite 40-bit downward observation on the cube')
    count('terminal_policy_observation_rows',int(np.prod(y.shape[:-1])))
    try:
        rec=terminal_certificate(I(y),alpha);actions=np.asarray(rec['action']).copy();bad=np.asarray(rec['gap'])>2**-21
    except ArithmeticError:
        actions=np.zeros(y.shape[:-1]);bad=np.ones(y.shape[:-1],dtype=bool)
    flat=actions.reshape(-1);points=y.reshape(-1,d)
    for j in np.flatnonzero(bad.reshape(-1)):
        count('terminal_rational_fallback_rows');flat[j]=rational_terminal_action(points[j],alpha)
    return actions
