"""Recover the exact native scientific sources; no experiment runs here."""
from pathlib import Path
import hashlib,io,json,lzma,zipfile
root=Path(__file__).resolve().parent
for folder,expected in [('source111','1b1cd6ee15d0b6f996eacc6ade56060b8d56fcd85deffea0f243440bd2497fac'),('source112','49bc20230b9d6411f6776c8f75ba284ea541a08f0edfcb9cf5a727eca2ed9551')]:
    data=b''.join(p.read_bytes() for p in sorted((root/folder).glob('part-*.bin')))
    if hashlib.sha256(data).hexdigest()!=expected:raise SystemExit('Archive identity mismatch: '+folder)
    with zipfile.ZipFile(io.BytesIO(lzma.decompress(data))) as archive:
        for name in archive.namelist():
            p=root/name
            if not p.resolve().is_relative_to(root.resolve()):raise SystemExit('Unsafe member')
            contents=archive.read(name)
            if p.exists() and p.read_bytes()!=contents:raise SystemExit('Refuse to overwrite changed source: '+name)
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(contents)
manifest=json.loads((root/'SOURCE_FREEZE112.json').read_text())
for name,expected in manifest['files'].items():
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise SystemExit('Frozen source mismatch: '+name)
print('VERIFIED',len(manifest['files']),'native Python sources; no numerical campaign was run')
