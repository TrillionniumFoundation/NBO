"""Restore exact frozen R116 Python sources, refusing different existing bytes."""
from pathlib import Path, PurePosixPath
import base64,hashlib,io,json,zipfile
R=Path(__file__).resolve().parent
parts=[(R/'source116'/('part'+str(i)+'.b64')).read_text().strip() for i in range(4)]
b=base64.b64decode(''.join(parts),validate=True)
assert hashlib.sha256(b).hexdigest()=='2c686b3e3be6d6d50e3cdfbc877d26b89564f709b8f6f76dfa230514090c2930'
with zipfile.ZipFile(io.BytesIO(b)) as z:
 freeze=json.loads(z.read('SOURCE_FREEZE116.json'))
 allowed=set(freeze['files'])|{'SOURCE_FREEZE116.json'}
 assert set(z.namelist())==allowed
 for name in sorted(allowed):
  p=PurePosixPath(name)
  assert not p.is_absolute() and '..' not in p.parts
  data=z.read(name)
  if name in freeze['files']:assert hashlib.sha256(data).hexdigest()==freeze['files'][name]
  dest=R/name
  if dest.exists() and dest.read_bytes()!=data:raise RuntimeError('Refuse to overwrite changed source '+name)
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
print('Restored four hash-verified executable files and their source freeze')
