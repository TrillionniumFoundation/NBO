"""Replay unchanged historical tests against their archived manuscript view.

Numerical modules and evidence stay at their original paths. Two historical
source-layout tests refer to ROOT/ECTA.tex or the old root bibliography; those
read an isolated view with byte-identical archived R10 roots. Current R11 source
preservation is checked independently by finalize.py, not by obsolete layout
assertions. No old test assertion or numerical input is modified.
"""
from pathlib import Path
import hashlib,json,shutil,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
bases=[ROOT/'revisions'/name for name in ['2026-09-29-r6','2026-10-03-r7','2026-10-03-r8','2026-10-03-r9','2026-10-04-r10']]
def hashes():
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for base in bases for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
for base in bases:sys.path.insert(0,str(base/'code'))
import test_r6,test_r7,test_r8,test_r9,test_r10
before=hashes();reports=[]
with tempfile.TemporaryDirectory() as tmp:
 data=Path(tmp)/'r6';shutil.copytree(bases[0]/'results',data);test_r6.OUT=data;test_r6.game.OUT=data
 view=Path(tmp)/'historical-root';view.mkdir()
 archived={'ECTA.tex':'ECTA.r10.tex','supp.tex':'supp.r10.tex','revision_reference.bib':'revision_reference.r10.bib'}
 for item in ROOT.iterdir():
  if item.name in archived:shutil.copy2(R/'archive'/archived[item.name],view/item.name)
  elif item.name!='.git':(view/item.name).symlink_to(item,target_is_directory=item.is_dir())
 view_hashes={name:hashlib.sha256((view/name).read_bytes()).hexdigest() for name in archived}
 old8,old9=test_r8.ROOT,test_r9.ROOT;test_r8.ROOT=view;test_r9.ROOT=view
 try:
  for name,cls in [('R6',test_r6.R6Tests),('R7',test_r7.R7Tests),('R8',test_r8.R8Tests),('R9',test_r9.R9Tests),('R10',test_r10.Checks)]:
   result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
   reports.append(dict(suite=name,tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),success=result.wasSuccessful()))
 finally:test_r8.ROOT=old8;test_r9.ROOT=old9
assert hashes()==before,'inherited source/evidence changed during replay'
record={'suites':reports,'history_unchanged':True,'historical_root_view':view_hashes,'compatibility_scope':'R8/R9 source-layout assertions use the byte-identical archived R10 root view. Numerical inputs and all historical assertions are unchanged. R11 preservation is checked separately by finalize.py.'}
(R/'results/INHERITED_TESTS.json').write_text(json.dumps(record,indent=2)+'\n')
if not all(r['success'] for r in reports):raise SystemExit(1)
