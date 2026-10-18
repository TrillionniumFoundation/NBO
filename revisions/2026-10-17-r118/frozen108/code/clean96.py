"""Second clean current-document build and byte identity, with retained logs."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
def dig(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=('ECTA','supp','appendix','response')
before={n:dig(R/f'build/{n}.pdf') for n in names}
p=subprocess.run([sys.executable,str(R/'code/build95.py'),'--audit-dir','audit/reproduction96/clean-build'])
after={n:dig(R/f'build/{n}.pdf') for n in names}
record=dict(first=before,clean=after,passed=p.returncode==0 and before==after)
(R/'audit/reproduction96/CLEAN96.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
if not record['passed']:raise RuntimeError('Clean PDF identity failed')
