"""Extension checks with explicit independence boundaries.

The equality-graph support computation below is recoded independently of
response_graph.supports. Analytical examples are checked with rational costs;
LP weak-duality inequalities are recomputed over their original rational data.
Timings, MLP fitting performance and the separate analytical proofs are not
claimed to be independently reproduced mathematical equalities.
"""
from __future__ import annotations
import argparse,json,time,copy
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
from canonical import load,dump,digest
from engine import Engine,SIGNS,EPS
from certified_arithmetic import derive
from oracle_polytope import RationalLP
HERE=Path(__file__).parent;EXT=HERE/'extensions'

def independent_support(e,v,adj,m,F,audit):
    W=np.asarray([[1,0,0],[0,1,0],[0,0,1],[1,F,0],[1,F/2,0],[1,0,.05],[1,0,-.05],[1,F,.05]],float);W=np.r_[W,-W]
    qfeature=(e.b.e[0].states[:,1]>=1.25).astype(float);h=np.zeros((e.S,16));nm=len(e.b.e[0].menu);slack=8*audit['bounds']['bellman_value'];counts=[]
    for n in reversed(range(1,8)):
        q=.875*e.q(0,n,v[n+1],.42425,F)+.125*e.q(1,n,v[n+1],.42425,F)
        active=e.mask(n,adj,m)&(q>=v[n,:,None]-slack)
        packed=np.flatnonzero(active);states=packed//(e.stop+1);actions=packed%(e.stop+1)
        if len(np.unique(states))!=e.S:raise ValueError('missing state in exact-response outer graph')
        result=np.zeros((len(packed),16));result[actions==e.stop]=W[:,1]
        for k,weight in enumerate((.875,.125)):
            for z,offset,selected in [(e.b.e[k].common,0,actions<nm),(e.b.e[k].extra[n],nm,(actions>=nm)&(actions<e.stop))]:
                loc=np.flatnonzero(selected);ss=states[loc];aa=actions[loc]-offset
                if not len(loc):continue
                now=np.outer(z.duration[ss,aa],W[:,0])+np.outer(z.duration[ss,aa]*qfeature[ss],W[:,2])
                result[loc]+=weight*(now+z.matrix[ss*z.na+aa]@h)
        beginnings=np.r_[0,np.flatnonzero(np.diff(states))+1]
        h=np.maximum.reduceat(result,beginnings,axis=0)
        counts.append(dict(date=n,actions=int(active.sum()),maximum_per_state=int(active.sum(1).max())))
    q=.875*e.fq(0,v[1],.42425)+.125*e.fq(1,v[1],.42425)
    features=np.zeros((len(q),16))
    for k,w in enumerate((.875,.125)):
        features+=w*(e.fm.rows[k]@h+np.outer(e.fm.duration[k],W[:,0]+qfeature[e.b.center]*W[:,2]))
    out={};boundary_gap=None
    for s in SIGNS:
        permitted=e.first_mask(adj,s,.8,.5);mx=q[permitted].max();ids=np.flatnonzero(permitted&(q>=mx-slack));support=features[ids].max(0)
        lower=-support[8:]-1e-9;upper=support[:8]+1e-9;lower[:3]=np.maximum(0.,lower[:3]);upper[:3]=np.minimum(1.,upper[:3])
        out[s]=(lower,upper)
        if s=='positive':
            zeros=permitted&(e.fm.actions[:,2]==0);positive=permitted&(e.fm.actions[:,2]>0)
            boundary_gap=float(q[positive].max()-q[zeros].max())
    return out,counts,boundary_gap

def verify_refinement(eng,audit,full=True):
    z=json.loads((EXT/'refinement.json').read_text())
    if z['canonical_manifest_sha256']!=digest(HERE/'canonical/manifest.json'):raise ValueError('refinement target differs')
    grouped={}
    for r in z['rows']:grouped.setdefault((r['adjustment'],r['fee'],r['term']),{})[r['sign']]=r
    if len(grouped)!=336 or len(z['rows'])!=672:raise ValueError('refined menu inventory')
    maxgap=0.;boundary=[];checked=0
    for (adj,F,m),rows in grouped.items():
        v,p,first=eng.solve(.125,.42425,F,adj,m);supported,counts,gap=independent_support(eng,v,adj,m,F,audit)
        for s in SIGNS:
            r=rows[s]
            if abs(r['value']-first[s][0])>2e-10:raise ValueError('refined private value mismatch')
            for key,got in zip(('lower','upper'),supported[s]):
                err=float(np.max(abs(np.asarray(r['support'][key])-got)));maxgap=max(maxgap,err)
                if err>2e-11:raise ValueError('joint response support mismatch')
            if s=='positive' and r['support']['attained_positive'] and gap<=4*audit['bounds']['bellman_value']:raise ValueError('open-class attainment not strictly separated from zero closure boundary')
        if counts!=z['graph_checks'][f'{int(adj)}.{F:.2f}.{m}']['graph_inventory']:raise ValueError('graph inventory mismatch')
        boundary.append(gap);checked+=1;eng.cache.clear();print('CHECKED RESPONSE GRAPH',adj,F,m,flush=True)
    # Independently reconstruct the finite-offer economic optimization, including
    # positive-part participation, fee recipients, quality and capacity incidence.
    choices=z['nested_menu_choices']+z['counterfactuals'];cases={c['name']:c for c in z['buyer_cases']}
    for result in choices:
        case=cases[result['case']];adj=result['adjustment'];step=result['fee_step'];rows=[r for r in z['rows'] if r['adjustment']==adj and abs(r['fee']/step-round(r['fee']/step))<1e-10]
        values=[]
        for r in rows:
            conv=lambda x:Q.from_float(float(x));E=conv(r['fee'])/conv(case.get('efficiency',1));C=conv(case.get('cost',.02))*E**case.get('power',2);D=conv(case.get('kappa',.02))*(Q(r['term']-1,8))**case.get('term_power',1);a=conv(case.get('capacity_incidence',1));G=conv(r['G'])+conv(case.get('outside_shift',0));d=case.get('direction',0);b=conv(case.get('b',1))
            lower=b*conv(r['support']['lower'][d])-max(Q(0),G-conv(r['value'])+conv(EPS)+a*C)-(1-a)*C-D
            upper=b*conv(r['support']['upper'][d])-max(Q(0),G-conv(r['value'])-conv(EPS)+a*C)-(1-a)*C-D
            if not r['support']['attained_positive']:lower=Q(-1000)
            values.append((lower,upper,r['id']))
        best=max(values,key=lambda x:x[0]);margin=best[0]-max([Q(0)]+[x[1] for x in values if x[2]!=best[2]])
        selected=best[2]
        if best[0]<0:selected='outside';margin=-max(x[1] for x in values)
        if selected!=result['choice'] or abs(float(margin)-result['margin'])>2e-13 or (margin>0)!=result['certified']:raise ValueError('refined purchaser choice mismatch')
    return dict(operating_problems=checked,offers=len(z['rows']),maximum_support_discrepancy=maxgap,minimum_positive_closure_boundary_gap=min(boundary),all_choice_comparisons=len(choices),independence='Separate support recursion and rational finite-offer economics; shared canonical primitives and independently recoded core Engine.')

def verify_primitive():
    z=json.loads((EXT/'primitive_contract.json').read_text());cnt=0;strict=0
    def q(x):return Q(x['exact']) if isinstance(x,dict) else Q(x)
    for row in z['comparative_statics']['rows']:
        c=q(row['c']);k=q(row['k']);eff=q(row['zeta']);T=q(row['T']);N=row['N'];p=row['power'];r=row['term_power'];choices=[]
        for loss,key in ((Q(9,10),'adjusted_term'),(Q(1),'unadjusted_term')):
            costs=[]
            for m in range(1,N+1):
                tau=T*m/N;fee=loss*(T-tau)+Q(1,1000) if m<N else Q(0);cost=c*(fee/eff)**p+k*(tau-T/N)**r;costs.append(cost)
            winner=min(range(N),key=lambda i:(costs[i],i))+1
            if winner!=row[key]:raise ValueError('incorrect rational primitive minimizer')
            choices.append(winner)
        if choices[0]>choices[1]:raise ValueError('primitive monotonicity violation')
        strict+=choices[0]<choices[1];cnt+=1
    if (cnt,strict)!=(972,373):raise ValueError('primitive factorial inventory')
    return dict(exact_rational_cases=cnt,strict_shortening=strict,unchanged=cnt-strict,independence='All term costs and extremal minimizers independently recomputed from rational primitives.')

def verify_lp():
    z=json.loads((EXT/'theory_tests.json').read_text());checked=0
    for case in z['sharp_oracle_examples']:
        lp=case['LP'];A=[[Q(x) for x in row] for row in lp['A']];d=list(map(Q,lp['b']));box=[list(map(Q,p)) for p in lp['box']];c=list(map(Q,case['objective']));x=list(map(Q,case['exact_primal']));mu=[Q.from_float(float(x)) for x in case['dual']['multipliers']]
        if any(v<0 for v in mu):raise ValueError('negative LP upper multiplier')
        residual=[c[j]-sum(mu[i]*A[i][j] for i in range(len(A))) for j in range(len(c))]
        upper=sum(a*b for a,b in zip(mu,d))+sum(max(a*l,a*u) for a,(l,u) in zip(residual,box))
        if upper!=Q(case['dual']['exact_upper']) or any(sum(a*b for a,b in zip(row,x))>b for row,b in zip(A,d)) or any(not l<=v<=u for v,(l,u) in zip(x,box)):raise ValueError('rational primal or weak-duality inequality failed')
        primal=sum(a*b for a,b in zip(c,x))
        if not 0<=upper-primal<Q(1,10**9) or primal!=Q(case['sharp_upper']):raise ValueError('sharp oracle objective mismatch')
        h=Q(1,10);queries=[(0,0),(h,0),(-h,0),(0,h),(0,-h)]
        if case['diagonal_queries']:queries += [(h,h),(-h,-h)]
        menu=[(Q(r['intercept']),list(map(Q,r['features']))) for r in case['constructed_menu']];eps=Q(case['error']);eta=Q(case['response_tolerance'])
        for beta,features in menu:
            if any(not 0<=v<=1 for v in features):raise ValueError('constructed service outside K')
        for t in queries:
            value=max(beta+sum(a*b for a,b in zip(t,f)) for beta,f in menu);oracle=max(t)
            if not oracle-eps<=value<=oracle+eps:raise ValueError('constructed economy violates original oracle')
        actual=max(beta for beta,_ in menu)
        if menu[0][0]<actual-eta or sum(menu[0][1])!=primal:raise ValueError('candidate is not an eta response of the constructed economy')
        checked+=1
    if checked!=8 or not all(r['rejected'] for r in z['negative_tests'].values()):raise ValueError('theory fixture inventory')
    return dict(exact_query_examples=checked,all_passed=True,scope='Rational primal feasibility, weak-duality support and original-query compatibility of every constructed finite economy are recomputed without invoking the LP solver or the producer dual-bound routine.')

def main():
    a=argparse.ArgumentParser();a.add_argument('--seal',action='store_true');args=a.parse_args();t=time.perf_counter();b,j=load(HERE/'canonical');eng=Engine(b,j);audit=derive(b,j)
    result=dict(schema='nbo-r13-extension-validation-v1',refinement=verify_refinement(eng,audit),primitive=verify_primitive(),information_oracle=verify_lp(),elapsed_seconds=time.perf_counter()-t,all_passed=True,scope='Independent equality-graph and finite-offer reconstruction; independent rational primitive cost checking. LP fitting, timing and broader original-diffusion approximation are not subsumed in this claim.')
    dump(EXT/'validation.json',result)
    if args.seal:
        files={p.name:digest(p) for p in EXT.iterdir() if p.is_file() and p.name!='manifest.json'}
        dump(EXT/'manifest.json',dict(schema='nbo-r13-extension-seal-v1',canonical_manifest_sha256=digest(HERE/'canonical/manifest.json'),files=files))
    print('EXTENSION CHECKS PASSED',flush=True)
if __name__=='__main__':main()
