"""Pin source, outputs and preservation, without a self-referential commit hash."""
from pathlib import Path
import json,hashlib,os,subprocess,zipfile,platform
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r21'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 validation=json.loads((REV/'build_logs/pdf_validation.json').read_text())
 replay=json.loads((REV/'results/replay_summary.json').read_text())
 assert replay['status']=='PASS' and replay['checks']==136 and replay['mpfr_checks']==20
 original=json.loads((REV/'INHERITED_SHA256.json').read_text())
 assert len(original)==3934
 for name,h in original.items():
  p=REV/'history/REVISION_INDEX_before_R21.md' if name=='REVISION_INDEX.md' else ROOT/name
  assert p.is_file() and sha(p)==h,name
 selected=[]
 for p in [ROOT/'ECTA_R21.tex',ROOT/'SUPP_R21.tex',ROOT/'RESPONSE_R21.tex',ROOT/'R21_REVIEW.md',ROOT/'REVISION_INDEX.md',ROOT/'reviews/2026-09-23-econometrica-r21/referee_report.md',ROOT/'ECTA_R21.pdf',ROOT/'SUPP_R21.pdf',ROOT/'RESPONSE_R21.pdf']+list(REV.rglob('*'))+list((ROOT/'revisions/2026-09-23-r20/results').rglob('*')):
  if p.is_file() and p.name!='PUBLICATION_MANIFEST.json' and '__pycache__' not in p.parts:selected.append(p)
 selected=sorted(set(selected))
 d={'format':'NBO_R21_publication_v1','source_commit':os.getenv('R21_SOURCE_COMMIT','local snapshot of 6951c3b plus R21 additions'),
 'review_commit':'074849b9aad1812b59e25e1d3833383ed11aa401','additional_review_commit':'bc118f20f6361cdeae668141e45f64c436ee6a2a','additional_review_snapshot':'6951c3b01b5102ef3d743a6ab14f9cc595b08804','inherited_head':'6916f250ca2115399dccf2df125c0b13f304547b','training_source':'b1a2ea39d895b330e5a11b4e55d86b7a4985b101','training_run':35802793602,
 'semantics':'R21 new analysis and frozen-policy re-execution; R20 confirmatory training retained unchanged; no self-referential publication SHA',
 'preservation':validation['historical_preservation'],'pdf_validation':validation['documents'],'replay_checks':136,
 'versions':{'python':platform.python_version(),'pdflatex':subprocess.check_output(['pdflatex','--version'],text=True).splitlines()[0]},
 'files':{str(p.relative_to(ROOT)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in selected}}
 (REV/'PUBLICATION_MANIFEST.json').write_text(json.dumps(d,indent=2)+'\n')
 out=ROOT/'NBO_R21_review_package.zip'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in selected+[REV/'PUBLICATION_MANIFEST.json']:
   if p.suffix=='.b64' or p.name=='INHERITED_SHA256.json':continue
   z.write(p,str(p.relative_to(ROOT)))
 print(json.dumps({'files':len(selected),'archive':out.name,'bytes':out.stat().st_size},indent=2))
if __name__=='__main__':main()
