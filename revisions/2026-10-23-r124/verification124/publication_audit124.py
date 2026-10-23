#!/usr/bin/env python3
"""Independent, post-execution R124 publication arithmetic and custody audit.

This reader is outside SOURCE_FREEZE124.  It imports only the Python standard
library.  It does not import the production reporter, optimizer, envelope,
economic primitives, or any learned representation, and runs no economic
evaluation, fitting, entropy draw, or timing experiment.

Saved independent economic enclosures are premises here.  Their accumulation,
chronological claim checks, intersections, inferential summaries, full costs,
and price domains are independently recomputed.  Exact dual arithmetic is
rechecked from saved paid information, without solving another optimization.
The separate frozen exact-certificate audit and economic-evaluation receipts
remain required and are bound by hashes; they are not replaced by this reader.

The final PUBLICATION_AUDIT124.json is created exclusively after a terminal
report exists and every check passes.  Each executed audit attempt, including
a failed attempt, has a separate immutable provenance subdirectory.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from fractions import Fraction as Q

SOURCE = "2f0485174e7f518909ab73311e00251647ed6b47"
DRAW = "a78ee67f386b2b547ecfb5f1986119c199c4fd68"
ACTORS = "796c5f2badf68b051ac6c144884c0e61b87faf5e"
TAU = Q(1, 256)
DELTA = Q(15, 16777216)
EVENT = Q(1, 2**24)
VOLUMES = (32, 256, 4096, 65536)
ARMS = ("quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid")
SERVICES = ("fused_two", "joint_two")
ACTOR_KEYS = [(i, 0, "online", "online") for i in range(2)] + [
    (i, b, a, loss) for i in range(2) for b in (5, 9)
    for a in ARMS for loss in ("value", "marginal")
]
CELL_KEYS = [a + (s,) for a in ACTOR_KEYS for s in SERVICES]
FIELDS = ("index", "budget", "arm", "training_loss", "mode")


def normalized(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): normalized(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalized(v) for v in value]
    return value


def exclusive_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(normalized(value), handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def blob_id(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def cell(row):
    return tuple(row[f] for f in FIELDS)


def observation(row):
    return cell(row) + (row["row"],)


def economic_key(row, action=None):
    action = row["action"] if action is None else action
    return (tuple(float(x).hex() for x in row["state"]),
            float(action).hex(), float(row["alpha"]).hex())


def key_hash(key):
    return sha_bytes(json.dumps(key, separators=(",", ":")).encode())


def avg(values):
    return sum(values, Q(0)) / len(values)


def exact_binomial_tail(k, n, p):
    # The finite polynomial is evaluated exactly; no floating cdf is trusted.
    return sum((Q(math.comb(n, j)) * p**j * (1-p)**(n-j)
                for j in range(k, n+1)), Q(0))


def event_lower(k):
    if k == 0:
        return Q(0)
    low, high = Q(0), Q(1)
    for _ in range(48):
        test = (low + high) / 2
        if exact_binomial_tail(k, 16, test) <= Q(1, 11600):
            low = test
        else:
            high = test
    return low


def price_interval(inequalities):
    """Intersect d+c*p<0 with p>=0 by independent endpoint classification."""
    strict_lowers, strict_uppers = [], []
    impossible = False
    for intercept, slope in inequalities:
        if slope < 0:
            strict_lowers.append(-intercept/slope)
        elif slope > 0:
            strict_uppers.append(-intercept/slope)
        elif intercept >= 0:
            impossible = True
    lower = max([Q(0)] + strict_lowers)
    upper = min(strict_uppers) if strict_uppers else None
    empty = impossible or (upper is not None and upper <= lower)
    return dict(empty=empty, lower=lower, upper=upper,
                strict_lower=lower in strict_lowers,
                strict_upper=upper is not None)


def gradient_lines(case, x, upper):
    mu, lipschitz = Q(case["mu"]), Q(case["L"])
    lines = []
    for payload in case["payloads"]:
        anchor = Q(payload["a"])
        if upper:
            slope = lipschitz if x >= anchor else mu
            value = Q(payload["g_upper"])
        else:
            slope = mu if x >= anchor else lipschitz
            value = Q(payload["g_lower"])
        lines.append((slope, value - slope*anchor))
    return lines


def envelope_value(case, x, upper):
    values = [s*x+c for s, c in gradient_lines(case, x, upper)]
    return min(values) if upper else max(values)


def integrated_envelope(case, left, right, upper):
    if left == right:
        return Q(0)
    breaks = sorted({left, right} | {
        Q(p["a"]) for p in case["payloads"] if left < Q(p["a"]) < right
    })
    answer = Q(0)
    for first, last in zip(breaks, breaks[1:]):
        lines = gradient_lines(case, (first+last)/2, upper)
        cuts = {first, last}
        for i, (s, c) in enumerate(lines):
            for t, d in lines[:i]:
                if s != t:
                    cross = (d-c)/(s-t)
                    if first < cross < last:
                        cuts.add(cross)
        ordered = sorted(cuts)
        for a, b in zip(ordered, ordered[1:]):
            middle = (a+b)/2
            scores = [s*middle+c for s, c in lines]
            wanted = min(scores) if upper else max(scores)
            slope, intercept = lines[scores.index(wanted)]
            answer += slope*(b*b-a*a)/2 + intercept*(b-a)
    return answer


def contrast(case, first, last):
    if first <= last:
        return (integrated_envelope(case, first, last, False),
                integrated_envelope(case, first, last, True))
    return (-integrated_envelope(case, last, first, True),
            -integrated_envelope(case, last, first, False))


class Audit:
    def __init__(self, root):
        self.root = root.resolve()
        self.repo = self.root.parents[1]
        self.prior = self.root.parent / "2026-10-22-r123"
        self.checks = 0
        self.inputs = {}
        self.sections = {}
        self._trees = {}
        self.receipts = {}

    def require(self, condition, message):
        self.checks += 1
        if not condition:
            raise AssertionError(message)

    def read(self, path):
        path = Path(path)
        if not path.is_absolute():
            path = self.root / path
        data = path.read_bytes()
        relative = str(path.relative_to(self.repo))
        meta = dict(path=relative, bytes=len(data), sha256=sha_bytes(data))
        if relative in self.inputs:
            self.require(self.inputs[relative] == meta, "Input changed during audit: " + relative)
        self.inputs[relative] = meta
        return data

    def hash_file(self, path):
        return sha_bytes(self.read(path))

    def obj(self, path):
        return json.loads(self.read(path))

    def rows(self, path):
        return [json.loads(line) for line in self.read(path).splitlines() if line.strip()]

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo)

    def tree(self, commit):
        if commit not in self._trees:
            raw = self.git("ls-tree", "-rz", commit, "--", "revisions/2026-10-20-r121/results121/",
                           "revisions/2026-10-22-r123/", "revisions/2026-10-23-r124/")
            table = {}
            for rec in raw.split(b"\0"):
                if not rec:
                    continue
                meta, name = rec.split(b"\t", 1)
                mode, kind, oid = meta.decode().split()
                if kind == "blob":
                    table[name.decode()] = oid
            self._trees[commit] = table
        return self._trees[commit]

    def pinned(self, path, commit, original=None):
        path = Path(path)
        if not path.is_absolute():
            path = self.root / path
        original = original or str(path.relative_to(self.repo))
        data = self.read(path)
        expected = self.tree(commit).get(original)
        self.require(expected is not None and blob_id(data) == expected,
                     f"Pinned Git content differs: {commit}:{original}")
        return dict(source_commit=commit, source_path=original,
                    git_blob=expected, sha256=sha_bytes(data), bytes=len(data))

    def compare(self, got, wanted, context):
        """Compare each independently derived field with typed exact equality."""
        for key, expected in wanted.items():
            self.require(key in got, f"Missing reported field {context}.{key}")
            actual = got[key]
            if isinstance(expected, Q):
                self.require(Q(actual) == expected, f"Exact rational mismatch {context}.{key}")
            elif isinstance(expected, dict):
                self.compare(actual, expected, context + "." + key)
            elif isinstance(expected, (tuple, list)):
                self.require(len(actual) == len(expected), f"List census differs {context}.{key}")
                for j, value in enumerate(expected):
                    if isinstance(value, Q):
                        self.require(Q(actual[j]) == value, f"Exact list endpoint differs {context}.{key}[{j}]")
                    else:
                        self.require(actual[j] == normalized(value), f"List member differs {context}.{key}[{j}]")
            else:
                self.require(actual == expected and (not isinstance(expected, bool) or type(actual) is bool),
                             f"Reported field differs {context}.{key}")

    def indexed(self, rows, key, expected, context):
        table = {key(row): row for row in rows}
        self.require(len(table) == len(rows) == len(expected) and set(table) == set(expected),
                     "Complete unique census differs: " + context)
        return table

    def completed(self, name):
        start = self.obj(f"results124/{name}/START124.json")
        end = self.obj(f"results124/{name}/EXECUTION124.json")
        self.require(end.get("status") == "executed" and end.get("exit_code") == 0,
                     "Stage is not terminal successful: " + name)
        self.require(start["started_unix"] <= end["ended_unix"] and end["seconds"] >= 0,
                     "Invalid stage clock: " + name)
        self.receipts[name] = (start, end)
        return start, end

    def custody(self):
        boundaries = self.obj("BOUNDARIES124.json")
        freeze = self.obj("SOURCE_FREEZE124.json")
        self.require(boundaries["source_commit"] == SOURCE and boundaries["state_commit"] == DRAW,
                     "Unexpected source/draw identity")
        self.require(freeze["actor_commit"] == ACTORS and len(freeze["files"]) == 269,
                     "Frozen actor or complete source census differs")
        self.pinned("SOURCE_FREEZE124.json", SOURCE)
        self.pinned("SOURCE_FREEZE124.json", DRAW)
        self.require(boundaries["source_manifest_sha256"] == self.hash_file("SOURCE_FREEZE124.json"),
                     "Source manifest SHA differs")
        sources = []
        for name, expected in sorted(freeze["files"].items()):
            path = self.repo / name
            actual = self.pinned(path, SOURCE)
            self.require(actual["sha256"] == expected, "Frozen SHA differs: " + name)
            self.require(self.tree(DRAW).get(name) == actual["git_blob"],
                         "Scientific source changed between F and D: " + name)
            sources.append(actual)
        source_readback = self.obj("provenance124/F124_REMOTE_READBACK.json")
        draw_readback = self.obj("provenance124/D124_REMOTE_READBACK.json")
        self.require(boundaries["source_readback_sha256"] == self.hash_file("provenance124/F124_REMOTE_READBACK.json")
                     and boundaries["state_readback_sha256"] == self.hash_file("provenance124/D124_REMOTE_READBACK.json"),
                     "Remote readback receipt SHA differs")
        self.require(source_readback["source_commit"] == SOURCE and draw_readback["state_commit"] == DRAW,
                     "Remote readback names another experiment")
        self.require({x["path"]: x["sha256"] for x in source_readback["checked_files"]} == freeze["files"],
                     "Remote F readback omitted a scientific file")
        for item in draw_readback["checked_files"]:
            got = self.pinned(self.repo / item["path"], DRAW)
            self.require(got["sha256"] == item["sha256"] and got["bytes"] == item["bytes"],
                         "Remote D checked file differs")
        entropy = self.read("results124/states/entropy124.bin")
        sample = self.obj("results124/states/states124.json")
        self.require(len(entropy) == 160 and len(sample["states"]) == 16,
                     "Frozen draw size differs")
        self.require(sha_bytes(entropy) == boundaries["entropy_sha256"]
                     and self.hash_file("results124/states/states124.json") == boundaries["states_sha256"],
                     "Draw SHA mismatch")
        self.require(sample["source_commit"] == SOURCE and sample["actor_commit"] == ACTORS,
                     "Sample source/actor mismatch")
        self.states = sample["states"]
        for j, row in enumerate(self.states):
            integers = [int.from_bytes(entropy[10*j+5*k:10*j+5*k+5], "little") for k in range(2)]
            state = [v/2**40 for v in integers]
            self.compare(row, dict(row=j, integers=integers, state=state,
                                   hex=[v.hex() for v in state]), "state")
        ftime = int(self.git("show", "-s", "--format=%ct", SOURCE))
        dtime = int(self.git("show", "-s", "--format=%ct", DRAW))
        self.require(self.git("show", "-s", "--format=%P", DRAW).decode().strip() == SOURCE,
                     "D is not the declared direct F child")
        draw_start, draw_end = self.completed("states")
        fr = dt.datetime.fromisoformat(source_readback["verified_utc"]).timestamp()
        dr = dt.datetime.fromisoformat(draw_readback["verified_utc"]).timestamp()
        self.require(ftime <= fr < draw_start["started_unix"] <= draw_end["ended_unix"] <= dtime <= dr,
                     "F/readback/draw/D/readback temporal order differs")
        self.require(boundaries["remote_source_readback_before_draw"] is True
                     and boundaries["remote_state_readback_before_economics"] is True,
                     "Independent source/draw barriers absent")
        for name in ("primary", "timing0", "timing1", "timing2", "audit", "independent", "report"):
            start, end = self.completed(name)
            self.require(dr < start["started_unix"], "Scientific execution preceded the D readback")
        primary_end = self.receipts["primary"][1]["ended_unix"]
        for name in ("audit", "independent"):
            self.require(primary_end <= self.receipts[name][0]["started_unix"],
                         "Post-primary verification started before terminal primary")
        report_start = self.receipts["report"][0]["started_unix"]
        self.require(max(self.receipts[name][1]["ended_unix"] for name in
                         ("primary", "timing0", "timing1", "timing2", "audit", "independent")) <= report_start,
                     "Reporting preceded a required terminal stage")
        models = {}
        actor_bindings = []
        for i, budget, arm, loss in ACTOR_KEYS:
            if arm == "online":
                continue
            suffix = f"results121/acquisition{budget}-attempt01/models/{i}-{arm}-{loss}/model.json"
            local = self.prior / "vendor/2026-10-20-r121" / suffix
            original = "revisions/2026-10-20-r121/" + suffix
            actor_bindings.append(self.pinned(local, ACTORS, original))
            models[(i, budget, arm, loss)] = self.obj(local)
        self.require(len(models) == 56, "Inherited fitted actor census differs")
        equivalences = 0
        for i in range(2):
            for budget in (5, 9):
                for loss in ("value", "marginal"):
                    relu = models[(i, budget, "relu", loss)]
                    hinge = models[(i, budget, "hinge", loss)]
                    for field in set(relu) | set(hinge):
                        if field in ("basis", "exact_feature_and_readout_identity_with_relu"):
                            continue
                        self.require(relu[field] == hinge[field], "ReLU/hinge readout data differ: " + field)
                    for field in set(relu["basis"]) | set(hinge["basis"]):
                        if field not in ("arm", "exact_corresponding_representation", "implementation"):
                            self.require(relu["basis"][field] == hinge["basis"][field],
                                         "ReLU/hinge feature geometry differs: " + field)
                    self.require(hinge["exact_feature_and_readout_identity_with_relu"] is True,
                                 "Hinge identity declaration absent")
                    equivalences += 1
        self.models = models
        self.boundaries = boundaries
        self.sections["custody"] = dict(source_commit=SOURCE, state_commit=DRAW,
            actor_commit=ACTORS, frozen_scientific_files=sources, frozen_file_count=len(sources),
            original_actor_bindings=actor_bindings, fitted_actors=56, online_risk_arms=2,
            independent_initial_states=16, entropy_bytes=160, independent_uniform_entropy_is_an_assumption=True,
            temporal_order=dict(source_commit_unix=ftime, source_readback_unix=fr,
                draw_started_unix=draw_start["started_unix"], draw_ended_unix=draw_end["ended_unix"],
                draw_commit_unix=dtime, draw_readback_unix=dr),
            relu_hinge_exact_model_pairs=equivalences,
            preserved_source_publication_failures=source_readback.get("publication_failures", []))

    def dual(self, row, selected):
        witness = selected["dual_witness"]
        p, case = witness["problem"], row["case"]
        origin, target = Q(row["baseline_action"]), Q(selected["b"])
        nodes = sorted({Q(x["a"]) for x in case["payloads"]} |
                       {Q(0), Q(case["A"]), origin, target})
        n = len(nodes)
        lo = [max(Q(a["W"])+contrast(case, Q(a["a"]), x)[0]
                  for a in case["payloads"]) for x in nodes]
        hi = [min(Q(a["U"])+contrast(case, Q(a["a"]), x)[1]
                  for a in case["payloads"]) for x in nodes]
        lo += [envelope_value(case, x, False) for x in nodes]
        hi += [envelope_value(case, x, True) for x in nodes]
        curvature, smoothness = Q(case["mu"]), Q(case["L"])
        K = smoothness-curvature
        self.compare(p, dict(nodes=nodes, lower=lo, upper=hi, mu=curvature, L=smoothness, K=K,
                             origin_index=nodes.index(origin), target_index=nodes.index(target)), "dual.problem")
        self.require(K > 0 and all(a <= b for a, b in zip(lo, hi)), "Invalid exact joint box")
        point, multipliers = list(map(Q, witness["point"])), list(map(Q, witness["multipliers"]))
        self.require(len(point) == 2*n and len(multipliers) == 4*(n-1)
                     and all(x >= 0 for x in multipliers), "Dual dimensions/nonnegativity differ")
        a, b = nodes.index(origin), nodes.index(target)
        objective = point[a]-point[b]
        value = objective
        derivative = [Q(0)]*(2*n)
        derivative[a] += 1
        derivative[b] -= 1
        for j in range(n-1):
            distance = nodes[j+1]-nodes[j]
            s = point[n+j+1]-point[n+j]-curvature*distance
            w = point[j+1]-point[j]-point[n+j]*distance-curvature*distance**2/2
            a1, a2, a3, a4 = multipliers[4*j:4*j+4]
            value += (a1+a2)*s*s/(2*K)+(a2-a1)*w-a2*s*distance+(a4-a3)*s-a4*K*distance
            ds = (a1+a2)*s/K-a2*distance+a4-a3
            dw = a2-a1
            derivative[j] -= dw
            derivative[j+1] += dw
            derivative[n+j] -= ds+distance*dw
            derivative[n+j+1] += ds
        residual = sum((g*((lower if g >= 0 else upper)-z)
                        for g, lower, upper, z in zip(derivative, lo, hi, point)), Q(0))
        self.compare(witness["dual"], dict(objective_at_point=objective,
            lagrangian_at_point=value, gradient=derivative, box_residual_correction=residual,
            lower_bound=value+residual, contrast_upper=-value-residual,
            primal_feasibility_or_solver_success_required=False), "dual.bound")
        progress = selected["dual_attempt"]
        self.require(progress["stage"] == "completed" and progress["started"] is True
                     and progress["exact_dual_completed"] is True,
                     "Successful dual witness lacks completed progress record")
        for field in ("problem", "point", "multipliers", "solver"):
            self.require(progress[field] == witness[field], "Dual progress/witness data differ")
        self.require(progress["solver_failure"] == witness["failure"], "Dual solver failure was lost")
        self.require(selected["dual_started"] and selected["dual_completed"]
                     and selected["dual_elapsed_seconds"] >= witness["seconds"] >= 0,
                     "Dual work or completed state not retained")
        return -value-residual

    def decisions(self):
        expected = {key+(j,) for key in CELL_KEYS for j in range(16)}
        primary = self.rows("results124/primary/records124.jsonl")
        lookup = self.indexed(primary, observation, expected, "1856 primary decisions")
        self.primary, self.primary_lookup = primary, lookup
        totals = collections.Counter()
        statuses = collections.Counter()
        support_counts = collections.Counter()
        for row in primary:
            key = observation(row)
            sample = self.states[row["row"]]
            self.compare(row, dict(state=sample["state"], state_hex=sample["hex"],
                alpha=(.5, .75)[row["index"]], source_commit=SOURCE, state_commit=DRAW,
                actor_commit=ACTORS, repeat=None, population_observation=True,
                qualified=True, additional_original_risk_queries=0,
                all_original_incumbent_work_reexecuted=True,
                original_objective_and_future_controller_unchanged=True), "primary.identity")
            self.require(float(row["action"]).hex() == row["action_hex"]
                         and float(row["baseline_action"]).hex() == row["baseline_action_hex"],
                         "Primary action hex differs")
            cap = Q(1, 8) + sum(map(Q, row["state"]))/16
            self.require(0 <= Q(row["action"]) <= cap and 0 <= Q(row["baseline_action"]) <= cap,
                         "Original constrained action infeasible")
            if row["case"] is not None:
                alpha=Q(row["alpha"])
                beta=Q(15,16)
                marginal=Q(1413,128)+beta*(Q(127,16)+Q(19625,20480)*alpha/(1-alpha))
                lipschitz=5+beta*(Q(5,16)*marginal+(Q(4,5)*marginal)**2*alpha/(Q(181,64)*(1-alpha)))
                self.compare(row["case"],dict(A=cap,incumbent=Q(row["baseline_action"]),mu=Q(2),
                    L=lipschitz,delta=DELTA,tau=TAU,omega=Q(1,8192),
                    old_optimum_lower=Q(row["baseline_optimum_lower"]),
                    gradient_rule="r122-finite-radii",gradient_cap=7,radius_indices=[2,40]),"original.case")
                self.require(len(row["case"]["payloads"])==len(row["initial_support_certificates"]),
                             "Paid supports were excluded from the joint-information case")
            self.require(0 <= Q(row["complete_policy_upper"])-Q(row["complete_policy_lower"]) <= Q(1,8192)
                         and 0 <= Q(row["complete_policy_upper"])-Q(row["original_optimum_lower"]) <= TAU,
                         "Returned original-objective qualification fails")
            self.require(row["accepted_improvement"] == (row["selected_menu_index"] is not None)
                         and row["accepted_improvement"] == (Q(row["certified_policy_gain_lower"]) > 0),
                         "Selected action/gain status differs")
            totals["accepted_actions"] += row["accepted_improvement"]
            totals["enhancement_failures"] += row["enhancement_failure"] is not None
            support_counts[(row["mode"], len(row["initial_support_certificates"]))] += 1
            all_menu = row["full_common_menu"]
            choices = {}
            for entry in all_menu:
                if Q(entry["b"]) != Q(row["baseline_action"]):
                    choices.setdefault(Q(entry["b"]), entry)
            ranked = sorted(choices.values(), key=lambda r: (-Q(r["certificate"]["gain_lower"]), Q(r["b"]), r["menu_index"]))[:2]
            selected = row["selected_common_menu"]
            self.require(len(selected) == len(ranked) or row["enhancement_failure"] is not None,
                         "Selected candidate census differs without retained failure")
            for candidate, common in zip(selected, ranked):
                self.require(candidate["menu_index"] == common["menu_index"] and Q(candidate["b"]) == Q(common["b"]),
                             "Joint solver changed the frozen two-candidate selector")
                if candidate.get("stage") != "completed":
                    self.require(row["enhancement_failure"] is not None and candidate.get("failure") is not None,
                                 "Incomplete candidate has no retained failure")
                    totals["incomplete_selected_candidates"] += 1
                    continue
                if row["mode"] == "joint_two":
                    upper = self.dual(row, candidate)
                    fused = Q(common["certificate"]["change_upper"])
                    self.require(Q(candidate["certificate"]["change_upper"]) == min(fused, upper),
                                 "Joint action contrast differs from rational safeguard")
                    self.require(Q(candidate["certificate"]["gain_lower"]) == -min(fused, upper)-DELTA,
                                 "Actual-future allowance omitted or changed")
                    totals["exact_dual_witnesses"] += 1
                    totals["duals_strictly_tighter_than_fused"] += upper < fused
                    totals["duals_equal_to_fused"] += upper == fused
                    totals["duals_weaker_than_fused"] += upper > fused
                    totals["single_anchor_duals"] += len(row["case"]["payloads"]) == 1
                    solver = candidate["dual_witness"]["solver"]
                    statuses[(solver.get("success"), solver.get("status"), solver.get("message"))] += 1
                else:
                    self.require(candidate["dual_witness"] is None and not candidate["dual_started"],
                                 "Fused comparator imported joint work")
                    self.require(candidate["certificate"] == common["certificate"],
                                 "Fused comparator certificate changed")
            self.require(row["dual_solves_started"] == sum(x["dual_started"] for x in selected)
                         and row["dual_solves_completed"] == sum(x["dual_completed"] for x in selected)
                         and row["dual_solver_successes"] == sum(bool(x["dual_witness"]["solver"]["success"])
                             for x in selected if x["dual_witness"] is not None), "Dual stage counts differ")
            # The frozen row records a sequential floating sum, not an exact sum.
            self.require(row["dual_seconds"] == sum(x["dual_elapsed_seconds"] for x in selected),
                         "Incomplete or complete dual elapsed work was dropped")
        timings = []
        fields = ("action_hex", "baseline_action_hex", "complete_policy_lower", "complete_policy_upper",
                  "original_optimum_lower", "loss", "width", "accepted_improvement",
                  "certified_policy_gain_lower", "selected_menu_index", "counts",
                  "dual_solves_started", "dual_solves_completed", "dual_solver_successes", "enhancement_failure")
        for repeat in range(3):
            rows = self.rows(f"results124/timing{repeat}/records124.jsonl")
            wanted = {key+(j,) for key in CELL_KEYS for j in range(4)}
            table = self.indexed(rows, observation, wanted, "464 timed decisions")
            for row in rows:
                self.compare(row, dict(source_commit=SOURCE, state_commit=DRAW, actor_commit=ACTORS,
                    repeat=repeat, population_observation=False,
                    state=self.states[row["row"]]["state"], state_hex=self.states[row["row"]]["hex"]), "timing.identity")
                for field in fields:
                    self.require(row[field] == lookup[observation(row)][field], "Timing changed a fixed decision: " + field)
            timings.append(table)
        totals["primary_decisions"] = len(primary)
        totals["timing_decisions"] = sum(len(x) for x in timings)
        paired_equal = 0
        for key in ACTOR_KEYS:
            for j in range(16):
                left, right = lookup[key+("fused_two",j)], lookup[key+("joint_two",j)]
                self.require(left["case"] == right["case"]
                             and left["full_common_menu"] == right["full_common_menu"],
                             "Paired services received different information or original candidate menus")
                paired_equal += left["action_hex"] == right["action_hex"]
        totals["joint_fused_action_pairs"] = 58*16
        totals["joint_fused_identical_final_actions"] = paired_equal
        hinge_counts = {}
        for name, table, n in [("primary", lookup,16)] + [(f"timing{j}",t,4) for j,t in enumerate(timings)]:
            count = 0
            for i in range(2):
                for budget in (5,9):
                    for loss in ("value","marginal"):
                        for service in SERVICES:
                            for j in range(n):
                                r = table[(i,budget,"relu",loss,service,j)]
                                h = table[(i,budget,"hinge",loss,service,j)]
                                for field in fields:
                                    self.require(r[field] == h[field], "ReLU/hinge declared decision differs: " + field)
                                count += 1
            hinge_counts[name] = count
        self.timings = timings
        audit_receipt = self.receipts["audit"][1]
        self.compare(audit_receipt, dict(status_detail="passed", primary_decisions=1856,
            timing_decisions=1392, dual_witnesses=totals["exact_dual_witnesses"],
            primary_sha256=self.hash_file("results124/primary/records124.jsonl"),
            original_economic_queries=0, production_optimizer_imported=False), "frozen.exact.audit")
        self.sections["decisions_and_duals"] = dict(totals=totals,
            solver_statuses=[dict(success=k[0], status=k[1], message=k[2], count=v) for k,v in statuses.items()],
            support_census=[dict(mode=k[0], paid_supports=k[1], rows=v) for k,v in support_counts.items()],
            relu_hinge_identical_decisions=hinge_counts,
            floating_solver_status_is_not_an_exact_certificate=True,
            exact_dual_validity_does_not_require_primal_feasibility=True)

    def independent(self):
        directory = self.root / "results124/independent"
        plan = self.obj(directory / "PLAN124.json")
        evaluations = self.rows(directory / "evaluations124.jsonl")
        claims = self.rows(directory / "claims124.jsonl")
        final_rows = self.rows(directory / "action_bounds124.jsonl")
        wanted = set()
        for row in self.primary:
            values = [row["action"], row["baseline_action"]]
            if row["raw_proposal_kept"] is not None:
                values.append(row["raw_proposal_kept"])
            values.extend(x["original_action"] for x in row["initial_support_certificates"])
            wanted.update(economic_key(row, action) for action in values)
        ordered = sorted(wanted)
        self.compare(plan, dict(primary_sha256=self.hash_file("results124/primary/records124.jsonl"),
            unique_action_keys=len(ordered), initial_bins=8, accepted_claim_ladder=[32,128],
            terminal_bisections=16), "independent.plan")
        self.require(normalized(ordered) == plan["ordered_keys"], "Independent action plan differs from complete original action set")
        table = self.indexed(evaluations, lambda r:(r["key_id"],r["bins"]),
                             {(r["key_id"],r["bins"]) for r in evaluations}, "unique saved independent evaluations")
        self.require(len(table) == len(evaluations), "Duplicate independent evaluation was hidden")
        eval_order = iter(evaluations)
        cache = {}
        best = {}
        consumed = 0
        def add(key, bins):
            nonlocal consumed
            kid = key_hash(key)
            if (kid,bins) in cache:
                return
            actual = next(eval_order)
            self.require(actual["key_id"] == kid and actual["bins"] == bins,
                         "Saved economic evaluation order differs from frozen complete ladder")
            self.require(economic_key(actual) == key and actual["action_hex"] == key[1]
                         and tuple(actual["state_hex"]) == key[0], "Economic evaluation identity differs")
            self.require(actual["terminal_steps"] == 16 and actual["terminal_contexts"] == 2*bins+1
                         and bins in (8,32,128), "Independent mesh or terminal budget changed")
            self.require(Q(actual["j_lower"]) == Q(actual["q_lower"])
                         and Q(actual["j_upper"])-Q(actual["q_upper"]) == DELTA
                         and Q(actual["future_controller_allowance_added_exactly_once"]) == DELTA,
                         "Original-future allowance was changed or applied twice")
            self.require(Q(actual["q_lower"]) <= Q(actual["q_upper"])
                         and Q(actual["optimum_lower"]) <= Q(actual["q_upper"]), "Independent interval order fails")
            tails = int(bins*(1-Q(actual["alpha"])))
            self.require(Q(actual["risk_bin_mass"]) == Q(1,tails)
                         and len(actual["risk_bin_indices"]) == len(set(actual["risk_bin_indices"])) == tails
                         and all(0 <= x < bins for x in actual["risk_bin_indices"]), "Original continuous risk density weights differ")
            action = Q(actual["action"])
            cap = Q(1,8)+sum(map(Q,actual["state"]))/16
            gradient, anchor = Q(actual["all_action_gradient"]), Q(actual["all_action_anchor"])
            displacement = max(-action,min(cap-action,-gradient/2))
            self.require(Q(actual["all_action_minimizer"]) == action+displacement
                         and Q(actual["optimum_lower"]) == anchor+gradient*displacement+displacement**2,
                         "Saved independent all-action lower-bound arithmetic differs")
            self.hash_file(directory / "witnesses" / f"{kid}-{bins}.jsonl.gz")
            cache[(kid,bins)] = actual
            candidates = [v for (k,_),v in cache.items() if k==kid]
            best[kid] = {f:(max if f.endswith("lower") else min)(Q(v[f]) for v in candidates)
                         for f in ("q_lower","q_upper","j_lower","j_upper","optimum_lower")}
            self.require(best[kid]["j_lower"] <= best[kid]["j_upper"], "Intersected independent bounds contradict")
            consumed += 1
        for key in ordered:
            add(key,8)
        accepted = [r for r in self.primary if r["accepted_improvement"]]
        self.require(len(claims) == len(accepted), "Accepted independent claim census differs")
        counters = collections.Counter()
        for row, claim in zip(accepted, claims):
            incumbent, candidate = economic_key(row,row["baseline_action"]), economic_key(row)
            ai,bi = key_hash(incumbent),key_hash(candidate)
            def verdict():
                a,b = best[ai],best[bi]
                low,high = a["j_lower"]-b["j_upper"],a["j_upper"]-b["j_lower"]
                gain = Q(row["certified_policy_gain_lower"])
                self.require(high >= gain, "Saved independent economics refutes a certified accepted gain")
                return dict(gain_lower=low,gain_upper=high,claimed_gain=gain,
                    claimed_gain_confirmed=low>=gain,
                    candidate_interval_contained=b["j_lower"]>=Q(row["complete_policy_lower"])
                        and b["j_upper"]<=Q(row["complete_policy_upper"]), independent_positive=low>0)
            current = verdict()
            levels=[]
            for bins in (32,128):
                if current["claimed_gain_confirmed"] and current["candidate_interval_contained"]:
                    break
                add(incumbent,bins)
                add(candidate,bins)
                levels.append(bins)
                current=verdict()
            self.compare(claim,dict(key=list(observation(row)),baseline_key_id=ai,candidate_key_id=bi,
                                    levels=levels,**current),"independent.claim")
            for field in ("claimed_gain_confirmed","candidate_interval_contained","independent_positive"):
                counters[field]+=current[field]
            counters["unresolved_claim_checks"] += not(current["claimed_gain_confirmed"] and current["candidate_interval_contained"])
        self.require(consumed == len(evaluations), "Unregistered extra economic evaluations remain")
        finals=self.indexed(final_rows,lambda r:r["key_id"],{key_hash(k) for k in ordered},"complete independent action bounds")
        for key in ordered:
            kid=key_hash(key);row=finals[kid]
            self.require(row["raw_initial"]==cache[(kid,8)],"Raw initial independent mesh was replaced")
            self.compare(row,dict(key=normalized(key),state=[float.fromhex(v) for v in key[0]],
                action=float.fromhex(key[1]),alpha=float.fromhex(key[2]),best=best[kid],
                bins_performed=sorted(bins for k,bins in cache if k==kid)),"independent.final")
        self.require({p.name for p in (directory/"witnesses").glob("*.jsonl.gz")} ==
                     {f"{kid}-{bins}.jsonl.gz" for kid,bins in cache},
                     "Independent witness census differs from the complete saved evaluation ladder")
        receipt=self.receipts["independent"][1]
        self.compare(receipt,dict(primary_sha256=self.hash_file("results124/primary/records124.jsonl"),
            unique_original_actions=len(ordered),action_mesh_evaluations=len(evaluations),accepted_changes=len(accepted),
            claimed_gains_confirmed=counters["claimed_gain_confirmed"],
            candidate_intervals_contained=counters["candidate_interval_contained"],
            unresolved_claim_checks=counters["unresolved_claim_checks"],terminal_bisections=16,
            initial_bins=8,claim_ladder=[32,128],unchanged_future_controller_allowance_added_once=True,
            rounded_terminal_controller_not_independently_replayed=True),"independent.receipt")
        self.independent_bounds={key:best[key_hash(key)] for key in ordered}
        self.sections["independent_economic_record_audit"]=dict(unique_actions=len(ordered),
            mesh_evaluations=len(evaluations),accepted_claims=len(accepted),claim_status_counts=counters,
            chronological_cache_and_ladder_reconstructed=True,raw_initial_intervals_preserved=True,
            all_witness_files_hashed=True,economic_primitives_reexecuted=False,
            scope="Arithmetic on saved independent original-q enclosures plus the single proved future-controller allowance; no direct rounded-controller replay.")

    def economics_and_inference(self):
        optima={}
        for key,b in self.independent_bounds.items():
            sr=(key[0],key[2])
            optima[sr]=max(optima.get(sr,b["optimum_lower"]),b["optimum_lower"])
        for row in self.primary:
            key=economic_key(row);sr=(key[0],key[2])
            optima[sr]=max(optima[sr],Q(row["original_optimum_lower"]))
        bounds={}
        for row in self.primary:
            key=economic_key(row);ib=self.independent_bounds[key]
            low=max(Q(row["complete_policy_lower"]),ib["j_lower"])
            high=min(Q(row["complete_policy_upper"]),ib["j_upper"])
            regret=min(TAU,high-optima[(key[0],key[2])])
            self.require(low<=high and regret>=0,"Joint original-objective interval contradicts its premises")
            bounds[observation(row)]=dict(lower=low,upper=high,regret=regret,raw=ib)
        policy=self.indexed(self.rows("results124/report/policy_cells124.jsonl"),lambda r:tuple(r["key"]),CELL_KEYS,"116 policy cells")
        safe=self.indexed(self.rows("results124/report/safe_gain_inference124.jsonl"),lambda r:tuple(r["key"]),CELL_KEYS,"116 safe-gain cells")
        safe_expected={};policy_expected={}
        cp_cache={}
        for k in CELL_KEYS:
            rs=[self.primary_lookup[k+(j,)] for j in range(16)]
            bb=[bounds[k+(j,)] for j in range(16)]
            reg=avg([v["regret"] for v in bb])
            fields=dict(key=k,mean_original_J_lower=avg([v["lower"] for v in bb]),
                mean_original_J_upper=avg([v["upper"] for v in bb]),mean_regret_upper=reg,
                accepted=sum(r["accepted_improvement"] for r in rs),
                failed_enhancements=sum(r["enhancement_failure"] is not None for r in rs),
                dual_solves=sum(r["dual_solves_started"] for r in rs),
                dual_solver_successes=sum(r["dual_solver_successes"] for r in rs),
                dual_seconds=sum((Q(r["dual_seconds"]) for r in rs),Q(0)),new_original_queries=0,
                all_qualified=all(r["qualified"] for r in rs),
                raw_independent_means=[avg([v["raw"]["j_lower"] for v in bb]),avg([v["raw"]["j_upper"] for v in bb])])
            self.compare(policy[k],fields,"policy.cell")
            root=policy[k]["rms_action_error_upper"]
            reconstructed_root=math.sqrt(float(reg))
            while Q(reconstructed_root)**2<reg:
                reconstructed_root=math.nextafter(reconstructed_root,math.inf)
            self.require(math.isfinite(root) and root>=0 and Q(root)**2>=reg,
                         "RMS action error display is not an outward upper bound")
            self.require(float(root).hex()==reconstructed_root.hex(),
                         "RMS action error display differs from the prescribed outward square root")
            policy_expected[k]=fields
            lows,highs=[],[]
            event_count=0
            for row,bound in zip(rs,bb):
                if row["action_hex"]==row["baseline_action_hex"]:
                    low=high=Q(0)
                else:
                    inc=self.independent_bounds[economic_key(row,row["baseline_action"])]
                    low=max(Q(0),Q(row["certified_policy_gain_lower"]),inc["j_lower"]-bound["upper"])
                    high=min(TAU,inc["j_upper"]-bound["lower"])
                self.require(low<=high,"Own-incumbent sample gain interval contradicts its premises")
                lows.append(low);highs.append(high)
                event_count+=Q(row["certified_policy_gain_lower"])>=EVENT
            if event_count not in cp_cache:
                cp_cache[event_count]=event_lower(event_count)
            cp=cp_cache[event_count]
            radius=5*TAU/8
            expected=dict(key=k,n=16,numerical_mean_lower=avg(lows),numerical_mean_upper=avg(highs),
                population_lower=max(Q(0),avg(lows)-radius,EVENT*cp),population_upper=min(TAU,avg(highs)+radius),
                hoeffding_radius=radius,threshold=EVENT,certified_threshold_count=event_count,
                threshold_probability_lower=cp,original_gain_support=[Q(0),TAU],
                independent_observation_unit="initial state")
            self.compare(safe[k],expected,"safe.gain.cell")
            safe_expected[k]=expected
        families=[]
        for k in CELL_KEYS:
            i,b,arm,loss,mode=k
            families.append((k,(i,0,"online","online","fused_two"),"same-risk-online-fused"))
            families.append((k,(i,b or 5,"quadratic","value","fused_two"),"same-budget-quadratic-value-fused"))
            if mode=="joint_two":
                families.append((k,k[:-1]+("fused_two",),"same-actor-joint-vs-fused"))
        signed=self.indexed(self.rows("results124/report/signed_inference124.jsonl"),
            lambda r:(tuple(r["key"]),tuple(r["comparator"]),r["label"]),families,"290 paired signed comparisons")
        signed_expected=[]
        for k,c,label in families:
            lows,highs=[],[]
            for j in range(16):
                first,second=self.primary_lookup[k+(j,)],self.primary_lookup[c+(j,)]
                if first["action_hex"]==second["action_hex"]:
                    low=high=Q(0)
                else:
                    a,b=bounds[k+(j,)],bounds[c+(j,)]
                    low=max(-TAU,b["lower"]-a["upper"])
                    high=min(TAU,b["upper"]-a["lower"])
                self.require(low<=high,"Paired sample interval contradicts its premises")
                lows.append(low);highs.append(high)
            radius=Q(0) if k==c else 5*TAU/4
            expected=dict(key=k,comparator=c,label=label,n=16,positive_means_first_method_lower_cost=True,
                numerical_mean_lower=avg(lows),numerical_mean_upper=avg(highs),
                population_lower=max(-TAU,avg(lows)-radius),population_upper=min(TAU,avg(highs)+radius),
                population_identity=k==c,sampling_radius=radius,sample_only_action_equality_not_population_identity=True)
            self.compare(signed[(k,c,label)],expected,"signed.comparison")
            self.require(expected["population_lower"]<=0<=expected["population_upper"],
                         "Prespecified broad signed population interval cannot exclude zero")
            signed_expected.append(expected)
        exp_lower=sum((Q(25,2)**j/math.factorial(j) for j in range(31)),Q(0))
        self.require(exp_lower>23200,"Exact Hoeffding-family exponential bound fails")
        self.bounds=bounds
        self.expected_safe=safe_expected
        self.expected_signed=signed_expected
        self.exp_lower=exp_lower
        self.sections["economic_report_arithmetic"]=dict(policy_cells=116,safe_gain_cells=116,
            threshold_event_cells=116,signed_comparisons=290,
            all_policy_means_exact=True,all_sample_gain_means_exact=True,
            all_probability_endpoints_exact=True,all_signed_means_and_intervals_exact=True,
            positive_safe_population_lower_bounds=sum(v["population_lower"]>0 for v in safe_expected.values()),
            positive_signed_population_lower_bounds=sum(v["population_lower"]>0 for v in signed_expected),
            negative_signed_population_upper_bounds=sum(v["population_upper"]<0 for v in signed_expected),
            exact_exponential_lower=exp_lower,conditional_joint_coverage_at_least="19/20",
            observation_units=16,observed_same_action_is_not_population_identity=True,
            signed_population_inability_to_rank_is_prespecified=True)

    def costs_and_menus(self):
        acquisition=self.rows(self.prior/"provenance123/inherited_costs121/fit_and_acquisition121.jsonl")
        charges=self.indexed(acquisition,lambda r:(r["index"],r["budget"],r["arm"],r["loss"]),
            [k for k in ACTOR_KEYS if k[2]!="online"],"56 inherited acquisition charges")
        for key,row in charges.items():
            i,b,a,l=key
            model=self.prior/f"vendor/2026-10-20-r121/results121/acquisition{b}-attempt01/models/{i}-{a}-{l}/model.json"
            self.require(row["model_sha256"]==self.hash_file(model),"Acquisition charge belongs to another actor")
            # Include label work, common residuals, own and matched-ReLU work.
            components=("label_phase_seconds","common_acquisition_residual_seconds",
                "common_training_audit_residual_seconds","own_model_phase_seconds",
                "own_required_training_audit_seconds","parent_relu_model_phase_seconds",
                "parent_relu_training_audit_seconds")
            self.require(all(Q(row[f])>=0 for f in components),"Negative inherited acquisition allocation")
            self.require(sum((Q(row[f]) for f in components),Q(0))==Q(row["complete_allocated_acquisition_seconds"]),
                         "Complete inherited acquisition allocation omitted a component")
        actual=self.indexed(self.rows("results124/report/clock_cells124.jsonl"),
            lambda r:(r["clock"],tuple(r["key"])),[(c,k) for c in range(4) for k in CELL_KEYS],"464 complete cost/economic cells")
        process_rows=self.indexed(self.rows("results124/report/process_clocks124.jsonl"),lambda r:r["clock"],range(4),"four saved process clocks")
        scenarios={}
        processes=[]
        for clock,name in enumerate(("primary","timing0","timing1","timing2")):
            cohort_rows=self.rows(f"results124/{name}/cohorts124.jsonl")
            cohorts=self.indexed(cohort_rows,cell,CELL_KEYS,"116 complete nonoverlapping cohorts")
            launch=f"launch-{name}"
            outer_start,outer_end=self.completed(launch)
            process=self.obj(f"results124/{launch}/PROCESS124.json")
            self.hash_file(f"results124/{launch}/stdout.log")
            self.require(process["returncode"]==0 and process["all_stdout_stderr_preserved"] is True,
                         "Incomplete external service clock")
            self.require(outer_start["started_unix"]<=self.receipts[name][0]["started_unix"]
                         <=self.receipts[name][1]["ended_unix"]<=outer_end["ended_unix"],
                         "External clock does not enclose its scientific process")
            total=Q(process["seconds"])
            cohort_total=sum((Q(c["seconds"]) for c in cohort_rows),Q(0))
            residual=total-cohort_total
            self.require(residual>=0,"Full process residual is negative")
            n=16 if clock==0 else 4
            expected_process=dict(clock=clock,n=n,process_seconds=total,cohort_seconds=cohort_total,
                standalone_residual_seconds=residual,
                receipt_sha256=self.hash_file(f"results124/{launch}/PROCESS124.json"))
            self.compare(process_rows[clock],expected_process,"process.clock")
            processes.append(expected_process)
            for k,c in cohorts.items():
                self.require(c["n"]==n and 0<=c["load_seconds"]<=c["seconds"],"Cohort load or state count differs")
                scientific_rows=self.primary_lookup if clock==0 else self.timings[clock-1]
                chosen=[scientific_rows[k+(j,)] for j in range(n)]
                summed_counts=collections.Counter()
                for row in chosen:
                    summed_counts.update(row["counts"])
                self.require(dict(summed_counts)==c["counts"],
                             "Complete cohort operation counts omit a saved decision")
                self.require(Q(c["seconds"])>=sum((Q(r["complete_seconds"]) for r in chosen),Q(0)),
                             "Complete cohort clock omits decision-service work")
                amount=Q(0) if k[2]=="online" else Q(charges[k[:4]]["complete_allocated_acquisition_seconds"])
                T,L=Q(c["seconds"]),Q(c["load_seconds"])
                bb=[self.bounds[k+(j,)] for j in range(n)]
                costs={str(v):amount+residual+L+Q(v,n)*(T-L) for v in VOLUMES}
                expected=dict(clock=clock,key=k,n=n,A=amount,H=residual,L=L,T=T,
                    mean_original_J_lower=avg([x["lower"] for x in bb]),
                    mean_original_J_upper=avg([x["upper"] for x in bb]),complete_cost_scenarios=costs,
                    economics_match_timed_states=True,large_volume_is_extrapolation=True)
                self.compare(actual[(clock,k)],expected,"clock.cell")
                scenarios[(clock,k)]=expected
        groups=(("primary",[0]),("timing1",[1]),("timing2",[2]),("timing3",[3]),("all-three-timings",[1,2,3]))
        all_menu_keys=[(k,v,g) for k in CELL_KEYS if k[2]=="relu" for v in VOLUMES for g,_ in groups]
        menus=self.indexed(self.rows("results124/report/price_menus124.jsonl"),
            lambda r:(tuple(r["key"]),r["volume"],r["clock_group"]),all_menu_keys,"320 complete neural purchase domains")
        menu_counts=collections.Counter()
        constraint_count=0
        for k,volume,group in all_menu_keys:
            clocks=dict(groups)[group]
            rivals=[c for c in CELL_KEYS if c[0]==k[0] and c[2]!="relu"]
            self.require(len(rivals)==50,"A conventional competitor was excluded")
            sufficient,optimistic=[],[]
            for clock in clocks:
                mine=scenarios[(clock,k)]
                for other in rivals:
                    theirs=scenarios[(clock,other)]
                    slope=mine["complete_cost_scenarios"][str(volume)]-theirs["complete_cost_scenarios"][str(volume)]
                    sufficient.append((volume*(mine["mean_original_J_upper"]-theirs["mean_original_J_lower"]),slope))
                    optimistic.append((volume*(mine["mean_original_J_lower"]-theirs["mean_original_J_upper"]),slope))
            s,o=price_interval(sufficient),price_interval(optimistic)
            self.compare(menus[(k,volume,group)],dict(key=k,volume=volume,clock_group=group,
                constraints=len(sufficient),sufficient=s,optimistic=o,population_adoption_claim=False),"price.domain")
            for label,domain in (("sufficient",s),("optimistic",o)):
                menu_counts[(group,label,"nonempty")]+=not domain["empty"]
                menu_counts[(group,label,"empty")]+=domain["empty"]
            constraint_count+=len(sufficient)
        self.scenarios,self.processes,self.menu_counts=scenarios,processes,menu_counts
        self.sections["cost_and_price_arithmetic"]=dict(saved_processes=4,cost_cells=464,
            exact_cost_scenarios=464*4,purchase_domains=len(menus),inequalities_per_endpoint_family=constraint_count,
            all_same_risk_conventional_competitors_per_clock=50,
            count_table=[dict(clock_group=k[0],endpoint_kind=k[1],status=k[2],count=v) for k,v in menu_counts.items()],
            measured_new_service_process_seconds=sum((p["process_seconds"] for p in processes),Q(0)),
            no_saved_service_clock_retimed=True,large_volume_scenarios_are_extrapolations=True,
            historical_unknown_research_work_remains_unknown=True,
            standalone_allocations_are_not_summed_as_actual_research_work=True)

    def summary(self):
        report=self.obj("results124/report/SUMMARY124.json")
        counted=self.sections["decisions_and_duals"]["totals"]
        wanted=dict(primary_decisions=1856,independent_states=16,policy_cells=116,
            accepted_changes=counted["accepted_actions"],
            joint_vs_fused_action_changes=counted["joint_fused_action_pairs"]-counted["joint_fused_identical_final_actions"],
            safe_mean_positive=sum(x["population_lower"]>0 for x in self.expected_safe.values()),
            signed_population_positive=sum(x["population_lower"]>0 for x in self.expected_signed),
            signed_population_negative=sum(x["population_upper"]<0 for x in self.expected_signed),
            full_three_clock_sufficient_nonempty=self.menu_counts[("all-three-timings","sufficient","nonempty")],
            full_three_clock_optimistic_nonempty=self.menu_counts[("all-three-timings","optimistic","nonempty")],
            inference_family=dict(coverage_at_least="19/20",safe_means=116,threshold_events=116,signed_comparisons=290,
                n=16,exact_exp_lower=self.exp_lower,hoeffding_exponent="25/2",failure_allocations=["1/100","1/100","3/100"]),
            independent_exact_dual_audit_sha256=self.hash_file("results124/audit/EXECUTION124.json"),
            research_new_service_process_seconds=sum((p["process_seconds"] for p in self.processes),Q(0)),
            historical_unknown_research_work_remains_unknown=True)
        self.compare(report,wanted,"report.summary")
        self.require(report["independent_economic_receipt"]==self.receipts["independent"][1]
                     and report["independent_exact_dual_audit_receipt"]==self.receipts["audit"][1],
                     "Report substituted a different independent receipt")
        terminal=self.receipts["report"][1]
        self.require(terminal["summary"]==report
                     and terminal["primary_sha256"]==self.hash_file("results124/primary/records124.jsonl"),
                     "Terminal reporter receipt does not bind its saved summary")
        failures=[]
        external_stages=[]
        for name in ("states","primary","timing0","timing1","timing2","audit","independent","report"):
            launch=self.root/f"results124/launch-{name}"
            if launch.exists():
                start,end=self.completed("launch-"+name)
                process=self.obj(launch/"PROCESS124.json")
                self.require(process["returncode"]==0 and process["all_stdout_stderr_preserved"] is True,
                             "A required recorded external stage is not terminal successful: "+name)
                self.require(start["started_unix"]<=self.receipts[name][0]["started_unix"]
                             <=self.receipts[name][1]["ended_unix"]<=end["ended_unix"],
                             "External stage does not enclose saved child: "+name)
                external_stages.append(dict(stage=name,seconds=Q(process["seconds"]),
                    process_receipt_sha256=self.hash_file(launch/"PROCESS124.json")))
        # Bind every actually present process log/receipt and failure without
        # treating a later success as erasure of an earlier failed attempt.
        for path in sorted((self.root/"results124").rglob("*")):
            if not path.is_file():
                continue
            if path.name in ("START124.json","EXECUTION124.json","PROCESS124.json","stdout.log","FAILURE124.json"):
                self.hash_file(path)
                if path.name=="FAILURE124.json":
                    failures.append(dict(path=str(path.relative_to(self.repo)),receipt=self.obj(path)))
        self.sections["reported_summary"]=wanted
        self.sections["failure_custody"]=dict(saved_stage_failures=failures,
            separately_measured_external_stage_clocks=external_stages,
            floating_optimizer_nonconvergence=self.sections["decisions_and_duals"]["solver_statuses"],
            source_publication_failures=self.sections["custody"]["preserved_source_publication_failures"],
            no_failure_removed_or_reclassified_as_success=True)

    def run(self):
        for method in (self.custody,self.decisions,self.independent,
                       self.economics_and_inference,self.costs_and_menus,self.summary):
            method()
            print(json.dumps(dict(stage=method.__name__,assertions=self.checks,inputs=len(self.inputs))),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output",type=Path,help="Defaults to provenance124/PUBLICATION_AUDIT124.json; exclusive create.")
    args=parser.parse_args()
    root=args.root.resolve()
    output=args.output.resolve() if args.output else root/"provenance124/PUBLICATION_AUDIT124.json"
    terminal=root/"results124/report/EXECUTION124.json"
    if not terminal.exists():
        raise SystemExit("No terminal R124 report is deposited; no publication audit receipt was written.")
    terminal_data=json.loads(terminal.read_bytes())
    if terminal_data.get("status")!="executed" or terminal_data.get("exit_code")!=0:
        raise SystemExit("R124 reporting has no successful terminal receipt; no publication success is asserted.")
    if output.exists():
        raise SystemExit("Publication audit receipt already exists; preserve it and choose a distinct --output for another attempt.")
    stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    attempt=root/"provenance124/publication-audit-attempts"/stamp
    attempt.mkdir(parents=True,exist_ok=False)
    tick=time.perf_counter()
    audit=Audit(root)
    started=dict(kind="post-execution independent publication arithmetic and custody audit",
        started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),argv=sys.argv,
        auditor_path=str(Path(__file__).resolve().relative_to(audit.repo)),
        auditor_sha256=sha_bytes(Path(__file__).read_bytes()),python=sys.version,
        source_commit=SOURCE,state_commit=DRAW,actor_commit=ACTORS,
        production_report_imported=False,scientific_source_modified=False,
        new_economic_evaluations=0,new_states=0,new_training=0,new_timing_processes=0)
    exclusive_json(attempt/"START124.json",started)
    try:
        audit.read(Path(__file__).resolve())
        audit.run()
        # Re-read every input immediately before the receipt.  Only unchanged
        # terminal records can support a durable publication audit result.
        for item in list(audit.inputs.values()):
            audit.read(audit.repo/item["path"])
        receipt=dict(status="passed",scope=started["kind"],started=started,
            ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),seconds=time.perf_counter()-tick,
            assertions=audit.checks,input_files=len(audit.inputs),inputs=sorted(audit.inputs.values(),key=lambda r:r["path"]),
            results=audit.sections,production_report_imported=False,economic_primitive_reexecution=False,
            new_economic_evaluations=0,new_states=0,new_training=0,new_timing_processes=0,
            remote_CI_success_asserted=False,whole_historical_research_program_complete=False,
            scientific_neural_superiority_asserted=False,
            independent_scope="Independent reconstruction from saved primary, timing and economic-enclosure records; every exact-dual bound is rechecked, but economic primitive evaluations are not repeated.")
        exclusive_json(attempt/"EXECUTION124.json",receipt)
        exclusive_json(output,receipt)
        print(json.dumps(dict(status="passed",assertions=audit.checks,output=str(output),
                              seconds=receipt["seconds"],input_files=len(audit.inputs))),flush=True)
    except BaseException:
        failure=dict(status="failed",started=started,seconds=time.perf_counter()-tick,
            assertions_completed=audit.checks,completed_sections=list(audit.sections),
            inputs=sorted(audit.inputs.values(),key=lambda r:r["path"]),traceback=traceback.format_exc(),
            partial_outputs_retained=True,publication_success_receipt_written=False)
        exclusive_json(attempt/"FAILURE124.json",failure)
        raise


if __name__=="__main__":
    main()
