"""Rational theorem regressions, not additional economic observations."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import math,sys,unittest
import numpy as np
import independent70 as i
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'2026-10-11-r69/code'))
import independent69 as p
import readout69 as r

class RevisionTests(unittest.TestCase):
    def test_interval_square_crossing(self):
        self.assertEqual(i.square((F(-2),F(3))),(F(0),F(9)))
        self.assertEqual(i.square((F(-3),F(-2))),(F(4),F(9)))

    def test_cost_intervals_contain_exact_corner_costs(self):
        for d in (2,4):
            box=[(F(j+1,16),F(j+2,16)) for j in range(d)]
            for m in (1,2):
                action=[F(1,32)]*m
                for terminal in (False,True):
                    interval=i.cost(box,action,terminal)
                    for x in product(*box):
                        exact=p.stage(list(x),action,terminal)
                        self.assertLessEqual(interval[0],exact);self.assertLessEqual(exact,interval[1])

    def test_monotone_transition_contains_all_corners(self):
        box=[(F(1,8),F(1,4)),(F(1,2),F(5,8))];z=(F(-1,32),F(1,32));w=(F(-1,64),F(1,64))
        for action in ([F(1,16)],[F(1,16),F(1,32)]):
            out=i.transition(box,action,z,w if len(action)==2 else i.iv(0))
            for x,shock,second in product(product(*box),z,w if len(action)==2 else [F(0)]):
                true=p.transition(list(x),action,shock,second)
                for bounds,value in zip(out,true):self.assertLessEqual(bounds[0],value);self.assertLessEqual(value,bounds[1])

    def test_terminal_moments_agree_with_point_cost_structure(self):
        # The analytic final expectation differs from a zero-shock point
        # evaluation by the known nonnegative innovation variance correction.
        for d in (2,8):
            x=[F(3,8)]*d;a=[F(1,32)]
            zero=p.stage(x,a)+p.B*p.stage(p.transition(x,a,F(0)),[],True)
            self.assertEqual(p.terminal_q(x,a)-zero,p.B*F(5,3072))

    def model(self,T=3):
        beta=F(3,4);g=[F(1,3),F(2,3)]
        costs=[[[F(1+x+2*a+t,16) for a in range(2)] for x in range(2)] for t in range(T)]
        probs=[[[F(3,4),F(1,4)],[F(1,4),F(3,4)]],[[F(1,2),F(1,2)],[F(3,4),F(1,4)]]]
        V=[None]*T+[g]
        for t in reversed(range(T)):
            V[t]=[min(costs[t][x][a]+beta*sum(probs[x][a][y]*V[t+1][y] for y in range(2)) for a in range(2)) for x in range(2)]
        return beta,costs,probs,V

    def trajectory_values(self,pi):
        T=len(pi);beta,c,P,V=self.model(T);out=[]
        for path in product(range(2),repeat=T+1):
            probability=F(1,2);cash=F(0);center=F(0);max_adv=[]
            for t in range(T):
                x,y=path[t:t+2];a=pi[t][x];probability*=P[x][a][y]
                cash+=beta**t*c[t][x][a]
                adv=c[t][x][a]+beta*sum(P[x][a][z]*V[t+1][z] for z in range(2))-V[t][x]
                self.assertGreaterEqual(adv,0);center+=beta**t*adv
            cash+=beta**T*V[T][path[T]]
            out.append((probability,cash,center,V[0][path[0]]))
        return out

    def test_centered_expectation_is_original_loss(self):
        for pi in ([[0,0]]*3,[[1,1]]*3,[[0,1],[1,0],[0,1]]):
            out=self.trajectory_values(pi)
            self.assertEqual(sum(p for p,*_ in out),1)
            self.assertEqual(sum(p*z for p,c,z,v in out),sum(p*(c-v) for p,c,z,v in out))

    def test_centered_difference_targets_actual_policy_difference(self):
        first=self.trajectory_values([[0,1]]*3);second=self.trajectory_values([[1,0]]*3)
        self.assertEqual(sum(p*z for p,c,z,v in first)-sum(p*z for p,c,z,v in second),sum(p*c for p,c,z,v in first)-sum(p*c for p,c,z,v in second))

    def test_centering_is_not_pathwise_cash_identity(self):
        out=self.trajectory_values([[1,0]]*3)
        self.assertTrue(any(z!=cash-v for probability,cash,z,v in out))

    def test_total_variation_transfer_with_factor_one(self):
        P=[F(1,2),F(1,4),F(1,4)];Q=[F(1,4),F(1,4),F(1,2)];K=F(17)
        tv=sum(abs(a-b) for a,b in zip(P,Q))/2
        for values in product((F(0),K/2,K),repeat=3):
            self.assertLessEqual(abs(sum((a-b)*v for a,b,v in zip(P,Q,values))),K*tv)
        self.assertEqual(abs(sum((a-b)*v for a,b,v in zip(P,Q,[K,0,0]))),K*tv)

    def test_predictable_weighted_conditional_means(self):
        # A dependent second Bernoulli variable; its conditional mean is
        # charged on the actual first-step history, not an IID substitution.
        c=[F(2),F(7)];expected=F(0);centered=F(0)
        for x,y in product((0,1),repeat=2):
            p1=F(1,2);p2=F(3,4) if x else F(1,4);prob=p1*(p2 if y else 1-p2)
            expected+=prob*(c[0]*x+c[1]*y)
            centered+=prob*(c[0]*(x-F(1,2))+c[1]*(y-p2))
        self.assertEqual(centered,0);self.assertEqual(expected,sum(c)/2)

    def test_failed_screen_is_dominated_by_clipped_margin_loss(self):
        tolerance=F(1,16);tau=tolerance/4;K=17
        for score in (F(0),tolerance-tau/2,tolerance,tolerance+tau):
            loss=min(F(1),max(F(0),score-tolerance+tau)**2/tau**2)
            count=K if score>tolerance else 0
            self.assertLessEqual(count,K*loss)

    def test_hat_and_bernstein_partition_of_unity(self):
        for d in (2,8):
            x=np.array([j/(d+1) for j in range(d)])
            for kind in ('hat-relu','bernstein4'):
                features=r.exact_phi(x,kind)
                self.assertEqual(len(features),5*d);self.assertEqual(sum(features),1);self.assertGreaterEqual(min(features),0)

    def test_adoption_multiplier_and_region(self):
        B,m,D=64,8,1;self.assertEqual(m*(B-D),504)
        lo,hi=F(-1,1000),F(1,1000);v=F(2);price=F(3);saving=F(1);fee=F(1,2)
        upper=v*m*(B-D)*hi-price*saving+fee
        self.assertEqual(upper<0,price*saving>fee+v*m*(B-D)*hi)
        self.assertLessEqual(v*m*(B-D)*lo-price*saving+fee,upper)

    def test_declines_cancel_benchmark_cost_in_expectation(self):
        delta=F(3,10000);actual=sum(8*(0 if block==16 else delta) for block in range(64))
        self.assertEqual(actual,504*delta)

    def test_log_allowance_covers_twelve_two_sided_contrasts(self):
        lower=sum((F(12)**k/F(math.factorial(k)) for k in range(20)),F(0))
        self.assertGreater(lower,2400);self.assertLess(F(24)/lower,F(1,100))

    def test_radius_and_numerical_budget(self):
        v=s=F(1,512);self.assertEqual(v+s,F(1,256))
        for width in (F(1,128),F(1,64)):
            squared=width**2*F(12,2*1024)
            self.assertLess(squared,s*s)

if __name__=='__main__':unittest.main(verbosity=2)
