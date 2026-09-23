"""Proposal objective only; directed acceptance is implemented in run_study.py."""
from pathlib import Path
import torch,numpy as np,time,json
from torch import nn
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss

torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
class Actor(nn.Module):
 def __init__(self):
  super().__init__();self.net=nn.Sequential(nn.Linear(1,16),nn.Tanh(),nn.Linear(16,16),nn.Tanh(),nn.Linear(16,3))
  with torch.no_grad():self.net[-1].weight.mul_(.1);self.net[-1].bias[:]=torch.tensor([0.,-1.,-1.])
 def forward(self,t):return self.net(t)
def setup(u0=2.,x0=1.25,n=16):
 tg,tw=leggauss(8);z,zw=hermgauss(16);z=torch.tensor(z*np.sqrt(2));zw=torch.tensor(zw/np.sqrt(np.pi))
 t=torch.tensor((np.arange(n)[:,None]+(tg+1)/2)/n);w=torch.tensor(tw/(2*n));ed=torch.arange(n)/n
 tt=t[:,:,None];root=torch.sqrt(tt);lp=-.025*tt+.3*root*z; lq=.065*tt+.3*root*z
 disc=torch.exp(-.02*t)*w
 Qr=(1-np.exp(-.02))/.02;budget=x0-(.50001)*np.exp(-.02)
 def obj(net,details=False):
  h=net((2*(torch.arange(n)+.5)/n-1).reshape(n,1));b=.3*h[:,0,None,None];s=(.1+6.4*torch.sigmoid(h[:,1]))[:,None,None];th=.2*torch.sigmoid(h[:,2])
  L=b-s*lq
  with torch.no_grad():
   lo=-10.;hi=10.
   for _ in range(45):
    mid=(lo+hi)/2;val=((.5+.3*torch.sigmoid(L+mid))*zw).sum(-1);q=(val*disc).sum()
    if q>budget:hi=mid
    else:lo=mid
   offset=(lo+hi)/2
  sig=torch.sigmoid(L+offset);q=((.5+.3*sig)*zw).sum(-1).mul(disc).sum();dq=((.3*sig*(1-sig))*zw).sum(-1).mul(disc).sum()
  offset=offset+(budget-q)/dq.detach()
  c=.5+.3*torch.sigmoid(b-s*lp+offset)
  mean=u0+(torch.cumsum(th,0)-th)[:,None]/n+th[:,None]*(t-ed[:,None]);U=mean[:,:,None,None]+.05*torch.sqrt(t)[:,:,None,None]*(.25*z[None,None,:,None]+np.sqrt(.9375)*z[None,None,None,:])
  f=-torch.exp(-(U-1)*torch.log(c[:,:,:,None]))/(U-1)
  flow=(f*zw[None,None,:,None]*zw[None,None,None,:]).sum((-1,-2))-th[:,None]**2
  payoff=(torch.exp(-.04*t)*flow*w).sum()+np.exp(-.04)*(-.02*((u0-2+th.mean())**2+.0025)+.1*np.log(.50001))
  if details:return {'b':(b[:,0,0]+offset).detach().tolist(),'s':s[:,0,0].detach().tolist(),'theta':th.detach().tolist(),'u0':u0,'x0':x0,'approx_value':float(payoff.detach()),'approx_budget':float(q.detach()),'n':n,'reserve':.50001}
  return payoff
 return obj
