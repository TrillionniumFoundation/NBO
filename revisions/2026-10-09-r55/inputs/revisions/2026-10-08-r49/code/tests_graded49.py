"""Small exact checks of the prospective graded implementation."""
import itertools,unittest
import graded49 as g
s=g.s;F=g.F
class GradedTests(unittest.TestCase):
    def terminal(self):
        x=g.np.array(list(itertools.product(g.np.arange(9)/8,repeat=2)))
        y,_=s.c.rounded_labels(s.costs(s.I.point(x),s.I.point(g.np.zeros(len(x))),1,True))
        return y
    def test_actual_primitive_grading(self):
        for N in (4,8,16):
            axes,_=g.graded_axes(self.terminal(),N,2)
            self.assertTrue(all(not g.np.array_equal(a,g.np.arange(N+1)/N) for a in axes))
    def test_uniform_quadratic(self):
        x=g.np.array(list(itertools.product(g.np.arange(9)/8,repeat=2)))
        axes,_=g.graded_axes(g.np.sum(x*x,axis=1),16,2)
        self.assertTrue(all(g.np.array_equal(a,g.np.arange(17)/16) for a in axes))
    def test_affine_floor(self):
        axes,_=g.graded_axes(g.np.zeros(81),32,2)
        self.assertTrue(all(g.np.array_equal(a,g.np.arange(33)/32) for a in axes))
    def test_exact_lattice_and_cover(self):
        for N in (4,8,128):
            axes,_=g.graded_axes(self.terminal(),N,2)
            for a in axes:
                self.assertEqual(len(a),N+1);self.assertEqual(a[0],0);self.assertEqual(a[-1],1)
                self.assertTrue(g.np.all(g.np.diff(a)>0));self.assertTrue(all((F(float(x))*2**24).denominator==1 for x in a))
                self.assertTrue(all((F(float(x))+F(float(y)))/2==F(float((x+y)/2)) for x,y in zip(a,a[1:])))
    def test_graded_rung(self):
        p=g.rung(4,2,1,2,1,'graded-fvi');self.assertGreater(p['nonuniform_date_models'],0)
        for m in p['models']:self.assertEqual(s.Model.load(m).payload(),m)
        self.assertGreater(F(p['policy_bound_exact']),0)
    def test_unchanged_comparators(self):
        for method in g.METHODS[:2]:
            self.assertEqual(g.rung(4,2,1,2,1,method),g.BASE_RUNG(4,2,1,2,1,method))
if __name__=='__main__':unittest.main()
