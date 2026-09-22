"""Exact deployment admissibility and immutable input identity checks."""
from __future__ import annotations
import hashlib,json,pathlib
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-22-r10'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check_actor(d):
    assert d['initial']==[0,2,1.25] and d['original_payoff'] is True
    assert len(d['c'])==len(d['theta'])==len(d['p'])==16
    assert all(Fraction('.05')<=Fraction(v)<=Fraction('.8') for v in d['c'])
    assert all(Fraction(0)<=Fraction(v)<=Fraction('.2') for v in d['theta'])
    assert all(v==0 for v in d['p'])
    return True

def run():
    m=json.loads((REV/'frozen_inputs.json').read_text())
    for path,h in m['files'].items():assert sha(ROOT/path)==h, path
    for k in [.5,2,8]:
        d=json.loads((REV/f'results/actor_k{k:g}.json').read_text());check_actor(d)
        d=json.loads((REV/f'results/dual_pilot_k{k:g}.json').read_text())
        assert len(d['theta'])==16 and 1.2<d['y0']<2.4
        assert all(Fraction(0)<=Fraction(v)<=Fraction('.2') for v in d['theta'])
    return {'status':'PASS','input_files':len(m['files']),'exact_decimal_admissibility':True}
if __name__=='__main__':print(json.dumps(run(),indent=2))
