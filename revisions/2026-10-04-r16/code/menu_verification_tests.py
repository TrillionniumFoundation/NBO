"""Manufactured correctness gates for the finite-menu economic verifier.

The zero-coupling economy has an exact Gaussian continuation and exact action
derivatives. These tests examine economic coverage, independence accounting,
boundary-safe regret, coefficient identity, and rejection of incomplete data.
They do not inspect any confirmatory NBO checkpoint or payoff bank.
"""
from pathlib import Path
import copy
import decimal
import json
import math
import sys
import tempfile
import unittest
from unittest import mock
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
import menu_economy as economy_module
import menu_verify as verify
import menu_curvature as curvature
import menu_confirm as confirm


def fixture():
    p=dict(T=1.,discount=.04,productivity=.1,coupling=0.,idiosyncratic_sigma=.2,
        common_sigma=.1,adjustment=.2,lower=.02,upper=2.,CHI=.03)
    co=economy_module.coefficient_proposal(p,4)
    # Kept here only so manufactured tests work during concurrent source
    # construction; final production proposals write these exact coefficients.
    co.update(terminal_penalty=float(p['CHI']*co['terminal_discount']),
              drift_constant=float(p['productivity']-(p['idiosyncratic_sigma']**2+p['common_sigma']**2)/2),
              noise_i_step=float(p['idiosyncratic_sigma']*math.sqrt(.25)),
              noise_c_step=float(p['common_sigma']*math.sqrt(.25)))
    e=economy_module.MenuEconomy(dict(id='manufactured_zero_coupling',primitives=p,steps=4,coefficients=co),3,np.eye(3))
    if not hasattr(e,'terminal_penalty'):e.terminal_penalty=co['terminal_penalty']
    if not hasattr(e,'noise_i'):e.noise_i=co['noise_i_step'];e.noise_c=co['noise_c_step']
    q=dict(states=np.asarray([[-.2,0.,.2],[.1,.4,-.2]]),catalog_sha256='manufactured-fixed-catalog',
        utility_weight=np.asarray([[1.],[.8]]),adjustment=np.asarray([[.2],[.4]]),
        lower=np.full((2,1),.02),upper=np.full((2,1),2.))
    a={m:np.full((2,3),e.schedule[0])+(i+1)*np.asarray([[.003,-.002,.001],[-.001,.002,.004]]) for i,m in enumerate(verify.METHODS)}
    proto=dict(training_streams=dict(seeds=[17,29]),confirmation=dict(antithetic_pairs_per_query=16,gaussian_cap=10.,tail_v=8.),
        confidence=dict(alpha=.018,event_count=216,economic_margin=1e-4),
        scalar_accuracy=dict(alpha=.002,event_count=128,economic_margin=1e-4,antithetic_pairs=256,secant_halfwidth=2.**-10))
    return e,q,a,proto


def exact_payoff_difference(e,q,left,right):
    def value(action):
        mean=action.mean(axis=1)
        immediate=e.A[0]*(q['utility_weight'].ravel()*np.log(action).mean(axis=1)-q['adjustment'].ravel()*mean*mean/2)-e.W[0]*mean
        x=q['states']+e.h*(e.c0-action)
        return immediate-e.terminal_penalty*np.mean((x-x.mean(axis=1,keepdims=True))**2,axis=1)
    return float(np.mean(value(left)-value(right)))


class MenuVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e,cls.q,cls.actions,cls.protocol=fixture()
        cls.runs=[verify.verify_arrays(cls.e,cls.q,cls.actions,cls.protocol,seed=s,stage=1,batch_rows=7) for s in [17,29]]

    def test_exact_gaussian_quadratic_economic_coverage(self):
        reference=np.full((2,3),self.e.schedule[0])
        for event,left,right in verify.events():
            true=exact_payoff_difference(self.e,self.q,self.actions[left],reference if right=='reference' else self.actions[right])
            got=verify.pooled_event(self.runs,self.protocol,event)
            self.assertLessEqual(got['lower'],true)
            self.assertGreaterEqual(got['upper'],true)
            self.assertLess(got['upper']-got['lower'],1e-5)
            self.assertEqual(got['paths'],2*2*16)
            self.assertEqual(got['pairs_per_query'],16)

    def test_antithetic_analytic_component_cancels(self):
        for record,arrays in self.runs:
            for m in verify.METHODS:
                self.assertLess(float(np.max(np.abs(arrays['residual_'+m]))),1e-12)
            self.assertEqual(record['independent_observations'],32)

    def test_batch_partition_does_not_change_noise_law_or_samples(self):
        record,arrays=verify.verify_arrays(self.e,self.q,self.actions,self.protocol,seed=17,stage=1,batch_rows=16)
        old,oldarrays=self.runs[0]
        self.assertEqual(record['noise_sha256'],old['noise_sha256'])
        for m in verify.METHODS:
            np.testing.assert_array_equal(arrays['residual_'+m],oldarrays['residual_'+m])

    def test_primary_geometry_replayed_without_randomness(self):
        with mock.patch.object(np.random,'Generator',side_effect=AssertionError('unexpected RNG')), \
             mock.patch.object(np.linalg,'norm',side_effect=AssertionError('hardware-dependent norm proposal')):
            replay=verify.verify_event_accounts(self.e,self.q,self.actions,self.protocol,stage=1)
        record,raw=self.runs[0]
        for key,value in replay.items():self.assertEqual(value,record[key],key)
        for method in verify.METHODS:
            self.assertEqual(replay['quadratic_center_sha256'][method],economy_module.array_hash(raw['quadratic_center_'+method]))

    def test_frozen_matrices_have_fresh_and_independent_positive_LDL(self):
        root=Path(__file__).resolve().parents[1]
        protocol=json.loads((root/'protocols/menu_protocol.json').read_text())
        with decimal.localcontext() as ctx:
            ctx.prec=90;D=decimal.Decimal.from_float
            for dimension in [10,50]:
                B=np.asarray(protocol['coupling_matrices'][str(dimension)]['values'],dtype=np.float64)
                with mock.patch.object(np.linalg,'norm',side_effect=AssertionError('SVD is not a proof input')):
                    account=curvature.deterministic_spectral_bound(B)
                self.assertIn('fixed pre-data dyadic',account['proposal_source'])
                self.assertTrue(all(p[0]>0 for p in account['attempts'][-1]['pivots']))
                # Independent 90-digit LDL uses its own exact binary64 inputs,
                # Gram construction and LDL recurrence, not the interval code.
                A=[[D(account['lambda_upper'])*(int(i==j))-sum((D(B[k,i])*D(B[k,j]) for k in range(dimension)),decimal.Decimal(0))
                    for j in range(dimension)] for i in range(dimension)]
                L=[[decimal.Decimal(int(i==j)) for j in range(dimension)] for i in range(dimension)];pivots=[]
                for j in range(dimension):
                    pivot=A[j][j]-sum((L[j][k]**2*pivots[k] for k in range(j)),decimal.Decimal(0))
                    self.assertGreater(pivot,0);pivots.append(pivot)
                    for i in range(j+1,dimension):
                        L[i][j]=(A[i][j]-sum((L[i][k]*L[j][k]*pivots[k] for k in range(j)),decimal.Decimal(0)))/pivot

    def test_unknown_matrix_uses_deterministic_gershgorin_fallback(self):
        with mock.patch.object(np.linalg,'norm',side_effect=AssertionError('SVD is not available')):
            account=curvature.deterministic_spectral_bound(np.eye(3))
        self.assertIn('unknown matrix',account['proposal_source'])
        self.assertNotIn(account['matrix_sha256'],curvature.FIXED_SPECTRAL_PROPOSALS)
        self.assertGreaterEqual(account['lambda_upper'],1.)

    def test_missing_stream_and_duplicate_noise_rejected(self):
        with self.assertRaises(ValueError):verify.pooled_event(self.runs[:1],self.protocol,'nbo_scalar_gain')
        bad=copy.deepcopy(self.runs)
        bad[1][0]['noise_domain']=bad[0][0]['noise_domain']
        bad[1][0]['noise_sha256']=bad[0][0]['noise_sha256']
        with self.assertRaises(ValueError):verify.pooled_event(bad,self.protocol,'nbo_scalar_gain')

    def test_registered_action_set_and_pair_count_enforced(self):
        bad=dict(self.actions);bad.pop('raw_saa')
        with self.assertRaises(ValueError):verify.verify_arrays(self.e,self.q,bad,self.protocol,seed=17,stage=1)
        bad=copy.deepcopy(self.actions);bad['nbo_scalar'][0,0]=0.
        with self.assertRaises(ValueError):verify.verify_arrays(self.e,self.q,bad,self.protocol,seed=17,stage=1)
        wrong=copy.deepcopy(self.runs[0][1]);wrong['residual_nbo_scalar']=wrong['residual_nbo_scalar'][:,:-1]
        with self.assertRaises(ValueError):verify.event_samples(self.runs[0][0],wrong,'nbo_scalar_gain')

    def test_true_scalar_curvature_and_whole_segment_regret(self):
        lo=np.full(3,.35);hi=np.full(3,.65);y=self.q['states'][0]
        account=curvature.scalar_curvature(self.e,y,lo,hi,utility_weight=1.,adjustment=.2)
        self.assertTrue(account['strong_concavity_verified'])
        r=hi-lo
        for s in np.linspace(0,1,21):
            a=lo+s*r
            exact_second=-self.e.A[0]*(np.mean(r*r/(a*a))+.2*float(r.mean())**2)
            self.assertLessEqual(exact_second,account['Q_second_derivative_upper'])
            self.assertLessEqual(abs(exact_second),account['absolute_second_derivative_upper'])
        ratio=self.e.W[0]/self.e.A[0]
        optimum=2/(ratio+math.sqrt(ratio*ratio+.8))
        optimum_s=np.clip((optimum-.35)/.3,0,1)
        def f(s):
            a=.35+.3*s
            return self.e.A[0]*(math.log(a)-.2*a*a/2)-self.e.W[0]*a
        for s in [0.,.1,.5,.9,1.]:
            a=.35+.3*s
            g=.3*(self.e.A[0]*(1/a-.2*a)-self.e.W[0])
            got=curvature.scalar_gradient_gap([g-1e-10,g+1e-10],s,account)
            self.assertGreaterEqual(got['gap_upper'],f(optimum_s)-f(s)-1e-14)

    def test_quadratic_support_encloses_exact_real_vertex_and_endpoints(self):
        with decimal.localcontext() as ctx:
            ctx.prec=90
            D=decimal.Decimal.from_float
            for gl,gu,G,s in [(-.4,.37,-2.3,.3),(-1e-14,1e-14,-.027,1/3),
                              (-2.,-.5,-.2,.7),(.1,.3,.8,.3),(-.3,.4,0.,.1)]:
                values=[decimal.Decimal(0)]
                for g in [gl,gu]:
                    deltas=[-D(s),1-D(s)]
                    if G<0:
                        vertex=-D(g)/D(G)
                        if deltas[0]<=vertex<=deltas[1]:deltas.append(vertex)
                    values.extend(D(g)*v+D(G)*v*v/2 for v in deltas)
                result=curvature.scalar_gradient_gap([gl,gu],s,{'Q_second_derivative_upper':G})
                self.assertGreaterEqual(D(result['gap_upper']),max(values))

    def test_scalar_finite_difference_protects_exact_optimum(self):
        e=self.e; ratio=e.W[0]/e.A[0]
        optimum=2/(ratio+math.sqrt(ratio*ratio+.8))
        lo=e.schedule[0]-.1;hi=e.schedule[0]+.1
        candidate=dict(a_left=[lo]*3,a_right=[hi]*3,candidate_s=(optimum-lo)/(hi-lo),
            state=self.q['states'][0].tolist(),task=dict(utility_weight=1.,adjustment=.2,lower=.02,upper=2.),
            continuation_sha256=e.continuation_sha256)
        record,arrays=verify.verify_scalar(e,None,candidate,self.protocol,seed=17,batch_rows=17)
        self.assertLessEqual(record['gradient_interval'][0],0.)
        self.assertGreaterEqual(record['gradient_interval'][1],0.)
        self.assertLess(record['implemented_candidate_gap_upper'],1e-4)
        self.assertEqual(record['independent_antithetic_pairs'],256)
        self.assertEqual(arrays['scalar_secant_residual'].shape,(256,))
        with mock.patch.object(np.random,'Generator',side_effect=AssertionError('unexpected RNG')), \
             mock.patch.object(verify,'_future_value',side_effect=AssertionError('unexpected rollout')):
            replay=verify.replay_scalar(e,None,candidate,self.protocol,seed=17,raw_arrays=arrays)
        expected={k:v for k,v in record.items() if k!='work'}
        self.assertEqual(replay,expected)
        wrong=dict(arrays);wrong['noise_seed']=np.asarray(0,dtype=np.uint64)
        with self.assertRaises(ValueError):verify.replay_scalar(e,None,candidate,self.protocol,seed=17,raw_arrays=wrong)

    def test_complete_fit_trial_and_scalar_identity_preflight(self):
        protocol=copy.deepcopy(self.protocol)
        states=np.asarray(self.q['states'])
        protocol['query_catalogs']={'3':dict(states=states.tolist(),states_sha256=economy_module.array_hash(states))}
        protocol['tasks']=[dict(id='manufactured-central',utility_weight=1.,adjustment=.2,lower=.02,upper=2.)]
        protocol['scalar_accuracy'].update(state_index=0,task_index=0,action_radius=.1)
        queries=economy_module.fixed_queries(protocol,3)
        source='0'*40; source_files={'manufactured_source.py':dict(sha256='a'*64,bytes=17)}
        with tempfile.TemporaryDirectory(prefix='r16-manufactured-menu-preflight-') as directory:
            root=Path(directory); protocol_path=root/'protocol.json'
            protocol_path.write_text(json.dumps(protocol,sort_keys=True))
            fits=root/'fits'
            for method in verify.METHODS:
                base=fits/method;base.mkdir(parents=True)
                for stage in [1,2,3]:
                    name=f'actions_stage{stage}.npz'
                    np.savez_compressed(base/name,actions=np.full((2,3),self.e.schedule[0]),
                        **{k:v for k,v in queries.items() if k!='catalog_sha256'})
                    (base/f'stage{stage}.json').write_text(json.dumps(dict(stage=stage,method=method,
                        schema='nbo-r16-menu-sealed-stage-v1',sealed=True,source_commit=source,
                        calibration=self.e.calibration['id'],dimension=3,seed=17,
                        actions_file=name,actions_sha256=confirm.sha(base/name),
                        continuation_sha256=self.e.continuation_sha256,query_catalog_sha256=queries['catalog_sha256'])))
                if method=='nbo_scalar':
                    candidate=economy_module.scalar_query_spec(protocol,self.e)
                    candidate.update(seed=17,stage=3,candidate_s=.5,primary_vector_candidate_unchanged=True)
                    (base/'SCALAR_CANDIDATE.json').write_text(json.dumps(candidate))
                if method=='raw_saa':
                    (base/'failure_recovery').mkdir()
                    (base/'failure_recovery/original-unsealed.json').write_text('{"sealed":false}\n')
                inventory={str(p.relative_to(base)):dict(sha256=confirm.sha(p),bytes=p.stat().st_size)
                    for p in base.rglob('*') if p.is_file()}
                work=dict(method=method,calibration=self.e.calibration['id'],dimension=3,seed=17,
                    source_commit=source,source_files=source_files,protocol_sha256=confirm.sha(protocol_path),
                    final_confirmation_read=False,payload_inventory=inventory)
                (base/'FIT_WORK.json').write_text(json.dumps(work))
            call=lambda:confirm.preflight(fits,self.e,queries,source,source_files,protocol_path,seed=17)
            actions,records,candidate,inputs=call()
            self.assertEqual(len(records),15)
            self.assertIn(str((fits/'raw_saa/failure_recovery/original-unsealed.json').resolve()),inputs)
            path=fits/'raw_saa/FIT_WORK.json';good=path.read_text();bad=json.loads(good);bad['seed']=29
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'another method, calibration, dimension, or seed'):call()
            path.write_text(good)
            stagepath=fits/'raw_saa/stage1.json';sealed=stagepath.read_text()
            unsealed=json.loads(sealed);unsealed['sealed']=False;stagepath.write_text(json.dumps(unsealed))
            bad=json.loads(good);bad['payload_inventory'][stagepath.name]=dict(sha256=confirm.sha(stagepath),bytes=stagepath.stat().st_size)
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'not atomically sealed'):call()
            path.write_text(good);stagepath.write_text(sealed)
            scalarpath=fits/'nbo_scalar/SCALAR_CANDIDATE.json';workpath=scalarpath.parent/'FIT_WORK.json'
            original_candidate=scalarpath.read_text();original_work=workpath.read_text()
            for key,value in [('seed',29),('a_left',[.03]*3)]:
                bad=json.loads(original_candidate);bad[key]=value;scalarpath.write_text(json.dumps(bad))
                work=json.loads(original_work)
                work['payload_inventory'][scalarpath.name]=dict(sha256=confirm.sha(scalarpath),bytes=scalarpath.stat().st_size)
                workpath.write_text(json.dumps(work))
                with self.assertRaisesRegex(ValueError,'scalar candidate'):call()
                scalarpath.write_text(original_candidate);workpath.write_text(original_work)


if __name__=='__main__':unittest.main(verbosity=2)
