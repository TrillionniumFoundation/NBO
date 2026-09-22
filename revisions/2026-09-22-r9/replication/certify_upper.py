"""Continuous original-economy certificate for a fitted polynomial witness."""
from __future__ import annotations
import json,pathlib,math,time,argparse
import numpy as np
from bernstein import *
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'revisions/2026-09-22-r9/results'

def utility_poly():
 # -exp(L*(A+B*z))/(A+B*z), z=2y-1. Exact inverse Chebyshev series.
 A=I('1.05');B=I('.55');L=-iv.ln(I('.8'));D=iv.sqrt(A*A-B*B);q=B/(A+D)
 Ts=shifted_cheb(16);inv=[I(0)]*17
 for n in range(17):
  c=(1 if n==0 else 2)*(-q)**n/D
  for j,t in enumerate(Ts[n]):inv[j]+=c*t
 invtail=2*q**17/(D*(1-q))
 expP=[I(0)]*9
 # exp(L*A) * sum (L*B*(2y-1))^j/j!
 for j in range(9):
  c=iv.exp(L*A)*(L*B)**j/math.factorial(j)
  for l in range(j+1):expP[l]+=c*math.comb(j,l)*2**l*(-1)**(j-l)
 exptail=iv.exp(L*(A+B))*(L*B)**9/math.factorial(9)
 err=iv.exp(L*(A+B))*invtail+(1/D*(1+2*q/(1-q)))*exptail
 return scale(mul([inv],[expP]),-1),bounds(err)[1]

def run(k,ceilings=(.005,.002,.001)):
 start=time.perf_counter();p=json.loads((OUT/f'upper_k{k:g}.json').read_text());P=from_cheb(p['coefficients'])
 F=[ [I(0)]*len(P[0]) ]+P
 Fu=scale(deriv(F,1),I(1)/I('1.1'));Fuu=scale(deriv(Fu,1),I(1)/I('1.1'))
 q=add(Fu,[[I('.02'),I('-.044')]])
 base=add(scale(deriv(F,0),-1),scale(Fuu,'.00125'))
 base=add(base,scale(F,'-.04'))
 utility,err=utility_poly();base=add(base,utility)
 base=add(base,[[I('.0002')+I('.00195')+I('.00352')-I('.04')-I('.004')*iv.ln(I(2)),I('-.00088'),I('.000968')]])
 plus=add(add(base,scale(q,'.2')),[[ -I('.02')*k ]])
 minus=add(add(base,scale(q,'-.2')),[[ -I('.02')*k ]])
 inside=add(base,scale(mul(q,q),I(1)/(2*I(k))))
 deg=(max(len(z) for z in [q,plus,minus,inside])-1,max(len(z[0]) for z in [q,plus,minus,inside])-1)
 polys=np.array([bern(z,deg) for z in [q,plus,minus,inside]])
 trace,ntrace=certify_min(bern(P),-8)
 assert trace>=-8,'Stopped-trace condition fails'
 at=I(0);Ts=shifted_cheb(len(P[0])-1);y=I(5)/11
 for i,row in enumerate(P):
  for j,c in enumerate(row):at+=c*y**j # h=1
 G=I('.1')*iv.ln(I('1.25'))
 barrier=8*(iv.exp(-I(18))+iv.exp(-I(32)))
 C=(1-iv.exp(-I('.04')))/I('.04')
 reports=[]
 for ceiling in ceilings:
  r=certify_hamiltonian(polys,k,ceiling-err)
  eps=I(r['residual_upper_bound'])+I(err)
  value=G+at+barrier+iv.mpf([0, max(0,bounds(eps)[1])])*C
  r.update({'utility_approximation_error':err,'upper_value_initial':bounds(value)[1],
           'fitted_F_initial_interval':bounds(at),'localization_correction_upper':bounds(barrier)[1]})
  reports.append(r);print('certificate',k,r,flush=True)
 result={'k':k,'initial':[0,2,1.25],'core_u':[1.5,2.6],'original_payoff':True,
 'f_over_h_lower_bound':trace,'trace_boxes':ntrace,'reports':reports,'total_seconds':time.perf_counter()-start,
 'arithmetic':'mpmath.iv 70-digit coefficient conversion; outward binary64 de Casteljau subdivisions',
 'witness':'G+F(h,u)+8h*sum of two exponential exit barriers+epsilon*C_rho(h)',
 'barrier_rates':[120,160],'barrier_time_rates':[42,64],
 'scope':'upper bound on optimal value in the original stopped Brownian economy, at stated initial state'}
 (OUT/f'upper_certificate_k{k:g}.json').write_text(json.dumps(result,indent=2)+'\n')
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--k',type=float,default=2);a=ap.parse_args();run(a.k)
