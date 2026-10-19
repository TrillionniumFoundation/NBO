"""Post-outcome, read-only summaries of the already preregistered report tables.

No economic primitive, risk integral, actor, optimizer or sampling function is
imported. This is an authored interpretation derivative, not an experiment.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json


ARMS = ["online", "quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid"]
SERVICES = ["completed", "legacy-safe", "paired", "direct-refine"]
NAMES = {"online": "Online", "quadratic": "Quadratic", "relu": "ReLU",
         "hinge": "Hinge", "spline": "Spline", "poly2": "Poly2",
         "poly3": "Poly3", "grid": "Grid"}


def ident(p):
    b = p.read_bytes()
    return {"path": str(p), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report = args.revision.resolve() / "results120/reporting-attempt01"
    bindings = []

    def load(name):
        p = report / name
        bindings.append(ident(p))
        return json.loads(p.read_text())

    execution = load("EXECUTION_REPORT120.json")
    assert execution["exit_code"] == 0 and not execution["economic_solver_executed"]
    manifest = load("OUTPUT_MANIFEST120.json")
    manifest_files = {r["path"]: r for r in manifest["files"]}
    groups = load("tables120/groups120.json")
    contrasts = load("tables120/sample_contrasts120.json")
    timings = load("tables120/raw_timing_clocks120.json")
    levels = load("tables120/paired_bound_levels120.json")
    bound_groups = load("tables120/paired_bound_groups120.json")
    prices = load("tables120/price_domains120.json")
    population = load("tables120/population_groups120.json")
    group = {(r["index"], r["arm"], r["service"]): r for r in groups}
    clock = {(r["index"], r["arm"], r["service"], r["repeat"]): r for r in timings}
    pair = {(r["index"], r["a_arm"], r["a_service"], r["b_arm"], r["b_service"]): r
            for r in contrasts}
    cells = []
    for i in range(2):
        for arm in ARMS:
            row = {"index": i, "arm": arm}
            for a, b in [("legacy-safe", "paired"), ("legacy-safe", "direct-refine")]:
                r = pair[(i, arm, a, arm, b)]
                row[a + "_minus_" + b] = r
            for a, b in [("paired", "legacy-safe"), ("direct-refine", "legacy-safe"),
                         ("direct-refine", "paired")]:
                vals = [F(clock[i, arm, a, rep]["complete_observed32_total_seconds"]) /
                        F(clock[i, arm, b, rep]["complete_observed32_total_seconds"])
                        for rep in range(3)]
                row[a + "_over_" + b] = {
                    "all_three_in_recorded_order": list(map(str, vals)),
                    "median": str(sorted(vals)[1]), "minimum": str(min(vals)),
                    "maximum": str(max(vals)),
                    "actual_primary64": str(F(group[i, arm, a]["complete_observed64_total_seconds"]) /
                                            F(group[i, arm, b]["complete_observed64_total_seconds"]))}
            cells.append(row)
    totals = {}
    for service in SERVICES:
        rs = [r for r in groups if r["service"] == service]
        total = {k: sum(r[k] for r in rs) for k in
                 ["changed_state_actions", "accepted_steps", "candidate_attempts",
                  "rejected_candidate_attempts", "budget_exhausted_candidates",
                  "precision_attempts", "identical_action_shortcuts"]}
        for k in ["cohort64_seconds", "complete_observed64_total_seconds"]:
            total[k] = str(sum((F(r[k]) for r in rs), F(0)))
        total["compiled_terminal_rows"] = sum(r["querycounts"].get("compiled_terminal_rows", 0) for r in rs)
        total["terminal_original_risk_queries"] = sum(r["querycounts"].get("terminal_original_risk_queries", 0) for r in rs)
        totals[service] = total
    price_counts = Counter()
    for r in prices:
        if r["repeat"] == "intersection-all-three" and r["comparator"] == "every-conventional-menu-alternative":
            price_counts[(r["arm"], r["service"],
                          r["sufficient_positive_benefit_prices"]["empty"],
                          r["not_ruled_out_positive_benefit_prices"]["empty"])] += 1
    result = {
        "kind": "post-outcome descriptive interpretation of frozen reporting summaries",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "executed_source": ident(Path(__file__).resolve()), "inputs": bindings,
        "no_new_scientific_evaluation_or_population_family": True,
        "all16_cells": cells, "all4_service_totals": totals,
        "all992_contrast_signs": dict(Counter(r["sign"] for r in contrasts)),
        "new_mixed_upper_necessary_levels": [r for r in levels if r["accepted_needs_mixed_upper_at_recorded_resolution"]],
        "transfer_density_pairs": sum(r.get("density_pairs", 0) for r in bound_groups),
        "transfer_active_density_pairs": sum(r.get("transfer_active_density_pairs", 0) for r in bound_groups),
        "all_three_menu_price_counts": [{"arm": k[0], "service": k[1],
                                         "sufficient_empty": k[2], "upper_empty": k[3], "count": v}
                                        for k, v in sorted(price_counts.items())],
        "all48_population_lower_positive": sum(F(r["simultaneous_population_mean_lower"]) > 0 for r in population),
        "population_positive_lower_range": list(map(str, [
            min(F(r["simultaneous_population_mean_lower"]) for r in population if F(r["simultaneous_population_mean_lower"]) > 0),
            max(F(r["simultaneous_population_mean_lower"]) for r in population)])),
    }
    for rec in bindings:
        assert ident(Path(rec["path"])) == rec
        rel = str(Path(rec["path"]).relative_to(report))
        if rel in manifest_files:
            assert rec["sha256"] == manifest_files[rel]["sha256"]
    with (out / "INTERPRETATION_BINDINGS120.json").open("x") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")

    def interval(r):
        if r["sign"] == "exact-zero":
            return "$0$"
        lo = float(F(r["mean_original_j_a_minus_b_lower"])) * 1e6
        hi = float(F(r["mean_original_j_a_minus_b_upper"])) * 1e6
        return "$[" + f"{lo:.4f}, {hi:.4f}" + "]$"

    tex = [r"\begin{table}[htbp]", r"\centering\scriptsize",
           r"\setlength{\tabcolsep}{3pt}",
           r"\caption{The new rule against inherited refinement, with the direct comparator retained. Value columns enclose mean $J_L-J_P$ and $J_L-J_D$ in $10^{-6}$ original-objective units. Cost columns are medians of three matched-repeat $(A+T_{32})$ ratios; all individual clocks and endpoints remain in the complete reporting tables.}",
           r"\label{tab:incrementalcomparison120}", r"\begin{tabular}{llrrrr}",
           r"\toprule $\alpha$ & Arm & $J_L-J_P$ & $J_L-J_D$ & P/L cost & D/L cost \\ \midrule"]
    for r in cells:
        tex.append((r"$1/2$" if r["index"] == 0 else r"$3/4$") + " & " + NAMES[r["arm"]] +
                   " & " + interval(r["legacy-safe_minus_paired"]) + " & " + interval(r["legacy-safe_minus_direct-refine"]) +
                   " & " + f"{float(F(r['paired_over_legacy-safe']['median'])):.3f}" +
                   " & " + f"{float(F(r['direct-refine_over_legacy-safe']['median'])):.3f}" + r" \\")
    tex += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    with (out / "incremental_comparison120.tex").open("x") as f:
        f.write("\n".join(tex))
    print(json.dumps({"files": [ident(out / "INTERPRETATION_BINDINGS120.json"),
                                  ident(out / "incremental_comparison120.tex")],
                      "scientific_evaluation": False}))


if __name__ == "__main__":
    main()
