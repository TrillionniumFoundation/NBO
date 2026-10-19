"""Assemble and fully verify the distributed R119 referee-ready ZIP parts.

No manuscript, experimental code, extraction, or network request is executed.
Use a fresh output path; failed attempts are retained and never overwritten.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--manifest', type=Path, default=Path('REFEREE_READY_PACKAGE119.json'))
    a.add_argument('--parts-dir', type=Path, default=Path('.'))
    a.add_argument('--output', type=Path, required=True)
    args = a.parse_args()
    spec = json.loads(args.manifest.read_bytes())
    assert spec['author_source_commit'] == '6250abfd317f3b2a56cb1303eb5ce78249bf4042'
    assert not args.output.exists(), 'Choose a fresh output path.'
    whole, total = hashlib.sha256(), 0
    with args.output.open('xb') as output:
        for i, row in enumerate(spec['parts']):
            assert row['path'] == 'referee-ready119.zip.part' + str(i).zfill(3)
            part, n = hashlib.sha256(), 0
            with (args.parts_dir / row['path']).open('rb') as source:
                for block in iter(lambda: source.read(1048576), b''):
                    part.update(block)
                    whole.update(block)
                    n += len(block)
                    output.write(block)
            assert n == row['bytes'] and part.hexdigest() == row['sha256'], row['path']
            total += n
    assert total == spec['bytes'] and whole.hexdigest() == spec['sha256']
    expected = {r['path']: r for r in spec['members']}
    assert len(expected) == len(spec['members'])
    seen = set()
    with zipfile.ZipFile(args.output) as archive:
        for member in archive.infolist():
            name = member.filename
            p = PurePosixPath(name)
            assert not p.is_absolute() and '..' not in p.parts
            assert not member.is_dir() and name in expected and name not in seen
            assert member.file_size == expected[name]['bytes']
            h = hashlib.sha256()
            with archive.open(member) as source:
                for block in iter(lambda: source.read(1048576), b''):
                    h.update(block)
            assert h.hexdigest() == expected[name]['sha256'], name
            seen.add(name)
    assert seen == set(expected)
    print(json.dumps({'status': 'verified', 'bytes': total, 'sha256': whole.hexdigest(),
                      'parts': len(spec['parts']), 'members': len(seen), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
