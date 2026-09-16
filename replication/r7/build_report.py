#!/usr/bin/env python3
"""Verify delivered manuscripts, source identities, outputs and protected history."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE='10a7cbee28de5126d844dea9eae8c36c5cda9e9b'
REV=ROOT/'revisions/2026-09-16-r7';OUT=ROOT/'replication/r7/output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def allowed(p):return p in {'ECTA_R7.tex','SUPP_R7.tex','REVISION_INDEX.md','.github/workflows/revision-r7.yml'} or p.startswith(('replication/r7/','revisions/2026-09-16-r7/'))
def run(source,local=False):
    env=json.loads((OUT/'environment.json').read_text());assert env['source_commit']==source
    inventory=json.loads((REV/'source_inventory.json').read_text())
    for p,digest in inventory.items():assert sha(ROOT/p)==digest,p
    for name in ('validation','primitive','decision','decision_replay','matched','adaptive','publication_tables'):
        assert (OUT/f'{name}.json').is_file(),name
    decision=json.loads((OUT/'decision.json').read_text());assert decision['minimum_adjusted_advantage']>0 and decision['minimum_fixed_disadvantage']>0
    assert decision['counts']=={'anchor_solves':8,'count_constructions':8}
    assert (OUT/'decision_coefficients.npz').is_file() and (OUT/'decision_policy_bank.npz').is_file()
    m=json.loads((OUT/'matched.json').read_text());assert len(m['rows'])==5
    original=[r for r in m['rows'] if r['bank']=='R6 matched'];assert sum(len(r['intervals']) for r in original)==51
    expected={0.:.0007338463674633200,.5:.0006851026198662069,1.:.0004357448654037643}
    for r in original:assert abs(r['methods']['count']['bound']-expected[r['d']])<2e-11
    ad=json.loads((OUT/'adaptive.json').read_text());assert len(ad['rows'])==3
    assert set(ad['rows'][2]['anchors'])<=set(ad['rows'][0]['anchors'])
    protected=[];changed=[]
    if not local:
        changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
        assert all(allowed(p) for p in changed),changed
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
        protected=[p for p in paths if p!='REVISION_INDEX.md']
        assert not subprocess.check_output(['git','diff','--name-only',BASE,'--',*protected],cwd=ROOT,text=True)
        oldindex=subprocess.check_output(['git','show',BASE+':REVISION_INDEX.md'],cwd=ROOT,text=True)
        assert oldindex in (ROOT/'REVISION_INDEX.md').read_text()
    else:
        hist=json.loads((REV/'inherited_r6_inventory.json').read_text())
        for p,digest in hist.items():assert sha(ROOT/p)==digest,p
        protected=list(hist)
    report=dict(source_commit=source,review_base=BASE,source_bytes_verified=True,
        authored_inputs_checked=len(inventory),historical_files_checked=len(protected),
        all_historical_files_preserved=True,history_check='local R6 SHA-256 inventory' if local else 'all inherited review-base Git paths',
        changed_paths=changed,documents={},output_sha256={p.name:sha(p) for p in sorted(OUT.glob('*')) if p.is_file()})
    for name in ('ECTA_R7','SUPP_R7'):
        log=ROOT/'build-r7'/f'{name}.log';text=log.read_text(errors='replace')
        assert 'Output written on' in text and 'Fatal error' not in text
        for bad in (r'Overfull \\hbox',r'Overfull \\vbox',r'undefined references',r'Citation .* undefined',r'Reference .* undefined',r'multiply defined'):
            assert not re.search(bad,text),(name,bad)
        pdf=ROOT/'build-r7'/f'{name}.pdf';info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
        pages=int(re.search(r'Pages:\s+(\d+)',info).group(1));assert pages>0
        extracted=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True)
        assert 'Local layout preview' not in extracted and '??' not in extracted
        shutil.copy2(pdf,REV/pdf.name);shutil.copy2(log,REV/f'{name}_build.log')
        report['documents'][name]=dict(pages=pages,pdf_sha256=sha(pdf),build_log_sha256=sha(log),undefined_references=False,overfull_boxes=False)
    report['scope']='Executed source and output identity, actual compilation and historical preservation; not a substitute for mathematical proof or an editorial judgment.'
    (REV/'build_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source-commit',required=True);ap.add_argument('--local',action='store_true');args=ap.parse_args();run(args.source_commit,args.local)
