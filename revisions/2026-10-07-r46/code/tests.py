"""Exact regression checks. Small development economies are not study rows."""
import hashlib,itertools,json,random,unittest
from fractions import Fraction as F
from pathlib import Path
import witness as w


def exact_q(f,x,a,p):
    x=F(x);a=F(a)
    stage=(x-F(11,16))**2+p*a*a+4*a**4+2*max(F(3,8)-x,0)**2
    b=F(1,32)+F(11,16)*x+F(1,16)*x*(1-x)+a
    expectation=(f.exact(b+F(1,32),True)-f.exact(b-F(1,32),True))*16
    return stage+F(15,16)*expectation


class Checks(unittest.TestCase):
    def verify_compilation(self,k,y,L):
        actor=w.compile_witness(k,y,L)
        f=w.old.PWL.from_labels(k,y,L,'min-plus-ReLU')
        points=set(k+list(map(F,actor['cuts']))+[F(i,113) for i in range(114)])
        for x in points:
            j=w.witness_index(actor,x)
            value=y[j]+L*abs(x-k[j])
            self.assertEqual(value,min(y[i]+L*abs(x-k[i]) for i in range(len(k))))
            self.assertEqual(value,f.exact(x))
    def test_01_irregular_noisy_labels(self):
        rng=random.Random(4601)
        for _ in range(30):
            k=[F(0),F(1,7),F(2,5),F(3,4),F(1)]
            y=[F(rng.randrange(-20,20),13) for _ in k]
            self.verify_compilation(k,y,F(9,4))
    def test_02_zero_modulus(self):
        self.verify_compilation([F(0),F(1,2),F(1)],[F(3),F(-1),F(-1)],F(0))
    def test_03_distant_witness(self):
        k=[F(0),F(1,2),F(1)];y=[F(-4),F(1),F(2)]
        actor=w.compile_witness(k,y,F(1))
        self.assertEqual(w.witness_index(actor,F(9,10)),0)
        self.verify_compilation(k,y,F(1))
    def test_04_exact_ties(self):
        self.verify_compilation([F(0),F(1)],[F(0),F(0)],F(1))
    def test_05_unequal_slopes_and_endpoints(self):
        self.verify_compilation([F(0),F(1,3),F(1)],[F(1),F(2,3),F(2)],F(2))
    def test_06_reject_bad_grid(self):
        with self.assertRaises(ValueError):w.compile_witness([0,1,1],[0,0,0],1)
        with self.assertRaises(ValueError):w.compile_witness([0,1],[0,0],-1)
        with self.assertRaises(ValueError):w.witness_index(w.compile_witness([0,1],[0,0],1),F(2))
    def test_07_one_sided_policy_sandwich(self):
        # Exhaustive finite deterministic dynamics; arbitrary signed continuations.
        states=range(3);actions=range(2);beta=F(3,4);T=3
        f=[[F((-1)**(i+t)*(2*i+t+1),7) for i in states] for t in range(T+1)]
        g=[F(i*i,5) for i in states];V=g[:];J=g[:];us=[];ds=[]
        for t in reversed(range(T)):
            q=[[F((i-a)**2+t,9)+beta*f[t+1][(i+a+1)%3] for a in actions] for i in states]
            pi=[(i+t)%2 for i in states]
            us.insert(0,max(f[t][i]-min(q[i]) for i in states))
            ds.insert(0,max(q[i][pi[i]]-f[t][i] for i in states))
            V=[min(F((i-a)**2+t,9)+beta*V[(i+a+1)%3] for a in actions) for i in states]
            J=[F((i-pi[i])**2+t,9)+beta*J[(i+pi[i]+1)%3] for i in states]
        ell=min(f[T][i]-g[i] for i in states);u=max(f[T][i]-g[i] for i in states)
        bound=sum(beta**t*(us[t]+ds[t]) for t in range(T))+beta**T*(u-ell)
        for i in states:
            self.assertLessEqual(J[i]-V[i],bound);self.assertGreaterEqual(J[i]-V[i],0)
    def test_08_date_shift_cancellation(self):
        beta=F(3,4);shift=[F(3,7),F(-8,9),F(5,2)]
        for t in range(2):
            v=shift[t]-beta*shift[t+1]
            self.assertEqual((F(2,9)+v)+(F(-1,7)-v),F(2,9)-F(1,7))
    def test_09_nearest_excess_complete_cells(self):
        for method in ('min-plus-ReLU','piecewise-linear-spline'):
            k=[F(i,4) for i in range(5)];y=[F(1),F(-1,3),F(2),F(0),F(1,2)]
            f=w.old.PWL.from_labels(k,y,F(3),method);D,_=w.nearest_excess(f.payload(),F(3))
            for j in range(401):
                x=F(j,400);i=min(4,int(4*x+F(1,2)))
                self.assertLessEqual(y[i]+3*abs(x-k[i])-f.exact(x),D)
    def test_10_exact_continuous_law_witness(self):
        base,_=w.old.rung(4,2,1,'min-plus-ReLU');new=w.enhance(base,'cone-witness')
        for t in range(2):
            f=w.load_pwl(base['models'][t])
            future=w.load_pwl(base['models'][t+1])
            for j in range(35):
                x=F(j,34);i=w.witness_index(new['policy_actors'][t],x)
                a=F(base['actors'][t][i]);q=exact_q(future,x,a,1)
                self.assertLessEqual(q-f.exact(x),F(base['rows'][t]['oracle_error']))
    def test_11_both_nearest_comparators(self):
        for method,gen in [('cone-nearest','min-plus-ReLU'),('spline-nearest','piecewise-linear-spline')]:
            base,_=w.old.rung(4,2,1,gen);new=w.enhance(base,method)
            for t in range(2):
                f=w.load_pwl(base['models'][t])
                future=w.load_pwl(base['models'][t+1])
                for j in range(35):
                    x=F(j,34);i=min(4,int(4*x+F(1,2)));a=F(base['actors'][t][i])
                    self.assertLessEqual(exact_q(future,x,a,1)-f.exact(x),F(new['joint_rows'][t]['selected_policy_upper']))
    def test_12_approximate_selector_allowance(self):
        k=[F(0),F(1)];y=[F(0),F(1,3)];L=F(2);x=F(1,3)
        cones=[y[i]+L*abs(x-k[i]) for i in range(2)];nu=cones[1]-min(cones)
        self.assertGreaterEqual(nu,0);self.assertEqual(cones[1],min(cones)+nu)
    def test_13_regret_budget_improves_without_old_actor_substitution(self):
        base,_=w.old.rung(4,2,1,'min-plus-ReLU');new=w.enhance(base,'cone-witness')
        self.assertLess(F(new['joint_bound_exact']),F(base['policy_bound_exact']))
        for row in new['joint_rows']:self.assertEqual(F(row['label_witness_excess']),0)
    def test_14_dependency_identity(self):
        expected={'constructive.py':'2555015db7634c6e54639462f55ebae9db5250f30ce41c91b36c0ae85fa3880d',
                  'interval.py':'a18f467743328597478b134fdce265c3a8a1d370687f9bf493a38d31f2c48a02'}
        for name,digest in expected.items():self.assertEqual(hashlib.sha256((w.BASE/'code'/name).read_bytes()).hexdigest(),digest)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    (w.R/'audit').mkdir(exist_ok=True)
    (w.R/'audit/TESTS_R46.json').write_text(json.dumps({'tests':result.testsRun,'success':result.wasSuccessful(),
        'failures':len(result.failures),'errors':len(result.errors),'scope':'exact finite checks and small development economies; not catalogue outcomes'},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
