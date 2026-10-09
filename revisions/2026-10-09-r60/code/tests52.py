"""Exact-rational tests of the action-contrast and finite-sweep results."""
from fractions import Fraction as F
import random
import unittest
import contrast52 as c
b = c.base

class ContrastTests(unittest.TestCase):
    def test_coupling_marginals_and_zero_weights(self):
        for p,q in [([F(0),F(1,3),F(2,3)],[F(1,2),F(1,2),F(0)]),
                    ([F(1)],[F(1,7),F(6,7)])]:
            C = c.coupling(p,q)
            self.assertEqual([sum((v for i,j,v in C if i==x),F(0)) for x in range(len(p))],p)
            self.assertEqual([sum((v for i,j,v in C if j==y),F(0)) for y in range(len(q))],q)

    def test_invalid_couplings_rejected(self):
        for p,q in [([], [F(1)]),([F(-1),F(2)],[F(1)]),([F(1,2)],[F(1)])]:
            with self.assertRaises(ValueError):c.coupling(p,q)
        with self.assertRaises(ValueError):c.transport([[F(-1)]],[F(1)],[F(1)])
        with self.assertRaises(ValueError):c.transport([[F(0),F(0)]],[F(1)],[F(1)])

    def test_residual_pair_bounds_and_kernel_contrasts(self):
        for seed in range(12):
            T=1+seed%4;model,g,pi,rng=b.instance(2000+seed,T)
            J=b.evaluate(model,g,pi)
            h=[[v+F(rng.randrange(-6,7),32) for v in row] for row in J]
            C=c.certificate(model,g,pi,h)
            for t in range(T+1):
                e=[j-v for j,v in zip(J[t],h[t])]
                for x in range(len(g)):
                    self.assertEqual(C['pair_bounds'][t][x][x],0)
                    for y in range(len(g)):
                        self.assertLessEqual(abs(e[x]-e[y]),C['pair_bounds'][t][x][y])
                        self.assertLessEqual(C['pair_bounds'][t][x][y],C['widths'][t])
                        self.assertEqual(C['pair_bounds'][t][x][y],C['pair_bounds'][t][y][x])
            for t in range(T):
                e=[j-v for j,v in zip(J[t+1],h[t+1])]
                for x in range(len(g)):
                    for a in range(3):
                        for v in range(3):
                            actual=abs(b.expectation(model[1][t][x][a],e)-b.expectation(model[1][t][x][v],e))
                            self.assertLessEqual(actual,C['action_bounds'][t][x][a][v])
                self.assertLessEqual(C['chi'][t],C['widths'][t+1])

    def test_safe_changes_and_improved_recursion(self):
        accepted=rejected=0;strictly_tighter=False
        for seed in range(16):
            T=1+seed%5;model,g,pi,rng=b.instance(3000+seed,T);V=b.optimal(model,g)
            for k in range(T):
                J=b.evaluate(model,g,pi)
                h=[[v+F(rng.randrange(-6,7),128) for v in row] for row in J]
                new,eps,C,counts=c.improve(model,g,pi,h,F(1,256));K=b.evaluate(model,g,new)
                accepted+=counts['accepted'];rejected+=counts['rejected']
                for t in range(T):
                    self.assertTrue(all(V[t][x]<=K[t][x]<=J[t][x] for x in range(len(g))))
                    self.assertLessEqual(max(K[t][x]-V[t][x] for x in range(len(g))),
                        model[2][t]*max(J[t+1][x]-V[t+1][x] for x in range(len(g)))+eps[t])
                    strictly_tighter |= C['chi'][t]<C['widths'][t+1]
                pi=new
        self.assertGreater(accepted,0);self.assertGreater(rejected,0);self.assertTrue(strictly_tighter)

    def test_full_horizon_with_unbounded_action_null_errors(self):
        for T in (1,2,3,4,5):
            model,g,initial,states=c.exogenous_instance(T);V=b.optimal(model,g)
            reference=None
            for amplitude in (F(0),F(1),F(16),F(4096)):
                pi=[row.copy() for row in initial];policies=[]
                for k in range(T):
                    J=b.evaluate(model,g,pi)
                    h=[[val-amplitude*(t+1)*z for val,(z,u) in zip(row,states)]
                       for t,row in enumerate(J)]
                    new,eps,C,counts=c.improve(model,g,pi,h)
                    self.assertEqual(C['chi'],[F(0)]*T);self.assertEqual(eps,[F(0)]*T)
                    K=b.evaluate(model,g,new)
                    self.assertTrue(all(v<=u for js,ks in zip(J,K) for u,v in zip(js,ks)))
                    policies.append(new);pi=new
                self.assertEqual(b.evaluate(model,g,pi),V)
                if reference is None:reference=policies
                else:self.assertEqual(reference,policies)

    def test_scalar_gate_can_block_null_error_improvement(self):
        model,g,pi,states=c.exogenous_instance(3);J=b.evaluate(model,g,pi)
        h=[[v-F(4096)*(t+1)*z for v,(z,u) in zip(row,states)] for t,row in enumerate(J)]
        local,eps,C,counts=c.improve(model,g,pi,h)
        scalar,_,_,_=b.improve(model,g,pi,h)
        self.assertEqual(scalar,pi);self.assertNotEqual(local,pi)
        self.assertEqual(C['chi'],[F(0)]*3)
        self.assertTrue(any(k<j for js,ks in zip(J,b.evaluate(model,g,local)) for j,k in zip(js,ks)))

    def test_non_null_error_is_not_free(self):
        model,g,pi,states=c.exogenous_instance(2);J=b.evaluate(model,g,pi)
        h=[[v-F(4)*u for v,(z,u) in zip(row,states)] for row in J]
        new,_,C,_=c.improve(model,g,pi,h)
        self.assertTrue(any(x>0 for x in C['chi']))
        K=b.evaluate(model,g,new)
        self.assertTrue(all(v<=u for js,ks in zip(J,K) for u,v in zip(js,ks)))

    def test_constant_shift_invariance(self):
        model,g,pi,rng=b.instance(700,4);J=b.evaluate(model,g,pi)
        h=[[v+F(rng.randrange(-3,4),16) for v in row] for row in J]
        shifted=[[v+F((t+1)**2,7) for v in row] for t,row in enumerate(h)]
        p,e,C,_=c.improve(model,g,pi,h);q,f,D,_=c.improve(model,g,pi,shifted)
        self.assertEqual((p,e,C['pair_bounds'],C['action_bounds']),(q,f,D['pair_bounds'],D['action_bounds']))

    def test_factor_two_still_sharp(self):
        model=([[[F(0),F(0)],[F(0),F(0)]]],
               [[[[F(1),F(0)],[F(0),F(1)]],[[F(1),F(0)],[F(0),F(1)]]]],[F(1)])
        for n in (8,32,128):
            d=F(1,n);g=[F(2),d];pi=[[0,0]];h=[[F(1),F(1)],[F(1),d]]
            new,eps,C,_=c.improve(model,g,pi,h)
            self.assertEqual(new,pi);self.assertEqual(C['chi'],[F(1)]);self.assertEqual(eps,[F(2)])
            self.assertEqual(b.evaluate(model,g,new)[0][0]-b.optimal(model,g)[0][0],2-d)

    def test_original_investment_action_null_identity(self):
        # Exact algebra evaluated over rational states/actions/innovations;
        # the general all-state identity is proved separately in the paper.
        rng=random.Random(9102)
        for d in (2,3,4):
            for _ in range(32):
                x=[F(rng.randrange(33),32) for j in range(d)]
                cap=F(1,8)+sum(x)/(8*d);a=cap*F(rng.randrange(17),16);b_=cap*F(rng.randrange(17),16)
                z=F(rng.randrange(-8,9),256)
                def nxt(u):return [F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16+(F(1,2) if j%2==0 else F(1,4))*u+((-1)**j)*z for j in range(d)]
                ya,yb=nxt(a),nxt(b_)
                self.assertEqual(ya[0]-2*ya[1],yb[0]-2*yb[1])
                for M in (1,16,4096):
                    self.assertEqual(M*max(F(0),ya[0]-2*ya[1]+1),M*max(F(0),yb[0]-2*yb[1]+1))

if __name__=='__main__':unittest.main(verbosity=2)
