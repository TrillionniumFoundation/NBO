"""Fresh prospective services on a common complete-return cost boundary.

Worker repetitions reuse mathematical inputs and are not independent samples.
Every mode pays for imports, fitting, search, verification, inference and fsync.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,os,platform,random,resource,subprocess,sys,time
import numpy as np
import search60 as u
import stress60 as st
import study57 as prior
p=prior.p;n=u.n;R=u.R
TASKS=((2,2),(4,4),(8,6));SEEDS=(60103,60209)
MODES=('common-only','quadratic-native','relu-screened','relu-native')
TARGETS=prior.TARGETS;RUNGS=prior.RUNGS;LOOKS=prior.LOOKS
SCIENCE=('code/search60.cpp','code/search60.py','code/multi60.py','code/bellman60.py','code/stress60.py','code/services60.py','code/tests60.py','STUDY_PROTOCOL60.md')

def read(path):return json.loads(Path(path).read_text())
def freeze():
    f=R/'audit/SOURCE_FREEZE60.json'
    if f.exists():return verify()
    import study58
    v=dict(files_sha256={x:u.digest(R/x) for x in SCIENCE},parent_freeze_sha256=study58.verify(),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),scope='R60 production has not run. Disjoint exact correctness fixtures only.',baseline_commit='00412e6a4f43100996b324ea1ace097232c3fbbf',review_commit='8f56a3ae24ef3ce4383d0e9d1d757bd3ed7378c6')
    st.save(f,v);return u.digest(f)
def verify():
    import study58
    path=R/'audit/SOURCE_FREEZE60.json';v=read(path)
    if study58.verify()!=v['parent_freeze_sha256']:raise AssertionError('R59/R58 scientific source changed')
    for name,h in v['files_sha256'].items():
        if u.digest(R/name)!=h:raise AssertionError('Frozen R60 scientific source changed: '+name)
    return u.digest(path)
def key(mode,d,T,target,seed):return f'{mode}-d{d}-T{T}-q{target.numerator}_{target.denominator}-seed{seed}'
def directory(worker):return R/'results60'/f'worker{worker}'/'prospective'

def inference(policy,part,T,target,seed,stage,folder):
    rng=np.random.Generator(np.random.PCG64(prior.seed_for(f'NBO-R60-STOP-d{part.d}-T{T}-q{target}-seed{seed}-stage{stage}')))
    lo=[];hi=[];zl=[];zh=[];looks=[];previous=0;zero=np.zeros_like(policy);H=p.old.inference.support(T,1)[1];start=time.perf_counter();stream=hashlib.sha256()
    for look in LOOKS:
        for offset in range(previous,look,2048):
            bins,x,z=prior.paths(rng,min(2048,look-offset),part.d,T);stream.update(bins.tobytes());v=n.score(policy,part,x,z);b=n.score(zero,part,x,z)
            lo.extend(v.lo);hi.extend(v.hi);zl.extend(b.lo);zh.extend(b.hi)
        val=n.I(np.array(lo),np.array(hi));base=n.I(np.array(zl),np.array(zh));diff=val-n.s.c.rat_i(target)*base;gain=base-val
        cost=p.ci(val.lo,val.hi,F(0),H);check=p.ci(diff.lo,diff.hi,-target*H,H);g=p.ci(gain.lo,gain.hi,-H,H);met=F(check['exact'][1])<=0
        raw=p.arrays(folder/f'stage{stage}-look{look}.npz',policy_lo=val.lo,policy_hi=val.hi,zero_lo=base.lo,zero_hi=base.hi)
        rec=dict(paths=look,cost=cost,target_contrast=check,gain=g,crossed=met,raw_sha256=raw,stream_sha256=stream.hexdigest(),seconds_through_raw=time.perf_counter()-start)
        p.save(folder/f'stage{stage}-look{look}.json',rec);looks.append(rec);previous=look
        if met or F(check['exact'][0])>0:break
    return met,looks

def service(worker,d,T,mode,target,seed):
    fz=verify();env=st.environment();begin=time.perf_counter();cpu=time.process_time();target=F(target)
    if (d,T) not in TASKS or mode not in MODES or target not in TARGETS or seed not in SEEDS:raise ValueError('Outside frozen R60 catalogue')
    folder=directory(worker)/'services'/key(mode,d,T,target,seed);folder.mkdir(parents=True,exist_ok=False);stages=[]
    for stage,(samples,leaves,q) in enumerate(RUNGS):
        t=time.perf_counter();part=n.Partition(d,leaves)
        if mode=='common-only':critics=[n.Critic.zero(d) for _ in range(T)]+[n.Critic.terminal(d)];training=[]
        else:critics,training=n.train('quadratic' if mode=='quadratic-native' else 'relu',d,T,samples,seed+1000*d+10*T+stage)
        fitseconds=time.perf_counter()-t;t=time.perf_counter();native_work={}
        if mode=='common-only':grid,exact,witnesses=u.sc.a.proposals(critics,part,'common-only')
        elif mode=='relu-screened':grid,exact,witnesses=u.sc.proposals(critics,part,'screened')
        else:grid,exact,witnesses,native_work=u.proposals(critics,part)
        searchseconds=time.perf_counter()-t;verifier=u.sc.a.ReferenceVerifier(part,T,q);t=time.perf_counter()
        policy,dates,raw=verifier.sweep(grid,None if mode=='common-only' else exact);vseconds=time.perf_counter()-t
        loss=[min(p.old.inference.support(T-t,1)[1],(n.BETA*p.old.inference.support(T-t-1,1)[1] if t<T-1 else F(0))+F(dates[t]['gap_upper'])) for t in range(T)]
        rawhash=p.arrays(folder/f'stage{stage}-certificate.npz',**raw)
        models=dict(critics=[c.payload() for c in critics],training=training,partition=part.payload(),policy=policy.tolist(),grid=grid.tolist(),exact=exact.tolist(),witnesses=witnesses)
        modelhash=p.save(folder/f'stage{stage}-models.json',models);met,looks=inference(policy,part,T,target,seed,stage,folder)
        nonterminal=[w for w in witnesses if not w['common_terminal']]
        rec=dict(stage=stage,samples=samples,leaves=leaves,innovation_bins=q,construction_seconds=fitseconds,action_search_seconds=searchseconds,verification_seconds=vseconds,dates=dates,policy_sha256=p.policy_hash(policy,part),critic_parameters_sha256=p.canonical(models['critics']),models_sha256=modelhash,certificate_sha256=rawhash,verification_work=verifier.work,native_work=native_work,
            all_state_policy_loss_bound_exact=list(map(str,loss)),nonterminal_queries=len(nonterminal),nonterminal_exact_evaluations=sum(w.get('exact_evaluations',len(w.get('candidate_indices',[]))) for w in nonterminal),difference_queries=sum(w.get('difference_queries',0) for w in nonterminal),root_isolations=sum(w.get('isolated_roots',0) for w in nonterminal),maximum_recorded_operand_bits=max([0]+[w.get('max_recorded_operand_bits',0) for w in nonterminal]),look_paths=[x['paths'] for x in looks],target_attained=met,prefix_seconds_through_inference=time.perf_counter()-begin)
        p.save(folder/f'stage{stage}.json',rec);stages.append(rec)
        if met:break
    r=dict(key=folder.name,worker=worker,d=d,T=T,mode=mode,seed=seed,target=str(target),status='target_attained' if met else 'budget_exhausted',stages=stages,files_sha256={x.name:u.digest(x) for x in folder.iterdir() if x.is_file()},source_freeze_sha256=fz,final_policy_sha256=p.policy_hash(policy,part),environment=env,peak_python_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,cpu_seconds=time.process_time()-cpu,child_cpu_seconds=resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime,seconds_before_record=time.perf_counter()-begin,statistical_family=dict(alpha='1/100',maximum_intervals=2048,log_upper=14),scope='Fresh R60 streams, common primitives/targets/attempts/menus/verifier/inference. Worker replicas reuse mathematical inputs; compilation is separately charged for cold deployment.')
    h=p.save(folder/'service.json',r);p.save(folder/'clock.json',dict(service_sha256=h,seconds_through_record=time.perf_counter()-begin))
    print(json.dumps(dict(key=folder.name,status=r['status'],seconds=time.perf_counter()-begin)),flush=True)

def paired(worker,d,T,target,seed):
    start=time.perf_counter();folder=directory(worker)/'paired'/f'd{d}-T{T}-q{target.numerator}_{target.denominator}-seed{seed}';folder.mkdir(parents=True,exist_ok=False)
    actors=[];identities=[]
    for mode in MODES:
        src=directory(worker)/'services'/key(mode,d,T,target,seed);svc=read(src/'service.json');z=svc['stages'][-1];m=read(src/f'stage{z["stage"]}-models.json');part=n.Partition(d,z['leaves']);policy=np.array(m['policy'],dtype=np.uint16);actors.append((part,policy));identities.append(p.policy_hash(policy,part))
    if identities[2]!=identities[3]:raise AssertionError('Lossless native solver changed the returned neural policy')
    rng=np.random.Generator(np.random.PCG64(prior.seed_for(f'NBO-R60-FRESH-PAIRED-d{d}-T{T}-q{target}-seed{seed}')));lo=[[] for _ in MODES];hi=[[] for _ in MODES];stream=hashlib.sha256()
    for offset in range(0,65536,2048):
        bins,x,z=prior.paths(rng,2048,d,T);stream.update(bins.tobytes())
        for k,(part,policy) in enumerate(actors):v=n.score(policy,part,x,z);lo[k].extend(v.lo);hi[k].extend(v.hi)
    lo=np.array(lo);hi=np.array(hi);h=p.arrays(folder/'endpoints.npz',lower=lo,upper=hi);H=p.old.inference.support(T,1)[1];contrasts={}
    for k in range(3):
        v=n.I(lo[3],hi[3])-n.I(lo[k],hi[k]);contrasts[MODES[k]]=dict(identity=True,exact=['0','0'],interval=[0.,0.]) if identities[k]==identities[3] else p.ci(v.lo,v.hi,-H,H)
    p.save(folder/'paired.json',dict(d=d,T=T,target=str(target),seed=seed,paths=65536,mode_order=MODES,policy_sha256=identities,contrasts=contrasts,raw_sha256=h,stream_sha256=stream.hexdigest(),seconds=time.perf_counter()-start,scope='Fresh independent final-policy comparison conditional on selection; charged separately as study overhead, not attributed to an unexecuted own-service stopping schedule.'))

def cohort(worker):
    fz=verify();root=directory(worker);root.mkdir(parents=True,exist_ok=False);rows=[];rng=random.Random(60733+worker);start=time.perf_counter()
    compile_record=read(R/'audit/NATIVE_COMPILE60.json')
    for d,T in TASKS:
        for seed in SEEDS:
            for target in TARGETS:
                order=list(MODES);rng.shuffle(order)
                for mode in order:
                    name=key(mode,d,T,target,seed);log=root/'logs'/(name+'.log');log.parent.mkdir(exist_ok=True);begin=time.perf_counter()
                    with log.open('x') as output:
                        process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(worker),'--service','--d',str(d),'--T',str(T),'--mode',mode,'--target',str(target),'--seed',str(seed)],cwd=R,stdout=output,stderr=subprocess.STDOUT,check=False);output.flush();os.fsync(output.fileno())
                    child=time.perf_counter()-begin;record=dict(key=name,returncode=process.returncode,process_and_log_seconds=child,log_sha256=u.digest(log),serialized_bytes=sum(f.stat().st_size for f in (root/'services'/name).rglob('*') if f.is_file()),order=order)
                    # Include the first durable parent completion receipt in the clock.
                    receipt=root/'receipts'/(name+'.json');p.save(receipt,record);elapsed=time.perf_counter()-begin
                    record.update(complete_return_seconds=elapsed,parent_receipt_seconds=elapsed-child,receipt_sha256=u.digest(receipt),cold_compile_seconds=compile_record['seconds'] if mode in ('relu-native','quadratic-native') else 0.)
                    record['cold_return_seconds']=record['complete_return_seconds']+record['cold_compile_seconds'];rows.append(record);p.save(root/'process-clocks.json',dict(worker=worker,runs=rows,source_freeze_sha256=fz));print(json.dumps(record),flush=True)
                    if process.returncode:raise RuntimeError(log.read_text()[-4000:])
                paired(worker,d,T,target,seed)
    p.save(root/'cohort.json',dict(status='passed',worker=worker,services=len(rows),source_freeze_sha256=fz,runs=rows,seconds_before_final_ledger=time.perf_counter()-start,compile_record=compile_record,scope='All subprocess, log and first durable parent-receipt work charged. Final study-ledger bookkeeping and fresh paired comparisons are additional measured cohort overhead. Host copies reuse seeds/streams, not independent observations.'))

if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('--freeze',action='store_true');q.add_argument('--worker',type=int,default=0);q.add_argument('--service',action='store_true');q.add_argument('--d',type=int);q.add_argument('--T',type=int);q.add_argument('--mode');q.add_argument('--target');q.add_argument('--seed',type=int);a=q.parse_args()
    if a.freeze:print(freeze())
    elif a.service:service(a.worker,a.d,a.T,a.mode,a.target,a.seed)
    else:cohort(a.worker)
