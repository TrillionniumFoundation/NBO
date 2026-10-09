"""Locally source-frozen R50 prospective construction and actual-policy study."""
from __future__ import annotations
import argparse,hashlib,itertools,json,os,platform,resource,shutil,subprocess,sys,time
from pathlib import Path
from fractions import Fraction as F
import operators50 as o
s=o.s;np=o.np;I=o.I;R=Path(__file__).resolve().parents[1]
import direct49
inference=direct49.inherited
inference.FAMILY=512;inference.LOG=13
PATHS=131072;BITS=40

def specifications():
    cells=[(d,2,1,5) for d in (2,3,4)]+[(2,T,p,2) for T,p in itertools.product((2,3),(1,4))]
    out=[]
    for d,T,p,e in cells:
        for method in ('compiled-witness','tensor-fvi'):
            out.append(dict(key=f'{method}-d{d}-T{T}-p{p}-e{e}-planned',method=method,d=d,T=T,p=p,epsilon=e,allocation='planned'))
    out.append(dict(key='surplus-fvi-d2-T2-p1-e5-planned',method='surplus-fvi',d=2,T=2,p=1,epsilon=5,allocation='planned'))
    for method in ('compiled-witness','tensor-fvi'):
        out.append(dict(key=f'{method}-d2-T2-p1-e5-isotropic',method=method,d=2,T=2,p=1,epsilon=5,allocation='isotropic'))
    assert len(out)==17
    return out

def pin():
    cpus=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else []
    if cpus:os.sched_setaffinity(0,{cpus[0]})
    return cpus[:1]

def one_service(spec,rep):
    out=R/'results/services'/f"{spec['key']}-r{rep}"
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);affinity=pin()
    # Identical non-economic warm-up is excluded from the internal service clock.
    np.dot(np.ones((8,8)),np.ones((8,8)))
    start=time.perf_counter();cpu=time.process_time()
    alloc=o.plan(spec['d'],spec['T'],spec['p'],spec['epsilon'])
    if spec['allocation']=='isotropic':
        a,b,q=s.coefficients(spec['d'],spec['T'],spec['p']);N=4
        while (a+b+q)/N+F(1,10**8)>spec['epsilon']:N*=2
        alloc=dict(status='planned',N=N,K=N,M=N,primitive_bound=str((a+b+q)/N),arithmetic_reserve='1/100000000',target=str(spec['epsilon']),objective='isotropic sufficient allocation',planning_candidates=int(np.log2(N))-1)
    plan_seconds=time.perf_counter()-start
    if alloc['status']!='planned':raise RuntimeError('Predeclared cap failure: '+str(alloc))
    N,K,M=(alloc[q] for q in ('N','K','M'))
    payload=o.surplus_rung(N,K,M,spec['T'],spec['p']) if spec['method']=='surplus-fvi' else s.rung(N,K,M,spec['T'],spec['p'],spec['method'],spec['d'])
    construct_seconds=time.perf_counter()-start
    digest=s.save(out/'checkpoint.json',payload)
    checkpoint_seconds=time.perf_counter()-start
    record=dict(spec=spec,repetition=rep,allocation=alloc,checkpoint='checkpoint.json',checkpoint_sha256=digest,policy_bound_exact=payload['policy_bound_exact'],policy_bound_upper=payload['policy_bound_upper'],attained=F(payload['policy_bound_exact'])<=spec['epsilon'],counts=payload['counts'],nonuniform_date_models=payload['nonuniform_date_models'],planning_seconds=plan_seconds,seconds_before_checkpoint=construct_seconds,seconds_through_checkpoint_fsync=checkpoint_seconds,cpu_seconds=time.process_time()-cpu,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,checkpoint_bytes=(out/'checkpoint.json').stat().st_size,affinity=affinity,python=platform.python_version(),numpy=np.__version__,clock_scope='primitives, planning, all own-future targets, model compilation, actor, verification and checkpoint fsync; process startup and common warm-up excluded')
    h=s.save(out/'record.json',record)
    s.save(out/'clock.json',dict(record_sha256=h,seconds_through_record_fsync=time.perf_counter()-start))
    print(json.dumps(dict(service=spec['key'],rep=rep,gap=record['policy_bound_upper'],attained=record['attained'],seconds=time.perf_counter()-start)),flush=True)

def direct_catalogue():
    specs=[]
    def add(paths,key,law,block,**meta):
        specs.append(dict(key=key,paths=[str(p.relative_to(R)) for p in paths],hashes=[s.H(p) for p in paths],law=law,block=block,**meta))
    for T,p in itertools.product((2,3),(1,4)):
        paths=[]
        for method in ('compiled-witness','tensor-fvi'):
            folder=R/'inputs/revisions/2026-10-08-r49/results/services'/f'{method}-d2-T{T}-p{p}-r0'
            crossing=s.read(folder/'record.json')['first_crossings']['2'];path=folder/crossing['checkpoint'];assert s.H(path)==crossing['checkpoint_sha256'];paths.append(path)
        for law in ('uniform','1/8','1/2','7/8'):add(paths,f'legacy-T{T}-p{p}-{law.replace("/","_")}',law,'legacy',T=T,p=p,d=2,target=2)
    cells=[(d,2,1,5) for d in (2,3,4)]+[(2,T,p,2) for T,p in itertools.product((2,3),(1,4))]
    for d,T,p,e in cells:
        paths=[R/'results/services'/f'{method}-d{d}-T{T}-p{p}-e{e}-planned-r0/checkpoint.json' for method in ('compiled-witness','tensor-fvi')]
        add(paths,f'planned-d{d}-T{T}-p{p}-e{e}','uniform','planned',T=T,p=p,d=d,target=e)
    paths=[R/'results/services'/f'{method}-d2-T2-p1-e5-planned-r0/checkpoint.json' for method in ('surplus-fvi','tensor-fvi')]
    add(paths,'surplus-d2-T2-p1-e5','uniform','surplus',T=2,p=1,d=2,target=5)
    paths=[R/'results/services'/f'{method}-d2-T2-p1-e5-isotropic-r0/checkpoint.json' for method in ('compiled-witness','tensor-fvi')]
    add(paths,'isotropic-d2-T2-p1-e5','uniform','isotropic',T=2,p=1,d=2,target=5)
    assert len(specs)==25
    return specs

def interval_record(lo,hi,a,b):
    A=s.c.enclosure(a)[0];B=s.c.enclosure(b)[1]
    lo=np.maximum(A,lo);hi=np.minimum(B,hi)
    if np.any(lo>hi):raise AssertionError('Empty deterministic support')
    lm=inference.moments(lo,A,B);hm=inference.moments(hi,A,B);lower,upper=inference.confidence(lm,hm,A,B)
    # Intersect with exact support; this cannot reduce coverage.
    lower=max(a,lower);upper=min(b,upper)
    return dict(support_exact=[str(a),str(b)],lower_endpoint_moments=lm,upper_endpoint_moments=hm,interval_exact=[str(lower),str(upper)],interval=[s.c.enclosure(lower)[0],s.c.enclosure(upper)[1]],sign='lower' if upper<0 else ('higher' if lower>0 else 'unresolved'),endpoint_sha256=hashlib.sha256(lo.tobytes()+hi.tobytes()).hexdigest(),mean_numerical_width=float(np.mean(hi-lo)),maximum_numerical_width=float(np.max(hi-lo)))

def run_direct(spec):
    out=R/'results/direct'/f"{spec['key']}.json"
    if out.exists():raise FileExistsError(out)
    affinity=pin();start=time.perf_counter();paths=[R/p for p in spec['paths']]
    assert [s.H(p) for p in paths]==spec['hashes']
    policies=[o.AcquiredPolicy(s.read(p),8) for p in paths];load_seconds=time.perf_counter()-start
    T,p,d=(spec[q] for q in ('T','p','d'))
    bound=inference.support(T,p)[1]
    seed=int.from_bytes(hashlib.sha256(('NBO-R50-LOCAL-FROZEN-v1:'+spec['key']).encode()).digest()[:8],'big')
    rng=np.random.Generator(np.random.PCG64(seed));stream=hashlib.sha256()
    lows=np.empty((4,PATHS));highs=np.empty((4,PATHS));dlo=np.empty((2,PATHS));dhi=np.empty((2,PATHS));clocks=[0.,0.];mechanisms=[[],[]]
    for begin in range(0,PATHS,4096):
        n=min(4096,PATHS-begin);bins=rng.integers(0,2**BITS,size=(d+T-1,n),dtype=np.uint64);stream.update(bins.tobytes());v=bins.astype(float)
        x=I(v[:d].T*2.**-BITS,(v[:d].T+1)*2.**-BITS) if spec['law']=='uniform' else I.point(np.full((n,d),float(F(spec['law']))))
        z=[I(-1/32+v[d+t]*2.**(-BITS-4),-1/32+(v[d+t]+1)*2.**(-BITS-4)) for t in range(T-1)]
        for k,policy in enumerate(policies):
            t0=time.perf_counter();old,new,delta,diag=policy.paired_scores(x,z);clocks[k]+=time.perf_counter()-t0;mechanisms[k].append(diag)
            for j,val in enumerate((old,new)):lows[2*k+j,begin:begin+n]=val.lo;highs[2*k+j,begin:begin+n]=val.hi
            dlo[k,begin:begin+n]=delta.lo;dhi[k,begin:begin+n]=delta.hi
    names=['left','left-repaired','right','right-repaired'];absolute={name:interval_record(lows[k],highs[k],F(0),bound) for k,name in enumerate(names)};contrasts={}
    for i,j in itertools.combinations(range(4),2):
        if (i,j) in ((0,1),(2,3)):
            k=i//2;ll,hh=-dhi[k],-dlo[k];a,b=F(0),bound
        else:ll,hh=lows[i]-highs[j],highs[i]-lows[j];a,b=-bound,bound
        contrasts[f'{names[i]}-minus-{names[j]}']=interval_record(ll,hh,a,b)
    record=dict(spec=spec,paths=PATHS,bin_bits=BITS,sensor_bits=8,action_quantum='1/4096',family_maximum=512,actual_family=250,family_error='1/100',log_upper=13,seed=seed,stream_sha256=stream.hexdigest(),estimand='actual expected discounted acquired-policy cost, final innovation integrated analytically',absolute_cost=absolute,contrasts=contrasts,load_seconds=load_seconds,evaluation_seconds=clocks,seconds_before_record=time.perf_counter()-start,actor_and_gate_counts=[q.counts for q in policies],model_operation_counts=[{name:sum(m.counts.get(name,0) for m in q.models) for name in q.models[0].counts} for q in policies],chunk_mechanism_diagnostics=mechanisms,affinity=affinity,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,clock_scope='joint checkpoint hash checks, compilation/loading, paired interval paths, cell gate, statistical reconstruction; do not splice historical construction clocks')
    digest=s.save(out,record);s.save(out.with_suffix('.clock.json'),dict(record_sha256=digest,seconds_through_record_fsync=time.perf_counter()-start))
    print(json.dumps(dict(direct=spec['key'],before=contrasts['left-minus-right']['interval'],after=contrasts['left-repaired-minus-right-repaired']['interval'],left_gain=contrasts['left-minus-left-repaired']['interval'],seconds=time.perf_counter()-start)),flush=True)

def freeze():
    files=list((R/'code').glob('*.py'))+[R/'STUDY_PROTOCOL.md']+[p for p in (R/'inputs').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    s.save(R/'audit/SOURCE_FREEZE.json',dict(scope='local pre-execution freeze, not remote preregistration',time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),sha256={str(p.relative_to(R)):s.H(p) for p in sorted(files)},specifications=specifications(),services=51,policy_groups=25,paths_per_group=PATHS,estimands=250))

def verify_freeze():
    for n,h in s.read(R/'audit/SOURCE_FREEZE.json')['sha256'].items():assert s.H(R/n)==h,n

def execute():
    verify_freeze();start=time.perf_counter();env=os.environ.copy()
    env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    specs=specifications()
    for rep in range(3):
        ordered=specs[rep:]+specs[:rep]
        for spec in ordered:subprocess.run([sys.executable,__file__,'--service',spec['key'],'--repeat',str(rep)],check=True,env=env)
    catalogue=direct_catalogue();s.save(R/'audit/DIRECT_CATALOGUE.json',dict(specs=catalogue,scope='fixed before new direct outcomes',actual_estimands=250))
    for index in range(len(catalogue)):subprocess.run([sys.executable,__file__,'--direct',str(index)],check=True,env=env)
    verify_freeze()
    files=sorted((R/'results').rglob('*.json'))
    s.save(R/'audit/EXECUTION_COMPLETE.json',dict(services=51,groups=25,estimands=250,elapsed_seconds=time.perf_counter()-start,result_sha256={str(p.relative_to(R)):s.H(p) for p in files},source_freeze_sha256=s.H(R/'audit/SOURCE_FREEZE.json')))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--execute',action='store_true');ap.add_argument('--service');ap.add_argument('--repeat',type=int);ap.add_argument('--direct',type=int);v=ap.parse_args()
    if v.freeze:freeze()
    elif v.execute:execute()
    elif v.service:verify_freeze();one_service(next(q for q in specifications() if q['key']==v.service),v.repeat)
    elif v.direct is not None:verify_freeze();run_direct(s.read(R/'audit/DIRECT_CATALOGUE.json')['specs'][v.direct])
