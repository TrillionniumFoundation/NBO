#!/usr/bin/env python3
"""Deterministic structural audit for the advisory R84 referee report.

This script uses only the Python standard library.  It reads the frozen R84
files already present in the repository.  It does not refit models, rerun
Bellman services, create new policy-cost observations, or claim to be an
independent implementation of the full numerical method.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


REVIEWED_COMMIT = "c1314494aca25e68f1426b554938e6fe89dd8409"
REVIEWED_TREE = "d799d244898baf319960a3f16f202dc2ec6b18e6"
SCIENCE_SOURCE_COMMIT = "2eac8514e703cc43ad6aba3d4ca8a9b5671c99f7"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def dicts_with_key(value: Any, key: str) -> list[dict[str, Any]]:
    return [item for item in walk(value) if isinstance(item, dict) and key in item]


def all_strings(value: Any) -> list[str]:
    return [item for item in walk(value) if isinstance(item, str)]


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    r84 = repo / "revisions" / "2026-10-12-r84"

    required = {
        "main": r84 / "ECTA.tex",
        "delivery": r84 / "DELIVERY84.md",
        "compatible": r84 / "sections" / "compatible84.tex",
        "actionwise": r84 / "sections" / "actionwise82.tex",
        "frontier": r84 / "sections" / "frontier83.tex",
        "summary": r84 / "results84" / "summary.json",
        "transfer": r84 / "results84" / "transfer.json",
        "independent_audit": r84 / "audit" / "VERIFY84.json",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise SystemExit("missing required R84 files: " + ", ".join(missing))

    summary = load_json(required["summary"])
    transfer = load_json(required["transfer"])
    independent = load_json(required["independent_audit"])
    delivery = required["delivery"].read_text(encoding="utf-8")
    compatible = required["compatible"].read_text(encoding="utf-8")
    actionwise = required["actionwise"].read_text(encoding="utf-8")
    frontier = required["frontier"].read_text(encoding="utf-8")

    assert summary.get("status") == "passed"
    assert summary.get("new_fit_attempts") == 0
    assert summary.get("new_independent_cost_rows") == 0
    assert summary.get("source_commit") == SCIENCE_SOURCE_COMMIT

    assert independent.get("status") == "passed"
    assert independent.get("new_fit_attempts") == 0
    assert independent.get("new_independent_rows") == 0
    assert independent.get("independent_qualification_certificates") == 2548
    assert independent.get("independent_assignment_inequalities") == 16548

    assert transfer.get("new_fits") == 0
    assert transfer.get("new_independent_cost_rows") == 0

    pairwise = transfer.get("pairwise")
    if not isinstance(pairwise, list) or not pairwise:
        raise AssertionError("transfer.json has no pairwise catalogue")
    unresolved = sum(
        1 for item in pairwise
        if isinstance(item, dict) and item.get("sign") == "unresolved"
    )
    if unresolved != len(pairwise):
        raise AssertionError(
            f"expected every retained pairwise policy-cost sign to be unresolved; "
            f"found {unresolved}/{len(pairwise)}"
        )

    transfer_strings = set(all_strings(transfer))
    for token in ("certified-readout", "analytic-endpoint", "adaptive"):
        if not any(token in value for value in transfer_strings):
            raise AssertionError(f"missing expected transfer token: {token}")

    assert "thm:compatible84" in compatible
    assert "thm:actionwise82" in actionwise
    assert "thm:frontier83" in frontier

    delivery_lower = delivery.lower()
    for token in ("source", "publication", "workflow"):
        if token not in delivery_lower:
            raise AssertionError(f"delivery note omits required token: {token}")

    result = {
        "status": "passed",
        "reviewed_snapshot": {
            "commit": REVIEWED_COMMIT,
            "tree": REVIEWED_TREE,
            "science_source_commit": SCIENCE_SOURCE_COMMIT,
        },
        "structural_checks": {
            "required_files": len(required),
            "pairwise_policy_cost_records": len(pairwise),
            "pairwise_unresolved_signs": unresolved,
            "independent_qualification_certificates": independent[
                "independent_qualification_certificates"
            ],
            "independent_assignment_inequalities": independent[
                "independent_assignment_inequalities"
            ],
            "new_fit_attempts": summary["new_fit_attempts"],
            "new_independent_cost_rows": summary["new_independent_cost_rows"],
        },
        "file_sha256": {name: sha256(path) for name, path in required.items()},
        "scope": [
            "Checks committed identities, theorem labels, audit status, and reported transfer structure.",
            "Does not refit models or rerun Bellman, policy simulation, timing, LaTeX, or visual inspection.",
            "Does not constitute an independent formal proof or an independent implementation of the heaviest numerical kernels.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
