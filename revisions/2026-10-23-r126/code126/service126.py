"""Prospective direct original-policy service with separate action and value gates.

The terminal-aware route never receives a completed strong prefix for free.
Its original-model oracle, fixed future controller, and fitted actors are the
unchanged published R125 dependencies. Recoverable numerical failure pays a
complete strong fused fallback. Every started query remains in the record.
"""
from common126 import *
import numpy as np

prior = old = env = None


def configure():
    global prior, old, env
    sys.path.insert(0, str(INHERITED / 'code125'))
    import service125
    prior = service125; prior.configure(); old = prior.old; env = prior.env


def terminal_certificate(case, action, common=None):
    """Exact action-aligned regret; this need not equal upper minus lower-optimum."""
    action = F(action)
    c = env.candidate(case, action, 'fused', common)
    left, right = env.envelope_root(case, True), env.envelope_root(case, False)
    if left > right: raise ArithmeticError('Contradictory optimizer bracket')
    gl, gu = env.gradient(case, action, False), env.gradient(case, action, True)
    projected = old.constrained_regret(dict(action=action, capacity=case['A'], mu=case['mu'], lower=gl, upper=gu))
    radius = max(abs(action-left), abs(action-right))
    bounds = dict(level=c['loss'], projected=case['delta']+projected,
                  terminal_linear=case['delta']+F(7)*radius)
    stationary = env.gradient(case, F(0), True) <= 0 <= env.gradient(case, case['A'], False)
    if stationary: bounds['terminal_quadratic'] = case['delta']+case['L']*radius*radius/2
    route, regret = min(bounds.items(), key=lambda item: (item[1], item[0]))
    if regret < 0: raise ArithmeticError('Negative original regret bound')
    lo = old.directed_float(c['lower'], False); hi = old.directed_float(c['upper'], True)
    optimum = old.directed_float(c['optimum_lower'], False)
    outward_regret = old.directed_float(regret, True)
    width = float(old.up(hi-lo))
    qualified = regret <= TAU and c['width'] <= OMEGA and F(outward_regret) <= TAU and F(width) <= OMEGA
    target = qualified and regret <= TARGET and F(outward_regret) <= TARGET
    c.update(action_gradient=[gl, gu], optimizer_bracket=[left, right], maximum_distance_to_bracket=radius,
             stationary_optimum_certified=stationary, regret_candidates=bounds, regret_route=route,
             direct_regret=regret, original_level_regret=c['loss'], qualified=qualified,
             target_qualified=target, outward=dict(lower=lo, upper=hi, optimum_lower=optimum,
                 certified_regret_upper=outward_regret, width=width,
                 level_regret_upper=float(old.up(hi-optimum))))
    return c


def actor_proposal(state, alpha, model):
    """Same paid actor and conventional proposal as the unchanged R121 service."""
    import models121 as models
    x = np.asarray(state, float)[None, :]
    if model is not None:
        d = model['basis']
        if (model.get('kind') != 'r121-anchored-root-critic' or d != models.definition(d['arm'], d['budget']) or
            len(model['theta']) != d['feature_count'] or np.any(~np.isfinite(model['theta'])) or
            np.any(np.asarray(model['theta']) < np.asarray(d['coefficient_lower'])) or
            np.any(np.asarray(model['theta']) > np.asarray(d['coefficient_upper']))):
            raise ValueError('Invalid frozen critic; no silent model replacement')
    tick = time.perf_counter()
    with old.kern.backend(True):
        if model is None:
            a = float(old.cont.actor(x, alpha, None, n=512, iterations=24)[0])
            trace = dict(rule='unchanged semi-analytic original midpoint proposal', midpoints=512, iterations=24)
        else:
            a, trace = models.actor(model, np.asarray(state, float))
            a = min(a, float(np.floor(old.econ.capacity(old.I(x)).lo[0]*2**30)/2**30))
            for name, field in [('piece_visits','action_piece_count'), ('root_candidates','polynomial_root_count'), ('value_evaluations','evaluated_proposal_count')]:
                old.econ.count('r121_learned_action_'+name, trace[field])
    cap = F(1,8)+sum(map(F,state))/16
    if not np.isfinite(a) or not 0 <= F(a) <= cap: raise ArithmeticError('Infeasible numerical actor proposal')
    trace = dict(trace, returned_feasible_action=float(a), returned_feasible_action_hex=float(a).hex(), seconds=time.perf_counter()-tick)
    return F(a), trace


def make_case(records, state, alpha, incumbent):
    baseline = dict(action=float(incumbent), original_optimum_lower=max(c['optimum_lower'] for c in records))
    return prior.make_case(records, state, alpha, baseline)


def final_row(c, state):
    d = c['outward']; regret = d['certified_regret_upper']
    return dict(state=list(state), action=float(c['b']), action_hex=float(c['b']).hex(),
                complete_policy_lower=d['lower'], complete_policy_upper=d['upper'],
                original_optimum_lower=d['optimum_lower'], certified_regret_upper=regret,
                action_distance_upper=float(old.up(np.sqrt(regret))),
                action_distance_quantity_is_bound_not_actual_error=True,
                lower=d['lower'], upper=d['upper'], optimum_lower=d['optimum_lower'],
                loss=regret, width=d['width'], level_regret_upper=d['level_regret_upper'],
                qualified=c['qualified'], future_controller='unchanged terminal_controller94.terminal_policy',
                future_error_allowance=str(DELTA), separate_action_and_value_certificates=True)


def direct_service(state, alpha, model):
    tick = time.perf_counter(); before = old.econ.COUNTS.copy()
    queries, candidates, acceptances, records = [], [], [], []
    used = 0; selected = None; actor = None; proposal = None; failure = None; fallback = None
    stop = 'maximum-action-centers'; visited = set()
    try:
        proposal, actor = actor_proposal(state, alpha, model)
        action = proposal; left, right = F(0), F(1,8)+sum(map(F,state))/16
        for center in range(MAX_CENTERS):
            previous = (left, right); queried_this_center = False; may_change_center = False
            for bins in LADDER:
                if (action, bins) in visited: continue
                nodes = 2*bins+1
                if used+nodes > NODE_BUDGET:
                    stop = 'declared-terminal-node-cap'; break
                q = dict(center=center, action=action, bins=bins, requested_terminal_nodes=nodes,
                         started=True, completed=False, bracket_before=[left,right])
                queries.append(q); used += nodes; visited.add((action,bins)); qt = time.perf_counter()
                c = prior.q_query(state, alpha, action, bins); records.append(c)
                q.update(completed=True, seconds=time.perf_counter()-qt, certificate=c)
                case = make_case(records, state, alpha, action if selected is None else selected['b'])
                common = env.support_minimum(case)
                left, right = env.envelope_root(case, True), env.envelope_root(case, False)
                if left > right: raise ArithmeticError('Empty original optimizer enclosure')
                q['bracket_after'] = [left,right]
                # Every earlier safe action is reconsidered under all paid information.
                menu = sorted({F(r['original_action']) for r in records} | ({selected['b']} if selected else set()))
                certificates = [terminal_certificate(case,b,common) for b in menu]
                candidates.append(dict(query=len(queries)-1, case=case, certificates=certificates))
                if selected is not None:
                    selected = next(d for d in certificates if d['b'] == selected['b'])
                    if not selected['qualified']: raise ArithmeticError('New valid information lost prior qualification')
                qualified = [d for d in certificates if d['qualified']]
                if selected is None and qualified:
                    selected = min(qualified, key=lambda d: (d['direct_regret'], d['upper'],d['b']))
                    acceptances.append(dict(query=len(queries)-1, reason='first-complete-qualified-policy', action=selected['b'], gain_lower=F(0)))
                elif selected is not None:
                    improvements = []
                    for d in qualified:
                        if d['b'] == selected['b']: continue
                        _, cu = env.contrast(case, selected['b'], d['b'])
                        cu = min(cu, d['upper']-case['delta']-selected['lower'])
                        gain = -cu-case['delta']
                        if gain > 0: improvements.append((gain,d))
                    if improvements:
                        gain, nxt = min(improvements,key=lambda item:(-item[0],item[1]['b']))
                        acceptances.append(dict(query=len(queries)-1,reason='strict-original-policy-improvement',old_action=selected['b'],action=nxt['b'],gain_lower=gain))
                        selected = nxt
                queried_this_center = True
                if selected is not None and selected['target_qualified']:
                    stop = 'action-target-and-independent-value-width'; break
                # Buying a sharper value level at a resolved action is distinct
                # from action localization. A failed width gate continues here.
                desired = env.rounded_action((left+right)/2, case['A'])
                if desired == action: continue
                # Finite center changes require certified localization progress,
                # except the first paid actor query which may lie anywhere.
                contraction = right-left <= (previous[1]-previous[0])/2 + abs(action-(previous[0]+previous[1])/2)
                q['certified_bracket_halving'] = contraction
                if center == 0 or contraction:
                    may_change_center = True; break
            if selected is not None and selected['target_qualified']: break
            if stop == 'declared-terminal-node-cap': break
            if not queried_this_center:
                stop = 'all-declared-precisions-at-current-center-already-paid'; break
            if not may_change_center:
                stop = 'maximum-risk-precision-without-required-progress'; break
            case = make_case(records, state, alpha, action if selected is None else selected['b'])
            desired = env.rounded_action((left+right)/2, case['A'])
            if desired == action:
                stop = 'maximum-risk-precision-at-resolved-center'; break
            action = desired
        if selected is not None:
            answer = final_row(selected, state)
        else:
            stop = 'no-direct-qualified-candidate-paid-complete-fused-fallback'
            fallback = prior.service(state, alpha, model, 'fused_control'); answer = dict(fallback)
    except (ArithmeticError, np.linalg.LinAlgError) as exc:
        failure = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc(), seconds=time.perf_counter()-tick)
        # A completed safe policy survives later enhancement failure.
        if selected is not None and selected['qualified']:
            answer = final_row(selected,state); stop = 'numerical-failure-retain-qualified-policy'
        else:
            fallback = prior.service(state,alpha,model,'fused_control'); answer = dict(fallback)
            stop = 'numerical-failure-paid-complete-fused-fallback'
    answer.update(service126='direct_terminal', state126=list(state), alpha=alpha,
        proposal_action126=None if proposal is None else float(proposal), actor_trace126=actor,
        new_queries126=queries, candidate_records126=candidates, acceptances126=acceptances,
        initial_support_certificates=records, direct_requested_terminal_contexts126=used,
        selected_certificate126=selected, fallback126=fallback, failure126=failure, stop126=stop,
        target_qualified126=F(answer['certified_regret_upper']) <= TARGET and F(answer['width']) <= OMEGA,
        strict_policy_improvements126=sum(x['reason']=='strict-original-policy-improvement' for x in acceptances),
        complete_service_seconds126=time.perf_counter()-tick, counts126=old.lab.inherited.base.counter_delta(before),
        same_original_future=True, initialized_from_completed_prefix=False,
        fallback_was_paid=(fallback is not None))
    return plain(answer)


def service(state, alpha, model, mode):
    if mode == 'direct_terminal': return direct_service(state,alpha,model)
    if mode not in ('fused_control','warm_adaptive','grid33'): raise ValueError('Undeclared R126 service')
    tick=time.perf_counter(); before=old.econ.COUNTS.copy()
    row=prior.grid_service(state,alpha) if mode=='grid33' else prior.service(state,alpha,model,mode)
    row.update(service126=mode,state126=list(state),alpha=alpha,
        target_qualified126=F(row['certified_regret_upper'])<=TARGET and F(row['width'])<=OMEGA,
        complete_service_seconds126=time.perf_counter()-tick,counts126=old.lab.inherited.base.counter_delta(before),
        direct_requested_terminal_contexts126=0,new_queries126=[],strict_policy_improvements126=0,
        failure126=row.get('failure125'),stop126=row.get('stop125'),same_original_future=True)
    return plain(row)
