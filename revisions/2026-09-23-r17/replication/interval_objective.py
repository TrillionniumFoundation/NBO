"""Differentiable interval surrogate; NEVER a rounding certificate.
All arithmetic here is ordinary torch.float64 and is used only for proposals.
The separately imported MPFR checker makes every acceptance decision.
"""
from __future__ import annotations
import torch
from torch import nn
class I:
    def __init__(self,lo,hi=None):
        self.lo=torch.as_tensor(lo);self.hi=self.lo if hi is None else torch.as_tensor(hi)
    def __add__(self,b):
        b=as_i(b);return I(self.lo+b.lo,self.hi+b.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,b):return self+-as_i(b)
    def __rsub__(self,b):return as_i(b)+-self
    def __mul__(self,b):
        b=as_i(b);v=torch.stack(torch.broadcast_tensors(self.lo*b.lo,self.lo*b.hi,self.hi*b.lo,self.hi*b.hi));return I(v.amin(0),v.amax(0))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=as_i(b)
        if torch.any((b.lo<=0)&(b.hi>=0)):raise ArithmeticError('Division through zero')
        return self*I(1/b.hi,1/b.lo)
    def __rtruediv__(self,b):return as_i(b)/self
    def square(self):
        l=torch.minimum(self.lo.square(),self.hi.square());return I(torch.where((self.lo<=0)&(self.hi>=0),0,l),torch.maximum(self.lo.square(),self.hi.square()))
    def __getitem__(self,k):return I(self.lo[k],self.hi[k])
    def maxabs(self):return torch.maximum(self.lo.abs(),self.hi.abs())
def as_i(x):return x if isinstance(x,I) else I(x)
def exp(x):x=as_i(x);return I(x.lo.exp(),x.hi.exp())
def log(x):x=as_i(x);return I(x.lo.log(),x.hi.log())
def tanh(x):x=as_i(x);return I(x.lo.tanh(),x.hi.tanh())
def clip(x,l,h):return I(x.lo.clamp(l,h),x.hi.clamp(l,h))
def stack(x,dim=-1):return I(torch.stack([v.lo for v in x],dim),torch.stack([v.hi for v in x],dim))
def affine(x,w,b=None):
    m=(x.lo+x.hi)/2;r=(x.hi-x.lo)/2;c=m@w.T;d=r@w.abs().T
    if b is not None:c=c+b
    return I(c-d,c+d)
def network_value(s,net):
    z=stack([2*s[:,0]-1,(s[:,1]-2)/.8,(s[:,2]-1.25)/.75])
    for layer in net.layers:
        z=affine(z,layer.weight,layer.bias) if isinstance(layer,nn.Linear) else tanh(z)
    return z

def network_jet(s,net):
    n=len(s.lo);z=stack([2*s[:,0]-1,(s[:,1]-2)/.8,(s[:,2]-1.25)/.75]);zero=I(torch.zeros(n,3))
    row=lambda a:I(torch.tensor(a).expand(n,3))
    j=[z,row([2.,0,0]),row([0,1.25,0]),row([0,0,4/3]),zero,zero,zero]
    for layer in net.layers:
        if isinstance(layer,nn.Linear):
            a=affine(stack(j,dim=1),layer.weight);j=[a[:,k] for k in range(7)];j[0]=j[0]+I(layer.bias)
        else:
            v=tanh(j[0]);d=1-v.square();dd=-2*v*d
            j=[v,d*j[1],d*j[2],d*j[3],dd*j[2].square()+d*j[4],dd*j[2]*j[3]+d*j[5],dd*j[3].square()+d*j[6]]
    return [v[:,0] for v in j]

def product(a,b):
    v,t,u,x,uu,ux,xx=a;w,wt,wu,wx,wuu,wux,wxx=b
    return [v*w,t*w+v*wt,u*w+v*wu,x*w+v*wx,uu*w+2*u*wu+v*wuu,ux*w+u*wx+x*wu+v*wux,xx*w+2*x*wx+v*wxx]
def factor(s,axis,rate,origin):
    z=I(torch.zeros(len(s.lo)));e=exp(rate*(s[:,axis]-origin));j=[1-e,z,z,z,z,z,z];j[axis+1]=-rate*e
    j[4 if axis==1 else 6]=-rate**2*e
    return j
def critic_jet(s,net,all_faces=False):
    B=product(product(factor(s,1,-12,1.2),factor(s,1,12,2.8)),factor(s,2,-4,.5))
    if all_faces:B=product(B,factor(s,2,4,2))
    y,yt,yu,yx,yuu,yux,yxx=network_jet(s,net);z=log(1+exp(y));sig=1/(1+exp(-y));dd=sig*(1-sig)
    j=product(B,[z,sig*yt,sig*yu,sig*yx,dd*yu.square()+sig*yuu,dd*yu*yx+sig*yux,dd*yx.square()+sig*yxx]);j[0]=j[0]-8
    t,u,x=s[:,0],s[:,1],s[:,2];h=1-t;y,yt,yu,yx,yuu,yux,yxx=j
    return [-.02*(u-2).square()+.1*log(x)+h*y,-y+h*yt,-.04*(u-2)+h*yu,.1/x+h*yx,-.04+h*yuu,h*yux,-.1/x.square()+h*yxx]
def actions(s,actor,delta=2**-24):
    a=tanh(network_value(s,actor));d=I(-delta,delta)
    return [clip(.425+.375*a[:,0]+d,.05,.8),clip(.2*a[:,1]+d,-.2,.2),(2-s[:,2])/1.5*clip(.15+.65*a[:,2]+d,-.5,.8)]
def utility(c,u):return -exp((u-1)*(-log(c)))/(u-1)
def action_h(s,j,a):
    _,_,vu,vx,_,vux,vxx=j;x=s[:,2];u=s[:,1];c,th,p=a
    return utility(c,u)-th.square()+th*vu+(.06*p*x-c)*vx+.02*p.square()*x.square()*vxx-.0025*p*x*vux

def oracle(s,j):
    _,_,vu,vx,_,vux,vxx=j;x=s[:,2];u=s[:,1];ones=torch.ones_like(vx.lo)
    safe=I(vx.lo.clamp_min(1e-30),vx.hi.clamp_min(1e-30));cp=clip(exp(-log(safe)/u),.05,.8)
    pos=vx.lo>0;nonpos=vx.hi<=0
    c=I(torch.where(pos,cp.lo,torch.where(nonpos,.8*ones,.05*ones)),torch.where(pos,cp.hi,.8*ones))
    th=clip(vu/2,-.2,.2);hc=utility(c,u)-c*vx;ht=th*vu-th.square()
    h1=.06*x*vx-.0025*x*vux;h2=.04*x.square()*vxx
    hp=lambda p:h1*p+h2/2*p.square()
    a,b=hp(I(-.5)),hp(I(.8));pl=torch.maximum(a.lo,b.lo);ph=torch.maximum(a.hi,b.hi)
    conc=h2.hi<0
    safeh=I(torch.minimum(h2.lo,-1e-30*ones),torch.minimum(h2.hi,-1e-30*ones));p=clip(-h1/safeh,-.5,.8);vv=hp(p)
    pl=torch.where(conc,torch.maximum(pl,vv.lo),pl);ph=torch.where(conc,torch.maximum(ph,vv.hi),ph)
    unc=(h2.lo<0)&(h2.hi>=0);vr=hp(I(-.5,.8));ph=torch.where(unc,torch.maximum(ph,vr.hi),ph)
    return hc+ht+I(pl,ph)
def residuals(s,actor,critic,all_faces=False):
    j=critic_jet(s,critic,all_faces);a=actions(s,actor);common=j[1]+.02*s[:,2]*j[3]+.00125*j[4]-.04*j[0]
    return common+oracle(s,j),common+action_h(s,j,a)
def objective(s,actor,critic,nt=4,all_faces=False,temperature=.15):
    ru,rp=residuals(s,actor,critic,all_faces);ep=ru.hi.reshape(nt,-1);en=-rp.lo.reshape(nt,-1)
    # Include zero as an additional entry so the smooth maximum is nonnegative.
    zero=torch.zeros(nt,1);ep=torch.cat([ep,zero],1);en=torch.cat([en,zero],1)
    maxima=lambda a:temperature*torch.logsumexp(a/temperature,dim=1)
    mass=(torch.exp(-.04*torch.arange(nt)/nt)-torch.exp(-.04*(torch.arange(nt)+1)/nt))/.04
    return (mass*(maxima(ep)+maxima(en))).sum()
