"""Fixed-policy, original-Bellman revalidation; no training or new path samples."""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,os,time
import numpy as np
import centered60 as c
import services60 as s
R=Path(__file__).resolve().parents[1];N=128;Q=32
TOLERANCES=(F(1,2),F(1,4),F(1,8),F(1,16),F(1,32))
FILES=('code/revalidate61.py','code/tests61.py','code/audit61.py','REVALIDATION_PROTOCOL61.md')
LOWER_HASH='246099e876d1b23f08f55810cde97a5903892763a44af931bbb2108bbd3b0621'
def read(p):return json.loads(Path(p).read_text())
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v,exclusive=False):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x' if exclusive else 'w') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def freeze():
    p=R/'audit/SOURCE_FREEZE61.json'
    if p.exists():return verify()
    import services60b
    v=dict(files_sha256={x:digest(R/x) for x in FILES},parent_freezes=dict(original=s.verify(),recording=services60b.verify(),centered=c.verify()),preparation_sha256=digest(R/'audit/PREPARATION61.json'),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),scope='R61 fixed-policy verification frozen after disjoint tests and before production. R60 outcomes were already observed and remain unchanged.')
    save(p,v,True);return digest(p)
def verify():
    import services60b
    p=R/'audit/SOURCE_FREEZE61.json';v=read(p)
    if v['parent_freezes']!=dict(original=s.verify(),recording=services60b.verify(),centered=c.verify()):raise AssertionError('Predecessor freeze changed')
    if v['preparation_sha256']!=digest(R/'audit/PREPARATION61.json'):raise AssertionError('Input provenance changed')
    for name,h in v['files_sha256'].items():
        if digest(R/name)!=h:raise AssertionError('R61 scientific source changed: '+name)
    return digest(p)

def upper_recursion(part,policy,lower,N=N,q=Q):
    policy=np.asarray(policy,dtype=np.uint16);lower=np.asarray(lower)
    if part.d!=2 or policy.shape!=(2,len(part.lo)) or lower.shape!=(2,N*N):raise ValueError('Expected complete two-date, two-state actor and lower table')
    if np.any(policy>part.capindex[None,:]):raise AssertionError('Stored actor not robustly feasible')
    x,_=c.base.boxes(N);plain=[None,None];tight=[None,None];tp=tm=None;dates=[]
    for t in (1,0):
        a=part.ranges(x,policy[t]/4096,policy[t]/4096)
        v=c.advantage_and_offset(x,a,t,q,tp);plain[t]=v.hi.copy()
        vm=v if t==1 else c.advantage_and_offset(x,a,t,q,tm)
        # This independent upper bound uses the separately re-proved global
        # nonworsening property of the original reference-advantage gate.
        tight[t]=np.minimum(vm.hi,0.)
        gp=(c.I.point(plain[t])-c.I.point(lower[t])).hi
        gm=(c.I.point(tight[t])-c.I.point(lower[t])).hi
        if not np.isfinite(gp).all() or not np.isfinite(gm).all() or np.any(gm<0) or np.any(gm>gp):raise AssertionError('Inconsistent fixed-policy bracket')
        dates.append(dict(date=t,gap_upper=float(gm.max()),unclipped_gap_upper=float(gp.max()),monotone_upper_max=float(tight[t].max()),unclipped_upper_max=float(plain[t].max()),active_zero_intersections=int(np.count_nonzero(vm.hi>0))))
        tp=c.base.RangeTable(plain[t].reshape(N,N),True);tm=c.base.RangeTable(tight[t].reshape(N,N),True)
    return dict(dates=sorted(dates,key=lambda z:z['date']),maximum_date_gap_upper=max(z['gap_upper'] for z in dates),maximum_unclipped_date_gap_upper=max(z['unclipped_gap_upper'] for z in dates),actor_range_queries=part.box_queries,actor_membership_tests=part.membership_tests,ambiguous_actor_boxes=part.ambiguous_boxes),dict(upper_excess=np.array(tight),unclipped_upper_excess=np.array(plain))

def actors():
    grouped={};aliases=0
    for folder in sorted((R/'results60').glob('worker*/prospective/services/*')):
        svc=read(folder/'service.json')
        if (svc['d'],svc['T'])!=(2,2):continue
        stage=svc['stages'][-1];model_path=folder/f'stage{stage["stage"]}-models.json';model=read(model_path)
        part=s.n.Partition(2,stage['leaves']);policy=np.asarray(model['policy'],dtype=np.uint16)
        if part.payload()!=model['partition'] or s.p.policy_hash(policy,part)!=svc['final_policy_sha256']:raise AssertionError('Returned actor identity changed')
        with np.load(folder/f'stage{stage["stage"]}-certificate.npz') as z:
            for t in (0,1):
                if not np.array_equal(z[f't{t}_selected'],policy[t]) or np.any(z[f't{t}_U']>0):raise AssertionError('Missing nonworsening certificate')
        identity=svc['final_policy_sha256'];aliases+=1
        alias=dict(worker=svc['worker'],mode=svc['mode'],seed=svc['seed'],target=svc['target'],status=svc['status'],service_path=str(folder.relative_to(R)),model_sha256=digest(model_path))
        if identity not in grouped:grouped[identity]=dict(model=model,leaves=stage['leaves'],aliases=[])
        grouped[identity]['aliases'].append(alias)
    if aliases!=32:raise AssertionError('Incomplete two-date returned-policy catalogue')
    return grouped,aliases

def main(replay=False):
    start=time.perf_counter();fz=verify();base=read(R/'audit/SCIENCE_REPLAY61.json')
    if base['status']!='passed' or base['source_freeze_sha256']!=fz:raise AssertionError('Full predecessor replay required before revalidation')
    lowerfile=R/'results60-centered/N128.npz'
    if digest(lowerfile)!=LOWER_HASH or base['centered_raw_sha256']!=LOWER_HASH:raise AssertionError('Wrong common lower Bellman table')
    with np.load(lowerfile) as z:lower=z['lower_excess'].copy()
    grouped,alias_count=actors();folder=R/'results61-revalidation'
    if not replay:folder.mkdir(parents=True,exist_ok=False)
    prior=read(folder/'summary.json') if replay else None;rows=[]
    for identity,g in sorted(grouped.items()):
        if identity not in base['validated_policy_hashes']:raise AssertionError('Unreconstructed monotonicity claim')
        begin=time.perf_counter();part=s.n.Partition(2,g['leaves']);policy=np.asarray(g['model']['policy'],dtype=np.uint16)
        before=s.p.policy_hash(policy,part);rec,raw=upper_recursion(part,policy,lower)
        if s.p.policy_hash(policy,part)!=before:raise AssertionError('Verification changed the actor')
        path=folder/(identity+'.npz')
        if replay:
            with np.load(path) as z:
                if set(z.files)!=set(raw):raise AssertionError('Revalidation archive fields changed')
                for name,value in raw.items():
                    if not np.array_equal(z[name],value):raise AssertionError('Fixed-policy endpoint replay differs: '+name)
        else:np.savez_compressed(path,**raw)
        rec.update(policy_sha256=identity,leaves=g['leaves'],aliases=g['aliases'],raw_sha256=digest(path),seconds_through_endpoint_archive=time.perf_counter()-begin,targets=[dict(tolerance=str(t),status='attained' if F(rec['maximum_date_gap_upper'])<=t else 'not_attained') for t in TOLERANCES])
        if replay:
            old=next(x for x in prior['rows'] if x['policy_sha256']==identity)
            for name in rec:
                if name!='seconds_through_endpoint_archive' and rec[name]!=old[name]:raise AssertionError('Revalidation report differs: '+name)
        else:save(folder/(identity+'.json'),rec,True)
        rows.append(rec)
    result=dict(status='passed',source_freeze_sha256=fz,original_actor_aliases=alias_count,distinct_actors=len(rows),verification_grid=dict(N=N,A=64,q=Q),common_lower_file_sha256=LOWER_HASH,source_science_audit_sha256=digest(R/'audit/SCIENCE_REPLAY61.json'),rows=rows,shared_lower_reconstruction_seconds=base['centered_replay_seconds'],seconds_through_all_endpoint_records=time.perf_counter()-start,new_training_services=0,new_policies=0,new_independent_path_samples=0,scope='Fixed original returned actors, complete acquired ranges, original continuous-action Bellman optimum. Monotonicity clipping is separately justified by full reference-gate reconstruction; unclipped bounds are retained. Shared lower reconstruction, per-actor verification and whole-process overhead have distinct clocks; predecessor stopping clocks remain unchanged.')
    if replay:save(R/'audit/REVALIDATION_REPLAY61.json',dict(status='passed',actors=len(rows),source_summary_sha256=digest(folder/'summary.json'),seconds=time.perf_counter()-start,new_samples=0))
    else:save(folder/'summary.json',result,True)
    print(json.dumps(dict(status='passed',distinct_actors=len(rows),aliases=alias_count,bounds=[dict(policy=x['policy_sha256'][:12],bound=x['maximum_date_gap_upper'],unclipped=x['maximum_unclipped_date_gap_upper'],modes=sorted(set(a['mode'] for a in x['aliases']))) for x in rows],replay=replay),indent=2),flush=True)
if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('--freeze',action='store_true');q.add_argument('--replay',action='store_true');a=q.parse_args()
    if a.freeze:print(freeze())
    else:main(a.replay)
