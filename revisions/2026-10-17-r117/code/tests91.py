"""Deterministic R91 counterexamples and exact finite-policy regression tests."""
from fractions import Fraction as F
import itertools, json, pathlib, unittest
import risk91 as r
import independent91 as independent


def fixture(case):
    costs = tuple(tuple(tuple(F((t+1)*(x+1)+a*(2-x), 16) for a in range(2))
                        for x in range(2)) for t in range(3))
    original, numerical = [], []
    for t in range(3):
        po, pn = [], []
        for x in range(2):
            aa, bb = [], []
            for a in range(2):
                p = F(2+((t+x+2*a) % 5), 8)
                q = (max(F(0), p-F(1,8)) if case == 0 else
                     (F(a) if case == 1 else min(F(1), p+F(1,8))))
                aa.append((p,1-p)); bb.append((q,1-q))
            po.append(tuple(aa)); pn.append(tuple(bb))
        original.append(tuple(po)); numerical.append(tuple(pn))
    stored = ((F(1,8),F(-1,8)),(F(1,4),F(3,8)),
              (F(-1,4),F(1,2)),(F(1,8),F(7,8)))
    return costs, tuple(original), tuple(numerical), (F(0),F(1)), stored


def exhaustive():
    records, policies_checked, state_inequalities = [], 0, 0
    for case, alpha, beta in itertools.product(range(3), (F(0),F(1,2),F(3,4)), (F(0),F(1,2),F(1))):
        costs, true, numerical, terminal, stored = fixture(case)
        discounts = (beta,)*3
        optimum = independent.original_values(costs,true,terminal,discounts,alpha)[0]
        q = [r.q_values(costs[t],numerical[t],stored[t+1],beta,alpha) for t in range(3)]
        discrepancy = []
        for t in range(3):
            discrepancy.append(tuple(tuple(costs[t][x][a]+beta*independent.tail_dual(
                stored[t+1],true[t][x][a],alpha)-q[t][x][a] for a in range(2)) for x in range(2)))
        max_loss, max_bound, min_slack = F(0),F(0),None
        for flat in itertools.product(range(2),repeat=6):
            policy = tuple(tuple(flat[2*t:2*t+2]) for t in range(3))
            stages = [r.qualify(q[t],stored[t],policy[t],
                      min(v for row in discrepancy[t] for v in row),
                      max(discrepancy[t][x][policy[t][x]] for x in range(2))) for t in range(3)]
            tail = [terminal[x]-stored[-1][x] for x in range(2)]
            bound = r.certificate(stages,discounts,min(tail),max(tail))['bound']
            values = independent.original_values(costs,true,terminal,discounts,alpha,policy)[0]
            for x in range(2):
                loss = values[x]-optimum[x]
                if not 0 <= loss <= bound:
                    raise AssertionError((case,str(alpha),str(beta),flat,x,str(loss),str(bound)))
                max_loss = max(max_loss,loss);max_bound=max(max_bound,bound)
                min_slack = bound-loss if min_slack is None else min(min_slack,bound-loss)
                state_inequalities += 1
            policies_checked += 1
        records.append(dict(case=case,alpha=str(alpha),discount=str(beta),policies=64,
                            max_actual_loss=str(max_loss),max_certificate=str(max_bound),min_slack=str(min_slack)))
    return dict(status='passed',models=len(records),complete_policies=policies_checked,
                initial_state_inequalities=state_inequalities,records=records,
                new_fit_attempts=0,new_independent_economic_rows=0,
                scope='Exhaustive deterministic finite-state diagnostics; not a continuous-domain proof or a vector investment experiment.')


class ExactRiskTests(unittest.TestCase):
    def test_rational_rejects_float(self):
        with self.assertRaises(TypeError):r.rational(.5)
    def test_rational_rejects_bool(self):
        with self.assertRaises(TypeError):r.rational(True)
    def test_unnormalized_law(self):
        with self.assertRaises(ValueError):r.avar([0,1],['1/3','1/3'],0)
    def test_negative_probability(self):
        with self.assertRaises(ValueError):r.avar([0,1],[-1,2],0)
    def test_empty_law(self):
        with self.assertRaises(ValueError):r.avar([],[],0)
    def test_law_length(self):
        with self.assertRaises(ValueError):r.avar([0,1],[1],0)
    def test_level_one_rejected(self):
        with self.assertRaises(ValueError):r.avar([0,1],['1/2','1/2'],1)
    def test_negative_level(self):
        with self.assertRaises(ValueError):r.avar([0,1],['1/2','1/2'],-1)
    def test_atoms_at_quantile_are_retained(self):
        self.assertEqual(r.avar([0,1],[F(3,4),F(1,4)],F(1,2)),F(1,2))
    def test_alpha_zero_is_expectation(self):
        self.assertEqual(r.avar([-3,1,5],[F(1,4),F(1,2),F(1,4)],0),1)
    def test_tail_dual_matches_threshold(self):
        count=0
        for values in itertools.product((-2,0,3),repeat=3):
            for probs in ((F(1,4),F(1,2),F(1,4)),(F(0),F(1,4),F(3,4))):
                for alpha in (F(0),F(1,2),F(3,4),F(7,8)):
                    self.assertEqual(r.avar(values,probs,alpha),independent.tail_dual(values,probs,alpha));count+=1
        self.assertEqual(count,216)
    def test_cash_invariance(self):
        for k in (F(-7),F(1,3),F(100)):
            self.assertEqual(r.avar([k,k+1],[F(3,4),F(1,4)],F(1,2)), k+F(1,2))
    def test_monotone_coupling(self):
        self.assertGreaterEqual(r.avar([1,3],[F(1,4),F(3,4)],F(1,2)),r.avar([0,2],[F(1,4),F(3,4)],F(1,2)))
    def test_tail_transport_factor_is_sharp(self):
        for denominator in (2,4,8,16,32,64):
            h=F(1,denominator)
            difference=r.avar([0,1],[1-h,h],1-h)-r.avar([0],[1],1-h)
            self.assertEqual(difference,r.avar_transport(1,h,1-h));self.assertEqual(difference,1)
    def test_no_uniform_unpriced_tail_limit(self):
        self.assertGreater(r.avar([0,1],[F(63,64),F(1,64)],F(63,64)),F(1,64))
    def test_signed_bound_is_sharp(self):
        for h in (F(1,8),F(1,64),F(1,1024)):
            self.assertEqual(r.certificate([r.Stage(0,0,0,0,h)],[1])['bound'],h)
    def test_signed_beats_symmetric(self):
        self.assertEqual(r.certificate([r.Stage(0,0,0,-1,1)],[1])['bound'],2)
        self.assertEqual(r.certificate([r.Stage(0,0,0,0,1)],[1])['bound'],1)
    def test_global_bias_cancels(self):
        self.assertEqual(r.certificate([r.Stage(-3,-3,0,3,3)],[1])['bound'],0)
    def test_statewise_bias_cannot_cancel(self):
        costs=(((0,0),),((2,), (0,)))
        transitions=((((1,0),(0,1)),),(((1,),),((1,),)))
        vp=independent.original_values(costs,transitions,[0],[1,1],0,((0,),(0,0)))[0][0]
        vo=independent.original_values(costs,transitions,[0],[1,1],0)[0][0]
        self.assertEqual(vp-vo,2)
        self.assertEqual(r.certificate([r.Stage(0,0,0,0,0),r.Stage(0,0,0,0,2)],[1,1])['bound'],2)
    def test_nested_not_static(self):
        static=r.avar([0,0,0,4],[F(1,4)]*4,F(1,2))
        nested=r.avar([r.avar([0,0],[F(1,2)]*2,F(1,2)),r.avar([0,4],[F(1,2)]*2,F(1,2))],[F(1,2)]*2,F(1,2))
        self.assertEqual((static,nested),(2,4))
    def test_negative_discount_rejected(self):
        with self.assertRaises(ValueError):r.certificate([r.Stage(0,0,0,0,0)],[-1])
    def test_discount_dimension(self):
        with self.assertRaises(ValueError):r.certificate([r.Stage(0,0,0,0,0)],[])
    def test_terminal_interval(self):
        with self.assertRaises(ValueError):r.certificate([],[],1,0)
    def test_residual_interval(self):
        with self.assertRaises(ValueError):r.Stage(1,0,0,0,0)
    def test_greediness_nonnegative(self):
        with self.assertRaises(ValueError):r.Stage(0,0,-1,0,0)
    def test_transfer_interval_consistent(self):
        with self.assertRaises(ValueError):r.Stage(0,0,0,1,0)
    def test_infeasible_actor(self):
        with self.assertRaises(ValueError):r.qualify([[0,1]],[0],[2],0,0)
    def test_missing_state(self):
        with self.assertRaises(ValueError):r.qualify([[0,1]],[0],[],0,0)
    def test_actor_error_not_menu_max(self):
        a=r.qualify([[0,1]],[0],[0],-1,0)
        self.assertEqual(a.allowance,1)
    def test_zero_discount_removes_future(self):
        result=r.certificate([r.Stage(0,1,0,0,0),r.Stage(0,100,0,0,0)],[0,1],0,100)
        self.assertEqual(result['bound'],1)
    def test_dated_terminal_weight(self):
        result=r.certificate([r.Stage(0,0,0,0,0)]*2,[F(1,2),F(1,4)],-1,1)
        self.assertEqual(result['terminal'],F(1,4))
    def test_local_risk_factors_do_not_multiply(self):
        local=r.avar_transport(1,F(1,8),F(1,2))
        stages=[r.Stage(0,0,0,-local,local)]*3
        self.assertEqual(r.certificate(stages,[F(1,2)]*3)['bound'],F(7,8))
    def test_shifted_residuals_same_certificate(self):
        a=[r.Stage(-1,2,F(1,4),-2,1),r.Stage(0,1,0,1,2)]
        b=[r.Stage(6,9,F(1,4),-2,1),r.Stage(-3,-2,0,1,2)]
        self.assertEqual(r.certificate(a,[F(1,2),1],-1,1),r.certificate(b,[F(1,2),1],9,11))
    def test_negative_transport_modulus(self):
        with self.assertRaises(ValueError):r.avar_transport(-1,1,0)
    def test_negative_transport_distance(self):
        with self.assertRaises(ValueError):r.avar_transport(1,-1,0)
    def test_exhaustive_complete_policy_qualification(self):
        out=exhaustive();self.assertEqual(out['complete_policies'],1728)
        self.assertEqual(out['initial_state_inequalities'],3456)


if __name__ == '__main__':
    import sys
    if '--write' in sys.argv:
        out=exhaustive();root=pathlib.Path(__file__).resolve().parents[1]
        p=root/'audit/RISK91.json';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'},indent=2))
    else:
        unittest.main(verbosity=2)
