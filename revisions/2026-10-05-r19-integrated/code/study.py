"""Execute the frozen family with actual per-procedure stopping and accounting."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, sys, time, traceback
from pathlib import Path
STARTUP=time.perf_counter()
import numpy as np
import torch
from economy import Economy, tasks, checksum
from intervals import environment_check
from methods import METHODS, STAGES, construct, select
ROOT=Path(__file__).resolve().parents[1]


def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w') as f:
        json.dump(obj,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def verify_freeze():
    manifest=json.loads((ROOT/'protocols/IMPLEMENTATION_FREEZE.json').read_text())
    for name,digest in manifest['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('changed frozen source: '+name)
    environment_check()
    return hashlib.sha256((ROOT/'protocols/IMPLEMENTATION_FREEZE.json').read_bytes()).hexdigest()


def diagnostics(e,method,model,y,t,a,stage):
    """Post-stop mechanism records. Never enter the stopping rule or fitting."""
    with torch.no_grad():
        actual=e.value(y,a,t)
        action_grid=torch.stack([torch.full_like(a,.05),(.05+t[:,3])/2,t[:,3]],1)
        xs=[e.post(y,action_grid[:,j]) for j in range(3)]
        truths=torch.stack([e.future(x).mean(0) for x in xs],1)
        owntruth=e.future(e.post(y,a)).mean(0)
    row=dict(payoff_mean=float(actual.mean()),withdrawal_mean=float(a.mean()),
        charge_mean=float(t[:,2].mean()),charge_resource_cost_mean=float((t[:,2]*a).mean()))
    if method not in ('myopic','shared_actor'):
        with torch.no_grad():
            pred=torch.stack([model(x) for x in xs],1)
            ownpred=model(e.post(y,a))
            err=pred-truths
            qp=pred+torch.stack([e.current(action_grid[:,j],t) for j in range(3)],1)
            qt=truths+torch.stack([e.current(action_grid[:,j],t) for j in range(3)],1)
            chosen=qp.argmax(1);optimal=qt.argmax(1)
            regret=qt.max(1).values-qt[torch.arange(len(y)),chosen]
            binary_pred=(qp[:,2]>=qp[:,0]);binary_true=(qt[:,2]>=qt[:,0])
            binary_regret=torch.abs(qt[:,2]-qt[:,0])*(binary_pred!=binary_true)
        row.update(exogenous_absolute_risk=float((err**2).mean()),
            exogenous_centered_risk=float(((err-err.mean(1,keepdim=True))**2).mean()),
            own_action_absolute_risk=float(((ownpred-owntruth)**2).mean()),
            exogenous_catalogue_regret=float(regret.mean()),
            exogenous_catalogue_misclassification=float((chosen!=optimal).double().mean()),
            binary_decision_regret=float(binary_regret.mean()),
            binary_misclassification=float((binary_pred!=binary_true).double().mean()))
    else:
        row['prediction_risk_status']='not applicable: this procedure returns actions, not a scalar predictor'
    zero=t.clone();zero[:,2]=0
    a0=select(e,method,model,y,zero)
    row['withdrawal_change_from_zero_charge_mean']=float((a-a0).mean())
    row['zero_charge_query_count']=len(y)
    row['diagnostic_scope']='finite stored law and three declared complete streams; float64 descriptive diagnostics, not a population confidence interval or full-control certificate'
    return row


def run_one(d,q,seed,method,out):
    begin=time.perf_counter();stages=[];frozen=verify_freeze()
    inputs=json.loads((ROOT/f'protocols/economy_d{d}.json').read_text());e=Economy(inputs)
    y,t=tasks(q,d,195520+d)
    taskhash=checksum(np.c_[y.numpy(),t.numpy()]);setup=time.perf_counter()-begin
    record=dict(dimension=d,queries=q,stream=seed,method=method,freeze_sha256=frozen,task_sha256=taskhash,
        task_initialization_seconds=setup,stages=stages,status='unresolved',tolerance=1e-4)
    maxstage=1 if method in ('myopic','enumerated') else 2
    for stage in range(maxstage):
        fit_start=time.perf_counter();model,ids=construct(e,method,seed,stage);fit=time.perf_counter()-fit_start
        query_start=time.perf_counter();a=select(e,method,model,y,t);query=time.perf_counter()-query_start
        check_start=time.perf_counter();cert=e.certify(y,a,t);check=time.perf_counter()-check_start
        stage_record=dict(stage=stage+1,cache_ids=ids,fit_and_cache_seconds=fit,query_seconds=query,
            verification_seconds=check,selected_actions=a.tolist(),certificate=cert)
        stages.append(stage_record)
        passed=cert['mean_regret_upper']<=1e-4
        record['status']='certified' if passed else 'unresolved'
        # Every attempted stage, including a failed check, is durably written
        # before the stop clock is read. Final timing metadata is measured and
        # added separately below rather than pretending its own write was free.
        save(out,record)
        record['stop_service_seconds']=time.perf_counter()-begin
        if passed:break
    meta_start=time.perf_counter();save(out,record)
    meta_seconds=time.perf_counter()-meta_start
    record['timing_metadata_write_seconds']=meta_seconds
    record['accounted_service_seconds']=record['stop_service_seconds']+meta_seconds
    record['final_certificate_upper']=cert['mean_regret_upper']
    record['selected_stage']=len(stages)
    # Economic grant is an external utility offset: A0*w*log(1+g).
    upper=np.asarray(cert['regret_upper']);weights=t[:,0].numpy()
    record['external_log_grant_bound_mean']=float(np.expm1(upper/(e.A[0]*weights)).mean())
    diag_start=time.perf_counter()
    record['mechanism']=diagnostics(e,method,model,y,t,a,stage)
    record['post_stop_diagnostics_seconds']=time.perf_counter()-diag_start
    save(out,record)
    return record


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'results/registered')
    parser.add_argument('--cell',nargs=4,metavar=('D','Q','SEED','METHOD'))
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    if (args.out/'RUNNING.json').exists():raise RuntimeError('output already used; preserve prior execution')
    frozen=verify_freeze();start=time.perf_counter()
    env=dict(python=sys.version,numpy=np.__version__,torch=torch.__version__,platform=platform.platform(),
        processor=platform.processor(),threads=torch.get_num_threads(),loaded_service_startup_seconds=start-STARTUP,
        freeze_sha256=frozen,scope='single warm service, separate real executions for every query volume; startup charged once to comparative total, not invented per-method clocks')
    save(args.out/'RUNNING.json',env)
    cells=[(d,q,s,m) for d in [10,50] for q in [1,4,16,64,256,1024] for s in [195501,195502,195503] for m in METHODS]
    if args.cell:
        d,q,s,m=args.cell;cells=[(int(d),int(q),int(s),m)]
    results=[];failures=[]
    for d,q,s,m in cells:
        name=f'd{d}_q{q}_s{s}_{m}.json'
        try:
            r=run_one(d,q,s,m,args.out/name);results.append(r)
            print(d,q,s,m,r['status'],r['final_certificate_upper'],r['accounted_service_seconds'],flush=True)
        except Exception as exc:
            f=dict(dimension=d,queries=q,stream=s,method=m,error=repr(exc),traceback=traceback.format_exc(),status='execution_failure')
            save(args.out/(name+'.failure.json'),f);failures.append(f);print('FAIL',f,flush=True)
    summary=dict(environment=env,records=results,failures=failures,expected_count=len(cells),completed_count=len(results),
        full_comparative_wall_seconds=time.perf_counter()-start+env['loaded_service_startup_seconds'],
        all_streams_retained=True,all_failed_checks_charged=True,retrospective_selection_of_budgets=False)
    save(args.out/'SUMMARY.json',summary)
    print('COMPLETE',len(results),'FAILURES',len(failures),flush=True)
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
