"""Frozen deterministic R122 evidence, economics and complete-work reporter.

This program reads saved records only. It never fits an actor, draws a state,
calls an economic solver, or repeats a timing process. Fractions preserve every
saved binary clock and rational numerical endpoint exactly. Deployment-price
domains are conditional measured-cost scenarios, not population adoption tests.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, io, json, math, time
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from common122 import ROOT, REPO, R121, ACTOR_COMMIT, N, SERVICES, catalog, identities, key, digest, plain, dump, start, finish, fail, verify_source, validated_primary

VOLUMES=(32,256,4096,65536)
SCENARIOS=('primary32','timing00','timing01','timing02')
FIELDS=('index','budget','arm','loss','service')
TAU=F(1,256)

def require(condition,message):
    if not condition: raise ValueError(message)

def exact(value):
    if isinstance(value,float):
        require(math.isfinite(value),'Nonfinite saved number')
        return F(value)
    return F(value)

def cell(row): return tuple(row[k] for k in FIELDS)
def cell_dict(k): return dict(zip(FIELDS,k))
def actor(k): return k[:4]
def control(k): return k[:4]+('control',)
def label(k): return '/'.join(map(str,k))
def average(xs):
    xs=list(xs); require(bool(xs),'Empty mean'); return sum(xs,F(0))/len(xs)

def sqrt_up(x,bits=48):
    x=exact(x);require(x>=0,'Negative square-root input')
    den=1<<bits;floor=math.isqrt((x.numerator*den*den)//x.denominator)
    if F(floor*floor,den*den)<x:floor+=1
    return F(floor,den)

class Inputs:
    def __init__(self):self.files={}
    def bind(self,p):
        p=Path(p).resolve();self.files[str(p)]={'path':str(p.relative_to(REPO)) if p.is_relative_to(REPO) else str(p),'bytes':p.stat().st_size,'sha256':digest(p)};return p
    def read(self,p):return json.loads(self.bind(p).read_text())
    def rows(self,p):
        p=self.bind(p);op=gzip.open if p.suffix=='.gz' else open
        with op(p,'rt',encoding='utf-8') as f:return [json.loads(s) for s in f if s.strip()]
    def stage(self,p,source,require_outer=True):
        p=Path(p);r=self.read(p/'EXECUTION122.json');v=self.read(p/'VERIFIED_SOURCE122.json')
        require(r.get('status')=='executed' and r.get('exit_code')==0,'Required original stage did not complete: '+str(p))
        require(v.get('source_commit')==source,'Stage used a different frozen source: '+str(p))
        if require_outer:
            outer=self.read(p/'OUTER_EXECUTION122.json')
            require(outer.get('status')=='executed' and outer.get('exit_code')==0,'Required external scientific launcher failed: '+str(p))
            require(Path(outer['child_output']).resolve()==p.resolve(),'External launcher identifies another stage')
            require(exact(outer['outer_seconds'])>=exact(r['seconds'])>=0,'External launcher does not enclose child runtime')
            r=dict(r,outer_seconds=outer['outer_seconds'],outer_child_clock_includes_interpreter_imports_and_source_gate=True)
        return r

def save_rows(out,name,rows,compressed=False):
    """Stable complete JSONL and CSV; gzip has fixed metadata."""
    rows=[plain(r) for r in rows]
    keys=sorted({k for r in rows for k in r})
    j=''.join(json.dumps(r,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n' for r in rows)
    f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader()
    for r in rows:w.writerow({k:json.dumps(v,sort_keys=True,separators=(',',':')) if isinstance(v,(dict,list)) else v for k,v in r.items()})
    for ext,data in (('jsonl',j.encode()),('csv',f.getvalue().encode())):
        p=out/(name+'.'+ext+('.gz' if compressed else ''))
        with p.open('xb') as stream:stream.write(gzip.compress(data,mtime=0) if compressed else data)

def unique(rows,keyfn,message):
    result={}
    for r in rows:
        k=keyfn(r);require(k not in result,message+': duplicate '+str(k));result[k]=r
    return result

def sign(lo,hi):return 'positive' if lo>0 else 'negative' if hi<0 else 'identity' if lo==hi==0 else 'unresolved'

def all_domain():return {'empty':False,'lower':F(0),'lower_closed':True,'upper':None,'upper_closed':False}
def empty_domain():return {'empty':True,'lower':None,'lower_closed':False,'upper':None,'upper_closed':False}

def price_domain(gain,extra):
    """Exact domain lambda>=0 where gain-lambda*extra>0."""
    gain,extra=exact(gain),exact(extra)
    if extra==0:return all_domain() if gain>0 else empty_domain()
    if extra>0:
        if gain<=0:return empty_domain()
        return dict(empty=False,lower=F(0),lower_closed=True,upper=gain/extra,upper_closed=False)
    threshold=gain/extra
    if threshold<0:return all_domain()
    return dict(empty=False,lower=threshold,lower_closed=False,upper=None,upper_closed=False)

def intersection(a,b):
    if a['empty'] or b['empty']:return empty_domain()
    lo=max(a['lower'],b['lower']);lc=all(d['lower_closed'] for d in (a,b) if d['lower']==lo)
    finite=[d['upper'] for d in (a,b) if d['upper'] is not None]
    hi=min(finite) if finite else None
    hc=all(d['upper_closed'] for d in (a,b) if d['upper']==hi) if hi is not None else False
    if hi is not None and (lo>hi or (lo==hi and not(lc and hc))):return empty_domain()
    return dict(empty=False,lower=lo,lower_closed=lc,upper=hi,upper_closed=hc)

def process_costs(inputs,a,primary,cohorts):
    tim=inputs.read(a.primary/'TIMINGS122.json')
    require(len(tim['processes'])==3 and {r['repeat'] for r in tim['processes']}=={0,1,2},'All three original clocks required')
    require(all(r['exit_code']==0 for r in tim['processes']),'A timing process failed')
    total_children=sum((exact(r['outer_seconds']) for r in tim['processes']),F(0))
    main=exact(tim['primary_catalogue_seconds_excluding_children'])
    parent_extra=exact(primary['outer_seconds'])-main-total_children
    require(parent_extra>=0,'Parent process clock does not enclose main and child clocks')
    phase={'primary32':dict(n=N,total_process_seconds=main+parent_extra,inner_catalogue_seconds=main,
        parent_source_and_bookkeeping_seconds=parent_extra,child_timing_seconds_excluded=total_children,
        process_seconds_source='Primary external OUTER_EXECUTION.outer_seconds minus all three actual child outer clocks',
        interpreter_start_before_START_measured_by_external_launcher=True,max_rss_kib=primary.get('max_rss_kib'))}
    for p in tim['processes']:
        i=p['repeat'];name=f'timing{i:02d}';inner=inputs.stage(a.primary/'timing'/f'attempt{i:02d}',a.source_commit,False)
        outer=exact(p['outer_seconds']);inner_time=exact(inner['seconds'])
        require(outer>=inner_time>=0,'Fresh-process outer clock does not enclose child receipt')
        phase[name]=dict(n=16,total_process_seconds=outer,inner_process_seconds=inner_time,
            interpreter_start_and_parent_launcher_seconds=outer-inner_time,
            process_seconds_source='Actual recorded sequential child outer clock',max_rss_kib=inner.get('max_rss_kib'))
    results=[]
    for name,p in phase.items():
        total=sum((exact(r['complete_cohort_seconds']) for r in cohorts[name]),F(0))
        residual=p['total_process_seconds']-total
        require(residual>=0,'Process residual negative: '+name)
        results.append(dict(scenario=name,**p,nonoverlapping_measured_cohort_seconds=total,
            shared_process_residual_seconds=residual,
            standalone_rule='Charge the entire measured common process residual once to every hypothetical standalone service; do not add cohort components twice.',
            actual_research_rule='The original whole process is counted once; repeated standalone allocations are not independent observed processes.'))
    return {r['scenario']:r for r in results},results

def validate_and_load(a,inputs):
    p_receipt=inputs.stage(a.primary,a.source_commit)
    i_receipt=inputs.stage(a.independent,a.source_commit)
    s_receipt=inputs.stage(a.stats,a.source_commit)
    primary_start=inputs.read(a.primary/'START122.json')
    argv=primary_start['argv'];require('--states' in argv,'Original state-stage path absent from primary launch')
    state_path=Path(argv[argv.index('--states')+1]);state_path=state_path if state_path.is_absolute() else ROOT/state_path
    state_receipt=inputs.stage(state_path,a.source_commit)
    raw=inputs.rows(a.primary/'records122.jsonl');p=unique(raw,key,'Primary rows')
    require(set(p)==identities(N),'Complete 5568-row primary catalogue required')
    _,binding=validated_primary(a.primary,a.source_commit)
    require(inputs.read(a.primary/'STATES_USED122.json')==binding,'Changed original primary state binding')
    require((REPO/binding['state_directory']).resolve()==state_path.resolve(),'Primary state directory differs from original launch')
    for name in ('STATE_MANIFEST122.json','states122.json','entropy122.bin'):inputs.bind(state_path/name)
    independent=inputs.rows(a.independent/'COMPARISONS122.jsonl');ind=unique(independent,key,'Independent rows')
    require(set(ind)==set(p),'Independent evidence must cover every primary row')
    ii=inputs.read(a.independent/'INPUTS122.json');si=inputs.read(a.stats/'INPUTS122.json')
    require(ii['primary_sha256']==digest(a.primary/'records122.jsonl') and ii['primary_state_binding']==binding,'Independent evidence must bind the actual primary bytes and F/D/M identities')
    require(si['primary_sha256']==digest(a.primary/'records122.jsonl') and si['independent_sha256']==digest(a.independent/'COMPARISONS122.jsonl') and si['primary_states']==N,'Statistics must bind the actual primary and independent evidence bytes')
    stats=inputs.rows(a.stats/'STATS122.jsonl');st=unique(stats,cell,'Population rows')
    expected={k+(s,) for k in catalog() for s in SERVICES[1:]}
    require(set(st)==expected,'All 116 prespecified treatment population cells required')
    for k,r in st.items():
        require(r['n']==N and r['simultaneous_family_size']==116 and exact(r['delta'])==F(1,100),'Changed statistical family')
        require(list(map(exact,r['support']))==[F(0),TAU],'Changed original-gain support')
        require(F(0)<=exact(r['population_gain_lower'])<=exact(r['population_gain_upper'])<=TAU,'Invalid population interval')
    signed=inputs.rows(a.stats/'SIGNED_COMPARISONS122.jsonl')
    signed_map=unique(signed,lambda r:(cell(r),r['comparator']),'Signed population comparisons')
    require(set(signed_map)=={(k+(s,),c) for k in catalog() for s in SERVICES for c in ('online-control','quadratic-value-control')},'All 348 declared signed population comparisons required')
    for r in signed:
        require(r['n']==N and r['simultaneous_family_size']==348 and exact(r['delta'])==F(3,100),'Signed inference has a different sample or family')
        require(list(map(exact,r['support']))==[-TAU,TAU] and exact(r['joint_failure_at_most'])==F(1,20),'Changed signed inference support or joint scope')
        require(-TAU<=exact(r['population_gain_lower'])<=exact(r['population_gain_upper'])<=TAU,'Invalid signed population interval')
    cohorts={};clocks={};clock_rows={}
    for scenario in SCENARIOS:
        root=a.primary if scenario=='primary32' else a.primary/'timing'/('attempt'+scenario[-2:])
        n=N if scenario=='primary32' else 16
        cr=inputs.rows(root/'cohorts122.jsonl');cm=unique(cr,cell,'Cohorts '+scenario)
        require(set(cm)=={k+(s,) for k in catalog() for s in SERVICES},'Incomplete cohort menu '+scenario)
        require(all(r['n']==n for r in cr),'Wrong cohort volume')
        rr=raw if scenario=='primary32' else inputs.rows(root/'records122.jsonl');rm=unique(rr,key,'Clock rows '+scenario)
        require(set(rm)==identities(n),'Incomplete timing catalogue '+scenario)
        for rk,r in rm.items():
            require(r['qualified'] and exact(r['certified_policy_gain_lower'])>=0,'Failed production qualification/gain')
            require(r['source_commit']==a.source_commit and r['state_commit']==binding['state_commit'] and r['actor_commit']==ACTOR_COMMIT,'Source/state/model identity mismatch')
            require(r['extra_candidate_economic_queries']==0,'Undeclared second-action economic oracle')
            require(r['refinement_count'] in (0,1,2),'Undeclared refinement budget')
            require(r['paid_refinement_attempt_count']==len(r['paid_refinement_levels_started']) and r['refinement_count']<=r['paid_refinement_attempt_count']<=2,'Paid refinement attempt ledger differs from completed work')
            if r['service']=='recycled':require(r['refinement_count']==0,'Recycled service bought new anchor information')
            c=rm[rk[:-1]+('control',)]
            require(r['baseline_action']==c['action'] and r['baseline_lower']==c['complete_policy_lower'] and r['baseline_upper']==c['complete_policy_upper'],'Changed control incumbent')
            for field in ('action','baseline_action','accepted_improvement','candidate_rejected','refinement_count','certified_policy_gain_lower','improvement_stop'):
                require(r[field]==p[rk][field],'Saved clock changes action/certificate identity')
            require(r['accepted_improvement']==(r['action']!=r['baseline_action']),'Acceptance/action mismatch')
        cohorts[scenario]=cr;clocks[scenario]=cm;clock_rows[scenario]=rr
    for k,r in ind.items():
        require(r['source_commit']==a.source_commit and r['state_commit']==binding['state_commit'] and r['actor_commit']==ACTOR_COMMIT,'Independent source/state/model identity mismatch')
        require(r['original_action_hex']==p[k]['action_hex'] and r['state_hex']==p[k]['state_hex'],'Independent action/state mismatch')
        require(r['independent_compatibility'],'Original independent economic enclosures conflict with production')
        for prefix in ('independent_policy','independent_q','independent_optimum','independent_gain'):
            require(exact(r[prefix+'_lower'])<=exact(r[prefix+'_upper']),'Reversed independent interval '+prefix)
        require(exact(r['theorem_gain_lower'])==exact(p[k]['certified_policy_gain_lower']),'Independent theorem-gain identity mismatch')
    acqpath=R121/'results121/report-attempt01/tables121/fit_and_acquisition121.jsonl'
    acq=inputs.rows(acqpath)
    frozen=inputs.read(ROOT/'SOURCE_FREEZE122.json')
    require(frozen['scientific_files'].get(str(acqpath.relative_to(REPO)))==digest(acqpath),'Historical acquisition table must be authenticated in the actual frozen F manifest')
    aq=unique(acq,lambda r:(r['index'],r['budget'],r['arm'],r['loss']),'Original acquisition allocation')
    require(set(aq)=={k for k in catalog() if k[2]!='online'},'Missing one of 56 original learned-actor acquisition allocations')
    for k in catalog():
        if k[2]=='online':
            aq[k]=dict(index=k[0],budget=0,arm='online',loss='online',complete_allocated_acquisition_seconds='0',
                no_fitted_artifact=True,derived_online_identity='No fitted actor exists; every online economic query, repair and service operation is separately charged in the fresh cohort.')
    for k,r in aq.items():
        require(exact(r['complete_allocated_acquisition_seconds'])>=0,'Negative acquisition allocation')
        if k[2]=='online':require(exact(r['complete_allocated_acquisition_seconds'])==0,'Online has no fitted actor acquisition')
        else:
            require(all(clocks[s][k+(v,)]['actor_sha256']==r['model_sha256'] for s in SCENARIOS for v in SERVICES),'R121 cost assigned to a different fitted actor')
    phases,processes=process_costs(inputs,a,p_receipt,cohorts)
    return dict(primary=p,independent=ind,stats=st,signed_stats=signed,clocks=clocks,clock_rows=clock_rows,acquisition=aq,state_binding=binding,
        phases=phases,processes=processes,receipts={'states':state_receipt,'primary':p_receipt,'independent':i_receipt,'stats':s_receipt})

def economics(data):
    p,ind=data['primary'],data['independent'];groups=[];contrasts=[];states=[];counters=[]
    for k in [q+(s,) for q in catalog() for s in SERVICES]:
        rs=[p[(k[0],j,*k[1:])] for j in range(N)];ir=[ind[(k[0],j,*k[1:])] for j in range(N)]
        low=average(exact(r['independent_policy_lower']) for r in ir);high=average(exact(r['independent_policy_upper']) for r in ir)
        d=dict(**cell_dict(k),n=N,original_policy_mean_lower=low,original_policy_mean_upper=high,
            independent_mean_regret_upper=average(exact(r['independent_regret_upper']) for r in ir),
            production_mean_regret_upper=average(exact(r['certified_regret_upper']) for r in rs),
            independent_rms_action_error_upper=sqrt_up(average(exact(r['squared_original_action_error_upper']) for r in ir)),
            production_rms_action_error_upper=sqrt_up(average(exact(r['action_distance_upper'])**2 for r in rs)),
            changed_actions=sum(bool(r['accepted_improvement']) for r in rs),
            retained_baseline_first_rejections=sum(bool(r['first_rejected']) for r in rs),
            candidate_qualification_refusals=sum(r['refused_candidate_bound_attempts'] for r in rs),
            decisions_with_candidate_refusal=sum(bool(r['candidate_rejected']) for r in rs),
            candidate_algebra_attempts=sum(r['candidate_algebra_attempts'] for r in rs),
            candidate_bound_attempts=sum(r['candidate_bound_attempts'] for r in rs),
            paid_anchor_refinements=sum(r['refinement_count'] for r in rs),
            paid_anchor_refinement_attempts=sum(r['paid_refinement_attempt_count'] for r in rs),
            paid_anchor_refinement_failures=sum(r['paid_refinement_attempt_count']-r['refinement_count'] for r in rs),
            extra_candidate_economic_queries=sum(r['extra_candidate_economic_queries'] for r in rs),
            mean_certified_original_policy_gain_lower=average(exact(r['certified_policy_gain_lower']) for r in rs),
            independent_raw_gain_confirmations=sum(bool(r['independent_gain_claim_confirmed']) for r in ir),
            accepted_action_independent_gain_confirmations=sum(bool(q['independent_gain_claim_confirmed']) for r,q in zip(rs,ir) if r['accepted_improvement']),
            accepted_action_independent_candidate_containment=sum(bool(q['independent_candidate_interval_contained']) for r,q in zip(rs,ir) if r['accepted_improvement']),
            independent_candidate_interval_contained=sum(bool(r['independent_candidate_interval_contained']) for r in ir),
            independent_compatible_rows=sum(bool(r['independent_compatibility']) for r in ir),
            complete_allocated_historical_acquisition_seconds=exact(data['acquisition'][actor(k)]['complete_allocated_acquisition_seconds']),
            raw_independent_regret_may_be_looser_than_production=True,
            same_acquired_actor_not_new_training=True,
            stop_reasons=dict(sorted(Counter(r['improvement_stop'] for r in rs).items())))
        groups.append(d)
        for j,(r,q) in enumerate(zip(rs,ir)):
            states.append(dict(**cell_dict(k),row=j,action_hex=r['action_hex'],baseline_action_hex=r['baseline_action_hex'],
                state_hex=r['state_hex'],independent_policy_lower=q['independent_policy_lower'],independent_policy_upper=q['independent_policy_upper'],
                independent_gain_lower=q['independent_gain_lower'],independent_gain_upper=q['independent_gain_upper'],
                certified_gain_lower=r['certified_policy_gain_lower'],accepted=r['accepted_improvement'],
                independent_gain_claim_confirmed=q['independent_gain_claim_confirmed'],candidate_qualified=r['qualified']))
        counts=Counter()
        for r in rs:counts.update(r['counts'])
        counters.append(dict(**cell_dict(k),n=N,operation_counts=dict(sorted(counts.items())),
            label_operation_counts_if_standalone=data['acquisition'][actor(k)].get('label_operation_counts_if_standalone',{}),
            counter_events_are_not_floating_point_operation_counts=True))
        if k[-1]!='control':
            s=data['stats'][k]
            contrasts.append(dict(**s,raw_independent_sample_gain_lower=average(exact(r['independent_gain_lower']) for r in ir),
                raw_independent_sample_gain_upper=average(exact(r['independent_gain_upper']) for r in ir),
                raw_independent_gain_confirmations=d['independent_raw_gain_confirmations'],
                changed_actions=d['changed_actions'],mean_certified_gain_lower=d['mean_certified_original_policy_gain_lower'],
                raw_and_theorem_supported_statistics_distinct=True))
    return groups,contrasts,states,counters

def all_clocks(data):
    result=[];by={}
    for s in SCENARIOS:
        p=data['phases'][s]
        for k in [q+(v,) for q in catalog() for v in SERVICES]:
            r=data['clocks'][s][k];T=exact(r['complete_cohort_seconds']);cold=exact(r['cold_load_seconds']);A=exact(data['acquisition'][actor(k)]['complete_allocated_acquisition_seconds'])
            require(T>=cold>=0,'Negative nonload cohort cost')
            c=dict(**cell_dict(k),scenario=s,n=r['n'],cold_load_seconds=cold,
                complete_cohort_seconds=T,complete_service_sum_seconds=exact(r['service_sum_seconds']),
                record_serialization_seconds=exact(r['record_serialization_seconds']),
                shared_process_residual_seconds=p['shared_process_residual_seconds'],
                historical_complete_acquisition_seconds=A,
                actual_new_cohort_seconds=T+p['shared_process_residual_seconds'],
                fully_allocated_matching_cohort_seconds=A+T+p['shared_process_residual_seconds'],
                descriptive_clock_not_population_sample=True,acquisition_clock_is_historical_not_remeasured=True,
                max_rss_kib=p.get('max_rss_kib'),actor_sha256=r['actor_sha256'])
            result.append(c);by[s,k]=c
    return result,by

def cost_at(c,n):
    return c['historical_complete_acquisition_seconds']+c['shared_process_residual_seconds']+c['cold_load_seconds']+(c['complete_cohort_seconds']-c['cold_load_seconds'])*n/c['n']

def contrast(data,candidate,comparator):
    require(candidate[0]==comparator[0],'Cross-objective risk comparison forbidden')
    pairs=[]
    for j in range(N):
        a=data['independent'][(candidate[0],j,*candidate[1:])];b=data['independent'][(comparator[0],j,*comparator[1:])]
        if a['final_key_id']==b['final_key_id']:pairs.append((F(0),F(0)))
        else:
            lo=exact(b['independent_policy_lower'])-exact(a['independent_policy_upper']);hi=exact(b['independent_policy_upper'])-exact(a['independent_policy_lower'])
            lo,hi=max(-TAU,lo),min(TAU,hi);require(lo<=hi,'Qualified cross-service contrasts conflict with original qualification');pairs.append((lo,hi))
    return average(x[0] for x in pairs),average(x[1] for x in pairs)

def price_tables(data,clocks):
    volumes=[];constraints=[];menus=[];intersections=[];contrasts={}
    keys=[k+(s,) for k in catalog() for s in SERVICES]
    neural=[k for k in keys if k[2]=='relu']
    all_costs={}
    for s in SCENARIOS:
        for n in VOLUMES:
            for k in keys:
                t=cost_at(clocks[s,k],n);all_costs[s,n,k]=t
                volumes.append(dict(**cell_dict(k),scenario=s,volume=n,economic_state_units=N,
                    total_allocated_seconds=t,seconds_per_decision=t/n,
                    actual_observed_cohort_volume=clocks[s,k]['n'],
                    scenario_extrapolation=n!=clocks[s,k]['n'],same_actor_reuse_assumed=True,
                    repeated_state_or_stationarity_scope_not_new_execution=True))
            for k in neural:
                menu=[b for b in keys if b[0]==k[0] and b[2]!='relu']
                sufficient=all_domain();possible=all_domain()
                for b in menu:
                    pair=(k,b)
                    if pair not in contrasts:contrasts[pair]=contrast(data,k,b)
                    lo,hi=contrasts[pair];extra=(all_costs[s,n,k]-all_costs[s,n,b])/n
                    low_domain=price_domain(lo,extra);up_domain=price_domain(hi,extra)
                    constraints.append(dict(candidate=cell_dict(k),comparator=cell_dict(b),scenario=s,volume=n,
                        sample_gain_lower=lo,sample_gain_upper=hi,sample_gain_sign=sign(lo,hi),extra_seconds_per_decision=extra,
                        sufficient_price_domain=low_domain,upper_not_ruled_out_domain=up_domain,
                        policy_means_conditional_on_32_saved_states=True,statistical_adoption_claim=False,
                        equivalent_hinge_remains_conventional=(b[2]=='hinge')))
                    sufficient=intersection(sufficient,low_domain);possible=intersection(possible,up_domain)
                menus.append(dict(**cell_dict(k),scenario=s,volume=n,comparators=len(menu),
                    menu='every conventional representation/budget/loss/service at the same risk, including matched hinge and online',
                    sufficient_price_domain=sufficient,upper_not_ruled_out_domain=possible,
                    statistical_adoption_claim=False,neural_exclusive_advantage_claim=False))
    mmap={(r['scenario'],r['volume'],cell(r)):r for r in menus}
    for n in VOLUMES:
        for k in neural:
            sufficient=all_domain();possible=all_domain()
            for s in SCENARIOS[1:]:
                sufficient=intersection(sufficient,mmap[s,n,k]['sufficient_price_domain']);possible=intersection(possible,mmap[s,n,k]['upper_not_ruled_out_domain'])
            intersections.append(dict(**cell_dict(k),volume=n,clock_scenarios=list(SCENARIOS[1:]),
                sufficient_price_domain=sufficient,upper_not_ruled_out_domain=possible,
                descriptive_all_clock_intersection_not_future_hardware_guarantee=True))
    return volumes,constraints,menus,intersections

def fmt(x):return f'{float(exact(x)):.6g}'

def write_tex(out,groups,contrasts,clockmap,summary):
    """Complete same-column cell tables plus a compact narrative; no selected win table."""
    text=['% Automatically generated from all saved R122 evidence.','\\section{Executed support-to-action comparison}\\label{sec:results122}',
        f'The fixed comparison contains {summary["primary_decisions"]:,} primary decisions on 32 new initial states and {summary["timed_decisions"]:,} decisions in three descriptive timing processes. These timing decisions are not additional independent population observations.',
        f'Across all 116 within-actor treatment cells, {summary["positive_population_gain_cells"]} fixed simultaneous population mean-gain lower endpoints are positive. All 58 acquired-actor/risk cells, both interventions, all first refusals, and all three clocks are retained.',
        f'The interventions change {summary["changed_treatment_actions"]:,} original actions. They start {summary["paid_anchor_refinement_attempts"]:,} paid anchor refinements, complete {summary["paid_anchor_refinements"]:,}, and purchase {summary["extra_candidate_economic_queries"]} second-action economic values. Started refinements remain charged if arithmetic recovery prevents a usable support record. Independent primitive reconstruction directly confirms {summary["accepted_action_independent_gain_confirmations"]:,} of these {summary["changed_treatment_actions"]:,} accepted improvements at its own precision. Unchanged-action exact-zero comparisons are excluded from this denominator; compatibility with every production certificate is checked separately.',
        'Original policy cost, regret and action-error columns below come from the independent implementation. A coarser independent regret enclosure can exceed the production tolerance without contradicting the separately proved production certificate. The population analysis also states exactly where it intersects independent intervals with theorem-backed nonnegative gains.',
        'The full cost allocation retains every original acquisition, fit and audit charge from the immutable R121 actors, adds the complete newly observed service and common process work, and reports that allocation separately from incremental reuse cost. Price domains use the full declared conventional menu and measured hardware scenarios; they are not calibrated population adoption conclusions.']
    (out/'results122.tex').write_text('\n\n'.join(text)+'\n')
    t=['% Complete 174 policy cells.','\\section{Complete policy and work cells}\\label{dev:allcells122}',
       '\\begingroup\\setlength{\\tabcolsep}{3pt}\\scriptsize','\\begin{longtable}{llrrrrrr}','\\caption{Every risk, representation, acquisition budget, fitting loss and service. Risk indices 0 and 1 mean $\\alpha=1/2$ and $3/4$; fitting suffixes v and m mean value and marginal. $J$ is independently enclosed original mean cost; work is the fully allocated actual 32-decision primary cohort in seconds.}\\label{tab:allcells122}\\\\',
       '\\hline Cell & Service & $J_L$ & $J_U$ & Regret$_U$ & Action$_U$ & Changed & Work \\\\ \\hline\\endfirsthead',
       '\\hline Cell & Service & $J_L$ & $J_U$ & Regret$_U$ & Action$_U$ & Changed & Work \\\\ \\hline\\endhead']
    for r in groups:
        k=cell(r);name=f'{r["index"]}/{r["budget"]}/{r["arm"]}/{r["loss"][0]}'
        t.append(f'{name} & {r["service"]} & {fmt(r["original_policy_mean_lower"])} & {fmt(r["original_policy_mean_upper"])} & {fmt(r["independent_mean_regret_upper"])} & {fmt(r["independent_rms_action_error_upper"])} & {r["changed_actions"]} & {fmt(clockmap["primary32",k]["fully_allocated_matching_cohort_seconds"])} \\\\')
    t+=['\\hline\\end{longtable}','\\endgroup']
    (out/'complete_tables122.tex').write_text('\n'.join(t)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True)
    for k in ('primary','independent','stats','output'):parser.add_argument('--'+k,required=True,type=Path)
    a=parser.parse_args()
    for k in ('primary','independent','stats','output'):setattr(a,k,getattr(a,k).resolve())
    out,initial,tick=start(a.output,'report',{'claimed_source_commit':a.source_commit})
    try:
        verified=verify_source(a.source_commit);dump(out/'VERIFIED_SOURCE122.json',verified)
        inputs=Inputs();data=validate_and_load(a,inputs)
        groups,contrasts,states,counters=economics(data);clocks,clockmap=all_clocks(data)
        volumes,price_constraints,menus,all_three=price_tables(data,clockmap)
        save_rows(out,'POLICY_CELLS122',groups);save_rows(out,'SERVICE_CONTRASTS122',contrasts)
        save_rows(out,'SIGNED_POPULATION_COMPARISONS122',data['signed_stats'])
        save_rows(out,'STATE_ECONOMICS122',states,True);save_rows(out,'OPERATION_COUNTS122',counters)
        save_rows(out,'CLOCKS122',clocks);save_rows(out,'PROCESS_COSTS122',data['processes'])
        save_rows(out,'ACQUISITION_ALLOCATIONS122',[dict(**v,original_acquired_actor_commit=ACTOR_COMMIT,source='R121 immutable complete acquisition allocation; not remeasured or refitted in R122') for v in data['acquisition'].values()])
        save_rows(out,'COST_VOLUMES122',volumes);save_rows(out,'PRICE_CONSTRAINTS122',price_constraints,True)
        save_rows(out,'PRICE_MENUS122',menus);save_rows(out,'ALL_THREE_CLOCK_INTERSECTIONS122',all_three)
        summary=dict(schema='nbo.r122.complete-evidence-report.v1',source_commit=a.source_commit,actor_commit=ACTOR_COMMIT,state_commit=data['state_binding']['state_commit'],
            independent_state_units=N,primary_decisions=len(data['primary']),timed_decisions=3*16*174,
            policy_cells=len(groups),treatment_population_cells=len(contrasts),signed_population_cells=len(data['signed_stats']),all_original_clocks=list(SCENARIOS),
            joint_confidence_allocation={'safe_mean':F(1,100),'safe_threshold_events':F(1,100),'signed_mean':F(3,100),'total':F(1,20)},
            positive_signed_population_gain_cells=sum(exact(r['population_gain_lower'])>0 for r in data['signed_stats']),
            negative_signed_population_gain_cells=sum(exact(r['population_gain_upper'])<0 for r in data['signed_stats']),
            positive_population_gain_cells=sum(exact(r['population_gain_lower'])>0 for r in contrasts),
            changed_treatment_actions=sum(r['changed_actions'] for r in groups),
            paid_anchor_refinements=sum(r['paid_anchor_refinements'] for r in groups),
            paid_anchor_refinement_attempts=sum(r['paid_anchor_refinement_attempts'] for r in groups),
            paid_anchor_refinement_failures=sum(r['paid_anchor_refinement_failures'] for r in groups),
            candidate_qualification_refusals=sum(r['candidate_qualification_refusals'] for r in groups),
            extra_candidate_economic_queries=sum(r['extra_candidate_economic_queries'] for r in groups),
            raw_independent_gain_confirmations=sum(r['independent_raw_gain_confirmations'] for r in groups),
            accepted_action_independent_gain_confirmations=sum(r['accepted_action_independent_gain_confirmations'] for r in groups),
            accepted_action_independent_candidate_containment=sum(r['accepted_action_independent_candidate_containment'] for r in groups),
            accepted_action_validation_denominator=sum(r['changed_actions'] for r in groups),
            independent_candidate_interval_containment=sum(r['independent_candidate_interval_contained'] for r in groups),
            independent_compatible_rows=sum(r['independent_compatible_rows'] for r in groups),
            primary_neural_menu_domains=len([r for r in menus if r['scenario']=='primary32']),
            primary_neural_nonempty_sufficient=sum(not r['sufficient_price_domain']['empty'] for r in menus if r['scenario']=='primary32'),
            individual_timing_neural_nonempty_sufficient=sum(not r['sufficient_price_domain']['empty'] for r in menus if r['scenario']!='primary32'),
            all_three_clock_neural_nonempty_sufficient=sum(not r['sufficient_price_domain']['empty'] for r in all_three),
            all_three_clock_neural_nonempty_upper_not_ruled_out=sum(not r['upper_not_ruled_out_domain']['empty'] for r in all_three),
            full_menu_price_constraints=len(price_constraints),scenario_volumes=list(VOLUMES),
            actual_new_scientific_stage_seconds_excluding_current_report=sum((exact(v['outer_seconds']) for v in data['receipts'].values()),F(0)),
            research_timing_children_already_in_primary=True,
            original_actor_acquisition='Prior immutable R121 acquisition; full per-standalone allocations retained separately, not new measured R122 training.',
            current_report_runtime='EXECUTION122.json plus the externally written OUTER_EXECUTION122.json after this reporter exits; separately disclosed, not silently charged to deployment service or counted twice',
            external_process_clock_scope='Every scientific child interpreter/import/source gate through exit is measured by its external launcher. Launcher startup and receipt serialization are separate and are not claimed to be scientific child runtime.',
            neural_exclusive_advantage_claim=False,population_adoption_claim=False,
            all_negative_unresolved_and_conventional_winner_cells_retained=True,
            independent_audit_does_not_erase_production_or_theorem_boundaries=True)
        dump(out/'SUMMARY_REPORT122.json',summary)
        write_tex(out,groups,contrasts,clockmap,summary)
        dump(out/'INPUTS_REPORT122.json',{'files':sorted(inputs.files.values(),key=lambda r:r['path']),'scope':'Complete reporter reads; frozen transitive source separately verified.'})
        dump(out/'OUTPUT_MANIFEST122.json',{'files':[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(out.iterdir()) if p.is_file()],
            'self_and_later_execution_receipt_excluded':True})
        finish(out,initial,tick,{'read_only_reporting':True,'economic_calls':0,'new_states':0,'new_training':0,'new_timing_processes':0,'policy_cells':len(groups)})
    except BaseException:fail(out,tick);raise

if __name__=='__main__':main()
