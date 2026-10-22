"""Authenticate the existing completed recovery artifact and preserve its final admin bytes.

No numerical program is called. The large artifact is downloaded on the runner
because the connector's 512 MiB download limit is smaller than this actual ZIP.
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
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BRANCH = 'revision/econometrica-nbo-r122-action-information-2026-10-20'
REPOSITORY = 'TrillionniumFoundation/NBO'
ORIGINAL = 'provenance122/runtime-recovery-39691016040-1/'
BASE = '5635a3a0af330933b3ff1b9331ba4fe468eac628'
R122 = 'revisions/2026-10-20-r122/'
OWN = ['verification122/extract_recovery_artifact122.py', 'provenance122/ARTIFACT_CUSTODY_PROTOCOL122.md', 'ARTIFACT_CUSTODY_TRIGGER122.json']
WORKFLOW = '.github/workflows/nbo-r122-artifact-custody.yml'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def git(*args, env=None):
    return subprocess.check_output(['git', *args], cwd=REPO, env=env)


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + '\n')


def main():
    started = time.perf_counter()
    source = os.environ['GITHUB_SHA']
    assert os.environ['GITHUB_REPOSITORY'] == REPOSITORY
    assert os.environ['GITHUB_REF'] == 'refs/heads/' + BRANCH
    assert git('rev-parse', 'HEAD').decode().strip() == source
    run_id, attempt = os.environ['GITHUB_RUN_ID'], os.environ['GITHUB_RUN_ATTEMPT']
    assert run_id.isdigit() and attempt.isdigit()
    admin = ROOT / ('provenance122/artifact-custody-' + run_id + '-' + attempt)
    admin.mkdir(parents=True, exist_ok=False)
    state = dict(status='started', source_commit=source, workflow_run_id=run_id,
        workflow_run_attempt=attempt, started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        stages=[], publication_attempts=[], new_economic_evaluations=0,
        scope='Existing completed artifact custody only; no experimental input, result, clock, or criterion is replaced.')
    def stage(label, command, binary_output=None):
        tick = time.perf_counter()
        log = admin / (label + '.log')
        with log.open('wb') as errors:
            if binary_output:
                with binary_output.open('wb') as stream:
                    result = subprocess.run(command, cwd=REPO, stdout=stream, stderr=errors)
            else:
                result = subprocess.run(command, cwd=REPO, stdout=errors, stderr=subprocess.STDOUT)
        state['stages'].append(dict(label=label, command=command, exit_code=result.returncode,
            elapsed_seconds=time.perf_counter()-tick, log=log.relative_to(ROOT).as_posix(), log_sha256=digest(log)))
        if result.returncode:
            raise RuntimeError('Actual custody stage failed: ' + label)
    try:
        source_rows = []
        for name in [R122 + x for x in OWN] + [WORKFLOW]:
            data = (REPO / name).read_bytes()
            assert git('show', source + ':' + name) == data
            source_rows.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
        write(admin / 'SOURCE_GATE122.json', dict(status='verified_before_artifact_retrieval', source_commit=source, files=source_rows))
        request = json.loads((ROOT / 'ARTIFACT_CUSTODY_TRIGGER122.json').read_text())
        assert request == dict(schema='nbo.r122.completed-artifact-custody.v1', run_id=39691016040,
            artifact_id=12391656973, artifact_bytes=630176089,
            artifact_sha256='92ba7a1ec1584a50017e4fb49a1d695a1e2bc53dd526477ecffd0c43891c29cf',
            experiment_source='6ab1f9d4f1f9eb70014a7d104b84a499b64ba84c', terminal_commit=BASE)
        for label, endpoint in [('artifact-metadata', 'actions/artifacts/12391656973'), ('run-metadata', 'actions/runs/39691016040')]:
            stage(label, ['gh', 'api', 'repos/' + REPOSITORY + '/' + endpoint], admin / (label + '.json'))
        meta = json.loads((admin / 'artifact-metadata.json').read_text())
        run = json.loads((admin / 'run-metadata.json').read_text())
        assert meta['id'] == request['artifact_id'] and meta['size_in_bytes'] == request['artifact_bytes'] and not meta['expired']
        assert meta['digest'] == 'sha256:' + request['artifact_sha256']
        assert meta['workflow_run']['id'] == request['run_id'] and meta['workflow_run']['head_sha'] == request['experiment_source']
        assert run['id'] == request['run_id'] and run['status'] == 'completed' and run['conclusion'] == 'success'
        assert run['head_sha'] == request['experiment_source']
        archive = Path(os.environ['RUNNER_TEMP']) / ('r122-artifact-' + run_id + '.zip')
        assert not archive.exists()
        stage('download-completed-artifact', ['gh', 'api', 'repos/' + REPOSITORY + '/actions/artifacts/12391656973/zip'], archive)
        assert archive.stat().st_size == request['artifact_bytes'] and digest(archive) == request['artifact_sha256']
        retained = []
        with zipfile.ZipFile(archive) as saved:
            infos = saved.infolist()
            assert len({x.filename for x in infos}) == len(infos)
            selected = [x for x in infos if x.filename.startswith(ORIGINAL) and not x.is_dir()]
            assert selected and sum(x.file_size for x in selected) < 50 * 1024 * 1024
            for info in selected:
                name = PurePosixPath(info.filename)
                assert not name.is_absolute() and '..' not in name.parts and '\\' not in info.filename and str(name) == info.filename
                assert ((info.external_attr >> 16) & 0o170000) in (0, 0o100000)
                data = saved.read(info)
                target = admin / 'native' / info.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(data)
                retained.append(dict(original_path=info.filename, native_path=target.relative_to(ROOT).as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
        native_admin = admin / 'native' / ORIGINAL
        status = json.loads((native_admin / 'RECOVERY_STATUS122.json').read_text())
        assert status['status'] == 'completed_recovery_science_and_report' and status['source_commit'] == request['experiment_source']
        assert all(status[k] == 0 for k in ['new_initial_states', 'new_training', 'new_primary_decisions', 'new_service_timing_replicates'])
        for row in status['publications']:
            assert row['path'].startswith(ORIGINAL)
            path = admin / 'native' / row['path']
            assert digest(path) == row['sha256']
            assert json.loads(path.read_text())['commit'] == row['commit']
        assert status['publications'][-1]['commit'] == BASE
        for item in status['stages']:
            assert item['log'].startswith(ORIGINAL)
            assert digest(admin / 'native' / item['log']) == item['log_sha256']
        state['authenticated_recovery_publications'] = len(status['publications'])
        state['retained_admin_files'] = len(retained)
        state['original_artifact_sha256'] = request['artifact_sha256']
        write(admin / 'EXTRACTION122.json', dict(status='verified_complete_final_admin_snapshot',
            source_commit=source, artifact=request, files=retained, terminal_commit=BASE,
            elapsed_seconds=time.perf_counter()-started, new_economic_evaluations=0,
            scope='Every original completed recovery admin byte is retained under a new prefix; the prior Git status is untouched.'))
        selected_paths = sorted(p.relative_to(REPO).as_posix() for p in admin.rglob('*') if p.is_file())
        selected_hashes = {name: digest(REPO / name) for name in selected_paths}
        for retry in range(3):
            tick = time.perf_counter(); log = admin / ('publication-' + str(retry + 1) + '.log')
            record = dict(attempt=retry + 1, log=log.relative_to(ROOT).as_posix())
            try:
                with log.open('wb') as stream:
                    subprocess.run(['git', 'fetch', '--filter=blob:none', '--depth=128', 'origin', BRANCH], cwd=REPO, stdout=stream, stderr=subprocess.STDOUT, check=True)
                    parent = git('rev-parse', 'FETCH_HEAD').decode().strip()
                    subprocess.run(['git', 'merge-base', '--is-ancestor', source, parent], cwd=REPO, check=True)
                    for name in [R122 + x for x in OWN] + [WORKFLOW]:
                        assert git('rev-parse', parent + ':' + name) == git('rev-parse', source + ':' + name)
                    with tempfile.TemporaryDirectory(prefix='nbo-r122-custody-index-') as tmp:
                        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
                        subprocess.run(['git', 'read-tree', parent], cwd=REPO, env=env, check=True)
                        assert all(digest(REPO / name) == expected for name, expected in selected_hashes.items())
                        subprocess.run(['git', 'add', '--force', '--sparse', '--', *selected_paths], cwd=REPO, env=env, check=True)
                        tree = git('write-tree', env=env).decode().strip()
                        changed = set(git('diff-tree', '--no-commit-id', '--name-only', '-r', parent, tree).decode().splitlines())
                        assert changed <= set(selected_paths) and changed
                        commit = git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                            'commit-tree', tree, '-p', parent, '-m', 'R122: preserve authenticated terminal recovery artifact custody').decode().strip()
                    subprocess.run(['git', 'push', 'origin', commit + ':refs/heads/' + BRANCH], cwd=REPO, stdout=stream, stderr=subprocess.STDOUT, check=True)
                    actual = git('ls-remote', 'origin', 'refs/heads/' + BRANCH).decode().split()[0]
                    if actual != commit:
                        subprocess.run(['git', 'fetch', '--depth=128', 'origin', actual], cwd=REPO, check=True)
                        subprocess.run(['git', 'merge-base', '--is-ancestor', commit, actual], cwd=REPO, check=True)
                    for name in selected_paths:
                        assert hashlib.sha256(git('show', commit + ':' + name)).hexdigest() == selected_hashes[name]
                    record.update(status='published_and_read_back', parent=parent, commit=commit, observed_remote_head=actual)
                state['publication_commit'] = commit
                break
            except Exception as error:
                record.update(status='failed', error=repr(error))
                if retry == 2:
                    raise
            finally:
                record.update(elapsed_seconds=time.perf_counter()-tick, log_sha256=digest(log))
                state['publication_attempts'].append(record)
        state['status'] = 'completed_artifact_custody_and_publication'
    except Exception as error:
        state.update(status='failed', error=repr(error))
        raise
    finally:
        state.update(elapsed_seconds=time.perf_counter()-started,
            finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
            cost_clock_components=[dict(category='artifact_custody_publication', clock_fields=[['elapsed_seconds']],
                scope='Whole actual custody driver including download, extraction, validation and publication; enclosed stages are not additional charges.',
                partial_lower_bound_only=True, overlaps_counted_parent=False)],
            unmeasured_scope='Workflow checkout/setup and artifact upload are outside this clock; no whole-study total is asserted.')
        write(admin / 'FINAL_CUSTODY_STATUS122.json', state)


if __name__ == '__main__':
    main()
