"""Prospectively frozen action-search attribution services and fresh comparisons."""
from __future__ import annotations
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import action57 as a
import prospective55 as p
n=a.n;R=Path(__file__).resolve().parents[1];OUT=R/'results57'
TASKS=((2,2),(4,4),(8,6));SEEDS=(57101,57203,57307)
MODES=('common-only','relu-menu','relu-exact','quadratic-exact','extra-trees-menu')
TARGETS=(F(9,10),F(4,5));RUNGS=((256,32,4),(1024,64,8));LOOKS=(4096,16384,65536)

def read(f):return json.loads(Path(f).read_text())
def seed_for(text):return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8],'big')
def freeze():
    p.verify();files=['code/action57.py','code/study57.py','code/tests57.py','STUDY_PROTOCOL57.md','code/algebraic56.py','code/neural55.py','code/tube55.py','code/prospective55.py','code/operators50.py','code/study53.py']
    files+=sorted(str(x.relative_to(R)) for x in (R/'inputs').rglob('*.py'))
    return p.save(R/'audit/SOURCE_FREEZE57.json',dict(files_sha256={x:p.old.digest(R/x) for x in files},parent_source_freeze_sha256=p.verify(),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),scope='New R57 production not yet executed. Earlier R55 outcomes motivated the design and are not new observations.'))
def verify():
    j=read(R/'audit/SOURCE_FREEZE57.json')
    if p.verify()!=j['parent_source_freeze_sha256']:raise AssertionError('Parent scientific sources changed')
    for path,h in j['files_sha256'].items():
        if p.old.digest(R/path)!=h:raise AssertionError('R57 frozen file changed: '+path)
    return p.old.digest(R/'audit/SOURCE_FREEZE57.json')
def key(mode,d,T,target,seed):return f'{mode}-d{d}-T{T}-q{target.numerator}_{target.denominator}-seed{seed}'
def paths(rng,count,d,T):
    bins=rng.integers(0,2**40,size=(d+T-1,count),dtype=np.uint64);v=bins.astype(float)
    x=n.I(v[:d].T*2.**-40,(v[:d].T+1)*2.**-40)
    z=[n.I(-1/32+v[d+t]*2.**-44,-1/32+(v[d+t]+1)*2.**-44) for t in range(T-1)]
    return bins,x,z

def inference(policy,part,T,target,seed,stage,folder):
    rng=np.random.Generator(np.random.PCG64(seed_for(f'NBO-R57-STOP-d{part.d}-T{T}-q{target}-seed{seed}-stage{stage}')))
    lo=[];hi=[];zl=[];zh=[];looks=[];previous=0;zero=np.zeros_like(policy);H=p.old.inference.support(T,1)[1];start=time.perf_counter();stream=hashlib.sha256()
    for look in LOOKS:
        for offset in range(previous,look,2048):
            bins,x,z=paths(rng,min(2048,look-offset),part.d,T);stream.update(bins.tobytes())
            val=n.score(policy,part,x,z);base=n.score(zero,part,x,z)
            lo.extend(val.lo);hi.extend(val.hi);zl.extend(base.lo);zh.extend(base.hi)
        val=n.I(np.array(lo),np.array(hi));base=n.I(np.array(zl),np.array(zh));diff=val-n.s.c.rat_i(target)*base;gain=base-val
        cost=p.ci(val.lo,val.hi,F(0),H);check=p.ci(diff.lo,diff.hi,-target*H,H);g=p.ci(gain.lo,gain.hi,-H,H)
        met=F(check['exact'][1])<=0
        h=p.arrays(folder/f'stage{stage}-look{look}.npz',policy_lo=val.lo,policy_hi=val.hi,zero_lo=base.lo,zero_hi=base.hi)
        rec=dict(paths=look,cost=cost,target_contrast=check,gain=g,crossed=met,raw_sha256=h,stream_sha256=stream.hexdigest(),seconds_through_raw=time.perf_counter()-start)
        p.save(folder/f'stage{stage}-look{look}.json',rec);looks.append(rec);previous=look
        if met or F(check['exact'][0])>0:break
    return met,looks

def service(d,T,mode,target,seed):
    fz=verify();core=p.old.cpu_pin();begin=time.perf_counter();cpu=time.process_time();target=F(target)
    folder=OUT/'services'/key(mode,d,T,target,seed);folder.mkdir(parents=True,exist_ok=False);stages=[]
    for stage,(samples,leaves,q) in enumerate(RUNGS):
        buildstart=time.perf_counter();part=n.Partition(d,leaves)
        if mode=='common-only':critics=[n.Critic.zero(d) for _ in range(T)]+[n.Critic.terminal(d)];training=[]
        else:
            kind='relu' if mode.startswith('relu') else 'quadratic' if mode.startswith('quadratic') else 'extra-trees'
            critics,training=n.train(kind,d,T,samples,seed+1000*d+10*T+stage)
        fitseconds=time.perf_counter()-buildstart;searchstart=time.perf_counter();grid,exact,witnesses=a.proposals(critics,part,mode);searchseconds=time.perf_counter()-searchstart
        verifier=a.ReferenceVerifier(part,T,q);vstart=time.perf_counter();pol,dates,raw=verifier.sweep(grid,exact if mode in ('relu-exact','quadratic-exact') else None);vseconds=time.perf_counter()-vstart
        policy_loss=[min(p.old.inference.support(T-t,1)[1],(n.BETA*p.old.inference.support(T-t-1,1)[1] if t<T-1 else F(0))+F(dates[t]['gap_upper'])) for t in range(T)]
        rawhash=p.arrays(folder/f'stage{stage}-certificate.npz',**raw)
        models=dict(critics=[c.payload() for c in critics],training=training,partition=part.payload(),policy=pol.tolist(),grid=grid.tolist(),exact=exact.tolist(),witnesses=witnesses)
        modelhash=p.save(folder/f'stage{stage}-models.json',models)
        met,looks=inference(pol,part,T,target,seed,stage,folder)
        rec=dict(stage=stage,samples=samples,leaves=leaves,innovation_bins=q,construction_seconds=fitseconds,action_search_seconds=searchseconds,verification_seconds=vseconds,dates=dates,reference_policy='installed zero at every construction attempt',policy_sha256=p.policy_hash(pol,part),critic_parameters_sha256=p.canonical(models['critics']),models_sha256=modelhash,certificate_sha256=rawhash,work=verifier.work,
                 all_state_policy_loss_bound_exact=list(map(str,policy_loss)),root_isolations=sum(r['isolated_roots'] for r in witnesses),exact_candidate_evaluations=sum(len(r['candidate_indices']) for r in witnesses),nonterminal_grid_regret_positive=sum(F(r['grid_regret_exact'])>0 for r in witnesses if not r['common_terminal']),look_paths=[z['paths'] for z in looks],target_attained=met,prefix_seconds_through_inference=time.perf_counter()-begin)
        p.save(folder/f'stage{stage}.json',rec);stages.append(rec)
        if met:break
    freq=Path(f'/sys/devices/system/cpu/cpu{core}/cpufreq/scaling_governor')
    rec=dict(key=folder.name,d=d,T=T,mode=mode,seed=seed,target=str(target),status='target_attained' if met else 'budget_exhausted',stages=stages,files_sha256={x.name:p.old.digest(x) for x in folder.iterdir() if x.is_file()},source_freeze_sha256=fz,final_policy_sha256=p.policy_hash(pol,part),cpu_affinity=core,governor=freq.read_text().strip() if freq.exists() else None,frequency_controlled=False,python=platform.python_version(),numpy=np.__version__,sympy=a.sp.__version__,platform=platform.platform(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,cpu_seconds=time.process_time()-cpu,seconds_before_record=time.perf_counter()-begin,statistical_family=dict(alpha='1/100',maximum_intervals=2048,log_upper=14),scope='Each target starts from primitives; only final selected target policy is returned. Refinement attempts stay relative to the installed zero, not a falsely differentiable acquired incumbent. Distinct seeds are training realizations, not pure timing repetitions.')
    h=p.save(folder/'service.json',rec);p.save(folder/'clock.json',dict(record_sha256=h,seconds_through_record_fsync=time.perf_counter()-begin))
    print(json.dumps(dict(key=folder.name,status=rec['status'],stages=len(stages),seconds=time.perf_counter()-begin,extra_changes=sum(z['extra_witness_changes'] for s in stages for z in s['dates']))),flush=True)

def paired(d,T,target,seed):
    start=time.perf_counter();fz=verify();folder=OUT/'paired'/f'd{d}-T{T}-q{target.numerator}_{target.denominator}-seed{seed}';folder.mkdir(parents=True,exist_ok=False)
    actors=[];identities=[]
    for mode in MODES:
        src=OUT/'services'/key(mode,d,T,target,seed);svc=read(src/'service.json');st=svc['stages'][-1];m=read(src/f'stage{st["stage"]}-models.json');part=n.Partition(d,st['leaves']);pol=np.array(m['policy'],dtype=np.uint16);actors.append((part,pol));identities.append(p.policy_hash(pol,part))
    rng=np.random.Generator(np.random.PCG64(seed_for(f'NBO-R57-INDEPENDENT-PAIRS-d{d}-T{T}-q{target}-seed{seed}')));los=[[] for _ in MODES];his=[[] for _ in MODES];stream=hashlib.sha256()
    for offset in range(0,65536,2048):
        bins,x,z=paths(rng,2048,d,T);stream.update(bins.tobytes())
        for i,(part,pol) in enumerate(actors):
            val=n.score(pol,part,x,z);los[i].extend(val.lo);his[i].extend(val.hi)
    lo=np.array(los);hi=np.array(his);h=p.arrays(folder/'endpoints.npz',lower=lo,upper=hi);H=p.old.inference.support(T,1)[1];contrasts={}
    for i in (0,1,3,4):
        diff=n.I(lo[2],hi[2])-n.I(lo[i],hi[i])
        contrasts[MODES[i]]=dict(identity=True,exact=['0','0'],interval=[0.,0.]) if identities[2]==identities[i] else p.ci(diff.lo,diff.hi,-H,H)
    p.save(folder/'paired.json',dict(d=d,T=T,target=str(target),seed=seed,paths=65536,mode_order=MODES,policy_sha256=identities,contrasts=contrasts,raw_sha256=h,stream_sha256=stream.hexdigest(),source_freeze_sha256=fz,seconds_through_endpoints=time.perf_counter()-start,scope='Fresh paired validation conditional on returned policies; additional study overhead, not hidden in own target-service clocks. Negative contrast favors relu-exact.'))

def cohort(d,T):
    freezehash=verify();rows=[];logs=OUT/f'logs-d{d}-T{T}';logs.mkdir(parents=True,exist_ok=True)
    for sidx,seed in enumerate(SEEDS):
        order=MODES[sidx:]+MODES[:sidx]
        for target in TARGETS:
            for mode in order:
                name=key(mode,d,T,target,seed);log=logs/(name+'.log');begin=time.perf_counter()
                with log.open('x') as out:
                    proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--service','--d',str(d),'--T',str(T),'--mode',mode,'--target',str(target),'--seed',str(seed)],cwd=R,stdout=out,stderr=subprocess.STDOUT,check=False);out.flush();os.fsync(out.fileno())
                row=dict(key=name,returncode=proc.returncode,whole_process_seconds=time.perf_counter()-begin,serialized_bytes=sum(x.stat().st_size for x in (OUT/'services'/name).rglob('*') if x.is_file()),log_sha256=p.old.digest(log));rows.append(row)
                p.save(OUT/f'checkpoints-d{d}-T{T}'/f'{len(rows):03d}.json',dict(runs=list(rows),source_freeze_sha256=freezehash));print(json.dumps(row),flush=True)
                if proc.returncode:raise RuntimeError('Failed execution retained: '+log.read_text()[-3000:])
            paired(d,T,target,seed)
    p.save(OUT/f'process-clocks-d{d}-T{T}.json',dict(runs=rows,d=d,T=T,processes_sequential=True,source_freeze_sha256=freezehash))

if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('--freeze',action='store_true');q.add_argument('--service',action='store_true');q.add_argument('--d',type=int);q.add_argument('--T',type=int);q.add_argument('--mode');q.add_argument('--target');q.add_argument('--seed',type=int);args=q.parse_args()
    if args.freeze:freeze()
    elif args.service:service(args.d,args.T,args.mode,args.target,args.seed)
    else:cohort(args.d,args.T)
