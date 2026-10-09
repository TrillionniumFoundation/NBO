"""Offline numerical reconstruction of the complete R60 evidence.

No training or new statistical observations are produced. Saved model parameters,
unique action computations, whole-cell certificates and declared path streams
are reconstructed. Identical host copies are checked, not double-counted.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,math,statistics,time
import numpy as np
import search60 as u
import stress60 as st
import multi60 as multi
import bellman60 as bell
import services60 as s
import services60b as amended
import audit56 as old
p=s.p;n=s.n;R=s.R
MODELS={};PATHS={};SOLVERS={};PAIRED={}
COUNTS=dict(unique_stress_solver_replays=0,stress_recorded_answers=0,unique_two_control_replays=0,unique_model_replays=0,unique_path_rows=0,unique_path_streams=0,checked_cell_decisions=0,checked_stopping_looks=0,checked_ci_records=0,checked_services=0,checked_paired_sets=0)

def read(f):return json.loads(Path(f).read_text())
def need(v,msg):
    if not v:raise AssertionError(msg)
def eq(a,b,msg):need(np.array_equal(np.asarray(a),np.asarray(b)),msg)
def save(f,j):f=Path(f);f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')

def deterministic_result(actual,record,label):
    for field in ('index','objective_exact','candidate_count','exact_evaluations','isolated_roots','difference_queries','pieces','screened_points','retained_points','screen_survivors','active_ridges','eliminated_ridges','fallback','fallback_reason','largest_single_pair_array_bytes','endpoint_sha256','max_recorded_operand_bits','pair_nodes','pruned_nodes','peak_stack','bound_fraction_bits'):
        if field in record:need(actual.get(field)==record[field],label+' '+field)

def replay_solver(o,cap,Q,rec):
    key=(st.canonical(o.payload()),cap,Q,rec['method'],rec.get('bound_fraction_bits',53))
    if key not in SOLVERS:
        SOLVERS[key]=u.solve(o,cap,Q,rec['method'],bits=rec.get('bound_fraction_bits',53));COUNTS['unique_stress_solver_replays']+=1
    deterministic_result(SOLVERS[key],rec,'stress solver');COUNTS['stress_recorded_answers']+=1

def stress(worker):
    folder=R/'results60'/f'worker{worker}'/'stress';summary=read(folder/'summary.json')
    need(summary['status']=='passed' and summary['cases']==90,'complete stress catalogue')
    primary=[];refs={}
    for entry in summary['factorial']:
        rec=read(folder/'cases'/(entry['key']+'.json'));o,cap,Q=st.fixture(rec['seed'],rec['width'],rec['size'],rec['regime'])
        need(o.payload()==rec['objective'] and st.canonical(o.payload())==rec['objective_sha256'],'prespecified stress object')
        need(set(rec['order'])==set(u.METHODS) and [x['method'] for x in rec['runs']]==rec['order'],'all factorial cells and random order')
        identity=(rec['seed'],rec['width'],rec['size'],rec['regime'])
        values=[o.value(F(k,Q)) for k in range(cap+1)];best=min(range(cap+1),key=lambda k:(values[k],k))
        ref=dict(index=best,objective_exact=str(values[best]),all_minimizers=[k for k,v in enumerate(values) if v==values[best]])
        for field,value in ref.items():need(rec['reference'][field]==value,'independent Python exhaustive reference')
        for run in rec['runs']+rec['coarse_endpoint_diagnostics']:replay_solver(o,cap,Q,run);st.same(run,ref)
        primary.append(rec);refs[identity]=(o,cap,Q,ref)
    expected={(a,b,c,d) for a in st.SEEDS for b in st.WIDTHS for c in st.SIZES for d in st.REGIMES}
    need(set(refs)==expected,'missing adverse regime')
    for record in summary['repetitions']:
        o,cap,Q=st.fixture(st.SEEDS[0],32,129,record['regime']);need(record['objective_sha256']==st.canonical(o.payload()),'fixed repeated fixture')
        for run in record['runs']:replay_solver(o,cap,Q,run)
    need(len(summary['repetitions'])==35,'seven repetitions of five regimes')
    for rec in summary['fallback_frontier']:
        o,cap,Q=st.fixture(st.SEEDS[0],8,rec['size'],rec['regime']);need(rec['objective']==o.payload(),'guard fixture identity')
        ref=st.reference(o,cap,Q)
        need(rec['reference']['index']==ref['index'] and rec['reference']['all_minimizers']==ref['all_minimizers'],'guard exact reference')
        for run in rec['runs']:replay_solver(o,cap,Q,run);st.same(run,ref)
    need(len(summary['fallback_frontier'])==8,'complete guard frontier')
    return summary,primary

def two_control(worker,cache):
    root=R/'results60'/f'worker{worker}'/'two-control';summary=read(root/'summary.json');need(summary['cases']==16,'complete constrained catalogue')
    for rec in summary['rows']:
        training=read(root/f"training-{rec['seed']}.json");critic=old.load_critic(training['critics'][1]);state=list(map(F,rec['state']))
        o=multi.from_critic(state,critic,rec['shocks']==2);need(o.payload()==rec['objective'],'two-control objective from actual trained critic')
        key=(st.canonical(rec['objective']),rec['cap'],rec['Q'])
        if key not in cache:
            cache[key]=(multi.exhaustive(o,rec['cap'],rec['Q']),multi.adaptive(o,rec['cap'],rec['Q']));COUNTS['unique_two_control_replays']+=1
        ref,got=cache[key]
        for field in ('index','objective_exact','evaluations','ties','max_recorded_operand_bits'):need(ref[field]==rec['reference'][field],'two-control exact exhaustive '+field)
        for field in ('index','objective_exact','evaluations','fallback','nodes','pruned','peak_stack'):need(got[field]==rec['adaptive'][field],'two-control adaptive '+field)
        need(sum(got['index'])<=rec['cap'],'shared-capacity feasibility')
    return summary

def bellman(worker,cache):
    folder=R/'results60'/f'worker{worker}'/'bellman';summary=read(folder/'summary.json')
    need([(r['N'],r['A'],r['q']) for r in summary['rungs']]==list(bell.RUNGS),'fixed Bellman ladder')
    for rec in summary['rungs']:
        key=(rec['N'],rec['A'],rec['q'])
        if key not in cache:cache[key]=bell.rung(*key)
        computed,arrays=cache[key];file=folder/f"N{rec['N']}.npz";need(u.digest(file)==rec['raw_sha256'],'Bellman raw archive')
        with np.load(file) as z:
            for name,v in arrays.items():eq(z[name],v,'full Bellman recomputation '+name)
        for field in ('dates','initial_gap_upper','maximum_date_gap_upper','table_bytes'):need(rec[field]==computed[field],'Bellman bracket '+field)
        need(np.all(arrays['lower']<=arrays['upper']) and np.all(arrays['policy']<=arrays['capindex']),'original-law valid brackets')
    for target in summary['targets']:
        hit=next((r for r in summary['rungs'] if F(r['maximum_date_gap_upper'])<=F(target['tolerance'])),None)
        need(target['status']==('attained' if hit else 'budget_exhausted'),'true Bellman tolerance classification')
        need(target['N']==(hit['N'] if hit else None),'first Bellman attainment')
    return summary

def model_replay(model,d,T,N,q,mode):
    key=(d,T,N,q,mode,p.canonical(model['critics']))
    if key not in MODELS:
        part=n.Partition(d,N);need(part.payload()==model['partition'],'original acquired partition')
        critics=[old.load_critic(c) for c in model['critics']]
        if mode=='common-only':grid,exact,witnesses=u.sc.a.proposals(critics,part,'common-only')
        elif mode=='relu-screened':grid,exact,witnesses=u.sc.proposals(critics,part,'screened')
        else:grid,exact,witnesses,work=u.proposals(critics,part)
        verifier=u.sc.a.ReferenceVerifier(part,T,q);policy,dates,raw=verifier.sweep(grid,None if mode=='common-only' else exact)
        MODELS[key]=dict(part=part,grid=grid,exact=exact,witnesses=witnesses,policy=policy,dates=dates,raw=raw,work=verifier.work)
        COUNTS['unique_model_replays']+=1
    return MODELS[key]

def paths(policy,part,T,target,seed,stage,looks):
    key=(part.d,T,str(target),seed,stage,p.policy_hash(policy,part),tuple(looks))
    if key in PATHS:return PATHS[key]
    rng=np.random.Generator(np.random.PCG64(s.prior.seed_for(f'NBO-R60-STOP-d{part.d}-T{T}-q{target}-seed{seed}-stage{stage}')))
    stream=hashlib.sha256();values={k:[] for k in ('policy_lo','policy_hi','zero_lo','zero_hi')};previous=0;out={};zero=np.zeros_like(policy)
    for look in looks:
        for offset in range(previous,look,2048):
            bins,x,z=s.prior.paths(rng,min(2048,look-offset),part.d,T);stream.update(bins.tobytes());v=n.score(policy,part,x,z);base=n.score(zero,part,x,z)
            for name,array in zip(values,(v.lo,v.hi,base.lo,base.hi)):values[name].extend(array)
        out[look]={**{name:np.array(x) for name,x in values.items()},'stream_sha256':stream.hexdigest()};previous=look
    PATHS[key]=out;COUNTS['unique_path_rows']+=previous;COUNTS['unique_path_streams']+=1;return out

def service(folder,clock,worker,freeze):
    rec=read(folder/'service.json');need(rec['worker']==worker and rec['source_freeze_sha256']==freeze,'service freeze/host identity')
    d,T,mode,seed,target=rec['d'],rec['T'],rec['mode'],rec['seed'],F(rec['target']);need(folder.name==s.key(mode,d,T,target,seed),'prespecified service key')
    need(clock['returncode']==0,'failed service cannot be published as completed')
    need(u.digest(folder/'service.json')==read(folder/'clock.json')['service_sha256'],'durable record identity')
    need(clock['complete_return_seconds']>=clock['process_and_log_seconds']>=read(folder/'clock.json')['seconds_through_record']>0,'complete return work boundary')
    need(clock['serialized_bytes']==sum(f.stat().st_size for f in folder.rglob('*') if f.is_file()),'complete serialized bytes')
    for name,h in rec['files_sha256'].items():need(u.digest(folder/name)==h,'service file hash '+name)
    need(set(rec['files_sha256'])=={f.name for f in folder.iterdir() if f.is_file()}-{'service.json','clock.json'},'complete registered record set')
    need(rec['statistical_family']==dict(alpha='1/100',maximum_intervals=2048,log_upper=14),'simultaneous finite family')
    transcript=[];met=False
    for stage,record in enumerate(rec['stages']):
        need(stage<len(s.RUNGS) and read(folder/f'stage{stage}.json')==record,'construction prefix')
        samples,N,q=s.RUNGS[stage];need((record['samples'],record['leaves'],record['innovation_bins'])==(samples,N,q),'unchanged ladder')
        model=read(folder/f'stage{stage}-models.json');need(u.digest(folder/f'stage{stage}-models.json')==record['models_sha256'],'saved model identity')
        need(p.canonical(model['critics'])==record['critic_parameters_sha256'],'critic parameter digest')
        got=model_replay(model,d,T,N,q,mode);part=got['part'];policy=got['policy']
        for name in ('grid','exact','policy'):eq(model[name],got[name],'recovered model '+name)
        need(len(model['witnesses'])==len(got['witnesses']),'complete action witness list')
        for actual,stored in zip(got['witnesses'],model['witnesses']):
            for field in stored:
                if field not in ('native_process_seconds','seconds'):need(actual.get(field)==stored[field],'exact witness record '+field)
        need(record['dates']==got['dates'] and record['verification_work']==got['work'],'full datewise accounting')
        with np.load(folder/f'stage{stage}-certificate.npz') as z:
            need(set(z.files)==set(got['raw']),'complete certificate arrays')
            for name,values in got['raw'].items():eq(z[name],values,'whole-cell reintegration '+name)
        need(record['policy_sha256']==p.policy_hash(policy,part),'full acquired policy identity')
        looks=record['look_paths'];need(looks==list(s.LOOKS[:len(looks)]) and len(looks)>0,'declared inference prefix')
        generated=paths(policy,part,T,target,seed,stage,looks);H=p.old.inference.support(T,1)[1]
        for j,look in enumerate(looks):
            info=read(folder/f'stage{stage}-look{look}.json');arrays=generated[look]
            need(u.digest(folder/f'stage{stage}-look{look}.npz')==info['raw_sha256'],'saved path hash')
            with np.load(folder/f'stage{stage}-look{look}.npz') as z:
                for name in ('policy_lo','policy_hi','zero_lo','zero_hi'):eq(z[name],arrays[name],'full original-law path reconstruction '+name)
            value=n.I(arrays['policy_lo'],arrays['policy_hi']);base=n.I(arrays['zero_lo'],arrays['zero_hi']);diff=value-n.s.c.rat_i(target)*base;gain=base-value
            old.verify_ci(value.lo,value.hi,F(0),H,info['cost']);old.verify_ci(diff.lo,diff.hi,-target*H,H,info['target_contrast']);old.verify_ci(gain.lo,gain.hi,-H,H,info['gain'])
            met=F(info['target_contrast']['exact'][1])<=0;positive=F(info['target_contrast']['exact'][0])>0
            need(info['crossed']==met and info['stream_sha256']==arrays['stream_sha256'],'prospective stopping and stream')
            if j<len(looks)-1:need(not met and not positive,'continuation beyond stopping look')
            else:need(met or positive or look==s.LOOKS[-1],'unexplained early stopping')
            COUNTS['checked_ci_records']+=3;COUNTS['checked_stopping_looks']+=1
        need(record['target_attained']==met,'stage attainment')
        if met:need(stage==len(rec['stages'])-1,'construction after target attainment')
        loss=[min(p.old.inference.support(T-t,1)[1],(n.BETA*p.old.inference.support(T-t-1,1)[1] if t<T-1 else F(0))+F(record['dates'][t]['gap_upper'])) for t in range(T)]
        need(list(map(str,loss))==record['all_state_policy_loss_bound_exact'],'inherited loose Bellman bound preserved')
        transcript.append(dict(stage=stage,parameters=record['critic_parameters_sha256'],policy=record['policy_sha256'],looks=looks,cost=info['cost']['exact'],gain=info['gain']['exact'],target=info['target_contrast']['exact'],dates=record['dates']))
        COUNTS['checked_cell_decisions']+=T*N
    need(rec['status']==('target_attained' if met else 'budget_exhausted'),'final service status')
    if not met:need(len(rec['stages'])==len(s.RUNGS),'unexecuted remaining budget')
    need(rec['final_policy_sha256']==transcript[-1]['policy'],'returned policy')
    COUNTS['checked_services']+=1
    return dict(key=folder.name,worker=worker,d=d,T=T,mode=mode,seed=seed,target=str(target),status=rec['status'],transcript=transcript,policy_sha256=rec['final_policy_sha256'],cost=list(map(float,map(F,transcript[-1]['cost']))),gain=list(map(float,map(F,transcript[-1]['gain']))),complete_return_seconds=clock['complete_return_seconds'],cold_return_seconds=clock['cold_return_seconds'],cold_compile_seconds=clock['cold_compile_seconds'],search_seconds=sum(x['action_search_seconds'] for x in rec['stages']),fit_seconds=sum(x['construction_seconds'] for x in rec['stages']),verification_seconds=sum(x['verification_seconds'] for x in rec['stages']),extra_witness_changes=sum(z['extra_witness_changes'] for x in rec['stages'] for z in x['dates']),maximum_all_state_bound=max(float(F(v)) for x in rec['stages'] for v in x['all_state_policy_loss_bound_exact']),max_recorded_operand_bits=max(x['maximum_recorded_operand_bits'] for x in rec['stages']),peak_python_rss_kib=rec['peak_python_rss_kib'],peak_child_rss_kib=rec['peak_child_rss_kib'])

def paired(worker,d,T,target,seed,services):
    root=s.directory(worker);folder=root/'paired'/f'd{d}-T{T}-q{target.numerator}_{target.denominator}-seed{seed}';record=read(folder/'paired.json');actors=[]
    for mode in s.MODES:
        src=root/'services'/s.key(mode,d,T,target,seed);rec=read(src/'service.json');last=rec['stages'][-1];model=read(src/f"stage{last['stage']}-models.json");actors.append((n.Partition(d,last['leaves']),np.array(model['policy'],dtype=np.uint16)))
    identities=[p.policy_hash(pol,part) for part,pol in actors];need(identities==record['policy_sha256'],'fresh-pair returned policy identities')
    key=(d,T,str(target),seed,tuple(identities))
    if key not in PAIRED:
        rng=np.random.Generator(np.random.PCG64(s.prior.seed_for(f'NBO-R60-FRESH-PAIRED-d{d}-T{T}-q{target}-seed{seed}')));lo=[[] for _ in actors];hi=[[] for _ in actors];stream=hashlib.sha256()
        for offset in range(0,65536,2048):
            bins,x,z=s.prior.paths(rng,2048,d,T);stream.update(bins.tobytes())
            for k,(part,pol) in enumerate(actors):v=n.score(pol,part,x,z);lo[k].extend(v.lo);hi[k].extend(v.hi)
        PAIRED[key]=(np.array(lo),np.array(hi),stream.hexdigest());COUNTS['unique_path_rows']+=65536;COUNTS['unique_path_streams']+=1
    lo,hi,stream=PAIRED[key];need(record['stream_sha256']==stream and record['paths']==65536,'fresh-pair declared stream')
    need(u.digest(folder/'endpoints.npz')==record['raw_sha256'],'fresh paired endpoint hash')
    with np.load(folder/'endpoints.npz') as z:eq(z['lower'],lo,'fresh paired lower reintegration');eq(z['upper'],hi,'fresh paired upper reintegration')
    H=p.old.inference.support(T,1)[1];classifications={}
    for k in range(3):
        info=record['contrasts'][s.MODES[k]]
        if identities[k]==identities[3]:need(info['exact']==['0','0'] and info['identity'],'exact identical policy');label='identity'
        else:
            v=n.I(lo[3],hi[3])-n.I(lo[k],hi[k]);old.verify_ci(v.lo,v.hi,-H,H,info);COUNTS['checked_ci_records']+=1
            a,b=map(F,info['exact']);label='neural_lower' if b<0 else 'neural_higher' if a>0 else 'unresolved'
        classifications[s.MODES[k]]=label
    COUNTS['checked_paired_sets']+=1
    return dict(worker=worker,d=d,T=T,target=str(target),seed=seed,classifications=classifications,contrasts=record['contrasts'],seconds=record['seconds'])

def main():
    begin=time.perf_counter();freeze=s.verify();amend=amended.verify();execution=read(R/'audit/SCIENCE_EXECUTION60.json')
    for name,h in execution['files_sha256'].items():need(u.digest(R/name)==h,'complete execution hash '+name)
    first=read(R/'audit/FIRST_ATTEMPT60.json')
    for name,h in first['files_sha256'].items():need(u.digest(R/name)==h,'failed predecessor evidence retained')
    stresses=[];multirows=[];bells=[];services=[];pairs=[];mc={};bc={};cohorts=[]
    for worker in (0,1):
        z,_=stress(worker);stresses.append(z);multirows.append(two_control(worker,mc));bells.append(bellman(worker,bc))
        root=s.directory(worker);cohort=read(root/'cohort.json');cohorts.append(cohort);need(cohort['services']==48 and cohort['status']=='passed' and cohort['source_freeze_sha256']==amend,'complete amended cohort')
        clocks=read(root/'process-clocks.json');need(clocks['runs']==cohort['runs'],'final immutable clock ledger')
        expected={s.key(mode,d,T,q,seed) for d,T in s.TASKS for q in s.TARGETS for seed in s.SEEDS for mode in s.MODES}
        need({x['key'] for x in cohort['runs']}==expected,'full fixed service catalogue')
        need({x.name for x in (root/'services').iterdir() if x.is_dir()}==expected,'no missing or extra services')
        for k,clock in enumerate(cohort['runs'],1):
            need(read(root/'checkpoints'/f'{k:03d}.json')['runs']==cohort['runs'][:k],'immutable timing prefix')
            need(u.digest(root/'logs'/(clock['key']+'.log'))==clock['log_sha256'],'flushed child log')
            need(u.digest(root/'receipts'/(clock['key']+'.json'))==clock['receipt_sha256'],'first durable parent receipt')
            services.append(service(root/'services'/clock['key'],clock,worker,freeze))
        for d,T in s.TASKS:
            for target in s.TARGETS:
                for seed in s.SEEDS:pairs.append(paired(worker,d,T,target,seed,services))
    index={(r['worker'],r['key']):r for r in services}
    for worker in (0,1):
        for d,T in s.TASKS:
            for target in s.TARGETS:
                for seed in s.SEEDS:
                    a=index[worker,s.key('relu-screened',d,T,target,seed)];b=index[worker,s.key('relu-native',d,T,target,seed)]
                    need(a['transcript']==b['transcript'] and a['status']==b['status'],'native exact solver preserves complete neural transcript')
    host_identity=all(index[0,key]['transcript']==index[1,key]['transcript'] for _,key in index if _==0)
    groups=[]
    for d,T in s.TASKS:
        for target in s.TARGETS:
            rows=[r for r in services if (r['d'],r['T'],r['target'])==(d,T,str(target))]
            methods={mode:dict(warm_median=statistics.median(r['complete_return_seconds'] for r in rows if r['mode']==mode),warm_range=[min(r['complete_return_seconds'] for r in rows if r['mode']==mode),max(r['complete_return_seconds'] for r in rows if r['mode']==mode)],cold_median=statistics.median(r['cold_return_seconds'] for r in rows if r['mode']==mode),attained=sum(r['status']=='target_attained' for r in rows if r['mode']==mode),services=sum(r['mode']==mode for r in rows)) for mode in s.MODES}
            groups.append(dict(d=d,T=T,target=str(target),methods=methods,least_warm_recorded_method=min(methods,key=lambda m:methods[m]['warm_median']),least_cold_recorded_method=min(methods,key=lambda m:methods[m]['cold_median'])))
    result=dict(status='passed',baseline_commit='00412e6a4f43100996b324ea1ace097232c3fbbf',review_commit='8f56a3ae24ef3ce4383d0e9d1d757bd3ed7378c6',source_freeze_sha256=freeze,recording_amendment_sha256=amend,counts=COUNTS,services=services,groups=groups,paired=pairs,stress=stresses,two_control=multirows,bellman=bells,cohort_environments=[x['environment'] for x in cohorts],all_neural_transcripts_identical=True,host_transcripts_identical=host_identity,attained_host_services=sum(r['status']=='target_attained' for r in services),budget_exhausted_host_services=sum(r['status']=='budget_exhausted' for r in services),scientific_host_executions=96,mathematical_service_designs=48,unique_stress_instances=90,unique_two_control_instances=16,failed_predecessor_files_retained=len(first['files_sha256']),audit_seconds=time.perf_counter()-begin,new_training_by_audit=0,new_statistical_observations_by_audit=0,scope='Every declared record bound; exact solvers, saved-critic witnesses, whole-cell certificates, Bellman brackets and unique original-law path streams reconstructed without retraining. Existing clocks retained, not remeasured. Repeated hosts are not new independent observations; code verification is not external mathematical approval.')
    save(R/'audit/RESULT_AUDIT60.json',result)
    save(R/'audit/SUMMARY60.json',{k:v for k,v in result.items() if k not in ('stress','services','paired','two_control')})
    print(json.dumps({k:v for k,v in result.items() if k not in ('stress','services','paired','two_control','groups','bellman')},indent=2))
if __name__=='__main__':main()
