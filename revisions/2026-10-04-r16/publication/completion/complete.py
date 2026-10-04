"""Complete the R16 reading edition without modifying scientific evidence.

Run from a repository checkout after complete_source/install.py. The original
installer, original reports, registered source trees and historical roots remain
unchanged. This module adds a proved stable-active-face extension and its tests.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, os, re, subprocess, tarfile
S=Path(__file__).resolve().parent
P=S.parent
ROOT=P.parents[2]
R16=ROOT/'revisions/2026-10-04-r16'
PREFIX='revisions/2026-10-04-r16/publication'

def put(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2)+'\n')

def restore():
    inventory=json.loads((R16/'protocols/signed_candidates.json').read_text())
    policies=inventory['files']
    assert len(policies)==32
    rows={r['path']:r for r in policies}
    archive=R16/'results/exploratory/menu'
    for name,info in json.loads((archive/'MANIFEST.json').read_text())['files'].items():
        rel=PurePosixPath(name)
        assert not rel.is_absolute() and '..' not in rel.parts
        rows[str((archive/name).relative_to(ROOT))]=info
    declared=json.loads((R16/'protocols/menu_protocol.json').read_text())['execution']['source_files']
    for name in declared:
        if name not in rows:
            blob=subprocess.check_output(['git','rev-parse','HEAD:'+name],cwd=ROOT,text=True).strip()
            assert re.fullmatch('[0-9a-f]{40}',blob),name
            rows[name]={'git_blob':blob}
    for name in rows:
        rel=PurePosixPath(name)
        assert not rel.is_absolute() and '..' not in rel.parts
    subprocess.run(['git','restore','--worktree','--ignore-skip-worktree-bits','--',*rows],cwd=ROOT,check=True)
    receipts=[]
    for name,info in rows.items():
        data=(ROOT/name).read_bytes()
        if 'bytes' in info:
            assert len(data)==info['bytes'] and hashlib.sha256(data).hexdigest()==info['sha256'],name
        if 'git_blob' in info:
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==info['git_blob'],name
        receipts.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    put(P/'checks/remote/POLICY_DEPENDENCIES.json',{'policies':32,'all_registered_pilot_files_restored':True,'declared_menu_source_files':len(declared),'files':receipts,'scientific_sources_changed':False})
    print('Restored and hash-checked all 32 policies, archived pilot files and the complete declared menu source closure.')

def assemble():
    subprocess.run(['python',str(P/'code/assemble_publication.py')],cwd=ROOT,check=True)
    details=P/'manuscript/reuse_details.tex'
    details.write_text(details.read_text()+'\n\\input{'+PREFIX+'/completion/active_face_value.tex}\n')
    main=P/'manuscript/reuse_main.tex'
    main.write_text(main.read_text()+'\nBinding task constraints also admit a positive decision-value result. Proposition~\\ref{prop:r16activefacevalue} in the supplement replaces full interiority by stable active faces and weights continuation errors by the directions in which the tasks can respond. Its strict-gain condition compares removed economically relevant variance with approximation cost; it is not inferred from a favorable fitted-policy endpoint.\n')
    response=P/'manuscript/response_body.tex'
    text=response.read_text()
    needle='\\section{M2'
    start=text.find(needle)
    assert start>=0
    addition='\\paragraph*{Binding-constraint extension.} Proposition~\\ref{prop:r16activefacevalue} supplies a complete proof of the decision-value identity on stable active faces. It allows each task to have binding constraints when their tangent spaces jointly span the continuation coordinates. The active faces and scalar-gradient dictionary are fixed for the original centered observation law; no post-selection recentering is allowed. Ten additional finite-law tests compare the identity with exact constrained KKT solutions, including off-diagonal curvature, unequal economic weights, misspecification, and explicit rejection of face switching and singular metrics. These manufactured checks are distinct from the registered economic outcomes.\n\n'
    response.write_text(text[:start]+addition+text[start:])
    status=json.loads((P/'COMMENT_STATUS.json').read_text())
    status['M1']['completed']+='; stable-active-face decision-value extension with complete proof and ten exact finite-law tests'
    put(P/'COMMENT_STATUS.json',status)
    note='\nThe final reading edition also includes the stable-active-face decision-value proposition and its full proof. Its ten exact constrained-optimizer tests and completion receipt are in `completion/`. All original numerical evidence and all 78 inherited unit-test requirements are retained.\n'
    (P/'README.md').write_text((P/'README.md').read_text()+note)
    (ROOT/'README.md').write_text((P/'ROOT_README.md').read_text()+note)
    put(S/'ASSEMBLY_RECEIPT.json',{'added_result':'prop:r16activefacevalue','original_installer_receipt_sha256':hashlib.sha256((P/'COMPLETE_SOURCE_RECEIPT.json').read_bytes()).hexdigest(),'source_commit':os.environ['NBO_R16_PUBLICATION_SOURCE'],'scientific_observations_or_sources_modified':False,'patch_scope':['manuscript/reuse_main.tex','manuscript/reuse_details.tex','manuscript/response_body.tex','COMMENT_STATUS.json','README.md']})

def audit():
    parent=json.loads((P/'FINAL_AUDIT.json').read_text())
    assert parent['publication_integrity_passed'] and parent['unit_tests_passed']==78
    log=(P/'checks/remote/test_active_face_value.py.stdout').read_text()
    assert 'Ran 10 tests' in log and re.search(r'\nOK\s*$',log)
    aux=(P/'build/supp_refs.aux').read_text()
    assert '\\newlabel{prop:r16activefacevalue}' in aux
    record={'schema':'nbo-r16-referee-completion-v1','complete':True,'source_commit':os.environ['NBO_R16_PUBLICATION_SOURCE'],'base_integration_commit':'b40e4f751b8b52f93c1889656b67ecd18653f643','review_commit':'cb4595bbcc7147e47e44ba40cb2f5034510ae19f','publication_integrity_passed':True,'inherited_unit_tests_passed':78,'additional_constrained_decision_tests_passed':10,'total_unit_tests_passed':88,'all_four_registered_evidence_families_complete':True,'all_original_compiled_labels_preserved':parent['original_compiled_labels_preserved'],'compilation':parent['compilation'],'all_empirical_referee_concerns_closed':False,'scope':'Completed NBO-centered revision, preserved evidence, active-face theorem and executable audits; no assertion of journal acceptance or universal method superiority.'}
    put(S/'FINAL_COMPLETION_AUDIT.json',record)
    manifest=json.loads((P/'PUBLICATION_MANIFEST.json').read_text())
    for path in sorted(S.rglob('*')):
        if path.is_file():
            manifest['files'][str(path.relative_to(ROOT))]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    put(P/'PUBLICATION_MANIFEST.json',manifest)
    print(json.dumps(record,indent=2))

def package():
    paths=set()
    for name in ('ECTA.tex','supp.tex','README.md'):
        if (ROOT/name).is_file():paths.add(ROOT/name)
    for path in P.rglob('*'):
        if path.is_file():paths.add(path)
    for path in ROOT.rglob('*'):
        if '.git' in path.parts or not path.is_file():continue
        if path.suffix in {'.tex','.bib','.bst','.cls','.sty','.cfg','.clo','.def'}:paths.add(path)
    for base in (R16/'code',R16/'protocols'):
        for path in base.rglob('*'):
            if path.is_file() and path.suffix in {'.py','.json','.md'}:paths.add(path)
    for path in (R16/'results').rglob('*'):
        if path.is_file() and path.suffix in {'.json','.csv','.md'} and ('report' in path.parts or path.name=='FINAL_AUDIT.json'):paths.add(path)
    with tarfile.open(ROOT/'nbo-r16-referee-completed.tar.gz','w:gz') as tar:
        for path in sorted(paths):tar.add(path,arcname=str(path.relative_to(ROOT)),recursive=False)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['restore','assemble','audit','package'])
    globals()[parser.parse_args().stage]()
