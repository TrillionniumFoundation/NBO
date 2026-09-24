"""Seeded exact property checks; finite tests are not proofs of all-input correctness."""
from pathlib import Path
from fractions import Fraction as F
import sys,random,json,copy,time,hashlib
from sympy import Rational as Q, Matrix
ROOT=Path(__file__).resolve().parents[1];R39=ROOT.parent/'2026-09-25-r39';R38=ROOT.parent/'2026-09-24-r38'
sys.path[:0]=[str(ROOT/'replication'),str(R39/'replication'),str(R38/'replication')]
import witness_repair as wr
import kernel as k
import verify_primary as vp
from primary_restart import local_value


def independent_values(m,p):
    n,actions,T,beta=m['n'],m['m'],m['T'],Q(str(m['beta']))
    J=[None]*T+[list(map(lambda x:Q(str(x)),m['g']))];C=[None]*T+[[Q(0)]*n]
    for t in range(T-1,-1,-1):
        # Matrix assembly and multiplication deliberately differ from the constructor.
        P=Matrix(n,n,lambda i,j:sum(Q(str(p[t][i][a]))*Q(str(m['P'][a][i][j])) for a in range(actions)))
        r=Matrix([sum(Q(str(p[t][i][a]))*Q(str(m['r'][a][i])) for a in range(actions)) for i in range(n)])
        c=Matrix([sum(Q(str(p[t][i][a]))*Q(str(m['k'][a][i])) for a in range(actions)) for i in range(n)])
        J[t]=list(r+beta*P*Matrix(J[t+1]));C[t]=list(c+beta*P*Matrix(C[t+1]))
    return J,C


def model_tests(rng):
    rows=[];rejected=0
    for case in range(48):
        n=2+case%2;actions=2+(case//2)%2;T=2+case%4;beta=(F(1,2),F(4,5),F(19,20))[case%3];eps=F(1,20)
        P=[]
        for a in range(actions):
            mat=[]
            for i in range(n):
                weights=[rng.randint(1,11) for _ in range(n)];mat.append([F(w,sum(weights)) for w in weights])
            P.append(mat)
        m=dict(n=n,m=actions,T=T,beta=beta,P=P,r=[[F(rng.randint(-10,10),10) for i in range(n)] for a in range(actions)],k=[[F(rng.randint(0,20),10) for i in range(n)] for a in range(actions)],g=[F(rng.randint(-10,10),10) for i in range(n)])
        V=[None]*T+[m['g'][:]]
        for t in range(T-1,-1,-1):V[t]=[max(m['r'][a][i]+beta*sum(P[a][i][j]*V[t+1][j] for j in range(n)) for a in range(actions)) for i in range(n)]
        tau=(1-beta)*eps/4
        h=[tau*sum(beta**s for s in range(T-t)) for t in range(T)]+[F(0)]
        U=[[v+h[t] for v in V[t]] for t in range(T+1)]
        policy=[]
        for t in range(T):
            stage=[]
            for i in range(n):
                weights=[rng.randint(0,10) for _ in range(actions)];weights[0]+=1;stage.append([F(w,sum(weights)) for w in weights])
            policy.append(stage)
        p,J,C,cert=wr.repair(m,U,policy,eps);iJ,iC=independent_values(m,p);oldJ,oldC=independent_values(m,policy)
        assert all(Q(str(J[t][i]))==iJ[t][i] and Q(str(C[t][i]))==iC[t][i] for t in range(T+1) for i in range(n))
        assert all(iJ[t][i]>=Q(str(U[t][i]-eps)) and iJ[t][i]>=oldJ[t][i] for t in range(T) for i in range(n))
        assert all(iC[t][i]-oldC[t][i]<=Q(str(cert['cost_bound'])) for t in range(T) for i in range(n))
        assert cert['defect']==tau
        # Exact-value special case and a deliberately uncertified witness margin.
        wr.repair(m,V,policy,eps)
        bad=[[v+(1-beta)*eps*2*sum(beta**s for s in range(T-t)) for v in V[t]] for t in range(T)]+[m['g'][:]]
        try:wr.repair(m,bad,policy,eps)
        except ValueError:rejected+=1
        else:raise AssertionError('nonpositive repair margin accepted')
        rows.append(dict(case=case,n=n,m=actions,T=T,beta=str(beta),epsilon=str(eps),**{key:str(v) for key,v in cert.items()}))
    return dict(outcomes=rows,passed=True,rejected_nonpositive_slack=rejected,scope='48 designed exact rational property cases; exact V constructs the TEST witness, not an input to the repair routine.')


def pw_tests(rng):
    comparisons=0;rejections=0
    for case in range(200):
        fs=[]
        for _ in range(2):
            xs=[F(0)]+sorted(F(i,32) for i in rng.sample(range(1,32),5))+[F(1)]
            ab=[(F(rng.randint(-20,20),7),F(rng.randint(-20,20),7)) for _ in range(6)]
            ys=[F(rng.randint(-20,20),7) for _ in xs]
            fs.append(k.PW(xs,ab,ys))
        lower,_=k.envelope(fs,maximize=False)
        parsed=[vp.parse(f.dump()) for f in fs];check=vp.parse(lower.dump())
        knots=sorted(set(lower.xs+fs[0].xs+fs[1].xs));points=knots+[(l+r)/2 for l,r in zip(knots,knots[1:])]
        for x in points:
            q=Q(str(x));assert vp.value(check,q)==min(vp.value(f,q) for f in parsed);comparisons+=1
        a,b=F(rng.randint(1,8),16),F(rng.randint(0,8),16)
        pulled=k.compose(lower,a,b);pcheck=vp.parse(pulled.dump());xs=pulled.xs
        for x in xs+[(l+r)/2 for l,r in zip(xs,xs[1:])]:
            assert vp.value(pcheck,Q(str(x)))==vp.value(check,Q(str(a*x+b)));comparisons+=1
        for mode in (0,1):
            bad=copy.deepcopy(fs[0].dump())
            if mode==0:bad['knots'][1]=bad['knots'][0]
            else:bad['points'].pop()
            try:vp.parse(bad)
            except (AssertionError,ValueError,IndexError):rejections+=1
            else:raise AssertionError('malformed partition accepted')
    assert rejections==400
    return dict(pairs=200,comparisons=comparisons,malformed_partition_rejections=rejections,passed=True)


def local_tests(rng):
    ties=boundaries=0
    for case in range(120):
        q=[F(rng.randint(-4,6),3) for _ in range(3)];z=[F(rng.randint(0,20),7) for _ in range(3)]
        if case%3==0:q[1]=q[0]
        b=q[case%3] if case%2==0 else min(q)+(max(q)-min(q))*F(1,3)
        ties+=len(set(q))<3;boundaries+=b in q
        got=local_value(q,z,b);candidates=[]
        for a in range(3):
            if q[a]>=b:candidates.append(Q(str(z[a])))
        # Solve each possible two-variable active basis with SymPy linear algebra.
        for a in range(3):
            for c in range(a+1,3):
                A=Matrix([[1,1],[Q(str(q[a])),Q(str(q[c]))]])
                if A.det()==0:continue
                sol=A.inv()*Matrix([1,Q(str(b))])
                if min(sol)>=0:candidates.append(sol[0]*Q(str(z[a]))+sol[1]*Q(str(z[c])))
        assert Q(str(got))==min(candidates)
    return dict(cases=120,coincident_operating_values=ties,active_pure_boundaries=boundaries,passed=True,scope='Independent active-basis check of the new fixed-partition local LP; not an occurrence count for historical adaptive runs.')


def main():
    if not __debug__:raise RuntimeError('assertions required')
    seed=400925;rng=random.Random(seed);tic=time.perf_counter()
    out=dict(schema='NBO-R40-exact-properties-v1',seed=seed,witness_repair=model_tests(rng),piecewise_affine=pw_tests(rng),local_lp=local_tests(rng),seconds=time.perf_counter()-tic,
      arithmetic='Fraction construction and separate SymPy matrix/value checks; finite adversarial tests do not prove all-input correctness.')
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/property_tests.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v if k!='witness_repair' else {kk:vv for kk,vv in v.items() if kk!='outcomes'} for k,v in out.items()},indent=2))
if __name__=='__main__':main()
