"""Pin the executed R18 publication; never infer a publication hash recursively."""
from pathlib import Path
import hashlib,json,os,platform,subprocess
import numpy,scipy,torch
from objective_bridge import ROOT,validate_inputs
BASE='982326994c8550db4e039d915c225a9ace8e3044'
PREFIX='revisions/2026-09-23-r18/'
NAMES={n+e for n in ['ECTA_R18','SUPP_R18','RESPONSE_R18'] for e in ['.tex','.pdf']}|{'R18_REVIEW.md'}

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def allowed(p):return p in NAMES or p.startswith(PREFIX) or p.startswith('.github/workflows/r18-')

def main():
    source=os.environ.get('R18_SOURCE_COMMIT',git('rev-parse','HEAD'))
    diff=git('diff','--name-status','--no-renames',BASE).splitlines()
    rows=[]
    for line in diff:
        status,path=line.split('\t',1)
        if status!='A' or not allowed(path):raise RuntimeError('Historical tree changed: '+line)
        rows.append({'status':status,'path':path})
    validation=json.loads((ROOT/PREFIX/'results/validation.json').read_text())
    build=json.loads((ROOT/PREFIX/'build_logs/pdf_validation.json').read_text())
    bridge=json.loads((ROOT/PREFIX/'results/objective_bridge/objective_bridge_summary.json').read_text())
    if validation['status']!='PASS' or build['status']!='PASS':raise RuntimeError('Failed validation')
    files={}
    paths=[ROOT/p for p in NAMES]+list((ROOT/PREFIX).rglob('*'))
    for p in sorted(set(paths)):
        if not p.is_file() or '__pycache__' in p.parts or 'bootstrap' in p.parts or p.name=='PUBLICATION_MANIFEST.json':continue
        if p.suffix in {'.pyc','.so','.aux','.out','.brf'}:continue
        files[str(p.relative_to(ROOT))]={'sha256':sha(p),'bytes':p.stat().st_size}
    result={'revision':'R18','review_commit':'82af00bc296da59e8a3a28ef1bf86c1d6fca2367','reviewed_R16_commit':'2932b74dad6d8d9efce5a114d5098a99ea17ab1f','scientific_input_commit':BASE,'new_source_commit':source,'publication_commit_rule':'The containing commit with this manifest and the PDFs is the publication commit; no self-referential hash is embedded.','workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'execution_scope':'New R18 objective/evidence audit and publication; inherited R17 training is not relabeled as newly run.','historical_tracked_files_changed':False,'new_tracked_paths':rows,'immutable_inputs':validate_inputs(),'environment':{'python':platform.python_version(),'platform':platform.platform(),'numpy':numpy.__version__,'scipy':scipy.__version__,'torch':torch.__version__,'mpfr':validation['arithmetic']['mpfr_version']},'validation':validation,'pdf_validation':build,'objective_audit':bridge,'original_neural_target':.01,'original_neural_target_attained':False,'files':files}
    path=ROOT/PREFIX/'PUBLICATION_MANIFEST.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'manifest':str(path.relative_to(ROOT)),'hashed_files':len(files),'historical_files_changed':False,'source_commit':source},indent=2))
if __name__=='__main__':main()
