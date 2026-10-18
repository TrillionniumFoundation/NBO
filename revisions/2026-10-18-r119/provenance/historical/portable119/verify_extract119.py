#!/usr/bin/env python3
"""Standard-library verification and safe optional index extraction.

No historical Python module is imported or executed.  No archive pickle or
object array is loaded.  Existing original records retain their paths/bytes.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tarfile


def digest_stream(stream):
    h = hashlib.sha256()
    size = 0
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
        size += len(chunk)
    return size, h.hexdigest()


def digest_file(path):
    with path.open('rb') as f:
        return digest_stream(f)


class PartsReader:
    """A bounded-memory sequential file interface over already verified parts."""
    def __init__(self, paths):
        self.paths = iter(paths)
        self.current = None

    def read(self, size=-1):
        if size < 0:
            raise ValueError('Only bounded reads are permitted')
        out = bytearray()
        while len(out) < size:
            if self.current is None:
                try:
                    self.current = next(self.paths).open('rb')
                except StopIteration:
                    break
            data = self.current.read(size - len(out))
            if data:
                out.extend(data)
            else:
                self.current.close()
                self.current = None
        return bytes(out)

    def close(self):
        if self.current is not None:
            self.current.close()
            self.current = None


def safe_bound(base, relative):
    target = (base / relative).resolve()
    # Existing companion receipts may be one directory above portable119.
    if not target.is_relative_to(base.parent.resolve()):
        raise ValueError(f'Location escapes the historical provenance directory: {relative}')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--extract-index', type=Path,
                        help='Optional new directory for the eight exact compressed index members')
    args = parser.parse_args()
    base = args.directory.resolve()
    locations = json.loads((base / 'PORTABLE_LOCATION_MANIFEST119.json').read_text())
    encodings = {'identity': 0, 'gzip': 0}
    for item in locations['items']:
        p = safe_bound(base, item['packaged_path'])
        size, digest = digest_file(p)
        if (size, digest) != (item['packaged_bytes'], item['packaged_sha256']):
            raise ValueError(f'Packaged identity mismatch: {p}')
        if item['encoding'] == 'gzip':
            with gzip.open(p, 'rb') as stream:
                original = digest_stream(stream)
        elif item['encoding'] == 'identity':
            original = (size, digest)
        else:
            raise ValueError('Unrecognized declared encoding')
        if original != (item['original_bytes'], item['original_sha256']):
            raise ValueError(f'Original-byte identity mismatch: {p}')
        encodings[item['encoding']] += 1

    archive = json.loads((base / 'INDEX_ARCHIVE119.json').read_text())
    paths = []
    total = 0
    combined = hashlib.sha256()
    for part in archive['parts']:
        if Path(part['path']).name != part['path']:
            raise ValueError('Archive part names must be simple basenames')
        p = base / part['path']
        h = hashlib.sha256()
        count = 0
        with p.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
                combined.update(chunk)
                count += len(chunk)
        if (count, h.hexdigest()) != (part['bytes'], part['sha256']):
            raise ValueError(f'Archive part mismatch: {p}')
        total += count
        paths.append(p)
    if (total, combined.hexdigest()) != (archive['bytes'], archive['sha256']):
        raise ValueError('Concatenated archive hash mismatch')

    expected = {x['name']: x for x in archive['members']}
    if len(expected) != len(archive['members']):
        raise ValueError('Duplicate declared archive member')
    output = args.extract_index.resolve() if args.extract_index else None
    if output is not None:
        if output.exists():
            raise ValueError('Extraction destination must be a new directory')
        output.mkdir(parents=True)
    seen = set()
    chain = PartsReader(paths)
    try:
        with gzip.GzipFile(fileobj=chain, mode='rb') as decoded:
            with tarfile.open(fileobj=decoded, mode='r|') as bundle:
                for member in bundle:
                    if (not member.isfile() or Path(member.name).name != member.name
                            or member.name not in expected or member.name in seen):
                        raise ValueError(f'Unexpected/unsafe archive member: {member.name}')
                    record = expected[member.name]
                    if member.size != record['bytes']:
                        raise ValueError(f'Member size mismatch: {member.name}')
                    payload = bundle.extractfile(member)
                    if payload is None:
                        raise ValueError('Regular archive member has no payload')
                    target = (output / member.name).open('xb') if output else None
                    h = hashlib.sha256()
                    count = 0
                    try:
                        for chunk in iter(lambda: payload.read(1024 * 1024), b''):
                            h.update(chunk)
                            count += len(chunk)
                            if target:
                                target.write(chunk)
                    finally:
                        if target:
                            target.close()
                    if (count, h.hexdigest()) != (record['bytes'], record['sha256']):
                        raise ValueError(f'Member bytes mismatch: {member.name}')
                    seen.add(member.name)
            # Read the gzip trailer and any remaining tar padding to check CRC.
            for _ in iter(lambda: decoded.read(1024 * 1024), b''):
                pass
    finally:
        chain.close()
    if seen != set(expected):
        raise ValueError('Archive does not contain exactly the declared index members')
    print(json.dumps({'verified': True, 'original_byte_records': len(locations['items']),
                      'encoding_counts': encodings, 'archive_parts': len(paths),
                      'archive_bytes': total, 'archive_sha256': combined.hexdigest(),
                      'index_members': len(seen),
                      'extracted_to': str(output) if output else None,
                      'historical_code_executed': False}, indent=2))


if __name__ == '__main__':
    main()
