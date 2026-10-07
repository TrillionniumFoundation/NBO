"""Source-pinned R40 scientific execution and append-only scoped publication."""
from __future__ import annotations
import os,sys,json,hashlib,base64,io,zipfile,gzip,subprocess
from pathlib import Path
import requests
REPO='TrillionniumFoundation/NBO';BRANCH='revision/econometrica-nbo-r40-neural-residual-source-2026-10-07'
REL='revisions/2026-10-07-r40';SOURCE=os.environ['GITHUB_SHA']
WORK=Path(os.environ.get('GITHUB_WORKSPACE','.')).resolve()/'work'
API='https://api.github.com/repos/'+REPO
SESSION=requests.Session();SESSION.headers.update({'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
def request(method,path,**kwargs):
 r=SESSION.request(method,API+path,timeout=120,**kwargs)
 if not r.ok:raise RuntimeError(f'GitHub {method} {path}: {r.status_code} {r.text[:400]}')
 return r
def get(path):return request('GET',path).json()
def blobsha(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def source_file(path,ref=SOURCE):
 obj=get('/contents/'+path+'?ref='+ref);data=base64.b64decode(obj['content'])
 if blobsha(data)!=obj['sha']:raise RuntimeError('Source blob mismatch')
 return data
def extract(artifact,expected,destination):
 data=request('GET',f'/actions/artifacts/{artifact}/zip').content
 if hashlib.sha256(data).hexdigest()!=expected:raise RuntimeError('Artifact digest mismatch')
 destination.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(io.BytesIO(data)) as a:
  for item in a.infolist():
   if not (destination/item.filename).resolve().is_relative_to(destination.resolve()):raise RuntimeError('Unsafe ZIP path')
   if ((item.external_attr>>16)&0o170000)==0o120000:raise RuntimeError('ZIP symlink')
  a.extractall(destination)
def restore():
 if os.environ.get('GITHUB_REF_NAME')!=BRANCH:raise RuntimeError('Wrong branch')
 if WORK.exists():raise RuntimeError('Fresh workspace required')
 extract(11454277229,'d295c8593277373b4d016d17cd6268bf960d6e3936ba49c70ec9e1c1f83f1844',WORK)
 extract(11447232117,'e567df2b3ff1efb39139e1ec5c5cfbfcbabac3ebb0f2c889f896c6dc5a0849ad',WORK/'revisions/2026-10-07-r38')
 parts=['science_source.b64']+[f'science_source.part{i}.b64' for i in range(1,4)]
 data=base64.b64decode(b''.join(source_file(REL+'/publication/'+p) for p in parts))
 assert hashlib.sha256(data).hexdigest()=='02b9be056ec2229b4998e29fd76ef6a59026ae3d0a6ae70ea826e974e50457ba','Science transport hash'
 items=json.loads(gzip.decompress(data));ids={}
 for name,text in items.items():
  p=(WORK/REL/name).resolve()
  if not p.is_relative_to((WORK/REL).resolve()):raise RuntimeError('Unsafe source path')
  p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);ids[name]=hashlib.sha256(text.encode()).hexdigest()
 for name in ['STUDY_PROTOCOL.md','publication/science_remote.py']:
  p=WORK/REL/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(source_file(REL+'/'+name))
 report=source_file('reviews/2026-10-07-econometrica-numerical-methods-r39/referee_report.md','review/econometrica-numerical-methods-r39-2026-10-07-f472a7c')
 if blobsha(report)!='1889b7f8afb63b8d8b548f4932368cc44fc22601':raise RuntimeError('Referee report changed')
 p=WORK/REL/'retained/referee_report_R39.md';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(report)
 p=WORK/REL/'audit/SCIENCE_SOURCE.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(dict(commit=SOURCE,run_id=os.environ['GITHUB_RUN_ID'],files=ids),indent=2)+'\n')
 for name in ['seed.py','tests.py','deployment.py','study.py']:
  subprocess.run([sys.executable,str(WORK/REL/'code'/name)],cwd=WORK,check=True)
def publish():
 ref='/git/refs/heads/'+BRANCH
 if get(ref)['object']['sha']!=SOURCE:raise RuntimeError('Branch advanced; refusing overwrite')
 tree0=get('/git/commits/'+SOURCE)['tree']['sha'];entries=[]
 for p in sorted((WORK/REL).rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  data=p.read_bytes();entry=dict(path=str(p.relative_to(WORK)),mode='100644',type='blob')
  try:entry['content']=data.decode('utf-8')
  except UnicodeDecodeError:
   b=request('POST','/git/blobs',json=dict(content=base64.b64encode(data).decode(),encoding='base64')).json();assert b['sha']==blobsha(data);entry['sha']=b['sha']
  entries.append(entry)
 tree=request('POST','/git/trees',json=dict(base_tree=tree0,tree=entries)).json()['sha']
 commit=request('POST','/git/commits',json=dict(message='R40: deposit direct-neural residual chains, nonzero deployment certificates and all native precision stress records',tree=tree,parents=[SOURCE])).json()['sha']
 if get(ref)['object']['sha']!=SOURCE:raise RuntimeError('Publication lease lost')
 request('PATCH',ref,json=dict(sha=commit,force=False));assert get(ref)['object']['sha']==commit
 (WORK/'R40_SCIENCE_COMMIT.txt').write_text(commit+'\n');print(json.dumps(dict(science_commit=commit,tree=tree,files=len(entries))))
if __name__=='__main__':restore();publish()
