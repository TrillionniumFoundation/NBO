"""Exploratory current-state witness refinement under STATE_PROTOCOL.md."""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
import torch
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r22';OUT=REV/'results/full_state'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
import accessibility_certificate as C
from accessibility_neural import load_model,serialize,actor_action
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r17/replication'))
import interval_objective as D

def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
class BudgetStop(Exception):pass

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64);torch.use_deterministic_algorithms(True)
    old=ROOT/'revisions/2026-09-23-r17/results/accessible/seed17107/network_step0400.json'
    a,v,d=load_model(old);save(OUT/'initial_network.json',d)
    grid=(4,16,16);exact,idx=C.cell_grid(*grid);s=D.I(torch.tensor(exact.lo),torch.tensor(exact.hi))
    initial=C.audit(OUT/'initial_network.json',OUT/'initial_certificate.json',grid,chunk=256)
    pars=list(a.parameters())+list(v.parameters());sizes=[p.numel() for p in pars]
    def vector():return np.concatenate([p.detach().numpy().ravel() for p in pars]).copy()
    def assign(x):
        off=0
        with torch.no_grad():
            for p,n in zip(pars,sizes):p.copy_(torch.from_numpy(x[off:off+n].copy()).reshape(p.shape));off+=n
    count=0;steps=0;accepted=vector();history=[];start=time.perf_counter()
    def fun(x):
        nonlocal count
        if count>=400:raise BudgetStop()
        assign(x);a.zero_grad(set_to_none=True);v.zero_grad(set_to_none=True)
        loss=D.objective(s,a,v,nt=4,all_faces=False,temperature=.15)
        if not torch.isfinite(loss):raise FloatingPointError('nonfinite full-state interval surrogate')
        loss.backward();count+=1
        grad=np.concatenate([p.grad.detach().numpy().ravel() for p in pars]).copy()
        if not np.isfinite(grad).all():raise FloatingPointError('nonfinite gradient')
        if count%20==0:print('full-state evaluation',count,float(loss.detach()),flush=True)
        return float(loss.detach()),grad
    def callback(x):
        nonlocal steps,accepted
        steps+=1;accepted=x.copy();history.append({'accepted_iterate':steps,'gradient_calls':count})
    try:
        r=minimize(fun,accepted,method='L-BFGS-B',jac=True,callback=callback,
                   options={'maxiter':400,'maxfun':400,'maxls':40,'ftol':1e-13,'gtol':1e-8})
        assign(r.x);status=str(r.message)
    except (BudgetStop,FloatingPointError,ArithmeticError) as exc:
        assign(accepted);status=type(exc).__name__+': '+str(exc)+'; restored last accepted iterate'
    generation=time.perf_counter()-start
    d.update({'version':'R22','step':400,'actual_gradient_calls':count,'actor':serialize(a),'critic':serialize(v),
              'warm_start_path':str(old.relative_to(ROOT)),'warm_start_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),
              'state_protocol_commit':'a1e73f4262a232db147b245521af6af429e8f501','training_wall_seconds':generation})
    save(OUT/'candidate_network.json',d)
    candidate=C.audit(OUT/'candidate_network.json',OUT/'candidate_certificate.json',grid,chunk=256)
    pts=torch.tensor([[0,2,1.25],[.25,1.6,.8],[.5,2.4,1.7],[.9,2,.6]],requires_grad=True)
    actions=actor_action(a,pts);derivatives=[]
    for q in range(3):derivatives.append(torch.autograd.grad(actions[:,q].sum(),pts,retain_graph=True)[0].detach().tolist())
    save(OUT/'state_dependence_diagnostic.json',{'points':pts.detach().tolist(),'actions':actions.detach().tolist(),
         'derivatives_action_by_point_by_state':derivatives,'scope':'pointwise derivative diagnostic only; MPFR complete-box audit certifies domain coverage'})
    save(OUT/'history.json',history)
    save(OUT/'summary.json',{'initial_bound':initial['t0_regret_upper'],'candidate_bound':candidate['t0_regret_upper'],
         'candidate_all_initial_times_bound':candidate['all_initial_times_regret_upper'],
         'certificate_decreased':candidate['t0_regret_upper']<initial['t0_regret_upper'],
         'gradient_calls':count,'function_calls':count,'accepted_optimizer_iterations':steps,
         'line_search_evaluations':max(0,count-1-steps),'termination':status,'generation_seconds':generation,
         'checker_seconds':initial['wall_seconds']+candidate['wall_seconds'],'parameter_dimension':sum(sizes),
         'global_target':.01,'global_target_closed':candidate['all_initial_times_regret_upper']<=.01,
         'payoff_improvement_proved':False,'scope':'entire state-time domain; warm-start joint actor/witness refinement; no claim of a policy-specific payoff gain'})
if __name__=='__main__':main()
