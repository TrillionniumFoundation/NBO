"""Independent rational endpoints and simultaneous inference for R96.

No production interval, first-action, quadrature, fitting, or inference module
is imported. The retained independent94 primitive reconstruction is reused.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,math,pathlib,random,struct,time
from fractions import Fraction as F
from independent94 import (economic_S,economic_gradient,next_state,
    polynomial_from_primitives,tail_threshold,terminal_bounds,objective_gradient,integral)
ROOT=pathlib.Path(__file__).resolve().parents[1]
ARMS=('online-risk-dp','quadratic','relu','spline')
TAU=F(1,256);WIDTH=F(1,8192);RADIUS=F(1,4096);MARGIN=F(1,1280)


def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def load_rows(path):
    with path.open() as stream:
        data=list(csv.DictReader(stream))
    # Use the exact binary64 values that produced the raw decimal CSV, not a
    # different decimal interpretation of the latent numerical endpoint.
    return [{k:(F(float(v)) if k not in ('rejected','exact') else v=='True') for k,v in row.items()} for row in data]


def tail(values,alpha):
    n=len(values);k=int(n*(1-alpha));ordered=sorted(values)
    eta=ordered[n-k]
    # Primal threshold integral on the numerical measure, independently coded.
    return eta+sum(max(F(0),v-eta) for v in values)/k


def model(path):
    a=list(map(F,struct.unpack('<16d',path.read_bytes())))
    kind=('quadratic','relu','spline')[int(a[0])]
    return kind,[a[1:3],a[3:5],a[5:7]],a[7:10],a[10:16]


def fitted_proposal(x,alpha,obj):
    kind,W,b,c=obj;cap=F(1,8)+sum(x)/16
    def gradient(a):
        vals=[];grads=[]
        for j in range(128):
            y=next_state(x,a,-F(1,32)+F(2*j+1,4096))
            v=c[0]+sum(c[t+1]*y[t] for t in range(2));g=sum(c[t+1]*(F(1,2) if t==0 else F(1,4)) for t in range(2))
            for q in range(3):
                z=b[q]+sum(W[q][t]*y[t] for t in range(2));w=c[3+q]
                v+=w*(z*z if kind=='quadratic' else max(F(0),z))
                slope=2*z if kind=='quadratic' else F(int(z>0))
                g+=w*slope*(W[q][0]/2+W[q][1]/4)
            vals.append(v);grads.append(g)
        k=int(128*(1-alpha));ids=sorted(range(128),key=lambda j:(vals[j],j))[-k:]
        return 2*a+16*a**3+F(15,16)*sum(grads[j] for j in ids)/k
    lo=F(0);hi=cap;gl=gradient(lo);gh=gradient(hi)
    if gl>=0:a=lo
    elif gh<=0:a=hi
    else:
        for _ in range(16):
            a=(lo+hi)/2
            if gradient(a)<0:lo=a
            else:hi=a
        a=(lo+hi)/2
    return F(math.floor(a*2**30),2**30)


def support(x,alpha):
    _,value,a=terminal_bounds(x,alpha,steps=18)
    _,g=objective_gradient(x,a,alpha)
    _,left,right,_=tail_threshold(polynomial_from_primitives(x,a),alpha)
    R=F(1,32);m1=(integral([F(0),F(1)],-R,left)+integral([F(0),F(1)],right,R))/(2*R*(1-alpha))
    zero=next_state(x,a,F(0));plus=next_state(x,a,R)
    g0=economic_gradient(zero,True);gp=economic_gradient(plus,True)
    gy=[g0[j]+(gp[j]-g0[j])*m1/R for j in range(len(x))]
    gx=economic_gradient(x);d=len(x)
    gx=[gx[j]+F(15,16)*(gy[j]*(F(1,2)+(1-x[(j+1)%d])/16)
                        +gy[(j-1)%d]*(F(1,8)-x[(j-1)%d]/16)) for j in range(d)]
    cap=F(1,8)+sum(x)/F(8*d)
    lam=max(F(0),-g) if a==cap else F(0)
    nu=max(F(0),g) if a==0 else F(0)
    e=g+lam-nu
    lower=value+lam*(a-cap)-nu*a-e*e/4
    return lower,value,[v-lam/F(8*d) for v in gx]


def endpoints(x,a,alpha,bins=256):
    R=F(1,32);mids=[];end=[]
    for j in range(bins):
        y=next_state(x,a,-R+(2*j+1)*R/bins)
        mids.append(terminal_bounds(y,alpha,steps=18)[0])
    for j in range(bins+1):
        y=next_state(x,a,-R+2*j*R/bins)
        end.append(terminal_bounds(y,alpha,steps=18)[1])
    upper=[v for j in range(bins) for v in (end[j],end[j+1])]
    base=economic_S(x)+a*a+4*a**4
    return base+F(15,16)*tail(mids,alpha),base+F(15,16)*(tail(upper,alpha)+F(1,2**20))


def original_lower(x,a,alpha,bins=128):
    records=[support(next_state(x,a,-F(1,32)+F(2*j+1,32*bins)),alpha) for j in range(bins)]
    k=int(bins*(1-alpha));ids=sorted(range(bins),key=lambda j:(records[j][0],j))[-k:]
    base=economic_S(x)+a*a+4*a**4
    w=base+F(15,16)*sum(records[j][0] for j in ids)/k
    g=2*a+16*a**3+F(15,16)*sum(records[j][2][0]/2+records[j][2][1]/4 for j in ids)/k
    cap=F(1,8)+sum(x)/16;delta=max(-a,min(cap-a,-g/2))
    return w+g*delta+delta*delta


def endpoint_job96(job):
    index,alpha,arm,j,row,obj=job
    x=[row['x0'],row['x1']];a=row['actions'];reconstructed=None
    if obj is not None:
        reconstructed=fitted_proposal(x,alpha,obj)
        if abs(reconstructed-row['proposed'])>F(1,2**29):
            raise AssertionError(f'Independent proposal disagreement: {index}/{arm}/{j}')
    lo,hi=endpoints(x,a,alpha);lb=original_lower(x,a,alpha)
    if not (row['lower']<=lo<=hi<=row['upper']):
        raise AssertionError(f'Independent enclosure not contained: {index}/{arm}/{j}')
    if hi-lb>TAU:raise AssertionError(f'Independent admission failed: {index}/{arm}/{j}')
    return dict(index=index,arm=arm,row=j,
        proposed_action=str(reconstructed) if reconstructed is not None else None,
        lower=str(lo),upper=str(hi),optimum_lower=str(lb),contained=True)


def audit(tag,fixtures=8):
    out=ROOT/f'results96/evaluation-{tag}';report=json.loads((out/'RESULTS96.json').read_text())
    start=time.perf_counter();receipt=dict(tag=tag,source_commit=report['source_commit'],
        exact_statistics=[],random_endpoints=[],all_rows_checked=0,success=False,
        scope='Independent rational simultaneous means on every row; eight randomly selected endpoint rows per arm-risk stratum. Stored proposals independently reconstructed; conventional proposal selection is not independently replayed.')
    dest=ROOT/f'audit/reproduction96/INDEPENDENT96-{tag}.json'
    # 24 exp(-8) < .05 proved without a floating logarithm or exponential.
    series=sum(F(8)**j/math.factorial(j) for j in range(12))
    if series<=480:raise AssertionError('Simultaneous coverage constant failed')
    for index,alpha in enumerate((F(1,2),F(3,4))):
        arms={arm:load_rows(out/f'alpha-{index}-{arm}.csv') for arm in ARMS}
        for arm,data in arms.items():
            if len(data)!=4096:raise AssertionError('Fixed sample size changed')
            if any(r['loss']>TAU or r['width']>WIDTH or r['lower']>r['upper'] for r in data):raise AssertionError('Invalid admitted observation')
            receipt['all_rows_checked']+=len(data)
        for left,right in itertools.combinations(ARMS,2):
            low=[];high=[]
            for a,b in zip(arms[left],arms[right]):
                if (a['row'],a['x0'],a['x1'])!=(b['row'],b['x0'],b['x1']):raise AssertionError('Pairs are not aligned')
                low.append(max(-TAU,a['lower']-b['upper']));high.append(min(TAU,a['upper']-b['lower']))
                if low[-1]>high[-1]:raise AssertionError('Support contradicted')
            lo=sum(low)/4096-RADIUS;hi=sum(high)/4096+RADIUS
            actual=report['levels'][str(index)]['pairs'][left+' minus '+right]
            if F(actual['interval'][0])>lo or F(actual['interval'][1])<hi:raise AssertionError('Production interval fails exact containment')
            if (hi-lo)/2>=MARGIN/2:raise AssertionError('Prospective resolution budget failed')
            receipt['exact_statistics'].append(dict(index=index,left=left,right=right,
                exact_lower=str(lo),exact_upper=str(hi),production_contains_exact=True))
        for arm in ARMS:
            rng=random.Random(2026101396000+100*index+ARMS.index(arm))
            ids=rng.sample(range(4096),fixtures)
            obj=None if arm=='online-risk-dp' else model(ROOT/f'results96/alpha-{index}/{arm}.bin')
            jobs=[(index,alpha,arm,j,arms[arm][j],obj) for j in ids]
            from concurrent.futures import ProcessPoolExecutor
            import os
            workers=min(4,os.cpu_count() or 1)
            receipt['endpoint_workers']=workers
            receipt['endpoint_execution']='Same fixed fixtures, rational algorithms and ordered records; parallel validation only, no additional observations.'
            with ProcessPoolExecutor(max_workers=workers) as pool:
                for result in pool.map(endpoint_job96,jobs,chunksize=1):
                    receipt['random_endpoints'].append(result)
                    dump(dest,receipt)
    receipt.update(success=True,seconds=time.perf_counter()-start,endpoint_count=len(receipt['random_endpoints']))
    dump(dest,receipt);return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tag',default='primary');p.add_argument('--fixtures',type=int,default=8)
    args=p.parse_args();audit(args.tag,args.fixtures)
