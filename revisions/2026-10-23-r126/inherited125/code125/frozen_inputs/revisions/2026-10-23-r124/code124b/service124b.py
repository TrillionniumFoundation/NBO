"""Complete original-law full-fused, value-bridge and joint services.

Every arm freshly pays the entire published R123 fused service. Bridge and
joint share one candidate menu fixed from that actual fused final action.
The joint arm also freshly pays the complete bridge stage before comparison
against its actual implemented-policy incumbent. No new economic query.
"""
from fractions import Fraction as F
import itertools,sys,time,traceback
from common124b import R123,A_CODE,serial,MODES
sys.path.insert(0,str(R123/'code123'));sys.path.insert(0,str(A_CODE))
import service123 as prior
import envelope123 as env
import joint124 as joint

FINAL_FIELDS=('action','action_hex','lower','upper','optimum_lower','loss','width','qualified','complete_policy_lower','complete_policy_upper','original_optimum_lower','certified_regret_upper','action_distance_upper')
def configure():prior.configure()
def final_fields(r):return {k:r[k] for k in FINAL_FIELDS}
def levels(case):
 values={}
 for p in case['payloads']:values[p['a']]=min(values.get(p['a'],p['U']),p['U'])
 return sorted(values.items())
def new_menu(case):
 anchors=levels(case);raw=[];a,A=case['incumbent'],case['A']
 if len(anchors)>=2:
  for (s,us),(t,ut) in itertools.combinations(anchors,2):
   d=t-s;u=max(F(0),min(F(1),F(1,2)-(ut-us)/(case['mu']*d*d)))
   for name,z in [('bridge-minimum',s+u*d),('bridge-midpoint',(s+t)/2)]:
    raw.append(dict(source=name,pair=[s,t],pair_upper=[us,ut],unrounded=z,b=env.rounded_action(z,A),menu_index=len(raw)))
  for den in (16,64,256):
   for sign in (-1,1):
    z=a+sign*A/den
    raw.append(dict(source='fused-neighbor',denominator=den,sign=sign,unrounded=z,b=env.rounded_action(z,A),menu_index=len(raw)))
 unique={}
 for r in raw:unique.setdefault(r['b'],r)
 return dict(reference_fused_action=a,distinct_paid_anchors=len(anchors),raw=raw,distinct=list(unique.values()),
  restriction='no new menu with fewer than two distinct paid anchors; this is an experimental restriction, not a general saturation theorem')
def recenter(case,origin):
 c=dict(case,incumbent=F(origin['action']),old_optimum_lower=F(origin['original_optimum_lower']))
 return env.normalize(c)
def q_upper(case,b):
 fused=min(p['U']+env.contrast(case,p['a'],b)[1] for p in case['payloads']);bounds=[]
 for (s,us),(t,ut) in itertools.combinations(levels(case),2):
  if s<=b<=t:
   u=(b-s)/(t-s);value=(1-u)*us+u*ut-case['mu']*u*(1-u)*(t-s)**2/2
   bounds.append(dict(s=s,t=t,u=u,upper=value))
 return min([fused]+[p['upper'] for p in bounds]),dict(fused_upper=fused,eligible_pair_bounds=bounds)
def certificate(case,b,common,dual=None):
 c=env.candidate(case,b,'fused',common);a=case['incumbent'];delta=case['delta']
 ub,parts=q_upper(case,b);ua,origin_parts=q_upper(case,a)
 origin_lower=env.candidate(case,a,'fused',common)['lower']
 contrast=min(c['change_upper'],ub-origin_lower)
 if dual is not None:contrast=min(contrast,dual['dual']['contrast_upper'])
 if b==a:contrast=F(0)
 ub=min(ub,ua+contrast);hi=ub+delta;gain=F(0) if b==a else -contrast-delta
 if hi<c['lower'] or ub<c['optimum_lower'] or contrast<c['change_lower']:raise ArithmeticError('Inconsistent paid bridge/joint premises')
 c.update(change_upper=contrast,gain_lower=gain,upper=hi,loss=hi-c['optimum_lower'],width=hi-c['lower'],
  q_upper=ub,q_origin_upper=ua,q_origin_lower=origin_lower,bridge_parts=parts,bridge_origin_parts=origin_parts)
 c['qualified']=c['loss']<=case['tau'] and c['width']<=case['omega']
 c['accepted']=b!=a and gain>0 and c['qualified']
 return c
def stage(case,menu,origin,kind):
 tick=time.perf_counter();case=recenter(case,origin);entries=[];eligible=[];failure=None;selected=None;active=None
 result=dict(kind=kind,case=case,origin=final_fields(origin),entries=entries,selected_menu_index=None,
  gain_lower=F(0),failure=None,complete_seconds=0.,answer=final_fields(origin))
 try:
  common=env.support_minimum(case)
  for item in menu['distinct']:
   rec=dict(item,dual_started=False,dual_completed=False,dual_elapsed_seconds=0.,dual_attempt={},dual_witness=None,stage='started');entries.append(rec);active=rec
   if kind=='joint' and item['b']!=case['incumbent']:
    t=time.perf_counter();rec['dual_started']=True
    try:rec['dual_witness']=joint.solve(case,item['b'],rec['dual_attempt']);rec['dual_completed']=True
    finally:rec['dual_elapsed_seconds']=time.perf_counter()-t
   rec['stage']='certificate';rec['certificate']=certificate(case,item['b'],common,rec['dual_witness'])
   rec['stage']='outward';rec['outward']=prior.float_certificate(rec['certificate'])
   rec['accepted']=rec['certificate']['accepted'] and rec['outward']['qualified'];rec['stage']='completed';active=None
   if rec['accepted']:eligible.append(rec)
  if eligible:
   selected=min(eligible,key=lambda z:(-z['certificate']['gain_lower'],z['b'],z['menu_index']))
   f=selected['outward'];action=float(selected['b'])
   result['answer'].update(action=action,action_hex=action.hex(),complete_policy_lower=f['lower'],complete_policy_upper=f['upper'],
    original_optimum_lower=f['optimum_lower'],certified_regret_upper=f['loss'],action_distance_upper=float(prior.old.up(prior.old.np.sqrt(f['loss']))),**f)
   result.update(selected_menu_index=selected['menu_index'],gain_lower=selected['certificate']['gain_lower'])
 except (ArithmeticError,prior.old.np.linalg.LinAlgError) as exc:
  failure=dict(exception_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),seconds_before_retain=time.perf_counter()-tick)
  if active is not None:active['failure']=dict(failure)
  result.update(failure=failure,answer=final_fields(origin),gain_lower=F(0),selected_menu_index=None)
 result.update(complete_seconds=time.perf_counter()-tick,dual_solves_started=sum(e['dual_started'] for e in entries),
  dual_solves_completed=sum(e['dual_completed'] for e in entries),dual_solver_successes=sum(bool(e['dual_witness']['solver']['success']) for e in entries if e['dual_witness']),
  dual_seconds=sum(e['dual_elapsed_seconds'] for e in entries),accepted=result['selected_menu_index'] is not None)
 return result
def service(state,alpha,model,mode):
 if mode not in MODES:raise ValueError('Undeclared R124B service')
 tick=time.perf_counter();count0=prior.old.econ.COUNTS.copy()
 fused=prior.service(state,alpha,model,'fused');answer=final_fields(fused)
 case=None;menu=None;bridge=None;joint_stage=None;failure=None
 own_origin=dict(action=fused['baseline_action'],action_hex=fused['baseline_action_hex'],lower=fused['baseline_lower'],upper=fused['baseline_upper'],optimum_lower=fused['baseline_optimum_lower'])
 own_gain=F(fused['certified_policy_gain_lower']);fused_gain=F(0)
 try:
  if mode!='fused_full':
   if fused['initial_support_certificates']:
    original=env.normalize(prior.make_case(fused['initial_support_certificates'],state,alpha,
     dict(action=fused['baseline_action'],original_optimum_lower=fused['baseline_optimum_lower'])))
    case=recenter(original,fused);menu=new_menu(case)
    bridge=stage(case,menu,fused,'bridge');answer=bridge['answer']
    own_origin=final_fields(fused);own_gain=bridge['gain_lower'];fused_gain=own_gain
    if mode=='joint':
     joint_stage=stage(case,menu,answer,'joint');own_origin=final_fields(answer);answer=joint_stage['answer'];own_gain=joint_stage['gain_lower'];fused_gain+=own_gain
   else:
    own_origin=final_fields(fused);own_gain=fused_gain=F(0)
 except (ArithmeticError,prior.old.np.linalg.LinAlgError) as exc:
  failure=dict(exception_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),seconds_before_retain=time.perf_counter()-tick)
  # No unproved stage is used. A completed bridge remains the actual joint
  # incumbent if a later case/menu operation fails.
  answer=bridge['answer'] if bridge is not None and mode=='joint' else final_fields(fused)
  own_origin=final_fields(answer);own_gain=F(0);fused_gain=bridge['gain_lower'] if bridge is not None and mode=='joint' else F(0)
 stages=[s for s in (bridge,joint_stage) if s is not None]
 answer=dict(answer)
 answer.update(state=fused['state'],state_hex=fused['state_hex'],mode=mode,alpha=alpha,
  full_fused_record=fused,new_menu=menu,bridge_stage=bridge,joint_stage=joint_stage,
  stage_incumbent_action=own_origin['action'],stage_incumbent_action_hex=own_origin['action_hex'],
  stage_incumbent_lower=own_origin['lower'],stage_incumbent_upper=own_origin['upper'],stage_incumbent_optimum_lower=own_origin['optimum_lower'],
  original_incumbent_action=fused['baseline_action'],fused_action=fused['action'],fused_action_hex=fused['action_hex'],
  bridge_action=fused['action'] if bridge is None else bridge['answer']['action'],
  certified_policy_gain_lower=own_gain,certified_gain_vs_fused_lower=fused_gain,
  accepted_improvement=answer['action']!=own_origin['action'] and own_gain>0,
  fused_accepted_improvement=fused['accepted_improvement'],bridge_accepted_improvement=bridge is not None and bridge['accepted'],
  joint_accepted_improvement=joint_stage is not None and joint_stage['accepted'],
  dual_solves_started=sum(s['dual_solves_started'] for s in stages),dual_solves_completed=sum(s['dual_solves_completed'] for s in stages),
  dual_solver_successes=sum(s['dual_solver_successes'] for s in stages),dual_seconds=sum(s['dual_seconds'] for s in stages),
  enhancement_failure=failure,fused_enhancement_failed=fused['enhancement_numerical_failure'] is not None,
  bridge_enhancement_failed=bridge is not None and bridge['failure'] is not None,
  joint_enhancement_failed=joint_stage is not None and joint_stage['failure'] is not None,
  outer_enhancement_failed=failure is not None,
  any_enhancement_failed=failure is not None or fused['enhancement_numerical_failure'] is not None or any(s['failure'] is not None for s in stages),
  original_service_numerical_failure=fused['numerical_service_failure'],original_proposal_numerical_failure=fused['proposal_numerical_failure'],
  additional_original_risk_queries=0,counts=prior.old.lab.inherited.base.counter_delta(count0),
  raw_proposal_kept=fused['raw_proposal_kept'],complete_seconds=time.perf_counter()-tick,
  all_original_fused_work_reexecuted=True,all_bridge_work_reexecuted=mode=='joint',original_objective_and_future_controller_unchanged=True)
 return serial(answer)
