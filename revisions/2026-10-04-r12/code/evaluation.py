"""Fresh population/origin evaluations and direct common-path method bounds.
Statistical endpoints retain the inherited conditional arithmetic contract.
"""
from __future__ import annotations
import functools,hashlib,math,time
from pathlib import Path
from common import *

@functools.lru_cache(maxsize=96)
def account(d,steps,eps,design,shift=0.,spread=0.):
    wt=pc.weights(steps)
    if design=='stress':
        yy=profiles(d,'origin');v=np.linspace(-1.,1.,d);v-=v.mean()
        if d>1:v/=np.sqrt(np.mean(v*v))
        yy[0]=float(shift)+float(spread)*v
    else:yy=profiles(d,design)
    cons=[pc.constants(d,steps,eps,y,wt) for y in yy]
    c=dict(dimension=d,steps=steps,epsilon=eps,design=design,initial_profiles=yy.tolist(),weights=[1/len(yy)]*len(yy),components=cons,
      bias_upper=float(pc.up(np.mean([v['bias_upper'] for v in cons]))),
      actor_bias_upper=float(pc.up(np.mean([v['actor_bias']['total'] for v in cons]))),
      statistic_error_upper=float(pc.up(max(v['quadrature_and_statistic_roundoff'] for v in cons))),
      clipping_threshold=max(v['clipping_threshold'] for v in cons),clipping_bias=max(v['clipping_bias'] for v in cons),
      anchor_upper=float(pc.up(np.mean([v['anchor_upper'] for v in cons]))),state_cap=max(v['state_cap'] for v in cons),
      scope='original continuous economy, prescribed continuously state-observed innovation-recovery controller; integrated over the declared finite population, or the one stated initial point')
    return wt,c

def evaluate(path,out,design='population',steps=None,paths=None,test_seed=None,shift=0.,spread=0.):
    path=Path(path);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    steps=PROTOCOL['final_steps'] if steps is None else int(steps);paths=PROTOCOL['final_paths'] if paths is None else int(paths)
    test_seed=PROTOCOL['final_noise_seed'] if test_seed is None else int(test_seed)
    a,c,state=old.load(path);d=state['dimension'];eps=float(state['epsilon'])
    wt,con=account(d,steps,eps,design,float(shift),float(spread));h=wt['h'];support=np.asarray(con['initial_profiles'])
    initial_rng=np.random.default_rng(test_seed+100003+d)
    ids=initial_rng.integers(0,len(support),size=paths);za=support[ids].copy();z0=za.copy()
    B=old.coupling(d);Am,Bm,Cm,Mm=[pc.midpoint(wt[k]) for k in ['A','B','C','M']]
    lo=pc.up(wt['center'].hi-eps);hi=pc.down(wt['center'].lo+eps)
    prod=np.zeros(paths);loss=np.zeros(paths);rng=np.random.default_rng(test_seed+d)
    noise_hash=hashlib.sha256();sat=0;outside=0;nonfinite=0;max_state=0.;noise_clipped=0;start=time.perf_counter()
    c0=P['productivity']-(P['idiosyncratic_sigma']**2+P['common_sigma']**2)/2
    for k in range(steps):
        xx=np.concatenate([np.full((paths,1),k*h),za],1)
        with torch.no_grad():proposal=a(torch.from_numpy(xx)).numpy()
        center=float(pc.midpoint(wt['center'])[k]);nonfinite+=int((~np.isfinite(proposal)).sum());proposal=np.where(np.isfinite(proposal),proposal,center)
        m=np.maximum(lo[k],np.minimum(hi[k],proposal));sat+=int((abs(m-center)>.99*eps).sum())
        outside+=int(((za< -1.5)|(za>.5)).any(1).sum())
        fa=P['coupling']*pc.safe_tanh(za@B.T);f0=P['coupling']*pc.safe_tanh(z0@B.T)
        ma=m.mean(1);prod+=Bm[k]*(fa-f0).mean(1)
        loss+=Cm[k]-Am[k]*pc.safe_log(m).mean(1)+Bm[k]*ma+P['adjustment']/2*Am[k]*ma*ma
        z=rng.standard_normal((paths,d+1));noise_hash.update(z.tobytes());noise_clipped+=int((abs(z)>10.).sum());z=np.clip(z,-10.,10.)
        dw=math.sqrt(h)*(P['idiosyncratic_sigma']*z[:,:d]+P['common_sigma']*z[:,d:])
        za=za+h*(c0+fa-m)+dw;z0=z0+h*(c0+f0)-Mm[k]+dw
        max_state=max(max_state,float(abs(za).max()),float(abs(z0).max()))
    va=((za-za.mean(1,keepdims=True))**2).mean(1);v0=((z0-z0.mean(1,keepdims=True))**2).mean(1)
    term=-CHI*math.exp(-P['discount']*P['T'])*(va-v0);raw=prod-loss+term
    bound=pc.empirical_lower(raw,con['clipping_threshold'],con['bias_upper'],con['clipping_bias'],family_size=PROTOCOL['one_sided_family_size'],alpha=PROTOCOL['alpha'])
    ident=path.stem+f'_{design}_n{steps}'+(f'_mu{shift:g}_sd{spread:g}' if design=='stress' else '')
    rawpath=out/f'{ident}.npz';np.savez_compressed(rawpath,paired_gain=raw,production=prod,consumption_deficit=loss,terminal_gain=term,terminal_policy=za,terminal_anchor=z0,initial_profile=ids)
    bench=np.concatenate([np.full((256,1),.5),za[:256]],1);ts=time.perf_counter()
    for _ in range(12):
        with torch.no_grad():_=a(torch.from_numpy(bench))
    online=(time.perf_counter()-ts)/12
    A=-math.expm1(-P['discount']*P['T'])/P['discount']
    fee_rows=[dict(rate=q,lower=float(pc.down(bound['lower']+A*math.log1p(-q))),upper=float(pc.up(bound['upper']+A*math.log1p(-q)))) for q in PROTOCOL['gross_consumption_fee_rates']]
    row=dict(id=ident,weights=str(path.relative_to(ROOT)),weights_sha256=digest(path),source_commit=source(),method=state['method'],dimension=d,iteration=state['iteration'],epsilon=eps,design=design,shift=float(shift),spread=float(spread),steps=steps,paths=paths,initial_state_hash=hashlib.sha256(support[ids].tobytes()).hexdigest(),initial_index_hash=hashlib.sha256(ids.tobytes()).hexdigest(),noise_seed=test_seed+d,noise_sha256=noise_hash.hexdigest(),raw_sha256=digest(rawpath),bound=bound,constants=con,policy_regret_upper=float(pc.up(con['anchor_upper']-bound['lower'])),seconds=time.perf_counter()-start,decision_batch256_seconds=online,nonfinite_proposals=nonfinite,noise_clipped=noise_clipped,action_saturation_frequency=sat/(steps*paths*d),outside_R11_training_box_frequency=outside/(steps*paths),max_internal_state=max_state,consumption_fee=fee_rows,fee_lower_break_even=float(-math.expm1(-max(0.,bound['lower'])/A)),interpretation='mean is the pre-adjustment paired numerical statistic; endpoints include sampling, diffusion transfer, clipping and arithmetic; not a calibrated welfare estimate')
    if max_state>con['state_cap']:raise AssertionError('arithmetic state cap violated')
    write(out/f'{ident}.json',row);print(ident,bound['lower'],bound['upper'],flush=True);return row

def paired(left,right,out,label=None):
    left=Path(left);right=Path(right);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    a=json.loads(left.read_text());b=json.loads(right.read_text())
    for k in ['dimension','design','steps','paths','initial_state_hash','initial_index_hash','noise_seed','noise_sha256']:
        if a[k]!=b[k]:raise ValueError('unpaired inputs: '+k)
    xa=np.load(left.with_suffix('.npz'));xb=np.load(right.with_suffix('.npz'))
    if not np.array_equal(xa['initial_profile'],xb['initial_profile']):raise ValueError('different initial profiles')
    if not np.array_equal(xa['terminal_anchor'],xb['terminal_anchor']):raise ValueError('common anchor failed to cancel')
    delta=xa['paired_gain']-xb['paired_gain'];ca,cb=a['constants'],b['constants']
    # Only policy transfer errors remain: the common reference cancels.
    bias=float(pc.up(ca['actor_bias_upper']+cb['actor_bias_upper']+ca['statistic_error_upper']+cb['statistic_error_upper']+1e-12))
    clip=float(pc.up(ca['clipping_threshold']+cb['clipping_threshold']));tail=float(pc.up(ca['clipping_bias']+cb['clipping_bias']))
    bound=pc.empirical_lower(delta,clip,bias,tail,PROTOCOL['one_sided_family_size'],PROTOCOL['alpha'])
    ident=label or a['id']+'__minus__'+b['id'];rp=out/f'{ident}.npz';np.savez_compressed(rp,paired_difference=delta)
    row=dict(id=ident,left=str(left.relative_to(ROOT)),right=str(right.relative_to(ROOT)),left_raw_sha256=a['raw_sha256'],right_raw_sha256=b['raw_sha256'],dimension=a['dimension'],design=a['design'],steps=a['steps'],paths=a['paths'],bound=bound,bias_upper=bias,clipping_threshold=clip,clipping_bias=tail,raw_sha256=digest(rp),shared_noise_sha256=a['noise_sha256'],anchor_transfer_cancelled=True,source_commit=source(),scope='direct simultaneous method contrast for these fitted policies; not the difference of two lower endpoints; no unseen-seed population inference')
    write(out/f'{ident}.json',row);print(ident,bound['lower'],bound['upper'],flush=True);return row
