"""Reconcile actual completed S recovery clocks without counting nested work twice.

Read-only administrative accounting. The original parent stops before terminal
publication 11. The frozen ledger already counts 20 child launches and 10 packer
inner clocks; this bridge supplies only the remaining parent clock and terminal
publication attempts. The separate enclosing launch counts this reader itself.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, subprocess, time
from fractions import Fraction as Q
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PREFIX='revisions/2026-10-20-r122/'
NATIVE='provenance122/runtime-recovery-39691016040-1/'
C='5635a3a0af330933b3ff1b9331ba4fe468eac628'
S='6ab1f9d4f1f9eb70014a7d104b84a499b64ba84c'
F='2f483615c8bc0037e43ec01a16cce05c724f8c60'
DRIVER='verification122/recover_after_runtime_reset122.py'
DRIVER_SHA='6270a71e0b8be2551838d4630c3691f51c9a5aed03fc277109f28120eb51353f'
LEDGER='verification122/research_cost_ledger122.py'
LEDGER_SHA='37efa69184cca24946aec4e6914de10c848509709f3b24e5d67edc4cc028e08c'
ARTIFACT_SHA='92ba7a1ec1584a50017e4fb49a1d695a1e2bc53dd526477ecffd0c43891c29cf'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def need(condition,message):
    if not condition:raise ValueError(message)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--custody-directory',required=True,type=Path)
    p.add_argument('--custody-source-commit',required=True)
    p.add_argument('--custody-publication-commit',required=True)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();tick=time.perf_counter();inputs={};checks=0
    out=a.output.resolve();custody=a.custody_directory.resolve()
    need(not out.exists() and out.is_relative_to(ROOT),'Output must be new and inside R122')
    need(custody.is_relative_to(ROOT/'provenance122') and custody.is_dir(),'New native custody prefix required')
    for c in (a.custody_source_commit,a.custody_publication_commit):need(len(c)==40 and all(x in '0123456789abcdef' for x in c),'Immutable custody commit required')
    def check(value,message):
        nonlocal checks
        need(value,message);checks+=1
    def bind(path):
        path=Path(path)
        check(path.resolve().is_relative_to(REPO) and path.is_file() and not path.is_symlink(),'Missing ordinary native input '+str(path))
        row=dict(path=path.relative_to(REPO).as_posix(),bytes=path.stat().st_size,sha256=sha(path))
        check(row['path'] not in inputs or inputs[row['path']]==row,'Input changed between reads')
        inputs[row['path']]=row;return path
    def read(path):return json.loads(bind(path).read_text())
    def relative(value):
        text=str(value)
        if PREFIX in text:text=text.split(PREFIX,1)[1]
        pure=PurePosixPath(text)
        check(not pure.is_absolute() and '..' not in pure.parts and pure.as_posix()==text,'Noncanonical R122 stage path')
        return ROOT/text
    def artifact_path(value):
        check(value.startswith(NATIVE),'Original admin prefix changed')
        return custody/'native'/value
    for name,expected,commit in ((DRIVER,DRIVER_SHA,S),(LEDGER,LEDGER_SHA,S)):
        b=bind(ROOT/name).read_bytes();check(hashlib.sha256(b).hexdigest()==expected and b==git('show',commit+':'+PREFIX+name),'Accounting source identity differs')
    extraction=read(custody/'EXTRACTION122.json')
    check(extraction['status']=='verified_complete_final_admin_snapshot','Custody extraction did not succeed')
    check(extraction['source_commit']==a.custody_source_commit and extraction['terminal_commit']==C,'Custody source/terminal identity differs')
    expected_artifact=dict(schema='nbo.r122.completed-artifact-custody.v1',run_id=39691016040,artifact_id=12391656973,artifact_bytes=630176089,artifact_sha256=ARTIFACT_SHA,experiment_source=S,terminal_commit=C)
    check(extraction['artifact']==expected_artifact,'Different original artifact')
    source_gate=read(custody/'SOURCE_GATE122.json')
    check(source_gate['status']=='verified_before_artifact_retrieval' and source_gate['source_commit']==a.custody_source_commit,'Custody source gate differs')
    expected_source_paths={PREFIX+'verification122/extract_recovery_artifact122.py',PREFIX+'provenance122/ARTIFACT_CUSTODY_PROTOCOL122.md',PREFIX+'ARTIFACT_CUSTODY_TRIGGER122.json','.github/workflows/nbo-r122-artifact-custody.yml'}
    check({r['path'] for r in source_gate['files']}==expected_source_paths and len(source_gate['files'])==4,'Incomplete custody source closure')
    for r in source_gate['files']:
        b=bind(REPO/r['path']).read_bytes()
        check((len(b),hashlib.sha256(b).hexdigest())==(r['bytes'],r['sha256']) and b==git('show',a.custody_source_commit+':'+r['path']),'Custody source is not published exact native bytes')
    # The source-bound extraction and every original member must be identical
    # to the newly published custody snapshot, not a text claim alone.
    check(bind(custody/'EXTRACTION122.json').read_bytes()==git('show',a.custody_publication_commit+':'+(custody/'EXTRACTION122.json').relative_to(REPO).as_posix()),'Extraction is not the published custody bytes')
    expected_native=set()
    for r in extraction['files']:
        original=PurePosixPath(r['original_path']);native=PurePosixPath(r['native_path'])
        check(not original.is_absolute() and '..' not in original.parts and original.as_posix().startswith(NATIVE),'Unsafe original member')
        target=ROOT/native
        check(target==custody/'native'/original,'Native custody mapping changed')
        check(str(target) not in expected_native,'Duplicate extracted member');expected_native.add(str(target))
        bind(target);check((target.stat().st_size,sha(target))==(r['bytes'],r['sha256']),'Native artifact member changed')
    check({str(x) for x in (custody/'native').rglob('*') if x.is_file()}==expected_native,'Incomplete/extra original admin members')
    meta=read(custody/'artifact-metadata.json');run=read(custody/'run-metadata.json')
    check(meta['id']==12391656973 and meta['size_in_bytes']==630176089 and meta['digest']=='sha256:'+ARTIFACT_SHA and not meta['expired'],'Original artifact metadata differs')
    check(run['id']==39691016040 and run['head_sha']==S and run['status']=='completed' and run['conclusion']=='success','Actual original source run did not succeed')
    old=read(ROOT/NATIVE/'RECOVERY_STATUS122.json')
    check((ROOT/NATIVE/'RECOVERY_STATUS122.json').read_bytes()==git('show',C+':'+PREFIX+NATIVE+'RECOVERY_STATUS122.json'),'Original Git C status changed')
    final=read(artifact_path(NATIVE+'RECOVERY_STATUS122.json'))
    check({k:v for k,v in old.items() if k!='publications'}=={k:v for k,v in final.items() if k!='publications'},'Terminal artifact changes more than the publication suffix')
    check(len(old['publications'])==10 and len(final['publications'])==11 and final['publications'][:10]==old['publications'],'Status/publication snapshots are inconsistent')
    check(final['status']=='completed_recovery_science_and_report' and final['source_commit']==S and final['source_commit_F']==F,'Actual science recovery identity differs')
    check(final['publications'][-1]['commit']==C,'Terminal custody publication differs')
    check(all(final[x]==0 for x in ('new_initial_states','new_training','new_primary_decisions','new_service_timing_replicates')),'This is not the fixed-state audit-only recovery')
    pubrows=[];pubobjects=[]
    for n,row in enumerate(final['publications'],1):
        expected=NATIVE+'CHECKPOINT'+str(n).zfill(3)+'_PUBLICATION122.json'
        check(row['path']==expected and sha(bind(artifact_path(expected)))==row['sha256'],'Publication path/hash changed')
        obj=read(artifact_path(expected));pubobjects.append(obj)
        check(obj['status']=='executed' and obj['commit']==row['commit'] and obj['source_commit_F']==F and obj['recovery_source_commit']==S and str(obj['workflow_run_id'])=='39691016040','Publication source/status differs')
        attempts=obj['publication_attempts'];check(bool(attempts) and attempts[-1]['status']=='published' and attempts[-1]['commit']==row['commit'],'Publication has no final successful attempt')
        total=Q(0)
        for attempt in attempts:
            check(attempt['status'] in ('failed','published') and Q(attempt['elapsed_seconds'])>=0,'Nonterminal/negative publication clock')
            check(sha(bind(artifact_path(attempt['log'])))==attempt['log_sha256'],'Publication log changed')
            if attempt['status']=='published':check(attempt['force'] is False and attempt['remote_readback_equal'] is True,'Publication was not a non-force read-back success')
            total+=Q(attempt['elapsed_seconds'])
        pubrows.append(dict(sequence=n,path=artifact_path(expected).relative_to(REPO).as_posix(),sha256=row['sha256'],commit=row['commit'],attempts=len(attempts),seconds_exact=str(total),enclosed_by_stopped_parent=n<=10))
    terminal_files={x['path']:x for x in pubobjects[-1]['publication_attempts'][-1]['files']}
    old_path=PREFIX+NATIVE+'RECOVERY_STATUS122.json'
    check(terminal_files[old_path]['sha256']==sha(ROOT/NATIVE/'RECOVERY_STATUS122.json'),'Final publication did not deliver the exact C pre-append status')
    launches=[];packs=[];stage_total=Q(0);all_labels=set()
    expected_launch_labels={'segment'+str(i).zfill(3) for i in range(1,9)}|{'cache'+str(i).zfill(3) for i in range(2,10)}|{'canonical','statistics','original-report','adapted-report'}
    for stage in final['stages']:
        label=stage['label'];check(label not in all_labels,'Duplicate recovery stage');all_labels.add(label)
        check(Q(stage['elapsed_seconds'])>=0 and sha(bind(artifact_path(stage['log'])))==stage['log_sha256'],'Stage clock/log changed')
        stage_total+=Q(stage['elapsed_seconds']);cmd=stage['command']
        if label in expected_launch_labels:
            check(cmd[1]=='code122/launch122.py' and '--receipt' in cmd and '--' in cmd,'Expected original child launcher')
            launcher_path=relative(cmd[cmd.index('--receipt')+1])/'LAUNCH122.json';launch=read(launcher_path)
            check(launch['command']==cmd[cmd.index('--')+1:] and launch['exit_code']==stage['exit_code'],'Stage/child command or exit differs')
            check(launch['status'] in ('executed','failed') and Q(launch['outer_seconds'])>=0 and Q(launch['outer_seconds'])<=Q(stage['elapsed_seconds']),'Stage does not enclose its saved child clock')
            outer_path=relative(launch['child_output'])/'OUTER_EXECUTION122.json'
            check(bind(outer_path).read_bytes()==bind(launcher_path).read_bytes(),'Saved outer mirror changed')
            launches.append(dict(label=label,path=launcher_path.relative_to(REPO).as_posix(),sha256=sha(launcher_path),seconds_exact=str(Q(launch['outer_seconds'])),auto_counted_by_frozen_ledger=True))
        if label.startswith('bundle-'):
            n=int(label.split('-')[1]);check(1<=n<=10 and cmd[1]=='verification122/make_evidence_bundle122.py','Unexpected packing stage')
            req_path=relative(cmd[cmd.index('--bundle')+1])/'REQUEST122.json';request=read(req_path)
            pub_files={x['path']:x for x in pubobjects[n-1]['publication_attempts'][-1]['files']}
            name=req_path.relative_to(REPO).as_posix();check(name in pub_files and sha(req_path)==pub_files[name]['sha256'],'Packer receipt differs from its actual checkpoint')
            seconds=Q(request['actual_publication_work_seconds']);check(0<=seconds<=Q(stage['elapsed_seconds']),'Pack inner clock exceeds enclosing stage')
            packs.append(dict(label=label,path=name,sha256=sha(req_path),seconds_exact=str(seconds),auto_counted_by_frozen_ledger=True))
    check({x['label'] for x in launches}==expected_launch_labels and len(launches)==20 and len(packs)==10,'Incomplete already-counted child/pack census')
    parent=Q(final['orchestrator_elapsed_seconds']);children=sum((Q(x['seconds_exact']) for x in launches),Q(0));packing=sum((Q(x['seconds_exact']) for x in packs),Q(0))
    previous_publications=sum((Q(x['seconds_exact']) for x in pubrows[:10]),Q(0));terminal=Q(pubrows[-1]['seconds_exact'])
    check(parent>=stage_total+previous_publications,'Parent does not enclose serial stage/publication intervals')
    residual=parent-children-packing;check(residual>=0,'Negative parent residual')
    bridge=residual+terminal
    check(children+packing+bridge==parent+terminal,'Exact nonoverlapping reconciliation failed')
    for row in inputs.values():
        q=REPO/row['path'];check(q.stat().st_size==row['bytes'] and sha(q)==row['sha256'],'Input changed before accounting completed')
    result=dict(status='verified_completed_recovery_cost_bridge',created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),reader_sha256=sha(Path(__file__)),assertions=checks,
        source_commit_S=S,delivery_commit_C=C,custody_source_commit=a.custody_source_commit,custody_publication_commit=a.custody_publication_commit,original_artifact_sha256=ARTIFACT_SHA,
        actual_parent_seconds_exact=str(parent),already_counted_child_outer_seconds_exact=str(children),already_counted_pack_inner_seconds_exact=str(packing),
        enclosing_stage_seconds_exact=str(stage_total),preceding_publication_attempt_seconds_exact=str(previous_publications),
        parent_residual_seconds_exact=str(residual),terminal_publication_attempt_seconds_exact=str(terminal),nonoverlapping_recovery_bridge_seconds_exact=str(bridge),
        actual_parent_plus_terminal_observed_seconds_exact=str(parent+terminal),
        child_launches=launches,packers=packs,publications=pubrows,input_files=sorted(inputs.values(),key=lambda x:x['path']),elapsed_seconds=time.perf_counter()-tick,
        cost_clock_components=[dict(category='recovery_parent_residual_and_terminal_publication',clock_fields=[['nonoverlapping_recovery_bridge_seconds_exact']],partial_lower_bound_only=True,overlaps_counted_parent=False,
            scope='Actual S parent minus only 20 auto-counted launch clocks and 10 auto-counted pack inner clocks, plus terminal publication11 attempts after the parent stopped. Includes earlier publication failures, source hydration, cache work, saved gates and wrappers; their inner clocks must not be added again.')],
        reader_clock_scope='Charge this reader only through its separate original launcher; elapsed_seconds is nested and is not an additional bridge component.',
        no_prior_interrupted_evaluator_clock_recharged=True,new_economic_evaluations=0,new_states=0,new_training=0,new_service_timing_processes=0,whole_study_exact_seconds=None,
        unmeasured_scope=['Original primary and independent interrupted parents remain unknown','Terminal publication preparation outside its attempt clock and final receipt writing','Workflow checkout/setup/artifact uploads and unclocked lost administrative work','Subsequent custody/release work is separate'],
        scope='New administrative reconstruction from exact published current run receipts. No prior lost reader identity, unavailable older completion, economic result, timing observation or confidence statement is reconstructed.')
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x') as stream:json.dump(result,stream,sort_keys=True,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({k:result[k] for k in ('status','assertions','parent_residual_seconds_exact','terminal_publication_attempt_seconds_exact','nonoverlapping_recovery_bridge_seconds_exact')},indent=2))
if __name__=='__main__':main()
