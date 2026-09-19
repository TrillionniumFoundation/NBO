"""An independently derived, data-dependent roundoff account for stored primitives.

No generator, Bellman solver, or advertised EPS is imported. All bounds in the
recurrence are Fractions of binary64 inputs. CSR summation is bounded over EVERY
row. See Supplement S.16 for the operation graph and exact scope.
"""
from __future__ import annotations
from fractions import Fraction as Q
import math
import numpy as np

U=Q(1,2**53)
SUB=Q(1,2**1074)
def rat(x): return Q.from_float(float(x))
def gamma(n):
    if n*U>=1: raise ValueError('arithmetic operation count overflow')
    return n*U/(1-n*U)
def upward(q):
    x=float(q)
    return float(np.nextafter(x,np.inf)) if rat(x)<q else x
def downward(q):
    x=float(q)
    return float(np.nextafter(x,-np.inf)) if rat(x)>q else x

def derive(b,j,allowance=1e-7):
    """Independently derive bounds; allowance is a ceiling, never a premise."""
    if not (0<float(allowance)<1): raise ValueError('invalid advertised allowance')
    if b.steps!=8: raise ValueError('this audit graph is for the eight-date target')
    matrices=[]; reward=Q(0); duration=Q(0); stepcost=rat(b.spec.cost)
    if stepcost<0 or stepcost>2: raise ValueError('uncovered adjustment-cost coefficient')
    ranges={'law':[0.,1.],'benefit':[-2.,2.],'fee':[0.,2.]}
    dmax=Q(2); fmax=Q(2); maxnnz=0; mass=Q(0); audits=[]
    for k,e in enumerate(b.e):
        for n,z in enumerate([e.common]+e.extra):
            arrays=[z.base,z.duration,z.effort,z.settlement,z.exit_discount]
            if not all(np.isfinite(a).all() for a in arrays):raise ValueError('nonfinite primitive')
            if np.any(z.duration<0) or np.any(z.effort<0):raise ValueError('negative duration or effort')
            reward=max(reward,rat(np.max(np.abs(z.base)))+dmax*rat(z.duration.max())+stepcost*rat(z.effort.max()))
            duration=max(duration,rat(z.duration.max()))
            matrices.append((f'kernel.{k}.{n}',z.matrix))
        matrices.append((f'first.{k}',j.fm.rows[k]))
        if np.any(j.fm.duration[k]<0) or not np.isfinite(j.fm.reward[k]).all():raise ValueError('invalid first-date primitives')
        reward=max(reward,rat(np.max(np.abs(j.fm.reward[k])))+dmax*rat(np.max(j.fm.duration[k])))
        duration=max(duration,rat(np.max(j.fm.duration[k])))
    for name,m in matrices:
        if not np.isfinite(m.data).all() or np.any(m.data<0):raise ValueError('negative/nonfinite '+name)
        s=int(np.diff(m.indptr).max(initial=0));maxnnz=max(maxnnz,s)
        # sum_duplicates has already been incorporated in the stored target.
        # reduceat/sparse sum uses at most s additions on each nonnegative row.
        computed=float(np.asarray(m.sum(axis=1)).max(initial=0.))
        upper=(rat(computed)+(s+1)*SUB)/(1-gamma(max(1,s)))
        if upper>1:raise ValueError('independently bounded row mass exceeds one: '+name)
        mass=max(mass,upper)
        audits.append(dict(name=name,rows=m.shape[0],nonzeros=m.nnz,max_terms=s,
                           computed_max_mass=computed,verified_max_mass=upward(upper)))
    terminal=max(rat(np.max(abs(b.terminal))),Q(0));stop=terminal+fmax
    # Global norm and forward error at each remaining horizon. The max operation
    # chooses an operand; it contributes no further arithmetic error.
    norm=[terminal];ev=[Q(0)];ep=[Q(0)];ec=[Q(0)]
    s=maxnnz
    counts=dict(bellman=2*s+20,polynomial=2*s+28,count_information=2*s+40,
                signed_majorant=2*s+30,restriction=6*b.steps*b.steps+12)
    for h in range(1,b.steps+1):
        q=reward+mass*norm[-1]
        norm.append(max(stop,q))
        ev.append(mass*ev[-1]+gamma(counts['bellman'])*max(q,stop)+counts['bellman']*SUB)
        ep.append(mass*ep[-1]+gamma(counts['polynomial'])*max(q,stop)+counts['polynomial']*SUB)
        ec.append(mass*ec[-1]+gamma(counts['count_information'])*max(q,stop)+counts['count_information']*SUB)
    major=Q(0);em=Q(0)
    for h in range(1,b.steps+1):
        # |(Kb-Ka)(Vb-Va)| <= 4*m*||V||. Endpoint errors and
        # the propagated majorant are charged before positive majorization.
        scale=4*mass*norm[h-1]+mass*major
        em=4*mass*ev[h-1]+mass*em+gamma(counts['signed_majorant'])*scale+counts['signed_majorant']*SUB
        major=scale
    signed=ev[-1]+em/2+gamma(16)*(norm[-1]+major/2)
    restriction=gamma(counts['restriction'])*(norm[-1]+major/2)
    # Signed midpoint/radius transport uses four continuation magnitudes;
    # its statewise interval uncertainty is separate from this roundoff cost.
    transport=gamma(2*s+32)*(4*mass*(norm[-1]+Q(b.steps)*rat(allowance))+2*reward)+4*mass*ev[-1]
    bounds={'bellman_value':ev[-1],'fixed_policy_bernstein':ep[-1],
            'count_information_upper':ec[-1],'signed_chord_upper':signed,
            'restricted_signed_chord':signed+restriction,
            'restricted_policy':ep[-1]+restriction,'signed_transport':transport}
    derived=max(bounds.values())
    if derived>=rat(allowance):
        raise ValueError(f'derived arithmetic bound {upward(derived):.17g} exceeds advertised allowance {allowance:.17g}')
    if Q(b.steps)*duration>1:raise ValueError('duration bound A<=1 is not verified')
    return dict(schema='nbo-r13-derived-arithmetic-v1',unit_roundoff=float(U),
        operation_counts=counts,parameter_ranges=ranges,all_kernel_rows=audits,
        first_date_included=True,reward_norm=upward(reward),terminal_norm=upward(terminal),
        value_norm_by_horizon=[upward(q) for q in norm],majorant_norm=upward(major),
        maximum_discounted_mass=upward(mass),duration_upper=upward(Q(b.steps)*duration),
        bounds={k:upward(v) for k,v in bounds.items()},derived_maximum=upward(derived),
        advertised_allowance=float(allowance),passed=True,
        exact_bound_fraction=f'{derived.numerator}/{derived.denominator}',
        scope='Stored binary64 primitive arrays; round-to-nearest with gradual underflow. Constructor/model error is separate.')

def scalar_bounds(wm,w,wp,dm,d0,dp,G,F,epsilon=1e-7,eta=0.,cost=.02):
    """Directed exact-rational secants and participation arithmetic."""
    hm=rat(d0)-rat(dm);hp=rat(dp)-rat(d0)
    if min(hm,hp)<=0:raise ValueError('unordered benefit probes')
    lo=max(Q(0),(rat(w)-rat(wm)-2*rat(epsilon)-rat(eta))/hm)
    hi=min(Q(1),(rat(wp)-rat(w)+2*rat(epsilon)+rat(eta))/hp)
    if lo>hi:raise ValueError('empty exact service enclosure')
    cap=rat(cost)*rat(F)**2
    qhi=max(Q(0),rat(G)-rat(w)+rat(epsilon)+cap+rat(eta))
    qlo=max(Q(0),rat(G)-rat(w)-rat(epsilon)+cap)
    return dict(service_lower=downward(lo),service_upper=upward(hi),
                grant_executable=upward(qhi),grant_lower=downward(qlo))

def positive_witness(fm,q,closed_index,L,adj,slack=1e-9):
    """Feasible open-class lower witness; closure is ONLY an upper supremum."""
    i=int(closed_index);a=fm.actions[i].copy();v=float(q[i])
    if a[2]>0:
        return dict(indices=[i],weights=[1.],action=a.tolist(),value=v,
                    positivity_margin=float(a[2]),closure_value=v,closure_gap=0.,attained=True)
    if a[2]!=0:raise ValueError('positive closure optimizer outside its domain')
    pair=np.all(fm.actions[:,:2]==a[:2],axis=1)
    right=np.flatnonzero(pair&(fm.actions[:,2]>0)&(fm.actions[:,2]<=L))
    if not len(right):raise ValueError('no strictly positive interpolation segment')
    k=int(right[np.argmin(fm.actions[right,2])]);diff=max(0.,v-float(q[k]))
    t=min(.5,float(slack)/(1.+diff));a[2]=t*fm.actions[k,2]
    vv=(1-t)*v+t*float(q[k]);gap=max(0.,v-vv)
    if not 0<a[2]<=L or gap>slack+2e-14:raise ValueError('open-class lower witness failed')
    return dict(indices=[i,k],weights=[1-t,t],action=a.tolist(),value=vv,
                positivity_margin=float(a[2]),closure_value=v,closure_gap=gap,attained=False)

def verify_positive(fm,q,rec,L,adj):
    """Independent interpolation/feasibility check, not a producer assertion."""
    a=np.asarray(rec['action']);ix=np.asarray(rec['indices'],dtype=int);w=np.asarray(rec['weights'])
    if not np.isfinite(a).all() or not 0<a[2]<=L:raise ValueError('positive mandate requires a strictly positive risky share')
    if float(rec['positivity_margin'])!=float(a[2]):raise ValueError('positivity margin does not match witness')
    if (not adj and a[1]!=0) or len(ix) not in (1,2) or np.any(ix<0) or np.any(ix>=len(q)):raise ValueError('positive first-action feasibility')
    if np.any(w<0) or abs(float(w.sum())-1)>1e-15 or not np.all(fm.actions[ix,:2]==a[:2]):raise ValueError('invalid first-date interpolation')
    if np.max(abs(w@fm.actions[ix]-a))>1e-14:raise ValueError('first action and canonical interpolation disagree')
    if len(ix)==2:
        ps=np.sort(fm.actions[np.all(fm.actions[:,:2]==a[:2],axis=1),2])
        if np.any((ps>fm.actions[ix[0],2])&(ps<fm.actions[ix[1],2])):raise ValueError('not adjacent first-date knots')
    value=float(w@q[ix]);gap=max(0.,float(rec['closure_value'])-value)
    if abs(value-rec['value'])>2e-12 or abs(gap-rec['closure_gap'])>2e-12:raise ValueError('open-class lower value mismatch')
    if rec['attained'] and (len(ix)!=1 or gap>2e-12):raise ValueError('false attainment claim')
    return gap
