"""Offline ordinary-source R72 build and source-bound record verification."""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,time
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r70'
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','SOURCE_DATE_EPOCH':'1791676800','FORCE_SOURCE_DATE':'1','TZ':'UTC'}
DOCS=('ECTA','supp','appendix','response')
FONT_EXTENSIONS={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def run(args,label,cwd=None):
    file=R/'audit/build-logs'/(label+'.log');file.parent.mkdir(parents=True,exist_ok=True)
    with file.open('w') as out:result=subprocess.run(args,cwd=cwd or R,env=ENV,stdout=out,stderr=subprocess.STDOUT)
    text=file.read_text(errors='replace')
    if result.returncode:raise RuntimeError(label+' failed:\n'+text[-14000:])
    return text

def preserve():
    a=json.loads((R/'audit/PREPARATION72.json').read_text());statements=proofs=0
    for path,record in a['unchanged_active_sections'].items():
        if sha(R/path)!=record['sha256'] or sha(OLD/path)!=record['sha256']:raise AssertionError('Inherited section changed: '+path)
        inputs=['\\input{'+path[:-4]+'}' in (R/(doc+'.tex')).read_text() for doc in DOCS[:-1]]
        if sum(inputs)!=1:raise AssertionError('Inherited content absent or duplicated: '+path)
        text=(R/path).read_text();statements+=len(re.findall(r'\\begin\{(?:theorem|lemma|proposition|corollary)\}',text));proofs+=text.count(r'\begin{proof}')
    for path,digest in a['prior_files'].items():
        if sha(R/path)!=digest:raise AssertionError('Prior wrapper changed')
    record=dict(status='passed',unchanged_active_sections=len(a['unchanged_active_sections']),inherited_formal_statements=statements,inherited_proof_blocks=proofs,all_prior_active_sections_compiled_once=True,baseline_commit=a['baseline_commit'],scope='All R70 active sections compiled byte-identically in main/supplement/appendix; original wrappers and prior editions retained.')
    save(R/'audit/PRESERVATION72.json',record);return record

def bibliography(name):
    entries=json.loads((R/'publication/bibliography-entries.json').read_text());aux=(R/'build'/(name+'.aux')).read_text()
    keys={k for group in re.findall(r'\\citation\{([^}]+)\}',aux) for k in group.split(',')}
    if '*' in keys:keys=set(entries)
    if keys-set(entries):raise AssertionError('Unknown bibliography '+str(keys-set(entries)))
    keys=sorted(keys,key=lambda k:re.search(r'\\textsc\{([^}]+)',entries[k])[1].lower())
    text='\\begin{thebibliography}{'+str(len(keys))+'}\n'+r"\providecommand{\enquote}[1]{``#1''}"+'\n'+r'\providecommand{\natexlab}[1]{#1}'+'\n\n'+'\n\n'.join(entries[k] for k in keys)+'\n\n\\end{thebibliography}\n'
    (R/'build'/(name+'.bbl')).write_text(text)

def response():
    run(['pandoc','-f','markdown','-t','latex','--wrap=auto','response.md','-o','build/response-body.tex'],'response-conversion')
    text=(R/'build/response-body.tex').read_text();text=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:r'\nolinkurl{'+m[1].replace(r'\_','_')+'}',text)
    front=(R/'supp.tex').read_text().split(r'\end{frontmatter}',1)[0]+r'\end{frontmatter}'+'\n';front=re.sub(r'^\\externaldocument[^\n]*\n?','',front,flags=re.M)
    front=front.replace('Technical Supplement to Neural Bellman Operators','Response to the Referee: Neural Bellman Operators').replace('Neural Bellman Operators: Supplement','Response to the Referee').replace('label=e72supp','label=e72response')
    front=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'Revision R72 addresses the 11 October 2026 advisory report on R67, retaining the original NBO paper, the intervening completed R70 revision and all adverse evidence. The response separates new theorems, executed query reuse, independent arithmetic and remaining empirical distinctions.'+m[2],front,flags=re.S)
    (R/'response.tex').write_text(front+r'\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}'+'\n'+text+'\n\\end{document}\n')

def pdf_record(name):
    file=R/'build'/(name+'.pdf');info=subprocess.check_output(['pdfinfo',str(file)],text=True);text=subprocess.check_output(['pdftotext','-layout',str(file),'-']);(R/'build'/(name+'.txt')).write_bytes(text)
    log=(R/'build'/(name+'.log')).read_text(errors='replace');patterns={'undefined':r'(?:Reference|Citation).*undefined|There were undefined references','duplicate_labels':r'multiply defined|multiply-defined labels','missing_glyphs':r'Missing character:','overfull':r'Overfull \\[hv]box','fatal':r'^!|Fatal error'}
    bad={k:re.findall(p,log,re.M) for k,p in patterns.items()}
    if any(bad.values()):raise AssertionError((name,bad))
    return dict(document=name,pages=int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1]),sha256=sha(file),text_sha256=hashlib.sha256(text).hexdigest(),checks=bad,font_substitutions=re.findall(r"Font shape `[^']+' undefined",log))

def main(full=False):
    begin=time.perf_counter();(R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    for exe in ('pdflatex','pandoc','pdfinfo','pdftotext'):
        if shutil.which(exe) is None:raise RuntimeError('Missing build dependency '+exe)
    for p in (R/'code').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    preserved=preserve();tests={}
    suites=[('72-theory',R/'code/tests72.py'),('72-release',R/'code/tests_publication72.py')]
    if full:
        suites += [(str(n),R.parent/f'2026-10-10-r{n}/code/tests{n}.py') for n in (63,64,65,66)]
        suites += [('67-science',R.parent/'2026-10-10-r67/code/tests67.py'),('67-math',R.parent/'2026-10-10-r67/code/tests_math67.py'),('67-records',R.parent/'2026-10-10-r67/code/tests_records67.py'),('69',R.parent/'2026-10-11-r69/code/tests69.py'),('70',OLD/'code/tests70.py')]
    for name,file in suites:
        start=time.perf_counter();text=run([sys.executable,str(file)],'tests-'+name);m=re.search(r'Ran (\d+) tests?',text)
        if not m or not re.search(r'^OK\s*$',text,re.M):raise AssertionError('Unittest success missing '+name)
        tests[name]=dict(tests=int(m[1]),seconds=time.perf_counter()-start,status='passed')
    run([sys.executable,'code/independent72.py'],'independent72')
    run([sys.executable,'code/audit_contract72.py'],'task-contract72')
    run([sys.executable,'code/tables72.py'],'tables72')
    if full:
        # R70 audit writes only its audit report; preserve the pinned old file
        # and copy the rerun report into R72. Original sources/data stay intact.
        file=OLD/'audit/RESULT_AUDIT70.json';before=file.read_bytes()
        try:
            run([sys.executable,str(OLD/'code/audit70.py')],'retained-record-audit70',OLD)
            shutil.copy2(file,R/'audit/RETAINED_REPLAY70_IN_R72.json')
        finally:file.write_bytes(before)
    response()
    for name in DOCS:(R/'build'/(name+'.bbl')).unlink(missing_ok=True)
    for iteration in range(5):
        for name in DOCS:
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex'],name+'-pass'+str(iteration))
            if iteration==0 and name!='response':bibliography(name)
    documents=[pdf_record(name) for name in DOCS]
    for d in documents:
        if d['document']=='ECTA' and d['pages']>45:raise AssertionError('Main article exceeds declared 45-page revision target: '+str(d['pages']))
        if d['document']=='supp' and d['pages']>25:raise AssertionError('Technical supplement exceeds declared 25-page target: '+str(d['pages']))
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',(R/'ECTA.tex').read_text(),re.S)[1]
    if len(abstract.split())>150:raise AssertionError('Abstract exceeds target')
    for p in R.rglob('*'):
        if p.is_file() and p.suffix.lower() in FONT_EXTENSIONS:raise AssertionError('Standalone font file')
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    report=dict(status='passed',tested_source_commit=commit,full_retained_replay=full,documents=documents,tests=tests,total_tests=sum(x['tests'] for x in tests.values()),preservation=preserved,independent_audit=json.loads((R/'audit/INDEPENDENT72.json').read_text()),new_scientific_services=36,new_independent_policy_cost_rows=0,scientific_source_freeze_sha256=sha(R/'SOURCE_FREEZE72.json'),seconds=time.perf_counter()-begin,abstract_words=len(abstract.split()),scope='Source-bound original process records, every new transfer and exact conditional moment independently checked, theorem and numerical regressions, ordinary-source publication. Inherited large recursive fills not independently regenerated; clocks not remeasured.',visual_scope='Log and text checks here; visual review is separately recorded against actual output hashes.')
    save(R/'audit/RELEASE72.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('independent_audit','tests')},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');args=p.parse_args();main(args.full)
