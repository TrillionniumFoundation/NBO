import unittest
import numpy as np
import mpmath as mp
import torch
from intervals import I, environment_check
from economy import Economy, make_inputs
from methods import Ridge, myopic

class ArithmeticTests(unittest.TestCase):
    def test_environment(self):self.assertTrue(environment_check())
    def test_tanh_enclosure(self):
        mp.mp.dps=80
        x=np.r_[np.linspace(-12,12,161),0.,1e-15,-1e-15]
        a=I(x).tanh()
        for i,v in enumerate(x):self.assertTrue(mp.mpf(float(a.lo[i]))<=mp.tanh(mp.mpf(float(v)))<=mp.mpf(float(a.hi[i])))
    def test_log_enclosure(self):
        mp.mp.dps=80
        x=np.r_[np.logspace(-8,8,121),1.,2.];a=I(x).log()
        for i,v in enumerate(x):self.assertTrue(mp.mpf(float(a.lo[i]))<=mp.log(mp.mpf(float(v)))<=mp.mpf(float(a.hi[i])))
    def test_interval_sum(self):
        x=np.array([1e12,1.,-1e12,.1]);a=I(x).sum();v=sum(mp.mpf(float(z)) for z in x)
        self.assertTrue(mp.mpf(float(a.lo))<=v<=mp.mpf(float(a.hi)))
    def test_strict_rejections(self):
        with self.assertRaises(ZeroDivisionError):I(1)/I(-1,1)
        with self.assertRaises(ValueError):I(-1).log()
    def test_exact_square(self):
        self.assertLessEqual(float(I(-2,3).square().lo),0.)
        self.assertGreaterEqual(float(I(-2,3).square().hi),9.)

class AlgebraTests(unittest.TestCase):
    # Synthetic states below are arithmetic checks, not prospective outcomes.
    def setUp(self):
        self.e=Economy(make_inputs(3))
        self.y=torch.tensor([[.2,-.1,.3],[-.3,.2,.1]])
        self.t=torch.tensor([[1.,.1,.03,.9],[.9,.12,.08,.85]])
    def test_interval_derivative(self):
        a=torch.tensor([.5,.6]);iv=self.e.interval_derivative(self.y,a,self.t);g=self.e.derivative(self.y,a,self.t).numpy()
        self.assertTrue(np.all(iv.lo<=g));self.assertTrue(np.all(g<=iv.hi))
    def test_derivative_against_difference(self):
        a=torch.tensor([.5,.6]);h=1e-5
        fd=(self.e.value(self.y,a+h,self.t)-self.e.value(self.y,a-h,self.t))/(2*h)
        np.testing.assert_allclose(fd.detach(),self.e.derivative(self.y,a,self.t),atol=1e-8)
    def test_global_curvature(self):
        k=self.e.curvature_lower(self.y,self.t)
        for v in [.05,.2,.5,.8]:
            a=torch.tensor([v,v],requires_grad=True);q=self.e.value(self.y,a,self.t)
            g=torch.autograd.grad(q.sum(),a,create_graph=True)[0]
            h=torch.autograd.grad(g.sum(),a)[0].detach().numpy()
            self.assertTrue(np.all(h<=-k))
    def test_residual_certificate(self):
        a=torch.tensor([.5,.6]);c=self.e.certify(self.y,a,self.t)
        vals=[]
        for z in np.linspace(.05,.85,301):vals.append(self.e.value(self.y,torch.tensor([z,z]),self.t).detach().numpy())
        loss=np.max(vals,axis=0)-self.e.value(self.y,a,self.t).detach().numpy()
        self.assertTrue(np.all(loss<=np.array(c['regret_upper'])+1e-12))
    def test_ridge_feature_derivatives(self):
        for kind in ['quadratic','rbf']:
            r=Ridge(self.e,kind,self.y);f,df=r.matrices(self.y)
            x=self.y.clone().requires_grad_(True);v=r.features(x)
            for j in range(v.shape[1]):
                gg=torch.autograd.grad(v[:,j].sum(),x,retain_graph=True,allow_unused=True)[0]
                np.testing.assert_allclose(gg.numpy(),df[:,:,j],atol=1e-14)
    def test_myopic_optimality(self):
        a=myopic(self.e,self.t);d=self.e.A[0]*(self.t[:,0]/a-self.t[:,1]*a-self.t[:,2])-self.e.W[0]
        for i in range(2):
            if .05<float(a[i])<float(self.t[i,3]):self.assertLess(abs(float(d[i])),1e-14)
    def test_cross_bank_risk_identity(self):
        z=np.array([-1.,2.,3.]);p=.7;mu=z.mean()
        val=np.mean((p-z[:,None])*(p-z[None,:]))
        self.assertAlmostEqual(val,(p-mu)**2)
    def test_centered_decision_risk(self):
        p=np.array([.2,.3,.5]);e=np.array([.5,-.7,.9]);r=np.sum(p*(e-np.dot(p,e))**2)
        for i in range(3):
            for j in range(3):self.assertLessEqual((e[i]-e[j])**2,(1/p[i]+1/p[j])*r+1e-14)
    def test_boundary_residual(self):
        # Analytic concave objectives: outward/inward derivatives at endpoints.
        for a,d in [(0.,-2.),(1.,2.)]:
            res=max(d,0) if a==0 else max(-d,0)
            self.assertEqual(res,0)
    def test_transport_recursion(self):
        L=[.8,.7,.9];eta=[.1,.2,.3];z=.4
        for l,h in zip(reversed(L),reversed(eta)):z=h+l*z
        self.assertAlmostEqual(z,.1+.8*.2+.8*.7*.3+.8*.7*.9*.4)

if __name__=='__main__':unittest.main(verbosity=2)
