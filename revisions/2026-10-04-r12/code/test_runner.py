"""Run the new and inherited tests with durable results and historical context."""
import argparse,importlib.util,math,subprocess,sys,unittest
from common import *
import test_r12,test_extra

def run(inherited=False):
    test_r12.math=math
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(test_r12),unittest.defaultTestLoader.loadTestsFromModule(test_extra)])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    records=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),success=result.wasSuccessful(),source_commit=source())
    write(R/'results/TESTS.json',records)
    if not result.wasSuccessful():raise SystemExit(1)
    if inherited:
        # Run historical source-layout assertions on their exact reviewed roots.
        paths=['ECTA.tex','supp.tex','revision_reference.bib'];original={p:(ROOT/p).read_bytes() for p in paths}
        try:
            for p in paths:(ROOT/p).write_bytes(subprocess.check_output(['git','show',PROTOCOL['base_evidence_commit']+':'+p],cwd=ROOT))
            cmd=[sys.executable,str(ROOT/'revisions/2026-10-04-r11/code/replay_inherited.py')]
            subprocess.run(cmd,cwd=ROOT,check=True)
            for file in ['test_r11.py','test_initial_state_inputs.py']:subprocess.run([sys.executable,str(ROOT/'revisions/2026-10-04-r11/code'/file)],cwd=ROOT,check=True)
        finally:
            for p,b in original.items():(ROOT/p).write_bytes(b)
        write(R/'results/INHERITED_TESTS.json',dict(source_commit=source(),scope='Unmodified historical assertions on exact historical manuscript roots. R12 current-root preservation is separately audited against the complete review tree.',success=True))
    return records
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inherited',action='store_true');a=p.parse_args();run(a.inherited)
