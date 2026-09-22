"""Finite proof-object checks and explicitly defined welfare normalization.
The proofs are in the paper; these arithmetic tests are not substitutes for
mathematical arguments or formal verification of the stochastic model.
"""
from pathlib import Path
import sys,json,itertools,random
from fractions import Fraction as F
import sympy as S
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from mpfr_interval import I,exp,log,test
Q=I.rational

def pi_checks():
    rng=random.Random(1616);q=F(4,5);checks=0
    for trial in range(8):
        P=[];r=[]
        for state in range(3):
            rr=[];pp=[]
            for action in range(2):
                w=[rng.randint(1,8) for _ in range(3)];pp.append([F(x,sum(w)) for x in w]);rr.append(F(rng.randint(-5,5),3))
            P.append(pp);r.append(rr)
        def value(pol):
            mat=S.eye(3)-S.Rational(q)*S.Matrix([P[i][pol[i]] for i in range(3)]);v=mat.inv()*S.Matrix([r[i][pol[i]] for i in range(3)])
            return [F(x) for x in v]
        policies=list(itertools.product(range(2),repeat=3));vals=[value(p) for p in policies];star=[max(v[i] for v in vals) for i in range(3)]
        for pol,old in zip(policies,vals):
            v=[x+F(rng.randint(-3,3),100) for x in old]
            T=[[r[i][a]+q*sum(P[i][a][j]*v[j] for j in range(3)) for a in range(2)] for i in range(3)]
            eps=max(abs(v[i]-T[i][pol[i]]) for i in range(3));newpol=tuple(max(range(2),key=lambda a:T[i][a]) for i in range(3));new=value(newpol)
            E=max(star[i]-old[i] for i in range(3));En=max(star[i]-new[i] for i in range(3))
            bound=q*E+2*q*eps/(1-q)**2
            assert En<=bound;checks+=1
    return {'status':'PASS','exact_rational_policy_updates':checks,'scope':'finite regression test of the policy-iteration inequality, not its proof'}

def main(root):
    out=root/'results';out.mkdir(exist_ok=True)
    jump=Q('6.45')-Q('.1')*log(Q(2))-Q('25.1')*exp(-Q(8))
    assert jump.lo>Q('6.37').hi
    # Two elementary inequalities used in the analytic lower payoff bound.
    assert F(5,4)**4 < F(6,5)**5
    assert exp(Q('.4')).lo>Q(F(10,7)).hi
    data={'upper_wealth_boundary_jump_lower_interval':jump.pair(),'strict_jump_exceeds':6.37,'kernel_tests':test(),'policy_iteration_regression':pi_checks()}
    for name in ['fresh_library','mpfr_library']:
        p=out/name/'envelope.json'
        if p.exists():
            e=json.loads(p.read_text());eps=I(e['uniform_regret_upper'])
            pexit=2*exp(-Q('.58').square()/(2*Q('.05').square()))
            A=(1-exp(-Q('.04')))/Q('.04')*(1-pexit)
            z=1-Q('1.8')*eps/A
            if z.lo<=0:raise ArithmeticError('Compensation inversion outside domain')
            lam=exp(-log(z)/Q('1.8'))-1
            data[name]={'absolute_regret_upper':float(eps.hi),'expected_discounted_alive_mass_lower':float(A.lo),
              'externally_financed_consumption_topup_fraction_upper':float(lam.hi),
              'percent_upper':float((100*lam).hi),
              'interpretation':'constant proportional consumption top-up financed outside the budget, preference/cost/wealth/stopping path held fixed; not feasible wealth compensation or a neural certificate'}
    (out/'foundation_checks.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
if __name__=='__main__':main(HERE.parent)
