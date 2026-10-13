"""Run every inherited and new suite without changing scientific inputs.

Use a separate output directory when replaying the package in a full checkout;
the original local receipt is evidence and must not be overwritten.
"""
from __future__ import annotations
import argparse,json,pathlib,re,subprocess,sys,time
R=pathlib.Path(__file__).resolve().parents[1]
SUITES=['tests72','tests_publication72','tests73','tests77','tests78','tests79','tests80','tests81','tests82','tests83','tests84','tests86','tests89','tests90','tests91','tests92','tests94','tests95']

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',default='audit/current-tests95')
    args=parser.parse_args()
    A=(R/args.output_dir).resolve()
    if not A.is_relative_to(R):
        parser.error('The output directory must be inside this revision.')
    A.mkdir(parents=True,exist_ok=True)
    out={};start=time.perf_counter()
    for name in SUITES:
        t=time.perf_counter()
        p=subprocess.run([sys.executable,'code/'+name+'.py'],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (A/(name+'.log')).write_text(p.stdout)
        m=re.search(r'Ran (\d+) tests?',p.stdout)
        out[name]={'returncode':p.returncode,'tests':int(m.group(1)) if m else None,'seconds':time.perf_counter()-t,'log':str((A/(name+'.log')).relative_to(R)),'passed':p.returncode==0,'skipped':bool(re.search(r'\bskipped\b',p.stdout))}
        (A/'TESTS95.json').write_text(json.dumps(out,indent=2)+'\n')
        print(name,out[name],flush=True)
    print('total_seconds',time.perf_counter()-start,flush=True)
    return 0 if all(x['passed'] and not x['skipped'] for x in out.values()) else 1

if __name__=='__main__':
    sys.exit(main())
