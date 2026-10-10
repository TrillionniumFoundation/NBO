"""Prospective complete-process R69 services and source-bound receipts."""
import time
ENTRY=time.perf_counter()
from pathlib import Path
import argparse,hashlib,json,os,platform,resource,subprocess,sys,traceback
import numpy as np
import readout69 as r
R=Path(__file__).resolve().parents[1];old=r.old
TASKS=((2,2,'1/128',32),(8,3,'1/64',8));SEEDS=(6901,6902);BLOCKS=64
ENV={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
SCIENCE_FILES=('readout69.py','center69.py','independent69.py','vector69.py','vector_base69.py','science69.py','tests69.py')

def specs():
    rows=[]
    for d,T,target,N in TASKS:
        for kind in r.KINDS:
            for seed in SEEDS if kind in r.LEARNED else (0,):
                for repeat in range(4):rows.append(dict(group='comparison',d=d,T=T,target=target,N=N,kind=kind,seed=seed,repeat=repeat))
        for kind in r.LEARNED:
            for seed in SEEDS:rows.append(dict(group='validation',d=d,T=T,target=target,N=256,kind=kind,seed=seed,repeat=0))
        for kind in ('adaptive','hat-relu','bernstein4','quadratic'):
            for seed in SEEDS if kind in r.LEARNED else (0,):
                for repeat in range(4):rows.append(dict(group='reuse',d=d,T=T,target=target,N=8,kind=kind,seed=seed,repeat=repeat))
        rows.append(dict(group='inference',d=d,T=T,target=target,N=1024,kind='paired',seed=6901,repeat=0))
    for d,T in ((2,2),(2,3),(8,2),(8,3)):
        for kind in ('simplicial','uniform','hat-vector','quadratic-vector'):
            for repeat in range(2):rows.append(dict(group='vector',d=d,T=T,target='1/4',N=8,kind=kind,seed=6901,repeat=repeat))
    for kind in ('simplicial','hat-vector'):rows.append(dict(group='vector',d=2,T=4,target='1/4',N=1,kind=kind,seed=6901,repeat=0))
    for i,s in enumerate(rows):s.update(index=i,key=f"{s['group']}-d{s['d']}-T{s['T']}-{s['kind']}-s{s['seed']}-r{s['repeat']}")
    if len(rows)!=188:raise AssertionError(('Catalogue size',len(rows)))
    return rows

def freeze():
    file=R/'audit/SOURCE_FREEZE69.json'
    if file.exists():return verify()
    dependencies={}
    for dirname in ('2026-10-10-r62','2026-10-10-r63','2026-10-10-r64','2026-10-10-r67'):
        for p in (R.parent/dirname/'code').glob('*.py'):dependencies[str(p.relative_to(R.parent))]=old.sha(p)
    old.save(file,dict(source_commit=os.getenv('GITHUB_SHA'),source_sha256={
        **{'code/'+name:old.sha(R/'code'/name) for name in SCIENCE_FILES},'PROTOCOL69.md':old.sha(R/'PROTOCOL69.md')},
        inherited_python_sha256=dependencies,catalogue=specs(),review_commit='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',
        reviewed_manuscript='eacd3e217ae1e2e9ea6e154b48da7d103159d051',
        source_scope='Ordinary prepared and tested scientific sources frozen before any complete service; historical R67 observations are unchanged'))
    return old.sha(file)

def verify():
    file=R/'audit/SOURCE_FREEZE69.json';j=old.read(file)
    for name,h in j['source_sha256'].items():
        if old.sha(R/name)!=h:raise AssertionError('Changed new source '+name)
    for name,h in j['inherited_python_sha256'].items():
        if old.sha(R.parent/name)!=h:raise AssertionError('Changed inherited source '+name)
    if j['catalogue']!=specs():raise AssertionError('Changed catalogue')
    return old.sha(file)

def machine():
    cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu})
    root=Path(f'/sys/devices/system/cpu/cpu{cpu}/cpufreq')
    data={}
    for name in ('scaling_cur_freq','scaling_governor','cpuinfo_min_freq','cpuinfo_max_freq'):
        p=root/name;data[name]=p.read_text().strip() if p.exists() else None
    return dict(cpu=cpu,frequency=data,frequency_locked_by_experiment=False,platform=platform.platform(),
                python=sys.version,numpy=np.__version__,threads=1)

def worker(s):
    binding=verify();out=R/'results69'/s['key']
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);hardware=machine();d,T,N=s['d'],s['T'],s['N'];kind=s['kind']
    try:
        if s['group']=='inference':
            import center69
            result=center69.study(d,T,s['target'],N,out)
        elif s['group']=='vector':
            import vector69
            models,fit,raw=vector69.fit(d,min(T,3),s['seed'],kind)
            if T==4 and models:
                models[4]=models[3];fit['horizon_four_transfer']='Three-date fitted weights used as an untrusted four-date proposal; no four-date training labels'
            old.save(out/'model.json',models);old.archive(out/'training.npz',**raw)
            oracle=vector69.Oracle(kind,models);randoms,initial=old.workload(d,T,N,693001+d*101+T,continuous=True,vector=True)
            arrays,account=old.paths(oracle,initial,randoms,T,s['target'],vector=True)
            old.archive(out/'trace.npz',**randoms,**arrays)
            result=dict(status='returned',training=fit,counts=oracle.counts.copy(),account=account)
        else:
            models,fit,raw=r.fit(d,T,s['target'],s['seed'],kind)
            old.save(out/'model.json',models);old.archive(out/'training.npz',**raw)
            if s['group']=='validation':
                validation,raw=r.validate(d,T,s['target'],kind,models,s['seed'],N)
                old.archive(out/'validation.npz',**raw);result=dict(status='returned',training=fit,validation=validation)
            elif s['group']=='comparison':
                oracle=r.Oracle(kind,models);randoms,initial=old.workload(d,T,N,694001+d*101+T,continuous=True)
                arrays,account=old.paths(oracle,initial,randoms,T,s['target'])
                old.archive(out/'trace.npz',**randoms,**arrays)
                result=dict(status='returned',training=fit,counts=oracle.counts.copy(),account=account)
            else:
                identity=dict(kind=kind,d=d,T=T,target=s['target'],bits=24,freeze=binding)
                old.save(out/'model.json',dict(identity=identity,models=models));modelsha=old.sha(out/'model.json')
                initial_seconds=time.perf_counter()-ENTRY;blocks=[]
                for block in range(BLOCKS):
                    begin=time.perf_counter();loaded=old.read(out/'model.json')
                    if block==16:loaded['identity']={**loaded['identity'],'bits':25}
                    valid=loaded['identity']==identity and old.sha(out/'model.json')==modelsha
                    chosen=kind if valid else 'adaptive';used_models=loaded['models'] if valid else {}
                    load_seconds=time.perf_counter()-begin;oracle=r.Oracle(chosen,used_models)
                    randoms,initial=old.workload(d,T,N,695001+d*1009+T*101+block,continuous=True)
                    arrays,account=old.paths(oracle,initial,randoms,T,s['target'])
                    old.archive(out/f'block{block:02d}.npz',**randoms,**arrays)
                    rec=dict(block=block,identity_valid=valid,used_kind=chosen,load_seconds=load_seconds,
                        counts=oracle.counts.copy(),account=account,trace_sha256=old.sha(out/f'block{block:02d}.npz'))
                    old.save(out/f'block{block:02d}.json',rec)
                    blocks.append(dict(**rec,seconds_through_durable_record=time.perf_counter()-begin,
                        cumulative_from_entry=time.perf_counter()-ENTRY))
                result=dict(status='returned',training=fit,initial_seconds=initial_seconds,blocks=blocks)
        result.update(spec=s,source_freeze_sha256=binding,hardware_start=hardware,hardware_end=machine(),
            peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            seconds_from_entry=time.perf_counter()-ENTRY,
            files_sha256={str(p.relative_to(out)):old.sha(p) for p in out.rglob('*') if p.is_file()})
        old.save(out/'summary.json',result)
    except Exception as error:
        old.save(out/'summary.json',dict(status='failed',spec=s,source_freeze_sha256=binding,
            exception=repr(error),traceback=traceback.format_exc(),seconds_from_entry=time.perf_counter()-ENTRY))
        raise

def group(name):
    verify();specifications=specs();chosen=[s for s in specifications if s['group']==name or (name=='scalar' and s['group'] in ('comparison','reuse','validation'))]
    if not chosen:raise ValueError('Empty group '+name)
    (R/'logs69').mkdir(exist_ok=True);(R/'receipts69').mkdir(exist_ok=True)
    start=time.perf_counter();returned=0
    for s in chosen:
        log=R/'logs69'/(s['key']+'.log');begin=time.perf_counter();status='completed';exit_code=None
        with log.open('w') as f:
            try:
                proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--service',str(s['index'])],env=ENV,stdout=f,stderr=subprocess.STDOUT,timeout=1200 if s['T']==4 else 900)
                exit_code=proc.returncode;status='completed' if not exit_code else 'failed'
            except subprocess.TimeoutExpired:status='timeout'
            f.flush();os.fsync(f.fileno())
        elapsed=time.perf_counter()-begin;summary=R/'results69'/s['key']/'summary.json'
        good=status=='completed' and summary.exists() and old.read(summary)['status']=='returned';returned+=int(good)
        old.save(R/'receipts69'/(s['key']+'.json'),dict(spec=s,status=status,exit_code=exit_code,
            returned=good,complete_process_seconds=elapsed,summary_sha256=old.sha(summary) if summary.exists() else None,
            log_sha256=old.sha(log),workflow_run_id=os.getenv('GITHUB_RUN_ID'),source_freeze_sha256=verify(),
            clock_boundary='Before child launch through child exit and flushed log; parent receipt bookkeeping belongs to cohort total'))
        print(json.dumps(dict(key=s['key'],status=status,returned=good,seconds=elapsed)),flush=True)
    old.save(R/'receipts69'/('GROUP-'+name+'.json'),dict(group=name,planned=len(chosen),returned=returned,
        seconds_including_parent_bookkeeping=time.perf_counter()-start))

def main():
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--group');p.add_argument('--service',type=int);args=p.parse_args()
    if args.freeze:print(freeze())
    elif args.group:group(args.group)
    elif args.service is not None:worker(specs()[args.service])
    else:print(json.dumps(specs(),indent=2))
if __name__=='__main__':main()
