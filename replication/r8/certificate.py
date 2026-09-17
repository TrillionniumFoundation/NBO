"""Decision-specific streaming certificate contest on one common economic target.
Every arm pays for full-menu upper anchors; mesh-only lower banks are separately
solved and evaluated.  No uncharged neural construction enters the new arms.
"""
from model import *
from arithmetic import audit

def upper_pair(mix,a,b,d,za,zb,adjust,method):
    if mix.steps==1:
        return {s:np.array([za[s]['value'][0,mix.center],zb[s]['value'][0,mix.center]]) for s in ('positive','nonpositive')}
    if method=='count':
        prev=mix.terminal[None,:]
        for n in range(mix.steps-1,-1,-1):
            h=mix.steps-n;z=np.empty((h+1,mix.ns))
            z[0]=za['positive']['value'][n];z[h]=zb['positive']['value'][n]
            candidates={}
            if h>1:
                q0=mix.q(0,n,prev[0],d);q1=mix.q(1,n,prev[0],d)
                previous=(1-b)*q0+b*q1
                for j in range(1,h):
                    q0=mix.q(0,n,prev[j],d);q1=mix.q(1,n,prev[j],d)
                    qa=(1-a)*q0+a*q1
                    q=(1-j/h)*qa+j/h*previous
                    z[j]=np.where(r7.mask(mix,n,adjust),q,-np.inf).max(1)
                    if n==0:
                        candidates[j]={s:np.where(r7.mask(mix,n,adjust,s),q,-np.inf).max(1) for s in ('positive','nonpositive')}
                    previous=(1-b)*q0+b*q1
            if n==0:
                out={}
                for sign in ('positive','nonpositive'):
                    co=z[:,mix.center].copy();co[0]=za[sign]['value'][n,mix.center];co[-1]=zb[sign]['value'][n,mix.center]
                    for j in range(1,h):co[j]=candidates[j][sign][mix.center]
                    out[sign]=co
                return out
            prev=z
    elif method=='chord':
        m=np.zeros(mix.ns)
        for n in range(mix.steps-2,-1,-1):
            diff=zb['positive']['value'][n+1]-za['positive']['value'][n+1]
            D=(b-a)*(r7.continuation(mix,0,n,diff)-r7.continuation(mix,1,n,diff))
            if n<mix.steps-2:
                k0=r7.continuation(mix,0,n,m);k1=r7.continuation(mix,1,n,m)
                D+=np.maximum((1-a)*k0+a*k1,(1-b)*k0+b*k1)
            if n==0:
                out={};h=mix.steps;j=np.arange(h+1)
                for sign in ('positive','nonpositive'):
                    m0=max(0.,float(np.where(r7.mask(mix,n,adjust,sign),D,-np.inf).max(1)[mix.center]))
                    out[sign]=(1-j/h)*za[sign]['value'][0,mix.center]+j/h*zb[sign]['value'][0,mix.center]+j*(h-j)/(h*(h-1))*m0
                return out
            m=np.maximum(0.,np.where(r7.mask(mix,n,adjust),D,-np.inf).max(1))
    raise ValueError(method)

def focal_coefficients(mix,policy,d):
    """Rolling backward evaluation: no all-date coefficient tensor retained."""
    prev=mix.terminal[None,:]
    for n in range(mix.steps-1,-1,-1):
        h=mix.steps-n;z=[]
        for j in range(h+1):
            v=np.zeros(mix.ns)
            if j<h:v+=(1-j/h)*mix.selected(0,n,policy[n],prev[j],d)
            if j>0:v+=j/h*mix.selected(1,n,policy[n],prev[j-1],d)
            z.append(v)
        prev=np.stack(z)
    return prev[:,mix.center]

def run(mix=None,region=(0.,.25,.4,.45),methods=('chord','count'),name='decision_contest.json',save_arrays=True):
    if mix is None:mix=Model()
    a,b,dl,dh=region;bank={};checks=[];policies={}
    tic=time.perf_counter()
    for adj in (True,False):
        for t in (a,b):
            for d in (dl,dh):
                pair=mix.class_pair(t,d,adj)
                bank[adj,t,d]=pair
    anchor_seconds=time.perf_counter()-tic
    lower={};tic=time.perf_counter();evaluation_seconds=0.;validation_seconds=0.
    for adj in (True,False):
        for t in (a,b):
            for d in (dl,dh):
                for sign,item in bank[adj,t,d].items():
                    p=item['policy'];t0=time.perf_counter()
                    co0=focal_coefficients(mix,p,0.);co1=focal_coefficients(mix,p,1.)
                    lower[adj,t,d,sign]=(co0,co1-co0)
                    evaluation_seconds+=time.perf_counter()-t0
                    t0=time.perf_counter();dv=mix.direct(p,t,d)
                    err=float(abs(dv-item['value']).max())
                    replay=abs(float(r7.bernstein_value(co0+d*(co1-co0),t))-float(dv[0,mix.center]))
                    assert max(err,replay)<2e-11
                    checks.append(dict(adjustment=adj,theta=t,d=d,sign=sign,value=float(dv[0,mix.center]),direct_error=err,coefficient_error=replay))
                    validation_seconds+=time.perf_counter()-t0
                    policies[f'{adj}.{t}.{d}.{sign}']=p
    # A deliberately conservative allowance under the documented arithmetic model.
    audit_start=time.perf_counter();arithmetic=audit(mix,b-a);validation_seconds+=time.perf_counter()-audit_start
    e=arithmetic['per_class_allowance']
    rows=[];upper_store={}
    for method in methods:
        t0=time.perf_counter();up={}
        for adj in (True,False):
            for d in (dl,dh):
                zz=upper_pair(mix,a,b,d,bank[adj,a,d],bank[adj,b,d],adj,method)
                for sign,co in zz.items():up[adj,d,sign]=co
        upper_seconds=time.perf_counter()-t0;upper_store[method]=up
        t0=time.perf_counter();bounds={};class_gaps={}
        for adj in (True,False):
            U={s:np.stack([up[adj,d,s] for d in (dl,dh)]) for s in ('positive','nonpositive')}
            L={s:[] for s in U}
            for sign in U:
                for t in (a,b):
                    for anchor_d in (dl,dh):
                        c0,c1=lower[adj,t,anchor_d,sign]
                        L[sign].append(np.stack([r7.restrict(c0+d*c1,a,b) for d in (dl,dh)]))
            lower_bound=max(float((l-U['nonpositive']).min()) for l in L['positive'])-2*e
            upper_bound=min(float((U['positive']-l).max()) for l in L['nonpositive'])+2*e
            bounds['adjusted' if adj else 'fixed']=[lower_bound,upper_bound]
            class_gaps['adjusted' if adj else 'fixed']={s:max(0.,min(float((U[s]-l).max()) for l in L[s]))+2*e for s in U}
        certification_seconds=time.perf_counter()-t0
        rows.append(dict(method=method,lower_bank='full_menu',bounds=bounds,class_gaps=class_gaps,
            signs_certified=bounds['adjusted'][0]>0 and bounds['fixed'][1]<0,
            upper_seconds=upper_seconds,certificate_seconds=certification_seconds,
            build_seconds=mix.build_seconds,anchor_seconds=anchor_seconds,evaluation_seconds=evaluation_seconds,
            independent_validation_seconds=validation_seconds,
            total_seconds=mix.build_seconds+anchor_seconds+evaluation_seconds+validation_seconds+upper_seconds+certification_seconds))
    # Non-neural bank: same upper target, common mesh unchanged, all proposal
    # exclusions apply to the LOWER policy construction only.
    tic=time.perf_counter();mesh_bank={};mesh_lower={};mesh_checks=[]
    for adj in (True,False):
        for t in (a,b):
            for d in (dl,dh):
                mesh_bank[adj,t,d]=mix.class_pair(t,d,adj,mesh_only=True)
    mesh_anchor_seconds=time.perf_counter()-tic
    tic=time.perf_counter()
    for key,pair in mesh_bank.items():
        adj,t,d=key
        for sign,item in pair.items():
            p=item['policy'];assert p.max()<len(mix.e[0].menu)
            co0=focal_coefficients(mix,p,0.);co1=focal_coefficients(mix,p,1.)
            mesh_lower[adj,t,d,sign]=(co0,co1-co0)
            direct=mix.direct(p,t,d)
            err=float(abs(direct-item['value']).max());assert err<2e-11
            mesh_checks.append(dict(adjustment=adj,theta=t,d=d,sign=sign,direct_error=err,value=float(direct[0,mix.center])))
    mesh_evaluation_seconds=time.perf_counter()-tic
    up=upper_store['chord'];t0=time.perf_counter();bounds={}
    for adj in (True,False):
        U={s:np.stack([up[adj,d,s] for d in (dl,dh)]) for s in ('positive','nonpositive')}
        L={s:[] for s in U}
        for sign in U:
            for t in (a,b):
                for ad in (dl,dh):
                    c0,c1=mesh_lower[adj,t,ad,sign]
                    L[sign].append(np.stack([r7.restrict(c0+d*c1,a,b) for d in (dl,dh)]))
        bounds['adjusted' if adj else 'fixed']=[max(float((l-U['nonpositive']).min()) for l in L['positive'])-2*e,min(float((U['positive']-l).max()) for l in L['nonpositive'])+2*e]
    certify=time.perf_counter()-t0
    chord_row=next(r for r in rows if r['method']=='chord')
    rows.append(dict(method='chord',lower_bank='mesh_only',bounds=bounds,
        signs_certified=bounds['adjusted'][0]>0 and bounds['fixed'][1]<0,
        build_seconds=mix.build_seconds,upper_anchor_seconds=anchor_seconds,
        lower_anchor_seconds=mesh_anchor_seconds,lower_evaluation_validation_seconds=mesh_evaluation_seconds,
        upper_seconds=chord_row['upper_seconds'],certificate_seconds=certify,
        total_seconds=mix.build_seconds+anchor_seconds+mesh_anchor_seconds+mesh_evaluation_seconds+chord_row['upper_seconds']+certify))
    if 'count' in upper_store:
        dominance=min(float((upper_store['chord'][key]-value).min()) for key,value in upper_store['count'].items())
        assert dominance>-2e-11
    else:dominance=None
    npz={}
    for method,U in upper_store.items():
        for key,v in U.items():npz[f'upper.{method}.{key}']=v
    for label,L in [('full',lower),('mesh',mesh_lower)]:
        for key,(c0,c1) in L.items():npz[f'lower.{label}.{key}']=np.stack([c0,c1])
    if save_arrays:
        np.savez_compressed(OUT/(name.removesuffix('.json')+'_coefficients.npz'),**npz)
        np.savez_compressed(OUT/(name.removesuffix('.json')+'_policies.npz'),**policies)
    out=dict(specification=mix.spec.__dict__,region=region,rows=rows,checks=checks,mesh_checks=mesh_checks,
        count_chord_min_coefficient_gap=dominance,per_class_arithmetic_allowance=e,arithmetic=arithmetic,
        kernel_and_reward_bytes=mix.nbytes,retained_focal_lower_coefficient_bytes=sum(x.nbytes+y.nbytes for x,y in lower.values()),
        retained_policy_bytes=sum(x.nbytes for x in policies.values()),
        maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        timing_protocol='common setup charged identically; full-menu anchors and independently replayed lower policies included; single serial pass, not independent-machine medians',
        target='finite eight-date lottery-settlement economy; no diffusion-error budget inferred')
    save(name,out);print(json.dumps(r7.serial(out),indent=2),flush=True);return out

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--nx',type=int,default=49);ap.add_argument('--dl',type=float,default=.4);ap.add_argument('--dh',type=float,default=.45);ap.add_argument('--name',default='decision_contest.json')
    args=ap.parse_args();run(Model(Specification(nx=args.nx)),region=(0.,.25,args.dl,args.dh),name=args.name)
