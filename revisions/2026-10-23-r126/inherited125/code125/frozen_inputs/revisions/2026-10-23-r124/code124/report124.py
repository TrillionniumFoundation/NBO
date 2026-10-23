"""Fixed complete R124 reporting, numerical bounds, inference and price menus."""
from fractions import Fraction as F
from math import comb,sqrt,nextafter,inf
import argparse,json,math
from common124 import *
TAU=F(1,256);THRESHOLD=F(1,2**24)

def cp_lower(k,n,alpha=F(1,11600)):
 if k==0:return F(0)
 lo,hi=F(0),F(1)
 for _ in range(48):
  p=(lo+hi)/2;tail=sum(F(comb(n,j))*p**j*(1-p)**(n-j) for j in range(k,n+1))
  if tail<=alpha:lo=p
  else:hi=p
 return lo

def mean(v):return sum(v,F(0))/len(v)
def square_root_upper(v):
 x=sqrt(float(v))
 while F(x)*F(x)<v:x=nextafter(x,inf)
 return x

def price_domain(constraints):
 lower=F(0);upper=None;strict_lower=False;empty=False
 for d,c in constraints:
  if c==0:
   if d>=0:empty=True
  elif c>0:
   v=-d/c;upper=v if upper is None else min(upper,v)
  else:
   v=-d/c
   if v>=lower:lower=v;strict_lower=True
 if upper is not None and (upper<=lower or upper<=0):empty=True
 return dict(empty=empty,lower=lower,upper=upper,strict_lower=strict_lower,strict_upper=upper is not None,
  criterion='strict original cost plus price times complete measured computation')

def run(primary,independent,output,timings,launches,audit):
 out,tick,info=start(output,'complete-fixed-report')
 try:
  verify_source();binding=boundaries();states();p=Path(primary);iv=Path(independent)
  records=rows(p/'records124.jsonl');evaluated=rows(iv/'action_bounds124.jsonl')
  audit_path=Path(audit)/'EXECUTION124.json';audit_receipt=json.loads(audit_path.read_text())
  if audit_receipt.get('status')!='executed' or audit_receipt.get('status_detail')!='passed' or audit_receipt.get('primary_sha256')!=digest(p/'records124.jsonl') or audit_receipt.get('primary_decisions')!=58*2*N or audit_receipt.get('timing_decisions')!=3*58*2*4:raise ValueError('Passing complete independent exact-dual and timing audit required before inference')
  if len(records)!=58*2*N or len(launches)!=4 or len(timings)!=3:raise ValueError('Complete declared experiment and all clocks required')
  er=json.loads((iv/'EXECUTION124.json').read_text())
  if er['status']!='executed' or er['primary_sha256']!=digest(p/'records124.jsonl'):raise ValueError('Independent evaluation belongs to another primary')
  key=lambda r:(r['index'],r['budget'],r['arm'],r['training_loss'],r['mode'])
  ekey=lambda r,a:(tuple(r['state_hex']),float(a).hex(),float(r['alpha']).hex())
  E={(tuple(e['key'][0]),e['key'][1],e['key'][2]):e for e in evaluated}
  opt={}
  for e in evaluated:
   s=(tuple(e['key'][0]),e['key'][2]);opt[s]=max(opt.get(s,F(-10)),F(e['best']['optimum_lower']))
  for r in records:
   s=(tuple(r['state_hex']),float(r['alpha']).hex());opt[s]=max(opt[s],F(r['original_optimum_lower']))
  bounds={}
  for r in records:
   e=E[ekey(r,r['action'])]['best'];lo=max(F(e['j_lower']),F(r['complete_policy_lower']));hi=min(F(e['j_upper']),F(r['complete_policy_upper']))
   if lo>hi:raise AssertionError('Independent and production intervals contradict')
   B=opt[(tuple(r['state_hex']),float(r['alpha']).hex())]
   regret=min(TAU,hi-B)
   if regret<0:raise AssertionError('Negative valid regret bound')
   bounds[key(r)+(r['row'],)]=dict(lower=lo,upper=hi,regret_upper=regret,raw_independent_lower=F(e['j_lower']),raw_independent_upper=F(e['j_upper']))
  cells={k:[r for r in records if key(r)==k] for k in [c+(m,) for c in catalog() for m in MODES]}
  if any(len(rs)!=N for rs in cells.values()):raise ValueError('Incomplete policy cell')
  policy=[];safe=[];signed=[]
  for k,rs in cells.items():
   bs=[bounds[k+(r['row'],)] for r in rs]
   policy.append(dict(key=k,mean_original_J_lower=mean([b['lower'] for b in bs]),mean_original_J_upper=mean([b['upper'] for b in bs]),
    mean_regret_upper=mean([b['regret_upper'] for b in bs]),rms_action_error_upper=square_root_upper(mean([b['regret_upper'] for b in bs])),
    accepted=sum(r['accepted_improvement'] for r in rs),failed_enhancements=sum(r['enhancement_failure'] is not None for r in rs),
    dual_solves=sum(r['dual_solves_started'] for r in rs),dual_solver_successes=sum(r['dual_solver_successes'] for r in rs),
    dual_seconds=sum(F(r['dual_seconds']) for r in rs),new_original_queries=0,
    all_qualified=all(r['qualified'] for r in rs),raw_independent_means=[mean([b['raw_independent_lower'] for b in bs]),mean([b['raw_independent_upper'] for b in bs])]))
   lows=[];highs=[];count=0
   for r,b in zip(rs,bs):
    if r['action']==r['baseline_action']:low=high=F(0)
    else:
     be=E[ekey(r,r['baseline_action'])]['best'];low=max(F(0),F(r['certified_policy_gain_lower']),F(be['j_lower'])-b['upper']);high=min(TAU,F(be['j_upper'])-b['lower'])
    if low>high:raise AssertionError('Own-incumbent bound contradiction')
    lows.append(low);highs.append(high);count+=F(r['certified_policy_gain_lower'])>=THRESHOLD
   event=cp_lower(count,N);radius=F(5,8)*TAU
   safe.append(dict(key=k,n=N,numerical_mean_lower=mean(lows),numerical_mean_upper=mean(highs),
    population_lower=max(F(0),mean(lows)-radius,THRESHOLD*event),population_upper=min(TAU,mean(highs)+radius),
    hoeffding_radius=radius,threshold=THRESHOLD,certified_threshold_count=count,threshold_probability_lower=event,
    original_gain_support=[F(0),TAU],independent_observation_unit='initial state'))
  def comparison(k,c,label):
   identity=k==c;lows=[];highs=[]
   for j in range(N):
    a=next(r for r in cells[k] if r['row']==j);b=next(r for r in cells[c] if r['row']==j)
    if a['action']==b['action']:lo=hi=F(0)
    else:
     aa=bounds[k+(j,)];bb=bounds[c+(j,)];lo=max(-TAU,bb['lower']-aa['upper']);hi=min(TAU,bb['upper']-aa['lower'])
    if lo>hi:raise AssertionError('Paired difference contradiction')
    lows.append(lo);highs.append(hi)
   radius=F(0) if identity else F(5,4)*TAU
   return dict(key=k,comparator=c,label=label,n=N,positive_means_first_method_lower_cost=True,
    numerical_mean_lower=mean(lows),numerical_mean_upper=mean(highs),
    population_lower=max(-TAU,mean(lows)-radius),population_upper=min(TAU,mean(highs)+radius),
    population_identity=identity,sampling_radius=radius,sample_only_action_equality_not_population_identity=True)
  for k in cells:
   i,b,a,l,m=k
   signed.append(comparison(k,(i,0,'online','online','fused_two'),'same-risk-online-fused'))
   signed.append(comparison(k,(i,b or 5,'quadratic','value','fused_two'),'same-budget-quadratic-value-fused'))
   if m=='joint_two':signed.append(comparison(k,k[:-1]+('fused_two',),'same-actor-joint-vs-fused'))
  if len(safe)!=116 or len(signed)!=290:raise AssertionError('Frozen inference family census')
  exponential_lower=sum(F(25,2)**j/math.factorial(j) for j in range(31))
  if not exponential_lower>23200:raise AssertionError('Exact family failure verification')
  # Original fixed actor acquisition includes its matched hinge parent and audit.
  acq={(r['index'],r['budget'],r['arm'],r['loss']):r for r in rows(R123/'provenance123/inherited_costs121/fit_and_acquisition121.jsonl')}
  for k in catalog():
   if k[2]=='online':acq[k]=dict(complete_allocated_acquisition_seconds='0')
   elif acq[k]['model_sha256']!=digest(model_path(k)):raise AssertionError('Acquisition charged to a different actor')
  clock_data=[]
  for ci,(directory,launch) in enumerate(zip([p]+list(map(Path,timings)),launches)):
   cs=rows(directory/'cohorts124.jsonl');receipt=json.loads((Path(launch)/'PROCESS124.json').read_text());n=16 if ci==0 else 4
   if receipt['returncode']!=0 or len(cs)!=116:raise ValueError('Incomplete actual process clock')
   total=F(receipt['seconds']);summed=sum(F(c['seconds']) for c in cs);H=total-summed
   if H<0:raise AssertionError('Cohorts exceed complete parent process')
   groups={tuple(c[f] for f in ('index','budget','arm','training_loss','mode')):c for c in cs}
   clock_data.append(dict(clock=ci,n=n,process_seconds=total,cohort_seconds=summed,standalone_residual_seconds=H,
    receipt_sha256=digest(Path(launch)/'PROCESS124.json')))
   for k,c in groups.items():
    A=F(acq[k[:4]]['complete_allocated_acquisition_seconds']);T=F(c['seconds']);load=F(c['load_seconds'])
    bb=[bounds[k+(j,)] for j in range(n)]
    append(out/'clock_cells124.jsonl',dict(clock=ci,key=k,n=n,A=A,H=H,L=load,T=T,
     mean_original_J_lower=mean([x['lower'] for x in bb]),mean_original_J_upper=mean([x['upper'] for x in bb]),
     complete_cost_scenarios={str(v):A+H+load+F(v,n)*(T-load) for v in (32,256,4096,65536)},
     economics_match_timed_states=True,large_volume_is_extrapolation=True))
  clocks=rows(out/'clock_cells124.jsonl');lookup={(r['clock'],tuple(r['key'])):r for r in clocks};menus=[]
  for k in cells:
   if k[2]!='relu':continue
   competitors=[c for c in cells if c[0]==k[0] and c[2]!='relu']
   for volume in (32,256,4096,65536):
    for grouping,ids in [('primary',[0]),('timing1',[1]),('timing2',[2]),('timing3',[3]),('all-three-timings',[1,2,3])]:
     suff=[];optim=[]
     for ci in ids:
      c=lookup[(ci,k)];C=F(c['complete_cost_scenarios'][str(volume)])
      for competitor in competitors:
       d=lookup[(ci,competitor)];D=F(d['complete_cost_scenarios'][str(volume)])
       suff.append((volume*(F(c['mean_original_J_upper'])-F(d['mean_original_J_lower'])),C-D))
       optim.append((volume*(F(c['mean_original_J_lower'])-F(d['mean_original_J_upper'])),C-D))
     menus.append(dict(key=k,volume=volume,clock_group=grouping,constraints=len(suff),
      sufficient=price_domain(suff),optimistic=price_domain(optim),population_adoption_claim=False))
  for name,data in [('policy_cells124.jsonl',policy),('safe_gain_inference124.jsonl',safe),('signed_inference124.jsonl',signed),('price_menus124.jsonl',menus),('process_clocks124.jsonl',clock_data)]:
   for row in data:append(out/name,row)
  summary=dict(primary_decisions=len(records),independent_states=N,policy_cells=len(policy),accepted_changes=sum(r['accepted_improvement'] for r in records),
   joint_vs_fused_action_changes=sum(next(r for r in cells[c+('joint_two',)] if r['row']==j)['action']!=next(r for r in cells[c+('fused_two',)] if r['row']==j)['action'] for c in catalog() for j in range(N)),
   safe_mean_positive=sum(r['population_lower']>0 for r in safe),signed_population_positive=sum(r['population_lower']>0 for r in signed),
   signed_population_negative=sum(r['population_upper']<0 for r in signed),
   full_three_clock_sufficient_nonempty=sum(not r['sufficient']['empty'] for r in menus if r['clock_group']=='all-three-timings'),
   full_three_clock_optimistic_nonempty=sum(not r['optimistic']['empty'] for r in menus if r['clock_group']=='all-three-timings'),
   inference_family=dict(coverage_at_least='19/20',safe_means=116,threshold_events=116,signed_comparisons=290,n=N,
    exact_exp_lower=exponential_lower,hoeffding_exponent='25/2',failure_allocations=['1/100','1/100','3/100']),
   independent_economic_receipt=er,independent_exact_dual_audit_sha256=digest(audit_path),
   independent_exact_dual_audit_receipt=audit_receipt,
   research_new_service_process_seconds=sum(r['process_seconds'] for r in clock_data),
   historical_unknown_research_work_remains_unknown=True,
   statistical_claim_scope='conditional on fixed algorithm, actors and independent entropy bits; all numerical premises stated')
  write(out/'SUMMARY124.json',summary)
  finish(out,tick,info,primary_sha256=digest(p/'records124.jsonl'),summary=summary)
 except BaseException:fail(out,tick);raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--independent',required=True);p.add_argument('--output',required=True);p.add_argument('--audit',required=True);p.add_argument('--timing',action='append',default=[]);p.add_argument('--launch',action='append',default=[]);a=p.parse_args();run(a.primary,a.independent,a.output,a.timing,a.launch,a.audit)
