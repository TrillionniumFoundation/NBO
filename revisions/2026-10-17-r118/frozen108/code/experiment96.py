"""Remotely frozen matched construction and new-stream confirmation for R96."""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,os,pathlib,platform,resource,subprocess,time
import numpy as np
from interval94 import I
from investment94 import terminal_certificate,COUNTS
from continuum94 import uniform_residual,query
from matched96 import construct,encode,decode,KINDS
from quadrature96 import service,paired,TAU,WIDTH,MARGIN,SAMPLE_SIZE
ROOT=pathlib.Path(__file__).resolve().parents[1]
ARMS=('online-risk-dp',)+KINDS
LEVELS=(.5,.75)


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')

def head():
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

def sources():
    names=('interval94.py','investment94.py','terminal_controller94.py','representations94.py',
           'continuum94.py','quadrature96.py','matched96.py','rational96.py',
           'experiment96.py','independent96.py')
    return {'code/'+n:digest(ROOT/'code'/n) for n in names}|{'PROTOCOL96.md':digest(ROOT/'PROTOCOL96.md')}

def rows(stream,index,n):
    rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence([2026101396,stream,index])))
    return rng.integers(0,2**20,size=(n,2),dtype=np.int64)/2**20

def measured(fn,*args,**kw):
    before=COUNTS.copy();t=time.perf_counter();result=fn(*args,**kw)
    return result,dict(seconds=time.perf_counter()-t,counts={k:v-before.get(k,0) for k,v in COUNTS.items() if v!=before.get(k,0)})

def machine():
    cpu=pathlib.Path('/proc/cpuinfo')
    return dict(architecture=platform.machine(),platform=platform.platform(),python=platform.python_version(),
                numpy=np.__version__,cpu_information=[s for s in cpu.read_text().splitlines() if s.startswith(('model name','cpu MHz'))][:8] if cpu.exists() else [],
                frequency_controlled=False,threads={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')})

def execute(x,alpha,model,path,ablation=None):
    result={k:[] for k in ('lower','upper','optimum_lower','loss','width','actions','proposed','rejected','proposed_loss','exact','used_bins')}
    records=[];start=time.perf_counter()
    for begin in range(0,len(x),32):
        data,work=measured(service,x[begin:begin+32],alpha,model);records.append(work)
        for key in result:result[key].extend(np.asarray(data[key]).tolist())
    result={k:np.array(v) for k,v in result.items()}
    before=time.perf_counter();path.parent.mkdir(parents=True,exist_ok=True)
    names=['row','x0','x1']+list(result)
    with path.open('w',newline='') as handle:
        writer=csv.writer(handle);writer.writerow(names)
        for i in range(len(x)):writer.writerow([i,*x[i]]+[result[k][i] for k in result])
    info=dict(rows=len(x),seconds=time.perf_counter()-start,output_seconds=time.perf_counter()-before,
              sha256=digest(path),rejected_proposals=int(result['rejected'].sum()),
              exact_fallbacks=int(result['exact'].sum()),maximum_bins=int(result['used_bins'].max()),
              maximum_loss=float(result['loss'].max()),maximum_width=float(result['width'].max()),
              mean_cost=[float(I(result['lower']).sum().lo/len(x)),float(I(result['upper']).sum().hi/len(x))],
              batches=records,all_rows_qualified=bool(np.all(result['loss']<=TAU)&np.all(result['width']<=WIDTH)))
    if model is not None and ablation is not None:
        # These are certificates of the proposed policy. Switched service rows
        # keep their identity; no scalar claim is silently attached to them.
        gaps=[];t=time.perf_counter()
        for begin in range(0,len(x),32):
            q=query(I(x[begin:begin+32]),I(result['proposed'][begin:begin+32]),alpha,model,128)
            gaps.extend(q['gap'])
        gaps=np.array(gaps);l,u=ablation['lower'],ablation['upper']
        norm=gaps+15/16*(2*max(abs(l),abs(u))+2**-20)
        signed=gaps+15/16*(u-l+2**-20)
        info['prospective_fixed_builder_ablation']=dict(seconds=time.perf_counter()-t,
                norm_passes=int(np.sum(norm<=TAU)),signed_passes=int(np.sum(signed<=TAU)),
                joint_proposal_passes=int(np.sum(result['proposed_loss']<=TAU)),
                scope='Same proposed actors; final service may invoke paid conventional fallback. Not optimally tuned builders.')
    return result,info


def prepare():
    out=ROOT/'results96';freeze=out/'FREEZE96.json'
    if freeze.exists():raise FileExistsError('A committed freeze cannot be overwritten')
    record=dict(source_commit=head(),source_files=sources(),evaluation_rows_opened=0,levels={},machine=machine())
    for index,alpha in enumerate(LEVELS):
        folder=out/f'alpha-{index}';folder.mkdir(parents=True,exist_ok=True)
        x=rows(1,index,1024);labels,lwork=measured(terminal_certificate,I(x),alpha)
        y=labels['lower']+(labels['upper']-labels['lower'])/2
        np.savez(folder/'training.npz',x=x,lower=labels['lower'],upper=labels['upper'])
        info=dict(alpha=alpha,labels=lwork,training_sha256=digest(folder/'training.npz'),models={},calibration={})
        for kind in KINDS:
            model,work=measured(construct,kind,x,y)
            cover,cwork=measured(uniform_residual,model,alpha,32)
            t=time.perf_counter();raw=encode(model);(folder/f'{kind}.bin').write_bytes(raw)
            restored=decode((folder/f'{kind}.bin').read_bytes())
            if not np.array_equal(restored.float_eval(x),model.float_eval(x)):raise AssertionError('Payload changed the continuation')
            io=time.perf_counter()-t;dump(folder/f'{kind}.json',model.to_dict())
            info['models'][kind]=dict(sha256=digest(folder/f'{kind}.bin'),construction=work,cover=cover,
                cover_work=cwork,serialization_reload_seconds=io,fit_record=model.record)
        cal=rows(2,index,128)
        for arm in ARMS:
            model=None if arm=='online-risk-dp' else decode((folder/f'{arm}.bin').read_bytes())
            _,entry=execute(cal,alpha,model,folder/f'calibration-{arm}.csv')
            info['calibration'][arm]=entry
        info['selected']=min(ARMS,key=lambda a:(sum(info['calibration'][a]['mean_cost']),a))
        record['levels'][str(index)]=info
    record['final_models']=6;record['candidate_solver_calls']=COUNTS.get('r96_candidate_fit_solves',0)
    record['counts']=COUNTS.copy();dump(freeze,record)
    return record


def load_freeze(require_committed=True):
    freeze=ROOT/'results96/FREEZE96.json';record=json.loads(freeze.read_text())
    if record['source_files']!=sources():raise RuntimeError('Source changed after freeze')
    if require_committed:
        repo=pathlib.Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip())
        raw=subprocess.check_output(['git','show','HEAD:'+str(freeze.relative_to(repo))],cwd=ROOT)
        if raw!=freeze.read_bytes():raise RuntimeError('Freeze is not committed before evaluation')
    for index in range(2):
        for kind in KINDS:
            if digest(ROOT/f'results96/alpha-{index}/{kind}.bin')!=record['levels'][str(index)]['models'][kind]['sha256']:
                raise RuntimeError('Frozen model changed')
    return record


def evaluate(tag):
    frozen=load_freeze();out=ROOT/f'results96/evaluation-{tag}'
    if (out/'RESULTS96.json').exists():raise FileExistsError('Retain completed evaluations')
    start=time.perf_counter();record=dict(source_commit=head(),freeze_sha256=digest(ROOT/'results96/FREEZE96.json'),
            tag=tag,machine=machine(),levels={},independent_initial_states=8192,new_fits=0,
            tau=TAU,width_target=WIDTH,margin=MARGIN,primary_samples_per_risk=SAMPLE_SIZE)
    for index,alpha in enumerate(LEVELS):
        x=rows(3,index,SAMPLE_SIZE);arms={};observations={}
        for arm in ARMS:
            model=None if arm=='online-risk-dp' else decode((ROOT/f'results96/alpha-{index}/{arm}.bin').read_bytes())
            cover=None if model is None else frozen['levels'][str(index)]['models'][arm]['cover']
            data,info=execute(x,alpha,model,out/f'alpha-{index}-{arm}.csv',cover)
            observations[arm]=data;arms[arm]=info
            dump(out/'PROGRESS96.json',dict(index=index,completed=arms,source_commit=head()))
        pairs={a+' minus '+b:paired(observations[a],observations[b]) for a,b in itertools.combinations(ARMS,2)}
        record['levels'][str(index)]=dict(alpha=alpha,selected=frozen['levels'][str(index)]['selected'],arms=arms,pairs=pairs)
    record['seconds']=time.perf_counter()-start;record['counts']=COUNTS.copy()
    record['maximum_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    record['all_rows_qualified']=all(a['all_rows_qualified'] for level in record['levels'].values() for a in level['arms'].values())
    dump(out/'RESULTS96.json',record);return record


def timing_one(index,arm,path):
    start=time.perf_counter();frozen=load_freeze();folder=ROOT/f'results96/alpha-{index}'
    model=None if arm=='online-risk-dp' else decode((folder/f'{arm}.bin').read_bytes())
    data,info=execute(rows(5,index,32),LEVELS[index],model,path.with_suffix('.csv'))
    info.update(machine=machine(),seconds_inside_process=time.perf_counter()-start,
                counts=COUNTS.copy(),maximum_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                independent_observations_added=0,source_commit=head())
    dump(path,info)


def timing():
    out=ROOT/'results96/timing';out.mkdir(parents=True,exist_ok=True);records=[]
    for repeat in range(5):
        for index in range(2):
            for arm in ARMS:
                path=out/f'{repeat}-{index}-{arm}.json';start=time.perf_counter()
                p=subprocess.run([os.sys.executable,__file__,'timing-one','--index',str(index),'--arm',arm,'--output',str(path)])
                elapsed=time.perf_counter()-start
                records.append(dict(repeat=repeat,index=index,arm=arm,exit_code=p.returncode,
                                    complete_process_seconds=elapsed,file=str(path.relative_to(ROOT))))
                dump(out/'TIMING96.json',dict(records=records,source_commit=head(),new_observations=0,
                    scope='Five fresh processes per arm-risk pair, including interpreter startup, loading, qualification, output and shutdown; CPU frequency recorded, not controlled.'))
                if p.returncode:raise RuntimeError('Timing failure retained')
    return records


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('prepare','evaluate','timing','timing-one'))
    p.add_argument('--tag',default='primary');p.add_argument('--index',type=int);p.add_argument('--arm');p.add_argument('--output',type=pathlib.Path)
    args=p.parse_args()
    if args.mode=='prepare':prepare()
    elif args.mode=='evaluate':evaluate(args.tag)
    elif args.mode=='timing':timing()
    else:timing_one(args.index,args.arm,args.output)
