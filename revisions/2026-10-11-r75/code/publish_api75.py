"""Persist exact R75 Git objects with non-forced, checked branch updates.

Used on the authorized Actions runner. Token contents are never printed.
Only the new revision subtree and root reading guide may be changed.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,base64,json,os,subprocess,time,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[3]
REPO='TrillionniumFoundation/NBO';PREFIX='revisions/2026-10-11-r75/'
API='https://api.github.com/repos/'+REPO

def git(*args,raw=False):
    data=subprocess.check_output(['git',*args],cwd=ROOT)
    return data if raw else data.decode().strip()

def request(method,path,data=None,allow404=False):
    token=os.environ.get('GITHUB_TOKEN')
    if not token:raise RuntimeError('Authorized Actions token required')
    body=None if data is None else json.dumps(data).encode()
    headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'NBO-R75-publication','Content-Type':'application/json'}
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(API+path,data=body,headers=headers,method=method),timeout=90) as response:return json.load(response)
        except urllib.error.HTTPError as exc:
            if allow404 and exc.code==404:return None
            detail=exc.read().decode(errors='replace')
            if exc.code in (429,500,502,503,504) or (exc.code==403 and 'rate limit' in detail.lower()):
                if attempt<4:time.sleep(2**attempt);continue
            raise RuntimeError('Git API '+method+' '+path+' failed '+str(exc.code)+': '+detail[:800]) from None
    raise RuntimeError('API retries exhausted')

def persist(sha):
    if request('GET','/git/commits/'+sha,allow404=True) is not None:return sha
    parents=git('rev-list','--parents','-n','1',sha).split()[1:]
    if len(parents)!=1:raise AssertionError('Only a single-parent revision commit is permitted')
    parent=parents[0];persist(parent)
    changes=git('diff-tree','--no-commit-id','--name-only','-r',parent,sha).splitlines()
    if any(not (p.startswith(PREFIX) or p=='README.md') for p in changes):raise AssertionError('Change outside R75 scope')
    entries=[];blobs={}
    for path in changes:
        info=git('ls-tree',sha,'--',path)
        if not info:
            entries.append({'path':path,'mode':'100644','type':'blob','sha':None});continue
        meta,name=info.split('\t',1);mode,kind,digest=meta.split()
        if kind!='blob' or mode not in ('100644','100755'):raise AssertionError('Unsupported entry '+path)
        if Path(path).suffix.lower() in ('.ttf','.otf','.pfb','.pfa','.woff','.woff2','.afm','.tfm'):raise AssertionError('Standalone font file')
        entries.append({'path':path,'mode':mode,'type':'blob','sha':digest})
        blobs[digest]=path
    def upload(item):
        digest,path=item;raw=git('show',sha+':'+path,raw=True)
        actual=request('POST','/git/blobs',{'content':base64.b64encode(raw).decode(),'encoding':'base64'})['sha']
        if actual!=digest:raise AssertionError('Remote blob identity mismatch '+path)
    with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(upload,blobs.items()))
    tree=request('POST','/git/trees',{'base_tree':git('rev-parse',parent+'^{tree}'),'tree':entries})['sha']
    if tree!=git('rev-parse',sha+'^{tree}'):raise AssertionError('Remote tree differs from tested tree')
    fields=git('show','-s','--format=%an%n%ae%n%aI%n%cn%n%ce%n%cI',sha).splitlines()
    raw=git('cat-file','commit',sha,raw=True);message=raw.split(b'\n\n',1)[1].decode()
    data={'tree':tree,'parents':[parent],'author':{'name':fields[0],'email':fields[1],'date':fields[2]},'committer':{'name':fields[3],'email':fields[4],'date':fields[5]}}
    for m in (message,message.rstrip('\n')):
        made=request('POST','/git/commits',{**data,'message':m})['sha']
        if made==sha:
            print('Exact remote commit persisted',sha,'changed files',len(entries),flush=True);return sha
    raise AssertionError('Remote commit metadata differs from the tested local commit')

def move(branch,sha,expected=None):
    path='/git/ref/heads/'+branch;current=request('GET',path,allow404=True)
    if current is None:
        if expected is not None:raise AssertionError('Expected existing branch absent')
        request('POST','/git/refs',{'ref':'refs/heads/'+branch,'sha':sha})
    else:
        old=current['object']['sha']
        if old==sha:return
        if expected is not None and old!=expected:raise AssertionError('Branch advanced concurrently; refusing overwrite')
        request('PATCH','/git/refs/heads/'+branch,{'sha':sha,'force':False})
    check=request('GET',path)
    if check['object']['sha']!=sha:raise AssertionError('Remote ref verification failed')
    print('Verified non-forced ref',branch,sha,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--branch');p.add_argument('--expected');p.add_argument('--sha',default='HEAD');a=p.parse_args();sha=git('rev-parse',a.sha);persist(sha)
    if a.branch:move(a.branch,sha,a.expected)
