"""Exact sharpness witnesses; no primary data or production integration imports."""
from fractions import Fraction as F
import unittest


def tail(values, alpha):
    count = int(len(values) * (1 - alpha))
    assert F(count) == len(values) * (1 - alpha)
    return sum(sorted(values)[-count:]) / count


class SharpnessTests(unittest.TestCase):
    def test_two_unit_relu_exactly_attains_the_width_bound(self):
        for n in (8, 16, 32, 64):
            for alpha in (F(1, 2), F(3, 4)):
                for K, R in ((F(1), F(1)), (F(15), F(1, 32))):
                    c = R / n
                    value = lambda z: K * (max(F(0), z-c) + max(F(0), c-z))
                    mids = [value(-R + (2*j+1)*R/n) for j in range(n)]
                    nodes = [value(-R + 2*j*R/n) for j in range(n+1)]
                    ends = [q for j in range(n) for q in (nodes[j], nodes[j+1])]
                    self.assertEqual(tail(ends, alpha)-tail(mids, alpha), K*R/((1-alpha)*n*n))
                    eta = K*alpha*R
                    self.assertEqual(sum(v > eta for v in mids), n*(1-alpha)-1)
                    self.assertEqual(sum(v == eta for v in mids), 2)
                    self.assertEqual(sum(v > eta for v in ends), 2*n*(1-alpha))


if __name__ == '__main__':
    unittest.main(verbosity=2)
