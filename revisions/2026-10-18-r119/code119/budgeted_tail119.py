"""R119 phase B: bounded preliminary tail work, original complete fallback.

Designed after the retained phase-A results. A floating boundary selection is
only a proposal; original endpoint intervals pay its kappa exactly as before.
At most 30 outward terminal point values and 16 floating terminal values are
purchased per proposed action before returning or entering the frozen service.
"""
from __future__ import annotations
from pathlib import Path
import sys,time,resource
import numpy as np
import active_tail119 as original
from active_tail119 import base,kern,econ,uniform,I,up,down
ROOT=Path(__file__).resolve().parents[1]
R,MZ,CUT_STEPS=original.R,original.MZ,original.CUT_STEPS
KEYS=original.KEYS
TAIL_LADDER=(2,4)
tail_mesh=original.tail_mesh
constrained_gain=original.constrained_gain
subset=original.subset


def propose_cut(x,a,alpha):
    n=len(x); length=alpha/16
    left=np.full(n,-R); right=np.full(n,R-length)
    def difference(ids,u):
        z=np.stack([u,u+length],axis=-1)
        y=econ.transition(I(x[ids]),I(a[ids]),I(z)).mid()
        value,_=kern.compiled_float_value_slope(y,alpha)
        econ.count('r119b_tail_proposal_point_values',value.size)
        return value[:,1]-value[:,0]
    ids=np.arange(n); dl,dr=difference(ids,left),difference(ids,right)
    at_left,at_right=dl>=0,dr<=0
    interior=np.flatnonzero(~(at_left|at_right))
    for _ in range(CUT_STEPS):
        if not len(interior): break
        middle=(left[interior]+right[interior])/2
        d=difference(interior,middle)
        left[interior]=np.where(d<0,middle,left[interior])
        right[interior]=np.where(d>=0,middle,right[interior])
    u=np.where(at_left,-R,np.where(at_right,R-length,(left+right)/2))
    return np.clip(np.rint(u*2**32)/2**32,-R,R-length)


def tail_state(x,a,alpha):
    x,a=np.asarray(x,dtype=float),np.asarray(a,dtype=float)
    if alpha not in (.5,.75) or x.ndim!=2 or a.shape!=(len(x),) or len(x)==0:
        raise ValueError('Nonempty original batched state/action/risk required')
    if x.shape[1]<2 or x.shape[1]%2 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(a)) or np.any(x<0) or np.any(x>1):
        raise ValueError('Original finite even-dimensional unit cube required')
    if np.any(a<0) or np.any(a>econ.capacity(I(x)).lo):
        raise ValueError('The actual original action must be feasible')
    u=propose_cut(x,a,alpha); length=alpha/16
    endpoints=np.stack([u,u+length],axis=-1)
    values=kern.compiled_certificate(econ.transition(I(x),I(a),I(endpoints)),alpha)
    d=I(values['lower'][:,1],values['upper'][:,1])-I(values['lower'][:,0],values['upper'][:,0])
    gap=constrained_gain(d,MZ*length,u,-R,R-length)
    kappa=(I(gap)/(2*R*(1-alpha))).hi
    econ.count('r119b_tail_residual_point_values',2*len(x))
    econ.count('r119b_tail_density_constructions',len(x))
    return dict(x=x.copy(),action=a.copy(),alpha=alpha,cut=u,
        derivative_lower=d.lo,derivative_upper=d.hi,kappa=kappa)


def certificate(x,a,alpha,bins_per_tail=2,state=None,trace=None):
    x,a=np.asarray(x,dtype=float),np.asarray(a,dtype=float)
    if state is None: state=tail_state(x,a,alpha)
    elif not (state['alpha']==alpha and np.array_equal(state['x'],x) and np.array_equal(state['action'],a)):
        raise ValueError('Tail cache cannot cross state/action/objective identities')
    m=int(bins_per_tail); mids,edges,weights=tail_mesh(state['cut'],alpha,bins_per_tail)
    if trace is None: trace={}
    trace.update(bins_per_tail=m,completed_groups=[],stage='group initialization')
    result={key:np.empty(len(x)) for key in KEYS+('witness_lower','slope_lower','slope_upper','selected_tail_lower','selected_tail_upper')}
    maximum_gap=0.; b,_=econ.exposures(x.shape[-1])
    has_left,has_right=weights[:,0]>0,weights[:,m]>0
    for left,right in ((True,False),(False,True),(True,True)):
        ids=np.flatnonzero((has_left==left)&(has_right==right))
        if not len(ids): continue
        blocks=[v for v,on in enumerate((left,right)) if on]
        midcols=np.concatenate([np.arange(v*m,(v+1)*m) for v in blocks])
        edgecols=np.concatenate([np.arange(v*(m+1),(v+1)*(m+1)) for v in blocks])
        trace['current_group']=dict(rows=ids.tolist(),positive_tail_blocks=blocks)
        trace['stage']='nonempty-tail midpoint values'
        mm=mids[np.ix_(ids,midcols)]; ee=edges[np.ix_(ids,edgecols)]; ww=weights[np.ix_(ids,midcols)]
        mid=kern.compiled_certificate(econ.transition(I(x[ids]),I(a[ids]),I(mm)),alpha)
        trace['current_group']['midpoint_lower']=mid['lower'].tolist()
        trace['stage']='nonempty-tail endpoint values'
        end=kern.compiled_certificate(econ.transition(I(x[ids]),I(a[ids]),I(ee)),alpha)
        trace['current_group']['endpoint_upper']=end['upper'].tolist()
        trace['stage']='original-law group aggregation'
        lv=(I(mid['lower'])*I(ww)).sum()
        endpoint_left=np.concatenate([end['upper'][:,v*(m+1):v*(m+1)+m] for v in range(len(blocks))],axis=-1)
        endpoint_right=np.concatenate([end['upper'][:,v*(m+1)+1:(v+1)*(m+1)] for v in range(len(blocks))],axis=-1)
        uv=(((I(endpoint_left)+I(endpoint_right))/2)*I(ww)).sum()
        stage=econ.S(I(x[ids]))+econ.action_cost(I(a[ids]))
        witness=stage+econ.BETA*lv
        policy_upper=stage+econ.BETA*(uv+I(state['kappa'][ids])+econ.TERMINAL_TOL)
        slope=econ.action_grad(I(a[ids]))+econ.BETA*(((mid['slope']*b).sum())*I(ww)).sum()
        optimum=econ.quadratic_minimum_lower(I(witness.lo),slope,I(a[ids]),econ.capacity(I(x[ids])))
        values=dict(lower=witness.lo,upper=policy_upper.hi,optimum_lower=optimum,
            loss=up(policy_upper.hi-optimum),width=up(policy_upper.hi-witness.lo),
            witness_lower=witness.lo,slope_lower=slope.lo,slope_upper=slope.hi,
            selected_tail_lower=lv.lo,selected_tail_upper=uv.hi)
        for key,value in values.items(): result[key][ids]=value
        trace['completed_groups'].append(dict(rows=ids.tolist(),values={k:v.tolist() for k,v in values.items()}))
        maximum_gap=max(maximum_gap,float(np.max(mid['gap'])),float(np.max(end['gap'])))
        econ.count('r119b_midpoint_terminal_rows',mid['lower'].size)
        econ.count('r119b_endpoint_terminal_rows',end['upper'].size)
    if np.any(~(has_left|has_right)) or np.any(result['loss']<0) or np.any(result['width']<0):
        raise ArithmeticError('Invalid nonempty-tail original-law certificate')
    econ.count('r119b_original_action_certificates',len(x))
    result.update(bins_per_tail=m,cut=state['cut'].copy(),kappa=state['kappa'].copy(),
        derivative_lower=state['derivative_lower'].copy(),derivative_upper=state['derivative_upper'].copy(),
        maximum_terminal_gap=maximum_gap)
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
        if tuple(ladder) not in (TAIL_LADDER,original.TAIL_LADDER):
            raise ValueError('Only the two declared phase-B schedules are allowed')
        result = _service_core(x, alpha, model, trace, tuple(ladder))
        result['seconds'] = time.perf_counter() - started
        return result
    except BaseException as exc:
        trace.update(status='failed', elapsed_seconds=time.perf_counter()-started,
            counts=base.counter_delta(before), exception_type=type(exc).__name__, exception=str(exc))
        exc.evidence119 = trace
        raise


def masked_service(x,alpha,model):
    """Ablation: sparse tail work with the full inherited six-level ladder."""
    return service(x,alpha,model,ladder=original.TAIL_LADDER)
