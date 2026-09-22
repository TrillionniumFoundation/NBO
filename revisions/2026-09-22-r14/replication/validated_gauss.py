"""Gauss--Legendre rules with rationally isolated roots and interval weights.

NumPy proposes root locations only. Exact rational sign changes in n disjoint
brackets prove that every root of the degree-n polynomial is represented once.
Cauchy remainders, not convergence between two meshes, validate quadrature.
"""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
import math
import numpy as np
from interval64 import I, add_reduce, exp, stack
Q=I.rational

def sqrt(a):
    a=a if isinstance(a,I) else I(a)
    if np.any(a.lo<0):raise ArithmeticError('sqrt domain')
    def endpoint(x,upper):
        shape=np.asarray(x).shape;out=[]
        for xx in np.asarray(x).reshape(-1):
            xx=float(xx)
            if xx==0:out.append(0.);continue
            f=math.sqrt(xx);target=F(xx)
            for _ in range(16):
                diff=F(f)**2-target
                if (diff>=0 if upper else diff<=0):break
                f=math.nextafter(f,math.inf if upper else -math.inf)
            else:raise ArithmeticError('Unverified sqrt proposal')
            out.append(f)
        return np.asarray(out).reshape(shape)
    return I(endpoint(a.lo,False),endpoint(a.hi,True))

@lru_cache(None)
def pi():
    def atan(q):
        s=sum(((-1)**j*q**(2*j+1)/F(2*j+1) for j in range(60)),F(0))
        er=q**121/F(121)
        return Q(s)+I(0,Q(er).hi) # 60 terms: next term positive
    return 16*atan(F(1,5))-4*atan(F(1,239))

def legendre(n,x):
    a,b=type(x)(1),x
    if n==0:return a
    for j in range(2,n+1):a,b=b,((2*j-1)*x*b-(j-1)*a)/j
    return b

@lru_cache(None)
def rule(n=8):
    proposals=np.polynomial.legendre.leggauss(n)[0];br=[]
    for guess in proposals:
        r=F(1,2**42);a=F(float(guess))-r;b=F(float(guess))+r
        fa,fb=legendre(n,a),legendre(n,b)
        if fa*fb>=0:raise ArithmeticError('Root sign isolation failed')
        for _ in range(80):
            c=(a+b)/2;fc=legendre(n,c)
            if fc==0:a=b=c;break
            if fa*fc<0:b,fb=c,fc
            else:a,fa=c,fc
        br.append((a,b))
    assert all(-1<a<=b<1 for a,b in br)
    assert all(br[j][1]<br[j+1][0] for j in range(n-1))
    x=I([float(Q(a).lo) for a,b in br],[float(Q(b).hi) for a,b in br])
    pn,pm=legendre(n,x),legendre(n-1,x)
    derivative=n*(x*pn-pm)/(x.square()-1)
    w=2/((1-x.square())*derivative.square())
    assert np.all(w.lo>0)
    for k in range(2*n):
        s=add_reduce(w*(x**k));truth=Q(F(2,k+1) if k%2==0 else F(0))
        assert s.lo<=truth.lo and truth.hi<=s.hi,(k,s.pair(),truth.pair())
    return x,w

def mapped_rule(a,b,n=8):
    a=a if isinstance(a,I) else I(a);b=b if isinstance(b,I) else I(b)
    x,w=rule(n);h=(b-a)/2;c=(a+b)/2
    if np.any(h.lo<0):raise ArithmeticError('Invalid quadrature interval')
    return c.reshape(-1,1)+h.reshape(-1,1)*x,h.reshape(-1,1)*w

def cauchy_remainder(length,h,radius,bound,n=8):
    """Positive rule exact through 2n-1: |int f-Qf| <= 2 |I| M q^(2n)/(1-q)."""
    q=h/Q(radius)
    if np.any(q.hi>=1):raise ArithmeticError('Cauchy disc does not contain cell strictly')
    return 2*length*Q(bound)*q**(2*n)/(1-q)

def weighted_moments(a,b,center,kind):
    """Three centered moments with separately enclosed analytic weight.
    v-weight = 2v exp(-.04v^2), z-weight = standard Gaussian density.
    Fixed Cauchy discs have radii 1/8 (v) and 2 (z).
    """
    nodes,w=mapped_rule(a,b);offset=nodes-center.reshape(-1,1)
    if kind=='v':
        density=2*nodes*exp(-Q('.04')*nodes.square());radius=F(1,8);M=F(3)
    elif kind=='z':
        density=exp(-nodes.square()/2)/sqrt(2*pi());radius=F(2);M=F(3)
    else:raise ValueError(kind)
    h=(b-a)/2;length=b-a;out=[]
    assert np.all(((a+b)/2-center).maxabs()<1/1024)
    for p in range(3):
        val=add_reduce(w*density*offset**p,axis=-1)
        er=cauchy_remainder(length,h,radius,M*(radius+F(1,1024))**p)
        v=val+I(-er.hi,er.hi)
        if p in (0,2):v=I(np.maximum(0,v.lo),v.hi)
        out.append(v)
    return out

if __name__=='__main__':
    import json
    x,w=rule();print(json.dumps({'status':'PASS','nodes':8,'rational_root_brackets':8,'polynomial_moments_checked':16,'weight_sum':add_reduce(w).pair(),'pi':pi().pair()},indent=2))
