"""Render every frozen observation result without selecting a favorable cell."""
from pathlib import Path
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def endpoint(value, upper=False):
    """Print an outward bound on the exact stored binary64 value."""
    rounding = ROUND_CEILING if upper else ROUND_FLOOR
    return format(Decimal.from_float(float(value)).quantize(Decimal('0.000001'), rounding=rounding), '.6f')


def main():
    source = R/'results/observation/FINAL_AUDIT.json'
    audit = json.loads(source.read_text())
    if not audit['complete'] or audit['cells_completed'] != 4 or audit['deterministic_sensor_transfers'] != 12:
        raise ValueError('observation evidence is incomplete')
    main_rows, all_rows, work_rows = [], [], []
    for r in audit['rows']:
        d, n = r['cell']['dimension'], r['cell']['cells']
        lower = r['parent_bound']['lower']
        vals = [lower] + [x['continuous_gain_interval'][0] for x in r['sensor_intervals']]
        main_rows.append(f'{d} & {n} & ' + ' & '.join(endpoint(v) for v in vals) + r' \\')
        for s in r['sensor_intervals']:
            nu = s['sensor_noise_rms']
            lo, hi = s['continuous_gain_interval']
            allowance = s['payoff_difference_upper']
            all_rows.append(f'{d} & {n} & {nu:.4f} & {endpoint(allowance, upper=True)} & {endpoint(lo)} & {endpoint(hi, upper=True)} & {allowance/lower:.3f}' + r' \\')
        work_rows.append(f'{d} & {n} & {r["end_to_end_seconds"]:.3f} & {r["peak_process_rss_kib"]/1024:.1f} & {r["state_transitions"]:,}' + r' \\')
    outputs = {}
    def save(name, text):
        path = R/'manuscript'/name
        path.write_text(text)
        outputs[str(path.relative_to(ROOT))] = digest(path)
    save('table_observation_main.tex', r'''\begin{table}[!htbp]
\centering
\caption{Continuous-Economy Gain Bounds With Finite Observations}
\label{tab:r15observation}
\footnotesize
\begin{tabular}{rrrrrr}
\toprule
$d$ & $N$ & Parent lower & $\nu=0$ & $\nu=0.0001$ & $\nu=0.001$ \\
\midrule
'''+'\n'.join(main_rows)+r'''
\bottomrule
\end{tabular}
\begin{minipage}{0.96\linewidth}\footnotesize
\emph{Notes:} All lower endpoints are printed downward to six decimal places.
The last three columns are lower bounds for the finite-observation
controller's payoff gain over the analytical schedule. Each parent is freshly
verified at the same decision grid as its sensor transfer, using 8,192 independent
paths. The four parent intervals share error probability 0.01; the transfers are
deterministic. The fixed weights and original volatility calibration are retained
from the reviewed study. A negative endpoint means that this error account does
not certify improvement at that observation precision.
\end{minipage}
\end{table}
''')
    save('table_observation_full.tex', r'''\begin{table}[!htbp]
\centering
\caption{Complete Finite-Observation Payoff Transfers}
\label{tab:r15observationfull}
\footnotesize
\begin{tabular}{rrrrrrr}
\toprule
$d$ & $N$ & $\nu$ & Allowance & Lower & Upper & Allowance/parent lower \\
\midrule
'''+'\n'.join(all_rows)+r'''
\bottomrule
\end{tabular}
\begin{minipage}{0.98\linewidth}\footnotesize
\emph{Notes:} Every declared dimension, grid, and observation precision appears.
Lower endpoints are printed downward; upper endpoints and allowances are printed
upward to six decimal places. Ratios are descriptive rounded values.
The allowance is subtracted from the parent lower endpoint and added to its upper
endpoint with outward arithmetic. The final column compares implementation error
with the positive parent guarantee; a ratio above one removes that guarantee.
The candidate's physical state remains the original unbounded diffusion. Its
measurements arrive only at the $N$ decision dates and have normalized root mean
square error at most $\nu$.
\end{minipage}
\end{table}
''')
    save('table_observation_work.tex', r'''\begin{table}[!htbp]
\centering
\caption{Measured Work for Protected-Parent Verification and Sensor Transfers}
\label{tab:r15observationwork}
\footnotesize
\begin{tabular}{rrrrr}
\toprule
$d$ & $N$ & Complete seconds & Peak MiB & State transitions \\
\midrule
'''+'\n'.join(work_rows)+r'''
\bottomrule
\end{tabular}
\begin{minipage}{0.95\linewidth}\footnotesize
\emph{Notes:} Each row is a fresh CPU process. Its elapsed time includes imports,
weight loading, interval constants, protected simulation, all three sensor
allowances, raw-file writes, and the final result record. Environment provisioning
is reported separately. No policy is refitted in this experiment.
\end{minipage}
\end{table}
''')
    save('observation_evidence.tex', r'''\subsection{Implementation from finite state measurements}
\label{sec:r15observation}
The implementation question has a direct economic interpretation. A manager
observes a vector of log capital stocks at specified dates, computes consumption
rates with the saved network, and holds those rates until the next observation.
The manager's input consists of the measured physical state. The finite-observation
controller does not require a Brownian coordinate or the intervening drift integral.
Proposition~\ref{prop:r14sensor} applies to this controller through a protected
parent with the same saved weights and inward action guard.

The experiment verifies that parent afresh at 1,024 and 4,096 decision dates in
dimensions 10 and 50. It retains the original volatility calibration and the
previously fixed iteration-80 NBO weights; no outcome in the new observation
experiment selects a policy. Table~\ref{tab:r15observation} subtracts each
deterministic sensing allowance from the corresponding parent guarantee.
All four parents have positive lower endpoints. Six of the twelve
finite-observation lower endpoints remain positive. With 4,096 dates and exact
measurements, the continuous-economy gain is at least 0.001050 in dimension 10
and 0.001054 in dimension 50. In dimension 10, a measurement error of 0.0001
retains a lower gain of 0.000889 at the finer grid.

The dependence on measurement precision is economically material. At dimension
50, an error of 0.0001 already exceeds the available parent margin under the
current global network bound, and an error of 0.001 removes a positive guarantee
in both dimensions. These endpoints give an implementation requirement for the
specific measured-state rule. They do not infer the sign of its actual gain when
the allowance is too large. The full intervals, allowance-to-gain ratios, and
fresh-process costs appear in Tables~\ref{tab:r15observationfull}
and~\ref{tab:r15observationwork}.
\input{revisions/2026-10-04-r15/manuscript/table_observation_main.tex}
''')
    save('observation_supplement.tex', r'''\subsection{Complete protected-parent and finite-observation results}
\label{app:r15observation}
The source package fixes the two saved policies, the four parent grids, the
population, all observation precisions, and the confidence allocation before
simulation. Each cell uses an independent process with pinned numerical
dependencies. The archive retains all raw paired payoffs, final states,
per-cell transfer recurrences, and the source and output digests.
\input{revisions/2026-10-04-r15/manuscript/table_observation_full.tex}
\input{revisions/2026-10-04-r15/manuscript/table_observation_work.tex}
''')
    report = dict(record_type='R15 observation publication table manifest',
        numerical_source_commit=audit['numerical_source_commit'],
        reporting_script_sha256=digest(Path(__file__)),
        printing_rule='Exact stored binary64 endpoints: decimal floor for lower bounds and decimal ceiling for upper bounds and allowances at six decimal places; descriptive means, ratios and work do not change any inference.',
        inputs={str(source.relative_to(ROOT)): digest(source)}, outputs=outputs,
        parent_rows=4, transferred_rows=12,
        positive_parent_lower=4,
        positive_sensor_lower=sum(x['continuous_gain_interval'][0]>0 for r in audit['rows'] for x in r['sensor_intervals']))
    (R/'OBSERVATION_TABLE_MANIFEST.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['parent_rows','transferred_rows','positive_sensor_lower']}))


if __name__ == '__main__':
    main()
