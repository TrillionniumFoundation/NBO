"""Exact small-matrix checks for the R33 warm-start implication.

This validates stored algebraic inputs and iteration-cap arithmetic. It does
not establish an economic evaluator's target radius, a BLAS roundoff bound,
or the full-policy stopping conditions. Quantized steps use exact rational
products followed by explicitly specified nearest-grid storage rounding.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import isqrt, isfinite
from typing import Sequence

Matrix = list[list[F]]


def rational(value) -> F:
    if isinstance(value, bool):
        raise ValueError('Boolean coefficients are not accepted')
    if isinstance(value, F):
        return value
    if isinstance(value, (int, str)):
        return F(value)
    if not isfinite(float(value)):
        raise ValueError('Finite coefficients required')
    return F.from_float(float(value))


def matrix(values: Sequence[Sequence]) -> Matrix:
    rows = [[rational(x) for x in row] for row in values]
    if not rows or not rows[0] or any(len(r) != len(rows[0]) for r in rows):
        raise ValueError('Nonempty rectangular matrix required')
    return rows


def transpose(a: Matrix) -> Matrix:
    return [list(c) for c in zip(*a)]


def mm(a: Matrix, b: Matrix) -> Matrix:
    if len(a[0]) != len(b):
        raise ValueError('Product dimensions disagree')
    return [[sum((x*y for x, y in zip(row, col)), F())
             for col in zip(*b)] for row in a]


def add(a: Matrix, b: Matrix, scale=1) -> Matrix:
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        raise ValueError('Sum dimensions disagree')
    return [[x+scale*y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def eye(d: int, scale=1) -> Matrix:
    return [[rational(scale) if i == j else F() for j in range(d)] for i in range(d)]


def norm2(a: Matrix) -> F:
    return sum((x*x for row in a for x in row), F())


def sqrt_up(value, bits: int = 96) -> F:
    value = rational(value)
    if value < 0 or not isinstance(bits, int) or not 1 <= bits <= 4096:
        raise ValueError('Nonnegative radicand and 1..4096 bits required')
    scale = 1 << bits
    k = isqrt((value.numerator * scale * scale) // value.denominator)
    if F(k, scale)**2 < value:
        k += 1
    return F(k, scale)


def psd(a: Matrix) -> None:
    if len(a) != len(a[0]) or a != transpose(a):
        raise ValueError('Symmetric square matrix required')
    b = [r[:] for r in a]
    for k in range(len(b)):
        pivot = b[k][k]
        if pivot < 0:
            raise ValueError('Negative PSD pivot')
        if not pivot:
            if any(b[j][k] for j in range(k+1, len(b))):
                raise ValueError('Nonzero zero-pivot column')
            continue
        for i in range(k+1, len(b)):
            for j in range(i, len(b)):
                b[i][j] -= b[i][k]*b[j][k]/pivot
                b[j][i] = b[i][j]


def gate(factor, target, *, m, upper, radius) -> F:
    """Check center spectrum and initial Gram ball exactly; return error bound."""
    w, target = matrix(factor), matrix(target)
    d = len(target)
    if len(target[0]) != d or len(w[0]) != d or len(w) < d:
        raise ValueError('Require a p-by-d factor with p >= d and d-by-d target')
    m, upper, radius = map(rational, (m, upper, radius))
    if not 0 < m <= upper or not 0 < radius <= m/2:
        raise ValueError('Invalid spectral or basin bounds')
    psd(add(target, eye(d, m), -1))
    psd(add(eye(d, upper), target, -1))
    error_squared = norm2(add(mm(transpose(w), w), target, -1))
    if error_squared > radius*radius:
        raise ValueError('Initial factor outside the certified warm basin')
    return min(radius, sqrt_up(error_squared))


def transport_gate(old_error, drift, radius) -> F:
    old_error, drift, radius = map(rational, (old_error, drift, radius))
    if min(old_error, drift) < 0 or radius <= 0 or old_error+drift > radius:
        raise ValueError('Transport bound does not certify the warm basin')
    return old_error+drift


def plan(*, m, upper, radius, alpha, initial, tolerance, factor_error=0,
         max_updates: int = 10000) -> dict:
    """Prove a finite cap by rational arithmetic; no rounded logarithms."""
    m, upper, radius, alpha, initial, tolerance, factor_error = map(
        rational, (m, upper, radius, alpha, initial, tolerance, factor_error))
    if not 0 < m <= upper or not 0 < radius <= m/2:
        raise ValueError('Invalid target or radius bound')
    if not 0 < alpha <= 1/(2*(upper+radius)):
        raise ValueError('Step size is outside the proved interval')
    if not 0 <= initial <= radius or tolerance <= 0 or factor_error < 0:
        raise ValueError('Invalid error or tolerance')
    if not isinstance(max_updates, int) or max_updates < 0:
        raise ValueError('Nonnegative integer cap required')
    q = 1-F(3, 4)*alpha*m
    noise = 2*sqrt_up(upper+radius)*(1+alpha*radius)*factor_error+factor_error**2
    floor = noise/(1-q)
    if floor > radius:
        raise ValueError('Perturbation allowance does not preserve the basin')
    bound = initial
    steps = 0
    if initial > tolerance:
        if tolerance <= floor:
            raise ValueError('Requested tolerance is at or below the proved noise floor')
        # These are exact scalar inequalities. The cap is a resource limit,
        # not a permission to accept an unmet threshold.
        while bound > tolerance:
            if steps >= max_updates:
                raise ArithmeticError('No finite cap certified within the resource limit')
            bound = q*bound+noise
            steps += 1
    return {'updates': steps, 'bound': bound, 'q': q, 'noise': noise,
            'floor': floor, 'initial': initial, 'tolerance': tolerance,
            'radius': radius, 'factor_error': factor_error}


def ideal_step(factor, target, alpha) -> Matrix:
    w, target = matrix(factor), matrix(target)
    alpha = rational(alpha)
    error = add(mm(transpose(w), w), target, -1)
    return mm(w, add(eye(len(target)), error, -alpha))


def quantized_step(factor, target, alpha, *, bits: int = 24) -> tuple[Matrix, F]:
    """Exact product then nearest dyadic rounding; return full-step error bound."""
    if not isinstance(bits, int) or not 1 <= bits <= 128:
        raise ValueError('Storage precision must be 1..128 bits')
    u = ideal_step(factor, target, alpha)
    scale = 1 << bits
    w = [[F(round(x*scale), scale) for x in row] for row in u]
    nu = sqrt_up(F(len(u)*len(u[0])))/(2*scale)
    if norm2(add(w, u, -1)) > nu*nu:
        raise ArithmeticError('Nearest-rounding error contract violated')
    return w, nu


def policy_residual_upper(*, actor_error, beta, b_norm, f_frobenius,
                          dimension: int, gram_error, target_spectral_radius) -> F:
    values = list(map(rational, (actor_error, beta, b_norm, f_frobenius,
                                gram_error, target_spectral_radius)))
    if min(values) < 0 or not isinstance(dimension, int) or dimension < 1:
        raise ValueError('Nonnegative bounds and positive dimension required')
    actor_error, beta, b_norm, f_frobenius, gram_error, radius = values
    return actor_error + beta*b_norm*f_frobenius*(gram_error+radius)/dimension
