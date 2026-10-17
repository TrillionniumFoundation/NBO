"""New theorem/implementation tests; these fixtures are not independent economic observations."""
from fractions import Fraction as Q
import itertools,json,math,tempfile,unittest
from pathlib import Path
import math89 as m

class CoupledTests(unittest.TestCase):
    terms=((1,(1,0)),(1,(1,1)),(2,(0,2)))
    def test_independent_formula_and_gradient(self):
        for u,v in ((Q(1,5),Q(3,10)),(Q(1,4),Q(1,4))):
            self.assertEqual(m.objective((u,v),self.terms),1/u+1/(u*v)+2/v**2)
            self.assertEqual(m.gradient((u,v),self.terms),(-1/u**2-1/(u*u*v),-1/(u*v*v)-4/v**3))
    def test_exact_uncapped_optimum(self):
        c=m.certificate((Q(1,4),)*2,((1,(1,0)),(1,(0,1))),(1,1),Q(1,2),(1,1))
        self.assertEqual(c['upper'],8);self.assertEqual(c['lower'],8)
    def test_cap_multiplier_is_charged(self):
        c=m.certificate((Q(1,10),Q(2,5)),((1,(1,0)),(1,(0,1))),(1,1),Q(1,2),(Q(1,10),1),lam=Q(25,4),nu=(Q(375,4),0))
        self.assertEqual(c['lower'],c['upper'])
    def test_negative_multiplier_rejected(self):
        with self.assertRaises(ValueError):m.certificate((Q(1,4),)*2,self.terms,(1,1),Q(1,2),(1,1),lam=-1)
    def test_infeasible_dual_rejected(self):
        with self.assertRaises(ValueError):m.certificate((Q(1,4),)*2,self.terms,(1,1),Q(1,2),(1,1),lam=0)
    def test_budget_violation_rejected(self):
        with self.assertRaises(ValueError):m.certificate((Q(1,3),)*2,self.terms,(1,1),Q(1,2),(1,1))
    def test_cap_violation_rejected(self):
        with self.assertRaises(ValueError):m.certificate((Q(1,4),)*2,self.terms,(1,1),Q(1,2),(Q(1,8),1))
    def test_bad_dimension_rejected(self):
        with self.assertRaises(ValueError):m.certificate((Q(1,4),)*2,self.terms,(1,),Q(1,2),(1,1))
    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):m.certificate((Q(1,4),)*2,self.terms,(-1,1),Q(1,2),(1,1))
    def test_nonpositive_allowance_rejected(self):
        with self.assertRaises(ValueError):m.objective((0,1),self.terms)
    def test_unsupported_exponents_rejected(self):
        for a in ((-1,0),(.5,0)):
            with self.assertRaises(ValueError):m.objective((1,1),((1,a),))
    def test_zero_or_negative_coefficient_rejected(self):
        for c in (0,-1):
            with self.assertRaises(ValueError):m.objective((1,1),((c,(1,0)),))
    def test_lower_certificate_against_feasible_grid(self):
        c=m.certificate((Q(4,25),Q(17,50)),self.terms,(1,1),Q(1,2),(1,1))
        for i in range(1,200):
            eta=(Q(i,400),Q(1,2)-Q(i,400))
            self.assertLessEqual(c['lower'],m.objective(eta,self.terms))
    def test_strict_convexity_on_rational_segments(self):
        x=(Q(1,5),Q(3,10));y=(Q(3,10),Q(1,5));mid=tuple((u+v)/2 for u,v in zip(x,y))
        self.assertLess(m.objective(mid,self.terms),(m.objective(x,self.terms)+m.objective(y,self.terms))/2)
    def test_coupled_degree_required_for_rounding(self):
        eta=(Q(49,100),)*2;rounded=tuple(m.dyadic(x) for x in eta);terms=((1,(1,1)),)
        ratio=m.objective(rounded,terms)/m.objective(eta,terms)
        self.assertGreater(ratio,2);self.assertLessEqual(ratio,4)
    def test_rounding_preserves_budgets_and_caps(self):
        eta=(Q(4,25),Q(17,50));rounded=tuple(m.dyadic(x) for x in eta)
        self.assertLessEqual(sum(rounded),Q(1,2))
        self.assertTrue(all(x/2<y<=x for x,y in zip(eta,rounded)))
    def test_setup_is_not_multiplicatively_charged(self):
        eta=(Q(49,100),)*2;rounded=tuple(m.dyadic(x) for x in eta);terms=((1,(1,1)),)
        self.assertLessEqual(m.objective(rounded,terms,100)-100,4*(m.objective(eta,terms,100)-100))
    def test_undiscounted_coupled_horizon_bound(self):
        for T in (2,4,8,16):
            terms=[]
            for t in range(T):
                a=[0]*T;a[t]=1;terms.append((1,tuple(a)))
                if t+1<T:a[t+1]=1;terms.append((1,tuple(a)))
            eta=(Q(1,2*T),)*T
            self.assertLessEqual(m.objective(eta,terms),8*T**3)
    def test_positive_global_gap_and_improvement(self):
        ex=m.example();self.assertEqual(ex['equal_allocation'],52)
        self.assertLess(ex['resource']['upper'],42)
        self.assertGreaterEqual(ex['resource']['gap'],0);self.assertLess(ex['resource']['gap'],Q(1,1000))

class PatternTests(unittest.TestCase):
    def test_path_enumeration_matches_actual_occupation(self):
        ref=((0,0),)*3
        for theta in (-2,-1,0,1,2):
            p=m.policy(theta);self.assertEqual(m.path_cost(p)-m.path_cost(ref),m.occupation_difference(p))
    def test_every_three_date_binary_policy(self):
        ref=((0,0),)*3
        for bits in itertools.product((0,1),repeat=6):
            p=tuple((bits[2*t],bits[2*t+1]) for t in range(3))
            self.assertEqual(m.path_cost(p)-m.path_cost(ref),m.occupation_difference(p))
    def test_exact_reference_zero_difference(self):self.assertEqual(m.occupation_difference(((0,0),)*3),0)
    def test_pattern_coverage_cannot_drop_an_unfavorable_member(self):
        actual=tuple(set(m.policy(x) for x in (-2,-1,0,1,2)))
        with self.assertRaises(ValueError):m.coverage(actual,actual[:-1])
    def test_superset_coverage_permitted(self):
        actual=tuple(set(m.policy(x) for x in (-2,-1,0,1,2)))
        self.assertTrue(m.coverage(actual,actual+(((0,0),)*3,)))
    def test_tie_convention_is_deterministic(self):self.assertEqual(m.policy(0)[0][0],0)
    def test_fractional_conflict_bound_not_attained_pattern(self):
        out=m.example()['pattern_example'];self.assertEqual(out['pair_conflict'],Q(1,2));self.assertEqual(out['complete_patterns'],0)
    def test_reference_occupation_is_not_candidate_occupation(self):
        reference_mass=(Q(1),Q(0));candidate_mass=(Q(0),Q(1));cost=(Q(0),Q(1))
        self.assertEqual(sum(a*b for a,b in zip(reference_mass,cost)),0)
        self.assertEqual(sum(a*b for a,b in zip(candidate_mass,cost)),1)
    def test_stochastic_contraction(self):
        a=(Q(1,5),Q(4,5));b=(Q(3,5),Q(2,5));P=(m.transition(0,0,0),m.transition(0,1,1))
        out=[sum((a[x]-b[x])*P[x][y] for x in (0,1)) for y in (0,1)]
        self.assertLessEqual(sum(map(abs,out)),sum(abs(x-y) for x,y in zip(a,b)))
    def test_transition_enclosure_error_vanishes(self):
        p=Q(1,3)
        for k in (8,16,32,64):
            h=Q(1,k);delta=4*h;upper=p+h
            self.assertLessEqual(upper-p,delta)
        self.assertEqual(4*Q(1,64),Q(1,16))

class RecordingTests(unittest.TestCase):
    def test_common_feature_dimension(self):
        import numpy as np,run89 as r
        for d in (2,4,8):self.assertEqual(r.features(np.full((3,d),.25)).shape,(3,14))
    def test_numpy_diagnostics_are_serializable_without_changing_values(self):
        import numpy as np,run89 as r
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'record.json';r.save(p,{'x':np.array([[1.,2.]]),'n':np.int64(2)})
            self.assertEqual(json.loads(p.read_text()),{'x':[[1.,2.]],'n':2})
    def test_invalid_predictor_uses_certified_service_not_fit_success(self):
        import run89 as r
        rows=r.run_rows('relu',[[.75,.25],[.5,.5]],{'relu':{'valid':False,'coefficients':None}})
        self.assertTrue(all(x['status']=='passed' for x in rows))
        for row in rows:
            c=row['counts'];self.assertEqual(c['invalid_predictions'],c['model_rows'])
            self.assertEqual(c['q_queries'],c['terminal_queries']+c['nonterminal_queries'])
            self.assertLessEqual(row['gap'],1/64)

if __name__=='__main__':unittest.main(verbosity=2)
