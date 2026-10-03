"""R8 regressions test validity and reporting, not guaranteed economic success."""
from __future__ import annotations
import hashlib,json,re,sys,unittest
from pathlib import Path
import numpy as np
import torch
from continuous_actor import Model,NDU,Net,bounded,LO,HI,OUT
from action_enclosure import I,Encloser,maximize,reflect,terminal
from action_enclosure_tight import CornerEncloser
ROOT=Path(__file__).resolve().parents[3];REV=Path(__file__).resolve().parents[1]

class R8Tests(unittest.TestCase):
    def test_01_continuous_evaluator_matches_finite_actions(self):
        m=Model(7,9,5);f=NDU(7,9,5);rng=np.random.default_rng(113);v=f.g+rng.normal(size=f.N)*.05
        actions=np.broadcast_to(f.actions,(m.N,f.A,3)).copy()
        with torch.no_grad():q=m.qvalue(torch.tensor(v),torch.tensor(actions),False).numpy()
        np.testing.assert_allclose(q,f.Q(v),rtol=1e-12,atol=1e-11)
    def test_02_reflection_inclusion(self):
        x=I(np.array([1.1,1.19,2.99,3.01]),np.array([1.15,1.21,3.01,3.1]));z=reflect(x,1.2,3.)
        for a in np.linspace(0,1,31):
            p=x.lo+a*(x.hi-x.lo);q=1.2+np.where(np.mod(p-1.2,3.6)<=1.8,np.mod(p-1.2,3.6),3.6-np.mod(p-1.2,3.6))
            self.assertTrue(np.all(q>=z.lo-1e-14) and np.all(q<=z.hi+1e-14))
    def test_03_both_action_enclosers_include_samples(self):
        m=Model(7,9,5);rng=np.random.default_rng(83);v=m.g+.03*rng.normal(size=m.N)
        rows=np.arange(m.N);a=LO+(HI-LO)*rng.random((m.N,3));b=LO+(HI-LO)*rng.random((m.N,3));lo=np.minimum(a,b);hi=np.maximum(a,b)
        for cls in [Encloser,CornerEncloser]:
            en=cls(m,v);bound=en.q(rows,lo,hi)
            for _ in range(7):
                aa=lo+(hi-lo)*rng.random(lo.shape)
                with torch.no_grad():q=m.qvalue(torch.tensor(v),torch.tensor(aa),False).numpy()
                self.assertTrue(np.all(q>=bound.lo-1e-10) and np.all(q<=bound.hi+1e-10))
    def test_04_budget_exhaustion_retains_full_upper(self):
        m=Model(7,9,5);pi=np.tile((LO+HI)/2,(m.N,1));u,stats=maximize(m,m.g,pi,max_depth=0,max_boxes=1)
        self.assertTrue(stats['budget_exhausted']);self.assertGreater(stats['unresolved_leaves'],0)
        f=NDU(7,9,5);self.assertTrue(np.all(u+1e-10>=f.Q(m.g).max(axis=1)))
    def test_05_boundary_and_domain(self):
        m=Model();pi=np.tile((LO+HI)/2,(m.N,1));en=Encloser(m,m.g)
        q=en.q(np.arange(m.N),pi);g=terminal(I(m.points[:,0]),I(m.points[:,1]))
        self.assertTrue(np.all(q.lo[m.boundary]<=g.hi[m.boundary]));self.assertTrue(np.all(q.hi[m.boundary]>=g.lo[m.boundary]))
        self.assertTrue(np.all(np.isfinite(q.lo)) and np.all(np.isfinite(q.hi)))
    def test_06_principal_files_hashes_feasibility_and_scope(self):
        for method in ['actor','direct']:
          for seed in [11,29,47]:
            p=OUT/f'continuous_{method}_s{seed}_search.json';d=json.loads(p.read_text());raw=OUT/d['raw_file'];self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),d['raw_sha256'])
            z=np.load(raw);self.assertTrue(np.all(z['policy']>=LO-1e-14) and np.all(z['policy']<=HI+1e-14))
            self.assertEqual(d['training_all_action_backups'],0);self.assertEqual(d['exact_argmax_training_labels'],0);self.assertIsNone(d['continuous_state_time_error'])
            m=Model();np.testing.assert_allclose(m.evaluate(z['policy']),z['policy_values'],rtol=1e-12,atol=1e-11)
    def test_07_raw_actor_snapshot_extraction(self):
        m=Model()
        for seed in [11,29,47]:
            z=np.load(OUT/f'continuous_actor_s{seed}_search.npz');net=Net(3)
            for t in [0,7,19]:
                net.load_state_dict({name:torch.tensor(z[f'actor_t{t}_'+name]) for name in net.state_dict()})
                with torch.no_grad():a=bounded(net(m.norm)).numpy()
                np.testing.assert_allclose(a,z['raw_policy'][t],rtol=1e-12,atol=1e-12)
    def test_08_pilot_failures_are_not_deleted_or_relabelled(self):
        for p in ['continuous_actor_s11_smoke.json','continuous_actor_s11.json','continuous_actor_s11_h4_fresh1.json','continuous_direct_s11.json']:
            d=json.loads((OUT/p).read_text());self.assertFalse(d['diagnostic_target_pass']);self.assertGreater(d['augmented_grid_deviation_max'],.1)
    def test_09_shared_bounds_and_arithmetic_width(self):
        d=json.loads((OUT/'SHARED_ACTION_CERTIFICATES.json').read_text());z=np.load(OUT/'SHARED_ACTION_CERTIFICATES.npz')
        self.assertEqual(len(d['records']),18);self.assertIsNone(d['continuous_state_time_error'])
        for k in z.files:
            if k.endswith('_lower'):
                hi=z[k[:-6]+'_upper'];self.assertTrue(np.all(z[k]<=hi));self.assertTrue(np.all(z['common_optimal_upper']+1e-9>=z[k]))
        for r in d['records']:
            for target,value in r['absolute_target_pass'].items():self.assertEqual(value,r['policy_regret_upper']<=float(target))
    def test_10_paired_rows_and_missing_nodes(self):
        d=json.loads((OUT/'R7_INTEGRATION.json').read_text());self.assertEqual(len(d['paired_payoffs']),36);self.assertEqual(len(d['missing_pure_nodes']),5)
        seen=set()
        for r in d['paired_payoffs']:
            k=(r['dimension'],r['seed'],r['wide'],r['steps']);self.assertNotIn(k,seen);seen.add(k)
            self.assertLessEqual(r['ci95'][0],r['mean']);self.assertGreaterEqual(r['ci95'][1],r['mean']);self.assertEqual(r['paths'],512)
    def test_11_comparators_include_every_declared_case(self):
        self.assertEqual(len(list(OUT.glob('comparison_game_*.json'))),8);self.assertEqual(len(list(OUT.glob('comparison_ndu_*.json'))),6)
        for p in OUT.glob('comparison_*.json'):
            d=json.loads(p.read_text());raw=OUT/d['raw_file'];self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),d['raw_sha256'])
            self.assertEqual(d['target_pass'],max(d['certificate']['payoff_loss_upper'])<=d['target'])
    def test_12_frozen_refinements_cover_all_levels(self):
        d=json.loads((OUT/'REFINEMENT.json').read_text());self.assertEqual(len(d['records']),18);self.assertIsNone(d['continuous_state_time_error'])
        for method in ['actor','direct']:
          for seed in [11,29,47]:self.assertEqual(sorted(r['steps'] for r in d['records'] if r['method']==method and r['seed']==seed),[20,40,80])
    def test_13_preceding_sources_are_preserved(self):
        from assemble import blob,EXPECTED
        for name,sha in EXPECTED.items():self.assertEqual(blob((REV/'archive'/name.replace('.tex','.R7.tex')).read_bytes()),sha)
        s=(ROOT/'ECTA.tex').read_text();self.assertIn(r'\title{Neural Bellman Operators}',s);self.assertIn('Qian',s)
        for name in ['recursive','Temporal','Games','Endogenous']:
            self.assertIn(name,s)
        self.assertIn('2026-10-03-r8/manuscript/ndu.tex',s)
    def test_14_generated_table_hashes(self):
        d=json.loads((REV/'TABLE_MANIFEST.json').read_text())
        for name,digest in {**d['input_sha256'],**d['generated']}.items():self.assertEqual(hashlib.sha256((REV/name).read_bytes()).hexdigest(),digest)
    def test_15_training_oracle_boundary_is_explicit(self):
        s=(REV/'code/continuous_actor.py').read_text();self.assertGreater(s.index('refmodel=NDU'),s.index('# Training is now over.'))
        self.assertNotIn('.Q(',s[s.index('def solve('):s.index('# Training is now over.')])

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(R8Tests);result=unittest.TextTestRunner(verbosity=2).run(suite)
    (OUT/'TEST_RESULTS.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'success':result.wasSuccessful(),
        'interpretation':'regression and accounting checks; not a claim that every economic target passed'},indent=2)+'\n')
    sys.exit(not result.wasSuccessful())
