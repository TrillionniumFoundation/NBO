"""Independent finite-menu payoff verification with exact known centering.

One observation is ONE independent antithetic future-path pair for one fixed
query. Methods share that pair; different queries, pairs, stages, and complete
training streams use disjoint declared noise domains. The finite query catalog
and complete finite stream population are exhaustively averaged.

The current reward and a known terminal quadratic difference are taken outside
the random interval. Only the paired continuation residual is clipped. All
positive claims require the separately frozen method-level confidence family.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from menu_curvature import model_constants,post_interval,scalar_curvature,scalar_gradient_gap
from menu_economy import array_hash,canonical_hash,stream_seed
sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r15/code'))
import costate_bridge as bridge
import method_statistics as statistics

I,pc=bridge.I,bridge.pc
sqrt,upper=bridge.isqrt,bridge.iu
METHODS=('nbo_scalar','vector_costate','raw_actor','dpo_actor','raw_saa')
REFERENCE='reference'
TANH_ERROR=2.**-34


def events():
    return [(m+'_gain',m,REFERENCE) for m in METHODS]+[
        ('nbo_minus_'+m,'nbo_scalar',m) for m in METHODS if m!='nbo_scalar']


def noise_coefficients(economy):
    if not all(hasattr(economy,k) for k in ['noise_i','noise_c','terminal_penalty']):
        raise ValueError('stored exact finite-model noise and terminal coefficients required')
    return I(economy.noise_i),I(economy.noise_c)


def exact_current(economy,queries,action):
    a=I(action); mean=pc.mean_i(a,axis=1)
    w=I(np.asarray(queries['utility_weight'],dtype=np.float64).reshape(-1))
    eta=I(np.asarray(queries['adjustment'],dtype=np.float64).reshape(-1))
    return I(economy.A[0])*(w*pc.mean_i(pc.log_i(a),axis=1)-eta*mean.square()/2)-I(economy.W[0])*mean


def quadratic_value_interval(economy,post):
    centered=post-bridge.column(pc.mean_i(post,axis=1))
    return -I(economy.terminal_penalty)*pc.mean_i(centered.square(),axis=1)


def post_float(economy,states,action):
    # A deterministic representative of the already proved postdecision
    # interval avoids BLAS-dependent last bits in the replayed error account.
    return pc.midpoint(post_interval(economy,states,action))


def numerical_account(economy,post_exact,post_executed,constants,gaussian_cap):
    """Global forward arithmetic and Gaussian-clipping expectation account.

    All constants are evaluated outward. The protected polynomial supplies
    a uniform tanh error. Stored binary64 economic coefficients are exact.
    Clipping is charged against the economy's UNCLIPPED Gaussian law.
    """
    d,N=economy.dimension,economy.steps
    h,kappa,penalty=I(economy.h),I(economy.p['coupling']),I(economy.terminal_penalty)
    ni,nc=noise_coefficients(economy); z=I(gaussian_cap)
    noise_amplitude=(ni+nc)*z
    schedule=I(float(np.max(np.abs(economy.schedule[1:]))))
    post_max=I(np.max(post_exact.absmax(),axis=1))
    bound=post_max+(I(abs(economy.c0))+kappa+schedule)*h*(N-1)+noise_amplitude*N
    cap=2*(bound+1)
    diff=post_exact-I(post_executed)
    initial=I(bridge.norm_upper(I(-diff.absmax(),diff.absmax())))
    rows=pc.sum_axis(I(np.abs(economy.B)),axis=1)
    rowmax=I(float(rows.hi.max()))
    dot_error=I(pc.gamma(d+2))*rowmax*cap
    function_error=kappa*(I(TANH_ERROR)+dot_error)+I(pc.gamma(4))*kappa
    noise_round=I(pc.gamma(8))*noise_amplitude
    local=h*function_error+noise_round+I(pc.gamma(12))*(cap+h*(I(abs(economy.c0))+kappa+schedule)+noise_amplitude)
    err=initial+noise_round+I(pc.gamma(4))*(cap+noise_amplitude)
    reward=I(np.zeros(len(post_executed)))
    for j in range(1,N):
        production=constants['beta_production']*err+function_error+I(pc.gamma(d+8))*kappa
        reward=reward+I(economy.W[j])*production
        err=(1+h*constants['beta'])*err+local
    terminal=penalty*err*(2*cap+err)
    magnitude=pc.sum_axis(I(np.abs(economy.W[1:])))*kappa+4*penalty*cap.square()+1
    # The allowance dominates pair averaging, reward accumulation, all scalar
    # multiplications, the two reductions for centered terminal squares, and
    # the final payoff difference. Each reduction has at most d terms.
    scalar_round=I(pc.gamma(20*d+20*N+200))*magnitude
    arithmetic=reward+terminal+scalar_round
    if np.any(err.hi>=bound.lo+1):
        raise ArithmeticError('the asserted deterministic state cap is not self-consistent')

    # E[(G-clip_z G)^2] <= 4 phi(z)/z^3 by integrating u^2 exp(-zu).
    pi_lower=I(float(np.nextafter(math.pi,-math.inf)))
    gaussian_density=pc.exp_i(-z.square()/2)/sqrt(2*pi_lower)
    clipping_second=4*gaussian_density/(z*z*z)
    step_error=sqrt((ni.square()+nc.square())*clipping_second)
    strong=step_error
    clipping_reward=I(0.)
    for j in range(1,N):
        clipping_reward=clipping_reward+I(economy.W[j])*constants['beta_production']*strong
        strong=(1+h*constants['beta'])*strong+step_error
    center=post_exact-bridge.column(pc.mean_i(post_exact,axis=1))
    initial_spread=I(bridge.norm_upper(center))
    S=initial_spread+kappa*h*(N-1)+ni*sqrt(I(N)*(1-I(1)/d))
    clipping=clipping_reward+penalty*strong*(2*S+strong)
    return dict(arithmetic_upper=arithmetic.hi.tolist(),
        gaussian_clipping_bias_upper=clipping.hi.tolist(),
        terminal_state_arithmetic_upper=err.hi.tolist(),
        deterministic_state_cap_upper=cap.hi.tolist(),
        payoff_magnitude_upper=magnitude.hi.tolist(),
        normal_clipping_second_moment_upper=upper(clipping_second),
        normal_clipping_terminal_L2_upper=upper(strong),
        gaussian_cap=float(gaussian_cap),
        protected_tanh_uniform_error=TANH_ERROR,
        arithmetic_contract='outward binary64 inputs; polynomial tanh; bounded dot/reduction error; actual input actions held fixed',
        clipping_scope='expectation transfer from clipped implementation to the stored-coefficient finite economy with unclipped independent Gaussians')


def conditional_range(economy,left_action,right_action,left_post,right_post,q0_center,constants,vstar):
    """One antithetic PAIR per observation, so r=1 in this population bound."""
    d,N=economy.dimension,economy.steps
    h,kappa,gamma=I(economy.h),I(economy.p['coupling']),I(economy.gamma)
    ni,_=noise_coefficients(economy)
    delta=h*sqrt(pc.mean_i((I(left_action)-I(right_action)).square(),axis=1))
    def spread(x):
        return bridge.norm_upper(x-bridge.column(pc.mean_i(x,axis=1)))
    s=I(np.maximum(spread(left_post),spread(right_post)))
    growth=I(1.)
    for j in range(N-1): growth=growth*(1+h*constants['beta'])
    P=I(0.); power=I(1.)
    for j in range(1,N):
        P=P+constants['beta_production']*I(economy.W[j])*power
        power=power*(1+h*constants['beta'])
    # There is only one future Gaussian concentration event, uniformly over
    # the entire straight bridge. The starting query is fixed, not sampled.
    C=P+gamma*growth*kappa*h*(N-1)+gamma*(growth-1)*(s+ni*sqrt(I(N)*(1-I(1)/d)))
    A=gamma*(growth-1)*ni*sqrt(I(N)/d)
    exact_q0=quadratic_value_interval(economy,left_post)-quadratic_value_interval(economy,right_post)
    q0_error=I((exact_q0-q0_center).absmax())
    bound=delta*(C+A*I(vstar))+q0_error
    tail=delta*A*pc.exp_i(-I(vstar).square()/2)/I(vstar)
    equal=np.all(left_action==right_action,axis=1)
    bounds=np.maximum(0.,bound.hi); tails=np.maximum(0.,tail.hi)
    bounds[equal]=0.; tails[equal]=0.
    return dict(bounds=bounds.tolist(),tails=tails.tolist(),
        postdecision_distance_upper=delta.hi.tolist(),
        residual_costate_constant_upper=C.hi.tolist(),
        residual_costate_tail_slope_upper=np.broadcast_to(A.hi,bounds.shape).tolist(),
        exact_quadratic_center_error_upper=q0_error.hi.tolist(),
        antithetic_pairs_per_observation=1,gaussian_union_events=1,
        tail_v=float(vstar),known_quadratic_removed=True,
        source_of_ranges='fixed query/action geometry and economic primitives; no observed future maximum')


def _future_value(economy,x,z,sign):
    d=economy.dimension
    ni,nc=float(economy.noise_i),float(economy.noise_c)
    state=x+sign*(ni*z[:,0,:d]+nc*z[:,0,d:])
    value=np.zeros(len(x))
    for j in range(1,economy.steps):
        production=economy.p['coupling']*pc.safe_tanh(state@economy.B.T)
        value=value+economy.W[j]*production.mean(axis=1)
        noise=sign*(ni*z[:,j,:d]+nc*z[:,j,d:])
        state=state+economy.h*(economy.c0+production-economy.schedule[j])+noise
    centered=state-state.mean(axis=1,keepdims=True)
    return value-economy.terminal_penalty*np.mean(centered*centered,axis=1)


def _menu_geometry(economy,queries,actions,protocol,*,stage):
    """All action-conditional mathematics is evaluated before any final draw."""
    if set(actions)!=set(METHODS): raise ValueError('every registered menu method is required')
    conf=protocol['confirmation']
    pairs=int(conf['antithetic_pairs_per_query'])
    cap=float(conf['gaussian_cap']); vstar=float(conf['tail_v'])
    if pairs<2 or cap!=10. or vstar<=0 or int(stage) not in [1,2,3]:
        raise ValueError('invalid frozen menu confirmation contract')
    states=np.asarray(queries['states'],dtype=np.float64)
    q,d=states.shape
    if d!=economy.dimension or not np.isfinite(states).all(): raise ValueError('query dimension mismatch')
    lower=np.broadcast_to(np.asarray(queries['lower'],dtype=np.float64),(q,d))
    high=np.broadcast_to(np.asarray(queries['upper'],dtype=np.float64),(q,d))
    acts={m:np.asarray(actions[m],dtype=np.float64) for m in METHODS}
    acts[REFERENCE]=np.full((q,d),economy.schedule[0],dtype=np.float64)
    for name,a in acts.items():
        if a.shape!=(q,d) or not np.isfinite(a).all() or np.any(a<lower) or np.any(a>high):
            raise ValueError('infeasible or incomplete menu action: '+name)
    constants=model_constants(economy)
    posts={m:post_interval(economy,states,a) for m,a in acts.items()}
    executed={m:pc.midpoint(posts[m]) for m in acts}
    current={m:exact_current(economy,queries,a) for m,a in acts.items()}
    numerical={m:numerical_account(economy,posts[m],executed[m],constants,cap) for m in acts}
    centers={}
    qref=quadratic_value_interval(economy,posts[REFERENCE])
    for m in METHODS:
        diff=quadratic_value_interval(economy,posts[m])-qref
        center=pc.midpoint(diff)
        center[np.all(acts[m]==acts[REFERENCE],axis=1)]=0.
        centers[m]=center
    centers[REFERENCE]=np.zeros(q)
    event_records={}
    for name,left,right in events():
        center=I(centers[left])-I(centers[right])
        known=current[left]-current[right]+center
        range_account=conditional_range(economy,acts[left],acts[right],posts[left],posts[right],center,constants,vstar)
        nl,nr=numerical[left],numerical[right]
        arithmetic=I(nl['arithmetic_upper'])+I(nr['arithmetic_upper'])
        # Direct differences are formed from the same two stored gains.
        # Retain their complete reference arithmetic rather than assuming
        # cancellation of separately rounded subtraction operations.
        if right!=REFERENCE:
            arithmetic=arithmetic+2*I(numerical[REFERENCE]['arithmetic_upper'])
        magnitude=(I(nl['payoff_magnitude_upper'])+I(nr['payoff_magnitude_upper'])+
            I(numerical[REFERENCE]['payoff_magnitude_upper'])*2+I(centers[left]).absmax()+I(centers[right]).absmax())
        arithmetic=arithmetic+I(pc.gamma(12))*magnitude
        clipping=I(nl['gaussian_clipping_bias_upper'])+I(nr['gaussian_clipping_bias_upper'])
        same=np.all(acts[left]==acts[right],axis=1)
        num=arithmetic.hi.copy(); clip=clipping.hi.copy()
        num[same]=0.; clip[same]=0.
        offset_lo=known.lo.copy();offset_hi=known.hi.copy()
        offset_lo[same]=0.;offset_hi[same]=0.
        event_records[name]=dict(left=left,right=right,range=range_account,
            known_offset_lower=offset_lo.tolist(),known_offset_upper=offset_hi.tolist(),
            arithmetic_upper=num.tolist(),gaussian_clipping_bias_upper=clip.tolist(),
            exact_identity_query_count=int(same.sum()))
    account=dict(calibration=economy.calibration['id'],dimension=d,stage=int(stage),
        continuation_sha256=economy.continuation_sha256,query_catalog_sha256=queries['catalog_sha256'],
        protocol_sha256=canonical_hash(protocol),query_count=q,pairs_per_query=pairs,
        independent_observations=q*pairs,methods=list(METHODS),events=event_records,
        action_sha256={m:array_hash(a) for m,a in acts.items()},
        quadratic_center_sha256={m:array_hash(centers[m]) for m in METHODS},
        numerical_accounts=numerical,spectral_certificate=constants['spectral'])
    return account,acts,executed,centers


def verify_event_accounts(economy,queries,actions,protocol,*,stage):
    """Deterministically reconstruct every primary geometric/numerical field.

    No payoff sample, empirical moment, or random number generator is read.
    Report assembly must compare every returned field with the saved record
    and each action/center hash with the corresponding durable raw array.
    """
    return _menu_geometry(economy,queries,actions,protocol,stage=stage)[0]


def verify_arrays(economy,queries,actions,protocol,*,seed,stage,batch_rows=1024):
    """Return (JSON-serializable record, complete raw ndarray mapping)."""
    started=time.perf_counter()
    if int(seed) not in protocol['training_streams']['seeds']:
        raise ValueError('undeclared complete training stream')
    if int(batch_rows)<1: raise ValueError('positive execution batch required')
    account,acts,executed,centers=_menu_geometry(economy,queries,actions,protocol,stage=stage)
    q,d,pairs=account['query_count'],economy.dimension,account['pairs_per_query']
    cap=float(protocol['confirmation']['gaussian_cap'])
    arrays={m:np.empty((q,pairs),dtype=np.float64) for m in METHODS}
    noise_seed=stream_seed(seed,economy.calibration['id'],d,'independent_final_payoff',stage)
    generator=np.random.Generator(np.random.PCG64(noise_seed))
    noise_sha=hashlib.sha256();total=q*pairs
    for start in range(0,total,int(batch_rows)):
        stop=min(total,start+int(batch_rows)); ids=np.arange(start,stop)//pairs
        z=generator.standard_normal((stop-start,economy.steps,d+1))
        noise_sha.update(z.astype('<f8',copy=False).tobytes())
        z=np.clip(z,-cap,cap)
        vals={}
        for m in acts:
            vals[m]=(_future_value(economy,executed[m][ids],z,1.)+
                     _future_value(economy,executed[m][ids],z,-1.))/2
        for m in METHODS:
            residual=vals[m]-vals[REFERENCE]-centers[m][ids]
            arrays[m].reshape(-1)[start:stop]=residual
    raw={f'residual_{m}':a for m,a in arrays.items()}
    for m in METHODS:
        raw[f'actions_{m}']=acts[m]
        raw[f'quadratic_center_{m}']=centers[m]
    record=dict(account,schema='nbo-r16-menu-confirmation-v1',complete=True,stream_seed=int(seed),
        noise_seed=noise_seed,noise_sha256=noise_sha.hexdigest(),
        noise_domain=f'NBO-R16-menu-v1/{seed}/{economy.calibration["id"]}/{d}/independent_final_payoff/{stage}',
        sample_layout='query-major, pair-minor; each row contains all dates and d+1 shocks; opposite signs form one observation',
        independence='distinct pairs, queries, streams and stages; common innovations across methods only',
        confidence_scope='No per-stream endpoint; pool every declared stream for the method-level family',
        confirmation_independent_of_training_and_selection=True,
        gaussian_law='unclipped independent standard normals; clip10 implementation with explicit expectation transfer',
        work=dict(elapsed_seconds=time.perf_counter()-started,
            independent_antithetic_pairs=total,gaussian_scalars=total*economy.steps*(d+1),
            continuation_paths=2*total*len(acts),
            simulator_transitions=2*total*len(acts)*economy.steps,
            protected_tanh_rows=2*total*len(acts)*(economy.steps-1),
            current_query_postdecision_rows=q*len(acts),batch_rows=int(batch_rows)))
    return record,raw


def event_samples(record,arrays,event):
    item=record['events'][event]; left,right=item['left'],item['right']
    x=np.asarray(arrays['residual_'+left],dtype=np.float64)
    if right!=REFERENCE:x=x-np.asarray(arrays['residual_'+right],dtype=np.float64)
    expected=(record['query_count'],record['pairs_per_query'])
    if x.shape!=expected or not np.isfinite(x).all():raise ValueError('incomplete independent pair array')
    b=np.asarray(item['range']['bounds'])[:,None]
    return np.clip(x,-b,b),int(np.count_nonzero(x!=np.clip(x,-b,b)))


def pooled_event(records_and_arrays,protocol,event):
    """Complete 16-stream method event, preserving fixed-query weights."""
    confidence=protocol['confidence']
    budget=statistics.ConfidenceBudget(float(confidence['alpha']),int(confidence['event_count']))
    seeds=list(protocol['training_streams']['seeds'])
    keyed={int(record['stream_seed']):(record,arrays) for record,arrays in records_and_arrays}
    if set(keyed)!=set(seeds) or len(keyed)!=len(records_and_arrays):
        raise ValueError('complete exactly-once declared menu streams required')
    identities={(r['calibration'],r['dimension'],r['stage'],r['continuation_sha256'],r['query_catalog_sha256'],
                 r['protocol_sha256'],r['query_count'],r['pairs_per_query']) for r,a in keyed.values()}
    if len(identities)!=1: raise ValueError('mixed menu models, catalogs, stages, or sample counts')
    identity=next(iter(identities))
    if identity[5]!=canonical_hash(protocol): raise ValueError('menu protocol changed')
    if identity[7]!=int(protocol['confirmation']['antithetic_pairs_per_query']):
        raise ValueError('unregistered primary confirmation count')
    if 'query_catalogs' in protocol:
        from menu_economy import fixed_queries
        registered=fixed_queries(protocol,identity[1])
        if identity[4]!=registered['catalog_sha256'] or identity[6]!=len(registered['states']):
            raise ValueError('unregistered fixed query population')
    vals={}; bounds={}; biases={}; tails={}; noise={}; known=[]; clipped=0
    for seed in seeds:
        r,a=keyed[seed]
        if not r['complete'] or not r['confirmation_independent_of_training_and_selection']:
            raise ValueError('incomplete or nonindependent menu confirmation')
        expected_seed=stream_seed(seed,r['calibration'],r['dimension'],'independent_final_payoff',r['stage'])
        expected_domain=f"NBO-R16-menu-v1/{seed}/{r['calibration']}/{r['dimension']}/independent_final_payoff/{r['stage']}"
        if r['noise_seed']!=expected_seed or r['noise_domain']!=expected_domain:
            raise ValueError('confirmation noise belongs to another trial or stage')
        x,count=event_samples(r,a,event); item=r['events'][event]
        vals[seed]=x.ravel(); clipped+=count
        bounds[seed]=max(item['range']['bounds'])
        biases[seed]=upper(pc.mean_i(I(item['arithmetic_upper'])+I(item['gaussian_clipping_bias_upper'])))
        tails[seed]=upper(pc.mean_i(I(item['range']['tails'])))
        noise[seed]=r['noise_domain']+':'+r['noise_sha256']
        known.append(pc.mean_i(I(item['known_offset_lower'],item['known_offset_upper'])))
    result=statistics.finite_stream_mean(vals,declared_seeds=seeds,noise_keys=noise,
        bounds=bounds,biases=biases,clipping_tails=tails,event_alpha=budget.event_alpha,
        confirmation_independent_of_selection=True)
    offset=pc.mean_i(I(np.asarray([k.lo for k in known]),np.asarray([k.hi for k in known])))
    lo=I(result['lower'])+offset; hi=I(result['upper'])+offset
    result.update(event=event,lower=float(lo.lo),upper=float(hi.hi),
        known_offset_interval=[float(offset.lo),float(offset.hi)],
        mean=result['raw_mean']+float(pc.midpoint(offset)),
        query_count=next(iter(identities))[6],pairs_per_query=next(iter(identities))[7],
        sampling_unit='one independent antithetic future pair within one fixed query and stream',
        fixed_query_and_complete_stream_average=True,clipped_paths=clipped,
        confidence_family=budget.as_dict(),economic_margin=float(confidence['economic_margin']),
        economic_decision=statistics.economic_decision(float(lo.lo),float(hi.hi),float(confidence['economic_margin'])))
    return result


def _scalar_query(candidate):
    task=candidate['task']
    state=np.asarray(candidate['state'],dtype=np.float64).reshape(1,-1)
    query=dict(states=state,catalog_sha256=canonical_hash(candidate))
    for key in ['utility_weight','adjustment','lower','upper']:
        query[key]=np.asarray([[float(task[key])]])
    return query


def _scalar_assessment(economy,query,scalar_candidate,protocol,*,seed,batch_rows=1024,raw_arrays=None):
    """One protected whole-segment accuracy event, on a fresh finite bank.

    A centered or boundary-adjusted secant estimates the true derivative.
    A proved second-derivative bound transfers the secant to the derivative;
    global semiconcavity then bounds the optimum over every scalar action.
    """
    began=time.perf_counter(); cfg=protocol['scalar_accuracy']
    candidate=scalar_candidate
    if int(seed) not in protocol['training_streams']['seeds']:
        raise ValueError('undeclared scalar training stream')
    if 'query_catalogs' in protocol:
        from menu_economy import scalar_query_spec
        specification=scalar_query_spec(protocol,economy)
        for key,value in specification.items():
            if canonical_hash(candidate.get(key))!=canonical_hash(value):
                raise ValueError('scalar candidate is outside the registered query class: '+key)
        if candidate.get('seed')!=int(seed) or candidate.get('stage')!=3:
            raise ValueError('scalar candidate belongs to another training stream or stage')
    if query is None: query=_scalar_query(candidate)
    y=np.asarray(query['states'],dtype=np.float64).reshape(1,-1)
    if y.shape!=(1,economy.dimension):raise ValueError('one registered scalar query required')
    if candidate.get('continuation_sha256',economy.continuation_sha256)!=economy.continuation_sha256:
        raise ValueError('scalar candidate belongs to another continuation')
    left=np.asarray(candidate['a_left'],dtype=np.float64).reshape(-1)
    right=np.asarray(candidate['a_right'],dtype=np.float64).reshape(-1)
    s=float(candidate['candidate_s'])
    if not 0<=s<=1 or left.shape!=y.shape[1:] or right.shape!=left.shape:
        raise ValueError('invalid scalar intervention candidate')
    if np.any(np.minimum(left,right)<query['lower'][0,0]) or np.any(np.maximum(left,right)>query['upper'][0,0]):
        raise ValueError('scalar class lies outside the economic action set')
    delta=float(cfg['secant_halfwidth']); pairs=int(cfg['antithetic_pairs'])
    if not 0<delta<.5 or pairs<2:raise ValueError('invalid frozen scalar power design')
    sl=max(0.,s-delta); sr=min(1.,s+delta)
    if sr<=sl:raise ValueError('empty scalar secant')
    curvature=scalar_curvature(economy,y[0],left,right,
        utility_weight=float(query['utility_weight'][0,0]),adjustment=float(query['adjustment'][0,0]))
    constants=model_constants(economy)
    acts={k:(left+t*(right-left)).reshape(1,-1) for k,t in [('left',sl),('right',sr),('candidate',s)]}
    posts={k:post_interval(economy,y,a) for k,a in acts.items()}
    executed={k:pc.midpoint(posts[k]) for k in acts}
    current={k:exact_current(economy,query,a) for k,a in acts.items()}
    cap=float(protocol['confirmation']['gaussian_cap']); vstar=float(protocol['confirmation']['tail_v'])
    numerics={k:numerical_account(economy,posts[k],executed[k],constants,cap) for k in ['left','right']}
    base=quadratic_value_interval(economy,posts['right'])-quadratic_value_interval(economy,posts['left'])
    center=float(pc.midpoint(base)[0])
    known=current['right']-current['left']+I(center)
    ra=conditional_range(economy,acts['right'],acts['left'],posts['right'],posts['left'],I(center),constants,vstar)

    # The mathematical scalar segment has exact real affine actions. Its
    # binary64 evaluation is enclosed separately, even though its error is tiny.
    action_round={}
    action_radii={}; action_sup_radii={}
    for name,t in [('left',sl),('right',sr),('candidate',s)]:
        exact_action=I(left)+I(t)*(I(right)-I(left))
        action_error=exact_action-I(acts[name][0])
        action_radii[name]=upper(I(bridge.norm_upper(action_error)))
        action_sup_radii[name]=float(np.max(action_error.absmax()))
    growth=I(1.); P=I(0.)
    for j in range(1,economy.steps):
        P=P+constants['beta_production']*I(economy.W[j])*growth
        growth=growth*(1+I(economy.h)*constants['beta'])
    q_bound=(P+I(economy.gamma)*growth*(I(curvature['terminal_dispersion_moment_upper'])+
        I(economy.h)*I(max(action_radii.values()))))
    action_expansion=I(max(action_sup_radii.values()))
    lower_action=I(float(min(left.min(),right.min())))-action_expansion
    upper_action=I(float(max(left.max(),right.max())))+action_expansion
    if lower_action.lo<=0: raise ArithmeticError('affine action enclosure reaches the log boundary')
    stage_lip=I(economy.A[0])*(I(float(query['utility_weight'][0,0]))/lower_action+
        I(float(query['adjustment'][0,0]))*upper_action)+I(economy.W[0])
    for name,t in [('left',sl),('right',sr),('candidate',s)]:
        rounding=I(action_radii[name])
        action_round[name]=upper((stage_lip+I(economy.h)*q_bound)*rounding)

    noise_seed=stream_seed(seed,economy.calibration['id'],economy.dimension,'independent_scalar_accuracy',3)
    noise_domain=f'NBO-R16-menu-v1/{seed}/{economy.calibration["id"]}/{economy.dimension}/independent_scalar_accuracy/3'
    if raw_arrays is None:
        if int(batch_rows)<1: raise ValueError('positive scalar execution batch required')
        gen=np.random.Generator(np.random.PCG64(noise_seed)); hs=hashlib.sha256()
        residual=np.empty(pairs)
        for first in range(0,pairs,int(batch_rows)):
            last=min(pairs,first+int(batch_rows)); count=last-first
            z=gen.standard_normal((count,economy.steps,economy.dimension+1))
            hs.update(z.astype('<f8',copy=False).tobytes()); z=np.clip(z,-cap,cap)
            values={}
            for name in ['left','right']:
                x=np.repeat(executed[name],count,axis=0)
                values[name]=(_future_value(economy,x,z,1.)+_future_value(economy,x,z,-1.))/2
            residual[first:last]=values['right']-values['left']-center
        digest=hs.hexdigest()
    else:
        residual=np.asarray(raw_arrays['scalar_secant_residual'],dtype=np.float64)
        if residual.shape!=(pairs,) or not np.isfinite(residual).all():
            raise ValueError('incomplete or nonfinite saved scalar pair array')
        if int(np.asarray(raw_arrays['noise_seed']).item())!=noise_seed or str(np.asarray(raw_arrays['noise_domain']).item())!=noise_domain:
            raise ValueError('saved scalar noise belongs to another frozen trial')
        digest=str(np.asarray(raw_arrays['noise_sha256']).item())
        if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('invalid scalar noise digest')
    nr,nl=numerics['right'],numerics['left']
    numerical=I(nr['arithmetic_upper'][0])+I(nl['arithmetic_upper'][0])
    numerical=numerical+I(pc.gamma(12))*(I(nr['payoff_magnitude_upper'][0])+I(nl['payoff_magnitude_upper'][0])+abs(center))
    clipping=I(nr['gaussian_clipping_bias_upper'][0])+I(nl['gaussian_clipping_bias_upper'][0])
    bias=numerical+clipping+I(action_round['left'])+I(action_round['right'])
    budget=statistics.ConfidenceBudget(float(cfg['alpha']),int(cfg['event_count']))
    endpoint=statistics.empirical_bernstein(residual,bound=ra['bounds'][0],
        event_alpha=budget.event_alpha,bias=upper(bias),clipping_tail=ra['tails'][0])
    width=I(sr)-I(sl)
    secant=I(endpoint['lower'],endpoint['upper'])+I(known.lo[0],known.hi[0])
    secant=secant/width
    derivative_error=(I(curvature['absolute_second_derivative_upper'])*
        ((I(s)-I(sl)).square()+(I(sr)-I(s)).square())/(2*width))
    gradient=secant+I(-upper(derivative_error),upper(derivative_error))
    gap=scalar_gradient_gap([float(gradient.lo),float(gradient.hi)],s,curvature)
    deployed_gap=upper(I(gap['gap_upper'])+I(action_round['candidate']))
    result=dict(schema='nbo-r16-scalar-accuracy-v1',complete=True,
        calibration=economy.calibration['id'],dimension=economy.dimension,stream_seed=int(seed),
        continuation_sha256=economy.continuation_sha256,protocol_sha256=canonical_hash(protocol),
        candidate=candidate,curvature=curvature,secant_parameters=[sl,sr],
        independent_antithetic_pairs=pairs,range=ra,known_secant_offset=[float(known.lo[0]),float(known.hi[0])],
        payoff_difference_interval=endpoint,secant_interval=[float(secant.lo),float(secant.hi)],
        secant_to_derivative_bias_upper=upper(derivative_error),
        gradient_interval=[float(gradient.lo),float(gradient.hi)],
        scalar_optimum_gap=gap,implemented_candidate_gap_upper=deployed_gap,
        numerical_action_roundoff_allowances=action_round,numerical_accounts=numerics,
        accuracy_margin=float(cfg['economic_margin']),accuracy_at_margin=deployed_gap<=float(cfg['economic_margin']),
        confidence_family=budget.as_dict(),noise_seed=noise_seed,noise_sha256=digest,
        noise_domain=noise_domain,
        scope='entire prescribed scalar action segment, fixed high-dimensional state, stored-coefficient finite economy; no full-adapted or continuous-time near-optimality claim',
        work=dict(elapsed_seconds=time.perf_counter()-began,independent_pairs=pairs,
            continuation_paths=4*pairs,simulator_transitions=4*pairs*economy.steps,
            gaussian_scalars=pairs*economy.steps*(economy.dimension+1)))
    return result,dict(scalar_secant_residual=residual,noise_seed=np.asarray(noise_seed,dtype=np.uint64),
        noise_domain=np.asarray(noise_domain),noise_sha256=np.asarray(digest))


def verify_scalar(economy,query,scalar_candidate,protocol,*,seed,batch_rows=1024):
    """Execute the independent registered scalar bank and protect its endpoint."""
    return _scalar_assessment(economy,query,scalar_candidate,protocol,seed=seed,batch_rows=batch_rows)


def replay_scalar(economy,query,scalar_candidate,protocol,*,seed,raw_arrays):
    """Rebuild every scalar scientific field from immutable saved residuals.

    This branch neither initializes a random generator nor runs a continuation
    path. Geometry, range, all arithmetic and population-tail allowances,
    moments, concentration, secant, derivative, curvature and global gap are
    recalculated using the same frozen account as the confirming process.
    Only the execution-time work record is excluded from the returned mapping.
    """
    result,_=_scalar_assessment(economy,query,scalar_candidate,protocol,seed=seed,raw_arrays=raw_arrays)
    result.pop('work')
    return result
