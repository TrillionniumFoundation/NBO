"""Independent rational reader for serialized multi-anchor Bellman certificates.

Only Python's standard library is used; no production operator, interval,
fitting, optimization, or certificate implementation is imported. This reader
verifies mathematical implications of supplied original-model anchor payloads.
It does not by itself establish that a supplied anchor encloses an economic
oracle: that requires a separate original-primitive evaluation.

The raw interval-slope support envelope need NOT be convex globally. Its exact
global minimum is found by splitting at all anchor kinks and all affine
crossings after removing the common quadratic term.
"""
from __future__ import annotations

import argparse
import datetime as dt
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time
import traceback

F = Fraction


def rational(x):
    """Floats are interpreted as their exact binary64 numbers, never decimals."""
    if isinstance(x, bool):
        raise ValueError("Boolean is not a numerical certificate endpoint")
    return x if isinstance(x, F) else F(x)


def serial(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [serial(v) for v in x]
    return x


def _linear_value(line, x):
    return line[0] * x + line[1]


def _crossings(lines, lo, hi):
    cuts = {lo, hi}
    for left, right in itertools.combinations(lines, 2):
        dm = left[0] - right[0]
        if dm:
            x = (right[1] - left[1]) / dm
            if lo < x < hi:
                cuts.add(x)
    return sorted(cuts)


class RationalCertificate:
    def __init__(self, case):
        self.original = case
        self.A = rational(case["A"])
        self.a = rational(case["incumbent"])
        self.mu = rational(case["mu"])
        self.L = rational(case["L"])
        self.delta = rational(case["delta"])
        self.tau = rational(case["tau"])
        self.omega = rational(case["omega"])
        self.old_B = rational(case["old_optimum_lower"])
        if not (self.A > 0 and 0 <= self.a <= self.A):
            raise ValueError("Invalid capacity or infeasible incumbent")
        if not (0 < self.mu <= self.L and self.delta >= 0):
            raise ValueError("Invalid curvature or future-policy allowance")
        if self.tau < 0 or self.omega < 0:
            raise ValueError("Negative qualification threshold")
        self.payloads = []
        for item in case["payloads"]:
            p = {k: rational(item[k]) for k in
                 ("a", "W", "U", "p_lower", "p_upper", "g_lower", "g_upper")}
            if not (0 <= p["a"] <= self.A and p["W"] <= p["U"]):
                raise ValueError("Invalid anchor domain or value interval")
            if p["p_lower"] > p["p_upper"] or p["g_lower"] > p["g_upper"]:
                raise ValueError("Reversed support or gradient interval")
            self.payloads.append(p)
        if not self.payloads:
            raise ValueError("At least one paid payload is required")
        self.gradient_recovery = self._check_gradient_recovery(case)
        self.lower_pieces = self._derivative_envelope("lower")
        self.upper_pieces = self._derivative_envelope("upper")
        self._check_envelope_consistency()
        self.support_minimum, self.support_minimizers, self.support_pieces = self._raw_minimum()
        self.B = max(self.old_B, self.support_minimum)

    def _check_gradient_recovery(self, case):
        rule = case.get("gradient_rule", "provided-validated-intervals")
        if rule == "provided-validated-intervals":
            return {"rule": rule, "independently_rederived": False,
                    "premise": "Each supplied gradient interval encloses the original Q derivative."}
        if rule != "r122-finite-radii":
            raise ValueError("Unknown gradient recovery rule")
        cap = rational(case.get("gradient_cap", 7))
        indices = case.get("radius_indices", [2, 40])
        if len(indices) != 2 or not (2 <= indices[0] <= indices[1] <= 100):
            raise ValueError("Invalid finite-radius index range")
        if cap <= 0:
            raise ValueError("Gradient cap must be positive")
        result = []
        for p in self.payloads:
            e = p["U"] - p["W"]
            k = self.L - self.mu
            def radius(side):
                if not side:
                    return None
                hs = {side}
                hs.update(F(1, 2**j) for j in range(indices[0], indices[1] + 1)
                          if F(1, 2**j) <= side)
                return min(e / h + k * h / 2 for h in hs)
            right, left = radius(self.A - p["a"]), radius(p["a"])
            gl = max(-cap, p["p_lower"] - right) if right is not None else -cap
            gu = min(cap, p["p_upper"] + left) if left is not None else cap
            if p["g_lower"] != gl or p["g_upper"] != gu:
                raise ValueError("Stored gradient endpoints disagree with independent finite-radius recovery")
            result.append({"a": p["a"], "g_lower": gl, "g_upper": gu,
                           "left_radius": left, "right_radius": right})
        return {"rule": rule, "independently_rederived": True, "anchors": result,
                "premise": "Raw supports, upper Q bounds, curvature and gradient cap are valid."}

    def _derivative_line(self, i, side, x):
        p = self.payloads[i]
        if side == "lower":
            m = self.L if x < p["a"] else self.mu
            g = p["g_lower"]
        elif side == "upper":
            m = self.mu if x < p["a"] else self.L
            g = p["g_upper"]
        else:
            raise ValueError("Unknown derivative side")
        return (m, g - m * p["a"])

    def _derivative_envelope(self, side):
        # First split at slope changes, then at every possible active-line change.
        roots = sorted({F(0), self.A, *(p["a"] for p in self.payloads)})
        result = []
        for lo, hi in zip(roots, roots[1:]):
            if lo == hi:
                continue
            midpoint = (lo + hi) / 2
            lines = [self._derivative_line(i, side, midpoint)
                     for i in range(len(self.payloads))]
            cuts = _crossings(lines, lo, hi)
            for l, h in zip(cuts, cuts[1:]):
                t = (l + h) / 2
                values = [_linear_value(z, t) for z in lines]
                target = max(values) if side == "lower" else min(values)
                active = values.index(target)
                m, c = lines[active]
                result.append({"lo": l, "hi": h, "slope": m,
                               "intercept": c, "active": active})
        return result

    @staticmethod
    def _piece_value(p, x):
        return p["slope"] * x + p["intercept"]

    def _value(self, side, x):
        values = [_linear_value(self._derivative_line(i, side, x), x)
                  for i in range(len(self.payloads))]
        return max(values) if side == "lower" else min(values)

    def _check_envelope_consistency(self):
        cuts = {F(0), self.A}
        for p in self.lower_pieces + self.upper_pieces:
            cuts.update((p["lo"], p["hi"]))
        for x in cuts:
            if self._value("lower", x) > self._value("upper", x):
                raise ValueError("Inconsistent transported gradient envelopes")

    def _integrate_fused(self, side, lo, hi):
        if not (0 <= lo <= hi <= self.A):
            raise ValueError("Integration outside the original feasible interval")
        pieces = self.lower_pieces if side == "lower" else self.upper_pieces
        value = F(0)
        for p in pieces:
            l, h = max(lo, p["lo"]), min(hi, p["hi"])
            if l < h:
                value += p["slope"] * (h*h - l*l) / 2 + p["intercept"] * (h-l)
        return value

    def _integrate_single(self, i, side, lo, hi):
        p = self.payloads[i]
        cuts = sorted({lo, hi, *([p["a"]] if lo < p["a"] < hi else [])})
        value = F(0)
        for l, h in zip(cuts, cuts[1:]):
            m, c = self._derivative_line(i, side, (l+h)/2)
            value += m * (h*h-l*l)/2 + c*(h-l)
        return value

    def contrast(self, a, b, mode="fused"):
        a, b = rational(a), rational(b)
        if not (0 <= a <= self.A and 0 <= b <= self.A):
            raise ValueError("Contrast action outside feasible interval")
        if a == b:
            return F(0), F(0)
        lo, hi = min(a, b), max(a, b)
        if mode == "fused":
            low = self._integrate_fused("lower", lo, hi)
            high = self._integrate_fused("upper", lo, hi)
        elif mode == "best_single":
            # Selection occurs once for the entire path in the comparator.
            low = max(self._integrate_single(i, "lower", lo, hi)
                      for i in range(len(self.payloads)))
            high = min(self._integrate_single(i, "upper", lo, hi)
                       for i in range(len(self.payloads)))
        else:
            raise ValueError("Unknown comparison mode")
        return (low, high) if a < b else (-high, -low)

    def raw_support(self, i, x):
        p = self.payloads[i]
        d = rational(x) - p["a"]
        return p["W"] + min(p["p_lower"]*d, p["p_upper"]*d) + self.mu*d*d/2

    def _raw_minimum(self):
        # Removing mu*x^2/2 leaves piecewise affine functions. Interval-slope
        # anchor kinks are split explicitly; global convexity is never assumed.
        roots = sorted({F(0), self.A, *(p["a"] for p in self.payloads)})
        minimum = None
        minimizers = []
        pieces = []
        for lo, hi in zip(roots, roots[1:]):
            middle = (lo+hi)/2
            lines = []
            for p in self.payloads:
                slope = p["p_upper"] if middle < p["a"] else p["p_lower"]
                lines.append((slope-self.mu*p["a"],
                              p["W"]-slope*p["a"]+self.mu*p["a"]**2/2))
            cuts = _crossings(lines, lo, hi)
            for l, h in zip(cuts, cuts[1:]):
                t = (l+h)/2
                values = [_linear_value(z, t) for z in lines]
                active = values.index(max(values))
                m, c = lines[active]
                vertex = max(l, min(h, -m/self.mu))
                checks = [(x, self.mu*x*x/2+m*x+c) for x in {l, h, vertex}]
                local = min(value for _, value in checks)
                local_x = sorted(x for x, value in checks if value == local)
                if minimum is None or local < minimum:
                    minimum, minimizers = local, local_x
                elif local == minimum:
                    minimizers.extend(local_x)
                pieces.append({"lo": l, "hi": h, "linear_slope": m,
                               "linear_intercept": c, "active": active,
                               "minimum": local, "minimizers": local_x})
        return minimum, sorted(set(minimizers)), pieces

    def absolute_lower(self, b):
        b = rational(b)
        if not 0 <= b <= self.A:
            raise ValueError("Infeasible lower-bound target")
        return max(max(p["W"] + self.contrast(p["a"], b)[0],
                       self.raw_support(i, b))
                   for i, p in enumerate(self.payloads))

    def absolute_upper_q(self, b, mode):
        b = rational(b)
        return min(p["U"] + self.contrast(p["a"], b, mode)[1]
                   for p in self.payloads)

    def _zero(self, side):
        if self._value(side, F(0)) >= 0:
            return F(0)
        if self._value(side, self.A) <= 0:
            return self.A
        pieces = self.lower_pieces if side == "lower" else self.upper_pieces
        for p in pieces:
            if self._piece_value(p, p["lo"]) <= 0 <= self._piece_value(p, p["hi"]):
                return -p["intercept"] / p["slope"]
        raise ArithmeticError("Strictly increasing envelope has no located zero")

    def fused_minimizer(self):
        # M_upper(a,b) has lower-envelope derivative left of a, and
        # upper-envelope derivative right of a, with an upward jump at a.
        if self._value("lower", self.a) > 0:
            return min(self.a, self._zero("lower"))
        if self._value("upper", self.a) < 0:
            return max(self.a, self._zero("upper"))
        return self.a

    def candidate(self, b, mode):
        b = rational(b)
        if not 0 <= b <= self.A:
            raise ValueError("Infeasible candidate")
        lower = self.absolute_lower(b)
        upper_q = self.absolute_upper_q(b, mode)
        if lower > upper_q:
            raise ValueError("Inconsistent absolute Q enclosure")
        upper = upper_q + self.delta
        if self.B > upper_q:
            raise ValueError("Global optimum lower bound exceeds feasible Q upper")
        qlo, qhi = self.contrast(self.a, b, mode)
        if self.original.get("direct_value_contrast", False):
            qlo = max(qlo, lower-self.absolute_upper_q(self.a, mode))
            qhi = min(qhi, upper_q-self.absolute_lower(self.a))
        if qlo > qhi:
            raise ValueError("Inconsistent Q contrast")
        if b == self.a:
            policy_lo = policy_hi = F(0)
        else:
            policy_lo, policy_hi = qlo-self.delta, qhi+self.delta
        regret = upper-self.B
        width = upper-lower
        qualified = regret <= self.tau and width <= self.omega
        return {"b": b, "q_contrast_lower": qlo, "q_contrast_upper": qhi,
                "policy_contrast_lower": policy_lo, "policy_contrast_upper": policy_hi,
                "q_lower": lower, "q_upper": upper_q,
                "policy_lower": lower, "policy_upper": upper,
                "optimum_lower": self.B, "regret_upper": regret, "width": width,
                "squared_action_error_upper": 2*regret/self.mu,
                "gain_lower": -policy_hi, "qualified": qualified,
                "unchanged": b == self.a,
                "eligible": b != self.a and qualified and policy_hi < 0}


def _check_rounding(case, candidate):
    if "proposal_raw" not in candidate:
        return None
    bits = case.get("rounding_bits")
    if not isinstance(bits, int) or isinstance(bits, bool) or not 1 <= bits <= 100:
        raise ValueError("Finite feasible rounding requires an explicit bit count")
    cap = rational(case.get("safe_capacity", case["A"]))
    if not 0 <= cap <= rational(case["A"]):
        raise ValueError("Unsafe rounding capacity")
    scale = 2**bits
    raw = rational(candidate["proposal_raw"])
    expected = F(max(0, min(raw*scale//1, cap*scale//1)), scale)
    if rational(candidate["b"]) != expected:
        raise ValueError("Candidate is not the declared downward feasible rounding")
    return {"bits": bits, "safe_capacity": cap, "raw": raw, "rounded": expected}


def _check_budget(case):
    if "query_ledger" not in case:
        return {"checked": False, "reason": "No query ledger supplied; no cost/budget claim is inferred."}
    used = F(0)
    seen = set()
    failed = 0
    for record in case["query_ledger"]:
        identity = record["query_id"]
        if identity in seen:
            raise ValueError("Duplicate paid query identity")
        seen.add(identity)
        cost = rational(record["charge"])
        if cost < 0:
            raise ValueError("Negative query charge")
        used += cost
        if not record.get("completed", True):
            failed += 1
    if "query_charge" in case and used != rational(case["query_charge"]):
        raise ValueError("Declared query charge omits or duplicates ledger entries")
    if "query_budget" in case and used > rational(case["query_budget"]):
        raise ValueError("Declared paid query budget exceeded")
    return {"checked": True, "queries": len(seen), "failed_charged_queries": failed,
            "charge": used, "budget": case.get("query_budget"),
            "scope": "Serialized charge reconciliation, not an independent physical clock measurement."}


def analyze_case(case):
    engine = RationalCertificate(case)
    candidates = []
    for raw in case.get("candidates", []):
        c = raw if isinstance(raw, dict) else {"b": raw}
        rounding = _check_rounding(case, c)
        b = rational(c["b"])
        modes = {mode: engine.candidate(b, mode) for mode in ("fused", "best_single")}
        f, s = modes["fused"], modes["best_single"]
        if not (f["q_contrast_lower"] >= s["q_contrast_lower"] and
                f["q_contrast_upper"] <= s["q_contrast_upper"] and
                f["q_upper"] <= s["q_upper"] and f["q_lower"] == s["q_lower"] and
                f["optimum_lower"] == s["optimum_lower"]):
            raise ArithmeticError("Exact same-payload certificate dominance failed")
        if s["eligible"] and not f["eligible"]:
            raise ArithmeticError("Fused envelope lost an eligible common candidate")
        candidates.append({"b": b, "rounding": rounding, "modes": modes})
    return {"schema": "nbo.r123.independent-envelope-arithmetic.v1",
            "A": engine.A, "incumbent": engine.a, "payload_count": len(engine.payloads),
            "gradient_recovery": engine.gradient_recovery,
            "raw_support_minimum": engine.support_minimum,
            "raw_support_minimizers": engine.support_minimizers,
            "optimum_lower": engine.B,
            "lower_envelope": engine.lower_pieces, "upper_envelope": engine.upper_pieces,
            "raw_support_envelope": engine.support_pieces,
            "fused_continuous_minimizer": engine.fused_minimizer(),
            "budget": _check_budget(case), "candidates": candidates,
            "economic_primitive_execution": False,
            "scope": "Exact consequences of supplied sound original-Q anchors, derivative bounds and future allowance."}


def validate_case(case):
    result = analyze_case(case)
    mismatches = []
    checks = 0
    for supplied, expected in zip(case.get("candidates", []), result["candidates"]):
        if not isinstance(supplied, dict):
            continue
        claims = supplied.get("modes", supplied.get("claimed", {}))
        for mode, values in claims.items():
            if mode not in expected["modes"]:
                mismatches.append({"b": expected["b"], "field": mode, "reason": "Unknown mode"})
                continue
            for field, actual in values.items():
                if field not in expected["modes"][mode]:
                    raise ValueError("Unknown claimed certificate field: "+field)
                wanted = expected["modes"][mode][field]
                checks += 1
                same = (actual is wanted) if isinstance(wanted, bool) else rational(actual) == wanted
                if not same:
                    mismatches.append({"b": expected["b"], "mode": mode, "field": field,
                                       "supplied": actual, "expected": wanted})
    return {"status": "passed" if not mismatches else "failed", "compared_fields": checks,
            "mismatches": mismatches, "analysis": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    tick = time.perf_counter()
    args.output.mkdir(parents=True, exist_ok=False)
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    input_hash = hashlib.sha256(args.input.read_bytes()).hexdigest()
    passed = failed = fields = 0
    with args.output.joinpath("CASES123.jsonl").open("x") as stream:
        for index, line in enumerate(args.input.read_text().splitlines()):
            if not line.strip():
                continue
            try:
                case = json.loads(line)
                report = validate_case(case)
                fields += report["compared_fields"]
                if report["status"] == "passed":
                    passed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
                report = {"status": "failed", "traceback": traceback.format_exc()}
            stream.write(json.dumps(serial({"index": index, **report}), sort_keys=True)+"\n")
    receipt = {"schema": "nbo.r123.independent-envelope-execution.v1",
               "status": "passed" if failed == 0 else "failed",
               "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "seconds": time.perf_counter()-tick, "source_sha256": source_hash,
               "input_sha256": input_hash, "passed_cases": passed, "failed_cases": failed,
               "compared_fields": fields, "original_economic_queries": 0,
               "independent_population_observations": 0,
               "scope": "Independent exact rational anchor/certificate arithmetic; sound economic inputs are premises."}
    args.output.joinpath("EXECUTION123.json").write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
