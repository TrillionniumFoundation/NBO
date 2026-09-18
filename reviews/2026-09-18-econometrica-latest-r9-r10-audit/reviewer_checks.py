#!/usr/bin/env python3
"""R9 independent review orchestration (NumPy/SciPy, no training or network).
Uses the pinned author's finite-array constructor, but an independent Bellman
recursion and directional masks. Not an independent constructor enclosure,
a continuous-control solution, or a diffusion calculation. No source writes.
Run: python reviewer_checks.py --repo /path/to/NBO --out reviewer_results.json
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,sys,time
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
import numpy as np
import scipy

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def serial(x):
    if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [serial(v) for v in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x

def run(root,dest):
    started=time.perf_counter()
    inputs=[p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.suffix!='.pyc']
    before={str(p.relative_to(root)):digest(p) for p in inputs}
    sys.path.insert(0,str(root/'replication/r9'))
    import contracts as author
    base=author.Model();e=base.e[0];N=base.steps;ns=base.ns;ctr=base.center;rows=np.arange(ns);bd=e.boundary
    arrays=[np.concatenate((np.broadcast_to(e.menu,(ns,len(e.menu),3)),e.extra[n].actions),axis=1) for n in range(N)]
    print('BUILT',base.build_seconds,base.nbytes,flush=True);cache={}
    yield {'phase':'constructor','seconds':base.build_seconds}
    def solve(lam,d,mode='full',fee=0.,minimum=8):
        key=(float(lam),float(d),mode,float(fee),int(minimum))
        if key in cache:return cache[key]
        V=np.empty((N+1,ns));V[-1]=base.terminal;pol=np.empty((N,ns),np.int32)
        for n in range(N-1,-1,-1):
            th=arrays[n][:,:,1]
            if mode=='full':allow=True
            elif mode=='zero':allow=np.abs(th)<=1e-14
            elif mode=='up':allow=th>=-1e-14
            elif mode=='down':allow=th<=1e-14
            else:raise ValueError(mode)
            Q=(1-lam)*base.q(0,n,V[n+1],d)+lam*base.q(1,n,V[n+1],d)
            Q=np.where(allow,Q,-np.inf)
            Q=np.column_stack((Q,np.where((~bd)&(n>=minimum),base.terminal-fee,-np.inf)))
            pol[n]=Q.argmax(1);V[n]=Q[rows,pol[n]]
        classes={};c=author.Contract(base,fee,minimum)
        for sign in ('positive','nonpositive'):
            assert minimum>=1
            risk=arrays[0][:,:,2];mask=risk>0 if sign=='positive' else risk<=0
            qq=np.where(np.column_stack((mask,np.zeros(ns,dtype=bool))),Q,-np.inf)
            pp=pol.copy();vv=V.copy();pp[0]=qq.argmax(1);vv[0]=qq[rows,pp[0]]
            f=c.moments(pp,lam);replay=float(np.max(abs(vv-(f[0]+d*f[1]-fee*f[2]))));assert replay<2e-11
            classes[sign]={'value':float(vv[0,ctr]),'action':c.initial_action(pp),'base':float(f[0,0,ctr]),
                'duration':float(f[1,0,ctr]),'surrender':float(f[2,0,ctr]),'effort':float(f[3,0,ctr]),
                'replay_error':replay,'V':vv,'policy':pp}
        classes['delta']=classes['positive']['value']-classes['nonpositive']['value'];cache[key]=classes
        print('SOLVED',key,classes['delta'],flush=True);return classes
    def brief(z):return {k:({a:b for a,b in v.items() if a not in ('V','policy')} if isinstance(v,dict) else v) for k,v in z.items()}
    result={'scope':__doc__,'review_date':'2026-09-18','snapshot_commit':'755b507870b54a100616b0658eba9a031eef2833',
        'scientific_commit':'8c1e0472279fb66a2419b63b3e35df028ecfdd78',
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
        'constructor':{'seconds':base.build_seconds,'kernel_bytes':base.nbytes,'states':ns,'steps':N,'operating_actions_per_node':arrays[0].shape[1]},
        'directional':[],'surrender':[]}
    # Focal direction diagnostic; not a regional certificate.
    for lam,d in ((.125,.425),):
        rr={'lambda':lam,'benefit':d}
        for mode in ('full','zero','up','down'):
            rr[mode]=brief(solve(lam,d,mode))
            yield {'phase':'direction','lambda':lam,'benefit':d,'mode':mode,'delta':rr[mode]['delta']}
        for mode in ('full','up','down'):rr[mode+'_relative_option']=rr[mode]['delta']-rr['zero']['delta']
        result['directional'].append(rr)
    checks=[]
    for mode,adj in (('full',True),('zero',False)):
        zz=solve(.125,.425,mode);az=author.Contract(base,0.,8).pair(.125,.425,adj)
        for sign in ('positive','nonpositive'):
            it=zz[sign];direct=base.direct(it['policy'],.125,.425)
            err=float(np.max(abs(direct-it['V'])));dp_err=float(np.max(abs(az[sign]['value']-it['V'])));assert max(err,dp_err)<2e-11
            checks.append({'mode':mode,'sign':sign,'selected_control_reconstruction':err,'author_dp_difference':dp_err})
    result['replay_checks']=checks;result['supersolution']=[]
    yield {'phase':'replays','checks':checks}
    for lam in (0.,.25):
        for n in range(N):
            q=(1-lam)*base.q(0,n,base.terminal,.45)+lam*base.q(1,n,base.terminal,.45);residual=q-base.terminal[:,None]
            result['supersolution'].append({'lambda':lam,'date':n,'max_interior':float(residual[~bd].max()),'boundary_abs':float(abs(residual[bd]).max())})
    deposited=json.loads((root/'replication/r9/output/surrender.json').read_text());dep={x['fee']:x for x in deposited['center'] if x['min_term']==1}
    for fee in (0.,.7,.8,.85):
        rr={'fee':fee,'lambda':.125,'benefit':.425}
        for mode,name in (('full','adjusted'),('zero','no_adjustment')):
            zz=solve(.125,.425,mode,fee,1);rr[name]=brief(zz);delta=abs(zz['delta']-dep[fee][name]['delta'])
            rr[name]['deposited_delta_error']=delta;assert delta<2e-11
            yield {'phase':'surrender','fee':fee,'mode':mode,'delta':zz['delta']}
        rr['relative_option']=rr['adjusted']['delta']-rr['no_adjustment']['delta'];result['surrender'].append(rr)
    result['adverse_fee_080_corner']={}
    for mode in ('full','zero'):
        result['adverse_fee_080_corner'][mode]=brief(solve(0.,.4,mode,.8,1))
        yield {'phase':'adverse_corner','mode':mode,'delta':result['adverse_fee_080_corner'][mode]['delta']}
    result['initial_action_value_diagnostics']=[];lam=.125;d=.425
    v1=solve(lam,d,'full')['positive']['V'][1];v10=solve(lam,d,'zero')['positive']['V'][1]
    Q1=sum(w*base.q(k,0,v1,d)[ctr] for k,w in enumerate((1-lam,lam)))
    Q0=sum(w*base.q(k,0,np.zeros(ns),d)[ctr] for k,w in enumerate((1-lam,lam)))
    Q10=sum(w*base.q(k,0,v10,d)[ctr] for k,w in enumerate((1-lam,lam)));aa=arrays[0][ctr]
    for pi in (.8,-.5):
        indices={}
        for th in (-.2,0.,.2):
            hits=np.flatnonzero(np.all(np.isclose(aa,np.array([.8,th,pi]),atol=1e-14,rtol=0),axis=1));assert len(hits)>0;indices[th]=int(hits[0])
        j0=indices[0.];comparisons=[]
        for th,j in indices.items():
            comparisons.append({'theta':th,'Q_adjusted_continuation':float(Q1[j]),'gain_vs_zero_theta':float(Q1[j]-Q1[j0]),
                'current_reward_gain':float(Q0[j]-Q0[j0]),'continuation_gain':float((Q1[j]-Q0[j])-(Q1[j0]-Q0[j0]))})
        result['initial_action_value_diagnostics'].append({'pi':pi,'comparison':comparisons,'future_adjustment_value_with_zero_initial_theta':float(Q1[j0]-Q10[j0])})
    bank=np.load(root/'replication/r9/output/reachable_fee_coefficients.npz');reach=np.zeros((N+1,ns),bool);reach[0,ctr]=True
    for n in range(N):
        for ee in base.e:
            for kernel in [ee.common]+ee.extra[n:n+1]:reach[n+1]|=(kernel.matrix.T@np.repeat(reach[n].astype(float),kernel.na))>0
    assert np.array_equal(reach,bank['reachable']);cc=author.Contract(base,0.,8);co=[];co_errors=[]
    for k in range(2):
        pp=bank[f'policy.{k}'];recomputed=cc.coefficients(pp,.4,0.,all_dates=True);co.append(recomputed)
        co_errors.extend(float(np.max(abs(recomputed[n]-bank[f'coefficient.{k}.{n}']))) for n in range(N+1))
    bounds=[]
    for minimum in range(1,9):
        worst=0.
        for n in range(minimum,8):
            for lo,hi in zip(np.linspace(0,.25,17)[:-1],np.linspace(0,.25,17)[1:]):
                lower=np.maximum.reduce([author.r7.restrict(x[n],lo,hi).min(0) for x in co])-1e-7;eligible=reach[n]&~bd
                if np.any(eligible):worst=max(worst,float(np.max((base.terminal-lower)[eligible])))
        bounds.append(worst)
    deposited_bound=json.loads((root/'replication/r9/output/reachable_fee.json').read_text())['sufficient_fee_bounds'];assert np.max(abs(np.array(bounds)-deposited_bound))<2e-11
    result['enforcement']={'reachable_counts':reach.sum(1),'coefficient_reconstruction_error':max(co_errors),'sufficient_bounds':bounds,
        'inactive_fee_margin':.85-bounds[0],'bound_deposit_error':float(np.max(abs(np.array(bounds)-deposited_bound)))}
    G=float(base.terminal[ctr]);b=.9;rows_out=[]
    for mode in ('full','zero'):
        for fee,minimum,C in ((.85,1,.01),(0.,8,0.)):
            zz=solve(.125,.425,mode,fee,minimum);sign=max(('positive','nonpositive'),key=lambda s:zz[s]['value']);ww=zz[sign]['value'];A=zz[sign]['duration'];q=max(0.,G-ww+C)
            rows_out.append({'mode':mode,'fee':fee,'minimum_term':minimum,'capacity_cost':C,'outside_value':G,'chosen_class':sign,'operating_value':ww,'duration':A,'minimum_grant':q,'principal_surplus':b*A-q})
    result['procurement']=rows_out
    result['source_hashes']={p:before[p] for p in before if (p.startswith('replication/r9/') and '/output/' not in p) or p in ('replication/r8/model.py','replication/r8/numerical_core.py','replication/r4/solver.py','replication/r7/core.py','ECTA_R9.tex','SUPP_R9.tex','REVISION_INDEX.md','.github/workflows/revision-r10.yml')}
    changed=[str(p.relative_to(root)) for p in inputs if digest(p)!=before[str(p.relative_to(root))]];assert not changed,changed
    result['input_integrity']={'files_checked':len(inputs),'changed_files':changed};result['elapsed_seconds']=time.perf_counter()-started
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(serial(result),indent=2,allow_nan=False)+'\n');print('DONE',dest,result['elapsed_seconds'],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    for progress in run(a.repo.resolve(),a.out.resolve()):print('CHECKPOINT',json.dumps(serial(progress)),flush=True)
