import contextlib,io,json,math,tempfile,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import numpy as np
from policy_certificate import Ball,gamma,certify,value_balls
from experiment import economy,evaluate,riccati,initial_state,fit_square_critic,run
from replay_and_tables import factor_certificate

class ArithmeticTests(unittest.TestCase):
 def test_gamma_guard(self):
  with self.assertRaises(ValueError):gamma(0)
 def test_nonfinite_ball(self):
  with self.assertRaises(ArithmeticError):Ball.exact([np.inf])
 def test_negative_radius(self):
  with self.assertRaises(ValueError):Ball(np.ones(2),-np.ones(2))
 def test_exact_rational_products(self):
  rng=np.random.default_rng(17)
  for _ in range(12):
   a=rng.normal(size=(3,5));b=rng.normal(size=(5,2));z=Ball.exact(a)@Ball.exact(b)
   for i in range(3):
    for j in range(2):
     v=sum(F(float(a[i,k]))*F(float(b[k,j])) for k in range(5))
     self.assertLessEqual(F(float(z.c[i,j]))-F(float(z.r[i,j])),v)
     self.assertGreaterEqual(F(float(z.c[i,j]))+F(float(z.r[i,j])),v)
 def test_exact_sum_scale(self):
  a=np.array([.1,-.3,1e8]);b=np.array([.2,.7,-1e8]);z=(Ball.exact(a)+Ball.exact(b)).scale(.13)
  for i in range(3):
   v=(F(float(a[i]))+F(float(b[i])))*F(.13)
   self.assertLessEqual(F(float(z.c[i]))-F(float(z.r[i])),v)
   self.assertGreaterEqual(F(float(z.c[i]))+F(float(z.r[i])),v)
 def test_uncertain_product(self):
  a=np.array([[1.,-.2],[.5,2.]]);b=np.array([[.4,.3],[-1.,2.]])
  z=Ball(a,np.full((2,2),.01))@Ball(b,np.full((2,2),.02))
  exact=(a+.009)@(b-.019)
  self.assertTrue(np.all(abs(exact-z.c)<=z.r))
 def test_infinity_norm(self):
  b=Ball.exact([[1.,-2.],[3.,4.]])
  self.assertGreaterEqual(b.norm_inf(),7.)
 def test_frobenius_norm(self):
  b=Ball.exact([[3.,4.]])
  self.assertGreaterEqual(b.norm_f(),5.)
 def test_trace_enclosure(self):
  b=Ball.exact(np.diag([.1,.2,.3])).trace();v=F(.1)+F(.2)+F(.3)
  self.assertLessEqual(F(b.lower()),v);self.assertGreaterEqual(F(b.upper()),v)
 def test_cancellation(self):
  a=np.array([[1e15,1.,-1e15]])
  b=Ball.exact(a)@Ball.exact(np.ones((3,1)))
  self.assertLessEqual(b.c.item()-b.r.item(),1.)
  self.assertGreaterEqual(b.c.item()+b.r.item(),1.)

class PolicyTests(unittest.TestCase):
 def setUp(self):self.m=economy(3,'anchor',4);self.K=riccati(self.m)
 def test_invalid_cost(self):
  self.m['Q'][0,0,0]=0
  with self.assertRaises(ValueError):certify(self.m,self.K)
 def test_invalid_covariance(self):
  self.m['Sigma'][0,1]=1
  with self.assertRaises(ValueError):certify(self.m,self.K)
 def test_invalid_shape(self):
  with self.assertRaises(ValueError):certify(self.m,np.zeros((1,2,2)))
 def test_nonfinite_policy(self):
  self.K[0,0,0]=np.nan
  with self.assertRaises(ArithmeticError):certify(self.m,self.K)
 def test_riccati_certified(self):
  self.assertLess(certify(self.m,self.K)['policy_gap_upper'],1e-8)
 def test_actual_global_loss(self):
  k=self.K+.05*np.eye(3);a,c=evaluate(self.m,k);p,v=evaluate(self.m,self.K)
  bound=certify(self.m,k)['policy_gap_upper']
  actual=3*max(0,float(np.linalg.eigvalsh(a[0]-p[0]).max()))+c[0]-v[0]
  self.assertLessEqual(actual,bound)
 def test_far_state_coercivity(self):
  k=self.K+.1*np.eye(3);p,_=evaluate(self.m,k);eta=certify(self.m,k)['eta']
  for t in range(4):
   a,b,r,q=(self.m[n][t] for n in ('A','B','R','Q'));beta=self.m['beta']
   h=r+beta*b.T@p[t+1]@b;d=h@k[t]-beta*b.T@p[t+1]@a
   x=np.array([1.,-.3,.8])*1e6
   g=x@d.T@np.linalg.solve(h,d@x)
   self.assertLessEqual(g,eta*(x@q@x))
 def test_implementation_envelope(self):
  e=1e-4;k=self.K;pe,ce=evaluate(self.m,k+e*np.eye(3));p,c=evaluate(self.m,k)
  allowance=certify(self.m,k,e)['implementation_gap_upper']
  actual=3*max(0,float(np.linalg.eigvalsh(pe[0]-p[0]).max()))+ce[0]-c[0]
  self.assertLessEqual(actual,allowance)
 def test_verifier_without_optimum(self):
  with patch('experiment.riccati',side_effect=RuntimeError('unavailable')):
   self.assertLess(certify(self.m,self.K)['policy_gap_upper'],1e-8)
 def test_initial_action_radius(self):
  k=self.K+.03*np.eye(3);bound=certify(self.m,k)['policy_gap_upper'];rmin=np.diag(self.m['R'][0]).min()
  radius=math.sqrt(bound/(rmin*3))
  self.assertLessEqual(abs(np.sum(k[0]-self.K[0])/3),radius)

class LearningTests(unittest.TestCase):
 def test_gradient_by_difference(self):
  rng=np.random.default_rng(17);w=rng.normal(size=(3,3));p=np.eye(3);e=w.T@w-3*p;g=w@e
  h=1e-6
  for i in range(3):
   for j in range(3):
    a=w.copy();b=w.copy();a[i,j]+=h;b[i,j]-=h
    loss=lambda z:np.sum((z.T@z-3*p)**2)/4
    self.assertAlmostEqual((loss(a)-loss(b))/(2*h),g[i,j],places=5)
 def test_hidden_weights_trained(self):
  m=economy(3,'anchor',4);w,k=initial_state(3,4,17);p,_=evaluate(m,k)
  nw,_,_=fit_square_critic(w,p,3,32)
  self.assertGreater(np.linalg.norm(nw-w),1e-3)
 def test_seed_repeatable(self):
  a,k=initial_state(3,4,17);b,l=initial_state(3,4,17)
  self.assertTrue(np.array_equal(a,b));self.assertTrue(np.array_equal(k,l))
 def test_current_primitives_fixed(self):
  a=economy(3,'anchor',8)
  for r in ('technology','valuation'):
   b=economy(3,r,8)
   for n in ('A','B','Q','R'):self.assertTrue(np.array_equal(a[n][:4],b[n][:4]))
   self.assertTrue(any(not np.array_equal(a[n],b[n]) for n in ('A','Q')))
 def test_existing_output_refused(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(FileExistsError):run(Path(t),{})
 def test_failed_attempts_retained(self):
  design={'dimensions':[2],'horizon':3,'seeds':[17],'methods':['NBO-cold'],'regimes':['anchor'],'check_passes':[0,1],'gradient_steps_per_pass':1,'execution_error_budget':1e-12,'policy_tolerance':1e-100,'randomizer':'excluded development test'}
  with tempfile.TemporaryDirectory() as t,contextlib.redirect_stdout(io.StringIO()):
   p=Path(t)/'run';s=run(p,design)
   attempts=[json.loads(x) for x in (p/'attempts.jsonl').read_text().splitlines()]
   self.assertEqual(len(attempts),2);self.assertEqual(s['failed_checks'],2)
   self.assertTrue(all((p/a['candidate_file']).exists() for a in attempts))
 def test_factor_bound(self):
  m=economy(2,'anchor',4);k=riccati(m);p,_=evaluate(m,k)
  w=np.stack([np.linalg.cholesky(2*x).T for x in p[:-1]])
  f=factor_certificate(m,k,w,certify(m,k))
  self.assertTrue(f['rank_verified']);self.assertLess(f['factor_policy_gap_upper'],1e-8)
 def test_factor_rank_failure_preserved(self):
  m=economy(2,'anchor',4);k=riccati(m)
  f=factor_certificate(m,k,np.zeros((4,2,2)),certify(m,k))
  self.assertFalse(f['rank_verified']);self.assertIsNone(f['factor_policy_gap_upper'])

if __name__=='__main__':unittest.main()
