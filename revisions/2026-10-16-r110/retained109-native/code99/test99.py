"""Deterministic exact-rational tests of the R99 constructions (no external packages)."""
from fractions import Fraction as F
import itertools
import json
from math import comb
from pathlib import Path
import unittest
import exact_decision as production
import independent_decision as independent

ROOT = Path(__file__).resolve().parents[1]


def avar(values, weights, alpha):
    if len(values) != len(weights) or any(w < 0 for w in weights) or sum(weights) != 1:
        raise ValueError("probability weights required")
    if not 0 <= alpha < 1:
        raise ValueError("risk level must belong to [0,1)")
    remain = 1-alpha
    total = F(0)
    for value, weight in sorted(zip(values, weights), reverse=True):
        taken = min(remain, weight)
        total += value*taken
        remain -= taken
        if remain == 0:
            return total/(1-alpha)
    raise ArithmeticError("insufficient tail mass")


def integral_power(k, a, b):
    return (b**(k+1)-a**(k+1))/(k+1)


class ExactRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = production.acquisition()
        cls.i = independent.audit()

    def test_independent_acquisition_coefficients(self):
        self.assertEqual(self.p['quadratic_coefficients'], self.i['quadratic_coefficients'])
        self.assertEqual(self.p['quadratic_coefficients'], ['17/15','-3/5','-3/5','1/2','6/5','1/2'])

    def test_independent_policy_cost_integrals(self):
        for key in ['additive_expected_regret','quadratic_expected_regret']:
            self.assertEqual(self.p[key],self.i[key])
        self.assertEqual(self.i['additive_expected_regret'],'1/540')
        self.assertEqual(self.i['quadratic_expected_regret'],'1/5400')

    def test_price_support_and_quadratic_extrema(self):
        self.assertEqual(self.p['quadratic_range'],self.i['quadratic_range'])
        lo, hi = map(F,self.i['quadratic_range'])
        self.assertGreater(lo,0)
        self.assertLess(hi,3)

    def test_exact_price_loss_identity(self):
        for v in [F(1),F(5,4),F(3,2),F(2)]:
            for h in [F(0),F(1,3),F(1),F(5,3),F(2),F(3)]:
                a,b=sorted([h,v])
                integral = abs((b*b-a*a)/2-v*(b-a))/3
                self.assertEqual(integral,(h-v)**2/6)

    def test_normal_equations_and_coefficient_mutation(self):
        self.assertEqual(self.p['normal_equation_residuals'],['0']*6)
        gram=[[F(x) for x in r] for r in self.p['gram']]
        rhs=list(map(F,self.p['rhs']))
        theta=list(map(F,self.p['quadratic_coefficients']))
        theta[4] += F(1,2**30)
        residual=[sum(a*b for a,b in zip(row,theta))-y for row,y in zip(gram,rhs)]
        self.assertTrue(any(residual))
        with self.assertRaises(ValueError): production.solve([[1,1],[1,1]],[0,0])

    def test_triangle_integrator_against_independent_quadrature(self):
        nodes,weights=independent.quadrature()
        for i in range(5):
            for j in range(5-i):
                actual=sum((wx*wt*x*x**i*(1-x+x*t)**j
                            for x,wx in zip(nodes,weights) for t,wt in zip(nodes,weights)),F(0))
                self.assertEqual(actual,production.upper_triangle_moment(i,j))

    def test_equivalent_oblique_geometry(self):
        for x in [F(i,8) for i in range(9)]:
            for y in [F(i,8) for i in range(9)]:
                relu=1+max(F(0),x+y-1)
                triangulation=F(1) if x+y<=1 else x+y
                self.assertEqual(relu,triangulation)
                for price in [F(0),F(1),F(3,2),F(2),F(3)]:
                    self.assertEqual(price<=relu,price<=triangulation)

    def test_constrained_directional_bound(self):
        for a,z,g_hat in itertools.product([F(i,2) for i in range(-2,3)],
                                          [F(-2),F(-3,4),F(0),F(1,4),F(2)],
                                          [F(-1),F(0),F(1)]):
            s=2*(a-z)
            proposal_value=(a-z)**2
            b=min(F(1),max(F(-1),a-s/2))
            gamma=F(1,100)-(s*(b-a)+(b-a)**2)
            optimum=(min(F(1),max(F(-1),z))-z)**2
            self.assertLessEqual(proposal_value-optimum,gamma)
            normal=abs(g_hat)*a if abs(a)==1 else F(0)
            d=abs(s-g_hat); residual=abs(g_hat+normal)
            self.assertLessEqual(gamma,F(1,100)+(d+residual)**2/4)

    def test_smaller_span_can_worsen_decision(self):
        eta=F(1,4)
        self.assertLess(2*eta,1)
        self.assertGreater((-eta/2)**2,0)
        self.assertEqual((-eta/2)**2,F(1,64))

    def test_nonuniform_adaptive_transcript_bound(self):
        # p(z)=1/2+z/4, alpha=3/8, q=0, K=R=L=1.
        for queries in [[],[F(1,2)],[F(1,8),F(7,8)],[F(i,9) for i in range(1,9)]]:
            vertices=[F(0)]+sorted(queries)+[F(1)]
            delta=F(0)
            for a,b in zip(vertices,vertices[1:]):
                # (chord - z^2/2)*p(z), expanded and integrated exactly.
                coeff={0:-a*b/4,1:(a+b)/4-a*b/8,2:F(-1,4)+(a+b)/8,3:F(-1,8)}
                delta += sum((c*integral_power(k,a,b) for k,c in coeff.items()),F(0))/F(5,8)
            n=len(queries)
            lower=F(1,4)/(12*F(5,8)*(n+1)**2)
            self.assertGreaterEqual(delta,lower)
            self.assertGreaterEqual(lower,F(1,4)*F(5,8)/(12*F(3,4)**2*(n+1)**2))

    def test_nonuniform_original_law_enclosure(self):
        # Odd part of p integrates out for v(z)=z^2, giving exact risk below.
        for n,alpha in itertools.product([1,2,4,8],[F(0),F(1,2),F(3,4)]):
            means=[];masses=[];endpoints=[];endweights=[]
            width=F(2,n)
            for i in range(n):
                a=F(-1)+i*width;b=a+width
                mass=(b-a)/2+(b*b-a*a)/8
                mean=((b*b-a*a)/4+(b**3-a**3)/12)/mass
                masses.append(mass);means.append(mean*mean)
                endpoints.extend([a*a,b*b])
                endweights.extend([mass*(b-mean)/width,mass*(mean-a)/width])
            lo=avar(means,masses,alpha);hi=avar(endpoints,endweights,alpha)
            true=(1+alpha+alpha*alpha)/3
            self.assertLessEqual(lo,true);self.assertLessEqual(true,hi)
            self.assertLessEqual(hi-lo,F(3,1)/((1-alpha)*n*n))

    def test_avar_atoms_and_invalid_weights(self):
        self.assertEqual(avar([F(0),F(1)],[F(3,4),F(1,4)],F(1,2)),F(1,2))
        with self.assertRaises(ValueError):avar([F(0)],[F(1,2)],F(0))

    def test_randomized_convex_bump_constants(self):
        for N in [1,2,4,8]:
            K=L=F(1);h=L/(2*N);amplitude=K*h*h/(8*L)
            for sign,u in itertools.product([-1,1],[F(0),F(1,2),F(1)]):
                second=K/(2*L)+sign*amplitude/(h*h)*(2-12*u+12*u*u)
                self.assertGreaterEqual(second,K/(4*L))
            bump_integral=F(1,3)-F(1,2)+F(1,5)
            self.assertEqual(bump_integral,F(1,30))
            beta=amplitude*h*bump_integral/L
            self.assertEqual(beta,K*L/(1920*N**3))
            # Enumerate the conditional variance of N unrevealed signs for small N.
            if N<=4:
                values=[beta*sum(signs) for signs in itertools.product([-1,1],repeat=N)]
                self.assertEqual(sum(v*v for v in values)/len(values),N*beta*beta)

    def test_exact_purchase_boundary(self):
        for fixed,unit in itertools.product([F(0),F(1,10),F(1)],[F(0),F(1,10800)]):
            gain=F(1,5400)-unit
            first=int(fixed//gain)+1
            self.assertGreater(first*gain-fixed,0)
            self.assertLessEqual((first-1)*gain-fixed,0)

    def test_admission_loss_dominates_rejection(self):
        for tau,gamma in itertools.product([F(1,256),F(1,10),F(1)],
                                          [F(0),F(1,256),F(1,64),F(1,10),F(1),F(2)]):
            self.assertLessEqual(int(gamma>tau),min(F(1),gamma/tau))


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ExactRevisionTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'successful':result.wasSuccessful(),'arithmetic':'fractions.Fraction',
            'scope':'New R99 mechanism and algebraic regressions; not the unexecuted R98 campaign.'}
    (ROOT/'results99'/'tests.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
