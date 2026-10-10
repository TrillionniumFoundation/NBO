"""Original expected-cost differences via paid optimal-advantage integration.

The deployed action is fixed before the tighter evaluation query. Common
initial values cancel in expectation, not path by path. No policy-value bound
is substituted for the expectation estimated by the new samples.
"""
from fractions import Fraction as F
from pathlib import Path
import math,itertools,time
import numpy as np
import readout69 as r
q=r.q;I=r.I;B=r.B;old=r.old;k=r.k
import core62 as c
BITS=24;BINBITS=48;LOG=12.;MARGIN=F(1,256)

def local_bounds(T,d,tol):
    bounds=[]
    for t in range(T):
        horizon=T-t;G,_=q.regularity(horizon,d);Gn,_=q.regularity(horizon-1,d)
        transfer=(F(8)+F(11,16)*B*d*Gn+d*G)/2**BITS
        bounds.append(F(tol)+transfer)
    return bounds

def trajectories(policy,initial,randoms,T,target,evaluation_tol):
    N,d=initial.lo.shape;state=I(initial.lo.copy(),initial.hi.copy());tol=old.budget(T,target)[0]
    e=local_bounds(T,d,tol);G=sum(B**t*e[t] for t in range(T))
    evaluator=k.Oracle('adaptive');active=np.ones(N,dtype=bool)
    advantage=I(np.zeros(N),np.zeros(N));cash=I(np.zeros(N),np.zeros(N))
    cashlo=np.zeros(N);cashhi=np.zeros(N);arrays={};dates=[]
    raw_conditional=np.zeros(N);state_expansion=np.zeros(N);ambiguous_width=np.zeros(N);rounding_width=np.zeros(N)
    den=2**BINBITS
    for t in range(T):
        horizon=T-t;state=I(np.maximum(0,state.lo),np.minimum(1,state.hi))
        loobs=np.floor(state.lo*2**BITS)/2**BITS;hiobs=np.floor(state.hi*2**BITS)/2**BITS
        ambiguous=active&np.any(loobs!=hiobs,axis=1);ids=np.flatnonzero(ambiguous)
        if len(ids):
            rem=sum(B**j*e[j] for j in range(t,T))
            advantage.hi[ids]=(I.point(advantage.hi[ids])+q.rat(rem)).hi
            ambiguous_width[ids]=q.up(rem)
            cashlo[ids]=cash.lo[ids];cashhi[ids]=(I.point(cash.hi[ids])+q.rat(B**t*old.support(horizon))).hi
            active[ids]=False
        ids=np.flatnonzero(active);actions=np.full(N,np.nan);observed=np.full((N,d),np.nan)
        current_lo=np.zeros(N);current_hi=np.full(N,q.up(e[t]));true_lo=state.lo.copy();true_hi=state.hi.copy()
        before={key:value for key,value in evaluator.counts.items()}
        if len(ids):
            deployed=policy.solve(loobs[ids],horizon,tol);a=deployed['action'].copy()
            if np.any(deployed['gap']>tol):raise AssertionError('Uncertified deployed action')
            actions[ids]=a;observed[ids]=loobs[ids]
            xx=I(state.lo[ids],state.hi[ids]);aa=I.point(a[:,None])
            if np.any(aa.hi[:,0]>c.capacity(xx).lo):raise AssertionError('True-state capacity')
            middle=xx.midpoint();radius=np.maximum((I.point(middle)-I.point(xx.lo)).hi,(I.point(xx.hi)-I.point(middle)).hi)
            value=evaluator.solve(middle,horizon,evaluation_tol)
            action_value=evaluator.q(middle,a,horizon,evaluation_tol)
            Gv,_=q.regularity(horizon,d);Gn,_=q.regularity(horizon-1,d)
            lips=F(8,d)+F(11,16)*B*Gn+Gv
            expansion=q.rat(lips)*q.n.s.isum(I.point(radius))
            raw=action_value-I(value['lower'],value['upper'])
            enclosure=raw+I(-expansion.hi,expansion.hi)
            lower=np.maximum(0,enclosure.lo);upper=np.minimum(q.up(e[t]),enclosure.hi)
            if np.any(lower>upper):raise AssertionError('Empty advantage intersection')
            current_lo[ids]=lower;current_hi[ids]=upper
            adv=I(advantage.lo[ids],advantage.hi[ids])+q.rat(B**t)*I(lower,upper)
            advantage.lo[ids]=adv.lo;advantage.hi[ids]=adv.hi
            conditional=(I.point(action_value.hi)-I.point(action_value.lo)+I.point(value['upper'])-I.point(value['lower'])).hi
            raw_conditional[ids]+=float(B**t)*conditional
            state_expansion[ids]+=float(B**t)*2*expansion.hi
            rounding_width[ids]+=float(B**t)*np.maximum(0,(I.point(enclosure.hi)-I.point(enclosure.lo)).hi-conditional-2*expansion.hi)
            cost=I(cash.lo[ids],cash.hi[ids])+q.rat(B**t)*c.stage(xx,aa)
            cash.lo[ids]=cost.lo;cash.hi[ids]=cost.hi
            zi=randoms['shock_index'][t,ids]
            shock=I(zi/(16*den)-1/32,(zi+1)/(16*den)-1/32)
            nxt=c.transition(xx,aa,shock);state.lo[ids]=nxt.lo;state.hi[ids]=nxt.hi
        arrays.update({f't{t}_observed':observed,f't{t}_action':actions,
            f't{t}_state_lo':true_lo,f't{t}_state_hi':true_hi,
            f't{t}_advantage_lo':current_lo,f't{t}_advantage_hi':current_hi})
        dates.append(dict(date=t,active=len(ids),new_ambiguous=int(ambiguous.sum()),
            evaluation_q_queries=evaluator.counts['q_queries']-before['q_queries'],
            local_advantage_upper_exact=str(e[t])))
    ids=np.flatnonzero(active)
    if len(ids):
        terminal=I(cash.lo[ids],cash.hi[ids])+q.rat(B**T)*c.terminal(I(state.lo[ids],state.hi[ids]))
        cashlo[ids]=terminal.lo;cashhi[ids]=terminal.hi
    advantage=I(np.maximum(0,advantage.lo),np.minimum(q.up(G),advantage.hi))
    if np.any(advantage.lo>advantage.hi) or np.any(cashlo>cashhi):raise AssertionError('Final endpoint order')
    arrays.update(center_lo=advantage.lo,center_hi=advantage.hi,cost_lo=cashlo,cost_hi=cashhi,
        raw_conditional_width=raw_conditional,state_expansion=state_expansion,
        unresolved_acquisition_width=ambiguous_width,final_arithmetic_width=rounding_width)
    return arrays,dict(local_bounds_exact=list(map(str,e)),center_upper_exact=str(G),
        deployed_local_tolerance=tol,evaluation_tolerance=evaluation_tol,
        ambiguous_paths=int((~active).sum()),dates=dates,policy_work=policy.counts,evaluation_work=evaluator.counts,
        mean_center_enclosure_width=float((I.point(advantage.hi)-I.point(advantage.lo)).hi.mean()),
        mean_raw_conditional_width=float(raw_conditional.mean()),mean_state_expansion=float(state_expansion.mean()),
        mean_unresolved_acquisition_width=float(ambiguous_width.mean()),mean_final_arithmetic_width=float(rounding_width.mean()),
        ledger_scope='Raw component widths are before valid [0,e] intersections; state expansion includes bin width and propagated state arithmetic, not separately identified estimates')

def bounded_interval(lo,hi,support_lo,support_hi,log=LOG):
    N=len(lo);R=F(support_hi)-F(support_lo)
    if N<2 or R<0 or np.any(lo>hi):raise ValueError('Inference inputs')
    lo=np.maximum(float(support_lo),lo);hi=np.minimum(q.up(support_hi),hi)
    meanlo=q.n.s.isum(I.point(lo))/N;meanhi=q.n.s.isum(I.point(hi))/N
    rad=q.rat(R)*I.point(np.nextafter(math.sqrt(log/(2*N)),np.inf))
    lower=max(float(support_lo),float((meanlo-rad).lo));upper=min(q.up(support_hi),float((meanhi+rad).hi))
    return dict(interval=[lower,upper],mean_endpoint_interval=[float(meanlo.lo),float(meanhi.hi)],
        sampling_radius=float(rad.hi),mean_numerical_width=float((meanhi-meanlo).hi),
        support_width_exact=str(R),rows=N,log_upper=log,
        noninferior_upper_margin=bool(upper<=float(MARGIN)),equivalent_at_margin=bool(lower>=-float(MARGIN) and upper<=float(MARGIN)),
        margin_exact=str(MARGIN))

def study(d,T,target,N,out):
    start=time.perf_counter();randoms,initial=old.workload(d,T,N,699001+d*101+T,continuous=True)
    old.archive(out/'randoms.npz',**randoms)
    arms={};lo={};hi={};cashlo={};cashhi={};Gs={}
    for kind in ('adaptive','hat-relu','bernstein4','r67-relu'):
        begin=time.perf_counter()
        if kind=='r67-relu':
            file=ROOT_OLD/f'results67/inference-d{d}-T{T}-paired-s6603-r0/relu-model.json'
            models=k.load_models('relu',old.read(file));fit=dict(source_file=str(file.relative_to(ROOT_OLD)),source_sha256=old.sha(file),new_fit=False)
            policy=k.Oracle('relu',models)
        else:
            models,fit,training=r.fit(d,T,target,6901,kind)
            old.archive(out/(kind+'-training.npz'),**training)
            policy=r.Oracle(kind,models)
        old.save(out/(kind+'-model.json'),models if kind!='r67-relu' else old.read(file))
        pieces=[];accounts=[];chunk=32 if T>=3 else 128
        for first in range(0,N,chunk):
            last=min(first+chunk,N)
            rr={key:(val[first:last] if key=='initial_index' else val[:,first:last]) for key,val in randoms.items()}
            arrays,account=trajectories(policy,I(initial.lo[first:last].copy(),initial.hi[first:last].copy()),rr,T,target,float(F(target)/32))
            pieces.append(arrays);accounts.append(account)
        merged={key:np.concatenate([a[key] for a in pieces]) for key in pieces[0]}
        old.archive(out/(kind+'-paths.npz'),**merged)
        lo[kind]=merged['center_lo'];hi[kind]=merged['center_hi'];cashlo[kind]=merged['cost_lo'];cashhi[kind]=merged['cost_hi']
        Gs[kind]=F(accounts[0]['center_upper_exact'])
        arms[kind]=dict(training=fit,seconds=time.perf_counter()-begin,accounts=accounts,
            trace_sha256=old.sha(out/(kind+'-paths.npz')),model_sha256=old.sha(out/(kind+'-model.json')))
    centered={};raw={}
    for a,b in itertools.combinations(arms,2):
        name=a+'-minus-'+b
        v=I(lo[a],hi[a])-I(lo[b],hi[b]);centered[name]=bounded_interval(v.lo,v.hi,-Gs[b],Gs[a])
        diff=I(cashlo[a],cashhi[a])-I(cashlo[b],cashhi[b]);H=old.support(T)
        raw[name]=dict(interval=old.infer_interval(np.maximum(-q.up(H),diff.lo),np.minimum(q.up(H),diff.hi),2*H),
                       rows=N,method='Retained empirical-Bernstein cash-cost estimator; same new paths')
    return dict(status='returned',d=d,T=T,rows=N,target=target,margin_exact=str(MARGIN),arms=arms,
                centered= centered,raw_cost=raw,random_sha256=old.sha(out/'randoms.npz'),
                seconds=time.perf_counter()-start,family_error=.01,
                scope='Same original continuous economic law and actual frozen callable policies; centered observations are cost differences in expectation, not realized cash-cost differences')
ROOT_OLD=r.ROOT.parent/'2026-10-10-r67'
