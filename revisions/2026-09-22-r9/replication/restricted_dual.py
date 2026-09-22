"""Validated market-deflator upper witness for the NO-ADJUSTMENT economy.
Portfolio and consumption remain fully adaptive and continuously valued.
A bounded-source Feynman--Kac potential is integrated by outward weighted
Taylor boxes; a scalar log-deflator augments, rather than alters, the economy.
"""
from __future__ import annotations
import json,pathlib,time,math
import numpy as np
from bernstein import I,iv,bounds
from original_policy_certificate import point,around,plus,minus,times,sum_out
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'revisions/2026-09-22-r9/results'
DN=-np.inf;UP=np.inf

def const(s):return around(I(s))
def divide(a,b):
 assert np.all(b[...,0]>0)
 inv=np.stack([np.nextafter(1/b[...,1],DN),np.nextafter(1/b[...,0],UP)],-1)
 return times(a,inv)
def exponential(x):
 assert np.all(x[...,0]>=-3) and np.all(x[...,1]<=3)
 a=point(np.zeros(x.shape[:-1]))
 for j in range(40,-1,-1):a=plus(times(a,x),around(I(1)/math.factorial(j)))
 err=bounds(iv.exp(I(3))*I(3)**41/math.factorial(41))[1]
 return plus(a,np.array([-err,err]))
def absbound(x):return np.maximum(abs(x[...,0]),abs(x[...,1]))
def clamp(x,low,high):
 return np.stack([np.minimum(np.maximum(x[...,0],low[0]),high[0]),np.minimum(np.maximum(x[...,1],low[1]),high[1])],-1)

def source_jet(v,z1,z2,hessian=False):
 A=plus(times(const('-.0125'),z1),times(around(I('.05')*iv.sqrt(I('.9375'))),z2))
 u=plus(const(2),times(v,A))
 ell=minus(minus(around(iv.ln(I('1.55'))),times(const('.025'),times(v,v))),times(const('.3'),times(v,z1)))
 y=exponential(ell);um=minus(u,const(1));q=divide(ell,u)
 Lmin=around(-iv.ln(I('.8')));Lmax=around(-iv.ln(I('.05')))
 L=clamp(q,Lmin,Lmax);c=exponential(-L[...,::-1]);yc=times(y,c);E=exponential(times(L,um))
 lu=times(L,um);one=point(np.ones(v.shape[:-1]))
 Uu=divide(times(E,minus(one,lu)),times(um,um))
 exactC=I('-.00005')-I('.004')*iv.ln(I('.5'))
 S=minus(-divide(E,um)[...,::-1],yc)
 S=plus(S,plus(times(const('.01'),y),around(exactC)))
 S=plus(S,times(const('.0008'),times(minus(u,const(2)),minus(u,const(2)))))
 Su=plus(Uu,times(const('.0016'),minus(u,const(2))));Sl=plus(-yc[...,::-1],times(const('.01'),y))
 uv=A;lv=minus(times(const('-.05'),v),times(const('.3'),z1))
 uz1=times(const('-.0125'),v);lz1=times(const('-.3'),v);uz2=times(around(I('.05')*iv.sqrt(I('.9375'))),v)
 deriv=[plus(times(Su,uv),times(Sl,lv)),plus(times(Su,uz1),times(Sl,lz1)),times(Su,uz2)]
 if not hessian:return S,deriv
 chi=np.stack([(q[...,0]>Lmin[1])&(q[...,1]<Lmax[0]),(q[...,1]>=Lmin[0])&(q[...,0]<=Lmax[1])],-1).astype(float)
 # U_uu=-E*((L*(u-1)-1)^2+1)/(u-1)^3; square interval can be conservative.
 lminus=minus(lu,one)
 Uuu=-divide(times(E,plus(times(lminus,lminus),one)),times(times(um,um),um))[...,::-1]
 Huu=plus(plus(Uuu,times(chi,divide(times(yc,times(L,L)),u))),const('.0016'))
 Hul=-times(chi,divide(times(yc,L),u))[...,::-1]
 Hll=plus(plus(-yc[...,::-1],times(chi,divide(yc,u))),times(const('.01'),y))
 zero=point(np.zeros(v.shape[:-1]));du=[uv,uz1,uz2];dl=[lv,lz1,zero];H={}
 for i in range(3):
  for j in range(i,3):
   h=plus(plus(times(Huu,times(du[i],du[j])),times(Hul,plus(times(du[i],dl[j]),times(dl[i],du[j])))),times(Hll,times(dl[i],dl[j])))
   if i==0 and j==0:h=plus(h,times(Sl,const('-.05')))
   if i==0 and j==1:h=plus(h,plus(times(Su,const('-.0125')),times(Sl,const('-.3'))))
   if i==0 and j==2:h=plus(h,times(Su,around(I('.05')*iv.sqrt(I('.9375')))))
   H[i,j]=absbound(h)
 return H

def weighted_moments(n,gaussian):
 """Outward exact-polynomial antiderivatives plus analytic series remainders."""
 ans=[];R=I(6)
 for j in range(n):
  a=-R+2*R*j/n if gaussian else I(j)/n
  b=-R+2*R*(j+1)/n if gaussian else I(j+1)/n
  center=(a+b)/2;raw=[]
  for m in range(3):
   s=I(0)
   for k in range(111 if gaussian else 13):
    power=2*k+m+(1 if gaussian else 2)
    coef=(-I('.5'))**k/math.factorial(k) if gaussian else 2*(-I('.04'))**k/math.factorial(k)
    s+=coef*(b**power-a**power)/power
   if gaussian:
    err=(b-a)*R**m*iv.exp(R*R/2)*(R*R/2)**111/math.factorial(111)
    s=(s+iv.mpf([-err.b,err.b]))/iv.sqrt(2*iv.pi)
   else:
    err=2*(b-a)*iv.exp(I('.04'))*I('.04')**13/math.factorial(13)
    s+=iv.mpf([-err.b,err.b])
   raw.append(s)
  mm=[raw[0],raw[1]-center*raw[0],raw[2]-2*center*raw[1]+center**2*raw[0]]
  row=np.array([bounds(x) for x in mm]);row[0,0]=max(0,row[0,0]);row[2,0]=max(0,row[2,0]);ans.append(row)
 return np.array(ans)

def run(resolutions=((16,32),(32,64),(64,128))):
 # The source bounds hold throughout u in[1.5,2.6], y in[.2,12].
 source_floor=-2/iv.sqrt(I('.35'))-I('4.2')
 source_ceiling=I('.8')**(-I('1.6'))/(-I('1.6'))+I('.12')+I('.0033')
 assert bounds(source_floor)[0]>-8 and bounds(source_ceiling)[1]<0
 z_u=8*(iv.exp(-I(50))+iv.exp(-I(72)))
 z_y=8*(iv.exp(-22*iv.ln(I('1.55')/I('.2'))+I('22.33'))+iv.exp(-22*iv.ln(I(12)/I('1.55'))+I('22.33')))
 base=I('1.55')*I('.75')+I('.1')*iv.ln(I('.5'))
 tail=4*iv.exp(-I(18));C=(1-iv.exp(-I('.04')))/I('.04');tailerr=8*C*tail
 rows=[]
 for nv,nz in resolutions:
  start=time.perf_counter();mv=weighted_moments(nv,False);mz=weighted_moments(nz,True)
  grid=np.meshgrid(np.arange(nv),np.arange(nz),np.arange(nz),indexing='ij');ids=[x.ravel() for x in grid]
  vc=(ids[0]+.5)/nv;z1c=-6+12*(ids[1]+.5)/nz;z2c=-6+12*(ids[2]+.5)/nz
  v=point(vc);z1=point(z1c);z2=point(z2c);S,g=source_jet(v,z1,z2)
  M=[mv[ids[0]],mz[ids[1]],mz[ids[2]]]
  mass=times(times(M[0][:,0],M[1][:,0]),M[2][:,0]);integ=times(S,mass)
  for i in range(3):
   w=M[i][:,1]
   for j in range(3):
    if i!=j:w=times(w,M[j][:,0])
   integ=plus(integ,times(g[i],w))
  radii=[.5/nv,6/nz,6/nz]
  V=np.stack([vc-radii[0],vc+radii[0]],-1);Z1=np.stack([z1c-radii[1],z1c+radii[1]],-1);Z2=np.stack([z2c-radii[2],z2c+radii[2]],-1)
  Hess=source_jet(V,Z1,Z2,True);error=point(np.zeros(len(vc)))
  for i in range(3):
   for j in range(i,3):
    if i==j:
     weight=M[i][:,2]
     for l in range(3):
      if i!=l:weight=times(weight,M[l][:,0])
     weight=times(const('.5'),weight)
    else:weight=times(point(radii[i]*radii[j]),mass)
    error=plus(error,times(point(Hess[i,j]),weight))
  integral=sum_out(integ);remainder=sum_out(error)[1];integral=plus(integral,np.array([-remainder,remainder]))
  total=plus(integral,around(base+z_u+z_y));total=plus(total,np.array([-bounds(tailerr)[1],0.]))
  row={'time_sqrt_cells':nv,'normal_cells_per_dimension':nz,'weighted_boxes':len(vc),'dual_value_interval':total.tolist(),'restricted_optimal_value_upper':float(total[1]),'width':float(np.nextafter(total[1]-total[0],UP)),
   'taylor_remainder_upper':float(remainder),'seconds':time.perf_counter()-start}
  rows.append(row);print(row,flush=True)
 result={'initial':[0,2,1.25],'lambda':1.55,'auxiliary_preference_domain':[1.5,2.6],'auxiliary_deflator_domain':[.2,12],
  'records':rows,'source_floor_lower':bounds(source_floor)[0],'source_ceiling_upper':bounds(source_ceiling)[1],
  'localization_upper':bounds(z_u+z_y)[1],'gaussian_tail_correction_upper':bounds(tailerr)[1],
  'scope':'Upper bound on the optimum over ALL adaptive original consumption/portfolio policies with theta=0; unchanged original payoff and exit contract',
  'arithmetic':'70-digit interval constants and weighted moments; outward binary64 Taylor boxes; exp degree40 with analytic remainder',
  'not_a_policy_value':'The dual-value interval encloses a supersolution at the initial state; only its upper endpoint bounds the restricted optimum.'}
 (OUT/'restricted_dual_certificate.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':run()
