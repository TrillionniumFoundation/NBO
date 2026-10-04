"""Outward curvature and complete scalar-intervention accuracy accounts.

The state may be high dimensional. The competitor class here is exactly
a(s)=a_left+s*(a_right-a_left), 0<=s<=1, followed by the common reference.
These are finite-period Bellman guarantees, not continuum HJB error bounds.
No fitted model, rollout sample, or empirical derivative maximum is used.
"""
from pathlib import Path
import hashlib
import math
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r15/code'))
import costate_bridge as bridge
I,pc,tc=bridge.I,bridge.pc,bridge.tc
sqrt=bridge.isqrt
upper=bridge.iu


FIXED_SPECTRAL_PROPOSALS={
    '4e12db288a7dd1c54839b4c8771285159e0665ec39b049f04b7b88befcb40743':2.566221237182617,
    '6ab6f5e446d7c83d52f0651fd5b6042cccd2f6f4580556b6b7179f8ed152e010':3.7256059646606445,
}


def deterministic_spectral_bound(B):
    """Fresh outward LDL at a pre-data dyadic proposal, without a BLAS SVD.

    The two frozen capital matrices use SHA-bound dyadic proposals. Unknown
    matrices use a deterministic Gershgorin power-of-two proposal instead.
    Every returned proposal must pass the full interval Schur recurrence.
    This prevents hardware-dependent SVD last bits from changing a replayed
    economic account; no historical certificate implementation is modified.
    """
    B=np.asarray(B,dtype=np.float64)
    if B.ndim!=2 or B.shape[0]!=B.shape[1] or not np.isfinite(B).all():
        raise ValueError('a finite square economic matrix is required')
    d=len(B);digest=hashlib.sha256(B.tobytes(order='C')).hexdigest()
    gram=I(np.zeros((d,d)))
    for row in B:gram=gram+I(row[:,None])*I(row[None,:])
    if digest in FIXED_SPECTRAL_PROPOSALS:
        proposal=FIXED_SPECTRAL_PROPOSALS[digest]
        origin='fixed pre-data dyadic proposal for the exact frozen matrix SHA-256'
    else:
        gersh=float(pc.sum_axis(I(gram.absmax()),axis=1).hi.max())
        if not math.isfinite(gersh):raise ArithmeticError('nonfinite spectral majorant')
        proposal=1.
        while proposal<=gersh:proposal*=2
        origin='deterministic outward Gershgorin power-of-two proposal for an unknown matrix'
    attempts=[]
    for _ in range(8):
        A=I(proposal)*I(np.eye(d))-gram;pivots=[];accepted=True
        for k in range(d):
            pivot=I(A.lo[k,k],A.hi[k,k]);pivots.append([float(pivot.lo),float(pivot.hi)])
            if pivot.lo<=0:accepted=False;break
            if k+1<d:
                v=I(A.lo[k+1:,k],A.hi[k+1:,k])/pivot
                block=I(A.lo[k+1:,k+1:],A.hi[k+1:,k+1:])-pivot*I(v.lo[:,None],v.hi[:,None])*I(v.lo[None,:],v.hi[None,:])
                A.lo[k+1:,k+1:]=block.lo;A.hi[k+1:,k+1:]=block.hi
        attempts.append(dict(lambda_candidate=proposal,positive_pivots=accepted,pivots=pivots))
        if accepted:
            return dict(dimension=d,lambda_upper=proposal,norm_upper=upper(sqrt(I(proposal))),
                attempts=attempts,matrix_sha256=digest,proposal_source=origin,
                independent_outward_LDL=True,no_floating_SVD_or_empirical_derivative_maximum=True)
        proposal*=2
    raise ArithmeticError('unable to prove a deterministic spectral majorant')


def model_constants(economy):
    B=np.asarray(economy.B,dtype=np.float64)
    proof=deterministic_spectral_bound(B)
    b=I(proof['norm_upper']); kappa=I(economy.p['coupling'])
    L2=4/(3*sqrt(I(3.)))
    rows=sqrt(pc.sum_axis(I(B).square(),axis=1))
    gram=I(np.zeros_like(B))
    for j in range(len(B)):
        gram=gram+I(B[:,j,None])*I(B[None,:,j])
    positive=pc.sum_axis(pc.sum_axis(I(np.maximum(gram.hi,0.)),axis=1))
    bp=I(min(upper(kappa*b),upper(kappa*sqrt(positive/len(B)))))
    return dict(spectral=proof,b=b,beta=kappa*b,beta_production=bp,
        scalar_hessian=kappa*L2*b.square(),
        vector_hessian=kappa*L2*b*I(float(rows.hi.max()))*sqrt(I(len(B))))


def post_interval(economy,y,action):
    y=np.atleast_2d(np.asarray(y,dtype=np.float64))
    action=np.broadcast_to(np.asarray(action,dtype=np.float64),y.shape)
    return I(y)+I(economy.h)*(I(economy.c0)+I(economy.p['coupling'])*
        bridge.tanh_interval(bridge.imat(I(y),economy.B))-I(action))


def scalar_curvature(economy,y,a_left,a_right,*,utility_weight=1.,adjustment=None):
    """Global bounds for the entire scalar segment, parameterized by [0,1]."""
    y=np.asarray(y,dtype=np.float64).reshape(-1)
    left=np.asarray(a_left,dtype=np.float64).reshape(-1)
    right=np.asarray(a_right,dtype=np.float64).reshape(-1)
    if y.shape!=left.shape or y.shape!=right.shape or len(y)!=economy.dimension:
        raise ValueError('one complete fixed query and two action endpoints required')
    if not (np.isfinite(y).all() and np.isfinite(left).all() and np.isfinite(right).all()):
        raise ValueError('nonfinite scalar intervention')
    if min(left.min(),right.min())<=0 or utility_weight<=0:
        raise ValueError('positive actions and current utility weight required')
    eta=economy.p['adjustment'] if adjustment is None else float(adjustment)
    if eta<0: raise ValueError('negative current adjustment curvature')
    c=model_constants(economy); h=I(economy.h); d=economy.dimension
    direction=I(right)-I(left)
    R=sqrt(pc.mean_i(direction.square()))
    V=h*R; W=I(0.); production=I(0.)
    for j in range(1,economy.steps):
        production=production+I(economy.W[j])*(c['scalar_hessian']*V.square()+c['beta_production']*W)
        nextW=(1+h*c['beta'])*W+h*c['vector_hessian']*V.square()
        V=(1+h*c['beta'])*V
        W=nextW
    xleft=post_interval(economy,y,left); xright=post_interval(economy,y,right)
    def spread(x):
        return float(bridge.norm_upper(x-bridge.column(pc.mean_i(x,axis=1)))[0])
    xspread=max(spread(xleft),spread(xright))
    noise_i=float(getattr(economy,'noise_i',economy.p['idiosyncratic_sigma']*math.sqrt(economy.h)))
    S=I(xspread)+I(economy.p['coupling'])*(economy.steps-1)*h+I(noise_i)*sqrt(I(economy.steps)*(1-I(1)/d))
    terminal_upper=I(economy.gamma)*S*W
    Lambda=production+terminal_upper
    lo=I(np.minimum(left,right)); hi=I(np.maximum(left,right))
    mean_direction=pc.mean_i(direction)
    stage_min=I(economy.A[0])*(I(utility_weight)*pc.mean_i(direction.square()/hi.square())+I(eta)*mean_direction.square())
    stage_max=I(economy.A[0])*(I(utility_weight)*pc.mean_i(direction.square()/lo.square())+I(eta)*mean_direction.square())
    q_second=Lambda-stage_min
    absolute=stage_max+production+I(economy.gamma)*(V.square()+S*W)
    mu=-q_second
    return dict(schema='nbo-r16-scalar-intervention-curvature-v1',
        parameter_interval=[0.,1.],dimension=d,steps=economy.steps,
        action_class='a_left+s*(a_right-a_left), 0<=s<=1; common future reference',
        state=y.tolist(),a_left=left.tolist(),a_right=right.tolist(),
        continuation_sha256=economy.continuation_sha256,
        current_utility_weight=float(utility_weight),current_adjustment=eta,
        first_variation_norm_upper=upper(V),second_variation_norm_upper=upper(W),
        terminal_dispersion_moment_upper=upper(S),production_curvature_upper=upper(production),
        continuation_second_derivative_upper=upper(Lambda),
        current_negative_curvature_lower=float(stage_min.lo),
        Q_second_derivative_upper=upper(q_second),absolute_second_derivative_upper=upper(absolute),
        strong_concavity_lower=float(mu.lo),strong_concavity_verified=bool(mu.lo>0),
        spectral_certificate=c['spectral'],
        no_observed_derivative_maximum=True,
        scope='exact stored-coefficient finite economy and complete continuous scalar action segment')


def scalar_gradient_gap(gradient_interval,candidate_s,curvature):
    """A simultaneous gradient interval gives a whole-segment optimum gap."""
    gl,gu=map(float,gradient_interval); s=float(candidate_s)
    if not (math.isfinite(gl) and math.isfinite(gu) and gl<=gu and 0<=s<=1):
        raise ValueError('invalid protected gradient interval or candidate')
    G=float(curvature['Q_second_derivative_upper'])
    if not math.isfinite(G): raise ValueError('finite global curvature required')
    deltas=[-I(s),1-I(s),I(0.)]
    candidates=[]
    for g in [gl,gu]:
        for delta in deltas:
            candidates.append(upper(I(g)*delta+I(G)*delta.square()/2))
        if G<0:
            vertex=-I(g)/I(G)
            # A rounded stationary point need not enclose the true maximum.
            # Include the exact-real vertex value whenever its outward
            # enclosure intersects the feasible displacement interval.
            if vertex.hi>=deltas[0].lo and vertex.lo<=deltas[1].hi:
                candidates.append(upper(-I(g).square()/(2*I(G))))
    return dict(gap_upper=max(0.,max(candidates)),gradient_interval=[gl,gu],candidate_s=s,
        curvature_upper=G,strong_concavity_used=G<0,
        scope='maximum over every s in [0,1], not only an evaluated grid')


def scalar_grid_gap(grid,upper_values,lower_candidate,curvature):
    """Protected point values plus curvature cover the entire scalar segment."""
    grid=np.asarray(grid,dtype=np.float64); vals=np.asarray(upper_values,dtype=np.float64)
    if grid.ndim!=1 or vals.shape!=grid.shape or len(grid)<2 or grid[0]!=0 or grid[-1]!=1 or np.any(np.diff(grid)<=0):
        raise ValueError('complete increasing [0,1] grid and one upper endpoint per point required')
    if not np.isfinite(vals).all() or not math.isfinite(lower_candidate):
        raise ValueError('finite protected endpoints required')
    spacing=I(float(np.max((I(grid[1:])-I(grid[:-1])).hi)))
    interpolation=I(curvature['absolute_second_derivative_upper'])*spacing.square()/8
    endpoint=I(float(vals.max()))+interpolation-I(lower_candidate)
    return dict(gap_upper=max(0.,upper(endpoint)),interpolation_upper=upper(interpolation),
        maximum_grid_spacing=upper(spacing),grid_points=len(grid),
        scope='entire continuous scalar interval in the finite economy; all point endpoints must be simultaneous')
