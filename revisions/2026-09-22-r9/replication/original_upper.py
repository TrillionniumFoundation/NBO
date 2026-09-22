"""Fit, then independently certify a reduced original-payoff upper witness.
The fitting solver is never trusted as a certificate. All continuous controls,
wealth states, stopping costs, and artificial preference exits are accounted for.
"""
from __future__ import annotations
import pathlib,time,json,argparse,sys
import numpy as np
from numpy.polynomial import chebyshev as C
from scipy.interpolate import RegularGridInterpolator
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'revisions/2026-09-22-r9/results'
UL=1.5; UH=2.6

def flow(u):return .8**(1-u)/(1-u)
def ham(q,k):
 a=np.clip(q/k,-.2,.2);return q*a-k*a*a/2

def fit(k,dh=12,du=14):
 start=time.perf_counter()
 # An enlarged-domain method-of-lines calculation supplies an initializer only.
 ug=np.linspace(1.25,3.25,1201);dx=ug[1]-ug[0];hstep=1/8000
 src=flow(ug)+.0008*(ug-2)**2-.03730258872223978
 def rhs(v):
  vu=np.gradient(v,dx,edge_order=2);vuu=np.gradient(vu,dx,edge_order=2)
  return .00125*vuu+ham(vu-.04*(ug-2),k)-.04*v+src
 v=np.zeros_like(ug);vstore=[v.copy()]
 for it in range(8000):
  a=rhs(v);b=rhs(v+.5*hstep*a);cc=rhs(v+.5*hstep*b);d=rhs(v+hstep*cc)
  v=v+hstep*(a+2*b+2*cc+d)/6
  if (it+1)%20==0:vstore.append(v.copy())
 interp=RegularGridInterpolator((np.linspace(0,1,401),ug),np.array(vstore))
 hs=(1+np.cos(np.linspace(np.pi,0,2*dh+9)))/2
 us=UL+(UH-UL)*(1+np.cos(np.linspace(np.pi,0,2*du+11)))/2
 H,U=np.meshgrid(hs,us,indexing='ij');h=H.ravel();u=U.ravel()
 z=2*h-1;y=2*(u-UL)/(UH-UL)-1
 B0=C.chebvander2d(z,y,[dh,du]).reshape(len(h),-1)
 B=h[:,None]*B0
 target=interp(np.c_[h,u]);Fover=np.where(h>0,target/np.maximum(h,1e-99),flow(u)+.0008*(u-2)**2-.03730258872223978+ham(-.04*(u-2),k))
 coef=np.linalg.lstsq(B0,Fover,rcond=1e-12)[0]
 # Residual minimization, with analytic derivative of the complete clipped selector.
 Bh=np.empty_like(B);Bu=np.empty_like(B);Buu=np.empty_like(B)
 for j in range(B.shape[1]):
  cc=np.zeros((dh+1,du+1));cc.flat[j]=1.
  Bh[:,j]=C.chebval2d(z,y,cc)+2*h*C.chebval2d(z,y,C.chebder(cc,axis=0))
  Bu[:,j]=h*2/(UH-UL)*C.chebval2d(z,y,C.chebder(cc,axis=1))
  Buu[:,j]=h*(2/(UH-UL))**2*C.chebval2d(z,y,C.chebder(cc,m=2,axis=1))
 history=[]
 for step in range(8):
  q=Bu@coef-.04*(u-2)
  res=(-Bh+.00125*Buu-.04*B)@coef+ham(q,k)+flow(u)+.0008*(u-2)**2-.03730258872223978
  jac=-Bh+.00125*Buu-.04*B+np.clip(q/k,-.2,.2)[:,None]*Bu
  dc=np.linalg.lstsq(jac,-res,rcond=1e-12)[0];coef+=dc
  history.append({'step':step,'max_abs_collocation_residual':float(abs(res).max())})
 payload={'k':k,'degrees':[dh,du],'representation':'F(h,u)=h*Chebyshev(2h-1,2(u-1.5)/1.1-1)','coefficients':coef.reshape(dh+1,du+1).tolist(),'fit_seconds':time.perf_counter()-start,'collocation_history':history,'scope':'fitted initializer; verification is separate'}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/f'upper_k{k:g}.json').write_text(json.dumps(payload,indent=2)+'\n')
 print(k,payload['fit_seconds'],history[-1],flush=True)
 return payload
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--k',type=float,default=2);ap.add_argument('--dh',type=int,default=12);ap.add_argument('--du',type=int,default=14);ar=ap.parse_args();fit(ar.k,ar.dh,ar.du)
