"""Read-only census of recorded R122 research and publication job clocks.

This is an additive reporting reader, not an economic experiment. Complete
outer scientific clocks enclose their timing children. Separate QA/build/
transport clocks are counted once. The interrupted parent has no terminal
clock; its measured nonoverlapping cohort sum is only a lower bound. Unclocked
work is not assigned zero and the whole-study exact total remains unavailable.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, sys, time
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def value_at(obj,fields):
    for field in fields:obj=obj[field]
    return obj

def local_path(value):
    p=Path(value)
    if p.is_relative_to(ROOT):return p
    marker='revisions/2026-10-20-r122/'
    if marker in str(value):return ROOT/str(value).split(marker,1)[1]
    return p

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-commit',required=True);ap.add_argument('--state-commit',required=True)
    ap.add_argument('--additional-receipts',nargs='*',type=Path,default=[])
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    started=time.perf_counter();inputs={};rows=[];excluded=[];unknown=[];seen=set();outer_roots=[]
    def read(p):
        p=Path(p).resolve()
        if not p.is_relative_to(REPO):raise ValueError('Move the custody receipt into the repository before cost reporting: '+str(p))
        relative=str(p.relative_to(REPO))
        inputs[relative]={'path':relative,'bytes':p.stat().st_size,'sha256':digest(p)}
        return json.loads(p.read_text())
    def add(p,obj,category,fields,scope,partial=False):
        p=Path(p).resolve();fingerprint=(digest(p),tuple(tuple(x) for x in fields))
        if fingerprint in seen:
            excluded.append({'path':str(p.relative_to(REPO)),'reason':'Exact duplicate saved clock receipt already counted'})
            return
        seen.add(fingerprint);seconds=sum((Q(value_at(obj,f)) for f in fields),Q(0))
        if seconds<0:raise ArithmeticError('Negative saved clock')
        rows.append({'source_path':str(p.relative_to(REPO)),'source_sha256':digest(p),
            'category':category,'status':obj.get('status','recorded'),
            'clock_fields':fields,'seconds_exact':str(seconds),
            'clock_scope':scope,'component_lower_bound_only':partial,
            'scientific_standalone_service_allocation_changed':False})
    def enclosed(p):
        return any(Path(p).resolve().is_relative_to(q) for q in outer_roots)
    # Include all completed success/failure launches. OUTER_EXECUTION mirrors
    # and nested timing launcher receipts are not independent charges.
    launch_paths=sorted(set((ROOT/'results122').rglob('LAUNCH122.json')) |
                        set((ROOT/'provenance122/review').rglob('LAUNCH122.json')))
    for p in launch_paths:
        obj=read(p)
        if 'outer_seconds' in obj:
            name=p.parent.name
            if obj.get('status') not in ('executed','failed') or 'exit_code' not in obj:
                raise ValueError('Nonterminal launch presented as complete: '+str(p))
            category='scientific_stage_outer' if any(s in name for s in ('states-','primary-','independent-','statistics-')) else 'reporting_stage_outer' if 'report-' in name else 'administrative_or_qa_outer'
            add(p,obj,category,[['outer_seconds']],obj.get('clock_scope','Saved external child spawn-to-exit clock'))
            if obj.get('child_output'):outer_roots.append(local_path(obj['child_output']).resolve())
        elif 'seconds' in obj:
            add(p,obj,'administrative_or_qa_outer',[['seconds']],obj.get('scope','Saved administrative execution clock'))
        else:unknown.append({'path':str(p.relative_to(REPO)),'reason':'Launch receipt has no numerical elapsed clock; no zero is imputed'})
    # The original parent never completed. Its serial completed cohorts are
    # observed work inside that missing clock, not a substitute full duration.
    interrupted=ROOT/'results122/primary-attempt01'
    forensic_path=interrupted/'INTERRUPTION_FORENSIC122.json';forensic=read(forensic_path)
    if forensic['source_commit']!=a.source_commit or forensic['state_commit']!=a.state_commit:
        raise ValueError('Ledger F/D differs from actual interrupted scientific identities')
    if forensic['exit_code'] is not None or forensic['actual_full_external_wall_seconds'] is not None:
        raise ValueError('Interrupted parent duration/status was invented')
    if (interrupted/'OUTER_EXECUTION122.json').exists() or (ROOT/'results122/launch-primary-attempt01/LAUNCH122.json').exists():
        raise ValueError('Unexpected terminal receipt for interrupted parent')
    interruption_lower=Q(0);interruption_sources=[]
    for relative in ('cohorts122.jsonl','timing/attempt00/cohorts122.jsonl','timing/attempt01/cohorts122.jsonl'):
        p=interrupted/relative
        expected=next(r for r in forensic['files'] if r['path']==relative)
        if digest(p)!=expected['sha256'] or p.stat().st_size!=expected['bytes']:raise ValueError('Changed interrupted cohort bytes')
        saved=[json.loads(s) for s in p.read_text().splitlines()]
        subtotal=sum((Q(z['complete_cohort_seconds']) for z in saved),Q(0));interruption_lower+=subtotal
        path=str(p.relative_to(REPO));inputs[path]={'path':path,'bytes':p.stat().st_size,'sha256':digest(p)}
        interruption_sources.append({'path':path,'sha256':digest(p),'cohorts':len(saved),'recorded_seconds_exact':str(subtotal)})
    unknown.append({'path':str(interrupted.relative_to(REPO)),'reason':'Original parent external clock and exit status unavailable; completed nonoverlapping cohorts only supply a lower bound','observed_seconds_lower':str(interruption_lower),'full_outer_seconds':None})
    # Read all local additive verifier attempts, including recorded failures.
    for directory in (ROOT/'verification122',ROOT/'verification_runs122'):
        for pattern in ('VERIFICATION122.json','FAILURE_VERIFICATION122.json'):
            for p in sorted(directory.rglob(pattern)):
                obj=read(p)
                if enclosed(p):excluded.append({'path':str(p.relative_to(REPO)),'reason':'Verifier inner clock enclosed by a counted outer launch'})
                else:add(p,obj,'saved_evidence_verification',[['elapsed_seconds']],'Recorded read-only verifier inner elapsed clock; process startup and final receipt serialization excluded',True)
    review=ROOT/'provenance122/review'
    for name in ('REPORTER_COMPLETE_SCHEMA_ORIGINAL_FAILURE122.json','REPORTER_COMPLETE_SCHEMA_ADAPTED_EXECUTION122.json','REPORTER_COMPLETE_SCHEMA_STATISTICS_EXECUTION122.json'):
        p=review/name;obj=read(p)
        add(p,obj,'artificial_reporter_qa_inner',[['seconds']],'Recorded inner stage of the artificial complete-schema fixture; zero original economic calls, no enclosing fixture clock retained',True)
    unclocked=set(review.glob('*_QA*.json')) | set(review.glob('REPORTER*RESULT122.json')) | set(review.glob('INFERENCE_PROOF122.json')) | set((review/'prefreeze-synthetic122').rglob('FAILURE122.json'))
    for p in sorted(unclocked):
        obj=read(p)
        if 'elapsed_seconds' in obj:add(p,obj,'source_or_artificial_qa_inner',[['elapsed_seconds']],'Saved source/artificial QA inner elapsed clock',True)
        elif 'seconds' in obj:add(p,obj,'source_or_artificial_qa_inner',[['seconds']],'Saved source/artificial QA inner elapsed clock',True)
        else:unknown.append({'path':str(p.relative_to(REPO)),'reason':'Actual source/artificial QA receipt has no elapsed clock; no zero is imputed'})
    # Compiler commands are serial within each build; diagnostics and failed
    # builds remain included. Their sum excludes source scanning/wrapper work.
    for directory in sorted(ROOT.glob('build_receipts122*')):
        for p in sorted(directory.rglob('BUILD_RECEIPT122.json')):
            obj=read(p);fields=[['commands',j,'elapsed_seconds'] for j,r in enumerate(obj['commands']) if 'elapsed_seconds' in r]
            if enclosed(p):excluded.append({'path':str(p.relative_to(REPO)),'reason':'Build inner command clocks enclosed by a counted outer launch'})
            elif fields:add(p,obj,'document_build_commands',fields,'Sum of saved serial TeX/BibTeX command elapsed clocks; successful, diagnostic and failed commands retained',True)
            if any('elapsed_seconds' not in r for r in obj['commands']):unknown.append({'path':str(p.relative_to(REPO)),'reason':'Started build command lacks terminal elapsed clock'})
    # Packing and materialization clocks are publication work, never economic
    # service costs. Distinct actual attempts are counted even when bytes match.
    for p in sorted((ROOT/'transport122').rglob('REQUEST122.json')):
        obj=read(p)
        if 'actual_publication_work_seconds' in obj:add(p,obj,'lossless_evidence_packing',[['actual_publication_work_seconds']],'Recorded pack/hash/split inner job clock; network publication excluded',True)
    for p in sorted((ROOT/'verification_runs122').rglob('*.json')):
        obj=read(p)
        if obj.get('status')=='verified_materialization':
            fields=[['bundles',j,'seconds'] for j in range(len(obj['bundles']))]
            if enclosed(p):excluded.append({'path':str(p.relative_to(REPO)),'reason':'Materialization clock enclosed by counted outer launch'})
            elif fields:add(p,obj,'lossless_evidence_materialization',fields,'Sum of serial saved bundle verification/materialization inner clocks',True)
    # Prior ledger snapshots are not scientific work and their totals must not
    # be added again. Only the duration of each previous census itself counts.
    for p in sorted((ROOT/'results122').rglob('COST_LEDGER122.json')):
        obj=read(p)
        if enclosed(p):excluded.append({'path':str(p.relative_to(REPO)),'reason':'Previous ledger reader clock enclosed by counted outer launch'})
        else:add(p,obj,'cost_ledger_reader',[['census_elapsed_seconds']],'Only the previous read-only ledger job clock; no previous aggregate is counted twice',True)
    # Additional native custody receipts must declare exactly which numerical
    # fields form nonoverlapping clocks. This accommodates partial publication
    # API readback records without fabricating coverage of all historical pushes.
    for p in a.additional_receipts:
        obj=read(p)
        for r in obj.get('cost_clock_components',[]):
            if r.get('overlaps_counted_parent',False):
                excluded.append({'path':str(Path(p).resolve().relative_to(REPO)),'reason':r['scope']})
            else:add(p,obj,r['category'],r['clock_fields'],r['scope'],r.get('partial_lower_bound_only',True))
        if not obj.get('cost_clock_components'):unknown.append({'path':str(Path(p).resolve().relative_to(REPO)),'reason':'No declared nonoverlapping numerical clock fields; receipt retained without imputing cost'})
    recorded=sum((Q(r['seconds_exact']) for r in rows),Q(0))
    categories={k:str(sum((Q(r['seconds_exact']) for r in rows if r['category']==k),Q(0))) for k in sorted({r['category'] for r in rows})}
    elapsed=time.perf_counter()-started
    result={'status':'saved_receipt_cost_census','source_commit':a.source_commit,'state_commit':a.state_commit,
        'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'reader_sha256':digest(__file__),'actual_command':sys.argv,
        'clock_rows':rows,'category_sums_seconds_exact':categories,
        'recorded_nonoverlapping_job_seconds_sum':str(recorded),
        'interrupted_completed_cohort_seconds_lower':str(interruption_lower),
        'interrupted_cohort_sources':interruption_sources,
        'recorded_job_sum_plus_interruption_lower':str(recorded+interruption_lower),
        'census_elapsed_seconds':elapsed,
        'observed_research_and_publication_job_seconds_lower_including_this_census':str(recorded+interruption_lower+Q(elapsed)),
        'complete_interrupted_parent_outer_seconds':None,'whole_study_exact_total_seconds':None,
        'whole_study_exact_total_unavailable':True,
        'excluded_nested_or_duplicate_clocks':excluded,'unavailable_or_unclocked':unknown,
        'known_additional_unclocked_scope':['Unmeasured source preparation, reading, discussion and orchestration','Publication operations without a retained full job clock','Startup and final receipt-writing overhead excluded from explicitly inner-only QA/publication clocks','Any later verification/build/CI/publication after this timestamp'],
        'historical_actor_acquisition':'Immutable prior R121 complete per-standalone allocations remain in the scientific comparison. R122 fits no new actor; summing all standalone allocations is not a measured new R122 research bill.',
        'measurement_scope':'Summed recorded job-wall seconds on the observed shared host, not dedicated-hardware speed, project critical-path duration, CPU-seconds or a monetary bill. Nested children and shared adapter clocks are excluded from double counting.',
        'standalone_scientific_service_allocation_unchanged':True,
        'new_states':0,'new_training':0,'new_economic_evaluations':0,'new_timing_processes':0,
        'original_interruption_or_frozen_report_success_asserted':False}
    for name,obj in (('INPUTS_COST_LEDGER122.json',{'files':sorted(inputs.values(),key=lambda r:r['path'])}),('COST_LEDGER122.json',result)):
        with (out/name).open('x') as f:json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
    print(json.dumps({k:result[k] for k in ('status','recorded_nonoverlapping_job_seconds_sum','interrupted_completed_cohort_seconds_lower','recorded_job_sum_plus_interruption_lower','whole_study_exact_total_seconds')},indent=2))

if __name__=='__main__':main()
