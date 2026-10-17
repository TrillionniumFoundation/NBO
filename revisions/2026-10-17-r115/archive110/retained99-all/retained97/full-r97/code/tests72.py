"""Exact theorem regression tests, plus original-economy cache contracts."""
from fractions import Fraction as F
from itertools import product
import math,random,unittest
from certificates72 import (BETA,Witness,transport,capacity,repair,moduli,regularity,
    relu_uniform_mean,relu_box_mean_independent,centered_support)

class FrozenContinuationTests(unittest.TestCase):
    @staticmethod
    def example(T=3):
        rng=random.Random(72001+T);S=3;A=2
        c=[[[F(rng.randrange(-4,8),8) for a in range(A)] for s in range(S)] for t in range(T)]
        P=[]
        for t in range(T):
            level=[]
            for s in range(S):
                acts=[]
                for a in range(A):
                    w=[rng.randrange(1,5) for j in range(S)];acts.append([F(v,sum(w)) for v in w])
                level.append(acts)
            P.append(level)
        g=[F(1,3),F(-1,5),F(2,7)]
        h=[[F(rng.randrange(-8,9),8) for s in range(S)] for t in range(T+1)]
        return c,P,g,h

    @staticmethod
    def evaluate(c,P,g,h,pi):
        T=len(c);v=list(g);z=[g[s]-h[T][s] for s in range(3)]
        for t in reversed(range(T)):
            old=v;oldz=z;v=[];z=[]
            for s in range(3):
                a=pi[t][s];w=P[t][s][a]
                v.append(c[t][s][a]+BETA*sum(w[j]*old[j] for j in range(3)))
                residual=c[t][s][a]+BETA*sum(w[j]*h[t+1][j] for j in range(3))-h[t][s]
                z.append(residual+BETA*sum(w[j]*oldz[j] for j in range(3)))
        return v,z

    def test_exact_identity_arbitrary_critic_and_terminal_correction(self):
        for T in (1,2,4,7):
            c,P,g,h=self.example(T);pi=[[(t+s)%2 for s in range(3)] for t in range(T)]
            v,z=self.evaluate(c,P,g,h,pi)
            self.assertEqual(z,[v[s]-h[0][s] for s in range(3)])

    def test_common_initial_law_policy_difference(self):
        c,P,g,h=self.example();p=[[0]*3 for t in c];n=[[1]*3 for t in c]
        vp,zp=self.evaluate(c,P,g,h,p);vn,zn=self.evaluate(c,P,g,h,n);law=[F(1,2),F(1,3),F(1,6)]
        self.assertEqual(sum(law[s]*(zp[s]-zn[s]) for s in range(3)),sum(law[s]*(vp[s]-vn[s]) for s in range(3)))

    def test_terminal_term_is_necessary(self):
        c,P,g,h=self.example(2);pi=[[0]*3 for _ in c];v,z=self.evaluate(c,P,g,h,pi)
        _,wrong=self.evaluate(c,P,h[-1],h,pi)
        self.assertNotEqual(z,wrong)

    def test_residual_oscillation_pathwise_support(self):
        c,P,g,h=self.example(2);r=[];a=[]
        for t in range(2):
            qs=[[c[t][s][u]+BETA*sum(P[t][s][u][j]*h[t+1][j] for j in range(3)) for u in range(2)] for s in range(3)]
            r.append([min(qs[s])-h[t][s] for s in range(3)])
            a.append([[z-min(qs[s]) for z in qs[s]] for s in range(3)])
        eta=[max(a[t][s][u] for s,u in product(range(3),range(2))) for t in range(2)]
        term=[g[s]-h[-1][s] for s in range(3)]
        L,U=centered_support([max(x)-min(x) for x in r],eta,eta,max(term)-min(term))
        values=[]
        for states in product(range(3),repeat=3):
            for actions in product(range(2),repeat=2):
                values.append(sum(BETA**t*(r[t][states[t]]+a[t][states[t]][actions[t]]) for t in range(2))+BETA**2*term[states[2]])
        self.assertGreaterEqual(min(values)-max(values),L);self.assertLessEqual(max(values)-min(values),U)

    def test_time_constant_gauge_preserves_paired_observation(self):
        c,P,g,h=self.example(3);pi=[[0]*3 for _ in c];nu=[[1]*3 for _ in c]
        hh=[[x+1000*(t+1) for x in row] for t,row in enumerate(h)]
        vp,zp=self.evaluate(c,P,g,h,pi);vn,zn=self.evaluate(c,P,g,h,nu)
        _,zzp=self.evaluate(c,P,g,hh,pi);_,zzn=self.evaluate(c,P,g,hh,nu)
        self.assertEqual([a-b for a,b in zip(zp,zn)],[a-b for a,b in zip(zzp,zzn)])

    def test_level_error_does_not_enter_range(self):
        self.assertEqual(centered_support([F(0)]*4,[F(1,100)]*4,[F(0)]*4)[0],0)

    def test_sharp_residual_width(self):
        self.assertEqual(centered_support([F(3)], [F(0)], [F(0)]),(-F(3),F(3)))

    def test_negative_allowance_rejected(self):
        with self.assertRaises(ValueError):centered_support([F(-1)],[F(0)],[F(0)])

class ConditionalIntegrationTests(unittest.TestCase):
    def test_zero_shocks(self):
        for z in (F(-1),F(0),F(1)):
            self.assertEqual(relu_uniform_mean(z,[0,0]),max(F(0),z))

    def test_one_shock_exact(self):
        for c,a in product([F(x,7) for x in range(-6,7)],[F(0),F(1,3),F(2)]):
            self.assertEqual(relu_uniform_mean(c,[a]),relu_box_mean_independent(c,[a]))

    def test_two_shocks_independent_polygon(self):
        for c,a,b in product([F(x,7) for x in range(-9,10)],[F(0),F(1,5),F(2,3)],[F(0),F(1,7),F(3,4)]):
            self.assertEqual(relu_uniform_mean(c,[a,b]),relu_box_mean_independent(c,[a,b]))

    def test_signed_exposure_invariance(self):
        self.assertEqual(relu_uniform_mean(F(1,9),[F(-2,3),F(1,7)]),relu_uniform_mean(F(1,9),[F(2,3),F(-1,7)]))

    def test_atom_and_touching_halfplane(self):
        for a,b in product([F(1,8),F(1,2)],repeat=2):
            self.assertEqual(relu_uniform_mean(-a-b,[a,b]),0)
            self.assertEqual(relu_uniform_mean(a+b,[a,b]),a+b)

    def test_shock_dimension_not_silently_truncated(self):
        with self.assertRaises(ValueError):relu_uniform_mean(F(0),[1,2,3])

class WitnessTests(unittest.TestCase):
    def record(self,m=1):
        return Witness((F(1,2),F(1,2)),tuple([F(3,16)] if m==1 else [F(3,32),F(3,32)]),F(1,4),F(5,16),2,'a')

    def test_exact_record_reuse(self):
        z=self.record();r=transport(z,z.state,F(1,8),'a')
        self.assertEqual(r['lower'],z.lower);self.assertEqual(r['upper'],z.upper)

    def test_geometric_transfer_is_not_exact_key_reuse(self):
        z=self.record();r=transport(z,(F(1,2)+F(1,2**20),F(1,2)),F(1,8),'a')
        self.assertGreater(r['state_distance'],0);self.assertGreater(r['gap'],z.upper-z.lower)

    def test_stale_context_rejected(self):
        self.assertIsNone(transport(self.record(),(F(1,2),F(1,2)),F(1,8),'b'))

    def test_tighter_budget_rejected(self):
        self.assertIsNone(transport(self.record(),(F(1,2),F(1,2)),F(1,32),'a'))

    def test_scalar_capacity_repair_charged(self):
        r=transport(self.record(),(F(1,2)-F(1,2**16),F(1,2)),F(1,8),'a')
        self.assertGreater(r['action_displacement'],0);self.assertLessEqual(sum(r['action']),capacity((F(1,2)-F(1,2**16),F(1,2))))

    def test_vector_capacity_repair_charged(self):
        r=transport(self.record(2),(F(1,2)-F(1,2**16),F(1,2)),F(1,8),'a')
        self.assertGreater(r['action_displacement'],0);self.assertEqual(len(r['action']),2)

    def test_action_quantum_exact(self):
        for m in (1,2):
            a=repair(tuple([F(1,9)]*m),F(1,7))
            self.assertTrue(all((z*2**32).denominator==1 for z in a));self.assertLessEqual(sum(a),F(1,7))

    def test_invalid_source_is_not_a_certificate(self):
        with self.assertRaises(ValueError):Witness((F(0),F(0)),(F(1),),F(0),F(1),1,'a').validate()

    def test_regularities_hold_long_horizon(self):
        for d,r in product((2,8,16),(1,4,20,100)):
            self.assertLessEqual(regularity(r,d),F(27,d));self.assertTrue(all(v>0 for v in moduli(r,d)))

    def test_zero_query_tolerance_rejected(self):
        with self.assertRaises(ValueError):transport(self.record(),(F(1,2),F(1,2)),F(0),'a')

class OriginalEconomySmokeTests(unittest.TestCase):
    def test_both_controls_return_safe_transferred_witness(self):
        from cache72 import Cache
        for m in (1,2):
            obj=Cache(m);a=obj.solve([.4,.6],2,F(1,16));b=obj.solve([.4+2**-20,.6],2,F(1,16))
            self.assertEqual(obj.counts['hits'],1);self.assertEqual(obj.counts['geometric_hits'],1)
            self.assertLessEqual(F(b['upper'])-F(b['lower']),F(1,16))

    def test_invalidation_and_bounded_storage(self):
        from cache72 import Cache
        obj=Cache(1,capacity=1);obj.solve([.4,.6],1,F(1,16));obj.solve([.8,.8],1,F(1,16))
        self.assertEqual(obj.counts['evictions'],1);obj.invalidate('changed')
        self.assertEqual(len(obj.records),0);self.assertEqual(obj.counts['invalidations'],1)

    def test_serialization_roundtrip(self):
        from cache72 import Cache
        obj=Cache(1);obj.solve([.4,.6],1,F(1,16));saved=obj.payload();new=Cache(1);new.load(saved,obj.epoch)
        new.solve([.4,.6],1,F(1,16));self.assertEqual(new.counts['exact_hits'],1)

    def test_stale_serialization_is_not_loaded(self):
        from cache72 import Cache
        obj=Cache(1);obj.solve([.4,.6],1,F(1,16))
        with self.assertRaises(ValueError):Cache(1).load(obj.payload(),'bad')

if __name__=='__main__':unittest.main(verbosity=2)
