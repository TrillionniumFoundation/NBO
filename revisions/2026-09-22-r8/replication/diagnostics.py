"""Post-review NDU action tests, explicitly priced safeguards, separated meshes.

Historical R5 data are immutable inputs. No coarse/fine difference is converted
into a continuum error bound and no corrected policy is called a raw success.
"""
from __future__ import annotations
import dataclasses,json,math,pathlib,sys,time
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'revisions/2026-09-22-r8/results'
OLD=ROOT/'revisions/2026-09-21-r5/results'
sys.path.insert(0,str(ROOT/'revisions/2026-09-21-r5/replication'))
import continuous_actor as ca
import scheme_validation as scheme

def maximize_jet(u,x,vu,vx,vxx,vux,k):
    c=.8 if vx<=0 else np.clip(math.exp(-math.log(vx)/u),.05,.8)
    th=np.clip(vu/k,-.2,.2)
    lin=.06*x*vx-.0025*x*vux; curvature=.04*x*x*vxx
    if curvature<0:p=np.clip(-lin/curvature,-.5,.8)
    else:p=max([-.5,.8],key=lambda a:lin*a+.5*curvature*a*a)
    return np.array([c,th,p])

def action_tests():
    rng=np.random.default_rng(8201);worst=0.
    for _ in range(1000):
        u=rng.uniform(1.2,2.8);x=rng.uniform(.5,2)
        vu,vx,vxx,vux=rng.normal(size=4);k=float(rng.choice([.5,2,8]))
        a=maximize_jet(u,x,vu,vx,vxx,vux,k)
        def h(c,th,p):return c**(1-u)/(1-u)-vx*c+vu*th-k*th*th/2+(.06*x*vx-.0025*x*vux)*p+.02*x*x*vxx*p*p
        grid=max(h(c,0,0) for c in np.linspace(.05,.8,101))+max(h(1,t,0) for t in np.linspace(-.2,.2,101))-h(1,0,0)+max(h(1,0,p) for p in np.linspace(-.5,.8,101))-h(1,0,0)
        worst=max(worst,float(grid-h(*a)))
    assert worst<1e-10
    cases=[maximize_jet(2,1,0,vx,curv,0,2).tolist() for vx,curv in [(0,0),(-1,1),(1,-1),(1,0)]]
    return {'random_jets':1000,'max_grid_advantage':worst,'edge_cases':cases,
      'interpretation':'Regression test of the proved generator selection formula, not a proof from random sampling.'}

def recost(tag,target):
    record=json.loads((OLD/(tag+'.json')).read_text());cfg=ca.old.Config(**record['config'])
    proposal=np.load(OLD/(tag+'.npz'))['proposal'];policy=proposal.copy()
    states,bd=ca.old.states(cfg);S=len(states);A=len(ca.old.actions(cfg))
    weights=np.exp(-cfg.rho*cfg.dt*np.arange(cfg.n));threshold=target/(2*weights.sum())
    start=time.perf_counter();history=[]
    for sweep in range(cfg.n+1):
        t=time.perf_counter();aud=ca.audit(cfg,policy,proposal)
        bound=float(aud['localized'][0].max())
        history.append({'sweep':sweep,'localized_bound':bound,'uniform_bound':aud['uniform'],
          'overridden_fraction':float(np.any(np.abs(policy[:,~bd]-proposal[:,~bd])>1e-10,-1).mean()),
          'audit_seconds':time.perf_counter()-t})
        if bound<=target:break
        bad=aud['gaps']>threshold
        policy=np.where(bad[...,None],aud['greedy'],policy)
    audits=len(history)
    result={'tag':tag,'target':target,'threshold':float(threshold),'history':history,
      'final_pass':bound<=target,'total_audit_seconds':time.perf_counter()-start,
      'audits':audits,'state_action_value_evaluations':audits*cfg.n*S*(A+2),
      'state_action_envelope_evaluations':audits*cfg.n*S*(A+1),
      'shock_branches_per_action':4,'grid_actions_per_state_date':A,
      'historical_training_seconds':record.get('training_seconds',record.get('train_seconds')),
      'timing_caveat':'Historical training and current audit use different runs/environments; do not add as a measured common-machine total.',
      'certificate_scope':'R5 finite candidate economy only; no continuum precision inferred'}
    np.savez_compressed(OUT/f'threshold_{tag}_{target:g}.npz',policy=policy,gaps=aud['gaps'],bound=aud['localized'])
    return result

def refinements():
    scheme.OUT=OUT
    configs=[]
    for n in [24,48,96]:configs.append(('time',ca.old.Config(n=n,nu=25,nx=31,na=5)))
    for nu,nx in [(25,31),(37,46),(49,61)]:configs.append(('state',ca.old.Config(n=48,nu=nu,nx=nx,na=5)))
    for na in [3,5,9]:configs.append(('action',ca.old.Config(n=48,nu=25,nx=31,na=na)))
    for k in [.5,2.,8.]:configs.append(('joint_cost',ca.old.Config(n=96,nu=49,nx=61,na=9,k=k)))
    cache={};rows=[]
    for factor,cfg in configs:
        key=str(cfg)
        if key not in cache:cache[key]=scheme.sparse_ndu(cfg)
        rows.append({'factor':factor,**cache[key]})
    return rows

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--task',choices=['algebra','safeguard','mesh'],default='algebra');args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if args.task=='algebra':result=action_tests()
    elif args.task=='safeguard':
        result=[recost(tag,target) for tag in ['n6_s10_w48_a600_c800_lr0.004','n12_s10_w48_a600_c800_lr0.004'] for target in [.05,.01]]
    else: result=refinements()
    (OUT/(args.task+'_results.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
