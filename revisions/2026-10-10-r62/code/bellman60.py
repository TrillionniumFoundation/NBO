"""All-state Bellman brackets in the unchanged two-state, two-date economy.

Continuous feasible actions are covered for the lower bound. Only whole-cell
feasible quantum actions construct the upper policy. No policy-value fit or
initial-law inference substitutes for this certificate.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time
import numpy as np
import search60 as u
n=u.n;I=n.I;R=Path(__file__).resolve().parents[1]
RUNGS=((8,8,4),(16,16,8),(32,32,16),(64,64,32))
TOLERANCES=(F(1,2),F(1,4),F(1,8),F(1,16))

class RangeTable:
    def __init__(self,values,maximum=False):
        values=np.asarray(values,dtype=float)
        if values.ndim!=2 or values.shape[0]!=values.shape[1] or not np.isfinite(values).all():raise ValueError('Square finite table required')
        self.n=len(values);self.op=np.maximum if maximum else np.minimum;self.tables={(0,0):values.copy()}
        self.level=self.n.bit_length()-1;self.logs=np.zeros(self.n+1,dtype=int)
        for k in range(2,self.n+1):self.logs[k]=self.logs[k//2]+1
        for p in range(self.level+1):
            if p:
                old=self.tables[p-1,0];step=1<<(p-1);self.tables[p,0]=self.op(old[:-step,:],old[step:,:])
            for q in range(1,self.level+1):
                old=self.tables[p,q-1];step=1<<(q-1);self.tables[p,q]=self.op(old[:,:-step],old[:,step:])
        self.bytes=sum(v.nbytes for v in self.tables.values())+self.logs.nbytes;self.queries=0
    def query(self,box):
        if np.any(box.lo<-1e-14) or np.any(box.hi>1+1e-14):raise AssertionError('Transition outside proven state domain')
        lo=np.clip(np.floor(box.lo*self.n).astype(int),0,self.n-1);hi=np.clip(np.floor(box.hi*self.n).astype(int),0,self.n-1)
        width=hi-lo+1;p=self.logs[width[:,0]];q=self.logs[width[:,1]];out=np.empty(len(lo));self.queries+=len(lo)
        for pp,qq in set(zip(p.tolist(),q.tolist())):
            ids=np.flatnonzero((p==pp)&(q==qq));ll=lo[ids];hh=hi[ids]-(np.array([1<<pp,1<<qq])-1)
            a=self.tables[pp,qq]
            out[ids]=self.op(self.op(a[ll[:,0],ll[:,1]],a[ll[:,0],hh[:,1]]),self.op(a[hh[:,0],ll[:,1]],a[hh[:,0],hh[:,1]]))
        return out

def boxes(N):
    ij=np.stack(np.meshgrid(np.arange(N),np.arange(N),indexing='ij'),axis=-1).reshape(-1,2)
    return I(ij/N,(ij+1)/N),ij

def qbound(x,a,q,table,lower):
    stage=n.s.costs(x,a,1)
    if table is None:return n.o.final_q(x,a,1)
    accum=I.point(np.zeros(len(a.lo)))
    for j in range(q):
        z=I(np.full(len(a.lo),-1/32+j/(16*q)),np.full(len(a.lo),-1/32+(j+1)/(16*q)))
        state=n.s.transition(x,a,z);endpoint=table.query(state);accum=accum+I.point(endpoint)
    return stage+n.s.c.rat_i(F(n.BETA))*accum/q

def rung(N,A,q):
    start=time.perf_counter();x,ij=boxes(N);M=N*N
    fullcap=n.s.cap(x).hi
    capindex=(4096*(2*N+ij.sum(axis=1)))//(16*N)
    low_next=up_next=None;lowers=[];uppers=[];policies=[];dates=[];storage=[]
    for t in (1,0):
        L=np.full(M,np.inf);U=np.full(M,np.inf);selected=np.zeros(M,dtype=np.uint16)
        for k in range(A):
            # Multiplication/division is outward, including the action cover.
            cell=n.I.point(fullcap);al=(cell*k/A).lo;ah=(cell*(k+1)/A).hi
            L=np.minimum(L,qbound(x,I(al,ah),q,low_next,True).lo)
        for k in range(A+1):
            ix=(capindex*k)//A;a=I.point(ix/4096)
            bound=qbound(x,a,q,up_next,False).hi;take=bound<U;U[take]=bound[take];selected[take]=ix[take]
        L=np.maximum(L,0.)
        if np.any(L>U) or np.any(selected>capindex):raise AssertionError('Invalid lower/upper Bellman bracket')
        gap=(I.point(U)-I.point(L)).hi
        dates.append(dict(date=t,gap_upper=float(gap.max()),continuous_cover_intervals=A,robust_candidates=A+1,lower_min=float(L.min()),upper_max=float(U.max())))
        lowers.insert(0,L);uppers.insert(0,U);policies.insert(0,selected)
        low_next=RangeTable(L.reshape(N,N));up_next=RangeTable(U.reshape(N,N),True);storage.append(low_next.bytes+up_next.bytes)
    return dict(N=N,A=A,q=q,dates=sorted(dates,key=lambda z:z['date']),initial_gap_upper=float((I.point(uppers[0])-I.point(lowers[0])).hi.max()),maximum_date_gap_upper=max(z['gap_upper'] for z in dates),table_bytes=max(storage),seconds=time.perf_counter()-start),dict(lower=np.array(lowers),upper=np.array(uppers),policy=np.array(policies),capindex=capindex)

def run(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False);rows=[];total=0.
    for N,A,q in RUNGS:
        start=time.perf_counter();r,raw=rung(N,A,q);file=folder/f'N{N}.npz';np.savez_compressed(file,**raw)
        r['raw_sha256']=u.digest(file);r['seconds_through_output']=time.perf_counter()-start;total+=r['seconds_through_output'];r['cumulative_seconds']=total;rows.append(r)
    targets=[]
    for tol in TOLERANCES:
        match=next((r for r in rows if F(r['maximum_date_gap_upper'])<=tol),None)
        targets.append(dict(tolerance=str(tol),status='attained' if match else 'budget_exhausted',N=match['N'] if match else None,work_seconds=match['cumulative_seconds'] if match else total,bound=match['maximum_date_gap_upper'] if match else rows[-1]['maximum_date_gap_upper']))
    result=dict(status='passed',state_dimension=2,action_dimension=1,horizon=2,primitive_laws='unchanged original investment model',rungs=rows,targets=targets,scope='Constructive interval Bellman comparator; not a neural-only speed or high-dimensional guarantee. These are all-state continuous-action optimality bounds, not initial-law gains. Cumulative work includes all preceding rungs and serialized arrays.')
    (folder/'summary.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return result
