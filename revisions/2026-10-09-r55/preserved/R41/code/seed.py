"""Freeze inherited inputs without changing any historical source or clock."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for n in ('inputs','vendor/r38','audit','results','build','retained'): (R/n).mkdir(parents=True,exist_ok=True)
 old=R.parent/'2026-10-07-r38';pub=R.parent/'2026-10-07-r39'
 manifests=json.loads((pub/'audit/FILES_SHA256.json').read_text())
 for p,h in manifests.items():assert sha(ROOT/p)==h,('R39 publication',p)
 rows=json.loads((old/'results/run-1/EXECUTIONS.json').read_text());by={}
 for row in rows:
  p=old/'results/run-1/raw'/(row['id']+'.json')
  assert sha(p)==row['clock']['record_sha256'],row['id']
  s=row['specification'];key=s['kind']+'-'+s.get('name','')
  if s['kind'] in ('neural','nonlinear') and key not in by:
   by[key]=row;shutil.copyfile(p,R/'inputs'/p.name)
 shutil.copytree(old/'code',R/'vendor/r38/code',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
 (R/'inputs/INDEX.json').write_text(json.dumps(by,indent=2,sort_keys=True)+'\n')
 shutil.copyfile(pub/'audit/R39_AUDIT.json',R/'inputs/R39_AUDIT.json')
 shutil.copyfile(old/'results/run-1/EXECUTIONS.json',R/'retained/R38_EXECUTIONS.json')
 inputs={str(p.relative_to(R)):sha(p) for d in ('inputs','vendor') for p in (R/d).rglob('*') if p.is_file()}
 out=dict(r39_publication_hashes_verified=len(manifests),r38_raw_hashes_verified=len(rows),r38_scientific_services=len(rows)-1,r38_excluded_warmups=1,original_clock_replacements=0,original_service_reruns=0,source_inputs=inputs)
 (R/'audit/INHERITED_INPUTS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('Inherited inputs verified:',len(manifests),len(rows),flush=True)
if __name__=='__main__':main()
