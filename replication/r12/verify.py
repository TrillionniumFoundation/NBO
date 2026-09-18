"""Witness-driven checker: identities, independently recoded recursions and economic inequalities."""
from __future__ import annotations
import argparse,itertools,json,time,tempfile
from pathlib import Path
import numpy as np
from canonical import load,check,digest,dump,csr_load
from engine import Engine,SIGNS,EPS,close,restrict

def identity(target,out):
    seal=json.loads((out/'expected.json').read_text())
    if seal['schema']!='nbo-r12-witness-v1':raise ValueError('unknown witness schema')
    check(target,seal['canonical_manifest_sha256'])
    for name,sha in seal['files'].items():
        if Path(name).name!=name or digest(out/name)!=sha:raise ValueError('witness identity: '+name)
    return seal

def reduce_region(arr,method,box):
    a,b=box['law'];lo={};up={}
    for t in range(3):
        for s in SIGNS:
            co=arr[f'{method}.lower.{t}.{s}']
            if co.ndim!=3 or co.shape[1:]!=(4,9) or not np.isfinite(co).all():raise ValueError('lower coefficient inventory')
            lo[t,s]=np.stack([[restrict(c,a,b) for c in p] for p in co])
            up[t,s]=arr[f'{method}.upper.0.{t}.{s}']
            if up[t,s].shape!=(4,9) or not np.isfinite(up[t,s]).all():raise ValueError('upper coefficient inventory')
    def diff(t1,s1,t0,s0):
        low=max(float((p-up[t0,s0]).min()) for p in lo[t1,s1])-2*EPS
        high=min(float((up[t1,s1]-p).max()) for p in lo[t0,s0])+2*EPS
        if low>high:raise ValueError('inconsistent regional interval')
        return [low,high]
    bounds=dict(adjusted=diff(0,'positive',0,'nonpositive'),zero=diff(1,'positive',1,'nonpositive'),active_surrender_gain=diff(1,'positive',2,'positive'))
    if not(bounds['adjusted'][0]>0 and bounds['zero'][1]<0 and bounds['active_surrender_gain'][0]>0):raise ValueError('regional signs not established')
    return bounds

def regional(eng,arr,out):
    B=eng.box;corners=list(itertools.product(B['benefit'],B['fee']));res={};maxgap=0.;policies=0;uppers=0
    for method in ('chord','count'):
        for t,(adj,m) in enumerate(((True,1),(False,1),(False,8))):
            for s in SIGNS:
                bank=arr[f'{method}.lower.{t}.{s}']
                for i,cc in enumerate(bank):
                    p=arr[f'{method}.policy.{t}.{s}.{i}'];action=arr[f'{method}.first.{t}.{s}.{i}']
                    for c,(d,F) in enumerate(corners):
                        co=eng.coefficients(p,action,adj,m,s,d,F,B['long'][0],B['short'][0])
                        maxgap=max(maxgap,close(co,cc[c],'primitive-to-lower polynomial'))
                    policies+=1
            for c,(d,F) in enumerate(corners):
                uu=eng.upper(*B['law'],d,F,adj,m,B['long'][1],B['short'][1],method)
                for s in SIGNS:maxgap=max(maxgap,close(uu[s],arr[f'{method}.upper.0.{t}.{s}'][c],'all-state upper recursion'))
                uppers+=1
        bounds=reduce_region(arr,method,B);summary=json.loads((out/(method+'_certificate.json')).read_text())
        for name,value in bounds.items():close(value,summary['bounds'][name],'summary-to-witness region')
        res[method]=bounds;print('VERIFIED REGION',method,flush=True)
    return dict(bounds=res,policies_checked=policies,upper_corner_recursions=uppers,max_coefficient_discrepancy=maxgap)

def transport(eng,arr,out):
    b=eng.b;B=eng.box;N=eng.N;R=np.zeros((N+1,eng.S),bool);R[0,b.center]=True
    good=eng.first_mask(True,'positive',B['long'][1],B['short'][1])|eng.first_mask(True,'nonpositive',B['long'][1],B['short'][1])
    for k in (0,1):R[1]|=np.asarray(eng.fm.rows[k][good].sum(0)).ravel()>0
    for n in range(1,N):
        for e in b.e:
            for z in (e.common,e.extra[n]):R[n+1]|=np.asarray(z.matrix.T@np.repeat(R[n].astype(float),z.na)).ravel()>0
    if not np.array_equal(R,arr['reachable']):raise ValueError('full feasible-support mismatch')
    lo=np.zeros((N+1,eng.S));hi=np.zeros_like(lo);lo[-1]=hi[-1]=b.terminal
    for n in range(N-1,0,-1):
        q0=eng.q(0,n,lo[n+1],B['benefit'][0],B['fee'][1]);q1=eng.q(1,n,lo[n+1],B['benefit'][0],B['fee'][1])
        q=np.minimum(*[(1-l)*q0+l*q1 for l in B['law']]);lo[n]=np.where(eng.mask(n,True,1,True),q,-np.inf).max(1)-EPS
        q0=eng.q(0,n,hi[n+1],B['benefit'][1],B['fee'][0]);q1=eng.q(1,n,hi[n+1],B['benefit'][1],B['fee'][0])
        q=np.maximum(*[(1-l)*q0+l*q1 for l in B['law']]);hi[n]=np.where(eng.mask(n,True,1,True),q,-np.inf).max(1)+EPS
    close(lo,arr['interval_lower'],'statewise lower enclosure');close(hi,arr['interval_upper'],'statewise upper enclosure')
    if np.any(lo>hi):raise ValueError('reversed continuation enclosure')
    records=[];menu=b.e[0].menu;lookup={tuple(np.round(a,13)):i for i,a in enumerate(menu)}
    neg=np.flatnonzero(menu[:,1]<-1e-14);zero=np.array([lookup[(round(menu[i,0],13),0.,round(menu[i,2],13))] for i in neg])
    for n in range(N-1,-1,-1):
        mid=(lo[n+1]+hi[n+1])/2;rad=(hi[n+1]-lo[n+1])/2;ix=np.flatnonzero(R[n]&~b.e[0].boundary);parts=[]
        if n:
            if np.any(b.e[0].extra[n].actions[ix,:,1]<-1e-14):raise ValueError('unpaired downward frozen proposal')
            rn=(ix[:,None]*len(menu)+neg).ravel();rz=(ix[:,None]*len(menu)+zero).ravel()
            for e in b.e:
                z=e.common;D=z.matrix[rn]-z.matrix[rz];reward=z.base-b.spec.cost*z.effort
                dr=(reward[ix[:,None],neg]-reward[ix[:,None],zero]).ravel();dd=(z.duration[ix[:,None],neg]-z.duration[ix[:,None],zero]).ravel()
                parts.append(dr+np.maximum(B['benefit'][0]*dd,B['benefit'][1]*dd)+D@mid+abs(D)@rad)
        else:
            a=eng.fm.actions;lookup0={tuple(np.round(x,13)):i for i,x in enumerate(a)};ni=np.flatnonzero(good&(a[:,1]<-1e-14));zi=np.array([lookup0[(round(a[i,0],13),0.,round(a[i,2],13))] for i in ni])
            for k in (0,1):
                D=eng.fm.rows[k][ni]-eng.fm.rows[k][zi];dr=eng.fm.reward[k][ni]-eng.fm.reward[k][zi];dd=eng.fm.duration[k][ni]-eng.fm.duration[k][zi]
                parts.append(dr+np.maximum(B['benefit'][0]*dd,B['benefit'][1]*dd)+D@mid+abs(D)@rad)
        upper=max(float(((1-l)*parts[0]+l*parts[1]).max()) for l in B['law'])+2*EPS
        if upper>=0:raise ValueError('directional dominance not established')
        records.append(upper)
    original=json.loads((out/'dominance.json').read_text());close(records,[r['negative_minus_zero_upper'] for r in original['dates']],'transport summary')
    return dict(reachable_counts=R.sum(1).tolist(),negative_minus_zero_upper=records)

def procurement(eng,out):
    src=json.loads((out/'procurement.json').read_text());G=float(eng.b.terminal[eng.b.center]);h=.01;eta=1e-8;rows=[];maxgap=0.
    with np.load(out/'procurement_witness.npz',allow_pickle=False) as data:
        for adj,F,m in itertools.product((True,False),(0.,.2,.4,.6,.8,1.),range(1,9)):
            key=f'{int(adj)}.{F:.1f}.{m}';vals=[]
            for shift in (-1,0,1):
                v,p,first=eng.solve(.125,.42425+shift*h,F,adj,m);tag=key+f'.{shift}';vals.append(first)
                maxgap=max(maxgap,close(v[1:],data[tag+'.values'],'complete procurement Bellman values'))
                close([first[s][0] for s in SIGNS],data[tag+'.first_values'],'procurement first optimization')
                witness=data[tag+'.policy']
                if witness.shape!=(eng.N,eng.S) or witness.dtype.kind not in 'iu':raise ValueError('procurement policy inventory')
                for n in range(1,eng.N):
                    if np.any(witness[n]<0) or np.any(witness[n]>eng.stop) or not eng.mask(n,adj,m)[eng.ix,witness[n]].all():raise ValueError('procurement policy feasibility')
                    q=(1-.125)*eng.selected(0,n,witness[n],v[n+1],.42425+shift*h,F)+.125*eng.selected(1,n,witness[n],v[n+1],.42425+shift*h,F)
                    close(q,v[n],'procurement policy optimality')
                for si,s in enumerate(SIGNS):
                    action=data[tag+'.first_actions'][si];ids=np.flatnonzero(np.all(abs(eng.fm.actions-action)<1e-14,axis=1))
                    if len(ids)!=1 or not eng.first_mask(adj,s,.8,.5)[ids[0]]:raise ValueError('procurement first feasibility')
                    q=.875*eng.fq(0,v[1],.42425+shift*h)+.125*eng.fq(1,v[1],.42425+shift*h)
                    close(q[ids[0]],first[s][0],'procurement first selected value')
            for s in SIGNS:
                wm,w,wp=[f[s][0] for f in vals];lo=max(0.,(w-wm-2*EPS-eta)/h);hi=min(1.,(wp-w+2*EPS+eta)/h)
                if lo>hi:raise ValueError('service interval empty')
                rows.append(dict(id=key+'.'+s,adjustment=adj,fee=F,term=m,service_lower=lo,service_upper=hi,grant_executable=max(0.,G-w+EPS+.02*F*F+eta),grant_lower=max(0.,G-w-EPS+.02*F*F)))
            print('VERIFIED PROCUREMENT',key,flush=True)
    byid={r['id']:r for r in src['rows']}
    for r in rows:
        for name in ('service_lower','service_upper','grant_executable','grant_lower'):close(r[name],byid[r['id']][name],'procurement accounting summary')
    corners=[]
    for b,kap,adj in itertools.product((.998,1.02),(.0198,.0202),(True,False)):
        rr=[r for r in rows if r['adjustment']==adj]
        lo=np.array([b*r['service_lower']-r['grant_executable']-kap*(r['term']-1)/8 for r in rr]);hi=np.array([b*r['service_upper']-r['grant_lower']-kap*(r['term']-1)/8 for r in rr]);best=int(lo.argmax())
        gap=lo[best]-max([0.]+[float(x) for i,x in enumerate(hi) if i!=best])
        if gap<=0:raise ValueError('menu choice not certified at a price-box vertex')
        corners.append(dict(b=b,kappa=kap,adjustment=adj,choice=rr[best]['id'],margin=float(gap)))
    for want in src['choices']:
        b=want['b'];kap=want['kappa'];rr=[r for r in rows if r['adjustment']==want['adjustment']]
        lo=np.array([b*r['service_lower']-r['grant_executable']-kap*(r['term']-1)/8 for r in rr]);hi=np.array([b*r['service_upper']-r['grant_lower']-kap*(r['term']-1)/8 for r in rr]);best=int(lo.argmax())
        if lo[best]<0:choice='outside';gap=-float(max(hi))
        else:choice=rr[best]['id'];gap=float(lo[best]-max([0.]+[float(v) for i,v in enumerate(hi) if i!=best]))
        if choice!=want['choice'] or gap<=0:raise ValueError('uncertified point procurement choice')
        close(gap,want['margin'],'point procurement summary')
    for adj in (True,False):
        if len({x['choice'] for x in corners if x['adjustment']==adj})!=1:raise ValueError('nonuniform price-box choice')
    for got,want in zip(corners,src['box_corners']):
        if got['choice']!=want['choice']:raise ValueError('stale menu selection')
        close(got['margin'],want['margin'],'price-box summary')
    return dict(offers=len(rows),bellman_parameter_queries=96*3,price_box_corners=corners,max_value_discrepancy=maxgap)

def diagnostics(eng,out):
    exp=json.loads((out/'exposure.json').read_text());largest=0.
    for row in exp['rows']:
        lam,d,F,m=[row[k] for k in ('law','benefit','fee','term')]
        va,_,fa=eng.solve(lam,d,F,True,m);vz,_,fz=eng.solve(lam,d,F,False,m);O=va[1]-vz[1];rr={};kk={}
        for sign in SIGNS:
            action=eng.fm.actions[fa[sign][1]].copy();action[1]=0.
            i=int(np.flatnonzero(np.all(abs(eng.fm.actions-action)<1e-14,axis=1))[0]);K=(1-lam)*eng.fm.rows[0].getrow(i)+lam*eng.fm.rows[1].getrow(i);kk[sign]=K
            qa=((1-lam)*eng.fq(0,va[1],d)+lam*eng.fq(1,va[1],d))[i];qz=((1-lam)*eng.fq(0,vz[1],d)+lam*eng.fq(1,vz[1],d))[i]
            rr[sign]=dict(local=fa[sign][0]-qa,future=float((K@O).item()),financial_replacement=qz-fz[sign][0],option=fa[sign][0]-fz[sign][0])
            for key,value in rr[sign].items():largest=max(largest,close(value,row['classes'][sign][key],'exposure reconstruction'))
        D=kk['positive']-kk['nonpositive'];uncertainty=2*EPS*float(abs(D).sum());future=float((D@O).item())
        close([future-uncertainty,future+uncertainty],row['future_interval'],'signed exposure enclosure')
        wealth=eng.b.e[0].states[:,1];bins=[float((D@(O*((wealth>=a)&(wealth<b)))).item()) for a,b in ((0,1.25),(1.25,3))]
        close(bins,row['wealth_bin_contributions'],'wealth-bin exposure')
    broad=json.loads((out/'broader.json').read_text())
    for row in broad['rows']:
        a,b=row['law'];adj=row['adjustment'];va,pa,fa=eng.solve(a,.42425,.8,adj,1);vb,pb,fb=eng.solve(b,.42425,.8,adj,1)
        co={sign:[eng.coefficients(p,eng.fm.actions[f[sign][1]],adj,1,sign,.42425,.8,.8,.5) for p,f in ((pa,fa),(pb,fb))] for sign in SIGNS}
        upper={method:eng.upper(a,b,.42425,.8,adj,1,.8,.5,method) for method in ('chord','count')}
        correction=max(float(np.max(upper['chord'][sign]-np.linspace(fa[sign][0],fb[sign][0],9))) for sign in SIGNS)
        difference=max(float(np.max(abs(upper['chord'][sign]-upper['count'][sign]))) for sign in SIGNS)
        close(correction,row['max_chord_correction'],'broad correction');close(difference,row['max_chord_count_difference'],'broad coefficient comparison')
        for method in upper:
            gap=0.
            for sign in SIGNS:
                for aa,bb in zip(np.linspace(0,1,9)[:-1],np.linspace(0,1,9)[1:]):
                    U=restrict(upper[method][sign],aa,bb)
                    gap=max(gap,min(float(np.max(U-restrict(c,a+(b-a)*aa,a+(b-a)*bb))) for c in co[sign])+2*EPS)
            close(gap,row['per_value_uniform_gap'][method],'broad precision gap')
        print('VERIFIED BROADER',a,b,adj,flush=True)
    return dict(exposure_cases=len(exp['rows']),broad_law_regime_cases=len(broad['rows']),max_exposure_discrepancy=largest,timing_scope='Generator wall-clock times are measurements, not independently reproduced equalities.')

def negative_tests(eng,arr,target,out):
    results={}
    def rejects(name,fn):
        try:fn()
        except (ValueError,AssertionError,KeyError,IndexError) as e:results[name]=dict(rejected=True,reason=str(e))
        else:raise AssertionError('negative fixture accepted: '+name)
    bad=dict(arr);bad['chord.upper.0.0.positive']=np.full_like(arr['chord.upper.0.0.positive'],-1e6)
    rejects('referee_destroyed_upper_semantic',lambda:reduce_region(bad,'chord',eng.box))
    p=arr['chord.policy.0.positive.0'].copy();p[1,0]=eng.stop+17
    rejects('invalid_policy_semantic',lambda:eng.coefficients(p,arr['chord.first.0.positive.0'],True,1,'positive',.424,.7999,.7999,.4999))
    rejects('stale_summary_semantic',lambda:close([1.,2.],reduce_region(arr,'chord',eng.box)['adjusted'],'stale summary'))
    rejects('wrong_canonical_identity',lambda:check(target,'0'*64))
    matrix=eng.fm.rows[0];aa={f'csr.{k}':getattr(matrix,k).copy() for k in ('data','indices','indptr')};aa['csr.shape']=np.array(matrix.shape);aa['csr.data'][0]=-1.
    rejects('negative_transition_semantic',lambda:csr_load(aa))
    bb={k:v.copy() for k,v in aa.items()};bb['csr.data'][0]=2.
    rejects('excess_transition_mass_semantic',lambda:csr_load(bb))
    altered=arr['interval_upper'].copy();altered[2,3]=-1e6
    rejects('continuation_enclosure_semantic',lambda:close(altered,arr['interval_upper'],'corrupted continuation'))
    with tempfile.TemporaryDirectory() as td:
        fixture=Path(td)/'certificate_arrays.npz';np.savez_compressed(fixture,**bad)
        expected=json.loads((out/'expected.json').read_text())['files']['certificate_arrays.npz']
        def filecheck():
            if digest(fixture)!=expected:raise ValueError('certificate archive hash changed')
        rejects('mutated_certificate_file_identity',filecheck)
    return results

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--target',type=Path,default=Path(__file__).parent/'canonical');ap.add_argument('--out',type=Path,default=Path(__file__).parent/'output');args=ap.parse_args();start=time.perf_counter()
    seal=identity(args.target,args.out);b,j=load(args.target,seal['canonical_manifest_sha256']);eng=Engine(b,j)
    with np.load(args.out/'certificate_arrays.npz',allow_pickle=False) as z:arr={k:z[k] for k in z.files}
    result=dict(schema='nbo-r12-independent-check-v1',scope='Binary64 witness reconstruction with the stated analytic allowances; not a second real-interval implementation, neural retraining, or diffusion-target verification.',input_manifest_sha256=digest(args.out/'expected.json'))
    result['negative_tests']=negative_tests(eng,arr,args.target,args.out)
    result['regional']=regional(eng,arr,args.out);result['transport']=transport(eng,arr,args.out);result['procurement']=procurement(eng,args.out)
    result['diagnostics']=diagnostics(eng,args.out)
    result['elapsed_seconds']=time.perf_counter()-start;result['all_passed']=True;dump(args.out/'independent_validation.json',result);print('INDEPENDENT WITNESS CHECK PASSED',flush=True)
if __name__=='__main__':main()
