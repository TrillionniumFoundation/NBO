"""Materialize the immutable R27 source; execute once; retain every outcome.

Uses authenticated repository API reads instead of cloning all historical
candidate arrays. Only the new R27 subtree is published; old records stay intact.
"""
from pathlib import Path
import base64
import hashlib
import json
import lzma
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT=Path(os.environ['GITHUB_WORKSPACE'])
PREFIX='revisions/2026-10-06-r27'
R=ROOT/PREFIX
REPO='TrillionniumFoundation/NBO'
BRANCH='revision/econometrica-nbo-r27-2026-10-06'
SOURCE=os.environ['GITHUB_SHA']
BASE='f5a54d5a04fd2851cc096ab4cd75106ea4d8fda2'
PAYLOAD_SHA='7f3e6672429dff963639fc3e9d9360148de551243d3bcf6e1f064c4766377f29'
TOKEN=os.environ['GH_TOKEN']
API='https://api.github.com/repos/'+REPO
DEPENDENCIES={
 'revisions/2026-10-05-r23/code/policy_certificate.py':'f9372adc31ab629ae36e3da9621f531f02da41a9',
 'revisions/2026-10-05-r23/code/experiment.py':'cf0aba47af5b5ca745f8adb67cd306db17402b09',
 'revisions/2026-10-05-r25/code/constructive.py':'3924203b852acba3cc2cbcc835365090730efb1a'}


def api(path,method='GET',data=None):
    body=None if data is None else json.dumps(data).encode()
    req=urllib.request.Request(API+path,data=body,method=method,
        headers={'Authorization':'Bearer '+TOKEN,'Accept':'application/vnd.github+json',
                 'X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req,timeout=120) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429,500,502,503,504) or attempt==5:raise
            time.sleep(min(60,2**attempt))
        except (TimeoutError,urllib.error.URLError):
            if attempt==5:raise
            time.sleep(min(60,2**attempt))


def fetch(path,ref):
    item=api('/contents/'+urllib.parse.quote(path,safe='/')+'?ref='+ref)
    data=base64.b64decode(item['content'])
    gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert gitsha==item['sha'],path
    return data,gitsha


def materialize():
    chunks=[fetch(PREFIX+f'/delivery/frozen_source.part{i:02d}.b64',SOURCE)[0].decode().strip() for i in range(4)]
    packed=base64.b64decode(''.join(chunks),validate=True)
    assert hashlib.sha256(packed).hexdigest()==PAYLOAD_SHA,'Frozen payload integrity mismatch'
    files=json.loads(lzma.decompress(packed))
    for name,text in files.items():
        p=(ROOT/name).resolve()
        assert p.is_relative_to((ROOT/PREFIX).resolve()) and '..' not in Path(name).parts,name
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8')
    for name,expected in DEPENDENCIES.items():
        data,sha=fetch(name,BASE);assert sha==expected,name
        p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    (R/'results').mkdir(exist_ok=True)
    record=dict(source_commit=SOURCE,review_commit='281e57b18a2d88de68d2219da1a7194e90570d13',
        inherited_base=BASE,payload_sha256=PAYLOAD_SHA,inherited_blobs=DEPENDENCIES,
        files={n:hashlib.sha256(t.encode()).hexdigest() for n,t in files.items()},
        primary_started=False)
    (R/'protocols/SOURCE_IDENTITY.json').write_text(json.dumps(record,indent=2)+'\n')


def command(args,name):
    with (R/'results'/name).open('w') as log:
        proc=subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
    print((R/'results'/name).read_text(errors='replace')[-12000:],flush=True)
    if proc.returncode:raise RuntimeError(name+' failed')


def publish():
    current=api('/git/ref/heads/'+BRANCH)['object']['sha']
    if current!=SOURCE:
        raise RuntimeError('Branch moved during execution; artifact preserved, no overwrite attempted')
    base_tree=api('/git/commits/'+current)['tree']['sha']
    elements=[]
    for p in sorted(R.rglob('*')):
        if not p.is_file() or '__pycache__' in str(p) or '/delivery/' in str(p):continue
        name=str(p.relative_to(ROOT));data=p.read_bytes()
        element=dict(path=name,mode='100644',type='blob')
        if p.suffix=='.npz':
            element['sha']=api('/git/blobs','POST',{'encoding':'base64','content':base64.b64encode(data).decode()})['sha']
        else:element['content']=data.decode('utf8')
        elements.append(element)
    tree=api('/git/trees','POST',{'base_tree':base_tree,'tree':elements})['sha']
    commit=api('/git/commits','POST',{'message':'R27: publish frozen primitive-budget and recursive-risk executions with all outcomes',
                                   'tree':tree,'parents':[current]})['sha']
    api('/git/refs/heads/'+BRANCH,'PATCH',{'sha':commit,'force':False})
    (R/'results/REMOTE_COMMIT.json').write_text(json.dumps({'commit':commit,'branch':BRANCH,'source_commit':SOURCE},indent=2)+'\n')
    print('REMOTE_EXECUTION_COMMIT',commit,flush=True)


def archive():
    files=[p for p in ROOT.rglob('*') if p.is_file() and p.is_relative_to(ROOT/'revisions') and '__pycache__' not in str(p)]
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    out=ROOT/'R27_EXECUTION_SHA256.json';out.write_text(json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile('/tmp/NBO_R27_execution.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,str(p.relative_to(ROOT)))
        z.write(out,out.name)


if __name__=='__main__':
    materialize()
    try:
        command([sys.executable,'-m','unittest','discover','-s',str(R/'code'),'-p','test*.py','-v'],'TESTS_R27.log')
        command([sys.executable,str(R/'code/execute.py')],'PRIMARY_RUN.log')
        command([sys.executable,str(R/'code/report.py')],'REPORT.log')
        publish()
    finally:archive()
