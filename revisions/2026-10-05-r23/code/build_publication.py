"""Build native econsocart PDFs, reject unresolved references, preserve sources."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[3]
R=Path(__file__).resolve().parents[1]
B=R/'build'
DOCS=('ECTA','supp','applications','evidence','response')


def command(cmd,log):
    with (B/log).open('w') as f:
        p=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=300)
    if p.returncode:raise RuntimeError(' '.join(map(str,cmd))+'\n'+(B/log).read_text(errors='replace')[-12000:])


def build():
    B.mkdir(exist_ok=True)
    for n in DOCS:
        for ext in ('aux','bbl','blg','log','out','toc','pdf','fls'):(B/f'{n}.{ext}').unlink(missing_ok=True)
        (B/f'{n}_refs.aux').unlink(missing_ok=True)
    for cycle in range(1,5):
        for n in DOCS:
            command(['pdflatex','-no-shell-escape','-recorder','-file-line-error','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(B.relative_to(ROOT)),str((R/f'{n}.tex').relative_to(ROOT))],f'{n}.pass{cycle}.stdout')
            aux=(B/f'{n}.aux').read_text(errors='replace')
            (B/f'{n}_refs.aux').write_text('\n'.join(x for x in aux.splitlines() if x.startswith('\\newlabel{'))+'\n')
            if cycle==1 and n!='response':command([shutil.which('bibtex') or 'bibtex',str((B/n).relative_to(ROOT))],f'{n}.bibtex.stdout')
    records=[]
    for n in DOCS:
        log=(B/f'{n}.log').read_text(errors='replace');pdf=B/f'{n}.pdf'
        info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
        command(['pdftotext','-layout',str(pdf),str(B/f'{n}.txt')],f'{n}.pdftotext.stdout')
        rec={'document':n,'source':str((R/f'{n}.tex').relative_to(ROOT)),'pages':int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1]),
             'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
             'undefined':bool(re.search(r'(?:Reference|Citation).* undefined|There were undefined',log)),
             'multiply_defined':bool(re.search(r'multiply[ -]defined',log,re.I)),
             'duplicate_destination':'destination with the same identifier' in log,
             'missing_character':'Missing character:' in log,
             'overfull_hbox':[float(x) for x in re.findall(r'Overfull \\hbox \(([-0-9.]+)pt too wide\)',log)],
             'overfull_vbox':[float(x) for x in re.findall(r'Overfull \\vbox \(([-0-9.]+)pt too high\)',log)]}
        records.append(rec)
    report={'class_name':'econsocart','options':'ecta,nameyear,draft','cycles':4,'documents':records,
            'visual_inspection':'PDF page renders are produced separately; automated log checks do not claim human visual inspection.'}
    (R/'results/COMPILATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    for rec in records:
        assert not any(rec[k] for k in ('undefined','multiply_defined','duplicate_destination','missing_character')),rec
        assert not any(v>1 for v in rec['overfull_hbox']+rec['overfull_vbox']),rec
    # Include only repository-owned inputs, never system fonts or installed files.
    inputs=set()
    for n in DOCS:
        for line in (B/f'{n}.fls').read_text(errors='replace').splitlines():
            if not line.startswith('INPUT '):continue
            p=Path(line[6:]);p=(p if p.is_absolute() else ROOT/p).resolve()
            if p.is_relative_to(ROOT) and p.is_file() and p.suffix not in ('.aux','.out','.log','.fls','.toc','.pfb','.pfm','.ttf','.otf','.tfm','.afm','.pk'):
                inputs.add(p)
        inputs.add(B/f'{n}.pdf')
    for p in ROOT.glob('*.bib'):inputs.add(p)
    for p in ROOT.glob('*.bst'):inputs.add(p)
    for sub in ('code','manuscript','protocols'):
        for p in (R/sub).rglob('*'):
            if p.is_file() and '__pycache__' not in str(p):inputs.add(p)
    for p in (R/'results/generated').glob('*'):
        if p.is_file():inputs.add(p)
    for p in (R/'results').glob('*.json'):inputs.add(p)
    for p in (R/'results').glob('TEST*.log'):inputs.add(p)
    for p in R.glob('*.tex'):inputs.add(p)
    for p in R.glob('*.md'):inputs.add(p)
    for p in R.glob('*.json'):inputs.add(p)
    for p in R.glob('*.txt'):inputs.add(p)
    for p in list(inputs):
        if p.suffix=='.tex':
            for group in re.findall(r'\\bibliography\{([^}]+)\}',p.read_text()):
                for name in group.split(','):
                    q=ROOT/(name.strip()+'.bib')
                    if q.exists():inputs.add(q)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)}
    (R/'PUBLICATION_FILES_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=Path('/tmp/NBO_R23_publication.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(inputs):z.write(p,str(p.relative_to(ROOT)))
        z.write(R/'PUBLICATION_FILES_SHA256.json',str((R/'PUBLICATION_FILES_SHA256.json').relative_to(ROOT)))
    print('PUBLICATION_ARCHIVE',archive,archive.stat().st_size,hashlib.sha256(archive.read_bytes()).hexdigest(),flush=True)
    return report

if __name__=='__main__':build()
