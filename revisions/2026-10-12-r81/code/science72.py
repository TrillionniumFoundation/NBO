"""Predeclared R72 query-reuse and conditional-integration catalogue.

Measurements are complete processes on deterministic localized workloads,
not IID economic observations. All original-law recursive misses are paid.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,resource,subprocess,sys,time,traceback
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1]
B=F(15,16)
TASKS=[dict(name='scalar-d2-T2',d=2,m=1,T=2,tol='1/256',blocks=32,repetitions=3,invalid=16,far=True),
       dict(name='scalar-d8-T3',d=8,m=1,T=3,tol='1/128',blocks=16,repetitions=3,invalid=8,far=True),
       dict(name='vector-d2-T2',d=2,m=2,T=2,tol='1/32',blocks=24,repetitions=3,invalid=12,far=True),
       dict(name='vector-d2-T3',d=2,m=2,T=3,tol='1/32',blocks=8,repetitions=2,invalid=4,far=True),
       dict(name='vector-d2-T4',d=2,m=2,T=4,tol=str(F(1,8)/sum((B**t for t in range(4)),F(0))),blocks=4,repetitions=1,invalid=None,far=False)]
MODES=('none','exact','geometric');TIMEOUT=900


def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w') as f:f.write(json.dumps(x,indent=2,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def hardware():
    cpus=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else []
    frequency={}
    for key in ('scaling_cur_freq','scaling_min_freq','scaling_max_freq','scaling_governor'):
        p=Path('/sys/devices/system/cpu/cpu'+str(cpus[0] if cpus else 0)+'/cpufreq')/key
        frequency[key]=p.read_text().strip() if p.exists() else None
    return dict(platform=platform.platform(),python=sys.version,affinity=cpus,frequency=frequency,frequency_locked=False)

def source_paths():
    p=[R/'code'/f for f in ('certificates72.py','cache72.py','science72.py','independent72.py','tests72.py')]
    # Bind every Python dependency in the inherited code roots, not a mutable
    # reference to the current default branch.
    for n in (62,63,64,65,66,67):p+=sorted((R.parent/f'2026-10-10-r{n}'/'code').glob('*.py'))
    p+=sorted((R.parent/'2026-10-11-r69/code').glob('*.py'))
    return p

def freeze():
    p=R/'SOURCE_FREEZE72.json'
    if p.exists():raise FileExistsError('Source freeze is immutable')
    data=dict(protocol='REVISION_PROTOCOL72.md',tasks=TASKS,modes=MODES,timeout_seconds=TIMEOUT,
              cache_capacity=128,coordinate_jitter_exact='1/1048576',source_files={str(x.relative_to(R.parent)):digest(x) for x in source_paths()},
              scope='Localized, deterministic root-query workloads with original recursive descendants, not independent policy-cost rows or trained representation comparisons',
              expected_processes=sum(t['repetitions']*len(MODES) for t in TASKS),
              baseline_commit='b576584cb5b1ff5ceccbcf37a3fa6e1ac613aca6')
    save(p,data);return data

def verify():
    data=json.loads((R/'SOURCE_FREEZE72.json').read_text())
    if data['tasks']!=TASKS or data['modes']!=list(MODES):raise AssertionError('Protocol changed')
    for name,h in data['source_files'].items():
        if digest(R.parent/name)!=h:raise AssertionError('Scientific source changed: '+name)
    return data

def state(task,j):
    row=[.4,.6]*(task['d']//2)
    if task['far'] and j==task['blocks']-2:return [.75]*task['d']
    if j>0 and j%2==0:row[j%task['d']]+=(-1 if j%4==0 else 1)*2**-20
    return row

def service(index,mode,rep):
    verify();task=TASKS[index];folder=R/'results72'/f"{task['name']}-{mode}-r{rep}";folder.mkdir(parents=True,exist_ok=True)
    hw=hardware()
    from cache72 import Cache
    import numpy as np
    cache=Cache(task['m'],mode,128);blocks=[];begin=time.perf_counter()
    for j in range(task['blocks']):
        step=time.perf_counter();before=cache.oracle.counts.get('q_queries',0)
        if task['invalid']==j:cache.invalidate('original-v2')
        result=cache.solve(state(task,j),task['T'],F(task['tol']))
        # Store and reload every paid cache. Hash comparison detects accidental
        # file mutation; provenance still rests on the accepted fill transcript.
        file=folder/'cache.json';save(file,cache.payload());expected=digest(file)
        payload=json.loads(file.read_text())
        if digest(file)!=expected:raise AssertionError('Serialized cache mutation')
        cache.load(payload,cache.epoch)
        block=dict(index=j,seconds=time.perf_counter()-step,prefix_seconds=time.perf_counter()-begin,
                   additional_q_queries=cache.oracle.counts.get('q_queries',0)-before,kind=cache.trace[-1]['kind'],
                   gap=result['gap'],action=result['action'],cache_sha256=expected)
        save(folder/f'block-{j:03d}.json',block);blocks.append(block)
    save(folder/'trace.json',cache.trace)
    save(folder/'summary.json',dict(status='returned',task=task,mode=mode,repetition=rep,cache_counts=cache.counts,
        recursive_counts=cache.oracle.counts,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        hardware_start=hw,hardware_end=hardware(),blocks=blocks,trace_sha256=digest(folder/'trace.json'),
        service_body_seconds=time.perf_counter()-begin,source_freeze_sha256=digest(R/'SOURCE_FREEZE72.json'),
        new_statistical_policy_cost_rows=0,
        scope='Cache acts only at workload roots; a miss executes the unchanged full recursive original-optimum verifier.'))


def run_task(index):
    verify();task=TASKS[index];receipts=[]
    for rep in range(task['repetitions']):
        # Fixed balanced cyclic order; no result-dependent ordering.
        modes=MODES[rep%3:]+MODES[:rep%3]
        for mode in modes:
            folder=R/'results72'/f"{task['name']}-{mode}-r{rep}";folder.mkdir(parents=True,exist_ok=True)
            start=time.perf_counter();error=None
            with (folder/'process.log').open('w') as output:
                try:
                    done=subprocess.run([sys.executable,__file__,'--service',str(index),'--mode',mode,'--rep',str(rep)],stdout=output,stderr=subprocess.STDOUT,timeout=TIMEOUT)
                    code=done.returncode
                except subprocess.TimeoutExpired:code=None;error='predeclared 900-second timeout'
            elapsed=time.perf_counter()-start
            receipt=dict(task=task['name'],mode=mode,repetition=rep,returncode=code,error=error,
                         complete_process_seconds=elapsed,source_freeze_sha256=digest(R/'SOURCE_FREEZE72.json'),
                         files_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file() and p.name!='receipt.json'})
            save(folder/'receipt.json',receipt);receipts.append(receipt)
            print(json.dumps({k:receipt[k] for k in ('task','mode','repetition','returncode','complete_process_seconds')}),flush=True)
    save(R/'results72'/f"catalogue-{index}.json",receipts)


def integration():
    import random
    from certificates72 import relu_uniform_mean
    rng=random.Random(720072);rows=[];begin=time.perf_counter()
    for d,m in ((2,1),(8,1),(2,2),(8,2)):
        for case in range(64):
            x=[F(rng.randrange(0,2**12),2**12) for _ in range(d)];cap=F(1,8)+sum(x)/(8*d)
            a=[cap*F(case%5,8)] if m==1 else [cap*F(case%3,8),cap*F((case+1)%3,8)]
            y=[F(1,16)+x[j]/2+x[(j+1)%d]/8+x[j]*(1-x[(j+1)%d])/16+(F(1,2) if j%2==0 else F(1,4))*a[0]+((F(1,4) if j%2==0 else F(1,2))*a[1] if m==2 else 0) for j in range(d)]
            for neuron in range(16):
                w=[F(rng.randrange(-8,9),8) for _ in range(d)];bias=F(rng.randrange(-16,17),8)
                center=bias+sum(w[j]*y[j] for j in range(d))
                radii=[sum(w[j]*(1 if j%2==0 else -1) for j in range(d))/32]
                if m==2:radii.append(sum(w)/64)
                value=relu_uniform_mean(center,radii)
                rows.append(dict(d=d,m=m,case=case,neuron=neuron,state=list(map(str,x)),action=list(map(str,a)),weights=list(map(str,w)),bias=str(bias),center=str(center),radii=list(map(str,radii)),mean_exact=str(value)))
    save(R/'results72/conditional-integrals.json',rows)
    save(R/'results72/conditional-summary.json',dict(status='returned',neurons=len(rows),contexts=256,hidden_units_per_context=16,
        seconds=time.perf_counter()-begin,new_statistical_policy_cost_rows=0,source_freeze_sha256=digest(R/'SOURCE_FREEZE72.json'),
        data_sha256=digest(R/'results72/conditional-integrals.json'),scope='Frozen rational feature diagnostics in the original economic transition; not fitted-critic performance or expected policy ranking.'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--task',type=int);p.add_argument('--service',type=int);p.add_argument('--mode');p.add_argument('--rep',type=int,default=0);p.add_argument('--integration',action='store_true');args=p.parse_args()
    if args.freeze:print(json.dumps(freeze(),indent=2))
    elif args.task is not None:run_task(args.task)
    elif args.service is not None:service(args.service,args.mode,args.rep)
    elif args.integration:verify();integration()
