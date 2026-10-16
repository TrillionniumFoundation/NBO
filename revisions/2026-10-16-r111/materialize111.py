"""Restore and verify the actual R111 executable bytes; no network required."""
from pathlib import Path
import hashlib,io,json,lzma,zipfile
root=Path(__file__).resolve().parent
payload=b''.join((root/'source111'/('part-%02d.bin'%i)).read_bytes() for i in range(4))
assert len(payload)==21256
assert hashlib.sha256(payload).hexdigest()=='1b1cd6ee15d0b6f996eacc6ade56060b8d56fcd85deffea0f243440bd2497fac'
with zipfile.ZipFile(io.BytesIO(lzma.decompress(payload))) as archive:
    for name in archive.namelist():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or not (name.startswith('code111/') or name in ('SOURCE_FREEZE111.json','requirements111.txt')):
            raise RuntimeError('Unexpected archive member: '+name)
        data=archive.read(name);dest=root/p
        if dest.exists() and dest.read_bytes()!=data:
            raise RuntimeError('Refusing to overwrite different local source: '+name)
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
manifest=json.loads((root/'SOURCE_FREEZE111.json').read_text())
for name,expected in manifest['files'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name
print('Verified actual R111 source and',len(manifest['files']),'frozen Python files')
