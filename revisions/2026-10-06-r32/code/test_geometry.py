"""Independent checks of R32 algebra, failure cases, and the terminal actor."""
from pathlib import Path
from fractions import Fraction as F
import math
import sys
import unittest
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
for rev in ('2026-10-05-r23', '2026-10-06-r27', '2026-10-06-r28', '2026-10-06-r29'):
    sys.path.insert(0, str(ROOT/'revisions'/rev/'code'))
import curvature_certificate as cc
from experiment import economy
from entropic_budget import solve
from entropic_certificate import nominal_transform
from residual_certificate import certify


class GeometryTests(unittest.TestCase):
    def test_exact_minimum(self):
        out = cc.certificate(np.eye(2), np.eye(2), m=1.)
        self.assertEqual(out['gram_error_upper'], 0.)

    def test_zero_gradient_saddle_rejected(self):
        with self.assertRaises(ValueError):
            cc.certificate(np.zeros((2, 2)), np.eye(2), m=1.)

    def test_singular_partial_fit_rejected(self):
        with self.assertRaises(ValueError):
            cc.certificate(np.diag([1., 0.]), np.eye(2), m=1., kappa=.25)

    def test_approximate_positive_factor(self):
        w = np.diag([.875, 1.125])
        out = cc.certificate(w, np.eye(2), m=1.)
        self.assertLessEqual(np.linalg.norm(w.T@w-np.eye(2), 'fro'), out['gram_error_upper'])

    def test_nondiagonal_factor(self):
        w = np.array([[1., .25], [-.125, 1.]])
        target = w.T@w
        out = cc.certificate(w, target, m=.5)
        self.assertEqual(out['gram_error_upper'], 0.)

    def test_inexact_target_uses_frobenius_allowance(self):
        w = np.eye(3)
        supplied = np.eye(3)
        true_target = supplied+np.diag([.125, -.125, .125])
        out = cc.certificate(w, supplied, m=.75, target_radius=.125)
        self.assertLessEqual(np.linalg.norm(w.T@w-true_target, 'fro'), out['gram_error_upper'])
        self.assertGreaterEqual(out['factor_frobenius_upper'], math.sqrt(3))

    def test_curvature_margin_rejected(self):
        with self.assertRaises(ValueError):
            cc.certificate(np.eye(2), np.eye(2), m=.5, kappa=.25, target_radius=.25)

    def test_full_hessian_formula(self):
        w = np.array([[1., .25], [-.125, 1.]])
        m = np.eye(2)
        h = np.array(cc.hessian(cc.matrix(w), cc.matrix(m)), dtype=float)
        z = np.array([[.25, -.5], [1., .125]])
        exact = .5*np.linalg.norm(w.T@z+z.T@w, 'fro')**2+np.trace((w.T@w-m)@z.T@z)
        self.assertAlmostEqual(float(z.ravel()@h@z.ravel()), exact, places=13)
        np.testing.assert_array_equal(h, h.T)

    def test_zero_pivot_psd_rule(self):
        cc.psd_pivots(cc.matrix([[0, 0], [0, 1]]))
        with self.assertRaises(ValueError):
            cc.psd_pivots(cc.matrix([[0, 1], [1, 1]]))

    def test_nonfinite_and_nonsymmetric_rejected(self):
        with self.assertRaises(ValueError):
            cc.certificate([[math.nan]], [[1.]], m=1.)
        with self.assertRaises(ValueError):
            cc.certificate(np.eye(2), [[1., .1], [0., 1.]], m=.5)

    def test_outward_sqrt_retains_exact_inequality(self):
        for q in (F(2), F(1, 3), F(7, 2**1000), F(0)):
            x = cc.sqrt_upper(q)
            self.assertGreaterEqual(F.from_float(x)**2, q)

    def test_terminal_actor_uses_risk_transform(self):
        model = economy(2, 'anchor', 1)
        theta = 8.
        k, _, record = solve(model, theta)
        a, b, r = (model[n][0] for n in ('A', 'B', 'R'))
        beta = model['beta']; p = nominal_transform(model['Qf'], model['Sigma'], theta)
        expected = np.linalg.solve(r+beta*b.T@p@b, beta*b.T@p@a)
        wrong = np.linalg.solve(r+beta*b.T@model['Qf']@b, beta*b.T@model['Qf']@a)
        np.testing.assert_allclose(k[0], expected, rtol=0., atol=1e-14)
        self.assertGreater(np.linalg.norm(k[0]-wrong), 1e-6)
        self.assertEqual(record['hidden_updates'], 0)
        self.assertLessEqual(certify(model, k, theta)['policy_gap_upper'], 1e-4)

    def test_terminal_risk_neutral_boundary(self):
        model = economy(2, 'anchor', 1)
        k, _, _ = solve(model, 0.)
        a, b, r = (model[n][0] for n in ('A', 'B', 'R'))
        p, beta = model['Qf'], model['beta']
        expected = np.linalg.solve(r+beta*b.T@p@b, beta*b.T@p@a)
        np.testing.assert_allclose(k[0], expected, rtol=0., atol=1e-14)

    def test_sharper_scalar_contraction(self):
        for lam in (.5, 1., 2.):
            alpha, c = .125, .125
            x = c
            for _ in range(30):
                nxt = x*(1+alpha*(lam-x))**2
                self.assertLessEqual(nxt, lam+1e-14)
                self.assertLessEqual(lam-nxt, (1-2*alpha*c)*(lam-x)+1e-14)
                x = nxt

if __name__ == '__main__':
    unittest.main()
