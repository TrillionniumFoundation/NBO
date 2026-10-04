"""Run new and inherited tests without changing historical evidence files."""
import argparse,math,re,subprocess,sys,unittest
from common import *
import test_r13,test_extra,test_extensions

def run(inherited=False):
    test_r13.math=math
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(test_r13),unittest.defaultTestLoader.loadTestsFromModule(test_extra),unittest.defaultTestLoader.loadTestsFromModule(test_extensions)])
    result=unittest.TextTestRunner(verbosity=2).run(suite);records=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),success=result.wasSuccessful(),source_commit=source())
    write(R/'results/TESTS.json',records)
    if not result.wasSuccessful():raise SystemExit(1)
    if inherited:
        roots=['ECTA.tex','supp.tex','revision_reference.bib','README.md'];generated=ROOT/'revisions/2026-10-04-r11/results/INHERITED_TESTS.json'
        original={ROOT/p:(ROOT/p).read_bytes() for p in roots};original[generated]=generated.read_bytes();reports=[]
        logdir=R/'logs';logdir.mkdir(exist_ok=True)
        try:
            for p in roots:(ROOT/p).write_bytes(subprocess.check_output(['git','show',PROTOCOL['base_evidence_commit']+':'+p],cwd=ROOT))
            for name in ['replay_inherited.py','test_r11.py','test_initial_state_inputs.py']:
                proc=subprocess.run([sys.executable,str(ROOT/'revisions/2026-10-04-r11/code'/name)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                (logdir/('inherited_'+name+'.log')).write_text(proc.stdout);print(proc.stdout[-1500:])
                reports.append(dict(script=name,returncode=proc.returncode,tests=sum(map(int,re.findall(r'Ran (\d+) tests?',proc.stdout)))))
                if proc.returncode:raise RuntimeError('historical suite failed: '+name)
            detail=json.loads(generated.read_text())
        finally:
            for p,b in original.items():p.write_bytes(b)
        write(R/'results/INHERITED_TESTS.json',dict(source_commit=source(),tests=sum(r['tests'] for r in reports),reports=reports,historical_details=detail,scope='Unmodified historical assertions on exact reviewed roots; every generated historical file restored byte for byte. R13 preservation is separately audited against the review tree.',success=True))
    return records
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inherited',action='store_true');a=p.parse_args();run(a.inherited)
