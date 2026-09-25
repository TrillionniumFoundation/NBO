"""Restore the exact R43 source package from its checked lossless transport."""
from pathlib import Path, PurePosixPath
import base64
import hashlib
import json
import lzma
import shutil

EXPECTED = '06f3d599cf6e42c3b5823f055ba27af083a77df4086d08122dbba3c86af9549a'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def restore(revision):
    root = revision.parents[1]
    source = root / 'revisions/2026-09-25-r42/paper'
    transport = revision / 'transport'
    chunks = [transport / f'payload.{i:02d}.b64' for i in range(5)]
    packed = base64.b64decode(''.join(p.read_text().strip() for p in chunks), validate=True)
    assert sha(packed) == EXPECTED, 'Transport identity mismatch; refusing to restore'
    package = json.loads(lzma.decompress(packed))
    def destination(name):
        rel = PurePosixPath(name)
        assert not rel.is_absolute() and '..' not in rel.parts
        p = revision.joinpath(*rel.parts)
        assert revision in p.resolve().parents
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    for old in source.rglob('*'):
        if old.is_file():
            new = destination('paper/' + old.relative_to(source).as_posix())
            if old.suffix == '.tex':
                content = old.read_text().replace('2026-09-25-r42', '2026-09-25-r43').replace('Revision R42', 'Revision R43')
                new.write_text(content)
            else:
                shutil.copyfile(old, new)
    for name, content in package['files'].items():
        destination(name).write_text(content)
    patched = {}
    for name, patch in package['patches'].items():
        p = destination(name)
        assert sha(p.read_bytes()) == patch['before'], ('Unexpected inherited source', name)
        lines = p.read_text().splitlines(keepends=True)
        for start, stop, replacement in reversed(patch['edits']):
            lines[start:stop] = replacement.splitlines(keepends=True)
        out = ''.join(lines)
        assert sha(out.encode()) == patch['after'], ('Patched source mismatch', name)
        p.write_text(out)
        patched[name] = patch['after']
    for prefix, name in [('ECTA','main'), ('SUPP','supplement'), ('RESPONSE','response'), ('COMPUTATION','computation')]:
        (root / f'{prefix}_R43.tex').write_text('\\input{revisions/2026-09-25-r43/paper/' + name + '}\n')
    protocol = json.loads((revision / 'PROTOCOL_AMENDED.json').read_text())
    for name, expected in protocol['source_sha256'].items():
        assert sha((revision / 'replication' / name).read_bytes()) == expected, name
    record = dict(passed=True, compressed_sha256=EXPECTED, restored_files=len(package['files']), patched_files=patched, numerical_source_identity=True)
    (revision / 'SOURCE_TRANSPORT_VERIFICATION.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))

if __name__ == '__main__':
    restore(Path(__file__).resolve().parents[1])
