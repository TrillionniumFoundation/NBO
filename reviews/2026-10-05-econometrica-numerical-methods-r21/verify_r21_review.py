#!/usr/bin/env python3
"""Deterministic independent checks for the R21 Econometrica review.

The script uses only Python's standard library and the committed publication
records. It does not refit a model, replace any recorded clock, or create a new
scientific observation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

R21 = Path("revisions/2026-10-05-r21")
R19 = Path("revisions/2026-10-05-r19-integrated")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def parse_frontier_tables(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    tables = re.findall(
        r"dimension (10|50).*?\\begin\{tabular\}\{rrrrrrr\}(.*?)\\end\{tabular\}",
        text,
        flags=re.S,
    )
    winners: list[dict[str, Any]] = []
    methods = ["Quadratic", "RBF", "NBO", "Actor", "SAA", "Enumeration"]
    for dim, body in tables:
        for line in body.splitlines():
            if "&" not in line or "\\" not in line:
                continue
            fields = [x.strip() for x in line.split("\\\\", 1)[0].split("&")]
            if len(fields) != 7 or not fields[0].isdigit():
                continue
            q = int(fields[0])
            values: dict[str, float] = {}
            for name, raw in zip(methods, fields[1:]):
                number = re.match(r"([0-9.]+)", raw)
                if number:
                    values[name] = float(number.group(1))
            qualified = {k: v for k, v in values.items() if k != "Actor"}
            winner = min(qualified, key=qualified.get)
            winners.append(
                {"dimension": int(dim), "queries": q, "winner": winner, "cost": qualified[winner]}
            )
    if len(winners) != 12:
        raise AssertionError(f"expected 12 R19 frontier cells, found {len(winners)}")
    return {
        "cells": winners,
        "winner_counts": dict(Counter(x["winner"] for x in winners)),
        "nbo_wins": sum(x["winner"] == "NBO" for x in winners),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    future_path = root / R21 / "results/FUTURE_TABLES.json"
    release_path = root / R21 / "results/RELEASE_AUDIT.json"
    frontier_path = root / R19 / "results/generated/frontier_tables.tex"
    for path in (future_path, release_path, frontier_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    future = load_json(future_path)
    release = load_json(release_path)
    summaries = {x["service"]: x for x in future["service_summary"]}

    assert future["services"] == 168
    assert future["regime_outcomes"] == 840
    assert summaries["NBO-reuse"]["certified_regimes"] == 72
    assert summaries["NBO-reuse"]["all_futures_certified"] == 0
    assert summaries["NBO-adaptive"]["certified_regimes"] == 120
    assert summaries["NBO-adaptive"]["all_futures_certified"] == 24
    assert summaries["NBO-adaptive"]["refreshes"] == 48
    assert summaries["NBO-refit"]["certified_regimes"] == 120

    fully_certified = {
        name for name, row in summaries.items() if row["all_futures_certified"] == 24
    }
    work_rows: list[dict[str, Any]] = []
    adaptive_refit_ratios: list[float] = []
    for cell in future["work_cells"]:
        costs = cell["costs"]
        qualified = {name: costs[name] for name in fully_certified}
        winner = min(qualified, key=qualified.get)
        ratio = costs["NBO-adaptive"] / costs["NBO-refit"]
        adaptive_refit_ratios.append(ratio)
        work_rows.append(
            {
                "dimension": cell["dimension"],
                "queries_per_future": cell["queries_per_future"],
                "winner": winner,
                "winner_seconds": qualified[winner],
                "nbo_adaptive_seconds": costs["NBO-adaptive"],
                "nbo_refit_seconds": costs["NBO-refit"],
                "adaptive_to_refit_ratio": ratio,
            }
        )
    assert len(work_rows) == 8
    assert all(x["winner"] == "SAA" for x in work_rows)
    assert all(x["adaptive_to_refit_ratio"] > 1 for x in work_rows)

    diagnostic_methods = {
        "NBO-adaptive",
        "NBO-refit",
        "quadratic-adaptive",
        "rbf-adaptive",
        "SAA",
    }
    metrics = ["absolute_risk", "centered_risk", "own_action_risk", "three_action_loss"]
    risk_wins: Counter[tuple[str, str]] = Counter()
    dimensions = sorted({x["dimension"] for x in future["risk_rows"]})
    regimes = sorted({x["future"] for x in future["risk_rows"]})
    for dimension in dimensions:
        for regime in regimes:
            rows = [
                x
                for x in future["risk_rows"]
                if x["dimension"] == dimension
                and x["future"] == regime
                and x["service"] in diagnostic_methods
            ]
            if len(rows) != len(diagnostic_methods):
                raise AssertionError((dimension, regime, len(rows)))
            for metric in metrics:
                best = min(rows, key=lambda x: x[metric])
                risk_wins[(metric, best["service"])] += 1
    assert risk_wins[("absolute_risk", "NBO-adaptive")] == 0
    assert risk_wins[("centered_risk", "NBO-adaptive")] == 0
    assert risk_wins[("own_action_risk", "NBO-adaptive")] == 0
    assert risk_wins[("three_action_loss", "NBO-adaptive")] == 1

    contrast_rows = future["nbo_economic_contrasts"]
    assert len(contrast_rows) == 4
    assert all(x["envelope_over_three_NBO_streams"][1] < 0 for x in contrast_rows)

    economic = {(x["dimension"], x["future"]): x for x in future["economic_intervals"]}
    contrast_checks: list[dict[str, Any]] = []
    for row in contrast_rows:
        d = row["dimension"]
        future_name = row["future"]
        anchor = economic[(d, "anchor")]["mean_optimal_action"]
        changed = economic[(d, future_name)]["mean_optimal_action"]
        exact_difference = [changed[0] - anchor[1], changed[1] - anchor[0]]
        band = row["envelope_over_three_NBO_streams"]
        contains = band[0] <= exact_difference[0] and exact_difference[1] <= band[1]
        assert contains
        contrast_checks.append(
            {
                "dimension": d,
                "future": future_name,
                "nbo_band": band,
                "enumerated_difference_interval": exact_difference,
                "band_width": band[1] - band[0],
                "enumerated_width": exact_difference[1] - exact_difference[0],
            }
        )

    r19_frontier = parse_frontier_tables(frontier_path)
    assert r19_frontier["nbo_wins"] == 1

    documents = {x["document"]: x for x in release["documents"]}
    assert documents["ECTA"]["pages"] == 51
    assert documents["supp"]["pages"] == 232
    assert documents["applications"]["pages"] == 48
    assert release["full_arithmetic_audit"]["attempt_certificates"] == 984
    assert release["full_arithmetic_audit"]["task_certificates"] == 319062

    result = {
        "status": "passed",
        "scope": "deterministic review checks; no refitting and no replacement clocks",
        "files": {
            str(future_path.relative_to(root)): sha256(future_path),
            str(release_path.relative_to(root)): sha256(release_path),
            str(frontier_path.relative_to(root)): sha256(frontier_path),
        },
        "reviewed_publication": {
            "services": future["services"],
            "future_outcomes": future["regime_outcomes"],
            "source_execution": future["source_execution"],
            "publication_pages": {
                "main": documents["ECTA"]["pages"],
                "supplement": documents["supp"]["pages"],
                "applications": documents["applications"]["pages"],
                "response": documents["response"]["pages"],
            },
        },
        "future_change_accuracy": {
            "reuse_certified": summaries["NBO-reuse"]["certified_regimes"],
            "adaptive_certified": summaries["NBO-adaptive"]["certified_regimes"],
            "refit_certified": summaries["NBO-refit"]["certified_regimes"],
            "adaptive_refreshes": summaries["NBO-adaptive"]["refreshes"],
        },
        "future_change_work": {
            "cells": work_rows,
            "accuracy_qualified_winner_counts": dict(Counter(x["winner"] for x in work_rows)),
            "adaptive_more_expensive_than_refit_cells": sum(
                x["adaptive_to_refit_ratio"] > 1 for x in work_rows
            ),
            "adaptive_to_refit_ratio_range": [
                min(adaptive_refit_ratios),
                max(adaptive_refit_ratios),
            ],
        },
        "future_change_risk_winners": {
            f"{metric}:{method}": count
            for (metric, method), count in sorted(risk_wins.items())
        },
        "economic_contrasts": contrast_checks,
        "fixed_future_frontier": r19_frontier,
        "release_audit_counts": {
            "attempt_certificates": release["full_arithmetic_audit"]["attempt_certificates"],
            "additional_zero_charge_certificates": release[
                "additional_zero_charge_certificates_replayed"
            ],
            "task_actions": release["full_arithmetic_audit"]["task_certificates"],
            "evidence_file_hashes": release["full_arithmetic_audit"][
                "evidence_file_hashes_verified"
            ],
        },
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
