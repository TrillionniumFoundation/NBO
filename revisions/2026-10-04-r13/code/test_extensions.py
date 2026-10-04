"""Tests for independent diagnostics and the finite-observation implementation."""
import tempfile,unittest
from pathlib import Path
from common import *
import sensor,extra_worker
class Extensions(unittest.TestCase):
    def saved(self,folder,d=10):
        torch.manual_seed(6321);a=old.Actor(d,8,.1);c=old.Critic(d,8)
        with torch.no_grad():
            for p in a.parameters():p.uniform_(-.1,.1)
        path=Path(folder)/'actor.pt'
        torch.save(dict(actor=a.state_dict(),critic=c.state_dict(),dimension=d,method='nbo',width=8,epsilon=.1,iteration=1),path)
        return a,path
    def test_protected_actor_shape_and_finiteness(self):
        with tempfile.TemporaryDirectory() as f:
            a,path=self.saved(f);p,_,_=sensor.protected_load(path)
            x=torch.cat([torch.rand(32,1),torch.randn(32,10)],1);y=p(x)
            self.assertEqual(tuple(y.shape),(32,10));self.assertTrue(torch.isfinite(y).all())
    def test_protected_activation_diagnostic(self):
        with tempfile.TemporaryDirectory() as f:
            a,path=self.saved(f);p,_,_=sensor.protected_load(path);acc=sensor.network_account(a,10,.1)
            x=torch.cat([torch.rand(128,1),500*torch.randn(128,10)],1)
            with torch.no_grad():delta=(p(x)-a(x)).abs().max().item()
            self.assertLess(delta,acc['actor_roundoff_rms_upper']*10+2e-10)
    def test_global_network_lipschitz_diagnostic(self):
        with tempfile.TemporaryDirectory() as f:
            a,path=self.saved(f);L=sensor.network_account(a,10,.1)['lipschitz_upper'];x=torch.randn(30,11);x[:,0]=.5;y=x.clone();y[:,1:]+=.001*torch.randn(30,10)
            with torch.no_grad():change=torch.linalg.vector_norm(a(x)-a(y),dim=1);distance=torch.linalg.vector_norm(x[:,1:]-y[:,1:],dim=1)
            self.assertTrue(torch.all(change<=L*distance+1e-12))
    def test_sensor_allowance_includes_arithmetic(self):
        with tempfile.TemporaryDirectory() as f:
            _,path=self.saved(f);r=sensor.allowance(path,32,0.)
            self.assertGreater(r['network']['actor_roundoff_rms_upper'],0.)
            self.assertGreater(r['recurrence_roundoff_per_cell_upper'],0.)
            self.assertGreaterEqual(r['payoff_difference_upper'],0.)
    def test_sensor_noise_monotonicity(self):
        with tempfile.TemporaryDirectory() as f:
            _,path=self.saved(f);a=sensor.allowance(path,32,0.);b=sensor.allowance(path,32,.01)
            self.assertGreaterEqual(b['payoff_difference_upper'],a['payoff_difference_upper'])
            self.assertLessEqual(b['action_error_upper'],.20000000000001)
    def test_nested_rollout_shapes(self):
        torch.manual_seed(1);a=old.Actor(2,8,.1)
        for p in a.parameters():p.requires_grad_(False)
        x=torch.zeros(6,3);z=torch.randn(8,6,3);B=torch.tensor(old.coupling(2))
        value,q=extra_worker.nested_bank(a,x,B,z,4)
        self.assertEqual(value.shape,(6,));self.assertEqual(q.shape,(6,2));self.assertTrue(np.isfinite(q).all())
    def test_cross_bank_mse_identity(self):
        q=1.2;g=.7;values=[(g-(q+a))*(g-(q+b)) for a in [-.4,.4] for b in [-.4,.4]]
        self.assertAlmostEqual(float(np.mean(values)),(g-q)**2)
    def test_cross_bank_estimate_can_be_negative(self):
        self.assertLess((0.-1.)*(0.-(-1.)),0.)
    def test_prespecified_fixed_work(self):
        self.assertEqual(PROTOCOL['fixed_work_budgets'],[80,160]);self.assertEqual(len(PROTOCOL['fixed_work_seeds']),10)
        for n in PROTOCOL['fixed_work_budgets']:self.assertEqual(n%PROTOCOL['checkpoint_every'],0)
    def test_final_banks_separated(self):
        self.assertNotEqual(PROTOCOL['final_noise_seed'],PROTOCOL['development_noise_seed'])
        self.assertNotEqual(PROTOCOL['fixed_work_noise_seed'],PROTOCOL['development_noise_seed'])
    def test_observation_grid_nested_in_diagnostic(self):
        for n in PROTOCOL['observation_cells']:self.assertEqual(PROTOCOL['observation_fine_cells']%n,0)
    def test_protected_clock_rejects_invalid(self):
        for t in [-.1,1.1]:
            with self.assertRaises(ValueError):sensor.center(t)
if __name__=='__main__':unittest.main(verbosity=2)
