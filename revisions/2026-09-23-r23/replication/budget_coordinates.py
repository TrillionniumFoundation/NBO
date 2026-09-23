"""Gauge-free proposal pricing for the unchanged R20 economy.

This is ordinary floating-point proposal generation, NOT the economic certifier.
The strictly positive quadrature rule gives an analytic finite root bracket.
The implicit derivative is evaluated at the enclosed numerical root; the
independent directed continuous-model checker remains unchanged.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, asdict
from typing import Callable
import numpy as np
import torch
from numpy.polynomial.hermite import hermgauss
from numpy.polynomial.legendre import leggauss

@dataclass
class RootAccounting:
    calls: int = 0
    bisections: int = 0
    max_bisections: int = 0
    max_absolute_discrete_budget_residual: float = 0.0
    minimum_discrete_price_derivative: float = math.inf
    failures: int = 0


def implicit_offset(logits: torch.Tensor, weights: torch.Tensor, target: float,
                    account: RootAccounting | None = None) -> torch.Tensor:
    """Solve sum(weights*sigmoid(logits+a))=target and expose its first derivative.

    weights are positive and broadcastable to logits; target is an absolute
    weighted sigmoid mass. The graph through the bisection is intentionally
    detached. The implicit correction gives the analytic first derivative.
    """
    if account is not None:
        account.calls += 1
    try:
        if not torch.isfinite(logits).all() or not torch.isfinite(weights).all():
            raise FloatingPointError('Nonfinite logits or weights')
        if not bool((weights > 0).all()):
            raise ValueError('Quadrature weights must be strictly positive')
        w = torch.broadcast_to(weights, logits.shape)
        mass = float(w.sum().detach())
        if not math.isfinite(target) or not 0 < target < mass:
            raise ValueError('Budget is outside the strict attainable interval')
        nu = target / mass
        logit_nu = math.log(nu) - math.log1p(-nu)
        with torch.no_grad():
            lo = logit_nu - float(logits.max())
            hi = logit_nu - float(logits.min())
            # Outward binary64 padding of the mathematical bracket. This is a
            # numerical safeguard, not a substitute for directed certification.
            pad = 32 * np.finfo(float).eps * max(1., abs(lo), abs(hi))
            lo -= pad; hi += pad
            def price(a: float) -> float:
                return float((w * torch.sigmoid(logits + a)).sum())
            if price(lo) > target or price(hi) < target:
                raise ArithmeticError('Numerical price does not respect its analytic bracket')
            iterations = 0
            for iterations in range(1, 81):
                mid = lo + (hi - lo) / 2
                if mid == lo or mid == hi:
                    break
                if price(mid) > target:
                    hi = mid
                else:
                    lo = mid
            a0 = lo + (hi - lo) / 2
        sig = torch.sigmoid(logits + a0)
        q = (w * sig).sum()
        derivative = (w * sig * (1 - sig)).sum()
        d = float(derivative.detach())
        if not math.isfinite(d) or d <= np.finfo(float).tiny:
            raise FloatingPointError('Unresolved or saturated budget derivative')
        # da/dlogits=-w*sigma_prime/sum(w*sigma_prime); first-order implicit
        # differentiation, with a roundoff-sized Newton correction in value.
        a = a0 + (target - q) / derivative.detach()
        residual = float(((w * torch.sigmoid(logits + a)).sum() - target).detach())
        if not math.isfinite(residual) or abs(residual) > 5e-13 * max(1., mass):
            raise ArithmeticError('Discrete budget residual exceeds the proposal tolerance')
        if account is not None:
            account.bisections += iterations
            account.max_bisections = max(account.max_bisections, iterations)
            account.max_absolute_discrete_budget_residual = max(
                account.max_absolute_discrete_budget_residual, abs(residual))
            account.minimum_discrete_price_derivative = min(
                account.minimum_discrete_price_derivative, d)
        return a
    except (ValueError, ArithmeticError, FloatingPointError):
        if account is not None:
            account.failures += 1
        raise


def setup(u0: float=2., x0: float=1.25, n: int=16) -> Callable:
    """The original proposal objective, with a root-safe redundant-coordinate map."""
    tg, tw = leggauss(8); z, zw = hermgauss(16)
    z = torch.tensor(z * np.sqrt(2)); zw = torch.tensor(zw / np.sqrt(np.pi))
    t = torch.tensor((np.arange(n)[:, None] + (tg + 1) / 2) / n)
    w = torch.tensor(tw / (2 * n)); edges = torch.arange(n) / n
    tt = t[:, :, None]; root = torch.sqrt(tt)
    lp = -.025 * tt + .3 * root * z
    lq = .065 * tt + .3 * root * z
    disc = torch.exp(-.02 * t) * w
    weights = disc[:, :, None] * zw
    budget = x0 - .50001 * np.exp(-.02)
    mass = float(weights.sum()); target = (budget - .5 * mass) / .3
    account = RootAccounting()
    def objective(net: torch.nn.Module, details: bool=False):
        h = net((2 * (torch.arange(n) + .5) / n - 1).reshape(n, 1))
        b = .3 * h[:, 0, None, None]
        b = b - b.mean()
        s = (.1 + 6.4 * torch.sigmoid(h[:, 1]))[:, None, None]
        theta = .2 * torch.sigmoid(h[:, 2])
        logits = b - s * lq
        offset = implicit_offset(logits, weights, target, account)
        cq = .5 + .3 * torch.sigmoid(logits + offset)
        q = (cq * weights).sum()
        c = .5 + .3 * torch.sigmoid(b - s * lp + offset)
        mean = u0 + (torch.cumsum(theta, 0) - theta)[:, None] / n + theta[:, None] * (t - edges[:, None])
        U = mean[:, :, None, None] + .05 * torch.sqrt(t)[:, :, None, None] * (
            .25 * z[None, None, :, None] + np.sqrt(.9375) * z[None, None, None, :])
        flow = (-torch.exp(-(U - 1) * torch.log(c[:, :, :, None])) / (U - 1)
                * zw[None, None, :, None] * zw[None, None, None, :]).sum((-1, -2)) - theta[:, None] ** 2
        payoff = (torch.exp(-.04 * t) * flow * w).sum() + np.exp(-.04) * (
            -.02 * ((u0 - 2 + theta.mean()) ** 2 + .0025) + .1 * np.log(.50001))
        if not torch.isfinite(payoff):
            raise FloatingPointError('Nonfinite proposal payoff')
        if details:
            return {'b': (b[:, 0, 0] + offset).detach().tolist(),
                    's': s[:, 0, 0].detach().tolist(), 'theta': theta.detach().tolist(),
                    'u0': u0, 'x0': x0, 'approx_value': float(payoff.detach()),
                    'approx_budget': float(q.detach()), 'n': n, 'reserve': .50001}
        return payoff
    objective.accounting = account
    return objective


class QuotientSlab(torch.nn.Module):
    """47 coordinates for the same financed family (one intercept fixed to zero)."""
    def __init__(self, raw: torch.Tensor):
        super().__init__()
        raw = raw.detach().clone()
        self.intercept_contrasts = torch.nn.Parameter(raw[:-1, 0] - raw[-1, 0])
        self.slopes_and_drifts = torch.nn.Parameter(raw[:, 1:].clone())
    def forward(self, _: torch.Tensor) -> torch.Tensor:
        intercepts = torch.cat((self.intercept_contrasts, self.intercept_contrasts.new_zeros(1)))
        return torch.cat((intercepts[:, None], self.slopes_and_drifts), dim=1)
