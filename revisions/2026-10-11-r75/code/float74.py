"""Production binary64 outward whole-bin path integration; no point replacement."""
import numpy as np
from common74 import BIN_BITS

class I:
    def __init__(self,lo,hi=None):
        self.lo=np.asarray(lo,dtype=float);self.hi=np.asarray(lo if hi is None else hi,dtype=float)
    @staticmethod
    def cast(x):return x if isinstance(x,I) else I(x)
    def __add__(self,x):
        x=I.cast(x);return I(np.nextafter(self.lo+x.lo,-np.inf),np.nextafter(self.hi+x.hi,np.inf))
    __radd__=__add__
    def __sub__(self,x):
        x=I.cast(x);return I(np.nextafter(self.lo-x.hi,-np.inf),np.nextafter(self.hi-x.lo,np.inf))
    def __rsub__(self,x):return I.cast(x)-self
    def __mul__(self,x):
        x=I.cast(x);v=[self.lo*x.lo,self.lo*x.hi,self.hi*x.lo,self.hi*x.hi]
        return I(np.nextafter(np.minimum.reduce(v),-np.inf),np.nextafter(np.maximum.reduce(v),np.inf))
    __rmul__=__mul__
    def sq(self):
        low=np.where((self.lo<=0)&(self.hi>=0),0,np.minimum(self.lo*self.lo,self.hi*self.hi))
        high=np.maximum(self.lo*self.lo,self.hi*self.hi)
        return I(np.maximum(0,np.nextafter(low,-np.inf)),np.nextafter(high,np.inf))
    def pos(self):return I(np.maximum(0,self.lo),np.maximum(0,self.hi))
    def unit(self):return I(np.maximum(0,self.lo),np.minimum(1,self.hi))

def actor(policy,t,x):
    n=policy['n'];tab=policy['actions'][t]
    ll=[np.clip(np.floor(z.lo*n).astype(int),0,n-1) for z in x];uu=[np.clip(np.floor(z.hi*n).astype(int),0,n-1) for z in x]
    low=tab[ll[0],ll[1]].astype(float).copy();high=low.copy()
    amb=(ll[0]!=uu[0])|(ll[1]!=uu[1])
    for k in np.flatnonzero(amb):
        box=tab[ll[0][k]:uu[0][k]+1,ll[1][k]:uu[1][k]+1];low[k]=box.min();high[k]=box.max()
    return I(low/4096,high/4096),int(amb.sum())

def c(x,a):
    state=(x[0]-5/8).sq()+(x[1]-5/8).sq()
    return state+(x[0]-x[1]).sq()*(1/4)+(1/2-x[0]-x[1]).pos().sq()*2+a.sq()+a.sq().sq()*4

def terminal(x):return ((x[0]-5/8).sq()+(x[1]-5/8).sq())*2+(x[0]-x[1]).sq()*(1/4)+(1/2-x[0]-x[1]).pos().sq()*2

def path(policy,bins):
    bins=np.asarray(bins,dtype=np.uint64);den=1<<BIN_BITS
    x=[I(bins[:,j].astype(float)/den,(bins[:,j].astype(float)+1)/den) for j in range(2)]
    total=I(np.zeros(len(bins)));amb=[]
    for t in range(2):
        a,k=actor(policy,t,x);amb.append(k);total=total+c(x,a)*(15/16)**t
        j=bins[:,2+t].astype(float);z=I((j-den/2)/(den*16),(j+1-den/2)/(den*16))
        y=[]
        for q in range(2):
            drift=1/16+x[q]*(1/2)+x[1-q]*(1/8)+x[q]*(1-x[1-q])*(1/16)+a*(1/2 if q==0 else 1/4)
            y.append((drift+(z if q==0 else z*(-1))).unit())
        x=y
    total=total+terminal(x)*(15/16)**2
    assert np.isfinite(total.lo).all() and np.isfinite(total.hi).all() and np.all(total.lo<=total.hi)
    return total.lo,total.hi,amb
