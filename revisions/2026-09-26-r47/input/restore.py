"""Materialize the hash-checked R47 authoring sources without changing ancestry."""
from pathlib import Path, PurePosixPath
import hashlib, io, json, subprocess, tarfile

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'revisions/2026-09-26-r47'
BASE = 'fb88b1122ce5709d36104993937083b57470d1de'
ARCHIVE = 'ae61f3bcb5a5620b60620f34c711261bce6ed1f69626da90018146d3102cf845'
PARTS = [
 'bbf59fd96ad2ff2193b10f3b51ddd9b7be9e6012',
 'd50ca7f19390221d89bbd8fa8e06a003e357b311',
 '762f022109e7ff8cb1bf32f1f14480af7b8c256e',
 '518176c31c69c049e4f4e8744cedeb214bf5fcf4',
 'fa8f28f878a604a86cd43c7a0ece8a791d0de5dd',
 '6f3676e0c9cebd1298cd622a5acf85df107be746',
 'da485118409829e7f26ddf15266fd0c98d0c54d2',
 '28b04435ed3d05b9afa5d391c8b95823ba0ca2a6',
]
parts = []
for i, expected in enumerate(PARTS):
    b = (R / 'input' / f'source.{i:02d}.part').read_bytes()
    actual = hashlib.sha1(f'blob {len(b)}\0'.encode() + b).hexdigest()
    if actual != expected:
        raise ValueError(f'Corrupted source part {i}: {actual}')
    parts.append(b)
data = b''.join(parts)
if hashlib.sha256(data).hexdigest() != ARCHIVE:
    raise ValueError('Source archive hash mismatch')
baseline = set(subprocess.check_output(
    ['git', 'ls-tree', '-r', '--name-only', BASE], cwd=ROOT, text=True).splitlines())
root_names = {'R47_BUILD.sh', 'R47_REVIEW.md'}
root_names.update(f'{n}_R{v}.tex' for v in [45, 47]
                  for n in ['ECTA', 'SUPP', 'RESPONSE', 'HISTORY'])
root_names.add('COMPUTATION_R47.tex')
with tarfile.open(fileobj=io.BytesIO(data), mode='r:xz') as tf:
    seen = set()
    for m in tf.getmembers():
        p = PurePosixPath(m.name)
        if (not m.isfile() or p.is_absolute() or '..' in p.parts
                or m.name in seen):
            raise ValueError(f'Unsafe or duplicate archive entry: {m.name}')
        if not (m.name in root_names or m.name.startswith(
                ('revisions/2026-09-25-r45/', 'revisions/2026-09-26-r47/'))):
            raise ValueError(f'Out-of-scope archive entry: {m.name}')
        if m.name in baseline:
            raise ValueError(f'Archive would modify inherited file: {m.name}')
        seen.add(m.name)
        target = ROOT / m.name
        content = tf.extractfile(m).read()
        if target.exists() and target.read_bytes() != content:
            raise ValueError(f'Conflicting existing new source: {m.name}')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
manifest = json.loads((R / 'SOURCE_MANIFEST.json').read_text())
if seen != set(manifest) | {'revisions/2026-09-26-r47/SOURCE_MANIFEST.json'}:
    raise ValueError('Source inventory mismatch')
for name, digest in manifest.items():
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
        raise ValueError(f'Materialized source mismatch: {name}')
inputs = json.loads((R / 'history/INPUT_IDENTITY.json').read_text())
for name, digest in inputs.items():
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
        raise ValueError(f'Frozen scientific input mismatch: {name}')
(R / 'paper/generated').mkdir(parents=True, exist_ok=True)
(R / 'build').mkdir(parents=True, exist_ok=True)
(R / 'build/source_identity.json').write_text(json.dumps({
    'passed': True, 'archive_sha256': ARCHIVE, 'source_files': len(manifest),
    'frozen_input_files': len(inputs), 'base_commit': BASE,
    'baseline_tracked_files': len(baseline)
}, indent=2) + '\n')
print(f'Materialized {len(manifest)} authoring sources; checked {len(inputs)} frozen inputs.')
