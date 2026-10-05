"""Post-execution, all-candidate refinement audit of the frozen R23 services.

No refitting, tuning, seed selection, replacement primary clock, or revised
historical stopping decision is performed. Every original failed attempt
remains an original failed attempt even if the new sufficient bound resolves it.
"""
from pathlib import Path
import hashlib
import json
import os
import time
import numpy as np
from refinements import certify_refined, Ball, up, down, positive_sum, value_balls
from experiment import economy

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]
P = ROOT / 'revisions/2026-10-05-r23/results/primary'
OLD = P.parents[1]
O = R / 'results'


def rows(path):
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def basin_diagnostic(model, K, W):
    """Check a possible future inner-loop basin against returned own P.

    This is not a claim that the *past* R23 step sizes satisfy the R24 bound.
    Its old training targets and learning rate are not relabeled.
    """
    own, _ = value_balls(*[model[k] for k in
                          ('A', 'B', 'Q', 'R', 'Qf', 'Sigma', 'beta')], K)
    d, T = model['d'], model['horizon']
    records = []
    for t in range(1, T):
        target = own[t].scale(d)
        off = target.abs_upper().copy()
        np.fill_diagonal(off, 0)
        m = float(np.min(down(down(np.diag(target.c) - np.diag(target.r))
                              - positive_sum(off, axis=1))))
        L = target.norm_inf()
        w = Ball.exact(W[t])
        b = (w.T @ w - target).norm_f()
        records.append({'date': t, 'm_lower': m, 'L_upper': L,
                        'residual_upper': b,
                        'basin_verified': bool(m > 0 and b <= float(down(m / 2)))})
    return records


def run():
    O.mkdir(parents=True, exist_ok=True)
    tic = time.perf_counter()
    protocol = json.loads((OLD / 'protocols/PROTOCOL.json').read_text())
    freeze = json.loads((OLD / 'protocols/FREEZE.json').read_text())
    assert {p: hash_file(OLD / p) for p in freeze['files']} == freeze['files']
    ledgers = {str(p.relative_to(ROOT)): hash_file(p)
               for p in (P / 'attempts.jsonl', P / 'services.jsonl', P / 'SUMMARY.json')}
    attempts = rows(P / 'attempts.jsonl')
    services = rows(P / 'services.jsonl')
    assert len(attempts) == 1088 and len(services) == 480
    tol = protocol['policy_tolerance']
    records, basins = [], []
    for i, row in enumerate(attempts):
        path = P / row['candidate_file']
        assert hash_file(path) == row['candidate_sha256']
        with np.load(path, allow_pickle=False) as data:
            model = economy(row['dimension'], row['regime'], protocol['horizon'])
            for name in ('A', 'B', 'Q', 'R', 'Qf', 'Sigma'):
                assert np.array_equal(model[name], data[name]), (path.name, name)
                model[name] = data[name].copy()
            K = data['gains'].copy()
            refined = certify_refined(model, K, protocol['execution_error_budget'])
            recomputed = refined['original']['policy_gap_upper']
            old = row['certificate']['policy_gap_upper']
            assert abs(old - recomputed) <= 1e-10 * max(abs(old), abs(recomputed)) + 1e-12
            assert bool(recomputed <= tol) == bool(row['certified'])
            assert refined['policy_gap_upper'] <= recomputed
            rec = {k: row[k] for k in ('key', 'dimension', 'seed', 'method', 'regime')}
            rec.update(attempt_index=i, candidate_sha256=row['candidate_sha256'],
                       original_certified=bool(row['certified']),
                       refined_certified=bool(refined['policy_gap_upper'] <= tol),
                       original_gap_upper=old,
                       refined_gap_upper=refined['policy_gap_upper'],
                       original_eta=row['certificate']['eta'],
                       refined_eta=refined['energy_eta_upper'],
                       available_dates=refined['available_dates'],
                       dates=refined['date_records'])
            records.append(rec)
            if row['certified'] and row['method'].startswith('NBO'):
                dates = basin_diagnostic(model, K, data['critic_factor'].copy())
                basins.append({'key': row['key'], 'candidate_sha256': row['candidate_sha256'],
                               'dates': dates,
                               'all_dates_verified': all(x['basin_verified'] for x in dates)})
        if i % 100 == 0:
            print('R24 symmetric replay', i, '/', len(attempts), flush=True)
    assert all(hash_file(ROOT / p) == h for p, h in ledgers.items())
    cells = []
    for d in protocol['dimensions']:
        for method in protocol['methods']:
            subset = [r for r in records if (r['dimension'], r['method']) == (d, method)]
            ratios = [r['refined_gap_upper'] / r['original_gap_upper'] for r in subset
                      if r['original_gap_upper'] > 0]
            cells.append({'dimension': d, 'method': method, 'attempts': len(subset),
                          'original_successful_checks': sum(r['original_certified'] for r in subset),
                          'newly_resolved_original_failures': sum(not r['original_certified'] and
                                                                  r['refined_certified'] for r in subset),
                          'minimum_bound_ratio': min(ratios),
                          'maximum_bound_ratio': max(ratios)})
    report = {
        'analysis_source_commit': os.environ.get('GITHUB_SHA', 'not supplied'),
        'inherited_source_commit': 'c327e0f4f1d5c8c6381dfe0f2b6001fbd7bb7f96',
        'primary_ledger_hashes_unchanged': ledgers,
        'original_services': len(services), 'attempts_replayed': len(records),
        'candidate_hashes_verified': len(records),
        'original_successful_checks': sum(r['original_certified'] for r in records),
        'original_failed_checks': sum(not r['original_certified'] for r in records),
        'newly_resolved_original_failures': sum(not r['original_certified'] and r['refined_certified'] for r in records),
        'unavailable_energy_dates': sum(protocol['horizon'] - r['available_dates'] for r in records),
        'final_neural_basin_candidates': len(basins),
        'final_neural_all_date_basins_verified': sum(r['all_dates_verified'] for r in basins),
        'basin_dates': sum(len(r['dates']) for r in basins),
        'basin_dates_verified': sum(x['basin_verified'] for r in basins for x in r['dates']),
        'cells': cells, 'analysis_seconds': time.perf_counter() - tic,
        'scope': 'Deterministic post-execution certificate and basin analysis. '
                 'No new training trial, historical stop, first-success clock, '
                 'or population inference. The old R23 learning rate is unchanged.'}
    (O / 'REFINEMENT.json').write_text(json.dumps(report, indent=2) + '\n')
    (O / 'REFINEMENT_RECORDS.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in records))
    (O / 'BASIN_RECORDS.json').write_text(json.dumps(basins, indent=2) + '\n')
    lines = [r'\section{Symmetric Certificate Refinement}\label{sec:r24record}',
             'This deterministic analysis replays every stored candidate of the original full-policy experiment. '
             'No fit, original decision, or primary clock is replaced. The additional matrix solves and '
             'verification work belong to this separate analysis, not to the original service bill.',
             r'\begin{longtable}{rlrrr}',
             r'\caption{Refinement of all original attempted certificates}\label{tab:r24refinement}\\',
             r'\toprule $d$ & Procedure & Attempts & Original passes & Newly resolved\\\midrule\endfirsthead',
             r'\toprule $d$ & Procedure & Attempts & Original passes & Newly resolved\\\midrule\endhead']
    for c in cells:
        lines.append(f"{c['dimension']} & {c['method']} & {c['attempts']} & "
                     f"{c['original_successful_checks']} & {c['newly_resolved_original_failures']}" + r'\\')
    lines += [r'\bottomrule\end{longtable}',
              f"All {report['attempts_replayed']} candidate hashes and original stopping decisions are checked. "
              f"The {report['original_failed_checks']} original unsuccessful checks remain in the original record. "
              f"The refined sufficient bound resolves {report['newly_resolved_original_failures']} of those checks. "
              f"There are {report['unavailable_energy_dates']} unavailable date-level energy refinements. "
              'These counts do not establish how a prospectively modified algorithm would spend its work.',
              f"A separate own-policy calculation verifies the new sufficient rank basin at "
              f"{report['basin_dates_verified']} of {report['basin_dates']} final neural continuation dates, "
              f"and at every relevant date for {report['final_neural_all_date_basins_verified']} of "
              f"{report['final_neural_basin_candidates']} final neural candidates. "
              'This tests the availability of the finite-step theorem for a further update against the '
              'returned own-policy target. It does not relabel the historical target, step size, or training path.',
              r'The all-candidate records, interval diagnostics, original candidate digests, and primary-ledger '
              r'digests accompany the revision. A rank-basin check or a sharper policy certificate is '
              r'not evidence of neural cost superiority.']
    (O / 'refinement_record.tex').write_text('\n\n'.join(lines) + '\n')
    print(json.dumps(report, indent=2), flush=True)
    return report


if __name__ == '__main__':
    run()
