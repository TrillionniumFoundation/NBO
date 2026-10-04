"""R16 paired capital transfer for the four prospectively declared economies.

The analytical theorem is the general-T result in the preserved R15 supplement.
This new implementation exposes physical horizon T everywhere, rather than
changing the old fixed-calibration program. In particular h=T/N, terminal
discounts and state moments use T, and every positive-series remainder uses
max(beta*t), not beta alone. All current calibration guards and primitive
bindings remain explicit. This program reads no fitted policy or payoff.

Coefficient formulas below retain the R15 source expressions except these
documented horizon/binding changes. A separate high-precision implementation
checks their output before the confirmation source is frozen.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
R16=ROOT/'revisions/2026-10-04-r16'
R15=ROOT/'revisions/2026-10-04-r15'
sys.dont_write_bytecode=True
sys.path.insert(0,str(R15/'code'))
import report_paired_transfer as preserved
sys.path.insert(0,str(R16/'code'))
from capital_adapter import bind_economy

av=preserved.av
pc,tc,I=av.pc,av.tc,av.pc.I
DIRECT_SUBTRACTION_CUSHION=preserved.DIRECT_SUBTRACTION_CUSHION
high=preserved.high
nonnegative=preserved.nonnegative
verified_spectral=preserved.verified_spectral
spectral_interval=preserved.spectral_interval
refined_allowances=preserved.refined_allowances

def inherited_account(d,steps,epsilon,support,coupling_proof):
    original=pc.spectral_bound
    try:
        pc.spectral_bound=lambda matrix: verified_spectral(matrix,coupling_proof)
        return av.account(d,steps,epsilon,support)
    finally:
        pc.spectral_bound=original

def positive_D_integrals(times, beta, radius, terms=28):
    """D=r*(exp(beta*t)-1)/beta and its first/two-square integrals.

    Positive power series avoid subtractive cancellation at the first cells.
    Geometric remainders use the verified maximum beta*t, allowing the two frozen horizons.
    """
    t, b, r = I(np.asarray(times)), I(beta), I(radius)
    z = b*t
    if np.any(t.lo < 0) or high(b) <= 0 or np.any(z.hi >= 1) or high(r) < 0:
        raise ValueError('the positive-series account requires beta*max(time)<1')
    dterm, iterm, jterm = r*t, r*t.square()/2, r.square()*t*t*t/3
    D, first, second = dterm, iterm, jterm
    for j in range(terms):
        dterm = dterm*z/(j+2)
        iterm = iterm*z/(j+3)
        jterm = jterm*z*(2**(j+3)-2)/(2**(j+2)-2)/(j+4)
        D, first, second = D+dterm, first+iterm, second+jterm
    # The next-term ratio is bounded uniformly, also for all later terms.
    zmax = I(float(z.hi.max()))
    rd = zmax/(terms+2)
    ri = zmax/(terms+3)
    rj = 3*zmax/(terms+4)
    D = D+I(np.zeros_like(times), (dterm*rd/(1-rd)).hi)
    first = first+I(np.zeros_like(times), (iterm*ri/(1-ri)).hi)
    second = second+I(np.zeros_like(times), (jterm*rj/(1-rj)).hi)
    return nonnegative(D), nonnegative(first), nonnegative(second)

def calculate(calibration, d, steps=2048, coefficient_proposals=None):
    global av, pc, tc, I
    bound = bind_economy(calibration['primitives'], calibration['epsilon'], calibration['initial_state_population'], calibration['id'])
    av = bound.verifier
    pc, tc, I = av.pc, av.tc, av.pc.I
    p, primitive_hash = av.bind_primitives(calibration['primitives'])
    epsilon = calibration['epsilon']
    if d not in [10, 50] or steps != 2048 or p['T'] not in [1., 2.]:
        raise ValueError('outside the prospectively specified capital family')
    if primitive_hash != calibration['primitives_sha256']:
        raise ValueError('calibration fingerprint differs')
    bound.assert_bound()
    support = av.population(d)
    B = av.old.coupling(d)
    proposals = coefficient_proposals or {}
    spectral = verified_spectral(B, proposals.get('coupling'))
    wt, inherited = inherited_account(d, steps, epsilon, support, spectral)
    b = I(spectral['norm_upper'])
    kappa, eta = I(p['coupling']), I(p['adjustment'])
    rho, chi = I(p['discount']), I(p['CHI'])
    si, sc = I(p['idiosyncratic_sigma']), I(p['common_sigma'])
    h, T = I(p['T'])/steps, I(p['T'])
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
    mend = tc.schedule_i(T)
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
    times = np.arange(steps+1)*(p['T']/steps)
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
    return dict(status='prospectively_computed_general_horizon_account', calibration_id=calibration['id'],
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

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',type=Path,required=True)
    parser.add_argument('--calibration',required=True)
    parser.add_argument('--dimension',type=int,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--coefficient-proposals',type=Path)
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('refusing to replace a coefficient account')
    p=json.loads(args.protocol.read_text())
    c=next(x for x in p['calibrations'] if x['id']==args.calibration)
    proposed=json.loads(args.coefficient_proposals.read_text())['coefficient_proofs'] if args.coefficient_proposals else None
    result=calculate(c,args.dimension,p['confirmation']['steps'],proposed)
    result['protocol_sha256']=hashlib.sha256(args.protocol.read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['calibration_id','dimension','beta','proposed_total_upper','inherited_direct_transfer_upper']}))

if __name__=='__main__':main()
