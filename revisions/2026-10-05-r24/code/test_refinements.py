"""Independent checks; tests are evidence for code, not substitutes for proofs."""
import math
import unittest
import mpmath as mp
import numpy as np
from refinements import (Ball, learning_budget, propagated_training_bound,
                         energy_bound, certify_refined)
from experiment import economy, riccati, evaluate

mp.mp.dps = 90


def mm(a):
    a = np.asarray(a)
    return mp.matrix([[mp.mpf(float(a[i, j])) for j in range(a.shape[1])]
                      for i in range(a.shape[0])])


def frob(a):
    return mp.sqrt(mp.fsum(v * v for v in a))


def exact_energy(H, D, q):
    hm, dm = mm(H), mm(D)
    invq = mp.diag([1 / mp.sqrt(mp.mpf(float(v))) for v in q])
    mat = invq * dm.T * (hm ** -1) * dm * invq
    mat = (mat + mat.T) / 2
    return max(mp.eigsy(mat, eigvals_only=True))


class LearningTests(unittest.TestCase):
    def test_zero_error(self):
        self.assertEqual(learning_budget(1, 2, 0, 1e-6)['steps'], 0)

    def test_already_below_target(self):
        self.assertEqual(learning_budget(1, 2, .01, .02)['steps'], 0)

    def test_budget_positive(self):
        out = learning_budget(1, 2, .2, .001)
        self.assertGreater(out['steps'], 0)
        self.assertLessEqual(out['residual_bound'], .001 * (1 + 1e-12))

    def test_basin_rejected(self):
        with self.assertRaises(ValueError): learning_budget(1, 2, .5001, .01)

    def test_zero_curvature_rejected(self):
        with self.assertRaises(ValueError): learning_budget(0, 2, .1, .01)

    def test_inconsistent_spectrum_rejected(self):
        with self.assertRaises(ValueError): learning_budget(2, 1, .1, .01)

    def test_nonfinite_rejected(self):
        for v in (float('inf'), float('nan')):
            with self.assertRaises(ValueError): learning_budget(1, v, .1, .01)

    def test_oversized_step_rejected(self):
        with self.assertRaises(ValueError): learning_budget(1, 2, .1, .01, 1)

    def test_noncommuting_descent_high_precision(self):
        M = mp.matrix([[1, 0], [0, mp.mpf('1.4')]])
        W = mp.matrix([[mp.mpf('1.01'), mp.mpf('.025')],
                       [mp.mpf('-.018'), mp.sqrt(mp.mpf('1.4'))]])
        alpha = 1 / (8 * mp.mpf('2.4'))
        e0 = frob(W.T * W - M)
        self.assertLess(e0, mp.mpf('.5'))
        self.assertGreater(frob(M * (W.T * W) - (W.T * W) * M), 0)
        for j in range(1, 81):
            W -= alpha * W * (W.T * W - M)
            self.assertLessEqual(frob(W.T * W - M),
                                 e0 * (1 - alpha) ** (mp.mpf(j) / 2))
            self.assertGreaterEqual(min(mp.eigsy(W.T * W, eigvals_only=True)),
                                    mp.mpf('.5'))

    def test_rectangular_trainable_factor(self):
        M = mp.eye(2)
        W = mp.matrix([[1, mp.mpf('.02')], [mp.mpf('.01'), 1],
                       [mp.mpf('.03'), mp.mpf('-.01')]])
        e0 = frob(W.T * W - M)
        alpha = mp.mpf(1) / 16
        for j in range(1, 33):
            W -= alpha * W * (W.T * W - M)
            self.assertLessEqual(frob(W.T * W - M),
                                 e0 * (1 - alpha) ** (mp.mpf(j) / 2))

    def test_perturbation_recursion(self):
        out = propagated_training_bound(1, 2, .1, 1 / 24, [1e-12] * 30)
        self.assertTrue(out['basin_verified'])
        b = mp.mpf('.1'); alpha = mp.mpf(float(1 / 24))
        for observed in out['history'][1:]:
            omega = mp.mpf(float(1e-12))
            b = mp.sqrt(1 - alpha) * b + 2 * mp.sqrt(mp.mpf('2.5')) * omega + omega**2
            self.assertGreaterEqual(mp.mpf(observed), b)

    def test_perturbation_leaves_basin(self):
        out = propagated_training_bound(1, 2, .4, 1 / 24, [1.0])
        self.assertFalse(out['basin_verified'])

    def test_invalid_perturbation(self):
        with self.assertRaises(ValueError):
            propagated_training_bound(1, 2, .1, 1 / 24, [-.1])

    def test_stale_target_is_not_own_policy(self):
        # Exact fit to S=1, actor greedy for S, but returned own P=3.
        Hfit = 2.0; K = .5; P = 3.0; Hown = 1 + P
        z = Hfit * K - 1
        D = Hown * K - P
        self.assertEqual(z, 0)
        self.assertEqual(D, -1)
        self.assertEqual(D, z + (1 - P) * (1 - K))
        self.assertGreater(abs(D), abs(z))


class EnergyTests(unittest.TestCase):
    def check_bound(self, H, D, q, r, proposal=None):
        out = energy_bound(Ball.exact(H), Ball.exact(D), q, r, proposal)
        self.assertGreaterEqual(mp.mpf(out['eta']), exact_energy(H, D, q))
        return out

    def test_scalar(self):
        out = self.check_bound(np.array([[2.]]), np.array([[3.]]), np.array([4.]), 1.)
        self.assertLess(out['eta'], 1.125000000001)

    def test_diagonal_anisotropy(self):
        H = np.diag([1., 10., 100.]); D = np.diag([.1, .5, 2.])
        self.check_bound(H, D, np.array([1., 2., 4.]), .5)

    def test_inaccurate_solve_proposal(self):
        H = np.array([[2., .2], [.2, 3.]])
        D = np.array([[1., -.3], [.4, .1]])
        self.check_bound(H, D, np.array([.5, 2.]), 1., np.full((2, 2), 3.))

    def test_zero_proposal_recovers_frobenius_account(self):
        H = np.eye(3); D = np.diag([1., 2., 3.]); q = np.array([1., 2., 3.])
        out = self.check_bound(H, D, q, 1., np.zeros((3, 3)))
        self.assertGreaterEqual(out['eta'], 14.)
        self.assertLess(out['eta'], 14.00000000001)

    def test_random_spd_high_precision(self):
        rng = np.random.default_rng(32417)
        for _ in range(12):
            C = rng.normal(size=(4, 4))
            H = C.T @ C + np.eye(4)
            D = rng.normal(size=(4, 4))
            q = .2 + rng.uniform(size=4)
            self.check_bound(H, D, q, .5)

    def test_enclosed_input_perturbations(self):
        H = np.array([[2., .1], [.1, 3.]])
        D = np.array([[.3, -.1], [.2, .4]])
        radius = np.full((2, 2), 1e-12)
        out = energy_bound(Ball(H, radius), Ball(D, radius), np.array([1., 2.]), 1.)
        hp = H + np.array([[.2, .3], [.3, -.4]]) * 1e-12
        dp = D + np.array([[.1, -.2], [.3, -.4]]) * 1e-12
        self.assertGreaterEqual(mp.mpf(out['eta']), exact_energy(hp, dp, [1., 2.]))

    def test_tiny_residual(self):
        self.check_bound(np.eye(1), np.array([[1e-160]]), np.ones(1), 1.)

    def test_invalid_positive_bound(self):
        with self.assertRaises(ValueError):
            energy_bound(Ball.exact(np.eye(2)), Ball.exact(np.eye(2)), np.ones(2), 0)

    def test_nonfinite_proposal(self):
        with self.assertRaises(ValueError):
            energy_bound(Ball.exact(np.eye(2)), Ball.exact(np.eye(2)), np.ones(2), 1,
                         np.full((2, 2), np.nan))

    def test_complete_policy_refinement(self):
        model = economy(3, 'anchor', 8)
        gains = np.zeros((8, 3, 3))
        out = certify_refined(model, gains)
        self.assertEqual(out['available_dates'], 8)
        self.assertLessEqual(out['policy_gap_upper'], out['original']['policy_gap_upper'])
        self.assertLess(out['energy_eta_upper'], out['original']['eta'])
        P, c = evaluate(model, gains)
        Ps, cs = evaluate(model, riccati(model))
        actual = 3 * max(np.linalg.eigvalsh(P[0] - Ps[0])) + c[0] - cs[0]
        self.assertGreaterEqual(out['policy_gap_upper'], actual)

    def test_invalid_model_not_hidden_by_fallback(self):
        model = economy(2, 'anchor', 4)
        model['Q'][0, 0, 0] = -1
        with self.assertRaises(ValueError):
            certify_refined(model, np.zeros((4, 2, 2)))

    def test_optimal_comparator_uses_same_verifier(self):
        model = economy(3, 'valuation', 8)
        out = certify_refined(model, riccati(model))
        self.assertLess(out['policy_gap_upper'], 1e-4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
