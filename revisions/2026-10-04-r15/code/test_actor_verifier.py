"""Independent identities and calibration guards for the new verifier.

The two-dimensional, eight-cell fixtures are software checks outside the
confirmatory protocol. Their numerical outcomes never enter method tables.
"""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import actor_verifier as av


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.params = dict(av.FIXED, idiosyncratic_sigma=.6, common_sigma=.3)
        self.temp = tempfile.TemporaryDirectory(prefix='nbo-r15-verifier-test-')
        self.addCleanup(self.temp.cleanup)
        self.actor = av.old.Actor(2, 4, .1)
        self.metadata = dict(method_id='nbo', stream_seed=123,
                             is_confirmation=False, noise_key='software-test')

    def evaluate(self, name, **changes):
        meta = dict(self.metadata, **changes)
        return av.verify(self.actor, dimension=2, steps=8, paths=16,
                         noise_seed=19731, event_alpha=.01, primitives=self.params,
                         out=self.temp.name, record_id=name, metadata=meta)

    def test_analytical_fallback_is_exact_and_shares_reference(self):
        a = self.evaluate('candidate')
        b = self.evaluate('fallback', analytic_schedule=True)
        self.assertEqual((b['lower'], b['upper'], b['mean']), (0., 0., 0.))
        for key in ['noise_hash', 'initial_profile_hash', 'terminal_anchor_hash']:
            self.assertEqual(a[key], b[key])
        raw = np.load(Path(self.temp.name)/b['raw_path'])
        self.assertTrue(np.array_equal(raw['paired_gain'], np.zeros(16)))
        self.assertEqual(b['terminal_policy_hash'], b['terminal_anchor_hash'])

    def test_common_path_cancellation_and_raw_decomposition(self):
        a = self.evaluate('left')
        b = self.evaluate('right', method_id='raw_costate')
        x = np.load(Path(self.temp.name)/a['raw_path'])
        y = np.load(Path(self.temp.name)/b['raw_path'])
        self.assertTrue(np.array_equal(x['paired_gain'], y['paired_gain']))
        self.assertTrue(np.array_equal(x['paired_gain'],
            x['production']-x['consumption_deficit']+x['terminal_gain']))
        self.assertEqual(a['primitives'], self.params)
        self.assertEqual(a['work']['verification_transitions'], 2*8*16)
        self.assertEqual(a['initial_state_hash'], b['initial_state_hash'])

    def test_mixed_economic_fingerprint_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'fingerprints differ'):
            self.evaluate('bad', primitives_sha256='0'*64)

    def test_unproved_primitive_change_is_rejected(self):
        self.params['coupling'] = .3
        with self.assertRaisesRegex(ValueError, 'fixed primitive'):
            self.evaluate('bad-model')


if __name__ == '__main__':
    unittest.main()
