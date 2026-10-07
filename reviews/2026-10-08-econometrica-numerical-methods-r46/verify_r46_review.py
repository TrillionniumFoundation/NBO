#!/usr/bin/env python3
"""Independent deterministic audit for the R46 Econometrica review.

The script reads a materialized R46 study package. By default it expects the
repository layout at revisions/2026-10-07-r46. Pass --root to point directly
at an extracted study artifact containing audit/, code/, and results/.

It verifies frozen source hashes, service/checkpoint identities, catalogue
counts, target crossings, certificate comparisons, timing comparisons, and an
exact-rational shift-invariance spot check. It does not rerun or retime the
economic study.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import statistics
from fractions import Fraction
from pathlib import Path
from typing import Any

EXPECTED = {
    "branch": "revision/econometrica-nbo-r46-review-ready-2026-10-08",
    "commit": "c3930399e3b8267451096d0e70ea67f49510065e",
    "tree": "42ac3db0d72ea030afb050754d2ae1da55864bc3",
    "artifact_sha256": "8cb0fa519bb5e9c15760541d29ca3af5312e73ca728a39ea81a5fc521ba7235a",
    "workflow_run_id": 37623758585,
    "artifact_id": 11483102637,
}
METHODS = ("cone-nearest", "cone-witness", "spline-nearest")
TARGETS = ("1/4", "1/8", "1/16")
RESOLUTIONS = (16, 32, 64, 128, 256, 512)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def locate_study(root: Path) -> Path:
    direct = root
    nested = root / "revisions" / "2026-10-07-r46"
    for candidate in (direct, nested):
        if (
            (candidate / "audit" / "EXECUTION_FREEZE.json").exists()
            and (candidate / "results" / "services").is_dir()
        ):
            return candidate
    raise FileNotFoundError(
        "Could not locate a materialized R46 study package under "
        f"{root!s}; expected audit/EXECUTION_FREEZE.json and results/services/."
    )


def exact_shift_check() -> dict[str, Any]:
    beta = [Fraction(15, 16), Fraction(7, 8)]
    B = [Fraction(1), beta[0], beta[0] * beta[1]]
    u = [Fraction(1, 5), Fraction(-1, 100)]
    d = [Fraction(3, 100), Fraction(1, 25)]
    u_terminal = Fraction(1, 20)
    l_terminal = Fraction(-1, 50)

    original = (
        sum(B[t] * (u[t] + d[t]) for t in range(2))
        + B[2] * (u_terminal - l_terminal)
    )

    shift = [Fraction(3, 7), Fraction(-2, 9), Fraction(5, 11)]
    shifted_u = [
        u[t] + shift[t] - beta[t] * shift[t + 1] for t in range(2)
    ]
    shifted_d = [
        d[t] - shift[t] + beta[t] * shift[t + 1] for t in range(2)
    ]
    shifted_terminal_u = u_terminal + shift[2]
    shifted_terminal_l = l_terminal + shift[2]
    transformed = (
        sum(B[t] * (shifted_u[t] + shifted_d[t]) for t in range(2))
        + B[2] * (shifted_terminal_u - shifted_terminal_l)
    )
    return {
        "one_sided_gap_shift_invariance_exact": original == transformed,
        "original_gap_exact": str(original),
        "shifted_gap_exact": str(transformed),
    }


def audit(root: Path, artifact_zip: Path | None = None) -> dict[str, Any]:
    study = locate_study(root)
    freeze = json.loads((study / "audit" / "EXECUTION_FREEZE.json").read_text())
    tests = json.loads((study / "audit" / "TESTS_R46.json").read_text())

    source_results: dict[str, bool] = {}
    for relative, expected_hash in freeze["source_sha256"].items():
        source_path = study / relative
        source_results[relative] = (
            source_path.is_file() and sha256(source_path) == expected_hash
        )
    if not all(source_results.values()):
        failed = [name for name, ok in source_results.items() if not ok]
        raise AssertionError(f"Frozen source hash mismatch: {failed}")

    services_root = study / "results" / "services"
    service_dirs = sorted(path for path in services_root.iterdir() if path.is_dir())
    if len(service_dirs) != 36:
        raise AssertionError(f"Expected 36 services, found {len(service_dirs)}")

    records: list[dict[str, Any]] = []
    checkpoint_count = 0
    checkpoint_hash_count = 0
    method_counts: collections.Counter[str] = collections.Counter()

    for service_dir in service_dirs:
        record_path = service_dir / "record.json"
        record = json.loads(record_path.read_text())
        records.append(record)
        method_counts[record["method"]] += 1

        if len(record["attempts"]) != 6:
            raise AssertionError(f"{service_dir.name}: expected six attempts")
        for attempt in record["attempts"]:
            N = attempt["N"]
            checkpoint_path = service_dir / f"checkpoint-N{N}.json"
            checkpoint_count += 1
            if sha256(checkpoint_path) != attempt["checkpoint_sha256"]:
                raise AssertionError(f"Checkpoint hash mismatch: {checkpoint_path}")
            checkpoint_hash_count += 1

    if set(method_counts) != set(METHODS) or any(
        method_counts[method] != 12 for method in METHODS
    ):
        raise AssertionError(f"Unexpected method counts: {dict(method_counts)}")

    keyed = {
        (
            record["method"],
            record["horizon"],
            record["price"],
            record["repeat"],
        ): record
        for record in records
    }
    cells = sorted({(record["horizon"], record["price"]) for record in records})

    attainment = {
        method: {target: 0 for target in TARGETS} for method in METHODS
    }
    for record in records:
        for target in TARGETS:
            if record["first_crossings"].get(target) is not None:
                attainment[record["method"]][target] += 1

    unique_frontier: list[dict[str, Any]] = []
    first_crossings_identical = True
    first_crossing_table: dict[str, Any] = {}

    for horizon, price in cells:
        cell_key = f"T{horizon}-p{price}"
        first_crossing_table[cell_key] = {}
        for target in TARGETS:
            by_method: dict[str, list[int | None]] = {}
            for method in METHODS:
                values: list[int | None] = []
                for repeat in range(3):
                    crossing = keyed[
                        (method, horizon, price, repeat)
                    ]["first_crossings"].get(target)
                    values.append(None if crossing is None else crossing["N"])
                by_method[method] = values
            first_crossings_identical &= len(
                {tuple(values) for values in by_method.values()}
            ) == 1
            first_crossing_table[cell_key][target] = by_method

        for N in RESOLUTIONS:
            row: dict[str, Any] = {"T": horizon, "price": price, "N": N}
            for method in METHODS:
                attempt = next(
                    item
                    for item in keyed[(method, horizon, price, 0)]["attempts"]
                    if item["N"] == N
                )
                row[method] = attempt["bound_upper"]
            unique_frontier.append(row)

    tighter_nearest = sum(
        row["cone-witness"] < row["cone-nearest"] for row in unique_frontier
    )
    tighter_spline = sum(
        row["cone-witness"] < row["spline-nearest"] for row in unique_frontier
    )
    spline_exceptions = [
        row
        for row in unique_frontier
        if not row["cone-witness"] < row["spline-nearest"]
    ]

    common_nearest = common_spline = 0
    faster_nearest = faster_spline = 0
    ratios_nearest: list[float] = []
    ratios_spline: list[float] = []

    for horizon, price in cells:
        for repeat in range(3):
            for target in TARGETS:
                witness = keyed[
                    ("cone-witness", horizon, price, repeat)
                ]["first_crossings"].get(target)
                nearest = keyed[
                    ("cone-nearest", horizon, price, repeat)
                ]["first_crossings"].get(target)
                spline = keyed[
                    ("spline-nearest", horizon, price, repeat)
                ]["first_crossings"].get(target)

                if witness is not None and nearest is not None:
                    common_nearest += 1
                    faster_nearest += (
                        witness["prefix_seconds"] < nearest["prefix_seconds"]
                    )
                    ratios_nearest.append(
                        witness["prefix_seconds"] / nearest["prefix_seconds"]
                    )
                if witness is not None and spline is not None:
                    common_spline += 1
                    faster_spline += (
                        witness["prefix_seconds"] < spline["prefix_seconds"]
                    )
                    ratios_spline.append(
                        witness["prefix_seconds"] / spline["prefix_seconds"]
                    )

    final_bounds: list[dict[str, Any]] = []
    for horizon, price in cells:
        values = {
            method: keyed[(method, horizon, price, 0)]["attempts"][-1][
                "bound_upper"
            ]
            for method in METHODS
        }
        final_bounds.append(
            {
                "T": horizon,
                "price": price,
                **values,
                "witness_reduction_vs_nearest_percent": 100
                * (values["cone-nearest"] - values["cone-witness"])
                / values["cone-nearest"],
                "witness_reduction_vs_spline_percent": 100
                * (values["spline-nearest"] - values["cone-witness"])
                / values["spline-nearest"],
            }
        )

    artifact_result: dict[str, Any] = {
        "workflow_run_id": EXPECTED["workflow_run_id"],
        "artifact_id": EXPECTED["artifact_id"],
    }
    if artifact_zip is not None:
        digest = sha256(artifact_zip)
        artifact_result.update(
            {
                "sha256": digest,
                "digest_matched": digest == EXPECTED["artifact_sha256"],
            }
        )
        if digest != EXPECTED["artifact_sha256"]:
            raise AssertionError("Artifact ZIP digest mismatch")

    return {
        "status": "passed",
        "reviewed_snapshot": {
            "branch": EXPECTED["branch"],
            "commit": EXPECTED["commit"],
            "tree": EXPECTED["tree"],
        },
        "evidence_artifact": artifact_result,
        "checks": {
            "source_hashes_verified": sum(source_results.values()),
            "source_hashes_total": len(source_results),
            "services": len(records),
            "checkpoints": checkpoint_count,
            "checkpoint_hashes_verified": checkpoint_hash_count,
            "method_counts": dict(method_counts),
            "tests_recorded": tests,
        },
        "attainment": attainment,
        "comparisons": {
            "unique_frontier_rows": len(unique_frontier),
            "witness_tighter_than_nearest": tighter_nearest,
            "witness_tighter_than_spline": tighter_spline,
            "witness_vs_spline_exception": spline_exceptions,
            "all_first_crossing_resolutions_identical": first_crossings_identical,
            "first_crossings": first_crossing_table,
            "common_successful_target_repetition_comparisons": {
                "nearest": common_nearest,
                "spline": common_spline,
            },
            "witness_faster": {
                "nearest": faster_nearest,
                "spline": faster_spline,
            },
            "prefix_time_ratio_witness_over_nearest": {
                "min": min(ratios_nearest),
                "median": statistics.median(ratios_nearest),
                "max": max(ratios_nearest),
                "mean": statistics.mean(ratios_nearest),
            },
            "prefix_time_ratio_witness_over_spline": {
                "min": min(ratios_spline),
                "median": statistics.median(ratios_spline),
                "max": max(ratios_spline),
                "mean": statistics.mean(ratios_spline),
            },
            "final_bounds": final_bounds,
            "expected_policy_cost_ranking": (
                "not identified by the R46 witness catalogue"
            ),
        },
        "mathematical_spot_checks": exact_shift_check(),
        "scope": [
            "The audit verifies frozen records and arithmetic; it does not rerun or retime the study.",
            "The exact algebra check is a spot check, not an independent proof of every theorem.",
            "The feasible-witness extension was not a separate performance catalogue.",
            "The R46 catalogue contains no new direct expected-policy-cost comparison.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root or extracted R46 study artifact root.",
    )
    parser.add_argument(
        "--artifact-zip",
        type=Path,
        default=None,
        help="Optional downloaded nbo-r46-study ZIP for digest verification.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path. Standard output is always written.",
    )
    args = parser.parse_args()

    result = audit(args.root.resolve(), args.artifact_zip)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.output is not None:
        args.output.write_text(text)


if __name__ == "__main__":
    main()
