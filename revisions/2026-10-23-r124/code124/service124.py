"""Fresh complete original-law services with matched two-candidate menus."""
from fractions import Fraction as F
import sys,time,traceback
from common124 import R123,serial
sys.path.insert(0,str(R123/'code123'))
import service123 as prior
import envelope123 as env
import joint124


def configure():prior.configure()

def common_menu(case,entries=None):
 entries=[] if entries is None else entries
 common=env.support_minimum(case)
 for i,item in enumerate(env.candidate_menu(case)):
  record=dict(item,menu_index=i,certificate=None);entries.append(record)
  try:record['certificate']=env.candidate(case,item['b'],'fused',common)
  except (ArithmeticError,prior.old.np.linalg.LinAlgError) as exc:
   record['failure']=dict(exception_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());raise
 distinct={}
 for row in entries:
  if row['b']!=case['incumbent']:distinct.setdefault(row['b'],row)
 selected=sorted(distinct.values(),key=lambda r:(-r['certificate']['gain_lower'],r['b'],r['menu_index']))[:2]
 return entries,selected


def tighten(case,b,cert,witness):
 c=dict(cert);d=case['delta'];upper=min(c['change_upper'],witness['dual']['contrast_upper'])
 uq_at_origin=min(p['U']+env.contrast(case,p['a'],case['incumbent'])[1] for p in case['payloads'])
 hi=min(c['upper'],uq_at_origin+upper+d)
 if hi<c['lower'] or hi<c['optimum_lower'] or upper<c['change_lower']:raise ArithmeticError('Contradictory exact joint-dual and fused premises')
 c.update(change_upper=upper,gain_lower=-upper-(d if b!=case['incumbent'] else 0),upper=hi,
  loss=hi-c['optimum_lower'],width=hi-c['lower'])
 c['qualified']=c['loss']<=case['tau'] and c['width']<=case['omega']
 c['accepted']=b!=case['incumbent'] and c['gain_lower']>0 and c['qualified']
 return c


def service(state,alpha,model,mode):
 if mode not in ('fused_two','joint_two'):raise ValueError('Undeclared R124 service')
 tick=time.perf_counter();before=prior.old.econ.COUNTS.copy();supports=[];failure=None;case=None;full=[];chosen=[];active_candidate=None
 with prior.old.capture_support(supports):base=prior.old.lab.service(state,alpha,model)
 incumbent=base['row'];answer=dict(incumbent);eligible=[]
 try:
  if supports:
   case=env.normalize(prior.make_case(supports,state,alpha,incumbent))
   _,menu=common_menu(case,full)
   for item in menu:
    rec=dict(item,dual_witness=None,dual_started=False,dual_completed=False,dual_elapsed_seconds=0.,dual_attempt={},stage='started');chosen.append(rec);active_candidate=rec
    if mode=='joint_two':
     dual_tick=time.perf_counter();rec['dual_started']=True
     try:
      rec['dual_witness']=joint124.solve(case,item['b'],rec['dual_attempt']);rec['dual_completed']=True
      rec['dual_attempt']['stage']='candidate-tightening'
      rec['certificate']=tighten(case,item['b'],item['certificate'],rec['dual_witness'])
      rec['dual_attempt']['stage']='completed'
     finally:rec['dual_elapsed_seconds']=time.perf_counter()-dual_tick
    rec['stage']='outward-conversion'
    rec['outward']=prior.float_certificate(rec['certificate'])
    rec['accepted']=rec['certificate']['accepted'] and rec['outward']['qualified']
    if rec['accepted']:eligible.append(rec)
    rec['stage']='completed';active_candidate=None
   if eligible:
    selected=min(eligible,key=lambda r:(-r['certificate']['gain_lower'],r['b'],r['menu_index']))
    c,f=selected['certificate'],selected['outward'];action=float(selected['b'])
    answer.update(action=action,action_hex=action.hex(),complete_policy_lower=f['lower'],complete_policy_upper=f['upper'],
     original_optimum_lower=f['optimum_lower'],certified_regret_upper=f['loss'],
     action_distance_upper=float(prior.old.up(prior.old.np.sqrt(f['loss']))),**f)
   else:selected=None
  else:selected=None
 except (ArithmeticError,prior.old.np.linalg.LinAlgError) as exc:
  failure=dict(exception_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),
   seconds_before_retain=time.perf_counter()-tick)
  if active_candidate is not None:active_candidate['failure']=dict(failure)
  answer=dict(incumbent);selected=None
 answer.update(mode=mode,baseline_action=incumbent['action'],baseline_action_hex=incumbent['action_hex'],
  baseline_lower=incumbent['complete_policy_lower'],baseline_upper=incumbent['complete_policy_upper'],
  baseline_optimum_lower=incumbent['original_optimum_lower'],baseline_qualification_attempts=base['attempts'],
  baseline_actor_trace=base['actor_trace'],initial_support_certificates=supports,case=case,
  full_common_menu=full,selected_common_menu=chosen,
  selected_menu_index=None if selected is None else selected['menu_index'],
  accepted_improvement=selected is not None,certified_policy_gain_lower=str(selected['certificate']['gain_lower'] if selected else F(0)),
  enhancement_failure=failure,raw_proposal_kept=incumbent['first_proposal_action'],
  additional_original_risk_queries=0,all_original_incumbent_work_reexecuted=True,
  dual_solves_started=sum(r['dual_started'] for r in chosen),
  dual_solves_completed=sum(r['dual_completed'] for r in chosen),
  dual_solver_successes=sum(bool(r['dual_witness']['solver']['success']) for r in chosen if r['dual_witness']),
  dual_seconds=sum(r['dual_elapsed_seconds'] for r in chosen),
  complete_seconds=time.perf_counter()-tick,counts=prior.old.lab.inherited.base.counter_delta(before),
  candidate_selection_scope='two distinct nonincumbent fused-menu candidates ranked before joint solve by fused gain, action, first menu index',
  original_objective_and_future_controller_unchanged=True)
 return serial(answer)
