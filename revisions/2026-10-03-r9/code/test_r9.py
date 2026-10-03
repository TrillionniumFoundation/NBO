"""Checks inclusion and faithful reporting, not guaranteed economic success."""
from __future__ import annotations
import hashlib,json,sys,unittest
from pathlib import Path
import numpy as np
import torch
from action_cover import ROOT,R8,OUT,SignedEncloser,CornerEncloser,I,Model,LO,HI,maximize
from global_benchmark import sqrt_i,relaxation,schedule
from audit import full_domain,payoff_envelope

class R9Tests(unittest.TestCase):
    def test_01_derivatives_include_autodiff(self):
        m=Model(7,9,5);r=np.random.default_rng(819);v=m.g+.01*r.normal(size=m.N);rows=np.arange(m.N)
        mid=LO+(HI-LO)*r.uniform(.05,.95,(m.N,3));lo=np.maximum(LO,mid-.015*(HI-LO));hi=np.minimum(HI,mid+.015*(HI-LO));en=SignedEncloser(m,v);g,regular=en.gradient(rows,lo,hi)
        for _ in range(6):
            aa=torch.tensor(lo+(hi-lo)*r.random(lo.shape),requires_grad=True);q=m.qvalue(torch.tensor(v),aa,False);d=torch.autograd.grad(q.sum(),aa)[0].detach().numpy();mask=regular&~m.boundary
            self.assertTrue(np.all(d[mask]>=g.lo[mask]-1e-9));self.assertTrue(np.all(d[mask]<=g.hi[mask]+1e-9))
    def test_02_signed_bounds_include_points(self):
        m=Model(7,9,5);r=np.random.default_rng(188);v=m.g+.01*r.normal(size=m.N);lo=np.tile(LO,(m.N,1));hi=np.tile(HI,(m.N,1));e=SignedEncloser(m,v);upper,*_=e.bounded(np.arange(m.N),lo,hi)
        for _ in range(9):
            a=lo+(hi-lo)*r.random(lo.shape);q=e.q(np.arange(m.N),a);self.assertTrue(np.all(q.lo<=upper+1e-11))
    def test_03_stopping_crossings_disable_derivative_bound(self):
        m=Model(17,25,20);e=SignedEncloser(m,m.g);lo=np.tile(LO,(m.N,1));hi=np.tile(HI,(m.N,1));_,regular=e.gradient(np.arange(m.N),lo,hi)
        self.assertTrue(np.any(~regular));self.assertTrue(np.any(regular&~m.boundary))
    def test_04_budget_never_means_success(self):
        m=Model(7,9,5);pi=np.tile((LO+HI)/2,(m.N,1));u,p,s=maximize(m,m.g,pi,max_boxes=1,max_depth=0)
        self.assertTrue(s['budget_exhausted']);self.assertGreater(s['unresolved_leaves'],0)
        for a in [LO,HI,(LO+HI)/2]:
            q=CornerEncloser(m,m.g).q(np.arange(m.N),np.tile(a,(m.N,1)));self.assertTrue(np.all(q.lo<=u+1e-11))
    def test_05_verified_face_reduction_is_exercised(self):
        m=Model(7,9,5);pi=np.tile((LO+HI)/2,(m.N,1));_,p,s=maximize(m,m.g,pi,max_boxes=20000,max_depth=8)
        self.assertGreater(s['verified_face_reductions'],0);self.assertTrue(np.all(p>=LO));self.assertTrue(np.all(p<=HI))
    def test_06_interval_sqrt_is_checked(self):
        x=I(np.array([.01,.9,1.,100.]),np.array([.02,1.,2.,101.]));y=sqrt_i(x)
        self.assertTrue(np.all(I(y.lo).square().hi<=x.lo));self.assertTrue(np.all(I(y.hi).square().lo>=x.hi))
        with self.assertRaises(ValueError):sqrt_i(I(-1))
    def test_07_relaxation_improves_with_quadrature(self):
        a=relaxation(10,256);b=relaxation(10,1024)
        self.assertLess(b['global_optimal_upper'],a['global_optimal_upper']);self.assertGreater(b['feasible_schedule_lower'],a['feasible_schedule_lower'])
        self.assertLess(b['feasible_schedule_lower'],b['global_optimal_upper'])
    def test_08_relaxation_not_a_sampled_claim(self):
        s=(Path(__file__).parent/'global_benchmark.py').read_text();sub=s[s.index('def relaxation'):s.index('def schedule')]
        self.assertNotIn('random',sub);self.assertNotIn('sample',sub);self.assertNotIn('quad(',sub)
    def test_09_schedule_is_feasible(self):
        self.assertTrue(all(.02<=schedule(float(t))<=2. for t in np.linspace(0,1,101)))
    def test_10_flow_transfer_is_monotone(self):
        m=Model(7,9,5);pi=np.tile((LO+HI)/2,(5,m.N,1));a,b=payoff_envelope(m,pi);c,d=payoff_envelope(m,pi,.1)
        self.assertTrue(np.all(c[:-1,~m.boundary]>b[:-1,~m.boundary]));np.testing.assert_allclose(c[:,m.boundary],a[:,m.boundary],atol=1e-10)
    def test_11_complete_domain_location_not_center_only(self):
        m=Model(7,9,5);gap=np.zeros((6,m.N));gap[3,9]=2.;s=full_domain(gap,m)
        self.assertEqual(s['maximum'],2);self.assertEqual(s['location']['time_index'],3);self.assertEqual(s['location']['state_index'],9)
    def test_12_historical_inputs_are_unchanged(self):
        d=json.loads((Path(__file__).resolve().parents[1]/'archive/R8_FILES_SHA256.json').read_text())
        for name,h in d.items():
            if name in ['ECTA.tex','supp.tex']:continue
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),h,name)
    def test_13_same_frozen_policy_accounts_keep_failures(self):
        d=json.loads((OUT/'COMMON_ACCOUNTS.json').read_text());self.assertEqual(len(d['records']),12)
        for r in d['records']:
            self.assertEqual(r['target_pass'],r['regret_upper']<=.1);self.assertIsNone(r['continuous_state_time_error']);self.assertIn('R8 archived',r['cost_basis'])
            if r['compensation']:self.assertGreaterEqual(r['compensation']['minimum_verified_compensation_slack'],0)
    def test_14_refinement_failure_keeps_worst_state(self):
        d=json.loads((OUT/'FULL_DOMAIN_REFINEMENT.json').read_text());self.assertEqual(len(d['records']),18)
        self.assertGreater(max(r['maximum'] for r in d['records']),2.)
        self.assertTrue(all('positive_quantiles' in r and 'lower_action_frequency' in r for r in d['records']))
    def test_15_nested_all_seeds_and_guard_account(self):
        d=json.loads((OUT/'NESTED_RETRAINING.json').read_text());self.assertEqual(len(d['records']),18)
        for r in d['records']:
            if r['guarded']:self.assertIsNotNone(r['guard_fraction']);self.assertGreaterEqual(r['guard_fraction'],0)
        self.assertEqual({tuple(r['grid']) for r in d['records']},{(17,25),(33,49)})
    def test_16_global_benchmark_includes_two_dimensions(self):
        d=json.loads((OUT/'GLOBAL_CAPITAL_BENCHMARK.json').read_text());self.assertEqual(len(d['bounds']),4)
        self.assertEqual([r['dimension'] for r in d['simulations']],[10,20]);self.assertTrue(all(r['continuous_policy_evaluation_error'] is None for r in d['simulations']))
    def test_17_guard_is_own_policy_not_maximizing_label(self):
        s=(Path(__file__).parent/'retrain.py').read_text();self.assertIn('np.nextafter(np.abs(value-target)',s);self.assertIn('np.where(selected,target,value)',s);self.assertNotIn('.Q(',s)
    def test_18_fine_certificates_match_saved_inputs(self):
        d=json.loads((OUT/'NESTED_CERTIFICATES.json').read_text());self.assertEqual(len(d['records']),12)
        for r in d['records']:
            self.assertEqual(hashlib.sha256((ROOT/r['source']).read_bytes()).hexdigest(),r['source_sha256']);self.assertIsNone(r['continuous_state_time_error'])
    def test_19_matching_cover_comparison(self):
        d=json.loads((OUT/'MATCHED_COVER.json').read_text());self.assertEqual(len(d['records']),6);self.assertTrue(d['same_continuation']);self.assertTrue(d['same_initial_policy'])
    def test_20_guarded_policies_have_no_action_labels(self):
        for p in OUT.glob('grid*guarded/*.json'):
            d=json.loads(p.read_text());self.assertEqual(d['exact_argmax_training_labels'],0);self.assertEqual(d['training_all_action_backups'],0)
            self.assertLessEqual(d['counters']['critic_guard_max_residual'],d['counters']['critic_guard_tolerance'])

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(R9Tests))
    (OUT/'TEST_RESULTS.json').write_text(json.dumps(dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),success=result.wasSuccessful(),scope='tests check inclusion and faithful accounts, not whether all economic targets pass'),indent=2)+'\n')
    sys.exit(not result.wasSuccessful())
