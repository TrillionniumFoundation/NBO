"""Restore pinned inputs, build R39, and publish only the new revision scope.

No repository checkout, old-source replacement, experiment rerun, force push,
or credential logging is performed. The branch-head lease must still match.
"""
from __future__ import annotations
import os,sys,json,hashlib,base64,io,zipfile,subprocess,time
from pathlib import Path
import requests
REPO='TrillionniumFoundation/NBO'
BRANCH='revision/econometrica-nbo-r39-integrated-source-2026-10-07'
REL='revisions/2026-10-07-r39'
SOURCE=os.environ['GITHUB_SHA']
WORK=Path(os.environ.get('GITHUB_WORKSPACE','.')).resolve()/'work'
API='https://api.github.com/repos/'+REPO
SESSION=requests.Session()
SESSION.headers.update(Authorization='Bearer '+os.environ['GITHUB_TOKEN'],Accept='application/vnd.github+json','X-GitHub-Api-Version'='2022-11-28')

def request(method,path,**kwargs):
    response=SESSION.request(method,API+path,timeout=120,**kwargs)
    if not response.ok:
        raise RuntimeError(f'GitHub {method} {path}: {response.status_code} {response.text[:1000]}')
    return response

def get(path):return request('GET',path).json()
def blobsha(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def source_file(path,ref=SOURCE):
    obj=get('/contents/'+path+'?ref='+ref)
    if obj.get('encoding')!='base64':raise RuntimeError('Unexpected file encoding '+path)
    data=base64.b64decode(obj['content'])
    if blobsha(data)!=obj['sha']:raise RuntimeError('Blob mismatch '+path)
    return data

def extract(artifact,expected,destination):
    data=request('GET',f'/actions/artifacts/{artifact}/zip').content
    if hashlib.sha256(data).hexdigest()!=expected:raise RuntimeError('Artifact digest mismatch')
    destination.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for item in archive.infolist():
            target=(destination/item.filename).resolve()
            if not target.is_relative_to(destination.resolve()):raise RuntimeError('Unsafe archive path')
            if ((item.external_attr>>16)&0o170000)==0o120000:raise RuntimeError('Archive symlink')
        archive.extractall(destination)

def restore():
    if os.environ.get('GITHUB_REF_NAME')!=BRANCH:raise RuntimeError('Wrong publication branch')
    if WORK.exists():raise RuntimeError('Work directory must be new')
    extract(11444691409,'3db88811f582bd073de7be9f85fab8dd8468978c5a559815763965acc104baf6',WORK)
    extract(11447232117,'e567df2b3ff1efb39139e1ec5c5cfbfcbabac3ebb0f2c889f896c6dc5a0849ad',WORK/'revisions/2026-10-07-r38')
    names=['manuscript/nonlinear_theory.tex','manuscript/finite_precision.tex',
           'manuscript/evidence_new.tex','references_new.bib','response.md',
           'code/audit.py','publication/publish.py','publication/remote.py']
    identities={}
    for name in names:
        data=source_file(REL+'/'+name);p=WORK/REL/name
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        identities[name]=dict(git_blob=blobsha(data),sha256=hashlib.sha256(data).hexdigest())
    report=source_file('reviews/2026-10-07-econometrica-numerical-methods-r37/referee_report.md','71949aa40c62c960dab824137bed12bb3516ff85')
    assert blobsha(report)=='642fbb72536aa61aad70e360a1ca14d96d3357a9'
    p=WORK/REL/'retained/review/referee_report.md';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(report)
    p=WORK/REL/'audit/PUBLICATION_SOURCE.json';p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(dict(commit=SOURCE,files=identities,run_id=os.environ['GITHUB_RUN_ID']),indent=2,sort_keys=True)+'\n')
    subprocess.run([sys.executable,str(WORK/REL/'publication/publish.py'),'all'],cwd=WORK,check=True)

def publish():
    if os.environ.get('GITHUB_REF_NAME')!=BRANCH:raise RuntimeError('Wrong publication branch')
    ref='/git/refs/heads/'+BRANCH
    if get(ref)['object']['sha']!=SOURCE:raise RuntimeError('Publication branch advanced; refusing overwrite')
    base=get('/git/commits/'+SOURCE)['tree']['sha']
    paths=sorted(p for p in (WORK/REL).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths += [WORK/'ECTA.tex',WORK/'supp.tex',WORK/'README.md']
    entries=[]
    for p in paths:
        name=str(p.relative_to(WORK));data=p.read_bytes()
        if not (name.startswith(REL+'/') or name in ('ECTA.tex','supp.tex','README.md')):
            raise RuntimeError('Write outside revision scope')
        entry=dict(path=name,mode='100644',type='blob')
        try:entry['content']=data.decode('utf-8')
        except UnicodeDecodeError:
            obj=request('POST','/git/blobs',json=dict(content=base64.b64encode(data).decode(),encoding='base64')).json()
            assert obj['sha']==blobsha(data);entry['sha']=obj['sha']
        entries.append(entry)
    tree=request('POST','/git/trees',json=dict(base_tree=base,tree=entries)).json()['sha']
    commit=request('POST','/git/commits',json=dict(message='R39: publish integrated Econometrica manuscript, complete evidence audit and native PDFs',tree=tree,parents=[SOURCE])).json()['sha']
    if get(ref)['object']['sha']!=SOURCE:raise RuntimeError('Publication lease lost; commit left unattached')
    request('PATCH',ref,json=dict(sha=commit,force=False))
    assert get(ref)['object']['sha']==commit
    (WORK/'REMOTE_COMMIT.txt').write_text(commit+'\n')
    print(json.dumps(dict(publication_commit=commit,publication_tree=tree,files=len(entries),branch=BRANCH)))

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'all'
    if mode in ('all','restore'):restore()
    if mode in ('all','publish'):publish()
