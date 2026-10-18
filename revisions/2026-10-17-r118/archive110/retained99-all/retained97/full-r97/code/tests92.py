"""Adversarial exact tests for R92. Test count is not a sample size."""
from fractions import Fraction as F
from itertools import permutations,product
import copy,unittest
import centered92 as c
import independent92 as independent

class CenteredRiskTests(unittest.TestCase):
    def setUp(self):
        self.m=c.fixture(2,F(1,2),0);self.k,self.r,self.pi=c.prepare(self.m)
    def record(self,m=None):
        m=self.m if m is None else m;k,r,pi=c.prepare(m);bs=[c.bounds(m,k,r,pi,v) for v in (F(0),F(1,64),F(1,8))]
        return {'model':m,'kernels':k,'residuals':r,'policy':pi,'bounds':bs,'flow':c.flow(m,k,r,pi,bs[0])}
    def test_probability_rejects_negative(self):
        with self.assertRaises(ValueError):c.probability((-1,2))
    def test_probability_rejects_wrong_total(self):
        with self.assertRaises(ValueError):c.probability((1,1))
    def test_probability_rejects_empty(self):
        with self.assertRaises(ValueError):c.probability(())
    def test_float_inputs_are_not_exact(self):
        with self.assertRaises(TypeError):c.rational(0.1)
    def test_risk_level_one_rejected(self):
        with self.assertRaises(ValueError):c.vertices((F(1),),F(1))
    def test_negative_risk_level_rejected(self):
        with self.assertRaises(ValueError):c.vertices((F(1),),F(-1))
    def test_negative_radius_rejected(self):
        with self.assertRaises(ValueError):c.bounds(self.m,self.k,self.r,self.pi,-1)
    def test_dot_dimension_rejected(self):
        with self.assertRaises(ValueError):c.dot((1,),(1,2))
    def test_reversed_box_rejected(self):
        with self.assertRaises(ValueError):c.support_box((F(1),),(F(1),),(F(0),))
    def test_empty_risk_piece_set_rejected(self):
        with self.assertRaises(ValueError):c.evaluate(self.k[0][0][0],(0,0,0),[])
    def test_duplicate_piece_rejected(self):
        with self.assertRaises(ValueError):c.evaluate(self.k[0][0][0],(0,0,0),[0,0])
    def test_expectation_limit(self):
        p=(F(1,3),F(2,3));k=c.kernel(p,0,(2,-3))
        self.assertEqual(k['q'],(p,));self.assertEqual(c.evaluate(k,(4,7)),F(6))
    def test_zero_probability_retained(self):
        p=(F(0),F(1,2),F(1,2));qs=c.vertices(p,F(1,2))
        self.assertTrue(all(q[0]==0 for q in qs))
        self.assertEqual(max(c.dot(q,(999,0,1)) for q in qs),1)
    def test_quantile_atom_threshold_agrees(self):
        p=(F(1,4),F(1,2),F(1,4));v=(0,1,2);a=F(1,2)
        self.assertEqual(c.kernel(p,a,v)['reference'],independent.tail(p,v,a))
    def test_vertex_completeness_by_independent_orderings(self):
        for p,a in product(((F(1,3),)*3,(F(1,4),F(1,2),F(1,4))), (F(0),F(1,2),F(3,4))):
            out=set()
            for order in permutations(range(3)):
                q=[F(0)]*3;left=F(1)
                for i in order:q[i]=min(left,p[i]/(1-a));left-=q[i]
                self.assertEqual(left,0);out.add(tuple(q))
            self.assertEqual(out,set(c.vertices(p,a)))
    def test_exact_centering_all_perturbations(self):
        p=(F(1,4),F(1,2),F(1,4));f=(0,1,2);k=c.kernel(p,F(1,2),f)
        for z in product((-1,0,2),repeat=3):
            self.assertEqual(c.evaluate(k,z),independent.tail(p,[x+y for x,y in zip(f,z)],F(1,2))-independent.tail(p,f,F(1,2)))
    def test_centered_zero(self):
        self.assertEqual(c.evaluate(self.k[0][0][0],(0,0,0)),0)
    def test_cash_invariance(self):
        k=self.k[0][0][0];z=(F(1),F(-2),F(3))
        self.assertEqual(c.evaluate(k,[v+5 for v in z]),c.evaluate(k,z)+5)
    def test_reference_constant_shift_does_not_change_penalty(self):
        p=(F(1,2),F(1,2));a=c.kernel(p,F(1,2),(0,1));b=c.kernel(p,F(1,2),(9,10))
        self.assertEqual(a['k'],b['k'])
    def test_inactive_reference_kernel_can_become_active(self):
        k=c.kernel((F(1,2),)*2,F(1,2),(0,1));j=min(range(len(k['q'])),key=lambda j:k['k'][j])
        self.assertEqual(c.evaluate(k,(2,0)),1);self.assertEqual(c.evaluate(k,(2,0),[j]),0)
    def test_dropping_penalty_is_strictly_loose(self):
        k=c.kernel((F(1,2),)*2,F(1,2),(0,1))
        self.assertEqual(max(c.dot(q,(2,0)) for q in k['q']),2);self.assertEqual(c.evaluate(k,(2,0)),1)
    def test_strict_support_prunes(self):
        k=c.kernel((F(1,2),)*2,F(1,2),(0,1));kept,cuts=c.safe_pieces(k,(0,0),(F(1,2),F(1,2)))
        self.assertEqual(len(kept),1);self.assertEqual(len(cuts),1)
    def test_equality_support_is_retained(self):
        k=c.kernel((F(1,2),)*2,F(1,2),(0,1));kept,cuts=c.safe_pieces(k,(0,0),(1,1))
        self.assertEqual(len(kept),2);self.assertFalse(cuts)
    def test_box_support_matches_all_vertices(self):
        d=(F(-1,3),F(1,2),F(-1,6));lo=(-2,1,-3);hi=(1,4,2)
        self.assertEqual(c.support_box(d,lo,hi),max(c.dot(d,z) for z in product(*zip(lo,hi))))
    def test_exact_original_value_independent(self):
        independent.verify_record(self.record())
    def test_terminal_and_zero_discount(self):
        m=copy.deepcopy(self.m);m['beta'][0]=F(0);rec=self.record(m)
        independent.verify_record(rec)
        self.assertEqual(rec['bounds'][0]['initial_loss_bounds'],[F(0)]*3)
    def test_state_dependent_bias_propagated(self):
        for T in (2,4,8):
            m=c.absorbing(T);k,r,pi=c.prepare(m);b=c.bounds(m,k,r,pi,0)
            self.assertEqual(b['scalar_bound'],T);self.assertEqual(b['initial_loss_bounds'],[0,0])
    def test_datewise_shift_preserves_loss(self):
        old=self.record();m=copy.deepcopy(self.m)
        for t,row in enumerate(m['f']):m['f'][t]=[x+F((t+1)**2,3) for x in row]
        new=self.record(m);independent.verify_record(new)
        for a,b in zip(old['bounds'],new['bounds']):self.assertEqual(a['initial_loss_bounds'],b['initial_loss_bounds'])
    def test_wider_radius_never_sharpens_exact_recursion(self):
        bs=self.record()['bounds']
        for first,second in zip(bs,bs[1:]):
            self.assertTrue(all(a<=b for a,b in zip(first['initial_loss_bounds'],second['initial_loss_bounds'])))
    def test_action_risk_order_not_joint_minimum(self):
        matrix=((0,2),(2,0))
        self.assertEqual(min(max(row) for row in matrix),2)
        self.assertEqual(min(min(row) for row in matrix),0)
    def test_corrupted_occupation_rejected(self):
        rec=self.record();rec['flow']['masses'][1][0]+=F(1,7)
        with self.assertRaises(AssertionError):independent.verify_record(rec)
    def test_corrupted_penalty_rejected(self):
        rec=self.record();rec['kernels'][0][0][0]['k']=tuple(v+1 for v in rec['kernels'][0][0][0]['k'])
        with self.assertRaises(AssertionError):independent.verify_record(rec)
    def test_missing_cut_node_rejected(self):
        rec=self.record();rec['bounds'][0]['cuts'].pop()
        with self.assertRaises(AssertionError):independent.verify_record(rec)
    def test_invalid_supersolution_rejected(self):
        rec=self.record();rec['bounds'][1]['U'][0][0]-=1
        with self.assertRaises(AssertionError):independent.verify_record(rec)
    def test_signed_terminal_values_retained(self):
        rec=self.record();independent.verify_record(rec)
        self.assertLess(rec['model']['g'][2],0)

if __name__=='__main__':unittest.main(verbosity=2)
