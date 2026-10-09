"""Additional publication tests; the pre-execution test file is unchanged."""
import unittest,math
from fractions import Fraction as F
import numpy as np
import operators50 as o
class PublicationTests(unittest.TestCase):
 def test_directed_subtraction(self):
  # Exact subtraction of binary endpoints must be enclosed even after cancellation.
  vals=[.1,.2,.3,1.,-1.,math.nextafter(1.,math.inf),2.**-52,1000.]
  saw_nearest_failure=False
  for a in vals:
   for b in vals:
    exact=F(a)-F(b);nearest=float(a-b)
    saw_nearest_failure|=F(nearest)>exact
    self.assertLessEqual(F(float(np.nextafter(nearest,-np.inf))),exact)
    self.assertGreaterEqual(F(float(np.nextafter(nearest,np.inf))),exact)
  self.assertTrue(saw_nearest_failure)
 def test_reference_advantage_width(self):
  # Independent finite exact construction: interval width, not twice a level bound.
  h=[F(3,2),F(-1,4),F(7,3)];e=[F(1,7),F(-2,5),F(1,3)];beta=F(15,16)
  for pa in ([F(1),0,0],[0,F(1),0],[F(1,3)]*3):
   for pb in ([0,0,F(1)],[F(1,2),F(1,2),0]):
    delta=sum((F(a-b)*v for a,b,v in zip(pa,pb,h)),F(0))*beta
    true=sum((F(a-b)*(v+ee) for a,b,v,ee in zip(pa,pb,h,e)),F(0))*beta
    self.assertLessEqual(true,delta+beta*(max(e)-min(e)))
 def test_price_envelope_regret(self):
  truth=[F(1),F(9,10),F(21,20)];lo=[x-F(1,40) for x in truth];hi=[x+F(1,40) for x in truth];work=[F(1),F(4),F(0)]
  for price in [F(0),F(1,100),F(1,10),F(10)]:
   j=min(range(3),key=lambda j:(hi[j]+price*work[j],j))
   regret=truth[j]+price*work[j]-min(v+price*w for v,w in zip(truth,work))
   upper=hi[j]+price*work[j]-min(v+price*w for v,w in zip(lo,work))
   self.assertLessEqual(regret,upper)
 def test_terminal_gate_incumbent_equality(self):
  x=o.I(np.array([[.1,.2],[.7,.8]]),np.array([[.101,.201],[.701,.801]]));a=o.I.point(np.array([.03,.04]))
  diff=o.final_difference(x,a,a,1)
  self.assertTrue(np.all(diff.lo<=0) and np.all(diff.hi>=0))
if __name__=='__main__':unittest.main(verbosity=2)
