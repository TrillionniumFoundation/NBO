"""R15 finite-uniform-stream inference; independent confirmatory paths only.

The population is an exhaustively executed, preregistered finite set of complete
algorithm streams, not arbitrary future initializations. Equal path counts per
stream identify its uniform average. Streams are independent in the confirmation
simulation; methods share innovations WITHIN a stream. Maurer--Pontil (2009),
Theorem 11, permits the resulting independent, nonidentical path variables.

This module does not create simulation arrays or validate a simulator's bias
proof. It requires certified clipping-tail and numerical-transfer allowances.
Only arrays independent of training/selection/stopping may enter final inference.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import math
from typing import Iterable, Mapping, Sequence

import numpy as np


def _up(x: Decimal | float) -> float:
    return math.nextafter(float(x), math.inf)


def _down(x: Decimal | float) -> float:
    return math.nextafter(float(x), -math.inf)


def _finite_nonnegative(x: float, label: str) -> float:
    x = float(x)
    if not math.isfinite(x) or x < 0:
        raise ValueError(f"{label} must be finite and nonnegative")
    return x


def _exact_moments(x: Sequence[float]) -> tuple[int, int, int, int]:
    """Exact rational mean and unbiased variance of binary64 inputs."""
    ratios=[float(v).as_integer_ratio() for v in x]
    denominator=max(q for _,q in ratios)  # all denominators are powers of two
    integers=[p*(denominator//q) for p,q in ratios]
    total=sum(integers);square_total=sum(z*z for z in integers);n=len(integers)
    return total,n*denominator,n*square_total-total*total,n*(n-1)*denominator**2


def _mean_upper(x: Sequence[float]) -> float:
    if all(float(v)==0 for v in x):return 0.
    ratios=[float(v).as_integer_ratio() for v in x]
    denominator=max(q for _,q in ratios)
    numerator=sum(p*(denominator//q) for p,q in ratios)
    with localcontext() as ctx:
        ctx.prec=80;ctx.rounding=ROUND_CEILING
        return _up(Decimal(numerator)/Decimal(len(ratios)*denominator))


@dataclass(frozen=True)
class ConfidenceBudget:
    """Two-sided events; event counts are fixed before any outcome is read."""
    alpha: float
    event_count: int

    def __post_init__(self):
        if not 0 < self.alpha < 1 or self.event_count < 1:
            raise ValueError("invalid confidence allocation")

    @property
    def event_alpha(self) -> float:
        return math.nextafter(self.alpha / self.event_count, 0.)

    def as_dict(self) -> dict:
        return dict(alpha=self.alpha, event_count=self.event_count,
                    event_alpha=self.event_alpha, sides=2,
                    log_factor="log(4/event_alpha)")


def empirical_bernstein(values: Sequence[float], *, bound: float,
                        event_alpha: float, bias: float = 0.,
                        clipping_tail: float = 0.) -> dict:
    """Two-sided finite-sample EB for independent, not necessarily iid paths.

    Each preclipped value has support [-bound,bound]. bias bounds the difference
    between the target expectation and the untruncated numerical statistic;
    clipping_tail bounds E|X-clip(X)|. A fresh array or prespecified finite-look
    union is required. event_alpha is the error probability for BOTH tails.
    Exact integer moments and directed Decimal arithmetic bound roundoff.
    """
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all():
        raise ValueError("at least two finite independent observations required")
    bound = _finite_nonnegative(bound, "bound")
    bias = _finite_nonnegative(bias, "bias")
    clipping_tail = _finite_nonnegative(clipping_tail, "clipping_tail")
    if not 0 < event_alpha < 1:
        raise ValueError("event_alpha must lie in (0,1)")
    if bound==0 and bias==0 and clipping_tail==0:
        if np.count_nonzero(x):raise ValueError("exact-zero range requires zero observations")
        return dict(paths=len(x),mean=0.,clipped_mean=0.,variance=0.,range_lower=0.,range_upper=0.,
                    empirical_bernstein_margin=0.,bias=0.,clipping_tail=0.,lower=0.,upper=0.,
                    event_alpha=event_alpha,clipped_paths=0,theorem="exact deterministic zero identity",
                    sampling_unit="one independent confirmation path")
    y = np.clip(x, -bound, bound)
    mean_num,mean_den,var_num,var_den=_exact_moments(y)
    with localcontext() as ctx:
        ctx.prec = 80;ctx.rounding=ROUND_FLOOR
        center_lo=Decimal(mean_num)/Decimal(mean_den)
        ctx.rounding=ROUND_CEILING
        center_hi=Decimal(mean_num)/Decimal(mean_den)
        variance=Decimal(var_num)/Decimal(var_den)
        n = Decimal(len(y))
        # Decimal ln and sqrt are correctly rounded with half-even; next_plus
        # makes each an upper endpoint irrespective of its last rounded digit.
        ell = ctx.next_plus((Decimal(4) / Decimal.from_float(float(event_alpha))).ln())
        width = Decimal(2) * Decimal.from_float(bound)
        margin = ctx.next_plus((Decimal(2)*variance*ell/n).sqrt()) + Decimal(7)*width*ell/(Decimal(3)*(n-1))
        allowance = Decimal.from_float(bias) + Decimal.from_float(clipping_tail)
        high = _up(center_hi+margin+allowance)
        ctx.rounding=ROUND_FLOOR
        low = _down(center_lo-margin-allowance)
    return dict(paths=len(x), mean=float(x.mean()), clipped_mean=float(center_lo),
                variance=float(variance), range_lower=-bound, range_upper=bound,
                empirical_bernstein_margin=_up(margin), bias=bias,
                clipping_tail=clipping_tail, lower=low, upper=high,
                event_alpha=event_alpha, clipped_paths=int(np.count_nonzero(x != y)),
                theorem="Maurer--Pontil (2009), Theorem 11; two tails by union",
                sampling_unit="one independent confirmation path")


def finite_stream_mean(values_by_seed: Mapping[int, Sequence[float]], *,
                       declared_seeds: Sequence[int],
                       noise_keys: Mapping[int, str],
                       bounds: Mapping[int, float],
                       biases: Mapping[int, float],
                       clipping_tails: Mapping[int, float],
                       event_alpha: float,
                       confirmation_independent_of_selection: bool) -> dict:
    """Certified mean over ALL declared streams, with no seed attrition.

    The caller must supply a fallback policy for failed fits. Missing seeds are
    errors, never silently dropped. Unequal n would change the target and is
    rejected. If shared noise is used across seeds, first average across seeds
    within each independent noise block and use empirical_bernstein on blocks;
    do not flatten dependent observations into a larger fictitious sample.
    """
    seeds = list(declared_seeds)
    if not seeds or len(seeds) != len(set(seeds)):
        raise ValueError("declared seeds must be nonempty and unique")
    required = set(seeds)
    for name, data in [("values", values_by_seed), ("noise_keys", noise_keys),
                       ("bounds", bounds), ("biases", biases),
                       ("clipping_tails", clipping_tails)]:
        if set(data) != required:
            raise ValueError(f"{name}: exact complete declared stream set required")
    if not confirmation_independent_of_selection:
        raise ValueError("stop/selection arrays cannot be pooled as fresh confirmation")
    if len(set(noise_keys.values())) != len(seeds):
        raise ValueError("confirmation noise must be independent across seed strata")
    arrays = [np.asarray(values_by_seed[s], dtype=np.float64) for s in seeds]
    if any(a.ndim != 1 or len(a) < 2 or not np.isfinite(a).all() for a in arrays):
        raise ValueError("invalid confirmation path vector")
    if len({len(a) for a in arrays}) != 1:
        raise ValueError("equal paths per seed required for uniform method target")
    # Clip each stratum at its certified range, then use a common maximal range.
    # The allowance is the uniform mean of stratum allowances, not their maximum.
    for s in seeds:
        for label, data in [("bound",bounds),("bias",biases),("tail",clipping_tails)]:
            _finite_nonnegative(data[s],label)
    clipped = np.concatenate([np.clip(a,-bounds[s],bounds[s]) for s,a in zip(seeds,arrays)])
    avg_bias = _mean_upper([biases[s] for s in seeds])
    avg_tail = _mean_upper([clipping_tails[s] for s in seeds])
    answer=empirical_bernstein(clipped,bound=max(bounds.values()),event_alpha=event_alpha,
                               bias=avg_bias,clipping_tail=avg_tail)
    answer.update(target="uniform expectation over the complete declared algorithm-stream set",
                  declared_seeds=seeds,seed_count=len(seeds),paths_per_seed=len(arrays[0]),
                  raw_mean=float(np.mean([a.mean() for a in arrays])),
                  per_seed_means={str(s):float(a.mean()) for s,a in zip(seeds,arrays)},
                  clipped_paths=sum(int(np.count_nonzero(a!=np.clip(a,-bounds[s],bounds[s]))) for s,a in zip(seeds,arrays)),
                  training_distribution="exhaustively enumerated; no unseen-seed population claim",
                  random_seed_variation="part of the finite method distribution, not omitted or estimated from a subset",
                  confirmation_noise_keys={str(s):noise_keys[s] for s in seeds})
    return answer


def paired_difference(left: Sequence[float], right: Sequence[float], *,
                      left_identity: Mapping, right_identity: Mapping) -> np.ndarray:
    """Direct difference; no subtraction of separately certified lower bounds."""
    keys=("initial_profile_hash","initial_state_hash","terminal_anchor_hash","noise_hash","steps","paths","stream_seed","confirmation_bank","primitives_sha256")
    for key in keys:
        if key not in left_identity or left_identity[key] != right_identity.get(key):
            raise ValueError(f"unpaired method observations: {key}")
    a,b=np.asarray(left,dtype=np.float64),np.asarray(right,dtype=np.float64)
    if a.shape!=b.shape or a.ndim!=1 or not(np.isfinite(a).all() and np.isfinite(b).all()):
        raise ValueError("invalid paired arrays")
    return a-b


def economic_decision(lower: float, upper: float, margin: float) -> dict:
    """Signed advantage and practical equivalence are separate conclusions."""
    if not(math.isfinite(lower) and math.isfinite(upper)) or lower>upper:
        raise ValueError("invalid interval")
    margin=_finite_nonnegative(margin,"economic margin")
    if margin==0:raise ValueError("equivalence needs a positive economic margin")
    return dict(statistical_superiority=lower>0,
                economically_material_superiority=lower>margin,
                noninferiority=lower>-margin,
                practical_equivalence=lower>-margin and upper<margin,
                economically_material_inferiority=upper<-margin,
                unresolved=not(lower>margin or upper<-margin or (lower>-margin and upper<margin)))


def certified_attainment_fraction(intervals: Mapping[int, Mapping], *,
                                  declared_seeds: Sequence[int], target: float) -> dict:
    """Bounds on true attainment probability under the finite uniform law.

    Assumes simultaneous seed intervals. No binomial confidence interval is
    appropriate: the declared seed population has been exhaustively enumerated.
    """
    if set(intervals)!=set(declared_seeds):raise ValueError("missing stream")
    n=len(declared_seeds)
    if n==0:raise ValueError("empty stream distribution")
    definite=sum(intervals[s]["lower"]>=target for s in declared_seeds)
    possible=sum(intervals[s]["upper"]>=target for s in declared_seeds)
    return dict(target=target,seed_count=n,definitely_attaining=definite,
                possibly_attaining=possible,probability_lower=definite/n,
                probability_upper=possible/n,
                scope="finite declared stream population; simultaneous final intervals")


def fee_to_utility(rate: float, discount: float, horizon: float) -> float:
    if not 0<=rate<1 or discount<0 or horizon<=0:raise ValueError("invalid fee conversion")
    annuity=horizon if discount==0 else -math.expm1(-discount*horizon)/discount
    return -annuity*math.log1p(-rate)


def work_distribution(records: Mapping[int, Mapping], declared_seeds: Sequence[int],
                      *, seconds_cap: float) -> dict:
    """Exact finite-stream work distribution, retaining capped failures.

    No median over successful runs only. Times are hardware-conditioned observed
    quantities. `attained` means an actually executed online stop/check, never a
    retrospective interpolation. Capped unsuccessful runs have infinite work to
    certified target; restricted mean work is min(T,cap), including failures.
    """
    if set(records)!=set(declared_seeds):raise ValueError("missing stream work record")
    if seconds_cap<=0:raise ValueError("positive work cap required")
    times=[];restricted=[];consumed=[]
    for s in declared_seeds:
        r=records[s]
        if not r.get("actual_early_stopping_execution",False):raise ValueError("retrospective frontier is not a stopping run")
        elapsed=_finite_nonnegative(r["end_to_end_seconds"],"inclusive elapsed seconds")
        consumed.append(elapsed)
        times.append(elapsed if r["attained"] else math.inf)
        restricted.append(min(elapsed,seconds_cap) if r["attained"] else seconds_cap)
    ordered=sorted(times);median=ordered[(len(times)-1)//2]
    return dict(seed_count=len(times),attained_count=sum(math.isfinite(t) for t in times),
                median_time_to_target=median if math.isfinite(median) else None,
                median_not_attained=not math.isfinite(median),
                median_definition="lower 0.5 quantile of the finite stream distribution",
                mean_consumed_seconds=sum(consumed)/len(consumed),
                restricted_mean_time=sum(restricted)/len(restricted),seconds_cap=seconds_cap,
                note="Uniform finite-stream distribution on the recorded execution environment; failures retained.")


def audit_descriptive_decomposition(components_by_seed: Mapping[int, Mapping],
                                    declared_seeds: Sequence[int]) -> dict:
    """Audit a descriptive numerical payoff decomposition, without component CIs.

    Only the TOTAL payoff receives the separately established continuous-time
    certificate. There is no arbitrary allocation of that allowance to these
    components and no claim of a signed continuous-time component effect.
    """
    if set(components_by_seed)!=set(declared_seeds) or not declared_seeds:
        raise ValueError("complete declared stream set required")
    rows={};sizes=set();max_error=0.
    keys=("production","consumption_deficit","terminal_gain","paired_gain")
    for seed in declared_seeds:
        data=components_by_seed[seed]
        if any(k not in data for k in keys):raise ValueError("missing decomposition component")
        arrays={k:np.asarray(data[k],dtype=np.float64) for k in keys}
        n=len(arrays['paired_gain'])
        if n<2 or any(a.ndim!=1 or len(a)!=n or not np.isfinite(a).all() for a in arrays.values()):
            raise ValueError("invalid decomposition arrays")
        sizes.add(n)
        reconstructed=arrays['production']-arrays['consumption_deficit']+arrays['terminal_gain']
        error=float(np.max(np.abs(reconstructed-arrays['paired_gain'])))
        scale=max(float(np.max(np.abs(a))) for a in arrays.values())
        tolerance=64*np.finfo(float).eps*max(scale,np.finfo(float).tiny)
        if error>tolerance:raise ValueError("pathwise payoff decomposition identity failed")
        max_error=max(max_error,error)
        rows[str(seed)]={
            'production':float(np.mean(arrays['production'])),
            'consumption_contribution':-float(np.mean(arrays['consumption_deficit'])),
            'terminal_dispersion_contribution':float(np.mean(arrays['terminal_gain'])),
            'total_numerical_gain':float(np.mean(arrays['paired_gain']))}
    if len(sizes)!=1:raise ValueError("equal paths per seed required")
    mean={k:float(np.mean([row[k] for row in rows.values()])) for k in next(iter(rows.values()))}
    return dict(seed_count=len(declared_seeds),paths_per_seed=sizes.pop(),
                method_means=mean,per_seed_means=rows,max_path_identity_error=max_error,
                inference="descriptive only; no component confidence intervals",
                scope="observed finite-step numerical common-path decomposition; only the total payoff has a separate continuous-time certificate")
