"""Independent exact-rational/high-precision checks; fixtures are not proofs."""
from pathlib import Path
import sys,json,math,random
from fractions import Fraction as F
import numpy as np
import mpmath as mp
import neural_chain as nc
import deployment as dep
R=Path(__file__).resolve().parents[1]
def main():
 mp.mp.dps=90;rng=random.Random(41007);checks=0
 nets=[dict(w=[0.,-3.,7.,-1.],b=[.25,1.,-2.,.5],c=[1.,.125,-.5,.25],linear=.125,intercept=.25)]
 for p in [1.,4.]:
  for t in [0.,1.]:nets+=nc.load_record(p,t)[1]['networks']
 for net in nets:
  cuts,slopes,val=nc.pieces(net);xs=sorted({0.,1.}|{float(x) for x in cuts}|{rng.random() for _ in range(20)})
  for x in xs:
   lo=max(0.,math.nextafter(x,-math.inf));hi=min(1.,math.nextafter(x,math.inf))
   out=nc.network(net,nc.I.point(np.array([x])));exact=val(F(x))
   assert F(float(out.lo[0]))<=exact<=F(float(out.hi[0]));checks+=1
   out=nc.network(net,nc.I(np.array([lo]),np.array([hi])))
   candidates=[F(lo),F(hi)]+[z for z in cuts if F(lo)<=z<=F(hi)]
   assert F(float(out.lo[0]))<=min(map(val,candidates)) and max(map(val,candidates))<=F(float(out.hi[0]));checks+=1
  terminal=nc.terminal_residual(net)
  for _ in range(20):
   x=F(rng.random());v=val(x)-2*(x-F(11,16))**2-2*max(F(0),F(3,8)-x)**2
   assert F(terminal['lower'])<=v<=F(terminal['upper']);checks+=1
 riskchecks=0
 for width in [.01,.2,1.,8.]:
  for _ in range(25):
   v=np.array([[rng.uniform(-width,width) for _ in range(3)]])
   out=nc.small_risk(nc.I.point(v),1.)
   exact=mp.log(sum(mp.mpf(p)*mp.exp(mp.mpf(float(z))) for p,z in zip([.25,.5,.25],v[0])))
   assert mp.mpf(float(out.lo[0]))<=exact<=mp.mpf(float(out.hi[0]));riskchecks+=1
 # Direct verification must remain executable with the conventional spline evaluator disabled.
 import nonlinear as nl
 old=nl.spline
 def forbidden(*args,**kwargs):raise AssertionError('Spline evaluator entered direct certificate')
 nl.spline=forbidden
 try:
  _,rec=nc.load_record(1.,0.);tiny=nc.certify_chain(rec['networks'],1.,0.,8,4)
  assert math.isfinite(tiny['policy_gap_upper'])
 finally:nl.spline=old
 output=dict(neural_rational_checks=checks,risk_high_precision_checks=riskchecks,direct_certificate_with_spline_disabled=True,deployment=dep.test())
 (R/'audit/TESTS.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n');print(json.dumps(output),flush=True)
if __name__=='__main__':main()
