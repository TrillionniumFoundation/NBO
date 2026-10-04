#!/usr/bin/env python3
"""Describe all saved R16 HJB diagnostics; verify authored outputs by default.

This publication helper reads three immutable JSON inputs. It does not import
scientific modules, read checkpoints or simulation arrays, train, select a new
policy, draw a bank, or construct a confidence interval. --write regenerates
only the authored TeX table and its descriptive provenance receipt.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path

R = Path('revisions/2026-10-04-r16')
ROOT = Path(__file__).resolve().parents[3]
SOURCE = '21d4cc505202686382b5b45d5f710ffdc12f889c'
EVIDENCE = '0b0b113b8c249d916daf0da22808180ce15caa2f'
REPORT = R / 'results/robustness/report/REPORT.json'
PROTOCOL = R / 'protocols/robustness.json'
DESIGN = R / 'protocols/strong_hjb_design.json'
SCRIPT = R / 'code/editorial_hjb_diagnostics.py'
TABLE = R / 'manuscript/robustness_diagnostics_tables.tex'
RECEIPT = R / 'results/receipts/HJB_EDITORIAL_DIAGNOSTICS.json'
INPUT_SHA256 = {
    str(REPORT): '2b675db41f2827d987c3ceae3e3ee01627a0e80228e0b9f54f85d2922d7e17fd',
    str(PROTOCOL): '623d79c63c567530c4dcde053a1ccd959e4907662e7fd8ec14dc98b3beefa6c3',
    str(DESIGN): '813a36aefec56bbfedbc4bc72ebd0e0035f7371bcf4f931bf3444c43b35f8b41',
}
CONFIG_LABEL = {
    'occupation_lr0015': 'O15', 'occupation_lr0005': 'O05',
    'mixture_lr0015': 'M15', 'mixture_lr0005': 'M05',
}
PROBE_KINDS = ('gaussian_covariance', 'rademacher_idiosyncratic_exact_common')
PROBE_LABEL = dict(zip(PROBE_KINDS, ('Gaussian', 'Rademacher')))
CHECKPOINTS = ['initial', *['adam_' + str(n) for n in range(200, 1201, 200)], 'lbfgs_final']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def number(value):
    require(isinstance(value, (int, float)) and not isinstance(value, bool) and
            math.isfinite(value), 'a descriptive diagnostic is not finite')
    return float(value)


def summary(values):
    values = [number(x) for x in values]
    require(len(values) == 8, 'every descriptive row must retain all eight declared streams')
    return dict(n=len(values), mean=math.fsum(values) / len(values), minimum=min(values), maximum=max(values))


def extrema(records):
    require(records, 'empty descriptive extrema')
    return dict(minimum=min(records, key=lambda x: x['value']),
                maximum=max(records, key=lambda x: x['value']))


def collect(repo):
    inputs = {}
    for path, expected in INPUT_SHA256.items():
        data = (repo / path).read_bytes()
        require(sha(data) == expected, 'immutable editorial input changed: ' + path)
        inputs[path] = json.loads(data)
    report, protocol, design = (inputs[str(p)] for p in (REPORT, PROTOCOL, DESIGN))
    require(report['complete'] is True and report['numerical_source_commit'] == SOURCE and
            report['trials'] == 64 and report['fresh_group_processes'] == 256 and
            report['policy_outputs'] == 320 and report['confidence_event_count_verified'] == 648,
            'the complete generating robustness family is required')
    require(report['favorable_sign_required'] is False, 'the saved report must retain every result')
    calibrations = [x['id'] for x in protocol['calibrations']]
    dimensions, seeds = protocol['dimensions'], protocol['seeds']
    cells = list(itertools.product(calibrations, dimensions))
    require(calibrations == ['high', 'low', 'long', 'stress'] and dimensions == [10, 50] and
            len(seeds) == len(set(seeds)) == 8, 'economic cells or stream population changed')
    configuration = design['implementation_configuration']
    variants = configuration['candidates']
    require([v['id'] for v in variants] == list(CONFIG_LABEL), 'all four fixed configurations are required')
    rows = report['hjb_diagnostics']
    by_trial = {(x['calibration_id'], x['dimension'], x['stream_seed']): x for x in rows}
    expected = set(itertools.product(calibrations, dimensions, seeds))
    require(len(rows) == len(by_trial) == 64 and set(by_trial) == expected, 'missing or repeated HJB trial')
    family_hashes, choices, changes, probe_rows = {}, {}, {}, {}
    selection_extrema, audit_extrema, value_extrema, policy_extrema, variance_extrema, trace_extrema = [], [], [], [], [], []
    checkpoint_count = 0
    for key in itertools.product(calibrations, dimensions, seeds):
        trial = by_trial[key]
        calibration, dimension, seed = key
        identity = dict(calibration_id=calibration, dimension=dimension, stream_seed=seed)
        require(trial['fallback'] is False and trial['operation_counters_complete'] is True,
                'failed or incomplete HJB family must not be silently omitted')
        candidates = trial['candidates']
        require(len(candidates) == 4 and [c['variant'] for c in candidates] == variants,
                'a fixed HJB candidate is missing or changed')
        for candidate in candidates:
            require(candidate['failure'] is None and candidate['payoff_used_for_selection'] is False,
                    'candidate failure or payoff selection cannot be omitted')
            require(number(candidate['seconds']) > 0, 'candidate fit time is missing')
            history = candidate['history']
            require([x['checkpoint'] for x in history] == CHECKPOINTS, 'the complete saved checkpoint history changed')
            checkpoint_count += len(history)
            selected = min(history, key=lambda x: x['residual_rms'])
            require(candidate['selected_checkpoint'] == selected['checkpoint'] and
                    candidate['selected_residual_rms'] == selected['residual_rms'],
                    'candidate choice does not reproduce the saved residual-only rule')
            require(all(x['terminal_value_error'] == 0 for x in history), 'hard terminal-lift diagnostic changed')
            selection_extrema.append(dict(**identity, configuration=candidate['variant']['id'],
                                          value=number(candidate['selected_residual_rms'])))
        winner = min(candidates, key=lambda x: x['selected_residual_rms'])
        require(winner['variant']['id'] == trial['selected_variant'] and
                winner['selected_residual_rms'] == trial['selection_residual_rms'],
                'family choice does not reproduce the fixed residual-only rule')
        choices[key] = winner
        history = winner['history']
        index = next(i for i, x in enumerate(history) if x['checkpoint'] == winner['selected_checkpoint'])
        require(index > 0, 'an initial checkpoint has no successive-iterate change')
        checkpoint = history[index]
        require(checkpoint['change_scope'] ==
                'successive iterates on the selection bank; not value or policy error against an optimum',
                'iterate-change meaning changed')
        change = dict(value_change_rms=number(checkpoint['value_change_rms']),
                      policy_change_rms=number(checkpoint['policy_change_rms']),
                      selected_checkpoint=checkpoint['checkpoint'], previous_checkpoint=history[index-1]['checkpoint'])
        require(change['value_change_rms'] >= 0 and change['policy_change_rms'] >= 0, 'invalid iterate RMS change')
        changes[key] = change
        value_extrema.append(dict(**identity, value=change['value_change_rms']))
        policy_extrema.append(dict(**identity, value=change['policy_change_rms']))
        diagnostic = trial['independent_diagnostics']
        require(diagnostic['used_for_selection'] is False and set(diagnostic['groups']) == {'occupation', 'broad'},
                'the untouched audit must retain both state populations')
        for kind, group in diagnostic['groups'].items():
            residual = group['residual']
            require(residual['rows'] == configuration['audit_rows_per_group'] == 1024,
                    'independent state-bank size changed')
            require(sum(x['count'] for x in residual['time_strata']) == 1024, 'incomplete time-stratum diagnostics')
            audit_extrema.append(dict(**identity, state_bank=kind, value=number(residual['residual_rms'])))
        probe = trial['probe_diagnostics']
        require(probe['used_for_checkpoint_selection'] is False and
                number(probe['analytic_vs_autograd_max_error']) <= 5e-11, 'probe or exact-trace audit changed')
        trace_extrema.append(dict(**identity, value=number(probe['analytic_vs_autograd_max_error'])))
        ps = {(x['kind'], x['probes_per_bank']): x for x in probe['rows']}
        require(len(ps) == len(probe['rows']) == 6 and
                set(ps) == set(itertools.product(PROBE_KINDS, configuration['probe_counts'])) and
                configuration['probe_counts'] == [2, 8, 32], 'a probe kind or count is missing')
        for (kind, count), entry in ps.items():
            require(entry['independent_banks'] == configuration['probe_diagnostic_banks'] == 64 and
                    entry['state_rows'] == configuration['probe_diagnostic_rows'] == 64,
                    'probe diagnostic bank size changed')
            variance = number(entry['average_conditional_variance'])
            require(variance >= 0, 'invalid recorded sample variance')
            variance_extrema.append(dict(**identity, probe_kind=kind, probes_per_bank=count, value=variance))
        probe_rows[key] = ps
        family_hashes[f'{calibration}_d{dimension}_s{seed}'] = trial['family_sha256']
    configs, audits, probes = [], [], []
    for calibration, dimension in cells:
        keys = [(calibration, dimension, s) for s in seeds]
        for position, variant in enumerate(variants):
            candidates = [by_trial[key]['candidates'][position] for key in keys]
            configs.append(dict(calibration_id=calibration, dimension=dimension, configuration=variant,
                selection_residual_rms=summary(c['selected_residual_rms'] for c in candidates),
                selected_count=sum(choices[key]['variant']['id'] == variant['id'] for key in keys),
                residual_early_stop_count=sum(c['stopped_by_independent_residual'] for c in candidates),
                fit_seconds=summary(c['seconds'] for c in candidates)))
        groups = [by_trial[key]['independent_diagnostics']['groups'] for key in keys]
        audits.append(dict(calibration_id=calibration, dimension=dimension,
            occupation_residual_rms=summary(x['occupation']['residual']['residual_rms'] for x in groups),
            broad_residual_rms=summary(x['broad']['residual']['residual_rms'] for x in groups),
            occupation_sampled_residual_maximum=summary(x['occupation']['residual']['residual_sample_max'] for x in groups),
            broad_sampled_residual_maximum=summary(x['broad']['residual']['residual_sample_max'] for x in groups),
            selected_value_iterate_change_rms=summary(changes[key]['value_change_rms'] for key in keys),
            selected_policy_iterate_change_rms=summary(changes[key]['policy_change_rms'] for key in keys),
            checkpoint_pairs=dict(Counter(changes[key]['previous_checkpoint'] + ' -> ' +
                                          changes[key]['selected_checkpoint'] for key in keys))))
        for kind, count in itertools.product(PROBE_KINDS, configuration['probe_counts']):
            probes.append(dict(calibration_id=calibration, dimension=dimension, probe_kind=kind, probes_per_bank=count,
                average_conditional_variance=summary(probe_rows[key][kind, count]['average_conditional_variance'] for key in keys)))
    require((len(configs), len(audits), len(probes)) == (32, 8, 48), 'descriptive table row population changed')
    require(sum(x['selected_count'] for x in configs) == 64 and checkpoint_count == 2048,
            'candidate selection or saved-checkpoint population incomplete')
    return dict(complete=True, numerical_source_commit=SOURCE, evidence_commit=EVIDENCE, original_github_run_id=37203261818,
        input_sha256=INPUT_SHA256, streams_per_row=8, declared_streams=seeds,
        validation=dict(economic_cells=8, complete_hjb_families=64, candidate_fits=256, retained_checkpoints=2048,
            candidate_failures=0, family_fallbacks=0, incomplete_operation_counters=0,
            payoff_used_for_selection=False, untouched_audit_used_for_selection=False, probe_used_for_selection=False,
            selected_checkpoint_rule_reconstructed=True, selected_configuration_rule_reconstructed=True,
            configuration_rows=32, independent_audit_rows=8, probe_summary_rows=48,
            recorded_probe_rows=384, state_rows_per_residual_bank=1024, state_rows_per_probe_bank=64,
            independent_probe_banks=64, new_training_runs=0, new_confirmation_draws=0, new_probability_events=0),
        definitions=dict(configuration_selection_residual='Each candidate\'s best retained selection-bank exact residual RMS; average and range over the eight declared streams.',
            chosen='Frequency of the recorded residual-only family winner among the eight streams; all four configurations remain reported.',
            fit_seconds='The recorded per-candidate fit timer. This is a component of the full shared HJB construction, not standalone deployment work.',
            independent_residual='Exact residual RMS on each selected critic\'s untouched occupation or broad audit bank; range across eight streams.',
            iterate_change='Saved RMS change from the preceding logged checkpoint to the selected checkpoint on the selection bank. These are successive-iterate diagnostics, not errors relative to an unknown optimum.',
            probe_variance='The recorded quantity is the unhalved covariance-Hessian trace, before the generator factor one half. For each saved trial, the unbiased variance across 64 trace-probe banks is averaged over 64 fixed broad-audit states. The table gives the mean and range of these eight recorded trial statistics. Probe counts 2, 8, 32 use nested prefixes within a bank. Gaussian covariance and idiosyncratic Rademacher with exact common-shock contraction are both retained.',
            scope='Post-execution descriptive tabulation of immutable diagnostics only. Ranges are observed minima and maxima, not confidence intervals or uniform error certificates. All fit and checkpoint records remain in the generating frozen JSON.'),
        configuration_summary=configs, independent_audit_summary=audits, probe_variance_summary=probes,
        extrema=dict(candidate_selection_residual_rms=extrema(selection_extrema),
            independent_residual_rms=extrema(audit_extrema), selected_value_iterate_change_rms=extrema(value_extrema),
            selected_policy_iterate_change_rms=extrema(policy_extrema), probe_conditional_variance=extrema(variance_extrema),
            analytic_trace_vs_autodiff_max_error=extrema(trace_extrema)),
        selected_configuration_totals={v['id']: sum(x['selected_variant'] == v['id'] for x in rows) for v in variants},
        residual_early_stops=sum(x['residual_early_stop_count'] for x in configs), family_record_sha256=family_hashes)


def fixed(value):
    return f'{number(value):.6f}'


def observed_range(row, scientific=False):
    fmt = (lambda x: f'{number(x):.3e}') if scientific else fixed
    return '[' + fmt(row['minimum']) + ', ' + fmt(row['maximum']) + ']'


def longtable(caption, label, columns, headings, rows, note, size='small'):
    lines = ['\\begingroup\\' + size, '\\setlength{\\tabcolsep}{3pt}',
        '\\begin{longtable}{' + columns + '}', '\\caption{' + caption + '}\\label{' + label + '}\\\\',
        '\\toprule', ' & '.join(headings) + r' \\', '\\midrule', '\\endfirsthead',
        '\\toprule', ' & '.join(headings) + r' \\', '\\midrule', '\\endhead']
    lines += [' & '.join(map(str, row)) + r' \\' for row in rows]
    lines += ['\\bottomrule', '\\end{longtable}',
              '\\par\\medskip\\noindent\\footnotesize ' + note, '\\endgroup', '']
    return '\n'.join(lines)


def render(record):
    text = '% Authored descriptive tables; all generating scientific records remain unchanged.\n'
    text += '% Frozen REPORT SHA256: ' + INPUT_SHA256[str(REPORT)] + '\n'
    text += longtable('All prespecified HJB candidate configurations', 'tab:r16hjbconfigurations', 'lrlrlrrr',
        ['Design', '$d$', 'Config.', 'Mean RMS', 'RMS range', 'Chosen', 'Stop', 'Fit sec.'],
        [[x['calibration_id'], x['dimension'], CONFIG_LABEL[x['configuration']['id']],
          fixed(x['selection_residual_rms']['mean']), observed_range(x['selection_residual_rms']),
          str(x['selected_count']) + '/8', str(x['residual_early_stop_count']) + '/8', f"{x['fit_seconds']['mean']:.2f}"]
         for x in record['configuration_summary']],
        r'Each row retains all eight declared streams. O15 and O05 use occupation training collocation with learning rates $0.0015$ and $0.0005$; M15 and M05 use equal occupation and broad training collocation at the same two rates. '
        r'Selection always gives equal weight to the separate occupation and broad selection banks. Mean RMS and its observed range use the best retained checkpoint of each candidate. '
        r'Chosen counts residual-only family winners; Stop counts residual-only early stopping. Fit seconds are per-candidate components, already included in the complete shared HJB work in Table~\ref{tab:r16-robustness-work}. '
        r'All 256 candidate fits and 2048 saved checkpoints are retained; no candidate failed and no final payoff selected a checkpoint or configuration.')
    text += longtable('Untouched HJB residual audits and selected-checkpoint iterate changes', 'tab:r16hjbaudit', 'lrllll',
        ['Design', '$d$', 'Occupation RMS', 'Broad RMS', r'$\Delta V$ RMS', r'$\Delta u$ RMS'],
        [[x['calibration_id'], x['dimension'], observed_range(x['occupation_residual_rms']),
          observed_range(x['broad_residual_rms']), observed_range(x['selected_value_iterate_change_rms']),
          observed_range(x['selected_policy_iterate_change_rms'])] for x in record['independent_audit_summary']],
        r'Each entry is the observed minimum and maximum over all eight streams in that economic cell. Residuals use the selected critic on untouched audit banks of 1024 occupation and 1024 broad states; these audit outcomes did not select a candidate. '
        r'The $\Delta V$ and $\Delta u$ columns use the saved selection-bank RMS changes from Adam step 1200 to the selected final L-BFGS checkpoint, which was selected in all 64 trials. '
        r'They measure differences between successive saved iterates. They do not measure error against the unknown optimal value or policy. Ranges are descriptive, not confidence intervals or uniform residual bounds.', size='footnotesize')
    text += longtable('Finite-bank trace-probe variance for both retained estimators', 'tab:r16hjbprobes', 'lrlrrl',
        ['Design', '$d$', 'Probe law', 'Probes', 'Mean variance', 'Variance range'],
        [[x['calibration_id'], x['dimension'], PROBE_LABEL[x['probe_kind']], x['probes_per_bank'],
          f"{x['average_conditional_variance']['mean']:.3e}", observed_range(x['average_conditional_variance'], scientific=True)]
         for x in record['probe_variance_summary']],
        r'Each row retains all eight streams. Within each saved trial, the unbiased variance across 64 independent probe banks is averaged over 64 fixed broad-audit states; the table then reports the mean and observed range across the eight trial statistics. '
        r'The traced quantity is $\operatorname{tr}(\Sigma\Sigma^\top D_x^2V)$, before the generator factor $1/2$. Gaussian uses covariance-distributed directions. Rademacher uses idiosyncratic directions and evaluates the common-shock contraction exactly. Probe counts 2, 8 and 32 use nested prefixes within each bank. '
        r'The fitted HJB models use exact diffusion contractions; neither these probe outcomes nor the untouched audit selected a checkpoint. The numbers describe the frozen finite banks and introduce no additional probability event.', size='footnotesize')
    return text.encode()


def execute(repo, write=False):
    repo = Path(repo).resolve()
    record = collect(repo)
    table = render(record)
    record.update(schema='nbo-r16-authored-hjb-diagnostics-v1',
        editorial_script_sha256=sha((repo / SCRIPT).read_bytes()),
        authored_table=dict(path=str(TABLE), bytes=len(table), sha256=sha(table)))
    receipt = encoded(record)
    for relative, expected in ((TABLE, table), (RECEIPT, receipt)):
        path = repo / relative
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected)
        else:
            require(path.is_file() and path.read_bytes() == expected,
                    'authored HJB diagnostic output is not byte exact: ' + str(relative))
    return dict(complete=True, mode='write' if write else 'verify', report_sha256=INPUT_SHA256[str(REPORT)],
        table_sha256=sha(table), receipt_sha256=sha(receipt), configuration_rows=32,
        independent_audit_rows=8, probe_rows=48, candidate_failures=0,
        new_training_runs=0, new_confirmation_draws=0, new_probability_events=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--write', action='store_true', help='write only the authored table and receipt; default verifies both')
    arguments = parser.parse_args()
    print(json.dumps(execute(arguments.repo, arguments.write), indent=2, allow_nan=False))
