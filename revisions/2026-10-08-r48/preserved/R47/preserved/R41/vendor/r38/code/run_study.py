"""Frozen R38 execution plan. A fresh result directory is mandatory.

Every replicate is a fresh process. The parent records startup-inclusive work;
scientific records separately report the complete service-through-fsync clock.
No CPU affinity/frequency control is claimed. Process high-water RSS is not
algorithm-exclusive memory. No old R37 scientific record is replaced.
"""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess,random,platform,datetime,resource
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
ROOT=Path(__file__).resolve().parent.parent
CODE=ROOT/'code'
REPS=3
METHODS=['fixed64-uncached','fixed64-cached','adaptive-uncached','adaptive-cached','tuned-cached','structural']


def cases():
    out=[]
    for eps in [1e-2,1e-4,1e-6,1e-8,1e-10]:
        out.append(dict(name='accuracy-'+str(eps),economy=dict(d=2,T=4,condition=4.),epsilon=eps))
    for d,T,c in [(8,4,8.),(16,8,16.),(32,4,16.),(4,12,4.)]:
        out.append(dict(name=f'scale-{d}-{T}-{c}',economy=dict(d=d,T=T,condition=c),epsilon=1e-6))
    for value in [1.005,.25,4.]:
        for warm in [False,True]:
            out.append(dict(name=f'target-{value}-'+('warm' if warm else 'cold'),economy=dict(d=2,T=4,condition=4.,valuation=value),epsilon=1e-6,warm=warm))
    out.append(dict(name='moment-margin',economy=dict(d=4,T=4,condition=4.,sigma=.025,theta=.5),epsilon=1e-6))
    return out


def specs():
    out=[]
    for c in cases():
        for met in METHODS:
            for rep in range(REPS):out.append(dict(kind='policy',replicate=rep,method=met,**c))
    for price,theta in [(1.,0.),(1.,1.),(4.,0.),(4.,1.)]:
        for rep in range(REPS):
            out.append(dict(kind='nonlinear',name=f'capital-{price}-{theta}',replicate=rep,N=256,A=128,T=4,price=price,theta=theta))
            out.append(dict(kind='neural',name=f'neural-{price}-{theta}',replicate=rep,N=256,A=128,T=4,price=price,theta=theta,width=31,steps=300))
    for rep in range(REPS):out.append(dict(kind='frontier',name='nonlinear-frontier',replicate=rep,N_schedule=[64,128,256,512],tolerances=[1.,.5,.25,.125],T=4,theta=1.,price=1.))
    return out


def default(x):
    import numpy as np
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)


def child(spec,out):
    begin=time.perf_counter()
    if spec['kind']=='policy':
        from policy_study import service
        r=service(spec)
    elif spec['kind'] in ('nonlinear','neural'):
        from nonlinear import construct,own_value,action
        import numpy as np
        parameters={k:spec[k] for k in ('N','A','T','theta','price')}
        if spec['kind']=='neural':
            from nonlinear_neural import neural_service
            r=neural_service(**parameters,width=spec['width'],steps=spec['steps'])
            candidate=r['candidate']
        else:
            candidate=construct(**parameters);r=dict(candidate=candidate)
        states=np.array([.125,.25,.5,.75]);v=own_value(candidate,states)
        r['own_policy_values']=dict(states=states,lower=v.lo,upper=v.hi)
        r['initial_actions']=action(candidate,0,states)
        if spec['price']==4.:
            old=construct(spec['N'],spec['A'],spec['T'],spec['theta'],1.)
            oldv=own_value(old,states,price=4.,theta=spec['theta'])
            gain=oldv-v
            r['counterfactual']=dict(old_rule_at_new_price_lower=oldv.lo,old_rule_at_new_price_upper=oldv.hi,
                 improvement_lower=gain.lo,improvement_upper=gain.hi,old_actions=action(old,0,states),
                 baseline_construction_seconds=old['construction_seconds'])
        r['spec']=spec
    elif spec['kind']=='frontier':
        from nonlinear import construct
        rows=[];passed={};cumulative=0.
        for n in spec['N_schedule']:
            candidate=construct(n,n//2,spec['T'],spec['theta'],spec['price'])
            cumulative+=candidate['construction_seconds'];gap=candidate['policy_gap_upper']
            rows.append(dict(N=n,A=n//2,bound=gap,seconds=candidate['construction_seconds'],cumulative_seconds=cumulative))
            for eps in spec['tolerances']:
                if str(eps) not in passed and gap<=eps:passed[str(eps)]=dict(N=n,gap=gap,slack=gap/eps,cumulative_seconds=cumulative)
        r=dict(spec=spec,all_checks=rows,first_pass=passed)
    else:raise ValueError('Unknown service kind')
    r['process_peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    payload=json.dumps(r,default=default,separators=(',',':'),sort_keys=True)+'\n'
    with out.open('w') as f:f.write(payload);f.flush();os.fsync(f.fileno())
    clock=dict(service_through_fsync_seconds=time.perf_counter()-begin,record_sha256=hashlib.sha256(payload.encode()).hexdigest())
    out.with_suffix('.clock.json').write_text(json.dumps(clock,sort_keys=True)+'\n')


def protocol():
    return dict(review_commit='71949aa40c62c960dab824137bed12bb3516ff85',reviewed_revision='9792d3dee69351f672dcc09098422b35207060a7',
        replicates=REPS,methods=METHODS,specifications=specs(),order='Source-fixed shuffle with seed 3807; isolated child per row',
        timing='Complete construction, failed checks, failed precision and fixed-grid tuning trials, verification and fsync. Parent startup clock separately. Warm setup separately and jointly reported.',
        warmups='One fresh-process LQ warmup, not included in contrasts; warmup recorded separately.',
        threads=1,cpu_affinity_control=False,cpu_frequency_control=False,
        fixed_precision_search='Minimum successful native type in ordered set {binary32,binary64}; not minimum arbitrary fractional precision',
        inference='Deterministic economy-method objects with repeated clocks; no population inference, asymptotic scaling claim or universal neural superiority',
        neural='All hidden affine weights trained; reference Bellman data generation charged; no SGD convergence assumed; independent interval actor certificate',
        source_change_rule='Changing any source after freezing requires a distinct execution directory and provenance record')


def run(destination):
    destination=Path(destination)
    if destination.exists():raise FileExistsError('Fresh result directory required: '+str(destination))
    destination.mkdir(parents=True);(destination/'raw').mkdir();(destination/'specs').mkdir()
    p=protocol();(destination/'PROTOCOL.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
    files={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(CODE.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
    freeze=dict(files=files,protocol_sha256=hashlib.sha256((destination/'PROTOCOL.json').read_bytes()).hexdigest(),
        source_commit=os.environ.get('GITHUB_SHA'),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        python=sys.version,platform=platform.platform(),numpy=__import__('numpy').__version__,
        torch=__import__('importlib.metadata',fromlist=['version']).version('torch'))
    (destination/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
    from test_revision import run as tests
    (destination/'TESTS.json').write_text(json.dumps(tests(),indent=2)+'\n')
    jobs=specs();random.Random(3807).shuffle(jobs)
    warm=dict(kind='policy',economy=dict(d=2,T=4,condition=4.),epsilon=1e-4,method='adaptive-cached')
    jobs=[warm]+jobs;index=[]
    for i,spec in enumerate(jobs):
        name='warmup' if i==0 else f'service-{i:04d}'
        inp=destination/'specs'/(name+'.json');out=destination/'raw'/(name+'.json')
        inp.write_text(json.dumps(spec,sort_keys=True)+'\n');start=time.perf_counter()
        cp=subprocess.run([sys.executable,str(__file__),'child',str(inp),str(out)],capture_output=True,text=True)
        parent_seconds=time.perf_counter()-start
        entry=dict(id=name,specification=spec,returncode=cp.returncode,parent_seconds=parent_seconds,
            stderr=cp.stderr,stdout=cp.stdout)
        if cp.returncode==0:entry['clock']=json.loads(out.with_suffix('.clock.json').read_text())
        index.append(entry);(destination/'EXECUTIONS.json').write_text(json.dumps(index,indent=2,sort_keys=True)+'\n')
        print(name,spec.get('name',spec['kind']),spec.get('method',''),cp.returncode,round(parent_seconds,3),flush=True)
    for f,h in files.items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
    (destination/'COMPLETED.json').write_text(json.dumps(dict(executions=len(index)-1,process_failures=sum(x['returncode']!=0 for x in index),source_unchanged=True,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='child':child(json.loads(Path(sys.argv[2]).read_text()),sys.argv[3])
    elif len(sys.argv)>1 and sys.argv[1]=='protocol':print(json.dumps(protocol(),indent=2,sort_keys=True))
    elif len(sys.argv)==2:run(sys.argv[1])
    else:raise SystemExit('Usage: run_study.py NEW_DIRECTORY | child SPEC OUTPUT | protocol')
