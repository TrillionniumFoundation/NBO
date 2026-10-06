"""Certified target-metric Newton--Schulz refresh of a trainable square critic.

The polynomial iteration is classical; the R35 result is its complete-step
error, relative transport, and full-policy budget in the NBO construction.
Matrices below are exact rational inputs. No unenclosed BLAS claim is made.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import importlib.util

_BACKEND = Path(__file__).resolve().parents[2]/'2026-10-06-r34/code/robust_policy.py'
_spec = importlib.util.spec_from_file_location('nbo_r35_policy_backend', _BACKEND)
if _spec is None or _spec.loader is None:
    raise ImportError('Preserved R34 policy backend is required')
r = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r)
matrix, mm, tr, add, eye, scale = r.matrix, r.mm, r.tr, r.add, r.eye, r.scale
psd, norm2, sqrt_up, rational = r.psd, r.norm2, r.sqrt_up, r.rational


def relative_gate(factor, target, *, m, radius=F(1, 2)) -> F:
    """Check (1-radius) M <= W'W <= (1+radius) M, without square roots.

    Return a rational, possibly sharper Frobenius/m upper bound when useful.
    The exact Loewner gate remains authoritative when that norm bound is loose.
    """
    w, M = matrix(factor), matrix(target)
    m, radius = map(rational, (m, radius))
    d = len(M)
    if len(M[0]) != d or len(w[0]) != d or len(w) < d:
        raise ValueError('Require p-by-d factor, p>=d, and d-by-d target')
    if not 0 < m or not 0 < radius <= F(1, 2):
        raise ValueError('Positive target floor and radius in (0,1/2] required')
    psd(add(M, eye(d, m), -1))
    H = mm(tr(w), w)
    psd(add(H, scale(M, 1-radius), -1))
    psd(add(scale(M, 1+radius), H, -1))
    return min(radius, sqrt_up(norm2(add(H, M, -1)))/m)


def transport_gate(old_radius, relative_drift, *, radius=F(1, 2)) -> F:
    old, drift, radius = map(rational, (old_radius, relative_drift, radius))
    if not 0 <= old < 1 or not 0 <= drift < 1 or not 0 < radius <= F(1, 2):
        raise ValueError('Invalid relative error, target drift, or basin')
    new = old+drift+old*drift
    if new > radius:
        raise ValueError('Relative transport does not certify a warm start')
    return new


def plan(*, initial, tolerance, factor_error=0, radius=F(1, 2), max_updates=32) -> dict:
    """Exact scalar cap for the spectral relative Gram error.

    factor_error bounds ||Delta M^{-1/2}||_2 for the WHOLE update. The returned
    cap is an upper bound, not the realized cost or a claim about other solvers.
    """
    initial, tolerance, nu, radius = map(rational, (initial, tolerance, factor_error, radius))
    if not 0 < radius <= F(1, 2) or not 0 <= initial <= radius:
        raise ValueError('Initial error outside the proved basin')
    if tolerance <= 0 or nu < 0:
        raise ValueError('Positive tolerance and nonnegative error required')
    if isinstance(max_updates, bool) or not isinstance(max_updates, int) or not 0 <= max_updates <= 32:
        raise ValueError('Integer resource cap in 0..32 required')
    c = (3+radius)/4
    lam = 2*c*radius
    noise = 2*nu+nu*nu
    floor = noise/(1-lam)
    if c*radius*radius+noise > radius:
        raise ValueError('Step error does not preserve the basin')
    bound = initial
    bounds = [bound]
    if initial > tolerance and floor >= tolerance:
        raise ValueError('Requested tolerance is at or below the proved error floor')
    while bound > tolerance:
        if len(bounds)-1 >= max_updates:
            raise ArithmeticError('No acceptance within the declared resource cap')
        bound = c*bound*bound+noise
        bounds.append(bound)
    return dict(updates=len(bounds)-1, bound=bound, bounds=bounds, c=c,
                lipschitz=lam, noise=noise, floor=floor, initial=initial,
                tolerance=tolerance, radius=radius, factor_error=nu)


def ideal_step(factor, target):
    """All hidden weights updated; exact rational target solve, no sqrt label."""
    w, M = matrix(factor), matrix(target)
    H = mm(tr(w), w)
    X = mm(r.inverse(M), H)
    if mm(M, X) != H:
        raise ArithmeticError('Target linear solve failed its exact residual check')
    return scale(mm(w, add(eye(len(M), 3), X, -1)), F(1, 2))


def quantized_step(factor, target, *, m, bits=40):
    """Exact products/solve, followed by nearest dyadic rounding.

    The upper bound divides by a downward rational sqrt(m), not by a rounded
    nominal square root. Positivity and dimensions are verified by the gate.
    """
    if isinstance(bits, bool) or not isinstance(bits, int) or not 1 <= bits <= 128:
        raise ValueError('Dyadic precision in 1..128 required')
    relative_gate(factor, target, m=m)
    u = ideal_step(factor, target)
    grid = 1 << bits
    w = [[F(round(x*grid), grid) for x in row] for row in u]
    absolute = sqrt_up(F(len(w)*len(w[0])))/(2*grid)
    if norm2(add(w, u, -1)) > absolute*absolute:
        raise ArithmeticError('Dyadic rounding allowance violated')
    return w, absolute/r.sqrt_down(m)


def solve_error_bound(*, radius, whitened_solve_residual, other_step_error=0):
    """For M X=H+R: Delta=-W M^{-1}R/2 plus independently enclosed work."""
    radius, residual, other = map(rational, (radius, whitened_solve_residual, other_step_error))
    if not 0 < radius <= F(1, 2) or min(residual, other) < 0:
        raise ValueError('Invalid solve/update error account')
    return sqrt_up(1+radius)*residual/2+other


def economic_residual(*, gram_radius, center_B_squared, center_F_squared,
                      evaluation_radius, b_norm, f_frobenius, actor_error,
                      beta, dimension):
    """Action-weighted bound; center_B^2 >= ||B'MB||_2,
    center_F^2 >= tr(F'MF). Target evaluation radius is spectral and absolute.
    """
    vals = list(map(rational, (gram_radius, center_B_squared, center_F_squared,
        evaluation_radius, b_norm, f_frobenius, actor_error, beta)))
    if min(vals) < 0 or isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1:
        raise ValueError('Nonnegative bounds and positive integer dimension required')
    rho, B2, F2, e, b, f, z, beta = vals
    return z+beta/dimension*(sqrt_up(B2*F2)*rho+b*f*e)


def policy_relative_allowance(*, gram_allowance, dimension, target_upper):
    a, L = map(rational, (gram_allowance, target_upper))
    if a <= 0 or L <= 0 or isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1:
        raise ValueError('Positive Gram allowance, dimension and target upper bound required')
    return min(F(1, 2), a/(sqrt_up(dimension)*L))
