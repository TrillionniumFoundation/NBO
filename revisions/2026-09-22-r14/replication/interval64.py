"""Standalone outward binary64 interval arithmetic used only by R14.

No imports from any R8--R12 arithmetic or certifier. Elementary exp/log/tanh
are enclosed by rational Taylor series, not by NumPy transcendental calls.
Trusted model: IEEE-754 binary64 basic arithmetic, gradual underflow, and
correct nextafter/frexp/ldexp. NaNs, infinities, invalid divisions fail closed.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
import math
import numpy as np

DN, UP = -np.inf, np.inf

def down(x): return np.nextafter(x, DN)
def up(x): return np.nextafter(x, UP)

@dataclass
class I:
    lo: np.ndarray
    hi: np.ndarray
    def __init__(self, lo, hi=None):
        self.lo = np.asarray(lo, dtype=np.float64)
        self.hi = np.asarray(lo if hi is None else hi, dtype=np.float64)
        if np.any(self.lo > self.hi) or not (np.isfinite(self.lo).all() and np.isfinite(self.hi).all()):
            raise ArithmeticError('Invalid/nonfinite interval')
    @staticmethod
    def rational(x):
        q=Fraction(x); f=float(q)
        return I(math.nextafter(f,-math.inf) if Fraction(f)>q else f,
                 math.nextafter(f,math.inf) if Fraction(f)<q else f)
    def __add__(self, b):
        b=as_i(b); return I(down(self.lo+b.lo),up(self.hi+b.hi))
    __radd__=__add__
    def __neg__(self): return I(-self.hi,-self.lo)
    def __sub__(self,b): return self+-as_i(b)
    def __rsub__(self,b): return as_i(b)+-self
    def __mul__(self,b):
        b=as_i(b)
        aa,bb=np.broadcast_arrays(self.lo,b.lo)
        q=np.stack([self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi])
        return I(down(np.min(q,axis=0)),up(np.max(q,axis=0)))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=as_i(b)
        if np.any((b.lo<=0)&(b.hi>=0)): raise ArithmeticError('Division through zero')
        return self*I(down(1/b.hi),up(1/b.lo))
    def __rtruediv__(self,b): return as_i(b)/self
    def square(self):
        q=np.stack([self.lo*self.lo,self.hi*self.hi])
        low=np.where((self.lo<=0)&(self.hi>=0),0,np.maximum(0,down(q.min(axis=0))))
        return I(low,up(q.max(axis=0)))
    def __pow__(self,n):
        if not isinstance(n,int) or n<0: raise ValueError('Nonnegative integer powers only')
        z=I(1); a=self
        while n:
            if n&1:z=z*a
            n//=2
            if n:a=a.square()
        return z
    def __getitem__(self,key): return I(self.lo[key],self.hi[key])
    def reshape(self,*shape): return I(self.lo.reshape(*shape),self.hi.reshape(*shape))
    def maxabs(self): return np.maximum(abs(self.lo),abs(self.hi))
    def clip(self,lo,hi):
        # Constants must themselves be inward-valid exact binary endpoints.
        return I(np.clip(self.lo,lo,hi),np.clip(self.hi,lo,hi))
    def intersect(self,lo,hi): return I(np.maximum(self.lo,lo),np.minimum(self.hi,hi))
    def pair(self): return [float(self.lo),float(self.hi)]

def as_i(x):return x if isinstance(x,I) else I(x)
def cat(xs,axis=0):return I(np.concatenate([x.lo for x in xs],axis),np.concatenate([x.hi for x in xs],axis))
def stack(xs,axis=0):return I(np.stack([x.lo for x in xs],axis),np.stack([x.hi for x in xs],axis))
def add_reduce(a,axis=0):
    a=I(np.moveaxis(a.lo,axis,0),np.moveaxis(a.hi,axis,0))
    while len(a.lo)>1:
        n=len(a.lo)//2; z=a[:2*n:2]+a[1:2*n:2]
        a=cat([z,a[-1:].reshape(1,*a.lo.shape[1:])]) if len(a.lo)%2 else z
    return a[0]

def affine(a,weight,bias=None):
    """No BLAS reduction; every product and every sum is rounded outward."""
    w=np.asarray(weight,dtype=np.float64)
    if a.lo.shape[-1]!=w.shape[1]:raise ValueError('Affine shape')
    outshape=(*a.lo.shape[:-1],w.shape[0]);r=I(np.zeros(outshape))
    for j in range(w.shape[1]):
        r=r+a[...,j].reshape(*a.lo.shape[:-1],1)*I(w[:,j])
    return r if bias is None else r+I(np.asarray(bias,dtype=np.float64))

def exp(a):
    a=as_i(a);mx=float(a.maxabs().max());s=0
    while math.ldexp(mx,-s)>.125:s+=1
    r=a*I(math.ldexp(1.,-s));p=I.rational(Fraction(1,math.factorial(18)))
    for j in range(17,-1,-1):p=p*r+I.rational(Fraction(1,math.factorial(j)))
    er=I.rational(Fraction(8,7)*Fraction(1,8)**19/math.factorial(19)).hi
    p=p+I(-er,er)
    for _ in range(s):p=p.square()
    return p

def _log_mantissa(m):
    y=(m-1)/(m+1);q=y.square();p=I.rational(Fraction(1,79))
    for j in range(38,-1,-1):p=p*q+I.rational(Fraction(1,2*j+1))
    tail=I.rational(2*Fraction(1,3)**81/(81*(1-Fraction(1,9)))).hi
    return 2*y*p+I(-tail,tail)

_LOG2=None

def _log_point(x):
    global _LOG2
    if _LOG2 is None:_LOG2=_log_mantissa(I(2.))
    m,e=np.frexp(np.asarray(x,dtype=float));m=np.ldexp(m,1);e=e-1
    return _log_mantissa(I(m))+I(e)*_LOG2

def log(a):
    a=as_i(a)
    if np.any(a.lo<=0):raise ArithmeticError('Log domain')
    low=_log_point(a.lo);high=_log_point(a.hi)
    return I(low.lo,high.hi)

def tanh(a):
    a=as_i(a)
    def point_t(x):return 1-2/(1+exp(2*I(x)))
    lower=point_t(a.lo);upper=point_t(a.hi)
    return I(np.maximum(-1,lower.lo),np.minimum(1,upper.hi))

def exact_clip(a,low,high):
    """Enclose projection onto exact rational (not binary64) endpoints."""
    a=as_i(a);l=I.rational(low);h=I.rational(high)
    return I(np.maximum(l.lo,np.minimum(h.lo,a.lo)),np.maximum(l.hi,np.minimum(h.hi,a.hi)))

def test():
    import mpmath as mp
    mp.mp.dps=100;rng=np.random.default_rng(1441);n=0
    def check(z,v):
        nonlocal n
        assert mp.mpf(float(z.lo))<=v<=mp.mpf(float(z.hi)),(z.pair(),str(v));n+=1
    for x in np.r_[np.linspace(-15,15,101),rng.normal(size=100),0.,np.nextafter(0.,1.)]:
        check(exp(I(x)),mp.exp(mp.mpf(float(x))))
        check(tanh(I(x)),mp.tanh(mp.mpf(float(x))))
    for x in np.geomspace(.0001,1000,101):check(log(I(x)),mp.log(mp.mpf(float(x))))
    for _ in range(100):
        a,b=rng.normal(size=2); aa,bb=mp.mpf(float(a)),mp.mpf(float(b))
        check(I(a)+I(b),aa+bb);check(I(a)*I(b),aa*bb);check(I(a)/I(b),aa/bb)
    return {'status':'PASS','point_enclosure_checks':n,'reference_digits':100,
      'production_certifier_imports':False,'elementary_transcendentals':'rational Taylor enclosures'}

if __name__=='__main__':
    import json
    print(json.dumps(test(),indent=2))
