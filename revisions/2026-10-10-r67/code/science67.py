"""Source-frozen R67 corrected comparison, reuse, inference and vector services.

The parent clock includes process launch, imports, fitting/loading, all policy
queries, interval path evaluation, durable records, shutdown and join. No old
policy, cost sample or timing is substituted for a new service.
"""
import time
ENTRY=time.perf_counter()
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,os,resource,subprocess,sys,traceback
import numpy as np
import kernel66 as k
q=k.q;I=k.I;B=k.B
import core62 as c
R=Path(__file__).resolve().parents[1]
BITS=24;BINBITS=48
TASKS=((2,2,'1/128',64),(8,3,'1/64',32))
SEEDS=tuple(range(6601,6609));INFER_N=8192;BLOCKS=24
ENV={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def archive(p,**arrays):
    with Path(p).open('wb') as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
def support(T):return sum(B**t*F(103,64) for t in range(T))+B**T*F(37,16)
def budget(T,target):
    S=sum(B**t for t in range(T));delta=float(F(target)/(2*S))
    allowance=(F(8)+F(297,16)*B+27)/2**BITS
    total=(F(delta)+allowance)*S
    if total>F(target):raise AssertionError('Uniform acquisition budget')
    return delta,str(total)
def specs():
    rows=[]
    for d,T,e,N in TASKS:
        for kind in k.KINDS:
            for seed in (SEEDS if kind in k.LEARNED else (0,)):
                for rep in (0,1):rows.append(dict(group='comparison',d=d,T=T,target=e,N=N,kind=kind,seed=seed,repeat=rep))
        for kind in ('adaptive','bisection','relu','quadratic'):
            for seed in ((6603,6607) if kind in k.LEARNED else (0,)):
                for rep in (0,1):rows.append(dict(group='reuse',d=d,T=T,target=e,N=128 if T==2 else 32,kind=kind,seed=seed,repeat=rep))
        rows.append(dict(group='inference',d=d,T=T,target=e,N=INFER_N,kind='paired',seed=6603,repeat=0))
    for d in (2,8):
        for T in (2,3,4):rows.append(dict(group='vector',d=d,T=T,target='1/4',N=4,kind='simplicial',seed=0,repeat=0))
    for i,row in enumerate(rows):row['index']=i;row['key']=f"{row['group']}-d{row['d']}-T{row['T']}-{row['kind']}-s{row['seed']}-r{row['repeat']}"
    return rows

def freeze():
    p=R/'audit/SOURCE_FREEZE67.json'
    if p.exists():raise FileExistsError(p)
    names=['PROTOCOL67.md']+[str(f.relative_to(R)) for f in sorted((R/'code').glob('*.py')) if f.name in ('kernel66.py','vector66.py','science67.py','tests67.py')]
    dependencies={}
    for folder in ('2026-10-10-r63/code','2026-10-10-r64/code','2026-10-10-r62'):
        for f in (R.parent/folder).rglob('*.py'):dependencies[str(f.relative_to(R.parent))]=sha(f)
    save(p,dict(source_commit=os.environ.get('GITHUB_SHA','local-development'),source_sha256={n:sha(R/n) for n in names},
        inherited_python_sha256=dependencies,reviewed_commit='34a5ce17dc3ac4681b6d004eca00637f28104e28',catalogue=specs(),
        acquisition_bits=BITS,continuous_bin_bits=BINBITS,inference_rows_per_task=INFER_N,reuse_blocks=BLOCKS,
        source_freeze_scope='Before the corrected R67 rerun; same fixed streams as R66, not additional independent observations. Original R66 records remain unchanged.'))
def verify():
    j=read(R/'audit/SOURCE_FREEZE67.json')
    for name,h in j['source_sha256'].items():
        if sha(R/name)!=h:raise AssertionError('Changed source '+name)
    for name,h in j['inherited_python_sha256'].items():
        if sha(R.parent/name)!=h:raise AssertionError('Changed dependency '+name)
    if j['catalogue']!=specs():raise AssertionError('Changed catalogue')
    return sha(R/'audit/SOURCE_FREEZE67.json')

def workload(d,T,N,seed,continuous=False,vector=False):
    rng=np.random.default_rng(seed);den=2**BINBITS
    x=rng.integers(0,den,size=(N,d),dtype=np.int64)
    z=rng.integers(0,den,size=(T,N),dtype=np.int64)
    w=rng.integers(0,den,size=(T,N),dtype=np.int64) if vector else np.zeros((T,N),dtype=np.int64)
    lo=x/den;hi=(x+1)/den
    if not continuous:
        count=min(N,4);named=np.array([np.zeros(d),np.ones(d),np.full(d,.25),np.full(d,.75)])[:count]
        lo[:count]=named;hi[:count]=named
    return dict(initial_index=x,shock_index=z,second_shock_index=w),I(lo,hi)

def paths(oracle,initial,randoms,T,target,vector=False,keep=True):
    N,d=initial.lo.shape;delta,uniform=budget(T,target);state=initial;cost=I(np.zeros(N),np.zeros(N));alive=np.ones(N,dtype=bool)
    final_lo=np.zeros(N);final_hi=np.zeros(N);arrays={};dates=[];den=2**BINBITS
    for t in range(T):
        # The proved invariant cube is an additional valid enclosure.
        state=I(np.maximum(0,state.lo),np.minimum(1,state.hi))
        obslo=np.floor(state.lo*2**BITS)/2**BITS;obshi=np.floor(state.hi*2**BITS)/2**BITS
        certain=np.all(obslo==obshi,axis=1);ambiguous=alive&~certain
        if ambiguous.any():
            ids=np.flatnonzero(ambiguous);final_lo[ids]=cost.lo[ids]
            final_hi[ids]=(I.point(cost.hi[ids])+q.rat(B**t*support(T-t))).hi;alive[ids]=False
        ids=np.flatnonzero(alive);a=np.zeros((N,2)) if vector else np.zeros(N)
        act=np.full(a.shape,np.nan);gaps=np.full(N,np.nan);lower=gaps.copy();upper=gaps.copy();observed=np.full((N,d),np.nan)
        if len(ids):
            v=oracle.solve(obslo[ids],T-t,delta)
            if np.any(v['gap']>delta):raise AssertionError('Failed local certificate')
            a[ids]=v['action'];act[ids]=v['action'];gaps[ids]=v['gap'];lower[ids]=v['lower'];upper[ids]=v['upper'];observed[ids]=obslo[ids]
            aa=I.point(a[ids] if vector else a[ids,None]);xx=I(state.lo[ids],state.hi[ids])
            if np.any(aa.hi.sum(axis=1)>c.capacity(xx).lo):raise AssertionError('True-state infeasibility')
            val=I(cost.lo[ids],cost.hi[ids])+q.rat(B**t)*c.stage(xx,aa)
            cost.lo[ids]=val.lo;cost.hi[ids]=val.hi
            zi=randoms['shock_index'][t,ids];z=I(zi/(16*den)-1/32,(zi+1)/(16*den)-1/32)
            if vector:
                wi=randoms['second_shock_index'][t,ids];w=I(wi/(32*den)-1/64,(wi+1)/(32*den)-1/64)
            else:w=0.
            y=c.transition(xx,aa,z,w);state.lo[ids]=y.lo;state.hi[ids]=y.hi
        dates.append(dict(date=t,active=len(ids),ambiguous=int(ambiguous.sum()),max_local_gap=float(np.nanmax(gaps)) if len(ids) else None))
        if keep:
            arrays.update({f't{t}_observed':observed,f't{t}_action':act,f't{t}_lower':lower,f't{t}_upper':upper,f't{t}_gap':gaps})
    ids=np.flatnonzero(alive)
    if len(ids):
        val=I(cost.lo[ids],cost.hi[ids])+q.rat(B**T)*c.terminal(I(state.lo[ids],state.hi[ids]));final_lo[ids]=val.lo;final_hi[ids]=val.hi
    if np.any(final_lo>final_hi) or not np.isfinite(final_hi).all():raise AssertionError('Path enclosure')
    arrays.update(cost_lo=final_lo,cost_hi=final_hi)
    return arrays,dict(dates=dates,ambiguous_paths=int((~alive).sum()),uniform_policy_gap_exact=uniform,local_tolerance=delta,
                       path_cost_mean_interval=[float(final_lo.mean()),float(final_hi.mean())],statistical_model='IID uniform bin indices and independent within-bin continuous coordinates' if keep else 'finite path diagnostics')

def packed_diagnostics(oracle):
    progress=np.concatenate(oracle.progress) if getattr(oracle,'progress',[]) else np.zeros((0,13))
    screens=np.concatenate(oracle.screens) if getattr(oracle,'screens',[]) else np.zeros((0,8))
    return dict(progress=progress,screens=screens)

def infer_interval(lo,hi,H,tail=F(1,4000)):
    # Maurer--Pontil sample-variance bound, applied separately to the two
    # endpoint samples. Independent rows, not independent methods, are used.
    N=len(lo);log=9.
    if tail!=F(1,4000):raise ValueError('Undeclared inference tail allocation')
    out=[]
    for values,lower in ((lo,True),(hi,False)):
        z=I.point(values);mean=q.n.s.isum(z)/N
        deviation=z-I.point(mean.midpoint());var=q.n.s.isum(deviation.square())/(N-1)
        rad=I.point(np.nextafter(np.sqrt((2*var*I.point(log)/N).hi),np.inf))+q.rat(F(7,3)*H)*I.point(log)/(N-1)
        out.append(float((mean-rad).lo if lower else (mean+rad).hi))
    return out

def service(s):
    binding=verify();out=R/'results67'/s['key']
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu})
    d,T,N=s['d'],s['T'],s['N'];kind=s['kind'];summary=dict(spec=s,source_freeze_sha256=binding,affinity=[cpu],python=sys.version,numpy=np.__version__)
    if s['group']=='comparison':
        models,fit=k.fit(d,T,s['seed'],kind);save(out/'model.json',dict(kind=kind,models=k.dump_models(kind,models)))
        oracle=k.Oracle(kind,models,record=True);randoms,initial=workload(d,T,N,661000+d*101+T)
        start=time.perf_counter();arrays,account=paths(oracle,initial,randoms,T,s['target']);elapsed=time.perf_counter()-start
        archive(out/'trace.npz',**randoms,**arrays,**packed_diagnostics(oracle))
        summary.update(status='returned',training=fit,account=account,counts=oracle.counts,deployment_seconds=elapsed,
                       model_sha256=sha(out/'model.json'),trace_sha256=sha(out/'trace.npz'),continuous_law_observations=0)
    elif s['group']=='reuse':
        models,fit=k.fit(d,T,s['seed'],kind);identity=dict(kind=kind,d=d,T=T,target=s['target'],bits=BITS,source=binding)
        payload=dict(identity=identity,models=k.dump_models(kind,models));save(out/'model.json',payload);modelsha=sha(out/'model.json')
        initial_seconds=time.perf_counter()-ENTRY;records=[];cumulative=initial_seconds
        for block in range(BLOCKS):
            start=time.perf_counter();loaded=read(out/'model.json')
            # One declared stale-identity case; no corruption of the saved file.
            if block==7:loaded['identity']={**loaded['identity'],'bits':BITS+1}
            valid=loaded['identity']==identity and sha(out/'model.json')==modelsha
            chosen=kind if valid else 'adaptive';mm=k.load_models(kind,loaded['models']) if valid else {}
            loadseconds=time.perf_counter()-start
            oracle=k.Oracle(chosen,mm);randoms,initial=workload(d,T,N,662000+d*1009+T*97+block,continuous=True)
            arrays,account=paths(oracle,initial,randoms,T,s['target']);archive(out/f'block{block:02d}.npz',**randoms,**arrays)
            record=dict(block=block,identity_valid=valid,used_kind=chosen,load_seconds=loadseconds,counts=oracle.counts,account=account,trace_sha256=sha(out/f'block{block:02d}.npz'))
            save(out/f'block{block:02d}.json',record);elapsed=time.perf_counter()-start;cumulative+=elapsed
            records.append(dict(**record,seconds_through_durable_record=elapsed,cumulative_seconds=cumulative))
        summary.update(status='returned',training=fit,initial_service_seconds=initial_seconds,blocks=records,model_sha256=modelsha,continuous_law_observations=0,
                       reuse_scope='24 new prospectively named workloads; block 7 has a stale acquisition contract and uses the conventional verifier; model loading, hashing, all queries and durable trace charged')
    elif s['group']=='inference':
        randoms,initial=workload(d,T,N,663000+d*1009+T,continuous=True);archive(out/'random-inputs.npz',**randoms)
        all_lo=[];all_hi=[];arms=[]
        for kind in ('adaptive','bisection','relu','quadratic'):
            start=time.perf_counter();models,fit=k.fit(d,T,s['seed'],kind);save(out/(kind+'-model.json'),k.dump_models(kind,models))
            oracle=k.Oracle(kind,models);parts=[];accounts=[]
            for first in range(0,N,512):
                end=min(N,first+512);rr={key:(v[first:end] if key=='initial_index' else v[:,first:end]) for key,v in randoms.items()}
                arrays,account=paths(oracle,I(initial.lo[first:end].copy(),initial.hi[first:end].copy()),rr,T,s['target']);parts.append(arrays);accounts.append(account)
            combined={key:np.concatenate([v[key] for v in parts]) for key in parts[0]};archive(out/(kind+'-paths.npz'),**combined)
            all_lo.append(combined['cost_lo']);all_hi.append(combined['cost_hi']);arms.append(dict(kind=kind,training=fit,counts=oracle.counts,
                ambiguous_paths=sum(x['ambiguous_paths'] for x in accounts),model_sha256=sha(out/(kind+'-model.json')),trace_sha256=sha(out/(kind+'-paths.npz')),seconds=time.perf_counter()-start))
        lo=np.maximum(0,np.stack(all_lo));hi=np.minimum(q.up(support(T)),np.stack(all_hi));archive(out/'path-endpoints.npz',lower=lo,upper=hi)
        H=F(q.up(support(T)));absolute={arm['kind']:infer_interval(lo[j],hi[j],H) for j,arm in enumerate(arms)};contrasts={}
        for a,b in __import__('itertools').combinations(range(4),2):
            diff=I(lo[a],hi[a])-I(lo[b],hi[b]);contrasts[arms[a]['kind']+'-minus-'+arms[b]['kind']]=infer_interval(np.maximum(-float(H),diff.lo),np.minimum(float(H),diff.hi),2*H)
        summary.update(status='returned',arms=arms,absolute_cost=absolute,contrasts=contrasts,raw_endpoint_sha256=sha(out/'path-endpoints.npz'),
                       random_inputs_sha256=sha(out/'random-inputs.npz'),continuous_law_observations=N,simultaneous_family_error='1/100',
                       family_scope='all 4 absolute costs and 6 paired differences at both declared tasks; at most 40 endpoint tails each of probability 1/4000',
                       inference_scope='Conditional on the frozen fitted controllers, IID uniform-bin model with outward original-continuous-law path enclosures; fresh seed fixes reproducibility, not a theorem of pseudorandom independence')
    else:
        import vector66 as v
        oracle=v.Oracle(batch=2048);randoms,initial=workload(d,T,N,664000+d*1009+T,continuous=False,vector=True)
        arrays,account=paths(oracle,initial,randoms,T,s['target'],vector=True);archive(out/'trace.npz',**randoms,**arrays)
        summary.update(status='returned',account=account,counts=oracle.counts,trace_sha256=sha(out/'trace.npz'),continuous_law_observations=0,
                       extension='same capacity-coupled two-control, two-innovation R62 primitives, with no stored state table and adaptive triangular action cover')
    summary['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;save(out/'summary.json',summary)
    save(out/'clock.json',dict(seconds_from_entry_through_summary=time.perf_counter()-ENTRY,summary_sha256=sha(out/'summary.json')))

def run_all():
    binding=verify();(R/'results67').mkdir(exist_ok=True);records=[]
    for s in specs():
        out=R/'results67'/s['key'];receipt=out/'receipt.json';log=R/'audit'/('service-'+s['key']+'.log')
        if receipt.exists():
            old=read(receipt)
            if old['source_freeze_sha256']!=binding:raise AssertionError('Resume identity')
            records.append(old);continue
        start=time.perf_counter()
        with log.open('w') as f:
            try:
                proc=subprocess.run([sys.executable,__file__,'--service',str(s['index'])],env=ENV,stdout=f,stderr=subprocess.STDOUT,timeout=900)
                status='returned' if proc.returncode==0 else 'failed';code=proc.returncode
            except subprocess.TimeoutExpired:status='timeout';code=None
        record=dict(spec=s,status=status,returncode=code,process_wall_seconds=time.perf_counter()-start,source_freeze_sha256=binding,log_sha256=sha(log))
        if status=='returned':record.update(summary_sha256=sha(out/'summary.json'),clock_sha256=sha(out/'clock.json'))
        out.mkdir(exist_ok=True);save(receipt,record);records.append(record)
        save(R/'audit/PROGRESS67.json',dict(completed=len(records),total=len(specs()),last=record))
        print(json.dumps(dict(completed=len(records),key=s['key'],status=status,seconds=record['process_wall_seconds'])),flush=True)
    save(R/'audit/EXECUTION67.json',dict(status='executed',source_freeze_sha256=binding,services=records,returned=sum(r['status']=='returned' for r in records),
        failed=sum(r['status']=='failed' for r in records),timed_out=sum(r['status']=='timeout' for r in records),service_count=len(records),
        total_process_seconds=sum(r['process_wall_seconds'] for r in records),observations_scope='Independent-bin inference rows are counted only in the two inference services, not repeated method arms, workload rows or process repetitions.'))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--run',action='store_true');ap.add_argument('--service',type=int);args=ap.parse_args()
    if args.freeze:freeze()
    elif args.run:run_all()
    elif args.service is not None:service(specs()[args.service])
