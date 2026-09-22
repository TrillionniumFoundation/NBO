"""Fail-closed, failure-preserving collector. It writes evidence BEFORE failing.
Each input folder is an exact planned cell, not a discovered successful subset.
"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, shutil
from fractions import Fraction
ROOT = pathlib.Path(__file__).resolve().parents[3]; REV = ROOT/'revisions/2026-09-22-r10'
def finite(x):
    if isinstance(x, dict): return all(finite(v) for v in x.values())
    if isinstance(x, list): return all(finite(v) for v in x)
    return not isinstance(x, float) or math.isfinite(x)
def read(path):
    v = json.loads(path.read_text())
    if not finite(v): raise ValueError('nonfinite value in '+str(path))
    return v
def check_cell(cell, k, source, frozen):
    tag = f'k{k:g}'; s = read(cell/'status.json')
    assert s['status'] == 'success', 'run did not succeed'
    assert s['cell'] == tag and s['source_commit'] == source, 'wrong cell/source'
    for name, h in s['files'].items():
        assert pathlib.PurePosixPath(name).name == name and '..' not in name
        assert hashlib.sha256((cell/name).read_bytes()).hexdigest() == h, 'output hash mismatch'
    for stem in ('actor', 'dual_pilot'):
        name = f'{stem}_{tag}.json'
        assert (cell/name).read_bytes() == (frozen/name).read_bytes(), 'frozen input changed'
    p = read(cell/f'policy_certificate_{tag}.json'); d = read(cell/f'flexible_dual_{tag}.json')
    assert d['status'] == 'complete' and d['planned_resolutions'] == [[4,64],[8,128],[16,256]]
    assert [r['cells_per_slab'] for r in p['records']] == [64,256,1024]
    assert [r['source_boxes'] for r in d['records']] == [4096,16384,65536]
    assert p['original_payoff'] and d['original_payoff'] and d['original_continuous_actions'] and d['original_stopping_contract']
    assert p['initial'] == d['initial'] == [0,2,1.25] and p['k'] == d['k'] == k
    assert p['terminal_wealth_interval'][0] > .5 and p['exit_payoff_correction_upper'] > 0
    L, U = p['records'][-1]['policy_value_interval']; r = d['records'][-1]
    assert L < U <= r['optimal_value_upper']
    assert Fraction(r['certified_regret_upper']) >= Fraction(r['optimal_value_upper']) - Fraction(L)
    assert Fraction(r['certified_regret_upper']) < Fraction('.01') and r['target_met']
    assert d['primitive_checks']['supporting_plane_verified']
    assert all(q['variance_allowance_upper'] > 0 and q['localization_upper'] > 0 and q['source_taylor_remainder_upper'] > 0 and q['covariance_correction_interval'][1] < 0 for q in d['records'])
    # This is a cross-environment regression check, not an error allowance.
    oldp = read(frozen/f'policy_certificate_{tag}.json'); oldd = read(frozen/f'flexible_dual_{tag}.json')
    deltas = [abs(L-oldp['records'][-1]['policy_value_interval'][0]), abs(r['optimal_value_upper']-oldd['records'][-1]['optimal_value_upper'])]
    assert max(deltas) < 1e-10, 're-execution materially differs from frozen tables'
    return {'status': 'success', 'policy_value_interval': [L,U], 'optimal_value_upper': r['optimal_value_upper'],
            'certified_regret_upper': r['certified_regret_upper'], 'maximum_endpoint_difference_from_frozen': max(deltas), 'target_met': True}
def collect(downloads, destination, source, frozen=None):
    downloads=pathlib.Path(downloads); destination=pathlib.Path(destination)
    frozen=pathlib.Path(frozen) if frozen else REV/'results'
    destination.mkdir(parents=True,exist_ok=True); rows=[]
    for k in (.5,2.,8.):
        tag=f'k{k:g}'; src=downloads/f'r10-cell-{tag}'; target=destination/tag
        row={'cell':tag,'cost':k,'source_commit':source,'status':'missing'}
        if src.is_dir():
            shutil.copytree(src,target,dirs_exist_ok=True)
            try: row.update(check_cell(target,k,source,frozen))
            except Exception as exc:
                row.update(status='invalid', reason=type(exc).__name__+': '+str(exc))
        else: target.mkdir(parents=True,exist_ok=True); row['reason']='planned artifact not returned'
        (target/'collection_status.json').write_text(json.dumps(row,indent=2,allow_nan=False)+'\n')
        rows.append(row)
    result={'source_commit':source,'planned_cells':['k0.5','k2','k8'],'cells':rows,
            'status':'PASS' if all(r['status']=='success' for r in rows) else 'FAIL',
            'preservation':'Every planned cell represented; raw returned files retained, including failures and nonfinite files',
            'scope':'Independent re-execution of new original-economy certificates; not new external training'}
    (destination/'ci_recheck.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--downloads',required=True);p.add_argument('--destination',required=True);p.add_argument('--source',required=True);p.add_argument('--preserve-only',action='store_true');a=p.parse_args()
    r=collect(a.downloads,a.destination,a.source);print(json.dumps(r,indent=2))
    if r['status']!='PASS' and not a.preserve_only: raise SystemExit(1)
