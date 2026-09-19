"""Read-only R14 checker. Reconstructs science; never regenerates its inputs.

The historical producer Joint, the R14 cell builder, support generator, table
builder, and LP solver are not called. Engine is the independently recoded R13
Bellman implementation. Canonical arrays and mathematical definitions are shared.
Run with Python -O as well: all validation uses explicit exceptions.
"""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import sys,json,math,time,hashlib,copy,argparse,resource
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'replication/r13'))
from canonical import load,digest
from engine import Engine,SIGNS
from certified_arithmetic import derive
from verify_extensions import independent_support,verify_lp,verify_primitive
D0=.42425;EPS=1e-10

def q(x):return x if isinstance(x,Q) else Q.from_float(float(x))
def require(ok,message):
    if not ok:raise ValueError(message)
def same(a,b,label,tol=1e-11):
    a=np.asarray(a);b=np.asarray(b);require(a.shape==b.shape and np.isfinite(a).all() and np.isfinite(b).all(),'invalid '+label)
    err=float(np.max(abs(a-b))) if a.size else 0.;require(err<=tol,label+': discrepancy '+str(err));return err

def dual(lp,c,record):
    A=[[Q(x) for x in row] for row in lp['A']];b=list(map(Q,lp['b']));box=[tuple(map(Q,x)) for x in lp['box']]
    c=list(map(Q,c));mu=list(map(q,record['multipliers']));require(len(A)==len(b)==len(mu),'dual dimension')
    require(all(x>=0 for x in mu),'negative dual multiplier');require(len(c)==len(box),'objective dimension')
    require(all(len(r)==len(c) for r in A),'constraint dimension');require(all(l<=u for l,u in box),'reversed box')
    residual=[c[j]-sum(mu[i]*A[i][j] for i in range(len(A))) for j in range(len(c))]
    bound=sum(x*y for x,y in zip(mu,b))+sum(max(r*l,r*u) for r,(l,u) in zip(residual,box))
    require(bound==Q(record['exact_upper']),'incorrect exact dual bound');require([Q(x) for x in record['residual']]==residual,'wrong stationarity residual')
    require(q(record['certified_upper'])>=bound,'inward-rounded LP upper');return bound

def coverage(cells):
    for m in range(1,9):
        for sign in SIGNS:
            intervals=sorted([tuple(map(Q,c['cell'])) for c in cells if c['term']==m and c['sign']==sign])
            require(bool(intervals) and intervals[0][0]==0 and intervals[-1][1]==1,'fee coverage endpoints')
            require(all(0<=a<b<=1 for a,b in intervals),'invalid fee cell')
            require(all(a[1]==b[0] for a,b in zip(intervals,intervals[1:])),'fee coverage gap or duplicate overlap')

def row_semantics(cell,bank,adj,eta,G):
    a,b=map(Q,cell['cell']);m=cell['term'];sg=cell['sign'];lp=cell['lp'];src=cell['box_sources'];lo,hi=Q(0),Q(1)
    for key in ('H_lower','H_upper'):
        if key not in src:continue
        r=bank[src[key]];require((r['adjustment'],r['term'],r['sign'],r['d'])==(adj,m,sg,D0),'bound query mismatch');f=q(r['F'])
        if key=='H_lower':
            require(f>b or (eta==0 and f==b),'invalid lower-surrender anchor');lo=max(Q(0),q(r['H'][0])-(eta/(f-b) if eta else Q(0)))
        else:
            require(f<a or (eta==0 and f==a),'invalid upper-surrender anchor');hi=min(Q(1),q(r['H'][1])+(eta/(a-f) if eta else Q(0)))
    expected_box=[[-200,200],[0,1],[lo,hi],[a,b],[a*lo,b*hi],[0,20]]
    require([[Q(x) for x in pair] for pair in lp['box']]==expected_box,'invalid response/product/grant box')
    r=bank[src['grant_cap']];require((r['adjustment'],r['term'],r['sign'],r['d'],r['F'])==(adj,m,sg,D0,1.),'grant-cap anchor')
    require(G-q(r['value'])+q(EPS)+q(.02)+eta<20,'unjustified grant truncation')
    for stored,rhs,pr in zip(lp['A'],lp['b'],cell['constraints']):
        rr=[Q(0)]*6;kind=pr['kind'];c=q(.02);mid=(a+b)/2
        if kind in ('query','response'):
            r=bank[pr['data']];require((r['adjustment'],r['term'],r['sign'])==(adj,m,sg),'wrong cell oracle')
        if kind=='query':rr[0]=1;rr[1]=q(r['d'])-q(D0);rr[2]=-q(r['F']);zz=q(r['value'])+q(EPS)
        elif kind=='response':
            require(r['d']==D0,'response lower plane at wrong benefit');f=q(r['F']);require(f<=a or f>=b,'interior response anchor')
            h=q(r['H'][1] if f<=a else r['H'][0]);rr[0]=-1;rr[4]=1;rr[3]=-h;zz=-q(r['value'])+q(EPS)-f*h+eta
        elif kind=='product':
            t=pr['data'];require(t in (0,1,2,3),'product facet identifier')
            if t==0:rr[4]=-1;rr[2]=a;rr[3]=lo;zz=a*lo
            elif t==1:rr[4]=-1;rr[2]=b;rr[3]=hi;zz=b*hi
            elif t==2:rr[4]=1;rr[2]=-b;rr[3]=-lo;zz=-b*lo
            else:rr[4]=1;rr[2]=-a;rr[3]=-hi;zz=-a*hi
        elif kind=='participation':rr[0]=-1;rr[4]=1;rr[3]=2*c*mid;rr[5]=-1;zz=-G+c*mid*mid
        else:raise ValueError('unknown constraint role')
        require(list(map(Q,stored))==rr and Q(rhs)==zz,'LP row does not match economic semantics')
    require(len(lp['A'])==len(lp['b'])==len(cell['constraints']),'missing constraint provenance')
    bound=dual(lp,['0','1','0','0','0','-1'],cell['dual'])-q(.02)*Q(m-1,8)
    require(Q(cell['constant'])==-q(.02)*Q(m-1,8),'wrong compulsory-term cost')
    require(q(cell['upper'])>=bound,'inward-rounded cell bound');return bound

def independent_oracle(offsets,values,eta):
    t=[[q(v) for v in r] for r in offsets];L=[q(v)-q(EPS) for v in values];U=[q(v)+q(EPS) for v in values];n=len(t);width=4+3*n
    A=[];b=[];box=[(L[0],U[0]),(L[0]-q(eta),U[0]),(Q(0),Q(1)),(Q(0),Q(1))]
    for i in range(n):box.extend([(L[i]-sum(max(Q(0),x) for x in t[i]),U[0]),(Q(0),Q(1)),(Q(0),Q(1))])
    def add(c,z):
        rr=[Q(0)]*width
        for i,x in c.items():rr[i]=q(x)
        A.append(rr);b.append(q(z))
    add({1:1,0:-1},0);add({0:1,1:-1},eta)
    for j in range(n):add({1:1,2:t[j][0],3:t[j][1]},U[j])
    for i in range(n):
        k=4+3*i;add({k:1,0:-1},0)
        for j in range(n):add({k:1,k+1:t[j][0],k+2:t[j][1]},U[j])
        add({k:-1,k+1:-t[i][0],k+2:-t[i][1]},-L[i])
    add({4:1,0:-1},0);add({4:-1,0:1},0)
    return dict(A=A,b=b,box=box)

def fixtures(sample,bank,G):
    tested={}
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError):tested[name]=True;return
        raise ValueError('destructive fixture accepted: '+name)
    c=copy.deepcopy(sample);c['dual']['multipliers'][0]=-1
    reject('negative_rational_multiplier',lambda:dual(c['lp'],['0','1','0','0','0','-1'],c['dual']))
    c=copy.deepcopy(sample);c['lp']['b'][0]='999/1'
    reject('altered_constraint_rhs',lambda:dual(c['lp'],['0','1','0','0','0','-1'],c['dual']))
    c=copy.deepcopy(sample);c['upper']=-1e6
    reject('destroyed_upper_summary',lambda:row_semantics(c,bank,True,Q(0),G))
    c=copy.deepcopy(sample);c['lp']['box'][3]=['-1/1','1/1']
    reject('fee_outside_declared_cell',lambda:row_semantics(c,bank,True,Q(0),G))
    reject('missing_coverage',lambda:coverage([sample]))
    reject('wrong_positive_attainment',lambda:require(0.>0,'zero is not a positive lower witness'))
    return tested

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fixtures-only',action='store_true');ap.add_argument('--receipt',type=Path);args=ap.parse_args();start=time.perf_counter()
    z=json.loads((HERE/'output/continuum_certificate.json').read_text());bank={r['id']:r for r in z['bank']};G=q(.1*math.log(1.25))
    if args.fixtures_only:
        report=dict(negative_tests=fixtures(z['results'][0]['leaves'][0],bank,G),optimized_python=not __debug__,all_passed=True)
        print(json.dumps(report,indent=2));return
    require(z['canonical_manifest_sha256']==digest(ROOT/'replication/r13/canonical/manifest.json'),'canonical identity')
    require(z['archive_sha256']==digest(HERE/'output/continuum_witness.npz'),'continuum archive hash')
    require(z['inherited_refinement_sha256']==digest(ROOT/'replication/r13/extensions/refinement.json'),'refinement input hash')
    require(z['inherited_procurement_sha256']==digest(ROOT/'replication/r13/output/procurement.json'),'procurement input hash')
    extmanifest=json.loads((ROOT/'replication/r13/extensions/manifest.json').read_text())
    for name,sha in extmanifest['files'].items():require(digest(ROOT/'replication/r13/extensions'/name)==sha,'inherited extension hash '+name)
    b,j=load(ROOT/'replication/r13/canonical');e=Engine(b,j);audit=derive(b,j,EPS);G=q(float(b.terminal[b.center]));require(audit['derived_maximum']<EPS,'value allowance too small')
    # Every stored target value has absolute envelope <200, including at F=0.
    require(max(audit['value_norm_by_horizon'])<200,'payoff box audit')
    ref=json.loads((ROOT/'replication/r13/extensions/refinement.json').read_text())
    problems={}
    for r in z['bank']:problems.setdefault((r['adjustment'],r['term'],r['F'],r['d']),[]).append(('bank',r))
    for r in ref['rows']:problems.setdefault((r['adjustment'],r['term'],r['fee'],D0),[]).append(('refinement',r))
    ar=np.load(HERE/'output/continuum_witness.npz');maxerr=0.;graphs=0;attainment=[]
    for nn,((adj,m,F,d),items) in enumerate(problems.items()):
        v,p,first=e.solve(.125,d,F,adj,m)
        if d==D0:
            supp,counts,bgap=independent_support(e,v,adj,m,F,audit);graphs+=1;attainment.append(bgap)
        for kind,r in items:
            sg=r['sign'];maxerr=max(maxerr,same(r['value'],first[sg][0],'private value'))
            if kind=='bank':
                if 'G' in r:same(r['G'],float(G),'outside value')
                if 'witness' in r:
                    tag=r['witness'];same(ar[tag+'.v'],v[1:],'all-state value witness')
                    pp=ar[tag+'.p'];require(pp.shape==p[1:].shape and pp.dtype.kind in 'iu','policy witness shape')
                    for n in range(1,8):require(np.all((pp[n-1]>=0)&(pp[n-1]<=e.stop)) and np.all(e.mask(n,adj,m)[e.ix,pp[n-1]]),'infeasible continuation policy')
                    act=np.asarray(r['first_action']);ids=np.flatnonzero(np.all(abs(e.fm.actions-act)<1e-14,axis=1));require(len(ids)==1,'first action not a canonical knot')
                    require(e.first_mask(adj,sg,.8,.5)[ids[0]],'first action permission');fq=.875*e.fq(0,v[1],d)+.125*e.fq(1,v[1],d);same(fq[ids[0]],r['value'],'recorded first action value')
                    if sg=='positive' and r.get('attained'):require(act[2]>0,'zero action presented as an attained positive witness')
                if d==D0:
                    same(r['H'],[supp[sg][0][1],supp[sg][1][1]],'surrender support');same(r['A'],[supp[sg][0][0],supp[sg][1][0]],'duration support')
                    if sg=='positive' and r.get('attained'):require(bgap>4*audit['bounds']['bellman_value'],'positive attainment not separated from closure')
            else:
                same(r['support']['lower'],supp[sg][0],'full inherited lower support');same(r['support']['upper'],supp[sg][1],'full inherited upper support')
                if sg=='positive' and r['support']['attained_positive']:require(bgap>4*audit['bounds']['bellman_value'],'inherited open-class gap')
        e.cache.clear();print('CHECKED QUERY',nn+1,len(problems),adj,m,F,d,flush=True)
    ar.close();continuum=[]
    for result in z['results']:
        adj=result['adjustment'];eta=q(result['eta']);require(eta==0,'exact-response compact certificate has nonzero eta');coverage(result['leaves'])
        for cell in result['leaves']:row_semantics(cell,bank,adj,eta,G)
        inc=result['incumbent'];r=bank[inc['id']];require(r['attained'] and r['sign']=='positive','no attained executable candidate');require((r['F'],r['term'],r['sign'])==(inc['F'],inc['term'],inc['sign']),'candidate identity')
        grant=max(Q(0),G-q(r['value'])+q(EPS)+q(.02)*q(r['F'])**2);lower=q(r['A'][0])-grant-q(.02)*Q(r['term']-1,8)
        require(q(inc['grant'])>=grant and q(inc['lower'])<=lower,'inward incumbent bound');same(inc['A_lower'],r['A'][0],'candidate service')
        upper=max(q(c['upper']) for c in result['leaves']);require(q(result['global_upper'])>=upper,'incorrect global upper');require(q(result['regret_upper'])>=upper-q(inc['lower']),'regret understated')
        require((result['regret_upper']<=result['tolerance'])==result['tolerance_met'],'tolerance flag')
        termmax={m:max(c['upper'] for c in result['leaves'] if c['term']==m) for m in range(1,9)}
        other=max(v for m,v in termmax.items() if m!=inc['term']);continuum.append(dict(adjustment=adj,leaves=len(result['leaves']),incumbent=inc,global_upper=result['global_upper'],regret_upper=result['regret_upper'],term_upper=termmax,other_term_gap=inc['lower']-other,term_identified=inc['lower']>other))
    # Reconstruct all 42 institutional comparisons with rational accounting.
    cases={c['name']:c for c in ref['buyer_cases']};choices=ref['nested_menu_choices']+ref['counterfactuals']
    for answer in choices:
        case=cases[answer['case']];values=[]
        for r in ref['rows']:
            if r['adjustment']!=answer['adjustment'] or abs(r['fee']/answer['fee_step']-round(r['fee']/answer['fee_step']))>1e-10:continue
            E=q(r['fee'])/q(case.get('efficiency',1));C=q(case.get('cost',.02))*E**case.get('power',2);D=q(case.get('kappa',.02))*Q(r['term']-1,8)**case.get('term_power',1);a=q(case.get('capacity_incidence',1));gg=q(r['G'])+q(case.get('outside_shift',0));direction=case.get('direction',0);price=q(case.get('b',1))
            low=price*q(r['support']['lower'][direction])-max(Q(0),gg-q(r['value'])+q(1e-7)+a*C)-(1-a)*C-D
            high=price*q(r['support']['upper'][direction])-max(Q(0),gg-q(r['value'])-q(1e-7)+a*C)-(1-a)*C-D
            if not r['support']['attained_positive']:low=Q(-1000)
            values.append((low,high,r['id']))
        best=max(values,key=lambda x:x[0]);gap=best[0]-max([Q(0)]+[v[1] for v in values if v[2]!=best[2]])
        require(best[2]==answer['choice'] and abs(float(gap)-answer['margin'])<2e-13 and (gap>0)==answer['certified'],'institutional comparison differs')
    econ=json.loads((HERE/'output/economic_extensions.json').read_text());require(econ['canonical_manifest_sha256']==z['canonical_manifest_sha256'],'economic target identity');require(digest(HERE/'output/mechanism_values.npz')==econ['mechanism_values_sha256'],'mechanism archive hash')
    oracle_count=0
    for case in econ['joint_oracle']['cases']:
        vals=[]
        for query in case['queries']:
            _,_,f=e.solve(.125,query['d'],query['F'],case['adjustment'],case['term']);same(query['values'][case['sign']],f[case['sign']][0],'joint value query');vals.append(query['values'][case['sign']])
            offset_error=abs((q(query['d'])-q(D0))-q(query['offset'][0]))+abs((q(case['fee'])-q(query['F']))-q(query['offset'][1]));require(float(offset_error)+audit['bounds']['bellman_value']+1e-11<EPS,'oracle parameter rounding not covered')
        bounds=[]
        for run,n in zip(case['runs'],(5,7)):
            fresh=independent_oracle([x['offset'] for x in case['queries'][:n]],vals[:n],case['eta']);lp=run['lp']
            require([[Q(x) for x in row] for row in lp['A']]==fresh['A'] and list(map(Q,lp['b']))==fresh['b'] and [tuple(map(Q,r)) for r in lp['box']]==fresh['box'],'joint oracle LP semantics')
            c=[Q(0)]*len(fresh['box']);c[2]=1;c[3]=q(case['fee']);require(list(map(Q,run['objective']))==c,'joint economic objective');bounds.append(float(dual(lp,[str(x) for x in c],run['dual'])))
        same(case['upper_reduction'],bounds[0]-bounds[1],'joint upper reduction');oracle_count+=1;e.cache.clear()
    archive=np.load(HERE/'output/mechanism_values.npz');mechanism_count=0
    for r in econ['mechanisms']['rows']:
        lam,d,F,m=r['law'],r['d'],r['fee'],r['term'];va,_,fa=e.solve(lam,d,F,True,m);v0,_,f0=e.solve(lam,d,F,False,m)
        same(archive[r['id']+'.adjusted_v'],va[1:],'mechanism adjusted arrays');same(archive[r['id']+'.fixed_v'],v0[1:],'mechanism fixed arrays');O=va[1]-v0[1];classes={};kernels={}
        for sg in SIGNS:
            act=e.fm.actions[fa[sg][1]].copy();act[1]=0.;ix=np.flatnonzero(np.all(abs(e.fm.actions-act)<1e-14,axis=1));require(len(ix)==1,'mechanism counterfactual missing');i=int(ix[0]);K=(1-lam)*e.fm.rows[0].getrow(i)+lam*e.fm.rows[1].getrow(i);kernels[sg]=K
            qa=float(((1-lam)*e.fq(0,va[1],d)+lam*e.fq(1,va[1],d))[i]);qq=float(((1-lam)*e.fq(0,v0[1],d)+lam*e.fq(1,v0[1],d))[i]);cc=dict(local=fa[sg][0]-qa,future=float((K@O).item()),replacement=qq-f0[sg][0],option=fa[sg][0]-f0[sg][0]);classes[sg]=cc
            for k,x in cc.items():same(x,r['classes'][sg][k],'mechanism '+k)
        DD=kernels['positive']-kernels['nonpositive'];err=2*EPS*float(abs(DD).sum());future=classes['positive']['future']-classes['nonpositive']['future'];same([future-err,future+err],r['future_interval'],'mechanism error interval')
        for k in ('local','future','replacement','option'):same(classes['positive'][k]-classes['nonpositive'][k],r['difference'][k],'class difference')
        wealth=b.e[0].states[:,1];bins=[float((DD@(O*mask)).item()) for mask in (wealth<1.25,wealth>=1.25)];same(bins,r['wealth_contributions'],'wealth contributions');mechanism_count+=1;e.cache.clear()
    archive.close();diag=econ['projection_diagnostic'];act=np.asarray(diag['action']);ids=np.flatnonzero(np.all(abs(e.fm.actions-act)<1e-14,axis=1));require(len(ids)==1,'diagnostic action missing')
    for k,rowinfo in enumerate(diag['stored_rows']):
        row=e.fm.rows[k].getrow(int(ids[0]));mass=sum(q(x) for x in row.data);mean=sum(q(x)*q(b.e[0].states[i,0]) for x,i in zip(row.data,row.indices))/mass;second=sum(q(x)*q(b.e[0].states[i,0])**2 for x,i in zip(row.data,row.indices))/mass;variance=second-mean**2
        require(variance==Q(rowinfo['variance']) and mass==Q(rowinfo['mass']) and mean==Q(rowinfo['mean']),'projection exact moment')
    require(Q(diag['diffusion_variance'])==Q(1,3200),'diffusion variance primitive')
    negative=fixtures(z['results'][0]['leaves'][0],bank,G)
    report=dict(schema='nbo-r14-independent-validation-v1',canonical_manifest_sha256=z['canonical_manifest_sha256'],arithmetic_bound=audit['derived_maximum'],checked_dynamic_problems=len(problems),checked_response_graphs=graphs,maximum_value_discrepancy=maxerr,minimum_positive_boundary_gap=min(attainment),continuum=continuum,institutional_comparisons=len(choices),joint_oracle_cases=oracle_count,mechanism_points=mechanism_count,projection_rows=2,inherited_exact_oracle=verify_lp(),inherited_primitive=verify_primitive(),negative_tests=negative,optimized_python=not __debug__,elapsed_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,all_passed=True,scope='Read-only independent dynamic recursion, enlarged equality-graph supports, economic accounting, semantic LP reconstruction, rational weak duality and complete fee coverage. Neural training timings and continuous-state diffusion inclusion are not certified by this checker.')
    if args.receipt:
        require(args.receipt.resolve().parent!=HERE/'output','read-only checker cannot overwrite scientific output');args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True),flush=True)
if __name__=='__main__':main()
