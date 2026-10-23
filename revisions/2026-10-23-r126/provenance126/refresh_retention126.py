"""Bind exact retained bytes and actual R126 TeX inputs to a successful receipt.

This is presentation/source-custody verification, not scientific re-execution.
The preceding CONTENT_RETENTION125 map and historical sources are never changed.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--receipt',required=True);args=ap.parse_args()
 receipt_path=(ROOT/args.receipt).resolve();receipt_path.relative_to(ROOT)
 receipt=json.loads(receipt_path.read_text())
 if receipt.get('status')!='compiled_clean':raise ValueError('A clean completed actual build is required')
 if receipt.get('source_mutations_during_build'):raise ValueError('Build changed its source inputs')
 project=receipt['actual_project_inputs'];retention_path=ROOT/'CONTENT_RETENTION126.json';retention=json.loads(retention_path.read_text())
 old=retention['inherited_map_identity'];assert sha(ROOT/old['path'])==old['sha256'],'Changed historical retention map'
 for doc,inputs in project.items():
  for relative,digest in inputs.items():
   p=(ROOT/relative).resolve();p.relative_to(ROOT)
   assert p.is_file() and sha(p)==digest,('Changed actual TeX input',doc,relative)
 rows=retention['inherited_records']+retention['exact_r125_additions']
 for row in rows:
  p=ROOT/row['retained_path'];assert p.is_file() and sha(p)==row['sha256'],('Changed retained source',row['retained_path'])
  row['r126_actual_rendered_in']=[doc for doc,inputs in project.items() if row['retained_path'] in inputs]
 pdfs=receipt['pdfs']
 pdfrows=pdfs if isinstance(pdfs,list) else [dict(info,path=info.get('path','build/'+doc+'.pdf')) for doc,info in pdfs.items()]
 assert len(pdfrows)==4,'All four actual manuscript PDFs are required'
 for info in pdfrows:
  p=(ROOT/info['path']).resolve();p.relative_to(ROOT)
  assert p.is_file() and sha(p)==info['sha256'],('Changed PDF',info['path'])
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 retention['actual_r126_build_closure']={'receipt':str(receipt_path.relative_to(ROOT)),'receipt_sha256':sha(receipt_path),'build_status':receipt['status'],'build_started_utc':receipt.get('started_utc'),'build_finished_utc':receipt.get('finished_utc'),'actual_project_inputs':project,'generated_build_inputs':receipt.get('generated_build_inputs',{}),'pdfs':pdfs,'refresh_utc':stamp,'refresh_script_sha256':sha(Path(__file__))}
 retention['build_closure_status']='Actual successful R126 TeX recorder closure verified against current source and retained file bytes.'
 retention_path.write_text(json.dumps(retention,indent=2,sort_keys=True)+'\n')
 check={'status':'verified','retained_records':len(rows),'inherited_records':len(retention['inherited_records']),'r125_additions':len(retention['exact_r125_additions']),'source_commit':retention['current_scientific_source_commit'],'build_receipt':str(receipt_path.relative_to(ROOT)),'build_receipt_sha256':sha(receipt_path),'actual_project_input_counts':{doc:len(x) for doc,x in project.items()},'scientific_computations_rerun':0,'verified_utc':stamp}
 (ROOT/'provenance126/CURRENT_RETENTION_CHECK126.json').write_text(json.dumps(check,indent=2,sort_keys=True)+'\n')
 md=ROOT/'CONTENT_RETENTION126.md';text=md.read_text();start='<!-- R126-ACTUAL-CLOSURE-BEGIN -->';end='<!-- R126-ACTUAL-CLOSURE-END -->'
 section=start+'\n## Actual completed R126 build\n\nThe clean build receipt `'+str(receipt_path.relative_to(ROOT))+'` (SHA256 `'+sha(receipt_path)+'`) records the source inputs actually read by TeX. The current bytes of all '+str(len(rows))+' retained source records and all recorded project inputs were verified against their hashes. `provenance126/CURRENT_RETENTION_CHECK126.json` records the verification. This build check did not rerun scientific experiments.\n\n| Document | Actual project inputs |\n|---|---:|\n'+''.join('| `'+doc+'` | '+str(len(inputs))+' |\n' for doc,inputs in project.items())+'\n'+end
 if start in text:text=text[:text.index(start)]+section+text[text.index(end)+len(end):]
 else:text=text.rstrip()+'\n\n'+section+'\n'
 md.write_text(text)
 print(json.dumps(check,sort_keys=True))
if __name__=='__main__':main()
