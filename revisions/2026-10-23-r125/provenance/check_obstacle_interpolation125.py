#!/usr/bin/env python3
"""Independent exact-arithmetic diagnostic of the R125 interpolation construction.

This imports no manuscript solver, uses no economic states or actors, and creates
no scientific population observation. It stress-checks an analytic identity with
deterministic rational data, including zero and saturated curvature increments.
The mathematical proof, not this finite diagnostic, establishes general validity.
"""
from fractions import Fraction as F
import datetime
import hashlib
import json
from pathlib import Path


def phi(v, K, lo, hi):
    assert K > 0 and lo <= 0 <= hi
    t = min(hi, max(lo, v / K))
    return v * t - K * t * t / 2


def interval_value(t, d, s, w, K, f, g):
    D = d - s / K
    if D == 0:
        assert s == K * d and w == K * d * d / 2
        return f + g * t + K * t * t / 2
    c = (w - s * s / (2 * K)) / D
    assert 0 <= c <= s
    first = K * t * t / 2 if t <= c / K else c * t - c * c / (2 * K)
    onset = d - (s - c) / K
    last = K * max(F(0), t - onset) ** 2 / 2
    return f + g * t + first + last


def interval_derivative(t, d, s, w, K, g):
    D = d - s / K
    if D == 0:
        return g + K * t
    c = (w - s * s / (2 * K)) / D
    return g + min(K * t, c) + max(F(0), s - c - K * (d - t))


def exact_min_gap(xs, fs, gs, K, slope):
    candidates = []
    for i, (x, y) in enumerate(zip(xs, xs[1:])):
        d, s = y - x, gs[i + 1] - gs[i]
        w = fs[i + 1] - fs[i] - gs[i] * d
        D = d - s / K
        breaks = [F(0), d]
        if D:
            c = (w - s * s / (2 * K)) / D
            breaks.extend([c / K, d - (s - c) / K])
        breaks = sorted(set(breaks))
        for left, right in zip(breaks, breaks[1:]):
            dl = interval_derivative(left, d, s, w, K, gs[i])
            dr = interval_derivative(right, d, s, w, K, gs[i])
            local = [left, right]
            if dr > dl and dl <= slope <= dr:
                local.append(left + (slope - dl) * (right - left) / (dr - dl))
            for t in local:
                candidates.append(interval_value(t, d, s, w, K, fs[i], gs[i]) - slope * (x + t))
    return min(candidates)


def main():
    state = 125

    def draw(n):
        nonlocal state
        state = (1103515245 * state + 12345) % (2 ** 31)
        return state % n

    cases = 240
    tested = 0
    degenerate = {"zero_increment": 0, "saturated_increment": 0, "lower_value_endpoint": 0, "upper_value_endpoint": 0}
    records = []
    for case in range(cases):
        K = F(1 + draw(7), 1 + draw(4))
        xs = [F(0), F(1, 5), F(3, 5), F(1)]
        fs, gs = [F(draw(13) - 6, 7)], [F(draw(19) - 9, 5)]
        for x, y in zip(xs, xs[1:]):
            d = y - x
            s = K * d * F(draw(9), 8)
            low = s * s / (2 * K)
            high = s * d - low
            w = low + (high - low) * F(draw(9), 8)
            degenerate["zero_increment"] += int(s == 0)
            degenerate["saturated_increment"] += int(s == K * d)
            degenerate["lower_value_endpoint"] += int(w == low)
            degenerate["upper_value_endpoint"] += int(w == high)
            f, g = fs[-1], gs[-1]
            assert interval_value(F(0), d, s, w, K, f, g) == f
            assert interval_value(d, d, s, w, K, f, g) == f + g * d + w
            assert interval_derivative(F(0), d, s, w, K, g) == g
            assert interval_derivative(d, d, s, w, K, g) == g + s
            fs.append(f + g * d + w)
            gs.append(g + s)
        for k in range(17):
            slope = gs[0] - K + F(k, 16) * (gs[-1] - gs[0] + 2 * K)
            node_intercept = min(f - slope * x - phi(slope - g, K, -x, F(1) - x) for x, f, g in zip(xs, fs, gs))
            actual_intercept = exact_min_gap(xs, fs, gs, K, slope)
            assert node_intercept == actual_intercept, (case, slope, node_intercept, actual_intercept)
            # Both a valid support and an explicitly invalid higher intercept.
            assert actual_intercept - (node_intercept - F(1, 97)) > 0
            assert actual_intercept - (node_intercept + F(1, 97)) < 0
            tested += 1
        records.append({"case": case, "K": str(K), "x": list(map(str, xs)), "f": list(map(str, fs)), "g": list(map(str, gs))})
    # K=0 is a separate affine problem: endpoint checks are sufficient.
    for g in (F(-2), F(0), F(3)):
        for slope in (F(-5), F(0), F(2), F(7)):
            intercept = min(F(2), F(2) + g - slope)
            for t in (F(0), F(1, 7), F(1, 2), F(6, 7), F(1)):
                assert F(2) + g * t >= intercept + slope * t
    source = Path(__file__).resolve()
    result = {"schema": 1, "executed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "status": "passed", "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "scope": "Independent deterministic rational interpolation diagnostic, not an economic experiment, population result, external referee review or proof-assistant verification.", "cases": cases, "affine_support_cases": tested, "degenerate_interval_counts": degenerate, "K_zero_affine_pairs": 12, "identity": "maximal admissible line intercept from all node Phi constraints equals exact minimum of constructed h(x)-slope*x", "arithmetic": "Python standard-library Fraction; exact equality", "case_data_sha256": hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()}
    destination = source.with_name("OBSTACLE_INTERPOLATION_DIAGNOSTIC125.json")
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
