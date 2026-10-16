"""Frozen deterministic original-economy comparison, not a population sample."""
from __future__ import annotations
from pathlib import Path
import os,sys,json,csv,hashlib,time,platform,resource,subprocess,traceback
import numpy as np
import scipy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import kernel108 as kern
import represent108 as rep
from interval94 import I,up
from investment94 import COUNTS, count
import quadrature96 as q
import continuum94 as c
SERVICES=('legacy','compiled','legacy-safe','compiled-safe')
LEVELS=(.5,.75)
KEYS=('lower','upper','optimum_lower','loss','width')


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def dump(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w') as f:
        json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())

def machine():
    p=Path('/proc/cpuinfo')
    return {'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,
      'cpu':p.read_text().split('\n\n')[0] if p.exists() else None,
      'threads':{x:os.environ.get(x) for x in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},
      'frequency_and_external_load_controlled':False,'time_is_descriptive':True}


def source():
    f=ROOT/'SOURCE_FREEZE108.json'
    if not f.exists():raise RuntimeError('Actual source freeze required before primary execution')
    freeze=json.loads(f.read_text())
    if digest(ROOT/'PROTOCOL108.md')!=freeze['protocol_sha256']:raise RuntimeError('Frozen protocol differs')
    for path,h in freeze['scientific_files'].items():
        if digest(ROOT/path)!=h:raise RuntimeError('Frozen scientific source differs: '+path)
    commit=os.environ.get('NBO_PROTOCOL108')
    if not commit or len(commit)!=40 or any(v not in '0123456789abcdef' for v in commit):raise RuntimeError('Set NBO_PROTOCOL108 to the deposited protocol/source commit')
    return {'protocol_source_commit':commit,'source_manifest_sha256':digest(f),'scientific_files':freeze['scientific_files']}


def counter_delta(before):return {key:COUNTS.get(key,0)-before.get(key,0) for key in sorted(set(COUNTS)|set(before)) if COUNTS.get(key,0)!=before.get(key,0)}


def complete_service(x,alpha,model,compiled=False,safe=False):
    x=np.asarray(x,dtype=float);before=COUNTS.copy();start=time.perf_counter();clock={};trials=[]
    with kern.backend(compiled):
        t=time.perf_counter();proposed=rep.proposal(x,alpha,model);clock['proposal']=time.perf_counter()-t
        actions=proposed.copy();t=time.perf_counter();rec=q.certificate(x,actions,alpha);clock['first_certificate']=time.perf_counter()-t
        first={key:rec[key].copy() for key in KEYS};rejected=~q.qualifies(rec)
        used=np.full(len(x),128,int);exact=np.zeros(len(x),bool)
        clock.update(conventional_fallback=0.,refinement=0.,exact_fallback=0.,safe_improvement=0.)
        if np.any(rejected):
            t=time.perf_counter();actions[rejected]=c.actor(x[rejected],alpha,None)
            fresh=q.certificate(x[rejected],actions[rejected],alpha)
            for key in KEYS:rec[key][rejected]=fresh[key]
            count('completed_conventional_fallback_rows',int(rejected.sum()))
            clock['conventional_fallback']=time.perf_counter()-t
        for bins in (256,512,1024,2048,4096):
            bad=~q.qualifies(rec)
            if not np.any(bad):break
            t=time.perf_counter();fresh=q.certificate(x[bad],actions[bad],alpha,bins)
            for key in KEYS:rec[key][bad]=fresh[key]
            used[bad]=bins;clock['refinement']+=time.perf_counter()-t
        for j in np.flatnonzero(~q.qualifies(rec)):
            from rational96 import exact_service
            t=time.perf_counter();a,low,high,opt,n=exact_service(x[j],alpha)
            actions[j]=a;rec['lower'][j]=low;rec['upper'][j]=high;rec['optimum_lower'][j]=opt
            rec['loss'][j]=up(high-opt);rec['width'][j]=up(high-low);used[j]=n;exact[j]=True
            clock['exact_fallback']+=time.perf_counter()-t
        if not np.all(q.qualifies(rec)):raise ArithmeticError('Original completed service failed closed')
        baseline={key:rec[key].copy() for key in KEYS};baseline_actions=actions.copy()
        improvements=np.zeros(len(x),int)
        if safe:
            t=time.perf_counter()
            for trial,fraction in enumerate((1.,.5,.25)):
                support=c.query(I(x),I(actions),alpha,None,128)
                step=np.clip(actions-support['gradient'].mid()/2,0,kern.econ.capacity(I(x)).lo)
                candidate=np.floor((actions+fraction*(step-actions))*2**30)/2**30
                candidate=np.minimum(candidate,np.floor(kern.econ.capacity(I(x)).lo*2**30)/2**30)
                fresh=q.certificate(x,candidate,alpha)
                # A valid common optimum lower bound may be reused. No policy
                # interval is reused across different candidate actions.
                fresh['optimum_lower']=np.maximum(fresh['optimum_lower'],rec['optimum_lower'])
                fresh['loss']=up(fresh['upper']-fresh['optimum_lower'])
                if np.any(fresh['loss']<0):raise ArithmeticError('Contradictory reused optimum lower bound')
                accepted=(fresh['upper']<rec['lower'])&q.qualifies(fresh)&(candidate!=actions)
                for j in range(len(x)):
                    trials.append({'row':j,'trial':trial,'fraction':fraction,'incumbent_action':float(actions[j]),
                       'incumbent_lower':float(rec['lower'][j]),'incumbent_upper':float(rec['upper'][j]),
                       'candidate_action':float(candidate[j]),'candidate_lower':float(fresh['lower'][j]),
                       'candidate_upper':float(fresh['upper'][j]),'candidate_optimum_lower':float(fresh['optimum_lower'][j]),
                       'candidate_loss':float(fresh['loss'][j]),'candidate_width':float(fresh['width'][j]),
                       'accepted':bool(accepted[j]),'support_gradient_lower':float(support['gradient'].lo[j]),
                       'support_gradient_upper':float(support['gradient'].hi[j])})
                actions[accepted]=candidate[accepted];improvements+=accepted.astype(int)
                for key in KEYS:rec[key][accepted]=fresh[key][accepted]
            clock['safe_improvement']=time.perf_counter()-t
        if not np.all(q.qualifies(rec)):raise ArithmeticError('Post-improvement original target failure')
    rows=[]
    for j,state in enumerate(x):
        row={'row':j,'x0':float(state[0]),'x1':float(state[1]),'proposed':float(proposed[j]),'action':float(actions[j]),
             'first_rejected':bool(rejected[j]),'bins':int(used[j]),'exact_fallback':bool(exact[j]),
             'safe_changes':int(improvements[j]),'completed_baseline_action':float(baseline_actions[j]),
             'action_distance_upper':float(up(np.sqrt(rec['loss'][j])))}
        for key in KEYS:
            row[key]=float(rec[key][j]);row['first_'+key]=float(first[key][j]);row['baseline_'+key]=float(baseline[key][j])
        rows.append(row)
    return {'rows':rows,'trials':trials,'clock':clock,'seconds':time.perf_counter()-start,
            'counts':counter_delta(before),'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'terminal_policy_unchanged':True}


def acquire(out):
    x=rep.grid(16);receipts=[]
    for index,alpha in enumerate(LEVELS):
        before=COUNTS.copy();t=time.perf_counter()
        lab=kern.OLD_CERTIFICATE(I(x),alpha);label_seconds=time.perf_counter()-t;label_counts=counter_delta(before)
        dump(out/f'labels-{index}.json',{'x':x.tolist(),'lower':lab['lower'].tolist(),'upper':lab['upper'].tolist(),
             'seconds':label_seconds,'counts':label_counts,'source':'unchanged original-model terminal certificate'})
        t=time.perf_counter();models,records=rep.fit_all(x,lab);fit_total=time.perf_counter()-t
        for arm in rep.ARMS:
            folder=out/'models'/f'{index}-{arm}';folder.mkdir(parents=True,exist_ok=True)
            (folder/'model.json').write_bytes(rep.encoded(models[arm]))
            r=records[arm];r.update(alpha=alpha,arm=arm,model_sha256=digest(folder/'model.json'),
                                  label_cost_if_standalone_seconds=label_seconds if arm!='online' else 0,
                                  shared_label_counts_if_standalone=label_counts if arm!='online' else {},
                                  label_sites=256 if arm!='online' else 0)
            dump(folder/'acquisition.json',r)
        receipts.append({'index':index,'alpha':alpha,'label_seconds':label_seconds,'all_models_fit_and_audit_seconds':fit_total,
                         'models':{arm:digest(out/'models'/f'{index}-{arm}'/'model.json') for arm in rep.ARMS}})
    dump(out/'ACQUISITION.json',{'source':source(),'records':receipts,'new_random_samples':0})


def load_models(out,index):
    return {arm:rep.restore(json.loads((out/'models'/f'{index}-{arm}'/'model.json').read_text())) for arm in rep.ARMS}


def catalogue(out):
    x=rep.grid(8);records=[]
    for index,alpha in enumerate(LEVELS):
        models=load_models(out,index)
        for arm in rep.ARMS:
            for service in SERVICES:
                data=complete_service(x,alpha,models[arm],service.startswith('compiled'),service.endswith('safe'))
                data.update(index=index,alpha=alpha,arm=arm,service=service,model_sha256=digest(out/'models'/f'{index}-{arm}'/'model.json'))
                path=out/'catalogue'/f'{index}-{arm}-{service}.json';dump(path,data)
                records.append({'path':str(path.relative_to(out)),'sha256':digest(path),'decisions':len(x),
                     'seconds':data['seconds'],'first_rejections':sum(r['first_rejected'] for r in data['rows']),
                     'safe_changes':sum(r['safe_changes'] for r in data['rows'])})
                print('CATALOGUE',index,arm,service,round(data['seconds'],3),flush=True)
                dump(out/'PROGRESS.json',{'source':source(),'catalogue':records,'status':'running'})
    dump(out/'CATALOGUE.json',{'source':source(),'catalogue':records,'status':'executed','decisions':sum(r['decisions'] for r in records)})


def reference(out):
    x=rep.grid(8);records=[]
    for index,alpha in enumerate(LEVELS):
        before=COUNTS.copy();t=time.perf_counter()
        with kern.backend(True):
            actions=c.actor(x,alpha,None);rec=q.certificate(x,actions,alpha,4096)
        records.append({'index':index,'alpha':alpha,'x':x.tolist(),'actions':actions.tolist(),
          **{key:rec[key].tolist() for key in KEYS},'seconds':time.perf_counter()-t,'counts':counter_delta(before),
          'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'not_an_exact_optimal_policy':True})
    dump(out/'REFERENCE.json',{'source':source(),'records':records,'reference_is_charged_benchmark_work':True})


def timing_one(out,repeat):
    x=rep.grid(8)[:32];records=[];start=time.perf_counter()
    for index,alpha in enumerate(LEVELS):
        models=load_models(out,index)
        for arm in rep.ARMS:
            for service in SERVICES:
                data=complete_service(x,alpha,models[arm],service.startswith('compiled'),service.endswith('safe'))
                path=out/'timing'/f'{repeat}-{index}-{arm}-{service}.json';dump(path,data)
                records.append({'index':index,'arm':arm,'service':service,'seconds':data['seconds'],
                                'path':str(path.relative_to(out)),'sha256':digest(path),'counts':data['counts']})
    dump(out/'timing'/f'PROCESS-{repeat}.json',{'repeat':repeat,'source':source(),'machine':machine(),'records':records,
                   'inside_process_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('all','acquire','catalogue','reference','timing-one'))
    p.add_argument('--output',type=Path,default=ROOT/'results108');p.add_argument('--repeat',type=int,default=0)
    a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True);source()
    if a.mode=='timing-one':return timing_one(out,a.repeat)
    if a.mode!='all':return globals()[a.mode](out)
    if (out/'START.json').exists():raise FileExistsError('Do not overwrite an attempted primary campaign; use a distinct replication output directory')
    dump(out/'START.json',{'source':source(),'machine':machine(),'started_unix':time.time()})
    t=time.perf_counter();receipt={'source':source(),'processes':[]}
    try:
        acquire(out);catalogue(out);reference(out)
        for repeat in range(7):
            command=[sys.executable,__file__,'timing-one','--output',str(out),'--repeat',str(repeat)]
            start=time.perf_counter();process=subprocess.run(command,capture_output=True,text=True)
            log=out/'timing'/f'PROCESS-{repeat}.log';log.parent.mkdir(exist_ok=True);log.write_text(process.stdout+process.stderr)
            receipt['processes'].append({'repeat':repeat,'command':command,'exit_code':process.returncode,
                  'elapsed_seconds':time.perf_counter()-start,'log_sha256':digest(log)})
            dump(out/'TIMING_PROGRESS.json',receipt)
            if process.returncode:raise RuntimeError('Timing process failed; all attempted evidence retained')
            print('TIMING PROCESS',repeat,'done',flush=True)
        receipt.update(status='executed',total_elapsed_seconds=time.perf_counter()-t,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        dump(out/'CAMPAIGN108.json',receipt)
    except BaseException:
        dump(out/'FAILED.json',{'source':source(),'exception':traceback.format_exc(),'elapsed_seconds':time.perf_counter()-t})
        raise

if __name__=='__main__':main()
