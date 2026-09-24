"""Common-policy McCormick search; floating LPs only propose rational certificates.
The accepted lower bound is a rational Lagrangian residual bound on a finite box,
not the floating solver objective/status. An LP failure keeps the interval bound.
"""
from common_markov import *
import numpy as np
from scipy.optimize import linprog


def linear_add(*terms):
    out={}
    for multiplier,expr in terms:
        for j,v in expr.items():out[j]=out.get(j,Z)+multiplier*v
    return {j:v for j,v in out.items() if v}


def lp_system(m,V,caps):
    n,T,b=m['n'],m['T'],m['beta'];d=n*T
    # Variables [p, J, C]. Constant terms are indexed by -1 in affine expressions.
    bounds=[tuple(v) for v in caps]
    bounds += [(V[t][i]-m['epsilon'],V[t][i]) for t in range(T) for i in range(n)]
    K=max(z for a in m['k'] for z in a)
    bounds += [(Z,K*sum((b**s for s in range(T-t)),Z)) for t in range(T) for i in range(n)]
    rows=[];rhs=[]
    for t in range(T):
        for i in range(n):
            v=t*n+i;l,u=caps[v]
            for cost,offset in ((False,d),(True,2*d)):
                stage=m['k'] if cost else m['r'];q=[]
                for a in (0,1):
                    expr={-1:stage[a][i]}
                    for j in range(n):
                        if t==T-1:
                            if not cost:expr[-1]+=b*m['P'][a][i][j]*m['g'][j]
                        else:expr[offset+(t+1)*n+j]=b*m['P'][a][i][j]
                    q.append(expr)
                y=linear_add((O,q[1]),(-O,q[0]));z=linear_add((O,{offset+v:O}),(-O,q[0]))
                yl=yu=y.get(-1,Z)
                for j,a in y.items():
                    if j<0:continue
                    lo,hi=bounds[j];yl+=min(a*lo,a*hi);yu+=max(a*lo,a*hi)
                # inequalities e <= 0, generated from the four product envelopes.
                for w,c,sign in ((l,yl,-1),(u,yu,-1),(u,yl,1),(l,yu,1)):
                    e=linear_add((F(sign),z),(-F(sign)*w,y),(-F(sign)*c,{v:O}),
                                 (F(sign)*w*c,{-1:O}))
                    rows.append({j:a for j,a in e.items() if j>=0});rhs.append(-e.get(-1,Z))
    c=[Z]*(3*d)
    for i,w in enumerate(m['nu']):c[2*d+i]=w
    return rows,rhs,bounds,c


def dual_lower(rows,rhs,bounds,c,multipliers):
    """Valid for every nonnegative multiplier, regardless of dual feasibility."""
    assert len(rows)==len(multipliers)
    residual=list(c);constant=Z
    for row,r,lam in zip(rows,rhs,multipliers):
        assert lam>=0
        constant-=lam*r
        for j,a in row.items():residual[j]+=lam*a
    return constant+sum((min(a*l,a*u) for a,(l,u) in zip(residual,bounds)),Z)


def lp_bound(m,V,caps):
    rows,rhs,bounds,c=lp_system(m,V,caps);A=np.zeros((len(rows),len(c)))
    for i,row in enumerate(rows):
        for j,v in row.items():A[i,j]=float(v)
    res=linprog(np.array(c,dtype=float),A_ub=A,b_ub=np.array(rhs,dtype=float),
                bounds=[tuple(map(float,z)) for z in bounds],method='highs',
                options={'time_limit':10.0})
    # Never use a floating infeasibility declaration to remove a policy box.
    if not res.success:return {'status':int(res.status),'message':res.message},None,None
    lam=[max(Z,F(float(-v)).limit_denominator(2**24)) for v in res.ineqlin.marginals]
    lower=dual_lower(rows,rhs,bounds,c,lam)
    p=[min(u,max(l,F(float(x)).limit_denominator(2**20)))
       for x,(l,u) in zip(res.x[:len(caps)],caps)]
    return {'status':0,'multipliers':lam,'lower':lower,'solver_objective':float(res.fun)},lower,p


def solve_lp(m,budget=512,tolerance=F(1,1000),seconds_cap=60,record=True):
    n,T=m['n'],m['T'];V=operating(m);tic=time.perf_counter();serial=itertools.count()
    incumbent=repair(m,V,[Z]*(n*T));nodes=[];heap=[];evaluations=0;failures=0;lp_calls=0
    def add(box):
        nonlocal incumbent,evaluations,failures,lp_calls
        idx=len(nodes);node={'box':box};nodes.append(node);evaluations+=1
        res=bound(m,V,box)
        if res is None:node['kind']='infeasible';return idx
        ilb,caps=res;node.update(interval_lower=ilb,caps=caps)
        cand=repair(m,V,[(l+u)/2 for l,u in caps])
        if cand[0]<incumbent[0]:incumbent=cand
        certificate,lb,p=lp_bound(m,V,caps);lp_calls+=1;node['lp']=certificate
        if lb is None:failures+=1;lb=ilb
        else:
            lb=max(lb,ilb)
            cand=repair(m,V,p)
            if cand[0]<incumbent[0]:incumbent=cand
        node['lower']=lb
        if lb>=incumbent[0]:node['kind']='pruned'
        else:node['kind']='open';heapq.heappush(heap,(lb,next(serial),idx))
        return idx
    add([[Z,O] for _ in range(n*T)])
    stop='budget'
    while heap and evaluations+2<=budget:
        if time.perf_counter()-tic>=seconds_cap:stop='time_cap';break
        if incumbent[0]-heap[0][0]<=tolerance:stop='gap';break
        _,_,idx=heapq.heappop(heap);node=nodes[idx]
        if node['lower']>=incumbent[0]:node['kind']='pruned';continue
        caps=node['caps'];v=max(range(n*T),key=lambda i:(caps[i][1]-caps[i][0])*m['beta']**(i//n))
        l,u=caps[v]
        if l==u:
            assert node['lower']>=incumbent[0]
        cut=(l+u)/2;left=[z[:] for z in caps];right=[z[:] for z in caps];left[v][1]=cut;right[v][0]=cut
        node.update(kind='split',variable=v,cut=cut,children=[add(left),add(right)])
    leaves=[d['lower'] for d in nodes if d['kind'] in ('open','pruned')]
    lower=min(leaves+[incumbent[0]]);upper,p,J,C=incumbent
    assert lower<=upper
    return dict(schema='NBO-R39-verified-McCormick-v1',model=m,V=V,lower=lower,upper=upper,gap=upper-lower,
       relative_gap=(upper-lower)/upper if upper else Z,policy=p,J=J,C=C,nodes=nodes if record else [],
       evaluations=evaluations,node_budget=budget,seconds_cap=seconds_cap,tolerance=tolerance,closed=upper-lower<=tolerance,
       order='verified_McCormick',seconds=time.perf_counter()-tic,stop=stop,lp_failures=failures,lp_calls=lp_calls,
       peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       policy_class='randomized_Markov_common_continuation',constraint='every_time_every_state',
       objective='specified_initial_distribution_discounted_revision_cost')

if __name__=='__main__':
    for T in (2,4,8):
        m=model(390001,2,T,'4/5','1/20');o=solve_lp(m,256,seconds_cap=20)
        print(T,float(o['lower']),float(o['upper']),float(o['relative_gap']),o['evaluations'],o['seconds'],flush=True)
        save(ROOT/'results'/f'toy_lp_T{T}.json',o)
