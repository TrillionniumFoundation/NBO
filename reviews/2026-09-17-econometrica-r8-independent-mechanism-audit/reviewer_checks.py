#!/usr/bin/env python3
"""Independent R8 mathematical micro-audit; no author-code imports or network.

Python >=3.11, standard library only. Exact Fraction tests address small
finite MDPs, NOT replication of the author's 1,568-action economy. Decimal
CRRA checks are high-precision numerical checks, NOT interval proofs.
"""
from __future__ import annotations
import argparse
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import json
from math import comb
from pathlib import Path
import platform
import random

REVIEWED = 'be77b2a81b4d3a68806c534c1e892d2eb4b1230d'
CONTEXT = '8c20474bca5b7388f5ba4640ec165f1ad8f5e91a'
ZERO = F(0)


def dot(x, y):
    return sum((a*b for a, b in zip(x, y)), ZERO)


def mix(a, b, t):
    return (1-t)*a+t*b


def generate(h, seed, states=3, actions=2):
    rng = random.Random(seed)
    kernels, rewards = [], []
    for _ in range(h):
        ke, re = [], []
        for _ in range(2):
            ks, rs = [], []
            for _ in range(states):
                ka, ra = [], []
                for _ in range(actions):
                    weights = [rng.randint(0, 5) for _ in range(states)]
                    denominator = sum(weights)+rng.randint(1, 5)
                    ka.append([F(v, denominator) for v in weights])
                    ra.append(F(rng.randint(-8, 8), 7))
                ks.append(ka); rs.append(ra)
            ke.append(ks); re.append(rs)
        kernels.append(ke); rewards.append(re)
    terminal = [F(rng.randint(-4, 4), 5) for _ in range(states)]
    return kernels, rewards, terminal


def audit_model(h, seed, left, right):
    k, r, g = generate(h, seed)
    s_count, a_count = len(g), len(k[0][0][0])
    kk, rr = [], []
    for n in range(h):
        kk.append([[[[mix(k[n][0][s][a][v], k[n][1][s][a][v], t)
                      for v in range(s_count)] for a in range(a_count)]
                    for s in range(s_count)] for t in (left, right)])
        rr.append([[[mix(r[n][0][s][a], r[n][1][s][a], t)
                     for a in range(a_count)] for s in range(s_count)]
                   for t in (left, right)])
    def backup(n, e, s, a, value):
        return rr[n][e][s][a]+dot(kk[n][e][s][a], value)
    def optimize(t):
        values = [None]*h+[g]
        policies = [None]*h
        for n in range(h-1, -1, -1):
            candidates = [[mix(backup(n, 0, s, a, values[n+1]),
                               backup(n, 1, s, a, values[n+1]), t)
                           for a in range(a_count)] for s in range(s_count)]
            policies[n] = [max(range(a_count), key=lambda a: candidates[s][a])
                           for s in range(s_count)]
            values[n] = [max(row) for row in candidates]
        return values, policies
    endpoints = [optimize(F(e)) for e in range(2)]
    v0, p0 = endpoints[0]; v1, _ = endpoints[1]
    correction = [None]*h+[[ZERO]*s_count]
    count = [None]*h+[[g]]
    lower = [None]*h+[[g]]
    upper = [None]*h+[[g]]
    rectangular = [None]*h+[g]
    for n in range(h-1, -1, -1):
        rem = h-n
        correction[n] = []
        for s in range(s_count):
            candidates = [ZERO]
            for a in range(a_count):
                delta_k = [x-y for x, y in zip(kk[n][0][s][a], kk[n][1][s][a])]
                delta_v = [y-x for x, y in zip(v0[n+1], v1[n+1])]
                candidates.append(dot(delta_k, delta_v)+max(
                    dot(kk[n][e][s][a], correction[n+1]) for e in range(2)))
            correction[n].append(max(candidates))
        rectangular[n] = [max(backup(n,e,s,a,rectangular[n+1])
                               for e in range(2) for a in range(a_count))
                          for s in range(s_count)]
        count[n], lower[n], upper[n] = [], [], []
        for j in range(rem+1):
            weight = F(j,rem)
            def conditional(a, s, continuations):
                result = ZERO
                if j < rem:
                    result += (1-weight)*backup(n,0,s,a,continuations[j])
                if j > 0:
                    result += weight*backup(n,1,s,a,continuations[j-1])
                return result
            count[n].append([max(conditional(a,s,count[n+1]) for a in range(a_count))
                             for s in range(s_count)])
            lower[n].append([conditional(p0[n][s],s,lower[n+1]) for s in range(s_count)])
            f = F(j*(rem-j),rem*(rem-1)) if rem >= 2 else ZERO
            upper[n].append([mix(v0[n][s],v1[n][s],weight)+f*correction[n][s]
                             for s in range(s_count)])
    checks = 0
    minimum_slack = None
    for n in range(h+1):
        for j in range(h-n+1):
            for s in range(s_count):
                slack = upper[n][j][s]-count[n][j][s]
                assert slack >= 0, ('count/chord',h,seed,n,j,s)
                assert count[n][j][s] <= rectangular[n][s], ('count/reset',h,seed,n,j,s)
                minimum_slack = slack if minimum_slack is None else min(slack, minimum_slack)
                checks += 2
    # Compare the original common-parameter optimum against both upper values,
    # and one feasible endpoint policy against that optimum, with exact rationals.
    point_comparisons = 0
    for t in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
        exact, _ = optimize(t)
        for n in range(h+1):
            degree=h-n
            basis=[F(comb(degree,j))*t**j*(1-t)**(degree-j) for j in range(degree+1)]
            for s in range(s_count):
                lo=dot(basis,[lower[n][j][s] for j in range(degree+1)])
                co=dot(basis,[count[n][j][s] for j in range(degree+1)])
                up=dot(basis,[upper[n][j][s] for j in range(degree+1)])
                assert lo <= exact[n][s] <= co <= up, ('point-order',h,seed,n,s,t)
                point_comparisons += 1
    # Independent primitive-constant recursion for the theorem's coefficient bound.
    magnitude=max(abs(x) for x in g); lipschitz=ZERO; quadratic=ZERO
    for n in range(h-1,-1,-1):
        beta=max(sum(k[n][e][s][a],ZERO) for e in range(2)
                 for s in range(s_count) for a in range(a_count))
        rho=max(abs(r[n][1][s][a]-r[n][0][s][a])
                for s in range(s_count) for a in range(a_count))
        kappa=max(sum((abs(x-y) for x,y in zip(k[n][0][s][a],k[n][1][s][a])),ZERO)
                  for s in range(s_count) for a in range(a_count))
        reward=max(abs(x) for e in r[n] for row in e for x in row)
        quadratic=kappa*lipschitz+beta*quadratic
        lipschitz=rho+kappa*magnitude+beta*lipschitz
        magnitude=reward+beta*magnitude
        bound=2*lipschitz*(right-left)+quadratic*(right-left)**2/2
        assert max(upper[n][j][s]-lower[n][j][s]
                   for j in range(h-n+1) for s in range(s_count)) <= bound
        checks += 1
    return {'horizon':h,'seed':seed,'interval':[str(left),str(right)],
            'exact_inequality_checks':checks,'point_order_chains':point_comparisons,
            'minimum_chord_minus_count':str(minimum_slack)}


def primitive_checks():
    with localcontext() as ctx:
        ctx.prec=65
        logs={c:D(c).ln() for c in ('0.05','0.8','0.5')}
        def utility(c,z):
            return -(-z*logs[c]).exp()/z
        def marginal(c,z):
            return (-z*logs[c]).exp()*(1+z*logs[c])/z**2
        def curv(c,z):
            return (-z*logs[c]).exp()*((1+z*logs[c])**2+1)/z**3
        def average(fun,positive,p,z):
            return p*fun('0.05',z)+(1-p)*fun('0.8',z) if positive else fun('0.5',z)
        def optimum(positive,p,k,tilt):
            lo,hi=D('-0.2'),D('0.2')
            def derivative(theta):
                return average(marginal,positive,p,1+theta)+tilt-k*theta
            if derivative(lo) <= 0: theta=lo
            elif derivative(hi) >= 0: theta=hi
            else:
                for _ in range(160):
                    mid=(lo+hi)/2
                    if derivative(mid)>0: lo=mid
                    else: hi=mid
                theta=(lo+hi)/2
            option=(average(utility,positive,p,1+theta)-average(utility,positive,p,D(1))
                    +tilt*theta-k*theta**2/2)
            return theta,option
        bound=((D('1.482')-D('.25'))**2*20/(20+D('17.342'))
               -(D('.6138')+D('.25'))**2)/160
        rows=[]
        for p in (D('.06'),D('.08'),D('.10')):
            for k in (D(20),D(40),D(80)):
                for tilt in (D('-.25'),D(0),D('.25')):
                    tp,op=optimum(True,p,k,tilt); tm,om=optimum(False,p,k,tilt)
                    assert tp<0<tm and op-om>bound
                    rows.append({'p':str(p),'k':str(k),'a':str(tilt),
                                 'theta_plus':str(tp),'theta_minus':str(tm),
                                 'relative_option':str(op-om)})
        baseline={}
        for tilt in (D(0),D(1),D(2)):
            tp,op=optimum(True,D('.08'),D(40),tilt)
            tm,om=optimum(False,D('.08'),D(40),tilt)
            baseline[str(tilt)]={'theta_plus':str(tp),'theta_minus':str(tm),
                                 'relative_option':str(op-om)}
        gradients=[average(marginal,True,p,D(1)) for p in (D('.06'),D('.10'))]
        vertices=[average(curv,True,p,z) for p in (D('.06'),D('.10'))
                  for z in (D('.8'),D('1.2'))]
        return {'precision_digits':65,'bound':str(bound),'sample_count':len(rows),'tilt_examples':baseline,
                'sample_grid':{'p':['0.06','0.08','0.10'],'k':[20,40,80],
                               'a':['-0.25','0','0.25']},
                'sample_minimum_relative_option':str(min(D(x['relative_option']) for x in rows)),
                'sample_theta_plus_range':[str(f(D(x['theta_plus']) for x in rows)) for f in (min,max)],
                'sample_theta_minus_range':[str(f(D(x['theta_minus']) for x in rows)) for f in (min,max)],
                'g_plus_endpoints':[str(x) for x in gradients],
                'g_minus':str(marginal('0.5',D(1))),
                'curvature_vertex_max':str(max(vertices)),
                'scope':'Decimal checks are not outward-rounded interval proofs.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    rows=[audit_model(h,20260917+100*h+i,left,right)
          for h in range(1,7) for i in range(4)
          for left,right in ((F(0),F(1)),(F(1,4),F(3,4)))]
    result={'reviewed_commit':REVIEWED,'historical_context_commit':CONTEXT,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'python_version':platform.python_version(),
            'independent_exact_arithmetic':{'base_models':24,'model_interval_cases':len(rows),
                'exact_inequality_checks':sum(x['exact_inequality_checks'] for x in rows),
                'point_order_chains':sum(x['point_order_chains'] for x in rows),
                'design':{'horizons':list(range(1,7)),'states':3,'actions':2,
                    'seed_formula':'20260917 + 100*horizon + i, i=0,1,2,3',
                    'intervals':[['0','1'],['1/4','3/4']],
                    'local_parameter_points':['0','1/4','1/2','3/4','1']},
                'minimum_chord_minus_count':str(min(F(x['minimum_chord_minus_count']) for x in rows))},
            'independent_primitive_checks':primitive_checks(),
            'excluded_claims':['No full author-program rerun','No neural training',
                'No new dynamic-economy solution','No manuscript PDF recompilation',
                'No diffusion or constructor error enclosure'],
            'all_checks_passed':True}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in
          ('independent_exact_arithmetic','independent_primitive_checks')},indent=2))
    print('exact checks:',result['independent_exact_arithmetic']['exact_inequality_checks'])
    print('point order chains:',result['independent_exact_arithmetic']['point_order_chains'])
    print('primitive baseline:',result['independent_primitive_checks']['tilt_examples']['0'])


if __name__=='__main__':
    main()
