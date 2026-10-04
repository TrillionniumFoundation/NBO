"""Immutable-source execution and lossless, bounded evidence for critic reuse.

All five methods finish all three registered work stages before a separate
process can read the independent confirmation banks. Payloads are partitioned
without deletion; each retrieval artifact is below 24 MiB. The collector
requires every declared stream, method, stage, raw file and protected endpoint.
"""
from __future__ import annotations
import argparse
import ast
import datetime as dt
import gzip
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time

from replication_pipeline import (require,canonical,digest,sha,read,write,git,
    safe,git_blob,tree,environment,inventory,bounded,PACKAGES,BASE)

R16=Path('revisions/2026-10-04-r16')
PROTOCOL=R16/'protocols/menu_protocol.json'
PIPELINE=R16/'code/menu_pipeline.py'
WORKER=R16/'code/menu_worker.py'
CONFIRM=R16/'code/menu_confirm.py'
REPORT=R16/'code/menu_report.py'
WORKFLOW=Path('.github/workflows/nbo-r16-continuation-menu.yml')
METHODS=['nbo_scalar','vector_costate','raw_actor','dpo_actor','raw_saa']
PART_PAYLOAD=23*1024*1024
MAX_PARTS=12

def trials(p):
    rows=[]
    for ci,c in enumerate(p['calibrations']):
        for di,d in enumerate(p['dimensions']):
            for si,s in enumerate(p['training_streams']['seeds']):
                offset=(ci+di+si)%5
                rows.append(dict(trial_id=f"{c['id']}_d{d}_s{s}",calibration=c['id'],dimension=d,
                    stream_seed=s,method_order=METHODS[offset:]+METHODS[:offset]))
    return rows

def validate_protocol(p):
    require(p['schema']=='nbo-r16-continuation-menu-protocol-v1','unknown menu protocol')
    require(p['status']=='requires_external_immutable_source_commit_before_execution','source freeze contract changed')
    require(p['methods']==METHODS and p['dimensions']==[10,50],'incomplete method or dimension family')
    require([c['id'] for c in p['calibrations']]==['original_low','quarterly_reuse','long_reuse','untouched_intermediate'],'economic family changed')
    seeds=p['training_streams']['seeds'];require(len(seeds)==len(set(seeds))==16,'all sixteen fixed streams required')
    require(p['training']['cumulative_replay_states']==[128,512,2048],'registered work stages changed')
    require(p['training']['saa_antithetic_paths']==[4,16,64],'Raw cache budget changed')
    conf=p['confidence'];require(conf['alpha']==.018 and conf['event_count']==216 and conf['scalar_alpha']==.002 and conf['scalar_event_count']==128 and conf['total_menu_alpha']==.02,'menu confidence family changed')
    require(conf['economic_margin']==.0001 and p['confirmation']['antithetic_pairs_per_query']==512,'registered precision or materiality changed')
    require(len(p['tasks'])==12 and all(p['query_catalogs'][str(d)]['complete_queries']==384 for d in [10,50]),'fixed query catalog incomplete')
    require(p['execution']['confirmation_may_be_read_by_fitting'] is False,'confirmation may enter fitting')
    names=[t['trial_id'] for t in trials(p)];require(len(names)==len(set(names))==128,'incomplete trial matrix')

def source_files(repo):
    p=read(Path(repo)/PROTOCOL)
    return sorted(set(p['execution']['source_files'])|{str(PIPELINE),str(WORKER),str(CONFIRM),str(REPORT),str(WORKFLOW),
        str(R16/'code/menu_pipeline_tests.py'),str(R16/'code/replication_pipeline.py'),
        str(R16/'protocols/confidence_families.json')})

def check(repo):
    repo=Path(repo).resolve();p=read(repo/PROTOCOL);validate_protocol(p)
    names=source_files(repo)
    require(set(names)<=set(p['execution']['source_files']),'protocol must enumerate the entire numerical closure')
    for name in names:
        f=safe(repo,name);require(f.is_file() and not f.is_symlink(),'missing declared dependency: '+name)
        if name.endswith('.py'):ast.parse(f.read_text(),filename=name)
    return dict(complete=True,trial_count=128,method_fits=640,stage_candidates=1920,
        primary_events=216,scalar_events=128,new_confirmation_observations=0,source_files=len(names))

def pack(repo,out,source):
    repo=Path(repo).resolve();out=Path(out).resolve()
    require(git(repo,'rev-parse','HEAD').decode().strip()==source,'checkout is not frozen source')
    git(repo,'merge-base','--is-ancestor',BASE,source)
    require(os.environ.get('GITHUB_RUN_ATTEMPT','1')=='1','second execution attempt rejected')
    if os.environ.get('GITHUB_SHA'):require(os.environ['GITHUB_SHA']==source,'workflow source mismatch')
    check(repo);committed=tree(repo,source);payload={};files={}
    for name in source_files(repo):
        data=safe(repo,name).read_bytes()
        require(name in committed and git_blob(data)==committed[name]['git_blob'],'uncommitted menu dependency: '+name)
        payload[name]=data;files[name]=dict(sha256=digest(data),bytes=len(data),git_blob=git_blob(data))
    require(not out.exists() or not any(out.iterdir()),'source output must be new')
    out.mkdir(parents=True,exist_ok=True);archive=out/'source.tar.gz'
    with archive.open('wb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as zipped:
            with tarfile.open(fileobj=zipped,mode='w',format=tarfile.PAX_FORMAT) as tar:
                for name,data in payload.items():
                    info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0
                    info.uid=info.gid=0;info.uname=info.gname='';tar.addfile(info,io.BytesIO(data))
    contract=dict(python='3.12',packages=PACKAGES,platform='Linux',numeric_threads=1,torch_device='cpu',
        process_scope='one fresh fitting process per method, all stages before independent verification')
    fp=dict(protocol_sha256=files[str(PROTOCOL)]['sha256'],files={n:v['sha256'] for n,v in files.items()},environment_contract=contract)
    m=dict(record_type='R16 immutable continuation-menu source',numerical_source_commit=source,source_commit=source,
        reviewed_parent_commit=BASE,protocol_sha256=files[str(PROTOCOL)]['sha256'],files=files,
        assessment_fingerprint=digest(canonical(fp)),fingerprint_input=fp,environment_contract=contract,
        matrix={'include':trials(read(repo/PROTOCOL))},archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        github_run_id=os.environ.get('GITHUB_RUN_ID'),github_run_attempt=os.environ.get('GITHUB_RUN_ATTEMPT','1'))
    write(out/'SOURCE_MANIFEST.json',m)
    # The outer launcher has a single pure-standard-library helper. Both
    # copies are matched against this manifest before extraction or execution.
    for name in [PIPELINE,R16/'code/replication_pipeline.py']:(out/name.name).write_bytes(payload[str(name)])
    bounded(out)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:
            f.write('matrix='+canonical({'include':[{'trial_id':t['trial_id']} for t in trials(read(repo/PROTOCOL))]}).decode()+'\n')
    return dict(complete=True,source=source,trial_count=128,source_files=len(files),archive_bytes=archive.stat().st_size)

def extract(bundle,workspace):
    bundle=Path(bundle).resolve();workspace=Path(workspace).resolve();m=read(bundle/'SOURCE_MANIFEST.json')
    require(sha(bundle/'menu_pipeline.py')==m['files'][str(PIPELINE)]['sha256'],'unbound menu launcher')
    require(sha(bundle/'replication_pipeline.py')==m['files'][str(R16/'code/replication_pipeline.py')]['sha256'],'unbound standard-library helper')
    require(sha(bundle/'source.tar.gz')==m['archive_sha256'],'source archive changed')
    require(digest(canonical(m['fingerprint_input']))==m['assessment_fingerprint'],'source fingerprint changed')
    require(not workspace.exists() or not any(workspace.iterdir()),'workspace must be new')
    workspace.mkdir(parents=True,exist_ok=True);seen=set()
    with tarfile.open(bundle/'source.tar.gz','r:gz') as tar:
        for member in tar:
            name=member.name;require(member.isfile() and name in m['files'] and name not in seen,'unlisted or repeated source member')
            data=tar.extractfile(member).read();facts=m['files'][name]
            require(len(data)==facts['bytes'] and digest(data)==facts['sha256'] and git_blob(data)==facts['git_blob'],'source member differs')
            f=safe(workspace,name);f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data);seen.add(name)
    require(seen==set(m['files']),'incomplete source closure');check(workspace)
    p=read(workspace/PROTOCOL);require(sha(workspace/PROTOCOL)==m['protocol_sha256'] and m['matrix']=={'include':trials(p)},'protocol or matrix differs')
    return m,p

def execute(workspace,command,log,env,timeout_seconds):
    log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='nbo-r16-menu-jit-') as cache:
        childenv=dict(env,NUMBA_CACHE_DIR=cache)
        with log.open('wb') as f:
            start=time.perf_counter_ns();child=subprocess.Popen(command,cwd=workspace,env=childenv,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            timed_out=False
            while True:
                finished,status,usage=os.wait4(child.pid,os.WNOHANG)
                if finished:break
                if (time.perf_counter_ns()-start)/1e9>timeout_seconds:
                    timed_out=True;os.killpg(child.pid,signal.SIGKILL)
                    _,status,usage=os.wait4(child.pid,0);break
                time.sleep(.2)
            finish=time.perf_counter_ns();child.returncode=os.waitstatus_to_exitcode(status)
            f.flush();os.fsync(f.fileno())
    return dict(returncode=child.returncode,end_to_end_seconds=(finish-start)/1e9,timed_out=timed_out,timeout_seconds=timeout_seconds,
        user_cpu_seconds=usage.ru_utime,system_cpu_seconds=usage.ru_stime,
        cpu_seconds=usage.ru_utime+usage.ru_stime,peak_rss_kib=int(usage.ru_maxrss),
        clock_scope='actual fresh outer process launch through exit; includes scientific child, candidate output, verification of source inputs and process finalization')

def partition(folder,out,trial_id,source,fingerprint):
    """Losslessly partition complete evidence, including unsuccessful attempts."""
    folder=Path(folder).resolve();out=Path(out).resolve()
    require(not out.exists(),'artifact parts already exist')
    files=[]
    for f in sorted(folder.rglob('*')):
        if f.is_file():
            require(not f.is_symlink(),'evidence symlink')
            require(f.stat().st_size<=PART_PAYLOAD,'a scientific file exceeds one retrieval part')
            files.append((f.relative_to(folder).as_posix(),f.stat().st_size,sha(f)))
    bins=[];sizes=[]
    for row in files:
        choice=next((i for i,n in enumerate(sizes) if n+row[1]<=PART_PAYLOAD),len(bins))
        if choice==len(bins):bins.append([]);sizes.append(0)
        bins[choice].append(row);sizes[choice]+=row[1]
    require(len(bins)<=MAX_PARTS,'more evidence parts required than the predeclared transport limit; nothing omitted')
    for index,rows in enumerate(bins):
        dest=out/f'part{index:02d}';dest.mkdir(parents=True)
        for name,_,_ in rows:
            target=safe(dest/'payload',name);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(folder/name,target)
        write(dest/'PART.json',dict(schema='nbo-r16-menu-evidence-part-v1',trial_id=trial_id,
            numerical_source_commit=source,assessment_fingerprint=fingerprint,index=index,parts=len(bins),
            files={n:dict(bytes=b,sha256=s) for n,b,s in rows},complete_trial_inventory_sha256=digest(canonical(files))))
        bounded(dest)
    return dict(parts=len(bins),files=len(files),uncompressed_bytes=sum(sizes))

def run_trial(bundle,workspace,out,parts,trial_id):
    m,p=extract(bundle,workspace);workspace=Path(workspace).resolve();out=Path(out).resolve()
    require(os.environ.get('GITHUB_RUN_ATTEMPT','1')=='1','second execution attempt rejected')
    matches=[t for t in trials(p) if t['trial_id']==trial_id];require(len(matches)==1,'undeclared trial')
    t=matches[0];require(not out.exists(),'trial already exists');out.mkdir(parents=True)
    actual=environment();env=dict(os.environ,NBO_R16_MENU_SOURCE_COMMIT=m['numerical_source_commit'],
        NBO_R16_MENU_SOURCE_MANIFEST=str(Path(bundle).resolve()/'SOURCE_MANIFEST.json'),
        NBO_R16_MENU_SOURCE_MANIFEST_SHA256=sha(Path(bundle).resolve()/'SOURCE_MANIFEST.json'),
        NBO_R16_MENU_FINGERPRINT=m['assessment_fingerprint'],PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',
        OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',NUMBA_NUM_THREADS='1')
    works={};failure=[]
    common=['--protocol',str(workspace/PROTOCOL),'--calibration',t['calibration'],'--dimension',str(t['dimension']),'--seed',str(t['stream_seed'])]
    for method in t['method_order']:
        cmd=[sys.executable,str(workspace/WORKER),*common,'--method',method,'--out',str(out/'fits'/method)]
        works[method]=execute(workspace,cmd,out/'logs'/f'{method}.log',env,p['execution']['method_timeout_seconds']+180)
        if works[method]['returncode']!=0:failure.append(dict(method=method,error='fit outer process failed; no replacement execution'))
    # Even a failed fit is represented by the declared feasible fallback. An
    # invalid source or missing fallback blocks confirmation and is retained.
    ready=not failure and all((out/'fits'/method/'FIT_WORK.json').is_file() for method in METHODS)
    confirmation=None
    if ready:
        cmd=[sys.executable,str(workspace/CONFIRM),*common,'--fits',str(out/'fits'),'--out',str(out/'confirmation')]
        confirmation=execute(workspace,cmd,out/'logs'/'confirmation.log',env,p['execution']['confirmation_timeout_seconds'])
        if confirmation['returncode']!=0:failure.append(dict(error='independent confirmation failed; original attempt retained'))
    for n,f in m['files'].items():require(sha(workspace/n)==f['sha256'],'frozen input mutated during trial: '+n)
    receipt=dict(schema='nbo-r16-menu-trial-v1',complete=ready and not failure,trial=t,
        numerical_source_commit=m['numerical_source_commit'],assessment_fingerprint=m['assessment_fingerprint'],
        protocol_sha256=m['protocol_sha256'],environment=actual,environment_fingerprint=digest(canonical(actual)),
        method_process_work=works,confirmation_process_work=confirmation,failures=failure,
        all_fitting_finished_before_confirmation=True,final_confirmation_used_for_selection=False,
        files=inventory(out),provisioning_scope='fixed dependency installation and verified source extraction precede scientific process clocks',
        finished_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    write(out/'TRIAL.json',receipt)
    sizes=partition(out,parts,trial_id,m['numerical_source_commit'],m['assessment_fingerprint'])
    require(receipt['complete'],'incomplete menu trial; all failed attempts remain in transport parts')
    return dict(complete=True,trial_id=trial_id,artifact=sizes)

def reassemble(input_dir,out,manifest,p):
    out=Path(out).resolve();require(not out.exists(),'reassembly destination exists');out.mkdir(parents=True)
    expected={t['trial_id']:t for t in trials(p)};found={}
    for f in Path(input_dir).rglob('PART.json'):
        r=read(f);ident=r['trial_id'];require(ident in expected,'undeclared evidence part')
        require(r['schema']=='nbo-r16-menu-evidence-part-v1' and r['numerical_source_commit']==manifest['numerical_source_commit'] and r['assessment_fingerprint']==manifest['assessment_fingerprint'],'mixed source evidence')
        key=(ident,r['index']);require(key not in found,'duplicate evidence part');found[key]=(f,r)
    require({ident for ident,_ in found}==set(expected),'incomplete finite stream evidence')
    for ident,t in expected.items():
        rows=sorted((v for (name,_),v in found.items() if name==ident),key=lambda x:x[1]['index'])
        count=rows[0][1]['parts'];require(1<=count<=MAX_PARTS and [r['index'] for f,r in rows]==list(range(count)),'missing or repeated part index')
        require(all(r['parts']==count and r['complete_trial_inventory_sha256']==rows[0][1]['complete_trial_inventory_sha256'] for f,r in rows),'part inventories disagree')
        seen=set();whole=[]
        for f,r in rows:
            require(inventory(f.parent/'payload')=={n:v['sha256'] for n,v in r['files'].items()},'unlisted or changed part payload')
            for n,v in r['files'].items():
                require(n not in seen,'duplicate original payload');seen.add(n)
                src=safe(f.parent/'payload',n);require(src.stat().st_size==v['bytes'],'payload size changed')
                dest=safe(out/ident,n);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
                whole.append((n,v['bytes'],v['sha256']))
        require(digest(canonical(sorted(whole)))==rows[0][1]['complete_trial_inventory_sha256'],'complete trial inventory differs')
        r=read(out/ident/'TRIAL.json')
        require(r['complete'] and r['trial']==t and r['numerical_source_commit']==manifest['numerical_source_commit'] and r['assessment_fingerprint']==manifest['assessment_fingerprint'] and r['protocol_sha256']==manifest['protocol_sha256'],'trial scientific identity changed')
        require(inventory(out/ident,exclude=['TRIAL.json'])==r['files'],'missing original scientific evidence')
        require(r['all_fitting_finished_before_confirmation'] and not r['final_confirmation_used_for_selection'],'selection read confirmation')
        require(digest(canonical(r['environment']))==r['environment_fingerprint'],'environment receipt changed')
        require(r['environment']['packages']==manifest['environment_contract']['packages'],'numerical environment changed')
        for method,w in r['method_process_work'].items():
            require(method in METHODS and w['returncode']==0 and w['end_to_end_seconds']>0,'incomplete fit process')
            fit=read(out/ident/'fits'/method/'FIT_WORK.json')
            require(fit['source_commit']==manifest['numerical_source_commit'] and fit['protocol_sha256']==manifest['protocol_sha256'] and not fit['final_confirmation_read'],'fit source or confirmation separation changed')
            require(fit['method']==method and fit['calibration']==t['calibration'] and fit['dimension']==t['dimension'] and fit['seed']==t['stream_seed'],'fitted method or complete stream identity differs')
            require(inventory(out/ident/'fits'/method,exclude=['FIT_WORK.json'])=={n:v['sha256'] for n,v in fit['payload_inventory'].items()},'fit payload inventory mismatch')
        require(set(r['method_process_work'])==set(METHODS),'one fitted method omitted')
        require(r['confirmation_process_work']['returncode']==0,'confirmation process did not finish')
    return len(expected)

def collect(repo,bundle,input_dir):
    from menu_transport import restore_analysis_parts,fetch_staging,assert_transport_tree
    repo=Path(repo).resolve();m=read(Path(bundle)/'SOURCE_MANIFEST.json');source=m['numerical_source_commit']
    require(git(repo,'rev-parse','HEAD').decode().strip()==source,'collector source differs')
    require(not git(repo,'diff','--name-only',source).strip(),'source or historical bytes changed')
    check(repo)
    for n,f in m['files'].items():require(sha(repo/n)==f['sha256'],'collector source closure differs: '+n)
    dest=repo/R16/'results/continuation_menu';require(not dest.exists(),'refusing evidence overwrite');dest.mkdir(parents=True)
    receipts=restore_analysis_parts(input_dir,dest/'trials',m)
    count=len(receipts);require(count==128,'every fixed trial must be transported')
    staging=fetch_staging(repo,source)
    full_proof=assert_transport_tree(repo,staging,receipts,m)
    write(dest/'SOURCE_MANIFEST.json',m);write(dest/'FULL_PAYLOAD_GIT_AUDIT.json',full_proof)
    subprocess.run([sys.executable,str(repo/REPORT),'--repo',str(repo),'--results',str(dest/'trials'),'--out',str(dest/'report')],cwd=repo,check=True)
    report=read(dest/'report/REPORT.json');require(report['complete'] and report['primary_event_count']==216 and report['scalar_event_count']==128,'complete protected report required')
    audit=dict(record_type='R16 complete continuation-menu evidence audit',complete=True,numerical_source_commit=source,
        protocol_sha256=m['protocol_sha256'],assessment_fingerprint=m['assessment_fingerprint'],trial_count=count,
        method_fits=640,stage_candidates=1920,primary_events=216,scalar_events=128,
        all_raw_inputs_and_outputs_retained=True,no_stage_or_seed_selection=True,
        staging_commit=staging,full_payload_git_audit_sha256=sha(dest/'FULL_PAYLOAD_GIT_AUDIT.json'),
        full_raw_files=full_proof['full_raw_files'],full_raw_bytes=full_proof['full_raw_bytes'],
        collector_scope='Every original raw file is already preserved and checked in the remote Git tree. The local collector materializes only the complete analysis subset; it recomputes all 216 primary and 128 scalar endpoints.',
        evidence_gate='Every source, fixed stream, all methods, stages, raw file and endpoint; no favorable sign gate')
    write(dest/'FINAL_AUDIT.json',audit)
    files={r['payload_tree_prefix']+'/'+name:value for r in receipts.values() for name,value in r['raw_files'].items()}
    for f in sorted(dest.rglob('*')):
        if f.is_file():
            data=f.read_bytes();name=f.relative_to(repo).as_posix()
            value=dict(sha256=digest(data),bytes=len(data),git_blob=git_blob(data))
            require(name not in files or files[name]==value,'local analysis differs from the complete remote raw identity')
            files[name]=value
    write(dest/'EVIDENCE_MANIFEST.json',dict(numerical_source_commit=source,staging_commit=staging,files=files,
        scope='Complete remote raw payload and local analysis/report files; this inventory alone excluded to avoid circularity. All original training arrays remain in Git.'))
    summary=repo/R16/'results/continuation_menu_summary';require(not summary.exists(),'summary exists');summary.mkdir(parents=True)
    for name in ['SOURCE_MANIFEST.json','FINAL_AUDIT.json','FULL_PAYLOAD_GIT_AUDIT.json','EVIDENCE_MANIFEST.json']:shutil.copyfile(dest/name,summary/name)
    shutil.copytree(dest/'report',summary/'report');bounded(summary)
    return dict(complete=True,trial_count=count,primary_events=216,scalar_events=128,report_sha256=sha(dest/'report/REPORT.json'))

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    x=sub.add_parser('check');x.add_argument('--repo',type=Path,default=Path.cwd())
    x=sub.add_parser('pack');x.add_argument('--repo',type=Path,default=Path.cwd());x.add_argument('--out',type=Path,required=True);x.add_argument('--source',required=True)
    x=sub.add_parser('run-trial')
    for name in ['bundle','workspace','out','parts']:x.add_argument('--'+name,type=Path,required=True)
    x.add_argument('--trial-id',required=True)
    x=sub.add_parser('collect');x.add_argument('--repo',type=Path,default=Path.cwd())
    for name in ['bundle','input-dir']:x.add_argument('--'+name,type=Path,required=True)
    args=vars(parser.parse_args());command=args.pop('command').replace('-','_');print(json.dumps(globals()[command](**args),indent=2,allow_nan=False))

if __name__=='__main__':main()
