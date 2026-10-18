"""Convex-order continuous AVaR enclosures and original-optimum admission.

All production primitive routines retain their R94 meanings. No grid is made
into the economic innovation law. Historical actors are never overwritten.
"""
from __future__ import annotations
import numpy as np
from interval94 import I, up, down
from investment94 import (BETA, TERMINAL_TOL, S, action_cost, action_grad,
                          exposures, transition, terminal_certificate,
                          tail_weights, weighted_sum, quadratic_minimum_lower,
                          capacity, discrete_avar_interval, count)
from continuum94 import actor, shock_mesh

TAU = 1 / 256
WIDTH = 1 / 8192
MARGIN = 1 / 1280
RADIUS = 1 / 4096
SAMPLE_SIZE = 4096


def endpoint_mixture(values):
    """Equal weights for left/right endpoints of every bin (interiors repeat)."""
    a = np.asarray(values)
    if a.shape[-1] < 2:
        raise ValueError('At least one interval is required')
    return np.stack((a[..., :-1], a[..., 1:]), axis=-1).reshape(a.shape[:-1] + (-1,))


def certificate(x, a, alpha, bins=128):
    x, a = I(x).checked(), I(a).checked()
    mids, edges = shock_mesh(bins)
    mid = terminal_certificate(transition(x, a, I(mids)), alpha)
    end = terminal_certificate(transition(x, a, I(edges)), alpha)
    lower_risk = discrete_avar_interval(I(mid['lower']), alpha)
    upper_risk = discrete_avar_interval(I(endpoint_mixture(end['upper'])), alpha)
    base = S(x) + action_cost(a)
    costs = I((base + BETA * lower_risk).lo,
              (base + BETA * (upper_risk + TERMINAL_TOL)).hi).checked()
    q = tail_weights(mid['lower'], alpha)
    b, _ = exposures(x.lo.shape[-1])
    witness = base + BETA * weighted_sum(I(mid['lower']), q)
    slope = action_grad(a) + BETA * weighted_sum((mid['slope'] * b).sum(), q)
    lower_optimum = quadratic_minimum_lower(I(witness.lo), slope, a, capacity(x))
    loss = up(costs.hi - lower_optimum)
    if np.any(loss < 0):
        raise ArithmeticError('Original optimum exceeds a feasible policy upper bound')
    count('r96_midpoint_terminal_rows', mid['lower'].size)
    count('r96_endpoint_terminal_rows', end['upper'].size)
    count('r96_original_action_certificates', a.lo.size)
    return dict(lower=costs.lo, upper=costs.hi, optimum_lower=lower_optimum,
                loss=loss, width=up(costs.hi - costs.lo), bins=bins,
                maximum_terminal_gap=float(max(np.max(mid['gap']), np.max(end['gap']))))


def qualifies(rec):
    return (np.isfinite(rec['loss']) & (rec['loss'] <= TAU) &
            np.isfinite(rec['width']) & (rec['width'] <= WIDTH))


def service(x, alpha, model):
    """A new qualified service, not a relabeling of an unchanged fitted policy.

A rejected fitted proposal is recorded and replaced by a paid conventional
proposal. Remaining cases use an exact finite action/innovation cover. Any
infrastructure error aborts the workload; no failed row is silently removed.
"""
    x = np.asarray(x, dtype=float)
    proposed = actor(x, alpha, model)
    actions = proposed.copy()
    rec = certificate(x, actions, alpha)
    rejected = ~qualifies(rec)
    original_proposal_loss = rec['loss'].copy()
    used = np.full(len(x), 128, dtype=int)
    exact = np.zeros(len(x), dtype=bool)
    if np.any(rejected):
        actions[rejected] = actor(x[rejected], alpha, None)
        count('r96_conventional_fallback_rows', int(rejected.sum()))
        fresh = certificate(x[rejected], actions[rejected], alpha)
        for key in ('lower', 'upper', 'optimum_lower', 'loss', 'width'):
            rec[key][rejected] = fresh[key]
    for bins in (256, 512, 1024, 2048, 4096):
        bad = ~qualifies(rec)
        if not np.any(bad):
            break
        fresh = certificate(x[bad], actions[bad], alpha, bins)
        used[bad] = bins
        for key in ('lower', 'upper', 'optimum_lower', 'loss', 'width'):
            rec[key][bad] = fresh[key]
    for j in np.flatnonzero(~qualifies(rec)):
        from rational96 import exact_service
        a, low, high, opt, n = exact_service(x[j], alpha)
        actions[j], rec['lower'][j], rec['upper'][j], rec['optimum_lower'][j] = a, low, high, opt
        rec['loss'][j], rec['width'][j] = up(high-opt), up(high-low)
        used[j], exact[j] = n, True
    if not np.all(qualifies(rec)):
        raise ArithmeticError('Workload failed closed; retain every attempted row')
    return dict(rec, actions=actions, proposed=proposed, rejected=rejected,
                proposed_loss=original_proposal_loss, exact=exact, used_bins=used)


def paired(left, right):
    if len(left['lower']) != SAMPLE_SIZE or len(right['lower']) != SAMPLE_SIZE:
        raise ValueError('The primary design fixes 4096 independent states per risk level')
    raw = I(left['lower'], left['upper']) - I(right['lower'], right['upper'])
    lo, hi = np.maximum(raw.lo, -TAU), np.minimum(raw.hi, TAU)
    if np.any(lo > hi):
        raise ArithmeticError('Certified support contradicted')
    mean = I(lo, hi).sum() / SAMPLE_SIZE
    low, high = float(down(mean.lo - RADIUS)), float(up(mean.hi + RADIUS))
    return dict(mean_numerical=[float(mean.lo), float(mean.hi)],
                midpoint=float((mean.lo + mean.hi)/2),
                numerical_half_width=float(up((mean.hi-mean.lo)/2)),
                sampling_radius=RADIUS, interval=[low, high], margin=MARGIN,
                equivalent=low > -float(down(MARGIN)) and high < float(down(MARGIN)),
                left_noninferior=high < float(down(MARGIN)), right_noninferior=low > -float(down(MARGIN)),
                left_superior=high < 0, right_superior=low > 0,
                half_width=float(up((high-low)/2)), family_confidence_at_least=.95)
