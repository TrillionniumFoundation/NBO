"""Verify and extract the complete immutable evidence, without overwriting files."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence119'
MANIFESTS = {'current': 'CURRENT_RESULTS_ARCHIVE119.json',
             'r110': 'R110_GENERATED_ARCHIVE119.json',
             'validationd': 'VALIDATION_D_ARCHIVE119.json'}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while b := f.read(1048576):
            h.update(b)
    return h.hexdigest()


def process(kind, destination=None):
    spec = json.loads((EVIDENCE / MANIFESTS[kind]).read_bytes())
    parts_name = 'VALIDATION_D_ARCHIVE_PARTS119.json' if kind == 'validationd' else 'ARCHIVE_PARTS119.json'
    part_spec = next(x for x in json.loads((EVIDENCE / parts_name).read_bytes())
                     if x['archive'] == spec['archive'])
    expected = {x['path']: x for x in spec['members']}
    assert len(expected) == len(spec['members'])
    if destination:
        destination = Path(destination).resolve()
        destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='nbo-evidence119-') as tmp:
        archive = Path(tmp) / spec['archive']
        total = 0
        with archive.open('wb') as output:
            for part in part_spec['parts']:
                p = EVIDENCE / part['path']
                assert p.stat().st_size == part['bytes'] and digest(p) == part['sha256'], part['path']
                with p.open('rb') as source:
                    while b := source.read(1048576):
                        output.write(b)
                        total += len(b)
        assert total == spec['bytes'] == part_spec['archive_bytes']
        assert digest(archive) == spec['sha256'] == part_spec['archive_sha256']
        seen = set()
        with tarfile.open(archive, 'r:gz') as tar:
            for member in tar:
                name = member.name
                path = PurePosixPath(name)
                assert member.isfile() and not path.is_absolute() and '..' not in path.parts
                assert name in expected and name not in seen
                seen.add(name)
                meta = expected[name]
                assert member.size == meta['bytes'], name
                target = destination.joinpath(*path.parts) if destination else None
                if target:
                    assert destination == target.resolve() or destination in target.resolve().parents
                    if target.exists():
                        assert target.is_file() and target.stat().st_size == meta['bytes'] and digest(target) == meta['sha256'], name
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                h = hashlib.sha256()
                handle = target.open('xb') if target and not target.exists() else None
                try:
                    source = tar.extractfile(member)
                    assert source is not None
                    with source:
                        while b := source.read(1048576):
                            h.update(b)
                            if handle:
                                handle.write(b)
                finally:
                    if handle:
                        handle.close()
                assert h.hexdigest() == meta['sha256'], name
        assert seen == set(expected)
    return {'scope': kind, 'verified_files': len(seen),
            'verified_uncompressed_bytes': sum(x['bytes'] for x in expected.values()),
            'archive_sha256': spec['sha256'],
            'destination': str(destination) if destination else None,
            'scientific_execution': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['verify', 'extract-current', 'extract-r110', 'extract-validationd'])
    parser.add_argument('--destination')
    args = parser.parse_args()
    if args.action == 'verify':
        assert args.destination is None
        results = [process(kind) for kind in MANIFESTS]
    else:
        if args.destination is None:
            parser.error('Extraction requires an explicit destination; existing files are never overwritten.')
        results = [process(args.action.removeprefix('extract-'), args.destination)]
    print(json.dumps({'status': 'verified', 'archives': results}, indent=2))


if __name__ == '__main__':
    main()
