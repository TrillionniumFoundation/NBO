"""Exact finite-catalogue payoff closure; no new statistical observations.

The input is the complete, simultaneous R16 216-event menu family. Every
binary64 interval endpoint is interpreted exactly. Stage-prefix work remains
an accounting allocation, not an independently measured stopping-time clock.
"""
from __future__ import annotations
import hashlib, json, math
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]
METHODS = ('nbo_scalar', 'vector_costate', 'raw_actor', 'dpo_actor', 'raw_saa')
BASE = 'reference'

def rational(value):
    if isinstance(value, F): return value
    if isinstance(value, bool): raise ValueError('boolean is not a numerical endpoint')
    if isinstance(value, (float, int)) and math.isfinite(value): return F(value)
    raise ValueError('finite numerical endpoint required')

def upper_float(x):
    y = float(x)
    return math.nextafter(y, math.inf) if F(y) < x else y

def lower_float(x): return -upper_float(-x)

def closure(nodes, intervals):
    """Return D[i,j] >= v[j]-v[i]; exact shortest-path upper envelopes."""
    nodes = tuple(nodes)
    if not nodes or len(set(nodes)) != len(nodes): raise ValueError('distinct nodes required')
    d = {(i,j): (F(0) if i == j else None) for i in nodes for j in nodes}
    for a,b,lo,hi in intervals:
        lo,hi = rational(lo),rational(hi)
        if a not in nodes or b not in nodes or lo > hi: raise ValueError('invalid contrast')
        for i,j,w in ((b,a,hi),(a,b,-lo)):
            if d[i,j] is None or w < d[i,j]: d[i,j] = w
    for k in nodes:
        for i in nodes:
            if d[i,k] is None: continue
            for j in nodes:
                if d[k,j] is None: continue
                x = d[i,k]+d[k,j]
                if d[i,j] is None or x < d[i,j]: d[i,j] = x
    if any(d[i,i] < 0 for i in nodes): raise ValueError('inconsistent simultaneous intervals')
    if any(x is None for x in d.values()): raise ValueError('disconnected comparison catalogue')
    return d

def summaries(nodes, intervals, costs, tolerance):
    d = closure(nodes, intervals); tau = rational(tolerance)
    if tau < 0 or set(costs) != set(nodes): raise ValueError('invalid costs or tolerance')
    c = {i:rational(costs[i]) for i in nodes}
    if min(c.values()) < 0: raise ValueError('negative work')
    gap = {i:max(d[i,j] for j in nodes) for i in nodes}
    safe = [i for i in nodes if gap[i] <= tau]
    winner = min(safe, key=lambda i:(c[i],str(i))) if safe else None
    return d,gap,winner

def make_report():
    p = ROOT/'revisions/2026-10-04-r16/results/continuation_menu/report/REPORT.json'
    r = json.loads(p.read_text())
    if not r['complete'] or r['primary_event_count'] != 216: raise ValueError('incomplete family')
    nodes = [BASE]+[f'{m}@{s}' for s in ('1','2','3') for m in METHODS]
    rows=[]
    for cell,stages in sorted(r['all_stages'].items()):
        if set(stages) != {'1','2','3'}: raise ValueError('missing stage')
        edges=[]; costs={BASE:F(0)}; clocks={}
        for stage,events in stages.items():
            if len(events) != 9: raise ValueError('missing event')
            for m in METHODS:
                event=events[f'{m}_gain']; edges.append((f'{m}@{stage}',BASE,event['lower'],event['upper']))
                records=r['work'][cell][stage][m]['complete_stream_records']
                if len(records)!=16 or any(x['failed_fit'] or x['fallback'] for x in records):
                    raise ValueError('changed finite cost population')
                costs[f'{m}@{stage}']=sum((F(x['construction_and_query_seconds']) for x in records),F(0))/16
                clocks[f'{m}@{stage}']=all(x['construction_clock_is_actual_complete_process'] for x in records)
            for m in METHODS[1:]:
                event=events[f'nbo_minus_{m}'];edges.append((f'nbo_scalar@{stage}',f'{m}@{stage}',event['lower'],event['upper']))
        d,gaps,winner=summaries(nodes,edges,costs,F(1,10000))
        records=r['work'][cell]['3']['nbo_scalar']['complete_stream_records']
        shared=sum((F(x['complete_shared_confirmation_process_seconds']) for x in records),F(0))/16
        bill=sum((costs[f'{m}@3'] for m in METHODS),F(0))+shared
        candidates=[]
        for i in nodes:
            candidates.append(dict(candidate=i,regret_upper=upper_float(gaps[i]),
                regret_upper_exact=str(gaps[i]),certifies_1e4=gaps[i]<=F(1,10000),
                mean_accounted_construction_seconds=float(costs[i]),
                construction_clock_is_actual_complete_process=clocks.get(i,False),
                regret_lower=lower_float(max(-d[j,i] for j in nodes))))
        rows.append(dict(cell=cell,candidate_count=len(nodes),interval_count=len(edges),
            selected_certified_candidate=winner,selected_regret_upper=None if winner is None else upper_float(gaps[winner]),
            selected_accounted_seconds=None if winner is None else float(costs[winner]),
            shared_confirmation_seconds=float(shared),complete_comparative_study_seconds=float(bill),
            candidates=candidates,
            closed_contrasts=[dict(left=i,right=j,lower=lower_float(-d[i,j]),upper=upper_float(d[j,i]))
                for i in nodes for j in nodes]))
    out=dict(schema='nbo-r18-exact-catalogue-closure-v1',complete=True,
        source_report_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),family_alpha=0.018,
        inherited_event_count=216,new_observations=0,analysis='post-freeze deterministic simultaneous-interval closure',
        scope='16 candidate procedures per cell: reference and five methods at three stages; complete 16-stream means',
        work_scope='Recorded construction allocations; early stages are prefix allocations, not independent stopping clocks. Selection does not erase the complete comparison bill.',rows=rows)
    (R/'results').mkdir(exist_ok=True)
    (R/'results/CATALOGUE_REPORT.json').write_text(json.dumps(out,indent=2)+'\n')
    for x in rows:
        n=next(z for z in x['candidates'] if z['candidate']=='nbo_scalar@3')
        print(x['cell'],x['selected_certified_candidate'],x['selected_regret_upper'],x['selected_accounted_seconds'],'NBO3',n['regret_upper'])
    return out

if __name__=='__main__': make_report()
