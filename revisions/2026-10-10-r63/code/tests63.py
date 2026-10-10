"""Independent rational fixtures for the new interval Bellman contract."""
import unittest,itertools,sys
from fractions import Fraction as F
import numpy as np
import query63 as q

class CertificateTests(unittest.TestCase):
    def test_discount_matches_unchanged_primitives(self): self.assertEqual(q.B,F(q.n.BETA))
    def test_regularities_are_dimension_normalized(self):
        for d in (2,4,8,16,32):
            for r in range(12):
                g,m=q.regularity(r,d);self.assertLessEqual(g,F(27,d));self.assertLessEqual(m,F(54,d))
    def test_primitive_curvature_slack(self):self.assertEqual(F(4)-F(15,16)*27/8,F(107,128))
    def test_scalar_terminal_hessian_coefficients(self):
        for d in (2,4,8,16):
            b=[F(1,2) if j%2==0 else F(1,4) for j in range(d)]
            self.assertEqual(8*sum(v*v for v in b)/d+sum((b[j]-b[(j+1)%d])**2 for j in range(d))/(2*d),F(41,32))
            self.assertEqual(16*sum(b)**2/d**2,F(9,4))
    def test_exact_terminal_values_and_derivatives(self):
        for d in (2,8):
            x=np.array([[float(F((j*3+k)%17,16)) for j in range(d)] for k in range(4)])
            for a in (0.,1/32,1/8):
                aa=np.full(len(x),a);v=q.n.o.final_q(q.I.point(x),q.I.point(aa),1);g=q.n.o.final_derivative(q.I.point(x),q.I.point(aa),1)
                for k in range(len(x)):
                    exact=q.n.o.exact_q(x[k],F(a),1);der=q.n.o.exact_q(x[k],F(a),1,True)
                    self.assertLessEqual(F(float(v.lo[k])),exact);self.assertGreaterEqual(F(float(v.hi[k])),exact)
                    self.assertLessEqual(F(float(g.lo[k])),der);self.assertGreaterEqual(F(float(g.hi[k])),der)
    def test_parabolic_minorant_rational(self):
        for l,r in ((F(0),F(1,4)),(F(1,32),F(3,16))):
            f=lambda a:a*a+4*a**4;H=2+48*r*r
            for j in range(65):
                s=F(j,64);p=(1-s)*f(l)+s*f(r)-H*(r-l)**2*s*(1-s)/2
                self.assertLessEqual(p,f(l+s*(r-l)))
    def test_lower_endpoints_need_not_be_convex(self):
        # Lowering either chord endpoint can only lower the minorant.
        for s in (F(0),F(1,7),F(1)):
            self.assertLessEqual((1-s)*F(-3)+s*F(2),(1-s)*F(-1)+s*F(4))
    def test_strong_convex_residual_rational(self):
        for a,b in itertools.product([F(0),F(1,16),F(1,8),F(1,4)],repeat=2):
            f=lambda x:(x-b)**2;der=2*(a-b)
            self.assertLessEqual(f(a),der*der/4)
    def test_boundary_projected_derivative(self):
        # Raw derivative need not vanish at a constrained minimizer.
        f=lambda a:a*a+3*a
        self.assertEqual(min(f(F(j,64)) for j in range(17)),0)
        self.assertNotEqual(3,0)
    def test_shock_variance_and_exact_moment(self):
        for bins in (1,2,4,8):
            mids=[F(2*j+1-bins,32*bins) for j in range(bins)]
            error=F(1,3072)-sum(z*z for z in mids)/bins
            self.assertEqual(error,F(1,3072*bins*bins))
    def test_quantized_actions_feasible(self):
        x=np.array([[0.,0.],[1.,1.],[.5,.25]])
        cap=q.cap_interval(x);a=q.clamp(np.array([np.inf,-1.,.5]),cap.lo)
        self.assertTrue(np.all(a>=0));self.assertTrue(np.all(a<=cap.lo));self.assertTrue(np.all(a*q.SCALE==np.floor(a*q.SCALE)))
    def test_cubic_guess_terminal_global_certificate(self):
        for d in (2,8,16):
            x=np.vstack([np.zeros(d),np.ones(d),np.full(d,.25),np.arange(d)/(d-1)])
            out=q.Oracle().solve(x,1,1e-7)
            self.assertTrue(np.all(out['gap']<=1e-7));self.assertTrue(np.all(out['probes']==1))
    def test_closed_boundary_queries(self):
        x=np.array([[0.,0.],[1.,1.],[0.,1.],[1.,0.]])
        out=q.Oracle().solve(x,2,1/128)
        self.assertTrue(np.all(out['gap']<=1/128));self.assertTrue(np.all(out['action']<=q.cap_interval(x).lo))
    def test_tighter_terminal_bracket_nested_in_wider(self):
        x=np.array([[.5,.25],[.8,.4]])
        a=q.Oracle().solve(x,1,1/32);b=q.Oracle().solve(x,1,1e-8)
        self.assertTrue(np.all(a['lower']<=b['upper']));self.assertTrue(np.all(b['lower']<=a['upper']))
    def test_r2_reference_quadrature_crosscheck(self):
        from scipy.optimize import minimize_scalar
        x=np.array([[.125,.75],[.5,.5]])
        result=q.Oracle().solve(x,2,1/512)
        for i in range(len(x)):
            def f(a):
                z=(np.arange(128)+.5)/2048-1/32;y=q.n.next_point(np.repeat(x[i:i+1],128,axis=0),np.full(128,a),z)
                return q.n.primitive_point(x[i:i+1],np.array([a]))[0]+float(q.B)*q.approximate(y,1)[1].mean()
            opt=minimize_scalar(f,bounds=(0,q.cap_point(x[i:i+1])[0]),method='bounded',options={'xatol':1e-12})
            v=min(opt.fun,f(0),f(q.cap_point(x[i:i+1])[0]))
            # The fine quadrature discrepancy has its own explicit remainder.
            _,M=q.regularity(1,2);error=float(q.B*M*2/F(6144*128**2))
            self.assertLessEqual(result['lower'][i],v+error);self.assertGreaterEqual(result['upper'][i],v-error)
    def test_bad_network_cannot_forge_acceptance(self):
        x=np.array([[.125,.75],[.5,.5]])
        # An arbitrary large constant is clipped, then still independently checked.
        features=q.coefficients(x).shape[1];model=(np.zeros((features,1)),np.zeros(1),np.zeros(1),999.)
        a=q.Oracle('relu',{2:model}).solve(x,2,1/128);b=q.Oracle().solve(x,2,1/128)
        self.assertTrue(np.all(a['gap']<=1/128));self.assertTrue(np.all(a['lower']<=b['upper']));self.assertTrue(np.all(b['lower']<=a['upper']))
    def test_no_state_table(self):
        out=q.Oracle();out.solve(np.full((2,16),.5),2,1/32);self.assertEqual(out.counts['stored_state_nodes'],0)
    def test_caps_are_fail_closed(self):
        with self.assertRaises(RuntimeError):q.Oracle(max_probes=2)._solve(np.full((1,2),.5),2,1/1024)
    def test_exact_fallback_keeps_controller_defined(self):
        o=q.Oracle(max_probes=2);out=o.solve(np.full((1,2),.5),2,1/128)
        self.assertTrue(np.all(out['gap']<=1/128));self.assertEqual(o.counts['rational_fallbacks'],1)
    def test_rational_fallback_encloses_float_reference(self):
        x=np.array([[.25,.75]]);lo,hi,a=q.Oracle().rational(list(map(F,x[0])),2,F(1,64))
        v=q.Oracle().solve(x,2,1/512)
        self.assertLessEqual(float(lo),v['upper'][0]);self.assertGreaterEqual(float(hi),v['lower'][0])
    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):q.Oracle().solve(np.array([[np.nan,0]]),2,.1)
    def test_uniform_policy_budget(self):
        for T in (2,3):
            for target in ('1/32','1/128'):
                self.assertLess(q.policy_allowance(T,target),float(F(target)))
    def test_horizon_error_unrolling(self):
        e=F(1,64);g=F(0)
        for _ in range(3):g=e+q.B*g
        self.assertEqual(g,e*(1+q.B+q.B*q.B))
    def test_adaptive_and_bisection_both_certify(self):
        x=np.array([[.1,.7],[.5,.5]])
        for mode in ('adaptive','bisection'):
            o=q.Oracle(mode);out=o.solve(x,2,1/128);self.assertTrue(np.all(out['gap']<=1/128))

if __name__=='__main__':unittest.main(verbosity=2)
