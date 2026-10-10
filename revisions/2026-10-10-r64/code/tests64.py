"""Exact and boundary regressions for certificate-gated queries; not data."""
from fractions import Fraction as F
import itertools,math,unittest
import numpy as np
import query64 as g
q=g.q

def model(d,value):
    return (np.zeros((d+5,1)),np.zeros(1),np.zeros(1),value)

class GatedTests(unittest.TestCase):
    def setUp(self):
        self.x=np.random.default_rng(999).integers(0,2**16,size=(12,8))/2**16
    def test_no_prediction_when_boundary_certificate_suffices(self):
        o=g.Oracle('relu',{})
        z=o.solve(np.zeros((2,8)),2,.02)
        self.assertEqual(o.counts['learned_proposals'],0)
        self.assertEqual(o.counts['prediction_free_returns'],2)
        self.assertTrue(np.all(z['gap']<=.02))
    def test_rejected_predictions_preserve_full_recursive_transcript(self):
        for r in (2,3):
            a=g.Oracle('adaptive');b=g.Oracle('relu',{j:model(8,-100) for j in range(2,r+1)})
            u=a.solve(self.x[:4],r,.004);v=b.solve(self.x[:4],r,.004)
            for k in ('action','lower','upper','probes'):np.testing.assert_array_equal(u[k],v[k])
            self.assertEqual(a.counts['q_queries'],b.counts['q_queries'])
            self.assertEqual(b.counts['routed_queries'],0)
    def test_terminal_is_common_analytic_kernel(self):
        a=g.Oracle('adaptive').solve(self.x,1,.001)
        b=g.Oracle('relu',{}).solve(self.x,1,.001)
        for k in ('action','lower','upper'):np.testing.assert_array_equal(a[k],b[k])
    def test_arbitrary_predictions_are_not_certificates(self):
        for value in (-100,0,.0625,.15,100,float('nan')):
            o=g.Oracle('relu',{2:model(8,value)})
            z=o.solve(self.x,2,.002)
            self.assertTrue(np.all(z['lower']<=z['upper']))
            self.assertTrue(np.all(z['gap']<=.002))
            self.assertTrue(np.all(z['action']<=q.cap_interval(self.x).lo))
    def test_action_quantum_and_protected_split(self):
        o=g.Oracle('relu',{2:model(8,.07)});z=o.solve(self.x,2,.0005)
        self.assertTrue(np.all(z['action']*2**32==np.floor(z['action']*2**32)))
        self.assertEqual(o.counts['rational_fallbacks'],0)
    def test_exhausted_floating_cap_uses_paid_exact_fallback(self):
        o=g.Oracle(max_probes=2);z=o.solve(self.x[:1],2,.003)
        self.assertEqual(o.counts['rational_fallbacks'],1)
        self.assertGreater(o.counts['rational_q_queries'],0)
        self.assertTrue(np.all(z['gap']<=.003))
    def test_recovery_precision_limit_is_enforced(self):
        with self.assertRaises(RuntimeError):g.Oracle().rational([F(1,2)]*2,2,F(1,2**40))
    def test_dimension_normalized_constants_exact(self):
        H=F(21,4)+F(15,16)*54*F(5,32)
        L=F(13,16)+F(15,16)*27*F(3,8)
        self.assertEqual(H,F(3369,256));self.assertEqual(L,F(1319,128))
        self.assertEqual(F(15,16)*54/F(6144),F(135,16384))
        for d,r in itertools.product((2,4,8,16,64),range(8)):
            G,M=q.regularity(r,d);self.assertLessEqual(d*G,27);self.assertLessEqual(d*M,54)
    def test_real_point_cap_dominates_executed_query_counts(self):
        for d in (2,8,16):
            x=np.random.default_rng(999).integers(0,65537,size=(8,d))/65536
            o=g.Oracle('relu',{2:model(d,.1)});z=o.solve(x,2,.002)
            _,M=q.regularity(1,d);H=F(21,4)+q.B*M*F(5*d,32)
            cap=4+math.ceil(5*.25*math.sqrt(float(H)/(3*.002)))
            self.assertLessEqual(int(z['probes'].max()),cap)
            self.assertEqual(o.counts['stored_state_nodes'],0)
    def test_parabolic_minorant_independent_rational_fixture(self):
        for c,k,H in itertools.product((F(-1),F(0),F(2)),(F(-2),F(1)),(F(2),F(5))):
            f=lambda x:H*x*x/2+k*x+c
            for l,u in ((F(0),F(1,4)),(F(1,16),F(3,16))):
                for j in range(21):
                    s=F(j,20);x=l+s*(u-l)
                    p=(1-s)*f(l)+s*f(u)-H*(u-l)**2*s*(1-s)/2
                    self.assertEqual(p,f(x))
    def test_running_lower_bounds_cannot_weaken(self):
        lows=[F(-3),F(-1),F(-2),F(0)];upper=F(1);running=lows[0];gap=upper-running
        for x in lows[1:]:
            running=max(running,x);self.assertLessEqual(upper-running,gap);gap=upper-running
    def test_catalogue_exactly_prespecified(self):
        import science64 as s
        cat=s.catalogue();self.assertEqual(len(cat),160)
        self.assertEqual(len({x['key'] for x in cat}),160)
        self.assertEqual({x['seed'] for x in cat},{0,6401,6402})
        self.assertEqual({x['repeat'] for x in cat},{0,1})
    def test_original_law_budget_at_all_declared_horizons(self):
        for T,den in itertools.product((2,3),(32,128)):
            self.assertLess(F(q.policy_allowance(T,F(1,den))),F(1,den))
    def test_monetary_adoption_interval_uses_positive_numeraire(self):
        n=7;m=F(20);l=F(1,100);u=F(3,100);delta=F(2)
        lower=n*m*l-delta;upper=n*m*u-delta
        for j in range(21):
            gain=l+(u-l)*F(j,20);self.assertLessEqual(lower,n*m*gain-delta);self.assertLessEqual(n*m*gain-delta,upper)
    def test_amortization_requires_actual_deployment_saving(self):
        B=7;C=10;L=8
        self.assertFalse(B+3*L<3*C);self.assertTrue(B+4*L<4*C)
        for k in range(1,100):self.assertFalse(B+k*(C+1)<k*C)
    def test_model_arrays_are_not_mutated(self):
        m=model(8,.1);before=[np.array(v,copy=True) for v in m]
        g.Oracle('relu',{2:m}).solve(self.x,2,.005)
        for a,b in zip(m,before):np.testing.assert_array_equal(a,b)
    def test_invalid_state_fails_before_certificate(self):
        for x in (np.array([[float('nan'),0]]),np.ones((1,3)),np.array([[2.,0.]])):
            with self.assertRaises(ValueError):g.Oracle().solve(x,2,.01)
if __name__=='__main__':unittest.main(verbosity=2)
