"""Materialize the hash-frozen R104 experiment and unchanged R99 dependencies."""
from pathlib import Path
import base64, hashlib, io, json, shutil, zipfile
ROOT = Path(__file__).resolve().parent
NAMES = ['part0', 'part1'] + ['chunk'+str(i) for i in range(4,10)]
raw = base64.b64decode(''.join((ROOT/'frozen_source'/('source104.'+n+'.b64')).read_text().strip() for n in NAMES), validate=True)
assert len(raw) == 21708
assert hashlib.sha256(raw).hexdigest() == '7a279d88d4a74f608e5e79d00f904a4c8bbb17e145148b8fab4198034422719b'
source = ROOT.parent/'2026-10-14-r99'
if source.is_dir():
    for p in sorted(source.rglob('*')):
        rel = p.relative_to(source)
        if not p.is_file() or p.is_symlink() or any(x in {'build','publication','__pycache__'} for x in rel.parts):
            continue
        dest = ROOT/rel
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for name in z.namelist():
        p = Path(name)
        if p.is_absolute() or '..' in p.parts or p.parts[0] not in {'code104','results104'}:
            raise RuntimeError('Invalid archive member: '+name)
        data = z.read(name); dest = ROOT/p
        if dest.exists() and dest.read_bytes() != data:
            raise RuntimeError('Refusing to overwrite changed scientific source: '+name)
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
frozen = json.loads((ROOT/'results104/source_freeze.json').read_text())
for name, digest in frozen['source_files'].items():
    p = ROOT/name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        raise RuntimeError('Missing or changed frozen dependency: '+name)
print('R104 source and all frozen Python dependencies verified.')
