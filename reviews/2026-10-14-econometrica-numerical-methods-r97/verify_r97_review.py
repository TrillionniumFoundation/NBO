#!/usr/bin/env python3
"""Independent finite-catalogue audit for the NBO R97 referee package.

Uses only the Python standard library. It verifies the downloaded artifact,
release identities, process exits, matched LS/CA comparisons, timing catalogue,
operation counts, price-grid classifications, and the independent-audit ledger.
It does not refit models or create new economic observations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import tempfile
import zipfile
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def median(values: list[float]) -> float:
    require(bool(values), "cannot take median of empty collection")
    return float(statistics.median(values))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision-root", type=Path)
    parser.add_argument("--artifact-zip", type=Path)
    parser.add_argument("--expected-artifact-sha256",
                        default="0ba9775b8ccb3ce81d268795dd7f5ad22ca02d24515ed501b779bfff5d2bec75")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def audit(root: Path, artifact_zip: Path | None, expected_artifact: str) -> dict[str, Any]:
    if artifact_zip is not None:
        require(artifact_zip.is_file(), f"missing artifact: {artifact_zip}")
        artifact_hash = sha256(artifact_zip)
        require(artifact_hash == expected_artifact,
                f"artifact SHA mismatch: {artifact_hash}")
    else:
        artifact_hash = None

    release = load(root / "RELEASE97.json")
    require(release["status"] == "verified", "release is not verified")

    identity_checks = 0
    for rel, expected in release["source_sha256"].items():
        path = root / rel
        require(path.is_file(), f"missing source-bound file: {rel}")
        require(sha256(path) == expected, f"source hash mismatch: {rel}")
        identity_checks += 1
    for name, item in release["documents"].items():
        path = root / "build" / f"{name}.pdf"
        require(path.is_file(), f"missing PDF: {name}")
        require(sha256(path) == item["sha256"], f"PDF hash mismatch: {name}")
        require(path.stat().st_size == item["bytes"], f"PDF size mismatch: {name}")
        identity_checks += 1

    campaign = load(root / "results97" / "CAMPAIGN97.json")
    configs = campaign["configurations"]
    timings = campaign["timings"]
    require(len(configs) == 84, f"expected 84 configurations, got {len(configs)}")
    require(len(timings) == 42, f"expected 42 timings, got {len(timings)}")
    require(all(row["exit_code"] == 0 for row in configs), "failed acquisition process")
    require(all(row["exit_code"] == 0 for row in timings), "failed timing process")
    arm_counts = Counter(row["arm"] for row in configs)
    require(set(arm_counts.values()) == {12}, f"unbalanced acquisition arms: {arm_counts}")

    summary = load(root / "results97" / "SUMMARY97.json")
    rows = summary["budget_rows"]
    require(summary["budget_pairs"] == 36 == len(rows), "budget-pair count mismatch")
    require(summary["strict_span_improvements"] == 36, "not all spans improved")
    abs_improvements: list[float] = []
    rel_improvements: list[float] = []
    direction = Counter()
    family = defaultdict(lambda: {"ls": 0, "ca": 0, "rel": [], "direction": Counter()})
    for row in rows:
        ls_span = float(row["ls_span"])
        ca_span = float(row["ca_span"])
        require(ca_span < ls_span, f"non-improving span: {row}")
        delta = ls_span - ca_span
        abs_improvements.append(delta)
        rel_improvements.append(delta / ls_span)
        ls_r = int(row["ls_rejected"])
        ca_r = int(row["ca_rejected"])
        key = "improved" if ca_r < ls_r else "equal" if ca_r == ls_r else "worsened"
        direction[key] += 1
        fam = family[row["family"]]
        fam["ls"] += ls_r
        fam["ca"] += ca_r
        fam["rel"].append(delta / ls_span)
        fam["direction"][key] += 1

    timing_groups: dict[str, list[float]] = defaultdict(list)
    for row in timings:
        timing_groups[f"risk{row['index']}:{row['arm']}"].append(float(row["seconds"]))
    require(all(len(v) == 3 for v in timing_groups.values()), "timing groups are not triplicates")
    timing_medians = {k: median(v) for k, v in sorted(timing_groups.items())}

    operations = load(root / "results97" / "OPERATIONS97.json")
    require(len(operations) == 14, "operation ledger should have 14 arm-risk rows")
    proposal_queries = {
        f"risk{row['risk_index']}:{row['arm']}": int(row["counts"]["terminal_proposal_queries"])
        for row in operations
    }

    price = load(root / "results97" / "PRICE_GRID97.json")
    require(len(price) == 1800, f"expected 1800 price cells, got {len(price)}")
    price_counts = Counter(row["status"] for row in price)
    require(price_counts == Counter({"unresolved": 1445, "reject": 199, "adopt": 156}),
            f"price-grid counts differ: {price_counts}")
    by_comparison: dict[str, Counter[str]] = defaultdict(Counter)
    for row in price:
        lower = Fraction(row["lower"])
        upper = Fraction(row["upper"])
        status = row["status"]
        require(lower <= upper, "invalid price interval")
        if status == "adopt":
            require(lower > 0, "adopt cell lacks positive lower endpoint")
        elif status == "reject":
            require(upper < 0, "reject cell lacks negative upper endpoint")
        else:
            require(lower <= 0 <= upper, "unresolved cell does not contain zero")
        by_comparison[f"{row['arm']} vs {row['baseline']}"][status] += 1
    adoptions_over_quadratic = sum(
        counts["adopt"] for key, counts in by_comparison.items()
        if key.endswith("vs quadratic-ls")
    )
    require(adoptions_over_quadratic == 0,
            "a candidate is classified adopted over quadratic LS")

    independent = load(root / "audit97" / "INDEPENDENT97.json")
    replay_rows = sum(int(row["rows"]) for row in independent["proposal_replay"])
    require(independent["discrepancies"] == [], "independent audit records discrepancies")
    require(independent["old_rows_statistically_recomputed"] == 32768,
            "statistical replay row mismatch")
    require(replay_rows == 32768, "proposal replay row mismatch")
    require(len(independent["exact_statistics"]) == 12, "exact-statistic count mismatch")
    require(all(row["contained"] for row in independent["exact_statistics"]),
            "an exact statistic is not contained")
    require(len(independent["rational_endpoints"]) == 24,
            "rational-endpoint count mismatch")
    require(all(row["contained"] for row in independent["rational_endpoints"]),
            "a rational endpoint check failed")

    return {
        "status": "passed",
        "reviewed_commit": "f802fe64d91d9f5c1c8f86123b0fbe114e622279",
        "artifact_sha256": artifact_hash,
        "release_identity_checks": identity_checks,
        "acquisition_processes": len(configs),
        "timing_processes": len(timings),
        "matched_pairs": len(rows),
        "span_improvements": {
            "strict": len(rows),
            "absolute_min": min(abs_improvements),
            "absolute_median": median(abs_improvements),
            "absolute_max": max(abs_improvements),
            "relative_median": median(rel_improvements),
        },
        "rejections": {
            "ls_total": sum(int(row["ls_rejected"]) for row in rows),
            "ca_total": sum(int(row["ca_rejected"]) for row in rows),
            "delta": sum(int(row["ca_rejected"] - row["ls_rejected"]) for row in rows),
            "cell_direction": dict(direction),
            "by_family": {
                key: {
                    "ls_total": value["ls"],
                    "ca_total": value["ca"],
                    "delta": value["ca"] - value["ls"],
                    "relative_span_improvement_median": median(value["rel"]),
                    "cell_direction": dict(value["direction"]),
                }
                for key, value in sorted(family.items())
            },
        },
        "timing_medians_seconds": timing_medians,
        "terminal_proposal_queries": proposal_queries,
        "price_grid": {
            "cells": len(price),
            "counts": dict(price_counts),
            "adoptions_over_quadratic_ls": adoptions_over_quadratic,
            "by_comparison": {k: dict(v) for k, v in sorted(by_comparison.items())},
        },
        "independent_audit": {
            "statistical_rows": independent["old_rows_statistically_recomputed"],
            "proposal_rows": replay_rows,
            "exact_statistics": len(independent["exact_statistics"]),
            "rational_endpoints": len(independent["rational_endpoints"]),
            "discrepancies": len(independent["discrepancies"]),
        },
        "scope": [
            "The script audits the frozen finite catalogue and identities; it does not refit models.",
            "The script creates no new policy-cost observations or timing samples.",
            "Timing ranges are descriptive and not future-hardware confidence intervals.",
        ],
    }


def main() -> None:
    args = parse_args()
    temp: tempfile.TemporaryDirectory[str] | None = None
    try:
        root = args.revision_root
        if root is None:
            require(args.artifact_zip is not None, "provide --revision-root or --artifact-zip")
            temp = tempfile.TemporaryDirectory(prefix="nbo-r97-review-")
            with zipfile.ZipFile(args.artifact_zip) as archive:
                archive.extractall(temp.name)
            root = Path(temp.name)
        result = audit(root, args.artifact_zip, args.expected_artifact_sha256)
        text = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(text, encoding="utf-8")
        print(text, end="")
    finally:
        if temp is not None:
            temp.cleanup()


if __name__ == "__main__":
    main()
