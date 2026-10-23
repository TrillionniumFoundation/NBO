"""Build a source-bound referee package, or recover its exact transport bytes.

This is an archive operation. It never runs the economic model or alters the
declared source, original results, logical witnesses, or delivery manifest.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STAMP = (2026, 10, 23, 0, 0, 0)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path escapes the declared package root: ' + relative)
    return path


def assemble(metadata):
    record = json.loads(metadata.read_text())
    base = metadata.parent
    destination = inside(base, record['archive_name'])
    if destination.exists():
        assert destination.stat().st_size == record['archive_bytes']
        assert digest(destination) == record['archive_sha256']
        return {'status': 'already-exact', 'path': str(destination)}
    temporary = destination.with_name(destination.name + '.assembling')
    with temporary.open('xb') as output:
        for part in record['parts']:
            source = inside(base, part['path'])
            assert source.stat().st_size == part['bytes'], part['path']
            assert digest(source) == part['sha256'], part['path']
            with source.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    output.write(block)
    assert temporary.stat().st_size == record['archive_bytes']
    assert digest(temporary) == record['archive_sha256']
    temporary.rename(destination)
    return {'status': 'assembled-exact', 'path': str(destination)}


def build(args):
    start = time.perf_counter()
    for value in (args.source_commit, args.source_tree):
        if not value or not re.fullmatch('[0-9a-f]{40}', value):
            raise ValueError('A complete published commit and tree SHA are required.')
    manifest_path = ROOT / 'DELIVERY_MANIFEST125.json'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['phase'] == 'complete'
    assert manifest['separate_followup_completed'] is True
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    logical = set(manifest['transports'])
    for relative, expected in manifest['files'].items():
        path = inside(ROOT, relative)
        if relative in logical and not path.exists():
            continue
        assert path.stat().st_size == expected['bytes'], relative
        assert digest(path) == expected['sha256'], relative
    identity = {'schema': 1, 'published_author_commit': args.source_commit,
                'published_author_root_tree': args.source_tree,
                'scientific_freeze': manifest['scientific_source_commit'],
                'separate_followup_freeze': manifest['separate_followup_source_commit'],
                'delivery_manifest_sha256': digest(manifest_path),
                'logical_witness_transport': manifest['transports'],
                'pdfs': {k: v for k, v in manifest['files'].items()
                         if k in {'build/ECTA.pdf', 'build/supp.pdf',
                                  'build/appendix.pdf', 'build/RESPONSE_TO_REFEREE.pdf'}},
                'scope': 'Exact author source and saved evidence. CI state belongs to the separately dated release receipt.'}
    readme = ('NEURAL BELLMAN OPERATORS — R125 REFEREE PACKAGE\n\n'
              'Author source commit: ' + args.source_commit + '\n'
              'Read README.md and the four PDFs in build/.\n'
              'Large original witnesses are delivered as exact ordered binary parts.\n'
              'From this directory, reconstruct and verify every logical evidence file with:\n'
              '  python verification125/verify_package125.py --output verification_runs/readback01\n'
              'The verification does not rerun the economy. For a fresh execution use the\n'
              'separate exclusive-output commands and frozen protocols in README.md.\n'
              'Original and follow-up audits retain separate identities and costs.\n'
              'No remote CI success is inferred from the existence of this archive.\n')
    archive = output / 'NBO-R125-referee-ready.zip'
    entries = []
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6, allowZip64=True) as z:
        def add(relative, data):
            info = zipfile.ZipInfo('NBO-R125/' + relative, STAMP)
            info.compress_type = (zipfile.ZIP_STORED if re.search(r'\.part\d+$|\.gz$', relative)
                                  else zipfile.ZIP_DEFLATED)
            info.external_attr = 0o100644 << 16
            z.writestr(info, data, compresslevel=6)
            entries.append(relative)
        for relative in sorted(set(manifest['files']) - logical):
            add(relative, (ROOT / relative).read_bytes())
        add('DELIVERY_MANIFEST125.json', manifest_path.read_bytes())
        add('SNAPSHOT_IDENTITY125.json', (json.dumps(identity, indent=2) + '\n').encode())
        add('README_REFEREE_READY.txt', readme.encode())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.infolist()) == len(entries)
        for relative, expected in manifest['files'].items():
            if relative in logical:
                h = hashlib.sha256()
                size = 0
                for part in manifest['transports'][relative]['parts']:
                    data = z.read('NBO-R125/' + part)
                    h.update(data)
                    size += len(data)
                assert (size, h.hexdigest()) == (expected['bytes'], expected['sha256'])
            else:
                data = z.read('NBO-R125/' + relative)
                assert len(data) == expected['bytes']
                assert hashlib.sha256(data).hexdigest() == expected['sha256']
    receipt = {**identity, 'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'archive_name': archive.name, 'archive_bytes': archive.stat().st_size,
               'archive_sha256': digest(archive), 'archive_entries': len(entries),
               'all_manifest_files_verified_inside_archive': True,
               'logical_witnesses_verified_from_archive_parts': sorted(logical),
               'economic_evaluations': 0, 'parts': []}
    if args.split_bytes:
        if args.split_bytes < 1:
            raise ValueError('Split size must be positive.')
        with archive.open('rb') as source:
            index = 0
            while block := source.read(args.split_bytes):
                part = output / (archive.name + '.part' + str(index).zfill(2))
                with part.open('xb') as stream:
                    stream.write(block)
                receipt['parts'].append({'path': part.name, 'bytes': len(block),
                                         'sha256': hashlib.sha256(block).hexdigest()})
                index += 1
    receipt['seconds'] = time.perf_counter() - start
    (output / 'RELEASE_ARCHIVE125.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-commit')
    parser.add_argument('--source-tree')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--split-bytes', type=int, default=0)
    parser.add_argument('--assemble', type=Path)
    args = parser.parse_args()
    if args.assemble:
        result = assemble(args.assemble.resolve())
    else:
        if args.output is None:
            parser.error('--output is required for archive construction')
        result = build(args)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
