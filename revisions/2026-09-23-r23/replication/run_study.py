"""Prospective root-safe crossed/quotient experiment; every configuration retained."""
from __future__ import annotations
from pathlib import Path
from dataclasses import asdict
import copy,hashlib,json,os,platform,sys,time,resource
import numpy as np,scipy,torch
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r23'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r22/replication'))
from crossed import Actor,Slab,NODES,CORNERS,canon,sha,write,check
from budget_coordinates import setup,QuotientSlab
SEEDS=(23000,23100,23200)
PROTOCOL='f0ab87bec39e4ba96a49bd01ba5608a7de739bed'

class BudgetStop(Exception):pass

def optimize(net,obj,opt,cap=400):
 stats={'function_evaluations':0,'gradient_evaluations':0,'accepted_optimizer_iterations':0,
        'line_search_evaluations':0,'parameter_dimension':sum(p.numel() for p in net.parameters()),'proposal_failed':False}
 start=time.perf_counter();params=list(net.parameters());sizes=[p.numel() for p in params]
 def vector():return np.concatenate([p.detach().numpy().ravel() for p in params]).copy()
 def assign(x):
  k=0
  with torch.no_grad():
   for p,n in zip(params,sizes):p.copy_(torch.from_numpy(x[k:k+n].copy()).reshape(p.shape));k+=n
 accepted=vector()
 try:
  if opt=='adam':
   optimizer=torch.optim.Adam(params,lr=.005)
   for _ in range(cap):
    optimizer.zero_grad(set_to_none=True);loss=-obj(net);stats['function_evaluations']+=1
    if not torch.isfinite(loss):raise FloatingPointError('Nonfinite objective')
    loss.backward();stats['gradient_evaluations']+=1
    if not all(p.grad is not None and torch.isfinite(p.grad).all() for p in params):raise FloatingPointError('Nonfinite gradient')
    optimizer.step()
    if not all(torch.isfinite(p).all() for p in params):raise FloatingPointError('Nonfinite parameter update')
    stats['accepted_optimizer_iterations']+=1;accepted=vector()
   status='gradient_budget_exhausted'
  else:
   def fun(x):
    if stats['gradient_evaluations']>=cap:raise BudgetStop()
    assign(x);net.zero_grad(set_to_none=True);loss=-obj(net);stats['function_evaluations']+=1
    if not torch.isfinite(loss):raise FloatingPointError('Nonfinite objective')
    loss.backward();stats['gradient_evaluations']+=1
    gradient=np.concatenate([p.grad.detach().numpy().ravel() for p in params]).copy()
    if not np.isfinite(gradient).all():raise FloatingPointError('Nonfinite gradient')
    return float(loss.detach()),gradient
   def callback(x):
    nonlocal accepted
    accepted=x.copy();stats['accepted_optimizer_iterations']+=1
   result=minimize(fun,accepted,method='L-BFGS-B',jac=True,callback=callback,
      options={'maxiter':cap,'maxfun':cap,'maxls':40,'ftol':1e-13,'gtol':1e-8})
   assign(result.x);status=str(result.message)
 except BudgetStop:
  assign(accepted);status='gradient_budget_exhausted_at_last_accepted_iterate'
 except (FloatingPointError,ArithmeticError,ValueError) as exc:
  assign(accepted);status=type(exc).__name__+': '+str(exc);stats['proposal_failed']=True
 stats['generation_seconds']=time.perf_counter()-start;stats['termination']=status
 stats['line_search_evaluations']=0 if opt=='adam' else max(0,stats['function_evaluations']-1-stats['accepted_optimizer_iterations'])
 stats['line_search_definition']='objective/gradient calls beyond one initial call and one per accepted optimizer iteration; not an instrumented count of rejected trials'
 return stats

def main():
 torch.set_default_dtype(torch.float64);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 source={str(p.relative_to(REV)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (REV/'replication').glob('*.py')}
 write(REV/'results/environment.json',{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'torch':torch.__version__,'platform':platform.platform(),'threads':torch.get_num_threads(),'protocol_commit':PROTOCOL,'source_commit':os.getenv('R23_SOURCE_COMMIT','UNSET'),'source_sha256':source,'execution_kind':'prospective R23 held-out root-safe factorial','historical_dual_cost_seconds':415.789,'dual_cost_scope':'inherited library construction, shared by all methods; no new dual constructed'})
 all_records=[];start=time.perf_counter()
 for base in SEEDS:
  for vertex,(u,x) in enumerate(CORNERS):
   block=REV/f'results/crossed/seed{base}/vertex{vertex}'
   torch.manual_seed(base+vertex);init=Actor();raw=init(NODES).detach();direct=Slab(raw);quotient=QuotientSlab(raw)
   initial_obj=setup(u,x);nd,dd,qd=[initial_obj(m,details=True) for m in (init,direct,quotient)]
   assert all(nd[k]==dd[k] for k in ('b','s','theta','approx_value','approx_budget'))
   qerr=max(abs(a-b) for k in ('b','s','theta') for a,b in zip(nd[k],qd[k]));assert qerr<=2e-12
   if (block/'initial_certificate.json').exists():
    initial=json.loads((block/'initial_certificate.json').read_text());seconds=initial['seconds']
   else:
    initial,seconds=check(nd);assert initial['status']=='CERTIFIED',initial
    write(block/'initial_certificate.json',initial)
   # Independently certify the mapped quotient incumbent, even when matching is
   # numerically exact; do not use a tolerance as proof of economic equivalence.
   if qd==nd:
    quotient_initial=initial;quotient_seconds=seconds;quotient_shared=True
   elif (block/'quotient_initial_certificate.json').exists():
    quotient_initial=json.loads((block/'quotient_initial_certificate.json').read_text());quotient_seconds=quotient_initial['seconds'];quotient_shared=False
   else:
    quotient_initial,quotient_seconds=check(qd);assert quotient_initial['status']=='CERTIFIED';quotient_shared=False
   write(block/'quotient_initial_certificate.json',quotient_initial)
   write(block/'initial_actor.json',nd);write(block/'quotient_initial_actor.json',qd)
   write(block/'initial_network.json',canon(init.state_dict()));write(block/'initial_raw_coefficients.json',canon(direct.state_dict()))
   write(block/'matching.json',{'base_seed':base,'vertex_seed':base+vertex,'exact_primary_match':True,'primary_sha256':sha(nd),'quotient_sha256':sha(qd),'quotient_max_delivered_coefficient_error':qerr,'quotient_exact_match':qd==nd,'quotient_check_shared':quotient_shared,'initial_checker_seconds':seconds,'quotient_initial_checker_seconds':quotient_seconds,'corners_share_initialization':False})
   for rep,template in [('neural',init),('direct',direct),('quotient',quotient)]:
    for opt in ('adam','lbfgsb'):
     out=block/f'{rep}_{opt}'
     if (out/'record.json').exists():
      all_records.append(json.loads((out/'record.json').read_text()));continue
     net=copy.deepcopy(template);obj=setup(u,x);stats=optimize(net,obj,opt)
     incumbent=quotient_initial if rep=='quotient' else initial
     initial_actor=qd if rep=='quotient' else nd
     try:
      d=obj(net,details=True);cert,check_seconds=check(d)
     except (ArithmeticError,FloatingPointError,ValueError) as exc:
      d=initial_actor;cert={'status':'REJECTED_PROPOSAL','error':type(exc).__name__+': '+str(exc)};check_seconds=0.;stats['proposal_failed']=True
     feasible=cert['status']=='CERTIFIED'
     accept=not stats['proposal_failed'] and feasible and cert['value_interval'][0]>incumbent['value_interval'][1]
     record={'base_seed':base,'vertex_seed':base+vertex,'vertex':vertex,'u0':u,'x0':x,'representation':rep,'optimizer':opt,'accepted':accept,'initial_value_interval':incumbent['value_interval'],'initial_policy_sha256':sha(initial_actor),'candidate_certificate':cert,'delivered_certificate':cert if accept else incumbent,'candidate_actor_sha256':sha(d),'delivered_actor_sha256':sha(d if accept else initial_actor),'initial_checker_seconds':quotient_seconds if rep=='quotient' else seconds,'final_checker_seconds':check_seconds,'checker_calls':2,'shared_initial_checker_calls':1,'final_checker_calls':int(not stats['proposal_failed'] or feasible),'reporting_forward_evaluations':1,'root_accounting':asdict(obj.accounting),'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**stats}
     write(out/'candidate_actor.json',d);write(out/'candidate_parameters.json',canon(net.state_dict()));write(out/'candidate_certificate.json',cert);write(out/'delivered_actor.json',d if accept else initial_actor);write(out/'record.json',record);all_records.append(record)
     print(base,vertex,rep,opt,'grads',stats['gradient_evaluations'],'accepted',accept,'regret',record['delivered_certificate']['regret_upper'],flush=True)
 write(REV/'results/study_summary.json',{'configurations':len(all_records),'accepted':sum(r['accepted'] for r in all_records),'rejected':sum(not r['accepted'] for r in all_records),'failed_feasibility':sum(r['candidate_certificate']['status']!='CERTIFIED' for r in all_records),'failed_proposals':sum(r['proposal_failed'] for r in all_records),'max_discrete_root_residual':max(r['root_accounting']['max_absolute_discrete_budget_residual'] for r in all_records),'total_function_calls':sum(r['function_evaluations'] for r in all_records),'total_gradient_calls':sum(r['gradient_evaluations'] for r in all_records),'total_generation_seconds':sum(r['generation_seconds'] for r in all_records),'total_final_checker_seconds':sum(r['final_checker_seconds'] for r in all_records),'total_elapsed_seconds':time.perf_counter()-start,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'protocol_commit':PROTOCOL,'no_configuration_dropped':len(all_records)==72})
 assert len(all_records)==72
if __name__=='__main__':main()
