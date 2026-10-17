"""Preflight and exact diagnostics. Not the primary investment catalogue."""
import unittest,sys
from pathlib import Path
from fractions import Fraction as F
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import kernel108 as k
from interval94 import I
import independent94 as independent

class Algebra(unittest.TestCase):
    def test_shock_coefficient_independent(self):
        for d in (2,4,8):
            x=[F(j+1,d+2) for j in range(d)]
            for a in (F(0),F(1,16)):
                self.assertEqual(independent.polynomial_from_primitives(x,a)[2],5)
    def test_derivative_identity(self):
        for d in (2,4,8):
            x=np.array([[0.]*d,[1.]*d,[(j+1)/(d+2) for j in range(d)]])
            c0,c1,d0,d1,h0,cap=k.coefficients(x)
            for alpha in (.5,.75):
                for frac in (0,.5,1):
                    a=frac*cap
                    pred=k.derivative_from_coefficients(a,alpha,c0,c1,d0,d1,h0)
                    actual=k.econ._float_terminal(x,a,alpha)[1]
                    np.testing.assert_allclose(pred,actual,rtol=1e-13,atol=2e-14)
    def test_independent_rational_derivative(self):
        x=[F(1,8),F(5,8)];a=F(1,16)
        for alpha in (.5,.75):
            g=independent.objective_gradient(x,a,F(alpha))[1]
            c=k.coefficients(np.array(list(map(float,x))))
            self.assertAlmostEqual(float(g),float(k.derivative_from_coefficients(float(a),alpha,*c[:5])),places=13)
    def test_compiled_certificates(self):
        x=np.array([[0,0],[1,1],[.125,.625],[.5,.5]])
        for alpha in (.5,.75):
            r=k.compiled_certificate(I(x),alpha)
            self.assertTrue(np.all(r['gap']<=2**-20))
            self.assertTrue(np.all(r['action']<=k.econ.capacity(I(x)).lo))
    def test_exact_tail_switch(self):
        # Independent affine upper-tail integral of c*z, z uniform[-1,1].
        def risk(c):
            lo,hi=(F(0),F(1)) if c>=0 else (F(-1),F(0))
            return c*(hi**2-lo**2)/2
        qm=lambda a:a*a+risk(a+1)
        qs=lambda a:a*a+risk(a-1)
        self.assertEqual(qm(F(1,4))-qm(F(-1,4)),F(1,4))
        self.assertEqual(qs(F(-1,4))-qs(F(1,4)),F(1,4))
        self.assertEqual(2*F(-1,4)+F(1,2),0)
        self.assertEqual(2*F(1,4)-F(1,2),0)
    def test_terminal_policy_unchanged(self):
        original=k.econ.terminal_proposal
        before=(k.continuum.terminal_certificate,k.quad.terminal_certificate)
        with k.backend(True):
            self.assertIs(k.econ.terminal_proposal,original)
            self.assertIs(k.quad.terminal_certificate,k.compiled_certificate)
        self.assertEqual(before,(k.continuum.terminal_certificate,k.quad.terminal_certificate))
    def test_exception_restoration(self):
        original=k.continuum.terminal_float_value_slope
        try:
            with k.backend(True):raise RuntimeError('fixture')
        except RuntimeError:pass
        self.assertIs(k.continuum.terminal_float_value_slope,original)
    def test_bad_domain(self):
        for x in ([float('nan'),0],[2,0],[0,0,0]):
            with self.assertRaises(ValueError):k.compiled_proposal(np.array(x),.5)
    def test_bad_risk(self):
        with self.assertRaises(ValueError):k.compiled_proposal(np.array([.5,.5]),.9)
    def test_boundary_normals(self):
        for a,s in ((F(0),F(2)),(F(1),F(-2))):
            b=max(F(0),min(F(1),a-s/2))
            self.assertEqual(s*(b-a)+(b-a)**2,0)
    def test_cubic_inverse(self):
        for p in (2.,3.,10.):
            for q in (-4.,0.,4.):
                u=np.sqrt(p/48);a=-2*u*np.sinh(np.arcsinh(q/(32*u**3))/3)
                self.assertAlmostEqual(16*a**3+p*a+q,0,places=12)

class ProposalEncoding(unittest.TestCase):
    def test_polynomial(self):
        import represent108 as r
        m=r.Conventional('poly2',{'coefficients':[0,0,0,1,0,1]})
        x=np.array([[.2,.3],[.4,.1]])
        v,g=m.float_eval(x,True)
        np.testing.assert_allclose(v,np.sum(x*x,axis=1))
        np.testing.assert_allclose(g,2*x)
    def test_grid_linear_extrapolation(self):
        import represent108 as r
        z=r.grid(4);values=(1+2*z[:,0]-3*z[:,1]).reshape(4,4)
        m=r.Conventional('grid',{'values':values.tolist()})
        x=np.array([[0,0],[1,1],[.5,.25]])
        v,g=m.float_eval(x,True)
        np.testing.assert_allclose(v,1+2*x[:,0]-3*x[:,1])
        np.testing.assert_allclose(g,np.array([[2,-3]]*3))
    def test_payload_identity(self):
        import represent108 as r,json
        m=r.Conventional('hinge',{'coefficients':[1,2,3,4],'directions':[[1,-1]],'offsets':[0]})
        raw=r.encoded(m);self.assertEqual(r.encoded(r.restore(json.loads(raw))),raw)
    def test_active_set_synthetic(self):
        import represent108 as r
        A=np.array([[1,0,0,0],[1,1,0,1],[1,0,1,1],[1,1,1,0],[1,.5,.25,.25]])
        y=A@np.array([1,2,3,4])
        loss,c,n=r.active_set_fit(A,y,1)
        self.assertLess(loss,1e-20);np.testing.assert_allclose(c,[1,2,3,4]);self.assertEqual(n,2)
    def test_disjoint_catalogues(self):
        import represent108 as r
        self.assertFalse(set(map(tuple,r.grid(16))) & set(map(tuple,r.grid(8))))

if __name__=='__main__':unittest.main(verbosity=2)
