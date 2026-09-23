"""Mathematical identities, implementation diagnostics, and evidence invariants.
Passing tests support the recorded certificates; they are not a proof of the
original economy's 0.01 objective or of a stopped-gradient error bound.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math, sys, unittest
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import sympy as sp
import torch
ROOT=Path(__file__).resolve().parents[3]; REV=ROOT/'revisions/2026-09-23-r26'
spec=importlib.util.spec_from_file_location('r26_jets',REV/'replication/jet_certificate.py')
J=importlib.util.module_from_spec(spec);sys.modules[spec.name]=J;spec.loader.exec_module(J)

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class RevisionChecks(unittest.TestCase):
    def test_01_completed_stopped_hamiltonian(self):
        t,x,z,a,p=sp.symbols('t x z a p',real=True);A=F(4,5)+t/5
        v=A*(sp.log(x)+x*z/10-z*z/10)
        vx,vxx=sp.diff(v,x),sp.diff(v,x,2)
        b=v/25-sp.diff(v,t)-x*vx/50-sp.Rational(9,200)*sp.diff(v,z,2)-vx**2/2+(vx/25)**2/(sp.Rational(1,8)*vxx)
        residual=sp.diff(v,t)+(x/50+a+p*x/25)*vx+p*p*x*x*vxx/32+sp.Rational(9,200)*sp.diff(v,z,2)+b-a*a/2-v/25
        aa=A*(1/x+z/10);pp=sp.Rational(16,25)*(1+x*z/10)
        self.assertEqual(sp.simplify(residual+((a-aa)**2+A*(p-pp)**2/16)/2),0)
    def test_02_second_order_chain_rule_against_autograd(self):
        fit=read(ROOT/'revisions/2026-09-23-r25/results/stochastic_reference/neural25201/fit.json')
        net=J.S.Actor()
        with torch.no_grad():
            for layer,data in zip(net.layers,fit['layers']):
                layer.weight.copy_(torch.tensor(data['w']));layer.bias.copy_(torch.tensor(data['b']))
        points=np.array([[0.,.5,-1.],[.25,1.25,0.],[.75,1.75,.5],[1.,2.,1.]])
        vi,gi,hi=J.neural_jet(J.I(points),fit['layers'])
        maxerr=0.
        for n,s in enumerate(points):
            q=torch.tensor(s,requires_grad=True)
            for c in (0,1):
                f=lambda r:net(r[None,:])[0,c]
                v=float(f(q).detach());g=torch.autograd.functional.jacobian(f,q).detach().numpy()
                h=torch.autograd.functional.hessian(f,q).detach().numpy()
                maxerr=max(maxerr,float(abs(v-(vi.lo[n,c]+vi.hi[n,c])/2)))
                self.assertTrue(np.allclose(g,(gi.lo[n,:,c]+gi.hi[n,:,c])/2,rtol=1e-10,atol=2e-11))
                for k,(i,j) in enumerate(J.PAIRS):
                    self.assertAlmostEqual(h[i,j],(hi.lo[n,k,c]+hi.hi[n,k,c])/2,delta=2e-10)
        self.assertLess(maxerr,2e-11)
    def test_03_exact_bernstein_identity(self):
        fit=read(ROOT/'revisions/2026-09-23-r25/results/stochastic_reference/direct/fit.json')
        coef=J.polynomial_mul([F(float(x)) for x in fit['coefficients']],[F(5,4),F(3,4)]);coef[0]-=1
        cert=read(REV/'results/jets/direct_exact.json');last=F(-1)
        for cell in cert['cells']:
            a,b=map(F,cell['xi']);self.assertEqual(a,last);last=b
            beta=list(map(F,cell['bernstein_coefficients']));n=len(beta)-1
            for s in (F(0),F(1,3),F(1,2),F(1)):
                x=a+(b-a)*s;power=sum(c*x**i for i,c in enumerate(coef))
                value=sum(beta[i]*math.comb(n,i)*s**i*(1-s)**(n-i) for i in range(n+1))
                self.assertEqual(power,value)
        self.assertEqual(last,F(1));self.assertLess(cert['regret_upper'],1.3e-7)
    def test_04_complete_jet_covers_and_hashes(self):
        summary=read(REV/'results/jet_summary.json')
        for row in summary['neural']:
            self.assertEqual(sha(ROOT/row['source']),row['source_sha256'])
            for attempt in row['attempts']:
                path=ROOT/attempt['path'];self.assertEqual(sha(path),attempt['sha256'])
                data=np.load(path);lo,hi=J.S.cover(tuple(attempt['shape']))
                np.testing.assert_array_equal(data['lower'],lo);np.testing.assert_array_equal(data['upper'],hi)
                self.assertEqual(len(lo),math.prod(attempt['shape']))
                self.assertTrue(np.isfinite(data['deficit_upper']).all())
                self.assertTrue((data['deficit_upper']>=0).all())
                self.assertLessEqual(attempt['regret_upper'],attempt['first_order_regret_upper_same_cells'])
    def test_05_restart_monotonicity_and_scope(self):
        rows=read(REV/'results/jet_summary.json')['neural']
        for row in rows:
            self.assertTrue(row['target_established']);self.assertFalse(row['is_original_economy']);self.assertTrue(row['policy_unchanged'])
            bounds=[r['upper'] for r in row['restart_upper']]
            self.assertEqual(bounds[-1],0);self.assertTrue(all(a>=b for a,b in zip(bounds,bounds[1:])))
            self.assertEqual(row['attempts'][-1]['cells'],32768)
    def test_06_online_dominance_and_rollback(self):
        rows=read(REV/'results/online_summary.json');self.assertEqual(len(rows),6);rejections=0
        for row in rows:
            for b in row['blocks']:
                path=REV/f"results/online/seed{row['seed']}/{row['arm']}"
                before=read(path/f"block{b['block']}_before_state.json");after=read(path/f"block{b['block']}_after_state.json")
                if b['accepted']:
                    self.assertGreater(b['certificate']['value_interval'][0],b['old_certificate']['value_interval'][1])
                else:
                    rejections+=1;self.assertEqual(before,after);self.assertTrue(b['rollback_verified'])
                    self.assertEqual(b['state_before_sha256'],b['state_after_sha256'])
        self.assertEqual(rejections,5)
    def test_07_shadow_isolated_and_distinct(self):
        rows=read(REV/'results/online_summary.json');shadows=[r for r in rows if r['shadow']]
        self.assertEqual(len(shadows),4)
        for row in shadows:
            self.assertTrue(row['shadow']['trajectory_differs']);self.assertGreater(row['shadow_seconds_excluded'],0.)
            self.assertNotEqual(row['shadow']['state_sha256'],row['shadow']['coupled_final_sha256'])
    def test_08_original_objective_not_relabelled(self):
        data=read(ROOT/'revisions/2026-09-23-r25/results/full_state/summary.json')
        self.assertEqual(data['target'],.01);self.assertTrue(data['original_economy_unchanged']);self.assertTrue(data['current_state_only'])
        self.assertFalse(data['target_established']);self.assertFalse(data['payoff_improvement_proved'])
        self.assertAlmostEqual(data['all_start_times_regret_upper'],7.181834580823298)
    def test_09_expanded_calibration_is_interior(self):
        data=read(ROOT/'revisions/2026-09-23-r25/results/tuning_selection.json')
        self.assertEqual(len(data),6)
        for row in data.values():
            self.assertTrue(row['interior_with_larger_deterioration']);self.assertFalse(row['censored_at_upper_endpoint'])
            self.assertLess(row['selected_rate'],max(t['learning_rate'] for t in row['trials']))
    def test_10_historical_preservation(self):
        for name in ('R24_BASE_SHA256.json','R25_IMPORTED_SHA256.json'):
            data=read(REV/'source_audit'/name)
            for path,want in data.items():
                p=(ROOT/'revisions/2026-09-23-r25'/path) if name=='R25_IMPORTED_SHA256.json' else ROOT/path
                if path=='REVISION_INDEX.md' and sha(p)!=want:
                    p=REV/'source_audit/REVISION_INDEX_before_R26.md'
                self.assertTrue(p.is_file(),path);self.assertEqual(sha(p),want,path)
    def test_11_poll_bound_on_exact_quadratic(self):
        # A finite exact-arithmetic test of the theorem's unsuccessful-poll bound.
        x=[F(3,10),F(-1,5)];h=F(1,10);sigma=F(1);kappa=F(1,8);L=F(1)
        f=lambda x:-sum(t*t for t in x)/2
        for _ in range(100):
            accepted=False
            for i,sgn in ((0,1),(0,-1),(1,1),(1,-1)):
                y=x.copy();y[i]+=sgn*h
                if f(y)-kappa*h*h/2>f(x)+kappa*h*h/2+sigma*h*h:
                    x=y;accepted=True;break
            if not accepted:break
        self.assertFalse(accepted)
        K=sigma+2*kappa+L/2
        self.assertLessEqual(sum(v*v for v in x),2*K*K*h*h)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(RevisionChecks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'passed':result.wasSuccessful(),'autograd_comparison':'floating-point implementation diagnostic only',
            'original_full_state_target_proved':False,'stopped_gradient_error_proved':False}
    J.write(REV/'results/test_summary.json',report)
    raise SystemExit(0 if result.wasSuccessful() else 1)
