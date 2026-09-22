"""Original-economy control ranges for the six unrestricted comparators and
all twenty fresh price-library policies. The ranges concern exact mathematical
controls, not a floating-point deployment program.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from objective_bridge import ROOT,R17,R16,HERE,M

def run():
    rows=[];bounds=[('.05','.8'),('-.2','.2'),('-.5','.8')]
    for method in ['markov_chain','semi_lagrangian']:
      for n in [9,17,25]:
        p=R17/'results/unrestricted'/f'{method}_{n}.npz'
        with np.load(p) as f:pol=f['policy']
        if not np.all(pol[:,:,-1,2]==0):raise AssertionError('Nonzero upper-face portfolio')
        axes=tuple(range(pol.ndim-1));lo=pol.min(axis=axes);hi=pol.max(axis=axes)
        v=[M.exact_clip(M.I(lo[k],hi[k]),*bounds[k]).pair() for k in range(3)]
        rows.append({'method':method,'n':n,'full_domain_control_ranges':v,
                     'policy_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                     'scope':'Original-action clipping of exact-real bilinear state interpolants, constant per time step; convex-combination range proof; no portfolio-distance multiplier',
                     'upper_face_portfolio_exact_zero':True})
    paths=sorted((R16/'results/fresh_library').glob('actor_k*.json'))
    if len(paths)!=20:raise AssertionError('Incomplete price library')
    cs=[];ts=[];hashes={}
    for p in paths:
        d=json.loads(p.read_text());c=np.array(d['c']);t=np.array(d['theta'])
        # Strict separation checks sufficient for all exact dyadic constants.
        if np.any(c<M.I.rational('.05').hi) or np.any(c>M.I.rational('.8').lo):raise AssertionError('Consumption outside original bounds')
        if np.any(t<M.I.rational('-.2').hi) or np.any(t>M.I.rational('.2').lo):raise AssertionError('Adjustment outside original bounds')
        cs.extend(c);ts.extend(t);hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    library={'method':'fresh_time_control_library','nodes':20,'full_price_time_control_ranges':[[float(min(cs)),float(max(cs))],[float(min(ts)),float(max(ts))],[0.,0.]],
             'scope':'Any policy selected by the certified library selector, all k in [.5,8], all times before the original stopping time; exact stored dyadic controls',
             'input_sha256':hashes}
    result={'status':'PASS','classical':rows,'fresh_library':library,'mathematical_justification':'A bilinear interpolant is a convex combination of its four node values. Original-action clipping is monotone and preserves these interval ranges. A finite time/price selector chooses one of the fully enumerated controls.'}
    out=HERE.parent/'results/control_ranges.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
