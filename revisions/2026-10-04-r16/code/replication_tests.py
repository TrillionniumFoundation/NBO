"""R16 replication gates; all simulated smoke data use a development-only bank."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import tempfile
import unittest

import replication_pipeline as pipe

ROOT=Path(__file__).resolve().parents[3]

class FrozenDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=pipe.read(ROOT/pipe.PROTOCOL);cls.c=pipe.read(ROOT/pipe.CANDIDATES)

    def test_complete_original_policies_and_separate_banks(self):
        expected=pipe.validate_protocol(self.p,self.c)
        self.assertEqual(len(expected),128);self.assertEqual(len(pipe.trials(self.p)),32)
        self.assertEqual(len({t['noise_key'] for t in pipe.trials(self.p)}),32)

    def test_missing_or_repeated_policy_is_not_a_complete_method(self):
        for mutate in ['remove','duplicate']:
            c=copy.deepcopy(self.c)
            if mutate=='remove':c['files'].pop()
            else:c['files'][-1]=copy.deepcopy(c['files'][0])
            with self.assertRaises(ValueError):pipe.validate_protocol(self.p,c)

    def test_changed_probability_or_sample_budget_is_rejected(self):
        for field,value in [('family_alpha',.02),('event_count',237),('historical_alpha_reused',True)]:
            p=copy.deepcopy(self.p);p['inference'][field]=value
            with self.assertRaises(ValueError):pipe.validate_protocol(p,self.c)
        p=copy.deepcopy(self.p);p['confirmation']['paths_per_seed']=16384
        with self.assertRaises(ValueError):pipe.validate_protocol(p,self.c)

    def test_original_noise_seed_cannot_be_reused(self):
        c=copy.deepcopy(self.c);c['files'][0]['original_confirmation_noise_seed']=pipe.trials(self.p)[0]['noise_seed']
        with self.assertRaises(ValueError):pipe.validate_protocol(self.p,c)

    def test_development_and_confirmation_domains_are_disjoint(self):
        production={t['noise_seed'] for t in pipe.trials(self.p)}
        development={pipe.bank(self.p,t['dimension'],t['stream_seed'],development=True)[0] for t in pipe.trials(self.p)}
        self.assertFalse(production&development)
        for t in pipe.trials(self.p):
            self.assertEqual(pipe.bank(self.p,t['dimension'],t['stream_seed'])[0],t['noise_seed'])

    def test_immutable_candidate_and_proof_closure(self):
        result=pipe.check(ROOT);self.assertTrue(result['complete']);self.assertEqual(result['policy_count'],128)

    def test_artifact_gate_and_path_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaises(ValueError):pipe.safe(root,'../outside')
            with self.assertRaises(ValueError):pipe.safe(root,'/absolute')
            (root/'safe').write_bytes(b'complete')
            self.assertEqual(pipe.bounded(root)['files'],1)
            with (root/'too_large').open('wb') as f:f.truncate(pipe.ARTIFACT_PAYLOAD_LIMIT+1)
            with self.assertRaises(ValueError):pipe.bounded(root)

    def test_creation_only_evidence_lease(self):
        source=(ROOT/pipe.WORKFLOW).read_text()
        self.assertIn('--force-with-lease="refs/heads/$evidence_branch:"',source)
        self.assertIn('git push --atomic',source)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = 1',source)

class OriginalPolicyDevelopmentSmoke(unittest.TestCase):
    def test_all_four_original_policy_types_on_only_development_data(self):
        sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r15/code'))
        from training_core import load_candidate
        from actor_verifier import verify
        from method_statistics import paired_difference
        import numpy as np
        p=pipe.read(ROOT/pipe.PROTOCOL);c=pipe.read(ROOT/pipe.CANDIDATES)
        d=10;seed=p['design']['seeds'][0];noise,key=pipe.bank(p,d,seed,development=True)
        self.assertNotIn(noise,{t['noise_seed'] for t in pipe.trials(p)})
        rows=[];arrays=[]
        with tempfile.TemporaryDirectory(prefix='r16-development-only-') as tmp:
            for method in pipe.METHODS:
                candidate=next(x for x in c['files'] if (x['dimension'],x['stream_seed'],x['method_id'])==(d,seed,method))
                actor,_,state=load_candidate(ROOT/candidate['path'])
                self.assertEqual(state['source_commit'],pipe.CANDIDATE_SOURCE)
                self.assertEqual(state['seed'],seed)
                self.assertEqual(state['params'],p['design']['primitives'])
                folder=Path(tmp)/method
                row=verify(actor,dimension=d,steps=8,paths=8,noise_seed=noise,event_alpha=.05,
                    primitives=p['design']['primitives'],out=folder,record_id='development_only',
                    metadata=dict(method_id=method,stream_seed=seed,is_confirmation=False,noise_key=key,
                        primitives_sha256=p['design']['primitives_sha256'],epsilon=.1,analytic_schedule=candidate['fallback']))
                self.assertIsNone(row['confirmation_bank']);self.assertEqual(row['paths'],8)
                self.assertNotEqual(row['noise_hash'],candidate['original_confirmation_noise_hash'])
                with np.load(folder/'development_only.npz',allow_pickle=False) as raw:arrays.append(raw['paired_gain'].copy())
                rows.append(row)
                self.assertEqual(pipe.sha(ROOT/candidate['path']),candidate['sha256'])
            for j in range(1,4):
                diff=paired_difference(arrays[0],arrays[j],left_identity=rows[0],right_identity=rows[j])
                self.assertEqual(diff.shape,(8,));self.assertTrue(np.isfinite(diff).all())

if __name__=='__main__':unittest.main()
