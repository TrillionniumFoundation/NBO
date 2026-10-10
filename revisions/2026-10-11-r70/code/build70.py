"""Offline build of ordinary R70 sources; scientific service records are read-only."""
from pathlib import Path
import ast,hashlib,json,os,re,shutil,subprocess,sys,time
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-10-r67'
ENV={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1','SOURCE_DATE_EPOCH':'1791676800','FORCE_SOURCE_DATE':'1','TZ':'UTC'}
THEORY=('core49','accuracy62-print','query63','gated64','localization65','operational67','vector67','decisions49')
DOCS=('ECTA','supp','response')
FONT_EXTENSIONS={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def run(args,label,cwd=None):
    path=R/'audit/build-logs'/(label+'.log');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as f:result=subprocess.run(args,cwd=cwd or R,env=ENV,stdout=f,stderr=subprocess.STDOUT)
    text=path.read_text(errors='replace')
    if result.returncode:raise RuntimeError(label+' failed:\n'+text[-11000:])
    return text

def preservation():
    p=json.loads((R/'audit/PREPARATION70.json').read_text());all_current='\n'.join(x.read_text() for x in (R/'sections').glob('*.tex') if x.name!='study67.tex' and x.name!='supp67.tex')
    for name,h in p['prior_sources_sha256'].items():
        if sha(OLD/name)!=h:raise AssertionError('Changed original source '+name)
    statements=proofs=0
    for name in THEORY:
        original=(OLD/'sections'/(name+'.tex')).read_text();current=(R/'sections'/(name+'.tex')).read_text()
        for m in re.finditer(r'\\begin\{(?P<kind>theorem|proposition|lemma|corollary)\}.*?\\end\{(?P=kind)\}',original,re.S):
            if m[0] not in current:raise AssertionError('Missing inherited statement '+name)
            statements+=1
        for block in re.findall(r'\\begin\{proof\}.*?\\end\{proof\}',original,re.S):
            if block not in all_current:raise AssertionError('Missing inherited proof '+name)
            proofs+=1
    # The R67 proof collection is copied unchanged, not counted as a new proof.
    if (OLD/'sections/proofs67.tex').read_bytes()!=(R/'sections/proofs67.tex').read_bytes():raise AssertionError('Changed inherited proof collection')
    for proof in p['relocated_proofs']:
        target=(R/'sections/proofs70.tex').read_text()
        if proof['sha256'] not in [hashlib.sha256(x.encode()).hexdigest() for x in re.findall(r'\\begin\{proof\}.*?\\end\{proof\}',target,re.S)]:raise AssertionError('Changed relocated proof')
    record=dict(status='passed',prior_sources=len(p['prior_sources_sha256']),inherited_active_statements=statements,inherited_active_inline_proofs=proofs,retained_proof_collection_sha256=sha(R/'sections/proofs67.tex'),relocated_proofs=len(p['relocated_proofs']),prior_label_locations=len(p['prior_label_locations']),historical_directories_modified=False)
    save(R/'audit/PRESERVATION70.json',record);return record

def bibliography(name):
    entries=json.loads((R/'publication/bibliography-entries.json').read_text());aux=(R/'build'/(name+'.aux')).read_text()
    keys={key for line in re.findall(r'\\citation\{([^}]+)\}',aux) for key in line.split(',')}
    if '*' in keys:keys=set(entries)
    if keys-set(entries):raise AssertionError('Missing bibliography keys '+str(keys-set(entries)))
    keys=sorted(keys,key=lambda k:re.search(r'\\textsc\{([^}]+)',entries[k])[1].lower())
    text='\\begin{thebibliography}{'+str(len(keys))+'}\n'+r"\providecommand{\enquote}[1]{``#1''}"+'\n'+r'\providecommand{\natexlab}[1]{#1}'+'\n\n'+'\n\n'.join(entries[k] for k in keys)+'\n\\end{thebibliography}\n'
    (R/'build'/(name+'.bbl')).write_text(text)

def response():
    run(['pandoc','-f','markdown','-t','latex','--wrap=auto','response.md','-o','build/response-body.tex'],'response-convert')
    body=(R/'build/response-body.tex').read_text()
    body=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:r'\nolinkurl{'+m[1].replace(r'\_','_')+'}',body)
    head=(R/'supp.tex').read_text().split(r'\input{sections/proofs67}')[0]
    head=head.replace(r'\externaldocument{build/ECTA}[ECTA.pdf]','').replace('Technical Supplement to Neural Bellman Operators','Response to the Referee: Neural Bellman Operators').replace('Neural Bellman Operators: Supplement','Response to the Referee')
    head=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'This response addresses the 11 October 2026 advisory report on R67. Revision R70 retains the original Neural Bellman Operators paper and integrates the separately frozen R69 execution, new deployment and cost-inference results, independent reconstruction and a point-by-point response.'+m[2],head,flags=re.S)
    (R/'response.tex').write_text(head+r'\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}'+'\n'+body+'\n\\end{document}\n')

def pdf_record(name,check=True):
    file=R/'build'/(name+'.pdf');info=subprocess.check_output(['pdfinfo',str(file)],text=True);text=subprocess.check_output(['pdftotext','-layout',str(file),'-'])
    (R/'build'/(name+'.txt')).write_bytes(text)
    result=dict(document=name,pages=int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1]),sha256=sha(file),text_sha256=hashlib.sha256(text).hexdigest())
    if check:
        log=(R/'build'/(name+'.log')).read_text(errors='replace')
        patterns={'undefined':r'(?:Reference|Citation).*undefined|There were undefined references','duplicate_labels':r'multiply defined|multiply-defined labels','missing_glyphs':r'Missing character:','overfull':r'Overfull \\[hv]box','fatal':r'^!|Fatal error'}
        bad={key:re.findall(pattern,log,re.M) for key,pattern in patterns.items()}
        if any(bad.values()):raise AssertionError((name,bad))
        result.update(checks=bad,font_substitutions=re.findall(r"Font shape `[^']+' undefined",log))
    return result

def compile_documents():
    for name in DOCS:(R/'build'/(name+'.bbl')).unlink(missing_ok=True)
    for iteration in range(4):
        for name in DOCS:
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build',name+'.tex'],name+'-pass'+str(iteration))
            if iteration==0 and name!='response':bibliography(name)
    return [pdf_record(name) for name in DOCS]

def main():
    begin=time.perf_counter();(R/'build').mkdir(exist_ok=True);(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    for exe in ('pdflatex','pandoc','pdfinfo','pdftotext'):
        if shutil.which(exe) is None:raise RuntimeError('Missing publication dependency '+exe)
    for p in (R/'code').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    keep=preservation();tests={}
    files=[(str(n),R.parent/f'2026-10-10-r{n}'/'code'/f'tests{n}.py') for n in (63,64,65,66)]
    files += [('67-scientific',OLD/'code/tests67.py'),('67-mathematical',OLD/'code/tests_math67.py'),('67-records',OLD/'code/tests_records67.py'),('69',R.parent/'2026-10-11-r69/code/tests69.py'),('70',R/'code/tests70.py')]
    for name,p in files:
        start=time.perf_counter();text=run([sys.executable,str(p)],'tests-'+name)
        m=re.search(r'Ran (\d+) tests?',text)
        if not m or not re.search(r'^OK\s*$',text,re.M):raise AssertionError('Missing unittest pass record '+name)
        tests[name]=dict(tests=int(m[1]),seconds=time.perf_counter()-start,status='passed')
    save(R/'audit/TESTS70.json',dict(status='passed',suites=tests,total=sum(x['tests'] for x in tests.values())))
    run([sys.executable,'code/audit70.py'],'independent-record-audit70')
    run([sys.executable,'code/tables70.py'],'tables70')
    response();documents=compile_documents()
    for d in documents:
        if d['document']=='ECTA' and d['pages']>45:raise AssertionError('Main article exceeds the 45-page revision target: '+str(d['pages']))
        if d['document']=='supp' and d['pages']>25:raise AssertionError('Supplement exceeds the 25-page revision target: '+str(d['pages']))
    companions=[]
    for name in ('ECTA','supp','response','prior-ECTA65','prior-supp65','development62','development-supp62','complete62','complete-supp62'):
        src=OLD/'build'/(name+'.pdf')
        if not src.exists():raise FileNotFoundError('Required retained companion '+str(src))
        dest='prior-'+name+'67' if name in ('ECTA','supp','response') else name
        shutil.copy2(src,R/'build'/(dest+'.pdf'))
        rec=pdf_record(dest,False);rec.update(source=str(src.relative_to(R.parent)),status='unchanged predecessor PDF',source_sha256=sha(src));companions.append(rec)
    keep=preservation();audit=json.loads((R/'audit/RESULT_AUDIT70.json').read_text());tables=json.loads((R/'audit/TABLES70.json').read_text())
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',(R/'ECTA.tex').read_text(),re.S)[1]
    if len(abstract.split())>150:raise AssertionError('Abstract length')
    record=dict(status='passed',tested_source_commit=commit,review_commit='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',reviewed_manuscript_commit='eacd3e217ae1e2e9ea6e154b48da7d103159d051',evidence_commit='2c07e464e81930f14b3122054704731ec5a139ff',documents=documents,companions=companions,tests=tests,total_tests=sum(x['tests'] for x in tests.values()),preservation=keep,independent_audit=audit,record_audit_sha256=sha(R/'audit/RESULT_AUDIT70.json'),all_precision_allocations_met=all(x['sampling_allocation_passed'] and x['numerical_allocation_passed'] for x in tables['inference']),abstract_words=len(abstract.split()),seconds=time.perf_counter()-begin,new_scientific_services=0,new_independent_inference_rows=0,network_used_by_builder=False,scope='Inherited and new regression suites; full frozen-record and independent cash-bin replay; exact training/validation and final inference checks; ordinary-source PDF builds. No independent regeneration of large optimal Bellman trees, universal numerical policy identity, external acceptance or formal proof-checker claim.',visual_scope='Compilation logs and extracted text; visual inspection is recorded separately only when actually performed.')
    save(R/'audit/RELEASE70.json',record)
    for p in R.rglob('*'):
        if p.is_file() and p.suffix.lower() in FONT_EXTENSIONS:raise AssertionError('Standalone font in delivery')
    print(json.dumps(record,indent=2))
if __name__=='__main__':main()
