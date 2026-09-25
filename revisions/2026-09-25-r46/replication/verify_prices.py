"""Independent standard-library R46 checker, with primitive and protocol identity.

This reader reconstructs C+lambda*D (rather than the constructor's shifted
C+lambda*(D-epsilon)). It imports no optimizer or certificate constructor.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse,gzip,hashlib,json,time
ZERO=Q(0)
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'revisions/2026-09-25-r44'
R=ROOT/'revisions/2026-09-25-r46'

def expect(condition,message):
    if not condition:raise ValueError(message)

def scalar_product(a,b):
    expect(len(a)==len(b),'inner-product dimension')
    return sum((x*y for x,y in zip(a,b)),ZERO)

class Model:
    def __init__(self,raw):
        self.raw=raw;self.n=int(raw['n']);self.T=int(raw['T']);self.m=int(raw['m'])
        n,T,m=self.n,self.T,self.m
        self.beta=Q(raw['beta']);self.epsilon=Q(raw['epsilon'])
        expect(n>=1 and T>=1 and m>=1 and 0<self.beta<1 and self.epsilon>0,'dimensions/discount/allowance')
        self.P=[[[Q(z) for z in row] for row in state] for state in raw['P']]
        self.reward=[list(map(Q,row)) for row in raw['r']]
        self.cost=[list(map(Q,row)) for row in raw['k']]
        self.terminal=list(map(Q,raw['terminal']));self.initial=list(map(Q,raw['nu']))
        expect(len(self.P)==len(self.reward)==len(self.cost)==len(self.terminal)==len(self.initial)==n,'state dimension')
        expect(min(self.initial)>=0 and sum(self.initial)==1,'initial distribution')
        for i in range(n):
            expect(len(self.P[i])==len(self.reward[i])==len(self.cost[i])==m,'action dimension')
            expect(min(self.cost[i])>=0,'nonnegative implementation cost')
            for row in self.P[i]:expect(len(row)==n and min(row)>=0 and sum(row)==1,'stochastic kernel')
        self.value=[[ZERO]*n for _ in range(T+1)];self.value[T]=self.terminal[:]
        self.disadvantage=[[[ZERO]*m for _ in range(n)] for _ in range(T)]
        self.face_dimension=0
        for t in range(T-1,-1,-1):
            for i in range(n):
                outcomes=[self.reward[i][a]+self.beta*scalar_product(self.P[i][a],self.value[t+1]) for a in range(m)]
                best=max(outcomes);self.value[t][i]=best
                self.disadvantage[t][i]=[best-q for q in outcomes]
                self.face_dimension+=sum(v==best for v in outcomes)-1

    def policy(self,p,require_feasible=True):
        expect(len(p)==self.T,'policy horizon')
        J=self.terminal[:];C=[ZERO]*self.n;maximum=ZERO
        for t in reversed(range(self.T)):
            expect(len(p[t])==self.n,'policy state dimension');nj=[];nc=[]
            for i in range(self.n):
                row=list(map(Q,p[t][i]));expect(len(row)==self.m and min(row)>=0 and sum(row)==1,'policy simplex')
                j=scalar_product(row,[self.reward[i][a]+self.beta*scalar_product(self.P[i][a],J) for a in range(self.m)])
                c=scalar_product(row,[self.cost[i][a]+self.beta*scalar_product(self.P[i][a],C) for a in range(self.m)])
                loss=self.value[t][i]-j
                expect(loss>=0,'nonnegative policy regret')
                if require_feasible:expect(loss<=self.epsilon,'all-restart constraint')
                maximum=max(maximum,loss);nj.append(j);nc.append(c)
            J,C=nj,nc
        return scalar_product(self.initial,C),maximum

    def support(self,prices,bits):
        n,T,m,b,e=self.n,self.T,self.m,self.beta,self.epsilon
        expect(isinstance(bits,int) and 1<=bits<=256,'precision')
        expect(len(prices)==T,'price horizon')
        ls=[list(map(Q,row)) for row in prices]
        expect(all(len(row)==n and min(row)>=0 for row in ls),'nonnegative price field')
        scale=2**bits;shifted=[[ZERO]*n for _ in range(T+1)];W=[[ZERO]*n for _ in range(T+1)]
        checks=0
        for t in reversed(range(T)):
            for i in range(n):
                price=ls[t][i];outcomes=[]
                for a in range(m):
                    future=ZERO
                    if t+1<T:
                        # Negative part of the PRICE CHANGE charges the full
                        # operating allowance. Switching min to max is invalid.
                        future=sum((p*(W[t+1][j]+e*min(ZERO,price-ls[t+1][j])) for j,p in enumerate(self.P[i][a])),ZERO)
                    v=self.cost[i][a]+price*self.disadvantage[t][i][a]+b*future
                    outcomes.append(v);checks+=1
                shifted_value=min(outcomes)-price*e
                rounded=Q((shifted_value.numerator*scale)//shifted_value.denominator,scale)
                shifted[t][i]=rounded;W[t][i]=rounded+price*e
        lower=scalar_product(self.initial,[max(ZERO,z) for z in shifted[0]])
        return lower,shifted,checks

def verify_object(obj,model_path,protocol_path):
    model_bytes=Path(model_path).read_bytes();protocol_bytes=Path(protocol_path).read_bytes()
    raw=json.loads(model_bytes);protocol=json.loads(protocol_bytes)
    expect(obj['schema']=='nbo-r46-restart-prices-v1','schema')
    expect(obj['model']==raw,'model object identity')
    digest=hashlib.sha256(model_bytes).hexdigest()
    expect(obj['model_sha256']==digest,'model hash')
    expect(digest==protocol['models_sha256'][Path(model_path).stem],'registered model hash')
    expect(obj['protocol_sha256']==hashlib.sha256(protocol_bytes).hexdigest(),'protocol hash')
    expect(Q(obj['target'])==Q(protocol['target']),'registered target')
    model=Model(raw);lower,table,checks=model.support(obj['prices'],obj['precision'])
    expect([[Q(v) for v in row] for row in obj['transformed_lower']]==table,'transformed Bellman table')
    expect(Q(obj['lower'])==lower,'lower endpoint')
    upper,regret=model.policy(obj['policy'])
    expect(Q(obj['upper'])==upper and lower<=upper,'upper endpoint/interval')
    return dict(passed=True,lower=str(lower),upper=str(upper),gap=float(upper-lower),relative_gap=float((upper-lower)/upper) if upper else 0.0,target_met=upper-lower<=Q(obj['target']),all_restart_checks=model.T*model.n,bellman_action_checks=checks,max_regret=str(regret),face_dimension=model.face_dimension,model_sha256=digest,protocol_sha256=hashlib.sha256(protocol_bytes).hexdigest())

def verify(path):
    started=time.perf_counter();path=Path(path);obj=json.loads(gzip.decompress(path.read_bytes()))
    result=verify_object(obj,BASE/'models'/f'{path.parent.name}.json',BASE/'PROTOCOL.json')
    result.update(proof_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),seconds=time.perf_counter()-started)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('paths',nargs='*');args=ap.parse_args()
    paths=[Path(p) for p in args.paths] if args.paths else sorted((R/'proofs').glob('*/*.json.gz'))
    results={str(p.relative_to(ROOT)):verify(p) for p in paths}
    summary=dict(passed=all(v['passed'] for v in results.values()),certificates=len(results),results=results)
    (R/'results/independent_prices.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'passed':summary['passed'],'certificates':len(results),'seconds':sum(v['seconds'] for v in results.values())}))
