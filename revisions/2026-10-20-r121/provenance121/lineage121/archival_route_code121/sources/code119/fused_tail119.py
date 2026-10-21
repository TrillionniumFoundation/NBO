"""R119 phase C: one packed original-compiler call for each tail resolution.

Designed after the retained phase-A and phase-B outcomes. All economic
information, cuts, budgets, outward rules and complete fallbacks remain fixed.
Only positive-mass midpoint/endpoint payloads are purchased; their dense zero
placeholders are not original model observations. No timing advantage asserted.
"""
from __future__ import annotations
from pathlib import Path
import sys,time,resource
import numpy as np
import budgeted_tail119 as previous
from budgeted_tail119 import base,kern,econ,uniform,I,up,down
ROOT=Path(__file__).resolve().parents[1]
R,MZ,CUT_STEPS=previous.R,previous.MZ,previous.CUT_STEPS
KEYS=previous.KEYS
TAIL_LADDER=(2,4)
tail_mesh=previous.tail_mesh
constrained_gain=previous.constrained_gain
subset=previous.subset
propose_cut=previous.propose_cut
tail_state=previous.tail_state


def certificate(x,a,alpha,bins_per_tail=2,state=None,trace=None):
    x,a=np.asarray(x,dtype=float),np.asarray(a,dtype=float)
    if state is None: state=tail_state(x,a,alpha)
    elif not (state['alpha']==alpha and np.array_equal(state['x'],x) and np.array_equal(state['action'],a)):
        raise ValueError('Tail cache cannot cross state/action/objective identities')
    m=int(bins_per_tail); mids,edges,weights=tail_mesh(state['cut'],alpha,bins_per_tail)
    if trace is None: trace={}
    n,d=x.shape
    positive=np.stack([weights[:,0]>0,weights[:,m]>0],axis=1)
    if np.any(~np.any(positive,axis=1)):
        raise ArithmeticError('Every original tail has positive total probability')
    midmask=np.repeat(positive,m,axis=1)
    edgemask=np.repeat(positive,m+1,axis=1)
    midrows,midcols=np.nonzero(midmask)
    endrows,endcols=np.nonzero(edgemask)
    owners=np.concatenate([midrows,endrows])
    nodes=np.concatenate([mids[midrows,midcols],edges[endrows,endcols]])
    nm=len(midrows); ne=len(endrows)
    trace.update(stage='packed original terminal acquisition',bins_per_tail=m,
        midpoint_rows=midrows.tolist(),midpoint_columns=midcols.tolist(),
        endpoint_rows=endrows.tolist(),endpoint_columns=endcols.tolist(),
        packed_original_points=nm+ne)
    # Shape (point,1,state coordinate) keeps each original interval transition
    # independent. Every duplicate midpoint/endpoint is still paid once for
    # each requested payload, exactly as in the bounded prelude theorem.
    transitions=econ.transition(I(x[owners]),I(a[owners]),I(nodes[:,None]))
    econ.count('r119c_packed_compiler_calls',1)
    econ.count('r119c_packed_point_rows',len(owners))
    payload=kern.compiled_certificate(transitions,alpha)
    trace.update(stage='original point payloads completed',
        lower=payload['lower'][:,0].tolist(),upper=payload['upper'][:,0].tolist(),
        slope_lower=payload['slope'].lo[:,0,:].tolist(),slope_upper=payload['slope'].hi[:,0,:].tolist())
    midlower=np.zeros((n,2*m)); endpointupper=np.zeros((n,2*(m+1)))
    sl=np.zeros((n,2*m,d)); sh=np.zeros_like(sl)
    midlower[midrows,midcols]=payload['lower'][:nm,0]
    endpointupper[endrows,endcols]=payload['upper'][nm:,0]
    sl[midrows,midcols,:]=payload['slope'].lo[:nm,0,:]
    sh[midrows,midcols,:]=payload['slope'].hi[:nm,0,:]
    # Empty summands are exactly zero by their original density weights. Each
    # sum is still performed by the inherited termwise-outward interval API.
    lv=(I(midlower)*I(weights)).sum()
    endpoint_left=np.concatenate([endpointupper[:,:m],endpointupper[:,m+1:2*m+1]],axis=-1)
    endpoint_right=np.concatenate([endpointupper[:,1:m+1],endpointupper[:,m+2:2*m+2]],axis=-1)
    uv=(((I(endpoint_left)+I(endpoint_right))/2)*I(weights)).sum()
    b,_=econ.exposures(d)
    stage=econ.S(I(x))+econ.action_cost(I(a))
    witness=stage+econ.BETA*lv
    policy_upper=stage+econ.BETA*(uv+I(state['kappa'])+econ.TERMINAL_TOL)
    slope=econ.action_grad(I(a))+econ.BETA*(((I(sl,sh)*b).sum())*I(weights)).sum()
    optimum=econ.quadratic_minimum_lower(I(witness.lo),slope,I(a),econ.capacity(I(x)))
    result=dict(lower=witness.lo,upper=policy_upper.hi,optimum_lower=optimum,
        loss=up(policy_upper.hi-optimum),width=up(policy_upper.hi-witness.lo),
        witness_lower=witness.lo,slope_lower=slope.lo,slope_upper=slope.hi,
        selected_tail_lower=lv.lo,selected_tail_upper=uv.hi)
    trace.update(stage='original-law packed aggregation completed',
        aggregated_values={k:v.tolist() for k,v in result.items()})
    if np.any(result['loss']<0) or np.any(result['width']<0):
        raise ArithmeticError('Invalid packed original-law certificate')
    econ.count('r119b_midpoint_terminal_rows',nm)
    econ.count('r119b_endpoint_terminal_rows',ne)
    econ.count('r119b_original_action_certificates',n)
    result.update(bins_per_tail=m,cut=state['cut'].copy(),kappa=state['kappa'].copy(),
        derivative_lower=state['derivative_lower'].copy(),derivative_upper=state['derivative_upper'].copy(),
        maximum_terminal_gap=float(np.max(payload['gap'])))
    return result


def _service_core(x, alpha, model, trace, ladder):
    """Original actor + active-tail certificate + unchanged complete fallback.

The 2- and 4-cell attempts precede the frozen 128-bin full-support fallback.
The full current conventional proposal and every later refinement are charged.
"""
    x = np.asarray(x, dtype=float); before = econ.COUNTS.copy(); started = time.perf_counter()
    attempts = []; trace['attempts'] = attempts
    n = len(x); resolved = np.zeros(n, bool)
    rec = {k: np.empty(n) for k in KEYS}; first = {k: np.empty(n) for k in KEYS}
    used = np.zeros(n, int); rejected = np.zeros(n, bool); exact = np.zeros(n, bool)
    sys.path.insert(0, str(ROOT / 'frozen117/code117'))
    import precision117 as inherited
    with kern.backend(True):
        trace['stage'] = 'original actor proposal'
        t = time.perf_counter(); proposed = base.rep.proposal(x, alpha, model)
        trace['proposed'] = proposed.tolist()
        proposal_seconds = time.perf_counter() - t; actions = proposed.copy()
        trace['stage'] = 'tail location and original residual'
        cache = tail_state(x, proposed, alpha)
        trace['tail_state'] = {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in cache.items()}
        for bins in ladder:
            ids = np.flatnonzero(~resolved)
            if not len(ids):
                break
            trace['stage'] = 'budgeted-tail certificate'
            trace['bins_per_tail'] = bins; trace['unresolved_rows'] = ids.tolist()
            trace['current_tail_certificate'] = {}
            fresh = certificate(x[ids], proposed[ids], alpha, bins, subset(cache, ids), trace=trace['current_tail_certificate'])
            ok = uniform.qualifies(fresh)
            if bins == ladder[0]:
                for k in KEYS:
                    first[k][:] = fresh[k]
            for p, j in enumerate(ids):
                fields = {k: float(fresh[k][p]) for k in KEYS +
                    ('cut','kappa','derivative_lower','derivative_upper','witness_lower','slope_lower',
                     'slope_upper','selected_tail_lower','selected_tail_upper')}
                attempts.append(dict(row=int(j),kind='budgeted-tail',bins_per_tail=bins,
                    action=float(proposed[j]),qualified=bool(ok[p]),**fields))
            for k in KEYS:
                rec[k][ids] = fresh[k]
            used[ids] = bins; resolved[ids[ok]] = True
        ids = np.flatnonzero(~resolved)
        if len(ids):
            trace['stage'] = 'full-support fallback'
            trace['unresolved_rows'] = ids.tolist()
            fresh = uniform.certificate(x[ids], proposed[ids], alpha, 128)
            for p,j in enumerate(ids):
                attempts.append(dict(row=int(j),kind='full-support-fallback',bins=128,
                    action=float(proposed[j]),qualified=bool(uniform.qualifies(fresh)[p]),
                    **{k:float(fresh[k][p]) for k in KEYS}))
            trace['stage'] = 'complete inherited repair and refinement'
            aa, tail, rr, uu, ee = inherited.finish(x[ids], alpha, proposed[ids], fresh, attempts, ids)
            actions[ids] = aa; rejected[ids] = rr; used[ids] = uu; exact[ids] = ee
            for k in KEYS:
                rec[k][ids] = tail[k]
            resolved[ids] = True
    if not np.all(resolved) or not np.all(uniform.qualifies(rec)):
        raise ArithmeticError('Every original-economy decision must be qualified')
    rows = [dict(row=j,x0=float(xx[0]),x1=float(xx[1]),proposed=float(proposed[j]),
        action=float(actions[j]),first_rejected=bool(rejected[j]),bins=int(used[j]),
        exact_fallback=bool(exact[j]),action_distance_upper=float(up(np.sqrt(rec['loss'][j]))),
        **{k:float(rec[k][j]) for k in KEYS},**{'first_'+k:float(first[k][j]) for k in KEYS}) for j,xx in enumerate(x)]
    return dict(rows=rows,attempts=attempts,counts=base.counter_delta(before),
        seconds=time.perf_counter()-started,proposal_seconds=proposal_seconds,
        max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        terminal_policy_unchanged=True,cache_scope='same state/action/risk tail density only')


def service(x, alpha, model, ladder=TAIL_LADDER):
    """Preserve partial scientific attempts if a batch fails before completion."""
    before = econ.COUNTS.copy(); started = time.perf_counter()
    trace = dict(stage='input', state=np.asarray(x).tolist(), alpha=alpha)
    try:
        if tuple(ladder)!=TAIL_LADDER:
            raise ValueError('Only the declared two-level phase-C schedule is allowed')
        result = _service_core(x, alpha, model, trace, tuple(ladder))
        result['seconds'] = time.perf_counter() - started
        return result
    except BaseException as exc:
        trace.update(status='failed', elapsed_seconds=time.perf_counter()-started,
            counts=base.counter_delta(before), exception_type=type(exc).__name__, exception=str(exc))
        exc.evidence119 = trace
        raise

