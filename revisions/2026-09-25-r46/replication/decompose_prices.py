"""Exact common-policy price-gap identity, evaluated independently of the LP."""
from pathlib import Path
from fractions import Fraction as Q
import gzip,json
from verify_prices import Model,scalar_product as dot,ZERO as Z,verify,expect
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-25-r46'

def decompose(path):
    verify(path);o=json.loads(gzip.decompress(path.read_bytes()));model=Model(o['model'])
    n,T,m,b,e=model.n,model.T,model.m,model.beta,model.epsilon
    p=[[list(map(Q,row)) for row in period] for period in o['policy']]
    lam=[list(map(Q,row)) for row in o['prices']]+[[Z]*n]
    u=[list(map(Q,row)) for row in o['transformed_lower']]
    D=[[Z]*n for _ in range(T+1)];A=[[Z]*n for _ in range(T+1)];B=[[Z]*n for _ in range(T+1)]
    for t in reversed(range(T)):
        for i in range(n):
            ds=[model.disadvantage[t][i][a]+b*dot(model.P[i][a],D[t+1]) for a in range(m)]
            D[t][i]=dot(p[t][i],ds)
            for a in range(m):
                row=model.P[i][a]
                q=model.cost[i][a]+lam[t][i]*(model.disadvantage[t][i][a]-e)
                q+=b*dot(row,[u[t+1][j]+e*min(lam[t][i],lam[t+1][j]) for j in range(n)])
                action=q-u[t][i];expect(action>=0,'Bellman action slack')
                hinge=[max(Z,lam[t][i]-lam[t+1][j])*D[t+1][j]+max(Z,lam[t+1][j]-lam[t][i])*(e-D[t+1][j]) for j in range(n)]
                expect(min(hinge)>=0,'price-flow hinge slack')
                A[t][i]+=p[t][i][a]*(action+b*dot(row,A[t+1]))
                B[t][i]+=p[t][i][a]*b*(dot(row,hinge)+dot(row,B[t+1]))
    initial=dot(model.initial,[lam[0][i]*(e-D[0][i]) for i in range(n)])
    actions=dot(model.initial,A[0]);flows=dot(model.initial,B[0]);nonnegative=dot(model.initial,[max(Z,-v) for v in u[0]])
    gap=Q(o['upper'])-Q(o['lower'])
    expect(initial+actions+flows-nonnegative==gap,'exact telescoping gap identity')
    return dict(name=Path(path).parent.name,initial_complementarity=str(initial),action_slack=str(actions),price_flow_slack=str(flows),nonnegative_cost_improvement=str(nonnegative),gap=str(gap),gap_float=float(gap),maximum_price=str(max(x for row in lam for x in row)),all_components_nonnegative=True,identity_passed=True)

if __name__=='__main__':
    data=[decompose(p) for p in sorted((R/'proofs').glob('*/restart.json.gz'))]
    (R/'results/price_gap_decomposition.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Exact gap decomposition checked on',len(data),'models.')
