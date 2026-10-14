"""Exact economic inversion of verified optimizer-sublevel action barriers.

No integration, fitting or sampling is performed. All thresholds and costs
remain rational; unknown controller identities and missing comparisons fail.
"""
from __future__ import annotations
from bisect import bisect_right
from fractions import Fraction as F
from itertools import combinations, groupby
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[1]
MAX_EXCESS=F(1,4096)
MARGIN=F(1,256)
MODELS=((8,'relu'),(8,'bernstein'),(16,'relu'),(16,'bernstein'))
IDENTITIES={
 'calibrated-relu-n8':'legacy-relu-n8',
 'calibrated-bernstein-n8':'legacy-bernstein-n8',
 'calibrated-relu-n16':'legacy-relu-n16',
 'calibrated-bernstein-n16':'legacy-bernstein-n16'}

def encode(value):
    if isinstance(value,F):return str(value)
    if isinstance(value,dict):return {str(k):encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(v) for v in value]
    return value

def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(encode(value),sort_keys=True,indent=2)+'\n')
def need(condition,message):
    if not condition:raise AssertionError(message)

def pair_band(report,first,second):
    roster=report['policies']
    need(len(roster)==len(set(roster)),'Duplicate policy identity in frozen roster')
    if first not in roster or second not in roster:raise KeyError('Unknown controller identity: '+first+', '+second)
    if first==second:return F(0),F(0)
    contrasts=report['inference']['conditional']['contrasts']
    forward=first+'-minus-'+second;reverse=second+'-minus-'+first
    if forward in contrasts:
        lo,hi=map(F,contrasts[forward]['interval_exact'])
        if reverse in contrasts:
            rlo,rhi=map(F,contrasts[reverse]['interval_exact'])
            need((lo,hi)==(-rhi,-rlo),'Contradictory directed comparison')
    elif reverse in contrasts:
        rlo,rhi=map(F,contrasts[reverse]['interval_exact']);lo,hi=-rhi,-rlo
    else:raise KeyError('Missing preallocated comparison: '+forward)
    need(lo<=hi,'Unordered actual-cost confidence interval')
    return lo,hi

def curve(service,tier=-1):
    """All left-closed exact tolerance strata, including equal barriers."""
    n=int(service['n']);reference=F(service['reference_objective'])
    pairs=service['admitted_switches'];intervals=service['tiers'][tier]['accumulated_intervals']
    need(len(pairs)==len(intervals),'Pair/interval cardinality mismatch')
    events=[]
    for item,interval in zip(pairs,intervals):
        threshold=max(F(0),F(item['switch_lower'])-reference)
        need(threshold<=MAX_EXCESS,'Integration outside declared excess domain')
        i,j=item['cell'];need(0<=i<n and 0<=j<n,'Bad state cell')
        lo,hi=map(F,interval);need(lo<=hi,'Unordered action enclosure')
        events.append((threshold,i*n+j,lo,hi))
    events.sort(key=lambda item:item[0])
    lows,highs=[F(0)]*(n*n),[F(0)]*(n*n)
    total_lo=total_hi=F(0);enabled=0;states=[]
    if not events or events[0][0]>0:states.append(dict(left=F(0),lower=F(0),upper=F(0),enabled=0))
    for threshold,group in groupby(events,key=lambda item:item[0]):
        for _,cell,lo,hi in group:
            lower,upper=min(lows[cell],lo),max(highs[cell],hi)
            total_lo+=lower-lows[cell];total_hi+=upper-highs[cell]
            lows[cell],highs[cell]=lower,upper;enabled+=1
        states.append(dict(left=threshold,lower=total_lo/(n*n),upper=total_hi/(n*n),enabled=enabled))
    for index,state in enumerate(states):
        state['right']=states[index+1]['left'] if index+1<len(states) else MAX_EXCESS
        state['right_closed']=index+1==len(states)
        need(state['left']<=state['right'],'Reversed tolerance stratum')
        if index:
            need(state['lower']<=states[index-1]['lower'],'Nonmonotone lower band')
            need(state['upper']>=states[index-1]['upper'],'Nonmonotone upper band')
    return states

def evaluate(states,excess):
    if not F(0)<=excess<=MAX_EXCESS:raise ValueError('Excess lies outside the frozen integration domain')
    position=bisect_right([F(s['left']) for s in states],excess)-1
    need(position>=0,'Missing zero-tolerance stratum')
    return states[position]

def slow_band(service,excess,tier=-1):
    """Independent cell rebuild, not incremental endpoint updates."""
    n=int(service['n']);U=F(service['reference_objective']);lower=[];upper=[]
    for i in range(n):
        for j in range(n):
            candidates=[(F(0),F(0))]
            for row,interval in zip(service['admitted_switches'],service['tiers'][tier]['accumulated_intervals']):
                if row['cell']==[i,j] and F(row['switch_lower'])<=U+excess:candidates.append(tuple(map(F,interval)))
            lower.append(min(v[0] for v in candidates));upper.append(max(v[1] for v in candidates))
    return sum(lower,F(0))/(n*n),sum(upper,F(0))/(n*n)

def transferred(base,a,b):return base[0]+F(a['lower'])-F(b['upper']),base[1]+F(a['upper'])-F(b['lower'])
def predicate(kind,lo,hi,margin=MARGIN):
    if kind=='positive':return lo>0
    if kind=='negative':return hi<0
    if kind=='equivalent':return -margin<lo and hi<margin
    raise ValueError('Unknown economic target: '+kind)

def frontier(a,b,base,kind,margin=MARGIN):
    """Largest downward-closed region supplied by these sufficient bands."""
    last=len(b)-1;stripes=[];evaluations=0
    for i,first in enumerate(a):
        while last>=0:
            evaluations+=1;lo,hi=transferred(base,first,b[last])
            if predicate(kind,lo,hi,margin):break
            last-=1
        if last<0:break
        stripes.append(dict(first_index=i,first_lower=first['left'],first_upper=first['right'],
            first_upper_closed=first['right_closed'],second_last_index=last,second_upper=b[last]['right'],
            second_upper_closed=b[last]['right_closed'],boundary_cost_interval=transferred(base,first,b[last])))
    need(evaluations<=len(a)+len(b),'Linear frontier scan exceeded its bound')
    return dict(target=kind,margin=margin if kind=='equivalent' else F(0),stripes=stripes,
        predicate_evaluations=evaluations,interpretation='largest region certified by these rectangular action enclosures; not the true joint optimizer feasibility region')

def common_limit(a,b,base,kind):
    knots=sorted(set(F(s['left']) for s in a+b)|{MAX_EXCESS})
    for threshold in knots:
        lo,hi=transferred(base,evaluate(a,threshold),evaluate(b,threshold))
        if not predicate(kind,lo,hi):return dict(nonempty=threshold>0,supremum=threshold,supremum_included=False,first_failure_interval=[lo,hi])
    lo,hi=transferred(base,evaluate(a,MAX_EXCESS),evaluate(b,MAX_EXCESS))
    return dict(nonempty=True,supremum=MAX_EXCESS,supremum_included=True,boundary_interval=[lo,hi])

def audit_curve(service,states):
    """Check each exact knot, both adjacent interiors and the closed domain."""
    events=service['admitted_switches'];endpoints=service['tiers'][-1]['accumulated_intervals']
    n=int(service['n']);U=F(service['reference_objective']);by_cell={}
    for row,interval in zip(events,endpoints):by_cell.setdefault(tuple(row['cell']),[]).append((F(row['switch_lower']),*map(F,interval)))
    checked=0;queries=set()
    for s in states:
        queries.add(F(s['left']));queries.add(F(s['right']));queries.add((F(s['left'])+F(s['right']))/2)
    for eps in sorted(queries):
        lows,highs,count=[F(0)]*(n*n),[F(0)]*(n*n),0
        for (i,j),values in by_cell.items():
            selected=[(lo,hi) for threshold,lo,hi in values if threshold<=U+eps];count+=len(selected)
            if selected:
                lows[i*n+j]=min(F(0),min(x[0] for x in selected));highs[i*n+j]=max(F(0),max(x[1] for x in selected))
        state=evaluate(states,eps)
        need((F(state['lower']),F(state['upper']),state['enabled'])==(sum(lows,F(0))/(n*n),sum(highs,F(0))/(n*n),count),'Exact all-breakpoint independent audit differs')
        checked+=1
    return dict(checked_breakpoint_and_interior_queries=checked,every_action_event_checked=True,tolerance_ties_included=True)

def main():
    started=time.perf_counter();report=read(ROOT/'results80/cost/summary.json')
    services=[read(ROOT/'results82'/f'{kind}-n{n}.json') for n,kind in MODELS]
    curves={};audits={};bindings={}
    for service in services:
        name=service['name'];n=service['n'];kind=service['basis'];metadata=report['controller_metadata'][name]
        source=ROOT/'results80/construction'/f'{kind}-n{n}/service.json'
        need(metadata['service_sha256']==sha(source)==service['source']['construction_sha256'],'Cost, construction, and integrated reference identities differ')
        legacy=IDENTITIES[name];need(legacy in report['controller_metadata'],'Missing explicitly named legacy controller')
        need(report['controller_metadata'][legacy]['n']==n and report['controller_metadata'][legacy]['basis']==kind,'Matched legacy construction identity mismatch')
        states=curve(service);curves[name]=states;audits[name]=audit_curve(service,states)
        for row in service['tiers'][-1]['sublevels']:
            state=evaluate(states,F(row['extra_objective']))
            need((F(row['lower']),F(row['upper']))==(state['lower'],state['upper']),'Original three-tolerance slice not preserved')
        bindings[name]=dict(legacy=legacy,construction_sha256=sha(source),callable_actor_sha256=metadata['actor_sha256'])
    pairs=[]
    for first,second in combinations(curves,2):
        base=pair_band(report,first,second);item=dict(first=first,second=second,attained_interval=base,targets={})
        for kind in ('positive','negative','equivalent'):
            boundary=frontier(curves[first],curves[second],base,kind)
            rows={s['first_index']:s['second_last_index'] for s in boundary['stripes']};checks=0
            for i,a in enumerate(curves[first]):
                for j,b in enumerate(curves[second]):
                    expected=predicate(kind,*transferred(base,a,b))
                    need(expected==(i in rows and j<=rows[i]),'Frontier differs from exhaustive grid');checks+=1
            boundary['independent_grid_checks']=checks
            boundary['common_excess_limit']=common_limit(curves[first],curves[second],base,kind)
            item['targets'][kind]=boundary
        pairs.append(item)
    own=[]
    for name,states in curves.items():
        for reference in ('zero',IDENTITIES[name]):
            base=pair_band(report,reference,name)
            zero=[dict(left=F(0),right=MAX_EXCESS,right_closed=True,lower=F(0),upper=F(0),enabled=0)]
            own.append(dict(reference=reference,class_name=name,attained_gain=base,
                positive_gain_region=frontier(zero,states,base,'positive'),
                all_tolerances_gain=[dict(lower_excess=s['left'],upper_excess=s['right'],upper_excess_closed=s['right_closed'],gain_interval=transferred(base,zero[0],s)) for s in states]))
    result=dict(status='passed',max_excess=MAX_EXCESS,economic_margin=MARGIN,model_curves=curves,
        callable_identity_bindings=bindings,independent_curve_audits=audits,pairwise_frontiers=pairs,own_controller_frontiers=own,
        cost_summary_sha256=sha(ROOT/'results80/cost/summary.json'),inherited_record_sha256={f'{k}-n{n}.json':sha(ROOT/'results82'/f'{k}-n{n}.json') for n,k in MODELS},
        model_tolerance_strata=sum(map(len,curves.values())),comparison_targets=18,
        independent_frontier_grid_checks=sum(t['independent_grid_checks'] for p in pairs for t in p['targets'].values()),
        new_independent_cost_rows=0,new_fitting_attempts=0,
        statistical_scope='Simultaneous over the continuum of tolerances on the existing R80 joint event; no statistical guarantee for a changed future actor, labels or economic law.',
        algorithmic_scope='Exact inversion of a sufficient rectangular certificate; not exact common-parameter optimizer identification or a measured training-speed comparison.')
    save(ROOT/'results83/frontier.json',result)
    elapsed=time.perf_counter()-started
    save(ROOT/'audit/FRONTIER_WORK83.json',dict(seconds=elapsed,frontier_sha256=sha(ROOT/'results83/frontier.json')))
    print(json.dumps(encode(dict(status='passed',model_tolerance_strata=result['model_tolerance_strata'],comparison_targets=18,independent_frontier_grid_checks=result['independent_frontier_grid_checks'],seconds=elapsed)),indent=2),flush=True)
if __name__=='__main__':main()
