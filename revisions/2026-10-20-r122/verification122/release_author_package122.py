"""Build and publish a source-bound final R122 author package on its actual runner.

No economic solver, state draw, actor fit or service timing campaign is called.
The actual runner build, source/PDF manifest and offline-verified archive become
this publication's artifacts. Local preflight PDFs have separate identities.
"""
from __future__ import annotations
import datetime as dt
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = 'revisions/2026-10-20-r122/'
BRANCH = 'revision/econometrica-nbo-r122-action-information-2026-10-20'
F = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
D = 'a3323b6f557315ea91b536637419ef6fd7984b61'
CONFIG = 'AUTHOR_RELEASE_CONFIG122.json'
WORKFLOW = '.github/workflows/nbo-r122-author-release.yml'
VERIFIER_SHA = 'ac5656f350fb126ccb096fc1ba71565ba0a37fa71fe2521bfd2a1e93da3e9a07'
LEDGER_SHA = '37efa69184cca24946aec4e6914de10c848509709f3b24e5d67edc4cc028e08c'
ALIASES = (Path('/workspace/scratch/411f2ee67342/NBO'), Path('/dev/shm/nbo-r122-411f2ee67342/NBO'))


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def canonical(name):
    need(isinstance(name, str) and name, 'Nonempty relative file name required')
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and '.git' not in p.parts
         and '\\' not in name and str(p) == name and name != '.', 'Unsafe path ' + repr(name))
    return name


def native(root, name, required=True):
    path = root
    for part in PurePosixPath(canonical(name)).parts:
        path /= part
        need(not path.is_symlink(), 'Native file cannot have a symlink component')
    need(path.resolve().is_relative_to(root), 'Native path escapes declared root')
    if required:
        need(path.is_file(), 'Missing ordinary native file: ' + str(path))
    return path


def row(path):
    return dict(path=path.relative_to(REPO).as_posix(), bytes=path.stat().st_size, sha256=digest(path))


def git(*args, env=None):
    return subprocess.check_output(['git', *args], cwd=REPO, env=env)


def tree_entries(commit, names):
    """Read selected native path identities, including their absence at S.

    A concurrent descendant may add unrelated evidence. It must not create or
    replace one of this publication's explicit targets before our normal push.
    This is a comparison of immutable trees, not a worktree reset or ref edit.
    """
    entries = {}
    for item in git('ls-tree', '-r', '-z', '--full-tree', commit, '--', *names).split(b'\0'):
        if not item:
            continue
        metadata, name = item.split(b'\t', 1)
        mode, kind, blob = metadata.decode().split()
        name = name.decode()
        need(name in names and kind == 'blob' and mode in ('100644', '100755'),
             'Publication source contains an unexpected non-native target')
        entries[name] = dict(mode=mode, git_blob=blob)
    return entries


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(obj, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    need(os.environ.get('GITHUB_ACTIONS') == 'true', 'Actual GitHub runner required')
    need(os.environ['GITHUB_REPOSITORY'] == 'TrillionniumFoundation/NBO', 'Wrong repository')
    need(os.environ['GITHUB_REF'] == 'refs/heads/' + BRANCH, 'Wrong isolated revision branch')
    need(Path(os.environ['GITHUB_WORKSPACE']).resolve() == REPO, 'Wrong native checkout')
    source = os.environ['GITHUB_SHA']
    need(git('rev-parse', 'HEAD').decode().strip() == source, 'Event source differs from checked-out source')
    run_id, attempt = os.environ['GITHUB_RUN_ID'], os.environ['GITHUB_RUN_ATTEMPT']
    need(run_id.isdigit() and attempt.isdigit(), 'Invalid actual workflow identity')
    tag = 'author-release-' + run_id + '-' + attempt
    admin = ROOT / 'provenance122' / tag
    admin.mkdir(parents=True, exist_ok=False)
    release = ROOT / 'referee_ready122' / tag
    release.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    state = dict(status='started', author_source_commit_S=source, workflow_run_id=run_id,
        workflow_run_attempt=attempt, started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        stages=[], publication_attempts=[], new_states=0, new_training=0,
        new_economic_evaluations=0, new_service_timing_processes=0,
        scope='Actual runner author build, saved evidence validation and scoped normal publication; no scientific rerun.')
    preledger = None
    ledger = None

    def run(label, command):
        tick = time.perf_counter()
        log = admin / (label + '.log')
        with log.open('xb') as stream:
            done = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        record = dict(label=label, command=command, exit_code=done.returncode,
            elapsed_seconds=time.perf_counter()-tick, log=log.relative_to(ROOT).as_posix(), log_sha256=digest(log))
        state['stages'].append(record)
        print(json.dumps({key: record[key] for key in ('label', 'exit_code', 'elapsed_seconds')}), flush=True)
        need(done.returncode == 0, 'Actual release stage failed: ' + label)

    try:
        config = json.loads(native(ROOT, CONFIG).read_text())
        need(config['schema'] == 'nbo.r122.runner-author-release.v1', 'Unexpected release configuration')
        need(config['source_commit_F'] == F and config['state_commit_D'] == D, 'Scientific identities differ')
        need(digest(ROOT / 'verification122/verify_package122.py') == VERIFIER_SHA, 'Frozen verifier changed')
        need(digest(ROOT / 'verification122/research_cost_ledger122.py') == LEDGER_SHA, 'Frozen ledger changed')
        guard_file = native(ROOT, config['source_guard_paths'])
        guard_names = json.loads(guard_file.read_text())
        required_guard = {PREFIX + CONFIG, PREFIX + 'verification122/release_author_package122.py', WORKFLOW,
            PREFIX + config['source_guard_paths'], PREFIX + config['static_native_manifest'],
            PREFIX + config['additional_cost_receipts'], PREFIX + 'verification122/ci_verify122.py',
            PREFIX + 'verification122/restore_author_dependencies_after_upload122.py',
            PREFIX + 'verification122/author_pdf_inspection_runtime03_122.py', PREFIX + 'AUTHOR_RELEASE_TRIGGER122.json'}
        need(isinstance(guard_names, list) and len(guard_names) == len(set(guard_names))
             and required_guard <= set(guard_names), 'Incomplete explicit publication source guard')
        guards = []
        for name in sorted(guard_names):
            path = native(REPO, name)
            data = git('show', source + ':' + name)
            need(len(data) == path.stat().st_size and hashlib.sha256(data).hexdigest() == digest(path),
                 'Author source is not the event commit: ' + name)
            guards.append(dict(row(path), git_blob=git('rev-parse', source + ':' + name).decode().strip()))
        write(admin / 'SOURCE_GATE122.json', dict(status='verified_before_build', author_source_commit_S=source,
            files=guards, frozen_verifier_sha256=VERIFIER_SHA, frozen_ledger_sha256=LEDGER_SHA))
        for alias in ALIASES:
            if alias == REPO:
                continue
            if alias.is_symlink():
                need(alias.resolve() == REPO, 'Unrelated existing historical alias')
            else:
                need(not alias.exists(), 'Existing historical path must not be displaced')
                subprocess.run(['sudo', 'mkdir', '-p', str(alias.parent)], check=True)
                subprocess.run(['sudo', 'ln', '-sT', str(REPO), str(alias)], check=True)
            need(alias.resolve() == REPO, 'Historical path alias differs')
        # Fetch immutable trees and sufficient ancestry; never weaken source or
        # merge-base checks to accommodate a shallow checkout.
        for index, commit in enumerate(config['immutable_commits']):
            need(len(commit) == 40 and all(c in '0123456789abcdef' for c in commit), 'Full immutable commit required')
            run('fetch-source-' + str(index), ['git', 'fetch', '--filter=tree:0', '--depth=256', 'origin', commit])
        run('restore-exact-historical-dependencies', [sys.executable,
            'verification122/restore_author_dependencies_after_upload122.py',
            '--output', str(admin / 'HISTORICAL_DEPENDENCIES122.json')])
        registry = native(ROOT, config['transport_registry'])
        need(digest(registry) == config['transport_registry_sha256'], 'Source-bound evidence registry changed')
        run('materialize-saved-evidence', [sys.executable, 'verification122/materialize_evidence122.py',
            '--registry', str(registry), '--output', str(admin / 'MATERIALIZATION122.json')])
        selected = json.loads(native(ROOT, config['static_native_manifest']).read_text())
        need(selected['path_root'] == 'repository' and selected['self_excluded'] is True, 'Wrong explicit static input root')
        records = selected['files']; names = [item['path'] for item in records]
        need(records and len(names) == len(set(names)), 'Empty or duplicate static native inputs')
        need(not any(name.startswith(PREFIX + 'build/') or name.startswith(PREFIX + 'referee_ready122/')
             or name.startswith(admin.relative_to(REPO).as_posix() + '/')
             or name == PREFIX + 'PUBLICATION_INPUTS122.json' for name in names),
             'Static inputs cannot include mutable build/PUBLICATION_INPUTS/current-release outputs')
        restored = []
        for item in records:
            path = native(REPO, item['path'], required=False)
            if not path.exists():
                data = git('show', source + ':' + item['path'])
                need(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'],
                     'Missing native member differs from exact source commit')
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(data)
                restored.append(item['path'])
            need(path.is_file() and path.stat().st_size == item['bytes'] and digest(path) == item['sha256'],
                 'Existing static native input differs; it cannot be overwritten: ' + item['path'])
        write(admin / 'STATIC_NATIVE_READBACK122.json', dict(status='verified', native_members=len(records),
            source_commit=source, restored_absent_from_same_commit=restored,
            static_manifest_sha256=digest(native(ROOT, config['static_native_manifest']))))
        run('prewarm', [sys.executable, 'verification122/prewarm_git_objects122.py', '--source-commit', F,
            '--state-commit', D, '--resume-publication', config['resume_publication'],
            '--output', str(admin / 'PREWARM122.json')])
        composite = [sys.executable, 'verification122/verify_independent_resume122.py', '--source-commit', F,
            '--state-commit', D, '--resume-publication', config['resume_publication'],
            '--primary', 'results122/primary-attempt02', '--independent', config['independent_directory']]
        run('saved-composite-verification', composite + ['--output', str(admin / 'composite-verification')])
        build_dir = 'build_receipts122_release/' + tag
        run('actual-four-document-build', [sys.executable, 'build122.py', '--receipt-dir', build_dir])
        builds = list((ROOT / build_dir).glob('*/BUILD_RECEIPT122.json'))
        need(len(builds) == 1, 'Exactly one current actual four-document build required')
        build_path = builds[0]; build = json.loads(build_path.read_text())
        need(build['status'] == 'compiled_clean' and not build['issues'] and not build['placeholders'], 'Actual author build is not clean')
        need(build['diagnostic'] is False and build['scientific_execution'] is False, 'Wrong build scope')
        build_source_paths = set(build['source_sha256']) | set(build.get('graphic_asset_sha256', {}))
        for paths in build['actual_project_inputs'].values():
            build_source_paths.update(paths)
        by_guard = {item['path']: item for item in guards}
        need({PREFIX + name for name in build_source_paths} <= set(by_guard),
             'An actual document source or graphic dependency is not guarded against concurrent parent changes')
        for name in sorted(build_source_paths):
            need(digest(native(ROOT, name)) == by_guard[PREFIX + name]['sha256'],
                 'An actual document source changed after sourceS was authenticated')
        run('actual-pdf-content-and-geometry', [sys.executable,
            'verification122/author_pdf_inspection_runtime03_122.py', '--build-receipt', str(build_path),
            '--output', str(admin / 'pdf-inspection')])
        inspection = json.loads((admin / 'pdf-inspection/PDF_INSPECTION122.json').read_text())
        need(inspection['status'] == 'executed' and inspection['exit_code'] == 0
             and not inspection['physical_page_boundary_exceptions'], 'Actual PDF text/geometry check failed')
        inclusion = [item for item in inspection['content_checks'] if item.get('kind') == 'complete_catalogue_inclusion']
        need(len(inclusion) == 1 and inclusion[0]['source_pages'] == 8
             and inclusion[0]['exact_whitespace_normalized_text_equal'] is True
             and inclusion[0]['same_page_size'] is True, 'The eight actual catalogue pages are not preserved')
        # The frozen ledger automatically includes these build command clocks.
        # Count every other elapsed part of this actual parent only once.
        preledger = Q(time.perf_counter()-started)
        build_commands = sum((Q(item['elapsed_seconds']) for item in build['commands']), Q(0))
        need(preledger >= build_commands, 'Build command clocks exceed their actual parent')
        preledger_path = admin / 'PRE_LEDGER_COST122.json'
        write(preledger_path, dict(status='recorded_actual_preledger_clock',
            parent_seconds_exact=str(preledger), already_counted_build_command_seconds_exact=str(build_commands),
            nonoverlapping_preledger_seconds_exact=str(preledger-build_commands),
            cost_clock_components=[dict(category='author_release_preledger_parent_residual',
                clock_fields=[['nonoverlapping_preledger_seconds_exact']], partial_lower_bound_only=True,
                overlaps_counted_parent=False, scope='This actual release parent through build, less its automatically counted serial TeX/BibTeX commands. Enclosed source retrieval, materialization, prewarm and saved-composite clocks are not additional charges.')],
            later_release_work_not_in_this_clock=True, whole_study_total_seconds=None))
        extra = json.loads(native(ROOT, config['additional_cost_receipts']).read_text())
        need(isinstance(extra, list) and len(extra) == len(set(extra)), 'Explicit unique extra cost paths required')
        for name in extra:
            native(ROOT, name)
        ledger_dir = release / 'cost-ledger'
        run('actual-cost-ledger', [sys.executable, 'verification122/research_cost_ledger122.py',
            '--source-commit', F, '--state-commit', D, '--additional-receipts', *extra,
            str(preledger_path), '--output', str(ledger_dir)])
        ledger = json.loads((ledger_dir / 'COST_LEDGER122.json').read_text())
        need(ledger['whole_study_exact_total_seconds'] is None, 'Unknown full research duration was invented')
        source_paths = set(build_source_paths)
        source_paths.update(item['path'] for item in build['pdfs'])
        source_paths.add(build_path.relative_to(ROOT).as_posix())
        pdf_manifest = release / 'SOURCE_PDF_MANIFEST122.json'
        write(pdf_manifest, dict(schema='nbo.r122.actual-runner-source-pdf.v1', author_source_commit_S=source,
            workflow_run_id=run_id, workflow_run_attempt=attempt, path_root='revision', self_excluded=True,
            build_receipt=build_path.relative_to(ROOT).as_posix(), build_receipt_sha256=digest(build_path),
            files=[dict(path=name, bytes=native(ROOT, name).stat().st_size, sha256=digest(native(ROOT, name))) for name in sorted(source_paths)],
            local_preflight_pdf_bytes_claimed_identical=False,
            scope='These exact four runner-built PDFs are the declared publication. Local preflight builds retain separate bytes and receipts.'))
        manifest = release / 'NATIVE_MANIFEST122.json'
        parts = release / 'parts'
        transport = parts / 'PACKAGE_TRANSPORT122.json'
        publication = dict(schema='nbo.r122.runner-publication-inputs.v1', author_source_commit_S=source,
            source_commit_F=F, state_commit_D=D, actual_runner_build=True,
            publication_commit_recorded_externally=True, future_author_CI_success_asserted=False,
            local_build_receipt=build_path.relative_to(ROOT).as_posix(),
            local_cost_ledger=(ledger_dir / 'COST_LEDGER122.json').relative_to(ROOT).as_posix(),
            source_pdf_manifest=pdf_manifest.relative_to(ROOT).as_posix(),
            package_manifest=manifest.relative_to(ROOT).as_posix(),
            package_transport=transport.relative_to(ROOT).as_posix(),
            local_clock_sensitivity=config['clock_sensitivity_directory'],
            resume_verification_command=composite[1:] + ['--output', 'ci122/resume-evidence'],
            **{name: config[name] for name in ('transport_registry', 'resume_publication', 'independent_directory',
                'stats_directory', 'report_directory', 'original_report_directory')})
        write(ROOT / 'PUBLICATION_INPUTS122.json', publication)
        # Enumerate actual new administrative outputs before creating the archive.
        # Future verification/publication receipts are deliberately not self-hashed.
        package_names = set(names) | {PREFIX + CONFIG, PREFIX + config['static_native_manifest'],
            PREFIX + config['source_guard_paths'], PREFIX + config['additional_cost_receipts'],
            PREFIX + 'PUBLICATION_INPUTS122.json', pdf_manifest.relative_to(REPO).as_posix()}
        package_names.update(PREFIX + name for name in source_paths)
        package_names.update(guard_names)
        package_names.update(PREFIX + name for name in extra)
        for directory in (admin, ROOT / build_dir, ledger_dir):
            package_names.update(path.relative_to(REPO).as_posix() for path in directory.rglob('*') if path.is_file())
        selection = release / 'EXPLICIT_NATIVE_PATHS122.json'
        package_names.add(selection.relative_to(REPO).as_posix())
        write(selection, sorted(package_names))
        archive = Path(os.environ['RUNNER_TEMP']) / (tag + '.zip')
        run('build-referee-archive', [sys.executable, 'verification122/make_referee_package122.py',
            '--paths', str(selection), '--manifest', manifest.relative_to(ROOT).as_posix(),
            '--archive', str(archive), '--parts-directory', parts.relative_to(ROOT).as_posix()])
        run('verify-offline-archive', [sys.executable, 'verification122/verify_referee_archive122.py',
            '--transport', str(transport), '--repository', str(REPO), '--receipt', str(admin / 'OFFLINE_ARCHIVE122.json')])
        core = [sys.executable, 'verification122/verify_package122.py', '--source-commit', F, '--state-commit', D,
            '--through', 'package', '--independent', config['independent_directory'],
            '--stats', config['stats_directory'], '--report', config['report_directory'],
            '--original-report', config['original_report_directory'],
            '--clock-sensitivity', config['clock_sensitivity_directory'],
            '--cost-ledger', str(ledger_dir / 'COST_LEDGER122.json'), '--build-receipt', str(build_path),
            '--pdf-manifest', str(pdf_manifest), '--package-manifest', str(manifest),
            '--transport-registry', config['transport_registry'], '--output', str(admin / 'package-verification')]
        run('unchanged-full-package-verification', core)
        complete = json.loads((admin / 'package-verification/VERIFICATION122.json').read_text())
        need(complete['status'] == 'verified' and complete['full_package_success'] is True, 'Full frozen package check did not succeed')
        archive_record = json.loads(transport.read_text())
        write(admin / 'READY_FOR_PUBLICATION122.json', dict(status='actual_runner_package_verified',
            author_source_commit_S=source, source_pdf_manifest=row(pdf_manifest), native_manifest=row(manifest),
            package_transport=row(transport), archive_sha256=archive_record['archive_sha256'],
            archive_bytes=archive_record['archive_bytes'], member_count=archive_record['member_count'],
            actual_build_receipt=row(build_path), frozen_package_verification=row(admin / 'package-verification/VERIFICATION122.json'),
            actual_author_CI_success_asserted=False))
        selected_paths = {PREFIX + 'PUBLICATION_INPUTS122.json'}
        selected_paths.update(PREFIX + item['path'] for item in build['pdfs'])
        promoted = config.get('promote_native_paths', [])
        need(isinstance(promoted, list) and len(promoted) == len(set(promoted))
             and set(promoted) <= set(names) and all(name.startswith(PREFIX) for name in promoted),
             'Promoted ordinary native files must be explicitly selected revision members')
        selected_paths.update(promoted)
        selected_paths.update(name for name in restored if name.startswith(PREFIX))
        for directory in (admin, release, ROOT / build_dir):
            selected_paths.update(path.relative_to(REPO).as_posix() for path in directory.rglob('*') if path.is_file())
        selected_paths = sorted(selected_paths)
        selected_hashes = {name: digest(native(REPO, name)) for name in selected_paths}
        selected_source_entries = tree_entries(source, selected_paths)
        for retry in range(3):
            tick = time.perf_counter(); log = admin / ('publication-' + str(retry + 1) + '.log')
            record = dict(attempt=retry + 1, log=log.relative_to(ROOT).as_posix())
            try:
                with log.open('xb') as stream:
                    subprocess.run(['git', 'fetch', '--filter=blob:none', '--depth=256', 'origin', BRANCH], cwd=REPO, stdout=stream, stderr=subprocess.STDOUT, check=True)
                    parent = git('rev-parse', 'FETCH_HEAD').decode().strip()
                    subprocess.run(['git', 'merge-base', '--is-ancestor', source, parent], cwd=REPO, check=True)
                    for guard in guards:
                        need(git('rev-parse', parent + ':' + guard['path']).decode().strip() == guard['git_blob'], 'Guarded author source changed during release')
                    need(tree_entries(parent, selected_paths) == selected_source_entries,
                         'A publication target changed in the concurrent parent; no evidence may be overwritten')
                    with tempfile.TemporaryDirectory(prefix='nbo-r122-release-index-') as temp:
                        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'index'))
                        subprocess.run(['git', 'read-tree', parent], cwd=REPO, env=env, check=True)
                        need(all(digest(native(REPO, name)) == expected for name, expected in selected_hashes.items()), 'Publication bytes changed after validation')
                        subprocess.run(['git', 'add', '--force', '--sparse', '--', *selected_paths], cwd=REPO, env=env, check=True)
                        tree = git('write-tree', env=env).decode().strip()
                        changed = set(git('diff-tree', '--no-commit-id', '--name-only', '-r', parent, tree).decode().splitlines())
                        need(changed and changed <= set(selected_paths), 'Publication would change an undeclared path')
                        commit = git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
                            'commit-tree', tree, '-p', parent, '-m', 'R122: publish actual runner-built author PDFs and verified referee archive').decode().strip()
                    subprocess.run(['git', 'push', 'origin', commit + ':refs/heads/' + BRANCH], cwd=REPO, stdout=stream, stderr=subprocess.STDOUT, check=True)
                    actual = git('ls-remote', 'origin', 'refs/heads/' + BRANCH).decode().split()[0]
                    if actual != commit:
                        subprocess.run(['git', 'fetch', '--depth=256', 'origin', actual], cwd=REPO, check=True)
                        subprocess.run(['git', 'merge-base', '--is-ancestor', commit, actual], cwd=REPO, check=True)
                    for name in selected_paths:
                        need(hashlib.sha256(git('show', commit + ':' + name)).hexdigest() == selected_hashes[name], 'Actual P readback differs')
                    record.update(status='published_and_read_back', parent=parent, commit=commit, observed_remote_head=actual,
                        force=False, changed_files=len(changed), selected_files=len(selected_paths))
                    state['publication_commit_P'] = commit
                break
            except Exception as error:
                record.update(status='failed', error=repr(error))
                if retry == 2:
                    raise
            finally:
                record.update(elapsed_seconds=time.perf_counter()-tick, log_sha256=digest(log))
                state['publication_attempts'].append(record)
        state.update(status='completed_actual_author_publication', actual_package_archive_sha256=archive_record['archive_sha256'],
            actual_package_members=archive_record['member_count'], actual_four_pdfs=build['pdfs'],
            author_source_is_not_publication_commit=True, final_author_CI_success_asserted=False)
    except BaseException:
        state.update(status='failed', traceback=traceback.format_exc())
        raise
    finally:
        elapsed = Q(time.perf_counter()-started)
        state.update(elapsed_seconds_exact=str(elapsed), finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
            whole_study_exact_total_seconds=None,
            unmeasured_scope='Workflow checkout/setup and final artifact upload are outside this parent; previous lost and interrupted work remains unknown.')
        if preledger is not None and ledger is not None:
            incremental = elapsed - preledger - Q(ledger['census_elapsed_seconds'])
            need(incremental >= 0, 'Post-ledger parent reconciliation is negative')
            state['additional_after_recorded_ledger_seconds_exact'] = str(incremental)
            state['cost_clock_components'] = [dict(category='author_release_after_ledger_parent',
                clock_fields=[['additional_after_recorded_ledger_seconds_exact']], partial_lower_bound_only=True,
                overlaps_counted_parent=False, scope='Only this actual parent after the packaged ledger cutoff, excluding its already counted preledger parent and ledger reader inner clock. Package/hash/offline/core/publication stages are enclosed; do not add their clocks again.')]
        else:
            state['cost_clock_components'] = []
            state['failed_release_clock_requires_enclosure_review'] = True
        write(admin / 'FINAL_RELEASE_STATUS122.json', state)


if __name__ == '__main__':
    main()
