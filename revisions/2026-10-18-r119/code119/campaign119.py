"""Source-bound original-investment experiment, with complete attempted work."""
from __future__ import annotations
from pathlib import Path
import os, sys, json, time, subprocess, traceback, resource, hashlib, math
import numpy as np
import active_tail119 as tail
from active_tail119 import base, kern, econ, uniform as q, I
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'frozen117/code117'))
import precision117 as inherited
SERVICES = ('compiled', 'geometric', 'active-tail')
LEVELS = (.5, .75)
os.environ.setdefault('NBO_PROTOCOL108', '29180a4ce4a6db7298e7458ecdfff3da08abb08f')


def source():
    manifest = ROOT / 'SOURCE_FREEZE119.json'
    freeze = json.loads(manifest.read_text())
    for path, sha in freeze['files'].items():
        if base.digest(ROOT / path) != sha:
            raise RuntimeError('Frozen scientific content differs: ' + path)
    commit = os.environ.get('NBO_SOURCE119', '')
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise RuntimeError('NBO_SOURCE119 must identify the actual committed executable')
    repo = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, text=True).strip())
    prefix = str(ROOT.relative_to(repo)) + '/'
    paths = list(freeze['files']) + ['SOURCE_FREEZE119.json']
    for path in paths:
        committed = subprocess.check_output(['git', 'show', commit + ':' + prefix + path], cwd=repo)
        if hashlib.sha256(committed).hexdigest() != base.digest(ROOT / path):
            raise RuntimeError('Actual committed source identity differs: ' + path)
    return dict(executable_protocol_commit=commit,
        manifest_sha256=base.digest(manifest), verified_committed_files=len(paths),
        protocol_sha256=base.digest(ROOT / 'PROTOCOL119.md'), inherited_source=base.source(),
        original_economy=True, population_inference=False)


def execute(x, alpha, model, service):
    start = time.perf_counter()
    if service == 'compiled':
        data = inherited.service(x, alpha, model, ladder=False)
    elif service == 'geometric':
        data = inherited.service(x, alpha, model, ladder=True)
    elif service == 'active-tail':
        data = tail.service(x, alpha, model)
    else:
        raise ValueError(service)
    for row in data['rows']:
        row['first_attempt_rejected'] = not (row['first_loss'] <= 1/256 and row['first_width'] <= 1/8192)
        row['proposal_repaired'] = row['first_rejected']
        row['returned_action_changed'] = row['action'] != row['proposed']
    data['algorithm_seconds'] = data['seconds']
    data['seconds'] = time.perf_counter() - start
    data['raw_first_rejected_means'] = '128-bin gate required conventional repair'
    return data


def failure_evidence(exc):
    def encode(value):
        if isinstance(value,np.ndarray): return encode(value.tolist())
        if isinstance(value,np.generic): return encode(value.item())
        if isinstance(value,float) and not math.isfinite(value): return {'nonfinite_float':repr(value)}
        if isinstance(value,dict): return {k:encode(v) for k,v in value.items()}
        if isinstance(value,(list,tuple)): return [encode(v) for v in value]
        return value
    if hasattr(exc, 'evidence119'):
        return encode(exc.evidence119)
    # Preserve only scientific fields in the immutable inherited adapter. No
    # environment, credentials or unrelated caller locals are inspected.
    evidence = []; tb = exc.__traceback__
    allowed = ('attempts','proposed','actions','rec','record','ids','indices','bins','used','rejected','exact')
    target = (ROOT/'frozen117/code117/precision117.py').resolve()
    while tb is not None:
        frame = tb.tb_frame
        if Path(frame.f_code.co_filename).resolve() == target:
            evidence.append(dict(function=frame.f_code.co_name,line=tb.tb_lineno,
                fields={k:encode(frame.f_locals[k]) for k in allowed if k in frame.f_locals}))
        tb = tb.tb_next
    return evidence


def load_models(out, index):
    start = time.perf_counter(); models = {}; per_arm = {}
    for arm in base.rep.ARMS:
        t = time.perf_counter()
        models[arm] = base.rep.restore(json.loads((out/'models'/f'{index}-{arm}'/'model.json').read_text()))
        per_arm[arm] = time.perf_counter()-t
    return models, dict(seconds=time.perf_counter()-start, per_arm=per_arm)


def catalogue(out):
    x = base.rep.grid(12); entries = []; loads = []
    for i, alpha in enumerate(LEVELS):
        models, loading = load_models(out, i)
        loads.append(dict(index=i, **loading, count=len(models)))
        for k, arm in enumerate(base.rep.ARMS):
            for service in SERVICES:
                before = econ.COUNTS.copy(); started = time.perf_counter()
                try:
                    data = execute(x, alpha, models[arm], service)
                except BaseException as exc:
                    base.dump(out/'failures'/f'catalogue-{i}-{arm}-{service}.json', dict(
                        index=i, alpha=alpha, arm=arm, service=service, exception=traceback.format_exc(),
                        partial=failure_evidence(exc), counts=base.counter_delta(before),
                        elapsed_seconds=time.perf_counter()-started))
                    raise
                data.update(index=i, alpha=alpha, arm=arm, service=service,
                    model_sha256=base.digest(out/'models'/f'{i}-{arm}'/'model.json'))
                path = out/'catalogue'/f'{i}-{arm}-{service}.json'
                base.dump(path, data)
                entries.append(dict(path=str(path.relative_to(out)), sha256=base.digest(path), decisions=len(x)))
                base.dump(out/'PROGRESS.json', dict(status='running', entries=entries))
                print('CATALOGUE', i, arm, service, round(data['seconds'], 6), flush=True)
    base.dump(out/'CATALOGUE119.json', dict(status='executed', source=source(), entries=entries,
        model_loading=loads, decisions=sum(v['decisions'] for v in entries)))


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
                for control, treatment in (('compiled','geometric'), ('compiled','active-tail'), ('geometric','active-tail')):
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


def timing_one(out, repeat):
    marker=out/'timing'/f'START-{repeat}.json'; marker.parent.mkdir(parents=True,exist_ok=True)
    with marker.open('x') as stream:
        json.dump(dict(repeat=repeat,started_unix=time.time(),no_overwrite=True),stream)
    x = base.rep.grid(12)[:32]; entries = []; loads = []; started = time.perf_counter()
    for i, alpha in enumerate(LEVELS):
        models, loading = load_models(out, i); loads.append(dict(index=i, **loading))
        for k, arm in enumerate(base.rep.ARMS):
            shift = (repeat+i+k) % 3
            order = SERVICES[shift:] + SERVICES[:shift]
            for position, service in enumerate(order):
                before = econ.COUNTS.copy(); call_started = time.perf_counter()
                try:
                    data = execute(x, alpha, models[arm], service)
                except BaseException as exc:
                    base.dump(out/'failures'/f'timing-{repeat}-{i}-{arm}-{service}.json', dict(
                        repeat=repeat, index=i, alpha=alpha, arm=arm, service=service,
                        exception=traceback.format_exc(), partial=failure_evidence(exc),
                        counts=base.counter_delta(before), elapsed_seconds=time.perf_counter()-call_started))
                    raise
                data.update(index=i, alpha=alpha, arm=arm, service=service, position=position)
                path = out/'timing'/f'{repeat}-{i}-{arm}-{service}.json'; base.dump(path, data)
                entries.append(dict(index=i, arm=arm, service=service, position=position,
                    path=str(path.relative_to(out)), sha256=base.digest(path),
                    seconds=data['seconds'], counts=data['counts']))
    base.dump(out/'timing'/f'PROCESS-{repeat}.json', dict(source=source(), repeat=repeat,
        entries=entries, model_loading=loads, inside_process_seconds=time.perf_counter()-started,
        machine=base.machine(), max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))


def scaling(out):
    records = []
    for d in (2,4,8):
        x = np.array([[((17*i+11*j+3)%64)/64 for j in range(d)] for i in range(32)])
        for alpha in LEVELS:
            before = econ.COUNTS.copy(); started = time.perf_counter()
            with kern.backend(True):
                a = base.c.actor(x, alpha, None)
            proposal = dict(seconds=time.perf_counter()-started, counts=base.counter_delta(before))
            for service in ('compiled','active-tail'):
                before = econ.COUNTS.copy(); started = time.perf_counter()
                with kern.backend(True):
                    rec = q.certificate(x,a,alpha,128) if service=='compiled' else tail.certificate(x,a,alpha,8)
                records.append(dict(d=d, alpha=alpha, service=service, state=x.tolist(), action=a.tolist(),
                    **{k:rec[k].tolist() for k in base.KEYS}, qualified=q.qualifies(rec).tolist(),
                    seconds=time.perf_counter()-started, counts=base.counter_delta(before),
                    common_proposal=proposal, complete_service=False))
                base.dump(out/'SCALING_PROGRESS.json', dict(status='running', records=records))
    base.dump(out/'SCALING119.json', dict(source=source(), records=records,
        scope='fixed 32 states per d/risk; primitive one-step certificate scaling, not a learned higher-dimensional tournament'))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('all','timing-one'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeat', type=int, default=0)
    args = parser.parse_args(); out = args.output
    identity = source(); out.mkdir(parents=True, exist_ok=True)
    if args.mode == 'timing-one':
        if (out/'timing'/f'PROCESS-{args.repeat}.json').exists():
            raise FileExistsError('Never overwrite a timing process')
        return timing_one(out, args.repeat)
    if (out/'START.json').exists():
        raise FileExistsError('Never overwrite an attempted campaign identity')
    base.dump(out/'START.json', dict(source=identity, machine=base.machine(), started_unix=time.time()))
    started = time.perf_counter(); processes = []
    try:
        before = econ.COUNTS.copy(); t = time.perf_counter(); base.acquire(out)
        base.dump(out/'ACQUISITION119.json', dict(source=identity, seconds=time.perf_counter()-t,
            counts=base.counter_delta(before), new_experiment='R119', fresh_labels=True))
        catalogue(out); reference(out)
        for repeat in range(7):
            command = [sys.executable, __file__, 'timing-one', '--output', str(out), '--repeat', str(repeat)]
            t = time.perf_counter(); process = subprocess.run(command, capture_output=True, text=True)
            log = out/'timing'/f'PROCESS-{repeat}.log'; log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text(process.stdout+process.stderr)
            processes.append(dict(repeat=repeat, command=command, exit_code=process.returncode,
                elapsed_seconds=time.perf_counter()-t, log_sha256=base.digest(log)))
            base.dump(out/'TIMING_PROGRESS.json', dict(processes=processes))
            if process.returncode:
                raise RuntimeError('Timing process failed; attempted evidence retained')
            print('TIMING', repeat, 'completed', flush=True)
        scaling(out)
        receipt = dict(source=identity, status='executed', processes=processes,
            total_elapsed_seconds=time.perf_counter()-started, primary_decisions=6912,
            timing_decisions=10752, population_inference=False, neural_exclusive_advantage=False,
            max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        base.dump(out/'CAMPAIGN119.json', receipt)
        print('CAMPAIGN EXECUTED', receipt['total_elapsed_seconds'], flush=True)
    except BaseException:
        base.dump(out/'FAILED.json', dict(source=identity, exception=traceback.format_exc(),
            elapsed_seconds=time.perf_counter()-started, processes=processes))
        raise


if __name__ == '__main__':
    main()
