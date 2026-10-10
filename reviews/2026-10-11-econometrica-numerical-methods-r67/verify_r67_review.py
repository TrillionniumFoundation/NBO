#!/usr/bin/env python3
"""Independent deterministic audit for the NBO R67 referee review.

Usage:
    python verify_r67_review.py /path/to/nbo-r67-publication-and-audits.zip \
        [--output verification_results.json]

The script uses only the Python standard library.  It verifies the frozen
publication artifact digest, parses the committed audit records, recomputes the
principal cold-start, reuse, policy-cost, and vector-horizon comparisons, and
writes a machine-readable summary.  It does not rerun fitting, Bellman queries,
policy simulation, LaTeX, or wall-clock experiments.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import math
import statistics
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable

EXPECTED_ARTIFACT_SHA256 = "d7f9274c3dca3697e95b22bb62d6d9df14ed0d677859033e0a4850584d8d031b"
EXPECTED_BRANCH = "revision/econometrica-nbo-r67-review-ready-2026-10-10"
EXPECTED_COMMIT = "eacd3e217ae1e2e9ea6e154b48da7d103159d051"
EXPECTED_TREE = "57db1bd03f307e19146635b7b37cce3a1c707ccc"
EXPECTED_WORKFLOW_RUN = 38063998843
EXPECTED_ARTIFACT_ID = 11674836596


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(zf: zipfile.ZipFile, name: str) -> Any:
    try:
        raw = zf.read(name)
    except KeyError as exc:
        raise AssertionError(f"artifact is missing required member: {name}") from exc
    return json.loads(raw.decode("utf-8"))


def median(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        raise AssertionError("cannot take median of empty values")
    return float(statistics.median(values))


def warning_count(summary: dict[str, Any]) -> int:
    total = 0
    for date in summary.get("training", {}).get("dates", []):
        total += len(date.get("warnings", []))
    for arm in summary.get("arms", []):
        for date in arm.get("training", {}).get("dates", []):
            total += len(date.get("warnings", []))
    return total


def task_key(summary: dict[str, Any]) -> tuple[int, int, str]:
    spec = summary["spec"]
    return int(spec["d"]), int(spec["T"]), str(spec["target"])


def cold_summary(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [s for s in summaries if s["spec"]["group"] == "comparison"]
    by_task: dict[str, Any] = {}
    for task in sorted({task_key(s) for s in rows}):
        d, T, target = task
        task_rows = [s for s in rows if task_key(s) == task]
        by_method: dict[str, Any] = {}
        for kind in sorted({s["spec"]["kind"] for s in task_rows}):
            xs = [s for s in task_rows if s["spec"]["kind"] == kind]
            by_method[kind] = {
                "services": len(xs),
                "complete_seconds_median": median(s["complete_seconds"] for s in xs),
                "complete_seconds_min": min(float(s["complete_seconds"]) for s in xs),
                "complete_seconds_max": max(float(s["complete_seconds"]) for s in xs),
                "q_queries_median": median(s["counts"]["q_queries"] for s in xs),
                "screen_attempts": sum(int(s["counts"].get("screen_attempts", 0)) for s in xs),
                "screen_returns": sum(int(s["counts"].get("screen_returns", 0)) for s in xs),
                "routed_queries": sum(int(s["counts"].get("routed_queries", 0)) for s in xs),
                "warnings": sum(warning_count(s) for s in xs),
            }
        winner = min(by_method, key=lambda k: by_method[k]["complete_seconds_median"])
        adaptive = by_method["adaptive"]
        for kind, item in by_method.items():
            item["complete_time_percent_vs_adaptive"] = 100.0 * (
                item["complete_seconds_median"] / adaptive["complete_seconds_median"] - 1.0
            )
            item["q_query_percent_vs_adaptive"] = 100.0 * (
                item["q_queries_median"] / adaptive["q_queries_median"] - 1.0
            )
        by_task[f"d{d}-T{T}-{target}"] = {
            "winner_by_raw_median": winner,
            "methods": by_method,
        }
    return {"services": len(rows), "tasks": by_task}


def reuse_summary(summaries: list[dict[str, Any]], analysis: dict[str, Any]) -> dict[str, Any]:
    rows = [s for s in summaries if s["spec"]["group"] == "reuse"]
    by_task: dict[str, Any] = {}
    for task in sorted({task_key(s) for s in rows}):
        d, T, target = task
        task_rows = [s for s in rows if task_key(s) == task]
        methods: list[dict[str, Any]] = []
        for kind in sorted({s["spec"]["kind"] for s in task_rows}):
            kind_rows = [s for s in task_rows if s["spec"]["kind"] == kind]
            for seed in sorted({int(s["spec"]["seed"]) for s in kind_rows}):
                xs = [s for s in kind_rows if int(s["spec"]["seed"]) == seed]
                methods.append({
                    "kind": kind,
                    "seed": seed,
                    "processes": len(xs),
                    "blocks_per_process": sorted({len(s["blocks"]) for s in xs}),
                    "complete_seconds_median": median(s["complete_seconds"] for s in xs),
                    "initial_service_seconds_median": median(s["initial_service_seconds"] for s in xs),
                    "total_q_queries_median": median(
                        sum(int(b["counts"]["q_queries"]) for b in s["blocks"]) for s in xs
                    ),
                })
        winners = []
        for repeat in sorted({int(s["spec"]["repeat"]) for s in task_rows}):
            xs = [s for s in task_rows if int(s["spec"]["repeat"]) == repeat]
            w = min(xs, key=lambda s: float(s["complete_seconds"]))
            winners.append({
                "repeat": repeat,
                "kind": w["spec"]["kind"],
                "seed": int(w["spec"]["seed"]),
                "seconds": float(w["complete_seconds"]),
            })
        by_task[f"d{d}-T{T}-{target}"] = {"methods": methods, "repeat_winners": winners}

    crossings = analysis["reuse_crossings"]
    return {
        "services": len(rows),
        "blocks_per_process": 24,
        "full_process_wins_against_matched_adaptive": sum(bool(x["full_process_win"]) for x in crossings),
        "full_process_nonwins": sum(not bool(x["full_process_win"]) for x in crossings),
        "wins_by_method": dict(collections.Counter(
            next(kind for kind in ("adaptive", "bisection", "relu", "quadratic") if f"-{kind}-" in x["key"])
            for x in crossings if x["full_process_win"]
        )),
        "persistent_prefix_crossings_within_window": sum(
            x["persistent_prefix_crossing_within_window"] is not None for x in crossings
        ),
        "first_prefix_crossings": sum(x["first_prefix_crossing"] is not None for x in crossings),
        "tasks": by_task,
    }


def inference_summary(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [s for s in summaries if s["spec"]["group"] == "inference"]
    intervals: list[dict[str, Any]] = []
    observations = 0
    for s in rows:
        observations += int(s["continuous_law_observations"])
        for name, pair in s["contrasts"].items():
            lo, hi = map(float, pair)
            raw = float(s["raw_mean_differences"][name])
            width = hi - lo
            intervals.append({
                "task": f"d{s['spec']['d']}-T{s['spec']['T']}",
                "contrast": name,
                "lower": lo,
                "upper": hi,
                "width": width,
                "raw_mean_difference": raw,
                "contains_zero": lo <= 0.0 <= hi,
                "half_width_to_abs_raw_ratio": (width / 2.0) / max(abs(raw), 1e-300),
            })
    return {
        "services": len(rows),
        "distinct_common_path_rows": observations,
        "contrasts": len(intervals),
        "all_contain_zero": all(x["contains_zero"] for x in intervals),
        "max_absolute_endpoint": max(max(abs(x["lower"]), abs(x["upper"])) for x in intervals),
        "interval_width_min": min(x["width"] for x in intervals),
        "interval_width_median": median(x["width"] for x in intervals),
        "interval_width_max": max(x["width"] for x in intervals),
        "max_absolute_raw_mean_difference": max(abs(x["raw_mean_difference"]) for x in intervals),
        "half_width_to_abs_raw_ratio_min": min(x["half_width_to_abs_raw_ratio"] for x in intervals),
        "half_width_to_abs_raw_ratio_median": median(x["half_width_to_abs_raw_ratio"] for x in intervals),
        "half_width_to_abs_raw_ratio_max": max(x["half_width_to_abs_raw_ratio"] for x in intervals),
        "intervals": intervals,
    }


def vector_summary(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    rows = sorted(
        [s for s in summaries if s["spec"]["group"] == "vector"],
        key=lambda s: (int(s["spec"]["d"]), int(s["spec"]["T"])),
    )
    cells = []
    by_d: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for s in rows:
        cell = {
            "d": int(s["spec"]["d"]),
            "T": int(s["spec"]["T"]),
            "complete_seconds": float(s["complete_seconds"]),
            "q_queries": int(s["counts"]["q_queries"]),
            "terminal_queries": int(s["counts"]["terminal_queries"]),
            "shock_children": int(s["counts"]["shock_children"]),
            "refinements": int(s["counts"]["refinements"]),
            "peak_rss_kib": int(s["peak_rss_kib"]),
            "uniform_policy_gap": float(eval_fraction(s["account"]["uniform_policy_gap_exact"])),
        }
        cells.append(cell)
        by_d[cell["d"]].append(cell)
    growth = {}
    for d, xs in by_d.items():
        xs = sorted(xs, key=lambda x: x["T"])
        growth[str(d)] = [{
            "from_T": a["T"],
            "to_T": b["T"],
            "seconds_ratio": b["complete_seconds"] / a["complete_seconds"],
            "q_query_ratio": b["q_queries"] / a["q_queries"],
        } for a, b in zip(xs, xs[1:])]
    return {"services": len(rows), "methods": sorted({s["spec"]["kind"] for s in rows}), "cells": cells, "growth": growth}


def eval_fraction(text: str) -> float:
    num, den = text.split("/", 1)
    return int(num) / int(den)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    digest = sha256_file(args.artifact)
    assert digest == EXPECTED_ARTIFACT_SHA256, (digest, EXPECTED_ARTIFACT_SHA256)

    with zipfile.ZipFile(args.artifact) as zf:
        final = load_json(zf, "audit/FINAL_DELIVERY67.json")
        release = load_json(zf, "audit/RELEASE67.json")
        tests = load_json(zf, "audit/TESTS67.json")
        execution = load_json(zf, "audit/EXECUTION67.json")
        result = load_json(zf, "audit/RESULT_AUDIT67.json")
        analysis = load_json(zf, "audit/ANALYSIS67.json")
        erratum = load_json(zf, "audit/ERRATUM67.json")

    assert final["status"] == "passed"
    assert final["canonical_branch"] == EXPECTED_BRANCH
    assert int(final["workflow_run_id"]) == EXPECTED_WORKFLOW_RUN
    assert final["clean_archive_rebuild"] == "passed"
    assert release["status"] == "passed" and release["network_used_by_builder"] is False
    assert tests["status"] == "passed" and tests["total"] == 135
    assert execution["status"] == "executed"
    assert execution["service_count"] == execution["returned"] == 212
    assert execution["failed"] == execution["timed_out"] == 0
    assert result["status"] == "passed" and result["catalogue_services"] == 212
    assert result["returned"] == 212 and result["failed"] == result["timed_out"] == 0
    assert analysis["status"] == "derived_from_passed_corrected_audit"
    assert erratum["status"] == "counterexample_reproduced_and_corrected"

    summaries = result["summaries"]
    group_counts = collections.Counter(s["spec"]["group"] for s in summaries)
    assert group_counts == {"comparison": 180, "reuse": 24, "inference": 2, "vector": 6}

    documents = {d["document"]: d for d in final["documents"]}
    output = {
        "status": "passed",
        "reviewed_snapshot": {
            "branch": EXPECTED_BRANCH,
            "commit": EXPECTED_COMMIT,
            "tree": EXPECTED_TREE,
        },
        "publication": {
            "workflow_run_id": EXPECTED_WORKFLOW_RUN,
            "artifact_id": EXPECTED_ARTIFACT_ID,
            "artifact_sha256": digest,
            "clean_archive_rebuild": final["clean_archive_rebuild"],
            "file_count": int(final["file_count"]),
            "tests": tests,
            "active_pages": {
                "article": documents["ECTA"]["pages"],
                "supplement": documents["supp"]["pages"],
                "response": documents["response"]["pages"],
            },
        },
        "catalogue": {
            "services": int(execution["service_count"]),
            "returned": int(execution["returned"]),
            "failed": int(execution["failed"]),
            "timed_out": int(execution["timed_out"]),
            "complete_process_seconds": float(execution["total_process_seconds"]),
            "group_counts": dict(group_counts),
            "implemented_decisions_replayed": int(result["implemented_decisions_replayed"]),
            "distinct_comparison_services_requeried": int(result["distinct_comparison_services_requeried"]),
            "independent_rational_midpoint_paths": int(result["independent_rational_midpoint_paths"]),
            "new_training_runs_in_publication_replay": int(result["new_training_runs"]),
            "new_independent_rows_in_publication_replay": int(result["new_independent_rows_in_this_replay"]),
            "warnings": int(analysis["warnings_total"]),
            "fitting_seeds": int(analysis["fitting_seeds"]),
        },
        "cold_start": cold_summary(summaries),
        "reuse": reuse_summary(summaries, analysis),
        "continuous_law_inference": inference_summary(summaries),
        "vector_horizon": vector_summary(summaries),
        "erratum": {
            "status": erratum["status"],
            "correction": erratum["correction"],
            "additional_independent_observations": int(erratum["additional_independent_observations"]),
            "policy_actions_changed": bool(erratum["policy_actions_changed_by_reenclosure"]),
            "original_interval": erratum["original_cost_interval"],
            "corrected_interval": erratum["corrected_cost_interval"],
        },
        "scope": [
            "The audit verifies the frozen publication artifact and recomputes reported comparisons; it does not rerun fitting, Bellman services, policy simulation, LaTeX, or clocks.",
            "Single-host process times are descriptive observations, not a hardware-general sampling distribution.",
            "The publication replay re-queries the 90 distinct scalar comparison services but does not independently re-integrate the large vector trees or every reuse/inference endpoint query.",
            "All direct expected-cost intervals are conditional on the declared independent-bin model and frozen callable policies.",
        ],
    }

    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
