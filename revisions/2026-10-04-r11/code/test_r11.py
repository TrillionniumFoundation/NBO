"""Adversarial mathematical, arithmetic, and gradient-routing regression tests."""
import copy,json,math,unittest
import numpy as np
import torch
from scipy.integrate import quad
from bellman_study import R,P,CHI,Actor,Critic,GreedyPolicy,coupling,rollout,first_jet,initial_states
from policy_certificate import I,weights,midpoint,safe_tanh,safe_log,constants,empirical_lower,mean_i,sqrt_nonnegative

class R11(unittest.TestCase):
    def test_tanh_polynomial(self):
        x=np.r_[np.linspace(-25,25,10001),-1e6,1e6]
        self.assertLess(np.max(abs(safe_tanh(x)-np.tanh(x))),2**-34)
    def test_log_polynomial(self):
        x=np.geomspace(.02,2.,10001)
        self.assertLess(np.max(abs(safe_log(x)-np.log(x))),2**-34)
    def test_log_rejects_domain(self):
        with self.assertRaises(ValueError):safe_log(np.array([0.]))
    def test_log_remainder_budget(self):
        remainder=2*(1/3)**37/(37*(1-1/9))
        self.assertLess(16*remainder,2**-50)
    def test_exp_remainder_budget(self):
        r=20/256.;err=math.exp(r)*r**15/math.factorial(15)
        self.assertLess(512*err*math.exp(r),2**-40)
    def test_schedule_derivative(self):
        t=torch.linspace(0,1,1001).requires_grad_(True)
        from tube_neural import schedule
        m=schedule(t);der=torch.autograd.grad(m.sum(),t)[0]
        self.assertGreaterEqual(float(der.min()),0)
        self.assertLess(float(der.max()),1.)
    def test_tanh_second_derivative(self):
        y=np.linspace(-1,1,10001);self.assertLess(np.max(abs(-2*y*(1-y*y))),1)
    def test_scalar_integrals(self):
        w=weights(8)
        def m(t):
            z=(1-math.exp(-.04*(1-t)))/.04+math.exp(-.04*(1-t))
            return 2/(z+math.sqrt(z*z+.8))
        for k in range(8):
            a,b=k/8,(k+1)/8
            M=quad(m,a,b,epsabs=1e-13)[0]
            self.assertLessEqual(w['M'].lo[k],M);self.assertGreaterEqual(w['M'].hi[k],M)
    def test_bad_grid(self):
        with self.assertRaises(ValueError):weights(10)
    def test_zero_dispersion_subnormal(self):
        r=constants(10,32,.1,np.zeros(10))
        self.assertTrue(np.isfinite(r['bias_upper']));self.assertLess(r['initial_spread_upper'],1e-30)
    def test_refined_transfer_decreases(self):
        a=constants(10,32,.1,np.zeros(10));b=constants(10,64,.1,np.zeros(10))
        self.assertLess(b['bias_upper'],a['bias_upper']*.6)
    def test_refined_bias_has_no_network(self):
        a=constants(10,32,.1,np.zeros(10));torch.manual_seed(999)
        b=constants(10,32,.1,np.zeros(10));self.assertEqual(a['bias_upper'],b['bias_upper'])
    def test_bad_radius(self):
        with self.assertRaises(ValueError):constants(10,32,.7,np.zeros(10))
    def test_statistical_bound_is_policy_specific(self):
        a=empirical_lower(np.full(10000,.02),.1,0,0)
        b=empirical_lower(np.full(10000,-.02),.1,0,0)
        self.assertGreater(a['lower'],b['upper'])
    def test_statistical_clip_count(self):
        r=empirical_lower(np.array([-.2,-.1,0,.1,.2]),.1,.01,.001)
        self.assertEqual(r['clipped_payoffs'],2)
    def test_statistical_reject_nonfinite(self):
        with self.assertRaises(ValueError):empirical_lower(np.array([0,np.nan]),1,0,0)
    def test_family_correction_widens(self):
        x=np.linspace(-.01,.01,1000)
        self.assertLess(empirical_lower(x,.1,0,0,2000)['lower'],empirical_lower(x,.1,0,0,2)['lower'])
    def test_mean_interval(self):
        x=np.array([1e5,-1e5,1e-12]);r=mean_i(I(x))
        self.assertLessEqual(float(r.lo),1e-12/3);self.assertGreaterEqual(float(r.hi),1e-12/3)
    def test_frozen_policy_keeps_state_costate(self):
        torch.manual_seed(2);a=Actor(2)
        for par in a.parameters():par.requires_grad_(False)
        x=torch.tensor([[.2,-.3,.1]]);B=torch.tensor(coupling(2))
        _,p,_=rollout(a,x,B,torch.Generator().manual_seed(21),8,True)
        self.assertTrue(torch.isfinite(p).all());self.assertGreater(float(abs(p).sum()),0)
        self.assertTrue(all(par.grad is None for par in a.parameters()))
    def test_pathwise_costate_finite_difference(self):
        a=Actor(2);B=torch.tensor(coupling(2));x=torch.tensor([[.2,-.3,.1]])
        for par in a.parameters():par.requires_grad_(False)
        _,p,_=rollout(a,x,B,torch.Generator().manual_seed(21),8,True)
        xp=x.clone();xm=x.clone();xp[0,1]+=1e-5;xm[0,1]-=1e-5
        vp,_=rollout(a,xp,B,torch.Generator().manual_seed(21),8)
        vm,_=rollout(a,xm,B,torch.Generator().manual_seed(21),8)
        self.assertAlmostEqual(float(p[0,0]),float((vp-vm)/(2e-5)),places=7)
    def test_actor_gradient_routing(self):
        c=Critic(2);a=Actor(2);x=torch.tensor([[.2,-.3,.1]])
        _,_,_,p=first_jet(c,x);m=a(x);loss=(m*p.detach()).sum();loss.backward()
        self.assertTrue(all(par.grad is None for par in c.parameters()))
        self.assertTrue(any(par.grad is not None for par in a.parameters()))
    def test_hard_terminal(self):
        c=Critic(3);x=torch.tensor([[1.,-.5,.1,.3]]);y=x[:,1:]
        expected=y.mean()-CHI*((y-y.mean())**2).mean()
        self.assertEqual(float(c(x)),float(expected))
    def test_greedy_with_outer_no_grad(self):
        c=Critic(3);a=GreedyPolicy(c,'direct_full',.5,.1);x=torch.zeros(4,4)
        with torch.no_grad():m=a(x)
        self.assertTrue(torch.isfinite(m).all());self.assertFalse(m.requires_grad)
    def test_protocol_no_development_seed(self):
        p=json.loads((R/'PROTOCOL.json').read_text())
        self.assertNotIn(p['development_training_seed'],p['training_seeds'])
        self.assertNotEqual(p['final_noise_seed'],p['development_noise_seed'])
    def test_tail_clipping_variance_bound(self):
        from scipy.stats import norm
        z=10.;bound=2*norm.pdf(z)*(z+1/z)
        actual=2*((1+z*z)*norm.sf(z)-z*norm.pdf(z))
        self.assertGreater(bound,actual);self.assertGreater(actual,0)

if __name__=='__main__':unittest.main(verbosity=2)
