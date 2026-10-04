"""Publish the tested revision; compare the complete historical index in one read."""
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
 # NUL-delimited whole-tree/index reads preserve unusual filenames and avoid
 # a subprocess and index reload for every historical file. No check is removed.
 base={}
 for record in git('ls-tree','-r','-z',BASE).split('\0'):
  if not record:continue
  header,path=record.split('\t',1);mode,kind,sha=header.split()
  if kind=='blob':base[path]=(mode,sha)
 index={}
 for record in git('ls-files','--stage','-z').split('\0'):
  if not record:continue
  header,path=record.split('\t',1);mode,sha,stage=header.split()
  if stage!='0':raise RuntimeError('Unmerged index: '+path)
  index[path]=(mode,sha)
 protected=[]
 for path,identity in base.items():
  if path in ('ECTA.tex','supp.tex','README.md'):continue
  if index.get(path)!=identity:raise RuntimeError('Historical index identity changed: '+path)
  protected.append(path)
 print('Verified complete historical index:',len(protected),'unchanged blobs and modes.',flush=True)
 for path in ('ECTA.tex','supp.tex','README.md'):
  data=(R/'archive'/path).read_bytes()
  sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if sha!=base[path][1]:raise RuntimeError('Original root not archived exactly: '+path)
 selected=[ROOT/'ECTA.tex',ROOT/'supp.tex',ROOT/'README.md']
 manifest_path=R/'results/PUBLICATION_MANIFEST.json'
 for p in R.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p==manifest_path:continue
  if p.suffix not in ('.py','.tex','.json','.md','.log','.pdf'):continue
  selected.append(p)
 # The manifest is intentionally not an entry in its own digest map.
 manifest={'source_commit':source,'base':BASE,'historical_blobs_unchanged':len(protected),'historical_modes_unchanged':True,'exact_original_roots_archived':3,'new_observations':0,'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in selected}}
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');selected.append(manifest_path)
 for i in range(0,len(selected),80):git('add','--sparse','-f','--',*[str(p.relative_to(ROOT)) for p in selected[i:i+80]])
 changes=git('diff','--cached','--no-renames','--name-status','-z',BASE).split('\0')
 if changes and changes[-1]=='':changes.pop()
 if len(changes)%2:raise RuntimeError('Malformed staged change list')
 for i in range(0,len(changes),2):
  status,path=changes[i:i+2]
  allowed=path in ('ECTA.tex','supp.tex','README.md','.github/workflows/nbo-r18-publication.yml') or path.startswith('revisions/2026-10-05-r18/')
  if status not in ('A','M') or not allowed:raise RuntimeError('Out-of-scope staged change: '+status+' '+path)
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
 print(json.dumps(receipt,indent=2),flush=True)
if __name__=='__main__':main()
