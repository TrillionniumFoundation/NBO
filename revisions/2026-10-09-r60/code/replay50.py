"""Numerical endpoint correction. Replay the same draws, preserve original records."""
from study50 import *
def run_direct(spec):
    out=R/'results/direct-verified'/f"{spec['key']}.json"
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
        else:
            ll=np.nextafter(lows[i]-highs[j],-np.inf);hh=np.nextafter(highs[i]-lows[j],np.inf);a,b=-bound,bound
        contrasts[f'{names[i]}-minus-{names[j]}']=interval_record(ll,hh,a,b)
    record=dict(spec=spec,paths=PATHS,bin_bits=BITS,sensor_bits=8,action_quantum='1/4096',family_maximum=512,actual_family=280,family_error='1/100',log_upper=13,seed=seed,stream_sha256=stream.hexdigest(),estimand='actual expected discounted acquired-policy cost, final innovation integrated analytically',absolute_cost=absolute,contrasts=contrasts,load_seconds=load_seconds,evaluation_seconds=clocks,seconds_before_record=time.perf_counter()-start,actor_and_gate_counts=[q.counts for q in policies],model_operation_counts=[{name:sum(m.counts.get(name,0) for m in q.models) for name in q.models[0].counts} for q in policies],chunk_mechanism_diagnostics=mechanisms,affinity=affinity,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,clock_scope='joint checkpoint hash checks, compilation/loading, paired interval paths, cell gate, statistical reconstruction; do not splice historical construction clocks')
    digest=s.save(out,record);s.save(out.with_suffix('.clock.json'),dict(record_sha256=digest,seconds_through_record_fsync=time.perf_counter()-start))
    print(json.dumps(dict(direct=spec['key'],before=contrasts['left-minus-right']['interval'],after=contrasts['left-repaired-minus-right-repaired']['interval'],left_gain=contrasts['left-minus-left-repaired']['interval'],seconds=time.perf_counter()-start)),flush=True)

def replay_freeze():
    s.save(R/'audit/REPLAY_FREEZE.json',dict(time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),reason='One outward rounding step for cross-policy endpoint subtraction; same exact bin stream and frozen policies, not new data',sha256={n:s.H(R/n) for n in ('code/replay50.py','NUMERICAL_CORRECTION.md','audit/SOURCE_FREEZE.json','audit/COMMON_FREEZE.json')},groups=28,estimands=280))
def replay_verify():
    verify_freeze()
    for n,h in s.read(R/'audit/REPLAY_FREEZE.json')['sha256'].items():assert s.H(R/n)==h,n

def replay_execute():
    replay_verify();start=time.perf_counter();specs=s.read(R/'audit/DIRECT_CATALOGUE.json')['specs']+s.read(R/'audit/COMMON_DIRECT_CATALOGUE.json')['specs']
    for i in range(len(specs)):subprocess.run([sys.executable,__file__,'--index',str(i)],check=True)
    files=sorted((R/'results/direct-verified').glob('*.json'));replay_verify()
    s.save(R/'audit/VERIFIED_EXECUTION_COMPLETE.json',dict(groups=28,estimands=280,elapsed_seconds=time.perf_counter()-start,result_sha256={str(p.relative_to(R)):s.H(p) for p in files},source_freeze_sha256=s.H(R/'audit/REPLAY_FREEZE.json')))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--execute',action='store_true');ap.add_argument('--index',type=int);v=ap.parse_args()
    if v.freeze:replay_freeze()
    elif v.execute:replay_execute()
    elif v.index is not None:
        replay_verify();specs=s.read(R/'audit/DIRECT_CATALOGUE.json')['specs']+s.read(R/'audit/COMMON_DIRECT_CATALOGUE.json')['specs'];run_direct(specs[v.index])
