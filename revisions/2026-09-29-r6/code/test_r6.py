"""Independent regression checks; numerical tests are not a machine proof."""
from __future__ import annotations
import hashlib,json,math,sys,unittest
from pathlib import Path
import mpmath as mp
import numpy as np
import torch
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'revisions/2026-09-28/code'))
import stopped_consumption as sc
import interval_certificate as ic
import ndu_neural as ndu
import coupled_diffusion as cd
import dynamic_cournot as game
from nbo_core import independent_probe_loss,jet
OUT=Path(__file__).resolve().parents[1]/'results'
mp.mp.dps=80

class R6Tests(unittest.TestCase):
    def test_transcendental_enclosures(self):
        for x in np.linspace(-30,30,151):
            for fn,mfn in [(ic.exp_i,mp.exp),(ic.tanh_i,mp.tanh)]:
                bound=fn(ic.I(x));true=mfn(mp.mpf(float(x)))
                self.assertLessEqual(mp.mpf(float(bound.lo)),true);self.assertGreaterEqual(mp.mpf(float(bound.hi)),true)
        for x in np.geomspace(.001,1000,151):
            b=ic.log_i(ic.I(x));t=mp.log(mp.mpf(float(x)))
            self.assertLessEqual(mp.mpf(float(b.lo)),t);self.assertGreaterEqual(mp.mpf(float(b.hi)),t)
    def test_interval_jets_against_autodiff(self):
        model=json.loads((OUT/'consumption_nbo_s11_w16_d2_r8_c60_a40.json').read_text())
        value=sc.Value();linear=[l for l in value.network.layers if isinstance(l,torch.nn.Linear)]
        with torch.no_grad():
            for layer,weights in zip(linear,model['value']):layer.weight.copy_(torch.tensor(weights['weight']));layer.bias.copy_(torch.tensor(weights['bias']))
        x=np.linspace(.5,2.5,113);a=ic.value_jets(ic.I(x[:,None]-1e-10,x[:,None]+1e-10),model)
        z,v,vt,p,H=jet(value,torch.tensor(np.c_[x*0,x]));truth=[v.detach().numpy(),p.detach().numpy(),H[:,0,:].detach().numpy()]
        for bound,t in zip(a,truth):self.assertTrue(np.all(bound.lo<=t));self.assertTrue(np.all(bound.hi>=t))
    def test_saved_continuous_certificates_and_full_cover(self):
        files=sorted(OUT.glob('consumption_*_s*_w16_d2_r8_c60_a40_certificate.json'));self.assertEqual(len(files),6)
        for f in files:
            c=json.loads(f.read_text());modelpath=f.with_name(f.name.replace('_certificate',''));leafpath=f.with_name(f.name.replace('_certificate.json','_interval_leaves.npz'))
            self.assertEqual(c['model_sha256'],hashlib.sha256(modelpath.read_bytes()).hexdigest());self.assertEqual(c['interval_source_sha256'],hashlib.sha256(Path(ic.__file__).read_bytes()).hexdigest());self.assertEqual(c['leaf_sha256'],hashlib.sha256(leafpath.read_bytes()).hexdigest())
            leaves=np.load(leafpath)['leaves'];self.assertEqual(leaves[0,0],.5);self.assertEqual(leaves[-1,1],2.5);np.testing.assert_array_equal(leaves[:-1,1],leaves[1:,0]);self.assertTrue(c['passed']);self.assertLess(c['policy_regret_upper'],.051)
    def test_consumption_reference_grid_refinement(self):
        a=sc.reference(640);b=sc.reference(1280);c=sc.reference(2560)
        e1=np.max(abs(a['value']-b['value'][::2]));e2=np.max(abs(b['value']-c['value'][::2]))
        self.assertLess(e2,e1);self.assertLess(c['discrete_residual'],1e-8)
    def test_ndu_referee_action_sensitivity(self):
        expected={'r2':-11.9152112208,'adjustment':-10.6081194696,'expanded':-4.8410081366}
        for name,target in expected.items():
            m=ndu.NDU(actions=name);v,a,t=m.reference();self.assertAlmostEqual(v[0,m.N//2],target,places=8)
    def test_finite_certificate_with_nonzero_approximation(self):
        m=ndu.NDU(7,9,4);v,a,_=m.reference();rng=np.random.default_rng(2);candidate=v+rng.normal(0,.02,v.shape);policy=a.copy();policy[:,::7]=0
        cert=m.certificate(candidate,policy);vp=m.evaluate_policy(policy)
        accounts=np.array(cert['accounts'])
        self.assertTrue(np.all(np.max(abs(candidate-vp),axis=1)<=np.r_[accounts[:,1],cert['terminal_error']]+1e-10))
        self.assertTrue(np.all(np.max(v-vp,axis=1)<=np.r_[accounts[:,3],2*cert['terminal_error']]+1e-10))
        for bad in [np.full_like(v,np.nan),v[:-1]]:
            with self.assertRaises(ValueError):m.certificate(bad,policy)
    def test_dense_action_solver_against_constrained_optimizer(self):
        rng=np.random.default_rng(18)
        for d in [2,5,10]:
            for _ in range(5):
                p=rng.normal(1/d,.5/d,d);a=cd.maximizing_action(torch.tensor(p)[None,:]).numpy().ravel()
                fun=lambda m:-np.log(m).mean()+.5*cd.P['adjustment']*m.mean()**2+np.dot(m,p)
                opt=minimize(fun,np.ones(d),method='L-BFGS-B',bounds=[(.02,2.)]*d,options={'ftol':1e-14,'gtol':1e-10,'maxiter':500})
                self.assertLessEqual(fun(a),opt.fun+1e-8)
    def test_trace_product_value_and_gradient(self):
        # Exact finite-dimensional trace; Monte Carlo tolerances declared in code.
        torch.manual_seed(91);n=150000;theta=torch.tensor(.7,requires_grad=True)
        H=theta*torch.tensor([[2.,.4],[.4,-1.]]).expand(n,-1,-1);S=torch.eye(2).expand(n,-1,-1)
        deterministic=torch.full((n,1),1.1);loss=independent_probe_loss(deterministic,S,H,4);loss.backward()
        true=(1.1-.5*.7)**2;gradient=-(1.1-.5*.7)
        self.assertLess(abs(float(loss.detach())-true),.012);self.assertLess(abs(theta.grad.item()-gradient),.025)
    def test_hvp_trace_contraction(self):
        d=3;torch.manual_seed(2);value=cd.Critic(d);tx=torch.rand(20,d+1);z,v,vt,p,H=jet(value,tx)
        gen=torch.Generator().manual_seed(77);estimate=cd.hvp_trace(p,z,400,gen).detach().numpy();truth=cd.exact_trace(H).detach().numpy()
        self.assertLess(np.max(abs(estimate-truth)),.005)
    def test_independent_dynamic_best_response(self):
        result=game.Game(17,30,11).solve();self.assertEqual(result['pure_stage_failures'],0);self.assertLess(max(result['exploitability_max']),1e-9)
    def test_missing_pure_stage_equilibrium_is_reported(self):
        result=game.Game(9,8,7).solve();self.assertGreater(result['pure_stage_failures'],0)
        raw=np.load(OUT/(result['model_id']+'.npz'))
        self.assertTrue(np.all(raw['exploitability'].max(axis=1)<=raw['exploitability_bounds_by_time']+1e-9))
    def test_bad_joint_loss_is_not_accepted(self):
        runs=json.loads((OUT/'consumption_primary.json').read_text())['runs'];joint=[r for r in runs if r['method']=='joint']
        self.assertEqual(len(joint),3);self.assertTrue(all(not r['diagnostic_pass'] for r in joint))

if __name__=='__main__':unittest.main(verbosity=2)
