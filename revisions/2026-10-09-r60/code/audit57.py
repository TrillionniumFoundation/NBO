"""Reintegrate saved R57 witnesses, certificates, stopping paths and comparisons.

No critic is retrained. Replaying an already declared pseudorandom stream is
not a fresh statistical observation. Original clocks are never replaced.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time,statistics
import numpy as np
import action57 as a
import study57 as s
import audit56 as old
n=a.n;p=s.p;R=s.R
CACHE={};REPLAYED=0

def need(x,msg):
    if not x:raise AssertionError(msg)
def equal(x,y,msg):need(np.array_equal(np.asarray(x),np.asarray(y)),msg)
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def replay_stopping(policy,part,T,target,seed,stage,folder,look_paths):
    rng=np.random.Generator(np.random.PCG64(s.seed_for(f'NBO-R57-STOP-d{part.d}-T{T}-q{target}-seed{seed}-stage{stage}')));stream=hashlib.sha256();lo=[];hi=[];zl=[];zh=[];previous=0;zero=np.zeros_like(policy);H=p.old.inference.support(T,1)[1];records=[]
    for ix,look in enumerate(look_paths):
        need(look==s.LOOKS[ix],'nonprospective inference look')
        for offset in range(previous,look,2048):
            bins,x,z=s.paths(rng,min(2048,look-offset),part.d,T);stream.update(bins.tobytes());val=n.score(policy,part,x,z);base=n.score(zero,part,x,z)
            lo.extend(val.lo);hi.extend(val.hi);zl.extend(base.lo);zh.extend(base.hi)
        f=folder/f'stage{stage}-look{look}.npz';rec=s.read(folder/f'stage{stage}-look{look}.json');need(p.old.digest(f)==rec['raw_sha256'],'stopping endpoint identity')
        with np.load(f) as z:
            for name,values in [('policy_lo',lo),('policy_hi',hi),('zero_lo',zl),('zero_hi',zh)]:equal(z[name],values,'full path reintegration '+name)
        val=n.I(np.array(lo),np.array(hi));base=n.I(np.array(zl),np.array(zh));dif=val-n.s.c.rat_i(target)*base;gain=base-val
        old.verify_ci(val.lo,val.hi,F(0),H,rec['cost']);old.verify_ci(dif.lo,dif.hi,-target*H,H,rec['target_contrast']);old.verify_ci(gain.lo,gain.hi,-H,H,rec['gain'])
        need(rec['stream_sha256']==stream.hexdigest(),'stopping stream hash');met=F(rec['target_contrast']['exact'][1])<=0;lowerpositive=F(rec['target_contrast']['exact'][0])>0
        need(rec['crossed']==met,'stopping classification')
        if ix<len(look_paths)-1:need(not met and not lowerpositive,'look executed after stopping rule')
        else:need(met or lowerpositive or look==s.LOOKS[-1],'premature inference stop')
        records.append(rec);previous=look
    return records

def service(folder,clock):
    global REPLAYED
    svc=s.read(folder/'service.json');need(svc['source_freeze_sha256']==s.verify(),'service freeze');need(svc['key']==folder.name,'service identity')
    need(p.old.digest(folder/'service.json')==s.read(folder/'clock.json')['record_sha256'],'service durable identity')
    for name,h in svc['files_sha256'].items():need(p.old.digest(folder/name)==h,'file identity '+name)
    need(clock['returncode']==0,'failed production service');need(sum(x.stat().st_size for x in folder.rglob('*') if x.is_file())==clock['serialized_bytes'],'full serialized bytes')
    d=svc['d'];T=svc['T'];mode=svc['mode'];target=F(svc['target']);seed=svc['seed'];stages=[];cells=looks=paths=0
    for stage,rec in enumerate(svc['stages']):
        need(s.read(folder/f'stage{stage}.json')==rec,'stage identity');Nrows,N,q=s.RUNGS[stage];need((rec['samples'],rec['leaves'],rec['innovation_bins'])==(Nrows,N,q),'resource rung')
        m=s.read(folder/f'stage{stage}-models.json');need(p.old.digest(folder/f'stage{stage}-models.json')==rec['models_sha256'],'model identity');part=n.Partition(d,N);need(m['partition']==part.payload(),'non-tensor geometry')
        identity=(mode,T,N,q,p.canonical(m['critics']))
        if identity not in CACHE:
            critics=[old.load_critic(c) for c in m['critics']]
            grid,exact,witnesses=a.proposals(critics,part,mode);equal(grid,m['grid'],'menu proposal reintegration');equal(exact,m['exact'],'exact proposal reintegration')
            need(len(witnesses)==len(m['witnesses']),'witness record count')
            for w,recorded in zip(witnesses,m['witnesses']):
                for field in ('index','objective_exact','grid_regret_exact','date','leaf','common_terminal','pieces','isolated_roots'):need(w[field]==recorded[field],'algebraic witness '+field)
            verifier=a.ReferenceVerifier(part,T,q);pol,dates,raw=verifier.sweep(grid,exact if mode in ('relu-exact','quadratic-exact') else None)
            CACHE[identity]=(pol,dates,raw,witnesses,verifier.work);REPLAYED+=1
        pol,dates,raw,witnesses,work=CACHE[identity];equal(pol,m['policy'],'deployed policy');need(dates==rec['dates'],'datewise numerical ledger');need(work==rec['work'],'machine-independent work')
        f=folder/f'stage{stage}-certificate.npz';need(p.old.digest(f)==rec['certificate_sha256'],'certificate identity')
        with np.load(f) as z:
            need(set(z.files)==set(raw),'complete certificate fields')
            for name,value in raw.items():equal(z[name],value,'certificate reintegration '+name)
        need(p.policy_hash(pol,part)==rec['policy_sha256'],'full policy identity')
        loss=[min(p.old.inference.support(T-t,1)[1],(n.BETA*p.old.inference.support(T-t-1,1)[1] if t<T-1 else F(0))+F(dates[t]['gap_upper'])) for t in range(T)]
        need(list(map(str,loss))==rec['all_state_policy_loss_bound_exact'],'one-sweep policy loss, not greedy-gap substitution')
        lks=replay_stopping(pol,part,T,target,seed,stage,folder,rec['look_paths']);met=lks[-1]['crossed'];need(met==rec['target_attained'],'target classification')
        if met:need(stage==len(svc['stages'])-1,'attempt executed after success')
        stages.append(dict(stage=stage,leaves=N,critic_sha256=p.canonical(m['critics']),policy_sha256=rec['policy_sha256'],dates=dates,cost=lks[-1]['cost']['interval'],gain=lks[-1]['gain']['interval'],target_contrast=lks[-1]['target_contrast']['interval'],paths=rec['look_paths'][-1],grid_regret_positive=rec['nonterminal_grid_regret_positive'],root_isolations=rec['root_isolations'],exact_candidate_evaluations=rec['exact_candidate_evaluations'],fit_seconds=rec['construction_seconds'],search_seconds=rec['action_search_seconds'],verification_seconds=rec['verification_seconds'],inference_seconds=lks[-1]['seconds_through_raw'],policy_loss_bound_exact=rec['all_state_policy_loss_bound_exact']))
        cells+=T*N;looks+=len(lks);paths+=rec['look_paths'][-1]
    need((svc['status']=='target_attained')==met,'service success classification')
    if not met:need(len(stages)==len(s.RUNGS),'unexplained early budget exhaustion')
    need(svc['final_policy_sha256']==stages[-1]['policy_sha256'],'returned policy')
    return dict(key=svc['key'],d=d,T=T,mode=mode,target=str(target),seed=seed,status=svc['status'],stages=stages,whole_process_seconds=clock['whole_process_seconds'],serialized_bytes=clock['serialized_bytes'],peak_rss_kib=svc['peak_rss_kib'],cell_decisions=cells,inference_looks=looks,unique_stop_path_rows=paths)

def paired(folder):
    rec=s.read(folder/'paired.json');d=rec['d'];T=rec['T'];target=F(rec['target']);seed=rec['seed'];f=folder/'endpoints.npz';need(p.old.digest(f)==rec['raw_sha256'],'paired raw identity');need(rec['source_freeze_sha256']==s.verify(),'paired source')
    actors=[];identities=[]
    for mode in s.MODES:
        src=s.OUT/'services'/s.key(mode,d,T,target,seed);svc=s.read(src/'service.json');st=svc['stages'][-1];m=s.read(src/f'stage{st["stage"]}-models.json');part=n.Partition(d,st['leaves']);pol=np.array(m['policy'],dtype=np.uint16);actors.append((part,pol));identities.append(p.policy_hash(pol,part))
    need(identities==rec['policy_sha256'],'paired returned-policy identity')
    rng=np.random.Generator(np.random.PCG64(s.seed_for(f'NBO-R57-INDEPENDENT-PAIRS-d{d}-T{T}-q{target}-seed{seed}')));stream=hashlib.sha256();H=p.old.inference.support(T,1)[1]
    with np.load(f) as data:
        lo=data['lower'];hi=data['upper'];need(lo.shape==hi.shape==(len(s.MODES),65536),'paired data shape')
        for off in range(0,65536,2048):
            bins,x,z=s.paths(rng,2048,d,T);stream.update(bins.tobytes())
            for i,(part,pol) in enumerate(actors):
                val=n.score(pol,part,x,z);equal(lo[i,off:off+2048],val.lo,'paired lower reintegration');equal(hi[i,off:off+2048],val.hi,'paired upper reintegration')
        for i in (0,1,3,4):
            c=rec['contrasts'][s.MODES[i]]
            if c.get('identity'):need(identities[2]==identities[i] and c['exact']==['0','0'],'exact policy equality')
            else:
                v=n.I(lo[2],hi[2])-n.I(lo[i],hi[i]);old.verify_ci(v.lo,v.hi,-H,H,c)
    need(stream.hexdigest()==rec['stream_sha256'],'paired inference stream')
    return dict(d=d,T=T,target=str(target),seed=seed,contrasts={k:dict(interval=v['interval'],identity=v.get('identity',False),classification='identity' if v.get('identity') else 'relu_more_costly' if F(v['exact'][0])>0 else 'relu_less_costly' if F(v['exact'][1])<0 else 'unresolved') for k,v in rec['contrasts'].items()},seconds_through_endpoints=rec['seconds_through_endpoints'])

def main():
    start=time.perf_counter();fz=s.verify();execution=s.read(R/'audit/EXECUTION57.json');need(execution['status']=='success' and execution['service_records']==90 and execution['paired_sets']==18,'complete production cohort')
    clocks={}
    for d,T in s.TASKS:
        cl=s.read(s.OUT/f'process-clocks-d{d}-T{T}.json');need(cl['processes_sequential'],'sequential task process control')
        for k,rec in enumerate(cl['runs'],1):
            need(s.read(s.OUT/f'checkpoints-d{d}-T{T}'/f'{k:03d}.json')['runs']==cl['runs'][:k],'immutable timing prefix')
            need(p.old.digest(s.OUT/f'logs-d{d}-T{T}'/(rec['key']+'.log'))==rec['log_sha256'],'process log identity');clocks[rec['key']]=rec
    expected={s.key(m,d,T,q,z) for d,T in s.TASKS for m in s.MODES for q in s.TARGETS for z in s.SEEDS}
    need(set(clocks)==expected,'complete prescribed target services')
    rows=[service(s.OUT/'services'/k,clocks[k]) for k in sorted(expected)];pairs=[paired(x.parent) for x in sorted((s.OUT/'paired').glob('*/paired.json'))]
    for d,T in s.TASKS:
        neural=[r for r in rows if r['d']==d and r['mode']=='relu-menu' and r['target']=='9/10'];need(len({r['stages'][0]['critic_sha256'] for r in neural})==3,'distinct fitted neural objects')
        for seed in s.SEEDS:
            for q in s.TARGETS:
                menu=next(r for r in rows if r['key']==s.key('relu-menu',d,T,q,seed));exact=next(r for r in rows if r['key']==s.key('relu-exact',d,T,q,seed))
                for m,e in zip(menu['stages'],exact['stages']):need(m['critic_sha256']==e['critic_sha256'],'matched fit for action-search ablation')
    counts={name:sum(v['classification']==name for r in pairs for v in r['contrasts'].values()) for name in ('identity','relu_more_costly','relu_less_costly','unresolved')}
    summary=dict(status='passed',source_freeze_sha256=fz,services=len(rows),attained=sum(r['status']=='target_attained' for r in rows),budget_exhausted=sum(r['status']!='target_attained' for r in rows),unique_certificate_and_solver_reintegrations=REPLAYED,checked_cell_decisions=sum(r['cell_decisions'] for r in rows),checked_stopping_looks=sum(r['inference_looks'] for r in rows),regenerated_stopping_path_rows=sum(r['unique_stop_path_rows'] for r in rows),paired_sets=len(pairs),paired_path_rows=len(pairs)*65536,paired_classifications=counts,
        neural_extra_witness_cell_decisions=sum(z['extra_witness_changes'] for r in rows if r['mode']=='relu-exact' for st in r['stages'] for z in st['dates']),neural_positive_center_regrets=sum(st['grid_regret_positive'] for r in rows if r['mode']=='relu-exact' for st in r['stages']),independent_seed_identifiers=list(s.SEEDS),rows=rows,paired=pairs,audit_seconds=time.perf_counter()-start,scope='Same frozen model and source reintegration of algebraic witnesses, all certificates and all declared interval paths; exact rational stored-moment checks. No retraining, no new independent observations and no replacement of original clocks.')
    save(R/'audit/RESULT_AUDIT57.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','paired')},indent=2))
if __name__=='__main__':main()
