"""Original-law active-tail certificates; no learned quantity certifies itself.

The floating tail location is a proposal. The outward residual of the SAME
feasible two-tail density certifies its suboptimality. All oracle work is paid.
The original terminal controller, investment primitives and tolerances persist.
"""
from __future__ import annotations
from pathlib import Path
import sys, time, resource
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'frozen108/code108'))
import campaign108 as base
from interval94 import I, up, down
import investment94 as econ
import quadrature96 as uniform
import continuum94 as cont
import kernel108 as kern

R = 1 / 32
MZ = 181 / 64
CUT_STEPS = 6
KEYS = ('lower', 'upper', 'optimum_lower', 'loss', 'width')
TAIL_LADDER = (2, 4, 8, 16, 32, 64)


def constrained_gain(gradient, curvature, anchor, left, right):
    """Outward -min_d (g*d+curvature*d²/2) on the ORIGINAL interval.

The minimum is concave in g, so both enclosed endpoint slopes suffice. The
completed-square distance uses an enlarged feasible interval, never clipping
an uncertain optimizer into a smaller interval.
"""
    gradient, anchor = I(gradient.lo, gradient.hi), I(anchor)
    curvature = I(curvature)
    lo = (I(left) - anchor).lo
    hi = (I(right) - anchor).hi
    mins = []
    for g in (gradient.lo, gradient.hi):
        stationary = -I(g) / curvature
        distance = np.maximum.reduce([np.zeros_like(g),
            (I(lo) - stationary).lo, (stationary - I(hi)).lo])
        value = -I(g).square() / (2 * curvature) + curvature * I(distance).square() / 2
        mins.append(value.lo)
    return np.maximum(0, up(-np.minimum.reduce(mins)))


def propose_cut(x, a, alpha):
    """Fixed-cost float proposal; no sign is treated as certified information."""
    n = len(x); length = alpha / 16
    left = np.full(n, -R); right = np.full(n, R - length)
    def difference(u):
        z = np.stack([u, u + length], axis=-1)
        y = econ.transition(I(x), I(a), I(z)).mid()
        value, _ = kern.compiled_float_value_slope(y, alpha)
        econ.count('r119_tail_proposal_point_values', value.size)
        return value[:, 1] - value[:, 0]
    dl, dr = difference(left), difference(right)
    at_left, at_right = dl >= 0, dr <= 0
    for _ in range(CUT_STEPS):
        middle = (left + right) / 2
        d = difference(middle)
        left = np.where(d < 0, middle, left)
        right = np.where(d >= 0, middle, right)
    # Final bracket midpoint, not the last sampled midpoint. Boundary location
    # and every interior sign remain proposals paid for by tail_state's kappa.
    u = np.where(at_left, -R, np.where(at_right, R - length, (left + right) / 2))
    u = np.clip(np.rint(u * 2**32) / 2**32, -R, R - length)
    return u


def tail_state(x, a, alpha):
    x, a = np.asarray(x, dtype=float), np.asarray(a, dtype=float)
    if alpha not in (.5, .75):
        raise ValueError('Inherited original-economy risk levels only')
    if x.ndim != 2 or a.shape != (len(x),) or len(x) == 0:
        raise ValueError('Nonempty batched state/action arrays required')
    if x.shape[1] < 2 or x.shape[1] % 2 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(a)) or np.any(x < 0) or np.any(x > 1):
        raise ValueError('The original finite even-dimensional unit state cube is required')
    if np.any(a < 0) or np.any(a > econ.capacity(I(x)).lo):
        raise ValueError('The ACTUAL action must satisfy the original capacity')
    u = propose_cut(x, a, alpha); length = alpha / 16
    endpoints = np.stack([u, u + length], axis=-1)
    values = kern.compiled_certificate(econ.transition(I(x), I(a), I(endpoints)), alpha)
    d = I(values['lower'][:, 1], values['upper'][:, 1]) - I(values['lower'][:, 0], values['upper'][:, 0])
    gap = constrained_gain(d, MZ * length, u, -R, R - length)
    kappa = (I(gap) / (2 * R * (1 - alpha))).hi
    econ.count('r119_tail_residual_point_values', 2 * len(x))
    econ.count('r119_tail_density_constructions', len(x))
    return dict(x=x.copy(), action=a.copy(), alpha=alpha, cut=u,
                derivative_lower=d.lo, derivative_upper=d.hi, kappa=kappa)


def subset(state, ids):
    """A cache reuses only a density bound for identical state/action/risk."""
    econ.count('r119_tail_cache_lookups', len(ids))
    return {k: (v[ids] if isinstance(v, np.ndarray) else v) for k, v in state.items()}


def tail_mesh(cut, alpha, m):
    """Exact binary-rational density geometry used by the production certificate."""
    requested = m; m = int(m)
    if m < 1 or m > 4096 or m & (m - 1) or m != requested:
        raise ValueError('Dyadic tail cells between 1 and 4096 required')
    if alpha not in (.5, .75):
        raise ValueError('Inherited original-economy risk levels only')
    u = np.asarray(cut, dtype=float); length = alpha / 16; tail = 2 * R * (1 - alpha)
    if u.ndim != 1 or not np.all(np.isfinite(u)) or np.any(u < -R) or np.any(u > R-length) or not np.all(u*2**32 == np.rint(u*2**32)):
        raise ValueError('Feasible 32-bit dyadic cut required')
    cut2 = u + length
    left_length, right_length = u + R, R - cut2
    fractions = np.arange(m + 1, dtype=float) / m
    le = -R + left_length[:, None] * fractions
    re = cut2[:, None] + right_length[:, None] * fractions
    mids = np.concatenate([(le[:, :-1] + le[:, 1:]) / 2,
                           (re[:, :-1] + re[:, 1:]) / 2], axis=-1)
    edges = np.concatenate([le, re], axis=-1)
    # For these dyadic risk levels, locations and m, each weight is an exact
    # binary rational; the two tail lengths sum EXACTLY to the tail length.
    weights = np.concatenate([np.broadcast_to((left_length / (m * tail))[:, None], (len(u), m)),
                              np.broadcast_to((right_length / (m * tail))[:, None], (len(u), m))], axis=-1)
    return mids, edges, weights


def certificate(x, a, alpha, bins_per_tail=2, state=None):
    x, a = np.asarray(x, dtype=float), np.asarray(a, dtype=float)
    if state is None:
        state = tail_state(x, a, alpha)
    elif not (state['alpha'] == alpha and np.array_equal(state['x'], x)
              and np.array_equal(state['action'], a)):
        raise ValueError('A tail cache cannot cross state/action/objective identities')
    u = state['cut']; m = int(bins_per_tail)
    mids, edges, weights = tail_mesh(u, alpha, bins_per_tail)
    mid = kern.compiled_certificate(econ.transition(I(x), I(a), I(mids)), alpha)
    end = kern.compiled_certificate(econ.transition(I(x), I(a), I(edges)), alpha)
    lv = (I(mid['lower']) * I(weights)).sum()
    endpoint_left = np.concatenate([end['upper'][:, :m], end['upper'][:, m+1:2*m+1]], axis=-1)
    endpoint_right = np.concatenate([end['upper'][:, 1:m+1], end['upper'][:, m+2:2*m+2]], axis=-1)
    uv = (((I(endpoint_left) + I(endpoint_right)) / 2) * I(weights)).sum()
    stage = econ.S(I(x)) + econ.action_cost(I(a))
    witness = stage + econ.BETA * lv
    policy_upper = stage + econ.BETA * (uv + I(state['kappa']) + econ.TERMINAL_TOL)
    b, _ = econ.exposures(x.shape[-1])
    slope = econ.action_grad(I(a)) + econ.BETA * (((mid['slope'] * b).sum()) * I(weights)).sum()
    optimum = econ.quadratic_minimum_lower(I(witness.lo), slope, I(a), econ.capacity(I(x)))
    loss, width = up(policy_upper.hi - optimum), up(policy_upper.hi - witness.lo)
    if np.any(loss < 0) or np.any(width < 0):
        raise ArithmeticError('Contradictory original-law certificate')
    econ.count('r119_midpoint_terminal_rows', mid['lower'].size)
    econ.count('r119_endpoint_terminal_rows', end['upper'].size)
    econ.count('r119_original_action_certificates', len(x))
    # Zero-length tails are deliberately evaluated and paid in this vector
    # implementation. Theory's sharper skipped-tail count is not an observed count.
    return dict(lower=witness.lo, upper=policy_upper.hi, optimum_lower=optimum,
        loss=loss, width=width, bins_per_tail=m, cut=u.copy(), kappa=state['kappa'].copy(),
        derivative_lower=state['derivative_lower'].copy(), derivative_upper=state['derivative_upper'].copy(),
        witness_lower=witness.lo, slope_lower=slope.lo, slope_upper=slope.hi,
        selected_tail_lower=lv.lo, selected_tail_upper=uv.hi,
        maximum_terminal_gap=float(max(np.max(mid['gap']), np.max(end['gap']))))


def _service_core(x, alpha, model, trace):
    """Original actor + active-tail certificate + unchanged complete fallback.

All 2,4,...,64-cell attempts precede the frozen 128-bin full-support fallback.
The full current conventional proposal and every later refinement are charged.
"""
    x = np.asarray(x, dtype=float); before = econ.COUNTS.copy(); started = time.perf_counter()
    attempts = []; trace['attempts'] = attempts
    n = len(x); resolved = np.zeros(n, bool)
    rec = {k: np.empty(n) for k in KEYS}; first = {k: np.empty(n) for k in KEYS}
    used = np.zeros(n, int); rejected = np.zeros(n, bool); exact = np.zeros(n, bool)
    sys.path.insert(0, str(ROOT / 'frozen117/code117'))
    import precision117 as inherited
    with kern.backend(True):
        trace['stage'] = 'original actor proposal'
        t = time.perf_counter(); proposed = base.rep.proposal(x, alpha, model)
        trace['proposed'] = proposed.tolist()
        proposal_seconds = time.perf_counter() - t; actions = proposed.copy()
        trace['stage'] = 'tail location and original residual'
        cache = tail_state(x, proposed, alpha)
        trace['tail_state'] = {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in cache.items()}
        for bins in TAIL_LADDER:
            ids = np.flatnonzero(~resolved)
            if not len(ids):
                break
            trace['stage'] = 'active-tail certificate'
            trace['bins_per_tail'] = bins; trace['unresolved_rows'] = ids.tolist()
            fresh = certificate(x[ids], proposed[ids], alpha, bins, subset(cache, ids))
            ok = uniform.qualifies(fresh)
            if bins == TAIL_LADDER[0]:
                for k in KEYS:
                    first[k][:] = fresh[k]
            for p, j in enumerate(ids):
                fields = {k: float(fresh[k][p]) for k in KEYS +
                    ('cut','kappa','derivative_lower','derivative_upper','witness_lower','slope_lower',
                     'slope_upper','selected_tail_lower','selected_tail_upper')}
                attempts.append(dict(row=int(j),kind='active-tail',bins_per_tail=bins,
                    action=float(proposed[j]),qualified=bool(ok[p]),**fields))
            for k in KEYS:
                rec[k][ids] = fresh[k]
            used[ids] = bins; resolved[ids[ok]] = True
        ids = np.flatnonzero(~resolved)
        if len(ids):
            trace['stage'] = 'full-support fallback'
            trace['unresolved_rows'] = ids.tolist()
            fresh = uniform.certificate(x[ids], proposed[ids], alpha, 128)
            for p,j in enumerate(ids):
                attempts.append(dict(row=int(j),kind='full-support-fallback',bins=128,
                    action=float(proposed[j]),qualified=bool(uniform.qualifies(fresh)[p]),
                    **{k:float(fresh[k][p]) for k in KEYS}))
            trace['stage'] = 'complete inherited repair and refinement'
            aa, tail, rr, uu, ee = inherited.finish(x[ids], alpha, proposed[ids], fresh, attempts, ids)
            actions[ids] = aa; rejected[ids] = rr; used[ids] = uu; exact[ids] = ee
            for k in KEYS:
                rec[k][ids] = tail[k]
            resolved[ids] = True
    if not np.all(resolved) or not np.all(uniform.qualifies(rec)):
        raise ArithmeticError('Every original-economy decision must be qualified')
    rows = [dict(row=j,x0=float(xx[0]),x1=float(xx[1]),proposed=float(proposed[j]),
        action=float(actions[j]),first_rejected=bool(rejected[j]),bins=int(used[j]),
        exact_fallback=bool(exact[j]),action_distance_upper=float(up(np.sqrt(rec['loss'][j]))),
        **{k:float(rec[k][j]) for k in KEYS},**{'first_'+k:float(first[k][j]) for k in KEYS}) for j,xx in enumerate(x)]
    return dict(rows=rows,attempts=attempts,counts=base.counter_delta(before),
        seconds=time.perf_counter()-started,proposal_seconds=proposal_seconds,
        max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        terminal_policy_unchanged=True,cache_scope='same state/action/risk tail density only')


def service(x, alpha, model):
    """Preserve partial scientific attempts if a batch fails before completion."""
    before = econ.COUNTS.copy(); started = time.perf_counter()
    trace = dict(stage='input', state=np.asarray(x).tolist(), alpha=alpha)
    try:
        result = _service_core(x, alpha, model, trace)
        result['seconds'] = time.perf_counter() - started
        return result
    except BaseException as exc:
        trace.update(status='failed', elapsed_seconds=time.perf_counter()-started,
            counts=base.counter_delta(before), exception_type=type(exc).__name__, exception=str(exc))
        exc.evidence119 = trace
        raise
