"""Bind the clean source, complete study, compiled articles and preserved history."""
from __future__ import annotations
import platform,subprocess
from common import *

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
    target=PROTOCOL['review_commit'];old={}
    for line in git('ls-tree','-r',target).decode().splitlines():
        meta,path=line.split('\t',1);mode,kind,sha=meta.split()
        if kind=='blob':old[path]=sha
    allowed={'ECTA.tex':'revisions/2026-10-04-r12/archive/ECTA.r11.tex','supp.tex':'revisions/2026-10-04-r12/archive/supp.r11.tex','README.md':'revisions/2026-10-04-r12/archive/README.r11.md'}
    count=0
    for path,sha in old.items():
        now=ROOT/(allowed.get(path,path))
        if not now.exists() or blob(now.read_bytes())!=sha:raise AssertionError('historical file not preserved: '+path)
        count+=1
    source_sha=source()
    if git('rev-parse','HEAD').decode().strip()!=source_sha:raise AssertionError('wrong fixed source checkout')
    changed=git('diff','--name-only',source_sha).decode().splitlines()
    for path in changed:
        if path not in ['ECTA.tex','supp.tex'] and not path.startswith('revisions/2026-10-04-r12/manuscript/table_') and not path.endswith(('results_summary.tex','full_results.tex')):raise AssertionError('source changed during execution: '+path)
    audit=json.loads((R/'results/AUDIT.json').read_text());comp=json.loads((R/'results/COMPILATION.json').read_text());tests=json.loads((R/'results/TESTS.json').read_text())
    if audit['development'] or audit['source_commit']!=source_sha or tests['failures'] or tests['errors']:raise AssertionError('not clean final evidence')
    manifest=json.loads((R/'TABLE_MANIFEST.json').read_text())
    for group in ['inputs','outputs']:
        for path,sha in manifest[group].items():
            if digest(ROOT/path)!=sha:raise AssertionError('table identity '+path)
    for item in comp.values():
        if item['undefined'] or item['multiply_defined'] or item['overfull_hbox_pt']:raise AssertionError('compilation defect')
    codefiles={str(p.relative_to(ROOT)):digest(p) for p in (R/'code').glob('*.py')}
    result=dict(source_commit=source_sha,review_commit=target,base_evidence_commit=PROTOCOL['base_evidence_commit'],workflow_run_id=os.environ.get('GITHUB_RUN_ID'),workflow_attempt=os.environ.get('GITHUB_RUN_ATTEMPT'),clean_single_source_run=True,numerical_recovery_layer=False,source_manifest_exceptions=[],historical_files_preserved=count,prior_roots_archived_exactly=True,tests=tests,compilation=comp,audit=audit,source_files=codefiles,protocol_sha256=digest(R/'PROTOCOL.json'),python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,scope='execution and identity assertions are distinct from signs of economic endpoints, method superiority and absolute continuous-time accuracy')
    write(R/'REMOTE_EXECUTION.json',result)
    evidence={str(p.relative_to(ROOT)):digest(p) for p in R.rglob('*') if p.is_file() and p.suffix not in ['.pyc'] and '__pycache__' not in p.parts and p.name!='EVIDENCE_MANIFEST.json' and 'development' not in p.parts}
    write(R/'EVIDENCE_MANIFEST.json',dict(source_commit=source_sha,files=evidence));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
