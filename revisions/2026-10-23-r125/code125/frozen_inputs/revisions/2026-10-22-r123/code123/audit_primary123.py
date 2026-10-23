"""Independent serialized-record audit for the R123 complete policy service.

The new algorithm is reconstructed by independent_envelopes123, which uses only
standard-library rational arithmetic. The optional inherited R122 auditor is a
separately pinned historical independent arithmetic reader, never a production
service. No economic oracle, trained actor, numpy, scipy, or optimizer is used.
"""
from __future__ import annotations

import argparse
import datetime as dt
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
import traceback

from independent_envelopes123 import RationalCertificate, serial


def _smoothness(alpha):
    beta = F(15, 16)
    m = F(1413, 128) + beta*(F(127, 16) + F(19625, 20480)*alpha/(1-alpha))
    return 5 + beta*(F(5, 16)*m + (F(4, 5)*m)**2*alpha/(F(181, 64)*(1-alpha)))


def _outward(x, upper):
    value = float(x)
    if upper and F(value) < x:
        value = math.nextafter(value, math.inf)
    elif not upper and F(value) > x:
        value = math.nextafter(value, -math.inf)
    return value


def _rounded(x, A):
    return F(max(0, min(int(x*2**30), int(A*2**30))), 2**30)


def _menu(case, engine):
    points = [("fused", engine.fused_minimizer())]
    for i, payload in enumerate(case["payloads"]):
        singleton = dict(case, payloads=[payload])
        points.append(("anchor-"+str(i), RationalCertificate(singleton).fused_minimizer()))
    return [{"source": label, "fraction": F(1, 2**j),
             "b": _rounded(engine.a+(point-engine.a)/2**j, engine.A)}
            for label, point in points for j in range(6)]


def audit_record(row, inherited_auditor=None):
    counts = {"rows": 1, "assertions": 0, "new_algorithm_rows": 0,
              "inherited_r122_rows": 0, "cases": 0, "payloads": 0,
              "candidate_records": 0, "accepted_actions": 0,
              "probe_queries_started": 0, "probe_queries_completed": 0,
              "retained_failure_rows": 0, "incomplete_cases": 0,
              "completed_prefix_candidates": 0, "failed_candidate_attempts": 0,
              "completed_candidates_discarded_after_failure": 0}
    mode = row["mode"]
    if mode == "r122":
        if inherited_auditor is None:
            raise ValueError("The R122 control requires its pinned historical independent auditor")
        old = inherited_auditor.audit(row)
        counts["inherited_r122_rows"] = 1
        counts["assertions"] = old["assertions"]
        counts["accepted_actions"] = old["accepted_actions"]
        counts["candidate_records"] = old["candidates"]
        counts["retained_failure_rows"] = old["retained_failure_rows"]
        return counts

    def require(condition, label):
        counts["assertions"] += 1
        if not condition:
            raise ArithmeticError("Independent R123 primary audit: "+label)

    require(mode in ("best_single", "fused", "probe_fused"), "known complete-service mode")
    counts["new_algorithm_rows"] = 1
    x = tuple(map(F, row["state"]))
    alpha = F(row["alpha"])
    require(len(x) == 2 and all(0 <= v <= 1 for v in x), "original state domain")
    require(alpha in (F(1, 2), F(3, 4)), "original risk preference")
    A = F(1, 8)+sum(x)/16
    incumbent = F(row["baseline_action"])
    require(0 <= incumbent <= A, "incumbent feasibility")
    require(0 <= F(row["baseline_upper"])-F(row["baseline_optimum_lower"]) <= F(1, 256),
            "completed original incumbent regret")
    require(0 <= F(row["baseline_upper"])-F(row["baseline_lower"]) <= F(1, 8192),
            "completed original incumbent width")
    cases = row["multi_anchor_cases"]
    partial = row.get("incomplete_menu_attempt")
    records = row["initial_support_certificates"]
    failure = row.get("enhancement_numerical_failure")
    if failure:
        counts["retained_failure_rows"] = 1
    require(partial is None or bool(failure), "an incomplete menu always belongs to a retained failure")
    require(len(cases) <= (2 if mode == "probe_fused" else 1), "fixed one-probe case budget")
    if records and not failure:
        require(bool(cases), "existing original support cannot silently bypass the case")
    require(row["support_count"] == len(records), "all captured supports retained")
    require(row["distinct_support_actions"] == len(set(F(c["original_action"]) for c in records)),
            "distinct captured support-action count")
    engines, winners, outward_winners = [], [], []
    total_refusals = 0
    previous_payloads = None
    stages = list(cases)
    if partial is not None:
        stages.append(dict(case=partial["case"], mode=partial["mode"],
                           candidates=partial["completed_candidates"], selected_index=None))
    incomplete_started = 0
    for case_index, stage in enumerate(stages):
        incomplete = partial is not None and case_index == len(cases)
        case = stage["case"]
        counts["incomplete_cases" if incomplete else "cases"] += 1
        require(F(case["A"]) == A and F(case["incumbent"]) == incumbent,
                "case original action-domain identity")
        require(F(case["mu"]) == 2 and F(case["L"]) == _smoothness(alpha),
                "case original curvature identity")
        require(F(case["delta"]) == F(15, 16777216) and F(case["tau"]) == F(1, 256)
                and F(case["omega"]) == F(1, 8192), "same original-policy allowance and tolerances")
        require(F(case["old_optimum_lower"]) == F(row["baseline_optimum_lower"]),
                "same completed incumbent optimum lower bound")
        require(case.get("gradient_rule") == "r122-finite-radii"
                and case.get("gradient_cap") == 7 and case.get("radius_indices") == [2, 40],
                "declared independent finite-radius recovery")
        payloads = case["payloads"]
        require(len(payloads) <= len(records), "no unrecorded original payload")
        for i, p in enumerate(payloads):
            c = records[i]
            counts["payloads"] += 1
            require(F(c["alpha"]) == alpha and c["original_state"] == [row["state"]],
                    "captured original state and risk")
            require(c["support_curvature"] == 2 and c["full_support_continuous_risk"] is True,
                    "captured original support premises")
            for key, raw in (("a", "original_action"), ("W", "support_anchor_lower"),
                             ("U", "original_q_upper"), ("p_lower", "support_slope_lower"),
                             ("p_upper", "support_slope_upper")):
                require(F(p[key]) == F(c[raw]), "immutable raw support field "+key)
        if previous_payloads is not None:
            require(payloads[:-1] == previous_payloads and len(payloads) == len(previous_payloads)+1,
                    "probe appends exactly one unchanged-prefix payload")
        previous_payloads = payloads
        engine = RationalCertificate(case)
        engines.append(engine)
        expected_mode = "best_single" if mode == "best_single" else "fused"
        require(stage["mode"] == expected_mode, "fixed arithmetic mode")
        expected_menu = _menu(case, engine)
        entries = stage["candidates"]
        if incomplete:
            incomplete_started = partial["started_candidates"]
            require(type(incomplete_started) is int and
                    0 <= len(entries) <= incomplete_started <= len(expected_menu),
                    "finite retained incomplete-menu prefix")
            require(partial["stage"] in ("support-minimum", "menu-construction", "candidate-arithmetic",
                                         "outward-conversion", "selection"), "declared failing arithmetic stage")
            counts["completed_prefix_candidates"] += len(entries)
            counts["completed_candidates_discarded_after_failure"] += len(entries)
            failed = partial["failed_attempt"]
            if failed is not None:
                require(incomplete_started == len(entries)+1 and failed["index"] == len(entries),
                        "one started and unfinished next candidate")
                expected = expected_menu[len(entries)]
                require(failed["source"] == expected["source"] and F(failed["fraction"]) == expected["fraction"]
                        and F(failed["b"]) == expected["b"], "failed attempt retains actual next menu action")
                require(failed["exception_type"] == failure["exception_type"] and bool(failed["traceback"]),
                        "failed candidate has retained exception identity")
            else:
                require(incomplete_started == len(entries), "no invisible unfinished candidate")
            counts["failed_candidate_attempts"] += incomplete_started-len(entries)
        else:
            require(len(entries) == len(expected_menu), "complete common finite candidate menu")
        eligible = []
        outward_by_index = {}
        for j, (entry, expected) in enumerate(zip(entries, expected_menu)):
            counts["candidate_records"] += 1
            require(entry["source"] == expected["source"] and F(entry["fraction"]) == expected["fraction"]
                    and F(entry["b"]) == expected["b"], "exact shared rounded menu order")
            actual = entry["certificate"]
            z = engine.candidate(expected["b"], expected_mode)
            mapping = {"b": "b", "change_lower": "q_contrast_lower", "change_upper": "q_contrast_upper",
                       "gain_lower": "gain_lower", "lower": "policy_lower", "upper": "policy_upper",
                       "optimum_lower": "optimum_lower", "loss": "regret_upper", "width": "width"}
            for key, target in mapping.items():
                require(F(actual[key]) == z[target], "exact candidate field "+key)
            require(F(actual["gain_upper"]) == -z["policy_contrast_lower"], "exact gain upper bound")
            require(F(actual["raw_envelope_minimum"]) == engine.support_minimum
                    and F(actual["raw_envelope_minimizer"]) == min(engine.support_minimizers),
                    "exact nonconvex raw-support global minimum and tie")
            require(actual["qualified"] is z["qualified"] and actual["accepted"] is z["eligible"],
                    "exact regret-width-gain qualification")
            low = _outward(z["policy_lower"], False)
            high = _outward(z["policy_upper"], True)
            B = _outward(z["optimum_lower"], False)
            loss = math.nextafter(high-B, math.inf)
            width = math.nextafter(high-low, math.inf)
            f = {"lower": low, "upper": high, "optimum_lower": B,
                 "loss": loss, "width": width,
                 "qualified": loss <= float(F(1, 256)) and width <= float(F(1, 8192))}
            require(entry["outward"] == f, "independent outward IEEE conversion")
            accepted = z["eligible"] and f["qualified"]
            require(entry["outward_accepted"] is accepted, "exact plus outward acceptance")
            if accepted:
                eligible.append((j, z))
                outward_by_index[j] = f
            else:
                total_refusals += 1
        winner = (min(eligible, key=lambda item: (-item[1]["gain_lower"], item[1]["b"], item[0]))
                  if eligible and not incomplete else None)
        require(stage["selected_index"] == (None if winner is None else winner[0]),
                "no incomplete-menu selection; completed menu uses prespecified gain and tie rule")
        winners.append(winner)
        outward_winners.append(None if winner is None else outward_by_index[winner[0]])
    require(row["candidate_algebra_attempts"] == counts["candidate_records"]+counts["failed_candidate_attempts"],
            "all started complete and incomplete candidate arithmetic charged")
    require(row["candidate_refusals"] == total_refusals, "all refused/unchanged candidates retained")
    probes = row.get("probes", [])
    require(len(probes) <= (1 if mode == "probe_fused" else 0), "at most one declared original query")
    if probes:
        require(bool(cases) and winners[0] is None, "probe only after initial menu has no qualified strict improvement")
        e = engines[0]
        left, right = e._zero("upper"), e._zero("lower")
        midpoint = (left+right)/2
        rounded = _rounded(midpoint, A)
        p = probes[0]
        require(F(p["bracket_lower"]) == left and F(p["bracket_upper"]) == right
                and F(p["midpoint"]) == midpoint and F(p["rounded_probe"]) == rounded
                and p["bins"] == 128, "exact optimum bracket and fixed midpoint query")
        needed = left < right and all(rounded != z["a"] for z in e.payloads)
        require(p["performed"] is needed, "no duplicate or empty-bracket query")
        if len(engines) == 2:
            e2 = engines[1]
            require(F(p["new_bracket_lower"]) == e2._zero("upper")
                    and F(p["new_bracket_upper"]) == e2._zero("lower"), "fresh bracket from appended support")
            require(p["payload"] == stages[1]["case"]["payloads"][-1]
                    and F(p["payload"]["a"]) == rounded, "fresh payload at paid rounded midpoint")
            require(e2._zero("upper") >= left and e2._zero("lower") <= right,
                    "additional information cannot enlarge the optimum bracket")
    starts, completions = row["new_risk_queries_started"], row["new_risk_queries_completed"]
    require(isinstance(starts, int) and isinstance(completions, int)
            and 0 <= completions <= starts <= 1, "finite paid starts/completions")
    require(starts == sum(p["performed"] for p in probes), "every started probe recorded")
    if not failure:
        require(starts == completions and completions == max(0, len(cases)-1),
                "successful query has exactly one appended case")
    counts["probe_queries_started"], counts["probe_queries_completed"] = starts, completions
    winner = None if failure or not winners else winners[-1]
    require(row["accepted_improvement"] is (winner is not None), "returned selection identity")
    if winner:
        z, f = winner[1], outward_winners[-1]
        require(F(row["action"]) == z["b"] and F(row["certified_policy_gain_lower"]) == z["gain_lower"] > 0,
                "actual deployed action and positive original-policy gain")
        for key, target in (("complete_policy_lower", "lower"), ("complete_policy_upper", "upper"),
                            ("original_optimum_lower", "optimum_lower"), ("certified_regret_upper", "loss"),
                            ("lower", "lower"), ("upper", "upper"), ("optimum_lower", "optimum_lower"),
                            ("width", "width")):
            require(row[key] == f[target], "returned exact outward endpoint "+key)
        counts["accepted_actions"] = 1
    else:
        require(F(row["action"]) == incumbent and F(row["certified_policy_gain_lower"]) == 0,
                "retention has exactly the same action and zero gain")
        require(row["complete_policy_lower"] == row["baseline_lower"]
                and row["complete_policy_upper"] == row["baseline_upper"]
                and row["original_optimum_lower"] == row["baseline_optimum_lower"], "retained incumbent certificate")
    require(row["qualified"] is True and 0 <= F(row["action"]) <= A
            and float(row["action"]).hex() == row["action_hex"], "final feasible binary action identity")
    return counts


def load_historical_auditor(path):
    spec = importlib.util.spec_from_file_location("pinned_historical_independent_r122_arithmetic", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def file_digest(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024*1024), b""):
            value.update(chunk)
    return value.hexdigest()


def input_records(path):
    """Stream the complete campaign, or read a small declared diagnostic JSON."""
    if path.suffix == ".json":
        document = json.loads(path.read_text())
        records = document["records"] if isinstance(document, dict) else document
        for number, record in enumerate(records):
            yield number, record
        return
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as source:
        for number, line in enumerate(source):
            if line.strip():
                yield number, json.loads(line)


class FrozenCensus:
    """Independent fixed-catalogue and source/state binding, without common123."""
    def __init__(self, root):
        self.root = root.resolve()
        self.boundary_path = self.root / "BOUNDARIES123.json"
        self.manifest_path = self.root / "SOURCE_FREEZE123.json"
        self.state_path = self.root / "results123/states/states123.json"
        self.boundary_digest = file_digest(self.boundary_path)
        self.boundaries = json.loads(self.boundary_path.read_text())
        manifest = json.loads(self.manifest_path.read_text())
        if file_digest(self.manifest_path) != self.boundaries["source_manifest_sha256"]:
            raise ValueError("Frozen source manifest does not match published boundary")
        for field in ("source_commit", "state_commit"):
            value = self.boundaries[field]
            if len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError("Full published source/state commit required")
        for relative, expected in manifest["files"].items():
            if file_digest(self.root / relative) != expected:
                raise ValueError("Frozen source member changed: "+relative)
        self.frozen_source_files = len(manifest["files"])
        if file_digest(self.state_path) != self.boundaries["states_sha256"]:
            raise ValueError("Original frozen state bytes do not match boundary")
        states = json.loads(self.state_path.read_text())
        if states["source_commit"] != self.boundaries["source_commit"]:
            raise ValueError("State draw belongs to another source commit")
        self.states = {}
        for record in states["states"]:
            number = record["row"]
            if type(number) is not int or number in self.states or not 0 <= number < 32:
                raise ValueError("Invalid or duplicate frozen state row")
            values = record["state"]
            if (len(values) != 2 or any(not 0 <= F(v) <= 1 for v in values)
                    or [float(v).hex() for v in values] != record["state_hex"]):
                raise ValueError("Invalid frozen original state values/hex")
            self.states[number] = record
        if set(self.states) != set(range(32)):
            raise ValueError("All 32 independently frozen state rows required")
        actors = [(i, 0, "online", "online") for i in range(2)]
        actors += [(i, budget, arm, loss) for i in range(2) for budget in (5, 9)
                   for arm in ("quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid")
                   for loss in ("value", "marginal")]
        self.expected = {actor+(mode, number) for actor in actors
                         for mode in ("r122", "best_single", "fused", "probe_fused")
                         for number in range(32)}
        assert len(self.expected) == 7424
        self.seen = set()

    def validate(self, row):
        identity = tuple(row[field] for field in
                         ("index", "budget", "arm", "training_loss", "mode", "row"))
        if identity not in self.expected:
            raise ValueError("Undeclared whole-catalogue identity: "+repr(identity))
        if identity in self.seen:
            raise ValueError("Duplicate primary identity: "+repr(identity))
        for field in ("source_commit", "state_commit"):
            if row[field] != self.boundaries[field]:
                raise ValueError("Primary "+field+" mismatch")
        if row["population_observation"] is not True:
            raise ValueError("Timing or diagnostic row substituted for primary observation")
        original = self.states[row["row"]]
        if row["state"] != original["state"] or row["state_hex"] != original["state_hex"]:
            raise ValueError("Primary row does not match its exact frozen original state")
        if F(row["alpha"]) != (F(1, 2), F(3, 4))[row["index"]]:
            raise ValueError("Risk label does not match original risk preference")
        self.seen.add(identity)

    def finish(self):
        if self.seen != self.expected:
            missing = self.expected-self.seen
            raise ValueError("Whole primary census incomplete: "+str(len(missing))+
                             " missing identities; first "+repr(sorted(missing)[:8]))
        if file_digest(self.boundary_path) != self.boundary_digest:
            raise ValueError("Published boundary changed during independent audit")
        if file_digest(self.manifest_path) != self.boundaries["source_manifest_sha256"]:
            raise ValueError("Frozen manifest changed during independent audit")
        if file_digest(self.state_path) != self.boundaries["states_sha256"]:
            raise ValueError("Frozen state bytes changed during independent audit")
        return dict(status="passed", expected_rows=7424, unique_primary_identities=len(self.seen),
                    independent_state_units=32, method_cells=232,
                    source_files_verified_before_input_processing=self.frozen_source_files,
                    source_manifest_sha256=self.boundaries["source_manifest_sha256"],
                    states_sha256=self.boundaries["states_sha256"],
                    source_commit=self.boundaries["source_commit"],
                    state_commit=self.boundaries["state_commit"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--r122-auditor", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fixture", action="store_true",
                      help="Engineering data only: explicitly disable the prospective whole-census claim")
    mode.add_argument("--frozen-root", type=Path,
                      help="R123 root with SOURCE_FREEZE123, BOUNDARIES123 and frozen states; default is code parent")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    tick = time.perf_counter()
    sources = [Path(__file__), Path(__file__).with_name("independent_envelopes123.py")]
    old, census = None, None
    input_before = file_digest(args.input)
    global_failures = []
    census_receipt = {"status": "not_requested", "scope": "Explicit engineering fixture, not a population census"}
    try:
        if not args.fixture:
            census = FrozenCensus(args.frozen_root or Path(__file__).resolve().parents[1])
    except Exception:
        global_failures.append(traceback.format_exc())
    if args.r122_auditor:
        old = load_historical_auditor(args.r122_auditor)
        sources.append(args.r122_auditor)
    total, failures, rows = {}, 0, 0
    with args.output.joinpath("ROWS123.jsonl").open("x") as target:
        try:
            for index, record in input_records(args.input):
                rows += 1
                try:
                    if census is not None:
                        census.validate(record)
                    counts = audit_record(record, old)
                    for key, value in counts.items():
                        total[key] = total.get(key, 0)+value
                    result = {"index": index, "status": "passed", "counts": counts}
                except Exception:
                    failures += 1
                    result = {"index": index, "status": "failed", "traceback": traceback.format_exc()}
                target.write(json.dumps(result, sort_keys=True)+"\n")
                if rows % 32 == 0:
                    target.flush()
                    print("AUDIT_ROWS", rows, "FAILURES", failures, flush=True)
        except Exception:
            global_failures.append(traceback.format_exc())
    try:
        if file_digest(args.input) != input_before:
            raise ValueError("Primary input bytes changed during independent audit")
        if census is not None:
            census_receipt = census.finish()
    except Exception:
        global_failures.append(traceback.format_exc())
    receipt = {"schema": "nbo.r123.independent-primary-arithmetic.v1",
               "status": "passed" if failures == 0 and not global_failures else "failed", "rows": rows,
               "failed_rows": failures, "counts": total, "global_failures": global_failures,
               "whole_census_binding": census_receipt,
               "seconds": time.perf_counter()-tick,
               "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "input_sha256": input_before, "input_sha256_after": file_digest(args.input),
               "source_hashes": {str(p): file_digest(p) for p in sources},
               "original_economic_queries": 0, "new_population_observations": 0,
               "scope": "Exact serialized support, menu, selection, outward rounding and query-account implications; original economic premises are checked separately."}
    args.output.joinpath("EXECUTION123.json").write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if failures == 0 and not global_failures else 1


if __name__ == "__main__":
    sys.exit(main())
