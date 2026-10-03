#!/usr/bin/env python3
"""Reviewer ledger diagnostics for the pinned NBO R11 evidence snapshot.

This script does not retrain policies and does not replace the repository's raw
array replay. It independently recomputes method-level arithmetic from the
committed JSON ledgers and verifies one representative empirical-Bernstein row.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
R11 = ROOT / "revisions/2026-10-04-r11"
RESULTS = R11 / "results"
PRIMARY_RE = re.compile(
    r"(nbo|dpo|linear)_d(10|20|50)_s(\d+)_n1024_r1_mean0_sd0"
)
FIT_RE = re.compile(r"(nbo|dpo|linear)_d(10|20|50)_s(\d+)")


def load_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evaluations: list[dict[str, Any]] = []
    fits: list[dict[str, Any]] = []
    for path in sorted(RESULTS.rglob("*.json")):
        try:
            record = json.loads(path.read_text())
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(record, dict) and "bound" in record and "constants" in record:
            record["_path"] = str(path.relative_to(ROOT))
            evaluations.append(record)
        if isinstance(record, dict) and "requested_iterations" in record:
            record["_path"] = str(path.relative_to(ROOT))
            fits.append(record)
    return evaluations, fits


def median(values: list[float]) -> float:
    if not values:
        raise AssertionError("empty median")
    return float(statistics.median(values))


def main(output: Path | None = None) -> dict[str, Any]:
    evaluations, fits = load_records()
    primary = [r for r in evaluations if PRIMARY_RE.fullmatch(r["id"])]
    if len(primary) != 90:
        raise AssertionError(f"expected 90 primary records, found {len(primary)}")

    audit = json.loads((RESULTS / "AUDIT.json").read_text())
    compilation = json.loads((RESULTS / "COMPILATION.json").read_text())
    remote = json.loads((R11 / "REMOTE_EXECUTION.json").read_text())
    protocol = json.loads((R11 / "PROTOCOL.json").read_text())

    groups: dict[tuple[int, str], list[dict[str, Any]]] = {}
    by_seed: dict[tuple[int, str, int], dict[str, Any]] = {}
    for record in primary:
        match = PRIMARY_RE.fullmatch(record["id"])
        assert match is not None
        method, d_text, seed_text = match.groups()
        d, seed = int(d_text), int(seed_text)
        groups.setdefault((d, method), []).append(record)
        by_seed[(d, method, seed)] = record

    comparisons: list[dict[str, Any]] = []
    rho, horizon = 0.04, 1.0
    annuity = (1.0 - math.exp(-rho * horizon)) / rho

    for d in (10, 20, 50):
        nbo = groups[(d, "nbo")]
        dpo = groups[(d, "dpo")]
        if len(nbo) != 10 or len(dpo) != 10:
            raise AssertionError(f"unexpected group size for d={d}")

        nbo_mean = statistics.fmean(r["bound"]["mean"] for r in nbo)
        dpo_mean = statistics.fmean(r["bound"]["mean"] for r in dpo)
        nbo_min_lower = min(r["bound"]["lower"] for r in nbo)
        dpo_min_lower = min(r["bound"]["lower"] for r in dpo)
        anchor = max(r["constants"]["anchor_upper"] for r in nbo)

        fit_nbo = [
            r for r in fits
            if r.get("method") == "nbo"
            and r.get("dimension") == d
            and r.get("requested_iterations") == 120
            and r.get("width") == 32
            and FIT_RE.fullmatch(r.get("id", ""))
        ]
        fit_dpo = [
            r for r in fits
            if r.get("method") == "dpo"
            and r.get("dimension") == d
            and r.get("requested_iterations") == 120
            and r.get("width") == 32
            and FIT_RE.fullmatch(r.get("id", ""))
        ]
        if len(fit_nbo) != 10 or len(fit_dpo) != 10:
            raise AssertionError(f"unexpected fit count for d={d}")

        seed_differences = []
        for seed in protocol["training_seeds"]:
            seed_differences.append(
                by_seed[(d, "nbo", seed)]["bound"]["mean"]
                - by_seed[(d, "dpo", seed)]["bound"]["mean"]
            )

        comparisons.append({
            "dimension": d,
            "nbo_mean_paired_statistic": nbo_mean,
            "dpo_mean_paired_statistic": dpo_mean,
            "nbo_minus_dpo_mean": nbo_mean - dpo_mean,
            "nbo_minus_dpo_seed_range": [
                min(seed_differences), max(seed_differences)
            ],
            "nbo_relative_mean_advantage_percent":
                100.0 * (nbo_mean / dpo_mean - 1.0),
            "nbo_min_lower": nbo_min_lower,
            "dpo_min_lower": dpo_min_lower,
            "anchor_upper": anchor,
            "nbo_min_lower_fraction_of_anchor": nbo_min_lower / anchor,
            "nbo_min_lower_flow_equivalent_percent":
                100.0 * math.expm1(nbo_min_lower / annuity),
            "nbo_target_count": sum(
                r["bound"]["lower"] >= 0.0005 for r in nbo
            ),
            "dpo_target_count": sum(
                r["bound"]["lower"] >= 0.0005 for r in dpo
            ),
            "nbo_median_train_seconds": median([r["seconds"] for r in fit_nbo]),
            "dpo_median_train_seconds": median([r["seconds"] for r in fit_dpo]),
            "nbo_training_overhead_percent":
                100.0 * (
                    median([r["seconds"] for r in fit_nbo])
                    / median([r["seconds"] for r in fit_dpo]) - 1.0
                ),
            "nbo_median_verify_seconds": median([r["seconds"] for r in nbo]),
            "dpo_median_verify_seconds": median([r["seconds"] for r in dpo]),
            "nbo_verification_overhead_percent":
                100.0 * (
                    median([r["seconds"] for r in nbo])
                    / median([r["seconds"] for r in dpo]) - 1.0
                ),
            "direct_pairwise_certificate_present": False,
        })

    state_stress = [
        r for r in evaluations
        if r.get("method") == "nbo"
        and "_s11_" in r.get("id", "")
        and (float(r.get("shift", 0.0)) != 0.0
             or float(r.get("spread", 0.0)) != 0.0)
        and "width" not in r.get("id", "")
        and "_long_" not in r.get("id", "")
    ]
    if len(state_stress) != 18:
        raise AssertionError(
            f"expected 18 primary initial-state stress rows, found {len(state_stress)}"
        )

    representative_path = (
        RESULTS / "seed_11" / "nbo_d10_s11_n1024_r1_mean0_sd0.json"
    )
    representative = json.loads(representative_path.read_text())
    bound = representative["bound"]
    constants = representative["constants"]
    ell = math.log(2.0 * bound["family_size"] / bound["alpha"])
    margin = (
        math.sqrt(2.0 * bound["sample_sd"] ** 2 * ell / bound["paths"])
        + 14.0 * constants["clipping_threshold"] * ell
          / (3.0 * (bound["paths"] - 1))
    )
    reconstructed_lower = (
        bound["mean"] - margin - constants["bias_upper"]
        - constants["clipping_bias"]
    )

    root_readme = (ROOT / "README.md").read_text()
    readme_stale = (
        "September 28" in root_readme
        and "revisions/2026-09-28" in root_readme
        and "2026-10-04-r11" not in root_readme
    )

    result: dict[str, Any] = {
        "schema_version": 1,
        "reviewed_commit": "840565f451be6103aeb325a8fc548a57507a8fb2",
        "scope": (
            "Independent arithmetic over committed R11 ledgers; no retraining, "
            "no independent raw-array replay, and no formal runtime verification."
        ),
        "annuity_factor": annuity,
        "method_comparisons": comparisons,
        "state_stress": {
            "rows": len(state_stress),
            "positive_lower_endpoints": sum(
                r["bound"]["lower"] > 0.0 for r in state_stress
            ),
            "negative_mean_paired_statistics": sum(
                r["bound"]["mean"] < 0.0 for r in state_stress
            ),
            "all_or_nearly_all_internal_states_outside_training_box": sum(
                r.get("outside_training_box_frequency", 0.0) >= 0.99
                for r in state_stress
            ),
        },
        "representative_empirical_bernstein_reconstruction": {
            "record": str(representative_path.relative_to(ROOT)),
            "recorded_margin": bound["empirical_bernstein_margin"],
            "reconstructed_margin": margin,
            "recorded_lower": bound["lower"],
            "reconstructed_lower_from_recorded_mean_sd": reconstructed_lower,
            "absolute_lower_difference":
                abs(bound["lower"] - reconstructed_lower),
        },
        "evidence_ledger": {
            "primary_policies": audit["primary_policies"],
            "two_sided_rows": audit["all_two_sided_rows"],
            "used_one_sided_statements": audit["used_one_sided_statements"],
            "allocated_one_sided_statements":
                audit["allocated_one_sided_statements"],
            "training_failures": len(audit["training_failures"]),
            "main_pages": compilation["ECTA"]["pages"],
            "supplement_pages": compilation["supp"]["pages"],
            "response_pages": compilation["response"]["pages"],
            "initial_state_failures_recovered":
                remote["initial_state_recovery"]["recovered_evaluations"],
            "initial_state_failures_unresolved":
                remote["initial_state_recovery"]["unresolved"],
            "refitted_policies_for_recovery":
                remote["initial_state_recovery"]["refitted_policies"],
        },
        "repository_surface": {
            "root_readme_stale_for_r11": readme_stale,
        },
        "interpretation": [
            "Both NBO and direct policy meet the declared gain target in every primary seed.",
            "The committed evidence does not contain a direct simultaneous NBO-minus-DPO certificate.",
            "Most declared shifted/dispersed state stresses do not have a positive lower endpoint.",
            "The certified lower improvement tightens only a small fraction of the inherited anchor regret bound.",
        ],
    }

    if output is not None:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    print(json.dumps(main(args.output), indent=2, sort_keys=True))
