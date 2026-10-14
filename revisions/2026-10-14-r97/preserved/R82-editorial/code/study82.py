"""Deterministic actionwise cost transfer for frozen optimization sublevels.

Every admissible switch is integrated on every declared dyadic rung with two
independent arithmetic implementations. No fitting or random sampling occurs.
The complete records bind integer sums and all raw endpoint stream digests.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse,hashlib,itertools,json,os,platform,resource,subprocess,time
import numpy as np
import paired82 as production
import independent82 as independent
R=Path(__file__).resolve().parents[1]
H=F(21097,4096);S=independent.S
TOLERANCES=(F(0),F(1,65536),F(1,4096))
RUNGS=((2,8),(4,16),(8,32),(16,64))
MODELS=tuple((n,k) for n in (8,16) for k in ('relu','bernstein'))
BASE='c411bfb2badac2981f001f4c84d99c8c3c306c5e'

def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def encode(v):
    if isinstance(v,F):return str(v)
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,dict):return {str(k):encode(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [encode(x) for x in v]
    return v

def save(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(encode(v),sort_keys=True,indent=2)+'\n')
def need(condition,message):
    if not condition:raise AssertionError(message)
def environment():
    frequencies={}
    for p in sorted(Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq/scaling_governor'))[:8]:
        for name in ('scaling_governor','scaling_cur_freq','scaling_min_freq','scaling_max_freq'):
            q=p.parent/name
            if q.exists():frequencies[str(q)]=q.read_text().strip()
    return dict(python=platform.python_version(),numpy=np.__version__,machine=platform.machine(),
        affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
        frequency=frequencies,frequency_locked=False)

def inputs(n,kind):
    path=R/'results80/construction'/f'{kind}-n{n}/service.json';service=read(path)
    barrier=R/'results80/barriers'/f'{kind}-n{n}.json';raw=read(barrier)
    need(sha(path)==raw['summary']['source_sha256'],'Barrier source identity')
    U=F(service['stages'][1]['attained']['objective'])
    actions=np.array([int(F(x)*4096) for x in service['stages'][1]['data']['actions']],dtype=np.int64).reshape(n,n)
    reference=tuple(map(F,service['stages'][0]['data']['actions']))
    pairs=[];position=0
    for i,j in itertools.product(range(n),repeat=2):
        cap=(4096*(2*n+i+j))//(16*n)
        need(0<=actions[i,j]<=cap,'Terminal robust feasibility')
        a=reference[i*n+j];need((a*4096).denominator==1,'Action quantum')
        menu=tuple(F((cap*k)//32,4096) for k in range(33))
        need(a in menu and len(set(menu))==33,'Complete distinct robust menu')
        for b in menu:
            if b==a:continue
            row=raw['records'][position]
            need(row['cell']==[i,j] and F(row['reference'])==a and F(row['competitor'])==b,'Ordered full switch catalogue')
            D=F(row['lower']);position+=1
            if D<=U+max(TOLERANCES):
                pairs.append(dict(cell=[i,j],reference_index=int(a*4096),alternative_index=int(b*4096),
                    switch_lower=D,enabled_tolerances=[str(e) for e in TOLERANCES if D<=U+e]))
    need(position==len(raw['records'])==32*n*n,'All switches accounted')
    return U,actions,pairs,dict(construction_sha256=sha(path),barrier_sha256=sha(barrier),all_switches=position)

def freeze():
    files={}
    for n in ('code/paired82.py','code/independent82.py','code/study82.py','code/tests82.py','PROTOCOL82.md'):
        files[n]=sha(R/n)
    for n,k in MODELS:
        for p in (R/'results80/construction'/f'{k}-n{n}/service.json',R/'results80/barriers'/f'{k}-n{n}.json'):
            files[str(p.relative_to(R))]=sha(p)
    files['results80/cost/summary.json']=sha(R/'results80/cost/summary.json')
    try:head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:head=None
    p=R/'SOURCE_FREEZE82.json'
    need(not p.exists(),'Do not overwrite a scientific source freeze')
    save(p,dict(baseline_commit=BASE,source_commit=head,files=files,rungs=RUNGS,tolerances=TOLERANCES,
        prospective_random_sample=False,development_pilots_disclosed=True,
        scope='Frozen deterministic exhaustive refinement, not a new IID economic experiment.'))

def verify_freeze():
    f=read(R/'SOURCE_FREEZE82.json')
    need(f['rungs']==encode(RUNGS) and f['tolerances']==encode(TOLERANCES),'Frozen design')
    for p,h in f['files'].items():need(sha(R/p)==h,'Frozen input changed '+p)
    return f

def integral(cell,n,r,q,b,a,actor,integer_actor):
    x=production.evaluate(cell,n,r,q,b,a,actor)
    z=independent.evaluate(cell,n,r,q,b,a,integer_actor)
    fl=np.floor(x.lo*S).astype(np.int64);fu=np.ceil(x.hi*S).astype(np.int64)
    zl=np.asarray(z.lo,dtype=np.int64);zu=np.asarray(z.hi,dtype=np.int64)
    need(all(v.shape==(r*r*q,) for v in (fl,fu,zl,zu)),'Complete dyadic array shape')
    bad=(fl>zu)|(zl>fu)
    if np.any(bad):
        save(R/'audit/DISAGREEMENT82.json',dict(cell=cell,n=n,r=r,q=q,b=b,a=a,rows=np.flatnonzero(bad).tolist()))
        raise AssertionError('Independent paired enclosures disjoint')
    L=np.maximum(-int(H*S),np.minimum(fl,zl));U=np.minimum(int(H*S),np.maximum(fu,zu))
    need(np.all(L<=U),'Hull and proved support consistent')
    checks=0
    for row in np.unique(np.linspace(0,len(L)-1,min(4,len(L)),dtype=np.int64)):
        v=independent.exact_point(cell,n,r,q,int(row),b,a,integer_actor.a)
        need(F(int(fl[row]),S)<=v<=F(int(fu[row]),S),'Exact path outside binary64 pair enclosure')
        need(F(int(zl[row]),S)<=v<=F(int(zu[row]),S),'Exact path outside integer pair enclosure')
        checks+=1
    sl,su=sum(map(int,L)),sum(map(int,U));count=len(L)
    digest=hashlib.sha256()
    for a0 in (fl,fu,zl,zu):digest.update(np.asarray(a0,dtype='<i8').tobytes())
    return dict(lower=F(sl,count*S),upper=F(su,count*S),sum_lower=sl,sum_upper=su,
        boxes=count,exact_midpoint_checks=checks,all_endpoint_stream_sha256=digest.hexdigest(),
        maximum_arithmetic_endpoint_disagreement_units=max(int(np.max(np.abs(fl-zl))),int(np.max(np.abs(fu-zu)))))

def class_bounds(n,pairs,intervals):
    out=[]
    for eps in TOLERANCES:
        lows=[F(0)]*(n*n);highs=lows.copy();uncertain=set();possible=0
        for row,box in zip(pairs,intervals):
            if str(eps) not in row['enabled_tolerances']:continue
            i,j=row['cell'];cell=i*n+j;lo,hi=map(F,box)
            need(-H<=lo<=hi<=H,'Per-action support')
            lows[cell]=min(lows[cell],lo);highs[cell]=max(highs[cell],hi)
            uncertain.add(cell);possible+=1
        l=sum(lows,F(0))/(n*n);u=sum(highs,F(0))/(n*n);coarse=H*F(len(uncertain),n*n)
        need(-coarse<=l<=0<=u<=coarse,'Directed refinement dominates binary radius')
        out.append(dict(extra_objective=eps,lower=l,upper=u,coarse_radius=coarse,
            unresolved_cells=len(uncertain),possible_alternatives=possible,
            cell_lowers=lows,cell_uppers=highs))
    return out

def model(n,kind):
    U,actions,pairs,meta=inputs(n,kind)
    actor=production.Actor(actions);integer_actor=independent.Actor(actions)
    accumulated=[(-H,H) for p in pairs];tiers=[];work=[]
    for r,q in RUNGS:
        start=time.perf_counter();before=(actor.queries,actor.ambiguous,integer_actor.queries,integer_actor.ambiguous)
        records=[]
        for i,row in enumerate(pairs):
            item=integral(tuple(row['cell']),n,r,q,row['alternative_index'],row['reference_index'],actor,integer_actor)
            lo,hi=accumulated[i];lo=max(lo,item['lower']);hi=min(hi,item['upper'])
            need(lo<=hi,'Independent refinement intersection empty')
            accumulated[i]=(lo,hi);records.append(item)
        bounds=class_bounds(n,pairs,accumulated)
        tiers.append(dict(state_subdivisions=r,shock_bins=q,per_action=records,accumulated_intervals=accumulated.copy(),sublevels=bounds))
        after=(actor.queries,actor.ambiguous,integer_actor.queries,integer_actor.ambiguous)
        work.append(dict(state_subdivisions=r,shock_bins=q,seconds=time.perf_counter()-start,
            binary64_actor_queries=after[0]-before[0],binary64_ambiguous_boxes=after[1]-before[1],
            integer_actor_queries=after[2]-before[2],integer_ambiguous_boxes=after[3]-before[3]))
        print(json.dumps(encode(dict(model=f'{kind}-n{n}',r=r,q=q,boxes=len(pairs)*r*r*q,
            sublevels=[{k:x[k] for k in ('extra_objective','lower','upper','coarse_radius')} for x in bounds],seconds=work[-1]['seconds']))),flush=True)
    return dict(name=f'calibrated-{kind}-n{n}',n=n,basis=kind,reference_objective=U,source=meta,
        admitted_switches=pairs,tiers=tiers),work

def pair_band(contrasts,a,b):
    key=a+'-minus-'+b
    if key in contrasts:return tuple(map(F,contrasts[key]['interval_exact']))
    lo,hi=map(F,contrasts[b+'-minus-'+a]['interval_exact']);return -hi,-lo

def transfer(services):
    report=read(R/'results80/cost/summary.json');contrasts=report['inference']['conditional']['contrasts']
    names={s['name']:s for s in services};rows=[]
    for first,second in itertools.combinations(names,2):
        l,u=pair_band(contrasts,first,second)
        for tier in range(len(RUNGS)):
            for e,eps in enumerate(TOLERANCES):
                a=names[first]['tiers'][tier]['sublevels'][e];b=names[second]['tiers'][tier]['sublevels'][e]
                L=l+F(a['lower'])-F(b['upper']);U=u+F(a['upper'])-F(b['lower'])
                rows.append(dict(first=first,second=second,rung=tier,extra_objective=eps,
                    attained_interval=[l,u],optimizer_sublevel_interval=[L,U],
                    sign='positive' if L>0 else 'negative' if U<0 else 'unresolved',
                    equivalence_at_1_over_256=(-F(1,256)<L and U<F(1,256)),
                    coarse_interval=[l-F(a['coarse_radius'])-F(b['coarse_radius']),u+F(a['coarse_radius'])+F(b['coarse_radius'])]))
    own=[]
    for s in services:
        name=s['name'];legacy=name.removeprefix('calibrated-')
        for reference in ('zero',legacy):
            l,u=pair_band(contrasts,reference,name)
            for e,eps in enumerate(TOLERANCES):
                a=s['tiers'][-1]['sublevels'][e]
                own.append(dict(reference=reference,class_name=name,extra_objective=eps,
                    reference_minus_class=[l-F(a['upper']),u-F(a['lower'])]))
    return dict(pairwise=rows,own_controller=own,statistical_family='Existing R80 preallocated joint event; no new failure probability or observations',
        original_cost_summary_sha256=sha(R/'results80/cost/summary.json'))

def main(mode):
    if mode=='freeze':freeze();return
    f=verify_freeze();folder=R/'results82';start=time.perf_counter();before=environment()
    if mode=='execute':need(not folder.exists(),'Execution exists: preserve before any changed attempt');folder.mkdir()
    elif mode!='replay':raise ValueError(mode)
    services=[];work={}
    for n,k in MODELS:
        record,times=model(n,k);services.append(record);work[record['name']]=times
        name=k+f'-n{n}.json'
        if mode=='execute':save(folder/name,record)
        else:need(encode(record)==read(folder/name),'Full paired replay differs '+name)
    movement=transfer(services)
    if mode=='execute':save(folder/'transfer.json',movement)
    else:need(encode(movement)==read(folder/'transfer.json'),'Class cost transfer differs')
    boxes=sum(x['boxes'] for s in services for tier in s['tiers'] for x in tier['per_action'])
    checks=sum(x['exact_midpoint_checks'] for s in services for tier in s['tiers'] for x in tier['per_action'])
    common=dict(status='passed',source_freeze_sha256=sha(R/'SOURCE_FREEZE82.json'),model_count=len(services),
        original_action_switches=sum(s['source']['all_switches'] for s in services),
        integrated_switches=sum(len(s['admitted_switches']) for s in services),
        paired_boxes_per_implementation=boxes,exact_rational_midpoints=checks,
        complete_sublevel_records=len(services)*len(TOLERANCES)*len(RUNGS),new_independent_rows=0,new_fit_attempts=0,
        original_cost_summary_sha256=sha(R/'results80/cost/summary.json'),
        scientific_scope='Deterministic exhaustive actionwise integration in the original two-date law; fixed terminal actor and robust action menu, all relevant R80 dual alternatives retained. Not jointly attainable worst-case coefficients, new statistical sampling, trained vector comparison or large-tree replay.')
    if mode=='execute':
        save(folder/'summary.json',dict(**common,source_commit=f['source_commit'],work=work,environment_before=before,environment_after=environment(),
            peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,seconds_before_summary=time.perf_counter()-start,
            records_sha256={p.name:sha(p) for p in folder.glob('*.json')}))
        save(folder/'clock.json',dict(seconds_through_summary=time.perf_counter()-start,summary_sha256=sha(folder/'summary.json')))
    else:
        old=read(folder/'summary.json');need(sha(folder/'summary.json')==read(folder/'clock.json')['summary_sha256'],'Summary binding')
        for p,h in old['records_sha256'].items():need(sha(folder/p)==h,'Scientific record changed '+p)
        for k,v in common.items():need(old[k]==v,'Replay count differs '+k)
        save(R/'audit/REPLAY82.json',dict(**common,original_summary_sha256=sha(folder/'summary.json'),seconds=time.perf_counter()-start,scientific_clocks_replaced=False))
    print(json.dumps(dict(**common,mode=mode,seconds=time.perf_counter()-start),indent=2),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('freeze','execute','replay'));main(p.parse_args().mode)
