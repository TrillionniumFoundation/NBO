"""Complete rational spatial search for the common-continuation Markov problem.
No occupation/history relaxation is substituted for the common policy variables.
All reported bounds use Fraction; optional floating-point search is never a certificate.
"""
from fractions import Fraction as F
from pathlib import Path
import heapq,itertools,json,time,resource,hashlib,argparse
Z,O=F(0),F(1)
ROOT=Path(__file__).resolve().parents[1]
def dot(a,b): return sum((x*y for x,y in zip(a,b)),Z)
def encode(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,dict): return {k:encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [encode(v) for v in x]
    return x
def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(encode(obj),sort_keys=True,indent=2)+'\n')
def model(seed,n,T,beta,epsilon):
    """Rational maintenance primitives; seeds only select joint perturbations."""
    import random
    rng=random.Random(seed)
    x=[F(1,5),F(4,5)] if n==2 else [F(1,5),F(1,2),F(1,2),F(4,5)]
    price=F(rng.randrange(11,21),100)
    P=[]
    for a in (0,1):
        rows=[]
        for i in range(n):
            if n==2:
                prob=F((22 if i==0 else 65)+rng.randrange(0,9)+(40 if a else 0),120)
                rows.append([1-prob,prob])
            else:
                ix,iy=divmod(i,2)
                px=F(18+39*ix+7*ix*iy+rng.randrange(0,7)+37*a,120)
                py=F(20+36*iy+5*ix*iy+rng.randrange(0,7)+37*a,120)
                rows.append([(1-px)*(1-py),(1-px)*py,px*(1-py),px*py])
        P.append(rows)
    raw=[0]*n
    nu=[F(1,n)]*n if seed%2 else [F(i+1,n*(n+1)//2) for i in range(n)]
    return dict(seed=seed,n=n,T=T,beta=F(beta),epsilon=F(epsilon),P=P,
                r=[[s-a*price for s in x] for a in (0,1)],
                k=[[Z if a==raw[i] else 1+x[i] for i in range(n)] for a in (0,1)],
                g=[s/2 for s in x],nu=nu,raw=raw,
                model_name='finite maintenance with joint rational perturbations',operation_price=price)

def operating(m):
    n,T,b=m['n'],m['T'],m['beta']; V=[None]*T+[m['g']]
    for t in reversed(range(T)):
        V[t]=[max(m['r'][a][i]+b*dot(m['P'][a][i],V[t+1]) for a in (0,1)) for i in range(n)]
    return V

def evaluate(m,p):
    n,T,b=m['n'],m['T'],m['beta']; J=[None]*T+[m['g']]; C=[None]*T+[[Z]*n]
    for t in reversed(range(T)):
        J[t]=[];C[t]=[]
        for i in range(n):
            v=p[t*n+i]
            J[t].append(sum(((1-v if a==0 else v)*(m['r'][a][i]+b*dot(m['P'][a][i],J[t+1])) for a in (0,1)),Z))
            C[t].append(sum(((1-v if a==0 else v)*(m['k'][a][i]+b*dot(m['P'][a][i],C[t+1])) for a in (0,1)),Z))
    return J,C

def repair(m,V,p):
    n,T,b,e=m['n'],m['T'],m['beta'],m['epsilon']; p=list(p)
    J=[None]*T+[m['g']];C=[None]*T+[[Z]*n]
    for t in reversed(range(T)):
        J[t]=[];C[t]=[]
        for i in range(n):
            qs=[m['r'][a][i]+b*dot(m['P'][a][i],J[t+1]) for a in (0,1)]
            v=p[t*n+i]; value=(1-v)*qs[0]+v*qs[1];target=V[t][i]-e
            if value<target:
                assert max(qs)>=target
                v=(target-qs[0])/(qs[1]-qs[0])
            assert 0<=v<=1
            p[t*n+i]=v;J[t].append((1-v)*qs[0]+v*qs[1])
            C[t].append(sum(((1-v if a==0 else v)*(m['k'][a][i]+b*dot(m['P'][a][i],C[t+1])) for a in (0,1)),Z))
            assert J[t][i]>=target
    return dot(m['nu'],C[0]),p,J,C

def affine_ext(a,c,l,u,upper):
    vl=a+(c-a)*l;vu=a+(c-a)*u
    return max(vl,vu) if upper else min(vl,vu)

def bound(m,V,box):
    """Interval Bellman evaluation, with sound necessary feasibility contraction."""
    n,T,b,e=m['n'],m['T'],m['beta'],m['epsilon']; caps=[list(z) for z in box]
    jl=m['g'];ju=m['g'];cl=[Z]*n;cu=[Z]*n
    for t in reversed(range(T)):
        nlo=[];nhi=[];ncl=[];ncu=[]
        for i in range(n):
            idx=t*n+i;l,u=caps[idx]
            ql=[m['r'][a][i]+b*dot(m['P'][a][i],jl) for a in (0,1)]
            qu=[m['r'][a][i]+b*dot(m['P'][a][i],ju) for a in (0,1)]
            target=V[t][i]-e;d=qu[1]-qu[0]
            if d>0:l=max(l,(target-qu[0])/d)
            elif d<0:u=min(u,(target-qu[0])/d)
            elif qu[0]<target:return None
            if l>u:return None
            caps[idx]=[l,u]
            lo=max(target,affine_ext(*ql,l,u,False));hi=min(V[t][i],affine_ext(*qu,l,u,True))
            if lo>hi:return None
            nlo.append(lo);nhi.append(hi)
            zlo=[m['k'][a][i]+b*dot(m['P'][a][i],cl) for a in (0,1)]
            zhi=[m['k'][a][i]+b*dot(m['P'][a][i],cu) for a in (0,1)]
            ncl.append(affine_ext(*zlo,l,u,False));ncu.append(affine_ext(*zhi,l,u,True))
        jl,ju,cl,cu=nlo,nhi,ncl,ncu
    return dot(m['nu'],cl),caps

def solve(m,budget=256,tolerance=F(1,1000),order='best',record=True,seconds_cap=60):
    assert m['beta']<1 and m['epsilon']>0
    n,T=m['n'],m['T'];V=operating(m);tic=time.perf_counter();serial=itertools.count()
    incumbent=repair(m,V,[Z]*(n*T));nodes=[];heap=[];evaluations=0
    def add(box):
        nonlocal incumbent,evaluations
        idx=len(nodes);node={'box':box};nodes.append(node);evaluations+=1
        res=bound(m,V,box)
        if res is None:node['kind']='infeasible';return idx
        lb,caps=res;node.update(lower=lb,caps=caps)
        cand=repair(m,V,[(l+u)/2 for l,u in caps])
        if cand[0]<incumbent[0]:incumbent=cand
        if lb>=incumbent[0]:node['kind']='pruned'
        else:
            node['kind']='open';key=lb if order=='best' else F(idx)
            heapq.heappush(heap,(key,next(serial),idx))
        return idx
    add([[Z,O] for _ in range(n*T)])
    stop='budget'
    while heap and evaluations+2<=budget:
        if time.perf_counter()-tic>=seconds_cap:stop='time_cap';break
        active=min(nodes[z[2]]['lower'] for z in heap)
        if incumbent[0]-active<=tolerance:stop='gap';break
        _,_,idx=heapq.heappop(heap);node=nodes[idx]
        if node['lower']>=incumbent[0]:node['kind']='pruned';continue
        caps=node['caps'];v=max(range(n*T),key=lambda i:(caps[i][1]-caps[i][0])*m['beta']**(i//n))
        l,u=caps[v]
        if l==u:
            assert node['lower']>=incumbent[0]
        cut=(l+u)/2;left=[z[:] for z in caps];right=[z[:] for z in caps];left[v][1]=cut;right[v][0]=cut
        node.update(kind='split',variable=v,cut=cut,children=[add(left),add(right)])
    # Every leaf is included. Old pruning thresholds dominate the final incumbent.
    leaves=[d['lower'] for d in nodes if d['kind'] in ('open','pruned')]
    lower=min(leaves+[incumbent[0]]);upper,p,J,C=incumbent
    assert lower<=upper
    out=dict(schema='NBO-R39-common-Markov-v1',model=m,V=V,lower=lower,upper=upper,gap=upper-lower,
             relative_gap=(upper-lower)/upper if upper else Z,policy=p,J=J,C=C,nodes=nodes if record else [],
             evaluations=evaluations,node_budget=budget,tolerance=tolerance,closed=upper-lower<=tolerance,
             order=order,stop=stop,seconds_cap=seconds_cap,seconds=time.perf_counter()-tic,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             policy_class='randomized_Markov_common_continuation',constraint='every_time_every_state',
             objective='specified_initial_distribution_discounted_revision_cost')
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--toy',action='store_true');ap.add_argument('--suite',action='store_true');args=ap.parse_args()
    if args.toy:
        for T in (2,4):
            m=model(390001,2,T,'4/5','1/20');o=solve(m,128)
            print(T,float(o['lower']),float(o['upper']),o['evaluations'],o['seconds'],flush=True)
            save(ROOT/'results'/f'toy_T{T}.json',o)
    if args.suite:
        protocol=json.loads((ROOT/'protocol/holdout.json').read_text());rows=[]
        for case in protocol['cases']:
            m=model(**case)
            for order in ('best','breadth'):
                o=solve(m,protocol['node_budget'],F(protocol['tolerance']),order)
                name=f"finite_{case['seed']}_T{case['T']}_{order}.json";save(ROOT/'results/finite'/name,o)
                row={k:v for k,v in o.items() if k not in ('model','V','policy','J','C','nodes')};row.update(case,proof_file='finite/'+name)
                rows.append(row);save(ROOT/'results/finite.json',{'outcomes':rows,'protocol_sha256':hashlib.sha256((ROOT/'protocol/holdout.json').read_bytes()).hexdigest()})
                print(case,order,float(o['lower']),float(o['upper']),o['seconds'],flush=True)
