"""All registered critic-reuse outcomes, with complete finite-family inference."""
from __future__ import annotations
import argparse
from decimal import Decimal,ROUND_CEILING,ROUND_FLOOR,localcontext
import json
from pathlib import Path
import sys
import numpy as np

sys.dont_write_bytecode=True
from menu_pipeline import (R16,PROTOCOL,METHODS,trials,validate_protocol,
    require,read,write,sha,canonical,digest,inventory)
from menu_economy import fixed_queries,load_economy,array_hash,canonical_hash,stream_seed
import menu_verify as verify

LABELS=dict(nbo_scalar='NBO',vector_costate='Vector',raw_actor='Raw actor',dpo_actor='DPO',raw_saa='Cached SAA')
CALIB=dict(original_low='Original',quarterly_reuse='Quarterly',long_reuse='Long',untouched_intermediate='Intermediate')

def number(x,digits=6,side=None):
    with localcontext() as ctx:
        ctx.prec=70;v=Decimal.from_float(float(x))
        if side:v=v.quantize(Decimal(10)**-digits,rounding=ROUND_FLOOR if side=='lower' else ROUND_CEILING)
        return f'{v:.{digits}f}'

def interval(row,digits=5,scale=1.):
    return '['+number(row['lower']*scale,digits,'lower')+', '+number(row['upper']*scale,digits,'upper')+']'

def table(caption,label,cols,header,rows,notes,*,long=False):
    opening=(r'\begin{longtable}{'+cols+'}\n'+r'\caption{'+caption+'}'+r'\label{'+label+r'}\\'+'\n') if long else (
        r'\begin{table}[!htbp]'+'\n'+r'\centering\footnotesize'+'\n'+r'\caption{'+caption+'}'+r'\label{'+label+'}\n'+r'\begin{tabular}{'+cols+'}\n')
    top=r'\toprule'+'\n'+header+r' \\'+'\n'+r'\midrule'+'\n'
    if long:top+=r'\endfirsthead'+'\n'+r'\toprule'+'\n'+header+r' \\'+'\n'+r'\midrule\endhead'+'\n'
    ending=r'\bottomrule'+'\n'+(r'\end{longtable}' if long else r'\end{tabular}')+'\n'
    ending+=r'\begin{minipage}{0.97\linewidth}\footnotesize\emph{Notes:} '+notes+'\n'+r'\end{minipage}'+'\n'
    if not long:ending+=r'\end{table}'+'\n'
    return opening+top+'\n'.join(rows)+'\n'+ending

def cost_record(folder,trial,method,stage):
    """Keep actual bundle clocks separate from explicit prefix allocations."""
    folder=Path(folder);fit=read(folder/'fits'/method/'FIT_WORK.json')
    rows={j:read(folder/'fits'/method/f'stage{j}.json') for j in [1,2,3]}
    outer=trial['method_process_work'][method]['end_to_end_seconds']
    inner=fit['complete_fit_seconds'];prefix=rows[stage]['parent_prefix_seconds']
    overhead=max(0.,outer-inner)
    finalization=max(0.,inner-rows[3]['parent_prefix_seconds'])
    construction=outer if stage==3 else prefix+overhead+finalization
    confirmation=trial['confirmation_process_work']['end_to_end_seconds']
    return dict(method=method,stage=stage,actual_all_stage_fit_process_seconds=outer,
        saved_candidate_prefix_seconds=prefix,outer_startup_and_finalization_seconds=overhead,
        inner_finalization_seconds=finalization,construction_and_query_seconds=construction,
        construction_clock_is_actual_complete_process=stage==3,
        prefix_allocation_scope='Earlier saved prefix plus all outer overhead and final-stage finalization; conservative accounting allocation, not a separate early-stopping process measurement',
        complete_shared_confirmation_process_seconds=confirmation,
        conservative_construction_plus_full_audit_seconds=construction+confirmation,
        confirmation_cost_scope='All three stages, five methods, common reference and scalar accuracy form one measured audit bundle. Charging this whole bundle to a single method gives the disclosed conservative accounting total; no one-fifth cost fiction.',
        failed_fit=fit['failed_fit'],fallback=rows[stage]['fallback'],counters=rows[stage].get('counters',{}),
        counters_complete=fit['counters_complete'],counter_scope=fit['counter_scope'],
        source_verification_exclusion_from_inner_clock=fit.get('clock_scope'),
        cpu_seconds=trial['method_process_work'][method]['cpu_seconds'],
        peak_rss_kib=trial['method_process_work'][method]['peak_rss_kib'])

def render(repo,results,out):
    repo=Path(repo).resolve();results=Path(results).resolve();out=Path(out).resolve()
    p=read(repo/PROTOCOL);validate_protocol(p);proto_sha=sha(repo/PROTOCOL)
    source_manifest_path=results.parent/'SOURCE_MANIFEST.json'
    source_manifest=read(source_manifest_path) if source_manifest_path.is_file() else None
    transport_receipts={}
    expected=trials(p);expected_by_id={t['trial_id']:t for t in expected}
    found={};sources=set();fingerprints=set();observed_noise=set();raw_hashes={};record_hashes={}
    for f in sorted(results.rglob('TRIAL.json')):
        r=read(f);ident=r['trial']['trial_id'];require(ident in expected_by_id and ident not in found,'undeclared or repeated trial')
        require(r['complete'] and r['trial']==expected_by_id[ident] and r['protocol_sha256']==proto_sha,'incomplete trial or protocol mismatch')
        if (f.parent/'TRANSPORT_RECEIPT.json').is_file():
            from menu_transport import verify_analysis_trial
            require(source_manifest is not None,'transported analysis requires the immutable source manifest')
            transport_receipts[ident]=verify_analysis_trial(f.parent,source_manifest)
        else:
            require(inventory(f.parent,exclude=['TRIAL.json'])==r['files'],'trial evidence inventory differs')
        require(not r['final_confirmation_used_for_selection'] and r['all_fitting_finished_before_confirmation'],'invalid sample separation')
        sources.add(r['numerical_source_commit']);fingerprints.add(r['assessment_fingerprint'])
        c=r['trial']['calibration'];d=r['trial']['dimension'];seed=r['trial']['stream_seed']
        economy=load_economy(p,c,d);queries=fixed_queries(p,d);stage_data={}
        for stage in [1,2,3]:
            path=f.parent/'confirmation'/f'stage{stage}.json';record=read(path)
            for key,value in [('complete',True),('calibration',c),('dimension',d),('stream_seed',seed),('stage',stage),('source_commit',r['numerical_source_commit']),('protocol_file_sha256',proto_sha),('query_count',384),('pairs_per_query',512)]:
                require(record.get(key)==value,'confirmation identity differs: '+key)
            require(record['continuation_sha256']==economy.continuation_sha256 and record['query_catalog_sha256']==queries['catalog_sha256'],'different continuation or fixed query population')
            require(record['protocol_sha256']==canonical_hash(p),'canonical scientific protocol differs')
            require(record['noise_seed']==stream_seed(seed,c,d,'independent_final_payoff',stage),'new payoff noise domain differs')
            require(record['noise_domain'] not in observed_noise,'confirmation domain reused');observed_noise.add(record['noise_domain'])
            raw=path.parent/record['raw_file'];require(sha(raw)==record['raw_sha256'],'raw confirmation changed')
            with np.load(raw,allow_pickle=False) as z:arrays={k:z[k] for k in z.files}
            account=verify.verify_event_accounts(economy,queries,{m:arrays['actions_'+m] for m in METHODS},p,stage=stage)
            for key,value in account.items():
                require(canonical(record[key])==canonical(value),'independent deterministic primary account replay differs: '+key)
            for method in METHODS:
                fitdir=f.parent/'fits'/method;fit_work=read(fitdir/'FIT_WORK.json')
                require(fit_work['method']==method and fit_work['calibration']==c and fit_work['dimension']==d and fit_work['seed']==seed,'fitted method or complete stream identity differs')
                stage_record=read(fitdir/f'stage{stage}.json');action_path=fitdir/stage_record['actions_file']
                require(stage_record['schema']=='nbo-r16-menu-sealed-stage-v1' and stage_record['sealed'] is True,'unsealed fitted stage')
                require(stage_record['method']==method and stage_record['calibration']==c and stage_record['dimension']==d and stage_record['seed']==seed and stage_record['source_commit']==r['numerical_source_commit'],'sealed stage belongs to another source or trial')
                require(sha(action_path)==stage_record['actions_sha256'],'fitted action evidence changed')
                with np.load(action_path,allow_pickle=False) as z:
                    require(np.array_equal(z['actions'],arrays['actions_'+method]),'confirmation did not use saved stage action')
                    require(array_hash(z['actions'])==record['action_sha256'][method],'confirmed action array hash differs')
                require(array_hash(arrays['quadratic_center_'+method])==record['quadratic_center_sha256'][method],'known continuation center changed')
            stage_data[stage]=(record,arrays)
            raw_hashes[f'{ident}/stage{stage}']=record['raw_sha256'];record_hashes[f'{ident}/stage{stage}']=sha(path)
        scalar_path=f.parent/'confirmation'/'scalar.json';scalar=read(scalar_path)
        require(scalar['complete'] and scalar['calibration']==c and scalar['dimension']==d and scalar['stream_seed']==seed,'incomplete scalar event')
        require(scalar['source_commit']==r['numerical_source_commit'] and scalar['protocol_file_sha256']==proto_sha and scalar['protocol_sha256']==canonical_hash(p),'scalar source identity differs')
        require(scalar['independent_antithetic_pairs']==65536 and scalar['continuation_sha256']==economy.continuation_sha256,'scalar model or bank precision differs')
        require(canonical(scalar['candidate'])==canonical(read(f.parent/'fits'/'nbo_scalar'/'SCALAR_CANDIDATE.json')),'scalar confirmation candidate differs from the durable fitted selection')
        require(scalar['noise_seed']==stream_seed(seed,c,d,'independent_scalar_accuracy',3),'scalar noise domain differs')
        require(scalar['noise_domain'] not in observed_noise,'scalar bank reused');observed_noise.add(scalar['noise_domain'])
        scalar_raw=scalar_path.parent/scalar['raw_file'];require(sha(scalar_raw)==scalar['raw_sha256'],'scalar raw evidence changed')
        with np.load(scalar_raw,allow_pickle=False) as z:scalar_arrays={k:z[k] for k in z.files}
        require(scalar_arrays['scalar_secant_residual'].shape==(65536,) and np.isfinite(scalar_arrays['scalar_secant_residual']).all(),'scalar independent-pair array incomplete')
        replay=verify.replay_scalar(economy,None,scalar['candidate'],p,seed=seed,raw_arrays=scalar_arrays)
        for key,value in replay.items():
            require(canonical(scalar[key])==canonical(value),'independent scalar endpoint replay differs: '+key)
        require(scalar['confidence_family']['alpha']==.002 and scalar['confidence_family']['event_count']==128,'scalar confidence family changed')
        raw_hashes[f'{ident}/scalar']=scalar['raw_sha256'];record_hashes[f'{ident}/scalar']=sha(scalar_path)
        found[ident]=dict(trial=r,path=f.parent,stages=stage_data,scalar=scalar)
    require(set(found)==set(expected_by_id),'every fixed stream is required')
    require(len(sources)==len(fingerprints)==1,'mixed numerical sources')
    full_raw_proof=None
    if transport_receipts:
        from menu_transport import assert_transport_tree
        saved=read(results.parent/'FULL_PAYLOAD_GIT_AUDIT.json')
        full_raw_proof=assert_transport_tree(repo,saved['staging_commit'],transport_receipts,source_manifest)
        require(canonical(saved)==canonical(full_raw_proof),'complete remote raw audit differs')
    report=dict(schema='nbo-r16-continuation-menu-report-v1',complete=True,
        numerical_source_commit=next(iter(sources)),assessment_fingerprint=next(iter(fingerprints)),
        protocol_sha256=proto_sha,primary_event_count=216,scalar_event_count=128,
        trial_count=128,method_fits=640,stage_candidates=1920,primary_confidence=dict(family_alpha=.018,event_count=216),
        scalar_confidence=dict(family_alpha=.002,event_count=128),total_menu_alpha=.02,
        estimand='Complete uniform distribution on 16 fixed training streams and 384 fixed current intervention queries, followed by the same future reference policy',
        scalar_scope='One fixed query per calibration and dimension; whole prescribed scalar action segment in the finite economy',
        continuous_time_or_full_vector_near_optimality_claim=False,
        calibrations=p['calibrations'],all_stages={},scalar_events={},work={},raw_hashes=raw_hashes,record_hashes=record_hashes,
        economic_margin=.0001,no_stage_or_stream_selection=True)
    report['full_raw_git_audit']=full_raw_proof
    fullrows=[];gainrows=[];mainrows=[];workrows=[];allworkrows=[];scalarrows=[];allscalarrows=[]
    event_count=0;decisions={m:dict(positive=0,materially_superior=0,negative=0,equivalent=0,total=0) for m in METHODS[1:]}
    for c in p['calibrations']:
        cal=c['id']
        for d in p['dimensions']:
            cell=f'{cal}_d{d}';items=[found[f'{cal}_d{d}_s{s}'] for s in p['training_streams']['seeds']]
            report['all_stages'][cell]={};report['work'][cell]={}
            for stage in [1,2,3]:
                pairs=[x['stages'][stage] for x in items]
                endpoints={name:verify.pooled_event(pairs,p,name) for name,_,_ in verify.events()}
                event_count+=len(endpoints);report['all_stages'][cell][str(stage)]=endpoints
                for name,left,right in verify.events():
                    e=endpoints[name];display=LABELS[left] if right=='reference' else 'NBO $-$ '+LABELS[right]
                    fullrows.append(' & '.join([CALIB[cal],str(d),str(stage),display,number(e['mean'],7),number(e['lower'],7,'lower'),number(e['upper'],7,'upper')])+r' \\')
                wr={}
                for method in METHODS:
                    records=[cost_record(x['path'],x['trial'],method,stage) for x in items]
                    wr[method]=dict(complete_stream_records=records,
                        mean_construction_and_query_seconds=float(np.mean([z['construction_and_query_seconds'] for z in records])),
                        mean_actual_all_stage_fit_process_seconds=float(np.mean([z['actual_all_stage_fit_process_seconds'] for z in records])),
                        mean_complete_shared_confirmation_seconds=float(np.mean([z['complete_shared_confirmation_process_seconds'] for z in records])),
                        mean_conservative_construction_plus_full_audit_seconds=float(np.mean([z['conservative_construction_plus_full_audit_seconds'] for z in records])),
                        fallback_streams=sum(z['fallback'] for z in records),failed_fit_streams=sum(z['failed_fit'] for z in records))
                    allworkrows.append(' & '.join([CALIB[cal],str(d),str(stage),LABELS[method],number(wr[method]['mean_construction_and_query_seconds'],2),str(wr[method]['fallback_streams'])])+r' \\')
                report['work'][cell][str(stage)]=wr
                for other in METHODS[1:]:
                    e=endpoints['nbo_minus_'+other];z=decisions[other];z['total']+=1
                    z['positive']+=int(e['lower']>0);z['materially_superior']+=int(e['lower']>=.0001)
                    z['negative']+=int(e['upper']<0);z['equivalent']+=int(e['lower']>=-.0001 and e['upper']<=.0001)
                if stage==3:
                    mainrows.append(' & '.join([CALIB[cal],str(d)]+[interval(endpoints['nbo_minus_'+m],2,1e4) for m in METHODS[1:]])+r' \\')
                    for method in METHODS:
                        e=endpoints[method+'_gain']
                        gainrows.append(' & '.join([CALIB[cal],str(d),LABELS[method],number(e['mean'],7),number(e['lower'],7,'lower'),number(e['upper'],7,'upper')])+r' \\')
                    workrows.append(' & '.join([CALIB[cal],str(d)]+[number(wr[m]['mean_actual_all_stage_fit_process_seconds'],2) for m in METHODS])+r' \\')
            scalars=[x['scalar'] for x in items];gaps=[z['implemented_candidate_gap_upper'] for z in scalars]
            report['scalar_events'][cell]=dict(events=scalars,attained=sum(z['accuracy_at_margin'] for z in scalars),streams=16,
                largest_gap_upper=max(gaps),smallest_gap_upper=min(gaps),strong_concavity_verified=sum(z['curvature']['strong_concavity_verified'] for z in scalars))
            scalarrows.append(' & '.join([CALIB[cal],str(d),str(report['scalar_events'][cell]['attained'])+'/16',number(min(gaps),7,'upper'),number(max(gaps),7,'upper')])+r' \\')
            for z in scalars:
                allscalarrows.append(' & '.join([CALIB[cal],str(d),str(z['stream_seed']),number(z['candidate']['candidate_s'],5),number(z['gradient_interval'][0],7,'lower'),number(z['gradient_interval'][1],7,'upper'),number(z['implemented_candidate_gap_upper'],7,'upper')])+r' \\')
    require(event_count==216 and sum(v['streams'] for v in report['scalar_events'].values())==128,'protected event count differs')
    report['all_stage_direct_decisions']=decisions
    report['total_failed_method_fits']=sum(read(x['path']/'fits'/m/'FIT_WORK.json')['failed_fit'] for x in found.values() for m in METHODS)
    out.mkdir(parents=True,exist_ok=True);write(out/'REPORT.json',report);outputs={}
    def save(name,text):
        (out/name).write_text(text);outputs[name]=sha(out/name)
    common=(r'Every cell averages all sixteen declared streams and all 384 fixed current-period queries. Each query has 512 independent antithetic future pairs; opposite signs form one observation. Five methods share each pair. All three stages and all eight economic-dimension cells contribute to one 216-event family with error probability $0.018$. Current reward and a known terminal quadratic are removed before the random residual is bounded. The mean column is the clipped residual estimator plus this known offset. Numerical arithmetic, clipping and the unclipped Gaussian law are included. The materiality margin is $10^{-4}$.')
    save('table_menu_comparisons.tex',table('Incremental Value of the Reusable NBO Continuation','tab:r16menucomparisons','llrrrr',r'Economy & $d$ & NBO $-$ Vector & NBO $-$ Raw actor & NBO $-$ DPO & NBO $-$ SAA',mainrows,
        r'Intervals are in units of $10^{-4}$ and use the final, third work stage. '+common))
    save('table_menu_work.tex',table('Complete Construction and Query Work','tab:r16menuwork','llrrrrr',r'Economy & $d$ & NBO & Vector & Raw actor & DPO & Cached SAA',workrows,
        r'Seconds per stream, averaged over all sixteen streams, including unsuccessful fits. Each entry is the actual outer-process clock for all three stages, imports, source checks, reusable training data, optimizer and derivative work, all saved queries and durable output. Fixed dependency installation and source extraction precede the clock. Independent confirmation is a shared measured bundle, reported separately in the complete account; the table does not allocate one-fifth of that bundle as an observed standalone verification cost.'))
    save('table_menu_scalar.tex',table('Conditional Accuracy on the Prescribed Scalar Intervention','tab:r16menuscalar','llrrr',r'Economy & $d$ & Gap $\leq10^{-4}$ & Smallest gap bound & Largest gap bound',scalarrows,
        r'All 128 conditional statements are retained under a separate error probability of $0.002$, with 65,536 independent antithetic pairs for each fixed scalar candidate. Each upper bound covers the whole continuous scalar action segment at the predeclared fixed high-dimensional state. It is not a bound on the complete vector action problem or continuous-time adapted policies. Endpoints are rounded upward.'))
    save('table_menu_all_events.tex',table('All Registered Menu Payoff Intervals','tab:r16menuall','llrlrrr',r'Economy & $d$ & Stage & Gain or contrast & Mean & Lower & Upper',fullrows,common,long=True))
    save('table_menu_gains.tex',table('Final-Stage Menu Gains over the Common Reference','tab:r16menugains','llrrrr',r'Economy & $d$ & Method & Mean & Lower & Upper',gainrows,common,long=True))
    save('table_menu_all_work.tex',table('Every Menu Work Stage and Retained Fallback','tab:r16menuallwork','llrlrr',r'Economy & $d$ & Stage & Method & Construction/query s & Fallbacks',allworkrows,
        r'Stage three is an actual full process measurement. Earlier stages use their observed saved-candidate prefix plus all outer overhead and finalization, an explicitly conservative allocation; no early-stopping run is invented. The complete JSON additionally retains every stream clock, CPU and memory record, counters, and the full common confirmation bill. No failed stream is replaced.',long=True))
    save('table_menu_all_scalar.tex',table('Every Conditional Scalar Accuracy Endpoint','tab:r16menualscalar','llrrrrr',r'Economy & $d$ & Stream & Candidate $s$ & Gradient lower & Gradient upper & Gap upper',allscalarrows,
        r'All prescribed scalar events appear. Their error budget is $0.002/128$ each. The secant-to-gradient error, global curvature, arithmetic and Gaussian clipping allowances enter before the global scalar regret upper bound. A large bound is retained without choosing another action class.',long=True))
    summaries=[]
    for method,z in decisions.items():
        summaries.append(LABELS[method]+': '+str(z['positive'])+' positive and '+str(z['materially_superior'])+' material lower endpoints among all '+str(z['total'])+' registered stage--economy comparisons.')
    save('menu_main.tex',r'''\subsection{Reusing a continuation across temporary interventions}
\label{sec:r16menuevidence}
The intervention changes current consumption utility, adjustment cost, or the
current feasible action set. The future reference policy and transition law
remain common. A scalar NBO continuation can therefore be queried at different
postdecision states without changing its economic target. The comparison
includes a fitted vector costate, a materialized Raw actor, a materialized
direct-policy actor, and a sample-average optimizer that reuses its complete
innovation cache throughout every action solve. All five methods retain their
data and materialized candidates across the three predetermined work stages.

\input{revisions/2026-10-04-r16/results/continuation_menu/report/table_menu_comparisons.tex}
\input{revisions/2026-10-04-r16/results/continuation_menu/report/table_menu_work.tex}

'''+ '\n\n'.join(summaries)+r'''

These comparisons concern the complete fixed menu and training-stream
population in each specified finite-period economy. They do not average an
unobserved optimizer distribution. The complete record gives all gains,
direct contrasts, work stages and fallback outcomes. The scalar accuracy
exercise additionally bounds the loss over a prescribed continuous scalar
intervention class; its comparator and separate confidence budget are stated
explicitly.
\input{revisions/2026-10-04-r16/results/continuation_menu/report/table_menu_scalar.tex}
''')
    save('menu_supplement.tex',r'''\subsection{Complete continuation reuse evidence}
\label{app:r16menurecord}
\input{revisions/2026-10-04-r16/results/continuation_menu/report/table_menu_gains.tex}
\input{revisions/2026-10-04-r16/results/continuation_menu/report/table_menu_all_events.tex}
\input{revisions/2026-10-04-r16/results/continuation_menu/report/table_menu_all_work.tex}
\input{revisions/2026-10-04-r16/results/continuation_menu/report/table_menu_all_scalar.tex}
''')
    write(out/'REPORT_MANIFEST.json',dict(complete=True,numerical_source_commit=report['numerical_source_commit'],protocol_sha256=proto_sha,
        report_sha256=sha(out/'REPORT.json'),report_source_sha256=sha(__file__),tex_files=outputs,
        input_raw_hashes=raw_hashes,input_record_hashes=record_hashes,no_favorable_sign_gate=True))
    return dict(complete=True,trials=128,primary_events=216,scalar_events=128,failed_fits=report['total_failed_method_fits'],all_stage_direct_decisions=decisions)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['repo','results','out']:p.add_argument('--'+name,type=Path,required=True)
    print(json.dumps(render(**vars(p.parse_args())),indent=2,allow_nan=False))

if __name__=='__main__':main()
