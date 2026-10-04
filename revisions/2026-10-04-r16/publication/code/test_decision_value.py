"""Independent finite-support checks of the economic projection identity.

No policy file or confirmation data is read. Every sign is obtained by exact
finite enumeration of the declared manufactured label law, not sampling.
"""
import itertools
import unittest
import numpy as np


def fixture(misspec=0.0):
    h=np.array([.2,.5,.8]); weights=np.array([.2,.3,.5])
    H=np.array([[[2.,.2,.1],[.2,1.,0],[.1,0,1.5]],
                [[1.3,0,.2],[0,2.,.1],[.2,.1,.9]],
                [[.8,.1,0],[.1,1.6,.2],[0,.2,1.2]]])
    b=np.array([[.3,.2,-.1],[-.4,.5,.1],[.2,-.1,.6]])
    inv=np.linalg.inv(H)
    W=sum(weights[j]*h[j]**2*inv[j] for j in range(3))
    ev,U=np.linalg.eigh(W); S=(U*np.sqrt(ev))@U.T
    Si=(U/np.sqrt(ev))@U.T
    features=np.array([[1.,.2],[.1,1.],[.3,-.4]])
    Q,_=np.linalg.qr(S@features);P=Q@Q.T
    perpendicular=np.linalg.svd(Q.T,full_matrices=True)[2][-1]
    q=features@np.array([.1,-.2])+misspec*(Si@perpendicular)
    L=np.array([[.08,.02,0],[.03,.09,.01],[0,.02,.07]])
    eps=np.array(list(itertools.product([-1.,1.],repeat=3)))@L.T
    z=q+eps;critic=(Si@P@S@z.T).T
    def payoff(est):
        total=np.zeros(len(est))
        for j in range(3):
            actions=(inv[j]@(b[j]-h[j]*est).T).T
            # An explicit finite action box contains every constructed action.
            assert np.max(abs(actions))<100
            val=actions@b[j]-.5*np.einsum('ni,ij,nj->n',actions,H[j],actions)-h[j]*(actions@q)
            total+=weights[j]*val
        return total
    Omega=S@(L@L.T)@S
    removed=np.trace((np.eye(3)-P)@Omega)
    bias=np.linalg.norm((np.eye(3)-P)@S@q)**2
    return dict(q=q,z=z,critic=critic,P=P,S=S,Si=Si,Omega=Omega,
                payoff=payoff,removed=removed,bias=bias,
                observed=np.mean(payoff(critic)-payoff(z)),predicted=.5*(removed-bias))

class DecisionValueTests(unittest.TestCase):
    def test_exact_economic_identity_with_correlated_labels(self):
        f=fixture(.02);self.assertAlmostEqual(f['observed'],f['predicted'],places=13)
    def test_correct_dictionary_strictly_improves(self):
        f=fixture();self.assertLess(f['bias'],1e-28)
        self.assertGreater(f['removed'],0);self.assertGreater(f['observed'],0)
    def test_misspecification_can_reverse_the_economic_sign(self):
        f=fixture(.5);self.assertGreater(f['bias'],f['removed'])
        self.assertLess(f['observed'],0);self.assertAlmostEqual(f['observed'],f['predicted'],places=13)
    def test_raw_receives_the_identical_projection_benefit(self):
        f=fixture(); projected_raw=(f['Si']@f['P']@f['S']@f['z'].T).T
        np.testing.assert_allclose(projected_raw,f['critic'],atol=0,rtol=0)
    def test_risk_identity_at_the_economic_weights(self):
        f=fixture(.1)
        er=(f['S']@(f['z']-f['q']).T).T
        ec=(f['S']@(f['critic']-f['q']).T).T
        risk=np.mean(np.sum(er**2,axis=1)-np.sum(ec**2,axis=1))
        self.assertAlmostEqual(risk,f['removed']-f['bias'],places=13)
    def test_full_dictionary_has_zero_gain(self):
        f=fixture();full=(f['Si']@f['S']@f['z'].T).T
        self.assertAlmostEqual(float(np.mean(f['payoff'](full)-f['payoff'](f['z']))),0.,places=14)
    def test_interior_hypothesis_is_not_silently_dropped(self):
        # q=0, H=h=1, a in [0,1], b=2, raw noise +/-0.1.
        # Both clipped actions equal 1, so the unconstrained .005 gain is false.
        raw=np.clip(2-np.array([-.1,.1]),0,1);critic=np.array([1.,1.])
        value=lambda a:2*a-.5*a*a
        self.assertEqual(float(np.mean(value(critic)-value(raw))),0.)
        self.assertNotEqual(.5*.1**2,0.)
    def test_work_threshold_charges_shared_cost(self):
        FC,FR,cC,cR=13.,2.,.5,2.
        threshold=int(np.ceil((FC-FR)/(cR-cC)))
        self.assertGreater(FC-FR+(threshold-1)*(cC-cR),0)
        self.assertLessEqual(FC-FR+threshold*(cC-cR),0)

if __name__=='__main__':unittest.main(verbosity=2)
