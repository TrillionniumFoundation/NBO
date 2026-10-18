"""Post-execution read-only aggregation of frozen R119 numerical records.

This is derived reporting, written after outcomes. It never imports or calls a
scientific evaluator, trains a model, reruns a clock, or changes a raw result.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import csv, hashlib, json, math, statistics

ROOT = Path('/workspace/scratch/913249553838/NBO/revisions/2026-10-18-r119')
RAW = ROOT/'results119/primary119'
OUT = Path(__file__).resolve().parent
ARMS = ('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
SERVICES = ('compiled','geometric','active-tail')

def load(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def fr(value): return F(float(value))
def avg(values): return float(sum(map(fr,values))/len(values))
def avg_lower(values): return math.nextafter(avg(values),-math.inf)
def avg_upper(values): return math.nextafter(avg(values),math.inf)
def dump(name,value): (OUT/name).write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')

checks=0
def check(condition,message):
    global checks
    checks += 1
    if not condition: raise ArithmeticError(message)

campaign=load(RAW/'CAMPAIGN119.json')
catalogue=load(RAW/'CATALOGUE119.json')
native_audit=load(RAW/'AUDIT119.json')
reference=load(RAW/'REFERENCE119.json')
acquisition=load(RAW/'ACQUISITION119.json')
check(campaign['source']['executable_protocol_commit']=='1f33c2667e0dff89699c6d6a01d03eacfecf3f4e','Prospective source identity')
check(native_audit['status']=='passed','Executed native record audit')
check(not (RAW/'FAILED.json').exists(),'No primary campaign failure marker')
files=catalogue['entries'][:]
timing_processes=[]
for repeat in range(7):
    proc=load(RAW/'timing'/f'PROCESS-{repeat}.json'); timing_processes.append(proc)
    check(proc['repeat']==repeat,'Every distinct timing repeat retained')
    files.extend(proc['entries'])
    receipt=campaign['processes'][repeat]
    check(receipt['exit_code']==0 and sha(RAW/'timing'/f'PROCESS-{repeat}.log')==receipt['log_sha256'],'Timing process exit and log hash')
allrecords={}
for entry in files:
    p=RAW/entry['path']; check(sha(p)==entry['sha256'],'Raw file manifest hash '+entry['path'])
    d=load(p); allrecords[entry['path']]=d
    for r in d['rows']:
        low,high,opt,loss,width=map(fr,(r['lower'],r['upper'],r['optimum_lower'],r['loss'],r['width']))
        check(low<=high and opt<=high,'Certificate ordering')
        check(loss>=high-opt and loss<=F(1,256),'Original objective loss qualification')
        check(width>=high-low and width<=F(1,8192),'Original-policy width qualification')
        cap=F(1,8)+(fr(r['x0'])+fr(r['x1']))/16
        check(0<=fr(r['action'])<=cap,'Actual original action feasibility')
        check(fr(r['action_distance_upper'])**2>=loss,'Outward action-distance allowance')
        check(r['returned_action_changed']==(r['action']!=r['proposed']),'Returned action flag')
        check(r['first_attempt_rejected']==(not (r['first_loss']<=1/256 and r['first_width']<=1/8192)),'First-attempt rejection flag')

refs={}
contrast_summary=Counter()
for rec in reference['records']:
    i=rec['index']
    for state in rec['states']:
        check(state['optimum_lower']<=state['optimum_upper'],'Reference optimum bracket')
        for p in state['policies']:
            refs[i,p['policy'],state['row']]=p
            check(fr(p['regret_upper'])>=fr(p['upper'])-fr(state['optimum_lower']),'Reference original regret allowance')
            check(fr(p['action_distance_upper'])**2>=fr(p['regret_upper']),'Reference distance allowance')
        for c in state['contrasts']:
            key=f"{c['control']}->{c['treatment']}"
            contrast_summary[key+'/total']+=1
            contrast_summary[key+'/identical']+=int(c['identical_policy'])
            contrast_summary[key+'/strictly_improved']+=int(c['strictly_improved'])
            contrast_summary[key+'/strictly_worse']+=int(c['strictly_worse'])
            if c['identical_policy']:
                check(c['lower']==c['upper']==0,'Identical complete policy has exactly zero contrast')

frontier=[]
standalone=[]
for i,alpha in enumerate((.5,.75)):
    for arm in ARMS:
        a=load(RAW/'models'/f'{i}-{arm}'/'acquisition.json')
        check(sha(RAW/'models'/f'{i}-{arm}'/'model.json')==a['model_sha256'],'Actual acquired model payload hash')
        component={k:a.get(k,0.0) for k in ('label_cost_if_standalone_seconds','fit_seconds','audit_seconds','serialization_seconds')}
        if arm=='hinge':
            r=load(RAW/'models'/f'{i}-relu'/'acquisition.json')
            component.update(fit_seconds=r['fit_seconds'],audit_seconds=r['audit_seconds'],underlying_relu_serialization_seconds=r['serialization_seconds'])
        acquisition_seconds=sum(component.values())
        fit=a.get('fit',{})
        standalone.append(dict(index=i,alpha=alpha,arm=arm,components=component,
            seconds=acquisition_seconds,label_sites=a['label_sites'],payload_bytes=a['payload_bytes'],
            candidate_solves=fit.get('candidate_solves'),recorded_fit_trials=len(fit.get('trials',[])),
            recorded_audit_trials=len(a.get('audit',{}).get('trials',[])),
            inherited_full_acquisition_from='relu' if arm=='hinge' else None))
        loading=catalogue['model_loading'][i]['per_arm'][arm]
        for service in SERVICES:
            d=allrecords[f'catalogue/{i}-{arm}-{service}.json']; rows=d['rows']
            clocks=[allrecords[f'timing/{r}-{i}-{arm}-{service}.json']['seconds'] for r in range(7)]
            primary_refs=[refs[i,arm+'/'+service,j] for j in range(144)]
            check(all(r['action']==v['action'] for r,v in zip(rows,primary_refs)),'Reference binds exact returned action')
            for r,v in zip(rows,primary_refs):
                check(r['lower']<=v['upper'] and v['lower']<=r['upper'],'Reference/production policy interval overlap')
            counts=d['counts']
            data=dict(index=i,alpha=alpha,arm=arm,service=service,
                acquisition_seconds=acquisition_seconds,model_loading_seconds=loading,payload_bytes=a['payload_bytes'],
                primary144_service_seconds=d['seconds'],primary144_proposal_seconds=d['proposal_seconds'],
                component_sum_acquisition_loading_primary144_seconds=acquisition_seconds+loading+d['seconds'],
                timing32_median_seconds=statistics.median(clocks),timing32_min_seconds=min(clocks),timing32_max_seconds=max(clocks),
                timing32_all_seconds=clocks,timing32_median_per_decision_seconds=statistics.median(clocks)/32,
                primary_mean_original_cost_lower=avg_lower([v['lower'] for v in primary_refs]),
                primary_mean_original_cost_upper=avg_upper([v['upper'] for v in primary_refs]),
                primary_mean_regret_lower=max(0.0,avg_lower([v['regret_lower'] for v in primary_refs])),
                primary_mean_regret_upper=avg_upper([v['regret_upper'] for v in primary_refs]),
                primary_max_regret_upper=max(v['regret_upper'] for v in primary_refs),
                primary_mean_action_distance_upper=avg_upper([v['action_distance_upper'] for v in primary_refs]),
                primary_max_action_distance_upper=max(v['action_distance_upper'] for v in primary_refs),
                first_attempt_rejections=sum(r['first_attempt_rejected'] for r in rows),
                proposals_repaired=sum(r['proposal_repaired'] for r in rows),
                returned_actions_changed=sum(r['returned_action_changed'] for r in rows),
                exact_fallbacks=sum(r['exact_fallback'] for r in rows),
                attempted_certificates=len(d['attempts']),
                rejected_attempted_certificates=sum(not r['qualified'] for r in d['attempts']),
                initial_schedule_exhausted=len({r['row'] for r in d['attempts'] if r['kind']=='full-support-fallback'}),
                accepted_resolution_histogram=dict(Counter(r['bins'] for r in rows)),
                certificate_mean_width=avg([r['width'] for r in rows]),certificate_max_width=max(r['width'] for r in rows),
                certificate_max_loss=max(r['loss'] for r in rows),
                original_risk_point_queries=counts.get('terminal_original_risk_queries',0),
                terminal_proposal_queries=counts.get('terminal_proposal_queries',0),
                compiled_terminal_rows=counts.get('compiled_terminal_rows',0),
                risk_sort_items=counts.get('risk_sort_items',0),counts=counts)
            frontier.append(data)

lookup={(r['index'],r['arm'],r['service']):r for r in frontier}
comparisons=[]
for i in range(2):
    for arm in ARMS:
        for control in ('compiled','geometric'):
            a,b=lookup[i,arm,control],lookup[i,arm,'active-tail']
            ar=allrecords[f'catalogue/{i}-{arm}-{control}.json']['rows']
            br=allrecords[f'catalogue/{i}-{arm}-active-tail.json']['rows']
            comparisons.append(dict(index=i,alpha=a['alpha'],arm=arm,control=control,treatment='active-tail',
                identical_primary_policies=sum(x['action']==y['action'] for x,y in zip(ar,br)),
                median_time_ratio=b['timing32_median_seconds']/a['timing32_median_seconds'],
                primary_time_ratio=b['primary144_service_seconds']/a['primary144_service_seconds'],
                full144_component_ratio=b['component_sum_acquisition_loading_primary144_seconds']/a['component_sum_acquisition_loading_primary144_seconds'],
                risk_query_ratio=b['original_risk_point_queries']/a['original_risk_point_queries'],
                compiled_row_ratio=b['compiled_terminal_rows']/a['compiled_terminal_rows'],
                sorting_item_ratio=b['risk_sort_items']/a['risk_sort_items'],
                faster_timing_repeats=sum(b['timing32_all_seconds'][r]<a['timing32_all_seconds'][r] for r in range(7))))

identities=[]
for i in range(2):
    for service in SERVICES:
        identities.append(dict(index=i,service=service,scope='primary',rows=144,
            exact_row_identity=allrecords[f'catalogue/{i}-relu-{service}.json']['rows']==allrecords[f'catalogue/{i}-hinge-{service}.json']['rows'],
            exact_attempt_identity=allrecords[f'catalogue/{i}-relu-{service}.json']['attempts']==allrecords[f'catalogue/{i}-hinge-{service}.json']['attempts']))
        for r in range(7):
            identities.append(dict(index=i,service=service,scope='timing',repeat=r,rows=32,
                exact_row_identity=allrecords[f'timing/{r}-{i}-relu-{service}.json']['rows']==allrecords[f'timing/{r}-{i}-hinge-{service}.json']['rows'],
                exact_attempt_identity=allrecords[f'timing/{r}-{i}-relu-{service}.json']['attempts']==allrecords[f'timing/{r}-{i}-hinge-{service}.json']['attempts']))
check(all(r['exact_row_identity'] and r['exact_attempt_identity'] for r in identities),'Complete ReLU/hinge numerical identity')

scaling=[]
sr=load(RAW/'SCALING119.json')['records']
for i in range(0,len(sr),2):
    a,b=sr[i:i+2]
    check(a['d']==b['d'] and a['alpha']==b['alpha'] and a['state']==b['state'] and a['action']==b['action'],'Scaling exact original proposal identity')
    scaling.append(dict(d=a['d'],alpha=a['alpha'],compiled_seconds=a['seconds'],active_tail_seconds=b['seconds'],
        certificate_time_ratio=b['seconds']/a['seconds'],common_proposal_seconds=a['common_proposal']['seconds'],
        proposal_plus_certificate_ratio=(b['seconds']+a['common_proposal']['seconds'])/(a['seconds']+a['common_proposal']['seconds']),
        compiled_qualified=sum(a['qualified']),active_tail_qualified=sum(b['qualified']),
        compiled_max_loss=max(a['loss']),active_tail_max_loss=max(b['loss']),
        compiled_max_width=max(a['width']),active_tail_max_width=max(b['width']),
        compiled_counts=a['counts'],active_tail_counts=b['counts'],complete_service=False))

support=load(ROOT/'results119/supporting_tail119/SUPPORTING_TAIL119.json')
support_summary=[]
for risk in ('0','1/2','3/4','7/8','15/16','31/32','63/64','255/256'):
    rows=[r for r in support['rows'] if r['alpha']==risk]
    support_summary.append(dict(alpha=risk,cells=len(rows),width_winners=dict(Counter(r['width_winner'] for r in rows)),
        maximum_width_to_theorem_bound=max(float(F(r['active']['width'])/F(r['active']['bound'])) for r in rows),
        active_distinct_queries=[min(r['active']['unique_queries'] for r in rows),max(r['active']['unique_queries'] for r in rows)],
        whole_distinct_queries=[min(r['whole_support']['unique_queries'] for r in rows),max(r['whole_support']['unique_queries'] for r in rows)],
        actual_active_total_queries=sum(r['active']['unique_queries'] for r in rows),
        actual_whole_total_queries=sum(r['whole_support']['unique_queries'] for r in rows)))

totals=dict(primary_decisions=sum(len(d['rows']) for p,d in allrecords.items() if p.startswith('catalogue/')),
    timing_decisions=sum(len(d['rows']) for p,d in allrecords.items() if p.startswith('timing/')),
    files=len(files),exact_postexecution_checks=checks,source_commit=campaign['source']['executable_protocol_commit'],
    campaign_inside_seconds=campaign['total_elapsed_seconds'],acquisition_shared_seconds=acquisition['seconds'],
    primary_service_seconds=sum(r['primary144_service_seconds'] for r in frontier),
    reference_seconds=sum(r['seconds'] for r in reference['records']),
    reference_unique_actions=sum(r['unique_policy_queries'] for r in reference['records']),
    timing_process_wall_seconds=sum(r['elapsed_seconds'] for r in campaign['processes']),
    primary_exact_fallbacks=sum(r['exact_fallbacks'] for r in frontier),
    primary_returned_action_repairs=sum(r['returned_actions_changed'] for r in frontier),
    maximum_primary_regret_upper=max(r['primary_max_regret_upper'] for r in frontier),
    native_record_audit=native_audit,contrast_summary=dict(contrast_summary),
    relu_hinge_identical_record_pairs=len(identities),relu_hinge_identical_decision_pairs=sum(r['rows'] for r in identities),
    active_tail_median_faster_counts={c:sum(r['median_time_ratio']<1 for r in comparisons if r['control']==c) for c in ('compiled','geometric')},
    active_tail_primary_faster_counts={c:sum(r['primary_time_ratio']<1 for r in comparisons if r['control']==c) for c in ('compiled','geometric')},
    supporting_checks=support['checks'],supporting_status=support['status'])

result=dict(totals=totals,frontier=frontier,comparisons=comparisons,acquisition=standalone,
    scaling=scaling,representation_identity=identities,supporting=support_summary,
    source_hashes={str(p.relative_to(ROOT)):sha(p) for p in (RAW/'CAMPAIGN119.json',RAW/'AUDIT119.json',RAW/'REFERENCE119.json',RAW/'CATALOGUE119.json',ROOT/'SOURCE_FREEZE119.json')},
    interpretation='Post-execution reporting only. Bounds are original-policy certificates, not exact regret observations. Same source, original objective, fixed tolerance, 7 complete timing repeats. Component-sum full cost is transparently assembled from actual recorded acquisition/loading/service costs, not retimed. Hinge includes complete underlying ReLU acquisition and its own encoding serialization.')
economic_pairs=[]
for rec in reference['records']:
    for control,treatment in (('online','relu'),('quadratic','relu'),('grid','relu'),('poly3','relu'),('spline','relu'),('quadratic','online')):
        lower=[];upper=[];same=cheaper=costlier=0
        for state in rec['states']:
            policies={v['policy']:v for v in state['policies']}
            a,b=(policies[arm+'/compiled'] for arm in (control,treatment))
            if a['action']==b['action']:
                lo=hi=F(0);same+=1
            else:
                lo,hi=fr(b['lower'])-fr(a['upper']),fr(b['upper'])-fr(a['lower'])
            cheaper+=int(hi<0);costlier+=int(lo>0);lower.append(lo);upper.append(hi)
        economic_pairs.append(dict(alpha=rec['alpha'],control=control,treatment=treatment,
            mean_difference_lower=math.nextafter(float(sum(lower)/144),-math.inf),
            mean_difference_upper=math.nextafter(float(sum(upper)/144),math.inf),
            exact_mean_lower=str(sum(lower)/144),exact_mean_upper=str(sum(upper)/144),
            same=same,treatment_strictly_lower_cost=cheaper,treatment_strictly_higher_cost=costlier,
            not_resolved=144-same-cheaper-costlier))
dump('R119_ECONOMIC_COMPARISONS.json',economic_pairs)
dump('R119_NUMERICAL_REVIEW.json',result)
flat=[{k:v for k,v in r.items() if not isinstance(v,(list,dict))} for r in frontier]
with (OUT/'R119_FRONTIER48.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
print(json.dumps(totals,indent=2))
print('COMPARISONS',json.dumps(comparisons,indent=2))
print('SCALING',json.dumps([{k:v for k,v in r.items() if not k.endswith('counts')} for r in scaling],indent=2))
print('SUPPORTING',json.dumps(support_summary,indent=2))
