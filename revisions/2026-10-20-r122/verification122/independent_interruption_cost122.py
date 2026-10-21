"""Account only for saved completed evaluator clocks in interrupted R122 I02.

This additive receipt is consumed by the unchanged research_cost_ledger122.py
through --additional-receipts.  It does not infer the missing parent duration,
resume a process, import an economic module, or charge cached/replayed values
as fresh work in a later process.
"""
from __future__ import annotations
import argparse
import datetime as dt
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
F = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
D = 'a3323b6f557315ea91b536637419ef6fd7984b61'
I = '1f19410305c707716135defd91d6644d70657d84'
FORENSIC_SHA = '58a899a4516a5df99ad712d5cb0fe94b699042424b055070acc19fe7d68e7ddd'
EXPECTED_LOWER = Q(92977404913995, 68719476736)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for b in iter(lambda: stream.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    out = a.output.resolve()
    if out.exists():
        raise FileExistsError('Cost receipt output must be new: ' + str(out))
    started = time.perf_counter()
    inputs = []

    def bind(path):
        path = path.resolve()
        if not path.is_relative_to(REPO) or not path.is_file():
            raise ValueError('Required native input outside repository or absent')
        row = {'path': path.relative_to(REPO).as_posix(),
               'bytes': path.stat().st_size, 'sha256': digest(path)}
        inputs.append(row)
        return row

    stage = ROOT / 'results122/independent-attempt02'
    forensic_path = stage / 'INTERRUPTION_FORENSIC122.json'
    if bind(forensic_path)['sha256'] != FORENSIC_SHA:
        raise ValueError('Original interruption forensic identity changed')
    forensic = json.loads(forensic_path.read_text())
    if (forensic['source_commit'], forensic['state_commit'], forensic['independent_repair_commit']) != (F, D, I):
        raise ValueError('Interrupted F/D/I scientific identity differs')
    if (forensic['status'] != 'interrupted_without_terminal_receipt'
            or forensic['actual_parent_exit_code'] is not None
            or forensic['actual_parent_wall_seconds'] is not None):
        raise ValueError('Missing parent terminal status or duration was invented')
    for name in ('EXECUTION122.json', 'FAILURE122.json', 'OUTER_EXECUTION122.json'):
        if (stage / name).exists():
            raise ValueError('Interrupted attempt acquired an unexpected terminal receipt')
    if (ROOT / 'results122/launch-independent-attempt02/LAUNCH122.json').exists():
        raise ValueError('Interrupted parent acquired an unexpected terminal launch receipt')
    paths = set()
    for expected in forensic['native_files']:
        rel = Path(expected['path'])
        if rel.is_absolute() or '..' in rel.parts or expected['path'] in paths:
            raise ValueError('Unsafe/duplicate forensic native path')
        paths.add(expected['path'])
        row = bind(ROOT / rel)
        if row['bytes'] != expected['bytes'] or row['sha256'] != expected['sha256']:
            raise ValueError('Original interrupted native bytes changed: ' + str(rel))
    if len(paths) != forensic['native_file_count'] or sum(x['bytes'] for x in forensic['native_files']) != forensic['native_bytes']:
        raise ValueError('Forensic native census differs')
    evaluations_path = stage / 'POLICY_EVALUATIONS122.jsonl'
    raw = evaluations_path.read_bytes()
    if not raw.endswith(b'\n'):
        raise ValueError('Incomplete final evaluation line')
    rows = [json.loads(line) for line in raw.splitlines()]
    keys = [row['key_id'] for row in rows]
    if len(rows) != 716 or len(set(keys)) != 716 or forensic['completed_policy_rows'] != 716 or forensic['completed_policy_unique_keys'] != 716:
        raise ValueError('Interrupted complete evaluation census differs')
    if forensic['completed_claim_rows'] != 0:
        raise ValueError('This reader handles only the observed base-prefix interruption')
    for row in rows:
        if row['bins'] != 64 or row['terminal_contexts'] != 129 or row['terminal_steps'] != 32 or Q(row['seconds']) < 0:
            raise ValueError('Unexpected completed evaluation level or clock')
    lower = sum((Q(row['seconds']) for row in rows), Q(0))
    if lower != EXPECTED_LOWER or lower != Q(forensic['completed_evaluation_seconds_lower']):
        raise ValueError('Exact observed completed-evaluator clock sum differs')
    primary = ROOT / 'results122/primary-attempt02/records122.jsonl'
    if bind(primary)['sha256'] != forensic['primary_sha256']:
        raise ValueError('Interrupted independent primary binding differs')
    source = bind(Path(__file__).resolve())
    elapsed = time.perf_counter() - started
    receipt = {
        'status': 'verified_interrupted_independent_cost_lower',
        'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'source_commit': F, 'state_commit': D,
        'independent_repair_commit': I, 'reader': source,
        'forensic_sha256': FORENSIC_SHA,
        'completed_evaluations': 716,
        'completed_evaluation_seconds_lower': str(lower),
        'interrupted_parent_wall_seconds': None,
        'interrupted_parent_exit_code': None,
        'full_interrupted_cost_known': False,
        'parent_utc_observation_interval_used_as_monotonic_clock': False,
        'elapsed_seconds': elapsed,
        'cost_clock_components': [
            {'category': 'interrupted_independent_completed_evaluations_lower',
             'clock_fields': [['completed_evaluation_seconds_lower']],
             'overlaps_counted_parent': False, 'partial_lower_bound_only': True,
             'scope': 'Sum of 716 nonoverlapping saved completed evaluate_action inner clocks from interrupted independent02. The full original parent elapsed time/exit is unknown; source checks, writes, startup, partial next evaluation and missing work are not imputed as zero. Later cached replay retains original seconds as provenance and is never a second charge of this work.'},
            {'category': 'independent_interruption_cost_reader',
             'clock_fields': [['elapsed_seconds']],
             'overlaps_counted_parent': False, 'partial_lower_bound_only': True,
             'scope': 'This separate saved-receipt/hash cost audit only; process startup and final receipt serialization excluded.'},
        ],
        'inputs': sorted(inputs, key=lambda x: x['path']),
        'standalone_service_allocation_changed': False,
        'new_economic_evaluations': 0, 'new_states': 0,
        'new_training': 0, 'new_timing_processes': 0,
        'original_interrupted_success_asserted': False,
    }
    # Recheck every bound byte before writing the administrative receipt.
    for row in inputs:
        path = REPO / row['path']
        if path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
            raise ValueError('Input changed during cost audit')
    receipt['elapsed_seconds'] = time.perf_counter() - started
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x') as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': receipt['status'], 'completed_evaluation_seconds_lower': str(lower),
                      'interrupted_parent_wall_seconds': None, 'elapsed_seconds': receipt['elapsed_seconds']}, indent=2))


if __name__ == '__main__':
    main()
