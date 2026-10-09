"""Exact multiple-root regressions for the neural action-witness theorem."""
from fractions import Fraction as F
import unittest
import algebraic56 as a
class MultipleRoots(unittest.TestCase):
    def test_double_and_triple_stationary_roots(self):
        # Both critics remain in one quadratic hinge region over [0, 1/4].
        # Their exact objective derivatives are respectively 16 a^3 and
        # 16(a-1/8)^2(a+1/4); every coefficient is dyadic.
        for u,b,v in [(-8,F(37,16),24),(-11,F(-37,32),6)]:
            params=dict(c=F(0),v=[F(v),F(0)],W=[[F(49)],[F(-86)]],b=[b],u=[F(u)])
            z=a.minimize_lattice([F(0),F(0)],params,32,128)
            value=a.reduce_critic([F(0),F(0)],params)[-1]
            exact=min(range(33),key=lambda k:(value(F(k,128)),k))
            self.assertEqual(z['index'],exact)
            self.assertGreaterEqual(z['isolated_roots'],1)
            self.assertEqual(z['pieces'],1)
if __name__=='__main__':unittest.main(verbosity=2)
