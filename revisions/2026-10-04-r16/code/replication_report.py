"""Reconstruct the complete R16 fresh-bank family from original raw arrays.

The paired transfer, its constants, clipping decisions and confidence budget
are fixed before these observations. Every old policy enters the new family.
No fitting, policy replacement, data-dependent refinement or alpha reuse occurs.
"""
from __future__ import annotations
import argparse
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from pathlib import Path
import sys
import numpy as np

from replication_pipeline import (R16,PROTOCOL,CANDIDATES,CONSTANTS,CANDIDATE_SOURCE,CANDIDATE_EVIDENCE,
    METHODS,canonical,digest,read,write,sha,require,safe,trials,check,verify_work)

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r15/code'))
import method_statistics as stats
import report_experiment as old_report
import report_paired_transfer as paired

def reconstruct(repo):
    """Reprove only deterministic constants; no payoff observations are read."""
    repo=Path(repo).resolve();p=read(repo/PROTOCOL);original=read(safe(repo,p['candidate_protocol']))
    frozen=read(repo/CONSTANTS);proposals=paired.read_coefficient_proposals(repo/CONSTANTS,original)
    previous={r['dimension']:r for r in frozen['model_accounts']};records={}
    for d in p['design']['dimensions']:
        actual=paired.calculate(original,d,steps=p['confirmation']['steps'],epsilon=.1,coefficient_proposals=proposals[d])
        require(canonical(actual)==canonical(previous[d]),'prospectively fixed deterministic account failed exact reconstruction')
        records[d]=actual
    return records

def endpoint(values,c,alpha):
    return stats.empirical_bernstein(values,bound=c['clip'],event_alpha=alpha,bias=c['bias'],clipping_tail=c['tail'])

def aggregate(values,constants,identities,seeds,alpha):
    return stats.finite_stream_mean(values,declared_seeds=seeds,
        noise_keys={s:identities[s]['noise_hash'] for s in seeds},
        bounds={s:constants[s]['clip'] for s in seeds},biases={s:constants[s]['bias'] for s in seeds},
        clipping_tails={s:constants[s]['tail'] for s in seeds},event_alpha=alpha,confirmation_independent_of_selection=True)

def report(repo,results,out):
    repo=Path(repo).resolve();results=Path(results).resolve();out=Path(out).resolve()
    require(not out.exists() or not any(out.iterdir()),'report output must be new')
    require(not out.is_relative_to(results),'report must not alter original worker evidence')
    check(repo);p=read(repo/PROTOCOL);candidates=read(repo/CANDIDATES);manifest=read(results.parent/'SOURCE_MANIFEST.json')
    require(sha(repo/PROTOCOL)==manifest['protocol_sha256'],'replication source protocol changed')
    require(sha(__file__)==manifest['files'][str(R16/'code/replication_report.py')]['sha256'],'report is not frozen execution source')
    require(digest(canonical(manifest['fingerprint_input']))==manifest['assessment_fingerprint'],'source fingerprint changed')
    for name,f in manifest['files'].items():require(sha(safe(repo,name))==f['sha256'],'source closure changed before report: '+name)
    source=manifest['numerical_source_commit'];design=p['design'];seeds=design['seeds'];dims=design['dimensions']
    budget=stats.ConfidenceBudget(p['inference']['family_alpha'],p['inference']['event_count'])
    accounts=reconstruct(repo);by_candidate={(r['dimension'],r['stream_seed'],r['method_id']):r for r in candidates['files']}
    expected={(d,s,m) for d in dims for s in seeds for m in METHODS};loaded={};input_manifest=[];identities=[]
    expected_results={results/f'd{d}_s{s}'/m/'RESULT.json' for d,s,m in expected}
    require(set(results.rglob('RESULT.json'))==expected_results,'missing or unexpected policy result')
    for trial in trials(p):
        d,seed=trial['dimension'],trial['stream_seed']
        for method in METHODS:
            folder=results/trial['trial_id']/method;rpath=folder/'RESULT.json';wpath=folder/'WORK.json'
            r=read(rpath);w=verify_work(folder,manifest,trial,method);candidate=by_candidate[d,seed,method]
            for key,value in [('complete',True),('method_id',method),('dimension',d),('stream_seed',seed),
                              ('numerical_source_commit',source),('candidate_source_commit',CANDIDATE_SOURCE),
                              ('candidate_evidence_commit',CANDIDATE_EVIDENCE),('protocol_sha256',manifest['protocol_sha256']),
                              ('assessment_fingerprint',manifest['assessment_fingerprint']),('checkpoint_sha256',candidate['sha256']),
                              ('method_fingerprint',candidate['method_fingerprint']),('training_runs',0),('new_optimizer_draws',0),('new_stopping_decisions',0),
                              ('original_attained_online',candidate['original_attained_online']),('original_selected_stage',candidate['original_selected_stage']),
                              ('original_stopping_unchanged',True),('confirmation_independent_of_selection',True),('fallback',candidate['fallback'])]:
                require(r.get(key)==value,'replication result identity mismatch: '+key)
            c=r['final_confirmation']
            for key in ['numerical_source_commit','candidate_source_commit','candidate_evidence_commit','protocol_sha256',
                        'assessment_fingerprint','checkpoint_sha256','method_fingerprint','method_id','dimension','stream_seed']:
                require(c.get(key)==r[key],'confirmation/result identity mismatch: '+key)
            require(c['noise_seed']==trial['noise_seed'] and c['confirmation_bank']==trial['noise_key'],'undeclared fresh bank')
            require(c['paths']==8192 and c['steps']==2048,'new confirmation size differs')
            require(c['noise_hash']!=candidate['original_confirmation_noise_hash'] and c['initial_state_hash']!=candidate['original_initial_state_hash'],'old confirmation bank reused')
            ident=old_report.normalize_identity(c,r,{'design':design})
            raw=safe(folder,c['raw_path']);require(sha(raw)==c['raw_sha256'],'fresh raw array hash mismatch')
            with np.load(raw,allow_pickle=False) as data: arrays={k:data[k].copy() for k in data.files}
            require(len(arrays['paired_gain'])==8192 and all(np.isfinite(a).all() for a in arrays.values()),'invalid fresh numerical arrays')
            constants={key:old_report.allowance(c,key) for key in ['clip','bias','tail','actor_bias','statistic_error']}
            require(r['fallback']==c['analytic_schedule'],'fallback classification changed')
            if r['fallback']: require(np.count_nonzero(arrays['paired_gain'])==0 and all(v==0 for v in constants.values()),'exact analytical fallback failed')
            own=endpoint(arrays['paired_gain'],constants,budget.event_alpha)
            for key in ['lower','upper','empirical_bernstein_margin','clipped_mean','variance','event_alpha']:
                require(own[key]==c['bound'][key],'independent schedule endpoint replay differs: '+key)
            loaded[d,seed,method]=dict(record=r,work=w,identity=ident,arrays=arrays,constants=constants)
            identities.append(dict(dimension=d,stream_seed=seed,method_id=method,result_sha256=sha(rpath),work_sha256=sha(wpath),
                raw_sha256=sha(raw),checkpoint_sha256=candidate['sha256'],original_method_fingerprint=candidate['method_fingerprint'],
                old_confirmation_noise_hash=candidate['original_confirmation_noise_hash'],new_confirmation_noise_hash=c['noise_hash'],
                original_stopping_unchanged=True))
            input_manifest.extend(dict(path=x.relative_to(results).as_posix(),sha256=sha(x),bytes=x.stat().st_size) for x in [rpath,wpath,raw])
        first=loaded[d,seed,METHODS[0]]
        for method in METHODS[1:]:
            right=loaded[d,seed,method]
            stats.paired_difference(first['arrays']['paired_gain'],right['arrays']['paired_gain'],left_identity=first['identity'],right_identity=right['identity'])
            require(np.array_equal(first['arrays']['initial_profile'],right['arrays']['initial_profile']),'unpaired initial-profile sample')
    seed_endpoints=[];method_endpoints=[];comparison_details=[];attainment=[];work=[]
    margin=p['economic_decision']['margin']
    for d in dims:
        for method in METHODS:
            values={s:loaded[d,s,method]['arrays']['paired_gain'] for s in seeds}
            cs={s:loaded[d,s,method]['constants'] for s in seeds};ids={s:loaded[d,s,method]['identity'] for s in seeds};per_seed={}
            for s in seeds:
                e=endpoint(values[s],cs[s],budget.event_alpha);e.update(dimension=d,stream_seed=s,endpoint=method,endpoint_type='schedule_gain')
                seed_endpoints.append(e);per_seed[s]=e
            e=aggregate(values,cs,ids,seeds,budget.event_alpha);e.update(dimension=d,endpoint=method,endpoint_type='schedule_gain')
            e['full_adapted_class_regret_upper']=float(paired.pc.up(max(loaded[d,s,method]['record']['final_confirmation']['constants']['anchor_upper'] for s in seeds)-e['lower']))
            method_endpoints.append(e)
            for target in p['economic_decision']['schedule_gain_targets']:
                attainment.append(dict(dimension=d,method_id=method,**stats.certified_attainment_fraction(per_seed,declared_seeds=seeds,target=target)))
            work.append(dict(dimension=d,method_id=method,mean_additional_confirmation_seconds=sum(loaded[d,s,method]['work']['end_to_end_seconds'] for s in seeds)/len(seeds),
                total_additional_confirmation_seconds=sum(loaded[d,s,method]['work']['end_to_end_seconds'] for s in seeds),
                scope='Additional independent verification only; no new training, stopping or work-to-target claim.'))
        for left_method,right_method in p['confirmation']['direct_contrasts']:
            name=left_method+'__minus__'+right_method;values={};cs={};ids={};original_cs={}
            for s in seeds:
                left,right=loaded[d,s,left_method],loaded[d,s,right_method]
                values[s]=stats.paired_difference(left['arrays']['paired_gain'],right['arrays']['paired_gain'],left_identity=left['identity'],right_identity=right['identity'])
                terms=paired.refined_allowances(left,right,accounts[d]);cs[s]=terms['refined'];original_cs[s]=terms['original'];ids[s]=left['identity']
                e=endpoint(values[s],cs[s],budget.event_alpha);original=endpoint(values[s],original_cs[s],budget.event_alpha)
                paired.assert_same_event(original,e)
                e.update(dimension=d,stream_seed=s,endpoint=name,endpoint_type='direct_method_contrast',original_transfer_endpoint=original,
                         decision=stats.economic_decision(e['lower'],e['upper'],margin))
                seed_endpoints.append(e);comparison_details.append(dict(dimension=d,stream_seed=s,endpoint=name,**terms))
            e=aggregate(values,cs,ids,seeds,budget.event_alpha);original=aggregate(values,original_cs,ids,seeds,budget.event_alpha)
            paired.assert_same_event(original,e)
            e.update(dimension=d,endpoint=name,endpoint_type='direct_method_contrast',original_transfer_endpoint=original,
                     decision=stats.economic_decision(e['lower'],e['upper'],margin));method_endpoints.append(e)
    require(len(seed_endpoints)==224 and len(method_endpoints)==14,'missing or double-counted confidence events')
    result=dict(record_type='R16 prospectively refined independent confirmation report',complete=True,numerical_source_commit=source,
        candidate_source_commit=CANDIDATE_SOURCE,candidate_evidence_commit=CANDIDATE_EVIDENCE,protocol_sha256=manifest['protocol_sha256'],
        assessment_fingerprint=manifest['assessment_fingerprint'],candidate_inventory_sha256=sha(repo/CANDIDATES),paired_constants_sha256=sha(repo/CONSTANTS),
        training_runs=0,new_optimizer_draws=0,policy_executions=128,trial_count=32,new_confirmation_banks=32,
        confidence=budget.as_dict(),economic_margin=margin,method_endpoints=method_endpoints,seed_endpoints=seed_endpoints,
        paired_allowance_details=comparison_details,identity_records=identities,input_file_manifest=input_manifest,
        final_certified_attainment=attainment,additional_confirmation_work=work,
        deterministic_account_reconstruction={str(d):dict(sha256=digest(canonical(a)),exact_match=True,proof='Fresh outward LDL of the exact frozen matrices') for d,a in accounts.items()},
        chronology='Protocol, all original candidates, paired theorem, deterministic accounts, interval implementation and new domain-separated banks were frozen in the recorded R16 source before every confirmation outcome.',
        estimand='Conditional on all R15 selection, uniform mean over its complete declared sixteen-stream finite policy distribution; this is independent payoff replication, not inference to unobserved training randomness.',
        historical_scope='Original R15 prospective intervals and later deterministic reanalysis remain unchanged; this new R16 confidence family uses only new observations and spends its own .01 allocation.',
        work_scope='Original fitting/stopping costs are unchanged. Recorded costs concern this additional independent replication only.',
        favorable_sign_required=False)
    out.mkdir(parents=True,exist_ok=True);write(out/'REPORT.json',result);tables(result,out)
    for row in input_manifest: require(sha(results/row['path'])==row['sha256'],'raw replication input changed while reporting')
    write(out/'REPORT_MANIFEST.json',dict(numerical_source_commit=source,files={x.name:sha(x) for x in sorted(out.iterdir()) if x.is_file()}))
    return dict(complete=True,policy_executions=128,events=238,report_sha256=sha(out/'REPORT.json'))

def number(x,side=None):
    if side is None:return f'{float(x):.6f}'
    return format(Decimal.from_float(float(x)).quantize(Decimal('0.000001'),rounding=ROUND_FLOOR if side=='lower' else ROUND_CEILING),'f')

def interval(row):return '['+number(row['lower'],'lower')+', '+number(row['upper'],'upper')+']'

def tables(result,out):
    gains=[r for r in result['method_endpoints'] if r['endpoint_type']=='schedule_gain']
    contrasts=[r for r in result['method_endpoints'] if r['endpoint_type']=='direct_method_contrast']
    note=('All 128 original R15 selected policies are evaluated without retraining on new R16 banks. '
          'Each of the sixteen original streams receives 8192 independent paths on 2048 cells. '
          'The paired theorem, constants and new familywise allocation $\\alpha=0.01$ precede these observations. '
          'Interval endpoints and regret upper bounds are rounded outward. This is independent confirmation of fixed policies; historical stopping is unchanged.')
    old_report.latex_table(out/'replication_methods.tex','Independent R16 confirmation of the fixed R15 policies','tab:r16-replication-methods',
        ['$d$','Method','Mean gain','Simultaneous interval','Regret bound'],
        [[r['dimension'],old_report.NAMES[r['endpoint']],number(r['raw_mean']),interval(r),number(r['full_adapted_class_regret_upper'],'upper')] for r in gains],note)
    old_report.latex_table(out/'replication_comparisons.tex','Prospectively fixed paired transfer on fresh confirmation banks','tab:r16-replication-comparisons',
        ['$d$','NBO minus','Mean','Original transfer','Fixed paired transfer'],
        [[r['dimension'],old_report.NAMES[r['endpoint'].split('__minus__')[1]],number(r['raw_mean']),interval(r['original_transfer_endpoint']),interval(r)] for r in contrasts],note)
    old_report.latex_table(out/'replication_work.tex','Additional work for independent policy replication','tab:r16-replication-work',
        ['$d$','Method','Mean seconds','Total seconds'],
        [[r['dimension'],old_report.NAMES[r['method_id']],f"{r['mean_additional_confirmation_seconds']:.2f}",f"{r['total_additional_confirmation_seconds']:.2f}"] for r in result['additional_confirmation_work']],
        'Complete fresh-process confirmation clocks include imports, frozen weight reload, constants, simulation and durable output. These additional assessment costs do not replace the original R15 training or stopping work.')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo',type=Path,default=ROOT)
    parser.add_argument('--results',type=Path);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--constants-only',action='store_true')
    args=parser.parse_args()
    if args.constants_only:
        records=reconstruct(args.repo);write(args.out,dict(complete=True,new_payoff_observations_read=0,model_accounts=list(records.values())))
        print('Both fixed deterministic paired-transfer accounts reconstructed exactly; no new payoff bank read.')
    else:
        if args.results is None:parser.error('--results is required for the complete fresh-bank report')
        import json
        print(json.dumps(report(args.repo,args.results,args.out),indent=2))

if __name__=='__main__':main()
