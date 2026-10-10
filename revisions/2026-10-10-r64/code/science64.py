"""Prospective isolated-process comparison of gated and unconditional queries.

Original continuous-law certificate; exact finite dyadic workload diagnostics.
No workload path is counted as an independent continuous-law cost observation.
"""
import time
ENTRY=time.perf_counter()
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,os,resource,subprocess,sys
import numpy as np
import query64 as g
q=g.q
import science63 as old
R=Path(__file__).resolve().parents[1]
TASKS=((2,2,128),(8,2,128),(16,2,128),(8,3,32))
TARGETS=('1/32','1/128');SEEDS=(6401,6402)
MODES=('adaptive','bisection','relu-insert','relu-route','quadratic-insert','quadratic-route')

def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w') as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def catalogue():
    result=[]
    for d,T,N in TASKS:
        for target in TARGETS:
            for mode in MODES:
                for seed in (SEEDS if '-' in mode else (0,)):
                    for repeat in (0,1):
                        result.append(dict(d=d,T=T,N=N,target=target,mode=mode,seed=seed,repeat=repeat,
                            key=f'd{d}-T{T}-e{F(target).denominator}-{mode}-s{seed}-r{repeat}'))
    return result

def freeze():
    inherited=old.verify()
    p=R/'audit/SOURCE_FREEZE64.json'
    if p.exists():raise FileExistsError(p)
    names=['PROTOCOL64.md','code/query64.py','code/science64.py','code/tests64.py','sections/gated64.tex']
    save(p,dict(baseline_commit='cfecc5ffcdeb836b1c70e9b98d1dc87f6f8cd097',
        review_commit='eb02fdb321fe6f26de9caa3afcbe2f84531faef2',
        completed_R63_commit='7128155b146d647adc39b0accd1ba483877853cc',
        source_commit=os.environ.get('GITHUB_SHA','local-engineering'),
        source_sha256={n:digest(R/n) for n in names},inherited_freeze_sha256=inherited,
        catalogue=catalogue(),new_independent_continuous_law_cost_samples=0))
def verify():
    j=read(R/'audit/SOURCE_FREEZE64.json')
    for n,h in j['source_sha256'].items():
        if digest(R/n)!=h:raise AssertionError('Changed frozen source: '+n)
    if old.verify()!=j['inherited_freeze_sha256']:raise AssertionError('Inherited source freeze differs')
    return digest(R/'audit/SOURCE_FREEZE64.json')

def service(spec):
    binding=verify();out=R/'results64'/spec['key']
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu})
    d,T,N=spec['d'],spec['T'],spec['N'];rng=np.random.default_rng(640000+d*101+T)
    initial=rng.integers(0,2**20,size=(N,d),dtype=np.int64)
    initial[:8]=np.array([np.zeros(d),np.full(d,2**20),np.tile([0,2**20],d//2),np.tile([2**20,0],d//2),np.full(d,2**18),np.full(d,3*2**18),np.full(d,2**19),np.ones(d)],dtype=np.int64)
    shocks=rng.integers(-2**15,2**15,size=(T,N),dtype=np.int64)
    mode=spec['mode'];kind=mode.split('-')[0];models={};fit=None
    if '-' in mode:models,fit=q.fit_models(d,T,spec['seed'],kind)
    payload={str(r):([np.asarray(a).tolist() for a in model] if kind=='relu' else model.tolist()) for r,model in models.items()}
    save(out/'models.json',payload)
    engine=q.Oracle if mode.endswith('-insert') else g.Oracle
    oracle=engine(kind,models);tol=q.local_tolerance(T,spec['target']);uniform=q.policy_allowance(T,spec['target'])
    if uniform>float(F(spec['target'])):raise AssertionError('Uniform policy budget')
    states=[[F(int(z),2**20) for z in row] for row in initial];cost=[F(0)]*N
    arrays=dict(initial=initial,shocks=shocks);dates=[];begin=time.perf_counter()
    for t in range(T):
        obs=np.array([[float(F((z*2**40).__floor__(),2**40)) for z in row] for row in states])
        val=oracle.solve(obs,T-t,tol);arrays[f't{t}_observed']=obs
        for n in ('lower','upper','gap','action','probes'):arrays[f't{t}_{n}']=val[n]
        arrays[f't{t}_fitted_selected']=val.get('fitted_selected',np.zeros(N,dtype=bool))
        dates.append(dict(date=t,maximum_gap=float(val['gap'].max()),sum_probes=int(val['probes'].sum()),fitted_selected=int(arrays[f't{t}_fitted_selected'].sum())))
        if np.any(val['gap']>tol):raise AssertionError('Returned local gap exceeds contract')
        for i in range(N):
            a=F(float(val['action'][i]));x=states[i]
            if not 0<=a<=F(1,8)+sum(x)/(8*d):raise AssertionError('True-state infeasibility')
            cost[i]+=q.B**t*old.exact_stage(x,a)
            states[i]=old.next_exact(x,a,F(int(shocks[t,i]),2**20))
            if not all(0<=v<=1 for v in states[i]):raise AssertionError('State invariance')
    for i in range(N):cost[i]+=q.B**T*old.exact_stage(states[i],F(0),True)
    deployment=time.perf_counter()-begin
    with (out/'trace.npz').open('wb') as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
    save(out/'exact-costs.json',dict(cost=list(map(str,cost)),mean=str(sum(cost)/N),scope='Exact costs for the fixed dyadic workload; not IID continuous-law estimates.'))
    save(out/'summary.json',dict(status='returned',spec=spec,source_freeze_sha256=binding,
        training=fit,training_work=q.APPROX_COUNTS,verification_counts=oracle.counts,dates=dates,
        uniform_policy_gap_upper=uniform,local_tolerance=tol,deployment_seconds=deployment,
        trace_sha256=digest(out/'trace.npz'),models_sha256=digest(out/'models.json'),exact_costs_sha256=digest(out/'exact-costs.json'),
        mean_workload_cost=float(sum(cost)/N),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        affinity=[cpu],python=sys.version,numpy=np.__version__,
        scope='Isolated complete original-economy controller; no precomputed state lattice or common policy. Gated predictions replace a required query location.'))
    save(out/'clock.json',dict(seconds_from_entry_through_summary=time.perf_counter()-ENTRY,
        summary_sha256=digest(out/'summary.json'),boundary='Process entry through durable summary; parent receipt includes startup, final clock, shutdown and join.'))

def run_all():
    binding=verify();(R/'results64').mkdir(exist_ok=True);records=[]
    env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
    for i,spec in enumerate(catalogue()):
        out=R/'results64'/spec['key'];receipt=out/'process-receipt.json'
        if receipt.exists():
            j=read(receipt)
            if j['source_freeze_sha256']!=binding:raise AssertionError('Resume source mismatch')
            records.append(j);continue
        log=R/'audit'/('service-'+spec['key']+'.log');start=time.perf_counter()
        with log.open('w') as f:p=subprocess.run([sys.executable,__file__,'--service',str(i)],stdout=f,stderr=subprocess.STDOUT,env=env)
        wall=time.perf_counter()-start
        if p.returncode:
            save(R/'audit/FAILED_SERVICE64.json',dict(spec=spec,returncode=p.returncode,wall_seconds=wall,log_sha256=digest(log)))
            raise RuntimeError('Service failed: '+spec['key']+'\n'+log.read_text()[-3000:])
        j=dict(spec=spec,process_wall_seconds=wall,source_freeze_sha256=binding,summary_sha256=digest(out/'summary.json'),clock_sha256=digest(out/'clock.json'),log_sha256=digest(log))
        save(receipt,j);records.append(j)
        save(R/'audit/PROGRESS64.json',dict(completed=len(records),total=len(catalogue()),last=spec['key']))
        print(json.dumps(dict(completed=len(records),key=spec['key'],seconds=wall)),flush=True)
    save(R/'audit/EXECUTION64.json',dict(status='executed',source_freeze_sha256=binding,services=records,
        service_count=len(records),total_process_seconds=sum(x['process_wall_seconds'] for x in records),
        reliability_estimand='All fixed task/target/method/seed services, two complete-process repetitions; not a population training-success estimate.',
        new_independent_continuous_law_cost_samples=0))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--run',action='store_true');ap.add_argument('--service',type=int);a=ap.parse_args()
    if a.freeze:freeze()
    elif a.run:run_all()
    elif a.service is not None:service(catalogue()[a.service])
