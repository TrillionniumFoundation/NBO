"""R11 referee audit. Does not modify the reviewed scientific inputs.

Usage: python reviewer_audit.py --repo /path/to/NBO --deposit /path/to/pristine/r11/output --out /path/to/results.json
Uses the author's dynamic solver for fresh economic experiments, but independently
reduces deposited Bernstein coefficients and adversarially tests the validator.
A copied, temporary fixture is the only evidence deliberately corrupted.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, importlib.util, io, json, os, platform
import shutil, sys, tempfile, time
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
import scipy

SHA = '3ab1ee131ee246fe1353ad3115451d0b72b60272'

def split(c: np.ndarray, t: float) -> tuple[np.ndarray, np.ndarray]:
    """De Casteljau subdivision, independently implemented for this audit."""
    row = np.asarray(c, dtype=float).copy()
    left, right = [row[0]], [row[-1]]
    while row.size > 1:
        row = (1-t)*row[:-1] + t*row[1:]
        left.append(row[0]); right.append(row[-1])
    return np.asarray(left), np.asarray(right[::-1])

def restrict(c: np.ndarray, a: float, b: float) -> np.ndarray:
    if not 0 <= a < b <= 1:
        raise ValueError('Invalid restriction interval')
    left, _ = split(c, b)
    _, answer = split(left, a/b)
    return answer

def coefficient_bounds(arr: dict, method: str) -> dict:
    def lower(target: int, sign: str) -> np.ndarray:
        raw = arr[f'{method}.lower.{target}.{sign}']
        return np.asarray([[restrict(c,.12,.13) for c in policy] for policy in raw])
    def upper(target: int, sign: str) -> np.ndarray:
        return arr[f'{method}.upper.0.{target}.{sign}']
    result = {}
    pairs = {'adjusted':(0,'positive',0,'nonpositive'),
             'zero':(1,'positive',1,'nonpositive'),
             'active_surrender_gain':(1,'positive',2,'positive')}
    for name,(t,s,v,w) in pairs.items():
        lo = np.max(np.min(lower(t,s)-upper(v,w)[None,:,:], axis=(1,2)))-2e-7
        hi = np.min(np.max(upper(t,s)[None,:,:]-lower(v,w), axis=(1,2)))+2e-7
        result[name] = [float(lo),float(hi)]
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--deposit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); start = time.perf_counter()
    root, deposit = args.repo.resolve(), args.deposit.resolve()
    source = root/'replication/r11'
    for p in (source/'core.py', source/'validate.py', deposit/'certificate_arrays.npz'):
        if not p.is_file(): raise FileNotFoundError(p)
    arr = dict(np.load(deposit/'certificate_arrays.npz',allow_pickle=False))
    result = {'reviewed_commit':SHA, 'environment':{'python':sys.version,
              'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform()}}
    independent = {m:coefficient_bounds(arr,m) for m in ('chord','count')}
    errors = []
    for m in independent:
        published = json.loads((deposit/f'{m}_certificate.json').read_text())['bounds']
        errors.extend(abs(np.asarray(independent[m][k])-published[k]).max() for k in published)
    result['independent_coefficient_reduction'] = independent
    result['maximum_coefficient_reduction_discrepancy'] = float(max(errors))
    assert max(errors) < 2e-13
    corrections = {}; method_difference = 0.
    for target in range(3):
        for sign in ('positive','nonpositive'):
            u = arr[f'chord.upper.0.{target}.{sign}']; t = np.arange(9)/8
            linear = u[:,0,None]*(1-t)+u[:,-1,None]*t
            corrections[f'{target}.{sign}'] = float(np.max(u-linear))
            method_difference = max(method_difference,float(abs(u-arr[f'count.upper.0.{target}.{sign}']).max()))
    result['chord_coefficient_corrections'] = corrections
    result['maximum_chord_count_coefficient_difference'] = method_difference
    with tempfile.TemporaryDirectory(prefix='nbo-referee-fixture-') as td:
        fixture = Path(td)/'output'; shutil.copytree(deposit,fixture)
        bad = {k:v.copy() for k,v in arr.items()}
        corrupted_key = 'chord.upper.0.0.positive'
        bad[corrupted_key][:] = -1e6
        np.savez_compressed(fixture/'certificate_arrays.npz',**bad)
        spec = importlib.util.spec_from_file_location('r11_fixture_validator',source/'validate.py')
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); mod.OUT = fixture
        captured = io.StringIO(); accepted = False
        try:
            with contextlib.redirect_stdout(captured): mod.main()
            accepted = True
        except Exception as exc:
            captured.write(repr(exc))
        bad_bounds = coefficient_bounds(bad,'chord')
        result['validator_mutation_test'] = {'temporary_fixture_only':True,
             'corrupted_key':corrupted_key,'replacement':-1e6,
             'author_validator_accepted':accepted,
             'independent_adjusted_interval':bad_bounds['adjusted'],
             'independent_interval_inconsistent':bad_bounds['adjusted'][0]>bad_bounds['adjusted'][1],
             'validator_output':captured.getvalue()}
    print('Coefficient reduction and temporary-fixture mutation test completed',flush=True)
    sys.path.insert(0,str(source))
    from core import Model, Joint, first_moments, SIGNS
    base = Model(); joint = Joint(base); reachable = joint.reachability()
    outside = float(base.terminal[base.center]); economics = []
    def offers(z, lam, benefit, fee, capacity, term_cost):
        features = z['c'].moments(z['p'],lam)[:,1]; rows = {}
        for sign in SIGNS:
            W = float(z['first'][sign]['value'])
            moments = first_moments(base,features,lam,z['first'][sign]['action'])
            assert abs(moments[0]+benefit*moments[1]-fee*moments[2]-W)<2e-11
            grant = max(0.,outside-W+.02*capacity**2)
            rows[sign] = {'W':W,'duration':float(moments[1]),'surrender':float(moments[2]),
                          'grant':grant,'principal_surplus_b1':float(moments[1]-grant-term_cost)}
        delta = rows['positive']['W']-rows['nonpositive']['W']
        duration_delta = rows['positive']['duration']-rows['nonpositive']['duration']
        principal_delta = rows['positive']['principal_surplus_b1']-rows['nonpositive']['principal_surplus_b1']
        assert abs(principal_delta-delta-duration_delta)<2e-12
        return {'offers':rows,'agent_difference':delta,'service_difference':duration_delta,
                'principal_difference_b1':principal_delta,
                'agent_choice':max(rows,key=lambda s:rows[s]['W']),
                'principal_choice_b1':max(rows,key=lambda s:rows[s]['principal_surplus_b1'])}
    for adj in (True,False):
        z = joint.solve(.125,.425,0.,adj,.8,.5,8); V = z['v']
        frontier = np.asarray([max([0.]+[float((base.terminal-V[n])[reachable[n]&~base.e[0].boundary].max())
                      for n in range(m,8)]) for m in range(1,9)])
        selected_W = max(z['first'][s]['value'] for s in SIGNS)
        for kappa in (0.,.01,.02):
            costs = np.maximum(0,outside-selected_W+.02*frontier**2)+kappa*np.arange(8)/8
            m = int(np.argmin(costs))+1; threshold = float(frontier[m-1])
            E = threshold+(1e-5 if m<8 else 0.)
            implemented = joint.solve(.125,.425,E,adj,.8,.5,m)
            assert max(abs(implemented['first'][s]['value']-z['first'][s]['value']) for s in SIGNS)<2e-11
            row = {'experiment':'priced_implementation','adjustment':adj,'kappa':kappa,'term':m,
                   'weak_threshold':threshold,'strict_capacity_and_fee':E,
                   'term_cost':kappa*(m-1)/8}
            row.update(offers(implemented,.125,.425,E,E,row['term_cost'])); economics.append(row)
        active = joint.solve(.125,.42425,.8,adj,.8,.5,1)
        row = {'experiment':'active_box_midpoint','adjustment':adj,'law':.125,
               'benefit':.42425,'fee_and_capacity':.8,'term':1,'term_cost':0.}
        row.update(offers(active,.125,.42425,.8,.8,0.)); economics.append(row)
    result['economic_experiments'] = economics
    result['scope'] = ('Pointwise model reoptimizations use the author solver and moment primitives; '
                       'they are not a parameter-continuum procurement certificate, a new optimal-contract theorem, '
                       'or an independent interval reconstruction of Bellman operators. '
                       'The coefficient check validates reduction of deposited coefficients, not their original validity.')
    result['elapsed_seconds'] = time.perf_counter()-start
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'validator_accepted_corruption':accepted,
                      'maximum_coefficient_discrepancy':max(errors),
                      'economic_experiments':len(economics)},indent=2),flush=True)
if __name__ == '__main__': main()
