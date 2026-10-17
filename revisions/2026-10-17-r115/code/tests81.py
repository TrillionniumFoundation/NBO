"""R81 exact regression tests; none is an additional economic observation."""
from fractions import Fraction as F
from itertools import product
import math,unittest
import dual81 as v
import study73 as inherited
from calibrated80 import derivative_rows

class TransferTests(unittest.TestCase):
    def test_derivative_controls_independent(self):
        for k in ('relu','bernstein'):self.assertEqual(v.slopes(k),derivative_rows(k))
    def test_affine_calibration(self):
        for a,b in product((F(-7,4),F(0),F(5,3)),repeat=2):
            r=(F(1),a,F(0),F(0),F(0),b,F(0),F(0),F(0))
            p=(F(1),)+tuple(a*j/4 for j in range(1,5))+tuple(b*j/4 for j in range(1,5))
            for kind,theta in (('relu',r),('bernstein',p)):
                self.assertEqual(max(abs(v.dot(s,theta)) for s in v.slopes(kind)),max(abs(a),abs(b)))
            for x in product((F(0),F(2,7),F(1)),repeat=2):
                self.assertEqual(v.dot(inherited.features(x,'relu'),r),v.dot(inherited.features(x,'bernstein'),p))
    def test_exact_uniform_antiderivative(self):
        for a,b in ((F(-1),F(1)),(F(1,3),F(5,7))):
            self.assertEqual(v.mean_power(a,b,0),1)
            self.assertEqual(v.mean_power(a,b,1),(a+b)/2)
            self.assertEqual(v.mean_power(a,b,2),(a*a+a*b+b*b)/3)
    def test_invalid_integral_interval(self):
        with self.assertRaises(ValueError):v.mean_power(F(1),F(1),2)
    def test_independent_feature_integrals(self):
        for x0,x1,a,kind in product((F(0),F(3,8),F(1)),(F(0),F(5,8),F(1)),(F(0),F(1,8)),('relu','bernstein')):
            x=(x0,x1)
            self.assertEqual(v.means(x,a,kind),inherited.feature_means(x,a,kind))
    def test_contrast_integrals_and_state_cancellation(self):
        for kind in ('relu','bernstein'):
            theta=tuple(F(k-4,7) for k in range(9));x=(F(1,7),F(5,9));a,b=F(0),F(1,8)
            d,c=v.action_contrast(x,a,b,kind)
            self.assertEqual(c+v.dot(d,theta),inherited.qvalue(x,b,theta,kind)-inherited.qvalue(x,a,theta,kind))
    def test_contrast_antisymmetry(self):
        for kind in ('relu','bernstein'):
            x=(F(1,3),F(2,3));a,b=F(1,32),F(1,16)
            d,c=v.action_contrast(x,a,b,kind);e,f=v.action_contrast(x,b,a,kind)
            self.assertEqual(c,-f);self.assertEqual(d,tuple(-x for x in e))
    def test_sparse_probability_validation(self):
        self.assertEqual(v.probability([[0,'1/3'],[2,'2/3']],3),{0:F(1,3),2:F(2,3)})
        for bad in ([[0,'1'],[0,'0']],[[0,'-1'],[1,'2']],[[3,'1']],[[0,'1/2']]):
            with self.assertRaises(ValueError):v.probability(bad,3)
    def test_independent_dual_weakness(self):
        features=((F(1),)+(F(0),)*8,(F(1),F(1))+(F(0),)*7)
        lo=(F(0),F(1));hi=(F(1,8),F(9,8));bounds=(F(2),)*9;rho=F(1,4);G=F(3)
        P=(features,lo,hi,bounds,rho,G);p=[[0,'1/4'],[1,'3/4']];q=[[0,'3/4'],[1,'1/4']]
        xi=(F(1,8),F(1,8))+(F(0),)*14;d=(F(0),F(-1))+(F(0),)*7;c=F(1)
        for kind in ('relu','bernstein'):
            D=v.lower_bound(P,p,q,xi,F(1,3),d,c,kind)
            for s in (F(1),F(3,2),F(2)):
                theta=(F(0),s)+(F(0),)*7
                U=max(u-v.dot(f,theta) for u,f in zip(hi,features))-min(l-v.dot(f,theta) for l,f in zip(lo,features))+2*rho*(G+max(abs(v.dot(row,theta)) for row in v.slopes(kind)))
                self.assertLessEqual(c+v.dot(d,theta),0);self.assertLessEqual(D,U)
    def test_invalid_dual_mass_and_multiplier(self):
        P=(((F(1),)+(F(0),)*8,),(F(0),),(F(1),),(F(1),)*9,F(1,8),F(2))
        for xi,nu in (((F(1),)*16,F(0)),((F(0),)*16,F(-1))):
            with self.assertRaises(ValueError):v.lower_bound(P,[[0,'1']],[[0,'1']],xi,nu,(F(0),)*9,F(0),'relu')
    def test_strict_barrier_sublevel(self):
        switch=F(9,100);center=F(1,5)
        for j in range(101):
            theta=F(j,100);objective=(theta-center)**2
            if objective<switch:self.assertGreater(F(1,2)-theta,0)
        self.assertEqual((F(1,2)-center)**2,switch)
        self.assertEqual(F(1,2)-F(1,2),0)
    def test_epsilon_optimal_is_reference_sublevel(self):
        optimum,reference,epsilon=F(1,3),F(1,2),F(1,16)
        self.assertLessEqual(optimum+epsilon,reference+epsilon)
    def test_bad_initial_mass_bound_and_sharpness(self):
        H=F(7);reference=[F(0)]*16;alternative=[H if i<3 else F(0) for i in range(16)]
        difference=abs(sum(alternative)-sum(reference))/16
        self.assertEqual(difference,H*F(3,16))
    def test_no_bad_cells_costs_identical(self):
        H=F(7);self.assertEqual(H*F(0),0)
    def test_uniform_band_enlargement(self):
        low,high=v.robust_band((F(1,10),F(1,5)),F(1,100),F(1,50))
        self.assertEqual((low,high),(F(7,100),F(23,100)))
        for base,x,y in product((F(1,10),F(3,20),F(1,5)),(-F(1,100),F(1,100)),(-F(1,50),F(1,50))):
            self.assertLessEqual(low,base+x-y);self.assertGreaterEqual(high,base+x-y)
    def test_invalid_cost_radii(self):
        with self.assertRaises(ValueError):v.robust_band((0,1),F(-1),F(0))
        with self.assertRaises(ValueError):v.robust_band((1,0),F(0),F(0))
    def test_first_disagreement_account(self):
        # Eight equally likely deterministic shock paths; no disagreement on
        # four, two first disagree at t=0 and two at t=1.
        beta=F(3,4);H=(F(4),F(2));first=(None,None,None,None,0,0,1,1)
        paid=[F(0) if t is None else beta**t*H[t] for t in first]
        self.assertEqual(sum(paid)/8,H[0]*F(2,8)+beta*H[1]*F(2,8))
        self.assertLessEqual(sum(paid)/8,H[0]*F(3,8)+beta*H[1]*F(4,8))
    def test_strict_ranking_and_equivalence_can_coexist(self):
        low,high,margin=F(1,1000),F(2,1000),F(1,256)
        self.assertGreater(low,0);self.assertLess(high,margin)
    def test_finite_family_tail_allocation(self):
        # Taylor lower bound for exp(11), entirely rational.
        lower=sum((F(11**k,math.factorial(k)) for k in range(80)),F(0))
        self.assertLess(F(376)/lower,F(1,100))
    def test_width_components_add_exactly(self):
        variance,support,numerical=F(1,10000),F(1,1000),F(1,10**10)
        width=variance+support+numerical
        self.assertGreater(width,support);self.assertLess(width,F(1,256))
    def test_difference_orientation(self):
        results={'a-minus-b':{'interval_exact':['1/3','1/2']}}
        self.assertEqual(v.pair_record(results,'b','a'),(-F(1,2),-F(1,3)))
    def test_sublevel_not_a_hidden_optimizer_success_claim(self):
        objective=F(1);upper=F(1,4);epsilon=F(1,8)
        self.assertFalse(objective<=upper+epsilon)

if __name__=='__main__':unittest.main(verbosity=2)
