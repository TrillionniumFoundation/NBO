"""New predeclared query distribution, matched directed tolerances.
All frozen plans, gradient-call counts, certificates and timing samples are
retained. Classical acceleration returns its checked search point, avoiding
an artificial extra gradient call merely to check another point.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import sys,json,time,hashlib,math,platform,resource
import numpy as np
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-23-r19'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r17/replication'))
import nonlinear_inventory as N
I,Q=N.I,N.Q
TARGETS=[1e-2,1e-3,1e-4,1e-6]

def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def netload(path):
    d=json.loads(path.read_text());layers=[(np.array(a['weight']),np.array(a['bias'])) for a in d['layers']]
    def forward(x):
        z=x
        for i,(w,b) in enumerate(layers):
            z=w@z+b
            if i<len(layers)-1:z=np.tanh(z)
        return .25*np.tanh(z).reshape(12,len(x))
    return forward,d

def exact_iterations(g2,tol):
    k=0
    while (I(g2)/8*Q(F(145,209))**(2*k)).hi>Q(str(tol)).lo:k+=1
    return k

def curve(x,method,forward,seed,d,query,out,cache,plans):
    tick=time.perf_counter();u=forward(x) if forward else np.zeros((12,d));inference=time.perf_counter()-tick
    previous=u.copy();records=[];remaining=list(TARGETS);online=inference;calls=0
    momentum=(math.sqrt(N.L)-2)/(math.sqrt(N.L)+2)
    for k in range(65):
        tick=time.perf_counter();_,g=N.cost_gradient(x,u);calls+=1;online+=time.perf_counter()-tick
        approx=float(np.sum(g*g)/8)
        check=None
        if k==0 or (remaining and approx<=max(remaining)):
            key=hashlib.sha256(x.tobytes()+u.tobytes()).hexdigest()
            if key not in cache:cache[key]=N.directed_check(x,u)
            check=cache[key]
        if k==0:g0=check['gradient_norm_squared_upper']
        for tol in remaining[:]:
            if check is not None and check['total_cost_loss_upper']<=Q(str(tol)).lo:
                pkey=f'{method}_s{seed}_q{query}_tol{tol:g}';plans[pkey]=u.copy()
                records.append({'d':d,'method':method,'seed':seed,'query':query,'tolerance':tol,'corrections':k,'gradient_calls':calls,
                  'online_generation_seconds':online,'inference_seconds':inference,'final_certificate_seconds':check['verification_seconds'],
                  'initial_gradient_norm_squared_upper':g0,'a_priori_gd_corrections_from_checked_initial':exact_iterations(g0,tol),
                  'plan_key':pkey,'plan_sha256':hashlib.sha256(u.tobytes()).hexdigest(),'status':'PASS','certificate':check,
                  'scope':'exact stored plan at exact stored query; neither a random confidence statement nor a whole-cube neural guarantee'})
                remaining.remove(tol)
        if not remaining:break
        if k<64:
            tick=time.perf_counter()
            if method=='accelerated':
                new=u-g/N.L;u=new+momentum*(new-previous);previous=new
            else:u=u-N.STEP*g
            online+=time.perf_counter()-tick
    for tol in remaining:records.append({'d':d,'method':method,'seed':seed,'query':query,'tolerance':tol,'status':'CAP_REACHED','corrections':64})
    return records

def timed_replay(x,method,forward,k,repeats=5):
    samples=[];momentum=(math.sqrt(N.L)-2)/(math.sqrt(N.L)+2)
    for _ in range(repeats):
        t=time.perf_counter();u=forward(x) if forward else np.zeros((12,len(x)));previous=u.copy()
        for j in range(k+1):
            _,g=N.cost_gradient(x,u)
            if j<k:
                if method=='accelerated':new=u-g/N.L;u=new+momentum*(new-previous);previous=new
                else:u=u-N.STEP*g
        samples.append(time.perf_counter()-t)
    return samples

def experiment(d):
    out=R/f'results/warm_frontier/d{d}';out.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(19200+d);xs=rng.uniform(-1,1,(32,d))
    write(out/'queries.json',{'generator':'numpy default_rng','seed':19200+d,'distribution':'finite uniform measure on the 32 serialized draws; draws generated from the continuous uniform cube','x':xs.tolist()})
    methods=[('zero',None,None,None),('accelerated',None,None,None)]
    for seed in [17400,17401,17402]:
        path=ROOT/f'revisions/2026-09-23-r17/results/nonlinear_inventory/d{d}/network_s{seed}.json';f,meta=netload(path);methods.append(('neural',seed,f,meta))
    rows=[];cache={};plans={};start=time.perf_counter()
    for method,seed,forward,meta in methods:
        for q,x in enumerate(xs):
            rr=curve(x,method,forward,seed,d,q,out,cache,plans)
            for r in rr:
                r['historical_training_seconds']=0. if meta is None else meta['training_seconds']
                if r['status']=='PASS':
                    r['timing_samples_seconds']=timed_replay(x,method,forward,r['corrections'])
                    r['online_median_seconds']=float(np.median(r['timing_samples_seconds']))
                if meta:r['network_path']=f'revisions/2026-09-23-r17/results/nonlinear_inventory/d{d}/network_s{seed}.json';r['network_sha256']=digest(ROOT/r['network_path'])
            rows.extend(rr)
            if q%8==7:print('WARM',d,method,seed,q+1,flush=True);write(out/'records.json',rows)
    write(out/'records.json',rows);np.savez_compressed(out/'plans.npz',**plans)
    write(out/'resources.json',{'seconds':time.perf_counter()-start,'plan_archive_sha256':digest(out/'plans.npz'),'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'historical_training_cost_used':True,'current_query_platform':platform.platform(),'numpy':np.__version__,'mpfr':N.M.VERSION,
        'timing_caveat':'Five-repeat medians; descriptive CPU timing, potentially concurrent checker load. Historical training cost is transferred accounting, not a matched-hardware retraining experiment.'})
    return rows

def summarize(rows):
    summary=[]
    for d in [8,32,128]:
        for tol in TARGETS:
            base={}
            for method in ['zero','accelerated']:
                rr=sorted([r for r in rows if r['d']==d and r['method']==method and r['tolerance']==tol],key=lambda r:r['query'])
                if len(rr)!=32 or any(r['status']!='PASS' for r in rr):raise RuntimeError('Incomplete baseline; retain failure rather than invent frontier')
                base[method]=rr
            for seed in [17400,17401,17402]:
                nn=sorted([r for r in rows if r['d']==d and r['method']=='neural' and r['seed']==seed and r['tolerance']==tol],key=lambda r:r['query'])
                if len(nn)!=32 or any(r['status']!='PASS' for r in nn):raise RuntimeError('Incomplete neural frontier')
                g2n=max(r['initial_gradient_norm_squared_upper'] for r in nn);g2z=max(r['initial_gradient_norm_squared_upper'] for r in base['zero'])
                ntime=float(np.mean([r['online_median_seconds'] for r in nn]));train=nn[0]['historical_training_seconds']
                comparisons={}
                for method,bb in base.items():
                    bt=float(np.mean([r['online_median_seconds'] for r in bb]));saving=bt-ntime
                    bfull=float(np.mean([r['online_median_seconds']+r['final_certificate_seconds'] for r in bb]));nfull=float(np.mean([r['online_median_seconds']+r['final_certificate_seconds'] for r in nn]));sfull=bfull-nfull
                    comparisons[method]={'mean_corrections':float(np.mean([r['corrections'] for r in bb])),
                        'mean_gradient_calls':float(np.mean([r['gradient_calls'] for r in bb])),
                        'mean_online_seconds':bt,'mean_full_query_seconds':bfull,
                        'queries_neural_uses_fewer_gradients':sum(n['gradient_calls']<b['gradient_calls'] for n,b in zip(nn,bb)),
                        'estimated_solver_only_break_even_queries':math.floor(train/saving)+1 if saving>0 else None,
                        'estimated_full_query_break_even_queries':math.floor(train/sfull)+1 if sfull>0 else None}
                summary.append({'d':d,'tolerance':tol,'seed':seed,'query_count':32,'mean_neural_corrections':float(np.mean([r['corrections'] for r in nn])),
                    'mean_neural_gradient_calls':float(np.mean([r['gradient_calls'] for r in nn])),'mean_neural_online_seconds':ntime,
                    'mean_neural_full_query_seconds':nfull,'historical_training_seconds':train,
                    'finite_query_set_gradient_squared_upper':g2n,'finite_query_uniform_gd_corrections_neural':exact_iterations(g2n,tol),
                    'finite_query_uniform_gd_corrections_zero':exact_iterations(g2z,tol),'comparisons':comparisons,
                    'scope':'certified gradient-based loss on the fixed finite query set; timing/amortization estimates are not certificates'})
    write(R/'results/warm_frontier/summary.json',summary)
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--d',type=int);a=p.parse_args()
    if a.d:experiment(a.d)
    else:
        rows=[]
        for d in [8,32,128]:rows.extend(experiment(d))
        summarize(rows)
