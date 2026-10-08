"""Exact-rational regression tests, not economic benchmark observations."""
from fractions import Fraction as F
import random, unittest

def expectation(row, val):
    return sum((p*x for p,x in zip(row,val)), F(0))

def q(model,t,x,a,h):
    c,P,beta=model
    return c[t][x][a]+beta[t]*expectation(P[t][x][a],h)

def evaluate(model,g,pi):
    T=len(pi); J=[None]*(T+1);J[T]=list(g)
    for t in reversed(range(T)):
        J[t]=[q(model,t,x,pi[t][x],J[t+1]) for x in range(len(g))]
    return J

def optimal(model,g):
    T=len(model[0]); V=[None]*(T+1);V[T]=list(g)
    for t in reversed(range(T)):
        V[t]=[min(q(model,t,x,a,V[t+1]) for a in range(len(model[0][t][x]))) for x in range(len(g))]
    return V

def residual_bands(model,g,pi,h):
    T=len(pi);a=[F(0)]*(T+1);b=a.copy()
    e=[u-v for u,v in zip(g,h[T])];a[T],b[T]=min(e),max(e)
    for t in reversed(range(T)):
        e=[q(model,t,x,pi[t][x],h[t+1])-h[t][x] for x in range(len(g))]
        a[t]=min(e)+model[2][t]*a[t+1]
        b[t]=max(e)+model[2][t]*b[t+1]
    return a,b

def improve(model,g,pi,h,zeta=F(0)):
    T=len(pi);a,b=residual_bands(model,g,pi,h);w=[v-u for u,v in zip(a,b)]
    new=[];epsilon=[];accepted=0
    for t in range(T):
        row=[]
        for x in range(len(g)):
            v=min(range(len(model[0][t][x])), key=lambda aa:(q(model,t,x,aa,h[t+1]),aa))
            d=q(model,t,x,v,h[t+1])-q(model,t,x,pi[t][x],h[t+1])
            safe=d+zeta+model[2][t]*w[t+1]<=0
            row.append(v if safe else pi[t][x]);accepted+=int(safe)
        new.append(row);epsilon.append(zeta+2*model[2][t]*w[t+1])
    return new,epsilon,(a,b),accepted

def instance(seed,T,S=3,A=3):
    rng=random.Random(seed)
    c=[[[F(rng.randrange(-8,17),8) for a in range(A)] for x in range(S)] for t in range(T)]
    P=[]
    for t in range(T):
        stage=[]
        for x in range(S):
            row=[]
            for a in range(A):
                counts=[rng.randrange(1,9) for _ in range(S)];n=sum(counts)
                row.append([F(k,n) for k in counts])
            stage.append(row)
        P.append(stage)
    beta=[F(rng.randrange(1,6),5) for _ in range(T)]
    g=[F(rng.randrange(-8,9),4) for _ in range(S)]
    pi=[[rng.randrange(A) for x in range(S)] for t in range(T)]
    return (c,P,beta),g,pi,rng

class ExactSweepTests(unittest.TestCase):
    def test_signed_band_gate_and_recurrence(self):
        accepted=rejected=0
        for seed in range(24):
            T=1+seed%5;model,g,pi,rng=instance(seed,T);V=optimal(model,g)
            for k in range(T+1):
                J=evaluate(model,g,pi)
                h=[[v+F(rng.randrange(-5,6),64) for v in row] for row in J]
                new,eps,(a,b),count=improve(model,g,pi,h,F(1,128))
                accepted+=count;rejected+=T*len(g)-count;K=evaluate(model,g,new)
                for t in range(T+1):
                    for x in range(len(g)):
                        self.assertLessEqual(a[t],J[t][x]-h[t][x]);self.assertLessEqual(J[t][x]-h[t][x],b[t])
                        self.assertLessEqual(K[t][x],J[t][x]);self.assertGreaterEqual(K[t][x],V[t][x])
                    if t<T:
                        err=max(K[t][x]-V[t][x] for x in range(len(g)))
                        nxt=max(J[t+1][x]-V[t+1][x] for x in range(len(g)))
                        self.assertLessEqual(err,model[2][t]*nxt+eps[t])
                        for x in range(len(g)):
                            lhs=q(model,t,x,new[t][x],J[t+1]);rhs=min(q(model,t,x,z,J[t+1]) for z in range(3))+eps[t]
                            self.assertLessEqual(lhs,rhs)
                pi=new
        self.assertGreater(accepted,0);self.assertGreater(rejected,0)

    def test_exact_termination_in_horizon_passes(self):
        for seed in range(18):
            T=1+seed%6;model,g,pi,_=instance(100+seed,T);V=optimal(model,g)
            for k in range(T):
                J=evaluate(model,g,pi);pi,eps,_,_=improve(model,g,pi,J)
                self.assertTrue(all(e==0 for e in eps))
            self.assertEqual(evaluate(model,g,pi),V)

    def test_constant_shift_invariance(self):
        model,g,pi,rng=instance(700,4);J=evaluate(model,g,pi)
        h=[[v+F(rng.randrange(-3,4),16) for v in row] for row in J]
        shifted=[[v+F((t+1)**2,7) for v in row] for t,row in enumerate(h)]
        p,e,_,_=improve(model,g,pi,h);q_,f,_,_=improve(model,g,pi,shifted)
        self.assertEqual(p,q_);self.assertEqual(e,f)

    def test_width_coefficient_two_is_sharp(self):
        model=([[[F(0),F(0)],[F(0),F(0)]]],[[[[F(1),F(0)],[F(0),F(1)]],[[F(1),F(0)],[F(0),F(1)]]]],[F(1)])
        for n in (8,32,128):
            d=F(1,n);g=[F(2),d];pi=[[0,0]];h=[[F(1),F(1)],[F(1),d]]
            new,eps,_,_=improve(model,g,pi,h)
            self.assertEqual(new,pi);self.assertEqual(eps,[F(2)])
            loss=evaluate(model,g,new)[0][0]-optimal(model,g)[0][0]
            self.assertEqual(loss,2-d);self.assertGreater(loss,F(1))

    def test_unrolled_recurrence(self):
        # Exact scalar recurrence attains the claimed diagonally indexed sum.
        T=5;beta=[F(2,3),F(3,4),F(1),F(4,5),F(1,2)]
        eps=[[F(2+k+t,97) for t in range(T)] for k in range(T)]
        E=[[F(3+t,7) for t in range(T)]+[F(0)]]
        for k in range(T):E.append([beta[t]*E[k][t+1]+eps[k][t] for t in range(T)]+[F(0)])
        for t in range(T):
            for m in range(1,T-t+1):
                product=F(1);rhs=F(0)
                for j in range(m):rhs+=product*eps[m-1-j][t+j];product*=beta[t+j]
                rhs+=product*E[0][t+m];self.assertEqual(rhs,E[m][t])

if __name__=='__main__':unittest.main(verbosity=2)
