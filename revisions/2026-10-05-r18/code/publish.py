"""Publish only this revision after source, mathematical, replay and build audits."""
from pathlib import Path
import subprocess,json,hashlib,os
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
BASE='3a5bae12938077002d1619a0dd32be6071e9adab'
BRANCH='revision/econometrica-nbo-r18-2026-10-05'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def main():
 if os.environ.get('GITHUB_REF_NAME')!=BRANCH:raise RuntimeError('Publication branch mismatch')
 source=os.environ['GITHUB_SHA']
 if git('rev-parse','HEAD')!=source:raise RuntimeError('Checkout changed')
 for name in ('SCIENTIFIC_AUDIT.json','COMPILATION.json'):
  if not (R/'results'/name).is_file():raise RuntimeError('Missing audit '+name)
 scientific=json.loads((R/'results/SCIENTIFIC_AUDIT.json').read_text())
 if not scientific['complete']:raise RuntimeError('Incomplete scientific audit')
 # Record the complete prior Git tree before checking unchanged historical blobs.
 base={}
 for line in git('ls-tree','-r',BASE).splitlines():
  mode_type_sha,path=line.split('\t',1)
  if mode_type_sha.split()[1]=='blob':base[path]=mode_type_sha.split()[2]
 protected=[]
 for path,sha in base.items():
  if path in ('ECTA.tex','supp.tex','README.md'):continue
  if git('rev-parse',':'+path)!=sha:raise RuntimeError('Historical index blob changed: '+path)
  protected.append(path)
 for path in ('ECTA.tex','supp.tex','README.md'):
  data=(R/'archive'/path).read_bytes()
  sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if sha!=base[path]:raise RuntimeError('Original root not archived exactly: '+path)
 selected=[ROOT/'ECTA.tex',ROOT/'supp.tex',ROOT/'README.md']
 for p in R.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts:continue
  if p.suffix not in ('.py','.tex','.json','.md','.log','.pdf'):continue
  selected.append(p)
 manifest={'source_commit':source,'base':BASE,'historical_blobs_unchanged':len(protected),'exact_original_roots_archived':3,'new_observations':0,'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in selected}}
 (R/'results/PUBLICATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 selected.append(R/'results/PUBLICATION_MANIFEST.json')
 # Stage explicit scoped paths, including ignored PDFs; never stage other archives.
 for i in range(0,len(selected),80):git('add','--sparse','-f','--',*[str(p.relative_to(ROOT)) for p in selected[i:i+80]])
 for line in git('diff','--cached','--name-status',BASE).splitlines():
  status,path=line.split('\t',1)
  allowed=path in ('ECTA.tex','supp.tex','README.md','.github/workflows/nbo-r18-publication.yml') or path.startswith('revisions/2026-10-05-r18/')
  if status.startswith('D') or not allowed:raise RuntimeError('Out-of-scope staged change: '+line)
 remote=git('ls-remote','origin','refs/heads/'+BRANCH).split()[0]
 if remote!=source:raise RuntimeError('Remote advanced; publication requires reconciliation')
 git('config','user.name','github-actions[bot]')
 git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
 git('commit','-m','paper(r18): publish nonlinear contrast evidence, exact catalogue accuracy, complete response and native PDFs [skip ci]')
 git('push','origin','HEAD:refs/heads/'+BRANCH)
 head=git('rev-parse','HEAD')
 if git('ls-remote','origin','refs/heads/'+BRANCH).split()[0]!=head:raise RuntimeError('Remote receipt mismatch')
 receipt={'remote_branch':BRANCH,'publication_commit':head,'source_commit':source,'base':BASE,'history_unchanged':len(protected)}
 (ROOT/'R18_REMOTE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
