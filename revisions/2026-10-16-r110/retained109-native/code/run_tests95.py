"""Replay all eighteen inherited current suites and every new R96 suite.

Original receipts remain immutable; each execution writes its own audit path.
The final aggregate includes the new tests, not only their pre-freeze run.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,subprocess,sys,time
R=pathlib.Path(__file__).resolve().parents[1]
INHERITED=['tests72','tests_publication72','tests73','tests77','tests78','tests79','tests80','tests81','tests82','tests83','tests84','tests86','tests89','tests90','tests91','tests92','tests94','tests95']

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',default='audit/reproduction96/tests')
    args=parser.parse_args();A=(R/args.output_dir).resolve()
    if not A.is_relative_to(R):parser.error('Output directory must be inside this revision')
    A.mkdir(parents=True,exist_ok=True)
    suites=INHERITED+sorted(p.stem for p in (R/'code').glob('tests*96.py') if p.stem not in INHERITED)
    if not {'tests96','tests_preservation96'}.issubset(suites):raise RuntimeError('New revision suites missing')
    out={};start=time.perf_counter()
    for name in suites:
        t=time.perf_counter();path=R/'code'/(name+'.py')
        p=subprocess.run([sys.executable,str(path)],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (A/(name+'.log')).write_text(p.stdout)
        m=re.search(r'Ran (\d+) tests?',p.stdout);n=int(m[1]) if m else 0
        failures=re.search(r'failures=(\d+)',p.stdout);errors=re.search(r'errors=(\d+)',p.stdout)
        out[name]={'returncode':p.returncode,'tests':n,'seconds':time.perf_counter()-t,
          'log':str((A/(name+'.log')).relative_to(R)),
          'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'passed':p.returncode==0 and n>0,'skipped':bool(re.search(r'\bskipped\b',p.stdout)),
          'failures':int(failures[1]) if failures else 0,'errors':int(errors[1]) if errors else 0}
        (A/'TESTS95.json').write_text(json.dumps(out,indent=2)+'\n')
        print(name,out[name],flush=True)
    print('total_seconds',time.perf_counter()-start,flush=True)
    return 0 if all(x['passed'] and not x['skipped'] for x in out.values()) else 1
if __name__=='__main__':sys.exit(main())
