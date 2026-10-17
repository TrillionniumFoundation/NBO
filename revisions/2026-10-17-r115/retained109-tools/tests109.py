"""Exact finite algebra regressions for R109 theory; not formal proof certification."""
from fractions import Fraction as F
from pathlib import Path
import json,unittest

class TailAlgebra(unittest.TestCase):
    def risk(self,k,a,R=F(1,32)):
        t=1-a
        if abs(k)<=10*R*t:return 5*R*R*(1+a+a*a)/3+a*k*k/(20*t)
        return 5*R*R*(4*a*a-2*a+1)/3+a*R*abs(k)
    def integral(self,k,lo,hi):return F(5,3)*(hi**3-lo**3)+k*(hi**2-lo**2)/2
    def direct(self,k,a,R=F(1,32)):
        t=1-a
        if abs(k)<=10*R*t:
            lo=-k/10-R*a;hi=-k/10+R*a
            return (self.integral(k,-R,R)-self.integral(k,lo,hi))/(2*R*t)
        if k>0:return self.integral(k,R*(2*a-1),R)/(2*R*t)
        return self.integral(k,-R,R*(1-2*a))/(2*R*t)
    def test_tail_integrals(self):
        for a in (F(1,4),F(1,2),F(3,4),F(7,8)):
            for n in range(-32,33):self.assertEqual(self.risk(F(n,64),a),self.direct(F(n,64),a))
    def test_junction_values(self):
        R=F(1,32)
        for a in (F(1,4),F(1,2),F(3,4)):
            k=10*R*(1-a)
            self.assertEqual(5*R*R*(1+a+a*a)/3+a*k*k/(20*(1-a)),5*R*R*(4*a*a-2*a+1)/3+a*R*k)
    def test_junction_derivatives(self):
        for a in (F(1,4),F(1,2),F(3,4)):
            k=10*F(1,32)*(1-a)
            self.assertEqual(a*k/(10*(1-a)),a/32)
    def test_reflection(self):
        for n in range(33):self.assertEqual(self.risk(F(n,64),F(1,2)),self.risk(F(-n,64),F(1,2)))
    def test_direction_only_counterexample(self):
        true=lambda a:a*a+abs(a+1)/2
        surrogate=lambda a:a*a+abs(a-1)/2
        a,b=F(-1,4),F(1,4)
        self.assertEqual(true(b)-true(a),F(1,4));self.assertEqual(surrogate(a)-surrogate(b),F(1,4))
    def test_centered_density_cancellation(self):
        # Exact equal-mass tail-set algebra; not a replacement for atomless assumptions.
        g=[F(2),F(4),F(8),F(16)];a=[0,1,1,0];b=[1,0,0,1]
        for v0 in (F(0),F(3),F(9)):
            self.assertEqual(sum((x-y)*(z-v0) for x,y,z in zip(a,b,g)),sum((x-y)*z for x,y,z in zip(a,b,g)))
    def test_tail_symmetric_difference_cap(self):
        import itertools
        for n in range(2,9):
            for k in range(1,n):
                for b in itertools.combinations(range(n),k):
                    a=set(range(k));self.assertLessEqual(len(a^set(b)),2*min(k,n-k))
    def test_zero_tail_oscillation(self):
        # A constant gradient contributes zero under any two equal-mass densities.
        self.assertEqual(sum(F(7)*(x-y) for x,y in zip((0,2),(2,0))),0)

class SafeAlgebra(unittest.TestCase):
    def gate(self,old,new):return new[1]<old[0]
    def test_strict_gate(self):self.assertTrue(self.gate((F(3),F(4)),(F(1),F(2))))
    def test_touching_refused(self):self.assertFalse(self.gate((F(2),F(3)),(F(1),F(2))))
    def test_overlap_refused(self):self.assertFalse(self.gate((F(1),F(3)),(F(1),F(2))))
    def test_regret_bound_improvement_not_cost(self):
        self.assertLess(F(1,20),F(1,10))
        self.assertFalse(self.gate((F(1),F(11,10)),(F(2),F(21,10))))
    def test_lower_boundary_normal(self):
        a=F(0);s=F(2);b=max(F(0),min(F(1),a-s/2));self.assertEqual(s*(b-a)+(b-a)**2,0)
    def test_upper_boundary_normal(self):
        a=F(1);s=F(-2);b=max(F(0),min(F(1),a-s/2));self.assertEqual(s*(b-a)+(b-a)**2,0)
    def test_recursive_gain_risk_distortion(self):
        beta=F(1,2);old=(F(4),F(3));new=(F(2),F(2));r=(F(1),F(0));D=tuple(a-b for a,b in zip(old,new))
        self.assertEqual(old,tuple(c+beta*max(old) for c in (2,1)))
        self.assertEqual(new,tuple(c+beta*max(new) for c in (1,1)))
        self.assertEqual(D,tuple(v+beta*max(D) for v in r))
        lower=(F(1),F(0));self.assertEqual(lower,tuple(v+beta*min(lower) for v in r))
        self.assertTrue(all(l<=d for l,d in zip(lower,D)))
        physical=(F(3,2),F(1,2));self.assertNotEqual(D,physical)
    def test_policy_residual_stopping(self):
        # One-state two-action original problem, exact values.
        beta=F(3,4);J=F(8);V=F(4);residual=J-min(F(1)+beta*J,F(2)+beta*J)
        self.assertEqual((J-V)*(1-beta),residual)
    def test_dyadic_gate_resolution(self):
        for A in (F(1),F(3),F(7)):
            for gain in (F(1,2),F(1,16),F(1,256)):
                n=1;work=1
                while 2*A/F(n*n)>=gain:n*=2;work+=n
                self.assertLess(2*A/F(n*n),gain);self.assertLess(work,4*n)
    def test_zero_gain_not_strict(self):
        for n in (1,2,4,16):self.assertFalse(self.gate((F(1)-F(1,n*n),F(1)),(F(1),F(1)+F(1,n*n)) ))
    def test_unit_consistent_stopping(self):
        upper=F(3);lb=F(2);cost=F(1)
        self.assertLessEqual(upper-lb-cost,0)

class SourceSafety(unittest.TestCase):
    def test_no_control_characters(self):
        root=Path(__file__).resolve().parents[1]
        for p in (root/'new109').glob('*.tex'):
            self.assertFalse(any(c<32 and c not in (9,10,13) for c in p.read_bytes()),str(p))
    def test_record_audit_passed(self):
        root=Path(__file__).resolve().parents[1];r=json.loads((root/'evidence109/SUMMARY109.json').read_text())
        self.assertEqual(r['record_audit']['decision_rows'],18432);self.assertEqual(r['record_audit']['trial_rows'],27648)
        self.assertEqual(r['record_audit']['status'],'passed')
    def test_no_unearned_population_claim(self):
        root=Path(__file__).resolve().parents[1];r=json.loads((root/'evidence109/SUMMARY109.json').read_text())
        self.assertFalse(r['statistical_confidence_intervals']);self.assertFalse(r['neural_specific_frontier_claim'])
    def test_equivalent_geometry(self):
        root=Path(__file__).resolve().parents[1];r=json.loads((root/'evidence109/SUMMARY109.json').read_text())
        self.assertTrue(all(x['all_rows_exactly_equal'] for x in r['hinge_identities']))

if __name__=='__main__':unittest.main(verbosity=2)
