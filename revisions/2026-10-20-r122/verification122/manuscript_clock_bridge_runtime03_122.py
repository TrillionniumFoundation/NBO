"""Add omitted actual manuscript work without counting nested clocks twice.

The frozen ledger already counts all saved TeX/BibTeX command clocks. Its
automatic launch scopes do not include final_manuscript_runtime03. This reader
adds four exact outer-minus-command remainders, eight separate non-build outer
clocks, and three separately executed later administrative inner clocks. It
does not execute a build, scientific solver, fit, state draw, or service timer.
"""
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = "provenance122/final_manuscript_runtime03/"
INDEX = BASE + "OPERATION_CLOCK_INDEX122.json"
INDEX_SHA = "0bb2ccacb94a2d81ac83d3892d4b1da996a6aaa17267b03360271bd7f25a8fdf"
LEDGER = "verification122/research_cost_ledger122.py"
LEDGER_SHA = "37efa69184cca24946aec4e6914de10c848509709f3b24e5d67edc4cc028e08c"
EXPECTED_NON_BUILD = {
    "aggregate_launch02", "display_launch01", "figure_launch01",
    "pdf_inspection_launch01", "pdf_inspection_launch02",
    "probe_launch01", "probe_launch02", "probe_launch03",
}
ADMIN = [
    (BASE + "supp_tail_visual/SUPP_TAIL_RENDER122.json",
     "6835dfc24ee981a206c582ffd4cd3d7ba5a4c131eb0abc3ce4664747bf56cf99",
     "seconds", "additional_supplement_rendering",
     "The separate final two-page rendering followed the main PDF inspection; its two Poppler commands are enclosed and excluded as extra charges."),
    (BASE + "AUTHOR_FINAL_VISUAL_QA122.json",
     "fe9f0e00d02dd16ee143b4ff87034ac61bef8adecfdb0b8d229aa2585a335601",
     "receipt_operation_seconds_before_write", "final_visual_receipt_and_pdf_copy",
     "Separate source/hash readback and successful-preflight PDF copy/receipt assembly after the visual inspection; manual review and receipt write excluded."),
    (INDEX, INDEX_SHA, "index_operation_seconds_before_write", "author_clock_index_creation",
     "Separate Git/tree read and actual operation-clock index assembly after the final visual receipt; later file-list/manifest work and index write excluded."),
]


def main():
    start = time.perf_counter()
    source_bytes = Path(__file__).read_bytes()
    source_sha = sha256(source_bytes).hexdigest()
    output = ROOT / (BASE + "MANUSCRIPT_COST_BRIDGE122.json")
    assert not output.exists()
    inputs = {}

    def bind(name, expected=None, parse=True):
        path = ROOT / name
        assert path.is_file() and path.resolve().is_relative_to(ROOT)
        data = path.read_bytes()
        actual = sha256(data).hexdigest()
        if expected is not None:
            assert actual == expected, name
        item = {"path": name, "bytes": len(data), "sha256": actual}
        if name in inputs:
            assert inputs[name] == item
        inputs[name] = item
        return json.loads(data) if parse else data

    bind(LEDGER, LEDGER_SHA, False)
    index = bind(INDEX, INDEX_SHA)
    assert index["schema"] == "nbo.r122.author-operation-clock-index.v1"
    launches = {}
    for row in index["launches"]:
        name = row["path"]
        assert name.startswith(BASE) and name.endswith("/LAUNCH122.json")
        assert name not in launches
        obj = bind(name, row["sha256"])
        assert obj["status"] in ("executed", "failed")
        assert obj["exit_code"] == row["exit_code"]
        assert obj["outer_seconds"] == row["outer_seconds"]
        assert Q(obj["outer_seconds"]) >= 0
        assert not obj.get("cost_clock_components")
        launches[name] = obj
    assert len(launches) == 12
    rows, exclusions = [], []
    builds = set()
    for entry in index["build_clock_nesting"]:
        name, launch_name = entry["build_receipt"], entry["launch"]
        assert launch_name in launches and launch_name not in builds
        builds.add(launch_name)
        build = bind(name, entry["build_receipt_sha256"])
        assert name.startswith("build_receipts122/")
        commands = build["commands"]
        assert len(commands) == 19
        assert all(c["exit_code"] == 0 for c in commands)
        assert sum(c["argv"][0] == "pdflatex" for c in commands) == 16
        assert sum(c["argv"][0] == "bibtex" for c in commands) == 3
        assert build["status"] == entry["strict_status"]
        for command in commands:
            bind(command["log"], command["log_sha256"], False)
        # Use exact rational conversions of the saved numeric values, exactly
        # as the frozen ledger does. Do not reuse the rounded index subtotal.
        inner = sum((Q(c["elapsed_seconds"]) for c in commands), Q(0))
        outer = Q(launches[launch_name]["outer_seconds"])
        assert outer >= inner
        rows.append({
            "category": "manuscript_build_outer_remainder",
            "source_path": launch_name,
            "source_sha256": inputs[launch_name]["sha256"],
            "saved_clock_fields": [["outer_seconds"]],
            "nested_source_path": name,
            "nested_source_sha256": inputs[name]["sha256"],
            "nested_clock_fields": [["commands", j, "elapsed_seconds"] for j in range(19)],
            "outer_seconds_exact": str(outer),
            "automatically_counted_command_seconds_exact": str(inner),
            "seconds_exact": str(outer - inner),
            "actual_launch_exit_code": launches[launch_name]["exit_code"],
            "scope": "Only this actual build outer clock minus its 19 serial TeX/BibTeX command clocks, already counted by the unchanged frozen ledger. Failed/diagnostic renderings are retained.",
        })
        exclusions.append({"path": name, "reason": "All 19 enclosed command clocks remain counted by the frozen ledger; they are subtracted from this bridge row."})
    assert len(builds) == 4
    non_build = set(launches) - builds
    assert {Path(p).parent.name for p in non_build} == EXPECTED_NON_BUILD
    for name in sorted(non_build):
        obj = launches[name]
        rows.append({
            "category": "manuscript_separate_administrative_outer",
            "source_path": name, "source_sha256": inputs[name]["sha256"],
            "saved_clock_fields": [["outer_seconds"]],
            "seconds_exact": str(Q(obj["outer_seconds"])),
            "actual_launch_exit_code": obj["exit_code"],
            "child_output": obj.get("child_output"),
            "scope": "This distinct actual non-build child spawn-to-exit outer clock, including all enclosed reader/renderer/command clocks. It lies outside the frozen automatic launch scopes. No enclosed receipt is an additional charge.",
        })
        exclusions.append({"path": name, "child_output": obj.get("child_output"), "reason": "All child/renderer/probe clocks inside this counted outer are excluded from additional charges; do not also pass them as separate additional cost receipts."})
    for name, expected, field, category, scope in ADMIN:
        obj = bind(name, expected)
        assert Q(obj[field]) >= 0
        rows.append({
            "category": category, "source_path": name,
            "source_sha256": inputs[name]["sha256"],
            "saved_clock_fields": [[field]], "seconds_exact": str(Q(obj[field])),
            "scope": scope, "distinct_later_operation_not_enclosed_by_listed_launches": True,
        })
    assert len(rows) == 15
    for name, item in inputs.items():
        data = (ROOT / name).read_bytes()
        assert len(data) == item["bytes"] and sha256(data).hexdigest() == item["sha256"], name
    assert Path(__file__).read_bytes() == source_bytes
    result = {
        "schema": "nbo.r122.manuscript-clock-bridge.v1",
        "status": "verified_saved_nonoverlapping_administrative_clock_bridge",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reader_sha256": source_sha,
        "frozen_ledger_sha256": LEDGER_SHA,
        "inputs": sorted(inputs.values(), key=lambda item: item["path"]),
        "rows": rows,
        "recorded_additional_seconds_exact_excluding_reader": str(sum((Q(r["seconds_exact"]) for r in rows), Q(0))),
        "excluded_nested_clocks": exclusions,
        "elapsed_seconds": time.perf_counter() - start,
        "cost_clock_components": [
            {"category": row["category"], "clock_fields": [["rows", i, "seconds_exact"]],
             "partial_lower_bound_only": True, "overlaps_counted_parent": False, "scope": row["scope"]}
            for i, row in enumerate(rows)
        ] + [{"category": "manuscript_clock_bridge_reader", "clock_fields": [["elapsed_seconds"]],
              "partial_lower_bound_only": True, "overlaps_counted_parent": False,
              "scope": "This separately executed source/hash/readback and exact-rational administrative reader only; interpreter startup and final receipt write excluded."}],
        "unknown_complete_clocks": [
            {"scope": name, "seconds": None} for name in index["unknown_complete_clocks"]
        ],
        "whole_study_exact_total_seconds": None,
        "manual_visual_review_seconds": None,
        "new_states": 0, "new_training": 0, "new_economic_evaluations": 0,
        "new_service_timing_processes": 0,
        "scope": "Additive saved administrative cost accounting only. Exact Fraction arithmetic reflects saved floating-point values; it does not increase the physical precision of the clocks. Prior receipts, frozen scientific data, standalone service allocations and the frozen ledger are unchanged.",
    }
    with output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"receipt": str(output.relative_to(ROOT)), "sha256": sha256(output.read_bytes()).hexdigest(),
                      "rows": len(rows), "authenticated_inputs": len(inputs),
                      "old_seconds_exact": result["recorded_additional_seconds_exact_excluding_reader"],
                      "reader_seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
