"""Prospective R123 exact simultaneous inference, with no economic execution.

All constants are fixed before the 32 fresh states.  The event is a proved
gain of at least 2**-24, not an independently selected numerical threshold.
Numerical endpoint uncertainty is intersected with deterministic theorem
bounds before inference.  Rational binomial and Taylor witnesses avoid
depending on floating-point quantiles or a rounded exponential evaluation.
"""
from __future__ import annotations
import math
from fractions import Fraction as F
from functools import lru_cache

N = 32
TAU = F(1, 256)
SAFE_FAMILY = 232
SIGNED_FAMILY = 696
SAFE_RADIUS = 7 * TAU / 16
SIGNED_RADIUS = 7 * TAU / 8
EVENT_THRESHOLD = F(1, 2**24)
EVENT_DELTA = F(1, 23200)
JOINT_FAILURE = F(1, 20)


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def exact(value):
    if isinstance(value, float):
        require(math.isfinite(value), 'Nonfinite saved endpoint')
    return F(value)


def average(values):
    values = list(values)
    require(bool(values), 'Empty arithmetic mean')
    return sum(map(exact, values), F(0)) / len(values)


def binomial_small(p, successes):
    """Is P_p[Binomial(32,p) >= successes] at most EVENT_DELTA?"""
    p = exact(p)
    require(0 <= p <= 1 and 0 <= successes <= N, 'Invalid binomial input')
    c, d = p.numerator, p.denominator
    total = sum(math.comb(N, j) * c**j * (d-c)**(N-j)
                for j in range(successes, N+1))
    return total * EVENT_DELTA.denominator <= EVENT_DELTA.numerator * d**N


@lru_cache(maxsize=None)
def cp(successes):
    require(isinstance(successes, int) and 0 <= successes <= N,
            'Invalid number of event successes')
    if successes == 0:
        return dict(successes=0, lower=F(0), inversion_upper=F(0),
                    delta=EVENT_DELTA, bisections=0)
    low, high = F(0), F(1)
    for _ in range(48):
        mid = (low + high) / 2
        if binomial_small(mid, successes):
            low = mid
        else:
            high = mid
    require(binomial_small(low, successes) and not binomial_small(high, successes),
            'Exact one-sided binomial inversion bracket failed')
    return dict(successes=successes, lower=low, inversion_upper=high,
                delta=EVENT_DELTA, bisections=48)


def radius_witness():
    exponent = 2 * N * (SAFE_RADIUS / TAU)**2
    require(exponent == 2*N*(SIGNED_RADIUS/(2*TAU))**2 == F(49, 4),
            'Changed prospective Hoeffding exponent')
    exp_lower = sum(exponent**j / math.factorial(j) for j in range(31))
    require(exp_lower > 46400, 'Exact exponential Taylor witness failed')
    require(SAFE_FAMILY * (2/exp_lower) < F(1, 100),
            'Safe mean family exceeds its failure allocation')
    require(SIGNED_FAMILY * (2/exp_lower) < F(3, 100),
            'Signed mean family exceeds its failure allocation')
    require(SAFE_FAMILY*EVENT_DELTA == F(1, 100),
            'Event family exceeds its failure allocation')
    return dict(independent_state_units=N, exponent=exponent,
                exponential_lower=exp_lower, taylor_degree=30,
                strict_exponential_lower_threshold=46400,
                safe_radius=SAFE_RADIUS, signed_radius=SIGNED_RADIUS,
                safe_mean_family=SAFE_FAMILY, signed_mean_family=SIGNED_FAMILY,
                event_family=SAFE_FAMILY, event_threshold=EVENT_THRESHOLD,
                event_delta=EVENT_DELTA, binomial_bisections=48,
                mean_safe_failure_at_most=F(1, 100),
                event_failure_at_most=F(1, 100),
                mean_signed_failure_at_most=F(3, 100),
                joint_failure_at_most=JOINT_FAILURE,
                arbitrary_dependence_between_methods_allowed=True,
                clocks_and_precision_levels_are_not_population_observations=True)


def safe_interval(pairs, certified_gains):
    """All 32 same-incumbent gain enclosures, including zero/fallback rows."""
    pairs = [(exact(lo), exact(hi)) for lo, hi in pairs]
    gains = list(map(exact, certified_gains))
    require(len(pairs) == len(gains) == N, 'Fixed complete 32-state family required')
    bounded = []
    for (low, high), gain in zip(pairs, gains):
        require(low <= high and F(0) <= gain <= TAU, 'Invalid gain evidence')
        lo, hi = max(F(0), gain, low), min(TAU, high)
        require(lo <= hi, 'Independent gain and deterministic certificate conflict')
        bounded.append((lo, hi))
    ml = average(x[0] for x in bounded)
    mh = average(x[1] for x in bounded)
    event = dict(cp(sum(g >= EVENT_THRESHOLD for g in gains)))
    event.update(threshold=EVENT_THRESHOLD,
                 mean_gain_lower_from_event=EVENT_THRESHOLD*event['lower'])
    pl = max(F(0), ml-SAFE_RADIUS, event['mean_gain_lower_from_event'])
    pu = min(TAU, mh+SAFE_RADIUS)
    require(pl <= pu, 'Safe population interval is empty')
    return dict(n=N, sample_gain_lower=ml, sample_gain_upper=mh,
                raw_independent_sample_gain_lower=average(x[0] for x in pairs),
                raw_independent_sample_gain_upper=average(x[1] for x in pairs),
                population_gain_lower=pl, population_gain_upper=pu,
                observed_positive_certified_gains=sum(g > 0 for g in gains),
                mean_certified_gain_lower=average(gains),
                threshold_event=event, hoeffding_radius_upper=SAFE_RADIUS,
                simultaneous_family_size=SAFE_FAMILY, delta=F(1, 100),
                support=[F(0), TAU], joint_failure_at_most=JOINT_FAILURE,
                source_proof_and_independent_intersection=True)


def signed_interval(pairs, identical_method=False, same_action_count=0):
    """A signed advantage is comparator J minus candidate J (minimization).

    Saved identical actions authorize a zero *sample* contrast. Only exactly
    the same mathematical method cell authorizes zero population contrast.
    """
    pairs = [(exact(lo), exact(hi)) for lo, hi in pairs]
    require(len(pairs) == N, 'Signed family must use every original state')
    bounded = [(max(-TAU, lo), min(TAU, hi)) for lo, hi in pairs]
    require(all(lo <= hi for lo, hi in bounded), 'Signed enclosures conflict with qualification')
    ml = average(x[0] for x in bounded)
    mh = average(x[1] for x in bounded)
    if identical_method:
        require(same_action_count == N and all(lo == hi == 0 for lo, hi in pairs),
                'Method identity requires exact paired action identity')
        pl = pu = F(0)
    else:
        pl, pu = max(-TAU, ml-SIGNED_RADIUS), min(TAU, mh+SIGNED_RADIUS)
    require(pl <= pu, 'Signed population interval is empty')
    return dict(n=N, sample_gain_lower=ml, sample_gain_upper=mh,
                raw_independent_sample_gain_lower=average(x[0] for x in pairs),
                raw_independent_sample_gain_upper=average(x[1] for x in pairs),
                population_gain_lower=pl, population_gain_upper=pu,
                exact_identical_method=identical_method,
                identical_sample_actions=same_action_count,
                sample_action_identity_does_not_imply_population_identity=True,
                hoeffding_radius_upper=SIGNED_RADIUS,
                simultaneous_family_size=SIGNED_FAMILY, delta=F(3, 100),
                support=[-TAU, TAU], joint_failure_at_most=JOINT_FAILURE)


def self_check():
    """Algebraic/inversion checks only; no states, solvers, or sample outcomes."""
    witness = radius_witness()
    lowers = [cp(k)['lower'] for k in range(N+1)]
    require(lowers == sorted(lowers) and lowers[0] == 0 and lowers[-1] > 0,
            'Monotonic exact binomial lower bounds')
    zero = [(F(0), F(0))]*N
    require(safe_interval(zero, [F(0)]*N)['population_gain_lower'] == 0,
            'Zero gain cannot produce a positive lower bound')
    require(signed_interval(zero, True, N)['population_gain_upper'] == 0,
            'Identical method has exactly zero population contrast')
    require(signed_interval(zero, False, N)['population_gain_upper'] > 0,
            'Identical sampled actions must retain population uncertainty')
    return dict(status='passed', scope='exact statistical algebra, no economic sample',
                binomial_success_counts_checked=N+1, witness=witness)


if __name__ == '__main__':
    import json
    print(json.dumps(self_check(), default=str, sort_keys=True, indent=2))
