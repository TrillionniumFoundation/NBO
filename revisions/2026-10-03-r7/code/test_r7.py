"""R7 regression tests and independent frozen-evidence replay."""
import hashlib, json, tempfile, unittest
from pathlib import Path
import numpy as np
import torch
import finite_study as f
from paired_coverage import all_policy_exit_bound

class R7Tests(unittest.TestCase):
    def test_invalid_indices(self):
        m=f.NDU(5,7,2);pi=np.zeros((2,m.N),int);pi[0,0]=m.A
        with self.assertRaises(ValueError):f.finite_certificate(m,pi)
    def test_noninteger_indices(self):
        m=f.NDU(5,7,2)
        with self.assertRaises(ValueError):f.finite_certificate(m,np.zeros((2,m.N)))
    def test_invalid_shape(self):
        m=f.NDU(5,7,2)
        with self.assertRaises(ValueError):f.finite_certificate(m,np.zeros((3,m.N),int))
    def test_positive_kernel_enclosure(self):
        m=f.NDU(5,7,2);v=np.sin(m.g);q=f.interval_q(m,f.I(v));exact=m.Q(v)
        self.assertTrue(np.all(q.lo<=exact+1e-14) and np.all(q.hi>=exact-1e-14))
    def test_optimal_finite_policy(self):
        m=f.NDU(5,7,3);ref,pi,_=m.reference();cert,z=f.finite_certificate(m,pi)
        self.assertLess(cert['payoff_loss_upper'][0],1e-10)
        self.assertTrue(np.all(z['best_lower'][...,0]<=ref+1e-12))
        self.assertTrue(np.all(z['best_upper'][...,0]>=ref-1e-12))
    def test_suboptimal_full_dynamic_return(self):
        m=f.NDU(5,7,3);pi=np.zeros((m.steps,m.N),int);ref,_,_=m.reference();value=m.evaluate_policy(pi)
        cert,_=f.finite_certificate(m,pi)
        self.assertGreaterEqual(cert['payoff_loss_upper'][0]+1e-12,float((ref-value).max()))
    def test_game_rival_indexing(self):
        m=f.Game(n=5,steps=2,actions=3);rng=np.random.default_rng(19);pi=rng.integers(m.A,size=(m.steps,m.N,2))
        cert,z=f.finite_certificate(m,pi,True);rows=np.arange(m.N)
        for i in range(2):
            pv=m.g[:,i].copy();br=pv.copy();best=0.
            for t in range(m.steps-1,-1,-1):
                qv=m.Q(pv,i);qb=m.Q(br,i);a,b=pi[t].T
                pv=qv[rows,a,b]
                br=(qb[rows,:,b] if i==0 else qb[rows,a,:]).max(axis=1)
                best=max(best,float((br-pv).max()))
            self.assertGreaterEqual(cert['payoff_loss_upper'][i]+1e-12,best)
            self.assertTrue(np.all(z['policy_lower'][0,:,i]<=pv+1e-12))
    def test_snapshot_is_immutable(self):
        net=f.Net(1);snapshot={};f.put_weights(snapshot,net,'x')
        old={k:v.copy() for k,v in snapshot.items()}
        with torch.no_grad():
            for p in net.parameters():p.add_(1)
        self.assertTrue(all(np.array_equal(v,old[k]) for k,v in snapshot.items()))
    def test_paired_increment_identity(self):
        rng=np.random.default_rng(47);dw=rng.normal(size=(160,32,3))
        d80=dw.reshape(80,2,32,3).sum(1);d40=dw.reshape(40,4,32,3).sum(1)
        np.testing.assert_allclose(d80.reshape(40,2,32,3).sum(1),d40,rtol=1e-14,atol=1e-14)
    def test_exit_bound_monotonicity(self):
        small=all_policy_exit_bound(20,-3,1)['exit_probability_upper_analytic']
        large=all_policy_exit_bound(20,-3.5,1.5)['exit_probability_upper_analytic']
        self.assertLess(large,small);self.assertLess(large,1e-9)
    def test_all_primary_arrays_and_actor_snapshots(self):
        reports=sorted(f.OUT.glob('ndu_*_s*.json'))+sorted(f.OUT.glob('game_M*_s*.json'))
        primary=[p for p in reports if '_smoke' not in p.name];self.assertEqual(len(primary),12)
        for path in primary:
            print('replaying',path.name,flush=True)
            r=json.loads(path.read_text());raw=f.OUT/r['raw_file']
            self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),r['raw_sha256'])
            with np.load(raw) as archive:z={k:archive[k] for k in archive.files}
            isgame=r['study']=='game'
            m=f.Game(market=r['market']) if isgame else f.NDU()
            cert,_=f.finite_certificate(m,z['policy'],isgame)
            np.testing.assert_allclose(cert['payoff_loss_upper'],r['certificates']['final']['payoff_loss_upper'],atol=1e-11,rtol=1e-11)
            self.assertIsNone(r.get('continuous_equilibrium_error') if isgame else r['continuous_state_action_time_error'])
            if not isgame and r['method']=='direct':continue
            x=2*(m.points-m.grid[0])/(m.grid[-1]-m.grid[0])-1 if isgame else np.c_[(m.points[:,0]-2.1)/.9,2*(m.points[:,1]-m.ys[0])/(m.ys[-1]-m.ys[0])-1]
            for t in range(m.steps):
                for player in range(2 if isgame else 1):
                    prefix=f'actor{player}_t{t}_' if isgame else f'actor_t{t}_'
                    actor=f.Net(m.A);actor.load_state_dict({k:torch.tensor(z[prefix+k]) for k in actor.state_dict()})
                    extracted=actor(torch.tensor(x)).detach().numpy().argmax(axis=1)
                    stored=z['raw_policy'][t,:,player] if isgame else z['raw_policy'][t]
                    np.testing.assert_array_equal(extracted,stored)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(R7Tests))
    output=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful())
    (f.OUT/'TEST_RESULTS.json').write_text(json.dumps(output,indent=2)+'\n')
    if not result.wasSuccessful():raise SystemExit(1)
