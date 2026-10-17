"""Exact and independent whole-box regressions for directed sublevel transfer."""
from fractions import Fraction as F
import itertools,json,unittest
import numpy as np
import paired82 as p
import independent82 as z
import study82 as s

class DirectedSublevelTests(unittest.TestCase):
    def test_reference_identity_exact_in_both_implementations(self):
        for n in (2,4):
            actions=np.zeros((n,n),dtype=np.int64)
            for c in itertools.product(range(n),repeat=2):
                a=p.evaluate(c,n,2,4,128,128,p.Actor(actions));b=z.evaluate(c,n,2,4,128,128,z.Actor(actions))
                self.assertTrue(np.all(a.lo==0) and np.all(a.hi==0) and np.all(b.lo==0) and np.all(b.hi==0))

    def test_direct_rational_paths_inside_both_whole_box_procedures(self):
        for n in (2,4):
            actions=np.fromfunction(lambda i,j:((i+j)%3)*128,(n,n),dtype=int).astype(np.int64)
            pa,za=p.Actor(actions),z.Actor(actions)
            for cell in itertools.product(range(n),repeat=2):
                for b,a in ((128,0),(0,128),(256,128)):
                    fp=p.evaluate(cell,n,2,4,b,a,pa);ip=z.evaluate(cell,n,2,4,b,a,za)
                    for i in range(16):
                        exact=z.exact_point(cell,n,2,4,i,b,a,actions)
                        self.assertLessEqual(F(float(fp.lo[i])),exact);self.assertGreaterEqual(F(float(fp.hi[i])),exact)
                        self.assertLessEqual(F(int(ip.lo[i]),z.S),exact);self.assertGreaterEqual(F(int(ip.hi[i]),z.S),exact)

    def test_arithmetic_implementations_are_source_independent(self):
        for fname in ('independent82.py','paired82.py'):
            text=(s.R/'code'/fname).read_text()
            self.assertNotIn('import '+('paired82' if fname.startswith('independent') else 'independent82'),text)
            self.assertNotIn('import float77',text);self.assertNotIn('import independent77',text)

    def test_integer_square_does_not_overflow_scalar(self):
        v=z.Z.const(4095,4096).square()
        exact=F(4095,4096)**2
        self.assertLessEqual(F(int(v.lo),z.S),exact);self.assertGreaterEqual(F(int(v.hi),z.S),exact)

    def test_outward_integer_non_dyadic_constant(self):
        for a,b in ((1,3),(-1,3),(123,17)):
            v=z.Z.const(a,b);exact=F(a,b)
            self.assertLessEqual(F(int(v.lo),z.S),exact);self.assertGreaterEqual(F(int(v.hi),z.S),exact)

    def test_dyadic_initial_and_shock_boxes_cover_declared_cell(self):
        x,w=p.boxes((2,3),8,4,16)
        self.assertEqual(float(x[0].lo.min()),2/8);self.assertEqual(float(x[0].hi.max()),3/8)
        self.assertEqual(float(x[1].lo.min()),3/8);self.assertEqual(float(x[1].hi.max()),4/8)
        self.assertEqual(float(w.lo.min()),-1/32);self.assertEqual(float(w.hi.max()),1/32)
        self.assertEqual(len(w.lo),4*4*16)

    def test_invalid_partition_rejected(self):
        for n,r,q in ((3,2,4),(4,3,4),(4,2,3)):
            with self.assertRaises(ValueError):p.boxes((0,0),n,r,q)
            with self.assertRaises(ValueError):z.evaluate((0,0),n,r,q,128,0,z.Actor(np.zeros((4,4),dtype=np.int64)))

    def test_terminal_lookup_retains_boundary_cells(self):
        a=np.arange(16,dtype=np.int64).reshape(4,4)*16
        pa,za=p.Actor(a),z.Actor(a)
        fp=pa.action((p.I(np.array([.25]),np.array([.5])),p.I(np.array([.25]),np.array([.5]))))
        ip=za.action((z.Z(np.array([z.S//4],dtype=object),np.array([z.S//2],dtype=object)),)*2)
        self.assertEqual(fp.lo[0],80/4096);self.assertEqual(fp.hi[0],160/4096)
        self.assertEqual(int(ip.lo[0]),80*z.S//4096);self.assertEqual(int(ip.hi[0]),160*z.S//4096)

    def test_final_innovation_analytic_correction(self):
        for x,y in ((F(1,8),F(1,16)),(F(1,2),F(3,8))):
            def g(w):return 2*((x+w-F(5,8))**2+(y-w-F(5,8))**2)+(x-y+2*w)**2/4+2*max(F(0),F(1,2)-x-y)**2
            h=F(1,32);integral=(g(-h)+4*g(0)+g(h))/6
            self.assertEqual(integral-g(0),F(5,3072))

    def test_all_switches_and_admitted_alternatives_enumerated(self):
        counts=[];total=0
        for n,k in s.MODELS:
            _,_,rows,meta=s.inputs(n,k);counts.append(len(rows));total+=meta['all_switches']
        self.assertEqual(total,20480);self.assertEqual(counts,[832,9,78,57]);self.assertEqual(sum(counts),976)

    def test_strict_exclusion_keeps_equal_barrier(self):
        U=F(1);eps=F(1,65536)
        possible=[D for D in (U-eps,U+eps,U+2*eps) if D<=U+eps]
        self.assertEqual(possible,[U-eps,U+eps])

    def test_class_envelope_contains_every_cellwise_selector(self):
        eps=[str(x) for x in s.TOLERANCES]
        rows=[dict(cell=[0,0],enabled_tolerances=eps),dict(cell=[0,0],enabled_tolerances=eps),dict(cell=[1,1],enabled_tolerances=eps)]
        bands=[(F(-1,8),F(1,16)),(F(0),F(1,4)),(F(-1,2),F(-1,4))]
        bound=s.class_bounds(2,rows,bands)[0]
        for a,b in itertools.product((F(0),F(-1,8),F(1,16),F(1,4)),(F(0),F(-1,2),F(-1,4))):
            self.assertLessEqual(bound['lower'],(a+b)/4);self.assertGreaterEqual(bound['upper'],(a+b)/4)
        self.assertEqual(bound['coarse_radius'],s.H/2)

    def test_no_uncertainty_has_zero_transfer_radius(self):
        for x in s.class_bounds(4,[],[]):self.assertEqual((x['lower'],x['upper'],x['coarse_radius']),(0,0,0))

    def test_directed_pair_enlargement_has_correct_sign(self):
        reference=(F(1,10),F(1,5));a=(F(-1,50),F(1,40));b=(F(-1,30),F(1,20))
        out=(reference[0]+a[0]-b[1],reference[1]+a[1]-b[0])
        for v,x,y in itertools.product(reference,a,b):self.assertLessEqual(out[0],v+x-y);self.assertGreaterEqual(out[1],v+x-y)

    def test_support_not_added_twice(self):
        rows=[dict(cell=[0,0],enabled_tolerances=[str(x) for x in s.TOLERANCES])]
        value=s.class_bounds(4,rows,[(F(-1,1024),F(1,512))])[0]
        self.assertEqual(value['lower'],-F(1,16384));self.assertEqual(value['upper'],F(1,8192))
        self.assertLess(value['upper'],value['coarse_radius'])

    def test_cell_relaxation_need_not_have_one_attaining_parameter(self):
        actual=[F(1,2),F(1,2)];independent_cell_upper=F(1)
        self.assertLess(max(actual),independent_cell_upper)

    def test_nested_valid_integrals_can_be_intersected(self):
        first=(F(-1,2),F(1,3));second=(F(-1,4),F(1,2));exact=F(1,8)
        lo=max(first[0],second[0]);hi=min(first[1],second[1])
        self.assertLessEqual(lo,exact);self.assertGreaterEqual(hi,exact);self.assertEqual((lo,hi),(F(-1,4),F(1,3)))

    def test_complete_r80_statistical_family_is_unchanged(self):
        record=s.read(s.R/'results80/cost/summary.json')
        self.assertEqual(record['rows'],524288);self.assertEqual(len(record['policies']),9)
        self.assertIn('conditional',record['inference']);self.assertIn('cash',record['inference'])

if __name__=='__main__':unittest.main(verbosity=2)
