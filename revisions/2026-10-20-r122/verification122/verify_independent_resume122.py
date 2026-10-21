"""Read-only composite gate for the separately published R122 continuation.

This supplements, and does not replace or alter, verify_package122.py.  It
performs no economic optimization, state draw, training or timing replication.
The published mathematical reader's completed checks are linked to exact raw
meshes; this reader independently checks custody, deterministic request order,
native outcomes, new-work clocks/counters and canonical full-trace equality.
"""
from __future__ import annotations

import argparse
import datetime as dt
from fractions import Fraction as Q
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import zlib

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
RREL = str(ROOT.relative_to(REPO))
F = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
D = 'a3323b6f557315ea91b536637419ef6fd7984b61'
I = '1f19410305c707716135defd91d6644d70657d84'
M = '796c5f2badf68b051ac6c144884c0e61b87faf5e'
FREEZE_SHA = 'eba26439a799392b7553d06fea5f17828c8988b9f72f4e049058771985ac8b0f'
STATE_SHA = '25dc1cdd876a1dcd9f38e867db79d073ea9f2bde3e95b324a1f6a0a1e7303405'
PRIMARY_SHA = '94fc7537e5020e464118c64076c8f6ace5ff3dd6d77b1e15d35dc3f2712e5044'
FORENSIC_SHA = '58a899a4516a5df99ad712d5cb0fe94b699042424b055070acc19fe7d68e7ddd'
SOURCE_PINS = {
    'verification122/resume_independent122.py': '32b7582c4f459851407bde3df24ae82a6c87f5ceaff34d606bba282b48b0d3a4',
    'verification122/validate_cached_witness122.py': 'ff4eade48c8f04f737a4c44847d0f801a267a2a7f4bb330b8defe070dc05585f',
    'verification122/test_resume_independent122.py': '157c01d46dcbced69e71347b6330427c1383cffc96b52e66b5302e6e03489a03',
    'provenance122/RESUME_INDEPENDENT_PROTOCOL122.md': '1c288e36a240e1389955baf9b7eece506b49bc687ab3ae6e35e11fe272971e4c',
}
EQUAL_OUTPUTS = (
    'POLICY_EVALUATIONS122.jsonl', 'BEST_POLICY_BOUNDS122.jsonl',
    'CLAIM_CHECKS122.jsonl', 'COMPARISONS122.jsonl',
    'ALGEBRA_AUDIT122.json', 'INPUTS122.json',
)
FIELDS = ('index', 'row', 'budget', 'arm', 'loss', 'service')
FRACTION_FIELDS = ('q_lower', 'q_upper', 'j_lower', 'j_upper', 'optimum_lower',
                  'all_action_anchor', 'all_action_gradient', 'all_action_minimizer',
                  'risk_bin_mass', 'future_controller_allowance_added_exactly_once')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def plain(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    return value


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(plain(value), stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def exact_clock(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError('An actual elapsed clock must be a finite nonnegative number')
    return Q(value)


def policy_key(row, field='action'):
    value = row[field]
    if value is None:
        return None
    return (tuple(row['state_hex']), float(value).hex(), float(row['alpha']).hex())


def saved_key(row):
    return (tuple(row['state_hex']), row['action_hex'], float(row['alpha']).hex())


def key_id(key):
    return hashlib.sha256(json.dumps(key, separators=(',', ':')).encode()).hexdigest()


class Verification:
    def __init__(self, args):
        self.args = args
        self.assertions = 0
        self.inputs = {}
        self.outer_jobs = {}
        self.source_summaries = []
        self.cache_summaries = []
        self.relocations = set()
        self.completed = []

    def check(self, condition, message):
        self.assertions += 1
        if not condition:
            raise AssertionError(message)

    def locate(self, value):
        """Resolve an explicitly saved R122/repository-relative path after relocation."""
        p = Path(value)
        if p.is_absolute():
            if p.is_relative_to(REPO):
                result = p.resolve()
            else:
                marker = '/' + RREL + '/'
                self.check(marker in str(p), 'Absolute saved path has no exact R122 relocation anchor')
                result = (ROOT / str(p).split(marker, 1)[1]).resolve()
                self.relocations.add((str(p), str(result.relative_to(REPO))))
        elif str(p) == RREL or str(p).startswith(RREL + '/'):
            result = (REPO / p).resolve()
        else:
            result = (ROOT / p).resolve()
        self.check(result.is_relative_to(REPO), 'Evidence path escapes the repository')
        return result

    def rel(self, value):
        p = Path(value).resolve()
        self.check(p.is_relative_to(REPO), 'Bound path escapes the repository')
        return str(p.relative_to(REPO))

    def bind(self, value):
        p = Path(value).resolve()
        name = self.rel(p)
        self.check(p.is_file() and not Path(value).is_symlink(), 'Required ordinary evidence file missing: ' + name)
        if name not in self.inputs:
            self.inputs[name] = {'path': name, 'bytes': p.stat().st_size, 'sha256': sha(p)}
        else:
            self.check(p.stat().st_size == self.inputs[name]['bytes'], 'Bound file size changed during verification')
        return p

    def read(self, value):
        return json.loads(self.bind(value).read_text())

    def rows(self, value):
        with self.bind(value).open() as stream:
            result = []
            for line in stream:
                self.check(line.endswith('\n') and bool(line.strip()), 'Incomplete or empty native JSONL record')
                result.append(json.loads(line))
            return result

    def digest(self, value):
        p = self.bind(value)
        return self.inputs[self.rel(p)]['sha256']

    def git(self, *args):
        env = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0')
        return subprocess.check_output(['git', *args], cwd=REPO, env=env)

    def git_source(self, commit, path):
        p = self.bind(path)
        raw = p.read_bytes()
        self.check(self.git('show', commit + ':' + self.rel(p)) == raw,
                   'Native source differs from immutable Git identity: ' + self.rel(p))
        return {'path': self.rel(p), 'bytes': len(raw), 'sha256': self.digest(p), 'git_blob': blob(raw)}

    def flag(self, command, flag):
        self.check(command.count(flag) == 1, 'Command must contain exactly one ' + flag)
        i = command.index(flag)
        self.check(i + 1 < len(command), 'Missing command argument after ' + flag)
        return command[i + 1]

    def outer(self, directory, mode, code, inner_seconds, cache=None, segment=None):
        outer = self.read(directory / 'OUTER_EXECUTION122.json')
        self.check(outer['exit_code'] == code and outer['status'] == ('executed' if code == 0 else 'failed'),
                   'Actual outer outcome differs from declared continuation outcome')
        self.check(outer.get('error') is None and outer['all_partial_outputs_retained'] is True,
                   'Continuation launch lacks ordinary preserved terminal evidence')
        self.check(self.locate(outer['child_output']) == directory, 'Outer launcher binds another output directory')
        wall = exact_clock(outer['outer_seconds'])
        self.check(wall >= exact_clock(inner_seconds), 'Outer launcher does not enclose the saved inner clock')
        command = outer['command']
        self.check(len(command) >= 2 and self.locate(command[1]) == ROOT / 'verification122/resume_independent122.py',
                   'Unexpected continuation launcher child program')
        self.check(self.flag(command, '--mode') == mode, 'Unexpected continuation mode')
        for flag, expected in (('--resume-commit', self.R), ('--repair-commit', I), ('--source-commit', F)):
            self.check(self.flag(command, flag) == expected, 'Continuation command source differs: ' + flag)
        self.check(self.locate(self.flag(command, '--primary')) == self.args.primary,
                   'Continuation command changed primary inputs')
        self.check(self.locate(self.flag(command, '--output')) == directory,
                   'Continuation command changed output destination')
        for flag, expected in (('--cache', cache), ('--segment', segment)):
            if expected is None:
                self.check(flag not in command, 'Unexpected continuation source argument: ' + flag)
            else:
                self.check(self.locate(self.flag(command, flag)) == expected, 'Continuation source path differs: ' + flag)
        launch_dir = self.locate(outer['receipt_directory'])
        launch = self.read(launch_dir / 'LAUNCH122.json')
        self.check(launch == outer and self.digest(launch_dir / 'LAUNCH122.json') == self.digest(directory / 'OUTER_EXECUTION122.json'),
                   'External launcher receipt and native mirror differ')
        start = self.read(launch_dir / 'START_LAUNCH122.json')
        self.check(all(outer[k] == value for k, value in start.items()), 'Launch start record changed')
        self.bind(launch_dir / 'stdout.log')
        self.check(outer['ended_unix'] >= outer['started_unix'], 'Observed launcher UTC clock order differs')
        self.check(set(outer['threads'].values()) == {'1'}, 'Launcher thread pins differ')
        name = self.rel(launch_dir / 'LAUNCH122.json')
        self.check(name not in self.outer_jobs, 'One launcher was assigned to two continuation stages')
        self.outer_jobs[name] = {'path': name, 'sha256': self.digest(launch_dir / 'LAUNCH122.json'),
                                 'mode': mode, 'exit_code': code, 'outer_seconds_exact': str(wall),
                                 'child_output': self.rel(directory)}
        return outer

    def sources(self):
        a = self.args
        self.check(a.source_commit == F and a.state_commit == D, 'Verifier must use the original F/D identities')
        publication = self.read(a.resume_publication)
        self.R = publication['commit']
        self.check(publication['status'] == 'executed' and publication['source_commit_F'] == F,
                   'Continuation has no actual pre-execution publication')
        self.check(len(self.R) == 40 and all(c in '0123456789abcdef' for c in self.R), 'Continuation commit must be a full SHA')
        tree = self.git('rev-parse', self.R + '^{tree}').decode().strip()
        self.check(publication['tree'] == tree, 'Published continuation tree differs from actual Git')
        listed = {self.rel(self.locate(r['path'])): r for r in publication['source_files']}
        self.check(len(listed) == len(publication['source_files']) == 4, 'Exactly four reviewed continuation sources are required')
        self.R_sources = []
        for relative, expected in SOURCE_PINS.items():
            path = ROOT / relative
            self.check(self.digest(path) == expected, 'Continuation source differs from the fresh reviewed identity')
            actual = self.git_source(self.R, path)
            record = listed.pop(self.rel(path), None)
            self.check(record is not None and all(record[k] == actual[k] for k in ('bytes', 'sha256', 'git_blob')),
                       'Published continuation source row differs from actual bytes/blob')
            self.R_sources.append(actual)
        self.check(not listed, 'Unexpected continuation source row')
        self.R_tree = tree
        freeze = self.read(ROOT / 'SOURCE_FREEZE122.json')
        self.check(self.digest(ROOT / 'SOURCE_FREEZE122.json') == FREEZE_SHA and freeze['source_file_count'] == 243,
                   'Original F source manifest differs')
        self.git_source(F, ROOT / 'SOURCE_FREEZE122.json')
        self.check(len(freeze['scientific_files']) == 243 and freeze['inherited_actor_commit'] == M,
                   'Original frozen closure/actor identity differs')
        for relative, expected in freeze['scientific_files'].items():
            self.check(self.digest(REPO / relative) == expected, 'A frozen scientific file changed: ' + relative)
        state = ROOT / 'results122/states-attempt01/STATE_MANIFEST122.json'
        self.check(self.digest(state) == STATE_SHA, 'Original state manifest differs')
        self.git_source(D, state)
        ipub = self.read(ROOT / 'provenance122/INDEPENDENT_SCHEMA_PUBLICATION122.json')
        self.check(ipub['status'] == 'executed' and ipub['commit'] == I and ipub['tree'] == '6f92dd077a1b27986d22c264603ddb1cf4f07667',
                   'Independent schema repair identity differs')
        for record in ipub['source_files']:
            actual = self.git_source(I, self.locate(record['path']))
            self.check(all(actual[k] == record[k] for k in ('bytes', 'sha256', 'git_blob')), 'I source record differs')
        self.git_source(I, ROOT / 'results122/independent-attempt01/FAILURE122.json')
        self.check(self.digest(a.primary / 'records122.jsonl') == PRIMARY_SHA, 'Fixed primary records changed')
        self.primary = []
        self.actions = {}
        with (a.primary / 'records122.jsonl').open() as stream:
            for line in stream:
                row = json.loads(line)
                self.check(row['source_commit'] == F and row['population_observation'] is True,
                           'Primary source/independent-observation status changed')
                item = {k: row[k] for k in FIELDS}
                for name in ('accepted_improvement', 'certified_policy_gain_lower', 'complete_policy_lower', 'complete_policy_upper'):
                    item[name] = row[name]
                for name in ('action', 'baseline_action', 'raw_proposal_kept'):
                    key = policy_key(row, name)
                    item[name] = key
                    if key is not None:
                        value = {'state': row['state'], 'action': row[name], 'alpha': row['alpha']}
                        if key in self.actions:
                            self.check(self.actions[key] == value, 'A policy key represents conflicting native values')
                        self.actions[key] = value
                self.primary.append(item)
        self.check(len(self.primary) == 5568 and len(self.actions) == 865,
                   'Original primary/unique-action census changed')
        self.check(len({tuple(r[k] for k in FIELDS) for r in self.primary}) == 5568,
                   'Duplicate original primary identity')
        self.check(sum(r['accepted_improvement'] for r in self.primary) == 824, 'Original accepted-action census changed')
        self.completed.append('immutable_sources_and_primary')

    def cache_chain(self, final_directory):
        chain = []
        seen = set()
        directory = final_directory
        child = None
        while True:
            self.check(directory.is_relative_to(ROOT) and directory not in seen, 'Cache ancestry escapes R122 or cycles')
            seen.add(directory)
            index = self.read(directory / 'CACHE_INDEX122.json')
            receipt = self.read(directory / 'CACHE_VALIDATION122.json')
            if child is not None:
                self.check(self.digest(directory / 'CACHE_INDEX122.json') == child['index_sha256'] and
                           self.digest(directory / 'CACHE_VALIDATION122.json') == child['receipt_sha256'],
                           'Cache ancestry hash binding differs')
            self.check(receipt['status'] == 'validated' and receipt['resume_commit'] == self.R and
                       receipt['index_sha256'] == self.digest(directory / 'CACHE_INDEX122.json'),
                       'Cache has no matching completed source-bound validation')
            self.check(receipt['source_hashes'] == SOURCE_PINS and receipt['validator_sha256'] == SOURCE_PINS['verification122/validate_cached_witness122.py'],
                       'Cache mathematical validation source differs')
            self.check(index['resume_commit'] == self.R and index['source_commit'] == F and index['state_commit'] == D and
                       index['repair_commit'] == I and index['primary_sha256'] == PRIMARY_SHA,
                       'Cache F/D/I/R/primary identity differs')
            self.check(index['new_population_states'] == index['new_primary_decisions'] == 0,
                       'Cache claims new primary observations')
            self.check(receipt['original_policy_optimization_calls'] == receipt['terminal_bisection_optimization_steps_performed'] == 0,
                       'Cache validation performed original optimization')
            self.check(receipt['elapsed_nested_in_outer_launcher'] is True,
                       'Cache validation inner clock was made additive')
            self.check(index['evaluation_count'] == len(index['entries']) and
                       len({(r['key_id'], r['bins']) for r in index['entries']}) == len(index['entries']),
                       'Cache evaluation census has duplicates or omissions')
            for row in index['entries']:
                key = saved_key(row)
                self.check(key in self.actions and key_id(key) == row['key_id'], 'Cache contains an undeclared original action')
                self.check(all(row[k] == self.actions[key][k] for k in ('state', 'action', 'alpha')),
                           'Cache changed original action/state/risk bits')
                self.check(type(row['bins']) is int and row['bins'] in (64, 128, 256, 512) and
                           row['terminal_contexts'] == 2 * row['bins'] + 1 and row['terminal_steps'] == 32,
                           'Cache changed the original independent precision rule')
                exact_clock(row['seconds'])
                for field in FRACTION_FIELDS:
                    Q(row[field])
            historical = sum((Q(r['seconds']) for r in index['entries']), Q(0))
            self.check(Q(index['historical_evaluation_seconds']) == historical, 'Cache historical clock sum differs')
            chain.append((directory, index, receipt))
            child = index['previous_cache']
            if child is None:
                break
            directory = self.locate(child['path'])
        chain.reverse()
        self.chain = chain
        prior = []
        previous_sources = []
        previous_directory = None
        for position, (directory, index, receipt) in enumerate(chain):
            self.check(index['entries'][:len(prior)] == prior and index['sources'][:-1] == previous_sources and
                       len(index['sources']) == position + 1, 'An immutable cache prefix was altered or source extension omitted')
            source = index['sources'][-1]
            segment = self.locate(source['directory'])
            self.check(source['first_index'] == len(prior) and source['last_index_exclusive'] == len(index['entries']) and
                       source['complete_fresh_evaluations'] == len(index['entries']) - len(prior) > 0,
                       'Cache source ranges are not a complete disjoint partition')
            self.check(receipt['previous_policies_reused_without_revalidating_math'] == len(prior) and
                       receipt['new_policies_mathematically_validated'] == source['complete_fresh_evaluations'],
                       'Cache new/reused mathematical-validation census differs')
            counts = receipt['exact_checks_this_extension']
            fresh = index['entries'][len(prior):]
            self.check(counts['policies_validated'] == len(fresh) and counts['terminal_contexts'] == sum(r['terminal_contexts'] for r in fresh),
                       'Cache validation lacks a complete exact mesh census')
            self.check(counts['represented_terminal_bisections'] == 32 * counts['interior_terminal_cells_checked'] and
                       counts['exact_assertions'] > counts['terminal_contexts'], 'Mathematical validation counters are inconsistent')
            self.check(receipt['trailing_witness_records_retained_not_reused'] == source['trailing_witness_records_not_reused'],
                       'Unused witness diagnostics differ')
            self.source_files(segment, source['files'])
            native = self.rows(segment / 'POLICY_EVALUATIONS122.jsonl')
            self.check(native == index['entries'], 'Native evaluation rows differ from the validated cache')
            self.outer(directory, 'cache', 0, receipt['seconds'], previous_directory, segment)
            start = self.read(directory / 'START_CACHE_VALIDATION122.json')
            self.check(start['source_hashes'] == SOURCE_PINS and start['resume_commit'] == self.R and
                       start['source_commit'] == F and start['repair_commit'] == I, 'Cache start identity differs')
            self.check(not (directory / 'FAILURE_CACHE_VALIDATION122.json').exists(), 'Completed cache has a failure receipt')
            if position == 0:
                self.initial(segment, source, native)
                self.check(index['completed_reference'] is None, 'Interrupted original attempt was presented as complete')
            else:
                meta = self.segment(segment, source, fresh, prior, previous_directory)
                expected = str(segment.relative_to(ROOT)) if meta['status'] == 'segment_complete_not_canonical' else None
                self.check(index['completed_reference'] == expected, 'Cache completed-reference selection differs')
                self.check((position == len(chain) - 1) == (expected is not None),
                           'Only the last validated segment may be naturally complete')
            self.cache_summaries.append({'directory': self.rel(directory), 'index_sha256': self.digest(directory / 'CACHE_INDEX122.json'),
                                        'validation_sha256': self.digest(directory / 'CACHE_VALIDATION122.json'),
                                        'old_evaluations_reused': len(prior), 'new_complete_evaluations_validated': len(fresh),
                                        'exact_validation_assertions': counts['exact_assertions']})
            prior = index['entries']
            previous_sources = index['sources']
            previous_directory = directory
        self.index = chain[-1][1]
        self.check(self.index['completed_reference'] is not None and len(chain) >= 2,
                   'Canonical completion needs the validated interrupted prefix and a naturally completed continuation')
        self.completed.append('full_cache_chain_and_native_outcomes')

    def source_files(self, directory, records):
        actual = set()
        for path in directory.rglob('*'):
            self.check(not path.is_symlink(), 'Native continuation stage contains a symlink')
            if path.is_file():
                actual.add(str(path.relative_to(directory)))
        self.check(len(records) == len({r['path'] for r in records}) and actual == {r['path'] for r in records},
                   'Cache native-source fingerprint does not cover the exact file census')
        for record in records:
            path = (directory / record['path']).resolve()
            self.check(path.is_relative_to(directory), 'Native source fingerprint path escapes its stage')
            self.bind(path)
            self.check(path.stat().st_size == record['bytes'] and self.digest(path) == record['sha256'],
                       'A cache-bound native byte changed')

    def initial(self, directory, source, native):
        self.check(directory == ROOT / 'results122/independent-attempt02', 'First cache uses another original attempt')
        path = directory / 'INTERRUPTION_FORENSIC122.json'
        forensic = self.read(path)
        self.check(self.digest(path) == FORENSIC_SHA and forensic['status'] == 'interrupted_without_terminal_receipt',
                   'Original independent interruption forensic changed')
        self.check(forensic['source_commit'] == F and forensic['state_commit'] == D and forensic['independent_repair_commit'] == I and
                   forensic['primary_sha256'] == PRIMARY_SHA, 'Interrupted attempt scientific identity differs')
        self.check(forensic['actual_parent_exit_code'] is None and forensic['actual_parent_wall_seconds'] is None,
                   'Unknown interrupted parent exit or full duration was invented')
        for name in ('EXECUTION122.json', 'FAILURE122.json', 'OUTER_EXECUTION122.json', 'INDEPENDENT_SCHEMA_ADAPTER122.json'):
            self.check(not (directory / name).exists(), 'Interrupted original attempt gained a terminal receipt')
        self.check(not (ROOT / 'results122/launch-independent-attempt02/LAUNCH122.json').exists(),
                   'Interrupted original launcher gained a terminal receipt')
        self.check(len(native) == forensic['completed_policy_rows'] == forensic['completed_policy_unique_keys'] == 716 and
                   forensic['completed_claim_rows'] == 0, 'Interrupted original evaluation census differs')
        self.check([(saved_key(r), r['bins']) for r in native] == [(k, 64) for k in sorted(self.actions)[:716]],
                   'Interrupted saved evaluations are not the original ordered 716-policy prefix')
        launch_directory = ROOT / 'results122/launch-independent-attempt02'
        forensic_paths = set()
        for record in forensic['native_files']:
            path = self.locate(record['path'])
            forensic_paths.add(path)
            self.check((path.is_relative_to(directory) or path.parent == launch_directory) and path.stat().st_size == record['bytes'] and
                       self.digest(path) == record['sha256'], 'Interrupted forensic native file differs')
        native_paths = {p.resolve() for p in directory.rglob('*') if p.is_file() and p.name != 'INTERRUPTION_FORENSIC122.json'}
        expected_launch_paths = {launch_directory / 'START_LAUNCH122.json', launch_directory / 'stdout.log'}
        self.check(forensic_paths == native_paths | expected_launch_paths and
                   {p.resolve() for p in launch_directory.rglob('*') if p.is_file()} == expected_launch_paths,
                   'Interrupted forensic must cover exactly the native partial stage and its two nonterminal launcher files')
        self.check(len(forensic['native_files']) == 21 and sum(r['bytes'] for r in forensic['native_files']) == forensic['native_bytes'],
                   'Interrupted forensic file/byte census differs')
        self.initial_lower = sum((Q(r['seconds']) for r in native), Q(0))
        self.check(self.initial_lower == Q(forensic['completed_evaluation_seconds_lower']) == Q(92977404913995, 68719476736),
                   'Interrupted completed-evaluation cost lower bound differs')
        self.check(source['allow_unsealed_prefix'] is True, 'Original unsealed prefix lost its explicit scope')

    def resume_meta(self, directory, expected_status, mode, cache_directory, reused, fresh):
        meta = self.read(directory / 'RESUME_SEGMENT122.json')
        self.check(meta['status'] in expected_status and meta['mode'] == mode,
                   'Unexpected source-bound continuation outcome')
        self.check(meta['resume_commit'] == self.R and meta['source_commit'] == F and meta['state_commit'] == D and
                   meta['repair_commit'] == I and meta['primary_sha256'] == PRIMARY_SHA and meta['source_hashes'] == SOURCE_PINS,
                   'Continuation actual source identity differs')
        self.check(self.locate(meta['cache_directory']) == cache_directory and
                   meta['cache_index_sha256'] == self.digest(cache_directory / 'CACHE_INDEX122.json') and
                   meta['cache_validation_sha256'] == self.digest(cache_directory / 'CACHE_VALIDATION122.json'),
                   'Continuation binds another validated cache')
        self.check(meta['source_F_I_files_changed'] is False and meta['raw_F_I_receipts_unchanged_and_retained'] is True,
                   'Continuation altered or discarded native F/I outputs')
        self.check(meta['new_population_states'] == meta['new_primary_decisions'] == meta['new_timing_replicates'] == 0,
                   'Continuation changed the scientific sample or timing design')
        self.check(meta['historical_seconds_not_charged_as_current_execution'] is True and
                   meta['elapsed_nested_in_outer_launcher_not_additive'] is True,
                   'Historical or nested continuation clocks were made additive')
        self.check(meta['reused_policy_calls'] == len(reused) and meta['fresh_policy_calls'] == len(fresh) and
                   meta['delivered_unique_evaluation_count'] == len(reused) + len(fresh), 'Actual reused/fresh evaluation counts differ')
        self.check(Q(meta['reused_historical_evaluation_seconds']) == sum((Q(r['seconds']) for r in reused), Q(0)),
                   'Reused historical clock provenance differs')
        self.check(meta['checkpoint_new_primitive_seconds_threshold'] == 300 and meta['checkpoint_checked_before_next_uncached_request_only'] is True,
                   'Prospective complete-evaluation checkpoint rule changed')
        self.check(meta['current_exact121_counts_scope'] == 'actual fresh primitives and ordinary module source checks only; no replay inflation',
                   'Current-process rational counter scope changed')
        expected_scope = 'aggregate unique original evaluations represented across validated retained and new native evidence; not current-process new calls'
        self.check(meta['frozen_actual_independent_evaluations_field_scope'] == expected_scope,
                   'Frozen aggregate evaluation field was relabeled as fresh work')
        attempts = meta['fresh_primitive_call_attempts']
        self.check(meta['fresh_primitive_call_attempt_count'] == len(attempts) == len(fresh) == len(meta['fresh_calls']),
                   'A fresh failed/extra call was omitted from a usable continuation source')
        accumulated = 0.0
        for row, actual, attempt in zip(fresh, meta['fresh_calls'], attempts):
            self.check(accumulated < 300, 'New primitive request began after the predeclared boundary budget')
            self.check((actual['key_id'], actual['bins'], actual['terminal_contexts']) ==
                       (row['key_id'], row['bins'], row['terminal_contexts']), 'Fresh call identity differs from the completed native suffix')
            self.check(attempt['status'] == 'returned_complete_result' and (attempt['key_id'], attempt['bins']) ==
                       (row['key_id'], row['bins']) and attempt['actual_new_call_seconds'] == actual['actual_new_call_seconds'],
                       'Fresh primitive call did not return a recorded complete result')
            self.check(exact_clock(actual['actual_new_call_seconds']) >= exact_clock(row['seconds']),
                       'Outer primitive-call clock does not enclose its native evaluation clock')
            accumulated += actual['actual_new_call_seconds']
        self.check(meta['fresh_primitive_seconds'] == accumulated and meta['fresh_terminal_contexts'] == sum(r['terminal_contexts'] for r in fresh),
                   'Fresh primitive work totals differ')
        self.check(exact_clock(meta['seconds']) >= exact_clock(meta['fresh_primitive_seconds']),
                   'Continuation inner clock does not enclose its new primitive work')
        repair = self.read(directory / 'INDEPENDENT_SCHEMA_ADAPTER122.json')
        self.check(repair['source_commit_F'] == F and repair['independent_adapter_commit'] == I and
                   repair['primary_sha256'] == PRIMARY_SHA and repair['adapter_sha256'] == self.digest(ROOT / 'verification122/independent_schema_adapter122.py'),
                   'Actual I adapter source or input identity differs')
        self.check(repair['checks']['native_rows_checked'] == 5568 and repair['checks']['accepted_numeric_candidate_equalities'] == 824,
                   'Continuation I schema validation omitted original rows')
        self.check(repair['elapsed_nested_in_outer_launcher_not_additive'] is True and
                   exact_clock(meta['seconds']) >= exact_clock(repair['elapsed_seconds']), 'I clock enclosure/scope differs')
        source = self.read(directory / 'VERIFIED_SOURCE122.json')
        self.check(source['source_commit'] == F and source['manifest_sha256'] == FREEZE_SHA,
                   'Native continuation source gate differs')
        inputs = self.read(directory / 'INPUTS122.json')
        self.check(inputs['primary_sha256'] == PRIMARY_SHA and inputs['unique_initial_policy_keys'] == 865 and
                   inputs['base_bins'] == 64 and inputs['accepted_claim_ladder'] == [64, 128, 256, 512] and
                   inputs['terminal_iterations_if_interior'] == 32, 'Frozen independent request design changed')
        return meta, repair

    def segment(self, directory, source, fresh, reused, cache_directory):
        self.check(source['allow_unsealed_prefix'] is False and source['trailing_witness_records_not_reused'] == 0,
                   'A continuation segment contains an unverified unsealed/trailing suffix')
        meta, repair = self.resume_meta(directory, {'planned_checkpoint', 'segment_complete_not_canonical'},
                                        'segment', cache_directory, reused, fresh)
        self.check(meta['fresh_only_noncanonical_trace'] is True and meta['replayed_witness_meshes'] == meta['replayed_witness_contexts'] == 0 and
                   meta['canonical_finalizer_new_economic_calls'] is None and meta['final_reference'] is None and
                   meta['canonical_exact_equalities'] == {}, 'Noncanonical segment was presented as a full replay')
        checkpoint = meta['status'] == 'planned_checkpoint'
        code = 75 if checkpoint else 0
        self.check(meta['exit_code'] == code and meta['planned_checkpoint_not_scientific_success_or_unexpected_failure'] == checkpoint,
                   'Checkpoint native status scope differs')
        if checkpoint:
            failure = self.read(directory / 'FAILURE122.json')
            self.check(failure['status'] == 'failed' and 'PlannedCheckpoint' in failure['traceback'] and
                       'PlannedCheckpoint' in meta['error_or_checkpoint_traceback'], 'Planned checkpoint lost its unchanged native failure evidence')
            self.check(not (directory / 'EXECUTION122.json').exists() and repair['status'] == 'failed' and
                       meta['fresh_primitive_seconds'] >= 300, 'Nonterminal planned checkpoint was marked complete or triggered early')
        else:
            execution = self.read(directory / 'EXECUTION122.json')
            self.check(execution['status'] == 'executed' and execution['exit_code'] == 0 and repair['status'] == 'executed' and
                       meta['error_or_checkpoint_traceback'] is None and not (directory / 'FAILURE122.json').exists(),
                       'Natural completed segment lacks successful native F/I receipts')
            self.check(execution['actual_independent_evaluations'] == len(reused) + len(fresh),
                       'Natural completed segment aggregate evaluation count differs')
        self.outer(directory, 'segment', code, meta['seconds'], cache_directory)
        self.source_summaries.append({'directory': self.rel(directory), 'status': meta['status'], 'reused': len(reused),
                                     'fresh': len(fresh), 'fresh_seconds_exact': str(Q(meta['fresh_primitive_seconds'])),
                                     'source_trace_is_fresh_only': True})
        return meta

    def stream_witness(self, directory, allow_unsealed, diagnostics):
        sealed = self.rows(directory / 'SEALED_WITNESS_PARTS122.jsonl')
        names = [r['path'] for r in sealed]
        self.check(len(names) == len(set(names)), 'Duplicate sealed witness part')
        parts = sorted((directory / 'terminal_witnesses122').glob('part*.jsonl.gz'))
        self.check([p.name for p in parts] == [f'part{n:05d}.jsonl.gz' for n in range(len(parts))] and
                   len(parts) == len(sealed) + int(allow_unsealed), 'Witness sealed/unsealed part census differs')
        self.check(names == [str(p.relative_to(directory)) for p in parts[:len(sealed)]], 'Sealed witness part order differs')
        if not allow_unsealed:
            manifest = self.read(directory / 'WITNESS_MANIFEST122.json')
            self.check(manifest['parts'] == sealed and manifest['no_record_omissions'] is True and
                       manifest['segment_seals_after_complete_policy_evaluation'] is True, 'Full witness manifest differs from actual seals')
        total = 0
        for position, path in enumerate(parts):
            path = self.bind(path)
            is_sealed = position < len(sealed)
            if is_sealed:
                record = sealed[position]
                self.check(path.stat().st_size == record['bytes'] and self.digest(path) == record['sha256'], 'Sealed witness byte identity differs')
            decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
            pending = b''
            sequence = 0
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(65536), b''):
                    pending += decoder.decompress(block)
                    while b'\n' in pending:
                        line, pending = pending.split(b'\n', 1)
                        self.check(bool(line), 'Empty witness record')
                        row = json.loads(line)
                        self.check(row['sequence'] == sequence, 'Witness per-part sequence differs')
                        sequence += 1
                        total += 1
                        yield row
            self.check(not decoder.unused_data, 'Unexpected extra gzip members or bytes')
            if is_sealed:
                self.check(decoder.eof and not pending, 'Sealed gzip lacks its complete CRC/footer or final line')
            diagnostics.append({'path': path, 'sealed': is_sealed, 'gzip_footer_validated': decoder.eof,
                                'complete_records': sequence, 'incomplete_unterminated_bytes': len(pending)})
        if not allow_unsealed:
            self.check(manifest['records'] == total, 'Full witness manifest record census differs')

    def witness_composition(self, canonical):
        canonical_diagnostics = []
        target = self.stream_witness(canonical, False, canonical_diagnostics)
        total = 0
        represented_bisections = 0
        for n, source in enumerate(self.index['sources']):
            directory = self.locate(source['directory'])
            entries = self.index['entries'][source['first_index']:source['last_index_exclusive']]
            diagnostics = []
            original = self.stream_witness(directory, source['allow_unsealed_prefix'], diagnostics)
            contexts = interiors = supports = 0
            for row in entries:
                for node in range(row['terminal_contexts']):
                    try:
                        old = next(original)
                        new = next(target)
                    except StopIteration:
                        raise AssertionError('Canonical/source witness lacks a complete cached mesh')
                    self.check(old['key_id'] == new['key_id'] == row['key_id'] and old['node'] == new['node'] == node,
                               'Canonical witness policy/node order differs from validated original requests')
                    old_numeric = dict(old)
                    new_numeric = dict(new)
                    del old_numeric['sequence']
                    del new_numeric['sequence']
                    self.check(old_numeric == new_numeric, 'Canonical witness differs beyond allowed per-part sequence renumbering')
                    self.check(old['terminal_bisections_executed'] in (0, 32), 'Unexpected original terminal bisection count')
                    contexts += 1
                    interiors += int(old['terminal_bisections_executed'] == 32)
                    supports += int(old['midpoint'])
                    represented_bisections += old['terminal_bisections_executed']
                    total += 1
            trailing = sum(1 for _ in original)
            self.check(trailing == source['trailing_witness_records_not_reused'], 'Unused original witness prefix diagnostic changed')
            saved_diagnostics = source['witness_diagnostics']
            self.check(len(saved_diagnostics) == len(diagnostics), 'Cache witness part diagnostics differ')
            for saved, actual in zip(saved_diagnostics, diagnostics):
                self.check(self.locate(saved['path']) == actual['path'] and all(saved[k] == actual[k] for k in
                           ('sealed', 'gzip_footer_validated', 'complete_records', 'incomplete_unterminated_bytes')),
                           'Cache witness sealing/trailing diagnostics differ from fresh readback')
            validation_counts = self.chain[n][2]['exact_checks_this_extension']
            self.check(validation_counts['terminal_contexts'] == contexts and validation_counts['interior_terminal_cells_checked'] == interiors and
                       validation_counts['represented_terminal_bisections'] == 32 * interiors, 'Validated mesh/bisection census differs from exact raw trace')
            if n > 0 and (directory / 'EXECUTION122.json').exists():
                counts = {'executed_assertions': 2 + 5 * len(entries) + 7 * contexts + 2 * supports,
                          'unique_original_policy_evaluations': len(entries), 'terminal_contexts': contexts,
                          'actual_terminal_bisection_iterations': 32 * interiors,
                          'independent_state_gradient_supports': supports, 'exact_finite_tail_sorts': 2 * len(entries)}
                if interiors:
                    counts['interior_terminal_contexts'] = interiors
                if contexts - interiors:
                    counts['boundary_terminal_contexts'] = contexts - interiors
                execution = self.read(directory / 'EXECUTION122.json')
                self.check(execution['counts'] == counts, 'Natural segment current-process counters were inflated by historical reuse')
        try:
            next(target)
        except StopIteration:
            pass
        else:
            raise AssertionError('Canonical trace contains witnesses outside the complete declared evaluation sequence')
        self.check(total == sum(r['terminal_contexts'] for r in self.index['entries']), 'Composite canonical witness census differs')
        self.witness_records = total
        self.represented_bisections = represented_bisections
        self.completed.append('every_canonical_witness_equals_validated_native_mesh')

    def deterministic_schedule(self, canonical):
        entries = self.index['entries']
        claims = self.rows(canonical / 'CLAIM_CHECKS122.jsonl')
        cursor = 0
        cache = {}
        best = {}
        expected_claims = []

        def evaluate(key, bins):
            nonlocal cursor
            pair = (key_id(key), bins)
            if pair in cache:
                return
            self.check(cursor < len(entries), 'Frozen deterministic schedule requires an absent evaluation')
            row = entries[cursor]
            self.check((row['key_id'], row['bins']) == pair and saved_key(row) == key,
                       'Actual original evaluation order differs from the unchanged deterministic F request schedule')
            cursor += 1
            cache[pair] = row
            if key not in best:
                best[key] = dict(row)
            else:
                previous = best[key]
                for field in ('q_lower', 'j_lower', 'optimum_lower'):
                    previous[field] = str(max(Q(previous[field]), Q(row[field])))
                for field in ('q_upper', 'j_upper'):
                    previous[field] = str(min(Q(previous[field]), Q(row[field])))
                previous['bins'] = max(previous['bins'], bins)
                self.check(Q(previous['q_lower']) <= Q(previous['q_upper']) and Q(previous['j_lower']) <= Q(previous['j_upper']),
                           'Replayed unchanged independent mesh intersections contradict')

        for key in sorted(self.actions):
            evaluate(key, 64)
        for row in sorted(self.primary, key=lambda r: tuple(r[k] for k in FIELDS)):
            if not row['accepted_improvement']:
                continue
            attempts = []
            for bins in (64, 128, 256, 512):
                evaluate(row['baseline_action'], bins)
                evaluate(row['action'], bins)
                old, new = best[row['baseline_action']], best[row['action']]
                claimed = Q(row['certified_policy_gain_lower'])
                checked = {
                    'gain_confirmed': Q(old['j_lower']) - Q(new['j_upper']) >= claimed,
                    'positive_gain_confirmed': Q(old['j_lower']) - Q(new['j_upper']) > 0,
                    'candidate_interval_contained': Q(new['j_lower']) >= Q(row['complete_policy_lower']) and Q(new['j_upper']) <= Q(row['complete_policy_upper']),
                    'candidate_interval_compatible': max(Q(new['j_lower']), Q(row['complete_policy_lower'])) <= min(Q(new['j_upper']), Q(row['complete_policy_upper'])),
                    'independent_gain_lower': str(Q(old['j_lower']) - Q(new['j_upper'])),
                    'independent_gain_upper': str(Q(old['j_upper']) - Q(new['j_lower'])),
                    'claimed_gain_lower': str(claimed), 'baseline_bins': old['bins'], 'candidate_bins': new['bins'],
                }
                attempts.append({'requested_bins': bins, **checked})
                self.check(checked['candidate_interval_compatible'], 'Original claim ladder produces incompatible intervals')
                if checked['gain_confirmed'] and checked['candidate_interval_contained']:
                    break
            expected_claims.append({'identity': [row[k] for k in FIELDS], 'attempts': attempts,
                                    'unresolved_after_fixed_ladder': not (checked['gain_confirmed'] and checked['candidate_interval_contained'])})
        self.check(cursor == len(entries) and claims == expected_claims and len(claims) == 824,
                   'Actual complete claim ladder differs from the unchanged deterministic schedule')
        self.check(self.rows(canonical / 'BEST_POLICY_BOUNDS122.jsonl') == [best[k] for k in sorted(best)],
                   'Native best-policy rows differ from exact unchanged bound intersections')
        self.ladder_time_unresolved = sum(r['unresolved_after_fixed_ladder'] for r in claims)
        self.accepted_unresolved = 0
        self.accepted_confirmed = 0
        self.accepted_contained = 0
        # Later claims can refine shared policies.  The final native census is
        # therefore recomputed from the final intersections, not from earlier
        # per-claim stopping records.
        for row in self.primary:
            if not row['accepted_improvement']:
                continue
            old, new = best[row['baseline_action']], best[row['action']]
            same = row['baseline_action'] == row['action']
            gain = Q(0) if same else Q(old['j_lower']) - Q(new['j_upper'])
            confirmed = same or gain >= Q(row['certified_policy_gain_lower'])
            contained = Q(new['j_lower']) >= Q(row['complete_policy_lower']) and Q(new['j_upper']) <= Q(row['complete_policy_upper'])
            self.accepted_confirmed += confirmed
            self.accepted_contained += contained
            self.accepted_unresolved += not (confirmed and contained)
        self.completed.append('unchanged_complete_request_and_precision_schedule')

    def finalizer(self):
        canonical = self.args.independent
        preliminary = self.read(canonical / 'RESUME_SEGMENT122.json')
        self.check(preliminary['status'] == 'canonical_complete' and preliminary['mode'] == 'finalize',
                   'Only a completed canonical cache-only finalizer can be used')
        final_cache = self.locate(preliminary['cache_directory'])
        self.cache_chain(final_cache)
        entries = self.index['entries']
        meta, repair = self.resume_meta(canonical, {'canonical_complete'}, 'finalize', final_cache, entries, [])
        self.check(meta['exit_code'] == 0 and repair['status'] == 'executed' and meta['error_or_checkpoint_traceback'] is None and
                   not (canonical / 'FAILURE122.json').exists(), 'Canonical finalizer did not finish successfully')
        self.check(meta['canonical_finalizer_new_economic_calls'] == meta['fresh_policy_calls'] == meta['fresh_primitive_call_attempt_count'] == 0 and
                   meta['fresh_primitive_seconds'] == 0 and meta['fresh_terminal_contexts'] == 0,
                   'Cache-only finalizer performed fresh economic work')
        self.check(meta['replayed_witness_meshes'] == len(entries) and
                   meta['replayed_witness_contexts'] == sum(r['terminal_contexts'] for r in entries) and
                   meta['fresh_only_noncanonical_trace'] is False and meta['planned_checkpoint_not_scientific_success_or_unexpected_failure'] is False,
                   'Canonical complete trace/replay scope differs')
        reference = self.locate(self.index['completed_reference'])
        self.check(self.locate(meta['final_reference']) == reference and set(meta['canonical_exact_equalities']) == set(EQUAL_OUTPUTS),
                   'Canonical completion uses another natural reference or equality family')
        for name in EQUAL_OUTPUTS:
            saved = meta['canonical_exact_equalities'][name]
            self.check(self.bind(canonical / name).read_bytes() == self.bind(reference / name).read_bytes(),
                       'Canonical native result differs from its naturally completed source: ' + name)
            self.check(saved['exact_bytes_equal'] is True and saved['sha256'] == self.digest(canonical / name) ==
                       saved['reference_sha256'] == self.digest(reference / name), 'Canonical exact-equality receipt differs')
        self.check(self.rows(canonical / 'POLICY_EVALUATIONS122.jsonl') == entries,
                   'Canonical evaluation rows differ from the complete mathematically validated cache')
        execution = self.read(canonical / 'EXECUTION122.json')
        self.check(execution['status'] == 'executed' and execution['exit_code'] == 0 and execution['actual_independent_evaluations'] == len(entries) and
                   execution['primary_rows'] == 5568 and execution['unique_policy_keys'] == 865 and execution['accepted_primary_decisions'] == 824,
                   'Canonical native aggregate evaluation census differs')
        self.check(execution['counts'] == {'executed_assertions': 2},
                   'Finalizer fabricated fresh primitive/assertion counters instead of the two unchanged source checks')
        self.outer(canonical, 'finalize', 0, meta['seconds'], final_cache)
        self.witness_composition(canonical)
        self.deterministic_schedule(canonical)
        self.check(execution['accepted_joint_checks_unresolved'] == self.accepted_unresolved and
                   execution['accepted_gain_claims_independently_confirmed'] == self.accepted_confirmed and
                   execution['accepted_candidate_intervals_independently_contained'] == self.accepted_contained,
                   'Canonical final accepted-claim census differs from the completed bound intersections')
        self.completed.append('zero_new_work_canonical_finalizer')

    def stable_inputs(self):
        for record in self.inputs.values():
            path = REPO / record['path']
            self.check(path.stat().st_size == record['bytes'] and sha(path) == record['sha256'],
                       'An input changed while the read-only composite verification was running')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-commit', default=F)
    parser.add_argument('--state-commit', default=D)
    parser.add_argument('--resume-publication', required=True, type=Path)
    parser.add_argument('--primary', required=True, type=Path)
    parser.add_argument('--independent', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    for name in ('resume_publication', 'primary', 'independent', 'output'):
        setattr(args, name, getattr(args, name).resolve())
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    verifier = Verification(args)
    write(args.output / 'START_RESUME_VERIFICATION122.json', {
        'argv': sys.argv, 'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'verifier_sha256': sha(Path(__file__)), 'new_economic_calls': 0,
        'scope': 'Additive read-only composition gate; unchanged ac5656 package verifier remains separately required.',
    })
    try:
        verifier.sources()
        verifier.finalizer()
        verifier.stable_inputs()
        write(args.output / 'INPUTS_RESUME_VERIFICATION122.json', {
            'files': sorted(verifier.inputs.values(), key=lambda r: r['path']),
            'saved_absolute_path_relocations': [{'original': a, 'repo_relative': b} for a, b in sorted(verifier.relocations)],
            'scope': 'Every exact source, cache chain, original/segment/finalizer native record, complete witness and launcher read by this gate.',
        })
        known_outer = sum((Q(r['outer_seconds_exact']) for r in verifier.outer_jobs.values()), Q(0))
        result = {
            'status': 'verified', 'source_commit_F': F, 'state_commit_D': D, 'actor_commit_M': M,
            'independent_schema_commit_I': I, 'resume_commit_R': verifier.R, 'resume_tree': verifier.R_tree,
            'resume_sources': verifier.R_sources, 'verifier_sha256': sha(Path(__file__)),
            'completed_stages': verifier.completed, 'assertions': verifier.assertions,
            'primary_sha256': PRIMARY_SHA, 'canonical_independent_directory': verifier.rel(args.independent),
            'canonical_resume_receipt_sha256': verifier.digest(args.independent / 'RESUME_SEGMENT122.json'),
            'input_manifest_sha256': sha(args.output / 'INPUTS_RESUME_VERIFICATION122.json'),
            'cache_validations': verifier.cache_summaries, 'native_continuation_segments': verifier.source_summaries,
            'original_interrupted_evaluations': 716, 'unique_original_policy_keys': 865,
            'total_distinct_original_evaluations_represented': len(verifier.index['entries']),
            'actual_new_original_evaluations_across_segments': len(verifier.index['entries']) - 716,
            'canonical_witness_records': verifier.witness_records,
            'historically_represented_terminal_bisections': verifier.represented_bisections,
            'accepted_claims': 824, 'accepted_joint_checks_unresolved': verifier.accepted_unresolved,
            'accepted_gain_claims_independently_confirmed': verifier.accepted_confirmed,
            'accepted_candidate_intervals_independently_contained': verifier.accepted_contained,
            'per_claim_ladder_time_unresolved_before_possible_shared_policy_refinements': verifier.ladder_time_unresolved,
            'canonical_finalizer_fresh_original_economic_calls': 0,
            'exact_numeric_output_equalities': list(EQUAL_OUTPUTS),
            'outer_jobs': sorted(verifier.outer_jobs.values(), key=lambda r: r['path']),
            'observed_used_continuation_outer_job_seconds': str(known_outer),
            'interrupted_completed_evaluation_seconds_lower': str(verifier.initial_lower),
            'used_independent_composition_work_seconds_lower': str(known_outer + verifier.initial_lower),
            'used_independent_composition_full_exact_seconds': None,
            'cost_scope': 'Used cache validations, native continuation segments and canonical finalizer outer clocks once, plus original completed-evaluation lower bound. Excludes this verification, earlier schema failures, unused attempts, publication and other research work; the separate whole-study ledger includes those. Historical replayed seconds and nested F/I clocks are not added.',
            'original_interrupted_parent_duration_and_exit_remain_unknown': True,
            'shared_host_timings_not_dedicated_hardware_benchmark': True,
            'frozen_scientific_files_changed': False, 'new_states': 0, 'new_training': 0,
            'new_economic_evaluations_by_this_verifier': 0, 'new_timing_processes': 0,
            'source_specific_CI_success_asserted': False,
            'unchanged_package_verifier_still_required': True,
            'elapsed_seconds': time.perf_counter() - started,
        }
        result['assertions'] = verifier.assertions
        result['elapsed_seconds'] = time.perf_counter() - started
        write(args.output / 'VERIFICATION_RESUME122.json', result)
        print(json.dumps({k: result[k] for k in ('status', 'assertions', 'total_distinct_original_evaluations_represented', 'canonical_witness_records', 'accepted_joint_checks_unresolved', 'elapsed_seconds')}, sort_keys=True), flush=True)
    except BaseException:
        failure_inputs = args.output / 'INPUTS_RESUME_VERIFICATION122.json'
        if failure_inputs.exists():
            failure_inputs = args.output / 'INPUTS_RESUME_VERIFICATION_FAILURE122.json'
        write(failure_inputs, {'files': sorted(verifier.inputs.values(), key=lambda r: r['path']), 'scope': 'Inputs reached before the preserved failed composite verification.'})
        write(args.output / 'FAILURE_RESUME_VERIFICATION122.json', {
            'status': 'failed', 'assertions': verifier.assertions, 'completed_stages': verifier.completed,
            'elapsed_seconds': time.perf_counter() - started, 'traceback': traceback.format_exc(),
            'verifier_sha256': sha(Path(__file__)), 'all_partial_outputs_retained': True,
            'new_economic_evaluations_by_this_verifier': 0,
        })
        raise


if __name__ == '__main__':
    main()
