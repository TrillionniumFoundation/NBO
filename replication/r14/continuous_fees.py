"""Continuous-fee procurement on the unchanged R13 stochastic settlement target.

Value queries constrain a common policy's duration and surrender. Rational weak
LP duality certifies whole cells. The product F*H is enclosed by McCormick facets;
a convex capacity-cost tangent is used only in the optimistic bound. An actual
contract and a separate all-eta-response service bound establish the incumbent.
"""
from __future__ import annotations
import os
for _k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[_k]='1'
import sys,json,time,argparse,resource
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'replication/r13'))
from canonical import load,digest,dump
from engine import Engine,SIGNS
from certified_arithmetic import derive,upward,downward
from response_graph import supports
from oracle_polytope import RationalLP,encode
D0=.42425;LAM=.125;EPS=1e-10;ETA=1e-8;COST=.02;KAPPA=.02

def frac(x):return x if isinstance(x,Q) else Q.from_float(float(x))

def cell_lp(bank,adj,m,sign,a,b,eta=ETA,rho=0.,benefit=1.,cost=COST,kappa=KAPPA):
    """Variables B=J(d0,0), A, H, F, T=F*H, q; maximize buyer payoff."""
    a,b=frac(a),frac(b);eta=frac(eta);beta=frac(benefit);rho=frac(rho);c=frac(cost);kap=frac(kappa);d0=frac(D0)
    central=sorted([r for r in bank if r['adjustment']==adj and r['term']==m and r['sign']==sign and r['d']==D0],key=lambda r:r['F'])
    if not central:raise ValueError('missing central queries')
    # Exterior exact-response slope bounds extend to eta responses with eta/distance.
    hlow=Q(0);hhigh=Q(1)
    for r in central:
        f=frac(r['F'])
        if f<a or (eta==0 and f==a):hhigh=min(hhigh,frac(r['H'][1])+(eta/(a-f) if eta else Q(0)))
        if f>b or (eta==0 and f==b):hlow=max(hlow,frac(r['H'][0])-(eta/(f-b) if eta else Q(0)))
    hlow=max(Q(0),hlow);hhigh=min(Q(1),hhigh)
    if hlow>hhigh:raise ValueError('empty surrender range')
    G=frac(central[0]['G']);rows=[];rhs=[];provenance=[]
    def add(terms,z,kind,data):
        rr=[Q(0)]*6
        for i,v in terms.items():rr[i]=frac(v)
        rows.append(rr);rhs.append(frac(z));provenance.append(dict(kind=kind,data=data))
    for r in bank:
        if r['adjustment']==adj and r['term']==m and r['sign']==sign:
            add({0:1,1:frac(r['d'])-d0,2:-frac(r['F'])},frac(r['value'])+frac(EPS),'query',r['id'])
    for r in central:
        f=frac(r['F'])
        if f<=a:h=frac(r['H'][1])
        elif f>=b:h=frac(r['H'][0])
        else:continue
        add({0:-1,4:1,3:-h},-frac(r['value'])+frac(EPS)-f*h+eta,'response',r['id'])
    add({4:-1,2:a,3:hlow},a*hlow,'product',0)
    add({4:-1,2:b,3:hhigh},b*hhigh,'product',1)
    add({4:1,2:-b,3:-hlow},-b*hlow,'product',2)
    add({4:1,2:-a,3:-hhigh},-a*hhigh,'product',3)
    mid=(a+b)/2
    add({0:-1,4:1,3:2*c*mid,5:-1},-G+c*mid*mid,'participation',None)
    boxes=[(Q(-200),Q(200)),(Q(0),Q(1)),(hlow,hhigh),(a,b),(a*hlow,b*hhigh),(Q(0),Q(20))]
    objective=[Q(0),beta,Q(0),Q(0),rho,Q(-1)];constant=-kap*Q(m-1,8)
    return RationalLP(rows,rhs,boxes),objective,constant,provenance

def maximize(lp,c):
    """LP output only proposes nonnegative multipliers; exact residuals are charged."""
    from scipy.optimize import linprog
    last=None
    for presolve in (True,False):
        last=linprog(-np.array(c,float),A_ub=np.array(lp.A,float),b_ub=np.array(lp.b,float),bounds=np.array(lp.box,float),method='highs',options={'presolve':presolve,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
        if last.success:break
    if not last.success:raise ValueError('LP proposal failed: '+last.message)
    mu=np.maximum(0.,-last.ineqlin.marginals);bound,residual=lp.dual_bound(c,mu)
    return dict(proposed_objective=float(-last.fun),certified_upper=upward(bound),exact_upper=encode(bound),multipliers=mu.tolist(),residual=[encode(x) for x in residual],proposed_point=last.x.tolist(),status=last.message)

class Research:
    def __init__(self):
        self.start=time.perf_counter();self.b,self.j=load(ROOT/'replication/r13/canonical');self.e=Engine(self.b,self.j)
        self.audit=derive(self.b,self.j,allowance=EPS);self.bank=[];self.new=[];self.archive={};self.seq=0
        ref=json.loads((ROOT/'replication/r13/extensions/refinement.json').read_text())
        for r in ref['rows']:
            self.bank.append(dict(id='r13.refined.'+r['id'],adjustment=r['adjustment'],term=r['term'],sign=r['sign'],F=r['fee'],d=D0,value=r['value'],H=[r['support']['lower'][1],r['support']['upper'][1]],A=[r['support']['lower'][0],r['support']['upper'][0]],G=r['G'],source='r13.refinement',attained=r['support']['attained_positive']))
        old=json.loads((ROOT/'replication/r13/output/procurement.json').read_text())
        for r in old['rows']:
            for i,dd in [(0,D0-.01),(2,D0+.01)]:
                self.bank.append(dict(id=f"r13.secant.{r['id']}.{i}",adjustment=r['adjustment'],term=r['term'],sign=r['sign'],F=r['fee'],d=dd,value=r['shifted_values'][i],source='r13.procurement'))
        self.cache={(r['adjustment'],r['term'],r['F'],r['d']) for r in self.bank}
    def query(self,adj,m,F,d):
        F=float(F);d=float(d);key=(adj,m,F,d)
        if key in self.cache:return
        t=time.perf_counter()
        # Producer: historical Joint/Contract. Checker: independently recoded Engine.
        z=self.j.solve(LAM,d,F,adj,.8,.5,m=m)
        first={s:(z['first'][s]['value'],z['first'][s]['index']) for s in SIGNS}
        if any(first[s][1]<0 for s in SIGNS):raise ValueError('unrecorded first-date interpolation')
        rec=supports(self.e,z['v'],first,adj,m,F,self.audit) if d==D0 else None
        tag=f'q{self.seq:05d}';self.seq+=1;self.archive[tag+'.v']=z['v'][1:];self.archive[tag+'.p']=z['p'][1:]
        for s in SIGNS:
            r=dict(id=tag+'.'+s,adjustment=adj,term=m,sign=s,F=F,d=d,value=first[s][0],G=float(self.b.terminal[self.b.center]),source='r14.Joint',first_action=z['first'][s]['action'].tolist(),witness=tag)
            if rec:
                rr=rec['responses'][s];r.update(H=[rr['lower'][1],rr['upper'][1]],A=[rr['lower'][0],rr['upper'][0]],attained=rr['attained_positive'])
            self.bank.append(r);self.new.append(r)
        self.cache.add(key);self.j.cache.clear();self.e.cache.clear();print('QUERY',adj,m,F,d,round(time.perf_counter()-t,3),flush=True)
    def incumbent(self,adj,eta=ETA):
        best=None
        for r in self.bank:
            if r['adjustment']!=adj or r['d']!=D0 or not r.get('attained'):continue
            vals=[q for q in self.bank if q['adjustment']==adj and q['term']==r['term'] and q['sign']==r['sign'] and q['F']==r['F'] and q['d']<D0]
            if eta:
                if not vals:continue
                alow=max(Q(0),max((frac(r['value'])-frac(q['value'])-2*frac(EPS)-frac(eta))/(frac(D0)-frac(q['d'])) for q in vals))
            else:alow=frac(r['A'][0])
            grant=max(Q(0),frac(r['G'])-frac(r['value'])+frac(EPS)+frac(COST)*frac(r['F'])**2+frac(eta))
            # Charge the implemented outward-rounded transfer, not its unrounded ideal.
            grant=frac(upward(grant))
            profit=alow-grant-frac(KAPPA)*Q(r['term']-1,8)
            if best is None or profit>best[0]:best=(profit,r,alow,grant)
        if best is None:raise ValueError('no executable incumbent')
        return dict(lower=downward(best[0]),id=best[1]['id'],F=best[1]['F'],term=best[1]['term'],sign=best[1]['sign'],A_lower=downward(best[2]),grant=upward(best[3]),eta=eta)
    def run(self,adj,tolerance=3e-6,max_splits=90,eta=ETA):
        ref=json.loads((ROOT/'replication/r13/extensions/refinement.json').read_text())
        candidates=[r for r in ref['rows'] if r['adjustment']==adj and r['support']['attained_positive']]
        candidates.sort(key=lambda r:r['support']['lower'][0]-max(0,r['G']-r['value']+COST*r['fee']**2)-KAPPA*(r['term']-1)/8,reverse=True)
        for r in candidates[:3]:self.query(adj,r['term'],r['fee'],D0-.01)
        leaves={};splits=0;trace=[]
        for m in range(1,9):
            for s in SIGNS:
                for i in range(20):leaves[(m,s,Q(i,20),Q(i+1,20))]=None
        def bound(key):
            m,s,a,b=key;lp,c,const,pr=cell_lp(self.bank,adj,m,s,a,b,eta);ans=maximize(lp,c)
            return dict(upper=upward(Q(ans['exact_upper'])+const),dual=ans,constant=encode(const),lp=lp.json(),constraints=pr,cell=[encode(a),encode(b)],term=m,sign=s)
        for k in leaves:
            try:leaves[k]=bound(k)
            except ValueError:
                print('FAILED CELL',adj,k,flush=True)
                lp,c,const,pr=cell_lp(self.bank,adj,*k,eta);dump(HERE/'output/failed_cell.json',dict(lp=lp.json(),c=[encode(x) for x in c],key=[adj,k[0],k[1],encode(k[2]),encode(k[3])]))
                raise
        while True:
            inc=self.incumbent(adj,eta);key=max(leaves,key=lambda k:leaves[k]['upper']);upper=leaves[key]['upper']
            print('FRONTIER',adj,splits,inc['F'],inc['term'],inc['lower'],upper,upper-inc['lower'],flush=True)
            trace.append(dict(splits=splits,incumbent=inc,upper=upper,cells=len(leaves)))
            if upper-inc['lower']<=tolerance or splits>=max_splits:break
            m,s,a,b=key;mid=(a+b)/2
            for dd in (D0,D0-.01,D0+.01,D0+.1):self.query(adj,m,mid,dd)
            for F in (a,b):
                if splits<24 or b-a>Q(1,100):self.query(adj,m,F,D0+.1)
            del leaves[key];leaves[(m,s,a,mid)]=bound((m,s,a,mid));leaves[(m,s,mid,b)]=bound((m,s,mid,b))
            for k in list(leaves):
                if k[0]==m:leaves[k]=bound(k)
            splits+=1
        inc=self.incumbent(adj,eta);upper=max(v['upper'] for v in leaves.values());live=[v for v in leaves.values() if v['upper']>=inc['lower']]
        return dict(adjustment=adj,fee_domain=[0.,1.],eta=eta,incumbent=inc,global_upper=upper,regret_upper=upward(frac(upper)-frac(inc['lower'])),tolerance=tolerance,tolerance_met=upper-inc['lower']<=tolerance,splits=splits,leaves=list(leaves.values()),not_excluded=[{k:v[k] for k in ('term','sign','cell','upper')} for v in live],trace=trace)
    def save(self,results):
        out=HERE/'output';out.mkdir(exist_ok=True);np.savez_compressed(out/'continuous_queries.npz',**self.archive)
        dump(out/'continuous_fees.json',dict(schema='nbo-r14-continuous-fee-v1',canonical_manifest_sha256=digest(ROOT/'replication/r13/canonical/manifest.json'),inherited_refinement_sha256=digest(ROOT/'replication/r13/extensions/refinement.json'),inherited_procurement_sha256=digest(ROOT/'replication/r13/output/procurement.json'),arithmetic=self.audit,value_allowance=EPS,bank=self.bank,new_queries=self.new,query_archive_sha256=digest(out/'continuous_queries.npz'),results=results,elapsed_seconds=time.perf_counter()-self.start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Same stored stochastic settlement economy. All terms, both initial mandates, every F in [0,1], every eta-best response. Capacity frontier E=F follows from the separately proved enforcement technology.'))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--max-splits',type=int,default=120);ap.add_argument('--tolerance',type=float,default=3e-6);ap.add_argument('--eta',type=float,default=0.);ap.add_argument('--resume',action='store_true');args=ap.parse_args();work=Research();results=[]
    if args.resume:
        old=json.loads((HERE/'output/continuous_fees.json').read_text());work.bank=old['bank'];work.new=old['new_queries']
        with np.load(HERE/'output/continuous_queries.npz') as ar:work.archive={k:ar[k] for k in ar.files}
        work.cache={(r['adjustment'],r['term'],r['F'],r['d']) for r in work.bank};work.seq=max([int(r['witness'][1:]) for r in work.new]+[-1])+1
    for adj in (True,False):
        for m in range(1,9):
            for i in range(11):work.query(adj,m,i/10,D0+.1)
        work.save(results);results.append(work.run(adj,args.tolerance,args.max_splits,args.eta));work.save(results)
    print('CONTINUOUS DONE',json.dumps([{k:r[k] for k in ('adjustment','incumbent','global_upper','regret_upper','splits')} for r in results]),flush=True)
