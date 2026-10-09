#!/usr/bin/env python3
"""Standard-library deterministic audit for the NBO R49 referee review.

The script audits frozen GitHub Actions artifacts. It does not rerun
construction, simulation, LaTeX, or timing services.
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

STUDY_SHA = "d367b908c754dfa66efd5b6ed40fd6ce46a6e6606cde959811afb850b4b3c601"
GRADED_SHA = "280f32e6cc66344e31c5e04487cd813bdaf21908f6860d1449b2c297f4268517"
BRANCH = "revision/econometrica-nbo-r49-source-2026-10-08"
COMMIT = "4ede6077aa3d78aa36ec9b9471e5338a636a49f4"
TREE = "98098e476c1f8d690e12ae8dc95c976264740693"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def q(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def verify_manifest(root: Path, rel: str) -> dict[str, int]:
    audit = load(root / rel)
    results = 0
    for path, expected in audit["result_hashes"].items():
        full = root / path
        assert full.is_file(), full
        assert digest(full) == expected, path
        results += 1
    current_sources = 0
    inherited_unbundled = 0
    for path, expected in audit["source_hashes"].items():
        full = (root / path).resolve()
        if not full.is_file():
            inherited_unbundled += 1
            continue
        assert digest(full) == expected, path
        current_sources += 1
    assert all(int(job.get("returncode", 1)) == 0 for job in audit["jobs"])
    return {
        "result_hashes_verified": results,
        "source_hashes_verified_from_artifact": current_sources,
        "inherited_source_hashes_not_materialized_in_artifact": inherited_unbundled,
        "jobs": len(audit["jobs"]),
    }


def records(root: Path, pattern: str) -> list[dict[str, Any]]:
    ans = []
    for path in sorted(root.glob(pattern)):
        row = load(path)
        row["_path"] = str(path)
        ans.append(row)
    return ans


def interval_sign(interval: list[float]) -> str:
    lo, hi = map(float, interval)
    if lo > 0:
        return "left-higher"
    if hi < 0:
        return "left-lower"
    return "unresolved"


def attainment(rows: list[dict[str, Any]], dimension: int | None = None) -> dict[str, dict[str, int]]:
    selected = [r for r in rows if dimension is None or r["dimension"] == dimension]
    targets = ["5", "4", "2", "1", "1/2"]
    return {
        method: {
            target: sum(r["first_crossings"].get(target) is not None for r in selected if r["method"] == method)
            for target in targets
        }
        for method in sorted({r["method"] for r in selected})
    }


def substantive(checkpoint: dict[str, Any]) -> dict[str, Any]:
    keys = ["N", "K", "M", "T", "dimension", "price", "actors", "models",
            "policy_bound_exact", "rows", "terminal_error", "terminal_width"]
    return {key: checkpoint[key] for key in keys if key in checkpoint}


def curvature_control(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tensors = {
        (r["dimension"], r["horizon"], r["price"], r["repeat"]): r
        for r in rows if r["method"] == "tensor-fvi"
    }
    curves = [r for r in rows if r["method"] == "curvature-fvi"]
    ratios = []
    pairs = equal = nonuniform = 0
    for curve in curves:
        key = (curve["dimension"], curve["horizon"], curve["price"], curve["repeat"])
        tensor = tensors[key]
        assert len(curve["attempts"]) == len(tensor["attempts"])
        for ca, ta in zip(curve["attempts"], tensor["attempts"]):
            assert ca["bound_exact"] == ta["bound_exact"]
            assert (ca["N"], ca["K"], ca["M"]) == (ta["N"], ta["K"], ta["M"])
            nonuniform += int(ca.get("nonuniform_date_models", 0))
            cp = Path(curve["_path"]).parent / ca["checkpoint"]
            tp = Path(tensor["_path"]).parent / ta["checkpoint"]
            pairs += 1
            equal += substantive(load(cp)) == substantive(load(tp))
        ratios.append(curve["attempts"][-1]["prefix_seconds"] / tensor["attempts"][-1]["prefix_seconds"])
    return {
        "services": len(curves),
        "checkpoint_pairs": pairs,
        "substantively_identical_checkpoint_pairs": equal,
        "nonuniform_date_models": nonuniform,
        "final_prefix_time_ratio_curvature_over_tensor": {
            "min": min(ratios), "median": statistics.median(ratios), "max": max(ratios)
        },
    }


def graded_control(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tensors = {(r["horizon"], r["price"], r["repeat"]): r for r in rows if r["method"] == "tensor-fvi"}
    graded = [r for r in rows if r["method"] == "graded-fvi"]
    bound_ratios, time_ratios = [], []
    worse = slower = nonuniform = 0
    for row in graded:
        tensor = tensors[(row["horizon"], row["price"], row["repeat"])]
        nonuniform += sum(int(a.get("nonuniform_date_models", 0)) for a in row["attempts"])
        gb = float(q(row["attempts"][-1]["bound_exact"]))
        tb = float(q(tensor["attempts"][-1]["bound_exact"]))
        gs = row["attempts"][-1]["prefix_seconds"]
        ts = tensor["attempts"][-1]["prefix_seconds"]
        bound_ratios.append(gb / tb)
        time_ratios.append(gs / ts)
        worse += gb > tb
        slower += gs > ts
    return {
        "services": len(rows),
        "rungs": sum(len(r["attempts"]) for r in rows),
        "nonuniform_date_models": nonuniform,
        "graded_worse_final_bound_pairs": worse,
        "graded_slower_pairs": slower,
        "graded_to_uniform_final_bound_ratio": {
            "min": min(bound_ratios), "median": statistics.median(bound_ratios), "max": max(bound_ratios)
        },
        "graded_to_uniform_final_prefix_time_ratio": {
            "min": min(time_ratios), "median": statistics.median(time_ratios), "max": max(time_ratios)
        },
        "attainment": attainment(rows, 2),
    }


def direct_cost(root: Path) -> dict[str, Any]:
    pairs, sensors = [], []
    for path in sorted((root / "results/direct").glob("*.json")):
        if path.name.endswith(".clock.json"):
            continue
        row = load(path)
        if path.name.startswith("new-") or path.name.startswith("R48-"):
            pairs.append(row)
        elif path.name.startswith("sensor-"):
            sensors.append(row)
    fresh = [r for r in pairs if r["spec"].get("frontier") == "R49"]
    retained = [r for r in pairs if r["spec"].get("frontier") == "R48"]
    by_target = {}
    for target in [1, 2, 4]:
        subset = [r for r in fresh if int(r["spec"]["target"]) == target]
        by_target[str(target)] = dict(collections.Counter(interval_sign(r["interval"]) for r in subset))
    mids = [(float(r["interval"][0]) + float(r["interval"][1])) / 2 for r in fresh]
    widths = [float(r["interval"][1]) - float(r["interval"][0]) for r in fresh]
    return {
        "r49_policy_pairs": len(fresh),
        "r49_signs": dict(collections.Counter(interval_sign(r["interval"]) for r in fresh)),
        "r49_signs_by_target": by_target,
        "r49_midpoint": {"min": min(mids), "median": statistics.median(mids), "max": max(mids)},
        "r49_interval_width": {"min": min(widths), "median": statistics.median(widths), "max": max(widths)},
        "retained_r48_pairs": len(retained),
        "retained_r48_signs": dict(collections.Counter(interval_sign(r["interval"]) for r in retained)),
        "sensor_contrasts": len(sensors),
        "sensor_signs": dict(collections.Counter(interval_sign(r["interval"]) for r in sensors)),
    }


def repeat_identity(rows: list[dict[str, Any]]) -> dict[str, int]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        groups[(row["dimension"], row["horizon"], row["price"], row["method"])].append(row)
    total = identical = 0
    for group in groups.values():
        if len(group) <= 1:
            continue
        ladders = [[a["checkpoint_sha256"] for a in row["attempts"]] for row in group]
        total += 1
        identical += all(x == ladders[0] for x in ladders[1:])
    return {"multi_repeat_groups": total, "checkpoint_identical_groups": identical}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--study-root", type=Path, required=True)
    p.add_argument("--graded-root", type=Path, required=True)
    p.add_argument("--study-zip", type=Path, required=True)
    p.add_argument("--graded-zip", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    assert digest(a.study_zip) == STUDY_SHA
    assert digest(a.graded_zip) == GRADED_SHA
    study_manifest = verify_manifest(a.study_root, "audit/EXECUTION_COMPLETE.json")
    graded_manifest = verify_manifest(a.graded_root, "graded/audit/EXECUTION_COMPLETE.json")
    study_rows = records(a.study_root, "results/services/*/record.json")
    graded_rows = records(a.graded_root, "graded/results/services/*/record.json")
    result = {
        "status": "passed",
        "reviewed_snapshot": {"branch": BRANCH, "commit": COMMIT, "tree": TREE},
        "artifact_digests": {"study": STUDY_SHA, "graded": GRADED_SHA},
        "manifest_checks": {"study": study_manifest, "graded": graded_manifest},
        "study": {
            "services": len(study_rows),
            "rungs": sum(len(r["attempts"]) for r in study_rows),
            "method_counts": dict(collections.Counter(r["method"] for r in study_rows)),
            "dimension_counts": dict(collections.Counter(str(r["dimension"]) for r in study_rows)),
            "attainment_by_dimension": {str(d): attainment(study_rows, d) for d in [2, 3, 4]},
            "original_curvature_control": curvature_control(study_rows),
            "checkpoint_repetitions": repeat_identity(study_rows),
        },
        "graded_block": graded_control(graded_rows),
        "direct_policy_cost": direct_cost(a.study_root),
        "scope": [
            "Frozen records and arithmetic are audited; construction, simulation, LaTeX and clocks are not rerun.",
            "Timing repetitions share deterministic checkpoints and are not independent trained policies.",
            "Single-runner clocks are descriptive and do not establish hardware-general performance.",
            "The source branch is not a canonical review-ready publication; the main evidence push failed after science completed."
        ],
    }
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
