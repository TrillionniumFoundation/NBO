"""Separate prospective adaptive comparison and controlled non-nullity study.

Primary R53 sources and observations are never altered. The adaptive cohort
uses a fresh stream and its own complete clocks; nuisance cases are deterministic
whole-cell diagnostics, not extra independent policy-cost observations.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,platform,resource,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import study53 as p
D=p.d;I=p.I;o=p.o;s=p.s;R=p.R
OUT=R/'results53-extension';METHODS=('compiled-witness','tensor-fvi','surplus-fvi')
GRID=(F(0),F(1,4096),F(1,256),F(1,16))

def freeze():
    p.verify_freeze()
    files=[R/'code/extend53.py',R/'STUDY_PROTOCOL53_EXTENSION.md',R/'audit/SOURCE_FREEZE53.json']
    p.save(R/'audit/SOURCE_FREEZE53_EXTENSION.json',dict(protocol_commit='7d9e7aee25f37f9633c45630a282d8820ea7e35b',
        source_sha256={str(x.relative_to(R)):p.digest(x) for x in files},time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        methods=METHODS,paths=p.PATHS,statistical_family_separate_from_primary=True,noise_catalogue_cases=384))

def verify():
    p.verify_freeze()
    for name,h in json.loads((R/'audit/SOURCE_FREEZE53_EXTENSION.json').read_text())['source_sha256'].items():
        if p.digest(R/name)!=h:raise AssertionError(name)
    return p.digest(R/'audit/SOURCE_FREEZE53_EXTENSION.json')

def service(method):
    frozen=verify();affinity=p.cpu_pin();start=time.perf_counter();cpu=time.process_time()
    folder=OUT/'services'/method
    if folder.exists():raise FileExistsError(folder)
    folder.mkdir(parents=True);prefix=[]
    for N,K,M in s.LADDERS[2]:
        if N>32:break
        t0=time.perf_counter()
        j=o.surplus_rung(N,K,M,2,1) if method=='surplus-fvi' else s.rung(N,K,M,2,1,method,2)
        h=p.save(folder/f'construction-N{N}-K{K}-M{M}.json',j)
        prefix.append(dict(N=N,K=K,M=M,seconds=time.perf_counter()-t0,counts=j['counts'],sha256=h,
                           original_bound_upper=j['policy_bound_upper'],nonuniform_date_models=j['nonuniform_date_models']))
    construction=time.perf_counter()-start;n=1<<p.BITS
    bins=np.stack(np.meshgrid(np.arange(n),np.arange(n),indexing='ij'),axis=-1).reshape(-1,2)
    actor=o.AcquiredPolicy(j,p.BITS)
    pol=np.array([np.rint(actor._cell_base(t,bins)*4096).astype(np.uint16).reshape(n,n) for t in range(2)])
    p.arrays(folder/'policy-pass0.npz',policy=pol)
    if method!='surplus-fvi':
        old=np.load(R/'results53/services'/f'{method}-T2/policy-pass0.npz')['policy']
        if not np.array_equal(old,pol):raise AssertionError('Primary policy not reconstructed')
    acquisition=time.perf_counter()-start-construction
    bound=[p.inference.support(2-t,1)[1] for t in range(2)]+[F(0)];hashes=[D.policy_digest(pol)]
    for k in range(2):
        t0=time.perf_counter();new,rec,raw=D.sweep(pol,p.BITS,p.Q,1)
        bound=[D.BETA*bound[t+1]+F(rec['dates'][t]['greedy_gap_upper']) for t in range(2)]+[F(0)]
        rec.update(pass_number=k+1,gap_upper_exact=list(map(str,bound)),gap_upper=[s.c.enclosure(x)[1] for x in bound])
        rec['records_sha256']=p.arrays(folder/f'pass{k+1}-cells.npz',**raw)
        rec['policy_file_sha256']=p.arrays(folder/f'policy-pass{k+1}.npz',policy=new)
        rec.update(seconds_through_outputs=time.perf_counter()-t0,prefix_seconds_through_outputs=time.perf_counter()-start)
        p.save(folder/f'pass{k+1}.json',rec)
        if method!='surplus-fvi':
            primary=np.load(R/'results53/services'/f'{method}-T2/policy-pass{k+1}.npz')['policy']
            if not np.array_equal(primary,new):raise AssertionError('Reproduction changed primary pass policy')
        pol=new;hashes.append(D.policy_digest(pol))
    rec=dict(method=method,T=2,p=1,d=2,source_freeze_sha256=frozen,reconstruction_prefix=prefix,
             construction_seconds=construction,acquisition_seconds=acquisition,snapshots=hashes,
             total_seconds_before_record=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,
             peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,affinity=affinity,
             nonuniform_date_models=j['nonuniform_date_models'],adaptive_geometry=j.get('adaptation_history',[]),
             python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),
             clock_scope='new same-runner cohort; all primitive prefixes, adaptive pilots, full sweeps and durable outputs; independent cost service separately charged')
    h=p.save(folder/'service.json',rec);p.save(folder/'clock.json',dict(service_sha256=h,seconds_through_record=time.perf_counter()-start))
    print(json.dumps(dict(method=method,seconds=time.perf_counter()-start,nonuniform=j['nonuniform_date_models'])),flush=True)

def direct():
    verify();p.cpu_pin();start=time.perf_counter();out=OUT/'direct'
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);keys=[];policies=[]
    for m in METHODS:
        for k in range(3):
            keys.append(f'{m}-pass{k}');policies.append(np.load(OUT/'services'/m/f'policy-pass{k}.npz')['policy'])
    seed=int.from_bytes(hashlib.sha256(b'NBO-R53-ADAPTIVE-FRESH-v1').digest()[:8],'big')
    rng=np.random.Generator(np.random.PCG64(seed));stream=hashlib.sha256();lows=np.empty((9,p.PATHS));highs=np.empty_like(lows);clocks=np.zeros(9)
    for begin in range(0,p.PATHS,4096):
        n=min(4096,p.PATHS-begin);idx=rng.integers(0,2**p.BIN_BITS,size=(3,n),dtype=np.uint64);stream.update(idx.tobytes());v=idx.astype(float)
        x=I(v[:2].T*2.**-p.BIN_BITS,(v[:2].T+1)*2.**-p.BIN_BITS)
        z=[I(-1/32+v[2]*2.**(-p.BIN_BITS-4),-1/32+(v[2]+1)*2.**(-p.BIN_BITS-4))]
        for j,pol in enumerate(policies):
            t0=time.perf_counter();score=p.path_score(pol,x,z);clocks[j]+=time.perf_counter()-t0
            lows[j,begin:begin+n]=score.lo;highs[j,begin:begin+n]=score.hi
    rawhash=p.arrays(out/'path-endpoints.npz',lower=lows,upper=highs);B=p.inference.support(2,1)[1]
    absolute={key:p.interval_record(lows[j],highs[j],F(0),B) for j,key in enumerate(keys)};contrasts={}
    def contrast(i,j,name):
        if np.array_equal(policies[i],policies[j]):rec=dict(identity=True,interval=[0.,0.],interval_exact=['0','0'],sign='zero')
        else:
            z=I(lows[i],highs[i])-I(lows[j],highs[j]);rec=p.interval_record(z.lo,z.hi,-B,B)
        contrasts[name]=rec
    for m,method in enumerate(METHODS):
        for k in (1,2):
            contrast(3*m,3*m+k,f'{method}-pass{k}-initial-gain')
            contrast(3*m+k-1,3*m+k,f'{method}-pass{k}-step-gain')
    for a,b in itertools.combinations(range(3),2):
        for k in range(3):contrast(3*a+k,3*b+k,f'{METHODS[a]}-minus-{METHODS[b]}-pass{k}')
    j=dict(T=2,paths=p.PATHS,bin_bits=p.BIN_BITS,seed=seed,stream_sha256=stream.hexdigest(),policy_keys=keys,
           policy_sha256=[D.policy_digest(x) for x in policies],absolute_cost=absolute,contrasts=contrasts,
           source_freeze_sha256=verify(),raw_endpoints_sha256=rawhash,evaluation_seconds=dict(zip(keys,clocks)),
           total_seconds_before_record=time.perf_counter()-start,family_maximum=128,family_error='1/100',log_upper=13,
           primary_family_separate=True,independence_scope='fresh independent-bin model; common paths across policies; no independence between estimands assumed',
           peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    h=p.save(out/'costs.json',j);p.save(out/'clock.json',dict(costs_sha256=h,seconds_through_record=time.perf_counter()-start))
    print(json.dumps(dict(costs={k:v['interval'] for k,v in absolute.items()})),flush=True)

def exposures(xi,lam):return F(1,2)+xi+lam,F(1,4)-xi/2-lam

def moved(x,a,xi,lam):
    y=o.deterministic_next(x,a)
    return y+s.stack([(xi+lam)*a,(-xi/2-lam)*a])

def true_contrast(x,a,b,xi,lam):
    ga,gb=exposures(xi,lam);delta=s.stack([ga*(a-b),gb*(a-b)])
    out=D.action_difference(a,b,1)+float(D.BETA)*D.state_difference(moved(x,a,xi,lam),moved(x,b,xi,lam),delta,True)
    same=(a.lo==b.lo)&(a.hi==b.hi)&(a.lo==a.hi);out.lo[same]=out.hi[same]=0
    return out

def nuisance_contrast(x,a,b,M,eta,xi,lam):
    ga,gb=exposures(xi,lam);slope=ga-(2+eta)*gb;da=a-b
    rho=abs(M*slope)*I.point(np.maximum(abs(da.lo),abs(da.hi)))
    if slope==0:return D.zero(len(a.lo)),D.zero(len(a.lo))
    xa=moved(x,a,xi,lam);xb=moved(x,b,xi,lam)
    va=s.col(xa,0)-(2+eta)*s.col(xa,1)+1;vb=s.col(xb,0)-(2+eta)*s.col(xb,1)+1
    total=D.zero(len(a.lo));delta=slope*da
    for j in range(16):
        z=I(np.full(len(a.lo),-1/32+j/256),np.full(len(a.lo),-1/32+(j+1)/256))
        total=total+D.positive_difference(va+(3+eta)*z,vb+(3+eta)*z,delta)
    out=M*(total/16)
    same=(a.lo==b.lo)&(a.hi==b.hi)&(a.lo==a.hi);out.lo[same]=out.hi[same]=0;rho.lo[same]=rho.hi[same]=0
    return out,rho

def diagnostics():
    frozen=verify();p.cpu_pin();start=time.perf_counter();out=OUT/'misspecification'
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);n=1<<p.BITS;bins=np.stack(np.meshgrid(np.arange(n),np.arange(n),indexing='ij'),axis=-1).reshape(-1,2)
    x=I(bins/n,(bins+1)/n);cap=(4096*(2*n+bins.sum(axis=1)))//(16*n);summaries=[]
    for method in METHODS[:2]:
        pol=np.load(R/'results53/services'/f'{method}-T2/policy-pass0.npz')['policy'];base=pol[-1].reshape(-1);b=I.point(base/4096)
        for ci,(M,eta,xi,lam) in enumerate(itertools.product((1,16,4096),GRID,GRID,GRID)):
            t0=time.perf_counter();best=np.zeros(n*n);wrongbest=best.copy();chosen=base.copy();wrong=base.copy();raw={};selected_hi=np.zeros(n*n);harmful_lo=np.zeros(n*n)
            accepted=blocked=0;maxrho=0.;null=exposures(xi,lam)[0]-(2+eta)*exposures(xi,lam)[1]==0
            for k in range(9):
                ai=(cap*k)//8;a=I.point(ai/4096);truth=true_contrast(x,a,b,xi,lam)
                nuisance,rho=nuisance_contrast(x,a,b,M,eta,xi,lam);maxrho=max(maxrho,float(rho.hi.max()))
                critic=truth-float(D.BETA)*nuisance
                corrected=truth if null else critic+float(D.BETA)*rho
                take=corrected.hi<best;bad=critic.hi<wrongbest
                chosen[take]=ai[take];selected_hi[take]=truth.hi[take];best[take]=corrected.hi[take]
                wrong[bad]=ai[bad];harmful_lo[bad]=truth.lo[bad];wrongbest[bad]=critic.hi[bad]
                different=ai!=base;accepted+=int(np.count_nonzero(different&(corrected.hi<0)));blocked+=int(np.count_nonzero(different&(corrected.hi>=0)))
                for name,v in [('true_lo',truth.lo),('true_hi',truth.hi),('nuisance_lo',nuisance.lo),('nuisance_hi',nuisance.hi),('rho_upper',rho.hi),('critic_upper',critic.hi),('corrected_upper',corrected.hi)]:raw[f'k{k}_{name}']=v
            if np.any(chosen>cap) or np.any(selected_hi>0):raise AssertionError('Misspecified safe gate invalid')
            raw.update(selected=chosen,false_null_selected=wrong,selected_true_upper=selected_hi,false_null_selected_true_lower=harmful_lo)
            name=f'{method}-{ci:03d}';h=p.arrays(out/(name+'.npz'),**raw)
            row=dict(key=name,method=method,M=M,eta=str(eta),xi=str(xi),innovation_mean_coefficient=str(lam),exact_null=null,
                changed_cells=int(np.count_nonzero(chosen!=base)),blocked_candidates=blocked,accepted_candidates=accepted,
                false_null_changed_cells=int(np.count_nonzero(wrong!=base)),false_null_certified_harmful_cells=int(np.count_nonzero((wrong!=base)&(harmful_lo>0))),
                contrast_bound_upper=maxrho,policy_sha256=D.policy_digest(chosen),records_sha256=h,
                largest_selected_true_upper=float(selected_hi.max()),seconds_through_outputs=time.perf_counter()-t0,
                primitive_contrast_queries=9*n*n,nuisance_bin_queries=0 if null else 9*16*n*n)
            summaries.append(row)
    j=dict(source_freeze_sha256=frozen,cases=summaries,cases_count=len(summaries),cells_per_case=n*n,
        total_seconds_before_record=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        statistical_observations=0,scope='explicit perturbed-kernel diagnostic; primary economic laws unchanged')
    h=p.save(out/'summary.json',j);p.save(out/'clock.json',dict(summary_sha256=h,seconds_through_record=time.perf_counter()-start))
    print(json.dumps(dict(cases=len(summaries),harmful_false_null=sum(r['false_null_certified_harmful_cells'] for r in summaries),seconds=time.perf_counter()-start)),flush=True)

def self_test():
    x=I.point([[0.,0.]]);a=I.point([0.]);b=I.point([.125]);M=4096;eta=F(1,16)
    exact=o.exact_q([F(0),F(0)],F(0),1)-o.exact_q([F(0),F(0)],F(1,8),1)
    val=true_contrast(x,a,b,F(0),F(0));nu,rho=nuisance_contrast(x,a,b,M,eta,F(0),F(0))
    assert F(val.lo[0])<=exact<=F(val.hi[0]) and exact>0
    assert (val-float(D.BETA)*nu).hi[0]<0
    assert (val-float(D.BETA)*nu+float(D.BETA)*rho).hi[0]>=float(exact)
    for eta,xi,lam in itertools.product(GRID,repeat=3):
        ga,gb=exposures(xi,lam);assert ga>0 and gb>0
        assert F(11,16)+max(ga,gb)/4+F(1,32)<1
        nu,rho=nuisance_contrast(x,a,b,16,eta,xi,lam)
        slope=ga-(2+eta)*gb;assert F(rho.hi[0])>=abs(16*slope)/8
        if slope==0:assert nu.lo[0]==nu.hi[0]==0
    print('R53 extension: exact false-null and 64 perturbed-domain checks passed')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--service',choices=METHODS);ap.add_argument('--direct',action='store_true');ap.add_argument('--diagnostics',action='store_true');ap.add_argument('--test',action='store_true');v=ap.parse_args()
    if v.test:self_test()
    elif v.freeze:freeze()
    elif v.service:service(v.service)
    elif v.direct:direct()
    elif v.diagnostics:diagnostics()
    else:ap.error('Choose an action')
