"""Offline R58 reintegration for the R59 original-paper revision.

Both exact solvers are run from saved fitted parameters. Every stored file and
row is checked; identical model and path calculations are memoized but not
counted as additional independent observations. No retraining or retiming.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time
import numpy as np
import study58 as s
import screen58 as sc
import audit56 as inherited
from prepare59 import main as inspect_catalogue
p=s.p;n=s.n;R=s.R
MODELS={};PATHS={}
COUNTS=dict(distinct_model_reintegrations=0,distinct_solver_calls=0,distinct_neural_calls=0,distinct_screened_lattice_points=0,distinct_screened_survivors=0,distinct_path_streams=0,distinct_path_rows=0,checked_cell_decisions=0,checked_stopping_looks=0,checked_ci_records=0,checked_service_files=0)

def need(x,msg):
    if not x:raise AssertionError(msg)
def equal(x,y,msg):need(np.array_equal(np.asarray(x),np.asarray(y)),msg)
def read(path):return json.loads(path.read_text())
def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def model_replay(model,d,T,N,q):
    ident=(d,T,N,q,p.canonical(model['critics']))
    if ident in MODELS:return MODELS[ident]
    part=n.Partition(d,N);need(part.payload()==model['partition'],'non-tensor partition identity')
    critics=[inherited.load_critic(c) for c in model['critics']]
    outputs={mode:sc.proposals(critics,part,mode) for mode in s.MODES}
    ga,ea,wa=outputs['algebraic'];gs,es,ws=outputs['screened']
    equal(ga,gs,'lossless common menu');equal(ea,es,'lossless exact neural witnesses')
    need(len(wa)==len(ws)==T*N,'full action witness count')
    for a,b in zip(wa,ws):
        for field in ('index','objective_exact','date','leaf','common_terminal'):
            need(a[field]==b[field],'exact solver equivalence: '+field)
        if not b['common_terminal']:
            COUNTS['distinct_neural_calls']+=1
            COUNTS['distinct_screened_lattice_points']+=b.get('screened_points',0)
            COUNTS['distinct_screened_survivors']+=b.get('retained_points',0)
            # Validate every original lattice endpoint, not just the selected
            # survivor, using exact values in a disjoint small-fixture test.
            # Production endpoints themselves are re-evaluated and hashed by
            # the screened solver above; its selected value is rational.
    verifier=sc.a.ReferenceVerifier(part,T,q);policy,dates,raw=verifier.sweep(ga,ea)
    result=dict(part=part,outputs=outputs,policy=policy,dates=dates,raw=raw,work=verifier.work)
    MODELS[ident]=result;COUNTS['distinct_model_reintegrations']+=1;COUNTS['distinct_solver_calls']+=2*T*N
    return result

def regenerate_paths(policy,part,T,target,stage,look_paths):
    key=(part.d,T,str(target),stage,p.policy_hash(policy,part),tuple(look_paths))
    if key in PATHS:return PATHS[key]
    rng=s.rng_for(part.d,T,target,stage);stream=hashlib.sha256();lower=[];upper=[];zl=[];zu=[];previous=0;records={};zero=np.zeros_like(policy)
    for look in look_paths:
        for off in range(previous,look,2048):
            bins,x,z=s.old.paths(rng,min(2048,look-off),part.d,T);stream.update(bins.tobytes())
            value=n.score(policy,part,x,z);base=n.score(zero,part,x,z)
            lower.extend(value.lo);upper.extend(value.hi);zl.extend(base.lo);zu.extend(base.hi)
        records[look]=dict(policy_lo=np.array(lower),policy_hi=np.array(upper),zero_lo=np.array(zl),zero_hi=np.array(zu),stream_sha256=stream.hexdigest())
        previous=look
    COUNTS['distinct_path_streams']+=1;COUNTS['distinct_path_rows']+=previous
    PATHS[key]=records;return records

def check_looks(folder,policy,part,T,target,stage,look_paths):
    need(bool(look_paths),'missing inference looks')
    need(look_paths==list(s.LOOKS[:len(look_paths)]),'undeclared inference look sequence')
    generated=regenerate_paths(policy,part,T,target,stage,look_paths);H=p.old.inference.support(T,1)[1];last=None
    for j,look in enumerate(look_paths):
        file=folder/f'stage{stage}-look{look}.npz';record=read(folder/f'stage{stage}-look{look}.json');got=generated[look]
        need(digest(file)==record['raw_sha256'],'path archive identity');need(record['paths']==look,'path count')
        with np.load(file) as z:
            need(set(z.files)=={'policy_lo','policy_hi','zero_lo','zero_hi'},'complete raw path fields')
            for name in z.files:equal(z[name],got[name],'full path endpoint reintegration '+name)
        value=n.I(got['policy_lo'],got['policy_hi']);base=n.I(got['zero_lo'],got['zero_hi']);difference=value-n.s.c.rat_i(target)*base;gain=base-value
        inherited.verify_ci(value.lo,value.hi,F(0),H,record['cost'])
        inherited.verify_ci(difference.lo,difference.hi,-target*H,H,record['target_contrast'])
        inherited.verify_ci(gain.lo,gain.hi,-H,H,record['gain'])
        need(record['stream_sha256']==got['stream_sha256'],'frozen inference stream')
        met=F(record['target_contrast']['exact'][1])<=0;positive=F(record['target_contrast']['exact'][0])>0
        need(record['crossed']==met,'target endpoint classification')
        if j<len(look_paths)-1:need(not met and not positive,'extra look after first stopping condition')
        else:need(met or positive or look==s.LOOKS[-1],'unexplained early inference stop')
        COUNTS['checked_stopping_looks']+=1;COUNTS['checked_ci_records']+=3;last=record
    return last

def check_service(folder,clock,freeze):
    service=read(folder/'service.json');need(service['key']==folder.name,'service key');need(service['source_freeze_sha256']==freeze,'source freeze binding')
    need(clock['returncode']==0,'failed service');need(sum(x.stat().st_size for x in folder.rglob('*') if x.is_file())==clock['serialized_bytes'],'serialized bytes')
    durable=read(folder/'clock.json');need(digest(folder/'service.json')==durable['record_sha256'],'durable record identity')
    need(clock['whole_process_seconds']>=durable['seconds_through_record_fsync']>0,'complete process clock')
    actual={x.name for x in folder.iterdir() if x.is_file()}-{'service.json','clock.json'}
    need(actual==set(service['files_sha256']),'unregistered service files')
    for name,h in service['files_sha256'].items():need(digest(folder/name)==h,'service file hash '+name);COUNTS['checked_service_files']+=1
    d,T=service['d'],service['T'];mode=service['mode'];target=F(service['target']);rep=service['repetition']
    need(service['seed']==s.SEED and folder.name==s.key(mode,d,T,target,rep),'prespecified service identity')
    need(service['statistical_family']==dict(alpha='1/100',maximum_intervals=2048,log_upper=14),'statistical family')
    need(service['frequency_controlled'] is False,'unsupported frequency control')
    stages=[]
    for stage,rec in enumerate(service['stages']):
        need(stage<len(s.RUNGS),'extra construction attempt');need(read(folder/f'stage{stage}.json')==rec,'stage record identity')
        samples,N,q=s.RUNGS[stage];need((rec['samples'],rec['leaves'],rec['innovation_bins'])==(samples,N,q),'resource ladder')
        model=read(folder/f'stage{stage}-models.json');need(digest(folder/f'stage{stage}-models.json')==rec['models_sha256'],'model hash')
        need(p.canonical(model['critics'])==rec['critic_parameters_sha256'],'fitted parameter identity')
        reconstructed=model_replay(model,d,T,N,q);part=reconstructed['part'];grid,exact,witnesses=reconstructed['outputs'][mode]
        equal(grid,model['grid'],'saved grid proposal');equal(exact,model['exact'],'saved exact proposal')
        need(witnesses==model['witnesses'],'every solver witness and diagnostic')
        policy=reconstructed['policy'];equal(policy,model['policy'],'whole acquired policy')
        need(rec['dates']==reconstructed['dates'],'datewise exact accounting');need(rec['work']==reconstructed['work'],'verifier operation counts')
        rawfile=folder/f'stage{stage}-certificate.npz';need(digest(rawfile)==rec['certificate_sha256'],'certificate hash')
        with np.load(rawfile) as z:
            need(set(z.files)==set(reconstructed['raw']),'complete certificate fields')
            for name,values in reconstructed['raw'].items():equal(z[name],values,'full certificate reintegration '+name)
        need(p.policy_hash(policy,part)==rec['policy_sha256'],'policy and observation identity')
        loss=[min(p.old.inference.support(T-t,1)[1],(n.BETA*p.old.inference.support(T-t-1,1)[1] if t<T-1 else F(0))+F(rec['dates'][t]['gap_upper'])) for t in range(T)]
        need(list(map(str,loss))==rec['all_state_policy_loss_bound_exact'],'original Bellman-loss account')
        neural=[w for w in witnesses if not w['common_terminal']]
        stats=dict(neural_searches=len(neural),neural_root_isolations=sum(w['isolated_roots'] for w in neural),neural_exact_evaluations=sum(len(w['candidate_indices']) for w in neural),neural_screened_points=sum(w.get('screened_points',0) for w in neural),neural_retained_points=sum(w.get('retained_points',0) for w in neural),neural_active_ridges=sum(w.get('active_ridges',0) for w in neural),neural_eliminated_ridges=sum(w.get('eliminated_ridges',0) for w in neural),fallbacks=sum(w.get('solver')=='algebraic-fallback' for w in neural))
        for name,value in stats.items():need(rec[name]==value,'action-search operation count '+name)
        last=check_looks(folder,policy,part,T,target,stage,rec['look_paths']);met=last['crossed'];need(met==rec['target_attained'],'stage target')
        if met:need(stage==len(service['stages'])-1,'construction continued after target')
        COUNTS['checked_cell_decisions']+=T*N
        stages.append(dict(stage=stage,policy_sha256=rec['policy_sha256'],critic_sha256=rec['critic_parameters_sha256'],look_paths=rec['look_paths'],cost=last['cost']['exact'],gain=last['gain']['exact'],target_contrast=last['target_contrast']['exact'],dates=rec['dates'],work=rec['work'],search=stats))
    need(bool(stages),'missing construction stages');need(service['status']==('target_attained' if met else 'budget_exhausted'),'final stopping status')
    if not met:need(len(stages)==len(s.RUNGS),'premature budget exhaustion')
    need(service['final_policy_sha256']==stages[-1]['policy_sha256'],'returned policy hash')
    return dict(key=folder.name,d=d,T=T,mode=mode,target=str(target),rep=rep,status=service['status'],stages=stages,cpu_affinity=service['cpu_affinity'])

def main():
    begin=time.perf_counter();freeze=s.verify();execution=read(R/'audit/EXECUTION58.json')
    for name,h in execution['files_sha256'].items():need(digest(R/name)==h,'executed source-record identity '+name)
    clocks={};affinities={}
    for d,T in s.TASKS:
        cl=read(s.OUT/f'process-clocks-d{d}-T{T}.json');need(cl['processes_sequential'] and cl['source_freeze_sha256']==freeze,'controlled cohort')
        affinities[(d,T)]=cl['cpu_affinity']
        for k,rec in enumerate(cl['runs'],1):
            prefix=read(s.OUT/f'checkpoints-d{d}-T{T}'/f'{k:03d}.json')
            need(prefix['runs']==cl['runs'][:k] and prefix['source_freeze_sha256']==freeze,'immutable sequential timing prefix')
            need(digest(s.OUT/f'logs-d{d}-T{T}'/(rec['key']+'.log'))==rec['log_sha256'],'complete process log')
            need(rec['key'] not in clocks,'duplicate service key');clocks[rec['key']]=rec
    expected={s.key(m,d,T,q,z) for d,T in s.TASKS for m in s.MODES for q in s.TARGETS for z in s.REPETITIONS}
    need(set(clocks)==expected,'missing or extra prescribed process clocks')
    need({x.name for x in (s.OUT/'services').iterdir() if x.is_dir()}==expected,'missing or extra service folders')
    rows={key:check_service(s.OUT/'services'/key,clocks[key],freeze) for key in sorted(expected)}
    for row in rows.values():need(row['cpu_affinity']==affinities[(row['d'],row['T'])],'task core binding')
    for d,T in s.TASKS:
        for q in s.TARGETS:
            baseline=rows[s.key('algebraic',d,T,q,0)]
            for mode in s.MODES:
                for rep in s.REPETITIONS:
                    row=rows[s.key(mode,d,T,q,rep)]
                    need(row['status']==baseline['status'],'identical stopping status')
                    need(len(row['stages'])==len(baseline['stages']),'identical stopping stage')
                    for x,y in zip(row['stages'],baseline['stages']):
                        for field in ('policy_sha256','critic_sha256','look_paths','cost','gain','target_contrast','dates','work'):
                            need(x[field]==y[field],'matched prospective transcript '+field)
    inspect_catalogue();inspection=read(R/'audit/INSPECTION59.json')
    need(inspection['services']==36 and inspection['all_recorded_matches'],'descriptive catalogue disagrees with replay')
    result=dict(status='passed',baseline_commit='4b5f1cc3241fe8df103844f225913d91c387795b',controlling_review_commit='adf1256cff9cde365246a3db2dac90c72fda3b13',source_freeze_sha256=freeze,services=len(rows),attained=sum(x['status']=='target_attained' for x in rows.values()),budget_exhausted=sum(x['status']=='budget_exhausted' for x in rows.values()),matched_policy_transcripts=18,all_exact_policy_identities=True,counts=COUNTS,groups=inspection['groups'],rows=inspection['rows'],replayed_services=list(rows.values()),new_training_services=0,new_independent_path_observations=0,original_clocks_replaced=False,audit_seconds=time.perf_counter()-begin,scope='Every frozen file and prospective decision checked; both solvers, unique saved-model certificates and unique declared path streams reintegrated; exact-rational inference validation; no retraining or new observations. Matched timing repetitions are not independent policy-cost observations.')
    save(R/'audit/RESULT_AUDIT59.json',result)
    save(R/'audit/SUMMARY59.json',{k:v for k,v in result.items() if k not in ('rows','replayed_services')})
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','replayed_services','groups')},indent=2))
if __name__=='__main__':main()
