"""Verify source closure, inherited identities, final TeX references and PDF receipts."""
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    record=json.loads((ROOT/'results99/retention.json').read_text())
    for row in record['unchanged_inherited_files']:
        if digest(ROOT/row['path'])!=row['sha256']:
            raise SystemExit('Inherited file identity changed: '+row['path'])
    for row in record.get('exact_section_splits',[]):
        data=(ROOT/row['head']).read_bytes()+(ROOT/row['tail']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=row['sha256']:
            raise SystemExit('Split retention failure: '+row['source'])
    inputs=set();seen=set()
    def scan(path):
        path=path.resolve()
        if path in seen:return
        if not path.is_relative_to(ROOT) or not path.is_file():raise SystemExit('Missing or external TeX dependency: '+str(path))
        seen.add(path)
        text=re.sub(r'(?<!\\)%[^\n]*','',path.read_text())
        for name in re.findall(r'\\(?:input|include)\s*\{([^}]+)\}',text):
            if '#' in name:continue
            q=ROOT/name
            if not q.suffix:q=q.with_suffix('.tex')
            inputs.add(str(q.relative_to(ROOT)));scan(q)
    pdfs={};warnings={}
    for stem in ['ECTA','supp','appendix','response99']:
        scan(ROOT/(stem+'.tex'))
        log=(ROOT/'build'/(stem+'.log')).read_text(errors='replace')
        bad=[line for line in log.splitlines() if
             ('undefined' in line.lower() and ('reference' in line.lower() or 'citation' in line.lower()))
             or 'multiply defined' in line.lower()]
        if bad:raise SystemExit('Unresolved final TeX state in '+stem+': '+str(bad[:5]))
        over=[line for line in log.splitlines() if 'Overfull \\hbox' in line or 'Overfull \\vbox' in line]
        warnings[stem]=over
        pdf=ROOT/'build'/(stem+'.pdf')
        info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
        pages=int(re.search(r'^Pages:\s*(\d+)',info,re.M).group(1))
        pdfs[stem]={'pages':pages,'bytes':pdf.stat().st_size,'sha256':digest(pdf)}
    tests=json.loads((ROOT/'results99/tests.json').read_text())
    if not tests['successful']:raise SystemExit('Exact tests failed')
    newfiles=sorted([p for folder in ['new','code99'] for p in (ROOT/folder).rglob('*')
                     if p.is_file() and '__pycache__' not in str(p) and ('99' in p.name or folder=='code99')])
    out={'scientific_baseline':record['baseline_commit'],'review_commit':record['review_commit'],
         'python':sys.version,'platform':platform.platform(),'tests':tests,
         'inherited_identity_count':len(record['unchanged_inherited_files']),
         'tex_dependency_count':len(seen),'tex_dependencies':sorted(inputs),
         'pdfs':pdfs,'overfull_warnings':warnings,
         'new_source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in newfiles},
         'scope':'Actual exact-mechanism tests and PDF build; no new investment refit, scaling tournament or journal acceptance.'}
    (ROOT/'results99/RELEASE99.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k in ['tests','inherited_identity_count','tex_dependency_count','pdfs','overfull_warnings']},indent=2))

if __name__=='__main__':main()
