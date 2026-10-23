"""Complete predeclared R126 economics, operation, timing and adoption report."""
import argparse,collections,statistics
from common126 import *


def group_key(r): return tuple(r[k] for k in ('index','budget','arm','training_loss','mode'))
def mean(values): return sum(map(F,values),F(0))/len(values)


def price_interval(own,competitors,N,optimistic):
    lower=F(0); upper=None
    own_v=own['first_cost_lower' if optimistic else 'first_cost_upper']
    own_t=own['timing_min' if optimistic else 'timing_max']+own['acquisition']/N
    for other in competitors:
        other_v=other['first_cost_upper' if optimistic else 'first_cost_lower']
        other_t=other['timing_max' if optimistic else 'timing_min']+other['acquisition']/N
        c,d=own_v-other_v,own_t-other_t
        if d==0:
            if c>0 or (c==0 and not optimistic):
                return dict(empty=True,blocker=other['cohort'],reason='parallel inequality')
        elif d>0:
            bound=-c/d; upper=bound if upper is None else min(upper,bound)
        else: lower=max(lower,-c/d)
        if upper is not None and (upper<lower or (upper==lower and not optimistic)):
            return dict(empty=True,blocker=other['cohort'],reason='incompatible price inequalities')
    return dict(empty=False,lower=lower,upper=upper,finite_binding_endpoints_strict=not optimistic)


def run(primary,timings,independent,verification,output):
    out,tick,info=start(output,'all-cohort-original-economy-and-complete-work-report')
    try:
        verified=verify_inputs(); data=rows(Path(primary)/'records126.jsonl.gz')
        grouped=collections.defaultdict(list)
        for r in data: grouped[group_key(r)].append(r)
        acquisitions=rows(R123/'provenance123/inherited_costs121/fit_and_acquisition121.jsonl')
        acquisition={(r['index'],r['budget'],r['arm'],r['loss']):F(r['complete_allocated_acquisition_seconds']) for r in acquisitions}
        times=collections.defaultdict(list); parent_total=F(0); receipts=[]
        for path in timings:
            p=Path(path); cohorts=rows(p/'cohorts126.jsonl')
            parent=json.loads((p.parent/('launch-'+p.name)/'PROCESS126.json').read_text())
            if parent['returncode']!=0: raise ValueError('Cannot report an unsuccessful timing as complete')
            total=F(parent['seconds']); subtotal=sum(F(c['seconds']) for c in cohorts)
            if total<subtotal: raise ArithmeticError('Parent timer is shorter than complete cohort sum')
            residual=total-subtotal; parent_total+=total
            receipts.append(dict(path=str(p),parent_seconds=total,cohort_sum=subtotal,
                                 residual_equally_allocated=residual,cohorts=len(cohorts)))
            for c in cohorts: times[group_key(c)].append((F(c['seconds'])+residual/len(cohorts))/c['n'])
        summaries=[]
        for key,rr in sorted(grouped.items()):
            if len(rr)!=9 or len(times[key])!=3: raise ValueError('Incomplete cohort or declared timing repetitions')
            index,budget,arm,loss,mode=key; first=next(r for r in rr if r['row']==0)
            costs=F(0) if arm in ('online','uniform_dp') else acquisition[(index,budget,arm,loss)]
            counts=dict(sum((collections.Counter(r['counts126']) for r in rr),collections.Counter()))
            s=dict(cohort=key,index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,n=9,
                cost_lower=mean([r['complete_policy_lower'] for r in rr]),cost_upper=mean([r['complete_policy_upper'] for r in rr]),
                mean_regret_bound=mean([r['certified_regret_upper'] for r in rr]),
                max_regret_bound=max(F(r['certified_regret_upper']) for r in rr),
                max_action_distance_bound=max(F(r['action_distance_upper']) for r in rr),
                ordinary_qualified=sum(F(r['certified_regret_upper'])<=TAU and F(r['width'])<=OMEGA for r in rr),
                stronger_target=sum(r['target_qualified126'] for r in rr),
                direct_strict_improvements=sum(r['strict_policy_improvements126'] for r in rr),
                direct_requested_contexts=sum(r['direct_requested_terminal_contexts126'] for r in rr),
                direct_query_attempts=sum(len(r['new_queries126']) for r in rr),
                direct_paid_fallbacks=sum(r.get('fallback126') is not None for r in rr),
                numerical_failures=sum(bool(r.get('failure126')) for r in rr),
                stop_reasons=dict(collections.Counter(r['stop126'] for r in rr)),
                primary_complete_service_seconds=sum(F(r['complete_service_seconds126']) for r in rr),
                acquisition=costs,timing_min=min(times[key]),timing_max=max(times[key]),timing_median=statistics.median(times[key]),
                first_action_hex=first['action_hex'],first_cost_lower=F(first['complete_policy_lower']),first_cost_upper=F(first['complete_policy_upper']),
                counts=counts,acquisition_scope='unchanged historical component allocations including actor acquisition, training and matched-parent charges; not new process clocks',
                timing_scope='all three complete first-state parent processes; shared host, descriptive ranges, not confidence intervals')
            summaries.append(s); append(out/'cohorts_summary126.jsonl',s)
        adoption=[]; blockers=[]
        for s in summaries:
            if s['arm']!='relu': continue
            others=[o for o in summaries if o['index']==s['index'] and o['arm']!='relu']
            for N in (1,32,1000,1000000):
                item=dict(cohort=s['cohort'],amortization=N,workload_state=STATES[0],
                    sufficient=price_interval(s,others,F(N),False),optimistic=price_interval(s,others,F(N),True))
                adoption.append(item); append(out/'neural_adoption126.jsonl',item)
                same=[o for o in others if o['first_action_hex']==s['first_action_hex'] and
                    o['timing_max']+o['acquisition']/N < s['timing_min']+s['acquisition']/N]
                if same:
                    other=min(same,key=lambda o:(o['timing_max']+o['acquisition']/N,o['cohort']))
                    block=dict(cohort=s['cohort'],amortization=N,blocker=other['cohort'],
                        identical_original_complete_policy=True,blocked_for_every_strictly_positive_compute_price=True,
                        zero_price_is_tie_only_with_this_blocker=True,
                        conservative_seconds_gap=s['timing_min']+s['acquisition']/N-other['timing_max']-other['acquisition']/N)
                    blockers.append(block); append(out/'same_policy_cost_blockers126.jsonl',block)
        by_mode=collections.defaultdict(list)
        for r in data: by_mode[r['mode']].append(r)
        mode_summary=[]
        for mode in ('fused_control','warm_adaptive','direct_terminal','grid33'):
            rr=by_mode[mode]; counts=dict(sum((collections.Counter(r['counts126']) for r in rr),collections.Counter()))
            mode_summary.append(dict(mode=mode,decisions=len(rr),stronger_target=sum(r['target_qualified126'] for r in rr),
                ordinary_qualified=sum(F(r['certified_regret_upper'])<=TAU and F(r['width'])<=OMEGA for r in rr),
                mean_regret_upper=mean([r['certified_regret_upper'] for r in rr]),
                max_regret_upper=max(F(r['certified_regret_upper']) for r in rr),
                direct_paid_fallbacks=sum(r.get('fallback126') is not None for r in rr),
                numerical_failures=sum(bool(r.get('failure126')) for r in rr),
                total_complete_service_seconds=sum(F(r['complete_service_seconds126']) for r in rr),counts=counts))
        ind=json.loads((Path(independent)/'SUMMARY126.json').read_text())
        audit=json.loads((Path(verification)/'EXECUTION126.json').read_text())
        if audit['exit_code']!=0 or ind['contradictions']: raise ValueError('Successful report requires successful actual checks')
        paired=[]; keyed={s['cohort']:s for s in summaries}
        for actor in actors():
            d=keyed[actor+('direct_terminal',)]
            for mode in ('fused_control','warm_adaptive'):
                c=keyed[actor+(mode,)]
                p=dict(actor=actor,comparator=mode,direct_stronger_target=d['stronger_target'],control_stronger_target=c['stronger_target'],
                    direct_timing_range=[d['timing_min'],d['timing_max']],control_timing_range=[c['timing_min'],c['timing_max']],
                    direct_definitely_faster_under_observed_ranges=d['timing_max']<c['timing_min'],
                    control_definitely_faster_under_observed_ranges=c['timing_max']<d['timing_min'],
                    acquisition_same=True,direct_complete_counts=d['counts'],control_complete_counts=c['counts'])
                paired.append(p);append(out/'matched_service_work126.jsonl',p)
        summary=dict(primary_decisions=len(data),cohorts=len(summaries),timing_decisions=528,states=STATES,
            mode_summary=mode_summary,neural_adoption_regions=len(adoption),
            empty_sufficient_neural_regions=sum(x['sufficient']['empty'] for x in adoption),
            empty_optimistic_neural_regions=sum(x['optimistic']['empty'] for x in adoption),
            same_policy_cost_blockers=len(blockers),matched_work_comparisons=len(paired),
            direct_observed_range_speed_wins=sum(x['direct_definitely_faster_under_observed_ranges'] for x in paired),
            control_observed_range_speed_wins=sum(x['control_definitely_faster_under_observed_ranges'] for x in paired),
            complete_timing_parent_seconds=parent_total,timing_cost_reconciliation=receipts,
            complete_primary_child_seconds=json.loads((Path(primary)/'EXECUTION126.json').read_text())['seconds'],
            independent_audit=ind,saved_algebra_and_timing_audit=audit,
            new_independent_seconds=json.loads((Path(independent)/'EXECUTION126.json').read_text())['seconds'],
            new_algebra_verification_seconds=audit['seconds'],source=verified,
            confidence_intervals=None,confidence_interval_reason='prespecified deterministic finite census and shared-host descriptive timing; no population samples',
            original_model_unchanged=True,independent_refitting_executed=False,
            historical_total_research_cost_known=False,
            unmeasured_historical_work='earlier interrupted parent-process clocks remain unknown; not imputed zero')
        write(out/'SUMMARY126.json',summary)
        lines=['# R126 original-economy direct decision-service study','',
            'All 1,584 predeclared primary decisions and 528 serial timing decisions are retained. The nine dyadic states form a deterministic finite census, not a population sample. All original risk laws, constraints, actor bytes and the implemented future controller remain fixed.','',
            '| Service | Decisions | Stronger target | Mean certified regret | Compiled terminal rows | Complete service seconds |',
            '|---|---:|---:|---:|---:|---:|']
        for s in mode_summary:
            lines.append(f"| {s['mode']} | {s['decisions']} | {s['stronger_target']} | {float(s['mean_regret_upper']):.8g} | {s['counts'].get('compiled_terminal_rows',0)} | {float(s['total_complete_service_seconds']):.6f} |")
        lines+=['',f"Independent original-economic reconstruction: {ind['interval_containments']}/{ind['decisions']} interval containments, {ind['regret_bounds_confirmed']}/{ind['decisions']} claimed regret bounds confirmed, {ind['contradictions']} contradictions. All unresolved checks remain unresolved.",'',
            f"Independent matched-policy comparisons: {ind['exact_policy_ties']} exact complete-policy ties, {ind['direct_strict_policy_improvements']} certified direct-service gains, {ind['direct_strict_policy_losses']} certified direct-service losses, and {ind['unresolved_policy_order']} unresolved orderings.",'',
            f"Neural adoption: {summary['empty_sufficient_neural_regions']}/{len(adoption)} sufficient regions empty; {summary['empty_optimistic_neural_regions']}/{len(adoption)} optimistic outer regions empty. {len(blockers)} cases have an exact same-policy conventional cost blocker under recorded acquisition allocations and all observed timing ranges.",'',
            'The first-state timing workload is distinct from the nine-state economic census. Prices and amortization are conditional sensitivity scenarios. Every complete process overhead is allocated, all actor acquisition costs are retained, and every refusal, unused query and paid fallback is charged. Current independent economic verification is additional research work. Unknown interrupted historical clocks remain unknown.','',
            'A sharper certificate at an unchanged action is not an observed policy improvement. All seven representation families share the same certificate machinery; the matched ReLU/hinge comparisons test identity, not neural specificity.']
        (out/'RESULTS126.md').write_text('\n'.join(lines)+'\n')
        finish(out,tick,primary_decisions=len(data),cohorts=len(summaries),source=verified)
    except BaseException: fail(out,tick); raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--timing',action='append',required=True)
    p.add_argument('--independent',required=True);p.add_argument('--verification',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.primary,a.timing,a.independent,a.verification,a.output)
