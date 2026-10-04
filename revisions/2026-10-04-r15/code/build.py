"""Build the current R15 Econometrica article, supplement and referee response."""
from pathlib import Path
import hashlib,json,re,subprocess,shutil
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parents[1];B=R/'build'
def call(args,log):
    B.mkdir(exist_ok=True)
    with (B/log).open('w') as f:p=subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=300)
    if p.returncode:
        print((B/log).read_text(errors='replace')[-8000:]);raise RuntimeError(f'build failed: {log}')
def build():
    B.mkdir(exist_ok=True);rel=str(B.relative_to(ROOT));sources=[('ECTA','ECTA.tex'),('supp','supp.tex'),('response',str((R/'response.tex').relative_to(ROOT)))]
    for p in B.glob('*'):
        if p.suffix in ['.pdf','.aux','.bbl','.blg','.log','.out']:p.unlink()
    for cycle in range(1,5):
        for name,source in sources:
            call(['pdflatex','-no-shell-escape','-file-line-error','-interaction=nonstopmode','-halt-on-error',f'-output-directory={rel}',source],f'{name}_{cycle}.stdout')
            aux=(B/f'{name}.aux').read_text(errors='replace').splitlines();refs=[x for x in aux if x.startswith(r'\newlabel{')]
            (B/f'{name}_refs.aux').write_text('\n'.join(refs)+'\n')
            if cycle==1 and name in ['ECTA','supp']:call([shutil.which('bibtex') or shutil.which('bibtex.original') or 'bibtex',f'{rel}/{name}'],f'{name}_bibtex.stdout')
    records={}
    for name,_ in sources:
        text=(B/f'{name}.log').read_text(errors='replace');pages=re.findall(r'Output written on .*?\((\d+) pages?',text,re.S)
        records[name]=dict(pages=int(pages[-1]),pdf_sha256=hashlib.sha256((B/f'{name}.pdf').read_bytes()).hexdigest(),undefined=bool(re.search(r'undefined references|Citation .* undefined|Reference .* undefined|Undefined control sequence',text)),multiply_defined=bool(re.search(r'multiply.defined (labels|citations)',text)),duplicate_destinations=bool(re.search(r'destination with the same identifier|duplicate destination',text,re.I)),overfull_hbox_pt=[float(x) for x in re.findall(r'Overfull \\hbox \(([\d.]+)pt',text)])
        call(['pdftotext','-layout',f'{rel}/{name}.pdf',f'{rel}/{name}.txt'],f'{name}_text.stdout')
    (R/'results').mkdir(exist_ok=True);(R/'results/COMPILATION.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2))
    if any(r['undefined'] or r['multiply_defined'] or r['duplicate_destinations'] or r['overfull_hbox_pt'] for r in records.values()):raise RuntimeError('unresolved references or overfull material require review')
    return records
if __name__=='__main__':build()
