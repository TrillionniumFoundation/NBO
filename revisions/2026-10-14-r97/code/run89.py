"""Prospective shared query proposals. Certificates remain in the unchanged oracle.
Run fit, calibrate, then evaluate; replay requires saved models and workload bytes.
No numerical or training exception is silently removed from the catalogue.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, os, platform, resource, subprocess, sys, time, warnings
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parents[1]
REVS = R.parent
for rel in ('2026-10-07-r45/code', '2026-10-08-r48/code', '2026-10-10-r67/code'):
    sys.path.insert(0, str(REVS / rel))
import kernel66 as kernel
ARMS = ('adaptive', 'bisection', 'analytic', 'relu', 'polynomial')
OUT = R / 'results89'
SEEDS = {'fit': 202610138901, 'calibration': 202610138902, 'evaluation': 202610138903}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False, default=lambda x: x.tolist() if isinstance(x,np.ndarray) else x.item() if isinstance(x,np.generic) else (_ for _ in ()).throw(TypeError(type(x).__name__))) + '\n')

def load(path):
    return json.loads(Path(path).read_text())

def metadata():
    return {'machine': platform.machine(), 'platform': platform.platform(),
            'python': sys.version, 'numpy': np.__version__,
            'source_sha256': sha(__file__), 'protocol_sha256': sha(R / 'PROTOCOL89.md')}

def features(x):
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or x.shape[1] not in (2, 4, 8) or not np.isfinite(x).all():
        raise ValueError('Finite original state in a declared dimension required')
    n, d = x.shape
    padded = np.zeros((n, 8)); padded[:, :d] = x
    return np.column_stack((padded, x.mean(1), x[:, ::2].mean(1), x[:, 1::2].mean(1),
                            (x*x).mean(1), (x*np.roll(x, -1, axis=1)).mean(1), np.full(n, d/8)))

def polynomial(z):
    return np.column_stack([np.ones(len(z)), z] +
                          [z[:, i]*z[:, j] for i, j in itertools.combinations_with_replacement(range(14), 2)])

def stream(name, dimensions, n):
    rng = np.random.Generator(np.random.PCG64(SEEDS[name]))
    return {str(d): rng.random((n, d)).tolist() for d in dimensions}

class SharedOracle(kernel.Oracle):
    def __init__(self, arm, models):
        kind = {'analytic': 'derivative', 'polynomial': 'quadratic'}.get(arm, arm)
        super().__init__(kind=kind, record=True)
        self.arm, self.payload = arm, models
        self.counts.update(invalid_predictions=0, feasibility_repairs=0, model_rows=0)

    def propose(self, x, r, cap):
        if self.arm not in ('relu', 'polynomial'):
            return super().propose(x, r, cap)
        start = time.perf_counter(); n = len(x)
        self.counts['learned_proposals'] += n; self.counts['model_rows'] += n
        model = self.payload[self.arm]
        if model['valid']:
            z = features(x)
            if self.arm == 'relu':
                a, b, u, c = model['coefficients']
                ratio = np.maximum(0, z @ np.asarray(a) + np.asarray(b)) @ np.asarray(u) + c
            else:
                ratio = polynomial(z) @ np.asarray(model['coefficients'])
            value = ratio * cap
        else:
            value = np.full(n, np.nan)
        invalid = ~np.isfinite(value)
        self.counts['invalid_predictions'] += int(invalid.sum())
        self.counts['feasibility_repairs'] += int(((value < 0) | (value > cap)).sum())
        value = np.where(invalid, cap/2, value)
        answer = kernel.q.clamp(value, cap)
        self.counts['prediction_seconds'] += time.perf_counter() - start
        return answer

def model_work(arm, calls, d):
    # Algebraic dense evaluation account, not CPU instructions or interval work.
    core = {'relu': (481, 480, 32), 'polynomial': (226, 119, 0)}.get(arm, (0, 0, 0))
    return {'multiplications': calls * (core[0] + 2*d),
            'additions': calls * (core[1] + 4*d - 5), 'divisions': calls * 5,
            'relu_gates': calls * core[2], 'feature_and_dense_account': True}

def run_rows(arm, states, models, tolerance=1/64):
    records = []
    for i, state in enumerate(states):
        oracle = SharedOracle(arm, models)
        try:
            x = np.asarray([state]); result = oracle.solve(x, 2, tolerance)
            counts = {k: v for k, v in oracle.counts.items() if k != 'prediction_seconds'}
            counts['nonterminal_queries'] = counts['q_queries'] - counts['terminal_queries']
            if counts['nonterminal_queries'] < 0:
                raise AssertionError('Terminal queries are a subset of all queries')
            action = float(result['action'][0]); gap = float(result['gap'][0])
            if not (0 <= action <= float(kernel.q.cap_point(x)[0]) and 0 <= gap <= tolerance):
                raise AssertionError('Feasibility or original-law bracket failed')
            progress = np.concatenate(oracle.progress, axis=0) if oracle.progress else np.empty((0,13))
            zero_progress = sum(float(row[8]) <= 0 and float(row[9]) <= 0 for row in progress)
            records.append({'row': i, 'status': 'passed', 'action': action, 'gap': gap,
                            'lower': float(result['lower'][0]), 'upper': float(result['upper'][0]),
                            'counts': counts, 'model_work': model_work(arm, counts['model_rows'], len(state)),
                            'zero_progress_probes': zero_progress,
                            'screens': oracle.screens, 'progress': oracle.progress})
        except Exception as exc:
            records.append({'row': i, 'status': 'failed', 'exception': type(exc).__name__ + ': ' + str(exc),
                            'counts': oracle.counts, 'screens': oracle.screens, 'progress': oracle.progress})
    return records

def fit():
    if (OUT / 'FIT89.json').exists():
        raise FileExistsError('Refitting a frozen experiment requires a separately named revision')
    OUT.mkdir(exist_ok=True)
    states = stream('fit', (2, 8), 128); z, labels, label_records = [], [], {}
    for d, values in states.items():
        x = np.asarray(values); oracle = kernel.Oracle('adaptive', record=True)
        result = oracle.solve(x, 2, 1/256)
        labels.extend((result['action']/kernel.q.cap_point(x)).tolist()); z.extend(features(x).tolist())
        label_records[d] = {'actions': result['action'].tolist(), 'gaps': result['gap'].tolist(),
                            'counts': oracle.counts}
    z = np.asarray(z); labels = np.asarray(labels); models = {}; diagnostics = []
    for arm in ('relu', 'polynomial'):
        start = time.perf_counter(); caught = []
        try:
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter('always')
                if arm == 'relu':
                    import sklearn
                    from sklearn.neural_network import MLPRegressor
                    m = MLPRegressor(hidden_layer_sizes=(32,), activation='relu', solver='lbfgs',
                                     alpha=1e-5, max_iter=1000, max_fun=15000, tol=1e-8, random_state=89)
                    m.fit(z, labels)
                    coefficients = [m.coefs_[0].tolist(), m.intercepts_[0].tolist(),
                                    m.coefs_[1].ravel().tolist(), float(m.intercepts_[1][0])]
                    extra = {'sklearn': sklearn.__version__, 'iterations': int(m.n_iter_)}
                else:
                    design = polynomial(z); reg = np.eye(design.shape[1])*1e-6; reg[0, 0] = 0
                    coefficients = np.linalg.solve(design.T @ design + reg, design.T @ labels).tolist()
                    extra = {'features': int(design.shape[1])}
                caught = [str(w.message) for w in ws]
            # JSON finiteness is part of model admissibility, not a fitting guarantee.
            json.dumps(coefficients, allow_nan=False)
            models[arm] = {'valid': True, 'coefficients': coefficients}
            diagnostics.append({'arm': arm, 'status': 'returned', 'warnings': caught,
                                'seconds': time.perf_counter()-start, **extra})
        except Exception as exc:
            models[arm] = {'valid': False, 'coefficients': None}
            diagnostics.append({'arm': arm, 'status': 'failed', 'warnings': caught,
                                'exception': type(exc).__name__ + ': ' + str(exc)})
    save(OUT/'TRAIN89.json', {'states': states, 'labels': labels.tolist(), 'oracle': label_records})
    save(OUT/'MODELS89.json', models)
    save(OUT/'FIT89.json', {'metadata': metadata(), 'fit_attempts': 2, 'training_rows': 256,
                           'diagnostics': diagnostics, 'models_sha256': sha(OUT/'MODELS89.json'),
                           'training_sha256': sha(OUT/'TRAIN89.json'),
                           'calibration_generated': False, 'evaluation_generated': False})

def check_models():
    frozen = load(OUT/'FIT89.json')
    if sha(OUT/'MODELS89.json') != frozen['models_sha256']:
        raise AssertionError('Frozen model bytes changed')
    return load(OUT/'MODELS89.json')

def calibrate():
    models = check_models()
    if (OUT/'SELECTOR89.json').exists():
        raise FileExistsError('Calibration selector already frozen')
    states = stream('calibration', (2, 8), 64)
    records = {a: {d: run_rows(a, xs, models) for d, xs in states.items()} for a in ARMS}
    scores = {}
    for arm, groups in records.items():
        rows = [row for group in groups.values() for row in group]
        scores[arm] = sum(row['counts']['q_queries'] for row in rows) if all(row['status']=='passed' for row in rows) else None
    usable = [a for a in ARMS if scores[a] is not None]
    if not usable:
        save(OUT/'CALIBRATION89.json', {'states': states, 'records': records}); raise RuntimeError('No valid service')
    selected = min(usable, key=lambda a: (scores[a], ARMS.index(a)))
    save(OUT/'CALIBRATION89.json', {'states': states, 'records': records})
    save(OUT/'SELECTOR89.json', {'selected': selected, 'total_q_queries': scores,
                                'models_sha256': sha(OUT/'MODELS89.json'),
                                'calibration_sha256': sha(OUT/'CALIBRATION89.json'), 'evaluation_generated': False})

def evaluate(machine, replay=False):
    check_models(); selector = load(OUT/'SELECTOR89.json')
    if selector['calibration_sha256'] != sha(OUT/'CALIBRATION89.json'):
        raise AssertionError('Calibration changed after selection')
    path = OUT/'EVALUATION_INPUTS89.json'
    if not replay:
        if path.exists(): raise FileExistsError('Holdout already generated')
        save(path, {'states': stream('evaluation', (2, 4, 8), 128),
                    'models_sha256': sha(OUT/'MODELS89.json'), 'selector_sha256': sha(OUT/'SELECTOR89.json')})
    inputs = load(path)
    if inputs['models_sha256'] != sha(OUT/'MODELS89.json') or inputs['selector_sha256'] != sha(OUT/'SELECTOR89.json'):
        raise AssertionError('Holdout freeze mismatch')
    folder = OUT/machine; folder.mkdir(exist_ok=True); runs = []
    for repetition in range(3):
        for d in (2, 4, 8):
            order = ARMS[repetition:] + ARMS[:repetition]
            for arm in order:
                output = folder/f'{arm}-d{d}-r{repetition}.json'; start = time.perf_counter()
                result = subprocess.run([sys.executable, __file__, 'worker', '--arm', arm, '--dimension', str(d), '--output', str(output)],
                                        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
                elapsed = time.perf_counter()-start
                output.with_suffix('.log').write_text(result.stdout)
                runs.append({'arm': arm, 'dimension': d, 'repetition': repetition, 'returncode': result.returncode,
                             'complete_process_seconds': elapsed, 'output': str(output.relative_to(OUT)),
                             'output_sha256': sha(output) if output.exists() else None})
    save(folder/'RUNS89.json', {'metadata': metadata(), 'runs': runs, 'independent_evaluation_rows': 384,
                               'new_independent_rows_for_machine_replay': 0 if replay else 384,
                               'model_payload_bytes': (OUT/'MODELS89.json').stat().st_size,
                               'input_sha256': sha(path), 'selector': selector})
    if any(run['returncode'] for run in runs):
        raise RuntimeError('At least one complete service process failed; all records retained')

def worker(arm, dimension, output):
    start = time.perf_counter(); models = check_models()
    states = load(OUT/'EVALUATION_INPUTS89.json')['states'][str(dimension)]
    records = run_rows(arm, states, models)
    save(output, {'arm': arm, 'dimension': dimension, 'records': records,
                  'worker_seconds': time.perf_counter()-start,
                  'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    if any(row['status'] != 'passed' for row in records):
        raise RuntimeError('An individual workload failed; saved, not discarded')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=('fit','calibrate','evaluate','replay','worker'))
    parser.add_argument('--machine', default=platform.machine()); parser.add_argument('--arm', choices=ARMS)
    parser.add_argument('--dimension', type=int); parser.add_argument('--output')
    args = parser.parse_args()
    if args.phase == 'fit': fit()
    elif args.phase == 'calibrate': calibrate()
    elif args.phase in ('evaluate','replay'): evaluate(args.machine, args.phase=='replay')
    else: worker(args.arm, args.dimension, args.output)
