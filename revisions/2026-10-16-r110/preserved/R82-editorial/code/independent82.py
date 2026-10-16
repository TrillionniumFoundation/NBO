"""Separate fixed-point implementation of first-action economic contrasts.

Uses Python-integer endpoints at 2^-48, expanded polynomials, exhaustive actor
rectangles, and rational antiderivatives for the terminal common shock. It
imports no binary64 interval, cost, transition, actor or partition routine.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import numpy as np
S=1<<48

@dataclass
class Z:
    lo: object
    hi: object
    def __post_init__(self):
        self.lo=np.asarray(self.lo,dtype=object);self.hi=np.asarray(self.hi,dtype=object)
    @staticmethod
    def const(p,q=1): return Z((p*S)//q,-((-p*S)//q))
    @staticmethod
    def cast(v): return v if isinstance(v,Z) else Z.const(v)
    def __add__(self,v):
        v=Z.cast(v);return Z(self.lo+v.lo,self.hi+v.hi)
    __radd__=__add__
    def __neg__(self):return Z(-self.hi,-self.lo)
    def __sub__(self,v):return self+-Z.cast(v)
    def __rsub__(self,v):return Z.cast(v)+-self
    def scale(self,p,q=1):
        if q<=0:raise ValueError('Divisor')
        if p<0:return (-self).scale(-p,q)
        return Z((self.lo*p)//q,-((-self.hi*p)//q))
    def __mul__(self,v):
        v=Z.cast(v);a=[self.lo*v.lo,self.lo*v.hi,self.hi*v.lo,self.hi*v.hi]
        return Z(np.minimum.reduce(a)//S,-((-np.maximum.reduce(a))//S))
    __rmul__=__mul__
    def square(self):
        ls=np.asarray(self.lo*self.lo,dtype=object);hs=np.asarray(self.hi*self.hi,dtype=object)
        a=np.where(self.lo>=0,ls,np.where(self.hi<=0,hs,np.asarray(0,dtype=object)))
        b=np.maximum(ls,hs)
        return Z(a//S,-((-b)//S))
    def positive(self):return Z(np.maximum(0,self.lo),np.maximum(0,self.hi))
    def state(self):
        a,b=np.maximum(0,self.lo),np.minimum(S,self.hi)
        if np.any(a>b):raise AssertionError('Independent state containment')
        return Z(a,b)

class Actor:
    def __init__(self,actions):
        self.a=np.asarray(actions,dtype=np.int64).copy();self.n=len(self.a)
        if self.a.shape!=(self.n,self.n):raise ValueError('Terminal actor shape')
        self.queries=self.ambiguous=self.rectangles=0
    def action(self,x):
        n=self.n
        corners=[np.clip(np.asarray(v*n//S,dtype=np.int64),0,n-1) for v in (x[0].lo,x[0].hi,x[1].lo,x[1].hi)]
        codes=((corners[0]*n+corners[1])*n+corners[2])*n+corners[3]
        keys,inverse=np.unique(codes,return_inverse=True);lo=[];hi=[]
        for code in keys:
            i,k,j,l=np.unravel_index(int(code),(n,n,n,n))
            values=[int(self.a[u,v]) for u in range(i,k+1) for v in range(j,l+1)]
            if not values:raise AssertionError('Empty acquired rectangle')
            lo.append(min(values)*(S//4096));hi.append(max(values)*(S//4096))
        self.queries+=len(codes);self.rectangles+=len(keys)
        self.ambiguous+=int(np.count_nonzero((corners[0]!=corners[1])|(corners[2]!=corners[3])))
        return Z(np.asarray(lo,dtype=object)[inverse],np.asarray(hi,dtype=object)[inverse])

def move(x,a,w):
    xy=(x[0]*x[1]).scale(1,16)
    z0=Z.const(1,16)+x[0].scale(9,16)+x[1].scale(1,8)-xy+a.scale(1,2)+w
    z1=Z.const(1,16)+x[1].scale(9,16)+x[0].scale(1,8)-xy+a.scale(1,4)-w
    return z0.state(),z1.state()

def penalty_delta(x,y,d):
    px=(Z.const(1,2)-sum(x)).positive();py=(Z.const(1,2)-sum(y)).positive()
    change=-sum(d);independent=px-py
    low=np.maximum(independent.lo,np.minimum(0,change.lo))
    high=np.minimum(independent.hi,np.maximum(0,change.hi))
    if np.any(low>high):raise AssertionError('Independent shortage intersection')
    return Z(low,high)*(px+py)

def polynomial_delta(x,y,d,last=False):
    squares=sum(d[j]*(x[j]+y[j]) for j in range(2))
    product=d[0]*x[1]+y[0]*d[1]
    return squares.scale(9 if last else 5,4)-product.scale(1,2)-sum(d).scale(5,2 if last else 4)+penalty_delta(x,y,d).scale(2)

def investment_delta(b,a):
    product=(b-a)*(b+a)
    return product+(product*(b.square()+a.square())).scale(4)

def evaluate(cell,n,r,q,b_index,a_index,actor):
    if b_index==a_index:return Z(np.zeros(r*r*q,dtype=object),np.zeros(r*r*q,dtype=object))
    if any(v<=0 or v&(v-1) for v in (n,r,q)) or n*r>S or 16*q>S:raise ValueError('Invalid dyadic partition')
    i,j=cell
    if not 0<=i<n or not 0<=j<n:raise ValueError('Cell')
    u=np.repeat(np.arange(r),r*q).astype(object)
    v=np.tile(np.repeat(np.arange(r),q),r).astype(object)
    z=np.tile(np.arange(q),r*r).astype(object)
    scale=S//(n*r)
    x=(Z((i*r+u)*scale,(i*r+u+1)*scale),Z((j*r+v)*scale,(j*r+v+1)*scale))
    w=Z(z*(S//(16*q))-S//32,(z+1)*(S//(16*q))-S//32)
    b,a=Z.const(b_index,4096),Z.const(a_index,4096)
    xb,xa=move(x,b,w),move(x,a,w)
    diff=b-a;d=(diff.scale(1,2),diff.scale(1,4))
    ab,aa=actor.action(xb),actor.action(xa)
    first=investment_delta(b,a)
    nextcost=polynomial_delta(xb,xa,d)+investment_delta(ab,aa)
    mb,ma=move(xb,ab,Z.const(0)),move(xa,aa,Z.const(0))
    dp=d[0]*xb[1]+xa[0]*d[1];da=ab-aa
    dm=(d[0].scale(9,16)+d[1].scale(1,8)-dp.scale(1,16)+da.scale(1,2),
        d[1].scale(9,16)+d[0].scale(1,8)-dp.scale(1,16)+da.scale(1,4))
    out=first+nextcost.scale(15,16)+polynomial_delta(mb,ma,dm,True).scale(225,256)
    if np.any(out.lo>out.hi):raise AssertionError('Independent paired endpoint order')
    return out

def exact_point(cell,n,r,q,row,b_index,a_index,actions):
    """Direct rational conditional cash costs; no paired interval identities."""
    u,v,w=map(int,np.unravel_index(int(row),(r,r,q)));i,j=map(int,cell)
    x=[F(2*(i*r+u)+1,2*n*r),F(2*(j*r+v)+1,2*n*r)]
    shock=F(2*w+1,32*q)-F(1,32)
    def step(y,a,z):
        return [F(1,16)+y[k]/2+y[1-k]/8+y[k]*(1-y[1-k])/16+F(1,2 if k==0 else 4)*a+(z if k==0 else -z) for k in range(2)]
    def statecost(y,terminal=False):
        return (2 if terminal else 1)*sum((v-F(5,8))**2 for v in y)+(y[0]-y[1])**2/4+2*max(F(0),F(1,2)-sum(y))**2
    def total(index):
        a=F(index,4096)
        if a<0 or a>F(1,8)+sum(x)/16:raise AssertionError('Exact forced action infeasible')
        y=step(x,a,shock);ix=[min(n-1,int(v*n)) for v in y];p=F(int(actions[tuple(ix)]),4096)
        if p<0 or p>F(1,8)+sum(y)/16:raise AssertionError('Exact terminal action infeasible')
        mean=step(y,p,F(0))
        # Opposite-signed final innovation leaves the shortage sum invariant.
        # The quadratic expectation correction is 5 E[W^2] = 5/3072.
        return statecost(x)+a*a+4*a**4+F(15,16)*(statecost(y)+p*p+4*p**4)+F(225,256)*(statecost(mean,True)+F(5,3072))
    return total(b_index)-total(a_index)
