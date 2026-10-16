"""Exact production acquisition and loss for the predeclared R99 mechanism.

Standard library only. Polynomials use (x exponent, y exponent) keys.  No
independent-audit code is imported. All returned numerical claims are rational.
"""
from fractions import Fraction as F
from math import comb
import json
from pathlib import Path

BASIS = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2))


def square_moment(i: int, j: int) -> F:
    if i < 0 or j < 0:
        raise ValueError("nonnegative polynomial exponents required")
    return F(1, (i + 1) * (j + 1))


def upper_triangle_moment(i: int, j: int) -> F:
    """Integral of x**i*y**j on 0<=x<=1, 1-x<=y<=1."""
    return (F(1, i + 1) - sum(
        (F((-1) ** k * comb(j + 1, k), i + k + 1)
         for k in range(j + 2)), F(0))) / (j + 1)


def integrate(poly: dict, triangle: bool = False) -> F:
    moment = upper_triangle_moment if triangle else square_moment
    return sum((F(c) * moment(i, j) for (i, j), c in poly.items()), F(0))


def plus(*polys: dict) -> dict:
    result = {}
    for p in polys:
        for key, value in p.items():
            result[key] = result.get(key, F(0)) + F(value)
    return {k: v for k, v in result.items() if v}


def times(a: dict, b: dict) -> dict:
    result = {}
    for (i, j), c in a.items():
        for (k, l), d in b.items():
            key = (i + k, j + l)
            result[key] = result.get(key, F(0)) + c * d
    return result


def scale(p: dict, c) -> dict:
    return {k: F(c) * v for k, v in p.items()}


def solve(matrix: list, rhs: list) -> list:
    """Rational Gauss-Jordan with deterministic first-nonzero pivots."""
    n = len(rhs)
    if len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("square system required")
    a = [[F(v) for v in row] + [F(rhs[i])] for i, row in enumerate(matrix)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            raise ValueError("singular acquisition system")
        a[k], a[pivot] = a[pivot], a[k]
        divisor = a[k][k]
        a[k] = [v / divisor for v in a[k]]
        for i in range(n):
            if i != k:
                factor = a[i][k]
                a[i] = [u - factor * v for u, v in zip(a[i], a[k])]
    return [row[-1] for row in a]


def loss(h: dict) -> F:
    # v=1+(x+y-1)_+. h-v equals h-1 below the diagonal and h-x-y above it.
    below = plus(h, {(0, 0): -1})
    above = plus(h, {(1, 0): -1, (0, 1): -1})
    squared = integrate(times(below, below))
    squared += integrate(plus(times(above, above), scale(times(below, below), -1)), True)
    return squared / 6


def acquisition() -> dict:
    ridge = {(1, 0): F(1), (0, 1): F(1), (0, 0): F(-1)}
    gram = [[square_moment(i + k, j + l) for k, l in BASIS] for i, j in BASIS]
    rhs = [square_moment(i, j) + integrate(times({(i, j): F(1)}, ridge), True)
           for i, j in BASIS]
    coefficients = solve(gram, rhs)
    quadratic = dict(zip(BASIS, coefficients))
    additive = {(0, 0): F(5, 6), (2, 0): F(1, 2), (0, 2): F(1, 2)}
    normal = [sum((gram[i][j] * coefficients[j] for j in range(6)), F(0)) - rhs[i]
              for i in range(6)]
    if any(normal):
        raise ArithmeticError("nonzero exact normal-equation residual")
    return {
        "basis": [list(z) for z in BASIS],
        "quadratic_coefficients": [str(c) for c in coefficients],
        "gram": [[str(c) for c in row] for row in gram],
        "rhs": [str(c) for c in rhs],
        "normal_equation_residuals": [str(c) for c in normal],
        "additive_l2_squared": str(6 * loss(additive)),
        "quadratic_l2_squared": str(6 * loss(quadratic)),
        "additive_expected_regret": str(loss(additive)),
        "quadratic_expected_regret": str(loss(quadratic)),
        "relu_expected_regret": "0",
        "native_hinge_expected_regret": "0",
        "two_triangle_expected_regret": "0",
        "formula_dictionary_expected_regret": "0",
        "additive_range": ["5/6", "11/6"],
        "quadratic_range": ["143/150", "32/15"],
        "scope": "Exact population acquisition with original-law moments; no sampled fit or investment timing.",
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    output = root / "results99" / "production.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(acquisition(), indent=2) + "\n")
    print(output)
