"""Lossless mixed-arithmetic search for the original fitted NBO action objective.

Outward intervals can reject lattice points, never choose an approximate
minimizer. Exact rational comparison preserves the smallest-index tie rule.
The inherited algebraic solver is the declared overflow/large-lattice fallback.
"""
from __future__ import annotations
from fractions import Fraction as F
import hashlib
import numpy as np
import action57 as a
n=a.n
MAX_LATTICE=2049


def positive(v):
    return n.I(np.maximum(v.lo,0.),np.maximum(v.hi,0.))


def simplify(reduced,cap):
    """Eliminate ridges contained in one exact activation region on [0,cap]."""
    q1,q2,features,squares,value=reduced
    offset=F(0);active=[];active_sq=[]
    for w,z,s,r in features:
        lo,hi=sorted((z,z+s*cap))
        if hi<=-r:continue
        if lo>=r:
            offset+=w*z;q1+=w*s
        elif r and lo>=-r and hi<=r:
            offset+=w*(z+r)**2/(4*r)
            q1+=w*(z+r)*s/(2*r);q2+=w*s*s/(4*r)
        else:active.append((w,z,s,r))
    for w,z,s in squares:
        lo,hi=sorted((z,z+s*cap))
        if hi<=0:continue
        if lo>=0:
            offset+=w*z*z;q1+=2*w*z*s;q2+=w*s*s
        else:active_sq.append((w,z,s))
    return (q1,q2,active,active_sq,value),offset


def endpoints(reduced,capindex,quantum):
    q1,q2,features,squares,_=reduced
    # Integer indices are exact. Division and rational conversion are outward.
    x=n.I.point(np.arange(capindex+1,dtype=float))/n.s.c.rat_i(F(quantum))
    val=n.s.c.rat_i(q1)*x+n.s.c.rat_i(q2)*x.square()+4*x.square().square()
    # No unrounded BLAS dot product or floating sum supplies an endpoint.
    for group in ([f for f in features if f[3]==0],[f for f in features if f[3]>0]):
        if not group:continue
        def col(j):
            v=n.s.c.array_i([f[j] for f in group])
            return n.I(v.lo[:,None],v.hi[:,None])
        xi=n.I(x.lo[None,:],x.hi[None,:]);z_i=col(1)+col(2)*xi
        if group[0][3]==0:h=positive(z_i)
        else:
            ri=col(3)
            h=(positive(z_i+ri).square()-positive(z_i-ri).square())/(4*ri)
        terms=col(0)*h
        while len(terms.lo)>1:
            m=len(terms.lo)//2
            paired=n.I(terms.lo[:2*m:2],terms.hi[:2*m:2])+n.I(terms.lo[1:2*m:2],terms.hi[1:2*m:2])
            if len(terms.lo)%2:
                terms=n.I(np.concatenate((paired.lo,terms.lo[-1:])),np.concatenate((paired.hi,terms.hi[-1:])))
            else:terms=paired
        val=val+n.I(terms.lo[0],terms.hi[0])
    for w,z,s in squares:
        val=val+n.s.c.rat_i(w)*positive(n.s.c.rat_i(z)+n.s.c.rat_i(s)*x).square()
    return val


def survivors(lo,hi):
    lo=np.asarray(lo,dtype=float);hi=np.asarray(hi,dtype=float)
    if lo.ndim!=1 or not len(lo) or lo.shape!=hi.shape or not np.all(np.isfinite(lo)) or not np.all(np.isfinite(hi)) or np.any(lo>hi):
        raise ValueError('Expected finite ordered scalar-objective enclosures')
    cutoff=float(hi.min());keep=np.flatnonzero(lo<=cutoff)
    if not len(keep):raise AssertionError('Valid interval screen cannot be empty')
    return keep,cutoff


def minimize(state,critic,capindex,quantum=4096):
    if not isinstance(capindex,(int,np.integer)) or not isinstance(quantum,(int,np.integer)) or quantum<=0 or not 0<=capindex<=quantum//4:
        raise ValueError('Expected an integer feasible action lattice')
    capindex=int(capindex);quantum=int(quantum)
    if capindex+1>MAX_LATTICE:
        out=a.minimize(state,critic,capindex,quantum)
        out.update(solver='algebraic-fallback',fallback_reason='lattice-limit',screened_points=0,retained_points=len(out['candidate_indices']),endpoint_sha256=None)
        return out
    original=a.reduce_objective(state,critic);reduced,offset=simplify(original,F(capindex,quantum))
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise',under='ignore'):
            val=endpoints(reduced,capindex,quantum);keep,cutoff=survivors(val.lo,val.hi)
    except (ArithmeticError,ValueError,OverflowError) as exc:
        out=a.minimize(state,critic,capindex,quantum)
        out.update(solver='algebraic-fallback',fallback_reason=type(exc).__name__,screened_points=0,retained_points=len(out['candidate_indices']),endpoint_sha256=None)
        return out
    value=reduced[-1];indices=list(map(int,keep));scores={k:value(F(k,quantum)) for k in indices}
    best=min(indices,key=lambda k:(scores[k],k));exact=scores[best]
    if not F(float(val.lo[best]))<=exact-offset<=F(float(val.hi[best])):
        raise AssertionError('Exact survivor evaluation outside its interval')
    return dict(index=best,objective_exact=str(exact),candidate_indices=indices,
        pieces=0,isolated_roots=0,lattice_size=capindex+1,solver='interval-screen-exact',
        screened_points=capindex+1,retained_points=len(indices),cutoff_upper=cutoff,
        offset_exact=str(offset),active_ridges=len(reduced[2]),eliminated_ridges=len(original[2])-len(reduced[2]),
        max_endpoint_width=float(val.width().max()),endpoint_sha256=hashlib.sha256(val.lo.tobytes()+val.hi.tobytes()).hexdigest(),fallback_reason=None)


def proposals(critics,part,solver):
    if solver not in ('algebraic','screened'):raise ValueError(solver)
    grid=n.propose(critics,part);exact=grid.copy();records=[]
    for t in range(len(critics)-1):
        for k in range(len(part.lo)):
            fn=a.minimize if solver=='algebraic' or t==len(critics)-2 else minimize
            r=fn(part.centers[k],critics[t+1],int(part.capindex[k]));exact[t,k]=r['index']
            r.update(date=t,leaf=k,grid_index=int(grid[t,k]),common_terminal=t==len(critics)-2)
            if r['common_terminal']:grid[t,k]=exact[t,k]
            records.append(r)
    return grid,exact,records
