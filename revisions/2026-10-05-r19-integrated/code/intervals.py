"""Binary64 outward intervals; elementary functions use proved series bounds.

Every primitive is widened by one nextafter. The certificate requires IEEE-754
round-to-nearest basic arithmetic with gradual underflow (tested at startup).
There is no assumption about libm tanh/log being correctly rounded.
"""
from __future__ import annotations
import numpy as np


def down(x): return np.nextafter(np.asarray(x, dtype=np.float64), -np.inf)
def up(x): return np.nextafter(np.asarray(x, dtype=np.float64), np.inf)

class I:
    __array_priority__ = 1000
    def __init__(self, lo, hi=None):
        self.lo = np.asarray(lo, dtype=np.float64)
        self.hi = np.asarray(lo if hi is None else hi, dtype=np.float64)
        if np.any(self.lo > self.hi) or np.any(np.isnan(self.lo)) or np.any(np.isnan(self.hi)):
            raise ValueError('invalid interval')
    @staticmethod
    def of(x): return x if isinstance(x, I) else I(x)
    def __add__(self, x):
        x=I.of(x); return I(down(self.lo+x.lo),up(self.hi+x.hi))
    __radd__=__add__
    def __neg__(self): return I(-self.hi,-self.lo)
    def __sub__(self, x): return self+-I.of(x)
    def __rsub__(self, x): return I.of(x)+-self
    def __mul__(self, x):
        x=I.of(x)
        p=np.stack(np.broadcast_arrays(self.lo*x.lo,self.lo*x.hi,self.hi*x.lo,self.hi*x.hi))
        return I(down(p.min(0)),up(p.max(0)))
    __rmul__=__mul__
    def __truediv__(self, x):
        x=I.of(x)
        if np.any((x.lo<=0)&(x.hi>=0)): raise ZeroDivisionError('interval contains zero')
        return self*I(down(1/x.hi),up(1/x.lo))
    def __rtruediv__(self,x): return I.of(x)/self
    def square(self):
        low=np.minimum(self.lo*self.lo,self.hi*self.hi)
        low=np.where((self.lo<=0)&(self.hi>=0),0,down(low))
        return I(low,up(np.maximum(self.lo*self.lo,self.hi*self.hi)))
    def __getitem__(self,key): return I(self.lo[key],self.hi[key])
    def sum(self,axis=-1,keepdims=False):
        lo=np.moveaxis(self.lo,axis,-1); hi=np.moveaxis(self.hi,axis,-1)
        if lo.shape[-1]==0: raise ValueError('empty sum')
        while lo.shape[-1]>1:
            if lo.shape[-1]%2:
                lo=np.concatenate([lo,np.zeros_like(lo[...,:1])],-1)
                hi=np.concatenate([hi,np.zeros_like(hi[...,:1])],-1)
            lo=down(lo[...,::2]+lo[...,1::2]);hi=up(hi[...,::2]+hi[...,1::2])
        lo,hi=lo[...,0],hi[...,0]
        if keepdims:
            lo=np.expand_dims(lo,axis);hi=np.expand_dims(hi,axis)
        return I(lo,hi)
    def mean(self,axis=-1,keepdims=False): return self.sum(axis,keepdims)/self.lo.shape[axis]
    def tanh(self):
        return I(_tanh_point(self.lo).lo,_tanh_point(self.hi).hi)
    def log(self):
        if np.any(self.lo<=0): raise ValueError('log requires positive interval')
        return I(_log_point(self.lo).lo,_log_point(self.hi).hi)


def _exp_positive_point(x):
    """x>=0; Taylor degree 18 after exact binary scaling to [0,1/2]."""
    x=np.asarray(x,dtype=np.float64)
    if np.any(x<0) or np.any(x>300): raise ValueError('exp domain [0,300]')
    k=0
    while np.max(x,initial=0)/2**k>.5: k+=1
    t=I(np.ldexp(x,-k)); term=I(np.ones_like(x)); total=term
    for j in range(1,19):
        term=term*t/j;total=total+term
    tail=(term*t/19)/(1-t/20)
    total=I(total.lo,(total+tail).hi)
    for _ in range(k): total=total.square()
    return total

def _tanh_point(x):
    x=np.asarray(x,dtype=np.float64)
    if not np.isfinite(x).all() or np.max(np.abs(x),initial=0)>100:
        raise ValueError('certified tanh domain [-100,100]')
    a=np.abs(x)
    # 2*a is exactly representable on this domain except subnormals, where
    # multiplication by two is exact as well.
    em=1/_exp_positive_point(2*a)
    v=(1-em)/(1+em)
    return I(np.where(x<0,-v.hi,v.lo),np.where(x<0,-v.lo,v.hi))

def _log_point(x):
    """atanh series on mantissa [1,2), with a rational tail bound."""
    m,e=np.frexp(np.asarray(x,dtype=np.float64));m=2*m;e=e-1
    z=(I(m)-1)/(I(m)+1);z2=z.square();term=z;total=z
    for j in range(1,32):
        term=term*z2;total=total+term/(2*j+1)
    tail=(term*z2/65)/(1-z2)
    logm=I((2*total).lo,(2*(total+tail)).hi)
    # Adjacent binary64 endpoints around log(2); verified as exact rationals
    # by the same positive series at z=1/3 in the test suite and proof.
    ln2=I(float.fromhex('0x1.62e42fefa39eep-1'),float.fromhex('0x1.62e42fefa39f0p-1'))
    return logm+I(e)*ln2

def environment_check():
    if np.finfo(np.float64).nmant !=52 or np.nextafter(0.,1.)==0:
        raise RuntimeError('IEEE binary64 gradual underflow required')
    if (1.+2.**-53)!=1. or (1.+3*2.**-53)!=(1.+2.**-51):
        raise RuntimeError('round-to-nearest ties-to-even required')
    return True
