"""Exact finite regression tests for the R59 theorem statements.
These fixtures do not add economic samples or production timing observations.
"""
from fractions import Fraction as F
from math import isqrt
import random,unittest
import numpy as np
import screen58 as sc

def screen(values,lower,upper):
    if not values or not(len(values)==len(lower)==len(upper)):raise ValueError('incomplete intervals')
    if any(not l<=v<=u for v,l,u in zip(values,lower,upper)):raise ValueError('invalid enclosure')
    b=min(upper);keep=[k for k,l in enumerate(lower) if l<=b]
    return min(keep,key=lambda k:(values[k],k)),keep

class LosslessTheoremTests(unittest.TestCase):
    def test_all_exact_minimizers_and_ties_survive(self):
        rng=random.Random(590271)
        for _ in range(200):
            v=[F(rng.randrange(-5,6),8) for _ in range(25)]
            lo=[x-F(rng.randrange(5),32) for x in v];hi=[x+F(rng.randrange(5),32) for x in v]
            best,keep=screen(v,lo,hi);mins=[k for k,x in enumerate(v) if x==min(v)]
            self.assertTrue(set(mins)<=set(keep));self.assertEqual(best,min(mins))
    def test_survivor_regret_bound(self):
        rng=random.Random(590311)
        for _ in range(200):
            v=[F(rng.randrange(-20,21),16) for _ in range(30)]
            lo=[x-F(rng.randrange(9),64) for x in v];hi=[x+F(rng.randrange(9),64) for x in v]
            _,keep=screen(v,lo,hi);eta=max(u-l for l,u in zip(lo,hi))
            for k in keep:self.assertLessEqual(v[k]-min(v),2*eta)
    def test_factor_two_cannot_be_reduced(self):
        v=[F(0),F(2)];lo=[F(0),F(1)];hi=[F(1),F(2)]
        best,keep=screen(v,lo,hi);self.assertEqual(keep,[0,1]);self.assertEqual(best,0)
        self.assertEqual(v[1]-v[0],2*max(u-l for l,u in zip(lo,hi)))
    def test_unique_gap_is_singleton(self):
        v=[F(2),F(-1),F(3)];eta=F(1,8)
        best,keep=screen(v,[x-eta/2 for x in v],[x+eta/2 for x in v]);self.assertEqual((best,keep),(1,[1]))
    def test_weak_screen_inequality_is_required(self):
        v=[F(0),F(0)];best,keep=screen(v,v,v)
        self.assertEqual((best,keep),(0,[0,1]));self.assertEqual([k for k,l in enumerate(v) if l<min(v)],[])
    def test_discrete_growth_cardinality(self):
        delta=F(1,16);mu=F(3,2);eta=F(1,128);centers=[5,21];N=33
        v=[mu*min((F(k-c)*delta)**2 for c in centers)/2 for k in range(N)]
        _,keep=screen(v,[x-eta/2 for x in v],[x+eta/2 for x in v])
        radius_squared=4*eta/(mu*delta**2)
        radius=isqrt(radius_squared.numerator//radius_squared.denominator)
        self.assertLessEqual(len(keep),min(N,len(centers)*(1+2*radius)))
        for k in keep:self.assertLessEqual(min((F(k-c)*delta)**2 for c in centers),4*eta/mu)
    def test_wide_valid_intervals_may_keep_every_point(self):
        v=list(map(F,range(20)));_,keep=screen(v,[F(-100)]*20,[F(100)]*20)
        self.assertEqual(keep,list(range(20)))
    def test_constant_elimination_preserves_every_order(self):
        v=[F(7,9),F(-3,7),F(-3,7),F(1,5)];c=F(10**12,7)
        lo=[x-F(1,100) for x in v];hi=[x+F(1,100) for x in v]
        self.assertEqual(screen(v,lo,hi),screen([x+c for x in v],[x+c for x in lo],[x+c for x in hi]))
    def test_mathematical_stopping_transcript(self):
        stages=[([F(1),F(0),F(2)],[(F(-2),F(1)),(F(-1),F(0))]),([F(0),F(1)],[(F(-2),F(-1))])]
        def run(use_screen):
            history=[]
            for stage,(v,looks) in enumerate(stages):
                ix=screen(v,[x-F(1,16) for x in v],[x+F(1,16) for x in v])[0] if use_screen else min(range(len(v)),key=lambda k:(v[k],k))
                for look,(l,u) in enumerate(looks):
                    history.append((stage,look,ix,l,u))
                    if u<=0:return history,'target_attained'
                    if l>0:break
            return history,'budget_exhausted'
        self.assertEqual(run(False),run(True));self.assertEqual(len(run(True)[0]),2)
    def test_wall_time_deadline_is_a_distinct_contract(self):
        deadline=F(3);fast=[F(1),F(1)];slow=[F(2),F(2)]
        reached=lambda times:sum(sum(times[:k+1])<=deadline for k in range(len(times)))
        self.assertNotEqual(reached(fast),reached(slow))
    def test_exact_fitting_does_not_erase_evaluation_error(self):
        fitted=[F(0),F(1)];true=[F(1),F(0)];best=screen(fitted,fitted,fitted)[0]
        self.assertEqual(fitted[best]-min(fitted),0);self.assertGreater(true[best]-min(true),0)
    def test_price_and_adoption_identity(self):
        J=F(13,7);C_A=F(5);C_S=F(3);price=F(2,9);fee=F(1,10);l,u=F(1,3),F(3,5)
        self.assertEqual((J+price*C_S)-(J+price*C_A),price*(C_S-C_A))
        self.assertEqual((l-fee-price*C_S)-(l-fee-price*C_A),price*(C_A-C_S))
        self.assertEqual((u-fee-price*C_S)-(l-fee-price*C_S),u-l)

if __name__=='__main__':unittest.main(verbosity=2)
