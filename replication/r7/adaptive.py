#!/usr/bin/env python3
"""Autonomous dyadic refinement on one declared full-model contract.
Each arm begins at [0,1] with an empty anchor cache; no inherited anchor list.
"""
from core import *
import gc

def run(mix=None):
    start=time.perf_counter();mix=build() if mix is None else mix;setup=time.perf_counter()-start
    d=.5;tolerance=.001;result=dict(contract=d,tolerance=tolerance,kernel_setup_seconds=setup,
        states=mix.ns,actions=len(mix.e[0].menu)+3,dates=mix.steps,
        scope='full-model autonomous left-first dyadic refinement; same two-endpoint policy rule and eight certificate cells; empty per-arm anchor caches',rows=[])
    for kind in ('chord','count','cascade'):
        begin=time.perf_counter();bank={};nodes=[];leaves=[];work=dict(anchor_seconds=0.,policy_seconds=0.,lower_restriction_seconds=0.,
            chord_upper_seconds=0.,count_upper_seconds=0.,certificate_seconds=0.,chord_constructions=0,count_constructions=0)
        def anchor(a):
            if a not in bank:
                t=time.perf_counter();z=mix.solve(a,d);work['anchor_seconds']+=time.perf_counter()-t
                t=time.perf_counter();z['coeff']=mix.policy_coefficients(z['policy'],d);work['policy_seconds']+=time.perf_counter()-t
                bank[a]=z
            return bank[a]
        def visit(a,b,depth=0):
            za,zb=anchor(a),anchor(b);t=time.perf_counter()
            lower=[[restrict(co,a,b) for co in z['coeff']] for z in (za,zb)];work['lower_restriction_seconds']+=time.perf_counter()-t
            rec=dict(left=a,right=b,depth=depth)
            methods=('chord','count') if kind=='cascade' else (kind,)
            for method in methods:
                t=time.perf_counter()
                upper=expand(mix,za['value'],zb['value'],chord(mix,a,b,za['value'],zb['value'])) if method=='chord' else count(mix,a,b,d,za['value'],zb['value'])
                work[method+'_upper_seconds']+=time.perf_counter()-t;work[method+'_constructions']+=1
                t=time.perf_counter();cert=envelope_certificate(upper,lower,depth=3);work['certificate_seconds']+=time.perf_counter()-t
                rec[method]=cert['bound'];del upper
                if cert['bound']<=tolerance:break
            rec['accepted']=cert['bound']<=tolerance;rec['bound']=cert['bound'];nodes.append(rec)
            if rec['accepted']:leaves.append(rec)
            else:
                if depth>=12:raise RuntimeError('declared refinement depth exhausted')
                del lower;mid=(a+b)/2;visit(a,mid,depth+1);visit(mid,b,depth+1)
        visit(0.,1.)
        r=dict(method=kind,anchors=sorted(bank),anchor_count=len(bank),nodes=nodes,leaves=leaves,
            bound=max(z['bound'] for z in leaves),work=work,total_seconds=setup+time.perf_counter()-begin)
        H=mix.steps;r['upper_kernel_applications']=work['chord_constructions']*(4*H-6)+work['count_constructions']*(H*(H+1)-2)
        r['lower_coefficient_bytes']=sum(sum(z.nbytes for z in v['coeff']) for v in bank.values())
        result['rows'].append(r);save('adaptive.json',result)
        print('ADAPTIVE',kind,'anchors',len(bank),'bound',r['bound'],'seconds',r['total_seconds'],flush=True)
        del bank;gc.collect()
    assert set(result['rows'][2]['anchors'])<=set(result['rows'][0]['anchors'])
    return result
if __name__=='__main__':run()
