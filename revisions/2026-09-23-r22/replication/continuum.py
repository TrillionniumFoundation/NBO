"""Directed unequal-initialization Jensen audit; no equal-slope assertions."""
from pathlib import Path
import json,sys
from fractions import Fraction as F
import numpy as np
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r22'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r21/replication'))
from audit import I,Q,exp,sqrt,pi,stack,add_reduce,MASS,PEXIT,PTAIL,hess_bounds,tanh

def read(p):return json.loads(p.read_text())
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def span(v):return I(float(np.max(v.hi)))-I(float(np.min(v.lo)))

def general_jensen(actors,certificates,H):
    n=16; assert len(actors)==4
    b=I(np.array([d['b'] for d in actors]));s=I(np.array([d['s'] for d in actors]));th=I(np.array([d['theta'] for d in actors]))
    assert all(len(d['b'])==n for d in actors)
    # The policy metadata decimals specify the exact initial states.
    u=stack([Q(str(d['u0'])) for d in actors]);theta_prefix=I(np.zeros(4))
    prefspan=[];consumptionspan=[];effortspan=[];gaps=[]
    bound=Q('2.425')
    for j in range(n):
        du=I(max(float(span(u+theta_prefix).hi),float(span(u+theta_prefix+th[:,j]/n).hi)))
        arg=I(max(float(span(b[:,j]-s[:,j]*bound).hi),float(span(b[:,j]+s[:,j]*bound).hi)))
        dc=Q('.3')*tanh(arg/4);dt=span(th[:,j])
        gap=(I(H[0])*du**2+2*I(H[1])*du*dc+I(H[2])*dc.square()+2*dt.square())/8
        prefspan.append(float(du.hi));consumptionspan.append(float(dc.hi));effortspan.append(float(dt.hi));gaps.append(gap)
        theta_prefix=theta_prefix+th[:,j]/n
    factor_tail=2*exp(-Q(32))/(8*sqrt(2*pi()))
    running=add_reduce(MASS*stack(gaps))+6*(PTAIL+factor_tail)*add_reduce(MASS)
    rs=[c['reserve_interval'] for c in certificates]
    rmin=min(r[0] for r in rs);assert rmin>.5
    dr=I(max(r[1] for r in rs))-I(rmin);duT=span(u+theta_prefix)
    terminal=exp(-Q('.04'))*(Q('.005')*duT.square()+Q('.0125')/I(rmin).square()*dr.square())
    gamma=running+terminal+16*PEXIT
    return {'bound':float(gamma.hi),'running':float(running.hi),'terminal':float(terminal.hi),
            'preference_span_by_slab':prefspan,'consumption_span_by_slab':consumptionspan,
            'theta_span_by_slab':effortspan,'factor_tail_probability_upper':float(factor_tail.hi),
            'preference_tail_probability_upper':float(PTAIL.hi),'log_factor_cutoff':'97/40',
            'identical_initial_slopes':all(d['s']==actors[0]['s'] for d in actors),
            'identical_initial_drifts':all(d['theta']==actors[0]['theta'] for d in actors),
            'arithmetic':'outward binary64 rational-Taylor intervals; no statistical confidence bound'}

def main():
    H=hess_bounds();rows=[];crossed=[]
    for seed in (22000,22100,22200):
        base=REV/f'results/crossed/seed{seed}'
        ds=[read(base/f'vertex{v}/initial_actor.json') for v in range(4)]
        cs=[read(base/f'vertex{v}/initial_certificate.json') for v in range(4)]
        gamma=general_jensen(ds,cs,H)
        for rep in ('neural','direct'):
            for opt in ('adam','lbfgsb'):
                rr=[read(base/f'vertex{v}/{rep}_{opt}/record.json') for v in range(4)]
                final=[r['delivered_certificate'] for r in rr]
                B=max(float((I(c['optimal_value_upper'])-I(c['value_interval'][0])+16*PEXIT).hi) for c in final)
                gains=[float((I(c['value_interval'][0])-I(old['value_interval'][1])).lo) for c,old in zip(final,cs)]
                gain=float((I(min(gains))-I(gamma['bound'])-16*PEXIT).lo)
                row={'base_seed':seed,'representation':rep,'optimizer':opt,'K_regret_upper':B,
                     'K_gain_from_initial_lower':gain,'strict_uniform_improvement_certified':gain>0,
                     'jensen_initial':gamma,'accepted_corners':sum(r['accepted'] for r in rr),
                     'generation_seconds':sum(r['generation_seconds'] for r in rr),
                     'gradient_evaluations':sum(r['gradient_evaluations'] for r in rr),
                     'function_evaluations':sum(r['function_evaluations'] for r in rr),
                     'line_search_evaluations':sum(r['line_search_evaluations'] for r in rr),
                     'checker_seconds':sum(r['initial_checker_seconds']+r['final_checker_seconds'] for r in rr)}
                if gain>0:row['true_regret_ratio_upper']=float((I(B)/(I(B)+I(gain))).hi)
                rows.append(row);crossed.extend(rr)
    paired=[]
    for seed in (22000,22100,22200):
        for v in range(4):
            rs=[r for r in crossed if r['base_seed']==seed and r['vertex']==v]
            assert len({r['initial_policy_sha256'] for r in rs})==1
            for opt in ('adam','lbfgsb'):
                a=next(r for r in rs if r['representation']=='neural' and r['optimizer']==opt)
                b=next(r for r in rs if r['representation']=='direct' and r['optimizer']==opt)
                ai=a['delivered_certificate']['value_interval'];bi=b['delivered_certificate']['value_interval']
                paired.append({'base_seed':seed,'vertex':v,'optimizer':opt,
                    'neural_minus_direct_interval':[float((I(ai[0])-I(bi[1])).lo),float((I(ai[1])-I(bi[0])).hi)]})
    save(REV/'results/continuum.json',{'theorem':'R22 Theorem: unequal-initialization continuum improvement',
         'scope':'t=0, K=[1.98,2.02] x [1.24,1.26], k=2; independent corner seeds',
         'hessian_absolute_upper':dict(zip(('uu','uc','cc'),H)),'rows':rows,'paired_same_optimizer':paired,
         'failed_feasibility_checks':sum(r['candidate_certificate']['status']!='CERTIFIED' for r in crossed),
         'accepted_final_proposals':sum(r['accepted'] for r in crossed),'total_configurations':len(crossed),
         'source_status':'new prospective R22 execution, not R20/R21 reanalysis'})
    print(json.dumps([{k:v for k,v in r.items() if k!='jensen_initial'} for r in rows],indent=2))
if __name__=='__main__':main()
