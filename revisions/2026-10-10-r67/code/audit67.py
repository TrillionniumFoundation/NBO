"""Replay all frozen corrected R67 outputs without fitting, resampling or retiming.

Every saved path enclosure is recalculated from the original interval
primitives and deployed actions. Two fixed rows of each path archive also
receive independent rational midpoint-trajectory checks. Every comparison
archive is re-queried with the saved model; the large vector continuation
services are not re-executed. Reproduction is not a proof of interval code.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys,time,statistics,collections
import numpy as np
R=Path(__file__).resolve().parents[1]
S=R
sys.path.insert(0,str(S/'code'))
import science67 as s
k=s.k;q=s.q;I=s.I;B=s.B

def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def need(ok,label):
    if not ok:raise AssertionError(label)
def equal(a,b,label):need(np.array_equal(a,b,equal_nan=True),label)
def save(p,j):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,sort_keys=True,indent=2)+'\n')
def checked(p,d):need(sha(p)==d,'Digest mismatch: '+str(p))

def rational_stage(x,a,terminal=False):
    d=len(x);short=max(F(0),F(1,2)-2*sum(x)/d)
    z=(4 if terminal else 2)*sum((v-F(5,8))**2 for v in x)/d
    z+=sum((x[j]-x[(j+1)%d])**2 for j in range(d))/(4*d)+2*short**2
    if not terminal:
        z+=sum(v*v+4*v**4 for v in a)
        if len(a)==2:z+=a[0]*a[1]/4
    return z

def rational_transition(x,a,z,w=F(0)):
    d=len(x)
    return [F(1,16)+F(9,16)*v+x[(j+1)%d]/8-v*x[(j+1)%d]/16
        +sum((F(1,2) if j%2==h else F(1,4))*ah for h,ah in enumerate(a))
        +(z if j%2==0 else -z)+w for j,v in enumerate(x)]

def rational_rows(spec,trace,randoms,named):
    count=0;den=2**s.BINBITS;T=spec['T'];d=spec['d'];N=spec['N']
    for row in sorted({0,N-1}):
        x=[F(2*int(v)+1,2*den) for v in randoms['initial_index'][row]]
        if named and row<4:x=[[F(0)]*d,[F(1)]*d,[F(1,4)]*d,[F(3,4)]*d][row]
        cost=F(0);complete=True
        for t in range(T):
            a=np.atleast_1d(trace[f't{t}_action'][row])
            if not np.isfinite(a).all():complete=False;break
            obs=[float(F((v*2**s.BITS).__floor__(),2**s.BITS)) for v in x]
            equal(np.asarray(obs),trace[f't{t}_observed'][row],'Rational acquired state')
            aa=[F(float(v)) for v in a]
            need(sum(aa)<=F(1,8)+sum(x)/(8*d),'Rational capacity')
            cost+=B**t*rational_stage(x,aa)
            z=F(2*int(randoms['shock_index'][t,row])+1,32*den)-F(1,32)
            w=F(0) if spec['group']!='vector' else F(2*int(randoms['second_shock_index'][t,row])+1,64*den)-F(1,64)
            x=rational_transition(x,aa,z,w)
        if complete:
            cost+=B**T*rational_stage(x,[],True)
            need(F(float(trace['cost_lo'][row]))<=cost<=F(float(trace['cost_hi'][row])),'Rational total inside path enclosure')
            count+=1
    return count

class StoredActions:
    def __init__(self,trace,T):self.trace=trace;self.T=T;self.decisions=0
    def solve(self,x,r,tol):
        t=self.T-r;observed=self.trace[f't{t}_observed'];valid=np.isfinite(observed).all(axis=1)
        equal(x,observed[valid],'Full acquired-state replay')
        a=self.trace[f't{t}_action'][valid];lo=self.trace[f't{t}_lower'][valid];hi=self.trace[f't{t}_upper'][valid];gap=self.trace[f't{t}_gap'][valid]
        need(np.isfinite(a).all() and np.isfinite(lo).all() and np.isfinite(hi).all(),'Finite deployed certificate')
        need((a>=0).all() and np.all(a*2**32==np.floor(a*2**32)),'Downward action lattice')
        need((lo<=hi).all() and (gap<=tol).all(),'Ordered accurate endpoint')
        equal(gap,(I.point(hi)-I.point(lo)).hi,'Directed outward gap')
        self.decisions+=len(x)
        return dict(action=a,lower=lo,upper=hi,gap=gap)

def validate_path(spec,trace,randoms,initial,account=None,named=False):
    oracle=StoredActions(trace,spec['T'])
    new,acc=s.paths(oracle,I(initial.lo.copy(),initial.hi.copy()),randoms,spec['T'],spec['target'],vector=spec['group']=='vector')
    for key,v in new.items():equal(v,trace[key],'Full continuous-bin path replay '+key)
    if account is not None:need(acc==account,'Path account replay')
    return oracle.decisions,rational_rows(spec,trace,randoms,named)

def progress(trace,tol,counts,T):
    p=trace['progress'];z=trace['screens'];need(p.ndim==2 and p.shape[1]==13,'Progress schema');need(z.ndim==2 and z.shape[1]==8,'Screen schema')
    need(np.isfinite(p).all() and np.isfinite(z).all(),'Finite progress records')
    need(len(p)==counts['refinements'] and len(z)==counts['screen_attempts'],'Progress completeness')
    need(int(p[:,10].sum())==counts['routed_queries'],'Route count')
    need(int(z[:,7].sum())==counts['screen_returns'],'Screen returns')
    equal(p[:,8],p[:,5]-p[:,7],'Upper witness progress identity')
    equal(p[:,9],p[:,6]-p[:,4],'Lower certificate progress identity')
    need((p[:,6]>=p[:,4]).all() and (p[:,7]<=p[:,5]).all(),'Monotone endpoint progress')
    need((p[:,11]<=p[:,12]).all(),'Query endpoint order')
    equal(z[:,6],(I.point(z[:,4])-I.point(z[:,5])).hi,'Prequery score identity')
    # Every deeper query has no larger local tolerance. A true flag must at
    # least satisfy the root tolerance; exact child tolerance is re-queried.
    need(np.all(z[z[:,7]==1,6]<=tol),'Valid recorded closure')
    route=p[:,10]==1
    return dict(refinements=len(p),routed=int(route.sum()),zero_progress=int(np.sum((p[:,8]==0)&(p[:,9]==0))),
        routed_zero_progress=int(np.sum(route&(p[:,8]==0)&(p[:,9]==0))),
        upper_only=int(np.sum((p[:,8]>0)&(p[:,9]==0))),lower_only=int(np.sum((p[:,8]==0)&(p[:,9]>0))),
        both_progress=int(np.sum((p[:,8]>0)&(p[:,9]>0))),
        routed_upper_improvement=float(p[route,8].sum()),routed_lower_improvement=float(p[route,9].sum()),
        screen_attempts=len(z),screen_returns=int(z[:,7].sum()),
        prequery_routed_scope='All recursive comparisons; widths checked at original child tolerance by saved-model replay.')

def requery_comparison(spec,trace,randoms,initial,model,summary):
    oracle=k.Oracle(spec['kind'],k.load_models(spec['kind'],model['models']),record=True)
    new,acc=s.paths(oracle,I(initial.lo.copy(),initial.hi.copy()),randoms,spec['T'],spec['target'])
    for key,v in new.items():equal(v,trace[key],'Saved-model policy replay '+key)
    for key,v in s.packed_diagnostics(oracle).items():equal(v,trace[key],'Saved-model diagnostic replay '+key)
    for key,v in oracle.counts.items():
        if key!='prediction_seconds':need(v==summary['counts'][key],'Logical query count '+key)
    need(acc==summary['account'],'Saved-model account')


def main():
    start=time.perf_counter();binding=s.verify();execution=read(S/'audit/EXECUTION67.json');catalogue=s.specs()
    need(len(catalogue)==212 and [x['spec'] for x in execution['services']]==catalogue,'Full prospective catalogue')
    need(execution['source_freeze_sha256']==binding,'Execution source identity')
    summaries=[];decisions=ratrows=archives=queries=0;inference=[];records=[];seen={};modelkeys={};diagnostics={}
    for spec,receipt in zip(catalogue,execution['services']):
        out=S/'results67'/spec['key'];need(read(out/'receipt.json')==receipt,'Parent receipt identity')
        checked(S/'audit'/('service-'+spec['key']+'.log'),receipt['log_sha256'])
        need(receipt['process_wall_seconds']>=0 and receipt['source_freeze_sha256']==binding,'Receipt boundary')
        if receipt['status']!='returned':records.append(receipt);continue
        checked(out/'summary.json',receipt['summary_sha256']);checked(out/'clock.json',receipt['clock_sha256'])
        summary=read(out/'summary.json');clock=read(out/'clock.json')
        need(clock['summary_sha256']==receipt['summary_sha256'] and summary['spec']==spec,'Summary identity')
        need(summary['source_freeze_sha256']==binding and summary['status']=='returned','Summary source')
        row=dict(spec=spec,complete_seconds=receipt['process_wall_seconds'],peak_rss_kib=summary['peak_rss_kib'])
        T,d,N=spec['T'],spec['d'],spec['N'];g=spec['group'];model=None
        if g in ('comparison','reuse'):
            checked(out/'model.json',summary['model_sha256']);model=read(out/'model.json')
            row.update(training=summary['training'],model_sha256=summary['model_sha256'])
            key=(d,T,spec['kind'],spec['seed'])
            mm=model['models'];canonical=json.dumps(mm,sort_keys=True)
            if key in modelkeys:need(canonical==modelkeys[key],'Matched saved-model identity')
            modelkeys[key]=canonical
        if g in ('comparison','vector'):
            checked(out/'trace.npz',summary['trace_sha256'])
            with np.load(out/'trace.npz') as zz:trace={key:zz[key] for key in zz.files}
            randoms,initial=s.workload(d,T,N,(661000+d*101+T) if g=='comparison' else (664000+d*1009+T),vector=g=='vector')
            for key,v in randoms.items():equal(v,trace[key],'Frozen diagnostic stream')
            n,m=validate_path(spec,trace,randoms,initial,summary['account'],named=True);decisions+=n;ratrows+=m;archives+=1
            row.update(counts=summary['counts'],account=summary['account'])
            if g=='comparison':
                diag=progress(trace,summary['account']['local_tolerance'],summary['counts'],T);row['diagnostics']=diag
                ident=(d,T,spec['kind'],spec['seed']);h=summary['trace_sha256']
                if ident in seen:need(seen[ident]==h,'Clock repeats are identical traces')
                else:
                    requery_comparison(spec,trace,randoms,initial,model,summary);queries+=1;seen[ident]=h
            need(summary['counts']['stored_state_nodes']==0,'No stored state lattice')
        elif g=='reuse':
            need(len(summary['blocks'])==s.BLOCKS,'Full reuse block sequence');last=summary['initial_service_seconds']
            row.update(initial_service_seconds=last,blocks=[])
            for i,block in enumerate(summary['blocks']):
                saved=read(out/f'block{i:02d}.json')
                need({key:val for key,val in block.items() if key not in ('seconds_through_durable_record','cumulative_seconds')}==saved,'Durable block identity')
                need(block['block']==i and block['identity_valid']==(i!=7),'Declared stale identity')
                need(block['used_kind']==('adaptive' if i==7 else spec['kind']),'Failed reuse fallback')
                need(block['cumulative_seconds']==last+block['seconds_through_durable_record'],'Complete prefix accounting')
                last=block['cumulative_seconds'];checked(out/f'block{i:02d}.npz',block['trace_sha256'])
                with np.load(out/f'block{i:02d}.npz') as zz:trace={key:zz[key] for key in zz.files}
                randoms,initial=s.workload(d,T,N,662000+d*1009+T*97+i,continuous=True)
                for key,v in randoms.items():equal(v,trace[key],'Prospective reuse stream')
                n,m=validate_path(spec,trace,randoms,initial,block['account']);decisions+=n;ratrows+=m;archives+=1
                row['blocks'].append(block)
        else:
            checked(out/'random-inputs.npz',summary['random_inputs_sha256']);checked(out/'path-endpoints.npz',summary['raw_endpoint_sha256'])
            randoms,initial=s.workload(d,T,N,663000+d*1009+T,continuous=True)
            with np.load(out/'random-inputs.npz') as zz:
                for key,v in randoms.items():equal(v,zz[key],'Fresh inference stream')
            all_lo=[];all_hi=[]
            for arm in summary['arms']:
                kind=arm['kind'];checked(out/(kind+'-model.json'),arm['model_sha256']);checked(out/(kind+'-paths.npz'),arm['trace_sha256'])
                model=read(out/(kind+'-model.json'));need(json.dumps(model,sort_keys=True)==modelkeys[(d,T,kind,spec['seed'] if kind in k.LEARNED else 0)],'Actual inference model identity')
                with np.load(out/(kind+'-paths.npz')) as zz:trace={key:zz[key] for key in zz.files}
                # Numerical arithmetic is elementwise; the archived inference
                # rows were processed in 512-row batches. Replay those batches.
                for first in range(0,N,512):
                    end=min(N,first+512);rr={key:(v[first:end] if key=='initial_index' else v[:,first:end]) for key,v in randoms.items()}
                    tr={key:v[first:end] for key,v in trace.items()}
                    n,m=validate_path({**spec,'N':end-first},tr,rr,I(initial.lo[first:end],initial.hi[first:end]));decisions+=n;ratrows+=m
                archives+=1;all_lo.append(trace['cost_lo']);all_hi.append(trace['cost_hi'])
            lo=np.maximum(0,np.stack(all_lo));hi=np.minimum(q.up(s.support(T)),np.stack(all_hi));H=F(q.up(s.support(T)))
            with np.load(out/'path-endpoints.npz') as zz:equal(lo,zz['lower'],'Inference endpoint lower');equal(hi,zz['upper'],'Inference endpoint upper')
            names=[arm['kind'] for arm in summary['arms']]
            for j,kind in enumerate(names):need(s.infer_interval(lo[j],hi[j],H)==summary['absolute_cost'][kind],'Marginal cost interval')
            from itertools import combinations
            for a,b in combinations(range(4),2):
                delta=I(lo[a],hi[a])-I(lo[b],hi[b]);actual=s.infer_interval(np.maximum(-float(H),delta.lo),np.minimum(float(H),delta.hi),2*H)
                need(actual==summary['contrasts'][names[a]+'-minus-'+names[b]],'Paired cost interval')
            row.update(absolute_cost=summary['absolute_cost'],contrasts=summary['contrasts'],arms=summary['arms'],continuous_law_observations=N,
                       raw_mean_differences={names[a]+'-minus-'+names[b]:float((lo[a]-lo[b]).mean()) for a,b in combinations(range(4),2)})
            inference.append(row)
        summaries.append(row)
    need(len(summaries)==execution['returned'],'Returned count');need(len(records)==execution['failed']+execution['timed_out'],'Failure retention')
    need(sum(x['complete_seconds'] for x in summaries)+sum(x['process_wall_seconds'] for x in records)==execution['total_process_seconds'],'All complete process work')
    result=dict(status='passed',review_commit='d548a97f461160296239ed6a973d4a91ef9d1fad',reviewed_commit='34a5ce17dc3ac4681b6d004eca00637f28104e28',
        scientific_source_freeze_commit='e60c552e5b1fc5bcdac05d90151b0b595ddd7560',source_freeze_sha256=binding,
        catalogue_services=len(catalogue),returned=len(summaries),failed=execution['failed'],timed_out=execution['timed_out'],
        complete_process_seconds=execution['total_process_seconds'],path_archives_replayed=archives,implemented_decisions_replayed=decisions,
        independent_rational_midpoint_paths=ratrows,distinct_comparison_services_requeried=queries,
        independent_continuous_law_rows=sum(z['continuous_law_observations'] for z in inference),new_independent_rows_in_this_replay=0,new_training_runs=0,
        summaries=summaries,failures=records,replay_seconds=time.perf_counter()-start,
        verification_scope='Every frozen record and interval path; all 90 distinct comparison services re-queried from saved models; two fixed midpoint paths per archive/batch independently checked with rational primitives. Reuse and inference endpoint queries and the vector continuation trees are not independently reintegrated.',
        statistical_scope='16,384 distinct common-path IID-model rows across two tasks, not multiplied by methods or clock repeats. Fixed seeds give reproducibility, not a theorem of pseudorandom independence.')
    save(R/'audit/RESULT_AUDIT67.json',result)
    print(json.dumps({key:val for key,val in result.items() if key not in ('summaries','failures')},indent=2))
if __name__=='__main__':main()
