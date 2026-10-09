"""Prospectively specified R53 services and independent interval-cost evidence."""
from __future__ import annotations
import argparse, hashlib, itertools, json, math, os, platform, resource, subprocess, sys, time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import directed53 as d
R=Path(__file__).resolve().parents[1];s=d.s;I=d.I;o=d.o
sys.path.insert(0,str(R/'inputs/revisions/2026-10-08-r48/code'))
import direct48 as inference
BITS=5;Q=16;PATHS=65536;BIN_BITS=40;FAMILY=128;LOG=13;ALPHA=F(1,100)
METHODS=('compiled-witness','tensor-fvi')

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:
        json.dump(j,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    return digest(p)
def arrays(p,**kw):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:
        np.savez_compressed(f,**kw);f.flush();os.fsync(f.fileno())
    return digest(p)
def canonical(j):return hashlib.sha256(json.dumps(j,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def cpu_pin():
    if hasattr(os,'sched_getaffinity'):
        z=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{z});return z
    return None

def old_path(T,method):
    n,k,m=(32,4,2) if T==2 else (64,8,4)
    return R/'inputs/revisions/2026-10-08-r49/results/services'/f'{method}-d2-T{T}-p1-r0'/f'checkpoint-N{n}-K{k}-M{m}.json'

def freeze():
    names=['code/directed53.py','code/study53.py','code/tests53.py','STUDY_PROTOCOL53.md']
    inherited=[p for p in (R/'inputs').rglob('*.py')]+[R/'code/operators50.py']
    files=[R/n for n in names]+inherited+[old_path(T,m) for T in (2,3) for m in METHODS]
    save(R/'audit/SOURCE_FREEZE53.json',dict(source_sha256={str(p.relative_to(R)):digest(p) for p in sorted(set(files))},
        protocol_commit='f457e04d36cf95ee80edece5ae99623a4a1854a6',
        time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),bits=BITS,quadrature_bins=Q,paths=PATHS,
        services=[dict(T=T,method=m) for T in (2,3) for m in METHODS],
        scope='scientific source and original checkpoint freeze before production execution; correctness tests are development only'))

def verify_freeze():
    j=json.loads((R/'audit/SOURCE_FREEZE53.json').read_text())
    for n,h in j['source_sha256'].items():
        if digest(R/n)!=h:raise AssertionError('Frozen source changed: '+n)
    return digest(R/'audit/SOURCE_FREEZE53.json')

def service(T,method):
    frozen=verify_freeze();affinity=cpu_pin();start=time.perf_counter();cpu=time.process_time()
    folder=R/'results53/services'/f'{method}-T{T}'
    if folder.exists():raise FileExistsError(folder)
    folder.mkdir(parents=True);prefix=[]
    stop=32 if T==2 else 64
    for n,k,m in s.LADDERS[2]:
        if n>stop:break
        begin=time.perf_counter();payload=s.rung(n,k,m,T,1,method,2)
        h=save(folder/f'construction-N{n}-K{k}-M{m}.json',payload)
        prefix.append(dict(N=n,K=k,M=m,seconds=time.perf_counter()-begin,prefix_seconds=time.perf_counter()-start,
                           policy_bound_upper=payload['policy_bound_upper'],counts=payload['counts'],sha256=h))
    old=json.loads(old_path(T,method).read_text())
    policy_fields=lambda j:{n:j[n] for n in ('models','actors','T','price','dimension','method','N','K','M')}
    if canonical(policy_fields(old))!=canonical(policy_fields(payload)):
        raise AssertionError('Reconstructed original policy differs; service not silently continued')
    construction_seconds=time.perf_counter()-start
    actor=o.AcquiredPolicy(payload,BITS);n=1<<BITS
    bins=np.stack(np.meshgrid(np.arange(n),np.arange(n),indexing='ij'),axis=-1).reshape(-1,2)
    pol=np.array([np.rint(actor._cell_base(t,bins)*4096).astype(np.uint16).reshape(n,n) for t in range(T)])
    snapshots=[pol.copy()];hist=[];bound=[inference.support(T-t,1)[1] for t in range(T)]+[F(0)]
    arrays(folder/'policy-pass0.npz',policy=pol)
    acquisition_seconds=time.perf_counter()-start-construction_seconds
    for k in range(T):
        begin=time.perf_counter();new,report,raw=d.sweep(pol,BITS,Q,1)
        eps=[F(v['greedy_gap_upper']) for v in report['dates']]
        bound=[d.BETA*bound[t+1]+eps[t] for t in range(T)]+[F(0)]
        report.update(pass_number=k+1,gap_upper_exact=list(map(str,bound)),gap_upper=[s.c.enclosure(z)[1] for z in bound])
        report['records_sha256']=arrays(folder/f'pass{k+1}-cells.npz',**raw)
        report['policy_file_sha256']=arrays(folder/f'policy-pass{k+1}.npz',policy=new)
        report['prefix_seconds_through_outputs']=time.perf_counter()-start
        report['seconds_through_outputs']=time.perf_counter()-begin
        save(folder/f'pass{k+1}.json',report);hist.append(report);pol=new;snapshots.append(pol.copy())
        print(json.dumps(dict(service=f'{method}-T{T}',pass_number=k+1,changes=[v['changed_cells'] for v in report['dates']],
                              gap=report['gap_upper'][0],seconds=time.perf_counter()-start)),flush=True)
    record=dict(method=method,T=T,p=1,d=2,sensor_bits=BITS,quadrature_bins=Q,passes=T,
        source_freeze_sha256=frozen,original_checkpoint=str(old_path(T,method).relative_to(R)),
        original_checkpoint_sha256=digest(old_path(T,method)),original_policy_identity_verified=True,
        reconstruction_prefix=prefix,construction_seconds=construction_seconds,acquisition_seconds=acquisition_seconds,
        snapshots=[d.policy_digest(z) for z in snapshots],pass_records=[f'pass{k+1}.json' for k in range(T)],
        total_seconds_before_record=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,affinity=affinity,frequency_controlled=False,
        python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),
        clock_scope='primitives; all original prefix rungs; checkpoint fsync; acquired actor; T all-date passes; full continuous-action lower covers; raw outputs; independent cost service separately itemized')
    h=save(folder/'service.json',record);save(folder/'clock.json',dict(service_sha256=h,seconds_through_record=time.perf_counter()-start))

def radius(stats,A,B):
    n=stats['n'];q=2*F(stats['variance_upper'])*LOG/n;root=math.sqrt(float(q))
    while F(root)**2<q:root=math.nextafter(root,math.inf)
    return F(root)+F(7*LOG,3*(n-1))*(B-A)

def interval_record(lo,hi,A,B):
    aa=s.c.enclosure(A)[0];bb=s.c.enclosure(B)[1]
    lo=np.maximum(aa,lo);hi=np.minimum(bb,hi)
    if np.any(lo>hi):raise AssertionError('Numerical enclosure misses independent deterministic support')
    lm=inference.moments(lo,aa,bb);hm=inference.moments(hi,aa,bb)
    a=max(A,F(lm['mean_lo'])-radius(lm,F(aa),F(bb)));b=min(B,F(hm['mean_hi'])+radius(hm,F(aa),F(bb)))
    return dict(support_exact=[str(A),str(B)],lower_endpoint_moments=lm,upper_endpoint_moments=hm,
        interval_exact=[str(a),str(b)],interval=[s.c.enclosure(a)[0],s.c.enclosure(b)[1]],
        sign='positive' if a>0 else ('negative' if b<0 else 'unresolved'),
        mean_numerical_width=float(np.mean((I(lo,hi)).width())),endpoint_sha256=hashlib.sha256(lo.tobytes()+hi.tobytes()).hexdigest())

def path_score(policy,x,z):
    actors=[d.RectangleActor(a,BITS) for a in policy];T=len(actors);total=d.zero(len(x.lo))
    for t in range(T-1):
        a=actors[t].action(x);total=total+float(d.BETA**t)*s.costs(x,a,1);x=s.transition(x,a,z[t])
    a=actors[-1].action(x);return total+float(d.BETA**(T-1))*o.final_q(x,a,1)

def direct(T):
    verify_freeze();cpu_pin();start=time.perf_counter();out=R/'results53/direct'/f'T{T}'
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);policies=[];keys=[];identities=[]
    for m in METHODS:
        for k in range(T+1):
            p=R/'results53/services'/f'{m}-T{T}'/f'policy-pass{k}.npz'
            pol=np.load(p)['policy'];policies.append(pol);keys.append(f'{m}-pass{k}');identities.append(d.policy_digest(pol))
    seed=int.from_bytes(hashlib.sha256(f'NBO-R53-FROZEN-COST-T{T}-v1'.encode()).digest()[:8],'big')
    rng=np.random.Generator(np.random.PCG64(seed));stream=hashlib.sha256()
    lows=np.empty((len(keys),PATHS));highs=np.empty_like(lows);clocks=np.zeros(len(keys))
    for begin in range(0,PATHS,4096):
        n=min(4096,PATHS-begin);bins=rng.integers(0,2**BIN_BITS,size=(2+T-1,n),dtype=np.uint64);stream.update(bins.tobytes());v=bins.astype(float)
        x=I(v[:2].T*2.**-BIN_BITS,(v[:2].T+1)*2.**-BIN_BITS)
        z=[I(-1/32+v[2+t]*2.**(-BIN_BITS-4),-1/32+(v[2+t]+1)*2.**(-BIN_BITS-4)) for t in range(T-1)]
        for j,pol in enumerate(policies):
            t0=time.perf_counter();score=path_score(pol,x,z);clocks[j]+=time.perf_counter()-t0
            lows[j,begin:begin+n]=score.lo;highs[j,begin:begin+n]=score.hi
    rawhash=arrays(out/'path-endpoints.npz',lower=lows,upper=highs)
    B=inference.support(T,1)[1];absolute={key:interval_record(lows[j],highs[j],F(0),B) for j,key in enumerate(keys)}
    contrasts={}
    for method_index,m in enumerate(METHODS):
        start_index=method_index*(T+1)
        for k in range(1,T+1):
            for initial,name in [(start_index,'initial-gain'),(start_index+k-1,'step-gain')]:
                final=start_index+k
                if identities[initial]==identities[final]:
                    contrasts[f'{m}-pass{k}-{name}']=dict(identity=True,interval=[0.,0.],interval_exact=['0','0'],sign='zero')
                else:
                    diff=I(lows[initial],highs[initial])-I(lows[final],highs[final])
                    # Safety is conditional-expectation dominance, not pathwise dominance.
                    # Negative common-shock path gains must not be clipped away.
                    rec=interval_record(diff.lo,diff.hi,-B,B)
                    rec['expected_gain_nonnegative_by_certificate']=True
                    contrasts[f'{m}-pass{k}-{name}']=rec
    for k in range(T+1):
        diff=I(lows[k],highs[k])-I(lows[T+1+k],highs[T+1+k])
        contrasts[f'witness-minus-fvi-pass{k}']=interval_record(diff.lo,diff.hi,-B,B)
    j=dict(T=T,paths=PATHS,bin_bits=BIN_BITS,seed=seed,stream_sha256=stream.hexdigest(),
        policy_keys=keys,policy_sha256=identities,unique_policy_count=len(set(identities)),
        source_freeze_sha256=verify_freeze(),absolute_cost=absolute,contrasts=contrasts,
        raw_endpoints_sha256=rawhash,evaluation_seconds=dict(zip(keys,clocks)),
        total_seconds_before_record=time.perf_counter()-start,family_maximum=FAMILY,
        family_error='1/100',log_upper=LOG,independence_scope='independent-bin model; common paths across all policies within a horizon; no independence asserted between estimands',
        estimand='actual expected cost of complete acquired policies under original continuous initial and shock laws',
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    h=save(out/'costs.json',j);save(out/'clock.json',dict(costs_sha256=h,seconds_through_record=time.perf_counter()-start))
    print(json.dumps(dict(T=T,costs={k:v['interval'] for k,v in absolute.items()},contrasts={k:v['interval'] for k,v in contrasts.items()})),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--freeze',action='store_true');a.add_argument('--service',choices=METHODS);a.add_argument('--T',type=int,choices=(2,3));a.add_argument('--direct',type=int,choices=(2,3));v=a.parse_args()
    if v.freeze:freeze()
    elif v.service:service(v.T,v.service)
    elif v.direct:direct(v.direct)
    else:a.error('Choose an action')
