"""Prospective R62 execution. Every source is frozen before any production task."""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import hashlib,itertools,json,os,platform,resource,subprocess,sys,time
import numpy as np
import scipy
import core62 as c
import proposals62 as p
import study53 as stats
R=c.R;PATHS=65536;LOG=16;FAMILY=512

def freeze():
    path=R/'audit/SOURCE_FREEZE62.json'
    if path.exists():return verify()
    names=['PROTOCOL62.md','sections/accuracy62.tex']
    names += [str(f.relative_to(R)) for f in (R/'code').iterdir() if f.is_file() and f.suffix in ('.py','.cpp')]
    c.save(path,dict(baseline_commit='19f17cef194b620cfbf9d33e7c78ee051a2dddf0',review_commit='08ca068d318ce159401b36655eccea1e05490d01',utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),files_sha256={name:c.digest(R/name) for name in sorted(names)},scope='Frozen before R62 production. Correctness fixtures are disjoint; publication does not add observations.'))
    return verify()
def verify():
    path=R/'audit/SOURCE_FREEZE62.json';data=json.loads(path.read_text())
    for name,h in data['files_sha256'].items():c.need(c.digest(R/name)==h,'Frozen source changed: '+name)
    return c.digest(path)
def array_hash(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def write_arrays(path,**arrays):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(path,**arrays);return c.digest(path)
def endpoint_record(lo,hi,A,B):
    old=stats.LOG;stats.LOG=LOG
    try:return stats.interval_record(lo,hi,A,B)
    finally:stats.LOG=old

def direct(task,policies,sub,folder):
    start=time.perf_counter();d,m,T=task;keys=list(policies);ids=[array_hash(policies[k]) for k in keys]
    unique={};aliases={}
    for k,h in zip(keys,ids):
        if h not in unique:unique[h]=k
        aliases[k]=unique[h]
    uk=list(unique.values());actors={k:c.Actor(policies[k],d,sub) for k in uk}
    lower=np.empty((len(uk),PATHS));upper=lower.copy();clocks={k:0. for k in uk}
    rng=np.random.default_rng(620000+d*100+m*10+T);stream=hashlib.sha256();den=2**40
    for first in range(0,PATHS,4096):
        last=min(first+4096,PATHS);size=last-first;bins=rng.integers(0,den,size=(d+m*T,size),dtype=np.uint64);stream.update(bins.tobytes());v=bins.astype(float)
        x=c.I(v[:d].T/den,(v[:d].T+1)/den)
        z1=[c.I(-1/32+v[d+t]/(16*den),-1/32+(v[d+t]+1)/(16*den)) for t in range(T)]
        z2=[c.I(-1/64+v[d+T+t]/(32*den),-1/64+(v[d+T+t]+1)/(32*den)) for t in range(T)] if m==2 else []
        for j,k in enumerate(uk):
            then=time.perf_counter();val=c.path_cost(actors[k],x,z1,z2);clocks[k]+=time.perf_counter()-then
            lower[j,first:last]=val.lo;upper[j,first:last]=val.hi
    H=c.support(T);idx={k:uk.index(aliases[k]) for k in keys}
    absolute={k:endpoint_record(lower[idx[k]],upper[idx[k]],F(0),H) for k in keys};contrasts={}
    def contrast(a,b,name):
        i,j=idx[a],idx[b]
        if i==j:rec=dict(identity=True,interval=[0.,0.],interval_exact=['0','0'],sign='zero')
        else:
            v=c.I(lower[i],upper[i])-c.I(lower[j],upper[j]);rec=endpoint_record(v.lo,v.hi,-H,H)
        contrasts[name]=dict(left=a,right=b,**rec)
    for k in keys:
        if k!='zero':contrast('zero',k,'zero-minus-'+k)
        if k not in ('zero','common'):contrast(k,'common',k+'-minus-common')
    for kind,seed in itertools.product(('relu','quadratic'),c.SEEDS):contrast(f'{kind}-{seed}-pure',f'{kind}-{seed}-guarded',f'{kind}-{seed}-pure-minus-guarded')
    c.need(len(absolute)+len(contrasts)<=FAMILY//5,'Declared inference family exceeded')
    raw=folder/'path-endpoints.npz';h=write_arrays(raw,lower=lower,upper=upper)
    result=dict(d=d,m=m,T=T,n=sub,paths=PATHS,bin_bits=40,policy_keys=keys,unique_policy_keys=uk,policy_sha256=dict(zip(keys,ids)),aliases=aliases,absolute=absolute,contrasts=contrasts,raw_sha256=h,evaluation_seconds=clocks,stream_sha256=stream.hexdigest(),support_exact=str(H),family_budget='1/100 across all five tasks',family_maximum=FAMILY,log_upper=LOG,seconds_through_arrays=time.perf_counter()-start,scope='Original continuous laws enclosed by 40-bit bins and outward full-path propagation. Common paths and repeated policy identities are not independent policy comparisons.')
    c.save(folder/'costs.json',result);result['seconds_through_record']=time.perf_counter()-start;c.save(folder/'clock.json',dict(seconds_through_record=result['seconds_through_record'],costs_sha256=c.digest(folder/'costs.json')))
    return result

def checkpoint(message):
    if os.environ.get('NBO_PUSH_CHECKPOINTS')!='1':return
    repo=R.parents[1];rel=str(R.relative_to(repo))
    subprocess.run(['git','add','-f',rel+'/results62',rel+'/audit'],cwd=repo,check=True,stdout=subprocess.DEVNULL)
    if subprocess.run(['git','diff','--cached','--quiet'],cwd=repo).returncode:
        subprocess.run(['git','commit','-m',message],cwd=repo,check=True,stdout=subprocess.DEVNULL)
        subprocess.run(['git','push','--atomic','origin','HEAD:refs/heads/revision/econometrica-nbo-r62-referee-revision-2026-10-10','HEAD:refs/heads/revision/econometrica-nbo-r62-science-2026-10-10'],cwd=repo,check=True)

def run():
    fz=verify();out=R/'results62';c.need(not out.exists(),'Production outputs already exist; do not overwrite or retime them')
    out.mkdir();begin=time.perf_counter()
    affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else []
    if affinity:os.sched_setaffinity(0,{affinity[0]})
    env=dict(platform=platform.platform(),machine=platform.machine(),processor=platform.processor(),python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,affinity=sorted(os.sched_getaffinity(0)) if affinity else [],frequency_controlled=False,hardware_counters_available=False)
    compiler=c.compile_kernel();t=time.perf_counter();cmd=['g++','-O3','-std=c++17',str(R/'code/search60.cpp'),'-o',str(R/'build/native60')];subprocess.run(cmd,check=True,capture_output=True)
    compiler['retained_exact_backend']=dict(command=cmd,seconds=time.perf_counter()-t,source_sha256=c.digest(R/'code/search60.cpp'),binary_sha256=c.digest(R/'build/native60'))
    c.save(R/'audit/COMPILER62.json',compiler);summaries=[]
    for d,m,T,ladder,A,q in c.TASKS:
        name=c.key(d,m,T);folder=out/name;folder.mkdir();proposals={};construction={};record_files={}
        for kind,seed in itertools.product(('relu','quadratic'),c.SEEDS):
            prop,record=p.make(kind,d,m,T,seed);k=f'{kind}-{seed}';path=folder/'proposals'/(k+'.json');c.save(path,record)
            proposals[k]=prop;construction[k]=record['seconds'];record_files[k]=c.digest(path)
            print(json.dumps(dict(task=name,proposal=k,seconds=record['seconds'])),flush=True)
        refs=[];method_rows={k:[] for k in proposals};cumref=0.;cummethod={k:0. for k in proposals};final_policies={}
        for sub in ladder:
            t=time.perf_counter();ref,arr=c.reference(d,m,T,sub,A,q);dest=folder/f'n{sub}';dest.mkdir()
            ref['raw_sha256']=write_arrays(dest/'reference.npz',**arr);ref['seconds_through_arrays']=time.perf_counter()-t;cumref+=ref['seconds_through_arrays'];ref['cumulative_reference_seconds']=cumref
            cert,_=c.certificate(arr['policy'],arr['selected_upper'],arr['lower'],d,m,T,sub,A,q);ref['policy_certificate']=cert
            c.save(dest/'reference.json',ref);refs.append(ref);final_policies={'common':arr['policy']}
            for k,prop in proposals.items():
                t=time.perf_counter();r,pa=c.policy_from_proposal(ref,arr,prop);r['raw_sha256']=write_arrays(dest/(k+'.npz'),**pa);r['seconds_through_arrays']=time.perf_counter()-t;cummethod[k]+=r['seconds_through_arrays']
                r.update(n=sub,cumulative_own_verification_seconds=cummethod[k],shared_reference_seconds=cumref,primitive_construction_seconds=construction[k],conservative_prefix_seconds=cumref+construction[k]+cummethod[k])
                c.save(dest/(k+'.json'),r);method_rows[k].append(r)
                final_policies[k+'-pure']=pa['pure'];final_policies[k+'-guarded']=pa['guarded']
            print(json.dumps(dict(task=name,n=sub,common_gap=cert['maximum_date_gap_upper'],reference_seconds=cumref)),flush=True)
        last=ladder[-1];final_policies['zero']=np.zeros_like(final_policies['common'])
        for k,pol in final_policies.items():write_arrays(folder/'returned'/(k+'.npz'),policy=pol)
        costs=direct((d,m,T),final_policies,last,folder)
        def targets(rows,getcert):
            result=[]
            for tol in c.TOLS:
                hit=next((r for r in rows if F(getcert(r)['maximum_date_gap_upper'])<=tol),None)
                result.append(dict(tolerance=str(tol),status='attained' if hit else 'budget_exhausted',first_n=hit['n'] if hit else None,final_bound=getcert(rows[-1])['maximum_date_gap_upper']))
            return result
        frontiers={'common':targets(refs,lambda r:r['policy_certificate'])}
        for k,rows in method_rows.items():
            for variant in ('pure','guarded'):frontiers[k+'-'+variant]=targets(rows,lambda r,v=variant:r[v+'_certificate'])
        cold=compiler['seconds']+compiler['retained_exact_backend']['seconds'];release_work={'common':cumref+costs['seconds_through_record']+cold}
        for k in proposals:
            for variant in ('pure','guarded'):release_work[k+'-'+variant]=cumref+construction[k]+cummethod[k]+costs['seconds_through_record']+cold
        summary=dict(task=name,d=d,m=m,T=T,ladder=list(ladder),A=A,q=q,reference=refs,methods=method_rows,construction_seconds=construction,proposal_record_sha256=record_files,targets=frontiers,full_catalogue_release_work_seconds=release_work,shared_inference_seconds=costs['seconds_through_record'],costs_sha256=c.digest(folder/'costs.json'),source_freeze_sha256=fz,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Every rung executed. Prefix verification clocks and full catalogue release costs are separate. Both pure and common-augmented fitted actors are real returned policies. Global process RSS is not a per-method independent peak.')
        c.save(folder/'summary.json',summary);summaries.append(summary)
        c.save(R/'audit/PROGRESS62.json',dict(completed_tasks=[s['task'] for s in summaries],source_freeze_sha256=fz))
        checkpoint('R62: retain frozen '+name+' complete policies, original-optimum frontier and continuous-law costs')
    result=dict(status='executed',source_freeze_sha256=fz,environment=env,tasks=[s['task'] for s in summaries],primitive_fitted_services=5*2*len(c.SEEDS),independent_path_rows_under_declared_model=5*PATHS,finite_fitting_seeds=list(c.SEEDS),elapsed_science_seconds=time.perf_counter()-begin,compiler_receipt_sha256=c.digest(R/'audit/COMPILER62.json'),scope='Fresh R62 prospective execution; no alteration of earlier results; finite seed catalogue is not a task-population or optimizer-success probability estimate.')
    c.save(R/'audit/EXECUTION62.json',result);checkpoint('R62: bind completed prospective science catalogue')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--freeze',action='store_true');z=a.parse_args()
    print(freeze()) if z.freeze else run()
