"""Read-only identity and report replay checks for all four R16 families.

Numerical pipelines remain byte exact at their generating commits. Publication
uses their deterministic checks and saved-data reporters; it never calls a
trainer, confirmation worker, collector, or a random-bank generator. The menu
family may use its source-bound analysis transport while all raw Git leaves
are checked against E and D without downloading omitted raw blobs.
"""
from __future__ import annotations

import hashlib
import importlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from publication_audit import (R, BASE, require, read, sha, canonical,
    safe_path, file_record, replay_environment)

CANDIDATE_SOURCE = '9142f404bb9c5163aa94d3a4ded4d0fa48a49c50'
CANDIDATE_EVIDENCE = 'b08347444e3001725d7fea33ff0bfce9c7e95e37'
SPECS = {
    'replication': dict(stem='replication', protocol='replication.json',
        trial_count=32, execution_count=128, events=238, alpha=.01),
    'economic_robustness': dict(stem='robustness', protocol='robustness.json',
        trial_count=64, execution_count=256, events=648, alpha=.01),
    'signed_mechanism': dict(stem='signed', evidence='signed_mechanism', protocol='signed_mechanism.json',
        trial_count=32, execution_count=32, events=6, alpha=.01),
    'continuation_menu': dict(stem='menu', evidence='continuation_menu', protocol='menu_protocol.json',
        trial_count=128, execution_count=640, events=344, alpha=.02),
}


def role_paths(role):
    spec = SPECS[role]
    evidence = R / 'results' / spec.get('evidence', spec['stem'])
    return dict(evidence=evidence, summary=evidence.with_name(evidence.name + '_summary'),
                protocol=R / 'protocols' / spec['protocol'],
                pipeline=R / 'code' / (spec['stem'] + '_pipeline.py'),
                reporter=R / 'code' / (spec['stem'] + '_report.py'))


def checked_record(repo, name, expected, tree=None):
    """All materialized records get independent length, SHA256 and Git checks."""
    path = safe_path(repo, name)
    require(path.is_file(), 'required bounded publication input missing: ' + str(name))
    actual = file_record(path)
    for field in ('sha256', 'bytes', 'git_blob'):
        if field in expected:
            require(actual[field] == expected[field], 'source/evidence ' + field + ' changed: ' + str(name))
    if tree is not None:
        require(str(name) in tree and tree[str(name)]['git_blob'] == actual['git_blob'],
                'materialized bytes differ from immutable Git leaf: ' + str(name))
    return actual


def compare_git_leaves(source_tree, delivery_tree, names, context):
    records = {}
    for name in sorted(names):
        require(name in source_tree, context + ' path absent from generating tree: ' + name)
        facts = source_tree[name]
        require(facts['mode'] in ('100644', '100755'), context + ' contains nonregular Git leaf')
        require(delivery_tree.get(name) == facts, context + ' Git leaf changed or missing in D: ' + name)
        records[name] = facts
    return records


def require_commit_parent(git, commit, expected_parent, context):
    """Inspect immutable commit bytes; shallow traversal must not erase parents."""
    header = git.git('cat-file', '-p', commit).split(b'\n\n', 1)[0]
    parents = [line.removeprefix(b'parent ').decode('ascii')
               for line in header.splitlines() if line.startswith(b'parent ')]
    require(parents == [expected_parent], context + ' must have exactly its declared predecessor as parent')
    return expected_parent


def source_identity(repo, git, role, cfg, publication_source):
    paths = role_paths(role)
    require(cfg['evidence_root'] == str(paths['evidence']), 'canonical evidence path cannot change')
    require(cfg.get('summary_root', str(paths['summary'])) == str(paths['summary']), 'canonical summary path cannot change')
    evidence_tree = git.tree(cfg['evidence_commit'])
    source_tree, delivery_tree = git.tree(cfg['source_commit']), git.tree(publication_source)
    manifest_path = str(paths['evidence'] / 'SOURCE_MANIFEST.json')
    checked_record(repo, manifest_path, {}, evidence_tree)
    m = read(repo / manifest_path)
    require(m['numerical_source_commit'] == cfg['source_commit'], 'family generating source differs')
    require(str(m.get('github_run_attempt')) == '1', 'a repeated confirmation workflow attempt is not admissible')
    require(m['protocol_sha256'] == sha(repo / paths['protocol']), 'family protocol digest differs')
    source_files = m['files']
    require(source_files and str(paths['pipeline']) in source_files and str(paths['reporter']) in source_files,
            'pipeline and report must belong to numerical source closure')
    compare_git_leaves(source_tree, delivery_tree, source_files, role + ' scientific source')
    for name, expected in source_files.items():
        checked_record(repo, name, expected, source_tree)
    expected_sha = {name: row['sha256'] for name, row in source_files.items()}
    if role == 'economic_robustness':
        require(set(m['method_fingerprints']) == {'nbo', 'raw_costate', 'direct_policy', 'hjb_family'}, 'method fingerprint family differs')
        for method, fp in m['method_fingerprints'].items():
            require(hashlib.sha256(canonical(fp['input'])).hexdigest() == fp['sha256'], 'method fingerprint digest differs')
            require(fp['input']['group'] == method and fp['input']['files'] == expected_sha and
                    fp['input']['protocol_sha256'] == m['protocol_sha256'] and
                    fp['input']['environment_contract'] == m['environment_contract'], 'method fingerprint input differs')
    else:
        fp = m['fingerprint_input']
        require(hashlib.sha256(canonical(fp)).hexdigest() == m['assessment_fingerprint'], 'assessment fingerprint differs')
        require(fp['files'] == expected_sha and fp['protocol_sha256'] == m['protocol_sha256'] and
                fp['environment_contract'] == m['environment_contract'], 'assessment fingerprint input differs')
    if role in ('replication', 'signed_mechanism'):
        require(m['candidate_source_commit'] == CANDIDATE_SOURCE and m['candidate_evidence_commit'] == CANDIDATE_EVIDENCE,
                'original selected policy source/evidence identity changed')
    # All imports happen only after the complete module closure is byte verified.
    code = str(repo / R / 'code')
    if code not in sys.path:
        sys.path.insert(0, code)
    module = importlib.import_module(SPECS[role]['stem'] + '_pipeline')
    require(set(module.source_files(repo)) == set(source_files), 'manifest omits or adds an execution dependency')
    deterministic = module.check(repo)
    require(deterministic.get('complete') is True, 'frozen deterministic source gate failed')
    p = read(repo / paths['protocol'])
    trials = module.trials(p)
    require(m['matrix'] == {'include': trials} and len(trials) == SPECS[role]['trial_count'], 'complete frozen trial matrix changed')
    return m, p, module, trials, deterministic


def evidence_identity(repo, git, role, cfg, publication_source):
    paths = role_paths(role)
    prefix = str(paths['evidence']) + '/'
    evidence_tree, delivery_tree = git.tree(cfg['evidence_commit']), git.tree(publication_source)
    evidence_parent = None
    if role != 'continuation_menu':
        evidence_parent = require_commit_parent(git, cfg['evidence_commit'], cfg['source_commit'],
                                               role + ' evidence commit')
    evidence_names = {name for name in evidence_tree if name.startswith(prefix)}
    require(evidence_names, 'empty family evidence tree')
    require({name for name in delivery_tree if name.startswith(prefix)} == evidence_names,
            'D adds or drops a file in the frozen canonical evidence root')
    leaves = compare_git_leaves(evidence_tree, delivery_tree, evidence_names, role + ' complete evidence')
    manifest_name = str(paths['evidence'] / 'EVIDENCE_MANIFEST.json')
    checked_record(repo, manifest_name, {}, evidence_tree)
    inventory = read(repo / manifest_name)
    require(inventory['numerical_source_commit'] == cfg['source_commit'], 'evidence inventory has another numerical source')
    require(set(inventory['files']) == evidence_names - {manifest_name}, 'canonical evidence manifest is not exhaustive')
    records = {}
    materialized_bytes = 0
    for name in sorted(evidence_names):
        expected = inventory['files'].get(name, {})
        if name != manifest_name:
            require(re.fullmatch('[0-9a-f]{64}', expected.get('sha256', '')) and
                    isinstance(expected.get('bytes'), int) and expected['bytes'] >= 0,
                    'evidence manifest lacks content identity/length')
        if 'git_blob' in expected:
            require(expected['git_blob'] == leaves[name]['git_blob'], 'manifest Git identity differs from E')
        records[name] = {**expected, **leaves[name], 'materialized': False}
        path = safe_path(repo, name)
        if path.is_file():
            actual = checked_record(repo, name, expected, evidence_tree)
            records[name].update(actual, materialized=True)
            materialized_bytes += actual['bytes']
    mode = cfg.get('replay_mode')
    require(mode == ('bounded_analysis' if role == 'continuation_menu' else 'complete_new_family'),
            'the frozen publication replay mode changed')
    if mode == 'complete_new_family':
        require(all(x['materialized'] for x in records.values()), 'complete fresh family must be materialized for replay')
    summary_prefix = str(paths['summary']) + '/'
    summary_names = {name for name in evidence_tree if name.startswith(summary_prefix)}
    summary_metadata = {'SOURCE_MANIFEST.json', 'FINAL_AUDIT.json', 'EVIDENCE_MANIFEST.json'}
    if role == 'continuation_menu':
        summary_metadata.add('FULL_PAYLOAD_GIT_AUDIT.json')
        require(str(paths['evidence'] / 'FULL_PAYLOAD_GIT_AUDIT.json') in evidence_names, 'menu full-payload Git audit is missing')
        proof_path = repo / paths['evidence'] / 'FULL_PAYLOAD_GIT_AUDIT.json'
        proof, final = read(proof_path), read(repo / paths['evidence'] / 'FINAL_AUDIT.json')
        require(proof.get('complete') is True and proof['numerical_source_commit'] == cfg['source_commit'] and
                proof['trial_count'] == 128 and proof['source_tree_preserved'] is True, 'menu full-payload audit is incomplete')
        require(proof['staging_commit'] == inventory['staging_commit'] == final['staging_commit'] and
                final['full_payload_git_audit_sha256'] == sha(proof_path), 'menu staging/audit linkage differs')
        evidence_parent = require_commit_parent(git, cfg['evidence_commit'], proof['staging_commit'],
                                               'menu evidence commit')
    canonical_subset = {name for name in evidence_names if '/report/' in name or Path(name).name in summary_metadata}
    expected_summary = {summary_prefix + name.removeprefix(prefix): name for name in canonical_subset}
    require(summary_names == set(expected_summary), 'summary does not contain its exact metadata set and complete report')
    compare_git_leaves(evidence_tree, delivery_tree, summary_names, role + ' summary')
    for summary, canonical_name in expected_summary.items():
        require(evidence_tree[summary]['git_blob'] == evidence_tree[canonical_name]['git_blob'], 'summary differs from canonical evidence')
        checked_record(repo, summary, {}, evidence_tree)
    return records, dict(materialized_files=sum(r['materialized'] for r in records.values()),
                        materialized_bytes=materialized_bytes, total_files=len(records),
                        total_bytes=sum(r['bytes'] for r in records.values()), replay_mode=mode,
                        complete_git_tree_preserved=True, summary_files=len(summary_names),
                        evidence_parent_commit=evidence_parent)


def verify_environment(actual, fingerprint, contract):
    require(hashlib.sha256(canonical(actual)).hexdigest() == fingerprint, 'worker environment fingerprint differs')
    require(actual['packages'] == contract['packages'] and actual['threads'] == contract['numeric_threads'], 'worker packages or thread contract differs')
    require(actual['python'].startswith(contract['python'] + '.') and actual['platform'].startswith(contract['platform']),
            'worker Python/platform contract differs')


def verify_standard_trials(repo, role, paths, m, module, trials):
    root = repo / paths['evidence'] / 'trials'
    require({p.parent.name for p in root.rglob('TRIAL.json')} == {t['trial_id'] for t in trials}, 'missing or additional trial')
    process_count = 0
    for trial in trials:
        folder = root / trial['trial_id']
        r = read(folder / 'TRIAL.json')
        require(r.get('complete') is True and r['trial'] == trial and r['numerical_source_commit'] == m['numerical_source_commit'],
                'trial receipt identity or completeness changed')
        require(r['protocol_sha256'] == m['protocol_sha256'], 'trial protocol changed')
        if role == 'economic_robustness':
            require([x['group'] for x in r['groups']] == trial['group_order'], 'execution-group rotation changed')
            entries = [(x['group'], x) for x in r['groups']]
        else:
            require(r['assessment_fingerprint'] == m['assessment_fingerprint'], 'trial assessment fingerprint changed')
            require([x['method_id'] for x in r['methods']] == trial['method_order'], 'method rotation changed')
            entries = [(x['method_id'], x) for x in r['methods']]
        for method, entry in entries:
            require(entry.get('complete') is True and sha(folder / method / 'WORK.json') == entry['work_sha256'], 'trial WORK digest/completeness changed')
            module.verify_work(folder / method, m, trial, method)
            process_count += 1
    require(process_count == SPECS[role]['execution_count'], 'complete new execution count changed')
    return dict(trials=len(trials), fresh_processes=process_count, complete_worker_inventory_rechecked=True)


def verify_menu_trials(repo, paths, m, trials, evidence_records):
    """Check the full raw inventory through the source-bound transport receipts.

    Each raw file was hashed in the completed generating trial. Its receipt
    binds SHA256, length and Git blob ID to the raw leaf in E and D. Analysis
    files are materialized and independently rehashed before complete report
    replay. No new random number or scalar reference bank is drawn here.
    """
    root = repo / paths['evidence'] / 'trials'
    require({p.parent.name for p in root.rglob('TRIAL.json')} == {t['trial_id'] for t in trials}, 'menu trial population differs')
    require(str(R / 'code/menu_transport.py') in m['files'], 'analysis transport must be frozen with numerical source')
    transport_module = importlib.import_module('menu_transport')
    raw_files = analysis_files = raw_bytes = 0
    for trial in trials:
        folder = root / trial['trial_id']
        transport_module.verify_analysis_trial(folder, m)
        transport = read(folder / 'TRANSPORT_RECEIPT.json')
        require(transport.get('numerical_source_commit', transport.get('source_commit')) == m['numerical_source_commit'], 'transport has another numerical source')
        require(transport.get('trial_id') == trial['trial_id'], 'transport trial identity differs')
        raw, analysis = transport['raw_files'], transport['analysis_files']
        require(transport.get('attempt_complete') is True and transport['payload_tree_prefix'] == str(folder.relative_to(repo)),
                'menu transport describes an incomplete or different trial')
        require(transport['raw_bytes'] == sum(row['bytes'] for row in raw.values()), 'menu raw byte counter differs')
        require('TRIAL.json' in raw and 'TRIAL.json' in analysis, 'transport omits original trial receipt')
        require(set(analysis) <= set(raw), 'analysis transport invents an original raw record')
        for name, expected in raw.items():
            relative = str((folder / name).relative_to(repo))
            safe_path(folder, name)
            require(relative in evidence_records, 'transport raw leaf absent from complete E')
            for field in ('sha256', 'bytes', 'git_blob'):
                require(evidence_records[relative][field] == expected[field], 'transport/raw Git identity differs: ' + relative)
        for name, expected in analysis.items():
            checked_record(folder, name, expected)
            require(expected == raw[name], 'analysis identity differs from original raw record')
        r = read(folder / 'TRIAL.json')
        require(r.get('complete') is True and r['trial'] == trial and r['numerical_source_commit'] == m['numerical_source_commit'] and
                r['protocol_sha256'] == m['protocol_sha256'] and r['assessment_fingerprint'] == m['assessment_fingerprint'],
                'menu trial source/protocol identity differs')
        require(r['files'] == {name: facts['sha256'] for name, facts in raw.items() if name != 'TRIAL.json'},
                'transport omits or adds an original raw trial file')
        require(r['all_fitting_finished_before_confirmation'] is True and r['final_confirmation_used_for_selection'] is False,
                'menu fitting may have read confirmation')
        verify_environment(r['environment'], r['environment_fingerprint'], m['environment_contract'])
        methods = {'nbo_scalar', 'vector_costate', 'raw_actor', 'dpo_actor', 'raw_saa'}
        require(set(r['method_process_work']) == methods, 'menu method fit omitted')
        for method, work in r['method_process_work'].items():
            require(work['returncode'] == 0 and work['end_to_end_seconds'] > 0, 'menu fit process incomplete')
            fit = read(folder / 'fits' / method / 'FIT_WORK.json')
            require(fit['source_commit'] == m['numerical_source_commit'] and fit['protocol_sha256'] == m['protocol_sha256'] and
                    fit['final_confirmation_read'] is False and fit['method'] == method and fit['calibration'] == trial['calibration'] and
                    fit['dimension'] == trial['dimension'] and fit['seed'] == trial['stream_seed'], 'menu fit receipt differs')
            prefix = 'fits/' + method + '/'
            expected_fit = {name.removeprefix(prefix): facts['sha256'] for name, facts in raw.items()
                            if name.startswith(prefix) and name != prefix + 'FIT_WORK.json'}
            require({name: facts['sha256'] for name, facts in fit['payload_inventory'].items()} == expected_fit, 'menu fitting payload inventory differs')
        require(r['confirmation_process_work']['returncode'] == 0 and r['confirmation_process_work']['end_to_end_seconds'] > 0,
                'menu confirmation process incomplete')
        raw_files += len(raw)
        analysis_files += len(analysis)
        raw_bytes += transport['raw_bytes']
    proof = read(repo / paths['evidence'] / 'FULL_PAYLOAD_GIT_AUDIT.json')
    final = read(repo / paths['evidence'] / 'FINAL_AUDIT.json')
    require(proof['full_raw_files'] == final['full_raw_files'] == raw_files and
            proof['full_raw_bytes'] == final['full_raw_bytes'] == raw_bytes, 'menu full-payload counters differ from all 128 receipts')
    return dict(trials=len(trials), fresh_processes=640, stage_candidates=1920,
                full_raw_leaf_identities_checked=raw_files, full_raw_bytes=raw_bytes, materialized_analysis_files=analysis_files,
                raw_scope='All raw SHA256/length/Git identities are linked through generating trial and transport receipts to E and D; saved analysis inputs are rehashed and replayed.')


def verify_family_report(repo, role, cfg, m):
    paths = role_paths(role)
    canonical_report = repo / paths['evidence'] / 'report'
    report = read(canonical_report / 'REPORT.json')
    final = read(repo / paths['evidence'] / 'FINAL_AUDIT.json')
    require(final.get('complete') is True and final['numerical_source_commit'] == cfg['source_commit'] and
            final['protocol_sha256'] == m['protocol_sha256'], 'family final audit identity/completeness differs')
    require(report.get('complete') is True, 'family report incomplete')
    common = dict(trial_count=SPECS[role]['trial_count'])
    if role in ('replication', 'signed_mechanism'):
        common.update(policy_executions=SPECS[role]['execution_count'], confidence_events=SPECS[role]['events'],
            old_policies_preserved=True, old_stopping_unchanged=True, new_confirmation_banks=32, new_training_runs=0)
        require(report['policy_executions'] == SPECS[role]['execution_count'] and report['confidence']['event_count'] == SPECS[role]['events'], 'complete family report counters differ')
    elif role == 'economic_robustness':
        common.pop('trial_count')
        common['trials'] = 64
        common.update(fresh_group_processes=256, policy_outputs=320, confidence_events=648,
                      all_declared_streams_retained=True, old_evidence_unchanged=True)
        require(report['policy_outputs'] == 320 and report['confidence']['event_count'] == 648, 'complete robustness report counters differ')
    else:
        common.update(method_fits=640, stage_candidates=1920, primary_events=216, scalar_events=128,
                      all_raw_inputs_and_outputs_retained=True, no_stage_or_seed_selection=True)
        require(report['trial_count'] == 128 and report['method_fits'] == 640 and report['stage_candidates'] == 1920 and
                report['primary_event_count'] == 216 and report['scalar_event_count'] == 128, 'menu report counters differ')
        require(report['no_stage_or_stream_selection'] is True and report['continuous_time_or_full_vector_near_optimality_claim'] is False,
                'menu evidence scope differs')
    for field, value in common.items():
        require(final.get(field) == value, 'family final audit counter differs: ' + field)
    with tempfile.TemporaryDirectory(prefix='nbo-r16-publication-report-') as temporary:
        out = Path(temporary) / 'report'
        base = [sys.executable, str(repo / paths['reporter']), '--repo', str(repo)]
        environment = replay_environment(Path(temporary) / 'jit')
        commands = []
        if role == 'economic_robustness':
            for calibration in ('high', 'low', 'long', 'stress'):
                commands.append(base + ['--results', str(repo / paths['evidence'] / 'trials'),
                    '--out', str(out / 'parts' / calibration), '--calibration', calibration])
            commands.append(base + ['--out', str(out), '--aggregate'])
        else:
            commands.append(base + ['--results', str(repo / paths['evidence'] / 'trials'), '--out', str(out)])
        for number, command in enumerate(commands):
            log = Path(temporary) / f'replay-{number}.log'
            with log.open('wb') as handle:
                result = subprocess.run(command, cwd=repo, env=environment, stdout=handle, stderr=subprocess.STDOUT)
            require(result.returncode == 0, 'saved-input report replay failed: ' + log.read_text(errors='replace')[-4000:])
        actual = {str(p.relative_to(out)): file_record(p) for p in out.rglob('*') if p.is_file()}
        expected = {str(p.relative_to(canonical_report)): file_record(p) for p in canonical_report.rglob('*') if p.is_file()}
        require(actual == expected, 'fresh complete report is not byte identical to the canonical report')
    return dict(report_files=expected, all_report_files_byte_identical=True,
                confirmation_draws=0, training_runs=0, event_count=SPECS[role]['events'],
                final_audit_sha256=sha(repo / paths['evidence'] / 'FINAL_AUDIT.json'))


def check_family(repo, git, role, cfg, publication_source):
    repo = Path(repo)
    m, protocol, module, trials, deterministic = source_identity(repo, git, role, cfg, publication_source)
    records, preservation = evidence_identity(repo, git, role, cfg, publication_source)
    paths = role_paths(role)
    if role == 'continuation_menu':
        executions = verify_menu_trials(repo, paths, m, trials, records)
    else:
        executions = verify_standard_trials(repo, role, paths, m, module, trials)
    report = verify_family_report(repo, role, cfg, m)
    return dict(source_commit=cfg['source_commit'], evidence_commit=cfg['evidence_commit'],
                protocol_sha256=m['protocol_sha256'], source_files=m['files'], evidence_files=records,
                deterministic_source_check=deterministic, preservation=preservation,
                complete_execution_account=executions, independent_report_replay=report)


def check_confidence_families(repo, roles):
    allocation = read(repo / R / 'protocols/confidence_families.json')
    expected = dict(paired_replication=.01, economic_robustness=.01, signed_mechanism=.01, continuation_menu=.02)
    require(allocation['alpha_total'] == .05 and allocation['allocations'] == expected, 'new independent family allocation changed')
    observations = {}
    for role in SPECS:
        paths = role_paths(role)
        p, report = read(repo / paths['protocol']), read(repo / paths['evidence'] / 'report/REPORT.json')
        if role == 'continuation_menu':
            require(p['confidence']['alpha'] == .018 and p['confidence']['scalar_alpha'] == .002 and
                    report['primary_confidence']['family_alpha'] == .018 and report['scalar_confidence']['family_alpha'] == .002 and
                    report['total_menu_alpha'] == .02, 'menu confidence subdivision differs')
        elif role == 'economic_robustness':
            require(p['inference']['alpha'] == .01 and report['confidence']['alpha'] == .01, 'robustness confidence allocation differs')
        else:
            require(p['inference']['family_alpha'] == .01 and report['confidence']['alpha'] == .01,
                    'independent family allocation differs')
        observations[role] = dict(alpha=SPECS[role]['alpha'], event_count=SPECS[role]['events'])
    return dict(alpha_total=.05, families=observations, historical_alpha_reused=False,
                allocation_sha256=sha(repo / R / 'protocols/confidence_families.json'))


def check_author_tables(repo):
    """The author-added attainment table must reproduce every recorded count."""
    report = read(repo / role_paths('replication')['evidence'] / 'report/REPORT.json')
    expected = {(row['dimension'], row['method_id'], row['target']):
                (row['definitely_attaining'], row['possibly_attaining']) for row in report['final_certified_attainment']}
    require(len(expected) == 16, 'replication must retain both targets for every method/dimension')
    methods = {'NBO': 'nbo', 'Raw': 'raw_costate', 'Direct policy': 'direct_policy', 'Neural HJB': 'neural_hjb'}
    text = (repo / R / 'manuscript/replication_supplement.tex').read_text()
    rows = re.findall(r'^(10|50) & (NBO|Raw|Direct policy|Neural HJB) & (\d+)--(\d+) & (\d+)--(\d+)\\\\', text, re.M)
    observed = {}
    for dimension, method, first_l, first_u, second_l, second_u in rows:
        observed[(int(dimension), methods[method], .0005)] = (int(first_l), int(first_u))
        observed[(int(dimension), methods[method], .001)] = (int(second_l), int(second_u))
    require(len(rows) == 8 and observed == expected, 'author attainment table differs from the complete protected report')
    return dict(table='tab:r16replicationattainment', complete_rows=8, protected_target_entries=16,
                source_report_sha256=sha(repo / role_paths('replication')['evidence'] / 'report/REPORT.json'),
                author_source_sha256=sha(repo / R / 'manuscript/replication_supplement.tex'), all_values_reproduced=True)


def check_prior_attempts(repo, git, attempts):
    records = []
    seen = set()
    for row in attempts:
        source = row['source_commit']
        require(source not in seen and re.fullmatch('[0-9a-f]{40}', source or ''), 'invalid/repeated prior source attempt')
        seen.add(source)
        receipt_path = safe_path(repo, row['receipt'])
        receipt = read(receipt_path)
        require(receipt['source_commit'] == source and receipt['confirmation_started'] is False and
                receipt['training_started'] is False and receipt['failure_stage'] == 'source_validation',
                'a preconfirmation failure receipt is not a scientific retry permission')
        require(str(receipt['github_run_attempt']) == '1' and receipt.get('github_run_id'), 'missing first-attempt CI provenance')
        require(receipt.get('complete') is True and receipt.get('jobs'), 'incomplete source failure chronology')
        jobs = {job['name']: job for job in receipt['jobs']}
        require(len(jobs) == len(receipt['jobs']) and jobs.get('source', {}).get('conclusion') == 'failure',
                'prior failure was not the source-validation job')
        require(all(job.get('conclusion') == 'skipped' for name, job in jobs.items() if name != 'source'),
                'a scientific job ran in the purported preconfirmation source failure')
        for name, expected in receipt.get('archive', {}).items():
            checked_record(repo, name, expected)
        tree = git.tree(source)
        changed = {}
        for original, destination in row['preserved_files'].items():
            require(original in tree, 'prior source file absent from its immutable tree')
            changed[original] = dict(destination=destination,
                **git.compare(tree[original]['git_blob'], safe_path(repo, destination)))
        require(changed, 'prior source attempt has no preserved differentiating source')
        records.append(dict(source_commit=source, receipt=str(row['receipt']), receipt_sha256=sha(receipt_path),
                            confirmation_started=False, preserved_files=changed))
    return dict(attempts=records, count=len(records), scope='Failed source validation before scientific execution is recorded separately; no confirmation observation is reused.')
