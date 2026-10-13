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
    # Bibliographic and line-breaking corrections; no scientific module, model
    # or primary protocol is altered by this publication-only completion.
    bib=R/'references92-canonical.bib'
    if 'RockafellarUryasev2000,' not in bib.read_text():
        bib.write_text(bib.read_text()+'\n@article{RockafellarUryasev2000,\n  author={Rockafellar, R. Tyrrell and Uryasev, Stanislav},\n  title={Optimization of Conditional Value-at-Risk},\n  journal={The Journal of Risk},\n  year={2000}, volume={2}, number={3}, pages={21--41},\n  doi={10.21314/JOR.2000.038}\n}\n')
    build=R/'code/build95.py';src=build.read_text();needle="    text=(R/'response.md').read_text()"
    if src.count(needle)!=1:raise RuntimeError('Unexpected publication builder version')
    shutil.copy2(build,history/'build95-before-publication-completion.py')
    src=src.replace(needle,needle+"\n    text=re.sub(r'`([0-9a-f]{40,64})`',lambda m:r'\\path{'+m[1]+'}',text)")
    build.write_text(src)
    with (R/'LITERATURE96.md').open('a') as f:
        f.write('\nThe new AVaR threshold citation additionally resolves to Rockafellar and Uryasev (2000), Journal of Risk 2(3), 21--41, DOI 10.21314/JOR.2000.038. Primary publisher record: https://www.risk.net/journal-risk/2161159/optimization-conditional-value-risk .\n')
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps({'status':'ordinary-sources-integrated','archive_sha256':EXPECTED,'archive_bytes':len(raw),'files':{str(p.relative_to(R)):hashlib.sha256(data).hexdigest() for p,data in staged},'publication_only_completion':['AVaR citation resolved','Breakable full commit hashes in typeset response'],'primary_evaluation_opened':False},indent=2,sort_keys=True)+'\n')
    print('Verified and materialized 22 R96 source files; primary data unopened.',flush=True)
if __name__=='__main__':main()
