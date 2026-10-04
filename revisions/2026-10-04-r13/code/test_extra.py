"""Regression tests for issues exposed by development and interval aggregation."""
import math,unittest
from common import *
import evaluation
class ExtraTests(unittest.TestCase):
    def test_small_deployment_batch(self):
        x=np.arange(640,dtype=float).reshape(64,10);y=evaluation.benchmark_batch(x);self.assertEqual(y.shape,(256,11));np.testing.assert_array_equal(y[:64,1:],x);np.testing.assert_array_equal(y[64:128,1:],x)
    def test_empty_deployment_batch(self):
        with self.assertRaises(ValueError):evaluation.benchmark_batch(np.empty((0,10)))
    def test_scalar_account_explicit_domain(self):
        with self.assertRaisesRegex(ValueError,'scalar HJB'):evaluation.account(1,32,.1,'origin')
    def test_interval_fee(self):
        rows,ceiling=evaluation.fee_account(dict(lower=.001,upper=.003));A=-math.expm1(-P['discount']*P['T'])/P['discount']
        for r in rows:
            self.assertLessEqual(r['lower'],.001+A*math.log1p(-r['rate']));self.assertGreaterEqual(r['upper'],.003+A*math.log1p(-r['rate']))
        self.assertLessEqual(ceiling,-math.expm1(-.001/A))
    def test_population_interval_average(self):
        _,c=evaluation.account(10,32,.1,'population');ordinary=sum(r['bias_upper'] for r in c['components'])/9
        self.assertGreaterEqual(c['bias_upper'],ordinary)
if __name__=='__main__':unittest.main(verbosity=2)
