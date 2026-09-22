"""Cutting-plane search for a wealth-sensitive polynomial supersolution.
Linear programs generate candidates; independent continuous residual validation
is indispensable. No LP result alone is labeled a certificate.
"""
from __future__ import annotations
import pathlib,json,time,argparse
import numpy as np
from scipy.special import comb
from scipy.optimize import linprog
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'revisions/2026-09-22-r9/results'
UL=1.5;UW=1.1;XL=.5;XW=1.5

def basis(z,n,order=0):
 z=np.asarray(z);B=np.array([comb(n-order,i)*z**i*(1-z)**(n-order-i) for i in range(n-order+1)]).T
 if order==0:return B
 fac=np.prod(np.arange(n-order+1,n+1));D=np.zeros((len(z),n+1))
 for i in range(n+1):
  for j in range(order+1):
   idx=i-j
   if 0<=idx<=n-order:D[:,i]+=fac*(-1)**(order-j)*comb(order,j)*B[:,idx]
 return D

def design(h,u,x,deg):
 dh,du,dx=deg;bH=basis(h,dh);bU=basis((u-UL)/UW,du);bX=basis((x-XL)/XW,dx)
 def outer(a,b,c):return np.einsum('ni,nj,nk->nijk',a,b,c).reshape(len(h),-1)
 M={};M['f']=h[:,None]*outer(bH,bU,bX)
 M['fh']=outer(bH+h[:,None]*basis(h,dh,1),bU,bX)
 M['fu']=h[:,None]*outer(bH,basis((u-UL)/UW,du,1)/UW,bX)
 M['fx']=h[:,None]*outer(bH,bU,basis((x-XL)/XW,dx,1)/XW)
 M['fuu']=h[:,None]*outer(bH,basis((u-UL)/UW,du,2)/UW**2,bX)
 M['fxx']=h[:,None]*outer(bH,bU,basis((x-XL)/XW,dx,2)/XW**2)
 M['fux']=h[:,None]*outer(bH,basis((u-UL)/UW,du,1)/UW,basis((x-XL)/XW,dx,1)/XW)
 return M

def selector(M,coef,u,x,k):
 vu=M['fu']@coef-.04*(u-2);vx=M['fx']@coef+.1/x
 vxx=M['fxx']@coef-.1/x**2;vux=M['fux']@coef
 c=np.where(vx>0,np.exp(-np.log(np.maximum(vx,1e-200))/u),.8);c=np.clip(c,.05,.8)
 th=np.clip(vu/k,-.2,.2);b=.06*x*vx-.0025*x*vux;dd=.04*x*x*vxx
 pvertex=np.clip(-b/np.minimum(dd,-1e-200),-.5,.8)
 ep1=b*(-.5)+.5*dd*.25;ep2=b*.8+.5*dd*.64
 p=np.where(dd<0,pvertex,np.where(ep1>=ep2,-.5,.8))
 return c,th,p

def constraint(M,u,x,c,th,p,k):
 Q=-M['fh']+.00125*M['fuu']-.04*M['f']+th[:,None]*M['fu']
 Q+=((.02+.06*p)*x-c)[:,None]*M['fx']+.02*((p*x)**2)[:,None]*M['fxx']-.0025*(p*x)[:,None]*M['fux']
 rg=c**(1-u)/(1-u)-.5*k*th**2-.04*(u-2)*th+.00195+.006*p-.002*p*p-.1*c/x+.0008*(u-2)**2-.004*np.log(x)
 return Q,-rg

def run(k=2,deg=(4,5,12),mesh=(9,10,24),iterations=25):
 start=time.perf_counter();axes=[(1-np.cos(np.linspace(0,np.pi,n)))/2 for n in mesh]
 H,U,X=np.meshgrid(axes[0],UL+UW*axes[1],XL+XW*axes[2],indexing='ij');h,u,x=H.ravel(),U.ravel(),X.ravel();M=design(h,u,x,deg)
 m=np.prod(np.array(deg)+1);coef=np.full(m,-2.);Qs=[];bs=[];history=[]
 shape=np.array(deg)+1;rows=[]
 for ih in range(shape[0]):
  for iu in range(shape[1]):
   for ix in range(shape[2]-1):
    row=np.zeros(m);row[np.ravel_multi_index((ih,iu,ix),shape)]=1;row[np.ravel_multi_index((ih,iu,ix+1),shape)]=-1;rows.append(row)
   for ix in range(shape[2]-2):
    row=np.zeros(m)
    for jj,vv in enumerate([1,-2,1]):row[np.ravel_multi_index((ih,iu,ix+jj),shape)]=vv
    rows.append(row)
 Qs.append(np.array(rows));bs.append(np.zeros(len(rows)))
 objective=design(np.array([1.]),np.array([2.]),np.array([1.25]),deg)['f'][0]+1e-5/m
 for it in range(iterations):
  c,th,p=selector(M,coef,u,x,k);Q,b=constraint(M,u,x,c,th,p,k);res=Q@coef-b
  idx=np.arange(len(h)) if it==0 else np.where(res>5e-7)[0]
  if len(idx)==0:break
  Qs.append(Q[idx]);bs.append(b[idx]);sol=linprog(objective,A_ub=np.vstack(Qs),b_ub=np.concatenate(bs),bounds=[(-8,0)]*m,method='highs',options={'dual_feasibility_tolerance':1e-8,'primal_feasibility_tolerance':1e-8})
  if not sol.success:raise RuntimeError(sol.message)
  coef=np.clip(sol.x,-8,0)
  c,th,p=selector(M,coef,u,x,k);Q,b=constraint(M,u,x,c,th,p,k);res=Q@coef-b
  hist={'iteration':it,'candidate_upper_no_residual':float(objective@coef+.1*np.log(1.25)),'max_collocation_residual':float(res.max()),'cuts':sum(len(v) for v in bs),'seconds':time.perf_counter()-start};history.append(hist);print(hist,flush=True);np.save(OUT/f'wealth_shaped_coeff_k{k:g}.npy',coef)
 out={'k':k,'degrees':deg,'mesh':mesh,'coefficients':coef.reshape(*(np.array(deg)+1)).tolist(),'history':history,'fit_seconds':time.perf_counter()-start,'scope':'candidate only; NOT yet a certificate'}
 (OUT/f'wealth_upper_shaped_k{k:g}.json').write_text(json.dumps(out,indent=2)+'\n')
 # Independent dense diagnostic, still not a bound.
 worst=-np.inf
 for hh in np.linspace(0,1,31):
  U,X=np.meshgrid(np.linspace(UL,UL+UW,51),np.linspace(XL,XL+XW,101),indexing='ij');u=U.ravel();x=X.ravel();h=np.full_like(u,hh);D=design(h,u,x,deg)
  c,th,p=selector(D,coef,u,x,k);Q,b=constraint(D,u,x,c,th,p,k);worst=max(worst,float((Q@coef-b).max()))
 print('DENSE DIAGNOSTIC',worst,flush=True)
 out['dense_residual_diagnostic']=worst;(OUT/f'wealth_upper_shaped_k{k:g}.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--k',type=float,default=2);a=ap.parse_args();run(a.k)
