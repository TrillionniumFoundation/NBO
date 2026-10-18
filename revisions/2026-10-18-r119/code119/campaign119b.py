"""Separately frozen, post-phase-A algorithm development experiment.

The original source and all phase-A outputs remain immutable. All phase-B
acquisition, controls, reference intervals and clocks execute afresh. Formatting
and source review are suspended during the seven local timing subprocesses.
"""
from __future__ import annotations
from pathlib import Path
from itertools import combinations
import os,sys,json,time,subprocess,traceback,resource,hashlib
import numpy as np
import campaign119 as retained
import budgeted_tail119 as budgeted
from campaign119 import base,kern,econ,q,I
ROOT=Path(__file__).resolve().parents[1]
LEVELS=(.5,.75)
SERVICES=('compiled','geometric','active-tail','masked-tail','budgeted-tail')
ORIGINAL_EXECUTE=retained.execute
ORIGINAL_SOURCE=retained.source


def source():
    frozen=json.loads((ROOT/'SOURCE_FREEZE119B.json').read_text())
    commit=os.environ.get('NBO_SOURCE119','')
    if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise RuntimeError('Actual prospective phase-B commit required')
    repo=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip())
    prefix=str(ROOT.relative_to(repo))+'/'
    for name,sha in frozen['files'].items():
        if base.digest(ROOT/name)!=sha: raise RuntimeError('Phase-B source content differs: '+name)
    for name in list(frozen['files'])+['SOURCE_FREEZE119B.json']:
        data=subprocess.check_output(['git','show',commit+':'+prefix+name],cwd=repo)
        if hashlib.sha256(data).hexdigest()!=base.digest(ROOT/name):
            raise RuntimeError('Actual committed phase-B source differs: '+name)
    return dict(executable_protocol_commit=commit,phase='R119-B',
        designed_after_phase_A=True,phase_A_commit='1f33c2667e0dff89699c6d6a01d03eacfecf3f4e',
        protocol_sha256=base.digest(ROOT/'PROTOCOL119B.md'),manifest_sha256=base.digest(ROOT/'SOURCE_FREEZE119B.json'),
        verified_committed_files=len(frozen['files'])+1,unchanged_first_stage_algorithms=ORIGINAL_SOURCE(),
        population_inference=False)


def execute(x,alpha,model,service):
    if service in ('compiled','geometric','active-tail'):
        return ORIGINAL_EXECUTE(x,alpha,model,service)
    started=time.perf_counter()
    if service=='budgeted-tail': data=budgeted.service(x,alpha,model)
    elif service=='masked-tail': data=budgeted.masked_service(x,alpha,model)
    else: raise ValueError(service)
    for row in data['rows']:
        row['first_attempt_rejected']=not(row['first_loss']<=1/256 and row['first_width']<=1/8192)
        row['proposal_repaired']=row['first_rejected']
        row['returned_action_changed']=row['action']!=row['proposed']
    data['algorithm_seconds']=data['seconds']; data['seconds']=time.perf_counter()-started
    data['raw_first_rejected_means']='128-bin gate required conventional repair'
    data['tail_schedule']=[2,4] if service=='budgeted-tail' else [2,4,8,16,32,64]
    return data


# Reuse only the transparent acquisition/catalogue/file adapters. Numerical
# functions and every retained source byte are unchanged; the new routing is
# itself included in the prospective phase-B freeze.
retained.SERVICES=SERVICES
retained.source=source
retained.execute=execute


def reference(out):
    """Independent risk partition; full original policy and optimum brackets."""
    xgrid = base.rep.grid(12); all_records = []
    for i, alpha in enumerate(LEVELS):
        before = econ.COUNTS.copy(); started = time.perf_counter()
        policies = {}
        for arm in base.rep.ARMS:
            for service in SERVICES:
                rows = json.loads((out/'catalogue'/f'{i}-{arm}-{service}.json').read_text())['rows']
                policies[arm + '/' + service] = rows
        unique = []
        keys = {}
        for j in range(len(xgrid)):
            actions = sorted(set(rows[j]['action'] for rows in policies.values()))
            for action in actions:
                keys[(j, action)] = len(unique)
                unique.append(dict(row=j, state=xgrid[j].tolist(), action=action))
        for start in range(0, len(unique), 32):
            batch = unique[start:start+32]
            x = np.array([r['state'] for r in batch]); a = np.array([r['action'] for r in batch])
            batch_before=econ.COUNTS.copy(); batch_started=time.perf_counter()
            try:
                with kern.backend(True):
                    rec = q.certificate(x, a, alpha, 1024)
            except BaseException:
                base.dump(out/'reference'/f'{i}-FAILED-{start}.json',dict(index=i,alpha=alpha,
                    batch=batch,exception=traceback.format_exc(),counts=base.counter_delta(batch_before),
                    seconds=time.perf_counter()-batch_started))
                raise
            for k, row in enumerate(batch):
                row.update({v: float(rec[v][k]) for v in base.KEYS})
            base.dump(out/'reference'/f'{i}-BATCH-{start}.json',dict(index=i,alpha=alpha,
                start=start,rows=batch,counts=base.counter_delta(batch_before),
                seconds=time.perf_counter()-batch_started))
        states = []
        for j in range(len(xgrid)):
            refs = [r for r in unique if r['row'] == j]
            optimum_lower = max(r['optimum_lower'] for r in refs)
            optimum_upper = min(r['upper'] for r in refs)
            if optimum_lower > optimum_upper:
                raise ArithmeticError('Contradictory original-optimum reference')
            policy_rows = []
            for name, rows in policies.items():
                ref = unique[keys[(j, rows[j]['action'])]]
                policy_rows.append(dict(policy=name, reference_index=keys[(j, rows[j]['action'])],
                    action=ref['action'], lower=ref['lower'], upper=ref['upper'],
                    regret_lower=float(max(0, (I(ref['lower'])-I(optimum_upper)).lo)),
                    regret_upper=float((I(ref['upper'])-I(optimum_lower)).hi),
                    action_distance_upper=float(econ.up(np.sqrt((I(ref['upper'])-I(optimum_lower)).hi)))))
            contrasts = []
            for arm in base.rep.ARMS:
                for control, treatment in tuple(combinations(SERVICES,2)):
                    a = policies[arm+'/'+control][j]['action']
                    b = policies[arm+'/'+treatment][j]['action']
                    ra, rb = unique[keys[(j,a)]], unique[keys[(j,b)]]
                    contrast = I(0) if a == b else I(rb['lower'],rb['upper'])-I(ra['lower'],ra['upper'])
                    contrasts.append(dict(arm=arm, control=control, treatment=treatment,
                        identical_policy=a==b, lower=float(contrast.lo), upper=float(contrast.hi),
                        strictly_improved=bool(contrast.hi < 0), strictly_worse=bool(contrast.lo > 0)))
            states.append(dict(row=j, state=xgrid[j].tolist(), optimum_lower=optimum_lower,
                optimum_upper=optimum_upper, policies=policy_rows, contrasts=contrasts))
        all_records.append(dict(index=i, alpha=alpha, bins=1024, unique_policy_queries=len(unique),
            total_policy_records=144*len(policies), unique=unique, states=states,
            seconds=time.perf_counter()-started, counts=base.counter_delta(before)))
        print('REFERENCE', i, len(unique), round(all_records[-1]['seconds'], 4), flush=True)
    base.dump(out/'REFERENCE119.json', dict(source=source(), records=all_records,
        paid_benchmark_work=True, original_policy_bounds=True, exact_optimal_policy=False,
        risk_partition_independent_of_active_tail=True, shares_verified_terminal_compiler=True))



def timing_one(out,repeat):
    marker=out/'timing'/f'START-{repeat}.json';marker.parent.mkdir(parents=True,exist_ok=True)
    with marker.open('x') as stream:
        json.dump(dict(repeat=repeat,started_unix=time.time(),phase='R119-B'),stream)
    x=base.rep.grid(12)[:32];entries=[];loads=[];started=time.perf_counter()
    for i,alpha in enumerate(LEVELS):
        models,loading=retained.load_models(out,i);loads.append(dict(index=i,**loading))
        for k,arm in enumerate(base.rep.ARMS):
            shift=(repeat+i+k)%len(SERVICES);order=SERVICES[shift:]+SERVICES[:shift]
            for position,service in enumerate(order):
                before=econ.COUNTS.copy();t=time.perf_counter()
                try:data=execute(x,alpha,models[arm],service)
                except BaseException as exc:
                    base.dump(out/'failures'/f'timing-{repeat}-{i}-{arm}-{service}.json',dict(
                        repeat=repeat,index=i,alpha=alpha,arm=arm,service=service,
                        exception=traceback.format_exc(),partial=retained.failure_evidence(exc),
                        counts=base.counter_delta(before),elapsed_seconds=time.perf_counter()-t))
                    raise
                data.update(index=i,alpha=alpha,arm=arm,service=service,position=position)
                path=out/'timing'/f'{repeat}-{i}-{arm}-{service}.json';base.dump(path,data)
                entries.append(dict(index=i,arm=arm,service=service,position=position,path=str(path.relative_to(out)),
                    sha256=base.digest(path),seconds=data['seconds'],counts=data['counts']))
    base.dump(out/'timing'/f'PROCESS-{repeat}.json',dict(source=source(),repeat=repeat,
        entries=entries,model_loading=loads,inside_process_seconds=time.perf_counter()-started,
        machine=base.machine(),max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('all','timing-one'))
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--repeat',type=int,default=0)
    args=parser.parse_args();out=args.output;identity=source();out.mkdir(parents=True,exist_ok=True)
    if args.mode=='timing-one':return timing_one(out,args.repeat)
    if (out/'START.json').exists():raise FileExistsError('Preserve every attempted phase-B campaign')
    base.dump(out/'START.json',dict(source=identity,machine=base.machine(),started_unix=time.time()))
    started=time.perf_counter();processes=[]
    try:
        before=econ.COUNTS.copy();t=time.perf_counter();base.acquire(out)
        base.dump(out/'ACQUISITION119.json',dict(source=identity,seconds=time.perf_counter()-t,
            counts=base.counter_delta(before),new_experiment='R119-B',fresh_labels=True))
        retained.catalogue(out);reference(out)
        base.dump(out/'TIMING_START119B.json',dict(started_unix=time.time(),request='suspend other controlled compute and formatting during the seven local subprocesses'))
        for repeat in range(7):
            command=[sys.executable,__file__,'timing-one','--output',str(out),'--repeat',str(repeat)]
            t=time.perf_counter();p=subprocess.run(command,capture_output=True,text=True)
            log=out/'timing'/f'PROCESS-{repeat}.log';log.parent.mkdir(parents=True,exist_ok=True);log.write_text(p.stdout+p.stderr)
            processes.append(dict(repeat=repeat,command=command,exit_code=p.returncode,
                elapsed_seconds=time.perf_counter()-t,log_sha256=base.digest(log)))
            base.dump(out/'TIMING_PROGRESS.json',dict(processes=processes))
            if p.returncode:raise RuntimeError('Preserve failed phase-B timing subprocess')
            print('TIMING',repeat,'completed',flush=True)
        base.dump(out/'TIMING_END119B.json',dict(ended_unix=time.time()))
        receipt=dict(source=identity,status='executed',processes=processes,
            total_elapsed_seconds=time.perf_counter()-started,primary_decisions=11520,timing_decisions=17920,
            population_inference=False,neural_exclusive_advantage=False,
            max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        base.dump(out/'CAMPAIGN119B.json',receipt);print('CAMPAIGN B EXECUTED',receipt['total_elapsed_seconds'],flush=True)
    except BaseException:
        base.dump(out/'FAILED.json',dict(source=identity,exception=traceback.format_exc(),
            elapsed_seconds=time.perf_counter()-started,processes=processes))
        raise


if __name__=='__main__':
    main()
