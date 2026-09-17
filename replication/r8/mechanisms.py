"""Reoptimized, two-regime interventions on the unaltered R7 dynamic target.

Parameter interventions alter economic primitives; they are not data-based
causal effects. Selected policies are independently replayed after each solve.
"""
from __future__ import annotations
from dataclasses import replace
import gc, time
from model import Model, Specification, old, np, save, OUT


def change_rewards(mix, *, tilt=0., normalization=1., settlement=1.):
    prev=mix.spec
    for e in mix.e:
        u=e.states[:,0,None]
        for k in [e.common]+e.extra:
            k.base+=(tilt-prev.cardinal_tilt)*(u-2)*k.duration
            k.base+=(normalization-prev.normalization_scale)/(1-u)*k.duration
            k.base+=(settlement-prev.settlement_scale)*k.settlement
    mix.terminal=settlement*old.terminal(mix.e[0].states)
    mix.spec=replace(prev,cardinal_tilt=tilt,normalization_scale=normalization,settlement_scale=settlement)


def calculate(mix,label,t,d,baseline=None):
    row=dict(intervention=label,lambda_=t,d=d,specification=mix.spec.__dict__,classes={})
    for adj in (True,False):
        pair=mix.class_pair(t,d,adj)
        for sign,item in pair.items():
            pol=item['policy'];direct=mix.direct(pol,t,d);features=mix.features(pol,t)
            weights=np.array([1.,mix.spec.normalization_scale,mix.spec.cardinal_tilt,d,-mix.spec.cost,mix.spec.settlement_scale])
            err=max(float(abs(direct-item['value']).max()),float(abs(np.einsum('f,fns->ns',weights,features)-direct).max()))
            assert err<2e-11
            key=('adj' if adj else 'fixed')+'_'+sign
            rec=dict(value=float(direct[0,mix.center]),features=features[:,0,mix.center],replay_error=err)
            if baseline is not None:
                replay=mix.direct(baseline[key],t,d)
                rec.update(baseline_policy_value=float(replay[0,mix.center]),reoptimization_gain=float(direct[0,mix.center]-replay[0,mix.center]))
                assert rec['reoptimization_gain']>=-2e-11
            row['classes'][key]=rec
    C=row['classes']
    row['delta_adjusted']=C['adj_positive']['value']-C['adj_nonpositive']['value']
    row['delta_fixed']=C['fixed_positive']['value']-C['fixed_nonpositive']['value']
    row['relative_option']=row['delta_adjusted']-row['delta_fixed']
    # Difference of optimized moments: an accounting/envelope object only.
    row['relative_option_features']=(C['adj_positive']['features']-C['adj_nonpositive']['features']-C['fixed_positive']['features']+C['fixed_nonpositive']['features'])
    return row


def run():
    start=time.perf_counter();mix=Model();rows=[];baselines={}
    for t,d in ((.125,.425),(.25,.45)):
        b={}
        for adj in (True,False):
            for sign,item in mix.class_pair(t,d,adj).items():
                b[('adj' if adj else 'fixed')+'_'+sign]=item['policy']
        baselines[t,d]=b
    cases=[('baseline',0.,1.,1.)]
    cases += [(f'cardinal_tilt_{a:g}',a,1.,1.) for a in (-1.,-.25,.25,1.,2.)]
    cases += [(f'normalization_scale_{b:g}',0.,b,1.) for b in (0.,.5,1.5,2.)]
    cases += [(f'settlement_scale_{g:g}',0.,1.,g) for g in (0.,.5,2.)]
    for label,a,b,g in cases:
        change_rewards(mix,tilt=a,normalization=b,settlement=g)
        for t,d in baselines:
            rows.append(calculate(mix,label,t,d,baselines[t,d]))
    change_rewards(mix)
    for t,d in ((.125,0.),(.125,.4),(.125,.45),(.125,1.),(0.,.425),(.25,.425),(.5,.425),(1.,.425)):
        rows.append(calculate(mix,'duration_or_covariance_contract',t,d,baselines[.125,.425]))
    # An actual zero-covariance law, not merely lambda=1/2: a mixture of
    # endpoint correlations is a different non-Gaussian four-shock law.
    del mix;gc.collect();mix=Model(Specification(correlation_low=0.,correlation_high=0.))
    for t,d in baselines:
        rows.append(calculate(mix,'zero_covariance_law',t,d,baselines[t,d]))
    out=dict(rows=rows,elapsed_seconds=time.perf_counter()-start,
        feature_order=['reference_consumption_exposure','cardinal_baseline','preference_tilt_exposure','discounted_operating_duration','quadratic_adjustment_effort','liquidation_payoff'],
        interpretation='reoptimized model counterfactuals, not identified causal channels; no-adjustment preference state remains stochastic',
        total_class_solves=4*len(rows),max_replay_error=max(v['replay_error'] for r in rows for v in r['classes'].values()))
    save('mechanisms.json',out)
    for r in rows:print(r['intervention'],r['lambda_'],r['d'],r['delta_adjusted'],r['delta_fixed'],r['relative_option'],flush=True)
    return out
if __name__=='__main__':run()
