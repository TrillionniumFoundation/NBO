"""Prospective nine-controller factorial under the original continuous law.

One frozen family covers 90 costs/pairs and four basis-by-modulus interactions.
Both independent whole-bin implementations are unchanged from R77. No fitting
or outcome-dependent extension is permitted after this source freeze.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse,hashlib,itertools,json,resource,time
import numpy as np
import cost77 as kernel
from study80 import encode,save,sha
R=Path(__file__).resolve().parents[1]
N=524288;BITS=40;SEED=20261012080;LOG=11;H=kernel.H;S=kernel.S;MARGIN=F(1,256)
NAMES=('zero',)+tuple(f'{rule}-{kind}-n{n}' for rule in ('legacy','calibrated') for n in (8,16) for kind in ('relu','bernstein'))

def configure():
    kernel.R=R;kernel.BITS=BITS;kernel.LOG=LOG

def controllers():
    actions={'zero':np.zeros((2,1,1),dtype=np.int64)};meta={}
    for name in NAMES[1:]:
        rule,kind,nn=name.split('-');n=int(nn[1:])
        folder=R/('results73' if rule=='legacy' else 'results80/construction')/f'{kind}-n{n}'
        record=json.loads((folder/'service.json').read_text());clock=json.loads((folder/'clock.json').read_text())
        if sha(folder/'service.json')!=clock['service_sha256']:raise AssertionError('Construction identity')
        a=np.asarray([[int(F(x)*4096) for x in stage['data']['actions']] for stage in record['stages']],dtype=np.int64).reshape(2,n,n)
        for t,i,j in itertools.product(range(2),range(n),range(n)):
            cap=int((F(1,8)+F(i+j,16*n))*4096)
            if not 0<=a[t,i,j]<=cap:raise AssertionError('Whole-cell feasibility')
        actions[name]=a
        meta[name]=dict(service_sha256=sha(folder/'service.json'),actor_sha256=hashlib.sha256(a.tobytes()).hexdigest(),
            rule=rule,basis=kind,n=n,coefficient_count=9,all_optimization_gaps_pass=record['all_optimization_gaps_pass'],
            construction_seconds=clock['seconds_through_service_output'],construction_scope=record['accounting'])
    return actions,meta

def verify_freeze():
    freeze=json.loads((R/'SOURCE_FREEZE80.json').read_text())
    for name,h in freeze['files'].items():
        if sha(R/name)!=h:raise AssertionError('R80 source freeze mismatch '+name)
    return freeze

def contrast_interval(arrays,coeff,estimator):
    low=np.zeros(N,dtype=np.int64);high=low.copy();total=0
    for name,value in coeff.items():
        a=arrays[name];total+=abs(value)
        low+=value*a[2*estimator if value>0 else 2*estimator+1]
        high+=value*a[2*estimator+1 if value>0 else 2*estimator]
    if sum(coeff.values())!=0:raise AssertionError('Centered contrast required')
    radius=F(total,2)*H
    return kernel.interval(low,high,(-radius,radius))

def infer(arrays):
    configure();out={}
    for e,est in enumerate(('cash','conditional')):
        costs={name:kernel.interval(a[2*e],a[2*e+1],(F(0),H)) for name,a in arrays.items()}
        pairs={a+'-minus-'+b:contrast_interval(arrays,{a:1,b:-1},e) for a,b in itertools.combinations(NAMES,2)}
        interactions={}
        for n in (8,16):
            coeff={f'calibrated-bernstein-n{n}':1,f'calibrated-relu-n{n}':-1,f'legacy-bernstein-n{n}':-1,f'legacy-relu-n{n}':1}
            interactions[f'basis-by-modulus-n{n}']=dict(coefficients=coeff,**contrast_interval(arrays,coeff,e))
        out[est]=dict(costs=costs,contrasts=pairs,interactions=interactions)
    return out

def execute():
    configure();freeze=verify_freeze();folder=R/'results80/cost'
    if folder.exists():raise FileExistsError('Retain the existing scientific attempt')
    folder.mkdir(parents=True);begin=time.perf_counter();before=kernel.environment();actions,meta=controllers()
    paths=np.random.Generator(np.random.PCG64(SEED)).integers(0,1<<BITS,size=(N,4),dtype=np.uint64)
    np.savez_compressed(folder/'bins.npz',bins=paths);arrays={};work={}
    for name in NAMES:
        print('R80 original-law cost:',name,flush=True);start=time.perf_counter()
        arrays[name],work[name]=kernel.enclose(paths,actions[name]);np.savez_compressed(folder/(name+'.npz'),endpoints=arrays[name])
        work[name]['seconds_through_output']=time.perf_counter()-start;work[name]['endpoint_sha256']=sha(folder/(name+'.npz'))
    t=time.perf_counter();result=infer(arrays);inference_seconds=time.perf_counter()-t
    report=dict(status='passed',source_freeze_sha256=sha(R/'SOURCE_FREEZE80.json'),source_commit=freeze['source_commit'],
        rows=N,bin_bits=BITS,seed=SEED,policies=NAMES,estimands=94,log_upper=LOG,family_failure_upper='376*exp(-11) < 1/100',
        new_independent_simulation_rows=N,controller_metadata=meta,work=work,inference=result,
        statistical_inference_seconds=inference_seconds,bins_sha256=sha(folder/'bins.npz'),
        environment_before=before,environment_after=kernel.environment(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        seconds_before_summary=time.perf_counter()-begin,paired_width_target=MARGIN,
        scope='Fresh original-law rows for nine complete actors; four new calibrated constructions and four retained legacy actors. Shared paths are not independent replications across methods. No hidden-layer training, timing distribution, or universal neural ranking.')
    save(folder/'summary.json',report);save(folder/'clock.json',dict(seconds_through_summary=time.perf_counter()-begin,summary_sha256=sha(folder/'summary.json')))
    print(json.dumps(encode(dict(status='passed',rows=N,conditional_interactions=result['conditional']['interactions'],seconds=time.perf_counter()-begin)),indent=2),flush=True)

def replay():
    configure();verify_freeze();begin=time.perf_counter();folder=R/'results80/cost';report=json.loads((folder/'summary.json').read_text())
    if sha(folder/'summary.json')!=json.loads((folder/'clock.json').read_text())['summary_sha256']:raise AssertionError('Summary identity')
    paths=np.load(folder/'bins.npz')['bins'];expected=np.random.Generator(np.random.PCG64(SEED)).integers(0,1<<BITS,size=(N,4),dtype=np.uint64)
    if not np.array_equal(paths,expected) or sha(folder/'bins.npz')!=report['bins_sha256']:raise AssertionError('Prospective row identity')
    actions,meta=controllers();arrays={}
    if encode(meta)!=report['controller_metadata']:raise AssertionError('Actor identity')
    for name in NAMES:
        path=folder/(name+'.npz')
        if sha(path)!=report['work'][name]['endpoint_sha256']:raise AssertionError('Endpoint identity')
        saved=np.load(path)['endpoints'];fresh,work=kernel.enclose(paths,actions[name])
        if not np.array_equal(saved,fresh):raise AssertionError('Independent full-bin replay '+name)
        arrays[name]=saved
    if encode(infer(arrays))!=report['inference']:raise AssertionError('94-estimand exact replay')
    rec=dict(status='passed',full_bin_trajectories_per_implementation=N*len(NAMES),exact_midpoint_trajectories=512*len(NAMES),
        recomputed_estimands=94,new_simulation_rows=0,seconds=time.perf_counter()-begin,
        original_summary_sha256=sha(folder/'summary.json'),scientific_clocks_replaced=False)
    save(R/'audit/REPLAY80.json',rec);print(json.dumps(rec,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--execute',action='store_true');g.add_argument('--replay',action='store_true');a=p.parse_args();execute() if a.execute else replay()
