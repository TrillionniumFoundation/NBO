"""Fresh deterministic comparators and certified affine payoff majorants on K.

Joint concavity gives a stochastic-payoff upper bound after replacing running
preference risk by its mean. This is an upper bound, not an equality, and hence
is safe for proving improvement of the new stochastic policies over these
named deterministic policies. No claim concerns all deterministic controls.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json,time
import numpy as np
from certify_stochastic import I,Q,exp,log,stack,add_reduce,upper,ROOT,gaussian_errors
from validated_gauss import mapped_rule,cauchy_remainder,sqrt
from fresh_time_frontier import generate_policy
from independent_primal import evaluate
REV=ROOT/'revisions/2026-09-23-r20'

def affine_upper(d):
 n=len(d['c']);th=I(d['theta']);c=I(d['c']);qr=(1-exp(-Q('.02')))/Q('.02')
 assert min(c.lo)-float((Q('.01')/qr).hi)>.5 and max(c.hi)+float((Q('.01')/qr).hi)<.8
 left=stack([Q(F(j,n)) for j in range(n)]);right=stack([Q(F(j+1,n)) for j in range(n)])
 t,w=mapped_rule(left,right);pref=stack([add_reduce(th[:j])/n if j else I(0) for j in range(n)])
 m=2+pref.reshape(-1,1)+th.reshape(-1,1)*(t-left.reshape(-1,1));r=m-1
 cc=c.reshape(-1,1);a=-log(cc);ex=exp(r*a)
 f=-ex/r;fu=ex*(1-r*a)/r.square();fc=ex/cc
 wd=w*exp(-Q('.04')*t)
 total=lambda z:add_reduce(add_reduce(z,axis=1),axis=0)
 ev=add_reduce(cauchy_remainder(right-left,(right-left)/2,F(1,4),F(100)))
 eps=I(-ev.hi,ev.hi)
 B=total(wd*f)+eps;gu=total(wd*fu)+eps;gx=total(wd*fc)/qr+eps
 dr=stack([(exp(-Q('.02')*left[j])-exp(-Q('.02')*right[j]))/Q('.02') for j in range(n)])
 R=exp(Q('.02'))*(Q('1.25')-add_reduce(dr*c));assert R.lo>.5
 masses=stack([(exp(-Q('.04')*left[j])-exp(-Q('.04')*right[j]))/Q('.04') for j in range(n)])
 mean=add_reduce(th)/n
 B-=add_reduce(masses*th.square())
 B+=exp(-Q('.04'))*(-Q('.02')*(mean.square()+Q('.0025'))+Q('.1')*log(R))
 gu+=exp(-Q('.04'))*(-Q('.04')*mean)
 pe=2*exp(-Q('.58')**2/(2*Q('.0025')))
 # Clipping bias <=2 sqrt(pe); |f_u|<=100 on the stated tangent states.
 error=200*sqrt(pe)+20*pe+Q('.02')*sqrt(Q('.01')*pe)
 out=[]
 for u,x in [('1.98','1.24'),('1.98','1.26'),('2.02','1.24'),('2.02','1.26')]:
  v=B+gu*(Q(u)-2)+gx*(Q(x)-Q('1.25'))+error
  out.append({'u0':u,'x0':x,'policy_value_upper':float(v.hi)})
 return {'intercept_interval':B.pair(),'u_slope_interval':gu.pair(),'x_slope_interval':gx.pair(),'tail_and_stopping_error':float(error.hi),
   'corners':out,'proof':'jointly concave running utility, exact mean dynamics, supporting affine plane, explicit clipping/stopping correction',
   'scope':'named deterministic time policy, consumption shifted by (x-1.25)/Q_r, p=0, t=0,k=2; not the unrestricted optimal value'}

def run():
 out=REV/'results/classical_deterministic';out.mkdir(parents=True,exist_ok=True);rows=[]
 for n in [16,32,64]:
  d=generate_policy(n,2);ap=out/f'actor_n{n}.json';ap.write_text(json.dumps(d,indent=2)+'\n')
  checked=evaluate(ap,'2');bound=affine_upper(d)
  row={'slabs':n,'generation_seconds':d['seconds'],'value_certificate':checked,'K_affine_policy_upper':bound,
       'reference_regret_upper':upper(2,1.25)-checked['value_interval'][0],'algorithm':'fresh deterministic SLSQP transcription'}
  rows.append(row);(out/'records.json').write_text(json.dumps(rows,indent=2)+'\n')
  print(n,checked['value_interval'],bound['corners'],flush=True)
if __name__=='__main__':run()
