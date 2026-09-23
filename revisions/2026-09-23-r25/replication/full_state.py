"""Original-state actor/witness continuation; independent MPFR acceptance.
Regret-bound improvement is not confused with a policy-payoff comparison.
"""
from pathlib import Path
from fractions import Fraction
import copy,hashlib,json,sys,time
import numpy as np
import torch
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r25';OUT=REV/'results/full_state'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
import accessibility_certificate as C
from accessibility_neural import load_model,serialize
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r17/replication'))
import interval_objective as D
M=C.M;I=M.I;Q=I.rational
PROTOCOL='25c32fae4099d3c6b52ffdb688520ab9bdc95090'
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def envelope(c):
    n=len(c['slabs']);h=Q(Fraction(1,n));e=M.exp(-Q('.04')*h);mass=(1-e)/Q('.04');tail=I(0);values=[0.]
    for s in reversed(c['slabs']):
        tail=mass*(I(s['positive_upper'])+I(s['negative_policy']))+e*tail;values.append(float(tail.hi))
    values=values[::-1]
    return {'slab_boundary_envelope_upper':values,'all_start_times_regret_upper':max(values),'arithmetic':'directed MPFR',
            'proof':'suffix on each slab is monotone or constant, so its maximum is at a slab endpoint'}
class Limit(Exception):pass

def main():
    if (OUT/'summary.json').exists():print('EXISTING full-state execution',flush=True);return
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64);torch.use_deterministic_algorithms(True)
    old=ROOT/'revisions/2026-09-23-r22/results/full_state/candidate_network.json';a,v,d=load_model(old)
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'initial_network.json').write_bytes(old.read_bytes())
    exact,idx=C.cell_grid(4,16,16);s=D.I(torch.tensor(exact.lo),torch.tensor(exact.hi));pars=list(a.parameters())+list(v.parameters());sizes=[p.numel() for p in pars]
    def vector():return np.concatenate([p.detach().numpy().ravel() for p in pars]).copy()
    def assign(x):
        off=0
        with torch.no_grad():
            for p,n in zip(pars,sizes):p.copy_(torch.tensor(x[off:off+n]).reshape(p.shape));off+=n
    def fingerprint(x):return hashlib.sha256(x.astype('<f8').tobytes()).hexdigest()
    initial=C.audit(OUT/'initial_network.json',OUT/'initial_coarse_certificate.json',(4,16,16),chunk=256)
    incert=initial;incenv=envelope(initial);inc=vector();incd=copy.deepcopy(d);rows=[];totalcalls=0;start=time.perf_counter()
    for block in range(1,5):
        assign(inc);calls=0;steps=0;accepted=vector();history=[];t0=time.perf_counter();before=fingerprint(inc)
        def fun(x):
            nonlocal calls
            if calls>=500:raise Limit()
            assign(x);a.zero_grad(set_to_none=True);v.zero_grad(set_to_none=True)
            loss=D.objective(s,a,v,nt=4,all_faces=False,temperature=.05)
            if not torch.isfinite(loss):raise FloatingPointError('nonfinite interval proposal')
            loss.backward();g=np.concatenate([p.grad.detach().numpy().ravel() for p in pars]).copy()
            if not np.isfinite(g).all():raise FloatingPointError('nonfinite gradient')
            calls+=1;history.append({'call':calls,'loss':float(loss.detach()),'gradient_norm':float(np.linalg.norm(g)),'seconds':time.perf_counter()-t0})
            return float(loss.detach()),g
        def callback(x):
            nonlocal accepted,steps
            accepted=x.copy();steps+=1
        try:
            r=minimize(fun,accepted,jac=True,method='L-BFGS-B',callback=callback,options={'maxiter':500,'maxfun':500,'maxls':40,'ftol':1e-13,'gtol':1e-8})
            assign(r.x);status=str(r.message)
        except (Limit,FloatingPointError,ArithmeticError) as e:assign(accepted);status=type(e).__name__+': '+str(e)+'; last accepted iterate restored'
        generation=time.perf_counter()-t0;totalcalls+=calls
        cand=copy.deepcopy(d);cand.update({'version':'R25','step':totalcalls,'actor':serialize(a),'critic':serialize(v),
              'protocol_commit':PROTOCOL,'warm_start_path':str(old.relative_to(ROOT)),'warm_start_sha256':hashlib.sha256(old.read_bytes()).hexdigest()})
        cp=OUT/f'block{block}_network.json';save(cp,cand);cc=C.audit(cp,OUT/f'block{block}_certificate.json',(4,16,16),chunk=256);ce=envelope(cc)
        take=ce['all_start_times_regret_upper']<incenv['all_start_times_regret_upper'];candidate_hash=fingerprint(vector());oldbound=incenv['all_start_times_regret_upper']
        if take:inc=vector();incd=cand;incert=cc;incenv=ce
        else:assign(inc)
        row={'block':block,'gradient_calls':calls,'accepted_optimizer_iterations':steps,'termination':status,'generation_seconds':generation,
             'checker_seconds':cc['wall_seconds'],'bound_before':oldbound,'candidate_envelope':ce,'accepted_for_certificate':take,
             'retained_bound':incenv['all_start_times_regret_upper'],'state_hash_before':before,'candidate_hash':candidate_hash,
             'state_hash_after':fingerprint(vector()),'rollback_verified':not take and fingerprint(vector())==before,
             'payoff_improvement_proved':False}
        rows.append(row);save(OUT/f'block{block}_history.json',history);save(OUT/f'block{block}_decision.json',row)
        print('FULL STATE BLOCK',block,take,ce['all_start_times_regret_upper'],flush=True)
    save(OUT/'retained_network.json',incd)
    finer=[]
    for phase in ('initial','retained'):
        c=C.audit(OUT/f'{phase}_network.json',OUT/f'{phase}_fine_certificate.json',(8,32,32),chunk=256)
        finer.append({'phase':phase,'certificate':c,'envelope':envelope(c)})
    result={'protocol_commit':PROTOCOL,'original_economy_unchanged':True,'current_state_only':True,'target':.01,
        'initial_coarse_envelope':envelope(initial),'blocks':rows,'fine':finer,'total_gradient_calls':totalcalls,
        'all_start_times_regret_upper':finer[-1]['envelope']['all_start_times_regret_upper'],
        'target_established':finer[-1]['envelope']['all_start_times_regret_upper']<=.01,'payoff_improvement_proved':False,
        'complete_experiment_seconds_excluding_initial_check':time.perf_counter()-start,'parameter_dimension':sum(sizes),
        'implementation_contract':'unchanged pre-distance action error 2^-24 and upper-wealth stopping inaccessibility'}
    save(OUT/'summary.json',result)
if __name__=='__main__':main()
