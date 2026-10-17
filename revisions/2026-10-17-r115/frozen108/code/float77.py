"""Binary64 whole-bin evaluator of frozen two-date investment actors.

All elementary operations are expanded outward. No fitted or optimal Bellman
value is used. The conditional estimator integrates the last innovation and
has the same original-law expected cost as the cash estimator.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


def down(x): return np.nextafter(np.asarray(x,dtype=np.float64),-np.inf)
def up(x): return np.nextafter(np.asarray(x,dtype=np.float64),np.inf)

@dataclass
class I:
    lo: object
    hi: object
    @staticmethod
    def exact(x): return I(np.asarray(x,dtype=np.float64),np.asarray(x,dtype=np.float64))
    @staticmethod
    def rat(p,q=1): return I(down(float(p)/q),up(float(p)/q))
    @staticmethod
    def cast(x): return x if isinstance(x,I) else I.exact(x)
    def __add__(self,other):
        b=I.cast(other);return I(down(self.lo+b.lo),up(self.hi+b.hi))
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,other):return self+-I.cast(other)
    def __rsub__(self,other):return I.cast(other)+-self
    def __mul__(self,other):
        b=I.cast(other);p=[self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi]
        return I(down(np.minimum.reduce(p)),up(np.maximum.reduce(p)))
    __rmul__=__mul__
    def square(self):
        low=np.where(self.lo>=0,self.lo*self.lo,np.where(self.hi<=0,self.hi*self.hi,0.0))
        high=np.maximum(self.lo*self.lo,self.hi*self.hi)
        return I(np.maximum(0,down(low)),up(high))
    def positive(self):return I(np.maximum(0,self.lo),np.maximum(0,self.hi))
    def state(self):
        lo=np.maximum(0,self.lo);hi=np.minimum(1,self.hi)
        if np.any(lo>hi):raise AssertionError('Empty state enclosure')
        return I(lo,hi)


def stage(x,a):
    return sum((z-I.rat(5,8)).square() for z in x)+(x[0]-x[1]).square()*I.rat(1,4)+2*(I.rat(1,2)-x[0]-x[1]).positive().square()+a.square()+4*a.square().square()

def terminal(x):
    return 2*sum((z-I.rat(5,8)).square() for z in x)+(x[0]-x[1]).square()*I.rat(1,4)+2*(I.rat(1,2)-x[0]-x[1]).positive().square()

def transition(x,a,w):
    return tuple((I.rat(1,16)+x[j]*I.rat(1,2)+x[1-j]*I.rat(1,8)+x[j]*(1-x[1-j])*I.rat(1,16)+a*I.rat(1,2 if j==0 else 4)+(w if j==0 else -w)).state() for j in range(2))

class Actor:
    def __init__(self,indices):
        self.indices=np.asarray(indices,dtype=np.int64)
        self.n=self.indices.shape[1]
        if self.indices.shape!=(2,self.n,self.n):raise ValueError('Bad actor dimensions')
        n=self.n;self.tables=[]
        for t in range(2):
            low=np.zeros((n,n,n,n),dtype=np.int64);high=low.copy()
            for i in range(n):
                for k in range(i,n):
                    for j in range(n):
                        for l in range(j,n):
                            values=self.indices[t,i:k+1,j:l+1]
                            low[i,k,j,l]=values.min();high[i,k,j,l]=values.max()
            self.tables.append((low,high))
        self.ambiguous_rows=0;self.action_calls=0
    def action(self,t,x):
        n=self.n
        corners=[np.clip(np.floor(v*n).astype(np.int64),0,n-1) for v in (x[0].lo,x[0].hi,x[1].lo,x[1].hi)]
        self.ambiguous_rows+=int(np.count_nonzero((corners[0]!=corners[1])|(corners[2]!=corners[3])))
        self.action_calls+=np.size(corners[0]);low,high=self.tables[t]
        return I(low[tuple(corners)]/4096.0,high[tuple(corners)]/4096.0)

def evaluate(indices,actor,bits=40):
    z=np.asarray(indices,dtype=np.uint64)
    if z.ndim!=2 or z.shape[1]!=4 or np.any(z>=2**bits):raise ValueError('Invalid path bins')
    cells=[I(z[:,j].astype(float)/2**bits,(z[:,j]+1).astype(float)/2**bits) for j in range(4)]
    x=tuple(v.state() for v in cells[:2]);a0=actor.action(0,x)
    c0=stage(x,a0);w0=cells[2]*I.rat(1,16)-I.rat(1,32)
    y=transition(x,a0,w0);a1=actor.action(1,y)
    base=c0+I.rat(15,16)*stage(y,a1)
    last=transition(y,a1,cells[3]*I.rat(1,16)-I.rat(1,32))
    cash=base+I.rat(225,256)*terminal(last)
    mean_state=transition(y,a1,I.exact(0))
    conditional=base+I.rat(225,256)*(terminal(mean_state)+I.rat(5,3072))
    for value in (cash,conditional):
        if np.any(~np.isfinite(value.lo)) or np.any(~np.isfinite(value.hi)) or np.any(value.lo>value.hi):raise AssertionError('Invalid cost enclosure')
    return cash,conditional
