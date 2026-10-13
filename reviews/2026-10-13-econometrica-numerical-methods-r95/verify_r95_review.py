#!/usr/bin/env python3
"""Deterministic audit for the advisory Econometrica numerical-methods review of NBO R95.

This script reads the pinned R95 manuscript tables and release ledgers from a full
repository checkout. It does not refit models, rerun policy services, reproduce
process clocks, or formally verify proofs. Its purpose is to make the report's
table-level calculations and release-blocker finding reproducible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

PINNED_REVISION = "85263fd95ccbb60f0cf1875c0f29f1b7c2558a34"
PINNED_TREE = "c302a05050f1100b86398db3f5e6a2e99fc8500a"
REVISION_DIR = Path("revisions/2026-10-13-r95")
MARGIN = 1.0 / 16.0

EXPECTED_BLOBS = {
    "ECTA.tex": "8cf26137129209e533d3e457357a14cb3f980a85",
    "supp.tex": "4cbab50c9757fbaff5bd2ae10255f22247d20520",
    "appendix.tex": "448f3ac0b44a5107d9c4cdf2c3c26f996969711d",
    "response.md": "c0c098bb6663d92ed6d8c75f12ccc0214f319726",
    "RELEASE95.json": "37de0eda13e4fa0e9944b084243f2dfa77759ec0",
}

def fail(message: str) -> None:
    raise AssertionError(message)

def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()

def read_text(root: Path, rel: str) -> str:
    path = root / REVISION_DIR / rel
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")

def parse_float(value: str) -> float:
    return float(value.replace(",", "").strip())

def data_rows(text: str) -> list[str]:
    rows: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if "&" not in s or not s.endswith(r"\\"):
            continue
        if any(token in s for token in (r"\toprule", r"\midrule", r"\bottomrule")):
            continue
        if s.startswith("$\\alpha$"):
            continue
        rows.append(s[:-2].strip())
    return rows

def parse_fits(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"^(?P<alpha>\d+(?:\.\d+)?)\s*&\s*(?P<method>[^&]+?)\s*&\s*"
        r"(?P<rank>\d+)\s*&\s*(?P<rmse>-?\d+(?:\.\d+)?)\s*&\s*"
        r"\[(?P<lo>-?\d+(?:\.\d+)?),\s*(?P<hi>-?\d+(?:\.\d+)?)\]$"
    )
    parsed = []
    for row in data_rows(text):
        match = pattern.match(row)
        if not match:
            fail(f"Unparsed fits row: {row}")
        item = match.groupdict()
        lo, hi = parse_float(item["lo"]), parse_float(item["hi"])
        parsed.append({
            "alpha": parse_float(item["alpha"]),
            "method": item["method"].strip().lower(),
            "rank": int(item["rank"]),
            "rmse": parse_float(item["rmse"]),
            "lo": lo,
            "hi": hi,
            "width": hi - lo,
        })
    return parsed

def parse_accounts(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"^(?P<alpha>\d+(?:\.\d+)?)\s*&\s*(?P<method>[^&]+?)\s*&\s*"
        r"(?P<sup>-?\d+(?:\.\d+)?)\s*&\s*(?P<signed>-?\d+(?:\.\d+)?)\s*&\s*"
        r"(?P<joint>-?\d+(?:\.\d+)?)\s*&\s*(?P<qualified>[\d,]+/[\d,]+)$"
    )
    parsed = []
    for row in data_rows(text):
        match = pattern.match(row)
        if not match:
            fail(f"Unparsed accounts row: {row}")
        item = match.groupdict()
        num, den = (int(x.replace(",", "")) for x in item["qualified"].split("/"))
        parsed.append({
            "alpha": parse_float(item["alpha"]),
            "method": item["method"].strip().lower(),
            "supremum": parse_float(item["sup"]),
            "signed": parse_float(item["signed"]),
            "joint": parse_float(item["joint"]),
            "qualified": num,
            "total": den,
        })
    return parsed

def parse_costs(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"^(?P<alpha>\d+(?:\.\d+)?)\s*&\s*(?P<method>[^&]+?)\s*&\s*"
        r"\[(?P<lo>-?\d+(?:\.\d+)?),\s*(?P<hi>-?\d+(?:\.\d+)?)\]\s*&\s*"
        r"(?P<loss>-?\d+(?:\.\d+)?)\s*&\s*(?P<failures>\d+)$"
    )
    parsed = []
    for row in data_rows(text):
        match = pattern.match(row)
        if not match:
            fail(f"Unparsed cost row: {row}")
        item = match.groupdict()
        parsed.append({
            "alpha": parse_float(item["alpha"]),
            "method": item["method"].strip().lower(),
            "lo": parse_float(item["lo"]),
            "hi": parse_float(item["hi"]),
            "loss": parse_float(item["loss"]),
            "failures": int(item["failures"]),
        })
    return parsed

def parse_work(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"^(?P<alpha>\d+(?:\.\d+)?)\s*&\s*(?P<method>[^&]+?)\s*&\s*"
        r"(?P<seconds>\d+(?:\.\d+)?)\s*&\s*(?P<proposals>[\d,]+)\s*&\s*"
        r"(?P<witnesses>[\d,]+)$"
    )
    parsed = []
    for row in data_rows(text):
        match = pattern.match(row)
        if not match:
            fail(f"Unparsed work row: {row}")
        item = match.groupdict()
        parsed.append({
            "alpha": parse_float(item["alpha"]),
            "method": item["method"].strip().lower(),
            "seconds": parse_float(item["seconds"]),
            "proposals": int(item["proposals"].replace(",", "")),
            "witnesses": int(item["witnesses"].replace(",", "")),
        })
    return parsed

def parse_pairs(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"^(?P<alpha>\d+(?:\.\d+)?)\s*&\s*(?P<contrast>.+?)\s*&\s*"
        r"\[(?P<lo>-?\d+(?:\.\d+)?),\s*(?P<hi>-?\d+(?:\.\d+)?)\]\s*&\s*"
        r"(?P<sampling>\d+(?:\.\d+)?)\s*&\s*(?P<equiv>Yes|No)$"
    )
    parsed = []
    for row in data_rows(text):
        match = pattern.match(row)
        if not match:
            fail(f"Unparsed pair row: {row}")
        item = match.groupdict()
        lo, hi = parse_float(item["lo"]), parse_float(item["hi"])
        parsed.append({
            "alpha": parse_float(item["alpha"]),
            "contrast": item["contrast"].strip(),
            "lo": lo,
            "hi": hi,
            "width": hi - lo,
            "midpoint": (lo + hi) / 2.0,
            "sampling": parse_float(item["sampling"]),
            "equivalent": item["equiv"] == "Yes",
        })
    return parsed

def parse_screens(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"^(?P<alpha>\d+(?:\.\d+)?)\s*&\s*(?P<method>[^&]+?)\s*&\s*"
        r"(?P<excluded>[\d,]+)/(?P<candidate>[\d,]+)\s*&\s*(?P<nocut>\d+)\s*&\s*"
        r"(?P<full>\d+(?:\.\d+)?)\s*&\s*(?P<pruned>\d+(?:\.\d+)?)$"
    )
    parsed = []
    for row in data_rows(text):
        match = pattern.match(row)
        if not match:
            fail(f"Unparsed screen row: {row}")
        item = match.groupdict()
        parsed.append({
            "alpha": parse_float(item["alpha"]),
            "method": item["method"].strip().lower(),
            "excluded": int(item["excluded"].replace(",", "")),
            "candidate": int(item["candidate"].replace(",", "")),
            "no_cut": int(item["nocut"]),
            "full_ms": parse_float(item["full"]),
            "pruned_ms": parse_float(item["pruned"]),
        })
    return parsed

def verify_blob_identities(root: Path) -> None:
    for rel, expected in EXPECTED_BLOBS.items():
        data = (root / REVISION_DIR / rel).read_bytes()
        actual = git_blob_sha1(data)
        if actual != expected:
            fail(f"Git blob mismatch for {rel}: {actual} != {expected}")

def run_audit(root: Path) -> dict[str, Any]:
    verify_blob_identities(root)

    fits = parse_fits(read_text(root, "tables/fits95.tex"))
    accounts = parse_accounts(read_text(root, "tables/accounts95.tex"))
    costs = parse_costs(read_text(root, "tables/cost95.tex"))
    work = parse_work(read_text(root, "tables/work95.tex"))
    pairs = parse_pairs(read_text(root, "tables/pairs95.tex"))
    screens = parse_screens(read_text(root, "tables/screens95.tex"))

    if [len(x) for x in (fits, accounts, costs, work, pairs, screens)] != [6, 6, 8, 8, 12, 8]:
        fail("Unexpected table row counts")

    if any(row["failures"] != 0 for row in costs):
        fail("A cost row has a qualification failure")
    max_loss = max(row["loss"] for row in costs)
    if not max_loss < MARGIN:
        fail("Maximum loss does not meet qualification target")

    if not all(row["lo"] <= 0.0 <= row["hi"] for row in pairs):
        fail("A paired interval excludes zero")
    if not all(row["lo"] > -MARGIN and row["hi"] < MARGIN and row["equivalent"] for row in pairs):
        fail("A paired interval fails the declared equivalence rule")

    fit_groups: dict[float, list[dict[str, Any]]] = {}
    for row in fits:
        fit_groups.setdefault(row["alpha"], []).append(row)
    for alpha, rows in fit_groups.items():
        relu = next(row for row in rows if row["method"] == "relu")
        if relu["width"] != min(row["width"] for row in rows):
            fail(f"ReLU is not the narrowest residual at alpha={alpha}")

    account_groups: dict[float, list[dict[str, Any]]] = {}
    for row in accounts:
        account_groups.setdefault(row["alpha"], []).append(row)
    for alpha, rows in account_groups.items():
        if not all(row["qualified"] == row["total"] == 2048 for row in rows):
            fail(f"Not every fitted row qualifies at alpha={alpha}")
        best = min(rows, key=lambda row: row["joint"])
        if best["method"] != "quadratic":
            fail(f"Quadratic is not the sharpest joint certificate at alpha={alpha}")

    reductions: list[float] = []
    speedups: list[float] = []
    for alpha in (0.5, 0.75):
        rows = [row for row in work if row["alpha"] == alpha]
        online = next(row for row in rows if row["method"] == "online risk-dp")
        fitted = [row for row in rows if row["method"] != "online risk-dp"]
        for row in fitted:
            if not row["seconds"] < online["seconds"]:
                fail(f"Fitted arm is not faster: alpha={alpha}, method={row['method']}")
            reductions.append(100.0 * (1.0 - row["seconds"] / online["seconds"]))
            speedups.append(online["seconds"] / row["seconds"])

    if not all(row["pruned_ms"] > row["full_ms"] for row in screens):
        fail("A screening row is not slower after paying for pruning")

    release = json.loads(read_text(root, "RELEASE95.json"))
    tests = json.loads(read_text(root, "audit/remote95/tests/TESTS95.json"))
    expected_gates = {
        "current_pdfs": True,
        "independent_kernel": True,
        "original_csv_identity": True,
        "tests": False,
    }
    if release["gates"] != expected_gates:
        fail(f"Unexpected release gates: {release['gates']}")

    passing_suites = sum(bool(value["passed"]) for value in tests.values())
    total_tests = sum(int(value["tests"]) for value in tests.values())
    passed_tests = sum(int(value["tests"]) for value in tests.values() if value["passed"])
    failed_suite = tests.get("tests_publication72")
    if len(tests) != 17 or passing_suites != 16 or total_tests != 401:
        fail("Unexpected test-ledger totals")
    if not failed_suite or failed_suite["passed"] or failed_suite["tests"] != 6:
        fail("Expected publication72 failure not found")
    # The log identifies one failure among the six tests in the failed suite.
    passed_tests += 5

    prep = json.loads(read_text(root, "audit/PREPARATION72.json"))
    expected_core = prep["unchanged_active_sections"]["sections/core49.tex"]["sha256"]
    actual_core = hashlib.sha256(
        (root / REVISION_DIR / "sections/core49.tex").read_bytes()
    ).hexdigest()
    if actual_core == expected_core:
        fail("Expected preservation-ledger mismatch is absent")

    widths = [row["width"] for row in pairs]
    midpoints = [abs(row["midpoint"]) for row in pairs]
    return {
        "schema_version": 1,
        "status": "passed_with_release_blocker",
        "pinned_revision": PINNED_REVISION,
        "pinned_tree": PINNED_TREE,
        "records": {
            "arm_state_records": 8 * 2048,
            "independent_initial_states": 2 * 2048,
            "qualification_failures": sum(row["failures"] for row in costs),
            "maximum_original_optimum_loss_bound": max_loss,
        },
        "paired_inference": {
            "contrasts": len(pairs),
            "all_contain_zero": True,
            "all_within_margin": True,
            "margin": MARGIN,
            "width_min": min(widths),
            "width_max": max(widths),
            "width_mean": sum(widths) / len(widths),
            "largest_absolute_midpoint": max(midpoints),
        },
        "work": {
            "time_reduction_percent_min": min(reductions),
            "time_reduction_percent_max": max(reductions),
            "speedup_min": min(speedups),
            "speedup_max": max(speedups),
        },
        "screening": {
            "rows": len(screens),
            "pruned_slower_rows": sum(row["pruned_ms"] > row["full_ms"] for row in screens),
        },
        "release": {
            "gates": release["gates"],
            "test_suites": len(tests),
            "passing_test_suites": passing_suites,
            "individual_tests": total_tests,
            "passing_individual_tests": passed_tests,
            "expected_core49_sha256": expected_core,
            "actual_core49_sha256": actual_core,
        },
    }

def self_test() -> None:
    sample = r"""
0.5 & ReLU & 35 & 0.01668 & [-0.04373, 0.08665]\\
0.75 & Spline & 35 & 0.03984 & [-0.10431, 0.45189]\\
"""
    rows = parse_fits(sample)
    assert len(rows) == 2
    assert math.isclose(rows[0]["width"], 0.13038, rel_tol=0.0, abs_tol=1e-12)
    assert rows[1]["method"] == "spline"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print(json.dumps({"status": "self-test-passed"}, sort_keys=True))
        return 0

    result = run_audit(args.repo_root.resolve())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
