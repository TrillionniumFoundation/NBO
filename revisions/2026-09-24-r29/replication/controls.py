"""R29 fixed-cohort controls and residual-budget completion.

The original R28 implementation and frozen candidates are read-only inputs.
New training is isolated from optimal-reference file reads and solver calls.
All arithmetic acceptance tests use integers or Fraction, never printed floats.
"""
from __future__ import annotations
import argparse, collections, contextlib, gzip, hashlib, importlib.util, json
import math, os, platform, resource, sys, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
REV = ROOT / 'revisions/2026-09-24-r29'
OLD = ROOT / 'revisions/2026-09-24-r28'
OUT = REV / 'results/controls'
SPEC = importlib.util.spec_from_file_location('inventory28', OLD/'replication/inventory.py')
inv = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(inv)
T, BETA = inv.T, inv.BETA
EPS = F(1, 100)
MODELS = [(2,4),(3,4),(4,4),(4,5),(5,4),(6,4),(7,4)]
PROTOCOL_COMMIT = 'd7a809a5913bc5178cba186e003750ee3a9cc574'
READ_GUARD = {'active': False, 'paths': set()}

def _audit(event, args):
    if event != 'open' or not READ_GUARD['active']:
        return
    path, mode = args[0], args[1]
    if not isinstance(path, (str, bytes, os.PathLike)):
        return
    p = os.fsdecode(path)
    if mode is None or 'r' in str(mode) or '+' in str(mode):
        if 'optimal_reference' in p or '/reference/' in p:
            raise PermissionError('Reference read prohibited during candidate/completion: '+p)
        READ_GUARD['paths'].add(p)
sys.addaudithook(_audit)

@contextlib.contextmanager
def isolated():
    old = inv.independent_optimal
    def forbidden(*args, **kwargs):
        raise RuntimeError('Full-horizon optimal solver prohibited in candidate/completion')
    if READ_GUARD['active']:
        raise RuntimeError('Nested isolation is not supported')
    READ_GUARD['paths'] = set()
    READ_GUARD['active'] = True
    inv.independent_optimal = forbidden
    try:
        yield READ_GUARD['paths']
    finally:
        inv.independent_optimal = old
        READ_GUARD['active'] = False

def dump(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(obj, indent=2, allow_nan=False)+'\n').encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix=='.gz' else raw)

def load(path):
    path = Path(path); raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def measured(fn, *args, **kwargs):
    w, c = time.perf_counter(), time.process_time()
    ans = fn(*args, **kwargs)
    return ans, {'wall_seconds': time.perf_counter()-w,
                 'cpu_seconds': time.process_time()-c,
                 'process_high_water_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}

def validate_policy(model, policy):
    p = np.asarray(policy)
    if p.shape != (T, model.N) or not np.issubdtype(p.dtype, np.integer):
        raise ValueError('Policy must have integer shape (T,N)')
    if np.any(p < 0) or np.any(p >= model.A):
        raise ValueError('Action index outside model')
    if not np.all(model.feasible[model.row[None,:], p]) or np.any(p[:,0]):
        raise ValueError('Infeasible action or action at an absorbing state')

def generate(model, spec):
    """No reference value, optimal action table, or learned hyperparameter enters."""
    kind = spec['kind']
    if kind == 'inherited':
        rec = spec['record']; p = OLD/'results/inventory'/f"d{model.d}_L{model.L}"/rec['tag']
        if sha(p/'raw_policy.json') != rec['raw_policy_sha256']:
            raise AssertionError('Inherited candidate hash mismatch')
        return np.array(load(p/'raw_policy.json'), dtype=np.int64), {
            'inherited_from': str(p.relative_to(ROOT)),
            'source_policy_sha256': rec['raw_policy_sha256'],
            'training_not_reexecuted': True,
            'historical_generation_seconds': rec['generation_seconds'],
            'historical_compilation_seconds': rec['compilation_seconds'],
            'historical_times_excluded_from_R29_hardware_comparisons': True}
    if kind in ('neural','polynomial'):
        return inv.train(model, **spec)
    policy = np.zeros((T,model.N), dtype=np.int64)
    if kind == 'myopic':
        q = model.qexact(T-1, np.zeros(model.N, dtype=object))
        a, _ = model.choose(q); policy[:] = a
    elif kind == 'random':
        rng = np.random.default_rng(spec['seed'])
        for t in range(T):
            for s in range(1,model.N):
                policy[t,s] = rng.choice(np.flatnonzero(model.feasible[s]))
    elif kind == 'base_stock':
        target = math.ceil((model.L-1)/2)
        for s in range(1,model.N):
            deficit = target-model.states[s]; j = int(np.argmax(deficit))
            units = min(2,max(0,int(deficit[j])))
            if units:
                policy[:,s] = 1+2*j+int(units==2)
    elif kind == 'tabular2':
        for t in range(T):
            h = min(2,T-t)
            values = model.terminal.astype(object)*(model.den[t+h]//model.R)
            for j in range(t+h-1,t-1,-1):
                a, values = model.choose(model.qexact(j,values))
            policy[t] = a
    else:
        raise ValueError('Unknown candidate kind '+kind)
    return policy, {'kind': kind, 'seed': spec.get('seed'),
                    'training_uses_optimal_reference': False}

def completion(model, raw, epsilon=EPS, rule='fixed'):
    """B_t = delta_t + beta max_a P_a B_{t+1}; terminal/stopped B=0.

    Budget rule retains an action iff delta_t + propagated B <= epsilon.
    Greedy replacement is always feasible since propagated B <= beta*epsilon.
    """
    validate_policy(model, raw)
    if epsilon <= 0 or rule not in ('fixed','budget'):
        raise ValueError('Positive epsilon and a recognized rule are required')
    eta = epsilon / sum(BETA**j for j in range(T))
    p = np.asarray(raw, dtype=np.int64).copy()
    vnext = model.terminal.astype(object); bnext = np.zeros(model.N,dtype=object)
    changes, trace, all_gaps, bitmax = [], [], [], 0
    for t in reversed(range(T)):
        q = model.qexact(t,vnext); greedy,best = model.choose(q)
        future = 99*np.sum(bnext[model.next],axis=2)
        v, b = np.empty(model.N,dtype=object), np.empty(model.N,dtype=object)
        changed = 0; bmax = 0
        for s in range(model.N):
            prop = 0 if s==0 else int(max(future[s,a] for a in np.flatnonzero(model.feasible[s])))
            a = int(p[t,s]); gap = int(best[s]-q[s,a]); den = model.den[t]
            if rule=='budget':
                allowed = epsilon-F(prop,den)
                if allowed < 0:
                    raise AssertionError('Negative residual budget')
            else:
                allowed = eta
            if gap*allowed.denominator > allowed.numerator*den:
                replacement = int(greedy[s])
                changes.append([t,s,a,replacement,str(gap),str(allowed)])
                p[t,s] = replacement; a = replacement; changed += 1
            if s:
                all_gaps.append(float(F(gap,den)))
            v[s] = q[s,a]; b[s] = 0 if s==0 else int(best[s]-v[s])+prop
            if b[s]<0 or int(b[s])*epsilon.denominator > epsilon.numerator*den:
                raise AssertionError('Completion exceeded its all-restart budget')
            bmax = max(bmax,int(b[s])); bitmax=max(bitmax,abs(int(v[s])).bit_length(),int(b[s]).bit_length(),den.bit_length())
        trace.append({'t':t,'changed':changed,'envelope_max':str(F(bmax,model.den[t]))})
        vnext,bnext=v,b
    topology = collections.Counter()
    for t,s,old,new,gap,allowance in changes:
        state = model.states[s]
        topology[(t,int(state.sum()),int(np.min(state)),int(np.count_nonzero(state==0)))] += 1
    return p, {'rule':rule,'epsilon':str(epsilon),'fixed_eta':str(eta),
        'changed_actions':len(changes),'changed_fraction_nonstopped':len(changes)/(T*(model.N-1)),
        'changes_columns':['time','state_index','raw_action','completed_action','suffix_deficit_numerator','allowance'],
        'changes':changes,'by_time':sorted(trace,key=lambda x:x['t']),
        'topology_columns':['time','total_inventory','minimum_inventory','zero_coordinates','changed_count'],
        'topology':[list(k)+[v] for k,v in sorted(topology.items())],
        'suffix_deficit_quantiles':dict(zip(['min','median','q90','q99','max'],np.quantile(all_gaps,[0,.5,.9,.99,1]).tolist())),
        'maximum_integer_bit_length':bitmax,'optimal_reference_used':False}

def specs(d,L, oldrows):
    entries=[]
    if (d,L) in MODELS[:4]:
        for r in oldrows:
            if (r['d'],r['L'])==(d,L):
                entries.append((r['tag'],{'kind':'inherited','record':r}))
        entries += [(f'random_s{s}',{'kind':'random','seed':s}) for s in range(29001,29011)]
        entries += [(k,{'kind':k}) for k in ('myopic','base_stock','tabular2')]
        extra = range(27303,27311) if (d,L)==(4,4) else range(27303,27306) if (d,L)==(4,5) else []
        entries += [(f'neural_w32_h2_s{s}',{'kind':'neural','width':32,'depth':2,'seed':s}) for s in extra]
    else:
        entries=[('neural_w32_h2_s27303',{'kind':'neural','width':32,'depth':2,'seed':27303}),
                 ('polynomial_p2',{'kind':'polynomial','degree':2}),
                 ('random_s29001',{'kind':'random','seed':29001})]
        entries += [(k,{'kind':k}) for k in ('myopic','base_stock','tabular2')]
    return entries

def certificate(model,p):
    validate_policy(model,p)
    values,cert=inv.residual_certificate(model,p)
    cert['maximum_integer_bit_length']=max(max(abs(int(v)).bit_length() for v in row) for row in values)
    cert['maximum_denominator_bit_length']=max(v.bit_length() for v in model.den)
    return values,cert

def snapshot_inventory(path):
    return {str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*')) if p.is_file()}

def run_model(d,L):
    dest=OUT/f'd{d}_L{L}';dest.mkdir(parents=True,exist_ok=True)
    if (dest/'summary.json').exists():
        raise FileExistsError('Refusing to overwrite a frozen model run: '+str(dest))
    oldrows=load(OLD/'results/inventory/summary.json')
    model,construction=measured(inv.Model,d,L)
    events=[];frozen=[];start=time.perf_counter()
    for tag,spec in specs(d,L,oldrows):
        folder=dest/tag;folder.mkdir(exist_ok=True)
        with isolated() as reads:
            (raw,training),generation=measured(generate,model,spec)
            input_paths=sorted(reads)
        validate_policy(model,raw)
        dump(folder/'raw_policy.json',raw.tolist());dump(folder/'training.json',training)
        dump(folder/'input_audit.json',{'opened_read_paths':input_paths,'reference_guard_enforced':True,
             'full_horizon_solver_disabled':True,'protocol_commit':PROTOCOL_COMMIT})
        rawsha=sha(folder/'raw_policy.json')
        events.append({'event':'raw_candidate_frozen','tag':tag,'sha256':rawsha})
        (rawv,rawcert),rawcheck=measured(certificate,model,raw)
        dump(folder/'raw_certificate.json.gz',rawcert)
        outputs=[]
        sensitivity_tag = 'neural_w32_h2_s27301' if d in (2,3) else 'neural_w32_h2_s27303'
        tolerances=[EPS]+([F(1,1000),F(1,20)] if tag in ('myopic',sensitivity_tag) else [])
        for eps in tolerances:
            for rule in ('fixed','budget'):
                key=f'{rule}_e{eps.numerator}_{eps.denominator}'
                with isolated():
                    (comp,detail),repair=measured(completion,model,raw,eps,rule)
                    (cv,cc),check=measured(certificate,model,comp)
                if F(cc['bound_rational'])>eps:
                    raise AssertionError('Independent certificate rejects completion')
                dump(folder/(key+'_policy.json'),comp.tolist())
                dump(folder/(key+'_completion.json.gz'),detail)
                dump(folder/(key+'_certificate.json.gz'),cc)
                outputs.append({'key':key,'rule':rule,'epsilon':str(eps),
                     'policy_sha256':sha(folder/(key+'_policy.json')),
                     'certificate_sha256':sha(folder/(key+'_certificate.json.gz')),
                     'bound_rational':cc['bound_rational'],'bound_upper':cc['bound_upper'],
                     'completion':repair,'certification':check,
                     'changed_actions':detail['changed_actions'],
                     'changed_fraction_nonstopped':detail['changed_fraction_nonstopped'],
                     'maximum_integer_bit_length':max(detail['maximum_integer_bit_length'],cc['maximum_integer_bit_length']),
                     'topology':detail['topology'],'suffix_deficit_quantiles':detail['suffix_deficit_quantiles']})
        original_spec=spec['record']['spec'] if spec['kind']=='inherited' else spec
        row={'d':d,'L':L,'states':model.N,'tag':tag,'spec':original_spec,
             'inherited':spec['kind']=='inherited','raw_policy_sha256':rawsha,
             'generation':generation,'model_construction':construction,'raw_certification':rawcheck,
             'raw_bound_rational':rawcert['bound_rational'],'raw_bound_upper':rawcert['bound_upper'],
             'variants':outputs,'model_array_bytes':model.memory(),'policy_bytes':int(raw.nbytes),
             'logical_feasible_state_action_successor_terms_per_sweep':T*int(model.feasible[1:].sum())*model.D,
             'dense_successor_slots_per_sweep':T*model.N*model.A*model.D,
             'training_input_audit_sha256':sha(folder/'input_audit.json')}
        dump(folder/'pre_reference.json',row);frozen.append(row)
        events.append({'event':'all_reference_free_variants_frozen','tag':tag,'pre_reference_sha256':sha(folder/'pre_reference.json')})
        print('FROZEN',d,L,tag,flush=True)
    dump(dest/'FREEZE_MANIFEST.json',frozen)
    freeze_sha=sha(dest/'FREEZE_MANIFEST.json')
    events.append({'event':'all_candidates_frozen','manifest_sha256':freeze_sha})
    independent_model,ref_setup=measured(inv.Model,d,L)
    (opt,optimal_policy,_),reference=measured(inv.independent_optimal,independent_model)
    dump(dest/'optimal_reference.json.gz',{'values':inv.rational_array(opt),'policy':optimal_policy.tolist(),
         'denominators':list(map(str,model.den)),'freeze_manifest_sha256':freeze_sha,
         'model_construction':ref_setup,'independent_solve':reference})
    events.append({'event':'independent_optimal_reference_created','sha256':sha(dest/'optimal_reference.json.gz')})
    rows=[]
    for row in frozen:
        folder=dest/row['tag'];raw=np.array(load(folder/'raw_policy.json'),dtype=np.int64)
        if sha(folder/'raw_policy.json')!=row['raw_policy_sha256']:
            raise AssertionError('Raw policy changed after freeze')
        (rv,_),raw_eval_cost=measured(certificate,model,raw)
        raw_eval,raw_eval_time=measured(inv.evaluate,model,rv,opt,raw,optimal_policy)
        row['raw']=raw_eval;row['raw_reference_evaluation']=raw_eval_time
        cert=load(folder/'raw_certificate.json.gz')
        for t in range(T):
            for s in range(model.N):
                if not 0<=int(opt[t][s]-rv[t][s])<=int(cert['envelope_numerators'][t][s]):
                    raise AssertionError('Raw envelope fails independent reference')
        for variant in row['variants']:
            key=variant['key'];comp=np.array(load(folder/(key+'_policy.json')),dtype=np.int64)
            if sha(folder/(key+'_policy.json'))!=variant['policy_sha256']:
                raise AssertionError('Completed policy changed after freeze')
            (cv,_),policy_eval=measured(certificate,model,comp)
            evaluation,evaluation_time=measured(inv.evaluate,model,cv,opt,comp,optimal_policy)
            cc=load(folder/(key+'_certificate.json.gz'))
            for t in range(T):
                for s in range(model.N):
                    if not 0<=int(opt[t][s]-cv[t][s])<=int(cc['envelope_numerators'][t][s]):
                        raise AssertionError('Completed envelope fails independent reference')
            variant['evaluation']=evaluation
            variant['reference_audit']={'own_policy_and_certificate_recheck':policy_eval,'gap_comparison':evaluation_time}
            component_times=[construction,row['generation'],row['raw_certification'],variant['completion'],variant['certification'],ref_setup,reference,raw_eval_cost,raw_eval_time,policy_eval,evaluation_time]
            variant['standalone_measured_components_seconds']=sum(x['wall_seconds'] for x in component_times)
            variant['standalone_measured_components_cpu_seconds']=sum(x['cpu_seconds'] for x in component_times)
            variant['cost_scope']='full non-amortized model and reference charged per policy; includes raw audit and chosen repair/certificate; excludes interpreter/import startup and file serialization (included only in cohort wall time); inherited fitting not rerun or included'
        row['reference_model_construction']=ref_setup;row['independent_reference']=reference
        row['reference_amortized_over_cases_seconds']=(ref_setup['wall_seconds']+reference['wall_seconds'])/len(frozen)
        dump(folder/'record.json',row);rows.append(row)
    dump(dest/'events.json',events);dump(dest/'summary.json',rows)
    dump(dest/'MODEL_EXECUTION.json',{'wall_seconds':time.perf_counter()-start,'cases':len(rows),
         'reference_free_variants':sum(len(x['variants']) for x in rows),
         'memory_scope':'process high-water RSS includes Python, libraries, prior cases and live model; not isolated per-case peak',
         'reference_guard_scope':'audited runtime candidate/completion dependency, not investigator blinding',
         'files_sha256':snapshot_inventory(dest)})
    return rows

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--model',type=int,nargs=2);args=parser.parse_args()
    inv.torch.set_num_threads(1);inv.torch.set_default_dtype(inv.torch.float64);inv.torch.use_deterministic_algorithms(True)
    before=time.perf_counter();rows=[]
    for d,L in ([tuple(args.model)] if args.model else MODELS):
        rows.extend(run_model(d,L))
    if not args.model:
        if len(rows)!=115: raise AssertionError('Fixed cohort was not fully retained')
        dump(OUT/'summary.json',rows)
        dump(OUT/'environment.json',{'python':sys.version,'numpy':np.__version__,'scipy':inv.scipy.__version__,
             'torch':inv.torch.__version__,'platform':platform.platform(),'torch_threads':1,
             'cpu_affinity':sorted(os.sched_getaffinity(0)),
             'wall_seconds':time.perf_counter()-before,'process_high_water_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             'integer_backend':'Python arbitrary-precision integers via NumPy object arrays; fractions.Fraction for comparisons',
             'protocol_commit':PROTOCOL_COMMIT,
             'base_evidence_commit':'cd1191f278948942f42c6507b4566108f2aa2f6d',
             'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),OLD/'replication/inventory.py']}})
if __name__=='__main__':
    main()
