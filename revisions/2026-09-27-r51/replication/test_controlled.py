import unittest,copy,math,random
from fractions import Fraction as F
import controlled as c
import check_controlled as v

BASE={'id':'test','beta':'3/4','eps':'1/5','c':'2','theta':['19/20','0'],'g':['1/8','2/5'],'h':['2/3','4/3'],'k':['2/3','-1/4']}
class Contracts(unittest.TestCase):
 def test_log(self):
  import mpmath as mp
  mp.mp.dps=100
  for r in [F(1),F(2),F(1,3),F(13,7),F(9999),F(1,10001)]:
   lo,hi=c.log_bound(r);x=mp.log(mp.mpf(r.numerator)/r.denominator)
   self.assertLessEqual(mp.mpf(lo.numerator)/lo.denominator,x)
   self.assertGreaterEqual(mp.mpf(hi.numerator)/hi.denominator,x)
 def test_ratio(self):
  import mpmath as mp
  mp.mp.dps=100
  lo,hi=c.integrate_ratio([F(3),F(-2),F(7)],[F(2),F(5)],F(0),F(1))
  x=mp.quad(lambda t:(3-2*t+7*t*t)/(2+5*t),[0,1])
  self.assertLessEqual(mp.mpf(lo.numerator)/lo.denominator,x)
  self.assertGreaterEqual(mp.mpf(hi.numerator)/hi.denominator,x)
 def test_full_and_restricted(self):
  for restricted in [False,True]:
   p=c.run(BASE,seconds=10,max_nodes=5000,restricted=restricted)
   self.assertTrue(v.check(p)['verified']);self.assertEqual(p['status'],'target')
 def test_tampered_lower(self):
  p=c.run(BASE,max_nodes=15);p['nodes'][0]['lower']='9999'
  with self.assertRaises(AssertionError):v.check(p)
 def test_tampered_policy(self):
  p=c.run(BASE,max_nodes=15);p['moment']=['1','1/4']
  with self.assertRaises(AssertionError):v.check(p)
 def test_missing_cover(self):
  p=c.run(BASE,max_nodes=15);p['nodes'][0]['children'].pop()
  with self.assertRaises(AssertionError):v.check(p)
 def test_false_domain_prune(self):
  p=c.run(BASE,max_nodes=15);p['nodes'][0]={'box':p['nodes'][0]['box'],'outside':True}
  with self.assertRaises(AssertionError):v.check(p)
 def test_corners_bound_exact_rows(self):
  from scipy.optimize import linprog
  d=c.validate(BASE);rng=random.Random(419)
  for _ in range(25):
   u=F(rng.randrange(100),100);z=(F(rng.randrange(201),100)-1)*u*(1-u)
   x=F(rng.randrange(100),100)
   costs,reg=c.coefficients(d,[u,u,z,z],1 if x>=F(1,2) else -1)
   qs=[float(c.ev(a,x)) for a in costs];rs=[float(c.ev(a,x)) for a in reg]
   sol=linprog(qs,A_ub=[rs],b_ub=[float(d['eps'])],A_eq=[[1,1]],b_eq=[1],bounds=[(0,1)]*2)
   self.assertTrue(sol.success)
   p0= min(F(1),max(F(0),(d['eps']-c.ev(reg[1],x))/(c.ev(reg[0],x)-c.ev(reg[1],x)))) if qs[0]<qs[1] else F(0)
   self.assertAlmostEqual(float(p0*c.ev(costs[0],x)+(1-p0)*c.ev(costs[1],x)),sol.fun,places=10)
if __name__=='__main__':unittest.main()
