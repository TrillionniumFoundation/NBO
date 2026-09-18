#!/usr/bin/env python3
"""Independent Bellman orchestration on pinned author-constructed finite arrays.
Nine-point tests are NOT continuum certificates. No neural retraining, real-
arithmetic constructor enclosure, or diffusion-error estimate is performed.
Run: python reviews/2026-09-18-econometrica-r9-r10-independent-harsh/reviewer_audit.py
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import hashlib,json,platform,sys,time
from pathlib import Path
import numpy as np
import scipy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'replication/r9'))
from contracts import Model,Specification,Contract,FirstDateMenu
TOL=2e-11

def hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in ROOT.rglob('*') if p.is_file() and HERE not in p.parents
        and '__pycache__' not in p.parts and '.git' not in p.parts}

def serial(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v) for v in x]
    return x

def save(x):
    (HERE/'reviewer_results.json').write_text(json.dumps(serial(x),indent=2,allow_nan=False)+'\n')

def actions(m,n):
    e=m.e[0];a=np.broadcast_to(e.menu,(m.ns,len(e.menu),3))
    return np.concatenate((a,e.extra[n].actions),axis=1) if e.extra else a

def solve(m,lam,d,mode='full',fee=0.,term=8):
    """New recursion/masks; shared rewards and transitions, no author solver."""
    rows=np.arange(m.ns);v=np.empty((m.steps+1,m.ns));v[-1]=m.terminal
    p=np.empty((m.steps,m.ns),dtype=np.int32)
    for n in range(m.steps-1,-1,-1):
        a=actions(m,n);theta=a[:,:,1]
        if mode=='full':ok=np.ones(theta.shape,bool)
        elif mode=='up':ok=theta>=-1e-14
        elif mode=='down':ok=theta<=1e-14
        elif mode=='none':ok=np.abs(theta)<=1e-14
        else:raise ValueError(mode)
        q=(1-lam)*m.q(0,n,v[n+1],d)+lam*m.q(1,n,v[n+1],d)
        stop=(~m.e[0].boundary)&(n>=term)
        q=np.column_stack((q,m.terminal-fee));ok=np.column_stack((ok,stop))
        q[~ok]=-np.inf;p[n]=q.argmax(1);v[n]=q[rows,p[n]]
    out={}
    for s in ('positive','nonpositive'):
        sm=a[:,:,2]>0 if s=='positive' else a[:,:,2]<=0
        qq=np.where(np.column_stack((sm,stop)),q,-np.inf)
        vv,pp=v.copy(),p.copy();pp[0]=qq.argmax(1);vv[0]=qq[rows,pp[0]]
        out[s]={'value':vv,'policy':pp}
    return out

def summary(m,z):
    out={s:float(y['value'][0,m.center]) for s,y in z.items()}
    out['delta']=out['positive']-out['nonpositive']
    return out

def main():
    start=time.perf_counter();before=hashes();m=Model(Specification())
    result={'reviewed_snapshot':'10248e4a7e5d6668bf82de7d3b146f46bb10ad8f',
        'archive_source':'755b507870b54a100616b0658eba9a031eef2833',
        'scientific_source':'8c1e0472279fb66a2419b63b3e35df028ecfdd78',
        'scope':'Nine-point directional and selected joint-contract finite-array diagnostics, not regional proofs.',
        'environment':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
            'platform':platform.platform(),'kernel_payload_bytes':m.nbytes,'states':m.ns,
            'dates':m.steps,'operating_actions':1568},'directional':[],'joint_contract':[],'checks':{}}
    print('Constructor completed',round(time.perf_counter()-start,3),flush=True)
    resume=HERE/'reviewer_results.json'
    if '--resume' in sys.argv and resume.exists():
        old=json.loads(resume.read_text())
        result['directional']=old['directional'];result['joint_contract']=old['joint_contract']
        result['resumed_completed_checkpoints']={'directional':len(old['directional']),'joint_contract':len(old['joint_contract'])}
    replay=0.
    for lam in (0.,.125,.25):
        for d in (.4,.425,.45):
            if any(x['lambda']==lam and x['benefit']==d for x in result['directional']):continue
            sol={mode:solve(m,lam,d,mode) for mode in ('full','up','down','none')}
            item={'lambda':lam,'benefit':d,'modes':{mode:summary(m,z) for mode,z in sol.items()}}
            item['initial_full_minus_up_max']=max(abs(item['modes']['full'][s]-item['modes']['up'][s]) for s in sol['full'])
            item['initial_down_minus_none_max']=max(abs(item['modes']['down'][s]-item['modes']['none'][s]) for s in sol['full'])
            item['global_full_minus_up_max']=max(float(np.max(sol['full'][s]['value']-sol['up'][s]['value'])) for s in sol['full'])
            item['global_down_minus_none_max']=max(float(np.max(sol['down'][s]['value']-sol['none'][s]['value'])) for s in sol['full'])
            for mode,z in sol.items():
                item['modes'][mode]['first_controls']={s:actions(m,0)[m.center,y['policy'][0,m.center]].tolist() for s,y in z.items()}
            if (lam,d)==(.125,.425):
                for mode,adj in (('full',True),('none',False)):
                    az=Contract(m,fee=0.,min_term=8).pair(lam,d,adj)
                    for s in az:
                        replay=max(replay,float(np.max(abs(az[s]['value']-sol[mode][s]['value']))))
                        direct=m.direct(sol[mode][s]['policy'],lam,d)
                        replay=max(replay,float(np.max(abs(direct-sol[mode][s]['value']))))
            result['directional'].append(item);save(result)
            print('Directional',lam,d,'initial gaps',item['initial_full_minus_up_max'],item['initial_down_minus_none_max'],flush=True)
    menu=FirstDateMenu(m)
    for lam,d,fee in ((.125,.425,.8),(.125,.425,.85),(0.,.4,.8),(0.,.4,.85)):
        if any(x['lambda']==lam and x['benefit']==d and x['fee']==fee for x in result['joint_contract']):continue
        row={'lambda':lam,'benefit':d,'fee':fee,'minimum_term':1,'regimes':{}}
        for mode,adj in (('full',True),('none',False)):
            z=solve(m,lam,d,mode,fee,1);c=Contract(m,fee=fee,min_term=1);az=c.pair(lam,d,adj)
            for s in z:replay=max(replay,float(np.max(abs(z[s]['value']-az[s]['value']))))
            moments={s:c.moments(y['policy'],lam) for s,y in z.items()}
            entry={'baseline':summary(m,z),'discounted_surrender':{s:float(y[2,0,m.center]) for s,y in moments.items()},'permissions':[]}
            for L,S in ((.8,.5),(.82,.5),(.8,.51)):
                v=menu.optimize(z['positive']['value'][1],lam,d,adj,L,S)
                entry['permissions'].append({'long':L,'short':S,'delta':v['positive']['value']-v['nonpositive']['value'],
                    'positive_action':v['positive']['action'],'nonpositive_action':v['nonpositive']['action']})
            row['regimes'][mode]=entry
        result['joint_contract'].append(row);save(result)
        print('Joint-contract',lam,d,fee,flush=True)
    # Recheck the focal recursions after resumption; do not infer validation
    # status from an interrupted process's unrecorded local variables.
    zz={mode:solve(m,.125,.425,mode) for mode in ('full','up','down','none')}
    result['global_gap_witnesses']=[]
    for a,b in (('full','up'),('down','none')):
        witnesses=[]
        for sign in zz[a]:
            diff=zz[a][sign]['value']-zz[b][sign]['value']
            n,state=np.unravel_index(np.argmax(diff),diff.shape)
            witnesses.append({'comparison':a+' minus '+b,'sign':sign,'date':int(n),
                'state':m.e[0].states[state].tolist(),'gap':float(diff[n,state])})
        result['global_gap_witnesses'].append(max(witnesses,key=lambda x:x['gap']))
    for mode,adj in (('full',True),('none',False)):
        author=Contract(m,fee=0.,min_term=8).pair(.125,.425,adj)
        for sign in author:
            replay=max(replay,float(np.max(abs(author[sign]['value']-zz[mode][sign]['value']))))
            replay=max(replay,float(np.max(abs(m.direct(zz[mode][sign]['policy'],.125,.425)-zz[mode][sign]['value']))))
    # Validate every completed joint-contract checkpoint, including those
    # saved by an earlier interrupted invocation. This makes the recorded
    # replay maximum independent of which checkpoint was resumed.
    for row in result['joint_contract']:
        lam,d,fee=row['lambda'],row['benefit'],row['fee']
        for mode,adj in (('full',True),('none',False)):
            z=solve(m,lam,d,mode,fee,1)
            author=Contract(m,fee=fee,min_term=1).pair(lam,d,adj)
            for sign in z:
                replay=max(replay,float(np.max(abs(z[sign]['value']-author[sign]['value']))))
                replay=max(replay,abs(float(z[sign]['value'][0,m.center])-row['regimes'][mode]['baseline'][sign]))
    assert len(result['directional'])==9 and len(result['joint_contract'])==4
    result['flow_derivative_check']={'consumption':.8,'preference_interval':[1.2,2.8],
        'minimum_numerator':float(1+1.8*np.log(.8)),
        'interpretation':'Positive current CRRA cardinal derivative at selected consumption, not a dynamic continuation theorem.'}
    result['checks']={'production_or_selected_control_max_abs_error':replay,
        'nine_points_initial_up_matches_full':all(x['initial_full_minus_up_max']<TOL for x in result['directional']),
        'nine_points_initial_down_matches_none':all(x['initial_down_minus_none_max']<TOL for x in result['directional']),
        'preexisting_input_files_checked':len(before)}
    after=hashes();changed=[p for p,h in before.items() if after.get(p)!=h]
    result['checks']['preexisting_input_files_changed']=changed
    result['elapsed_seconds']=time.perf_counter()-start
    result['elapsed_scope']='Current invocation only; resumed runs are not end-to-end timings.'
    assert replay<TOL,replay
    assert not changed,changed
    result['execution_completed']=True;save(result)
    print('Completed',round(result['elapsed_seconds'],3),'replay',replay,flush=True)

if __name__=='__main__':main()
