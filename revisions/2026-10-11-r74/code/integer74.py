"""Independent dyadic-integer path enclosures; no production numerical imports.

Every operation is rounded outwards at scale 2**80 using arbitrary precision
integers. Conditional on a bin, the full continuous rectangle is evaluated.
"""
from fractions import Fraction
import math
import numpy as np
S=1<<80
class Q:
    def __init__(self,lo,hi=None):
        self.lo=np.atleast_1d(np.asarray(lo,dtype=object));self.hi=np.atleast_1d(np.asarray(lo if hi is None else hi,dtype=object))
    @staticmethod
    def const(x):
        if isinstance(x,Q):return x
        v=Fraction(x);lo=v.numerator*S//v.denominator;hi=-((-v.numerator*S)//v.denominator)
        return Q(lo,hi)
    def __add__(self,v):
        v=Q.const(v);return Q(self.lo+v.lo,self.hi+v.hi)
    __radd__=__add__
    def __sub__(self,v):
        v=Q.const(v);return Q(self.lo-v.hi,self.hi-v.lo)
    def __rsub__(self,v):return Q.const(v)-self
    def __mul__(self,v):
        v=Q.const(v)
        aa=self.lo*v.lo;bb=self.lo*v.hi;cc=self.hi*v.lo;dd=self.hi*v.hi
        low=np.minimum(np.minimum(aa,bb),np.minimum(cc,dd));high=np.maximum(np.maximum(aa,bb),np.maximum(cc,dd))
        return Q(low//S,-((-high)//S))
    __rmul__=__mul__
    def square(self):
        low=np.where((self.lo<=0)&(self.hi>=0),0,np.minimum(self.lo*self.lo,self.hi*self.hi))
        high=np.maximum(self.lo*self.lo,self.hi*self.hi)
        return Q(low//S,-((-high)//S))
    def positive(self):return Q(np.maximum(self.lo,0),np.maximum(self.hi,0))
    def unit(self):
        low=np.maximum(self.lo,0);high=np.minimum(self.hi,S)
        if np.any(low>high):raise AssertionError('Empty invariant-state intersection')
        return Q(low,high)

def action(policy,date,states):
    n=int(policy['n']);table=policy['actions'][date]
    left=[np.maximum(0,np.minimum(n-1,(v.lo*n)//S)).astype(np.int64) for v in states]
    right=[np.maximum(0,np.minimum(n-1,(v.hi*n)//S)).astype(np.int64) for v in states]
    low=table[left[0],left[1]].astype(object);high=low.copy();amb=0
    for k in np.flatnonzero((left[0]!=right[0])|(left[1]!=right[1])):
        values=[int(table[i,j]) for i in range(left[0][k],right[0][k]+1) for j in range(left[1][k],right[1][k]+1)]
        low[k]=min(values);high[k]=max(values);amb+=1
    return Q(low*(S//4096),high*(S//4096)),amb

def path(policy,bins,bits=40):
    b=np.asarray(bins,dtype=object);den=1<<bits
    state=[Q(b[:,i]*(S//den),(b[:,i]+1)*(S//den)) for i in (0,1)]
    running=Q(np.zeros(len(b),dtype=object));amb=[];beta=Fraction(15,16)
    for t in (0,1):
        a,n=action(policy,t,state);amb.append(n);x,y=state
        loss=(x-Fraction(5,8)).square()+(y-Fraction(5,8)).square()
        loss=loss+(x-y).square()*Fraction(1,4)+(Fraction(1,2)-x-y).positive().square()*2
        loss=loss+a.square()+a.square().square()*4
        running=running+loss*beta**t
        z=Q((b[:,2+t]-den//2)*(S//(16*den)),(b[:,2+t]+1-den//2)*(S//(16*den)))
        # Expanded transition differs from the production factorization.
        product=x*y
        one=Q.const(Fraction(1,16))+x*Fraction(9,16)+y*Fraction(1,8)-product*Fraction(1,16)+a*Fraction(1,2)+z
        two=Q.const(Fraction(1,16))+y*Fraction(9,16)+x*Fraction(1,8)-product*Fraction(1,16)+a*Fraction(1,4)-z
        state=[one.unit(),two.unit()]
    x,y=state
    final=((x-Fraction(5,8)).square()+(y-Fraction(5,8)).square())*2
    final=final+(x-y).square()*Fraction(1,4)+(Fraction(1,2)-x-y).positive().square()*2
    result=running+final*beta**2
    down=np.asarray(result.lo//(1<<20),dtype=np.int64)
    up=np.asarray(-((-result.hi)//(1<<20)),dtype=np.int64)
    if np.any(down>up):raise AssertionError('Reversed integer enclosure')
    return down,up,amb

def independent_support(a,b):
    """Separate exhaustive rational cell test, independent of vectorized mask."""
    grid=math.lcm(a['n'],b['n'])
    def value(p,t,i,j):return int(p['actions'][t,i*p['n']//grid,j*p['n']//grid])
    if all(value(a,t,i,j)==value(b,t,i,j) for t in (0,1) for i in range(grid) for j in range(grid)):return Fraction(0)
    delta=Fraction(0);bound=Fraction(0);beta=Fraction(15,16)
    for t in (0,1):
        largest=0
        for i,j in np.ndindex(a['n'],a['n']):
            for k,l in np.ndindex(b['n'],b['n']):
                distance=max(Fraction(0),Fraction(i,a['n'])-Fraction(k+1,b['n']),Fraction(k,b['n'])-Fraction(i+1,a['n']))
                distance+=max(Fraction(0),Fraction(j,a['n'])-Fraction(l+1,b['n']),Fraction(l,b['n'])-Fraction(j+1,a['n']))
                if distance<=delta:largest=max(largest,abs(int(a['actions'][t,i,j])-int(b['actions'][t,k,l])))
        step=Fraction(largest,4096)
        bound+=beta**t*(4*delta+Fraction(13,16)*step)
        delta=min(Fraction(2),Fraction(11,16)*delta+Fraction(3,4)*step)
    bound+=beta**2*5*delta
    H=Fraction(87,64)*(1+beta)+beta**2*Fraction(33,16)
    return min(H,bound)

def point(policy,coordinates):
    """Exact Fraction trajectory for boundary and independently chosen fixtures."""
    x=list(map(Fraction,coordinates[:2]));total=Fraction(0);beta=Fraction(15,16)
    for t in (0,1):
        n=policy['n'];i,j=[max(0,min(n-1,math.floor(v*n))) for v in x];a=Fraction(int(policy['actions'][t,i,j]),4096)
        total+=beta**t*(sum((v-Fraction(5,8))**2 for v in x)+(x[0]-x[1])**2/4+2*max(Fraction(0),Fraction(1,2)-sum(x))**2+a*a+4*a**4)
        z=Fraction(coordinates[2+t]);x=[Fraction(1,16)+x[q]/2+x[1-q]/8+x[q]*(1-x[1-q])/16+(Fraction(1,2) if q==0 else Fraction(1,4))*a+(z if q==0 else -z) for q in (0,1)]
    return total+beta**2*(2*sum((v-Fraction(5,8))**2 for v in x)+(x[0]-x[1])**2/4+2*max(Fraction(0),Fraction(1,2)-sum(x))**2)
