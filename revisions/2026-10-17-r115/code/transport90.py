"""Exact arithmetic for the R90 certificate; fixtures are not economic observations."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Union
import argparse
import json

Q = Fraction
Scalar = Union[int, str, Fraction]

def rational(x: Scalar) -> Fraction:
    if isinstance(x, bool) or not isinstance(x, (int, str, Fraction)):
        raise TypeError('Use integers, rational strings or Fraction; qualify decimal arithmetic separately.')
    return Q(x)

@dataclass(frozen=True)
class Stage:
    lower: Fraction
    upper: Fraction
    greedy: Fraction
    beta: Fraction
    lipschitz: Fraction
    transport: Fraction
    arithmetic: Fraction = Q(0)

    def __post_init__(self) -> None:
        for field in self.__dataclass_fields__:
            object.__setattr__(self, field, rational(getattr(self, field)))
        if self.lower > self.upper:
            raise ValueError('Reversed residual enclosure')
        if any(getattr(self, x) < 0 for x in ('greedy', 'beta', 'lipschitz', 'transport', 'arithmetic')):
            raise ValueError('Negative certificate input')

    @property
    def operator_error(self) -> Fraction:
        return self.beta * self.lipschitz * self.transport + self.arithmetic

    @property
    def local_loss(self) -> Fraction:
        return self.upper - self.lower + self.greedy + 2 * self.operator_error

def finite_bound(stages: Iterable[Stage], terminal_lower: Scalar = 0,
                 terminal_upper: Scalar = 0) -> dict:
    lo, hi = rational(terminal_lower), rational(terminal_upper)
    if lo > hi:
        raise ValueError('Reversed terminal enclosure')
    discount = Q(1)
    residual = greedy = transport = arithmetic = Q(0)
    dated = []
    for t, row in enumerate(stages):
        if not isinstance(row, Stage):
            raise TypeError('Each stage must be a validated Stage')
        residual += discount * (row.upper - row.lower)
        greedy += discount * row.greedy
        transport += 2 * discount * row.beta * row.lipschitz * row.transport
        arithmetic += 2 * discount * row.arithmetic
        dated.append({'date': t, 'discount': discount, 'operator_error': row.operator_error,
                      'loss_allowance': discount * row.local_loss})
        discount *= row.beta
    terminal = discount * (hi - lo)
    return {'bound': residual + greedy + transport + arithmetic + terminal,
            'residual_span': residual, 'greedy': greedy, 'transport': transport,
            'arithmetic': arithmetic, 'terminal_span': terminal, 'dated': dated}

def stationary_bound(stage: Stage) -> Fraction:
    if not Q(0) <= stage.beta < Q(1):
        raise ValueError('A stationary certificate requires 0 <= beta < 1')
    return stage.local_loss / (1 - stage.beta)

def wasserstein_line(points: Iterable[Scalar], first: Iterable[Scalar],
                     second: Iterable[Scalar]) -> Fraction:
    x, p, q = tuple(map(rational, points)), tuple(map(rational, first)), tuple(map(rational, second))
    if not x or len(x) != len(p) or len(x) != len(q):
        raise ValueError('Probability support dimensions differ')
    if any(b <= a for a, b in zip(x, x[1:])):
        raise ValueError('Support must be strictly increasing')
    if min(p + q) < 0 or sum(p) != 1 or sum(q) != 1:
        raise ValueError('Inputs must be probability vectors')
    cumulative = total = Q(0)
    for i in range(len(x) - 1):
        cumulative += p[i] - q[i]
        total += abs(cumulative) * (x[i+1] - x[i])
    return total

def singular_fixture(h: Scalar) -> dict:
    h = rational(h)
    if not 0 < h <= 1:
        raise ValueError('The singular fixture requires 0 < h <= 1')
    cert = finite_bound([Stage(0, 0, 0, 1, 1, h)])
    true_selected, true_optimum = h, h / 2
    return {'h': h, 'selected_true_cost': true_selected, 'optimal_true_cost': true_optimum,
            'true_regret': true_selected-true_optimum, 'nominal_residual_bound': Q(0),
            'certified_bound': cert['bound'], 'transport_distance': h,
            'total_variation_distance': Q(1), 'new_independent_rows': 0}

def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True,
                               default=lambda x: str(x) if isinstance(x, Q) else x) + '\n')

def write_fixture() -> None:
    root = Path(__file__).resolve().parents[1]
    rows = [singular_fixture(Q(1, n)) for n in (4, 16, 64, 256, 1024)]
    save(root/'results90/TRANSPORT90.json', {'status': 'passed', 'rows': rows,
          'scope': 'Exact singular-kernel diagnostic; not investment data, fitting, or new independent observations.'})
    lines = [r'\begin{table}[htbp]', r'\centering',
             r'\caption{Exact singular-transition diagnostic}\label{tab:transport90}',
             r'\begin{tabular}{lllll}', r'\toprule',
             r'$h$ & True regret & Nominal bound & Transport bound & TV distance \\', r'\midrule']
    for row in rows:
        lines.append(' & '.join('$'+str(row[k])+'$' for k in
                     ('h', 'true_regret', 'nominal_residual_bound', 'certified_bound', 'total_variation_distance')) + r' \\')
    lines += [r'\bottomrule', r'\end{tabular}', r'\par\smallskip',
              r'{\footnotesize All entries are exact rational numbers. The zero nominal bound omits the transition charge and is invalid. These five fixtures add no independent economic observations.}', r'\end{table}']
    (root/'tables').mkdir(exist_ok=True)
    (root/'tables/transport90.tex').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status': 'passed', 'fixtures': len(rows), 'new_independent_rows': 0}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write:
        write_fixture()
