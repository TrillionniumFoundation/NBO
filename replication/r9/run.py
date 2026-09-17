"""Executed R9 economic analysis. Run from repository root, no network/training."""
from contracts import *
import argparse
from scipy.optimize import brentq

def verify_inputs():
    manifests=['revisions/2026-09-17-r8-full-response/protected_history.json','revisions/2026-09-17-r8-full-response/source_inventory.json']
    inventory={};checked=0
    for name in manifests:
        p=ROOT/name;expected=json.loads(p.read_text())
        inventory[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        for path,h in expected.items():
            # R8 generated tables and build prose are not source inputs here.
            if name.endswith('source_inventory.json') and not path.startswith('replication/r8/'):continue
            q=ROOT/path
            if not q.exists() or hashlib.sha256(q.read_bytes()).hexdigest()!=h:raise RuntimeError('historical input changed: '+path)
            checked+=1
    paths=['replication/r4/solver.py','replication/r6/transport.py','replication/r6/kernel_certificate.py','replication/r7/core.py','replication/r8/model.py','replication/r8/numerical_core.py']+[f'replication/r4/output/safe_policy_{s}.npz' for s in (101,202,303)]
    inventory.update({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
    return dict(checked_files=checked,sha256=inventory,base_commit='8c20474bca5b7388f5ba4640ec165f1ad8f5e91a',reviewed_scientific_commit='be77b2a81b4d3a68806c534c1e892d2eb4b1230d')

def summarized(c,z,lam,d):
    row={}
    for s,it in z.items():
        f=c.moments(it['policy'],lam);point=f[:,0,c.center]
        err=float(np.max(abs(it['value']-(f[0]+d*f[1]-c.fee*f[2]))))
        assert err<2e-11
        row[s]=dict(value=float(it['value'][0,c.center]),action=c.initial_action(it['policy']),base=float(point[0]),duration=float(point[1]),discounted_surrender=float(point[2]),effort=float(point[3]),feature_replay_error=err)
    row['delta']=row['positive']['value']-row['nonpositive']['value']
    row['duration_difference']=row['positive']['duration']-row['nonpositive']['duration']
    row['surrender_difference']=row['positive']['discounted_surrender']-row['nonpositive']['discounted_surrender']
    row['participation_payment']=max(0.,float(c.terminal[c.center])-max(row[s]['value'] for s in SIGNS))
    return row

def surrender(base):
    results=[];policies={};baseline_error=0.
    specs=[(f,1) for f in (0.,.4,.6,.65,.7,.75,.78,.8,.82,.85,.9,1.)]+[(0.,m) for m in (2,3,4,5,6,7,8)]
    for f,m in specs:
        c=Contract(base,f,m);r=dict(fee=f,min_term=m,lam=.125,d=.425)
        for adj in (True,False):
            z=c.pair(.125,.425,adj);r['adjusted' if adj else 'no_adjustment']=summarized(c,z,.125,.425)
            for s,it in z.items():policies[f'{f}.{m}.{adj}.{s}']=it['policy']
            if m==8:
                ref=base.class_pair(.125,.425,adj)
                for s in SIGNS:baseline_error=max(baseline_error,float(np.max(abs(ref[s]['value']-z[s]['value']))))
        r['relative_option']=r['adjusted']['delta']-r['no_adjustment']['delta']
        results.append(r);print('SURRENDER',f,m,r['adjusted']['delta'],r['no_adjustment']['delta'],flush=True)
    grid=[]
    for f in (0.,.7,.8,.85):
        c=Contract(base,f,1)
        for lam,d in ((0.,.4),(0.,.45),(.25,.4),(.25,.45),(.125,.425)):
            r=dict(fee=f,lam=lam,d=d,min_term=1)
            for adj in (True,False):
                z=c.pair(lam,d,adj)
                r['adjusted' if adj else 'no_adjustment']=summarized(c,z,lam,d)
                for sign,it in z.items():policies[f'grid.{f}.{lam}.{d}.{adj}.{sign}']=it['policy']
            r['relative_option']=r['adjusted']['delta']-r['no_adjustment']['delta'];grid.append(r)
    residuals=[]
    for lam in (0.,.25):
        for n in range(base.steps):
            q=(1-lam)*base.q(0,n,base.terminal,.45)+lam*base.q(1,n,base.terminal,.45)
            z=q-base.terminal[:,None]
            residuals.append(dict(lam=lam,date=n,max_interior=float(z[~base.e[0].boundary].max()),max_boundary_abs=float(abs(z[base.e[0].boundary]).max())))
    assert max(x['max_interior'] for x in residuals)<0 and baseline_error<2e-12
    free=[x for x in results if x['fee']==0 and x['min_term']==1][0]
    no=[x for x in results if x['min_term']==8][0]
    # Absolute values obey fee and minimum-term orders; differences need not.
    for regime in ('adjusted','no_adjustment'):
        for s in SIGNS:
            vs=[x[regime][s]['value'] for x in results if x['min_term']==1]
            assert np.max(np.diff(vs))<2e-12
            ms=sorted([x for x in results if x['fee']==0],key=lambda x:x['min_term'])
            assert np.max(np.diff([x[regime][s]['value'] for x in ms]))<2e-12
    save('surrender.json',dict(center=results,original_region_grid=grid,supersolution=residuals,baseline_max_replay_error=baseline_error,
        noncancellable_participation_saving=no['no_adjustment']['participation_payment']-no['adjusted']['participation_payment']))
    np.savez_compressed(OUT/'surrender_policies.npz',**policies)

def reachable_fee(base):
    N=base.steps;reachable=np.zeros((N+1,base.ns),bool);reachable[0,base.center]=True
    for n in range(N):
        for e in base.e:
            for k in [e.common]+([e.extra[n]] if e.extra else []):
                if k.matrix is None:raise ValueError('baseline CSR expected')
                z=k.matrix.T@np.repeat(reachable[n].astype(float),k.na)
                reachable[n+1]|=z>0
    c=Contract(base,0.,N);policies=[c.pair(lam,.4,False)['positive']['policy'] for lam in (0.,.25)]
    coeff=[c.coefficients(p,.4,0.,all_dates=True) for p in policies]
    bounds=[];allbounds=[];where=[]
    cuts=np.linspace(0.,.25,17)
    for m in range(1,N+1):
        worst=0.;allworst=0.;loc=None
        for n in range(m,N):
            for a,b in zip(cuts[:-1],cuts[1:]):
                lower=np.maximum.reduce([r7.restrict(co[n],a,b).min(0) for co in coeff])-1e-7
                deficit=base.terminal-lower;eligible=reachable[n] & ~base.e[0].boundary
                now=float(np.max(deficit[eligible])) if eligible.any() else 0.
                if now>worst:
                    worst=now;j=np.where(eligible)[0][np.argmax(deficit[eligible])];loc=dict(date=n,state=base.e[0].states[j],lambda_cell=[a,b])
                allworst=max(allworst,float(np.max(deficit[~base.e[0].boundary])))
        bounds.append(worst);allbounds.append(allworst);where.append(loc)
    result=dict(reachable_counts=reachable.sum(1),minimum_terms=list(range(1,N+1)),sufficient_fee_bounds=bounds,all_node_sufficient_bounds=allbounds,locations=where,
        region=[0.,.25,.4,.45],policy_bank='two no-adjustment noncancellable policies at lambda endpoints and d=0.4',arithmetic_allowance=1e-7,
        interpretation='sufficient bounds, not minimal initial-state fees; all controls and both endpoint kernels enter reachability, so the bounds cover both adjustment regimes')
    save('reachable_fee.json',result)
    np.savez_compressed(OUT/'reachable_fee_coefficients.npz',reachable=reachable,**{f'policy.{i}':p for i,p in enumerate(policies)},**{f'coefficient.{i}.{n}':cc for i,co in enumerate(coeff) for n,cc in enumerate(co)})
    print('REACHABLE FEES',bounds,flush=True)

def permission_analysis(base):
    fm=FirstDateMenu(base);c=Contract(base,0.,base.steps);rows=[];oldmatch=0.;rootrows=[]
    contracts=[(lam,d) for lam in (0.,.125,.25) for d in (.4,.425,.45)]
    for lam,d in contracts:
        row=dict(lam=lam,d=d)
        for adj in (True,False):
            z=c.pair(lam,d,adj);v=z['positive']['value'][1];q=fm.values(v,lam,d)
            nominal=fm.optimize(v,lam,d,adj,cached=q)
            oldmatch=max(oldmatch,max(abs(nominal[s]['value']-z[s]['value'][0,c.center]) for s in SIGNS))
            out={}
            for L,S in ((.8,.5),(.82,.5),(.8,.51)):
                zz=fm.optimize(v,lam,d,adj,long=L,short=S,cached=q)
                delta=zz['positive']['value']-zz['nonpositive']['value']
                out[f'{L}.{S}']=dict(classes=zz,delta=delta)
            def spread(L,S):
                zz=fm.optimize(v,lam,d,adj,long=L,short=S,cached=q)
                return zz['positive']['value']-zz['nonpositive']['value']
            lroot=brentq(lambda L:spread(L,.5),.7,.9,xtol=2e-12)
            sroot=brentq(lambda S:spread(.8,S),.42,.58,xtol=2e-12)
            slopeL=risk_slope(base,v,lam,nominal['positive']['action']);slopeS=-risk_slope(base,v,lam,nominal['nonpositive']['action'])
            eps=1e-5
            fdL=(spread(.8+eps,.5)-spread(.8-eps,.5))/(2*eps)
            fdS=-(spread(.8,.5+eps)-spread(.8,.5-eps))/(2*eps)
            assert max(abs(slopeL-fdL),abs(slopeS-fdS))<2e-8
            out.update(long_switch=lroot,short_switch=sroot,long_shadow=slopeL,short_shadow=slopeS,shadow_fd_error=max(abs(slopeL-fdL),abs(slopeS-fdS)))
            row['adjusted' if adj else 'no_adjustment']=out
        rows.append(row);print('PERMISSIONS',lam,d,row['adjusted']['long_switch'],row['no_adjustment']['long_switch'],flush=True)
    # Reoptimize the continuation as d moves: not a frozen-policy threshold.
    for lam in (0.,.125,.25):
        for adj in (True,False):
            cache={}
            def target(d,L,S,details=False):
                if d not in cache:
                    z=c.pair(lam,d,adj);v=z['positive']['value'][1];cache[d]=(z,v,fm.values(v,lam,d))
                z,v,q=cache[d];zz=fm.optimize(v,lam,d,adj,long=L,short=S,cached=q)
                delta=zz['positive']['value']-zz['nonpositive']['value']
                if not details:return delta
                ff=c.moments(z['positive']['policy'],lam)[:,1]
                moments={s:first_moments(base,ff,lam,zz[s]['action']) for s in SIGNS}
                return zz,moments
            for L,S in ((.8,.5),(.82,.5),(.8,.51)):
                fl,fh=target(.05,L,S),target(.8,L,S)
                if fl*fh>0:raise ValueError('unbracketed benefit crossing')
                droot=brentq(lambda d:target(d,L,S),.05,.8,xtol=2e-10)
                zz,features=target(droot,L,S,True)
                da=float(features['positive'][1]-features['nonpositive'][1]);assert da>0
                lo=droot-1e-6;hi=droot+1e-6
                rootrows.append(dict(lam=lam,adjustment=adj,long=L,short=S,root=droot,bracket=[lo,hi],endpoint_differences=[target(lo,L,S),target(hi,L,S)],duration_difference=da,
                    long_shadow=risk_slope(base,cache[droot][1],lam,zz['positive']['action']),short_shadow=-risk_slope(base,cache[droot][1],lam,zz['nonpositive']['action']),initial_actions={s:zz[s]['action'] for s in SIGNS}))
                print('BENEFIT ROOT',lam,adj,L,S,droot,flush=True)
    assert oldmatch<2e-11
    save('permissions.json',dict(knots=fm.nknots,risky_domain=[fm.lower,fm.upper],common_consumption_adjustment_pairs=len(fm.pairs),nominal_full_continuum_vs_finite_error=oldmatch,permission_roots=rows,benefit_roots=rootrows,
        scope='continuous FIRST-DATE risky share, finite inherited c/theta pairs and frozen proposals, unchanged later full menu; exact breakpoint reduction under the verified no-exit premise, floating-point evaluations, no claim of continuous consumption/adjustment or diffusion optimization'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('all','economics','certificates','permissions','reachable'),default='all');args=ap.parse_args()
    inputs=verify_inputs();save('input_provenance.json',inputs)
    base=Model();save('environment.json',dict(python=sys.version,numpy=np.__version__,platform=platform.platform(),build_seconds=base.build_seconds,kernel_bytes=base.nbytes,backend_checks=base.backend_checks))
    if args.mode in ('all','economics'):surrender(base)
    if args.mode in ('all','reachable'):reachable_fee(base)
    if args.mode in ('all','permissions'):permission_analysis(base)
    if args.mode in ('all','certificates'):
        for fs,ms,nm in (((0.,),8,'noncancellable_certificate.json'),((.8,),1,'fee_080_certificate.json'),((.85,.9),1,'fee_085_090_certificate.json')):
            ans=region_certificate(base,fees=fs,min_term=ms,name=nm)
            print('CERTIFICATE',nm,[(r['method'],r['bounds'],r['signs_certified']) for r in ans['methods']],flush=True)
if __name__=='__main__':main()
