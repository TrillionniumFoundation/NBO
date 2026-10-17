"""Verify active TeX dependency/citation closure and actual PDF bytes."""
from pathlib import Path
import re,json,hashlib
import fitz
R=Path(__file__).resolve().parents[1]
DOCS=('ECTA','supp','appendix','RESPONSE_TO_REFEREE')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seen=set();labels={};refs=set();cites=set();bibfiles=set()
def scan(p):
    p=p.resolve()
    if p in seen:return
    if not p.is_file():raise FileNotFoundError(p)
    seen.add(p);t=re.sub(r'(?<!\\)%[^\n]*','',p.read_text())
    for l in re.findall(r'\\label\{([^}]+)\}',t):
        if l in labels:raise AssertionError('Duplicate active label: '+l)
        labels[l]=str(p.relative_to(R))
    refs.update(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',t))
    for c in re.findall(r'\\cite\w*\*?(?:\[[^]]*\])*\{([^}]+)\}',t):cites.update(s.strip() for s in c.split(','))
    for b in re.findall(r'\\bibliography\{([^}]+)\}',t):bibfiles.update(x.strip()+'.bib' for x in b.split(','))
    for s in re.findall(r'\\(?:input|include)\{([^}]+)\}',t):scan(R/(s if s.endswith('.tex') else s+'.tex'))
for d in DOCS:scan(R/(d+'.tex'))
keys=set()
for b in bibfiles:
    p=R/b;assert p.exists();keys.update(re.findall(r'@\w+\s*\{\s*([^,]+),',p.read_text()))
assert not refs-labels.keys(),('Undefined source refs',refs-labels.keys())
assert not cites-keys,('Missing citations',cites-keys)
report={'documents':{},'tex_dependencies':{str(p.relative_to(R)):sha(p) for p in sorted(seen)},'active_labels':len(labels),'cited_keys':sorted(cites),'bibliography_files':{b:sha(R/b) for b in sorted(bibfiles)},'validation':'source closure and actual final LaTeX logs/PDFs; visual inspection recorded separately'}
for d in DOCS:
    log=(R/f'build/{d}.log').read_text(errors='replace')
    bad=[x for x in log.splitlines() if any(s in x.lower() for s in ('undefined references','undefined citations','multiply defined','label(s) may have changed','rerun to get cross-references'))]
    if bad:raise AssertionError((d,bad))
    p=R/f'build/{d}.pdf';pdf=fitz.open(p)
    report['documents'][d]={'pages':len(pdf),'bytes':p.stat().st_size,'sha256':sha(p),'overfull_warnings':re.findall(r'Overfull [^\n]+',log),'pages_with_no_text':[i+1 for i,page in enumerate(pdf) if not page.get_text().strip()]}
(R/'evidence109/PUBLICATION109.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report['documents'],indent=2))
