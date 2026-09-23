#!/usr/bin/env python3
"""Recover exactly the delivered source and independently pinned audit inputs."""
from pathlib import Path, PurePosixPath
import base64, hashlib, io, json, subprocess, tempfile, zipfile, zlib

ROOT = Path.cwd()
REV = ROOT / 'revisions/2026-09-23-r26'
EXPECTED = [
 '608efabe49b3f841c7e10a18e656575dfec1e79c',
 '0950f6d8721d8f502cc3e49c7872428b4ba5aac5',
 'b5ef414c49d6fc9a37ae0bc3feeca99b894af87a',
 'df894c3132a400573f1237395d57a86539efa08b',
 'ba10ee6ecfb409f8f8765133415e93a15925b6e0',
 '30b13f676029260fe4a0dd8b9aff2ec9d32dc339',
 '46ee8a224ea82cca5d9370d78833d84c091bba5b',
 'dea5b794354bd5f3bb0243b5d0365c9220a411c4',
 '75c188b1644997ef0402d55940eb34953f7ca9db',
 'c989ca0da1612b1e35f33c71b4bfdfe3a0821afa',
 '65f67af539788bc20151390c31ea6cbff9c7a769',
]
chunks=[]
for i, want in enumerate(EXPECTED):
    data=(ROOT/f'.r26/part{i:02d}.b64').read_bytes()
    got=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if got != want: raise RuntimeError(f'Transmission mismatch at chunk {i}: {got}')
    chunks.append(data.strip())
raw=zlib.decompress(base64.b64decode(b''.join(chunks), validate=True))
assert hashlib.sha256(raw).hexdigest() == 'caad5af9a8f8496780446046554feff87eadd7faadfcba7d7308fbf525140fbe'
files=json.loads(raw)
assert len(files)==35
allowed={'ECTA_R26.tex','RESPONSE_R26.tex','SUPP_R26.tex','R26_REVIEW.md','REVISION_INDEX.md'}
for path, text in files.items():
    p=PurePosixPath(path)
    assert not p.is_absolute() and '..' not in p.parts
    assert path in allowed or path.startswith('revisions/2026-09-23-r26/')
    target=ROOT/path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text,encoding='utf-8')
print('Verified and materialized 35 delivered source files.')

def downloaded(artifact_id, want, destination):
    with destination.open('wb') as output:
        subprocess.run(['gh','api',f'repos/TrillionniumFoundation/NBO/actions/artifacts/{artifact_id}/zip'],stdout=output,check=True)
    got=hashlib.sha256(destination.read_bytes()).hexdigest()
    if got != want: raise RuntimeError(f'Pinned archive hash mismatch: {artifact_id}: {got}')

def inventory(z):
    return {i.filename:hashlib.sha256(z.read(i)).hexdigest()
            for i in z.infolist() if not i.is_dir() and '__pycache__' not in PurePosixPath(i.filename).parts and not i.filename.endswith('.pyc')}

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n')

with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    downloaded(10741115093,'c8a546a74888e9e0127724cdcd2a2008a8e70f444fdb8ea0ab09d26983bb0e6d',tmp/'r24.zip')
    with zipfile.ZipFile(tmp/'r24.zip') as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read('dist/NBO_R24_referee_source.zip'))) as source:
            r24=inventory(source)
    downloaded(10742814762,'5a63c11abec99d16644f4d09cbac35bd921e2c3f45e97c8f5c49c9ed304c247c',tmp/'r25.zip')
    with zipfile.ZipFile(tmp/'r25.zip') as source:
        r25=inventory(source)
assert len(r24)==5760 and len(r25)==781
write(REV/'source_audit/R24_BASE_SHA256.json',r24)
write(REV/'source_audit/R25_IMPORTED_SHA256.json',r25)
for name, manifest in [('R24',r24),('R25',r25)]:
    for path, want in manifest.items():
        target=ROOT/path if name=='R24' else ROOT/'revisions/2026-09-23-r25'/path
        if name=='R24' and path=='REVISION_INDEX.md':
            target=REV/'source_audit/REVISION_INDEX_before_R26.md'
        assert target.is_file(), f'Missing historical {name} file: {path}'
        assert hashlib.sha256(target.read_bytes()).hexdigest()==want, f'Historical mutation: {name}/{path}'
print('Verified all 5760 R24 archive files and 781 R25 evidence files.')
for filename, want in [('ECTA_R24.pdf','018296c267190387fc421e9616a40556de6c1551322b88c44546e58bde1ffd06'),('SUPP_R24.pdf','f0f51417f598d85f97df4634c447396c0fbf4b78f51163f5c791177e5b24d7af')]:
    data=(ROOT/filename).read_bytes()
    assert hashlib.sha256(data).hexdigest()==want
    dest=REV/'history'/filename.replace('.pdf','_as_reviewed.pdf')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
(REV/'results').mkdir(exist_ok=True)
write(REV/'source_audit/remote_publication_inputs.json',{
    'source_payload_sha256':hashlib.sha256(raw).hexdigest(),
    'delivered_source_files':len(files),'r24_inventory_files':len(r24),'r25_inventory_files':len(r25),
    'frozen_base':'c78d934c0b3b8d346a40c7ddcaf415e167462265',
    'publication_policy':'Reproduce binary evidence and PDFs, verify, then atomically create two isolated revision refs. No force push.',
    'preparation_status_note':'preparation_status.json describes the original local preparation; remote publication is established by the workflow receipt and remote refs.'
})
