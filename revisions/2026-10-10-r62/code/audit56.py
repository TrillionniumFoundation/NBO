"""Offline evidence replay; no training, fresh samples or scientific retiming."""
from pathlib import Path
from fractions import Fraction as F
from types import SimpleNamespace as NS
import hashlib,json,time,math
import numpy as np
import neural55 as n
import prospective55 as p
import execute_tube55 as e
import tube55,null55,cohort55b
R=Path(__file__).resolve().parents[1]
def read(x):return json.loads(Path(x).read_text())
def digest(x):
    with Path(x).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(x,j):
    x=Path(x);x.parent.mkdir(parents=True,exist_ok=True);x.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def same(a,b,msg):need(np.array_equal(np.asarray(a),np.asarray(b)),msg)
def load_critic(j):
    k=j['kind'];d=j['d']
    if k=='legacy':return n.Critic(k,d,forest=n.s.Model.load(j['model']))
    if k=='extra-trees':
        trees=[]
        for t in j['params']['trees']:
            tr=NS(children_left=np.array(t['left']),children_right=np.array(t['right']),feature=np.array(t['feature']),threshold=np.array(t['threshold']),value=np.array(t['value']))
            trees.append(NS(tree_=tr))
        return n.Critic(k,d,forest=NS(estimators_=trees))
    return n.Critic(k,d,{k:np.asarray(v) for k,v in j['params'].items()})


MOMENT_CACHE={}
def exact_moments(values):
    key=hashlib.sha256(np.asarray(values,dtype=np.float64).tobytes()).hexdigest()
    if key not in MOMENT_CACHE:
        ratios=[float(x).as_integer_ratio() for x in values];bits=max(b.bit_length()-1 for a,b in ratios)
        ints=[a << (bits-(b.bit_length()-1)) for a,b in ratios];N=len(ints);S=sum(ints);SS=sum(x*x for x in ints)
        mean=F(S,N*(1<<bits));second=F(SS,N*(1<<(2*bits)));var=(second-mean*mean)*F(N,N-1)
        MOMENT_CACHE[key]=(mean,second,var)
    return key,MOMENT_CACHE[key]
def verify_ci(lo,hi,A,B,rec):
    aa=n.s.c.enclosure(A)[0];bb=n.s.c.enclosure(B)[1];lo=np.maximum(aa,lo);hi=np.minimum(bb,hi)
    need(np.all(lo<=hi),'supported interval endpoints')
    for values,st in ((lo,rec['lower_moments']),(hi,rec['upper_moments'])):
        key,(mu,sq,var)=exact_moments(values)
        need(key==st['endpoint_sha256'] and len(values)==st['n'],'moment identity')
        need(F(st['mean_lo'])<=mu<=F(st['mean_hi']),'exact sample mean enclosure')
        need(sq<=F(st['second_moment_upper']) and var<=F(st['variance_upper']),'exact sample second moment and variance')
    def rad(st):
        N=st['n'];q=2*F(st['variance_upper'])*p.LOG/N;root=math.sqrt(float(q))
        while F(root)**2<q:root=math.nextafter(root,math.inf)
        return F(root)+F(7*p.LOG,3*(N-1))*(F(bb)-F(aa))
    l=max(A,F(rec['lower_moments']['mean_lo'])-rad(rec['lower_moments']));u=min(B,F(rec['upper_moments']['mean_hi'])+rad(rec['upper_moments']))
    need([str(l),str(u)]==rec['exact'],'rational confidence endpoints')
    same([n.s.c.enclosure(l)[0],n.s.c.enclosure(u)[1]],rec['interval'],'outward displayed endpoints')

def audit_services(cohort,cache):
    root=R/('results55-tube' if cohort=='tube' else 'results55');freeze=e.verify() if cohort=='tube' else cohort55b.verify();clocks={}
    for d,T in p.TASKS:
        j=read(root/f'process-clocks-d{d}-T{T}.json');need(j['processes_sequential'],'sequential driver')
        for i,z in enumerate(j['runs'],1):
            need(z['returncode']==0,'completed process');need(digest(R/z['log'])==z['log_sha256'],'process log')
            snap=read(root/f'process-checkpoints-d{d}-T{T}'/f'{i:03d}.json');need(snap['runs']==j['runs'][:i],'immutable prefix');clocks[z['key']]=z
    rows=[];cells=looks_count=changed=extra_cells=reintegration=0
    for folder in sorted((root/'services').iterdir()):
        svc=read(folder/'service.json');clock=read(folder/'clock.json');key=svc['key'];d=svc['d'];T=svc['T'];target=F(svc['target'])
        need(digest(folder/'service.json')==clock['record_sha256'],'service identity');need(svc['source_freeze_sha256']==freeze,'source freeze')
        need(svc['own_inference'] and svc['own_construction'],'own services')
        for fn,h in svc['files_sha256'].items():need(digest(folder/fn)==h,'saved file: '+str(folder/fn))
        need(sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())==clocks[key]['serialized_bytes'],'serialized bytes')
        prior=None;oldpart=None;bound=[p.old.inference.support(T-t,1)[1] for t in range(T)]+[F(0)];stages=[]
        for k,stage in enumerate(svc['stages']):
            need(read(folder/f'stage{k}.json')==stage,'stage copy');need(stage['stage']==k,'ordered stages')
            samples,N,Q=p.RUNGS[k];need((stage['samples'],stage['leaves'],stage['innovation_bins'])==(samples,N,Q),'resource rung')
            part=n.Partition(d,N);pol=np.zeros((T,N),dtype=np.uint16) if prior is None else prior[:,oldpart.locate(part.centers)]
            need(p.policy_hash(pol,part)==stage['before_policy_sha256'],'inherited incumbent')
            model=read(folder/f'stage{k}-models.json');need(digest(folder/f'stage{k}-models.json')==stage['models_sha256'],'model identity')
            need(model['partition']==part.payload(),'geometry');proposed=np.array(model['proposals'],dtype=np.uint16);final=np.array(model['policy'],dtype=np.uint16)
            cert=folder/f'stage{k}-certificate.npz';need(digest(cert)==stage['certificate_sha256'],'certificate identity')
            ckey=(cohort,p.canonical(model['critics']),p.policy_hash(pol,part),Q)
            if ckey not in cache:
                critics=[load_critic(c) for c in model['critics']];same(n.propose(critics,part),proposed,'proposal from saved weights')
                engine=(tube55.TubeCache if cohort=='tube' else n.Cache)(critics,part,pol,Q);new,report,raw=engine.sweep(proposed)
                for t in range(T):
                    for name in ('err','direct','ranges'):
                        z=getattr(engine,name)[t];raw[f't{t}_{name}_lo']=z.lo;raw[f't{t}_{name}_hi']=z.hi
                cache[ckey]=(new,report,raw);reintegration+=1;print('certificate',cohort,key,k,flush=True)
            new,report,regen=cache[ckey];same(new,final,'recomputed policy');dates=[]
            with np.load(cert) as raw:
                for name,value in regen.items():same(value,raw[name],'recomputed primitive certificate: '+name)
                for t,z in enumerate(stage['dates']):
                    same(report[t]['gap'],z['gap'],'recomputed gap');lo=raw[f't{t}_lower'];hi=raw[f't{t}_upper'];cover=raw[f't{t}_cover']
                    need(lo.shape==hi.shape==(10,N) and cover.shape==(8,N),'complete candidate and cover shapes');need(np.all(lo<=hi),'endpoint order')
                    menu=[part.capindex*j//8 for j in range(9)]+[proposed[t]];U=np.zeros(N);selected=pol[t].copy();common=None
                    for j,ai in enumerate(menu):
                        take=hi[j]<U;U[take]=hi[j,take];selected[take]=ai[take]
                        if j==8:common=selected.copy()
                    L=np.minimum(0,cover.min(axis=0));C=np.maximum(L,np.minimum(0,lo.min(axis=0)))
                    for nm,val in [('U',U),('L',L),('C',C),('selected',selected)]:same(val,raw[f't{t}_{nm}'],'gate '+nm)
                    same(selected,final[t],'deployed decision');need(np.all(selected<=part.capindex) and np.all(U<=0) and np.all(L<=C) and np.all(C<=U),'safe selection')
                    need(float((n.I.point(U)-n.I.point(L)).hi.max())==z['gap'],'gap')
                    need(float((n.I.point(U)-n.I.point(C)).hi.max())==z['candidate_enclosure_component'],'enclosure decomposition')
                    need(float((n.I.point(C)-n.I.point(L)).hi.max())==z['continuous_cover_component'],'cover decomposition')
                    nc=int(np.count_nonzero(selected!=pol[t]));specific=int(np.count_nonzero(common!=selected));need(nc==z['changed'],'change count')
                    dates.append(dict(z,proposal_attributable_changes=specific));cells+=N;changed+=nc;extra_cells+=specific
            bound=[n.BETA*bound[t+1]+F(stage['dates'][t]['gap']) for t in range(T)]+[F(0)];need(list(map(str,bound))==stage['all_state_gap_exact'],'exact recurrence')
            previous=0;old_arrays=None;last=None
            for ix,fn in enumerate(stage['look_files']):
                look=read(folder/fn);nn=look['paths'];need(nn==p.LOOKS[ix],'declared cumulative look');rawpath=folder/f'stage{k}-look{nn}.npz';need(digest(rawpath)==look['raw_sha256'],'path digest')
                with np.load(rawpath) as z:
                    values={x:z[x].copy() for x in z.files};need(set(values)=={'policy_lo','policy_hi','zero_lo','zero_hi'},'endpoint fields');need(all(v.shape==(nn,) for v in values.values()),'sample count')
                    if old_arrays is not None:
                        for name in values:same(values[name][:previous],old_arrays[name],'cumulative prefix')
                    value=n.I(values['policy_lo'],values['policy_hi']);zero=n.I(values['zero_lo'],values['zero_hi']);H=p.old.inference.support(T,1)[1];delta=value-n.s.c.rat_i(target)*zero;gain=zero-value
                    for name,band,A,B in [('cost',value,F(0),H),('target_contrast',delta,-target*H,H),('gain',gain,-H,H)]:verify_ci(band.lo,band.hi,A,B,look[name])
                    old_arrays=values
                passed=F(look['target_contrast']['exact'][1])<=0;rejected=F(look['target_contrast']['exact'][0])>0;need(passed==look['crossed'],'stop inequality')
                if passed or rejected:need(ix==len(stage['look_files'])-1,'no later look')
                previous=nn;last=look;looks_count+=1
            need(last is not None and stage['target_attained']==last['crossed'],'stage conclusion')
            if last['crossed']:need(k==len(svc['stages'])-1,'no later construction')
            else:need(F(last['target_contrast']['exact'][0])>0 or last['paths']==p.LOOKS[-1],'valid stage end')
            stages.append(dict(stage=k,leaves=N,dates=dates,gap=stage['all_state_gap_upper'][0],paths=last['paths'],looks=len(stage['look_files']),cost=last['cost']['interval'],gain=last['gain']['interval'],target_contrast=last['target_contrast']['interval'],policy_sha256=stage['after_policy_sha256'],construction_seconds=stage['construction_seconds'],cache_seconds=stage['cache_seconds'],gate_seconds=stage['gate_seconds'],inference_seconds=last['seconds_through_raw'],membership_comparisons=stage['verification_membership_comparisons'],critic_evaluated_rows=stage['critic_evaluated_rows'],tube_work=stage.get('tube_work',{})))
            prior=final;oldpart=part
        need(svc['status']==('target_attained' if last['crossed'] else 'budget_exhausted'),'service stop')
        if not last['crossed']:need(len(stages)==len(p.RUNGS),'full budget exhausted')
        need(svc['final_policy_sha256']==stages[-1]['policy_sha256'],'final identity')
        rows.append(dict(key=key,cohort=cohort,d=d,T=T,kind=svc['kind'],target=svc['target'],repeat=svc['repeat'],status=svc['status'],stages=stages,whole_process_seconds=clocks[key]['whole_process_seconds'],service_seconds=clock['seconds_through_record_fsync'],serialized_bytes=clocks[key]['serialized_bytes'],peak_rss_kib=svc['peak_rss_kib'],affinity=svc['cpu_affinity'],governor=svc['governor'],frequency_controlled=svc['frequency_controlled']))
    need(len(rows)==66,'66-service cohort')
    return dict(services=rows,service_count=len(rows),attained=sum(x['status']=='target_attained' for x in rows),exhausted=sum(x['status']=='budget_exhausted' for x in rows),checked_cell_decisions=cells,checked_looks=looks_count,changed_cell_dates=changed,proposal_attributable_changes=extra_cells,unique_certificate_reintegrations=reintegration)

def audit_null():
    root=R/'results55/learned-null';j=read(root/'summary.json');need(j['source_freeze_sha256']==p.verify(),'null freeze');changes=harms=0;fits={}
    for fit in j['fits']:
        key=fit['key'];f=root/(key+'-data.npz');need(digest(f)==fit['data_sha256'],'null data hash')
        with np.load(f) as a:
            box=n.I(np.array(fit['box_lo']),np.array(fit['box_hi']));rad=F(fit['radius_exact']);same(a['direction'],fit['direction'],'direction')
            N=len(a['validation_exposures']);need((rad-F(1,2**40))**2>=F(14,8*N),'confidence radius')
            for jj in range(fit['dimension']):
                _,(mu,sq,var)=exact_moments(a['validation_exposures'][:,jj])
                need(F(float(box.lo[jj]))<=max(F(0),mu-rad) and F(float(box.hi[jj]))>=min(F(1),mu+rad),'exact-mean confidence box')
            v=a['direction'];coeff=n.dot(n.I(box.lo[None,:],box.hi[None,:]),v);same(max(abs(coeff.lo[0]),abs(coeff.hi[0])),fit['robust_direction_exposure_upper'],'projection support')
        fits[key]=fit
    for z in j['cases']:
        fit=fits[z['key']];part=n.Partition(fit['dimension'],64);cap=part.capindex;base=cap*3//4;f=root/(z['key']+f'-M{z["amplitude"]}.npz');need(digest(f)==z['raw_sha256'],'null record hash')
        with np.load(f) as a:
            chosen=base.copy();wrong=base.copy();U=np.zeros(64);W=U.copy();trueU=U.copy();trueL=U.copy()
            for k in range(9):
                ai=cap*k//8;hi=a[f'j{k}_corrected_hi'];naive=a[f'j{k}_naive_hi'];take=hi<U;bad=naive<W
                chosen[take]=ai[take];U[take]=hi[take];trueU[take]=a[f'j{k}_true_hi'][take];wrong[bad]=ai[bad];W[bad]=naive[bad];trueL[bad]=a[f'j{k}_true_lo'][bad]
                need(np.all(a[f'j{k}_true_lo']<=a[f'j{k}_true_hi']) and np.all(a[f'j{k}_allowance_hi']>=0),'null interval order')
            same(chosen,a['selected'],'null gate');same(wrong,a['false_null_selected'],'plug-in gate');same(trueU,a['selected_true_hi'],'true postcheck');same(trueL,a['false_null_true_lo'],'harm postcheck')
            if fit['true_exposure_contained']:need(np.all(trueU<=0),'covered corrected safety')
            c=int(np.count_nonzero(chosen!=base));h=int(np.count_nonzero((wrong!=base)&(trueL>0)));need(c==z['changed'] and h==z['harmful_false_null'],'null totals');changes+=c;harms+=h
    return dict(validation_boxes=len(fits),covered_boxes=sum(x['true_exposure_contained'] for x in fits.values()),cases=len(j['cases']),cell_cases=j['cell_cases'],safe_changes=changes,certified_harmful_plugin_cells=harms,fits=list(fits.values()),case_records=j['cases'],scope=j['model'])

def structural_checks(primary,tube):
    geometry=[];identities=[]
    for d,T in p.TASKS:
        for _,N,_ in p.RUNGS:
            part=n.Partition(d,N)
            cuts=[len(set(part.lo[:,j])|set(part.hi[:,j]))-1 for j in range(d)]
            product=math.prod(cuts);need(product>N,'genuinely non-tensor leaf partition')
            geometry.append(dict(d=d,leaves=N,cartesian_refinement_cells=product))
    for name,cohort in [('primary',primary),('tube',tube)]:
        for d,T in p.TASKS:
            for q in ('9/10','49/50'):
                rows=[z for z in cohort['services'] if z['d']==d and z['target']==q and z['repeat']==0]
                expected=[z for z in rows if not (name=='tube' and d==2 and z['kind']=='compiled-witness')]
                sig=[tuple(t['policy_sha256'] for t in z['stages']) for z in expected]
                need(len(set(sig))==1,'cross-generator policy identity')
                identities.append(dict(cohort=name,d=d,target=q,identical_generators=[z['kind'] for z in expected],stage_identities=list(sig[0])))
    return dict(non_tensor_partitions=geometry,policy_identity_groups=identities)

def main():
    start=time.perf_counter();cache={};primary=audit_services('primary',cache);save(R/'audit/PRIMARY_REPLAY56.json',primary);tube=audit_services('tube',cache);save(R/'audit/TUBE_REPLAY56.json',tube);null=audit_null();groups=[]
    for cohort in (primary,tube):
        rows=cohort['services']
        for key in sorted(set((z['d'],z['T'],z['kind'],z['target']) for z in rows)):
            rr=[x for x in rows if (x['d'],x['T'],x['kind'],x['target'])==key];need(len(rr)==3,'three repetitions')
            sig=[[(s['policy_sha256'],s['cost'],s['gain'],s['target_contrast'],s['paths']) for s in x['stages']] for x in rr];need(sig[0]==sig[1]==sig[2],'repetition identity')
            v=sorted(x['whole_process_seconds'] for x in rr);r0=next(x for x in rr if x['repeat']==0)
            groups.append(dict(cohort=r0['cohort'],d=key[0],T=key[1],kind=key[2],target=key[3],status=r0['status'],clock_min=v[0],clock_median=v[1],clock_max=v[2],final=r0['stages'][-1],serialized_bytes=r0['serialized_bytes'],peak_rss_kib=max(x['peak_rss_kib'] for x in rr)))
    result=dict(status='passed',review_commit='adf1256cff9cde365246a3db2dac90c72fda3b13',evidence_commit='7f4de488134e93b6cfb5dd95a3e6d7e14b45ac2a',primary=primary,tube=tube,learned_null=null,grouped=groups,structural_checks=structural_checks(primary,tube),source_freezes=[p.verify(),e.verify()],replay_seconds=time.perf_counter()-start,new_scientific_services=0,new_cost_samples=0,scope='Saved trained models regenerate proposals and all unique full-domain certificates; all saved decisions, finite-stop paths and numerical inference replayed. No retraining, fresh observations or retiming of scientific services.')
    save(R/'audit/RESULT_AUDIT56.json',result);print(json.dumps(dict(status='passed',seconds=result['replay_seconds'],primary=primary['attained'],tube=tube['attained'],unique_certificates=len(cache),primary_proposal_changes=primary['proposal_attributable_changes'],tube_proposal_changes=tube['proposal_attributable_changes']),indent=2))
if __name__=='__main__':main()
