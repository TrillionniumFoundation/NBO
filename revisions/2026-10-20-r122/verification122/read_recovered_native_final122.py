"""Read actual completed recovery evidence; run no economics or inference.

This new administrative reader authenticates the completed Git snapshot,
current native output manifests and saved gate relationships. It does not
recreate the unavailable earlier reader or count unavailable earlier results.
"""
from __future__ import annotations
import argparse
import datetime as dt
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = 'revisions/2026-10-20-r122/'
C = '5635a3a0af330933b3ff1b9331ba4fe468eac628'
S = '6ab1f9d4f1f9eb70014a7d104b84a499b64ba84c'
F = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
D = 'a3323b6f557315ea91b536637419ef6fd7984b61'
M = '796c5f2badf68b051ac6c144884c0e61b87faf5e'
R = '0fe0f2bbf76529201a1890db0fc2a94b0be44418'
I = '1f19410305c707716135defd91d6644d70657d84'
STATUS = 'provenance122/runtime-recovery-39691016040-1/RECOVERY_STATUS122.json'
PRIMARY_SHA = '94fc7537e5020e464118c64076c8f6ace5ff3dd6d77b1e15d35dc3f2712e5044'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    tick = time.perf_counter()
    output = args.output.resolve()
    require(output.is_relative_to(ROOT) and not output.exists(), 'New R122 output required')
    inputs = {}
    assertions = 0

    def check(condition, message):
        nonlocal assertions
        require(condition, message)
        assertions += 1

    def bind(relative):
        pure = PurePosixPath(relative)
        check(not pure.is_absolute() and '..' not in pure.parts and pure.as_posix() == relative,
              'Noncanonical native path')
        path = ROOT / pure
        check(path.is_file() and not path.is_symlink(), 'Missing ordinary native input: ' + relative)
        record = dict(path=path.relative_to(REPO).as_posix(), bytes=path.stat().st_size, sha256=sha(path))
        key = record['path']
        check(key not in inputs or inputs[key] == record, 'Input changed between reads')
        inputs[key] = record
        return path

    def read(relative):
        return json.loads(bind(relative).read_text())

    def rows(relative):
        with bind(relative).open() as stream:
            return [json.loads(line) for line in stream if line.strip()]

    status = read(STATUS)
    git_status = subprocess.check_output(['git', 'show', C + ':' + PREFIX + STATUS], cwd=REPO)
    check(bind(STATUS).read_bytes() == git_status, 'Native status differs from completed delivery C')
    check(status['status'] == 'completed_recovery_science_and_report', 'Run is not complete')
    check((status['source_commit'], status['source_commit_F'], status['state_commit_D'],
           status['actor_commit_M'], status['continuation_commit_R'], status['independent_schema_commit_I'])
          == (S, F, D, M, R, I), 'Recovery source identities differ')
    check(all(status[key] == 0 for key in ['new_initial_states', 'new_training',
        'new_primary_decisions', 'new_service_timing_replicates']), 'Recovery changed original experiment')
    check(status['prior_unpublished_completion_is_not_a_native_input'] is True,
          'Unavailable prior completion used as native evidence')
    for stage in status['stages']:
        check(sha(bind(stage['log'])) == stage['log_sha256'], 'Stage log changed')
    canonical = status['canonical_directory']
    stats = status['statistics_directory']
    report = status['report_directory']
    original = status['original_report_directory']
    independent = read(canonical + '/EXECUTION122.json')
    resume = read(canonical + '/RESUME_SEGMENT122.json')
    composite = read(status['composite_verification'])
    core = read(status['report_verification'])
    check(sha(bind(canonical + '/RESUME_SEGMENT122.json')) == status['canonical_receipt_sha256'],
          'Canonical identity differs from completed run')
    check(independent['status'] == 'executed' and independent['exit_code'] == 0
          and resume['status'] == 'canonical_complete' and resume['exit_code'] == 0,
          'Canonical audit did not succeed')
    check(resume['canonical_finalizer_new_economic_calls'] == resume['fresh_policy_calls'] == 0,
          'Canonical finalizer must use zero fresh policy calls')
    check(composite['status'] == core['status'] == 'verified' and core['verified_through'] == 'report',
          'Saved independent/composite report gates did not pass')
    check(core['full_package_success'] is False, 'The report gate is not the final full package')
    check(sha(bind('results122/primary-attempt02/records122.jsonl')) == PRIMARY_SHA,
          'Original completed primary bytes differ')
    check(composite['primary_sha256'] == resume['primary_sha256'] == PRIMARY_SHA,
          'Gate primary identities differ')
    check(sha(bind(str(PurePosixPath(status['composite_verification']).parent / 'INPUTS_RESUME_VERIFICATION122.json')))
          == composite['input_manifest_sha256'], 'Composite input inventory changed')
    frozen_manifest = read('SOURCE_FREEZE122.json')
    check(len(frozen_manifest['scientific_files']) == frozen_manifest['source_file_count'] == 243,
          'Frozen scientific inventory changed')
    for name, expected in frozen_manifest['scientific_files'].items():
        path = REPO / name
        check(path.is_file() and not path.is_symlink() and sha(path) == expected, 'Frozen native member differs: ' + name)
        inputs[name] = dict(path=name, bytes=path.stat().st_size, sha256=expected)
    manifest = read(report + '/OUTPUT_MANIFEST122.json')
    seen = set()
    for item in manifest['files']:
        check(item['path'] not in seen, 'Duplicate report manifest member')
        seen.add(item['path'])
        path = bind(report + '/' + item['path'])
        check((path.stat().st_size, sha(path)) == (item['bytes'], item['sha256']), 'Report output changed')
    summary = read(report + '/SUMMARY_REPORT122.json')
    report_execution = read(report + '/EXECUTION122.json')
    stats_execution = read(stats + '/EXECUTION122.json')
    for directory, execution in [(canonical, independent), (stats, stats_execution), (report, report_execution)]:
        outer = read(directory + '/OUTER_EXECUTION122.json')
        check(execution['status'] == outer['status'] == 'executed'
              and execution['exit_code'] == outer['exit_code'] == 0, 'Nonterminal successful stage')
    original_failure = read(original + '/FAILURE122.json')
    original_outer = read(original + '/OUTER_EXECUTION122.json')
    check(original_failure['status'] == original_outer['status'] == 'failed'
          and original_outer['exit_code'] == 1 and 'multiple values for keyword argument' in original_failure['traceback'],
          'Actual frozen reporter failure was not preserved')
    check(summary['source_commit'] == F and summary['state_commit'] == D and summary['actor_commit'] == M,
          'Report source/sample/actor identities differ')
    policy_rows = rows(report + '/POLICY_CELLS122.jsonl')
    contrasts = rows(report + '/SERVICE_CONTRASTS122.jsonl')
    signed = rows(report + '/SIGNED_POPULATION_COMPARISONS122.jsonl')
    domains = rows(report + '/ALL_THREE_CLOCK_INTERSECTIONS122.jsonl')
    check(len(policy_rows) == summary['policy_cells'] == report_execution['policy_cells'], 'Policy census differs')
    check(len(contrasts) == summary['treatment_population_cells'] == stats_execution['safe_mean_intervals'], 'Own-control population census differs')
    check(len(signed) == summary['signed_population_cells'] == stats_execution['signed_mean_intervals'], 'Signed population census differs')
    check(sum(Q(row['population_gain_lower']) > 0 for row in contrasts) == summary['positive_population_gain_cells'], 'Positive own-control population count differs')
    check(sum(Q(row['population_gain_lower']) > 0 for row in signed) == summary['positive_signed_population_gain_cells'], 'Positive signed population count differs')
    check(sum(Q(row['population_gain_upper']) < 0 for row in signed) == summary['negative_signed_population_gain_cells'], 'Negative signed population count differs')
    check(sum(row['arm'] == 'relu' and not row['sufficient_price_domain']['empty'] for row in domains)
          == summary['all_three_clock_neural_nonempty_sufficient'], 'Sufficient neural domain count differs')
    check(sum(row['arm'] == 'relu' and not row['upper_not_ruled_out_domain']['empty'] for row in domains)
          == summary['all_three_clock_neural_nonempty_upper_not_ruled_out'], 'Not-ruled-out neural domain count differs')
    check(stats_execution['actual_state_units'] == summary['independent_state_units'] == core['counts']['independent_states'], 'Population unit census differs')
    check(independent['actual_independent_evaluations'] == composite['total_distinct_original_evaluations_represented']
          == resume['delivered_unique_evaluation_count'] == core['counts']['independent_evaluations'], 'Independent evaluation census differs')
    for ik, ck, rk in [('accepted_primary_decisions', 'accepted_claims', 'accepted_action_validation_denominator'),
        ('accepted_gain_claims_independently_confirmed', 'accepted_gain_claims_independently_confirmed', 'accepted_action_independent_gain_confirmations'),
        ('accepted_candidate_intervals_independently_contained', 'accepted_candidate_intervals_independently_contained', 'accepted_action_independent_candidate_containment')]:
        check(independent[ik] == composite[ck] == summary[rk], 'Accepted-claim census differs')
    for item in inputs.values():
        path = REPO / item['path']
        check((path.stat().st_size, sha(path)) == (item['bytes'], item['sha256']), 'Input changed before success')
    result = dict(status='verified_actual_recovered_native_summary', created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        delivery_commit_C=C, recovery_source_S=S, source_F=F, states_D=D, actor_M=M,
        reader_sha256=sha(Path(__file__)), assertions=assertions,
        paths={k:status[k] for k in ['canonical_directory','statistics_directory','original_report_directory','report_directory','composite_verification','report_verification']},
        input_files=sorted(inputs.values(), key=lambda x:x['path']), report_summary=summary,
        verified_report_members=len(seen), composite_assertions=composite['assertions'],
        report_gate_assertions=core['assertions'], core_counts=core['counts'],
        actual_new_evaluations_in_recovery=composite['actual_new_original_evaluations_across_segments'],
        retained_evaluations=composite['original_interrupted_evaluations'],
        actual_segments=composite['native_continuation_segments'],
        canonical_finalizer_new_economic_calls=0, new_economic_evaluations_by_reader=0,
        actual_frozen_report_failure_preserved=True, full_package_success_asserted=False,
        source_specific_ci_success_asserted=False, whole_study_exact_seconds=None,
        cost_warning='The unchanged SUMMARY_REPORT actual_new_scientific_stage_seconds_excluding_current_report is a stage subtotal, not a full independent recovery or whole-study cost. Separate measured segment, cache, publication and interruption accounting is required.',
        scope='Actual completed current Git/native saved receipts and complete report bytes only. This reader does not execute economics, recompute confidence bounds, replace the unchanged scientific verifier, or use unavailable earlier completion observations.',
        elapsed_seconds=time.perf_counter()-tick,
        cost_clock_components=[dict(category='administrative_evidence_readback', clock_fields=[['elapsed_seconds']],
            scope='This separate read-only complete-report and frozen-native identity reader; original science and saved verifier clocks are not included.',
            partial_lower_bound_only=True, overlaps_counted_parent=False)])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(status=result['status'], assertions=assertions, report_members=len(seen),
        receipt_sha256=sha(output), elapsed_seconds=result['elapsed_seconds']), indent=2))


if __name__ == '__main__':
    main()
