"""Mathematical and numerical regression tests; not economic observations."""
import itertools,unittest,math
from fractions import Fraction as F
import numpy as np
import readout69 as r
import center69 as center
import independent69 as independent
import vector69 as vector
import core62 as c
q=r.q;I=r.I;B=r.B

class RevisionTests(unittest.TestCase):
    def test_hat_partition_exact(self):
        for d in (2,8):
            for x in (0.,.125,.25,.5,.875,1.):
                f=r.exact_phi([x]*d,'hat-relu');self.assertEqual(sum(f),1);self.assertGreaterEqual(min(f),0)
    def test_bernstein_partition_exact(self):
        for d in (2,8):
            f=r.exact_phi([F(j+1,d+2) for j in range(d)],'bernstein4')
            self.assertEqual(sum(f),1);self.assertGreaterEqual(min(f),0);self.assertEqual(len(f),5*d)
    def test_feature_budgets_match(self):
        x=np.array([[.1,.7],[.2,.8]])
        self.assertEqual(r.phi(x,'hat-relu').shape,r.phi(x,'bernstein4').shape)
    def test_numeric_features_match_exact(self):
        x=np.array([[.125,.625],[.5,.875]])
        for kind in ('hat-relu','bernstein4'):
            for row,actual in zip(x,r.phi(x,kind)):
                np.testing.assert_allclose(actual,[float(v) for v in r.exact_phi(row,kind)],atol=1e-14,rtol=0)
    def test_original_scalar_terminal_integration(self):
        for row in ([F(1,8),F(7,8)],[F(3,16)]*8,[F(1,2)]*2):
            for act in (F(0),F(1,16),F(1,8)):
                exact=independent.terminal_q(row,[act])
                val=q.n.o.final_q(I.point(np.array([list(map(float,row))])),I.point(np.array([float(act)])),1)
                self.assertLessEqual(F(float(val.lo[0])),exact);self.assertGreaterEqual(F(float(val.hi[0])),exact)
    def test_original_vector_terminal_integration(self):
        from vector_base69 import terminal_value_grad
        for d in (2,8):
            x=[F(j+1,d+2) for j in range(d)]
            for a in ([F(0),F(0)],[F(1,16),F(1,16)],[F(1,8),F(0)]):
                val,_=terminal_value_grad(np.array([list(map(float,x))]),np.array([list(map(float,a))]))
                # Exact original values use the represented floating inputs.
                exact=independent.terminal_q(list(map(lambda z:F(float(z)),x)),a)
                self.assertLessEqual(F(float(val.lo[0])),exact);self.assertGreaterEqual(F(float(val.hi[0])),exact)
    def test_independent_state_primitives(self):
        for d in (2,8):
            x=[F(3,16)]*d;a=[F(1,16),F(1,32)];z=F(1,128);w=F(-1,256)
            y=independent.transition(x,a,z,w);got=c.transition(I.point(np.array([list(map(float,x))])),I.point(np.array([list(map(float,a))])),float(z),float(w))
            for exact,l,u in zip(y,got.lo[0],got.hi[0]):self.assertLessEqual(F(float(l)),exact);self.assertGreaterEqual(F(float(u)),exact)
    def test_independent_stage(self):
        x=[F(3,16),F(7,16)];a=[F(1,16),F(1,32)]
        got=c.stage(I.point(np.array([list(map(float,x))])),I.point(np.array([list(map(float,a))])))
        exact=independent.stage(x,a);self.assertLessEqual(F(float(got.lo[0])),exact);self.assertGreaterEqual(F(float(got.hi[0])),exact)
    def test_independent_two_date_bellman_overlap(self):
        x=[F(1,4),F(3,4)];lo,hi=independent.uniform_value(x,2,F(1,16))
        got=r.Oracle('adaptive').solve(np.array([list(map(float,x))]),2,1/64)
        self.assertLessEqual(lo,F(float(got['upper'][0])));self.assertGreaterEqual(hi,F(float(got['lower'][0])))
    def test_centered_identity_exact_finite_model(self):
        # Two states, two actions; enumerate each trajectory exactly.
        T=3;P=[[[F(3,4),F(1,4)],[F(1,4),F(3,4)]],[[F(1,2),F(1,2)],[F(1,8),F(7,8)]]]
        costs=[[F(1,4),F(1,2)],[F(3,4),F(1,8)]];g=[F(1,3),F(2,3)]
        V=[None]*T+[g]
        for t in reversed(range(T)):
            V[t]=[min(costs[x][a]+B*sum(P[x][a][y]*V[t+1][y] for y in range(2)) for a in range(2)) for x in range(2)]
        for policy in (0,1):
            cash=loss=F(0)
            for path in itertools.product(range(2),repeat=T+1):
                prob=F(1,2)
                for t in range(T):prob*=P[path[t]][policy][path[t+1]]
                realized=sum(B**t*costs[path[t]][policy] for t in range(T))+B**T*g[path[T]]
                centered=sum(B**t*(costs[path[t]][policy]+B*sum(P[path[t]][policy][y]*V[t+1][y] for y in range(2))-V[t][path[t]]) for t in range(T))
                cash+=prob*realized;loss+=prob*centered
            self.assertEqual(cash-sum(V[0])/2,loss)
    def test_centered_is_not_pathwise_cash_difference(self):
        # Zero-action one-step example with random terminal cost.
        terminal=[F(0),F(1)];V=F(1,2)
        advantage=V-V
        self.assertEqual(advantage,0);self.assertNotEqual(terminal[0]-V,advantage)
    def test_local_bounds_within_original_contract(self):
        for d,T,target in ((2,2,'1/128'),(8,3,'1/64')):
            tol=r.old.budget(T,target)[0];e=center.local_bounds(T,d,tol)
            self.assertLessEqual(sum(B**t*z for t,z in enumerate(e)),F(target))
    def test_endpoint_confidence_width_decomposition(self):
        lo=np.full(64,-.001);hi=np.full(64,.002)
        got=center.bounded_interval(lo,hi,F(-1,8),F(1,8))
        self.assertGreaterEqual(got['mean_numerical_width'],.003-1e-15)
        self.assertLessEqual(got['interval'][1]-got['interval'][0],got['mean_numerical_width']+2*got['sampling_radius']+1e-14)
    def test_negative_support_rounds_outward(self):
        bound=F(1,10);v=center.bounded_interval(np.array([-.1,-.1]),np.array([.1,.1]),-bound,bound)
        self.assertLessEqual(F(v['interval'][0]),-bound);self.assertGreaterEqual(F(v['interval'][1]),bound)
    def test_certified_readout_is_executed(self):
        for kind in ('hat-relu','bernstein4'):
            models,report,raw=r.fit(2,2,'1/128',6901,kind,train_n=8)
            certificate=report['dates'][0]['exact_certificate']
            self.assertTrue(certificate['feature_partition_verified']);self.assertGreaterEqual(F(certificate['dual_gap_exact']),0)
            a=r.Oracle(kind,models).solve(np.array([[.2,.7],[.5,.5]]),2,1/128)
            self.assertTrue(np.all(a['gap']<=1/128));self.assertTrue(np.all(a['action']<=q.cap_interval(np.array([[.2,.7],[.5,.5]])).lo))
    def test_independent_validation_work_domination(self):
        models,_,_=r.fit(2,2,'1/128',6901,'hat-relu',train_n=8)
        reports,raw=r.validate(2,2,'1/128','hat-relu',models,6901,n=8)
        self.assertTrue(np.all(raw['r2_additional_root_queries']<=reports[0]['K']*raw['r2_loss']))
    def test_centered_continuous_paths_and_aliasing(self):
        randoms,initial=r.old.workload(2,2,4,692001,continuous=True)
        arrays,report=center.trajectories(r.Oracle('adaptive'),initial,randoms,2,'1/128',1/1024)
        self.assertFalse(np.shares_memory(arrays['center_lo'],arrays['center_hi']))
        self.assertTrue(np.all(arrays['center_lo']<=arrays['center_hi']))
        audit=independent.audit_paths(randoms,arrays,2)
        self.assertEqual(audit['complete_midbin_paths_checked'],4)
    def test_vector_optional_witness_and_uniform_splits(self):
        states=np.array([[.25,.75],[.5,.5]])
        for kind in ('simplicial','uniform','hat-vector'):
            models={2:[[.25,.25]]*10} if kind=='hat-vector' else None
            value=vector.Oracle(kind,models).solve(states,2,1/16)
            self.assertTrue(np.all(value['gap']<=1/16));self.assertTrue(np.all(value['action'].sum(axis=1)<=q.cap_interval(states).lo))
    def test_projected_two_control_feasibility(self):
        a=vector.project(np.array([[.7,-.1],[.5,.5],[.1,.1]]),np.array([.2,.2,.2]))
        self.assertTrue(np.all(a>=0));self.assertTrue(np.all(a.sum(axis=1)<=.2))
    def test_empty_enclosure_is_not_a_certificate(self):
        with self.assertRaises(ValueError):center.bounded_interval(np.array([1.,1.]),np.array([0.,0.]),F(0),F(1))

if __name__=='__main__':unittest.main(verbosity=2)
