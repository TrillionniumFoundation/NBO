#!/usr/bin/env python3
"""Deterministic external-review checks for the NBO R14 evidence snapshot.

The script does not train a policy.  It verifies immutable source identities,
recomputes the review's aggregate counts from the committed tables, and can
spot-check the original GitHub Actions delivery and one raw fixed-work shard.
It uses only Python's standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable

REVIEWED_COMMIT = "f5021cefa71492babfcbfa580e0c984f59a9de26"
REVIEWED_TREE = "5a0084d6ce3df47469125a7afe85c081cd29d94f"
EXPECTED = {
    "ECTA.tex": {
        "sha256": "70bb1613fc29792eb73ae17d2f1add7f8637faa89dfb6d77bc5059305fb7a38d",
        "git_blob_sha1": "c13f5e951b47577f0cd4bcbb8b3d003e92e6a33e",
    },
    "supp.tex": {
        "sha256": "73a4387baa53046fd0b6eaf4b9b6c52c07eeccaf24e7c41569369bf84c13fbad",
        "git_blob_sha1": "9ae1d87ddc6da2e0cd0475522c269da8ee55a1be",
    },
}
EXPECTED_DELIVERY_ZIP_SHA256 = "461a938b0866746f8bbf536efad2d14bfbcaea25e6ba8fd1deb428413b2f6ca7"
EXPECTED_FIXED_WORK_ZIP_SHA256 = "985558b09377c86f2493271d4112c5265cfd375645631b89332144e8738e6c5c"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def read_rows(path: Path, expected_fields: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("%") or "&" not in line:
            continue
        if any(token in line for token in ("toprule", "midrule", "bottomrule", "multicolumn")):
            continue
        line = re.sub(r"\\\\\s*$", "", line)
        fields = [field.strip() for field in line.split("&")]
        if len(fields) != expected_fields:
            continue
        if not re.fullmatch(r"-?\d+(?:\.\d+)?", fields[0]):
            continue
        rows.append(fields)
    return rows


def f(text: str) -> float:
    return float(text.replace("$", "").replace("\\times10^", "e"))


def assert_close(a: float, b: float, tol: float = 1e-12) -> None:
    if not math.isclose(a, b, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"{a!r} != {b!r}")


def zip_json(zf: zipfile.ZipFile, suffix: str) -> dict[str, Any]:
    matches = [name for name in zf.namelist() if name.endswith(suffix)]
    if len(matches) != 1:
        raise AssertionError(f"Expected one ZIP member ending in {suffix!r}; found {matches}")
    return json.loads(zf.read(matches[0]).decode("utf-8"))


def audit(repo: Path, delivery_zip: Path | None, fixed_work_zip: Path | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": 1,
        "reviewed_snapshot": {
            "commit": REVIEWED_COMMIT,
            "tree": REVIEWED_TREE,
        },
        "checks": {},
        "derived_findings": {},
        "limitations": [
            "No time-budgeted policy training was rerun; such a rerun would use a different hardware and timing environment.",
            "The deterministic audit checks the committed publication tables and final audit, plus an optional original raw fixed-work shard.",
            "The review does not convert descriptive fixed-stream results into a probability statement over future optimizer initializations.",
        ],
    }

    source_checks: dict[str, Any] = {}
    for rel, expected in EXPECTED.items():
        path = repo / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = {"sha256": sha256(path), "git_blob_sha1": git_blob_sha1(path)}
        if actual != expected:
            raise AssertionError(f"Source identity mismatch for {rel}: {actual} != {expected}")
        source_checks[rel] = actual
    result["checks"]["source_identities"] = source_checks

    r14 = repo / "revisions/2026-10-04-r14"
    final_audit = json.loads((r14 / "FINAL_AUDIT.json").read_text(encoding="utf-8"))
    if not final_audit.get("complete") or not final_audit.get("publication_source_verified"):
        raise AssertionError("R14 final audit is not complete/source-verified")
    if not final_audit["tests"].get("all_passed") or final_audit["tests"].get("total") != 123:
        raise AssertionError("R14 test ledger mismatch")
    for name in ("ECTA", "supp", "response"):
        comp = final_audit["compilation"][name]
        if comp.get("undefined") or comp.get("multiply_defined") or comp.get("overfull_hbox_pt"):
            raise AssertionError(f"Compilation gate failed for {name}: {comp}")
    result["checks"]["publication_gate"] = {
        "complete": True,
        "publication_source_verified": True,
        "tests_passed": final_audit["tests"]["total"],
        "pages": {k: final_audit["compilation"][k]["pages"] for k in ("ECTA", "supp", "response")},
        "artifact_identity": final_audit["artifact_identity"],
    }

    # Primary schedule-relative rows.
    primary_rows = read_rows(r14 / "manuscript/table_primary.tex", 6)
    primary_nbo = []
    primary_nbo_population = []
    for row in primary_rows:
        d, method_state, mean, lower, regret, positive = row
        if method_state.startswith("NBO"):
            item = {
                "dimension": int(d),
                "state": method_state.split("/")[-1].strip(),
                "mean": f(mean),
                "lower": f(lower),
                "regret_upper": f(regret),
                "positive_count": positive,
            }
            primary_nbo.append(item)
            if item["state"] == "P":
                item["regret_to_mean_ratio"] = item["regret_upper"] / item["mean"]
                item["regret_to_lower_ratio"] = item["regret_upper"] / item["lower"]
                primary_nbo_population.append(item)
    if len(primary_nbo) != 6 or not all(x["lower"] > 0 and x["positive_count"] == "10/10" for x in primary_nbo):
        raise AssertionError("Primary NBO schedule-improvement count mismatch")

    paired_rows = read_rows(r14 / "manuscript/table_paired.tex", 7)
    if len(paired_rows) != 12:
        raise AssertionError(f"Expected 12 primary paired summary rows, found {len(paired_rows)}")
    paired = [
        {
            "dimension": int(row[0]),
            "state": row[1],
            "comparator": row[2],
            "mean": f(row[3]),
            "lower": f(row[4]),
            "upper": f(row[5]),
            "sign_count": row[6],
        }
        for row in paired_rows
    ]
    if not all(x["lower"] < 0 < x["upper"] and x["sign_count"] == "0/0" for x in paired):
        raise AssertionError("A primary paired interval is signed unexpectedly")

    fixed_rows = read_rows(r14 / "manuscript/table_extension_fixed_work.tex", 7)
    fixed: dict[tuple[int, int, str], dict[str, Any]] = {}
    for row in fixed_rows:
        key = (int(row[0]), int(row[1]), row[2])
        fixed[key] = {
            "mean": f(row[3]),
            "min_lower": f(row[4]),
            "positive": row[5],
            "fit_seconds": f(row[6]),
        }
    nbo_raw_fixed = []
    for d in (10, 20, 50):
        for k in (20, 80):
            nbo = fixed[(d, k, "NBO")]
            raw = fixed[(d, k, "Raw")]
            item = {
                "dimension": d,
                "checkpoint": k,
                "nbo_mean": nbo["mean"],
                "raw_mean": raw["mean"],
                "nbo_minus_raw_mean": nbo["mean"] - raw["mean"],
                "nbo_fit_seconds": nbo["fit_seconds"],
                "raw_fit_seconds": raw["fit_seconds"],
            }
            nbo_raw_fixed.append(item)
    if not all(x["nbo_minus_raw_mean"] < 0 and x["raw_fit_seconds"] < x["nbo_fit_seconds"] for x in nbo_raw_fixed):
        raise AssertionError("Fixed-work NBO/raw pattern differs from the committed table")

    ext_paired_rows = read_rows(r14 / "manuscript/table_extension_paired.tex", 8)
    ext_paired = [
        {
            "os": row[0],
            "dimension": int(row[1]),
            "seed": int(row[2]),
            "checkpoint": int(row[3]),
            "comparator": row[4],
            "mean": f(row[5]),
            "lower": f(row[6]),
            "upper": f(row[7]),
        }
        for row in ext_paired_rows
    ]
    if len(ext_paired) != 42 or not all(x["lower"] < 0 < x["upper"] for x in ext_paired):
        raise AssertionError("Fixed-work paired interval count/sign mismatch")
    ubuntu24_raw = [x for x in ext_paired if x["os"] == "24" and x["comparator"] == "Raw"]
    if len(ubuntu24_raw) != 12 or not all(x["mean"] < 0 for x in ubuntu24_raw):
        raise AssertionError("Ubuntu 24 NBO-minus-Raw sample-mean pattern mismatch")

    costate_rows = read_rows(r14 / "manuscript/table_extension_mechanism_costate.tex", 7)
    costates = [
        {
            "dimension": int(row[0]),
            "seed": int(row[1]),
            "critic_mse_x1e5": f(row[2]),
            "raw_mse_x1e5": f(row[3]),
            "ratio": f(row[2]) / f(row[3]),
        }
        for row in costate_rows
    ]
    if len(costates) != 6 or not all(x["critic_mse_x1e5"] > x["raw_mse_x1e5"] for x in costates):
        raise AssertionError("Costate mechanism pattern mismatch")

    ham_rows = read_rows(r14 / "manuscript/table_extension_mechanism_hamiltonian.tex", 8)
    hams = [
        {
            "dimension": int(row[0]),
            "seed": int(row[1]),
            "actor_gap_x1e5": f(row[2]),
            "critic_gap_x1e5": f(row[3]),
            "raw_gap_x1e5": f(row[4]),
            "payoff_mean_x1e5": f(row[5]),
            "lower_x1e5": f(row[6]),
            "upper_x1e5": f(row[7]),
        }
        for row in ham_rows
    ]
    if len(hams) != 6 or not all(x["critic_gap_x1e5"] > x["raw_gap_x1e5"] for x in hams):
        raise AssertionError("Hamiltonian mechanism pattern mismatch")

    reference_rows = read_rows(r14 / "manuscript/table_reference.tex", 6)
    scalar_reference = [
        {
            "space_nodes": int(row[0]),
            "time_cells": int(row[1]),
            "domain_half_width": int(row[2]),
            "nbo_loss": f(row[3]),
            "dpo_loss": f(row[4]),
            "schedule_loss": f(row[5]),
        }
        for row in reference_rows
    ]
    if len(scalar_reference) != 4 or not all(x["nbo_loss"] < x["dpo_loss"] < x["schedule_loss"] for x in scalar_reference):
        raise AssertionError("Scalar origin-reference ordering mismatch")

    result["derived_findings"].update(
        {
            "primary_nbo_schedule_rows_positive": len(primary_nbo),
            "primary_direct_summary_intervals_straddling_zero": len(paired),
            "fixed_work_direct_intervals_straddling_zero": len(ext_paired),
            "ubuntu24_nbo_minus_raw_sample_means_negative": len(ubuntu24_raw),
            "fixed_work_cells_raw_mean_above_nbo_and_raw_fit_faster": len(nbo_raw_fixed),
            "mechanism_panels_critic_mse_above_raw": len(costates),
            "mechanism_panels_critic_gap_above_raw": len(hams),
            "critic_to_raw_mse_ratio_range": [min(x["ratio"] for x in costates), max(x["ratio"] for x in costates)],
            "primary_population_regret_ratios": primary_nbo_population,
            "scalar_origin_rows_nbo_below_dpo": len(scalar_reference),
            "primary_pair_rows": paired,
            "fixed_work_nbo_raw_rows": nbo_raw_fixed,
        }
    )

    # Cross-check the author's aggregate ledger against independently parsed rows.
    ext = final_audit["extension"]
    if ext["pair_signs"]["raw"]["inconclusive"] != 12:
        raise AssertionError("Final audit raw pair ledger mismatch")
    if ext["critic_mse_better_count"] != 0 or ext["critic_hamiltonian_better_count"] != 0:
        raise AssertionError("Final audit mechanism ledger mismatch")
    result["checks"]["author_ledger_consistency"] = {
        "primary": final_audit["primary"],
        "extension": {
            "source_fits": ext["source_fits"],
            "policy_evaluations": ext["policy_evaluations"],
            "paired_comparisons": ext["paired_comparisons"],
            "pair_signs": ext["pair_signs"],
            "critic_mse_better_count": ext["critic_mse_better_count"],
            "critic_hamiltonian_better_count": ext["critic_hamiltonian_better_count"],
        },
    }

    if delivery_zip is not None:
        digest = sha256(delivery_zip)
        if digest != EXPECTED_DELIVERY_ZIP_SHA256:
            raise AssertionError(f"Delivery ZIP digest mismatch: {digest}")
        with zipfile.ZipFile(delivery_zip) as zf:
            names = zf.namelist()
            if not any(name.endswith("revisions/2026-10-04-r14/FINAL_AUDIT.json") for name in names):
                raise AssertionError("Delivery ZIP lacks FINAL_AUDIT.json")
        result["checks"]["delivery_zip"] = {
            "path": str(delivery_zip),
            "sha256": digest,
            "members": len(names),
        }

    if fixed_work_zip is not None:
        digest = sha256(fixed_work_zip)
        if digest != EXPECTED_FIXED_WORK_ZIP_SHA256:
            raise AssertionError(f"Fixed-work ZIP digest mismatch: {digest}")
        with zipfile.ZipFile(fixed_work_zip) as zf:
            ledger = zip_json(zf, "FIXED_WORK.json")
            pair = zip_json(zf, "paired_d10_s7919_k80_nbo_raw.json")
            mechanism = zip_json(zf, "nbo_d10_s7919_fixed_nbo_k80_mechanism.json")
            nbo_eval = zip_json(zf, "nbo_d10_s7919_fixed_nbo_k80_population_n1024.json")
            raw_eval = zip_json(zf, "nbo_d10_s7919_fixed_raw_k80_population_n1024.json")
        if ledger["source_commit"] != "c8299feb2a3af0f147295d50036c8d8acca8f65c" or not ledger["complete"]:
            raise AssertionError("Raw fixed-work ledger identity/completeness mismatch")
        if pair["bound"]["lower"] >= 0 or pair["bound"]["upper"] <= 0:
            raise AssertionError("Raw NBO-minus-Raw interval unexpectedly signed")
        if pair["bound"]["mean"] >= 0:
            raise AssertionError("Raw NBO-minus-Raw sample mean unexpectedly nonnegative")
        if mechanism["critic_costate_mse_to_fine_mean"] <= mechanism["raw_costate_mse_to_independent_fine_mean"]:
            raise AssertionError("Raw mechanism MSE ordering mismatch")
        if mechanism["critic_greedy_hamiltonian_gap"] <= mechanism["raw_greedy_hamiltonian_gap"]:
            raise AssertionError("Raw mechanism Hamiltonian ordering mismatch")
        assert_close(
            nbo_eval["bound"]["mean"] - raw_eval["bound"]["mean"],
            pair["bound"]["mean"],
            tol=1e-10,
        )
        result["checks"]["raw_fixed_work_spot_check"] = {
            "zip_sha256": digest,
            "source_commit": ledger["source_commit"],
            "dimension": ledger["dimension"],
            "seed": ledger["seed"],
            "nbo_critic_updates": next(x["critic_updates"] for x in ledger["fits"] if x["method"] == "nbo"),
            "nbo_actor_updates": next(x["actor_updates"] for x in ledger["fits"] if x["method"] == "nbo"),
            "raw_actor_updates": next(x["actor_updates"] for x in ledger["fits"] if x["tag"] == "_fixed_raw"),
            "nbo_minus_raw": pair["bound"],
            "mechanism": {
                "critic_costate_mse": mechanism["critic_costate_mse_to_fine_mean"],
                "raw_costate_mse": mechanism["raw_costate_mse_to_independent_fine_mean"],
                "critic_greedy_gap": mechanism["critic_greedy_hamiltonian_gap"],
                "raw_greedy_gap": mechanism["raw_greedy_hamiltonian_gap"],
            },
        }

    result["status"] = "passed"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--delivery-zip", type=Path)
    parser.add_argument("--fixed-work-zip", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.repo_root.resolve(), args.delivery_zip, args.fixed_work_zip)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
