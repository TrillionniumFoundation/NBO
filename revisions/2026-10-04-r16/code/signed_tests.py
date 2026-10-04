"""Manufactured signed-identity, interval, finite-family and source checks.

No confirmatory occupation or future bank is drawn by this suite.
"""
from __future__ import annotations
from collections import defaultdict
import copy
from decimal import Decimal,localcontext
import json
from pathlib import Path
import unittest
import numpy as np
import signed_worker as w
import signed_pipeline as pipe
import signed_report as report

class SignedIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params=dict(T=1.,discount=.04,productivity=.1,coupling=0.,idiosyncratic_sigma=.6,common_sigma=.3,adjustment=.2,lower=.02,upper=2.,CHI=.03)
        cls.N=8;cls.wt=w.pc.weights(cls.N)
        cls.const=dict(state_cap=100.,beta=0.,accumulated_state_error=1e-12)
        cls.xp=np.array([[-.5,0.,.5],[.7,.4,-.1],[-.3,-.2,.6],[.1,.2,.4]])
        cls.xa=cls.xp-np.array([[.01,-.005,.003],[.008,.006,-.004],[-.01,.004,.002],[.002,.003,.006]])
        cls.nodes=np.array([0,2,5,7])
    def bank(self,xa,xp,seed=741963):
        counters=defaultdict(int)
        v,extra=w.endpoint_bank(w.I(xa),w.I(xp),self.nodes,seed,self.params,self.wt,self.const,2,counters,19)
        return v,extra,counters
    def test_uncoupled_antithetic_closed_form(self):
        value,extra,counters=self.bank(self.xa,self.xp)
        with localcontext() as ctx:
            ctx.prec=90
            gam=2*Decimal.from_float(.03)*(-Decimal.from_float(.04)).exp()
            for i in range(len(self.nodes)):
                a=[Decimal.from_float(x) for x in self.xa[i]];p=[Decimal.from_float(x) for x in self.xp[i]]
                am=sum(a)/3;pm=sum(p)/3
                exact=-gam/2*(sum((x-am)**2 for x in a)-sum((x-pm)**2 for x in p))/3
                self.assertLessEqual(Decimal.from_float(value.lo[i]),exact)
                self.assertGreaterEqual(Decimal.from_float(value.hi[i]),exact)
        self.assertEqual(counters['reference_endpoint_transitions'],8*int((self.N-self.nodes).sum()))
        self.assertEqual(extra['terminal_a'].shape,(4,4,3))
    def test_identical_endpoints_include_exact_zero(self):
        value,_,_=self.bank(self.xp,self.xp)
        self.assertTrue(np.all(value.lo<=0));self.assertTrue(np.all(value.hi>=0))
    def test_endpoint_reversal_preserves_signed_law(self):
        forward,_,_=self.bank(self.xa,self.xp);reverse,_,_=self.bank(self.xp,self.xa)
        np.testing.assert_allclose(forward.lo,-reverse.hi,rtol=0,atol=3e-17)
        np.testing.assert_allclose(forward.hi,-reverse.lo,rtol=0,atol=3e-17)
    def test_last_date_is_only_terminal_and_first_innovation(self):
        z=np.zeros((self.N,1,4));z[0]=[.2,-.1,.3,.4]
        z2=z.copy();z2[1:]=3.
        a=self.xa[-1:];p=self.xp[-1:];nodes=np.array([7])
        first=w.continuation_difference(a,p,nodes,z,self.params,self.wt,self.const,defaultdict(int))[0]
        second=w.continuation_difference(a,p,nodes,z2,self.params,self.wt,self.const,defaultdict(int))[0]
        np.testing.assert_array_equal(first.lo,second.lo);np.testing.assert_array_equal(first.hi,second.hi)
    def test_joint_identity_is_enclosed_before_clipping(self):
        G=w.I(np.array([-.1,.001,.03]),np.array([-.09,.002,.04]));M=w.I(np.array([.002,.003,.004]))
        C=M-G
        self.assertTrue(np.all((M-C).lo<=G.lo));self.assertTrue(np.all((M-C).hi>=G.hi))
        self.assertLess(float(C.lo[2]),0)

class ProtectedRangeTests(unittest.TestCase):
    def test_stage_chord_bound_covers_all_two_sector_vertices(self):
        params=pipe.read(w.ROOT/pipe.PROTOCOL)['design']['primitives']
        wt=w.pc.weights(2048);pi=w.pc.midpoint(wt['M'])*2048
        lo=w.pc.up(wt['center'].hi-.1);hi=w.pc.down(wt['center'].lo+.1)
        for k in [0,257,1023,2047]:
            acts=np.array([[lo[k],lo[k]],[lo[k],hi[k]],[hi[k],lo[k]],[hi[k],hi[k]]])
            v=w.stage_interval(acts,np.full(4,k),params,wt)*2048
            self.assertGreaterEqual(float(v.lo[1]),min(float(v.lo[0]),float(v.lo[3]))-1e-10)
            self.assertGreaterEqual(float(v.lo[2]),min(float(v.lo[0]),float(v.lo[3]))-1e-10)
    def test_centered_interval_bernstein_translates(self):
        a=np.array([-.02,.01,.03,-.01,.002,.003,.008,.012])
        lo=a-1e-8;hi=a+1e-8;c=-.013
        raw=w.oldbridge.interval_empirical_bernstein(lo,hi,bound=.1,event_alpha=.01/6)
        shifted=w.oldbridge.interval_empirical_bernstein(lo-c,hi-c,bound=.1,event_alpha=.01/6)
        self.assertAlmostEqual(raw['lower'],shifted['lower']+c,places=12)
        self.assertAlmostEqual(raw['upper'],shifted['upper']+c,places=12)
    def test_frozen_bounds_reconstruct_without_new_random_samples(self):
        root=w.ROOT;p=pipe.read(root/pipe.PROTOCOL);constants=pipe.read(root/p['signed_constants'])
        params,_=w.oldbridge.verifier.bind_primitives(p['design']['primitives']);wt=w.pc.weights(2048)
        for d in [10,50]:
            reprmax=max(c['bridge_state_error'] for k,c in constants['trials'].items() if k.startswith(f'd{d}_'))
            got=w.signed_range(d,2048,.1,w.oldbridge.verifier.population(d),wt,params,2,8.,reprmax)
            saved=constants['dimensions'][str(d)]
            self.assertGreaterEqual(got['lower_clip'],saved['lower_clip']);self.assertLessEqual(got['upper_clip'],saved['upper_clip'])
            self.assertTrue(got['signed_range_has_no_critic_parameter']);self.assertFalse(got['empirical_population_bounds'])
    def test_development_and_confirmation_domains_are_disjoint(self):
        p=pipe.read(w.ROOT/pipe.PROTOCOL)
        for t in pipe.trials(p):
            dev=pipe.bank(p,t['dimension'],t['stream_seed'],development=True)[0]
            self.assertNotEqual(dev,t['noise_seed'])
            self.assertNotEqual(w.purpose_seed(dev,'occupation_innovations'),w.purpose_seed(t['noise_seed'],'occupation_innovations'))

class ProtocolTests(unittest.TestCase):
    def test_changed_sample_count_and_alpha_are_rejected(self):
        p=pipe.read(w.ROOT/pipe.PROTOCOL);c=pipe.read(w.ROOT/pipe.CANDIDATES)
        pipe.validate_protocol(p,c)
        for key,val in [('paths_per_seed',2048),('antithetic_pairs',4)]:
            bad=copy.deepcopy(p);bad['confirmation'][key]=val
            with self.assertRaises(ValueError):pipe.validate_protocol(bad,c)
        bad=copy.deepcopy(p);bad['inference']['event_count']=2
        with self.assertRaises(ValueError):pipe.validate_protocol(bad,c)
    def test_missing_original_stream_is_rejected(self):
        p=pipe.read(w.ROOT/pipe.PROTOCOL);c=pipe.read(w.ROOT/pipe.CANDIDATES);bad=copy.deepcopy(c);bad['files'].pop()
        with self.assertRaises(ValueError):pipe.validate_protocol(p,bad)
    def test_exact_source_and_candidate_inventory(self):
        got=pipe.check(w.ROOT);self.assertTrue(got['complete']);self.assertEqual(got['policy_count'],32)

if __name__=='__main__':unittest.main()
