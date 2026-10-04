"""Analytic ranges for a fresh R16 signed endpoint Bellman statistic.

Development proposal only. Imports immutable R15 interval primitives read-only.
The bound contains no learned-network norm and no empirical range estimate.
"""
from __future__ import annotations
import pathlib,sys,json,math
import numpy as np
BASE=pathlib.Path('/workspace/scratch/f7129d88c27c/NBO/revisions/2026-10-04-r15')
sys.path.insert(0,str(BASE/'code'))
import costate_bridge as oldbridge
I,pc,tc=oldbridge.I,oldbridge.pc,oldbridge.tc
u=oldbridge.iu
sqrt=oldbridge.isqrt


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

if __name__=='__main__':
    protocol=json.loads((BASE/'MECHANISM_PROTOCOL.json').read_text())
    params,_=oldbridge.verifier.bind_primitives(protocol['primitives'])
    wt=pc.weights(protocol['assessment_steps'])
    diagnostic=json.loads(pathlib.Path('/workspace/scratch/f7129d88c27c/r16-mechanism-proposal/R15_DIAGNOSTIC.json').read_text())
    summary=json.loads((BASE/'results/mechanism/report/MECHANISM_SUMMARY.json').read_text())
    ans={}
    for d in [10,50]:
        support=oldbridge.verifier.population(d)
        oldrows=[json.loads(f.read_text()) for f in (BASE/'results/mechanism').glob(f'trials/d{d}_*/BRIDGE.json')]
        representation=max(z['constants']['arithmetic']['bridge_state_error'] for z in oldrows)
        r=signed_range(d,2048,.1,support,wt,params,2,8.,representation)
        mean=diagnostic['dimensions'][str(d)]['directional_gain']['mean'];var=diagnostic['dimensions'][str(d)]['directional_gain']['sample_variance']
        CT=summary['dimensions'][str(d)]['holding_deficit_upper']+summary['dimensions'][str(d)]['paired_payoff_transfer_upper']
        log=math.log(4/(.01/6))
        r['planning_only']={'historical_directional_mean':mean,'historical_directional_variance':var,'family_alpha':.01,'event_count':6,'rows':[]}
        for n in [4096,8192,16384]:
            eb=math.sqrt(2*var*log/n)+14*r['clip_radius']*log/(3*(n-1))
            rem=mean-.0005-(14*r['clip_radius']*log/(3*(n-1)))-CT-r['clipping_expectation_allowance']
            r['planning_only']['rows'].append(dict(n=n,empirical_bernstein_halfwidth_at_historical_variance=eb,
                legacy_transfer_and_holding=CT,lower_if_historical_mean_variance_recur=mean-eb-CT-r['clipping_expectation_allowance'],
                maximum_variance_compatible_with_0_0005_lower_at_historical_mean=n*max(0,rem)**2/(2*log)))
        ans[str(d)]=r
    out=pathlib.Path('/workspace/scratch/f7129d88c27c/r16-mechanism-proposal/SIGNED_RANGE_PLANNING.json')
    out.write_text(json.dumps(ans,indent=2)+'\n')
    for d,r in ans.items(): print(json.dumps({k:v for k,v in r.items() if k!='spectral_proof'},indent=2))
