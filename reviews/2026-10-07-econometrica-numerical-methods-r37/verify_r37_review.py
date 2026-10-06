#!/usr/bin/env python3
"""Independent deterministic checks for the NBO R37 advisory review.

This script does not rerun the measured services. It verifies the committed
protocol, summary ledger, source hashes, reported comparison arithmetic, and
the central exact matrix identity used by the precision-refresh theorem.
Only the Python standard library is required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

getcontext().prec = 50
REL = Path("revisions/2026-10-07-r37")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pct_reduction(old: Decimal, new: Decimal) -> Decimal:
    return (old - new) / old * Decimal(100)


def mm(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((x * y for x, y in zip(row, col)), Fraction()) for col in zip(*b)]
        for row in a
    ]


def madd(
    a: list[list[Fraction]],
    b: list[list[Fraction]],
    scale: Fraction = Fraction(1),
) -> list[list[Fraction]]:
    return [
        [x + scale * y for x, y in zip(ar, br)]
        for ar, br in zip(a, b)
    ]


def mscale(a: list[list[Fraction]], scale: Fraction) -> list[list[Fraction]]:
    return [[scale * x for x in row] for row in a]


def matrix_identity_check() -> bool:
    # A non-diagonal exact rational test of
    # C(3I-C)^2/4-I = (-3E^2+E^3)/4, C=I+E.
    E = [
        [Fraction(1, 5), Fraction(1, 10)],
        [Fraction(1, 10), Fraction(-1, 10)],
    ]
    I = [[Fraction(1), Fraction()], [Fraction(), Fraction(1)]]
    C = madd(I, E)
    three_i_minus_c = madd(mscale(I, Fraction(3)), C, Fraction(-1))
    lhs = madd(
        mscale(mm(mm(C, three_i_minus_c), three_i_minus_c), Fraction(1, 4)),
        I,
        Fraction(-1),
    )
    E2 = mm(E, E)
    E3 = mm(E2, E)
    rhs = mscale(madd(mscale(E2, Fraction(-3)), E3), Fraction(1, 4))
    return lhs == rhs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    summary_path = root / REL / "results/SUMMARY.json"
    protocol_path = root / REL / "protocols/PROTOCOL.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))

    assert protocol["dimension"] == 2
    assert protocol["horizon"] == 4
    assert protocol["requested_full_policy_tolerance"] == "1/10000"
    assert summary["services"] == 8
    assert summary["certified"] == 8
    assert all(row["simulation_transitions"] == 0 for row in summary["rows"])
    assert summary["source_freeze_commit"] == "2b43dce935af3ee2e1b4cb2edb5e614f24f81ac9"

    by_key = {(row["method"], row["regime"]): row for row in summary["rows"]}
    required = {
        ("linear-warm", "anchor"),
        ("linear-warm", "changed-valuation"),
        ("quadratic-refresh", "anchor"),
        ("quadratic-refresh", "changed-valuation"),
        ("adaptive-cached", "anchor"),
        ("adaptive-cached", "changed-valuation"),
        ("structural", "anchor"),
        ("structural", "changed-valuation"),
    }
    assert set(by_key) == required

    def D(value: Any) -> Decimal:
        return Decimal(str(value))

    fixed_anchor = by_key[("quadratic-refresh", "anchor")]
    fixed_changed = by_key[("quadratic-refresh", "changed-valuation")]
    adaptive_anchor = by_key[("adaptive-cached", "anchor")]
    adaptive_changed = by_key[("adaptive-cached", "changed-valuation")]
    structural_anchor = by_key[("structural", "anchor")]
    structural_changed = by_key[("structural", "changed-valuation")]

    assert fixed_anchor["total_hidden_updates"] == adaptive_anchor["total_hidden_updates"] == 6
    assert fixed_changed["total_hidden_updates"] == adaptive_changed["total_hidden_updates"] == 3
    assert fixed_anchor["training_target_inverse_builds"] == 6
    assert adaptive_anchor["training_target_inverse_builds"] == 3
    assert fixed_changed["training_target_inverse_builds"] == 3
    assert adaptive_changed["training_target_inverse_builds"] == 3

    source_hashes_verified = 0
    for rel, expected in summary["source_files_sha256"].items():
        path = root / rel
        actual = sha256(path)
        assert actual == expected, f"Source hash mismatch: {rel}"
        source_hashes_verified += 1

    gaps = [
        D(row["policy_gap_upper"])
        for row in summary["rows"]
        if row["method"] != "structural"
    ]
    largest_nonstructural_gap = max(gaps)
    target = Decimal(1) / Decimal(10000)

    result = {
        "status": "passed",
        "reviewed_snapshot": {
            "branch": "revision/econometrica-nbo-r37-review-ready-2026-10-07",
            "commit": "9792d3dee69351f672dcc09098422b35207060a7",
            "tree": "df6abbbd45f46c0aed6b1345a895e3e33ce6c503",
        },
        "checks": {
            "protocol_dimension": protocol["dimension"],
            "protocol_horizon": protocol["horizon"],
            "services": summary["services"],
            "certified_services": summary["certified"],
            "zero_simulation_transition_services": sum(
                row["simulation_transitions"] == 0 for row in summary["rows"]
            ),
            "source_hashes_verified": source_hashes_verified,
            "newton_schulz_gram_identity_exact": matrix_identity_check(),
        },
        "derived": {
            "adaptive_bits_reduction_percent": {
                "anchor": float(
                    pct_reduction(
                        D(fixed_anchor["fractional_bits_sum"]),
                        D(adaptive_anchor["fractional_bits_sum"]),
                    )
                ),
                "changed_valuation": float(
                    pct_reduction(
                        D(fixed_changed["fractional_bits_sum"]),
                        D(adaptive_changed["fractional_bits_sum"]),
                    )
                ),
            },
            "adaptive_clock_reduction_percent": {
                "anchor": float(
                    pct_reduction(
                        D(fixed_anchor["complete_service_seconds"]),
                        D(adaptive_anchor["complete_service_seconds"]),
                    )
                ),
                "changed_valuation": float(
                    pct_reduction(
                        D(fixed_changed["complete_service_seconds"]),
                        D(adaptive_changed["complete_service_seconds"]),
                    )
                ),
            },
            "structural_speed_ratio_over_adaptive": {
                "anchor": float(
                    D(adaptive_anchor["complete_service_seconds"])
                    / D(structural_anchor["complete_service_seconds"])
                ),
                "changed_valuation": float(
                    D(adaptive_changed["complete_service_seconds"])
                    / D(structural_changed["complete_service_seconds"])
                ),
            },
            "largest_nonstructural_policy_gap": float(largest_nonstructural_gap),
            "requested_policy_tolerance": float(target),
            "target_to_largest_nonstructural_gap_ratio": float(
                target / largest_nonstructural_gap
            ),
            "adaptive_and_fixed_update_counts_match": True,
            "anchor_inverse_build_difference": 3,
            "changed_inverse_build_difference": 0,
        },
        "scope": [
            "The script verifies committed deterministic records; it does not rerun or retime the eight services.",
            "The exact identity check is a spot check of the theorem's central polynomial identity, not an independent proof of every theorem.",
            "Clock reductions are descriptive single-execution comparisons, not sampling-based performance estimates.",
        ],
    }
    assert result["checks"]["newton_schulz_gram_identity_exact"] is True

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
