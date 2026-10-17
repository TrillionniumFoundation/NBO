"""R91-added regression coverage for inherited R86 claims.

The R90 recipe named a tests86.py that was absent from its tree. This is newly
written coverage, not a recovered historical execution or proof of the general
theorems. It tests joint-domain cones, adaptive cover probabilities, work margins,
owner feasibility and robust price regions using independent exact examples.
"""
from fractions import Fraction as F
from itertools import product
import unittest


def relu(x): return max(x,F(0))
def native_cone(x,sites,labels,L):
    return min(y+L*sum(abs(a-b) for a,b in zip(x,z)) for z,y in zip(sites,labels))
def circuit(x,sites,labels,L):
    values=[y+L*sum(relu(a-b)+relu(b-a) for a,b in zip(x,z)) for z,y in zip(sites,labels)]
    while len(values)>1:
        values=[values[i]-relu(values[i]-values[i+1]) if i+1<len(values) else values[i] for i in range(0,len(values),2)]
    return values[0]
def adaptive_miss(n):
    total=F(0)
    for seq in product(range(3),repeat=n):
        p=F(1);history=[]
        for x in seq:
            favored=history[-1] if history else 0
            p*=F(1,2) if x==favored else F(1,4);history.append(x)
        if len(set(seq))<3:total+=p
    return total

class InheritedTheoryRegression(unittest.TestCase):
    sites=tuple(product((F(0),F(1,2),F(1)),repeat=2))
    labels=tuple(x+2*y for x,y in sites)
    def test_affine_relu_and_native_min_plus_agree(self):
        for x in product(tuple(F(i,8) for i in range(9)),repeat=2):
            self.assertEqual(circuit(x,self.sites,self.labels,2),native_cone(x,self.sites,self.labels,2))
    def test_joint_domain_labels_are_interpolated(self):
        for x,y in zip(self.sites,self.labels):self.assertEqual(circuit(x,self.sites,self.labels,2),y)
    def test_joint_domain_uniform_error_example(self):
        for x in product(tuple(F(i,8) for i in range(9)),repeat=2):
            error=circuit(x,self.sites,self.labels,2)-(x[0]+2*x[1])
            self.assertTrue(0<=error<=2)
    def test_shift_invariance_of_joint_circuit(self):
        labels=tuple(v+F(7,3) for v in self.labels)
        for x in self.sites:self.assertEqual(circuit(x,self.sites,labels,2),circuit(x,self.sites,self.labels,2)+F(7,3))
    def test_all_adaptive_conditional_hit_probabilities(self):
        for history in product(range(3),repeat=3):
            probs=[F(1,2) if x==history[-1] else F(1,4) for x in range(3)]
            self.assertEqual(sum(probs),1);self.assertGreaterEqual(min(probs),F(1,4))
    def test_dependent_acquisition_union_bound(self):
        for n in range(2,7):self.assertLessEqual(adaptive_miss(n),min(F(1),3*F(3,4)**n))
    def test_no_coverage_claim_without_hit_probability(self):
        never_hit=F(1);valid_union_bound=min(F(1),3*(1-F(0))**8)
        self.assertEqual(never_hit,valid_union_bound)
    def test_original_owner_feasibility_repair(self):
        original_cap=lambda x:F(1,8)+sum(x)/16
        source=(F(1),F(1));owner=(F(0),F(0));witness=original_cap(source)
        self.assertGreater(witness,original_cap(owner))
        repaired=min(witness,original_cap(owner));self.assertEqual(repaired,F(1,8))
    def test_tie_mass_must_remain_in_work_bound(self):
        gap=(F(0),F(1,8),F(1,2));prob=(F(1,4),F(1,4),F(1,2));e=F(1,16)
        bad=sum(p for g,p in zip(gap,prob) if g<=4*e)
        positive_bad=sum(p for g,p in zip(gap,prob) if 0<g<=4*e)
        self.assertEqual(1+10*bad,6);self.assertLess(1+10*positive_bad,1+10*bad)
    def test_margin_threshold_equality_is_not_strict_separation(self):
        e=F(1,16);self.assertFalse(F(1,4)>4*e);self.assertTrue(F(5,16)>4*e)
    def test_resource_upper_bounds_do_not_prove_speedup(self):
        true_proposal,true_baseline=10,1;proposal_upper,baseline_upper=11,100
        self.assertLess(proposal_upper,baseline_upper);self.assertGreater(true_proposal,true_baseline)
    def test_fixed_calibration_selection_is_not_test_winner(self):
        calibration={'first':4,'second':5};evaluation={'first':8,'second':2}
        selected=min(calibration,key=calibration.get)
        self.assertEqual(selected,'first');self.assertEqual(evaluation[selected]-min(evaluation.values()),6)
    def test_uniform_price_region_checked_at_vertices(self):
        score=lambda price,fee:-F(1,4)+2*price+fee
        vertices=tuple(product((F(0),F(1,16)),(F(0),F(1,16))))
        self.assertLessEqual(max(score(*v) for v in vertices),0)
        for p,f in product(tuple(F(i,64) for i in range(5)),repeat=2):self.assertLessEqual(score(p,f),0)
    def test_negative_fee_ceiling_is_not_deleted(self):
        upper_cost=F(1,8);fee_ceiling=-upper_cost
        self.assertLess(fee_ceiling,0);self.assertGreater(upper_cost+0,0)

if __name__=='__main__':unittest.main(verbosity=2)
