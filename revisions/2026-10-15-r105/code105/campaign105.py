"""Separate, source-frozen R105 postqualification experiment; stages are write-once."""
from __future__ import annotations
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key]='1'
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, time, traceback
from datetime import datetime, timezone
import numpy as np
from descent105 import ROOT, MODES, service, inv
sys.path.insert(0,str(ROOT/'code104'))
import campaign104 as prior
from fitting104 import ARMS
BASE=ROOT/'results105/postqualification'
PROTOCOL_COMMIT='bbc3d3e07137de97cac6b7c40a8d1e186e9229da'
SCIENTIFIC=('descent105.py','campaign105.py')


def save(path,obj):
    prior.save(path,obj)


def sites():
    axis=np.array([(3*i+1)/24 for i in range(8)],dtype=float)
    return np.stack(np.meshgrid(axis,axis,indexing='ij'),-1).reshape(-1,2)


def manifest():
    source={f'code105/{name}':prior.sha(ROOT/'code105'/name) for name in SCIENTIFIC}
    actors={str(p.relative_to(ROOT)):prior.sha(p) for p in sorted((ROOT/'results104/acquisition').glob('model-*.json'))}
    return dict(source_files=source,actor_files=actors)


def verify():
    prior.verify_freeze()
    record=json.loads((BASE/'FREEZE105.json').read_text())
    actual=manifest()
    if record['source_files']!=actual['source_files'] or record['actor_files']!=actual['actor_files']:
        raise RuntimeError('Frozen scientific source or actors changed')
    if len(actual['actor_files'])!=16:raise RuntimeError('Incomplete fixed actor menu')


def freeze():
    prior.verify_freeze()
    if (BASE/'FREEZE105.json').exists():raise RuntimeError('Do not overwrite freeze')
    x=sites()
    for grid in (prior.sites(16),prior.sites(8)):
        if set(map(tuple,x))&set(map(tuple,grid)):raise RuntimeError('Catalogue not disjoint')
    record=manifest()
    if len(record['actor_files'])!=16:raise RuntimeError('Incomplete actor menu')
    save(BASE/'FREEZE105.json',dict(record,protocol_commit=PROTOCOL_COMMIT,
         inherited_source_commit='922964becc2e76c8d5965cb1c4a263ac8579cace',
         source_freeze104_sha256=prior.sha(ROOT/'results104/source_freeze.json'),
         utc=prior.utc(),states=x.tolist(),timing_states=x[:32].tolist(),
         source_scope='two new scientific modules plus the unchanged 136-file R104 dependency manifest',
         design_scope='chosen after disclosed R104 observations, before R105 execution; deterministic catalogue, not a random population sample'))
    print('FROZEN',json.dumps(record['source_files']),flush=True)


def start(name):
    verify()
    path=BASE/(name+'.started.json')
    if path.exists():raise RuntimeError('Stage already attempted; preserve evidence before any amendment')
    save(path,dict(utc=prior.utc(),protocol_commit=PROTOCOL_COMMIT,environment=prior.environment()))


def one(x,alpha,model,mode,keep):
    inv.COUNTS.clear();begin=time.perf_counter()
    rec=service(x,alpha,model,mode,keep_trials=keep)
    import resource
    work=dict(seconds=time.perf_counter()-begin,counts=dict(inv.COUNTS),
              rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return rec,work


def catalogue():
    start('catalogue');x=sites();summary=[]
    for index,alpha in enumerate((.5,.75)):
        models=prior.load_models(index)
        for arm in ARMS:
            incumbent=None
            for mode in MODES:
                rec,work=one(x,alpha,models[arm],mode,True)
                if incumbent is None:incumbent=rec
                else:
                    for key in ('actions','lower','upper','optimum_lower'):
                        if not np.array_equal(incumbent[key],rec['baseline_'+key]):
                            raise ArithmeticError('Complete incumbent changed between services')
                save(BASE/f'catalogue/{index}-{arm}-{mode}.json',
                     dict(alpha=alpha,arm=arm,mode=mode,x=x.tolist(),results=prior.serial(rec),work=work))
                row=dict(alpha=alpha,arm=arm,mode=mode,accepted=int(rec['post_accepted'].sum()),
                         skipped=int(rec['post_skipped'].sum()),cost_queries=int(rec['post_queries'].sum()),
                         max_loss=float(np.max(rec['loss'])),max_width=float(np.max(rec['width'])),work=work)
                summary.append(row)
                print('R105',alpha,arm,mode,'accepted',row['accepted'],'queries',row['cost_queries'],flush=True)
    save(BASE/'catalogue/summary.json',summary)
    save(BASE/'catalogue.success.json',dict(utc=prior.utc(),combinations=len(summary),
          decisions=len(summary)*len(x),all_qualified=True,baseline_identity=True,
          scope='complete fixed new original-economy catalogue, not population inference'))


def timing_worker(index):
    verify();x=sites()[:32];rows=[];begin=time.perf_counter()
    for k,alpha in enumerate((.5,.75)):
        models=prior.load_models(k)
        for arm in ARMS:
            for mode in MODES:
                rec,work=one(x,alpha,models[arm],mode,False)
                rows.append(dict(repetition=index,alpha=alpha,arm=arm,mode=mode,work=work,
                    accepted=int(rec['post_accepted'].sum()),
                    action_sha256=hashlib.sha256(rec['actions'].tobytes()).hexdigest(),
                    qualified=bool(np.all(rec['loss']<=1/256)&np.all(rec['width']<=1/8192))))
    save(BASE/f'clocks/repetition-{index}.json',dict(rows=rows,
          internal_process_seconds=time.perf_counter()-begin,environment=prior.environment()))


def clocks():
    start('clocks');records=[];(BASE/'clocks').mkdir(exist_ok=True)
    for index in range(7):
        begin=time.perf_counter()
        with (BASE/f'clocks/repetition-{index}.log').open('w') as log:
            completed=subprocess.run([sys.executable,__file__,'timing-worker','--index',str(index)],stdout=log,stderr=subprocess.STDOUT)
        rec=dict(repetition=index,returncode=completed.returncode,external_process_seconds=time.perf_counter()-begin)
        records.append(rec);save(BASE/'clocks/processes.json',records)
        print('R105 CLOCK',rec,flush=True)
        if completed.returncode:raise RuntimeError('Timing failure retained')
    save(BASE/'clocks.success.json',dict(utc=prior.utc(),processes=7,combinations_per_process=48,
          scope='one-thread descriptive clocks on this host; not pooled with R104'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=['freeze','catalogue','clocks','timing-worker'])
    p.add_argument('--index',type=int,default=0);a=p.parse_args()
    try:
        if a.stage=='timing-worker':timing_worker(a.index)
        else:globals()[a.stage]()
    except Exception:
        directory=BASE/'failures';directory.mkdir(parents=True,exist_ok=True)
        (directory/('failure-'+a.stage+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'.log')).write_text(traceback.format_exc())
        raise

if __name__=='__main__':main()
