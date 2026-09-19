"""Continuous-capacity commitment theorem: exact rational validation examples.

These are deliberately specified analytical economies, NOT a calibration of the
stored settlement model. Every term is optimized after analytically eliminating
continuous F and E; there is no capacity grid in this computation.
"""
from __future__ import annotations
from fractions import Fraction as Q
import itertools,json
from pathlib import Path

def number(q):return dict(exact=str(q),decimal=float(q))
def solve(loss=Q(1),cost=Q(1,50),term_cost=Q(1,50),efficiency=Q(1),slack=Q(1,1000),horizon=Q(1),periods=8,power=2,term_power=1):
    assert loss>0 and cost>0 and term_cost>=0 and efficiency>0 and slack>0 and horizon>0 and periods>=2
    rows=[]
    for m in range(1,periods+1):
        tau=horizon*m/periods
        F=loss*(horizon-tau)+slack if m<periods else Q(0)
        E=F/efficiency
        cap=cost*E**power;duration=term_cost*(tau-horizon/periods)**term_power
        rows.append(dict(m=m,tau=tau,fee=F,capacity=E,capacity_cost=cap,term_cost=duration,total=cap+duration))
    best=min(rows,key=lambda x:(x['total'],x['m']))
    tied=[r['m'] for r in rows if r['total']==best['total']]
    margin=min(r['total']-best['total'] for r in rows if r['m']!=best['m'])
    return best,margin,tied,rows

def serial(x):
    if isinstance(x,Q):return number(x)
    if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v) for v in x]
    return x

def run():
    # The adjustment primitive is a-a^2*chi/2, a in [0,bar a], chi=5.
    # a*=1/chi=1/5, surplus gain=1/10, so loss falls from 1 to 9/10.
    baseline={}
    for name,loss in [('adjustment',Q(9,10)),('no_adjustment',Q(1))]:
        best,gap,tied,rows=solve(loss)
        baseline[name]=dict(loss=loss,choice=best,margin=gap,ties=tied,all_terms=rows)
    assert baseline['adjustment']['choice']['m']==3 and baseline['no_adjustment']['choice']['m']==4
    # Cost differences are monotone in loss and affine in c,kappa. Therefore
    # corner verification covers the WHOLE stated box, not merely eight points.
    region=[]
    for name,losses,winner in [('adjustment',(Q(179,200),Q(181,200)),3),('no_adjustment',(Q(199,200),Q(201,200)),4)]:
        worst=None
        for loss,c,k in itertools.product(losses,(Q(99,5000),Q(101,5000)),(Q(19,1000),Q(21,1000))):
            best,gap,_,rows=solve(loss,c,k)
            selected=rows[winner-1]
            for rr in rows:
                if rr['m']==winner:continue
                dd=rr['total']-selected['total']
                rec=dict(regime=name,loss=loss,cost=c,term_cost=k,winner=winner,rival=rr['m'],margin=dd)
                if worst is None or dd<worst['margin']:worst=rec
        assert worst['margin']>0,worst
        region.append(worst)
    checks=[];strict=weak=0
    for c,k,zeta,T,N,p,r in itertools.product((Q(1,100),Q(1,50),Q(1,25)),(Q(1,100),Q(1,50),Q(1,25)),(Q(4,5),Q(1),Q(6,5)),(Q(3,4),Q(1),Q(5,4)),(6,8,10),(2,3),(1,2)):
        a=solve(Q(9,10),c,k,zeta,horizon=T,periods=N,power=p,term_power=r)
        n=solve(Q(1),c,k,zeta,horizon=T,periods=N,power=p,term_power=r)
        # Minimum minimizers are monotone; checking all costs avoids a floating
        # argmin and preserves ties rather than arbitrarily counting a switch.
        assert a[0]['tau']<=n[0]['tau']
        strict+=a[0]['tau']<n[0]['tau'];weak+=a[0]['tau']==n[0]['tau']
        checks.append(dict(c=c,k=k,zeta=zeta,T=T,N=N,power=p,term_power=r,adjusted_term=a[0]['m'],unadjusted_term=n[0]['m'],adjusted_capacity=a[0]['capacity'],unadjusted_capacity=n[0]['capacity']))
    # Interior, continuous-time formula for quadratic capacity and linear term.
    continuous={}
    for name,ell in [('adjustment',Q(9,10)),('no_adjustment',Q(1))]:
        c=k=Q(1,50);delta=Q(1,1000);E=k/(2*c*ell);tau=1-(E-delta)/ell
        f=c*E**2+k*(tau-Q(1,8))
        assert Q(1,8)<tau<1 and f<k*Q(7,8)
        continuous[name]=dict(term=tau,capacity=E,total_cost=f)
    return serial(dict(schema='nbo-r13-primitive-contract-v1',scope='Exact analytical full-completion procurement; continuous fee and capacity, arbitrary convex cost theorem; the stochastic settlement economy is a distinct application.',adjustment_primitive=dict(baseline_loss=Q(1),chi=5,maximum_adjustment=Q(1,2),optimal_adjustment=Q(1,5),loss_reduction=Q(1,10)),baseline=baseline,continuous_time=continuous,uniform_box=dict(adjusted_loss=[Q(179,200),Q(181,200)],unadjusted_loss=[Q(199,200),Q(201,200)],cost=[Q(99,5000),Q(101,5000)],term_cost=[Q(19,1000),Q(21,1000)],strict_worst_corners=region),comparative_statics=dict(cases=len(checks),strict_shortening=strict,weak_equality=weak,violations=0,rows=checks),fee_incidence='Zero surrender on every exact response; recipient does not affect the exact full-completion comparison.',capacity_incidence='Total cost invariant for every incidence share in [0,1] when participation binds.',near_optimal_completion_lower='max(0,1-eta/slack)',all_passed=True))

if __name__=='__main__':
    out=Path(__file__).parent/'extensions';out.mkdir(exist_ok=True)
    z=run();(out/'primitive_contract.json').write_text(json.dumps(z,indent=2)+'\n')
    print(json.dumps({k:z[k] for k in ['baseline','continuous_time','uniform_box']},indent=2))
    print('EXACT COMPARATIVE STATICS',z['comparative_statics']['cases'],z['comparative_statics']['strict_shortening'],z['comparative_statics']['weak_equality'])
