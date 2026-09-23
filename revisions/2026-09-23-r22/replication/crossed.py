"""Prospective R22 crossed optimizer experiment in the unchanged R20 economy.

The proposal objective is not an accuracy certificate. Only certify_stochastic
provides payoff intervals. Initial policies are exactly mapped between the two
parameterizations; no inherited outcomes are selected or overwritten.
"""
from __future__ import annotations
from pathlib import Path
import argparse, copy, hashlib, json, platform, random, sys, time
import numpy as np
import scipy
from scipy.optimize import minimize
import torch
ROOT = Path(__file__).resolve().parents[3]
REV = ROOT / 'revisions/2026-09-23-r22'
sys.path.insert(0, str(ROOT / 'revisions/2026-09-23-r20/replication'))
from proposal import Actor, setup
from certify_stochastic import certify
CORNERS = [(1.98,1.24),(1.98,1.26),(2.02,1.24),(2.02,1.26)]
SEEDS = (22000,22100,22200)
NODES = (2*(torch.arange(16)+.5)/16-1).reshape(16,1)

def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')
    tmp.replace(path)

def canon(x):
    if isinstance(x, torch.Tensor):
        return {'tensor':x.detach().cpu().tolist(), 'dtype':str(x.dtype), 'shape':list(x.shape)}
    if isinstance(x, np.ndarray): return {'ndarray':x.tolist(), 'dtype':str(x.dtype)}
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, dict): return {str(k):canon(v) for k,v in sorted(x.items(),key=lambda q:str(q[0]))}
    if isinstance(x, (list,tuple)): return [canon(v) for v in x]
    return x

def sha(x) -> str:
    return hashlib.sha256(json.dumps(canon(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

class Slab(torch.nn.Module):
    def __init__(self, raw):
        super().__init__(); self.coefficients = torch.nn.Parameter(raw.detach().clone())
    def forward(self, _): return self.coefficients

class BudgetExhausted(Exception): pass

def optimize(net, obj, optimizer: str, cap: int=400):
    stats = dict(function_evaluations=0, gradient_evaluations=0,
                 accepted_optimizer_iterations=0, line_search_evaluations=0,
                 parameter_dimension=sum(p.numel() for p in net.parameters()))
    start = time.perf_counter()
    if optimizer == 'adam':
        opt = torch.optim.Adam(net.parameters(), lr=.005)
        for _ in range(cap):
            opt.zero_grad(set_to_none=True); loss=-obj(net)
            if not torch.isfinite(loss): raise FloatingPointError('Nonfinite proposal objective')
            stats['function_evaluations']+=1; loss.backward(); stats['gradient_evaluations']+=1
            opt.step(); stats['accepted_optimizer_iterations']+=1
        status = 'gradient_budget_exhausted'
    else:
        params=list(net.parameters()); shapes=[p.shape for p in params]; sizes=[p.numel() for p in params]
        def vector(): return np.concatenate([p.detach().numpy().ravel() for p in params]).copy()
        def assign(x):
            pos=0
            with torch.no_grad():
                for p,sh,n in zip(params,shapes,sizes):
                    p.copy_(torch.from_numpy(x[pos:pos+n].copy()).reshape(sh));pos+=n
        accepted=vector()
        def fun(x):
            if stats['gradient_evaluations'] >= cap: raise BudgetExhausted()
            assign(x); net.zero_grad(set_to_none=True); loss=-obj(net)
            if not torch.isfinite(loss): raise FloatingPointError('Nonfinite proposal objective')
            stats['function_evaluations']+=1; loss.backward();stats['gradient_evaluations']+=1
            return float(loss.detach()),np.concatenate([p.grad.detach().numpy().ravel() for p in params]).copy()
        def callback(x):
            nonlocal accepted
            accepted=x.copy();stats['accepted_optimizer_iterations']+=1
        try:
            result=minimize(fun,accepted,method='L-BFGS-B',jac=True,callback=callback,
                options={'maxiter':cap,'maxls':40,'maxfun':cap,'ftol':1e-13,'gtol':1e-8})
            assign(result.x);status=str(result.message)
        except BudgetExhausted:
            assign(accepted);status='gradient_budget_exhausted_at_last_accepted_iterate'
        stats['line_search_evaluations']=max(0,stats['function_evaluations']-1-stats['accepted_optimizer_iterations'])
        stats['line_search_definition']='objective/gradient calls beyond one initial call and one call per accepted iterate'
    stats['generation_seconds']=time.perf_counter()-start
    stats['termination']=status
    return stats

def check(d):
    start=time.perf_counter()
    try:
        c=certify(d);return c, time.perf_counter()-start
    except (AssertionError, FloatingPointError, ValueError) as exc:
        return {'status':'REJECTED_CHECK','error':str(exc)},time.perf_counter()-start

def run_crossed():
    for base in SEEDS:
        for v,(u,x) in enumerate(CORNERS):
            block=REV/f'results/crossed/seed{base}/vertex{v}'
            torch.manual_seed(base+v); init=Actor(); obj=setup(u,x)
            direct=Slab(init(NODES)); nd=obj(init,details=True);dd=obj(direct,details=True)
            assert all(nd[key]==dd[key] for key in ('b','s','theta','approx_value','approx_budget'))
            initial_path=block/'initial_certificate.json'
            if initial_path.exists(): initial=json.loads(initial_path.read_text());initial_seconds=initial['seconds']
            else:
                initial,initial_seconds=check(nd);assert initial['status']=='CERTIFIED',initial
                write(initial_path,initial)
            write(block/'initial_actor.json',nd)
            write(block/'initial_network.json',canon(init.state_dict()))
            write(block/'initial_raw_coefficients.json',canon(direct.state_dict()))
            write(block/'matching.json',{'base_seed':base,'vertex_seed':base+v,'vertex':v,'initial_policy_sha256':sha(nd),
                 'exact_binary64_match':True,'matched_fields':['b','s','theta','approx_value','approx_budget'],
                 'initial_checker_seconds':initial_seconds,'corners_share_initialization':False})
            for representation in ('neural','direct'):
                for opt in ('adam','lbfgsb'):
                    out=block/f'{representation}_{opt}'
                    if (out/'record.json').exists(): continue
                    net=copy.deepcopy(init if representation=='neural' else direct)
                    stats=optimize(net,obj,opt)
                    d=obj(net,details=True); stats['reporting_forward_evaluations']=1
                    write(out/'candidate_actor.json',d); write(out/'candidate_parameters.json',canon(net.state_dict()))
                    certificate,seconds=check(d);write(out/'candidate_certificate.json',certificate)
                    feasible=certificate['status']=='CERTIFIED'
                    accept=feasible and certificate['value_interval'][0]>initial['value_interval'][1]
                    record={'base_seed':base,'vertex_seed':base+v,'vertex':v,'u0':u,'x0':x,
                        'representation':representation,'optimizer':opt,'accepted':accept,
                        'initial_value_interval':initial['value_interval'],'candidate_certificate':certificate,
                        'delivered_certificate':certificate if accept else initial,
                        'candidate_actor_sha256':sha(d),'delivered_actor_sha256':sha(d if accept else nd),
                        'initial_policy_sha256':sha(nd),'candidate_approximate_objective':d['approx_value'],
                        'checker_calls':2,'shared_initial_checker_calls':1,'final_checker_calls':1,
                        'initial_checker_seconds':initial_seconds,'final_checker_seconds':seconds,**stats}
                    write(out/'delivered_actor.json',d if accept else nd);write(out/'record.json',record)
                    print(base,v,representation,opt,stats['gradient_evaluations'],accept,
                          record['delivered_certificate']['regret_upper'],flush=True)

def snapshot(net,opt):
    return {'network':copy.deepcopy(net.state_dict()),'optimizer':copy.deepcopy(opt.state_dict()),
            'torch_rng':torch.get_rng_state().clone(),'numpy_rng':copy.deepcopy(np.random.get_state()),
            'python_rng':copy.deepcopy(random.getstate())}

def restore(net,opt,s):
    net.load_state_dict(s['network']);opt.load_state_dict(s['optimizer']);torch.set_rng_state(s['torch_rng'])
    np.random.set_state(s['numpy_rng']);random.setstate(s['python_rng'])

def run_stress():
    out=REV/'results/stress';out.mkdir(parents=True,exist_ok=True)
    torch.manual_seed(22300);np.random.seed(22300);random.seed(22300)
    net=Actor();opt=torch.optim.Adam(net.parameters(),lr=.5);obj=setup(*CORNERS[0])
    d=obj(net,details=True);inc,seconds=check(d);assert inc['status']=='CERTIFIED'
    write(out/'initial_actor.json',d);write(out/'initial_certificate.json',inc)
    records=[]
    for block in range(8):
        saved=snapshot(net,opt);before=sha(saved);start=time.perf_counter()
        for _ in range(25):
            opt.zero_grad(set_to_none=True);loss=-obj(net);loss.backward();opt.step()
        generation=time.perf_counter()-start
        candidate=obj(net,details=True);c,checkseconds=check(candidate)
        accepted=c['status']=='CERTIFIED' and c['value_interval'][0]>inc['value_interval'][1]
        oldinterval=inc['value_interval'][:]
        if accepted: inc=c
        else: restore(net,opt,saved)
        after=sha(snapshot(net,opt))
        assert accepted or before==after
        r={'block':block+1,'accepted':accepted,'candidate_certificate':c,'incumbent_before':oldinterval,
           'incumbent_after':inc['value_interval'],'state_hash_before':before,'state_hash_after':after,
           'restoration_exact':not accepted and before==after,'gradient_calls':25,'function_calls':25,
           'generation_seconds':generation,'checker_seconds':checkseconds}
        records.append(r);write(out/f'candidate_{block+1:02d}.json',candidate)
        write(out/'records.json',records);print('stress',block+1,accepted,flush=True)
    saved=snapshot(net,opt);before=sha(saved)
    # Explicit fault injection is a state-integrity regression, not solver evidence.
    with torch.no_grad():next(net.parameters()).add_(7)
    opt.param_groups[0]['lr']=.123;torch.rand(3);np.random.rand(3);random.random()
    corrupted=sha(snapshot(net,opt));restore(net,opt,saved);after=sha(snapshot(net,opt))
    tests={'no_op_rejected':not(inc['value_interval'][0]>inc['value_interval'][1]),
           'corrupted_state_detected':corrupted!=before,'network_optimizer_rng_restored':after==before,
           'nature':'explicit fault-injection regression; not an optimizer performance observation'}
    assert all(tests[k] for k in ('no_op_rejected','corrupted_state_detected','network_optimizer_rng_restored'))
    write(out/'fault_injection.json',tests)
    write(out/'summary.json',{'blocks':8,'accepted':sum(r['accepted'] for r in records),
          'rejected':sum(not r['accepted'] for r in records),'initial_checker_seconds':seconds,
          'total_checker_seconds':seconds+sum(r['checker_seconds'] for r in records),
          'total_generation_seconds':sum(r['generation_seconds'] for r in records),'final_value_interval':inc['value_interval'],
          'checkpoint_spacing':25,'adam_learning_rate':.5,'stress_test_not_broad_robustness':True})

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--part',choices=['crossed','stress','all'],default='all')
    args=parser.parse_args()
    write(REV/'results/environment.json',{'python':platform.python_version(),'torch':torch.__version__,
          'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),'threads':1,
          'protocol_commit':'082a3fdcf97d426df65858702b506bcdd7384ee3'})
    if args.part in ('crossed','all'):run_crossed()
    if args.part in ('stress','all'):run_stress()
