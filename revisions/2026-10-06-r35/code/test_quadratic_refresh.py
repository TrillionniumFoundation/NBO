"""Exact rational tests; not independent economic replications."""
from fractions import Fraction as F
import unittest
import quadratic_refresh as q


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.M=q.matrix([[2,F(1,10)],[F(1,10),2]])
        self.W=q.matrix([[F(7,5),F(1,40)],[-F(1,50),F(7,5)],[F(1,100),0]])
        self.m=F(3,2)

    def test_noncommuting_start(self):
        H=q.mm(q.tr(self.W),self.W)
        self.assertNotEqual(q.mm(H,self.M),q.mm(self.M,H))
        self.assertLess(q.relative_gate(self.W,self.M,m=self.m),F(1,2))

    def test_exact_polynomial_identity(self):
        H=q.mm(q.tr(self.W),self.W); inv=q.r.inverse(self.M)
        E=q.add(q.mm(inv,H),q.eye(2),-1)
        plus=q.ideal_step(self.W,self.M)
        actual=q.add(q.mm(inv,q.mm(q.tr(plus),plus)),q.eye(2),-1)
        E2=q.mm(E,E)
        expected=q.add(q.scale(E2,-F(3,4)),q.scale(q.mm(E2,E),F(1,4)))
        self.assertEqual(actual,expected)

    def test_ideal_step_one_sided(self):
        radius=q.relative_gate(self.W,self.M,m=self.m)
        plus=q.ideal_step(self.W,self.M); H=q.mm(q.tr(plus),plus)
        q.psd(q.add(self.M,H,-1))
        q.psd(q.add(H,q.scale(self.M,1-F(7,8)*radius**2),-1))

    def test_quantized_step_entire_error(self):
        ideal=q.ideal_step(self.W,self.M)
        plus,nu=q.quantized_step(self.W,self.M,m=self.m,bits=20)
        self.assertLessEqual(q.norm2(q.add(plus,ideal,-1)),nu**2*self.m)

    def test_noisy_recurrence_certifies_iterates(self):
        w=self.W
        initial=q.relative_gate(w,self.M,m=self.m)
        nu=q.sqrt_up(6)/(2*(1<<32)*q.r.sqrt_down(self.m))
        plan=q.plan(initial=initial,tolerance=F(1,10**8),factor_error=nu)
        for bound in plan['bounds'][1:]:
            w,used=q.quantized_step(w,self.M,m=self.m,bits=32)
            self.assertLessEqual(used,nu)
            H=q.mm(q.tr(w),w)
            q.psd(q.add(H,q.scale(self.M,1-bound),-1))
            q.psd(q.add(q.scale(self.M,1+bound),H,-1))
        self.assertLessEqual(plan['bound'],F(1,10**8))

    def test_closed_envelope(self):
        p=q.plan(initial=F(1,3),tolerance=F(1,10**10),factor_error=F(1,10**15))
        for j,b in enumerate(p['bounds']):
            ideal=(p['c']*p['initial'])**(2**j)/p['c']
            self.assertLessEqual(b,ideal+p['floor']*(1-p['lipschitz']**j))

    def test_zero_steps(self):
        self.assertEqual(q.plan(initial=F(1,100),tolerance=F(1,50))['updates'],0)

    def test_precision_floor_rejected(self):
        with self.assertRaises(ValueError):
            q.plan(initial=F(1,3),tolerance=F(1,1000),factor_error=F(1,1000))

    def test_noise_basin_rejected(self):
        with self.assertRaises(ValueError):
            q.plan(initial=F(1,4),tolerance=F(1,10),factor_error=1)

    def test_resource_exhaustion_rejected(self):
        with self.assertRaises(ArithmeticError):
            q.plan(initial=F(1,2),tolerance=F(1,10**12),max_updates=0)

    def test_singular_factor_rejected(self):
        with self.assertRaises(ValueError):
            q.relative_gate(q.eye(2,0),self.M,m=self.m)

    def test_indefinite_target_rejected(self):
        with self.assertRaises(ValueError):
            q.relative_gate(self.W,[[1,0],[0,-1]],m=1)

    def test_false_target_floor_rejected(self):
        with self.assertRaises(ValueError):
            q.relative_gate(self.W,self.M,m=3)

    def test_wrong_shape_rejected(self):
        with self.assertRaises(ValueError):
            q.relative_gate([[1,2]],self.M,m=self.m)

    def test_transport(self):
        self.assertEqual(q.transport_gate(F(1,10),F(1,20)),F(31,200))

    def test_transport_failure(self):
        with self.assertRaises(ValueError):
            q.transport_gate(F(2,5),F(1,5))

    def test_relative_order_not_absolute_error(self):
        M=q.eye(2,10000); W=q.eye(2,99)
        self.assertLess(q.relative_gate(W,M,m=10000),F(1,2))

    def test_solve_residual_allowance(self):
        residual=q.matrix([[F(1,100),0],[F(1,200),-F(1,100)]])
        X=q.mm(q.r.inverse(self.M),q.add(q.mm(q.tr(self.W),self.W),residual))
        inexact=q.scale(q.mm(self.W,q.add(q.eye(2,3),X,-1)),F(1,2))
        ideal=q.ideal_step(self.W,self.M)
        residual_bound=q.sqrt_up(q.norm2(residual))/self.m
        nu=q.solve_error_bound(radius=F(1,2),whitened_solve_residual=residual_bound)
        Delta=q.add(inexact,ideal,-1)
        # This direct Frobenius/m bound is sufficient in the fixed test instance.
        self.assertLessEqual(q.norm2(Delta)/self.m,nu**2)

    def test_action_geometry_bound(self):
        d=2; M=self.M; H=q.mm(q.tr(self.W),self.W)
        B=q.matrix([[1,0],[0,0]]); C=q.matrix([[F(1,10),F(1,20)],[0,F(1,5)]])
        rho=q.relative_gate(self.W,M,m=self.m)
        B2=q.r.op_upper(q.mm(q.mm(q.tr(B),M),B))
        Fc=q.mm(q.mm(q.tr(C),M),C); F2=sum(Fc[i][i] for i in range(d))
        bound=q.economic_residual(gram_radius=rho,center_B_squared=B2,center_F_squared=F2,
            evaluation_radius=0,b_norm=1,f_frobenius=1,actor_error=0,beta=F(19,20),dimension=d)
        actual=q.scale(q.mm(q.mm(q.tr(B),q.add(H,M,-1)),C),F(19,40))
        self.assertLessEqual(q.norm2(actual),bound**2)

    def test_zero_control_direction(self):
        self.assertEqual(q.economic_residual(gram_radius=F(1,10),center_B_squared=0,
            center_F_squared=1,evaluation_radius=0,b_norm=0,f_frobenius=1,
            actor_error=F(1,100),beta=1,dimension=2),F(1,100))

    def test_dimension_safe_conversion(self):
        a=F(1,1000); L=3; d=50
        rho=q.policy_relative_allowance(gram_allowance=a,dimension=d,target_upper=L)
        self.assertLessEqual(F(d)*L**2*rho**2,a**2)

    def test_negative_arguments(self):
        for values in [dict(initial=-1,tolerance=1),dict(initial=0,tolerance=0),
                       dict(initial=0,tolerance=1,factor_error=-1),dict(initial=0,tolerance=1,radius=1)]:
            with self.assertRaises(ValueError): q.plan(**values)

if __name__=='__main__': unittest.main()
