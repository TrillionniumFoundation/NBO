"""Full replay of frozen R63/R64 services, not retraining or retiming.

Trajectory checking uses independently written rational economic primitives.
Re-querying stored observations checks the original numerical implementation;
it is a reproducibility check, not an independent proof of every enclosure.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys,time,statistics
import numpy as np
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R.parent/'2026-10-10-r64/code'))
import science64 as s64
s63=s64.old;q=s64.q;g=s64.g

def read(p):return json.loads(Path(p).read_text())
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def require(condition,message):
    if not condition:raise AssertionError(message)
def same(a,b,message):require(np.array_equal(a,b),message)
def stage(x,a,terminal=False):
    d=len(x);short=max(F(0),F(1,2)-2*sum(x)/d)
    z=(4 if terminal else 2)*sum((v-F(5,8))**2 for v in x)/d
    z+=sum((x[j]-x[(j+1)%d])**2 for j in range(d))/(4*d)+2*short**2
    return z if terminal else z+a*a+4*a**4

def transition(x,a,z):
    return [F(1,16)+F(9,16)*v+x[(j+1)%len(x)]/8-v*x[(j+1)%len(x)]/16
            +(F(1,2) if j%2==0 else F(1,4))*a+(z if j%2==0 else -z)
            for j,v in enumerate(x)]

def validate_trace(spec,summary,trace,costs):
    d,T,N=spec['d'],spec['T'],spec['N'];tol=F(summary['local_tolerance'])
    require(F(summary['uniform_policy_gap_upper'])<=F(spec['target']),'Uniform target')
    require(F(summary['uniform_policy_gap_upper'])>=sum((F(15,16)**t*(tol+F(8,2**40)+F(15,16)*F(297,16*2**40)+F(27,2**40)) for t in range(T)),F(0)),'Uniform rounding direction')
    state=[[F(int(v),2**20) for v in row] for row in trace['initial']];total=[F(0)]*N
    require(trace['initial'].shape==(N,d) and trace['shocks'].shape==(T,N),'Workload shapes')
    require(np.all((trace['initial']>=0)&(trace['initial']<=2**20)),'Initial support')
    require(np.all((trace['shocks']>=-2**15)&(trace['shocks']<2**15)),'Shock support')
    for t in range(T):
        obs=np.array([[float(F((v*2**40).__floor__(),2**40)) for v in row] for row in state])
        same(obs,trace[f't{t}_observed'],'Acquisition identity')
        for i in range(N):
            a=F(float(trace[f't{t}_action'][i]));L=F(float(trace[f't{t}_lower'][i]));U=F(float(trace[f't{t}_upper'][i]));gap=F(float(trace[f't{t}_gap'][i]))
            require(a*2**32==(a*2**32).__floor__(),'Action quantum')
            require(0<=a<=F(1,8)+sum(state[i])/(8*d),'True-state feasibility')
            require(0<=U-L<=gap<=tol,'Local bracket contract')
            total[i]+=F(15,16)**t*stage(state[i],a)
            state[i]=transition(state[i],a,F(int(trace['shocks'][t,i]),2**20))
            require(all(0<=v<=1 for v in state[i]),'Invariant domain')
    for i in range(N):total[i]+=F(15,16)**T*stage(state[i],F(0),True)
    require(list(map(str,total))==costs['cost'],'Exact path costs')
    require(str(sum(total)/N)==costs['mean'],'Exact workload mean')
    require(float(sum(total)/N)==summary['mean_workload_cost'],'Recorded workload mean')
    return N*T

def load_models(path,kind):
    raw=read(path)
    if kind=='relu':return {int(r):(np.array(v[0]),np.array(v[1]),np.array(v[2]),float(v[3])) for r,v in raw.items()}
    return {int(r):np.array(v) for r,v in raw.items()}

def cohort(number,requery=True):
    s=s64 if number==64 else s63;root=s.R;binding=s.verify();execution=read(root/f'audit/EXECUTION{number}.json')
    specs=s.catalogue();keys={x['key'] for x in specs}
    actual={p.name for p in (root/f'results{number}').iterdir() if p.is_dir()}
    require(keys==actual,'Complete prespecified catalogue')
    require(execution['service_count']==len(specs),'Execution service count')
    results=[];decisions=0;requeried=0;validated=set();numerical={}
    for spec in specs:
        p=root/f'results{number}'/spec['key'];summary=read(p/'summary.json');receipt=read(p/'process-receipt.json');clock=read(p/'clock.json')
        require(summary['spec']==receipt['spec']==spec,'Service request identity')
        require(summary['source_freeze_sha256']==receipt['source_freeze_sha256']==binding,'Source binding')
        require(digest(p/'summary.json')==receipt['summary_sha256']==clock['summary_sha256'],'Summary identity')
        require(digest(p/'clock.json')==receipt['clock_sha256'],'Clock identity')
        for field,file in [('trace_sha256','trace.npz'),('models_sha256','models.json'),('exact_costs_sha256','exact-costs.json')]:require(digest(p/file)==summary[field],field)
        require(summary['status']=='returned','Return status')
        require(receipt['process_wall_seconds']>0 and len(summary['affinity'])==1,'Timing or affinity')
        kind=spec['mode'].split('-')[0]
        oracle=(q.Oracle if number==63 or spec['mode'].endswith('-insert') else g.Oracle)(kind,load_models(p/'models.json',kind))
        with np.load(p/'trace.npz') as trace:
            identity=(summary['trace_sha256'],summary['models_sha256'],summary['local_tolerance'],spec['mode'])
            if identity not in validated:
                validate_trace(spec,summary,trace,read(p/'exact-costs.json'));validated.add(identity)
            decisions+=spec['N']*spec['T']
            if requery and identity not in numerical:
                for t in range(spec['T']):
                    v=oracle.solve(trace[f't{t}_observed'],spec['T']-t,summary['local_tolerance'])
                    for name in ('action','lower','upper','gap','probes'):same(v[name],trace[f't{t}_{name}'],'Numerical replay '+spec['key']+' '+name)
                    requeried+=spec['N']
                require(oracle.counts==summary['verification_counts'],'Complete query counts '+spec['key'])
                numerical[identity]=dict(oracle.counts)
            elif requery:
                require(numerical[identity]==summary['verification_counts'],'Identical-trace counts')
        print('verified',number,spec['key'],flush=True)
        fit=summary.get('training')
        results.append(dict(**spec,wall=receipt['process_wall_seconds'],deployment=summary['deployment_seconds'],
            uniform_gap=summary['uniform_policy_gap_upper'],local_tolerance=summary['local_tolerance'],
            counts=summary['verification_counts'],training_counts=summary['training_work'],
            training_seconds=fit['seconds'] if fit else 0,fit_warnings=sum(len(x['warnings']) for x in fit['dates']) if fit else 0,
            peak_rss_kib=summary['peak_rss_kib'],workload_mean=summary['mean_workload_cost'],
            model_sha256=summary['models_sha256'],trace_sha256=summary['trace_sha256']))
    require(abs(sum(x['wall'] for x in results)-execution['total_process_seconds'])<1e-9,'Complete process sum')
    pairs=0
    for a in results:
        if a['repeat']!=0:continue
        b=next(x for x in results if all(x[k]==a[k] for k in ('d','T','target','mode','seed')) and x['repeat']==1)
        require(a['model_sha256']==b['model_sha256'] and a['trace_sha256']==b['trace_sha256'],'Repeat identity')
        pairs+=1
    return dict(cohort=number,services=len(results),decisions=decisions,requeried=requeried,repeat_identity_pairs=pairs,
        source_freeze_sha256=binding,rows=results,process_seconds=execution['total_process_seconds'])

def summarize(a,b):
    rows=b['rows'];matches=0;groups=[]
    for d,T,N in s64.TASKS:
        for target in s64.TARGETS:
            group=[x for x in rows if x['d']==d and x['T']==T and x['target']==target]
            methods={}
            for mode in s64.MODES:
                v=[x for x in group if x['mode']==mode]
                methods[mode]=dict(services=len(v),median_wall=statistics.median(x['wall'] for x in v),
                    min_wall=min(x['wall'] for x in v),max_wall=max(x['wall'] for x in v),
                    min_queries=min(x['counts']['q_queries'] for x in v),max_queries=max(x['counts']['q_queries'] for x in v),
                    median_queries=statistics.median(x['counts']['q_queries'] for x in v),
                    max_rss_kib=max(x['peak_rss_kib'] for x in v))
            for kind in ('relu','quadratic'):
                for seed in s64.SEEDS:
                    for rep in (0,1):
                        v=[x for x in group if x['mode'].startswith(kind+'-') and x['seed']==seed and x['repeat']==rep]
                        require(len(v)==2 and v[0]['model_sha256']==v[1]['model_sha256'],'Matched insert/route model')
                        matches+=1
            winner=min(methods,key=lambda k:methods[k]['median_wall'])
            groups.append(dict(d=d,T=T,N=N,target=target,methods=methods,median_wall_winner=winner))
    return dict(groups=groups,matched_model_pairs=matches,
        returned_services=a['services']+b['services'],checked_policy_decisions=a['decisions']+b['decisions'],
        no_stored_state_grid=all(x['counts']['stored_state_nodes']==0 for c in (a,b) for x in c['rows']),
        rational_fallbacks=sum(x['counts']['rational_fallbacks'] for c in (a,b) for x in c['rows']),
        fit_warning_count=sum(x['fit_warnings'] for c in (a,b) for x in c['rows']))

def main():
    start=time.perf_counter();a=cohort(63);b=cohort(64);summary=summarize(a,b)
    save(R/'audit/RESULT_AUDIT65.json',dict(status='passed',R63=a,R64=b,summary=summary,
        new_training_runs=0,new_continuous_law_observations=0,seconds=time.perf_counter()-start,
        scope='Complete frozen-record replay, independently coded rational trajectories and re-query of each distinct saved observation; identical repetitions checked by source/model/trace/request bindings; no training, original-service retiming, or formal proof-checker claim.'))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
