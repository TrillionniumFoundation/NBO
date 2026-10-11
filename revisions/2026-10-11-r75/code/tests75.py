"""Exact primitive, inference, adoption and preservation regressions."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib,json,math,unittest
import numpy as np
import common74 as c
import integer74 as q
from tables75 import endpoint
R=Path(__file__).resolve().parents[1]
class Revision75Tests(unittest.TestCase):
    def test_state_vertex_cost_bound(self):
        def loss(x,y):return (x-F(5,8))**2+(y-F(5,8))**2+(x-y)**2/4+2*max(F(0),F(1,2)-x-y)**2
        vertices=[loss(x,y) for x,y in product((F(0),F(1)),repeat=2)]
        self.assertEqual(max(vertices),F(82,64));self.assertEqual(max(vertices)+F(1,4)**2+4*F(1,4)**4,F(87,64))
    def test_terminal_vertex_bound(self):
        vals=[2*((x-F(5,8))**2+(y-F(5,8))**2)+(x-y)**2/4+2*max(F(0),F(1,2)-x-y)**2 for x,y in product((F(0),F(1)),repeat=2)]
        self.assertEqual(max(vals),F(33,16))
    def test_jacobian_column_bounds(self):
        for x,y in product([F(k,8) for k in range(9)],repeat=2):
            a,b=F(9,16)-y/16,F(1,8)-y/16
            self.assertGreaterEqual(min(a,b),0);self.assertLessEqual(a+b,F(11,16))
    def test_closed_pair_distance(self):
        for i,j in product(range(4),repeat=2):
            d=max(F(0),F(i-j-1,4),F(j-i-1,4))
            self.assertEqual(d,F(max(0,abs(i-j)-1),4))
    def test_identical_lifted_policies_have_zero_support(self):
        a={'n':1,'actions':np.full((2,1,1),64,dtype=np.uint16)};b={'n':4,'actions':np.full((2,4,4),64,dtype=np.uint16)}
        self.assertTrue(c.identical(a,b));self.assertEqual(c.support(a,b)['bound'],0)
    def test_single_date_mutation_breaks_identity(self):
        a={'n':2,'actions':np.zeros((2,2,2),dtype=np.uint16)};b={'n':2,'actions':a['actions'].copy()};b['actions'][1,1,1]=1
        self.assertFalse(c.identical(a,b));self.assertGreater(c.support(a,b)['bound'],0)
    def test_outward_printing_handles_negative_values(self):
        for v in (F(-1,3),F(0),F(17,100000000),F(-33,19)):
            self.assertLessEqual(F(endpoint(v,False)),v);self.assertGreaterEqual(F(endpoint(v,True)),v)
    def test_precision_failure_is_not_failed_sign(self):
        lo,hi=-F(17,100),-F(16,100)
        self.assertLess(hi,0);self.assertGreater(hi-lo,F(1,256))
    def test_equivalence_can_have_strict_sign(self):
        lo,hi=-F(1,1024),-F(1,2048)
        self.assertTrue(-F(1,256)<=lo<=hi<=F(1,256));self.assertLess(hi,0)
    def test_adoption_threshold_boundary(self):
        gain=F(3,20);price=F(2);per=F(1,20);setup=F(7);threshold=setup/(price*gain-per)
        self.assertEqual(threshold*(price*gain-per)-setup,0);self.assertGreater((threshold+1)*(price*gain-per)-setup,0)
    def test_nonpositive_margin_cannot_recover_positive_setup(self):
        for D in (0,1,100,10000):self.assertLessEqual(D*(F(1,10)-F(1,5))-1,0)
    def test_deployment_count_is_not_sample_count(self):
        gain=F(1,10);setup=F(1);sample_count=131072
        self.assertLess(1*gain-setup,0);self.assertGreater(20*gain-setup,0);self.assertNotEqual(sample_count,20)
    def test_exact_inference_width_ledger(self):
        a=np.array([c.SCALE//3]*2048,dtype=np.int64);v=c.endpoint_interval(a,a+7,0,1)
        self.assertEqual(F(v['width']),F(v['mean_bin_enclosure_width'])+F(v['sampling_radius_lower'])+F(v['sampling_radius_upper'])+2*F(v['range_radius']))
    def test_all_frozen_controllers_feasible(self):
        for a in c.actors():
            for t,i,j in np.ndindex(a['actions'].shape):self.assertLessEqual(F(int(a['actions'][t,i,j]),4096),F(1,8)+F(i+j,16*a['n']))
    def test_current_estimand_catalogue(self):
        r=json.loads((R/'results74/study.json').read_text());self.assertEqual(len(r['inference']['contrasts']),8);self.assertEqual(len(r['inference']['absolute_costs']),5);self.assertEqual(r['original_law_rows'],131072)
    def test_prior_sections_preserved_once(self):
        m=json.loads((R/'audit/PREPARATION75.json').read_text())
        for name,h in m['active_sections'].items():
            self.assertEqual(hashlib.sha256((R/name).read_bytes()).hexdigest(),h)
            count=sum((R/(doc+'.tex')).read_text().count('\\input{'+name[:-4]+'}') for doc in ('ECTA','supp','appendix'));self.assertEqual(count,1)
if __name__=='__main__':unittest.main(verbosity=2)
