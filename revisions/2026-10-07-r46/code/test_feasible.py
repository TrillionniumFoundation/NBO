"""Independent exact checks of feasible-witness transport; no study rewrites."""
from fractions import Fraction as F
import itertools
import unittest

STATES = tuple(itertools.product((F(i, 8) for i in range(9)), repeat=2))
ANCHORS = tuple(itertools.product((F(i, 2) for i in range(3)), repeat=2))
LX, LA, KA = F(1, 8), F(3, 2), F(1, 2)
L = LX + LA * KA


def distance(x, y):
    return sum((abs(a-b) for a, b in zip(x, y)), F(0))


def capacity(x):
    return sum(x, F(0)) / 2


def q(x, a):
    assert 0 <= a <= capacity(x), (x, a)
    return (a-F(3, 4))**2 + x[0]/8 + x[1]/16


def optimum(x):
    return q(x, min(F(3, 4), capacity(x)))


def labels(error):
    answer = []
    for i, x in enumerate(ANCHORS):
        menu = [capacity(x)*j/4 for j in range(5)]
        observed = [(q(x, a) + (error if (i+j)%2 else -error), a)
                    for j, a in enumerate(menu)]
        y, action = min(observed)
        answer.append((x, y, action))
    return answer


def select(x, nodes):
    value, i = min((y + L*distance(x, z), i)
                   for i, (z, y, a) in enumerate(nodes))
    z, y, a = nodes[i]
    return value, min(a, capacity(x)), i


class FeasibleWitnessTests(unittest.TestCase):
    def test_hausdorff_modulus(self):
        for x, z in itertools.product(STATES, repeat=2):
            self.assertLessEqual(abs(capacity(x)-capacity(z)), KA*distance(x, z))

    def test_bellman_modulus(self):
        for x, z in itertools.product(STATES, repeat=2):
            self.assertLessEqual(abs(optimum(x)-optimum(z)), L*distance(x, z))

    def test_exact_repair_and_feasible_graph_transport(self):
        for x, z in itertools.product(STATES, ANCHORS):
            for j in range(5):
                a = capacity(z)*j/4
                repaired = min(a, capacity(x))
                self.assertTrue(0 <= repaired <= capacity(x))
                self.assertLessEqual(abs(a-repaired), KA*distance(x, z))
                self.assertLessEqual(q(x, repaired)-q(z, a), L*distance(x, z))

    def test_noisy_selected_policy_residual(self):
        for error in (F(0), F(1, 100), F(1, 4)):
            nodes = labels(error)
            for x in STATES:
                value, a, _ = select(x, nodes)
                self.assertLessEqual(q(x, a)-value, error)

    def test_optimal_residual_and_policy_sandwich(self):
        # State l1 cover radius is 1/2; maximum node-action radius is 1/8.
        for error in (F(0), F(1, 100), F(1, 4)):
            nodes = labels(error)
            u = LA/8 + error + 2*L*F(1, 2)
            for x in STATES:
                value, a, _ = select(x, nodes)
                self.assertGreaterEqual(value-optimum(x), -error)
                self.assertLessEqual(value-optimum(x), u)
                self.assertGreaterEqual(q(x, a)-optimum(x), 0)
                self.assertLessEqual(q(x, a)-optimum(x), u+error)

    def test_approximate_feasible_repair_is_charged(self):
        error = F(1, 100)
        nodes = labels(error)
        for x in STATES:
            value, _, i = select(x, nodes)
            z, _, anchor_action = nodes[i]
            # Deliberately return the feasible zero action rather than exact clipping.
            zeta = max(F(0), abs(anchor_action)-KA*distance(x, z))
            self.assertLessEqual(q(x, F(0))-value, error+LA*zeta)

    def test_nonminimizing_index_allowance(self):
        error = F(1, 100)
        nodes = labels(error)
        for x in STATES:
            value, _, _ = select(x, nodes)
            for z, y, a in nodes:
                nu = y+L*distance(x, z)-value
                self.assertGreaterEqual(nu, 0)
                self.assertLessEqual(q(x, min(a, capacity(x)))-value, error+nu)

    def test_resource_budget_and_common_action_reduction(self):
        s = F(7, 1000)
        self.assertEqual(s/4 + 2*(s/8) + 2*(s/8) + s/4, s)
        for lx, la in itertools.product((F(0), F(2, 3), F(7, 2)), repeat=2):
            self.assertEqual(lx + la*F(0), lx)
            self.assertEqual(la*F(0), 0)
        # Feasibility is not implied by a small objective error.
        self.assertGreater(F(3, 4), capacity((F(0), F(0))))


if __name__ == '__main__':
    unittest.main(verbosity=2)
