"""Reproduce the frozen study; every numerical call runs in its own process."""
import os,sys,json,subprocess,time,platform,hashlib
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;REPO=ROOT.parents[1]
for name in ['models','proofs','results','logs','paper/generated']:(ROOT/name).mkdir(parents=True,exist_ok=True)
def run(args):subprocess.run(args,check=True,cwd=REPO)
def cross_language():
 rows=[]
 for path in sorted((ROOT/'results').glob('*-401-highs-ds.json')):
  v=json.loads(path.read_text());proof=REPO/v['trajectory'][-1]['proof'];start=time.perf_counter()
  out=json.loads(subprocess.check_output(['node',str(HERE/'check_diffuse.mjs'),str(proof),str(ROOT/'models'/f"{v['case']}.json")],cwd=REPO))
  out['seconds']=time.perf_counter()-start;out['proof']=str(proof.relative_to(REPO));rows.append(out)
 assert len(rows)==13 and all(v['valid'] for v in rows)
 (ROOT/'results/cross-language.json').write_text(json.dumps({'checked':len(rows),'rows':rows},indent=2)+'\n')
def main():
 import numpy,scipy
 protocol=json.loads((ROOT/'PROTOCOL.json').read_text())
 for name,digest in protocol['code_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 start=time.perf_counter()
 run([sys.executable,str(HERE/'test_contracts.py')])
 run([sys.executable,str(HERE/'evaluate.py'),'study'])
 run([sys.executable,str(HERE/'evaluate.py'),'finite'])
 for case in ['warranty1','warranty2','inventory1','inventory2','queue1','queue2','ties0','ties2']:
  run([sys.executable,str(HERE/'price_audit.py'),str(REPO/'revisions/2026-09-26-r48/models'/f'{case}.json')])
 cross_language();run([sys.executable,str(HERE/'tables.py')])
 meta={'schema':'nbo-r50-evaluation-complete-v1','freeze_commit':'62585130b01f1b3479b5fc9f8ee0ee927509633a','python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,'platform':platform.platform(),'node':subprocess.check_output(['node','--version']).decode().strip(),'total_evaluation_seconds':time.perf_counter()-start,'external_preregistration':False,'retains_failures':True}
 (ROOT/'EVALUATION_COMPLETE.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':main()
