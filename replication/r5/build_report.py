#!/usr/bin/env python3
"""Compile-log checks and immutable-history audit before publication."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE='11082cc5054e91d3b2ac27826705f374ca74bfae'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def allowed(path):
 return path in {'ECTA_R5.tex','SUPP_R5.tex','REVISION_INDEX.md','.github/workflows/revision-r5.yml'} or path.startswith(('replication/r5/','revisions/2026-09-16-r5/'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-commit',required=True);a=ap.parse_args()
 validation=json.loads((ROOT/'replication/r5/output/validation.json').read_text());assert validation['source_commit']==a.source_commit and validation['source_bytes_verified']
 changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines();assert all(allowed(p) for p in changed),changed
 oldindex=subprocess.check_output(['git','show',BASE+':REVISION_INDEX.md'],cwd=ROOT,text=True);assert oldindex in (ROOT/'REVISION_INDEX.md').read_text()
 historical=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
 protected=[p for p in historical if p!='REVISION_INDEX.md'];diff=subprocess.check_output(['git','diff','--name-only',BASE,'--',*protected],cwd=ROOT,text=True);assert not diff,diff
 report=dict(source_commit=a.source_commit,review_base=BASE,all_prior_files_preserved=True,protected_paths_checked=len(protected),changed_paths=changed,documents={})
 for name in ('ECTA_R5','SUPP_R5'):
  log=ROOT/'build-r5'/f'{name}.log';text=log.read_text(errors='replace')
  assert 'Output written on' in text and 'Fatal error' not in text
  for bad in (r'Overfull \\hbox',r'Overfull \\vbox',r'undefined references',r'Citation .* undefined',r'Reference .* undefined',r'multiply defined'):
   assert not re.search(bad,text), (name,bad)
  pdf=ROOT/'build-r5'/f'{name}.pdf';info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
  pages=int(re.search(r'Pages:\s+(\d+)',info).group(1));assert pages>0
  dst=ROOT/'revisions/2026-09-16-r5';shutil.copy2(pdf,dst/pdf.name);shutil.copy2(log,dst/f'{name}_build.log')
  report['documents'][name]=dict(pages=pages,pdf_sha256=sha(pdf),build_log_sha256=sha(log),undefined_references=False,overfull_boxes=False)
 report['scope']='Compilation and protected-history checks, separate from mathematical review and finite-model numerical validation.'
 (ROOT/'revisions/2026-09-16-r5/build_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
