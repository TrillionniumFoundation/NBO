"""Bind the complete sensing and scalar diagnostics into the reading copy."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]
M = R / 'manuscript'


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def table(name, title, label, cols, header, rows, note):
    s = '\\begingroup\\small\\setlength{\\tabcolsep}{4pt}\n'
    s += '\\begin{longtable}{' + cols + '}\n\\caption{' + title + '}\\label{' + label + '}\\\\\n'
    line = ' & '.join(header) + r'\\\midrule' + '\n'
    s += '\\toprule\n' + line + '\\endfirsthead\n\\toprule\n' + line + '\\endhead\n'
    s += '\n'.join(' & '.join(map(str, row)) + r'\\' for row in rows)
    s += '\n\\bottomrule\n\\end{longtable}\n\\noindent ' + note + '\n\\endgroup\n'
    (M / name).write_text(s)


def run():
    M.mkdir(exist_ok=True)
    sensing = R / 'results/sensing'
    index = json.loads((sensing / 'INDEX.json').read_text())
    if not index['complete'] or index['diagnostic_rows'] != 18:
        raise AssertionError('Incomplete sensing diagnostic')
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in sensing.iterdir() if p.is_file()}
    rows = []
    for p in sorted(sensing.glob('nbo_*.json')):
        record = json.loads(p.read_text())
        if digest(ROOT / record['raw_file']) != record['raw_sha256']:
            raise AssertionError('Sensing raw-array identity')
        if digest(ROOT / record['weights']) != record['weights_sha256']:
            raise AssertionError('Sensing checkpoint identity')
        inputs[record['weights']] = record['weights_sha256']
        rows.extend(record['rows'])
    found = {(r['dimension'], r['actor_cells'], r['sensor_noise_rms']) for r in rows}
    expected = {(d, n, nu) for d in (10, 20, 50) for n in (64, 128) for nu in (0., .001, .01)}
    if found != expected or len(rows) != 18:
        raise AssertionError('Sensing diagnostic cells differ from the declared family')
    rows.sort(key=lambda r: (r['dimension'], r['actor_cells'], r['sensor_noise_rms']))
    up6 = lambda x: f'{math.ceil(float(x)*1e6)/1e6:.6f}'
    table('table_sensing_summary.tex', 'Finite-observation implementation and transfer', 'tab:r14sensing',
          'rrrrr', ['$d$', 'Cells', '$\\nu_{\\rm obs}$', 'Euler difference', 'Transfer ub.'],
          [[r['dimension'], r['actor_cells'], f"{r['sensor_noise_rms']:g}",
            f"{r['fine_euler_mean_sensor_minus_parent']:.3e}", up6(r['allowance']['payoff_difference_upper'])]
           for r in rows],
          'The fourth column is a 128-path shared-noise fine-Euler mean; it has no continuous-time confidence interpretation. '
          'The last column is the separate outward continuous-diffusion transfer allowance, displayed upward. '
          'Every decision cell has eight fine diagnostic cells. No 1,024-cell parent certificate is assigned to these coarser parents.')
    table('table_sensing_accounts.tex', 'Components of the finite-observation allowance', 'tab:r14sensingaccounts',
          'rrrrrr', ['$d$', 'Cells', '$\\nu_{\\rm obs}$', 'Production', 'Consumption', 'Terminal'],
          [[r['dimension'], r['actor_cells'], f"{r['sensor_noise_rms']:g}",
            up6(r['allowance']['production_payoff_allowance']), up6(r['allowance']['consumption_deficit_allowance']),
            up6(r['allowance']['terminal_dispersion_allowance'])] for r in rows],
          'Each component is displayed upward. The machine-readable records give the full recurrence, network Lipschitz and roundoff bounds, '
          'initial-profile bounds, seeds, pathwise diagnostic arrays, and the separate Monte Carlo standard errors.')
    (M / 'sensing_supplement.tex').write_text(
        '\\section{Finite-Observation Diagnostic Accounts}\\label{app:r14sensingdiagnostics}\n'
        'The experiment fixes the same saved NBO checkpoint before drawing the diagnostic bank. '
        'The sensor uses finite state measurements and independent private noise; the parent uses a clipped-innovation internal state. '
        'The deterministic allowance and the finite-Euler measurement answer different questions. '
        'Neither the observed mean nor its simulation standard error supplies the fine-Euler bias.\n'
        '\\input{revisions/2026-10-04-r14/manuscript/table_sensing_accounts.tex}\n')
    reference = R / 'results/reference'
    rr = json.loads((reference / 'REFERENCE_DIAGNOSTICS.json').read_text())
    if not rr['all_original_arrays_reproduced'] or not rr['all_howard_steps_converged']:
        raise AssertionError('Scalar reference replay failed')
    (M / 'table_reference_diagnostics.tex').write_text(
        '\\input{revisions/2026-10-04-r14/results/reference/table_reference_diagnostics.tex}\n'
        '\\clearpage\n')
    (M / 'reference_supplement.tex').write_text(
        '\\section{Independent Scalar Reference: Equations and Complete Diagnostics}\\label{app:r14reference}\n'
        '\\input{revisions/2026-10-04-r14/results/reference/reference_scope.tex}\n'
        '\\input{revisions/2026-10-04-r14/results/reference/table_reference_losses.tex}\n'
        '\\input{revisions/2026-10-04-r14/results/reference/table_reference_refinement.tex}\n'
        '\\clearpage\n')
    for p in reference.iterdir():
        if p.is_file():
            inputs[str(p.relative_to(ROOT))] = digest(p)
    outputs = {str((M / name).relative_to(ROOT)): digest(M / name) for name in [
        'table_sensing_summary.tex', 'table_sensing_accounts.tex', 'sensing_supplement.tex',
        'table_reference_diagnostics.tex', 'reference_supplement.tex']}
    manifest = {'reporting_script_sha256': digest(__file__), 'inputs': inputs, 'outputs': outputs,
                'sensing_rows': 18, 'reference_grids': 4, 'new_statistical_endpoints': 0}
    (R / 'DIAGNOSTIC_TABLE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'sensing_rows': 18, 'reference_grids': 4, 'new_statistical_endpoints': 0}))


if __name__ == '__main__':
    run()
