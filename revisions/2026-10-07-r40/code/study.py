"""Execute the frozen protocol; retain every refinement and precision failure.

These are post-training verification services, not retimed R38 training.
"""
from pathlib import Path
import os,sys,json,hashlib,time,subprocess,platform
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import numpy as np
import neural_chain as nc
import deployment as dep
import nonlinear as nl
R=Path(__file__).resolve().parents[1]
def save(path,obj):
 if path.exists():raise FileExistsError(path)
 raw=(json.dumps(obj,default=nc.encode,sort_keys=True,separators=(',',':'))+'\n').encode()
 with path.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 return hashlib.sha256(raw).hexdigest()
def main():
 affinity=None
 if hasattr(os,'sched_getaffinity'):
  affinity=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{affinity})
 (R/'results').mkdir(exist_ok=True)
 if (R/'results/R40_STUDY.json').exists():raise FileExistsError('Never replace completed evidence')
 ledger=[];final=[]
 for price in [1.,4.]:
  for theta in [0.,1.]:
   row,record=nc.load_record(price,theta)
   for N,A in [(256,128),(1024,512),(2048,1024),(4096,2048)]:
    start=time.perf_counter();name=f'neural-{price}-{theta}-{N}.json';out=R/'results'/name
    if out.exists():raise FileExistsError('Use a fresh run, not development records')
    result=nc.certify_chain(record['networks'],price,theta,N,A,record['candidate'])
    result['frozen_source_record']=row['id'];result['source_record_sha256']=row['clock']['record_sha256']
    result['deployment']=dep.apply(result)
    h=save(out,result);elapsed=time.perf_counter()-start
    lr=dict(path='results/'+name,sha256=h,seconds_through_fsync=elapsed,price=price,theta=theta,N=N,A=A,query_target_passed=bool(max(result['statewise_policy_gap_upper'])<=.02))
    ledger.append(lr);print(json.dumps(lr),flush=True)
    if lr['query_target_passed']:break
   start=time.perf_counter();original_risk=nl.risk;nl.risk=nc.small_risk
   try:spline=nl.construct(N=N,A=A,T=4,theta=theta,price=price,batch=32)
   finally:nl.risk=original_risk
   sv=nl.own_value(spline,[.125,.25,.5,.75]);nv=nc.I(result['own_policy_values']['lower'],result['own_policy_values']['upper']);dv=nv-sv
   comparison=dict(price=price,theta=theta,N=N,A=A,conventional_policy=spline,conventional_values=dict(lower=sv.lo,upper=sv.hi),neural_minus_reoptimized_spline=dict(lower=dv.lo,upper=dv.hi),equivalence_margin=.001,conventional_construction_and_query_seconds=time.perf_counter()-start,comparison_scope='Same final verification resolution. Networks already trained; no end-to-end speed comparison inferred.')
   if price==4.:
    idx=json.loads((R/'inputs/INDEX.json').read_text());oldrow=idx[f'nonlinear-capital-1.0-{theta}'];old=json.loads((R/'inputs'/(oldrow['id']+'.json')).read_text())
    stale=nl.own_value(old['candidate'],[.125,.25,.5,.75],price=4.,theta=theta);gain=stale-nv
    comparison['neural_gain_over_old_rule']=dict(lower=gain.lo,upper=gain.hi)
   ch=save(R/'results'/f'comparison-{price}-{theta}.json',comparison)
   final.append(dict(price=price,theta=theta,N=N,A=A,neural_result='results/'+name,comparison_result=f'results/comparison-{price}-{theta}.json',comparison_sha256=ch,global_gap=result['policy_gap_upper'],max_query_gap=float(max(result['statewise_policy_gap_upper'])),deployed_extra=result['deployment']['extra_global_loss_upper'],min_direct_difference=float(min(dv.lo)),max_direct_difference=float(max(dv.hi)),newly_constructed_policy=True))
 subprocess.run([sys.executable,str(R/'code/precision_catalogue.py')],check=True)
 clocks=json.loads((R/'results/precision/INDEX.json').read_text());assert len(clocks)==48
 summary={}
 for m in ['fixed32-cached','fixed64-cached','adaptive-cached','tuned-cached']:
  rows=[x for x in clocks if x['spec']['method']==m]
  summary[m]=dict(services=len(rows),passed=sum(x['certified'] for x in rows),**{k:sum(x[k] for x in rows) for k in ['accepted32','accepted64','rejected32','rejected64']})
 results=dict(protocol_commit='d66fc832e67050518317de6f505bcd2eb98a3158',science_source_commit=os.environ.get('GITHUB_SHA'),run_id=os.environ.get('GITHUB_RUN_ID'),neural_refinements=ledger,final=final,precision=summary,execution=dict(cpu_affinity=affinity,frequency_controlled=False,threads=1,python=platform.python_version(),numpy=np.__version__,new_neural_training_runs=0),clock_scope='New post-training neural verification, policy construction and independent queries. All refinements retained; inherited clocks unchanged.',code_hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'code').glob('*.py')})
 save(R/'results/R40_STUDY.json',results);print(json.dumps(results,indent=2),flush=True)
if __name__=='__main__':main()
