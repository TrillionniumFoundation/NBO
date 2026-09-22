"""Build the exact R8 review artifacts; no reconstruction capsule or retraining.

Requirements: Python 3.11+, NumPy, a LaTeX distribution with the packages used
by ECTA_R8.tex, and pdflatex. The repository retains econsocart support files.
"""
from __future__ import annotations
import hashlib,json,os,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE=ROOT/'revisions/2026-09-22-r8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def command(args,**kw):return subprocess.run(args,cwd=ROOT,check=True,**kw)
def git_value(*args):
    try:return subprocess.check_output(['git',*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError,FileNotFoundError):return None

def run():
    for path in ['ECTA_R8.tex','SUPP_R8.tex','revisions/2026-09-22-r8/RESPONSE_TO_REFEREE.md']:
        assert (ROOT/path).is_file(),f'Missing canonical plaintext source: {path}'
    command([sys.executable,str(BASE/'replication/validate_evidence.py')])
    command([sys.executable,str(BASE/'replication/assemble_tables.py')])
    logs=BASE/'build_logs';logs.mkdir(exist_ok=True)
    for stem in ['ECTA_R8','SUPP_R8']:
        for iteration in range(3):
            with (logs/f'{stem}_pass{iteration+1}.txt').open('w') as f:
                command(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',stem+'.tex'],stdout=f,stderr=subprocess.STDOUT)
        text=(ROOT/f'{stem}.log').read_text(errors='replace')
        if re.search(r'There were undefined references|Citation .* undefined|Reference .* undefined|multiply-defined labels',text):
            raise RuntimeError(f'Unresolved citations/references in {stem}.log')
        assert (ROOT/f'{stem}.pdf').stat().st_size>10000
    source_commit=git_value('rev-parse','HEAD') or os.environ.get('NBO_BUILD_SOURCE_SHA')
    if not source_commit:
        p=ROOT/'R8_REVIEW_SOURCE_COMMIT.txt'
        source_commit=p.read_text().strip() if p.exists() else 'unversioned-container-copy'
    tracked=git_value('ls-files','-z')
    if tracked:
        files=[ROOT/p for p in tracked.split('\0') if p]
    else:
        files=[p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts]
    # Include newly generated tables even on a source checkout before delivery.
    files+=list((BASE/'paper/tables').glob('*.tex'))
    ignored={BASE/'build_manifest.json',BASE/'validation_report.json',ROOT/'ECTA_R8.pdf',ROOT/'SUPP_R8.pdf'}
    inputs={}
    for p in sorted(set(files)):
        rel=p.relative_to(ROOT)
        if p in ignored or not p.is_file() or 'build_logs' in rel.parts or '__pycache__' in rel.parts:continue
        if p.suffix in {'.aux','.log','.out','.toc','.fls','.fdb_latexmk'}:continue
        inputs[str(rel)]=sha(p)
    evidence=json.loads((BASE/'results/execution_manifest.json').read_text())
    manifest={'build_source_commit':source_commit,
        'build_run_id':os.environ.get('GITHUB_RUN_ID'),
        'numerical_execution_source_commit':evidence['source_commit'],
        'numerical_execution_run_id':evidence['run_id'],
        'author_implementation_commit':evidence['author_commit'],
        'canonical_sources':['ECTA_R8.tex','SUPP_R8.tex','revisions/2026-09-22-r8/RESPONSE_TO_REFEREE.md'],
        'source_and_evidence_sha256':inputs,
        'outputs_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'ECTA_R8.pdf',ROOT/'SUPP_R8.pdf',BASE/'validation_report.json']},
        'tex_engine':subprocess.check_output(['pdflatex','--version'],text=True).splitlines()[0],
        'python':sys.version,
        'validation':'Source/output hashes, complete cells, paired raw-array statistics and correction shares checked; both manuscripts compiled three times without unresolved references.',
        'identity_note':'The delivery commit adds generated files. This manifest binds the exact input commit built, not its own future commit hash.',
        'precision_note':'The original-payoff continuous NDU bounds remain above target. A successful build is not a claim that all scientific gaps are closed.'}
    (BASE/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['build_source_commit','numerical_execution_source_commit','outputs_sha256']},indent=2))
if __name__=='__main__':run()
