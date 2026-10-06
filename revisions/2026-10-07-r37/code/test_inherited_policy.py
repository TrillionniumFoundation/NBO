"""Regression tests for R34. Each suite runs in its own process."""
from fractions import Fraction as F
import copy
import unittest
import adaptive_refresh as ar
qr = ar.qr
r = ar.r


def economy(d=2, dates=3, epsilon=F(1, 10000), theta=F(1, 10)):
    A = r.eye(d, F(1, 10))
    if d > 1:
        A[0][1] = F(1, 50)
    stage = dict(A=A, B=r.eye(d), Q=r.eye(d), R=r.eye(d),
                 L=r.eye(d, 0), q=1, r=1)
    stages = [copy.deepcopy(stage) for _ in range(dates)]
    kw = dict(stages=stages, terminal=r.eye(d), covariance=r.eye(d, F(1, 1000)),
              beta=F(19, 20), theta=theta, eta=F(1, 10), epsilon=epsilon,
              initial_radius=d)
    return kw


def local_example():
    plan = r.allocate(**economy(dates=1))
    x = plan['stages'][0]
    S = r.transform(plan['terminal'], plan['covariance'], plan['theta'])
    center = r.scale(S, plan['d'])
    return plan, x, S, center


class RobustPolicyTests(unittest.TestCase):
    def test_exact_inverse_with_pivot(self):
        A = r.matrix([[0, 2], [3, 1]])
        self.assertEqual(r.mm(A, r.inverse(A)), r.eye(2))

    def test_singular_inverse_rejected(self):
        with self.assertRaises(ValueError):
            r.inverse([[1, 2], [2, 4]])

    def test_noncommuting_risk_transform(self):
        P = r.matrix([[2, F(1, 4)], [F(1, 4), 1]])
        C = r.matrix([[F(1, 100), 0], [0, F(1, 200)]])
        self.assertNotEqual(r.mm(P, C), r.mm(C, P))
        S = r.transform(P, C, F(1, 10))
        self.assertEqual(S, r.tr(S))
        r.psd(S)

    def test_terminal_transform_is_not_raw_terminal(self):
        p, x, S, _ = local_example()
        self.assertNotEqual(r.greedy(x, S, p['beta']),
                            r.greedy(x, p['terminal'], p['beta']))
        self.assertEqual(r.transform(p['terminal'], p['covariance'], 0), p['terminal'])

    def test_last_date_has_actor_allowance(self):
        p = r.allocate(**economy(dates=1))
        self.assertEqual(p['lam'][0], 1)
        self.assertGreater(p['gap_bound'], 0)
        self.assertLessEqual(p['gap_bound'], p['epsilon'])

    def test_tighter_tolerance_reduces_allocation(self):
        p = r.allocate(**economy())
        q = r.allocate(**economy(epsilon=F(1, 100000)))
        self.assertLess(q['s'], p['s'])
        self.assertEqual(q['pbar'], p['pbar'])

    def test_inputs_are_not_mutated(self):
        kw = economy(); before = copy.deepcopy(kw)
        r.allocate(**kw)
        self.assertEqual(kw, before)

    def test_primitive_budget_does_not_evaluate_targets(self):
        original = r.transform
        def forbidden(*args, **kwargs):
            raise AssertionError('Primitive budget evaluated a policy target')
        try:
            r.transform = forbidden
            r.allocate(**economy())
        finally:
            r.transform = original

    def test_domain_failure_is_explicit(self):
        with self.assertRaisesRegex(ValueError, 'domain'):
            r.allocate(**economy(theta=1000))

    def test_noncoercive_cost_rejected(self):
        kw = economy(); kw['stages'][0]['Q'] = r.eye(2, 0)
        with self.assertRaises(ValueError):
            r.allocate(**kw)

    def test_dimension_mismatch_rejected(self):
        kw = economy(); kw['stages'][0]['B'] = r.matrix([[1, 0]])
        with self.assertRaises(ValueError):
            r.allocate(**kw)

    def test_target_radius_is_checked_two_sided(self):
        truth = r.eye(2, 2); e = F(1, 100)
        center = r.add(truth, r.eye(2, e))
        r.target_radius(center, truth, e)
        with self.assertRaises(ValueError):
            r.target_radius(center, truth, e/2)

    def test_spectral_radius_needs_dimension_factor(self):
        e = F(1, 100); E = r.eye(4, e)
        self.assertEqual(r.norm2(E), 4*e*e)
        self.assertGreater(r.norm2(E), e*e)
        # Compare exact squared norms; separately test the outward enclosure.
        # sqrt_up(4)*e is exact 1/50, whereas sqrt_up(1/2500) is
        # generally strictly larger than 1/50 on the dyadic grid.
        self.assertEqual((r.sqrt_up(F(4))*e)**2, r.norm2(E))
        self.assertGreaterEqual(r.sqrt_up(r.norm2(E))**2, r.norm2(E))

    def test_overshooting_gram_is_admissible(self):
        p, x, S, center = local_example()
        gram = r.add(center, r.eye(2, F(1, 100000)))
        actor = r.greedy(x, r.scale(gram, F(1, 2)), p['beta'])
        check = r.local_gate(p, 0, gram, center, actor)
        self.assertEqual(check['actor_error_upper'], 0)
        self.assertGreater(check['gram_error_upper'], 0)

    def test_actor_error_consumes_budget(self):
        p, x, S, center = local_example()
        actor = r.greedy(x, S, p['beta'])
        small = r.add(actor, r.eye(2, F(1, 100000)))
        check = r.local_gate(p, 0, center, center, small)
        self.assertGreater(check['actor_error_upper'], 0)
        with self.assertRaises(ValueError):
            r.local_gate(p, 0, center, center, r.add(actor, r.eye(2)))

    def test_magnitude_gate_is_not_omitted(self):
        p, x, S, center = local_example()
        gram = r.add(center, r.eye(2, 10))
        actor = r.greedy(x, r.scale(gram, F(1, 2)), p['beta'])
        with self.assertRaisesRegex(ValueError, 'magnitude'):
            r.local_gate(p, 0, gram, center, actor)

    def test_four_date_exact_policy_envelope(self):
        p = r.allocate(**economy(dates=4)); P = p['terminal']
        for t in range(3, -1, -1):
            x = p['stages'][t]
            S = r.transform(P, p['covariance'], p['theta'])
            gram = r.scale(S, 2); actor = r.greedy(x, S, p['beta'])
            check = r.local_gate(p, t, gram, gram, actor)
            self.assertEqual(check['exact_residual_upper'], 0)
            P = r.own_coefficient(x, actor, S, p['beta'])
            r.psd(r.add(r.eye(2, p['pbar'][t]), P, -1))

    def test_continuation_independent_action(self):
        kw = economy(dates=1); kw['stages'][0]['B'] = r.eye(2, 0)
        p = r.allocate(**kw)
        check = r.local_gate(p, 0, r.eye(2, 2), r.eye(2), r.eye(2, 0))
        self.assertEqual(check['exact_residual_upper'], 0)

    def test_mixed_radius_dominates_exact_residual(self):
        p, x, S, truth = local_example(); e = F(1, 100000)
        center = r.add(truth, r.matrix([[e, 0], [0, -e]]))
        r.target_radius(center, truth, e)
        actor = r.greedy(x, r.scale(center, F(1, 2)), p['beta'])
        check = r.local_gate(p, 0, center, center, actor, e)
        D = r.add(r.mm(x['R'], actor),
                  r.scale(r.mm(r.mm(r.tr(x['B']), S), check['closed']), p['beta']), -1)
        self.assertLessEqual(r.norm2(D), check['exact_residual_upper']**2)

    def test_invalid_coefficients_rejected(self):
        for bad in (True, float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                r.matrix([[bad]])


if __name__ == '__main__':
    unittest.main()
