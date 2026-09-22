import numpy as np,json,pathlib
from scipy.optimize import minimize,minimize_scalar
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss
import torch
torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
n=16;zg,zw=hermgauss(40);tg,tw=leggauss(12)
t=(np.arange(n)[:,None]+(tg[None,:]+1)/2)/n;w=np.broadcast_to(tw[None,:]/(2*n),t.shape)*np.exp(-.04*t)
A=np.maximum(0,np.minimum(t.ravel()[:,None]-np.arange(n)[None,:]/n,1/n))
AT=torch.tensor(A);TT=torch.tensor(t.ravel()[:,None]);WW=torch.tensor(w.ravel()[:,None]*zw[None,:]/np.sqrt(np.pi));ZZ=torch.tensor(zg[None,:]*np.sqrt(2))
root=pathlib.Path(__file__).resolve().parents[3]
for k in [.5,2,8]:
 start=np.array(json.load(open(root/f'revisions/2026-09-22-r9/results/actor_k{k:g}.json'))['theta'])
 def solve(lamy,verbose=False):
  l=np.log(lamy)-.025*TT-.3*torch.sqrt(TT)*ZZ;y=torch.exp(l)
  def fun(th,jac=True):
   th=torch.tensor(th,requires_grad=True);m=2+AT@th;m=m[:,None]
   c=torch.clamp(torch.exp(-l/m),.05,.8);E=c**(1-m);psi=E/(1-m)-y*c
   val=((psi+.01*y-.004*np.log(.5)-.5*k*th.repeat_interleave(12)[:,None]**2)*WW).sum()-.02*np.exp(-.04)*(th.sum()/n)**2
   gr=torch.autograd.grad(-val,th)[0]
   return float(-val.detach()),gr.detach().numpy()
  opt=minimize(fun,start,jac=True,bounds=[(0,.2)]*n,method='L-BFGS-B',options={'ftol':1e-13,'gtol':1e-10,'maxiter':200})
  th=np.clip(opt.x,0,np.nextafter(.2,-np.inf));m=2+A@th;L=np.clip(l.numpy()/m[:,None],-np.log(.8),-np.log(.05));E=np.exp(L*(m[:,None]-1))
  beta=E*(1-L*(m[:,None]-1))/(m[:,None]-1)**2
  bl=-np.exp(l.numpy()-L)*L/m[:,None]*((l.numpy()/m[:,None]>=-np.log(.8))&(l.numpy()/m[:,None]<=-np.log(.05)))
  cov=(w.ravel()*.00375*t.ravel()*(bl@(zw/np.sqrt(np.pi)))).sum()
  val=lamy*.75+.1*np.log(.5)-opt.fun+cov
  if verbose:return {'k':k,'y0':lamy,'theta':th.tolist(),'objective_pilot':val,'covariance_correction':cov,'max_E_beta_l_sq':float(((bl**2)@(zw/np.sqrt(np.pi))).max()),'theta_solve_success':bool(opt.success)}
  return val
 opty=minimize_scalar(solve,bounds=(1.2,2.4),method='bounded',options={'xatol':1e-9})
 out=solve(opty.x,True);print(json.dumps(out),flush=True)
 (root/f'revisions/2026-09-22-r10/results/dual_pilot_k{k:g}.json').write_text(json.dumps(out,indent=2))
