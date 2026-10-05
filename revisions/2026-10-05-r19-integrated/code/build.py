"""Build the four native Econometrica-class documents with resolved cross-references."""
from pathlib import Path
import subprocess,re,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[3]
R=Path(__file__).resolve().parents[1]
BUILD=R/'build'
def run(cmd,log):
 with (BUILD/log).open('w') as f:
  result=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=300)
 if result.returncode:
  raise RuntimeError(' '.join(map(str,cmd))+'\n'+(BUILD/log).read_text(errors='replace')[-9000:])
def build():
 BUILD.mkdir(exist_ok=True)
 sources={n:(ROOT/f'{n}.tex' if n in ('ECTA','supp') else R/f'{n}.tex') for n in ('ECTA','supp','applications','response')}
 for n in sources:
  for ext in ('aux','bbl','blg','log','out','toc','pdf'):(BUILD/f'{n}.{ext}').unlink(missing_ok=True)
  (BUILD/f'{n}_refs.aux').unlink(missing_ok=True)
 for cycle in range(1,5):
  for n,p in sources.items():
   run(['pdflatex','-no-shell-escape','-file-line-error','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(BUILD.relative_to(ROOT)),str(p.relative_to(ROOT))],f'{n}.pass{cycle}.stdout')
   aux=(BUILD/f'{n}.aux').read_text(errors='replace')
   (BUILD/f'{n}_refs.aux').write_text('\n'.join(x for x in aux.splitlines() if x.startswith('\\newlabel{'))+'\n')
   if cycle==1 and n!='response':run([shutil.which('bibtex') or shutil.which('bibtex.original') or 'bibtex',str((BUILD/n).relative_to(ROOT))],f'{n}.bibtex.stdout')
 records=[]
 for n,p in sources.items():
  log=(BUILD/f'{n}.log').read_text(errors='replace');pdf=BUILD/f'{n}.pdf'
  info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
  run(['pdftotext','-layout',str(pdf),str(BUILD/f'{n}.txt')],f'{n}.pdftotext.stdout')
  record=dict(document=n,source=str(p.relative_to(ROOT)),pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1]),pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),undefined=bool(re.search(r'(?:Reference|Citation).* undefined|There were undefined',log)),multiply_defined=bool(re.search(r'multiply[ -]defined',log,re.I)),duplicate_destination='destination with the same identifier' in log,missing_character='Missing character:' in log,overfull_hbox=[float(x) for x in re.findall(r'Overfull \\hbox \(([-0-9.]+)pt too wide\)',log)],overfull_vbox=[float(x) for x in re.findall(r'Overfull \\vbox \(([-0-9.]+)pt too high\)',log)])
  records.append(record)
 report=dict(class_name='econsocart',options='ecta,nameyear,draft',cycles=4,documents=records,visual_inspection='Recorded separately against these PDF hashes.')
 (R/'results/COMPILATION.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
 for rec in records:
  if any(rec[x] for x in ('undefined','multiply_defined','duplicate_destination','missing_character')) or any(x>1 for x in rec['overfull_hbox']+rec['overfull_vbox']):raise RuntimeError('Publication diagnostics require correction: '+rec['document'])
 return report
if __name__=='__main__':build()
