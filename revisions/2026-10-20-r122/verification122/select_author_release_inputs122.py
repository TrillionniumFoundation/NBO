"""Seal explicit R122 author-release inputs after every named receipt exists.

This is an administrative census. It creates no result and does not rewrite an
existing source or receipt. Generated control files must be published before
the separate release trigger. Scientific members retain their native hashes.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = 'revisions/2026-10-20-r122/'
F = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
D = 'a3323b6f557315ea91b536637419ef6fd7984b61'
RESET = 'provenance122/runtime_recovery_after_upload_reset/'
CONTROL = ('AUTHOR_RELEASE_CONFIG122.json', 'AUTHOR_RELEASE_STATIC_NATIVE122.json',
           'AUTHOR_RELEASE_SOURCE_GUARD122.json', 'AUTHOR_RELEASE_ADDITIONAL_COST122.json')
RECEIPT = RESET + 'AUTHOR_RELEASE_SELECTION122.json'
PROMOTION = RESET + 'AUTHOR_RELEASE_REQUIRED_NATIVE_PROMOTION122.json'
WORKFLOWS = ('.github/workflows/nbo-r122-author-release.yml',
             '.github/workflows/nbo-r122-author-package.yml',
             '.github/workflows/nbo-r122-author-source-promotion.yml',
             '.github/workflows/nbo-r122-artifact-custody.yml',
             '.github/workflows/nbo-r122-runtime-recovery.yml',
             '.github/workflows/nbo-r122-handoff.yml')
FIXED_EXTRA = (
    'provenance122/INDEPENDENT_INTERRUPTION_COST122.json',
    'verification_runs122/baseline-r120-recovery01/BASELINE_R120_READBACK122.json',
    'provenance122/recovery/AUTHOR_RESPONSE_REBUILD_ATTEMPT03.json',
    'provenance122/review/RESUME_COMPOSITE_SOURCE_REVIEW122.json',
    'provenance122/review/RESUME_INDEPENDENT_SOURCE_REVIEW122.json',
    'provenance122/runtime_recovery/AUTHOR_DEPENDENCIES_READBACK122.json',
    'provenance122/runtime_recovery/AUTHOR_MATH_PUBLICATION122.json',
    'provenance122/runtime_recovery/AUTHOR_RESPONSE_RUNTIME02.json',
    'provenance122/runtime_recovery/REMOTE_BRANCH_CENSUS122.json',
    'provenance122/runtime_recovery/RUNTIME_SOURCE_PUBLICATION122.json',
    'provenance122/runtime_recovery/R_PACKAGE_BINDING_REVIEW122.json',
    'provenance122/runtime_recovery/r120-native-readback01/BASELINE_R120_READBACK122.json',
    'provenance122/final_manuscript_runtime03/MANUSCRIPT_COST_BRIDGE122.json',
    RESET + 'ANCESTRY_HYDRATION_RUNTIME03_122.json',
    RESET + 'ARTIFACT_CUSTODY_NATIVE_READBACK122.json',
    RESET + 'ARTIFACT_CUSTODY_SOURCE_PUBLICATION122.json',
    RESET + 'AUTHOR_DEPENDENCIES_READBACK122.json',
    RESET + 'AUTHOR_RESPONSE_FINAL_BINDINGS122.json',
    RESET + 'AUTHOR_RESPONSE_FINAL_COMPLETE122.json',
    RESET + 'AUTHOR_RESPONSE_FINAL_GRAPHICS122.json',
    RESET + 'AUTHOR_RESPONSE_FINAL_PAGE_ORIGIN122.json',
    RESET + 'AUTHOR_RESPONSE_FINAL_TYPOGRAPHY122.json',
    RESET + 'AUTHOR_RESPONSE_REBUILD122.json',
    RESET + 'AUTHOR_TRANSPORT_PREPARATION_SOURCE_REVIEW122.json',
    RESET + 'CI_NATIVE_HYDRATION_QA122.json',
    RESET + 'COMPLETED_RECOVERY_COST_BRIDGE122.json',
    RESET + 'FINAL_ADMINISTRATIVE_TRANSPORT_REGISTRY_APPEND122.json',
    RESET + 'LEGACY_NATIVE_READBACK_COST122.json',
    RESET + 'REMOTE_BRANCH_CENSUS122.json',
    RESET + 'frozen-native-runtime03/FROZEN_NATIVE_READBACK122.json',
    RESET + 'frozen-native-runtime04/FROZEN_NATIVE_READBACK122.json',
    RESET + 'r120-native-readback02/BASELINE_R120_READBACK122.json',
    RESET + 'response_before/PRESERVATION122.json',
    # These retained disclosures have no measured complete clock. The frozen
    # ledger records them as unavailable, never as zero-valued work.
    RESET + 'UNAVAILABLE_UPLOAD_ADMIN122.json',
    RESET + 'PREWARM_RUNTIME03_FAILURE122.json',
    RESET + 'RESPONSE_PREFLIGHT_VISUAL_QA122.json',
    RESET + 'source_qa_disk_full/SOURCE_QA_DISK_FULL122.json',
)


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def relative(name):
    p = PurePosixPath(name)
    need(isinstance(name, str) and name and not p.is_absolute() and '..' not in p.parts
         and '.git' not in p.parts and '\\' not in name and str(p) == name,
         'Unsafe explicit native path: ' + repr(name))
    return name


def native(base, name):
    path = base
    for part in PurePosixPath(relative(name)).parts:
        path /= part
        need(not path.is_symlink(), 'A source input cannot have a symlink component')
    need(path.is_file() and path.resolve().is_relative_to(base), 'Missing ordinary file: ' + str(path))
    return path


def record(path):
    return dict(path=path.relative_to(REPO).as_posix(), bytes=path.stat().st_size, sha256=digest(path))


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(obj, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--extra-receipt', action='append', default=[])
    ap.add_argument('--build-receipt', default='build_receipts122/final-runtime03-origin/20261022T025302.033102Z/BUILD_RECEIPT122.json')
    a = ap.parse_args()
    started = time.perf_counter()
    outputs = [ROOT / name for name in (*CONTROL, RECEIPT, PROMOTION)]
    need(not any(p.exists() for p in outputs), 'Selection is append-only; preserve an earlier selection before a new administrative amendment')
    extra = sorted(set(FIXED_EXTRA) | {relative(name) for name in a.extra_receipt} | {RECEIPT})
    for name in extra:
        if name != RECEIPT:
            receipt = json.loads(native(ROOT, name).read_text())
            need(isinstance(receipt, dict), 'Cost receipt must be a JSON object')
    bridge = json.loads(native(ROOT, RESET + 'COMPLETED_RECOVERY_COST_BRIDGE122.json').read_text())
    need(bridge.get('cost_clock_components'), 'Actual completed recovery clock reconciliation is required')
    bridge_inputs = set()
    for item in bridge['input_files']:
        p = native(REPO, item['path'])
        need(p.stat().st_size == item['bytes'] and digest(p) == item['sha256'],
             'Current recovery-bridge input differs from its executed authenticated bytes')
        bridge_inputs.add(item['path'])
    launch = native(ROOT, 'results122/launch-final-recovery-cost-bridge03/LAUNCH122.json')
    need(json.loads(launch.read_text()).get('exit_code') == 0, 'Actual successful bridge launch is required')
    registry_path = native(ROOT, 'transport122/REGISTRY122.json')
    need(digest(registry_path) == 'ddfc4ad44d553494f4e5314c44fce56e6b5ea4c0b8e7dcddae0a9d34bc7c49e6',
         'The already authenticated thirteen-entry registry changed')
    registry = json.loads(registry_path.read_text())
    need(len(registry['requests']) == 13, 'The exact twelve historical bundles and additive administrative bundle are required')
    registered = set()
    for request_name in registry['requests']:
        request = json.loads(native(ROOT, request_name).read_text())
        for item in request['files']:
            p = native(ROOT, item['path'])
            need(p.stat().st_size == item['bytes'] and digest(p) == item['sha256'], 'Registered native evidence changed')
            registered.add(PREFIX + item['path'])
    dependencies = json.loads(native(ROOT, RESET + 'AUTHOR_DEPENDENCIES_READBACK122.json').read_text())
    for item in dependencies['records']:
        p = native(REPO, item['path'])
        need(p.stat().st_size == item['bytes'] and digest(p) == item['sha256'],
             'An exact pinned historical dependency changed after its readback')
    historical = {item['path'] for item in dependencies['records']}
    excluded_top = {'build', 'ci122', 'referee_ready122', '.git'}
    excluded_files = set(CONTROL) | {RECEIPT, PROMOTION, 'PUBLICATION_INPUTS122.json', 'AUTHOR_RELEASE_TRIGGER122.json'}
    names = set()
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(ROOT)
        if rel.parts[0] in excluded_top or '__pycache__' in rel.parts or rel.as_posix() in excluded_files:
            continue
        names.add(p.relative_to(REPO).as_posix())
    names.update(historical)
    names.update(bridge_inputs)
    names.update(WORKFLOWS)
    records = [record(native(REPO, name)) for name in sorted(names)]
    # Native result files are authenticated by the static SHA manifest and the
    # immutable F objects or registered transports. All other ordinary R122
    # inputs are guarded as S blobs, including exact transport chunks.
    guard = {name for name in names if name.startswith(PREFIX) and not name.startswith(PREFIX + 'results122/')}
    guard.update(WORKFLOWS)
    guard.update(PREFIX + name for name in (*CONTROL, RECEIPT, PROMOTION, 'AUTHOR_RELEASE_TRIGGER122.json'))
    build = json.loads(native(ROOT, a.build_receipt).read_text())
    need(build['status'] == 'compiled_clean' and not build['issues'] and not build['placeholders'], 'Strict actual preflight is required')
    author_inputs = set(build['source_sha256']) | set(build['graphic_asset_sha256'])
    for group in build['actual_project_inputs'].values():
        author_inputs.update(group)
    need({PREFIX + name for name in author_inputs} <= guard, 'Actual author dependency missing from S guard')
    # Only source promotion is requested here. Expanded scientific transport
    # members and cross-revision historical objects have existing exact routes.
    current_tree = {}
    raw = subprocess.check_output(['git', 'ls-tree', '-r', '-z', 'HEAD', '--', PREFIX.rstrip('/'), '.github/workflows'], cwd=REPO)
    for item in raw.split(b'\0'):
        if item:
            meta, name = item.split(b'\t', 1)
            current_tree[name.decode()] = meta.decode().split()[2]
    publication = set()
    for item in records:
        name = item['path']
        if not name.startswith(PREFIX) and name not in WORKFLOWS:
            continue
        if name in registered:
            continue
        data = native(REPO, name).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if current_tree.get(name) != blob:
            need(len(data) < 95 * 1024**2, 'Native source publication target exceeds the explicit Git limit')
            publication.add(name)
    # The bootstrap source is already promoted before execution. This final
    # ordinary source/control addition is published without the trigger.
    publication.update(PREFIX + name for name in (*CONTROL, RECEIPT, PROMOTION))
    config = dict(schema='nbo.r122.runner-author-release.v1', source_commit_F=F, state_commit_D=D,
        source_guard_paths=CONTROL[2], static_native_manifest=CONTROL[1], additional_cost_receipts=CONTROL[3],
        immutable_commits=[F, D, '796c5f2badf68b051ac6c144884c0e61b87faf5e',
            '56cff43b088c7d6b1cee352d27fc9de8573c46ed', 'af73f9bca8f2249da1601208a1921f50ea8fd074',
            '1f19410305c707716135defd91d6644d70657d84', '0fe0f2bbf76529201a1890db0fc2a94b0be44418',
            '80dec8acbfb8225be5f8dee135ed10efb5054d93', '9723c6cd2cc8b3e071422f3e522d4a843946db63'],
        transport_registry='transport122/REGISTRY122.json', transport_registry_sha256=digest(registry_path),
        resume_publication='provenance122/RESUME_INDEPENDENT_PUBLICATION122.json',
        independent_directory='results122/runtime-recovery-39691016040-1-canonical',
        stats_directory='results122/runtime-recovery-39691016040-1-statistics',
        report_directory='results122/runtime-recovery-39691016040-1-adapted-report',
        original_report_directory='results122/runtime-recovery-39691016040-1-original-report',
        clock_sensitivity_directory='results122/final-clock-sensitivity03',
        promote_native_paths=[],
        source_plan='Ordinary author/control files are promoted before the separate S trigger. Registered scientific native files are re-materialized losslessly; missing explicit ordinary S members may be restored from S only.',
        new_economic_experiment=False)
    write(ROOT / CONTROL[3], extra)
    write(ROOT / CONTROL[1], dict(schema='nbo.r122.explicit-static-native-inputs.v1', path_root='repository',
        self_excluded=True, files=records,
        exclusions='Mutable build and current/future release outputs, control files added separately, and Python caches. Historical sources are explicit pinned-dependency records; this is not a claim to duplicate every historical Git tree.'))
    write(ROOT / CONTROL[2], sorted(guard))
    write(ROOT / CONTROL[0], config)
    write(ROOT / PROMOTION, sorted(publication))
    elapsed = time.perf_counter() - started
    write(ROOT / RECEIPT, dict(schema='nbo.r122.actual-author-release-selection.v1', status='selected_actual_native_inputs',
        created_utc=dt.datetime.now(dt.timezone.utc).isoformat(), reader_sha256=digest(Path(__file__)),
        files=len(records), bytes=sum(item['bytes'] for item in records), source_guard_paths=len(guard),
        additional_cost_receipts=len(extra), required_native_publication_paths=len(publication),
        controls=[record(ROOT / name) for name in CONTROL], required_publication=record(ROOT / PROMOTION),
        actual_preflight_build=record(ROOT / a.build_receipt), elapsed_seconds=elapsed,
        cost_clock_components=[dict(category='author_release_native_selection', clock_fields=[['elapsed_seconds']],
            overlaps_counted_parent=False, partial_lower_bound_only=True,
            scope='Actual explicit native hashing, source/control selection and writes until final receipt assembly begins. No economic execution; final source/hash binding and receipt serialization are outside this clock.')],
        future_release_success_asserted=False, final_author_ci_success_asserted=False))
    print(json.dumps(dict(status='selected_actual_native_inputs', files=len(records),
        source_guard_paths=len(guard), publication_paths=len(publication), receipt=RECEIPT), indent=2))


if __name__ == '__main__':
    main()
