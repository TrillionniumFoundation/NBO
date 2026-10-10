#!/usr/bin/env python3
"""Independent deterministic audit for the Econometrica numerical-methods review of NBO R61.

The script audits the frozen R61 publication-audit artifact. It does not retrain,
resimulate, rebuild LaTeX, or retime any service. All timing summaries are
therefore descriptive properties of the deposited records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any

EXPECTED_ARTIFACT_SHA256 = "144cc465cb625473d23d14547accd839a517e851ea1a01af1c8b3f64383c672b"
EXPECTED_COMMIT = "19f17cef194b620cfbf9d33e7c78ee051a2dddf0"
EXPECTED_TREE = "2a7fc185511a78eaf447a01e70f168b05cc839ae"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise TypeError(f"Expected JSON object in {path}")
    return data


def fsummary(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "minimum": min(values),
        "median": statistics.median(values),
        "mean": statistics.fmean(values),
        "maximum": max(values),
    }


def root_free_candidates(values: list[Fraction]) -> set[int]:
    """Candidate indices from the concave-prefix/convex-tail lemma."""
    n = len(values)
    if n <= 2:
        return set(range(n))
    first = [values[j + 1] - values[j] for j in range(n - 1)]
    second = [first[j + 1] - first[j] for j in range(n - 2)]
    out = {0, n - 1}
    j0 = next((j for j, x in enumerate(second) if x >= 0), None)
    if j0 is None:
        return out
    out.add(j0)
    k = next((j for j in range(j0, len(first)) if first[j] >= 0), None)
    if k is not None:
        out.add(k)
    return out


def exact_root_free_spot_check(cases: int = 50_000) -> dict[str, Any]:
    rng = random.Random(6102026)
    mismatches: list[dict[str, Any]] = []
    for case in range(cases):
        n = rng.randint(2, 80)
        q = rng.randint(1, 19)
        d0 = Fraction(rng.randint(-20, 20), rng.randint(1, 11))
        d1 = Fraction(rng.randint(-30, 30), rng.randint(1, 13))
        d2 = Fraction(rng.randint(-30, 30), rng.randint(1, 13))
        c4 = Fraction(rng.randint(0, 12), rng.randint(1, 13))
        vals = []
        for j in range(n):
            a = Fraction(j, q)
            vals.append(d0 + d1 * a + d2 * a * a + c4 * a**4)
        brute = min(range(n), key=lambda j: (vals[j], j))
        cand = min(root_free_candidates(vals), key=lambda j: (vals[j], j))
        if brute != cand:
            mismatches.append({"case": case, "n": n, "q": q, "brute": brute, "candidate": cand})
            if len(mismatches) >= 5:
                break
    return {"cases": cases, "mismatches": mismatches, "passed": not mismatches}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-root", type=Path, required=True, help="Directory containing the extracted audit JSON files")
    ap.add_argument("--artifact-zip", type=Path, help="Optional original workflow artifact ZIP")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    root = args.audit_root
    pub = load(root / "PUBLICATION_FACTS61.json")
    science = load(root / "SCIENCE_REPLAY61.json")
    factorial = load(root / "FACTORIAL_AUDIT61.json")
    tests = load(root / "TESTS61.json")
    assembly = load(root / "ASSEMBLY61.json")
    revalidation = load(root / "REVALIDATION_REPLAY61.json")

    assert pub["status"] == science["status"] == factorial["status"] == revalidation["status"] == "passed"
    assert science["services"] == pub["services"] == 96
    assert science["attained"] == pub["attained"] == 80
    assert science["budget_exhausted"] == pub["budget_exhausted"] == 16
    assert science["new_training_services"] == 0
    assert science["new_independent_path_observations"] == 0
    assert assembly["scientific_sources_changed"] is False
    assert assembly["substantive_original_labels_removed"] is False

    verified_hashes = 0
    for rel, expected in pub["source_hashes"].items():
        target = root.parent / rel
        if not target.exists():
            continue
        actual = sha256(target)
        if actual != expected:
            raise AssertionError(f"Hash mismatch for {rel}: {actual} != {expected}")
        verified_hashes += 1

    artifact_digest = None
    if args.artifact_zip:
        artifact_digest = sha256(args.artifact_zip)
        if artifact_digest != EXPECTED_ARTIFACT_SHA256:
            raise AssertionError(f"Artifact digest mismatch: {artifact_digest}")

    rows = science["rows"]
    by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_mode[row["mode"]].append(row)

    mode_summary: dict[str, Any] = {}
    for mode, rr in sorted(by_mode.items()):
        times = [float(r["complete_return_seconds"]) for r in rr]
        mode_summary[mode] = {
            "services": len(rr),
            "attained": sum(r["status"] == "target_attained" for r in rr),
            "budget_exhausted": sum(r["status"] == "budget_exhausted" for r in rr),
            "complete_return_seconds": fsummary(times),
        }

    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[(r["d"], r["T"], r["target"], r["seed"], r["worker"])].append(r)
    common_fastest = 0
    fastest_counts: Counter[str] = Counter()
    for rr in groups.values():
        fastest = min(rr, key=lambda x: float(x["complete_return_seconds"]))["mode"]
        fastest_counts[fastest] += 1
        common_fastest += fastest == "common-only"

    keyed = {(r["d"], r["T"], r["target"], r["seed"], r["worker"], r["mode"]): r for r in rows}
    native_savings: list[float] = []
    native_faster = 0
    for d, T, target, seed, worker in groups:
        n = keyed[(d, T, target, seed, worker, "relu-native")]
        s = keyed[(d, T, target, seed, worker, "relu-screened")]
        nt = float(n["complete_return_seconds"])
        st = float(s["complete_return_seconds"])
        saving = 100.0 * (st - nt) / st
        native_savings.append(saving)
        native_faster += nt < st

    paired_counts: dict[str, Counter[str]] = {k: Counter() for k in ("common-only", "quadratic-native", "relu-screened")}
    for record in science["paired"]:
        for comparator, entry in record["contrasts"].items():
            if entry.get("identity") is True or entry.get("interval") == [0.0, 0.0]:
                paired_counts[comparator]["identity"] += 1
                continue
            lower, upper = map(float, entry["interval"])
            if upper < 0:
                paired_counts[comparator]["native_lower_cost"] += 1
            elif lower > 0:
                paired_counts[comparator]["native_higher_cost"] += 1
            else:
                paired_counts[comparator]["unresolved"] += 1

    fixed_bounds = [float(x["bound"]) for x in pub["fixed_bounds"]]
    fixed_target_counts = {
        "at_most_1_8": sum(x <= 1 / 8 for x in fixed_bounds),
        "at_most_1_16": sum(x <= 1 / 16 for x in fixed_bounds),
    }

    factorial_rows = factorial["reduced_representation_search_contrasts"]
    factorial_summary = [
        {
            "worker": x["worker"],
            "width": x["width"],
            "lattice": x["size"],
            "instances": x["instances"],
            "piecewise_faster": x["reduced_piecewise_faster"],
            "median_saving_percent": 100.0 * float(x["median_fraction_saved"]),
        }
        for x in factorial_rows
    ]

    multi_ratios = [float(x["adaptive_seconds"]) / float(x["exhaustive_seconds"]) for x in science["two_controls"]]
    multi_fallbacks = sum(bool(x["fallback"]) for x in science["two_controls"])

    test_counts = {name: int(value["tests"]) for name, value in tests.items()}
    assert all(value["status"] == "passed" for value in tests.values())

    root_free = exact_root_free_spot_check()
    if not root_free["passed"]:
        raise AssertionError(f"Root-free spot check failed: {root_free['mismatches']}")

    result = {
        "status": "passed",
        "reviewed_snapshot": {
            "branch": "revision/econometrica-nbo-r61-review-ready-2026-10-09",
            "commit": EXPECTED_COMMIT,
            "tree": EXPECTED_TREE,
        },
        "artifact": {
            "id": 11626669714,
            "name": "nbo-r61-paper-and-publication-audit",
            "sha256": artifact_digest or EXPECTED_ARTIFACT_SHA256,
        },
        "audit_checks": {
            "published_audit_hashes_verified_in_compact_artifact": verified_hashes,
            "services": science["services"],
            "attained": science["attained"],
            "budget_exhausted": science["budget_exhausted"],
            "protected_predecessor_files_checked": science["protected_files_checked"],
            "scientific_input_files_checked": science["scientific_files_checked"],
            "scalar_solver_records": science["counts"]["scalar_solver_records"],
            "cell_date_decisions": science["counts"]["cell_decisions"],
            "confidence_interval_records": science["counts"]["ci_records"],
            "original_law_path_rows_reconstructed": science["counts"]["distinct_path_rows"],
            "native_factorial_exact_answers": factorial["checked_exact_answers"],
            "fixed_policy_actors": revalidation["actors"],
            "new_training_services": science["new_training_services"],
            "new_independent_policy_cost_observations": science["new_independent_path_observations"],
            "test_counts_in_compact_artifact": test_counts,
        },
        "service_comparison": {
            "mode_summary": mode_summary,
            "mathematical_service_groups": len(groups),
            "fastest_mode_counts": dict(fastest_counts),
            "common_only_fastest_groups": common_fastest,
            "relu_native_vs_screened": {
                "paired_services": len(native_savings),
                "native_faster": native_faster,
                "native_slower": len(native_savings) - native_faster,
                "saving_percent": fsummary(native_savings),
            },
        },
        "policy_cost_comparison": {k: dict(v) for k, v in paired_counts.items()},
        "original_optimum": {
            "centered_final_gap": float(pub["centered_final_gap"]),
            "centered_cumulative_seconds": float(pub["centered_total_work"]),
            "fixed_policy_bounds": fixed_bounds,
            "fixed_policy_target_counts": fixed_target_counts,
        },
        "native_factorial": {
            "checked_exact_answers": factorial["checked_exact_answers"],
            "rows": factorial_summary,
        },
        "multi_action_query": {
            "records": len(science["two_controls"]),
            "fallbacks": multi_fallbacks,
            "adaptive_to_exhaustive_time_ratio": fsummary(multi_ratios),
        },
        "independent_exact_spot_check": {
            "root_free_quartic_piece": root_free,
        },
        "scope": [
            "The audit verifies frozen records and arithmetic; it does not retrain, resimulate, rebuild the publication, or retime services.",
            "Worker repetitions reuse the same mathematical designs, policies, and statistical streams and are not independent economic observations.",
            "The root-free check is an independent exact-arithmetic spot check of the discrete quartic lemma, not a proof of every theorem in the cumulative manuscript.",
            "Complete publication status and the 204-test, seven-document clean rebuild are separately pinned by FINAL_DELIVERY61.json on the canonical branch.",
        ],
    }

    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
