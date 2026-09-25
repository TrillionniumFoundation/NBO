"""Development-only adapter test, never part of untouched evaluation."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,gzip
import global_solver as core
from scip_baseline import solve
from verify_tree import Reader
HERE=Path(__file__).resolve().parents[1]
d=core.old.model(430001,3,4,3,'19/20','1/100')
o=solve(d,seconds=20,nodes=255,logfile=HERE/'history'/'scip_development.log')
p=HERE/'history'/'scip_development.json.gz';core.save(o,p)
s=json.loads(gzip.decompress(p.read_bytes()));c,regret=Reader(s['model'],True).policy(s['policy'])
assert c==F(s['verified_candidate_upper'])
(HERE/'history'/'scip_development.json').write_text(json.dumps(dict(summary=o['summary'],checked_upper=str(c),checked_max_regret=str(regret),purpose='development interface check; not a prospective environment'),indent=2)+'\n')
print(json.dumps(o['summary'],indent=2))
