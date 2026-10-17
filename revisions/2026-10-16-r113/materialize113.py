"""Restore and verify exact R113 executable bytes; no experiment is run."""
from pathlib import Path
import hashlib,io,json,lzma,tarfile,subprocess,sys
R=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(R/'materialize112.py')],check=True)
parts=[('part-00.bin','5eb7f842a8d4072b580f37266cff47bdc5825f486f63ff77c1a2b6c78201e7a6'),('part-01.bin','9858bb2726f1b71837e30d1625d4d820fdb5a93f3fb0520979ed2bc15a708892'),('part-02.bin','889423a102dac392af86519e905e53d05f1f88bd04333c43ef92fc872aed6227'),('part-03.bin','355e146a087077bd4524af161004a3a13275e6353d85eef41a3620425f200735'),('part-04.bin','c1de4f078167603ff421a858c09253a142875cd36476b4dccf295742eb24fc58')]
raw=[]
for p,h in parts:
    d=(R/'source113'/p).read_bytes()
    if hashlib.sha256(d).hexdigest()!=h:raise ValueError('Source fragment differs: '+p)
    raw.append(d)
z=b''.join(raw)
if len(z)!=21564 or hashlib.sha256(z).hexdigest()!='dff1c0598f0396f7587071b97798508432e38b22fd8190d465760e26ab1bec30':raise ValueError('Source archive identity')
records={}
with tarfile.open(fileobj=io.BytesIO(lzma.decompress(z)),mode='r:') as t:
    for e in t.getmembers():
        p=(R/e.name).resolve()
        if not e.isfile() or not p.is_relative_to(R) or e.name in records:raise ValueError('Unsafe or repeated source member')
        records[e.name]=t.extractfile(e).read()
records['code113/independent_control111.py']=lzma.decompress((R/'auditcode111/independent111.py.xz').read_bytes())
if hashlib.sha256(records['code113/independent_control111.py']).hexdigest()!='15f721618a80328e6d318f5ee7a73dc2aa06573b138dee3dd1c8362624a6fc4a':raise ValueError('Independent checker identity')
if hashlib.sha256(records['SOURCE_FREEZE113.json']).hexdigest()!='de2994cdde7d55ba6538b6ed12a73c831c416c39ea4c4ffec907009cdceb8727':raise ValueError('Manifest identity')
for p,d in records.items():
    q=R/p
    if q.exists() and q.read_bytes()!=d:raise FileExistsError('Refuse changed source: '+p)
for p,d in records.items():
    q=R/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(d)
m=json.loads((R/'SOURCE_FREEZE113.json').read_text())
for p,h in m['files'].items():
    if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen dependency differs: '+p)
print('Verified',len(m['files']),'native Python files; no scientific campaign executed.')
