import copy
import math
from pathlib import Path
import sys
import unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(ROOT/'revisions/2026-10-05-r23/code'))
from experiment import economy
from policy_certificate import Ball
from entropic_certificate import certify,candidate,transform,inverse,nominal_transform,margin


class EntropicTests(unittest.TestCase):
    def setUp(self): self.m=economy(3,'anchor',5)

    def test_scalar_gaussian_formula(self):
        p=np.array([[.3]]);s=np.array([[.2]]);theta=.4
        v=transform(Ball.exact(p),s,theta)
        exact=.3/(1-2*.4*.2*.3)
        self.assertLessEqual(v.c[0,0]-v.r[0,0],exact)
        self.assertGreaterEqual(v.c[0,0]+v.r[0,0],exact)

    def test_zero_risk_limit(self):
        p=np.array([[.3,.1],[.1,.4]])
        got=transform(Ball.exact(p),np.eye(2)*.2,0)
        np.testing.assert_array_equal(got.c,p)
        np.testing.assert_array_equal(got.r,np.zeros_like(p))

    def test_inverse_inclusion(self):
        a=np.array([[2.,.2],[-.1,1.5]])
        got=inverse(Ball.exact(a));truth=np.linalg.inv(a)
        self.assertTrue(np.all(np.abs(got.c-truth)<=got.r))

    def test_domain_failure(self):
        with self.assertRaises(ArithmeticError): transform(Ball.exact(np.eye(2)),np.eye(2),1.)

    def test_invalid_theta(self):
        for theta in (-1.,math.nan,math.inf):
            with self.assertRaises(ValueError): transform(Ball.exact(np.eye(2)),np.eye(2),theta)

    def test_noncommuting_transform(self):
        p=np.array([[.3,.1],[.1,.4]]);s=np.array([[.2,.03],[.03,.1]])
        got=transform(Ball.exact(p),s,.5);truth=nominal_transform(p,s,.5)
        self.assertTrue(np.all(np.abs(got.c-truth)<=got.r))

    def test_structural_certificate(self):
        k,_,_=candidate(self.m,6.,'structural')
        self.assertLess(certify(self.m,k,6.)['policy_gap_upper'],1e-4)

    def test_nbo_certificate(self):
        k,_,r=candidate(self.m,6.,'NBO')
        self.assertTrue(r['all_training_thresholds_met'])
        self.assertLess(certify(self.m,k,6.)['policy_gap_upper'],1e-4)

    def test_zero_risk_candidate(self):
        k,_,_=candidate(self.m,0.,'NBO')
        self.assertLess(certify(self.m,k,0.)['policy_gap_upper'],1e-4)

    def test_implementation_monotonicity(self):
        k,_,_=candidate(self.m,6.,'NBO')
        a=certify(self.m,k,6.,1e-12);b=certify(self.m,k,6.,1e-8)
        self.assertGreater(b['implementation_gap_upper'],a['implementation_gap_upper'])

    def test_reject_bad_covariance(self):
        m=copy.deepcopy(self.m);m['Sigma'][0,1]=1
        k=np.zeros_like(m['A'])
        with self.assertRaises(ValueError):certify(m,k,1.)

    def test_reject_nondiagonal_cost(self):
        m=copy.deepcopy(self.m);m['Q'][0,0,1]=.1
        with self.assertRaises(ValueError):certify(m,np.zeros_like(m['A']),1.)

    def test_reject_nonfinite_gain(self):
        k=np.zeros_like(self.m['A']);k[0,0,0]=math.nan
        with self.assertRaises(ValueError):certify(self.m,k,1.)

    def test_certificate_is_not_automatic(self):
        k=np.ones_like(self.m['A'])*2
        try: result=certify(self.m,k,6.)
        except ArithmeticError: return
        self.assertGreater(result['policy_gap_upper'],1e-4)

    def test_one_date(self):
        m=economy(2,'anchor',1);k,_,r=candidate(m,2.,'NBO')
        self.assertEqual(r['hidden_updates'],0)
        self.assertLess(certify(m,k,2.)['policy_gap_upper'],1e-4)

    def test_full_value_crosscheck(self):
        k,_,_=candidate(self.m,6.,'NBO');ko,_,_=candidate(self.m,6.,'structural')
        def val(kk):
            p=self.m['Qf'].copy();c=0.
            for t in range(4,-1,-1):
                sign,logdet=np.linalg.slogdet(np.eye(3)-12*self.m['Sigma']@p)
                self.assertEqual(sign,1)
                c=.96*(c-logdet/12)
                psi=nominal_transform(p,self.m['Sigma'],6.)
                f=self.m['A'][t]-self.m['B'][t]@kk[t]
                p=self.m['Q'][t]+kk[t].T@self.m['R'][t]@kk[t]+.96*f.T@psi@f
            return p,c
        p,c=val(k);po,co=val(ko)
        gap=3*max(0.,np.linalg.eigvalsh(p-po)[-1])+c-co
        self.assertLessEqual(gap,certify(self.m,k,6.)['policy_gap_upper']+1e-12)


if __name__=='__main__':unittest.main()
