"""Disjoint R61 correctness tests; not training or policy-cost observations."""
from fractions import Fraction as F
from itertools import product
import random,unittest
import numpy as np
import search60 as u
import multi60 as m
import centered60 as c
import revalidate61 as r

class R61Tests(unittest.TestCase):
    def test_fixed_cover_operator_is_discount_nonexpansive(self):
        beta=F(15,16);rng=random.Random(99173)
        for trial in range(40):
            costs=[F(rng.randrange(-20,21),16) for _ in range(4)]
            weights=[[F(1,4),F(1,2),F(1,4)],[F(1,2),F(1,4),F(1,4)],[F(1,8),F(3,8),F(1,2)],[F(1,3)]*3]
            x=[F(rng.randrange(-20,21),16) for _ in range(3)];y=[F(rng.randrange(-20,21),16) for _ in range(3)]
            op=lambda z:min(costs[a]+beta*sum(w*v for w,v in zip(weights[a],z)) for a in range(4))
            self.assertLessEqual(abs(op(x)-op(y)),beta*max(abs(a-b) for a,b in zip(x,y)))
            self.assertEqual(op([a+F(7,11) for a in x]),op(x)+beta*F(7,11))
    def test_inclusion_alone_does_not_imply_stability(self):
        beta=F(1,2);valid_upper=lambda v:beta*v+v*v
        self.assertEqual(valid_upper(F(0)),0)
        self.assertGreaterEqual(valid_upper(F(1)),beta)
        self.assertGreater(valid_upper(F(1))-valid_upper(F(0)),beta)
    def test_two_sided_allowances_unroll(self):
        beta=F(15,16);eta=[F(1,13),F(1,17),F(1,19),F(1,23)];minus=plus=eta[-1]
        for e in reversed(eta[:-1]):minus=e+beta*minus;plus=e+beta*plus
        self.assertEqual(minus+plus,2*sum(beta**j*x for j,x in enumerate(eta)))
    def test_common_reference_cancels_pointwise_not_by_ranges(self):
        h=[F(-100),F(200)];optimal=[F(1),F(2)];policy=[F(5,4),F(9,4)]
        lo=[j-v for j,v in zip(optimal,h)];hi=[j-v for j,v in zip(policy,h)]
        self.assertEqual([a-b for a,b in zip(hi,lo)],[F(1,4)]*2)
        self.assertGreater(max(hi)-min(lo),F(100))
    def test_closed_actor_ranges_cover_every_intersected_leaf(self):
        part=u.n.Partition(2,8);indices=np.arange(8,dtype=np.uint16)*8
        x=u.n.I(np.array([[0.,0.],[.5,.5],[.25,0.],[.125,.125]]),np.array([[1.,1.],[.5,.5],[.75,.5],[.375,.375]]))
        got=part.ranges(x,indices/4096,indices/4096)
        for k in range(len(x.lo)):
            hit=np.all((x.lo[k]<=part.hi)&(x.hi[k]>=part.lo),axis=1)
            self.assertEqual(got.lo[k],indices[hit].min()/4096);self.assertEqual(got.hi[k],indices[hit].max()/4096)
    def test_fixed_zero_actor_has_exact_monotone_excess(self):
        part=u.n.Partition(2,8);policy=np.zeros((2,8),dtype=np.uint16);before=policy.copy()
        record,lower=c.rung(8,8,4);got,raw=r.upper_recursion(part,policy,lower['lower_excess'],N=8,q=4)
        self.assertTrue(np.array_equal(policy,before));self.assertTrue(np.all(raw['upper_excess']==0))
        self.assertTrue(np.all(raw['unclipped_upper_excess']>=0));self.assertGreaterEqual(got['maximum_date_gap_upper'],0)
    def test_fixed_verified_nonzero_actor_is_unchanged(self):
        part=u.n.Partition(2,8);grid=np.zeros((2,8),dtype=np.uint16)
        verifier=u.sc.a.ReferenceVerifier(part,2,4);policy,dates,certificate=verifier.sweep(grid)
        self.assertTrue(all(np.all(certificate[f't{t}_U']<=0) for t in (0,1)))
        before=policy.tobytes();record,lower=c.rung(8,8,4);got,raw=r.upper_recursion(part,policy,lower['lower_excess'],N=8,q=4)
        self.assertEqual(before,policy.tobytes());self.assertTrue(np.all(raw['upper_excess']<=0));self.assertLessEqual(got['maximum_date_gap_upper'],got['maximum_unclipped_date_gap_upper'])
    def test_fixed_actor_rejects_infeasibility_and_wrong_shapes(self):
        part=u.n.Partition(2,4);lower=np.full((2,16),-10.)
        with self.assertRaises(AssertionError):r.upper_recursion(part,np.full((2,4),4096),lower,N=4,q=2)
        with self.assertRaises(ValueError):r.upper_recursion(part,np.zeros((1,4)),lower,N=4,q=2)
    def test_native_handles_large_exact_coefficient_bits(self):
        big=F(2**220,3);o=u.Objective(F(-1,4),F(1),F(4),[(big,F(-1,8),F(1),F(1,64)),(-big,F(-1,8),F(1),F(1,64))],[])
        got=u.native(o,24,128);values=[o.value(F(j,128)) for j in range(25)];best=min(range(25),key=lambda j:(values[j],j))
        self.assertEqual(got['index'],best);self.assertEqual(F(got['objective_exact']),values[best]);self.assertGreaterEqual(got['max_recorded_operand_bits'],220)
    def test_native_breakpoints_and_zero_capacity(self):
        for knot in (F(0),F(3,32),F(1,4)):
            o=u.Objective(F(-1,4),F(-1,2),F(4),[(F(2),-knot,F(1),F(0)),(F(-3),knot,F(-1),F(0))],[])
            for cap in (0,1,8):
                values=[o.value(F(j,32)) for j in range(cap+1)];best=min(range(cap+1),key=lambda j:(values[j],j));got=u.native(o,cap,32)
                self.assertEqual((got['index'],F(got['objective_exact'])),(best,values[best]))
    def test_three_shock_integral_and_signed_output(self):
        self.assertEqual(m.mean_relu(F(0),[F(1)]*3),F(13,32))
        for w in (F(-7,3),F(5,2)):
            lo,hi=sorted((w*m.mean_relu(F(-1,2),[F(1)]*3),w*m.mean_relu(F(1,2),[F(1)]*3)))
            for j in range(-4,5):self.assertLessEqual(lo,w*m.mean_relu(F(j,8),[F(1)]*3));self.assertGreaterEqual(hi,w*m.mean_relu(F(j,8),[F(1)]*3))
    def test_lexicographic_ties_under_two_controls(self):
        o=m.Objective2([F(0)]*2,[F(0)]*2,[F(0)]*2,F(0),[])
        a=m.adaptive(o,8,64);b=m.exhaustive(o,8,64)
        self.assertEqual(a['index'],[0,0]);self.assertEqual(a['index'],b['index']);self.assertEqual(b['ties'],45)
    def test_exact_tolerance_classification_includes_equality(self):
        t=F(1,16);self.assertTrue(F(float(t))<=t)
        self.assertFalse(F(float(np.nextafter(float(t),np.inf)))<=t)
    def test_monetary_price_does_not_rescale_a_statistical_gain(self):
        gain=(F(1,100),F(3,100));fee=F(1,200);rho=F(1,10000);extra_time=F(20)
        net=(gain[0]-fee-rho*extra_time,gain[1]-fee-rho*extra_time)
        self.assertEqual(net,(F(3,1000),F(23,1000)))
if __name__=='__main__':unittest.main(verbosity=2)
