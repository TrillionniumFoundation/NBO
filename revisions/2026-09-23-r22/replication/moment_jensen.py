"""Verified pair-moment Jensen bounds for independently initialized experts.

The Lipschitz/range certificate is retained in continuum.json. This additional
analytic audit integrates pairwise consumption differences and then applies the
weighted-variance identity and Cauchy--Schwarz. It does not select neural seeds.
"""
from pathlib import Path
from itertools import combinations
import sys,json,time
import numpy as np
from continuum import ROOT,REV,I,Q,exp,sqrt,pi,stack,add_reduce,MASS,PEXIT,PTAIL,hess_bounds,span,read,save
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r20/replication'))
from certify_stochastic import grid

def pair_moments(actors):
    v,wv,z,wz,idx,quaderr=grid();t=v.square()
    weight=2*v*exp(-Q('.04')*t)*wv*wz*exp(-z.square()/2)/sqrt(2*pi())
    lp=-Q('.025')*t+Q('.3')*v*z
    cs=[]
    for d in actors:
        b=I(np.asarray(d['b'])[idx,None]);s=I(np.asarray(d['s'])[idx,None])
        cs.append(Q('.5')+Q('.3')/(1+exp(-(b-s*lp))))
    tail=Q('.09')*2*exp(-Q(32))/(8*sqrt(2*pi()))
    results=[]
    for i,k in combinations(range(4),2):
        integrand=weight*(cs[i]-cs[k]).square();byrow=add_reduce(integrand,axis=1);intervals=[]
        for j in range(16):
            value=add_reduce(byrow[idx==j]);error=I(quaderr)
            intervals.append([max(0,float((value-error).lo)),float((value+error+tail).hi)])
        results.append({'pair':[i,k],'discounted_square_difference_by_slab':intervals})
    return {'pairs':results,'quadrature_error_per_pair_per_slab_upper':quaderr,
            'omitted_normal_tail_per_pair_per_slab_upper':float(tail.hi),
            'complex_integrand_bound':100,'cauchy_radii':['1/16','1/2'],
            'proof':'logistic analytic for |Im(argument)|<9/4<3*pi/4; |c|<.95, density<1, |2v exp(-.04v^2)|<3; integrand magnitude<11<100'}

def moment_jensen(actors,certificates,H):
    start=time.perf_counter();mom=pair_moments(actors);n=16
    th=I(np.array([d['theta'] for d in actors]));u=stack([Q(str(d['u0'])) for d in actors]);prefix=I(np.zeros(4));terms=[];rows=[]
    for j in range(n):
        du=I(max(float(span(u+prefix).hi),float(span(u+prefix+th[:,j]/n).hi)))
        vc=Q('0.375')*I(max(p['discounted_square_difference_by_slab'][j][1] for p in mom['pairs']))
        vu=MASS[j]*du.square()/4;dt=span(th[:,j])
        term=I(H[0])*vu/2+I(H[1])*sqrt(vu*vc)+I(H[2])*vc/2+MASS[j]*dt.square()/4
        terms.append(term);rows.append({'slab':j,'integrated_preference_variance_upper':float(vu.hi),'integrated_consumption_variance_upper':float(vc.hi),'jensen_upper':float(term.hi)})
        prefix=prefix+th[:,j]/n
    rs=[c['reserve_interval'] for c in certificates];rmin=min(r[0] for r in rs);assert rmin>.5
    dr=I(max(r[1] for r in rs))-I(rmin);duT=span(u+prefix)
    terminal=exp(-Q('.04'))*(Q('.005')*duT.square()+Q('.0125')/I(rmin).square()*dr.square())
    running=add_reduce(stack(terms))+6*PTAIL*add_reduce(MASS)
    bound=running+terminal+16*PEXIT
    return {'bound':float(bound.hi),'running':float(running.hi),'terminal':float(terminal.hi),'slabs':rows,
            'pair_moments':mom,'seconds':time.perf_counter()-start,'identical_slopes_required':False,'identical_drifts_required':False}

def main():
    H=hess_bounds();base_summary=read(REV/'results/continuum.json');rows=[];comparisons=[]
    for seed in (22000,22100,22200):
        base=REV/f'results/crossed/seed{seed}'
        initial=[read(base/f'vertex{v}/initial_actor.json') for v in range(4)]
        initial_c=[read(base/f'vertex{v}/initial_certificate.json') for v in range(4)]
        gamma=moment_jensen(initial,initial_c,H);save(REV/f'results/moments/seed{seed}_initial.json',gamma)
        for row in [r for r in base_summary['rows'] if r['base_seed']==seed]:
            rr=[read(base/f"vertex{v}/{row['representation']}_{row['optimizer']}/record.json") for v in range(4)]
            finals=[r['delivered_certificate'] for r in rr]
            corner=min(float((I(c['value_interval'][0])-I(i['value_interval'][1])).lo) for c,i in zip(finals,initial_c))
            improvement=float((I(corner)-I(gamma['bound'])-16*PEXIT).lo);B=I(row['K_regret_upper'])
            r={k:v for k,v in row.items() if k!='jensen_initial'}
            r.update({'moment_jensen_initial_upper':gamma['bound'],'range_jensen_initial_upper':row['jensen_initial']['bound'],
                'K_gain_from_initial_lower':improvement,'strict_uniform_improvement_certified':improvement>0})
            r.pop('true_regret_ratio_upper',None)
            if improvement>0:r['true_regret_ratio_upper']=float((B/(B+I(improvement))).hi)
            rows.append(r)
        direct=[read(base/f'vertex{v}/direct_adam/delivered_actor.json') for v in range(4)]
        dc=[read(base/f'vertex{v}/direct_adam/record.json')['delivered_certificate'] for v in range(4)]
        nc=[read(base/f'vertex{v}/neural_adam/record.json')['delivered_certificate'] for v in range(4)]
        gd=moment_jensen(direct,dc,H);save(REV/f'results/moments/seed{seed}_direct_adam_final.json',gd)
        corner=min(float((I(a['value_interval'][0])-I(b['value_interval'][1])).lo) for a,b in zip(nc,dc))
        gain=float((I(corner)-I(gd['bound'])-16*PEXIT).lo)
        comparisons.append({'base_seed':seed,'neural_adam_minus_direct_adam_uniform_payoff_gain_lower':gain,
            'minimum_vertex_payoff_gain_lower':corner,'direct_mixture_jensen_upper':gd['bound'],
            'conditional_on_optimizer_and_gradient_budget':True,'unconditional_neural_frontier_advantage':False})
        print('moment Jensen',seed,gamma['bound'],'uniform neural Adam advantage',gain,flush=True)
    save(REV/'results/moment_continuum.json',{'rows':rows,'conditional_representation_comparison':comparisons,
        'same_models_as_primary_experiment':True,'analysis_status':'a posteriori directed pair-moment analysis of all three frozen ensembles',
        'not_a_global_state_claim':True,'hessian_absolute_upper':H})
if __name__=='__main__':main()
