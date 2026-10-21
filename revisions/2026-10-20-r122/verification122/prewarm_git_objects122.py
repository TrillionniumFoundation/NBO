"""Hydrate and strictly read back the exact Git objects used by R122 readers.

No ref is moved and no native scientific file is written. Ordinary immutable
Git reads may retrieve promised objects in a partial clone. Every object is
then reread with GIT_NO_LAZY_FETCH=1 before the strict saved-evidence audit.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = 'revisions/2026-10-20-r122/'
F = '2f483615c8bc0037e43ec01a16cce05c724f8c60'
D = 'a3323b6f557315ea91b536637419ef6fd7984b61'
M = '796c5f2badf68b051ac6c144884c0e61b87faf5e'
RESTART = '56cff43b088c7d6b1cee352d27fc9de8573c46ed'
AF = 'af73f9bca8f2249da1601208a1921f50ea8fd074'
I = '1f19410305c707716135defd91d6644d70657d84'
F_MANIFEST_SHA = 'eba26439a799392b7553d06fea5f17828c8988b9f72f4e049058771985ac8b0f'
D_MANIFEST_SHA = '25dc1cdd876a1dcd9f38e867db79d073ea9f2bde3e95b324a1f6a0a1e7303405'
FIXED = [
 (RESTART, 'RESTART_PROTOCOL122.json', 'c776a9c7e8bff1b7ea8c5b9e60f17ad5fc02fef7c8458ea7555497be10a419e4'),
 (AF, 'verification122/report_schema_adapter122.py', '7b0a1f2d520990509b63db504162ec009869f580825675ec83649029e696462a'),
 (AF, 'verification122/report_protocol_adapter122.py', '531699d7228d8638da7d7fb749e48ecd84e4380cd56e4f1985479ef342ac30d5'),
 (AF, 'provenance122/REPORTING_AMENDMENT122.md', '4c63b176fc6e7082d31df8671eebafd8b3fcf306288fc74620deb3a40aad4452'),
 (I, 'verification122/independent_schema_adapter122.py', '9d2fcf4dd41cb1eab45afec5f4e737164b0992bac459105dd06563abc95aa92c'),
 (I, 'verification122/test_independent_schema_adapter122.py', '6c6c293f5432eaa8d87b1b8d01ae6f392c90fe92e8a6c33a6d18733b3955c67a'),
 (I, 'provenance122/INDEPENDENT_SCHEMA_AMENDMENT122.md', '2e21674081a07c03a797b43b8f765c9acffa8ff40f5528854f00817cecc14518'),
 (I, 'results122/independent-attempt01/FAILURE122.json', '769f99215850fd61ea09e90d1b8cf916c8fccf7afde77ac4d8990a011fa6dcd2'),
]


def sha(b): return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-commit', default=F)
    ap.add_argument('--state-commit', default=D)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--resume-publication', type=Path,
                    help='Actual immutable resume publication receipt with commit/tree/source_files; optional until that source is published.')
    ap.add_argument('--additional-bindings', type=Path,
                    help='Optional JSON array of exact {commit,path,sha256} records; no wildcard or mutable branch.')
    a = ap.parse_args()
    if a.source_commit != F or a.state_commit != D:
        raise ValueError('This helper serves the actual fixed R122 F/D pair only')
    if a.output.exists(): raise FileExistsError('Output receipt must be new')
    started = time.perf_counter()
    ordinary_env = dict(os.environ)
    ordinary_env.pop('GIT_NO_LAZY_FETCH', None)
    strict_env = {**os.environ, 'GIT_NO_LAZY_FETCH': '1'}
    verified = {}
    inputs = []

    def check(commit, path, expected):
        if (len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit)
                or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected)):
            raise ValueError('Full immutable commit and SHA256 required')
        rel = PurePosixPath(path)
        if rel.is_absolute() or '..' in rel.parts or '\\' in path or rel.as_posix() != path:
            raise ValueError('Unsafe/noncanonical Git path')
        key = (commit, path)
        if key in verified:
            if verified[key]['sha256'] != expected: raise ValueError('Conflicting expected object')
            return (REPO / path).read_bytes()
        native = (REPO / path).resolve()
        if not native.is_relative_to(REPO) or not native.is_file(): raise ValueError('Missing native object ' + path)
        before = native.read_bytes()
        if sha(before) != expected: raise ValueError('Native SHA differs before Git read: ' + path)
        published = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=REPO, env=ordinary_env)
        strict = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=REPO, env=strict_env)
        if published != strict or strict != before or native.read_bytes() != before:
            raise ValueError('Published, strict and native object bytes differ: ' + path)
        verified[key] = {'commit': commit, 'path': path, 'bytes': len(before), 'sha256': expected,
                         'git_blob_sha1': hashlib.sha1(b'blob ' + str(len(before)).encode() + b'\0' + before).hexdigest(),
                         'strict_no_lazy_fetch_readback': True}
        return before

    freeze = json.loads(check(F, PREFIX + 'SOURCE_FREEZE122.json', F_MANIFEST_SHA))
    if len(freeze['scientific_files']) != 243 or freeze['inherited_actor_commit'] != M:
        raise ValueError('Frozen scientific member/model scope changed')
    for path, expected in sorted(freeze['scientific_files'].items()): check(F, path, expected)
    state_prefix = PREFIX + 'results122/states-attempt01/'
    states = json.loads(check(D, state_prefix + 'STATE_MANIFEST122.json', D_MANIFEST_SHA))
    if states['source_commit'] != F or states['actor_commit'] != M:
        raise ValueError('D source or actor identity differs')
    if set(states['files']) != {'ACTORS122.json', 'entropy122.bin', 'states122.json'}:
        raise ValueError('D member census differs')
    for name, expected in sorted(states['files'].items()): check(D, state_prefix + name, expected)
    actors = json.loads((REPO / state_prefix / 'ACTORS122.json').read_text())
    if actors['actor_commit'] != M or len(actors['models']) != 56:
        raise ValueError('Actual M actor census differs')
    for row in actors['models']: check(M, row['path'], row['sha256'])
    for commit, path, expected in FIXED: check(commit, PREFIX + path, expected)
    if a.resume_publication:
        path = a.resume_publication if a.resume_publication.is_absolute() else ROOT / a.resume_publication
        path = path.resolve()
        if not path.is_relative_to(REPO): raise ValueError('Keep resume publication in the repository')
        raw = path.read_bytes();publication = json.loads(raw)
        inputs.append({'path': path.relative_to(REPO).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
        if publication.get('status') != 'executed' or publication.get('source_commit_F') != F:
            raise ValueError('Resume source has no actual publication identity')
        commit = publication['commit'];tree = publication['tree']
        if (len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit)
                or len(tree) != 40 or any(c not in '0123456789abcdef' for c in tree)):
            raise ValueError('Exact resume commit and tree required')
        actual_tree = subprocess.check_output(['git', 'rev-parse', commit + '^{tree}'], cwd=REPO, env=ordinary_env, text=True).strip()
        if actual_tree != tree: raise ValueError('Resume publication tree differs from actual Git')
        source_rows = publication['source_files']
        if not isinstance(source_rows, list) or not source_rows:
            raise ValueError('Complete explicit resume source rows required')
        for row in source_rows:
            if set(row) != {'path', 'bytes', 'sha256', 'git_blob'}:
                raise ValueError('Resume source rows require path/bytes/SHA256/Git blob')
            native = check(commit, row['path'], row['sha256'])
            blob = hashlib.sha1(b'blob ' + str(len(native)).encode() + b'\0' + native).hexdigest()
            if len(native) != row['bytes'] or blob != row['git_blob']:
                raise ValueError('Resume published source byte/blob identity differs')
    if a.additional_bindings:
        path = a.additional_bindings.resolve()
        if not path.is_relative_to(REPO): raise ValueError('Keep additional binding list in the repository')
        raw = path.read_bytes();extra = json.loads(raw)
        inputs.append({'path': path.relative_to(REPO).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
        if not isinstance(extra, list): raise ValueError('Additional bindings must be an exact array')
        for row in extra:
            if set(row) != {'commit', 'path', 'sha256'}: raise ValueError('Unexpected extra binding schema')
            check(row['commit'], row['path'], row['sha256'])
    for parent, child in ((M, F), (F, D)):
        subprocess.run(['git', 'merge-base', '--is-ancestor', parent, child], cwd=REPO, env=strict_env, check=True)
    source = Path(__file__).resolve();data = source.read_bytes()
    result = {'status': 'verified_git_object_prewarm', 'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'scope': 'Exact immutable source-object preparation and strict local readback for subsequent saved-evidence verification; promised-object cache hydration only, no ref movement or native scientific writes.',
              'source_commit_F': F, 'state_commit_D': D, 'actor_commit_M': M,
              'source': {'path': source.relative_to(REPO).as_posix(), 'bytes': len(data), 'sha256': sha(data)},
              'actual_command': sys.argv, 'objects': sorted(verified.values(), key=lambda x: (x['commit'], x['path'])),
              'bound_objects': len(verified), 'additional_input_lists': inputs,
              'elapsed_seconds': time.perf_counter() - started,
              'clock_scope': 'This Git source-object readback process; initial startup and final receipt serialization excluded.',
              'new_economic_evaluations': 0, 'new_population_observations': 0, 'new_training': 0,
              'scientific_success_asserted': False}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'bound_objects': len(verified), 'elapsed_seconds': result['elapsed_seconds']}, indent=2))


if __name__ == '__main__': main()
