#!/usr/bin/env python3
"""Independent standard-library audit for the NBO R47 referee report.

This script audits the frozen study and the preserved publication artifact. It
verifies archive digests, source and record hashes, reconstructs the principal
direct-policy, constrained-service, deployment and frontier findings, and checks
that the preserved assembled sources match the publication bindings. It does
not rerun training, simulation, LaTeX, or wall-clock experiments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import tempfile
import zipfile
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
from typing import Any

EXPECTED_STUDY_SHA256 = "782e437ccb4886a18f6692b02d0e4a109abe67d729e53f5c266cf1f5df2428db"
EXPECTED_PUBLICATION_SHA256 = "65a3c49014b58f1708802496106175631b0bb0cba9b1bfc6f00128e6afbc1bbf"
EXPECTED_SNAPSHOT = {
    "branch": "revision/econometrica-nbo-r47-integrated-source-2026-10-08",
    "commit": "27f3c36984f00ff060d0586712a01b87355914ba",
    "tree": "c75871b821aa3f3e540b627c60891766c1f302b6",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def extract(zip_path: Path, target: Path) -> Path:
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            p = Path(info.filename)
            if p.is_absolute() or ".." in p.parts:
                raise ValueError(f"unsafe archive member: {info.filename}")
        archive.extractall(target)
    children = [p for p in target.iterdir()]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return target


def verify_sources(root: Path) -> int:
    ledger = load(root / "SOURCE_SHA256.json")
    for rel, expected in ledger.items():
        actual = sha256(root / rel)
        if actual != expected:
            raise AssertionError(f"source hash mismatch: {rel}: {actual} != {expected}")
    return len(ledger)


def audit_direct(root: Path) -> dict[str, Any]:
    droot = root / "results" / "direct"
    complete = load(droot / "COMPLETE.json")
    declared = {row["key"]: row["file_sha256"] for row in complete["records"]}
    files = sorted(droot.glob("T*.json"))
    if len(files) != 40 or complete["groups"] != 40 or complete["contrasts"] != 120:
        raise AssertionError("unexpected direct comparison catalogue")
    signs: Counter[str] = Counter()
    within = 0
    max_abs = F(0)
    max_width = F(0)
    actor_queries = 0
    ambiguities = 0
    policy_hashes: set[str] = set()
    midpoint_diag_max = 0.0
    family_counts: Counter[str] = Counter()
    for path in files:
        item = load(path)
        if sha256(path) != declared[item["key"]]:
            raise AssertionError(f"direct record hash mismatch: {path.name}")
        if item["paths"] != 131072 or item["uniform_bin_bits"] != 40:
            raise AssertionError("unexpected direct sampling design")
        if F(item["decision_margin"]) != F(1, 1024):
            raise AssertionError("unexpected direct decision margin")
        actor_queries += sum(item["actor_queries"])
        ambiguities += sum(item["ambiguous_actor_queries"])
        policy_hashes.update(row["sha256"] for row in item["policy_files"])
        for comp in item["comparisons"]:
            lo, hi = map(F, comp["interval_exact"])
            if lo > hi:
                raise AssertionError("reversed interval")
            sign = "first-lower" if hi < 0 else "first-higher" if lo > 0 else "unresolved"
            if sign != comp["sign"]:
                raise AssertionError("stored interval sign mismatch")
            in_margin = -F(1, 1024) <= lo and hi <= F(1, 1024)
            if in_margin != comp["within_margin"]:
                raise AssertionError("stored margin classification mismatch")
            signs[sign] += 1
            within += int(in_margin)
            max_abs = max(max_abs, abs(lo), abs(hi))
            max_width = max(max_width, hi - lo)
            midpoint_diag_max = max(midpoint_diag_max, abs(float(comp["raw_cost_midpoint_mean_diagnostic"])))
            family_counts[f"{comp['first']} minus {comp['second']}"] += 1
    return {
        "groups": len(files),
        "contrasts": sum(family_counts.values()),
        "paths_per_group": complete["paths_per_group"],
        "total_paths": len(files) * complete["paths_per_group"],
        "unique_policy_checkpoints": len(policy_hashes),
        "signs": dict(signs),
        "within_margin": within,
        "max_absolute_endpoint": float(max_abs),
        "max_interval_width": float(max_width),
        "actor_queries": actor_queries,
        "ambiguous_actor_queries": ambiguities,
        "ambiguous_query_rate": ambiguities / actor_queries,
        "max_absolute_midpoint_cost_diagnostic": midpoint_diag_max,
        "families": dict(family_counts),
    }


def audit_constrained(root: Path) -> dict[str, Any]:
    croot = root / "results" / "constrained"
    records = []
    checkpoint_groups: defaultdict[tuple[Any, ...], list[str]] = defaultdict(list)
    for path in sorted(croot.glob("*/record.json")):
        item = load(path)
        clock = load(path.parent / "clock.json")
        if clock["record_sha256"] != sha256(path):
            raise AssertionError(f"constrained record hash mismatch: {path.parent.name}")
        if [row["N"] for row in item["attempts"]] != [4, 8, 16]:
            raise AssertionError("unexpected constrained ladder")
        for row in item["attempts"]:
            cp = path.parent / f"checkpoint-N{row['N']}.json"
            if sha256(cp) != row["checkpoint_sha256"]:
                raise AssertionError(f"checkpoint hash mismatch: {cp}")
            checkpoint_groups[(item["method"], item["horizon"], item["price"], row["N"])].append(row["checkpoint_sha256"])
        records.append(item)
    if len(records) != 24:
        raise AssertionError(f"expected 24 constrained services, found {len(records)}")
    repeated_identically = all(len(values) == 3 and len(set(values)) == 1 for values in checkpoint_groups.values())
    attainment: dict[str, dict[str, int]] = {}
    for method in ("feasible-cone-witness", "bilinear-fvi"):
        subset = [r for r in records if r["method"] == method]
        attainment[method] = {
            target: sum(r["first_crossings"][target] is not None for r in subset)
            for target in ("4", "2", "1", "1/2")
        }
    cells = []
    fvi_faster = 0
    for T in (2, 3):
        for p in (1, 4):
            cell: dict[str, Any] = {"T": T, "price": p}
            by_method = {}
            for method in ("feasible-cone-witness", "bilinear-fvi"):
                subset = [r for r in records if r["method"] == method and r["horizon"] == T and r["price"] == p]
                seconds = [r["attempts"][-1]["prefix_seconds"] for r in subset]
                by_method[method] = {
                    "final_bound": subset[0]["attempts"][-1]["bound_upper"],
                    "median_seconds": statistics.median(seconds),
                    "min_seconds": min(seconds),
                    "max_seconds": max(seconds),
                    "prefix_queries": subset[0]["attempts"][-1]["prefix_bellman_queries"],
                }
            witness = by_method["feasible-cone-witness"]
            fvi = by_method["bilinear-fvi"]
            cell["methods"] = by_method
            cell["witness_bound_reduction_percent"] = 100 * (fvi["final_bound"] - witness["final_bound"]) / fvi["final_bound"]
            cell["witness_to_fvi_median_time_ratio"] = witness["median_seconds"] / fvi["median_seconds"]
            cells.append(cell)
            for rep in range(3):
                w = next(r for r in records if (r["method"], r["horizon"], r["price"], r["repeat"]) == ("feasible-cone-witness", T, p, rep))
                b = next(r for r in records if (r["method"], r["horizon"], r["price"], r["repeat"]) == ("bilinear-fvi", T, p, rep))
                fvi_faster += int(b["attempts"][-1]["prefix_seconds"] < w["attempts"][-1]["prefix_seconds"])
    return {
        "services": len(records),
        "rungs": sum(len(r["attempts"]) for r in records),
        "repetitions_checkpoint_identical": repeated_identically,
        "attainment": attainment,
        "fvi_faster_common_crossings": fvi_faster,
        "common_crossings": 12,
        "cells": cells,
    }


def audit_deployment(root: Path) -> dict[str, Any]:
    droot = root / "results" / "deployment"
    acquisition = load(droot / "acquisition.json")
    frontier = load(droot / "frontier.json")
    representation = load(droot / "representation.json")
    cases: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    active_repairs = 0
    for model in acquisition["records"]:
        for test in model["tests"]:
            cases[(test["coordinate_radius"], test["action_quantum"])].append(test)
            active_repairs += sum(row["active_robust_repairs"] for row in test["rows"])
    case_summary = []
    for (radius, quantum), tests in sorted(cases.items(), key=lambda item: (F(item[0][0]), F(item[0][1]))):
        case_summary.append({
            "coordinate_radius": radius,
            "action_quantum": quantum,
            "policies": len(tests),
            "max_extra_policy_bound": max(float(F(test["extra_policy_bound"])) for test in tests),
            "active_repairs": sum(row["active_robust_repairs"] for test in tests for row in test["rows"]),
            "quantized_actions": sum(row["quantized_actions"] for test in tests for row in test["rows"]),
        })
    relations = Counter()
    for cell in frontier["cells"]:
        for interval in cell["intervals"]:
            relations[interval["relation"]] += 1
    rows = [row for record in representation["records"] for row in record["rows"]]
    max_difference = max(float(F(row["maximum_float_difference"])) for row in rows)
    max_allowance = max(float(F(row["proved_difference_allowance"])) for row in rows)
    if not all(F(row["maximum_float_difference"]) <= F(row["proved_difference_allowance"]) for row in rows):
        raise AssertionError("representation error exceeded allowance")
    return {
        "acquisition_cases": acquisition["deployment_cases"],
        "policies": acquisition["models"],
        "total_active_repairs": active_repairs,
        "case_summary": case_summary,
        "frontier_partition_intervals": sum(relations.values()),
        "frontier_relations": dict(relations),
        "representation_checkpoints": len(representation["records"]),
        "representation_function_dates": len(rows),
        "max_native_relu_difference": max_difference,
        "max_proved_representation_allowance": max_allowance,
        "neural_acceleration_established": representation["neural_acceleration_established"],
    }


def audit_publication(root: Path) -> dict[str, Any]:
    bindings = load(root / "publication" / "SOURCE_BINDINGS.json")
    assembled = bindings["assembled_source_sha256"]
    for name, expected in assembled.items():
        path = root / name
        if sha256(path) != expected:
            raise AssertionError(f"assembled source hash mismatch: {name}")
    summary = load(root / "audit" / "PUBLICATION_SUMMARY.json")
    pdfs = {}
    for name in ("ECTA.pdf", "supp.pdf", "response.pdf"):
        path = root / "build" / name
        pdfs[name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    return {
        "assembled_source_hashes_verified": len(assembled),
        "source_bindings": {
            "protocol_commit": bindings["protocol_commit"],
            "scientific_source_commit": bindings["scientific_source_commit"],
            "evidence_commit": bindings["evidence_commit"],
        },
        "publication_summary_revision": summary["revision"],
        "pdfs": pdfs,
        "note": "This preserved artifact came from the first publication run, which stopped after compilation because pdfinfo was unavailable; it is not a completed release gate.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-zip", type=Path, required=True)
    parser.add_argument("--publication-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if sha256(args.study_zip) != EXPECTED_STUDY_SHA256:
        raise AssertionError("study artifact digest mismatch")
    if sha256(args.publication_zip) != EXPECTED_PUBLICATION_SHA256:
        raise AssertionError("publication artifact digest mismatch")
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        study = extract(args.study_zip, base / "study")
        publication = extract(args.publication_zip, base / "publication")
        result = {
            "status": "passed",
            "reviewed_snapshot": EXPECTED_SNAPSHOT,
            "artifact_digests": {
                "study": EXPECTED_STUDY_SHA256,
                "preserved_first_publication": EXPECTED_PUBLICATION_SHA256,
            },
            "source_hashes_verified": verify_sources(study),
            "direct": audit_direct(study),
            "constrained": audit_constrained(study),
            "deployment": audit_deployment(study),
            "publication": audit_publication(publication),
            "scope": [
                "The audit verifies frozen files and arithmetic; it does not rerun training, simulation, LaTeX, or timing experiments.",
                "The publication artifact is the preserved first failed publication run, not a completed review-ready release.",
                "Single-host clocks are descriptive observations, and three repeated constrained records share identical checkpoints rather than independent trained policies.",
            ],
        }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
