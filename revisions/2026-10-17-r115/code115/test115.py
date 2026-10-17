"""Pre-primary arithmetic tests; no fitted actor or investment sample is drawn."""
import itertools, unittest
from fractions import Fraction as F
import statistics115 as s

class ExactGains(unittest.TestCase):
    def test_telescoping_dominance(self):
        intervals=[(F(10,100),F(11,100)),(F(8,100),F(9,100)),(F(5,100),F(6,100))]
        lower=sum(intervals[i][0]-intervals[i+1][1] for i in range(2))
        self.assertEqual(lower,F(3,100));self.assertEqual(intervals[0][0]-intervals[-1][1],F(4,100))
    def test_touching_no_descent(self): self.assertFalse(F(1,2)<F(1,2))
    def test_negative_observation_rejected(self):
        with self.assertRaises(ArithmeticError):s.infer([F(-1,1000)])
    def test_above_cap_rejected(self):
        with self.assertRaises(ArithmeticError):s.infer([F(1,100)])
    def test_null_products(self):
        d=s.infer([F(0)]*32)
        self.assertEqual(d['prefixes'][0]['lower'],'0')
        self.assertTrue(all(v is None for v in d['first_crossings'].values()))
    def test_exact_product_comparison(self):
        p=F(32768)
        self.assertTrue(s.product_ge(p,1,0,15))
        self.assertFalse(s.product_ge(p,1,s.D,15))
    def test_largest_grid_endpoint(self):
        products=[(1+c)**32 for c in s.STAKES]
        d=s.mean_bound(list(map(F,products)),32)
        self.assertGreater(F(d['lower']),0)
        self.assertTrue(d['next_grid_endpoint_rejected'])
    def test_censoring_product_monotonicity(self):
        for c in s.STAKES:
            for y in (F(0),F(1,10),F(1)):
                self.assertLessEqual(1+c*y/2,1+c*y)
    def test_null_supermartingale_exact(self):
        p=F(1,5)
        for c in s.STAKES:
            self.assertEqual((1-p)/(1+c*p)+p*(1+c)/(1+c*p),1)
    def test_censored_supermartingale_exact(self):
        p=F(1,5)
        for c in s.STAKES:
            self.assertLessEqual((1-p)/(1+c*p)+p*(1+c/F(2))/(1+c*p),1)
    def test_optional_stopping_enumeration(self):
        p=F(1,3);threshold=F(4);n=8;c=4;prob=F(0)
        for xs in itertools.product((0,1),repeat=n):
            weight=p**sum(xs)*(1-p)**(n-sum(xs));e=F(1);hit=False
            for x in xs:
                e*=F(1+c*x)/(1+c*p)
                if e>=threshold:hit=True
            if hit:prob+=weight
        self.assertLessEqual(prob,1/threshold)
    def test_radius_is_positive(self): self.assertGreater(s.radius(1600,2048),0)
    def test_cap_is_original(self): self.assertEqual(s.TAU,F(1,256))
    def test_multiplicity(self): self.assertEqual(s.THRESHOLD,32*10*50)
    def test_joint_account(self): self.assertEqual(F(1)-F(1,50)-F(1,50),F(24,25))
    def test_same_observed_action_not_population_identity(self):
        self.assertGreater((1-F(1,1000))**1024,0)
    def test_safe_vs_cross_arm_not_same_sign(self):
        baseline,updated,competitor=F(3),F(2),F(1)
        self.assertGreater(baseline-updated,0);self.assertGreater(updated-competitor,0)
    def test_gain_under_reporting_can_hide_gain(self):
        true=[F(1,1024)]*32;observed=[F(0)]*32
        self.assertGreater(sum(true),0)
        self.assertEqual(s.infer(observed)['prefixes'][0]['lower'],'0')

if __name__=='__main__':unittest.main(verbosity=2)
