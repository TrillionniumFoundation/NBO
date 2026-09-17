#!/usr/bin/env python3
"""Independent R9 referee checks. Standard library only; no author-code imports.

Exact rational toy tests support stated finite-model propositions, not a proof
of them. Portfolio quantities below are TRANSCRIBED author results, not new
full-model solves. Decimal computations are high precision, not interval proofs.
Run: python independent_audit.py > independent_audit_results.json
"""
from __future__ import annotations
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from itertools import product
import json
import random

BASE = '8c1e0472279fb66a2419b63b3e35df028ecfdd78'
CHECKS: dict[str, int] = {}


def check(condition: bool, name: str) -> None:
    if not condition:
        raise AssertionError(name)
    CHECKS[name] = CHECKS.get(name, 0) + 1


class Toy:
    """Two states, four operating actions, affine endpoint laws, killed mass."""
    def __init__(self, seed: int, horizon: int):
        rng = random.Random(seed)
        self.h = horizon
        self.g = [Q(rng.randint(-2, 5), 10) for _ in range(2)]
        self.r, self.a, self.k = {}, {}, {}
        for n, x, act, e in product(range(horizon), range(2), range(4), range(2)):
            key = n, x, act, e
            self.r[key] = Q(rng.randint(-8, 3), 10)
            self.a[key] = Q(rng.randint(0, 2), 8)
            w = rng.randint(0, 6)
            self.k[key] = [Q(w, 8), Q(6 - w, 8)]
        self.reachable = [{0}]
        for n in range(horizon):
            self.reachable.append({y for x in self.reachable[-1]
                for act in range(4) for e in range(2) for y in range(2)
                if self.k[n, x, act, e][y] > 0})

    def acts(self, adj: bool, n: int, sign: int | None = None) -> list[int]:
        aa = list(range(4 if adj else 2))
        return [a for a in aa if n != 0 or sign is None or a % 2 == sign]

    def backup(self, n: int, x: int, act: int, v: list[Q], lam: Q, d: Q) -> Q:
        return sum(prob * (self.r[n, x, act, e] + d*self.a[n, x, act, e]
            + sum(self.k[n, x, act, e][y]*v[y] for y in range(2)))
            for e, prob in ((0, 1-lam), (1, lam)))

    def solve(self, adj: bool, lam: Q, d: Q, m: int, fee: Q,
              sign: int | None = None) -> list[list[Q]]:
        vv = [[Q(0), Q(0)] for _ in range(self.h)] + [self.g[:]]
        for n in range(self.h-1, -1, -1):
            for x in range(2):
                candidates = [self.backup(n, x, a, vv[n+1], lam, d)
                              for a in self.acts(adj, n, sign)]
                if n >= m:
                    candidates.append(self.g[x]-fee)
                vv[n][x] = max(candidates)
        return vv

    def threshold(self, vv: list[list[Q]], m: int) -> Q:
        return max([Q(0)] + [self.g[x]-vv[n][x]
            for n in range(m, self.h) for x in self.reachable[n]])

    def enumerate_initial(self, adj: bool, lam: Q, d: Q, fee: Q, sign: int) -> tuple[Q, int]:
        # Horizon two: explicitly evaluate every full Markov policy; no maximized
        # continuation values are used. STOP=-1 is eligible only at the last date.
        if self.h != 2:
            raise ValueError('enumerator is intentionally a two-date test')
        choices = [self.acts(adj, 0, sign)]*2 + [self.acts(adj, 1)+[-1]]*2
        best, count = None, 0
        for policy in product(*choices):
            end = []
            for x in range(2):
                a = policy[2+x]
                if a == -1:
                    end.append(self.g[x]-fee)
                else:
                    # Separate explicit path expectation, not Toy.backup.
                    end.append(sum(prob*(self.r[1,x,a,e]+d*self.a[1,x,a,e]
                        + sum(self.k[1,x,a,e][y]*self.g[y] for y in range(2)))
                        for e,prob in ((0,1-lam),(1,lam))))
            a = policy[0]
            value = sum(prob*(self.r[0,0,a,e]+d*self.a[0,0,a,e]
                    + sum(self.k[0,0,a,e][y]*end[y] for y in range(2)))
                    for e,prob in ((0,1-lam),(1,lam)))
            best = value if best is None else max(best,value)
            count += 1
        assert best is not None
        return best, count


def exact_tests() -> dict:
    models = 18
    for i in range(models):
        t = Toy(2026091700+i, 2+i % 4)
        for lam in (Q(0), Q(1,3), Q(1)):
            mandatory = {a: t.solve(a,lam,Q(2,5),t.h,Q(0)) for a in (False,True)}
            previous = {False: None, True: None}
            for m in range(1,t.h+1):
                thresholds = {}
                for adj in (False,True):
                    vv = mandatory[adj]
                    star = t.threshold(vv,m)
                    thresholds[adj] = star
                    if previous[adj] is not None:
                        check(star <= previous[adj], 'minimum_term_order')
                    previous[adj] = star
                    hi_d = t.solve(adj,lam,Q(3,5),t.h,Q(0))
                    check(t.threshold(hi_d,m) <= star, 'benefit_threshold_order')
                    for fee in (star, star+Q(1,7)):
                        ww = t.solve(adj,lam,Q(2,5),m,fee)
                        check(all(ww[n][x] == vv[n][x] for n in range(t.h+1)
                                  for x in t.reachable[n]), 'statewise_sufficiency')
                        for sign in (0,1):
                            v0 = t.solve(adj,lam,Q(2,5),t.h,Q(0),sign)[0][0]
                            w0 = t.solve(adj,lam,Q(2,5),m,fee,sign)[0][0]
                            check(v0 == w0, 'initial_class_implementation')
                    if star > 0:
                        ww = t.solve(adj,lam,Q(2,5),m,star/2)
                        check(any(ww[n][x] > vv[n][x] for n in range(m,t.h)
                                  for x in t.reachable[n]), 'statewise_necessity')
                    left = t.solve(adj,lam,Q(1,5),m,Q(1,10))
                    right = t.solve(adj,lam,Q(3,5),m,Q(7,10))
                    mid = t.solve(adj,lam,Q(2,5),m,Q(2,5))
                    check(all(2*mid[n][x] <= left[n][x]+right[n][x]
                              for n in range(t.h+1) for x in range(2)), 'joint_convexity')
                    lowfee = t.solve(adj,lam,Q(2,5),m,Q(1,10))
                    highfee = t.solve(adj,lam,Q(2,5),m,Q(7,10))
                    check(all(Q(0) <= lowfee[n][x]-highfee[n][x] <= Q(3,5)
                              for n in range(t.h+1) for x in range(2)), 'fee_order_lipschitz')
                check(thresholds[True] <= thresholds[False], 'adjustment_capacity_order')
    policies, comparisons = 0, 0
    for i in range(8):
        t = Toy(2026091800+i,2)
        for adj,sign,lam in product((False,True),(0,1),(Q(0),Q(1,3),Q(1))):
            brute, count = t.enumerate_initial(adj,lam,Q(2,5),Q(3,10),sign)
            check(brute == t.solve(adj,lam,Q(2,5),1,Q(3,10),sign)[0][0],
                  'exhaustive_policy_agreement')
            policies += count
            comparisons += 1
    return {'frontier_models':models, 'horizons':[2,3,4,5],
            'law_probabilities':['0','1/3','1'], 'enumeration_models':8,
            'enumerated_policy_evaluations':policies,
            'enumerated_class_point_comparisons':comparisons,
            'assertions':dict(CHECKS), 'total_assertions':sum(CHECKS.values()),
            'arithmetic':'exact fractions', 'passed':True}


def primitive_tests() -> dict:
    with localcontext() as ctx:
        ctx.prec = 65
        D = Decimal
        def utility(c: Decimal, theta: Decimal) -> Decimal:
            z = 1+theta
            return -(-z*c.ln()).exp()/z
        def marginal(c: Decimal, theta: Decimal) -> Decimal:
            z = 1+theta
            return (-z*c.ln()).exp()*(1+z*c.ln())/(z*z)
        def optimum(cons: list[tuple[Decimal,Decimal]], k: Decimal, a: Decimal):
            lo,hi = D('-.2'),D('.2')
            def der(th):
                return sum(pr*marginal(c,th) for c,pr in cons)+a-k*th
            if der(lo)<=0: th=lo
            elif der(hi)>=0: th=hi
            else:
                for _ in range(225):
                    mid=(lo+hi)/2
                    if der(mid)>0: lo=mid
                    else: hi=mid
                th=(lo+hi)/2
            gain=sum(pr*(utility(c,th)-utility(c,D(0))) for c,pr in cons)+a*th-k*th*th/2
            return th,gain
        rows=[]
        for p,k,a in product(map(D,('.06','.08','.10')), map(D,('20','40','80')), map(D,('-.25','0','.25'))):
            plus,op=optimum([(D('.05'),p),(D('.8'),1-p)],k,a)
            minus,om=optimum([(D('.5'),D(1))],k,a)
            check(plus<0<minus, 'primitive_adjustment_directions')
            rows.append({'p':str(p),'k':str(k),'a':str(a),'theta_positive':str(plus),
                         'theta_nonpositive':str(minus),'relative_option':str(op-om)})
        bound=((D('1.482')-D('.25'))**2*20/(20+D('17.342'))-(D('.6138')+D('.25'))**2)/160
        return {'precision':65,'cases_checked':len(rows),
                'center_row':next(r for r in rows if r['p']=='0.08' and r['k']=='40' and r['a']=='0'),
                'uniform_lower_bound_recalculation':str(bound),
                'uniform_positive_class_derivative_upper_bound':'-1.232',
                'uniform_nonpositive_class_derivative_lower_bound':str(2*(1-D(2).ln())-D('.25')),
                'scope':'Decimal optimizer checks are not interval proofs; uniform direction follows analytically from cited shadow bounds and strict concavity'}


def economic_diagnostics() -> dict:
    D=Decimal
    with localcontext() as ctx:
        ctx.prec=55
        # Direct transcription from output/procurement.json at BASE.
        rows=[]
        for regime,aa,qq in (
            ('adjusted','0.890233276155981','0.781344080901693'),
            ('no_adjustment','0.8878979357486028','0.8165920768823858')):
            A,q=D(aa),D(qq)
            rows.append({'regime':regime,'duration_transcribed':aa,'grant_before_capacity_transcribed':qq,
                'surplus_m1_F085_C001':str(D('.9')*A-q-D('.01')),
                'surplus_m8_F0_C0':str(D('.9')*A-q),
                'surplus_gain_same_operating_policy':'.01'})
        # S.13 supplies a sufficient stored-array uniform enforcement bound.
        slack=D('.85')-D('.8348592805606')
        # Nested agent-policy sets need not improve principal service surplus.
        outside,b=D(1),D('.8')
        oldW,oldA,newW,newA=map(D,('.4','1','.5','.1'))
        toy={'outside':'1','service_price':'.8','old_agent_value':str(oldW),
             'new_agent_value':str(newW),'old_duration':str(oldA),'new_duration':str(newA),
             'old_grant':str(outside-oldW),'new_grant':str(outside-newW),
             'old_principal_surplus':str(b*oldA-(outside-oldW)),
             'new_principal_surplus':str(b*newA-(outside-newW)),
             'scope':'separate illustrative two-policy example; not the NBO calibration; not a counterexample to Proposition r9_participation'}
        check(D(toy['new_grant'])<D(toy['old_grant']), 'grant_example_decreases')
        check(D(toy['new_principal_surplus'])<D(toy['old_principal_surplus']), 'grant_example_surplus_decreases')
        check(slack>0, 'certified_fee_strictly_above_sufficient_frontier')
        return {'author_data_source':f'{BASE}:replication/r9/output/procurement.json',
                'commitment_comparison':rows,
                'additional_comparison_assumption':'C(0)=0; identical agent-policy selection; m=8 is admissible without a separate mandatory-commitment cost, as in the declared family',
                'minimum_fee_minus_sufficient_frontier':str(slack),
                'fee_box_implication':'conditional on the deposited sufficient bound, surrender is strictly suboptimal at all reachable eligible nodes throughout the advertised fee box; S=0 and W_F=0 there',
                'nested_policy_counterexample':toy,
                'full_portfolio_model_rerun':False}


def main() -> None:
    tests=exact_tests()
    primitive=primitive_tests()
    economics=economic_diagnostics()
    result={'reviewed_commit':BASE,'exact_toy_tests':tests,'primitive':primitive,
            'economic_diagnostics':economics,'all_assertions':CHECKS,
            'total_all_assertions':sum(CHECKS.values()),
            'scope':'Independent rational toy and Decimal checks only. No author solver imported. No full portfolio rerun, PDF build, neural training, or constructor interval enclosure.'}
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))

if __name__=='__main__':
    main()
