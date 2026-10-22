"""Losslessly promote explicitly manifested author files before the final source commit.

This administrative transport does not build a PDF, call a scientific program,
or modify an experimental protocol. Its source commit authenticates all payload
bytes; its distinct publication commit contains the ordinary native files.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = 'revisions/2026-10-20-r122/'
BRANCH = 'revision/econometrica-nbo-r122-action-information-2026-10-20'
REPOSITORY = 'TrillionniumFoundation/NBO'
TRIGGER = PREFIX + 'AUTHOR_SOURCE_PROMOTION_TRIGGER122.json'
WORKFLOW = '.github/workflows/nbo-r122-author-source-promotion.yml'
DRIVER = PREFIX + 'verification122/promote_author_source122.py'
FREEZE = PREFIX + 'SOURCE_FREEZE122.json'
FREEZE_SHA = 'eba26439a799392b7553d06fea5f17828c8988b9f72f4e049058771985ac8b0f'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def canonical(name):
    need(isinstance(name, str) and name, 'Nonempty relative path required')
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and '.git' not in p.parts
         and '\\' not in name and str(p) == name and name != '.', 'Unsafe path: ' + repr(name))
    return name


def native(name, exists=True):
    path = REPO
    for part in PurePosixPath(canonical(name)).parts:
        path /= part
        need(not path.is_symlink(), 'Symlink component: ' + name)
    need(path.resolve().is_relative_to(REPO), 'Path escapes checkout')
    if exists:
        need(path.is_file(), 'Missing ordinary native file: ' + name)
    return path


def git(*args, env=None):
    return subprocess.check_output(['git', *args], cwd=REPO, env=env)


def blob_at(commit, name):
    output = git('ls-tree', commit, '--', name).decode().strip()
    if not output:
        return None
    info, actual_name = output.split('\t', 1)
    mode, kind, identity = info.split()
    need(actual_name == name and kind == 'blob' and mode in ('100644', '100755'), 'Expected ordinary Git blob')
    return identity


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    need(os.environ.get('GITHUB_ACTIONS') == 'true', 'Actual GitHub runner required')
    need(os.environ['GITHUB_REPOSITORY'] == REPOSITORY, 'Wrong repository')
    need(os.environ['GITHUB_REF'] == 'refs/heads/' + BRANCH, 'Wrong isolated branch')
    need(Path(os.environ['GITHUB_WORKSPACE']).resolve() == REPO, 'Wrong checkout')
    source = os.environ['GITHUB_SHA']
    need(git('rev-parse', 'HEAD').decode().strip() == source, 'Event and checkout differ')
    run_id, attempt = os.environ['GITHUB_RUN_ID'], os.environ['GITHUB_RUN_ATTEMPT']
    need(run_id.isdigit() and attempt.isdigit(), 'Invalid workflow identity')
    admin = ROOT / ('provenance122/author-source-promotion-' + run_id + '-' + attempt)
    admin.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    state = dict(status='started', transport_source_commit=source,
        workflow_run_id=run_id, workflow_run_attempt=attempt,
        started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        publication_attempts=[], new_economic_evaluations=0, new_training=0,
        new_initial_states=0, new_service_timings=0,
        scope='Exact administrative source promotion before the final ordinary native author source commit; no science or PDF execution.')
    try:
        request = json.loads(native(TRIGGER).read_text())
        need(request['schema'] == 'nbo.r122.author-source-promotion.v1', 'Wrong trigger schema')
        manifest_name = canonical(request['manifest'])
        need(manifest_name.startswith(PREFIX + 'transport122/author-source/'), 'Manifest outside author transport')
        manifest_path = native(manifest_name)
        need(digest(manifest_path) == request['manifest_sha256'], 'Trigger/manifest mismatch')
        manifest = json.loads(manifest_path.read_text())
        need(manifest['schema'] == 'nbo.r122.exact-author-source-transport.v1', 'Wrong transport schema')
        need(manifest['path_root'] == 'repository' and manifest['scientific_execution'] is False, 'Wrong transport scope')
        members = manifest['files']
        names = [canonical(x['path']) for x in members]
        need(members and len(names) == len(set(names)), 'Empty or duplicate author files')
        need(all(x.startswith(PREFIX) or (x.startswith('.github/workflows/nbo-r122-') and x.endswith('.yml')) for x in names), 'Target outside isolated revision scope')
        current_admin = admin.relative_to(REPO).as_posix() + '/'
        need(not any(x.startswith(current_admin) for x in names), 'Payload cannot replace this run\'s own custody receipts')
        part_names = [canonical(x['path']) for x in manifest['parts']]
        need(part_names and len(part_names) == len(set(part_names)), 'Missing or duplicate transport parts')
        guarded = [TRIGGER, WORKFLOW, DRIVER, FREEZE, manifest_name, *part_names]
        need(len(guarded) == len(set(guarded)) and not (set(names) & set(guarded)), 'Payload cannot replace its own executing source')
        guards = []
        for name in guarded:
            path = native(name)
            data = git('show', source + ':' + name)
            need(data == path.read_bytes(), 'Executing transport differs from source: ' + name)
            guards.append(dict(path=name, bytes=len(data), sha256=sha(data), git_blob=blob_at(source, name)))
        write(admin / 'SOURCE_GATE122.json', dict(status='verified_before_extraction', transport_source_commit=source, files=guards))
        need(digest(native(FREEZE)) == FREEZE_SHA, 'Frozen scientific manifest changed')
        scientific_files = json.loads(native(FREEZE).read_text())['scientific_files']
        # The base-blob condition authenticates replacements and protects work
        # added concurrently after this explicitly selected snapshot.
        for item in members:
            need(item['mode'] in ('100644', '100755'), 'Unsupported native mode')
            if item['path'] in scientific_files:
                need(item['sha256'] == scientific_files[item['path']], 'Frozen scientific member cannot change')
            need(blob_at(source, item['path']) == item['base_blob'], 'Target base changed before execution: ' + item['path'])
        with tempfile.TemporaryDirectory(prefix='nbo-r122-author-promotion-') as temp:
            archive = Path(temp) / 'author-source.zip'
            with archive.open('xb') as output:
                for part in manifest['parts']:
                    need(part['path'].startswith(PREFIX + 'transport122/author-source/'), 'Part outside author transport')
                    path = native(part['path'])
                    need(path.stat().st_size == part['bytes'] and digest(path) == part['sha256'], 'Part digest mismatch')
                    need(path.stat().st_size <= 184320, 'Transport part exceeds bounded payload rule')
                    output.write(path.read_bytes())
            need(archive.stat().st_size == manifest['archive_bytes'] and digest(archive) == manifest['archive_sha256'], 'Reconstructed archive differs')
            expected = {item['path']: item for item in members}
            with zipfile.ZipFile(archive) as zipped:
                infos = zipped.infolist()
                need(len(infos) == len(members) and {x.filename for x in infos} == set(names), 'Archive membership differs')
                need(len({x.filename for x in infos}) == len(infos), 'Duplicate ZIP member')
                for info in infos:
                    need(not info.is_dir() and ((info.external_attr >> 16) & 0o170000) in (0, 0o100000), 'Non-file ZIP member')
                    item = expected[info.filename]
                    need(info.file_size == item['bytes'] and info.file_size < 95 * 1024 * 1024, 'Wrong or oversized native member')
                    data = zipped.read(info)
                    need(sha(data) == item['sha256'], 'Native member digest mismatch')
                    actual_git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                    need(actual_git_blob == item['git_blob'], 'Native Git blob mismatch')
                    path = native(item['path'], exists=False)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open('wb') as output:
                        output.write(data)
                    path.chmod(0o755 if item['mode'] == '100755' else 0o644)
        for item in members:
            path = native(item['path'])
            data = path.read_bytes()
            mode = '100755' if path.stat().st_mode & 0o111 else '100644'
            need(len(data) == item['bytes'] and sha(data) == item['sha256'], 'Actual reconstructed native bytes differ')
            need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == item['git_blob'], 'Actual native Git blob differs')
            need(mode == item['mode'], 'Actual native mode differs')
        write(admin / 'NATIVE_READBACK122.json', dict(status='verified_exact_author_bytes',
            transport_source_commit=source, source_manifest=manifest_name,
            source_manifest_sha256=digest(manifest_path), native_files=len(members),
            native_bytes=sum(x['bytes'] for x in members), files=members,
            new_economic_evaluations=0))
        selected = sorted(set(names) | {p.relative_to(REPO).as_posix() for p in admin.rglob('*') if p.is_file()})
        hashes = {name: digest(native(name)) for name in selected}
        for retry in range(3):
            tick = time.perf_counter()
            log = admin / ('publication-' + str(retry + 1) + '.log')
            event = dict(attempt=retry + 1, log=log.relative_to(ROOT).as_posix())
            try:
                with log.open('xb') as output:
                    subprocess.run(['git', 'fetch', '--filter=blob:none', '--depth=256', 'origin', BRANCH], cwd=REPO, stdout=output, stderr=subprocess.STDOUT, check=True)
                    parent = git('rev-parse', 'FETCH_HEAD').decode().strip()
                    subprocess.run(['git', 'merge-base', '--is-ancestor', source, parent], cwd=REPO, check=True)
                    for item in guards:
                        need(blob_at(parent, item['path']) == item['git_blob'], 'Transport source changed during promotion')
                    for item in members:
                        need(blob_at(parent, item['path']) in (item['base_blob'], item['git_blob']), 'Concurrent target edit would be replaced')
                    need(all(digest(native(name)) == value for name, value in hashes.items()), 'Checked bytes changed before publication')
                    with tempfile.TemporaryDirectory(prefix='nbo-r122-promotion-index-') as temp:
                        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'index'))
                        subprocess.run(['git', 'read-tree', parent], cwd=REPO, env=env, check=True)
                        # Avoid an operating-system argument-size limit while
                        # keeping exactly the declared ordinary file set.
                        for offset in range(0, len(selected), 100):
                            subprocess.run(['git', 'add', '--force', '--sparse', '--', *selected[offset:offset+100]], cwd=REPO, env=env, check=True)
                        tree = git('write-tree', env=env).decode().strip()
                        changed = set(git('diff-tree', '--no-commit-id', '--name-only', '-r', parent, tree).decode().splitlines())
                        need(changed and changed <= set(selected), 'Undeclared publication path')
                        commit = git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                            'commit-tree', tree, '-p', parent, '-m', 'R122: promote exact completed author sources and preserved administrative evidence').decode().strip()
                    subprocess.run(['git', 'push', 'origin', commit + ':refs/heads/' + BRANCH], cwd=REPO, stdout=output, stderr=subprocess.STDOUT, check=True)
                    actual = git('ls-remote', 'origin', 'refs/heads/' + BRANCH).decode().split()[0]
                    if actual != commit:
                        subprocess.run(['git', 'fetch', '--filter=blob:none', '--depth=256', 'origin', actual], cwd=REPO, check=True)
                        subprocess.run(['git', 'merge-base', '--is-ancestor', commit, actual], cwd=REPO, check=True)
                    for name in selected:
                        need(sha(git('show', commit + ':' + name)) == hashes[name], 'Published native readback failed')
                    for item in members:
                        published_mode = git('ls-tree', commit, '--', item['path']).decode().split()[0]
                        need(published_mode == item['mode'], 'Published native mode differs')
                    event.update(status='published_and_read_back', parent=parent, commit=commit,
                        changed_files=len(changed), selected_files=len(selected), force=False)
                    state['publication_commit'] = commit
                break
            except Exception as error:
                event.update(status='failed', error=repr(error))
                if retry == 2:
                    raise
            finally:
                event.update(elapsed_seconds=time.perf_counter()-tick, log_sha256=digest(log))
                state['publication_attempts'].append(event)
        state.update(status='completed_exact_author_source_promotion', native_files=len(members),
            source_manifest_sha256=digest(manifest_path), final_author_release_CI_success_asserted=False)
    except BaseException:
        state.update(status='failed', traceback=traceback.format_exc())
        raise
    finally:
        state.update(elapsed_seconds=time.perf_counter()-started,
            finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(), whole_study_exact_total_seconds=None,
            cost_clock_components=[dict(category='author_source_promotion_parent',
                clock_fields=[['elapsed_seconds']], partial_lower_bound_only=True,
                overlaps_counted_parent=False,
                scope='Actual whole source-promotion parent; enclosed extraction, native readback and publication stages are not additional costs.')],
            unmeasured_scope='Checkout/setup and terminal artifact upload lie outside this actual clock; interrupted historical costs remain unknown.')
        write(admin / 'FINAL_SOURCE_PROMOTION_STATUS122.json', state)


if __name__ == '__main__':
    main()
