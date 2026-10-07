"""Direct original-continuous-law costs of every R46 common-crossing policy."""
from __future__ import annotations
import itertools,json,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from common import R,I,fi,bins,confidence,quantize_interval,save_npz,write,hfile,BETA
import constructive as old
BASE=R.parent/'2026-10-07-r46'
METHODS=('cone-witness','cone-nearest','spline-nearest')

class Actor:
    def __init__(self,payload,t):
        self.a=np.array(payload['definition']['actors'][t],dtype=float)
        raw=payload['policy_actors'][t]
        if raw['kind']=='cone-witness':
            cuts=list(map(F,raw['cuts']));owners=np.array(raw['owners'],dtype=int)
            self.a=self.a[owners]
        else:
            N=payload['N'];cuts=[F(0)]+[F(2*j+1,2*N) for j in range(N)]+[F(1)]
        self.cl=np.array([float(fi(c).lo) for c in cuts])
        self.ch=np.array([float(fi(c).hi) for c in cuts])
        self.ambiguities=0
    def __call__(self,x):
        il=np.clip(np.searchsorted(self.ch,x.lo,side='right')-1,0,len(self.a)-1)
        ih=np.clip(np.searchsorted(self.cl,x.hi,side='right')-1,0,len(self.a)-1)
        lo=self.a[il].copy();hi=self.a[ih].copy()
        bad=np.flatnonzero(il!=ih);self.ambiguities+=int(len(bad))
        for k in bad:
            allowed=self.a[il[k]:ih[k]+1];lo[k]=allowed.min();hi[k]=allowed.max()
        return I(np.minimum(lo,hi),np.maximum(lo,hi))

def cost(payload,initial,shocks):
    x=initial;v=I.point(np.zeros_like(x.lo));actors=[Actor(payload,t) for t in range(payload['T'])]
    for t,a in enumerate(actors):
        u=a(x);v=v+fi(BETA**t)*old.stage(x,u,payload['price'])
        x=(old.base_state(x,u)+(2*shocks[t]-1)/32).clip(0,1)
    v=v+fi(BETA**payload['T'])*old.terminal(x)
    return v,sum(a.ambiguities for a in actors)

def main(out=None,n=262144):
    out=R/'results/scalar' if out is None else Path(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);records=[];frontier=[]
    for T,p in itertools.product((2,4),(1,4)):
        services={m:json.loads((BASE/f'results/services/{m}-T{T}-p{p}-r0/record.json').read_text()) for m in METHODS}
        for m,s in services.items():
            for row in s['attempts']:
                frontier.append({'T':T,'price':p,'method':m,'N':row['N'],
                    'bound':row['bound_upper'],'prefix_q':row['prefix_q_evaluations'],
                    'historical_prefix_seconds':row['prefix_seconds']})
        for target in (F(1,4),F(1,8),F(1,16)):
            chosen={}
            for m,s in services.items():
                rows=[a for a in s['attempts'] if F(a['bound_exact'])<=target]
                if rows:chosen[m]=rows[0]
            if len(chosen)!=3:continue
            start=time.perf_counter();seed=470000+1000*T+100*p+int(1/target)
            rng=np.random.Generator(np.random.PCG64(seed))
            initial=bins(rng,(n,));shocks=[bins(rng,(n,)) for _ in range(T)]
            costs={};ids={};amb={}
            for m,row in chosen.items():
                path=BASE/f'results/services/{m}-T{T}-p{p}-r0'/f"checkpoint-N{row['N']}.json"
                assert hfile(path)==row['checkpoint_sha256']
                payload=json.loads(path.read_text());ids[m]={'path':str(path.relative_to(BASE)),'sha256':hfile(path),'N':row['N']}
                costs[m],amb[m]=cost(payload,initial,shocks)
            arrays={};group=[]
            cmax=F(197,256)+F(p,16);gmax=F(314,256)
            M=sum(BETA**t*cmax for t in range(T))+BETA**T*gmax
            for j,(a,b) in enumerate(itertools.combinations(METHODS,2)):
                lo,hi=quantize_interval(costs[a]-costs[b]);arrays[f'lo{j}']=lo;arrays[f'hi{j}']=hi
                row={'T':T,'price':p,'target_exact':str(target),'left':a,'right':b,
                     'n':n,'seed':seed,'initial_distribution':'Uniform[0,1]',
                     'policy_identities':ids,'actor_ambiguities':amb,
                     'continuous_cost_upper_exact':str(M),
                     **confidence(lo,hi,M,30)}
                group.append(row)
            name=f'T{T}-p{p}-target{target.denominator}'
            digest=save_npz(out/(name+'.npz'),**arrays)
            for row in group:row.update(raw_endpoints=name+'.npz',raw_sha256=digest,group_seconds=time.perf_counter()-start)
            write(out/(name+'.json'),group);records+=group
    assert len(records)==30
    write(out/'summary.json',{'contrasts':records,'family_size':30,'margin':0.005,
          'within_margin':sum(r['within_margin'] for r in records),
          'lower_cost':sum(r['sign']=='lower-cost' for r in records),
          'higher_cost':sum(r['sign']=='higher-cost' for r in records),
          'sign_unresolved':sum(r['sign']=='sign-unresolved' for r in records)})
    write(out/'R46_full_frontier.json',{'rows':frontier,'scope':'All R46 repetition-zero rungs; clocks are historical, not new measurements.'})
    print('Scalar contrasts',len(records),'within margin',sum(r['within_margin'] for r in records),flush=True)

if __name__=='__main__':main()
