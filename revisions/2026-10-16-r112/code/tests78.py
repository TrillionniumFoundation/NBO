"""Exact tests of simultaneous NBO controller choice and its failure modes."""
from fractions import Fraction as F
import itertools,json,random,unittest
from pathlib import Path
import decision78 as d

class ChoiceTests(unittest.TestCase):
    def graph(self):
        edges=[(0,1,F(1)),(1,0,F(0)),(0,2,F(1)),(2,0,F(0)),
               (2,1,F(-1,10)),(1,2,F(1,5))]
        return edges,d.closure(3,edges)
    def test_orientation(self):
        _,a=self.graph();self.assertEqual(a[2][1],F(-1,10));self.assertEqual(a[1][2],F(1,5))
    def test_potential_attainment(self):
        edges,a=self.graph()
        for j,v in enumerate(d.potentials(a)):
            self.assertEqual(v[0],0)
            self.assertTrue(all(v[b]-v[c]<=e for c,b,e in edges))
            for i in range(3):self.assertEqual(v[i]-v[j],a[j][i])
    def test_negative_self_loop_is_not_erased(self):
        with self.assertRaises(ValueError):d.closure(1,[(0,0,F(-1))])
    def test_negative_two_cycle(self):
        with self.assertRaises(ValueError):d.closure(2,[(0,1,F(1)),(1,0,F(-2))])
    def test_negative_three_cycle(self):
        with self.assertRaises(ValueError):d.closure(3,[(0,1,F(0)),(1,2,F(-2)),(2,0,F(1))])
    def test_unbounded_system_rejected(self):
        with self.assertRaises(ValueError):d.closure(2,[(0,1,F(1))])
    def test_invalid_vertex_rejected(self):
        with self.assertRaises(ValueError):d.closure(2,[(0,2,F(0))])
    def test_zero_cost_graph(self):
        a=d.closure(2,[(0,1,0),(1,0,0)]);self.assertEqual(d.regrets(a,[0]),[0])
    def test_zero_regret_means_universal_optimum(self):
        _,a=self.graph();self.assertEqual(d.regrets(a,[0,0]),[0,F(1,5)])
    def test_sharp_regret_attains_its_maximum(self):
        _,a=self.graph();w=[F(1,8),F(0)];rr=d.regrets(a,w)
        for i in range(2):
            values=[v[i+1]+w[i]-min(v[j+1]+w[j] for j in range(2)) for v in d.potentials(a)]
            self.assertEqual(rr[i],max(values))
    def test_common_charge_cancels(self):
        _,a=self.graph();self.assertEqual(d.regrets(a,[F(1,8),0]),d.regrets(a,[F(81,8),10]))
    def test_fee_boundaries(self):
        _,a=self.graph()
        for fee in (F(0),F(1,10),F(3,20),F(1,5),F(1)):
            self.assertEqual(d.regrets(a,[fee,0]),[max(F(0),fee-F(1,10)),max(F(0),F(1,5)-fee)])
    def test_minimax_tie(self):
        _,a=self.graph();self.assertEqual(d.regrets(a,[F(3,20),0]),[F(1,20),F(1,20)])
    def test_pairwise_information_can_improve_marginal_choice(self):
        edges=[(0,1,1),(1,0,0),(0,2,1),(2,0,0),(2,1,0),(1,2,F(1,4))]
        a=d.closure(3,edges);self.assertEqual(d.regrets(a,[0,0]),[0,F(1,4)])
    def test_transitive_improvement_example(self):
        edges=[(0,i,10) for i in (1,2,3)]+[(i,0,0) for i in (1,2,3)]+[(1,2,1),(2,3,1),(1,3,5)]
        a=d.closure(4,edges);self.assertEqual(a[1][3],2)
    def test_two_algorithms_on_random_feasible_systems(self):
        rng=random.Random(7801)
        for n in range(2,8):
            for _ in range(10):
                true=[F(0)]+[F(rng.randrange(-10,11),7) for _ in range(n-1)]
                edges=[(0,i,true[i]+1) for i in range(1,n)]+[(i,0,1-true[i]) for i in range(1,n)]
                for i,j in itertools.permutations(range(n),2):
                    if rng.randrange(3)==0:edges.append((i,j,true[j]-true[i]+F(rng.randrange(5),11)))
                a=d.closure(n,edges);self.assertEqual(a,d.independent_closure(n,edges))
                for v in d.potentials(a):self.assertTrue(all(v[j]-v[i]<=c for i,j,c in edges))
    def test_duplicate_bounds_only_tighten(self):
        edges,a=self.graph();b=d.closure(3,edges+[(2,1,F(-3,20))])
        self.assertTrue(all(b[i][j]<=a[i][j] for i in range(3) for j in range(3)))
    def test_outward_display(self):
        for value in (F(1,3),F(-1,3),F(10,7)):
            self.assertLessEqual(F(d.decimal(value,True)),value)
            self.assertGreaterEqual(F(d.decimal(value,False)),value)
    def test_all_pinned_intervals_feasible(self):
        p=d.R/'results77/summary.json'
        if not p.exists():p=d.R.parent/'2026-10-11-r77/results77/summary.json'
        self.assertEqual(d.sha(p),d.SOURCE_SHA)
        names,edges,ledger=d.edges_from_summary(json.loads(p.read_text()))
        self.assertEqual(len(ledger),30);a=d.closure(len(names)+1,edges)
        self.assertEqual(a,d.independent_closure(len(names)+1,edges))
        self.assertEqual([names[i] for i,r in enumerate(d.regrets(a,[0]*len(names))) if r==0],['relu-n16'])
    def test_noncovering_statistical_inputs_not_silently_repaired(self):
        edges,_=self.graph()
        with self.assertRaises(ValueError):d.closure(3,edges+[(1,2,0)])

if __name__=='__main__':unittest.main(verbosity=2)
