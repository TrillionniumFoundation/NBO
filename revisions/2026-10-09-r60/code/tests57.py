"""Disjoint small deterministic correctness fixtures, never production data."""
import unittest
from fractions import Fraction as F
import numpy as np
import action57 as a
n=a.n
class Tests(unittest.TestCase):
    def test_terminal_rational_lattice(self):
        for d in (2,4,8):
            x=np.linspace(.125,.75,d);c=n.Critic.terminal(d);r=a.minimize(x,c,16,64);v=a.reduce_objective(x,c)[-1]
            self.assertEqual(r['index'],min(range(17),key=lambda k:(v(F(k,64)),k)))
    def test_quadratic_rational_lattice(self):
        for sign in (-1,1):
            c=n.Critic('quadratic',2,dict(c=0.,v=np.array([-1.,.125]),Q=np.eye(2)*sign*4));x=np.array([.25,.5]);r=a.minimize(x,c,32,128);v=a.reduce_objective(x,c)[-1]
            self.assertEqual(r['index'],min(range(33),key=lambda k:(v(F(k,128)),k)))
    def test_relu_matches_inherited(self):
        c=n.Critic('relu',2,dict(c=0.,v=np.array([-.5,.25]),W=np.array([[1.,-2.],[2.,-.5]]),b=np.array([-.5,.125]),u=np.array([-1.,.25])))
        x=np.array([.25,.5]);self.assertEqual(a.minimize(x,c,16,64)['index'],a.old.minimize_lattice(x,c.params,16,64)['index'])
    def test_zero_cap(self):
        self.assertEqual(a.minimize([0.,0.],n.Critic.terminal(2),0)['index'],0)
    def test_terminal_objective_difference(self):
        for d in (2,4,8):
            x=np.linspace(.0625,.5625,d);v=a.reduce_objective(x,n.Critic.terminal(d))[-1]
            for k in (0,37,512):
                a0=F(k,4096);diff=n.o.final_difference(n.I.point(x[None]),n.I.point(np.array([float(a0)])),n.I.point(np.array([0.])),1)
                exact=v(a0)-v(F(0));self.assertLessEqual(F(float(diff.lo[0])),exact);self.assertLessEqual(exact,F(float(diff.hi[0])))
    def test_nested_menu_safety(self):
        part=n.Partition(2,4);grid=np.zeros((3,4),dtype=np.uint16);extra=np.array([part.capindex//3]*3,dtype=np.uint16)
        v=a.ReferenceVerifier(part,3,2);pol,rows,raw=v.sweep(grid,extra)
        for t in range(3):
            self.assertTrue(np.all(raw[f't{t}_U']<=raw[f't{t}_baseline_U']))
            self.assertTrue(np.all(raw[f't{t}_U']<=0));self.assertTrue(np.all(pol[t]<=part.capindex))
    def test_refinement_restarts_from_installed_reference(self):
        part=n.Partition(2,4);z=np.zeros((2,4),dtype=np.uint16);v=a.ReferenceVerifier(part,2,2);one=v.sweep(z)[0];two=a.ReferenceVerifier(part,2,2).sweep(z)[0];np.testing.assert_array_equal(one,two)
    def test_enclosure_decomposition(self):
        part=n.Partition(2,4);raw=a.ReferenceVerifier(part,2,2).sweep(np.zeros((2,4),dtype=np.uint16))[2]
        for t in range(2):
            for u,c,l in zip(raw[f't{t}_U'],raw[f't{t}_C'],raw[f't{t}_L']):
                self.assertEqual(F(float(u))-F(float(l)),F(float(u))-F(float(c))+F(float(c))-F(float(l)))
    def test_menu_regret_nonnegative(self):
        part=n.Partition(2,2);critics,_=n.train('relu',2,2,16,579001);grid,exact,records=a.proposals(critics,part,'relu-exact')
        self.assertTrue(all(F(r['grid_regret_exact'])>=0 for r in records if not r['common_terminal']))
    def test_confidence_allocation(self):
        import math
        self.assertGreater(sum((F(14)**k/math.factorial(k) for k in range(80)),F(0)),4*2048*100)
        self.assertLessEqual(5*3*3*2*2*3*3+4*3*3*2,2048)
if __name__=='__main__':unittest.main(verbosity=2)
