"""R47 direct policy costs. Frozen R46 policies, continuous-bin enclosures.

No policy is trained here. Independent uniform bins are the statistical model;
PCG64 is only the reproducible implementation. The complete family is fixed.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse, hashlib, itertools, json, math, sys, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
BASE=R.parent/'2026-10-07-r46'; PREV=R.parent/'2026-10-07-r45'
sys.path.insert(0,str(PREV/'code'))
import constructive as c
from interval import I
METHODS=('cone-witness','cone-nearest','spline-nearest')
PAIRS=((0,1),(0,2),(1,2)); LAWS=('uniform','1/8','1/2','7/8')
N_PATHS=131072; BITS=40; FAMILY=120; ALPHA=F(1,100); MARGIN=F(1,1024)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

class Actor:
    """Enclose every cell intersecting an acquired state interval."""
    def __init__(self,a):
        actions=list(map(F,a['node_actions']))
        if a['kind']=='cone-witness':
            cuts=list(map(F,a['cuts'])); vals=[actions[j] for j in a['owners']]
        else:
            n=a['N']; cuts=[F(0)]+[F(2*j+1,2*n) for j in range(n)]+[F(1)]
            vals=actions
        if len(cuts)!=len(vals)+1:raise ValueError('Bad actor partition')
        self.cuts=cuts; self.a=np.array(list(map(float,vals)))
        if any(F(float(x))!=q for x,q in zip(self.a,vals)):
            raise ValueError('Action must be an exactly represented dyadic')
        self.bounds=c.array_i(cuts); self.ambiguities=0; self.queries=0
    def evaluate(self,x):
        if np.any(x.lo<0) or np.any(x.hi>1):raise ValueError('Outside state domain')
        first=np.clip(np.searchsorted(self.bounds.hi,x.lo,side='left')-1,0,len(self.a)-1)
        last=np.clip(np.searchsorted(self.bounds.lo,x.hi,side='right')-1,0,len(self.a)-1)
        lo=self.a[first].copy(); hi=self.a[last].copy(); bad=(first!=last)
        self.queries+=int(x.lo.size);self.ambiguities+=int(np.count_nonzero(bad))
        for j in np.flatnonzero(bad):
            values=self.a[first[j]:last[j]+1];lo[j]=np.min(values);hi[j]=np.max(values)
        return I(lo,hi)

class Policy:
    def __init__(self,path):
        self.path=path;self.raw=json.loads(path.read_text());d=self.raw['definition']
        self.f=[c.PWL(list(map(F,m['knots'])),list(map(F,m['values']))) for m in d['models']]
        self.actors=[Actor(a) for a in self.raw['policy_actors']]
        self.T=d['T'];self.p=d['price'];self.N=d['N'];self.method=self.raw['method']
    def terminal_support(self):
        width=F(self.raw['definition']['terminal_width']);L=F(17,4);h=F(1,2*self.N)
        e=(width-2*L*h)/2
        if e<0:raise AssertionError('Invalid inherited terminal budget')
        if self.method=='spline-nearest':return -e-L*h,e+L*h
        return -e-2*L*h,e
    def score(self,x0,z):
        x=x0;score=self.f[0].evaluate(x);raw_cost=I.point(np.zeros(x.lo.shape))
        for t in range(self.T):
            a=self.actors[t].evaluate(x);cost=c.stage(x,a,self.p)
            base=c.base_state(x,a)
            residual=cost+float(c.BETA)*self.f[t+1].uniform(base)-self.f[t].evaluate(x)
            score=score+float(c.BETA**t)*residual
            raw_cost=raw_cost+float(c.BETA**t)*cost
            x=(base+z[t]).clip(0,1) # intersection with the proved invariant domain
        terminal=c.terminal(x)
        score=score+float(c.BETA**self.T)*(terminal-self.f[-1].evaluate(x))
        raw_cost=raw_cost+float(c.BETA**self.T)*terminal
        return score,raw_cost

def difference_support(a,b,law):
    if law=='uniform':
        points=sorted(set(a.f[0].k+b.f[0].k))
        values=[a.f[0].exact(x)-b.f[0].exact(x) for x in points]
        lo,hi=min(values),max(values)
    else:lo=hi=a.f[0].exact(F(law))-b.f[0].exact(F(law))
    for t,(ar,br) in enumerate(zip(a.raw['joint_rows'],b.raw['joint_rows'])):
        lo+=c.BETA**t*(-F(ar['optimal_residual_upper'])-F(br['selected_policy_upper']))
        hi+=c.BETA**t*(F(ar['selected_policy_upper'])+F(br['optimal_residual_upper']))
    al,ah=a.terminal_support();bl,bh=b.terminal_support()
    lo+=c.BETA**a.T*(al-bh);hi+=c.BETA**a.T*(ah-bl)
    return lo,hi

def moments(x,a,b):
    """Exact rational error budget for binary64 sums and products.

    gamma_(n+4) bounds even sequential summation; pairwise numpy summation
    needs no stronger assumption. Mean and second moment are not exact replay.
    """
    n=int(x.size);u=F(1,2**53);gamma=(n+4)*u/(1-(n+4)*u)
    M=max(abs(F(a)),abs(F(b)))
    mu=F(float(np.mean(x)));sq=F(float(np.mean(x*x)))
    ml,mh=mu-gamma*M,mu+gamma*M
    ql,qh=sq-gamma*M*M,sq+gamma*M*M
    min_sq=F(0) if ml<=0<=mh else min(ml*ml,mh*mh)
    var=max(F(0),F(n,n-1)*(qh-min_sq))
    return {'n':n,'mean':float(mu),'mean_lo':str(ml),'mean_hi':str(mh),
            'second_lo':str(ql),'second_hi':str(qh),'variance_upper':str(var),
            'gamma':str(gamma),'endpoint_sha256':hashlib.sha256(x.tobytes()).hexdigest()}

def radius(stats,a,b):
    # exp(11)>48000=4*120/.01 by a finite positive Taylor lower bound.
    assert sum((F(11)**j/math.factorial(j) for j in range(41)),F(0))>4*FAMILY/ALPHA
    n=stats['n'];q=2*F(stats['variance_upper'])*11/n
    root=math.sqrt(float(q))
    while F(root)**2<q:root=math.nextafter(root,math.inf)
    return F(root)+F(7*11,3*(n-1))*(F(b)-F(a))

def interval_from_stats(left,right,a,b):
    lower=F(left['mean_lo'])-radius(left,a,b)
    upper=F(right['mean_hi'])+radius(right,a,b)
    return max(F(a),lower),min(F(b),upper)

def classify(lo,hi):
    return {'sign':'first-lower' if hi<0 else ('first-higher' if lo>0 else 'unresolved'),
            'within_margin':bool(-MARGIN<=lo and hi<=MARGIN),
            'first_noninferior_at_margin':bool(hi<=MARGIN)}

def catalogue():
    out=[]
    for T,p in itertools.product((2,4),(1,4)):
        dirs=[BASE/'results/services'/f'{m}-T{T}-p{p}-r0' for m in METHODS]
        records=[json.loads((d/'record.json').read_text()) for d in dirs]
        for target in ('1/4','1/8','1/16'):
            first=[v['first_crossings'][target] for v in records]
            if not all(first):continue
            paths=[d/f"checkpoint-N{v['N']}.json" for d,v in zip(dirs,first)]
            for path,d,v,rec in zip(paths,dirs,first,records):
                attempt=next(a for a in rec['attempts'] if a['N']==v['N'])
                assert H(path)==attempt['checkpoint_sha256']
            out.append((T,p,target,paths))
    if len(out)*len(LAWS)*len(PAIRS)!=FAMILY:raise AssertionError('Protocol family size changed')
    return out

def group(T,p,target,paths,law,out):
    key=f'T{T}-p{p}-e{target.replace("/","_")}-x{law.replace("/","_")}'
    seed=int.from_bytes(hashlib.sha256(('NBO-R47-DIRECT-v1:'+key).encode()).digest()[:8],'big')
    rng=np.random.Generator(np.random.PCG64(seed));policies=[Policy(q) for q in paths]
    pair_support=[difference_support(policies[i],policies[j],law) for i,j in PAIRS]
    support=[(c.enclosure(a)[0],c.enclosure(b)[1]) for a,b in pair_support]
    low=np.empty((3,N_PATHS));high=np.empty_like(low);raw=np.empty_like(low)
    stream=hashlib.sha256();start=time.perf_counter();raw_means=np.zeros(3)
    batch=8192
    for begin in range(0,N_PATHS,batch):
        n=min(batch,N_PATHS-begin)
        bins=rng.integers(0,2**BITS,size=(T+1,n),dtype=np.uint64)
        stream.update(bins.tobytes());v=bins.astype(float)
        x0=I(v[0]*2.**-BITS,(v[0]+1)*2.**-BITS) if law=='uniform' else I.point(np.full(n,float(F(law))))
        z=[I(-1/32+v[t+1]*2.**(-BITS-4),-1/32+(v[t+1]+1)*2.**(-BITS-4)) for t in range(T)]
        scores=[];costs=[]
        for policy in policies:
            score,cost=policy.score(x0,z);scores.append(score);costs.append(cost)
        for j,(a,b) in enumerate(PAIRS):
            diff=scores[a]-scores[b];A,B=support[j]
            low[j,begin:begin+n]=np.maximum(diff.lo,A)
            high[j,begin:begin+n]=np.minimum(diff.hi,B)
            if np.any(low[j,begin:begin+n]>high[j,begin:begin+n]):
                raise AssertionError('Empty support/path intersection')
            raw[j,begin:begin+n]=(costs[a]-costs[b]).midpoint()
    comparisons=[]
    for j,(a,b) in enumerate(PAIRS):
        A,B=support[j];left=moments(low[j],A,B);right=moments(high[j],A,B)
        lo,hi=interval_from_stats(left,right,A,B)
        comparisons.append({'first':METHODS[a],'second':METHODS[b],
            'support_exact':[str(q) for q in pair_support[j]],'support_float':[A,B],
            'lower_endpoint_moments':left,'upper_endpoint_moments':right,
            'interval_exact':[str(lo),str(hi)],'interval':[c.enclosure(lo)[0],c.enclosure(hi)[1]],
            'raw_cost_midpoint_mean_diagnostic':float(np.mean(raw[j])),
            'maximum_path_enclosure_width':float(np.max(high[j]-low[j])),
            'mean_path_enclosure_width':float(np.mean(high[j]-low[j])),**classify(lo,hi)})
    record={'key':key,'horizon':T,'price':p,'target':target,'initial_law':law,
            'seed':seed,'paths':N_PATHS,'uniform_bin_bits':BITS,'stream_sha256':stream.hexdigest(),
            'family_size':FAMILY,'family_error':str(ALPHA),'log_upper':11,'decision_margin':str(MARGIN),
            'policy_files':[{ 'path':str(q.relative_to(BASE)), 'sha256':H(q)} for q in paths],
            'actor_queries':[sum(a.queries for a in m.actors) for m in policies],
            'ambiguous_actor_queries':[sum(a.ambiguities for a in m.actors) for m in policies],
            'score_evaluator_stats':[{k:sum(f.stats[k] for f in m.f) for k in m.f[0].stats} for m in policies],
            'comparisons':comparisons,'seconds_before_record':time.perf_counter()-start,
            'clock_scope':'loading, exact support and serialization excluded from this inner group clock; outer process clock separate',
            'statistical_scope':'conditional on frozen policies and iid uniform-bin model; pseudorandom seed is reproducibility only'}
    c.write_new(out/(key+'.json'),record);print(key,flush=True)
    return record

def main():
    out=R/'results/direct'
    if out.exists():raise FileExistsError('Completed direct observations must not be overwritten')
    out.mkdir(parents=True);start=time.perf_counter();summaries=[]
    for T,p,target,paths in catalogue():
        for law in LAWS:
            record=group(T,p,target,paths,law,out)
            summaries.append({'key':record['key'],'file_sha256':H(out/(record['key']+'.json'))})
    c.write_new(out/'COMPLETE.json',{'groups':len(summaries),'contrasts':FAMILY,
                'paths_per_group':N_PATHS,'seconds_through_groups':time.perf_counter()-start,'records':summaries})
if __name__=='__main__':main()
