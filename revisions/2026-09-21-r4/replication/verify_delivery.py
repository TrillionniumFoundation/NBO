#!/usr/bin/env python3
"""Check delivered bytes and internal evidence assertions; NOT a training rerun."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE if (BASE / 'ECTA_R4.tex').exists() else BASE.parents[1]


def scientific_payload(value):
    """Exclude environment/wall-clock metadata, retaining dt and all economics."""
    if isinstance(value, dict):
        return {k: scientific_payload(v) for k, v in value.items()
                if k != 'environment' and not k.endswith('seconds')}
    if isinstance(value, list):
        return [scientific_payload(v) for v in value]
    return value


def payload_digest(value):
    data = json.dumps(scientific_payload(value), sort_keys=True,
                      separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def require(test, message):
    if not test:
        raise AssertionError(message)


def main():
    manifest = json.loads((BASE / 'manifest.json').read_text())
    for section, root in [('files', BASE), ('root_files', ROOT)]:
        for relative, expected in manifest[section].items():
            p = root / relative
            require(p.is_file(), f'Missing delivery file: {p}')
            actual = hashlib.sha256(p.read_bytes()).hexdigest()
            require(actual == expected['sha256'], f'Hash mismatch: {p}')
    result = json.loads((BASE / 'results/summary.json').read_text())
    require(payload_digest(result) == manifest['scientific_payload_sha256'],
            'Scientific payload digest mismatch')
    require([r['seed'] for r in result['NDU']] == [0, 1, 2], 'NDU seed set')
    for r in result['NDU']:
        require(r['execution_status'] == 'completed', 'Incomplete NDU seed')
        require(r['policy_loss_t0_max'] <= r['tolerance_target'], 'NDU target')
        require(r['finite_model_gain_bound'] >= r['policy_loss_t0_max'] - 1e-10,
                'Finite certificate below observed initial loss')
        require(len(r['policy_component_max_difference_c_theta_pi']) == 3,
                'Incomplete policy error vector')
        require(r['continuous_diffusion_value_error'] is None,
                'Finite model must not acquire a fake continuum error')
        require(r['source_sha256'] == manifest['files']['replication/solver.py']['sha256'],
                'NDU executed source mismatch')
    require([r['seed'] for r in result['merton']] == [0, 1, 2], 'Merton seed set')
    for r in result['merton']:
        require(r['transversality_decay_rate'] > 0, 'Merton admissibility')
        require(r['value_loss_max_on_half_to_two'] <= r['value_tolerance'], 'Merton target')
        require(r['critic_gradient_from_actor'] == 'disconnected', 'Gradient leak')
        require(r['source_sha256'] == manifest['files']['replication/merton.py']['sha256'],
                'Merton executed source mismatch')
    audits = result['audits']
    require(len(audits) == 9, 'Expected nine audit records')
    for name, row in audits.items():
        require(row['execution_status'] == 'completed', f'Incomplete audit: {name}')
        require(row['source_sha256'] == manifest['files']['replication/audits.py']['sha256'],
                f'Audit source mismatch: {name}')
    require(audits['generator']['result']['numpy_torch_Bellman_discrepancy'] < 1e-10,
            'Independent operators disagree')
    require(abs(audits['temporal']['result'][0]['sophisticated_c0_ratio'] - 5/12) < 1e-12,
            'Present-biased recursion mismatch')
    require(all(abs(r['bias_standard_errors']) < 5 for r in audits['trace']['result']),
            'Trace expectation test')
    require(audits['actor']['result']['rival_gradient_is_none'], 'Rival gradient leak')
    require(audits['actor']['result']['suboptimal_stable_gap'] > .39, 'Actor counterexample')
    for key in ['value_monotonicity_violation', 'adjustment_budget_monotonicity_violation',
                'flexibility_dominance_violation']:
        require(audits['economic']['result'][key] <= 1e-10, key)
    require(audits['game']['result']['one_shot_deviation_max'] <= 1e-10,
            'Finite game deviation')
    require(audits['recursive']['result']['minimum_bV'] > 0, 'Recursive sign domain')
    require(result['failures']['initial_pilot']['tolerance_status'] == 'not_met',
            'Failed pilot must remain unsuccessful')
    require(not result['failures']['timeouts']['results_available'], 'Timeout mislabeled')
    print(json.dumps({'delivery_hash_check': 'passed',
          'completed_NDU_seeds': 3, 'completed_Merton_seeds': 3, 'audit_records': 9,
          'training_rerun': False, 'canonical_class_build_verified': False,
          'continuum_NDU_error_verified': False,
          'scientific_payload_sha256': payload_digest(result)}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, OSError, KeyError, ValueError) as exc:
        raise SystemExit(f'Delivery verification failed: {exc}') from exc
