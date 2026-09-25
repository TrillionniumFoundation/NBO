"""Restore the exact pre-execution source bundle; never alter inherited files."""
from pathlib import Path
import base64,gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'revisions/2026-09-25-r44'
patches={'source.00.b64':[(1009,1009,'/T',''),(2956,2958,'','fZ'),(9826,9828,'','cl')],'source.01.b64':[(12352,12352,'9','')],'source.02.b64':[]}
raw_sha={'source.00.b64':'107e215e9f7abd4b8bf6a7254a17d88f61f4772f7d5a51aac46a62bcca6e04cf','source.01.b64':'0625623d752c4518050793c0549cf0578108bf433d2bde18489474dd82e3ab7b','source.02.b64':'6362557679785c8f919445c0d6ed5f30c6f8649f7521f46be83858a1754e065f'}
parts=[]
for name,edits in patches.items():
    text=(R/'transport'/name).read_text().strip()
    assert hashlib.sha256(text.encode()).hexdigest()==raw_sha[name],name
    for start,end,replacement,old in reversed(edits):
        assert text[start:end]==old
        text=text[:start]+replacement+text[end:]
    parts.append(text)
data=base64.b64decode(''.join(parts),validate=True)
assert hashlib.sha256(data).hexdigest()=='c741095b73e64806a359efb344346bec7809342bab4d29444f0a99b07aa755a2'
files=json.loads(gzip.decompress(data));identities={}
for rel,text in files.items():
    path=ROOT/rel
    assert rel.startswith('revisions/2026-09-25-r44/') and '..' not in Path(rel).parts
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    identities[rel]=hashlib.sha256(path.read_bytes()).hexdigest()
(R/'SOURCE_TRANSPORT_VERIFICATION.json').write_text(json.dumps({'passed':True,'compressed_sha256':hashlib.sha256(data).hexdigest(),'transport_corrections_before_experiments':patches,'restored_sha256':identities},indent=2)+'\n')
print('Restored and verified',len(files),'source/model files before execution.')
