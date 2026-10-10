"""Frozen matched-work experiment: algebraic versus screened neural action search.
Only nonterminal ReLU search differs. Repetitions reuse seeds and streams.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import screen58 as sc
import study57 as old
p=old.p;n=sc.n;R=Path(__file__).resolve().parents[1];OUT=R/'results58'
TASKS=((2,2),(4,4),(8,6));MODES=('algebraic','screened');REPETITIONS=(0,1,2)
TARGETS=old.TARGETS;RUNGS=old.RUNGS;LOOKS=old.LOOKS;SEED=57101

def read(f):return json.loads(Path(f).read_text())
def freeze():
    f=R/'audit/SOURCE_FREEZE58.json'
    if f.exists():return verify()
    prior=old.verify();files=['code/screen58.py','code/study58.py','code/tests58.py','STUDY_PROTOCOL58.md']
    p.save(f,dict(files_sha256={x:p.old.digest(R/x) for x in files},parent_freeze_sha256=prior,utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),scope='Before R58 production; only disjoint correctness fixtures have run'))
    return p.old.digest(f)
def verify():
    f=R/'audit/SOURCE_FREEZE58.json';j=read(f)
    if old.verify()!=j['parent_freeze_sha256']:raise AssertionError('Inherited scientific source changed')
    for name,h in j['files_sha256'].items():
        if p.old.digest(R/name)!=h:raise AssertionError('R58 scientific source changed: '+name)
    return p.old.digest(f)
def key(mode,d,T,target,rep):return f'{mode}-d{d}-T{T}-q{target.numerator}_{target.denominator}-rep{rep}'
def rng_for(d,T,target,stage):
    return np.random.Generator(np.random.PCG64(old.seed_for(f'NBO-R58-STOP-d{d}-T{T}-q{target}-seed{SEED}-stage{stage}')))
def inference(policy,part,T,target,stage,folder):
    rng=rng_for(part.d,T,target,stage);lo=[];hi=[];zl=[];zh=[];looks=[];previous=0
    zero=np.zeros_like(policy);H=p.old.inference.support(T,1)[1];start=time.perf_counter();stream=hashlib.sha256()
    for look in LOOKS:
        for offset in range(previous,look,2048):
            bins,x,z=old.paths(rng,min(2048,look-offset),part.d,T);stream.update(bins.tobytes())
            val=n.score(policy,part,x,z);base=n.score(zero,part,x,z)
            lo.extend(val.lo);hi.extend(val.hi);zl.extend(base.lo);zh.extend(base.hi)
        val=n.I(np.array(lo),np.array(hi));base=n.I(np.array(zl),np.array(zh));diff=val-n.s.c.rat_i(target)*base;gain=base-val
        cost=p.ci(val.lo,val.hi,F(0),H);check=p.ci(diff.lo,diff.hi,-target*H,H);g=p.ci(gain.lo,gain.hi,-H,H);met=F(check['exact'][1])<=0
        h=p.arrays(folder/f'stage{stage}-look{look}.npz',policy_lo=val.lo,policy_hi=val.hi,zero_lo=base.lo,zero_hi=base.hi)
        rec=dict(paths=look,cost=cost,target_contrast=check,gain=g,crossed=met,raw_sha256=h,stream_sha256=stream.hexdigest(),seconds_through_raw=time.perf_counter()-start)
        p.save(folder/f'stage{stage}-look{look}.json',rec);looks.append(rec);previous=look
        if met or F(check['exact'][0])>0:break
    return met,looks

def service(d,T,mode,target,rep):
    fz=verify();core=p.old.cpu_pin();begin=time.perf_counter();cpu=time.process_time();target=F(target)
    if (d,T) not in TASKS or mode not in MODES or target not in TARGETS or rep not in REPETITIONS:raise ValueError('Outside frozen catalogue')
    folder=OUT/'services'/key(mode,d,T,target,rep);folder.mkdir(parents=True,exist_ok=False);stages=[]
    for stage,(samples,leaves,q) in enumerate(RUNGS):
        t=time.perf_counter();part=n.Partition(d,leaves);critics,training=n.train('relu',d,T,samples,SEED+1000*d+10*T+stage);fitseconds=time.perf_counter()-t
        t=time.perf_counter();grid,exact,witnesses=sc.proposals(critics,part,mode);searchseconds=time.perf_counter()-t
        verifier=sc.a.ReferenceVerifier(part,T,q);t=time.perf_counter();pol,dates,raw=verifier.sweep(grid,exact);vseconds=time.perf_counter()-t
        loss=[min(p.old.inference.support(T-t,1)[1],(n.BETA*p.old.inference.support(T-t-1,1)[1] if t<T-1 else F(0))+F(dates[t]['gap_upper'])) for t in range(T)]
        rawhash=p.arrays(folder/f'stage{stage}-certificate.npz',**raw)
        models=dict(critics=[c.payload() for c in critics],training=training,partition=part.payload(),policy=pol.tolist(),grid=grid.tolist(),exact=exact.tolist(),witnesses=witnesses)
        modelhash=p.save(folder/f'stage{stage}-models.json',models);met,looks=inference(pol,part,T,target,stage,folder)
        neural=[w for w in witnesses if not w['common_terminal']]
        rec=dict(stage=stage,samples=samples,leaves=leaves,innovation_bins=q,construction_seconds=fitseconds,action_search_seconds=searchseconds,verification_seconds=vseconds,dates=dates,
            policy_sha256=p.policy_hash(pol,part),critic_parameters_sha256=p.canonical(models['critics']),models_sha256=modelhash,certificate_sha256=rawhash,work=verifier.work,
            all_state_policy_loss_bound_exact=list(map(str,loss)),neural_searches=len(neural),neural_root_isolations=sum(w['isolated_roots'] for w in neural),neural_exact_evaluations=sum(len(w['candidate_indices']) for w in neural),
            neural_screened_points=sum(w.get('screened_points',0) for w in neural),neural_retained_points=sum(w.get('retained_points',0) for w in neural),neural_active_ridges=sum(w.get('active_ridges',0) for w in neural),neural_eliminated_ridges=sum(w.get('eliminated_ridges',0) for w in neural),fallbacks=sum(w.get('solver')=='algebraic-fallback' for w in neural),
            look_paths=[x['paths'] for x in looks],target_attained=met,prefix_seconds_through_inference=time.perf_counter()-begin)
        p.save(folder/f'stage{stage}.json',rec);stages.append(rec)
        if met:break
    freq=Path(f'/sys/devices/system/cpu/cpu{core}/cpufreq/scaling_governor')
    rec=dict(key=folder.name,d=d,T=T,mode=mode,repetition=rep,seed=SEED,target=str(target),status='target_attained' if met else 'budget_exhausted',stages=stages,
        files_sha256={x.name:p.old.digest(x) for x in folder.iterdir() if x.is_file()},source_freeze_sha256=fz,final_policy_sha256=p.policy_hash(pol,part),cpu_affinity=core,governor=freq.read_text().strip() if freq.exists() else None,frequency_controlled=False,
        python=platform.python_version(),numpy=np.__version__,sympy=sc.a.sp.__version__,platform=platform.platform(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cpu_seconds=time.process_time()-cpu,seconds_before_record=time.perf_counter()-begin,
        statistical_family=dict(alpha='1/100',maximum_intervals=2048,log_upper=14),scope='Fixed-seed timing replication, not independent learned objects or independent path samples. Only nonterminal neural action search differs. All terminal solves, menus, verifier, fits and inference rules match.')
    h=p.save(folder/'service.json',rec);p.save(folder/'clock.json',dict(record_sha256=h,seconds_through_record_fsync=time.perf_counter()-begin))
    print(json.dumps(dict(key=folder.name,status=rec['status'],stages=len(stages),seconds=time.perf_counter()-begin)),flush=True)

def cohort(d,T):
    fz=verify();core=p.old.cpu_pin();rows=[];logs=OUT/f'logs-d{d}-T{T}';logs.mkdir(parents=True,exist_ok=True)
    for rep in REPETITIONS:
        for qi,target in enumerate(TARGETS):
            order=MODES if (rep+qi)%2==0 else MODES[::-1]
            for mode in order:
                name=key(mode,d,T,target,rep);log=logs/(name+'.log');begin=time.perf_counter()
                with log.open('x') as out:
                    proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--service','--d',str(d),'--T',str(T),'--mode',mode,'--target',str(target),'--rep',str(rep)],cwd=R,stdout=out,stderr=subprocess.STDOUT,check=False);out.flush();os.fsync(out.fileno())
                row=dict(key=name,returncode=proc.returncode,whole_process_seconds=time.perf_counter()-begin,serialized_bytes=sum(x.stat().st_size for x in (OUT/'services'/name).rglob('*') if x.is_file()),log_sha256=p.old.digest(log));rows.append(row)
                p.save(OUT/f'checkpoints-d{d}-T{T}'/f'{len(rows):03d}.json',dict(runs=list(rows),source_freeze_sha256=fz));print(json.dumps(row),flush=True)
                if proc.returncode:raise RuntimeError('Failed process retained: '+log.read_text()[-3000:])
    p.save(OUT/f'process-clocks-d{d}-T{T}.json',dict(runs=rows,d=d,T=T,processes_sequential=True,cpu_affinity=core,source_freeze_sha256=fz))

if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('--freeze',action='store_true');q.add_argument('--service',action='store_true');q.add_argument('--d',type=int);q.add_argument('--T',type=int);q.add_argument('--mode');q.add_argument('--target');q.add_argument('--rep',type=int);args=q.parse_args()
    if args.freeze:print(freeze())
    elif args.service:service(args.d,args.T,args.mode,args.target,args.rep)
    else:cohort(args.d,args.T)
