"""Independent policy, welfare, whole-domain and total-cost accounts for R9."""
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from action_cover import ROOT,R8,OUT,CornerEncloser,I,exp_i,log_i,up,terminal,Model,LO,HI

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,record,arrays=None):
    OUT.mkdir(parents=True,exist_ok=True)
    if arrays is not None:
        p=OUT/(name+'.npz');np.savez_compressed(p,**arrays);record['raw_sha256']=sha(p)
    (OUT/(name+'.json')).write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
    return record

def full_domain(gap,m,policy=None):
    gap=np.asarray(gap);positive=np.maximum(gap,0);arg=np.unravel_index(np.argmax(gap),gap.shape)
    t,i=arg;u,y=m.points[i];left=m.points[:,1]<=m.ys[0]+2*(m.ys[1]-m.ys[0]);right=m.points[:,1]>=m.ys[-1]-2*(m.ys[1]-m.ys[0]);middle=~(left|right)
    result=dict(maximum=float(np.max(gap)),positive_quantiles=dict(zip(['0','50','90','95','99','100'],np.quantile(positive,[0,.5,.9,.95,.99,1]).tolist())),
       location=dict(time_index=int(t),time=float(t/m.steps),state_index=int(i),u=float(u),log_wealth=float(y),wealth=float(np.exp(y))),
       lower_wealth_region_max=float(np.max(gap[:,left])),upper_wealth_region_max=float(np.max(gap[:,right])),interior_max=float(np.max(gap[:,middle])) if middle.any() else None,
       fraction_above_point1=float(np.mean(gap>.1)),states=int(m.N),time_levels=int(gap.shape[0]))
    if policy is not None:
        active=policy[:,~m.boundary]
        result['lower_action_frequency']=np.mean(np.isclose(active,LO,rtol=0,atol=1e-4),axis=(0,1)).tolist()
        result['upper_action_frequency']=np.mean(np.isclose(active,HI,rtol=0,atol=1e-4),axis=(0,1)).tolist()
    return result

def inherited_refinement():
    source=R8/'results/REFINEMENT.npz';z=np.load(source);meta=json.loads(source.with_suffix('.json').read_text());records=[];base=Model()
    for rec in meta['records']:
        method,seed=rec['method'],rec['seed'];nu,nx=rec['grid'];nt=rec['steps'];m=Model(nu,nx,nt)
        key=f'{method}_s{seed}_{nu}_{nx}_{nt}';gap=z[key+'_reference']-z[key+'_payoff']
        old=np.load(R8/f'results/continuous_{method}_s{seed}_search.npz')['policy'];pi=[]
        for t in range(nt):
            j=min(base.steps-1,t*base.steps//nt)
            pi.append(RegularGridInterpolator((base.us,base.ys),old[j].reshape(base.nu,base.nx,3))(m.points))
        stats=full_domain(gap,m,np.array(pi));assert abs(stats['maximum']-rec['finite_reference_minus_policy'])<1e-12
        records.append(dict(method=method,seed=seed,grid=[nu,nx],steps=nt,**stats))
    return save('FULL_DOMAIN_REFINEMENT',dict(source_sha256=sha(source),records=records,
      scope='all original R8 frozen-policy refinement nodes; observed finite-reference advantages are lower bounds on regret, not uniform continuous-economy upper bounds',
      note='17/25/33 by 25/37/49 grids are not consecutively nested; the R9 17/33 by 25/49 comparison is genuinely nested'))

def payoff_envelope(m,policy,topup=0.):
    """Externally financed flow top-up; original controls and state law fixed."""
    g=terminal(I(m.points[:,0]),I(m.points[:,1]));lo=g.lo.copy();hi=g.hi.copy();los=[lo.copy()];his=[hi.copy()]
    u=I(m.points[:,0]);y=I(m.points[:,1]);scale=exp_i((1-u)*log_i(I(1)+topup))-1 if topup else None
    for t in range(m.steps-1,-1,-1):
        value=CornerEncloser(m,lo,hi).q(np.arange(m.N),policy[t])
        if topup:
            c=I(policy[t,:,0]);utility=exp_i((1-u)*(log_i(c)+y))/(1-u)
            increment=I(m.h)*utility*scale
            increment=I(np.where(m.boundary,0.,increment.lo),np.where(m.boundary,0.,increment.hi))
            value=value+increment
        lo,hi=value.lo,value.hi;los.append(lo.copy());his.append(hi.copy())
    return np.array(los[::-1]),np.array(his[::-1])

def compensating_topup(m,pi,opt,iterations=12):
    start=time.perf_counter();a,b=0.,.01;calls=0;mask=~m.boundary
    while b<=16:
        lo,hi=payoff_envelope(m,pi,b);calls+=1
        if np.all(lo[:-1,mask]>=opt[:-1,mask]):break
        a,b=b,2*b
    else:return dict(percent_upper=None,seconds=time.perf_counter()-start,evaluations=calls,reason='no finite transfer bracket found up to 1600 percent')
    for _ in range(iterations):
        mid=a+(b-a)/2;lo,hi=payoff_envelope(m,pi,mid);calls+=1
        if np.all(lo[:-1,mask]>=opt[:-1,mask]):b=mid
        else:a=mid
    lo,hi=payoff_envelope(m,pi,b);calls+=1
    return dict(percent_upper=float(up(100*b)),bracket_percent=[100*a,100*b],seconds=time.perf_counter()-start,evaluations=calls,
      minimum_verified_compensation_slack=float(np.min(lo[:-1,mask]-opt[:-1,mask])),
      definition='uniform externally financed flow-consumption supplement; fixed policy and state law; terminal bequest and adjustment costs unchanged; not a common homothetic consumption-equivalent percentage')

def common_accounts(cover='continuous_actor_s29_search_signed_cover'):
    cp=OUT/(cover+'.npz');z=np.load(cp);opt=z['optimal_upper'];coverinfo=json.loads((OUT/(cover+'.json')).read_text());m=Model();records=[];arrays={}
    for method in ['actor','direct','search']:
      for seed in [11,29,47]:
        name=f'continuous_{method}_s{seed}_search' if method!='search' else f'continuous_direct_s{seed}_steps0_search'
        path=R8/'results'/f'{name}.npz';zz=np.load(path);info=json.loads(path.with_suffix('.json').read_text())
        for raw in [False,True] if method=='actor' else [False]:
            pi=zz['raw_policy' if raw else 'policy'];begin=time.perf_counter();lo,hi=payoff_envelope(m,pi);seconds=time.perf_counter()-begin
            gap=up(opt-lo);tag=f'{method}_s{seed}'+('_raw' if raw else '')
            arrays[tag+'_lower']=lo;arrays[tag+'_upper']=hi
            transfer=compensating_topup(m,pi,opt) if not raw else None
            cost={str(k):info['training_seconds']+info['timings']['reference']+info['timings']['policy_evaluation']+seconds+coverinfo['seconds']/k for k in [1,9,100]}
            rec=dict(method=method,seed=seed,raw=raw,input=str(path.relative_to(ROOT)),input_sha256=sha(path),
                regret_upper=float(np.max(gap)),initial_center_upper=float(gap[0,(m.nu//2)*m.nx+m.nx//2]),
                policy_evaluation_seconds=seconds,policy_bracket=float(np.max(up(hi-lo))),training_seconds=info['training_seconds'],
                original_reference_seconds=info['timings']['reference'],original_policy_evaluation_seconds=info['timings']['policy_evaluation'],
                local_search_changed_fraction=info['local_search_changed_fraction'] if not raw else 0.,
                target_pass=bool(np.max(gap)<=.1),compensation=transfer,total_cost_by_number_policies=cost,
                total_with_compensation_by_number_policies={k:v+(transfer['seconds'] if transfer else 0.) for k,v in cost.items()},
                cost_basis='R8 archived training/reference cost plus R9 current verification cost; not a same-machine training speed comparison',
                arithmetic='outward binary64 under the inherited arithmetic contract; not machine formal verification',continuous_state_time_error=None)
            records.append(rec)
    return save('COMMON_ACCOUNTS',dict(records=records,upper_source_sha256=sha(cp),shared_cover_seconds=coverinfo['seconds'],
       scope='every node/date, complete three-control box of the unchanged R8 nodal economy; comparison of the same frozen policies'),arrays)

def nested_diagnostics():
    records=[]
    for folder in sorted(OUT.glob('grid_*')):
        for path in sorted(folder.glob('*.npz')):
            meta=path.with_suffix('.json')
            if not meta.exists():continue
            info=json.loads(meta.read_text())
            if info.get('study')!='continuous_ndu':continue
            nu,nx=info['state_grid'];nt=info['steps'];m=Model(nu,nx,nt);z=np.load(path);gap=z['finite_reference']-z['policy_values']
            rec=dict(method='actor' if info['method']=='actor' else 'search',seed=info['seed'],grid=[nu,nx],steps=nt,
              training_seconds=info['training_seconds'],raw_source_sha256=sha(path),raw_file=str(path.relative_to(ROOT)),
              guarded=bool(info.get('continuation_guard',False)),guard_fraction=info.get('critic_guard_fraction'),
              own_value_fit_error=info['own_policy_value_fit_error'],**full_domain(gap,m,z['policy']))
            records.append(rec)
    return save('NESTED_RETRAINING',dict(records=records,scope='fresh training on each stated grid; full-domain finite-reference diagnostics, NOT a continuous-state/time certificate'))

if __name__=='__main__':inherited_refinement();nested_diagnostics();common_accounts()
