"""Decode the checked source transport into ordinary, reviewable source files.

This is only a transport bootstrap. The publication commits every resulting
Python, TeX, Markdown, and fixture file in its ordinary editable form. Later
tracked source edits are retained rather than overwritten by this seed bundle.
"""
from pathlib import Path, PurePosixPath
import base64
import hashlib
import json
import lzma

REV = Path(__file__).resolve().parent
EXPECTED = 'c0dbc59fe2e1f9d3ae9a85f5203079248720ebe5acb8852cb3bf34cbeaa89184'

def main():
    transport = REV / 'source_transport'
    encoded = ''.join((transport / f'part{i}.b64').read_text().strip() for i in range(6))
    raw = lzma.decompress(base64.b64decode(encoded, validate=True))
    assert hashlib.sha256(raw).hexdigest() == EXPECTED, 'Source transport digest mismatch'
    sources = json.loads(raw)
    assert len(sources) == 21
    manifest = {'transport_sha256': EXPECTED, 'files': {}, 'retained_later_edits': []}
    for name, content in sources.items():
        rel = PurePosixPath(name)
        assert not rel.is_absolute() and '..' not in rel.parts
        assert rel.parts[0] in {'replication', 'paper', 'fixtures', 'RESPONSE.md'}
        dest = REV / rel
        data = content.encode('utf-8')
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_bytes(data)
        elif dest.read_bytes() != data:
            manifest['retained_later_edits'].append(name)
        manifest['files'][name] = {
            'seed_sha256': hashlib.sha256(data).hexdigest(),
            'materialized_sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
        }
    (transport / 'SOURCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
