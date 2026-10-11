"""Exact and boundary regressions for the R74 original-law qualification."""
from fractions import Fraction as F
import itertools,math,unittest
import numpy as np
import common74 as c
import float74 as p
import integer74 as q


def fixture(n=2,shift=0):
    a=np.array([[[min(512,32*(i+j+t+shift)) for j in range(n)] for i in range(n)] for t in range(2)],dtype=np.uint16)
    return dict(n=n,name='fixture',actions=a)

class Qualification74Tests(unittest.TestCase):
    def test_exact_integer_multiplication(self):
        for a,b,d,e in itertools.product((F(-3,4),F(0),F(1,2)),repeat=4):
            if a>b or d>e:continue
            x=q.Q(int(a*q.S),int(b*q.S));y=q.Q(int(d*q.S),int(e*q.S));v=x*y
            for z in (a*d,a*e,b*d,b*e):self.assertTrue(F(int(v.lo),q.S)<=z<=F(int(v.hi),q.S))
    def test_square_crossing_zero(self):
        x=q.Q(-q.S,q.S//2).square();self.assertEqual(int(x.lo),0);self.assertEqual(int(x.hi),q.S)
        y=p.I(-1,0.5).sq();self.assertEqual(float(y.lo),0);self.assertGreaterEqual(float(y.hi),1)
    def test_signed_rounding(self):
        x=q.Q.const(F(-1,3));self.assertLessEqual(F(int(x.lo),q.S),-F(1,3));self.assertGreaterEqual(F(int(x.hi),q.S),-F(1,3))
    def test_cumulative_storage_does_not_alias(self):
        x=p.I(np.zeros(3));y=x+p.I(np.ones(3),np.ones(3)*2)
        self.assertTrue(np.all(x.lo==0));self.assertFalse(np.shares_memory(y.lo,y.hi))
        z=q.Q(np.zeros(3,dtype=object));w=z+q.Q(np.ones(3,dtype=object),np.ones(3,dtype=object)*2)
        self.assertTrue(np.all(z.lo==0));self.assertFalse(np.shares_memory(w.lo,w.hi))
    def test_closed_cell_boundary_range(self):
        a=fixture();s=[q.Q(np.array([q.S//2-1],dtype=object),np.array([q.S//2],dtype=object)),q.Q(np.array([0],dtype=object))]
        v,n=q.action(a,0,s);self.assertEqual(n,1);self.assertEqual(int(v.lo[0]),0);self.assertEqual(int(v.hi[0]),32*q.S//4096)
    def test_exact_boundary_point_ownership(self):
        a=fixture();x=[q.Q(np.array([q.S//2],dtype=object)),q.Q(np.array([0],dtype=object))]
        v,n=q.action(a,0,x);self.assertEqual(int(v.lo[0]),32*q.S//4096);self.assertEqual(n,0)
    def test_support_two_implementations(self):
        for n,m in ((1,2),(2,2),(2,4)):
            a,b=fixture(n),fixture(m,1);self.assertEqual(c.support(a,b)['bound'],q.independent_support(a,b))
    def test_identity_on_common_refinement(self):
        a=fixture(2);b=dict(n=4,name='lift',actions=np.repeat(np.repeat(a['actions'],2,axis=1),2,axis=2))
        self.assertTrue(c.identical(a,b));self.assertEqual(c.support(a,b)['bound'],0);self.assertEqual(q.independent_support(a,b),0)
    def test_same_path_difference_within_support(self):
        a,b=fixture(2),fixture(4,1);K=c.support(a,b)['bound']
        for x,y,z,w in itertools.product((F(0),F(1,2),F(1)),repeat=4):
            coords=(x,y,(z-F(1,2))/16,(w-F(1,2))/16)
            self.assertLessEqual(abs(q.point(a,coords)-q.point(b,coords)),K)
    def test_whole_bin_encloses_exact_faces(self):
        a=fixture();D=1<<40
        bins=np.array([[0,D//2-1,D//2,D//2],[D-1]*4,[D//3]*4],dtype=np.uint64)
        il,iu,_=q.path(a,bins);lo,hi,_=p.path(a,bins)
        for k in range(3):
            for side in (F(0),F(1,2),F(1)):
                v=[F(int(bins[k,j])+side,D) for j in (0,1)]+[F(int(bins[k,j])+side-D//2,D*16) for j in (2,3)]
                value=q.point(a,v);self.assertTrue(F(int(il[k]),c.SCALE)<=value<=F(int(iu[k]),c.SCALE));self.assertTrue(F(float(lo[k]))<=value<=F(float(hi[k])))
    def test_support_global_cost_bound(self):
        a=fixture()
        for x,y,z,w in itertools.product((F(0),F(1,2),F(1)),repeat=4):
            v=q.point(a,(x,y,(z-F(1,2))/16,(w-F(1,2))/16));self.assertTrue(0<=v<=c.H)
    def test_sqrt_upper_exact(self):
        for x in (F(0),F(1,3),F(4),F(1,10**20)):
            y=c.sqrt_upper(x);self.assertGreaterEqual(y*y,x)
            if y:self.assertLess((y-F(1,c.SCALE))**2,x)
    def test_exact_endpoint_variance(self):
        a=np.array([0,c.SCALE//2,c.SCALE],dtype=np.int64);v=c.endpoint_interval(a,a,F(0),F(1))
        self.assertEqual(v['mean_lower'],F(1,2));self.assertEqual(v['variance_lower'],F(1,4));self.assertEqual(v['mean_bin_enclosure_width'],0)
    def test_identity_cost_is_not_monte_carlo(self):
        a=np.zeros(4,dtype=np.int64);v=c.endpoint_interval(a,a,0,0,True);self.assertEqual(v['interval'],(0,0));self.assertFalse(v['strictly_lower'])
    def test_width_account(self):
        a=np.full(65536,c.SCALE//4,dtype=np.int64);v=c.endpoint_interval(a,a+8,0,1)
        self.assertEqual(v['width'],v['mean_bin_enclosure_width']+v['sampling_radius_lower']+v['sampling_radius_upper']+2*v['range_radius'])
    def test_declared_family_logarithm(self):
        self.assertGreater(sum(F(9)**k/math.factorial(k) for k in range(25)),4*13/F(1,100))

if __name__=='__main__':unittest.main(verbosity=2)
