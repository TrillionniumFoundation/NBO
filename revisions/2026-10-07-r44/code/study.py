"""R44 retained-policy and direct economic comparison study.

The R42 catalogue is immutable input. New clocks are diagnostic clocks only.
All arithmetic enclosures use the source-bound outward interval implementation.
"""
from __future__ import annotations
import os
for _k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_k] = '1'
from pathlib import Path
import argparse, hashlib, json, math, platform, sys, time
from fractions import Fraction
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT/'evidence/2026-10-07-r42'
sys.path.insert(0,str(INPUT/'code'))
import coupled_training as ct
import scalar_training as st
import neural_chain as nc
from nonlinear import I, encode
BETA = 15/16
FAILED = (41,89,120,124,128,145,147)
ALPHA = Fraction(1,100)
SAMPLE_SIZE = 65536


def canonical(obj):
    return (json.dumps(obj, default=encode, sort_keys=True, separators=(',',':'))+'\n').encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load_service(i):
    p=INPUT/'results/publication'/f'service-{i:03d}'
    raw=(p/'record.json').read_bytes()
    clock=json.loads((p/'clock.json').read_text())
    if hashlib.sha256(raw).hexdigest()!=clock['record_sha256']:
        raise ValueError(f'Record digest mismatch: {i}')
    return json.loads(raw),clock


def write_new(path,obj,start=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists(): raise FileExistsError(path)
    raw=canonical(obj)
    with path.open('xb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    clock={'record_sha256':hashlib.sha256(raw).hexdigest(),
           'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'python':platform.python_version(),'numpy':np.__version__,
           'machine':platform.platform(),'cpu_affinity':sorted(os.sched_getaffinity(0)),
           'frequency_controlled':False,
           'timing_interpretation':'new diagnostic only; never a reconstructed R42 service clock'}
    if start is not None: clock['seconds_through_fsync']=time.perf_counter()-start
    path.with_suffix('.clock.json').write_bytes(canonical(clock))
    return clock


def policy_bound(records,terminal,allowances):
    out=I.point(0.); d=I.point(1.)
    for r,a in zip(records,allowances):
        out=out+d*(I.point(r['residual_upper'])-r['residual_lower']+a)
        d=d*BETA
    return float((out+d*(I.point(terminal['upper'])-terminal['lower'])).hi)


def decompose(r,v):
    if 'terminal' not in v:
        return {'verifier':'inherited spline verifier','reported_policy_bound':v['policy_gap_upper']}
    d=1.; cover=0.; actor=0.; action=0.; floor=0.
    for row in v['records']:
        cv=row.get('state_cover_allowance',row.get('interpolation_allowance',0.))
        cover+=d*2*cv; actor+=d*row['actor_allowance']
        action+=d*row.get('action_cover_allowance',0.)
        floor+=d*(row['residual_upper']-row['residual_lower']-2*cv)
        d*=BETA
    tc=v['terminal'].get('interpolation_allowance',0.)
    term=d*(v['terminal']['upper']-v['terminal']['lower'])
    return {'state_cover_in_residual':cover,'actor_total':actor,
            'action_cover_inside_actor':action,'nodal_residual_enclosure_width':floor,
            'terminal_total':term,'terminal_cover_inside_total':d*2*tc,
            'accounting_note':'representation and optimizer errors are not separately identified by a nodal residual; subcomponents inside totals are not added twice'}


def recertify(i):
    if i not in FAILED: raise ValueError('Outside frozen diagnostic catalogue')
    r,clock=load_service(i); old=r['attempts'][-1]
    net_hash=digest(r['networks'])
    old_actor=old['actors'] if i==128 else old['policy']['actors']
    actor_hash=digest(old_actor)
    start=time.perf_counter()
    if i==128:
        v=ct.certificate(r['networks'],r['price'],256)
        transient=len(v['actors'])*len(v['actors'][0])*2
        counters={k:v[k] for k in ('state_nodes','inner_iterations_per_node','neural_neuron_expectations','expectation_gradient_float_calls','expectation_interval_calls')}
    else:
        v=nc.certify_chain(r['networks'],r['price'],r['theta'],4096,1024,
                           old_policy=old['policy'])
        transient=sum(len(a) for a in v['policy']['actors'])
        counters={'bellman_transition_evaluations':v['bellman_transition_evaluations'],
                  'state_nodes':4097,'action_nodes':1025}
    # These are the ORIGINAL deployed actors' allowances, not fine-grid ones.
    original_allowances=[z['actor_allowance'] for z in old['records']]
    bound=policy_bound(v['records'],old['terminal'],original_allowances)
    if net_hash!=digest(r['networks']) or actor_hash!=digest(old_actor):
        raise AssertionError('An inherited network or actor was changed')
    target=.10 if i==128 else .04
    out={'service_id':i,'method':r['method'],'price':r['price'],
         'theta':r.get('theta'),'seed':r['seed'],'target':target,
         'original_record_sha256':clock['record_sha256'],
         'network_sha256':net_hash,'original_actor_sha256':actor_hash,
         'networks_unchanged':True,'deployed_actor_unchanged':True,'training_updates':0,
         'original_N':old['N'],'verification_N':v['N'],'verification_A':v.get('A'),
         'original_bound':old['policy_gap_upper'],'retained_policy_bound':bound,
         'target_attained':bound<=target,
         'original_actor_allowances':original_allowances,
         'retained_terminal_enclosure':old['terminal'],
         'refined_residual_records':v['records'],
         'original_decomposition':decompose(r,old),
         'original_actor_scalar_storage':int(np.asarray(old_actor).size),
         'transient_fine_actor_scalars_discarded':transient,
         'new_stored_actor_scalars':0,'verification_work':counters,
         'interpretation':'post-review verification of unchanged R42 policy; original capped failure remains a failure'}
    c=write_new(ROOT/'results'/f'recertify-{i:03d}.json',out,start)
    print(json.dumps({'id':i,'old':out['original_bound'],'new':bound,'pass':out['target_attained'],'seconds':c['seconds_through_fsync']}),flush=True)
    return out


def isum_arrays(x:I):
    """Outward pairwise reduction, with no unverified BLAS/reduction bound."""
    lo=x.lo.reshape(-1); hi=x.hi.reshape(-1)
    while len(lo)>1:
        if len(lo)%2: lo=np.r_[lo,0.]; hi=np.r_[hi,0.]
        lo=np.nextafter(lo[::2]+lo[1::2],-np.inf)
        hi=np.nextafter(hi[::2]+hi[1::2],np.inf)
    return I(lo[0],hi[0])


def sqrt_up(x):
    """Check the rounded square root by exact dyadic arithmetic."""
    x=float(x)
    if x<0 or not math.isfinite(x): raise ArithmeticError('Invalid square root')
    y=math.sqrt(x)
    while Fraction(y)*Fraction(y)<Fraction(x): y=math.nextafter(y,math.inf)
    return math.nextafter(y,math.inf)


def endpoint_moments(x):
    n=len(x); m=isum_arrays(I.point(x))/n
    # Sum about an enclosing mean also bounds the sample variance above.
    v=isum_arrays((I.point(x)-m).square())/(n-1)
    return m,float(v.hi)


def support(r,v,x0):
    f0=ct.ivalue(r['networks'][0],[I.point(x0[j]) for j in range(2)])
    lo=I.point(0.); hi=I.point(0.); d=I.point(1.)
    for z in v['records']:
        lo=lo-d*z['residual_upper']
        hi=hi+d*(I.point(z['actor_allowance'])-z['residual_lower'])
        d=d*BETA
    lo=lo-d*v['terminal']['upper']; hi=hi-d*v['terminal']['lower']
    return I((f0+lo).lo,(f0+hi).hi)


def actor_interval(v,t,x):
    N=v['N']; a=np.asarray(v['actors'][t]).reshape(N+1,N+1,2)
    jl=[];ju=[]
    for xx in x:
        # Include every possible half-up nearest-node decision at the boundary.
        z=xx*N+.5
        jl.append(np.clip(np.floor(z.lo).astype(np.int64),0,N))
        ju.append(np.clip(np.floor(z.hi).astype(np.int64),0,N))
    al=a[jl[0],jl[1]].copy(); ah=al.copy()
    bad=np.flatnonzero((jl[0]!=ju[0])|(jl[1]!=ju[1]))
    for k in bad:
        rect=a[jl[0][k]:ju[0][k]+1,jl[1][k]:ju[1][k]+1,:]
        al[k]=rect.min(axis=(0,1));ah[k]=rect.max(axis=(0,1))
    return [I(al[:,j],ah[:,j]) for j in range(2)],len(bad)


def advance(x,a,z):
    return [.125+.5*x[j]+.125*x[1-j]+.0625*x[j]*(1-x[1-j])+a[j]+z[j] for j in range(2)]


def method_scores(r,v,x0,innovations):
    n=len(innovations);x=[I.point(np.full(n,x0[j])) for j in range(2)]
    score=ct.ivalue(r['networks'][0],x);cost=I.point(np.zeros(n));d=I.point(1.)
    ambiguity=0
    for t in range(4):
        a,bad=actor_interval(v,t,x); ambiguity+=bad
        q,_=ct.iq(r['networks'][t+1],x,a,r['price'])
        f=ct.ivalue(r['networks'][t],x)
        score=score+d*(q-f)
        c=ct.istatecost(x)+r['price']*ct.isum([aa.square() for aa in a])+.5*a[0]*a[1]+4*ct.isum([aa.square().square() for aa in a])
        cost=cost+d*c
        z=[]
        for j in range(2):
            k=innovations[:,t,j]
            # Exactly representable dyadic endpoints, no inverse-CDF libm call.
            z.append(I((k.astype(float)*2**-39-1)*ct.SHOCK,
                       ((k+1).astype(float)*2**-39-1)*ct.SHOCK))
        x=advance(x,a,z);d=d*BETA
    terminal=ct.istatecost(x,True)
    score=score+d*(terminal-ct.ivalue(r['networks'][4],x))
    cost=cost+d*terminal
    return score,cost,ambiguity


def coupled_pairs():
    methods={}
    for i in range(150):
        r,c=load_service(i)
        if r.get('method') in ('convex-neural','ridge-projection'):
            methods[(r['price'],r['seed'],r['method'])]=(i,r,c)
    pairs=[]
    for p in (1,4):
        for s in ct.SEEDS:
            pairs.append((methods[p,s,'convex-neural'],methods[p,s,'ridge-projection']))
    return pairs


def paired(pair_index,state_index):
    start=time.perf_counter()
    (ni,nr,nc0),(ri,rr,rc0)=coupled_pairs()[pair_index]
    nv=nr['attempts'][nr['crossings']['0.25']['attempt']]
    rv=rr['attempts'][rr['crossings']['0.25']['attempt']]
    x0=((.125,.125),(.25,.5),(.5,.25),(.75,.75))[state_index]
    ns,rs=support(nr,nv,x0),support(rr,rv,x0)
    sup=ns-rs; range_upper=float(sup.width())
    seed=441007+100*pair_index+state_index
    rng=np.random.Generator(np.random.PCG64(seed))
    innovations=rng.integers(0,2**40,size=(SAMPLE_SIZE,4,2),dtype=np.uint64)
    scores=[];costs=[];ambiguities=[0,0]
    # A bounded batch keeps memory independent of the sample count.
    for offset in range(0,SAMPLE_SIZE,4096):
        zz=innovations[offset:offset+4096]
        sn,cn,an=method_scores(nr,nv,x0,zz)
        sr,cr,ar=method_scores(rr,rv,x0,zz)
        z=sn-sr; c=cn-cr
        lower=np.maximum(z.lo,float(sup.lo));upper=np.minimum(z.hi,float(sup.hi))
        if np.any(lower>upper): raise ArithmeticError('Sample contradicts certified support')
        scores.append(np.column_stack((lower,upper))); costs.append(np.column_stack((c.lo,c.hi)))
        ambiguities[0]+=an;ambiguities[1]+=ar
    scores=np.concatenate(scores); costs=np.concatenate(costs)
    from nonlinear import log_bound
    logfactor=log_bound(I.point(9600.)) # 2 / (0.01 / 48)
    intervals=[];moments=[]
    for j in (0,1):
        mean,var=endpoint_moments(scores[:,j])
        root=(2*I.point(var)*logfactor/SAMPLE_SIZE).hi
        rad=I.point(sqrt_up(root))+7*I.point(range_upper)*logfactor/(3*(SAMPLE_SIZE-1))
        intervals.append((mean-rad).lo.item() if j==0 else (mean+rad).hi.item())
        moments.append({'mean_lower':float(mean.lo),'mean_upper':float(mean.hi),'sample_variance_upper':var,'bernstein_radius_upper':float(rad.hi)})
    # The deterministic support can only sharpen the confidence interval.
    lower=max(intervals[0],float(sup.lo));upper=min(intervals[1],float(sup.hi))
    if lower>upper: raise ArithmeticError('Empty confidence interval')
    cmlo,_=endpoint_moments(costs[:,0]); cmhi,_=endpoint_moments(costs[:,1])
    out={'pair_index':pair_index,'state_index':state_index,'price':nr['price'],'training_seed':nr['seed'],'state':x0,
         'neural_service_id':ni,'ridge_service_id':ri,'neural_record_sha256':nc0['record_sha256'],'ridge_record_sha256':rc0['record_sha256'],
         'neural_attempt':nr['crossings']['0.25']['attempt'],'ridge_attempt':rr['crossings']['0.25']['attempt'],
         'neural_N':nv['N'],'ridge_N':rv['N'],'common_target':.25,'sample_size':SAMPLE_SIZE,
         'rng':'numpy.random.PCG64','simulation_seed':seed,'innovation_bits':40,
         'innovation_bin_sha256':hashlib.sha256(innovations.astype('<u8').tobytes()).hexdigest(),
         'endpoint_sha256':hashlib.sha256(scores.astype('<f8').tobytes()).hexdigest(),
         'support_lower':float(sup.lo),'support_upper':float(sup.hi),'range_upper':range_upper,
         'lower_endpoint_moments':moments[0],'upper_endpoint_moments':moments[1],
         'direct_cost_sample_mean_enclosure':[float(cmlo.lo),float(cmhi.hi)],
         'confidence_lower':lower,'confidence_upper':upper,
         'sign':'neural-cost-higher' if lower>0 else 'neural-cost-lower' if upper<0 else 'unresolved',
         'family_error':.01,'family_tails':48,'ambiguous_actions_neural':ambiguities[0],'ambiguous_actions_ridge':ambiguities[1],
         'max_sample_enclosure_width':float(np.max(np.nextafter(scores[:,1]-scores[:,0],np.inf))),
         'confidence_interpretation':'simultaneous finite-sample guarantee under iid uniform-bin simulation model, not independence of a fixed PRNG stream',
         'estimand':'original continuous-law J(neural policy)-J(ridge policy); own-policy Bellman control variate'}
    clock=write_new(ROOT/'results'/f'paired-{pair_index}-{state_index}.json',out,start)
    print(json.dumps({'pair':pair_index,'state':state_index,'interval':[lower,upper],'sign':out['sign'],'seconds':clock['seconds_through_fsync']}),flush=True)
    return out


def audit():
    from collections import Counter
    idx=json.loads((INPUT/'results/publication/INDEX.json').read_text())
    if idx['executed']!=150 or idx['fixed_catalogue_size']!=150:raise ValueError('Incomplete original catalogue')
    records={};counts=Counter();attainment={};sources={}
    for i in range(150):
        r,c=load_service(i);r.setdefault('method',r.get('selected_method'));records[i]=(r,c);counts[r['method']]+=1
        for name,sha in c.get('source_sha256',{}).items():
            raw=(INPUT/'code'/name).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('Original code hash mismatch')
            sources[name]=sha
        if r.get('crossings') is not None:
            for e,v in r['crossings'].items():
                key=f'{r["method"]}@{e}';attainment[key]=attainment.get(key,0)+(v is not None)
    signed={};scalar=[];coup=[]
    for e in ('.06','.04'):
        key=str(float(e));counts2=Counter();ratios=[]
        for i,(r,c) in records.items():
            if r['method']!='direct-neural':continue
            j,other=next((j,z[0]) for j,z in records.items() if z[0]['method']=='spline' and (z[0]['price'],z[0]['theta'],z[0]['seed'])==(r['price'],r['theta'],r['seed']))
            if r['crossings'][key] is None or other['crossings'][key] is None:continue
            a=r['attempts'][r['crossings'][key]['attempt']]['own_policy_values'];b=other['attempts'][other['crossings'][key]['attempt']]['own_policy_values']
            v=I(a['lower'],a['upper'])-I(b['lower'],b['upper'])
            counts2['positive']+=int(np.sum(v.lo>0));counts2['negative']+=int(np.sum(v.hi<0));counts2['overlap']+=int(np.sum((v.lo<=0)&(v.hi>=0)))
            counts2['contained_in_descriptive_margin']+=int(np.sum((v.lo>=-.005)&(v.hi<=.005)))
        signed[key]=dict(counts2)
    for i,(r,c) in records.items():
        if r['method'] in ('direct-neural','spline','convex-neural','ridge-projection','quadratic-projection'):
            row={'id':i,'method':r['method'],'price':r['price'],'theta':r.get('theta'),'seed':r['seed'],'final_gap':r['attempts'][-1]['policy_gap_upper'],'final_N':r['attempts'][-1]['N'],'training_seconds':r.get('training_seconds'),'seconds_through_fsync':c['seconds_through_fsync'],'crossings':r['crossings'],'decompositions':[decompose(r,v) for v in r['attempts']]}
            (scalar if r['method'] in ('direct-neural','spline') else coup).append(row)
    precision=[{'id':i,'record':r,'clock':c} for i,(r,c) in records.items() if r['method'] not in ('direct-neural','spline','convex-neural','ridge-projection','quadratic-projection')]
    out={'original_records_verified':150,'original_source_hashes':sources,'method_counts':dict(counts),'attainment':attainment,'scalar_direct_signs':signed,'scalar_services':scalar,'coupled_services':coup,'precision_services':precision,'original_record_replacements':0}
    write_new(ROOT/'results/R42_REPLAY.json',out)
    print(json.dumps({'verified':150,'counts':dict(counts),'attainment':attainment,'signs':signed}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('audit','recertify','paired'));p.add_argument('--id',type=int);p.add_argument('--pair',type=int);p.add_argument('--state',type=int);args=p.parse_args()
    if args.mode=='audit':audit()
    elif args.mode=='recertify':recertify(args.id)
    else:paired(args.pair,args.state)
