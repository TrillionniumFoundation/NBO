"""Outward binary64 intervals. Inputs denote exact stored binary numbers.

Each elementary operation is expanded with nextafter, including every term
of a reduction. No BLAS reduction or approximate optimizer certifies a bound.
"""
from __future__ import annotations
import numpy as np

def down(x): return np.nextafter(np.asarray(x, dtype=np.float64), -np.inf)
def up(x): return np.nextafter(np.asarray(x, dtype=np.float64), np.inf)

class I:
    __slots__ = ('lo', 'hi')
    def __init__(self, lo, hi=None):
        self.lo = np.asarray(lo, dtype=np.float64)
        self.hi = self.lo if hi is None else np.asarray(hi, dtype=np.float64)
    def __add__(self, b):
        b=as_i(b); return I(down(self.lo+b.lo), up(self.hi+b.hi))
    __radd__=__add__
    def __neg__(self): return I(-self.hi,-self.lo)
    def __sub__(self,b): return self+-as_i(b)
    def __rsub__(self,b): return as_i(b)+-self
    def __mul__(self,b):
        b=as_i(b)
        p=(self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi)
        return I(down(np.minimum.reduce(p)),up(np.maximum.reduce(p)))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=as_i(b)
        if np.any((b.lo<=0)&(b.hi>=0)): raise ValueError('Zero in interval divisor')
        return self*I(down(1/b.hi),up(1/b.lo))
    def __rtruediv__(self,b): return as_i(b)/self
    def __getitem__(self,k): return I(self.lo[k],self.hi[k])
    def square(self):
        lo=np.where((self.lo<=0)&(self.hi>=0),0,np.minimum(self.lo*self.lo,self.hi*self.hi))
        return I(np.maximum(0,down(lo)),up(np.maximum(self.lo*self.lo,self.hi*self.hi)))
    def positive(self): return I(np.maximum(0,self.lo),np.maximum(0,self.hi))
    def clamp(self,lo,hi): return I(np.clip(self.lo,lo,hi),np.clip(self.hi,lo,hi))
    def sum(self,axis=-1):
        l=np.moveaxis(self.lo,axis,-1); h=np.moveaxis(self.hi,axis,-1)
        ans=I(np.zeros(l.shape[:-1]))
        for j in range(l.shape[-1]): ans=ans+I(l[...,j],h[...,j])
        return ans
    def mid(self): return self.lo+(self.hi-self.lo)/2
    def checked(self):
        if not np.all(np.isfinite(self.lo)) or not np.all(np.isfinite(self.hi)) or np.any(self.lo>self.hi):
            raise ArithmeticError('Invalid or nonfinite interval')
        return self

def as_i(x): return x if isinstance(x,I) else I(x)
def stack(xs,axis=-1): return I(np.stack([as_i(x).lo for x in xs],axis),np.stack([as_i(x).hi for x in xs],axis))
def roll(x,k,axis=-1):
    x=as_i(x);return I(np.roll(x.lo,k,axis),np.roll(x.hi,k,axis))
def expand(x,axis):
    x=as_i(x);return I(np.expand_dims(x.lo,axis),np.expand_dims(x.hi,axis))
