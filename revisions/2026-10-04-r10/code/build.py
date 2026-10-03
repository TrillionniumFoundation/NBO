"""Compile the integrated journal documents and reject unresolved references."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1];B=R/'build'
B.mkdir(exist_ok=True)
def call(args,log):
 with (B/log).open('w') as f:p=subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(f'compilation failed: {log}')
for name,source in [('ECTA','ECTA.tex'),('supp','supp.tex'),('response','revisions/2026-10-04-r10/response.tex')]:
 for n in [1,2,3]:
  call(['pdflatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={B}',source],f'{name}_pass{n}.stdout')
  if name=='ECTA' and n==1:call(['bibtex',str(B/'ECTA')],'bibtex.stdout')
result={}
for name in ['ECTA','supp','response']:
 text=(B/f'{name}.log').read_text(errors='replace')
 meta=dict(pdf_sha256=hashlib.sha256((B/f'{name}.pdf').read_bytes()).hexdigest(),
  pages=int(re.findall(r'Output written on .*?\((\d+) pages?',text,re.S)[-1]),
  undefined=bool(re.search(r'undefined references|Citation .* undefined|Reference .* undefined|Undefined control sequence',text)),
  overfull_hbox_pt=[float(v) for v in re.findall(r'Overfull \\hbox \(([\d.]+)pt',text)])
 result[name]=meta
 call(['pdftotext','-layout',str(B/f'{name}.pdf'),str(B/f'{name}.txt')],f'{name}_text.stdout')
(R/'results/COMPILATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
assert all(not r['undefined'] for r in result.values()),'unresolved citations or references'
assert all(not r['overfull_hbox_pt'] for r in result.values()),'overfull material requires layout review'
