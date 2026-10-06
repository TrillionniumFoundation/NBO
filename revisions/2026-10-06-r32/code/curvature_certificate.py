"""Exact stored-input gradient/curvature diagnostics for square critics.

This is a small-matrix proof checker, not an economic stopping rule. A supplied
spectral target radius is an external mathematical premise. Fractions retain
all bits of a binary float. No numerical eigenvalue is used as a PSD proof.
"""
from __future__ import annotations
from fractions import Fraction as F
import math
from typing import Sequence

Matrix = list[list[F]]


def rational(x) -> F:
    if isinstance(x, F):
        return x
    if isinstance(x, int):
        return F(x)
    x = float(x)
    if not math.isfinite(x):
        raise ValueError('Finite stored coefficients required')
    return F.from_float(x)


def matrix(x: Sequence[Sequence[float]]) -> Matrix:
    ans = [[rational(v) for v in row] for row in x]
    n = len(ans)
    if not n or any(len(row) != n for row in ans):
        raise ValueError('Nonempty square matrix required')
    return ans


def transpose(a: Matrix) -> Matrix:
    return [list(row) for row in zip(*a)]


def mm(a: Matrix, b: Matrix) -> Matrix:
    return [[sum((x*y for x, y in zip(row, col)), F(0))
             for col in zip(*b)] for row in a]


def plus(a: Matrix, b: Matrix, sign: int = 1) -> Matrix:
    return [[x+sign*y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def identity(n: int, scale: F = F(1)) -> Matrix:
    return [[scale if i == j else F(0) for j in range(n)] for i in range(n)]


def squared_norm(a: Matrix) -> F:
    return sum((x*x for row in a for x in row), F(0))


def psd_pivots(a: Matrix) -> list[F]:
    """Exact symmetric elimination, including the zero-pivot PSD condition."""
    if a != transpose(a):
        raise ValueError('Symmetric matrix required')
    b = [row[:] for row in a]
    pivots = []
    for k in range(len(b)):
        p = b[k][k]
        pivots.append(p)
        if p < 0:
            raise ValueError('PSD premise not certified: negative pivot')
        if p == 0:
            if any(b[i][k] != 0 for i in range(k+1, len(b))):
                raise ValueError('PSD premise not certified: nonzero zero-pivot column')
            continue
        for i in range(k+1, len(b)):
            for j in range(i, len(b)):
                b[i][j] -= b[i][k]*b[j][k]/p
                b[j][i] = b[i][j]
    return pivots


def hessian(w: Matrix, target: Matrix) -> Matrix:
    n = len(w)
    wt = transpose(w)
    err = plus(mm(wt, w), target, -1)
    columns = []
    for k in range(n*n):
        z = [[F(0) for _ in range(n)] for _ in range(n)]
        z[k//n][k % n] = F(1)
        hz = plus(mm(z, err), mm(w, plus(mm(transpose(z), w), mm(wt, z))))
        columns.append([v for row in hz for v in row])
    return [list(row) for row in zip(*columns)]


def sqrt_upper(q: F) -> float:
    if q < 0:
        raise ValueError('Negative squared bound')
    if q == 0:
        return 0.
    try:
        x = math.sqrt(float(q))
    except (OverflowError, ValueError) as exc:
        raise ArithmeticError('Bound outside supported floating output range') from exc
    if not math.isfinite(x):
        raise ArithmeticError('Nonfinite output bound')
    while rational(x)*rational(x) < q:
        x = math.nextafter(x, math.inf)
        if not math.isfinite(x):
            raise ArithmeticError('Output bound overflow')
    return x


def certificate(w_values, target_values, *, m: float,
                kappa: float = 0., target_radius: float = 0.) -> dict:
    """Check sufficient premises and return an outward Gram-error bound.

    target_radius bounds the SPECTRAL distance between the supplied symmetric
    target and the exact own-policy target. Establishing that distance belongs
    to the independent evaluator. The returned conditional bound uses ||W||_F.
    """
    w, target = matrix(w_values), matrix(target_values)
    if len(w) != len(target):
        raise ValueError('Matrix dimensions disagree')
    n = len(w)
    floor, curvature, radius = map(rational, (m, kappa, target_radius))
    if floor <= 0 or curvature < 0 or radius < 0 or floor <= curvature+radius:
        raise ValueError('Require m > kappa + target_radius >= 0')
    target_pivots = psd_pivots(plus(target, identity(n, floor+radius), -1))
    curvature_pivots = psd_pivots(plus(hessian(w, target), identity(n*n, curvature)))
    err = plus(mm(transpose(w), w), target, -1)
    grad = mm(w, err)
    gu = sqrt_upper(squared_norm(grad))
    wu = sqrt_upper(squared_norm(w))
    numerator = rational(gu)+rational(wu)*radius
    gap = floor-curvature-radius
    gram = sqrt_upper(F(3)*numerator*numerator/gap)
    return {
        'certified_conditional_on_target_radius': True,
        'dimension': n,
        'gradient_norm_upper': gu,
        'factor_frobenius_upper': wu,
        'gram_error_upper': gram,
        'sigma_min_squared_lower_exact': str(gap/3),
        'target_radius_exact': str(radius),
        'target_floor_pivots_exact': [str(v) for v in target_pivots],
        'hessian_shift_pivots_exact': [str(v) for v in curvature_pivots],
        'scope': 'Exact binary-input algebra; external spectral target-radius premise; not a policy certificate'
    }
