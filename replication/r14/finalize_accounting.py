"""Tighten R14 deposit accounting without solving or modifying value witnesses.

Publisher-only, explicit transformation. The read-only review command never
calls this module. The implemented grant is charged exactly as stored, and the
mechanism interval explicitly includes its separate arithmetic allowance.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'replication/r13'))
from certified_arithmetic import downward,upward
EPS=Q.from_float(1e-10)
def q(x):return Q.from_float(float(x))
def main():
    path=HERE/'output/continuum_certificate.json';data=json.loads(path.read_text());bank={r['id']:r for r in data['bank']}
    for regime in data['results']:
        inc=regime['incumbent'];r=bank[inc['id']]
        required=max(Q(0),q(r['G'])-q(r['value'])+EPS+q(.02)*q(r['F'])**2)
        if q(inc['grant'])<required:raise ValueError('implemented grant does not secure participation')
        inc['lower']=downward(q(r['A'][0])-q(inc['grant'])-q(.02)*Q(r['term']-1,8))
        regime['regret_upper']=upward(q(regime['global_upper'])-q(inc['lower']))
        regime['tolerance_met']=regime['regret_upper']<=regime['tolerance']
        if not regime['tolerance_met']:raise ValueError('tightened accounting fails regret requirement')
    data['accounting']='Executable outward-rounded grant is charged exactly; no inward transfer rounding.'
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    path=HERE/'output/economic_extensions.json';data=json.loads(path.read_text())
    if data.get('mechanism_arithmetic_allowance') != float(8*EPS):
        for row in data['mechanisms']['rows']:
            low,high=row['future_interval'];row['future_interval']=[downward(q(low)-8*EPS),upward(q(high)+8*EPS)]
        data['mechanism_arithmetic_allowance']=float(8*EPS)
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print('Charged implemented grants and explicit signed-exposure arithmetic; value witnesses unchanged.')
if __name__=='__main__':main()
