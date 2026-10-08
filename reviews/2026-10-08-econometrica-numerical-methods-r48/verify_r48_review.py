#!/usr/bin/env python3
"""Independent standard-library audit for the NBO R48 referee report.

This script verifies frozen source/record hashes and reconstructs the headline
attainment, timing, direct-cost, compiler, sensor, and publication results. It
does not rerun training, simulation, LaTeX, or timing services.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import statistics
from fractions import Fraction
from pathlib import Path
from typing import Any

EXPECTED = {
    "study_zip": "9ac1f57b4e4b899594029e775c1f1c9e921ad943490e85481badedcd5d722bbc",
    "publication_zip": "b82272add8e7ea630ef1ab45455b079514fd848311e2d23db84d2b11ab9cd5df",
    "branch": "revision/econometrica-nbo-r48-review-ready-2026-10-08",
    "commit": "2650fd92f24be0f4807ec8ee0eac1d075a8d63e3",
    "tree": "20ca4fb03bf1a725190f3a43a456b4ad14411d0d",
}
TARGETS = ("4", "2", "1", "1/2", "1/4")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def sources(root: Path) -> int:
    manifest = read(root / "SOURCE_SHA256.json")
    for rel, expected in manifest.items():
        path = root / rel
        check(path.is_file(), f"missing source {rel}")
        check(digest(path) == expected, f"source hash {rel}")
    return len(manifest)


def services(root: Path) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    checkpoints = 0
    for folder in sorted((root / "results" / "services").iterdir()):
        if not folder.is_dir():
            continue
        record_path = folder / "record.json"
        clock = read(folder / "clock.json")
        check(digest(record_path) == clock["record_sha256"], f"record hash {folder.name}")
        record = read(record_path)
        for attempt in record["attempts"]:
            checkpoint = folder / f"checkpoint-N{attempt['N']}.json"
            check(digest(checkpoint) == attempt["checkpoint_sha256"], f"checkpoint {checkpoint}")
            checkpoints += 1
        records.append(record)
    check(len(records) == 44, "service count")
    check(sum(len(r["attempts"]) for r in records) == 204, "rung count")
    return records, checkpoints


def attainment_and_times(records: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    main = [r for r in records if r["dimension"] == 2]
    attainment = {m: {t: 0 for t in TARGETS} for m in ("compiled-witness", "tensor-fvi", "adaptive-fvi")}
    for record in main:
        for target in TARGETS:
            attainment[record["method"]][target] += int(record["first_crossings"][target] is not None)

    timing: dict[str, Any] = {}
    for comparator in ("tensor-fvi", "adaptive-fvi"):
        counts = {"common": 0, "compiled_faster": 0, "compiled_slower": 0, "equal": 0}
        for T, price, repeat in itertools.product((2, 3), (1, 4), (0, 1, 2)):
            w = next(r for r in main if r["method"] == "compiled-witness" and r["horizon"] == T and r["price"] == price and r["repeat"] == repeat)
            c = next(r for r in main if r["method"] == comparator and r["horizon"] == T and r["price"] == price and r["repeat"] == repeat)
            for target in ("4", "2", "1"):
                a, b = w["first_crossings"][target], c["first_crossings"][target]
                if a is None or b is None:
                    continue
                counts["common"] += 1
                if a["prefix_seconds"] < b["prefix_seconds"]:
                    counts["compiled_faster"] += 1
                elif a["prefix_seconds"] > b["prefix_seconds"]:
                    counts["compiled_slower"] += 1
                else:
                    counts["equal"] += 1
        timing[comparator] = counts
    return attainment, timing


def direct(root: Path) -> dict[str, Any]:
    paths = sorted(p for p in (root / "results" / "direct").glob("*.json") if not p.name.endswith(".clock.json"))
    check(len(paths) == 48, "direct count")
    rows = []
    seconds = 0.0
    for path in paths:
        clock_path = path.with_name(path.stem + ".clock.json")
        clock = read(clock_path)
        check(digest(path) == clock["record_sha256"], f"direct hash {path.name}")
        rows.append(read(path))
        seconds += clock["seconds_through_record_fsync"]
    signs: dict[str, int] = {"witness-higher": 0, "witness-lower": 0, "unresolved": 0}
    for row in rows:
        signs[row["sign"]] = signs.get(row["sign"], 0) + 1
    endpoint = max(max(abs(r["interval"][0]), abs(r["interval"][1])) for r in rows)
    fee = float(Fraction(1, 64))
    return {
        "tasks": 48,
        "total_paths": sum(r["paths"] for r in rows),
        "signs": signs,
        "all_neither_direction_recoups_fee": all(r["neither_direction_recoups_fee"] for r in rows),
        "replacement_fee": fee,
        "max_absolute_endpoint": endpoint,
        "fee_to_max_endpoint_ratio": fee / endpoint,
        "max_interval_width": max(r["interval"][1] - r["interval"][0] for r in rows),
        "total_pair_seconds": seconds,
    }


def diagnostics(root: Path) -> dict[str, Any]:
    sensors = read(root / "results" / "diagnostics" / "sensors.json")
    choices: dict[str, int] = {}
    for record in sensors:
        for curve in record["curves"]:
            key = str(curve["selected_bits"])
            choices[key] = choices.get(key, 0) + 1

    compiler = read(root / "results" / "diagnostics" / "compiler.json")
    ratios = []
    for checkpoint in compiler:
        for rep in checkpoint["repetitions"]:
            dense = rep["dense_load_seconds"] + rep["dense_query_seconds"]
            compiled = rep["compile_seconds"] + rep["compiled_query_seconds"]
            ratios.append(dense / compiled)
    return {
        "sensor_selected_bits": dict(sorted(choices.items(), key=lambda x: int(x[0]))),
        "compiler_checkpoints": len(compiler),
        "compiler_runs": len(ratios),
        "dense_over_compiled_ratio_including_setup": {
            "min": min(ratios), "median": statistics.median(ratios), "max": max(ratios)
        },
    }


def full(coords: list[list[Fraction]], labels: list[Fraction], slope: Fraction, point: tuple[Fraction, ...]) -> tuple[Fraction, int]:
    sites = list(itertools.product(*coords))
    return min((labels[i] + slope * sum(abs(a-b) for a, b in zip(point, site)), i) for i, site in enumerate(sites))


def compiled(coords: list[list[Fraction]], labels: list[Fraction], slope: Fraction, point: tuple[Fraction, ...]) -> tuple[Fraction, int]:
    sites = list(itertools.product(*coords))
    shape = [len(x) for x in coords]
    owners = []
    for vertex in sites:
        owners.append(min((labels[i] + slope * sum(abs(a-b) for a, b in zip(vertex, site)), i) for i, site in enumerate(sites))[1])
    lower = []
    for axis, value in zip(coords, point):
        if value >= axis[-1]:
            lower.append(len(axis)-2)
        else:
            lower.append(max(0, max((i for i, x in enumerate(axis[:-1]) if x <= value), default=0)))
    def flat(index: tuple[int, ...]) -> int:
        answer = 0
        for width, coordinate in zip(shape, index):
            answer = answer * width + coordinate
        return answer
    candidates = []
    for bits in itertools.product((0, 1), repeat=len(coords)):
        corner = tuple(lower[j] + bits[j] for j in range(len(coords)))
        owner = owners[flat(corner)]
        site = sites[owner]
        candidates.append((labels[owner] + slope * sum(abs(a-b) for a, b in zip(point, site)), owner))
    return min(candidates)


def compiler_checks() -> int:
    rng = random.Random(20261008)
    count = 0
    for dimension in range(1, 5):
        for _ in range(40):
            coords = [sorted({Fraction(0), Fraction(rng.randrange(1, 16), 16), Fraction(1)}) for _ in range(dimension)]
            labels = [Fraction(rng.randrange(-20, 21), 8) for _ in itertools.product(*coords)]
            slope = Fraction(rng.randrange(0, 9), 4)
            point = tuple(rng.choice(axis) if rng.random() < 0.3 else Fraction(rng.randrange(65), 64) for axis in coords)
            check(full(coords, labels, slope, point) == compiled(coords, labels, slope, point), "compiler identity")
            count += 1
    return count


def publication(root: Path) -> dict[str, Any]:
    files = read(root / "audit" / "FILES_SHA256.json")
    for rel, expected in files.items():
        path = root / rel
        check(path.is_file() or path.is_symlink(), f"missing publication file {rel}")
        if path.is_file():
            check(digest(path) == expected, f"publication hash {rel}")
    clean = read(root / "audit" / "CLEAN_REBUILD.json")
    delivery = read(root / "audit" / "FINAL_DELIVERY.json")
    release = read(root / "audit" / "RELEASE_AUDIT.json")
    check(clean["successful"] and clean["tests"] == 96, "clean rebuild")
    check(delivery["historical_paths_unchanged"], "historical paths")
    return {
        "files_verified": len(files),
        "tests": clean["tests"],
        "clean_rebuild": clean["successful"],
        "historical_paths_unchanged": delivery["historical_paths_unchanged"],
        "pages": {row["document"]: row["pages"] for row in release["compilation"]},
        "main_source_sha256": digest(root / "ECTA.tex"),
        "supp_source_sha256": digest(root / "supp.tex"),
        "response_source_sha256": digest(root / "response.md"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-root", type=Path, required=True)
    parser.add_argument("--study-zip", type=Path)
    parser.add_argument("--publication-root", type=Path, required=True)
    parser.add_argument("--publication-zip", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.study_zip:
        check(digest(args.study_zip) == EXPECTED["study_zip"], "study artifact digest")
    if args.publication_zip:
        check(digest(args.publication_zip) == EXPECTED["publication_zip"], "publication artifact digest")

    source_count = sources(args.study_root)
    records, checkpoint_count = services(args.study_root)
    attainment, timing = attainment_and_times(records)
    result = {
        "status": "passed",
        "reviewed_snapshot": {"branch": EXPECTED["branch"], "commit": EXPECTED["commit"], "tree": EXPECTED["tree"]},
        "study_integrity": {"source_hashes_verified": source_count, "services": 44, "rungs": 204, "checkpoint_hashes_verified": checkpoint_count},
        "attainment_out_of_12": attainment,
        "common_successful_target_timing": timing,
        "direct_policy_cost": direct(args.study_root),
        "diagnostics": diagnostics(args.study_root),
        "compiler_exact_random_spot_checks": compiler_checks(),
        "publication": publication(args.publication_root),
        "scope": [
            "Frozen records and arithmetic are audited; scientific and timing services are not rerun.",
            "Direct records compare frozen R47 N=16 policies, not the new R48 first-crossing policies.",
            "Exact compiler checks establish identity, not a neural-exclusive advantage."
        ]
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
