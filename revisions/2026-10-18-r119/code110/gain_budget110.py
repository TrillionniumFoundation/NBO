"""R110 gain-budgeted improvements under the unchanged original Bellman target.

Controls and acquisition are the immutable R108-source reproduction. No training
or population resampling occurs here. Stopping discards at most the recorded
upper bound on remaining original-policy improvement, not its loss tolerance.
"""
from __future__ import annotations
from pathlib import Path
import os,sys,json,time,hashlib,resource,subprocess,traceback,copy
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=Path(os.environ.get('NBO_FROZEN108',ROOT/'frozen108')).resolve()
sys.path.insert(0,str(BASE/'code108'))
import campaign108 as base
import kernel108 as kern
import represent108 as rep
from interval94 import I,up
from investment94 import COUNTS,count
import continuum94 as cont
import quadrature96 as quad
SERVICES=('compiled','compiled-safe','gain-12','gain-14','gain-16','gain-18')
KEYS=base.KEYS


def source():
    manifest=ROOT/'SOURCE_FREEZE110.json'
    info=json.loads(manifest.read_text())
    for name,expected in info['scientific_files'].items():
        p=ROOT/name
        if base.digest(p)!=expected:raise RuntimeError('R110 frozen source differs: '+name)
    commit=os.environ.get('NBO_SOURCE110','')
    if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise RuntimeError('The remote R110 executable-source freeze SHA is required')
    return {'new_source_commit':commit,'new_source_manifest_sha256':base.digest(manifest),
            'inherited':base.source(),'new_random_samples':0}


def validate(rec):
    for key in KEYS:
        if not np.all(np.isfinite(rec[key])):raise ArithmeticError('Nonfinite certificate')
    if np.any(rec['lower']>rec['upper']) or np.any(rec['optimum_lower']>rec['upper']):
        raise ArithmeticError('Contradictory original certificate')
    if np.any(rec['loss']<0) or np.any(rec['width']<0) or not np.all(quad.qualifies(rec)):
        raise ArithmeticError('Unqualified completed incumbent')


def service(x,alpha,model,name):
    if name not in SERVICES:raise ValueError('Unregistered service')
    if name in ('compiled','compiled-safe'):
        data=base.complete_service(x,alpha,model,True,name.endswith('safe'))
        data.update(service=name,theta=None,scope='unchanged R108 complete control',stop_checks=0)
        return data
    theta=2.0**(-int(name.split('-')[1]));x=np.asarray(x,dtype=float)
    before=COUNTS.copy();start=time.perf_counter()
    data=base.complete_service(x,alpha,model,True,False)
    rows=data['rows'];actions=np.array([r['action'] for r in rows]);initial_actions=actions.copy()
    rec={key:np.array([r[key] for r in rows]) for key in KEYS};validate(rec)
    stopped=np.zeros(len(x),bool);changes=np.zeros(len(x),int);first_stop=np.full(len(x),-1,int)
    stop_bounds=[None for _ in rows];trials=[];stop_checks=0;t=time.perf_counter()
    with kern.backend(True):
        for trial,fraction in enumerate((1.,.5,.25)):
            validate(rec)
            # Only a valid CURRENT original-optimum bound authorizes stopping.
            entering=~stopped;stop_checks+=int(entering.sum())
            new_stop=entering&(rec['loss']<=theta)
            for j in np.flatnonzero(new_stop):
                first_stop[j]=trial
                stop_bounds[j]={'action':float(actions[j]),**{k:float(rec[k][j]) for k in KEYS}}
            stopped|=new_stop
            ids=np.flatnonzero(~stopped)
            attempted={}
            if len(ids):
                xx=x[ids];aa=actions[ids]
                support=cont.query(I(xx),I(aa),alpha,None,128)
                cap=kern.econ.capacity(I(xx)).lo
                step=np.clip(aa-support['gradient'].mid()/2,0,cap)
                candidate=np.floor((aa+fraction*(step-aa))*2**30)/2**30
                candidate=np.minimum(candidate,np.floor(cap*2**30)/2**30)
                fresh=quad.certificate(xx,candidate,alpha)
                fresh['optimum_lower']=np.maximum(fresh['optimum_lower'],rec['optimum_lower'][ids])
                fresh['loss']=up(fresh['upper']-fresh['optimum_lower'])
                if np.any(fresh['loss']<0):raise ArithmeticError('Contradictory candidate lower bound')
                accepted=(fresh['upper']<rec['lower'][ids])&quad.qualifies(fresh)&(candidate!=aa)
                for k,j in enumerate(ids):
                    attempted[int(j)]={'row':int(j),'trial':trial,'fraction':fraction,'skipped':False,
                      'incumbent_action':float(aa[k]),**{'incumbent_'+v:float(rec[v][j]) for v in KEYS},
                      'candidate_action':float(candidate[k]),**{'candidate_'+v:float(fresh[v][k]) for v in KEYS},
                      'support_gradient_lower':float(support['gradient'].lo[k]),
                      'support_gradient_upper':float(support['gradient'].hi[k]),'accepted':bool(accepted[k])}
                for k,j in enumerate(ids):
                    if accepted[k]:
                        actions[j]=candidate[k];changes[j]+=1
                        for key in KEYS:rec[key][j]=fresh[key][k]
            for j in range(len(x)):
                if j in attempted:trials.append(attempted[j])
                else:trials.append({'row':j,'trial':trial,'fraction':fraction,'skipped':True,'accepted':False,
                     'reason':'certified original-policy remaining-gain ceiling','theta':theta,
                     'incumbent_action':float(actions[j]),**{'incumbent_'+v:float(rec[v][j]) for v in KEYS}})
            count('r110_stopping_predicates',int(entering.sum()))
            count('r110_omitted_support_and_trial_pairs',int(stopped.sum()))
            count('r110_active_support_and_trial_pairs',len(ids))
    validate(rec)
    for j,row in enumerate(rows):
        row.update(action=float(actions[j]),safe_changes=int(changes[j]),theta=theta,
                   stopped=bool(stopped[j]),first_stop_round=int(first_stop[j]),stop_certificate=stop_bounds[j],
                   action_distance_upper=float(up(np.sqrt(rec['loss'][j]))))
        for key in KEYS:row[key]=float(rec[key][j])
        if row['completed_baseline_action']!=float(initial_actions[j]):raise ArithmeticError('Baseline custody')
    data.update(rows=rows,trials=trials,counts=base.counter_delta(before),service=name,theta=theta,
                stop_checks=stop_checks,seconds=time.perf_counter()-start,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    data['clock']['gain_budget_improvement']=time.perf_counter()-t
    data['scope']='original completed incumbent, immutable tail-law and future policy, gain-budgeted extra work'
    return data


def inventory_models(acquired):
    paths=[Path(acquired)/'models'/f'{i}-{a}'/'model.json' for i in range(2) for a in rep.ARMS]
    return {str(p.relative_to(acquired)):base.digest(p) for p in paths}


def execute_catalogue(acquired,out,repeat=None):
    x=rep.grid(8) if repeat is None else rep.grid(8)[:32]
    rows=[];inside=time.perf_counter()
    for i,alpha in enumerate(base.LEVELS):
        models=base.load_models(acquired,i)
        for arm in rep.ARMS:
            for name in SERVICES:
                d=service(x,alpha,models[arm],name)
                d.update(risk_index=i,alpha=alpha,arm=arm,model_sha256=base.digest(acquired/'models'/f'{i}-{arm}'/'model.json'))
                relative=Path('catalogue')/f'{i}-{arm}-{name}.json' if repeat is None else Path('timing')/f'{repeat}-{i}-{arm}-{name}.json'
                base.dump(out/relative,d)
                rows.append({'path':str(relative),'sha256':base.digest(out/relative),'risk_index':i,'alpha':alpha,
                             'arm':arm,'service':name,'decisions':len(x),'seconds':d['seconds'],'counts':d['counts']})
                if repeat is None:
                    base.dump(out/'PROGRESS.json',{'status':'running','records':rows});print(i,arm,name,round(d['seconds'],3),flush=True)
    record={'source':source(),'models':inventory_models(acquired),'records':rows,
            'inside_process_seconds':time.perf_counter()-inside,'machine':base.machine(),
            'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    base.dump(out/'CATALOGUE110.json' if repeat is None else out/'timing'/f'PROCESS-{repeat}.json',record)


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('all','timing-one'))
    p.add_argument('--acquired',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--repeat',type=int,default=0);args=p.parse_args();source()
    acquired=args.acquired.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if args.mode=='timing-one':return execute_catalogue(acquired,out,args.repeat)
    if (out/'START110.json').exists():raise FileExistsError('Keep prior attempts; use a new output directory')
    base.dump(out/'START110.json',{'source':source(),'started_unix':time.time(),'models':inventory_models(acquired),
              'protocol_commit':'f43602de6a29132feceb36d4b323c4c21a9e6ebe','primary_theta':2**-16})
    t=time.perf_counter();receipt={'source':source(),'processes':[]}
    try:
        execute_catalogue(acquired,out)
        for repeat in range(7):
            cmd=[sys.executable,__file__,'timing-one','--acquired',str(acquired),'--output',str(out),'--repeat',str(repeat)]
            ts=time.perf_counter();run=subprocess.run(cmd,capture_output=True,text=True)
            log=out/'timing'/f'PROCESS-{repeat}.log';log.parent.mkdir(exist_ok=True);log.write_text(run.stdout+run.stderr)
            receipt['processes'].append({'repeat':repeat,'command':cmd,'exit_code':run.returncode,
                                        'elapsed_seconds':time.perf_counter()-ts,'log_sha256':base.digest(log)})
            base.dump(out/'TIMING_PROGRESS110.json',receipt)
            if run.returncode:raise RuntimeError('Fresh timing failed; partial data retained')
            print('TIMING',repeat,'complete',flush=True)
        receipt.update(status='executed',total_elapsed_seconds=time.perf_counter()-t)
        base.dump(out/'CAMPAIGN110.json',receipt)
    except BaseException:
        base.dump(out/'FAILED110.json',{'source':source(),'exception':traceback.format_exc(),'seconds':time.perf_counter()-t})
        raise

if __name__=='__main__':main()
