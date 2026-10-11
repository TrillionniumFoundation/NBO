"""R73 exact, anytime ledger for original-law NBO cost contrasts.

Range qualifications and target identities must be fixed before each episode.
The API cannot establish that probabilistic assumption on a caller's behalf.
No martingale observation is silently discarded after a numerical failure.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from typing import Sequence


def log_upper(x: F, terms: int = 24) -> F:
    """A rational upper bound on log(x), for x >= 1; no floating logarithm."""
    x = F(x)
    if x < 1 or not isinstance(terms, int) or terms < 1:
        raise ValueError('Require x >= 1 and positive integer series length')
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    def series(z: F) -> F:
        value = sum((2*z**(2*j+1)/F(2*j+1) for j in range(terms)), F(0))
        return value + 2*z**(2*terms+1)/(F(2*terms+1)*(1-z*z))
    return k*series(F(1, 3)) + series((x-1)/(x+1))


@dataclass(frozen=True)
class Qualification:
    target_id: str
    critic_id: str
    lower: F
    upper: F

    def __post_init__(self) -> None:
        if not self.target_id or not self.critic_id or F(self.lower) > F(self.upper):
            raise ValueError('An identified, ordered support is required')


class Ledger:
    """Finite-mixture confidence sequence with predictable, variable ranges.

    In fixed-target mode the target ID includes both complete controllers,
    initial law, model version and episode reset contract. A carried cache
    state can change the conditional target even if the controller code does
    not change. Such deployment belongs in varying-target mode.
    """
    def __init__(self, alpha: F = F(1,100), lambdas: Sequence[F] | None = None,
                 weights: Sequence[F] | None = None, fixed_target: bool = True):
        self.alpha = F(alpha)
        self.lambdas = tuple(map(F,[F(64,2**j) for j in range(16)] if lambdas is None else lambdas))
        self.weights = tuple(map(F,[F(1,(j+1)*(j+2)) for j in range(len(self.lambdas))] if weights is None else weights))
        if not 0 < self.alpha < 1 or len(self.lambdas) != len(self.weights):
            raise ValueError('Invalid error allocation')
        if not self.lambdas or any(x <= 0 for x in self.lambdas+self.weights) or sum(self.weights) > 1:
            raise ValueError('Positive bets and subprobability weights required')
        self.logs = tuple(log_upper(2/(self.alpha*w)) for w in self.weights)
        self.fixed_target = bool(fixed_target)
        self.target_id: str | None = None
        self.pending: Qualification | None = None
        self.n = 0
        self.sum_lower = self.sum_upper = F(0)
        self.support_lower = self.support_upper = F(0)
        self.range_squares = self.work = F(0)
        self.failed_numerical_rows = 0

    def reserve(self, qualification: Qualification) -> None:
        if self.pending is not None:
            raise RuntimeError('Resolve the previous episode, including a failed numerical episode')
        if self.fixed_target and self.target_id not in (None,qualification.target_id):
            raise ValueError('Changed target requires a new error-allocated epoch')
        if self.target_id is None:
            self.target_id = qualification.target_id
        self.pending = qualification

    def include(self, lower: F | None, upper: F | None, work: F = F(0)) -> None:
        if self.pending is None:
            raise RuntimeError('Support must be reserved before observing an episode')
        if F(work) < 0:
            raise ValueError('Negative work')
        q = self.pending
        a,b = F(q.lower),F(q.upper)
        failed = lower is None and upper is None
        if failed:
            l,u = a,b
        elif lower is None or upper is None:
            raise ValueError('Provide both endpoints or neither')
        else:
            lower,upper = F(lower),F(upper)
            if lower > upper:
                raise ValueError('Inverted path enclosure')
            l,u = max(a,lower),min(b,upper)
            if l > u:
                raise ValueError('Empty support intersection: certificate failure, not an observation to discard')
        self.n += 1
        self.sum_lower += l; self.sum_upper += u
        self.support_lower += a; self.support_upper += b
        self.range_squares += (b-a)**2
        self.work += F(work)
        self.failed_numerical_rows += int(failed)
        self.pending = None

    def boundary(self) -> F:
        return min(c/lam + lam*self.range_squares/8 for c,lam in zip(self.logs,self.lambdas))

    def interval(self) -> tuple[F,F]:
        if not self.n or self.pending is not None:
            raise RuntimeError('A completed nonempty prefix is required')
        b = self.boundary()
        return (max(self.support_lower,self.sum_lower-b)/self.n,
                min(self.support_upper,self.sum_upper+b)/self.n)

    def decision(self, margin: F, setup_charge: F = F(0), deployments: int = 1,
                 per_deployment_charge: F = F(0)) -> dict:
        margin = F(margin)
        if margin < 0 or F(setup_charge) < 0 or not isinstance(deployments,int) or deployments < 1:
            raise ValueError('Invalid declared economic decision')
        l,u = self.interval()
        charge = F(setup_charge)/deployments+F(per_deployment_charge)
        return {'target': 'fixed_original_law_cost_difference' if self.fixed_target else 'average_conditional_cost_difference',
                'lower':l,'upper':u,'net_lower':l+charge,'net_upper':u+charge,
                'strict_net_improvement':u+charge<0,
                'equivalent_at_declared_margin':l>=-margin and u<=margin,
                'episodes':self.n,'failed_numerical_rows':self.failed_numerical_rows,
                'paid_work':self.work,'deployment_count':deployments}
