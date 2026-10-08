"""Prospective first-attainment services. No R53/R54 outcome is resampled.

Each target has its own from-primitives process, error allocation, inference
stream, stop or budget-exhaustion record, and all-in process clock.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,platform,resource,sys,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import neural55 as n
import study53 as old
R=Path(__file__).resolve().parents[1]
TASKS=((2,2),(4,4),(8,6));TARGETS=(F(9,10),F(49,50));REPEATS=3
RUNGS=((256,32,4),(1024,128,8));LOOKS=(4096,16384,65536)
KINDS=('relu','quadratic','extra-trees');FAMILY=2048;LOG=14;ALPHA=F(1,100)


def save(p,v):return old.save(p,v)
def arrays(p,**kw):return old.arrays(p,**kw)
def canonical(v):return old.canonical(v)
def policy_hash(p,part):return canonical(dict(policy=np.asarray(p).tolist(),partition=part.payload()))
def source_paths():
    return [R/'STUDY_PROTOCOL55.md']+[R/'code'/f for f in ('neural55.py','prospective55.py','null55.py','tests55.py')]+[R/'code'/f for f in ('operators50.py','directed53.py','study53.py')]+sorted((R/'inputs').rglob('*.py'))
def freeze():
    return save(R/'audit/SOURCE_FREEZE55.json',dict(source_sha256={str(p.relative_to(R)):old.digest(p) for p in source_paths()},protocol='STUDY_PROTOCOL55.md',utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),python=platform.python_version(),numpy=np.__version__,scope='Frozen before new production services. Development tests use disjoint tiny tasks and seeds.'))
def verify():
    for path,h in json.loads((R/'audit/SOURCE_FREEZE55.json').read_text())['source_sha256'].items():
        if old.digest(R/path)!=h:raise AssertionError('Frozen source changed: '+path)
    return old.digest(R/'audit/SOURCE_FREEZE55.json')
def ci(lo,hi,A,B):
    if sum((F(LOG)**j/math.factorial(j) for j in range(80)),F(0))<=4*FAMILY/ALPHA:raise AssertionError('Insufficient family logarithm')
    aa=n.s.c.enclosure(A)[0];bb=n.s.c.enclosure(B)[1];lo=np.maximum(aa,lo);hi=np.minimum(bb,hi)
    if np.any(lo>hi):raise AssertionError('Invalid support intersection')
    lm=old.inference.moments(lo,aa,bb);hm=old.inference.moments(hi,aa,bb)
    def rad(st):
        size=st['n'];q=2*F(st['variance_upper'])*LOG/size;v=math.sqrt(float(q))
        while F(v)**2<q:v=math.nextafter(v,math.inf)
        return F(v)+F(7*LOG,3*(size-1))*(F(bb)-F(aa))
    l=max(A,F(lm['mean_lo'])-rad(lm));u=min(B,F(hm['mean_hi'])+rad(hm))
    return dict(exact=[str(l),str(u)],interval=[n.s.c.enclosure(l)[0],n.s.c.enclosure(u)[1]],lower_moments=lm,upper_moments=hm)

def inference(policy,part,T,target,folder,stage):
    seed=int.from_bytes(hashlib.sha256(f'NBO-R55-INFERENCE-d{part.d}-T{T}-q{target}-s{stage}'.encode()).digest()[:8],'big')
    rng=np.random.Generator(np.random.PCG64(seed));lo=[];hi=[];zl=[];zh=[];looks=[];zero=np.zeros_like(policy)
    begin=time.perf_counter();stream=hashlib.sha256();previous=0;H=old.inference.support(T,1)[1]
    for look in LOOKS:
        for start in range(previous,look,2048):
            count=min(2048,look-start);bins=rng.integers(0,2**40,size=(part.d+T-1,count),dtype=np.uint64);stream.update(bins.tobytes());v=bins.astype(float)
            x=n.I(v[:part.d].T*2.**-40,(v[:part.d].T+1)*2.**-40)
            z=[n.I(-1/32+v[part.d+t]*2.**-44,-1/32+(v[part.d+t]+1)*2.**-44) for t in range(T-1)]
            p=n.score(policy,part,x,z);b=n.score(zero,part,x,z)
            lo.extend(p.lo);hi.extend(p.hi);zl.extend(b.lo);zh.extend(b.hi)
        p=n.I(np.array(lo),np.array(hi));b=n.I(np.array(zl),np.array(zh));delta=p-n.s.c.rat_i(target)*b;gain=b-p
        cost=ci(p.lo,p.hi,F(0),H);check=ci(delta.lo,delta.hi,-target*H,H);g=ci(gain.lo,gain.hi,-H,H)
        crossed=F(check['exact'][1])<=0
        raw=arrays(folder/f'stage{stage}-look{look}.npz',policy_lo=p.lo,policy_hi=p.hi,zero_lo=b.lo,zero_hi=b.hi)
        record=dict(stage=stage,paths=look,seed=seed,stream_sha256=stream.hexdigest(),cost=cost,target_contrast=check,gain=g,crossed=crossed,raw_sha256=raw,numerical_path_width=float(p.width().max()),seconds_through_raw=time.perf_counter()-begin)
        save(folder/f'stage{stage}-look{look}.json',record);looks.append(record);previous=look
        if crossed:break
        # An interval strictly above the target avoids spending the larger look.
        # Failure is not declared globally: a later construction stage is tried.
        if F(check['exact'][0])>0:break
    return crossed,looks

def service(d,T,kind,target,repeat):
    frozen=verify();affinity=old.cpu_pin();start=time.perf_counter();cpu=time.process_time();target=F(target)
    key=f'{kind}-d{d}-T{T}-q{target.numerator}_{target.denominator}-r{repeat}';folder=R/'results55/services'/key
    folder.mkdir(parents=True,exist_ok=False);oldpart=None;policy=None;stages=[];bound=[old.inference.support(T-t,1)[1] for t in range(T)]+[F(0)];allcounts=0
    for k,(samples,leaves,q) in enumerate(RUNGS):
        stage_start=time.perf_counter();part=n.Partition(d,leaves)
        if oldpart is None:policy=np.zeros((T,leaves),dtype=np.uint16)
        else:policy=policy[:,oldpart.locate(part.centers)]
        before=policy_hash(policy,part)
        critics,training=n.train(kind,d,T,samples,55001+d*100+T*10+k)
        proposed=n.propose(critics,part);construction=time.perf_counter()-stage_start
        cache_start=time.perf_counter();cache=n.Cache(critics,part,policy,q);cache_seconds=time.perf_counter()-cache_start
        gate_start=time.perf_counter();updated,report,raw=cache.sweep(proposed);gate_seconds=time.perf_counter()-gate_start
        bound=[n.BETA*bound[t+1]+F(report[t]['gap']) for t in range(T)]+[F(0)]
        for t in range(T):
            for name in ('err','direct','ranges'):
                band=getattr(cache,name)[t];raw[f't{t}_{name}_lo']=band.lo;raw[f't{t}_{name}_hi']=band.hi
        rawhash=arrays(folder/f'stage{k}-certificate.npz',**raw)
        modelhash=save(folder/f'stage{k}-models.json',dict(critics=[c.payload() for c in critics],training=training,partition=part.payload(),policy=updated.tolist(),proposals=proposed.tolist()))
        allcounts+=part.membership_tests;verifyqueries=part.box_queries;ambiguities=part.ambiguous_boxes
        met,looks=inference(updated,part,T,target,folder,k)
        record=dict(stage=k,samples=samples,leaves=leaves,innovation_bins=q,construction_seconds=construction,cache_seconds=cache_seconds,gate_seconds=gate_seconds,verification_membership_comparisons=allcounts,verification_box_queries=verifyqueries,ambiguous_verification_boxes=ambiguities,
            critic_evaluated_rows=sum(c.work for c in critics),residuals=cache.residuals,dates=report,before_policy_sha256=before,after_policy_sha256=policy_hash(updated,part),certificate_sha256=rawhash,models_sha256=modelhash,all_state_gap_exact=list(map(str,bound)),all_state_gap_upper=[n.s.c.enclosure(x)[1] for x in bound],look_files=[f'stage{k}-look{x["paths"]}.json' for x in looks],target_attained=met,prefix_seconds=time.perf_counter()-start)
        save(folder/f'stage{k}.json',record);stages.append(record);policy=updated;oldpart=part
        if met:break
    files={str(p.relative_to(folder)):old.digest(p) for p in folder.iterdir() if p.is_file()}
    freq=Path(f'/sys/devices/system/cpu/cpu{affinity}/cpufreq/scaling_governor')
    rec=dict(key=key,d=d,T=T,kind=kind,target=str(target),repeat=repeat,status='target_attained' if met else 'budget_exhausted',stages=stages,files_sha256=files,
        source_freeze_sha256=frozen,final_policy_sha256=policy_hash(policy,part),own_inference=True,own_construction=True,cpu_affinity=affinity,frequency_controlled=False,governor=freq.read_text().strip() if freq.exists() else None,
        python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cpu_seconds=time.process_time()-cpu,seconds_before_record=time.perf_counter()-start,
        timing_repetition='identical training and inference seeds; three isolated sequential processes per service; not independent training samples',statistical_family=dict(alpha=str(ALPHA),maximum_intervals=FAMILY,log_upper=LOG),scope='first attained prespecified expected-cost ratio to zero investment under original continuous law; statewise nonworsening verified at every complete sweep; budget exhaustion is not unattainability')
    h=save(folder/'service.json',rec);save(folder/'clock.json',dict(record_sha256=h,seconds_through_record_fsync=time.perf_counter()-start))
    print(json.dumps(dict(key=key,status=rec['status'],passes=len(stages),seconds=time.perf_counter()-start,changes=[sum(x['changed'] for x in z['dates']) for z in stages])),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--freeze',action='store_true');a.add_argument('--d',type=int);a.add_argument('--T',type=int);a.add_argument('--kind');a.add_argument('--target');a.add_argument('--repeat',type=int,default=0);v=a.parse_args()
    if v.freeze:freeze()
    else:service(v.d,v.T,v.kind,v.target,v.repeat)
