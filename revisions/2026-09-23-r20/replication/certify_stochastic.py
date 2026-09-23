"""Directed, policy-specific payoff/price enclosures for neural hedged consumption.

No optimizer, simulated paths, learned critic, or inherited policy labels are
used by this checker. Rationally isolated Gauss roots and Cauchy/Taylor bounds
certify the integrals. BACKEND=mpfr selects the separate MPFR arithmetic path.
The shared mathematics is explicitly not a formal proof assistant certificate.
"""
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
import os,sys,json,math,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
if os.getenv('BACKEND')=='mpfr':
 sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
 import mpfr_interval as A
 sys.modules['interval64']=A
else:
 sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
 import interval64 as A
sys.path.insert(0,str(ROOT/'revisions/2026-09-22-r14/replication'))
from validated_gauss import mapped_rule,cauchy_remainder,sqrt,pi
I,Q,exp,log,stack,add_reduce=A.I,A.I.rational,A.exp,A.log,A.stack,A.add_reduce
BACKEND='mpfr' if os.getenv('BACKEND')=='mpfr' else 'rational-taylor-binary64'

@lru_cache(None)
def grid(n=16,nz=96,vstep=F(1,40)):
 # Cell endpoints enclose EXACT sqrt(j/n), not the floating proposals.
 va=[];vb=[];slabs=[]
 for j in range(n):
  left=sqrt(Q(F(j,n)));right=sqrt(Q(F(j+1,n)))
  nv=math.ceil(float((right-left).hi)/float(vstep))
  for k in range(nv):
   va.append(left+(right-left)*Q(F(k,nv)))
   vb.append(left+(right-left)*Q(F(k+1,nv)));slabs.append(j)
 va,vb=stack(va),stack(vb)
 v,wv=mapped_rule(va,vb);v=v.reshape(-1,1);wv=wv.reshape(-1,1)
 za=stack([Q(-8)+Q(F(16*j,nz)) for j in range(nz)])
 zb=stack([Q(-8)+Q(F(16*(j+1),nz)) for j in range(nz)])
 assert add_reduce(wv.reshape(-1)).lo<=1<=add_reduce(wv.reshape(-1)).hi
 assert add_reduce((2*v*wv).reshape(-1)).lo<=1<=add_reduce((2*v*wv).reshape(-1)).hi
 z,wz=mapped_rule(za,zb);z=z.reshape(1,-1);wz=wz.reshape(1,-1)
 ev=add_reduce(cauchy_remainder(vb-va,(vb-va)/2,F(1,16),F(100)))
 ez=add_reduce(cauchy_remainder(zb-za,(zb-za)/2,F(1,2),F(100)))
 # Sum v-rule weights encloses length 1, bounded by 2. z-length is 16.
 error=(16*ev+2*ez).hi
 return v,wv,z,wz,np.repeat(np.asarray(slabs),8),float(error)

def gaussian_errors():
 # Taylor remainder of order 12 about r0>=.88, on |z2|<=8;
 # r>=.49, r<=1.71, |log c|<=.7 gives derivative/n! <=10/.49^(n+1).
 taylor=Q(10*10395)*Q('.00234375')**6/Q('.49')**13
 # Tail probability and full even moments omitted from |Z|<=8.
 phi=exp(-Q(32))/sqrt(2*pi());tail0=2*phi/8
 tails=[tail0]
 for n in range(2,12,2):tails.append(2*Q(8)**(n-1)*phi+(n-1)*tails[-1])
 coefftail=I(0)
 for j,tau in enumerate(tails):
  # Derivative coefficient at r0>=.88 is bounded by 10/.88^(2j+1).
  coefftail+=Q(10)*Q('.00234375')**j/Q('.88')**(2*j+1)*tau
 normal_tail=Q(12)*tail0 # union of omitted z1 and z2 tails; clipped utility magnitude <=6.
 return taylor,coefftail,normal_tail,tail0

def upper(u,x):
 """Common independently certified original-economy dual, not a policy critic."""
 library=ROOT/'revisions/2026-09-23-r16/results/fresh_library'
 nodes=json.loads((library/'nodes.json').read_text())
 lo=max((r for r in nodes if r['k']<=2),key=lambda r:r['k'])
 hi=min((r for r in nodes if r['k']>=2),key=lambda r:r['k'])
 def U(r):
  d=json.loads((library/f"dual_k{r['k']:g}.json").read_text())
  du=Q(str(u))-2;loc=8*exp(-Q(18))*(exp(120*du)+exp(-120*du)-2)
  return I(d['optimal_value_upper'])+du*I(*d['b0_interval'])+(Q(str(x))-Q('1.25'))*I(d['y0'])+loc
 w=(Q(2)-I(lo['k']))/(I(hi['k'])-I(lo['k']))
 result=(1-w)*U(lo)+w*U(hi)
 return float(result.hi)

def certify(d,nz=96,vstep=F(1,40)):
 start=time.perf_counter();n=len(d['b'])
 assert n==16 and len(d['s'])==len(d['theta'])==n
 assert all(.1<=s<=6.5 for s in d['s']) and all(0<=t<=.2 for t in d['theta'])
 assert 1.98<=float(d['u0'])<=2.02 and 1.24<=float(d['x0'])<=1.28
 v,wv,z,wz,idx,quaderr=grid(n,nz,vstep);t=v.square()
 b=I(np.asarray(d['b'])[idx,None]);s=I(np.asarray(d['s'])[idx,None]);th=I(np.asarray(d['theta'])[idx,None])
 th_all=I(d['theta']);prefix=stack([add_reduce(th_all[:j])/n if j else I(0) for j in range(n)])
 mean=Q(str(d['u0']))+prefix[idx].reshape(-1,1)+th*(t-I(idx).reshape(-1,1)/n)
 density=exp(-z.square()/2)/sqrt(2*pi());weight=wv*wz*density
 Lq=Q('.065')*t+Q('.3')*v*z
 sq=1/(1+exp(-(b-s*Lq)));cq=Q('.5')+Q('.3')*sq
 def total(a):return add_reduce(add_reduce(a,axis=1),axis=0)
 price_raw=total(weight*2*v*exp(-Q('.02')*t)*cq)
 price_derivative_raw=total(weight*2*v*exp(-Q('.02')*t)*(-Q('.3')*s*sq*(1-sq)))
 tay,tailpoly,tailflow,tail0=gaussian_errors()
 price_error=I(quaderr)+Q('.8')*tail0
 # Missing price tail is positive; a symmetric enclosure is conservative.
 price=price_raw+I(-price_error.hi,price_error.hi)
 derivative_error=I(quaderr)+Q('1.95')*tail0
 price_derivative=price_derivative_raw+I(-derivative_error.hi,derivative_error.hi)
 reserve=exp(Q('.02'))*(Q(str(d['x0']))-price)
 assert float(reserve.lo)>.5 and float(reserve.hi)<.5001,('Reserve infeasible',reserve.pair())
 initial_portfolio=-Q('1.5')*price_derivative/Q(str(d['x0']))
 Lp=-Q('.025')*t+Q('.3')*v*z
 c=Q('.5')+Q('.3')/(1+exp(-(b-s*Lp)))
 ell=log(c);r0=mean-1+Q('.0125')*v*z
 assert np.min(r0.lo)>.879 and np.max(r0.hi)<1.321
 expo=exp(-r0*ell);a=-expo/r0;poly=a;epart=-expo;moment=I(1)
 # Coefficients satisfy (r0+x) F(r0+x)=-exp(-r0*ell) exp(-x*ell).
 for k in range(1,11):
  epart=epart*(-ell)/k;a=(epart-a)/r0
  if k%2==0:
   moment=moment*(k-1)*Q('.00234375')*t
   poly+=a*moment
 running_raw=total(weight*2*v*exp(-Q('.04')*t)*poly)
 running_error=I(quaderr)+tay+tailpoly+tailflow
 running=running_raw+I(-running_error.hi,running_error.hi)
 masses=stack([(exp(-Q('.04')*Q(F(j,n)))-exp(-Q('.04')*Q(F(j+1,n))))/Q('.04') for j in range(n)])
 effort=add_reduce(th_all.square()*masses) # k=2: k theta^2/2=theta^2.
 terminal_mean=Q(str(d['u0']))-2+add_reduce(th_all)/n
 terminal=exp(-Q('.04'))*(-Q('.02')*(terminal_mean.square()+Q('.0025'))+Q('.1')*log(reserve))
 pexit=2*exp(-Q('.58')**2/(2*Q('.0025')))
 fourth=Q('.22')**4+6*Q('.22')**2*Q('.0025')+3*Q('.0025')**2
 exit_error=20*pexit+Q('.02')*sqrt(fourth*pexit)
 value=running-effort+terminal+I(-exit_error.hi,exit_error.hi)
 u=upper(d['u0'],d['x0'])
 # Global control bound, using a common bound on terminal reserve for mixtures.
 kappa=(sqrt(Q('.79'))-sqrt(Q('.49')))/(sqrt(Q('.79'))+sqrt(Q('.49')))
 xmax=Q('.5')+Q('.79')*(1-exp(-Q('.02')))/Q('.02')+Q('.0001')
 pmax=Q('1.5')*Q('6.5')*kappa*(1-Q('.5')/xmax)
 assert pmax.hi<.8 and initial_portfolio.lo>0 and initial_portfolio.hi<.8
 return {'status':'CERTIFIED','backend':BACKEND,'u0':d['u0'],'x0':d['x0'],'k':2,
  'value_interval':value.pair(),'optimal_value_upper':u,'regret_upper':float((I(u)-I(value.lo)).hi),
  'price_interval':price.pair(),'reserve_interval':reserve.pair(),'initial_portfolio_interval':initial_portfolio.pair(),
  'portfolio_global_upper':float(pmax.hi),'wealth_global_upper':float(xmax.hi),
  'proof_errors':{'quadrature':quaderr,'conditional_taylor':float(tay.hi),'conditional_tail':float(tailpoly.hi),'normal_tail':float(tailflow.hi),'stopping':float(exit_error.hi)},
  'quadrature_nodes':int(v.lo.size*z.lo.size),'normal_cells':nz,'max_v_cell':str(vstep),
  'seconds':time.perf_counter()-start,'scope':'t=0, k=2, stated initial state; four-corner mixing separately proves K-uniform transfer',
  'upper_source':'R16 unrestricted dual certificates with convex price interpolation; no neural value labels'}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('actor',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
 r=certify(json.loads(a.actor.read_text()));s=json.dumps(r,indent=2)+'\n';print(s)
 if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(s)
