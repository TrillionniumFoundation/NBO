"""Apply the narrowly identified R19 checker indexing correction, idempotently.

The release commits the corrected checker itself; this script is retained as a
transparent patch record. It does not alter witnesses or acceptance thresholds.
"""
from pathlib import Path
p=Path(__file__).with_name('verify.py')
s=p.read_text()
a="val=float(w@q);close(val,rec['value'],'first payoff');return val"
b="val=float(w@q[ids]);close(val,rec['value'],'first payoff');return val"
if a in s:
    if s.count(a)!=1:raise RuntimeError('ambiguous witness correction')
    p.write_text(s.replace(a,b))
elif b not in s:
    raise RuntimeError('unknown checker version; do not patch blindly')
print('Selected-knot evaluation uses exactly the deposited feasible indices.')
