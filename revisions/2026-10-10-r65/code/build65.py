"""Offline R65 publication from ordinary sources and frozen repository records."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time
R=Path(__file__).resolve().parents[1]
DOCS=[(R,'ECTA','ECTA'),(R,'supp','supp'),(R,'response','response'),
      (R/'retained62','ECTA','development62'),(R/'retained62','supp','development-supp62'),
      (R/'retained62','complete','complete62'),(R/'retained62','complete-supp','complete-supp62')]
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','SOURCE_DATE_EPOCH':'1791590400','FORCE_SOURCE_DATE':'1'}
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def run(args,label,cwd=R):
    log=R/'audit/build-logs'/(label+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w') as f:v=subprocess.run(args,cwd=cwd,env=ENV,stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text(errors='replace')
    if v.returncode:raise RuntimeError(label+' failed:\n'+text[-7000:])
    return text

def bibliography(root,name):
    entries=json.loads((root/'publication/bibliography-entries.json').read_text())
    aux=(root/'build'/(name+'.aux')).read_text();keys={v for c in re.findall(r'\\citation\{([^}]+)\}',aux) for v in c.split(',')}
    if '*' in keys:keys=set(entries)
    if keys-set(entries):raise ValueError('Missing references '+str(keys-set(entries)))
    ordered=sorted(keys,key=lambda k:re.search(r'\\textsc\{([^}]+)',entries[k])[1].lower())
    out='\\begin{thebibliography}{'+str(len(keys))+'}\n'+r"\providecommand{\enquote}[1]{``#1''}"+'\n'+r'\providecommand{\natexlab}[1]{#1}'+'\n\n'
    (root/'build'/(name+'.bbl')).write_text(out+'\n\n'.join(entries[k] for k in ordered)+'\n\n\\end{thebibliography}\n')

def response():
    run(['pandoc','-f','markdown','-t','latex','--wrap=auto','response.md','-o','build/response-body.tex'],'response-convert')
    body=(R/'build/response-body.tex').read_text()
    body=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:r'\nolinkurl{'+m[1].replace(r'\_','_')+'}',body)
    head=(R/'supp.tex').read_text().split(r'\input{sections/supp65}')[0]
    head=head.replace('Technical Supplement to Neural Bellman Operators','Response to the Referee: Neural Bellman Operators').replace('Neural Bellman Operators: Supplement','Response to the Referee')
    head=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'Revision R65 responds to the 10 October 2026 report on R62 and integrates the separately frozen R63 and R64 scientific services. The original paper and complete prior editions are retained.'+m[2],head,flags=re.S)
    (R/'response.tex').write_text(head+r'\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}'+'\n'+body+'\n\\end{document}\n')

def compile_one(root,name,output):
    (root/'build').mkdir(exist_ok=True)
    (root/'build'/(name+'.bbl')).unlink(missing_ok=True)
    cmd=['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex']
    run(cmd,output+'-pass0',root)
    if name!='response':bibliography(root,name)
    for k in range(1,4):run(cmd,output+'-pass'+str(k),root)
    log=(root/'build'/(name+'.log')).read_text(errors='replace')
    patterns={'undefined':r'(?:Reference|Citation).*undefined|There were undefined references','duplicates':r'multiply defined|multiply-defined labels','missing_glyphs':r'Missing character:','overfull':r'Overfull \\[hv]box','fatal':r'^!|Fatal error'}
    bad={key:re.findall(p,log,re.M) for key,p in patterns.items()}
    if any(bad.values()):raise AssertionError((output,bad))
    source=root/'build'/(name+'.pdf');dest=R/'build'/(output+'.pdf')
    if source!=dest:shutil.copy2(source,dest)
    info=subprocess.check_output(['pdfinfo',str(dest)],text=True)
    raw=subprocess.check_output(['pdftotext','-layout',str(dest),'-']);(R/'build'/(output+'.txt')).write_bytes(raw)
    return dict(document=output,pages=int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1]),sha256=sha(dest),text_sha256=hashlib.sha256(raw).hexdigest(),checks=bad,
        font_substitution_warnings=re.findall(r"Font shape `[^']+' undefined",log))

def verify_preservation():
    p=json.loads((R/'audit/PRESERVATION65.json').read_text())
    for name,h in p['retained_source_sha256'].items():
        if sha(R/'retained62'/name)!=h:raise AssertionError('Changed prior source '+name)
    return dict(files=len(p['retained_source_sha256']),distinct_labels=len(p['label_locations']))

def main():
    start=time.perf_counter();(R/'build').mkdir(exist_ok=True);preserved=verify_preservation()
    docs_only='--documents' in sys.argv
    if not docs_only:
        tests={}
        run([sys.executable,'code/audit65.py'],'complete-record-replay')
        for n in (63,64,65):
            file=R.parent/f'2026-10-10-r{n}'/'code'/f'tests{n}.py'
            text=run([sys.executable,str(file)],f'tests{n}')
            m=re.search(r'Ran (\d+) tests?',text)
            if not m or not re.search(r'^OK\s*$',text,re.M):raise AssertionError('Tests failed '+str(n))
            tests[str(n)]=int(m[1])
        save(R/'audit/TESTS65.json',dict(status='passed',counts=tests,total=sum(tests.values())))
    run([sys.executable,'code/tables65.py'],'derive-tables');response()
    docs=[compile_one(*spec) for spec in DOCS]
    out=dict(status='passed',documents=docs,preservation=preserved,tests=json.loads((R/'audit/TESTS65.json').read_text()) if (R/'audit/TESTS65.json').exists() else None,
        record_audit_sha256=sha(R/'audit/RESULT_AUDIT65.json'),seconds=time.perf_counter()-start,
        new_training_runs=0,new_independent_continuous_law_observations=0,
        scope='Ordinary source publication; complete frozen-record replay and independent rational trajectories; no formal proof-checker or external acceptance claim.',
        typography='Compilation and extracted text; visual page inspection has its own separate record.')
    save(R/'audit'/('DOCUMENT_REBUILD65.json' if docs_only else 'RELEASE65.json'),out)
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
