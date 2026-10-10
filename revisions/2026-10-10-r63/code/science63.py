"""Source-frozen, isolated complete services; fixed digital deployment workloads.

No workload average is called a continuous-law statistical estimate. The
continuous-law original-optimum guarantee is the proved uniform policy bound.
"""
from __future__ import annotations
import time
PROCESS_START=time.perf_counter()
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,os,platform,resource,subprocess,sys
import numpy as np
import query63 as q
R=Path(__file__).resolve().parents[1]
TASKS=((2,2,128),(8,2,128),(16,2,128),(8,3,32))
TARGETS=('1/32','1/128');SEEDS=(6301,6302);REPEATS=(0,1)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w') as f:json.dump(j,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def freeze():
    files=['PROTOCOL63.md','code/query63.py','code/science63.py','code/tests63.py','sections/query63.tex']
    inherited=[str(p.relative_to(q.BASE)) for p in (q.BASE/'code').glob('*.py')]
    # Bind every ordinary numerical input source, including imported old modules.
    imported={str(p.relative_to(q.BASE)):sha(p) for p in q.BASE.rglob('*.py') if '__pycache__' not in p.parts}
    payload=dict(tasks=TASKS,targets=TARGETS,seeds=SEEDS,repeats=REPEATS,source_sha256={n:sha(R/n) for n in files},inherited_source_sha256=imported,
                 baseline_commit='cfecc5ffcdeb836b1c70e9b98d1dc87f6f8cd097',review_commit='eb02fdb321fe6f26de9caa3afcbe2f84531faef2',
                 source_commit=os.environ.get('NBO63_SOURCE_SHA','local-preproduction'),new_independent_policy_cost_samples=0)
    path=R/'audit/SOURCE_FREEZE63.json'
    if path.exists():raise FileExistsError(path)
    save(path,payload)
def verify():
    f=json.loads((R/'audit/SOURCE_FREEZE63.json').read_text())
    for n,h in f['source_sha256'].items():
        if sha(R/n)!=h:raise AssertionError('Changed frozen source: '+n)
    for n,h in f['inherited_source_sha256'].items():
        if sha(q.BASE/n)!=h:raise AssertionError('Changed inherited source: '+n)
    return sha(R/'audit/SOURCE_FREEZE63.json')
def catalogue():
    result=[]
    for d,T,N in TASKS:
        for target in TARGETS:
            for mode in ('adaptive','bisection','relu','quadratic'):
                for seed in (SEEDS if mode in ('relu','quadratic') else (0,)):
                    for repeat in REPEATS:
                        result.append(dict(d=d,T=T,N=N,target=target,mode=mode,seed=seed,repeat=repeat,
                                           key=f'd{d}-T{T}-e{F(target).denominator}-{mode}-s{seed}-r{repeat}'))
    return result

def exact_stage(x,a,terminal=False):
    d=len(x);short=max(F(0),F(1,2)-2*sum(x)/d)
    value=(4 if terminal else 2)*sum((z-F(5,8))**2 for z in x)/d+sum((x[j]-x[(j+1)%d])**2 for j in range(d))/(4*d)+2*short*short
    return value if terminal else value+a*a+4*a**4

def next_exact(x,a,z):
    d=len(x)
    return [F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16+(F(1,2) if j%2==0 else F(1,4))*a+(1 if j%2==0 else -1)*z for j in range(d)]

def service(spec):
    binding=verify();out=R/'results63'/spec['key']
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);cpus=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpus[0]})
    d,T,N=spec['d'],spec['T'],spec['N'];rng=np.random.default_rng(630000+d*101+T)
    initial=rng.integers(0,2**20,size=(N,d),dtype=np.int64)
    initial[0]=0;initial[1]=2**20;initial[2]=np.tile([0,2**20],d//2);initial[3]=2**20-initial[2]
    initial[4]=2**18;initial[5]=3*2**18;initial[6]=2**19;initial[7]=1
    shocks=rng.integers(-2**15,2**15,size=(T,N),dtype=np.int64)
    models={};fit=None
    if spec['mode'] in ('relu','quadratic'):models,fit=q.fit_models(d,T,spec['seed'],spec['mode'])
    model_payload={str(r):([np.asarray(v).tolist() for v in model] if spec['mode']=='relu' else model.tolist()) for r,model in models.items()}
    save(out/'models.json',model_payload)
    oracle=q.Oracle(spec['mode'],models);tol=q.local_tolerance(T,spec['target']);uniform=q.policy_allowance(T,spec['target'])
    if uniform>float(F(spec['target'])):raise AssertionError('Uniform budget')
    states=[[F(int(z),2**20) for z in row] for row in initial];cost=[F(0)]*N
    arrays=dict(initial=initial,shocks=shocks);certs=[];begin=time.perf_counter()
    for t in range(T):
        obs=np.array([[float((z*2**40).__floor__()/F(2**40)) for z in row] for row in states])
        result=oracle.solve(obs,T-t,tol)
        arrays[f't{t}_observed']=obs
        for name in ('lower','upper','gap','action','probes'):
            arrays[f't{t}_{name}']=result[name]
        arrays[f't{t}_fitted_selected']=result.get('fitted_selected',np.zeros(N,dtype=bool))
        certs.append(dict(date=t,maximum_gap=float(result['gap'].max()),sum_probes=int(result['probes'].sum()),
                          fitted_selected=int(arrays[f't{t}_fitted_selected'].sum())))
        for i in range(N):
            a=F(float(result['action'][i]));x=states[i]
            if not 0<=a<=F(1,8)+sum(x)/(8*d):raise AssertionError('True-state capacity')
            cost[i]+=q.B**t*exact_stage(x,a)
            states[i]=next_exact(x,a,F(int(shocks[t,i]),2**20))
            if not all(0<=z<=1 for z in states[i]):raise AssertionError('State invariance')
    for i in range(N):cost[i]+=q.B**T*exact_stage(states[i],F(0),True)
    deploy_seconds=time.perf_counter()-begin
    trace=out/'trace.npz'
    with trace.open('wb') as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
    save(out/'exact-costs.json',dict(cost=[str(v) for v in cost],mean=str(sum(cost)/N),scope='Fixed dyadic initial/shock workload, including specified boundary paths. Exact rational trajectory costs; not an IID continuous-law cost estimate.'))
    payload=dict(status='returned',spec=spec,source_freeze_sha256=binding,training=fit,training_work=q.APPROX_COUNTS,
                 verification_counts=oracle.counts,dates=certs,uniform_policy_gap_upper=uniform,local_tolerance=tol,
                 deployment_seconds=deploy_seconds,trace_sha256=sha(trace),models_sha256=sha(out/'models.json'),
                 exact_costs_sha256=sha(out/'exact-costs.json'),mean_workload_cost=float(sum(cost)/N),
                 peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,affinity=[cpus[0]],
                 python=sys.version,numpy=np.__version__,platform=platform.platform(),
                 scope='State-grid-free adaptive Bellman service. Neural/quadratic predictions guide queries; neither is a pure policy certificate or a cached conventional fallback.')
    save(out/'summary.json',payload)
    save(out/'clock.json',dict(seconds_from_process_entry_through_summary=time.perf_counter()-PROCESS_START,
                              summary_sha256=sha(out/'summary.json'),boundary='Before imports through fsynced summary; parent receipt includes process startup, this clock write, shutdown, and join.'))

def run_all():
    binding=verify();out=R/'results63';out.mkdir(exist_ok=True);records=[]
    env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
    for i,spec in enumerate(catalogue()):
        path=out/spec['key'];receipt=path/'process-receipt.json'
        if receipt.exists():
            old=json.loads(receipt.read_text())
            if old['source_freeze_sha256']!=binding:raise AssertionError('Resume binding')
            records.append(old);continue
        start=time.perf_counter();log=R/'audit'/('service-'+spec['key']+'.log')
        with log.open('w') as f:
            proc=subprocess.run([sys.executable,__file__,'--service',str(i)],stdout=f,stderr=subprocess.STDOUT,env=env)
        wall=time.perf_counter()-start
        if proc.returncode:raise RuntimeError(spec['key']+' failed: '+log.read_text()[-2000:])
        data=dict(spec=spec,process_wall_seconds=wall,source_freeze_sha256=binding,
                  summary_sha256=sha(path/'summary.json'),clock_sha256=sha(path/'clock.json'),log_sha256=sha(log))
        save(receipt,data);records.append(data)
        save(R/'audit/PROGRESS63.json',dict(completed=len(records),total=len(catalogue()),last=spec['key']))
        print(json.dumps(dict(completed=len(records),key=spec['key'],seconds=wall)),flush=True)
    save(R/'audit/EXECUTION63.json',dict(status='executed',source_freeze_sha256=binding,services=records,
         service_count=len(records),new_independent_continuous_law_cost_samples=0,
         reliability_estimand='Worst observed complete-service work and successful certificate returns over the fixed two-seed catalogue; two repetitions per exact service. No population optimizer-success claim.',
         total_process_seconds=sum(x['process_wall_seconds'] for x in records)))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--run',action='store_true');ap.add_argument('--service',type=int);args=ap.parse_args()
    if args.freeze:freeze()
    elif args.run:run_all()
    elif args.service is not None:service(catalogue()[args.service])
