"""Exact regressions for R73 mathematics and numerical contracts.
Finite diagnostic models here are tests, not replacement economic experiments.
"""
from fractions import Fraction as F
from decimal import Decimal,localcontext
from itertools import product
from pathlib import Path
import copy,random,sys,unittest
from qualification73 import Problem,solve,simplex,dot
from sequential73 import Ledger,Qualification,log_upper
import study73 as s

class ReadoutTests(unittest.TestCase):
    def fixture(self):
        return Problem(((F(1),F(0)),(F(1),F(1))),(F(0),F(1)),(F(0),F(1)),(F(0),F(1)),(F(2),F(1)),F(1,8),F(1))
    def test_exact_primal_dual_optimum(self):
        p=self.fixture();r=p.verify((F(0),F(1)),(F(0),F(1)),(F(1),F(0)))
        self.assertEqual(r['objective'],F(1,2));self.assertEqual(r['optimization_gap'],0)
    def test_solver_proposal_checked_exactly(self):
        r=solve(self.fixture(),28);self.assertLessEqual(r['optimization_gap'],F(1,65536));self.assertEqual(r['objective'],F(1,2))
    def test_any_simplex_is_valid_weak_dual(self):
        p=self.fixture();rng=random.Random(73)
        for _ in range(128):
            a,b=F(rng.randrange(129),128),F(rng.randrange(129),128)
            theta=(F(rng.randrange(-32,33),16),F(rng.randrange(-16,17),16))
            self.assertGreaterEqual(p.verify(theta,(a,1-a),(b,1-b))['optimization_gap'],0)
    def test_invalid_dual_is_not_repaired_silently(self):
        with self.assertRaises(ValueError):self.fixture().dual((F(1),F(1)),(F(1),F(0)))
    def test_outside_coefficient_box_rejected(self):
        with self.assertRaises(ValueError):self.fixture().primal((F(0),F(2)))
    def test_constant_gauge_invariance(self):
        p=self.fixture();self.assertEqual(p.primal((F(0),F(1)))['objective'],p.primal((F(2),F(1)))['objective'])
    def test_interval_width_cannot_disappear(self):
        p=Problem(((F(1),),),(F(-1),),(F(2),),(F(0),),(F(8),),F(0),F(0))
        self.assertEqual(p.primal((F(7),))['objective'],3);self.assertEqual(p.dual((F(1),),(F(1),)),3)
    def test_whole_cover_encloses_quadratic_residual(self):
        n=8;xs=[F(2*j+1,2*n) for j in range(n)]
        p=Problem(tuple((F(1),x) for x in xs),tuple(x*x for x in xs),tuple(x*x for x in xs),(F(0),F(1)),(F(2),F(2)),F(1,2*n),F(2))
        r=p.primal((F(1,4),F(-3,2)))
        for j in range(257):
            x=F(j,256);value=x*x-F(1,4)+F(3,2)*x
            self.assertLessEqual(r['residual_lower'],value);self.assertLessEqual(value,r['residual_upper'])
    def test_rational_simplex(self):
        p=simplex([-.001,.2,.8],28);self.assertEqual(sum(p),1);self.assertGreaterEqual(min(p),0)
    def test_problem_rejects_inverted_interval(self):
        with self.assertRaises(ValueError):Problem(((F(1),),),(F(1),),(F(0),),(F(0),),(F(8),),F(0),F(0))

class SequentialTests(unittest.TestCase):
    def test_rational_logarithm_upper(self):
        with localcontext() as ctx:
            ctx.prec=90
            for x in (F(1),F(2),F(3,2),F(400),F(1234567,3)):
                r=log_upper(x);v=(Decimal(x.numerator)/Decimal(x.denominator)).ln()
                got=Decimal(r.numerator)/Decimal(r.denominator)
                self.assertGreaterEqual(got,v);self.assertLess(got-v,Decimal('1e-19'))
    def test_support_must_precede_endpoint(self):
        with self.assertRaises(RuntimeError):Ledger().include(F(0),F(0))
    def test_pending_episode_cannot_be_skipped(self):
        l=Ledger();l.reserve(Qualification('pair','h',F(-1),F(1)))
        with self.assertRaises(RuntimeError):l.reserve(Qualification('pair','h2',F(-1),F(1)))
        with self.assertRaises(RuntimeError):l.interval()
    def test_failed_numeric_row_remains_counted(self):
        l=Ledger();l.reserve(Qualification('pair','h',F(-2),F(3)));l.include(None,None,F(7))
        self.assertEqual(l.interval(),(F(-2),F(3)));self.assertEqual(l.failed_numerical_rows,1);self.assertEqual(l.work,7)
    def test_invalid_support_intersection_stops(self):
        l=Ledger();l.reserve(Qualification('pair','h',F(0),F(1)))
        with self.assertRaises(ValueError):l.include(F(2),F(3))
        self.assertEqual(l.n,0);self.assertIsNotNone(l.pending)
    def test_changed_target_rejected_in_fixed_mode(self):
        l=Ledger();l.reserve(Qualification('a','h',F(0),F(0)));l.include(F(0),F(0))
        with self.assertRaises(ValueError):l.reserve(Qualification('b','h',F(0),F(1)))
    def test_predictable_critic_change_preserves_target(self):
        l=Ledger()
        for i in range(4):
            l.reserve(Qualification('same-pair',str(i),F(-1),F(1)));l.include(F(0),F(0))
        self.assertEqual(l.n,4);self.assertLessEqual(l.interval()[0],0);self.assertGreaterEqual(l.interval()[1],0)
    def test_varying_mean_is_not_last_policy_mean(self):
        l=Ledger(fixed_target=False)
        for i,v in enumerate((F(-1),F(1))):
            l.reserve(Qualification(str(i),'h',v,v));l.include(v,v)
        self.assertEqual(l.interval(),(F(0),F(0)))
        with self.assertRaises(ValueError):l.decision(F(1,16))
    def test_setup_amortization_uses_deployments_not_samples(self):
        l=Ledger();l.reserve(Qualification('p','h',F(-1,8),F(-1,8)));l.include(F(-1,8),F(-1,8))
        self.assertFalse(l.decision(F(0),F(1),4)['net_strict_improvement'])
        self.assertTrue(l.decision(F(0),F(1),16)['net_strict_improvement'])
    def test_invalid_error_and_work_allocations(self):
        with self.assertRaises(ValueError):Ledger(alpha=F(0))
        with self.assertRaises(ValueError):Ledger(weights=[F(2)],lambdas=[F(1)])
        l=Ledger();l.reserve(Qualification('p','h',F(0),F(1)))
        with self.assertRaises(ValueError):l.include(F(0),F(1),F(-1))
    def test_whole_adaptive_tree_time_uniform_coverage(self):
        # Outcome-dependent range and Bernoulli law; all histories are included.
        alpha=F(1,4);lambdas=(F(1),F(2));weights=(F(1,2),F(1,2))
        constants=[log_upper(2/(alpha*w)) for w in weights];bad_probability=F(0)
        frontier=[(F(1),F(0),F(0),F(0),0,False)]
        for i in range(12):
            nxt=[]
            for probability,total,means,variance,ones,bad in frontier:
                width=F(1) if ones%2==0 else F(1,2);p=F(1,4) if ones%3==0 else F(3,4)
                for bit in (0,1):
                    mass=probability*(p if bit else 1-p);v=width*(bit-F(1,2));mu=width*(p-F(1,2));V=variance+width*width
                    boundary=min(c/lam+lam*V/8 for c,lam in zip(constants,lambdas))
                    crossed=bad or abs(total+v-means-mu)>boundary
                    nxt.append((mass,total+v,means+mu,V,ones+bit,crossed))
            frontier=nxt
        bad_probability=sum((r[0] for r in frontier if r[-1]),F(0))
        self.assertEqual(sum(r[0] for r in frontier),1);self.assertLessEqual(bad_probability,alpha)
    def test_terminal_correction_and_predictable_gauge(self):
        # Two-state, two-date exact diagnostic; arbitrary fitted terminal values.
        beta=F(3,4);g=(F(1,8),F(3,4))
        def c(t,x,a):return F(1+t+2*x+a,8)
        def kernel(a):return (F(3-a,4),F(1+a,4))
        def J(a):
            v=list(g)
            for t in (1,0):v=[c(t,x,a)+beta*dot(kernel(a),v) for x in (0,1)]
            return sum(v)/2
        for history in range(8):
            h=[(F(history+t,3),F(history-t,5)) for t in range(3)]
            means=[]
            for a in (0,1):
                total=F(0)
                for x0,x1,x2 in product((0,1),repeat=3):
                    mass=F(1,2)*kernel(a)[x1]*kernel(a)[x2];xs=(x0,x1,x2)
                    z=sum((beta**t*(c(t,xs[t],a)+beta*dot(kernel(a),h[t+1])-h[t][xs[t]]) for t in (0,1)),F(0))+beta**2*(g[x2]-h[2][x2])
                    total+=mass*z
                means.append(total)
            self.assertEqual(means[0]-means[1],J(0)-J(1))

class OriginalPrimitiveTests(unittest.TestCase):
    def test_original_terminal_primitive_identity(self):
        base=Path(__file__).resolve().parents[2]/'2026-10-10-r62/code'
        sys.path.insert(0,str(base));import operators50 as o
        for i,j,k in product(range(3),repeat=3):
            x=(F(i,2),F(j,2));a=s.capacity(x)*k/2
            self.assertEqual(s.qvalue(x,a,None,'relu'),o.exact_q(x,a,1))
    def test_basis_moduli_and_cardinality(self):
        for kind in ('relu','bernstein'):
            for i in range(17):
                x=(F(i,16),F(16-i,16));y=(F(i,32),F(1,4));f=s.features(x,kind);g=s.features(y,kind)
                self.assertEqual(len(f),9);D=sum(abs(a-b) for a,b in zip(x,y));L=1 if kind=='relu' else 4
                self.assertTrue(all(abs(a-b)<=L*D for a,b in zip(f,g)))
    def test_bernstein_exact_moments_independent_boole_rule(self):
        weights=(7,32,12,32,7)
        for i,j,k in product(range(3),repeat=3):
            x=(F(i,2),F(j,2));a=s.capacity(x)*k/2;y=s.deterministic_next(x,a)
            values=[s.features((y[0]+F(z,64),y[1]-F(z,64)),'bernstein') for z in (-2,-1,0,1,2)]
            independent=tuple(sum(F(w,90)*row[c] for w,row in zip(weights,values)) for c in range(9))
            self.assertEqual(s.feature_means(x,a,'bernstein'),independent)
    def test_transition_invariance(self):
        for i,j,k,z in product(range(3),range(3),range(3),(-1,1)):
            x=(F(i,2),F(j,2));a=s.capacity(x)*k/2;y=s.deterministic_next(x,a)
            self.assertTrue(all(0<=v+F(z*sign,32)<=1 for v,sign in zip(y,(1,-1))))

if __name__=='__main__':unittest.main(verbosity=2)
