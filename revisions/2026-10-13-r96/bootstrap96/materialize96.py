"""Verify the frozen R96 overlay before writing ordinary revision sources."""
from pathlib import Path
import base64,hashlib,io,json,shutil,subprocess,sys,tarfile
R=Path(__file__).resolve().parents[1]
EXPECTED='70bb7b264215e6437ef8bc0c514096d7c19ccc9ee2ea14a682cfb111f545693c'
def main():
    receipt=R/'audit/reproduction96/TRANSPORT96.json'
    if receipt.exists() or (R/'results96/FREEZE96.json').exists():
        raise RuntimeError('Already materialized or scientifically frozen; refuse replacement')
    raw=base64.b64decode(''.join((R/'bootstrap96'/f'part-{i}.b64').read_text().strip() for i in range(3)),validate=True)
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:
        raise RuntimeError('Overlay checksum failed; no source written')
    staged=[];names=set()
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as archive:
        for m in archive:
            p=R/m.name
            if not m.isfile() or not p.resolve().is_relative_to(R.resolve()) or m.name in names:
                raise RuntimeError('Unsafe or duplicate archive member')
            names.add(m.name);f=archive.extractfile(m)
            if f is None:raise RuntimeError('Unreadable source member')
            staged.append((p,f.read()))
    if len(staged)!=22:raise RuntimeError('Unexpected overlay size')
    history=R/'preserved/R95-source';history.mkdir(parents=True,exist_ok=True)
    shutil.copy2(R/'response.md',history/'response.md')
    for p,data in staged:
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    subprocess.run([sys.executable,str(R/'code/integrate96.py')],check=True,cwd=R)
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps({'status':'ordinary-sources-integrated','archive_sha256':EXPECTED,'archive_bytes':len(raw),'files':{str(p.relative_to(R)):hashlib.sha256(data).hexdigest() for p,data in staged},'primary_evaluation_opened':False},indent=2,sort_keys=True)+'\n')
    print('Verified and materialized 22 R96 source files; primary data unopened.',flush=True)
if __name__=='__main__':main()
