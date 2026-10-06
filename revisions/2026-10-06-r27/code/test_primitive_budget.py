import copy
import math
import sys
import unittest
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT/'revisions/2026-10-05-r23/code'))
from primitive_budget import allocation, solve
from experiment import economy, evaluate, riccati
from policy_certificate import certify


class PrimitiveBudgetTests(unittest.TestCase):
    def setUp(self):
        self.model = economy(3, 'anchor', horizon=5)

    def test_plan_before_fit(self):
        p = allocation(self.model)
        self.assertEqual(len(p['dates']), 4)
        self.assertGreater(p['total_ideal_iteration_cap'], 0)
        self.assertTrue(all(0 < r['c'] <= r['m'] <= r['L'] for r in p['dates']))

    def test_cap_contraction(self):
        for r in allocation(self.model)['dates']:
            rho = 1-2*r['alpha']*r['c']
            self.assertLessEqual(rho**r['ideal_iteration_cap']*r['initial_error_bound'], r['target']/2*(1+1e-10))

    def test_invalid_tolerance(self):
        for tol in (0., -1., math.nan, math.inf):
            with self.assertRaises(ValueError): allocation(self.model, tol)

    def test_reject_nondiagonal_coercivity_shortcut(self):
        m = copy.deepcopy(self.model); m['Q'][0,0,1] = .1
        with self.assertRaises(ValueError): allocation(m)

    def test_reject_zero_stage_cost(self):
        m = copy.deepcopy(self.model); m['R'][0,0,0] = 0
        with self.assertRaises(ValueError): allocation(m)

    def test_reject_nonfinite_primitive(self):
        m = copy.deepcopy(self.model); m['A'][0,0,0] = math.nan
        with self.assertRaises(ValueError): allocation(m)

    def test_reject_discount(self):
        m = copy.deepcopy(self.model); m['beta'] = 1.1
        with self.assertRaises(ValueError): allocation(m)

    def test_thresholds_and_caps(self):
        _, _, rec = solve(self.model)
        self.assertTrue(rec['all_training_thresholds_met'])
        self.assertLessEqual(rec['hidden_updates'], rec['plan']['total_ideal_iteration_cap'])

    def test_own_target_matches_returned_future(self):
        K, W, rec = solve(self.model)
        P, _ = evaluate(self.model, K)
        for row in rec['dates']:
            j = row['continuation_date']
            err = np.linalg.norm(W[j].T@W[j]-3*P[j], 'fro')
            self.assertLessEqual(err, row['target']*(1+1e-8))

    def test_target_envelope(self):
        K, _, rec = solve(self.model)
        P, _ = evaluate(self.model, K)
        for row in rec['dates']:
            eig = np.linalg.eigvalsh(3*P[row['continuation_date']])
            self.assertGreaterEqual(eig[0]+1e-12, row['m'])
            self.assertLessEqual(eig[-1], row['L'])

    def test_full_policy_certificate(self):
        K, _, _ = solve(self.model)
        self.assertLessEqual(certify(self.model, K, 1e-12)['policy_gap_upper'], 1e-4)

    def test_independent_optimum_crosscheck(self):
        K, _, _ = solve(self.model)
        P, c = evaluate(self.model, K)
        Po, co = evaluate(self.model, riccati(self.model))
        gap = 3*max(0., np.linalg.eigvalsh(P[0]-Po[0])[-1])+c[0]-co[0]
        self.assertLessEqual(gap, certify(self.model, K, 1e-12)['policy_gap_upper']+1e-13)

    def test_one_date_no_training(self):
        m = economy(2, 'anchor', 1); K, _, rec = solve(m)
        self.assertEqual(rec['hidden_updates'], 0)
        self.assertEqual(rec['dates'], [])
        self.assertLessEqual(certify(m, K, 1e-12)['policy_gap_upper'], 1e-4)

    def test_zero_control_channel(self):
        m = copy.deepcopy(self.model); m['B'][:] = 0
        K, _, rec = solve(m)
        self.assertTrue(np.array_equal(K, np.zeros_like(K)))
        self.assertTrue(rec['all_training_thresholds_met'])

    def test_primitives_not_mutated(self):
        m = copy.deepcopy(self.model); solve(m)
        for name in ('A','B','Q','R','Qf','Sigma'):
            np.testing.assert_array_equal(m[name], self.model[name])

    def test_budget_monotonicity(self):
        loose = allocation(self.model, 1e-3)
        tight = allocation(self.model, 1e-6)
        self.assertGreaterEqual(tight['total_ideal_iteration_cap'], loose['total_ideal_iteration_cap'])


if __name__ == '__main__': unittest.main()
