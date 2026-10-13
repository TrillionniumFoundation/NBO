"""Binary64 directed differences for the original two-date investment law.

A first action is held fixed on a declared acquired cell. The last action is
looked up from the frozen terminal actor, including every intersected cell.
The final common innovation is integrated analytically, not sampled.
"""
from dataclasses import dataclass
import numpy as np


def down(x): return np.nextafter(np.asarray(x, dtype=float), -np.inf)
def up(x): return np.nextafter(np.asarray(x, dtype=float), np.inf)

@dataclass
class I:
    lo: object
    hi: object
    @staticmethod
    def exact(x): return I(np.asarray(x, dtype=float), np.asarray(x, dtype=float))
    @staticmethod
    def cast(x): return x if isinstance(x, I) else I.exact(x)
    def __add__(self, x):
        x = I.cast(x); return I(down(self.lo+x.lo), up(self.hi+x.hi))
    __radd__ = __add__
    def __neg__(self): return I(-self.hi, -self.lo)
    def __sub__(self, x): return self + -I.cast(x)
    def __rsub__(self, x): return I.cast(x) + -self
    def __mul__(self, x):
        x = I.cast(x)
        p = [self.lo*x.lo, self.lo*x.hi, self.hi*x.lo, self.hi*x.hi]
        return I(down(np.minimum.reduce(p)), up(np.maximum.reduce(p)))
    __rmul__ = __mul__
    def square(self):
        lo = np.where(self.lo >= 0, self.lo*self.lo,
                      np.where(self.hi <= 0, self.hi*self.hi, 0.))
        return I(np.maximum(0, down(lo)), up(np.maximum(self.lo*self.lo, self.hi*self.hi)))
    def positive(self): return I(np.maximum(0, self.lo), np.maximum(0, self.hi))
    def state(self):
        lo, hi = np.maximum(0, self.lo), np.minimum(1, self.hi)
        if np.any(lo > hi): raise AssertionError('Empty state box')
        return I(lo, hi)

class Actor:
    def __init__(self, actions):
        a = np.asarray(actions, dtype=np.int64); n = a.shape[0]
        if a.shape != (n,n) or np.any(a < 0): raise ValueError('Terminal actor')
        self.n = n; self.a = a.copy(); self.queries = self.ambiguous = 0
        self.low = np.zeros((n,n,n,n), dtype=np.int64); self.high = self.low.copy()
        for i in range(n):
            for k in range(i,n):
                for j in range(n):
                    for l in range(j,n):
                        block = a[i:k+1,j:l+1]
                        self.low[i,k,j,l] = block.min(); self.high[i,k,j,l] = block.max()
    def action(self, x):
        v = (x[0].lo,x[0].hi,x[1].lo,x[1].hi)
        c = tuple(np.clip(np.floor(z*self.n).astype(np.int64),0,self.n-1) for z in v)
        self.queries += np.size(c[0]); self.ambiguous += int(np.count_nonzero((c[0]!=c[1])|(c[2]!=c[3])))
        return I(self.low[c]/4096., self.high[c]/4096.)

def transition(x, a, w):
    return tuple((I.exact(1/16)+x[j]*.5+x[1-j]*.125+x[j]*(1-x[1-j])*.0625
                  +a*(.5 if j==0 else .25)+(w if j==0 else -w)).state() for j in range(2))

def shortage_difference(x,y,delta):
    u = (I.exact(.5)-x[0]-x[1]).positive()
    v = (I.exact(.5)-y[0]-y[1]).positive()
    d = -(delta[0]+delta[1]); natural = u-v
    lo = np.maximum(natural.lo, np.minimum(0,d.lo))
    hi = np.minimum(natural.hi, np.maximum(0,d.hi))
    if np.any(lo>hi): raise AssertionError('Inconsistent positive-part difference')
    return I(lo,hi)*(u+v)

def state_cost_difference(x,y,delta,terminal=False):
    squares = sum(delta[j]*(x[j]+y[j]-1.25) for j in range(2))
    cross = (delta[0]-delta[1])*(x[0]-x[1]+y[0]-y[1])*.25
    return (2 if terminal else 1)*squares+cross+2*shortage_difference(x,y,delta)

def action_cost_difference(b,a):
    d=b-a; total=b+a; squares=b.square()+a.square()
    return d*total*(1+4*squares)

def boxes(cell,n,r,q):
    if min(n,r,q)<=0 or any(v&(v-1) for v in (n,r,q)): raise ValueError('Dyadic partition required')
    i,j=cell
    if not (0<=i<n and 0<=j<n): raise ValueError('Cell outside cover')
    a,b,w=np.meshgrid(np.arange(r),np.arange(r),np.arange(q),indexing='ij')
    a,b,w=(v.reshape(-1) for v in (a,b,w))
    x=(I((i*r+a)/(n*r),(i*r+a+1)/(n*r)),I((j*r+b)/(n*r),(j*r+b+1)/(n*r)))
    shock=I(w/(16*q)-1/32,(w+1)/(16*q)-1/32)
    return x,shock

def evaluate(cell,n,r,q,b_index,a_index,actor):
    if b_index==a_index:
        return I.exact(np.zeros(r*r*q))
    x,w=boxes(cell,n,r,q); b=I.exact(b_index/4096);a=I.exact(a_index/4096)
    xb,xa=transition(x,b,w),transition(x,a,w)
    d=b-a;delta=(d*.5,d*.25)
    ab,aa=actor.action(xb),actor.action(xa)
    stage=state_cost_difference(xb,xa,delta)+action_cost_difference(ab,aa)
    mb,ma=transition(xb,ab,I.exact(0)),transition(xa,aa,I.exact(0))
    product_difference=delta[0]*xb[1]+xa[0]*delta[1]
    da=ab-aa
    dm=(delta[0]*(9/16)+delta[1]*.125-product_difference*.0625+da*.5,
        delta[1]*(9/16)+delta[0]*.125-product_difference*.0625+da*.25)
    result=action_cost_difference(b,a)+(15/16)*stage+(225/256)*state_cost_difference(mb,ma,dm,True)
    if np.any(~np.isfinite(result.lo)) or np.any(~np.isfinite(result.hi)) or np.any(result.lo>result.hi): raise AssertionError('Invalid paired cost')
    return result
