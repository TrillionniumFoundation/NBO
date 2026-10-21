"""Synthetic exact-quadratic fixtures only: never imports or runs original economy."""
from fractions import Fraction as F
from types import SimpleNamespace
import hashlib,json,sys
from pathlib import Path
import service122 as s
from stats122 import radius_witness,cp
s.lab=SimpleNamespace(smoothness_rational=lambda alpha:{'L_action':F(20)})
checks=0;qualified=0;strict=0
for state in ([0.,0.],[1.,1.]):
 cap=F(1,8)+sum(map(F,state))/16
 for a in (F(0),cap/4,cap/2,3*cap/4,cap):
  for curvature in (F(2),F(4),F(10)):
   for opt in (-cap,0,cap/3,cap,2*cap):
    def q(t):return F(1)+curvature*(t-opt)**2/2
    true_gradient=curvature*(a-opt)
    for error in (F(0),F(1,2**24),F(1,2**16)):
     # An exact tangent with downward anchor remains a valid global mu=2 support.
     c={'original_action':float(a),'support_anchor_lower':float(q(a)-error),'original_q_upper':float(q(a)+error),
        'support_slope_lower':float(true_gradient),'support_slope_upper':float(true_gradient),'optimum_lower':0.}
     # First make all endpoints independently outward with exact rational tests.
     c['support_anchor_lower']=s.directed_float(q(a)-error,False);c['original_q_upper']=s.directed_float(q(a)+error,True)
     c['support_slope_lower']=s.directed_float(true_gradient,False);c['support_slope_upper']=s.directed_float(true_gradient,True)
     g=s.recover(c,state,.5)
     assert g['lower']<=true_gradient<=g['upper'];checks+=1
     for fraction in (F(1),F(1,2),F(1,4),F(1,8),F(1,16),F(1,32)):
      p=s.proposal(g,float(cap),fraction);b=p['candidate'];assert 0<=b<=cap
      assert p['robust_original_q_gain_lower']<=q(a)-q(b);checks+=2
      if p['original_policy_gain_lower']>0 and not p['unchanged_action']:
       strict+=1;cert=s.candidate_certificate(c,g,p,0.)
       assert F(cert['lower'])<=q(b) and F(cert['upper'])>=q(b)+s.DELTA
       assert F(cert['exact_optimum_lower'])<=q(max(F(0),min(cap,opt)));checks+=3
       qualified+=cert['qualified']
w=radius_witness()
for k in range(33):
 r=cp(k);assert 0<=r['lower']<=r['inversion_upper']<=1;checks+=1
print(json.dumps({'scope':'synthetic exact quadratic boundary/rounding/safe-gain/qualification fixtures plus exact distribution-free arithmetic; zero original-economic queries','checks':checks,'strict_gain_candidates':strict,'qualified_candidates':qualified,'radius_exponent':str(w['exponent']),'source_sha256':hashlib.sha256(Path(s.__file__).read_bytes()).hexdigest()},indent=2))
