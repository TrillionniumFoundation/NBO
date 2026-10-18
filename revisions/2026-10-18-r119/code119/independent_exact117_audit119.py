"""Independent R119 audit of a separately attributed frozen R117 diagnostic.

No production module is imported. Exact tail polynomial coefficients and
Faulhaber sums reconstruct every midpoint/secant enclosure, cost, decision,
stopping event, and counted point request. This validates only the declared
120-row supporting Bellman class, not the original investment campaign.
"""
from fractions import Fraction as F
from pathlib import Path
from math import comb
import argparse
import hashlib
import itertools
import json
import platform
import sys
import time

FROZEN_SOURCE_SHA256 = "c6e324a223e3a5ae1c10a029941e6ae3d0737a5a03a2cd07733c9dde1c655e3e"
PROTOCOL_COMMIT = "e65a0180896406610922e48f65bcf7f55ada366f"
SOURCE_FREEZE_COMMIT = "a21e33471047b966dd375d0b9aceab6b9492e4fb"
# All risk-tail coordinates are at least 1/2, so the 1/3 hinge is active
# throughout and the mixed function's 1/2 hinge begins at the tail endpoint.
TAIL_COEFFICIENTS = {
    "linear": {1: F(1)},
    "square": {2: F(1)},
    "quartic": {4: F(1)},
    "hinge": {0: -F(1, 3), 1: F(1)},
    "hinge-square": {0: F(1, 9), 1: -F(2, 3), 2: F(1)},
    "mixed": {0: -F(1, 8), 1: F(1, 4), 2: F(1)},
}


def powers(n, exponent):
    """Sum j**exponent for integer 0 <= j < n, without point evaluation."""
    if n < 0:
        raise ValueError("Negative polynomial-sum limit")
    if exponent == 0:
        return F(n)
    if exponent == 1:
        return F(n * (n - 1), 2)
    if exponent == 2:
        return F(n * (n - 1) * (2 * n - 1), 6)
    if exponent == 3:
        return F(n * n * (n - 1) * (n - 1), 4)
    if exponent == 4:
        return F(n * (n - 1) * (2 * n - 1) * (3 * n * n - 3 * n - 1), 30)
    raise ValueError("Declared inputs have degree at most four")


def closed_enclosure(coefficients, alpha, bins):
    first = alpha * bins
    if first.denominator != 1:
        raise ValueError("Unaligned declared tail")
    first = int(first)
    mid_total, end_total = F(0), F(0)
    for exponent, coefficient in coefficients.items():
        shifted = sum(
            (F(comb(exponent, j), 2 ** (exponent - j))
             * (powers(bins, j) - powers(first, j)) for j in range(exponent + 1)),
            F(0),
        )
        endpoints = (powers(bins, exponent) - powers(first + 1, exponent)
                     + F(first ** exponent + bins ** exponent, 2))
        mid_total += coefficient * shifted / bins ** exponent
        end_total += coefficient * endpoints / bins ** exponent
    denominator = bins * (1 - alpha)
    return mid_total / denominator, end_total / denominator


def audit(input_path, output_path):
    if output_path.exists():
        raise FileExistsError("Never overwrite a prior audit receipt")
    started = time.perf_counter()
    raw = input_path.read_bytes()
    data = json.loads(raw)
    checks = 0

    def require(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            raise ArithmeticError(message)

    require(data["source_sha256"] == FROZEN_SOURCE_SHA256, "Frozen diagnostic source identity")
    require(data["method_rows"] == len(data["rows"]) == 120, "Complete row count")
    require(data["original_investment"] is False and data["population_inference"] is False,
            "Supporting-class evidence boundary")
    expected = set(itertools.product(TAIL_COEFFICIENTS, (F(1, 2), F(3, 4)),
                                    (12, 16, 20, 24, 28), ("risk-width", "decision-gap")))
    seen = set()
    summaries = {name: {"rows": 0, "qualified": 0, "unresolved": 0,
                        "unique_queries": 0, "point_requests": 0}
                 for name in ("risk-width", "decision-gap")}
    trace_count = 0
    for row in data["rows"]:
        key = row["name"], F(row["alpha"]), row["epsilon_exponent"], row["rule"]
        require(key in expected and key not in seen, "Unique fixed context")
        seen.add(key)
        name, alpha, exponent, rule = key
        coefficients = TAIL_COEFFICIENTS[name]
        exact_risk = sum((c * (1 - alpha ** (k + 1)) / (k + 1)
                          for k, c in coefficients.items()), F(0)) / (1 - alpha)
        require(F(row["risk"]) == exact_risk, "Independent polynomial tail integral")
        tolerance = F(1, 2 ** exponent)
        require(F(row["epsilon"]) == tolerance, "Unchanged economic tolerance")
        # Original objective coefficient form: 4a^2 + (beta*risk-4)a + 1.
        linear = F(15, 16) * exact_risk - 4
        optimum_action, optimum_value = -linear / 8, 1 - linear * linear / 16
        require(0 < optimum_action < 1, "Stated interior condition")
        require(F(row["optimal_action"]) == optimum_action, "Original optimum action")
        require(F(row["optimal_cost"]) == optimum_value, "Original optimum cost")
        requests = 0
        trace = row["trace"]
        require(1 <= len(trace) <= 11, "Valid finite stopping trace")
        for index, step in enumerate(trace):
            trace_count += 1
            bins = 2 ** (index + 2)
            require(step["bins"] == bins, "Unchanged full precision ladder")
            lo, hi = closed_enclosure(coefficients, alpha, bins)
            require(F(step["lower"]) == lo and F(step["upper"]) == hi,
                    "Independent closed-form midpoint/secant sums")
            require(lo <= exact_risk <= hi, "Original-risk bracket")
            midpoint_linear = F(15, 32) * (lo + hi) - 4
            unrounded = -midpoint_linear / 8
            integer = (unrounded * 2 ** 30).numerator // (unrounded * 2 ** 30).denominator
            action = min(F(1), max(F(0), F(integer, 2 ** 30)))
            allowance = 4 * (F(15, 256) * (hi - lo) + F(1, 2 ** 30)) ** 2
            accept = (F(15, 16) * (hi - lo) <= tolerance if rule == "risk-width"
                      else allowance <= tolerance)
            require(F(step["action"]) == action, "Feasible downward action realization")
            require(F(step["regret_bound"]) == allowance, "Decision-scale certificate")
            require(step["accepted"] is accept, "Unchanged stopping predicate")
            requests += 2 * bins + 1
            require(step["requests"] == requests and step["unique_queries"] == 2 * bins + 1,
                    "All full-domain points and repeated requests charged")
            if index < len(trace) - 1:
                require(not accept, "No computation beyond first successful certificate")
            else:
                require(accept or bins == 4096, "No unregistered early stop")
        final = trace[-1]
        value = 4 * action * action + linear * action + 1
        regret = value - optimum_value
        require(F(row["action"]) == action and F(row["original_cost"]) == value,
                "Delivered original action and objective")
        require(F(row["regret"]) == regret == 4 * (action - optimum_action) ** 2,
                "Exact true regret identity")
        require(F(row["regret_bound"]) == allowance and 0 <= regret <= allowance,
                "Original action loss covered")
        require(row["qualified"] is accept and (not accept or regret <= tolerance),
                "Qualification and economic tolerance")
        require(row["bins"] == bins and row["unique_queries"] == 2 * bins + 1
                and row["requests"] == requests, "Final work and stopping receipt")
        summary = summaries[rule]
        summary["rows"] += 1
        summary["qualified"] += int(accept)
        summary["unresolved"] += int(not accept)
        summary["unique_queries"] += 2 * bins + 1
        summary["point_requests"] += requests
    require(seen == expected, "Every prescribed method/context retained")
    result = {
        "status": "passed", "method_rows": len(seen), "precision_attempts": trace_count,
        "exact_checks": checks, "summaries": summaries,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "audit_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "frozen_production_sha256": FROZEN_SOURCE_SHA256,
        "original_protocol_commit": PROTOCOL_COMMIT,
        "original_source_freeze_commit": SOURCE_FREEZE_COMMIT,
        "seconds": time.perf_counter() - started, "python": sys.version,
        "platform": platform.platform(),
        "scope": "New-host validation of the unchanged 120-row R117 exact supporting diagnostic; "
                 "not R117 original observations, investment evidence, population inference, or a theorem proof assistant.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    print(json.dumps(audit(arguments.input, arguments.output), indent=2))
