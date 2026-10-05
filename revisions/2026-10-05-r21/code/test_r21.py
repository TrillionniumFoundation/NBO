import unittest,math,json
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from policy_accounts import allocate,finite_policy_account
R=Path(__file__).resolve().parents[1]

class CompositionTests(unittest.TestCase):
    def model(self):
        rng=np.random.default_rng(210005)
        r=rng.uniform(-1,1,(4,3,2));p=rng.uniform(0,1,(4,3,2,3));p/=p.sum(-1,keepdims=True)
        return r,p,np.array([.9,.8,.7,.6]),rng.integers(0,2,(4,3)),rng.uniform(-1,1,3)
    def test_uniform_and_state_bounds(self):
        x=finite_policy_account(*self.model());loss=x['optimal_values']-x['policy_values']
        self.assertTrue(np.all(loss>=-1e-14))
        self.assertTrue(np.all(loss<=x['state_envelope']+1e-14))
        self.assertLessEqual(float(loss[0].max()),x['uniform_bound']+1e-14)
    def test_sharp_single_state(self):
        r=np.array([[[0,1]],[[0,2]],[[0,3]]],float);p=np.ones((3,1,2,1))
        b=[.5,.25,.8];x=finite_policy_account(r,p,b,np.zeros((3,1),int),[0])
        exact=F(1)+F(1,2)*2+F(1,2)*F(1,4)*3
        self.assertEqual(x['uniform_bound'],float(exact))
        self.assertEqual(x['optimal_values'][0,0]-x['policy_values'][0,0],float(exact))
    def test_zero_discount(self):
        r,p,b,pi,v=self.model();b[0]=0;x=finite_policy_account(r,p,b,pi,v)
        self.assertEqual(x['uniform_bound'],float(x['local_advantages'][0].max()))
    def test_optimal_policy_zero_gap(self):
        r,p,b,pi,v=self.model();x=finite_policy_account(r,p,b,pi,v)
        for t in range(len(b)):
            pi[t]=(r[t]+b[t]*np.einsum('sak,k->sa',p[t],x['optimal_values'][t+1])).argmax(1)
        y=finite_policy_account(r,p,b,pi,v)
        np.testing.assert_allclose(y['local_advantages'],0,atol=1e-14)
    def test_unvisited_state_counterexample(self):
        r=np.zeros((2,2,2));r[1,1,1]=1
        p=np.zeros((2,2,2,2));p[:,:,0,0]=1;p[:,:,1,1]=1
        x=finite_policy_account(r,p,[1,1],np.zeros((2,2),int),[0,0])
        self.assertEqual(x['local_advantages'][0,0],0)
        self.assertEqual(x['local_advantages'][1,0],0)
        self.assertEqual(x['optimal_values'][0,0]-x['policy_values'][0,0],1)
        self.assertEqual(x['state_envelope'][0,0],1)
    def test_constant_shift_invariance(self):
        r,p,b,pi,v=self.model();x=finite_policy_account(r,p,b,pi,v)
        y=finite_policy_account(r+np.arange(4)[:,None,None],p,b,pi,v+5)
        np.testing.assert_allclose(x['local_advantages'],y['local_advantages'],atol=1e-14)
    def test_invalid_kernel(self):
        r,p,b,pi,v=self.model();p[0,0,0,0]+=1
        with self.assertRaises(ValueError):finite_policy_account(r,p,b,pi,v)
    def test_infeasible_policy(self):
        r,p,b,pi,v=self.model();pi[0,0]=10
        with self.assertRaises(ValueError):finite_policy_account(r,p,b,pi,v)

class AllocationTests(unittest.TestCase):
    def args(self):return [1,.9,.4],[2,4,1],[1,3,2],[.01,.02,.01],.2
    def test_constraint_and_objective(self):
        w,A,c,b,target=self.args();z=allocate(w,A,c,b,target);e=np.array(z.allowances)
        self.assertAlmostEqual(np.dot(w,e),z.slack,places=13)
        self.assertAlmostEqual(sum(np.array(A)*c/e**2),z.continuous_cost,places=9)
        self.assertLessEqual(z.integer_cost,z.continuous_cost+sum(c)+1e-9)
    def test_holder_lower_bound(self):
        w,A,c,b,target=self.args();z=allocate(w,A,c,b,target);rng=np.random.default_rng(210006)
        for _ in range(100):
            shares=rng.uniform(.01,1,3);shares/=shares.sum();e=z.slack*shares/np.array(w)
            self.assertGreaterEqual(sum(np.array(A)*c/e**2)+1e-9,z.continuous_cost)
    def test_one_date(self):
        z=allocate([2],[3],[4],[.1],1)
        self.assertAlmostEqual(z.allowances[0],.4)
        self.assertAlmostEqual(z.continuous_cost,75)
    def test_slack_scaling(self):
        z=allocate([1,.5],[2,3],[1,2],[0,0],.2)
        z2=allocate([1,.5],[2,3],[1,2],[0,0],.4)
        self.assertAlmostEqual(z.continuous_cost,4*z2.continuous_cost)
    def test_no_slack(self):
        with self.assertRaises(ValueError):allocate([1],[2],[1],[.5],.1)
    def test_nonpositive_rate(self):
        with self.assertRaises(ValueError):allocate([1],[0],[1],[0],.1)
    def test_nonfinite(self):
        with self.assertRaises(ValueError):allocate([1],[math.inf],[1],[0],.1)
    def test_shape(self):
        with self.assertRaises(ValueError):allocate([1,2],[1],[1],[0],.1)

class PublicationEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.x=json.loads((R/'results/FUTURE_TABLES.json').read_text())
    def test_all_services(self):
        self.assertEqual((self.x['services'],self.x['regime_outcomes']),(168,840))
        self.assertEqual(len(self.x['all_services']),168)
    def test_success_and_failures_retained(self):
        x={s['service']:s for s in self.x['service_summary']}
        self.assertEqual(x['NBO-reuse']['certified_regimes'],72)
        self.assertEqual(x['NBO-adaptive']['certified_regimes'],120)
        self.assertEqual(x['NBO-adaptive']['refreshes'],48)
        self.assertLess(x['NBO-adaptive']['largest_final_mean_regret_bound'],1e-4)
    def test_adaptive_cost_disadvantage_not_hidden(self):
        for x in self.x['work_cells']:
            self.assertGreater(x['costs']['NBO-adaptive'],x['costs']['NBO-refit'])
    def test_positive_economic_conclusion(self):
        self.assertEqual(len(self.x['nbo_economic_contrasts']),4)
        for x in self.x['nbo_economic_contrasts']:
            lo,hi=x['envelope_over_three_NBO_streams'];self.assertLess(lo,hi);self.assertLess(hi,0)
    def test_total_work_not_selected_work(self):
        self.assertGreater(self.x['original_full_comparative_seconds'],self.x['sum_accounted_service_seconds']+self.x['sum_post_stop_diagnostic_seconds'])
    def test_risks_separated(self):
        row=next(x for x in self.x['risk_rows'] if x['dimension']==50 and x['service']=='NBO-reuse' and x['future']=='future_withdrawal_low')
        self.assertGreater(row['absolute_risk'],.07)
        self.assertLess(row['centered_risk'],1e-7)
        self.assertLess(row['three_action_loss'],1e-6)
if __name__=='__main__':unittest.main()
