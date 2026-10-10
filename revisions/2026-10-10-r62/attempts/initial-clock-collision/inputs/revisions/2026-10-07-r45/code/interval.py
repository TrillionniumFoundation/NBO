"""Outward basic arithmetic retained from the R38/R44 verifier.
IEEE binary64 round-to-nearest with numpy.nextafter; finite values only.
"""
from dataclasses import dataclass
import numpy as np

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


