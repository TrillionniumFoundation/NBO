"""GitHub-only publication verification of saved R122 science and four PDFs.

Original execution clocks and scientific receipts are inputs. This job never
creates population observations, trains actors, runs an economic solver, or
performs a service timing campaign. Its actual job receipts have their own CI
identity; success refers only to the checked-out commit.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
F = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
D = 'a3323b6f557315ea91b536637419ef6fd7984b61'
ALIASES = (Path('/workspace/scratch/411f2ee67342/NBO'),
           Path('/dev/shm/nbo-r122-411f2ee67342/NBO'))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def local(value):
    if not isinstance(value, str) or Path(value).is_absolute():
        raise ValueError('Publication paths must be revision-relative strings')
    p = (ROOT / value).resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError('Publication path escapes revision')
    return p


def hydrate_package_members(publication, commit, out):
    """Restore only absent ordinary package members from this exact CI commit.

    Scientific transport members must already have been materialized. A missing
    member absent from the tested Git tree fails closed; no historical branch,
    changed manifest, reconstructed result or alternative source is substituted.
    """
    manifest_path = local(publication['package_manifest'])
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('path_root') != 'repository' or manifest.get('self_excluded') is not True:
        raise ValueError('Publication native manifest root/self policy differs')
    rows, seen, restored = manifest['files'], set(), []
    if not isinstance(rows, list) or not rows:
        raise ValueError('Publication native manifest must enumerate every input')
    for row in rows:
        name = row['path']; rel = PurePosixPath(name)
        if (not isinstance(name, str) or rel.is_absolute() or '..' in rel.parts
                or '.git' in rel.parts or str(rel) != name or '\\' in name
                or name in seen):
            raise ValueError('Unsafe or duplicate package member: ' + repr(name))
        seen.add(name); path = REPO
        for part in rel.parts:
            path /= part
            if path.is_symlink():
                raise ValueError('Symlink package member is not ordinary native evidence')
        if not path.resolve().is_relative_to(REPO):
            raise ValueError('Package member escapes the tested repository')
        if not path.exists():
            data = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=REPO)
            if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError('Exact tested-commit bytes do not match the missing package member')
            blob = subprocess.check_output(['git', 'rev-parse', commit + ':' + name], cwd=REPO, text=True).strip()
            actual_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if actual_blob != blob:
                raise ValueError('Exact tested-commit Git blob identity differs')
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(data)
            restored.append(dict(path=name, bytes=len(data), sha256=row['sha256'], git_blob=blob))
        if not path.is_file() or path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
            raise ValueError('Existing package native bytes differ; nothing may be overwritten: ' + name)
    result = dict(status='verified', checked_commit=commit, native_members=len(rows),
        native_manifest_sha256=digest(manifest_path), restored_members=restored,
        scientific_bytes_from_alternative_source=False,
        scope='Only absent files were restored from the exact tested commit; all listed native bytes were checked.')
    target = out / 'PACKAGE_NATIVE_HYDRATION122.json'
    with target.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2); stream.write('\n')
    return result


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('This runner is restricted to an actual GitHub Actions environment')
    if Path(os.environ['GITHUB_WORKSPACE']).resolve() != REPO:
        raise RuntimeError('GitHub workspace is not the current repository')
    out = ROOT / 'ci122'
    out.mkdir(exist_ok=True)
    native = ROOT / 'PUBLICATION_INPUTS122.json'
    publication = json.loads(native.read_text())
    if (publication['source_commit_F'], publication['state_commit_D']) != (F, D):
        raise ValueError('Published scientific identities differ')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    if commit != os.environ['GITHUB_SHA']:
        raise ValueError('Checked-out commit differs from workflow event SHA')
    receipt = dict(status='started', checked_commit=commit, source_commit_F=F,
        state_commit_D=D, workflow_run_id=os.environ['GITHUB_RUN_ID'],
        workflow_run_attempt=os.environ['GITHUB_RUN_ATTEMPT'],
        created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        runner_sha256=digest(__file__), publication_inputs_sha256=digest(native),
        stages=[], aliases=[], new_states=0, new_training=0,
        new_economic_evaluations=0, new_service_timing_processes=0,
        scope='Exact saved evidence validation, deterministic inference/report replay, and actual four-document TeX build only.')
    started = time.perf_counter()

    def save():
        (out / 'CI_EXECUTION122.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')

    def run(label, argv):
        log = out / (label + '.log')
        begin = time.perf_counter()
        with log.open('xb') as stream:
            result = subprocess.run(argv, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        row = dict(stage=label, argv=argv, exit_code=result.returncode,
                   elapsed_seconds=time.perf_counter()-begin,
                   log=str(log.relative_to(ROOT)), log_sha256=digest(log))
        receipt['stages'].append(row)
        save()
        print(json.dumps({k: row[k] for k in ('stage', 'exit_code', 'elapsed_seconds')}), flush=True)
        if result.returncode:
            print(log.read_text(errors='replace')[-10000:], flush=True)
            raise RuntimeError('CI stage failed: ' + label)

    save()
    try:
        trigger_path = ROOT / 'CI_TRIGGER122.json'
        trigger = json.loads(trigger_path.read_text())
        source = trigger['author_source_commit_S']
        published = trigger['author_publication_commit_P']
        if any(not isinstance(value, str) or len(value) != 40
               or any(char not in '0123456789abcdef' for char in value)
               for value in (source, published)):
            raise ValueError('Final author CI requires full actual S and P commit identities')
        if publication['author_source_commit_S'] != source:
            raise ValueError('CI trigger author source differs from actual delivered publication')
        run('fetch-actual-author-publication', ['git', 'fetch', '--filter=tree:0', '--depth=256',
            'origin', source, published])
        for older, newer in ((source, published), (published, commit)):
            subprocess.run(['git', 'merge-base', '--is-ancestor', older, newer], cwd=REPO, check=True)
        for field, path in (
                ('publication_inputs_sha256', native),
                ('source_pdf_manifest_sha256', local(publication['source_pdf_manifest'])),
                ('native_manifest_sha256', local(publication['package_manifest'])),
                ('package_transport_sha256', local(publication['package_transport']))):
            data = subprocess.check_output(['git', 'show', published + ':' + path.relative_to(REPO).as_posix()], cwd=REPO)
            if hashlib.sha256(data).hexdigest() != trigger[field] or digest(path) != trigger[field]:
                raise ValueError('Actual P and tested C publication custody differ: ' + field)
        receipt['actual_author_publication'] = dict(author_source_commit_S=source,
            author_publication_commit_P=published, checked_commit_C=commit,
            exact_publication_manifests_preserved=True, source_is_ancestor_of_publication=True,
            publication_is_ancestor_of_tested_commit=True, trigger_sha256=digest(trigger_path))
        save()
        # These are authentic prior execution prefixes. The unchanged report
        # checks resolved child paths. No receipt path or prior byte is edited.
        for alias in ALIASES:
            if alias == REPO:
                receipt['aliases'].append(dict(path=str(alias), action='already_actual_repository'))
                continue
            if alias.is_symlink():
                if alias.resolve() != REPO:
                    raise ValueError('An existing unrelated alias must not be replaced: ' + str(alias))
                action = 'already_same_alias'
            elif alias.exists():
                raise ValueError('An existing directory or file must not be displaced in CI: ' + str(alias))
            else:
                subprocess.run(['sudo', 'mkdir', '-p', str(alias.parent)], check=True)
                # No force flag: an unexpected existing target fails closed.
                subprocess.run(['sudo', 'ln', '-sT', str(REPO), str(alias)], check=True)
                action = 'created_absent_authenticated_prefix'
            if alias.resolve() != REPO:
                raise ValueError('CI path alias does not resolve to the actual checkout')
            receipt['aliases'].append(dict(path=str(alias), action=action, target=str(REPO)))
        save()
        run('materialize', [sys.executable, 'verification122/materialize_evidence122.py',
            '--registry', str(local(publication['transport_registry'])), '--output', 'ci122/MATERIALIZATION122.json'])
        run('fetch-author-history', ['git', 'fetch', '--filter=tree:0', '--depth=1', 'origin',
            '80dec8acbfb8225be5f8dee135ed10efb5054d93', '9723c6cd2cc8b3e071422f3e522d4a843946db63'])
        run('restore-exact-author-history', [sys.executable, 'verification122/restore_author_dependencies_after_upload122.py',
            '--output', 'ci122/HISTORICAL_DEPENDENCIES122.json'])
        if not publication.get('package_manifest') or not publication.get('package_transport'):
            raise ValueError('Final author CI requires the delivered native manifest and complete archive transport')
        hydration_started = time.perf_counter()
        hydration = hydrate_package_members(publication, commit, out)
        receipt['native_package_hydration'] = dict(receipt='ci122/PACKAGE_NATIVE_HYDRATION122.json',
            receipt_sha256=digest(out / 'PACKAGE_NATIVE_HYDRATION122.json'),
            native_members=hydration['native_members'], restored_members=len(hydration['restored_members']),
            elapsed_seconds=time.perf_counter()-hydration_started)
        transport = json.loads(local(publication['package_transport']).read_text())
        if (transport['manifest_sha256'] != digest(local(publication['package_manifest']))
                or transport['manifest_path'] != local(publication['package_manifest']).relative_to(REPO).as_posix()
                or transport['member_count'] != hydration['native_members'] + 1):
            raise ValueError('Delivered archive and native manifest are not the same publication')
        run('delivered-offline-archive', [sys.executable, 'verification122/verify_referee_archive122.py',
            '--transport', str(local(publication['package_transport'])), '--repository', str(REPO),
            '--receipt', 'ci122/OFFLINE_ARCHIVE_VERIFICATION122.json'])
        receipt['delivered_archive_sha256'] = transport['archive_sha256']
        receipt['delivered_archive_members'] = transport['member_count']
        save()
        # The gate below uses GIT_NO_LAZY_FETCH=1. Hydrate exactly its known
        # immutable object paths first and preserve the actual readback receipt.
        prewarm = [sys.executable, 'verification122/prewarm_git_objects122.py',
            '--source-commit', F, '--state-commit', D, '--output', 'ci122/PREWARM122.json']
        if publication.get('resume_publication'):
            resume_path = local(publication['resume_publication'])
            resume = json.loads(resume_path.read_text())
            resume_commit = resume['commit']
            if len(resume_commit) != 40 or any(c not in '0123456789abcdef' for c in resume_commit):
                raise ValueError('Full immutable resume commit required')
            run('fetch-resume-source', ['git', 'fetch', '--filter=tree:0', '--depth=1', 'origin', resume_commit])
            prewarm.extend(['--resume-publication', str(resume_path)])
        run('prewarm', prewarm)
        if publication.get('resume_verification_command'):
            command = publication['resume_verification_command']
            if not isinstance(command, list) or not command or any(not isinstance(v, str) for v in command):
                raise ValueError('Invalid explicit composite verification command')
            if command[0] != 'verification122/verify_independent_resume122.py':
                raise ValueError('Undeclared composite verification program')
            run('resume-evidence', [sys.executable, *command])
        verifier = [sys.executable, 'verification122/verify_package122.py',
            '--source-commit', F, '--state-commit', D, '--through', 'package',
            '--independent', str(local(publication['independent_directory'])),
            '--build-receipt', str(local(publication['local_build_receipt'])),
            '--cost-ledger', str(local(publication['local_cost_ledger'])),
            '--clock-sensitivity', str(local(publication['local_clock_sensitivity'])),
            '--transport-registry', str(local(publication['transport_registry'])),
            '--pdf-manifest', str(local(publication['source_pdf_manifest'])),
            '--output', 'ci122/delivered-package-verification']
        for key, flag in (('stats_directory', '--stats'),
                          ('report_directory', '--report'),
                          ('original_report_directory', '--original-report')):
            if publication.get(key):
                stage_path = local(publication[key])
                if not stage_path.is_relative_to(ROOT / 'results122'):
                    raise ValueError('Published scientific stage must be inside results122: ' + key)
                verifier.extend([flag, str(stage_path)])
        if publication.get('package_manifest'):
            verifier.extend(['--package-manifest', str(local(publication['package_manifest']))])
        # Verify the delivered PDF bytes before compiling fresh CI PDFs.
        run('delivered-package', verifier)
        run('saved-replay', [sys.executable, 'verification122/ci_saved_replay122.py',
                            '--output', 'ci122/saved-replay'])
        run('build', [sys.executable, 'build122.py', '--receipt-dir', 'ci122/build-receipts'])
        builds = list((out / 'build-receipts').glob('*/BUILD_RECEIPT122.json'))
        if len(builds) != 1:
            raise ValueError('CI requires exactly one completed build receipt')
        build = json.loads(builds[0].read_text())
        if build['status'] != 'compiled_clean' or build['issues'] or build['placeholders']:
            raise ValueError('Four-document CI build is not clean')
        run('fresh-pdf-content-and-geometry', [sys.executable, 'verification122/author_pdf_inspection_runtime03_122.py',
            '--build-receipt', str(builds[0]), '--output', 'ci122/pdf-inspection'])
        inspection = json.loads((out / 'pdf-inspection/PDF_INSPECTION122.json').read_text())
        if inspection['status'] != 'executed' or inspection['exit_code'] != 0 or inspection['physical_page_boundary_exceptions']:
            raise ValueError('Actual fresh CI PDF content/geometry did not pass')
        for alias in ALIASES:
            if alias.resolve() != REPO:
                raise ValueError('Historical path alias changed during replay')
        receipt.update(status='verified', build_receipt=str(builds[0].relative_to(ROOT)),
            build_receipt_sha256=digest(builds[0]), pdfs=build['pdfs'],
            all_original_saved_service_clocks_unchanged=True,
            checked_commit_only=True, later_publication_commits_tested=False)
    except BaseException:
        receipt.update(status='failed', traceback=traceback.format_exc())
        raise
    finally:
        receipt.update(elapsed_seconds=time.perf_counter()-started,
            finished_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        save()


if __name__ == '__main__':
    main()
