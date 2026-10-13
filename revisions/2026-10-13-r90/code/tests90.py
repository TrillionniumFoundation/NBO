"""Exact fixtures for R90. No test is a new independent economic observation."""
from fractions import Fraction as Q
import itertools
import unittest
import transport90 as m

class InputTests(unittest.TestCase):
    def test_reversed_residual(self):
        with self.assertRaises(ValueError): m.Stage(1, 0, 0, 1, 1, 0)
    def test_each_negative_error_rejected(self):
        for pos in range(2, 7):
            a = [0, 1, 0, 1, 1, 0, 0]; a[pos] = -1
            with self.assertRaises(ValueError): m.Stage(*a)
    def test_signed_residual_is_allowed(self):
        self.assertEqual(m.Stage(-5, -3, 0, 1, 1, 0).local_loss, 2)
    def test_unqualified_binary64_rejected(self):
        with self.assertRaises(TypeError): m.Stage(0, 1, 0, 0.5, 1, 0)
    def test_boolean_rejected(self):
        with self.assertRaises(TypeError): m.rational(True)
    def test_rational_string_accepted(self):
        self.assertEqual(m.Stage('1/3', '2/3', 0, '1/2', 1, 0).beta, Q(1,2))
    def test_terminal_reversal_rejected(self):
        with self.assertRaises(ValueError): m.finite_bound([], 1, 0)
    def test_invalid_stage_rejected(self):
        with self.assertRaises(TypeError): m.finite_bound([{}])
    def test_stationary_unit_discount_rejected(self):
        with self.assertRaises(ValueError): m.stationary_bound(m.Stage(0,1,0,1,1,0))

class AccountTests(unittest.TestCase):
    def test_exact_one_date_budget(self):
        s=m.Stage(-1, 2, Q(1,4), Q(1,2), 3, Q(1,10), Q(1,20))
        self.assertEqual(s.operator_error,Q(1,5))
        self.assertEqual(m.finite_bound([s])['bound'], Q(73,20))
    def test_all_components_add_once(self):
        out=m.finite_bound([m.Stage(-1,2,1,Q(1,2),3,Q(1,5),Q(1,10)),m.Stage(0,1,2,Q(1,3),2,Q(1,6),Q(1,8))],-1,2)
        self.assertEqual(out['bound'],sum(out[k] for k in ('residual_span','greedy','transport','arithmetic','terminal_span')))
        self.assertEqual(out['terminal_span'],Q(1,2))
    def test_transition_receives_next_discount(self):
        out=m.finite_bound([m.Stage(0,0,0,Q(1,2),2,Q(1,3)),m.Stage(0,0,0,Q(1,4),4,Q(1,5))])
        self.assertEqual(out['transport'],Q(2,3)+Q(1,5))
    def test_zero_discount_stops_future_cost(self):
        out=m.finite_bound([m.Stage(0,0,0,0,100,100),m.Stage(0,100,100,1,100,100)],-100,100)
        self.assertEqual(out['bound'],0)
    def test_terminal_span_not_terminal_absolute_level(self):
        self.assertEqual(m.finite_bound([],100,100)['bound'],0)
        self.assertEqual(m.finite_bound([],-2,3)['bound'],5)
    def test_state_constant_residual_shift_is_free(self):
        s=m.Stage(-1,2,1,Q(1,2),2,Q(1,8))
        shifted=m.Stage(6,9,1,Q(1,2),2,Q(1,8))
        self.assertEqual(m.finite_bound([s])['bound'],m.finite_bound([shifted])['bound'])
    def test_stationary_geometric_account(self):
        s=m.Stage(-1,1,0,Q(3,4),1,Q(1,8))
        self.assertEqual(m.stationary_bound(s),Q(35,4))
        self.assertLess(m.finite_bound([s]*20)['bound'],m.stationary_bound(s))
    def test_monotone_transport_precision(self):
        self.assertLess(m.finite_bound([m.Stage(0,0,0,1,1,Q(1,8))])['bound'],m.finite_bound([m.Stage(0,0,0,1,1,Q(1,4))])['bound'])
    def test_empty_horizon_has_only_terminal_span(self):
        self.assertEqual(m.finite_bound([],Q(1,3),Q(2,3))['bound'],Q(1,3))

class TransportTests(unittest.TestCase):
    def test_identical_laws_zero(self):
        self.assertEqual(m.wasserstein_line((0,1),(Q(1,3),Q(2,3)),(Q(1,3),Q(2,3))),0)
    def test_singular_laws(self):
        self.assertEqual(m.wasserstein_line((0,Q(1,8)),(1,0),(0,1)),Q(1,8))
    def test_three_point_mass_transport(self):
        self.assertEqual(m.wasserstein_line((0,1,3),(Q(1,2),0,Q(1,2)),(0,1,0)),Q(3,2))
    def test_probability_mass_required(self):
        with self.assertRaises(ValueError): m.wasserstein_line((0,1),(1,1),(1,0))
    def test_negative_mass_rejected(self):
        with self.assertRaises(ValueError): m.wasserstein_line((0,1),(-1,2),(1,0))
    def test_sorted_support_required(self):
        with self.assertRaises(ValueError): m.wasserstein_line((1,0),(1,0),(0,1))
    def test_support_dimensions_required(self):
        with self.assertRaises(ValueError): m.wasserstein_line((0,1),(1,),(0,1))
    def test_lipschitz_expectation_inequality_independently(self):
        x=(Q(0),Q(1,2),Q(1));p=(Q(1,3),Q(1,6),Q(1,2));q=(Q(1,6),Q(1,2),Q(1,3))
        for f in itertools.product((Q(-1),Q(0),Q(1)),repeat=3):
            K=max(abs(f[i]-f[j])/abs(x[i]-x[j]) for i in range(3) for j in range(i))
            self.assertLessEqual(abs(sum((a-b)*v for a,b,v in zip(p,q,f))),K*m.wasserstein_line(x,p,q))
    def test_singular_fixture_refutes_omitted_charge(self):
        row=m.singular_fixture(Q(1,16))
        self.assertGreater(row['true_regret'],row['nominal_residual_bound'])
        self.assertLessEqual(row['true_regret'],row['certified_bound'])
    def test_transport_converges_without_tv_convergence(self):
        rows=[m.singular_fixture(Q(1,2**k)) for k in range(2,11)]
        self.assertTrue(all(r['total_variation_distance']==1 for r in rows))
        self.assertTrue(all(a['certified_bound']>b['certified_bound'] for a,b in zip(rows,rows[1:])))
    def test_singular_fixture_domain_enforced(self):
        for h in (-1,0,2):
            with self.assertRaises(ValueError): m.singular_fixture(h)

class IndependentBellmanTests(unittest.TestCase):
    @staticmethod
    def evaluate(P,c,g,policy,beta):
        """Backward original-law evaluation, independent of certificate implementation."""
        value=tuple(g)
        for t in reversed(range(len(P))):
            value=tuple(c[t][x][policy[t][x]]+beta[t]*sum(p*v for p,v in zip(P[t][x][policy[t][x]],value)) for x in range(2))
        return value
    @staticmethod
    def optimum(P,c,g,beta):
        value=tuple(g)
        for t in reversed(range(len(P))):
            value=tuple(min(c[t][x][a]+beta[t]*sum(p*v for p,v in zip(P[t][x][a],value)) for a in range(2)) for x in range(2))
        return value
    def test_all_complete_three_date_policies_under_perturbed_law(self):
        T=3; beta=(Q(1),Q(3,4),Q(1,2))
        c=tuple(tuple(tuple(Q((t+1)*(a+1)-x,8) for a in range(2)) for x in range(2)) for t in range(T))
        P=tuple(tuple(tuple((Q(2+t+x+a,8),1-Q(2+t+x+a,8)) for a in range(2)) for x in range(2)) for t in range(T))
        H=tuple(tuple(tuple((Q(1,2),Q(1,2)) for a in range(2)) for x in range(2)) for t in range(T))
        f=((Q(-1,4),Q(1,4)),(Q(1,2),Q(1)),(Q(0),Q(3,4)),(Q(0),Q(1)))
        g=f[-1];opt=self.optimum(P,c,g,beta)
        for bits in itertools.product(range(2),repeat=6):
            policy=tuple(tuple(bits[2*t+x] for x in range(2)) for t in range(T)); stages=[]
            for t in range(T):
                approx=[[c[t][x][a]+beta[t]*sum(p*v for p,v in zip(H[t][x][a],f[t+1])) for a in range(2)] for x in range(2)]
                resid=[min(approx[x])-f[t][x] for x in range(2)]
                gamma=max(approx[x][policy[t][x]]-min(approx[x]) for x in range(2))
                e=max(abs(P[t][x][a][1]-H[t][x][a][1]) for x in range(2) for a in range(2))
                stages.append(m.Stage(min(resid),max(resid),gamma,beta[t],abs(f[t+1][1]-f[t+1][0]),e))
            bound=m.finite_bound(stages)['bound']; value=self.evaluate(P,c,g,policy,beta)
            for v,o in zip(value,opt):
                self.assertGreaterEqual(v-o,0);self.assertLessEqual(v-o,bound)
    def test_exact_greedy_values_have_zero_bound(self):
        P=((((Q(1),Q(0)),(Q(0),Q(1))),((Q(1),Q(0)),(Q(0),Q(1)))),)
        c=(((Q(0),Q(1)),(Q(1),Q(0))),);g=(Q(0),Q(1));beta=(Q(1),)
        opt=self.optimum(P,c,g,beta)
        policy=((0,0),)
        self.assertEqual(self.evaluate(P,c,g,policy,beta),opt)
        self.assertEqual(m.finite_bound([m.Stage(0,0,0,1,1,0)])['bound'],0)

if __name__=='__main__': unittest.main(verbosity=2)
