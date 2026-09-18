"""Generate R12 witnesses from immutable canonical inputs, never overwrite a target."""
from __future__ import annotations
import argparse,gc,itertools,json,os,time,resource
from pathlib import Path
import numpy as np
from canonical import ROOT,core,freeze,load,dump,digest
EPS=core.EPS
restrict=core.r7.restrict
from contracts import arithmetic_audit,Contract
SIGNS=core.SIGNS; ETA=1e-8; H=.01

def moments(j,z,lam):
    v=z['c'].moments(z['p'],lam)[:,1];out={}
    for s in SIGNS:
        f=z['first'][s];ix=f['indices'];w=f['weights'];ans=np.zeros(3)
        for k,prob in enumerate((1-lam,lam)):
            ans[0]+=prob*float(w@(j.fm.reward[k]+j.fm.rows[k]@v[0])[ix])
            ans[1]+=prob*float(w@(j.fm.duration[k]+j.fm.rows[k]@v[1])[ix])
            ans[2]+=prob*float(w@(j.fm.rows[k]@v[2])[ix])
        out[s]=ans
    return out

def evaluate(rows,b,kap,adj):
    rr=[r for r in rows if r['adjustment']==adj]
    lo=np.array([b*r['service_lower']-r['grant_executable']-kap*(r['term']-1)/8 for r in rr])
    hi=np.array([b*r['service_upper']-r['grant_lower']-kap*(r['term']-1)/8 for r in rr])
    best=int(lo.argmax())
    if lo[best]<0:return {'adjustment':adj,'b':b,'kappa':kap,'choice':'outside','margin':float(-max(hi))}
    rival=max([0.]+[float(v) for i,v in enumerate(hi) if i!=best])
    return {'adjustment':adj,'b':b,'kappa':kap,'choice':rr[best]['id'],'margin':float(lo[best]-rival),'profit_interval':[float(lo[best]),float(hi[best])]}

def procurement(j,out):
    rows=[];witness={};G=float(j.base.terminal[j.base.center])
    for adj in (True,False):
        for F in (0.,.2,.4,.6,.8,1.):
            for m in range(1,9):
                key=f'{int(adj)}.{F:.1f}.{m}';sol=[]
                for shift in (-1,0,1):
                    d=.42425+shift*H;z=j.solve(.125,d,F,adj,.8,.5,m);sol.append(z)
                    tag=key+f'.{shift}'
                    witness[tag+'.values']=z['v'][1:];witness[tag+'.policy']=z['p']
                    witness[tag+'.first_values']=np.array([z['first'][s]['value'] for s in SIGNS])
                    witness[tag+'.first_actions']=np.array([z['first'][s]['action'] for s in SIGNS])
                mm=moments(j,sol[1],.125)
                for s in SIGNS:
                    wm,w,wp=[z['first'][s]['value'] for z in sol]
                    B,A,inc=map(float,mm[s]);assert abs(B+.42425*A-F*inc-w)<2e-11
                    lower=max(0.,(w-wm-2*EPS-ETA)/H);upper=min(1.,(wp-w+2*EPS+ETA)/H)
                    assert lower-2e-11<=A<=upper+2e-11
                    rows.append(dict(id=key+'.'+s,adjustment=adj,fee=F,term=m,sign=s,value=w,
                        shifted_values=[wm,w,wp],service=A,surrender=inc,service_lower=lower,service_upper=upper,
                        grant_executable=max(0.,G-w+EPS+.02*F*F+ETA),grant_lower=max(0.,G-w-EPS+.02*F*F),
                        nominal_profit=A-max(0.,G-w+.02*F*F)-.02*(m-1)/8))
                j.cache.clear();gc.collect();print('PROCUREMENT',key,flush=True)
    choices=[evaluate(rows,b,.02,adj) for b in (.8,.9,.94,.98,1.,1.02,1.05) for adj in (True,False)]
    corners=[evaluate(rows,b,kap,adj) for b,kap,adj in itertools.product((.998,1.02),(.0198,.0202),(True,False))]
    for adj in (True,False):
        rr=[r for r in corners if r['adjustment']==adj]
        assert len({r['choice'] for r in rr})==1 and min(r['margin'] for r in rr)>0,rr
    dump(out/'procurement.json',dict(parameters=dict(law=.125,benefit=.42425,long=.8,short=.5,G=G,value_allowance=EPS,agent_tolerance=ETA,service_perturbation=H),rows=rows,choices=choices,price_box=dict(b=[.998,1.02],kappa=[.0198,.0202]),box_corners=corners))
    np.savez_compressed(out/'procurement_witness.npz',**witness)

def exposure(j):
    rows=[]
    for lam,d,F,m in ((.125,.42425,.8,1),(.125,.42425,0.,8),(.12,.424,0.,8),(.13,.4245,0.,8)):
        za=j.solve(lam,d,F,True,.8,.5,m);z0=j.solve(lam,d,F,False,.8,.5,m);O=za['v'][1]-z0['v'][1];classes={};kernels={}
        for s in SIGNS:
            f=za['first'][s];assert len(f['indices'])==1
            a=f['action'].copy();a[1]=0.;ix=np.where(np.all(np.abs(j.fm.actions-a)<1e-14,axis=1))[0];assert len(ix)==1;i=int(ix[0])
            K=(1-lam)*j.fm.rows[0].getrow(i)+lam*j.fm.rows[1].getrow(i);kernels[s]=K
            qa=float(((1-lam)*j.q(0,za['v'][1],d)+lam*j.q(1,za['v'][1],d))[i])
            q0=float(((1-lam)*j.q(0,z0['v'][1],d)+lam*j.q(1,z0['v'][1],d))[i])
            classes[s]=dict(local=f['value']-qa,future=float((K@O).item()),financial_replacement=q0-z0['first'][s]['value'],option=f['value']-z0['first'][s]['value'],first_action=f['action'])
        D=kernels['positive']-kernels['nonpositive'];rel={k:classes['positive'][k]-classes['nonpositive'][k] for k in ('local','future','financial_replacement','option')}
        assert abs(rel['option']-rel['local']-rel['future']-rel['financial_replacement'])<2e-11
        uncertainty=2*EPS*float(abs(D).sum());wealth=j.base.e[0].states[:,1]
        bins=[float((D@(O*((wealth>=a)&(wealth<b)))).item()) for a,b in ((0,1.25),(1.25,3))]
        rows.append(dict(law=lam,benefit=d,fee=F,term=m,classes=classes,relative=rel,future_interval=[rel['future']-uncertainty,rel['future']+uncertainty],wealth_bin_contributions=bins,signed_kernel_mass=float(D.sum())))
        j.cache.clear();gc.collect()
    return dict(scope='Pointwise accounting and signed-exposure enclosures, not a uniform primitive ordering.',rows=rows)

def broader(j):
    rows=[]
    for a,b in ((.12,.13),(0.,.25),(0.,1.)):
        for adj in (True,False):
            t=time.perf_counter();za=j.solve(a,.42425,.8,adj,.8,.5);zb=j.solve(b,.42425,.8,adj,.8,.5);endpoint=time.perf_counter()-t
            t=time.perf_counter();pol={s:[j.coefficients(z,s,.42425,.8) for z in (za,zb)] for s in SIGNS};lower_time=time.perf_counter()-t
            upp={};elapsed={}
            for method in ('chord','count'):
                t=time.perf_counter();upp[method]=j.upper(za,zb,a,b,.42425,.8,adj,.8,.5,method);elapsed[method]=time.perf_counter()-t
            lin={s:np.linspace(za['first'][s]['value'],zb['first'][s]['value'],9) for s in SIGNS}
            gaps={}
            for method in upp:
                maximum=0.
                for s in SIGNS:
                    for aa,bb in zip(np.linspace(0,1,9)[:-1],np.linspace(0,1,9)[1:]):
                        U=restrict(upp[method][s],aa,bb)
                        gap=min(float(np.max(U-restrict(p,a+(b-a)*aa,a+(b-a)*bb))) for p in pol[s])+2*EPS
                        maximum=max(maximum,gap)
                gaps[method]=maximum
            rows.append(dict(law=[a,b],adjustment=adj,max_chord_correction=max(float(np.max(upp['chord'][s]-lin[s])) for s in SIGNS),
                max_chord_count_difference=max(float(np.max(abs(upp['chord'][s]-upp['count'][s]))) for s in SIGNS),
                per_value_uniform_gap=gaps,endpoint_policy_switch_states=int(np.sum(za['p'][1:]!=zb['p'][1:])),matched_component_total_seconds={mm:endpoint+lower_time+elapsed[mm] for mm in elapsed},endpoint_seconds=endpoint,lower_policy_seconds=lower_time,nonendpoint_seconds=elapsed,
                endpoint_first_actions={s:[za['first'][s]['action'],zb['first'][s]['action']] for s in SIGNS}))
            j.cache.clear();gc.collect();print('BROAD',a,b,adj,flush=True)
    return dict(scope='Matched endpoints and lower-policy bank; neither wall-time dominance nor economic sign is presumed.',rows=rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--build-target',action='store_true');ap.add_argument('--target',type=Path,default=Path(__file__).parent/'canonical');ap.add_argument('--out',type=Path,default=Path(__file__).parent/'output');args=ap.parse_args()
    t=time.perf_counter();constructor_seconds=0.;freeze_seconds=0.
    if args.out.exists():raise FileExistsError('Output already exists: do not overwrite a sealed witness')
    if args.build_target:
        t0=time.perf_counter();b=core.Model();j=core.Joint(b);constructor_seconds=time.perf_counter()-t0
        t0=time.perf_counter();freeze(b,j,args.target);freeze_seconds=time.perf_counter()-t0;del b,j;gc.collect()
    t0=time.perf_counter();b,j=load(args.target);read_seconds=time.perf_counter()-t0;args.out.mkdir(parents=True)
    import importlib.util
    sp=importlib.util.spec_from_file_location('r11_array_identity',ROOT/'replication/r11/run.py');r11=importlib.util.module_from_spec(sp);sp.loader.exec_module(r11)
    oldpath=ROOT/'replication/r11/output/array_manifest.json'
    if oldpath.exists():
        old=json.loads(oldpath.read_text());new=r11.array_manifest(b,j)
        dump(args.out/'target_comparison.json',dict(scope='R12 is separately identified; matching signs are not an R11-to-R12 transfer proof.',entries=len(old),mismatches=[k for k in old if old[k]['sha256']!=new[k]['sha256']]))
    arith=arithmetic_audit(Contract(b,1.,1),1.,1.);dump(args.out/'arithmetic.json',arith)
    for method in ('chord','count'):
        z=j.region(method);assert z['certified'];dump(args.out/(method+'_certificate.json'),z);print('REGION',method,z['bounds'],flush=True)
    dom=j.dominance();assert dom['certified'];dump(args.out/'dominance.json',dom)
    np.savez_compressed(args.out/'certificate_arrays.npz',**j.artifacts);j.cache.clear();gc.collect()
    procurement(j,args.out);dump(args.out/'exposure.json',exposure(j));dump(args.out/'broader.json',broader(j))
    dump(args.out/'execution.json',dict(source_commit=os.getenv('R12_SOURCE_SHA',os.getenv('GITHUB_SHA','local-development')),canonical_load_seconds=read_seconds,constructor_seconds=constructor_seconds,canonical_freeze_seconds=freeze_seconds,elapsed_seconds=time.perf_counter()-t,kernel_payload_bytes=b.nbytes,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    expected=dict(schema='nbo-r12-witness-v1',canonical_manifest_sha256=digest(args.target/'manifest.json'),files={p.name:digest(p) for p in sorted(args.out.iterdir()) if p.is_file()})
    dump(args.out/'expected.json',expected);print('SEALED',digest(args.out/'expected.json'),flush=True)
if __name__=='__main__':main()
