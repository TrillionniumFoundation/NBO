"""Algebraic regression tests, not independent economic observations."""
import unittest
from fractions import Fraction as F
import adaptive_refresh as a
r=a.r
class PrecisionTests(unittest.TestCase):
    def test_whole_step_budget(self):
        for e in (F(1,2),F(1,10),F(1,1000),F(1,10**12)):
            p=a.precision(e,m=F(3,2),rows=3,columns=2)
            self.assertLessEqual(p['c']*e*e+p['noise'],e*e)
    def test_minimal_registered_bits(self):
        p=a.precision(F(1,8),m=1,rows=2,columns=2)
        nu=p['relative_step_error']*2
        self.assertGreater(2*nu+nu*nu,(1-p['c'])*F(1,8)**2)
    def test_precision_increases(self):
        self.assertGreater(a.precision(F(1,10000),m=1,rows=2,columns=2)['bits'],a.precision(F(1,10),m=1,rows=2,columns=2)['bits'])
    def test_noise_nonnegative(self):
        p=a.precision(F(1,2),m=2,rows=3,columns=2)
        self.assertGreater(p['relative_step_error'],0)
    def test_zero_bound(self):
        with self.assertRaises(ValueError):a.precision(0,m=1,rows=2,columns=2)
    def test_invalid_basin(self):
        with self.assertRaises(ValueError):a.precision(F(3,4),m=1,rows=2,columns=2)
    def test_zero_floor(self):
        with self.assertRaises(ValueError):a.precision(F(1,2),m=0,rows=2,columns=2)
    def test_boolean_bits(self):
        with self.assertRaises(ValueError):a.precision(F(1,2),m=1,rows=2,columns=2,max_bits=True)
    def test_precision_exhaustion(self):
        with self.assertRaises(ArithmeticError):a.precision(F(1,10**30),m=1,rows=2,columns=2,max_bits=8)
    def test_wide_factor(self):
        with self.assertRaises(ValueError):a.precision(F(1,2),m=1,rows=1,columns=2)
class TargetTests(unittest.TestCase):
    def test_inverse_once(self):
        t=a.FixedTarget(r.eye(2,2),m=1); W=r.eye(2,F(7,5))
        for _ in range(4):W=t.apply(W)
        self.assertEqual(t.inverse_builds,1);self.assertEqual(t.solve_applications,4)
    def test_input_is_copied(self):
        M=r.eye(2,2);t=a.FixedTarget(M,m=1);M[0][0]=0
        self.assertEqual(t.target,r.eye(2,2))
    def test_return_is_copied(self):
        t=a.FixedTarget(r.eye(2,2),m=1);M=t.target;M[0][0]=0
        self.assertEqual(t.target,r.eye(2,2))
    def test_distinct_targets_have_distinct_cache(self):
        x=a.FixedTarget(r.eye(2,2),m=1);y=a.FixedTarget(r.eye(2,3),m=1)
        self.assertNotEqual(x.apply(r.eye(2)),y.apply(r.eye(2)))
        self.assertEqual((x.inverse_builds,y.inverse_builds),(1,1))
    def test_noncommuting_matches_uncached(self):
        M=r.matrix([[2,F(1,10)],[F(1,10),3]])
        W=r.matrix([[F(7,5),F(1,10)],[F(1,20),F(17,10)],[F(1,50),0]])
        self.assertEqual(a.FixedTarget(M,m=1).apply(W),a.qr.ideal_step(W,M))
    def test_singular_target(self):
        with self.assertRaises(ValueError):a.FixedTarget([[1,0],[0,0]],m=1)
    def test_nonsymmetric_target(self):
        with self.assertRaises(ValueError):a.FixedTarget([[2,1],[0,2]],m=1)
    def test_bad_factor_dimension(self):
        with self.assertRaises(ValueError):a.FixedTarget(r.eye(2),m=1).apply([[1,2]])
class RefreshTests(unittest.TestCase):
    M=r.eye(2,2)
    W=r.matrix([[F(7,5),F(1,30)],[F(-1,40),F(7,5)],[F(1,50),0]])
    def test_precision_adaptive_convergence(self):
        ans=a.refresh(self.W,self.M,m=F(3,2),tolerance=F(1,10**10))
        self.assertLessEqual(ans['relative_error_bound'],F(1,10**10))
        self.assertEqual(ans['inverse_builds'],1)
        self.assertEqual(ans['updates'],ans['solve_applications'])
    def test_exact_zero_update(self):
        ans=a.refresh(r.eye(2),r.eye(2),m=1,tolerance=F(1,100))
        self.assertEqual(ans['updates'],0);self.assertEqual(ans['inverse_builds'],0)
    def test_already_acceptable(self):
        ans=a.refresh(self.W,self.M,m=F(3,2),tolerance=1)
        self.assertEqual(ans['updates'],0)
    def test_doubly_exponential_envelope(self):
        ans=a.refresh(self.W,self.M,m=F(3,2),tolerance=F(1,10**12))
        for j,row in enumerate(ans['trace'],1):
            self.assertEqual(row['bound'],ans['initial_bound']**(2**j))
    def test_monotone_bit_allocation(self):
        ans=a.refresh(self.W,self.M,m=F(3,2),tolerance=F(1,10**10))
        bits=[v['bits'] for v in ans['trace']]
        self.assertEqual(bits,sorted(bits))
    def test_exact_final_loewner_check(self):
        ans=a.refresh(self.W,self.M,m=F(3,2),tolerance=F(1,10**8))
        H=r.mm(r.tr(ans['factor']),ans['factor']);b=ans['relative_error_bound']
        r.psd(r.add(H,r.scale(self.M,1-b),-1));r.psd(r.add(r.scale(self.M,1+b),H,-1))
    def test_outside_gate(self):
        with self.assertRaises(ValueError):a.refresh(r.eye(2,10),self.M,m=1,tolerance=F(1,100))
    def test_zero_tolerance(self):
        with self.assertRaises(ValueError):a.refresh(self.W,self.M,m=1,tolerance=0)
    def test_zero_update_budget(self):
        with self.assertRaises(ArithmeticError):a.refresh(self.W,self.M,m=F(3,2),tolerance=F(1,100000),max_updates=0)
    def test_exhausted_storage(self):
        with self.assertRaises(ArithmeticError):a.refresh(self.W,self.M,m=F(3,2),tolerance=F(1,100000),max_bits=2)
    def test_negative_update_budget(self):
        with self.assertRaises(ValueError):a.refresh(self.W,self.M,m=1,tolerance=1,max_updates=-1)
    def test_factor_input_preserved(self):
        W=[row[:] for row in self.W];a.refresh(W,self.M,m=F(3,2),tolerance=F(1,10000))
        self.assertEqual(W,self.W)
if __name__=='__main__': unittest.main()
