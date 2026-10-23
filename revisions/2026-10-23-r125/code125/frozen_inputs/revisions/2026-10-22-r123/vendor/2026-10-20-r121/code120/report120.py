"""Read-only, post-freeze reporting of the prospectively frozen R120 study.

This file was specified and authored without reading R120 scientific outcomes.
It imports only the standard library, evaluates no economic primitive, and
changes no frozen input. Its own reporting receipt is separate from the science
freeze and from the actual experiment's cost. See REPORTING_SPEC120.md.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import datetime as dt
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import io
import itertools
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import traceback


SOURCE = "369d02724cf12ae0e54390b4e7b5f894f703892e"
ARMS = ("online", "quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid")
SERVICES = ("completed", "legacy-safe", "paired", "direct-refine")
LEVELS = (F(1, 2), F(3, 4))
N = 64
TIMING_N = 32
TAU = F(1, 256)
WIDTH = F(1, 8192)
BETA = F(15, 16)
EPS = F(1, 2**20)
RADIUS = F(33, 128) * TAU
EVENT_DELTA = F(1, 7680)
THRESHOLDS = (F(1, 2**20), F(1, 2**18), F(1, 2**16), F(1, 2**14))
VOLUMES = (1, 64, 1024, 65536)
GROUPS = tuple((i, arm, service) for i in range(2) for arm in ARMS for service in SERVICES)
SHORT = {"online": "Online", "quadratic": "Quadratic", "relu": "ReLU",
         "hinge": "Hinge", "spline": "Spline", "poly2": "Poly2",
         "poly3": "Poly3", "grid": "Grid", "completed": "C",
         "legacy-safe": "L", "paired": "P", "direct-refine": "D"}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def exact(value):
    if isinstance(value, float):
        require(math.isfinite(value), "Nonfinite input cannot be a reported bound")
    return F(value)


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def blob(path):
    path = Path(path)
    h = hashlib.sha1(b"blob " + str(path.stat().st_size).encode() + b"\0")
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def identity(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path), git_blob=blob(path))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(encode(value), stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def append_json(path, value):
    with Path(path).open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(encode(value), sort_keys=True, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def table(root, name, rows, fields=None):
    """Keep exact rational strings in the authoritative JSON and CSV cells."""
    rows = list(rows)
    write_json(root / (name + ".json"), rows)
    if fields is None:
        fields = list(dict.fromkeys(k for row in rows for k in row))
    with (root / (name + ".csv")).open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            clean = {}
            for key in fields:
                value = encode(row.get(key, ""))
                clean[key] = json.dumps(value, sort_keys=True, separators=(",", ":")) if isinstance(value, (dict, list)) else value
            writer.writerow(clean)


class Inputs:
    """Bind each actual read and verify that no registered input later changed."""
    def __init__(self, revision, evidence, repository):
        self.revision = revision.resolve()
        self.evidence = evidence.resolve()
        self.repository = repository.resolve()
        self.records = {}
        self.trees = {}

    def bind(self, path):
        path = Path(path).resolve()
        now = identity(path)
        old = self.records.get(str(path))
        require(old is None or now == old, "Input changed between reads: " + str(path))
        self.records[str(path)] = now
        return now

    def json(self, path):
        self.bind(path)
        with Path(path).open(encoding="utf-8") as stream:
            value = json.load(stream)
        self.bind(path)
        return value

    def bytes(self, path):
        self.bind(path)
        raw = Path(path).read_bytes()
        self.bind(path)
        return raw

    def jsonl(self, path):
        self.bind(path)
        opener = gzip.open if str(path).endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    yield json.loads(line)
        self.bind(path)

    def final(self):
        for path, old in self.records.items():
            require(identity(path) == old, "Input changed during reporting: " + path)
        return sorted(self.records.values(), key=lambda row: row["path"])

    def tree(self, commit):
        require(len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "Full immutable commit required")
        if commit not in self.trees:
            prefix = self.revision.relative_to(self.repository).as_posix()
            run = subprocess.run(["git", "-C", str(self.repository), "ls-tree", "-r", "-z", commit, "--", prefix],
                                 check=True, capture_output=True)
            result = {}
            for item in run.stdout.split(b"\0"):
                if item:
                    meta, path = item.split(b"\t", 1)
                    mode, kind, sha = meta.decode().split()
                    if kind == "blob":
                        result[path.decode()] = sha
            self.trees[commit] = result
        return self.trees[commit]

    def git_file(self, path, commit, native_path=None):
        got = self.bind(path)
        native = Path(native_path or path).resolve().relative_to(self.repository).as_posix()
        require(self.tree(commit).get(native) == got["git_blob"], "Immutable Git blob differs: " + native)
        return dict(**got, commit=commit, repository_path=native)

    def source(self, commit):
        manifest = self.revision / "SOURCE_FREEZE120.json"
        files = [self.git_file(manifest, commit)]
        info = self.json(manifest)
        require("PROTOCOL120.md" in info["scientific_files"], "Frozen protocol absent")
        for name, expected in sorted(info["scientific_files"].items()):
            path = (self.revision / name).resolve()
            path.relative_to(self.revision)
            row = self.git_file(path, commit)
            require(row["sha256"] == expected, "Frozen source SHA differs: " + name)
            files.append(row)
        return dict(source_commit=commit, files=files, scientific_inputs=len(files)-1,
                    verification_scope="read-only post-execution source identity; no scientific import")

    def manifest(self, root, name, source, kind, commit=None):
        path = root / name
        info = self.json(path)
        require(info["source_commit"] == source and info["kind"] == kind,
                "Artifact manifest kind/source differs: " + str(path))
        seen = set()
        for row in info["files"]:
            require(row["path"] not in seen, "Duplicate manifest member")
            seen.add(row["path"])
            p = (root / row["path"]).resolve()
            p.relative_to(root.resolve())
            got = self.bind(p)
            require(all(got[key] == row[key] for key in ("bytes", "sha256", "git_blob")),
                    "Artifact manifest member differs: " + str(p))
            if commit:
                native = self.revision / p.relative_to(self.evidence)
                self.git_file(p, commit, native)
        if commit:
            self.git_file(path, commit, self.revision / path.resolve().relative_to(self.evidence))
        return info


def group(row):
    return row["index"], row["arm"], row["service"]


def rowkey(row):
    return row["index"], row["row"], row["arm"], row["service"]


def label(key):
    return str(key[0]) + "/" + key[1] + "/" + key[2]


def key_id(row):
    key = (tuple(row["state_hex"]), row["action_hex"], float(row["alpha"]).hex())
    return hashlib.sha256(json.dumps(key, separators=(",", ":")).encode()).hexdigest()


def mean(values):
    values = list(values)
    require(values, "Mean of empty selected sample is forbidden")
    return sum(map(exact, values), F(0)) / len(values)


def sqrt_up(value, bits=60):
    value = exact(value)
    require(value >= 0, "Negative squared bound")
    scale = 2**bits
    n = math.isqrt((value.numerator * scale * scale) // value.denominator)
    if F(n, scale)**2 < value:
        n += 1
    answer = F(n, scale)
    require(answer**2 >= value, "Exact upward square root")
    return answer


def sign(lo, hi):
    require(lo <= hi, "Empty reported interval")
    if lo == hi == 0:
        return "exact-zero"
    if hi < 0:
        return "strict-negative"
    if lo > 0:
        return "strict-positive"
    return "contains-zero"


def census(rows, n, population):
    mapping = {rowkey(row): row for row in rows}
    expected = {(i, j, a, s) for i in range(2) for j in range(n) for a in ARMS for s in SERVICES}
    require(len(mapping) == len(rows) == len(expected) and set(mapping) == expected,
            "Complete declared decision census required")
    for row in rows:
        require(exact(row["alpha"]) == LEVELS[row["index"]], "Risk identity differs")
        require(row["state_hex"] == [float(v).hex() for v in row["state"]], "State binary identity differs")
        require(row["action_hex"] == float(row["action"]).hex(), "Action binary identity differs")
        require(row["population_observation"] is population, "Population/timing scope differs")
        require(row["original_initial_state_batch_size"] == 1, "Row-local service required")
        require(row["qualified"] is True, "Unqualified returned policy")
    return mapping


def successful(inputs, path, source):
    receipt = inputs.json(path / "EXECUTION120.json")
    require(receipt.get("exit_code") == 0 and receipt.get("status") == "executed",
            "Actual exit-zero scientific receipt required: " + str(path))
    require(receipt["source"]["source_commit"] == source, "Executed source differs")
    return receipt


def validate_states(inputs, state_dir, primary, source, actor):
    data = inputs.json(state_dir / "states120.json")
    entropy = inputs.bytes(state_dir / "entropy120.bin")
    require(len(entropy) == 640 and hashlib.sha256(entropy).hexdigest() == data["entropy_sha256"],
            "Actual original entropy binding differs")
    require(len(data["states"]) == 64 and data["source_commit"] == source and data["actor_commit"] == actor,
            "State/source/actor custody differs")
    values = {}
    for j, row in enumerate(data["states"]):
        integers = [int.from_bytes(entropy[(2*j+k)*5:(2*j+k+1)*5], "big") for k in range(2)]
        x = [v / 2**40 for v in integers]
        require(row["row"] == j and row["coordinate_numerators"] == integers and row["denominator"] == 2**40,
                "The stored independent row differs from actual entropy bytes")
        require(row["state"] == x and row["state_hex"] == [v.hex() for v in x], "Exact dyadic state differs")
        values[j] = row["state_hex"]
    for row in primary.values():
        require(row["state_hex"] == values[row["row"]], "Method/risk did not use its declared common state")
    return dict(rows=64, entropy_bytes=640, distinct_states=len(set(map(tuple, values.values()))),
                duplicate_draws_are_preserved_as_separate_population_rows=True,
                source_commit=source, actor_commit=actor, entropy_sha256=data["entropy_sha256"])


def compare_independent(inputs, independent_dir, primary):
    comparisons = list(inputs.jsonl(independent_dir / "comparisons120.jsonl"))
    mapping = {rowkey(row): row for row in comparisons}
    require(len(mapping) == len(comparisons) == 4096 and set(mapping) == set(primary), "Full independent census required")
    policies = list(inputs.jsonl(independent_dir / "policies120.jsonl"))
    policy_map = {row["key_id"]: row for row in policies}
    expected_keys = {key_id(row) for row in primary.values()}
    require(len(policy_map) == len(policies) and set(policy_map) == expected_keys, "Every unique actual policy key is required")
    optima = list(inputs.jsonl(independent_dir / "original_optima120.jsonl"))
    optima_map = {(tuple(row["state_hex"]), row["alpha_hex"]): row for row in optima}
    calculated = {}
    for row in policies:
        require(row["key_id"] == key_id(row), "Independent policy key hash differs")
        require(row["bins"] == 64 and row["terminal_steps"] == 32 and row["terminal_contexts"] == 129,
                "Independent validation budget changed")
        lo, hi = exact(row["q_lower"]), exact(row["q_upper"])
        require(lo <= hi and exact(row["j_lower"]) == lo and exact(row["j_upper"]) == hi+BETA*EPS,
                "Exactly one unchanged-future allowance required")
        require(exact(row["future_controller_allowance_added_exactly_once"]) == BETA*EPS,
                "Future-controller allowance identity differs")
        sk = (tuple(row["state_hex"]), float(row["alpha"]).hex())
        bounds = exact(row["optimum_lower"]), hi
        old = calculated.get(sk)
        calculated[sk] = bounds if old is None else (max(old[0], bounds[0]), min(old[1], bounds[1]))
    require(set(calculated) == set(optima_map), "Independent original-optimum state census differs")
    for key, bounds in calculated.items():
        require(bounds == (exact(optima_map[key]["lower"]), exact(optima_map[key]["upper"])) and bounds[0] <= bounds[1],
                "All-action original-optimum aggregation differs")
    checks = Counter()
    diagnostic = []
    for key, row in primary.items():
        observed = mapping[key]
        policy = policy_map[key_id(row)]
        incrow = primary[(key[0], key[1], key[2], "completed")]
        inc = policy_map[key_id(incrow)]
        require(float(row["completed_incumbent_action"]).hex() == incrow["action_hex"], "Completed incumbent identity differs")
        require(observed["key_id"] == policy["key_id"] and observed["incumbent_key_id"] == inc["key_id"],
                "Independent comparison key differs")
        require(observed["action_hex"] == row["action_hex"] and observed["state_hex"] == row["state_hex"], "Independent row serialization differs")
        jl, ju = exact(policy["j_lower"]), exact(policy["j_upper"])
        pl, pu = exact(row["complete_policy_lower"]), exact(row["complete_policy_upper"])
        ol, ou = calculated[(tuple(row["state_hex"]), float(row["alpha"]).hex())]
        require(max(pl, jl) <= min(pu, ju), "Original-policy interval compatibility failure")
        require(exact(row["original_optimum_lower"]) <= ou, "Production original lower exceeds independent feasible upper")
        same = policy["key_id"] == inc["key_id"]
        gl = F(0) if same else max(F(0), exact(inc["j_lower"])-ju)
        gu = F(0) if same else min(TAU, exact(inc["j_upper"])-jl)
        require(0 <= gl <= gu <= TAU, "Safe original gain interval differs")
        certified = exact(row["certified_gain_lower"])
        require(0 <= certified <= gu, "Certified gain exceeds independent upper")
        cap = F(1, 8)+sum(map(exact, row["state"]))/16
        rl, ru = max(F(0), jl-ou), ju-ol
        expected = dict(j_lower=jl, j_upper=ju, original_optimum_lower=ol, original_optimum_upper=ou,
                        original_regret_lower=rl, original_regret_upper=ru,
                        squared_original_action_error_upper=min(cap**2, ru), gain_lower=gl, gain_upper=gu,
                        certified_gain_lower=certified)
        require(all(exact(observed[name]) == value for name, value in expected.items()), "Independent recorded value reaggregation differs")
        require(observed["same_action"] is same and 0 <= rl <= ru, "Independent action/regret identity differs")
        flags = dict(policy_intervals_overlap=True, independent_contains_production=jl <= pl <= pu <= ju,
                     production_contains_independent=pl <= jl <= ju <= pu,
                     original_optimum_feasibility_compatible=True, certified_gain_compatible=True)
        checks.update({key: int(value) for key, value in flags.items()})
        diagnostic.append(dict(index=key[0], row=key[1], arm=key[2], service=key[3],
                               key_id=policy["key_id"], production_width=pu-pl, independent_width=ju-jl, **flags))
    design = inputs.json(independent_dir / "INDEPENDENT_DESIGN120.json")
    require(design["unique_actions"] == len(policies) and design["expected_terminal_contexts"] == len(policies)*129,
            "Independent design/execution unique-key count differs")
    # The full trace is hash-bound; this reporter reaggregates its retained
    # policy enclosures, not the original primitive calculations.
    trace = inputs.bind(independent_dir / "terminal_witnesses120.jsonl.gz")
    return mapping, policies, diagnostic, dict(**checks, primary_rows=4096, unique_policy_keys=len(policies),
        independent_terminal_contexts=len(policies)*129, primitive_trace_identity=trace,
        validation_only_seconds=sum(exact(row["seconds"]) for row in policies),
        scope="finite enclosure compatibility and exact record reaggregation; no primitive or certificate proof rerun")


@lru_cache(maxsize=None)
def binomial_at_most(p, k):
    c, d = p.numerator, p.denominator
    numerator = sum(math.comb(N, j) * c**j * (d-c)**(N-j) for j in range(k, N+1))
    return numerator * EVENT_DELTA.denominator <= EVENT_DELTA.numerator * d**N


def population(inputs, stats_dir, primary, independent):
    rows = list(inputs.jsonl(stats_dir / "POPULATION_GROUPS120.jsonl"))
    mapping = {group(row): row for row in rows}
    expected = {key for key in GROUPS if key[2] != "completed"}
    require(len(mapping) == len(rows) == 48 and set(mapping) == expected, "Full population group census required")
    thresholds = []
    for key in (value for value in GROUPS if value in expected):
        row = mapping[key]
        ids = [(key[0], j, key[1], key[2]) for j in range(N)]
        gl = mean(independent[k]["gain_lower"] for k in ids)
        gu = mean(independent[k]["gain_upper"] for k in ids)
        require(row["independent_units"] == 64 and row["missing_independent_rows"] == [], "All independent population rows required")
        require(exact(row["alpha"]) == LEVELS[key[0]], "Population risk identity differs")
        events = row["positive_threshold_events"]
        require(len(events) == 4 and tuple(exact(e["threshold"]) for e in events) == THRESHOLDS,
                "The fixed threshold family changed")
        stair, previous = F(0), F(0)
        for event in events:
            threshold = exact(event["threshold"])
            count = sum(exact(independent[k]["gain_lower"]) >= threshold for k in ids)
            lo, hi = exact(event["lower"]), exact(event["inversion_upper"])
            require(count == event["successes"] and 0 <= lo <= hi <= 1, "Exact event census differs")
            if count == 0:
                require(lo == hi == 0 and event["exact_bisections"] == 0, "Zero-event interval differs")
            else:
                require(event["exact_bisections"] == 48 and hi-lo == F(1, 2**48), "CP bracket resolution differs")
                require(binomial_at_most(lo, count) and not binomial_at_most(hi, count), "Exact binomial bracket failed")
            stair += (threshold-previous)*lo
            previous = threshold
            thresholds.append(dict(index=key[0], alpha=LEVELS[key[0]], arm=key[1], service=key[2],
                threshold=threshold, successes=count, independent_units=64, event_probability_lower=lo,
                inversion_upper=hi, exact_bracket_verified=True, per_event_failure=EVENT_DELTA))
        hl, hu = max(F(0), gl-RADIUS), min(TAU, gu+RADIUS)
        check = dict(sample_mean_gain_lower=gl, sample_mean_gain_upper=gu,
                     hoeffding_population_mean_lower=hl, hoeffding_population_mean_upper=hu,
                     population_mean_staircase_lower=stair,
                     simultaneous_population_mean_lower=max(hl, stair), simultaneous_population_mean_upper=hu)
        require(all(exact(row[name]) == value for name, value in check.items()), "Frozen population aggregation differs")
        require(row["accepted_steps"] == sum(primary[k]["accepted_steps"] for k in ids), "Population accepted-step total differs")
        require(row["changed_state_actions"] == sum(primary[k]["action_hex"] != float(primary[k]["completed_incumbent_action"]).hex() for k in ids),
                "Population action-change total differs")
    execution = inputs.json(stats_dir / "EXECUTION120.json")
    require(exact(execution["global_simultaneous_coverage_at_least"]) == F(19, 20) and execution["complete_independent_validation"] is True,
            "Population coverage/completeness receipt differs")
    exponent = 2*N*(RADIUS/TAU)**2
    taylor = sum(exponent**j/math.factorial(j) for j in range(21))
    require(exponent == F(1089, 128) and taylor > 3840, "Exact fixed Hoeffding radius certificate")
    certificate = execution["radius_certificate"]
    require(exact(certificate["exact_radius"]) == RADIUS and exact(certificate["exact_exponential_lower_bound"]) == taylor,
            "Recorded exact radius certificate differs")
    require(48*4*EVENT_DELTA+48*F(1, 1920) == F(1, 20), "Fixed simultaneous family allocation")
    return mapping, thresholds


def acquisition(inputs, root):
    records, models = {}, {}
    for index in range(2):
        labels = inputs.json(root / f"labels-{index}.json")
        require(labels["index"] == index and exact(labels["alpha"]) == LEVELS[index] and len(labels["state"]) == 256,
                "Fixed common training-label catalogue differs")
        # Inspect every recorded fit attempt; do not rerun fitting or audits.
        fit_events = list(inputs.jsonl(root / f"fit-events-{index}.jsonl"))
        require(fit_events and fit_events[0]["event"] == "all-fits-start" and fit_events[-1]["event"] == "all-fits-complete",
                "Complete actual fitting-event boundary required")
        for arm in ARMS:
            folder = root / "models" / f"{index}-{arm}"
            model = inputs.json(folder / "model.json")
            row = inputs.json(folder / "acquisition.json")
            require(row["index"] == index and row["arm"] == arm and row["model_sha256"] == inputs.bind(folder / "model.json")["sha256"],
                    "Model/acquisition identity differs")
            require(row["model_bytes"] == (folder / "model.json").stat().st_size, "Model byte count differs")
            require(row["original_label_sites"] == (0 if arm == "online" else 256), "Standalone information allocation differs")
            if arm != "online":
                require(row["original_label_querycounts_if_standalone"] == labels["querycounts"], "A learned representation lacks the same complete label charge")
            models[index, arm] = model
            records[index, arm] = row
    identical = []
    for index in range(2):
        equal = models[index, "relu"]["parameters"] == models[index, "hinge"]["parameters"]
        require(equal, "Inherited ReLU/hinge feature and coefficient identity differs")
        rr, hr = records[index, "relu"], records[index, "hinge"]
        require(rr["standalone_fit_component_seconds"] == hr["standalone_fit_component_seconds"] and
                rr["standalone_fit_audit_component_seconds"] == hr["standalone_fit_audit_component_seconds"],
                "The conventional hinge lacks its full neural feature-acquisition charge")
        identical.append(dict(index=index, parameters_equal=equal,
                              relu_model_sha256=rr["model_sha256"], hinge_model_sha256=hr["model_sha256"],
                              hinge_fully_charged_for_parent_fit_and_audit=True))
    return records, identical


def trial_summary(trials):
    candidates = {(row["row"], row["trial"]) for row in trials}
    levels = [row for row in trials if "m" in row]
    legacy = [row for row in trials if "m" not in row and not row.get("no_new_density_or_point_query", False)]
    unqualified = sum(not row["qualified"] for row in levels)
    unqualified += sum(exact(row["candidate_loss"]) > TAU or exact(row["candidate_width"]) > WIDTH for row in legacy)
    return dict(candidate_attempts=len(candidates), recorded_trial_rows=len(trials), precision_attempts=len(levels),
        identical_action_shortcuts=sum(row.get("no_new_density_or_point_query", False) for row in trials),
        accepted_candidate_steps=sum(row["accepted"] for row in trials),
        unqualified_candidate_levels=unqualified,
        certified_nonimprovement_levels=sum(row.get("certified_not_better", False) for row in levels),
        budget_exhausted_candidates=sum(row.get("exhausted", False) for row in levels),
        rejected_candidate_attempts=len(candidates)-sum(row["accepted"] for row in trials),
        legacy_candidate_attempts=len(legacy),
        paired_lower_active_levels=sum(row.get("paired_lower_active", False) for row in levels),
        paired_upper_active_levels=sum(row.get("paired_upper_active", False) for row in levels),
        incumbent_tail_transfer_active_levels=sum(row.get("incumbent_tail_transfer_active", False) for row in levels),
        resolution_histogram=dict(sorted(Counter(str(row["m"]) for row in levels).items())))


def read_batches(inputs, root, primary, n, acq):
    catalogue = inputs.json(root / "CATALOGUE120.json")
    require(catalogue["decisions"] == 64*n and catalogue["singleton_decision_calls"] == 64*n,
            "Catalogue census differs")
    information = {group(row): row for row in catalogue["records"]}
    require(set(information) == set(GROUPS) and len(catalogue["records"]) == 64, "Every cohort must be retained")
    alltrials = list(inputs.jsonl(root / "trials120.jsonl"))
    bytrial = defaultdict(list)
    for row in alltrials:
        require(group(row) in GROUPS and 0 <= row["row"] < n, "Trial outside declared cohort")
        bytrial[group(row)].append(row)
    batches = {}
    for key in GROUPS:
        path = root / "batches" / f"{key[0]}-{key[1]}-{key[2]}.json"
        row = inputs.json(path)
        require(group(row) == key and row["original_initial_state_batch_size"] == 1, "Batch identity differs")
        expected_rows = [primary[(key[0], j, key[1], key[2])] for j in range(n)]
        require(row["rows"] == expected_rows and row["trials"] == bytrial[key], "Batch/JSONL copies differ")
        counts = Counter()
        for item in expected_rows:
            counts.update(item["querycounts"])
        require(dict(counts) == row["counts"] == information[key]["querycounts"], "Paid operation-count aggregation differs")
        require(row["seconds"] == sum(item["seconds"] for item in expected_rows), "Singleton clock aggregation differs")
        require(inputs.bind(path)["sha256"] == information[key]["batch_sha256"], "Catalogue batch binding differs")
        eventpath = root / "events" / (row["batch_id"] + ".jsonl.gz")
        require(inputs.bind(eventpath)["sha256"] == row["event_trace_sha256"], "Full original event trace binding differs")
        acquisition_charge = acq[key[0], key[1]]["actual_standalone_acquisition_charge_seconds"]
        require(row["standalone_acquisition_charge_seconds"] == acquisition_charge and
                all(item["standalone_acquisition_charge_seconds"] == acquisition_charge for item in expected_rows),
                "Standalone acquisition charge differs across cohort records")
        require(row["cohort_end_to_end_seconds"] >= row["seconds"] and row["cohort_end_to_end_seconds"] >= row["cold_model_load_seconds"],
                "Cohort clock cannot exclude its contained work")
        row["trial_summary_reporting"] = trial_summary(bytrial[key])
        batches[key] = row
    return batches, alltrials, catalogue


def group_rows(primary, independent, batches, acq):
    rows = []
    for key in GROUPS:
        ids = [(key[0], j, key[1], key[2]) for j in range(N)]
        pp, ii = [primary[k] for k in ids], [independent[k] for k in ids]
        batch, acquisition_row = batches[key], acq[key[0], key[1]]
        accepted = sum(row["accepted_steps"] for row in pp)
        require(accepted == batch["trial_summary_reporting"]["accepted_candidate_steps"], "Accepted primary/trial counts differ")
        maxsq = max(exact(row["squared_original_action_error_upper"]) for row in ii)
        msq = mean(row["squared_original_action_error_upper"] for row in ii)
        A = exact(acquisition_row["actual_standalone_acquisition_charge_seconds"])
        T = exact(batch["cohort_end_to_end_seconds"])
        S = exact(batch["seconds"])
        L = exact(batch["cold_model_load_seconds"])
        W = exact(batch["decision_row_trial_recording_seconds"])
        rows.append(dict(index=key[0], alpha=LEVELS[key[0]], arm=key[1], service=key[2], independent_units=64,
            original_j_mean_lower=mean(row["j_lower"] for row in ii),
            original_j_mean_upper=mean(row["j_upper"] for row in ii),
            original_regret_mean_lower=mean(row["original_regret_lower"] for row in ii),
            original_regret_mean_upper=mean(row["original_regret_upper"] for row in ii),
            original_regret_maximum_upper=max(exact(row["original_regret_upper"]) for row in ii),
            squared_original_action_error_mean_upper=msq, squared_original_action_error_maximum_upper=maxsq,
            original_action_rms_error_upper=sqrt_up(msq), original_action_maximum_error_upper=sqrt_up(maxsq),
            mean_individual_original_action_distance_upper=mean(sqrt_up(row["squared_original_action_error_upper"]) for row in ii),
            own_incumbent_gain_mean_lower=mean(row["gain_lower"] for row in ii),
            own_incumbent_gain_mean_upper=mean(row["gain_upper"] for row in ii),
            original_certified_gain_mean_lower=mean(row["certified_gain_lower"] for row in pp),
            changed_state_actions=sum(row["action_hex"] != float(row["completed_incumbent_action"]).hex() for row in pp),
            accepted_steps=accepted, first_actor_rejections=sum(bool(row["first_rejected"]) for row in pp),
            completed_exact_fallback_entries=sum(bool(row["completed_incumbent_exact_fallback"]) for row in pp),
            final_tail_certificates=sum(row["final_certificate_kind"] == "paired-tail" for row in pp),
            final_resolution_histogram=dict(sorted(Counter(str(row["final_certificate_resolution"]) for row in pp).items())),
            standalone_acquisition_charge_seconds=A, cohort64_seconds=T, singleton_service_sum_seconds=S,
            cold_load_seconds=L, decision_trial_recording_seconds=W,
            cohort_remaining_overhead_seconds=T-S-L-W,
            event_serialization_seconds=exact(batch["event_serialization_seconds"]),
            event_serialization_is_overlapping_not_an_additive_component=True,
            complete_observed64_total_seconds=A+T, complete_observed64_per_call_seconds=(A+T)/64,
            standalone_label_sites=acquisition_row["original_label_sites"], model_payload_bytes=acquisition_row["model_bytes"],
            querycounts=dict(batch["counts"]), label_querycounts_if_standalone=acquisition_row["original_label_querycounts_if_standalone"],
            **batch["trial_summary_reporting"]))
    return rows


def all_contrasts(primary, independent):
    rows, lookup = [], {}
    for risk in range(2):
        keys = [key for key in GROUPS if key[0] == risk]
        for a, b in itertools.combinations(keys, 2):
            lo, hi, identical, disagreement = F(0), F(0), 0, F(0)
            for j in range(N):
                ka, kb = (risk, j, a[1], a[2]), (risk, j, b[1], b[2])
                aa, bb = independent[ka], independent[kb]
                if aa["key_id"] == bb["key_id"]:
                    identical += 1
                else:
                    lo += exact(aa["j_lower"])-exact(bb["j_upper"])
                    hi += exact(aa["j_upper"])-exact(bb["j_lower"])
                disagreement += abs(exact(primary[ka]["action"])-exact(primary[kb]["action"]))
            lo, hi = lo/N, hi/N
            row = dict(index=risk, alpha=LEVELS[risk], a_arm=a[1], a_service=a[2], b_arm=b[1], b_service=b[2],
                mean_original_j_a_minus_b_lower=lo, mean_original_j_a_minus_b_upper=hi,
                mean_original_regret_a_minus_b_lower=lo, mean_original_regret_a_minus_b_upper=hi,
                sign=sign(lo, hi), identical_policy_rows=identical, changed_policy_rows=N-identical,
                mean_absolute_action_disagreement=disagreement/N,
                disagreement_is_not_error_to_the_optimal_action=True,
                within_arm_service_contrast=a[1] == b[1], same_service_arm_contrast=a[2] == b[2],
                population_confidence_claim=False)
            rows.append(row)
            lookup[a, b] = lo, hi
            lookup[b, a] = -hi, -lo
        for a in keys:
            lookup[a, a] = F(0), F(0)
    require(len(rows) == 992 and sum(row["within_arm_service_contrast"] for row in rows) == 96 and
            sum(row["same_service_arm_contrast"] for row in rows) == 224, "Full comparison-family census")
    return rows, lookup


def timing(inputs, root, primary, acq):
    clocks, matches, batches, executions = [], [], {}, []
    receipt = inputs.json(root / "TIMING120.json")
    require(receipt["status"] == "executed" and len(receipt["repeats"]) == 3, "Every declared timing process is required")
    for repeat in range(3):
        folder = root / "timing" / f"attempt-{repeat:02d}"
        execution = successful(inputs, folder, next(iter(primary.values()))["source_commit"])
        executions.append(execution)
        launcher = inputs.json(root / "timing" / f"launcher-{repeat:02d}.json")
        require(launcher == receipt["repeats"][repeat] and launcher["repeat"] == repeat and launcher["exit_code"] == 0,
                "Timing launcher identity/return differs")
        require(inputs.bind(root / "timing" / f"launcher-{repeat:02d}.log")["sha256"] == launcher["log_sha256"], "Timing log differs")
        records = census(list(inputs.jsonl(folder / "records120.jsonl")), TIMING_N, False)
        these, _, catalogue = read_batches(inputs, folder, records, TIMING_N, acq)
        batches[repeat] = these
        for key, row in records.items():
            ref = primary[key]
            require(row["repeat"] == repeat and row["state_hex"] == ref["state_hex"], "Timing subset/repetition identity differs")
            for name in ("source_commit", "actor_commit", "state_commit", "model_sha256"):
                require(row[name] == ref[name], "Timing scientific input differs")
            matches.append(dict(repeat=repeat, index=key[0], row=key[1], arm=key[2], service=key[3],
                action_hex=row["action_hex"], primary_action_hex=ref["action_hex"],
                action_equal=row["action_hex"] == ref["action_hex"], state_equal=True,
                complete_policy_interval_equal=(row["complete_policy_lower"], row["complete_policy_upper"]) ==
                                              (ref["complete_policy_lower"], ref["complete_policy_upper"]),
                querycounts_equal=row["querycounts"] == ref["querycounts"]))
        for key in GROUPS:
            item = these[key]
            base = these[key[0], key[1], "completed"]
            cost, costbase = exact(item["cohort_end_to_end_seconds"]), exact(base["cohort_end_to_end_seconds"])
            A = exact(acq[key[0], key[1]]["actual_standalone_acquisition_charge_seconds"])
            clocks.append(dict(repeat=repeat, index=key[0], alpha=LEVELS[key[0]], arm=key[1], service=key[2], rows=32,
                cohort_seconds=cost, singleton_sum_seconds=exact(item["seconds"]), cold_load_seconds=exact(item["cold_model_load_seconds"]),
                decision_trial_recording_seconds=exact(item["decision_row_trial_recording_seconds"]),
                complete_observed32_total_seconds=A+cost,
                cohort_ratio_to_own_completed=cost/costbase,
                complete_observed32_ratio_to_own_completed=(A+cost)/(A+costbase),
                global_timing_process_max_rss_kib=execution.get("max_rss_kib"),
                rss_is_not_per_method_memory=True, querycounts=item["counts"],
                timing_cohort_order_rule=catalogue["timing_order_rule"]))
    require(len(matches) == 6144 and len(clocks) == 192, "Full timing action/clock census")
    summaries = []
    for key in GROUPS:
        members = [row for row in clocks if group(row) == key]
        fields = ("cohort_seconds", "complete_observed32_total_seconds", "cohort_ratio_to_own_completed", "complete_observed32_ratio_to_own_completed")
        row = dict(index=key[0], arm=key[1], service=key[2], repeats=3, population_timing_confidence_claim=False)
        for field in fields:
            values = [item[field] for item in members]
            row[field + "_median"] = statistics.median(values)
            row[field + "_minimum"] = min(values)
            row[field + "_maximum"] = max(values)
        summaries.append(row)
    return clocks, matches, batches, summaries, executions


def singleton(value):
    while isinstance(value, list):
        require(len(value) == 1, "Row-local scalar expected in paired record")
        value = value[0]
    return value


def paired_events(inputs, root, batches, primary):
    records, groups = [], []
    for key in GROUPS:
        batch = batches[key]
        eventpath = root / "events" / (batch["batch_id"] + ".jsonl.gz")
        counts = Counter()
        density = payload = proposal = None
        last_row = None
        seen = 0
        for event in inputs.jsonl(eventpath):
            require(event["sequence"] == seen, "Paid event sequence is torn")
            seen += 1
            name = event["event"]
            rowindex = event.get("initial_state_row")
            if rowindex is not None and rowindex != last_row:
                density = payload = proposal = None
                last_row = rowindex
            if name == "improvement-proposal-start":
                proposal = event["trial"]
            elif name == "tail-density-complete":
                density = event["density"]
                counts["density_pairs"] += 1
                counts["transfer_active_density_pairs"] += bool(singleton(density["incumbent_transfer_active"]))
            elif name == "paired-payload-complete":
                payload = event["result"]
                counts["paid_terminal_rows"] += payload["purchased_terminal_rows"]
                counts["paid_paired_compiler_calls"] += 1
            elif name == "paired-trial-resolution":
                require(density is not None and payload is not None and proposal == event["trial"], "Paired event dependencies are absent")
                require(payload["m"] == event["m"] and rowindex is not None, "Paired event resolution/outer row differs")
                require(singleton(payload["difference_lower"]) == event["difference_lower"] and
                        singleton(payload["difference_upper"]) == event["difference_upper"], "Paid payload/decision bounds differ")
                a, b = exact(event["incumbent_action"]), exact(event["candidate_action"])
                # Exact arithmetic on recorded action values only. No original
                # continuation, risk distribution or primitive is re-evaluated.
                action_cost_difference = (b-a)*(b+a)*(1+4*(b*b+a*a))
                convex_upper = action_cost_difference+BETA*(exact(singleton(payload["convex_integral_upper"]))+
                    exact(singleton(density["kappa"]))+EPS)
                direct_lower = action_cost_difference+BETA*(exact(singleton(payload["integral_lower"]))-
                    exact(singleton(density["incumbent_direct_kappa"]))-EPS)
                mixed_needed = bool(event["accepted"] and convex_upper >= 0)
                transfer_needed = bool(event["certified_not_better"] and direct_lower < 0)
                counts["precision_levels"] += 1
                counts["accepted_steps"] += bool(event["accepted"])
                counts["accepted_levels_needing_mixed_upper"] += mixed_needed
                counts["rejected_levels_needing_transfer_lower"] += transfer_needed
                counts["paired_upper_active_levels"] += bool(event["paired_upper_active"])
                counts["paired_lower_active_levels"] += bool(event["paired_lower_active"])
                records.append(dict(index=key[0], arm=key[1], service=key[2], row=rowindex, trial=event["trial"], m=event["m"],
                    incumbent_action_hex=float(a).hex(), candidate_action_hex=float(b).hex(),
                    difference_lower=exact(event["difference_lower"]), difference_upper=exact(event["difference_upper"]),
                    accepted=event["accepted"], qualified=event["qualified"], certified_not_better=event["certified_not_better"],
                    exhausted=event["exhausted"], paired_upper_active=event["paired_upper_active"], paired_lower_active=event["paired_lower_active"],
                    convex_only_exact_scalar_upper=convex_upper, accepted_needs_mixed_upper_at_recorded_resolution=mixed_needed,
                    without_transfer_exact_scalar_lower=direct_lower, rejection_needs_transfer_at_recorded_resolution=transfer_needed,
                    counterfactual_later_refinement_or_timing_claim=False,
                    candidate_tail_slack=exact(singleton(density["kappa"])),
                    incumbent_direct_tail_slack=exact(singleton(density["incumbent_direct_kappa"])),
                    incumbent_transferred_tail_slack=exact(singleton(density["incumbent_transferred_kappa"])),
                    incumbent_used_tail_slack=exact(singleton(density["incumbent_kappa"])),
                    action_modulus_upper=exact(singleton(payload["action_modulus_upper"])),
                    midpoint_error_upper=exact(singleton(payload["midpoint_error_upper"])),
                    purchased_terminal_rows=payload["purchased_terminal_rows"]))
        require(seen == batch["event_records"], "Recorded event count differs")
        if key[2] in ("paired", "direct-refine"):
            paid = batch["counts"]
            require(counts["paid_terminal_rows"] == paid.get("r120_paired_terminal_rows", 0), "Paired terminal payload count differs")
            require(counts["paid_paired_compiler_calls"] == paid.get("r120_paired_compiler_calls", 0), "Paired compiler call count differs")
            require(counts["density_pairs"] == paid.get("r120_tail_transfer_bounds", 0), "Paid transfer count differs")
            require(counts["accepted_steps"] == sum(primary[key[0], j, key[1], key[2]]["accepted_steps"] for j in range(N)),
                    "Event versus primary accepted-step count differs")
        groups.append(dict(index=key[0], arm=key[1], service=key[2], event_records=seen, **counts,
            paid_integer_sqrt_calls=batch["counts"].get("r120_tail_transfer_integer_sqrt_calls", 0),
            scope="diagnostic use at recorded resolution; no measured counterfactual or economic primitive rerun"))
    return records, groups


def domain_empty():
    return dict(empty=True, lower=None, lower_closed=False, upper=None, upper_closed=False)


def domain_all():
    return dict(empty=False, lower=F(0), lower_closed=True, upper=None, upper_closed=False)


def positive_domain(gain, extra_seconds):
    """Exactly solve gain - lambda*extra_seconds > 0 for lambda >= 0."""
    gain, extra_seconds = exact(gain), exact(extra_seconds)
    if extra_seconds == 0:
        return domain_all() if gain > 0 else domain_empty()
    threshold = gain/extra_seconds
    if extra_seconds > 0:
        if threshold <= 0:
            return domain_empty()
        return dict(empty=False, lower=F(0), lower_closed=True, upper=threshold, upper_closed=False)
    if threshold < 0:
        return domain_all()
    return dict(empty=False, lower=threshold, lower_closed=False, upper=None, upper_closed=False)


def intersect_domains(a, b):
    if a["empty"] or b["empty"]:
        return domain_empty()
    low = max(a["lower"], b["lower"])
    lc = (a["lower"] < low or a["lower_closed"]) and (b["lower"] < low or b["lower_closed"])
    finite = [x["upper"] for x in (a, b) if x["upper"] is not None]
    high = min(finite) if finite else None
    hc = high is not None and all(x["upper"] is None or x["upper"] > high or x["upper_closed"] for x in (a, b))
    if high is not None and (low > high or (low == high and not (lc and hc))):
        return domain_empty()
    return dict(empty=False, lower=low, lower_closed=lc, upper=high, upper_closed=hc)


def scenario_cost(acq, batches, key, volume, repeat):
    A = exact(acq[key[0], key[1]]["actual_standalone_acquisition_charge_seconds"])
    row = batches[repeat][key]
    T, L = exact(row["cohort_end_to_end_seconds"]), exact(row["cold_model_load_seconds"])
    require(T >= L, "Invalid operating/load cost decomposition")
    return (A+L)/volume+(T-L)/32


def price_scenarios(acq, timing_batches, group_map, contrast_lookup, action_checks):
    rows = []
    costs = []
    action_binding = {(repeat, key): all(row["action_equal"] and row["state_equal"] for row in action_checks
                       if row["repeat"] == repeat and group(row) == key)
                      for repeat in range(3) for key in GROUPS}
    for key in GROUPS:
        for volume in VOLUMES:
            own_domains, menu_domains = [], []
            for repeat in range(3):
                own = (key[0], key[1], "completed")
                C = scenario_cost(acq, timing_batches, key, volume, repeat)
                costs.append(dict(index=key[0], arm=key[1], service=key[2], volume=volume, repeat=repeat,
                    seconds_per_decision_scenario=C, measured_workload=32,
                    amortization_is_not_measured_scaling=True,
                    production_acquisition_and_every_candidate_certificate_charged=True,
                    separate_research_independent_validation_excluded_from_deployment_scenario=True))
                if key[2] != "completed":
                    dc = C-scenario_cost(acq, timing_batches, own, volume, repeat)
                    source = group_map[key]
                    gl, gu = source["own_incumbent_gain_mean_lower"], source["own_incumbent_gain_mean_upper"]
                    sufficient, possible = positive_domain(gl, dc), positive_domain(gu, dc)
                    row = dict(index=key[0], arm=key[1], service=key[2], comparator="own-completed", volume=volume,
                        repeat=repeat, mean_original_gain_lower=gl, mean_original_gain_upper=gu,
                        extra_seconds_per_decision=dc, sufficient_positive_benefit_prices=sufficient,
                        not_ruled_out_positive_benefit_prices=possible, comparisons=1,
                        timing_action_binding_verified=action_binding[repeat, key] and action_binding[repeat, own],
                        domains_conditional_on_verified_action_binding=True,
                        population_adoption_claim=False)
                    rows.append(row)
                    own_domains.append(row)
                conventional = [other for other in GROUPS if other[0] == key[0] and other[1] != "relu" and other != key]
                sufficient, possible = domain_all(), domain_all()
                active_lower, active_upper = [], []
                for other in conventional:
                    dl, du = contrast_lookup[key, other]
                    dc = C-scenario_cost(acq, timing_batches, other, volume, repeat)
                    gldomain, gudomain = positive_domain(-du, dc), positive_domain(-dl, dc)
                    newlow, newup = intersect_domains(sufficient, gldomain), intersect_domains(possible, gudomain)
                    if newlow != sufficient:
                        active_lower.append(label(other))
                    if newup != possible:
                        active_upper.append(label(other))
                    sufficient, possible = newlow, newup
                row = dict(index=key[0], arm=key[1], service=key[2], comparator="every-conventional-menu-alternative", volume=volume,
                    repeat=repeat, sufficient_positive_benefit_prices=sufficient, not_ruled_out_positive_benefit_prices=possible,
                    comparisons=len(conventional), menu=[label(other) for other in conventional],
                    constraints_tightening_lower_domain_in_fixed_order=active_lower,
                    constraints_tightening_upper_domain_in_fixed_order=active_upper,
                    upper_intersection_is_pairwise_not_ruled_out_not_joint_existence=True,
                    timing_action_binding_verified=action_binding[repeat, key] and all(action_binding[repeat, other] for other in conventional),
                    domains_conditional_on_verified_action_binding=True,
                    population_adoption_claim=False)
                rows.append(row)
                menu_domains.append(row)
            for name, entries in (("own-completed", own_domains), ("every-conventional-menu-alternative", menu_domains)):
                if entries:
                    sufficient, possible = domain_all(), domain_all()
                    for entry in entries:
                        sufficient = intersect_domains(sufficient, entry["sufficient_positive_benefit_prices"])
                        possible = intersect_domains(possible, entry["not_ruled_out_positive_benefit_prices"])
                    rows.append(dict(index=key[0], arm=key[1], service=key[2], comparator=name, volume=volume,
                        repeat="intersection-all-three", sufficient_positive_benefit_prices=sufficient,
                        not_ruled_out_positive_benefit_prices=possible, comparisons=sum(e["comparisons"] for e in entries),
                        robustness_scope="all three recorded timing scenarios; not timing confidence",
                        timing_action_binding_verified=all(entry["timing_action_binding_verified"] for entry in entries),
                        domains_conditional_on_verified_action_binding=True,
                        population_adoption_claim=False))
    require(len(costs) == 768 and len(rows) == 1792, "Full fixed price-scenario census")
    # The observed primary workload supplies a distinct non-extrapolated cost
    # comparison. It is not replaced by any favorable amortization volume.
    for key in GROUPS:
        C = group_map[key]["complete_observed64_per_call_seconds"]
        own = (key[0], key[1], "completed")
        if key[2] != "completed":
            source = group_map[key]
            gl, gu = source["own_incumbent_gain_mean_lower"], source["own_incumbent_gain_mean_upper"]
            dc = C-group_map[own]["complete_observed64_per_call_seconds"]
            rows.append(dict(index=key[0], arm=key[1], service=key[2], comparator="own-completed", volume=64,
                repeat="actual-primary64", mean_original_gain_lower=gl, mean_original_gain_upper=gu,
                extra_seconds_per_decision=dc, sufficient_positive_benefit_prices=positive_domain(gl, dc),
                not_ruled_out_positive_benefit_prices=positive_domain(gu, dc), comparisons=1,
                timing_action_binding_verified=True, actual_same_64_decisions_with_their_own_cost=True,
                population_adoption_claim=False))
        conventional = [other for other in GROUPS if other[0] == key[0] and other[1] != "relu" and other != key]
        sufficient, possible = domain_all(), domain_all()
        for other in conventional:
            dl, du = contrast_lookup[key, other]
            dc = C-group_map[other]["complete_observed64_per_call_seconds"]
            sufficient = intersect_domains(sufficient, positive_domain(-du, dc))
            possible = intersect_domains(possible, positive_domain(-dl, dc))
        rows.append(dict(index=key[0], arm=key[1], service=key[2], comparator="every-conventional-menu-alternative", volume=64,
            repeat="actual-primary64", sufficient_positive_benefit_prices=sufficient, not_ruled_out_positive_benefit_prices=possible,
            comparisons=len(conventional), menu=[label(other) for other in conventional],
            timing_action_binding_verified=True, actual_same_64_decisions_with_their_own_cost=True,
            upper_intersection_is_pairwise_not_ruled_out_not_joint_existence=True, population_adoption_claim=False))
    require(len(rows) == 1904, "All 112 actual-primary cost domains must also remain")
    return rows, costs


def frontiers(group_map, contrast_lookup):
    """Unresolved interval comparisons stay; membership proves no true optimum."""
    axes = ("terminal_original_risk_queries", "compiled_terminal_rows", "risk_sort_items")
    records = []
    for risk in range(2):
        keys = [key for key in GROUPS if key[0] == risk]
        for kind in ("complete_observed64_cost_and_original_J", "recorded_resource_vector_and_original_J"):
            def resources(key):
                row = group_map[key]
                if kind.startswith("complete"):
                    return dict(complete_observed64_total_seconds=row["complete_observed64_total_seconds"])
                result = {"standalone_label_sites": row["standalone_label_sites"], "model_payload_bytes": row["model_payload_bytes"]}
                for axis in axes:
                    result["decision_"+axis] = row["querycounts"].get(axis, 0)
                    result["standalone_label_"+axis] = row["label_querycounts_if_standalone"].get(axis, 0)
                return result
            for candidate in keys:
                rc = resources(candidate)
                dominators = []
                for other in keys:
                    if other == candidate:
                        continue
                    ro = resources(other)
                    _, j_upper = contrast_lookup[other, candidate]
                    if all(ro[k] <= rc[k] for k in rc) and j_upper <= 0 and (j_upper < 0 or any(ro[k] < rc[k] for k in rc)):
                        dominators.append(label(other))
                records.append(dict(index=risk, arm=candidate[1], service=candidate[2], frontier=kind,
                    interval_nondominated=not dominators, certified_recorded_dominators=dominators, resources=rc,
                    no_population_or_true_pareto_optimality_claim=True,
                    distinct_overlapping_counter_dimensions_never_summed=True))
    require(len(records) == 128, "Full frontier census")
    return records


def interval_union(intervals):
    intervals = sorted(intervals)
    result = []
    for low, high in intervals:
        require(low <= high, "Invalid execution wall interval")
        if result and low <= result[-1][1]:
            result[-1][1] = max(result[-1][1], high)
        else:
            result.append([low, high])
    return result, sum(high-low for low, high in result)


def research_ledger(inputs, selected, extra):
    """Retain all supplied attempts; distinguish nested clocks from total work."""
    paths = set()
    for root in selected:
        for path in root.rglob("*"):
            if path.is_file() and (path.name in ("EXECUTION120.json", "FAILED120.jsonl", "ERRORS120.jsonl") or
                                   path.name.startswith("launcher-") and path.suffix == ".json"):
                paths.add(path.resolve())
    for path in extra:
        if path.is_dir():
            paths.update(p.resolve() for p in path.rglob("*.json") if p.is_file())
            paths.update(p.resolve() for p in path.rglob("*FAILED*.jsonl") if p.is_file())
        else:
            paths.add(path.resolve())
    rows, intervals = [], []
    for path in sorted(paths):
        data = list(inputs.jsonl(path)) if path.suffix == ".jsonl" else [inputs.json(path)]
        for ordinal, item in enumerate(data):
            # The original receipt is retained intact. Some metadata receipts
            # have no compatible wall interval and are not assigned zero cost.
            start = item.get("started_unix", item.get("start_unix", item.get("started_at_unix")))
            end = item.get("ended_unix", item.get("end_unix", item.get("ended_at_unix")))
            elapsed = item.get("total_seconds", item.get("elapsed_seconds", item.get("elapsed")))
            if start is None and isinstance(item.get("started_utc"), str):
                start = dt.datetime.fromisoformat(item["started_utc"].replace("Z", "+00:00")).timestamp()
            if end is None and isinstance(item.get("ended_utc"), str):
                end = dt.datetime.fromisoformat(item["ended_utc"].replace("Z", "+00:00")).timestamp()
            if "stdout_sha256" in item:
                log = path.parent / "stdout.log"
                require(inputs.bind(log)["sha256"] == item["stdout_sha256"], "External launcher output log binding differs")
            if isinstance(start, (float, int)) and isinstance(end, (float, int)):
                require(end >= start, "Execution wall timestamps run backwards")
                intervals.append((exact(start), exact(end)))
            else:
                start = end = None
            rows.append(dict(path=str(path), receipt_row=ordinal, sha256=inputs.bind(path)["sha256"],
                status=item.get("status", "receipt"), exit_code=item.get("exit_code", item.get("returncode")),
                started_unix=start, ended_unix=end, reported_elapsed_seconds=elapsed,
                elapsed_scope=item.get("scope", item.get("mode", "use the original receipt")),
                retained_receipt=item,
                component_may_be_nested_and_must_not_be_added_to_parent=True))
    union, seconds = interval_union(intervals)
    return rows, dict(supplied_receipts=len(rows), recorded_wall_intervals=len(intervals), disjoint_recorded_wall_intervals=union,
        union_of_recorded_wall_intervals_seconds=seconds,
        union_is_elapsed_wall_coverage_not_a_sum_of_cpu_or_standalone_deployment_costs=True,
        independent_research_validation_is_separately_paid_and_not_in_deployment_price_scenarios=True,
        untimed_authoring_remote_waits_and_future_publication_work="unavailable, not zero",
        this_reporting_pass_has_a_separate_actual_execution_receipt=True,
        source_schema_only_or_failed_attempts_are_not_scientific_successes=True)


def texescape(value):
    return str(value).replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#")


def num(value, scale=1, digits=3):
    """Human-readable approximation; exact endpoints stay in machine tables."""
    return f"{float(exact(value)*scale):.{digits}f}"


def pairnum(lo, hi, scale=1, digits=3):
    return "["+num(lo, scale, digits)+", "+num(hi, scale, digits)+"]"


def texlong(caption, heading, rows, columns, labelname, size="\\scriptsize"):
    return "\n".join([r"\begingroup", size, r"\setlength{\tabcolsep}{3pt}",
        r"\begin{longtable}{"+columns+"}", r"\caption{"+caption+r"}\label{"+labelname+r"}\\",
        r"\toprule", heading+r" \\ \midrule", r"\endfirsthead", r"\toprule", heading+r" \\ \midrule", r"\endhead",
        r"\midrule\multicolumn{"+str(len(columns.replace("@{}", "")))+r"}{r}{Continued on next page}\\\endfoot",
        r"\bottomrule\endlastfoot", *[" & ".join(row)+r" \\" for row in rows], r"\end{longtable}", r"\endgroup", ""])


def domain_tex(domain):
    if domain["empty"]:
        return r"$\varnothing$"
    def compact(value):
        text = f"{float(value):.3g}"
        if "e" in text:
            coefficient, exponent = text.split("e")
            return coefficient+r"\mathord{\times}10^{"+str(int(exponent))+"}"
        return text
    low = compact(domain["lower"])
    high = r"\infty" if domain["upper"] is None else compact(domain["upper"])
    return "$"+("[" if domain["lower_closed"] else "(")+low+", "+high+("]" if domain["upper_closed"] else ")")+"$"


def manuscript(out, groups, population_map, thresholds, contrasts, clocks, clock_summaries,
               diagnostics, price_rows, frontier_rows, summary):
    gm = {group(row): row for row in groups}
    tm = {group(row): row for row in clock_summaries}
    economic, costs, pop = [], [], []
    for risk in range(2):
        for arm in ARMS:
            base = gm[risk, arm, "completed"]
            prefix = [r"$1/2$" if risk == 0 else r"$3/4$", SHORT[arm]]
            economic.append(prefix+[pairnum(base["original_j_mean_lower"], base["original_j_mean_upper"], digits=6)]+
                [pairnum(gm[risk, arm, service]["own_incumbent_gain_mean_lower"], gm[risk, arm, service]["own_incumbent_gain_mean_upper"], 10**6) for service in SERVICES[1:]])
            costs.append(prefix+[num(gm[risk, arm, service]["complete_observed64_total_seconds"]) for service in SERVICES])
            pop.append(prefix+[pairnum(population_map[risk, arm, service]["simultaneous_population_mean_lower"],
                        population_map[risk, arm, service]["simultaneous_population_mean_upper"], 10**6) for service in SERVICES[1:]])
    event_total = sum(row.get("accepted_levels_needing_mixed_upper", 0) for row in diagnostics)
    transfer_total = sum(row.get("rejected_levels_needing_transfer_lower", 0) for row in diagnostics)
    changed = sum(row["changed_state_actions"] for row in groups)
    accepted = sum(row["accepted_steps"] for row in groups)
    signs = Counter(row["sign"] for row in contrasts)
    primary_seconds = sum(row["cohort64_seconds"] for row in groups)
    validation_seconds = summary["scientific_execution_receipts"]["independent"]["total_seconds"]
    neural_pairs = [row for row in contrasts if row["a_arm"] == "quadratic" and row["b_arm"] == "relu" and row["same_service_arm_contrast"]]
    neural_adverse = sum(row["sign"] == "strict-negative" for row in neural_pairs)
    neural_favorable = sum(row["sign"] == "strict-positive" for row in neural_pairs)
    neural_unresolved = len(neural_pairs)-neural_adverse-neural_favorable
    main = [r"\section{New actions under the original recursive objective}\label{sec:results120}",
        "The prospectively frozen experiment changes root decisions while retaining the original continuous innovation law, risk operator, feasible actions and terminal controller. "
        "Each of 64 newly acquired two-coordinate states is evaluated at both risk levels by all eight representations and all four services. "
        "Training uses the same fixed value-label grid for every learned representation; the paired method changes the policy comparison and acquisition rule, not the critic's training target. "
        "The source, fitted actors and actual entropy/state artifacts were separately committed before held-out decisions. Initial states are the independent units; shock nodes, risk levels, methods and timing repetitions add no independent observations.",
        r"We denote the completed incumbent by C, inherited compiled-safe improvement by L, the new paired rule by P, and the strong direct-refinement proposal with the same paired acceptance gate by D. "
        r"Every returned root action is followed by the unchanged terminal controller. Independent rational bounds reconstruct the original policy objective $J$, with the single $\beta 2^{-20}$ implemented-future allowance; the original all-action lower yields regret and action-error upper bounds.",
        texlong(r"All-arm original-policy objectives and within-arm gains. C reports mean $J$; L/P/D report mean $J_C-J$ in $10^{-6}$ units. Bracket endpoints are displayed approximations of retained exact rational bounds.",
                r"$\alpha$ & Arm & C: mean $J$ & L gain & P gain & D gain", economic, "llrrrr", "tab:economic120"),
        f"Across the complete 4096-decision catalogue, {changed} returned decisions differ from their own completed incumbent and {accepted} strict improvement steps are accepted. "
        f"At the actual recorded resolutions, {event_total} accepted steps need the new mixed upper comparison: the separately valid convex-only scalar upper remains nonnegative. "
        f"The transferred incumbent slack is needed for {transfer_total} recorded early non-improvement rejections. "
        "These counts describe which bound enables the recorded stopping decision; they do not claim that a conventional method would fail at a later paid refinement or supply a measured counterfactual running time.",
        f"All 992 unordered same-risk method/service comparisons are retained: {signs['strict-negative']} strict negative, {signs['strict-positive']} strict positive, {signs['exact-zero']} exact zero and {signs['contains-zero']} intervals containing zero, in the declared A-minus-B order. "
        f"Among the eight same-service quadratic-versus-ReLU comparisons, {neural_adverse} favor quadratic, {neural_favorable} favor ReLU and {neural_unresolved} are exact-zero or unresolved. "
        "These are comparisons of the recorded common-state sample. The ReLU and hinge actors use identical retained feature and coefficient arrays, with the full feature-acquisition charge paid by each; action identity is separately checked rather than inferred from that representation identity.",
        r"\subsection{Complete costs and adoption conditions}\label{sec:costresults120}",
        texlong(r"Complete observed cost of serving all 64 original states, in seconds. Each entry includes its standalone acquisition charge and the actual full cohort clock, including rejected candidates and certificate work.",
                r"$\alpha$ & Arm & C & L & P & D", costs, "llrrrr", "tab:cost120"),
        f"The 64 measured primary cohort clocks sum to {num(primary_seconds)} seconds. The separate independent rational validation process takes {num(validation_seconds)} seconds; its full primitive trace and all per-policy costs are retained. "
        "This research validation cost is displayed separately from a deployed service, which already pays its actual production certificate and every refused candidate. "
        "Acquisition charges include common labels, feature search and all fitting audits, serialization and conservatively assigned common overhead. They are allocations of measured components, not hypothetical independently timed fits. "
        "Three fresh serial timing processes serve the fixed first 32 states. All 192 cohort clocks and 6144 action comparisons are retained. Medians and ranges are descriptive; no timing confidence or throughput extrapolation is asserted.",
        r"The predeclared amortization scenarios use $B\in\{1,64,1024,65536\}$ and "
        r"$C_{m,r}(B)=(A_m+L_{m,r})/B+(T_{m,r}-L_{m,r})/32$. "
        r"They reuse observed 32-state operating costs and are not measured scaling. For each original sample gain interval $[g_L,g_U]$ and extra cost $\Delta C$, the reporter retains the exact nonnegative-price sets on which "
        r"$g_L-\lambda\Delta C>0$ and $g_U-\lambda\Delta C>0$. Empty sets, zero or negative extra costs, and strict endpoints remain explicit. "
        "Comparison with the best conventional sample alternative intersects sufficient conditions against the full seven-arm, four-service menu, then across all three clocks. This is a conditional sufficient statement for the measured menu and cost scenario; it is not population adoption or a joint existence claim from overlapping upper bounds.",
        r"\subsection{The prespecified population gain family}\label{sec:populationresults120}",
        texlong(r"Simultaneous population mean-gain bounds in $10^{-6}$ original-objective units for all 48 within-arm service comparisons. The fixed event and mean family has coverage at least $19/20$ under the declared independent finite-uniform initial-state law, conditional on frozen actors and the ideal independent OS-entropy assumption.",
                r"$\alpha$ & Arm & L population gain & P population gain & D population gain", pop, "llrrr", "tab:population120"),
        "The exact binomial calculation uses all 64 states and the four fixed positive-gain thresholds. The bounded-mean calculation and event staircase use the same predeclared family allocation. "
        "No state is discarded for a small gain, broad interval, repeated draw or a conventional winner. Positive within-incumbent gain does not establish cross-representation superiority. "
        "The full development tables retain all original regret bounds, optimal-action-error upper bounds, precision failures, operation counters, timing repetitions, 992 sample contrasts and price domains. A reported execution pass asserts record consistency and finite compatibility; the associated theorems, rather than numerical pass counts, justify the certificate's mathematical scope.", ""]
    extended = [r"\section{Complete R120 numerical reporting}\label{sec:developmentresults120}",
        "This appendix displays the fixed all-arm census and retains every adverse or unresolved entry. Exact fraction endpoints and all raw counter dimensions accompany these rounded tables in tables120. C/L/P/D denote completed, legacy-safe, paired and direct-refine. Action error columns are independently justified upper bounds, never an observed distance to an exact optimizer. The original future controller, model, information access and accuracy requirement are unchanged."]
    objective_rows = []
    cost_rows = []
    for row in groups:
        key = group(row)
        prefix = [str(key[0]), SHORT[key[1]], SHORT[key[2]]]
        objective_rows.append(prefix+[pairnum(row["original_j_mean_lower"], row["original_j_mean_upper"], digits=6),
            pairnum(row["original_regret_mean_lower"], row["original_regret_mean_upper"], 10**6),
            num(row["original_regret_maximum_upper"], 10**6), num(row["original_action_rms_error_upper"], digits=6),
            str(row["changed_state_actions"]), str(row["accepted_steps"])])
        ts = tm[key]
        cost_rows.append(prefix+[num(row["standalone_acquisition_charge_seconds"]), num(row["cohort64_seconds"]),
            num(row["singleton_service_sum_seconds"]), num(row["cold_load_seconds"], digits=6),
            num(row["decision_trial_recording_seconds"]), num(row["cohort_remaining_overhead_seconds"]),
            num(ts["cohort_seconds_median"])+" ["+num(ts["cohort_seconds_minimum"])+", "+num(ts["cohort_seconds_maximum"])+"]"])
    extended += [texlong(r"All 64 original objective and regret groups. Regret columns use $10^{-6}$ units; RMS is an optimal-action-error upper bound. Risk index 0/1 means $\alpha=1/2,3/4$.",
        r"Risk & Arm & Svc & Mean $J$ & Mean regret & Max regret & RMS bound & Changes & Steps", objective_rows, "lllrrrrrr", "tab:allobjective120"),
        texlong(r"All 64 cost decompositions in seconds. A is the complete standalone acquisition charge; T64 includes load, service and logging. The last column retains the median and full range of all three T32 clocks. Event-serialization clocks overlap service time and are not added twice.",
        r"Risk & Arm & Svc & A & T64 & Service & Load & Records & Other & T32: med [range]", cost_rows, "lllrrrrrrr", "tab:allcost120")]
    trialrows = [[str(row["index"]), SHORT[row["arm"]], SHORT[row["service"]], str(row["candidate_attempts"]),
        str(row["precision_attempts"]), str(row["unqualified_candidate_levels"]), str(row["certified_nonimprovement_levels"]),
        str(row["budget_exhausted_candidates"]), str(row["identical_action_shortcuts"]), str(row["first_actor_rejections"]),
        str(row["completed_exact_fallback_entries"])] for row in groups]
    extended.append(texlong("All candidate and certificate outcomes. Candidates and precision levels count different units. Refused candidates and exhausted ladders remain paid in every measured service.",
        "Risk & Arm & Svc & Candidates & Levels & Unqual. & Nonimpr. & Exhaust & Equal & First rej. & Fallback", trialrows, "lllrrrrrrrr", "tab:alltrials120"))
    diagnosticrows = [[str(row["index"]), SHORT[row["arm"]], SHORT[row["service"]],
        str(row.get("density_pairs", 0)), str(row.get("precision_levels", 0)), str(row.get("paid_terminal_rows", 0)),
        str(row.get("paid_integer_sqrt_calls", 0)), str(row.get("paired_upper_active_levels", 0)),
        str(row.get("accepted_levels_needing_mixed_upper", 0)), str(row.get("rejected_levels_needing_transfer_lower", 0))] for row in diagnostics]
    extended.append(texlong("All recorded paired-bound activity. Need-upper identifies accepted levels whose separate convex-only scalar upper is nonnegative. Need-transfer identifies certified rejections whose lower remains negative with the directly measured incumbent slack. Neither is a counterfactual timing experiment.",
        "Risk & Arm & Svc & Densities & Levels & Paid rows & Sqrts & Upper active & Need upper & Need transfer", diagnosticrows, "lllrrrrrrr", "tab:allpairuse120"))
    clockrows = [[str(row["index"]), SHORT[row["arm"]], SHORT[row["service"]], str(row["repeat"]), num(row["cohort_seconds"]),
        num(row["singleton_sum_seconds"]), num(row["cold_load_seconds"], digits=6),
        num(row["cohort_ratio_to_own_completed"]), num(row["complete_observed32_ratio_to_own_completed"])] for row in clocks]
    extended.append(texlong("All 192 raw 32-state cohort clocks and matched-repeat ratios. Timing repetitions are descriptive observations on the same first 32 states and are not new population units.",
        "Risk & Arm & Svc & Rep & T32 & Service & Load & T32/C & Full/C", clockrows, "lllrrrrrr", "tab:allclocks120"))
    thresholdrows = [[str(row["index"]), SHORT[row["arm"]], SHORT[row["service"]], str(THRESHOLDS.index(row["threshold"])+1),
        str(row["successes"]), num(row["event_probability_lower"], digits=6), num(row["inversion_upper"], digits=6)] for row in thresholds]
    extended.append(texlong(r"All 192 exact event inferences. Threshold indices 1--4 denote $2^{-20},2^{-18},2^{-16},2^{-14}$. Displayed bracket endpoints may round identically; exact 48-bisection rational endpoints and integer checks remain in the machine tables.",
        "Risk & Arm & Svc & Threshold & Successes/64 & Probability lower & Inversion upper", thresholdrows, "lllrrrr", "tab:allevents120"))
    contrastrows = [[str(row["index"]), SHORT[row["a_arm"]]+"/"+SHORT[row["a_service"]],
        SHORT[row["b_arm"]]+"/"+SHORT[row["b_service"]],
        pairnum(row["mean_original_j_a_minus_b_lower"], row["mean_original_j_a_minus_b_upper"], 10**6),
        texescape(row["sign"]), str(row["identical_policy_rows"])] for row in contrasts]
    extended.append(texlong(r"All 992 sample mean original-J contrasts A minus B, in $10^{-6}$ units. The original optimum cancels in the same regret contrast. Exact equal-policy rows contribute zero before averaging. These are sample interval signs, without additional cross-arm population confidence claims.",
        "Risk & A & B & Mean A minus B & Sign & Equal/64", contrastrows, "lllr lr".replace(" ", ""), "tab:allcontrasts120"))
    pricerows = [[str(row["index"]), SHORT[row["arm"]]+"/"+SHORT[row["service"]], str(row["volume"]),
        "Own C" if row["comparator"] == "own-completed" else "All conv.",
        domain_tex(row["sufficient_positive_benefit_prices"]) if row["timing_action_binding_verified"] else "Unbound",
        domain_tex(row["not_ruled_out_positive_benefit_prices"]) if row["timing_action_binding_verified"] else "Unbound"]
        for row in price_rows if row["repeat"] == "intersection-all-three"]
    extended.append(texlong("All workload and comparator price domains after intersection across the three measured clocks. Units are original objective per second. Endpoints are displayed approximations; the exact open/closed fractions are authoritative. Possible means not ruled out by pairwise intervals, not simultaneous existence or population adoption. Research validation is separately paid in the research ledger and excluded from deployed-service scenarios.",
        "Risk & Candidate & B & Comparator & Sufficient prices & Not ruled out", pricerows, "llrlrr", "tab:allprices120"))
    actualprices = [[str(row["index"]), SHORT[row["arm"]]+"/"+SHORT[row["service"]],
        "Own C" if row["comparator"] == "own-completed" else "All conv.",
        domain_tex(row["sufficient_positive_benefit_prices"]), domain_tex(row["not_ruled_out_positive_benefit_prices"])]
        for row in price_rows if row["repeat"] == "actual-primary64"]
    extended.append(texlong("All 112 price domains using the actual primary 64-state workload, its complete acquisition charge and its own recorded cohort clock. These contain no timing-workload extrapolation. They remain recorded-sample sufficient or not-ruled-out conditions, not population adoption.",
        "Risk & Candidate & Comparator & Sufficient prices & Not ruled out", actualprices, "lllrr", "tab:actualprices120"))
    frontierdisplay = [[str(row["index"]), SHORT[row["arm"]], SHORT[row["service"]],
        "Cost/J" if row["frontier"].startswith("complete") else "Resources/J", "Yes" if row["interval_nondominated"] else "No",
        str(len(row["certified_recorded_dominators"]))] for row in frontier_rows]
    extended.append(texlong("All interval-nondomination classifications. An unresolved pair remains undominated by that comparison. Counters are separate resource dimensions rather than a universal query unit; membership is not proof of true Pareto or population optimality.",
        "Risk & Arm & Svc & Dimensions & Undominated & Dominators", frontierdisplay, "lllllr", "tab:allfrontiers120"))
    extended += ["The machine tables also retain the complete operation-counter vector for every primary and timing cohort, all 6144 timing action identities, exact model/acquisition identities and all 4096 production/independent interval checks. The input registry binds every file actually read before and after reporting. Research clocks are listed by original scope and nesting; the union of their recorded wall intervals avoids adding child timing clocks twice. Untimed authoring, remote waits and later publication work are unavailable rather than assigned zero cost.", ""]
    write_text(out / "new120" / "results120.tex", "\n\n".join(main))
    write_text(out / "new120" / "development120_results.tex", "\n\n".join(extended))


def ancestry(repository, earlier, later):
    require(earlier != later, "Custody barriers must be separate commits")
    run = subprocess.run(["git", "-C", str(repository), "merge-base", "--is-ancestor", earlier, later], capture_output=True)
    require(run.returncode == 0, "Required source/actor/state ancestor relation is absent")
    return dict(earlier=earlier, later=later, distinct=True, git_ancestor_verified=True)


def scientific_input_links(inputs, directories, primary_path, independent_path):
    independent_link = inputs.json(directories["independent"] / "PRIMARY_INPUT120.json")
    require(independent_link["sha256"] == inputs.bind(primary_path)["sha256"] and
            independent_link["bytes"] == primary_path.stat().st_size, "Independent input does not bind this primary catalogue")
    stats_link = inputs.json(directories["stats"] / "INPUTS120.json")
    require(stats_link["primary"]["sha256"] == inputs.bind(primary_path)["sha256"] and
            stats_link["independent"]["sha256"] == inputs.bind(independent_path)["sha256"],
            "Statistics do not bind this primary/independent catalogue")
    return dict(independent=independent_link, statistics=stats_link,
                paths_in_original_receipts_are_preserved_while_actual_content_is_remapped_by_hash=True)


def reporting_summary(groups, contrast_rows, match_rows, diagnostics, prices, frontier_rows,
                      parameters, primary, independent_summary, executions, states):
    matching = []
    for i in range(2):
        for j in range(N):
            for service in SERVICES:
                rr, hr = primary[i, j, "relu", service], primary[i, j, "hinge", service]
                matching.append(dict(index=i, row=j, service=service, relu_action_hex=rr["action_hex"],
                    hinge_action_hex=hr["action_hex"], action_equal=rr["action_hex"] == hr["action_hex"],
                    state_equal=rr["state_hex"] == hr["state_hex"]))
    require(len(matching) == 512, "Full ReLU/hinge matching-action census")
    gm = {group(row): row for row in groups}
    wholecost = {}
    for risk in range(2):
        keys = [key for key in GROUPS if key[0] == risk]
        wholecost[risk] = dict(
            minimum_recorded_original_j_mean_upper=min(gm[key]["original_j_mean_upper"] for key in keys),
            minimum_recorded_complete_observed64_total_seconds=min(gm[key]["complete_observed64_total_seconds"] for key in keys),
            j_upper_minimizers=[label(key) for key in keys if gm[key]["original_j_mean_upper"] == min(gm[k]["original_j_mean_upper"] for k in keys)],
            complete_cost_minimizers=[label(key) for key in keys if gm[key]["complete_observed64_total_seconds"] == min(gm[k]["complete_observed64_total_seconds"] for k in keys)],
            minimizers_are_descriptive_over_all_cells_not_selected_replacement_baselines=True)
    selected = [row for row in prices if row["repeat"] == "intersection-all-three"]
    price_counts = Counter((row["comparator"], "unbound" if not row["timing_action_binding_verified"] else
                           "empty" if row["sufficient_positive_benefit_prices"]["empty"] else "nonempty") for row in selected)
    return dict(status="complete-record-analysis", source_commit=SOURCE,
        population_states=64, primary_decisions=4096, primary_groups=64, population_gain_groups=48, threshold_events=192,
        unordered_sample_contrasts=992, within_arm_service_sample_contrasts=96, same_service_arm_sample_contrasts=224,
        timing_decisions=6144, raw_cohort_clocks=192, timing_processes=3,
        timing_action_matches=sum(row["action_equal"] for row in match_rows),
        timing_action_mismatches=sum(not row["action_equal"] for row in match_rows),
        timing_interval_mismatches=sum(not row["complete_policy_interval_equal"] for row in match_rows),
        timing_querycount_mismatches=sum(not row["querycounts_equal"] for row in match_rows),
        relu_hinge_parameter_identities=parameters, relu_hinge_action_pairs=512,
        relu_hinge_action_matches=sum(row["action_equal"] for row in matching),
        relu_hinge_action_mismatches=sum(not row["action_equal"] for row in matching),
        accepted_steps=sum(row["accepted_steps"] for row in groups),
        changed_state_actions=sum(row["changed_state_actions"] for row in groups),
        sample_contrast_sign_counts=dict(Counter(row["sign"] for row in contrast_rows)),
        new_mixed_upper_necessary_at_accepted_recorded_levels=sum(row.get("accepted_levels_needing_mixed_upper", 0) for row in diagnostics),
        incumbent_transfer_necessary_at_rejected_recorded_levels=sum(row.get("rejected_levels_needing_transfer_lower", 0) for row in diagnostics),
        price_domains_all_three_clocks={"/".join(key): value for key, value in sorted(price_counts.items())},
        interval_nondominated_counts=dict(Counter(row["frontier"] for row in frontier_rows if row["interval_nondominated"])),
        complete_menu_descriptive_minima=wholecost, independent_validation=independent_summary,
        scientific_execution_receipts=executions, state_custody=states,
        population_inference_scope="only the prospectively declared 48 within-arm gain groups and 192 events",
        cross_representation_scope="all64-state original-policy sample interval contrasts, no new population family",
        price_scope="sufficient recorded-menu conditions in declared amortization scenarios, not measured scaling or population adoption",
        false_success_requirements_absent="No favorable sign, neural winner, narrow interval, empty failure ledger or adoption region is required"), matching


def run(args, out, inputs):
    source = inputs.source(args.source_commit)
    require(args.source_commit == SOURCE, "This reporter's fixed design is bound to the actual R120 F commit")
    inputs.bind(Path(__file__).resolve())
    spec = inputs.git_file(args.revision / "REPORTING_SPEC120.md", "594d9336d89bedfd360e942146ae490e0fabd3a0")
    require(spec["sha256"] == "0f6bcd35b6b78ed924acce413eb2e715968eebe441efa5c0f0f20ffe3c012b7c", "Pre-outcome reporting specification differs")
    directories = {name: getattr(args, name) for name in ("acquisition", "states", "primary", "independent", "stats")}
    executions = {name: successful(inputs, root, args.source_commit) for name, root in directories.items()}
    primary_path = args.primary / "records120.jsonl"
    primary = census(list(inputs.jsonl(primary_path)), N, True)
    actor_commits = {row["actor_commit"] for row in primary.values()}
    state_commits = {row["state_commit"] for row in primary.values()}
    require(len(actor_commits) == len(state_commits) == 1 and {row["source_commit"] for row in primary.values()} == {args.source_commit},
            "All primary decisions must share the declared F/M/D boundaries")
    actor_commit, state_commit = next(iter(actor_commits)), next(iter(state_commits))
    orders = [ancestry(args.repository, args.source_commit, actor_commit), ancestry(args.repository, actor_commit, state_commit)]
    actor_manifest = inputs.manifest(args.acquisition, "ACQUISITION_MANIFEST120.json", args.source_commit, "acquire", actor_commit)
    state_manifest = inputs.manifest(args.states, "STATE_MANIFEST120.json", args.source_commit, "sample", state_commit)
    primary_manifest = inputs.manifest(args.primary, "RESULT_MANIFEST120.json", args.source_commit, "primary")
    for row in primary.values():
        require(row["repeat"] is None, "Primary timing contamination")
    states = validate_states(inputs, args.states, primary, args.source_commit, actor_commit)
    acq, parameters = acquisition(inputs, args.acquisition)
    for row in primary.values():
        require(row["model_sha256"] == acq[row["index"], row["arm"]]["model_sha256"], "Returned policy used a different frozen actor")
    independent, policies, reliability, independent_summary = compare_independent(inputs, args.independent, primary)
    links = scientific_input_links(inputs, directories, primary_path, args.independent / "comparisons120.jsonl")
    population_map, threshold_rows = population(inputs, args.stats, primary, independent)
    batches, trials, catalogue = read_batches(inputs, args.primary, primary, N, acq)
    groups = group_rows(primary, independent, batches, acq)
    group_map = {group(row): row for row in groups}
    contrast_rows, lookup = all_contrasts(primary, independent)
    clocks, matches, timing_batches, clock_summaries, timing_executions = timing(inputs, args.primary, primary, acq)
    for repeat in range(3):
        inputs.manifest(args.primary / "timing" / f"attempt-{repeat:02d}", "RESULT_MANIFEST120.json", args.source_commit, "timing-one")
    paired_rows, diagnostic_groups = paired_events(inputs, args.primary, batches, primary)
    prices, scenario_costs = price_scenarios(acq, timing_batches, group_map, lookup, matches)
    frontier_rows = frontiers(group_map, lookup)
    summary, hinge_matches = reporting_summary(groups, contrast_rows, matches, diagnostic_groups, prices, frontier_rows,
        parameters, primary, independent_summary, executions, states)
    summary["custody_ancestry"] = orders
    summary["recorded_source_verification"] = source
    summary["actual_actor_commit"] = actor_commit
    summary["actual_state_commit"] = state_commit
    summary["pre_outcome_reporting_spec_identity"] = spec
    summary["scientific_input_links"] = links
    summary["timing_execution_receipts"] = timing_executions
    summary["positive_staircase_groups"] = sum(exact(row["population_mean_staircase_lower"]) > 0 for row in population_map.values())
    summary["positive_independent_sample_gain_lower_groups"] = sum(row["own_incumbent_gain_mean_lower"] > 0 for row in groups)
    summary["primary_inside_catalogue_seconds"] = catalogue["inside_catalogue_seconds"]
    summary["frozen_artifact_member_counts"] = dict(actors=len(actor_manifest["files"]), states=len(state_manifest["files"]), primary=len(primary_manifest["files"]))
    tables = out / "tables120"
    tables.mkdir()
    table(tables, "groups120", groups)
    table(tables, "acquisition120", [acq[i, arm] for i in range(2) for arm in ARMS])
    table(tables, "population_groups120", [population_map[key] for key in GROUPS if key[2] != "completed"])
    table(tables, "threshold_events120", threshold_rows)
    table(tables, "sample_contrasts120", contrast_rows)
    table(tables, "raw_timing_clocks120", clocks)
    table(tables, "timing_summaries120", clock_summaries)
    table(tables, "timing_action_checks120", matches)
    table(tables, "relu_hinge_action_checks120", hinge_matches)
    table(tables, "certificate_compatibility120", reliability)
    table(tables, "paired_bound_levels120", paired_rows)
    table(tables, "paired_bound_groups120", diagnostic_groups)
    table(tables, "price_domains120", prices)
    table(tables, "scenario_costs120", scenario_costs)
    table(tables, "interval_frontiers120", frontier_rows)
    # Preserve every operation dimension as a separate column and never add
    # overlapping counters into a fabricated universal information budget.
    operation_rows = []
    for row in groups:
        operation_rows.append(dict(index=row["index"], arm=row["arm"], service=row["service"],
            **{"decision_"+name: count for name, count in row["querycounts"].items()},
            **{"standalone_labels_"+name: count for name, count in row["label_querycounts_if_standalone"].items()}))
    table(tables, "all_operation_dimensions120", operation_rows)
    table(tables, "unique_independent_policy_costs120", [dict(key_id=row["key_id"], state_hex=row["state_hex"],
        action_hex=row["action_hex"], alpha=row["alpha"], seconds=row["seconds"], terminal_contexts=row["terminal_contexts"],
        bins=row["bins"], terminal_steps=row["terminal_steps"], separate_research_validation_cost=True) for row in policies])
    manuscript(out, groups, population_map, threshold_rows, contrast_rows, clocks, clock_summaries,
               diagnostic_groups, prices, frontier_rows, summary)
    extra = list(args.ledger)
    for name in ("logs", "launchers", "launches"):
        folder = args.evidence_root / "results120" / name
        if folder.is_dir():
            extra.append(folder)
    # Include all earlier scientific attempt/failure receipts under results120,
    # not only the five explicitly selected successful input directories.
    all_attempts = args.evidence_root / "results120"
    selected = list(directories.values()) + ([all_attempts] if all_attempts.is_dir() else [])
    ledger, ledger_summary = research_ledger(inputs, selected, extra)
    table(tables, "research_ledger120", ledger)
    write_json(out / "RESEARCH_COST_SCOPE120.json", ledger_summary)
    summary["research_ledger"] = ledger_summary
    write_json(out / "SUMMARY_REPORT120.json", summary)
    write_json(out / "INPUTS_REPORT120.json", dict(files=inputs.final(), all_read_inputs_unchanged=True,
        source_commit=args.source_commit, actor_commit=actor_commit, state_commit=state_commit,
        spec_commit="594d9336d89bedfd360e942146ae490e0fabd3a0",
        economic_scientific_execution=False, input_raw_records_modified=False))
    return summary


def output_manifest(out):
    files = []
    for path in sorted(out.rglob("*")):
        if not path.is_file() or path.name == "OUTPUT_MANIFEST120.json":
            continue
        row = identity(path)
        row["path"] = path.relative_to(out).as_posix()
        stable = (row["path"].startswith("tables120/") and not path.name.startswith("research_ledger120.")) or row["path"].startswith("new120/")
        row["stable_replay_bytes"] = stable
        if not stable:
            row["replay_byte_exclusion_reason"] = ("Research ledger may include additional actual publication receipts or remapped evidence paths"
                if "research" in path.name.lower() or path.name == "RESEARCH_COST_SCOPE120.json" else
                "Actual reporting time, execution environment, source/input paths, or receipt binding; retain and inspect rather than byte-match")
        files.append(row)
    return dict(kind="R120 post-freeze read-only reporting outputs", files=files,
        stable_replay_files=[row["path"] for row in files if row["stable_replay_bytes"]],
        stable_replay_rule="The exact tables and generated snippets use all recorded scientific inputs and no new solver; compare all listed files byte-for-byte",
        mutable_or_environmental_receipts_remain_retained=True,
        excluded_from_byte_equality_does_not_mean_excluded_from_custody=True,
        reporting_does_not_amend_the_frozen_experiment=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--repository", type=Path)
    parser.add_argument("--source-commit", default=SOURCE)
    parser.add_argument("--output", required=True, type=Path)
    for name in ("acquisition", "states", "primary", "independent", "stats"):
        parser.add_argument("--"+name, type=Path, default=Path("results120")/(name+"-attempt01"))
    parser.add_argument("--ledger", action="append", type=Path, default=[],
                        help="Additional original execution/failure receipt or directory; preserved in the non-double-counted research ledger")
    args = parser.parse_args()
    args.revision = args.revision.resolve()
    args.evidence_root = (args.evidence_root or args.revision).resolve()
    if args.repository is None:
        result = subprocess.run(["git", "-C", str(args.revision), "rev-parse", "--show-toplevel"], check=True, capture_output=True, text=True)
        args.repository = Path(result.stdout.strip())
    args.repository = args.repository.resolve()
    for name in ("acquisition", "states", "primary", "independent", "stats"):
        path = getattr(args, name)
        setattr(args, name, (args.evidence_root/path if not path.is_absolute() else path).resolve())
    args.ledger = [(args.evidence_root/path if not path.is_absolute() else path).resolve() for path in args.ledger]
    args.output = args.output.resolve()
    # The reporter writes only its fresh attempt directory. In particular it
    # never writes root-owned native manuscript files or any frozen raw data.
    for name in ("acquisition", "states", "primary", "independent", "stats"):
        selected = getattr(args, name)
        require(args.output != selected and selected not in args.output.parents,
                "Reporting output cannot be inside a scientific input directory")
    args.output.mkdir(parents=True, exist_ok=False)
    start_wall, start_clock = time.time(), time.perf_counter()
    initial = dict(kind="post-freeze read-only reporting", status="started", argv=sys.argv,
        started_unix=start_wall, source_commit=args.source_commit, reporter_source=identity(Path(__file__).resolve()),
        reporting_spec=identity(args.revision/"REPORTING_SPEC120.md"), python=sys.version,
        revision=str(args.revision), evidence_root=str(args.evidence_root), repository=str(args.repository),
        economic_solver_imported_or_executed=False, new_randomness_or_models=False)
    write_json(args.output/"START_REPORT120.json", initial)
    inputs = Inputs(args.revision, args.evidence_root, args.repository)
    try:
        summary = run(args, args.output, inputs)
        receipt = dict(kind="read-only original-record analysis", status="executed", exit_code=0,
            source_commit=args.source_commit, started_unix=start_wall, ended_unix=time.time(),
            total_seconds=time.perf_counter()-start_clock, reporter_source=initial["reporter_source"],
            reporting_spec=initial["reporting_spec"], economic_solver_executed=False,
            all_scientific_input_bytes_unchanged=True, unique_input_files=len(inputs.records),
            primary_decisions=4096, timing_decisions=6144, sample_contrasts=992,
            population_groups=48, threshold_events=192,
            stable_outputs_are_reporting_derivatives_not_new_scientific_observations=True)
        write_json(args.output/"EXECUTION_REPORT120.json", receipt)
        write_json(args.output/"OUTPUT_MANIFEST120.json", output_manifest(args.output))
        print(json.dumps(encode({name: summary[name] for name in (
            "status", "primary_decisions", "accepted_steps", "changed_state_actions", "timing_action_mismatches",
            "relu_hinge_action_mismatches", "sample_contrast_sign_counts",
            "new_mixed_upper_necessary_at_accepted_recorded_levels", "positive_staircase_groups")})), flush=True)
        print(json.dumps(dict(reporting_seconds=receipt["total_seconds"], output=str(args.output))), flush=True)
    except BaseException:
        append_json(args.output/"FAILED_REPORT120.jsonl", dict(status="failed", exit_code=1,
            started_unix=start_wall, ended_unix=time.time(), total_seconds=time.perf_counter()-start_clock,
            exception=traceback.format_exc(), read_inputs=list(inputs.records.values()),
            source_commit=args.source_commit, partial_reporting_outputs_retained=True,
            scientific_input_replaced_or_modified=False, no_success_receipt_created=True))
        raise


if __name__ == "__main__":
    main()
