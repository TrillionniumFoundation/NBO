#!/usr/bin/env python3
"""Deterministic audit for the R42 Econometrica numerical-methods review.

The script reads an extracted ``nbo-r42-from-primitives-science`` artifact,
checks the immutable service records and source digests, and recomputes the
review's core scalar, coupled, and precision comparisons. It does not rerun
training or replace any frozen clock. An extracted first-run artifact can be
provided to verify the disclosed pre-correction software failures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

EXPECTED_PUBLICATION_COMMIT = "70bf2db76bf7c873be0d8748a5cc120001f347aa"
EXPECTED_SERVICES = 150
EXPECTED_METHOD_COUNTS = {
    "scalar": {"direct-neural": 12, "spline": 12},
    "coupled": {
        "convex-neural": 6,
        "ridge-projection": 6,
        "quadratic-projection": 6,
    },
    "precision": {
        "fixed32-cached": 36,
        "fixed64-cached": 36,
        "adaptive-cached": 36,
    },
}
SEEDS = (104729, 130363, 155921)
PRICES = (1, 4)
THETAS = (0, 1)
QUERY_MARGIN = 0.005


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def crossing_time(crossing: dict[str, Any]) -> float:
    return float(crossing["seconds_through_checkpoint_fsync"])


def selected_attempt(record: dict[str, Any], target: str) -> dict[str, Any] | None:
    crossing = record["crossings"].get(target)
    if crossing is None:
        return None
    return record["attempts"][int(crossing["attempt"])]


def summarize(values: Iterable[float]) -> dict[str, float]:
    xs = list(values)
    if not xs:
        return {}
    return {
        "count": len(xs),
        "min": min(xs),
        "median": statistics.median(xs),
        "mean": statistics.mean(xs),
        "max": max(xs),
    }


def load_services(root: Path) -> tuple[dict[str, Any], list[tuple[dict[str, Any], dict[str, Any]]]]:
    publication = root / "results" / "publication"
    index = read_json(publication / "INDEX.json")
    if index["publication_source_commit"] != EXPECTED_PUBLICATION_COMMIT:
        raise AssertionError("unexpected R42 publication commit")
    if index["fixed_catalogue_size"] != EXPECTED_SERVICES or index["executed"] != EXPECTED_SERVICES:
        raise AssertionError("R42 catalogue is incomplete")
    if index["software_failures"] != 0:
        raise AssertionError("successful R42 catalogue reports software failures")

    source_hashes: dict[str, str] = {}
    loaded: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for service in index["services"]:
        sid = int(service["id"])
        directory = publication / f"service-{sid:03d}"
        record_path = directory / "record.json"
        record = read_json(record_path)
        expected_record_hash = service["clock"]["record_sha256"]
        if sha256(record_path) != expected_record_hash:
            raise AssertionError(f"record digest mismatch for service {sid}")
        if service["exit_code"] != 0 or service["clock"]["status"] != "completed":
            raise AssertionError(f"service {sid} did not complete")
        for name, digest in service["clock"]["source_sha256"].items():
            old = source_hashes.setdefault(name, digest)
            if old != digest:
                raise AssertionError(f"inconsistent source digest for {name}")
        loaded.append((service, record))

    for name, digest in source_hashes.items():
        path = root / "code" / name
        if sha256(path) != digest:
            raise AssertionError(f"source digest mismatch for {name}")
    return index, loaded


def method_counts(rows: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, dict[str, int]]:
    out: dict[str, Counter[str]] = {
        "scalar": Counter(),
        "coupled": Counter(),
        "precision": Counter(),
    }
    for service, _record in rows:
        spec = service["spec"]
        if spec["kind"] == "precision":
            out["precision"][spec["service"]["method"]] += 1
        else:
            out[spec["kind"]][spec["method"]] += 1
    result = {kind: dict(counts) for kind, counts in out.items()}
    if result != EXPECTED_METHOD_COUNTS:
        raise AssertionError(f"unexpected method catalogue: {result}")
    return result


def scalar_audit(rows: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    scalar = [(s, r) for s, r in rows if s["spec"]["kind"] == "scalar"]
    by_method: dict[str, Any] = {}
    for method in ("direct-neural", "spline"):
        subset = [(s, r) for s, r in scalar if s["spec"]["method"] == method]
        by_method[method] = {
            "successes": {
                target: sum(r["crossings"][target] is not None for _s, r in subset)
                for target in ("0.06", "0.04")
            },
            "time_to_target": {
                target: summarize(
                    crossing_time(r["crossings"][target])
                    for _s, r in subset
                    if r["crossings"][target] is not None
                )
                for target in ("0.06", "0.04")
            },
            "final_all_state_gap": summarize(r["accepted_global_bound"] for _s, r in subset),
        }

    matched_gap_ratios: list[float] = []
    for price in PRICES:
        for theta in THETAS:
            for seed in SEEDS:
                neural = next(
                    r for s, r in scalar
                    if s["spec"]["method"] == "direct-neural"
                    and s["spec"]["price"] == price
                    and s["spec"]["theta"] == theta
                    and s["spec"]["seed"] == seed
                )
                spline = next(
                    r for s, r in scalar
                    if s["spec"]["method"] == "spline"
                    and s["spec"]["price"] == price
                    and s["spec"]["theta"] == theta
                    and s["spec"]["seed"] == seed
                )
                matched_gap_ratios.append(neural["accepted_global_bound"] / spline["accepted_global_bound"])

    direct_comparisons: dict[str, Any] = {}
    for target in ("0.06", "0.04"):
        signs = Counter()
        intervals: list[tuple[float, float]] = []
        for price in PRICES:
            for theta in THETAS:
                for seed in SEEDS:
                    neural = next(
                        r for s, r in scalar
                        if s["spec"]["method"] == "direct-neural"
                        and s["spec"]["price"] == price
                        and s["spec"]["theta"] == theta
                        and s["spec"]["seed"] == seed
                    )
                    spline = next(
                        r for s, r in scalar
                        if s["spec"]["method"] == "spline"
                        and s["spec"]["price"] == price
                        and s["spec"]["theta"] == theta
                        and s["spec"]["seed"] == seed
                    )
                    na = selected_attempt(neural, target)
                    sa = selected_attempt(spline, target)
                    if na is None or sa is None:
                        continue
                    nl = na["own_policy_values"]["lower"]
                    nu = na["own_policy_values"]["upper"]
                    sl = sa["own_policy_values"]["lower"]
                    su = sa["own_policy_values"]["upper"]
                    for i in range(len(nl)):
                        lo = float(nl[i]) - float(su[i])
                        hi = float(nu[i]) - float(sl[i])
                        intervals.append((lo, hi))
                        if lo > 0:
                            signs["neural_higher_cost"] += 1
                        elif hi < 0:
                            signs["neural_lower_cost"] += 1
                        else:
                            signs["overlap"] += 1
                        if lo >= -QUERY_MARGIN and hi <= QUERY_MARGIN:
                            signs["inside_prespecified_margin"] += 1
        direct_comparisons[target] = {
            "intervals": len(intervals),
            "signs": dict(signs),
            "lower_min": min((x[0] for x in intervals), default=None),
            "upper_max": max((x[1] for x in intervals), default=None),
        }

    return {
        "methods": by_method,
        "matched_neural_to_spline_gap_ratio": summarize(matched_gap_ratios),
        "direct_neural_minus_spline_cost": direct_comparisons,
        "conventional_labels_used_by_neural": sum(r["conventional_training_labels"] for s, r in scalar if s["spec"]["method"] == "direct-neural"),
        "inherited_weights_used_by_neural": sum(r["inherited_weights"] for s, r in scalar if s["spec"]["method"] == "direct-neural"),
        "spline_fallbacks_used_by_neural": sum(r["spline_fallbacks"] for s, r in scalar if s["spec"]["method"] == "direct-neural"),
    }


def coupled_audit(rows: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    coupled = [(s, r) for s, r in rows if s["spec"]["kind"] == "coupled"]
    methods: dict[str, Any] = {}
    for method in ("convex-neural", "ridge-projection", "quadratic-projection"):
        subset = [(s, r) for s, r in coupled if s["spec"]["method"] == method]
        methods[method] = {
            "successes": {
                target: sum(r["crossings"][target] is not None for _s, r in subset)
                for target in ("0.25", "0.1")
            },
            "time_to_target": {
                target: summarize(
                    crossing_time(r["crossings"][target])
                    for _s, r in subset
                    if r["crossings"][target] is not None
                )
                for target in ("0.25", "0.1")
            },
            "final_all_state_gap": summarize(r["all_state_gap"] for _s, r in subset),
            "training_seconds": summarize(r["training_seconds"] for _s, r in subset),
        }

    matched: dict[str, Any] = {}
    for target in ("0.25", "0.1"):
        counts = Counter()
        time_ratios: list[float] = []
        for price in PRICES:
            for seed in SEEDS:
                neural = next(
                    r for s, r in coupled
                    if s["spec"]["method"] == "convex-neural"
                    and s["spec"]["price"] == price
                    and s["spec"]["seed"] == seed
                )
                ridge = next(
                    r for s, r in coupled
                    if s["spec"]["method"] == "ridge-projection"
                    and s["spec"]["price"] == price
                    and s["spec"]["seed"] == seed
                )
                if neural["all_state_gap"] < ridge["all_state_gap"]:
                    counts["neural_tighter_final_gap"] += 1
                elif neural["all_state_gap"] > ridge["all_state_gap"]:
                    counts["ridge_tighter_final_gap"] += 1
                else:
                    counts["equal_final_gap"] += 1
                nc = neural["crossings"][target]
                rc = ridge["crossings"][target]
                if nc is not None and rc is not None:
                    ratio = crossing_time(nc) / crossing_time(rc)
                    time_ratios.append(ratio)
                    counts["neural_faster_to_target" if ratio < 1 else "ridge_faster_to_target"] += 1
                elif nc is not None:
                    counts["only_neural_reached_target"] += 1
                elif rc is not None:
                    counts["only_ridge_reached_target"] += 1
                else:
                    counts["neither_reached_target"] += 1
        matched[target] = {"counts": dict(counts), "neural_to_ridge_time_ratio": summarize(time_ratios)}

    neural = [r for s, r in coupled if s["spec"]["method"] == "convex-neural"]
    ridge = [r for s, r in coupled if s["spec"]["method"] == "ridge-projection"]
    return {
        "methods": methods,
        "matched_neural_vs_ridge": matched,
        "neural_hidden_weight_change": summarize(
            n["hidden_weight_change"] for r in neural for n in r["networks"]
        ),
        "neural_training_max_error": summarize(
            n["training_max_error"] for r in neural for n in r["networks"]
        ),
        "final_scalar_storage": {
            "neural": summarize(r["attempts"][-1]["neural_scalar_storage"] for r in neural),
            "ridge": summarize(r["attempts"][-1]["neural_scalar_storage"] for r in ridge),
        },
        "direct_neural_minus_ridge_policy_value_intervals_present": False,
    }


def precision_audit(rows: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    precision = [(s, r) for s, r in rows if s["spec"]["kind"] == "precision"]
    methods: dict[str, Any] = {}
    for method in ("fixed32-cached", "fixed64-cached", "adaptive-cached"):
        subset = [(s, r) for s, r in precision if s["spec"]["service"]["method"] == method]
        work = {
            bits: {key: 0 for key in ("attempts", "accepted", "rejected", "multiply_adds")}
            for bits in ("32", "64")
        }
        for _s, record in subset:
            for bits in ("32", "64"):
                for key in work[bits]:
                    work[bits][key] += int(record["precision_work"][bits][key])
        methods[method] = {
            "certified": sum(bool(record["certified"]) for _s, record in subset),
            "services": len(subset),
            "seconds_through_fsync": summarize(s["clock"]["seconds_through_fsync"] for s, _r in subset),
            "seconds_sum": sum(float(s["clock"]["seconds_through_fsync"]) for s, _r in subset),
            "precision_work": work,
        }

    pairs: list[float] = []
    by_object: dict[str, list[float]] = {}
    for service, _record in precision:
        spec = service["spec"]
        if spec["service"]["method"] != "adaptive-cached":
            continue
        name = spec["service"]["name"]
        repeat = spec["repeat"]
        fixed = next(
            other for other, _r in precision
            if other["spec"]["service"]["method"] == "fixed64-cached"
            and other["spec"]["service"]["name"] == name
            and other["spec"]["repeat"] == repeat
        )
        ratio = float(service["clock"]["seconds_through_fsync"]) / float(fixed["clock"]["seconds_through_fsync"])
        pairs.append(ratio)
        by_object.setdefault(name, []).append(ratio)
    medians = [statistics.median(xs) for xs in by_object.values()]
    adaptive_sum = methods["adaptive-cached"]["seconds_sum"]
    fixed64_sum = methods["fixed64-cached"]["seconds_sum"]
    return {
        "methods": methods,
        "adaptive_vs_fixed64": {
            "pairs": len(pairs),
            "adaptive_faster": sum(x < 1 for x in pairs),
            "adaptive_slower": sum(x > 1 for x in pairs),
            "ratio": summarize(pairs),
            "aggregate_time_percent_change": 100.0 * (adaptive_sum / fixed64_sum - 1.0),
            "object_median_faster": sum(x < 1 for x in medians),
            "object_median_slower": sum(x > 1 for x in medians),
            "object_median_ratio": summarize(medians),
        },
    }


def first_run_audit(root: Path | None) -> dict[str, Any] | None:
    if root is None:
        return None
    index = read_json(root / "results" / "publication" / "INDEX.json")
    failures = []
    for service in index["services"]:
        if service["exit_code"] != 0 or service["clock"]["status"] != "completed":
            failures.append({
                "id": service["id"],
                "spec": service["spec"],
                "error_tail": (service["clock"].get("error") or "").splitlines()[-1:],
            })
    return {
        "executed": index["executed"],
        "fixed_catalogue_size": index["fixed_catalogue_size"],
        "software_failures": index["software_failures"],
        "failure_count_recomputed": len(failures),
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_root", type=Path, help="Extracted successful R42 artifact root")
    parser.add_argument("--first-run-root", type=Path, default=None, help="Optional extracted first-run artifact root")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    index, rows = load_services(args.artifact_root)
    result = {
        "status": "passed",
        "reviewed_science_snapshot": {
            "branch": "revision/econometrica-nbo-r42-source-2026-10-07",
            "commit": EXPECTED_PUBLICATION_COMMIT,
            "tree": "661afa45b698a6f928f39d2d1ff7977764044b37",
            "workflow_run_id": 37581511628,
            "artifact_id": 11465997076,
            "artifact_sha256": "540f80f65c27b9998b2a54375f79413f1a1f3d82bd04e50b810dba6dfed607cc",
        },
        "catalogue": {
            "fixed": index["fixed_catalogue_size"],
            "executed": index["executed"],
            "software_failures": index["software_failures"],
            "method_counts": method_counts(rows),
            "source_hashes_verified": len(index["services"][0]["clock"]["source_sha256"]),
            "record_hashes_verified": len(rows),
        },
        "scalar": scalar_audit(rows),
        "coupled": coupled_audit(rows),
        "precision": precision_audit(rows),
        "first_run": first_run_audit(args.first_run_root),
        "scope": [
            "The script audits frozen records and arithmetic; it does not rerun training or retime services.",
            "Service clocks are descriptive single-machine observations, not a hardware-general sampling distribution.",
            "Separate all-state regret bounds are not direct neural-versus-ridge policy-value comparisons.",
            "The R42 branch contains science and protocol additions but no rematerialized R42 article, supplement, response, or release PDF.",
        ],
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
