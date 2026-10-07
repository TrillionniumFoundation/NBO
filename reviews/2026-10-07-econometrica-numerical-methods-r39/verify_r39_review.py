#!/usr/bin/env python3
"""Independent deterministic audit for the R39 NBO referee report.

This script reads only committed repository files. It does not rerun or
retime the 315 economic services. It verifies publication hashes, the frozen
service ledger and raw-record hashes, and reproduces the numerical comparisons
used in the report. It also performs an exact rational spot check of the
Newton--Schulz Gram identity used by the precision-refresh proof.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import statistics
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

REVIEWED_BRANCH = "revision/econometrica-nbo-r39-review-ready-2026-10-07"
REVIEWED_COMMIT = "f472a7c21f2f9db5285f1bf7746edf2d9463638e"
REVIEWED_TREE = "c7837c55b507b3e50eed6af0bca13444b968fc06"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def median(values: Iterable[float]) -> float:
    vals = list(values)
    if not vals:
        raise AssertionError("median requested for an empty collection")
    return float(statistics.median(vals))


def stable_spec(spec: dict[str, Any], *, drop_method: bool = False) -> str:
    obj = json.loads(json.dumps(spec))
    obj.pop("replicate", None)
    if drop_method:
        obj.pop("method", None)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def mm(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    if len(a[0]) != len(b):
        raise AssertionError("incompatible matrix product")
    return [[sum((x * y for x, y in zip(row, col)), Fraction())
             for col in zip(*b)] for row in a]


def tr(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(col) for col in zip(*a)]


def add(a: list[list[Fraction]], b: list[list[Fraction]], scale: Fraction = Fraction(1)) -> list[list[Fraction]]:
    return [[x + scale * y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def smul(a: list[list[Fraction]], s: Fraction) -> list[list[Fraction]]:
    return [[s * x for x in row] for row in a]


def eye(n: int, s: Fraction = Fraction(1)) -> list[list[Fraction]]:
    return [[s if i == j else Fraction() for j in range(n)] for i in range(n)]


def newton_schulz_identity() -> bool:
    y = [
        [Fraction(1), Fraction(1, 4)],
        [Fraction(1, 3), Fraction(1)],
        [Fraction(1, 5), Fraction(-1, 7)],
    ]
    c = mm(tr(y), y)
    e = add(c, eye(2), Fraction(-1))
    ybar = smul(mm(y, add(smul(eye(2), Fraction(3)), c, Fraction(-1))), Fraction(1, 2))
    lhs = add(mm(tr(ybar), ybar), eye(2), Fraction(-1))
    e2 = mm(e, e)
    rhs = smul(add(smul(e2, Fraction(-3)), mm(e2, e)), Fraction(1, 4))
    return lhs == rhs


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="Repository root; defaults to the script's repository root")
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional JSON output path")
    args = parser.parse_args()

    root = args.repo_root.resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    r39 = root / "revisions/2026-10-07-r39"
    r38 = root / "revisions/2026-10-07-r38"
    run = r38 / "results/run-1"

    required = [
        r39 / "audit/FILES_SHA256.json",
        r39 / "audit/R39_AUDIT.json",
        r39 / "audit/RELEASE_AUDIT.json",
        r38 / "protocols/PROTOCOL.json",
        run / "EXECUTIONS.json",
    ]
    missing = [str(p.relative_to(root)) for p in required if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"missing required repository files: {missing}")

    manifest = load(r39 / "audit/FILES_SHA256.json")
    publication_mismatches: list[dict[str, str]] = []
    for rel, expected in manifest.items():
        path = root / rel
        actual = sha256(path) if path.is_file() else "MISSING"
        if actual != expected:
            publication_mismatches.append({"path": rel, "expected": expected, "actual": actual})

    release = load(r39 / "audit/RELEASE_AUDIT.json")
    compilation = {row["document"]: row for row in release["compilation"]}
    active_docs = {name: compilation[name] for name in ("ECTA", "supp", "applications", "response")}
    active_compilation_clean = all(
        not row["undefined_references"]
        and not row["duplicate_labels"]
        and not row["missing_characters"]
        and row["overfull_hboxes"] == 0
        and row["overfull_vboxes"] == 0
        for row in active_docs.values()
    )

    executions = load(run / "EXECUTIONS.json")
    warmups = [row for row in executions if row["id"] == "warmup"]
    services = [row for row in executions if row["id"] != "warmup"]
    if len(warmups) != 1:
        raise AssertionError(f"expected one warmup, found {len(warmups)}")

    records: dict[str, dict[str, Any]] = {}
    raw_mismatches: list[dict[str, str]] = []
    for row in executions:
        path = run / "raw" / f"{row['id']}.json"
        actual = sha256(path) if path.is_file() else "MISSING"
        expected = row["clock"]["record_sha256"]
        if actual != expected:
            raw_mismatches.append({"id": row["id"], "expected": expected, "actual": actual})
        if row["id"] != "warmup":
            records[row["id"]] = load(path)

    kind_counts = collections.Counter(row["specification"]["kind"] for row in services)
    method_counts = collections.Counter(
        row["specification"].get("method", "") for row in services
        if row["specification"]["kind"] == "policy"
    )

    adaptive: dict[str, Any] = {}
    for method in ("adaptive-cached", "adaptive-uncached"):
        rows = [row for row in services if row["specification"].get("method") == method]
        updates = native32 = native64 = rejected = 0
        used_precisions: collections.Counter[int] = collections.Counter()
        for row in rows:
            trial = records[row["id"]]["trials"][-1]
            counts = trial["counts"]
            updates += int(counts["updates"])
            native32 += int(counts["native32_updates"])
            native64 += int(counts["native64_updates"])
            for step in trial["steps"]:
                used_precisions[int(step["precision"])] += 1
                rejected += len(step.get("rejected_precisions", []))
        adaptive[method] = {
            "services": len(rows),
            "updates": updates,
            "native32_updates": native32,
            "native64_updates": native64,
            "rejected_precision_attempts": rejected,
            "used_precisions": dict(sorted(used_precisions.items())),
        }

    tuned_rows = [row for row in services if row["specification"].get("method") == "tuned-cached"]
    tuned_selection = collections.Counter(records[row["id"]]["selected_method"] for row in tuned_rows)
    tuned_trial_counts = collections.Counter(len(records[row["id"]]["trials"]) for row in tuned_rows)

    by_rep: dict[tuple[str, int], dict[str, dict[str, Any]]] = collections.defaultdict(dict)
    for row in services:
        method = row["specification"].get("method")
        if method:
            by_rep[(stable_spec(row["specification"], drop_method=True),
                    int(row["specification"].get("replicate", 0)))][method] = row

    matched_pairs = matched_exact = 0
    signature_fields = (
        "certified", "policy_gap_upper", "requested_policy_tolerance", "slack",
        "minimum_domain_margin", "checkpoints", "counts", "steps", "error",
    )
    for methods in by_rep.values():
        if "adaptive-cached" not in methods or "tuned-cached" not in methods:
            continue
        matched_pairs += 1
        a = records[methods["adaptive-cached"]["id"]]["trials"][-1]
        t = records[methods["tuned-cached"]["id"]]["trials"][-1]
        if all(a.get(field) == t.get(field) for field in signature_fields):
            matched_exact += 1

    policy_objects: dict[str, dict[str, list[float]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    for row in services:
        spec = row["specification"]
        if spec["kind"] == "policy":
            policy_objects[stable_spec(spec, drop_method=True)][spec["method"]].append(
                float(row["clock"]["service_through_fsync_seconds"])
            )

    structural_faster = 0
    structural_ratios: list[float] = []
    factor_winners: collections.Counter[str] = collections.Counter()
    adaptive_cached_faster_than_fixed = 0
    adaptive_uncached_faster_than_fixed = 0
    for methods in policy_objects.values():
        med = {method: median(times) for method, times in methods.items()}
        factors = {method: value for method, value in med.items() if method != "structural"}
        best = min(factors, key=factors.get)
        factor_winners[best] += 1
        ratio = factors[best] / med["structural"]
        structural_ratios.append(ratio)
        structural_faster += int(med["structural"] < factors[best])
        adaptive_cached_faster_than_fixed += int(med["adaptive-cached"] < med["fixed64-cached"])
        adaptive_uncached_faster_than_fixed += int(med["adaptive-uncached"] < med["fixed64-uncached"])

    baseline_times: dict[str, float] = {}
    for key, methods in policy_objects.items():
        spec = json.loads(key)
        if spec.get("name") == "accuracy-0.0001":
            baseline_times = {method: median(times) for method, times in methods.items()}
            break

    neural: dict[tuple[float, float, int], tuple[dict[str, Any], dict[str, Any]]] = {}
    spline: dict[tuple[float, float, int], tuple[dict[str, Any], dict[str, Any]]] = {}
    for row in services:
        spec = row["specification"]
        if spec["kind"] not in ("neural", "nonlinear"):
            continue
        key = (float(spec["price"]), float(spec["theta"]), int(spec["replicate"]))
        target = neural if spec["kind"] == "neural" else spline
        target[key] = (row, records[row["id"]])

    nonlinear_time_ratios: list[float] = []
    neural_gap_larger = 0
    neural_cost_strictly_higher = neural_cost_strictly_lower = cost_intervals_overlap = 0
    price4_higher = price4_lower = price4_overlap = 0
    economies = sorted({(price, theta) for price, theta, _ in neural})
    for price, theta in economies:
        nrows = [neural[(price, theta, rep)] for rep in range(3)]
        srows = [spline[(price, theta, rep)] for rep in range(3)]
        ntime = median(item[0]["clock"]["service_through_fsync_seconds"] for item in nrows)
        stime = median(item[0]["clock"]["service_through_fsync_seconds"] for item in srows)
        nonlinear_time_ratios.append(ntime / stime)
        nrecord = nrows[0][1]
        srecord = srows[0][1]
        neural_gap_larger += int(
            float(nrecord["candidate"]["policy_gap_upper"])
            > float(srecord["candidate"]["policy_gap_upper"])
        )
        nvals = nrecord["own_policy_values"]
        svals = srecord["own_policy_values"]
        for nl, nu, sl, su in zip(nvals["lower"], nvals["upper"], svals["lower"], svals["upper"]):
            if float(nl) > float(su):
                neural_cost_strictly_higher += 1
                outcome = "higher"
            elif float(nu) < float(sl):
                neural_cost_strictly_lower += 1
                outcome = "lower"
            else:
                cost_intervals_overlap += 1
                outcome = "overlap"
            if price == 4.0:
                if outcome == "higher":
                    price4_higher += 1
                elif outcome == "lower":
                    price4_lower += 1
                else:
                    price4_overlap += 1

    audit = load(r39 / "audit/R39_AUDIT.json")
    network_bounds = [float(row["new_upper"]) for row in audit["network_bounds"]]
    counterfactual_lowers: dict[str, list[float]] = {"neural": [], "nonlinear": []}
    for group in audit["groups"]:
        cf = group.get("counterfactual")
        if cf and group.get("kind") in counterfactual_lowers:
            counterfactual_lowers[group["kind"]].extend(float(x) for x in cf["improvement_lower"])

    identity_ok = newton_schulz_identity()

    result = {
        "reviewed_snapshot": {
            "branch": REVIEWED_BRANCH,
            "commit": REVIEWED_COMMIT,
            "tree": REVIEWED_TREE,
        },
        "status": "passed" if not publication_mismatches and not raw_mismatches and identity_ok else "failed",
        "publication": {
            "manifest_entries_verified": len(manifest),
            "hash_mismatches": publication_mismatches,
            "active_compilation_clean": active_compilation_clean,
            "active_pages": {name: int(row["pages"]) for name, row in active_docs.items()},
        },
        "evidence": {
            "services": len(services),
            "warmups": len(warmups),
            "raw_record_hash_mismatches": raw_mismatches,
            "kind_counts": dict(sorted(kind_counts.items())),
            "policy_method_counts": dict(sorted(method_counts.items())),
        },
        "precision_mechanism": {
            "adaptive": adaptive,
            "combined_adaptive_updates": sum(row["updates"] for row in adaptive.values()),
            "combined_native64_updates": sum(row["native64_updates"] for row in adaptive.values()),
            "combined_rejected_precision_attempts": sum(row["rejected_precision_attempts"] for row in adaptive.values()),
            "tuned_selected_methods": dict(tuned_selection),
            "tuned_trial_counts": {str(k): v for k, v in sorted(tuned_trial_counts.items())},
            "adaptive_cached_tuned_pairs": matched_pairs,
            "pairs_with_identical_certificate_path": matched_exact,
        },
        "quadratic_work": {
            "policy_objects": len(policy_objects),
            "structural_faster_than_best_factor": structural_faster,
            "best_factor_over_structural_ratio": {
                "min": min(structural_ratios),
                "median": median(structural_ratios),
                "max": max(structural_ratios),
            },
            "factor_method_winners": dict(factor_winners),
            "adaptive_cached_faster_than_fixed64_cached": adaptive_cached_faster_than_fixed,
            "adaptive_uncached_faster_than_fixed64_uncached": adaptive_uncached_faster_than_fixed,
            "epsilon_1e-4_median_service_seconds": dict(sorted(baseline_times.items())),
        },
        "nonlinear_comparison": {
            "economies": len(economies),
            "neural_slower_than_spline": sum(ratio > 1 for ratio in nonlinear_time_ratios),
            "neural_over_spline_time_ratio": {
                "min": min(nonlinear_time_ratios),
                "median": median(nonlinear_time_ratios),
                "max": max(nonlinear_time_ratios),
            },
            "neural_policy_gap_larger": neural_gap_larger,
            "displayed_state_economy_intervals": {
                "neural_cost_strictly_higher": neural_cost_strictly_higher,
                "neural_cost_strictly_lower": neural_cost_strictly_lower,
                "overlap": cost_intervals_overlap,
            },
            "price_4_intervals": {
                "neural_cost_strictly_higher": price4_higher,
                "neural_cost_strictly_lower": price4_lower,
                "overlap": price4_overlap,
            },
        },
        "endpoint_and_counterfactual_checks": {
            "network_records": int(audit["network_checks"]),
            "unique_networks": int(audit["unique_networks"]),
            "rational_endpoint_checks": int(audit["rational_endpoint_checks_passed"]),
            "uniform_network_error_range": {"min": min(network_bounds), "max": max(network_bounds)},
            "old_rule_reoptimization": {
                kind: {
                    "positive_lower_endpoints": sum(x > 0 for x in values),
                    "lower_endpoint_range": {"min": min(values), "max": max(values)},
                }
                for kind, values in counterfactual_lowers.items()
            },
        },
        "algebra": {
            "newton_schulz_rectangular_noncommuting_gram_identity_exact": identity_ok,
        },
        "scope": [
            "Committed deterministic records were audited; the 315 economic services were not rerun or retimed.",
            "Timing comparisons are descriptive medians of three frozen clocks per deterministic object, not population or hardware-general inference.",
            "The cost-interval comparison uses the displayed policy-evaluation enclosures and does not claim exact ordering when intervals overlap.",
            "The exact matrix identity is a central algebraic spot check, not an independent proof of every theorem in the manuscript.",
        ],
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    if result["status"] != "passed":
        raise SystemExit(1)
    return result


if __name__ == "__main__":
    main()
