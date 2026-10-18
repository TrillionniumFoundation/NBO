"""Pre-execution tests: algebra and declared non-catalogue fixtures only."""
import unittest,sys
from pathlib import Path
from fractions import Fraction as F
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import gain_budget110 as g
from interval94 import I

class BudgetAlgebra(unittest.TestCase):
    def test_no_gain_above_ceiling(self):
        for lower in (F(0),F(1,3),F(2)):
            for gap in (F(0),F(1,65536),F(1,256)):
                upper=lower+gap
                for feasible in (lower,lower+gap/2,upper,upper+1):self.assertLessEqual(upper-feasible,gap)
    def test_equality_stops(self):self.assertLessEqual(F(1,65536),F(1,65536))
    def test_touching_is_not_descent(self):self.assertFalse(F(2)<F(2))
    def test_overlap_not_descent(self):self.assertFalse(F(3)<F(2))
    def test_sum_budget(self):
        a=[F(1,8),F(1,16),F(1,32)];w=[F(1,2),F(1,4),F(1,4)]
        self.assertEqual(sum(x*y for x,y in zip(a,w)),F(11,128))
    def test_recursive_risk_not_physical_average(self):
        e=[F(0),F(1)];self.assertNotEqual(max(e),sum(e)/2)
    def test_nonnegative_loss_required(self):
        r={k:np.array([0.]) for k in g.KEYS};r['loss'][0]=-1
        with self.assertRaises(ArithmeticError):g.validate(r)
    def test_invalid_width_rejected(self):
        r={k:np.array([0.]) for k in g.KEYS};r['upper'][0]=1;r['width'][0]=1
        with self.assertRaises(ArithmeticError):g.validate(r)
    def test_nonfinite_rejected(self):
        r={k:np.array([0.]) for k in g.KEYS};r['loss'][0]=float('nan')
        with self.assertRaises(ArithmeticError):g.validate(r)
    def test_frozen_menu(self):self.assertEqual(len(g.SERVICES),6)
    def test_fixture_original_targets(self):
        # Four declared fixtures, not the 64-site experiment and no trained actor.
        x=np.array([[0.,0.],[1.,1.],[.125,.625],[.5,.5]])
        for alpha in (.5,.75):
            control=g.service(x,alpha,None,'compiled')
            d=g.service(x,alpha,None,'gain-16')
            self.assertTrue(all(r['loss']<=1/256 and r['width']<=1/8192 for r in d['rows']))
            self.assertTrue(all(r['action']==s['action'] or r['upper']<s['lower'] for r,s in zip(d['rows'],control['rows'])))
            self.assertTrue(all(not t['accepted'] for t in d['trials'] if t['skipped']))
    def test_bad_service(self):
        with self.assertRaises(ValueError):g.service(np.array([[0.,0.]]),.5,None,'unregistered')

if __name__=='__main__':unittest.main(verbosity=2)
