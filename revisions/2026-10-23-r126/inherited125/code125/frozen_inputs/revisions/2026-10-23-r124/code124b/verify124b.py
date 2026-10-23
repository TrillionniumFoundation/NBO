"""Independent rational reader for B's actual staged Bellman decisions.

No production envelope, optimizer, learned model, NumPy, SciPy or economic
primitive is imported. A's standard-library dual reader is reused as a
mathematical subroutine without invoking A source/state gates or outcomes.
"""
import argparse,itertools,math,sys
from fractions import Fraction as F
from common124b import *
sys.path.insert(0,str(A_CODE))
import verify124 as ar
RationalCertificate=ar.RationalCertificate
CHECKS=0
FINAL=('action','action_hex','lower','upper','optimum_lower','loss','width','qualified','complete_policy_lower','complete_policy_upper','original_optimum_lower','certified_regret_upper','action_distance_upper')
def require(ok,msg):
 global CHECKS;CHECKS+=1
 if not ok:raise AssertionError(msg)
def final(r):return {k:r[k] for k in FINAL}
def check_final(r):
 require(r['qualified'] is True,'Unqualified final original policy')
 require(float(r['action']).hex()==r['action_hex'],'Actual action hex differs')
 require(r['lower']==r['complete_policy_lower'] and r['upper']==r['complete_policy_upper'] and r['optimum_lower']==r['original_optimum_lower'],'Final endpoint aliases differ')
 require(r['loss']==r['certified_regret_upper']==math.nextafter(r['upper']-r['optimum_lower'],math.inf),'Final outward regret differs')
 require(r['width']==math.nextafter(r['upper']-r['lower'],math.inf),'Final outward width differs')
 require(0<=r['loss']<=1/256 and 0<=r['width']<=1/8192,'Original final qualification differs')
 require(F(r['action_distance_upper'])**2>=F(r['loss']),'Action-error upper bound too small')
def bind(row,case,origin,answer):
 f=row['full_fused_record']
 adapted=dict(index=row['index'],alpha=row['alpha'],state=row['state'],case=case,
  initial_support_certificates=f['initial_support_certificates'],baseline_action=origin['action'],baseline_action_hex=origin['action_hex'],
  baseline_lower=origin['lower'],baseline_upper=origin['upper'],baseline_optimum_lower=origin['optimum_lower'],
  action=answer['action'],action_hex=answer['action_hex'],enhancement_failure=f['enhancement_numerical_failure'])
 ar.bind_original_case(adapted)
def outward_values(c):
 lo=ar.outward(c['lower'],False);hi=ar.outward(c['upper'],True);B=ar.outward(c['optimum_lower'],False)
 return dict(lower=lo,upper=hi,optimum_lower=B,loss=math.nextafter(hi-B,math.inf),width=math.nextafter(hi-lo,math.inf))
def accepted(c,b,a):
 z=outward_values(c);good=b!=a and c['gain_lower']>0 and c['loss']<=F(1,256) and c['width']<=F(1,8192) and z['loss']<=1/256 and z['width']<=1/8192
 return good,z
def final_from(origin,entry):
 if entry is None:return final(origin)
 c,b=entry['certificate'],F(entry['b']);z=outward_values(c);a=float(b);loss=z['loss']
 return dict(action=a,action_hex=a.hex(),lower=z['lower'],upper=z['upper'],optimum_lower=z['optimum_lower'],loss=loss,width=z['width'],qualified=True,
  complete_policy_lower=z['lower'],complete_policy_upper=z['upper'],original_optimum_lower=z['optimum_lower'],certified_regret_upper=loss,
  action_distance_upper=math.nextafter(math.sqrt(loss),math.inf))
def old_candidate(engine,b):
 x=engine.candidate(b,'fused')
 return {a:x[z] for a,z in [('lower','policy_lower'),('upper','policy_upper'),('optimum_lower','optimum_lower'),('loss','regret_upper'),('width','width'),
  ('change_lower','q_contrast_lower'),('change_upper','q_contrast_upper'),('gain_lower','gain_lower')]}
def audit_fused(row):
 f=row['full_fused_record'];check_final(f)
 require(f['state']==row['state'] and f['state_hex']==row['state_hex'],'Nested fused state differs')
 require(f['mode']=='fused' and not f['probes'] and f['new_risk_queries_started']==f['new_risk_queries_completed']==0,'Strong full-fused comparator changed information')
 origin=dict(action=f['baseline_action'],action_hex=f['baseline_action_hex'],lower=f['baseline_lower'],upper=f['baseline_upper'],optimum_lower=f['baseline_optimum_lower'])
 partial=f['incomplete_menu_attempt'];cases=f['multi_anchor_cases']
 require(len(cases)<=1,'Unexpected fused probe case')
 case=cases[0]['case'] if cases else (partial['case'] if partial else None)
 bind(row,case,origin,f)
 if case is None:
  require(not f['accepted_improvement'] and f['action']==origin['action'] and F(f['certified_policy_gain_lower'])==0,'No-case fused action changed')
  require(f['lower']==origin['lower'] and f['upper']==origin['upper'] and f['optimum_lower']==origin['optimum_lower'],'No-case fused endpoints changed')
  return
 engine=RationalCertificate(case);expected=ar.reconstructed_menu(engine)
 entries=cases[0]['candidates'] if cases else partial['completed_candidates']
 require(len(entries)==len(expected) or f['enhancement_numerical_failure'] is not None,'Incomplete full-fused menu without failure')
 eligible=[]
 for i,(actual,want) in enumerate(zip(entries,expected)):
  b=want['b'];c=old_candidate(engine,b)
  require(F(actual['b'])==b and actual['source']==want['source'] and F(actual['fraction'])==want['fraction'],'Published full fused menu differs')
  for k,v in c.items():require(F(actual['certificate'][k])==v,'Full fused exact implication differs: '+k)
  good,z=accepted(c,b,engine.a)
  require(all(actual['outward'][k]==v for k,v in z.items()) and actual['outward_accepted']==good,'Full fused outward gate differs')
  if good:eligible.append(dict(b=b,certificate=c,menu_index=i))
 if f['enhancement_numerical_failure'] is not None:eligible=[]
 chosen=min(eligible,key=lambda r:(-r['certificate']['gain_lower'],r['b'],r['menu_index'])) if eligible else None
 require(f['accepted_improvement']==(chosen is not None),'Full fused selection acceptance differs')
 require(F(f['certified_policy_gain_lower'])==(chosen['certificate']['gain_lower'] if chosen else 0),'Full fused gain differs')
 if chosen:
  require(final(f)==final_from(f,chosen),'Full fused returned final differs')
  require(cases[0]['selected_index']==chosen['menu_index'],'Full fused tie rule differs')
 else:require(f['action']==origin['action'] and f['lower']==origin['lower'] and f['upper']==origin['upper'] and f['optimum_lower']==origin['optimum_lower'],'Retained full-fused incumbent changed')
def distinct_levels(engine):
 d={}
 for p in engine.payloads:d[p['a']]=min(d.get(p['a'],p['U']),p['U'])
 return sorted(d.items())
def independent_menu(engine):
 level=distinct_levels(engine);raw=[]
 def add(source,z,**data):
  b=F(max(0,min(int(z*2**30),int(engine.A*2**30))),2**30)
  raw.append(dict(source=source,unrounded=z,b=b,menu_index=len(raw),**data))
 if len(level)>=2:
  for (s,us),(t,ut) in itertools.combinations(level,2):
   z=max(s,min(t,(s+t)/2-(ut-us)/(engine.mu*(t-s))))
   add('bridge-minimum',z,pair=[s,t],pair_upper=[us,ut]);add('bridge-midpoint',(s+t)/2,pair=[s,t],pair_upper=[us,ut])
  for den in (16,64,256):
   for sign in (-1,1):add('fused-neighbor',engine.a+sign*engine.A/den,denominator=den,sign=sign)
 unique={}
 for r in raw:unique.setdefault(r['b'],r)
 return dict(reference_fused_action=engine.a,distinct_paid_anchors=len(level),raw=raw,distinct=list(unique.values()),
  restriction='no new menu with fewer than two distinct paid anchors; this is an experimental restriction, not a general saturation theorem')
def bridge_upper(engine,b):
 fused=engine.absolute_upper_q(b,'fused');values=[]
 for (s,us),(t,ut) in itertools.combinations(distinct_levels(engine),2):
  if s<=b<=t:
   v=us+(ut-us)*(b-s)/(t-s)+engine.mu*(b-s)*(b-t)/2
   values.append(dict(s=s,t=t,u=(b-s)/(t-s),upper=v))
 return min([fused]+[v['upper'] for v in values]),dict(fused_upper=fused,eligible_pair_bounds=values)
def check_stage_math(record,origin,menu,kind):
 require(record['kind']==kind and record['origin']==final(origin),'Actual stage incumbent differs')
 engine=RationalCertificate(record['case'])
 require(engine.a==F(origin['action']) and engine.old_B==F(origin['original_optimum_lower']),'Recentered stage differs')
 expected=menu['distinct'];entries=record['entries'];eligible=[]
 require(len(entries)==len(expected) or record['failure'] is not None,'Unrecorded incomplete B stage')
 for i,(r,item) in enumerate(zip(entries,expected)):
  require(all(r[k]==serial(v) for k,v in item.items()),'Shared actual candidate differs')
  b=F(r['b']);w=r['dual_witness'];started=kind=='joint' and b!=engine.a
  require(r['dual_started']==started and r['dual_elapsed_seconds']>=0,'Started dual identity/time differs')
  if 'outward' not in r:
   require(record['failure'] is not None and i==len(entries)-1,'Unfinished stage candidate without retained failure')
   if w is not None:ar.checked_dual(engine,b,w)
   continue
  c=old_candidate(engine,b);ub,parts=bridge_upper(engine,b);ua,origin_parts=bridge_upper(engine,engine.a);lo=engine.absolute_lower(engine.a)
  contrast=min(c['change_upper'],ub-lo)
  if started:
   require(w is not None and r['dual_completed'],'Missing completed joint dual')
   contrast=min(contrast,ar.checked_dual(engine,b,w))
  else:require(w is None and not r['dual_completed'],'Undeclared joint arithmetic')
  if b==engine.a:contrast=F(0)
  ub=min(ub,ua+contrast);upper=ub+engine.delta;gain=F(0) if b==engine.a else -contrast-engine.delta
  c.update(change_upper=contrast,gain_lower=gain,upper=upper,loss=upper-c['optimum_lower'],width=upper-c['lower'],
   q_upper=ub,q_origin_upper=ua,q_origin_lower=lo,bridge_parts=parts,bridge_origin_parts=origin_parts)
  for k,v in c.items():require(r['certificate'][k]==serial(v),'Independent bridge/joint implication differs: '+k)
  good,z=accepted(c,b,engine.a)
  require(all(r['outward'][k]==v for k,v in z.items()) and r['accepted']==good,'Actual B outward gate differs')
  if good:eligible.append(dict(b=b,certificate=c,menu_index=r['menu_index']))
 if record['failure'] is not None:eligible=[]
 chosen=min(eligible,key=lambda r:(-r['certificate']['gain_lower'],r['b'],r['menu_index'])) if eligible else None
 require(record['selected_menu_index']==(chosen['menu_index'] if chosen else None) and record['accepted']==(chosen is not None),'Stage selection/tie rule differs')
 require(F(record['gain_lower'])==(chosen['certificate']['gain_lower'] if chosen else 0),'Stage selected gain differs')
 require(record['answer']==final_from(origin,chosen),'Actual completed stage policy differs')
 for k,field in [('dual_solves_started','dual_started'),('dual_solves_completed','dual_completed'),('dual_seconds','dual_elapsed_seconds')]:require(record[k]==sum(e[field] for e in entries),'Uncharged partial B dual work: '+k)
 require(record['dual_solver_successes']==sum(bool(e['dual_witness']['solver']['success']) for e in entries if e['dual_witness']),'Floating solver status census differs')
 check_final(record['answer'])
def check_stage(row,record,origin,menu,kind):
 bind(row,record['case'],origin,record['answer'])
 check_stage_math(record,origin,menu,kind)
def audit_row(row):
 check_final(row);audit_fused(row);f=row['full_fused_record'];mode=row['mode'];bridge=row['bridge_stage'];joint=row['joint_stage'];menu=row['new_menu']
 require(row['additional_original_risk_queries']==0 and row['counts']==f['counts'],'B service changed original information budget')
 expected_origin=dict(action=f['baseline_action'],action_hex=f['baseline_action_hex'],lower=f['baseline_lower'],upper=f['baseline_upper'],optimum_lower=f['baseline_optimum_lower'])
 own=F(f['certified_policy_gain_lower']);cumulative=F(0);answer=final(f)
 if mode=='fused_full':require(menu is None and bridge is None and joint is None,'Fused comparator ran new stages')
 else:
  expected_origin=final(f);own=F(0)
  if bridge is not None:
   fused_case=dict(bridge['case'],incumbent=str(F(f['action'])),old_optimum_lower=str(F(f['original_optimum_lower'])))
   expected=independent_menu(RationalCertificate(fused_case));require(menu==serial(expected),'Fixed B shared menu differs')
   check_stage(row,bridge,f,expected,'bridge');answer=bridge['answer'];own=F(bridge['gain_lower']);cumulative=own
   if mode=='joint':
    expected_origin=final(answer);own=F(0)
    if joint is not None:
     check_stage(row,joint,answer,expected,'joint');own=F(joint['gain_lower']);cumulative+=own;answer=joint['answer']
    else:require(row['enhancement_failure'] is not None,'Missing joint stage without failure')
  else:require(not f['initial_support_certificates'] or row['enhancement_failure'] is not None,'Missing bridge stage without recorded cause')
  if row['enhancement_failure'] is not None:
   answer=bridge['answer'] if bridge is not None and mode=='joint' else final(f)
   expected_origin=final(answer);own=F(0);cumulative=F(bridge['gain_lower']) if bridge is not None and mode=='joint' else F(0)
 require(final(row)==final(answer),'Returned policy differs from actual completed stage')
 for k,v in [('stage_incumbent_action',expected_origin['action']),('stage_incumbent_action_hex',expected_origin['action_hex']),('stage_incumbent_lower',expected_origin['lower']),('stage_incumbent_upper',expected_origin['upper']),('stage_incumbent_optimum_lower',expected_origin['optimum_lower'])]:require(row[k]==v,'Actual comparison baseline differs: '+k)
 require(F(row['certified_policy_gain_lower'])==own and F(row['certified_gain_vs_fused_lower'])==cumulative,'Reported stage/cumulative gain differs')
 require(row['accepted_improvement']==(row['action']!=expected_origin['action'] and own>0),'Own-stage acceptance differs')
 require(row['fused_action']==f['action'] and row['fused_action_hex']==f['action_hex'] and row['original_incumbent_action']==f['baseline_action'],'Saved fused/original action differs')
 require(row['bridge_action']==(f['action'] if bridge is None else bridge['answer']['action']),'Saved actual bridge action differs')
 stages=[s for s in (bridge,joint) if s is not None]
 for field in ('dual_solves_started','dual_solves_completed','dual_solver_successes','dual_seconds'):require(row[field]==sum(s[field] for s in stages),'Missing nested stage cost/counter: '+field)
 flags=dict(fused_enhancement_failed=f['enhancement_numerical_failure'] is not None,bridge_enhancement_failed=bridge is not None and bridge['failure'] is not None,
  joint_enhancement_failed=joint is not None and joint['failure'] is not None,outer_enhancement_failed=row['enhancement_failure'] is not None)
 require(all(row[k]==v for k,v in flags.items()) and row['any_enhancement_failed']==any(flags.values()),'Hidden stage failure')
 require(row['original_service_numerical_failure']==f['numerical_service_failure'] and row['original_proposal_numerical_failure']==f['proposal_numerical_failure'],'Original service/proposal failure scope differs')
def run(primary,output,timings):
 out,tick,info=start(output,'B-independent-exact-staged-audit')
 try:
  verify_source();binding=boundaries();ss=states();data=rows(Path(primary)/RECORDS)
  key=lambda r:tuple(r[k] for k in ('index','budget','arm','training_loss','mode','row'))
  expected={c+(m,j) for c in catalog() for m in MODES for j in range(N)}
  require(len(data)==len(expected) and {key(r) for r in data}==expected,'Complete B primary census differs');lookup={key(r):r for r in data}
  def identity(r,repeat):
   require(r['state']==ss[r['row']]['state'] and r['state_hex']==ss[r['row']]['hex'],'B state/entropy identity differs')
   require(r['source_commit']==binding['source_commit'] and r['state_commit']==binding['state_commit'] and r['actor_commit']==ACTOR_COMMIT and r['repeat']==repeat and r['population_observation']==(repeat is None),'B immutable identity differs')
  for r in data:identity(r,None);audit_row(r)
  for c in catalog():
   for j in range(N):
    f,b,z=[lookup[c+(m,j)] for m in MODES]
    for r in (b,z):require(final(r['full_fused_record'])==final(f) and r['full_fused_record']['initial_support_certificates']==f['full_fused_record']['initial_support_certificates'] and r['counts']==f['counts'],'Cross-arm actual fused prefix/information differs')
    require(z['bridge_action']==b['action'],'Joint actual incumbent differs from completed bridge comparator')
    if b['bridge_stage'] is not None and z['bridge_stage'] is not None:require(z['bridge_stage']['answer']==b['bridge_stage']['answer'] and z['bridge_stage']['gain_lower']==b['bridge_stage']['gain_lower'] and z['new_menu']==b['new_menu'],'Cross-arm bridge prefix/menu differs')
  require(len(timings)==3,'All three serial B clocks required');timed=0
  fields=FINAL+('stage_incumbent_action_hex','certified_policy_gain_lower','certified_gain_vs_fused_lower','counts','fused_action_hex','bridge_action','accepted_improvement','dual_solves_started','dual_solves_completed')
  for i,p in enumerate(timings):
   rs=rows(Path(p)/RECORDS);te={k for k in expected if k[-1]<TIMED_N}
   require(len(rs)==len(te) and {key(r) for r in rs}==te,'Complete B timing census differs')
   for r in rs:
    identity(r,i);audit_row(r);require(all(r[f]==lookup[key(r)][f] for f in fields),'B timing changed actual policy/certificate/counter');timed+=1
  finish(out,tick,info,status_detail='passed',assertions=CHECKS+ar.CHECKS,primary_decisions=len(data),timing_decisions=timed,
   primary_sha256=digest(Path(primary)/RECORDS),timing_sha256=[digest(Path(p)/RECORDS) for p in timings],
   production_optimizer_imported=False,original_economic_queries=0,all_actual_stage_incumbents_and_prefixes_checked=True)
 except BaseException:fail(out,tick);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--output',required=True);p.add_argument('--timing',action='append',default=[]);a=p.parse_args();run(a.primary,a.output,a.timing)
