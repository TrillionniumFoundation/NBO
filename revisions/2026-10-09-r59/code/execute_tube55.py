"""Separately frozen signed-tube extension; primary results remain unchanged."""
from __future__ import annotations
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import neural55 as n
import prospective55 as p
import tube55 as tube
R=p.R;OUT=R/'results55-tube'

def freeze():
    common=p.verify();paths=['code/tube55.py','code/tests_tube55.py','code/execute_tube55.py','STUDY_PROTOCOL55_TUBE.md']
    p.save(R/'audit/SOURCE_FREEZE55_TUBE.json',dict(common_source_freeze_sha256=common,files_sha256={x:p.old.digest(R/x) for x in paths},utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),scope='Extension motivated by the completed primary cache experiment; frozen before all extension production and fresh inference.'))

def verify():
    record=json.loads((R/'audit/SOURCE_FREEZE55_TUBE.json').read_text())
    if p.verify()!=record['common_source_freeze_sha256']:raise AssertionError('Common source mismatch')
    for path,h in record['files_sha256'].items():
        if p.old.digest(R/path)!=h:raise AssertionError('Extension source changed: '+path)
    return p.old.digest(R/'audit/SOURCE_FREEZE55_TUBE.json')

def inference(policy,part,T,target,folder,stage):
    seed=int.from_bytes(hashlib.sha256(f'NBO-R55-TUBE-INFERENCE-d{part.d}-T{T}-q{target}-s{stage}'.encode()).digest()[:8],'big')
    rng=np.random.Generator(np.random.PCG64(seed));lo=[];hi=[];zl=[];zh=[];looks=[];zero=np.zeros_like(policy)
    begin=time.perf_counter();stream=hashlib.sha256();previous=0;H=p.old.inference.support(T,1)[1]
    for look in p.LOOKS:
        for start in range(previous,look,2048):
            count=min(2048,look-start);bins=rng.integers(0,2**40,size=(part.d+T-1,count),dtype=np.uint64);stream.update(bins.tobytes());v=bins.astype(float)
            x=n.I(v[:part.d].T*2.**-40,(v[:part.d].T+1)*2.**-40)
            z=[n.I(-1/32+v[part.d+t]*2.**-44,-1/32+(v[part.d+t]+1)*2.**-44) for t in range(T-1)]
            value=n.score(policy,part,x,z);base=n.score(zero,part,x,z)
            lo.extend(value.lo);hi.extend(value.hi);zl.extend(base.lo);zh.extend(base.hi)
        value=n.I(np.array(lo),np.array(hi));base=n.I(np.array(zl),np.array(zh));delta=value-n.s.c.rat_i(target)*base;gain=base-value
        cost=p.ci(value.lo,value.hi,F(0),H);check=p.ci(delta.lo,delta.hi,-target*H,H);g=p.ci(gain.lo,gain.hi,-H,H)
        crossed=F(check['exact'][1])<=0
        raw=p.arrays(folder/f'stage{stage}-look{look}.npz',policy_lo=value.lo,policy_hi=value.hi,zero_lo=base.lo,zero_hi=base.hi)
        record=dict(stage=stage,paths=look,seed=seed,stream_sha256=stream.hexdigest(),cost=cost,target_contrast=check,gain=g,crossed=crossed,raw_sha256=raw,numerical_path_width=float(value.width().max()),seconds_through_raw=time.perf_counter()-begin)
        p.save(folder/f'stage{stage}-look{look}.json',record);looks.append(record);previous=look
        if crossed or F(check['exact'][0])>0:break
    return crossed,looks

def service(d,T,kind,target,repeat):
    frozen=verify();affinity=p.old.cpu_pin();start=time.perf_counter();cpu=time.process_time();target=F(target)
    key=f'{kind}-d{d}-T{T}-q{target.numerator}_{target.denominator}-r{repeat}';folder=OUT/'services'/key
    folder.mkdir(parents=True,exist_ok=False);oldpart=None;policy=None;stages=[];bound=[p.old.inference.support(T-t,1)[1] for t in range(T)]+[F(0)];allcounts=0
    for k,(samples,leaves,q) in enumerate(p.RUNGS):
        stage_start=time.perf_counter();part=n.Partition(d,leaves)
        if oldpart is None:policy=np.zeros((T,leaves),dtype=np.uint16)
        else:policy=policy[:,oldpart.locate(part.centers)]
        before=p.policy_hash(policy,part)
        critics,training=n.train(kind,d,T,samples,55001+d*100+T*10+k)
        proposed=n.propose(critics,part);construction=time.perf_counter()-stage_start
        cache_start=time.perf_counter();cache=tube.TubeCache(critics,part,policy,q);cache_seconds=time.perf_counter()-cache_start
        gate_start=time.perf_counter();updated,report,raw=cache.sweep(proposed);gate_seconds=time.perf_counter()-gate_start
        bound=[n.BETA*bound[t+1]+F(report[t]['gap']) for t in range(T)]+[F(0)]
        for t in range(T):
            for name in ('err','direct','ranges'):
                band=getattr(cache,name)[t];raw[f't{t}_{name}_lo']=band.lo;raw[f't{t}_{name}_hi']=band.hi
        rawhash=p.arrays(folder/f'stage{k}-certificate.npz',**raw)
        modelhash=p.save(folder/f'stage{k}-models.json',dict(critics=[c.payload() for c in critics],training=training,partition=part.payload(),policy=updated.tolist(),proposals=proposed.tolist()))
        allcounts+=part.membership_tests;verifyqueries=part.box_queries;ambiguities=part.ambiguous_boxes
        met,looks=inference(updated,part,T,target,folder,k)
        record=dict(stage=k,samples=samples,leaves=leaves,innovation_bins=q,construction_seconds=construction,cache_seconds=cache_seconds,gate_seconds=gate_seconds,verification_membership_comparisons=allcounts,verification_box_queries=verifyqueries,ambiguous_verification_boxes=ambiguities,
            critic_evaluated_rows=sum(c.work for c in critics),residuals=cache.residuals,dates=report,before_policy_sha256=before,after_policy_sha256=p.policy_hash(updated,part),certificate_sha256=rawhash,models_sha256=modelhash,all_state_gap_exact=list(map(str,bound)),all_state_gap_upper=[n.s.c.enclosure(x)[1] for x in bound],look_files=[f'stage{k}-look{x["paths"]}.json' for x in looks],target_attained=met,prefix_seconds=time.perf_counter()-start,
            tube_work=cache.tube_work,smooth_zero_reference=cache.zero_reference)
        p.save(folder/f'stage{k}.json',record);stages.append(record);policy=updated;oldpart=part
        if met:break
    files={str(x.relative_to(folder)):p.old.digest(x) for x in folder.iterdir() if x.is_file()}
    freq=Path(f'/sys/devices/system/cpu/cpu{affinity}/cpufreq/scaling_governor')
    rec=dict(key=key,d=d,T=T,kind=kind,target=str(target),repeat=repeat,status='target_attained' if met else 'budget_exhausted',stages=stages,files_sha256=files,
        source_freeze_sha256=frozen,common_source_freeze_sha256=p.verify(),final_policy_sha256=p.policy_hash(policy,part),own_inference=True,own_construction=True,cpu_affinity=affinity,frequency_controlled=False,governor=freq.read_text().strip() if freq.exists() else None,
        python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cpu_seconds=time.process_time()-cpu,seconds_before_record=time.perf_counter()-start,
        timing_repetition='identical seeds within this independent extension family; isolated sequential processes, not independent training draws',statistical_family=dict(alpha=str(p.ALPHA),maximum_intervals=p.FAMILY,log_upper=p.LOG),scope='first attainment with signed sensitivity tubes only for a smooth zero incumbent; generic outward cache for every discontinuous incumbent; original economic law and primary protocol targets unchanged')
    h=p.save(folder/'service.json',rec);p.save(folder/'clock.json',dict(record_sha256=h,seconds_through_record_fsync=time.perf_counter()-start))
    print(json.dumps(dict(key=key,status=rec['status'],passes=len(stages),seconds=time.perf_counter()-start,changes=[sum(x['changed'] for x in z['dates']) for z in stages])),flush=True)

def cohort(d,T):
    frozen=verify();started=time.perf_counter();logdir=OUT/f'logs-d{d}-T{T}';logdir.mkdir(parents=True,exist_ok=True);rows=[]
    methods=list(p.KINDS)+(['compiled-witness','tensor-fvi'] if d==2 else [])
    for repeat in range(p.REPEATS):
        ordered=methods[repeat%len(methods):]+methods[:repeat%len(methods)]
        for target in p.TARGETS:
            for method in ordered:
                key=f'{method}-d{d}-T{T}-q{target.numerator}_{target.denominator}-r{repeat}';begin=time.perf_counter();log=logdir/(key+'.log')
                with log.open('x') as out:
                    proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--d',str(d),'--T',str(T),'--kind',method,'--target',str(target),'--repeat',str(repeat)],cwd=R,stdout=out,stderr=subprocess.STDOUT,check=False)
                    out.flush();os.fsync(out.fileno())
                rows.append(dict(key=key,returncode=proc.returncode,whole_process_seconds=time.perf_counter()-begin,serialized_bytes=sum(x.stat().st_size for x in (OUT/'services'/key).rglob('*') if x.is_file()),log_sha256=p.old.digest(log),log=str(log.relative_to(R))))
                record=dict(d=d,T=T,source_freeze_sha256=frozen,platform=platform.platform(),runs=list(rows),cohort_seconds_through_last_process=time.perf_counter()-started,frequency_controlled=False,processes_sequential=True)
                p.save(OUT/f'process-checkpoints-d{d}-T{T}'/f'{len(rows):03d}.json',record)
                print(json.dumps(rows[-1]),flush=True)
                if proc.returncode:print(log.read_text()[-3000:],flush=True)
    p.save(OUT/f'process-clocks-d{d}-T{T}.json',record)
    if any(x['returncode'] for x in rows):raise RuntimeError('Failed services retained')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--freeze',action='store_true');a.add_argument('--cohort',action='store_true');a.add_argument('--d',type=int);a.add_argument('--T',type=int);a.add_argument('--kind');a.add_argument('--target');a.add_argument('--repeat',type=int,default=0);v=a.parse_args()
    if v.freeze:freeze()
    elif v.cohort:cohort(v.d,v.T)
    else:service(v.d,v.T,v.kind,v.target,v.repeat)
