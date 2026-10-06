"""Two exact, specified construction instances, not a population experiment.

All products and actor/evaluation solves are rational. Factor updates alone
are rounded to the stated dyadic grid, with a full-step error allowance. The
changed-valuation case actually reuses the first case's trained factors.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import time
import robust_policy as r


def encode(x):
    if isinstance(x, F):
        if max(x.numerator.bit_length(), x.denominator.bit_length()) > 12000:
            return {'numerator_hex': hex(x.numerator), 'denominator_hex': hex(x.denominator)}
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    return x


def digest(x):
    return hashlib.sha256(json.dumps(encode(x), sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()


def primitives(changed=False):
    d = 2
    A = r.matrix([[F(1, 10), F(1, 50)], [0, F(11, 100)]])
    Q = r.matrix([[F(201, 200), 0], [0, F(199, 200)]]) if changed else r.eye(d)
    stages = [dict(A=A, B=r.eye(d), Q=Q, R=r.eye(d), L=r.eye(d, 0),
                   q=F(99, 100), r=1) for _ in range(4)]
    return dict(stages=stages, terminal=r.eye(d), covariance=r.eye(d, F(1, 1000)),
        beta=F(19, 20), theta=F(1, 10), eta=F(1, 10), epsilon=F(1, 10000),
        initial_radius=2)


def construct(changed=False, previous=None):
    kw = primitives(changed)
    plan = r.allocate(**kw)  # Before any own-policy target exists.
    T, d, beta = plan['T'], plan['d'], plan['beta']
    P = [None]*T+[plan['terminal']]
    delta = [F() for _ in range(T+1)]
    kappa = delta.copy()
    factors = {}; records = []; bits = 40
    for t in range(T-1, -1, -1):
        x = plan['stages'][t]
        S = r.transform(P[t+1], plan['covariance'], plan['theta'])
        truth = r.scale(S, d)
        traces = []; steps = 0; commutator_squared = F()
        if t == T-1:
            center = gram = truth
            evaluation_radius = F(); factor = None; cap = None
        else:
            evaluation_radius = F(1, 10**7)
            center = r.add(truth, r.matrix([[evaluation_radius, 0], [0, -evaluation_radius]]))
            r.target_radius(center, truth, evaluation_radius)
            factor = previous[t] if previous is not None else r.matrix([
                [F(7, 5), F(3, 100)], [-F(1, 100), F(7, 5)],
                [F(1, 100), -F(1, 100)]])
            initial_gram = r.mm(r.tr(factor), factor)
            commutator_squared = r.norm2(r.add(r.mm(initial_gram, center),
                                                r.mm(center, initial_gram), -1))
            e0 = r.warm.gate(factor, center, m=F(3, 2), upper=3, radius=F(1, 2))
            available = r.sqrt_down(plan['s']*x['r']*x['q'])
            tolerance = min(d*plan['qstar']/4,
                            d*available/(8*beta*x['b']*x['f']))
            nu = r.sqrt_up(F(len(factor)*d))/(2*(1 << bits))
            cap = r.warm.plan(m=F(3, 2), upper=3, radius=F(1, 2), alpha=F(1, 8),
                initial=e0, tolerance=tolerance, factor_error=nu, max_updates=10000)
            envelope = e0
            for j in range(cap['updates']):
                factor, actual_nu = r.warm.quantized_step(factor, center, F(1, 8), bits=bits)
                if actual_nu > nu:
                    raise ArithmeticError('Step error exceeded its planned allowance')
                envelope = cap['q']*envelope+cap['noise']
                error_squared = r.norm2(r.add(r.mm(r.tr(factor), factor), center, -1))
                if error_squared > envelope*envelope:
                    raise ArithmeticError('Warm contraction envelope violated')
                traces.append(dict(update=j+1, factor_sha256=digest(factor),
                                   gram_error_squared=error_squared, envelope=envelope))
            steps = cap['updates']
            gram = r.mm(r.tr(factor), factor)
            if r.norm2(r.add(gram, center, -1)) > tolerance*tolerance:
                raise ArithmeticError('Final Gram allowance not met')
            factors[t] = factor
        # A deliberately nonzero solve error exercises the actor share.
        actor = r.add(r.greedy(x, r.scale(gram, F(1, d)), beta), r.eye(d, F(1, 10**8)))
        check = r.local_gate(plan, t, gram, center, actor, evaluation_radius)
        D = r.add(r.mm(x['R'], actor),
            r.scale(r.mm(r.mm(r.tr(x['B']), S), check['closed']), beta), -1)
        zeta = check['exact_residual_upper']
        if r.norm2(D) > zeta*zeta:
            raise ArithmeticError('Exact action residual exceeds mixed-norm account')
        P[t] = r.own_coefficient(x, actor, S, beta)
        r.psd(r.add(r.eye(d, plan['pbar'][t]), P[t], -1))
        r.psd(r.add(P[t], r.eye(d, x['q']), -1))
        gamma = x['gamma']
        w = delta[t+1]/gamma**2
        fbar = x['f']+x['b']/x['r']*(zeta+beta*x['b']*x['f']*w)
        delta[t] = zeta*zeta/x['r']+beta*fbar*fbar*w
        kappa[t] = beta*(kappa[t+1]+plan['tau']*delta[t+1]/gamma)
        if delta[t] > plan['s']*plan['lam'][t] or kappa[t] > plan['s']*plan['mu'][t]:
            raise ArithmeticError('Primitive full-policy allocation exceeded')
        if t and delta[t] > x['q']:
            raise ArithmeticError('Lower subsolution is not positive')
        lower_next = r.add(P[t+1], r.eye(d, delta[t+1]), -1)
        r.psd(lower_next)
        lower_S = r.transform(lower_next, plan['covariance'], plan['theta'])
        lower_actor = r.greedy(x, lower_S, beta)
        lower_bellman = r.own_coefficient(x, lower_actor, lower_S, beta)
        lower_current = r.add(P[t], r.eye(d, delta[t]), -1)
        # An independent matrix subsolution check, not only scalar recurrence.
        r.psd(r.add(lower_bellman, lower_current, -1))
        records.append(dict(date=t, target=truth, center=center, factor=factor, gram=gram,
            actor=actor, own_coefficient=P[t], initial_commutator_squared=commutator_squared,
            reused_previous_factor=previous is not None and t<T-1,
            training_cap=cap, hidden_updates=steps, trace=traces, local_check=check,
            exact_action_residual_squared=r.norm2(D), delta=delta[t], kappa=kappa[t]))
    gap = delta[0]*plan['initial_radius']+kappa[0]
    if gap > plan['epsilon']:
        raise ArithmeticError('Requested economic accuracy not certified')
    records.sort(key=lambda v: v['date'])
    result = dict(regime='changed-valuation' if changed else 'anchor',
        primitives=kw, primitive_budget=plan, records=records, certified=True,
        policy_gap_upper=gap, requested_policy_tolerance=plan['epsilon'],
        total_hidden_updates=sum(v['hidden_updates'] for v in records),
        noncommuting_fits=sum(v['initial_commutator_squared']>0 for v in records),
        storage_bits=bits, arithmetic='Exact rational products and solves; nearest dyadic factor storage',
        physical_action_allowance=0,
        physical_action_scope='The specified rational actor is applied exactly in this construction instance.')
    return result, factors


def execute():
    start = time.perf_counter()
    anchor, factors = construct()
    changed, _ = construct(True, factors)
    here = Path(__file__).resolve().parent
    sources = [here/'robust_policy.py', here/'exact_construction.py', r._PATH]
    report = dict(instances=[anchor, changed],
        elapsed_seconds=time.perf_counter()-start,
        source_sha256={str(p.relative_to(here.parents[2])):
                       hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        scope='Two exact specified constructive validations, not independent economic samples or a cost-dominance study.')
    dest = here.parent/'results/EXACT_CONSTRUCTION.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(encode(report), indent=2)+'\n')
    print(json.dumps(dict(instances=[dict(regime=x['regime'], certified=x['certified'],
        total_hidden_updates=x['total_hidden_updates'], noncommuting_fits=x['noncommuting_fits'],
        policy_gap_upper=float(x['policy_gap_upper'])) for x in (anchor, changed)],
        exact_record=str(dest), elapsed_seconds=report['elapsed_seconds']), indent=2))


if __name__ == '__main__':
    execute()
