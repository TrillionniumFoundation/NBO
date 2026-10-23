"""Prospective exact joint inference on the 64 new R121 state units."""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from functools import lru_cache
import json
import math
from pathlib import Path
import time
import traceback

from custody121 import verify_source
from io121 import append_jsonl, digest, exclusive_attempt, write_json

N = 64
ARMS = ('quadratic', 'relu', 'hinge', 'spline', 'poly2', 'poly3', 'grid')
BUDGETS = (5, 9)
LOSSES = ('value', 'marginal')
TAU = F(1, 256)
K = F(21097, 4096)
R_REGRET, R_GAIN, R_OPTIMUM = 35*TAU/128, 35*TAU/64, 7*K/32
D_OPTIMUM, D_REGRET, D_GAIN = F(1, 200), F(1, 5800), F(1, 2800)
D_THRESHOLD, D_REJECTION = F(1, 11200), F(1, 11600)
THRESHOLDS = (F(1, 2**20), F(1, 2**16))


def exact(x):
    if isinstance(x, dict) and set(x) >= {'numerator', 'denominator'}:
        return F(x['numerator'], x['denominator'])
    return F(x)


def encoded(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encoded(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encoded(v) for v in x]
    return x


def require(c, m):
    if not c:
        raise ArithmeticError(m)


def read_rows(path):
    with Path(path).open(encoding='utf-8') as stream:
        return [json.loads(s) for s in stream if s.strip()]


def identity(r):
    return (r['index'], r['row'], r['budget'], r['arm'], r['loss'])


def groups():
    return [(i, b, a, l) for i in range(2) for b in BUDGETS for a in ARMS for l in LOSSES]+[(i, 0, 'online', 'online') for i in range(2)]


def binomial_at_most(p, k, delta):
    c, d = p.numerator, p.denominator
    total = sum(math.comb(N, j)*c**j*(d-c)**(N-j) for j in range(k, N+1))
    return total*delta.denominator <= delta.numerator*d**N


@lru_cache(maxsize=None)
def cp_lower(k, delta):
    require(0 <= k <= N, 'Complete fixed binomial sample size')
    if k == 0:
        return dict(successes=0, lower=F(0), inversion_upper=F(0), bisections=0)
    lo, hi = F(0), F(1)
    for _ in range(48):
        mid = (lo+hi)/2
        if binomial_at_most(mid, k, delta):
            lo = mid
        else:
            hi = mid
    require(binomial_at_most(lo, k, delta), 'Exact lower binomial bracket')
    require(not binomial_at_most(hi, k, delta), 'Exact upper binomial bracket')
    return dict(successes=k, lower=lo, inversion_upper=hi, bisections=48)


def radius_certificate():
    exponent = 2*N*(R_REGRET/TAU)**2
    require(exponent == 2*N*(R_GAIN/(2*TAU))**2 == F(1225, 128), 'Signed support and exact contrast exponent')
    exp_lower = sum(exponent**j/math.factorial(j) for j in range(21))
    require(exp_lower > 11600, 'Exact contrast exponential bound')
    ref_exponent = 2*N*(R_OPTIMUM/K)**2
    ref_lower = sum(ref_exponent**j/math.factorial(j) for j in range(21))
    require(ref_exponent == F(49, 8) and ref_lower > 400, 'Exact optimum exponential bound')
    total = 2*D_OPTIMUM+58*D_REGRET+28*D_GAIN+112*D_THRESHOLD+116*D_REJECTION
    require(total == F(1, 20), 'Prospective joint multiplicity allocation')
    require(F(49, 32)+F(5, 64)+F(15, 16)*F(37, 16) == F(967, 256), 'Original last-date primitive range')
    require(F(49, 32)+F(5, 64)+F(15, 16)*F(967, 256) == K, 'Original root primitive range')
    return dict(independent_units=N, regret_radius=R_REGRET, signed_gain_radius=R_GAIN,
                optimum_radius=R_OPTIMUM, original_optimum_range=[F(0), K],
                regret_range=[F(0), TAU], signed_gain_range=[-TAU, TAU],
                contrast_exponent=exponent, contrast_exponential_lower=exp_lower,
                optimum_exponent=ref_exponent, optimum_exponential_lower=ref_lower,
                taylor_degree=20, total_failure_at_most=total)


def mean_bounds(pairs, support, radius):
    require(len(pairs) == N, 'All 64 independent state units')
    low, high = support
    for a, b in pairs:
        require(low <= a <= b <= high, 'Declared bounded observation interval')
    ml, mh = sum(a for a, _ in pairs)/N, sum(b for _, b in pairs)/N
    return dict(sample_mean_lower=ml, sample_mean_upper=mh,
                population_mean_lower=max(low, ml-radius), population_mean_upper=min(high, mh+radius))


def analyse(primary, independent, out):
    expect = {(i, j, b, a, l) for i, b, a, l in groups() for j in range(N)}
    p = {identity(r): r for r in primary}; audit = {identity(r): r for r in independent}
    require(len(p) == len(primary) == len(audit) == len(independent) == 3712, 'Full primary and independent censuses')
    require(set(p) == set(audit) == expect, 'All 58 complete policy cells')
    for r in primary:
        require(r['population_observation'] is True and r['repeat'] is None and r['original_initial_state_batch_size'] == 1,
                'Fixed row-local primary services only')
        require(r['qualified'] is True, 'Original-policy qualification')
    certificate = radius_certificate(); optima = {}
    for i in range(2):
        pairs = []
        for j in range(N):
            row = audit[(i, j, 0, 'online', 'online')]
            pair = (exact(row['original_optimum_lower']), exact(row['original_optimum_upper']))
            pairs.append((max(F(0), pair[0]), min(K, pair[1])))
        result = dict(index=i, independent_units=N, **mean_bounds(pairs, (F(0), K), R_OPTIMUM))
        append_jsonl(out/'ORIGINAL_OPTIMUM121.jsonl', encoded(result)); optima[i] = result
    summaries = []; contrasts = []
    for i, b, arm, loss in groups():
        ids = [(i, j, b, arm, loss) for j in range(N)]
        rows = [p[k] for k in ids]; values = [audit[k] for k in ids]
        regret = [(max(F(0), exact(r['original_regret_lower'])), min(TAU, exact(r['original_regret_upper']))) for r in values]
        estimate = mean_bounds(regret, (F(0), TAU), R_REGRET)
        rejected = sum(bool(r['first_rejected']) for r in rows)
        cl, cu = cp_lower(rejected, D_REJECTION), cp_lower(N-rejected, D_REJECTION)
        raw_missing=sum(r['proposal_regret_lower'] is None for r in values)
        result = dict(index=i, budget=b, arm=arm, loss=loss, independent_units=N,
            regret=estimate,
            sample_original_objective_lower=sum(exact(r['j_lower']) for r in values)/N,
            sample_original_objective_upper=sum(exact(r['j_upper']) for r in values)/N,
            population_original_objective_lower=max(F(0), optima[i]['population_mean_lower']+estimate['population_mean_lower']),
            population_original_objective_upper=min(K+TAU, optima[i]['population_mean_upper']+estimate['population_mean_upper']),
            sample_raw_proposal_regret_lower=None if raw_missing else sum(exact(r['proposal_regret_lower']) for r in values)/N,
            sample_raw_proposal_regret_upper=None if raw_missing else sum(exact(r['proposal_regret_upper']) for r in values)/N,
            sample_action_squared_error_upper=sum(exact(r['squared_original_action_error_upper']) for r in values)/N,
            sample_raw_proposal_action_squared_error_upper=None if raw_missing else sum(exact(r['proposal_squared_original_action_error_upper']) for r in values)/N,
            first_rejections=rejected, rejection_probability_lower=cl['lower'], rejection_probability_upper=1-cu['lower'],
            rejection_lower_inversion=cl, rejection_complement_lower_inversion=cu,
            changed_first_proposals=sum(r['proposal_equals_final'] is False for r in values),
            unavailable_raw_proposals=raw_missing,
            total_singleton_seconds=sum(F(r['seconds']) for r in rows),
            exact_fallback_rows=sum(bool(r['exact_fallback']) for r in rows),
            all_primary_qualified=True, no_missing_independent_rows=True,
            objective_population_bounds_use_joint_optimum_and_regret_intervals=True,
            action_error_is_upper_bound_not_exact_error=True)
        append_jsonl(out/'POLICY_GROUPS121.jsonl', encoded(result)); summaries.append(result)
        if loss == 'marginal':
            pairs = [(exact(r['marginal_gain_lower']), exact(r['marginal_gain_upper'])) for r in values]
            gain = mean_bounds(pairs, (-TAU, TAU), R_GAIN); events = []
            for threshold in THRESHOLDS:
                for sign in ('benefit', 'harm'):
                    k = sum(lo >= threshold for lo, _ in pairs) if sign == 'benefit' else sum(hi <= -threshold for _, hi in pairs)
                    event = dict(threshold=threshold, direction=sign, **cp_lower(k, D_THRESHOLD))
                    events.append(event)
            value_rows = [p[(i, j, b, arm, 'value')] for j in range(N)]
            contrast = dict(index=i, budget=b, arm=arm, independent_units=N, gain=gain, threshold_events=events,
                identical_original_policy_keys=sum(r['key_id'] == r['value_incumbent_key_id'] for r in values),
                first_rejection_change=rejected-sum(bool(r['first_rejected']) for r in value_rows),
                signed_service_seconds_change=sum(F(r['seconds']) for r in rows)-sum(F(r['seconds']) for r in value_rows),
                gain_is_not_assumed_nonnegative=True, finite_sample_only_runtime_difference=True)
            append_jsonl(out/'LOSS_CONTRASTS121.jsonl', encoded(contrast)); contrasts.append(contrast)
    require(len(summaries) == 58 and len(contrasts) == 28, 'Complete declared inference groups')
    return dict(status='executed', policy_groups=58, paired_loss_groups=28, threshold_events=112,
                first_rejection_one_sided_endpoints=116, original_optimum_groups=2,
                simultaneous_coverage_at_least=F(19, 20), independent_units=N, radius_certificate=certificate,
                positive_population_gain_lower_groups=sum(r['gain']['population_mean_lower'] > 0 for r in contrasts),
                negative_population_gain_upper_groups=sum(r['gain']['population_mean_upper'] < 0 for r in contrasts),
                complete_independent_validation=True,
                cross_representation_neural_adoption_inference_claimed=False,
                population='New independent 40-bit product-uniform initial states conditional on ideal OS entropy and frozen actors; original continuous innovation law unchanged')


def main():
    p = argparse.ArgumentParser(); p.add_argument('--source-commit', required=True)
    p.add_argument('--primary', type=Path, required=True); p.add_argument('--independent', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    source = verify_source(a.source_commit); out, initial = exclusive_attempt(a.output, 'stats121', source)
    clock = time.perf_counter(); inputs = {name: dict(path=str(path), sha256=digest(path)) for name, path in [('primary', a.primary), ('independent', a.independent)]}
    write_json(out/'INPUTS121.json', inputs)
    try:
        result = analyse(read_rows(a.primary), read_rows(a.independent), out)
        require(digest(a.primary) == inputs['primary']['sha256'] and digest(a.independent) == inputs['independent']['sha256'], 'Immutable inference inputs')
        result.update(source=source, exit_code=0, started_unix=initial['started_unix'], ended_unix=time.time(),
                      total_seconds=time.perf_counter()-clock, inputs=inputs)
        write_json(out/'EXECUTION121.json', encoded(result))
        print(json.dumps(encoded({k: result[k] for k in ['status', 'policy_groups', 'paired_loss_groups', 'positive_population_gain_lower_groups', 'negative_population_gain_upper_groups', 'total_seconds']})), flush=True)
    except BaseException:
        append_jsonl(out/'FAILED121.jsonl', dict(status='failed', source=source, ended_unix=time.time(),
                       elapsed_seconds=time.perf_counter()-clock, exception=traceback.format_exc(), all_partial_evidence_retained=True))
        raise


if __name__ == '__main__':
    main()
