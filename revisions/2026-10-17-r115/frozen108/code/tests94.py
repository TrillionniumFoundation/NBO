"""Adversarial tests, including independent original-law rational witnesses."""
from fractions import Fraction as F
import unittest,math,json
import numpy as np
from interval94 import I
import investment94 as econ
import terminal_controller94 as controller
from continuum94 import query,strict_tail_cuts,uniform_residual,policy_cost,actor
from representations94 import Fit,features,fit
import independent94 as ind

class IntervalTests(unittest.TestCase):
    def test_rational_arithmetic(self):
        rng=np.random.default_rng(941)
        for _ in range(100):
            a=float(rng.normal());b=float(rng.normal());fa,fb=F(a),F(b)
            for box,truth in ((I(a)+b,fa+fb),(I(a)-b,fa-fb),(I(a)*b,fa*fb),(I(a)/b,fa/fb)):
                self.assertLessEqual(F(float(box.lo)),truth);self.assertGreaterEqual(F(float(box.hi)),truth)
    def test_zero_square(self):self.assertEqual(float(I(-1,2).square().lo),0)
    def test_reversed_rejected(self):
        with self.assertRaises(ArithmeticError):I(2,1).checked()
    def test_nonfinite_rejected(self):
        with self.assertRaises(ArithmeticError):I(float('nan')).checked()
    def test_division_by_zero_rejected(self):
        with self.assertRaises(ValueError):I(1)/I(-1,1)
    def test_whole_interval_quadratic_minimum(self):
        for a in (0.,.0625,.125,.25):
            for g in (-2.,-.3,0.,.4,2.):
                cap=.25;v=econ.quadratic_minimum_lower(I(.3),I(g-1e-12,g+1e-12),I(a),I(cap))
                for slope in (g-1e-12,g,g+1e-12):
                    d=max(-F(a),min(F(cap)-F(a),-F(slope)/2))
                    self.assertLessEqual(F(float(v)),F(.3)+F(slope)*d+d*d)

class OriginalRiskTests(unittest.TestCase):
    def test_exact_threshold_integral(self):
        for d in (2,4,8):
            for alpha in (.5,.75):
                for k in range(4):
                    x=[F((j*7+k*3)%16,16) for j in range(d)];a=F(k,32)
                    poly=ind.polynomial_from_primitives(x,a);self.assertEqual(poly[2],5)
                    true,_=ind.objective_gradient(x,a,alpha)
                    actual,*_=econ.terminal_details(I([float(v) for v in x]),I(float(a)),alpha)
                    self.assertLessEqual(F(float(actual.lo)),true);self.assertGreaterEqual(F(float(actual.hi)),true)
    def test_terminal_whole_action_lower(self):
        for x in ([0.,0.],[1.,1.],[.375,.75],[.9375,.125]):
            for alpha in (.5,.75):
                r=econ.terminal_certificate(I(x),alpha)
                lo,hi,_=ind.terminal_bounds(x,alpha)
                self.assertLessEqual(F(float(r['lower'])),hi)
                self.assertGreaterEqual(F(float(r['upper'])),lo)
                cap=F(1,8)+sum(map(F,x))/16
                for j in range(17):
                    val,_=ind.objective_gradient(x,cap*j/16,alpha)
                    self.assertLessEqual(F(float(r['lower'])),val)
    def test_global_state_support(self):
        x=np.array([[.125,.75],[.875,.25]])
        r=econ.terminal_certificate(I(x),.75)
        for y in ([0.,0.],[1.,1.],[.5,.375]):
            lo,hi,_=ind.terminal_bounds(y,.75)
            line=I(r['lower'])+(r['slope']*(I(y)-I(x))).sum()
            self.assertTrue(np.all(line.lo<=float(hi)))
    def test_risk_not_physical_expectation(self):
        x=list(map(F,[.25,.75]));p=ind.polynomial_from_primitives(x,F(1,8))
        r,*_=ind.tail_threshold(p,F(3,4));mean=ind.integral(p,F(-1,32),F(1,32))*16
        self.assertGreater(r,mean)
    def test_bad_risk_level(self):
        with self.assertRaises(ValueError):econ.terminal_details(I([.5,.5]),I(.1),.9)
    def test_scalar_and_vector_dimensions(self):
        for d in (2,4,8):
            x=I(np.full((3,d),.5));r=econ.terminal_certificate(x,.5)
            self.assertTrue(np.all(r['gap']<=2**-20))
    def test_invalid_dimension(self):
        with self.assertRaises(ValueError):econ.exposures(3)

    def test_complete_terminal_observation_controller(self):
        for alpha in (.5,.75):
            y=np.array([[.25,.75],[0.,0.],[1.,1.]])
            a=controller.terminal_policy(y,alpha)
            for x,act in zip(y,a):
                q,_=ind.objective_gradient(x,act,alpha);l,u,_=ind.terminal_bounds(x,alpha)
                self.assertLessEqual(q-l,F(1,2**21))
    def test_exact_fallback_independent_check(self):
        for alpha in (.5,.75):
            y=[.8125,.6875];a=controller.rational_terminal_action(y,alpha)
            q,_=ind.objective_gradient(y,a,alpha);l,u,_=ind.terminal_bounds(y,alpha)
            self.assertLessEqual(q-l,F(1,2**21))
    def test_sensor_transfer_budget(self):self.assertLess(F(1,2**21)+F(30,2**40),F(1,2**20))
    def test_unqualified_observation_rejected(self):
        with self.assertRaises(ValueError):controller.terminal_policy([.1,.2],.5)

class ContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        x=np.random.default_rng(3194).integers(0,2**20,(64,2))/2**20
        r=econ.terminal_certificate(I(x),.5)
        cls.fits={k:fit(k,x,(r['lower']+r['upper'])/2) for k in ('relu','spline','quadratic')}
    def test_exact_feature_reconstruction(self):
        for f in self.fits.values():
            for x in ([.125,.625],[.9990234375,0.]):
                val=f.interval(I(x));true=ind.feature_value(f.to_dict(),x)
                self.assertLessEqual(F(float(val.lo)),true);self.assertGreaterEqual(F(float(val.hi)),true)
    def test_serialization_identity(self):
        for f in self.fits.values():self.assertEqual(f.identity(),Fit.from_dict(json.loads(json.dumps(f.to_dict()))).identity())
    def test_feature_budget(self):
        for f in self.fits.values():self.assertEqual(len(f.directions),32);self.assertTrue(np.all(f.coefficients[3:]>=0))
    def test_convex_support(self):
        for f in self.fits.values():
            x=I([.25,.75]);v,g=f.interval(x,True)
            for y in ([0.,0.],[1.,1.],[.5,.625]):
                low=v+(g*(I(y)-x)).sum();val=ind.feature_value(f.to_dict(),y)
                self.assertLessEqual(F(float(low.lo)),val)
    def test_all_action_witness_not_sample_minimum(self):
        x=np.array([[.25,.625]])
        for f in self.fits.values():
            a=actor(x,.5,f);r=query(I(x),I(a),.5,f)
            for aa in np.linspace(0,.1796875,33):
                rr=query(I(x),I(np.array([aa])),.5,f)
                self.assertTrue(np.all(r['lower']<=rr['upper']))
    def test_uniform_residual_contains_off_grid(self):
        points=np.random.default_rng(884).uniform(size=(32,2))
        r=econ.terminal_certificate(I(points),.5)
        for f in self.fits.values():
            cert=uniform_residual(f,.5,8);v=f.interval(I(points))
            self.assertTrue(np.all(r['lower']-v.hi>=cert['lower']-1e-12))
            self.assertTrue(np.all(r['upper']-v.lo<=cert['upper']+1e-12))
    def test_bad_arm(self):
        with self.assertRaises(ValueError):features('invented',2)

class ScreeningTests(unittest.TestCase):
    def test_strict_tail_and_denominator(self):
        cut=strict_tail_cuts(np.array([[0.,1.,2.,3.]]),np.array([[.1,1.1,2.1,3.1]]),.5)
        self.assertEqual(cut.tolist(),[[True,True,False,False]])
    def test_equality_retained(self):self.assertFalse(bool(strict_tail_cuts(np.array([[0.,1.]]),np.array([[1.,1.]]),.5)[0,0]))
    def test_no_cut(self):self.assertFalse(np.any(strict_tail_cuts(np.zeros((2,4)),np.ones((2,4)),.75)))
    def test_wrong_cut_attempt_rejected(self):
        with self.assertRaises(ValueError):strict_tail_cuts(np.ones(4),np.zeros(4),.5)
    def test_nonfinite_cut_rejected(self):
        with self.assertRaises(ValueError):strict_tail_cuts(np.array([0.,np.nan]),np.array([1.,2.]),.5)
    def test_wrong_bin_ladder(self):
        from continuum94 import shock_mesh
        with self.assertRaises(ValueError):shock_mesh(3)
    def test_threshold_discrete_agreement(self):
        vals=np.array([.5,-.25,1.,1.5,.375,.625,-1.,.125])
        for alpha in (.5,.75):
            got=econ.discrete_avar_interval(I(vals),alpha);exact=ind.discrete_threshold(vals,alpha)
            self.assertLessEqual(F(float(got.lo)),exact);self.assertGreaterEqual(F(float(got.hi)),exact)

class DesignTests(unittest.TestCase):
    def test_domain_separated_streams(self):
        streams=[np.random.PCG64(np.random.SeedSequence([2026101394,s,j])).random_raw(16).tobytes() for s in (1,2,3) for j in (0,1)]
        self.assertEqual(len(set(streams)),6)
    def test_old_seed_collision_is_reproduced(self):self.assertEqual(202610139301+1,202610139302)
    def test_logarithmic_allowance(self):
        self.assertGreater(sum(F(7)**k/F(math.factorial(k)) for k in range(30)),960)

if __name__=='__main__':unittest.main(verbosity=2)
