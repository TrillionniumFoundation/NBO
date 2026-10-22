"""Actual isolated file-restoration checks using existing immutable Git objects.

No user-repository ref or index is changed. A temporary fixture reads the
existing Git object store through a .git link, and writes only fixture files.
This validates restoration failure modes; it is not a GitHub CI execution.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OUTPUT = ROOT / 'provenance122/runtime_recovery_after_upload_reset/CI_NATIVE_HYDRATION_QA122.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if OUTPUT.exists():
        raise ValueError('Preserve the preceding actual QA receipt')
    started = time.perf_counter()
    source = ROOT / 'verification122/ci_verify122.py'
    spec = importlib.util.spec_from_file_location('r122_ci_hydration_source', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    name = 'revisions/2026-10-20-r122/PROTOCOL122.md'
    data = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=REPO)
    git_dir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=REPO, text=True).strip()
    base = dict(path=name, bytes=len(data), sha256=sha(data))
    observations = []
    with tempfile.TemporaryDirectory(prefix='nbo-r122-ci-hydration-') as tmp:
        fixture = Path(tmp)
        (fixture / '.git').symlink_to(git_dir, target_is_directory=True)
        module.REPO = fixture
        module.ROOT = fixture / 'revisions/2026-10-20-r122'
        module.ROOT.mkdir(parents=True)
        manifest = module.ROOT / 'NATIVE_MANIFEST122.json'
        publication = dict(package_manifest='NATIVE_MANIFEST122.json')
        target = fixture / name

        def check(label, rows, succeed):
            manifest.write_text(json.dumps(dict(path_root='repository', self_excluded=True, files=rows)))
            out = fixture / label
            out.mkdir()
            before = target.read_bytes() if target.is_file() else None
            error = None
            result = None
            try:
                result = module.hydrate_package_members(publication, commit, out)
            except (ValueError, subprocess.CalledProcessError) as exc:
                error = type(exc).__name__ + ': ' + str(exc)
            if (error is None) != succeed:
                raise AssertionError('Unexpected hydration result: ' + label)
            if not succeed and before is not None and target.read_bytes() != before:
                raise AssertionError('Rejected native input was overwritten')
            observations.append(dict(case=label, expected_success=succeed,
                actual_success=error is None, error=error,
                restored_members=len(result['restored_members']) if result is not None else None,
                existing_bytes_preserved=before is None or target.read_bytes() == before))

        check('restore_absent_from_exact_commit', [base], True)
        if target.read_bytes() != data:
            raise AssertionError('Restored bytes differ from the exact immutable Git object')
        check('verify_existing_without_overwrite', [base], True)
        target.write_bytes(b'changed fixture bytes\n')
        check('reject_changed_existing_native', [base], False)
        target.unlink()
        check('reject_wrong_manifest_hash_before_write', [dict(base, sha256='0' * 64)], False)
        if target.exists():
            raise AssertionError('Wrong manifest hash produced a native file')
        check('reject_path_traversal', [dict(base, path='../outside.txt')], False)
        check('reject_missing_object_in_exact_commit', [dict(base, path='revisions/2026-10-20-r122/nonexistent-fixture-only122.txt')], False)
        target.symlink_to(ROOT / 'PROTOCOL122.md')
        check('reject_symlink_native_member', [base], False)
        target.unlink()
        target.write_bytes(data)
        check('reject_duplicate_member', [base, base], False)
    elapsed = time.perf_counter() - started
    result = dict(schema='nbo.r122.ci-native-hydration-isolated-qa.v1',
        status='verified_actual_isolated_cases', source='verification122/ci_verify122.py',
        source_sha256=sha(source.read_bytes()), reader_sha256=sha(Path(__file__).read_bytes()),
        created_utc=dt.datetime.now(dt.timezone.utc).isoformat(), immutable_git_commit=commit,
        immutable_git_input=dict(path=name, bytes=len(data), sha256=sha(data)),
        cases=observations, case_count=len(observations), elapsed_seconds=elapsed,
        cost_clock_components=[dict(category='ci_native_restoration_isolated_qa', clock_fields=[['elapsed_seconds']],
            partial_lower_bound_only=True, overlaps_counted_parent=False,
            scope='Actual isolated file-restoration/failure-mode checks and temporary fixture cleanup; final receipt binding/serialization are outside the clock.')],
        user_repository_refs_changed=False, user_repository_index_changed=False,
        actual_github_ci_success_asserted=False, new_economic_evaluations=0)
    with OUTPUT.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(dict(status=result['status'], case_count=len(observations), elapsed_seconds=elapsed), indent=2))


if __name__ == '__main__':
    main()
