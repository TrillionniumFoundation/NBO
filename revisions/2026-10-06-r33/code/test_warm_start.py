from fractions import Fraction as F
import unittest
import warm_start as w


class WarmStartTests(unittest.TestCase):
    def setUp(self):
        self.target = w.matrix([[1, F(2,25)], [F(2,25), F(25,16)]])
        self.factor = w.matrix([[1, F(1,20)], [0, F(5,4)]])
        self.base = dict(m=F(3,4), upper=2, radius=F(1,3), alpha=F(1,6),
                         tolerance=F(1,4096), max_updates=1000)

    def run_trace(self, factor, bits=24):
        e0 = w.gate(factor, self.target, m=self.base['m'], upper=2, radius=F(1,3))
        nu = w.sqrt_up(F(len(factor)*len(factor[0])))/(2*(1<<bits))
        plan = w.plan(**self.base, initial=e0, factor_error=nu)
        bound = e0
        for _ in range(plan['updates']):
            factor, actual_nu = w.quantized_step(factor, self.target, self.base['alpha'], bits=bits)
            self.assertLessEqual(actual_nu, nu)
            bound = plan['q']*bound+plan['noise']
            self.assertLessEqual(w.norm2(w.add(w.mm(w.transpose(factor), factor), self.target, -1)), bound**2)
            self.assertLessEqual(bound, self.base['radius'])
        self.assertLessEqual(bound, self.base['tolerance'])
        return factor, plan

    def test_noncommuting_square_trace(self):
        h = w.mm(w.transpose(self.factor), self.factor)
        self.assertNotEqual(w.mm(h, self.target), w.mm(self.target, h))
        self.run_trace(self.factor)

    def test_rectangular_trace(self):
        self.run_trace(self.factor+[[F(1,128), F(-1,128)]])

    def test_rotated_factor_trace(self):
        rotation = w.matrix([[F(3,5),F(-4,5)],[F(4,5),F(3,5)]])
        self.run_trace(w.mm(rotation,self.factor))

    def test_above_and_below_target(self):
        self.run_trace(w.matrix([[F(101,100),0],[F(1,64),F(123,100)]]))

    def test_exact_gram_identity(self):
        h = w.mm(w.transpose(self.factor),self.factor)
        e = w.add(h,self.target,-1); alpha=self.base['alpha']
        rhs=w.add(w.add(e,w.add(w.mm(e,h),w.mm(h,e)),-alpha),w.mm(w.mm(e,h),e),alpha**2)
        out=w.ideal_step(self.factor,self.target,alpha)
        self.assertEqual(w.add(w.mm(w.transpose(out),out),self.target,-1),rhs)

    def test_exact_one_step_contraction(self):
        out=w.ideal_step(self.factor,self.target,self.base['alpha'])
        old=w.norm2(w.add(w.mm(w.transpose(self.factor),self.factor),self.target,-1))
        new=w.norm2(w.add(w.mm(w.transpose(out),out),self.target,-1))
        q=1-F(3,4)*self.base['alpha']*self.base['m']
        self.assertLessEqual(new,q*q*old)

    def test_cap_is_minimal_for_scalar_envelope(self):
        p=w.plan(**self.base,initial=F(1,10),factor_error=F(1,1<<26))
        k=p['updates']; previous=p['floor']+p['q']**(k-1)*(p['initial']-p['floor'])
        self.assertGreater(previous,p['tolerance'])
        self.assertLessEqual(p['bound'],p['tolerance'])

    def test_zero_update_acceptance(self):
        p=w.plan(**self.base,initial=F(1,8192))
        self.assertEqual(p['updates'],0)

    def test_zero_initial_with_noise(self):
        p=w.plan(**self.base,initial=0,factor_error=F(1,1<<30))
        self.assertEqual(p['updates'],0)

    def test_basin_boundary_allowed(self):
        p=w.plan(**self.base,initial=F(1,3))
        self.assertLessEqual(p['bound'],self.base['tolerance'])

    def test_bad_basin_rejected(self):
        with self.assertRaises(ValueError): w.plan(**self.base,initial=F(1,2))
        with self.assertRaises(ValueError): w.gate([[0,0],[0,0]],self.target,m=F(3,4),upper=2,radius=F(1,3))

    def test_bad_steps_rejected(self):
        for alpha in (0,-1,F(1,2)):
            opts=dict(self.base,alpha=alpha)
            with self.assertRaises(ValueError): w.plan(**opts,initial=F(1,10))

    def test_bad_spectrum_rejected(self):
        with self.assertRaises(ValueError): w.gate(self.factor,self.target,m=F(3,2),upper=2,radius=F(1,3))
        with self.assertRaises(ValueError): w.gate(self.factor,self.target,m=F(3,4),upper=1,radius=F(1,3))

    def test_noise_floor_rejected(self):
        with self.assertRaises(ValueError): w.plan(**self.base,initial=F(1,10),factor_error=F(1,1024))

    def test_noise_destabilization_rejected(self):
        with self.assertRaises(ValueError): w.plan(**self.base,initial=F(1,10),factor_error=1)

    def test_finite_resource_limit_fails_closed(self):
        with self.assertRaises(ArithmeticError): w.plan(**dict(self.base,max_updates=1),initial=F(1,10))

    def test_transport_gate(self):
        self.assertEqual(w.transport_gate(F(1,20),F(1,10),F(1,3)),F(3,20))
        for old,drift in ((F(1,4),F(1,4)),(-1,0),(0,-1)):
            with self.assertRaises(ValueError): w.transport_gate(old,drift,F(1,3))

    def test_outward_square_roots(self):
        for value in (F(0),F(1),F(2),F(1,3),F(1234567,987654321)):
            upper=w.sqrt_up(value)
            self.assertGreaterEqual(upper**2,value)
            self.assertLess((upper-F(1,1<<96))**2,value if value else F(1))

    def test_target_error_uses_frobenius_channel(self):
        ans=w.policy_residual_upper(actor_error=F(1,100),beta=F(24,25),b_norm=F(1,5),f_frobenius=7,
            dimension=50,gram_error=F(1,1000),target_spectral_radius=F(1,2000))
        expected=F(1,100)+F(24,25)*F(1,5)*7*F(3,2000)/50
        self.assertEqual(ans,expected)

    def test_bad_shapes_and_values(self):
        for factor in ([[1,0]], [[1,0],[0]], [[float('nan'),0],[0,1]]):
            with self.assertRaises(ValueError): w.gate(factor,self.target,m=F(3,4),upper=2,radius=F(1,3))
        with self.assertRaises(ValueError): w.rational(True)
        with self.assertRaises(ValueError): w.quantized_step(self.factor,self.target,F(1,6),bits=0)

    def test_non_symmetric_target_rejected(self):
        with self.assertRaises(ValueError): w.gate(self.factor,[[1,F(1,10)],[0,F(25,16)]],m=F(3,4),upper=2,radius=F(1,3))

    def test_exact_storage_error_contract(self):
        u=w.ideal_step(self.factor,self.target,F(1,6))
        for bits in (8,16,24):
            out,nu=w.quantized_step(self.factor,self.target,F(1,6),bits=bits)
            self.assertLessEqual(w.norm2(w.add(out,u,-1)),nu**2)

if __name__=='__main__': unittest.main()
