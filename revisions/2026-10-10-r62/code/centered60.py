"""Reference-shifted all-state Bellman brackets in the original d=2,T=2 law.

Adds a separately frozen constructive improvement after the uncentered R60
frontier was observed. Old results and scientific sources are unchanged.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time
import numpy as np
import bellman60 as base
import directed53 as d
import search60 as u
n=u.n;I=n.I;R=u.R
RUNGS=((8,8,4),(16,16,8),(32,32,16),(64,64,32),(128,64,32))
TOLERANCES=(F(1,2),F(1,4),F(1,8),F(1,16),F(1,32))

def save(path,v):path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def freeze():
    import services60
    path=R/'audit/SOURCE_FREEZE60C.json';parent=services60.verify()
    if path.exists():return verify()
    files=('code/centered60.py','code/tests_centered60.py','CENTERED_BELLMAN_AMENDMENT60.md')
    save(path,dict(parent_freeze_sha256=parent,files_sha256={name:u.digest(R/name) for name in files},utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),scope='Centered design frozen after the original uncentered bounds were observed and before any centered production rung. Disjoint correctness fixtures are separate.'))
    return u.digest(path)
def verify():
    import services60
    path=R/'audit/SOURCE_FREEZE60C.json';v=json.loads(path.read_text())
    if services60.verify()!=v['parent_freeze_sha256']:raise AssertionError('Original R60 freeze changed')
    for name,h in v['files_sha256'].items():
        if u.digest(R/name)!=h:raise AssertionError('Centered scientific source changed: '+name)
    return u.digest(path)

def advantage_and_offset(x,a,t,q,table=None):
    N=len(a.lo);zero=I.point(np.zeros(N));same=(a.lo==0)&(a.hi==0)
    if t==1:
        out=n.o.final_difference(x,a,zero,1)
        out.lo[same]=out.hi[same]=0.;return out
    xx=n.o.deterministic_next(x,a);yy=n.o.deterministic_next(x,zero)
    delta=n.s.stack([a*F(1,2),a*F(1,4)])
    accum=I.point(np.zeros(N))
    for j in range(q):
        shock=I(np.full(N,-1/32+j/(16*q)),np.full(N,-1/32+(j+1)/(16*q)))
        noise=n.s.stack([shock,-shock]);xa=xx+noise;yb=yy+noise
        pair=d.last_pair(xa,yb,delta,zero,zero,1)
        pair.lo[same]=pair.hi[same]=0.
        if table is not None:pair=pair+I.point(table.query(xa))
        accum=accum+pair
    return d.action_difference(a,zero,1)+n.s.c.rat_i(F(n.BETA))*accum/q

def rung(N,A,q):
    start=time.perf_counter();x,ij=base.boxes(N);M=N*N
    capindex=(4096*(2*N+ij.sum(axis=1)))//(16*N)
    fullcap=(2*N+ij.sum(axis=1)+2)/(16*N)
    next_lower=next_upper=None;lower=[];upper=[];policy=[];dates=[];tablebytes=0
    for t in (1,0):
        L=np.full(M,np.inf);U=np.full(M,np.inf);selected=np.zeros(M,dtype=np.uint16)
        for k in range(A):
            # All quantities are exact dyadics for the declared ladder.
            a=I(fullcap*k/A,fullcap*(k+1)/A)
            val=advantage_and_offset(x,a,t,q,next_lower);L=np.minimum(L,val.lo)
        for k in range(A+1):
            ix=(capindex*k)//A;val=advantage_and_offset(x,I.point(ix/4096),t,q,next_upper)
            bound=val.hi
            if k==0:
                # The reference zero action followed by an already certified
                # nonworsening continuation cannot have positive true excess.
                bound=np.minimum(bound,0.)
            take=bound<U;U[take]=bound[take];selected[take]=ix[take]
        if np.any(L>U) or np.any(U>0) or np.any(selected>capindex):raise AssertionError('Invalid centered Bellman bracket')
        gap=(I.point(U)-I.point(L)).hi
        dates.append(dict(date=t,gap_upper=float(gap.max()),lower_excess_min=float(L.min()),upper_excess_max=float(U.max()),continuous_cover_intervals=A,robust_candidates=A+1))
        lower.insert(0,L);upper.insert(0,U);policy.insert(0,selected)
        next_lower=base.RangeTable(L.reshape(N,N));next_upper=base.RangeTable(U.reshape(N,N),True)
        tablebytes=max(tablebytes,next_lower.bytes+next_upper.bytes)
    return dict(N=N,A=A,q=q,dates=sorted(dates,key=lambda r:r['date']),maximum_date_gap_upper=max(r['gap_upper'] for r in dates),initial_gap_upper=float((I.point(upper[0])-I.point(lower[0])).hi.max()),table_bytes=tablebytes,seconds=time.perf_counter()-start),dict(lower_excess=np.array(lower),upper_excess=np.array(upper),policy=np.array(policy),capindex=capindex)

def run():
    import stress60
    fz=verify();folder=R/'results60-centered';folder.mkdir(parents=True,exist_ok=False);env=stress60.environment();rows=[];total=0.
    for N,A,q in RUNGS:
        start=time.perf_counter();r,arrays=rung(N,A,q);path=folder/f'N{N}.npz';np.savez_compressed(path,**arrays)
        r['raw_sha256']=u.digest(path);r['seconds_through_output']=time.perf_counter()-start;total+=r['seconds_through_output'];r['cumulative_seconds']=total;rows.append(r)
        save(folder/f'N{N}.json',r);print(json.dumps(r),flush=True)
    targets=[]
    for tol in TOLERANCES:
        hit=next((r for r in rows if F(r['maximum_date_gap_upper'])<=tol),None)
        targets.append(dict(tolerance=str(tol),status='attained' if hit else 'budget_exhausted',N=hit['N'] if hit else None,bound=hit['maximum_date_gap_upper'] if hit else rows[-1]['maximum_date_gap_upper'],cumulative_seconds=hit['cumulative_seconds'] if hit else total))
    result=dict(status='executed',source_freeze_sha256=fz,environment=env,rows=rows,targets=targets,primitive_laws='Unchanged original two-state, two-date investment model',scope='Bounds are excess values relative to the same exact zero-policy reference. The reference itself is not fitted or queried as an oracle; signed primitive differences suffice. Original uncentered frontier retained. Single-host measured timing; no new policy-cost samples.')
    save(folder/'summary.json',result);print(json.dumps(result,indent=2),flush=True)
    return result
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');a=p.parse_args()
    if a.freeze:print(freeze())
    else:run()
