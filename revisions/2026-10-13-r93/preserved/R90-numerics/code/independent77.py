"""Independent integer-directed original-economy evaluator.

No production interval or economic routine is imported. Endpoints are Python
integers in units 2^-48. Expanded cost/transition polynomials and exhaustive
acquisition rectangles differ from the binary64 implementation.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
import numpy as np
S=1<<48

def floor_div(a,b):return a//b
def ceil_div(a,b):return -((-a)//b)

@dataclass
class Z:
    lo: object
    hi: object
    def __post_init__(self):
        self.lo=np.asarray(self.lo,dtype=object);self.hi=np.asarray(self.hi,dtype=object)
    @staticmethod
    def const(p,q=1):return Z((p*S)//q,-((-p*S)//q))
    @staticmethod
    def cast(v):return v if isinstance(v,Z) else Z.const(v)
    def __add__(self,v):
        v=Z.cast(v);return Z(self.lo+v.lo,self.hi+v.hi)
    __radd__=__add__
    def __neg__(self):return Z(-self.hi,-self.lo)
    def __sub__(self,v):return self+-Z.cast(v)
    def __rsub__(self,v):return Z.cast(v)+-self
    def scale(self,p,q=1):
        if p<0:return (-self).scale(-p,q)
        if q<=0:raise ValueError('Nonpositive divisor')
        return Z((self.lo*p)//q,-((-self.hi*p)//q))
    def __mul__(self,v):
        v=Z.cast(v);prods=[self.lo*v.lo,self.lo*v.hi,self.hi*v.lo,self.hi*v.hi]
        return Z(np.minimum.reduce(prods)//S,-((-np.maximum.reduce(prods))//S))
    __rmul__=__mul__
    def sq(self):
        lower=np.where(self.lo>=0,self.lo*self.lo,np.where(self.hi<=0,self.hi*self.hi,0))
        upper=np.maximum(self.lo*self.lo,self.hi*self.hi)
        return Z(lower//S,-((-upper)//S))
    def pos(self):return Z(np.maximum(0,self.lo),np.maximum(0,self.hi))
    def state(self):
        a=np.maximum(0,self.lo);b=np.minimum(S,self.hi)
        if np.any(a>b):raise AssertionError('Integer state intersection empty')
        return Z(a,b)

def running(x,a):
    squares=x[0].sq()+x[1].sq();cross=x[0]*x[1]
    return squares.scale(5,4)-cross.scale(1,2)-(x[0]+x[1]).scale(5,4)+Z.const(25,32)+(Z.const(1,2)-x[0]-x[1]).pos().sq().scale(2)+a.sq()+a.sq().sq().scale(4)

def final(x):
    return (x[0].sq()+x[1].sq()).scale(9,4)-(x[0]*x[1]).scale(1,2)-(x[0]+x[1]).scale(5,2)+Z.const(25,16)+(Z.const(1,2)-x[0]-x[1]).pos().sq().scale(2)

def step(x,a,shock):
    product=(x[0]*x[1]).scale(1,16)
    first=Z.const(1,16)+x[0].scale(9,16)+x[1].scale(1,8)-product+a.scale(1,2)+shock
    second=Z.const(1,16)+x[1].scale(9,16)+x[0].scale(1,8)-product+a.scale(1,4)-shock
    return first.state(),second.state()

class IntegerActor:
    def __init__(self,actions):
        self.a=np.asarray(actions,dtype=np.int64).copy();self.n=self.a.shape[1]
        if self.a.shape!=(2,self.n,self.n):raise ValueError('Integer actor shape')
        self.ambiguous_rows=0;self.action_calls=0;self.rectangles=0
    def action(self,t,x):
        n=self.n
        corner=[np.clip(np.asarray(v*n//S,dtype=np.int64),0,n-1) for v in (x[0].lo,x[0].hi,x[1].lo,x[1].hi)]
        code=((corner[0]*n+corner[1])*n+corner[2])*n+corner[3]
        keys,inverse=np.unique(code,return_inverse=True);lo=[];hi=[]
        for key in keys:
            i,k,j,l=np.unravel_index(int(key),(n,n,n,n))
            vals=[int(self.a[t,u,v]) for u in range(i,k+1) for v in range(j,l+1)]
            if not vals:raise AssertionError('Empty acquired rectangle')
            lo.append(min(vals)*(S//4096));hi.append(max(vals)*(S//4096))
        self.rectangles+=len(keys);self.action_calls+=len(code)
        self.ambiguous_rows+=int(np.count_nonzero((corner[0]!=corner[1])|(corner[2]!=corner[3])))
        return Z(np.asarray(lo,dtype=object)[inverse],np.asarray(hi,dtype=object)[inverse])

def evaluate(indices,actor,bits=40):
    if bits>48:raise ValueError('Source bins finer than independent grid')
    z=np.asarray(indices,dtype=np.uint64)
    cells=[Z(z[:,j].astype(object)*(1<<(48-bits)),(z[:,j].astype(object)+1)*(1<<(48-bits))) for j in range(4)]
    x=cells[:2];a=actor.action(0,x)
    base=running(x,a);y=step(x,a,cells[2].scale(1,16)-Z.const(1,32))
    b=actor.action(1,y);base=base+running(y,b).scale(15,16)
    last=step(y,b,cells[3].scale(1,16)-Z.const(1,32))
    cash=base+final(last).scale(225,256)
    mean=step(y,b,Z.const(0))
    conditional=base+(final(mean)+Z.const(5,3072)).scale(225,256)
    answer=[]
    for value in (cash,conditional):
        if np.any(value.lo>value.hi):raise AssertionError('Reversed independent endpoints')
        answer.extend((np.asarray(value.lo,dtype=np.int64),np.asarray(value.hi,dtype=np.int64)))
    return np.asarray(answer)

def exact_point(row,actions,bits=40):
    """A separate rational midpoint trajectory; no interval routines called."""
    z=[F(2*int(v)+1,2**(bits+1)) for v in row];x=z[:2];n=actions.shape[1]
    def action(t,y):
        i=min(n-1,int(y[0]*n));j=min(n-1,int(y[1]*n))
        a=F(int(actions[t,i,j]),4096)
        if a<0 or a>F(1,8)+sum(y)/16:raise AssertionError('Exact path infeasible')
        return a
    def c(y,a):
        return sum((v-F(5,8))**2 for v in y)+(y[0]-y[1])**2/4+2*max(F(0),F(1,2)-sum(y))**2+a*a+4*a**4
    def move(y,a,w):
        return [F(1,16)+y[j]/2+y[1-j]/8+y[j]*(1-y[1-j])/16+(F(1,2) if j==0 else F(1,4))*a+(w if j==0 else -w) for j in range(2)]
    def g(y):return 2*sum((v-F(5,8))**2 for v in y)+(y[0]-y[1])**2/4+2*max(F(0),F(1,2)-sum(y))**2
    a=action(0,x);y=move(x,a,z[2]/16-F(1,32));b=action(1,y)
    base=c(x,a)+F(15,16)*c(y,b)
    cash=base+F(225,256)*g(move(y,b,z[3]/16-F(1,32)))
    mean=move(y,b,F(0));conditional=base+F(225,256)*(g(mean)+F(5,3072))
    return cash,conditional
