"""Independent complete R16 economic-family inference and work accounting.

Each calibration is reported in a separate process, so mutable historical
kernel aliases cannot cross economic designs. The aggregate combines tables,
not economic observations or probability budgets across calibrations.
"""
from __future__ import annotations
import argparse
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from pathlib import Path
import sys
import numpy as np

from robustness_pipeline import (R16,PROTOCOL,REPORT,METHODS,CALIBRATIONS,GROUPS,
    read,write,sha,require,safe,canonical,digest,trials,check,verify_work)

ROOT=Path(__file__).resolve().parents[3]
NAMES=dict(nbo='NBO',raw_costate='Raw',direct_policy='Direct policy',hjb_greedy='HJB greedy',hjb_distilled='HJB actor')

def scientific_modules():
    sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r15/code'))
    import method_statistics as stats
    import report_experiment as old
    sys.path.insert(0,str(ROOT/R16/'code'))
    import paired_capital as paired
    return stats,old,paired

def reconstruct(repo,p,calibration,paired):
    answer={}
    for d in p['dimensions']:
        path=repo/R16/f"protocols/robustness_constants/{calibration['id']}_d{d}.json";saved=read(path)
        actual=paired.calculate(calibration,d,p['confirmation']['steps'],saved['coefficient_proofs'])
        actual['protocol_sha256']=sha(repo/PROTOCOL)
        require(canonical(actual)==canonical(saved),'frozen paired account does not reconstruct exactly')
        answer[d]=actual
    return answer

def endpoint(stats,values,c,alpha):
    return stats.empirical_bernstein(values,bound=c['clip'],event_alpha=alpha,bias=c['bias'],clipping_tail=c['tail'])

def pooled(stats,values,constants,identities,seeds,alpha):
    return stats.finite_stream_mean(values,declared_seeds=seeds,noise_keys={s:identities[s]['noise_hash'] for s in seeds},
        bounds={s:constants[s]['clip'] for s in seeds},biases={s:constants[s]['bias'] for s in seeds},
        clipping_tails={s:constants[s]['tail'] for s in seeds},event_alpha=alpha,confirmation_independent_of_selection=True)

def report_calibration(repo,results,out,calibration_id):
    repo=Path(repo).resolve();results=Path(results).resolve();out=Path(out).resolve()
    require(not out.exists() or not any(out.iterdir()),'report output must be new');check(repo)
    p=read(repo/PROTOCOL);calibration=next(c for c in p['calibrations'] if c['id']==calibration_id)
    manifest=read(results.parent/'SOURCE_MANIFEST.json');source=manifest['numerical_source_commit']
    require(sha(repo/PROTOCOL)==manifest['protocol_sha256'] and sha(__file__)==manifest['files'][str(REPORT)]['sha256'],'report/source identity changed')
    for n,f in manifest['files'].items():require(sha(safe(repo,n))==f['sha256'],'frozen reporting closure changed: '+n)
    stats,old,paired=scientific_modules();accounts=reconstruct(repo,p,calibration,paired)
    seeds=p['seeds'];dims=p['dimensions'];budget=stats.ConfidenceBudget(p['inference']['alpha'],p['inference']['two_sided_event_count'])
    loaded={};input_manifest={};identity_records=[];hjb_diagnostics=[]
    own_trials=[t for t in trials(p) if t['calibration_id']==calibration_id]
    require(len(own_trials)==16,'complete calibration required')
    for trial in own_trials:
        d,s=trial['dimension'],trial['stream_seed']
        for group in GROUPS:
            folder=results/trial['trial_id']/group;rpath=folder/'RESULT.json';wpath=folder/'WORK.json'
            r=read(rpath);w=verify_work(folder,manifest,trial,group)
            for key,value in [('complete',True),('trial_id',trial['trial_id']),('calibration_id',calibration_id),('dimension',d),('stream_seed',s),
                ('numerical_source_commit',source),('protocol_sha256',manifest['protocol_sha256']),('method_fingerprint',manifest['method_fingerprints'][group]['sha256']),
                ('primitives_sha256',calibration['primitives_sha256']),('epsilon',calibration['epsilon']),('online_payoff_checks',0),('final_payoff_used_for_selection',False)]:
                require(r.get(key)==value,'group scientific identity mismatch: '+key)
            binding=r['capital_binding'];require(binding['identity']['primitives']==calibration['primitives'],'bound group primitives changed')
            require(binding['identity']['initial_state_population']==calibration['initial_state_population'],'bound occupation population changed')
            require(binding['identity']['epsilon']==calibration['epsilon'] and binding['identity']['calibration_id']==calibration_id,'bound radius/calibration changed')
            if group=='hjb_family':
                if 'hjb_family_record' in r:
                    family_path=safe(folder,r['hjb_family_record']);require(sha(family_path)==r['hjb_family_sha256'],'HJB family evidence changed')
                    family=read(family_path);hjb_diagnostics.append(dict(calibration_id=calibration_id,dimension=d,stream_seed=s,
                        selected_variant=family['selected_variant'],selection_residual_rms=family['selected_residual_rms'],
                        candidates=family['candidates'],independent_diagnostics=family['independent_diagnostics'],
                        probe_diagnostics=family['probe_diagnostics'],operation_counters_complete=family['operation_counters_complete'],
                        family_sha256=sha(family_path),fallback=False))
                    require(family['payoff_evaluations']==0 and len(family['candidates'])==4,'HJB selection did not preserve the fixed four-candidate design')
                else:hjb_diagnostics.append(dict(calibration_id=calibration_id,dimension=d,stream_seed=s,fallback=True,failures=r['failures'],operation_counters_complete=False))
            for method,item in r['outputs'].items():
                c=item['confirmation'];require(item['complete'] and c is not None,'missing final method confirmation')
                for key,value in [('method_id',method),('stream_seed',s),('dimension',d),('calibration_id',calibration_id),('numerical_source_commit',source),
                                  ('protocol_sha256',manifest['protocol_sha256']),('primitives_sha256',calibration['primitives_sha256']),('epsilon',calibration['epsilon']),
                                  ('checkpoint_sha256',item['checkpoint_sha256']),('noise_seed',trial['noise_seed']),('confirmation_bank',trial['noise_key']),
                                  ('paths',8192),('steps',2048),('is_confirmation',True),('fixed_fit',True),('online_target_attainment',False)]:
                    require(c.get(key)==value,'confirmation scientific identity mismatch: '+key)
                require(c['economic_design_identity_sha256']==binding['identity_sha256'],'verification economic identity differs from fitting')
                require(item['fallback']==c['analytic_schedule'],'fallback scope mismatch')
                require(sha(safe(folder,item['checkpoint']))==item['checkpoint_sha256'],'returned policy checkpoint changed')
                if group!='hjb_family' and not item['fallback']:
                    require(len(item['training_stages'])==3 and [x['stage'] for x in item['training_stages']]==[1,2,3],'fixed training envelope omitted stages')
                raw=safe(folder,c['raw_path']);require(sha(raw)==c['raw_sha256'],'raw confirmation changed')
                with np.load(raw,allow_pickle=False) as bank:arrays={k:bank[k].copy() for k in bank.files}
                require(len(arrays['paired_gain'])==8192 and all(np.isfinite(a).all() for a in arrays.values()),'invalid confirmation arrays')
                ident=old.normalize_identity(c,r,{'design':{'primitives_sha256':calibration['primitives_sha256']}})
                constants={key:old.allowance(c,key) for key in ['clip','bias','tail','actor_bias','statistic_error']}
                if item['fallback']:require(not np.count_nonzero(arrays['paired_gain']) and all(v==0 for v in constants.values()),'invalid analytical fallback')
                replay=endpoint(stats,arrays['paired_gain'],constants,budget.event_alpha)
                for key in ['lower','upper','clipped_mean','variance','empirical_bernstein_margin','event_alpha']:
                    require(replay[key]==c['bound'][key],'schedule inference did not replay exactly: '+key)
                record=dict(r,method_id=method,fallback=item['fallback'],final_confirmation=c)
                loaded[d,s,method]=dict(record=record,output=item,identity=ident,arrays=arrays,constants=constants,
                    work=w['method_complete_work_allocation'][method],group_work=w)
                identity_records.append(dict(calibration_id=calibration_id,dimension=d,stream_seed=s,method_id=method,group=group,
                    result_sha256=sha(rpath),work_sha256=sha(wpath),raw_sha256=sha(raw),checkpoint_sha256=item['checkpoint_sha256'],
                    method_fingerprint=r['method_fingerprint'],noise_hash=c['noise_hash'],fallback=item['fallback']))
                for path in [rpath,wpath,raw]:input_manifest[path.relative_to(results).as_posix()]=dict(sha256=sha(path),bytes=path.stat().st_size)
        first=loaded[d,s,'nbo']
        for method in METHODS[1:]:
            right=loaded[d,s,method]
            stats.paired_difference(first['arrays']['paired_gain'],right['arrays']['paired_gain'],left_identity=first['identity'],right_identity=right['identity'])
            require(np.array_equal(first['arrays']['initial_profile'],right['arrays']['initial_profile']),'initial-profile paths differ across methods')
    require(len(loaded)==80,'missing calibration policy output')
    seed_endpoints=[];method_endpoints=[];work_rows=[];attainment=[];allowance_details=[]
    margin=p['economic_decisions']['material_payoff_margin']
    for d in dims:
        for method in METHODS:
            values={s:loaded[d,s,method]['arrays']['paired_gain'] for s in seeds};cs={s:loaded[d,s,method]['constants'] for s in seeds}
            ids={s:loaded[d,s,method]['identity'] for s in seeds};per_seed={}
            for s in seeds:
                e=endpoint(stats,values[s],cs[s],budget.event_alpha);e.update(calibration_id=calibration_id,dimension=d,stream_seed=s,endpoint=method,endpoint_type='schedule_gain')
                seed_endpoints.append(e);per_seed[s]=e
            e=pooled(stats,values,cs,ids,seeds,budget.event_alpha);e.update(calibration_id=calibration_id,dimension=d,endpoint=method,endpoint_type='schedule_gain')
            anchor=max(loaded[d,s,method]['record']['final_confirmation']['constants']['anchor_upper'] for s in seeds)
            e['full_adapted_class_anchor_upper']=anchor;e['full_adapted_class_regret_upper']=float(paired.pc.up(anchor-e['lower']));method_endpoints.append(e)
            for target in [p['confirmation']['fixed_budget_gain_target'],p['confirmation']['secondary_gain_target']]:
                attainment.append(dict(calibration_id=calibration_id,dimension=d,method_id=method,**stats.certified_attainment_fraction(per_seed,declared_seeds=seeds,target=target)))
            times={s:loaded[d,s,method]['work']['standalone_end_to_end_seconds'] for s in seeds}
            work_rows.append(dict(calibration_id=calibration_id,dimension=d,method_id=method,mean_complete_seconds=sum(times.values())/len(seeds),
                per_seed_complete_seconds={str(s):times[s] for s in seeds},fallback_count=sum(loaded[d,s,method]['output']['fallback'] for s in seeds),
                fixed_final_target_attained=sum(loaded[d,s,method]['output']['final_certified_target'] for s in seeds),
                operation_counters_complete=all(loaded[d,s,method]['output']['operation_counters_complete'] for s in seeds),
                shared_hjb_construction=method.startswith('hjb_'),
                work_scope='All fixed-envelope fits and final confirmations retained. HJB charges all shared prerequisites and finalization plus its own deployment; no online payoff stopping or successful-only work average.'))
        for a,b in p['confirmation']['direct_contrasts']:
            name=a+'__minus__'+b;values={};cs={};oldcs={};ids={}
            for s in seeds:
                left,right=loaded[d,s,a],loaded[d,s,b]
                values[s]=stats.paired_difference(left['arrays']['paired_gain'],right['arrays']['paired_gain'],left_identity=left['identity'],right_identity=right['identity'])
                terms=paired.refined_allowances(left,right,accounts[d]);cs[s]=terms['refined'];oldcs[s]=terms['original'];ids[s]=left['identity']
                e=endpoint(stats,values[s],cs[s],budget.event_alpha);old_e=endpoint(stats,values[s],oldcs[s],budget.event_alpha)
                paired.preserved.assert_same_event(old_e,e)
                e.update(calibration_id=calibration_id,dimension=d,stream_seed=s,endpoint=name,endpoint_type='direct_method_contrast',original_transfer_endpoint=old_e,
                    decision=stats.economic_decision(e['lower'],e['upper'],margin));seed_endpoints.append(e)
                allowance_details.append(dict(calibration_id=calibration_id,dimension=d,stream_seed=s,endpoint=name,**terms))
            e=pooled(stats,values,cs,ids,seeds,budget.event_alpha);old_e=pooled(stats,values,oldcs,ids,seeds,budget.event_alpha)
            paired.preserved.assert_same_event(old_e,e)
            e.update(calibration_id=calibration_id,dimension=d,endpoint=name,endpoint_type='direct_method_contrast',original_transfer_endpoint=old_e,
                decision=stats.economic_decision(e['lower'],e['upper'],margin));method_endpoints.append(e)
    require(len(seed_endpoints)==144 and len(method_endpoints)==18,'calibration probability family incomplete')
    part=dict(record_type='R16 complete fixed-calibration robustness report',complete=True,calibration_id=calibration_id,calibration=calibration,
        numerical_source_commit=source,protocol_sha256=manifest['protocol_sha256'],confidence=budget.as_dict(),policy_outputs=80,
        seed_endpoints=seed_endpoints,method_endpoints=method_endpoints,work=work_rows,final_certified_attainment=attainment,
        paired_allowance_details=allowance_details,identity_records=identity_records,input_file_manifest=input_manifest,hjb_diagnostics=hjb_diagnostics,
        deterministic_accounts={str(d):dict(sha256=digest(canonical(a)),fresh_outward_reconstruction_exact=True) for d,a in accounts.items()},
        economic_margin=margin,scope='Uniform average over all eight pre-drawn, subsequently frozen streams in this single economic calibration; no aggregation of observations across calibrations.',
        target_scope='One final certification after the complete fixed fitting envelope; no economic early stopping.',favorable_sign_required=False)
    out.mkdir(parents=True,exist_ok=True);write(out/'PART.json',part)
    for n,f in input_manifest.items():require(sha(results/n)==f['sha256'],'worker evidence changed during report')
    return dict(complete=True,calibration_id=calibration_id,policy_outputs=80,events=162)

def number(x,side=None):
    if side is None:return f'{float(x):.6f}'
    return format(Decimal.from_float(float(x)).quantize(Decimal('0.000001'),rounding=ROUND_FLOOR if side=='lower' else ROUND_CEILING),'f')

def interval(row):return '['+number(row['lower'],'lower')+', '+number(row['upper'],'upper')+']'

def aggregate(repo,out):
    repo=Path(repo).resolve();out=Path(out).resolve();p=read(repo/PROTOCOL)
    require(not (out/'REPORT.json').exists(),'refusing repeated aggregate report')
    parts=[read(out/'parts'/c/'PART.json') for c in CALIBRATIONS]
    require([q['calibration_id'] for q in parts]==CALIBRATIONS and all(q['complete'] for q in parts),'complete four-calibration reports required')
    require(len({q['numerical_source_commit'] for q in parts})==1 and all(q['protocol_sha256']==sha(repo/PROTOCOL) for q in parts),'mixed source or protocol')
    result=dict(record_type='R16 complete prospective economic robustness family',complete=True,numerical_source_commit=parts[0]['numerical_source_commit'],
        protocol_sha256=sha(repo/PROTOCOL),confidence=parts[0]['confidence'],calibrations=p['calibrations'],trials=64,fresh_group_processes=256,policy_outputs=320,
        economic_margin=p['economic_decisions']['material_payoff_margin'],
        inference_scope='Four prespecified economic calibrations reported separately; each estimand averages all eight fixed streams. No pooling across calibrations or extrapolation to all training randomness.',
        work_scope='Complete observed process work; both HJB deployments are charged their shared construction and all common finalization. All failures and nonattaining fixed final targets remain included.',
        target_scope='Independent final target certification after fixed-envelope fitting. Historical R15 online stopping remains separate and unchanged.',
        favorable_sign_required=False,part_sha256={c:sha(out/'parts'/c/'PART.json') for c in CALIBRATIONS})
    for key in ['seed_endpoints','method_endpoints','work','final_certified_attainment','paired_allowance_details','identity_records','hjb_diagnostics']:
        result[key]=[row for part in parts for row in part[key]]
    require(len(result['seed_endpoints'])==576 and len(result['method_endpoints'])==72 and len(result['identity_records'])==320,'incomplete full family')
    result['confidence_event_count_verified']=648;write(out/'REPORT.json',result)
    _,old,_=scientific_modules()
    note=('All four economic designs and all eight pre-drawn streams are retained. Each method receives 8192 independent confirmation paths on 2048 cells. '
          'Intervals share a prospectively fixed familywise allocation $\\alpha=0.01$ over 648 two-sided events. '
          'The full-adapted-class regret bound is displayed beside each gain; positive improvement does not imply near optimality. Endpoints are rounded outward.')
    gains=[r for r in result['method_endpoints'] if r['endpoint_type']=='schedule_gain']
    old.latex_table(out/'robustness_methods.tex','Prospective robustness over economic calibrations','tab:r16-robustness-methods',
        ['Design','$d$','Method','Mean gain','Simultaneous interval','Regret bound'],
        [[r['calibration_id'],r['dimension'],NAMES[r['endpoint']],number(r['raw_mean']),interval(r),number(r['full_adapted_class_regret_upper'],'upper')] for r in gains],note,long=True)
    contrasts=[r for r in result['method_endpoints'] if r['endpoint_type']=='direct_method_contrast']
    old.latex_table(out/'robustness_comparisons.tex','Direct common-path NBO comparisons across economic designs','tab:r16-robustness-comparisons',
        ['Design','$d$','NBO minus','Mean','Fixed paired interval'],
        [[r['calibration_id'],r['dimension'],NAMES[r['endpoint'].split('__minus__')[1]],number(r['raw_mean']),interval(r)] for r in contrasts],
        'The continuous-time paired transfer and all calibration-specific constants are fixed before confirmation. Original-transfer intervals remain in the complete machine-readable record. A crossing interval is unresolved, not evidence of equivalence.',long=True)
    old.latex_table(out/'robustness_work.tex','Complete fixed-envelope work and final target attainment','tab:r16-robustness-work',
        ['Design','$d$','Method','Mean seconds','Final target','Fallbacks'],
        [[r['calibration_id'],r['dimension'],NAMES[r['method_id']],f"{r['mean_complete_seconds']:.2f}",f"{r['fixed_final_target_attained']}/8",r['fallback_count']] for r in result['work']],
        'All streams enter the mean, including failed training and nonattainment. Target is 0.0005 at the single final decision. HJB greedy and its distilled actor share the complete four-candidate construction; each is charged that prerequisite and its own deployment, with all launch and finalization overhead. These are environment-specific measured costs, not equal FLOPs.',long=True)
    write(out/'REPORT_MANIFEST.json',dict(numerical_source_commit=result['numerical_source_commit'],files={x.relative_to(out).as_posix():sha(x) for x in sorted(out.rglob('*')) if x.is_file()}))
    return dict(complete=True,policy_outputs=320,events=648,report_sha256=sha(out/'REPORT.json'))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo',type=Path,default=ROOT);parser.add_argument('--results',type=Path)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--calibration');parser.add_argument('--aggregate',action='store_true');args=parser.parse_args()
    if args.aggregate:result=aggregate(args.repo,args.out)
    else:
        if args.results is None or args.calibration not in CALIBRATIONS:parser.error('--results and a declared --calibration are required')
        result=report_calibration(args.repo,args.results,args.out,args.calibration)
    import json
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':main()
