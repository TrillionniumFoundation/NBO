"""Disjoint exact-arithmetic fixtures for lossless action screening."""
import unittest
from fractions import Fraction as F
from unittest.mock import patch
import numpy as np
import screen58 as s
n=s.n

class ScreeningTests(unittest.TestCase):
    def critic(self,seed=580013,d=2,m=5):
        rng=np.random.default_rng(seed)
        return n.Critic('relu',d,dict(c=0.,v=rng.integers(-8,9,d)/8,W=rng.integers(-16,17,(d,m))/8,b=rng.integers(-8,9,m)/8,u=rng.integers(-8,9,m)/8))
    def check_all(self,x,c,K,q):
        reduced,offset=s.simplify(s.a.reduce_objective(x,c),F(K,q));v=reduced[-1];out=s.endpoints(reduced,K,q)
        for j in range(K+1):
            z=v(F(j,q))-offset
            self.assertLessEqual(F(float(out.lo[j])),z);self.assertLessEqual(z,F(float(out.hi[j])))
        r=s.minimize(x,c,K,q);k=min(range(K+1),key=lambda j:(v(F(j,q)),j))
        self.assertEqual(r['index'],k);self.assertEqual(F(r['objective_exact']),v(F(k,q)))
        self.assertEqual(r['index'],s.a.minimize(x,c,K,q)['index']);return r
    def test_random_signed_ridges_and_exact_oracle(self):
        for seed in range(580101,580109):self.check_all([.25,.625],self.critic(seed),16,64)
    def test_non_dyadic_lattice(self):self.check_all([.125,.875],self.critic(),17,71)
    def test_zero_projection(self):
        c=self.critic();c.params['W'][1]=c.params['W'][0];self.check_all([.5,.25],c,16,64)
    def test_inactive_and_action_null_ridges(self):
        c=self.critic();c.params['W'][1]=-2*c.params['W'][0]
        r=self.check_all([.25,.5],c,16,64);self.assertEqual(r['active_ridges'],0)
    def test_quadratic_negative_curvature(self):
        c=n.Critic('quadratic',2,dict(c=0.,v=[-1.,.25],Q=[[-8.,0.],[0.,-8.]]));self.check_all([.25,.625],c,16,64)
    def test_terminal_dimensions(self):
        for d in (2,4,8):self.check_all(np.linspace(.125,.75,d),n.Critic.terminal(d),16,64)
    def test_zero_capacity(self):
        r=self.check_all([0.,0.],self.critic(),0,64);self.assertEqual(r['index'],0)
    def test_exact_tie_preserves_smallest_index(self):
        h=F(1,64);q1=-h-4*h**3
        c=n.Critic('quadratic',2,dict(c=0.,v=[2*q1/n.BETA,F(0)],Q=[[F(0),F(0)],[F(0),F(0)]]))
        r=self.check_all([.25,.5],c,16,64);self.assertEqual(r['index'],0);self.assertIn(1,r['candidate_indices'])
    def test_fallback_limit(self):
        with patch.object(s,'MAX_LATTICE',4):r=s.minimize([.5,.5],n.Critic.zero(2),16,64)
        self.assertEqual(r['index'],0);self.assertEqual(r['fallback_reason'],'lattice-limit')
    def test_fallback_arithmetic(self):
        with patch.object(s,'endpoints',side_effect=FloatingPointError):r=s.minimize([.5,.5],n.Critic.zero(2),16,64)
        self.assertEqual(r['index'],0);self.assertEqual(r['solver'],'algebraic-fallback')
    def test_invalid_lattices(self):
        for k,q in ((2.5,64),(1,0),(-1,64),(17,64)):
            with self.assertRaises(ValueError):s.minimize([.5,.5],n.Critic.zero(2),k,q)
    def test_reject_invalid_intervals(self):
        for l,u in (([],[]),([1],[0]),([0],[float('nan')]),([float('-inf')],[0])):
            with self.assertRaises(ValueError):s.survivors(l,u)
    def test_all_minimizers_survive(self):
        rng=np.random.default_rng(580291)
        for _ in range(20):
            exact=rng.integers(-5,6,40);lo=exact-rng.random(40);hi=exact+rng.random(40);keep,_=s.survivors(lo,hi)
            self.assertTrue(set(np.flatnonzero(exact==exact.min()))<=set(keep))
    def test_factor_two_is_sharp(self):
        keep,_=s.survivors([0.,1.],[1.,2.]);self.assertEqual(list(keep),[0,1]);self.assertEqual(2-0,2*1)
    def test_reduction_identity_at_activation_boundaries(self):
        c=self.critic();red=s.a.reduce_objective([.25,.5],c);simp,off=s.simplify(red,F(1,4));q1,q2,features,squares,_=simp
        for x in (F(0),F(1,8),F(1,4)):
            val=q1*x+q2*x*x+4*x**4+sum(w*s.a.old.hinge(z+b*x,r) for w,z,b,r in features)+sum(w*max(0,z+b*x)**2 for w,z,b in squares)
            self.assertEqual(red[-1](x),val+off)
    def test_whole_policy_and_certificate_identity(self):
        part=n.Partition(2,4);cs=[n.Critic.zero(2),self.critic(),n.Critic.terminal(2)]
        g,e,_=s.proposals(cs,part,'algebraic');h,f,_=s.proposals(cs,part,'screened')
        np.testing.assert_array_equal(g,h);np.testing.assert_array_equal(e,f)
        v=s.a.ReferenceVerifier(part,2,2).sweep(g,e);w=s.a.ReferenceVerifier(part,2,2).sweep(h,f);self.assertEqual(v[1],w[1])
        for key in v[2]:np.testing.assert_array_equal(v[2][key],w[2][key])
    def test_no_statistical_repetitions_from_identical_streams(self):
        import hashlib
        streams=[hashlib.sha256(b'fixed-stream').hexdigest()]*6;self.assertEqual(len(set(streams)),1)
if __name__=='__main__':unittest.main(verbosity=2)
