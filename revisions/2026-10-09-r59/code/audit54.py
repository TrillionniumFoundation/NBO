"""Offline replay of the deposited R53 studies; no new policies or samples.

Checks every saved cell decision, all output hashes, cost interval arithmetic,
and controlled false-null decisions. It does not retime scientific services or
claim that replaying stored endpoints independently re-proves their enclosure.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,time
import numpy as np
import study53 as p
import extend53 as ext
R=Path(__file__).resolve().parents[1]

def read(f):return json.loads(Path(f).read_text())
def digest(f):
    with open(f,'rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()
def same(a,b,label):
    if not np.array_equal(a,b):raise AssertionError(label)
def need(condition,label):
    if not condition:raise AssertionError(label)
def save(f,v):
    f=Path(f);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')

def service(folder):
    s=read(folder/'service.json');clock=read(folder/'clock.json')
    need(digest(folder/'service.json')==clock['service_sha256'],'service digest')
    T=s['T'];n=1<<p.BITS;N=n*n
    bins=np.stack(np.meshgrid(np.arange(n),np.arange(n),indexing='ij'),axis=-1).reshape(-1,2)
    cap=(4096*(2*n+bins.sum(axis=1)))//(16*n)
    old=np.load(folder/'policy-pass0.npz')['policy']
    need(p.d.policy_digest(old)==s['snapshots'][0],'initial policy digest')
    for rung in s['reconstruction_prefix']:
        name=f"construction-N{rung['N']}-K{rung['K']}-M{rung['M']}.json"
        need(digest(folder/name)==rung['sha256'],'construction digest')
    bounds=[p.inference.support(T-t,1)[1] for t in range(T)]+[F(0)]
    rows=[];checked=0
    for k in range(1,T+1):
        rec=read(folder/f'pass{k}.json');raw=folder/f'pass{k}-cells.npz';polfile=folder/f'policy-pass{k}.npz'
        need(digest(raw)==rec['records_sha256'],'cell file digest')
        need(digest(polfile)==rec['policy_file_sha256'],'policy file digest')
        new=np.load(polfile)['policy'];need(new.shape==(T,n,n),'policy shape')
        need(p.d.policy_digest(old)==rec['before_sha256'],'before identity')
        need(p.d.policy_digest(new)==rec['after_sha256']==s['snapshots'][k],'after identity')
        eps=[]
        with np.load(raw) as a:
            for t,report in enumerate(rec['dates']):
                lo=a[f't{t}_candidate_lo'];hi=a[f't{t}_candidate_hi'];ix=a[f't{t}_candidate_indices']
                ll=a[f't{t}_cover_lo'];lu=a[f't{t}_cover_hi']
                need(lo.shape==hi.shape==ix.shape==(9,N),'candidate shapes')
                need(ll.shape==lu.shape==(8,N),'cover shapes')
                need(np.isfinite(lo).all() and np.isfinite(hi).all() and np.isfinite(ll).all() and np.isfinite(lu).all(),'finite endpoints')
                need((lo<=hi).all() and (ll<=lu).all(),'ordered endpoints')
                base=old[t].reshape(-1);chosen=base.copy();upper=np.zeros(N)
                for j in range(9):
                    same(ix[j],(cap*j)//8,'complete robust proposal menu')
                    take=hi[j]<upper;chosen[take]=ix[j,take];upper[take]=hi[j,take]
                lower=np.minimum(0,ll.min(axis=0));gap=(p.I.point(upper)-p.I.point(lower)).hi
                same(chosen,a[f't{t}_selected'],'selected action replay');same(chosen,new[t].reshape(-1),'deployed policy replay')
                same(upper,a[f't{t}_accepted_upper'],'upper replay');same(lower,a[f't{t}_continuous_inf_lower'],'lower cover replay')
                same(gap,a[f't{t}_greedy_gap_upper'],'directed gap replay')
                need((chosen<=cap).all() and (upper<=0).all() and (lower<=upper).all(),'feasibility safety and gap order')
                changed=int(np.count_nonzero(chosen!=base));need(changed==report['changed_cells'],'changed count')
                need(int(np.count_nonzero((ix!=base)&(hi<0)))==report['strict_candidate_comparisons'],'strict comparison count')
                need(int(np.count_nonzero((ix!=base)&(hi>=0)))==report['blocked_candidate_comparisons'],'blocked comparison count')
                need(float(gap.max())==report['greedy_gap_upper'],'supremum gap')
                eps.append(F(float(gap.max())));checked+=N
            bounds=[p.d.BETA*bounds[t+1]+eps[t] for t in range(T)]+[F(0)]
            need(list(map(str,bounds))==rec['gap_upper_exact'],'finite-sweep recursion')
        rows.append(dict(pass_number=k,changed_by_date=[d['changed_cells'] for d in rec['dates']],
            changed_cells=sum(d['changed_cells'] for d in rec['dates']),
            nonterminal_changed_cells=sum(d['changed_cells'] for d in rec['dates'][:-1]),
            gap_upper=rec['gap_upper'][0],greedy_gap_by_date=[d['greedy_gap_upper'] for d in rec['dates']],
            contrast_bound_by_date=[d['uniform_action_contrast_upper'] for d in rec['dates']],
            strict_candidate_comparisons=sum(d['strict_candidate_comparisons'] for d in rec['dates']),
            blocked_candidate_comparisons=sum(d['blocked_candidate_comparisons'] for d in rec['dates']),
            symmetric_candidate_acceptances=sum(d['absolute_contrast_candidate_acceptances'] for d in rec['dates']),
            scalar_candidate_acceptances=sum(d['scalar_width_candidate_acceptances'] for d in rec['dates']),
            prefix_seconds_through_outputs=rec['prefix_seconds_through_outputs'],work=rec['work']))
        old=new
    return dict(method=s['method'],T=T,passes=rows,checked_cell_decisions=checked,
        construction_seconds=s['construction_seconds'],acquisition_seconds=s['acquisition_seconds'],
        total_service_seconds=clock['seconds_through_record'],peak_rss_kib=s['peak_rss_kib'],
        nonuniform_date_models=s.get('nonuniform_date_models'),
        adaptive_geometry=s.get('adaptive_geometry',[]),snapshots=s['snapshots'])

def costs(folder,extension=False):
    j=read(folder/'costs.json');clock=read(folder/'clock.json')
    need(digest(folder/'costs.json')==clock['costs_sha256'],'cost record digest')
    f=folder/'path-endpoints.npz';need(digest(f)==j['raw_endpoints_sha256'],'path endpoints digest')
    T=j['T'];keys=j['policy_keys'];B=p.inference.support(T,1)[1]
    with np.load(f) as z:
        lo=z['lower'];hi=z['upper'];need(lo.shape==hi.shape==(len(keys),j['paths']),'cost shapes')
        for i,key in enumerate(keys):
            rec=p.interval_record(lo[i],hi[i],F(0),B)
            for field in ('interval_exact','endpoint_sha256','sign'):
                need(rec[field]==j['absolute_cost'][key][field],'absolute cost '+key+' '+field)
        def check(i,k,name):
            old=j['contrasts'][name]
            if j['policy_sha256'][i]==j['policy_sha256'][k]:
                need(old['interval_exact']==['0','0'],'identity contrast');return
            diff=p.I(lo[i],hi[i])-p.I(lo[k],hi[k]);rec=p.interval_record(diff.lo,diff.hi,-B,B)
            for field in ('interval_exact','endpoint_sha256','sign'):
                need(rec[field]==old[field],'paired cost '+name+' '+field)
        methods=ext.METHODS if extension else p.METHODS
        for m,method in enumerate(methods):
            start=m*(T+1)
            for k in range(1,T+1):
                check(start,start+k,f'{method}-pass{k}-initial-gain')
                check(start+k-1,start+k,f'{method}-pass{k}-step-gain')
        if extension:
            import itertools
            for a,b in itertools.combinations(range(3),2):
                for k in range(T+1):check(a*(T+1)+k,b*(T+1)+k,f'{methods[a]}-minus-{methods[b]}-pass{k}')
        else:
            for k in range(T+1):check(k,T+1+k,f'witness-minus-fvi-pass{k}')
    return dict(T=T,paths=j['paths'],policy_keys=keys,policy_sha256=j['policy_sha256'],
        absolute_cost={k:v['interval'] for k,v in j['absolute_cost'].items()},
        contrasts={k:v['interval'] for k,v in j['contrasts'].items()},
        full_shared_cost_service_seconds=clock['seconds_through_record'],
        evaluation_seconds=j['evaluation_seconds'],family_error=j['family_error'],
        family_maximum=j['family_maximum'],log_upper=j['log_upper'],stream_sha256=j['stream_sha256'])

def misspecification():
    folder=R/'results53-extension/misspecification';j=read(folder/'summary.json');clock=read(folder/'clock.json')
    need(digest(folder/'summary.json')==clock['summary_sha256'],'misspecification summary digest')
    n=1<<p.BITS;N=n*n;changed=harmful=blocked=0
    for row in j['cases']:
        f=folder/(row['key']+'.npz');need(digest(f)==row['records_sha256'],'nuisance file digest')
        pol=np.load(R/'results53/services'/f"{row['method']}-T2/policy-pass0.npz")['policy'];base=pol[-1].reshape(-1)
        bins=np.stack(np.meshgrid(np.arange(n),np.arange(n),indexing='ij'),axis=-1).reshape(-1,2)
        cap=(4096*(2*n+bins.sum(axis=1)))//(16*n)
        best=np.zeros(N);badbest=np.zeros(N);chosen=base.copy();wrong=base.copy();upper=np.zeros(N);harm=np.zeros(N)
        with np.load(f) as a:
            accepted=blocked_here=0
            for k in range(9):
                ix=(cap*k)//8;true_lo=a[f'k{k}_true_lo'];true_hi=a[f'k{k}_true_hi'];corr=a[f'k{k}_corrected_upper'];bad=a[f'k{k}_critic_upper']
                need((true_lo<=true_hi).all(),'true contrast order');need((a[f'k{k}_nuisance_lo']<=a[f'k{k}_nuisance_hi']).all(),'nuisance order')
                need((a[f'k{k}_rho_upper']>=0).all(),'nonnegative allowance')
                take=corr<best;unsafe=bad<badbest
                chosen[take]=ix[take];upper[take]=true_hi[take];best[take]=corr[take]
                wrong[unsafe]=ix[unsafe];harm[unsafe]=true_lo[unsafe];badbest[unsafe]=bad[unsafe]
                accepted+=int(np.count_nonzero((ix!=base)&(corr<0)))
                blocked_here+=int(np.count_nonzero((ix!=base)&(corr>=0)))
            same(chosen,a['selected'],'nuisance gate');same(wrong,a['false_null_selected'],'false-null gate')
            same(upper,a['selected_true_upper'],'nuisance true upper');same(harm,a['false_null_selected_true_lower'],'false-null true lower')
            need((chosen<=cap).all() and (upper<=0).all(),'safe perturbed action')
            c=int(np.count_nonzero(chosen!=base));h=int(np.count_nonzero((wrong!=base)&(harm>0)))
            need(c==row['changed_cells'] and h==row['false_null_certified_harmful_cells'],'perturbation counts')
            need(accepted==row['accepted_candidates'] and blocked_here==row['blocked_candidates'],'perturbation candidate counts')
            need(p.d.policy_digest(chosen)==row['policy_sha256'],'nuisance policy identity')
            changed+=c;harmful+=h;blocked+=blocked_here
    return dict(cases=len(j['cases']),cells_per_case=N,checked_cell_cases=N*len(j['cases']),
        safe_changed_cell_cases=changed,false_null_certified_harmful_cell_cases=harmful,
        blocked_candidate_cases=blocked,exact_null_cases=sum(x['exact_null'] for x in j['cases']),
        nonzero_bound_cases=sum(x['contrast_bound_upper']>0 for x in j['cases']),
        maximum_contrast_bound=max(x['contrast_bound_upper'] for x in j['cases']),
        service_seconds=clock['seconds_through_record'],statistical_observations=0,
        scope='controlled known perturbations; not learned-null discovery or unknown-kernel inference')

def main():
    start=time.perf_counter();p.verify_freeze();ext.verify()
    primary=[service(R/'results53/services'/f'{m}-T{T}') for T in (2,3) for m in p.METHODS]
    adaptive=[service(R/'results53-extension/services'/m) for m in ext.METHODS]
    primary_costs=[costs(R/'results53/direct'/f'T{T}') for T in (2,3)]
    adaptive_cost=costs(R/'results53-extension/direct',True);mis=misspecification()
    for m in p.METHODS:
        old=next(x for x in primary if x['method']==m and x['T']==2)
        new=next(x for x in adaptive if x['method']==m)
        need(old['snapshots']==new['snapshots'],'cohort policy identity')
    # These are observed release costs of a completed catalogue, not unobserved
    # optimal stopping costs. Full shared inference is conservatively charged
    # to each method and all its own executed sweeps are charged, even when an
    # earlier policy has the lowest upper cost endpoint.
    catalogues=[]
    for cohort,services,costset in [('primary-T2',[x for x in primary if x['T']==2],primary_costs[0]),('primary-T3',[x for x in primary if x['T']==3],primary_costs[1]),('adaptive',adaptive,adaptive_cost)]:
        points=[]
        for svc in services:
            candidates=[(k,v[1]) for k,v in costset['absolute_cost'].items() if k.startswith(svc['method']+'-')]
            key,upper=min(candidates,key=lambda x:(x[1],x[0]))
            points.append(dict(method=svc['method'],selected_policy=key,actual_cost_upper=upper,
                construction_and_all_sweeps_seconds=svc['total_service_seconds'],
                full_shared_inference_seconds=costset['full_shared_cost_service_seconds'],
                measured_catalogue_work_seconds=svc['total_service_seconds']+costset['full_shared_cost_service_seconds']))
        thresholds=sorted(set(x['actual_cost_upper'] for x in points))
        frontier=[dict(cost_upper_target=u,eligible_methods=[x['method'] for x in points if x['actual_cost_upper']<=u],
            least_recorded_work_method=min([x for x in points if x['actual_cost_upper']<=u],key=lambda x:x['measured_catalogue_work_seconds'])['method']) for u in thresholds]
        catalogues.append(dict(cohort=cohort,points=points,frontier=frontier))
    result=dict(status='passed',baseline_commit='de82bbe365b1b2124ab2edcab7d9237182f51617',
        review_commit='8e811efb4e1b2e9d588472bce1d35bb93eaaf23a',
        primary=primary,adaptive=adaptive,primary_costs=primary_costs,adaptive_cost=adaptive_cost,
        misspecification=mis,actual_cost_catalogues=catalogues,
        checked_full_sweep_cell_decisions=sum(x['checked_cell_decisions'] for x in primary+adaptive),
        new_scientific_services=0,new_policy_cost_samples=0,
        primary_strict_changes=sum(z['changed_cells'] for x in primary for z in x['passes']),
        primary_nonterminal_strict_changes=sum(z['nonterminal_changed_cells'] for x in primary for z in x['passes']),
        scope='all frozen files and stored decision records replayed; interval inference recomputed; no resimulation, service retiming, or independent full kernel reintegration',
        catalogue_work_scope='all own construction/sweeps plus full shared inference; audit and publication overhead separately recorded; not a minimal sequential stopping frontier',
        replay_seconds=time.perf_counter()-start)
    save(R/'audit/RESULT_AUDIT54.json',result)
    print(json.dumps({k:result[k] for k in ('status','checked_full_sweep_cell_decisions','primary_strict_changes','primary_nonterminal_strict_changes','misspecification','replay_seconds')},indent=2))
if __name__=='__main__':main()
