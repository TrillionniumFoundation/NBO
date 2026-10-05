"""Independent algebraic checks for the economic linkage; not new experiments."""
from __future__ import annotations
from pathlib import Path
import json,unittest
import numpy as np

class TheoryChecks(unittest.TestCase):
    def test_oscillation_with_transport_and_imperfect_action(self):
        g=np.random.default_rng(31901)
        for _ in range(80):
            r,s,e,dt=g.normal(size=(4,5))
            pred=r+s+e;true=r+s+dt
            for a in range(5):
                delta=pred.max()-pred[a]
                loss=true.max()-true[a]
                self.assertLessEqual(loss,delta+np.ptp(e)+np.ptp(dt)+1e-12)
    def test_constant_levels_leave_actions_unchanged(self):
        r=np.array([.1,-.2,.3]);s=np.array([-.4,.8,.1])
        self.assertEqual(np.argmax(r+s),np.argmax(r+s+30))
    def test_centered_pair_constant_is_attainable(self):
        p=np.array([.2,.3,.5]);e=np.array([1/p[0],-1/p[1],0.])
        risk=np.sum(p*(e-np.sum(p*e))**2)
        self.assertAlmostEqual((e[0]-e[1])**2,(1/p[0]+1/p[1])*risk)
    def test_recursive_transport_products(self):
        beta=np.array([.7,1.1,.8]);nu=np.array([.2,.1,.4]);terminal=.3
        v=terminal
        for b,n in zip(beta[::-1],nu[::-1]):v=n+b*v
        explicit=sum(np.prod(beta[:k])*nu[k] for k in range(3))+np.prod(beta)*terminal
        self.assertAlmostEqual(v,explicit)
    def test_path_transport_coupling(self):
        x=x0=.2;bound=0.
        for shift in [.01,-.03,.02]:
            x=.8*np.tanh(x)+shift;x0=.8*np.tanh(x0)
            bound=.8*bound+abs(shift)
            self.assertLessEqual(abs(x-x0),bound+1e-15)
    def test_true_residual_at_interior_and_both_boundaries(self):
        for target in [-1.,.4,2.]:
            optimum=np.clip(target,0.,1.)
            for a in [0.,.2,.7,1.]:
                derivative=2*(target-a)
                residual=max(derivative,0) if a==0 else max(-derivative,0) if a==1 else abs(derivative)
                loss=(a-target)**2-(optimum-target)**2
                self.assertLessEqual(loss,residual**2/4+1e-15)
    def test_strict_integer_break_even(self):
        F=12;difference=3
        self.assertFalse(4*difference>F);self.assertTrue(5*difference>F)
    def test_caching_counts_distinct_arguments(self):
        queries=[('same-future',.1),('same-future',.1),('same-future',.2)]
        self.assertEqual(len(set(queries)),2)
        self.assertEqual(len(set(queries+[('different-future',.1)])),3)
    def test_least_squares_noise_coefficient(self):
        X=np.array([[1.,0.],[1.,1.],[1.,-1.],[1.,2.]])
        phi=np.array([1.,.3]);G=X.T@X;inv=np.linalg.inv(G)
        coeff=X@inv@phi
        self.assertAlmostEqual(coeff@coeff,phi@inv@phi)
    def test_leverage_sufficient_bound(self):
        X=np.array([[1.,0.],[1.,1.],[1.,-1.],[1.,2.]])
        phi=np.array([1.,.3]);c=np.linalg.eigvalsh(X.T@X/len(X)).min()
        self.assertLessEqual(phi@np.linalg.inv(X.T@X)@phi,(phi@phi)/c/len(X)+1e-15)
    def test_charge_comparative_statics(self):
        previous=1.
        for charge in np.linspace(0,2,30):
            action=np.clip((1-charge)/2,.05,.95)
            self.assertLessEqual(action,previous);previous=action
    def test_all_referee_items_are_addressed(self):
        p=Path(__file__).resolve().parents[1]/'RESPONSE_MAP.json'
        if not p.exists():self.skipTest('editorial integration not materialized')
        x=json.loads(p.read_text())['comments']
        self.assertEqual({r['id'] for r in x},{f'B{i}' for i in range(1,9)}|{f'M{i}' for i in range(1,11)})
        self.assertTrue(all(r['response'] and r['labels'] for r in x))
if __name__=='__main__':unittest.main(verbosity=2)
