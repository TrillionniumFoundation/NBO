#!/usr/bin/env python3
"""Independent Bellman orchestration and selected-transition replay for NBO R9.
Run from a full checkout. Author constructors and frozen proposals are reused,
not represented as an independent economic model. No scientific output is
modified. Pointwise binary64 checks are not continuum/interval certificates.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[k]='1'
import sys,json,hashlib,time,platform,argparse,csv
from pathlib import Path
import numpy as np
import scipy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'replication/r8'))
from model import Model,old
SIGNS=('positive','nonpositive')

def serial(x):
    if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v) for v in x]
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    return x

def input_hashes():
    paths=['ECTA_R9.tex','SUPP_R9.tex','REVISION_INDEX.md',
      'replication/r4/solver.py','replication/r6/transport.py',
      'replication/r6/kernel_certificate.py','replication/r7/core.py',
      'replication/r8/numerical_core.py','replication/r8/model.py',
      'replication/r9/contracts.py']
    paths += [f'replication/r4/output/safe_policy_{s}.npz' for s in (101,202,303)]
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}

def actions(m,n):
    e=m.e[0];common=np.broadcast_to(e.menu,(m.ns,len(e.menu),3))
    return np.concatenate((common,e.extra[n].actions),axis=1) if e.extra else common

def solve(m,lam,d,fee=.85,term=1,mode='full'):
    """Own optimizer including action/sign/stop masks, not Model.class_pair."""
    ns,N=m.ns,m.steps;row=np.arange(ns)
    v=np.empty((N+1,ns));v[-1]=m.terminal
    policy=np.empty((N,ns),dtype=np.int32)
    for n in range(N-1,-1,-1):
        q=None
        for weight,e in zip((1-lam,lam),m.e):
            ks=[e.common]+([e.extra[n]] if e.extra else [])
            z=np.concatenate([k.base+d*k.duration-m.spec.cost*k.effort+k.continuation(v[n+1]) for k in ks],axis=1)
            q=weight*z if q is None else q+weight*z
        aa=actions(m,n);theta=aa[:,:,1];allowed=np.ones(theta.shape,dtype=bool)
        if mode=='zero':allowed &= np.abs(theta)<=1e-14
        elif mode=='up':allowed &= theta>=-1e-14
        elif mode=='down':allowed &= theta<=1e-14
        elif mode!='full':raise ValueError(mode)
        allowed=np.column_stack((allowed,(~m.e[0].boundary)&(n>=term)))
        raw=np.column_stack((q,m.terminal-fee));q=np.where(allowed,raw,-np.inf)
        policy[n]=q.argmax(axis=1);v[n]=q[row,policy[n]]
    pair={}
    for sign in SIGNS:
        mask=allowed.copy();mask[:,:-1] &= aa[:,:,2]>0 if sign=='positive' else aa[:,:,2]<=0
        q0=np.where(mask,raw,-np.inf);p=policy.copy();vv=v.copy()
        p[0]=q0.argmax(axis=1);vv[0]=q0[row,p[0]];pair[sign]={'value':vv,'policy':p}
    return pair

def replay(m,policy,lam,d,fee,term):
    """Selected-control transition replay without stored CSR rewards/kernels.
    Features: value, duration, surrender, signed theta, quadratic effort.
    """
    N,ns=m.steps,m.ns;s=m.e[0].states;out=np.zeros((5,N+1,ns));out[0,-1]=m.terminal
    for n in range(N-1,-1,-1):
        aa=actions(m,n);stop=policy[n]==aa.shape[1]
        assert not np.any(stop & (m.e[0].boundary | (n<term)))
        ctrl=aa[np.arange(ns),np.minimum(policy[n],aa.shape[1]-1)]
        for weight,e in zip((1-lam,lam),m.e):
            y,live,disc,flow,effort,_,alpha=old.transition(s,ctrl,1/N,e.model)
            ann=-np.expm1(-e.model.rho*alpha/N)/e.model.rho
            cont=[old.interpolate(out[j,n+1].reshape(e.shape),y) for j in range(5)]
            stage=[flow+d*ann,ann,np.zeros_like(ann),ann*ctrl[:,1,None],effort]
            for j in range(5):
                terminal=old.terminal(y) if j==0 else 0.
                val=np.mean(stage[j]+disc*np.where(live,cont[j],terminal),axis=-1)
                out[j,n,~stop]+=weight*val[~stop]
        out[:,n,stop]=0.;out[0,n,stop]=m.terminal[stop]-fee;out[2,n,stop]=1.
    return out

def record(m,pair,lam,d,fee,term,mode,cost=.01):
    g=float(m.terminal[m.center]);rows={};maxerr=0.
    for sign,z in pair.items():
        moments=replay(m,z['policy'],lam,d,fee,term)
        err=float(np.max(np.abs(moments[0]-z['value'])));maxerr=max(maxerr,err);assert err<2e-11,err
        val,dur,surr,theta,eff=map(float,moments[:,0,m.center]);grant=max(0.,g-val+cost)
        aa=actions(m,0);a=int(z['policy'][0,m.center])
        rows[sign]=dict(value=val,duration=dur,surrender=surr,signed_adjustment=theta,effort=eff,
          grant=grant,action=aa[m.center,a].tolist() if a<len(aa[0]) else 'stop',
          principal_surplus={str(b):b*dur-grant for b in (.9,1.)},replay_error=err)
    delta=rows['positive']['value']-rows['nonpositive']['value'];da=rows['positive']['duration']-rows['nonpositive']['duration']
    contrasts={str(b):rows['positive']['principal_surplus'][str(b)]-rows['nonpositive']['principal_surplus'][str(b)] for b in (.9,1.)}
    assert all(abs(contrasts[str(b)]-(delta+b*da))<2e-12 for b in (.9,1.))
    return dict(lam=lam,d=d,fee=fee,min_term=term,mode=mode,capacity_cost=cost,classes=rows,
      delta=delta,duration_difference=da,principal_contrast=contrasts,
      principal_switch_flow=(-delta/da if da!=0 else None),max_replay_error=maxerr)

def reachable_support(m):
    R=np.zeros((m.steps+1,m.ns),dtype=bool);R[0,m.center]=True
    for n in range(m.steps):
        for e in m.e:
            for k in [e.common]+([e.extra[n]] if e.extra else []):
                R[n+1] |= k.matrix.T@np.repeat(R[n].astype(float),k.na)>0
    rows=[]
    for n in range(m.steps+1):
        u=m.e[0].states[R[n],0]
        rows.append(dict(date=n,nodes=int(R[n].sum()),u_min=float(u.min()),u_max=float(u.max()),
          preference_boundary_nodes=int(np.sum(R[n] & ((m.e[0].states[:,0]<=1.2)|(m.e[0].states[:,0]>=2.8))))))
    return R,rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=HERE/'reviewer_results.json');args=ap.parse_args()
    before=input_hashes();start=time.perf_counter();m=Model();print('BUILT',m.build_seconds,m.nbytes,flush=True)
    R,reach=reachable_support(m);rows=[];center={}
    cases=[(lam,d,.85,1,.01) for lam in (0.,.125,.25) for d in (.4,.425,.45)]
    cases += [(.125,.425,.8,1,.01),(0.,.4,.8,1,.01),(.125,.425,0.,8,0.)]
    for lam,d,fee,term,cost in cases:
        for mode in ('full','zero'):
            pair=solve(m,lam,d,fee,term,mode);rec=record(m,pair,lam,d,fee,term,mode,cost);rows.append(rec)
            if (lam,d,fee,term)==(.125,.425,.85,1):center[mode]=pair
            print('CASE',lam,d,fee,term,mode,rec['delta'],rec['principal_contrast']['1.0'],flush=True)
    directional=[]
    for mode,comparison in (('up','full'),('down','zero')):
        pair=solve(m,.125,.425,.85,1,mode);rec=record(m,pair,.125,.425,.85,1,mode)
        rec['comparison']=comparison;rec['gaps']={}
        for sign in SIGNS:
            full=center[comparison][sign]['value'];rest=pair[sign]['value']
            gap=(full-rest) if mode=='up' else (rest-full)
            rec['gaps'][sign]=dict(initial=float(gap[0,m.center]),max_all_states_dates=float(gap.max()),max_all_action_reachable=float(gap[R].max()))
        directional.append(rec);print('DIRECTION',mode,rec['gaps'],flush=True)
    import importlib.util
    sp=importlib.util.spec_from_file_location('author_r9_contracts',ROOT/'replication/r9/contracts.py')
    module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module);parity={}
    for mode,adj in (('full',True),('zero',False)):
        author=module.Contract(m,.85,1).pair(.125,.425,adj)
        parity[mode]=max(float(np.max(np.abs(author[s]['value']-center[mode][s]['value']))) for s in SIGNS)
        assert parity[mode]<2e-11
    assert before==input_hashes(),'protected source changed'
    result=dict(reviewed_snapshot='30548ad06852cc0a447dedf1e63cc9e7f79f6c06',scientific_commit='8c1e0472279fb66a2419b63b3e35df028ecfdd78',
      archive_source_commit='755b507870b54a100616b0658eba9a031eef2833',
      scope='fresh independent orchestration with pinned author constructors; finite-array point diagnostics only',
      environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform()),
      source_sha256=before,rows=rows,directional=directional,reachability=reach,production_parity=parity,
      protected_hashes_unchanged=True,full_class_values_replayed=2*(len(rows)+len(directional)),
      max_replay_error=max(x['max_replay_error'] for x in rows+directional),kernel_bytes=m.nbytes,
      build_seconds=m.build_seconds,elapsed_seconds=time.perf_counter()-start,
      caveats=['Procurement contrasts enlarge the contract menu to allow class-specific grants and sign mandates.',
        'Principal flow b does not enter the agent Bellman reward and is distinct from d.',
        'No neural training, regional certificate sweep, constructor enclosure, or diffusion convergence run.',
        'No timing comparison, peak-memory claim, or full-grid directional theorem is made.'])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(serial(result),indent=2,allow_nan=False)+'\n')
    fields=['lambda','benefit','fee','term','mode','capacity_cost','W_plus','W_minus','A_plus','A_minus','S_plus','S_minus','q_plus','q_minus','principal_b1_plus','principal_b1_minus','agent_delta','principal_b1_delta','replay_error']
    with args.output.with_suffix('.csv').open('w',newline='') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(fields)
        for rec in rows+directional:
            a,b=rec['classes']['positive'],rec['classes']['nonpositive']
            writer.writerow([rec['lam'],rec['d'],rec['fee'],rec['min_term'],rec['mode'],rec['capacity_cost'],
              a['value'],b['value'],a['duration'],b['duration'],a['surrender'],b['surrender'],a['grant'],b['grant'],
              a['principal_surplus']['1.0'],b['principal_surplus']['1.0'],rec['delta'],rec['principal_contrast']['1.0'],rec['max_replay_error']])
    diag={k:v for k,v in result.items() if k not in ('rows','directional')}
    diag['directional']=[{k:v for k,v in rec.items() if k not in ('classes',)} for rec in directional]
    args.output.with_name('reviewer_diagnostics.json').write_text(json.dumps(serial(diag),indent=2,allow_nan=False)+'\n')
    print('DONE',result['full_class_values_replayed'],result['max_replay_error'],result['elapsed_seconds'],flush=True)
if __name__=='__main__':main()
