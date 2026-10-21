"""Administrative identity check fixed by the published R122 restart protocol.

This additive reader does not change the frozen scientific source and makes no
economic call.  Run only after the complete retry and its external receipt.
"""
from __future__ import annotations
import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code122'))
from common122 import ACTOR_COMMIT, REPO, digest, dump, fail, finish, git_file, identities, key, start, validated_states, verify_source

IDENTITY_FIELDS = (
    'action', 'baseline_action', 'accepted_improvement', 'candidate_rejected',
    'refinement_count', 'paid_refinement_attempt_count',
    'paid_refinement_levels_started', 'candidate_algebra_attempts',
    'candidate_bound_attempts', 'refused_candidate_bound_attempts',
    'certified_policy_gain_lower', 'improvement_stop', 'complete_policy_lower',
    'complete_policy_upper', 'certified_regret_upper', 'raw_proposal_kept',
)


def stream(path):
    with Path(path).open() as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    for name in ('source-commit', 'state-commit', 'restart-commit'):
        parser.add_argument('--' + name, required=True)
    for name in ('original', 'current', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    out, initial, tick = start(args.output, 'administrative-restart-comparison',
                              {'claimed_source_commit': args.source_commit})
    try:
        dump(out / 'VERIFIED_SOURCE122.json', verify_source(args.source_commit))
        protocol_path = ROOT / 'RESTART_PROTOCOL122.json'
        require(git_file(args.restart_commit, protocol_path.relative_to(REPO)) == protocol_path.read_bytes(),
                'Administrative protocol is not the published restart identity')
        protocol = json.loads(protocol_path.read_text())
        require(protocol['source_commit'] == args.source_commit and protocol['state_commit'] == args.state_commit,
                'Restart changed original source or states')
        require(args.original.resolve() == (ROOT / protocol['original_attempt']).resolve()
                and args.current.resolve() == (ROOT / protocol['new_attempt']).resolve(),
                'Restart directory identity differs')
        forensic_path = args.original / 'INTERRUPTION_FORENSIC122.json'
        require(digest(forensic_path) == protocol['forensic_sha256'], 'Forensic identity differs')
        forensic = json.loads(forensic_path.read_text())
        for record in forensic['files']:
            path = args.original / record['path']
            require(path.stat().st_size == record['bytes'] and digest(path) == record['sha256'],
                    'Preserved interrupted evidence changed: ' + record['path'])
        require(forensic['exit_code'] is None and forensic['actual_full_external_wall_seconds'] is None,
                'Unavailable interrupted process clock was invented')
        require(not (args.original / 'EXECUTION122.json').exists()
                and not (args.original / 'OUTER_EXECUTION122.json').exists(),
                'Interrupted parent acquired an unsupported terminal receipt')
        for filename in ('EXECUTION122.json', 'OUTER_EXECUTION122.json'):
            executed = json.loads((args.current / filename).read_text())
            require(executed['status'] == 'executed' and executed['exit_code'] == 0,
                    'Retry lacks its actual complete successful receipt')
        binding = json.loads((args.current / 'STATES_USED122.json').read_text())
        require(binding['source_commit'] == args.source_commit and binding['state_commit'] == args.state_commit
                and binding['actor_commit'] == ACTOR_COMMIT, 'Retry scientific identity differs')
        states = validated_states(REPO / binding['state_directory'], args.source_commit, args.state_commit)

        def checked_identity(row):
            require(row['source_commit'] == args.source_commit and row['state_commit'] == args.state_commit
                    and row['actor_commit'] == ACTOR_COMMIT, 'Mixed scientific identity in retained rows')
            require(row['state'] == states[row['row']]['state'] and row['state_hex'] == states[row['row']]['hex'],
                    'State bytes changed across the administrative retry')
            return tuple(row[name] for name in IDENTITY_FIELDS)

        current_path = args.current / 'records122.jsonl'
        current = {}
        for row in stream(current_path):
            require(key(row) not in current, 'Duplicate retry primary row')
            current[key(row)] = checked_identity(row)
        require(set(current) == identities(), 'Retry does not contain exactly 5568 primary identities')
        datasets = []
        work_lower = Fraction(0)
        declared = (
            ('primary', args.original, 5568),
            ('timing0', args.original / 'timing' / 'attempt00', 2784),
            ('timing1', args.original / 'timing' / 'attempt01', 1456),
        )
        for name, directory, expected in declared:
            path = directory / 'records122.jsonl'
            count = 0
            seen = set()
            for row in stream(path):
                identity = key(row)
                require(identity not in seen, 'Duplicate original row in ' + name)
                seen.add(identity)
                require(checked_identity(row) == current[identity],
                        'Policy identity changed after interruption: ' + repr((name, identity)))
                count += 1
            require(count == expected, 'Original complete/prefix census changed in ' + name)
            for cohort in stream(directory / 'cohorts122.jsonl'):
                work_lower += Fraction(cohort['complete_cohort_seconds'])
            datasets.append({'name': name, 'path': str(path.resolve().relative_to(REPO)),
                             'rows': count, 'sha256': digest(path),
                             'identity_fields': list(IDENTITY_FIELDS), 'status': 'identical'})
        result = {
            'status': 'identical', 'source_commit': args.source_commit,
            'state_commit': args.state_commit, 'actor_commit': ACTOR_COMMIT,
            'restart_protocol_commit': args.restart_commit,
            'protocol_sha256': digest(protocol_path),
            'original_forensic_sha256': digest(forensic_path),
            'primary02_sha256': digest(current_path), 'datasets': datasets,
            'total_rows': sum(row['rows'] for row in datasets),
            'new_population_observations': 0, 'original_parent_wall_seconds': None,
            'interrupted_completed_cohort_seconds_lower': str(work_lower),
            'reader_sha256': digest(Path(__file__)),
            'reader_is_additive_administrative_code_outside_original_F': True,
            'economic_calls': 0, 'new_timing_processes': 0,
            'cost_scope': 'Only the measured nonoverlapping interrupted cohort sum is an exact recorded lower bound; no complete interrupted parent clock is invented.',
        }
        require(result['total_rows'] == 9808, 'Complete retry comparison census required')
        dump(out / 'RESTART_COMPARISON122.json', result)
        dump(args.current / 'RESTART_COMPARISON122.json', result)
        finish(out, initial, tick, {'rows_compared': 9808, 'economic_calls': 0,
                                    'new_population_observations': 0})
    except BaseException:
        fail(out, tick)
        raise


if __name__ == '__main__':
    main()
