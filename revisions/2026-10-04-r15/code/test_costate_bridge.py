"""Manufactured mathematical gates; no fitted confirmatory stream is loaded."""
from collections import defaultdict
import math
import json
from pathlib import Path
import tempfile
import unittest

import mpmath as mp
import numpy as np
import torch

import costate_bridge as cb
import training_core as core


PARAMS = dict(T=1., discount=.04, productivity=.1, coupling=.15,
              idiosyncratic_sigma=.6, common_sigma=.3, adjustment=.2,
              lower=.02, upper=2., CHI=.03)


class ProtectedBellmanBridge(unittest.TestCase):
    def setUp(self):
        core.configure_primitives(PARAMS)
        self.d, self.steps = 3, 8
        self.weights = cb.pc.weights(self.steps)
        self.support = cb.verifier.population(self.d)
        self.critic = core.SplitCritic(self.d, PARAMS, width=1, time_width=1)
        self.protected = cb.ProtectedCritic(self.critic, PARAMS)
        self.account = cb.global_account(self.d, self.steps, .1, self.support,
            self.weights, dict(components=[dict(initial_spread_upper=.5)],
                               bias_upper=0., anchor_upper=0.),
            self.protected, PARAMS)

    def test_nonzero_scalar_critic_against_high_precision_derivative(self):
        # One neuron per layer has a closed scalar chain-rule expression.
        with torch.no_grad():
            self.critic.space[0].weight[:] = torch.tensor([[0., .4, -.2, .1]])
            self.critic.space[0].bias.zero_()
            self.critic.space[2].weight[:] = .3
            self.critic.space[2].bias.zero_()
            self.critic.space[4].weight[:] = .2
            self.critic.space[4].bias.zero_()
        protected = cb.ProtectedCritic(self.critic, PARAMS)
        x = np.array([[.5, -.3, .7], [-.2, .1, .9]])
        dates = np.array([.25, .75])
        _, q = protected.jet(dates, x)
        with mp.workdps(80):
            gamma = 2*mp.mpf(PARAMS['CHI'])*mp.exp(-mp.mpf(PARAMS['discount']))
            for r in range(2):
                v = [mp.mpf(float(xx)) for xx in x[r]]
                a, b, c = map(mp.mpf, [.4, -.2, .1])
                pre = a*v[0]+b*v[1]+c*v[2]
                h1 = mp.tanh(pre)
                h2 = mp.tanh(mp.mpf(.3)*h1)
                slope = (1-mp.mpf(float(dates[r])))*mp.mpf(.2)*mp.mpf(.3)*(1-h2*h2)*(1-h1*h1)
                for j, w in enumerate([a, b, c]):
                    exact = -gamma*(v[j]-sum(v)/3)+slope*w
                    self.assertLessEqual(mp.mpf(float(q.lo[r, j])), exact)
                    self.assertGreaterEqual(mp.mpf(float(q.hi[r, j])), exact)

    def test_global_grid_nonlinear_adjoint_including_last_node(self):
        nodes = np.array([0, 1, 2, 3, 5, 6, 7])
        x = np.random.default_rng(714).normal(size=(len(nodes), self.d))
        z = np.random.default_rng(715).normal(size=(self.steps, len(nodes), self.d+1)).clip(-10, 10)
        q, radius = cb.reference_path(x, nodes, z, PARAMS, self.weights,
                                     self.account, defaultdict(int))
        weights = {key:torch.from_numpy(cb.pc.midpoint(self.weights[key])) for key in ['A', 'B', 'M']}
        post = torch.from_numpy(np.column_stack(((nodes+1)/self.steps, x)))
        _, autodiff = core.postdecision_target(post, torch.from_numpy(nodes),
            torch.from_numpy(z), PARAMS, weights, torch.from_numpy(core.old.coupling(self.d)))
        self.assertTrue(np.all(cb.norm_float(q-autodiff.numpy()) <= radius))
        self.assertLess(np.max(cb.norm_float(q-autodiff.numpy())), 1e-12)
        self.assertTrue(np.all(radius > 0))

    def test_antithetic_terminal_costate_and_zero_change_identity(self):
        nodes = np.full(5, self.steps-1)
        y = np.random.default_rng(905).normal(size=(5, self.d))
        bank, err, _ = cb.reference_bank(y, nodes, 906, PARAMS, self.weights,
                                         self.account, 2, defaultdict(int))
        expected = -2*PARAMS['CHI']*math.exp(-PARAMS['discount'])*(y-y.mean(1, keepdims=True))
        self.assertTrue(np.all(cb.norm_float(bank-expected) <= err))
        pi = cb.pc.midpoint(self.weights['M'])[nodes]*self.steps
        action = np.repeat(pi[:, None], self.d, axis=1)
        stats, _ = cb.interval_statistics(y, action, nodes, np.full(5, .4),
            PARAMS, self.weights, self.protected, self.account, (bank, err), (bank, err))
        # The target banks need not be independent for this deterministic
        # identity gate; independence is enforced by official bank domains.
        for key in ['M', 'A']:
            self.assertTrue(np.all(stats[key].lo <= 0))
            self.assertTrue(np.all(stats[key].hi >= 0))

    def test_quadratic_support_concave_linear_and_nonconcave(self):
        grad = np.array([[.02, -.1, .03], [.1, -.2, .3], [1., 2., -1.]])
        action = np.full((3, 3), .5)
        gamma = np.array([-1., 0., .1])
        result = cb.quadratic_support(cb.I(grad), action, np.full(3, .3),
                                      np.full(3, .7), gamma)
        with mp.workdps(80):
            for i in range(3):
                values = []
                for j in range(3):
                    g, ga = mp.mpf(float(grad[i, j])), mp.mpf(float(gamma[i]))
                    left = mp.mpf(.3)-mp.mpf(.5)
                    right = mp.mpf(.7)-mp.mpf(.5)
                    v = min(right, max(left, -g/ga)) if ga < 0 else None
                    candidates = [g*left+ga*left*left/2, g*right+ga*right*right/2]
                    if v is not None:
                        candidates.append(g*v+ga*v*v/2)
                    values.append(max(candidates))
                exact = sum(values)/3
                self.assertLessEqual(mp.mpf(float(result.lo[i])), exact)
                self.assertGreaterEqual(mp.mpf(float(result.hi[i])), exact)

    def test_interval_sample_moments_enclose_exact_sample_eb(self):
        rng = np.random.default_rng(1117)
        center = rng.normal(0, .1, 64)
        radius = rng.uniform(.001, .02, 64)
        truth = center+rng.uniform(-1, 1, 64)*radius
        interval = cb.interval_empirical_bernstein(center-radius, center+radius,
            bound=.2, event_alpha=.01, clipping_tail=.0001)
        exact = cb.empirical_bernstein(truth, bound=.2, event_alpha=.01,
                                      clipping_tail=.0001)
        self.assertLessEqual(interval['lower'], exact['lower'])
        self.assertGreaterEqual(interval['upper'], exact['upper'])
        self.assertGreater(interval['sample_moment_arithmetic_cushion'], 0)

    def test_zero_and_subnormal_square_root_enclosures(self):
        for value in [0., 1e-323, 1e-100, 1e-10]:
            enclosed = cb.isqrt(cb.I(value))
            with mp.workdps(100):
                exact = mp.sqrt(mp.mpf(value))
                self.assertLessEqual(mp.mpf(float(enclosed.lo)), exact)
                self.assertGreaterEqual(mp.mpf(float(enclosed.hi)), exact)

    def test_complete_fallback_report_is_exact_zero_gain(self):
        import report_mechanism
        protocol_path = cb.R15/'MECHANISM_PROTOCOL.json'
        protocol = json.loads(protocol_path.read_text())
        with tempfile.TemporaryDirectory(prefix='nbo-r15-manufactured-report-') as temporary:
            root = Path(temporary)
            trials = root/'trials'
            trials.mkdir()
            for d in protocol['dimensions']:
                for seed in protocol['declared_seeds']:
                    ident = f'd{d}_s{seed}'
                    folder = trials/ident
                    folder.mkdir()
                    arrays = {key+suffix:np.zeros(256) for key in cb.STATISTICS
                              for suffix in ['', '_lower', '_upper']}
                    np.savez_compressed(folder/'BRIDGE.npz', **arrays)
                    row = dict(schema='nbo-r15-protected-bridge-v1', trial_id=ident,
                        dimension=d, stream_seed=seed, method_id='nbo', complete=True,
                        paths=256, N_audit=2048, N_train=64,
                        primitives_sha256=protocol['primitives_sha256'],
                        protocol_sha256=cb.sha(protocol_path), assessment_fingerprint='a'*64,
                        numerical_source_commit='b'*40, candidate_source_commit='c'*40,
                        analytic_schedule_fallback=True,
                        ranges={key:0. for key in cb.STATISTICS},
                        clipping_expectation_allowances={key:0. for key in cb.STATISTICS},
                        raw_path='BRIDGE.npz', raw_sha256=cb.sha(folder/'BRIDGE.npz'), counters={},
                        constants=dict(holding_deficit_upper=0., payoff_transfer_upper=0.,
                            anchor_regret_upper=.02, strong_concavity_verified=False,
                            strong_concavity_modulus_lower=0., arithmetic=dict(
                                risk_representation_root_allowance=0.,
                                predicted_gain_representation_allowance=0.,
                                actor_gap_representation_allowance=0.)))
                    cb.write(folder/'BRIDGE.json', row)
                    cb.write(folder/'WORK.json', dict(complete=True, returncode=0,
                        end_to_end_seconds=1., user_cpu_seconds=.7,
                        system_cpu_seconds=.1, peak_rss_kib=1000))
            manifest = report_mechanism.render(protocol_path, trials, root/'report')
            result = json.loads((root/'report/MECHANISM_SUMMARY.json').read_text())
            self.assertEqual(manifest['trial_count'], 32)
            self.assertTrue(all(row['continuous_gain_lower'] == 0.
                                for row in result['dimensions'].values()))
            self.assertEqual(len(manifest['tex_files']), 5)


if __name__ == '__main__':
    unittest.main()
