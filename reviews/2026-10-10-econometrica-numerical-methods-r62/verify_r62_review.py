#!/usr/bin/env python3
"""Independent standard-library audit for the NBO R62 referee review.

The script audits the two source-bound GitHub Actions artifacts deposited for
R62.  It does not retrain, resimulate, recompile, or retime the experiment.
It verifies artifact identities, internal file bindings, prospective target
attainment, direct policy-cost signs, complete-work frontiers, proposal
activity, and final delivery metadata.

Usage:
    python verify_r62_review.py \
        --science-zip nbo-r62-prospective-science.zip \
        --publication-zip nbo-r62-publication.zip \
        --output verification_results.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import tempfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

EXPECTED = {
    "science_zip_sha256": "33416454ea1418303e132c4fd00cba1f47c7c48ee3564acf2b808833e105c9fb",
    "publication_zip_sha256": "25b15a12a5ad2ed15af1291f7a5ca2789bbe9ac2abfd9f7550ece872b45e3963",
    "canonical_branch": "revision/econometrica-nbo-r62-review-ready-2026-10-10",
    "revision_commit": "cfecc5ffcdeb836b1c70e9b98d1dc87f6f8cd097",
    "revision_tree": "8e7d70f846f0744edb35ee0de35d85cb210d64be",
    "science_commit": "d868cb5bc113e521be134cb9f50f04b5c68b3493",
    "source_freeze_sha256": "80690864c5f9605e891c1640b401be4208570b0710f8638865782eea0bef4b81",
    "publication_workflow_run_id": 38020293255,
    "science_workflow_run_id": 38016958569,
}

TASKS = ["d2-m1-T2", "d2-m1-T3", "d4-m1-T3", "d8-m1-T2", "d2-m2-T2"]
TOLERANCES = ["1/2", "1/4", "1/8", "1/16", "1/32"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise AssertionError(f"Expected object in {path}")
    return value


def locate(root: Path, relative: str) -> Path:
    direct = root / relative
    if direct.exists():
        return direct
    matches = list(root.rglob(relative))
    if len(matches) != 1:
        raise FileNotFoundError(f"Could not uniquely locate {relative!r} under {root}")
    return matches[0]


def classify_policy(key: str) -> tuple[str, str]:
    if key == "common":
        return ("common", "common")
    if key.startswith("relu-"):
        family = "relu"
    elif key.startswith("quadratic-"):
        family = "quadratic"
    else:
        raise AssertionError(f"Unexpected policy key {key!r}")
    variant = "guarded" if key.endswith("-guarded") else "pure"
    return family, variant


def audit(science_root: Path, publication_root: Path) -> dict[str, Any]:
    summaries: dict[str, dict[str, Any]] = {}
    costs: dict[str, dict[str, Any]] = {}
    clocks: dict[str, dict[str, Any]] = {}

    pub_audit = locate(publication_root, "audit")
    result_interpretation = read_json(pub_audit / "RESULT_INTERPRETATION62.json")
    publication_facts = read_json(pub_audit / "PUBLICATION_FACTS62.json")
    complete_work = read_json(pub_audit / "COMPLETE_WORK62.json")
    final_delivery = read_json(pub_audit / "FINAL_DELIVERY62.json")
    science_replay = read_json(pub_audit / "SCIENCE_REPLAY62.json")
    clean_rebuild = read_json(pub_audit / "CLEAN_REBUILD62.json")

    source_records = result_interpretation["source_records"]
    interval_count = 0
    record_hashes_checked = 0
    target_attainment: dict[str, Counter[str]] = defaultdict(Counter)
    final_bounds: dict[str, list[float]] = defaultdict(list)
    complete_work_values: dict[str, list[float]] = defaultdict(list)
    additional_nodes: Counter[str] = Counter()
    proposal_node_opportunities: Counter[str] = Counter()
    direct_signs: dict[str, Counter[str]] = defaultdict(Counter)
    interval_widths: dict[str, list[float]] = defaultdict(list)
    common_final_bounds: dict[str, float] = {}
    final_reference_nodes: dict[str, int] = {}
    final_reference_queries: dict[str, int] = {}
    peak_rss_kib: dict[str, int] = {}

    for task in TASKS:
        task_dir = locate(science_root, f"results62/{task}")
        summary_path = task_dir / "summary.json"
        costs_path = task_dir / "costs.json"
        clock_path = task_dir / "clock.json"
        summary = read_json(summary_path)
        cost = read_json(costs_path)
        clock = read_json(clock_path)
        summaries[task], costs[task], clocks[task] = summary, cost, clock

        assert summary["task"] == task
        assert summary["source_freeze_sha256"] == EXPECTED["source_freeze_sha256"]
        assert sha256_file(summary_path) == source_records[task]["summary_sha256"]
        assert sha256_file(costs_path) == source_records[task]["costs_sha256"]
        assert sha256_file(costs_path) == summary["costs_sha256"] == clock["costs_sha256"]
        record_hashes_checked += 3

        interval_count += len(cost["absolute"]) + len(cost["contrasts"])
        assert len(cost["absolute"]) == 18
        assert len(cost["contrasts"]) == 41
        assert cost["paths"] == 65536

        common_targets = summary["targets"]["common"]
        common_final_bounds[task] = float(common_targets[-1]["final_bound"])
        for item in common_targets:
            target_attainment["common"][item["tolerance"]] += item["status"] == "attained"
        final_bounds["common"].append(float(common_targets[-1]["final_bound"]))
        complete_work_values["common"].append(float(summary["full_catalogue_release_work_seconds"]["common"]))

        final_reference = summary["reference"][-1]
        final_reference_nodes[task] = int(final_reference["nodes"])
        final_reference_queries[task] = sum(int(row["point_action_queries"]) for row in final_reference["work"])
        peak_rss_kib[task] = int(summary["peak_rss_kib"])

        for policy, target_rows in summary["targets"].items():
            if policy == "common":
                continue
            family, variant = classify_policy(policy)
            bucket = f"{family}-{variant}"
            for item in target_rows:
                target_attainment[bucket][item["tolerance"]] += item["status"] == "attained"
            final_bounds[bucket].append(float(target_rows[-1]["final_bound"]))
            complete_work_values[bucket].append(float(summary["full_catalogue_release_work_seconds"][policy]))

        # The last rung is the finest declared rung.  Count how often the
        # fitted generator strictly improves the common candidate at a node.
        for method_key, rungs in summary["methods"].items():
            family = "relu" if method_key.startswith("relu-") else "quadratic"
            final_rung = rungs[-1]
            additional_nodes[family] += sum(int(row["additional_witness_nodes"]) for row in final_rung["counts"])
            proposal_node_opportunities[family] += int(final_reference["nodes"]) * int(summary["T"])

        for name, row in cost["contrasts"].items():
            left, right = row["left"], row["right"]
            if right != "common" and not right.endswith("-guarded"):
                continue
            if left.startswith("relu-"):
                family = "relu"
            elif left.startswith("quadratic-"):
                family = "quadratic"
            else:
                continue
            left_variant = "guarded" if left.endswith("-guarded") else "pure"
            if right == "common":
                pair = f"{family}-{left_variant}-minus-common"
            else:
                pair = f"{family}-pure-minus-guarded"
            direct_signs[pair][row["sign"]] += 1
            lo, hi = map(float, row["interval"])
            interval_widths[pair].append(hi - lo)

    assert interval_count == 295
    assert final_delivery["canonical_branch"] == EXPECTED["canonical_branch"]
    assert final_delivery["completed_science_commit"] == EXPECTED["science_commit"]
    assert int(final_delivery["workflow_run_id"]) == EXPECTED["publication_workflow_run_id"]
    assert final_delivery["clean_archive_rebuild"] == "passed"
    assert clean_rebuild["status"] == "passed"
    assert science_replay["status"] == "passed"
    assert science_replay["checked_interval_records"] == 295
    assert science_replay["checked_nodal_action_records"] == 18806777

    documents = {row["document"]: row for row in final_delivery["documents"]}
    assert documents["ECTA"]["pages"] == 106
    assert documents["supp"]["pages"] == 69
    assert documents["response"]["pages"] == 10

    frontiers = publication_facts["frontiers"]
    attainable_frontiers = [row for row in frontiers if row["eligible"]]
    assert len(frontiers) == 25
    assert len(attainable_frontiers) == 20
    assert all(row["least_recorded_complete_release_method"] == "common" for row in attainable_frontiers)

    # Recompute the very small difference between common and augmented bounds.
    guarded_minus_common: dict[str, list[float]] = defaultdict(list)
    pure_over_common: dict[str, list[float]] = defaultdict(list)
    for task, summary in summaries.items():
        common = float(summary["targets"]["common"][-1]["final_bound"])
        for policy, rows in summary["targets"].items():
            if policy == "common":
                continue
            family, variant = classify_policy(policy)
            final = float(rows[-1]["final_bound"])
            if variant == "guarded":
                guarded_minus_common[family].append(final - common)
            else:
                pure_over_common[family].append(final / common)

    def stats(values: list[float]) -> dict[str, float | int]:
        if not values:
            return {}
        return {
            "count": len(values),
            "min": min(values),
            "median": statistics.median(values),
            "max": max(values),
            "mean": statistics.fmean(values),
        }

    result = {
        "status": "passed",
        "reviewed_snapshot": {
            "branch": EXPECTED["canonical_branch"],
            "commit": EXPECTED["revision_commit"],
            "tree": EXPECTED["revision_tree"],
            "completed_science_commit": EXPECTED["science_commit"],
        },
        "checks": {
            "tasks": len(TASKS),
            "source_records_verified": record_hashes_checked,
            "interval_records": interval_count,
            "checked_nodal_action_records": science_replay["checked_nodal_action_records"],
            "prospective_path_rows": final_delivery["prospective_path_rows"],
            "fitting_services": final_delivery["fitting_services"],
            "clean_archive_rebuild": final_delivery["clean_archive_rebuild"],
            "article_pages": documents["ECTA"]["pages"],
            "supplement_pages": documents["supp"]["pages"],
            "response_pages": documents["response"]["pages"],
        },
        "accuracy": {
            "target_attainment": {key: dict(value) for key, value in sorted(target_attainment.items())},
            "common_final_all_state_bounds": common_final_bounds,
            "final_bound_stats": {key: stats(value) for key, value in sorted(final_bounds.items())},
            "guarded_minus_common_final_bound": {key: stats(value) for key, value in sorted(guarded_minus_common.items())},
            "pure_to_common_final_bound_ratio": {key: stats(value) for key, value in sorted(pure_over_common.items())},
        },
        "direct_costs": {
            "sign_counts": {key: dict(value) for key, value in sorted(direct_signs.items())},
            "interval_width_stats": {key: stats(value) for key, value in sorted(interval_widths.items())},
        },
        "proposal_activity": {
            family: {
                "additional_witness_node_dates": additional_nodes[family],
                "node_date_opportunities": proposal_node_opportunities[family],
                "share": additional_nodes[family] / proposal_node_opportunities[family],
            }
            for family in ("relu", "quadratic")
        },
        "complete_work": {
            "attainable_task_tolerance_cells": len(attainable_frontiers),
            "cells_won_by_common": sum(row["least_recorded_complete_release_method"] == "common" for row in attainable_frontiers),
            "recorded_component_work_stats": {key: stats(value) for key, value in sorted(complete_work_values.items())},
            "outer_envelope_charge_seconds": complete_work["outer_envelope_charge_seconds"],
            "unallocated_residual_charged_to_every_method_seconds": complete_work[
                "unallocated_residual_charged_to_every_method_seconds"
            ],
            "timing_scope": complete_work["scope"],
        },
        "scaling": {
            "final_reference_nodes": final_reference_nodes,
            "final_reference_point_action_queries": final_reference_queries,
            "peak_process_rss_kib": peak_rss_kib,
        },
        "scope": [
            "The audit replays frozen JSON records and hashes; it does not retrain, resimulate, recompile, or retime R62.",
            "The four fitting seeds are a fixed finite catalogue, not an estimator of optimizer success on future tasks.",
            "Policy-cost paths quantify interval uncertainty for frozen policies and do not add independent fitting objects.",
            "Complete-work times are descriptive single-host component sums plus a disclosed shared residual charge.",
        ],
    }

    # These are the review's load-bearing empirical checks.
    assert result["direct_costs"]["sign_counts"]["relu-pure-minus-common"] == {"positive": 20}
    assert result["direct_costs"]["sign_counts"]["relu-guarded-minus-common"] == {"unresolved": 20}
    assert result["direct_costs"]["sign_counts"]["quadratic-pure-minus-common"] == {
        "positive": 16,
        "unresolved": 4,
    }
    assert result["direct_costs"]["sign_counts"]["quadratic-guarded-minus-common"] == {"unresolved": 20}
    assert target_attainment["relu-pure"]["1/32"] == 0
    assert target_attainment["quadratic-pure"]["1/32"] == 0
    assert target_attainment["relu-guarded"]["1/32"] == 12
    assert target_attainment["quadratic-guarded"]["1/32"] == 12
    assert max(guarded_minus_common["relu"]) < 3e-12
    assert max(guarded_minus_common["quadratic"]) < 3e-12
    assert result["complete_work"]["cells_won_by_common"] == 20
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--science-zip", required=True, type=Path)
    parser.add_argument("--publication-zip", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    science_digest = sha256_file(args.science_zip)
    publication_digest = sha256_file(args.publication_zip)
    if science_digest != EXPECTED["science_zip_sha256"]:
        raise AssertionError(f"Unexpected science artifact digest: {science_digest}")
    if publication_digest != EXPECTED["publication_zip_sha256"]:
        raise AssertionError(f"Unexpected publication artifact digest: {publication_digest}")

    with tempfile.TemporaryDirectory(prefix="nbo-r62-review-") as tmp:
        tmp_path = Path(tmp)
        science_root = tmp_path / "science"
        publication_root = tmp_path / "publication"
        science_root.mkdir()
        publication_root.mkdir()
        with zipfile.ZipFile(args.science_zip) as archive:
            archive.extractall(science_root)
        with zipfile.ZipFile(args.publication_zip) as archive:
            archive.extractall(publication_root)
        result = audit(science_root, publication_root)

    result["artifact_digests"] = {
        "science": science_digest,
        "publication": publication_digest,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
