import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import numpy as np
import mpmath as mp

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT/'revisions/2026-10-05-r23/code'))
from experiment import economy
from residual_certificate import certify, evaluation_tube, nominal_values
from entropic_certificate import candidate, certify as box_certify


class ResidualTests(unittest.TestCase):
    def setUp(self):
        self.model = economy(3, 'anchor', 5)
        self.gains, _, _ = candidate(self.model, 6., 'NBO')

    def test_neural_policy(self):
        self.assertLess(certify(self.model, self.gains, 6.)['policy_gap_upper'], 1e-4)

    def test_structural_policy(self):
        k, _, _ = candidate(self.model, 6., 'structural')
        self.assertLess(certify(self.model, k, 6.)['policy_gap_upper'], 1e-4)

    def test_high_precision_evaluation(self):
        mp.mp.dps = 90
        centers, radii, _ = evaluation_tube(self.model, self.gains, 6.)
        mm = lambda a: mp.matrix([[mp.mpf(float(x)) for x in row] for row in a])
        p = mm(self.model['Qf']); s = mm(self.model['Sigma']); I = mp.eye(3)
        beta = mp.mpf(float(self.model['beta']))
        for t in range(4, -1, -1):
            a,b,q,r = (mm(self.model[n][t]) for n in ('A','B','Q','R'))
            k = mm(self.gains[t]); f = a - b*k
            psi = p * (I - 12*s*p)**-1
            p = q + k.T*r*k + beta*f.T*psi*f
            error = p - mm(centers[t])
            error = (error + error.T)/2
            largest = max(abs(v) for v in mp.eigsy(error, eigvals_only=True))
            self.assertLessEqual(largest, mp.mpf(float(radii[t])))

    def test_supplied_inaccurate_centers_charged(self):
        centers = nominal_values(self.model, self.gains, 6.)
        _, a, _ = evaluation_tube(self.model, self.gains, 6., centers)
        centers[2] += np.eye(3)*1e-6
        _, b, _ = evaluation_tube(self.model, self.gains, 6., centers)
        self.assertGreater(b[2], a[2])
        self.assertGreaterEqual(b[2], 0.999e-6)

    def test_no_optimal_policy_in_verifier(self):
        with patch('experiment.riccati', side_effect=AssertionError('forbidden')), \
             patch('entropic_certificate.candidate', side_effect=AssertionError('forbidden')):
            self.assertLess(certify(self.model, self.gains, 6.)['policy_gap_upper'], 1e-4)

    def test_terminal_identity(self):
        centers = nominal_values(self.model, self.gains, 6.); centers[-1,0,0] += .01
        with self.assertRaises(ValueError): evaluation_tube(self.model, self.gains, 6., centers)

    def test_asymmetric_center_rejected(self):
        centers = nominal_values(self.model, self.gains, 6.); centers[1,0,1] += .01
        with self.assertRaises(ValueError): evaluation_tube(self.model, self.gains, 6., centers)

    def test_one_date(self):
        m = economy(2,'anchor',1); k,_,_ = candidate(m, 2., 'NBO')
        self.assertLess(certify(m,k,2.)['policy_gap_upper'], 1e-4)

    def test_zero_risk(self):
        k,_,_ = candidate(self.model, 0., 'NBO')
        self.assertLess(certify(self.model,k,0.)['policy_gap_upper'], 1e-4)

    def test_implementation_increases_allowance(self):
        a = certify(self.model,self.gains,6.,0.)
        b = certify(self.model,self.gains,6.,1e-8)
        self.assertGreater(b['policy_gap_upper'],a['policy_gap_upper'])

    def test_bad_execution_contract(self):
        for x in (-1.,float('nan'),float('inf')):
            with self.assertRaises(ValueError): certify(self.model,self.gains,6.,x)

    def test_bad_risk_parameter(self):
        for x in (-1.,float('nan'),float('inf')):
            with self.assertRaises(ValueError): certify(self.model,self.gains,x)

    def test_bad_policy_not_automatically_certified(self):
        k = self.gains + np.eye(3)[None,:,:]*.8
        try: result = certify(self.model,k,6.)
        except ArithmeticError: return
        self.assertGreater(result['policy_gap_upper'],1e-4)

    def test_nonfinite_input(self):
        k=self.gains.copy(); k[0,0,0]=float('nan')
        with self.assertRaises(ValueError): certify(self.model,k,6.)

    def test_covariance_validation_retained(self):
        m=copy.deepcopy(self.model);m['Sigma'][0,1]=1.
        with self.assertRaises(ValueError):certify(m,self.gains,6.)

    def test_same_candidate_as_box_verifier(self):
        a=box_certify(self.model,self.gains,6.); b=certify(self.model,self.gains,6.)
        self.assertLess(a['policy_gap_upper'],1e-4)
        self.assertLess(b['policy_gap_upper'],1e-4)
        self.assertGreaterEqual(b['maximum_evaluation_radius'],0.)

if __name__=='__main__':unittest.main()
