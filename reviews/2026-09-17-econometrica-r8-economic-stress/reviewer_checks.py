#!/usr/bin/env python3
"""R8 reviewer stress tests. No author files are modified.

Run each mode from a checkout carrying reviewed commit be77b2a. These are new
reviewer experiments using the author's hash-pinned transition constructor,
not an independently implemented kernel or a diffusion convergence test.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'

REVIEWED = 'be77b2a81b4d3a68806c534c1e892d2eb4b1230d'
MANIFESTS = {
    'source_inventory.json': '12c99b246a5f609d59a19db1f9b3b229848b0b50e9701c12c69a9a772868c2ee',
    'protected_history.json': 'f7c55a9713c93d7acee9a615bc49aa351f1d8cc2d0e0c3f7e328548ae83484a8',
}
SIGNS = ('positive', 'nonpositive')
POINTS = ((0., .4), (.125, .425), (.25, .45))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources(repo: Path) -> dict[str, str]:
    expected = {}
    directory = repo / 'revisions/2026-09-17-r8-full-response'
    for name, sha in MANIFESTS.items():
        path = directory / name
        if digest(path) != sha:
            raise ValueError(f'Not the reviewed manifest: {path}')
        expected.update(json.loads(path.read_text()))
    names = ['replication/r8/model.py', 'replication/r8/numerical_core.py',
             'replication/r4/solver.py', 'replication/r6/transport.py',
             'replication/r6/kernel_certificate.py', 'replication/r7/core.py']
    names += [f'replication/r4/output/safe_policy_{s}.npz' for s in (101, 202, 303)]
    result = {name: digest(repo / name) for name in names}
    for name, actual in result.items():
        if actual != expected[name]:
            raise ValueError(f'Changed scientific input: {name}')
    return result


def economics(m, old, r7, np):
    center = m.center
    state = m.e[0].states[center]
    rows, caps = [], []
    direct_error = 0.
    # Reoptimize the original full target; later-date values remain exact when
    # the intervention changes only the initial-date action menu.
    for lam, d in POINTS:
        for adjust in (True, False):
            pair = m.class_pair(lam, d, adjust)
            base = {}
            for sign, item in pair.items():
                base[sign] = {'value': float(item['value'][0, center]),
                              'action': m.e[0].controls(item['policy'])[0, center].tolist()}
                direct_error = max(direct_error, float(abs(m.direct(item['policy'], lam, d) - item['value']).max()))
            continuation = pair['positive']['value'][1].reshape(m.e[0].shape)
            ct = np.unique(m.e[0].menu[:, :2], axis=0)
            if not adjust:
                ct = ct[np.isclose(ct[:, 1], 0.)]

            def action_values(actions):
                q = np.zeros(len(actions))
                for prob, economy in zip((1-lam, lam), m.e):
                    y, live, disc, flow, _, _, alpha = old.transition(state[None, :], actions, 1/8, economy.model)
                    annuity = -np.expm1(-economy.model.rho*alpha/8)/economy.model.rho
                    q += prob * (flow + d*annuity + disc*np.where(live, old.interpolate(continuation, y), old.terminal(y))).mean(-1)
                return q

            grid = np.unique(np.r_[np.linspace(-.5, .8, 651), 0., 1e-8, -1e-8])
            actions = np.c_[np.repeat(ct, len(grid), axis=0), np.tile(grid, len(ct))]
            q = action_values(actions)
            dense = {}
            for sign in SIGNS:
                allowed = actions[:, 2] > 0 if sign == 'positive' else actions[:, 2] <= 0
                j = np.where(allowed, q, -np.inf).argmax()
                dense[sign] = {'value': float(q[j]), 'action': actions[j].tolist()}
            rows.append({'lambda': lam, 'd': d, 'adjustment': adjust,
                         'original': base, 'first_period_dense_scan': dense,
                         'scan_risky_positions': len(grid)})
            for pi in (.805, .81, .82, -.505, -.51, -.52):
                actions = np.c_[ct, np.full(len(ct), pi)]
                q = action_values(actions); j = q.argmax()
                new = {s: base[s]['value'] for s in SIGNS}
                sign = 'positive' if pi > 0 else 'nonpositive'
                new[sign] = max(new[sign], float(q[j]))
                caps.append({'lambda': lam, 'd': d, 'adjustment': adjust, 'added_pi': pi,
                             'best_added_action': actions[j].tolist(), 'new_values': new,
                             'new_delta': new['positive']-new['nonpositive']})
    assert direct_error < 2e-11

    # G is tested as a supersolution for every action, date, and node. At d=.45
    # it suffices to test lambda endpoints: duration is nonnegative and each
    # fixed-action backup is affine in lambda. Boundary rows pay G exactly.
    obstacle = []
    for lam in (0., .25):
        for n in range(8):
            q = (1-lam)*m.q(0, n, m.terminal, .45) + lam*m.q(1, n, m.terminal, .45)
            residual = q-m.terminal[:, None]
            bd = m.e[0].boundary
            obstacle.append({'lambda': lam, 'date': n,
                             'max_interior': float(residual[~bd].max()),
                             'max_boundary_abs': float(abs(residual[bd]).max())})
    assert max(r['max_interior'] for r in obstacle) < -.02
    assert max(r['max_boundary_abs'] for r in obstacle) < 2e-14

    # Independent backward optional-stopping calculation, while retaining the
    # compulsory first interval in each risk class. Exit may start at date 1.
    exits = []
    for lam, d in POINTS:
        for adjust in (True, False):
            value = m.terminal.copy()
            for n in range(7, -1, -1):
                q = (1-lam)*m.q(0, n, value, d)+lam*m.q(1, n, value, d)
                q = np.where(r7.mask(m, n, adjust), q, -np.inf)
                if n == 0:
                    committed = {s: float(np.where(r7.mask(m, n, adjust, s), q, -np.inf).max(1)[center]) for s in SIGNS}
                value = np.maximum(m.terminal, q.max(1))
            exits.append({'lambda': lam, 'd': d, 'adjustment': adjust,
                          'immediate_exit': float(m.terminal[center]),
                          'value_when_time_zero_exit_allowed': float(value[center]),
                          'first_interval_commitment_values': committed})
    return {'original_and_dense': rows, 'initial_menu_extensions': caps,
            'uniform_exit_obstacle': obstacle, 'optional_exit': exits,
            'maximum_selected_policy_replay_error': direct_error,
            'scope': 'Finite arrays. Cap extensions alter only the first action menu; all later controls remain the original full target. Optional exit changes admissibility, not the original theorem.'}


def rectangular(m, repo, r7, np):
    path = repo/'replication/r8/output/decision_contest_coefficients.npz'
    if digest(path) != '811facbb8de820fa8f747d891be13fe3912787fa9b4ca594ba567a0c08af9b8a':
        raise ValueError('Not the reviewed feasible-policy coefficient bank')
    bank = np.load(path)

    def upper(a, b, d, adjust):
        value = m.terminal.copy()
        for n in range(7, -1, -1):
            q0, q1 = m.q(0, n, value, d), m.q(1, n, value, d)
            q = np.maximum((1-a)*q0+a*q1, (1-b)*q0+b*q1)
            q = np.where(r7.mask(m, n, adjust), q, -np.inf)
            if n == 0:
                return {s: float(np.where(r7.mask(m, n, adjust, s), q, -np.inf).max(1)[m.center]) for s in SIGNS}
            value = q.max(1)

    results = []
    for count in (1, 2, 4):
        start = time.perf_counter(); edges = np.linspace(0., .25, count+1)
        cell_results = []
        for a, b in zip(edges[:-1], edges[1:]):
            bounds = {}
            for adjust in (True, False):
                up = {d: upper(a, b, d, adjust) for d in (.4, .45)}
                U = {s: np.stack([np.repeat(up[d][s], 9) for d in (.4, .45)]) for s in SIGNS}
                L = {s: [] for s in SIGNS}
                for s in SIGNS:
                    for t in (0., .25):
                        for ad in (.4, .45):
                            c0, c1 = bank[f'lower.full.{(adjust, t, ad, s)}']
                            L[s].append(np.stack([r7.restrict(c0+d*c1, a, b) for d in (.4, .45)]))
                bounds[str(adjust)] = [max(float((l-U['nonpositive']).min()) for l in L['positive'])-2e-7,
                                      min(float((U['positive']-l).max()) for l in L['nonpositive'])+2e-7]
            cell_results.append(bounds)
        aggregate = {s: [min(r[s][0] for r in cell_results), max(r[s][1] for r in cell_results)] for s in ('True', 'False')}
        results.append({'cells': count, 'bounds': aggregate, 'cell_bounds': cell_results,
                        'signs_pass_with_2e_minus7_padding': aggregate['True'][0] > 0 and aggregate['False'][1] < 0,
                        'upper_and_restriction_seconds': time.perf_counter()-start})
    bank.close()
    return {'rows': results, 'padding_per_difference': 2e-7,
            'scope': 'Shared deposited feasible lower bank and full 1568-action upper target. Timings exclude bank construction and are serial component diagnostics, not end-to-end software rankings. Same conservative padding as the R8 difference comparison; not directed-rounding kernel certification.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--mode', choices=('economics', 'rectangular'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); repo = args.repo.resolve()
    verified = verify_sources(repo)
    sys.path.insert(0, str(repo/'replication/r8'))
    import numpy as np
    import scipy
    from model import Model, old, r7
    start = time.perf_counter(); model = Model()
    result = economics(model, old, r7, np) if args.mode == 'economics' else rectangular(model, repo, r7, np)
    result.update(reviewed_commit=REVIEWED, mode=args.mode, verified_input_sha256=verified,
                  python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                  model_build_seconds=model.build_seconds, elapsed_seconds=time.perf_counter()-start)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(f'{args.mode}: wrote {args.out}; reviewed inputs verified')


if __name__ == '__main__':
    main()
