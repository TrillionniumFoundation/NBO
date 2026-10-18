"""Execute only the separately frozen R117 catalogue, including every cost."""
from __future__ import annotations
from pathlib import Path
import os,sys,json,time,subprocess,traceback,resource,hashlib
import numpy as np
import precision117 as p
from precision117 import base,rep,kern,q,c,COUNTS
ROOT=Path(__file__).resolve().parents[1]
SERVICES=('compiled','geometric');PROTOCOL='e65a0180896406610922e48f65bcf7f55ada366f'
os.environ.setdefault('NBO_PROTOCOL108','29180a4ce4a6db7298e7458ecdfff3da08abb08f')


def source():
    f=ROOT/'SOURCE_FREEZE117.json'
    frozen=json.loads(f.read_text())
    for path,h in frozen['files'].items():
        if base.digest(ROOT/path)!=h:raise RuntimeError('Different frozen source: '+path)
    commit=os.environ.get('NBO_SOURCE117','')
    if len(commit)!=40 or any(x not in '0123456789abcdef' for x in commit):
        raise RuntimeError('NBO_SOURCE117 must identify the remotely committed executable freeze')
    return dict(protocol_commit=PROTOCOL,executable_commit=commit,
        manifest_sha256=base.digest(f),inherited_source=base.source())


def execute(x,alpha,model,service):
    if service=='compiled':return base.complete_service(x,alpha,model,compiled=True,safe=False)
    if service=='geometric':return p.service(x,alpha,model)
    raise ValueError(service)


def catalogue(out):
    x=rep.grid(12);entries=[]
    for i,alpha in enumerate(base.LEVELS):
        models=base.load_models(out,i)
        for arm in rep.ARMS:
            for service in SERVICES:
                data=execute(x,alpha,models[arm],service)
                data.update(index=i,alpha=alpha,arm=arm,service=service,
                    model_sha256=base.digest(out/'models'/f'{i}-{arm}'/'model.json'))
                path=out/'catalogue'/f'{i}-{arm}-{service}.json';base.dump(path,data)
                entries.append(dict(path=str(path.relative_to(out)),sha256=base.digest(path),decisions=len(x)))
                base.dump(out/'PROGRESS.json',dict(status='running',entries=entries))
                print('CATALOGUE',i,arm,service,round(data['seconds'],4),flush=True)
    base.dump(out/'CATALOGUE.json',dict(status='executed',source=source(),entries=entries,
        decisions=sum(v['decisions'] for v in entries)))


def reference(out):
    """Paid same-policy contrasts, with new 4096-bin bounds for changed actions."""
    records=[]
    for i,alpha in enumerate(base.LEVELS):
        for arm in rep.ARMS:
            control=json.loads((out/'catalogue'/f'{i}-{arm}-compiled.json').read_text())['rows']
            treatment=json.loads((out/'catalogue'/f'{i}-{arm}-geometric.json').read_text())['rows']
            ids=[j for j,(a,b) in enumerate(zip(control,treatment)) if a['action']!=b['action']]
            before=COUNTS.copy();t=time.perf_counter();rows=[]
            if ids:
                x=np.array([[control[j]['x0'],control[j]['x1']] for j in ids])
                aa=np.array([control[j]['action'] for j in ids]);bb=np.array([treatment[j]['action'] for j in ids])
                with kern.backend(True):
                    ra=q.certificate(x,aa,alpha,4096);rb=q.certificate(x,bb,alpha,4096)
                for k,j in enumerate(ids):
                    rows.append(dict(row=j,control_action=float(aa[k]),treatment_action=float(bb[k]),
                        control={v:float(ra[v][k]) for v in base.KEYS},
                        treatment={v:float(rb[v][k]) for v in base.KEYS}))
            records.append(dict(index=i,alpha=alpha,arm=arm,rows=rows,
                identical_actions=144-len(ids),seconds=time.perf_counter()-t,counts=base.counter_delta(before)))
            print('PAID REFERENCE',i,arm,len(ids),flush=True)
    base.dump(out/'REFERENCE117.json',dict(source=source(),records=records,
        identity_contrast_is_zero=True,benchmark_cost_not_free=True))


def timing_one(out,repeat):
    x=rep.grid(12)[:32];entries=[];t=time.perf_counter()
    for i,alpha in enumerate(base.LEVELS):
        models=base.load_models(out,i)
        for arm in rep.ARMS:
            for service in SERVICES:
                data=execute(x,alpha,models[arm],service)
                data.update(index=i,alpha=alpha,arm=arm,service=service)
                path=out/'timing'/f'{repeat}-{i}-{arm}-{service}.json';base.dump(path,data)
                entries.append(dict(index=i,arm=arm,service=service,path=str(path.relative_to(out)),
                    sha256=base.digest(path),seconds=data['seconds'],counts=data['counts']))
    base.dump(out/'timing'/f'PROCESS-{repeat}.json',dict(source=source(),repeat=repeat,
        entries=entries,inside_process_seconds=time.perf_counter()-t,machine=base.machine(),
        max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('all','timing-one'))
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--repeat',type=int,default=0)
    a=parser.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True);identity=source()
    if a.mode=='timing-one':return timing_one(out,a.repeat)
    if (out/'START.json').exists():raise FileExistsError('Use a distinct output identity; do not overwrite any attempted campaign')
    base.dump(out/'START.json',dict(source=identity,machine=base.machine(),started_unix=time.time()))
    t=time.perf_counter();processes=[]
    try:
        before=COUNTS.copy();ta=time.perf_counter();base.acquire(out)
        base.dump(out/'ACQUISITION117.json',dict(source=identity,seconds=time.perf_counter()-ta,
            counts=base.counter_delta(before),inherited_acquisition_unchanged=True,new_experiment='R117'))
        catalogue(out);reference(out)
        for repeat in range(7):
            command=[sys.executable,__file__,'timing-one','--output',str(out),'--repeat',str(repeat)]
            tp=time.perf_counter();proc=subprocess.run(command,capture_output=True,text=True)
            log=out/'timing'/f'PROCESS-{repeat}.log';log.parent.mkdir(parents=True,exist_ok=True)
            log.write_text(proc.stdout+proc.stderr)
            processes.append(dict(repeat=repeat,command=command,exit_code=proc.returncode,
                elapsed_seconds=time.perf_counter()-tp,log_sha256=base.digest(log)))
            base.dump(out/'TIMING_PROGRESS.json',dict(processes=processes))
            if proc.returncode:raise RuntimeError('Timing failed; all attempted evidence retained')
            print('TIMING',repeat,'completed',flush=True)
        import exact117
        diagnostic=exact117.run(out/'EXACT117.json')
        from audit108 import kernel_diagnostic
        kernel_diagnostic(out/'KERNEL_REPLAY108.json')
        receipt=dict(source=identity,status='executed',processes=processes,
            total_elapsed_seconds=time.perf_counter()-t,
            max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            exact_method_rows=diagnostic['method_rows'],primary_decisions=4608,
            timing_decisions=7168,population_inference=False,neural_exclusive_advantage=False)
        base.dump(out/'CAMPAIGN117.json',receipt)
        print('CAMPAIGN EXECUTED',receipt['total_elapsed_seconds'],flush=True)
    except BaseException:
        base.dump(out/'FAILED.json',dict(source=identity,exception=traceback.format_exc(),
            elapsed_seconds=time.perf_counter()-t,processes=processes))
        raise

if __name__=='__main__':main()
