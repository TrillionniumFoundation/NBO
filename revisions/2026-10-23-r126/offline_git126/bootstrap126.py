#!/usr/bin/env python3
"""Install immutable F126 identity objects without changing existing Git state.
This is a minimal path witness, not a complete repository clone. No network,
checkout, reset, ref update, index write, hook execution or economic calculation.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,datetime,time
F126='769e3eb3ac08beaa7bb6778c1676f15e1f8d6d2b'
HERE=Path(__file__).resolve().parent

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    started=time.perf_counter()
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repository-root',type=Path,default=HERE.parents[2])
    args=ap.parse_args();root=args.repository_root.resolve()
    if not root.is_dir():raise RuntimeError('Repository-layout directory does not exist')
    env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_TERMINAL_PROMPT='0',GIT_NO_LAZY_FETCH='1')
    def git(*a,input=None,check=True):
        p=subprocess.run(['git','-c','protocol.allow=never','-C',str(root),*a],input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
        if check and p.returncode:raise RuntimeError('Git operation failed: '+repr(a)+'; '+p.stderr.decode(errors='replace'))
        return p
    def gitpath(name):
        p=Path(git('rev-parse','--git-path',name).stdout.decode().strip());return p if p.is_absolute() else root/p
    def fileidentity(p):
        return {'exists':p.exists(),'sha256':sha(p.read_bytes()) if p.exists() else None}
    def state():
        return {'refs_sha256':sha(git('for-each-ref','--format=%(refname) %(objectname) %(symref)').stdout),
                'head':fileidentity(gitpath('HEAD')),'index':fileidentity(gitpath('index'))}
    manifest_path=HERE/'WITNESS_MANIFEST126.json';m=json.loads(manifest_path.read_text())
    if m['source_commit']!=F126 or m['gate_file_count']!=184 or len(m['gate_files'])!=184:raise RuntimeError('Unexpected witness identity or gate count')
    packname=Path(m['pack']['path'])
    if packname.name!=str(packname):raise RuntimeError('Invalid pack path')
    pack=HERE/packname;packraw=pack.read_bytes()
    if len(packraw)!=m['pack']['bytes'] or sha(packraw)!=m['pack']['sha256']:raise RuntimeError('Pack checksum mismatch')
    seen=set()
    for row in m['gate_files']:
        p=Path(row['path'])
        if p.is_absolute() or '..' in p.parts or p.as_posix() in seen:raise RuntimeError('Unsafe or duplicate gate path')
        seen.add(p.as_posix())
        resolved=(root/p).resolve()
        if root not in resolved.parents:raise RuntimeError('Gate path escapes repository')
        raw=resolved.read_bytes()
        if len(raw)!=row['bytes'] or sha(raw)!=row['sha256']:raise RuntimeError('Working-file mismatch: '+p.as_posix())
    before_probe=git('rev-parse','--show-toplevel',check=False)
    created=False
    if (root/'.git').exists():
        if before_probe.returncode or Path(before_probe.stdout.decode().strip()).resolve()!=root:raise RuntimeError('Existing Git identity is not the requested repository root')
    else:
        if before_probe.returncode==0:raise RuntimeError('Target is already inside a different repository; choose a separate archive root')
        git('init','--quiet','--template=','--initial-branch=offline-f126','--object-format=sha1')
        created=True
    if git('rev-parse','--show-object-format').stdout.strip()!=b'sha1':raise RuntimeError('The authentic F126 witness requires a SHA-1 Git object repository')
    before=state()
    installed=git('index-pack','--stdin','--keep=R126 minimal immutable identity witness',input=packraw).stdout.decode().strip()
    for obj in m['objects']:
        typ=git('cat-file','-t',obj['oid']).stdout.decode().strip()
        if typ!=obj['type']:raise RuntimeError('Git object type mismatch')
        raw=git('cat-file',typ,obj['oid']).stdout
        if len(raw)!=obj['bytes'] or sha(raw)!=obj['payload_sha256'] or hashlib.sha1((typ+' '+str(len(raw))+'\0').encode()+raw).hexdigest()!=obj['oid']:raise RuntimeError('Git object identity mismatch')
    checked=[]
    for row in m['gate_files']:
        raw=git('show',F126+':'+row['path']).stdout
        current=(root/row['path']).read_bytes()
        if raw!=current or len(raw)!=row['bytes'] or sha(raw)!=row['sha256']:raise RuntimeError('Frozen source readback mismatch: '+row['path'])
        checked.append({'path':row['path'],'sha256':sha(raw),'git_blob':row['git_blob']})
    after=state()
    if before!=after:raise RuntimeError('Git refs, HEAD or worktree index unexpectedly changed')
    print(json.dumps({'schema':'r126-offline-witness-bootstrap-receipt-v1','source_commit':F126,'created_repository_identity':created,
      'repository_root':str(root),'network_used':False,'economic_evaluations':0,'fits':0,'objects_verified':len(m['objects']),
      'git_show_files_verified':len(checked),'verified_files':checked,'pack_sha256':sha(packraw),'manifest_sha256':sha(manifest_path.read_bytes()),
      'existing_refs_HEAD_and_worktree_index_unchanged':True,'git_state_before':before,'git_state_after':after,
      'pack_index_receipt':installed,'seconds':time.perf_counter()-started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2,sort_keys=True))
if __name__=='__main__':main()
