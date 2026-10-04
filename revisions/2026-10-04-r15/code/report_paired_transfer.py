"""A deterministic paired-transfer refinement of the unchanged R15 events.

This module does not train, load fitted weights, simulate, change stopping, or
spend a confidence event.  It checks the complete original report and arrays,
replays its finite-expectation events, and replaces only the deterministic
normal--normal transfer by the smaller independently proved allowance.

Chronology: developed after numerical source 9142f404 was frozen and the first
trial's deterministic transfer width had been inspected.  It is expressly a
subsequent theorem/account, not a preregistered analysis change.  All original
endpoints are retained beside their refined versions.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
R15 = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import actor_verifier as av
import report_experiment as frozen
import method_statistics as stats

pc, tc, I = av.pc, av.tc, av.pc.I
FROZEN_NUMERICAL_SOURCE = '9142f404bb9c5163aa94d3a4ded4d0fa48a49c50'
DIRECT_SUBTRACTION_CUSHION = 1e-12
MODEL_PRIMITIVES_SHA256 = 'f795e65fa8ee89a92e3935217032cdc940c6dc5a50230aee4a510720b03b6e4e'
NAMES = frozen.NAMES


def validate_model_contract(protocol, dimension, steps, epsilon):
    d = protocol['design']
    if protocol.get('status') != 'frozen_before_confirmatory_execution':
        raise ValueError('original prospectively frozen protocol required')
    if dimension not in d['dimensions'] or d['dimensions'] != [10, 50]:
        raise ValueError('this account is for the two declared R15 dimensions')
    if steps != 2048 or protocol['confirmation']['steps'] != steps or epsilon != .1:
        raise ValueError('this account retains the original 2048-cell radius-.1 experiment')
    if d['primitives_sha256'] != MODEL_PRIMITIVES_SHA256:
        raise ValueError('fixed-model refinement cannot be transferred to other primitives')
    if hashlib.sha256(av.canonical(d['primitives'])).hexdigest() != MODEL_PRIMITIVES_SHA256:
        raise ValueError('primitive data and fingerprint differ')
    if d['initial_state_population'] != dict(means=[-.5, 0., .5], spreads=[0., .25, .5], weights='uniform over nine profiles as in R12'):
        raise ValueError('the declared initial law has changed')
    if protocol['training']['epsilon'] != epsilon:
        raise ValueError('training and verifier tube radii differ')


def high(x):
    return float(x.hi)


def nonnegative(x):
    return I(np.maximum(0., x.lo), np.maximum(0., x.hi))


def verified_spectral(matrix, proposal=None):
    """An SVD or saved record proposes a majorant; fresh interval LDL proves it.

    Replaying a saved proposal avoids platform-dependent SVD proposal bits.
    No tolerance is granted to an economic endpoint or to a matrix identity.
    """
    matrix = np.asarray(matrix, dtype=np.float64)
    proof = tc.spectral_bound(matrix) if proposal is None else proposal
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.isfinite(matrix).all():
        raise ValueError('finite square matrix required')
    d = len(matrix)
    if proof['dimension'] != d or proof['matrix_sha256'] != hashlib.sha256(matrix.tobytes()).hexdigest():
        raise ValueError('spectral proposal matrix identity mismatch')
    lam, norm = float(proof['lambda_upper']), float(proof['norm_upper'])
    if not (math.isfinite(lam) and math.isfinite(norm) and lam > 0 and norm > 0):
        raise ValueError('invalid spectral proposal')
    if float(I(norm).square().lo) < lam:
        raise ValueError('proposed operator-norm upper endpoint does not enclose sqrt(lambda)')
    gram = I(np.zeros((d, d)))
    for row in matrix:
        gram = gram+I(row[:, None])*I(row[None, :])
    A, pivots = I(lam)*I(np.eye(d))-gram, []
    for k in range(d):
        pivot = I(A.lo[k, k], A.hi[k, k])
        pivots.append([float(pivot.lo), float(pivot.hi)])
        if float(pivot.lo) <= 0:
            raise ValueError('saved spectral proposal failed a fresh outward LDL pivot')
        if k+1 < d:
            v = I(A.lo[k+1:, k], A.hi[k+1:, k])/pivot
            block = I(A.lo[k+1:, k+1:], A.hi[k+1:, k+1:])-pivot*I(v.lo[:, None], v.hi[:, None])*I(v.lo[None, :], v.hi[None, :])
            A.lo[k+1:, k+1:], A.hi[k+1:, k+1:] = block.lo, block.hi
    final = proof['attempts'][-1]
    if final['lambda_candidate'] != lam or final['positive_pivots'] is not True or final['pivots'] != pivots:
        raise ValueError('stored spectral certificate does not match fresh outward verification')
    return proof


def inherited_account(d, steps, epsilon, support, coupling_proof):
    """Replay the unchanged formulas with the same proved norm majorant.

    This isolated postprocessing process temporarily supplies a freshly
    validated spectral proposal to the historical formula.  The imported
    function is restored immediately; no source file or experiment changes.
    """
    original = pc.spectral_bound
    try:
        pc.spectral_bound = lambda matrix: verified_spectral(matrix, coupling_proof)
        return av.account(d, steps, epsilon, support)
    finally:
        pc.spectral_bound = original


def spectral_interval(matrix, proposal=None):
    """Exact-real interval matrix norm from verified midpoint + radius norm."""
    midpoint = pc.midpoint(matrix)
    radius = pc.radius(matrix)
    proof = verified_spectral(midpoint, None if proposal is None else proposal['midpoint_proof'])
    error = pc.sqrt_nonnegative(pc.sum_axis(pc.sum_axis(I(radius).square(), axis=1)))
    return high(I(proof['norm_upper'])+error), dict(midpoint_proof=proof,
        matrix_radius_frobenius_upper=high(error))


def positive_D_integrals(times, beta, radius, terms=28):
    """D=r*(exp(beta*t)-1)/beta and its first/two-square integrals.

    Positive power series avoid subtractive cancellation at the first cells.
    Geometric remainder bounds use beta*T<1, as verified for this economy.
    """
    t, b, r = I(np.asarray(times)), I(beta), I(radius)
    z = b*t
    if np.any(t.lo < 0) or np.any(t.hi > 1) or high(b) <= 0 or high(b) >= 1 or high(r) < 0:
        raise ValueError('the fixed-horizon series account requires beta*T<1')
    dterm, iterm, jterm = r*t, r*t.square()/2, r.square()*t*t*t/3
    D, first, second = dterm, iterm, jterm
    for j in range(terms):
        dterm = dterm*z/(j+2)
        iterm = iterm*z/(j+3)
        jterm = jterm*z*(2**(j+3)-2)/(2**(j+2)-2)/(j+4)
        D, first, second = D+dterm, first+iterm, second+jterm
    # The next-term ratio is bounded uniformly, also for all later terms.
    rd = b/(terms+2)
    ri = b/(terms+3)
    rj = 3*b/(terms+4)
    D = D+I(np.zeros_like(times), (dterm*rd/(1-rd)).hi)
    first = first+I(np.zeros_like(times), (iterm*ri/(1-ri)).hi)
    second = second+I(np.zeros_like(times), (jterm*rj/(1-rj)).hi)
    return nonnegative(D), nonnegative(first), nonnegative(second)


def calculate(protocol, d, steps=2048, epsilon=.1, coefficient_proposals=None):
    validate_model_contract(protocol, d, steps, epsilon)
    p, primitive_hash = av.bind_primitives(protocol['design']['primitives'])
    if p['T'] != 1.:
        raise ValueError('fixed horizon contract')
    support = av.population(d)
    B = av.old.coupling(d)
    proposals = coefficient_proposals or {}
    spectral = verified_spectral(B, proposals.get('coupling'))
    wt, inherited = inherited_account(d, steps, epsilon, support, spectral)
    b = I(spectral['norm_upper'])
    kappa, eta = I(p['coupling']), I(p['adjustment'])
    rho, chi = I(p['discount']), I(p['CHI'])
    si, sc = I(p['idiosyncratic_sigma']), I(p['common_sigma'])
    h, T = I(1.)/steps, I(1.)
    beta = high(kappa*b)
    beta_i = I(beta)
    L2 = high(4/(3*pc.sqrt_nonnegative(I(3.))))
    row_sum = pc.sum_axis(I(B), axis=1)
    row_abs = pc.sum_axis(I(np.abs(B)), axis=1)
    row_norm = pc.sqrt_nonnegative(pc.sum_axis(I(B).square(), axis=1))
    row_max = float(row_norm.hi.max())
    q = si.square()*pc.sum_axis(I(B).square(), axis=1)+sc.square()*row_sum.square()
    q_rms = pc.sqrt_nonnegative(pc.mean_i(q.square()))
    q_root = pc.sqrt_nonnegative(q)
    matrix_q = I(q.hi[:, None])*I(B)
    matrix_sqrtq = I(q_root.hi[:, None])*I(B)
    qnorm, qp = spectral_interval(matrix_q, proposals.get('weighted_noise'))
    sqnorm, sqp = spectral_interval(matrix_sqrtq, proposals.get('weighted_noise_root'))
    c0 = I(p['productivity'])-(si.square()+sc.square())/2
    mend = tc.schedule_i(I(1.))
    if not float(c0.hi) < float(tc.schedule_i(I(0.)).lo):
        raise ValueError('endpoint drift bound requires c < increasing schedule(0)')
    c_distance = I(float((c0-mend).absmax()))
    drift_norm = c_distance+kappa+I(epsilon)
    R = c_distance*I(row_sum.absmax())+(kappa+I(epsilon))*row_abs
    rnorm, rp = spectral_interval(I(R.hi[:, None])*I(B), proposals.get('weighted_drift'))
    # Global vector generator difference and martingale derivative constants.
    Lvector = kappa*I(L2)*I(rnorm)+beta_i.square()+kappa*I(qnorm)
    Hnoise = kappa*I(L2)*I(sqnorm)
    Hmean = kappa*I(L2)*b.square()
    Hcross = kappa*I(L2)*b*I(row_max)*pc.sqrt_nonnegative(I(d))

    gram = I(np.zeros((d, d)))
    for j in range(d):
        gram = gram+I(B[:, j, None])*I(B[None, :, j])
    positive_sum = pc.sum_axis(pc.sum_axis(I(np.maximum(gram.hi, 0.)), axis=1))
    beta_prod = min(beta, high(kappa*pc.sqrt_nonnegative(positive_sum/d)))
    mean_noise_lipschitz = kappa*I(min(high(q_rms*b), qnorm))
    Lmean = Hmean*drift_norm+I(beta_prod)*beta_i+mean_noise_lipschitz

    # A sharper individual generator bound exploits the common scalar action
    # centre; it remains a global bound for every feasible tube action.
    norm_B1 = pc.sqrt_nonnegative(pc.mean_i(row_sum.square()))
    Kbase = kappa*(c_distance*norm_B1+b*(kappa+I(epsilon)))+kappa*I(L2)*q_rms/2
    G = kappa*pc.sqrt_nonnegative(pc.mean_i(q))
    times = np.arange(steps+1)/steps
    ti = I(times)
    u0 = h*pc.exp_i(beta_i*ti)*(Kbase*ti/2+G*pc.sqrt_nonnegative(ti/3))
    # Both controllers are held and lie in the SAME radius-epsilon tube.
    radius = high(2*I(epsilon))
    D, integral_D, integral_D2 = positive_D_integrals(times, beta, radius)
    cumulative_drift = h/2*(Lvector*integral_D+beta_i*I(radius)*ti)
    cumulative_martingale = h*Hnoise*pc.sqrt_nonnegative(integral_D2/3)
    pair_bounds = [I(0.)]
    cumulative_pair, cumulative_cross = I(0.), I(0.)
    for k in range(1, steps+1):
        cumulative_cross = cumulative_cross+h*Hcross*I(D.lo[k-1], D.hi[k-1])*I(u0.lo[k-1], u0.hi[k-1])
        forcing = I(cumulative_drift.lo[k], cumulative_drift.hi[k])+I(cumulative_martingale.lo[k], cumulative_martingale.hi[k])+cumulative_cross
        value = forcing+h*beta_i*cumulative_pair
        pair_bounds.append(value)
        cumulative_pair = cumulative_pair+value
    pair = I(np.asarray([x.lo for x in pair_bounds]), np.asarray([x.hi for x in pair_bounds]))
    nodal = I(beta_prod)*I(pair.lo[:-1], pair.hi[:-1])+Hmean*I(D.lo[:-1], D.hi[:-1])*I(u0.lo[:-1], u0.hi[:-1])
    production_grid = pc.sum_axis(wt['B']*nodal)
    # Psi_k(s)=integral_s^{t_(k+1)} w(t)dt decreases in s, while D(s)
    # increases. Chebyshev bounds its integral by J_k times the cell mean.
    Dcell = nonnegative(I(integral_D.lo[1:], integral_D.hi[1:])-I(integral_D.lo[:-1], integral_D.hi[:-1]))/h
    Kmean_cell = Lmean*Dcell+I(beta_prod)*I(radius)
    production_within = pc.sum_axis(wt['J']*Kmean_cell)
    average_s0 = pc.mean_i(I(np.asarray([r['initial_spread_upper'] for r in inherited['components']])))
    S = average_s0+(kappa+I(epsilon))*T+si*pc.sqrt_nonnegative((1-I(1.)/d)*T)
    DT, uT, u0T = I(D.lo[-1], D.hi[-1]), pair_bounds[-1], I(u0.lo[-1], u0.hi[-1])
    terminal = chi*pc.exp_i(-rho*T)*((2*S+2*DT)*uT+2*DT*u0T)
    ideal_bias = production_grid+production_within+terminal

    # Retain the inherited per-policy path/noise and complete statistic
    # arithmetic allowances. No numerical cancellation is silently claimed.
    extras = np.asarray([high(I(r['forward_roundoff'])+I(r['normal_clipping_strong_error'])) for r in inherited['components']])
    extra = I(float(extras.max()))
    extra_production = 2*I(beta_prod)*pc.sum_axis(wt['B'])*extra
    extra_terminal = 2*chi*pc.exp_i(-rho*T)*extra*(2*S+extra)
    statistic = 2*I(inherited['statistic_error_upper'])
    subtraction_cushion = I(DIRECT_SUBTRACTION_CUSHION)
    total = ideal_bias+extra_production+extra_terminal+statistic+subtraction_cushion
    legacy_direct = 2*I(inherited['actor_bias_upper'])+2*I(inherited['statistic_error_upper'])+subtraction_cushion
    return dict(status='independently_reviewed_deterministic_account',
        scope='Two arbitrary total-held tube controllers on common innovations; the original stored direct paired payoff statistic; model constants independent of fitted weights and payoff observations.',
        no_weights_or_random_samples_read=True, no_new_confidence_event=True,
        dimension=d, steps=steps, epsilon=epsilon, action_difference_upper=radius,
        beta=beta, beta_production=beta_prod, tanh_second_derivative_bound=L2,
        vector_generator_lipschitz=high(Lvector), scalar_generator_lipschitz=high(Lmean),
        paired_diffusion_derivative_lipschitz=high(Hnoise), scalar_production_hessian=high(Hmean),
        four_point_vector_cross_coefficient=high(Hcross), base_generator_bound=high(Kbase),
        base_diffusion_derivative_bound=high(G), terminal_base_error=high(u0T),
        terminal_pair_error=high(uT), terminal_state_distance=high(DT),
        production_grid=high(production_grid), production_within_cell=high(production_within),
        terminal_dispersion=high(terminal), ideal_paired_transfer=high(ideal_bias),
        inherited_path_and_clipping_transfer=high(extra_production+extra_terminal),
        inherited_statistic_arithmetic=high(statistic), proposed_total_upper=high(total),
        inherited_direct_transfer_upper=high(legacy_direct),
        improvement_factor_lower=float((legacy_direct/total).lo),
        below_registered_materiality_margin=bool(total.hi < 1e-4),
        population_average_initial_spread_upper=high(average_s0),
        coefficient_proofs=dict(coupling=spectral, weighted_noise=qp,
            weighted_noise_root=sqp, weighted_drift=rp),
        economic_primitives=p, primitives_sha256=primitive_hash,
        integrated_production_weight_upper=high(pc.sum_axis(wt['B'])),
        terminal_payoff_coefficient_upper=high(chi*pc.exp_i(-rho*T)),
        averaged_conditional_dispersion_moment_upper=high(S),
        inherited_state_arithmetic_and_clipping_upper=high(extra),
        inherited_single_statistic_arithmetic_upper=inherited['statistic_error_upper'],
        direct_subtraction_cushion=DIRECT_SUBTRACTION_CUSHION,
        initial_profiles=support.tolist(), initial_profiles_sha256=hashlib.sha256(support.tobytes()).hexdigest(),
        initial_spread_component_bounds=[r['initial_spread_upper'] for r in inherited['components']],
        initial_profile_averaging='Apply conditional Cauchy--Schwarz separately to each profile, then average nine affine bounds; mean spread is not an unconditional mixture L2 norm.',
        grid_error_scope='L2 at original decision nodes; frozen realised actions shared between physical and ideal Euler economies; no actor derivative required.')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_label(path):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_json(path, value):
    path = Path(path)
    if path.exists():
        raise FileExistsError('refusing to overwrite a derived artifact: '+str(path))
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def source_bindings(protocol_path=R15/'PROTOCOL.json'):
    """Bind imported historical/model/statistical sources to the executed SHA.

    The new theorem is independently versioned.  It cannot silently substitute
    new arithmetic kernels or a different empirical-Bernstein implementation.
    No checkpoint or learned parameter is opened by this audit.
    """
    new_paths = {Path(__file__).resolve(),
                 Path(__file__).with_name('paired_transfer_checks.py').resolve()}
    paths = set()
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_file() and path.suffix == '.py' and ROOT in path.parents and path not in new_paths:
                paths.add(path)
    if not {Path(av.__file__).resolve(), Path(frozen.__file__).resolve(),
            Path(stats.__file__).resolve(), Path(pc.__file__).resolve(),
            Path(tc.__file__).resolve()} <= paths:
        raise AssertionError('missing imported frozen dependency')
    records = []
    for path in sorted(paths):
        relative = path.relative_to(ROOT).as_posix()
        blob = subprocess.run(['git', 'show', FROZEN_NUMERICAL_SOURCE+':'+relative],
            cwd=ROOT, check=True, capture_output=True).stdout
        expected = hashlib.sha256(blob).hexdigest()
        actual = digest(path)
        if expected != actual:
            raise ValueError('imported source differs from the executed commit: '+relative)
        records.append(dict(path=relative, sha256=actual,
                            numerical_source_commit=FROZEN_NUMERICAL_SOURCE))
    protocol_relative = 'revisions/2026-10-04-r15/PROTOCOL.json'
    original_protocol = subprocess.run(['git', 'show', FROZEN_NUMERICAL_SOURCE+':'+protocol_relative],
        cwd=ROOT, check=True, capture_output=True).stdout
    protocol_hash = hashlib.sha256(original_protocol).hexdigest()
    if digest(protocol_path) != protocol_hash:
        raise ValueError('protocol bytes differ from the executed numerical-source commit')
    artifacts = [Path(__file__), Path(__file__).with_name('paired_transfer_checks.py'),
        R15/'manuscript/paired_transfer.tex', R15/'PAIRED_TRANSFER_REFINEMENT.md']
    if not all(path.is_file() for path in artifacts):
        raise ValueError('the new proof, checks, and provenance record must all exist')
    return dict(numerical_source_commit=FROZEN_NUMERICAL_SOURCE,
        frozen_imported_files=records,
        frozen_protocol=dict(path=file_label(protocol_path), sha256=protocol_hash),
        refinement_files=[dict(path=file_label(path), sha256=digest(path)) for path in artifacts],
        scope='Historical imported sources verified byte-for-byte against the generating commit; new deterministic refinement files separately hashed. No fitted weights read.')


def per_policy_numerical_extra(account, confirmation):
    """Retain saved path/clipping allowances, never infer them from outcomes."""
    saved = confirmation['constants']
    for field in ['dimension', 'steps', 'epsilon']:
        if saved.get(field) != account[field] or confirmation.get(field) != account[field]:
            raise ValueError('refinement/saved account mismatch: '+field)
    if saved.get('design') != 'uniform_nine_profiles':
        raise ValueError('unknown population account')
    support = np.asarray(saved['initial_profiles'], dtype=np.float64)
    if hashlib.sha256(support.tobytes()).hexdigest() != account['initial_profiles_sha256']:
        raise ValueError('saved and proved initial profile laws differ')
    if saved['population_weights'] != [1./9]*9 or len(saved['components']) != 9:
        raise ValueError('complete equally weighted initial-profile components required')
    extra = []
    for i, item in enumerate(saved['components']):
        if item['initial_state'] != account['initial_profiles'][i]:
            raise ValueError('saved profile order/identity mismatch')
        if item['dimension'] != account['dimension'] or item['steps'] != account['steps'] or item['epsilon'] != account['epsilon']:
            raise ValueError('inconsistent component account')
        if item['spectral']['matrix_sha256'] != account['coefficient_proofs']['coupling']['matrix_sha256']:
            raise ValueError('saved and refined binary64 coupling matrices differ')
        values = [item['forward_roundoff'], item['normal_clipping_strong_error'],
                  item['initial_spread_upper'], item['quadrature_and_statistic_roundoff']]
        if not all(math.isfinite(x) and x >= 0 for x in values):
            raise ValueError('invalid saved numerical allowance')
        if item['gaussian_cap'] != 10. or item['clip_u'] != 8.:
            raise ValueError('changed original Gaussian or payoff clipping contract')
        extra.append(high(I(values[0])+I(values[1])))
    # Rebuilt model arithmetic is an additional conservative guard.  The saved
    # allowances are charged even when their own platform produced larger ones.
    e = max(max(extra), account['inherited_state_arithmetic_and_clipping_upper'])
    s0 = max(account['population_average_initial_spread_upper'],
             high(pc.mean_i(I(np.asarray([x['initial_spread_upper'] for x in saved['components']])))))
    p = account['economic_primitives']
    S = I(s0)+(I(p['coupling'])+I(account['epsilon']))*I(p['T'])+I(p['idiosyncratic_sigma'])*pc.sqrt_nonnegative((1-I(1.)/account['dimension'])*I(p['T']))
    production = I(account['beta_production'])*I(account['integrated_production_weight_upper'])*I(e)
    terminal = I(account['terminal_payoff_coefficient_upper'])*I(e)*(2*S+I(e))
    statistic = frozen.allowance(confirmation, 'statistic_error')
    if statistic < max(x['quadrature_and_statistic_roundoff'] for x in saved['components']):
        raise ValueError('top-level statistic allowance omits a saved component')
    return dict(state_error_upper=e, production_upper=high(production),
        terminal_upper=high(terminal), statistic_error_upper=statistic,
        saved_scalar_reference_quadrature=[x['scalar_M0_quadrature'] for x in saved['components']],
        reference_quadrature_scope='Common analytical-reference path cancels for two simulated policies; both complete statistic quadrature allowances are retained. No cancellation is used for a mixed fallback.')


def refined_allowances(left, right, account):
    original = frozen.contrast_allowances(left, right)
    fa, fb = bool(left['record']['fallback']), bool(right['record']['fallback'])
    if fa or fb:
        return dict(original=original, refined=dict(original),
            refinement_applied=False,
            eligibility='both_exact_reference' if fa and fb else 'mixed_fallback_original_transfer_retained',
            new_theorem_bias_candidate=None, numerical_terms=None)
    for item in [left, right]:
        c = item['record']['final_confirmation']
        if c['implementation'] != 'specified inward-guarded innovation-history controller' or c['analytic_schedule']:
            raise ValueError('paired refinement requires two simulated total-held policies')
        if c['primitives_sha256'] != account['primitives_sha256']:
            raise ValueError('refinement and saved policy have different primitives')
    na = per_policy_numerical_extra(account, left['record']['final_confirmation'])
    nb = per_policy_numerical_extra(account, right['record']['final_confirmation'])
    total = I(account['ideal_paired_transfer'])+I(DIRECT_SUBTRACTION_CUSHION)
    for x in [na, nb]:
        total = total+I(x['production_upper'])+I(x['terminal_upper'])+I(x['statistic_error_upper'])
    candidate = high(total)
    result = dict(original)
    result['bias'] = min(original['bias'], candidate)
    # This event has the original clipping range and tail; only a deterministic
    # bridge from its finite expectation to the same economic target changes.
    return dict(original=original, refined=result, refinement_applied=candidate < original['bias'],
        eligibility='two_simulated_total_held_policies', new_theorem_bias_candidate=candidate,
        numerical_terms=dict(left=na, right=nb, direct_subtraction_cushion=DIRECT_SUBTRACTION_CUSHION))


def assert_same_event(original, replay):
    keys = ['paths', 'clipped_mean', 'variance', 'range_lower', 'range_upper',
        'empirical_bernstein_margin', 'clipping_tail', 'event_alpha', 'clipped_paths']
    for key in keys:
        if original[key] != replay[key]:
            raise ValueError('original finite-expectation event did not replay exactly: '+key)


def assert_original_endpoint(original, replay):
    assert_same_event(original, replay)
    for key in ['lower', 'upper', 'bias']:
        if original[key] != replay[key]:
            raise ValueError('original endpoint did not replay exactly: '+key)


def load_original(protocol_path, results, original_path):
    """Require the exact complete dataset that produced the original report."""
    protocol_path, results, original_path = map(Path, [protocol_path, results, original_path])
    p = json.loads(protocol_path.read_text())
    original = json.loads(original_path.read_text())
    design = p['design']
    expected = {(d, s, m) for d in design['dimensions'] for s in design['seeds'] for m in design['methods']}
    if original.get('status') != 'complete' or original.get('trial_count') != len(expected):
        raise ValueError('the complete original report is required before refinement')
    if original['protocol_sha256'] != digest(protocol_path) or original['primitives_sha256'] != design['primitives_sha256']:
        raise ValueError('original report protocol/primitive identity mismatch')
    if original['source_commit'] != FROZEN_NUMERICAL_SOURCE:
        raise ValueError('original report was generated by another numerical source')
    bindings = {(r['dimension'], r['stream_seed'], r['method']): r for r in original['identity_records']}
    if set(bindings) != expected or len(bindings) != len(original['identity_records']):
        raise ValueError('original report omitted or duplicated complete method streams')
    loaded, manifest = {}, []
    for d, seed, m in sorted(expected):
        trial = results/f'd{d}_s{seed}'/m
        rpath, wpath = trial/'RESULT.json', trial/'WORK.json'
        if not rpath.is_file() or not wpath.is_file():
            raise ValueError(f'missing complete original trial {d}/{seed}/{m}')
        if digest(rpath) != bindings[d, seed, m]['result_sha256'] or digest(wpath) != bindings[d, seed, m]['work_sha256']:
            raise ValueError('original trial records changed after the original report')
        r, w = json.loads(rpath.read_text()), json.loads(wpath.read_text())
        if r.get('complete') is not True or w.get('complete') is not True:
            raise ValueError('incomplete original record')
        for k, target in [('method_id', m), ('dimension', d), ('stream_seed', seed),
                          ('primitives_sha256', design['primitives_sha256']),
                          ('protocol_sha256', digest(protocol_path))]:
            if r.get(k) != target:
                raise ValueError('original record identity mismatch: '+k)
        if frozen.pick(r, 'numerical_source_commit', 'source_commit', 'source') != FROZEN_NUMERICAL_SOURCE:
            raise ValueError('trial numerical source changed')
        if r['method_fingerprint'] != bindings[d, seed, m]['method_fingerprint']:
            raise ValueError('trial method fingerprint changed')
        c = r['final_confirmation']
        if r.get('confirmation_independent_of_selection') is not True or c.get('confirmation_independent_of_selection') is not True:
            raise ValueError('selection/online bank cannot substitute for independent confirmation')
        identity = frozen.normalize_identity(c, r, p)
        if identity['paths'] != p['confirmation']['paths_per_seed'] or identity['steps'] != p['confirmation']['steps'] or identity['stream_seed'] != seed:
            raise ValueError('undeclared confirmation bank')
        rp = frozen.raw_file(c, trial, results)
        if digest(rp) != bindings[d, seed, m]['raw_sha256']:
            raise ValueError('raw confirmation arrays changed after the original report')
        with np.load(rp, allow_pickle=False) as bank:
            arrays = {k: bank[k].copy() for k in ['paired_gain', 'initial_profile']}
        if len(arrays['paired_gain']) != identity['paths']:
            raise ValueError('raw confirmation path count changed')
        constants = {key: frozen.allowance(c, key) for key in ['clip', 'bias', 'tail', 'actor_bias', 'statistic_error']}
        if bool(r['fallback']) != bool(c.get('analytic_schedule', False)) or bool(r['fallback']) != bool(bindings[d, seed, m]['fallback']):
            raise ValueError('fallback identity changed')
        if r['fallback'] and (np.count_nonzero(arrays['paired_gain']) or any(constants.values())):
            raise ValueError('analytical fallback must retain exact-zero statistic and allowances')
        loaded[d, seed, m] = dict(record=r, work=w, identity=identity,
            arrays=arrays, constants=constants, raw_sha256=digest(rp))
        manifest.extend(dict(path=file_label(path), sha256=digest(path)) for path in [rpath, wpath, rp])
    for d in design['dimensions']:
        for seed in design['seeds']:
            first = loaded[d, seed, design['methods'][0]]
            for m in design['methods'][1:]:
                row = loaded[d, seed, m]
                stats.paired_difference(first['arrays']['paired_gain'], row['arrays']['paired_gain'],
                    left_identity=first['identity'], right_identity=row['identity'])
                if not np.array_equal(first['arrays']['initial_profile'], row['arrays']['initial_profile']):
                    raise ValueError('original common initial-profile draws differ')
    manifest.extend(dict(path=file_label(path), sha256=digest(path)) for path in [protocol_path, original_path])
    return p, original, loaded, manifest


def generate_tables(result, out):
    def endpoint(z):
        unit = Decimal('0.000001')
        lo = Decimal.from_float(z['lower']).quantize(unit, rounding=ROUND_FLOOR)
        hi = Decimal.from_float(z['upper']).quantize(unit, rounding=ROUND_CEILING)
        return f'[{lo:.6f}, {hi:.6f}]'
    def decision(z):
        d = z['decision']
        return ('Equivalent' if d['practical_equivalence'] else 'Superior' if d['economically_material_superiority']
                else 'Inferior' if d['economically_material_inferiority'] else 'Unresolved')
    rows = []
    for r in result['method_comparisons']:
        name = r['endpoint'].split('__minus__')[1]
        rows.append([r['dimension'], 'NBO--'+NAMES[name], f"{r['original']['raw_mean']:.6f}",
            endpoint(r['original']), endpoint(r['refined']), decision(r['refined'])])
    frozen.latex_table(out/'paired_transfer_main.tex',
        'Original and refined direct method endpoints on the same observations',
        'tab:r15-paired-refined-main',
        ['$d$', 'Comparison', 'Mean', 'Original interval', 'Refined interval', 'Decision'], rows,
        r'The new deterministic common-innovation transfer is proved in Appendix~\ref{app:r15pairedtransfer}. '
        r'Both intervals use the identical original clipped statistic, path identities, empirical Bernstein event, and confidence allocation. '
        r'The refinement was developed after the original source freeze and inspection of the first transfer width. '
        r'Only the deterministic transfer changes; mixed analytical fallbacks retain the original allowance. '
        r'Decisions use the original $10^{-4}$ economic margin. Original training, stopping, and work records remain unchanged.')
    seed_rows = []
    for r in result['seed_comparisons']:
        name = r['endpoint'].split('__minus__')[1]
        seed_rows.append([r['dimension'], r['stream_seed'], NAMES[name],
            f"{r['original']['mean']:.6f}", endpoint(r['original']), endpoint(r['refined']),
            'Both' if r['eligibility'] == 'both_exact_reference' else 'Mixed' if r['eligibility'].startswith('mixed_') else 'Normal'])
    frozen.latex_table(out/'paired_transfer_supplement.tex',
        'Every registered direct stream comparison before and after deterministic refinement',
        'tab:r15-paired-refined-seeds',
        ['$d$', 'Stream', 'NBO minus', 'Mean', 'Original interval', 'Refined interval', 'Case'], seed_rows,
        r'All declared streams are retained. Normal means two simulated total-held policies; Mixed means one analytical fallback; Both means two exact analytical references. '
        r'Only Normal rows are eligible for the new transfer. No payoff vector is regenerated and no skipped stopping event is recycled.', long=True)


def read_coefficient_proposals(path, protocol):
    if path is None:
        return {}
    supplied = json.loads(Path(path).read_text())
    rows = supplied['model_accounts']
    by_dimension = {r['dimension']: r for r in rows}
    if set(by_dimension) != set(protocol['design']['dimensions']) or len(rows) != len(by_dimension):
        raise ValueError('exact complete dimension set required for coefficient replay')
    for d, row in by_dimension.items():
        validate_model_contract(protocol, d, row['steps'], row['epsilon'])
        if row['primitives_sha256'] != protocol['design']['primitives_sha256'] or row['economic_primitives'] != protocol['design']['primitives']:
            raise ValueError('coefficient proposal belongs to another economy')
    # Only these mathematical proposals are used.  Every one is included in
    # the resulting account and re-proved against its exact matrix.  Runtime
    # provenance of the replay command belongs in the independent audit log.
    return {d: r['coefficient_proofs'] for d, r in by_dimension.items()}


def refine_report(protocol_path, results, original_path, out, coefficient_record=None):
    start = time.perf_counter()
    p, original, loaded, manifest = load_original(protocol_path, results, original_path)
    design, contrasts = p['design'], p['confirmation']['direct_contrasts']
    sources = source_bindings(protocol_path)
    count = len(design['dimensions'])*(len(design['methods'])+len(contrasts))*(len(design['seeds'])+1)
    if count != p['inference']['method_confirmation_events']:
        raise ValueError('original confidence family changed')
    budget = stats.ConfidenceBudget(p['inference']['alpha_allocation']['method_confirmation'], count)
    delta = budget.event_alpha
    if original['confidence'] != budget.as_dict():
        raise ValueError('original confidence allocation changed')
    proposals = read_coefficient_proposals(coefficient_record, p)
    accounts = {d: calculate(p, d, coefficient_proposals=proposals.get(d)) for d in design['dimensions']}
    old_seed = {(r['dimension'], r['stream_seed'], r['endpoint']): r for r in original['seed_endpoints']}
    old_method = {(r['dimension'], r['endpoint']): r for r in original['method_endpoints']}
    seed_rows, method_rows = [], []
    for d in design['dimensions']:
        for a, b in contrasts:
            name = a+'__minus__'+b
            values, constants = {}, {}
            for seed in design['seeds']:
                left, right = loaded[d, seed, a], loaded[d, seed, b]
                values[seed] = stats.paired_difference(left['arrays']['paired_gain'], right['arrays']['paired_gain'],
                    left_identity=left['identity'], right_identity=right['identity'])
                constants[seed] = refined_allowances(left, right, accounts[d])
                endpoints = {}
                for key in ['original', 'refined']:
                    c = constants[seed][key]
                    endpoints[key] = stats.empirical_bernstein(values[seed], bound=c['clip'], bias=c['bias'],
                        clipping_tail=c['tail'], event_alpha=delta)
                old = old_seed[d, seed, name]
                assert_original_endpoint(old, endpoints['original'])
                assert_same_event(old, endpoints['refined'])
                if endpoints['refined']['lower'] < old['lower'] or endpoints['refined']['upper'] > old['upper']:
                    raise AssertionError('smaller deterministic allowance widened an endpoint')
                seed_rows.append(dict(dimension=d, stream_seed=seed, endpoint=name,
                    original=old, refined=endpoints['refined'],
                    **{k: v for k, v in constants[seed].items() if k not in ['original', 'refined']}))
            mean_endpoints = {}
            for key in ['original', 'refined']:
                by_seed = {s: constants[s][key] for s in design['seeds']}
                mean_endpoints[key] = stats.finite_stream_mean(values,
                    declared_seeds=design['seeds'],
                    noise_keys={s: loaded[d, s, a]['identity']['noise_hash'] for s in design['seeds']},
                    bounds={s: by_seed[s]['clip'] for s in design['seeds']},
                    biases={s: by_seed[s]['bias'] for s in design['seeds']},
                    clipping_tails={s: by_seed[s]['tail'] for s in design['seeds']},
                    event_alpha=delta, confirmation_independent_of_selection=True)
            old = old_method[d, name]
            assert_original_endpoint(old, mean_endpoints['original'])
            assert_same_event(old, mean_endpoints['refined'])
            refined = mean_endpoints['refined']
            refined['decision'] = stats.economic_decision(refined['lower'], refined['upper'], p['economic_decision']['equivalence_margin_payoff'])
            method_rows.append(dict(dimension=d, endpoint=name, original=old, refined=refined,
                eligible_normal_normal_streams=sum(constants[s]['eligibility']=='two_simulated_total_held_policies' for s in design['seeds']),
                refined_streams=sum(constants[s]['refinement_applied'] for s in design['seeds'])))
    expected_events = len(design['dimensions'])*len(contrasts)*(len(design['seeds'])+1)
    if len(seed_rows)+len(method_rows) != expected_events:
        raise AssertionError('missing registered direct contrast')
    result = dict(status='complete', refinement_type='subsequent deterministic theorem on unchanged original events',
        generated_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=digest(protocol_path),
        original_report_path=file_label(original_path), original_report_sha256=digest(original_path),
        original_numerical_source_commit=FROZEN_NUMERICAL_SOURCE,
        primitives_sha256=design['primitives_sha256'], sources=sources,
        original_trial_count=original['trial_count'], original_confidence=original['confidence'],
        reused_direct_events=expected_events, additional_confidence_events=0,
        changed_payoff_observations=0, fitted_weights_read=False,
        unchanged_quantities=['all original sample arrays', 'clipping ranges', 'clipping tails',
            'finite-expectation empirical Bernstein events', 'confidence allocation',
            'method and stream population', 'fitting', 'actual stopping', 'attainment', 'complete work records'],
        chronology='Developed after the original numerical-source freeze and review of the first deterministic transfer width; no preregistration claim for the theorem refinement.',
        model_accounts=list(accounts.values()), seed_comparisons=seed_rows, method_comparisons=method_rows,
        original_identity_records=original['identity_records'], input_file_manifest=manifest,
        original_unchanged_attainment=original['attainment'], original_unchanged_work=original['work'],
        postprocessing_seconds_before_writes=time.perf_counter()-start,
        postprocessing_work_scope='Independent deterministic/report work; not inserted into or subtracted from historical per-method execution clocks.')
    # Verify that no input was edited while it was being replayed.
    for entry in manifest:
        path = Path(entry['path'])
        path = path if path.is_absolute() else ROOT/path
        if digest(path) != entry['sha256']:
            raise ValueError('an original input changed during refinement')
    write_json(out/'PAIRED_TRANSFER_REPORT.json', result)
    generate_tables(result, out)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, default=R15/'PROTOCOL.json')
    parser.add_argument('--results', type=Path, help='Complete original experiment/trials directory')
    parser.add_argument('--original-report', type=Path, help='Original complete REPORT.json; never overwritten')
    parser.add_argument('--out', type=Path, required=True, help='New empty derived-output directory')
    parser.add_argument('--coefficient-record', type=Path,
        help='Prior constants/refinement JSON: revalidate its spectral proposals without a new SVD proposal; endpoints still replay exactly')
    parser.add_argument('--constants-only', action='store_true', help='Read no payoff arrays; calculate only model bounds')
    args = parser.parse_args()
    if not args.constants_only and (args.results is None or args.original_report is None):
        parser.error('--results and --original-report are required for endpoint refinement')
    out = args.out.resolve()
    for protected in [args.results, args.original_report.parent if args.original_report else None]:
        if protected:
            protected = protected.resolve()
            if out == protected or protected in out.parents:
                raise ValueError('derived output must be outside the original evidence/report directory')
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('derived output directory must be new or empty')
    out.mkdir(parents=True, exist_ok=True)
    if args.constants_only:
        start = time.perf_counter()
        protocol = json.loads(args.protocol.read_text())
        proposals = read_coefficient_proposals(args.coefficient_record, protocol)
        records = [calculate(protocol, d, coefficient_proposals=proposals.get(d)) for d in protocol['design']['dimensions']]
        result = dict(status='complete_deterministic_model_account', generated_utc=datetime.now(timezone.utc).isoformat(),
            protocol_sha256=digest(args.protocol), sources=source_bindings(args.protocol), model_accounts=records,
            no_fitted_weights_or_payoff_samples_read=True, additional_confidence_events=0,
            postprocessing_seconds=time.perf_counter()-start)
        write_json(out/'PAIRED_TRANSFER_CONSTANTS.json', result)
        print(json.dumps([{k: x[k] for k in ['dimension', 'ideal_paired_transfer', 'proposed_total_upper', 'inherited_direct_transfer_upper']} for x in records], indent=2))
    else:
        result = refine_report(args.protocol, args.results, args.original_report, out, args.coefficient_record)
        print(json.dumps(dict(status=result['status'], reused_direct_events=result['reused_direct_events'],
            additional_confidence_events=0, output=str(out/'PAIRED_TRANSFER_REPORT.json')), indent=2))


if __name__ == '__main__':
    main()
