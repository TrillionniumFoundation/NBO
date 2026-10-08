"""Restore pinned inputs, execute a fresh R41 catalogue, and publish one commit.

Runs only in the dedicated source branch. No historical entry is changed.
The initial source bundle and workflow are immutable inputs to this run.
"""
from pathlib import Path,PurePosixPath
import os,sys,json,hashlib,base64,zipfile,io,shutil,subprocess,requests,time
REPO='TrillionniumFoundation/NBO';BRANCH='revision/econometrica-nbo-r41-source-2026-10-07';REL='revisions/2026-10-07-r41'
SRC=os.environ['GITHUB_SHA'];WORK=Path('work').resolve();R=WORK/REL
API='https://api.github.com/repos/'+REPO
SESSION=requests.Session();SESSION.headers.update({'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
def call(method,path,**kw):
 for attempt in range(4):
  res=SESSION.request(method,API+path,timeout=180,**kw)
  if res.status_code<500:break
  time.sleep(2**attempt)
 res.raise_for_status();return res.json()
def digest(b):return hashlib.sha256(b).hexdigest()
def artifact(i,h):
 res=SESSION.get(API+f'/actions/artifacts/{i}/zip',timeout=180);res.raise_for_status();assert digest(res.content)==h,(i,'artifact digest mismatch')
 z=zipfile.ZipFile(io.BytesIO(res.content))
 for info in z.infolist():
  p=PurePosixPath(info.filename);assert not p.is_absolute() and '..' not in p.parts
 z.extractall(WORK);return dict(artifact_id=i,sha256=h,files=len(z.infolist()))
def run(path):
 subprocess.run([sys.executable,str(R/path)],cwd=WORK,check=True)
def restore():
 WORK.mkdir(exist_ok=True)
 inherited=[artifact(11454277229,'d295c8593277373b4d016d17cd6268bf960d6e3936ba49c70ec9e1c1f83f1844')]
 manifest=json.loads((WORK/'revisions/2026-10-07-r39/audit/FILES_SHA256.json').read_text())
 for name,h in manifest.items():assert digest((WORK/name).read_bytes())==h,name
 inherited.append(artifact(11458577321,'20be1bb8744652bf84af9192e26129e147da992e4c5630b8060d71a48a25d20e'))
 old=WORK/'revisions/2026-10-07-r40';r39=WORK/'revisions/2026-10-07-r39'
 for name in ['code','vendor','inputs']:shutil.copytree(old/name,R/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
 for name in ['audit','results','manuscript','retained','publication']:(R/name).mkdir(exist_ok=True)
 shutil.copytree(r39/'retained',R/'retained',dirs_exist_ok=True)
 shutil.copy2(old/'retained/referee_report_R39.md',R/'retained/referee_report_R39.md')
 p=R/'code/study.py';s=p.read_text().replace('R40_STUDY','R41_STUDY')
 needle="stale=nl.own_value(old['candidate']";assert needle in s
 s=s.replace(needle,"old['candidate']['knots']=np.asarray(old['candidate']['knots']);old['candidate']['actors']=[np.asarray(a) for a in old['candidate']['actors']]\n    stale=nl.own_value(old['candidate']")
 s=s.replace("protocol_commit='d66fc832e67050518317de6f505bcd2eb98a3158'","inherited_protocol_commit='d66fc832e67050518317de6f505bcd2eb98a3158',execution_location='Fresh R41 GitHub execution after local development replay; inherited clocks unchanged'")
 p.write_text(s)
 protocol=(old/'STUDY_PROTOCOL.md').read_text().replace('# R40 study protocol','# R41 study protocol')
 (R/'STUDY_PROTOCOL.md').write_text(protocol+'\n## Complete R41 replay\n\nThe entire inherited design is executed in a fresh directory after correcting the JSON policy restoration bug. The failed R40 artifact is retained. Its partial results and a complete local development replay were observed before this publication run. This is therefore not described as a blinded or independently prospective experiment. The displayed service clocks belong only to this GitHub execution; no inherited clock is replaced.\n')
 provenance=dict(review_commit='c95c0771c468db7d98ee9746a6bf5972de242569',reviewed_manuscript_commit='f472a7c21f2f9db5285f1bf7746edf2d9463638e',development_parent='a4ec3525a7184e2d2fe04953d131fbfd725ac941',publication_source_commit=SRC,run_id=os.environ['GITHUB_RUN_ID'],input_artifacts=inherited,verified_R39_publication_hashes=len(manifest),historical_clock_replacements=0)
 (R/'audit/INPUT_PROVENANCE.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n')
 run('code/tests.py');run('code/deployment.py');run('code/study.py');run('publication/audit_results.py');run('publication/assemble.py');run('publication/build.py')
def publish():
 head=call('GET','/git/ref/heads/'+BRANCH)['object']['sha'];assert head==SRC,'Source branch moved; refusing to overwrite concurrent work'
 parent=call('GET','/git/commits/'+SRC);items=[]
 paths=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[WORK/'ECTA.tex',WORK/'supp.tex',WORK/'README.md']
 for p in sorted(paths):
  b=p.read_bytes();item=dict(path=str(p.relative_to(WORK)),mode='100644',type='blob')
  try:item['content']=b.decode('utf-8')
  except UnicodeDecodeError:
   item['sha']=call('POST','/git/blobs',json=dict(content=base64.b64encode(b).decode(),encoding='base64'))['sha']
  items.append(item)
 tree=call('POST','/git/trees',json=dict(base_tree=parent['tree']['sha'],tree=items))['sha']
 commit=call('POST','/git/commits',json=dict(message='R41: materialize direct-neural Econometrica revision with complete science and four clean PDFs',tree=tree,parents=[SRC]))['sha']
 assert call('GET','/git/ref/heads/'+BRANCH)['object']['sha']==SRC
 call('PATCH','/git/refs/heads/'+BRANCH,json=dict(sha=commit,force=False))
 (WORK/'R41_FINAL_COMMIT.txt').write_text(commit+'\n')
 print('PUBLISHED_R41_COMMIT='+commit,flush=True)
if __name__=='__main__':restore();publish()
