"""Fixed complete B economic, information, inference and cost reporting."""
from fractions import Fraction as F
import argparse,json,math,sys
from common124b import *
sys.path.insert(0,str(A_CODE))
from report124 import cp_lower,mean,square_root_upper,price_domain
TAU=F(1,256);THRESHOLD=F(1,2**24)

def run(primary,independent,output,timings,launches,audit):
 out,tick,info=start(output,'B-complete-fixed-report')
 try:
  verify_source();binding=boundaries();states();p=Path(primary);iv=Path(independent)
  records=rows(p/RECORDS);evaluated=rows(iv/'action_bounds124b.jsonl')
  if len(records)!=58*3*N or len(timings)!=3 or len(launches)!=4:raise ValueError('Complete fixed B census and clocks required')
  ap=Path(audit)/'EXECUTION124B.json';ar=json.loads(ap.read_text())
  if ar.get('status')!='executed' or ar.get('status_detail')!='passed' or ar.get('primary_sha256')!=digest(p/RECORDS) or ar.get('primary_decisions')!=58*3*N or ar.get('timing_decisions')!=3*58*3*TIMED_N:raise ValueError('Passing complete independent B stage audit required')
  if ar.get('timing_sha256')!=[digest(Path(t)/RECORDS) for t in timings]:raise ValueError('B audit belongs to other timing records')
  er=json.loads((iv/'EXECUTION124B.json').read_text())
  if er.get('status')!='executed' or er.get('primary_sha256')!=digest(p/RECORDS):raise ValueError('Independent economics belongs to another B primary')
  key=lambda r:tuple(r[k] for k in ('index','budget','arm','training_loss','mode'))
  ekey=lambda r,a:(tuple(r['state_hex']),float(a).hex(),float(r['alpha']).hex())
  E={(tuple(e['key'][0]),e['key'][1],e['key'][2]):e for e in evaluated};opt={}
  for e in evaluated:
   s=(tuple(e['key'][0]),e['key'][2]);opt[s]=max(opt.get(s,F(-10)),F(e['best']['optimum_lower']))
  for r in records:
   s=(tuple(r['state_hex']),float(r['alpha']).hex());opt[s]=max(opt[s],F(r['original_optimum_lower']))
  bounds={}
  for r in records:
   e=E[ekey(r,r['action'])]['best'];lo=max(F(e['j_lower']),F(r['complete_policy_lower']));hi=min(F(e['j_upper']),F(r['complete_policy_upper']))
   if lo>hi:raise AssertionError('Independent B and production final intervals contradict')
   B=opt[(tuple(r['state_hex']),float(r['alpha']).hex())];regret=min(TAU,hi-B)
   if regret<0:raise AssertionError('Negative valid original regret upper bound')
   bounds[key(r)+(r['row'],)]=dict(lower=lo,upper=hi,regret_upper=regret,raw_independent_lower=F(e['j_lower']),raw_independent_upper=F(e['j_upper']),q_lower=F(e['q_lower']),q_upper=F(e['q_upper']))
  cells={c+(m,):sorted([r for r in records if key(r)==c+(m,)],key=lambda r:r['row']) for c in catalog() for m in MODES}
  if any([r['row'] for r in rs]!=list(range(N)) for rs in cells.values()):raise ValueError('Incomplete or duplicated B cell')
  policy=[];safe=[];signed=[]
  for k,rs in cells.items():
   bs=[bounds[k+(r['row'],)] for r in rs]
   policy.append(dict(key=k,n=N,mean_original_J_lower=mean([b['lower'] for b in bs]),mean_original_J_upper=mean([b['upper'] for b in bs]),
    mean_independent_q_lower=mean([b['q_lower'] for b in bs]),mean_independent_q_upper=mean([b['q_upper'] for b in bs]),
    mean_regret_upper=mean([b['regret_upper'] for b in bs]),rms_action_error_upper=square_root_upper(mean([b['regret_upper'] for b in bs])),
    own_stage_accepted=sum(r['accepted_improvement'] for r in rs),fused_prefix_accepted=sum(r['fused_accepted_improvement'] for r in rs),
    bridge_prefix_accepted=sum(r['bridge_accepted_improvement'] for r in rs),joint_stage_accepted=sum(r['joint_accepted_improvement'] for r in rs),
    new_menu_restricted_rows=sum(r['new_menu'] is not None and r['new_menu']['distinct_paid_anchors']<2 for r in rs),
    candidate_evaluations=sum(sum(len(r[s]['entries']) if r[s] else 0 for s in ('bridge_stage','joint_stage')) for r in rs),
    any_enhancement_failures=sum(r['any_enhancement_failed'] for r in rs),
    failure_counts={s:sum(r[s] for r in rs) for s in ('fused_enhancement_failed','bridge_enhancement_failed','joint_enhancement_failed','outer_enhancement_failed','original_service_numerical_failure','original_proposal_numerical_failure')},
    dual_solves_started=sum(r['dual_solves_started'] for r in rs),dual_solves_completed=sum(r['dual_solves_completed'] for r in rs),
    floating_solver_successes=sum(r['dual_solver_successes'] for r in rs),dual_seconds=sum(F(r['dual_seconds']) for r in rs),new_original_queries=0,
    all_qualified=all(r['qualified'] for r in rs),raw_independent_means=[mean([b['raw_independent_lower'] for b in bs]),mean([b['raw_independent_upper'] for b in bs])]))
   comparisons=['own-stage']+(['joint-vs-fused'] if k[-1]=='joint' else [])
   for comparison in comparisons:
    lows=[];highs=[];count=0
    for r,b in zip(rs,bs):
     if comparison=='own-stage':origin=r['stage_incumbent_action'];cert=F(r['certified_policy_gain_lower']);ol=F(r['stage_incumbent_lower']);ou=F(r['stage_incumbent_upper'])
     else:origin=r['fused_action'];cert=F(r['certified_gain_vs_fused_lower']);ol=F(r['full_fused_record']['complete_policy_lower']);ou=F(r['full_fused_record']['complete_policy_upper'])
     if r['action']==origin:
      if cert!=0:raise AssertionError('Identical action has positive claimed gain')
      low=high=F(0)
     else:
      e=E[ekey(r,origin)]['best'];ol=max(ol,F(e['j_lower']));ou=min(ou,F(e['j_upper']))
      if ol>ou:raise AssertionError('Original incumbent production/independent intervals contradict')
      low=max(F(0),cert,ol-b['upper']);high=min(TAU,ou-b['lower'])
     if low>high:raise AssertionError('B stage/cumulative numerical gain bounds contradict')
     lows.append(low);highs.append(high);count+=cert>=THRESHOLD
    radius=F(7,16)*TAU;event=cp_lower(count,N,F(1,23200))
    safe.append(dict(key=k,comparison=comparison,n=N,numerical_mean_lower=mean(lows),numerical_mean_upper=mean(highs),
     population_lower=max(F(0),mean(lows)-radius,THRESHOLD*event),population_upper=min(TAU,mean(highs)+radius),
     hoeffding_radius=radius,threshold=THRESHOLD,certified_threshold_count=count,threshold_probability_lower=event,
     threshold_event_failure='1/23200',original_gain_support=[F(0),TAU],independent_observation_unit='fresh initial B state'))
  def compare(k,c,label):
   lows=[];highs=[];identity=k==c
   for j,(a,b) in enumerate(zip(cells[k],cells[c])):
    if a['action']==b['action']:lo=hi=F(0)
    else:
     aa,bb=bounds[k+(j,)],bounds[c+(j,)];lo=max(-TAU,bb['lower']-aa['upper']);hi=min(TAU,bb['upper']-aa['lower'])
    if lo>hi:raise AssertionError('B signed numerical intervals contradict')
    lows.append(lo);highs.append(hi)
   ml,mh=mean(lows),mean(highs);radius=F(7,8)*TAU
   return dict(key=k,comparator=c,label=label,n=N,numerical_mean_lower=ml,numerical_mean_upper=mh,
    population_lower=F(0) if identity else max(-TAU,ml-radius),population_upper=F(0) if identity else min(TAU,mh+radius),
    hoeffding_radius=radius,original_difference_support=[-TAU,TAU],identity_zero=identity,positive_means_first_algorithm_lower_original_cost=True)
  for k in cells:
   i,b,a,l,m=k;signed.append(compare(k,(i,0,'online','online','fused_full'),'same-risk-online-full-fused'))
   signed.append(compare(k,(i,b or 5,'quadratic','value','fused_full'),'same-budget-quadratic-value-full-fused'))
  if len(policy)!=174 or len(safe)!=232 or len(signed)!=348:raise AssertionError('Frozen B inference family census')
  exponential_lower=sum(F(49,4)**j/math.factorial(j) for j in range(31))
  if not exponential_lower>200000:raise AssertionError('Exact B exponential lower bound fails')
  acq={(r['index'],r['budget'],r['arm'],r['loss']):r for r in rows(R123/'provenance123/inherited_costs121/fit_and_acquisition121.jsonl')}
  for k in catalog():
   if k[2]=='online':acq[k]=dict(complete_allocated_acquisition_seconds='0')
   elif acq[k]['model_sha256']!=digest(model_path(k)):raise AssertionError('B acquisition identity differs from actual fixed actor')
  clocks=[]
  for ci,(directory,launch) in enumerate(zip([p]+list(map(Path,timings)),launches)):
   cs=rows(directory/'cohorts124b.jsonl');receipt=json.loads((Path(launch)/'PROCESS124B.json').read_text());n=N if ci==0 else TIMED_N
   if receipt['returncode']!=0 or len(cs)!=174:raise ValueError('Incomplete B parent/cohort clock')
   total=F(receipt['seconds']);summed=sum(F(c['seconds']) for c in cs);H=total-summed
   if H<0:raise AssertionError('B cohorts exceed complete measured parent')
   clocks.append(dict(clock=ci,n=n,process_seconds=total,cohort_seconds=summed,standalone_residual_seconds=H,receipt_sha256=digest(Path(launch)/'PROCESS124B.json')))
   for c in cs:
    k=tuple(c[f] for f in ('index','budget','arm','training_loss','mode'));A=F(acq[k[:4]]['complete_allocated_acquisition_seconds']);T=F(c['seconds']);L=F(c['load_seconds'])
    bb=[bounds[k+(j,)] for j in range(n)]
    append(out/'clock_cells124b.jsonl',dict(clock=ci,key=k,n=n,A=A,H=H,L=L,T=T,
     mean_original_J_lower=mean([v['lower'] for v in bb]),mean_original_J_upper=mean([v['upper'] for v in bb]),
     complete_cost_scenarios={str(v):A+H+L+F(v,n)*(T-L) for v in (32,256,4096,65536)},
     full_nested_stages_and_compression_charged=True,economics_match_timed_states=True,large_volume_is_extrapolation=True))
  clock_cells=rows(out/'clock_cells124b.jsonl');lookup={(r['clock'],tuple(r['key'])):r for r in clock_cells};menus=[]
  for k in cells:
   if k[2]!='relu':continue
   competitors=[c for c in cells if c[0]==k[0] and c[2]!='relu']
   if len(competitors)!=75:raise AssertionError('Complete conventional B comparator census')
   for volume in (32,256,4096,65536):
    for grouping,ids in [('primary',[0]),('timing1',[1]),('timing2',[2]),('timing3',[3]),('all-three-timings',[1,2,3])]:
     sufficient=[];optimistic=[]
     for ci in ids:
      c=lookup[(ci,k)];C=F(c['complete_cost_scenarios'][str(volume)])
      for competitor in competitors:
       d=lookup[(ci,competitor)];D=F(d['complete_cost_scenarios'][str(volume)])
       sufficient.append((volume*(F(c['mean_original_J_upper'])-F(d['mean_original_J_lower'])),C-D))
       optimistic.append((volume*(F(c['mean_original_J_lower'])-F(d['mean_original_J_upper'])),C-D))
     menus.append(dict(key=k,volume=volume,clock_group=grouping,constraints=len(sufficient),sufficient=price_domain(sufficient),optimistic=price_domain(optimistic),population_adoption_claim=False))
  for name,data in [('policy_cells124b.jsonl',policy),('safe_gain_inference124b.jsonl',safe),('signed_inference124b.jsonl',signed),('price_menus124b.jsonl',menus),('process_clocks124b.jsonl',clocks)]:
   for r in data:append(out/name,r)
  summary=dict(phase='B-post-A-prospectively-frozen',primary_decisions=len(records),independent_states=N,policy_cells=len(policy),safe_gain_cells=len(safe),signed_cells=len(signed),
   own_stage_accepted_by_mode={m:sum(r['accepted_improvement'] for r in records if r['mode']==m) for m in MODES},
   joint_cumulative_changed=sum(r['action']!=r['fused_action'] for r in records if r['mode']=='joint'),
   safe_mean_positive=sum(r['population_lower']>0 for r in safe),safe_mean_positive_by_comparison={c:sum(r['population_lower']>0 for r in safe if r['comparison']==c) for c in ('own-stage','joint-vs-fused')},
   signed_population_positive=sum(r['population_lower']>0 for r in signed),signed_population_negative=sum(r['population_upper']<0 for r in signed),
   full_three_clock_sufficient_nonempty=sum(not r['sufficient']['empty'] for r in menus if r['clock_group']=='all-three-timings'),
   full_three_clock_optimistic_nonempty=sum(not r['optimistic']['empty'] for r in menus if r['clock_group']=='all-three-timings'),
   inference_family=dict(conditional_coverage_at_least='19/20',safe_means=232,threshold_events=232,signed_comparisons=348,n=N,
    exact_exp_lower=exponential_lower,hoeffding_exponent='49/4',failure_allocations=['1/100','1/100','3/100'],conditional_on_A_and_frozen_B_source=True),
   independent_economic_receipt=er,independent_exact_stage_audit_sha256=digest(ap),independent_exact_stage_audit_receipt=ar,
   research_new_service_process_seconds=sum(c['process_seconds'] for c in clocks),historical_unknown_research_work_remains_unknown=True,
   original_objective_and_future_controller_unchanged=True,no_A_or_R123_outcomes_substituted=True)
  write(out/'SUMMARY124B.json',summary);finish(out,tick,info,primary_sha256=digest(p/RECORDS),summary=summary)
 except BaseException:fail(out,tick);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--independent',required=True);p.add_argument('--audit',required=True);p.add_argument('--output',required=True);p.add_argument('--timing',action='append',default=[]);p.add_argument('--launch',action='append',default=[]);a=p.parse_args();run(a.primary,a.independent,a.output,a.timing,a.launch,a.audit)
