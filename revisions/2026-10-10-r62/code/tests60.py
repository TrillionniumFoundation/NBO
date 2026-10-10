"""Disjoint rational correctness fixtures; not R60 production observations."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import math,random,unittest
import numpy as np
import search60 as s
import multi60 as m
import bellman60 as b

class ExactSearchTests(unittest.TestCase):
    def test_native_random_against_python_exhaustive(self):
        rng=random.Random(99011);queries=[];expected=[]
        for z in range(64):
            features=[]
            for j in range(6):features.append((F(rng.randrange(-8,9),8),F(rng.randrange(-8,9),32),F(rng.choice((-4,-2,-1,1,2,4)),2),F(rng.randrange(0,3),32)))
            squares=[(F(rng.randrange(-4,5),4),F(rng.randrange(-4,5),16),F(rng.choice((-2,-1,1,2))))]
            o=s.Objective(F(rng.randrange(-16,17),8),F(rng.randrange(-8,9),4),F(rng.randrange(0,5)),features,squares)
            cap=32;Q=128;scores=[o.value(F(k,Q)) for k in range(cap+1)];best=min(range(cap+1),key=lambda k:(scores[k],k))
            queries.append((o,cap,Q,1,None));expected.append((best,scores[best]))
        out,work=s.native_batch(queries)
        self.assertEqual([(r['index'],F(r['objective_exact'])) for r in out],expected)
    def test_native_flat_and_smallest_tie(self):
        zero=s.Objective(F(0),F(0),F(0),[(F(3),F(-1,8),F(1),F(1,32)),(F(-3),F(-1,8),F(1),F(1,32))],[])
        self.assertEqual(s.native(zero,513,4096)['index'],0)
        a=F(7,128);c=F(8,128);q1=-(a+c)-4*(a**3+a*a*c+a*c*c+c**3)
        obj=s.Objective(q1,F(1),F(4),[],[])
        self.assertEqual(obj.value(a),obj.value(c));self.assertEqual(s.native(obj,32,128)['index'],7)
    def test_nonconvex_piece_endpoint(self):
        o=s.Objective(F(1,20),F(-1),F(4),[],[]);scores=[o.value(F(k,128)) for k in range(33)]
        self.assertEqual(s.native(o,32,128)['index'],min(range(33),key=lambda k:(scores[k],k)))
    def test_second_difference_formula_and_monotonicity(self):
        for q1,q2,q4 in product((F(-2),F(1)),(F(-3),F(2)),(F(0),F(4))):
            o=s.Objective(q1,q2,q4,[],[]);values=[o.value(F(k,64)) for k in range(35)]
            sec=[values[k+2]-2*values[k+1]+values[k] for k in range(33)]
            self.assertEqual(sec,[2*q2/64**2+q4*F(12*k*k+24*k+14,64**4) for k in range(33)])
            self.assertTrue(all(a<=c for a,c in zip(sec,sec[1:])))
    def test_all_implementation_cells_match(self):
        o=s.Objective(F(-3,8),F(-1,4),F(4),[(F(3,8),F(-1,8),F(2),F(1,32)),(F(-5,8),F(1,8),F(-1),F(0))],[])
        ref=s.native(o,32,128,0)
        for method in s.METHODS:
            r=s.solve(o,32,128,method);self.assertEqual((r['index'],r['objective_exact']),(ref['index'],ref['objective_exact']))
    def test_reduction_identity_on_region(self):
        o=s.Objective(F(2),F(-1),F(4),[(F(-2),F(3),F(-1),F(1,8)),(F(3),F(-3),F(1),F(1,8)),(F(5),F(0),F(1,4),F(1,2))],[])
        reduced,offset=o.reduced(F(1,4))
        self.assertEqual(len(reduced.features),0)
        for j in range(33):self.assertEqual(o.value(F(j,128)),reduced.value(F(j,128))+offset)
    def test_lossless_screen_keeps_every_exact_minimum(self):
        o=s.Objective(F(0),F(0),F(0),[(F(1),F(-1,8),F(1),F(1,32)),(F(-1),F(-1,8),F(1),F(1,32))],[])
        val,peak=s.endpoints(o,32,128);keep,cut=s.sc.survivors(val.lo,val.hi)
        self.assertEqual(list(keep),list(range(33)))
    def test_outward_endpoint_coarsening(self):
        o=s.Objective(F(-1,3),F(1),F(4),[(F(-7,11),F(-1,8),F(3),F(1,64))],[])
        for bits in (8,24,53):
            lo,hi=s.bound(o,F(1,32),F(1,8),bits)
            for j in range(4,17):self.assertLessEqual(lo,o.value(F(j,128)));self.assertGreaterEqual(hi,o.value(F(j,128)))
    def test_declared_fallback_is_exact(self):
        o=s.Objective(F(-1,4),F(1),F(4),[],[])
        a=s.solve(o,2050,16384,'screen-reduced');ref=s.native(o,2050,16384,0)
        self.assertTrue(a['fallback']);self.assertEqual(a['index'],ref['index'])
        z=s.solve(o,64,256,'adaptive',node_limit=0);self.assertTrue(z['fallback']);self.assertEqual(z['index'],s.native(o,64,256,0)['index'])
    def test_box_shock_recovers_scalar_formula(self):
        for z,r in product([F(k,8) for k in range(-5,6)],(F(0),F(1,8),F(1,4))):self.assertEqual(m.mean_relu(z,[r]),s.sc.a.old.hinge(z,r))
    def test_two_shock_formula_independent_piecewise_quadrature(self):
        r1=F(1,8);r2=F(1,4)
        for z in (F(-1,2),F(-1,8),F(0),F(1,7),F(1,2)):
            knots=sorted({-r2,r2,*[x for x in (-r1-z,r1-z) if -r2<x<r2]});value=F(0)
            for a,c in zip(knots,knots[1:]):
                # Scalar mean is quadratic/affine on each segment; Simpson is exact.
                value+=(c-a)*(s.sc.a.old.hinge(z+a,r1)+4*s.sc.a.old.hinge(z+(a+c)/2,r1)+s.sc.a.old.hinge(z+c,r1))/6
            self.assertEqual(m.mean_relu(z,[r1,r2]),value/(2*r2))
    def test_uniform_mixture_partition_identity(self):
        for z in [F(j,16) for j in range(-8,9)]:
            r=F(1,4);self.assertEqual(m.mean_relu(z,[r]),(m.mean_relu(z-r/2,[r/2])+m.mean_relu(z+r/2,[r/2]))/2)
    def test_two_control_feasibility_and_witness(self):
        o=m.Objective2([F(-1,3),F(-1,4)],[F(1),F(1)],[F(4),F(4)],F(1,4),[(F(-1,5),F(-1,8),[F(1),F(-1)],[F(1,16),F(1,32)])])
        got=m.adaptive(o,8,64);ref=m.exhaustive(o,8,64)
        self.assertEqual(got['index'],ref['index']);self.assertLessEqual(sum(got['index']),8)
        fallback=m.adaptive(o,8,64,node_limit=0);self.assertTrue(fallback['fallback']);self.assertEqual(fallback['index'],ref['index'])
    def test_rectangle_range_queries_are_exact(self):
        values=np.random.default_rng(99021).normal(size=(8,8));lo=b.RangeTable(values);hi=b.RangeTable(values,True)
        for i,j,k,l in ((0,0,7,7),(1,2,4,6),(7,7,7,7),(0,3,2,3)):
            box=b.I(np.array([[(i+.1)/8,(j+.1)/8]]),np.array([[(k+.9)/8,(l+.9)/8]]))
            self.assertEqual(lo.query(box)[0],values[i:k+1,j:l+1].min());self.assertEqual(hi.query(box)[0],values[i:k+1,j:l+1].max())
    def test_bellman_bracket_feasibility_and_order(self):
        record,raw=b.rung(4,4,2);self.assertTrue(np.all(raw['lower']<=raw['upper']));self.assertTrue(np.all(raw['policy']<=raw['capindex']))
        self.assertGreaterEqual(record['maximum_date_gap_upper'],0)
    def test_native_rejects_invalid_input(self):
        o=s.Objective(F(0),F(0),F(4),[],[])
        with self.assertRaises(ValueError):s.native(o,-1,64)
        with self.assertRaises(ValueError):s.native(o,4,0)

if __name__=='__main__':unittest.main(verbosity=2)
