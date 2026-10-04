"""R16 explicit-calibration common-path capital verification.

Derived from the byte-preserved R15 actor verifier. Numerical integration,
interval constants, payoff arrays and range accounting retain their original
implementation. The R16 adapter supplies one explicit worker economy; method
identifiers, radius and analytic HJB deployment work are handled here.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'revisions/2026-10-04-r12/code'))
import common
import policy_certificate as pc
import tube_certificate as tc
from method_statistics import empirical_bernstein

old, torch = common.old, common.torch



def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def write(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def bind_primitives(primitives):
    from capital_adapter import active_binding
    bound = active_binding()
    p = bound._accept_primitives(primitives)
    return p, bound.primitives_sha256


def population(d):
    from capital_adapter import active_binding
    return active_binding().support(d)


def account(d, steps, epsilon, support):
    """Fresh primitive-specific constants, including each population component."""
    wt = pc.weights(steps)
    records = [pc.constants(d, steps, epsilon, y, wt) for y in support]
    average = lambda values: float(pc.mean_i(pc.I(np.asarray(values, dtype=float))).hi)
    result = dict(dimension=d, steps=steps, epsilon=epsilon,
        design='uniform_nine_profiles', initial_profiles=support.tolist(),
        population_weights=[1./len(support)]*len(support), components=records,
        bias_upper=average([x['bias_upper'] for x in records]),
        actor_bias_upper=average([x['actor_bias']['total'] for x in records]),
        statistic_error_upper=float(pc.up(max(x['quadrature_and_statistic_roundoff'] for x in records))),
        clipping_threshold=max(x['clipping_threshold'] for x in records),
        clipping_bias=max(x['clipping_bias'] for x in records),
        anchor_upper=average([x['anchor_upper'] for x in records]),
        state_cap=max(x['state_cap'] for x in records),
        scope='declared continuous capital diffusion and innovation-history controller; the original full adapted action class enters the regret bound')
    return wt, result


def verify(actor, *, dimension, steps, paths, noise_seed, event_alpha,
           primitives, out, record_id, metadata):
    """Evaluate one frozen policy; the caller supplies a domain-separated bank.

    All methods within a trial receive identical noise_seed, steps and paths.
    The confirmation bank must be independent of all selection and stopping.
    An analytical-schedule fallback is identified explicitly in metadata and
    has exact gain zero; it is never confused with a left-held schedule.
    """
    start = time.perf_counter()
    d, steps, paths = int(dimension), int(steps), int(paths)
    if paths < 2 or steps < 2 or steps & (steps-1):
        raise ValueError('verification requires at least two paths and a dyadic grid')
    if Path(record_id).name != record_id:
        raise ValueError('record_id must be a plain file stem')
    metadata = dict(metadata)
    for key in ['method_id', 'stream_seed', 'is_confirmation', 'noise_key']:
        if key not in metadata:
            raise ValueError('missing verification identity: ' + key)
    if metadata['method_id'] not in ['nbo', 'raw_costate', 'direct_policy', 'hjb_greedy', 'hjb_distilled']:
        raise ValueError('noncanonical scientific method identifier')
    p, p_sha = bind_primitives(primitives)
    if metadata.get('primitives_sha256', p_sha) != p_sha:
        raise ValueError('caller and verifier primitive fingerprints differ')
    epsilon = float(metadata.get('epsilon', getattr(actor, 'epsilon', .1)))
    from capital_adapter import active_binding
    if epsilon != active_binding().epsilon:
        raise ValueError('candidate radius differs from the bound R16 economy')
    support = population(d)
    wt, constants = account(d, steps, epsilon, support)
    constants_seconds = time.perf_counter() - start
    h = wt['h']
    seed = int(noise_seed)
    if seed < 0 or seed >= 2**64:
        raise ValueError('noise seed outside uint64')
    initial_seed = int.from_bytes(hashlib.sha256(
        ('NBO-R16-robustness-verifier-initial/' + str(seed)).encode()).digest()[:8], 'big')
    ids = np.random.default_rng(initial_seed).integers(len(support), size=paths)
    za = support[ids].copy()
    z0 = za.copy()
    initial_hash = hashlib.sha256(support[ids].tobytes()).hexdigest()
    ids_hash = hashlib.sha256(ids.tobytes()).hexdigest()
    B = old.coupling(d)
    Am, Bm, Cm, Mm = [pc.midpoint(wt[k]) for k in ['A', 'B', 'C', 'M']]
    lo = pc.up(wt['center'].hi-epsilon)
    hi = pc.down(wt['center'].lo+epsilon)
    center = pc.midpoint(wt['center'])
    production = np.zeros(paths)
    deficit = np.zeros(paths)
    integrated_action = np.zeros(paths)
    integrated_action_dispersion = np.zeros(paths)
    c0 = p['productivity'] - (p['idiosyncratic_sigma']**2+p['common_sigma']**2)/2
    rng = np.random.default_rng(seed)
    noise_hash = hashlib.sha256()
    maximum, saturated, clipped = 0., 0, 0
    analytical = bool(metadata.get('analytic_schedule', False))
    if hasattr(actor, 'eval'):
        actor.eval()
    deployment_work_before = dict(getattr(actor, 'work', {}))
    simulation_start = time.perf_counter()
    for k in range(steps):
        f0 = p['coupling']*pc.safe_tanh(z0@B.T)
        if not analytical:
            tx = np.column_stack((np.full(paths, k*h), za))
            with torch.no_grad():
                proposal = actor(torch.from_numpy(tx))
            if isinstance(proposal, torch.Tensor):
                proposal = proposal.detach().cpu().numpy()
            proposal = np.asarray(proposal, dtype=np.float64)
            if proposal.shape == (paths, 1):
                proposal = np.broadcast_to(proposal, (paths, d))
            if proposal.shape != (paths, d) or not np.isfinite(proposal).all():
                raise FloatingPointError('invalid action from frozen policy')
            action = np.maximum(lo[k], np.minimum(hi[k], proposal))
            saturated += int((np.abs(action-center[k]) > .99*epsilon).sum())
            fa = p['coupling']*pc.safe_tanh(za@B.T)
            ma = action.mean(1)
            production += Bm[k]*(fa-f0).mean(1)
            deficit += Cm[k]-Am[k]*pc.safe_log(action).mean(1)+Bm[k]*ma
            deficit += p['adjustment']/2*Am[k]*ma*ma
            integrated_action += h*ma
            integrated_action_dispersion += h*((action-ma[:, None])**2).mean(1)
        else:
            integrated_action += Mm[k]
        z = rng.standard_normal((paths, d+1))
        noise_hash.update(z.tobytes())
        clipped += int((np.abs(z)>10.).sum())
        z = np.clip(z, -10., 10.)
        dw = math.sqrt(h)*(p['idiosyncratic_sigma']*z[:, :d]+p['common_sigma']*z[:, d:])
        if not analytical:
            za = za+h*(c0+fa-action)+dw
        z0 = z0+h*(c0+f0)-Mm[k]+dw
        if analytical:
            za = z0.copy()
        maximum = max(maximum, float(np.max(np.abs(za))))
    if maximum > constants['state_cap']:
        raise ArithmeticError('verified forward-arithmetic state cap exceeded')
    var_a = ((za-za.mean(1, keepdims=True))**2).mean(1)
    var_0 = ((z0-z0.mean(1, keepdims=True))**2).mean(1)
    terminal = -p['CHI']*math.exp(-p['discount']*p['T'])*(var_a-var_0)
    gain = production-deficit+terminal
    simulation_seconds = time.perf_counter()-simulation_start
    if analytical:
        if np.count_nonzero(gain):
            raise AssertionError('analytical reference must cancel identically')
        bound = empirical_bernstein(gain, bound=0., event_alpha=event_alpha)
        # Its expectation equals zero deterministically, independent of sampling.
        bound.update(lower=0., upper=0., empirical_bernstein_margin=0.,
                     theorem='exact analytical reference identity; no statistical error')
        bias, clipping, tail = 0., 0., 0.
        actor_bias, statistic_error = 0., 0.
    else:
        bias, clipping, tail = constants['bias_upper'], constants['clipping_threshold'], constants['clipping_bias']
        actor_bias = constants['actor_bias_upper']
        statistic_error = constants['statistic_error_upper']
        bound = empirical_bernstein(gain, bound=clipping, event_alpha=event_alpha,
                                    bias=bias, clipping_tail=tail)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    raw_path = out/(record_id+'.npz')
    json_path = out/(record_id+'.json')
    if raw_path.exists() or json_path.exists():
        raise ValueError('refusing to overwrite a verification bank')
    np.savez_compressed(raw_path, paired_gain=gain, production=production,
        consumption_deficit=deficit, terminal_gain=terminal, initial_profile=ids,
        terminal_policy_variance=var_a, terminal_anchor_variance=var_0,
        terminal_policy_mean=za.mean(1), terminal_anchor_mean=z0.mean(1),
        integrated_mean_action=integrated_action,
        integrated_action_dispersion=integrated_action_dispersion)
    deployment_work_after = dict(getattr(actor, 'work', {}))
    hjb_first_jet_rows = deployment_work_after.get('online_critic_first_jet_rows', 0)-deployment_work_before.get('online_critic_first_jet_rows', 0)
    hjb_root_rows = deployment_work_after.get('online_scalar_row_iterations', 0)-deployment_work_before.get('online_scalar_row_iterations', 0)
    row = dict(metadata)
    row.update(record_type='R16 independently verified policy payoff', id=record_id,
        method=metadata['method_id'], method_id=metadata['method_id'],
        dimension=d, steps=steps, paths=paths, noise_seed=seed,
        confirmation_bank=metadata['noise_key'] if metadata['is_confirmation'] else None,
        confirmation_independent_of_selection=bool(metadata['is_confirmation']),
        primitives=p, primitives_sha256=p_sha, epsilon=epsilon,
        lower=bound['lower'], upper=bound['upper'], mean=bound['mean'], bound=bound,
        clipping_threshold=clipping, bias=bias, clipping_tail=tail,
        actor_bias_upper=actor_bias, statistic_error_upper=statistic_error,
        initial_profile_hash=ids_hash, initial_state_hash=initial_hash,
        noise_hash=noise_hash.hexdigest(),
        terminal_anchor_hash=hashlib.sha256(z0.tobytes()).hexdigest(),
        terminal_policy_hash=hashlib.sha256(za.tobytes()).hexdigest(),
        raw_path=raw_path.name, raw_sha256=sha(raw_path), json_path=json_path.name,
        constants=constants, policy_regret_upper=float(pc.up(constants['anchor_upper']-bound['lower'])),
        analytic_schedule=analytical, maximum_internal_state=maximum,
        clipped_normal_coordinates=clipped,
        action_saturation_frequency=saturated/(steps*paths*d),
        descriptive_decomposition=dict(production=float(production.mean()),
            consumption_deficit=float(deficit.mean()), terminal_gain=float(terminal.mean()),
            raw_gain=float(gain.mean()), scope='finite-step pathwise means; no separate continuous-component confidence claim'),
        work=dict(verification_transitions=(1 if analytical else 2)*steps*paths,
            verification_paths=paths, actor_forward_rows=0 if analytical else steps*paths,
            first_derivative_rows=hjb_first_jet_rows,
            action_search_iterations=hjb_root_rows,
            exact_hjb_first_jet_rows=hjb_first_jet_rows,
            constants_seconds=constants_seconds, simulation_seconds=simulation_seconds,
            seconds_before_final_record_write=time.perf_counter()-start),
        comparison='continuous payoff relative to the analytical schedule in the same declared economy',
        implementation='analytical continuous schedule' if analytical else 'specified inward-guarded innovation-history controller',
        numerical_arithmetic='inherited outward binary64 and iid Gaussian sampling contract; no change to historical numerical source files')
    write(json_path, row)
    return row
