"""Separate, locally pre-frozen common-accuracy amendment; primary data unchanged."""
from study50 import *

def common_service(d,method,rep):
    key=f'common-{method}-d{d}-r{rep}'
    out=R/'results/commonaccuracy'/key
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);affinity=pin();np.dot(np.ones((8,8)),np.ones((8,8)))
    start=time.perf_counter();alloc=o.plan(d,2,1,5);N,K,M=(alloc[k] for k in ('N','K','M'));attempts=[]
    while N<=64:
        raw=s.rung(N,K,M,2,1,method,d);name=f'checkpoint-N{N}.json';digest=s.save(out/name,raw)
        attempts.append(dict(N=N,K=K,M=M,checkpoint=name,checkpoint_sha256=digest,policy_bound_exact=raw['policy_bound_exact'],policy_bound_upper=raw['policy_bound_upper'],counts=raw['counts'],prefix_seconds_through_checkpoint_fsync=time.perf_counter()-start,checkpoint_bytes=(out/name).stat().st_size))
        if F(raw['policy_bound_exact'])<=5:break
        N*=2
    attained=F(attempts[-1]['policy_bound_exact'])<=5
    counts={k:sum(a['counts'].get(k,0) for a in attempts) for k in attempts[-1]['counts']}
    rec=dict(key=key,dimension=d,method=method,T=2,price=1,target=5,repetition=rep,initial_allocation=alloc,attempts=attempts,attained=attained,returned=attempts[-1] if attained else None,prefix_counts=counts,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,affinity=affinity,seconds_before_record=time.perf_counter()-start)
    h=s.save(out/'record.json',rec);s.save(out/'clock.json',dict(record_sha256=h,seconds_through_record_fsync=time.perf_counter()-start));print(json.dumps(dict(common=key,N=attempts[-1]['N'],attained=attained,seconds=time.perf_counter()-start)),flush=True)

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
    record=dict(spec=spec,paths=PATHS,bin_bits=BITS,sensor_bits=8,action_quantum='1/4096',family_maximum=512,actual_family=30,family_error='1/100',log_upper=13,seed=seed,stream_sha256=stream.hexdigest(),estimand='actual expected discounted acquired-policy cost, final innovation integrated analytically',absolute_cost=absolute,contrasts=contrasts,load_seconds=load_seconds,evaluation_seconds=clocks,seconds_before_record=time.perf_counter()-start,actor_and_gate_counts=[q.counts for q in policies],model_operation_counts=[{name:sum(m.counts.get(name,0) for m in q.models) for name in q.models[0].counts} for q in policies],chunk_mechanism_diagnostics=mechanisms,affinity=affinity,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,clock_scope='joint checkpoint hash checks, compilation/loading, paired interval paths, cell gate, statistical reconstruction; do not splice historical construction clocks')
    digest=s.save(out,record);s.save(out.with_suffix('.clock.json'),dict(record_sha256=digest,seconds_through_record_fsync=time.perf_counter()-start))
    print(json.dumps(dict(direct=spec['key'],before=contrasts['left-minus-right']['interval'],after=contrasts['left-repaired-minus-right-repaired']['interval'],left_gain=contrasts['left-minus-left-repaired']['interval'],seconds=time.perf_counter()-start)),flush=True)

def common_freeze():
    s.save(R/'audit/COMMON_FREEZE.json',dict(time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),scope='local amendment after primary outcomes, before these outcomes',sha256={n:s.H(R/n) for n in ('code/common50.py','COMMON_ACCURACY_AMENDMENT.md','audit/SOURCE_FREEZE.json')},services=18,groups=3,estimands=30))

def common_verify():
    verify_freeze()
    for n,h in s.read(R/'audit/COMMON_FREEZE.json')['sha256'].items():assert s.H(R/n)==h,n

def common_execute():
    common_verify();start=time.perf_counter()
    for rep in range(3):
        methods=('compiled-witness','tensor-fvi') if rep%2==0 else ('tensor-fvi','compiled-witness')
        for d in (2,3,4):
            for method in methods:subprocess.run([sys.executable,__file__,'--cell',str(d),'--method',method,'--rep',str(rep)],check=True)
    specs=[]
    for d in (2,3,4):
        paths=[]
        for method in ('compiled-witness','tensor-fvi'):
            folder=R/'results/commonaccuracy'/f'common-{method}-d{d}-r0';j=s.read(folder/'record.json');assert j['attained'];paths.append(folder/j['returned']['checkpoint'])
        specs.append(dict(key=f'common-d{d}-T2-p1-e5',paths=[str(p.relative_to(R)) for p in paths],hashes=[s.H(p) for p in paths],law='uniform',block='commonaccuracy',T=2,p=1,d=d,target=5))
    s.save(R/'audit/COMMON_DIRECT_CATALOGUE.json',dict(specs=specs,estimands=30))
    for i in range(3):subprocess.run([sys.executable,__file__,'--pair',str(i)],check=True)
    files=list((R/'results/commonaccuracy').rglob('*.json'))+list((R/'results/direct').glob('common-*.json'))
    common_verify();s.save(R/'audit/COMMON_EXECUTION_COMPLETE.json',dict(services=18,groups=3,estimands=30,elapsed_seconds=time.perf_counter()-start,result_sha256={str(p.relative_to(R)):s.H(p) for p in sorted(files)},source_freeze_sha256=s.H(R/'audit/COMMON_FREEZE.json')))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--execute',action='store_true');ap.add_argument('--cell',type=int);ap.add_argument('--method');ap.add_argument('--rep',type=int);ap.add_argument('--pair',type=int);v=ap.parse_args()
    if v.freeze:common_freeze()
    elif v.execute:common_execute()
    elif v.cell:common_verify();common_service(v.cell,v.method,v.rep)
    elif v.pair is not None:common_verify();run_direct(s.read(R/'audit/COMMON_DIRECT_CATALOGUE.json')['specs'][v.pair])
