"""Lossless source transport; generated ordinary Python files are the review sources."""
import base64,hashlib,json,zlib
from pathlib import Path
root=Path(__file__).resolve().parent
encoded=''.join((root/f'source_extension_bundle.{i}.b64').read_text().strip() for i in range(3))
raw=zlib.decompress(base64.b64decode(encoded,validate=True))
assert hashlib.sha256(raw).hexdigest()=='613fe43a9799374c39daf38df9671f0d76980befc1911143062fd29b0aa9d2bd','source bundle checksum mismatch'
for item in json.loads(raw):
    p=Path(item['path'])
    if not str(p).startswith('replication/r13/') or '..' in p.parts: raise ValueError('invalid bundle path')
    if p.exists() and p.read_text()!=item['text']: raise ValueError('nonidentical existing source: '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(item['text'])
    print(hashlib.sha256(p.read_bytes()).hexdigest(),p)
