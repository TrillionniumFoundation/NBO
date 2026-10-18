"""Create attributable evidence or referee-ready containers from explicit files.

No numerical program is run and no previous archive is overwritten. Every
container and part is hashed; every member is independently read back before
the corresponding manifest is written. Run this after scientific execution.
"""
from __future__ import annotations
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parent
PART_SIZE = 8 * 1024 * 1024
D_SOURCE = 'cafd38aedc5bcbddf5aafee2481fbf5e9a267bab'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def describe(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'bytes': path.stat().st_size, 'sha256': digest(path)}


def write_new(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as target:
        json.dump(data, target, indent=2, sort_keys=True, allow_nan=False)
        target.write('\n')


def split_archive(path):
    parts = []
    with path.open('rb') as source:
        while block := source.read(PART_SIZE):
            target = path.with_name(path.name + '.part' + str(len(parts)).zfill(3))
            with target.open('xb') as output:
                output.write(block)
            sha = hashlib.sha256(block).hexdigest()
            git = hashlib.sha1(b'blob ' + str(len(block)).encode() + b'\0' + block).hexdigest()
            assert digest(target) == sha
            parts.append({'path': target.name, 'bytes': len(block),
                          'sha256': sha, 'git_blob': git})
    h = hashlib.sha256()
    for p in parts:
        with (path.parent / p['path']).open('rb') as source:
            for block in iter(lambda: source.read(1048576), b''):
                h.update(block)
    assert h.hexdigest() == digest(path)
    return {'archive': path.name, 'archive_bytes': path.stat().st_size,
            'archive_sha256': digest(path), 'parts': parts}


def verify_members(container, expected, kind):
    records = {r['path']: r for r in expected}
    assert len(records) == len(expected)
    seen = set()
    handle = tarfile.open(container, 'r:gz') if kind == 'tar' else zipfile.ZipFile(container)
    with handle as archive:
        members = archive if kind == 'tar' else archive.infolist()
        for member in members:
            name = member.name if kind == 'tar' else member.filename
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts
            assert name in records and name not in seen
            assert member.isfile() if kind == 'tar' else not member.is_dir()
            seen.add(name)
            size = member.size if kind == 'tar' else member.file_size
            assert size == records[name]['bytes']
            source = archive.extractfile(member) if kind == 'tar' else archive.open(member)
            h = hashlib.sha256()
            assert source is not None
            with source:
                for block in iter(lambda: source.read(1048576), b''):
                    h.update(block)
            assert h.hexdigest() == records[name]['sha256'], name
    assert seen == set(records)
    return {'verified_members': len(seen), 'verified_uncompressed_bytes': sum(r['bytes'] for r in expected)}


def evidence_d():
    out = ROOT / 'evidence119'
    original = ROOT / 'results119/validation119d_attempt01'
    report = ROOT / 'results119/validation119d_reporting_attempt01'
    launch = ROOT / 'results119/logs/validation119d_attempt01.json'
    executed = json.loads((original / 'EXECUTION119D.json').read_bytes())
    external = json.loads(launch.read_bytes())
    assert executed['status'] == 'passed' and executed['custody_commit'] == D_SOURCE
    assert external['exit_code'] == 0 and external['source_commit'] == D_SOURCE
    assert report.is_dir(), 'Include the first actual completed read-only reporting attempt.'
    reported = json.loads((report / 'R119D_REPORTER_EXECUTION.json').read_bytes())
    assert reported['status'] == 'passed' and not (report / 'FAILED_REPORT119D.json').exists()
    report_files = {x['path']: x for x in reported['outputs']}
    actual_report_files = {p.name for p in report.iterdir() if p.is_file()
                           and p.name != 'R119D_REPORTER_EXECUTION.json'}
    assert len(report_files) == len(reported['outputs']) and set(report_files) == actual_report_files
    for name, row in report_files.items():
        assert Path(name).name == name
        p = report / name
        assert p.stat().st_size == row['bytes'] and digest(p) == row['sha256'], name
    files = sorted([p for directory in (original, report) for p in directory.rglob('*') if p.is_file()]
                   + [launch, launch.with_suffix('.log')])
    members = [describe(p) for p in files]
    path = out / 'validation-d119.tar.gz'
    with path.open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=9, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as tar:
                for p, meta in zip(files, members):
                    info = tarfile.TarInfo(meta['path'])
                    info.size, info.mode, info.mtime = meta['bytes'], 0o644, 0
                    with p.open('rb') as source:
                        tar.addfile(info, source)
    verified = verify_members(path, members, 'tar')
    parts = split_archive(path)
    manifest = {'archive': path.name, 'bytes': path.stat().st_size,
                'sha256': digest(path), 'members': members,
                'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                'scientific_source_commit': D_SOURCE,
                'packager_sha256': digest(Path(__file__)),
                'scope': 'Separate complete D scientific execution and subsequent read-only reporting; the original A/B/C and R110 archives are unchanged.',
                'independent_member_verification': verified}
    write_new(out / 'VALIDATION_D_ARCHIVE119.json', manifest)
    write_new(out / 'VALIDATION_D_ARCHIVE_PARTS119.json', [parts])
    print(json.dumps({'status': 'verified', 'archive': path.name, **verified,
                      'bytes': path.stat().st_size, 'sha256': manifest['sha256'], 'parts': len(parts['parts'])}))


def referee_ready(input_manifest, source_commit):
    spec = json.loads(input_manifest.read_bytes())
    assert re.fullmatch('[0-9a-f]{40}', source_commit), 'Use an immutable full commit SHA.'
    repository = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                             cwd=ROOT, text=True).strip())
    actual_commit = subprocess.check_output(['git', 'rev-parse', '--verify', source_commit + '^{commit}'],
                                           cwd=repository, text=True).strip()
    assert actual_commit == source_commit == spec['author_source_commit']
    prefix = ROOT.relative_to(repository).as_posix() + '/'
    listing = subprocess.check_output(['git', 'ls-tree', '-r', '-z', source_commit, '--', prefix],
                                      cwd=repository)
    source_tree = {}
    for entry in listing.split(b'\0'):
        if not entry:
            continue
        head, name = entry.split(b'\t', 1)
        mode, kind, sha = head.decode().split()
        path = name.decode('utf-8')
        assert kind == 'blob' and mode in ('100644', '100755') and path.startswith(prefix)
        source_tree[path[len(prefix):]] = sha
    assert source_tree
    members = spec['files']
    files = []
    seen = set()
    source_members = set()
    for row in members:
        rel = PurePosixPath(row['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        assert row['path'] not in seen
        seen.add(row['path'])
        p = ROOT.joinpath(*rel.parts)
        assert p.is_file() and p.stat().st_size == row['bytes'] and digest(p) == row['sha256']
        if row['path'] in source_tree:
            assert row['kind'] == 'author_source'
            h = hashlib.sha1(b'blob ' + str(row['bytes']).encode() + b'\0')
            with p.open('rb') as source:
                for block in iter(lambda: source.read(1048576), b''):
                    h.update(block)
            assert h.hexdigest() == source_tree[row['path']] == row['git_blob'], row['path']
            source_members.add(row['path'])
        else:
            assert row['kind'] == 'publication_derivative'
        files.append(p)
    assert source_members == set(source_tree), 'The review package must include every native author-source path.'
    required = {'build/' + d + '.pdf' for d in ('ECTA', 'supp', 'appendix', 'RESPONSE_TO_REFEREE')}
    assert required | {'SOURCE_PDF_MANIFEST119.json', 'PUBLICATION119.json'} <= seen
    pdf_manifest = json.loads((ROOT / 'SOURCE_PDF_MANIFEST119.json').read_bytes())
    publication = json.loads((ROOT / 'PUBLICATION119.json').read_bytes())
    assert pdf_manifest['author_source_commit'] == publication['author_source_commit'] == source_commit
    pdfs = {x['path']: x for x in pdf_manifest['pdfs']}
    assert set(pdfs) == required
    for path, row in pdfs.items():
        assert (ROOT / path).stat().st_size == row['bytes'] and digest(ROOT / path) == row['sha256']
    path = ROOT / 'referee-ready119.zip'
    with zipfile.ZipFile(path, 'x', allowZip64=True) as z:
        for p, meta in zip(files, members):
            info = zipfile.ZipInfo(meta['path'], date_time=(2026, 10, 18, 0, 0, 0))
            info.create_system, info.external_attr = 3, 0o100644 << 16
            packed = p.suffix in ('.gz', '.pdf', '.png', '.zip') or '.part' in p.name
            info.compress_type = zipfile.ZIP_STORED if packed else zipfile.ZIP_DEFLATED
            with p.open('rb') as source, z.open(info, 'w', force_zip64=True) as target:
                for block in iter(lambda: source.read(1048576), b''):
                    target.write(block)
    verified = verify_members(path, members, 'zip')
    parts = split_archive(path)
    manifest = {'archive': path.name, 'bytes': path.stat().st_size,
                'sha256': digest(path), 'parts': parts['parts'], 'members': members,
                'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                'author_source_commit': source_commit,
                'source_tree_verified_members': len(source_members),
                'publication_derivative_members': len(members) - len(source_members),
                'input_manifest': input_manifest.name,
                'input_manifest_sha256': digest(input_manifest),
                'packager_sha256': digest(Path(__file__)),
                'independent_member_verification': verified,
                'scope': 'Complete reviewable native source, four PDFs, protocols, exact evidence containers, all historical indices and actual validation/custody receipts. The archive excludes its own output manifest to avoid a self-hash cycle.'}
    write_new(ROOT / 'REFEREE_READY_PACKAGE119.json', manifest)
    print(json.dumps({'status': 'verified', 'archive': path.name, **verified,
                      'bytes': path.stat().st_size, 'sha256': manifest['sha256'], 'parts': len(parts['parts'])}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    sub.add_parser('evidence-d')
    package = sub.add_parser('referee-ready')
    package.add_argument('--input-manifest', type=Path, required=True)
    package.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    if args.mode == 'evidence-d':
        evidence_d()
    else:
        referee_ready(args.input_manifest.resolve(), args.source_commit)


if __name__ == '__main__':
    main()
