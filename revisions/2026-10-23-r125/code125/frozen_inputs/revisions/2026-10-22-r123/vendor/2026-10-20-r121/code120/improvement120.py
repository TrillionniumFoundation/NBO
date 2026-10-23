"""Paid original-policy changes using action-scaled paired continuation quadrature.

Scientific imports are intentional. The campaign must verify its remote source
freeze before importing this module. No fitting objective or future controller
is changed. The old compiled-safe comparator is called without source changes.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from fractions import Fraction
import math
import resource
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "frozen108/code108"))
sys.path.insert(0, str(ROOT / "code119"))
import campaign108 as base
import kernel108 as kern
import represent108 as rep
import continuum94 as cont
import quadrature96 as quad
import investment94 as econ
from interval94 import I, up, down
import budgeted_tail119 as tail

SERVICES = ("completed", "legacy-safe", "paired", "direct-refine")
LADDER = (2, 4, 8, 16, 32, 64)
FRACTIONS = (1.0, 0.5, 0.25)
KEYS = ("lower", "upper", "optimum_lower", "loss", "width")
R = 1 / 32


def plain(value):
    if isinstance(value, np.ndarray):
        return plain(value.tolist())
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        return plain(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonfinite_float": repr(value)}
    if isinstance(value, Fraction):
        return {"fraction_numerator": value.numerator, "fraction_denominator": value.denominator}
    if isinstance(value, I):
        return {"interval_lower": plain(value.lo), "interval_upper": plain(value.hi)}
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value


def partial_scientific_frames(exc):
    """Retain actual scientific locals if a solver fails before returning its log."""
    wanted = {"trials", "selected", "independent_choices", "records", "receipts",
              "x", "lab", "kind", "step", "j", "alpha", "bins", "n",
              "actions", "candidate", "loss", "values", "rec", "payload"}
    files = {"study97.py", "represent108.py", "kernel108.py", "investment94.py",
             "rational96.py", "campaign120.py", "improvement120.py"}
    answer, tb = [], exc.__traceback__
    while tb is not None:
        frame = tb.tb_frame
        if Path(frame.f_code.co_filename).name in files:
            variables = {}
            for name in sorted(wanted & set(frame.f_locals)):
                value = frame.f_locals[name]
                if isinstance(value, (str, int, float, bool, type(None), dict, list,
                                      tuple, np.ndarray, np.generic, I, Fraction)):
                    try:
                        converted = plain(value)
                        # A record may contain an optimizer object. Do not lose
                        # the otherwise recoverable failure evidence to it.
                        import json
                        json.dumps(converted, allow_nan=False)
                        variables[name] = converted
                    except (TypeError, ValueError):
                        variables[name] = {"representation": repr(value)}
            answer.append(dict(file=frame.f_code.co_filename, function=frame.f_code.co_name,
                               line=tb.tb_lineno, scientific_locals=variables))
        tb = tb.tb_next
    return answer


def emit(sink, event, **payload):
    if sink is not None:
        sink(dict(event=event, **plain(payload)))


def validate(x, actions, alpha):
    x, actions = np.asarray(x, float), np.asarray(actions, float)
    if x.ndim != 2 or x.shape[1] != 2 or actions.shape != (len(x),) or not len(x):
        raise ValueError("The proved R120 mixed modulus is restricted to d=2")
    if alpha not in (0.5, 0.75) or not np.all(np.isfinite(x)) or not np.all(np.isfinite(actions)):
        raise ValueError("Original finite state/action/risk identity required")
    if np.any((x < 0) | (x > 1)) or np.any(actions < 0) or np.any(actions > econ.capacity(I(x)).lo):
        raise ValueError("An original feasible action is required")
    return x, actions


def modulus(alpha):
    """Outward original d=2 Lipschitz gradient constant, not a fitted modulus."""
    a = I(alpha)
    return I(1413) / 128 + (I(15) / 16) * (I(127) / 16 + I(19625) * a / (I(20480) * (1-a)))


def rational_sqrt_upper(value):
    """Exact integer-square-root construction of a dyadic upper bound.

    No floating sqrt is assumed to enclose a real square root. The final
    binary64 conversion is checked against its exact Fraction before use.
    """
    values = np.asarray(value, float)
    if not np.all(np.isfinite(values)) or np.any(values < 0):
        raise ValueError("A finite nonnegative upper bound is required")
    out = np.empty_like(values)
    for index, val in np.ndenumerate(values):
        f = Fraction(float(val))
        scaled = f.numerator << 80
        root = math.isqrt(scaled // f.denominator)
        if root * root * f.denominator < scaled:
            root += 1
        bound = Fraction(root, 2**40)
        v = float(bound)
        if Fraction(v) < bound:
            v = float(up(v))
        if Fraction(v)**2 < f:
            raise ArithmeticError("Exact dyadic square-root upper check failed")
        out[index] = v
    econ.count("r120_tail_transfer_integer_sqrt_calls", values.size)
    return out


def _tail_density(x, incumbent, candidate, alpha, sink):
    """Candidate-proposed common feasible density, with BOTH original slacks."""
    emit(sink, "tail-density-start", state=x, incumbent=incumbent,
         candidate=candidate, alpha=alpha)
    state = tail.tail_state(x, candidate, alpha)
    cut = state["cut"]
    z = np.stack([cut, cut + alpha / 16], axis=-1)
    values = kern.compiled_certificate(econ.transition(I(x), I(incumbent), I(z)), alpha)
    derivative = I(values["lower"][:, 1], values["upper"][:, 1]) - I(values["lower"][:, 0], values["upper"][:, 0])
    # Both factors and this product are exactly representable binary rationals.
    gap = tail.constrained_gain(derivative, tail.MZ * (alpha / 16), cut, -R, R-alpha/16)
    direct_kappa = (I(gap) / (I(2*R) * (1-I(alpha)))).hi
    separation = I(candidate)-I(incumbent)
    absolute_separation = np.maximum(np.abs(separation.lo), np.abs(separation.hi))
    E = (I(4)/5)*modulus(alpha)*I(absolute_separation)
    transfer_factor = (I(alpha)/(I(2*tail.MZ)*(1-I(alpha)))).hi
    transferred_kappa = (I(rational_sqrt_upper(state["kappa"]))+
                         E*I(rational_sqrt_upper(transfer_factor))).square().hi
    incumbent_kappa = np.minimum(direct_kappa, transferred_kappa)
    econ.count("r120_incumbent_tail_residual_point_values", 2 * len(x))
    state.update(incumbent=incumbent.copy(), incumbent_kappa=incumbent_kappa,
                 incumbent_direct_kappa=direct_kappa,
                 incumbent_transferred_kappa=transferred_kappa,
                 incumbent_transfer_active=transferred_kappa < direct_kappa,
                 action_modulus_upper=E.hi,
                 incumbent_derivative_lower=derivative.lo,
                 incumbent_derivative_upper=derivative.hi)
    econ.count("r120_tail_transfer_bounds", len(x))
    econ.count("r120_tail_transfer_active", int(np.sum(transferred_kappa < direct_kappa)))
    emit(sink, "tail-density-complete", density=state,
         incumbent_endpoint_lower=values["lower"], incumbent_endpoint_upper=values["upper"])
    return state


def paired_certificate(x, incumbent, candidate, alpha, m, density, old_optimum, sink=None):
    """Enclose J(candidate)-J(incumbent) and qualify the actual candidate policy.

The fixed-density continuation difference need not be convex. Its Lipschitz
midpoint bound is intersected with the separately valid convex bounds for the
two continuations. Terminal-controller error is added exactly once as +/-beta
epsilon. A density acquired for another action pair cannot be reused.
"""
    x, incumbent = validate(x, incumbent, alpha)
    _, candidate = validate(x, candidate, alpha)
    if not (density["alpha"] == alpha and np.array_equal(density["x"], x)
            and np.array_equal(density["action"], candidate)
            and np.array_equal(density["incumbent"], incumbent)):
        raise ValueError("A paired cache cannot cross state, action or risk identities")
    m = int(m)
    if m not in LADDER:
        raise ValueError("Only the prospectively fixed paired resolution ladder is allowed")
    started = time.perf_counter()
    mids, edges, weights = tail.tail_mesh(density["cut"], alpha, m)
    n, d = x.shape
    positive = np.stack([weights[:, 0] > 0, weights[:, m] > 0], axis=1)
    mmask = np.repeat(positive, m, axis=1)
    emask = np.repeat(positive, m+1, axis=1)
    mr, mc = np.nonzero(mmask)
    er, ec = np.nonzero(emask)
    owners = np.concatenate([mr, er])
    nodes = np.concatenate([mids[mr, mc], edges[er, ec]])
    nm, ne, npair = len(mr), len(er), len(owners)
    # Both action payloads are purchased. No competitor is denied these nodes;
    # each standalone service pays all of its requested rows and duplicates.
    actions = np.concatenate([incumbent[owners], candidate[owners]])
    joint_owners = np.tile(owners, 2)
    joint_nodes = np.tile(nodes, 2)
    emit(sink, "paired-payload-start", m=m, state=x, incumbent=incumbent,
         candidate=candidate, owners=owners, nodes=nodes, midpoint_rows=mr,
         midpoint_columns=mc, endpoint_rows=er, endpoint_columns=ec,
         purchased_terminal_rows=2*npair)
    payload = kern.compiled_certificate(
        econ.transition(I(x[joint_owners]), I(actions), I(joint_nodes[:, None])), alpha)
    lo, hi = payload["lower"][:, 0], payload["upper"][:, 0]
    midlo, midhi, endhi, slopeslo, slopeshi = [], [], [], [], []
    for side in range(2):
        off = side * npair
        ml, mh = np.zeros((n, 2*m)), np.zeros((n, 2*m))
        eh = np.zeros((n, 2*(m+1)))
        sl, sh = np.zeros((n, 2*m, d)), np.zeros((n, 2*m, d))
        ml[mr, mc] = lo[off:off+nm]
        mh[mr, mc] = hi[off:off+nm]
        eh[er, ec] = hi[off+nm:off+npair]
        sl[mr, mc, :] = payload["slope"].lo[off:off+nm, 0, :]
        sh[mr, mc, :] = payload["slope"].hi[off:off+nm, 0, :]
        midlo.append(ml); midhi.append(mh); endhi.append(eh)
        slopeslo.append(sl); slopeshi.append(sh)
    weighted_mid = [(I(midlo[k], midhi[k]) * I(weights)).sum() for k in range(2)]
    lower_mid = [(I(midlo[k]) * I(weights)).sum() for k in range(2)]
    upper_secant = []
    for eh in endhi:
        left = np.concatenate([eh[:, :m], eh[:, m+1:2*m+1]], axis=-1)
        right = np.concatenate([eh[:, 1:m+1], eh[:, m+2:2*m+2]], axis=-1)
        upper_secant.append((((I(left)+I(right))/2)*I(weights)).sum())
    convex_lo = (lower_mid[1] - upper_secant[0]).lo
    convex_hi = (upper_secant[1] - lower_mid[0]).hi
    paired_mid = weighted_mid[1] - weighted_mid[0]
    left_len = (I(density["cut"]) + R) / m
    right_len = (I(R) - I(density["cut"]) - I(alpha)/16) / m
    # Sum h_i^2/(4*tail_length), computed outward from dyadic geometry.
    mean_radius = (I(m) * (left_len.square()+right_len.square()) /
                   (I(4) * I(2*R) * (1-I(alpha))))
    E = I(density["action_modulus_upper"])
    error = E * mean_radius
    paired_lo, paired_hi = (paired_mid-error).lo, (paired_mid+error).hi
    integral_lo = np.maximum(convex_lo, paired_lo)
    integral_hi = np.minimum(convex_hi, paired_hi)
    if np.any(integral_lo > integral_hi):
        raise ArithmeticError("Contradictory independently valid paired integral enclosures")
    # Factoring cancels the common stage cost algebraically and avoids subtracting
    # large, identical state costs in floating arithmetic.
    cost_difference = ((I(candidate)-I(incumbent)) * (I(candidate)+I(incumbent)) *
                       (1 + 4*(I(candidate).square()+I(incumbent).square())))
    risk_difference = I(integral_lo, integral_hi) + I(-density["incumbent_kappa"], density["kappa"])
    actual_difference = cost_difference + econ.BETA*(risk_difference + I(-econ.TERMINAL_TOL, econ.TERMINAL_TOL))
    stage = econ.S(I(x)) + econ.action_cost(I(candidate))
    witness = stage + econ.BETA * lower_mid[1]
    upper = stage + econ.BETA * (upper_secant[1] + I(density["kappa"]) + econ.TERMINAL_TOL)
    b, _ = econ.exposures(d)
    slope = econ.action_grad(I(candidate)) + econ.BETA*((I(slopeslo[1], slopeshi[1])*b).sum()*I(weights)).sum()
    optimum = econ.quadratic_minimum_lower(I(witness.lo), slope, I(candidate), econ.capacity(I(x)))
    optimum = np.maximum(optimum, old_optimum)
    rec = dict(lower=witness.lo, upper=upper.hi, optimum_lower=optimum,
               loss=up(upper.hi-optimum), width=up(upper.hi-witness.lo))
    if np.any(rec["loss"] < 0) or np.any(rec["width"] < 0):
        raise ArithmeticError("Contradictory original policy qualification")
    result = dict(candidate_certificate=rec,
                  difference_lower=actual_difference.lo, difference_upper=actual_difference.hi,
                  integral_lower=integral_lo, integral_upper=integral_hi,
                  convex_integral_lower=convex_lo, convex_integral_upper=convex_hi,
                  paired_integral_lower=paired_lo, paired_integral_upper=paired_hi,
                  action_modulus_upper=E.hi, midpoint_error_upper=error.hi,
                  paired_lower_active=paired_lo > convex_lo,
                  paired_upper_active=paired_hi < convex_hi,
                  incumbent_tail_transfer_active=density["incumbent_transfer_active"],
                  m=m, purchased_terminal_rows=2*npair,
                  maximum_terminal_gap=float(np.max(payload["gap"])),
                  seconds=time.perf_counter()-started)
    econ.count("r120_paired_terminal_rows", 2*npair)
    econ.count("r120_paired_midpoint_terminal_rows", 2*nm)
    econ.count("r120_paired_endpoint_terminal_rows", 2*ne)
    econ.count("r120_paired_certificates", n)
    econ.count("r120_paired_compiler_calls", 1)
    emit(sink, "paired-payload-complete", lower=lo, upper=hi,
         slope_lower=payload["slope"].lo[:, 0, :], slope_upper=payload["slope"].hi[:, 0, :],
         result=result)
    return result


@contextmanager
def audit_legacy(sink):
    """Keep every paid legacy proposal/certificate attempt, including failures.

The wrapped routines and returned arrays are unchanged. Recording time is part
of measured service time, with the same event sink used for every service.
"""
    original_certificate, original_query, original_proposal = quad.certificate, cont.query, rep.proposal
    def certificate(x, actions, alpha, bins=128):
        emit(sink, "legacy-certificate-start", state=np.asarray(x), action=np.asarray(actions), alpha=alpha, bins=bins)
        result = original_certificate(x, actions, alpha, bins)
        emit(sink, "legacy-certificate-complete", certificate=result)
        return result
    def query(x, actions, alpha, fit=None, n=128):
        emit(sink, "legacy-support-start", state_lower=x.lo, state_upper=x.hi,
             action_lower=actions.lo, action_upper=actions.hi, alpha=alpha, n=n)
        result = original_query(x, actions, alpha, fit, n)
        emit(sink, "legacy-support-complete", lower=result["lower"], upper=result["upper"],
             witness_lower=result["witness"].lo, witness_upper=result["witness"].hi,
             slope_lower=result["gradient"].lo, slope_upper=result["gradient"].hi)
        return result
    def proposal(x, alpha, model):
        emit(sink, "legacy-proposal-start", state=np.asarray(x), alpha=alpha)
        result = original_proposal(x, alpha, model)
        emit(sink, "legacy-proposal-complete", action=result)
        return result
    quad.certificate, cont.query, rep.proposal = certificate, query, proposal
    try:
        yield
    finally:
        quad.certificate, cont.query, rep.proposal = original_certificate, original_query, original_proposal


def _records(data):
    return ({key: np.array([row[key] for row in data["rows"]]) for key in KEYS},
            np.array([row["action"] for row in data["rows"]]))


def _density_subset(density, ids):
    return {key: value[ids] if isinstance(value, np.ndarray) else value for key, value in density.items()}


def service(x, alpha, model, name, sink=None):
    if name not in SERVICES:
        raise ValueError("Undeclared R120 service")
    x = np.asarray(x, float)
    validate(x, np.zeros(len(x)), alpha)
    started, before = time.perf_counter(), econ.COUNTS.copy()
    trace = dict(service=name, state=x.tolist(), alpha=alpha, trials=[])
    try:
        with audit_legacy(sink):
            data = base.complete_service(x, alpha, model, compiled=True, safe=name=="legacy-safe")
        rec, actions = _records(data)
        baseline = {k: np.array([row["baseline_"+k] for row in data["rows"]]) for k in KEYS}
        original_actions = np.array([row["completed_baseline_action"] for row in data["rows"]])
        gains = np.zeros(len(x))
        changes = np.zeros(len(x), int)
        final_tail_resolution = np.zeros(len(x), int)
        if name == "legacy-safe":
            for trial in data["trials"]:
                if trial["accepted"]:
                    j = trial["row"]
                    g = (I(trial["incumbent_lower"])-I(trial["candidate_upper"])).lo
                    gains[j] = (I(gains[j])+I(g)).lo
                    changes[j] += 1
            trace["trials"] = data["trials"]
        elif name in ("paired", "direct-refine"):
            with kern.backend(True):
                fractions = FRACTIONS if name=="paired" else (None,)
                for trial, fraction in enumerate(fractions):
                    ts = time.perf_counter()
                    emit(sink, "improvement-proposal-start", trial=trial, service=name, incumbent=actions)
                    if name == "paired":
                        support = cont.query(I(x), I(actions), alpha, None, 128)
                        cap = econ.capacity(I(x)).lo
                        step = np.clip(actions-support["gradient"].mid()/2, 0, cap)
                        candidate = np.floor((actions+fraction*(step-actions))*2**30)/2**30
                        candidate = np.minimum(candidate, np.floor(cap*2**30)/2**30)
                        proposal = dict(slope_lower=support["gradient"].lo,
                                        slope_upper=support["gradient"].hi, fraction=fraction,
                                        slope_is_fixed_feasible_minorant=True)
                    else:
                        candidate = cont.actor(x, alpha, None, n=512, iterations=24)
                        proposal = dict(original_midpoints=512, derivative_bisections=24,
                                        proposal_is_not_an_exact_original_optimizer=True)
                    emit(sink, "improvement-proposal-complete", trial=trial, candidate=candidate,
                         proposal=proposal, seconds=time.perf_counter()-ts)
                    entering_actions = actions.copy()
                    pending = np.flatnonzero(candidate != actions)
                    for j in np.flatnonzero(candidate == actions):
                        row = dict(row=int(j), trial=trial, fraction=fraction,
                                   incumbent_action=float(actions[j]), candidate_action=float(candidate[j]),
                                   accepted=False, reason="exact identical action", difference_lower=0.,
                                   difference_upper=0., no_new_density_or_point_query=True)
                        trace["trials"].append(row); emit(sink, "trial-finished", **row)
                    if not len(pending):
                        continue
                    density = _tail_density(x[pending], actions[pending], candidate[pending], alpha, sink)
                    local_pending = np.arange(len(pending))
                    for m in LADDER:
                        if not len(local_pending):
                            break
                        ids = pending[local_pending]
                        result = paired_certificate(x[ids], actions[ids], candidate[ids], alpha, m,
                            _density_subset(density, local_pending), rec["optimum_lower"][ids], sink)
                        fresh = result["candidate_certificate"]
                        qualified = quad.qualifies(fresh)
                        accepted = (result["difference_upper"] < 0) & qualified
                        certified_worse = result["difference_lower"] >= 0
                        exhausted = m == LADDER[-1]
                        stop = accepted | certified_worse | exhausted
                        for k, j in enumerate(ids):
                            row = dict(row=int(j), trial=trial, fraction=fraction, m=m,
                                incumbent_action=float(actions[j]), candidate_action=float(candidate[j]),
                                difference_lower=float(result["difference_lower"][k]),
                                difference_upper=float(result["difference_upper"][k]),
                                qualified=bool(qualified[k]), accepted=bool(accepted[k]),
                                certified_not_better=bool(certified_worse[k]),
                                exhausted=bool(exhausted and not (accepted[k] or certified_worse[k])),
                                paired_lower_active=bool(result["paired_lower_active"][k]),
                                paired_upper_active=bool(result["paired_upper_active"][k]),
                                incumbent_tail_transfer_active=bool(result["incumbent_tail_transfer_active"][k]),
                                midpoint_error_upper=float(result["midpoint_error_upper"][k]),
                                action_modulus_upper=float(result["action_modulus_upper"][k]),
                                **{"candidate_"+key: float(fresh[key][k]) for key in KEYS})
                            trace["trials"].append(row)
                            emit(sink, "paired-trial-resolution", **row)
                            if accepted[k]:
                                gain = float(down(-result["difference_upper"][k]))
                                gains[j] = float((I(gains[j])+I(gain)).lo)
                                actions[j] = candidate[j]
                                changes[j] += 1
                                final_tail_resolution[j] = m
                                for key in KEYS:
                                    rec[key][j] = fresh[key][k]
                        local_pending = local_pending[~stop]
                    if np.any((actions != entering_actions) & (gains <= 0)):
                        raise ArithmeticError("Changed action lacks a positive original-policy gain certificate")
        if not np.all(quad.qualifies(rec)):
            raise ArithmeticError("A completed original policy failed qualification")
        for j, row in enumerate(data["rows"]):
            incumbent_bins = int(row["bins"])
            tail_final = final_tail_resolution[j] > 0
            final_bins = int(final_tail_resolution[j]) if tail_final else (128 if changes[j] else incumbent_bins)
            row.update(state=x[j].tolist(), state_hex=[v.hex() for v in x[j]],
                       action=float(actions[j]), action_hex=float(actions[j]).hex(),
                       completed_incumbent_action=float(original_actions[j]),
                       certified_gain_lower=float(max(0., gains[j])),
                       accepted_steps=int(changes[j]), safe_changes=int(changes[j]), qualified=True,
                       completed_incumbent_bins=incumbent_bins,
                       completed_incumbent_exact_fallback=bool(row["exact_fallback"]),
                       final_certificate_kind="paired-tail" if tail_final else "whole-support",
                       final_certificate_resolution=final_bins,
                       final_certificate_resolution_unit="cells per positive tail" if tail_final else "whole-support cells",
                       bins=None if tail_final else final_bins,
                       complete_policy_lower=float(rec["lower"][j]),
                       complete_policy_upper=float(rec["upper"][j]),
                       original_optimum_lower=float(rec["optimum_lower"][j]),
                       action_distance_upper=float(up(np.sqrt(rec["loss"][j]))))
            for key in KEYS:
                row[key] = float(rec[key][j])
                row["baseline_"+key] = float(baseline[key][j])
            if actions[j] == original_actions[j]:
                if changes[j]:
                    raise ArithmeticError("A strict positive-gain sequence cannot return to its original action")
                row["certified_gain_lower"] = 0.
            if row["certified_gain_lower"] < 0:
                raise ArithmeticError("Invalid nonnegative improvement guarantee")
            if row["certified_gain_lower"] > float(baseline["loss"][j]):
                raise ArithmeticError("Certified gain exceeds the completed incumbent's original regret ceiling")
        data.update(service=name, trials=trace["trials"], seconds=time.perf_counter()-started,
                    counts=base.counter_delta(before), future_controller="terminal_controller94.terminal_policy with downward 40-bit observations",
                    future_error_allowance=econ.TERMINAL_TOL,
                    stage_clock_scope="inherited clock contains incumbent work; total seconds includes all new work and audit recording",
                    max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        emit(sink, "service-complete", service=name, counts=data["counts"], seconds=data["seconds"])
        return data
    except BaseException as exc:
        trace.update(status="failed", exception_type=type(exc).__name__, exception=str(exc),
                     counts=base.counter_delta(before), seconds=time.perf_counter()-started,
                     partial_scientific_frames=partial_scientific_frames(exc))
        emit(sink, "service-failed", trace=trace)
        exc.evidence120 = plain(trace)
        raise
