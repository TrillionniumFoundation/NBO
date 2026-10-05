"""Bind current manuscript, complete evidence tables, tests and PDF diagnostics."""
from pathlib import Path
import hashlib,json,re,platform,sys
import numpy as np
import torch
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def main():
    preserve=json.loads((R/'results/PRESERVATION.json').read_text())
    full=json.loads((R/'results/FUTURE_AUDIT.json').read_text())
    comp=json.loads((R/'results/COMPILATION.json').read_text())
    tables=json.loads((R/'results/FUTURE_TABLES.json').read_text())
    assert (full['services'],full['regime_outcomes'],full['attempt_certificates'],full['task_certificates'])==(168,840,984,319062)
    assert full['all_recorded_certificate_fields_replayed_exactly']
    assert (preserve['inherited_components_verified'],preserve['inherited_labels_retained'])==(129,408)
    assert (ROOT/'ECTA.tex').read_bytes()==(R/'ECTA.tex').read_bytes()
    assert (ROOT/'supp.tex').read_bytes()==(R/'supp.tex').read_bytes()
    tests={}
    for name in ['UNIT_TESTS','INHERITED_TESTS']:
        txt=(R/f'results/{name}.log').read_text()
        assert re.search(r'^OK\s*$',txt,re.M),name+' contains failures or skips'
        assert 'skipped' not in txt and 'FAILED' not in txt,name
        tests[name]=int(re.search(r'Ran (\d+) tests',txt)[1])
    assert tests=={'UNIT_TESTS':22,'INHERITED_TESTS':34}
    for doc in comp['documents']:
        assert not any(doc[k] for k in ['undefined','multiply_defined','duplicate_destination','missing_character'])
        assert not doc['overfull_hbox']
        assert all(x<1 for x in doc['overfull_vbox'])
        assert hashlib.sha256((R/f"build/{doc['document']}.pdf").read_bytes()).hexdigest()==doc['pdf_sha256']
    maps=json.loads((R/'protocols/RESPONSE_MAP.json').read_text())
    assert {x['comment'] for x in maps}=={f'B{i}' for i in range(1,9)}|{f'M{i}' for i in range(1,11)}
    names=set(preserve['live_components'])
    for p in R.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and 'transport' not in p.parts and p.suffix in {'.py','.tex','.bib','.md'}:
            names.add(str(p.relative_to(ROOT)))
    for n in ['econsocart.cls','econsocart.cfg','ecta-fullname.bst','revision_reference.bib','revisions/2026-10-05-r19-integrated/references.bib']:
        names.add(n)
    hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in sorted(names)}
    result=dict(base_commit=preserve['base_commit'],reviewed_commit='20afc6c1c4828e3c469e7906366bcc8730cc04d0',
        tests=tests,inherited_components=129,inherited_labels=408,publication_labels=preserve['publication_labels'],
        frozen_services=168,frozen_future_outcomes=840,attempt_certificates_replayed=984,
        task_certificates_replayed=319062,additional_zero_charge_certificates_replayed=120,
        full_arithmetic_audit=full,documents=comp['documents'],response_items=len(maps),source_sha256=hashes,
        environment=dict(python=sys.version,numpy=np.__version__,torch=torch.__version__,platform=platform.platform()),
        chronology='R19/R20 are inherited frozen executions. R21 theorem checks, certificate replay, reorganization and economic bands introduce no new fitting observations or replacement scientific clocks.',
        scope='Finite-law economic certificates are distinct from the uniform assumptions and transfer allowances of the policy-composition theorem.')
    (R/'results/RELEASE_AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','full_arithmetic_audit','environment']},indent=2))
if __name__=='__main__':main()
