"""R47 retrospective witness-precision audit on every unchanged R44 model.

The constructor does not use an exact operating value to construct either
endpoint. Dyadic Bellman enclosures supply the oracle information. An old
feasible policy is a proposal only; it is repaired to the upper witness.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'revisions/2026-09-25-r44'
PRICES = ROOT / 'revisions/2026-09-25-r46'
OUT = ROOT / 'revisions/2026-09-26-r47'
ZERO = F(0)
ONE = F(1)
sys.set_int_max_str_digits(0)


def dot(a, b):
    assert len(a) == len(b)
    return sum((x * y for x, y in zip(a, b)), ZERO)


def floor_to(value, bits):
    scale = 1 << bits
    return F(value.numerator * scale // value.denominator, scale)


def read_model(raw):
    d = dict(raw)
    for key in ('beta', 'epsilon'):
        d[key] = F(raw[key])
    for key in ('nu', 'terminal'):
        d[key] = [F(v) for v in raw[key]]
    for key in ('r', 'k'):
        d[key] = [[F(v) for v in row] for row in raw[key]]
    d['P'] = [[[F(v) for v in row] for row in state] for state in raw['P']]
    return d


def witnesses(d, bits):
    n, T, m, beta = d['n'], d['T'], d['m'], d['beta']
    lo = [[ZERO] * n for _ in range(T + 1)]
    hi = [[ZERO] * n for _ in range(T + 1)]
    lo[T] = [floor_to(v, bits) for v in d['terminal']]
    hi[T] = [-floor_to(-v, bits) for v in d['terminal']]
    for t in reversed(range(T)):
        for i in range(n):
            low = max(d['r'][i][a] + beta * dot(d['P'][i][a], lo[t+1]) for a in range(m))
            high = max(d['r'][i][a] + beta * dot(d['P'][i][a], hi[t+1]) for a in range(m))
            lo[t][i] = floor_to(low, bits)
            hi[t][i] = -floor_to(-high, bits)
    return lo, hi


def lower_certificate(d, lo, hi, prices, bits=44):
    n, T, m, beta, eps = d['n'], d['T'], d['m'], d['beta'], d['epsilon']
    u = [[ZERO] * n for _ in range(T + 1)]
    for t in reversed(range(T)):
        for i in range(n):
            lam = prices[t][i]
            action_values = []
            for a in range(m):
                disadvantage = max(ZERO, lo[t][i] - d['r'][i][a] - beta * dot(d['P'][i][a], hi[t+1]))
                future = [u[t+1][j] + eps * min(lam, prices[t+1][j]) for j in range(n)]
                action_values.append(d['k'][i][a] + lam * (disadvantage - eps) + beta * dot(d['P'][i][a], future))
            u[t][i] = floor_to(min(action_values), bits)
    return dot(d['nu'], [max(ZERO, v) for v in u[0]]), u


def repair_with_upper_witness(d, hi, proposal, bits=40):
    """Choose a continuation-best action; rounding toward it never lowers J."""
    n, T, m, beta, eps = d['n'], d['T'], d['m'], d['beta'], d['epsilon']
    policy = [[[ZERO] * m for _ in range(n)] for _ in range(T)]
    J = [[ZERO] * n for _ in range(T+1)]
    C = [[ZERO] * n for _ in range(T+1)]
    J[T] = d['terminal'][:]
    mixes = []
    for t in reversed(range(T)):
        for i in range(n):
            qa = [d['r'][i][a] + beta * dot(d['P'][i][a], J[t+1]) for a in range(m)]
            best = max(range(m), key=lambda a: qa[a])
            target = hi[t][i] - eps
            if qa[best] < target:
                return None, dict(reason='upper witness not repairable against this continuation', t=t, i=i,
                                  target=str(target), best_action_value=str(qa[best]))
            row = proposal[t][i]
            assert min(row) >= ZERO and sum(row) == ONE
            value = dot(row, qa)
            alpha = ZERO if value >= target else (target-value)/(qa[best]-value)
            mixed = [(ONE-alpha)*v for v in row]
            mixed[best] += alpha
            rounded = [floor_to(v, bits) if a != best else ZERO for a, v in enumerate(mixed)]
            rounded[best] = ONE-sum(rounded)
            assert min(rounded) >= ZERO and sum(rounded) == ONE
            policy[t][i] = rounded
            J[t][i] = dot(rounded, qa)
            C[t][i] = dot(rounded, [d['k'][i][a] + beta*dot(d['P'][i][a], C[t+1]) for a in range(m)])
            assert J[t][i] >= target
            mixes.append(alpha)
    return dict(policy=policy, cost=dot(d['nu'], C[0]), J=J,
                maximum_mixing=max(mixes, default=ZERO)), None


def run(name, bits):
    started = time.perf_counter()
    data = (BASE/'models'/f'{name}.json').read_bytes()
    protocol_data = (BASE/'PROTOCOL.json').read_bytes()
    protocol = json.loads(protocol_data)
    digest = hashlib.sha256(data).hexdigest()
    assert digest == protocol['models_sha256'][name]
    raw = json.loads(data)
    d = read_model(raw)
    source_path = PRICES/'proofs'/name/'restart.json.gz'
    source_bytes = source_path.read_bytes()
    source = json.loads(gzip.decompress(source_bytes))
    assert source['model'] == raw and source['model_sha256'] == digest
    prices = [[F(v) for v in row] for row in source['prices']] + [[ZERO]*d['n']]
    proposal = [[[F(v) for v in row] for row in period] for period in source['policy']]
    lo, hi = witnesses(d, bits)
    witness_seconds = time.perf_counter()-started
    lower, u = lower_certificate(d, lo, hi, prices)
    lower_seconds = time.perf_counter()-started-witness_seconds
    repaired, failure = repair_with_upper_witness(d, hi, proposal)
    widths = [max(y-x for x, y in zip(lrow, hrow)) for lrow, hrow in zip(lo, hi)]
    xi = max(widths[:-1])
    s = (ONE-d['beta'])*d['epsilon']
    lower_budget = sum((d['beta']**t * (max(prices[t])*(widths[t]+d['beta']*widths[t+1])+F(1,2**44)) for t in range(d['T'])), ZERO)
    D_C = max(v for row in d['k'] for v in row)*sum((d['beta']**t*sum((d['beta']**j for j in range(d['T']-t)), ZERO) for t in range(d['T'])), ZERO)
    upper_budget = D_C*min(ONE,xi/s+F(d['m']-1,2**40)) if xi < s else None
    previous_lower, previous_upper = F(source['lower']), F(source['upper'])
    assert ZERO <= previous_lower-lower <= lower_budget
    if repaired is not None:
        upper = repaired['cost']
        assert lower <= upper
        if upper_budget is not None:
            assert upper-previous_upper <= upper_budget
    else:
        upper = None
    proof = dict(schema='nbo-r47-witness-v1', case=name, model=raw, model_sha256=digest,
                 protocol_sha256=hashlib.sha256(protocol_data).hexdigest(),
                 source_price_sha256=hashlib.sha256(source_bytes).hexdigest(),
                 witness_bits=bits, lower_bits=44, policy_bits=40, operating_lower=lo, operating_upper=hi,
                 lower_table=u, lower=lower, upper=upper, policy=repaired['policy'] if repaired else None,
                 failure=failure, uniform_guard_passed=xi<s, witness_width=xi,
                 lower_error_budget=lower_budget, upper_error_budget=upper_budget, target='1/1000')
    path = OUT/'proofs'/f'{name}_b{bits}.json.gz'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(proof,default=str,separators=(',',':')).encode(),mtime=0))
    elapsed = time.perf_counter()-started
    result = dict(name=name,bits=bits,lower=str(lower),upper=str(upper) if upper is not None else None,
                  gap=float(upper-lower) if upper is not None else None,
                  target_met=upper is not None and upper-lower<=F(1,1000),
                  actual_lower_loss=float(previous_lower-lower), lower_budget=float(lower_budget),
                  actual_upper_change=float(upper-previous_upper) if upper is not None else None,
                  upper_budget=float(upper_budget) if upper_budget is not None else None,
                  witness_width=float(xi),guard_passed=xi<s,repair_succeeded=repaired is not None,
                  maximum_mixing=float(repaired['maximum_mixing']) if repaired else None,
                  witness_seconds=witness_seconds,lower_seconds=lower_seconds,total_seconds=elapsed,
                  proof_bytes=path.stat().st_size,proof_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    print(json.dumps(result),flush=True)
    return result


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--names',nargs='+')
    ap.add_argument('--bits',nargs='+',type=int,default=[16,24,32,40])
    args=ap.parse_args()
    names=args.names or [f'{family}{j}' for family in ['maintenance','inventory','queue','tie'] for j in range(4)]
    results=[run(name,bits) for name in names for bits in args.bits]
    (OUT/'results').mkdir(exist_ok=True)
    (OUT/'results/witness_audit.json').write_text(json.dumps(results,indent=2)+'\n')
