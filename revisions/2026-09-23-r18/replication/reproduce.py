"""Execute the new R18 checks without overwriting any R16/R17 evidence.
Run from any working directory: python revisions/2026-09-23-r18/replication/reproduce.py
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json, random, sys, time
import numpy as np
import torch
from objective_bridge import ROOT,R16,R17,HERE,M,C,audit_all,validate_inputs
sys.path.insert(0,str(R17/'replication'))
import nonlinear_inventory as N
import control_ranges
OUT=HERE.parent/'results'

def finite_horizon_exact_tests():
    """Exact rational finite-MDP checks, including policy-dependent defects."""
    rng=random.Random(1823);q=F(99,100);worst=F(0);cases=0
    for horizon in [1,2,4,8]:
      for trial in range(20):
        S,A=3,2
        P=[];r=[];pol=[];v=[]
        for n in range(horizon):
            weights=[[[rng.randint(1,9) for k in range(S)] for a in range(A)] for s in range(S)]
            P.append([[[F(t,sum(w)) for t in w] for w in row] for row in weights])
            r.append([[F(rng.randint(-8,8),10) for a in range(A)] for s in range(S)])
            pol.append([rng.randrange(A) for s in range(S)])
            v.append([F(rng.randint(-40,40),10) for s in range(S)])
        g=[F(rng.randint(-10,10),10) for s in range(S)]
        v.append([t+F(rng.randint(-4,4),10) for t in g]);b=max(abs(v[-1][s]-g[s]) for s in range(S))
        star=g.copy();pay=g.copy();eps=[];eta=[]
        for n in reversed(range(horizon)):
            op=lambda w:[[r[n][s][a]+q*sum(P[n][s][a][k]*w[k] for k in range(S)) for a in range(A)] for s in range(S)]
            tv=op(v[n+1]);ev=max(abs(v[n][s]-tv[s][pol[n][s]]) for s in range(S));gr=max(max(tv[s])-tv[s][pol[n][s]] for s in range(S));eps.append(ev);eta.append(gr)
            optimal=op(star);candidate=op(pay);star=[max(x) for x in optimal];pay=[candidate[s][pol[n][s]] for s in range(S)]
        eps.reverse();eta.reverse();bound=2*q**horizon*b+sum(q**n*(2*eps[n]+eta[n]) for n in range(horizon))
        actual=max(star[s]-pay[s] for s in range(S))
        assert 0<=actual<=bound
        worst=max(worst,actual/bound if bound else F(0));cases+=1
    return {'status':'PASS','exact_rational_finite_MDP_cases':cases,'largest_loss_to_bound_ratio':float(worst),'scope':'Regression of the stated finite-horizon lemma; not a continuous-time neural convergence experiment'}

def direct_replays():
    out=OUT/'direct_replay';out.mkdir(exist_ok=True)
    rows=[]
    for arch in ['accessible','allface']:
        folder=R17/'results'/arch/'seed17100'
        old=json.loads((folder/'certificate400.json').read_text())
        new=C.audit(folder/'network_step0400.json',out/f'{arch}_seed17100.json',(4,16,16),chunk=1024)
        assert new['network_sha256']==old['network_sha256']
        assert abs(new['t0_regret_upper']-old['t0_regret_upper'])<1e-11
        rows.append({'architecture':arch,'old_upper':old['t0_regret_upper'],'new_upper':new['t0_regret_upper'],'complete_cells':new['interior_cells'],'wall_seconds':new['wall_seconds']})
    # Recompute every retained final neural-plan query certificate (3*3*2).
    plans=[]
    for d in [8,32,128]:
        folder=R17/'results/nonlinear_inventory'/f'd{d}'
        old=json.loads((folder/'records.json').read_text())
        for seed in [17400,17401,17402]:
          for query in ['alternating','uniform']:
            path=folder/f'plan_neural_s{seed}_{query}_k32.json'
            p=json.loads(path.read_text());new=N.directed_check(np.array(p['x']),np.array(p['u']))
            prior=next(t for t in old if t['method']=='neural_plus_gradient' and t['seed']==seed and t['query']==query and t['corrections']==32)
            assert abs(new['total_cost_loss_upper']-prior['total_cost_loss_upper'])<=1e-24
            new.update({'d':d,'seed':seed,'query':query,'plan_sha256':hashlib.sha256(path.read_bytes()).hexdigest()});plans.append(new)
    result={'whole_cylinder_replays':rows,'nonlinear_final_plan_replays':plans}
    (out/'replays.json').write_text(json.dumps(result,indent=2)+'\n')
    return {'original_full_domain_replays':len(rows),'nonlinear_point_plan_replays':len(plans)}

def tests():
    # MPFR core exact-rational basic operations are tested, not assumed tested.
    checks={'arithmetic':M.test(),'finite_horizon':finite_horizon_exact_tests()}
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
    rng=np.random.default_rng(1823);d=8;x=rng.uniform(-1,1,d);u=rng.uniform(-.25,.25,(12,d))
    a=torch.tensor(u,requires_grad=True);v=N.torch_cost(torch.tensor(x),a);g=torch.autograd.grad(v,a)[0].detach().numpy();_,analytical=N.cost_gradient(x,u)
    discrepancy=float(np.max(np.abs(g-analytical)));assert discrepancy<1e-11
    # The Hessian checks are regression diagnostics; the global Hessian theorem
    # in the manuscript is proved analytically, not inferred from eigenvalues.
    h=torch.autograd.functional.hessian(lambda z:N.torch_cost(torch.tensor(x),z.reshape(12,d)),torch.tensor(u.ravel())).detach().numpy()
    ev=np.linalg.eigvalsh(h);assert ev.min()>=4-1e-10 and ev.max()<=177/8+1e-10
    checks['gradient_diagnostic']={'max_difference':discrepancy,'sample_hessian_eigenvalue_range':[float(ev.min()),float(ev.max())],'proof_by_sampling':False}
    for d in [8,32,128]:
        vals=[N.uniform_bound(d,k)['total_cost_loss_upper'] for k in [0,8,16,24,32]]
        assert all(b<a for a,b in zip(vals,vals[1:]));assert vals[-1]<.000002
    checks['analytic_uniform_curve']={'dimensions':[8,32,128],'budgets':[0,8,16,24,32],'status':'PASS'}
    return checks

if __name__=='__main__':
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    audit_all(OUT/'objective_bridge');check=tests();check['direct_replays']=direct_replays()
    ranges=control_ranges.run();check['control_ranges']={'status':ranges['status'],'classical_policies':len(ranges['classical']),'fresh_library_nodes':ranges['fresh_library']['nodes']}
    check['immutable_inputs_after_execution']=validate_inputs();check['wall_seconds']=time.perf_counter()-start;check['status']='PASS'
    (OUT/'validation.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps(check,indent=2),flush=True)
