#!/usr/bin/env python3
"""Build-log, historical-byte, and source provenance checks for R6 delivery."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE='0d0e79a52e540bd0647801ce316f051d667c6797'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def allowed(p):
    return p in {'ECTA_R6.tex','SUPP_R6.tex','REVISION_INDEX.md','.github/workflows/revision-r6.yml'} or p.startswith(('replication/r6/','revisions/2026-09-16-r6/'))
def run(source,local=False):
    validation=json.loads((ROOT/'replication/r6/output/validation.json').read_text())
    if not local:assert validation['source_commit']==source and validation['source_bytes_verified']
    changed=[];historical=[]
    if not local:
        changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
        assert all(allowed(p) for p in changed),changed
        oldindex=subprocess.check_output(['git','show',BASE+':REVISION_INDEX.md'],cwd=ROOT,text=True)
        assert oldindex in (ROOT/'REVISION_INDEX.md').read_text()
        historical=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
        protected=[p for p in historical if p!='REVISION_INDEX.md']
        assert not subprocess.check_output(['git','diff','--name-only',BASE,'--',*protected],cwd=ROOT,text=True)
    report=dict(source_commit=source,review_base=BASE,all_prior_files_preserved=not local,
        historical_paths_checked=len(historical)-(1 if historical else 0),changed_paths=changed,documents={})
    for name in ('ECTA_R6','SUPP_R6'):
        log=ROOT/'build-r6'/f'{name}.log';text=log.read_text(errors='replace')
        assert 'Output written on' in text and 'Fatal error' not in text
        for bad in (r'Overfull \\hbox',r'Overfull \\vbox',r'undefined references',r'Citation .* undefined',r'Reference .* undefined',r'multiply defined'):
            assert not re.search(bad,text),(name,bad)
        pdf=ROOT/'build-r6'/f'{name}.pdf';info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
        pages=int(re.search(r'Pages:\s+(\d+)',info).group(1));assert pages>0
        dst=ROOT/'revisions/2026-09-16-r6';shutil.copy2(pdf,dst/pdf.name);shutil.copy2(log,dst/f'{name}_build.log')
        report['documents'][name]=dict(pages=pages,pdf_sha256=sha(pdf),build_log_sha256=sha(log),undefined_references=False,overfull_boxes=False)
    report['scope']='Actual compilation and protected-history checks; distinct from mathematical evaluation, finite-model validation and a publication judgment.'
    (ROOT/'revisions/2026-09-16-r6/build_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source-commit',required=True);ap.add_argument('--local',action='store_true');a=ap.parse_args();run(a.source_commit,a.local)
