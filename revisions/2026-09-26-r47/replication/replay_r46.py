from pathlib import Path
import sys,json,time
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/"revisions/2026-09-25-r46"
O=ROOT/"revisions/2026-09-26-r47/results"
sys.path.insert(0,str(R/"replication"))
from verify_prices import verify as vp
from verify_price_tree import verify as vt
rows=[]
for p in sorted((R/"proofs").glob("*/*.json.gz")):
    start=time.perf_counter()
    record=vt(p) if p.name.startswith("price_") else vp(p)
    rows.append(dict(path=str(p.relative_to(ROOT)),**record))
    print(str(p.relative_to(ROOT)),round(time.perf_counter()-start,2),flush=True)
    (O/"r46_recheck.json").write_text(json.dumps(dict(passed=all(r["passed"] for r in rows),completed=len(rows),expected=64,results=rows),indent=2)+"\n")
