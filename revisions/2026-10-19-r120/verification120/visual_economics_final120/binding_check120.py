"""Read-only final PDF/table/figure binding; never imports scientific code."""
from pathlib import Path
from fractions import Fraction as F
import datetime as dt
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ARMS = ["online", "quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid"]
NAMES = ["Online", "Quadratic", "ReLU", "Hinge", "Spline", "Poly2", "Poly3", "Grid"]
SERVICES = ["completed", "legacy-safe", "paired", "direct-refine"]


def ident(p):
    b = p.read_bytes()
    return {"path": str(p.relative_to(ROOT)), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}


def main():
    pdf = ROOT / "build/ECTA.pdf"
    pdf_id = ident(pdf)
    assert pdf_id["sha256"] == "0b1dcc7a40388b6b278012dc8257e46b37a316de6ee044024f75e6fe2518e791"
    build_path = ROOT / "build_receipts120/20261019T091308.243215Z/BUILD_RECEIPT120.json"
    build = json.loads(build_path.read_text())
    assert build["status"] == "compiled_clean" and not build["issues"]
    assert next(x for x in build["pdfs"] if x["path"] == "build/ECTA.pdf") == pdf_id
    source_paths = ["new120/results120.tex", "new120/development120_results.tex",
                    "new120/economic_interpretation120.tex", "new120/comparison_figure120.tex",
                    "new120/numerical120.tex"]
    sources = [ident(ROOT / p) for p in source_paths]
    for x in sources:
        assert build["source_sha256"][x["path"]] == x["sha256"]
    report = ROOT / "results120/reporting-attempt01"
    loaded = {}
    inputs = []
    for name in ["groups120", "population_groups120", "raw_timing_clocks120", "sample_contrasts120"]:
        p = report / "tables120" / (name + ".json")
        inputs.append(ident(p))
        loaded[name] = json.loads(p.read_text())
    groups = {(x["index"], x["arm"], x["service"]): x for x in loaded["groups120"]}
    population = {(x["index"], x["arm"], x["service"]): x for x in loaded["population_groups120"]}
    clocks = {(x["index"], x["arm"], x["service"], x["repeat"]): x for x in loaded["raw_timing_clocks120"]}
    contrasts = {(x["index"], x["a_arm"]): x for x in loaded["sample_contrasts120"]
                 if x["a_arm"] == x["b_arm"] and x["a_service"] == "legacy-safe" and x["b_service"] == "paired"}
    text = (OUT / "final_s/PAGES31_42_LAYOUT120.txt").read_text().split("\f")
    assert "Proposition S.12" in text[0]
    assert "Proposition 12" in text[0]
    final_render = json.loads((OUT/"final_s/RENDER_RECEIPT120.json").read_text())
    assert final_render["pdf"] == pdf_id and final_render["exit_code"] == 0
    assert final_render["build_receipt_sha256"] == ident(build_path)["sha256"]
    assert [x["path"] for x in final_render["rendered_pages"] if not x["byte_identical_to_previous_visual_render"]] == ["page-31.png"]
    for x in final_render["rendered_pages"]:
        got = ident(OUT/"final_s"/x["path"])
        assert got["bytes"] == x["bytes"] and got["sha256"] == x["sha256"]
        assert ident(OUT/x["path"])["sha256"] == x["previous_sha256"]
    source = (ROOT / "new120/results120.tex").read_text()
    source_tables = source.split("\\begin{longtable}")[1:]
    assert len(source_tables) == 3
    number = lambda value, scale=1, digits=3: f"{float(F(value)*scale):.{digits}f}"
    pdf_pattern = re.compile(r"(?<![\d/])(1/2|3/4)\s+(Online|Quadratic|ReLU|Hinge|Spline|Poly2|Poly3|Grid)\s+(.*)")
    source_pattern = re.compile(r"^\$(1/2|3/4)\$ & (Online|Quadratic|ReLU|Hinge|Spline|Poly2|Poly3|Grid) & (.*)", re.M)
    rows_checked = []
    for table, pages in enumerate([[32], [33], [34, 35]]):
        tex_rows = {(risk, arm): re.findall(r"-?\d+\.\d+", vals) for risk, arm, vals in source_pattern.findall(source_tables[table])}
        pdf_rows = {}
        for pn in pages:
            for line in text[pn-31].splitlines():
                m = pdf_pattern.search(line)
                if m:
                    key = m.group(1), m.group(2)
                    assert key not in pdf_rows
                    pdf_rows[key] = re.findall(r"-?\d+\.\d+", m.group(3))
        assert len(tex_rows) == len(pdf_rows) == 16
        for i in range(2):
            for arm, name in zip(ARMS, NAMES):
                key = ("1/2" if i == 0 else "3/4", name)
                expected = []
                if table == 0:
                    row = groups[i, arm, "completed"]
                    expected.extend(number(row[x], digits=6) for x in ["original_j_mean_lower", "original_j_mean_upper"])
                    for service in SERVICES[1:]:
                        row = groups[i, arm, service]
                        expected.extend(number(row[x], 10**6) for x in ["own_incumbent_gain_mean_lower", "own_incumbent_gain_mean_upper"])
                elif table == 1:
                    expected = [number(groups[i, arm, service]["complete_observed64_total_seconds"]) for service in SERVICES]
                else:
                    for service in SERVICES[1:]:
                        row = population[i, arm, service]
                        expected.extend(number(row[x], 10**6) for x in ["simultaneous_population_mean_lower", "simultaneous_population_mean_upper"])
                assert expected == tex_rows[key] == pdf_rows[key], (table, key)
                rows_checked.append({"table": table+2, "risk": key[0], "arm": arm,
                                     "displayed_numbers": expected, "raw_source_pdf_agree": True})
    plotted_path = ROOT / "figures120/PLOTTED_VALUES120.json"
    plotted = json.loads(plotted_path.read_text())
    assert len(plotted) == 16
    for j, row in enumerate(plotted):
        i, arm = divmod(j, 8)[0], ARMS[j % 8]
        assert (row["index"], row["arm"]) == (i, arm)
        expected_clocks = [F(clocks[i, arm, "paired", q]["complete_observed32_total_seconds"]) /
                           F(clocks[i, arm, "legacy-safe", q]["complete_observed32_total_seconds"]) for q in range(3)]
        assert list(map(F, row["clock_ratios"])) == expected_clocks
        assert F(row["primary_ratio"]) == F(groups[i, arm, "paired"]["complete_observed64_total_seconds"]) / F(groups[i, arm, "legacy-safe"]["complete_observed64_total_seconds"])
        pair = contrasts[i, arm]
        assert F(row["gain_lower"]) == F(pair["mean_original_j_a_minus_b_lower"])
        assert F(row["gain_upper"]) == F(pair["mean_original_j_a_minus_b_upper"])
    assert sum(F(x["gain_lower"]) == F(x["gain_upper"]) == 0 for x in plotted) == 9
    assert sum(F(x["gain_lower"]) < 0 < F(x["gain_upper"]) for x in plotted) == 7
    figure_receipt = json.loads((ROOT / "figures120/FIGURE_RECEIPT120.json").read_text())
    assert figure_receipt["script_sha256"] == ident(ROOT/"verification120/figure120.py")["sha256"]
    for name, entry in figure_receipt["outputs"].items():
        x = ident(ROOT / "figures120" / name)
        assert entry["bytes"] == x["bytes"] and entry["sha256"] == x["sha256"]
    for name in ["figures120/paired_legacy120.pdf", "figures120/paired_legacy120.png"]:
        assert build["graphic_asset_sha256"][name] == ident(ROOT/name)["sha256"]
    assert ident(pdf) == pdf_id
    for x in sources + inputs:
        assert ident(ROOT/x["path"]) == x
    receipt = {"kind": "final numerical PDF visual and exact source binding",
               "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "status": "numerical_and_layout_checks_passed",
               "executed_binding_source": ident(Path(__file__)), "pdf": pdf_id,
               "build_receipt": ident(build_path), "sources": sources, "inputs": inputs,
               "reviewed_pages": list(range(31, 43)), "render_dpi": 100,
               "render_receipt": ident(OUT/"final_s/RENDER_RECEIPT120.json"),
               "prior_render_receipt": ident(OUT/"RENDER_RECEIPT120.json"),
               "implementation_history": ident(OUT/"BINDING_IMPLEMENTATION_HISTORY120.json"),
               "visual_review_custody": {"initial_pages_actually_viewed": list(range(31,43)),
                 "initial_pdf_sha256": "0bfdd0e06a79a134db3f8619d48b8ef9c5c158e766a61e05427b73c05bca47bb",
                 "final_materially_changed_pages_actually_viewed": [31],
                 "final_pages_byte_identical_to_previously_viewed_pngs": list(range(32,43)),
                 "reviewer": "AI author assistant"},
               "all48_table_rows": rows_checked,
               "displayed_scalar_numbers_checked": sum(len(x["displayed_numbers"]) for x in rows_checked),
               "all16_figure_records_exactly_match_saved_tables": True,
               "figure_clock_ratios": 48, "figure_primary_ratios": 16,
               "figure_exact_zero_cells": 9, "figure_unresolved_cells": 7,
               "manual_visual_review": {"reviewer": "AI author assistant", "clipping": False,
                 "overlap": False, "missing_or_truncated_table_rows": False,
                 "illegible_math_or_captions": False, "figure_legends_cover_data": False,
                 "population_table_continuation": "Clean repeated header across pages34 and35",
                 "figure_placement": "Intentional page float on42 after references",
                 "zero_enclosures": "All nine have coincident blue endpoint marks at zero"},
               "caption_scope": {"timing_ranges_are_descriptive": True,
                 "economic_intervals_are_numerical_not_population_CIs": True,
                 "all_cells_included": True, "cost_and_research_validation_scopes_distinct": True,
                 "12_individual_and2_primary_upper_regions_preserved_in_visible_text": True},
               "navigation_note": {"page": 31, "status": "resolved_in_final_build",
                 "original_finding": "The independent supplement witness and the main population result both printed Proposition12 in the prior PDF; prior hyperlinks were correct.",
                 "final_visually_confirmed": "Independent witness prints Proposition S.12; population result prints Proposition12.",
                 "reported_to_root": True},
               "scientific_execution_or_primary_timing_rerun": False,
               "pdf_or_author_sources_modified": False}
    with (OUT/"VISUAL_ECONOMICS_RECEIPT120.json").open("x") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"receipt": ident(OUT/"VISUAL_ECONOMICS_RECEIPT120.json"),
                      "table_rows": 48, "numbers": 288, "figure_cells": 16,
                      "source_and_raw_bytes_unchanged": True}))


if __name__ == "__main__":
    main()
