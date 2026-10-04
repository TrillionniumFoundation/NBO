"""Same-parent payoff certificates and finite-observation transfers for R15.

The protected parent is evaluated afresh at each declared grid. The sensor
controller receives only its measured physical state at the decision dates.
Its continuous-diffusion guarantee follows by the R14 deterministic transfer;
no fine-Euler sensor simulation is relabelled a continuous-time certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def run(d, cells, out=None):
    beginning = time.perf_counter()
    protocol_path = R / 'PROTECTED_OBSERVATION_PROTOCOL.json'
    protocol = json.loads(protocol_path.read_text())
    if d not in protocol['dimensions'] or cells not in protocol['actor_cells']:
        raise ValueError('cell is not in the frozen observation protocol')
    sys.path.insert(0, str(ROOT / 'revisions/2026-10-04-r12/code'))
    import common
    import evaluation
    spec = importlib.util.spec_from_file_location('r14_sensing', ROOT / 'revisions/2026-10-04-r14/code/sensing_diagnostic.py')
    sensing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sensing)
    old, pc, tc, torch = sensing.load_runtime(ROOT)
    weight = ROOT / protocol['weights'][str(d)]['path']
    if sha(weight) != protocol['weights'][str(d)]['sha256']:
        raise ValueError('protected-parent weights changed')
    a, critic, state = old.load(weight)
    protected = sensing.ProtectedActor(a, state['epsilon'], pc, torch)
    wt, constants = evaluation.account(d, cells, float(state['epsilon']), 'population')
    support = np.asarray(constants['initial_profiles'])
    count, h = int(protocol['paths']), float(wt['h'])
    seed = int(protocol['noise_seed']) + 10000 * d + cells
    initial = np.random.default_rng(seed + 100000000).integers(len(support), size=count)
    za, z0 = support[initial].copy(), support[initial].copy()
    B = old.coupling(d)
    Am, Bm, Cm, Mm = [pc.midpoint(wt[k]) for k in ['A', 'B', 'C', 'M']]
    center = pc.midpoint(wt['center'])
    lo = pc.up(wt['center'].hi - state['epsilon'])
    hi = pc.down(wt['center'].lo + state['epsilon'])
    production = np.zeros(count)
    deficit = np.zeros(count)
    noise_hash = hashlib.sha256()
    rng = np.random.default_rng(seed)
    c0 = old.P['productivity'] - (old.P['idiosyncratic_sigma']**2 + old.P['common_sigma']**2) / 2
    maximum = 0.0
    clipped = 0
    for k in range(cells):
        action = protected(k * h, za, center[k], lo[k], hi[k])
        fa = old.P['coupling'] * pc.safe_tanh(za @ B.T)
        f0 = old.P['coupling'] * pc.safe_tanh(z0 @ B.T)
        mean_action = action.mean(1)
        production += Bm[k] * (fa - f0).mean(1)
        deficit += Cm[k] - Am[k] * pc.safe_log(action).mean(1) + Bm[k] * mean_action
        deficit += old.P['adjustment'] / 2 * Am[k] * mean_action**2
        z = rng.standard_normal((count, d + 1))
        noise_hash.update(z.tobytes())
        clipped += int((np.abs(z) > 10).sum())
        z = np.clip(z, -10., 10.)
        dw = math.sqrt(h) * (old.P['idiosyncratic_sigma'] * z[:, :d] + old.P['common_sigma'] * z[:, d:])
        za += h * (c0 + fa - action) + dw
        z0 += h * (c0 + f0) - Mm[k] + dw
        maximum = max(maximum, float(np.max(np.abs(za))))
    if maximum > constants['state_cap']:
        raise ArithmeticError('protected-parent forward-error bootstrap exceeded')
    terminal = -old.CHI * math.exp(-old.P['discount'] * old.P['T']) * (
        ((za - za.mean(1, keepdims=True))**2).mean(1) -
        ((z0 - z0.mean(1, keepdims=True))**2).mean(1))
    gain = production - deficit + terminal
    bound = pc.empirical_lower(gain, constants['clipping_threshold'],
        constants['bias_upper'], constants['clipping_bias'],
        family_size=protocol['one_sided_family_size'], alpha=protocol['alpha'])
    out = Path(out) if out else R / 'results/observation'
    out.mkdir(parents=True, exist_ok=True)
    name = f'protected_nbo_d{d}_n{cells}'
    raw_path = out / (name + '.npz')
    np.savez_compressed(raw_path, paired_gain=gain, production=production,
        consumption_deficit=deficit, terminal_gain=terminal,
        terminal_policy=za, terminal_anchor=z0, initial_profile=initial)
    transfers = []
    for nu in protocol['sensor_noise_rms']:
        transfer = sensing.transfer_allowance(a, state, cells, float(nu), support, old, pc, tc, torch)
        interval = pc.I(bound['lower'], bound['upper']) + pc.I(
            -transfer['payoff_difference_upper'], transfer['payoff_difference_upper'])
        transfer['parent_id'] = name
        transfer['parent_grid'] = cells
        transfer['continuous_gain_interval'] = [float(interval.lo), float(interval.hi)]
        transfer['allowance_over_parent_lower'] = (
            transfer['payoff_difference_upper'] / bound['lower'] if bound['lower'] > 0 else None)
        transfer['scope'] = 'original continuous physical diffusion; same protected parent and grid; finite measured-state feedback with the stated RMS observation error'
        transfers.append(transfer)
    record = dict(record_type='protected_parent_and_sensor_certificate',
        method='nbo', implementation='protected_finite_observation', dimension=d,
        cells=cells, paths=count, seed=seed, weights=str(weight.relative_to(ROOT)),
        weights_sha256=sha(weight), protocol_sha256=sha(protocol_path),
        numerical_source_commit=os.environ.get('NBO_R15_NUMERICAL_SOURCE_COMMIT', 'uncommitted-development'),
        parent_bound=bound, constants=constants, transfers=transfers,
        raw_sha256=sha(raw_path), noise_sha256=noise_hash.hexdigest(),
        initial_state_sha256=hashlib.sha256(support[initial].tobytes()).hexdigest(),
        maximum_internal_state=maximum, clipped_normal_coordinates=clipped,
        state_transitions=2 * cells * count,
        peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        seconds_before_final_record_write=time.perf_counter() - beginning,
        timing_scope='imports, model loading, interval constants, protected simulation, raw I/O and all sensor allowances; process wrapper adds startup and final JSON write',
        comparison='continuous policy gain relative to the analytical schedule',
        selection='fixed reviewed iteration-80 NBO weights; all declared dimensions, grids and observation errors reported')
    write(out / (name + '.json'), record)
    print(json.dumps({'id': name, 'parent_lower': bound['lower'],
        'sensor_lowers': [r['continuous_gain_interval'][0] for r in transfers]}), flush=True)
    return record


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dimension', type=int, required=True)
    p.add_argument('--cells', type=int, required=True)
    p.add_argument('--out', type=Path)
    args = p.parse_args()
    run(args.dimension, args.cells, args.out)
