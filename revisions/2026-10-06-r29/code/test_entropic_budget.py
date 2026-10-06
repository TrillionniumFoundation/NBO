"""Checks for primitive risk budgets and independent own-policy certification."""
from pathlib import Path
import copy
import math
import sys
import unittest
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
for sub in ('2026-10-05-r23','2026-10-06-r27','2026-10-06-r28','2026-10-06-r29'):
    sys.path.insert(0,str(ROOT/'revisions'/sub/'code'))
import entropic_budget as eb
from experiment import economy
from entropic_certificate import nominal_transform, candidate
from residual_certificate import certify, evaluation_tube, nominal_values


def evaluate_with_constants(m,K,theta):
    P=nominal_values(m,K,theta); c=0.
    for t in range(len(K)-1,-1,-1):
        if theta:
            sign,ld=np.linalg.slogdet(np.eye(len(K[0]))-2*theta*m['Sigma']@P[t+1])
            if sign<=0:raise ArithmeticError('domain')
            h=-ld/(2*theta)
        else:h=float(np.trace(m['Sigma']@P[t+1]))
        c=m['beta']*(c+h)
    return P,c


class EntropicBudgetTests(unittest.TestCase):
    def setUp(self):
        self.m=economy(3,'valuation',5); self.theta=12.

    def test_primitive_plan_does_not_evaluate_a_target(self):
        with patch.object(eb,'nominal_transform',side_effect=AssertionError('target consulted')):
            p=eb.plan(self.m,self.theta)
        self.assertEqual(len(p['dates']),4)

    def test_primitive_domains_are_positive(self):
        p=eb.plan(self.m,self.theta)
        self.assertGreater(min(p['domain_margins']),0)
        self.assertLessEqual(p['nominal_policy_allowance'],.00005*(1+1e-12))

    def test_cap_contraction(self):
        for row in eb.plan(self.m,self.theta)['dates']:
            logr=math.log1p(-2*row['alpha']*row['c'])
            self.assertLessEqual(math.exp(row['ideal_iteration_cap']*logr)*row['initial_error_upper'],row['target']/2)

    def test_isotropic_scale_inside_all_targets(self):
        for row in eb.plan(self.m,self.theta)['dates']:
            self.assertTrue(0<row['c']<=row['m']<=row['L'])
            self.assertLessEqual(row['alpha'],1/(4*row['L']))

    def test_thresholds_and_hard_caps(self):
        _,_,rec=eb.solve(self.m,self.theta)
        self.assertTrue(rec['all_training_thresholds_met'])
        self.assertLessEqual(rec['hidden_updates'],rec['plan']['total_ideal_iteration_cap'])

    def test_targets_use_returned_future(self):
        K,W,rec=eb.solve(self.m,self.theta)
        P=nominal_values(self.m,K,self.theta)
        for row in rec['dates']:
            j=row['continuation_date']; M=3*nominal_transform(P[j],self.m['Sigma'],self.theta)
            self.assertLessEqual(np.linalg.norm(W[j].T@W[j]-M,'fro'),row['target'])

    def test_target_spectra_in_primitive_envelope(self):
        K,_,rec=eb.solve(self.m,self.theta); P=nominal_values(self.m,K,self.theta)
        for row in rec['dates']:
            eig=np.linalg.eigvalsh(3*nominal_transform(P[row['continuation_date']],self.m['Sigma'],self.theta))
            self.assertGreaterEqual(eig[0]+1e-12,row['m'])
            self.assertLessEqual(eig[-1],row['L'])

    def test_own_values_below_primitive_reference_envelope(self):
        K,_,rec=eb.solve(self.m,self.theta); P=nominal_values(self.m,K,self.theta)
        for j,p in enumerate(P):self.assertLessEqual(np.linalg.eigvalsh(p)[-1],rec['plan']['coefficient_envelope'][j]+1e-13)

    def test_independent_full_policy_certificate(self):
        K,_,_=eb.solve(self.m,self.theta)
        self.assertLessEqual(certify(self.m,K,self.theta)['policy_gap_upper'],1e-4)

    def test_optimum_is_only_a_test_comparator(self):
        K,_,_=eb.solve(self.m,self.theta); Ko,_,_=candidate(self.m,self.theta,'structural')
        P,c=evaluate_with_constants(self.m,K,self.theta); Po,co=evaluate_with_constants(self.m,Ko,self.theta)
        gap=3*max(0.,np.linalg.eigvalsh(P[0]-Po[0])[-1])+c-co
        self.assertLessEqual(gap,certify(self.m,K,self.theta)['policy_gap_upper']+1e-12)

    def test_signed_permutation_randomness_preserves_success(self):
        for seed in (7,19,101):
            K,_,r=eb.solve(self.m,self.theta,seed=seed)
            self.assertTrue(r['all_training_thresholds_met'])
            self.assertLessEqual(certify(self.m,K,self.theta)['policy_gap_upper'],1e-4)

    def test_risk_neutral_limit(self):
        K,_,r=eb.solve(self.m,0.)
        self.assertTrue(r['all_training_thresholds_met'])
        self.assertEqual(r['plan']['domain_margins'],[1.]*5)
        self.assertLessEqual(certify(self.m,K,0.)['policy_gap_upper'],1e-4)

    def test_single_date_needs_no_fit(self):
        m=economy(2,'anchor',1); K,_,r=eb.solve(m,8.)
        self.assertEqual(r['hidden_updates'],0)
        self.assertEqual(r['dates'],[])
        self.assertLessEqual(certify(m,K,8.)['policy_gap_upper'],1e-4)

    def test_budget_monotone_in_precision(self):
        self.assertGreaterEqual(eb.plan(self.m,self.theta,1e-6)['total_ideal_iteration_cap'],eb.plan(self.m,self.theta,1e-3)['total_ideal_iteration_cap'])

    def test_primitives_not_mutated(self):
        before=copy.deepcopy(self.m); eb.solve(self.m,self.theta)
        for key in ('A','B','Q','R','Qf','Sigma'):np.testing.assert_array_equal(self.m[key],before[key])

    def test_invalid_tolerance_or_slack(self):
        for value in (0.,-1.,math.nan,math.inf):
            with self.assertRaises(ValueError):eb.plan(self.m,self.theta,tolerance=value)
            with self.assertRaises(ValueError):eb.plan(self.m,self.theta,slack=value)

    def test_invalid_risk(self):
        for value in (-1.,math.nan,math.inf):
            with self.assertRaises(ValueError):eb.plan(self.m,value)

    def test_domain_failure_is_explicit(self):
        with self.assertRaises(ArithmeticError):eb.plan(self.m,1e6)

    def test_reference_shape_rejected(self):
        with self.assertRaises(ValueError):eb.plan(self.m,self.theta,reference_gain=np.eye(3))

    def test_noncoercive_cost_rejected(self):
        m=copy.deepcopy(self.m);m['R'][0,0,0]=0.
        with self.assertRaises(ValueError):eb.plan(m,self.theta)

    def test_tube_accepts_inaccurate_symmetric_centers(self):
        K,_,_=eb.solve(self.m,self.theta); C=nominal_values(self.m,K,self.theta)
        shifted=C.copy();shifted[:-1]+=1e-7*np.eye(3)
        _,r,_=evaluation_tube(self.m,K,self.theta,shifted)
        for t in range(5):self.assertLessEqual(np.linalg.norm(C[t]-shifted[t],2),r[t])

    def test_tube_rejects_wrong_terminal(self):
        K,_,_=eb.solve(self.m,self.theta); C=nominal_values(self.m,K,self.theta);C[-1]*=1.01
        with self.assertRaises(ValueError):evaluation_tube(self.m,K,self.theta,C)

    def test_execution_contract_is_separate(self):
        K,_,_=eb.solve(self.m,self.theta)
        cert=certify(self.m,K,self.theta,1e-9)
        self.assertGreater(cert['implementation_gap_upper'],0)
        self.assertGreater(cert['policy_gap_upper'],cert['nominal_policy_gap_upper'])

    def test_initial_state_radius_only_changes_allocation(self):
        p=eb.plan(self.m,self.theta);m=copy.deepcopy(self.m);m['initial_radius_sq']*=2
        p2=eb.plan(m,self.theta)
        self.assertEqual(p['coefficient_envelope'],p2['coefficient_envelope'])
        self.assertLessEqual(p2['local_scale'],p['local_scale'])

if __name__=='__main__':unittest.main()
