"""R117 paid initial-precision search; original primitives and targets unchanged.

Only proposal/certificate scheduling changes. No evaluation is free or cached.
The final tail is the frozen compiled service, from its already-paid proposal.
"""
from __future__ import annotations
from pathlib import Path
import sys,time,resource
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'frozen108/code108'))
import campaign108 as base
from interval94 import up
from investment94 import COUNTS,count
q,c,kern,rep=base.q,base.c,base.kern,base.rep
KEYS=base.KEYS


def finish(x,alpha,proposed,record,attempts,indices):
    """Finish unresolved proposals, under an already installed backend."""
    actions=proposed.copy();n=len(x)
    rec={key:np.array(record[key],copy=True) for key in KEYS}
    rejected=~q.qualifies(rec);used=np.full(n,128,int);exact=np.zeros(n,bool)
    def log(kind,mask,bins,fresh):
        for p,j in enumerate(np.flatnonzero(mask)):
            attempts.append(dict(row=int(indices[j]),kind=kind,bins=bins,
                action=float(actions[j]),qualified=bool(q.qualifies(fresh)[p]),
                **{key:float(fresh[key][p]) for key in KEYS}))
    if np.any(rejected):
        actions[rejected]=c.actor(x[rejected],alpha,None)
        fresh=q.certificate(x[rejected],actions[rejected],alpha)
        for key in KEYS:rec[key][rejected]=fresh[key]
        count('completed_conventional_fallback_rows',int(rejected.sum()))
        log('online-repair',rejected,128,fresh)
    for bins in (256,512,1024,2048,4096):
        bad=~q.qualifies(rec)
        if not np.any(bad):break
        fresh=q.certificate(x[bad],actions[bad],alpha,bins)
        for key in KEYS:rec[key][bad]=fresh[key]
        used[bad]=bins;log('refinement',bad,bins,fresh)
    for j in np.flatnonzero(~q.qualifies(rec)):
        from rational96 import exact_service
        a,lo,hi,opt,bins=exact_service(x[j],alpha)
        actions[j]=a;rec['lower'][j]=lo;rec['upper'][j]=hi
        rec['optimum_lower'][j]=opt;rec['loss'][j]=up(hi-opt);rec['width'][j]=up(hi-lo)
        used[j]=bins;exact[j]=True
        attempts.append(dict(row=int(indices[j]),kind='rational-fallback',bins=int(bins),
            action=float(a),qualified=bool(q.qualifies(rec)[j]),
            **{key:float(rec[key][j]) for key in KEYS}))
    if not np.all(q.qualifies(rec)):raise ArithmeticError('Original qualification failed closed')
    return actions,rec,rejected,used,exact


def service(x,alpha,model,ladder=True):
    x=np.asarray(x,dtype=float)
    if x.ndim!=2 or x.shape[1]!=2 or len(x)==0 or not np.all(np.isfinite(x)):
        raise ValueError('A nonempty finite d=2 catalogue is required')
    before=COUNTS.copy();start=time.perf_counter();attempts=[]
    n=len(x);rec={key:np.empty(n) for key in KEYS};first={key:np.empty(n) for key in KEYS}
    resolved=np.zeros(n,bool);used=np.zeros(n,int);initial_bins=np.zeros(n,int)
    rejected=np.zeros(n,bool);exact=np.zeros(n,bool)
    with kern.backend(True):
        t=time.perf_counter();proposed=rep.proposal(x,alpha,model)
        proposal_seconds=time.perf_counter()-t;actions=proposed.copy()
        for bins in ((8,16,32,64,128) if ladder else (128,)):
            ids=np.flatnonzero(~resolved)
            if len(ids)==0:break
            fresh=q.certificate(x[ids],proposed[ids],alpha,bins)
            ok=q.qualifies(fresh)
            if bins==(8 if ladder else 128):
                for key in KEYS:first[key][:]=fresh[key]
            for p,j in enumerate(ids):
                attempts.append(dict(row=int(j),kind='initial',bins=bins,
                    action=float(proposed[j]),qualified=bool(ok[p]),
                    **{key:float(fresh[key][p]) for key in KEYS}))
            for key in KEYS:rec[key][ids]=fresh[key]
            used[ids]=bins;initial_bins[ids]=bins
            resolved[ids[ok]]=True
            if bins==128:
                aa,tail,rr,uu,ee=finish(x[ids],alpha,proposed[ids],fresh,attempts,ids)
                actions[ids]=aa;rejected[ids]=rr;used[ids]=uu;exact[ids]=ee
                for key in KEYS:rec[key][ids]=tail[key]
                resolved[ids]=True
        if not np.all(resolved) or not np.all(q.qualifies(rec)):
            raise ArithmeticError('Incomplete original-policy service')
    rows=[]
    for j,xx in enumerate(x):
        rows.append(dict(row=j,x0=float(xx[0]),x1=float(xx[1]),proposed=float(proposed[j]),
            action=float(actions[j]),first_rejected=bool(rejected[j]),
            first_resolution=int(initial_bins[j]),bins=int(used[j]),exact_fallback=bool(exact[j]),
            action_distance_upper=float(up(np.sqrt(rec['loss'][j]))),
            **{key:float(rec[key][j]) for key in KEYS},
            **{'first_'+key:float(first[key][j]) for key in KEYS}))
    return dict(rows=rows,attempts=attempts,counts=base.counter_delta(before),
        seconds=time.perf_counter()-start,proposal_seconds=proposal_seconds,
        max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        terminal_policy_unchanged=True,cache_used=False)
