"""Outward certificate for an affine-preference market-deflator upper bound.
All original continuous actions and the actual first-exit covenant are retained.
Fitting, quadrature, control-relaxation error, and outward arithmetic are separate.
"""
from __future__ import annotations
import argparse,json,pathlib,sys,time,math
from fractions import Fraction
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r9/replication'))
from bernstein import I,iv,bounds
from original_policy_certificate import point,around,plus,minus,times,sum_out
from restricted_dual import divide,exponential,absbound,clamp,weighted_moments
OUT=ROOT/'revisions/2026-09-22-r10/results';DN=-np.inf;UP=np.inf

def C(x):return around(I(x))
def neg(a):return -a[...,::-1]
def sq(a):
 b=times(a,a);b[...,0]=np.where((a[...,0]<=0)&(a[...,1]>=0),0,np.maximum(0,b[...,0]));return b

def source(u,l,hessian=False):
 """Source S0, preference derivative beta, and (u,log y) derivatives."""
 y=exponential(l);r=minus(u,C(1));q=divide(l,u)
 Lmin=around(-iv.ln(I('.8')));Lmax=around(-iv.ln(I('.05')))
 L=clamp(q,Lmin,Lmax);c=exponential(neg(L));yc=times(y,c);E=exponential(times(L,r));lr=times(L,r)
 beta=divide(times(E,minus(C(1),lr)),sq(r))
 S=plus(minus(neg(divide(E,r)),yc),plus(times(C('.01'),y),around(-I('.004')*iv.ln(I('.5')))))
 Sl=plus(neg(yc),times(C('.01'),y))
 chi=np.stack([(q[...,0]>Lmin[1])&(q[...,1]<Lmax[0]),(q[...,1]>=Lmin[0])&(q[...,0]<=Lmax[1])],-1).astype(float)
 Huu=plus(neg(divide(times(E,plus(sq(minus(lr,C(1))),C(1))),times(sq(r),r))),times(chi,divide(times(yc,sq(L)),u)))
 Hul=neg(times(chi,divide(times(yc,L),u)))
 Hll=plus(plus(neg(yc),times(chi,divide(yc,u))),times(C('.01'),y))
 return S,beta,Sl,Huu,Hul,Hll

def primitive_checks():
 # H_uu is increasing in log y on its interior branch: its derivative is
 # E*L*(2-L)/u^2 >= 0. The consumption-upper clipping jump is also upward.
 l12=around(iv.ln(I(12)))
 edges=np.linspace(1.5,2.3,1601);u=np.stack([np.nextafter(edges[:-1],DN),np.nextafter(edges[1:],UP)],-1)
 H=source(u,l12)[3];curvature=float(H[...,1].max());assert curvature<0
 edges=np.linspace(2.3,2.5,2001);u=np.stack([np.nextafter(edges[:-1],DN),np.nextafter(edges[1:],UP)],-1)
 beta=source(u,l12)[1];upper=float(beta[...,1].max());lower=float(source(C('2.2'),l12)[1][0]);assert upper<lower
 edges=np.linspace(2,2.2,1001);u=np.stack([np.nextafter(edges[:-1],DN),np.nextafter(edges[1:],UP)],-1)
 S,beta,*_=source(u,l12);bmax=source(u,around(iv.ln(I('.2'))))[1]
 floor=float(S[...,0].min());babs=float(max(absbound(beta).max(),absbound(bmax).max()));ceiling=float(source(u,around(iv.ln(I(".2"))))[0][...,1].max());assert floor>-7.1 and babs<1.1 and ceiling<0
 # The affine terminal tangent Q satisfies |Q(U)| <= .0068 in expectation
 # under theta=0, starting within [1.5,2.5], over at most one year.
 continuation_floor=I('-7.1')-I('1.1')*I('.75')-I('.04')*I('.0068');assert bounds(continuation_floor)[0]>-8
 out={'Huu_upper_u_1.5_to_2.3_at_y12':curvature,'beta_upper_u_2.3_to_2.5_at_y12':upper,
 'beta_lower_u_2.2_at_y12':lower,'source_floor':floor,'source_ceiling':ceiling,'beta_absolute_upper':babs,'continuation_source_floor':bounds(continuation_floor)[0],
 'supporting_plane_domain':{'u':[1.5,2.5],'m':[2,2.2],'y':[.2,12]},'supporting_plane_verified':True}
 (OUT/'tangent_primitive_checks.json').write_text(json.dumps(out,indent=2)+'\n');return out

def time_moments(a,b,center):
 raw=[]
 for m in range(3):
  s=I(0)
  for j in range(13):
   power=2*j+m+2;s+=2*(-I('.04'))**j/math.factorial(j)*(b**power-a**power)/power
  err=2*(b-a)*iv.exp(I('.04'))*I('.04')**13/math.factorial(13)
  raw.append(s+iv.mpf([-err.b,err.b]))
 mm=[raw[0],raw[1]-center*raw[0],raw[2]-2*center*raw[1]+center**2*raw[0]]
 out=np.array([bounds(v) for v in mm]);out[0,0]=max(0,out[0,0]);out[2,0]=max(0,out[2,0]);return out

def gap_at(q,theta,k):
 q=I(float(q));theta=I(float(theta));k=I(float(k));A=I('.2')
 if bounds(q-k*A)[0]>0:g=(A-theta)*(q-k*(A+theta)/2)
 elif bounds(q+k*A)[1]<0:g=(-A-theta)*(q-k*(-A+theta)/2)
 else:
  # The unconstrained quadratic conjugate is always an upper bound.
  g=(q-k*theta)**2/(2*k)
 return max(0,bounds(g)[1])

def run(k=2,resolutions=((4,64),(8,128),(16,256))):
 start=time.perf_counter();primitive=primitive_checks();fit=json.loads((OUT/f'dual_pilot_k{k:g}.json').read_text())
 y0=float(fit['y0']);theta=[float(v) for v in fit['theta']];n=len(theta)
 assert 1.2<y0<2.4 and all(Fraction(0)<=Fraction(v)<=Fraction(".2") for v in theta)
 mleft=[];mu=I(0)
 for th in theta:mleft.append(mu);mu+=I(th)/n
 terminal=iv.exp(-I('.04'))*(-I('.02')*mu**2);bT=-I('.04')*mu
 base=I(y0)*I('.75')+I('.1')*iv.ln(I('.5'))
 Z=16*iv.exp(-I(18))+8*(iv.exp(-22*iv.ln(I(y0)/I('.2'))+I('22.33'))+iv.exp(-22*iv.ln(I(12)/I(y0))+I('22.33')))
 a=I(12)/11;M=iv.ln(I(y0));var=I('.09')
 D2=iv.exp(a*M+a*a*var/2)*((M+a*var)**2+var)/16
 variance=I('.09')*D2/(24*I(k))
 tail=2*iv.exp(-I(18));tail_source=-I('7.1')*tail*(1-iv.exp(-I('.04')))/I('.04')
 rows=[]
 for ns,nz in resolutions:
  clock=time.perf_counter();mz=weighted_moments(nz,True)
  vm=[];vc=[];vbox=[];slabs=[];tmass=[];tbox=[];radii=[]
  for j in range(n):
   a0=iv.sqrt(I(j)/n);a1=iv.sqrt(I(j+1)/n)
   for z in range(ns):
    va=a0+(a1-a0)*z/ns;vb=a0+(a1-a0)*(z+1)/ns
    lo=bounds(va)[0];hi=bounds(vb)[1];lo=max(0,lo)
    mid=float((lo+hi)/2);rad=np.nextafter(max(mid-lo,hi-mid),UP)
    vc.append(mid);vbox.append([lo,hi]);radii.append(rad);slabs.append(j)
    vm.append(time_moments(va,vb,I(mid)));tbox.append([max(0,bounds(va*va)[0]),min(1,bounds(vb*vb)[1])])
  vm=np.array(vm);vc=np.array(vc);vbox=np.array(vbox);slabs=np.array(slabs);nt=len(vc)
  zc=-6+12*(np.arange(nz)+.5)/nz;zr=6/nz
  Zc=point(np.tile(zc,nt));V=point(np.repeat(vc,nz));J=np.repeat(slabs,nz)
  MU=np.array([around(mleft[j]) for j in J]);TH=point(np.array(theta)[J]);left=point(J/n)
  def jets(V,Z):
   u=plus(C(2),plus(MU,times(TH,minus(sq(V),left))))
   l=minus(minus(around(iv.ln(I(y0))),times(C('.025'),sq(V))),times(C('.3'),times(V,Z)))
   assert l[...,0].min()>float(iv.ln(I('.2')).a) and l[...,1].max()<float(iv.ln(I(12)).b)
   vals=source(u,l);S,B,Sl,Huu,Hul,Hll=vals
   uv=times(times(C(2),TH),V);lv=minus(times(C('-.05'),V),times(C('.3'),Z));lz=times(C('-.3'),V)
   Sv=plus(times(B,uv),times(Sl,lv));Sz=times(Sl,lz)
   Hvv=plus(plus(times(Huu,sq(uv)),times(C(2),times(Hul,times(uv,lv)))),times(Hll,sq(lv)))
   Hvv=plus(Hvv,plus(times(B,times(C(2),TH)),times(Sl,C('-.05'))))
   Hvz=plus(times(Hul,times(uv,lz)),times(Hll,times(lv,lz)));Hvz=plus(Hvz,times(Sl,C('-.3')))
   Hzz=times(Hll,sq(lz))
   return S,B,Sv,Sz,Hvv,Hvz,Hzz,Hul
  S,B,Sv,Sz,*_=jets(V,Zc)
  Mv=np.repeat(vm,nz,axis=0);Mz=np.tile(mz,(nt,1,1));mass=times(Mv[:,0],Mz[:,0])
  integrand=plus(times(S,mass),plus(times(Sv,times(Mv[:,1],Mz[:,0])),times(Sz,times(Mv[:,0],Mz[:,1]))))
  VB=np.repeat(vbox,nz,axis=0);ZB=np.stack([np.nextafter(np.tile(zc-zr,nt),DN),np.nextafter(np.tile(zc+zr,nt),UP)],-1)
  _,BB,_,_,Hvv,Hvz,Hzz,Beta_l=jets(VB,ZB)
  er=plus(times(point(absbound(Hvv)),times(C('.5'),times(Mv[:,2],Mz[:,0]))),times(point(absbound(Hzz)),times(C('.5'),times(Mv[:,0],Mz[:,2]))))
  er=plus(er,times(point(absbound(Hvz)),times(times(point(np.repeat(radii,nz)),point(zr)),mass)))
  rem=sum_out(er)[1];integ=sum_out(integrand);integ=plus(integ,np.array([-rem,rem]));integ=plus(integ,np.array([bounds(tail_source)[0],0.]))
  covariance=sum_out(times(C('.00375'),times(sq(VB),times(Beta_l,mass))))
  beta_l_tail=I('.00375')*I('2.5')*tail/2
  assert bounds(I(12)**(I(6)/11)*iv.ln(I(12))/4)[1]<2.5
  covariance=plus(covariance,np.array([-bounds(beta_l_tail)[1],0.]))
  assert covariance[1]<0
  cost=I(0)
  for j,th in enumerate(theta):cost+=I(k)*I(th)**2/2*(iv.exp(-I('.04')*j/n)-iv.exp(-I('.04')*(j+1)/n))/I('.04')
  # Mean dual coefficient b(t): integrate beta on full covering boxes, then
  # bound the remaining fraction of the current time cell independently.
  bm=times(BB,mass).reshape(nt,nz,2);bz=times(BB,Mz[:,0]).reshape(nt,nz,2)
  br=[];rangebeta=[]
  for j in range(nt):
   tailB=times(C('1.1'),around(tail))
   rangebeta.append(plus(sum_out(bz[j]),np.array([-tailB[1],tailB[1]])))
   tailint=times(tailB,vm[j,0]);br.append(plus(sum_out(bm[j]),np.array([-tailint[1],tailint[1]])))
  future=around(iv.exp(-I('.04'))*bT);gparts=[]
  for j in range(nt-1,-1,-1):
   partial=times(rangebeta[j],np.array([0,vm[j,0,1]]))
   qq=times(plus(future,partial),np.array([bounds(iv.exp(I('.04')*I(float(tbox[j][0]))))[0],bounds(iv.exp(I('.04')*I(float(tbox[j][1]))))[1]]))
   gap=max(gap_at(qq[0],theta[slabs[j]],k),gap_at(qq[1],theta[slabs[j]],k))
   gparts.append(times(point(gap),vm[j,0]));future=plus(future,br[j])
  gap_upper=sum_out(np.array(gparts))[1]
  total=plus(plus(integ,covariance),around(base+terminal-cost+variance+Z));total=plus(total,np.array([0,gap_upper]))
  # Gaussian integration by parts gives the covariance term. Boxes crossing
  # the consumption constraint use the full derivative interval [negative,0].
  row={'time_cells':nt,'normal_cells':nz,'source_boxes':nt*nz,'source_integral_interval':integ.tolist(),'source_taylor_remainder_upper':float(rem),'covariance_correction_interval':covariance.tolist(),
   'tangent_control_gap_upper':float(gap_upper),'variance_allowance_upper':bounds(variance)[1],'localization_upper':bounds(Z)[1],
   'optimal_value_upper':float(total[1]),'seconds':time.perf_counter()-clock,
   'target':.01,'target_met':False}
  policy=json.loads((OUT/f'policy_certificate_k{k:g}.json').read_text());L=policy['records'][-1]['policy_value_interval'][0]
  row['certified_regret_upper']=float(np.nextafter(row['optimal_value_upper']-L,UP));row['target_met']=row['certified_regret_upper']<.01
  rows.append(row)
  (OUT/f"flexible_dual_k{k:g}.partial.json").write_text(json.dumps({"k":k,"status":"in_progress","planned_resolutions":list(resolutions),"records":rows},indent=2)+"\n")
  print(k,json.dumps(row),flush=True)
 result={'k':k,'initial':[0,2,1.25],'y0':y0,'tangent_theta':theta,'terminal_slope_interval':bounds(bT),'primitive_checks':primitive,
  'gradient_second_moment_bound':bounds(D2),'normal_tail_probability_upper':bounds(tail)[1],
  'original_payoff':True,'original_continuous_actions':True,'original_stopping_contract':True,
  'scope':'Upper bound on the optimum of the original flexible economy, not a policy payoff; central initial state only',
  'arithmetic':'70-digit interval constants/weight moments; outward binary64 elementary operations; analytic Taylor and Gaussian tails',
  'records':rows,'total_seconds':time.perf_counter()-start,'status':'complete','planned_resolutions':list(resolutions)}
 (OUT/f'flexible_dual_k{k:g}.json').write_text(json.dumps(result,indent=2)+'\n')
 (OUT/f'flexible_dual_k{k:g}.partial.json').unlink(missing_ok=True)
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--k',type=float,default=2);ap.add_argument('--quick',action='store_true');a=ap.parse_args()
 run(a.k,((4,64),(8,128)) if a.quick else ((4,64),(8,128),(16,256)))
