"""Independent algebra, arithmetic and deployment regression tests."""
import hashlib,sys,unittest
from pathlib import Path
import numpy as np
import mpmath as mp
import torch
from tube_certificate import *
import tube_neural as n

class Checks(unittest.TestCase):
    def test_log_curvature(self):
        for a in [.49,.6,.85]:
            m=np.r_[np.linspace(.02,a-1e-4,300),np.linspace(a+1e-4,2.,300)]
            mu=2*(np.log(a/2)+(2-a)/a)/(2-a)**2
            residual=np.log(m/a)-(m-a)/a+mu*(m-a)**2/2
            self.assertLessEqual(residual.max(),2e-14)
    def test_local_curvature(self):
        rng=np.random.default_rng(819);a=.49+.36*rng.random(10000);delta=.1*(2*rng.random(10000)-1)
        remainder=delta/a-np.log1p(delta/a)
        self.assertTrue(np.all(remainder<=delta**2/(2*(a-.1)**2)+1e-15))
    def test_interval_transcendentals(self):
        mp.mp.dps=90
        for x in np.linspace(-3,3,101):
            z=exp_i(I(x));v=mp.exp(mp.mpf(float(x)))
            self.assertLessEqual(mp.mpf(float(z.lo)),v);self.assertLessEqual(v,mp.mpf(float(z.hi)))
        for x in np.linspace(.02,3,101):
            z=log_i(I(x));v=mp.log(mp.mpf(float(x)))
            self.assertLessEqual(mp.mpf(float(z.lo)),v);self.assertLessEqual(v,mp.mpf(float(z.hi)))
    def test_sqrt(self):
        for x in [0.,1e-12,.2,1.,8.]:
            z=sqrt_i(I(x));self.assertLessEqual(mp.mpf(float(z.lo))**2,mp.mpf(x));self.assertGreaterEqual(mp.mpf(float(z.hi))**2,mp.mpf(x))
    def test_exponential_integral(self):
        mp.mp.dps=90
        for a in [-.04,0.,.2]:
            z=exponential_integral(I(a),I(1.));v=1 if a==0 else mp.expm1(mp.mpf(a))/mp.mpf(a)
            self.assertLessEqual(mp.mpf(float(z.lo)),v);self.assertLessEqual(v,mp.mpf(float(z.hi)))
    def test_verified_spectrum(self):
        for d in [2,10,20,50]:
            B=coupling(d);s=spectral_bound(B)
            self.assertTrue(s['attempts'][-1]['positive_pivots'])
            self.assertLess(float(np.linalg.eigvalsh(B.T@B)[-1]),s['lambda_upper'])
            self.assertTrue(all(p[0]>0 for p in s['attempts'][-1]['pivots']))
    def test_matrix_binding(self):
        B=coupling(2);s=spectral_bound(B);B[0,0]+=.01
        with self.assertRaises(ValueError):enclosure(B,spectral=s)
    def test_invalid_tube(self):
        with self.assertRaises(ValueError):enclosure(coupling(2),eps=.5,panels=64)
    def test_monotonic_allowances(self):
        B=coupling(10);a=enclosure(B,0,0,1024);b=enclosure(B,.1,0,1024);c=enclosure(B,.1,.5,1024)
        self.assertLess(a['regret_upper'],b['regret_upper']);self.assertLess(b['regret_upper'],c['regret_upper'])
    def test_tube_and_terminal(self):
        torch.manual_seed(47);a=n.Actor(10);v=n.Critic(10)
        for p in a.parameters():p.data.uniform_(-3,3)
        x=torch.cat([torch.linspace(0,1,100)[:,None],torch.randn(100,10)*1e6],1)
        self.assertLessEqual(float((a(x)-n.schedule(x[:,:1])).abs().max()),.10000000000001)
        x[:,0]=1;self.assertTrue(torch.equal(v(x),n.terminal(x[:,1:])))
    def test_no_actor_gradient_from_evaluation(self):
        v=n.Critic(2);a=n.Actor(2);x=n.draw_states(torch.Generator().manual_seed(4),2,8)
        xx,y,vt,p=n.first_jet(v,x)
        with torch.no_grad():m=a(xx)
        r=-vt-n.flow(xx[:,1:],m)-(n.drift(xx[:,1:],m,torch.tensor(coupling(2)))*p).sum(1,keepdim=True)+P['discount']*y
        r.square().mean().backward();self.assertTrue(all(z.grad is None for z in a.parameters()))
    def test_no_critic_gradient_from_improvement(self):
        v=n.Critic(2);a=n.Actor(2);x=n.draw_states(torch.Generator().manual_seed(4),2,8)
        _,_,_,p=n.first_jet(v,x);m=a(x)
        loss=-(n.flow(x[:,1:],m)+(n.drift(x[:,1:],m,torch.tensor(coupling(2)))*p.detach()).sum(1,keepdim=True)).mean()
        loss.backward();self.assertTrue(all(z.grad is None for z in v.parameters()))
    def test_schedule_optimality(self):
        t=torch.linspace(0,1,101)[:,None];m=n.schedule(t);e=torch.exp(-P['discount']*(1-t));w=(1-e)/P['discount']+e
        self.assertLess(float((1/m-w-P['adjustment']*m).abs().max()),1e-13)
    def test_greedy_feasibility(self):
        p=torch.randn(300,10);t=torch.rand(300,1);m=n.greedy(p,t,.1)
        self.assertLessEqual(float((m-n.schedule(t)).abs().max()),.10000000000001)
    def test_inward_deployment_guard(self):
        from paired import tube_guard
        clock=torch.linspace(0,1,101)[:,None]
        proposal=torch.randn(101,10)*1e4;proposal[0,0]=float('nan')
        guarded=tube_guard(proposal,clock).numpy()
        center=schedule_i(I(clock.numpy()))
        self.assertTrue(np.all(guarded>=center.hi-.1))
        self.assertTrue(np.all(guarded<=center.lo+.1))
    def test_original_model_identity(self):
        import coupled_diffusion as old
        self.assertEqual(P,old.P)
        for d in [10,20,50]:
            B=torch.tensor(coupling(d));self.assertTrue(torch.equal(B,old.coupling(d)))
            y=torch.randn(20,d);m=.02+1.98*torch.rand(20,d)
            self.assertTrue(torch.equal(n.flow(y,m),old.flow(y,m)))
            self.assertTrue(torch.equal(n.drift(y,m,B),old.drift(y,m,B)))
            self.assertTrue(torch.equal(n.terminal(y),old.terminal(y)))

    def test_printed_upper_endpoints(self):
        from decimal import Decimal
        from report import upper_decimal
        for value in [.0574292151442084,.0672437436158303,.070080174736732,.0805315402447]:
            for places in [2,5,6]:
                self.assertGreaterEqual(Decimal(upper_decimal(value,places)),Decimal.from_float(value))
    def test_paired_aggregation_metadata(self):
        from report import paired_average
        result=paired_average(10,'anchor',np.array([[1.,2.,3.],[0.,1.,2.],[2.,3.,4.]]))
        self.assertEqual(result['dimension'],10);self.assertEqual(result['mean'],2.)
        self.assertIn('not a seed-population interval',result['interpretation'])

if __name__=='__main__':unittest.main(verbosity=2)
