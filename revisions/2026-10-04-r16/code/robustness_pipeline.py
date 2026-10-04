"""Source-bound R16 robustness execution and complete finite-family collection.

Each trial runs four fresh processes and produces five prespecified policies.
The HJB process has two outputs with a disclosed shared prerequisite cost.
Only bounded source and trial artifacts are transported; historical raw data
remain in Git ancestry. This module never selects a favorable calibration.
"""
from __future__ import annotations
import argparse
import ast
import datetime as dt
import gzip
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

# These small generic helpers are themselves an immutable, source-bound input.
from replication_pipeline import (require,canonical,digest,sha,read,write,git,safe,
    git_blob,tree,environment,inventory,bounded,PACKAGES)

R16=Path('revisions/2026-10-04-r16')
R15=Path('revisions/2026-10-04-r15')
PROTOCOL=R16/'protocols/robustness.json'
HJB_DESIGN=R16/'protocols/strong_hjb_design.json'
PIPELINE=R16/'code/robustness_pipeline.py'
WORKER=R16/'code/robustness_worker.py'
REPORT=R16/'code/robustness_report.py'
TESTS=R16/'code/robustness_tests.py'
WORKFLOW=Path('.github/workflows/nbo-r16-robustness.yml')
INHERITED_MANIFEST=R15/'results/experiment/SOURCE_MANIFEST.json'
BASE='cb4595bbcc7147e47e44ba40cb2f5034510ae19f'
GROUPS=['nbo','raw_costate','direct_policy','hjb_family']
METHODS=['nbo','raw_costate','direct_policy','hjb_greedy','hjb_distilled']
CALIBRATIONS=['high','low','long','stress']

def outputs(group):return ['hjb_greedy','hjb_distilled'] if group=='hjb_family' else [group]

def trials(p):
    rows=[]
    for ci,c in enumerate(p['calibrations']):
        for di,d in enumerate(p['dimensions']):
            for si,s in enumerate(p['seeds']):
                offset=(ci+di+si)%len(GROUPS)
                key=f"{p['stream_domain']}/{c['id']}/{s}/{d}/{p['confirmation']['bank_domain']}/0"
                rows.append(dict(trial_id=f"{c['id']}_d{d}_s{s}",calibration_id=c['id'],dimension=d,stream_seed=s,
                    noise_key=key,noise_seed=int.from_bytes(__import__('hashlib').sha256(key.encode()).digest()[:8],'big'),
                    group_order=GROUPS[offset:]+GROUPS[:offset]))
    return rows

def validate_protocol(p):
    require(p['schema']=='nbo-r16-robustness-v1' and p['status']=='frozen_before_confirmatory_execution','robustness protocol is not frozen')
    require(p['review_commit']==BASE,'review source identity changed')
    require([c['id'] for c in p['calibrations']]==CALIBRATIONS and p['dimensions']==[10,50],'complete economic family required')
    require(p['execution_groups']==GROUPS and p['methods']==METHODS,'canonical execution/output family changed')
    require(len(p['seeds'])==len(set(p['seeds']))==8,'all eight pre-drawn streams required')
    require(p['confirmation']['paths_per_stream']==8192 and p['confirmation']['steps']==2048,'confirmation budget changed')
    require(p['confirmation']['direct_contrasts']==[['nbo',m] for m in METHODS[1:]],'direct contrast family changed')
    require(p['inference']['alpha']==.01 and p['inference']['two_sided_event_count']==648,'new confidence allocation changed')
    require(p['economic_decisions']['material_payoff_margin']==.0001 and p['economic_decisions']['equivalence_margin']==.0001,'economic margins changed')
    require(p['training']['checkpoint_count']==3 and p['training']['global_steps']==64,'fixed training envelope changed')
    for c in p['calibrations']:
        require(digest(canonical(c['primitives']))==c['primitives_sha256'],'primitive fingerprint mismatch')
    t=trials(p);require(len(t)==64 and len({r['noise_seed'] for r in t})==64,'new confirmation banks collide')
    return t

def source_files(repo):
    repo=Path(repo);p=read(repo/PROTOCOL)
    old=[n for n in read(repo/INHERITED_MANIFEST)['files'] if not n.endswith('.pt')]
    own=[PROTOCOL,HJB_DESIGN,PIPELINE,WORKER,REPORT,TESTS,WORKFLOW,INHERITED_MANIFEST,
         R16/'code/replication_pipeline.py',R16/'code/capital_adapter.py',R16/'code/capital_verifier.py',
         R16/'code/strong_hjb.py',R16/'code/strong_hjb_tests.py',R16/'code/paired_capital.py',R16/'code/independent_capital_pair_audit.py',
         R15/'code/report_paired_transfer.py',R15/'code/paired_transfer_checks.py',
         R15/'manuscript/paired_transfer.tex',R15/'PAIRED_TRANSFER_REFINEMENT.md']
    for c in p['calibrations']:
        for d in p['dimensions']:
            own.extend([R16/f"protocols/robustness_constants/{c['id']}_d{d}.json",
                        R16/f"results/receipts/robustness_constant_audits/{c['id']}_d{d}.json"])
    return sorted(set(map(str,own))|set(old))

def check(repo):
    repo=Path(repo).resolve();p=read(repo/PROTOCOL);t=validate_protocol(p)
    inherited=read(repo/INHERITED_MANIFEST)
    require(inherited['numerical_source_commit']=='9142f404bb9c5163aa94d3a4ded4d0fa48a49c50','incorrect inherited kernel source')
    for name,f in inherited['files'].items():
        if name.endswith('.pt'):continue
        data=safe(repo,name).read_bytes()
        require(digest(data)==f['sha256'] and git_blob(data)==f['git_blob'],'preserved historical kernel changed: '+name)
    for c in p['calibrations']:
        for d in p['dimensions']:
            path=repo/R16/f"protocols/robustness_constants/{c['id']}_d{d}.json";a=read(path)
            audit=read(repo/R16/f"results/receipts/robustness_constant_audits/{c['id']}_d{d}.json")
            require(a['calibration_id']==c['id'] and a['dimension']==d and a['economic_primitives']==c['primitives'],'wrong paired account')
            require(a['protocol_sha256']==sha(repo/PROTOCOL),'paired account was not frozen with the current protocol')
            require(a['epsilon']==c['epsilon'] and a['steps']==p['confirmation']['steps'],'paired account radius/grid changed')
            require(audit['status']=='passed' and audit['account_sha256']==sha(path) and audit['protocol_sha256']==sha(repo/PROTOCOL),'independent mathematical audit does not bind the fixed account')
            require(len(audit['account']['checks'])==21 and all(x['stored_encloses_reference'] for x in audit['account']['checks']),'independent formula account incomplete')
    for n in source_files(repo):
        path=safe(repo,n);require(path.is_file() and not path.is_symlink(),'missing source input: '+n)
        if n.endswith('.py'):ast.parse(path.read_text(),filename=n)
    return dict(complete=True,trials=len(t),fresh_group_processes=256,policy_outputs=320,confidence_events=648,
                deterministic_accounts=8,independent_formula_enclosures=168,confirmation_observations_evaluated=0)

def pack(repo,out,source):
    repo=Path(repo).resolve();out=Path(out).resolve()
    require(git(repo,'rev-parse','HEAD').decode().strip()==source,'checkout differs from numerical source')
    git(repo,'merge-base','--is-ancestor',BASE,source)
    require(os.environ.get('GITHUB_RUN_ATTEMPT','1')=='1','second confirmatory workflow attempt rejected')
    if os.environ.get('GITHUB_SHA'):require(os.environ['GITHUB_SHA']==source,'Actions source mismatch')
    check(repo);committed=tree(repo,source);payload={};files={}
    for name in source_files(repo):
        data=safe(repo,name).read_bytes();require(name in committed and git_blob(data)==committed[name]['git_blob'],'uncommitted numerical dependency: '+name)
        payload[name]=data;files[name]=dict(sha256=digest(data),bytes=len(data),git_blob=git_blob(data))
    require(not out.exists() or not any(out.iterdir()),'source package must be new');out.mkdir(parents=True,exist_ok=True)
    archive=out/'source.tar.gz'
    with archive.open('wb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT) as tar:
                for name,data in payload.items():
                    item=tarfile.TarInfo(name);item.size=len(data);item.mode=0o644;item.mtime=0;item.uid=item.gid=0;item.uname=item.gname='';tar.addfile(item,io.BytesIO(data))
    p=read(repo/PROTOCOL);contract=dict(python='3.12',packages=PACKAGES,platform='Linux',numeric_threads=1,torch_device='cpu')
    fingerprints={}
    for group in GROUPS:
        info=dict(group=group,output_methods=outputs(group),protocol_sha256=files[str(PROTOCOL)]['sha256'],files={n:f['sha256'] for n,f in files.items()},environment_contract=contract)
        fingerprints[group]=dict(sha256=digest(canonical(info)),input=info)
    m=dict(record_type='R16 immutable complete economic-robustness source bundle',numerical_source_commit=source,reviewed_parent_commit=BASE,
        protocol_sha256=files[str(PROTOCOL)]['sha256'],files=files,environment_contract=contract,method_fingerprints=fingerprints,
        matrix={'include':trials(p)},archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        github_run_id=os.environ.get('GITHUB_RUN_ID'),github_run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT','1'),
        scope='Four economic calibrations, two dimensions, eight pre-drawn fixed streams, four fresh group processes and five prespecified method outputs per trial.')
    write(out/'SOURCE_MANIFEST.json',m);(out/'robustness_pipeline.py').write_bytes(payload[str(PIPELINE)])
    (out/'replication_pipeline.py').write_bytes(payload[str(R16/'code/replication_pipeline.py')]);bounded(out)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('matrix='+canonical({'include':[{'trial_id':x['trial_id']} for x in trials(p)]}).decode()+'\n')
    return dict(complete=True,source=source,source_files=len(files),source_archive_bytes=archive.stat().st_size,trials=64)

def extract(bundle,workspace):
    bundle=Path(bundle).resolve();workspace=Path(workspace).resolve();m=read(bundle/'SOURCE_MANIFEST.json')
    require(sha(__file__)==m['files'][str(PIPELINE)]['sha256'],'unbound robustness launcher')
    require(sha(bundle/'replication_pipeline.py')==m['files'][str(R16/'code/replication_pipeline.py')]['sha256'],'unbound generic source helper')
    require(sha(bundle/'source.tar.gz')==m['archive_sha256'],'source archive changed')
    for fp in m['method_fingerprints'].values():require(digest(canonical(fp['input']))==fp['sha256'],'method fingerprint changed')
    require(not workspace.exists() or not any(workspace.iterdir()),'worker workspace must be empty');workspace.mkdir(parents=True,exist_ok=True);seen=set()
    with tarfile.open(bundle/'source.tar.gz','r:gz') as tar:
        for item in tar:
            name=item.name;require(item.isfile() and name in m['files'] and name not in seen,'unlisted/repeated source member')
            path=safe(workspace,name);data=tar.extractfile(item).read();require(digest(data)==m['files'][name]['sha256'] and len(data)==m['files'][name]['bytes'],'source content mismatch')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);seen.add(name)
    require(seen==set(m['files']),'source closure incomplete');check(workspace);p=read(workspace/PROTOCOL)
    require(sha(workspace/PROTOCOL)==m['protocol_sha256'] and m['matrix']=={'include':trials(p)},'source matrix/protocol changed')
    return m,p

def standalone_work(elapsed,r):
    shared=float(r['shared_prerequisite_seconds_since_entry'])
    durations={m:float(v['deployment_and_confirmation_seconds']) for m,v in r['outputs'].items()}
    overhead=float(elapsed)-shared-sum(durations.values())
    require(overhead>=0,'group clock does not cover all child phases')
    answer={}
    for method,own in durations.items():
        answer[method]=dict(standalone_end_to_end_seconds=float(elapsed) if len(durations)==1 else shared+own+overhead,
            shared_prerequisite_seconds=shared,own_deployment_and_confirmation_seconds=own,
            shared_launch_and_finalization_seconds=overhead,
            excluded_other_deployment_seconds=sum(v for m,v in durations.items() if m!=method),
            cost_scope='Full recorded group clock, less only the other prespecified deployment/evaluation phase. All shared fitting, diagnostics, both output writes, process launch and exit are assigned to each standalone method. This is a stated allocation from a shared construction, not a separately timed independent HJB fit.')
    return answer

def execute_child(workspace,out,m,trial,group):
    workspace=Path(workspace);out=Path(out);require(not out.exists(),'refusing repeated robustness group')
    actual=environment();env=dict(os.environ)
    env.update(NBO_R16_SOURCE_COMMIT=m['numerical_source_commit'],NBO_R16_METHOD_FINGERPRINT=m['method_fingerprints'][group]['sha256'],
        PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',NUMBA_NUM_THREADS='1')
    work=dict(record_type='R16 complete independent robustness group process work',complete=False,group=group,output_methods=outputs(group),
        trial_id=trial['trial_id'],calibration_id=trial['calibration_id'],dimension=trial['dimension'],stream_seed=trial['stream_seed'],
        numerical_source_commit=m['numerical_source_commit'],protocol_sha256=m['protocol_sha256'],method_fingerprint=m['method_fingerprints'][group]['sha256'],
        environment=actual,environment_fingerprint=digest(canonical(actual)),started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        timing_scope='Parent process launch through all fitted candidates, successful/failed selection checks, all policy outputs, final RESULT write and process exit.',
        provisioning_scope='Dependency installation and verified source extraction occur before the complete algorithm clock; imports and every scientific computation are charged.')
    command=[sys.executable,str(workspace/WORKER),'--protocol',str(workspace/PROTOCOL),'--trial-id',trial['trial_id'],'--group',group,'--out',str(out)]
    # The worker requires an empty destination. Keep its parent log outside
    # that destination until the child has exited, then retain it verbatim.
    with tempfile.TemporaryDirectory(prefix='nbo-r16-robustness-parent-') as tmp:
        tmp=Path(tmp);env['NUMBA_CACHE_DIR']=str(tmp/'numba');logpath=tmp/'process.log'
        with logpath.open('wb') as log:
            start=time.perf_counter_ns();child=subprocess.Popen(command,cwd=workspace,env=env,stdout=log,stderr=subprocess.STDOUT)
            _,status,usage=os.wait4(child.pid,0);finished=time.perf_counter_ns();child.returncode=os.waitstatus_to_exitcode(status)
        out.mkdir(parents=True,exist_ok=True);shutil.copyfile(logpath,out/'process.log')
        work.update(end_to_end_seconds=(finished-start)/1e9,returncode=child.returncode,peak_rss_kib=int(usage.ru_maxrss),
            user_cpu_seconds=usage.ru_utime,system_cpu_seconds=usage.ru_stime,cpu_seconds=usage.ru_utime+usage.ru_stime)
    try:
        require(child.returncode==0,'robustness child failed');r=read(out/'RESULT.json')
        for k,v in [('complete',True),('group',group),('trial_id',trial['trial_id']),('numerical_source_commit',m['numerical_source_commit']),
                    ('protocol_sha256',m['protocol_sha256']),('method_fingerprint',m['method_fingerprints'][group]['sha256']),('online_payoff_checks',0),('final_payoff_used_for_selection',False)]:
            require(r.get(k)==v,'invalid complete group result: '+k)
        require(set(r['outputs'])==set(outputs(group)) and all(x['complete'] for x in r['outputs'].values()),'missing prespecified method output')
        work['method_complete_work_allocation']=standalone_work(work['end_to_end_seconds'],r)
        work['operation_counters_complete']=all(v.get('operation_counters_complete',False) for v in r['outputs'].values())
        for n,f in m['files'].items():require(sha(workspace/n)==f['sha256'],'frozen source changed: '+n)
        work['complete']=True
    except Exception as exc:work['failure']=str(exc)
    work['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat();work['files']=inventory(out,exclude=['WORK.json']);write(out/'WORK.json',work)
    return work

def verify_work(folder,m,trial,group):
    folder=Path(folder);w=read(folder/'WORK.json')
    for k,v in [('complete',True),('returncode',0),('group',group),('trial_id',trial['trial_id']),('numerical_source_commit',m['numerical_source_commit']),
                ('protocol_sha256',m['protocol_sha256']),('method_fingerprint',m['method_fingerprints'][group]['sha256'])]:require(w.get(k)==v,'group WORK identity mismatch: '+k)
    require(w['end_to_end_seconds']>0 and w['peak_rss_kib']>0,'missing full group time or memory')
    require(inventory(folder,exclude=['WORK.json'])==w['files'],'unlisted or missing group evidence')
    require(digest(canonical(w['environment']))==w['environment_fingerprint'],'environment receipt changed')
    e,c=w['environment'],m['environment_contract'];require(e['packages']==c['packages'] and e['threads']==c['numeric_threads'],'wrong numerical environment')
    require(e['python'].startswith(c['python']+'.') and e['platform'].startswith(c['platform']),'wrong interpreter/platform')
    require(w['method_complete_work_allocation']==standalone_work(w['end_to_end_seconds'],read(folder/'RESULT.json')),'standalone shared-work account does not reconstruct')
    return w

def run_trial(bundle,workspace,out,trial_id):
    m,p=extract(bundle,workspace);require(os.environ.get('GITHUB_RUN_ATTEMPT','1')=='1','repeated confirmation attempt rejected')
    rows=[x for x in trials(p) if x['trial_id']==trial_id];require(len(rows)==1,'unknown declared trial');trial=rows[0]
    out=Path(out).resolve();require(not out.exists(),'refusing repeated trial');out.mkdir(parents=True)
    works=[execute_child(Path(workspace).resolve(),out/g,m,trial,g) for g in trial['group_order']]
    receipt=dict(record_type='R16 complete five-method economic robustness trial',trial=trial,complete=all(w['complete'] for w in works),
        numerical_source_commit=m['numerical_source_commit'],protocol_sha256=m['protocol_sha256'],
        groups=[dict(group=w['group'],complete=w['complete'],work_sha256=sha(out/w['group']/'WORK.json')) for w in works])
    write(out/'TRIAL.json',receipt);size=bounded(out);require(receipt['complete'],'failed group retained; no omitted method or replacement stream')
    return dict(complete=True,trial_id=trial_id,artifact=size)

def collect(repo,bundle,input_dir):
    repo=Path(repo).resolve();m=read(Path(bundle)/'SOURCE_MANIFEST.json');source=m['numerical_source_commit']
    require(git(repo,'rev-parse','HEAD').decode().strip()==source,'collector source changed')
    require(not git(repo,'diff','--name-only',source).strip(),'historical/source files changed');check(repo)
    for n,f in m['files'].items():require(sha(repo/n)==f['sha256'],'collector source closure changed')
    p=read(repo/PROTOCOL);expected=trials(p);found={}
    for path in Path(input_dir).rglob('TRIAL.json'):
        ident=read(path)['trial']['trial_id'];require(ident not in found,'duplicate trial artifact');found[ident]=path
    require(set(found)=={x['trial_id'] for x in expected},'complete fixed 64-trial population required')
    dest=repo/R16/'results/robustness';require(not dest.exists(),'refusing existing robustness evidence');dest.mkdir(parents=True)
    for trial in expected:
        path=found[trial['trial_id']];r=read(path)
        require(r['complete'] and r['trial']==trial and r['numerical_source_commit']==source and r['protocol_sha256']==m['protocol_sha256'],'trial provenance mismatch')
        require([x['group'] for x in r['groups']]==trial['group_order'],'group rotation changed')
        for x in r['groups']:
            folder=path.parent/x['group'];require(sha(folder/'WORK.json')==x['work_sha256'],'group work hash changed');verify_work(folder,m,trial,x['group'])
        shutil.copytree(path.parent,dest/'trials'/trial['trial_id'])
    write(dest/'SOURCE_MANIFEST.json',m)
    for calibration in CALIBRATIONS:
        subprocess.run([sys.executable,str(repo/REPORT),'--repo',str(repo),'--results',str(dest/'trials'),
            '--out',str(dest/'report/parts'/calibration),'--calibration',calibration],cwd=repo,check=True)
    subprocess.run([sys.executable,str(repo/REPORT),'--repo',str(repo),'--out',str(dest/'report'),'--aggregate'],cwd=repo,check=True)
    report=read(dest/'report/REPORT.json');require(report['complete'] and report['policy_outputs']==320 and report['confidence']['event_count']==648,'incomplete scientific family report')
    write(dest/'FINAL_AUDIT.json',dict(record_type='R16 complete source-bound robustness evidence audit',complete=True,
        numerical_source_commit=source,protocol_sha256=m['protocol_sha256'],trials=64,fresh_group_processes=256,policy_outputs=320,confidence_events=648,
        calibrations=CALIBRATIONS,all_declared_streams_retained=True,favorable_sign_required=False,old_evidence_unchanged=True))
    write(dest/'EVIDENCE_MANIFEST.json',dict(record_type='R16 robustness exhaustive evidence inventory',numerical_source_commit=source,
        files={x.relative_to(repo).as_posix():dict(sha256=sha(x),bytes=x.stat().st_size) for x in sorted(dest.rglob('*')) if x.is_file()},
        scope='All new raw records, independent work, fixed-source manifest, reports and final audit; only this digest manifest is excluded.'))
    summary=repo/R16/'results/robustness_summary';require(not summary.exists(),'summary already exists');summary.mkdir(parents=True)
    for name in ['SOURCE_MANIFEST.json','FINAL_AUDIT.json','EVIDENCE_MANIFEST.json']:shutil.copyfile(dest/name,summary/name)
    shutil.copytree(dest/'report',summary/'report');bounded(summary)
    return dict(complete=True,trials=64,policy_outputs=320,report_sha256=sha(dest/'report/REPORT.json'))

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    x=sub.add_parser('check');x.add_argument('--repo',type=Path,default=Path.cwd())
    x=sub.add_parser('pack');x.add_argument('--repo',type=Path,default=Path.cwd());x.add_argument('--out',type=Path,required=True);x.add_argument('--source',default=os.environ.get('NBO_R16_SOURCE_COMMIT'))
    x=sub.add_parser('run-trial')
    for n in ['bundle','workspace','out']:x.add_argument('--'+n,type=Path,required=True)
    x.add_argument('--trial-id',required=True)
    x=sub.add_parser('collect');x.add_argument('--repo',type=Path,default=Path.cwd())
    for n in ['bundle','input-dir']:x.add_argument('--'+n,type=Path,required=True)
    args=vars(parser.parse_args());command=args.pop('command').replace('-','_')
    import json
    print(json.dumps(globals()[command](**args),indent=2,allow_nan=False))

if __name__=='__main__':main()
