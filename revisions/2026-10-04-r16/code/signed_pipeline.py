"""R16 prospective signed Bellman signed: immutable inputs and complete evidence.

The numerical source is frozen before any new confirmation bank is evaluated.
Every selected R15 NBO policy is retained. Workers receive only a verified small
source/weight bundle and execute in fresh processes; no historical raw dataset
is copied into their bundle. Old training work is not charged as new work.
"""
from __future__ import annotations
import argparse
import ast
import datetime as dt
import gzip
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

R16 = Path('revisions/2026-10-04-r16')
PROTOCOL = R16/'protocols/signed_mechanism.json'
CANDIDATES = R16/'protocols/signed_candidates.json'
CONSTANTS = R16/'protocols/signed_constants.json'
PIPELINE = R16/'code/signed_pipeline.py'
WORKER = R16/'code/signed_worker.py'
REPORT = R16/'code/signed_report.py'
TESTS = R16/'code/signed_tests.py'
WORKFLOW = Path('.github/workflows/nbo-r16-signed-mechanism.yml')
BASE = 'cb4595bbcc7147e47e44ba40cb2f5034510ae19f'
CANDIDATE_SOURCE = '9142f404bb9c5163aa94d3a4ded4d0fa48a49c50'
CANDIDATE_EVIDENCE = 'b08347444e3001725d7fea33ff0bfce9c7e95e37'
METHODS = ['nbo']
PACKAGES = {'numpy':'2.3.5','scipy':'1.17.0','numba':'0.65.1',
            'mpmath':'1.3.0','torch':'2.10.0+cpu'}
ARTIFACT_PAYLOAD_LIMIT = 24*1024*1024

def require(ok, message):
    if not ok: raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',',':'), allow_nan=False).encode()

def digest(data): return hashlib.sha256(data).hexdigest()

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def read(path): return json.loads(Path(path).read_text())

def write(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')

def git(repo,*args): return subprocess.check_output(['git','-C',str(repo),*args])

def safe(root,name):
    p=PurePosixPath(str(name))
    require(not p.is_absolute() and '..' not in p.parts and str(p)!='.','unsafe relative path')
    result=Path(root)/Path(*p.parts)
    require(result.resolve().is_relative_to(Path(root).resolve()),'path outside root')
    return result

def git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def tree(repo,commit):
    require(bool(re.fullmatch('[0-9a-f]{40}',commit or '')),'full source SHA required')
    answer={}
    for entry in git(repo,'ls-tree','-rz','--full-tree',commit).split(b'\0'):
        if entry:
            meta,name=entry.split(b'\t',1);mode,kind,oid=meta.split()
            if kind==b'blob': answer[name.decode()]={'mode':mode.decode(),'git_blob':oid.decode()}
    return answer

def bank(protocol,d,seed,*,development=False):
    namespace=('NBO-R16-development-only-v1' if development else protocol['confirmation']['bank_namespace'])
    key=f'{namespace}/d{d}/s{seed}/confirmation'
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],'big'),key

def trials(protocol):
    answer=[]
    for di,d in enumerate(protocol['design']['dimensions']):
        for si,seed in enumerate(protocol['design']['seeds']):
            offset=(di+si)%len(METHODS);noise,key=bank(protocol,d,seed)
            answer.append(dict(trial_id=f'd{d}_s{seed}',dimension=d,stream_seed=seed,
                               noise_seed=noise,noise_key=key,method_order=METHODS[offset:]+METHODS[:offset]))
    return answer

def validate_protocol(p,candidates):
    require(p['status']=='frozen_before_confirmatory_execution','signed design is not frozen')
    require(p['family']=='fresh_signed_mechanism' and p['protocol_version']==1,'unknown family')
    require(p['reviewed_parent_commit']==BASE,'incorrect reviewed source parent')
    require(p['candidate_source_commit']==CANDIDATE_SOURCE and p['candidate_evidence_commit']==CANDIDATE_EVIDENCE,'candidate source/evidence roles changed')
    require(p['design']['dimensions']==[10,50] and p['design']['methods']==METHODS,'complete dimensions/methods required')
    seeds=p['design']['seeds'];require(len(seeds)==len(set(seeds))==16,'all sixteen original streams required')
    conf=p['confirmation'];require(conf['paths_per_seed']==1024 and conf['steps']==2048,'fresh-bank precision changed')
    require(conf['antithetic_pairs']==2 and conf['future_paths_per_bridge']==4 and conf['batch_size']==128,'future bank or fixed batching changed')
    require(conf['training_runs']==0 and conf['policy_executions']==32 and conf['bank_count']==32,'signed assessment is not retraining')
    require(conf['attempts_per_trial']==1,'confirmation attempts changed')
    require(p['inference']['family_alpha']==.01 and p['inference']['event_count']==6 and p['inference']['historical_alpha_reused'] is False,'independent R16 error budget changed')
    require(p['inference']['statistics']==['M','C','G'],'all declared signed statements required')
    require(p['economic_decision']['gain_target']==.0005,'economic gain target changed')
    require(digest(canonical(p['design']['primitives']))==p['design']['primitives_sha256'],'economic primitive identity differs')
    rows=candidates['files'];expected={(d,s,m) for d in [10,50] for s in seeds for m in METHODS}
    require(len(rows)==32 and {(r['dimension'],r['stream_seed'],r['method_id']) for r in rows}==expected,'missing or repeated original NBO policy')
    old={r['original_confirmation_noise_seed'] for r in rows}
    old.update(s for r in rows for s in r['original_online_noise_seeds'])
    old.update(s for r in rows for s in r['original_mechanism_noise_seeds'].values())
    new=[t['noise_seed'] for t in trials(p)]
    require(len(set(new))==32 and not set(new)&old,'bank seed reused or duplicated')
    purposes=['initial_profile','uniform_node','occupation_innovations']+[f'future_batch_{i}_pair_{j}' for i in range(8) for j in range(2)]
    derived=[int.from_bytes(hashlib.sha256(f'NBO-R16-signed-purpose-v1/{seed}/{purpose}'.encode()).digest()[:8],'big') for seed in new for purpose in purposes]
    require(len(set(derived))==len(derived) and not set(derived)&old and not set(derived)&set(new),'derived occupation/future seed reused or duplicated')
    require(not set(new)&{bank(p,d,s,development=True)[0] for d,s,_ in expected},'development bank collides with confirmation')
    for row in rows:
        require(row['candidate_source_commit']==CANDIDATE_SOURCE and row['candidate_evidence_commit']==CANDIDATE_EVIDENCE,'mixed original candidate identities')
        require(row['candidate_protocol_sha256']==p['candidate_protocol_sha256'] and row['primitives_sha256']==p['design']['primitives_sha256'],'candidate contract mismatch')
    return expected

def source_files(repo):
    p=read(Path(repo)/PROTOCOL);c=read(Path(repo)/CANDIDATES)
    own=[PROTOCOL,CANDIDATES,CONSTANTS,R16/'protocols/signed_power.json',PIPELINE,WORKER,REPORT,TESTS,WORKFLOW,Path(p['source_contract']['development_manifest'])]
    return sorted({str(x) for x in own}|set(p['source_contract']['inherited_files'])|
                  set(p['source_contract']['mathematical_sources'])|{r['path'] for r in c['files']})

def check(repo):
    repo=Path(repo).resolve();p=read(repo/PROTOCOL);c=read(repo/CANDIDATES)
    validate_protocol(p,c)
    family=read(safe(repo,p['confidence_families']))
    require(family['allocations']['signed_mechanism']==p['inference']['family_alpha'] and sum(family['allocations'].values())<=family['alpha_total'],'signed family exceeds the predeclared R16 union budget')
    require(sha(safe(repo,p['source_contract']['development_manifest']))==p['source_contract']['development_manifest_sha256'],'development archive binding changed')
    require(sha(repo/CANDIDATES)==p['candidate_inventory_sha256'],'frozen candidate inventory changed')
    require(sha(repo/CONSTANTS)==p['signed_constants_sha256'],'paired deterministic constants changed')
    require(sha(safe(repo,p['candidate_protocol']))==p['candidate_protocol_sha256'],'original protocol changed')
    for name,facts in p['source_contract']['inherited_files'].items():
        path=safe(repo,name);data=path.read_bytes()
        require(digest(data)==facts['sha256'] and git_blob(data)==facts['git_blob'],'historical numerical source changed: '+name)
    for name,expected in p['source_contract']['mathematical_sources'].items():
        require(sha(safe(repo,name))==expected,'paired theorem/implementation changed: '+name)
    for r in c['files']:
        path=safe(repo,r['path']);data=path.read_bytes()
        require(len(data)==r['bytes'] and digest(data)==r['sha256'] and git_blob(data)==r['git_blob'],'original selected weights changed: '+r['path'])
    for name in source_files(repo):
        path=safe(repo,name);require(path.is_file() and not path.is_symlink(),'missing source dependency')
        if name.endswith('.py'): ast.parse(path.read_text(),filename=name)
    return dict(complete=True,policy_count=32,bank_count=32,events=6,
                operation='Deterministic source, mathematical-account and candidate-identity check; no new bank sampled')

def pack(repo,out,source):
    repo=Path(repo).resolve();out=Path(out).resolve()
    require(git(repo,'rev-parse','HEAD').decode().strip()==source,'checkout is not execution source')
    git(repo,'merge-base','--is-ancestor',BASE,source)
    require(os.environ.get('GITHUB_RUN_ATTEMPT','1')=='1','second workflow attempt is inadmissible')
    if os.environ.get('GITHUB_SHA'): require(os.environ['GITHUB_SHA']==source,'workflow source mismatch')
    check(repo);committed=tree(repo,source);payload={};inventory={}
    for name in source_files(repo):
        data=safe(repo,name).read_bytes()
        require(name in committed and git_blob(data)==committed[name]['git_blob'],'uncommitted execution dependency: '+name)
        payload[name]=data;inventory[name]=dict(sha256=digest(data),bytes=len(data),git_blob=git_blob(data))
    require(not out.exists() or not any(out.iterdir()),'source package must be new')
    out.mkdir(parents=True,exist_ok=True);archive=out/'source.tar.gz'
    with archive.open('wb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as zipped:
            with tarfile.open(fileobj=zipped,mode='w',format=tarfile.PAX_FORMAT) as tar:
                for name,data in payload.items():
                    info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0
                    info.uid=info.gid=0;info.uname=info.gname='';tar.addfile(info,io.BytesIO(data))
    p=read(repo/PROTOCOL)
    contract=dict(python='3.12',packages=PACKAGES,platform='Linux',numeric_threads=1,torch_device='cpu',
                  process_scope='fresh process and empty JIT cache per policy; no training')
    fingerprint_input=dict(protocol_sha256=inventory[str(PROTOCOL)]['sha256'],
        files={n:f['sha256'] for n,f in inventory.items()},environment_contract=contract)
    manifest=dict(record_type='R16 immutable prospective-signed source package',numerical_source_commit=source,
        candidate_source_commit=CANDIDATE_SOURCE,candidate_evidence_commit=CANDIDATE_EVIDENCE,reviewed_parent_commit=BASE,
        protocol_sha256=inventory[str(PROTOCOL)]['sha256'],candidate_inventory_sha256=inventory[str(CANDIDATES)]['sha256'],
        signed_constants_sha256=inventory[str(CONSTANTS)]['sha256'],files=inventory,
        assessment_fingerprint=digest(canonical(fingerprint_input)),fingerprint_input=fingerprint_input,
        environment_contract=contract,matrix={'include':trials(p)},archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        github_run_id=os.environ.get('GITHUB_RUN_ID'),github_run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT','1'),
        scope='R15 policies and fitting are fixed conditioning information; only independent R16 signed Bellman assessment is executed.')
    write(out/'SOURCE_MANIFEST.json',manifest);(out/'signed_pipeline.py').write_bytes(payload[str(PIPELINE)])
    bounded(out)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('matrix='+canonical({'include':[{'trial_id':t['trial_id']} for t in manifest['matrix']['include']]}).decode()+'\n')
    return dict(complete=True,source=source,source_files=len(inventory),archive_bytes=archive.stat().st_size,bank_count=32)

def extract(bundle,workspace):
    bundle=Path(bundle).resolve();workspace=Path(workspace).resolve();m=read(bundle/'SOURCE_MANIFEST.json')
    require(sha(__file__)==m['files'][str(PIPELINE)]['sha256'],'unbound signed launcher')
    require(sha(bundle/'source.tar.gz')==m['archive_sha256'],'source archive changed')
    require(digest(canonical(m['fingerprint_input']))==m['assessment_fingerprint'],'assessment fingerprint changed')
    require(not workspace.exists() or not any(workspace.iterdir()),'worker workspace must be empty')
    workspace.mkdir(parents=True,exist_ok=True);seen=set()
    with tarfile.open(bundle/'source.tar.gz','r:gz') as tar:
        for member in tar:
            name=member.name
            require(member.isfile() and name in m['files'] and name not in seen,'unlisted/repeated source member')
            path=safe(workspace,name);data=tar.extractfile(member).read()
            require(len(data)==m['files'][name]['bytes'] and digest(data)==m['files'][name]['sha256'],'source member hash mismatch')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);seen.add(name)
    require(seen==set(m['files']),'incomplete dependency archive');check(workspace)
    p=read(workspace/PROTOCOL)
    require(sha(workspace/PROTOCOL)==m['protocol_sha256'] and m['matrix']=={'include':trials(p)},'protocol/matrix mismatch')
    return m,p

def environment():
    actual={n:importlib.metadata.version(n) for n in PACKAGES}
    require(actual==PACKAGES,'unexpected numerical package versions')
    require(sys.version_info[:2]==(3,12) and platform.system()=='Linux','Python 3.12/Linux required')
    cpu=None
    if Path('/proc/cpuinfo').exists():
        cpu=next((x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),None)
    return dict(python=sys.version,packages=actual,platform=platform.platform(),cpu=cpu,threads=1)

def inventory(folder,exclude=()):
    folder=Path(folder);answer={}
    for path in sorted(folder.rglob('*')):
        if path.is_file():
            require(not path.is_symlink(),'output symlink not permitted')
            name=path.relative_to(folder).as_posix()
            if name not in exclude: answer[name]=sha(path)
    return answer

def bounded(folder):
    folder=Path(folder);files=[p for p in folder.rglob('*') if p.is_file()]
    total=sum(p.stat().st_size for p in files)
    require(total<=ARTIFACT_PAYLOAD_LIMIT,'artifact exceeds safe 24 MiB payload; retain failure, never omit files')
    require(len(files)<10000,'excessive ZIP metadata')
    return dict(files=len(files),uncompressed_bytes=total,limit=ARTIFACT_PAYLOAD_LIMIT,
                scope='At most 24 MiB uncompressed payload, leaving ample ZIP metadata overhead below the 32 MiB retrieval limit.')

def execute_child(workspace,out,manifest,trial,method):
    workspace=Path(workspace);out=Path(out);require(not out.exists(),'refusing repeated policy execution');out.mkdir(parents=True)
    actual=environment();env=dict(os.environ);env.pop('NBO_R16_SIGNED_DEVELOPMENT',None)
    env.update(NBO_R16_SIGNED_SOURCE_COMMIT=manifest['numerical_source_commit'],
        NBO_R16_SIGNED_FINGERPRINT=manifest['assessment_fingerprint'],
        PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',NUMBA_NUM_THREADS='1')
    work=dict(record_type='R16 additional independent confirmation process work',complete=False,method_id=method,
        trial_id=trial['trial_id'],dimension=trial['dimension'],stream_seed=trial['stream_seed'],
        numerical_source_commit=manifest['numerical_source_commit'],candidate_source_commit=CANDIDATE_SOURCE,
        candidate_evidence_commit=CANDIDATE_EVIDENCE,protocol_sha256=manifest['protocol_sha256'],
        assessment_fingerprint=manifest['assessment_fingerprint'],environment=actual,environment_fingerprint=digest(canonical(actual)),
        started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        timing_scope='Fresh process launch through exit, including imports, original weight reload, constants, independent confirmation and durable result I/O.',
        provisioning_scope='Dependency installation and verified source extraction precede this additional assessment clock; historical training/stopping costs remain unchanged.')
    command=[sys.executable,str(workspace/WORKER),'--protocol',str(workspace/PROTOCOL),'--trial-id',trial['trial_id'],
             '--method-id',method,'--out',str(out)]
    with tempfile.TemporaryDirectory(prefix='nbo-r16-signed-numba-') as cache:
        env['NUMBA_CACHE_DIR']=cache
        with (out/'process.log').open('wb') as log:
            start=time.perf_counter_ns();child=subprocess.Popen(command,cwd=workspace,env=env,stdout=log,stderr=subprocess.STDOUT)
            _,status,usage=os.wait4(child.pid,0);finish=time.perf_counter_ns();child.returncode=os.waitstatus_to_exitcode(status)
        work.update(end_to_end_seconds=(finish-start)/1e9,returncode=child.returncode,peak_rss_kib=int(usage.ru_maxrss),
                    user_cpu_seconds=usage.ru_utime,system_cpu_seconds=usage.ru_stime,cpu_seconds=usage.ru_utime+usage.ru_stime)
    try:
        require(child.returncode==0,'confirmation child failed')
        r=read(out/'RESULT.json')
        for k,v in [('complete',True),('method_id',method),('trial_id',trial['trial_id']),('numerical_source_commit',manifest['numerical_source_commit']),('assessment_fingerprint',manifest['assessment_fingerprint']),('protocol_sha256',manifest['protocol_sha256'])]:
            require(r.get(k)==v,'result identity mismatch: '+k)
        for n,f in manifest['files'].items(): require(sha(workspace/n)==f['sha256'],'frozen input changed during execution: '+n)
        work['complete']=True
    except Exception as exc: work['failure']=str(exc)
    work['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat();work['files']=inventory(out,exclude=['WORK.json']);write(out/'WORK.json',work)
    return work

def run_trial(bundle,workspace,out,trial_id):
    m,p=extract(bundle,workspace);require(os.environ.get('GITHUB_RUN_ATTEMPT','1')=='1','second workflow attempt rejected')
    found=[t for t in trials(p) if t['trial_id']==trial_id];require(len(found)==1,'unknown declared trial')
    t=found[0];out=Path(out).resolve();require(not out.exists(),'refusing duplicate trial');out.mkdir(parents=True)
    records=[]
    for method in t['method_order']: records.append(execute_child(Path(workspace).resolve(),out/method,m,t,method))
    receipt=dict(record_type='R16 all-original-NBO independent signed trial',complete=all(w['complete'] for w in records),trial=t,
        numerical_source_commit=m['numerical_source_commit'],candidate_source_commit=CANDIDATE_SOURCE,candidate_evidence_commit=CANDIDATE_EVIDENCE,
        protocol_sha256=m['protocol_sha256'],assessment_fingerprint=m['assessment_fingerprint'],
        methods=[dict(method_id=w['method_id'],complete=w['complete'],work_sha256=sha(out/w['method_id']/'WORK.json')) for w in records])
    write(out/'TRIAL.json',receipt);size=bounded(out)
    require(receipt['complete'],'incomplete signed; every method attempt retained')
    return dict(complete=True,trial_id=trial_id,artifact=size)

def verify_work(folder,manifest,trial,method):
    folder=Path(folder);w=read(folder/'WORK.json')
    for k,v in [('complete',True),('returncode',0),('method_id',method),('trial_id',trial['trial_id']),
                ('numerical_source_commit',manifest['numerical_source_commit']),('protocol_sha256',manifest['protocol_sha256']),
                ('assessment_fingerprint',manifest['assessment_fingerprint']),('candidate_source_commit',CANDIDATE_SOURCE),('candidate_evidence_commit',CANDIDATE_EVIDENCE)]:
        require(w.get(k)==v,'invalid complete signed WORK: '+k)
    require(w['end_to_end_seconds']>0 and w['peak_rss_kib']>0,'missing complete assessment work')
    require(digest(canonical(w['environment']))==w['environment_fingerprint'],'environment receipt changed')
    require(w['environment']['packages']==manifest['environment_contract']['packages'] and w['environment']['threads']==1,'numerical environment contract changed')
    require(w['environment']['python'].startswith('3.12.') and 'Linux' in w['environment']['platform'],'Python/Linux contract changed')
    require(inventory(folder,exclude=['WORK.json'])==w['files'],'unlisted or missing worker evidence')
    return w

def collect(repo,bundle,input_dir):
    repo=Path(repo).resolve();m=read(Path(bundle)/'SOURCE_MANIFEST.json');source=m['numerical_source_commit']
    require(git(repo,'rev-parse','HEAD').decode().strip()==source,'collector source changed')
    require(not git(repo,'diff','--name-only',source).strip(),'tracked historical/source bytes changed')
    check(repo)
    for name,f in m['files'].items():require(sha(repo/name)==f['sha256'],'collector source closure changed')
    p=read(repo/PROTOCOL);expected=trials(p);found={}
    for path in Path(input_dir).rglob('TRIAL.json'):
        r=read(path);ident=r['trial']['trial_id'];require(ident not in found,'duplicate trial artifact');found[ident]=path
    require(set(found)=={t['trial_id'] for t in expected},'complete original finite stream set required')
    dest=repo/R16/'results/signed_mechanism';require(not dest.exists(),'refusing existing signed evidence');dest.mkdir(parents=True)
    for t in expected:
        path=found[t['trial_id']];r=read(path)
        require(r['complete'] and r['trial']==t and r['numerical_source_commit']==source and r['assessment_fingerprint']==m['assessment_fingerprint'],'trial source/bank mismatch')
        require([v['method_id'] for v in r['methods']]==t['method_order'],'method rotation changed')
        for entry in r['methods']:
            method=entry['method_id'];folder=path.parent/method
            require(sha(folder/'WORK.json')==entry['work_sha256'],'trial WORK digest changed');verify_work(folder,m,t,method)
        shutil.copytree(path.parent,dest/'trials'/t['trial_id'])
    write(dest/'SOURCE_MANIFEST.json',m)
    subprocess.run([sys.executable,str(repo/REPORT),'--repo',str(repo),'--results',str(dest/'trials'),'--out',str(dest/'report')],cwd=repo,check=True)
    report=read(dest/'report/REPORT.json')
    require(report['complete'] and report['policy_executions']==32 and report['confidence']['event_count']==6,'incomplete scientific report')
    audit=dict(record_type='R16 complete independent prospective signed Bellman signed audit',complete=True,numerical_source_commit=source,
        candidate_source_commit=CANDIDATE_SOURCE,candidate_evidence_commit=CANDIDATE_EVIDENCE,protocol_sha256=m['protocol_sha256'],
        assessment_fingerprint=m['assessment_fingerprint'],trial_count=32,policy_executions=32,confidence_events=6,
        old_policies_preserved=True,old_stopping_unchanged=True,new_confirmation_banks=32,new_training_runs=0,
        evidence_gate='Every source, candidate, independent bank, raw array and report is required; no favorable sign is required.')
    write(dest/'FINAL_AUDIT.json',audit)
    write(dest/'EVIDENCE_MANIFEST.json',dict(record_type='R16 prospective signed evidence inventory',numerical_source_commit=source,
        files={x.relative_to(repo).as_posix():dict(sha256=sha(x),bytes=x.stat().st_size) for x in sorted(dest.rglob('*')) if x.is_file()},
        scope='All new signed payload; this manifest alone is excluded to avoid a circular digest.'))
    summary=repo/R16/'results/signed_mechanism_summary'
    require(not summary.exists(),'summary already exists');summary.mkdir(parents=True)
    for name in ['SOURCE_MANIFEST.json','FINAL_AUDIT.json','EVIDENCE_MANIFEST.json']: shutil.copyfile(dest/name,summary/name)
    shutil.copytree(dest/'report',summary/'report');bounded(summary)
    return dict(complete=True,trials=32,policy_executions=32,report_sha256=sha(dest/'report/REPORT.json'))

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    x=sub.add_parser('check');x.add_argument('--repo',type=Path,default=Path.cwd())
    x=sub.add_parser('pack');x.add_argument('--repo',type=Path,default=Path.cwd());x.add_argument('--out',type=Path,required=True);x.add_argument('--source',default=os.environ.get('NBO_R16_SIGNED_SOURCE_COMMIT'))
    x=sub.add_parser('run-trial')
    for name in ['bundle','workspace','out']:x.add_argument('--'+name,type=Path,required=True)
    x.add_argument('--trial-id',required=True)
    x=sub.add_parser('collect');x.add_argument('--repo',type=Path,default=Path.cwd())
    for name in ['bundle','input-dir']:x.add_argument('--'+name,type=Path,required=True)
    x=sub.add_parser('bounded');x.add_argument('folder',type=Path)
    args=vars(parser.parse_args());command=args.pop('command').replace('-','_');print(json.dumps(globals()[command](**args),indent=2,allow_nan=False))

if __name__=='__main__':main()
