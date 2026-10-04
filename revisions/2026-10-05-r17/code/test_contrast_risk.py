"""Exact manufactured checks. These are not observations from the NBO study."""
import itertools, json, math, tempfile, unittest
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from contrast_risk import (I,pc,statistics,exact_contrast,two_action_regret,seed_for,
    risk_account,protocols,load_economy,fixed_queries,geometry)

class ContrastTests(unittest.TestCase):
    def test_01_exact_identity(self):
        for a,b,z in itertools.product(map(F,[-3,-1,0,2,5]),repeat=3):
            self.assertEqual(exact_contrast(a,b,z),(a-z)**2-(b-z)**2)
    def test_02_unbiased_finite_law(self):
        a,b=F(4,5),F(9,10);zs=[F(-2),F(4)];mu=sum(zs)/2
        self.assertEqual(sum(exact_contrast(a,b,z) for z in zs)/2,(a-mu)**2-(b-mu)**2)
    def test_03_cancellation_precision(self):
        a,b=F(4,5),F(9,10);zs=[F(-2),F(4)]
        def var(v):
            m=sum(v)/len(v);return sum((x-m)**2 for x in v)/len(v)
        shared=[exact_contrast(a,b,z) for z in zs]
        independent=[(a-z1)**2-(b-z2)**2 for z1,z2 in itertools.product(zs,repeat=2)]
        self.assertLess(var(shared),var(independent))
    def test_04_identical_predictors_exact_zero(self):
        for x in [-1e100,0,1e100]:self.assertEqual(exact_contrast(x,x,2.),0.)
    def test_05_shift_invariance(self):
        self.assertEqual(exact_contrast(F(1),F(2),F(3)),exact_contrast(F(101),F(102),F(103)))
    def test_06_antisymmetry(self):
        self.assertEqual(exact_contrast(F(1,7),F(3,5),F(2)), -exact_contrast(F(3,5),F(1,7),F(2)))
    def test_07_two_bank_absolute_risk(self):
        zs=[F(-2),F(4)];p=F(4,5)
        value=sum((p-z1)*(p-z2) for z1,z2 in itertools.product(zs,repeat=2))/4
        self.assertEqual(value,(p-F(1))**2)
    def test_08_single_bank_square_has_noise(self):
        self.assertEqual(sum((F(1)-z)**2 for z in [F(-2),F(4)])/2,F(9))
    def test_09_two_action_decision_bound(self):
        for reward,c,p in itertools.product(np.arange(-2,2.1,.25),repeat=3):
            self.assertLessEqual(two_action_regret(reward,c,p),abs(p-c)+1e-14)
    def test_10_risk_order_not_payoff_order(self):
        # The more accurate predictor crosses the wrong decision boundary.
        self.assertLess((-.01-.01)**2,(.2-.01)**2)
        self.assertGreater(two_action_regret(0,.01,-.01),two_action_regret(0,.01,.2))
    def test_11_domains_are_disjoint(self):
        keys=[seed_for(s,c,d,k) for s in [0,1,2] for c in ['a','b'] for d in [10,50]
              for k in ['cached-raw-before-audit','independent-risk-audit']]
        self.assertEqual(len(keys),len(set(keys)))
    def test_12_zero_interval(self):
        x=statistics.empirical_bernstein([0.,0.],bound=0,event_alpha=.01)
        self.assertEqual((x['lower'],x['upper']),(0.,0.))
    def test_13_no_seed_attrition(self):
        with self.assertRaises(ValueError):
            statistics.finite_stream_mean({1:[0.,0.]},declared_seeds=[1,2],noise_keys={1:'x'},
                bounds={1:1.},biases={1:0.},clipping_tails={1:0.},event_alpha=.01,
                confirmation_independent_of_selection=True)
    def test_14_no_pseudoreplication(self):
        with self.assertRaises(ValueError):
            statistics.finite_stream_mean({s:[0.,0.] for s in [1,2]},declared_seeds=[1,2],
                noise_keys={1:'same',2:'same'},bounds={1:1.,2:1.},biases={1:0.,2:0.},
                clipping_tails={1:0.,2:0.},event_alpha=.01,confirmation_independent_of_selection=True)
    def test_15_risk_numeric_account(self):
        g=dict(center=[.25,.25],bounds=[2.,2.],tails=[1e-10,1e-10],evaluation_bias_upper=[1e-12,1e-12])
        acc=risk_account({'geometry':g},{'nbo_prediction':np.array([.125,1.]),'raw_4':np.array([.5,1.])},4)
        self.assertEqual(acc['bounds'][1],0.)
        for z in np.linspace(-2,2,101):
            exact=exact_contrast(F(.125),F(.5),F(.25)+F(float(z)))
            estimate=float((acc['known_lower'][0]+acc['known_upper'][0])/2)+acc['coefficient'][0]*z
            self.assertLessEqual(abs(estimate-float(exact)),acc['bias'][0]+1e-15)
    def test_16_family_and_margin(self):
        old,p=protocols();self.assertEqual(p['event_count'],len(old['calibrations'])*len(old['dimensions'])*len(p['raw_paths']))
        self.assertEqual(p['audit_pairs'],256);self.assertEqual(p['risk_margin'],1e-8)
        self.assertLessEqual(statistics.ConfidenceBudget(p['alpha'],p['event_count']).event_alpha*p['event_count'],p['alpha'])
    def test_17_geometry_identity(self):
        old,_=protocols();e=load_economy(old,'original_low',10);q=fixed_queries(old,10)
        a=np.full_like(q['states'],e.schedule[0]);g,xa,xb=geometry(e,q,a)
        self.assertTrue(np.array_equal(xa,xb));self.assertEqual(max(g['bounds']),0.);self.assertEqual(max(g['evaluation_bias_upper']),0.)
    def test_18_geometry_nonzero(self):
        old,_=protocols();e=load_economy(old,'original_low',10);q=fixed_queries(old,10)
        a=np.full_like(q['states'],e.schedule[0]);a[:,0]+=1e-4;g,xa,xb=geometry(e,q,a)
        self.assertTrue(np.all(np.asarray(g['bounds'])>0));self.assertTrue(np.isfinite(g['evaluation_bias_upper']).all())

if __name__=='__main__':unittest.main(verbosity=2)
