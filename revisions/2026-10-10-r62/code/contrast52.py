"""Exact finite-state reference for the R52 action-contrast theorem.

The certificate uses policy Bellman residuals, not the unknown true policy
value. Fractions keep the regression implementation independent of floating
point. This module is not an investment-economy discretization.
"""
from __future__ import annotations
from fractions import Fraction as F
from typing import Sequence
import tests51 as base


def coupling(p: Sequence[F], q: Sequence[F]) -> list[tuple[int, int, F]]:
    """Common-uniform (ordered quantile) coupling with exact marginals."""
    if not p or not q or any(x < 0 for x in [*p, *q]):
        raise ValueError('Nonempty nonnegative probability vectors required')
    if sum(p, F(0)) != 1 or sum(q, F(0)) != 1:
        raise ValueError('Probability vectors must sum exactly to one')
    left, right = list(p), list(q)
    out = []; i = j = 0
    while i < len(left) and j < len(right):
        mass = min(left[i], right[j])
        if mass:
            out.append((i, j, mass))
            left[i] -= mass; right[j] -= mass
        if left[i] == 0: i += 1
        if right[j] == 0: j += 1
    if any(left) or any(right):
        raise ArithmeticError('Coupling marginal mismatch')
    return out


def transport(D, p, q):
    if len(D) != len(p) or any(len(row) != len(q) for row in D):
        raise ValueError('Pair-bound matrix has incompatible shape')
    if any(v < 0 for row in D for v in row):
        raise ValueError('Pair bounds must be nonnegative')
    return sum((m * D[i][j] for i, j, m in coupling(p, q)), F(0))


def certificate(model, g, pi, h):
    """Backward coupled-residual bound, capped by signed scalar widths."""
    costs, P, beta = model; T = len(pi); S = len(g)
    if len(h) != T + 1 or any(len(row) != S for row in h):
        raise ValueError('One continuation vector is required at every date')
    a, b = base.residual_bands(model, g, pi, h)
    widths = [hi - lo for lo, hi in zip(a, b)]
    D = [None] * (T + 1)
    residual = [None] * (T + 1)
    residual[T] = [g[x] - h[T][x] for x in range(S)]
    D[T] = [[min(widths[T], abs(residual[T][x] - residual[T][y]))
             for y in range(S)] for x in range(S)]
    for t in reversed(range(T)):
        residual[t] = [base.q(model, t, x, pi[t][x], h[t+1]) - h[t][x]
                       for x in range(S)]
        D[t] = [[min(widths[t], abs(residual[t][x] - residual[t][y]) +
                     beta[t] * transport(D[t+1], P[t][x][pi[t][x]],
                                          P[t][y][pi[t][y]]))
                 for y in range(S)] for x in range(S)]
    bounds = []; chi = []
    for t in range(T):
        stage = []
        for x in range(S):
            A = len(costs[t][x])
            stage.append([[min(widths[t+1], transport(D[t+1], P[t][x][v], P[t][x][u]))
                           for u in range(A)] for v in range(A)])
        bounds.append(stage)
        chi.append(max(z for cell in stage for row in cell for z in row))
    return {'lower': a, 'upper': b, 'widths': widths, 'pair_bounds': D,
            'action_bounds': bounds, 'chi': chi, 'residuals': residual}


def improve(model, g, pi, h, zeta=F(0)):
    if zeta < 0:
        raise ValueError('Upper-enclosure slack must be nonnegative')
    cert = certificate(model, g, pi, h)
    costs, _, beta = model; T = len(pi)
    new = []; accepted = rejected = changed = 0
    for t in range(T):
        row = []
        for x in range(len(g)):
            v = min(range(len(costs[t][x])),
                    key=lambda u: (base.q(model, t, x, u, h[t+1]), u))
            d = base.q(model, t, x, v, h[t+1]) - base.q(model, t, x, pi[t][x], h[t+1])
            safe = d + zeta + beta[t] * cert['action_bounds'][t][x][v][pi[t][x]] <= 0
            u = v if safe else pi[t][x]
            row.append(u); accepted += int(safe); rejected += int(not safe)
            changed += int(u != pi[t][x])
        new.append(row)
    return new, [zeta + 2 * beta[t] * cert['chi'][t] for t in range(T)], cert, {
        'accepted': accepted, 'rejected': rejected, 'strict_changes': changed}


def exogenous_instance(T=4):
    """Four-state controlled example; ordering groups the exogenous states."""
    states = [(z, u) for z in (0, 1) for u in (0, 1)]
    costs = []; P = []
    for t in range(T):
        ct = []; pt = []
        for z, u in states:
            ct.append([F((u-z)**2, 2) + F(a*a, 8) + F((a-u)**2, 7)
                       + F(t*a, 40) for a in (0, 1)])
            actions = []
            for a in (0, 1):
                pz = F(1 + 2*z, 4)
                pu = F(1 + u + 3*a, 6)
                actions.append([(pz if zn else 1-pz) * (pu if un else 1-pu)
                                for zn, un in states])
            pt.append(actions)
        costs.append(ct); P.append(pt)
    g = [F((u-z)**2, 1) + F(u, 5) for z, u in states]
    pi = [[1] * len(states) for _ in range(T)]
    return (costs, P, [F(4, 5)] * T), g, pi, states
