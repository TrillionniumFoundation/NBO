"""Independent exact-arithmetic and implementation regressions; not cost data."""
import itertools, math, unittest
from fractions import Fraction as F
import numpy as np
import directed53 as d

class DirectedTests(unittest.TestCase):
    def test_mutable_endpoint_independence(self):
        x=d.zero(2);x.lo[0]=-1;x.hi[0]=2
        self.assertEqual(x.lo[0],-1);self.assertEqual(x.hi[0],2)
    def test_all_rectangle_extrema(self):
        n=8;rng=np.random.default_rng(53);a=rng.integers(0,1025,(n,n));actor=d.RectangleActor(a,3)
        for i,j,k,l in itertools.product(range(n),repeat=4):
            if k<i or l<j:continue
            x=d.I([[i/n,j/n]],[[(k+.5)/n,(l+.5)/n]])
            v=actor.action(x)
            self.assertEqual(v.lo[0]*4096,a[i:k+1,j:l+1].min())
            self.assertEqual(v.hi[0]*4096,a[i:k+1,j:l+1].max())
    def test_relu_difference(self):
        for a,b in itertools.product(range(-8,9),repeat=2):
            x=d.I([a/8-.125],[a/8+.125]);y=d.I([b/8-.125],[b/8+.125]);delta=x-y
            v=d.positive_difference(x,y,delta)
            z=max(0,F(a,8))-max(0,F(b,8))
            self.assertLessEqual(F(v.lo[0]),z);self.assertGreaterEqual(F(v.hi[0]),z)
    def test_exact_last_pair(self):
        rng=np.random.default_rng(5301)
        for _ in range(100):
            x=list(map(lambda z:F(int(z),32),rng.integers(0,33,2)))
            y=list(map(lambda z:F(int(z),32),rng.integers(0,33,2)))
            a=F(int(rng.integers(0,513)),4096);b=F(int(rng.integers(0,513)),4096)
            xi=d.I.point([list(map(float,x))]);yi=d.I.point([list(map(float,y))])
            v=d.last_pair(xi,yi,xi-yi,d.I.point([float(a)]),d.I.point([float(b)]),1)
            exact=d.o.exact_q(x,a,1)-d.o.exact_q(y,b,1)
            self.assertLessEqual(F(v.lo[0]),exact);self.assertGreaterEqual(F(v.hi[0]),exact)
    def test_terminal_equals_retained_centered_formula(self):
        bins=np.array(list(itertools.product(range(4),repeat=2)));x=d.I(bins/4,(bins+1)/4)
        a=d.I.point(np.full(16,.0625));b=d.I.point(np.full(16,.125))
        engine=d.PairCertificate(np.zeros((2,4,4),dtype=int),2,2)
        v=engine.contrast(1,x,a,b);old=d.o.final_difference(x,a,b,1)
        self.assertTrue(np.all(v.lo<=old.hi));self.assertTrue(np.all(old.lo<=v.hi))
    def test_identity_is_exact(self):
        a=np.full((3,4,4),256,dtype=int);engine=d.PairCertificate(a,2,2)
        v=engine.contrast(0,d.I([[0.,0.]],[[.25,.25]]),d.I.point([.0625]),d.I.point([.0625]))
        self.assertEqual(v.lo[0],0);self.assertEqual(v.hi[0],0)
        self.assertEqual(engine.counts['pair_nodes'],0)
    def test_directed_selector_exact_finite_arrays(self):
        rng=np.random.default_rng(53)
        for _ in range(500):
            q=rng.integers(-50,51,7);q[0]=0
            low=q-rng.integers(0,10,7);high=q+rng.integers(0,10,7);low[0]=high[0]=0
            v=int(np.argmin(high));epsilon=int(high[v]-low.min())
            self.assertLessEqual(q[v],0);self.assertLessEqual(q[v]-q.min(),epsilon)
    def test_directed_full_sweeps_exact_finite_model(self):
        rng=np.random.default_rng(531)
        for T in range(1,5):
            costs=rng.integers(-5,6,(T,4,3));dest=rng.integers(0,4,(T,4,3));g=rng.integers(0,5,4)
            opt=[None]*T+[g]
            for t in range(T-1,-1,-1):opt[t]=(costs[t]+opt[t+1][dest[t]]).min(axis=1)
            pol=np.zeros((T,4),int)
            def evaluate(pp):
                vv=[None]*T+[g]
                for tt in range(T-1,-1,-1):vv[tt]=costs[tt,np.arange(4),pp[tt]]+vv[tt+1][dest[tt,np.arange(4),pp[tt]]]
                return vv
            for _ in range(T):
                vv=evaluate(pol);new=pol.copy()
                for t in range(T):
                    q=costs[t]+vv[t+1][dest[t]];new[t]=q.argmin(axis=1)
                nxt=evaluate(new)
                for t in range(T):self.assertTrue(np.all(nxt[t]<=vv[t]))
                pol=new
            for a,b in zip(evaluate(pol),opt):self.assertTrue(np.array_equal(a,b))
    def test_toy_continuous_all_date_passes(self):
        pol=np.full((2,4,4),128,dtype=int)
        for _ in range(2):
            new,j,raw=d.sweep(pol,2,2)
            self.assertEqual(len(j['dates']),2)
            for t in range(2):
                self.assertTrue(np.all(raw[f't{t}_accepted_upper']<=0))
                self.assertTrue(np.all(raw[f't{t}_continuous_inf_lower']<=raw[f't{t}_accepted_upper']))
                self.assertTrue(np.all(raw[f't{t}_greedy_gap_upper']>=0))
            pol=new
    def test_approximate_null_exact_bound(self):
        # F1-2 F2 loses nullity by exactly -eta a/4. ReLU is 1-Lipschitz.
        for M,eta,a,b in itertools.product((1,16,4096),(F(0),F(1,4096),F(1,256),F(1,16)),(F(0),F(1,16),F(1,8)),(F(0),F(1,16),F(1,8))):
            gamma=F(1,2)-(2+eta)*F(1,4)
            self.assertEqual(abs(M*gamma*(a-b)),M*eta*abs(a-b)/4)
    def test_false_null_is_unsafe_in_original_economy(self):
        x=[F(0),F(0)];a=F(0);b=F(1,8);M=4096;eta=F(1,16)
        true=d.o.exact_q(x,a,1)-d.o.exact_q(x,b,1)
        nuisance_difference=M*(-eta/4)*(a-b)
        critic=true-d.BETA*nuisance_difference
        self.assertGreater(true,0);self.assertLess(critic,0)
        self.assertGreaterEqual(critic+d.BETA*abs(nuisance_difference),true)
    def test_exposure_uncertainty_bound(self):
        for eta,ex1,ex2 in itertools.product((F(0),F(1,16)),(F(-1,64),F(1,64)),(F(-1,128),F(1,128))):
            slope=(F(1,2)+ex1)-(2+eta)*(F(1,4)+ex2)
            bound=eta/4+abs(ex1)+(2+eta)*abs(ex2)
            self.assertLessEqual(abs(slope),bound)
    def test_negative_path_gains_are_not_clipped(self):
        import study53 as study
        x=np.tile(np.array([-1.,2.]),100)
        r=study.interval_record(x,x,F(-3),F(3))
        self.assertEqual(r['support_exact'],['-3','3'])
        self.assertLessEqual(F(r['lower_endpoint_moments']['mean_lo']),F(1,2))
        self.assertGreaterEqual(F(r['upper_endpoint_moments']['mean_hi']),F(1,2))
    def test_confidence_family_log(self):
        lower=sum((F(13)**j/math.factorial(j) for j in range(41)),F(0))
        self.assertGreater(lower,4*128/F(1,100))

if __name__=='__main__':unittest.main(verbosity=2)
