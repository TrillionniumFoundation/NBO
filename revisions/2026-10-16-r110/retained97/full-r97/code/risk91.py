"""Exact finite-law implementation of the R91 signed qualification formula.

This module supplies deterministic verification fixtures, not an investment
experiment. A certificate's input enclosures must be verified independently;
finite arithmetic alone cannot establish their continuous-domain validity.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

F = Fraction
Exact = int | str | Fraction


def rational(value: Exact) -> Fraction:
    """Reject binary floats, booleans and non-rational inputs at the boundary."""
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise TypeError("An exact integer, rational string or Fraction is required")
    return F(value)


def law(values: Sequence[Exact], probabilities: Sequence[Exact]) -> tuple:
    values, probabilities = tuple(map(rational, values)), tuple(map(rational, probabilities))
    if not values or len(values) != len(probabilities):
        raise ValueError("A nonempty finite law with matching lengths is required")
    if any(p < 0 for p in probabilities) or sum(probabilities) != 1:
        raise ValueError("Probabilities must be nonnegative and sum exactly to one")
    return values, probabilities


def avar(values: Sequence[Exact], probabilities: Sequence[Exact], alpha: Exact) -> Fraction:
    """Upper-tail AVaR by minimization over all support thresholds; atoms retained."""
    values, probabilities = law(values, probabilities)
    alpha = rational(alpha)
    if not 0 <= alpha < 1:
        raise ValueError("The AVaR level must lie in [0,1)")
    return min(z + sum(p * max(v-z, 0) for v, p in zip(values, probabilities))/(1-alpha)
               for z in values)


@dataclass(frozen=True)
class Stage:
    lower_residual: Fraction
    upper_residual: Fraction
    greediness: Fraction
    lower_transfer: Fraction
    actor_upper_transfer: Fraction

    def __post_init__(self):
        for name in self.__dataclass_fields__:
            object.__setattr__(self, name, rational(getattr(self, name)))
        if self.lower_residual > self.upper_residual or self.greediness < 0:
            raise ValueError("Reversed residual interval or negative greediness")
        if self.lower_transfer > self.actor_upper_transfer:
            raise ValueError("Incompatible all-action lower and actor upper enclosures")

    @property
    def allowance(self) -> Fraction:
        return (self.upper_residual-self.lower_residual + self.greediness
                + self.actor_upper_transfer-self.lower_transfer)


def certificate(stages: Sequence[Stage], discounts: Sequence[Exact],
                terminal_lower: Exact = 0, terminal_upper: Exact = 0) -> dict:
    discounts = tuple(map(rational, discounts))
    if len(stages) != len(discounts) or any(b < 0 for b in discounts):
        raise ValueError("One nonnegative exact discount is required per stage")
    dl, du = rational(terminal_lower), rational(terminal_upper)
    if dl > du:
        raise ValueError("Reversed terminal enclosure")
    weight, dated = F(1), []
    for stage, beta in zip(stages, discounts):
        if not isinstance(stage, Stage):
            raise TypeError("Each dated input must be a validated Stage")
        dated.append(weight * stage.allowance)
        weight *= beta
    terminal = weight * (du-dl)
    return {"bound": sum(dated, terminal), "dated": tuple(dated), "terminal": terminal}


def avar_transport(lipschitz: Exact, distance: Exact, alpha: Exact) -> Fraction:
    k, e, alpha = map(rational, (lipschitz, distance, alpha))
    if k < 0 or e < 0 or not 0 <= alpha < 1:
        raise ValueError("Invalid transport modulus, distance or risk level")
    return k * e / (1-alpha)


def q_values(costs, transitions, successor, beta: Exact, alpha: Exact):
    """Numerical Bellman action values at one date, for a stored continuation."""
    beta = rational(beta)
    if beta < 0 or len(costs) != len(transitions):
        raise ValueError("Invalid dated costs or discount")
    output = []
    for row, laws in zip(costs, transitions):
        if not row or len(row) != len(laws):
            raise ValueError("Every state needs its complete nonempty action menu")
        output.append(tuple(rational(c) + beta * avar(successor, p, alpha)
                            for c, p in zip(row, laws)))
    return tuple(output)


def qualify(numerical_q, stored, actor, lower_transfer: Exact,
            actor_upper_transfer: Exact) -> Stage:
    """Compute finite-domain residuals only; do not infer unseen-state coverage."""
    if not numerical_q or not len(numerical_q) == len(stored) == len(actor):
        raise ValueError("State, continuation and action dimensions must match")
    residuals, gaps = [], []
    for q, f, a in zip(numerical_q, stored, actor):
        q = tuple(map(rational, q))
        if not q or isinstance(a, bool) or not isinstance(a, int) or not 0 <= a < len(q):
            raise ValueError("The actor must select an original feasible menu entry")
        residuals.append(min(q)-rational(f)); gaps.append(q[a]-min(q))
    return Stage(min(residuals), max(residuals), max(gaps),
                 rational(lower_transfer), rational(actor_upper_transfer))
