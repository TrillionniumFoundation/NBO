"""Exact continuation-frontier comparator for randomized history-conditioned policies.
Fixed restarts are distinct from the primary uniform initial-distribution objective.
Also solves an all-state, uniform-initial, two-period randomized Markov reference.
"""
from fractions import Fraction as F
from functools import lru_cache
import itertools,time
import kernel as k
from primary import ROOT,load,save,digest
Z,O=F(0),F(1)
def efficient(points):
    by={}
    for j,c in points:by[j]=min(c,by.get(j,c))
    best=None;kept=[]
    for j in sorted(by,reverse=True):
        c=by[j]
        if best is None or c<best:kept.append((j,c));best=c
    hull=[]
    for p in reversed(kept):
        while len(hull)>=2:
            a,b=hull[-2:]
            if (b[0]-a[0])*(p[1]-b[1])-(b[1]-a[1])*(p[0]-b[0])<=0:hull.pop()
            else:break
        hull.append(p)
    return hull

def clip(hull,floor):
    if hull[0][0]>=floor:return hull,[('point',p,p,O) for p in hull]
    assert hull[-1][0]>=floor
    for n in range(1,len(hull)):
        a,b=hull[n-1],hull[n]
        if b[0]>=floor:
            w=(b[0]-floor)/(b[0]-a[0]);p=(floor,w*a[1]+(1-w)*b[1])
            return [p]+hull[n:] if p!=b else hull[n:],([('mix',a,b,w)]+[('point',v,v,O) for v in hull[n:]]) if p!=b else [('point',v,v,O) for v in hull[n:]]
    raise AssertionError

def solve(T,x0,raw,V,eps):
    nodes=[];counts={'candidates':0,'vertices':0,'dual_comparisons':0}
    @lru_cache(None)
    def rec(t,x):
        if t==T:return ((x/2,Z),)
        candidates=[];sources=[];children=[]
        for a in range(3):
            pair=[]
            for m,b in k.MAPS[a]:pair.append(rec(t+1,m*x+b))
            children.append([[str(m*x+b),t+1] for m,b in k.MAPS[a]])
            for u,v in itertools.product(*pair):
                j=x-k.COSTS[a]+k.BETA*(k.PROBS[0]*u[0]+k.PROBS[1]*v[0])
                c=(1+x if a!=raw[t].at(x) else Z)+k.BETA*(k.PROBS[0]*u[1]+k.PROBS[1]*v[1])
                candidates.append((j,c));sources.append((a,u,v))
        h=efficient(candidates);floor=V[t].at(x)-eps;fr,provenance=clip(h,floor)
        assert max(j for j,c in candidates)==V[t].at(x)
        duals=[]
        for n,(j,c) in enumerate(fr):
            if n:previous=fr[n-1];mu=(c-previous[1])/(j-previous[0])
            elif j>floor or len(fr)==1:mu=Z
            else:nextp=fr[1];mu=(nextp[1]-c)/(nextp[0]-j)
            assert mu>=0
            intercept=min(cc-mu*jj for jj,cc in candidates)
            assert mu*j+intercept==c,('dual equality',t,x,n)
            # Vertex is a candidate or an exactly feasible convex combination.
            tag,a,b,w=provenance[n];assert a in candidates and b in candidates and 0<=w<=1
            assert (w*a[0]+(1-w)*b[0],w*a[1]+(1-w)*b[1])==(j,c) and j>=floor
            duals.append({'mu':str(mu),'intercept':str(intercept),'primal':{'left':list(map(str,a)),'right':list(map(str,b)),'left_weight':str(w)}})
            counts['dual_comparisons']+=len(candidates)
        nodes.append({'t':t,'x':str(x),'operating_floor':str(floor),'children':children,
             'frontier':[[str(j),str(c)] for j,c in fr],'primal_dual':duals,'candidate_count':len(candidates),
             'candidate_sha256':digest([[str(j),str(c)] for j,c in candidates])})
        counts['candidates']+=len(candidates);counts['vertices']+=len(fr)
        return tuple(fr)
    frontier=rec(0,x0)
    return frontier,nodes,{**counts,'states':len(nodes),'memoization':str(rec.cache_info())}

def log_bounds(r,n=40):
    assert r>0
    if r<1:
        l,u=log_bounds(1/r,n);return -u,-l
    m=0
    while r>=2:r/=2;m+=1
    def series(x):
        y=(x-1)/(x+1);s=2*sum((y**(2*i+1)/F(2*i+1) for i in range(n)),Z)
        e=2*y**(2*n+1)/(F(2*n+1)*(1-y*y))
        return s,s+e
    l,u=series(r);l2,u2=series(F(2));return l+m*l2,u+m*u2

def two_period(eps):
    V,pol,_=k.exact_dp(2);assert pol[1].extent()==(Z,Z)
    q0=k.q_functions(V[1])[0];gap=k.linear_comb([V[0],q0],[O,-O]);allowed=k.threshold(gap,eps)
    knots=set(gap.xs)|set(allowed.xs);knots=sorted(knots)
    det=Z;lo=Z;hi=Z;pieces=[]
    for l,r in zip(knots,knots[1:]):
        if gap.at((l+r)/2)<=eps:continue
        a,b=gap.line((l+r)/2);mass=(r-l)+(r*r-l*l)/2;det+=mass
        if a==0:il=iu=mass/b;expression={'constant':str(il)}
        else:
            ratio=(a*r+b)/(a*l+b);ll,uu=log_bounds(ratio);co=(a-b)/(a*a);base=(r-l)/a
            il=base+co*(ll if co>=0 else uu);iu=base+co*(uu if co>=0 else ll)
            expression={'constant':str(base),'log_coefficient':str(co),'log_argument':str(ratio)}
        lo+=mass-eps*iu;hi+=mass-eps*il
        pieces.append({'left':str(l),'right':str(r),'gap_slope':str(a),'gap_intercept':str(b),'saved_cost_integral_expression':expression})
    assert 0<lo<=hi<det and hi-lo<F(1,10**20)
    # Explicit exact Markov counterexample at x=0, all future actions defer.
    gap0=gap.at(Z);prob=1-eps/gap0
    return {'T':2,'epsilon':str(eps),'installed':'defer','policy_class':'randomized_Markov',
       'constraint':'all_state_all_restart','objective':'uniform_initial_integrated_discounted_revision_cost',
       'deterministic_optimum':str(det),'randomized_optimum_lower':str(lo),'randomized_optimum_upper':str(hi),
       'analytic_pieces':pieces,'point_x0':{'operating_action_gap':str(gap0),'replace_probability':str(prob),'randomized_cost':str(prob),'deterministic_cost':'1'},
       'log_enclosure_method':'atanh rational series, 40 terms after powers-of-two range reduction; exact positive remainder bound'}

def run():
    start=time.perf_counter();rows=[]
    for p in sorted((ROOT/'results/primary').glob('H4*')):
        d=load(p);raw=list(map(k.PW.load,d['raw']));V=list(map(k.PW.load,d['V']));B=k.PW.load(d['lower'][0]);C=k.PW.load(d['C'][0]);eps=F(d['epsilon'])
        for x in (Z,F(1,4),F(1,2),F(3,4),O):
            tic=time.perf_counter();fr,nodes,stats=solve(4,x,raw,V,eps);value=fr[0][1]
            assert value<=C.at(x)
            name=p.name.replace('.json.gz','')+'_x'+str(x).replace('/','_')+'.json.gz'
            obj={'schema':'NBO-R38-continuation-frontier-v1','T':4,'proposal':d['proposal'],'epsilon':str(eps),'initial_state':str(x),
               'policy_class':'randomized_history_conditioned','initial_distribution':'Dirac_at_reported_state',
               'frontier':[[str(j),str(c)] for j,c in fr],'nodes':nodes,'value':str(value),'whole_state_uniform_objective':False}
            h=save(ROOT/'results/frontiers'/name,obj)
            row={kk:obj[kk] for kk in ('T','proposal','epsilon','initial_state','policy_class','initial_distribution','value')}
            row.update({'deterministic_lower':str(B.at(x)),'deterministic_upper':str(C.at(x)),
              'strict_randomization_gain_vs_deterministic_lower':value<B.at(x),'seconds':time.perf_counter()-tic,
              'proof_sha256':h,'proof_file':'frontiers/'+name,**stats});rows.append(row)
            print(d['proposal'],eps,x,'randomized',float(value),'deterministic',float(B.at(x)),flush=True)
    extra=[two_period(eps) for eps in (F(1,100),F(1,20))]
    save(ROOT/'results/frontier.json',{'point_cases':len(rows),'outcomes':rows,'two_period_uniform_references':extra,
        'strict_class_separations':sum(r['strict_randomization_gain_vs_deterministic_lower'] for r in rows),'seconds':time.perf_counter()-start,
        'interpretation':'The 70 T=4 objectives use fixed restarts and the randomized history-conditioned class, not the uniform primary Markov objective. The two T=2 references solve the all-state uniform-initial randomized Markov objective without changing the primary cohort.'})
if __name__=='__main__':run()
