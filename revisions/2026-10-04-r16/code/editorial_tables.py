"""Render author presentation tables from the complete immutable menu report.

This descriptive work table adds no scientific event, observation or fitted
candidate. It preserves the source reporter's distinction between a complete
shared confirmation bundle and a standalone method's verification expense.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

R = Path('revisions/2026-10-04-r16')
REPORT = R / 'results/continuation_menu/report/REPORT.json'
TABLE = R / 'manuscript/menu_shared_work.tex'
FROZEN_COMPARISON = R / 'results/continuation_menu/report/table_menu_comparisons.tex'
COMPARISON = R / 'manuscript/menu_comparisons.tex'
RECEIPT = R / 'results/receipts/MENU_SHARED_WORK_TABLE.json'
CALIBRATIONS = {'original_low': 'Original', 'quarterly_reuse': 'Quarterly',
                'long_reuse': 'Long', 'untouched_intermediate': 'Intermediate'}
METHODS = {'nbo_scalar', 'vector_costate', 'raw_actor', 'dpo_actor', 'raw_saa'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render(repo):
    report = json.loads((repo / REPORT).read_text())
    config = json.loads((repo / R / 'PUBLICATION_SOURCES.json').read_text())
    require(report.get('complete') is True and report['trial_count'] == 128 and
            report['method_fits'] == 640 and report['stage_candidates'] == 1920,
            'shared work table requires the complete menu family')
    require(report['numerical_source_commit'] == config['roles']['continuation_menu']['source_commit'],
            'menu report belongs to another source')
    expected_cells = {cal + '_d' + str(d) for cal in CALIBRATIONS for d in (10, 50)}
    require(set(report['work']) == expected_cells, 'complete work table must contain all eight cells')
    rows, records = [], []
    for cal, label in CALIBRATIONS.items():
        for d in (10, 50):
            cell = cal + '_d' + str(d)
            work = report['work'][cell]
            require(set(work) == {'1', '2', '3'}, 'a work stage is missing')
            reference = work['3']['nbo_scalar']
            clocks = [x['complete_shared_confirmation_process_seconds']
                      for x in reference['complete_stream_records']]
            mean = reference['mean_complete_shared_confirmation_seconds']
            require(len(clocks) == 16 and all(math.isfinite(x) and x > 0 for x in clocks),
                    'complete positive clocks for all sixteen streams are required')
            require(math.isclose(mean, math.fsum(clocks) / 16, rel_tol=1e-14),
                    'reported mean differs from its full clock population')
            for stage in work.values():
                require(set(stage) == METHODS, 'a method is missing from shared work')
                for item in stage.values():
                    require(item['mean_complete_shared_confirmation_seconds'] == mean and
                            [x['complete_shared_confirmation_process_seconds']
                             for x in item['complete_stream_records']] == clocks,
                            'shared confirmation was allocated inconsistently across methods or stages')
            low, high = min(clocks), max(clocks)
            rows.append(f'{label} & {d} & {mean:.2f} & {low:.2f} & {high:.2f}' + r'\\')
            records.append(dict(calibration=cal, dimension=d, streams=16,
                                mean_seconds=mean, minimum_seconds=low, maximum_seconds=high))
    text = ('% Complete menu REPORT SHA256: ' + sha(repo / REPORT) + '\n' + r'''\begin{table}[!htbp]
\centering\small
\caption{Complete Shared Confirmation Work}
\label{tab:r16menusharedwork}
\begin{tabular}{llrrr}
\toprule
Economy & $d$ & Mean seconds & Minimum seconds & Maximum seconds\\
\midrule
''' + '\n'.join(rows) + r'''
\bottomrule
\end{tabular}
\par\medskip\noindent\footnotesize\raggedright Each observation is the actual
complete confirmation-process clock for one of the sixteen declared streams.
The shared bundle evaluates five methods, all three work stages, the common
reference, and the scalar accuracy exercise. Its mean is an additional bill
to the construction and query clocks in Table~\ref{tab:r16menuwork}. Charging
that complete bill to an individual method gives a conservative allocation;
it does not measure a separate method-specific verification job. All eight
economic-dimension cells and every stream are retained. These are descriptive
timings for the executed runs, without a runtime-distribution confidence claim.
\end{table}
''')
    frozen_comparison = (repo / FROZEN_COMPARISON).read_text()
    old_note = 'The mean column is the clipped residual estimator plus this known offset.'
    new_note = 'The point estimator underlying each interval is the clipped residual estimator plus this known offset.'
    require(frozen_comparison.count(old_note) == 1 and new_note not in frozen_comparison,
            'the single documented comparison-table wording correction changed')
    comparison = frozen_comparison.replace(old_note, new_note)
    require(comparison.replace(new_note, old_note) == frozen_comparison,
            'comparison presentation must preserve every other source character')
    receipt = dict(schema='nbo-r16-author-shared-work-table-v1', complete=True,
        report=str(REPORT), report_sha256=sha(repo / REPORT),
        numerical_source_commit=report['numerical_source_commit'],
        generator_sha256=sha(__file__), table=str(TABLE),
        table_sha256=hashlib.sha256(text.encode()).hexdigest(),
        comparison_presentation=dict(frozen_source=str(FROZEN_COMPARISON),
            frozen_source_sha256=sha(repo / FROZEN_COMPARISON), table=str(COMPARISON),
            table_sha256=hashlib.sha256(comparison.encode()).hexdigest(),
            exact_old_phrase=old_note, exact_new_phrase=new_note,
            all_other_source_characters_preserved=True, numerical_cells_changed=0),
        cells=records, confidence_events_added=0, new_observations=0,
        scope='All 128 recorded complete shared confirmation clocks; no one-fifth allocation or standalone method experiment.')
    return {TABLE: text, COMPARISON: comparison,
            RECEIPT: json.dumps(receipt, indent=2, sort_keys=True) + '\n'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--write', action='store_true', help='Create the reviewable table and receipt before D.')
    args = parser.parse_args()
    repo = args.repo.resolve()
    for relative, content in render(repo).items():
        path = repo / relative
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        else:
            require(path.is_file() and path.read_bytes() == content.encode(),
                    'author shared-work source differs from the complete frozen report: ' + str(relative))
    print(json.dumps(dict(complete=True, table=str(TABLE), cells=8, recorded_clocks=128,
                         mode='write' if args.write else 'byte_exact_check')))


if __name__ == '__main__':
    main()
