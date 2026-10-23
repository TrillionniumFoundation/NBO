"""Abstract staging and failure-custody fixture; zero original-economic calls."""
import argparse,ast,copy,sys,time
from types import SimpleNamespace
from fractions import Fraction as F
from common124b import ROOT,write,serial,Path,digest
import service124b as svc
import verify124b as reader

def run(output):
 tick=time.perf_counter()
 parsed=sorted(Path(__file__).parent.glob('*.py'))
 for p in parsed:ast.parse(p.read_text(),filename=str(p))
 # Configure only the scalar outward arithmetic used by the service. No
 # original economy, actor, state, primitive, source draw or cache is invoked.
 svc.prior.old.up=lambda v:svc.prior.old.np.nextafter(v,svc.prior.old.np.inf)
 s,t=F(1,16),F(9,128);delta=F(15,2**24)
 case=svc.env.normalize(dict(A=F(1,4),incumbent=s,mu=F(2),L=F(4),delta=delta,tau=F(1,256),omega=F(1,8192),old_optimum_lower=F(-1,16384),
  payloads=[dict(a=s,W=F(0),U=F(0),p_lower=F(-1,64),p_upper=F(1,64),g_lower=F(-1,64),g_upper=F(1,64)),
            dict(a=t,W=F(0),U=F(0),p_lower=F(0),p_upper=F(1,32),g_lower=F(0),g_upper=F(1,32))]))
 c=svc.env.candidate(case,s);f=svc.prior.float_certificate(c);a=float(s)
 origin=dict(action=a,action_hex=a.hex(),complete_policy_lower=f['lower'],complete_policy_upper=f['upper'],
  original_optimum_lower=f['optimum_lower'],certified_regret_upper=f['loss'],action_distance_upper=float(svc.prior.old.up(svc.prior.old.np.sqrt(f['loss']))),**f)
 menu=svc.new_menu(case);engine=reader.RationalCertificate(case);expected=reader.independent_menu(engine)
 assert serial(menu)==serial(expected)
 bridge=svc.stage(case,menu,origin,'bridge');reader.check_stage_math(serial(bridge),origin,expected,'bridge')
 assert bridge['accepted'] and F(bridge['answer']['action'])==F(17,256) and bridge['gain_lower']==F(241,2**24)
 chosen=next(r for r in bridge['entries'] if r['menu_index']==bridge['selected_menu_index']);bc=chosen['certificate']
 assert bc['lower']==F(-768,2**24) and bc['upper']==F(-241,2**24) and bc['loss']==F(783,2**24) and bc['width']==F(527,2**24)
 assert chosen['b']==s+(t-s)/2 and chosen['b']==F(float(chosen['b']))
 joint=svc.stage(case,menu,bridge['answer'],'joint');reader.check_stage_math(serial(joint),bridge['answer'],expected,'joint')
 assert not joint['accepted'] and joint['answer']==bridge['answer'] and joint['gain_lower']==0
 original_solve=svc.joint.solve
 def forced_failure(case,b,progress):
  progress.update(stage='injected-abstract-failure',paid_attempt_retained=True)
  raise ArithmeticError('Declared abstract fault after joint solve start')
 try:
  svc.joint.solve=forced_failure;failed=svc.stage(case,menu,bridge['answer'],'joint')
 finally:svc.joint.solve=original_solve
 reader.check_stage_math(serial(failed),bridge['answer'],expected,'joint')
 assert failed['failure'] is not None and failed['dual_solves_started']==1 and failed['dual_solves_completed']==0 and failed['dual_seconds']>0
 assert failed['answer']==bridge['answer'] and failed['gain_lower']==0
 started=next(r for r in failed['entries'] if r['dual_started'])
 assert started['dual_attempt']['paid_attempt_retained'] and started['failure']['traceback']
 # A declared synthetic full-fused prefix exercises the actual nested service
 # and complete serialization without calling any original-economic primitive.
 # Its state label is deliberately not an original-model state or population unit.
 original_econ,original_lab=svc.prior.old.econ,svc.prior.old.lab
 assert original_econ is None and original_lab is None
 synthetic_counts={'abstract_original_query_counter':0}
 svc.prior.old.econ=SimpleNamespace(COUNTS=synthetic_counts)
 svc.prior.old.lab=SimpleNamespace(inherited=SimpleNamespace(base=SimpleNamespace(counter_delta=lambda before:{k:v-before[k] for k,v in synthetic_counts.items()})))
 counter_before=synthetic_counts.copy()
 zero_counts=svc.prior.old.lab.inherited.base.counter_delta(counter_before)
 abstract_state=['abstract mathematical fixture, not an economic state']
 synthetic_fused=dict(origin,state=abstract_state,state_hex=['abstract'],mode='fused',alpha='abstract',
  baseline_action=a,baseline_action_hex=a.hex(),baseline_lower=origin['lower'],baseline_upper=origin['upper'],
  baseline_optimum_lower=origin['optimum_lower'],certified_policy_gain_lower='0',accepted_improvement=False,
  initial_support_certificates=[dict(abstract_fixture_only=True)],counts=zero_counts,
  enhancement_numerical_failure=None,numerical_service_failure=False,proposal_numerical_failure=False,raw_proposal_kept=None)
 original_service,original_make_case=svc.prior.service,svc.prior.make_case
 def fake_service(state,alpha,model,mode):
  assert state==abstract_state and alpha=='abstract' and model is None and mode=='fused'
  return copy.deepcopy(synthetic_fused)
 def fake_make_case(records,state,alpha,baseline):
  assert records==synthetic_fused['initial_support_certificates'] and state==abstract_state and alpha=='abstract'
  return copy.deepcopy(case)
 try:
  svc.prior.service,svc.prior.make_case=fake_service,fake_make_case
  complete={m:svc.service(abstract_state,'abstract',None,m) for m in svc.MODES}
  for m,r in complete.items():
   assert r['counts']==zero_counts and not r['any_enhancement_failed']
   assert svc.final_fields(r['full_fused_record'])==svc.final_fields(complete['fused_full'])
   if r['bridge_stage'] is not None:reader.check_stage_math(r['bridge_stage'],synthetic_fused,expected,'bridge')
   if r['joint_stage'] is not None:reader.check_stage_math(r['joint_stage'],r['bridge_stage']['answer'],expected,'joint')
  assert complete['joint']['stage_incumbent_action']==complete['bridge']['action']==float(F(17,256))
  assert F(complete['bridge']['certified_policy_gain_lower'])==F(241,2**24)
  assert F(complete['joint']['certified_policy_gain_lower'])==0 and F(complete['joint']['certified_gain_vs_fused_lower'])==F(241,2**24)
  svc.joint.solve=forced_failure
  full_failed=svc.service(abstract_state,'abstract',None,'joint')
  assert full_failed['joint_enhancement_failed'] and full_failed['any_enhancement_failed']
  assert not full_failed['bridge_enhancement_failed'] and not full_failed['fused_enhancement_failed'] and not full_failed['outer_enhancement_failed']
  assert svc.final_fields(full_failed)==svc.final_fields(complete['bridge'])
  assert F(full_failed['certified_policy_gain_lower'])==0 and F(full_failed['certified_gain_vs_fused_lower'])==F(241,2**24)
  assert full_failed['dual_solves_started']==1 and full_failed['dual_solves_completed']==0 and full_failed['dual_seconds']>0
  reader.check_stage_math(full_failed['joint_stage'],full_failed['bridge_stage']['answer'],expected,'joint')
 finally:
  svc.prior.service,svc.prior.make_case=original_service,original_make_case;svc.joint.solve=original_solve
  svc.prior.old.econ,svc.prior.old.lab=original_econ,original_lab
 assert synthetic_counts==counter_before and svc.prior.old.econ is None and svc.prior.old.lab is None
 result=dict(status='passed',kind='abstract mathematical and injected-failure engineering fixture',original_economic_outcomes=0,population_units=0,
  exact_bridge_action='17/256',exact_original_policy_gain='241/16777216',joint_retains_attaining_parabola_minimum=True,
  bridge=serial(bridge),joint=serial(joint),failed_joint=serial(failed),synthetic_complete_services=complete,synthetic_failed_joint_service=full_failed,
  synthetic_counter_delta=zero_counts,original_economy_remained_unconfigured=True,parsed_python_sources=len(parsed),independent_math_assertions=reader.CHECKS+reader.ar.CHECKS,
  seconds=time.perf_counter()-tick,source_hashes={p.name:digest(p) for p in (Path(__file__),Path(svc.__file__),Path(reader.__file__))})
 write(output,result);print(serial({k:v for k,v in result.items() if k not in ('bridge','joint','failed_joint','synthetic_complete_services','synthetic_failed_joint_service')}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default=str(ROOT/'provenance124b/ANALYTIC_STAGING124B.json'));run(p.parse_args().output)
