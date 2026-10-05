"""Independent small-case checks; primary cases never serve as development data."""
import inspect, math, unittest
from fractions import Fraction as F
import numpy as np
from constructive import budget, dyadic_scale, train_factor, backward_nbo
from experiment import economy, evaluate, riccati
from policy_certificate import certify


class IsotropicLearning(unittest.TestCase):
    def test_01_exact_scalar_invariant(self):
        for lam in (F(1),F(7,3),F(4)):
            r=F(1,16); c=r; alpha=F(1,16); rho=1-2*alpha*c
            for _ in range(4):
                nxt=r*(1+alpha*(lam-r))**2
                self.assertLessEqual(r,nxt);self.assertLessEqual(nxt,lam)
                self.assertLessEqual(lam-nxt,rho*(lam-r));r=nxt

    def test_02_nondiagonal_gram_rate(self):
        M=np.array([[3.,.75],[.75,2.]])
        c=.0625; W=math.sqrt(c)*np.eye(2);alpha=1/16
        e0=np.linalg.norm(W.T@W-M);rho=1-2*alpha*c
        for j in range(100):
            C=W.T@W
            self.assertLessEqual(np.linalg.norm(C-M),rho**j*e0+1e-12)
            self.assertGreaterEqual(np.linalg.eigvalsh(C)[0],c-1e-12)
            self.assertGreaterEqual(np.linalg.eigvalsh(M-C)[0],-1e-12)
            W-=alpha*W@(C-M)

    def test_03_rectangular_factor(self):
        M=np.array([[2.,.25],[.25,1.]])
        W=np.vstack((.25*np.eye(2),np.zeros((2,2))))
        e0=np.linalg.norm(W.T@W-M)
        for j in range(80):W-=.05*W@(W.T@W-M)
        self.assertLess(np.linalg.norm(W.T@W-M),e0*(1-.1*.0625)**80)

    def test_04_far_from_old_basin(self):
        W,r=train_factor(np.diag([4.,2.]),1.,1e-7,.25)
        self.assertTrue(r['outside_previous_rank_basin'])
        self.assertTrue(r['training_threshold_met'])
        self.assertLessEqual(r['iterations'],r['ideal_iteration_cap'])

    def test_05_orientation_equivariance(self):
        M=np.array([[3.,.4],[.4,2.]])
        W,_=train_factor(M,1.,1e-7,.5,17)
        V,_=train_factor(M,1.,1e-7,.5,29)
        np.testing.assert_allclose(W.T@W,V.T@V,atol=1e-12,rtol=1e-12)

    def test_06_exact_fixed_point(self):
        M=np.eye(2)/4;W=np.eye(2)/2
        for _ in range(4):W-=.1*W@(W.T@W-M)
        np.testing.assert_array_equal(W,np.eye(2)/2)

    def test_07_singular_orientation_is_not_isotropic(self):
        M=np.eye(2);W=np.diag([.5,0.])
        for _ in range(20):W-=.1*W@(W.T@W-M)
        self.assertEqual(W[1,1],0.)
        self.assertGreaterEqual(np.linalg.norm(W.T@W-M),1.)

    def test_08_unsafe_step_can_overshoot(self):
        lam=F(1);r=F(1,4);alpha=F(4)
        self.assertGreater(r*(1+alpha*(lam-r))**2,lam)

    def test_09_budget_inequality(self):
        for e0 in (.01,1.,100.):
          for target in (1e-5,.01):
            n=budget(e0,target,.01,.1)
            self.assertLessEqual((1-.002)**n*e0,target*(1+1e-12))

    def test_10_zero_budget(self):self.assertEqual(budget(0.,1e-5,.1,.1),0)
    def test_11_invalid_budget(self):
        for x in ((-1,1,.1,.1),(1,0,.1,.1),(1,1,-.1,.1),(1,1,.1,0),(1,1,float('nan'),1)):
            with self.assertRaises(ValueError):budget(*x)
    def test_12_dyadic_coercivity(self):
        for m in (.01,.3,1.,2.,10.):
          for a in (.25,.5):self.assertTrue(0<dyadic_scale(m,a)**2<=m)
    def test_13_invalid_scale(self):
        with self.assertRaises(ValueError):dyadic_scale(1.,.9)
    def test_14_invalid_target(self):
        with self.assertRaises(ValueError):train_factor([[1,2],[0,1]],1,1e-4)
    def test_15_scalar_small_coercivity(self):
        _,r=train_factor(np.array([[.01]]),.01,1e-8)
        self.assertTrue(r['training_threshold_met'])


class BackwardConstruction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=economy(3,'anchor',4)
        cls.K,cls.W,cls.P,cls.count=backward_nbo(cls.model,1e-4,.5,17)
    def test_16_own_future_identity(self):
        expected,_=evaluate(self.model,self.K)
        np.testing.assert_allclose(self.P,expected,rtol=1e-13,atol=1e-13)
    def test_17_all_state_certificate(self):
        self.assertLessEqual(certify(self.model,self.K)['policy_gap_upper'],1e-4)
    def test_18_unrestricted_class(self):
        result=certify(self.model,self.K)
        self.assertEqual(result['class_gap'],0.)
        self.assertEqual(result['value_transfer_gap'],0.)
    def test_19_training_dates(self):
        self.assertEqual([x['date'] for x in self.count['dates']],[2,1,0])
        self.assertTrue(self.count['training_thresholds_met'])
    def test_20_finite_update_cap(self):
        self.assertLessEqual(self.count['hidden_updates'],self.count['ideal_hidden_update_cap'])
        self.assertEqual(self.count['actor_solves'],4)
    def test_21_neural_actor_uses_its_factor(self):
        m=self.model
        for t in range(3):
            phat=self.W[t+1].T@self.W[t+1]/3
            H=m['R'][t]+m['beta']*m['B'][t].T@phat@m['B'][t]
            rhs=m['beta']*m['B'][t].T@phat@m['A'][t]
            self.assertLess(np.linalg.norm(H@self.K[t]-rhs),1e-13)
    def test_22_terminal_actor_exact(self):
        np.testing.assert_allclose(self.K[-1],riccati(self.model)[-1],rtol=1e-14,atol=1e-14)
    def test_23_bound_dominates_independent_optimal_gap(self):
        opt=riccati(self.model);po,co=evaluate(self.model,opt);pk,ck=evaluate(self.model,self.K)
        x=np.array([.1,-.2,.3]);gap=x@(pk[0]-po[0])@x+ck[0]-co[0]
        self.assertGreaterEqual(gap,-1e-12)
        self.assertLessEqual(gap,certify(self.model,self.K)['policy_gap_upper'])
    def test_24_no_optimal_oracle_in_constructor(self):
        source=inspect.getsource(backward_nbo)
        self.assertNotIn('riccati(',source)
        self.assertNotIn('eigh(',source)
        self.assertNotIn('svd(',source)
    def test_25_changed_future_reoptimized(self):
        model=economy(3,'valuation',4)
        model['Q'][2:]*=1.3
        K,*_=backward_nbo(model,1e-4,.5,17)
        self.assertGreater(np.linalg.norm(K[2]-self.K[2]),1e-4)
    def test_26_no_action_channel(self):
        m=economy(2,'anchor',3);m['B'][:]=0
        K,*_=backward_nbo(m,1e-4,.5,17)
        np.testing.assert_array_equal(K,np.zeros_like(K))
        self.assertLess(certify(m,K)['policy_gap_upper'],1e-4)
    def test_27_larger_execution_error_charged(self):
        a=certify(self.model,self.K,0.)['policy_gap_upper']
        b=certify(self.model,self.K,1e-7)['policy_gap_upper']
        self.assertGreater(b,a)
    def test_28_bad_policy_rejected(self):
        bad=self.K.copy();bad[0]+=3*np.eye(3)
        self.assertGreater(certify(self.model,bad)['policy_gap_upper'],1e-4)
    def test_29_explicit_reference_not_optimal(self):
        self.assertGreater(self.count['reference_value_upper'],0)
        self.assertEqual(self.count['reference_policy_matrix_updates'],4)
    def test_30_second_scale(self):
        K,W,P,c=backward_nbo(economy(2,'anchor',3),1e-4,.25,17)
        self.assertTrue(c['training_thresholds_met'])
        self.assertLessEqual(certify(economy(2,'anchor',3),K)['policy_gap_upper'],1e-4)

if __name__=='__main__':unittest.main()
