"""Original-economy active-region terminal Bellman compiler.

Only an action proposal is evaluated in floating arithmetic. The inherited
outward original-law certificate remains authoritative. The deployed terminal
controller in investment94 is NEVER replaced by this context manager.
"""
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'code'))
import investment94 as econ
import continuum94 as continuum
import quadrature96 as quad
from interval94 import I, as_i, expand, up
OLD_CERTIFICATE = econ.terminal_certificate
OLD_FLOAT_VALUE_SLOPE = econ.terminal_float_value_slope


def coefficients(x: np.ndarray):
    x = np.asarray(x, dtype=float)
    if x.ndim < 1 or not np.all(np.isfinite(x)) or np.any((x < 0) | (x > 1)):
        raise ValueError('Finite states in the original invariant unit cube required')
    d = x.shape[-1]; b, s = econ.exposures(d)
    xn = np.roll(x, -1, axis=-1)
    r = 1/16 + x/2 + xn/8 + x*(1-xn)/16
    c0 = 8/d*np.sum(b*(r-5/8), axis=-1)
    c0 += np.sum((b-np.roll(b,-1))*(r-np.roll(r,-1,axis=-1)),axis=-1)/(2*d)
    return c0, 41/32, 10/d*np.sum(s*r,axis=-1), 5/4, .5-2*np.mean(r,axis=-1), .125+np.mean(x,axis=-1)/8


def derivative_from_coefficients(a, alpha, c0, c1, d0, d1, h0):
    t = 1-alpha
    mean = np.clip(alpha*(d0+d1*a)/(10*t), -alpha/32, alpha/32)
    return 16*a**3 + 2*a + econ.BETA*(c0+c1*a-3*np.maximum(h0-.75*a,0)+d1*mean)


def compiled_proposal(x, alpha):
    """At most four ordered action regions; one cubic inversion per row.

The cubic inversion is a proposal, not an exact transcendental oracle.
The lower-level callers certify the proposed dyadic action independently.
"""
    if alpha not in (.5,.75):
        raise ValueError('The inherited executable freezes alpha at 1/2 and 3/4')
    x = np.asarray(x,dtype=float)
    c0,c1,d0,d1,h0,cap = coefficients(x)
    knots = np.stack((np.zeros_like(cap),cap,np.clip(h0/.75,0,cap),
                      np.clip((-10*econ.RADIUS*(1-alpha)-d0)/d1,0,cap),
                      np.clip((10*econ.RADIUS*(1-alpha)-d0)/d1,0,cap)),axis=-1)
    knots.sort(axis=-1)
    signs = derivative_from_coefficients(knots,alpha,c0[...,None],c1,d0[...,None],d1,h0[...,None])
    idx = np.maximum(1,np.argmax(signs>=0,axis=-1))
    low = np.take_along_axis(knots,(idx-1)[...,None],axis=-1)[...,0]
    high = np.take_along_axis(knots,idx[...,None],axis=-1)[...,0]
    mid = (low+high)/2
    hinge = h0-.75*mid > 0
    raw = d0+d1*mid; threshold=10*econ.RADIUS*(1-alpha)
    central = np.abs(raw) < threshold
    tail_intercept = np.where(central,alpha*d0/(10*(1-alpha)),np.where(raw>=0,alpha/32,-alpha/32))
    p = 2+econ.BETA*(c1+2.25*hinge+d1*d1*alpha/(10*(1-alpha))*central)
    q = econ.BETA*(c0-3*h0*hinge+d1*tail_intercept)
    u = np.sqrt(p/48)
    root = -2*u*np.sinh(np.arcsinh(q/(32*u**3))/3)
    root = np.clip(root,low,high)
    root = np.where(signs[...,0]>=0,0,np.where(signs[...,-1]<=0,cap,root))
    root = np.minimum(cap,np.maximum(0,np.floor(root*2**38)/2**38))
    if not np.all(np.isfinite(root)):
        raise ArithmeticError('Nonfinite cubic proposal')
    econ.count('compiled_terminal_rows',root.size)
    econ.count('compiled_cubic_evaluations',root.size)
    econ.count('compiled_region_derivative_values',5*root.size)
    econ.count('compiled_interior_cubic_rows',int(np.sum((signs[...,0]<0)&(signs[...,-1]>0))))
    return root


def compiled_certificate(x, alpha):
    """Use the unchanged feasible risk witness and strong-convexity account."""
    x=as_i(x).checked();cap=econ.capacity(x)
    a=np.maximum(0,np.floor(np.minimum(compiled_proposal(x.mid(),alpha),cap.lo)*2**38)/2**38)
    true,W,px,pa,cut=econ.terminal_details(x,I(a),alpha)
    lam=np.where(cap.lo-a<2**-36,np.maximum(-pa.mid(),0),0)
    nu=np.where(a==0,np.maximum(pa.mid(),0),0)
    e=pa+lam-nu
    lower=W+I(lam)*(I(a)-cap)-I(nu)*a-e.square()/4
    slope=px-expand(I(lam)/(8*x.lo.shape[-1]),-1)
    gap=up(true.hi-lower.lo)
    if np.any(~np.isfinite(gap)) or np.any(gap>econ.TERMINAL_TOL):
        # Keep and charge the complete failed attempt, then the inherited oracle.
        econ.count('compiled_certificate_fallback_rows',gap.size)
        return OLD_CERTIFICATE(x,alpha)
    return dict(lower=lower.lo,upper=true.hi,action=a,slope=slope,gap=gap,tail=cut)


def compiled_float_value_slope(x,alpha):
    """Compiled optimal-continuation proposal, never certificate authority."""
    x=np.asarray(x);d=x.shape[-1];b,sgn=econ.exposures(d)
    a=compiled_proposal(x,alpha)
    val,pa=econ._float_terminal(x,a,alpha)
    xn=np.roll(x,-1,axis=-1)
    m=1/16+x/2+xn/8+x*(1-xn)/16+a[...,None]*b
    D=10/d*np.sum(m*sgn,axis=-1)
    mz=np.clip(alpha*D/(10*(1-alpha)),-alpha/32,alpha/32)
    def gs(y,term=False):
        return (8 if term else 4)/d*(y-.625)+(2*y-np.roll(y,-1,axis=-1)-np.roll(y,1,axis=-1))/(2*d)-8/d*np.maximum(.5-2*np.mean(y,axis=-1),0)[...,None]
    gm=gs(m,True)+10/d*mz[...,None]*sgn
    px=gs(x)+econ.BETA*(gm*(.5+(1-xn)/16)+np.roll(gm,1,axis=-1)*(.125-np.roll(x,1,axis=-1)/16))
    cap=.125+np.mean(x,axis=-1)/8
    lam=np.where(cap-a<2**-30,np.maximum(-pa,0),0)
    return val,px-lam[...,None]/(8*d)


@contextmanager
def backend(compiled=False):
    """Scope bindings; leave econ.terminal_proposal and terminal policy intact.

Not thread safe: the frozen campaign uses one computational thread and serial
service calls. Every binding is restored on success and on exceptions.
"""
    bindings=[(continuum,'terminal_certificate'),(quad,'terminal_certificate'),
              (continuum,'terminal_float_value_slope')]
    before=[getattr(mod,key) for mod,key in bindings]
    try:
        if compiled:
            continuum.terminal_certificate=compiled_certificate
            quad.terminal_certificate=compiled_certificate
            continuum.terminal_float_value_slope=compiled_float_value_slope
        yield
    finally:
        for (mod,key),value in zip(bindings,before):setattr(mod,key,value)
