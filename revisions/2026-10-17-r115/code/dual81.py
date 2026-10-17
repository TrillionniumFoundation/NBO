"""Independent exact action-switch verifier and optimizer-class cost transfer.

No imports from the R80 LP, derivative-control or feature-integration code.
Frozen LP multipliers are checked, not regenerated. All powers are integrated
by antiderivatives, independently of the earlier even-moment implementation.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,itertools,json,math,time
R=Path(__file__).resolve().parents[1]
H=F(21097,4096)

def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    return x

def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(encode(x),sort_keys=True,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dot(x,y):
    if len(x)!=len(y):raise ValueError('Dot-product dimension')
    return sum((a*b for a,b in zip(x,y)),F(0))
def slopes(kind):
    out=[]
    for axis in range(2):
        for j in range(4):
            row=[F(0)]*9
            for k in range(4):
                if kind=='relu':row[1+4*axis+k]=F(k<=j)
                elif kind=='bernstein':row[1+4*axis+k]=F(4*(k==j)-4*(j>0 and k==j-1))
                else:raise ValueError(kind)
            out.append(tuple(row))
    return tuple(out)

def mean_power(lo,hi,p):
    if not lo<hi or p<0:raise ValueError('Integration interval')
    return (hi**(p+1)-lo**(p+1))/((p+1)*(hi-lo))
def means(x,a,kind):
    out=[F(1)]
    for j in range(2):
        other=x[1-j]
        center=F(1,16)+x[j]/2+other/8+x[j]*(1-other)/16+(F(1,2) if j==0 else F(1,4))*a
        lo,hi=center-F(1,32),center+F(1,32)
        if kind=='relu':
            for k in range(4):
                knot=F(k,4)
                out.append((max(F(0),hi-knot)**2-max(F(0),lo-knot)**2)/(2*(hi-lo)))
        elif kind=='bernstein':
            for k in range(1,5):
                out.append(math.comb(4,k)*sum(((-1)**l*math.comb(4-k,l)*mean_power(lo,hi,k+l) for l in range(5-k)),F(0)))
        else:raise ValueError(kind)
    return tuple(out)
def action_contrast(x,a,b,kind):
    A=means(x,a,kind);B=means(x,b,kind)
    return tuple(F(15,16)*(v-u) for u,v in zip(A,B)),b*b-a*a+4*(b**4-a**4)

def probability(raw,n):
    out={}
    for i,v in raw:
        if not isinstance(i,int) or i<0 or i>=n or i in out:raise ValueError('Sparse probability index')
        out[i]=F(v)
    if any(v<0 for v in out.values()) or sum(out.values(),F(0))!=1:raise ValueError('Probability normalization')
    return out

def lower_bound(problem,p,q,xi,nu,d,c,kind):
    features,yl,yu,bounds,rho,G=problem
    p=probability(p,len(yl));q=probability(q,len(yl));xi=tuple(map(F,xi));nu=F(nu)
    if len(xi)!=16 or any(v<0 for v in xi) or nu<0 or sum(xi)>2*rho:raise ValueError('Exact dual feasibility')
    rows=slopes(kind);g=[F(0)]*9
    for i,w in q.items():
        for k in range(9):g[k]+=w*features[i][k]
    for i,w in p.items():
        for k in range(9):g[k]-=w*features[i][k]
    for j,row in enumerate(rows):
        for k in range(9):g[k]+=(xi[2*j]-xi[2*j+1])*row[k]
    for k in range(9):g[k]+=nu*d[k]
    return sum((w*yu[i] for i,w in p.items()),F(0))-sum((w*yl[i] for i,w in q.items()),F(0))+2*rho*G+nu*c-dot(bounds,tuple(abs(v) for v in g))

def robust_band(pair,radius_a,radius_b):
    if radius_a<0 or radius_b<0:raise ValueError('Negative cost radius')
    lo,hi=map(F,pair)
    if lo>hi:raise ValueError('Reversed band')
    return lo-radius_a-radius_b,hi+radius_a+radius_b

def verify_service(n,kind):
    source=R/'results80/construction'/f'{kind}-n{n}/service.json'
    rec=json.loads(source.read_text());barrier=R/'results80/barriers'/f'{kind}-n{n}.json'
    raw=json.loads(barrier.read_text());stage=rec['stages'][1];data=stage['problem'];fit=stage['attained']
    features=tuple(tuple(map(F,row)) for row in data['features']);yl=tuple(map(F,data['lower']));yu=tuple(map(F,data['upper']))
    bounds=tuple(map(F,data['bounds']));rho=F(data['radius']);G=F(data['bellman_lipschitz']);problem=(features,yl,yu,bounds,rho,G)
    theta=tuple(map(F,fit['theta']));rows=slopes(kind)
    if tuple(tuple(map(F,v)) for v in stage['derivative_control_rows'])!=rows:raise AssertionError('Independent derivative controls')
    if any(abs(t)>b for t,b in zip(theta,bounds)):raise AssertionError('Reference coefficient feasibility')
    residual_lower=min(l-dot(f,theta) for l,f in zip(yl,features));residual_upper=max(u-dot(f,theta) for u,f in zip(yu,features))
    objective=residual_upper-residual_lower+2*rho*(G+max(abs(dot(row,theta)) for row in rows))
    if objective!=F(fit['objective']):raise AssertionError('Independent reference objective')
    if sha(source)!=raw['summary']['source_sha256']:raise AssertionError('Barrier source binding')
    reference=tuple(map(F,rec['stages'][0]['data']['actions']));cell_lowers=[];pos=0
    for i,j in itertools.product(range(n),repeat=2):
        x=(F(2*i+1,2*n),F(2*j+1,2*n));cap=math.floor((F(1,8)+F(i+j,16*n))*4096)
        menu=tuple(F((cap*k)//32,4096) for k in range(33));a=reference[i*n+j]
        if a not in menu:raise AssertionError('Robust reference menu')
        lower=[]
        for b in menu:
            if b==a:continue
            row=raw['records'][pos]
            if row['cell']!=[i,j] or F(row['reference'])!=a or F(row['competitor'])!=b:raise AssertionError('Complete ordered switch enumeration')
            d,c=action_contrast(x,a,b,kind)
            if c+dot(d,theta)<0:raise AssertionError('Independent reference greediness')
            v=lower_bound(problem,row['p'],row['q'],row['xi'],row['nu'],d,c,kind)
            if v!=F(row['lower']):raise AssertionError('Independent switch lower bound')
            lower.append(v);pos+=1
        if len(lower)!=32:raise AssertionError('Missing alternative')
        cell_lowers.append(min(lower))
    if pos!=len(raw['records']):raise AssertionError('Unexpected saved alternatives')
    surplus=min(cell_lowers)-objective
    if surplus!=F(raw['summary']['global_action_preserving_surplus']):raise AssertionError('Minimum surplus')
    safe=None
    if surplus>0:
        safe=F(1)
        while safe>=surplus:safe/=2
    tolerances=(F(0),F(1,65536),F(1,4096))
    table=[]
    for epsilon in tolerances:
        good=sum(v>objective+epsilon for v in cell_lowers);qbad=F(n*n-good,n*n)
        if good!=raw['summary']['certified_cells_by_optimization_tolerance'][str(epsilon)]:raise AssertionError('Sublevel coverage count')
        table.append(dict(extra_objective=epsilon,certified_cells=good,uncertified_initial_mass=qbad,cost_radius=H*qbad))
    if safe is not None and not all(v>objective+safe for v in cell_lowers):raise AssertionError('Uniform dyadic allowance')
    return dict(name=f'calibrated-{kind}-n{n}',n=n,basis=kind,switches=pos,reference_objective=objective,
        global_surplus=surplus,uniform_dyadic_allowance=safe,all_exact_minimizers_same_policy=surplus>0,
        sublevel_bounds=table,cell_switch_lowers=cell_lowers,source_sha256=sha(source),barrier_sha256=sha(barrier))

def pair_record(results,a,b):
    key=a+'-minus-'+b
    if key in results:return tuple(map(F,results[key]['interval_exact']))
    key=b+'-minus-'+a
    if key not in results:raise KeyError((a,b))
    lo,hi=map(F,results[key]['interval_exact']);return -hi,-lo

def closed_costs(report):
    names=['anchor']+list(report['policies']);m=len(names);index={s:i for i,s in enumerate(names)}
    # D[i][j] bounds cost_i-cost_j. Every controller has the same proved support.
    D=[[H if i!=j else F(0) for j in range(m)] for i in range(m)]
    for i in range(1,m):D[0][i]=F(0)
    for estimator in ('cash','conditional'):
        r=report['inference'][estimator]
        for name,cost in r['costs'].items():
            lo,hi=map(F,cost['interval_exact']);i=index[name];D[i][0]=min(D[i][0],hi);D[0][i]=min(D[0][i],-lo)
        for a,b in itertools.combinations(names[1:],2):
            lo,hi=pair_record(r['contrasts'],a,b);i,j=index[a],index[b];D[i][j]=min(D[i][j],hi);D[j][i]=min(D[j][i],-lo)
    for k in range(m):
        for i in range(m):
            for j in range(m):D[i][j]=min(D[i][j],D[i][k]+D[k][j])
    if any(D[i][i]!=0 for i in range(m)):raise AssertionError('Inconsistent simultaneous difference system')
    # Independent feasibility and attainment checks for all column potentials.
    potentials=[]
    for j in range(m):
        mu=[D[i][j]-D[0][j] for i in range(m)]
        if mu[0]!=0 or any(mu[i]-mu[k]>D[i][k] for i in range(m) for k in range(m)):raise AssertionError('Invalid attaining cost potential')
        if any(mu[i]-mu[j]!=D[i][j] for i in range(m)):raise AssertionError('Nonattaining column')
        potentials.append(mu)
    regret={name:max(D[i][j] for j in range(1,m)) for i,name in enumerate(names) if i}
    winner=min(regret,key=regret.get)
    a=index['calibrated-relu-n16'];b=index['calibrated-bernstein-n16']
    return dict(policy_names=names[1:],zero_charge_regret=regret,zero_charge_minimax_policy=winner,
        calibrated_n16_R_minus_B=[-D[b][a],D[a][b]],closed_upper_difference_matrix=D,
        attaining_cost_potentials=potentials,used_statistical_family='R80 cash and conditional marginal/pair intervals, on their one preallocated joint event',
        interaction_intervals_not_inserted='Four-term interactions are reported separately; their extra restrictions are not claimed in this pair-system sharpness result.')

def main():
    start=time.perf_counter();services=[verify_service(n,k) for n,k in itertools.product((8,16),('relu','bernstein'))]
    report=json.loads((R/'results80/cost/summary.json').read_text());contrasts=report['inference']['conditional']['contrasts'];stable={x['name'] for x in services if x['all_exact_minimizers_same_policy']}
    transfer=[]
    for a,b in itertools.combinations(sorted(stable),2):
        transfer.append(dict(first=a,second=b,optimizer_class_interval=pair_record(contrasts,a,b),radius_enlargement=0,
            class_definition='Every exact minimizer of each fixed terminal-label qualification problem; terminal actor and robust menus fixed.'))
    choices=closed_costs(report)
    result=dict(status='passed',independent_action_switches=sum(x['switches'] for x in services),services=services,
        exact_optimizer_class_comparisons=transfer,choice=choices,
        new_cost_rows=0,new_fit_attempts=0,refitted=False,source_commit='ec8d40a058bfc03a88a62a223559698c5e849b22',
        original_cost_summary_sha256=sha(R/'results80/cost/summary.json'),seconds=time.perf_counter()-start,
        scope='Independent rational feature integrals, derivative controls, greediness and switch duals; deterministic optimizer-class cost transfer and pair-constraint closure. Not hidden-layer or long-horizon training reliability.')
    save(R/'audit/TRANSFER81.json',result)
    print(json.dumps(encode({k:result[k] for k in ('status','independent_action_switches','exact_optimizer_class_comparisons','seconds')}),indent=2),flush=True)
if __name__=='__main__':main()
