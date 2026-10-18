#!/usr/bin/env python3
"""Actual author-side packaging command, retaining original source identities.

This script expects the original workspace input layout.  It only creates the
new portable119 package; it does not change or run historical/scientific code.
The independent verify/extract helper needs only the published package.
"""
from __future__ import annotations

from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tarfile


BASE = Path('/workspace/scratch/913249553838')
AUDIT = BASE / 'audit/theory_research'
DEST = Path(__file__).resolve().parent
HIST = DEST.parent
PART_BYTES = 8 * 1024 * 1024


def filehash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, obj):
    with path.open('x') as out:
        json.dump(obj, out, indent=2, sort_keys=True)
        out.write('\n')


class SplitWriter:
    def __init__(self):
        self.archive_hash = hashlib.sha256()
        self.total = 0
        self.parts = []
        self.current = None
        self.current_size = 0
        self.current_hash = None
        self.current_name = None

    def writable(self):
        return True

    def write(self, data):
        self.archive_hash.update(data)
        self.total += len(data)
        offset = 0
        while offset < len(data):
            if self.current is None:
                self.current_name = f'index119.tar.gz.part{len(self.parts):03d}'
                self.current = (DEST / self.current_name).open('xb')
                self.current_hash = hashlib.sha256()
                self.current_size = 0
            count = min(PART_BYTES - self.current_size, len(data) - offset)
            block = data[offset:offset + count]
            self.current.write(block)
            self.current_hash.update(block)
            self.current_size += count
            offset += count
            if self.current_size == PART_BYTES:
                self.close_part()
        return len(data)

    def close_part(self):
        if self.current is not None:
            self.current.close()
            self.parts.append({'path': self.current_name, 'bytes': self.current_size,
                               'sha256': self.current_hash.hexdigest()})
            self.current = None

    def flush(self):
        if self.current is not None:
            self.current.flush()


def main():
    if (DEST / 'PORTABLE_LOCATION_MANIFEST119.json').exists():
        raise SystemExit('This actual package already exists; do not overwrite its receipts.')
    started = datetime.now(timezone.utc).isoformat()
    items = []

    def retain(source, relative, reason, compress=False, existing=None):
        if not source.is_file():
            raise FileNotFoundError(source)
        original_size = source.stat().st_size
        original_hash = filehash(source)
        if existing is not None:
            target = existing
            encoding = 'gzip' if target.suffix == '.gz' and source.suffix != '.gz' else 'identity'
        else:
            target = DEST / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            encoding = 'gzip' if compress else 'identity'
            if compress:
                with source.open('rb') as f, target.open('xb') as out:
                    with gzip.GzipFile(filename='', mode='wb', fileobj=out,
                                       mtime=0, compresslevel=9) as gz:
                        shutil.copyfileobj(f, gz, 1024 * 1024)
            else:
                with source.open('rb') as f, target.open('xb') as out:
                    shutil.copyfileobj(f, out, 1024 * 1024)
        packaged_path = str(target.relative_to(DEST)) if target.is_relative_to(DEST) else '../' + str(target.relative_to(HIST))
        items.append({'original_path': str(source), 'original_bytes': original_size,
                      'original_sha256': original_hash, 'packaged_path': packaged_path,
                      'packaged_bytes': target.stat().st_size,
                      'packaged_sha256': filehash(target), 'encoding': encoding,
                      'reason': reason, 'already_packaged_without_duplicate': existing is not None,
                      'original_source_modified': False})

    scripts = ['HISTORICAL_index.py', 'HISTORICAL_total_read_closure119.py',
               'HISTORICAL_remote_close119.py', 'HISTORICAL_complete_field_inventory119.py',
               'HISTORICAL_stream_audit_v1_executed.py', 'HISTORICAL_stream_audit_test.py',
               'HISTORICAL_local_raw_supervisor.py']
    for name in scripts:
        existing = HIST / name
        retain(AUDIT / name, 'scripts/' + name, 'Exact executed audit or parser-test source',
               existing=existing if existing.is_file() and filehash(existing) == filehash(AUDIT / name) else None)
    retain(AUDIT / 'HISTORICAL_git_refs.tsv', 'scope/HISTORICAL_git_refs.tsv', 'Exact initial captured ref snapshot')
    for name in ['HISTORICAL_stream_all_blobs.jsonl', 'HISTORICAL_stream_available_raw_unread.jsonl']:
        retain(AUDIT / name, 'scope/' + name + '.gz', 'Exact original object-selection input', compress=True)
    for name in ['HISTORICAL_stream_all_blobs.jsonl.scope.json', 'HISTORICAL_stream_available_raw_unread.scope.json']:
        retain(AUDIT / name, 'scope/' + name, 'Scope-construction receipt')
    retain(AUDIT / 'EARLY_REFEREE_AUTHOR_TREATMENTS119_VALIDATION.json',
           'author/EARLY_REFEREE_AUTHOR_TREATMENTS119_VALIDATION.json', 'Exact 159-row author-treatment validation')

    launch = BASE / 'audit/historical_remote119'
    retain(BASE / 'audit/run_historical_remote119.py', 'launch/run_historical_remote119.py',
           'Actual immutable-read shard launcher; not scientific execution')
    for name in ['START119.json', 'COMMANDS119.json']:
        retain(launch / name, 'launch/historical_remote119/' + name, 'Actual initial remote-mirror command receipt')
    for source in sorted(launch.glob('shard-*/summary.json')):
        retain(source, 'launch/historical_remote119/' + str(source.relative_to(launch)),
               'Actual per-shard parse/runtime summary; full remote attempts already published')

    retry = AUDIT / 'HISTORICAL_remote_closure119/retry-01'
    for name in ['COMMAND119.json', 'RETRY_ONLY_MANIFEST119.jsonl', 'results/summary.json']:
        already = HIST / 'retry-01' / name
        retain(retry / name, 'launch/retry-01/' + name, 'Exact retry-only custody record',
               existing=already if already.is_file() and filehash(already) == filehash(retry / name) else None)

    local = AUDIT / 'HISTORICAL_local_raw_run'
    retain(local / 'supervisor.json', 'local_raw119/supervisor.json', 'Actual local-read supervisor receipt')
    for source in sorted(local.glob('shard-*.log')):
        retain(source, 'local_raw119/' + source.name, 'Original read/parse log including retained failures')
    for source in sorted(local.glob('shard-*/summary.json')):
        retain(source, 'local_raw119/' + str(source.relative_to(local)), 'Actual local-read shard summary')
    for source in sorted(local.glob('shard-*/records.jsonl')):
        retain(source, 'local_raw119/' + str(source.relative_to(local)) + '.gz',
               'Complete original local-read parse records, not only final hash union', compress=True)

    for name in ['summary.json', 'records.jsonl']:
        retain(AUDIT / 'HISTORICAL_stream_identity_run' / name,
               'priority_identity119/' + name + ('.gz' if name.endswith('.jsonl') else ''),
               'Original priority-identity read, preserving capped first-attempt summaries',
               compress=name.endswith('.jsonl'))
    for name, packaged in [('summary.json', 'R110_JSON_READ_SUMMARY119.json'),
                           ('records.jsonl', 'R110_JSON_MEMBER_READS119.jsonl.gz')]:
        source = AUDIT / 'HISTORICAL_r110_json_run' / name
        already = HIST / packaged
        retain(source, 'r110_json119/' + name + ('.gz' if name.endswith('.jsonl') else ''),
               'Actual complete R110 JSON member parse; source archive custody remains distinct',
               compress=name.endswith('.jsonl'), existing=already if already.is_file() else None)

    # The original manifest is name-bound; retain its compact complete diagnostic
    # bundle even where the current article also contains an identical source.
    for name in ['FOUNDATIONS_MANIFEST119.json', 'FOUNDATIONS_RUN_TIMING119.json',
                 'FOUNDATIONS_AUDIT119.md', 'foundations_main.tex',
                 'foundations_supplement.tex', 'verify_foundations119.py',
                 'foundations_algebra119.json', 'foundations_check119.tex',
                 'foundations_check119.pdf', 'foundations_check119.log']:
        retain(AUDIT / name, 'foundations119/' + name,
               'Original name-bound, non-preregistered proof diagnostic; not new economic observations')

    desired = {'HISTORICAL_objects.jsonl.gz', 'HISTORICAL_commits.jsonl.gz',
               'HISTORICAL_tree_edges.jsonl.gz', 'HISTORICAL_source_blobs.jsonl.gz',
               'HISTORICAL_latex_labels.jsonl.gz', 'HISTORICAL_functions.jsonl.gz',
               'HISTORICAL_primitive_assignments.jsonl.gz', 'HISTORICAL_signatures.jsonl.gz'}
    coverage = json.loads((AUDIT / 'HISTORICAL_coverage.json').read_text())
    members = []
    for item in coverage['exports']:
        if item['file'] in desired:
            source = AUDIT / item['file']
            if source.stat().st_size != item['bytes'] or filehash(source) != item['sha256']:
                raise ValueError('Index source does not match the original coverage receipt')
            members.append({'name': item['file'], 'bytes': item['bytes'],
                            'sha256': item['sha256'], 'original_path': str(source)})
    if {x['name'] for x in members} != desired:
        raise ValueError('Incomplete original index selection')
    members.sort(key=lambda x: x['name'])
    sink = SplitWriter()
    with gzip.GzipFile(filename='', mode='wb', fileobj=sink, mtime=0, compresslevel=9) as gz:
        with tarfile.open(fileobj=gz, mode='w|', format=tarfile.USTAR_FORMAT) as bundle:
            for item in members:
                info = tarfile.TarInfo(item['name'])
                info.size = item['bytes']
                info.mtime = 0
                info.uid = info.gid = 0
                info.uname = info.gname = ''
                info.mode = 0o644
                with Path(item['original_path']).open('rb') as source:
                    bundle.addfile(info, source)
    sink.close_part()
    write_json(DEST / 'INDEX_ARCHIVE119.json', {
        'archive': 'index119.tar.gz', 'bytes': sink.total,
        'sha256': sink.archive_hash.hexdigest(), 'parts': sink.parts,
        'part_byte_limit': PART_BYTES, 'members': members,
        'member_bytes': sum(x['bytes'] for x in members),
        'deterministic_recipe': 'Sorted exact gzip members in USTAR; mtime/uid/gid=0; empty owner names; mode0644; outer gzip filename empty, mtime0, level9; split8MiB.',
        'full_archive_duplicate_written': False,
        'scientific_execution': False})
    write_json(DEST / 'PORTABLE_LOCATION_MANIFEST119.json', {
        'schema': 'NBO-R119-portable-historical-custody-v1',
        'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Exact custody/index/launch/proof-diagnostic material. Original source paths retained as execution identities; no historical/scientific code run and no original bytes edited.',
        'items': items, 'index_archive_manifest': 'INDEX_ARCHIVE119.json',
        'author_package_script_sha256': filehash(Path(__file__)),
        'verification_helper_sha256': filehash(DEST / 'verify_extract119.py'),
        'sqlite_copied': False, 'page_rasterizations_copied': False})
    print(json.dumps({'items': len(items), 'already_present': sum(x['already_packaged_without_duplicate'] for x in items),
                      'archive_parts': len(sink.parts), 'archive_bytes': sink.total,
                      'archive_sha256': sink.archive_hash.hexdigest(),
                      'full_archive_duplicate_written': False}, indent=2))


if __name__ == '__main__':
    main()
