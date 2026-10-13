"""Exact tests for attained mixed choices, their costs, and implementation."""
import unittest,itertools,random,json
from fractions import Fraction as F
from pathlib import Path
import allocation79 as a
import decision78 as d

class AllocationTests(unittest.TestCase):
    def graph(self):
        e=[(0,1,1),(1,0,0),(0,2,1),(2,0,0),(2,1,F(-1,10)),(1,2,F(1,5))]
        return e,d.closure(3,e)
    def test_sharp_mixture_needs_common_attainment(self):
        e,D=self.graph();H=a.matrix(D,[F(3,20),0]);p=[F(1,2)]*2
        ans=a.certificate(H,p,p);self.assertEqual(ans['upper'],F(1,40));self.assertEqual(ans['gap'],0)
        values=[]
        for theta in d.potentials(D)[1:]:
            self.assertTrue(all(theta[j]-theta[i]<=c for i,j,c in e))
            cost=[theta[1]+F(3,20),theta[2]]
            values.append(sum(x*y for x,y in zip(p,cost))-min(cost))
        self.assertEqual(max(values),ans['upper'])
    def test_matching_pennies(self):
        r=a.solve_game([[1,-1],[-1,1]])
        self.assertEqual(r['p'],[F(1,2)]*2);self.assertEqual(r['upper'],0)
    def test_rectangular_game(self):
        r=a.solve_game([[1,0],[0,1],[F(1,3),F(1,3)]])
        self.assertEqual(r['upper'],F(1,2));self.assertEqual(r['gap'],0)
    def test_degenerate_singleton_game(self):
        r=a.solve_game([[0,0],[0,0]])
        self.assertEqual(r['upper'],0);self.assertEqual(r['gap'],0)
    def test_one_column(self):
        self.assertEqual(a.solve_game([[-3],[2],[0]])['upper'],2)
    def test_one_row(self):
        self.assertEqual(a.solve_game([[2,-3,0]])['upper'],-3)
    def test_probability_rejection(self):
        for p in ([F(-1),F(2)],[F(1,3),F(1,3)],[1]):
            with self.assertRaises(ValueError):a.simplex(p,2)
    def test_gain_reversal_rejected(self):
        with self.assertRaises(ValueError):a.two_policy(2,1,1)
    def test_zero_width_and_boundary(self):
        self.assertEqual(a.two_policy(1,1,1),(1,0));self.assertEqual(a.two_policy(1,1,2),(0,0))
    def test_analytic_two_policy_against_exact_game(self):
        for l,u in ((F(-1),F(2)),(F(1,10),F(1,5)),(F(2),F(3))):
            for t in (F(-1,4),0,F(1,4),F(1,2),F(3,4),1,F(5,4)):
                f=l+t*(u-l);p,v=a.two_policy(l,u,f)
                H=[[0,u-f],[f-l,0]];r=a.solve_game(H)
                self.assertEqual(r['upper'],v)
                self.assertEqual(a.certificate(H,[p,1-p],r['dual'])['gap'],0)
    def test_extra_setup_cutoff(self):
        l,u,f=F(1,10),F(1,5),F(3,20);width=u-l
        H=[[0,u-f],[f-l,0]]
        for k in (0,width/8,width/4,width/2):
            r=a.installed_game(H,1,{(0,):0,(1,):0,(0,1):k})
            self.assertEqual(r['value'],min(width/2,width/4+k))
    def test_installed_subset_keeps_external_comparator(self):
        H=[[0,2],[3,0]]
        r=a.installed_game(H,2,{(0,):1,(1,):2,(0,1):3})
        singleton=next(x for x in r['all_subset_certificates'] if x['installed']==(0,))
        self.assertEqual(singleton['upper'],F(5,2))
    def test_installation_monotonicity(self):
        with self.assertRaises(ValueError):a.installed_game([[0,1],[1,0]],1,{(0,):2,(1,):0,(0,1):1})
    def test_complete_subset_cost_required(self):
        with self.assertRaises(ValueError):a.installed_game([[0,1],[1,0]],1,{(0,):0,(1,):0})
    def test_finite_cohort_all_integers(self):
        for t in (F(1,7),F(1,2),F(4,5)):
            l,u=F(1,10),F(1,5);f=l+t*(u-l)
            for m in (1,2,3,7,16):
                for setup in (0,F(1,100),F(1)):
                    r=a.cohort(l,u,f,m,setup)
                    v=[max(F(k,m)*(f-l),(1-F(k,m))*(u-f))+(setup if 0<k<m else 0) for k in range(m+1)]
                    self.assertEqual(r['regret'],min(v))
    def test_cohort_rounding_bound(self):
        for t in (F(1,7),F(1,2),F(4,5)):
            l,u=F(1,10),F(1,5);f=l+t*(u-l);p,v=a.two_policy(l,u,f)
            for m in (1,2,3,7,16):
                r=a.cohort(l,u,f,m)
                self.assertLessEqual(r['regret']-v,max(f-l,u-f)/(2*m))
    def test_no_coefficient_averaging_identity(self):
        self.assertEqual(F(1,2)*(-1)**2+F(1,2)*1**2,1)
        self.assertEqual((F(1,2)*(-1)+F(1,2)*1)**2,0)
    def test_common_charge_invariance(self):
        _,D=self.graph()
        self.assertEqual(a.matrix(D,[F(1,8),0]),a.matrix(D,[F(81,8),10]))
    def test_primal_dual_gap_not_solver_status(self):
        r=a.certificate([[0,1],[1,0]],[1,0],[1,0])
        self.assertEqual(r['gap'],1);self.assertEqual(r['lower'],0);self.assertEqual(r['upper'],1)
    def test_rational_games_against_independent_grid(self):
        rng=random.Random(7901)
        for _ in range(25):
            H=[[F(rng.randrange(-7,8),3) for i in range(3)] for j in range(3)]
            r=a.solve_game(H);self.assertEqual(r['gap'],0)
            grid=[max(sum(H[j][k]*p[k] for k in range(3)) for j in range(3))
                  for i in range(21) for k in range(21-i) for p in [[F(i,20),F(k,20),F(20-i-k,20)]]]
            self.assertLessEqual(r['upper'],min(grid))
    def test_singular_system(self):
        self.assertIsNone(a.linear_solve([[1,1],[2,2]],[0,0]))
    def test_zero_charge_retains_identified_best(self):
        file=a.R/'results77/summary.json'
        self.assertTrue(file.exists(),'Pinned original cost file required')
        self.assertEqual(d.sha(file),d.SOURCE_SHA)
        names,e,_=d.edges_from_summary(json.loads(file.read_text()));D=d.closure(len(names)+1,e)
        r=a.solve_game(a.matrix(D,[0]*len(names)));self.assertEqual(r['upper'],0)
        self.assertEqual(r['p'][names.index('relu-n16')],1)

if __name__=='__main__':unittest.main(verbosity=2)
