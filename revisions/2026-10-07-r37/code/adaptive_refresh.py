"""Precision-adaptive, target-cached hidden-weight refresh (exact rational model).

Every nonzero update changes the trainable factor. A target inverse is formed
at most once per fixed target, never transported to a different continuation.
The complete update error is checked before accepting its Gram enclosure.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import importlib.util

_BACKEND = Path(__file__).resolve().parents[2]/'2026-10-06-r35/code/quadratic_refresh.py'
_spec = importlib.util.spec_from_file_location('nbo_r37_quadratic_backend', _BACKEND)
if _spec is None or _spec.loader is None:
    raise ImportError('Preserved R35 exact quadratic backend is required')
qr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qr)
r = qr.r


def _integer(x, name, lower, upper):
    if isinstance(x, bool) or not isinstance(x, int) or not lower <= x <= upper:
        raise ValueError(f'{name} must be an integer in {lower}..{upper}')


def precision(bound, *, m, rows, columns, radius=F(1, 2), max_bits=128):
    """Smallest allowed bit count meeting the proved whole-step error budget.

    The actual next bound is c*b^2 + 2*nu + nu^2 <= b^2. The uniform
    recurrence b -> b^2 is used here so bit complexity is explicitly bounded.
    The exact products/target solve are not floating-point approximations.
    """
    bound, m, radius = map(r.rational, (bound, m, radius))
    _integer(rows, 'rows', 1, 1000000)
    _integer(columns, 'columns', 1, rows)
    _integer(max_bits, 'max_bits', 1, 4096)
    if not 0 < bound <= radius <= F(1, 2) or m <= 0:
        raise ValueError('Require 0 < bound <= radius <= 1/2 and m > 0')
    mroot = r.sqrt_down(m, bits=256)
    if mroot <= 0:
        raise ValueError('Positive rational square-root lower bound unavailable')
    scale = r.sqrt_up(F(rows*columns))/mroot
    c = (3+radius)/4
    for bits in range(1, max_bits+1):
        nu = scale / (1 << (bits+1))
        noise = 2*nu+nu*nu
        if noise <= (1-c)*bound*bound:
            return dict(bits=bits, relative_step_error=nu, noise=noise,
                        c=c, next_bound=bound*bound)
    raise ArithmeticError('Precision budget exhausted; no certificate returned')


class FixedTarget:
    """A copied, fixed target with a lazy checked inverse, owned by one fit."""
    def __init__(self, target, *, m):
        M = r.matrix(target)
        self.m = r.rational(m)
        if self.m <= 0 or len(M) != len(M[0]):
            raise ValueError('Positive target floor and square target required')
        r.psd(r.add(M, r.eye(len(M), self.m), -1))
        self._target = tuple(tuple(row) for row in M)
        self._inverse = None
        self.inverse_builds = 0
        self.solve_applications = 0

    @property
    def target(self):
        return [list(row) for row in self._target]

    def apply(self, factor):
        W = r.matrix(factor)
        d = len(self._target)
        if len(W) < d or len(W[0]) != d:
            raise ValueError('Require p-by-d factor, p >= d')
        if self._inverse is None:
            inv = r.inverse(self.target)
            self._inverse = tuple(tuple(row) for row in inv)
            self.inverse_builds += 1
        H = r.mm(r.tr(W), W)
        X = r.mm([list(row) for row in self._inverse], H)
        if r.mm(self.target, X) != H:
            raise ArithmeticError('Cached target solve failed its residual check')
        self.solve_applications += 1
        return r.scale(r.mm(W, r.add(r.eye(d, 3), X, -1)), F(1, 2))


def refresh(factor, target, *, m, tolerance, radius=F(1, 2),
            max_bits=128, max_updates=32):
    """Return a factor and full trace only after a relative Gram certificate.

    Initial target gating and all per-update Loewner checks are performed.
    This certifies a critic, not by itself the surrounding economic policy.
    """
    _integer(max_updates, 'max_updates', 0, 64)
    _integer(max_bits, 'max_bits', 1, 4096)
    tolerance = r.rational(tolerance)
    if tolerance <= 0:
        raise ValueError('Positive tolerance required')
    cache = FixedTarget(target, m=m)
    W = r.matrix(factor)
    initial = qr.relative_gate(W, cache.target, m=m, radius=radius)
    bound = initial
    trace = []
    while bound > tolerance:
        if len(trace) >= max_updates:
            raise ArithmeticError('Update budget exhausted; no certificate returned')
        p = precision(bound, m=m, rows=len(W), columns=len(W[0]),
                      radius=radius, max_bits=max_bits)
        U = cache.apply(W)
        grid = 1 << p['bits']
        new = [[F(round(x*grid), grid) for x in row] for row in U]
        absolute = r.sqrt_up(F(len(W)*len(W[0])))/(2*grid)
        if r.norm2(r.add(new, U, -1)) > absolute*absolute:
            raise ArithmeticError('Whole-step rounding enclosure failed')
        next_bound = p['next_bound']
        gram = r.mm(r.tr(new), new)
        r.psd(r.add(gram, r.scale(cache.target, 1-next_bound), -1))
        r.psd(r.add(r.scale(cache.target, 1+next_bound), gram, -1))
        trace.append(dict(update=len(trace)+1, starting_bound=bound,
            bits=p['bits'], relative_step_error=p['relative_step_error'],
            bound=next_bound, inverse_builds=cache.inverse_builds,
            rounding_error_squared=r.norm2(r.add(new, U, -1))))
        bound, W = next_bound, new
    return dict(factor=W, relative_error_bound=bound, initial_bound=initial,
        trace=trace, updates=len(trace), inverse_builds=cache.inverse_builds,
        solve_applications=cache.solve_applications,
        stored_factor_bits_sum=sum(x['bits'] for x in trace),
        stored_factor_bits_max=max((x['bits'] for x in trace), default=0))
