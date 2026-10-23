"""All prespecified rows and complete-cost summaries, without population claims."""
import argparse,collections,statistics
from common125 import *

def groupkey(r):return tuple(r[k] for k in ('index','budget','arm','training_loss','mode'))
def mean(xs):return sum(map(F,xs),F(0))/len(xs)
def price_interval(own,others,N,optimistic):
 lo=F(0);hi=None;reason=None
 vo=own['first_cost_lower' if optimistic else 'first_cost_upper']
 to=own['timing_min' if optimistic else 'timing_max']+own['acquisition']/N
 for other in others:
  vc=other['first_cost_upper' if optimistic else 'first_cost_lower']
  tc=other['timing_max' if optimistic else 'timing_min']+other['acquisition']/N
  c,d=vo-vc,to-tc
  # Conservative sufficient uses <= at endpoints but explicitly flags that
  # equality endpoints are excluded. Optimistic outer region keeps endpoints.
  if d==0:
   if c>0 or (c==0 and not optimistic):return dict(empty=True,blocking_cohort=other['cohort'],reason='parallel cost line')
  elif d>0:
   b=-c/d;hi=b if hi is None else min(hi,b)
  else:lo=max(lo,-c/d)
  if hi is not None and (hi<lo or (hi==lo and not optimistic)):return dict(empty=True,blocking_cohort=other['cohort'],reason='incompatible cost inequalities')
 return dict(empty=False,price_lower=lo,price_upper=hi,finite_endpoints_strict=not optimistic)

def run(primary,timings,independent,verification,output):
 out,tick,info=start(output,'complete-deterministic-report')
 try:
  verified=verify_inputs();data=rows(Path(primary)/'records125.jsonl.gz')
  cc=rows(Path(primary)/'cohorts125.jsonl');groups=collections.defaultdict(list)
  for r in data:groups[groupkey(r)].append(r)
  cost=rows(R123/'provenance123/inherited_costs121/fit_and_acquisition121.jsonl')
  costs={(r['index'],r['budget'],r['arm'],r['loss']):F(r['complete_allocated_acquisition_seconds']) for r in cost}
  timed=collections.defaultdict(list);timing_process_total=F(0)
  for path in timings:
   p=Path(path);cs=rows(p/'cohorts125.jsonl');execution=json.loads((p/'EXECUTION125.json').read_text())
   # Complete child process includes source checks, imports, configuration,
   # loading, every refused proposal, gzip output and inter-cohort overhead.
   parent=json.loads((p.parent/('launch-'+p.name)/'PROCESS125.json').read_text())
   total=F(parent['seconds']);subtotal=sum(F(c['seconds']) for c in cs)
   residual=max(F(0),total-subtotal);timing_process_total+=total
   for c in cs:timed[groupkey(c)].append((F(c['seconds'])+residual/len(cs))/c['n'])
  summaries=[]
  for k,rr in sorted(groups.items()):
   i,b,a,l,m=k;f=costs.get((i,b,a,l),F(0));ts=timed[k]
   if len(rr)!=4 or len(ts)!=3:raise ValueError('Incomplete declared cohort')
   first=next(r for r in rr if r['row']==0)
   s=dict(cohort=k,index=i,budget=b,arm=a,training_loss=l,mode=m,n=len(rr),cost_lower=mean([r['complete_policy_lower'] for r in rr]),cost_upper=mean([r['complete_policy_upper'] for r in rr]),regret_max=max(F(r['certified_regret_upper']) for r in rr),regret_mean=mean([r['certified_regret_upper'] for r in rr]),rms_action_distance_upper=float(mean([F(r['certified_regret_upper']) for r in rr]))**.5,action_error_basis='strong convexity mu=2; distance to original optimal-future q optimizer',accepted=sum(r.get('accepted125',False) for r in rr),stronger_target=sum(r['target_qualified125'] for r in rr),gain_lower_sum=sum((F(r.get('gain_lower125',0)) for r in rr),F(0)),new_terminal_nodes=sum(r['new_terminal_nodes125'] for r in rr),query_attempts=sum(len(r['new_queries125']) for r in rr),stops=dict(collections.Counter(r['stop125'] for r in rr)),failures=sum(bool(r.get('failure125')) for r in rr),acquisition=f,timing_min=min(ts),timing_max=max(ts),timing_median=statistics.median(ts),timing_scope='three serial complete one-state services at (1/4,1/4), shared unregulated host',first_cost_lower=F(first['complete_policy_lower']),first_cost_upper=F(first['complete_policy_upper']),historical_acquisition_clock_scope='inherited measured component allocation, not newly observed standalone process',counts=dict(sum((collections.Counter(r['counts125']) for r in rr),collections.Counter())))
   summaries.append(s);append(out/'cohorts_summary125.jsonl',s)
  adoption=[]
  for s in summaries:
   if s['arm']!='relu':continue
   competitors=[x for x in summaries if x['index']==s['index'] and x['arm']!='relu']
   for N in (1,32,1000,1000000):
    d=dict(cohort=s['cohort'],N=N,workload_state=[.25,.25],original_objective='actual implemented future controller J',same_state_economics_and_complete_service_timing=True,sufficient=price_interval(s,competitors,F(N),False),optimistic=price_interval(s,competitors,F(N),True))
    adoption.append(d);append(out/'neural_adoption125.jsonl',d)
  ind=json.loads((Path(independent)/'SUMMARY125.json').read_text());check=json.loads((Path(verification)/'EXECUTION125.json').read_text())
  summary=dict(primary_decisions=len(data),cohorts=len(summaries),timing_decisions=702,accepted=sum(s['accepted'] for s in summaries),stronger_target=sum(s['stronger_target'] for s in summaries),all_original_qualified=sum(F(r['certified_regret_upper'])<=TAU and F(r['width'])<=OMEGA for r in data),query_attempts=sum(s['query_attempts'] for s in summaries),new_terminal_nodes=sum(s['new_terminal_nodes'] for s in summaries),failures=sum(s['failures'] for s in summaries),neural_adoption_regions=len(adoption),empty_sufficient=sum(r['sufficient']['empty'] for r in adoption),empty_optimistic=sum(r['optimistic']['empty'] for r in adoption),independent_audit=ind,algebra_and_timing_audit=check,source=verified,confidence_intervals=None,reason_no_confidence_intervals='Fixed deterministic census and unregulated timing repeats; no iid population sample or stochastic inference',theory_scope='Operational localization experiment; full-support interpolation theorem tested separately by exact rational fixtures, not implemented in these services',historical_total_research_cost_known=False,historical_missing_clock_reason='Published R122 custody records explicitly lack interrupted parent clocks; do not impute zero',complete_primary_child_seconds=json.loads((Path(primary)/'EXECUTION125.json').read_text())['seconds'],complete_timing_parent_seconds=timing_process_total,new_independent_seconds=json.loads((Path(independent)/'EXECUTION125.json').read_text())['seconds'],new_verification_seconds=check['seconds'])
  write(out/'SUMMARY125.json',summary)
  lines=['# R125 deterministic original-economy results','',f"All {len(data)} prespecified primary decisions and 702 timed decisions are retained.",'','This is a four-state census; no population inference or confidence interval is claimed. Cost bounds refer to the original continuous-risk Bellman model with the unchanged implemented future controller. The stronger target is 1/65536, separate from service qualification 1/256 and width 1/8192.','',f"Accepted additional strict policy improvements: {summary['accepted']}; stronger-target successes: {summary['stronger_target']}; enhancement failures: {summary['failures']}.",'',f"Independent contained intervals: {ind['contained']}/{ind['decisions']}; accepted gains independently confirmed: {ind['accepted_gain_confirmed']}/{ind['accepted']}; contradictions: {ind['contradictions']}. Unresolved checks remain unresolved.",'',f"First-state, complete-cost neural regions: {summary['empty_sufficient']}/{len(adoption)} sufficient regions empty; {summary['empty_optimistic']}/{len(adoption)} optimistic regions empty.",'','All 234 cohort details, inherited acquisition allocations, query failures, support certificates, accepted and rejected candidates, independent rational witnesses, and parent process clocks accompany this summary. The total historical research bill is unknown because some earlier interrupted parent clocks are absent.','']
  (out/'RESULTS125.md').write_text('\n'.join(lines))
  finish(out,tick,primary_decisions=len(data),cohorts=len(summaries),source=verified)
 except BaseException:fail(out,tick);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--timing',action='append',required=True);p.add_argument('--independent',required=True);p.add_argument('--verification',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.primary,a.timing,a.independent,a.verification,a.output)
