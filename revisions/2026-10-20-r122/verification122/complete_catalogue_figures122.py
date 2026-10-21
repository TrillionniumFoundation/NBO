"""Publication figures from every saved R122 intervention and timing clock.

No economic computation, training, sampling, policy refinement, timing rerun
or source mutation occurs here.  The script refuses an incomplete report,
requires the disclosed protocol adapter receipt, and displays all 116
within-actor contrasts in four fixed risk/service panels.  No result-based
row filtering or ordering is supported.  Output is a four-page PDF, four
PNG pages and a source/hash/data receipt.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time

F_COMMIT = "2f483615c8bc0037e43ec01a16cce05c724f8c60"
FIELDS = ("index", "budget", "arm", "loss", "service")
ARMS = ("quadratic", "relu", "hinge", "spline", "poly2", "poly3", "grid")
SERVICES = ("recycled", "adaptive")
CLOCKS = ("timing00", "timing01", "timing02")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]


def key(row):
    return tuple(row[name] for name in FIELDS)


def catalog(index):
    return [(index, 0, "online", "online")] + [
        (index, budget, arm, loss)
        for budget in (5, 9) for arm in ARMS for loss in ("value", "marginal")]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.report.resolve()
    output = args.output.resolve()
    tick = time.perf_counter()
    bound_inputs = {}

    def load(name, jsonl=False):
        p = source / name
        bound_inputs[name] = {"bytes": p.stat().st_size, "sha256": sha(p)}
        return rows(p) if jsonl else read(p)

    stage = load("EXECUTION122.json")
    outer = load("OUTER_EXECUTION122.json")
    for receipt in (stage, outer):
        require(receipt.get("status") == "executed" and receipt.get("exit_code") == 0,
                "A complete actually executed adapted report is required")
    require(Path(outer["child_output"]).resolve() == source,
            "Outer receipt belongs to a different report directory")
    verified = load("VERIFIED_SOURCE122.json")
    require(verified.get("source_commit") == F_COMMIT and verified.get("files") == 243,
            "Wrong frozen scientific source identity")
    adapter = load("REPORTING_PROTOCOL_ADAPTER122.json")
    require(adapter.get("status") == "executed",
            "The protocol adapter must have an actual successful receipt")
    load("REPORTING_ADAPTER122.json")
    summary = load("SUMMARY_REPORT122.json")
    require(summary.get("source_commit") == F_COMMIT and
            summary.get("primary_decisions") == 5568 and
            summary.get("treatment_population_cells") == 116 and
            summary.get("independent_state_units") == 32,
            "Incomplete or different scientific report")
    manifest = load("OUTPUT_MANIFEST122.json")
    manifest_map = {row["path"]: row for row in manifest["files"]}
    table_names = ("SERVICE_CONTRASTS122.jsonl", "CLOCKS122.jsonl", "POLICY_CELLS122.jsonl")
    for name in table_names:
        p = source / name
        require(name in manifest_map and manifest_map[name]["sha256"] == sha(p),
                "Report table is absent from or differs from its own output manifest: " + name)
    contrasts = load(table_names[0], True)
    clocks = load(table_names[1], True)
    policies = load(table_names[2], True)
    c = {key(row): row for row in contrasts}
    clock = {(row["scenario"], key(row)): row for row in clocks}
    policy = {key(row): row for row in policies}
    expected = {k + (s,) for i in range(2) for k in catalog(i) for s in SERVICES}
    allcells = {k + (s,) for i in range(2) for k in catalog(i)
                for s in ("control",) + SERVICES}
    require(len(contrasts) == len(c) == 116 and set(c) == expected,
            "All 116 intervention contrasts, with no duplicates, are required")
    require(len(policies) == len(policy) == 174 and set(policy) == allcells,
            "All 174 policy cells are required")
    require(len(clocks) == len(clock) == 696 and set(clock) ==
            {(s, k) for s in ("primary32",) + CLOCKS for k in allcells},
            "One primary and all three timing clocks are required for every cell")

    plotted = []
    for i in range(2):
        for service in SERVICES:
            for actor in catalog(i):
                k, control = actor + (service,), actor + ("control",)
                r = c[k]
                require(r["n"] == 32, "Plot cannot change independent sample size")
                observations = []
                for scenario in CLOCKS:
                    tr, co = clock[scenario, k], clock[scenario, control]
                    require(tr["n"] == co["n"] == 16, "Timing cohort is not the frozen first 16 states")
                    extra = (F(tr["fully_allocated_matching_cohort_seconds"]) -
                             F(co["fully_allocated_matching_cohort_seconds"])) / 16
                    observations.append({"scenario": scenario,
                        "treatment_full_allocated_16_seconds": tr["fully_allocated_matching_cohort_seconds"],
                        "control_full_allocated_16_seconds": co["fully_allocated_matching_cohort_seconds"],
                        "added_full_allocated_seconds_per_decision": str(extra)})
                plotted.append({**dict(zip(FIELDS, k)),
                    "changed_actions": policy[k]["changed_actions"],
                    "sample_gain_lower": r["sample_gain_lower"],
                    "sample_gain_upper": r["sample_gain_upper"],
                    "raw_independent_sample_gain_lower": r["raw_independent_sample_gain_lower"],
                    "raw_independent_sample_gain_upper": r["raw_independent_sample_gain_upper"],
                    "population_gain_lower": r["population_gain_lower"],
                    "population_gain_upper": r["population_gain_upper"],
                    "mean_certified_gain_lower": r["mean_certified_gain_lower"],
                    "clocks": observations})
    require(len(plotted) == 116 and sum(len(r["clocks"]) for r in plotted) == 348,
            "No intervention or timing clock may be omitted")

    output.mkdir(parents=True, exist_ok=False)
    # Only the plotting dependency is imported; no scientific code is loaded.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.lines import Line2D

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "pdf.fonttype": 42, "savefig.facecolor": "white"})
    blue, orange, gray = "#185c8d", "#bc5a15", "#9ca6ae"
    colors = ("#175b8a", "#b05a17", "#477d48")
    pdf = output / "complete_intervention_catalogue122.pdf"
    layouts = []
    with PdfPages(pdf, metadata={"Title": "NBO R122 complete intervention catalogue",
            "Author": "Qian QI", "CreationDate": None, "ModDate": None}) as pages:
        for index in range(2):
            for service in SERVICES:
                data = [r for r in plotted if r["index"] == index and r["service"] == service]
                fig, axes = plt.subplots(1, 3, figsize=(11.7, 8.3), sharey=True,
                    gridspec_kw={"width_ratios": [1.16, 1, 1.05]})
                fig.subplots_adjust(left=.22, right=.98, top=.86, bottom=.15, wspace=.22)
                risk = "1/2" if index == 0 else "3/4"
                fig.suptitle(f"Original-policy intervention: risk {risk}, {service}",
                    x=.03, ha="left", y=.97, fontsize=15, fontweight="bold")
                fig.text(.03, .925,
                    "Complete fixed catalogue: 29 actors on this page; 116 contrasts across all four pages. "
                    "Row order follows the frozen design.", fontsize=8)
                labels = []
                for y, r in enumerate(data):
                    name = "online" if r["arm"] == "online" else \
                           f"b{r['budget']}  {r['arm']} / {r['loss']}"
                    labels.append(f"{name}  [{r['changed_actions']}/32]")
                    raw = [float(F(r[k])) * 1e6 for k in
                           ("raw_independent_sample_gain_lower", "raw_independent_sample_gain_upper")]
                    safe = [float(F(r[k])) * 1e6 for k in ("sample_gain_lower", "sample_gain_upper")]
                    pop = [float(F(r[k])) * 1e6 for k in ("population_gain_lower", "population_gain_upper")]
                    axes[0].plot(raw, [y, y], color=gray, linewidth=2.4, zorder=1)
                    axes[0].plot(safe, [y, y], color=blue, linewidth=1.2, zorder=2)
                    axes[0].plot(float(F(r["mean_certified_gain_lower"])) * 1e6, y,
                                 marker="o", markersize=3, color=orange, zorder=3)
                    axes[1].plot(pop, [y, y], color=blue, linewidth=1.2)
                    axes[1].plot(pop[0], y, marker="|", markersize=4, color=blue)
                    for j, observation in enumerate(r["clocks"]):
                        value = float(F(observation["added_full_allocated_seconds_per_decision"])) * 1000
                        axes[2].plot(value, y + (j - 1) * .15, marker=("o", "s", "^")[j],
                                     markersize=3.3, color=colors[j], linestyle="none")
                for axis in axes:
                    axis.axvline(0, color="#555555", linewidth=.7, zorder=0)
                    axis.grid(axis="x", color="#e4e7ea", linewidth=.55)
                    axis.set_ylim(len(data) - .4, -.6)
                    axis.ticklabel_format(axis="x", style="plain", useOffset=False)
                axes[0].set_yticks(range(len(data)), labels=labels)
                axes[0].set_title("Observed 32-state mean gain", fontsize=9)
                axes[0].set_xlabel("Original cost units x 10^-6")
                axes[1].set_title("Joint conditional 95% mean interval", fontsize=9)
                axes[1].set_xlabel("Original cost units x 10^-6")
                axes[2].set_title("Added complete work, first 16 states", fontsize=9)
                axes[2].set_xlabel("Milliseconds per decision")
                handles = [Line2D([0], [0], color=gray, linewidth=2.4, label="Raw independent interval"),
                    Line2D([0], [0], color=blue, linewidth=1.2, label="Proof-supported intersection"),
                    Line2D([0], [0], marker="o", color=orange, linewidth=0,
                           label="Mean certified gain lower bound")]
                fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(.02, .077), ncol=3,
                           frameon=False, fontsize=7.4)
                fig.legend(handles=[Line2D([0], [0], marker=("o", "s", "^")[j],
                    color=colors[j], linewidth=0, label=f"Clock {j}") for j in range(3)],
                    loc="upper right", bbox_to_anchor=(.98, .915), frameon=False, ncol=3, fontsize=7)
                fig.text(.03, .056,
                    "Gain is against the same actor's completed control; [k/32] is the changed-action count. "
                    "All gain columns use 32 independent initial states.", fontsize=7.2)
                fig.text(.03, .038,
                    "Clocks are descriptive repeated measurements on the fixed first 16 states. Full acquisition "
                    "and shared costs are retained; common costs cancel only in this paired difference.", fontsize=7.2)
                fig.text(.03, .020,
                    "Intervals and timing differences are separate displays. They do not constitute a "
                    "price-adjusted population adoption test or a neural-specific advantage claim.", fontsize=7.2)
                fig.canvas.draw()
                layouts.append({"index": index, "service": service,
                    "xlimits": [list(a.get_xlim()) for a in axes],
                    "xticks": [list(a.get_xticks()) for a in axes]})
                pages.savefig(fig)
                fig.savefig(output / f"catalogue_risk{index}_{service}122.png", dpi=140)
                plt.close(fig)

    (output / "PLOTTED_COMPLETE_DATA122.json").write_text(json.dumps(plotted, indent=2) + "\n")
    (output / "PANELS_LAYOUT122.json").write_text(json.dumps(layouts, indent=2) + "\n")
    receipt = {"kind": "complete saved-evidence publication figures",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_freeze_commit": F_COMMIT, "source_report": str(source),
        "input_files": bound_inputs, "builder_sha256": sha(__file__),
        "all_intervention_contrasts": 116, "all_timing_contrast_points": 348,
        "figures": 4, "fixed_order": "risk, service, online then budget, arm, loss",
        "outcome_based_selection": False, "original_economic_queries": 0,
        "new_population_observations": 0, "new_clock_executions": 0,
        "gain_population_units": 32, "timing_population_units": 16,
        "scope": "Separate descriptive mean-gain and paired-work panels; no new price-domain or population computation.",
        "seconds": time.perf_counter() - tick,
        "matplotlib_version": matplotlib.__version__,
        "output_files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)}
                         for p in sorted(output.iterdir()) if p.is_file()]}
    (output / "FIGURES_RECEIPT122.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"output": str(output), "receipt_sha256": sha(output / "FIGURES_RECEIPT122.json"),
                      "contrasts": 116, "timing_points": 348, "economic_queries": 0}))


if __name__ == "__main__":
    main()
