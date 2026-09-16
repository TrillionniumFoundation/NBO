#!/usr/bin/env python3
"""Matched precision/work comparison, including all 51 R6 anchor intervals."""
from core import *
import argparse, gc

def run(mix=None):
    start=time.perf_counter();mix=build() if mix is None else mix
    setup=time.perf_counter()-start
    source=json.loads((ROOT/'replication/r6/output/kernel_certificate.json').read_text())
    result=dict(scope='all states/dates; same closed cells, target, policies and anchors within each row',
        states=mix.ns,dates=mix.steps,actions=len(mix.e[0].menu)+3,kernel_setup_seconds=setup,
        timing='serial single-thread, one complete measured pass per row; no cross-machine times',rows=[])
    for row in source['rows']:
        d=row['d'];anchor_list=row['anchors'];bank={};anchor_seconds=0.;policy_seconds=0.;replay=0.
        old=np.load(ROOT/f'replication/r6/output/kernel_certificate_{d:g}.npz')
        for i,a in enumerate(anchor_list):
            t=time.perf_counter();z=mix.solve(a,d);st=time.perf_counter()-t;anchor_seconds+=st
            t=time.perf_counter();z['coeff']=mix.policy_coefficients(z['policy'],d);pt=time.perf_counter()-t;policy_seconds+=pt
            z['solve_seconds']=st;z['policy_seconds']=pt;bank[a]=z
            replay=max(replay,float(abs(z['value']-old[f'value.{i}']).max()))
            for n,co in enumerate(z['coeff']):replay=max(replay,float(abs(co-old[f'lower.{i}.{n}']).max()))
        assert replay<2e-11
        grids=[('R6 matched',anchor_list)]
        if d==.5:
            for stride in (4,2):grids.append((f'every {stride}th anchor',sorted(set(anchor_list[::stride]+[1.]))))
        for label,anchors in grids:
            r=dict(d=d,bank=label,anchors=anchors,anchor_count=len(anchors),input_replay_max=replay,
                anchor_seconds=sum(bank[a]['solve_seconds'] for a in anchors),
                policy_seconds=sum(bank[a]['policy_seconds'] for a in anchors),
                lower_coefficient_bytes=sum(sum(x.nbytes for x in bank[a]['coeff']) for a in anchors),
                policy_index_bytes=sum(bank[a]['policy'].nbytes for a in anchors),intervals=[])
            acc={k:dict(upper_seconds=0.,certificate_seconds=0.,bound=0.) for k in ('chord','count','rectangular')}
            for a,b in zip(anchors[:-1],anchors[1:]):
                t=time.perf_counter();lo=[[restrict(x,a,b) for x in bank[z]['coeff']] for z in (a,b)]
                lower_local_seconds=time.perf_counter()-t
                iv=dict(left=a,right=b,lower_local_seconds=lower_local_seconds)
                upper={}
                for kind in ('chord','count','rectangular'):
                    t=time.perf_counter()
                    if kind=='chord':u=expand(mix,bank[a]['value'],bank[b]['value'],chord(mix,a,b,bank[a]['value'],bank[b]['value']))
                    elif kind=='count':u=count(mix,a,b,d,bank[a]['value'],bank[b]['value'])
                    else:u=rectangular(mix,a,b,d)
                    ut=time.perf_counter()-t;t=time.perf_counter();cert=envelope_certificate(u,lo,depth=3);ct=time.perf_counter()-t
                    upper[kind]=u;iv[kind]=dict(bound=cert['bound'],upper_seconds=ut,certificate_seconds=ct,cells=cert['cells'])
                    acc[kind]['bound']=max(acc[kind]['bound'],cert['bound']);acc[kind]['upper_seconds']+=ut;acc[kind]['certificate_seconds']+=ct
                iv['minimum_chord_minus_count']=min(float((u-w).min()) for u,w in zip(upper['chord'],upper['count']))
                iv['minimum_rectangular_minus_count']=min(float((u-w).min()) for u,w in zip(upper['rectangular'],upper['count']))
                assert iv['minimum_chord_minus_count']>=-2e-11 and iv['minimum_rectangular_minus_count']>=-2e-11
                assert iv['count']['bound']<=iv['chord']['bound']+2e-11
                r['intervals'].append(iv)
                print('MATCHED',d,label,a,b,*[iv[k]['bound'] for k in acc],flush=True)
            intervals=len(anchors)-1;H=mix.steps;S=mix.ns;A=len(mix.e[0].menu)+3
            for kind,z in acc.items():
                z['matched_total_seconds']=setup+r['anchor_seconds']+r['policy_seconds']+sum(x['lower_local_seconds'] for x in r['intervals'])+z['upper_seconds']+z['certificate_seconds']
                calls={'chord':max(0,4*H-6),'count':H*(H+1)-2,'rectangular':2*H}[kind]
                z['kernel_applications_per_interval']=calls
                z['kernel_action_rows']=calls*intervals*S*A
            r['methods']=acc;r['compact_chord_additional_bytes']=(H-1)*S*8
            r['count_interior_coefficient_bytes']=H*(H-1)//2*S*8
            r['dense_expanded_upper_bytes']=sum((h+1)*S*8 for h in range(H+1))
            r['memory_scope']='per active interval; compact chord excludes shared endpoint values; count excludes endpoint coefficients; lower bank is not compressed'
            result['rows'].append(r);save('matched.json',result)
        old.close();del bank;gc.collect()
    return result
if __name__=='__main__':run()
