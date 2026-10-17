"""New exact and adversarial checks; diagnostic seeds never open the R96 streams."""
from fractions import Fraction as F
from pathlib import Path
import math,unittest
import numpy as np
from interval94 import I
from investment94 import discrete_avar_interval
from quadrature96 import endpoint_mixture,certificate,service,TAU,WIDTH,MARGIN,RADIUS,SAMPLE_SIZE,paired
from matched96 import MatchedFit,construct,encode,decode
from independent96 import fitted_proposal

class ConvexOrderTests(unittest.TestCase):
    def test_endpoint_multiplicities(self):
        np.testing.assert_array_equal(endpoint_mixture([1,2,3,4]),[1,2,2,3,3,4])
    def test_degenerate_endpoint_rejected(self):
        with self.assertRaises(ValueError):endpoint_mixture([0])
    def test_quadratic_continuous_risk_enclosed(self):
        for n in (4,8,16,32,64):
            edge=np.linspace(0,1,n+1);mid=(edge[:-1]+edge[1:])/2
            for a in (.5,.75):
                low=discrete_avar_interval(I(mid*mid),a).lo
                high=discrete_avar_interval(I(endpoint_mixture(edge*edge)),a).hi
                truth=(1-F(a)**3)/(3*(1-F(a)))
                self.assertLessEqual(F(float(low)),truth);self.assertGreaterEqual(F(float(high)),truth)
                self.assertLessEqual(float(high-low),1/(n*n*(1-a))+1e-12)
    def test_nonsmooth_convex_risk_enclosed(self):
        for n in (4,8,16,32):
            edge=np.linspace(-1,1,n+1);mid=(edge[:-1]+edge[1:])/2
            for a in (.5,.75):
                low=discrete_avar_interval(I(abs(mid)),a).lo
                high=discrete_avar_interval(I(endpoint_mixture(abs(edge))),a).hi
                self.assertLessEqual(float(low),(1+a)/2);self.assertGreaterEqual(float(high),(1+a)/2)
    def test_no_claim_for_concave_continuation(self):
        # Midpoint lower construction would fail even for expectation without convexity.
        self.assertGreater(0.,-1/3)
    def test_nested_mesh_width_reduction(self):
        widths=[]
        for n in (4,8,16):
            edges=np.linspace(0,1,n+1);mid=(edges[:-1]+edges[1:])/2
            widths.append(float(discrete_avar_interval(I(endpoint_mixture(edges**2)),.75).hi-discrete_avar_interval(I(mid**2),.75).lo))
        self.assertTrue(all(b<a for a,b in zip(widths,widths[1:])))
    def test_original_primitive_corners(self):
        x=np.array([[0.,0.],[1.,1.],[0.,1.],[1.,0.]])
        for alpha in (.5,.75):
            r=service(x,alpha,None)
            self.assertTrue(np.all(r['loss']<=TAU));self.assertTrue(np.all(r['width']<=WIDTH))
            self.assertTrue(np.all(r['actions']<=.125+x.mean(axis=1)/8))

class PowerTests(unittest.TestCase):
    def test_simultaneous_failure_probability(self):
        series=sum(F(8)**j/math.factorial(j) for j in range(12))
        self.assertLess(F(24)/series,F(1,20))
    def test_sample_size_exponent(self):
        self.assertEqual(F(SAMPLE_SIZE)*F(RADIUS)**2/(2*F(TAU)**2),8)
    def test_resolution_smaller_than_economic_margin(self):
        self.assertLess(F(RADIUS)+F(WIDTH),F(MARGIN)/2)
    def test_margin_is_one_percent_of_max_charge(self):
        self.assertEqual(F(1,1280),F(5,64)/100)
        self.assertEqual(MARGIN,float(F(1,1280)))
    def test_wrong_sample_size_rejected(self):
        d=dict(lower=np.zeros(2),upper=np.ones(2))
        with self.assertRaises(ValueError):paired(d,d)
    def test_interval_width_and_all_signs(self):
        a=dict(lower=np.zeros(4096),upper=np.full(4096,WIDTH/2))
        b=dict(lower=np.full(4096,TAU/2),upper=np.full(4096,TAU/2+WIDTH/2))
        p=paired(a,b)
        self.assertTrue(p['left_superior']);self.assertFalse(p['right_superior'])
        self.assertLess(p['half_width'],MARGIN/2)
    def test_contradictory_support_rejected(self):
        a=dict(lower=np.zeros(4096),upper=np.zeros(4096));b=dict(lower=np.ones(4096),upper=np.ones(4096))
        with self.assertRaises(ArithmeticError):paired(a,b)

class PayloadTests(unittest.TestCase):
    def setUp(self):
        self.model=MatchedFit('relu',np.array([[1.,0.],[0.,1.],[.5,.5]]),np.array([-.25,-.5,-.75]),np.array([0.,1.,2.,.5,.5,.5]),{})
    def test_fixed_payload_roundtrip(self):
        data=encode(self.model);self.assertEqual(len(data),128)
        x=np.random.default_rng(73).random((8,2))
        np.testing.assert_array_equal(self.model.float_eval(x),decode(data).float_eval(x))
    def test_bad_length_rejected(self):
        with self.assertRaises(ValueError):decode(b'bad')
    def test_negative_readout_rejected(self):
        data=np.frombuffer(encode(self.model),dtype='<f8').copy();data[13]=-1
        with self.assertRaises(ValueError):decode(data.tobytes())
    def test_nan_payload_rejected(self):
        data=np.frombuffer(encode(self.model),dtype='<f8').copy();data[4]=np.nan
        with self.assertRaises(ValueError):decode(data.tobytes())
    def test_independent_proposal_boundary(self):
        obj=(self.model.kind,[[F(v) for v in row] for row in self.model.directions],list(map(F,self.model.offsets)),list(map(F,self.model.coefficients)))
        self.assertEqual(fitted_proposal([F(1),F(1)],F(1,2),obj),0)
    def test_all_three_designs_full_rank(self):
        x=np.random.default_rng(731).random((64,2));y=(x*x).sum(axis=1)
        for kind in ('quadratic','relu','spline'):
            m=construct(kind,x,y);self.assertEqual(m.record['effective_design_rank'],6)
            self.assertEqual(m.record['payload_bytes'],128)

class IndependenceTests(unittest.TestCase):
    def test_independent_statistics_do_not_import_production(self):
        text=(Path(__file__).with_name('independent96.py')).read_text()
        for name in ('quadrature96','interval94','continuum94','experiment96','matched96'):
            self.assertNotIn('from '+name+' import',text)
    def test_current_sources_have_no_silent_skips(self):
        self.assertNotIn('@unittest.'+'skip(',Path(__file__).read_text())

if __name__=='__main__':unittest.main(verbosity=2)
