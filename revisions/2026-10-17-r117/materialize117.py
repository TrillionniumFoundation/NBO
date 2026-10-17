"""Restore the exact pre-execution R117 source; never overwrite different bytes."""
from pathlib import Path
import base64,hashlib,io,json,zipfile
root=Path(__file__).resolve().parent
parts=['ff874bcfea31f9947f6c21c3c78545f9ceeb9118','5497aca52dec7fcb4c384a82f74372940811a3e7','56d1cea8e0abef309f3558e7336e403abebe0d9f']
text=[]
for i,sha in enumerate(parts):
    data=(root/'frozen_source117'/f'part{i}.b64').read_bytes()
    if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=sha:raise RuntimeError('Source fragment identity failed')
    text.append(data.strip())
b=base64.b64decode(b''.join(text),validate=True)
if len(b)!=14313 or hashlib.sha256(b).hexdigest()!='fefe2817fc88d7ed843fed837f8e19bc741ee727f4cc0a9c81af4b26efafa92d':raise RuntimeError('Executable archive identity failed')
with zipfile.ZipFile(io.BytesIO(b)) as z:
    expected={'SOURCE_FREEZE117.json','code117/audit117.py','code117/campaign117.py','code117/exact117.py','code117/precision117.py','code117/test117.py'}
    if set(z.namelist())!=expected:raise RuntimeError('Unexpected source path')
    for name in sorted(expected):
        data=z.read(name);p=root/name
        if p.exists() and p.read_bytes()!=data:raise RuntimeError('Refusing to overwrite changed frozen source: '+name)
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
frozen=json.loads((root/'SOURCE_FREEZE117.json').read_text())
for name,h in frozen['files'].items():
    p=root/name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise RuntimeError('Missing or different frozen dependency: '+name)
print('Verified six exact R117 source files and',len(frozen['files']),'scientific identities; no primary experiment executed.')
