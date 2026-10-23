"""Frozen R123 full-census economics, inference, work and adoption reporter.

Reads original saved execution only: no actor fitting, economic solver, state
draw, or clock rerun.  Every cell and prespecified comparison is retained.
Rational interval endpoints and the actual saved binary clocks remain exact.
Price menus are conditional measured-cost scenarios, not population adoption
tests, and no geometric advantage is called neural-exclusive.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import io
import json
import math
import time
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import common123 as common
import stats123 as stat

ROOT = common.ROOT
FIELDS = common.FIELDS
N = 32
TAU = F(1, 256)
OMEGA = F(1, 8192)
VOLUMES = (32, 256, 4096, 65536)
SCENARIOS = ('primary32', 'timing0', 'timing1', 'timing2')
COMPARATORS = ('same-actor-r122', 'quadratic-value-r122', 'online-r122')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact(value):
    if isinstance(value, float):
        require(math.isfinite(value), 'Nonfinite saved number')
    return F(value)


def cell(row):
    return tuple(row[k] for k in FIELDS)


def cell_dict(key):
    return dict(zip(FIELDS, key))


def identity(row):
    return cell(row) + (row['row'],)


def label(key):
    return '/'.join(map(str, key))


def average(values):
    values = list(values)
    require(bool(values), 'Empty arithmetic mean')
    return sum(map(exact, values), F(0))/len(values)


def sqrt_up(value, bits=64):
    value = exact(value)
    require(value >= 0, 'Negative square-root input')
    scale = 1 << bits
    floor = math.isqrt((value.numerator*scale*scale)//value.denominator)
    if F(floor*floor, scale*scale) < value:
        floor += 1
    return F(floor, scale)


def sign(lo, hi):
    return ('positive' if lo > 0 else 'negative' if hi < 0
            else 'identity' if lo == hi == 0 else 'unresolved')


class Inputs:
    def __init__(self):
        self.files = {}

    def bind(self, path):
        path = Path(path).resolve()
        rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        self.files[rel] = dict(path=rel, bytes=path.stat().st_size, sha256=common.digest(path))
        return path

    def read(self, path):
        return json.loads(self.bind(path).read_text())

    def rows(self, path):
        return common.rows(self.bind(path))

    def verify_unchanged(self):
        for name, item in self.files.items():
            path = ROOT/name if not Path(name).is_absolute() else Path(name)
            require(path.stat().st_size == item['bytes'] and common.digest(path) == item['sha256'],
                    'A report input changed during execution: '+name)
        return dict(files=len(self.files),all_before_after_hashes_equal=True)

    def stage(self, directory, bounds, outer=None):
        directory = Path(directory)
        receipt = self.read(directory/'EXECUTION123.json')
        require(receipt.get('status') == 'executed' and receipt.get('exit_code') == 0,
                'Required stage did not execute successfully: '+str(directory))
        require(receipt['source']['source_manifest_sha256'] == bounds['source_manifest_sha256'],
                'Stage source closure differs: '+str(directory))
        binding = receipt.get('boundaries', receipt)
        require(binding.get('source_commit') == bounds['source_commit'] and
                binding.get('state_commit') == bounds['state_commit'],
                'Stage source/state identity differs: '+str(directory))
        self.bind(directory/'START123.json')
        if outer is not None:
            launch = self.read(Path(outer)/'LAUNCH123.json')
            require(launch.get('status') == 'executed' and launch.get('exit_code') == 0,
                    'Required parent launcher did not succeed: '+str(outer))
            require(exact(launch['seconds']) >= exact(receipt['seconds']) >= 0,
                    'Actual parent clock must enclose child receipt')
            command = launch['command']
            require('--output' in command, 'Outer launcher omitted child output identity')
            output = Path(command[command.index('--output')+1])
            output = output if output.is_absolute() else ROOT/output
            require(output.resolve() == directory.resolve(), 'Outer launcher names another child output')
            stdout = Path(outer)/'stdout.log'
            require(common.digest(self.bind(stdout)) == launch['stdout_sha256'],
                    'Changed original launcher log')
            receipt = dict(receipt, outer_seconds=launch['seconds'],
                           outer_launch_path=str(Path(outer).relative_to(ROOT)),
                           interpreter_and_startup_included=True)
        return receipt


def save_rows(out, name, records, compressed=False, csv_also=False):
    """Save all rows with deterministic gzip headers and no clobbering."""
    records = list(records)
    path = Path(out)/(name+'.jsonl'+('.gz' if compressed else ''))
    with path.open('xb') as raw:
        if compressed:
            with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, filename='') as gz:
                for record in records:
                    gz.write((json.dumps(common.serial(record), sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode())
        else:
            for record in records:
                raw.write((json.dumps(common.serial(record), sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode())
    if csv_also:
        columns = sorted({key for record in records for key in record})
        with (Path(out)/(name+'.csv')).open('x', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\n')
            writer.writeheader()
            for record in records:
                r = common.serial(record)
                writer.writerow({k:json.dumps(v, sort_keys=True, separators=(',', ':'))
                                 if isinstance(v, (dict, list)) else v for k, v in r.items()})
    return dict(path=path.name, rows=len(records), sha256=common.digest(path), bytes=path.stat().st_size)


def unique(records, keyfn, description):
    result = {}
    for record in records:
        key = keyfn(record)
        require(key not in result, description+': duplicate '+str(key))
        result[key] = record
    return result


def action_key(index, state_hex, action_hex):
    return (index, tuple(state_hex), action_hex)


def validate_states(inputs, bounds):
    path = ROOT/'results123/states/states123.json'
    data = inputs.read(path)
    require(common.digest(path) == bounds['states_sha256'], 'Changed committed fresh states')
    require(data['source_commit'] == bounds['source_commit'], 'States do not follow the frozen source')
    states = unique(data['states'], lambda r:r['row'], 'Original states')
    require(set(states) == set(range(N)), 'Exactly 32 prespecified state rows required')
    for j, row in states.items():
        require(len(row['state']) == len(row['state_hex']) == len(row['integers']) == 2,
                'Original two-dimensional state required')
        require(row['state_hex'] == [float(v).hex() for v in row['state']], 'State hex mismatch')
        require(all(isinstance(z, int) and 0 <= z < 2**40 for z in row['integers']),
                'State entropy coordinates outside frozen dyadic grid')
        require(all(exact(x) == F(z, 2**40) for x,z in zip(row['state'], row['integers'])),
                'State values differ from committed entropy coordinates')
    inputs.bind(ROOT/'results123/states/entropy123.bin')
    return states


def compact_row(row):
    omit = {'multi_anchor_cases', 'support_attempts', 'baseline_actor_trace',
            'baseline_qualification_attempts', 'initial_support_certificates'}
    result = {k:v for k,v in row.items() if k not in omit}
    result['saved_support_action_hex'] = sorted({float(r['original_action']).hex()
                                               for r in row.get('initial_support_certificates', [])})
    result['saved_multi_anchor_case_count'] = len(row.get('multi_anchor_cases', []))
    result['saved_baseline_qualification_attempts'] = len(row.get('baseline_qualification_attempts', []))
    return result


def validate_records(inputs, directory, n, states, bounds, primary=None, repeat=None):
    expected = {k+(j,) for k in common.groups() for j in range(n)}
    result = {}
    for raw in inputs.rows(Path(directory)/'records123.jsonl.gz'):
        key = identity(raw)
        require(key in expected and key not in result, 'Undeclared or duplicate service row: '+str(key))
        row = compact_row(raw)
        k, j = key[:-1], key[-1]
        require(row['state_hex'] == states[j]['state_hex'], 'Service used another state')
        require([float(v).hex() for v in row['state']] == states[j]['state_hex'], 'Saved service state mismatch')
        require(exact(row['alpha']) == (F(1,2), F(3,4))[k[0]], 'Changed risk objective')
        require(row['source_commit'] == bounds['source_commit'] and row['state_commit'] == bounds['state_commit'],
                'Service uses another source or state identity')
        require(row['population_observation'] == (primary is None) and row['repeat'] == repeat,
                'Timing repetitions may not become population observations')
        for action, action_hex in (('action','action_hex'), ('baseline_action','baseline_action_hex')):
            require(float(row[action]).hex() == row[action_hex], 'Saved action hex mismatch')
            cap = F(1,8)+sum(map(exact, row['state']))/16
            require(F(0) <= exact(row[action]) <= cap, 'Original action infeasible')
        lo, hi = exact(row['complete_policy_lower']), exact(row['complete_policy_upper'])
        B = exact(row['original_optimum_lower'])
        require(row['qualified'] and lo <= hi and B <= hi, 'Returned service lacks valid qualification')
        require(F(0) <= exact(row['loss']) <= TAU and F(0) <= exact(row['width']) <= OMEGA,
                'Returned regret/width exceeds frozen requirement')
        require(exact(row['loss']) >= hi-B and exact(row['width']) >= hi-lo,
                'Outward saved qualification understates its actual endpoints')
        gain = exact(row['certified_policy_gain_lower'])
        changed = row['action_hex'] != row['baseline_action_hex']
        require(row['accepted_improvement'] == changed, 'Accepted/action identity mismatch')
        require(F(0) <= gain <= TAU and (gain > 0 if changed else gain == 0),
                'Gain certificate does not match strict acceptance/fallback')
        started, completed = row.get('new_risk_queries_started',0), row.get('new_risk_queries_completed',0)
        require(0 <= completed <= started <= 1, 'Undeclared new-query budget')
        if k[-1] != 'probe_fused':
            require(started == completed == 0, 'No-query service purchased extra information')
        if primary is not None:
            original = primary[key]
            invariant = ('action_hex','baseline_action_hex','accepted_improvement','certified_policy_gain_lower',
                         'qualified','loss','width','improvement_stop','candidate_algebra_attempts',
                         'new_risk_queries_started','new_risk_queries_completed')
            for field in invariant:
                require(row.get(field) == original.get(field), 'Saved clock changed policy/certificate: '+field+' '+str(key))
        result[key] = row
    require(set(result) == expected, 'Incomplete fixed catalogue: '+str(directory))
    return result


def validate_cohorts(inputs, directory, n):
    cohorts = unique(inputs.rows(Path(directory)/'cohorts123.jsonl'), cell, 'Complete cohorts')
    require(set(cohorts) == set(common.groups()), 'All 232 declared service cohorts required')
    for k, row in cohorts.items():
        require(row['n'] == row['records'] == n, 'Wrong actual cohort volume')
        require(exact(row['seconds']) >= exact(row['load_seconds']) >= 0, 'Cohort does not enclose cold load')
        model = common.model_path(k)
        if model is None:
            require(row['model_sha256'] is None and row['model_bytes'] == 0, 'Online service has no fitted actor')
        else:
            require(common.digest(model) == row['model_sha256'] and model.stat().st_size == row['model_bytes'],
                    'Cohort model differs from frozen actor')
    return cohorts


def independent_intersections(inputs, directory, states, bounds, primary):
    evaluations, levels, count = {}, {}, 0
    seen = set()
    for row in inputs.rows(Path(directory)/'values123.jsonl'):
        count += 1
        alpha = exact(row['alpha'])
        require(alpha in (F(1,2), F(3,4)), 'Independent risk objective differs')
        index = (F(1,2), F(3,4)).index(alpha)
        key = action_key(index, row['state_hex'], row['action_hex'])
        require(tuple(row['state_hex']) in {tuple(s['state_hex']) for s in states.values()},
                'Independent evaluation added/replaced a state')
        require(row['source_commit'] == bounds['source_commit'] and row['state_commit'] == bounds['state_commit'],
                'Independent source/state identity differs')
        require(float(row['action']).hex() == row['action_hex'], 'Independent action identity mismatch')
        bins = row['bins']
        require(bins in (32,128,256) and (key,bins) not in seen, 'Undeclared or repeated independent precision')
        seen.add((key,bins))
        data = {field:exact(row[field]) for field in ('q_lower','q_upper','j_lower','j_upper','optimum_lower')}
        require(data['q_lower'] <= data['q_upper'] and data['j_lower'] <= data['j_upper'],
                'Reversed original independent interval')
        require(data['optimum_lower'] <= data['q_upper'], 'Invalid independent optimum bound')
        if key not in evaluations:
            evaluations[key] = data
            levels[key] = []
        else:
            old = evaluations[key]
            for f in ('q_lower','j_lower','optimum_lower'):
                old[f] = max(old[f], data[f])
            for f in ('q_upper','j_upper'):
                old[f] = min(old[f], data[f])
        levels[key].append(bins)
        data = evaluations[key]
        require(data['q_lower'] <= data['q_upper'] and data['j_lower'] <= data['j_upper'],
                'Independent precision levels contradict; no favorable level selection allowed')
    needed = set()
    for key, row in primary.items():
        actions = [row['action_hex'],row['baseline_action_hex'],*row['saved_support_action_hex']]
        if row.get('raw_proposal_kept') is not None:
            actions.append(float(row['raw_proposal_kept']).hex())
        for a in actions:
            needed.add(action_key(key[0],row['state_hex'],a))
    require(set(evaluations) == needed, 'Independent original-economics action census differs')
    require(all(32 in level for level in levels.values()), 'Every action requires its fixed 32-bin evaluation')
    pooled = {}
    for (i, state, a), row in evaluations.items():
        key = (i,state)
        if key not in pooled:
            pooled[key] = dict(lower=row['optimum_lower'], upper=row['q_upper'])
        else:
            pooled[key]['lower'] = max(pooled[key]['lower'], row['optimum_lower'])
            pooled[key]['upper'] = min(pooled[key]['upper'], row['q_upper'])
    require(len(pooled) == len({(i,tuple(s['state_hex'])) for i in range(2) for s in states.values()}),
            'Missing independent risk/state optimum bounds')
    require(all(r['lower'] <= r['upper'] for r in pooled.values()), 'Pooled independent optimum interval empty')
    accepted = {key for key,row in primary.items() if row['accepted_improvement']}
    claim_path = Path(directory)/'claims123.jsonl'
    claim_rows = inputs.rows(claim_path) if claim_path.exists() else []
    require(claim_path.exists() or not accepted, 'Accepted actions require their independent claim file')
    claims = unique(claim_rows, lambda r:identity(r['identity']), 'Accepted independent claims')
    require(set(claims) == accepted, 'Every accepted action requires its independent claim ledger')
    for key, claim in claims.items():
        row = primary[key]
        require(claim['action_hex'] == row['action_hex'] and claim['baseline_action_hex'] == row['baseline_action_hex'],
                'Independent accepted-claim action mismatch')
        require(bool(claim['independently_confirmed']) ==
                bool(claim['stages'][-1]['production_gain_confirmed'] and claim['stages'][-1]['candidate_interval_contained']),
                'Independent claim status disagrees with final saved stage')
    return dict(values=evaluations, levels=levels, pooled=pooled, claims=claims,
                evaluations=count, distinct_actions=len(evaluations))


def value(data, row, action_hex=None):
    return data['independent']['values'][action_key(row['index'],row['state_hex'],action_hex or row['action_hex'])]


def paired(data, candidate, comparator, n=N):
    require(candidate[0] == comparator[0], 'Cross-objective economic contrast forbidden')
    pairs, identical = [], 0
    for j in range(n):
        a = data['primary'][candidate+(j,)]
        b = data['primary'][comparator+(j,)]
        if a['action_hex'] == b['action_hex']:
            lo = hi = F(0)
            identical += 1
        else:
            av, bv = value(data,a), value(data,b)
            lo, hi = bv['j_lower']-av['j_upper'], bv['j_upper']-av['j_lower']
        require(max(-TAU,lo) <= min(TAU,hi), 'Independent paired contrast contradicts qualification')
        pairs.append((lo,hi))
    return pairs, identical


def acquisition(inputs, clocks):
    path = ROOT/'provenance123/inherited_costs121/fit_and_acquisition121.jsonl'
    # This historical file intentionally retains its old string `loss` label.
    result = unique(inputs.rows(path), lambda r:(r['index'],r['budget'],r['arm'],r['loss']), 'Inherited acquisition')
    require(set(result) == {k for k in common.actors() if k[2] != 'online'},
            'All 56 unchanged learned-actor acquisition allocations required')
    for k in common.actors():
        if k[2] == 'online':
            result[k] = dict(complete_allocated_acquisition_seconds='0', no_fitted_artifact=True,
                             explanation='No fitted actor; every online query and service operation is charged in its measured fresh cohort.')
        row = result[k]
        require(exact(row['complete_allocated_acquisition_seconds']) >= 0, 'Negative inherited allocation')
        if k[2] != 'online':
            require(all(clocks[s][k+(m,)]['model_sha256'] == row['model_sha256']
                        for s in SCENARIOS for m in common.MODES),
                    'Historical acquisition charged to a different actor')
    return result


def load_data(args, inputs, bounds):
    states = validate_states(inputs,bounds)
    primary_receipt = inputs.stage(args.primary,bounds,ROOT/'results123/launch-primary')
    primary = validate_records(inputs,args.primary,N,states,bounds)
    require(primary_receipt['records'] == len(primary) == 7424 and primary_receipt['cohorts'] == 232,
            'Primary execution receipt does not match full census')
    require(primary_receipt['records_sha256'] == common.digest(args.primary/'records123.jsonl.gz'),
            'Changed primary record bytes')
    cohorts = {'primary32':validate_cohorts(inputs,args.primary,N)}
    receipts = {'primary32':primary_receipt}
    for repeat in range(3):
        name = 'timing'+str(repeat)
        directory = ROOT/'results123'/name
        receipt = inputs.stage(directory,bounds,ROOT/'results123'/('launch-'+name))
        clock_rows = validate_records(inputs,directory,16,states,bounds,primary,repeat)
        require(receipt['records'] == len(clock_rows) == 3712 and receipt['cohorts'] == 232,
                'Timing receipt does not match entire fixed half-sample census')
        require(receipt['records_sha256'] == common.digest(directory/'records123.jsonl.gz'), 'Changed timing records')
        cohorts[name] = validate_cohorts(inputs,directory,16)
        receipts[name] = receipt
    independent_receipt = inputs.stage(args.independent,bounds,ROOT/'results123/launch-independent')
    independent = independent_intersections(inputs,args.independent,states,bounds,primary)
    require(independent_receipt['distinct_actions'] == independent['distinct_actions'] and
            independent_receipt['evaluations'] == independent['evaluations'], 'Independent receipt/census mismatch')
    witness = args.independent/'original_terminal_witnesses123.jsonl.gz'
    require(common.digest(inputs.bind(witness)) == independent_receipt['original_witness_sha256'],
            'Changed independent original-terminal witness bytes')
    processes = {}
    for name in SCENARIOS:
        receipt = receipts[name]
        total = exact(receipt['outer_seconds'])
        measured = sum((exact(r['seconds']) for r in cohorts[name].values()),F(0))
        require(total >= measured, 'Negative whole-process common residual: '+name)
        processes[name] = dict(scenario=name,n=N if name=='primary32' else 16,
            actual_parent_process_seconds=total,inner_process_seconds=exact(receipt['seconds']),
            nonoverlapping_measured_cohort_seconds=measured,shared_process_residual_seconds=total-measured,
            interpreter_start_and_source_checks_measured=True,child_timing_processes_included=False,
            actual_research_rule='Count this whole process once; standalone allocations below cannot be summed as observed research cost.',
            standalone_rule='Charge this entire common residual once to each hypothetical separately deployed method.',
            max_rss_kib=receipt.get('peak_rss_kib'))
    return dict(states=states,primary=primary,independent=independent,clocks=cohorts,processes=processes,
                receipts=dict(receipts,independent=independent_receipt),acquisition=acquisition(inputs,cohorts),bounds=bounds)


def economics_and_statistics(data):
    groups, states, counters, safe, signed = [], [], [], [], []
    for k in common.groups():
        records = [data['primary'][k+(j,)] for j in range(N)]
        individual, own_pairs, gains = [], [], []
        operations = Counter()
        for j, row in enumerate(records):
            v = value(data,row)
            base = value(data,row,row['baseline_action_hex'])
            optimum = data['independent']['pooled'][k[0],tuple(row['state_hex'])]
            p_lo, p_hi = exact(row['complete_policy_lower']), exact(row['complete_policy_upper'])
            require(max(p_lo,v['j_lower']) <= min(p_hi,v['j_upper']), 'Independent and production policy intervals disjoint')
            require(v['q_upper'] >= optimum['lower'], 'Independent Q below its all-action lower bound')
            regret_lo = max(F(0), v['j_lower']-optimum['upper'])
            regret_hi = v['j_upper']-optimum['lower']
            require(regret_lo <= min(TAU,regret_hi), 'Independent policy regret conflicts with qualification')
            sq_error = max(F(0),v['q_upper']-optimum['lower'])  # mu=2.
            if row['action_hex'] == row['baseline_action_hex']:
                gain_lo = gain_hi = F(0)
            else:
                gain_lo, gain_hi = base['j_lower']-v['j_upper'], base['j_upper']-v['j_lower']
            g = exact(row['certified_policy_gain_lower'])
            own_pairs.append((gain_lo,gain_hi));gains.append(g)
            claim = data['independent']['claims'].get(k+(j,))
            raw_action = row.get('raw_proposal_kept')
            raw_hex = None if raw_action is None else float(raw_action).hex()
            raw_value = None if raw_hex is None else value(data,row,raw_hex)
            result = dict(**cell_dict(k),row=j,state_hex=row['state_hex'],action_hex=row['action_hex'],
                baseline_action_hex=row['baseline_action_hex'],accepted=row['accepted_improvement'],
                baseline_policy_lower=base['j_lower'],baseline_policy_upper=base['j_upper'],
                raw_proposal_action_hex=raw_hex,
                raw_proposal_policy_lower=None if raw_value is None else raw_value['j_lower'],
                raw_proposal_policy_upper=None if raw_value is None else raw_value['j_upper'],
                raw_proposal_regret_lower=None if raw_value is None else max(F(0),raw_value['j_lower']-optimum['upper']),
                raw_proposal_regret_upper=None if raw_value is None else raw_value['j_upper']-optimum['lower'],
                raw_proposal_not_assumed_qualified=True,
                original_q_lower=v['q_lower'],original_q_upper=v['q_upper'],
                original_policy_lower=v['j_lower'],original_policy_upper=v['j_upper'],
                independent_optimum_lower=optimum['lower'],independent_optimum_upper=optimum['upper'],
                independent_regret_lower=regret_lo,independent_regret_upper=regret_hi,
                theorem_intersected_regret_upper=min(TAU,regret_hi),
                independent_squared_action_error_upper=sq_error,
                theorem_intersected_squared_action_error_upper=min(TAU,sq_error),
                independent_action_error_upper=sqrt_up(sq_error),
                action_error_is_an_enclosure_not_exact_observed_error=True,
                raw_independent_gain_lower=gain_lo,raw_independent_gain_upper=gain_hi,
                certified_gain_lower=g,independent_gain_claim_confirmed=gain_lo>=g,
                production_candidate_interval_contains_independent=p_lo<=v['j_lower']<=v['j_upper']<=p_hi,
                independent_claim_status=None if claim is None else claim['independently_confirmed'],
                independent_bins=sorted(data['independent']['levels'][action_key(k[0],row['state_hex'],row['action_hex'])]),
                qualification=True)
            individual.append(result);states.append(result)
            operations.update(row.get('counts',{}))
        group = dict(**cell_dict(k),n=N,
            original_policy_mean_lower=average(r['original_policy_lower'] for r in individual),
            original_policy_mean_upper=average(r['original_policy_upper'] for r in individual),
            original_q_mean_lower=average(r['original_q_lower'] for r in individual),
            original_q_mean_upper=average(r['original_q_upper'] for r in individual),
            independent_mean_regret_lower=average(r['independent_regret_lower'] for r in individual),
            independent_mean_regret_upper=average(r['independent_regret_upper'] for r in individual),
            theorem_intersected_mean_regret_upper=average(r['theorem_intersected_regret_upper'] for r in individual),
            production_mean_regret_upper=average(exact(r['certified_regret_upper']) for r in records),
            independent_rms_action_error_upper=sqrt_up(average(r['independent_squared_action_error_upper'] for r in individual)),
            theorem_intersected_rms_action_error_upper=sqrt_up(average(r['theorem_intersected_squared_action_error_upper'] for r in individual)),
            changed_actions=sum(r['accepted_improvement'] for r in records),
            accepted_independently_confirmed=sum(r['accepted'] and r['independent_claim_status'] is True for r in individual),
            accepted_independently_unresolved=sum(r['accepted'] and r['independent_claim_status'] is False for r in individual),
            positive_certified_gains=sum(g>0 for g in gains),mean_certified_gain_lower=average(gains),
            candidate_algebra_attempts=sum(r.get('candidate_algebra_attempts',0) for r in records),
            candidate_refusals=sum(r.get('candidate_refusals',r.get('refused_candidate_bound_attempts',0)) for r in records),
            new_risk_queries_started=sum(r.get('new_risk_queries_started',0) for r in records),
            new_risk_queries_completed=sum(r.get('new_risk_queries_completed',0) for r in records),
            enhancement_numerical_failures=sum(bool(r.get('enhancement_numerical_failure')) for r in records),
            baseline_first_proposal_rejections=sum(bool(r.get('first_rejected')) for r in records),
            baseline_qualification_attempts=sum(r['saved_baseline_qualification_attempts'] for r in records),
            mean_paid_support_actions=average(len(r['saved_support_action_hex']) for r in records),
            acquisition_seconds=exact(data['acquisition'][k[:4]]['complete_allocated_acquisition_seconds']),
            stop_reasons=dict(sorted(Counter(r['improvement_stop'] for r in records).items())),
            same_acquired_actor_not_new_training=True)
        available_raw = [r for r in individual if r['raw_proposal_action_hex'] is not None]
        group.update(baseline_policy_mean_lower=average(r['baseline_policy_lower'] for r in individual),
                     baseline_policy_mean_upper=average(r['baseline_policy_upper'] for r in individual),
                     raw_proposal_available_rows=len(available_raw),
                     raw_proposal_unavailable_rows=N-len(available_raw),
                     raw_proposal_policy_mean_lower=None if len(available_raw)!=N else average(r['raw_proposal_policy_lower'] for r in individual),
                     raw_proposal_policy_mean_upper=None if len(available_raw)!=N else average(r['raw_proposal_policy_upper'] for r in individual),
                     raw_proposal_mean_regret_lower=None if len(available_raw)!=N else average(r['raw_proposal_regret_lower'] for r in individual),
                     raw_proposal_mean_regret_upper=None if len(available_raw)!=N else average(r['raw_proposal_regret_upper'] for r in individual),
                     incomplete_raw_proposal_means_are_not_conditionally_selected=True)
        groups.append(group)
        counters.append(dict(**cell_dict(k),n=N,operation_counts=dict(sorted(operations.items())),
            counter_events_are_not_floating_point_operation_counts=True,
            inherited_acquisition_operation_counts=data['acquisition'][k[:4]].get('label_operation_counts_if_standalone',{})))
        safe.append(dict(**cell_dict(k),**stat.safe_interval(own_pairs,gains)))
        for comparator in COMPARATORS:
            ref = (k[:4]+('r122',) if comparator=='same-actor-r122' else
                   (k[0],k[1] if k[1] else 5,'quadratic','value','r122') if comparator=='quadratic-value-r122' else
                   (k[0],0,'online','online','r122'))
            pairs, same = paired(data,k,ref)
            signed.append(dict(**cell_dict(k),comparator=comparator,comparator_key=ref,
                               **stat.signed_interval(pairs,k==ref,same)))
    require(len(groups)==len(safe)==232 and len(signed)==696 and len(states)==7424,
            'Declared reporting families incomplete')
    return groups,states,counters,safe,signed


def all_clocks(data):
    records, lookup = [], {}
    for s in SCENARIOS:
        p = data['processes'][s]
        for k in common.groups():
            cohort = data['clocks'][s][k]
            A = exact(data['acquisition'][k[:4]]['complete_allocated_acquisition_seconds'])
            T,L,H = exact(cohort['seconds']),exact(cohort['load_seconds']),p['shared_process_residual_seconds']
            row = dict(**cell_dict(k),scenario=s,n=cohort['n'],cold_load_seconds=L,
                complete_cohort_seconds=T,shared_process_residual_seconds=H,
                historical_complete_acquisition_seconds=A,fully_allocated_matching_cohort_seconds=A+T+H,
                actual_new_cohort_plus_allocated_common_seconds=T+H,
                descriptive_clock_not_population_sample=True,acquisition_clock_historical_not_remeasured=True,
                max_rss_kib=p['max_rss_kib'],model_sha256=cohort['model_sha256'])
            records.append(row);lookup[s,k]=row
    return records,lookup


def cost_at(clock, volume):
    return (clock['historical_complete_acquisition_seconds']+clock['shared_process_residual_seconds']+
            clock['cold_load_seconds']+(clock['complete_cohort_seconds']-clock['cold_load_seconds'])*volume/clock['n'])


def all_domain():
    return dict(empty=False,lower=F(0),lower_closed=True,upper=None,upper_closed=False)


def empty_domain():
    return dict(empty=True,lower=None,lower_closed=False,upper=None,upper_closed=False)


def price_domain(gain, extra):
    """Exact nonnegative prices p for gain - p*extra > 0."""
    gain,extra = exact(gain),exact(extra)
    if extra == 0:
        return all_domain() if gain>0 else empty_domain()
    if extra > 0:
        return dict(empty=False,lower=F(0),lower_closed=True,upper=gain/extra,upper_closed=False) if gain>0 else empty_domain()
    threshold = gain/extra
    return all_domain() if threshold<0 else dict(empty=False,lower=threshold,lower_closed=False,upper=None,upper_closed=False)


def intersection(a,b):
    if a['empty'] or b['empty']:
        return empty_domain()
    lo = max(a['lower'],b['lower'])
    lc = all(d['lower_closed'] for d in (a,b) if d['lower']==lo)
    finite = [d['upper'] for d in (a,b) if d['upper'] is not None]
    hi = min(finite) if finite else None
    hc = all(d['upper_closed'] for d in (a,b) if d['upper']==hi) if hi is not None else False
    if hi is not None and (lo>hi or (lo==hi and not(lc and hc))):
        return empty_domain()
    return dict(empty=False,lower=lo,lower_closed=lc,upper=hi,upper_closed=hc)


def price_tables(data, clocks):
    volumes,constraints,menus,intersections = [],[],[],[]
    keys = common.groups()
    neural = [k for k in keys if k[2]=='relu']
    contrasts = {}
    for k in neural:
        for b in keys:
            if b[0] == k[0] and b[2] != 'relu':
                pairs,_ = paired(data,k,b)
                contrasts[k,b] = (average(max(-TAU,lo) for lo,hi in pairs),
                                  average(min(TAU,hi) for lo,hi in pairs))
    for scenario in SCENARIOS:
        for volume in VOLUMES:
            costs = {}
            for k in keys:
                cost = cost_at(clocks[scenario,k],volume)
                costs[k] = cost
                volumes.append(dict(**cell_dict(k),scenario=scenario,volume=volume,
                    total_allocated_seconds=cost,seconds_per_decision=cost/volume,
                    actual_observed_cohort_volume=clocks[scenario,k]['n'],
                    scenario_extrapolation=volume!=clocks[scenario,k]['n'],
                    same_actor_reuse_assumed=True,new_deployment_execution=False))
            for k in neural:
                menu = [b for b in keys if b[0]==k[0] and b[2]!='relu']
                sufficient,possible = all_domain(),all_domain()
                for b in menu:
                    lo,hi = contrasts[k,b]
                    extra = (costs[k]-costs[b])/volume
                    low,high = price_domain(lo,extra),price_domain(hi,extra)
                    constraints.append(dict(candidate=cell_dict(k),comparator=cell_dict(b),scenario=scenario,volume=volume,
                        sample_gain_lower=lo,sample_gain_upper=hi,sample_gain_sign=sign(lo,hi),
                        extra_seconds_per_decision=extra,sufficient_price_domain=low,upper_not_ruled_out_domain=high,
                        policy_means_conditional_on_32_saved_states=True,statistical_adoption_claim=False,
                        equivalent_hinge_remains_conventional=b[2]=='hinge'))
                    sufficient,possible = intersection(sufficient,low),intersection(possible,high)
                menus.append(dict(**cell_dict(k),scenario=scenario,volume=volume,comparators=len(menu),
                    sufficient_price_domain=sufficient,upper_not_ruled_out_domain=possible,
                    menu='All conventional representations, both training losses, both budgets and all four modes at the same risk, including matched hinge and online.',
                    statistical_adoption_claim=False,neural_exclusive_advantage_claim=False,
                    upper_domain_is_not_a_jointly_attainable_positive_claim=True))
    lookup = {(r['scenario'],r['volume'],cell(r)):r for r in menus}
    for volume in VOLUMES:
        for k in neural:
            sufficient,possible = all_domain(),all_domain()
            for s in SCENARIOS[1:]:
                r = lookup[s,volume,k]
                sufficient = intersection(sufficient,r['sufficient_price_domain'])
                possible = intersection(possible,r['upper_not_ruled_out_domain'])
            intersections.append(dict(**cell_dict(k),volume=volume,clock_scenarios=list(SCENARIOS[1:]),
                sufficient_price_domain=sufficient,upper_not_ruled_out_domain=possible,
                descriptive_all_clock_intersection_not_future_hardware_guarantee=True))
    require(len(volumes)==3712 and len(constraints)==51200 and len(menus)==512 and len(intersections)==128,
            'Complete cost/adoption census failed')
    return volumes,constraints,menus,intersections


def research_ledger(inputs, data, output):
    inherited = ROOT/'provenance123/inherited_costs121'
    history = {}
    for path in sorted(inherited.iterdir()):
        if path.is_file():
            inputs.bind(path)
            history[path.name] = dict(sha256=common.digest(path),bytes=path.stat().st_size)
    receipts = []
    for path in sorted((ROOT/'results123').rglob('*123.json')):
        if path.name not in ('EXECUTION123.json','LAUNCH123.json','FAILURE123.json') or path.is_relative_to(output):
            continue
        row = inputs.read(path)
        receipts.append(dict(path=str(path.relative_to(ROOT)),kind=path.name,status=row.get('status'),
            seconds=row.get('seconds'),exit_code=row.get('exit_code'),sha256=common.digest(path),
            nested_clock_must_not_be_added_to_its_parent=True))
    known = sum((exact(r['outer_seconds']) for r in data['receipts'].values()),F(0))
    return dict(inherited_files=history,current_stage_receipts=receipts,
        selected_nonoverlapping_actual_outer_process_seconds=known,
        selected_outer_processes=list(SCENARIOS)+['independent'],
        selected_sum_is_not_total_research_cost=True,
        current_report_cost_recorded_by_its_own_execution_and_launcher=True,
        failed_and_partial_runs_retained=True,failed_runs_are_not_zero_cost=True,
        unknown_total_historical_research_cost=None,
        excluded_or_incomplete_categories=['historical stages without complete outer receipts','current source preparation and proof development',
                                          'author compilation and independent code audit','this reporter while its receipt is unfinished'],
        no_historical_refit_or_retiming=True,
        per_method_standalone_allocations_are_not_observed_total_research_cost=True)


def self_check():
    stat.self_check()
    require(len(common.actors())==58 and len(common.groups())==232, 'Frozen actor/service catalogue')
    require(len({k+(j,) for k in common.groups() for j in range(32)})==7424 and
            len({k+(j,) for k in common.groups() for j in range(16)})==3712,
            'Exact prospective primary/timing censuses')
    require(price_domain(F(1),F(2))['upper']==F(1,2), 'Positive-gain price ceiling')
    require(price_domain(F(-1),F(-2))['lower']==F(1,2), 'Negative-gain cheaper-service price floor')
    require(price_domain(0,0)['empty'], 'Identical gain and cost is not strict adoption')
    require(not price_domain(1,0)['empty'], 'Strict gain at equal cost')
    require(intersection(price_domain(1,2),price_domain(-1,-2))['empty'], 'Strict boundary coincidence is empty')
    for x in (F(0),F(1,9),F(2),F(7,17)):
        u = sqrt_up(x)
        require(u*u>=x and (u-F(1,2**64))**2<x if u>0 else x==0, 'Outward rational square root')
    return dict(status='passed',scope='statistical algebra, cost domains and rational endpoints only; no economic states or outcomes')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--primary',type=Path,default=ROOT/'results123/primary')
    parser.add_argument('--independent',type=Path,default=ROOT/'results123/independent')
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    out,tick,initial = common.start(args.output,'full-census-report-and-statistics')
    try:
        source = common.verify_source()
        bounds = common.boundaries()
        inputs = Inputs()
        inputs.bind(ROOT/'SOURCE_FREEZE123.json');inputs.bind(ROOT/'BOUNDARIES123.json')
        data = load_data(args,inputs,bounds)
        common.write(out/'RADIUS_WITNESS123.json',stat.radius_witness())
        groups,states,counters,safe,signed = economics_and_statistics(data)
        clocks,clock_lookup = all_clocks(data)
        volumes,constraints,menus,intersections = price_tables(data,clock_lookup)
        tables = []
        for name,rows,compressed,csv_also in (
            ('ECONOMICS123',groups,False,True),('STATE_ECONOMICS123',states,True,False),
            ('OPERATION_COUNTS123',counters,False,False),('STATS123',safe,False,True),
            ('SIGNED_COMPARISONS123',signed,False,True),('PROCESS_CLOCKS123',list(data['processes'].values()),False,True),
            ('COMPLETE_COSTS123',clocks,False,True),('DEPLOYMENT_VOLUMES123',volumes,True,False),
            ('PRICE_CONSTRAINTS123',constraints,True,False),('FULL_MENU_PRICE_DOMAINS123',menus,False,False),
            ('THREE_CLOCK_PRICE_INTERSECTIONS123',intersections,False,False)):
            tables.append(save_rows(out,name,rows,compressed,csv_also))
        ledger = research_ledger(inputs,data,out.resolve())
        common.write(out/'RESEARCH_LEDGER123.json',ledger)
        after_source = common.verify_source()
        after_bounds = common.boundaries()
        require(after_source == source and after_bounds == bounds, 'Source/state custody changed during reporting')
        after_inputs = inputs.verify_unchanged()
        common.write(out/'INPUTS123.json',dict(source=source,boundaries=bounds,files=inputs.files,
            before_after_source_and_state_identical=True,input_hash_recheck=after_inputs,
            independent_levels_combined_by_interval_intersection=True,no_economic_solver_or_new_state_draw=True))
        summary = dict(source=source,boundaries=bounds,status='complete-original-execution-reported',
            primary_records=len(data['primary']),primary_state_units=N,service_cells=len(groups),
            timing_records=3*232*16,timing_processes=3,timing_state_units_added=0,
            independent_distinct_actions=data['independent']['distinct_actions'],independent_evaluations=data['independent']['evaluations'],
            accepted_actions=sum(r['changed_actions'] for r in groups),
            accepted_independently_confirmed=sum(r['accepted_independently_confirmed'] for r in groups),
            accepted_independently_unresolved=sum(r['accepted_independently_unresolved'] for r in groups),
            enhancement_numerical_failures=sum(r['enhancement_numerical_failures'] for r in groups),
            own_incumbent_population_mean_intervals=len(safe),event_bounds=len(safe),signed_mean_intervals=len(signed),
            positive_own_incumbent_population_lower_bounds=sum(r['population_gain_lower']>0 for r in safe),
            signed_population_conclusions=dict(Counter(sign(r['population_gain_lower'],r['population_gain_upper']) for r in signed)),
            signed_sample_conclusions=dict(Counter(sign(r['sample_gain_lower'],r['sample_gain_upper']) for r in signed)),
            joint_population_failure_at_most=stat.JOINT_FAILURE,
            neural_full_menu_domains=len(menus),neural_nonempty_sufficient_domains=sum(not r['sufficient_price_domain']['empty'] for r in menus),
            neural_nonempty_upper_not_ruled_out_domains=sum(not r['upper_not_ruled_out_domain']['empty'] for r in menus),
            three_clock_domains=len(intersections),three_clock_nonempty_sufficient_domains=sum(not r['sufficient_price_domain']['empty'] for r in intersections),
            three_clock_nonempty_upper_not_ruled_out_domains=sum(not r['upper_not_ruled_out_domain']['empty'] for r in intersections),
            all_favorable_adverse_and_unresolved_rows_retained=True,
            neural_exclusive_advantage_inferred=False,price_menus_are_conditional_measured_cost_scenarios=True,
            tables=tables,reporting_seconds_before_final_receipt=time.perf_counter()-tick)
        common.write(out/'SUMMARY_REPORT123.json',summary)
        common.finish(out,tick,initial,source=source,boundaries=bounds,
            primary_records=7424,safe_intervals=232,event_bounds=232,signed_intervals=696,
            full_menu_constraints=51200,no_new_economic_sample=True,summary_sha256=common.digest(out/'SUMMARY_REPORT123.json'))
        print(json.dumps(common.serial(summary),sort_keys=True,indent=2),flush=True)
    except BaseException:
        common.failed(out,tick)
        raise


if __name__ == '__main__':
    main()
