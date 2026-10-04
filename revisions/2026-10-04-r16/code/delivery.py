"""Bounded sparse checkout and atomic creation-only R16 publication.

The numerical evidence is already committed before this program runs. D names
the reviewed delivery source; CI rebuilds the four documents and constructs one
child F using a private index. Publishing creates three previously absent refs
atomically. No existing branch, scientific source, or evidence object is edited.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from publication_audit import (R, BASE, REVIEW, HISTORICAL_BLOBS, ROOT_ARCHIVE,
    ROOTS, WORKFLOW, SOURCE_BRANCH, TARGET_BRANCHES, ROLES, DERIVED_TOP,
    DERIVED_RESULTS, NONPUBLIC, GitStore, require, read, write, safe_path, sha,
    file_record, validate_configuration, payload_path)
from publication_families import role_paths, compare_git_leaves


def git(repo, *args, **kwargs):
    return subprocess.check_output(['git', *args], cwd=repo, stderr=subprocess.PIPE, **kwargs)


def configuration(repo):
    cfg = read(repo / R / 'PUBLICATION_SOURCES.json')
    validate_configuration(cfg)
    return cfg


def remote_ref(repo, branch):
    data = git(repo, 'ls-remote', '--heads', 'origin', 'refs/heads/' + branch).decode().splitlines()
    require(len(data) <= 1, 'ambiguous remote ref')
    if not data:
        return None
    oid, name = data[0].split('\t')
    require(name == 'refs/heads/' + branch and re.fullmatch('[0-9a-f]{40}', oid), 'unexpected remote ref response')
    return oid


def preflight(repo, source, require_sparse=False):
    repo = Path(repo).resolve()
    configuration(repo)
    require(re.fullmatch('[0-9a-f]{40}', source or ''), 'full D commit identity required')
    require(git(repo, 'rev-parse', 'HEAD').decode().strip() == source, 'checkout is not D')
    require(remote_ref(repo, SOURCE_BRANCH) == source, 'delivery source branch no longer names D')
    for branch in TARGET_BRANCHES:
        require(remote_ref(repo, branch) is None, 'refusing to change existing publication branch: ' + branch)
    if require_sparse:
        require(git(repo, 'config', '--get', 'core.sparseCheckout').decode().strip() == 'true', 'publication requires sparse checkout')
        require(git(repo, 'config', '--get', 'remote.origin.partialclonefilter').decode().strip() == 'blob:none',
                'publication must fetch metadata before bounded blobs')
    return dict(source_commit=source, all_target_branches_absent=True, sparse_required=require_sparse)


def fetch_sources(repo, source):
    repo = Path(repo).resolve()
    cfg = configuration(repo)
    commits = {source, BASE, REVIEW}
    for role in cfg['roles'].values():
        commits.update(role[name] for name in ('source_commit', 'evidence_commit'))
        commits.update(role[name] for name in ('candidate_source_commit', 'candidate_evidence_commit') if name in role)
    commits.update(row['source_commit'] for row in cfg.get('prior_attempts', []))
    missing = []
    for oid in sorted(commits):
        require(re.fullmatch('[0-9a-f]{40}', oid or ''), 'source identity must be an immutable commit')
        result = subprocess.run(['git', 'cat-file', '-e', oid + '^{commit}'], cwd=repo,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode:
            missing.append(oid)
    if missing:
        subprocess.run(['git', 'fetch', '--filter=blob:none', '--no-tags', '--depth=1', 'origin', *missing], cwd=repo, check=True)
    # The saved menu reporter checks S -> the 128-append staging tip. Fetch the
    # complete necessary commit/tree chain explicitly; a shallow E alone would
    # leave this to version-dependent lazy ancestor fetching. E plus its 128
    # trial parents and S has exactly 130 commits. No blobs are requested.
    menu_evidence = cfg['roles']['continuation_menu']['evidence_commit']
    subprocess.run(['git', 'fetch', '--filter=blob:none', '--no-tags', '--depth=130', 'origin', menu_evidence], cwd=repo, check=True)
    return dict(immutable_commits=len(commits), metadata_commits_fetched=len(missing), filter='blob:none',
                menu_ancestry_depth=130, menu_ancestry_fetched_explicitly=True)


def sparse_pattern(name):
    require(not any(ord(c) < 32 for c in name), 'control character in sparse source path')
    safe_path(Path('/'), name)
    return '/' + re.sub(r'([\\*?\[\]!#])', r'\\\1', name)


def set_sparse(repo, names):
    data = '\n'.join(sparse_pattern(name) for name in sorted(names)) + '\n'
    subprocess.run(['git', 'sparse-checkout', 'set', '--no-cone', '--stdin'], cwd=repo,
                   input=data, text=True, check=True, stdout=subprocess.DEVNULL)


def publication_input_names(tree, evidence_roots):
    names = {str(WORKFLOW), 'README.md'}
    for name in tree:
        path = Path(name)
        if not path.is_relative_to(R):
            continue
        sub = path.relative_to(R)
        if set(sub.parts) & NONPUBLIC or sub.suffix == '.pyc' or sub.parts[0] in ('build', 'retained'):
            continue
        if len(sub.parts) == 1 and sub.name in DERIVED_TOP:
            continue
        if sub.parts[0] == 'results' and sub.name in DERIVED_RESULTS:
            continue
        if any(path.is_relative_to(Path(root)) for root in evidence_roots):
            continue
        names.add(name)
    return names


def materialize(repo, source):
    repo = Path(repo).resolve()
    preflight(repo, source, require_sparse=True)
    cfg = configuration(repo)
    fetch_sources(repo, source)
    store = GitStore(repo)
    try:
        tree = store.tree(source)
        evidence_roots = [row['evidence_root'] for row in cfg['roles'].values()]
        names = publication_input_names(tree, evidence_roots)
        names.update({'ECTA.tex', 'supp.tex', 'econsocart.cls', 'econsocart.cfg', 'ecta-fullname.bst', 'revision_reference.bib'})
        names.update(name for name in tree if name.startswith('reviews/2026-10-04-econometrica-numerical-methods-r15/'))
        for role in ROLES:
            paths = role_paths(role)
            prefix = str(paths['evidence']) + '/'
            names.update(name for name in tree if name.startswith(prefix) and
                ('/report/' in name or Path(name).name in {'SOURCE_MANIFEST.json', 'FINAL_AUDIT.json', 'EVIDENCE_MANIFEST.json', 'FULL_PAYLOAD_GIT_AUDIT.json',
                 'TRANSPORT_RECEIPT.json', 'ANALYSIS_MANIFEST.json', 'TRANSPORT_PUBLICATION.json'}))
        require(names <= tree.keys(), 'bounded initial metadata source absent from D')
        set_sparse(repo, names)
        inventory = read(repo / R / 'SOURCE_INVENTORY.json')
        names.update(row['path'] for row in inventory['files'])
        evidence_size = 0
        expected = {}
        for role, config in cfg['roles'].items():
            paths = role_paths(role)
            source_manifest = read(repo / paths['evidence'] / 'SOURCE_MANIFEST.json')
            names.update(source_manifest['files'])
            expected.update(source_manifest['files'])
            evidence_manifest = read(repo / paths['evidence'] / 'EVIDENCE_MANIFEST.json')
            if config['replay_mode'] == 'complete_new_family':
                names.update(evidence_manifest['files'])
                expected.update(evidence_manifest['files'])
            else:
                require(role == 'continuation_menu' and config['replay_mode'] == 'bounded_analysis', 'unknown sparse analysis contract')
                receipt_paths = sorted((repo / paths['evidence'] / 'trials').glob('*/TRANSPORT_RECEIPT.json'))
                require(len(receipt_paths) == 128, 'complete menu analysis transport receipt set missing')
                for receipt_path in receipt_paths:
                    receipt = read(receipt_path)
                    for relative, record in receipt['analysis_files'].items():
                        full = str(safe_path(receipt_path.parent, relative).relative_to(repo))
                        names.add(full)
                        expected[full] = record
                    for auxiliary in ('ANALYSIS_MANIFEST.json', 'TRANSPORT_PUBLICATION.json'):
                        auxiliary_path = str((receipt_path.parent / auxiliary).relative_to(repo))
                        require(auxiliary_path in tree, 'menu transport publication proof missing')
                        names.add(auxiliary_path)
                        if auxiliary_path in evidence_manifest['files']:
                            expected[auxiliary_path] = evidence_manifest['files'][auxiliary_path]
            evidence_size += sum(row['bytes'] for row in evidence_manifest['files'].values())
        require(names <= tree.keys(), 'bounded publication dependency absent from D')
        anticipated = sum(row['bytes'] for row in expected.values())
        limit = int(cfg['materialization']['maximum_selected_bytes'])
        require(0 < anticipated <= limit <= 6 * 1024 ** 3, 'bounded analysis payload exceeds the fixed publication limit')
        # Partial objects and their expanded working files coexist. Refuse a
        # build that cannot retain both plus 1 GiB for PDFs and temporary output.
        require(shutil.disk_usage(repo).free > 2 * anticipated + 1024 ** 3, 'insufficient disk for bounded publication inputs')
        set_sparse(repo, names)
        records = {}
        for name in sorted(names):
            actual = file_record(safe_path(repo, name))
            require(actual['git_blob'] == tree[name]['git_blob'], 'sparse checkout bytes differ from D: ' + name)
            for field in ('sha256', 'bytes', 'git_blob'):
                if field in expected.get(name, {}):
                    require(actual[field] == expected[name][field], 'bounded source/evidence input changed: ' + name)
            records[name] = actual
        record = dict(schema='nbo-r16-bounded-materialization-v1', publication_source_commit=source,
            complete=True, selected_files=len(names), selected_bytes=sum(row['bytes'] for row in records.values()),
            complete_new_evidence_bytes=evidence_size, files=records,
            historical_raw_materialized=False, menu_raw_scope='Full Git leaves retained; only source-bound report analysis inputs expanded.',
            filter='blob:none', sparse_checkout=True)
        require(record['selected_bytes'] <= limit, 'actual bounded working set exceeds the fixed publication limit')
        write(repo / R / 'results/MATERIALIZATION.json', record)
        return {key: value for key, value in record.items() if key != 'files'}
    finally:
        store.close()


def verify_payload(repo, source):
    repo = Path(repo).resolve()
    cfg = configuration(repo)
    final = read(repo / R / 'FINAL_AUDIT.json')
    ledger_path, manifest_path = repo / R / 'SOURCE_LEDGER.json', repo / R / 'EVIDENCE_MANIFEST.json'
    ledger, manifest = read(ledger_path), read(manifest_path)
    require(final.get('complete') is True and ledger.get('complete') is True and final['issues'] == ledger['issues'] == [], 'publication gates incomplete')
    require(final['publication_source_commit'] == ledger['publication_source_commit'] == manifest['publication_source_commit'] == source,
            'publication D identity differs')
    require(final['source_ledger_sha256'] == sha(ledger_path) and final['evidence_manifest_sha256'] == sha(manifest_path), 'predecessor ledger/payload changed after audit')
    require(final['configuration_sha256'] == ledger['configuration_sha256'] == sha(repo / R / 'PUBLICATION_SOURCES.json'), 'source configuration changed after audit')
    expected_checks = {'publication_inputs', 'history', 'review', *ROLES, 'confidence_families', 'author_tables', 'prior_attempts',
                       'editorial', 'narrative', 'editorial_replay', 'pdfs', 'layout', 'current_source_closure'}
    require(set(ledger['checks']) == set(final['checks']) == expected_checks, 'publication gate set is incomplete')
    require(final['payload_files'] == len(manifest['files']) and set(final['pdfs']) == set(ROOTS), 'publication payload/PDF counts differ')
    store = GitStore(repo)
    try:
        tree = store.tree(source)
        for name, expected in manifest['files'].items():
            require(payload_path(name), 'unapproved publication payload path: ' + name)
            path = safe_path(repo, name)
            if expected['storage'] == 'materialized':
                actual = file_record(path)
                require(all(actual[field] == expected[field] for field in ('sha256', 'bytes', 'git_blob')), 'materialized payload changed after audit: ' + name)
            else:
                require(expected['storage'] == 'preserved_git_leaf' and tree.get(name) ==
                        {'git_blob': expected['git_blob'], 'mode': expected['mode']}, 'sparse raw payload differs from D')
                if path.is_file():
                    require(file_record(path)['git_blob'] == expected['git_blob'], 'a present raw file differs from preserved Git leaf')
        for name, row in ledger['checks']['publication_inputs'].items():
            require(file_record(safe_path(repo, name))['git_blob'] == tree[name]['git_blob'] == row['git_blob'], 'D-bound publication source changed after audit')
        identity = final['delivery_identity']
        require(identity['source_branch'] == SOURCE_BRANCH and tuple(identity['target_branches']) == TARGET_BRANCHES and
                identity['workflow_sha256'] == sha(repo / WORKFLOW) and
                file_record(repo / WORKFLOW)['git_blob'] == tree[str(WORKFLOW)]['git_blob'], 'delivery workflow/ref contract changed')
        # A generated file cannot escape the final inventory merely by being
        # absent from Git before publication.
        current = {str(path.relative_to(repo)) for path in (repo / R).rglob('*') if path.is_file() and
                   not path.is_symlink() and payload_path(str(path.relative_to(repo)))} | {'ECTA.tex', 'supp.tex', 'README.md'}
        require(current <= manifest['files'].keys(), 'unlisted current publication payload')
        return final, ledger, manifest
    finally:
        store.close()


def verify_final_tree(store, source, final, ledger, manifest):
    old, new = store.tree(source), store.tree(final)
    expected = dict(old)
    for name, row in manifest['files'].items():
        expected[name] = dict(mode=row['mode'], git_blob=row['git_blob'])
    for name in ('EVIDENCE_MANIFEST.json', 'FINAL_AUDIT.json'):
        path = R / name
        expected[str(path)] = dict(mode='100644', git_blob=file_record(store.repo / path)['git_blob'])
    require(new == expected, 'F contains a change outside the audited payload or drops an inherited file')
    historical = store.tree(BASE)
    require(len(historical) == HISTORICAL_BLOBS, 'reviewed historical tree count differs')
    for name, facts in historical.items():
        require(new.get(str(ROOT_ARCHIVE.get(name, Path(name)))) == facts, 'F loses a reviewed historical blob')
    for role in ROLES:
        record = ledger['checks'][role]
        compare_git_leaves(store.tree(record['source_commit']), new, record['source_files'], role + ' final scientific source')
        compare_git_leaves(store.tree(record['evidence_commit']), new, record['evidence_files'], role + ' final complete evidence')
    parents = git(store.repo, 'rev-list', '--parents', '-n', '1', final).decode().split()
    require(parents == [final, source], 'F must have exactly D as its parent')


def atomic_push_command(final):
    require(re.fullmatch('[0-9a-f]{40}', final or ''), 'full final commit identity required')
    return (['git', 'push', '--atomic'] +
            ['--force-with-lease=refs/heads/' + branch + ':' for branch in TARGET_BRANCHES] +
            ['origin'] + [final + ':refs/heads/' + branch for branch in TARGET_BRANCHES])


def construct_commit(repo, source, source_tree, updates):
    """Create only an object and a private index; leave HEAD and shared index intact."""
    with tempfile.TemporaryDirectory(prefix='nbo-r16-delivery-index-') as temporary:
        index = Path(temporary) / 'publication.index'
        env = dict(os.environ, GIT_INDEX_FILE=str(index), GIT_NO_LAZY_FETCH='1', GIT_AUTHOR_NAME='github-actions[bot]',
            GIT_AUTHOR_EMAIL='41898282+github-actions[bot]@users.noreply.github.com',
            GIT_COMMITTER_NAME='github-actions[bot]', GIT_COMMITTER_EMAIL='41898282+github-actions[bot]@users.noreply.github.com')
        subprocess.run(['git', 'read-tree', source], cwd=repo, env=env, check=True)
        changed = []
        for name, row in sorted(updates.items()):
            safe_path(repo, name)
            new = dict(mode=row['mode'], git_blob=row['git_blob'])
            if source_tree.get(name) == new:
                continue
            require(row['storage'] == 'materialized', 'publication cannot manufacture absent raw evidence')
            oid = git(repo, 'hash-object', '-w', '--', name).decode().strip()
            require(oid == row['git_blob'], 'payload changed during staging')
            subprocess.run(['git', 'update-index', '--add', '--cacheinfo', row['mode'] + ',' + oid + ',' + name],
                           cwd=repo, env=env, check=True)
            changed.append(name)
        tree = git(repo, 'write-tree', '--missing-ok', env=env).decode().strip()
        message = Path(temporary) / 'commit-message.txt'
        message.write_text('Revise Neural Bellman Operators after the latest advisory referee report\n\n'
            'Publish four rebuilt review documents, complete preserved scientific evidence,\n'
            'source identities, independent report replay, and final publication audits.\n\n'
            'Delivery source: ' + source + '\n')
        final = git(repo, 'commit-tree', tree, '-p', source, '-F', str(message), env=env).decode().strip()
    return final, changed


def publish(repo, source, execute=False):
    repo = Path(repo).resolve()
    preflight(repo, source, require_sparse=execute)
    final_audit, ledger, manifest = verify_payload(repo, source)
    if not execute:
        return dict(ready=True, publication_source_commit=source, targets=list(TARGET_BRANCHES),
                    mutation_performed=False, scope='Payload verified; no commit or remote write without --execute in the delivery CI.')
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_SHA') == source,
            'publication execution is restricted to the frozen delivery CI')
    require(str(os.environ.get('GITHUB_RUN_ID')) == str(final_audit['delivery_identity']['github_run_id']), 'audit belongs to another CI run')
    store = GitStore(repo)
    try:
        source_tree = store.tree(source)
        updates = dict(manifest['files'])
        for name in ('EVIDENCE_MANIFEST.json', 'FINAL_AUDIT.json'):
            path = R / name
            updates[str(path)] = dict(**file_record(repo / path), mode='100644', storage='materialized')
        final, changed = construct_commit(repo, source, source_tree, updates)
        verify_final_tree(store, source, final, ledger, manifest)
        # Check both immediately before the transaction; empty leases also close
        # the race between this check and the remote atomic update.
        preflight(repo, source, require_sparse=True)
        subprocess.run(atomic_push_command(final), cwd=repo, check=True)
        require(all(remote_ref(repo, branch) == final for branch in TARGET_BRANCHES), 'remote refs do not all identify audited F')
        result = dict(publication_source_commit=source, publication_commit=final, target_branches=list(TARGET_BRANCHES),
                      changed_payload_files=len(changed), all_refs_created_atomically=True)
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as handle:
                handle.write('## NBO R16 publication\n\nDelivery source D: `' + source + '`\n\nPublication F: `' + final + '`\n\n')
                for branch in TARGET_BRANCHES:
                    handle.write('- `' + branch + '`\n')
        return result
    finally:
        store.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['preflight', 'fetch-sources', 'materialize', 'verify-payload', 'publish'])
    parser.add_argument('--repo', default='.')
    parser.add_argument('--publication-source', required=True)
    parser.add_argument('--require-sparse', action='store_true')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if args.command == 'preflight':
        result = preflight(repo, args.publication_source, args.require_sparse)
    elif args.command == 'fetch-sources':
        result = fetch_sources(repo, args.publication_source)
    elif args.command == 'materialize':
        result = materialize(repo, args.publication_source)
    elif args.command == 'verify-payload':
        final, _, _ = verify_payload(repo, args.publication_source)
        result = dict(complete=True, payload_files=final['payload_files'])
    else:
        result = publish(repo, args.publication_source, args.execute)
    print(json.dumps(result, indent=2, allow_nan=False))
