"""Preflight only: algebra and independent source fixtures, not primary data."""
import unittest,json,sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import exact117 as ex
import precision117 as p

class Preflight(unittest.TestCase):
    def test_exact_references(self):
        for name in ex.NAMES:
            for alpha in (F(0),F(1,4),F(1,2),F(3,4)):
                self.assertEqual(ex.reference(name,alpha),ex.independent_reference(name,alpha))
    def test_algebraic_action_loss(self):
        for theta in (F(0),F(1,3),F(7,8),F(5,4)):
            star=F(1,2)-ex.BETA*theta/ex.MU
            for a in (F(0),F(1,4),F(1,2),F(1)):
                self.assertEqual(ex.objective(a,theta)-ex.objective(star,theta),4*(a-star)**2)
    def test_enclosures(self):
        for name in ex.NAMES:
            oracle=ex.Oracle(name)
            for n in (4,8):
                lo,hi=ex.interval(oracle,F(1,2),n)
                self.assertLessEqual(lo,ex.reference(name,F(1,2)))
                self.assertGreaterEqual(hi,ex.reference(name,F(1,2)))
            self.assertEqual(len(oracle.cache),17)
    def test_rounding_allowance(self):
        for theta in (F(1,3),F(3,5)):
            lo,hi=theta-F(1,128),theta+F(1,128)
            a=ex.action(lo,hi);star=F(1,2)-ex.BETA*theta/ex.MU
            self.assertLessEqual(4*(a-star)**2,ex.certificate(lo,hi))
    def test_invalid_exact_input(self):
        with self.assertRaises(ValueError):ex.certificate(F(1),F(0))
        with self.assertRaises(ValueError):ex.interval(ex.Oracle('linear'),F(1,2),3)
    def test_feasible_boundaries(self):
        self.assertEqual(ex.action(F(8),F(8)),F(0))
        self.assertEqual(ex.action(F(-8),F(-8)),F(1))
    def test_control_refactor(self):
        x=np.array([[1/7,2/7],[3/11,7/11],[13/17,2/17]])
        for alpha in (.5,.75):
            a=p.base.complete_service(x,alpha,None,compiled=True,safe=False)
            b=p.service(x,alpha,None,ladder=False)
            for aa,bb in zip(a['rows'],b['rows']):
                for key in ('action','proposed','bins','exact_fallback',*p.KEYS):
                    self.assertEqual(aa[key],bb[key])
            self.assertEqual(a['counts'],b['counts'])
    def test_ladder_paid_and_qualified(self):
        x=np.array([[2/13,3/13],[8/13,11/13]])
        for alpha in (.5,.75):
            data=p.service(x,alpha,None)
            self.assertGreaterEqual(data['counts']['r96_original_action_certificates'],2)
            for row in data['rows']:
                self.assertLessEqual(row['loss'],1/256);self.assertLessEqual(row['width'],1/8192)
                self.assertGreaterEqual(F(row['action_distance_upper'])**2,F(row['loss']))
            self.assertFalse(data['cache_used'])
    def test_empty_rejected(self):
        with self.assertRaises(ValueError):p.service(np.empty((0,2)),.5,None)
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):p.service([[np.nan,0]],.5,None)
    def test_evaluation_grids_disjoint(self):
        def sites(n):return {(F(2*i+1,2*n),F(2*j+1,2*n)) for i in range(n) for j in range(n)}
        self.assertFalse(sites(12)&sites(16));self.assertFalse(sites(12)&sites(8))
    def test_regret_information_minimax_pair(self):
        low,high=F(1,3),F(2,3);estimate=(low+high)/2
        a=F(1,2)-ex.BETA*estimate/ex.MU
        errors=[ex.objective(a,t)-ex.objective(F(1,2)-ex.BETA*t/ex.MU,t) for t in (low,high)]
        self.assertEqual(max(errors),ex.BETA**2*(high-low)**2/(8*ex.MU))

if __name__=='__main__':unittest.main(verbosity=2)
