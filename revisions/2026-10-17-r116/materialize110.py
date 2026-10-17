"""Restore exact publication support bytes; never alter a nonmatching local file.

The current empirical table and bulky author/build support use lossless source
transport. This is not numerical execution and grants no scientific CI verdict.
"""
from pathlib import Path
import base64, hashlib, io, json, lzma, tarfile
R=Path(__file__).resolve().parent
m=json.loads((R/'SOURCE_SUPPORT110.json').read_text())
parts=[]
for p in m['parts']:
    d=(R/p['path']).read_bytes()
    if hashlib.sha256(d).hexdigest()!=p['sha256']:raise ValueError('Source fragment differs: '+p['path'])
    parts.append(d)
z=b''.join(parts)
if hashlib.sha256(z).hexdigest()!=m['archive_sha256']:raise ValueError('Source archive digest')
raw=lzma.decompress(z)
records={}
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as t:
    for info in t.getmembers():
        if not info.isfile() or info.name not in m['files']:raise ValueError('Unexpected source member')
        p=(R/info.name).resolve()
        if not p.is_relative_to(R):raise ValueError('Unsafe source path')
        d=t.extractfile(info).read()
        if hashlib.sha256(d).hexdigest()!=m['files'][info.name]:raise ValueError('Member source digest')
        records[p]=d
if len(records)!=len(m['files']):raise ValueError('Incomplete source archive')
table=lzma.decompress((R/'new110/full_tables.tex.xz').read_bytes())
if hashlib.sha256(table).hexdigest()!='cd6d1ea7bcb19f740ee2649a71716ed0901c4bc46e0013dd7892e9c52b5ab3dd':raise ValueError('Table source digest')
records[R/'new110/full_tables.tex']=table
# Validate all existing destinations before writing any missing source.
for p,d in records.items():
    if p.exists() and p.read_bytes()!=d:raise FileExistsError('Refuse to overwrite modified source: '+str(p))
for p,d in records.items():
    if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(d)
print('Verified/restored',len(records),'exact source files; no experiment run.')
