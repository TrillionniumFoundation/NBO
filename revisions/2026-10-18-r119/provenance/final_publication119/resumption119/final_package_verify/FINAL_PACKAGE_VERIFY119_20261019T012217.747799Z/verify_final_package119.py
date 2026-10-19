#!/usr/bin/env python3
"""External, read-only scientific-content verification of the resumed R119 package."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import time
import zipfile

SOURCE = '6250abfd317f3b2a56cb1303eb5ce78249bf4042'
PUBLICATION = '68df062c7a29736b57f8bdb9e13bec951f510c7f'
ZIP_BYTES = 180801336
ZIP_SHA = '86a4f5b26861ba009b6c62fc8b483f492ce8cf8ca10bebac5a29c8a8021dd769'
MANIFEST_BYTES = 403655
MANIFEST_SHA = '1b2d480870769a161139655a76e3b6ca3c92322b1f31da7f200d650878622902'
ASSEMBLER_SHA = '5648c88ce4375626547f6803d850311e6559f56f417b8c522007e5f73ba59eb8'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, data):
    with path.open('x') as f:
        json.dump(data, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def safe(name):
    p = PurePosixPath(name)
    assert not p.is_absolute() and '..' not in p.parts and name
    return p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', type=Path, required=True)
    parser.add_argument('--audit-root', type=Path, required=True)
    args = parser.parse_args()
    assert sys.flags.optimize == 0
    revision = args.revision.resolve()
    repository = revision.parents[1]
    revision_path = revision.relative_to(repository).as_posix()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = args.audit_root.resolve() / ('FINAL_PACKAGE_VERIFY119_' + stamp)
    out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env['GIT_NO_LAZY_FETCH'] = '1'
    env['PYTHONOPTIMIZE'] = '0'
    manifest_path = revision / 'REFEREE_READY_PACKAGE119.json'
    assembler_origin = revision / 'assemble_referee_ready119.py'
    assert manifest_path.stat().st_size == MANIFEST_BYTES and sha(manifest_path) == MANIFEST_SHA
    assert sha(assembler_origin) == ASSEMBLER_SHA
    manifest = json.loads(manifest_path.read_text())
    assert manifest['bytes'] == ZIP_BYTES and manifest['sha256'] == ZIP_SHA
    assert manifest['author_source_commit'] == SOURCE
    assert len(manifest['parts']) == 22 and len(manifest['members']) == 1311
    input_manifest = revision / manifest['input_manifest']
    assert sha(input_manifest) == manifest['input_manifest_sha256']
    assembler = out / 'assemble_referee_ready119.py'
    with assembler_origin.open('rb') as fin, assembler.open('xb') as fout:
        shutil.copyfileobj(fin, fout)
    assert sha(assembler) == ASSEMBLER_SHA
    archive = out / 'referee-ready119.reconstructed.zip'
    argv = [sys.executable, '-B', str(assembler), '--manifest', str(manifest_path),
            '--parts-dir', str(revision), '--output', str(archive)]
    log = out / 'ASSEMBLY_STDOUT_STDERR119.log'
    started = time.time()
    write_json(out / 'ASSEMBLY_STARTED119.json', {
        'argv': argv, 'cwd': str(out), 'started_unix': started,
        'assembler_origin': str(assembler_origin), 'executed_assembler_sha256': ASSEMBLER_SHA,
        'manifest_sha256': MANIFEST_SHA, 'python_optimization': 0,
        'scope': 'Assemble and verify archive bytes only. No extraction, scientific solver, numerical rerun, typesetting, or network request.'})
    with log.open('xb') as stdout:
        process = subprocess.run(argv, cwd=out, env=env, stdout=stdout, stderr=subprocess.STDOUT)
    ended = time.time()
    execution = {
        'argv': argv, 'cwd': str(out), 'started_unix': started, 'ended_unix': ended,
        'elapsed_seconds': ended - started, 'exit_code': process.returncode,
        'log': {'path': log.name, 'bytes': log.stat().st_size, 'sha256': sha(log)},
        'assembler_origin': str(assembler_origin), 'executed_assembler_sha256': ASSEMBLER_SHA,
        'manifest_sha256': MANIFEST_SHA, 'python_optimization': 0,
        'output_exists': archive.exists(),
        'scope': 'External process receipt for archive assembly/verification; this elapsed time is not an economic-method benchmark.'}
    write_json(out / 'ASSEMBLY_EXECUTION119.json', execution)
    assert process.returncode == 0, 'Assembler failed; original output and log retained.'
    assert archive.stat().st_size == ZIP_BYTES and sha(archive) == ZIP_SHA
    assert sha(assembler_origin) == sha(assembler) == ASSEMBLER_SHA
    assert sha(manifest_path) == MANIFEST_SHA

    def git(*argv):
        r = subprocess.run(['git', *argv], cwd=repository, env=env, capture_output=True)
        assert r.returncode == 0, (argv, r.stderr.decode(errors='replace'))
        return r.stdout

    def tree(commit):
        rows = {}
        for raw in git('ls-tree', '-r', '-z', commit + ':' + revision_path).split(b'\0'):
            if not raw:
                continue
            header, name = raw.split(b'\t', 1)
            mode, kind, blob = header.decode().split()
            name = name.decode()
            safe(name)
            assert kind == 'blob' and name not in rows
            rows[name] = {'git_mode': mode, 'git_blob': blob}
        return rows

    local_head = git('rev-parse', 'HEAD').decode().strip()
    source = tree(SOURCE)
    publication = tree(PUBLICATION)
    assert len(source) == 1224 and len(publication) == 1233
    assert set(source).issubset(publication) and all(source[p] == publication[p] for p in source)
    expected = {row['path']: row for row in manifest['members']}
    assert len(expected) == len(manifest['members'])
    assert set(publication).issubset(expected)
    part_rows = []
    concatenated = hashlib.sha256()
    concat_bytes = 0
    for index, row in enumerate(manifest['parts']):
        assert row['path'] == 'referee-ready119.zip.part' + str(index).zfill(3)
        p = revision / row['path']
        size = p.stat().st_size
        h = hashlib.sha256()
        blob = hashlib.sha1(('blob ' + str(size) + '\0').encode())
        with p.open('rb') as f:
            for block in iter(lambda: f.read(1048576), b''):
                h.update(block)
                blob.update(block)
                concatenated.update(block)
                concat_bytes += len(block)
        assert size == row['bytes'] and h.hexdigest() == row['sha256']
        assert blob.hexdigest() == row['git_blob']
        part_rows.append(dict(row))
    assert concat_bytes == ZIP_BYTES and concatenated.hexdigest() == ZIP_SHA
    actual = {}
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            name = item.filename
            safe(name)
            assert not item.is_dir() and name not in actual and name in expected
            assert item.file_size == expected[name]['bytes']
            h = hashlib.sha256()
            blob = hashlib.sha1(('blob ' + str(item.file_size) + '\0').encode())
            count = 0
            with z.open(item) as f:
                for block in iter(lambda: f.read(1048576), b''):
                    h.update(block)
                    blob.update(block)
                    count += len(block)
            assert count == item.file_size and h.hexdigest() == expected[name]['sha256']
            if name in publication:
                assert blob.hexdigest() == publication[name]['git_blob'], ('publication Git identity', name)
                if 'git_blob' in expected[name]:
                    assert expected[name]['git_blob'] == blob.hexdigest()
                if 'git_mode' in expected[name]:
                    assert expected[name]['git_mode'] == publication[name]['git_mode']
            if name in source:
                assert expected[name]['kind'] == 'author_source'
            actual[name] = {'path': name, 'bytes': count, 'sha256': h.hexdigest(),
                            'computed_git_blob': blob.hexdigest(), 'kind': expected[name]['kind'],
                            'in_source_S': name in source, 'in_publication_P': name in publication}
        assert set(actual) == set(expected)
        spm = json.loads(z.read('SOURCE_PDF_MANIFEST119.json'))
        source_inventory = json.loads(z.read('provenance/final_publication119/source_binding/AUTHOR_SOURCE_INVENTORY119.json'))
        assert source_inventory['author_source_commit'] == spm['author_source_commit'] == SOURCE
        assert len(source_inventory['files']) == source_inventory['native_files'] == spm['native_files'] == len(source)
        assert {row['path'] for row in source_inventory['files']} == set(source)
        for row in source_inventory['files']:
            seen = actual[row['path']]
            assert (row['bytes'], row['sha256'], row['git_blob']) == (
                seen['bytes'], seen['sha256'], seen['computed_git_blob'])
        pdfs = []
        for row in spm['pdfs']:
            seen = actual[row['path']]
            assert (row['bytes'], row['sha256']) == (seen['bytes'], seen['sha256'])
            pdfs.append(seen)
    assert len(pdfs) == 4
    total = sum(row['bytes'] for row in actual.values())
    assert total == manifest['independent_member_verification']['verified_uncompressed_bytes'] == 220645605
    assert len(actual) == manifest['independent_member_verification']['verified_members'] == 1311
    assert sum(row['in_source_S'] for row in actual.values()) == manifest['source_tree_verified_members'] == 1224
    assert len(actual) - len(source) == manifest['publication_derivative_members'] == 87
    source_bytes = sum(actual[p]['bytes'] for p in source)
    assert source_bytes == source_inventory['native_bytes'] == spm['native_bytes'] == 210506054
    inventory_file = out / 'ZIP_MEMBER_IDENTITIES119.jsonl.gz'
    with inventory_file.open('xb') as f:
        with gzip.GzipFile(filename='', fileobj=f, mode='wb', compresslevel=9, mtime=0) as g:
            for name in sorted(actual):
                g.write((json.dumps(actual[name], sort_keys=True, separators=(',', ':')) + '\n').encode())
    receipt = {
        'status': 'passed_independent_part_assembly_full_membership_and_git_source_verification',
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'External final receipt outside the already frozen ZIP. No scientific experiment, build, source rewrite, archive-member rewrite, or Git-ref mutation.',
        'author_source_commit': SOURCE, 'publication_commit': PUBLICATION,
        'local_head_observed': local_head,
        'archive': {'path': str(archive), 'bytes': ZIP_BYTES, 'sha256': ZIP_SHA,
                    'parts': 22, 'members': len(actual), 'uncompressed_bytes': total},
        'package_manifest': {'path': str(manifest_path), 'bytes': MANIFEST_BYTES, 'sha256': MANIFEST_SHA},
        'input_manifest_sha256': manifest['input_manifest_sha256'],
        'assembler_source_sha256': ASSEMBLER_SHA,
        'independent_verifier_source_sha256': sha(Path(__file__)),
        'external_assembly_execution': execution,
        'source_S_files_verified_inside_zip': len(source), 'source_S_bytes_inside_zip': source_bytes,
        'publication_P_files_verified_inside_zip': len(publication),
        'publication_P_additions_to_S': sorted(set(publication) - set(source)),
        'all_source_and_publication_paths_present': True,
        'all_1311_members_exactly_match_manifest': True,
        'missing_members': [], 'unexpected_members': [], 'duplicate_members': [],
        'publication_derivative_members': len(actual) - len(source),
        'additional_members_beyond_immutable_P': len(actual) - len(publication),
        'pdfs': pdfs, 'parts': part_rows,
        'member_identity_inventory': {'path': inventory_file.name, 'bytes': inventory_file.stat().st_size,
                                      'sha256': sha(inventory_file)},
        'preinterruption_package': {'bytes': 178247262,
                                    'sha256': '1cfa881913f4c61113b78cd59d3e659738898f4b4459bd2784a54493b6571751',
                                    'status': 'Unavailable historical local-only ZIP; distinct from this newly constructed and verified derivative; not verified or substituted.'},
        'ci_scope': 'No CI state queried or inferred.',
    }
    receipt_path = out / 'FINAL_PACKAGE_VERIFICATION119.json'
    write_json(receipt_path, receipt)
    destination = revision / 'provenance/final_publication119/resumption119/final_package_verify' / out.name
    destination.mkdir(parents=True, exist_ok=False)
    copies = []
    for p in (receipt_path, inventory_file, log, out / 'ASSEMBLY_STARTED119.json',
              out / 'ASSEMBLY_EXECUTION119.json', assembler, Path(__file__)):
        q = destination / p.name
        with p.open('rb') as f, q.open('xb') as g:
            shutil.copyfileobj(f, g)
        assert sha(p) == sha(q)
        copies.append({'source': str(p), 'destination': str(q), 'bytes': q.stat().st_size, 'sha256': sha(q)})
    write_json(out / 'FINAL_PACKAGE_VERIFICATION_COPY_BINDING119.json', {
        'status': 'copied_after_successful_verification', 'files': copies,
        'frozen_zip_rewritten': False, 'external_receipt_intentionally_outside_zip': True})
    print(json.dumps({'status': receipt['status'], 'receipt': str(receipt_path),
                      'receipt_sha256': sha(receipt_path), 'archive_sha256': ZIP_SHA,
                      'native_copy': str(destination), 'assembler_exit_code': process.returncode,
                      'source_files': len(source), 'publication_files': len(publication),
                      'members': len(actual), 'uncompressed_bytes': total,
                      'assembly_log_sha256': sha(log), 'copied_small_bytes': sum(r['bytes'] for r in copies)}), flush=True)


if __name__ == '__main__':
    main()
