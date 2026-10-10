"""Exact regression tests for operational NBO certification and readout fitting."""
import unittest
from fractions import Fraction as F
from itertools import product
import certificates67 as c

class ReadoutTests(unittest.TestCase):
    def test_hat_partition_identity(self):
        for knots in ((F(0),F(1,4),F(1,2),F(1)),(F(0),F(1,10),F(9,10),F(1))):
            for j in range(101):
                p=c.hat_features(F(j,100),knots)
                self.assertEqual(sum(p),1);self.assertGreaterEqual(min(p),0)
    def test_hat_nodal_values(self):
        knots=tuple(F(j,4) for j in range(5))
        for j,z in enumerate(knots):self.assertEqual(c.hat_features(z,knots),tuple(F(i==j) for i in range(5)))
    def test_hat_invalid_inputs(self):
        for x,knots in ((F(-1),(F(0),F(1))),(F(0),(F(1),F(0))),(F(0),(F(0),))):
            with self.assertRaises(ValueError):c.hat_features(x,knots)
    def test_box_fraction_feasible(self):
        p=c.hat_features(F(3,8),(F(0),F(1,4),F(1,2),F(1)))
        for w in product((F(0),F(1,2),F(1)),repeat=4):
            self.assertGreaterEqual(c.fraction(p,w),0);self.assertLessEqual(c.fraction(p,w),1)
    def test_invalid_readout_rejected(self):
        with self.assertRaises(ValueError):c.fraction((F(1),),(F(2),))
        with self.assertRaises(ValueError):c.fraction((F(1,2),),(F(0),))
    def test_chord_quadratic_exact(self):
        ctx=c.Context(F(0),F(1),F(1,4),F(1,4),F(0),F(1,100),F(2))
        for j in range(101):self.assertEqual(ctx.chord(F(j,100)),(F(j,100)-F(1,2))**2)
    def test_smaller_curvature_is_safe(self):
        for m,h in product((F(1),F(2),F(3)),repeat=2):
            if m>h:continue
            ctx=c.Context(F(0),F(1),h/8,h/8,F(0),F(1,100),m)
            for j in range(21):self.assertGreaterEqual(ctx.chord(F(j,20)),h*(F(j,20)-F(1,2))**2/2)
    def test_operational_nonvacuous_closure(self):
        ctx=c.Context(F(0),F(1),F(1,4),F(1,4),F(0),F(1,100))
        self.assertLessEqual(ctx.score(F(1,2)),ctx.tolerance)
        self.assertGreater(ctx.upper_left-ctx.lower,ctx.tolerance)
    def test_upper_endpoints_never_assumed_exact(self):
        ctx=c.Context(F(0),F(1),F(3,10),F(2,5),F(0),F(1,100))
        for j in range(21):self.assertGreaterEqual(ctx.chord(F(j,20)),(F(j,20)-F(1,2))**2)
    def test_boundary_optimum_screen(self):
        ctx=c.Context(F(0),F(1),F(0),F(2),F(0),F(1,100))
        self.assertEqual(ctx.score(F(0)),0);self.assertGreater(ctx.score(F(1,2)),ctx.tolerance)
    def test_rounding_allowance_charged(self):
        ctx=c.Context(F(0),F(1),F(1,4),F(1,4),F(0),F(1,100),rounding_allowance=F(1,50))
        self.assertGreater(ctx.score(F(1,2)),ctx.tolerance)
    def test_score_direction_not_sample_fit(self):
        ctx=c.Context(F(0),F(1),F(1,4),F(1,4),F(-1),F(1,100))
        self.assertGreater(ctx.score(F(1,2)),ctx.tolerance)
        # Even a perfect optimal-action label cannot repair a loose lower bound.
    def example(self):
        contexts=[c.Context(F(0),F(1),F(1,16),F(9,16),F(0),F(1,32),work_cap=F(4)),c.Context(F(0),F(1),F(9,16),F(1,16),F(0),F(1,32),work_cap=F(8))]
        features=((F(1),F(0)),(F(0),F(1)))
        return contexts,features
    def test_convex_training_loss(self):
        contexts,features=self.example();u=(F(0),F(1));v=(F(1),F(0))
        for j in range(11):
            t=F(j,10);w=tuple((1-t)*a+t*b for a,b in zip(u,v))
            fx=lambda x:c.objective(contexts,features,x,F(1,64),F(1,100))['value']
            self.assertLessEqual(fx(w),(1-t)*fx(u)+t*fx(v))
    def test_gradient_at_zero_hinge(self):
        ctx=c.Context(F(0),F(1),F(1,4),F(1,4),F(0),F(1,100))
        r=c.objective([ctx],[(F(1),)],(F(1,2),),F(1,100))
        self.assertEqual(r['gradient'],(F(0),));self.assertEqual(r['value'],0)
    def test_exact_box_gap_dominates_grid_improvement(self):
        contexts,features=self.example();w=(F(1,3),F(2,3));r=c.objective(contexts,features,w,F(1,64),F(1,100))
        for v in product((F(0),F(1,4),F(1,2),F(3,4),F(1)),repeat=2):
            self.assertLessEqual(r['value']-c.objective(contexts,features,v,F(1,64),F(1,100))['value'],r['dual_gap'])
    def test_work_loss_bounds_failed_catalogue(self):
        contexts,features=self.example()
        for w in product((F(0),F(1,4),F(1,2),F(3,4),F(1)),repeat=2):
            r=c.objective(contexts,features,w,F(1,64));actual=sum(ctx.work_cap for ctx,phi in zip(contexts,features) if ctx.score(c.fraction(phi,w))>ctx.tolerance)/2
            self.assertLessEqual(actual,r['average_work_upper'])
    def test_training_returns_achieved_certificate(self):
        contexts,features=self.example();r=c.fit_readout(contexts,features,F(1,64),iterations=96)
        self.assertLess(r['best']['value'],r['history'][0]['value'])
        self.assertEqual(r['best']['failures'],0)
        self.assertGreaterEqual(r['best']['dual_gap'],0)
    def test_zero_iterations_is_honest_finite_return(self):
        contexts,features=self.example();r=c.fit_readout(contexts,features,F(1,64),iterations=0)
        self.assertEqual(len(r['history']),1);self.assertEqual(r['best']['weights'],(F(1,2),F(1,2)))
    def test_clipped_margin_majorizes_failure(self):
        tau=F(1,16);delta=F(1,8)
        for j in range(-10,31):
            score=F(j,32);loss=min(F(1),max(F(0),score-delta+tau)**2/tau**2)
            self.assertLessEqual(int(score>delta),loss)
    def test_weighted_work_bound(self):
        for cap,loss in product((F(0),F(1),F(7)),(F(0),F(1,2),F(1))):
            indicator=int(loss==1);self.assertLessEqual(cap*indicator,cap*loss)
    def test_triangle_minorant_on_exact_quadratic(self):
        vertices=((F(0),F(0)),(F(1),F(0)),(F(0),F(1)));H=F(3)
        f=lambda a:H*sum(v*v for v in a)/2+sum(a)/7+F(1,13)
        for i in range(11):
            for j in range(11-i):
                weights=(F(10-i-j,10),F(i,10),F(j,10));x=(F(i,10),F(j,10))
                minor=sum(t*f(v) for t,v in zip(weights,vertices))-H/2*sum(t*sum((a-b)**2 for a,b in zip(v,x)) for t,v in zip(weights,vertices))
                self.assertEqual(minor,f(x))
    def test_dual_support_point_need_not_be_feasible(self):
        vertices=((F(0),F(0)),(F(1),F(0)),(F(0),F(1)))
        f=lambda a:sum(v*v for v in a)-sum(a)/3
        for y in ((F(3),F(-5)),(F(1,6),F(1,6))):
            grad=tuple(2*v-F(1,3) for v in y);lower=f(y)+min(sum(g*(v-a) for g,v,a in zip(grad,x,y)) for x in vertices)
            self.assertLessEqual(lower,F(-1,18))
    def test_two_shock_variance_constant(self):
        self.assertEqual((F(1,32)**2+F(1,64)**2)/6,F(5,24576))
    def test_simplex_vertex_count(self):
        for A in range(1,25):self.assertEqual(sum(A+1-i for i in range(A+1)),(A+1)*(A+2)//2)

if __name__=='__main__':unittest.main(verbosity=2)
