"""Prespecified implementation ablation, adverse regimes and two-control tasks."""
from fractions import Fraction as F
from pathlib import Path
from itertools import product
import hashlib,json,os,platform,random,resource,shutil,subprocess,time
import numpy as np
import search60 as s
import multi60 as m
R=s.R
SEEDS=(60103,60209,60317)
WIDTHS=(8,32)
SIZES=(33,129,513)
REGIMES=('mixed','crossing','cancellation','near-tie','flat')

def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def fixture(seed,width,size,regime):
    rng=random.Random(seed+1009*width+31*size);Q=4*(size-1);q1=F(-1,3);q2=F(1);q4=F(4);features=[]
    count=width//2 if regime in ('cancellation','near-tie','flat') else width
    for k in range(count):
        slope=F(rng.choice((-4,-3,-2,-1,1,2,3,4)),2);radius=F(1,128)
        center=F(rng.randrange(1,16),64);z=-slope*center
        if regime=='mixed' and k%2==0:z=F((-1)**k,2)
        w=F(rng.choice((-7,-5,-3,-1,1,3,5,7)),16)
        if regime=='cancellation':w*=2**16
        features.append((w,z,slope,radius))
        if regime in ('cancellation','near-tie','flat'):features.append((-w,z,slope,radius))
    if regime=='near-tie':
        a=F(size//2-1,Q);b=F(size//2,Q);q1=-q2*(a+b)-q4*(a**3+a*a*b+a*b*b+b**3)
    if regime=='flat':q1=q2=q4=F(0)
    return s.Objective(q1,q2,q4,features,[]),size-1,Q

def reference(o,cap,Q):
    start=time.perf_counter();values=[o.value(F(k,Q)) for k in range(cap+1)];best=min(range(cap+1),key=lambda k:(values[k],k))
    return dict(index=best,objective_exact=str(values[best]),all_minimizers=[k for k,v in enumerate(values) if v==values[best]],seconds=time.perf_counter()-start,max_recorded_operand_bits=max(max(x.numerator.bit_length(),x.denominator.bit_length()) for x in values))
def same(record,ref):
    if record['index']!=ref['index'] or F(record['objective_exact'])!=F(ref['objective_exact']):raise AssertionError(dict(actual=record,reference=ref))

def environment():
    pin=s.sc.a.n.s.cpu_pin if hasattr(s.sc.a.n.s,'cpu_pin') else None
    try:
        core=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{core})
    except (AttributeError,OSError):core=None
    text=Path('/proc/cpuinfo').read_text() if Path('/proc/cpuinfo').exists() else ''
    model=next((v.split(':',1)[1].strip() for v in text.splitlines() if v.startswith('model name')),None)
    governor=Path(f'/sys/devices/system/cpu/cpu{core}/cpufreq/scaling_governor')
    perf={'available':bool(shutil.which('perf')),'counter_values':None}
    if perf['available']:
        p=subprocess.run(['perf','stat','-e','cycles,instructions','true'],capture_output=True,text=True)
        perf.update(returncode=p.returncode,diagnostic=p.stderr[-2000:])
    return dict(hostname=platform.node(),system=platform.platform(),processor=model,python=platform.python_version(),numpy=np.__version__,affinity=core,frequency_controlled=False,governor=governor.read_text().strip() if governor.exists() else None,performance_counters=perf)

def run(worker):
    root=R/'results60'/f'worker{worker}'/'stress';root.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter();env=environment();rows=[];rng=random.Random(60991+worker)
    for seed,width,size,regime in product(SEEDS,WIDTHS,SIZES,REGIMES):
        name=f's{seed}-m{width}-N{size}-{regime}';o,cap,Q=fixture(seed,width,size,regime);ref=reference(o,cap,Q);order=list(s.METHODS);rng.shuffle(order);runs=[]
        for method in order:
            record=s.solve(o,cap,Q,method);same(record,ref);runs.append(record)
        coarse=[]
        for bits in (8,24):
            r=s.solve(o,cap,Q,'adaptive',bits=bits);same(r,ref);coarse.append(r)
        row=dict(key=name,seed=seed,width=width,size=size,regime=regime,objective=o.payload(),objective_sha256=canonical(o.payload()),cap=cap,Q=Q,reference=ref,order=order,runs=runs,coarse_endpoint_diagnostics=coarse)
        save(root/'cases'/(name+'.json'),row);rows.append({k:row[k] for k in ('key','seed','width','size','regime','objective_sha256','order','runs','coarse_endpoint_diagnostics')})
    repeated=[]
    # Selection fixed in source, not selected for observed favorable timings.
    for regime in REGIMES:
        o,cap,Q=fixture(SEEDS[0],32,129,regime);ref=reference(o,cap,Q)
        for rep in range(7):
            order=list(s.METHODS);rng.shuffle(order);runs=[]
            for method in order:
                r=s.solve(o,cap,Q,method);same(r,ref);runs.append(r)
            repeated.append(dict(regime=regime,rep=rep,order=order,runs=runs,objective_sha256=canonical(o.payload())))
    fallback=[]
    for size,regime in product((2050,4097),('mixed','cancellation','near-tie','flat')):
        o,cap,Q=fixture(SEEDS[0],8,size,regime);ref=reference(o,cap,Q);runs=[]
        for method in ('native-piecewise','screen-reduced','adaptive'):
            r=s.solve(o,cap,Q,method);same(r,ref);runs.append(r)
        fallback.append(dict(size=size,regime=regime,objective=o.payload(),cap=cap,Q=Q,reference=ref,runs=runs))
    result=dict(status='passed',worker=worker,environment=env,cases=len(rows),factorial=rows,repetitions=repeated,fallback_frontier=fallback,source='STUDY_PROTOCOL60.md',seconds_through_cases=time.perf_counter()-start,scope='Rational objective diagnostics; not training draws or economic policy-cost observations. The precision intervention coarsens certified endpoints after exact rational box bounds; it does not change binary64 internal arithmetic.')
    save(root/'summary.json',result);print(json.dumps(dict(stress_cases=len(rows),worker=worker,seconds=result['seconds_through_cases'])),flush=True)
    return result

def multi(worker):
    root=R/'results60'/f'worker{worker}'/'two-control';root.mkdir(parents=True,exist_ok=False);rows=[];start=time.perf_counter()
    for seed in SEEDS[:2]:
        critics,training=s.n.train('relu',2,2,256,seed+70000)
        save(root/f'training-{seed}.json',dict(critics=[c.payload() for c in critics],training=training))
        for state,cap,two_shocks in product(((F(1,8),F(1,4)),(F(3,4),F(5,8))),(8,16),(False,True)):
            # Capacity is a safe constant 1/8 within the state-dependent economy.
            Q=8*cap;o=m.from_critic(state,critics[1],two_shocks);ref=m.exhaustive(o,cap,Q);got=m.adaptive(o,cap,Q)
            if got['index']!=ref['index'] or F(got['objective_exact'])!=F(ref['objective_exact']):raise AssertionError('Two-control witness mismatch')
            rows.append(dict(seed=seed,state=list(map(str,state)),cap=cap,Q=Q,shocks=2 if two_shocks else 1,objective=o.payload(),reference=ref,adaptive=got))
    out=dict(status='passed',worker=worker,cases=len(rows),rows=rows,seconds=time.perf_counter()-start,scope='Actual trained continuation at two constrained controls with shared capacity; action-search correctness/work only. The additional control and optional second shock are stated extensions; a2=0 with the second shock disabled recovers the original action-dependent objective.')
    save(root/'summary.json',out);print(json.dumps(dict(two_control_cases=len(rows),worker=worker,seconds=out['seconds'])),flush=True);return out

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--worker',type=int,required=True);p.add_argument('--multi',action='store_true');args=p.parse_args()
    if args.multi:multi(args.worker)
    else:run(args.worker)
