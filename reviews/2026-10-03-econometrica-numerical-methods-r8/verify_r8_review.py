from __future__ import annotations
import sys, json, math, hashlib, time
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution

ROOT=Path(__file__).resolve().parents[2]
R8=ROOT/'revisions/2026-10-03-r8'
CODE=R8/'code'; RES=R8/'results'
sys.path.insert(0,str(CODE))
import action_enclosure as ae
from action_enclosure_tight import CornerEncloser
from continuous_actor import Model, LO, HI

rng=np.random.default_rng(20261003)
m=Model()
cert=np.load(RES/'SHARED_ACTION_CERTIFICATES.npz')
U=cert['common_optimal_upper']

# independent point evaluator (does not call project qvalue/interp/encloser)
def reflect_np(x,lo,hi):
    length=hi-lo
    z=np.mod(x-lo,2*length)
    return lo+np.where(z<=length,z,2*length-z)

def terminal_np(u,y):
    return np.exp((1-u)*y)/(1-u)

def interp_np(v,u,y):
    fu=(u-m.us[0])/(m.us[1]-m.us[0]); fy=(y-m.ys[0])/(m.ys[1]-m.ys[0])
    iu=np.clip(np.floor(fu).astype(int),0,m.nu-2); iy=np.clip(np.floor(fy).astype(int),0,m.nx-2)
    wu=np.clip(fu-iu,0,1); wy=np.clip(fy-iy,0,1)
    vg=np.asarray(v).reshape(m.nu,m.nx)
    return ((1-wu)*(1-wy)*vg[iu,iy] + wu*(1-wy)*vg[iu+1,iy]
            +(1-wu)*wy*vg[iu,iy+1] + wu*wy*vg[iu+1,iy+1])

def q_rows(v, actions):
    # actions shape (N,3)
    actions=np.asarray(actions,float)
    u=m.points[:,0]; y=m.points[:,1]
    cons,p,theta=actions.T
    reward=m.h*(np.exp((1-u)*(np.log(cons)+y))/(1-u)-.5*m.cost*theta**2)
    cont=np.zeros(m.N)
    for z1,z2 in [(math.sqrt(2),0),(-math.sqrt(2),0),(0,math.sqrt(2)),(0,-math.sqrt(2))]:
        un=reflect_np(u+theta*m.h+.08*math.sqrt(m.h)*z1,m.us[0],m.us[-1])
        yn=y+(.02+.06*p-cons-.02*p*p)*m.h+.2*p*math.sqrt(m.h)*(-.3*z1+math.sqrt(.91)*z2)
        outside=(yn<m.ys[0])|(yn>m.ys[-1]); yc=np.clip(yn,m.ys[0],m.ys[-1])
        z=interp_np(v,un,yc)
        z[outside]=terminal_np(un[outside],yc[outside])
        cont+=z/4
    out=reward+m.q*cont
    out[m.boundary]=m.g[m.boundary]
    return out

def q_scalar(v,row,a):
    if m.boundary[row]:
        return float(m.g[row])
    u=float(m.points[row,0]); y=float(m.points[row,1])
    cons,p,theta=map(float,a)
    reward=m.h*(math.exp((1-u)*(math.log(cons)+y))/(1-u)-.5*m.cost*theta*theta)
    cont=0.0
    vg=np.asarray(v).reshape(m.nu,m.nx)
    for z1,z2 in [(math.sqrt(2),0),(-math.sqrt(2),0),(0,math.sqrt(2)),(0,-math.sqrt(2))]:
        un=float(reflect_np(np.array([u+theta*m.h+.08*math.sqrt(m.h)*z1]),m.us[0],m.us[-1])[0])
        yn=y+(.02+.06*p-cons-.02*p*p)*m.h+.2*p*math.sqrt(m.h)*(-.3*z1+math.sqrt(.91)*z2)
        outside=(yn<m.ys[0]) or (yn>m.ys[-1]); yc=min(max(yn,m.ys[0]),m.ys[-1])
        if outside:
            z=math.exp((1-un)*yc)/(1-un)
        else:
            fu=(un-m.us[0])/(m.us[1]-m.us[0]); fy=(yc-m.ys[0])/(m.ys[1]-m.ys[0])
            iu=min(max(int(math.floor(fu)),0),m.nu-2); iy=min(max(int(math.floor(fy)),0),m.nx-2)
            wu=min(max(fu-iu,0.0),1.0); wy=min(max(fy-iy,0.0),1.0)
            z=((1-wu)*(1-wy)*vg[iu,iy] + wu*(1-wy)*vg[iu+1,iy]
               +(1-wu)*wy*vg[iu,iy+1] + wu*wy*vg[iu+1,iy+1])
        cont+=z/4
    return float(reward+m.q*cont)

# Cross-check independent evaluator against project torch point evaluator
point_eval_max_abs=0.0
for _ in range(12):
    a=rng.uniform(LO,HI,size=(m.N,3)); v=rng.normal(-5,1,size=m.N)
    exact=q_rows(v,a)
    import torch
    with torch.no_grad(): proj=m.qvalue(torch.tensor(v),torch.tensor(a),False).numpy()
    point_eval_max_abs=max(point_eval_max_abs,float(np.max(np.abs(exact-proj))))

# Random enclosure inclusion with point continuation and interval continuation.
def random_boxes():
    center=rng.uniform(LO,HI,size=(m.N,3))
    half=rng.uniform(0,.45,size=(m.N,3))*(HI-LO)
    return np.maximum(LO,center-half),np.minimum(HI,center+half)

point_violation=0.0; interval_violation=0.0; checked_points=0
for t in [0,4,9,14,19]:
    lo_a,hi_a=random_boxes()
    enc=CornerEncloser(m,U[t+1]).q(np.arange(m.N),lo_a,hi_a)
    for _ in range(48):
        a=lo_a+rng.random((m.N,3))*(hi_a-lo_a)
        q=q_rows(U[t+1],a)
        point_violation=max(point_violation,float(np.max(np.maximum(enc.lo-q,q-enc.hi))))
        checked_points+=m.N

    # interval continuation from a genuine propagated policy bracket
    vlo=cert['continuous_actor_s11_search_hybrid_lower'][t+1]
    vhi=cert['continuous_actor_s11_search_hybrid_upper'][t+1]
    lo_a,hi_a=random_boxes(); enc=CornerEncloser(m,vlo,vhi).q(np.arange(m.N),lo_a,hi_a)
    for _ in range(32):
        vv=vlo+rng.random(m.N)*(vhi-vlo)
        a=lo_a+rng.random((m.N,3))*(hi_a-lo_a)
        q=q_rows(vv,a)
        interval_violation=max(interval_violation,float(np.max(np.maximum(enc.lo-q,q-enc.hi))))
        checked_points+=m.N

# Independent DE lower bounds compared with stored global upper envelope
active=np.flatnonzero(~m.boundary)
rows=[]
for t in [0,4,9,14,19]:
    selected=[active[len(active)//2],active[0],active[-1]]
    selected+=rng.choice(active,size=5,replace=False).tolist()
    for r in selected: rows.append((t,int(r)))
max_upper_violation=-np.inf; max_slack=-np.inf; min_slack=np.inf; opt_records=[]
for idx,(t,r) in enumerate(rows):
    f=lambda a:-q_scalar(U[t+1],r,a)
    de=differential_evolution(f,list(zip(LO,HI)),seed=20261003+idx,maxiter=60,popsize=10,
                              polish=True,tol=1e-9,atol=1e-11,workers=1,updating='immediate')
    lower=-float(de.fun); upper=float(U[t,r]); slack=upper-lower
    max_upper_violation=max(max_upper_violation,lower-upper)
    max_slack=max(max_slack,slack); min_slack=min(min_slack,slack)
    opt_records.append(dict(t=t,row=r,lower=lower,stored_upper=upper,slack=slack,success=bool(de.success)))

# Summaries of evidence/results
action=json.loads((RES/'SHARED_ACTION_CERTIFICATES.json').read_text())['records']
hybrid=[x for x in action if not x['raw']]
method_summary={}
for meth in ['actor','direct','local']:
    rr=[x for x in hybrid if x['method']==meth]
    method_summary[meth]={
        'uniform_bounds':[x['policy_regret_upper'] for x in rr],
        'mean_uniform_bound':float(np.mean([x['policy_regret_upper'] for x in rr])),
        'center_bounds':[x['initial_state_regret_upper'] for x in rr],
        'passes_0_1':sum(x['absolute_target_pass']['0.1'] for x in rr),
    }
run_summary={}
for meth,patterns in {
    'actor':'continuous_actor_s{seed}_search.json',
    'direct':'continuous_direct_s{seed}_search.json',
    'local':'continuous_direct_s{seed}_steps0_search.json'}.items():
    xs=[json.loads((RES/patterns.format(seed=s)).read_text()) for s in [11,29,47]]
    run_summary[meth]={
        'training_seconds':[x['training_seconds'] for x in xs],
        'mean_training_seconds':float(np.mean([x['training_seconds'] for x in xs])),
        'training_action_queries':[x['training_action_queries'] for x in xs],
        'mean_queries':float(np.mean([x['training_action_queries'] for x in xs])),
        'lower_bound_deviation':[x['augmented_grid_deviation_max'] for x in xs],
        'local_search_changed_fraction':[x['local_search_changed_fraction'] for x in xs],
        'raw_finite_reference_loss':[x['raw_finite_reference_minus_policy_max'] for x in xs],
        'hybrid_finite_reference_loss':[x['finite_reference_minus_policy_max'] for x in xs],
    }

comparators=[]
for p in sorted(RES.glob('comparison_ndu_*.json')):
    x=json.loads(p.read_text())
    comparators.append(dict(file=p.name,method=x['method'],degree=x.get('degree'),seed=x['seed'],
        policy_bound=max(x['certificate']['payoff_loss_upper']),value_error=x.get('value_error'),
        training_seconds=x['training_seconds'],verification_seconds=x['certificate']['seconds'],
        target_pass=x['target_pass'],parameter_count=x.get('parameter_count')))

games=[]
for p in sorted(RES.glob('comparison_game_*.json')):
    x=json.loads(p.read_text()); games.append(dict(file=p.name,method=x['method'],market=x['market'],seed=x['seed'],
        max_regret=max(x['certificate']['payoff_loss_upper']),training_seconds=x['training_seconds'],
        verification_seconds=x['certificate']['seconds'],missing_pure_stages=x['missing_pure_stages'],target_pass=x['target_pass']))

ref=json.loads((RES/'REFINEMENT.json').read_text())['records']
ref_summary={
    'max_finite_reference_minus_policy_by_grid':{},
    'center_policy_payoff_ranges':{}
}
for grid in sorted({tuple(x['grid']+[x['steps']]) for x in ref}):
    xs=[x for x in ref if tuple(x['grid']+[x['steps']])==grid]
    key=f'{grid[0]}x{grid[1]}_steps{grid[2]}'
    ref_summary['max_finite_reference_minus_policy_by_grid'][key]=float(max(x['finite_reference_minus_policy'] for x in xs))
    ref_summary['center_policy_payoff_ranges'][key]=[float(min(x['center_policy_payoff'] for x in xs)),float(max(x['center_policy_payoff'] for x in xs))]

execution=json.loads((RES/'EXECUTION.json').read_text())
result={
    'reviewed_evidence_commit':'f9a7e32e23c0b4173390d4807da6eace46f42ba1',
    'independent_point_evaluator_max_abs_difference':point_eval_max_abs,
    'random_enclosure_stress':{
        'checked_point_evaluations':checked_points,
        'point_continuation_max_violation':point_violation,
        'interval_continuation_max_violation':interval_violation,
        'interpretation':'nonpositive/numerical-zero violation supports inclusion on sampled boxes; not a formal proof'
    },
    'independent_global_search_stress':{
        'cases':len(opt_records),
        'max_lower_bound_above_stored_upper':max_upper_violation,
        'minimum_stored_upper_minus_DE_lower':min_slack,
        'maximum_stored_upper_minus_DE_lower':max_slack,
        'records':opt_records,
        'interpretation':'heuristic differential-evolution optima are lower bounds only; no case exceeded the stored upper envelope'
    },
    'all_recorded_commands_returned_zero':all(x['returncode']==0 for x in execution),
    'recorded_commands':len(execution),
    'method_summary':method_summary,
    'run_summary':run_summary,
    'finite_ndu_comparators':comparators,
    'dynamic_game_comparators':games,
    'refinement_summary':ref_summary,
    'certificate_budget':{}
}
for name in ['continuous_actor_s11_search_action_certificate.json','continuous_actor_s11_search_corner_certificate.json']:
    x=json.loads((RES/name).read_text()); result['certificate_budget'][name]={
        'policy_regret_upper':x['policy_regret_upper'],
        'all_action_optimizations_closed':x['all_action_optimizations_closed'],
        'budget_exhausted_steps':sum(h['budget_exhausted'] for h in x['history']),
        'steps':len(x['history']),
        'total_box_evaluations':sum(h['box_evaluations'] for h in x['history']),
        'total_unresolved_leaves':sum(h['unresolved_leaves'] for h in x['history']),
        'max_one_step_optimization_bracket':max(h['maximum_optimization_bracket'] for h in x['history']),
        'seconds':x['seconds']}


import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--output',default=str(Path(__file__).with_name('verification_results.json')))
args=parser.parse_args()
out=Path(args.output)
out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['independent_global_search_stress','finite_ndu_comparators','dynamic_game_comparators','run_summary']},indent=2))
print('DE max violation',max_upper_violation,'slack range',min_slack,max_slack)
print('wrote',out)
