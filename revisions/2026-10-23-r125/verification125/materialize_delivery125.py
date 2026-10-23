"""Reconstruct exact large evidence files from published binary transport parts.

This performs no economic evaluation and never replaces an existing file.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def checked_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Transport path escapes the revision: ' + relative)
    return path


def digest(path):
    h = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
            size += len(block)
    return size, h.hexdigest()


def materialize(root, manifest):
    root = Path(root).resolve()
    result = []
    for relative, transport in manifest.get('transports', {}).items():
        record = manifest['files'][relative]
        target = checked_path(root, relative)
        concatenated = hashlib.sha256()
        total = 0
        parts = []
        for part_relative in transport['parts']:
            part = checked_path(root, part_relative)
            expected = manifest['files'][part_relative]
            size, sha = digest(part)
            if (size, sha) != (expected['bytes'], expected['sha256']):
                raise ValueError('Transport part differs: ' + part_relative)
            with part.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    concatenated.update(block)
                    total += len(block)
            parts.append(part)
        if (total, concatenated.hexdigest()) != (record['bytes'], record['sha256']):
            raise ValueError('Transport concatenation differs: ' + relative)
        created = False
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                for part in parts:
                    with part.open('rb') as source:
                        for block in iter(lambda: source.read(1024 * 1024), b''):
                            stream.write(block)
            created = True
        if digest(target) != (record['bytes'], record['sha256']):
            raise ValueError('Existing logical evidence differs: ' + relative)
        result.append(dict(path=relative, bytes=total, sha256=record['sha256'],
                           created=created, economic_evaluations=0))
    return result


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'DELIVERY_MANIFEST125.json').read_text())
    print(json.dumps(materialize(root, manifest), indent=2))
