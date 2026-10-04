"""Numerical operator, maximization and deployment tests for the new baselines."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from baselines import (P, old, torch, np, trace_exact, hjb_residuals, hjb_step,
                       make_policy, policy_snapshot, load_policy)
from scalar_baseline import (best_action, implicit_policy_step, equation_residual,
                             equation_residual_enclosure,
                             train_grid, ScalarGridPolicy, evaluate_common_paths,
                             SchedulePolicy)


class Quadratic(torch.nn.Module):
    def __init__(self, hessian):
        super().__init__()
        self.register_buffer("hessian", torch.as_tensor(hessian))

    def forward(self, x):
        y = x[:, 1:]
        return .3 * x[:, :1] + .5 * (y @ self.hessian * y).sum(1, keepdim=True)


class Affine(torch.nn.Module):
    def forward(self, x):
        return .7 * x[:, :1] + x[:, 1:].mean(1, keepdim=True)


class NeuralBaselineTests(unittest.TestCase):
    def test_covariance_trace_includes_common_noise_cross_derivatives(self):
        matrix = np.array([[2., .4, -.3], [.4, 1.4, .8], [-.3, .8, -.2]])
        xx = torch.tensor([[.2, -.1, .4, .8], [.7, .3, -.2, .1]])
        x, _, _, p = old.first_jet(Quadratic(matrix), xx)
        expected = (P["idiosyncratic_sigma"] ** 2 * np.trace(matrix)
                    + P["common_sigma"] ** 2 * matrix.sum())
        np.testing.assert_allclose(trace_exact(p, x).detach().numpy(), expected, rtol=0., atol=2e-15)
        noisy = dict(P, idiosyncratic_sigma=.6, common_sigma=.3)
        expected_noisy = .6 ** 2 * np.trace(matrix) + .3 ** 2 * matrix.sum()
        np.testing.assert_allclose(trace_exact(p, x, primitives=noisy).detach().numpy(),
                                   expected_noisy, rtol=0., atol=2e-15)

    def test_hjb_sign_and_discount_for_affine_manufactured_value(self):
        states = torch.tensor([[.2, -.7, .4], [.8, .5, -.2]])
        B = torch.tensor(old.coupling(2))
        r1, r2, m = hjb_residuals(Affine(), states, B, None, trace_mode="exact")
        value = .7 * states[:, :1] + states[:, 1:].mean(1, keepdim=True)
        running = (torch.log(m) + states[:, 1:]).mean(1, keepdim=True) - P["adjustment"] / 2. * m.mean(1, keepdim=True) ** 2
        drift = (P["productivity"] + P["coupling"] * torch.tanh(states[:, 1:] @ B.T)
                 - m - (P["idiosyncratic_sigma"] ** 2 + P["common_sigma"] ** 2) / 2.)
        expected = -.7 - running - drift.mean(1, keepdim=True) + P["discount"] * value
        torch.testing.assert_close(r1, expected, rtol=0., atol=1e-14)
        torch.testing.assert_close(r1, r2, rtol=0., atol=0.)

    def test_independent_probe_product_targets_squared_residual(self):
        # Identical collocation points isolate only trace-bank randomness.
        # A single-bank square has a positive variance term; the two-bank
        # product used for training has the exact residual square as its mean.
        n = 16384
        matrix = np.array([[2., .4], [.4, 1.1]])
        xx = torch.tensor([[.3, -.2, .1]]).repeat(n, 1)
        B = torch.tensor(old.coupling(2))
        g = torch.Generator().manual_seed(90513)
        r1, r2, _ = hjb_residuals(Quadratic(matrix), xx, B, g, probes=1)
        exact, _, _ = hjb_residuals(Quadratic(matrix), xx[:1], B, None, trace_mode="exact")
        product = (r1 * r2).detach().numpy().ravel()
        error = abs(product.mean() - float(exact.detach()[0, 0] ** 2))
        self.assertLess(error, 5. * product.std(ddof=1) / np.sqrt(n))
        self.assertFalse(torch.equal(r1, r2))

    def test_greedy_feasible_maximum_and_canonical_snapshot(self):
        p = torch.tensor([[.45, -.15]])
        t = torch.tensor([[.3]])
        m = old.greedy(p, t, .1).numpy().ravel()
        center = float(old.schedule(t))
        grid = np.linspace(center - .1, center + .1, 201)
        aa, bb = np.meshgrid(grid, grid, indexing="ij")
        def H(x, y):
            mean = (x + y) / 2.
            return (np.log(x) + np.log(y)) / 2. - P["adjustment"] * mean ** 2 / 2. - .45 * x + .15 * y
        self.assertGreaterEqual(H(m[0], m[1]) + 1e-13, H(aa, bb).max())
        with tempfile.TemporaryDirectory() as directory:
            torch.manual_seed(171)
            critic = old.Critic(2, 8)
            states = torch.tensor([[.2, -.1, .4], [.7, .3, -.2]])
            optimizer = torch.optim.Adam(critic.parameters(), lr=.001)
            row = hjb_step(critic, states, torch.tensor(old.coupling(2)), optimizer,
                           torch.Generator().manual_seed(77), trace_mode="exact")
            self.assertEqual(row["hessian_vector_product_states"], 6)
            snapshot = policy_snapshot(critic, dimension=2, width=8, epsilon=.1,
                                       iteration=1, seed=171)
            self.assertEqual(snapshot["method"], "neural_hjb")
            path = Path(directory) / "hjb.pt"
            torch.save(snapshot, path)
            loaded, _, metadata = load_policy(path)
            self.assertEqual(metadata["model_kind"], "critic_greedy")
            with torch.no_grad():
                torch.testing.assert_close(loaded(states), make_policy(critic)(states), rtol=0., atol=0.)


class ScalarBaselineTests(unittest.TestCase):
    def test_interval_hamiltonian_encloses_the_actual_two_branch_maximum(self):
        y = np.linspace(-2., 2., 21)
        v = .13 * np.sin(2.1 * y) + 7. * y
        m = best_action(v, y, .2)
        residual, maximum = equation_residual_enclosure(v, v + .1, y, m, .05, .2)
        dx = y[1] - y[0]
        pf, pb = np.diff(v)[1:] / dx, np.diff(v)[:-1] / dx
        d0 = (P["productivity"] - (P["idiosyncratic_sigma"] ** 2 + P["common_sigma"] ** 2) / 2.
              + P["coupling"] * np.tanh(y[1:-1]))
        actual = np.log(m) - P["adjustment"] * m * m / 2. + np.maximum(d0 - m, 0.) * pf + np.minimum(d0 - m, 0.) * pb
        self.assertTrue(np.all(maximum.lo <= actual + 1e-13))
        self.assertTrue(np.all(maximum.hi >= actual - 1e-13))
        self.assertLess(np.max(maximum.hi - maximum.lo), 1e-9)
        numerical = equation_residual(v, v + .1, y, m, .05)
        self.assertTrue(np.all(residual.lo <= numerical + 1e-12))
        self.assertTrue(np.all(residual.hi >= numerical - 1e-12))

    def test_upwind_greedy_compares_both_drift_sign_branches(self):
        y = np.linspace(-2., 2., 21)
        v = .13 * np.sin(2.1 * y) + 7. * y
        m = best_action(v, y, .2)
        pf, pb = np.diff(v)[1:] / (y[1] - y[0]), np.diff(v)[:-1] / (y[1] - y[0])
        d0 = (P["productivity"] - (P["idiosyncratic_sigma"] ** 2 + P["common_sigma"] ** 2) / 2.
              + P["coupling"] * np.tanh(y[1:-1]))
        candidates = np.linspace(P["lower"], P["upper"], 10001)[:, None]
        self.assertTrue(np.any(d0 - m > 0.))
        self.assertTrue(np.any(d0 - m < 0.))
        def objective(a):
            mu = d0 - a
            return np.log(a) - P["adjustment"] * a ** 2 / 2. + np.maximum(mu, 0.) * pf + np.minimum(mu, 0.) * pb
        self.assertTrue(np.all(objective(m) + 1e-12 >= objective(candidates).max(axis=0)))

    def test_implicit_step_is_monotone_and_satisfies_original_equation(self):
        y = np.linspace(-3., 3., 41)
        m = np.linspace(.1, 1.8, len(y) - 2)
        vnext = np.sin(y)
        h = .05
        low = implicit_policy_step(vnext, y, m, h, (-.4, .6))
        upper = implicit_policy_step(vnext + .3, y, m, h, (-.4, .6))
        self.assertLess(np.max(abs(equation_residual(low, vnext, y, m, h))), 1e-12)
        self.assertTrue(np.all(upper >= low - 1e-14))
        self.assertLessEqual(np.max(upper - low), .3 / (1. + P["discount"] * h) + 1e-13)

    def test_trained_scalar_table_is_an_actual_deployed_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            row = train_grid(51, 12, 5., out, epsilon=.1)
            self.assertTrue(row["converged"])
            self.assertLess(row["max_equation_residual"], 1e-8)
            self.assertGreaterEqual(row["max_equation_residual_upper"], row["max_equation_residual"])
            self.assertLess(row["finite_grid_solve_error_bound"], 1e-7)
            policy = ScalarGridPolicy(out / row["policy_path"])
            # Exact interior table nodes, boundary extension, terminal time,
            # and the curved time-dependent action tube are all deployed.
            nodes = torch.tensor([[float(policy.time[3]), float(policy.state[17])],
                                  [0., -8.], [1., 8.], [.319, -.217]])
            with torch.no_grad():
                actions = policy(nodes)
            self.assertAlmostEqual(float(actions[0]), float(policy.action[3, 17]), places=13)
            centers = old.schedule(nodes[:, :1])
            self.assertTrue(bool((abs(actions - centers) <= .1 + 1e-14).all()))
            self.assertAlmostEqual(float(actions[1]), float(centers[1]), places=14)
            result = evaluate_common_paths({"grid": policy, "anchor": SchedulePolicy()},
                                           out, steps=8, paths=32, seed=99901)
            self.assertEqual(len(result["paired_contrasts"]), 1)
            self.assertEqual(result["records"][0]["action_states"], 256)
            self.assertTrue(np.isfinite(result["paired_contrasts"][0]["mean"]))


if __name__ == "__main__":
    unittest.main()
