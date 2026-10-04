"""Render all prespecified R15 Bellman-bridge evidence and numerical accounts.

No result is selected, refitted, resampled, or used to alter a policy. The
producer's protected interval samples are pooled over the complete fixed stream
population. TeX bounds are rounded outward; point estimates are descriptive.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
import hashlib
import json
from pathlib import Path

from costate_bridge import STATISTICS, I, iu, pc, pool, sha, write


def number(value, digits=6, side=None, scale=1):
    if value is None:
        return "---"
    with localcontext() as context:
        context.prec = 60
        x = Decimal.from_float(float(value))*Decimal(scale)
        if side is not None:
            rounding = ROUND_FLOOR if side == "lower" else ROUND_CEILING
            x = x.quantize(Decimal(10)**-digits, rounding=rounding)
        return f"{x:.{digits}f}"


def table(caption, label, columns, headings, rows, notes):
    return ("\\begin{table}[!htbp]\n\\centering\n\\footnotesize\n"
        +"\\caption{"+caption+"}\\label{"+label+"}\n"
        +"\\begin{tabular}{"+columns+"}\n\\toprule\n"
        +headings+r" \\"+"\n\\midrule\n"+"\n".join(rows)
        +"\n\\bottomrule\n\\end{tabular}\n"
        +"\\begin{minipage}{0.97\\linewidth}\\footnotesize\n\\emph{Notes:} "
        +notes+"\n\\end{minipage}\n\\end{table}\n")


def render(protocol_path, results, out):
    protocol_path, results, out = Path(protocol_path), Path(results), Path(out)
    protocol = json.loads(protocol_path.read_text())
    protocol["file_sha256"] = sha(protocol_path)
    records, work = [], {}
    for path in sorted(results.rglob("BRIDGE.json")):
        row = json.loads(path.read_text())
        row["record_path"] = str(path.resolve())
        records.append(row)
        work_path = path.parent/"WORK.json"
        if not work_path.exists():
            raise ValueError("complete fresh-process work record is required")
        worker = json.loads(work_path.read_text())
        if not worker.get("complete") or worker.get("returncode") != 0:
            raise ValueError("failed assessment work record")
        work[row["trial_id"]] = worker
    if len(records) != len(protocol["dimensions"])*len(protocol["declared_seeds"]):
        raise ValueError("the complete registered mechanism population is required")
    pooled = pool(records, protocol)
    for d in protocol["dimensions"]:
        rows = [r for r in records if r["dimension"] == d]
        workers = [work[r["trial_id"]] for r in rows]
        q = pooled["dimensions"][str(d)]
        q["work"] = dict(complete_process_seconds=sum(w["end_to_end_seconds"] for w in workers),
            user_cpu_seconds=sum(w["user_cpu_seconds"] for w in workers),
            system_cpu_seconds=sum(w["system_cpu_seconds"] for w in workers),
            peak_rss_kib=max(w["peak_rss_kib"] for w in workers),
            candidate_transitions=sum(r["counters"].get("candidate_simulator_transitions", 0) for r in rows),
            reference_transitions=sum(r["counters"].get("reference_simulator_transitions", 0) for r in rows),
            padded_reference_transition_rows=sum(r["counters"].get("reference_padded_transition_rows", 0) for r in rows),
            scope="additional independent scientific assessment; all fresh-process imports, constants, queries, adjoints and I/O included")
    out.mkdir(parents=True, exist_ok=True)
    write(out/"MECHANISM_SUMMARY.json", pooled)

    evaluation_rows, welfare_rows, full_rows, work_rows = [], [], [], []
    evaluation_statements, welfare_statements = [], []
    names = dict(M=r"$M$", A=r"$A$", E=r"$E$", D=r"$D$",
                 E_raw=r"$E^{\rm raw}$", E_minus_raw=r"$E-E^{\rm raw}$")
    for d in protocol["dimensions"]:
        row = pooled["dimensions"][str(d)]
        intervals = row["intervals"]
        contrast = intervals["E_minus_raw"]
        evaluation_rows.append(" & ".join([str(d),
            number(intervals["E"]["raw_descriptive_mean"], 3, scale=10000),
            number(intervals["E_raw"]["raw_descriptive_mean"], 3, scale=10000),
            number(contrast["lower"], 3, "lower", 10000),
            number(contrast["upper"], 3, "upper", 10000)])+r" \\")
        # Print the actual subtracted Cauchy term, not a training MSE.
        risk_charge = iu(pc.sqrt_nonnegative(I(row["U_A"])*I(row["U_E"]))) if row["U_A"]*row["U_E"] else 0.
        welfare_rows.append(" & ".join([str(d),number(row["L_M"],side="lower"),
            number(risk_charge,side="upper"),number(row["U_D"],side="upper"),
            number(iu(I(row["holding_deficit_upper"])+I(row["paired_payoff_transfer_upper"])),side="upper"),
            number(row["continuous_gain_lower"],side="lower")])+r" \\")
        for key in STATISTICS:
            ci = intervals[key]
            full_rows.append(" & ".join([str(d),names[key],
                number(ci["raw_descriptive_mean"], 7), number(ci["lower"], 7, "lower"),
                number(ci["upper"], 7, "upper"),number(ci["range_upper"], 5, "upper"),
                number(ci["sample_moment_arithmetic_cushion"], 8, "upper")])+r" \\")
        w = row["work"]
        work_rows.append(" & ".join([str(d),number(w["complete_process_seconds"],2),
            number(w["user_cpu_seconds"]+w["system_cpu_seconds"],2),
            number(w["peak_rss_kib"]/1024,1),f'{w["reference_transitions"]:,}',
            f'{w["padded_reference_transition_rows"]:,}'])+r" \\")
        if contrast["upper"] < 0:
            evaluation_statements.append(f"In dimension {d}, the upper endpoint for the critic-minus-raw costate-risk difference is "
                +number(contrast["upper"],7,"upper")+", establishing lower risk for the reusable critic on these assessment queries.")
        elif contrast["lower"] > 0:
            evaluation_statements.append(f"In dimension {d}, the lower endpoint for the critic-minus-raw costate-risk difference is "
                +number(contrast["lower"],7,"lower")+", establishing higher risk for the critic on these assessment queries.")
        else:
            evaluation_statements.append(f"In dimension {d}, the costate-risk contrast has endpoints "
                +number(contrast["lower"],7,"lower")+" and "+number(contrast["upper"],7,"upper")
                +"; this interval does not determine which predictor has smaller risk.")
        if row["continuous_gain_lower"] > 0:
            welfare_statements.append(f"The combined Bellman-bridge account certifies a continuous-economy gain of at least "
                +number(row["continuous_gain_lower"],6,"lower")+f" in dimension {d}.")
        else:
            welfare_statements.append(f"The combined Bellman-bridge lower endpoint in dimension {d} is "
                +number(row["continuous_gain_lower"],6,"lower")
                +". The retained costate, sampling, and implementation allowances do not establish improvement through this sufficient bound.")

    outputs = {}
    def save(name, text):
        path = out/name
        path.write_text(text)
        outputs[name] = sha(path)

    save("table_mechanism_evaluation.tex", table(
        "Costate Prediction on the Candidate's Occupation Law", "tab:r15mechanismevaluation",
        "rrrrr", r"$d$ & Critic risk mean & Raw risk mean & Contrast lower & Contrast upper",
        evaluation_rows,
        r"All displayed risk entries are multiplied by $10^4$. Each dimension pools 256 independent action bridges from every one of the 16 registered NBO streams, or 4,096 bridges. Each bridge has two independent four-path antithetic continuation banks on the 2,048-cell global grid. The signed critic statistic removes reference Monte Carlo variance in expectation. The raw statistic is the risk of one four-path bank on the identical represented queries. The paired contrast estimates critic risk minus raw risk. Its endpoints use the registered family of 12 two-sided statements with total error probability 0.01 and include interval sample arithmetic and proved clipping tails. These are evaluation-subproblem comparisons; the returned Raw policy's welfare is assessed separately."))
    save("table_mechanism_welfare.tex", table(
        "From the Continuation Account to Economic Gain", "tab:r15mechanismwelfare",
        "rrrrrr", r"$d$ & $L_M$ & $\sqrt{U_AU_E}$ & $U_D$ & Holding/transfer & Gain lower",
        welfare_rows,
        r"The costate upper bound includes the exact-state representation allowance. The holding and transfer column sums the outward holding deficit and the quantitative paired payoff transfer to the original continuous economy. The last column is the larger of the product bound and the optional quadratic actor-gap bound when its positive modulus is verified. A negative endpoint records the limit of this sufficient mechanism account. Actual method welfare remains assessed by the independent direct payoff experiment; the mechanism assessment cannot change selection or stopping."))
    save("table_mechanism_full.tex", table(
        "Complete Protected Bellman-Bridge Statistics", "tab:r15mechanismfull",
        "rlrrrrr", r"$d$ & Statistic & Raw mean & Lower & Upper & Clip bound & Arithmetic",
        full_rows,
        r"Every registered statistic and dimension appears. These intervals concern the exact represented-query sample expectations before the additional state-representation conversion used in the welfare bound. The arithmetic column is the outward sample-mean and sample-standard-deviation perturbation allowance, not an empirical population range. The source records each stream's scalar weights, verified network norms, curvature, clipping tail and state/adjoint error constants. There is no per-stream inferential claim."))
    save("table_mechanism_work.tex", table(
        "Complete Work for the Independent Mechanism Assessment", "tab:r15mechanismwork",
        "rrrrrr", r"$d$ & Process seconds & CPU seconds & Peak MiB & Future updates & Padded rows",
        work_rows,
        r"Process and CPU seconds sum all 16 fresh stream processes in each dimension; peak memory is their maximum. The assessment includes loading the already selected policy, rebuilding constants, candidate occupation paths, both continuation banks, reverse derivatives, interval arithmetic and output. Future updates count mathematically active continuation transitions; padded rows additionally disclose vectorized inactive arithmetic. This work is reported in addition to the primary algorithms' complete stopping and independent payoff-assessment costs."))
    save("mechanism_evidence.tex", r'''\subsection{Continuation accuracy where the policy changes the allocation}
\label{sec:r15mechanismevidence}
The mechanism assessment follows the policy that each registered NBO stream
actually returns. It draws fresh occupation paths and uniform action bridges
after all policy selection. The reference remains the cell-average analytical
schedule on one global assessment grid. The saved scalar critic may have been
fitted on a coarser grid; its assessment error includes this discrepancy.

Table~\ref{tab:r15mechanismevaluation} compares the fitted costate with a direct
four-path antithetic bank on the identical continuation queries. The calculation
uses independent cross-products to remove reference-bank variance from the
critic's risk estimand. It also reports the paired difference in risk, retaining
negative sample contributions and all registered streams.
'''+"\n\n".join(evaluation_statements)+r'''

Table~\ref{tab:r15mechanismwelfare} carries the same continuation account
through the feasible actor's actual action change and the quantitative
continuous-payoff transfer of Theorem~\ref{thm:r15mechanism}. The approximate
continuation's scalar advantage is evaluated at both action endpoints. The
actor's gap is bounded from the saved global curvature certificate, including
the endpoint calculation when strong concavity is unavailable.
'''+"\n\n".join(welfare_statements)+r'''

The complete six-statistic intervals and numerical cushions appear in
Table~\ref{tab:r15mechanismfull}. Table~\ref{tab:r15mechanismwork} reports the
additional fresh-process assessment work. These calculations distinguish
accuracy of the evaluation stage, quality of the feasible action update,
and the independent payoff comparison between complete algorithms.
''')
    manifest = dict(schema="nbo-r15-mechanism-report-v1", complete=True,
        protocol_sha256=sha(protocol_path), trial_count=len(records),
        streams_per_dimension=len(protocol["declared_seeds"]),
        numerical_source_commit=records[0]["numerical_source_commit"],
        candidate_source_commit=records[0]["candidate_source_commit"],
        assessment_fingerprint=records[0]["assessment_fingerprint"],
        input_raw_hashes={r["trial_id"]:r["raw_sha256"] for r in records},
        summary_sha256=sha(out/"MECHANISM_SUMMARY.json"), tex_files=outputs,
        report_source_sha256=sha(__file__),
        numerical_interpretation="all signs and inconclusive endpoints rendered mechanically; no filtering or policy reselection")
    write(out/"REPORT_MANIFEST.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = render(args.protocol, args.results, args.out)
    print(json.dumps({"complete":result["complete"],"trials":result["trial_count"]}), flush=True)
