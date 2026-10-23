"""Create new standalone follow-up TeX and a reporting-cost completion ledger."""
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    tick = time.perf_counter()
    out = ROOT / 'results125/followup-presentation'
    inputs = {}
    outputs = {}
    for stem, tex in [('MAIN_FOLLOWUP_FRAGMENT125.txt', 'followup_audit_main125.tex'),
                      ('DEVELOPMENT_FOLLOWUP_FRAGMENT125.txt', 'followup_audit_development125.tex')]:
        source = out / stem
        target = ROOT / 'new125' / tex
        inputs[str(source.relative_to(ROOT))] = sha(source)
        with target.open('x') as f:
            f.write(source.read_text())
        outputs[str(target.relative_to(ROOT))] = sha(target)
    comparison_path = ROOT / 'results125/ADOPTION_BLOCKER_COMPARABILITY125.json'
    comparison = json.loads(comparison_path.read_text())
    inputs[str(comparison_path.relative_to(ROOT))] = sha(comparison_path)
    assert comparison['witnesses'] == 128
    assert comparison['selected_blocker_roles'] == {'online': 64, 'poly2': 64}
    assert comparison['matching_counts']['same_acquired_training_label_digest'] == 32
    text = r'''\subsection{Comparator roles in the post-execution policy-identity diagnostic}
\label{dev:identitycomparators125}
The original adoption calculation retains 128 nonempty optimistic outer
regions, each with a zero lower price endpoint and a strictly positive
finite upper endpoint. Its 128 sufficient regions are empty. These
classifications are unchanged. The separate identity diagnostic uses
the same actual complete policy at $(1/4,1/4)$ to cancel the true economic
value difference before comparing charged acquisition and service costs.
For every one of the 128 neural-service/amortization cases, a conventional
service has an upper complete cost strictly below the neural service's
lower complete cost under the recorded timing ranges. This excludes
strictly positive computation prices conditionally on those ranges;
at zero price the pair ties. It does not establish optimality against
the different-policy uniform-DP comparator.

The selected blockers are online controls in 64 cases and degree-two
polynomial controls in 64 cases. The following counts describe those
already selected witnesses; no blocker was changed for this diagnostic.
\begin{center}\small
\begin{tabular}{lr}
\hline
Property of selected blocker relative to neural service & Cases \\
\hline
Same acquired training-label digest & 32 \\
Different acquired training-label digest & 32 \\
Direct online route without a fitted training-label bundle & 64 \\
Same acquisition-budget label & 32 \\
Same fitting-loss label & 32 \\
Same budget and fitting-loss labels & 16 \\
Same service mode & 32 \\
Same feature dictionary & 0 \\
\hline
\end{tabular}
\end{center}
The inherited acquisition constructs a complete value-and-marginal label
bundle once per risk and budget, then supplies it to every representation
and both fitting losses. Thus fitting-loss equality is distinct from
acquired-training-information equality. The comparison checks the stored
label digest references in the frozen models and the immutable acquisition
code; it does not independently re-hash the unmaterialized historical
label streams. It also does not equate all subsequently acquired
decision-service oracle information. The polynomial blockers have four
declared features and the ReLU services have 39, while the online control
has no fitted feature dictionary. None of these selected blockers is
the matched hinge control. The budget label is lower in 88 cases, equal
in 32 and higher in eight. All acquisition charges and actual service
times remain in the comparison.

This is complete-service cost competition conditional on exact equality
of the implemented original policy at the first workload. It is not an
equal-feature representation comparison, an equal-resource complexity
separation, or a claim about other states or neural architectures.
The original outer regions and the separately derived identity exclusion
are both retained. The source-bound witnesses are in
\texttt{ADOPTION\_SUPPORT\_DIAGNOSTIC125.json}; comparator metadata are
in \texttt{ADOPTION\_BLOCKER\_COMPARABILITY125.json}.
'''
    target = ROOT / 'new125/identity_adoption_diagnostic125.tex'
    with target.open('x') as f:
        f.write(text)
    outputs[str(target.relative_to(ROOT))] = sha(target)
    reconciliation_path = out / 'RECONCILIATION125.json'
    reconciliation = json.loads(reconciliation_path.read_text())
    inputs[str(reconciliation_path.relative_to(ROOT))] = sha(reconciliation_path)
    rows = list(reconciliation['additional_measured_reporting_costs'])
    for relative in ('results125/followup-presentation/EXECUTION125.json',
                     'results125/followup-presentation/TEXT_RENDER125.json',
                     'results125/ADOPTION_BLOCKER_COMPARABILITY125.json'):
        path = ROOT / relative
        receipt = json.loads(path.read_text())
        rows.append(dict(path=relative, sha256=sha(path),
                         seconds=receipt['seconds'], economic_evaluations=0))
    assert len({r['path'] for r in rows}) == len(rows)
    for row in rows:
        assert sha(ROOT / row['path']) == row['sha256']
    failure_rows = []
    for relative in ('reporting125/PRESENTATION_ATTEMPT02_FAILURE.json',
                     'results125/reporting_failures/BALANCED_WEIGHTING_ATTEMPT01_FAILURE.json',
                     'results125/reporting_failures/UNRESOLVED_METADATA_QUERY125.json'):
        path = ROOT / relative
        receipt = json.loads(path.read_text())
        failure_rows.append(dict(path=relative, sha256=sha(path), receipt=receipt))
    cohort_path = ROOT / 'results125/report/cohorts_summary125.jsonl'
    cohorts = [json.loads(line) for line in cohort_path.read_text().splitlines()]
    inherited = defaultdict(set)
    for cohort in cohorts:
        if cohort['budget']:
            inherited[tuple(cohort['cohort'][:4])].add(cohort['acquisition'])
    assert len(inherited) == 56 and all(len(values) == 1 for values in inherited.values())
    inherited_rows = [dict(model_identity=list(key), charged_historical_allocation=next(iter(values)))
                      for key, values in sorted(inherited.items())]
    inputs[str(cohort_path.relative_to(ROOT))] = sha(cohort_path)
    ledger = dict(
        status='executed', economic_evaluations=0, services_retimed=0,
        script_sha256=sha(Path(__file__)), input_sha256=inputs, output_sha256=outputs,
        scientific_phase_costs=reconciliation['scientific_phase_costs'],
        sum_listed_complete_numeric_parent_seconds=reconciliation['sum_complete_scientific_process_seconds'],
        numerical_subtotal_is_not_total_research_elapsed_time=True,
        recorded_reporting_costs=rows,
        sum_listed_successful_reporting_child_seconds=float(sum(Fraction(r['seconds']) for r in rows)),
        reporting_failures_preserved=failure_rows,
        inherited_model_acquisition_allocations=inherited_rows,
        inherited_acquisition_scope=(
            'The 56 stored model charges are inherited measured component allocations used '
            'for standalone service/adoption accounting, equal across the four current '
            'service modes for each model. They are not newly timed standalone acquisition '
            'runs. Their sum is not asserted to be historical joint process elapsed time, '
            'because common labels and hinge parent fitting charges can be shared in the '
            'historical execution while being fully charged to a standalone alternative.'),
        unmeasured_costs=reconciliation['unmeasured_costs'],
        interactive_metadata_queries_are_not_comprehensively_timed=True,
        this_integration_child_seconds=time.perf_counter()-tick,
    )
    with (out / 'COMPLETION125.json').open('x') as f:
        json.dump(ledger, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps(dict(status=ledger['status'], outputs=outputs,
                         scientific_parent_subtotal=ledger['sum_listed_complete_numeric_parent_seconds'],
                         reporting_child_subtotal=ledger['sum_listed_successful_reporting_child_seconds'],
                         integration_seconds=ledger['this_integration_child_seconds'],
                         economic_evaluations=0), sort_keys=True))


if __name__ == '__main__':
    main()
