from pathlib import Path
import hashlib,json,gzip,time
from check_controlled import check
R=Path(__file__).resolve().parent.parent
start=time.perf_counter();freeze=json.loads((R/'SOURCE_FREEZE.json').read_text())
for rel,want in freeze['source_sha256'].items():
    assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==want,rel
reports=[]
for path in sorted((R/'results').glob('*.json.gz')):
    proof=json.loads(gzip.decompress(path.read_bytes()));record=json.loads(path.with_suffix('').read_text())
    assert record['proof_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    for k in ['raw','lower','upper','width','moment','restricted','target','status']:
        assert proof[k]==record[k],(path,k)
    reports.append({'path':str(path.relative_to(R)),**check(proof)})
assert len(reports)==54
out={'all_54_complete_covers_verified':True,'frozen_source_hashes_match':True,'verify_seconds':time.perf_counter()-start,'reports':reports,'scope':'New R51 proofs re-executed. R48/R50 retained proofs retain their previous verification records; no claim they were all rerun here.'}
(R/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='reports'},indent=2))
