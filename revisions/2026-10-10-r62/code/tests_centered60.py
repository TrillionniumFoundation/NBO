"""Disjoint exact checks for the common-reference Bellman bracket."""
from fractions import Fraction as F
import unittest
import numpy as np
import centered60 as c


def transition(x,a,z):return [F(1,16)+x[j]/2+x[1-j]/8+x[j]*(1-x[1-j])/16+(F(1,2) if j==0 else F(1,4))*a+(z if j==0 else -z) for j in range(2)]
def cost(x,terminal=False):return (2 if terminal else 1)*sum((y-F(5,8))**2 for y in x)+(x[0]-x[1])**2/4+2*max(F(0),F(1,2)-sum(x))**2

def true_advantage(x,a):
    def integrand(z):
        y=transition(x,a,z);b=transition(x,F(0),z)
        yy=transition(y,F(0),F(0));bb=transition(b,F(0),F(0))
        # Both terminal shortages are inactive throughout these disjoint fixtures.
        if min(sum(yy),sum(bb))<=F(1,2):raise AssertionError('Fixture crosses terminal shortage kink')
        return cost(y)-cost(b)+F(c.n.BETA)*(cost(yy,True)-cost(bb,True))
    r=F(1,32);z=(-r,-r/2,F(0),r/2,r);weights=(7,32,12,32,7)
    mean=sum(w*integrand(v) for w,v in zip(weights,z))/90
    return a*a+4*a**4+F(c.n.BETA)*mean

class CenteredTests(unittest.TestCase):
    def test_initial_advantage_contains_exact_original_expectation(self):
        for state in ((F(3,4),F(1,2)),(F(7,8),F(5,8)),(F(1,2),F(3,4))):
            for a in (F(0),F(1,16),F(1,8),F(3,16)):
                x=c.I.point(np.array([list(map(float,state))]));action=c.I.point(np.array([float(a)]));v=c.advantage_and_offset(x,action,0,8)
                exact=true_advantage(state,a)
                self.assertLessEqual(F(v.lo[0]),exact);self.assertGreaterEqual(F(v.hi[0]),exact)
    def test_terminal_advantage_contains_exact_difference(self):
        for state in ((F(1,8),F(1,8)),(F(1,2),F(3,4))):
            x=c.I.point(np.array([list(map(float,state))]));a=F(1,8)
            value=c.advantage_and_offset(x,c.I.point(np.array([float(a)])),1,4)
            ya=transition(state,a,F(0));yb=transition(state,F(0),F(0))
            exact=a*a+4*a**4+F(c.n.BETA)*(cost(ya,True)-cost(yb,True))
            self.assertLessEqual(F(value.lo[0]),exact);self.assertGreaterEqual(F(value.hi[0]),exact)
    def test_zero_difference_is_exact_before_continuation(self):
        x=c.I(np.array([[.2,.4]]),np.array([[.3,.5]]));zero=c.I.point(np.array([0.]))
        for t in (0,1):
            v=c.advantage_and_offset(x,zero,t,4)
            self.assertLessEqual(v.lo[0],0);self.assertGreaterEqual(v.hi[0],0)
            self.assertLessEqual(v.hi[0]-v.lo[0],1e-300)
    def test_shifted_certificate_order_and_robust_feasibility(self):
        record,arrays=c.rung(4,4,2)
        self.assertTrue(np.all(arrays['lower_excess']<=arrays['upper_excess']))
        self.assertTrue(np.all(arrays['upper_excess']<=0))
        self.assertTrue(np.all(arrays['policy']<=arrays['capindex']))
        self.assertGreaterEqual(record['maximum_date_gap_upper'],0)
    def test_constant_reference_shift_cancels_from_width(self):
        lower=F(-3,8);upper=F(-1,8)
        for reference in (F(-100),F(0),F(1234567,19)):
            self.assertEqual((reference+upper)-(reference+lower),upper-lower)

if __name__=='__main__':unittest.main(verbosity=2)
