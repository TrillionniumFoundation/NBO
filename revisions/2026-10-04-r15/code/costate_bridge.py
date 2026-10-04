"""Protected R15 occupation-law Bellman bridge, on the declared finite grid.

This is an independent post-selection assessment, never a training or stopping
input.  The candidate's torch proposal, inward action guard, polynomial drift,
and clipped innovation recurrence match actor_verifier.verify.  The reference
derivative is for ONE fixed global finite-grid Bellman continuation.  A coarse
critic is an arbitrary fixed predictor on that assessment grid.

Population clipping ranges come from parameter-derived bounds and Gaussian
concentration.  Saved per-observation intervals enclose numerical sample error;
they are not empirical population bounds.  The reported payoff endpoint uses
the existing quantitative diffusion payoff transfer, not a costate bias guess.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
R15 = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import training_core as core
import actor_verifier as verifier
from method_statistics import ConfidenceBudget, empirical_bernstein

pc, torch = core.legacy.pc, core.torch
import tube_certificate as tc
I = pc.I
STATISTICS = ("M", "A", "E", "D", "E_raw", "E_minus_raw")
TANH_ERROR = 2.0**-34


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n")


def seed_for(seed, dimension, purpose):
    key = f"NBO-R15-mechanism-v1/{seed}/{dimension}/{purpose}"
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")


def iu(value):
    return float(value.hi) if isinstance(value, I) else float(pc.up(value))


def il(value):
    return float(value.lo) if isinstance(value, I) else float(pc.down(value))


def isqrt(value):
    """Outward nonnegative square root, including subnormal lower endpoints.

    The historical endpoint checker assumes its positive lower square is
    resolvable. Widening a tiny lower endpoint to zero avoids that unnecessary
    assumption. Exact zero upper endpoints have exact zero square roots.
    """
    x = value if isinstance(value, I) else I(value)
    lo, hi = np.maximum(0., x.lo), np.maximum(0., x.hi)
    zero = hi == 0
    lower = np.where((lo < 1e-100) | zero, 0., lo)
    upper = np.where(zero, 1., np.maximum(1e-100, hi))
    result = tc.sqrt_i(I(lower, upper))
    return I(np.where(zero, 0., result.lo), np.where(zero, 0., result.hi))


def norm_upper(value, axis=-1):
    z = value if isinstance(value, I) else I(value)
    return isqrt(pc.mean_i(z.square(), axis=axis)).hi


def norm_float(value):
    return np.sqrt(np.mean(np.asarray(value)**2, axis=-1))


def radii(value):
    center = pc.midpoint(value)
    return center, np.maximum(pc.up(center-value.lo), pc.up(value.hi-center))


def column(value):
    return I(value.lo[:, None], value.hi[:, None])


def imat(value, weight):
    """Outward value @ exact_binary64_weight.T; rectangular matrices allowed."""
    x = value if isinstance(value, I) else I(value)
    w = np.asarray(weight, dtype=np.float64)
    if x.lo.ndim != 2 or w.ndim != 2 or x.lo.shape[1] != w.shape[1]:
        raise ValueError("interval matrix shape mismatch")
    return pc.sum_axis(I(x.lo[:, None, :], x.hi[:, None, :])*I(w[None, :, :]), axis=-1)


def tanh_interval(value):
    x = value if isinstance(value, I) else I(value)
    lower = pc.down(pc.safe_tanh(x.lo)-TANH_ERROR)
    upper = pc.up(pc.safe_tanh(x.hi)+TANH_ERROR)
    return I(np.maximum(-1., lower), np.minimum(1., upper))


def verified_norm(weight):
    """An SVD proposal is accepted only after the inherited interval LDL test."""
    w = np.asarray(weight, dtype=np.float64)
    if w.ndim == 1:
        return dict(norm_upper=iu(isqrt(pc.sum_axis(I(w).square()))),
                    proof="outward sum of exact coefficient squares")
    n = max(w.shape)
    padded = np.zeros((n, n))
    padded[:w.shape[0], :w.shape[1]] = w
    result = tc.spectral_bound(padded)
    result["original_shape"] = list(w.shape)
    return result


class ProtectedCritic:
    """Exact spatial scalar lift and its normalized derivative, enclosed.

    The time-only network and noise-variance constant cancel identically in
    every action difference, and have zero spatial derivative.  They need not
    be numerically evaluated.  All saved coefficients denote exact real input.
    """
    def __init__(self, critic, params):
        if critic.kind != "postdecision":
            raise ValueError("bridge assessment requires a postdecision critic")
        layers = [m for m in critic.space.modules() if isinstance(m, torch.nn.Linear)]
        if len(layers) != 3:
            raise ValueError("unsupported scalar spatial architecture")
        self.weights = [m.weight.detach().cpu().numpy().copy() for m in layers]
        self.biases = [m.bias.detach().cpu().numpy().copy() for m in layers]
        self.d, self.params = critic.d, dict(params)
        self.gamma = 2*I(params["CHI"])*pc.exp_i(-I(params["discount"])*I(params["T"]))
        self.norms = [verified_norm(self.weights[0][:, 1:]),
                      verified_norm(self.weights[1]), verified_norm(self.weights[2].ravel())]
        l1, l2, l3 = [I(x["norm_upper"]) for x in self.norms]
        self.residual_gradient_rate = iu(l1*l2*l3/isqrt(I(self.d)))
        self.hessian_rate = iu(l3*l1.square()*(l2.square()+l2))

    def jet(self, dates, x):
        """Return spatial value, q=d*Dx(value), with interval sample enclosures."""
        y = x if isinstance(x, I) else I(np.asarray(x, dtype=np.float64))
        t = np.asarray(dates, dtype=np.float64).reshape(-1)
        if len(t) != len(y.lo):
            raise ValueError("critic dates and rows differ")
        tx = I(np.column_stack((t, y.lo)), np.column_stack((t, y.hi)))
        w1, w2, w3 = self.weights
        b1, b2, b3 = self.biases
        a1 = tanh_interval(imat(tx, w1)+I(b1))
        a2 = tanh_interval(imat(a1, w2)+I(b2))
        spatial = imat(a2, w3)+I(b3)
        v2 = (1-a2.square())*I(w3)
        v1 = imat(v2, w2.T)*(1-a1.square())
        dx = imat(v1, w1[:, 1:].T)
        centered = y-column(pc.mean_i(y, axis=1))
        tau = I(self.params["T"])-I(t[:, None])
        value = -self.gamma/2*column(pc.mean_i(centered.square(), axis=1))+tau*spatial/self.d
        q = -self.gamma*centered+tau*dx
        return value, q

    def as_dict(self):
        return dict(spectral_proofs=self.norms,
                    residual_gradient_rate=self.residual_gradient_rate,
                    normalized_hessian_rate=self.hessian_rate,
                    terminal_costate_coefficient=[il(self.gamma), iu(self.gamma)],
                    scalar_definition="quadratic terminal lift + (T-s)*space_MLP(s,x)/d; time constants cancel")


def global_account(d, steps, epsilon, support, wt, payoff_account, net, params, pairs=2, vstar=8.):
    """Outward statistical ranges and small numerical representation accounts."""
    p, h = params, I(params["T"])/steps
    T, kappa, sigma_i = I(p["T"]), I(p["coupling"]), I(p["idiosyncratic_sigma"])
    sigma_c, eta = I(p["common_sigma"]), I(p["adjustment"])
    B = core.old.coupling(d)
    spectral = tc.spectral_bound(B)
    bnorm = I(spectral["norm_upper"])
    beta = kappa*bnorm
    gamma = net.gamma
    times = np.arange(steps)*(p["T"]/steps)
    tail_times = p["T"]-(times+p["T"]/steps)
    # Exponentials are an upper bound on the finite Jacobian product.
    F = pc.exp_i(beta*I(tail_times))
    s0 = max(x["initial_spread_upper"] for x in payoff_account["components"])
    sd = isqrt(I(d-1))
    pi = pc.midpoint(wt["M"])/(p["T"]/steps)
    guard_lo = pc.up(wt["center"].hi-epsilon)
    guard_hi = pc.down(wt["center"].lo+epsilon)
    if np.any(pi < guard_lo) or np.any(pi > guard_hi):
        raise ValueError("reference outside declared actor action box")
    lower, upper = np.minimum(guard_lo, pi), np.maximum(guard_hi, pi)
    delta = max(float(np.max((I(lower)-I(pi)).absmax())),
                float(np.max((I(upper)-I(pi)).absmax())))
    diameter = float(np.max((I(upper)-I(lower)).hi))
    c0 = I(p["productivity"])-(sigma_i.square()+sigma_c.square())/2
    drift_size = I(max(float((c0-I(float(lower.min()))).absmax()),
                      float((c0-I(float(upper.max()))).absmax())))+kappa

    # Deterministic enclosure is used ONLY in tiny arithmetic cushions.
    cap = 4*(I(float(np.max(np.abs(support))))+drift_size*T
             +(sigma_i+sigma_c)*10*T/isqrt(h)+1)
    row_abs = I(float(pc.sum_axis(I(np.abs(B)), axis=1).hi.max()))
    row_l2 = I(float(isqrt(pc.sum_axis(I(B).square(), axis=1)).hi.max()))
    dot_error = I(pc.gamma(d+2))*cap*row_abs
    ferr = kappa*(I(TANH_ERROR)+dot_error)
    ferr = ferr+I(pc.gamma(8))*(I(float(c0.absmax()))+kappa+I(float(upper.max())))
    noise_cap = (sigma_i+sigma_c)*10*isqrt(h)
    step_error = h*ferr+I(pc.gamma(32))*(cap+h*drift_size+noise_cap)
    step_error = step_error+16*np.finfo(float).eps*noise_cap
    path_error = steps*step_error*pc.exp_i(beta*T)
    if iu(path_error) >= 1:
        raise ArithmeticError("mechanism state-roundoff bootstrap failed")
    bridge_error = (1+h*beta)*path_error+2*step_error+I(pc.gamma(16))*(cap+h*drift_size)
    df_error = beta*(row_l2*isqrt(I(d))*path_error+dot_error
                     +2*TANH_ERROR+I(pc.gamma(5))*I(1+TANH_ERROR).square())
    # |B| spectral norm is bounded by its (outward) Frobenius norm.
    abs_b_norm = isqrt(pc.sum_axis(pc.sum_axis(I(B).square(), axis=1)))
    hessian_f = kappa*bnorm.square()
    all_flow = pc.exp_i(beta*T)
    total_b = pc.sum_axis(wt["B"])
    # Derivative of a vector flow has ordinary Euclidean second-derivative
    # bound H_f*T*exp(2 beta T). Multiplication by d is recorded explicitly.
    q_lipschitz = hessian_f*all_flow.square()*total_b*(1+beta*isqrt(I(d))*T)
    q_lipschitz = q_lipschitz+gamma*all_flow.square()*(1+isqrt(I(d))*cap*hessian_f*T)
    qhat_lipschitz = gamma+T*I(net.hessian_rate)
    representation_root = isqrt(T)*(q_lipschitz+qhat_lipschitz)*bridge_error
    m_representation = T*I(delta)*qhat_lipschitz*(1+h*beta)*path_error
    d_representation = T*I(diameter)*qhat_lipschitz*(1+h*beta)*path_error

    # A rigorous improvement to ||Df^T 1|| <= beta exploits s in [0,1]^d.
    gram = I(np.zeros((d, d)))
    for j in range(d):
        gram = gram+I(B[:, j, None])*I(B[None, :, j])
    positive_gram_sum = pc.sum_axis(pc.sum_axis(I(np.maximum(gram.hi, 0.)), axis=1))
    cube_bound = kappa*isqrt(positive_gram_sum/d)
    beta_production = min(iu(beta), iu(cube_bound))
    adjoint_production = np.zeros(steps)
    running = I(0.)
    for k in range(steps-2, -1, -1):
        running = I(beta_production)*I(wt["B"].lo[k+1], wt["B"].hi[k+1])+(1+h*beta)*running
        adjoint_production[k] = iu(running)

    ctheta = I(tail_times)*I(net.residual_gradient_rate)
    prefix_size = I(s0)+(kappa+I(epsilon))*T+bridge_error
    sigma_scale = sigma_i/isqrt(I(d))
    troot = isqrt(I(times))
    future_root = isqrt(I(p["T"]-times))
    cz = I(adjoint_production)+gamma*F*kappa*I(tail_times)
    cz = cz+gamma*(F-1)*(prefix_size+sigma_scale*(troot+future_root)*sd)
    atail = gamma*(F-1)*sigma_scale*(troot+future_root/isqrt(I(pairs)))
    CE, CZ, AE = float((ctheta+cz).hi.max()), float(cz.hi.max()), float(atail.hi.max())
    CE, CZ, AE = max(0., CE), max(0., CZ), max(0., AE)
    exp_tail = pc.exp_i(-I(vstar).square()/2)
    bE = T*(I(CE)+I(AE)*vstar).square()
    tauE = 6*T*I(AE)*exp_tail*(I(CE)/vstar+I(AE))
    bR = 2*T*(I(CZ)+I(AE)*vstar).square()
    tauR = 12*T*I(AE)*exp_tail*(I(CZ)/vstar+I(AE))

    grad_lo = wt["A"]/h*(1/I(lower)-eta*I(lower))-wt["B"]/h
    grad_hi = wt["A"]/h*(1/I(upper)-eta*I(upper))-wt["B"]/h
    ell_lipschitz = max(float(grad_lo.absmax().max()), float(grad_hi.absmax().max()))
    Ctheta = float(ctheta.hi.max())
    CM = T*I(delta)*(I(ell_lipschitz)+I(Ctheta)+gamma*(prefix_size+sigma_i*isqrt(T/I(d))*sd))
    AM = T*I(delta)*gamma*sigma_i*isqrt(T/I(d))
    bM, tauM = CM+AM*vstar, AM*exp_tail/vstar
    normalized_hessian = I(tail_times)*I(net.hessian_rate)
    curvature = h.square()*normalized_hessian-wt["A"]/I(upper).square()
    gamma_k = curvature.hi.copy()  # each is an exact chosen upper-bound coefficient
    mu = float((-I(gamma_k)/h).lo.min())
    gamma_plus = max(0., float((I(gamma_k)/h).hi.max()))
    CD = T*I(diameter)*(I(ell_lipschitz)+I(Ctheta)+gamma*(prefix_size+sigma_i*isqrt(T/I(d))*sd))
    CD = CD+T*I(gamma_plus)*I(diameter).square()/2
    AD = T*I(diameter)*gamma*sigma_i*isqrt(T/I(d))
    bD, tauD = CD+AD*vstar, AD*exp_tail/vstar
    hold = pc.sum_axis(wt["C"]-wt["A"]*pc.log_i(I(pi))+wt["B"]*I(pi)+eta*wt["A"]*I(pi).square()/2)
    if float(hold.hi) < 0:
        raise ArithmeticError("holding-deficit enclosure contradicts pointwise optimality")
    bounds = dict(M=iu(bM), A=iu(T*I(delta).square()), E=iu(bE), D=iu(bD),
                  E_raw=iu(bR), E_minus_raw=iu(bE+bR))
    tails = dict(M=iu(tauM), A=0., E=iu(tauE), D=iu(tauD),
                 E_raw=iu(tauR), E_minus_raw=iu(tauE+tauR))
    result = dict(dimension=d, assessment_steps=steps, h=iu(h), epsilon=epsilon,
        reference_action=pi.tolist(), guard_lower=guard_lo.tolist(), guard_upper=guard_hi.tolist(),
        maximum_action_distance=delta, maximum_action_box_diameter=diameter,
        beta=iu(beta), beta_production=beta_production, coupling_spectral_proof=spectral,
        critic=net.as_dict(), normalized_hessian_upper=normalized_hessian.hi.tolist(),
        action_curvature_upper=gamma_k.tolist(), strong_concavity_verified=mu>0,
        strong_concavity_modulus_lower=max(0., mu),
        C_E=CE, C_Z=CZ, A_E=AE, tail_v=vstar, antithetic_pairs_per_bank=pairs,
        ranges=bounds, clipping_expectation_allowances=tails,
        holding_deficit_interval=[max(0., il(hold)), max(0., iu(hold))],
        holding_deficit_upper=max(0., iu(hold)),
        holding_weights_scope="exact integrated A,B,C enclosed outward; pi uses fixed midpoint(M)/h; full scalar numerical account retained in paired payoff transfer",
        payoff_transfer_upper=payoff_account["bias_upper"], anchor_regret_upper=payoff_account["anchor_upper"],
        arithmetic=dict(state_cap=iu(cap), one_step_state_error=iu(step_error),
            accumulated_state_error=iu(path_error), bridge_state_error=iu(bridge_error),
            drift_jacobian_error=iu(df_error), absolute_coupling_norm_upper=iu(abs_b_norm),
            true_costate_lipschitz_upper=iu(q_lipschitz), critic_costate_lipschitz_upper=iu(qhat_lipschitz),
            risk_representation_root_allowance=iu(representation_root),
            predicted_gain_representation_allowance=iu(m_representation),
            actor_gap_representation_allowance=iu(d_representation),
            contract="Inherited binary64/ideal-Gaussian-input contract; protected polynomial tanh/log, verified coefficient norms, interval neural jets, and proved adjoint sample error. RNG and hardware are not machine-formally verified."),
        state_cap_role="arithmetic only; never substituted for the Gaussian statistical range")
    return result


def candidate_occupation(actor, support, nodes, seed, params, wt, counters):
    """Same guarded policy and internal state recurrence as actor_verifier."""
    n, d, steps = len(nodes), support.shape[1], len(wt["A"].lo)
    h, B = params["T"]/steps, core.old.coupling(d)
    initial_rng = np.random.default_rng(seed["initial_profile"])
    initial_ids = initial_rng.integers(len(support), size=n)
    y = support[initial_ids].copy()
    out, actions = np.zeros_like(y), np.zeros_like(y)
    lo = pc.up(wt["center"].hi-actor.epsilon)
    hi = pc.down(wt["center"].lo+actor.epsilon)
    rng = np.random.default_rng(seed["occupation_innovations"])
    noise_hash = hashlib.sha256()
    c0 = params["productivity"]-(params["idiosyncratic_sigma"]**2+params["common_sigma"]**2)/2
    maximum = float(np.max(np.abs(y)))
    for k in range(steps):
        tx = np.column_stack((np.full(n, k*h), y))
        with torch.no_grad():
            proposal = actor(torch.from_numpy(tx)).detach().cpu().numpy()
        if proposal.shape != (n, d) or not np.isfinite(proposal).all():
            raise FloatingPointError("invalid frozen candidate proposal")
        action = np.maximum(lo[k], np.minimum(hi[k], proposal))
        take = nodes == k
        out[take], actions[take] = y[take], action[take]
        production = params["coupling"]*pc.safe_tanh(y@B.T)
        z = rng.standard_normal((n, d+1))
        noise_hash.update(z.tobytes())
        z = np.clip(z, -10., 10.)
        dw = math.sqrt(h)*(params["idiosyncratic_sigma"]*z[:, :d]+params["common_sigma"]*z[:, d:])
        y = y+h*(c0+production-action)+dw
        maximum = max(maximum, float(np.abs(y).max()))
    counters["candidate_simulator_transitions"] += n*steps
    counters["actor_forward_rows"] += n*steps
    return out, actions, initial_ids, noise_hash.hexdigest(), maximum


def reference_path(x, nodes, innovations, params, wt, account, counters):
    """One protected finite-continuation derivative and its normalized error.

    Reverse vector-Jacobian recursion uses scalar time-only reference actions.
    No d-by-d state Jacobian is stored. Padded inactive arithmetic is disclosed.
    Error propagation uses each computed q norm and a global proved drift
    Jacobian error, never an empirical population bound.
    """
    n, d = x.shape
    steps, h = len(wt["A"].lo), params["T"]/len(wt["A"].lo)
    B = core.old.coupling(d)
    Bmid, Brad = pc.midpoint(wt["B"]), pc.radius(wt["B"])
    pi = pc.midpoint(wt["M"])/h
    beta = account["beta"]
    arith = account["arithmetic"]
    gamma_i = 2*I(params["CHI"])*pc.exp_i(-I(params["discount"])*I(params["T"]))
    gamma_mid = float(pc.midpoint(gamma_i))
    c0 = params["productivity"]-(params["idiosyncratic_sigma"]**2+params["common_sigma"]**2)/2
    noise = lambda z: math.sqrt(h)*(params["idiosyncratic_sigma"]*z[:, :d]+params["common_sigma"]*z[:, d:])
    y = x+noise(innovations[0])
    # Only tanh values, rather than full autograd graphs, are retained.
    max_offsets = int(steps-int(nodes.min()))
    activation = np.empty((max_offsets, n, d), dtype=np.float64)
    for offset in range(1, max_offsets):
        j = nodes+offset
        active = j < steps
        jj = np.minimum(j, steps-1)
        tanh_value = pc.safe_tanh(y@B.T)
        activation[offset] = tanh_value
        candidate = y+h*(c0+params["coupling"]*tanh_value-pi[jj, None])+noise(innovations[offset])
        y = np.where(active[:, None], candidate, y)
    centered_i = I(y)-column(pc.mean_i(I(y), axis=1))
    q_i = -gamma_i*centered_i
    q = -gamma_mid*(y-y.mean(axis=1, keepdims=True))
    q_round = I(q)-q_i
    error = (I(norm_upper(q_round))+gamma_i*I(arith["accumulated_state_error"])).hi
    round_factor = pc.gamma(d+24)
    absolute_beta = I(params["coupling"])*I(arith["absolute_coupling_norm_upper"])
    for offset in range(max_offsets-1, 0, -1):
        j = nodes+offset
        active = j < steps
        jj = np.minimum(j, steps-1)
        qnorm = norm_upper(I(q))
        s = 1-activation[offset]*activation[offset]
        temp = (h*q+Bmid[jj, None])*(params["coupling"]*s)
        next_q = q+temp@B
        qnorm_i, h_i = I(qnorm), I(h)
        local_round = I(round_factor)*(qnorm_i+absolute_beta*(h_i*qnorm_i+I(np.abs(Bmid[jj])))*(1+4*I(TANH_ERROR)))
        # The error recurrence itself uses outward interval operations.  The
        # absolute term exceeds gradual-underflow contributions to this fixed
        # d<=50 dot/update graph; relative gamma bounds cover normal results.
        next_error = (1+h_i*I(beta))*I(error)
        next_error = next_error+(h_i*qnorm_i+I(wt["B"].hi[jj]))*I(arith["drift_jacobian_error"])
        next_error = next_error+I(beta)*I(Brad[jj])+local_round+I(1e-24)
        next_error = next_error.hi
        q = np.where(active[:, None], next_q, q)
        error = np.where(active, next_error, error)
    if not np.isfinite(q).all() or not np.isfinite(error).all():
        raise FloatingPointError("nonfinite protected reference adjoint")
    if float(np.abs(y).max()) > arith["state_cap"]:
        raise ArithmeticError("reference arithmetic enclosure exceeded")
    counters["reference_simulator_transitions"] += int((steps-nodes).sum())
    counters["reference_rollout_starts"] += n
    counters["reference_padded_transition_rows"] += n*max_offsets
    counters["reverse_vector_jacobian_rows"] += int((steps-nodes-1).sum())
    return q, error


def reference_bank(x, nodes, seed, params, wt, account, pairs, counters):
    n, d, steps = len(nodes), x.shape[1], len(wt["A"].lo)
    rng, noise_hash = np.random.default_rng(seed), hashlib.sha256()
    targets, errors = [], []
    for _ in range(pairs):
        z = rng.standard_normal((steps, n, d+1))
        counters["reference_standard_normal_draws"] += steps*n*(d+1)
        noise_hash.update(z.tobytes())
        z = np.clip(z, -10., 10.)
        for sign in [1., -1.]:
            if sign < 0:
                z = -z
            q, err = reference_path(x, nodes, z, params, wt, account, counters)
            targets.append(q)
            errors.append(err)
    target = np.mean(targets, axis=0)
    norm_array = np.asarray([norm_upper(I(q)) for q in targets]).T
    error_array = np.asarray(errors).T
    round_error = I(pc.gamma(2*pairs+4))*pc.mean_i(I(norm_array), axis=1)
    error = (pc.mean_i(I(error_array), axis=1)+round_error).hi
    return target, error, noise_hash.hexdigest()


def quadratic_support(g, action, lower, upper, curvature):
    """Interval enclosure of the exact box quadratic-support gap."""
    grad = g if isinstance(g, I) else I(g)
    a, lo, hi = I(action), I(lower[:, None]), I(upper[:, None])
    gamma = np.asarray(curvature, dtype=float)
    output_lo, output_hi = np.empty(len(action)), np.empty(len(action))
    for negative in [False, True]:
        mask = (gamma < 0) == negative
        if not mask.any():
            continue
        gi = I(grad.lo[mask], grad.hi[mask])
        ai = I(a.lo[mask], a.hi[mask])
        left = I(lo.lo[mask], lo.hi[mask])-ai
        right = I(hi.lo[mask], hi.hi[mask])-ai
        gam = I(gamma[mask, None])
        if negative:
            v = gi/(-gam)
            vl = np.maximum(left.lo, np.minimum(right.lo, v.lo))
            vh = np.maximum(left.hi, np.minimum(right.hi, v.hi))
            point = I(vl, vh)
            result = pc.mean_i(gi*point+gam*point.square()/2, axis=1)
        else:
            lval = gi*left+gam*left.square()/2
            rval = gi*right+gam*right.square()/2
            result = pc.mean_i(I(np.maximum(lval.lo, rval.lo), np.maximum(lval.hi, rval.hi)), axis=1)
        output_lo[mask], output_hi[mask] = np.maximum(0., result.lo), np.maximum(0., result.hi)
    return I(output_lo, output_hi)


def interval_statistics(y, action, nodes, uniform, params, wt, net, account, target1, target2):
    """Enclose exact represented-state samples, with separately saved shift."""
    n, d = y.shape
    steps, h = len(wt["A"].lo), params["T"]/len(wt["A"].lo)
    A = I(wt["A"].lo[nodes], wt["A"].hi[nodes])
    Bweight = I(wt["B"].lo[nodes], wt["B"].hi[nodes])
    pi = pc.midpoint(wt["M"])[nodes]/h
    B = core.old.coupling(d)
    c0 = I(params["productivity"])-(I(params["idiosyncratic_sigma"]).square()+I(params["common_sigma"]).square())/2
    production = I(params["coupling"])*tanh_interval(imat(I(y), B))
    xp = I(y)+h*(c0+production-I(pi[:, None]))
    xa = I(y)+h*(c0+production-I(action))
    dates = (nodes+1)*h
    va, qa = net.jet(dates, xa)
    vp, _ = net.jet(dates, xp)
    mean_action = pc.mean_i(I(action), axis=1)
    # Consumption log is enclosed by the proved log polynomial.
    log_action = I(pc.down(pc.safe_log(action)-TANH_ERROR), pc.up(pc.safe_log(action)+TANH_ERROR))
    stage = A*(pc.mean_i(log_action, axis=1)-pc.log_i(I(pi)))
    stage = stage-Bweight*(mean_action-I(pi))
    stage = stage-params["adjustment"]*A*(mean_action.square()-I(pi).square())/2
    mstat = steps*(stage+I(va.lo[:, 0], va.hi[:, 0])-I(vp.lo[:, 0], vp.hi[:, 0]))
    astat = params["T"]*pc.mean_i((I(action)-I(pi[:, None])).square(), axis=1)
    # The reference paths start from this exact disclosed binary64 point.
    xpm, xam = pc.midpoint(xp), pc.midpoint(xa)
    bridge = xpm+uniform[:, None]*(xam-xpm)
    _, qb = net.jet(dates, bridge)
    qhat, qrad = radii(qb)
    qhat_err = norm_upper(I(qrad))
    z1, e1 = target1
    z2, e2 = target2
    err1, err2 = I(qhat)-I(z1), I(qhat)-I(z2)
    # Dot products themselves are enclosed by the inherited interval kernel.
    cross = params["T"]*pc.mean_i(err1*err2, axis=1)
    eta1, eta2 = I(qhat_err)+I(e1), I(qhat_err)+I(e2)
    cross_radius = (I(params["T"])*(eta1*I(norm_upper(err2))+eta2*I(norm_upper(err1))+eta1*eta2)).hi
    estat = I(pc.down(cross.lo-cross_radius), pc.up(cross.hi+cross_radius))
    diff = I(z1)-I(z2)
    raw = params["T"]/2*pc.mean_i(diff.square(), axis=1)
    total_error = I(e1)+I(e2)
    raw_radius = (I(params["T"])*(I(norm_upper(diff))*total_error+total_error.square()/2)).hi
    rstat = I(np.maximum(0., pc.down(raw.lo-raw_radius)), pc.up(raw.hi+raw_radius))
    econtrast = estat-rstat
    grad = column(A)*(1/I(action)-params["adjustment"]*column(mean_action))-column(Bweight)-h*qa
    gap = quadratic_support(grad, action, np.asarray(account["guard_lower"])[nodes],
                            np.asarray(account["guard_upper"])[nodes],
                            np.asarray(account["action_curvature_upper"])[nodes])
    stats = dict(M=mstat, A=astat, E=estat, D=steps*gap, E_raw=rstat, E_minus_raw=econtrast)
    extras = dict(bridge=bridge, qhat=qhat, qhat_radius=qrad,
                  approximate_q_advantage=pc.midpoint(mstat)/steps,
                  actor_gap=pc.midpoint(gap), state=y, action=action,
                  reference_action=pi, postdecision_a=xam, postdecision_pi=xpm)
    return stats, extras


def interval_empirical_bernstein(lower, upper, *, bound, event_alpha, clipping_tail=0.):
    """EB for unknown exact samples enclosed by observed numerical intervals.

    Projection contracts the centered Euclidean norm. Consequently replacing
    the exact clipped samples by interval midpoints changes their mean by at
    most mean(radius), and their sample SD by at most sqrt(n/(n-1))*RMS(radius).
    This is a sample-moment enclosure, not a data-dependent population bias.
    """
    lo, hi = np.asarray(lower, float), np.asarray(upper, float)
    if lo.shape != hi.shape or lo.ndim != 1 or len(lo) < 2 or np.any(lo > hi):
        raise ValueError("invalid sample intervals")
    if not np.isfinite(lo).all() or not np.isfinite(hi).all():
        raise ValueError("nonfinite sample intervals")
    lo, hi = np.clip(lo, -bound, bound), np.clip(hi, -bound, bound)
    mid = (lo+hi)/2
    radius = np.maximum(pc.up(mid-lo), pc.up(hi-mid))
    answer = empirical_bernstein(mid, bound=bound, event_alpha=event_alpha,
                                 clipping_tail=clipping_tail)
    if bound == 0:
        answer.update(lower=-clipping_tail, upper=clipping_tail,
            mean=0., clipped_mean=0., variance=0., empirical_bernstein_margin=0.,
            sample_moment_arithmetic_cushion=0.,
            sample_moment_scope="exact zero clipping range; only the declared expectation tail remains")
        return answer
    ell = pc.log_i(I(4.)/I(event_alpha))
    cushion = pc.mean_i(I(radius))+isqrt(2*ell/(len(mid)-1))*isqrt(pc.mean_i(I(radius).square()))
    answer["lower"] = il(I(answer["lower"])-cushion)
    answer["upper"] = iu(I(answer["upper"])+cushion)
    answer["sample_moment_arithmetic_cushion"] = iu(cushion)
    answer["sample_moment_scope"] = "interval enclosure of exact clipped observations, including variance perturbation; not an empirical population range"
    return answer


def evaluate(protocol_path, checkpoint, trial_id, out):
    started = time.perf_counter()
    protocol_path, checkpoint, out = Path(protocol_path), Path(checkpoint), Path(out)
    protocol = json.loads(protocol_path.read_text())
    match = re.fullmatch(r"d(\d+)_s(\d+)", trial_id)
    if match is None:
        raise ValueError("invalid trial id")
    d, seed = map(int, match.groups())
    if d not in protocol["dimensions"] or seed not in protocol["declared_seeds"]:
        raise ValueError("undeclared mechanism stream")
    steps, n = protocol["assessment_steps"], protocol["bridges_per_stream"]
    if steps != 2048 or n != 256 or protocol["future_banks"] != 2 or protocol["antithetic_pairs_per_bank"] != 2:
        raise ValueError("mechanism protocol differs from the frozen design")
    out.mkdir(parents=True, exist_ok=True)
    if (out/"BRIDGE.json").exists() or (out/"BRIDGE.npz").exists():
        raise ValueError("refusing to overwrite mechanism outcomes")
    actor, critic, state = core.load_candidate(checkpoint, critic_step=1/steps)
    if state["dimension"] != d or state["seed"] != seed or state["method_id"] != "nbo":
        raise ValueError("selected checkpoint does not identify this NBO stream")
    if state["primitives_sha256"] != protocol["primitives_sha256"]:
        raise ValueError("mechanism and selected policy economies differ")
    params, primitive_sha = verifier.bind_primitives(protocol["primitives"])
    if primitive_sha != protocol["primitives_sha256"]:
        raise ValueError("primitive fingerprint mismatch")
    source = os.environ.get("NBO_R15_NUMERICAL_SOURCE_COMMIT", "uncommitted-development")
    metadata = dict(schema="nbo-r15-protected-bridge-v1", trial_id=trial_id, dimension=d,
        stream_seed=seed, method_id="nbo", method_fingerprint=state.get("method_fingerprint"),
        selected_source_commit=state.get("source_commit"), numerical_source_commit=source,
        candidate_source_commit=state.get("source_commit"), candidate_sha256=sha(checkpoint),
        assessment_fingerprint=os.environ.get("NBO_R15_ASSESSMENT_FINGERPRINT", "uncommitted-development"),
        selected_checkpoint_sha256=sha(checkpoint), protocol_sha256=sha(protocol_path),
        primitives_sha256=primitive_sha, N_train=state.get("N_train"), N_audit=steps,
        paths=n, future_banks=2, rollouts_per_bank=4,
        inference_scope="one descriptive stratum of the complete prespecified 16-stream pooled mechanism; no per-stream inference",
        noise_independent_of_selection_and_primary_confirmation=True)
    fallback = bool(getattr(actor, "is_analytical_schedule", False))
    counters = defaultdict(int)
    support = verifier.population(d)
    wt, payoff = verifier.account(d, steps, state["epsilon"], support)
    if fallback:
        arrays = {key+suffix:np.zeros(n) for key in STATISTICS for suffix in ["", "_lower", "_upper"]}
        np.savez_compressed(out/"BRIDGE.npz", **arrays)
        row = dict(metadata, complete=True, analytic_schedule_fallback=True,
            ranges={key:0. for key in STATISTICS}, clipping_expectation_allowances={key:0. for key in STATISTICS},
            constants=dict(holding_deficit_upper=0., payoff_transfer_upper=0., anchor_regret_upper=payoff["anchor_upper"],
                           strong_concavity_verified=False, strong_concavity_modulus_lower=0.,
                           arithmetic=dict(risk_representation_root_allowance=0.,
                              predicted_gain_representation_allowance=0.,actor_gap_representation_allowance=0.)),
            deterministic_gain=0., counters=dict(counters), seconds=time.perf_counter()-started,
            fallback_scope=protocol["fallback_rule"], raw_path="BRIDGE.npz", raw_sha256=sha(out/"BRIDGE.npz"))
        write(out/"BRIDGE.json", row)
        return row
    if critic is None:
        raise ValueError("nonfallback NBO checkpoint lacks its fitted scalar critic")
    net = ProtectedCritic(critic, params)
    account = global_account(d, steps, state["epsilon"], support, wt, payoff, net, params)
    constants_seconds = time.perf_counter()-started
    seeds = {purpose:seed_for(seed, d, purpose) for purpose in protocol["randomness_purposes"]}
    nodes = np.random.default_rng(seeds["uniform_node"]).integers(steps, size=n)
    uniform = np.random.default_rng(seeds["uniform_bridge"]).random(n)
    y, action, initial_ids, occupation_hash, maximum = candidate_occupation(actor, support, nodes, seeds, params, wt, counters)
    # Construct the disclosed reference-query points in exactly the same way
    # as interval_statistics, with outward x means before taking their centers.
    h, B = params["T"]/steps, core.old.coupling(d)
    pi = pc.midpoint(wt["M"])[nodes]/h
    c0 = I(params["productivity"])-(I(params["idiosyncratic_sigma"]).square()+I(params["common_sigma"]).square())/2
    production = params["coupling"]*tanh_interval(imat(I(y), B))
    xp, xa = I(y)+h*(c0+production-I(pi[:, None])), I(y)+h*(c0+production-I(action))
    xpm, xam = pc.midpoint(xp), pc.midpoint(xa)
    bridge = xpm+uniform[:, None]*(xam-xpm)
    z1, e1, hash1 = reference_bank(bridge, nodes, seeds["future_bank_1"], params, wt, account, 2, counters)
    z2, e2, hash2 = reference_bank(bridge, nodes, seeds["future_bank_2"], params, wt, account, 2, counters)
    stats, extras = interval_statistics(y, action, nodes, uniform, params, wt, net, account, (z1, e1), (z2, e2))
    if not np.array_equal(bridge, extras["bridge"]):
        raise AssertionError("reference and critic bridge points differ")
    if maximum > account["arithmetic"]["state_cap"]:
        raise ArithmeticError("candidate arithmetic enclosure exceeded")
    arrays = dict(nodes=nodes, bridge_uniform=uniform, initial_profile=initial_ids,
        bank1=z1, bank2=z2, bank1_normalized_error=e1, bank2_normalized_error=e2, **extras)
    for key, interval in stats.items():
        arrays[key], arrays[key+"_lower"], arrays[key+"_upper"] = pc.midpoint(interval), interval.lo, interval.hi
    np.savez_compressed(out/"BRIDGE.npz", **arrays)
    numerical_widths = {key:dict(maximum=float((stats[key].hi-stats[key].lo).max()),
                               mean=float((stats[key].hi-stats[key].lo).mean())) for key in STATISTICS}
    row = dict(metadata, complete=True, analytic_schedule_fallback=False,
        ranges=account["ranges"], clipping_expectation_allowances=account["clipping_expectation_allowances"],
        constants=account, numerical_interval_widths=numerical_widths,
        descriptive_means={key:float(arrays[key].mean()) for key in STATISTICS},
        raw_path="BRIDGE.npz", raw_sha256=sha(out/"BRIDGE.npz"),
        source_files={name:sha(Path(__file__).parent/name) for name in ["costate_bridge.py", "training_core.py", "actor_verifier.py", "method_statistics.py"]},
        noise_seeds=seeds, noise_key=f"NBO-R15-mechanism-v1/{seed}/{d}",
        occupation_noise_sha256=occupation_hash, future_bank_sha256=[hash1, hash2],
        initial_profile_sha256=hashlib.sha256(initial_ids.tobytes()).hexdigest(),
        bridge_sha256=hashlib.sha256(bridge.tobytes()).hexdigest(),
        counters=dict(counters), constants_seconds=constants_seconds, seconds=time.perf_counter()-started,
        payoff_scope="continuous original economy only after pooled Bellman bridge and saved paired payoff transfer",
        raw_costate_scope="antithetic4 evaluation-subproblem risk on the same NBO represented occupation queries; not Raw actor welfare",
        arithmetic_scope="saved intervals enclose exact represented-query samples; additional state-representation shift is saved separately for the welfare bridge")
    write(out/"BRIDGE.json", row)
    return row


def pool(records, protocol):
    """Complete balanced finite-stream intervals and continuous gain endpoint."""
    budget = ConfidenceBudget(protocol["confidence"]["alpha"], protocol["confidence"]["event_count"])
    output = dict(schema="nbo-r15-pooled-bridge-v1", confidence=budget.as_dict(), dimensions={})
    fingerprints = {r.get("assessment_fingerprint") for r in records}
    sources = {r.get("numerical_source_commit") for r in records}
    protocol_hashes = {r.get("protocol_sha256") for r in records}
    if len(fingerprints) != 1 or len(sources) != 1 or len(protocol_hashes) != 1:
        raise ValueError("mixed mechanism assessment, numerical source, or protocol identity")
    for r in records:
        if (r.get("schema") != "nbo-r15-protected-bridge-v1" or r.get("complete") is not True
                or r.get("method_id") != "nbo" or r.get("primitives_sha256") != protocol["primitives_sha256"]
                or r.get("N_audit") != protocol["assessment_steps"]
                or r.get("paths") != protocol["bridges_per_stream"]
                or r.get("dimension") not in protocol["dimensions"]):
            raise ValueError("incomplete or scientifically mismatched mechanism record")
        if protocol.get("file_sha256") is not None and r["protocol_sha256"] != protocol["file_sha256"]:
            raise ValueError("mechanism protocol file hash mismatch")
    for d in protocol["dimensions"]:
        selected = [r for r in records if r["dimension"] == d]
        if {r["stream_seed"] for r in selected} != set(protocol["declared_seeds"]) or len(selected) != len(protocol["declared_seeds"]):
            raise ValueError("complete one-record-per-stream mechanism population required")
        selected.sort(key=lambda r:protocol["declared_seeds"].index(r["stream_seed"]))
        if len({r["noise_key"] for r in selected if not r.get("analytic_schedule_fallback")}) != sum(not r.get("analytic_schedule_fallback") for r in selected):
            raise ValueError("reused cross-stream mechanism noise")
        loaded = []
        for r in selected:
            path = Path(r["record_path"]).parent/r["raw_path"]
            if sha(path) != r["raw_sha256"]:
                raise ValueError("mechanism raw hash mismatch")
            a = np.load(path)
            if len(a["M"]) != protocol["bridges_per_stream"]:
                raise ValueError("unbalanced mechanism sample count")
            loaded.append(a)
        intervals = {}
        for key in STATISTICS:
            # Each stratum is clipped at its own predeclared coefficient bound.
            low = np.concatenate([np.clip(a[key+"_lower"],-r["ranges"][key],r["ranges"][key]) for a,r in zip(loaded,selected)])
            high = np.concatenate([np.clip(a[key+"_upper"],-r["ranges"][key],r["ranges"][key]) for a,r in zip(loaded,selected)])
            tail_values = [r["clipping_expectation_allowances"][key] for r in selected]
            tail = 0. if not any(tail_values) else iu(pc.mean_i(I(np.asarray(tail_values))))
            intervals[key] = interval_empirical_bernstein(low, high,
                bound=max(r["ranges"][key] for r in selected), event_alpha=budget.event_alpha,
                clipping_tail=tail)
            intervals[key]["raw_descriptive_mean"] = float(np.mean([a[key].mean() for a in loaded]))
        avg = lambda values: 0. if not any(values) else iu(pc.mean_i(I(np.asarray(values, dtype=float))))
        mr = avg([r["constants"]["arithmetic"]["predicted_gain_representation_allowance"] for r in selected])
        dr = avg([r["constants"]["arithmetic"]["actor_gap_representation_allowance"] for r in selected])
        er = iu(isqrt(pc.mean_i(I(np.asarray([r["constants"]["arithmetic"]["risk_representation_root_allowance"] for r in selected])).square())))
        LM = il(I(intervals["M"]["lower"])-I(mr))
        UA = max(0., intervals["A"]["upper"])
        UE = iu((isqrt(I(max(0., intervals["E"]["upper"])))+I(er)).square())
        UD = iu(I(intervals["D"]["upper"])+I(dr))
        hold = avg([r["constants"]["holding_deficit_upper"] for r in selected])
        transfer = avg([r["constants"]["payoff_transfer_upper"] for r in selected])
        anchor = avg([r["constants"]["anchor_regret_upper"] for r in selected])
        product_gain = il(I(LM)-isqrt(I(UA)*I(UE))-I(hold)-I(transfer))
        active = [r for r in selected if not r.get("analytic_schedule_fallback")]
        concave = bool(active) and all(r["constants"]["strong_concavity_verified"] for r in active)
        mu = min((r["constants"]["strong_concavity_modulus_lower"] for r in active), default=0.) if concave else 0.
        quadratic_gain = il(I(LM)/2-I(UD)-2*I(UE)/I(mu)-I(hold)-I(transfer)) if concave else None
        gain = max(product_gain, quadratic_gain) if quadratic_gain is not None else product_gain
        if not active:
            LM = UA = UE = UD = hold = transfer = mr = dr = er = product_gain = gain = 0.
        output["dimensions"][str(d)] = dict(dimension=d, stream_count=len(selected),
            bridges_per_stream=protocol["bridges_per_stream"], total_bridges=len(low),
            intervals=intervals, represented_query_costate_risk_comparison_upper=intervals["E_minus_raw"]["upper"],
            critic_risk_reduction_verified=intervals["E_minus_raw"]["upper"]<0,
            L_M=LM, U_A=UA, U_E=UE, U_D=UD, holding_deficit_upper=hold,
            paired_payoff_transfer_upper=transfer, strong_concavity_verified=concave,
            curvature_modulus_lower=mu, product_gain_lower=product_gain,
            quadratic_gain_lower=quadratic_gain, continuous_gain_lower=gain,
            anchor_regret_upper=anchor, continuous_regret_upper=iu(I(anchor)-I(gain)),
            predicted_gain_representation_allowance=mr, risk_representation_root_allowance=er,
            actor_gap_representation_allowance=dr,
            descriptive_qrisk={key:intervals[key]["raw_descriptive_mean"] for key in ["E", "E_raw", "E_minus_raw"]},
            fallback_streams=[r["stream_seed"] for r in selected if r.get("analytic_schedule_fallback")],
            record_hashes=[r["raw_sha256"] for r in selected],
            scope="complete fixed finite uniform stream distribution; predictor subproblem comparison on represented candidate bridge queries; welfare includes exact-state and continuous-payoff allowances")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--trial-id")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pool", type=Path, nargs="*")
    args = parser.parse_args()
    if args.pool is not None:
        records = []
        for path in args.pool:
            row = json.loads(path.read_text())
            row["record_path"] = str(path.resolve())
            records.append(row)
        protocol = json.loads(args.protocol.read_text())
        protocol["file_sha256"] = sha(args.protocol)
        result = pool(records, protocol)
        write(args.out, result)
    else:
        if args.checkpoint is None or args.trial_id is None:
            parser.error("--checkpoint and --trial-id are required for one stream")
        result = evaluate(args.protocol, args.checkpoint, args.trial_id, args.out)
        print(json.dumps({"trial":args.trial_id,"complete":result["complete"],"seconds":result["seconds"]}), flush=True)
