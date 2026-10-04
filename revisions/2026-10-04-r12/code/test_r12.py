"""Regression tests supplement, rather than replace, the analytical proofs."""
import unittest,tempfile
from common import *
import observation,reference,evaluation,training
class Tests(unittest.TestCase):
    def test_profiles_are_float(self):
        for d in [1,10,20,50]:self.assertEqual(profiles(d).dtype,np.float64)
    def test_population_moments(self):
        p=profiles(10);np.testing.assert_allclose(p.mean(1),np.repeat(PROTOCOL['population_means'],3),atol=1e-14)
        np.testing.assert_allclose(p.std(1),np.tile(PROTOCOL['population_spreads'],3),atol=1e-14)
    def test_observation_right_inverse(self):
        for d in [1,10,50]:
            S,A,n=observation.matrices(d);np.testing.assert_allclose(S@A,np.eye(d),atol=1e-13);np.testing.assert_allclose(S@n,0,atol=1e-13)
    def test_observation_covariance(self):
        for d in [1,10,50]:
            S,A,n=observation.matrices(d);np.testing.assert_allclose(A@(S@S.T)@A.T+np.outer(n,n),np.eye(d+1),atol=1e-12)
    def test_observation_requires_null_randomization(self):
        S,A,n=observation.matrices(10);self.assertEqual(np.linalg.matrix_rank(A@(S@S.T)@A.T),10)
    def test_observation_increment(self):
        g=np.random.default_rng(1);dy=g.normal(size=(20,10));drift=g.normal(size=(20,10));z=g.normal(size=20)
        w=observation.recover(dy,drift,z);S,_,_=observation.matrices(10);np.testing.assert_allclose(w@S.T,dy-drift,atol=1e-12)
    def test_root_first_order(self):
        p=np.linspace(-5,5,200);m=reference.root(p);np.testing.assert_allclose(1/m-P['adjustment']*m,p,atol=1e-12)
    def test_action_search(self):
        y=np.linspace(-2,2,51);v=.6*y+.03*y*y;m=reference.best_action(v,y);dx=y[1]-y[0];pf=np.diff(v)[1:]/dx;pb=np.diff(v)[:-1]/dx
        b=P['productivity']-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2+P['coupling']*np.tanh(float(old.coupling(1)[0,0])*y[1:-1])
        def H(a):return np.log(a)-P['adjustment']*a*a/2+np.maximum(b-a,0)*pf+np.minimum(b-a,0)*pb
        value=H(m)
        for a in np.linspace(P['lower'],P['upper'],1001):self.assertTrue(np.all(value>=H(a)-1e-12))
    def test_implicit_residual(self):
        y=np.linspace(-3,3,101);v,res=reference.implicit(y,y,np.full(99,.8),.01,(-3.,3.));self.assertLess(res,1e-10)
    def test_bernstein_zero_not_positive(self):
        r=pc.empirical_lower(np.zeros(100),.1,.001,0.,4000);self.assertLessEqual(r['lower'],0.);self.assertGreaterEqual(r['upper'],0.)
    def test_concavity_action_bound(self):
        rng=np.random.default_rng(3);mu=1/P['upper']**2
        for _ in range(200):
            q=rng.normal();e=rng.normal()*.05;m=np.clip(reference.root(q),P['lower'],P['upper']);z=np.clip(reference.root(q+e),P['lower'],P['upper'])
            H=lambda a:np.log(a)-P['adjustment']*a*a/2-q*a
            self.assertLessEqual(H(m)-H(z),e*e/(2*mu)+1e-12)
    def test_fee_identity(self):
        for m in [.2,.8,1.5]:
            for fee in PROTOCOL['gross_consumption_fee_rates']:self.assertAlmostEqual(math.log((1-fee)*m)-math.log(m),math.log1p(-fee))
    def test_state_sampler_shape(self):
        x=training.states(10,64,torch.Generator().manual_seed(1));self.assertEqual(tuple(x.shape),(64,11));self.assertTrue(torch.isfinite(x).all())
    def test_pair_rejects_noncommon_noise(self):
        from unittest.mock import patch
        a=dict(dimension=10,design='origin',steps=2,paths=3,initial_state_hash='x',initial_index_hash='y',noise_seed=1,noise_sha256='a')
        b=dict(a,noise_sha256='b')
        with tempfile.TemporaryDirectory() as dr:
            p=Path(dr);write(p/'a.json',a);write(p/'b.json',b)
            with self.assertRaises(ValueError):evaluation.paired(p/'a.json',p/'b.json',p)
if __name__=='__main__':
    import math
    unittest.main(verbosity=2)
