"""Full R60 mathematical replay from frozen inputs; original clocks stay intact.

No training is repeated. Exact solvers, whole-cell verifiers and the original
continuous-law endpoint paths are reconstructed. Duplicate numerical objects
are cached by their complete inputs, never counted as independent samples.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib,json,statistics,time
import numpy as np
import services60 as s
import services60b as sb
import stress60 as st
import search60 as u
import multi60 as multi
import bellman60 as bell
import centered60 as centered
import audit56 as inherited
import revalidate61 as rv
R=Path(__file__).resolve().parents[1];n=s.n;p=s.p
SCALARS={};REFERENCES={};MODELS={};VERIFIERS={};PATHS={};PAIRS={}
COUNTS=dict(service_files=0,service_stages=0,cell_decisions=0,stopping_looks=0,ci_records=0,distinct_models=0,distinct_verifiers=0,distinct_path_calculations=0,distinct_path_rows=0,scalar_reference_objects=0,scalar_solver_records=0,two_control_records=0,distinct_extra_witness_cell_changes=0)

def read(path):return json.loads(Path(path).read_text())
def need(x,msg):
    if not x:raise AssertionError(msg)
def equal(a,b,msg):need(np.array_equal(np.asarray(a),np.asarray(b)),msg)
def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,v):rv.save(path,v)
def scalar_key(o,cap,Q):return(st.canonical(o.payload()),cap,Q)
def scalar_reference(o,cap,Q):
    key=scalar_key(o,cap,Q)
    if key not in REFERENCES:
        values=[o.value(F(j,Q)) for j in range(cap+1)];best=min(range(cap+1),key=lambda j:(values[j],j))
        REFERENCES[key]=dict(index=best,objective_exact=str(values[best]),all_minimizers=[j for j,v in enumerate(values) if v==values[best]])
        COUNTS['scalar_reference_objects']+=1
    return REFERENCES[key]
def check_scalar(o,cap,Q,record):
    key=scalar_key(o,cap,Q);ref=scalar_reference(o,cap,Q)
    need(record['index']==ref['index'] and F(record['objective_exact'])==F(ref['objective_exact']),'original scalar minimizer/tie rule')
    mode=record['method'];bits=record.get('bound_fraction_bits',53);ckey=(*key,mode,bits)
    if ckey not in SCALARS:SCALARS[ckey]=u.solve(o,cap,Q,mode,bits=bits)
    got=SCALARS[ckey]
    fields=('index','objective_exact','method','lattice_size','exact_evaluations','difference_queries','pieces','candidate_count','isolated_roots','fallback','fallback_reason','screened_points','retained_points','screen_survivors','bound_fraction_bits','pair_nodes','pruned_nodes','peak_stack','pre_fallback_exact_evaluations','original_ridges','active_ridges','eliminated_ridges','offset_exact','max_recorded_operand_bits','largest_single_pair_array_bytes','endpoint_sha256')
    for name in fields:
        if name in record:need(got.get(name)==record[name],'scalar diagnostic '+name)
    COUNTS['scalar_solver_records']+=1

def stress(worker):
    root=R/'results60'/f'worker{worker}'/'stress';summary=read(root/'summary.json')
    expected=set(product(st.SEEDS,st.WIDTHS,st.SIZES,st.REGIMES));seen=set();objects={}
    for row in summary['factorial']:
        ident=(row['seed'],row['width'],row['size'],row['regime']);need(ident in expected and ident not in seen,'factorial completeness');seen.add(ident)
        raw=read(root/'cases'/(row['key']+'.json'));o,cap,Q=st.fixture(*ident)
        need(raw['objective']==o.payload() and raw['objective_sha256']==st.canonical(o.payload()),'fixed stress primitive identity')
        need((raw['cap'],raw['Q'])==(cap,Q),'stress lattice');ref=scalar_reference(o,cap,Q)
        for name in ref:need(raw['reference'][name]==ref[name],'independent exhaustive reference '+name)
        objects[row['objective_sha256']]=(o,cap,Q)
        need(set(row['order'])==set(u.METHODS) and [x['method'] for x in row['runs']]==row['order'],'complete randomized solver order')
        for rec in row['runs']+row['coarse_endpoint_diagnostics']:check_scalar(o,cap,Q,rec)
        need([r['bound_fraction_bits'] for r in row['coarse_endpoint_diagnostics']]==[8,24],'declared endpoint precision diagnostics')
    need(seen==expected and len(summary['factorial'])==90,'90 stress instances')
    need(len(summary['repetitions'])==35,'seven repetitions of five fixed instances')
    repeated_seen=set()
    for row in summary['repetitions']:
        ident=(row['regime'],row['rep']);need(ident not in repeated_seen and row['rep'] in range(7),'repetition identity');repeated_seen.add(ident)
        o,cap,Q=st.fixture(st.SEEDS[0],32,129,row['regime']);need(st.canonical(o.payload())==row['objective_sha256'],'prespecified repeated subset')
        need([r['method'] for r in row['runs']]==row['order'] and set(row['order'])==set(u.METHODS),'repetition method order')
        for rec in row['runs']:check_scalar(o,cap,Q,rec)
    guards=[]
    for row in summary['fallback_frontier']:
        o,cap,Q=st.fixture(st.SEEDS[0],8,row['size'],row['regime']);need(o.payload()==row['objective'],'guard objective')
        for rec in row['runs']:check_scalar(o,cap,Q,rec)
        for name in scalar_reference(o,cap,Q):need(row['reference'][name]==scalar_reference(o,cap,Q)[name],'guard exact reference')
        guards.extend(dict(worker=worker,size=row['size'],regime=row['regime'],**r) for r in row['runs'])
    need(len(summary['fallback_frontier'])==8,'complete large-lattice catalogue')
    aggregate=[]
    for regime in st.REGIMES:
        for method in u.METHODS:
            rows=[r for x in summary['factorial'] if x['regime']==regime for r in x['runs'] if r['method']==method]
            reps=[r['seconds'] for x in summary['repetitions'] if x['regime']==regime for r in x['runs'] if r['method']==method]
            aggregate.append(dict(worker=worker,regime=regime,method=method,cases=len(rows),median_seconds=statistics.median(r['seconds'] for r in rows),total_seconds=sum(r['seconds'] for r in rows),repeated_median_seconds=statistics.median(reps),repeated_min_seconds=min(reps),repeated_max_seconds=max(reps),fallbacks=sum(r.get('fallback',False) for r in rows),maximum_survivors=max([0]+[r.get('screen_survivors',0) for r in rows]),maximum_operand_bits=max([0]+[r.get('max_recorded_operand_bits',0) for r in rows]),largest_pair_array_bytes=max([0]+[r.get('largest_single_pair_array_bytes',0) for r in rows])))
    wins={method:0 for method in u.METHODS}
    for row in summary['factorial']:wins[min(row['runs'],key=lambda r:r['seconds'])['method']]+=1
    return dict(worker=worker,environment=summary['environment'],aggregate=aggregate,guards=guards,fastest_instance_counts=wins,factorial=summary['factorial'],repetitions=summary['repetitions'])

def two_controls(worker):
    root=R/'results60'/f'worker{worker}'/'two-control';summary=read(root/'summary.json');need(len(summary['rows'])==16,'two-control catalogue')
    rows=[]
    for row in summary['rows']:
        training=read(root/f'training-{row["seed"]}.json');critic=inherited.load_critic(training['critics'][1])
        o=multi.from_critic(list(map(F,row['state'])),critic,row['shocks']==2)
        need(o.payload()==row['objective'],'trained multi-control objective identity')
        ref=multi.exhaustive(o,row['cap'],row['Q']);got=multi.adaptive(o,row['cap'],row['Q'])
        for original,current in ((row['reference'],ref),(row['adaptive'],got)):
            for name in original:
                if name!='seconds':need(current.get(name)==original[name],'multi-control exact recovery '+name)
        need(sum(got['index'])<=row['cap'],'shared-capacity feasibility')
        COUNTS['two_control_records']+=1
        rows.append(dict(worker=worker,seed=row['seed'],state=row['state'],cap=row['cap'],Q=row['Q'],shocks=row['shocks'],index=got['index'],exhaustive_evaluations=ref['evaluations'],adaptive_evaluations=got['evaluations'],nodes=got['nodes'],fallback=got['fallback'],exhaustive_seconds=row['reference']['seconds'],adaptive_seconds=row['adaptive']['seconds'],ties=ref['ties']))
    return rows

def model_replay(model,d,T,N,q,mode):
    key=(d,T,N,q,mode,p.canonical(model['critics']))
    if key in MODELS:return MODELS[key]
    part=n.Partition(d,N);need(part.payload()==model['partition'],'acquired partition identity');critics=[inherited.load_critic(v) for v in model['critics']]
    if mode=='common-only':grid,exact,witnesses=u.sc.a.proposals(critics,part,'common-only')
    elif mode=='relu-screened':grid,exact,witnesses=u.sc.proposals(critics,part,'screened')
    else:grid,exact,witnesses,native_work=u.proposals(critics,part)
    equal(grid,model['grid'],'original finite-menu proposal');equal(exact,model['exact'],'original exact proposal');need(witnesses==model['witnesses'],'all exact witness records')
    vkey=(d,T,N,q,grid.tobytes(),None if mode=='common-only' else exact.tobytes())
    if vkey not in VERIFIERS:
        verifier=u.sc.a.ReferenceVerifier(part,T,q);policy,dates,raw=verifier.sweep(grid,None if mode=='common-only' else exact)
        VERIFIERS[vkey]=dict(policy=policy,dates=dates,raw=raw,work=verifier.work)
        COUNTS['distinct_verifiers']+=1;COUNTS['distinct_extra_witness_cell_changes']+=sum(z['extra_witness_changes'] for z in dates)
    result=dict(part=part,grid=grid,exact=exact,witnesses=witnesses,**VERIFIERS[vkey]);MODELS[key]=result;COUNTS['distinct_models']+=1
    return result

def regenerate_paths(policy,part,T,target,seed,stage,looks):
    key=(part.d,T,str(target),seed,stage,p.policy_hash(policy,part),tuple(looks))
    if key in PATHS:return PATHS[key]
    tag=f'NBO-R60-STOP-d{part.d}-T{T}-q{target}-seed{seed}-stage{stage}'
    rng=np.random.Generator(np.random.PCG64(s.prior.seed_for(tag)));stream=hashlib.sha256();lo=[];hi=[];zl=[];zh=[];previous=0;out={};zero=np.zeros_like(policy)
    for look in looks:
        for offset in range(previous,look,2048):
            bins,x,z=s.prior.paths(rng,min(2048,look-offset),part.d,T);stream.update(bins.tobytes());val=n.score(policy,part,x,z);base=n.score(zero,part,x,z)
            lo.extend(val.lo);hi.extend(val.hi);zl.extend(base.lo);zh.extend(base.hi)
        out[look]=dict(policy_lo=np.array(lo),policy_hi=np.array(hi),zero_lo=np.array(zl),zero_hi=np.array(zh),stream_sha256=stream.hexdigest());previous=look
    COUNTS['distinct_path_calculations']+=1;COUNTS['distinct_path_rows']+=previous;PATHS[key]=out;return out

def looks_replay(folder,policy,part,T,target,seed,stage,looks):
    need(looks==list(s.LOOKS[:len(looks)]) and bool(looks),'declared sequential looks')
    generated=regenerate_paths(policy,part,T,target,seed,stage,looks);H=p.old.inference.support(T,1)[1]
    for j,look in enumerate(looks):
        file=folder/f'stage{stage}-look{look}.npz';rec=read(folder/f'stage{stage}-look{look}.json');got=generated[look]
        need(digest(file)==rec['raw_sha256'],'inference archive identity')
        with np.load(file) as z:
            need(set(z.files)=={'policy_lo','policy_hi','zero_lo','zero_hi'},'inference fields')
            for name in z.files:equal(z[name],got[name],'continuous-law path reintegration '+name)
        val=n.I(got['policy_lo'],got['policy_hi']);zero=n.I(got['zero_lo'],got['zero_hi']);difference=val-n.s.c.rat_i(target)*zero;gain=zero-val
        inherited.verify_ci(val.lo,val.hi,F(0),H,rec['cost']);inherited.verify_ci(difference.lo,difference.hi,-target*H,H,rec['target_contrast']);inherited.verify_ci(gain.lo,gain.hi,-H,H,rec['gain'])
        need(rec['paths']==look and rec['stream_sha256']==got['stream_sha256'],'path stream identity')
        met=F(rec['target_contrast']['exact'][1])<=0;positive=F(rec['target_contrast']['exact'][0])>0;need(rec['crossed']==met,'stopping classification')
        if j<len(looks)-1:need(not met and not positive,'continued after a stopping condition')
        else:need(met or positive or look==s.LOOKS[-1],'premature inference stop')
        COUNTS['ci_records']+=3;COUNTS['stopping_looks']+=1
    return rec

def service(folder,clock,freeze):
    svc=read(folder/'service.json');durable=read(folder/'clock.json')
    need(svc['source_freeze_sha256']==freeze and clock['returncode']==0,'service source and exit')
    need(digest(folder/'service.json')==durable['service_sha256'],'durable scientific record')
    need(clock['complete_return_seconds']>=clock['process_and_log_seconds']>=durable['seconds_through_record']>0,'complete return clock boundary')
    need(abs(clock['cold_return_seconds']-clock['complete_return_seconds']-clock['cold_compile_seconds'])<1e-8,'cold compile account')
    need(sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())==clock['serialized_bytes'],'all serialized bytes')
    actual={f.name for f in folder.iterdir() if f.is_file()}-{'service.json','clock.json'};need(actual==set(svc['files_sha256']),'all service files registered')
    for name,h in svc['files_sha256'].items():need(digest(folder/name)==h,'service hash '+name);COUNTS['service_files']+=1
    d,T,mode,seed=svc['d'],svc['T'],svc['mode'],svc['seed'];target=F(svc['target'])
    need(folder.name==s.key(mode,d,T,target,seed),'prespecified service key')
    need(svc['statistical_family']==dict(alpha='1/100',maximum_intervals=2048,log_upper=14),'statistical family')
    stages=[]
    for k,rec in enumerate(svc['stages']):
        need(k<len(s.RUNGS) and rec==read(folder/f'stage{k}.json'),'complete stage record');samples,N,q=s.RUNGS[k]
        need((rec['samples'],rec['leaves'],rec['innovation_bins'])==(samples,N,q),'original resource ladder')
        model=read(folder/f'stage{k}-models.json');need(digest(folder/f'stage{k}-models.json')==rec['models_sha256'],'model archive identity')
        need(p.canonical(model['critics'])==rec['critic_parameters_sha256'],'fitted parameter identity')
        got=model_replay(model,d,T,N,q,mode);policy=got['policy'];part=got['part'];equal(policy,model['policy'],'returned complete policy')
        need(got['dates']==rec['dates'] and got['work']==rec['verification_work'],'datewise certificate/work account')
        file=folder/f'stage{k}-certificate.npz';need(digest(file)==rec['certificate_sha256'],'certificate archive identity')
        with np.load(file) as z:
            need(set(z.files)==set(got['raw']),'all whole-cell certificate fields')
            for name,value in got['raw'].items():equal(z[name],value,'primitive whole-cell reintegration '+name)
        need(p.policy_hash(policy,part)==rec['policy_sha256'],'policy and acquired geometry hash')
        loss=[min(p.old.inference.support(T-t,1)[1],(n.BETA*p.old.inference.support(T-t-1,1)[1] if t<T-1 else F(0))+F(rec['dates'][t]['gap_upper'])) for t in range(T)]
        need(list(map(str,loss))==rec['all_state_policy_loss_bound_exact'],'original loss bound arithmetic')
        last=looks_replay(folder,policy,part,T,target,seed,k,rec['look_paths']);met=last['crossed'];need(rec['target_attained']==met,'stage stopping status')
        if met:need(k==len(svc['stages'])-1,'construction after successful target')
        stages.append(dict(stage=k,policy_sha256=rec['policy_sha256'],critic_sha256=rec['critic_parameters_sha256'],look_paths=rec['look_paths'],cost=last['cost']['interval'],gain=last['gain']['interval'],target_contrast=last['target_contrast']['interval'],dates=rec['dates'],maximum_loss_bound=max(map(float,loss)),action_search_seconds=rec['action_search_seconds'],construction_seconds=rec['construction_seconds'],verification_seconds=rec['verification_seconds']))
        COUNTS['cell_decisions']+=T*N;COUNTS['service_stages']+=1
    need(bool(stages) and svc['status']==('target_attained' if met else 'budget_exhausted'),'final service status')
    if not met:need(len(stages)==len(s.RUNGS),'premature budget exhaustion')
    need(svc['final_policy_sha256']==stages[-1]['policy_sha256'],'final output identity')
    return dict(worker=svc['worker'],key=folder.name,d=d,T=T,mode=mode,seed=seed,target=str(target),status=svc['status'],stages=stages,final_policy_sha256=svc['final_policy_sha256'],complete_return_seconds=clock['complete_return_seconds'],cold_return_seconds=clock['cold_return_seconds'],cold_compile_seconds=clock['cold_compile_seconds'],peak_python_rss_kib=svc['peak_python_rss_kib'],peak_child_rss_kib=svc['peak_child_rss_kib'])

def paired(worker,folder):
    rec=read(folder/'paired.json');d,T,target,seed=rec['d'],rec['T'],F(rec['target']),rec['seed'];actors=[];identities=[]
    for mode in s.MODES:
        sf=s.directory(worker)/'services'/s.key(mode,d,T,target,seed);sv=read(sf/'service.json');stage=sv['stages'][-1];mo=read(sf/f'stage{stage["stage"]}-models.json');part=n.Partition(d,stage['leaves']);policy=np.array(mo['policy'],dtype=np.uint16);actors.append((part,policy));identities.append(p.policy_hash(policy,part))
    need(list(s.MODES)==rec['mode_order'] and identities==rec['policy_sha256'] and identities[2]==identities[3],'matched complete neural outputs')
    key=(d,T,str(target),seed,tuple(identities));H=p.old.inference.support(T,1)[1]
    if key not in PAIRS:
        rng=np.random.Generator(np.random.PCG64(s.prior.seed_for(f'NBO-R60-FRESH-PAIRED-d{d}-T{T}-q{target}-seed{seed}')));stream=hashlib.sha256();lo=[[] for _ in s.MODES];hi=[[] for _ in s.MODES]
        for offset in range(0,65536,2048):
            bins,x,z=s.prior.paths(rng,2048,d,T);stream.update(bins.tobytes())
            for k,(part,policy) in enumerate(actors):val=n.score(policy,part,x,z);lo[k].extend(val.lo);hi[k].extend(val.hi)
        PAIRS[key]=(np.array(lo),np.array(hi),stream.hexdigest());COUNTS['distinct_path_calculations']+=1;COUNTS['distinct_path_rows']+=65536
    lo,hi,stream=PAIRS[key];need(digest(folder/'endpoints.npz')==rec['raw_sha256'],'paired raw archive')
    with np.load(folder/'endpoints.npz') as z:equal(z['lower'],lo,'paired lower reintegration');equal(z['upper'],hi,'paired upper reintegration')
    need(rec['paths']==65536 and rec['stream_sha256']==stream,'fresh independent paired stream identity')
    for k in range(3):
        old=rec['contrasts'][s.MODES[k]]
        if identities[k]==identities[3]:need(old.get('identity') and old['exact']==['0','0'],'exact identical-policy contrast')
        else:
            v=n.I(lo[3],hi[3])-n.I(lo[k],hi[k]);inherited.verify_ci(v.lo,v.hi,-H,H,old)
        COUNTS['ci_records']+=1
    return dict(worker=worker,d=d,T=T,target=str(target),seed=seed,contrasts=rec['contrasts'],seconds=rec['seconds'],policy_sha256=identities)

def bellman_replay():
    uncentered=[];start=time.perf_counter()
    for N,A,q in bell.RUNGS:
        got,raw=bell.rung(N,A,q)
        for worker in (0,1):
            root=R/'results60'/f'worker{worker}'/'bellman';summary=read(root/'summary.json');old=next(x for x in summary['rungs'] if x['N']==N)
            need(digest(root/f'N{N}.npz')==old['raw_sha256'],'uncentered raw identity')
            with np.load(root/f'N{N}.npz') as z:
                for name,val in raw.items():equal(z[name],val,'uncentered original Bellman reintegration')
            for name in ('dates','initial_gap_upper','maximum_date_gap_upper','table_bytes'):need(got[name]==old[name],'uncentered report '+name)
            uncentered.append(dict(worker=worker,**old))
    original_seconds=time.perf_counter()-start;start=time.perf_counter();summary=read(R/'results60-centered/summary.json')
    for N,A,q in centered.RUNGS:
        got,raw=centered.rung(N,A,q);old=next(x for x in summary['rows'] if x['N']==N);path=R/'results60-centered'/f'N{N}.npz'
        need(digest(path)==old['raw_sha256'],'centered raw identity')
        with np.load(path) as z:
            need(set(z.files)==set(raw),'centered archive fields')
            for name,val in raw.items():equal(z[name],val,'common-reference primitive reintegration '+name)
        for name in ('dates','initial_gap_upper','maximum_date_gap_upper','table_bytes'):need(got[name]==old[name],'centered report '+name)
    for target in summary['targets']:
        hit=next((z for z in summary['rows'] if F(z['maximum_date_gap_upper'])<=F(target['tolerance'])),None)
        need(target['status']==('attained' if hit else 'budget_exhausted') and target['N']==(hit['N'] if hit else None),'centered unrounded first attainment')
    return dict(uncentered=uncentered,uncentered_replay_seconds=original_seconds,centered=summary,centered_replay_seconds=time.perf_counter()-start)

def main():
    begin=time.perf_counter();freeze=rv.verify();provenance=read(R/'audit/PREPARATION61.json')
    for family in ('protected_sha256','scientific_sha256'):
        for name,h in provenance[family].items():need(digest(R/name)==h,'preserved source/evidence '+name)
    print('Source identities verified; replaying scalar stress catalogues.',flush=True)
    stresses=[stress(w) for w in (0,1)];multis=[x for w in (0,1) for x in two_controls(w)]
    print('Exact scalar and two-control witnesses verified; reconstructing complete services.',flush=True)
    rows=[];pairs=[];environments=[]
    for worker in (0,1):
        root=s.directory(worker);cohort=read(root/'cohort.json');clocks=read(root/'process-clocks.json');need(cohort['runs']==clocks['runs'],'final complete-process ledger')
        need(cohort['source_freeze_sha256']==sb.verify(),'amended recorder identity');expected={s.key(m,d,T,q,z) for d,T in s.TASKS for m in s.MODES for q in s.TARGETS for z in s.SEEDS}
        need({x['key'] for x in cohort['runs']}==expected and len(cohort['runs'])==48,'complete prescribed service catalogue')
        need({x.name for x in (root/'services').iterdir() if x.is_dir()}==expected,'no omitted or additional services')
        for j,clock in enumerate(cohort['runs'],1):
            check=read(root/'checkpoints'/f'{j:03d}.json');need(check['runs']==cohort['runs'][:j],'immutable parent checkpoint')
            need(digest(root/'logs'/(clock['key']+'.log'))==clock['log_sha256'],'child log identity')
            need(digest(root/'receipts'/(clock['key']+'.json'))==clock['receipt_sha256'],'first durable receipt identity')
            rows.append(service(root/'services'/clock['key'],clock,s.verify()))
            if j%8==0:print(json.dumps(dict(worker=worker,services=j,counts=COUNTS)),flush=True)
        for folder in sorted((root/'paired').iterdir()):
            if folder.is_dir():pairs.append(paired(worker,folder))
        environments.append(dict(worker=worker,environment=cohort.get('environment'),compilation=cohort['compile_record']))
    need(len(rows)==96 and len(pairs)==24,'full fresh comparison catalogue')
    for worker,d,T,target,seed in product((0,1),[2,4,8],[2,4,6],s.TARGETS,s.SEEDS):
        if (d,T) not in s.TASKS:continue
        a=next(r for r in rows if r['worker']==worker and r['key']==s.key('relu-screened',d,T,target,seed));b=next(r for r in rows if r['worker']==worker and r['key']==s.key('relu-native',d,T,target,seed))
        need(a['status']==b['status'] and len(a['stages'])==len(b['stages']),'lossless prospective stopping')
        for x,y in zip(a['stages'],b['stages']):
            for name in ('policy_sha256','critic_sha256','look_paths','cost','gain','target_contrast','dates'):need(x[name]==y[name],'lossless native/screened transcript '+name)
    print('All original-law service and paired paths verified; reconstructing Bellman frontiers.',flush=True)
    bells=bellman_replay();result=dict(status='passed',source_freeze_sha256=freeze,counts=COUNTS,services=len(rows),attained=sum(r['status']=='target_attained' for r in rows),budget_exhausted=sum(r['status']=='budget_exhausted' for r in rows),rows=rows,paired=pairs,stress=stresses,two_controls=multis,environments=environments,validated_policy_hashes=sorted(set(r['final_policy_sha256'] for r in rows)),centered_raw_sha256=digest(R/'results60-centered/N128.npz'),**bells,protected_files_checked=len(provenance['protected_sha256']),scientific_files_checked=len(provenance['scientific_sha256']),replay_seconds=time.perf_counter()-begin,new_training_services=0,new_independent_path_observations=0,original_clocks_replaced=False,scope='Every retained R60 service file, mathematical decision, exact solver record, distinct original-law endpoint calculation and Bellman bracket reconstructed. Old timers remain descriptive observed work; this replay adds no training or independent economic observations. Exact scalar witnesses are checked against Python Fraction exhaustive references; retained operand diagnostics are not a proof of the maximum of every native intermediate.')
    save(R/'audit/SCIENCE_REPLAY61.json',result)
    save(R/'audit/SCIENCE_SUMMARY61.json',{k:v for k,v in result.items() if k not in ('rows','paired','stress','two_controls','uncentered','centered')})
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','paired','stress','two_controls','uncentered','centered','validated_policy_hashes','environments')},indent=2),flush=True)
if __name__=='__main__':main()
