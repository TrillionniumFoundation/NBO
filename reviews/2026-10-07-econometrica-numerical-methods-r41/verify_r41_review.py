#!/usr/bin/env python3
"""Independent deterministic audit for the NBO R41 referee review.

This standard-library script verifies the source-bound publication ledger,
record hashes, direct neural-versus-spline comparisons, certificate sharpness,
and the activated native-precision catalogue. It does not rerun training or
replace the frozen service clocks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

REV = Path("revisions/2026-10-07-r41")
SNAPSHOT = {
    "branch": "revision/econometrica-nbo-r41-review-ready-2026-10-07",
    "commit": "06a104a8db06b76464165899d817b303cb2aaa01",
    "tree": "783b70a4ea1ead950d7ea04aeebccc27a7510bf4",
}
EXPECTED_BLOBS = {
    "ECTA.tex": "07e8100e1a97d1b2b1aae7e47d0be3b1906e8f6d",
    "supp.tex": "ac5fc091749f32c31a6aec891943f29b591d687f",
    "response.md": "25b4f5c41023a17dbcafe22448ce7cfabcdbb903",
    "applications.tex": "311fde2ab16eb51fc70f8c90bdd412704060f71b",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def key(row: dict[str, Any]) -> tuple[int, float, float]:
    e = row["spec"]["economy"]
    return int(e["d"]), float(e["condition"]), float(row["spec"]["epsilon"])


def audit(repo_root: Path) -> dict[str, Any]:
    rev = repo_root / REV
    require(rev.is_dir(), f"missing revision directory: {rev}")

    # Verify the complete publication-file ledger, not only selected files.
    ledger = load(rev / "audit/FILES_SHA256.json")
    for relative, expected in ledger.items():
        path = repo_root / relative
        require(path.is_file(), f"missing publication file: {relative}")
        require(sha256(path) == expected, f"SHA-256 mismatch: {relative}")

    blob_results: dict[str, str] = {}
    for name, expected in EXPECTED_BLOBS.items():
        actual = git_blob_sha1(rev / name)
        require(actual == expected, f"Git blob mismatch: {name}")
        blob_results[name] = actual

    study = load(rev / "results/R41_STUDY.json")
    require(study["science_source_commit"] == "8ecce0c377da591adde926e562f1466aaf6e7c31",
            "unexpected science source commit")
    for relative, expected in study["code_hashes"].items():
        require(sha256(rev / relative) == expected, f"study code hash mismatch: {relative}")
    for row in study["neural_refinements"]:
        require(sha256(rev / row["path"]) == row["sha256"], f"neural record mismatch: {row['path']}")
    for row in study["final"]:
        require(sha256(rev / row["comparison_result"]) == row["comparison_sha256"],
                f"comparison record mismatch: {row['comparison_result']}")

    # Direct neural-versus-contemporaneously-reoptimized spline comparison.
    direct_positive = direct_negative = direct_overlap = direct_total = 0
    all_within_margin = True
    certificate_rows: list[dict[str, Any]] = []
    verification_seconds: dict[str, float] = {}
    for final in study["final"]:
        price, theta = float(final["price"]), float(final["theta"])
        tag = f"P{price:g}-theta{theta:g}"
        comparison = load(rev / final["comparison_result"])
        neural = load(rev / final["neural_result"])
        lower = comparison["neural_minus_reoptimized_spline"]["lower"]
        upper = comparison["neural_minus_reoptimized_spline"]["upper"]
        margin = float(comparison["equivalence_margin"])
        for lo, hi in zip(lower, upper):
            direct_total += 1
            if lo > 0:
                direct_positive += 1
            elif hi < 0:
                direct_negative += 1
            else:
                direct_overlap += 1
            all_within_margin = all_within_margin and lo >= -margin and hi <= margin

        spline_global = float(comparison["conventional_policy"]["policy_gap_upper"])
        neural_global = float(final["global_gap"])
        # The conventional certificate supplies its own lower Bellman value:
        # the certified spline at the queried grid state minus lower_value_shift.
        states = [float(x) for x in neural["own_policy_values"]["states"]]
        knots = [float(x) for x in comparison["conventional_policy"]["knots"]]
        spline_values0 = [float(x) for x in comparison["conventional_policy"]["values"][0]]
        spline_lower = []
        for state in states:
            matches = [i for i, x in enumerate(knots) if x == state]
            require(len(matches) == 1, f"query state is not a unique spline knot: {tag}, {state}")
            spline_lower.append(
                spline_values0[matches[0]] - float(comparison["conventional_policy"]["lower_value_shift"])
            )
        spline_query = max(
            float(up) - low
            for up, low in zip(comparison["conventional_values"]["upper"], spline_lower)
        )
        neural_query = float(final["max_query_gap"])
        require(spline_global < neural_global, f"spline global certificate not tighter: {tag}")
        require(spline_query < neural_query, f"spline query certificate not tighter: {tag}")
        certificate_rows.append({
            "economy": tag,
            "neural_global_gap": neural_global,
            "spline_global_gap": spline_global,
            "neural_to_spline_global_ratio": neural_global / spline_global,
            "neural_query_gap": neural_query,
            "spline_query_gap": spline_query,
            "neural_to_spline_query_ratio": neural_query / spline_query,
            "neural_verification_seconds_all_refinements": sum(
                float(x["seconds_through_fsync"]) for x in study["neural_refinements"]
                if float(x["price"]) == price and float(x["theta"]) == theta
            ),
            "spline_final_construction_and_query_seconds": float(comparison["conventional_construction_and_query_seconds"]),
        })
        verification_seconds[tag] = certificate_rows[-1]["neural_verification_seconds_all_refinements"]

    require((direct_total, direct_positive, direct_negative, direct_overlap) == (16, 14, 0, 2),
            "unexpected direct comparison signs")
    require(all_within_margin, "a direct interval exceeds the disclosed descriptive margin")

    # Precision mechanism: verify all source-bound records and match methods object by object.
    index = load(rev / "results/precision/INDEX.json")
    require(len(index) == 48, "unexpected precision catalogue size")
    for row in index:
        record = rev / "results/precision" / f"service-{int(row['id']):03d}.json"
        require(sha256(record) == row["record_sha256"], f"precision record mismatch: {record.name}")

    by_method: dict[str, dict[tuple[int, float, float], dict[str, Any]]] = {}
    for row in index:
        by_method.setdefault(row["spec"]["method"], {})[key(row)] = row
    adaptive = by_method["adaptive-cached"]
    fixed64 = by_method["fixed64-cached"]
    require(adaptive.keys() == fixed64.keys(), "adaptive/fixed64 object sets differ")

    adaptive_slower = 0
    ratios: list[float] = []
    accepted_adaptive = accepted_fixed64 = rejected32_adaptive = 0
    mixed_services = 0
    for obj in sorted(adaptive):
        a, f = adaptive[obj], fixed64[obj]
        accepted_a = int(a["accepted32"]) + int(a["accepted64"])
        accepted_f = int(f["accepted32"]) + int(f["accepted64"])
        require(accepted_a == accepted_f, f"accepted update counts differ: {obj}")
        accepted_adaptive += accepted_a
        accepted_fixed64 += accepted_f
        rejected32_adaptive += int(a["rejected32"])
        mixed_services += int(a["accepted32"] > 0 and a["accepted64"] > 0)
        ratio = float(a["seconds_through_fsync"]) / float(f["seconds_through_fsync"])
        ratios.append(ratio)
        adaptive_slower += int(ratio > 1)

    total_adaptive_seconds = sum(float(r["seconds_through_fsync"]) for r in adaptive.values())
    total_fixed64_seconds = sum(float(r["seconds_through_fsync"]) for r in fixed64.values())
    require(accepted_adaptive == accepted_fixed64 == 158, "unexpected accepted update totals")
    require(rejected32_adaptive == 42, "unexpected adaptive binary32 rejection count")
    require(mixed_services == 10, "unexpected mixed-precision service count")
    require(adaptive_slower == 12, "adaptive was not slower in every recorded object")

    result_audit = load(rev / "audit/RESULT_AUDIT.json")
    require(result_audit["passed"] is True, "committed result audit is not passed")
    require(result_audit["adaptive_mixed_services"] == mixed_services, "mixed-service audit mismatch")
    tests = load(rev / "audit/TESTS.json")
    require(tests["direct_certificate_with_spline_disabled"] is True,
            "direct neural certificate did not pass with spline evaluator disabled")

    release = load(rev / "audit/RELEASE_AUDIT.json")
    compilation = {row["document"]: row for row in release["compilation"]}
    for name in ("ECTA", "supp", "applications", "response"):
        row = compilation[name]
        require(not row["undefined_references"], f"undefined references in {name}")
        require(row["duplicate_labels"] is False, f"duplicate labels in {name}")
        require(row["missing_characters"] is False, f"missing characters in {name}")
        require(row["overfull_boxes"] == 0, f"overfull boxes in {name}")

    global_ratios = [r["neural_to_spline_global_ratio"] for r in certificate_rows]
    query_ratios = [r["neural_to_spline_query_ratio"] for r in certificate_rows]
    return {
        "status": "passed",
        "reviewed_snapshot": SNAPSHOT,
        "checks": {
            "publication_files_sha256_verified": len(ledger),
            "pinned_git_blobs_verified": blob_results,
            "study_code_hashes_verified": len(study["code_hashes"]),
            "neural_refinement_records_verified": len(study["neural_refinements"]),
            "comparison_records_verified": len(study["final"]),
            "precision_records_verified": len(index),
            "direct_certificate_with_spline_disabled": True,
            "active_publication_pages": {k: compilation[k]["pages"] for k in ("ECTA", "supp", "applications", "response")},
        },
        "direct_neural_vs_spline": {
            "intervals": direct_total,
            "strictly_higher_neural_cost": direct_positive,
            "strictly_lower_neural_cost": direct_negative,
            "overlap_zero": direct_overlap,
            "all_within_posthoc_descriptive_margin_0_001": all_within_margin,
            "certificate_rows": certificate_rows,
            "neural_to_spline_global_gap_ratio_range": [min(global_ratios), max(global_ratios)],
            "neural_to_spline_query_gap_ratio_range": [min(query_ratios), max(query_ratios)],
        },
        "precision_mechanism": {
            "objects": len(adaptive),
            "adaptive_mixed_precision_services": mixed_services,
            "adaptive_accepted_updates": accepted_adaptive,
            "fixed64_accepted_updates": accepted_fixed64,
            "adaptive_rejected_binary32_attempts": rejected32_adaptive,
            "adaptive_slower_than_fixed64_objects": adaptive_slower,
            "adaptive_to_fixed64_time_ratio_range": [min(ratios), max(ratios)],
            "adaptive_to_fixed64_time_ratio_median": statistics.median(ratios),
            "adaptive_total_seconds": total_adaptive_seconds,
            "fixed64_total_seconds": total_fixed64_seconds,
            "adaptive_to_fixed64_total_time_ratio": total_adaptive_seconds / total_fixed64_seconds,
        },
        "scope": [
            "The audit verifies committed source-bound records; it does not rerun training or replace frozen clocks.",
            "Single service clocks are descriptive and do not support hardware-general performance inference.",
            "The derived spline query gaps use the same stored lower bound on the optimum and the contemporaneous spline policy's outward upper value at the four declared states.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository or extracted artifact root")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = audit(args.root.resolve())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
