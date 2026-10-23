"""Paid original-root value probes and sound action-marginal label intervals.

Imported only after the immutable source gate. No fitted critic or compiler
support slope is treated as an exact Bellman derivative. Whole-support convex
order uses the unchanged original V1 primitive and continuous innovation law.
"""
from __future__ import annotations

from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path
import sys
import time
import json
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"frozen108/code108"))
sys.path.insert(0, str(ROOT/"code120"))
import improvement120 as inherited
import kernel108 as kern
import continuum94 as cont
import quadrature96 as quad
import investment94 as econ
from interval94 import I, up

BINS = 256
PROBE_H = 2**-12
V_KNOTS = (0., .25, .5, .75, 1.)
KEYS = ("lower", "upper", "optimum_lower", "loss", "width")


def emit(sink, event, **payload):
    if sink is not None:
        sink(dict(event=event, **inherited.plain(payload)))


def smoothness_rational(alpha):
    a = Fraction.from_float(float(alpha)); t = 1-a
    beta, mz = Fraction(15, 16), Fraction(181, 64)
    m = Fraction(1413, 128)+beta*(Fraction(127, 16)+Fraction(19625, 20480)*a/t)
    c = Fraction(4, 5)*m
    la = 5+beta*(Fraction(5, 16)*m+c*c*a/(mz*t))
    global_h = beta*(Fraction(441, 1024)*m+Fraction(147, 160)*m*m*a/(mz*t))
    return dict(M=m, C=c, L_action=la, H_global_Lipschitz=global_h)


def fraction_interval(q):
    v = float(q)
    lo = np.nextafter(v, -np.inf) if Fraction.from_float(v)>q else v
    hi = np.nextafter(v, np.inf) if Fraction.from_float(v)<q else v
    return I(lo, hi)


def value_probe(state, v, alpha, sink=None):
    x = np.asarray(state, float)[None, :]
    cap = .125+(x[0, 0]+x[0, 1])/16
    action = cap*float(v)
    before, started = econ.COUNTS.copy(), time.perf_counter()
    emit(sink, "root-value-probe-start", state=x[0], normalized_action=v,
         action=action, alpha=alpha, bins=BINS, deployed_future_pad_in_label=False)
    mids, edges = cont.shock_mesh(BINS)
    middle = kern.compiled_certificate(econ.transition(I(x), I([action]), I(mids)), alpha)
    endpoint = kern.compiled_certificate(econ.transition(I(x), I([action]), I(edges)), alpha)
    lower_risk = econ.discrete_avar_interval(I(middle["lower"]), alpha)
    upper_risk = econ.discrete_avar_interval(I(quad.endpoint_mixture(endpoint["upper"])), alpha)
    stage = econ.S(I(x))+econ.action_cost(I([action]))
    low = (stage+econ.BETA*lower_risk).lo
    high = (stage+econ.BETA*upper_risk).hi
    if np.any(low>high) or np.any(~np.isfinite(low)) or np.any(~np.isfinite(high)):
        raise ArithmeticError("Invalid original-root value enclosure")
    econ.count("r121_label_midpoint_terminal_rows", middle["lower"].size)
    econ.count("r121_label_endpoint_terminal_rows", endpoint["upper"].size)
    econ.count("r121_label_original_root_contexts", 1)
    emit(sink, "root-value-probe-complete", state=x[0], normalized_action=v,
         action=action, alpha=alpha, bins=BINS,
         midpoint_payload=middle, endpoint_payload=endpoint,
         q_lower=low, q_upper=high,
         continuum_method="midpoint hinge Jensen lower; repeated endpoint hinge secant upper before AVaR minimization",
         seconds_before_this_record=time.perf_counter()-started)
    return dict(u=[float(x[0,0]), float(x[0,1]), float(v)], state=x[0].tolist(),
        action=float(action), action_hex=float(action).hex(), alpha=alpha, bins=BINS,
        q_lower=float(low[0]), q_upper=float(high[0]),
        original_optimal_future_value=True, deployed_future_error_allowance_in_training_label=0.,
        maximum_terminal_gap=float(max(np.max(middle["gap"]), np.max(endpoint["gap"]))),
        counts=inherited.base.counter_delta(before), seconds=time.perf_counter()-started)


def derivative_label(state, v, by_v, alpha):
    cap = .125+(state[0]+state[1])/16
    action, step = cap*v, cap*PROBE_H
    la = fraction_interval(smoothness_rational(alpha)["L_action"])
    d, mu = I(step), I(2)
    def q(vv):
        row = by_v[vv]
        return I(row["q_lower"], row["q_upper"])
    available = []
    if v<1:
        forward = (q(v+PROBE_H)-q(v))/d
        bound = forward+I((-la*d/2).lo, (-mu*d/2).hi)
        available.append(dict(rule="forward strong-convex/smooth secant", lower=float(bound.lo), upper=float(bound.hi)))
    if v>0:
        backward = (q(v)-q(v-PROBE_H))/d
        bound = backward+I((mu*d/2).lo, (la*d/2).hi)
        available.append(dict(rule="backward strong-convex/smooth secant", lower=float(bound.lo), upper=float(bound.hi)))
    if 0<v<1:
        central = (q(v+PROBE_H)-q(v-PROBE_H))/(2*d)
        pad = (la-mu)*d/4
        bound = central+I(-pad.hi, pad.hi)
        available.append(dict(rule="central strong-convex/smooth secant", lower=float(bound.lo), upper=float(bound.hi)))
    lo = max(row["lower"] for row in available); hi = min(row["upper"] for row in available)
    if lo>hi:
        raise ArithmeticError("Independent sound secant bounds had an empty intersection")
    target = I(lo, hi)-econ.action_grad(I(action))
    return dict(u=[float(state[0]), float(state[1]), float(v)], action=float(action),
        action_hex=float(action).hex(), normalized_probe_radius=PROBE_H, original_action_probe_radius=float(step),
        original_action_derivative_lower=float(lo), original_action_derivative_upper=float(hi),
        continuation_marginal_lower=float(target.lo), continuation_marginal_upper=float(target.hi),
        secant_bounds=available, original_action_curvature_lower=2,
        original_action_gradient_Lipschitz_lower=float(la.lo), original_action_gradient_Lipschitz_upper=float(la.hi),
        exact_compiler_gradient_used=False, compiler_support_slope_is_not_a_derivative_label=True)


def acquire_labels(budget, alpha, sink=None):
    if budget not in (5,9) or alpha not in (.5,.75):
        raise ValueError("Only the prospectively declared designs are permitted")
    started, before = time.perf_counter(), econ.COUNTS.copy()
    knots = [i/(budget-1) for i in range(budget)]
    states = [[x0,x1] for x0 in knots for x1 in knots]
    probes = sorted(set([v for knot in V_KNOTS for v in (knot-PROBE_H,knot,knot+PROBE_H) if 0<=v<=1]))
    if len(probes)!=13:
        raise ArithmeticError("The paid fixed-probe census must be thirteen per state")
    values, marginals, anchors = [], [], []
    for row, state in enumerate(states):
        by_v = {}
        for v in probes:
            result = value_probe(state, v, alpha, sink)
            result.update(state_grid_row=row, probe_row=len(values)+len(by_v))
            by_v[v] = result
        base = I(by_v[0.]["q_lower"], by_v[0.]["q_upper"])
        anchors.append(dict(state=state, lower=float(base.lo), upper=float(base.hi)))
        for v in probes:
            result = by_v[v]
            target = I(result["q_lower"],result["q_upper"])-base-econ.action_cost(I(result["action"]))
            # The same original Q at exactly the same zero-action key cancels.
            if v==0:
                target = I(0)
            result.update(continuation_difference_lower=float(target.lo), continuation_difference_upper=float(target.hi),
                          anchor_identity_cancellation=v==0)
            values.append(result)
        for v in V_KNOTS:
            result = derivative_label(state,v,by_v,alpha)
            result.update(state_grid_row=row, marginal_row=len(marginals))
            marginals.append(result)
            emit(sink,"marginal-label-complete",**result)
        emit(sink,"state-grid-labels-complete",row=row,state=state,paid_contexts=len(probes))
    constants = smoothness_rational(alpha)
    return dict(kind="r121-original-root-value-and-marginal-labels", budget=budget, alpha=alpha,
        state_grid=states, state_knots=knots, normalized_action_main_knots=list(V_KNOTS),
        normalized_action_probes=probes, values=values, marginals=marginals,
        anchor=dict(state_knots=knots, rows=anchors,
                    q0_midpoints=[(row["lower"]+row["upper"])/2 for row in anchors],
                    interpolation="tensor bilinear", state_only_gauge_cancels_from_actor=True),
        original_root_Q_contexts=len(values), main_marginal_contexts=len(marginals),
        counts=inherited.base.counter_delta(before), seconds=time.perf_counter()-started,
        smoothness_rational={k:dict(numerator=v.numerator,denominator=v.denominator) for k,v in constants.items()},
        no_economic_law_discretization=True, no_heldout_states_used=True,
        every_family_gets_identical_complete_payload=True,
        future_controller_unchanged="terminal_controller94.terminal_policy, downward 40-bit observations, uniform 2^-20 allowance in policy evaluation only")


@contextmanager
def trace_certificates(sink):
    """Record complete primitive payloads and every paid production attempt."""
    old = quad.certificate
    old_terminal = quad.terminal_certificate
    old_query = cont.float_query
    def terminal(states, alpha):
        emit(sink,"qualification-terminal-start",states=states,alpha=alpha)
        answer=old_terminal(states,alpha)
        emit(sink,"qualification-terminal-complete",payload=answer)
        return answer
    def float_query(x,action,alpha,fit,n=128):
        answer=old_query(x,action,alpha,fit,n)
        emit(sink,"online-proposal-query",state=x,action=action,alpha=alpha,
             midpoints=n,proposal_value=answer[0],proposal_derivative=answer[1],
             proposal_only_not_original_value_certificate=True)
        return answer
    def certificate(x, action, alpha, bins=128):
        emit(sink,"qualification-certificate-start",state=x,action=action,alpha=alpha,bins=bins)
        rec = old(x,action,alpha,bins)
        emit(sink,"qualification-certificate-complete",certificate=rec)
        return rec
    quad.certificate = certificate
    quad.terminal_certificate = terminal
    cont.float_query = float_query
    try:
        yield
    finally:
        quad.certificate = old
        quad.terminal_certificate = old_terminal
        cont.float_query = old_query


def partial_scientific_frames(exc):
    """Retain failed root/piece/certificate work, including pre-return locals."""
    answer=inherited.partial_scientific_frames(exc);tb=exc.__traceback__
    wanted={"state","x","alpha","v","action","proposed","rec","first","attempts",
            "pieces","candidates","values","breaks","roots","record","left","right","mid",
            "theta","low","high","lower_risk","upper_risk","middle","endpoint","available",
            "result","raw","theta_raw","design","labels","index","row"}
    while tb is not None:
        frame=tb.tb_frame
        if Path(frame.f_code.co_filename).name in {"models121.py","labels121.py","campaign121.py"}:
            variables={}
            for name in sorted(wanted & set(frame.f_locals)):
                value=frame.f_locals[name]
                try:
                    converted=inherited.plain(value);json.dumps(converted,allow_nan=False)
                    variables[name]=converted
                except (TypeError,ValueError,OverflowError):
                    variables[name]={"representation":repr(value)}
            answer.append(dict(file=frame.f_code.co_filename,function=frame.f_code.co_name,
                               line=tb.tb_lineno,scientific_locals=variables))
        tb=tb.tb_next
    return answer


def exact_fallback(state,alpha,sink):
    """Execute the inherited proved finite cover, retaining every action cover row.

Any failure here is fatal; this helper is never recursively retried. The
unchanged primitive owns its fixed 1025-action, 256-cell, 80-step bounds.
"""
    import rational96 as rational
    old=rational.exact_cost
    def cost(x,a,risk,bins):
        emit(sink,"exact-cover-action-start",state=x,action=a,alpha=risk,bins=bins)
        answer=old(x,a,risk,bins)
        emit(sink,"exact-cover-action-complete",state=x,action=a,alpha=risk,bins=bins,
             original_policy_lower=answer[0],original_policy_upper=answer[1])
        econ.count("r121_exact_cover_action_contexts",1)
        return answer
    rational.exact_cost=cost
    try:
        return rational.exact_service(state,alpha)
    finally:
        rational.exact_cost=old


def service(state, alpha, model, sink=None):
    """The same original-law completed service for every fixed learned actor."""
    started,before = time.perf_counter(),econ.COUNTS.copy()
    import models121 as models
    state = np.asarray(state,float)
    if state.shape!=(2,) or alpha not in (.5,.75) or np.any(~np.isfinite(state)) or np.any((state<0)|(state>1)):
        raise ValueError("Population calls are singleton original states")
    if model is not None:
        desc=model["basis"]
        if (model.get("kind")!="r121-anchored-root-critic" or desc!=models.definition(desc["arm"],desc["budget"]) or
            len(model["theta"])!=desc["feature_count"] or np.any(~np.isfinite(model["theta"])) or
            np.any(np.asarray(model["theta"])<np.asarray(desc["coefficient_lower"])) or
            np.any(np.asarray(model["theta"])>np.asarray(desc["coefficient_upper"]))):
            raise ValueError("A valid frozen declared critic is required; corrupt model errors abort")
    x = state[None,:]
    attempts=[]; clock=dict(first_proposal=0.,first_certificate=0.,conventional_fallback=0.,refinement=0.,exact_fallback=0.)
    actor_trace=None;proposed=None;first=None;rejected=True;numerical_failure=None;exact=False;bins=128
    try:
        try:
            with kern.backend(True), trace_certificates(sink):
                tp=time.perf_counter()
                if model is None:
                    emit(sink,"online-original-proposal-start",state=state,alpha=alpha,midpoints=512,iterations=24)
                    candidate=float(cont.actor(x,alpha,None,n=512,iterations=24)[0])
                    actor_trace=dict(rule="original semi-analytic continuous-risk midpoint proposal",midpoints=512,
                        derivative_iterations=24,original_optimizer_claim=False,action=candidate,action_hex=candidate.hex())
                else:
                    candidate,actor_trace=models.actor(model,state)
                    candidate=min(candidate,float(np.floor(econ.capacity(I(x)).lo[0]*2**30)/2**30))
                    econ.count("r121_learned_action_piece_visits",actor_trace["action_piece_count"])
                    econ.count("r121_learned_action_root_candidates",actor_trace["polynomial_root_count"])
                    econ.count("r121_learned_action_value_evaluations",actor_trace["evaluated_proposal_count"])
                if not np.isfinite(candidate) or candidate<0 or candidate>float(econ.capacity(I(x)).lo[0]):
                    raise ArithmeticError("The numerical proposal did not supply a finite feasible action")
                proposed=float(candidate);clock["first_proposal"]=time.perf_counter()-tp
                actor_trace.update(returned_feasible_action=proposed,returned_feasible_action_hex=proposed.hex())
                emit(sink,"first-proposal-complete",actor_trace=actor_trace)
                action=np.array([proposed]);tc=time.perf_counter()
                rec=quad.certificate(x,action,alpha,128);clock["first_certificate"]=time.perf_counter()-tc
                first={key:float(rec[key][0]) for key in KEYS}
                rejected=not bool(quad.qualifies(rec)[0])
                attempts.append(dict(stage="first",action=proposed,bins=128,qualified=not rejected,certificate=first))
                if rejected:
                    tf=time.perf_counter()
                    emit(sink,"conventional-fallback-start",original_first_proposal=proposed,first_certificate=first)
                    action=cont.actor(x,alpha,None,n=512,iterations=24)
                    rec=quad.certificate(x,action,alpha,128)
                    attempts.append(dict(stage="conventional-fallback",action=float(action[0]),bins=128,
                        qualified=bool(quad.qualifies(rec)[0]),certificate={key:float(rec[key][0]) for key in KEYS}))
                    clock["conventional_fallback"]=time.perf_counter()-tf
                    econ.count("r121_conventional_fallback_rows",1)
                for next_bins in (256,512,1024,2048,4096):
                    if bool(quad.qualifies(rec)[0]):break
                    tr=time.perf_counter();rec=quad.certificate(x,action,alpha,next_bins)
                    bins=next_bins;clock["refinement"]+=time.perf_counter()-tr
                    attempts.append(dict(stage="integration-refinement",action=float(action[0]),bins=bins,
                        qualified=bool(quad.qualifies(rec)[0]),certificate={key:float(rec[key][0]) for key in KEYS}))
                need_exact=not bool(quad.qualifies(rec)[0])
        except (ArithmeticError,np.linalg.LinAlgError) as exc:
            # Only recoverable numerical errors are totalized. Domain/model,
            # source identity, I/O and infrastructure exceptions still abort.
            numerical_failure=dict(exception_type=type(exc).__name__,exception=str(exc),
                traceback=traceback.format_exc(),partial_scientific_frames=partial_scientific_frames(exc),
                feasible_first_proposal_already_existed=proposed is not None,
                elapsed_pre_recovery_seconds=time.perf_counter()-started,
                counts_before_recovery=inherited.base.counter_delta(before))
            clock["failed_numerical_work_before_exact_recovery"]=time.perf_counter()-started
            attempts.append(dict(stage="numerical-failure",action=proposed,qualified=False,
                                 certificate=first,failure=numerical_failure))
            emit(sink,"recoverable-numerical-failure",failure=numerical_failure)
            econ.count("r121_recoverable_numerical_failure_rows",1)
            need_exact=True
        if need_exact:
            te=time.perf_counter();emit(sink,"exact-fallback-start",state=state,alpha=alpha)
            a,lo,hi,opt,n=exact_fallback(state,alpha,sink)
            action=np.array([a]);rec=dict(lower=np.array([lo]),upper=np.array([hi]),
                optimum_lower=np.array([opt]),loss=np.array([float(up(hi-opt))]),width=np.array([float(up(hi-lo))]))
            bins=n;exact=True;clock["exact_fallback"]=time.perf_counter()-te
            attempts.append(dict(stage="exact-fallback",action=float(a),bins=int(n),
                qualified=bool(quad.qualifies(rec)[0]),certificate={key:float(rec[key][0]) for key in KEYS}))
            econ.count("r121_exact_fallback_rows",1)
        if not bool(quad.qualifies(rec)[0]):raise ArithmeticError("Original-policy completion failed closed")
        final=float(action[0]);loss=float(rec["loss"][0])
        row=dict(state=state.tolist(),state_hex=[float(v).hex() for v in state],
            action=final,action_hex=final.hex(),first_proposal_action=proposed,
            first_proposal_action_hex=None if proposed is None else proposed.hex(),
            first_rejected=bool(rejected),first_proposal_changed=None if proposed is None else final!=proposed,
            first_rejection_scope="a first proposal not accepted, including numerical proposal/certificate failure; reasons retained separately",
            numerical_service_failure=numerical_failure is not None,
            proposal_numerical_failure=proposed is None and numerical_failure is not None,
            numerical_failure=numerical_failure,
            first_proposal_certificate=first,qualified=True,bins=int(bins),exact_fallback=exact,
            complete_policy_lower=float(rec["lower"][0]),complete_policy_upper=float(rec["upper"][0]),
            original_optimum_lower=float(rec["optimum_lower"][0]),
            certified_regret_upper=loss,
            action_distance_upper=float(up(np.sqrt(loss))),action_distance_quantity_is_bound_not_actual_error=True,
            future_error_allowance=econ.TERMINAL_TOL,future_controller="unchanged terminal_controller94.terminal_policy with downward 40-bit state observations",
            clock=clock,qualification_attempts=len(attempts),
            fitted_actor_is_proposal_only=True,training_loss_is_not_a_policy_certificate=True,
            **{key:float(rec[key][0]) for key in KEYS})
        for key in KEYS:
            row["first_"+key]=None if first is None else first[key]
        emit(sink,"service-complete",row=row,attempts=attempts,counts=inherited.base.counter_delta(before))
        row.update(seconds=time.perf_counter()-started,counts=inherited.base.counter_delta(before))
        return dict(row=row,attempts=attempts,actor_trace=actor_trace,
                    seconds=row["seconds"],counts=row["counts"])
    except BaseException as exc:
        evidence=dict(state=state.tolist(),alpha=alpha,attempts=attempts,actor_trace=actor_trace,
                      counts=inherited.base.counter_delta(before),seconds=time.perf_counter()-started,
                      partial_scientific_frames=partial_scientific_frames(exc))
        emit(sink,"service-failed",evidence=evidence,exception_type=type(exc).__name__,exception=str(exc))
        exc.evidence121=inherited.plain(evidence)
        raise
