"""Replay inherited suites without allowing their writers to alter history."""
from pathlib import Path
import hashlib,json,shutil,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
r6=ROOT/'revisions/2026-09-29-r6';r7=ROOT/'revisions/2026-10-03-r7'
def hashes():
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for base in [r6,r7] for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
sys.path.insert(0,str(r6/'code'));sys.path.insert(0,str(r7/'code'))
import test_r6,test_r7
before=hashes();reports=[]
with tempfile.TemporaryDirectory() as tmp:
 data=Path(tmp)/'results';shutil.copytree(r6/'results',data)
 test_r6.OUT=data;test_r6.game.OUT=data
 for name,cls in [('R6',test_r6.R6Tests),('R7',test_r7.R7Tests)]:
  result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
  reports.append(dict(suite=name,tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),success=result.wasSuccessful()))
assert hashes()==before,'inherited source/evidence changed during replay'
(R/'results/INHERITED_TESTS.json').write_text(json.dumps({'suites':reports,'history_unchanged':True},indent=2)+'\n')
if not all(r['success'] for r in reports):raise SystemExit(1)
