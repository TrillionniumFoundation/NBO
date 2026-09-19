"""Refined fee menus, alternative services/incidence, and exact-response supports."""
from __future__ import annotations
import gc,json,time,os
from pathlib import Path
import numpy as np
from canonical import load,dump,digest
from engine import Engine,SIGNS,EPS
from certified_arithmetic import derive,rat,downward,upward
from response_graph import supports

HERE=Path(__file__).parent

def economics(rows,case,adj,fee_step=.05):
    rr=[r for r in rows if r['adjustment']==adj and abs(r['fee']/fee_step-round(r['fee']/fee_step))<1e-10]
    lo=[];hi=[]
    b=rat(case.get('b',1.));alpha=rat(case.get('capacity_incidence',1.));c=rat(case.get('cost',.02));zeta=rat(case.get('efficiency',1.));kap=rat(case.get('kappa',.02));power=case.get('power',2);term_power=case.get('term_power',1);G=rat(rows[0]['G'])+rat(case.get('outside_shift',0.));direction=case.get('direction',0)
    for r in rr:
        E=rat(r['fee'])/zeta;cost=c*E**power;D=kap*(rat(r['term']-1)/8)**term_power
        qhi=max(rat(0),G-rat(r['value'])+rat(EPS)+alpha*cost);qlo=max(rat(0),G-rat(r['value'])-rat(EPS)+alpha*cost)
        ll=b*rat(r['support']['lower'][direction])-qhi-(1-alpha)*cost-D
        hh=b*rat(r['support']['upper'][direction])-qlo-(1-alpha)*cost-D
        if not r['support']['attained_positive']:ll=rat(-1000)
        lo.append(ll);hi.append(hh)
    k=max(range(len(rr)),key=lambda i:lo[i]);rival=max([(rat(0),'outside')]+[(h,rr[i]['id']) for i,h in enumerate(hi) if i!=k])
    if lo[k]<0:return dict(choice='outside',margin=downward(-max(hi)),binding_rival=rr[max(range(len(rr)),key=lambda i:hi[i])]['id'],certified=max(hi)<0,adjustment=adj,fee_step=fee_step,case=case['name'])
    gap=lo[k]-rival[0]
    return dict(choice=rr[k]['id'],fee=rr[k]['fee'],term=rr[k]['term'],sign=rr[k]['sign'],margin=downward(gap),binding_rival=rival[1],certified=gap>0,profit_interval=[downward(lo[k]),upward(hi[k])],adjustment=adj,fee_step=fee_step,case=case['name'])

def main():
    out=HERE/'extensions';out.mkdir(exist_ok=True);start=time.perf_counter();b,j=load(HERE/'canonical');audit=derive(b,j);eng=Engine(b,j);rows=[];summaries={}
    G=float(b.terminal[b.center]);raw=np.load(HERE/'output/procurement_witness.npz',allow_pickle=False)
    # Denser nested menus are diagnostics, not silently labeled as a continuum.
    for adj in (True,False):
        for integer in range(21):
            F=integer/20
            for m in range(1,9):
                t=time.perf_counter();key=f'{int(adj)}.{F:.2f}.{m}';old=f'{int(adj)}.{F:.1f}.{m}.0'
                if integer%4==0:
                    v=np.zeros((eng.N+1,eng.S));v[1:]=raw[old+'.values'];q=.875*eng.fq(0,v[1],.42425)+.125*eng.fq(1,v[1],.42425);first=eng.first(q,adj,.8,.5)
                else:v,p,first=eng.solve(.125,.42425,F,adj,m)
                rec=supports(eng,v,first,adj,m,F,audit)
                summaries[key]=dict(graph_inventory=rec['graph_inventory'],comparison_slack=rec['comparison_slack'],derived_support_roundoff=rec['derived_support_roundoff'],elapsed_seconds=time.perf_counter()-t)
                for sign in SIGNS:
                    rows.append(dict(id=key+'.'+sign,adjustment=adj,fee=F,term=m,sign=sign,value=first[sign][0],G=G,support=rec['responses'][sign]))
                eng.cache.clear();print('REFINED',key,flush=True)
            gc.collect()
    raw.close()
    cases=[dict(name='baseline'),dict(name='fee_to_purchaser',direction=3),dict(name='half_fee_to_purchaser',direction=4),dict(name='capacity_paid_directly',capacity_incidence=0.),dict(name='capacity_cost_shared',capacity_incidence=.5),dict(name='lower_capacity_efficiency',efficiency=.8),dict(name='higher_capacity_efficiency',efficiency=1.2),dict(name='low_capacity_cost',cost=.01),dict(name='high_capacity_cost',cost=.04),dict(name='cubic_capacity_cost',power=3),dict(name='quadratic_term_cost',term_power=2),dict(name='quality_premium',direction=5),dict(name='quality_penalty',direction=6),dict(name='fee_and_quality',direction=7),dict(name='higher_outside_option',outside_shift=.05),dict(name='lower_outside_option',outside_shift=-.05),dict(name='low_price',b=.9),dict(name='high_price',b=1.1)]
    result=dict(schema='nbo-r13-exact-response-refinement-v1',canonical_manifest_sha256=digest(HERE/'canonical/manifest.json'),rows=rows,graph_checks=summaries,nested_menu_choices=[economics(rows,cases[0],adj,step) for step in (.2,.1,.05) for adj in (True,False)],counterfactuals=[economics(rows,c,adj,.05) for c in cases for adj in (True,False)],buyer_cases=cases,quality_definition='discounted operating time priced by the indicator that beginning-of-period wealth is at least 1.25; Q<=A, and Q is not an intrinsic utility coefficient',elapsed_seconds=time.perf_counter()-start,source_commit=os.getenv('R13_SOURCE_SHA','local-development'),scope='All exact best responses on the stated nested finite fee menus. This is not a certificate over fees between grid points; continuous instruments are treated analytically in the separate primitive economy.')
    dump(out/'refinement.json',result)
    print('REFINEMENT FINISHED',json.dumps(result['nested_menu_choices']),flush=True)
if __name__=='__main__':main()
