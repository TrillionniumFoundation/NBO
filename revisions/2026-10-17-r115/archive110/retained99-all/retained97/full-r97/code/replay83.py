"""R83 recovery without rewriting the interrupted R82 execution.

Both original arithmetic implementations run on every subbox. The four old
records, source freeze and failed-run log remain byte-identical. A completed
R83 execution and later replay have separate clocks and explicit boundaries.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
import argparse,json,resource,time
import study82 as old
import frontier83 as new
R=Path(__file__).resolve().parents[1]

def services():
    old.verify_freeze()
    return [old.read(R/'results82'/f'{kind}-n{n}.json') for n,kind in old.MODELS]

def transfers(records):
    report=old.read(R/'results80/cost/summary.json');pairwise=[];own=[]
    for first,second in combinations(records,2):
        base=new.pair_band(report,first['name'],second['name'])
        for tier in range(len(old.RUNGS)):
            for i,eps in enumerate(old.TOLERANCES):
                a=first['tiers'][tier]['sublevels'][i];b=second['tiers'][tier]['sublevels'][i]
                lo,hi=new.transferred(base,a,b)
                pairwise.append(dict(first=first['name'],second=second['name'],rung=tier,extra_objective=eps,
                    attained_interval=base,optimizer_sublevel_interval=[lo,hi],sign='positive' if lo>0 else 'negative' if hi<0 else 'unresolved',
                    equivalence_at_1_over_256=(-new.MARGIN<lo and hi<new.MARGIN),
                    coarse_interval=[base[0]-F(a['coarse_radius'])-F(b['coarse_radius']),base[1]+F(a['coarse_radius'])+F(b['coarse_radius'])]))
    for record in records:
        name=record['name']
        for reference in ('zero',new.IDENTITIES[name]):
            base=new.pair_band(report,reference,name)
            for item in record['tiers'][-1]['sublevels']:
                lo,hi=base[0]-F(item['upper']),base[1]-F(item['lower'])
                own.append(dict(reference=reference,class_name=name,extra_objective=F(item['extra_objective']),reference_minus_class=[lo,hi]))
    old.need(len(pairwise)==72 and len(own)==24,'Complete predeclared comparison catalogue')
    return dict(pairwise=pairwise,own_controller=own,original_cost_summary_sha256=new.sha(R/'results80/cost/summary.json'),
        statistical_family='Existing R80 joint event; no additional observations or failure probability',
        identity_resolution='Exact frozen policy roster and explicit calibrated-to-legacy mapping; missing names fail closed')

def original_prefix_work():
    log=R/'audit/build-logs/execute82.log';items=[]
    for line in log.read_text().splitlines():
        if line.startswith('{'):
            try:row=json.loads(line)
            except json.JSONDecodeError:continue
            if all(k in row for k in ('model','r','q','seconds','boxes')):items.append(row)
    expected={(f'{k}-n{n}',r,q) for n,k in old.MODELS for r,q in old.RUNGS}
    old.need({(x['model'],x['r'],x['q']) for x in items}==expected and len(items)==16,'Missing or duplicate inherited integration clocks')
    return dict(log_sha256=new.sha(log),recorded_integration_tiers=items,summed_logged_integration_seconds=sum(x['seconds'] for x in items),
        scope='Sum of printed integration-phase clocks from the failed R82 run, not its complete service or publication wall clock. No missing clock is inferred.')

def main(full,execute=False):
    begin=time.perf_counter()
    if execute:
        import freeze83
        freeze83.verify()
    records=services()
    if execute and (R/'results83/EXECUTION83.json').exists():raise AssertionError('Preserve the first completed execution; use --full for replay')
    bound_files={str(p.relative_to(R)):new.sha(p) for p in (R/'results82').glob('*.json')}
    source_before=new.sha(R/'SOURCE_FREEZE82.json')
    for record in records:
        U,actions,pairs,meta=old.inputs(record['n'],record['basis'])
        old.need(str(U)==record['reference_objective'] and old.encode(pairs)==record['admitted_switches'],'Inherited admitted switch catalogue differs')
        old.need(meta==record['source'],'Inherited source bindings differ')
    reproduced=False
    try:old.transfer(records)
    except KeyError as exc:
        old.need('calibrated-relu-n8-minus-relu-n8' in str(exc),'Different legacy failure');reproduced=True
    old.need(reproduced,'Pinned failed transfer did not reproduce the recorded identity error')
    work={}
    if full:
        for n,kind in old.MODELS:
            result,times=old.model(n,kind)
            old.need(old.encode(result)==old.read(R/'results82'/f'{kind}-n{n}.json'),'Full paired re-integration differs: '+kind+f'-n{n}')
            work[result['name']]=times
    movement=transfers(records);new.save(R/'results83/transfer.json',movement)
    for path,h in bound_files.items():old.need(new.sha(R/path)==h,'Original numerical record modified')
    old.need(new.sha(R/'SOURCE_FREEZE82.json')==source_before,'Original freeze changed')
    boxes=sum(x['boxes'] for record in records for tier in record['tiers'] for x in tier['per_action'])
    midpoints=sum(x['exact_midpoint_checks'] for record in records for tier in record['tiers'] for x in tier['per_action'])
    result=dict(status='passed' if full else 'stored_record_checks_passed_not_full_reintegration',full_reintegration=full,
        baseline_attempt_commit='e6d2b89f4f113f4b54b5f270359fafdc7bee67c4',controlling_review_commit='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',
        source_freeze82_sha256=source_before,source_freeze83_sha256=new.sha(R/'SOURCE_FREEZE83.json') if (R/'SOURCE_FREEZE83.json').exists() else None,
        inherited_record_sha256=bound_files,legacy_failure_reproduced=True,original_failure_not_relabelled_success=True,original_scientific_clocks_replaced=False,
        integration_implementations=['outward_binary64_centered','directed_integer_expanded'],model_count=4,
        original_switches=sum(s['source']['all_switches'] for s in records),integrated_alternatives=sum(len(s['admitted_switches']) for s in records),
        paired_boxes_per_implementation=boxes if full else 0,exact_rational_midpoint_checks=midpoints if full else 0,
        complete_model_allowance_rung_bands=48,pairwise_transfers=72,own_controller_transfers=24,new_independent_cost_rows=0,new_fitting_attempts=0,
        old_integration_work=original_prefix_work(),current_replay_work=work,environment=old.environment(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        seconds=time.perf_counter()-begin,scope='Entire original two-date actionwise integration; fixed terminal actor and labels. Independent large vector-tree regeneration is not claimed.')
    new.save(R/('audit/REPLAY83.json' if full else 'audit/RECORD_CHECK83.json'),result)
    if execute:
        old.need(full,'Execution requires both full implementations')
        result['clock_scope']='First completed R83 recovery through verification and transfer calculations, excluding this execution-record serialization; not the old R82 service clock.'
        new.save(R/'results83/EXECUTION83.json',result)
        new.save(R/'results83/EXECUTION_CLOCK83.json',dict(seconds_through_execution_record=time.perf_counter()-begin,execution_sha256=new.sha(R/'results83/EXECUTION83.json')))
    print(json.dumps({k:result[k] for k in ('status','model_count','original_switches','integrated_alternatives','paired_boxes_per_implementation','exact_rational_midpoint_checks','seconds')},indent=2),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--execute',action='store_true');a=p.parse_args();main(a.full or a.execute,a.execute)
