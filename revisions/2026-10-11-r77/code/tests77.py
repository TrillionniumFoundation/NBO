"""Exact and interval regressions for the R77 original-controller cost study."""
from fractions import Fraction as F
import itertools,math,unittest
import numpy as np
import float77 as f
import independent77 as z
import cost77 as s

class CostQualificationTests(unittest.TestCase):
    def test_integer_products_and_signed_squares(self):
        for a,b,c,d in ((-7,3,-5,4),(1,8,2,9),(-9,-3,-8,-2),(0,0,0,0)):
            x=z.Z.const(a,7);x.hi=z.Z.const(b,7).hi
            y=z.Z.const(c,11);y.hi=z.Z.const(d,11).hi
            p=x*y;q=x.sq()
            for v,w in itertools.product((F(a,7),F(b,7)),(F(c,11),F(d,11))):
                self.assertLessEqual(F(int(p.lo),z.S),v*w);self.assertGreaterEqual(F(int(p.hi),z.S),v*w)
                self.assertLessEqual(F(int(q.lo),z.S),v*v);self.assertGreaterEqual(F(int(q.hi),z.S),v*v)
    def test_float_products_contain_rational_endpoints(self):
        for a,b in itertools.product((-7,-1,0,2,9),repeat=2):
            p=f.I.rat(a,13)*f.I.rat(b,17);actual=F(a*b,13*17)
            self.assertLessEqual(F(float(p.lo)),actual);self.assertGreaterEqual(F(float(p.hi)),actual)
    def test_square_across_zero(self):
        p=f.I(np.array([-2.]),np.array([3.])).square()
        self.assertEqual(p.lo[0],0);self.assertGreaterEqual(p.hi[0],9)
        q=z.Z(-2*z.S,3*z.S).sq();self.assertEqual(int(q.lo),0);self.assertEqual(int(q.hi),9*z.S)
    def test_ceil_square_root(self):
        for x in (F(0),F(1,7),F(2),F(49,64),F(10**20+1,11)):
            r=s.exact_sqrt_up(x);self.assertGreaterEqual(r*r,x)
            if r>0:self.assertLess((r-F(1,2**60))**2,x)
    def test_exact_sample_variance(self):
        a=np.asarray([-3*z.S,0,z.S,2*z.S],dtype=np.int64)
        mean,var,_=s.moments(a);self.assertEqual(mean,0);self.assertEqual(var,F(14,3))
    def test_family_tail_budget(self):
        lower=sum((F(10)**k/F(math.factorial(k)) for k in range(21)),F(0))
        self.assertGreater(lower,12000)
    def test_primitive_cost_support(self):
        beta=F(15,16);running=F(103,64);terminal=F(37,16)
        self.assertEqual(running*(1+beta)+beta**2*terminal,s.H)
        for x,y,a in itertools.product((F(0),F(1,2),F(1)),(F(0),F(1,2),F(1)),(F(0),F(1,8),F(1,4))):
            c=(x-F(5,8))**2+(y-F(5,8))**2+(x-y)**2/4+2*max(F(0),F(1,2)-x-y)**2+a*a+4*a**4
            g=2*((x-F(5,8))**2+(y-F(5,8))**2)+(x-y)**2/4+2*max(F(0),F(1,2)-x-y)**2
            self.assertLessEqual(c,running);self.assertLessEqual(g,terminal)
    def test_exact_final_noise_moment(self):
        for u,v in itertools.product((F(1,8),F(3,8),F(3,4)),repeat=2):
            def g(w):return 2*((u+w-F(5,8))**2+(v-w-F(5,8))**2)+(u-v+2*w)**2/4+2*max(F(0),F(1,2)-u-v)**2
            simpson=(g(-F(1,32))+4*g(0)+g(F(1,32)))/6
            self.assertEqual(simpson,g(0)+F(5,3072))
    def test_frozen_actors_and_original_hashes(self):
        actors,meta=s.controllers();self.assertEqual(set(actors),set(s.NAMES))
        self.assertTrue(all(v['optimization_passed'] for v in meta.values()))
    def test_full_bin_boundary_and_noise_extremes(self):
        values=(0,(1<<39)-1,(1<<40)-1)
        paths=np.array(list(itertools.product(values,repeat=4)),dtype=np.uint64)
        actions=np.arange(32,dtype=np.int64).reshape(2,4,4)*8
        result,work=s.enclose(paths,actions)
        self.assertEqual(result.shape,(4,81));self.assertTrue(np.all(result[::2]<=result[1::2]))
        self.assertEqual(work['complete_interval_trajectories_per_implementation'],81)
        self.assertEqual(work['original_optimal_value_queries'],0)
    def test_actual_rectangle_extrema_not_corner_sampling(self):
        actions=np.zeros((2,4,4),dtype=np.int64);actions[:,1,1]=64
        actor=f.Actor(actions);value=actor.action(0,(f.I(np.array([0.]),np.array([.75])),f.I(np.array([0.]),np.array([.75]))))
        self.assertEqual(value.lo[0],0);self.assertEqual(value.hi[0],F(1,64))
        other=z.IntegerActor(actions);w=other.action(0,(z.Z([0],[3*z.S//4]),z.Z([0],[3*z.S//4])))
        self.assertEqual(int(w.hi[0]),z.S//64)
    def test_exact_width_decomposition(self):
        lo=np.array([z.S//8]*64,dtype=np.int64);hi=lo+3
        rec=s.interval(lo,hi,(F(0),s.H));parts=rec['width_decomposition']
        self.assertEqual(rec['width_exact'],sum(parts.values()));self.assertEqual(parts['numerical'],F(3,z.S))
    def test_precision_is_not_equivalence(self):
        lo=np.array([z.S//8]*200000,dtype=np.int64)
        rec=s.interval(lo,lo,(-s.H,s.H))
        self.assertTrue(rec['paired_width_target_passed']);self.assertFalse(rec['equivalence_at_margin'])
    def test_no_pathwise_gain_clipping(self):
        lo=np.array([-z.S//8,z.S//16,z.S//4],dtype=np.int64)
        rec=s.interval(lo,lo,(-s.H,s.H))
        self.assertEqual(rec['enclosure_midpoint_mean'],F(1,16))
    def test_adoption_fee_interval(self):
        low,high=F(1,20),F(1,10);episodes=12;price=F(7);work=F(3,2);fee=F(1,4)
        net=(episodes*price*low-work-fee,episodes*price*high-work-fee)
        for gain in (low,(low+high)/2,high):self.assertTrue(net[0]<=episodes*price*gain-work-fee<=net[1])

if __name__=='__main__':unittest.main(verbosity=2)
