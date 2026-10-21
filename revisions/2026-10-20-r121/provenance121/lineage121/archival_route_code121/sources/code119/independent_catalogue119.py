"""Validation D: exhaustive independent Fraction original-policy enclosures.

This is post-C validation of a known, fixed catalogue. It neither imports a
production terminal compiler nor reexecutes a campaign or competitive timer.
The only scientific import is the unchanged standard-library independent94
primitive implementation. Every existing observation remains unchanged.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PHASE_C_COMMIT = '095936f1a7556d90d74809e63d75d9959d118360'
ARMS = ('online', 'quadratic', 'relu', 'hinge', 'spline', 'poly2', 'poly3', 'grid')
SERVICES = ('compiled', 'geometric', 'active-tail', 'masked-tail', 'budgeted-tail', 'fused-tail')
ALPHAS = (F(1, 2), F(3, 4))
BINS = 64
TERMINAL_STEPS = 32
R = F(1, 32)
BETA = F(15, 16)
TERMINAL_ALLOWANCE = F(1, 2**20)
EXPECTED_KEYS = (492, 491)
EXPECTED_ROWS = 13824
MANIFEST_NAME = 'VALIDATION_D119_MANIFEST.json'
KEYS_NAME = 'VALIDATION_D119_KEYS.json'


def serial(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    return value


def packed(value):
    return (json.dumps(serial(value), sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_new(path, value):
    with Path(path).open('xb') as stream:
        stream.write(packed(value))
        stream.flush()
        os.fsync(stream.fileno())


def append_record(stream, value):
    stream.write(packed(value))
    stream.flush()
    os.fsync(stream.fileno())


def as_binary(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError('Expected a stored finite binary64 number')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Nonfinite stored number')
    return value.hex(), str(F(value))


def safe_relative(relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative:
        raise ValueError('Unsafe manifest path')
    return ROOT/path


def bind_sources(commit):
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('A full lowercase immutable Git commit is required')
    manifest_path = ROOT/MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text())
    if manifest['phase_C_execution_commit'] != PHASE_C_COMMIT:
        raise ValueError('Wrong original phase C identity')
    bound = []
    new_and_current = dict(manifest['current_scientific_files'])
    new_and_current.update(manifest['validation_files'])
    # The manifest itself is Git-bound; it cannot contain its own hash.
    new_and_current[MANIFEST_NAME] = digest(manifest_path)
    for relative, expected in sorted(new_and_current.items()):
        path = safe_relative(relative)
        if digest(path) != expected:
            raise ValueError(f'Local source hash mismatch: {relative}')
        git_path = path.relative_to(REPO).as_posix()
        original = subprocess.run(['git', 'show', f'{commit}:{git_path}'], cwd=REPO,
                                  check=True, capture_output=True).stdout
        if hashlib.sha256(original).hexdigest() != expected:
            raise ValueError(f'Prospective committed source mismatch: {relative}')
        bound.append(dict(path=relative, sha256=expected))
    inputs = []
    for relative, spec in sorted(manifest['input_files'].items()):
        path = safe_relative(relative)
        if path.stat().st_size != spec['bytes'] or digest(path) != spec['sha256']:
            raise ValueError(f'Frozen phase C input mismatch: {relative}')
        inputs.append(dict(path=relative, **spec))
    return manifest, dict(custody_commit=commit, phase_C_execution_commit=PHASE_C_COMMIT,
        source_files=bound, input_files=inputs, python=sys.version, platform=platform.platform(),
        production_scientific_imports=False, scientific_execution_started=False,
        scope='Post-C validation of a known fixed catalogue, not a new campaign or population sample.')


def derive_keys(manifest):
    """Read every primary row; no primitive, value, risk or solver evaluation."""
    grouped, raw_records, seen_files, state_by_row = {}, {}, set(), {}
    for relative in manifest['catalogue_files']:
        data = json.loads(safe_relative(relative).read_text())
        index, arm, service = data['index'], data['arm'], data['service']
        identity = (index, arm, service)
        if identity in seen_files or index not in (0, 1) or arm not in ARMS or service not in SERVICES:
            raise ValueError('Unexpected/duplicate primary catalogue identity')
        seen_files.add(identity)
        if F(float(data['alpha'])) != ALPHAS[index] or data['terminal_policy_unchanged'] is not True:
            raise ValueError('Risk or future-controller identity changed')
        rows = data['rows']
        if len(rows) != 144 or [r['row'] for r in rows] != list(range(144)):
            raise ValueError('Primary catalogue rows changed')
        for row in rows:
            state = [as_binary(row['x0']), as_binary(row['x1'])]
            action = as_binary(row['action'])
            state_row = (index, row['row'])
            state_identity = tuple(v[0] for v in state)
            if state_row in state_by_row and state_by_row[state_row] != state_identity:
                raise ValueError('The original common state differs across actions or services')
            state_by_row[state_row] = state_identity
            key_id = f"{index}:{row['row']}:{action[0]}"
            entry = dict(key_id=key_id, index=index, row=row['row'], alpha=str(ALPHAS[index]),
                         state_binary64=[v[0] for v in state], state_exact=[v[1] for v in state],
                         action_binary64=action[0], action_exact=action[1])
            if key_id not in grouped:
                grouped[key_id] = dict(entry, policies=[])
            if {k: grouped[key_id][k] for k in entry} != entry:
                raise ValueError('The same declared key has inconsistent states')
            policy = f'{arm}/{service}'
            grouped[key_id]['policies'].append(policy)
            raw_records[(index, row['row'], policy)] = dict(row, source_path=relative, key_id=key_id)
    if seen_files != set(itertools.product((0, 1), ARMS, SERVICES)):
        raise ValueError('All 96 primary catalogue files are required')
    if len(raw_records) != EXPECTED_ROWS:
        raise ValueError('Not every original primary record was retained')
    keys = sorted(grouped.values(), key=lambda r: (r['index'], r['row'], F(r['action_exact'])))
    for key in keys:
        key['policies'].sort()
    if tuple(sum(k['index'] == i for k in keys) for i in (0, 1)) != EXPECTED_KEYS:
        raise ValueError('The exact 492+491 original key catalogue changed')
    expected = json.loads((ROOT/KEYS_NAME).read_text())
    if keys != expected['keys'] or expected['primary_records'] != EXPECTED_ROWS:
        raise ValueError('Derived primary keys differ from prospectively frozen exact keys')
    references = {}
    ref = json.loads(safe_relative(manifest['reference_file']).read_text())
    if ref['shares_verified_terminal_compiler'] is not True:
        raise ValueError('The existing reference independence scope changed')
    for block in ref['records']:
        index = block['index']
        if F(float(block['alpha'])) != ALPHAS[index]:
            raise ValueError('Reference risk mismatch')
        for row in block['unique']:
            key_id = f"{index}:{row['row']}:{float(row['action']).hex()}"
            if key_id in references or key_id not in grouped:
                raise ValueError('Reference key mismatch or duplicate')
            if [float(v).hex() for v in row['state']] != grouped[key_id]['state_binary64']:
                raise ValueError('Reference state does not equal the original realized state')
            references[key_id] = row
    if set(references) != set(grouped):
        raise ValueError('Existing 983 reference keys are not exhausted')
    return keys, raw_records, references


def load_primitive_only():
    path = ROOT/'frozen108/code/independent94.py'
    tree = ast.parse(path.read_text())
    permitted = {'__future__', 'fractions', 'json', 'math', 'pathlib', 'time'}
    for node in ast.walk(tree):
        names = [v.name.split('.')[0] for v in node.names] if isinstance(node, ast.Import) else []
        if isinstance(node, ast.ImportFrom):
            names = [(node.module or '').split('.')[0]]
        if any(name not in permitted for name in names):
            raise ValueError('The supposedly independent primitive imports scientific production code')
    spec = importlib.util.spec_from_file_location('r119d_primitive_only', path)
    exact = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exact)
    return exact


def exact_avar(values, alpha):
    """Upper equal-mass tail with an exact possible split atom; no float sort."""
    values = list(values)
    tail_mass = len(values)*(1-alpha)
    if not values or not 0 <= alpha < 1:
        raise ValueError('Invalid exact AVaR data')
    remaining, total = tail_mass, F(0)
    for value in sorted(values, reverse=True):
        mass = min(F(1), remaining)
        total += mass*value
        remaining -= mass
        if remaining == 0:
            break
    if remaining != 0:
        raise ArithmeticError('Exact risk tail mass was not exhausted')
    return total/tail_mass


def check(condition, label, failures):
    if not condition:
        failures.append(label)
    return 1


def compatibility(observed, lower, upper):
    observed_lower, observed_upper = F(float(observed['lower'])), F(float(observed['upper']))
    return dict(observed_lower=observed_lower, observed_upper=observed_upper,
        overlap=observed_lower <= upper and lower <= observed_upper,
        production_contains_independent_enclosure=observed_lower <= lower and upper <= observed_upper,
        independent_contains_production_interval=lower <= observed_lower and observed_upper <= upper,
        interpretation='Interval overlap is compatibility only, not verification of every observed endpoint.')


def one_policy(exact, key, raw_records, reference, trace_path):
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    state, action, alpha = list(map(F, key['state_exact'])), F(key['action_exact']), F(key['alpha'])
    failures, checks, values, terminal_count = [], 0, [], 0
    max_gap, inferred_objective_calls, max_retained_fraction_bits = F(0), 0, 0
    trace_hash = hashlib.sha256()
    capacity = F(1, 8)+sum(state)/(8*len(state))
    checks += check(len(state) == 2 and all(0 <= v <= 1 for v in state), 'Original state domain', failures)
    checks += check(0 <= action <= capacity, 'Original feasible root action', failures)
    stage = exact.economic_S(state)+action*action+4*action**4
    # Separate exclusive trace file per key: a later failure cannot overwrite a
    # completed trace. The current failed file and all successful prefixes stay.
    with trace_path.open('xb') as raw_trace:
        with gzip.GzipFile(fileobj=raw_trace, mode='wb', filename='', mtime=0) as trace:
            for k in range(2*BINS+1):
                z = -R+R*F(k, BINS)
                terminal_state = exact.next_state(state, action, z)
                lo, hi, terminal_action = exact.terminal_bounds(terminal_state, alpha, steps=TERMINAL_STEPS)
                terminal_capacity = F(1, 8)+sum(terminal_state)/(8*len(terminal_state))
                polynomial = exact.polynomial_from_primitives(terminal_state, terminal_action)
                risk, left, right, eta = exact.tail_threshold(polynomial, alpha)
                reconstructed_hi = (exact.economic_S(terminal_state)+terminal_action**2
                                    +4*terminal_action**4+BETA*risk)
                gap = hi-lo
                checks += check(all(F(1, 32) <= v <= F(27, 32) for v in terminal_state), 'Original reachable terminal domain', failures)
                checks += check(0 <= terminal_action <= terminal_capacity, 'Independent terminal action feasible', failures)
                checks += check(polynomial[2] == 5, 'Exact original quadratic shock coefficient five', failures)
                checks += check(lo <= hi == reconstructed_hi, 'Independent primitive value and terminal bracket agree', failures)
                checks += check(0 <= gap <= TERMINAL_ALLOWANCE, 'Independent terminal gap no larger than unchanged allowance', failures)
                endpoint = 'zero' if terminal_action == 0 else 'capacity' if terminal_action == terminal_capacity else 'interior'
                inferred_objective_calls += 35 if endpoint == 'interior' else 3
                terminal_count += 1
                max_gap = max(max_gap, gap)
                values.append((lo, hi))
                fractions = [*terminal_state, terminal_action, lo, hi, *polynomial, risk, left, right, eta]
                max_retained_fraction_bits = max(max_retained_fraction_bits, *(max(abs(v.numerator).bit_length(), v.denominator.bit_length()) for v in fractions))
                record = dict(node=k, z=z, terminal_state=terminal_state, action=terminal_action,
                              lower=lo, upper=hi, polynomial=polynomial, risk=risk, tail=(left, right),
                              eta=eta, terminal_exit=endpoint, root_steps_requested=TERMINAL_STEPS)
                payload = packed(record)
                trace.write(payload)
                trace_hash.update(payload)
        raw_trace.flush()
        os.fsync(raw_trace.fileno())
    midpoint_lower = [values[2*j+1][0] for j in range(BINS)]
    # Do not deduplicate these endpoint atoms: every bin contributes two mass
    # 1/(2*BINS) values, so interior endpoints appear exactly twice.
    endpoint_upper = [values[k][1] for j in range(BINS) for k in (2*j, 2*j+2)]
    q_lower = stage+BETA*exact_avar(midpoint_lower, alpha)
    q_upper = stage+BETA*exact_avar(endpoint_upper, alpha)
    j_lower, j_upper = q_lower, q_upper+BETA*TERMINAL_ALLOWANCE
    checks += check(q_lower <= q_upper, 'Convex whole-support Q enclosure ordered', failures)
    checks += check(j_lower <= j_upper and j_upper-q_upper == BETA*TERMINAL_ALLOWANCE,
                    'Unchanged discounted terminal-policy allowance added exactly once', failures)
    comparisons = []
    for policy in key['policies']:
        observed = raw_records[(key['index'], key['row'], policy)]
        comp = compatibility(observed, j_lower, j_upper)
        checks += check(comp['overlap'], f'Compatibility with recorded service {policy}', failures)
        comparisons.append(dict(policy=policy, **comp))
    reference_comparison = compatibility(reference, j_lower, j_upper)
    checks += check(reference_comparison['overlap'], 'Compatibility with existing shared-compiler 1024-bin reference', failures)
    trace_sha256 = digest(trace_path)
    return dict(key_id=key['key_id'], index=key['index'], row=key['row'], status='failed' if failures else 'passed',
        state=state, action=action, alpha=alpha, policies=key['policies'], stage=stage,
        optimum_continuation_lower=q_lower, optimum_continuation_upper=q_upper,
        implemented_policy_lower=j_lower, implemented_policy_upper=j_upper,
        implemented_policy_allowance=BETA*TERMINAL_ALLOWANCE,
        whole_support_bins=BINS, terminal_root_steps=TERMINAL_STEPS,
        terminal_contexts=terminal_count, maximum_terminal_gap=max_gap,
        objective_gradient_calls_inferred_from_frozen_code=inferred_objective_calls,
        maximum_retained_fraction_bits=max_retained_fraction_bits,
        bit_length_scope='Only retained terminal Fraction values; not all arithmetic intermediates or a bit-operation count.',
        checks=checks, failures=failures,
        original_service_comparisons=comparisons, existing_reference_comparison=reference_comparison,
        trace=dict(path=f'primitive_traces/{trace_path.name}', compressed_bytes=trace_path.stat().st_size,
                   sha256=trace_sha256, uncompressed_jsonl_sha256=trace_hash.hexdigest()),
        policy_seconds=time.perf_counter()-start_wall, policy_cpu_seconds=time.process_time()-start_cpu,
        clock_scope='Solve, primitive trace close/hash and comparisons; result-log serialization remains in total process cost.')


def aggregate(keys, results, raw_records):
    by_key = {row['key_id']: row for row in results if 'implemented_policy_lower' in row}
    identities, means, contrasts = [], [], []
    complete = len(by_key) == sum(EXPECTED_KEYS)
    def interval(key_id):
        row = by_key[key_id]
        return F(row['implemented_policy_lower']), F(row['implemented_policy_upper'])
    for index in (0, 1):
        for arm in ARMS:
            pairs = []
            for left, right in itertools.combinations(SERVICES, 2):
                same = all(raw_records[(index, j, f'{arm}/{left}')]['key_id'] ==
                           raw_records[(index, j, f'{arm}/{right}')]['key_id'] for j in range(144))
                pairs.append(dict(left=left, right=right, identical_every_primary_state=same))
                identities.append(dict(index=index, arm=arm, **pairs[-1],
                    exact_mean_policy_difference='0' if same else None))
            if complete:
                for service in SERVICES:
                    ids = [raw_records[(index, j, f'{arm}/{service}')]['key_id'] for j in range(144)]
                    means.append(dict(index=index, alpha=ALPHAS[index], arm=arm, service=service,
                        lower=sum((interval(k)[0] for k in ids), F(0))/144,
                        upper=sum((interval(k)[1] for k in ids), F(0))/144))
        if complete:
            # All six services are retained. The 56 unique arm comparisons use
            # the prospectively fixed compiled-policy labels; exact identities
            # show when these also apply to every other service.
            for left, right in itertools.combinations(ARMS, 2):
                lower, upper, identical = F(0), F(0), 0
                for j in range(144):
                    a = raw_records[(index, j, f'{left}/compiled')]['key_id']
                    b = raw_records[(index, j, f'{right}/compiled')]['key_id']
                    if a == b:
                        identical += 1
                        continue
                    al, au = interval(a)
                    bl, bu = interval(b)
                    lower, upper = lower+al-bu, upper+au-bl
                lower, upper = lower/144, upper/144
                contrasts.append(dict(index=index, alpha=ALPHAS[index], left=left, right=right,
                    orientation='left original mean policy cost minus right', lower=lower, upper=upper,
                    identical_policy_states=identical,
                    sign='negative' if upper < 0 else 'positive' if lower > 0 else 'exact_zero' if lower == upper == 0 else 'contains_zero'))
    return dict(complete=complete, original_service_identity_cells=identities,
        all_96_arm_service_mean_intervals=means, all_56_arm_mean_contrasts=contrasts,
        primary_service_identity_all_true=all(v['identical_every_primary_state'] for v in identities),
        inference='Deterministic original-policy value intervals on the known 144-state catalogue per risk. No population inference, independent global regret optimum, or required favorable sign.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--custody-commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # This must fail outside the exception handler if an old attempt exists:
    # no failure receipt may be written into or overwrite that old attempt.
    args.output.mkdir(parents=True, exist_ok=False)
    started_unix, started_wall, started_cpu = time.time(), time.perf_counter(), time.process_time()
    results, global_failures = [], []
    try:
        with (args.output/'EVENTS119D.jsonl').open('xb') as events, (args.output/'POLICY_ENCLOSURES119D.jsonl').open('xb') as policy_log:
            append_record(events, dict(event='start', started_unix=started_unix, argv=sys.argv))
            manifest, provenance = bind_sources(args.custody_commit)
            keys, raw_records, references = derive_keys(manifest)
            provenance.update(started_unix=started_unix, fixed_keys=len(keys), primary_rows=len(raw_records),
                              input_binding_seconds=time.perf_counter()-started_wall)
            write_new(args.output/'PROVENANCE119D.json', provenance)
            append_record(events, dict(event='binding_passed', keys=len(keys), primary_rows=len(raw_records)))
            exact = load_primitive_only()
            (args.output/'primitive_traces').mkdir()
            for position, key in enumerate(keys):
                trace_path = args.output/'primitive_traces'/f'{position:04d}.jsonl.gz'
                before_wall, before_cpu = time.perf_counter(), time.process_time()
                append_record(events, dict(event='policy_start', position=position, key_id=key['key_id']))
                try:
                    row = one_policy(exact, key, raw_records, references[key['key_id']], trace_path)
                except Exception:
                    row = dict(key, status='failed',
                        exception=traceback.format_exc(), failures=['Exception; entire original key retained'],
                        policy_seconds=time.perf_counter()-before_wall,
                        policy_cpu_seconds=time.process_time()-before_cpu)
                    if trace_path.exists():
                        row['partial_trace'] = dict(path=f'primitive_traces/{trace_path.name}', bytes=trace_path.stat().st_size, sha256=digest(trace_path))
                results.append(row)
                append_record(policy_log, row)
                append_record(events, dict(event='policy_finished', position=position, key_id=key['key_id'],
                    status=row['status'], seconds=row['policy_seconds']))
                print(f"VALIDATION_D {position+1}/{len(keys)} {key['key_id']} {row['status']} {row['policy_seconds']:.6f}s", flush=True)
            aggregate_started = time.perf_counter()
            summary = aggregate(keys, results, raw_records)
            if not summary['complete'] or not summary['primary_service_identity_all_true']:
                global_failures.append('Incomplete independent enclosures or changed recorded service-policy identities')
            if len(results) != 983 or sum(r.get('terminal_contexts', 0) for r in results) != 126807:
                global_failures.append('The exact prospectively fixed exhaustive workload was not completed')
            if any(row['status'] != 'passed' for row in results):
                global_failures.append('One or more independent policy checks or compatibility checks failed')
            summary.update(status='failed' if global_failures else 'passed', failures=global_failures,
                policy_keys=len(results), passed_policy_keys=sum(row['status'] == 'passed' for row in results),
                primitive_contexts=sum(row.get('terminal_contexts', 0) for row in results),
                checks=sum(row.get('checks', 0) for row in results),
                phase_C_execution_commit=PHASE_C_COMMIT, custody_commit=args.custody_commit,
                total_policy_seconds=sum(row['policy_seconds'] for row in results),
                total_policy_cpu_seconds=sum(row['policy_cpu_seconds'] for row in results),
                aggregation_seconds=time.perf_counter()-aggregate_started,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                production_terminal_compiler_imported=False, competitive_timing_rerun=False,
                exact_terminal_controller_evaluation=False,
                implemented_future_policy_scope='Independent optimal V1 enclosure plus the unchanged proved beta*2^-20 allowance; not reconstruction of the deployed 40-step floating controller.',
                validation_cost_scope='Additional author-side numerical validation work, separate from all unchanged A/B/C acquisition and service costs.')
            write_new(args.output/'SUMMARY119D.json', summary)
            append_record(events, dict(event='complete', status=summary['status'], policies=len(results)))
        files = [dict(path=f.relative_to(args.output).as_posix(), bytes=f.stat().st_size, sha256=digest(f))
                 for f in sorted(args.output.rglob('*')) if f.is_file()]
        receipt = dict(status=summary['status'], custody_commit=args.custody_commit,
            started_unix=started_unix, ended_unix=time.time(), inside_process_seconds=time.perf_counter()-started_wall,
            cpu_seconds=time.process_time()-started_cpu, files=files,
            exact_finite_validation=True, competitive_timing_or_population_experiment=False,
            scientific_sign_is_not_a_pass_condition=True,
            process_cost_scope='All binding, independent numerical work, traces, logging, aggregation and receipt input hashing; external launcher records final serialization/exit overhead.')
        write_new(args.output/'EXECUTION119D.json', receipt)
        if summary['status'] != 'passed':
            raise ArithmeticError('Independent full-catalogue validation failed; all cases retained')
    except BaseException:
        failure = dict(status='failed', custody_commit=args.custody_commit, started_unix=started_unix,
            ended_unix=time.time(), exception=traceback.format_exc(), completed_policy_records=len(results),
            inside_process_seconds=time.perf_counter()-started_wall,
            scope='This failed attempt and its partial traces/logs remain immutable; no retry is performed by this program.')
        write_new(args.output/'FAILED119D.json', failure)
        raise


if __name__ == '__main__':
    main()
