"""Exact independent original-policy and original-optimum validation for R120.

Only standard-library arithmetic and the byte-identified independent94 economic
primitives are imported. Production interval, fitting, risk, quadrature and
compiler modules are neither imported nor called. This is an independent
implementation, not a claim of external authorship. All unique returned actions
are evaluated; no outcome-dependent selection or refinement is permitted.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import resource
import sys
import time
import traceback

from custody120 import verify_source
from io120 import REVISION, append_jsonl, digest, exclusive_attempt, write_json

BINS = 64
TERMINAL_STEPS = 32
R = F(1, 32)
BETA = F(15, 16)
EPSILON = F(1, 2**20)
TAU = F(1, 256)
PRIMITIVE_SHA256 = "a1a0e4ce5563d1105c3cea9eaad6678c609229446ba6794f7b8a7c03df01ebad"
ARMS = ("online", "quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid")
SERVICES = ("completed", "legacy-safe", "paired", "direct-refine")
COUNTS = {}


def count(name, n=1):
    COUNTS[name] = COUNTS.get(name, 0) + n


def require(condition, message):
    count("executed_assertions")
    if not condition:
        raise AssertionError(message)


def exact(value):
    if isinstance(value, F):
        return value
    if isinstance(value, str):
        return F(value)
    return F(value)


def encoded(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encoded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encoded(v) for v in value]
    return value


def key(x, a, alpha):
    return (tuple(float(v).hex() for v in x), float(a).hex(), float(alpha).hex())


def key_id(k):
    return hashlib.sha256(json.dumps(k, separators=(",", ":")).encode()).hexdigest()


def load_primitives():
    path = REVISION / "frozen108/code/independent94.py"
    require(digest(path) == PRIMITIVE_SHA256, "Independent primitive source identity")
    tree = ast.parse(path.read_text())
    allowed = {"__future__", "fractions", "json", "math", "pathlib", "time"}
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    require(imports <= allowed, "No production or third-party scientific dependency")
    spec = importlib.util.spec_from_file_location("r120_exact_independent_primitives", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, dict(path=str(path.relative_to(REVISION)), sha256=PRIMITIVE_SHA256,
                        imports=sorted(imports), imported_after_source_commit_gate=True)


def read_rows(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def validate_catalogue(rows):
    require(len(rows) == 64 * 2 * len(ARMS) * len(SERVICES), "Complete primary census")
    seen, states, actions = set(), {}, {}
    for row in rows:
        identity = (row["index"], row["row"], row["arm"], row["service"])
        require(identity not in seen, "Duplicate primary identity")
        seen.add(identity)
        require(row["index"] in (0, 1) and 0 <= row["row"] < 64,
                "Declared risk and initial-state indices")
        require(row["arm"] in ARMS and row["service"] in SERVICES, "Declared method")
        alpha = F(1, 2) if row["index"] == 0 else F(3, 4)
        require(F(row["alpha"]) == alpha, "Original risk parameter")
        x, a = tuple(map(F, row["state"])), F(row["action"])
        require(len(x) == 2 and all(0 <= v < 1 and (v * 2**40).denominator == 1 for v in x),
                "Original two-coordinate 40-bit sampled state")
        require(row["state_hex"] == [float(v).hex() for v in x], "Exact state serialization")
        require(row["action_hex"] == float(a).hex(), "Exact action serialization")
        require(0 <= a <= F(1, 8) + sum(x) / 16, "Original action feasibility")
        require(row["population_observation"] is True and row["repeat"] is None,
                "Timing rows cannot become independent observations")
        require(row["original_initial_state_batch_size"] == 1, "Row-local population service")
        require(row["qualified"] is True, "Production qualification is required and separately audited")
        if row["row"] in states:
            require(states[row["row"]] == x, "Same independent state across risk and methods")
        states[row["row"]] = x
        k = key(x, a, alpha)
        actions[k] = dict(x=x, a=a, alpha=alpha)
    expected = {(i, j, arm, service) for i in (0, 1) for j in range(64)
                for arm in ARMS for service in SERVICES}
    require(seen == expected, "All predeclared observations, without exclusion")
    completed = {(r["index"], r["row"], r["arm"]): r for r in rows if r["service"] == "completed"}
    for row in rows:
        inc = completed[row["index"], row["row"], row["arm"]]
        require(F(row["completed_incumbent_action"]) == F(inc["action"]),
                "Every service starts at its independently rerun identical completed incumbent")
    return actions, completed


class ExactTrace:
    def __init__(self, path):
        self.raw = Path(path).open("xb")
        self.gz = gzip.GzipFile(filename="", mode="wb", fileobj=self.raw, mtime=0)
        self.text = io.TextIOWrapper(self.gz, encoding="utf-8", newline="\n")
        self.rows = 0

    def write(self, row):
        self.text.write(json.dumps(encoded(dict(sequence=self.rows, **row)), sort_keys=True) + "\n")
        self.rows += 1

    def flush(self):
        self.text.flush()
        self.raw.flush()
        os.fsync(self.raw.fileno())

    def close(self):
        self.text.close()
        self.raw.close()


def terminal(ir, y, alpha, support):
    count("terminal_contexts")
    require(all(F(1, 32) <= v <= F(27, 32) for v in y), "Invariant successor domain")
    lower, upper, action = ir.terminal_bounds(y, alpha, steps=TERMINAL_STEPS)
    capacity = F(1, 8) + sum(y) / (8 * len(y))
    require(0 <= action <= capacity, "Independent terminal feasibility")
    require(F(0) <= upper - lower <= EPSILON, "Independent original terminal gap")
    poly = ir.polynomial_from_primitives(y, action)
    require(poly[2] == 5, "Original even-dimensional quadratic shock coefficient")
    risk, left, right, eta = ir.tail_threshold(poly, alpha)
    require(right - left == 2 * R * alpha and -R <= left <= right <= R,
            "Exact feasible continuous-risk density")
    dual = (ir.integral(poly, -R, left) + ir.integral(poly, right, R)) / (2 * R * (1 - alpha))
    excess = list(poly)
    excess[0] -= eta
    primal = eta + (ir.integral(excess, -R, left) + ir.integral(excess, right, R)) / (2 * R * (1 - alpha))
    require(primal == dual == risk, "Independent exact continuous-risk primal-dual identity")
    original_value = ir.economic_S(y) + action**2 + 4 * action**4 + BETA * risk
    require(original_value == upper, "Independent original one-date objective identity")
    result = dict(state=y, action=action, lower=lower, upper=upper, polynomial=poly,
                  tail_left=left, tail_right=right, threshold=eta, risk_primal=primal,
                  risk_dual=dual, terminal_steps=TERMINAL_STEPS)
    if support:
        count("independent_state_gradient_supports")
        d = len(y)
        zero, at_r = ir.next_state(y, action, F(0)), ir.next_state(y, action, R)
        g0, gr = ir.economic_gradient(zero, True), ir.economic_gradient(at_r, True)
        # The squared aggregate hinge is independent of this alternating shock.
        # Integrate the exact affine state gradient against the fixed tail density.
        tail_mean = (left**2 - right**2) / (4 * R * (1 - alpha))
        mean_gradient = [g0[j] + (gr[j] - g0[j]) * tail_mean / R for j in range(d)]
        b = [F(1, 2) if j % 2 == 0 else F(1, 4) for j in range(d)]
        p_action = 2 * action + 16 * action**3 + BETA * sum(bj * gj for bj, gj in zip(b, mean_gradient))
        checked_value, checked_derivative = ir.objective_gradient(y, action, alpha)
        require(checked_value == upper and checked_derivative == p_action,
                "Independent integrated state-gradient action derivative identity")
        s_gradient = ir.economic_gradient(y)
        p_state = [s_gradient[j] + BETA * (mean_gradient[j] * (F(1, 2) + (1 - y[(j + 1) % d]) / 16)
                   + mean_gradient[(j - 1) % d] * (F(1, 8) - y[(j - 1) % d] / 16)) for j in range(d)]
        lam = max(F(0), -p_action) if action == capacity else F(0)
        nu = max(F(0), p_action) if action == 0 else F(0)
        residual = p_action + lam - nu
        anchor = upper + lam * (action - capacity) - nu * action - residual**2 / 4
        slope = [v - lam / (8 * d) for v in p_state]
        require(lam >= 0 and nu >= 0 and anchor <= upper, "Feasible Lagrange minorant")
        result.update(state_gradient=p_state, action_gradient=p_action, multiplier_upper=lam,
                      multiplier_lower=nu, stationarity_residual=residual,
                      support_anchor=anchor, support_slope=slope)
    return result


def upper_tail(values, alpha):
    count("exact_finite_tail_sorts")
    k = len(values) * (1 - alpha)
    require(k.denominator == 1 and 1 <= k <= len(values), "Integral equal-mass tail count")
    return sum(sorted(values, reverse=True)[:int(k)]) / k


def evaluate_action(ir, k, values, trace):
    started = time.perf_counter()
    x, a, alpha = values["x"], values["a"], values["alpha"]
    mids, endpoints = [], []
    kid = key_id(k)
    for node in range(2 * BINS + 1):
        z = -R + F(node, 2 * BINS) * 2 * R
        is_midpoint = node % 2 == 1
        result = terminal(ir, ir.next_state(x, a, z), alpha, is_midpoint)
        trace.write(dict(key_id=kid, node=node, z=z, midpoint=is_midpoint, **result))
        (mids if is_midpoint else endpoints).append(result)
    require(len(mids) == BINS and len(endpoints) == BINS + 1, "Complete fixed independent mesh")
    stage = ir.economic_S(x) + a * a + 4 * a**4
    q_lower = stage + BETA * upper_tail([v["lower"] for v in mids], alpha)
    # Duplicated adjacent endpoints are separate equal-probability atoms. They
    # must never be deduplicated from the upper comparison distribution.
    endpoint_atoms = [endpoints[j]["upper"] for j in range(BINS)] + [endpoints[j + 1]["upper"] for j in range(BINS)]
    q_upper = stage + BETA * upper_tail(endpoint_atoms, alpha)
    j_lower, j_upper = q_lower, q_upper + BETA * EPSILON
    require(q_lower <= q_upper <= j_upper, "Original-optimal-future and actual-future interval order")
    tails = int(BINS * (1 - alpha))
    selected = sorted(range(BINS), key=lambda j: (-mids[j]["support_anchor"], j))[:tails]
    # Each selected bin has exactly 1/tails risk mass. This is a feasible
    # original continuous density, not a discretized replacement of the model.
    anchor = stage + BETA * sum(mids[j]["support_anchor"] for j in selected) / tails
    b = [F(1, 2) if j % 2 == 0 else F(1, 4) for j in range(len(x))]
    gradient = 2 * a + 16 * a**3 + BETA * sum(sum(v * bj for v, bj in zip(mids[j]["support_slope"], b)) for j in selected) / tails
    cap = F(1, 8) + sum(x) / (8 * len(x))
    delta = max(-a, min(cap - a, -gradient / 2))
    optimum_lower = anchor + gradient * delta + delta * delta
    require(optimum_lower <= q_upper, "Independent all-action lower and feasible upper compatibility")
    result = dict(key_id=kid, state=[float(v) for v in x], state_hex=list(k[0]),
                  action=float(a), action_hex=k[1], alpha=float(alpha),
                  q_lower=q_lower, q_upper=q_upper, j_lower=j_lower, j_upper=j_upper,
                  optimum_lower=optimum_lower, all_action_anchor=anchor,
                  all_action_gradient=gradient, all_action_minimizer=a + delta,
                  risk_bin_indices=selected, risk_bin_mass=F(1, tails),
                  bins=BINS, terminal_steps=TERMINAL_STEPS,
                  terminal_contexts=2 * BINS + 1, seconds=time.perf_counter() - started,
                  future_controller_allowance_added_exactly_once=BETA * EPSILON)
    count("unique_original_policy_evaluations")
    trace.flush()
    return result


def compare_rows(rows, completed, policies, out):
    # Sharing here is limited to already purchased supports at one identical
    # initial state and risk. It is separately paid validation, never free input
    # to an experimental decision rule or a new population observation.
    state_bounds = {}
    for item in policies.values():
        sk = (tuple(item["state_hex"]), float(item["alpha"]).hex())
        old = state_bounds.get(sk)
        bounds = (item["optimum_lower"], item["q_upper"])
        state_bounds[sk] = bounds if old is None else (max(old[0], bounds[0]), min(old[1], bounds[1]))
    expected_states = {(tuple(row["state_hex"]), float(row["alpha"]).hex()) for row in rows}
    require(set(state_bounds) == expected_states, "All independent state/risk original-optimum intervals, including any repeated draws")
    for sk, (lo, hi) in state_bounds.items():
        require(lo <= hi, "Independent original optimum interval is nonempty")
        append_jsonl(out / "original_optima120.jsonl", encoded(dict(state_hex=sk[0], alpha_hex=sk[1], lower=lo, upper=hi)))
    for row in rows:
        k = key(row["state"], row["action"], row["alpha"])
        policy = policies[k]
        original = completed[row["index"], row["row"], row["arm"]]
        inc_key = key(original["state"], original["action"], original["alpha"])
        inc = policies[inc_key]
        lo, hi = state_bounds[(tuple(row["state_hex"]), float(row["alpha"]).hex())]
        pl, pu = F(row["complete_policy_lower"]), F(row["complete_policy_upper"])
        require(pl <= pu and max(pl, policy["j_lower"]) <= min(pu, policy["j_upper"]),
                "Production versus independent fixed-policy interval compatibility")
        require(F(row["original_optimum_lower"]) <= hi,
                "Production original lower versus independent feasible upper compatibility")
        if k == inc_key:
            gain_lower = gain_upper = F(0)
        else:
            gain_lower = max(F(0), inc["j_lower"] - policy["j_upper"])
            gain_upper = min(TAU, inc["j_upper"] - policy["j_lower"])
        require(F(0) <= gain_lower <= gain_upper <= TAU,
                "Independent gain interval and uniform safe-service support compatibility")
        certified = F(row["certified_gain_lower"])
        require(0 <= certified <= gain_upper, "Production improvement certificate versus independent upper compatibility")
        regret_lower, regret_upper = max(F(0), policy["j_lower"] - hi), policy["j_upper"] - lo
        require(0 <= regret_lower <= regret_upper, "Independent original policy regret interval")
        cap = F(1, 8) + sum(map(F, row["state"])) / 16
        result = dict(index=row["index"], row=row["row"], arm=row["arm"], service=row["service"],
                      key_id=policy["key_id"], incumbent_key_id=inc["key_id"],
                      state_hex=row["state_hex"], action_hex=row["action_hex"],
                      j_lower=policy["j_lower"], j_upper=policy["j_upper"],
                      original_optimum_lower=lo, original_optimum_upper=hi,
                      original_regret_lower=regret_lower, original_regret_upper=regret_upper,
                      squared_original_action_error_upper=min(cap**2, regret_upper),
                      gain_lower=gain_lower, gain_upper=gain_upper,
                      certified_gain_lower=certified, same_action=k == inc_key,
                      compatibility_is_not_an_exact_value_equality=True,
                      gain_interval_uses_row_local_policy_values_only=True)
        append_jsonl(out / "comparisons120.jsonl", encoded(result))
        count("independent_policy_comparisons")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = verify_source(args.source_commit)
    out, start_record = exclusive_attempt(args.output, "independent120", source)
    started = time.perf_counter()
    trace = None
    try:
        primary = args.primary.resolve()
        write_json(out / "PRIMARY_INPUT120.json", dict(path=str(primary), bytes=primary.stat().st_size,
                   sha256=digest(primary), input_read_after_source_gate=True,
                   all_primary_rows_required=True, no_adaptive_selection_or_resolution=True))
        rows = read_rows(primary)
        actions, completed = validate_catalogue(rows)
        ir, primitive_receipt = load_primitives()
        write_json(out / "INDEPENDENT_DESIGN120.json", dict(unique_actions=len(actions),
                   primary_rows=len(rows), bins=BINS, terminal_steps=TERMINAL_STEPS,
                   expected_terminal_contexts=len(actions) * (2 * BINS + 1),
                   primitives=primitive_receipt, independent_original_optimum_lower=True,
                   output_scope="exact rational original objective and all-action lower witnesses",
                   population_gain_bounds_are_row_local=True))
        trace = ExactTrace(out / "terminal_witnesses120.jsonl.gz")
        policies = {}
        for i, (k, values) in enumerate(sorted(actions.items())):
            append_jsonl(out / "PROGRESS120.jsonl", dict(event="action-start", index=i, key_id=key_id(k)))
            result = evaluate_action(ir, k, values, trace)
            policies[k] = result
            append_jsonl(out / "policies120.jsonl", encoded(result))
            append_jsonl(out / "PROGRESS120.jsonl", dict(event="action-complete", index=i,
                         key_id=key_id(k), seconds=result["seconds"], counts=dict(COUNTS)))
            if (i + 1) % 16 == 0 or i + 1 == len(actions):
                print("INDEPENDENT", i + 1, "/", len(actions), round(time.perf_counter() - started, 3), flush=True)
        trace.close()
        trace = None
        compare_rows(rows, completed, policies, out)
        require(digest(primary) == json.loads((out / "PRIMARY_INPUT120.json").read_text())["sha256"],
                "Primary input remained byte-identical through validation")
        write_json(out / "EXECUTION120.json", dict(status="executed", exit_code=0,
                   source=source, started_unix=start_record["started_unix"], ended_unix=time.time(),
                   total_seconds=time.perf_counter() - started, counts=COUNTS,
                   primary_observations=len(rows), unique_policy_keys=len(policies),
                   max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   no_claim_of_external_authorship=True,
                   no_claim_of_exact_deployed_future_policy_equality=True,
                   independent_global_original_optimum_and_regret_bounds=True))
    except BaseException:
        if trace is not None:
            trace.close()
        append_jsonl(out / "FAILED120.jsonl", dict(status="failed", source=source,
                     ended_unix=time.time(), elapsed_seconds=time.perf_counter() - started,
                     counts=COUNTS, exception=traceback.format_exc(), all_partial_evidence_retained=True))
        raise


if __name__ == "__main__":
    main()
