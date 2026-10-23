"""Prespecified exact simultaneous inference for the R120 original-policy study.

The 64 initial states, not shock nodes, methods or timing repetitions, are the
independent units. Binomial inversion and the Hoeffding radius are evaluated
with exact integers/rationals. These classical methods are not novelty claims.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from functools import lru_cache
import json
import math
from pathlib import Path
import time
import traceback

from custody120 import verify_source
from io120 import append_jsonl, digest, exclusive_attempt, write_json

N = 64
ARMS = ("online", "quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid")
SERVICES = ("legacy-safe", "paired", "direct-refine")
THRESHOLDS = (F(1, 2**20), F(1, 2**18), F(1, 2**16), F(1, 2**14))
TAU = F(1, 256)
RADIUS = 33 * TAU / 128
EVENT_DELTA = F(1, 7680)
MEAN_TWO_SIDED_DELTA = F(1, 1920)


def encoded(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encoded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encoded(v) for v in value]
    return value


def read_rows(path):
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def binomial_tail_at_most(p, k, delta):
    """Exact comparison of P_p[Binomial(64,p)>=k] to a rational delta."""
    c, d = p.numerator, p.denominator
    numerator = sum(math.comb(N, j) * c**j * (d - c)**(N - j) for j in range(k, N + 1))
    denominator = d**N
    return numerator * delta.denominator <= delta.numerator * denominator


@lru_cache(maxsize=None)
def cp_lower(k):
    if not 0 <= k <= N:
        raise ValueError("The event count must use all 64 independent state rows")
    if k == 0:
        return dict(successes=0, lower=F(0), inversion_upper=F(0), exact_bisections=0)
    lo, hi = F(0), F(1)
    for _ in range(48):
        mid = (lo + hi) / 2
        if binomial_tail_at_most(mid, k, EVENT_DELTA):
            lo = mid
        else:
            hi = mid
    assert binomial_tail_at_most(lo, k, EVENT_DELTA)
    assert not binomial_tail_at_most(hi, k, EVENT_DELTA)
    return dict(successes=k, lower=lo, inversion_upper=hi, exact_bisections=48,
                lower_endpoint_has_tail_at_most_delta=True,
                upper_endpoint_has_tail_above_delta=True)


def radius_certificate():
    exponent = 2 * N * (RADIUS / TAU)**2
    assert exponent == F(1089, 128)
    taylor = sum(exponent**j / math.factorial(j) for j in range(21))
    assert taylor > 3840
    assert 48 * 4 * EVENT_DELTA == F(1, 40)
    assert 48 * MEAN_TWO_SIDED_DELTA == F(1, 40)
    return dict(n=N, gain_support=[F(0), TAU], exact_radius=RADIUS,
                exact_hoeffding_exponent=exponent, exponential_lower_taylor_degree=20,
                exact_exponential_lower_bound=taylor, strict_lower_bound_exceeds=3840,
                two_sided_tail_strictly_below=MEAN_TWO_SIDED_DELTA,
                family_failure_probability_at_most=F(1, 20))


def analyse(primary, independent, out):
    assert len(primary) == N * 2 * 8 * 4
    identities = [(r["index"], r["row"], r["arm"], r["service"]) for r in primary]
    assert len(set(identities)) == len(identities)
    assert set(identities) == {(i, j, arm, service) for i in range(2) for j in range(N)
                               for arm in ARMS for service in ("completed",) + SERVICES}
    audit = {(r["index"], r["row"], r["arm"], r["service"]): r for r in independent}
    assert len(audit) == len(independent)
    assert set(audit) <= set(identities)
    certificate = radius_certificate()
    summaries = []
    for risk in range(2):
        for arm in ARMS:
            for service in SERVICES:
                group = [r for r in primary if (r["index"], r["arm"], r["service"]) == (risk, arm, service)]
                group.sort(key=lambda r: r["row"])
                assert [r["row"] for r in group] == list(range(N))
                assert all(r["original_initial_state_batch_size"] == 1 for r in group)
                intervals = []
                missing = []
                for row in group:
                    identity = (risk, row["row"], arm, service)
                    if identity not in audit:
                        # A missing independent calculation is not dropped. The
                        # fixed original-policy safety theorem supplies [0,tau].
                        intervals.append((F(0), TAU))
                        missing.append(row["row"])
                    else:
                        bounds = (F(audit[identity]["gain_lower"]), F(audit[identity]["gain_upper"]))
                        assert F(0) <= bounds[0] <= bounds[1] <= TAU
                        intervals.append(bounds)
                events = []
                staircase = F(0)
                previous = F(0)
                for threshold in THRESHOLDS:
                    k = sum(lo >= threshold for lo, _ in intervals)
                    inversion = cp_lower(k)
                    events.append(dict(threshold=threshold, **inversion))
                    staircase += (threshold - previous) * inversion["lower"]
                    previous = threshold
                empirical_lower = sum(lo for lo, _ in intervals) / N
                empirical_upper = sum(hi for _, hi in intervals) / N
                mean_lower = max(F(0), empirical_lower - RADIUS)
                mean_upper = min(TAU, empirical_upper + RADIUS)
                assert 0 <= staircase <= mean_upper <= TAU
                result = dict(index=risk, alpha=F(1, 2) if risk == 0 else F(3, 4), arm=arm,
                    service=service, independent_units=N, positive_threshold_events=events,
                    sample_mean_gain_lower=empirical_lower, sample_mean_gain_upper=empirical_upper,
                    hoeffding_population_mean_lower=mean_lower,
                    hoeffding_population_mean_upper=mean_upper,
                    population_mean_staircase_lower=staircase,
                    simultaneous_population_mean_lower=max(mean_lower, staircase),
                    simultaneous_population_mean_upper=mean_upper,
                    missing_independent_rows=missing,
                    missing_rows_use_full_safe_support_and_are_not_excluded=True,
                    accepted_steps=sum(r["accepted_steps"] for r in group),
                    changed_state_actions=sum(r["action"] != r["completed_incumbent_action"] for r in group),
                    total_singleton_seconds=sum(r["seconds"] for r in group),
                    actual_costs_are_descriptive_not_a_population_runtime_interval=True)
                summaries.append(result)
                append_jsonl(out / "POPULATION_GROUPS120.jsonl", encoded(result))
    assert len(summaries) == 48
    return dict(status="executed", groups=48, threshold_events=192, independent_units=N,
                global_simultaneous_coverage_at_least=F(19, 20),
                per_threshold_failure=EVENT_DELTA, per_mean_two_sided_failure=MEAN_TWO_SIDED_DELTA,
                radius_certificate=certificate, thresholds=THRESHOLDS,
                population="IID finite-uniform 40-bit two-coordinate initial states, conditional on the declared ideal independent OS entropy law and frozen actors",
                innovation_distribution="original continuous uniform risk law is unchanged",
                services_are_row_local_and_fixed_before_sampling=True,
                independence_between_methods_risks_or_thresholds_not_assumed=True,
                sampling_no_action_or_method_selection_by_outcome=True,
                unseen_timing_rows_do_not_add_population_observations=True,
                complete_independent_validation=len(audit) == len(primary),
                positive_staircase_groups=sum(r["population_mean_staircase_lower"] > 0 for r in summaries),
                neural_adoption_or_cross_representation_advantage_not_implied=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--primary", required=True, type=Path)
    parser.add_argument("--independent", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = verify_source(args.source_commit)
    out, initial = exclusive_attempt(args.output, "stats120", source)
    started = time.perf_counter()
    inputs = dict(primary=dict(path=str(args.primary), sha256=digest(args.primary)),
                  independent=dict(path=str(args.independent), sha256=digest(args.independent)))
    write_json(out / "INPUTS120.json", inputs)
    try:
        result = analyse(read_rows(args.primary), read_rows(args.independent), out)
        assert digest(args.primary) == inputs["primary"]["sha256"]
        assert digest(args.independent) == inputs["independent"]["sha256"]
        result.update(source=source, exit_code=0, total_seconds=time.perf_counter() - started,
                      started_unix=initial["started_unix"], ended_unix=time.time(), inputs=inputs)
        write_json(out / "EXECUTION120.json", encoded(result))
        print(json.dumps(encoded({k: result[k] for k in ("status", "groups", "threshold_events", "positive_staircase_groups", "total_seconds")})), flush=True)
    except BaseException:
        append_jsonl(out / "FAILED120.jsonl", dict(status="failed", source=source,
                     ended_unix=time.time(), total_seconds=time.perf_counter() - started,
                     exception=traceback.format_exc(), all_partial_evidence_retained=True))
        raise


if __name__ == "__main__":
    main()
