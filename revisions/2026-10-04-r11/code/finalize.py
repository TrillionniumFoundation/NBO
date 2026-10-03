"""Verify preservation, source identity, and tables before publishing evidence."""
import hashlib,json,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1]
BASE='3ad498fa0647533da210f248fb6b1ebd27cffca5'

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finalize():
    source=git('rev-parse','HEAD');assert source==os.environ['NBO_SOURCE_COMMIT']
    numerical=os.environ['NBO_NUMERICAL_SOURCE_COMMIT']
    correction=json.loads((R/'POSTPROCESSING.json').read_text())
    assert correction['numerical_source_commit']==numerical
    assert correction['protocol_unchanged'] is True
    assert set(correction['source_manifest_exceptions'])=={'revisions/2026-10-04-r11/code/replay_inherited.py','revisions/2026-10-04-r11/code/finalize.py'}
    for path,digest in correction['pinned_files'].items():assert sha(ROOT/path)==digest,path
    expected={}
    for entry in subprocess.check_output(['git','ls-tree','-rz',BASE],cwd=ROOT).split(b'\0'):
        if not entry:continue
        meta,path=entry.split(b'\t',1);mode,typ,blob=meta.decode().split()
        if typ=='blob':expected[path.decode()]=blob
    roots={'ECTA.tex':'ECTA.r10.tex','supp.tex':'supp.r10.tex','revision_reference.bib':'revision_reference.r10.bib'}
    for path,blob in expected.items():
        p=R/'archive'/roots[path] if path in roots else ROOT/path
        assert p.exists(),path
        assert git('hash-object',str(p))==blob,path
    source_manifest=json.loads((R/'SOURCE_MANIFEST.json').read_text())
    for path,digest in source_manifest['files'].items():
        if path in correction['source_manifest_exceptions']:
            assert path in correction['pinned_files'];continue
        assert sha(ROOT/path)==digest,path
    assert sha(R/'PROTOCOL.json')==correction['protocol_sha256']
    original=json.loads((R/'results/INHERITED_ORIGINAL.json').read_text())
    assert [(x['suite'],x['failures'],x['errors']) for x in original['suites'] if not x['success']]==[('R8',1,0),('R9',1,0)]
    original_log=(R/'logs/inherited_original.log').read_text()
    assert 'test_13_preceding_sources_are_preserved' in original_log and 'test_12_historical_inputs_are_unchanged' in original_log
    table=json.loads((R/'TABLE_MANIFEST.json').read_text())
    for group in ['inputs','outputs']:
        for path,digest in table[group].items():assert sha(ROOT/path)==digest,path
    audit=json.loads((R/'results/AUDIT.json').read_text());comp=json.loads((R/'results/COMPILATION.json').read_text())
    assert all(not r['undefined'] and not r['multiply_defined'] and not r['overfull_hbox_pt'] for r in comp.values())
    inherited=json.loads((R/'results/INHERITED_TESTS.json').read_text());assert inherited['history_unchanged'] and all(r['success'] for r in inherited['suites'])
    newlog=(R/'logs/new_tests.log').read_text();assert newlog.rstrip().endswith('OK');count=int(re.findall(r'Ran (\d+) tests?',newlog)[-1])
    ledgers=[]
    for p in (R/'results').glob('*/EXECUTION.json'):
        record=json.loads(p.read_text());assert record['source_commit']==numerical,(p,record['source_commit'],numerical)
        assert all(r['success'] for r in record['commands']),p;ledgers.append(str(p.relative_to(ROOT)))
    assert len(ledgers)==11,ledgers
    record=dict(source_commit=source,numerical_source_commit=numerical,postprocessing=correction,original_replay=original,review_commit=BASE,base_evidence_commit='8ded2629289c4633141b9fac1aa9b41a8c1595af',workflow_run_id=os.environ['GITHUB_RUN_ID'],workflow_attempt=os.environ['GITHUB_RUN_ATTEMPT'],historical_files_preserved=len(expected)-3,prior_roots_archived_exactly=True,new_tests=count,inherited_tests=inherited,compilation=comp,audit=audit,worker_ledgers=ledgers,scope='complete reproducible revision; statistical economic guarantees remain conditional and pointwise; no universal actor superiority or missing application transfer inferred')
    (R/'REMOTE_EXECUTION.json').write_text(json.dumps(record,indent=2)+'\n')
    paths=[ROOT/'ECTA.tex',ROOT/'supp.tex',ROOT/'revision_reference.bib']+[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='EVIDENCE_MANIFEST.json']
    (R/'EVIDENCE_MANIFEST.json').write_text(json.dumps({'source_commit':source,'numerical_source_commit':numerical,'files':{str(p.relative_to(ROOT)):sha(p) for p in paths}},indent=2)+'\n')
    print(json.dumps(record,indent=2))
if __name__=='__main__':finalize()
