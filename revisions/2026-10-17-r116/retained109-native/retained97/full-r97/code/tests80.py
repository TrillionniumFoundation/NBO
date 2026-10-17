"""Exact regression checks for calibrated qualification and training barriers."""
from fractions import Fraction as F
import itertools,random,unittest
from qualification73 import Problem,dot
from calibrated80 import Calibrated,modulus,derivative_rows
from study73 import features


def small(kind='relu'):
    x=[(F(0),F(0)),(F(1,2),F(0)),(F(0),F(1,2)),(F(1),F(1))]
    y=[F(0),F(-1,2),F(-1,2),F(-1)]
    return Calibrated(Problem(tuple(features(z,kind) for z in x),tuple(y),tuple(v+F(1,128) for v in y),tuple([F(0)]+[F(1 if kind=='relu' else 4)]*8),tuple([F(8)]*9),F(1,64),F(2)),kind)

class CalibrationTests(unittest.TestCase):
    def test_affine_moduli_equal(self):
        for a,b in itertools.product([F(-3,2),F(0),F(5,4)],repeat=2):
            relu=[F(1),a,F(0),F(0),F(0),b,F(0),F(0),F(0)]
            bern=[F(1)]+[a*j/4 for j in range(1,5)]+[b*j/4 for j in range(1,5)]
            self.assertEqual(modulus(relu,'relu'),max(abs(a),abs(b)))
            self.assertEqual(modulus(bern,'bernstein'),max(abs(a),abs(b)))
            for x in itertools.product([F(0),F(1,7),F(1)],repeat=2):
                self.assertEqual(dot(features(x,'relu'),relu),dot(features(x,'bernstein'),bern))
    def test_legacy_affine_factor_ten(self):
        a,b=F(3,2),F(-1,4)
        old_relu=abs(a)+abs(b)
        old_bern=4*sum(abs(z*j/4) for z in (a,b) for j in range(1,5))
        self.assertEqual(old_bern,10*old_relu)
    def test_relu_exact_slopes(self):
        theta=tuple(F(i-4,3) for i in range(9));rows=derivative_rows('relu')
        for axis,j in itertools.product(range(2),range(4)):
            x=[F(1,8),F(1,8)];y=x.copy();x[axis]=F(2*j+1,8);y[axis]=x[axis]+F(1,32)
            derivative=(dot(features(y,'relu'),theta)-dot(features(x,'relu'),theta))/F(1,32)
            self.assertEqual(derivative,dot(rows[axis*4+j],theta))
    def test_bernstein_derivative_identity(self):
        import math
        theta=tuple(F(i-4,3) for i in range(9));rows=derivative_rows('bernstein')
        for axis,x in itertools.product(range(2),[F(0),F(1,8),F(1,2),F(1)]):
            weights=[F(math.comb(3,j))*x**j*(1-x)**(3-j) for j in range(4)]
            self.assertEqual(sum(weights),1)
            self.assertTrue(all(w>=0 for w in weights))
            d=sum(weights[j]*dot(rows[axis*4+j],theta) for j in range(4))
            self.assertLessEqual(abs(d),modulus(theta,'bernstein'))
    def test_new_bound_below_old(self):
        rng=random.Random(801)
        for kind in ('relu','bernstein'):
            model=small(kind)
            for _ in range(30):
                theta=tuple(F(rng.randrange(-16,17),4) for i in range(9))
                p=model.primal(theta)
                self.assertLessEqual(p['objective'],p['legacy_objective_same_labels'])
    def test_constant_gauge(self):
        for kind in ('relu','bernstein'):
            model=small(kind);a=[F(0)]*9;b=a.copy();b[0]=F(3)
            self.assertEqual(model.primal(a)['objective'],model.primal(b)['objective'])
    def test_dual_weakness_arbitrary_primal(self):
        for kind in ('relu','bernstein'):
            m=small(kind);p=(F(1,2),F(1,2),F(0),F(0));q=(F(0),F(0),F(1,3),F(2,3));xi=(F(1,64),)+(F(0),)*15
            low=m.dual(p,q,xi)
            for z in (-2,0,2):self.assertLessEqual(low,m.primal([F(z)]*9)['objective'])
    def test_invalid_probabilities(self):
        m=small()
        with self.assertRaises(ValueError):m.dual([0]*4,[F(1,4)]*4,[0]*16)
    def test_invalid_derivative_mass(self):
        m=small()
        with self.assertRaises(ValueError):m.dual([F(1,4)]*4,[F(1,4)]*4,[1]*16)
    def test_negative_action_multiplier(self):
        m=small()
        with self.assertRaises(ValueError):m.dual([F(1,4)]*4,[F(1,4)]*4,[0]*16,F(-1),[0]*9)
    def test_attained_lp_exact_gap(self):
        for kind in ('relu','bernstein'):
            r=small(kind).solve();self.assertTrue(r['solver_success']);self.assertGreaterEqual(r['optimization_gap'],0);self.assertLess(r['optimization_gap'],F(1,65536))
    def test_switch_dual_and_feasibility(self):
        m=small();d=[F(0)]*9;d[1]=F(-1);r=m.solve(d,F(1))
        self.assertTrue(r['solver_success']);self.assertLessEqual(r['action_constraint'],0)
        for v in (F(1),F(2),F(8)):
            theta=[F(0)]*9;theta[1]=v
            self.assertLessEqual(r['dual_lower'],m.primal(theta)['objective'])
    def test_certified_positive_switch_barrier(self):
        m=small();base=m.solve();d=[F(0)]*9;d[1]=F(-1)
        r=m.solve(d,F(1));self.assertGreater(r['dual_lower'],base['objective'])
    def test_weak_tie_needs_strict_sublevel(self):
        scores=[F(0),F(0)];self.assertEqual(min(range(2),key=lambda i:(scores[i],i)),0)
    def test_halfspace_box_lower_bound(self):
        d=[F(0),F(2)]+[F(0)]*7;c=F(17)
        self.assertGreater(c-8*sum(abs(v) for v in d),0)
    def test_no_invalid_basis(self):
        with self.assertRaises(ValueError):derivative_rows('neural-best')
    def test_state_l1_bound(self):
        rng=random.Random(802)
        for kind in ('relu','bernstein'):
            theta=tuple(F(rng.randrange(-12,13),4) for _ in range(9));L=modulus(theta,kind)
            for _ in range(40):
                x=tuple(F(rng.randrange(33),32) for j in range(2));y=tuple(F(rng.randrange(33),32) for j in range(2))
                self.assertLessEqual(abs(dot(features(x,kind),theta)-dot(features(y,kind),theta)),L*sum(abs(a-b) for a,b in zip(x,y)))

if __name__=='__main__':unittest.main(verbosity=2)
