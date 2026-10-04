"""Bind one clean source, complete study, compiled articles and preserved history."""
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
    for path,sha in old.items():
        now=ROOT/allowed.get(path,path)
        if not now.exists() or blob(now.read_bytes())!=sha:raise AssertionError('historical file not preserved: '+path)
    source_sha=source()
    if git('rev-parse','HEAD').decode().strip()!=source_sha:raise AssertionError('wrong fixed source checkout')
    changed=git('diff','--name-only',source_sha).decode().splitlines()
    for path in changed:
        if path not in ['ECTA.tex','supp.tex'] and not path.startswith('revisions/2026-10-04-r12/manuscript/table_') and not path.endswith(('results_summary.tex','full_results.tex')):raise AssertionError('source changed during execution: '+path)
    audit=json.loads((R/'results/AUDIT.json').read_text());comp=json.loads((R/'results/COMPILATION.json').read_text());tests=json.loads((R/'results/TESTS.json').read_text());inherited=json.loads((R/'results/INHERITED_TESTS.json').read_text())
    if audit['development'] or audit['source_commit']!=source_sha or tests['failures'] or tests['errors'] or not inherited['success']:raise AssertionError('not clean final evidence')
    manifest=json.loads((R/'TABLE_MANIFEST.json').read_text())
    for group in ['inputs','outputs']:
        for path,sha in manifest[group].items():
            if digest(ROOT/path)!=sha:raise AssertionError('table identity '+path)
    for item in comp.values():
        if item['undefined'] or item['multiply_defined'] or item['overfull_hbox_pt']:raise AssertionError('compilation defect')
    codefiles={str(p.relative_to(ROOT)):digest(p) for p in (R/'code').glob('*.py')}
    envs=list((R/'results').glob('*/ENVIRONMENT.json'))
    if len(envs)!=12:raise AssertionError('missing independent worker environments')
    for path in envs:
        r=json.loads(path.read_text())
        if r['source_commit']!=source_sha or r['source_files']!=codefiles or r['protocol_sha256']!=digest(R/'PROTOCOL.json'):raise AssertionError('worker executed a different source: '+str(path))
    result=dict(source_commit=source_sha,review_commit=target,base_evidence_commit=PROTOCOL['base_evidence_commit'],workflow_run_id=os.environ.get('GITHUB_RUN_ID'),workflow_attempt=os.environ.get('GITHUB_RUN_ATTEMPT'),clean_single_source_run=True,numerical_recovery_layer=False,source_manifest_exceptions=[],historical_files_preserved=len(old),prior_roots_archived_exactly=True,tests=tests,inherited_tests=inherited,compilation=comp,audit=audit,source_files=codefiles,worker_source_maps_verified=len(envs),protocol_sha256=digest(R/'PROTOCOL.json'),python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,scope='execution and identity assertions are distinct from signs of economic endpoints, method superiority and absolute continuous-time accuracy')
    write(R/'REMOTE_EXECUTION.json',result)
    excluded={'EVIDENCE_MANIFEST.json','finalize.log'}
    evidence={str(p.relative_to(ROOT)):digest(p) for p in R.rglob('*') if p.is_file() and p.suffix!='.pyc' and '__pycache__' not in p.parts and p.name not in excluded and 'development' not in p.parts}
    write(R/'EVIDENCE_MANIFEST.json',dict(source_commit=source_sha,files=evidence,excluded=['self-referential manifest','live finalize stdout','Python bytecode','development outputs']))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
