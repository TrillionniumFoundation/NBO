"""Fault-injection custody fixture; no original economic primitive is called."""
from contextlib import contextmanager
from fractions import Fraction as F
from types import SimpleNamespace
import argparse,sys,time
from common124 import ROOT,R123,write,Path
sys.path.insert(0,str(R123/'code123'))
import service124 as svc

def main(destination):
 tick=time.perf_counter()
 case=dict(A=F(1),incumbent=F(0),mu=F(1),L=F(2),delta=F(0),tau=F(1),omega=F(1),old_optimum_lower=F(-1),
  payloads=[dict(a=F(0),W=F(0),U=F(0),p_lower=F(-1,2),p_upper=F(-1,2),g_lower=F(-1,2),g_upper=F(-1,2)),
  dict(a=F(1),W=F(3,16),U=F(3,16),p_lower=F(1),p_upper=F(1),g_lower=F(1),g_upper=F(1))])
 baseline=dict(action=0.,action_hex=0..hex(),complete_policy_lower=0.,complete_policy_upper=0.,
  original_optimum_lower=-1.,first_proposal_action=0.)
 @contextmanager
 def capture(records):
  records.append({'synthetic_fixture_payload':True});yield
 def fail_solve(case,b,progress):
  progress.update(stage='injected-failure',paid_fixture_attempt=True)
  raise ArithmeticError('Declared fixture failure after solve start')
 svc.prior.old.capture_support=capture
 svc.prior.old.lab=SimpleNamespace(service=lambda *args:dict(row=baseline,attempts=[],actor_trace={'fixture':True}),
  inherited=SimpleNamespace(base=SimpleNamespace(counter_delta=lambda before:{})))
 svc.prior.old.econ=SimpleNamespace(COUNTS={})
 svc.prior.make_case=lambda *args:case
 svc.joint124.solve=fail_solve
 row=svc.service(['abstract','fixture'],.5,None,'joint_two')
 assert row['action']==0. and not row['accepted_improvement'] and row['certified_policy_gain_lower']=='0'
 assert row['dual_solves_started']==1 and row['dual_solves_completed']==0 and row['dual_seconds']>0
 attempt=row['selected_common_menu'][0]
 assert attempt['dual_started'] and not attempt['dual_completed'] and attempt['dual_attempt']['paid_fixture_attempt']
 assert attempt['failure']['exception_type']=='ArithmeticError' and row['enhancement_failure'] is not None
 assert row['full_common_menu'] and attempt['dual_elapsed_seconds']==row['dual_seconds']
 result=dict(status='passed',kind='synthetic failure-custody engineering fixture',original_economic_outcomes=0,population_units=0,
  returned_action=0,retained_started_attempts=1,retained_completed_attempts=0,paid_failed_dual_seconds=row['dual_seconds'],
  retained_traceback=bool(attempt['failure']['traceback']),seconds=time.perf_counter()-tick)
 write(Path(destination),result);print(result)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(ROOT/'provenance124/FAILURE_CUSTODY_FIXTURE124.json'));main(parser.parse_args().output)
