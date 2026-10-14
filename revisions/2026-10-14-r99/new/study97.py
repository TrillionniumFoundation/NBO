"""R97 certificate-oriented readouts, complete acquisition receipts and service work.

New experiments do not reuse R96 confirmation as fresh observations. All reported
population purchase bounds use the deterministic service regret bound, not pilot
means. Every subprocess is retained, including failures and fallback work.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, os, pathlib, platform, resource
import subprocess, sys, time, struct
R = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'code'))
import numpy as np
from scipy.optimize import linprog, lsq_linear
from interval94 import I, up
from investment94 import COUNTS, terminal_certificate
from continuum94 import actor, uniform_residual
from representations94 import features
from matched96 import MatchedFit
from quadrature96 import certificate, qualifies, TAU, WIDTH
KINDS = ('quadratic', 'relu', 'spline')
ARMS = ('online', 'quadratic-ls', 'quadratic-ca', 'relu-ls', 'relu-ca', 'spline-ls', 'spline-ca')
LEVELS = (.5, .75)


def digest(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def dump(p, obj):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w') as f:
        json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False); f.write('\n')
        f.flush(); os.fsync(f.fileno())


def source():
    return {'pinned_R96': '9a80ab7d4de97c9a61747899766fab43ec3c2598',
            'execution_source': os.environ.get('NBO_SOURCE97', 'local-development'),
            'script_sha256': digest(__file__)}


def states(stream, index, n, rank=6, labels=1024):
    g = np.random.Generator(np.random.PCG64(np.random.SeedSequence([2026101497, stream, index, rank, labels])))
    return g.integers(0, 2**20, size=(n, 2), dtype=np.int64) / 2**20


def machine():
    p = pathlib.Path('/proc/cpuinfo')
    return {'architecture': platform.machine(), 'python': platform.python_version(),
            'numpy': np.__version__, 'frequency_controlled': False,
            'cpu': [s for s in p.read_text().splitlines() if s.startswith(('model name', 'cpu MHz'))][:4] if p.exists() else [],
            'threads': {k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')}}


def serialize(model):
    if model is None:
        return b'online-original-risk-service-v97\n'
    # Family tag and all executable numbers, no uncharged architecture metadata.
    values = np.r_[KINDS.index(model.kind), model.directions.ravel(), model.offsets, model.coefficients]
    return np.asarray(values, dtype='<f8').tobytes()


def load_model(path):
    raw = pathlib.Path(path).read_bytes()
    if raw == b'online-original-risk-service-v97\n': return None
    if len(raw) % 32 or len(raw) < 64: raise ValueError('Invalid executable payload length')
    values = np.frombuffer(raw, dtype='<f8').copy(); k = len(values)//4-1
    tag = int(values[0])
    if values[0] != tag or tag not in range(3): raise ValueError('Invalid family tag')
    return MatchedFit(KINDS[tag], values[1:1+2*k].reshape(k,2),
                      values[1+2*k:1+3*k], values[1+3*k:], {})


def trace_service(x, alpha, model):
    """Same production decision rule as R96, with initial width and paid stages."""
    x = np.asarray(x, dtype=float); clocks = {}; before = COUNTS.copy()
    t = time.perf_counter(); proposed = actor(x, alpha, model); clocks['proposal'] = time.perf_counter()-t
    actions = proposed.copy(); t = time.perf_counter()
    rec = certificate(x, actions, alpha); clocks['first_certificate'] = time.perf_counter()-t
    first_loss = rec['loss'].copy(); first_width = rec['width'].copy()
    rejected = ~qualifies(rec); used = np.full(len(x), 128, int); exact = np.zeros(len(x), bool)
    clocks.update(repair_proposal=0., repair_certificate=0., refinement=0., exact_fallback=0.)
    if np.any(rejected):
        t = time.perf_counter(); actions[rejected] = actor(x[rejected], alpha, None); clocks['repair_proposal'] = time.perf_counter()-t
        t = time.perf_counter(); fresh = certificate(x[rejected], actions[rejected], alpha); clocks['repair_certificate'] = time.perf_counter()-t
        for key in ('lower', 'upper', 'optimum_lower', 'loss', 'width'): rec[key][rejected] = fresh[key]
    for bins in (256, 512, 1024, 2048, 4096):
        bad = ~qualifies(rec)
        if not np.any(bad): break
        t = time.perf_counter(); fresh = certificate(x[bad], actions[bad], alpha, bins); clocks['refinement'] += time.perf_counter()-t
        used[bad] = bins
        for key in ('lower', 'upper', 'optimum_lower', 'loss', 'width'): rec[key][bad] = fresh[key]
    for j in np.flatnonzero(~qualifies(rec)):
        from rational96 import exact_service
        t = time.perf_counter(); a, lo, hi, opt, n = exact_service(x[j], alpha); clocks['exact_fallback'] += time.perf_counter()-t
        actions[j] = a; rec['lower'][j] = lo; rec['upper'][j] = hi; rec['optimum_lower'][j] = opt
        rec['loss'][j] = up(hi-opt); rec['width'][j] = up(hi-lo); used[j] = n; exact[j] = True
    if not np.all(qualifies(rec)): raise ArithmeticError('Complete workload failed; no row deletion')
    data = {k: rec[k] for k in ('lower', 'upper', 'optimum_lower', 'loss', 'width')}
    data.update(actions=actions, proposed=proposed, rejected=rejected, proposed_loss=first_loss,
                proposed_width=first_width, loss_reason=first_loss>TAU, width_reason=first_width>WIDTH,
                exact=exact, used_bins=used)
    counts = {k: v-before.get(k, 0) for k, v in COUNTS.items() if v != before.get(k, 0)}
    return data, {'stage_seconds': clocks, 'counts': counts, 'rejected': int(rejected.sum()),
                  'loss_reason': int((first_loss>TAU).sum()), 'width_reason': int((first_width>WIDTH).sum()),
                  'refined_rows': int((used>128).sum()), 'exact_fallbacks': int(exact.sum())}


def design(kind, x, W, b):
    z = x @ W.T + b
    return np.column_stack((np.ones(len(x)), x, z*z if kind == 'quadratic' else np.maximum(z, 0)))


def build(kind, x, labels, rank):
    W, b = features(kind, 2)
    if kind == 'spline':
        b = np.array([-np.quantile(x[:, k%2], (k//2+1)/17) for k in range(32)])
        b = np.rint(b*2**16)/2**16
    Aall = design(kind, x, W, b); selected = []; trials = []
    y = labels['lower']+(labels['upper']-labels['lower'])/2
    for step in range(rank-3):
        candidates = []
        for j in range(32):
            if j in selected: continue
            ids = [0, 1, 2]+[3+k for k in selected+[j]]; A = Aall[:, ids]
            attained = int(np.linalg.matrix_rank(A))
            if attained != len(ids):
                trials.append({'step': step, 'candidate': j, 'rank_rejected': True}); continue
            f = lsq_linear(A, y, bounds=(np.r_[[-np.inf]*3, np.zeros(len(ids)-3)], np.full(len(ids), np.inf)),
                           method='trf', lsq_solver='exact', tol=1e-10, max_iter=1000)
            if not f.success or not np.all(np.isfinite(f.x)): raise ArithmeticError('Candidate optimization failed')
            loss = float(np.sum((A@f.x-y)**2)); trials.append({'step': step, 'candidate': j, 'loss': loss, 'iterations': int(f.nit)})
            candidates.append((loss, j, f.x, A))
        if not candidates: raise ArithmeticError('No full-rank candidate')
        minimum = min(c[0] for c in candidates)
        # Declared numerical tie cell; unlike a platform-dependent exact-float tie.
        tied = [c for c in candidates if c[0] <= minimum+1e-12*max(1., abs(minimum))]
        chosen = min(tied, key=lambda c: c[1]); _, j, theta, A = chosen; selected.append(j)
    theta = np.rint(theta*2**30)/2**30; theta[3:] = np.maximum(theta[3:], 0)
    fit = MatchedFit(kind, W[selected], b[selected], theta, {})
    fit.record = {'rank': int(np.linalg.matrix_rank(A)), 'selected': selected, 'condition_number': float(np.linalg.cond(A)),
                  'trials': trials, 'candidate_solves': sum('loss' in q for q in trials),
                  'nonlinear_features': rank-3, 'readout_coefficients': len(theta), 'tie_tolerance': 1e-12}
    return fit


def certificate_readout(model, z, bounds):
    """Minimize an interval residual span on acquired nodes; verify after rounding.

The full-domain cell bound is authoritative. If it worsens, keep the LS model.
A node LP is not mislabeled as a globally optimal semi-infinite program.
"""
    A = design(model.kind, z, model.directions, model.offsets); k = A.shape[1]
    c = np.r_[np.zeros(k), -1., 1.]
    lhs = np.vstack((np.column_stack((A, np.ones(len(A)), np.zeros(len(A)))),
                     np.column_stack((-A, np.zeros(len(A)), -np.ones(len(A))))))
    rhs = np.r_[bounds['lower'], -bounds['upper']]
    variable_bounds = [(0.,0.)]+[(-1e4,1e4)]*2+[(0.,1e4)]*(k-3)+[(None,None)]*2
    fit = linprog(c, A_ub=lhs, b_ub=rhs, bounds=variable_bounds, method='highs',
                  options={'primal_feasibility_tolerance':1e-9, 'dual_feasibility_tolerance':1e-9})
    if not fit.success: raise ArithmeticError('Certificate-readout LP failed: '+fit.message)
    theta = np.rint(fit.x[:k]*2**30)/2**30; theta[3:] = np.maximum(theta[3:],0)
    new = MatchedFit(model.kind, model.directions.copy(), model.offsets.copy(), theta, dict(model.record))
    # Outward interval node assessment: LP solver status is never a certificate.
    pred = new.interval(I(z)); l = float(np.min((I(bounds['lower'])-pred).lo)); u = float(np.max((I(bounds['upper'])-pred).hi))
    new.record.update(lp_objective=float(fit.fun), rounded_node_span=float(up(u-l)), lp_iterations=int(fit.nit))
    return new


def write_rows(path, x, data):
    keys = list(data)
    with pathlib.Path(path).open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['row','x0','x1']+keys)
        for j in range(len(x)): w.writerow([j,*x[j]]+[data[k][j] for k in keys])
        f.flush(); os.fsync(f.fileno())


def one(index, arm, rank, labels, folder):
    folder = pathlib.Path(folder); folder.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter(); stages = {}; model = None; receipt = {'source':source(),'machine':machine(), 'arm':arm,
        'index':index,'alpha':LEVELS[index],'rank_budget':rank,'training_label_budget':labels,'status':'started'}
    alpha = LEVELS[index]
    if arm != 'online':
        kind, method = arm.split('-'); x = states(1,index,labels,rank,labels)
        t=time.perf_counter(); lab=terminal_certificate(I(x),alpha); stages['training_labels']=time.perf_counter()-t
        t=time.perf_counter(); model=build(kind,x,lab,rank); stages['feature_search_and_fit']=time.perf_counter()-t
        grid=np.linspace(0,1,33); z=np.stack(np.meshgrid(grid,grid,indexing='ij'),-1).reshape(-1,2)
        t=time.perf_counter(); bound=terminal_certificate(I(z),alpha); stages['cover_labels']=time.perf_counter()-t
        t=time.perf_counter(); old_cover=uniform_residual(model,alpha,32); stages['initial_whole_domain_validation']=time.perf_counter()-t
        receipt['baseline_cover']=old_cover
        if method=='ca':
            t=time.perf_counter(); candidate=certificate_readout(model,z,bound); stages['certificate_readout_lp']=time.perf_counter()-t
            t=time.perf_counter(); new_cover=uniform_residual(candidate,alpha,32); stages['candidate_whole_domain_validation']=time.perf_counter()-t
            receipt['candidate_cover']=new_cover; receipt['readout_candidate_record']=candidate.record
            # Both candidate construction and a rejected candidate remain charged.
            receipt['readout_admitted']=new_cover['span']<=old_cover['span']
            if receipt['readout_admitted']: model=candidate
        receipt['fit_record']=model.record
        # Count repeated label calls used by validation, not only unique sites.
        receipt['unique_acquired_label_sites_at_most']=labels+1089
    t=time.perf_counter(); data, val=trace_service(states(2,index,16,rank,labels),alpha,model)
    stages['validation_services']=time.perf_counter()-t; receipt['validation']=val
    t=time.perf_counter(); raw=serialize(model); p=folder/'model.bin'
    with p.open('wb') as f: f.write(raw); f.flush(); os.fsync(f.fileno())
    descriptor=os.open(folder,os.O_RDONLY); os.fsync(descriptor); os.close(descriptor)
    receipt['model_sha256']=digest(p); restored=load_model(p)
    if serialize(restored)!=raw: raise ArithmeticError('Durable serialization identity failed')
    if model is not None and not np.array_equal(model.float_eval(states(2,index,16,rank,labels)),restored.float_eval(states(2,index,16,rank,labels))):
        raise ArithmeticError('Reload changed model')
    stages['durable_serialization_hash_reload']=time.perf_counter()-t
    receipt.update(status='acquired', acquisition_inside_seconds=time.perf_counter()-start,
                   acquisition_stage_seconds=stages, payload_bytes=len(raw), acquisition_counts=COUNTS.copy(),
                   max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    dump(folder/'acquisition.json',receipt)
    # Model and its complete acquisition record are durable before test outcomes.
    x=states(3,index,64,rank,labels); t=time.perf_counter(); data, trace=trace_service(x,alpha,restored)
    write_rows(folder/'evaluation.csv',x,data)
    trace.update(seconds=time.perf_counter()-t, source=source(), rows=64,
                 maximum_loss=float(data['loss'].max()),maximum_width=float(data['width'].max()),
                 population_inference_claim=False, rows_sha256=digest(folder/'evaluation.csv'))
    dump(folder/'evaluation.json',trace)
    return receipt


def timing_one(index, arm, model_path, output):
    t=time.perf_counter(); model=load_model(model_path); identity=digest(model_path)
    data, trace=trace_service(states(5,index,32),LEVELS[index],model)
    trace.update(source=source(), machine=machine(), model_sha256=identity,
                 inside_process_seconds=time.perf_counter()-t, rows=32, independent_observations_added=0)
    dump(output,trace)


def campaign():
    out=R/'results97'; out.mkdir(exist_ok=True)
    if (out/'CAMPAIGN97.json').exists(): raise FileExistsError('Completed campaign cannot be overwritten')
    record={'source':source(),'machine':machine(),'configurations':[], 'timings':[],
            'scope':'Construction and deterministic service probes; no new population superiority claim.'}
    for index in range(2):
        for rank in (4,5,6):
            for labels in (256,1024):
                for arm in ARMS:
                    folder=out/f'a{index}-r{rank}-n{labels}-{arm}'
                    command=[sys.executable,__file__,'one','--index',str(index),'--arm',arm,'--rank',str(rank),'--labels',str(labels),'--output',str(folder)]
                    t=time.perf_counter(); p=subprocess.run(command,capture_output=True,text=True); total=time.perf_counter()-t
                    # The complete process is retained as a conservative acquisition
                    # charge, including its post-acquisition diagnostic probe.
                    # No subtraction is used to manufacture a smaller setup cost.
                    (folder.parent/(folder.name+'.log')).write_text(p.stdout+p.stderr)
                    record['configurations'].append({'index':index,'rank':rank,'labels':labels,'arm':arm,
                        'path':str(folder.relative_to(R)),'complete_acquire_and_probe_process_seconds':total,'exit_code':p.returncode})
                    dump(out/'PROGRESS97.json',record)
                    if p.returncode: raise RuntimeError('Failed configuration retained: '+str(folder))
    # Sequential fresh-process timing, same workload and source per arm and risk.
    for repeat in range(3):
        for index in range(2):
            for arm in ARMS:
                folder=out/f'a{index}-r6-n1024-{arm}'; pth=out/f'timing-{repeat}-{index}-{arm}.json'
                t=time.perf_counter(); p=subprocess.run([sys.executable,__file__,'timing-one','--index',str(index),'--arm',arm,
                      '--model',str(folder/'model.bin'),'--output',str(pth)],capture_output=True,text=True)
                elapsed=time.perf_counter()-t
                record['timings'].append({'repeat':repeat,'index':index,'arm':arm,'seconds':elapsed,'exit_code':p.returncode,
                                         'path':str(pth.relative_to(R))})
                if p.returncode: raise RuntimeError(p.stderr)
    record['status']='executed'; dump(out/'CAMPAIGN97.json',record)
    return record


def main():
    p=argparse.ArgumentParser(); p.add_argument('mode',choices=('one','timing-one','campaign'))
    p.add_argument('--index',type=int);p.add_argument('--arm');p.add_argument('--rank',type=int,default=6)
    p.add_argument('--labels',type=int,default=1024);p.add_argument('--output');p.add_argument('--model'); a=p.parse_args()
    if a.mode=='one': one(a.index,a.arm,a.rank,a.labels,a.output)
    elif a.mode=='timing-one':timing_one(a.index,a.arm,a.model,a.output)
    else: campaign()
if __name__=='__main__':main()
