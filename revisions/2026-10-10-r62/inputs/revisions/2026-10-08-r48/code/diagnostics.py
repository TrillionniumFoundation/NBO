"""Frozen representation, observation-price and historical full-clock diagnostics."""
from __future__ import annotations
import itertools, time
from common import *
from tensor import Model

def sensor_curve(payload,price):
    d=2;Ka=F(1,16);T=payload['T'];S=sum((BETA**t for t in range(T)),F(0));rows=[]
    for bits in range(4,17):
        radius=F(d,2**(bits+1));allowance=F(0)
        for t,(m,row) in enumerate(zip(payload['models'][:-1],payload['rows'])):
            allowance+=BETA**t*(2*F(m['L'])*radius+F(row['D'])*(2*Ka*radius+F(1,4096)))
        fee=F(price)*d*bits*S
        rows.append({'bits':bits,'l1_radius':str(radius),'acquisition_allowance':str(allowance),'observation_charge':str(fee),'augmented_upper':str(F(payload['policy_bound_exact'])+allowance+fee)})
    best=min(rows,key=lambda x:(F(x['augmented_upper']),x['bits']))
    return {'price_per_coordinate_bit':str(price),'rows':rows,'selected_bits':best['bits'],'selected_augmented_upper':best['augmented_upper'],'selection_scope':'minimizes the proved uniform upper account, not the unknown actual cost'}

def main():
    out=R/'results/diagnostics'
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);sensors=[];compiler=[]
    # Import the unchanged dense implementation for a representation comparison.
    sys.path.insert(0,str(P47/'code'));import constrained as old
    points=np.array(list(itertools.product(np.arange(33)/32,repeat=2)))
    for T,p,N in itertools.product((2,3),(1,4),(4,8,16)):
        path=P47/'results/constrained'/f'feasible-cone-witness-T{T}-p{p}-r0'/f'checkpoint-N{N}.json'
        payload=read(path);rows=[]
        for rep in range(3):
            start=time.perf_counter();models=[Model([np.arange(N+1)/N]*2,m['labels'],'witness',F(m['L'])) for m in payload['models']]
            build=time.perf_counter()-start;start=time.perf_counter();values=[m.point(points) for m in models];fast=time.perf_counter()-start
            start=time.perf_counter();dense=[old.Model.load(m) for m in payload['models']];creation=time.perf_counter()-start;start=time.perf_counter();ref=[m.point(points) for m in dense];slow=time.perf_counter()-start
            for a,b in zip(values,ref):assert np.all(a.lo<=b.hi) and np.all(b.lo<=a.hi)
            maxwidth=max(float(np.max(v.hi-v.lo)) for v in values)
            # Exact rational witnesses at a fixed off-grid validation catalogue.
            if rep==0:
                for m in models:
                    for j in range(9):
                        x=(F(2*j+1,32),F(2*((j*5)%15)+1,32));truth,idx=m.exact(x)
                        value=m.point([list(map(float,x))]);actor,_=m.actor(I.point([list(map(float,x))]),np.arange(m.S,dtype=float))
                        assert F(float(value.lo[0]))<=truth<=F(float(value.hi[0])) and actor.lo[0]==idx and actor.hi[0]==idx
            rows.append({'repeat':rep,'compile_seconds':build,'compiled_query_seconds':fast,'dense_load_seconds':creation,'dense_query_seconds':slow,'maximum_compiled_interval_width':maxwidth,'queries':len(points)*len(models),'corner_terms':sum(m.counts['corner_terms'] for m in models),'dense_cone_terms':sum(m.counts['cone_terms'] for m in dense)})
        compiler.append({'T':T,'p':p,'N':N,'source_sha256':H(path),'repetitions':rows,'policy_identity':'theorem and exact original-index checks; interval overlap alone is not the identity proof'})
        sensors.append({'T':T,'p':p,'N':N,'source_sha256':H(path),'curves':[sensor_curve(payload,F(q)) for q in ('1/16384','1/4096','1/1024')]})
    save(out/'compiler.json',compiler);save(out/'sensors.json',sensors)
    historical=[]
    for T,p in itertools.product((2,4),(1,4)):
        services={}
        for name in ('cone-witness','cone-nearest','spline-nearest'):
            records=[]
            for rep in range(3):
                path=P46/'results/services'/f'{name}-T{T}-p{p}-r{rep}/record.json';records.append({'source_sha256':H(path),'record':read(path)})
            services[name]=records
        cuts=sorted({F(0)}|{F(a['bound_exact']) for rr in services.values() for a in rr[0]['record']['attempts']})
        rows=[]
        for left,right in zip(cuts,cuts[1:]+[None]):
            if right is not None and right==0:continue
            selection={}
            for name,recs in services.items():
                values=[]
                for rec in recs:
                    at=next((a for a in rec['record']['attempts'] if F(a['bound_exact'])<=left),None)
                    values.append(None if at is None else {k:v for k,v in at.items() if k in ('N','prefix_seconds','prefix_q_evaluations','checkpoint_bytes')})
                selection[name]=values
            rows.append({'epsilon_left_closed':str(left),'epsilon_right_open':None if right is None else str(right),'methods':selection})
        historical.append({'T':T,'p':p,'rows':rows,'source_records':{m:[q['source_sha256'] for q in v] for m,v in services.items()},'clock_scope':'unaltered historical R46 internal prefix times; not retimed, not combined with R48 clocks'})
    save(out/'historical_scalar_clock_frontier.json',historical)
if __name__=='__main__':main()
