"""Independent exact acquisition audit: Newton-Cotes and Legendre projection.

This file does not import the production integrator, basis builder or solver.
The original square's upper triangle is mapped to the unit square by
(x,t) -> (x,1-x+x*t), with Jacobian x. Nine rational Newton-Cotes nodes integrate
all polynomials used here exactly. Projection uses orthogonal Legendre norms,
not normal equations. Both algorithms use Python's rational arithmetic kernel.
"""
from fractions import Fraction as Q
from pathlib import Path
import json


def multiply_univariate(a, b):
    result = [Q(0)] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            result[i + j] += u * v
    return result


def quadrature(order=8):
    nodes = [Q(i, order) for i in range(order + 1)]
    weights = []
    for i, x in enumerate(nodes):
        polynomial = [Q(1)]
        denominator = Q(1)
        for j, y in enumerate(nodes):
            if j != i:
                polynomial = multiply_univariate(polynomial, [-y, Q(1)])
                denominator *= x - y
        weights.append(sum((v / (k + 1) for k, v in enumerate(polynomial)), Q(0)) / denominator)
    for degree in range(order + 1):
        if sum((w * x ** degree for x, w in zip(nodes, weights)), Q(0)) != Q(1, degree + 1):
            raise ArithmeticError("quadrature exactness failure")
    return nodes, weights


def legendre(degree, x):
    if degree == 0:
        return Q(1)
    if degree == 1:
        return 2 * x - 1
    if degree == 2:
        return 6 * x * x - 6 * x + 1
    raise ValueError("degree exceeds the declared quadratic comparator")


def audit():
    nodes, weights = quadrature()
    indices = [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)]
    coefficients = {}
    for i, j in indices:
        moment = Q(i == 0 and j == 0)
        for x, wx in zip(nodes, weights):
            for t, wt in zip(nodes, weights):
                y = 1 - x + x * t
                moment += wx * wt * x * x * t * legendre(i, x) * legendre(j, y)
        coefficients[i, j] = moment * (2 * i + 1) * (2 * j + 1)
    one_d = {0: [Q(1)], 1: [Q(-1), Q(2)], 2: [Q(1), Q(-6), Q(6)]}
    monomials = {}
    for (i, j), c in coefficients.items():
        for k, a in enumerate(one_d[i]):
            for l, b in enumerate(one_d[j]):
                monomials[k, l] = monomials.get((k, l), Q(0)) + c * a * b

    def fitted(x, y):
        return sum((c * legendre(i, x) * legendre(j, y)
                    for (i, j), c in coefficients.items()), Q(0))

    def loss(evaluator):
        value = Q(0)
        # lower triangle (x,(1-x)*t), upper triangle (x,1-x+x*t)
        for x, wx in zip(nodes, weights):
            for t, wt in zip(nodes, weights):
                lower_y = (1 - x) * t
                upper_y = 1 - x + x * t
                value += wx * wt * ((1 - x) * (evaluator(x, lower_y) - 1) ** 2
                                     + x * (evaluator(x, upper_y) - x - upper_y) ** 2) / 6
        return value

    additive = lambda x, y: Q(5, 6) + (x*x + y*y) / 2
    # Enumerate all stationary edge and interior points for this quadratic.
    candidates = [(Q(x), Q(y)) for x in (0, 1) for y in (0, 1)]
    candidates += [(Q(3, 5), Q(0)), (Q(0), Q(3, 5)), (Q(3, 11), Q(3, 11))]
    extrema = [fitted(x, y) for x, y in candidates]
    return {
        "quadrature_nodes": len(nodes),
        "polynomial_exactness_degree_per_coordinate": 8,
        "legendre_coefficients": {str(k): str(v) for k, v in coefficients.items()},
        "quadratic_coefficients": [str(monomials[k]) for k in indices],
        "quadratic_expected_regret": str(loss(fitted)),
        "additive_expected_regret": str(loss(additive)),
        "quadratic_range": [str(min(extrema)), str(max(extrema))],
        "shared_kernel": "Python fractions.Fraction only; no shared fitting or integration routines",
    }


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "results99" / "independent.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(audit(), indent=2) + "\n")
    print(out)
