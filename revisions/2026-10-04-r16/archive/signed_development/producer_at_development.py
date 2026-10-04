"""Fresh signed occupation-law Bellman assessment of every original R15 NBO.

The joint gain cancels the fitted continuation from every endpoint observation.
This is a policy mechanism certificate, not a critic-versus-Raw risk ranking.
The original negative Cauchy--Schwarz evidence remains unchanged.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
R16=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r15/code'))
import costate_bridge as oldbridge
I,pc,tc=oldbridge.I,oldbridge.pc,oldbridge.tc
u=oldbridge.iu
sqrt=oldbridge.isqrt
from signed_pipeline import read,write,sha,canonical,digest,require,bank,validate_protocol,CANDIDATE_SOURCE,CANDIDATE_EVIDENCE

def signed_range(d,steps,epsilon,support,wt,params,pairs=2,vstar=8.,representation=0.):
    p=params;T=I(p['T']);h=T/steps;kappa=I(p['coupling'])
    sigma=I(p['idiosyncratic_sigma'])/sqrt(I(d))
    B=oldbridge.core.old.coupling(d)
    spectral=tc.spectral_bound(B)
    beta=kappa*I(spectral['norm_upper'])
    gram=I(np.zeros((d,d)))
    for j in range(d): gram=gram+I(B[:,j,None])*I(B[None,:,j])
    pos=pc.sum_axis(pc.sum_axis(I(np.maximum(gram.hi,0.)),axis=1))
    beta_prod=I(min(u(beta),u(kappa*sqrt(pos/d))))
    gamma=2*I(p['CHI'])*pc.exp_i(-I(p['discount'])*T)
    pi=pc.midpoint(wt['M'])/(p['T']/steps)
    alo=pc.up(wt['center'].hi-epsilon);ahi=pc.down(wt['center'].lo+epsilon)
    if np.any(pi<alo) or np.any(pi>ahi): raise ValueError('reference outside action tube')
    delta=np.maximum((I(alo)-I(pi)).absmax(),(I(ahi)-I(pi)).absmax())
    # For any coordinate box point, Jensen/chord inequalities sandwich the
    # separable-log/mean-quadratic concave stage between its uniform endpoints
    # and its tangent upper support at pi.
    ref=wt['A']*pc.log_i(I(pi))-wt['B']*I(pi)-p['adjustment']*wt['A']*I(pi).square()/2
    ends=[]
    for a in [alo,ahi]:
        f=wt['A']*pc.log_i(I(a))-wt['B']*I(a)-p['adjustment']*wt['A']*I(a).square()/2
        ends.append(steps*(f-ref))
    stage_lo=np.minimum(ends[0].lo,ends[1].lo)
    grad=wt['A']*(1/I(pi)-p['adjustment']*I(pi))-wt['B']
    stage_hi=(steps*I(grad.absmax())*I(delta)).hi
    # Uniform action-bridge prefix: candidate's cumulative centered drift
    # through k plus the current postdecision drift/action.
    sup=I(support);cent=sup-oldbridge.column(pc.mean_i(sup,axis=1))
    s0=I(float(oldbridge.norm_upper(cent).max()))
    k=I(np.arange(steps,dtype=float)); t=k*h; tail=(steps-k)*h; n=steps-1-k
    F=pc.exp_i(beta*n*h)
    P=np.zeros(steps);running=I(0.)
    for j in range(steps-2,-1,-1):
        running=beta_prod*I(wt['B'].lo[j+1],wt['B'].hi[j+1])+(1+h*beta)*running
        P[j]=u(running)
    H=s0+(kappa+I(epsilon))*(t+h)+I(representation)
    sd=sqrt(I(d-1))
    CZ=I(P)+gamma*F*kappa*n*h+gamma*(F-1)*(H+sigma*(sqrt(t)+sqrt(tail))*sd)
    AZ=gamma*(F-1)*sigma*(sqrt(t)+sqrt(tail/pairs))
    CQ=CZ+gamma*(H+sigma*sqrt(t)*sd)
    AQ=AZ+gamma*sigma*sqrt(t)
    qC=T*I(delta)*CQ; qA=T*I(delta)*AQ
    lower=(I(stage_lo)-qC-qA*vstar).lo
    upper=(I(stage_hi)+qC+qA*vstar).hi
    L=float(lower.min());U=float(upper.max())
    # The center is an exact binary64 number. Enclose both distances from it.
    center=(L+U)/2
    radius=max(u(I(center)-I(L)),u(I(U)-I(center)))
    tail_slope=float(qA.hi.max())
    tail_allowance=u(2*I(tail_slope)*pc.exp_i(-I(vstar).square()/2)/vstar)
    return dict(schema='nbo-r16-signed-range-development-v1',dimension=d,steps=steps,
        antithetic_pairs=pairs,tail_v=vstar,
        lower_clip=L,upper_clip=U,clip_center=center,clip_radius=radius,
        gaussian_union_events=2,gaussian_tail_slope=tail_slope,
        clipping_expectation_allowance=tail_allowance,
        stage_lower=float(stage_lo.min()),stage_upper=float(stage_hi.max()),
        beta=u(beta),beta_production=u(beta_prod),initial_spread_upper=u(s0),
        maximum_action_distance=float(delta.max()),
        signed_range_has_no_critic_parameter=True,empirical_population_bounds=False,
        spectral_proof=spectral,
        proof_scope='One uniform decision from an independent candidate occupation path; paired endpoint continuation with exact shared innovations and antithetic r pairs. All comparisons concern one fixed finite-grid reference. Continuous-time and numerical allowances are separate.')


def outward_planning_upper(x):
    return u(I(float(x))*(1+I(1e-9))+I(1e-15))


def purpose_seed(root_seed,purpose):
    return int.from_bytes(hashlib.sha256(f'NBO-R16-signed-purpose-v1/{root_seed}/{purpose}'.encode()).digest()[:8],'big')


def selected_constants(actor,critic,d,steps,params,wt,payoff,support):
    """Rebuild parameter and coefficient bounds before drawing a new bank."""
    net=oldbridge.ProtectedCritic(critic,params)
    ac=oldbridge.global_account(d,steps,actor.epsilon,support,wt,payoff,net,params,pairs=2,vstar=8.)
    ar=ac['arithmetic']
    grepr=u(I(params['T'])*I(ac['maximum_action_distance'])*I(ar['true_costate_lipschitz_upper'])*(1+I(params['T'])/steps*I(ac['beta']))*I(ar['accumulated_state_error']))
    values=dict(M_bound=ac['ranges']['M'],M_tail=ac['clipping_expectation_allowances']['M'],
        M_representation=ar['predicted_gain_representation_allowance'],G_representation=grepr,
        accumulated_state_error=ar['accumulated_state_error'],bridge_state_error=ar['bridge_state_error'],
        beta=ac['beta'],state_cap=ar['state_cap'],payoff_transfer=ac['payoff_transfer_upper'],holding_deficit=ac['holding_deficit_upper'],
        true_costate_lipschitz=ar['true_costate_lipschitz_upper'],maximum_action_distance=ac['maximum_action_distance'])
    return net,values,ac


def stage_interval(action,nodes,params,wt):
    steps=len(wt['A'].lo);h=params['T']/steps
    A=I(wt['A'].lo[nodes],wt['A'].hi[nodes]);B=I(wt['B'].lo[nodes],wt['B'].hi[nodes])
    pi=pc.midpoint(wt['M'])[nodes]/h
    mean_action=pc.mean_i(I(action),axis=1)
    logs=pc.log_i(I(action))
    stage=A*(pc.mean_i(logs,axis=1)-pc.log_i(I(pi)))-B*(mean_action-I(pi))
    stage=stage-params['adjustment']*A*(mean_action.square()-I(pi).square())/2
    return stage


def postdecision_intervals(y,action,nodes,params,wt):
    steps=len(wt['A'].lo);h=params['T']/steps;d=y.shape[1]
    pi=pc.midpoint(wt['M'])[nodes]/h;B=oldbridge.core.old.coupling(d)
    c0=I(params['productivity'])-(I(params['idiosyncratic_sigma']).square()+I(params['common_sigma']).square())/2
    f=I(params['coupling'])*oldbridge.tanh_interval(oldbridge.imat(I(y),B))
    shared=I(y)+h*(c0+f)
    return shared-h*I(action),shared-h*I(pi[:,None])


def continuation_difference(xa,xp,nodes,innovations,params,wt,constants,counters):
    """Protected paired scalar difference; same innovations at both endpoints.

    The sample enclosure uses proved state-error bounds, not an empirical
    population range. Only production differences and the terminal quadratic
    difference are accumulated; time-only reference rewards cancel exactly.
    """
    n,d=xa.shape;steps=len(wt['A'].lo);h=params['T']/steps
    B=oldbridge.core.old.coupling(d);kap=params['coupling']
    pi=pc.midpoint(wt['M'])/h
    c0=params['productivity']-(params['idiosyncratic_sigma']**2+params['common_sigma']**2)/2
    def noise(z):return math.sqrt(h)*(params['idiosyncratic_sigma']*z[:,:d]+params['common_sigma']*z[:,d:])
    ya=xa+noise(innovations[0]);yp=xp+noise(innovations[0])
    result=I(np.zeros(n));cap=I(constants['state_cap']);beta=I(constants['beta'])
    state_error=I(np.asarray(constants.get('state_error_rows',np.full(n,constants['accumulated_state_error']))))
    row_abs=I(float(pc.sum_axis(I(np.abs(B)),axis=1).hi.max()))
    dot_error=I(pc.gamma(d+2))*cap*row_abs
    production_round=I(kap)*(I(oldbridge.TANH_ERROR)+dot_error)
    production_round=production_round+I(pc.gamma(4))*I(kap)*(1+I(oldbridge.TANH_ERROR))
    production_error=2*(production_round+beta*state_error)
    max_offsets=int(steps-int(nodes.min()))
    maximum=max(float(np.abs(ya).max()),float(np.abs(yp).max()))
    for offset in range(1,max_offsets):
        j=nodes+offset;active=j<steps;jj=np.minimum(j,steps-1)
        fa=kap*pc.safe_tanh(ya@B.T);fp=kap*pc.safe_tanh(yp@B.T)
        difference=pc.mean_i(I(fa)-I(fp),axis=1)
        difference=I(pc.down(difference.lo-production_error.hi),pc.up(difference.hi+production_error.hi))
        weighted=I(wt['B'].lo[jj],wt['B'].hi[jj])*difference
        result=result+I(np.where(active,weighted.lo,0.),np.where(active,weighted.hi,0.))
        dw=noise(innovations[offset])
        next_a=ya+h*(c0+fa-pi[jj,None])+dw
        next_p=yp+h*(c0+fp-pi[jj,None])+dw
        ya=np.where(active[:,None],next_a,ya);yp=np.where(active[:,None],next_p,yp)
        maximum=max(maximum,float(np.abs(ya).max()),float(np.abs(yp).max()))
    ca=I(ya)-oldbridge.column(pc.mean_i(I(ya),axis=1))
    cp=I(yp)-oldbridge.column(pc.mean_i(I(yp),axis=1))
    gamma=2*I(params['CHI'])*pc.exp_i(-I(params['discount'])*I(params['T']))
    terminal=-gamma/2*pc.mean_i((ca-cp)*(ca+cp),axis=1)
    terminal_error=gamma*(state_error*(I(oldbridge.norm_upper(ca))+I(oldbridge.norm_upper(cp)))+state_error.square())
    terminal=I(pc.down(terminal.lo-terminal_error.hi),pc.up(terminal.hi+terminal_error.hi))
    require(maximum<=constants['state_cap'],'paired future left its arithmetic state cap')
    counters['reference_endpoint_transitions']+=2*int((steps-nodes).sum())
    counters['reference_endpoint_rollouts']+=2*n
    counters['reference_padded_endpoint_rows']+=2*n*max_offsets
    counters['reference_terminal_quadratic_pairs']+=n
    return result+terminal,ya,yp


def endpoint_bank(xa_interval,xp_interval,nodes,root_seed,params,wt,constants,pairs,counters,batch_id):
    xa=pc.midpoint(xa_interval);xp=pc.midpoint(xp_interval)
    er_a=oldbridge.norm_upper(I(pc.radius(xa_interval)))
    er_p=oldbridge.norm_upper(I(pc.radius(xp_interval)))
    initial_radius=np.maximum(er_a,er_p)
    modified=dict(constants,state_error_rows=(I(constants['accumulated_state_error'])+pc.exp_i(I(constants['beta'])*I(params['T']))*I(initial_radius)).hi)
    n,d=xa.shape;steps=len(wt['A'].lo)
    values=[];terminal_a=[];terminal_p=[];hashes=[]
    for pair in range(pairs):
        seed=purpose_seed(root_seed,f'future_batch_{batch_id}_pair_{pair}')
        z=np.random.default_rng(seed).standard_normal((steps,n,d+1))
        hashes.append(dict(batch=batch_id,pair=pair,seed=seed,sha256=hashlib.sha256(z.tobytes()).hexdigest()))
        counters['future_standard_normal_draws']+=z.size
        z=np.clip(z,-10.,10.)
        for sign in [1.,-1.]:
            value,ta,tp=continuation_difference(xa,xp,nodes,sign*z,params,wt,modified,counters)
            values.append(value);terminal_a.append(ta);terminal_p.append(tp)
    all_values=I(np.stack([v.lo for v in values]),np.stack([v.hi for v in values]))
    answer=pc.mean_i(all_values,axis=0)
    return answer,dict(future_hashes=hashes,initial_endpoint_radius=initial_radius,
        terminal_a=np.stack(terminal_a),terminal_pi=np.stack(terminal_p),
        path_difference_lower=all_values.lo,path_difference_upper=all_values.hi)


def execute(protocol,trial_id,method_id,out):
    started=time.perf_counter();protocol=Path(protocol);out=Path(out)
    p=read(protocol);candidates=read(ROOT/p['candidate_inventory']);validate_protocol(p,candidates)
    require(method_id=='nbo','only the original NBO family is assessed')
    chosen=[x for x in candidates['files'] if x['trial_id']==trial_id];require(len(chosen)==1,'undeclared original NBO stream')
    c=chosen[0];d=c['dimension'];stream_seed=c['stream_seed'];noise,key=bank(p,d,stream_seed)
    source=os.environ.get('NBO_R16_SIGNED_SOURCE_COMMIT','uncommitted-development')
    fingerprint=os.environ.get('NBO_R16_SIGNED_FINGERPRINT','uncommitted-development')
    require(source!='uncommitted-development' or os.environ.get('NBO_R16_SIGNED_DEVELOPMENT')=='1','a frozen source identity is required')
    if os.environ.get('NBO_R16_SIGNED_DEVELOPMENT')=='1':noise,key=bank(p,d,stream_seed,development=True)
    metadata=dict(method_id='nbo',trial_id=trial_id,dimension=d,stream_seed=stream_seed,
        numerical_source_commit=source,assessment_fingerprint=fingerprint,protocol_sha256=sha(protocol),
        candidate_source_commit=CANDIDATE_SOURCE,candidate_evidence_commit=CANDIDATE_EVIDENCE,
        checkpoint_sha256=c['sha256'],primitives_sha256=p['design']['primitives_sha256'],noise_seed=noise,noise_key=key)
    out.mkdir(parents=True,exist_ok=True)
    require(not any((out/x).exists() for x in ['RESULT.json','SIGNED.npz','START.json']),'refusing repeated signed assessment')
    write(out/'START.json',dict(metadata,status='before reload, constants and any fresh bank'))
    result=dict(metadata,complete=False,record_type='R16 signed Bellman occupation assessment',training_runs=0,new_stopping_decisions=0,
        old_stopping_unchanged=True,confirmation_independent_of_selection=True,failure=None)
    failure=None
    try:
        checkpoint=ROOT/c['path'];require(sha(checkpoint)==c['sha256'],'selected original weight bytes changed')
        actor,critic,state=oldbridge.core.load_candidate(checkpoint,critic_step=1/p['confirmation']['steps'])
        for field,value in [('source_commit',CANDIDATE_SOURCE),('method_id','nbo'),('dimension',d),('seed',stream_seed),('primitives_sha256',p['design']['primitives_sha256']),('epsilon',.1)]:
            require(state.get(field)==value,'original candidate mismatch: '+field)
        params,p_sha=oldbridge.verifier.bind_primitives(p['design']['primitives']);require(p_sha==p['design']['primitives_sha256'],'wrong primitive identity')
        steps=p['confirmation']['steps'];n=p['confirmation']['paths_per_seed'];batch=p['confirmation']['batch_size'];pairs=p['confirmation']['antithetic_pairs']
        support=oldbridge.verifier.population(d);wt,payoff=oldbridge.verifier.account(d,steps,.1,support)
        net,current,old_account=selected_constants(actor,critic,d,steps,params,wt,payoff,support)
        frozen=read(ROOT/p['signed_constants']);bound=frozen['trials'][trial_id];Gbound=frozen['dimensions'][str(d)]
        for k,v in current.items():require(v<=bound[k],f'fresh proved {k} exceeds its pre-frozen bound')
        got=signed_range(d,steps,.1,support,wt,params,pairs,8.,bound['bridge_state_error'])
        require(got['lower_clip']>=Gbound['lower_clip'] and got['upper_clip']<=Gbound['upper_clip'] and got['clipping_expectation_allowance']<=Gbound['clipping_expectation_allowance'],'fresh signed range exceeds frozen range')
        seeds={name:purpose_seed(noise,name) for name in ['initial_profile','uniform_node','occupation_innovations']}
        nodes=np.random.default_rng(seeds['uniform_node']).integers(steps,size=n)
        counters=defaultdict(int)
        y,actions,initial_ids,occupation_hash,maximum=oldbridge.candidate_occupation(actor,support,nodes,seeds,params,wt,counters)
        require(maximum<=bound['state_cap'],'occupation path outside proved arithmetic cap')
        xa,xp=postdecision_intervals(y,actions,nodes,params,wt)
        va,_=net.jet((nodes+1)*(params['T']/steps),xa);vp,_=net.jet((nodes+1)*(params['T']/steps),xp)
        stage=stage_interval(actions,nodes,params,wt)
        M=steps*(stage+I(va.lo[:,0],va.hi[:,0])-I(vp.lo[:,0],vp.hi[:,0]))
        values=[];records=[];term_a=[];term_p=[];path_lo=[];path_hi=[];rad=[]
        for start in range(0,n,batch):
            stop=min(n,start+batch);part=slice(start,stop)
            val,extra=endpoint_bank(I(xa.lo[part],xa.hi[part]),I(xp.lo[part],xp.hi[part]),nodes[part],noise,params,wt,bound,pairs,counters,start//batch)
            values.append(val);records+=extra['future_hashes'];term_a.append(extra['terminal_a']);term_p.append(extra['terminal_pi'])
            path_lo.append(extra['path_difference_lower']);path_hi.append(extra['path_difference_upper']);rad.append(extra['initial_endpoint_radius'])
        future=I(np.concatenate([v.lo for v in values]),np.concatenate([v.hi for v in values]))
        G=steps*(stage+future);C=M-G
        arrays=dict(nodes=nodes,initial_profile=initial_ids,state=y,action=actions,postdecision_a=pc.midpoint(xa),postdecision_pi=pc.midpoint(xp),
            postdecision_radius=np.concatenate(rad),terminal_a=np.concatenate(term_a,axis=1),terminal_pi=np.concatenate(term_p,axis=1),
            path_difference_lower=np.concatenate(path_lo,axis=1),path_difference_upper=np.concatenate(path_hi,axis=1),
            stage_lower=stage.lo,stage_upper=stage.hi,future_difference_lower=future.lo,future_difference_upper=future.hi)
        for name,value in [('M',M),('C',C),('G',G)]:arrays.update({name:pc.midpoint(value),name+'_lower':value.lo,name+'_upper':value.hi})
        np.savez_compressed(out/'SIGNED.npz',**arrays)
        result.update(complete=True,paths=n,steps=steps,antithetic_pairs=pairs,future_paths_per_bridge=2*pairs,
            frozen_constants=bound,frozen_G_range=Gbound,fresh_proved_constants=current,
            fresh_network_norm_proofs=net.as_dict(),fresh_coupling_proof=got['spectral_proof'],
            raw_path='SIGNED.npz',raw_sha256=sha(out/'SIGNED.npz'),noise_seeds=seeds,future_banks=records,
            occupation_noise_sha256=occupation_hash,initial_profile_sha256=hashlib.sha256(initial_ids.tobytes()).hexdigest(),
            represented_state_sha256=hashlib.sha256(y.tobytes()).hexdigest(),selected_checkpoint_sha256=sha(checkpoint),
            descriptive_means={k:float(arrays[k].mean()) for k in ['M','C','G']},
            numerical_interval_widths={k:dict(maximum=float((arrays[k+'_upper']-arrays[k+'_lower']).max()),mean=float((arrays[k+'_upper']-arrays[k+'_lower']).mean())) for k in ['M','C','G']},
            counters=dict(counters),arithmetic_scope='Interval scalar stage/critic values, two protected forward endpoints and quadratic terminal difference. Complete prefix representation and continuous-payoff allowances are separate.',
            interpretation='G is a direct occupation-law Bellman identity for the fixed returned NBO policy. It does not compare critic risk or establish incremental value over Raw.')
        require(sha(checkpoint)==c['sha256'],'fixed candidate changed during assessment')
    except Exception as exc:
        failure=exc;result['failure']=dict(error_type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());write(out/'FAILURE.json',result['failure'])
    finally:
        result['seconds_before_final_write']=time.perf_counter()-started
        result['timing_authority']='Independent parent WORK.json covers launch through exit and durable evidence; this is additional scientific assessment.'
        write(out/'RESULT.json',result)
    if failure:raise RuntimeError('signed assessment failed; no seed, sample or candidate replacement is permitted') from failure
    return dict(complete=True,trial_id=trial_id,means=result['descriptive_means'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',type=Path,required=True);parser.add_argument('--trial-id',required=True)
    parser.add_argument('--method-id',default='nbo');parser.add_argument('--out',type=Path,required=True)
    print(json.dumps(execute(**vars(parser.parse_args())),indent=2,allow_nan=False))

if __name__=='__main__':main()
