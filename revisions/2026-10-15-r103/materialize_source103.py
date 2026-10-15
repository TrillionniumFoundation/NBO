"""Materialize the actual source frozen before the R103 investment campaign.
No network or experiment execution. All decoded bytes are verified first.
"""
import base64, hashlib, io, zipfile
from pathlib import Path
root = Path(__file__).resolve().parent
encoded = ''.join((root/'frozen_source'/f'source103.part{i}.b64').read_text().strip() for i in range(6))
data = base64.b64decode(encoded, validate=True)
assert hashlib.sha256(data).hexdigest() == '8841650673c720a370440a6101effea572f2c1e795141bbc001b735cafa15287', 'Source transport failed'
expected = {
 'code103/campaign103.py': '2715229fc09b244b52665c3d0ac5bf900497712f5b27627748506c729872d8af',
 'code103/core103.py': '2534095be0c3a99b3f61c37218d3e4c0e6e234cd8de56f1ae7f26f7540268520',
 'code103/test103.py': '0f4b4cf13bec5e2aa786ef1a7b047235e92fbfd533e74fd97d9deec31f4119ec'
}
with zipfile.ZipFile(io.BytesIO(data)) as archive:
 assert set(archive.namelist()) == set(expected), 'Unexpected source member'
 for name, sha in expected.items():
  content = archive.read(name)
  assert hashlib.sha256(content).hexdigest() == sha, name
  target = root/name
  if target.exists():
   assert target.read_bytes() == content, 'Refusing to overwrite changed source: '+name
  else:
   target.parent.mkdir(parents=True, exist_ok=True)
   target.write_bytes(content)
print('Verified and materialized three frozen executable source files.')
