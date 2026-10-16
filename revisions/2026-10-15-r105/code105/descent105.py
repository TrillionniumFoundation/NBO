"""Postqualification cost descent for the unchanged original investment economy.

Only disjoint original-policy intervals authorize replacement. The old global
lower bound is reused; this module never infers safety from an optimizer flag.
"""
from __future__ import annotations
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key]='1'
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code104'))
import runtime104 as rt
from interval94 import I, up
from quadrature96 import endpoint_mixture, qualifies
from continuum94 import shock_mesh
inv=rt.inv
MODES=('baseline','fixed128','adaptive')
WIDTH=1/8192
TAU=1/256
SKIP_LOSS=2**-16


def cost_only(x,actions,alpha,bins):
    """Enclose the same complete policy without a new root minimum solve."""
    x,a=I(x).checked(),I(actions).checked()
    mids,edges=shock_mesh(bins)
    mid=inv.terminal_certificate(inv.transition(x,a,I(mids)),alpha)
    end=inv.terminal_certificate(inv.transition(x,a,I(edges)),alpha)
    low=inv.discrete_avar_interval(I(mid['lower']),alpha)
    high=inv.discrete_avar_interval(I(endpoint_mixture(end['upper'])),alpha)
    base=inv.S(x)+inv.action_cost(a)
    out=I((base+inv.BETA*low).lo,
          (base+inv.BETA*(high+inv.TERMINAL_TOL)).hi).checked()
    inv.count('r105_cost_only_queries',a.lo.size)
    inv.count('r105_midpoint_terminal_rows',mid['lower'].size)
    inv.count('r105_endpoint_terminal_rows',end['upper'].size)
    return out


def strict_gate(old_lower,new_lower,new_upper,bound):
    """Necessary numerical consistency checks; inputs must be valid enclosures."""
    values=np.broadcast_arrays(old_lower,new_lower,new_upper,bound)
    if any(np.any(~np.isfinite(v)) for v in values):
        raise ArithmeticError('Nonfinite policy evidence')
    old_lower,new_lower,new_upper,bound=values
    if np.any(new_lower>new_upper) or np.any(new_upper<bound):
        raise ArithmeticError('Contradictory policy or original-optimum bounds')
    gate=(new_upper<old_lower)&(up(new_upper-new_lower)<=WIDTH)
    if np.any(gate&(up(new_upper-bound)>TAU)):
        raise ArithmeticError('Descent contradicts inherited qualification')
    return gate


def service(x,alpha,model,mode,keep_trials=True):
    if mode not in MODES:raise ValueError('Unknown postqualification mode')
    base=rt.service(x,alpha,model,'fast_legacy',keep_trials=False)
    if not np.all(qualifies(base)):raise ArithmeticError('Unqualified incumbent')
    x=np.asarray(x,dtype=float)
    final={key:(value.copy() if isinstance(value,np.ndarray) else value)
           for key,value in base.items() if key not in ('trials','slope_lo','slope_hi')}
    final.update(baseline_actions=base['actions'].copy(),baseline_lower=base['lower'].copy(),
                 baseline_upper=base['upper'].copy(),baseline_loss=base['loss'].copy(),
                 baseline_optimum_lower=base['optimum_lower'].copy())
    skipped=base['exact']|(base['loss']<=SKIP_LOSS)
    accepted=np.zeros(len(x),dtype=bool)
    trials=[];queries=np.zeros(len(x),dtype=int);accepted_bins=np.zeros(len(x),dtype=int)
    if mode!='baseline':
        full=rt.clip_action(x,base['actions']-(base['slope_lo']+base['slope_hi'])/4)
        with rt.terminal_mode(True):
            for displacement in (1.,.5,.25):
                ids=np.flatnonzero(~skipped&~accepted)
                if not len(ids):break
                candidate=rt.clip_action(x[ids],base['actions'][ids]+displacement*(full[ids]-base['actions'][ids]))
                moved=candidate!=base['actions'][ids]
                ids,candidate=ids[moved],candidate[moved]
                if not len(ids):continue
                lower=np.full(len(ids),-np.inf);upper=np.full(len(ids),np.inf)
                active=np.ones(len(ids),dtype=bool)
                ladder=(128,) if mode=='fixed128' else (8,16,32,64,128)
                for bins in ladder:
                    local=np.flatnonzero(active)
                    if not len(local):break
                    rows=ids[local]
                    cost=cost_only(x[rows],candidate[local],alpha,bins)
                    lower[local]=np.maximum(lower[local],cost.lo)
                    upper[local]=np.minimum(upper[local],cost.hi)
                    queries[rows]+=1
                    gate=strict_gate(base['lower'][rows],lower[local],upper[local],base['optimum_lower'][rows])
                    reject=lower[local]>=base['upper'][rows]
                    for j,where in enumerate(local):
                        row=int(ids[where])
                        if keep_trials:
                            trials.append(dict(row=row,displacement=displacement,bins=bins,
                                incumbent_action=float(base['actions'][row]),candidate=float(candidate[where]),
                                incumbent_cost=[float(base['lower'][row]),float(base['upper'][row])],
                                candidate_cost=[float(lower[where]),float(upper[where])],
                                bound=float(base['optimum_lower'][row]),accepted=bool(gate[j]),
                                rejected_by_lower=bool(reject[j])))
                    yes=local[gate];outrows=ids[yes]
                    accepted[outrows]=True;accepted_bins[outrows]=bins
                    final['actions'][outrows]=candidate[yes]
                    final['lower'][outrows]=lower[yes];final['upper'][outrows]=upper[yes]
                    final['loss'][outrows]=up(upper[yes]-base['optimum_lower'][outrows])
                    final['width'][outrows]=up(upper[yes]-lower[yes])
                    active[local[gate|reject]]=False
    if not np.all(qualifies(final)):raise ArithmeticError('Final policy not qualified')
    if not np.array_equal(final['optimum_lower'],base['optimum_lower']):
        raise ArithmeticError('Original-optimum lower bound changed')
    unchanged=~accepted
    for key in ('actions','lower','upper'):
        if not np.array_equal(final[key][unchanged],base[key][unchanged]):
            raise ArithmeticError('Refusal changed incumbent')
    final.update(post_accepted=accepted,post_skipped=skipped,post_queries=queries,
                 post_bins=accepted_bins,post_trials=trials,
                 scope='same original problem and fixed terminal policy; root-state comparison only')
    return final
