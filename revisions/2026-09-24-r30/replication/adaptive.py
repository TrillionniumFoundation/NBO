"""Exact regional certificates for a stopped operating-mode economy.

Training uses floating point; compilation, bounds, deployment and economic
integrals use rational arithmetic. No certificate depends on a sampled test.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse, hashlib, heapq, json, math, platform, time
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[3]
REV=Path(__file__).resolve().parents[1]
GAMMA=F(171,200); T=8; EPS=F(1,100)
H=sum(GAMMA**j for j in range(T)); ETA=EPS/H
MODELS={'linear':[-F(3,8),F(1)],
        'cubic':[-F(32,25), F(264,25),-F(24),F(16)],
        'quadratic':[F(889,5000),-F(33,25),F(2)]}

def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,default=str)+'\n')
def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,default=str).encode()).hexdigest()
def val(c,x):
    z=F(0)
    for a in reversed(c): z=z*x+a
    return z
def bernstein(c,l,r):
    """Exact power-to-Bernstein conversion on [l,r]."""
    n=len(c)-1; h=r-l
    power=[sum(c[j]*math.comb(j,k)*l**(j-k)*h**k for j in range(k,n+1)) for k in range(n+1)]
    b=[sum(power[k]*F(math.comb(i,k),math.comb(n,k)) for k in range(i+1)) for i in range(n+1)]
    return min(b),max(b)
def integral(c,l,r,density=(F(0),F(2))):
    return sum(a*b*(r**(i+j+1)-l**(i+j+1))/F(i+j+1) for i,a in enumerate(c) for j,b in enumerate(density))
def mass(l,r,priority=False):
    return integral([F(1)],l,r,(F(0),F(2),F(2)) if priority else (F(0),F(2)))
def nnval(params,x):
    w,b,v,o=[[F(z) for z in row] if isinstance(row,list) else F(row) for row in params]
    return o+sum(vv*max(F(0),ww*x+bb) for ww,bb,vv in zip(w,b,v))
def compile_nn(params):
    w,b,v,o=[[F(z) for z in row] if isinstance(row,list) else F(row) for row in params]
    breaks={F(0),F(1)}
    for ww,bb in zip(w,b):
        if ww and 0<-bb/ww<1:breaks.add(-bb/ww)
    coarse=sorted(breaks)
    for l,r in zip(coarse,coarse[1:]):
        m=(l+r)/2; a=F(0);z=o
        for ww,bb,vv in zip(w,b,v):
            if ww*m+bb>0:a+=vv*ww;z+=vv*bb
        if a and l<-z/a<r:breaks.add(-z/a)
    bps=sorted(breaks)
    segments=[(l,r,int(nnval(params,(l+r)/2)>=0)) for l,r in zip(bps,bps[1:])]
    points={x:int(nnval(params,x)>=0) for x in bps}
    return segments,points

def constant(a):return [(F(0),F(1),a)],{F(0):a,F(1):a}

def complete(c,segments,points,eta=ETA):
    if eta<0:raise ValueError('negative tolerance')
    leaves=[]; calls=0
    def visit(l,r,a,depth):
        nonlocal calls
        calls+=1; sign=1 if a==0 else -1
        lo,hi=bernstein([sign*z for z in c],l,r)
        # Retain whenever every point passes. Change only with certified
        # dominance; isolate the tolerance boundary, not every model state.
        if hi<=eta:chosen=a; forced=False
        elif lo>eta:chosen=1-a;forced=True
        elif depth>=36 and lo>=0:chosen=1-a;forced=False
        else:
            if depth>=60:raise RuntimeError('unresolved regional certificate')
            m=(l+r)/2;visit(l,m,a,depth+1);visit(m,r,a,depth+1);return
        leaves.append({'l':str(l),'r':str(r),'raw':a,'action':chosen,
                       'raw_gap_lo':str(lo),'raw_gap_hi':str(hi),'forced':forced})
    for l,r,a in segments:visit(l,r,a,0)
    p=[]
    # Include ALL leaf boundaries, not just neural breakpoints. This removes
    # any ambiguity of tie/endpoint conventions, including finite grids.
    boundary=set(points)|{F(z[k]) for z in leaves for k in ('l','r')}
    def raw_at(x):
        if x in points:return points[x]
        return next(a for l,r,a in segments if l<x<r)
    for x in sorted(boundary):
        a=raw_at(x);d=(1-2*a)*val(c,x)
        p.append({'x':str(x),'raw':a,'action':a if d<=eta else 1-a})
    return {'eta':str(eta),'leaves':leaves,'points':p,'bound_calls':calls}

def verify(c,cert):
    eta=F(cert['eta']);assert eta>=0
    leaves=cert['leaves'];assert leaves and F(leaves[0]['l'])==0 and F(leaves[-1]['r'])==1
    last=F(0);changed=F(0);weighted=F(0);forced=F(0);gain=F(0);length=F(0);worst=F(0);bits=0
    for row in leaves:
        l,r=F(row['l']),F(row['r']);a,b=row['raw'],row['action']
        assert l==last and l<r;last=r;assert a in (0,1) and b in (0,1)
        lo,hi=bernstein([(1-2*a)*z for z in c],l,r)
        assert lo==F(row['raw_gap_lo']) and hi==F(row['raw_gap_hi'])
        if a==b:assert hi<=eta;worst=max(worst,hi)
        else:
            assert lo>=0
            changed+=mass(l,r);weighted+=mass(l,r,True);length+=r-l
            gain+=(b-a)*integral(c,l,r)
            if row['forced']:assert lo>eta;forced+=mass(l,r,True)
        bits=max(bits,*[max(z.numerator.bit_length(),z.denominator.bit_length()) for z in (l,r,lo,hi)])
    pts=cert['points'];expected={F(z[k]) for z in leaves for k in ('l','r')}
    assert {F(z['x']) for z in pts}==expected
    assert len(pts)==len(expected)
    for p in pts:
        x=F(p['x']);a,b=p['raw'],p['action'];assert a in (0,1) and b in (0,1)
        d=(1-2*b)*val(c,x);assert d<=eta
        assert (b-a)*val(c,x)>=0;worst=max(worst,d)
    assert H*max(F(0),worst)<=H*eta
    return {'guaranteed_regret':str(H*max(F(0),worst)),
            'occupancy_edits':str(H*changed),'priority_edits':str(H*weighted),
            'minimum_priority_cost_lower':str(H*forced),
            'minimum_priority_cost_upper':str(H*weighted),
            'extra_cost_bound':str(H*(weighted-forced)),
            'expected_payoff_gain':str(H*gain),'hamming_measure':str(length),
            'max_certificate_integer_bits':bits,'leaf_count':len(leaves),'point_count':len(pts)}

def deploy_index(cert,i,m):
    """Exact rational comparisons, including every boundary/tie.

    A binary64 neural forward pass is deliberately NOT the deployed object.
    """
    if not isinstance(i,int) or not isinstance(m,int) or m<0 or not 0<=i<2**m:raise ValueError('invalid grid index')
    x=F(2*i+1,2**(m+1))
    for p in cert['points']:
        if x==F(p['x']):return p['action']
    for p in cert['leaves']:
        if F(p['l'])<x<F(p['r']):return p['action']
    raise ValueError('incomplete certificate')

def positive_integral(c,l,r,tol=F(1,10**12)):
    lo,hi=bernstein(c,l,r)
    if hi<=0:return F(0),F(0)
    if lo>=0:
        q=integral(c,l,r);return q,q
    if r-l<=tol:return F(0),max(F(0),hi)*mass(l,r)
    m=(l+r)/2;a,b=positive_integral(c,l,m,tol);d,e=positive_integral(c,m,r,tol)
    return a+d,b+e

def maximum(c,l,r,tol=F(1,10**9)):
    lo,hi=bernstein(c,l,r);best=max(val(c,l),val(c,r),val(c,(l+r)/2));heap=[(-hi,l,r)]
    while heap and -heap[0][0]>best+tol:
        _,a,b=heapq.heappop(heap);m=(a+b)/2
        for x,y in ((a,m),(m,b)):
            _,u=bernstein(c,x,y);best=max(best,val(c,(x+y)/2))
            if u>best:heapq.heappush(heap,(-u,x,y))
    return best,max(best,-heap[0][0] if heap else best)

def raw_regret(c,segments,points):
    il=iu=mxlo=mxhi=F(0)
    for l,r,a in segments:
        q=[(1-2*a)*z for z in c];lo,hi=positive_integral(q,l,r);il+=lo;iu+=hi
        lo,hi=maximum(q,l,r);mxlo=max(mxlo,lo);mxhi=max(mxhi,hi)
    for x,a in points.items():mxlo=max(mxlo,(1-2*a)*val(c,x));mxhi=max(mxhi,mxlo)
    return {'worst_regret_lower':str(mxlo+(H-1)*il),'worst_regret_upper':str(mxhi+(H-1)*iu),
            'mean_regret_lower':str(H*il),'mean_regret_upper':str(H*iu)}

def train(c,width,seed,method):
    torch.manual_seed(seed);torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
    net=torch.nn.Sequential(torch.nn.Linear(1,width),torch.nn.ReLU(),torch.nn.Linear(width,1))
    x=(torch.arange(512,dtype=torch.float64)+.5).reshape(-1,1)/512
    y=sum(float(a)*x**j for j,a in enumerate(c))
    calls=0;t=time.perf_counter()
    if method=='adam':
        op=torch.optim.Adam(net.parameters(),lr=.02)
        for _ in range(200):
            op.zero_grad();loss=((net(x)-y)**2).mean();loss.backward();op.step();calls+=1
    else:
        op=torch.optim.LBFGS(net.parameters(),max_iter=200,line_search_fn='strong_wolfe')
        def closure():
            nonlocal calls
            op.zero_grad();loss=((net(x)-y)**2).mean();loss.backward();calls+=1;return loss
        op.step(closure)
    elapsed=time.perf_counter()-t
    params=[net[0].weight.detach().reshape(-1).tolist(),net[0].bias.detach().tolist(),
            net[2].weight.detach().reshape(-1).tolist(),float(net[2].bias.detach().item())]
    rational=[[str(F(v)) for v in z] if isinstance(z,list) else str(F(z)) for z in params]
    return rational,{'training_seconds':elapsed,'objective_gradient_calls':calls,'training_mse':float(((net(x)-y)**2).mean().detach())}

def run():
    out=REV/'results/adaptive';out.mkdir(parents=True,exist_ok=True);allrows=[];events=[]
    started=time.perf_counter()
    # Freeze all candidates in the complete declared cohort before evaluation.
    cohort=[]
    for model,c in MODELS.items():
        for width in (8,16):
            for method in ('adam','lbfgs'):
                for seed in range(30001,30006):
                    p,rec=train(c,width,seed,method);tag=f'{model}_{method}_w{width}_s{seed}'
                    payload={'params':p,'record':rec,'model':model,'tag':tag}
                    save(out/'candidates'/f'{tag}.json',payload)
                    events.append({'event':'candidate_frozen','tag':tag,'sha256':digest(payload)})
                    cohort.append((tag,model,p,rec,width,method,seed))
    save(out/'FREEZE_MANIFEST.json',events)
    for tag,model,p,rec,width,method,seed in cohort:
        c=MODELS[model];t=time.perf_counter();segments,points=compile_nn(p);comp=time.perf_counter()-t
        save(out/'compiled'/f'{tag}.json',{'segments':segments,'points':[[x,a] for x,a in points.items()]})
        t=time.perf_counter();cert=complete(c,segments,points);ct=time.perf_counter()-t
        t=time.perf_counter();metrics=verify(c,cert);vt=time.perf_counter()-t
        t=time.perf_counter();raw=raw_regret(c,segments,points);rt=time.perf_counter()-t
        save(out/'certificates'/f'{tag}.json',cert)
        allrows.append(dict(tag=tag,model=model,method=method,width=width,seed=seed,**rec,**metrics,**raw,
                            compilation_seconds=comp,certification_seconds=ct,independent_check_seconds=vt,
                            reference_diagnostic_seconds=rt,bound_calls=cert['bound_calls'],
                            certificate_bytes=(out/'certificates'/f'{tag}.json').stat().st_size,
                            raw_action_regions=len(segments),certificate_sha256=digest(cert)))
        print(tag,'raw',float(F(raw['worst_regret_upper'])),'leaves',len(cert['leaves']),flush=True)
    baselines=[]
    for model,c in MODELS.items():
        for action in (0,1):
            s,p=constant(action);t=time.perf_counter();ce=complete(c,s,p);ct=time.perf_counter()-t
            metrics=verify(c,ce);save(out/'baselines'/f'{model}_constant{action}.json',ce)
            baselines.append(dict(model=model,method=f'constant{action}',seconds=ct,bound_calls=ce['bound_calls'],**metrics))
        # Strong structure-aware optimizer: same Bernstein oracle, no proposal.
        # eta/2 assigns the sign at uncertain zero cells and bounds its regret.
        for tol,label in ((ETA,'structured_matched'),(F(1,10**12),'structured_near_exact')):
            t=time.perf_counter();s,p=constant(0);ce=complete(c,s,p,tol);ct=time.perf_counter()-t
            metrics=verify(c,ce);save(out/'baselines'/f'{model}_{label}.json',ce)
            baselines.append(dict(model=model,method=label,seconds=ct,bound_calls=ce['bound_calls'],**metrics))
        # Polynomial least squares is an exact-class approximation control.
        x=(np.arange(512)+.5)/512;t=time.perf_counter();cf=np.polynomial.polynomial.polyfit(x,np.polynomial.polynomial.polyval(x,list(map(float,c))),len(c)-1)
        baselines.append(dict(model=model,method='polynomial_fit',seconds=time.perf_counter()-t,coefficients=cf.tolist()))
        # Vectorized full dynamic programming; all actions and model information
        # matched, not the slower scalar implementation from the older study.
        for m in (8,12,20):
            t=time.perf_counter();N=2**m;x=(np.arange(N,dtype=float)+.5)/N;g=np.polynomial.polynomial.polyval(x,list(map(float,c)));w=2*x/N
            v=np.zeros(N);policy=np.empty((T,N),dtype=np.uint8)
            for stage in range(T-1,-1,-1):
                continuation=float(GAMMA)*np.dot(w,v);q0=x/5+continuation;q1=q0+g
                policy[stage]=(q1>=q0);v=np.maximum(q0,q1)
            baselines.append(dict(model=model,method='vectorized_dp',m=m,states=N,seconds=time.perf_counter()-t,
                                  action_values=T*N*2,array_bytes=x.nbytes+g.nbytes+w.nbytes+v.nbytes+policy.nbytes,
                                  arithmetic='binary64 diagnostic, not the rational certificate'))
    save(out/'summary.json',allrows);save(out/'baselines.json',baselines)
    save(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'torch':torch.__version__,
        'platform':platform.platform(),'threads':torch.get_num_threads(),'total_seconds':time.perf_counter()-started,
        'H':str(H),'eta':str(ETA),'state_grids':[8,12,20,40],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'models':MODELS,'study_status':'exploratory; cohort frozen before certification; no seed selection'})
    print('DONE',len(allrows),time.perf_counter()-started,flush=True)

if __name__=='__main__':run()
