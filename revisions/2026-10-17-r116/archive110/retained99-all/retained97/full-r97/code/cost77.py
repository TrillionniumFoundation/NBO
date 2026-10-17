"""Predetermined original-law cost qualification; fitting is never rerun.

Execute once with --execute after the source freeze. --replay recomputes all
new path enclosures and statistical endpoints without modifying measurements.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import argparse,hashlib,itertools,json,math,os,platform,resource,time
import numpy as np
import float77 as production
import independent77 as independent
R=Path(__file__).resolve().parents[1]
OLD=R.parent/'2026-10-11-r73'
N=524288;BITS=40;BATCH=8192;SEED=20261011077;LOG=10;S=independent.S
H=F(21097,4096);MARGIN=F(1,256)
NAMES=('zero','relu-n8','bernstein-n8','relu-n16','bernstein-n16')
EXPECTED={
 'relu-n8':'0c1358216a7e2daf63e930a1081bb8510f039eba99a06af426bd18e1d56e92ee',
 'bernstein-n8':'6933f7edfd904798bea6481cf35841ee5a685b664557a2ba9830214968cbc8f9',
 'relu-n16':'5f334cf5cc478c1f080247c02b73df64bda0742f629e97d9620e6699a9f70f22',
 'bernstein-n16':'eda461a25f4be89931d8b0e5d3669afd404c9c83abb00000cb57db5b44e7623b'}

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    return x
def save(path,x):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(encode(x),indent=2,sort_keys=True)+'\n')
def read(path):return json.loads(Path(path).read_text())
def exact_sqrt_up(x,bits=60):
    x=F(x)
    if x<0:raise ValueError('Negative squared radius')
    scale=1<<bits;k=math.isqrt((x.numerator*scale*scale)//x.denominator)
    if k*k*x.denominator<x.numerator*scale*scale:k+=1
    return F(k,scale)
def rounded(x,upper):
    y=float(x);return float(np.nextafter(y,np.inf if upper else -np.inf))

def environment():
    freq={}
    for p in sorted(Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq/scaling_governor'))[:8]:
        for name in ('scaling_governor','scaling_cur_freq','scaling_min_freq','scaling_max_freq'):
            q=p.parent/name
            if q.exists():freq[str(q)]=q.read_text().strip()
    return dict(python=platform.python_version(),numpy=np.__version__,machine=platform.machine(),processor=platform.processor(),affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,frequency=freq,frequency_locked=False)

def controllers():
    out={'zero':np.zeros((2,1,1),dtype=np.int64)};metadata={}
    for name,h in EXPECTED.items():
        path=OLD/'results73'/name/'service.json'
        if sha(path)!=h:raise AssertionError('Frozen constructed controller changed: '+name)
        data=read(path);n=data['n'];actions=np.zeros((2,n,n),dtype=np.int64)
        for t,stage in enumerate(data['stages']):
            if stage['date']!=t:raise AssertionError('Backward stage identity')
            values=[F(v)*4096 for v in stage['data']['actions']]
            if any(v.denominator!=1 for v in values) or len(values)!=n*n:raise AssertionError('Invalid action quantum')
            actions[t]=np.asarray([int(v) for v in values]).reshape(n,n)
        for i,j in itertools.product(range(n),repeat=2):
            cap=F(1,8)+F(i+j,16*n)
            if np.any(actions[:,i,j]<0) or any(F(int(v),4096)>cap for v in actions[:,i,j]):raise AssertionError('Whole-cell feasibility')
        out[name]=actions
        clock=read(path.parent/'clock.json')
        if clock['service_sha256']!=h:raise AssertionError('Construction clock identity')
        metadata[name]=dict(n=n,service_sha256=h,actor_sha256=hashlib.sha256(actions.tobytes()).hexdigest(),construction_seconds=clock['seconds_through_service_output'],construction_scope=data['accounting'],regret_upper=data['original_optimum_regret_upper'],optimization_passed=data['all_optimization_gaps_pass'])
    return out,metadata

def verify_freeze():
    f=read(R/'SOURCE_FREEZE77.json')
    for name,h in f['files'].items():
        if sha(R/name)!=h:raise AssertionError('R77 scientific source changed: '+name)
    if f['controllers']!=EXPECTED:raise AssertionError('Controller freeze mismatch')
    return f

def enclose(paths,actions):
    floating=production.Actor(actions);integer=independent.IntegerActor(actions)
    result=np.empty((4,len(paths)),dtype=np.int64);float_seconds=integer_seconds=0.;max_difference=0
    for begin in range(0,len(paths),BATCH):
        end=min(len(paths),begin+BATCH);part=paths[begin:end]
        start=time.perf_counter();f=production.evaluate(part,floating,BITS);float_seconds+=time.perf_counter()-start
        start=time.perf_counter();z=independent.evaluate(part,integer,BITS);integer_seconds+=time.perf_counter()-start
        for k,box in enumerate(f):
            low=np.floor(box.lo*S).astype(np.int64);high=np.ceil(box.hi*S).astype(np.int64)
            if np.any(low>z[2*k+1]) or np.any(z[2*k]>high):
                bad=np.flatnonzero((low>z[2*k+1])|(z[2*k]>high))
                save(R/'audit/ARITHMETIC_DISAGREEMENT77.json',dict(begin=begin,local_rows=bad[:20].tolist(),bins=part[bad[:20]].tolist()))
                raise AssertionError('Independent full-bin enclosures disjoint')
            max_difference=max(max_difference,int(np.max(np.abs(low-z[2*k]))),int(np.max(np.abs(high-z[2*k+1]))))
            result[2*k,begin:end]=np.maximum(0,np.minimum(low,z[2*k]))
            result[2*k+1,begin:end]=np.minimum(int(H*S),np.maximum(high,z[2*k+1]))
    if np.any(result[::2]>result[1::2]):raise AssertionError('Published hull reversed')
    checks=0
    for row in np.linspace(0,len(paths)-1,min(512,len(paths)),dtype=np.int64):
        for k,value in enumerate(independent.exact_point(paths[row],actions,BITS)):
            if not F(int(result[2*k,row]),S)<=value<=F(int(result[2*k+1,row]),S):raise AssertionError(('Exact midpoint outside enclosure',int(row),k))
        checks+=1
    return result,dict(float_evaluation_seconds=float_seconds,integer_evaluation_seconds=integer_seconds,
         complete_interval_trajectories_per_implementation=len(paths),exact_midpoint_checks=checks,
         binary64_acquisition_ambiguities=floating.ambiguous_rows,integer_acquisition_ambiguities=integer.ambiguous_rows,
         binary64_actor_queries=floating.action_calls,integer_actor_queries=integer.action_calls,
         integer_rectangle_evaluations=integer.rectangles,largest_endpoint_disagreement_units=max_difference,
         published_endpoint_unit='1/'+str(S),original_optimal_value_queries=0)

def moments(values):
    numbers=[int(v) for v in values];n=len(numbers);total=sum(numbers);squares=sum(v*v for v in numbers)
    variance=F(n*squares-total*total,n*(n-1)*S*S)
    if variance<0:raise AssertionError('Exact variance negative')
    return F(total,n*S),variance,dict(sum=total,sum_squares=squares,n=n,unit=S)

def interval(lo,hi,support):
    if np.any(lo>hi):raise AssertionError('Endpoint order')
    if min(lo)<support[0]*S or max(hi)>support[1]*S:raise AssertionError('Endpoint exceeds proved support')
    lm,lv,ls=moments(lo);um,uv,us=moments(hi);n=len(lo);width=support[1]-support[0]
    sampling_lower=exact_sqrt_up(2*lv*LOG/n);sampling_upper=exact_sqrt_up(2*uv*LOG/n)
    penalty=7*width*LOG/(3*(n-1));left=lm-sampling_lower-penalty;right=um+sampling_upper+penalty
    numerical=um-lm;variance_term=sampling_lower+sampling_upper;support_term=2*penalty
    if right-left!=numerical+variance_term+support_term:raise AssertionError('Width decomposition')
    return dict(interval_exact=(left,right),interval=(rounded(left,False),rounded(right,True)),
      endpoint_mean_exact=(lm,um),enclosure_midpoint_mean=(lm+um)/2,
      endpoint_variance_exact=(lv,uv),moments=(ls,us),
      width_exact=right-left,width_decomposition=dict(numerical=numerical,sampling_variance=variance_term,finite_support=support_term),
      sign='positive' if left>0 else 'negative' if right<0 else 'unresolved',
      paired_width_target_passed=right-left<=MARGIN,equivalence_at_margin=(-MARGIN<left and right<MARGIN),
      first_minus_second_noninferior=right<MARGIN,support=support)

def infer(arrays):
    answer={}
    for index,estimator in enumerate(('cash','conditional')):
        values={}
        for name in NAMES:values[name]=interval(arrays[name][2*index],arrays[name][2*index+1],(F(0),H))
        pairs={}
        for i,j in itertools.combinations(NAMES,2):
            a=arrays[i];b=arrays[j]
            pairs[i+'-minus-'+j]=interval(a[2*index]-b[2*index+1],a[2*index+1]-b[2*index],(-H,H))
        answer[estimator]=dict(costs=values,contrasts=pairs)
    return answer

def execute():
    freeze=verify_freeze();folder=R/'results77'
    if folder.exists():raise FileExistsError('Scientific attempt already exists; preserve it and use a new freeze for any correction')
    folder.mkdir();begin=time.perf_counter();before=environment();actions,meta=controllers()
    paths=np.random.Generator(np.random.PCG64(SEED)).integers(0,1<<BITS,size=(N,4),dtype=np.uint64)
    np.savez_compressed(folder/'bins.npz',bins=paths);arrays={};work={}
    for name in NAMES:
        print('Complete original-law evaluation:',name,flush=True);start=time.perf_counter()
        arrays[name],work[name]=enclose(paths,actions[name]);np.savez_compressed(folder/(name+'.npz'),endpoints=arrays[name])
        work[name]['seconds_through_output']=time.perf_counter()-start
        work[name]['endpoint_sha256']=sha(folder/(name+'.npz'))
    start=time.perf_counter();inference=infer(arrays);inference_seconds=time.perf_counter()-start
    report=dict(status='passed',source_freeze_sha256=sha(R/'SOURCE_FREEZE77.json'),source_commit=freeze['source_commit'],
        seed=SEED,rows=N,bin_bits=BITS,estimator_names=['cash','conditional'],policies=list(NAMES),
        new_independent_simulation_rows=N,estimands=30,log_upper=LOG,family_failure_upper='120*exp(-10) < 1/100',
        support=H,margin=MARGIN,paired_total_width_target=MARGIN,controller_metadata=meta,
        work=work,statistical_inference_seconds=inference_seconds,inference=inference,
        bins_sha256=sha(folder/'bins.npz'),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        environment_before=before,environment_after=environment(),seconds_before_summary=time.perf_counter()-begin,
        scientific_scope='Original R73 constructed policies, original continuous law, both complete interval implementations and all fixed paired contrasts; no refitting, no recursive optimal-value queries, no claim of neural superiority over unexecuted comparators')
    save(folder/'summary.json',report)
    save(folder/'clock.json',dict(seconds_through_summary=time.perf_counter()-begin,summary_sha256=sha(folder/'summary.json')))
    print(json.dumps(encode(dict(status='passed',rows=N,conditional_contrasts={k:{p:v[p] for p in ('interval','sign','paired_width_target_passed','equivalence_at_margin')} for k,v in inference['conditional']['contrasts'].items()},seconds=time.perf_counter()-begin)),indent=2),flush=True)

def replay():
    start=time.perf_counter();verify_freeze();folder=R/'results77';report=read(folder/'summary.json')
    if sha(folder/'summary.json')!=read(folder/'clock.json')['summary_sha256']:raise AssertionError('Summary identity')
    if sha(folder/'bins.npz')!=report['bins_sha256']:raise AssertionError('Sample bins identity')
    paths=np.load(folder/'bins.npz')['bins'];actions,meta=controllers();arrays={}
    if paths.shape!=(N,4):raise AssertionError('Sample count')
    expected=np.random.Generator(np.random.PCG64(SEED)).integers(0,1<<BITS,size=(N,4),dtype=np.uint64)
    if not np.array_equal(paths,expected):raise AssertionError('Predetermined stream')
    if encode(meta)!=report['controller_metadata']:raise AssertionError('Controller metadata')
    for name in NAMES:
        path=folder/(name+'.npz')
        if sha(path)!=report['work'][name]['endpoint_sha256']:raise AssertionError('Cost archive identity')
        arrays[name]=np.load(path)['endpoints'];fresh,record=enclose(paths,actions[name])
        if not np.array_equal(fresh,arrays[name]):raise AssertionError('Full-bin replay disagreement: '+name)
        for key in ('complete_interval_trajectories_per_implementation','exact_midpoint_checks','binary64_acquisition_ambiguities','integer_acquisition_ambiguities','original_optimal_value_queries'):
            if record[key]!=report['work'][name][key]:raise AssertionError('Work ledger mismatch: '+key)
    if encode(infer(arrays))!=report['inference']:raise AssertionError('Exact confidence interval replay')
    result=dict(status='passed',full_bin_trajectories_per_implementation=N*len(NAMES),
        exact_midpoint_trajectories=512*len(NAMES),recomputed_estimands=30,
        scientific_services_retimed=False,new_simulation_rows=0,seconds=time.perf_counter()-start,
        original_summary_sha256=sha(folder/'summary.json'),scope='Both arithmetic implementations re-evaluate every NEW bin and acquired action; not a replay of the historical large vector recursion')
    save(R/'audit/REPLAY77.json',result);print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--execute',action='store_true');group.add_argument('--replay',action='store_true')
    args=parser.parse_args();execute() if args.execute else replay()
