"""Complete fresh paired cache cost report, retaining F126 primary negatives."""
import argparse,statistics
from cache126c import *
from report126 import price_interval


def group_key(r):return tuple(r[k] for k in ('index','budget','arm','training_loss','mode'))

def run(primary,timings,verification,output):
    out,tick,info=start(output,'R126C-paired-complete-cost-and-identity-report')
    try:
        gate=verify_sources();audit=json.loads((Path(verification)/'EXECUTION126.json').read_text())
        if audit['exit_code']!=0 or audit['exact_full_scientific_records']!=4224:raise ValueError('Full successful equality audit required')
        primary_path=Path(primary)
        data=rows(primary_path/'records126c.jsonl.gz'); grouped={}
        primary_cc=rows(primary_path/'cohorts126c.jsonl')
        primary_parent=json.loads((primary_path.parent/('launch-'+primary_path.name)/'PROCESS126.json').read_text())
        if primary_parent['returncode']!=0 or len(primary_cc)!=352:raise ValueError('Complete successful paired primary required')
        primary_total=F(primary_parent['seconds']);primary_subtotal=sum((F(c['seconds']) for c in primary_cc),F(0))
        if primary_total<primary_subtotal:raise ArithmeticError('Primary parent shorter than cohort sum')
        primary_extra=primary_total-primary_subtotal
        primary_complete={(c['variant126c'],group_key(c)):F(c['seconds'])+primary_extra/352 for c in primary_cc}
        primary_reconciliation=dict(parent_seconds=primary_total,cohort_seconds=primary_subtotal,
            residual_equally_allocated=primary_extra,cohorts=352)
        for r in data:grouped.setdefault((r['variant126c'],group_key(r)),[]).append(r)
        times={};receipts=[];parent_total=F(0)
        for path in timings:
            p=Path(path);cc=rows(p/'cohorts126c.jsonl')
            receipt=json.loads((p.parent/('launch-'+p.name)/'PROCESS126.json').read_text())
            if receipt['returncode']!=0:raise ValueError('Unsuccessful timing cannot enter successful report')
            seconds=F(receipt['seconds']);subtotal=sum((F(c['seconds']) for c in cc),F(0))
            if seconds<subtotal or len(cc)!=352:raise ArithmeticError('Incomplete parent cost reconciliation')
            extra=seconds-subtotal;parent_total+=seconds
            receipts.append(dict(path=str(p),parent_seconds=seconds,cohort_seconds=subtotal,residual_equally_allocated=extra,cohorts=352))
            for c in cc:times.setdefault((c['variant126c'],group_key(c)),[]).append((F(c['seconds'])+extra/352)/c['n'])
        acquisitions=rows(R123/'provenance123/inherited_costs121/fit_and_acquisition121.jsonl')
        acq={(r['index'],r['budget'],r['arm'],r['loss']):F(r['complete_allocated_acquisition_seconds']) for r in acquisitions}
        summaries=[];keyed={}
        for (variant,cohort),rr in sorted(grouped.items()):
            assert len(rr)==9 and len(times[(variant,cohort)])==3
            first=next(r for r in rr if r['row']==0);index,budget,arm,loss,mode=cohort
            s=dict(variant=variant,cohort=cohort,index=index,budget=budget,arm=arm,training_loss=loss,mode=mode,
                ordinary_qualified=sum(F(r['certified_regret_upper'])<=TAU and F(r['width'])<=OMEGA for r in rr),
                stronger_target=sum(r['target_qualified126'] for r in rr),
                complete_primary_service_seconds=primary_complete[(variant,cohort)],
                primary_service_component_seconds=sum((F(r['complete_service_seconds126c']) for r in rr),F(0)),
                counts=dict(sum((Counter(r['counts126']) for r in rr),Counter())),
                cache_counts=dict(sum((Counter(r['cache_stats126c']) for r in rr),Counter())),
                timing_min=min(times[(variant,cohort)]),timing_max=max(times[(variant,cohort)]),timing_median=statistics.median(times[(variant,cohort)]),
                acquisition=F(0) if arm in ('online','uniform_dp') else acq[(index,budget,arm,loss)],
                first_action_hex=first['action_hex'],first_cost_lower=F(first['complete_policy_lower']),first_cost_upper=F(first['complete_policy_upper']))
            summaries.append(s);keyed[(variant,cohort)]=s;append(out/'cohorts_summary126c.jsonl',s)
        comparisons=[]
        for cohort in catalog():
            u,c=(keyed[(v,cohort)] for v in VARIANTS)
            assert u['counts']==c['counts'] and u['stronger_target']==c['stronger_target']
            item=dict(cohort=cohort,uncached_primary_seconds=u['complete_primary_service_seconds'],cached_primary_seconds=c['complete_primary_service_seconds'],
                uncached_timing_range=[u['timing_min'],u['timing_max']],cached_timing_range=[c['timing_min'],c['timing_max']],
                cached_observed_range_faster=c['timing_max']<u['timing_min'],uncached_observed_range_faster=u['timing_max']<c['timing_min'],
                identical_complete_original_policy_and_economic_work=True)
            comparisons.append(item);append(out/'paired_cache_comparisons126c.jsonl',item)
        same_cache=[]
        for actor in actors():
            direct=keyed[('cached',actor+('direct_terminal',))]
            for comparator in ('fused_control','warm_adaptive'):
                control=keyed[('cached',actor+(comparator,))]
                item=dict(actor=actor,comparator=comparator,direct_timing_range=[direct['timing_min'],direct['timing_max']],control_timing_range=[control['timing_min'],control['timing_max']],
                    direct_observed_range_faster=direct['timing_max']<control['timing_min'],control_observed_range_faster=control['timing_max']<direct['timing_min'],
                    direct_stronger_target=direct['stronger_target'],control_stronger_target=control['stronger_target'],
                    direct_primary_seconds=direct['complete_primary_service_seconds'],control_primary_seconds=control['complete_primary_service_seconds'])
                same_cache.append(item);append(out/'same_cache_service_comparisons126c.jsonl',item)
        modes=[]
        for variant in VARIANTS:
            for mode in ('fused_control','warm_adaptive','direct_terminal','grid33'):
                rr=[r for r in data if r['variant126c']==variant and r['mode']==mode]
                item=dict(variant=variant,mode=mode,decisions=len(rr),stronger_target=sum(r['target_qualified126'] for r in rr),
                    complete_primary_service_seconds=sum((s['complete_primary_service_seconds'] for s in summaries if s['variant']==variant and s['mode']==mode),F(0)),
                    primary_service_component_seconds=sum((F(r['complete_service_seconds126c']) for r in rr),F(0)),
                    counts=dict(sum((Counter(r['counts126']) for r in rr),Counter())),
                    cache_counts=dict(sum((Counter(r['cache_stats126c']) for r in rr),Counter())))
                modes.append(item)
        adoption=[];blockers=[]
        for s in summaries:
            if s['arm']!='relu':continue
            others=[o for o in summaries if o['variant']==s['variant'] and o['index']==s['index'] and o['arm']!='relu']
            for N in (1,32,1000,1000000):
                item=dict(variant=s['variant'],cohort=s['cohort'],amortization=N,sufficient=price_interval(s,others,F(N),False),optimistic=price_interval(s,others,F(N),True))
                adoption.append(item);append(out/'neural_adoption126c.jsonl',item)
                same=[o for o in others if o['first_action_hex']==s['first_action_hex'] and o['timing_max']+o['acquisition']/N<s['timing_min']+s['acquisition']/N]
                if same:
                    other=min(same,key=lambda o:(o['timing_max']+o['acquisition']/N,o['cohort']))
                    block=dict(variant=s['variant'],cohort=s['cohort'],amortization=N,blocker=other['cohort'],same_complete_policy=True,
                        blocked_at_every_strictly_positive_compute_price=True,zero_price_tie_with_this_blocker=True)
                    blockers.append(block);append(out/'same_policy_cost_blockers126c.jsonl',block)
        summary=dict(primary_decisions=3168,timing_decisions=1056,exact_records_compared=4224,cohort_variants=352,
            all_scientific_outcomes_and_economic_work_identical_to_F126=True,mode_summary=modes,
            paired_cache_comparisons=176,cached_observed_range_speed_wins=sum(r['cached_observed_range_faster'] for r in comparisons),
            uncached_observed_range_speed_wins=sum(r['uncached_observed_range_faster'] for r in comparisons),
            same_cache_service_comparisons=116,direct_observed_range_speed_wins_against_cached_controls=sum(r['direct_observed_range_faster'] for r in same_cache),
            cached_control_observed_range_speed_wins=sum(r['control_observed_range_faster'] for r in same_cache),
            neural_adoption_scenarios=len(adoption),empty_sufficient_neural_regions=sum(r['sufficient']['empty'] for r in adoption),
            empty_optimistic_neural_regions=sum(r['optimistic']['empty'] for r in adoption),same_policy_cost_blockers=len(blockers),
            timing_parent_seconds=parent_total,timing_reconciliation=receipts,primary_parent_seconds=primary_total,primary_reconciliation=primary_reconciliation,
            independent_population_samples=0,confidence_intervals=None,shared_host_descriptive_clocks_only=True,
            first_F126_negative_complete_cost_result_retained=True,post_F126_prospective_algorithm_variant=True,
            original_independent_economic_audit_applies_to_identical_complete_policies=True,source=gate,
            equality_verification_seconds=audit['seconds'])
        write(out/'SUMMARY126C.json',summary)
        lines=['# R126C: a separately prospective exact-geometry algorithm study','',
          'Both uncached and cached methods were executed afresh under the second published source boundary. The first F126 primary negative complete-cost evidence is retained. This study changes certificate computation, not economic information or policy selection.','',
          '| Variant | Service | Decisions | Stronger target | Parent-allocated complete primary seconds | Terminal rows |',
          '|---|---|---:|---:|---:|---:|']
        for s in modes:lines.append(f"| {s['variant']} | {s['mode']} | {s['decisions']} | {s['stronger_target']} | {float(s['complete_primary_service_seconds']):.6f} | {s['counts'].get('compiled_terminal_rows',0)} |")
        lines+=['',f"All4,224 full scientific records equal their F126 references after deleting clocks and declared run metadata only. Cached first-state timing ranges are strictly below uncached ranges in {summary['cached_observed_range_speed_wins']}/176 cohorts; the converse holds in {summary['uncached_observed_range_speed_wins']}/176. These are descriptive observations on one shared host, not statistical confidence statements.",'',
          'All conventional representations and all strong controls receive exactly the same caching mechanism. Cache construction, model loading, parent overhead, serialization and cleanup are charged in both primary and timing totals; the service-only component is retained separately. No economic queries, previously paid service prefixes or fitted models are cached across paid services.','',
          f"Across both variant-specific neural comparisons, {summary['empty_sufficient_neural_regions']}/{len(adoption)} sufficient adoption regions and {summary['empty_optimistic_neural_regions']}/{len(adoption)} optimistic outer regions are empty; {len(blockers)} scenarios have an exact identical-policy conventional cost blocker. These conditional first-state cost calculations do not establish a neural-specific advantage."]
        (out/'RESULTS126C.md').write_text('\n'.join(lines)+'\n')
        finish(out,tick,source=gate,primary_decisions=3168,timing_decisions=1056)
    except BaseException:fail(out,tick);raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--timing',action='append',required=True);p.add_argument('--verification',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.primary,a.timing,a.verification,a.output)
