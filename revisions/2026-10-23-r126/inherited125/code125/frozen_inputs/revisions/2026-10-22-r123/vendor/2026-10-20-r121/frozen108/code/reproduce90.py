"""R90 reproduction. Failed/missing checks remain failures; visual approval is separate."""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys,tempfile,time,traceback
R=Path(__file__).resolve().parents[1]
ROOT=R.parents[1]
BASE='21883cbed1911f3da53eba2591c02110f812885b'
R89_DATA='d8385366c26b8bf696518c5d59ff7a1c85272ac2'
DOCS=('ECTA','supp','appendix','response')
AUDIT=R/'audit';LOGS=AUDIT/'r90-logs'

def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def command(argv,label,cwd=R,timeout=2400):
    LOGS.mkdir(parents=True,exist_ok=True);p=LOGS/(label+'.log');start=time.perf_counter()
    with p.open('w') as f:
        f.write('COMMAND '+json.dumps(list(map(str,argv)))+'\n');f.flush()
        try:out=subprocess.run(list(map(str,argv)),cwd=cwd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout,check=False)
        except subprocess.TimeoutExpired:
            f.write('\nTIMEOUT\n');raise
    text=p.read_text(errors='replace')
    print(label,'exit',out.returncode,'seconds',round(time.perf_counter()-start,3),flush=True)
    if out.returncode:
        print(text[-14000:],flush=True);raise RuntimeError(f'{label}: exit {out.returncode}; log {p.relative_to(R)}')
    return {'returncode':out.returncode,'seconds':time.perf_counter()-start,'log':str(p.relative_to(R)),'log_sha256':digest(p)},text

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def recover():
    """Import only frozen execution records into R90, never into earlier directories."""
    target=R/'results89'
    command(['git','fetch','--no-tags','--depth=1','origin',R89_DATA],'fetch-frozen-r89',ROOT)
    prefix='revisions/2026-10-13-r89/results89'
    paths=git('ls-tree','-r','--name-only',R89_DATA,'--',prefix).splitlines()
    if not paths:raise AssertionError('The pinned executed R89 tree has no scientific records')
    with tempfile.TemporaryDirectory(prefix='nbo-r90-import-') as folder:
        archive=Path(folder)/'records.tar'
        with archive.open('wb') as f:subprocess.run(['git','archive',R89_DATA,prefix],cwd=ROOT,stdout=f,check=True)
        import tarfile
        with tarfile.open(archive) as tar:tar.extractall(folder,filter='data')
        source=Path(folder)/prefix
        recovered=[]
        for p in sorted(source.rglob('*')):
            if not p.is_file():continue
            q=target/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True)
            if q.exists() and digest(q)!=digest(p):raise AssertionError('Conflicting preserved R89 record '+str(q))
            if not q.exists():shutil.copy2(p,q)
            recovered.append({'path':str(q.relative_to(R)),'sha256':digest(q)})
    out={'status':'passed','source_commit':R89_DATA,'source_directory':prefix,'files':recovered,'new_fit_attempts':0,'new_independent_rows':0}
    save(AUDIT/'IMPORT90.json',out)
    command([sys.executable,'code/integrate90.py'],'integrate90')
    print('AVAILABLE CODE',','.join(p.name for p in sorted((R/'code').glob('*.py'))),flush=True)
    return out

def bibliography_inventory():
    # The active bibliography remains ordinary BibTeX, not an inherited .bbl.
    seen={};duplicates=[]
    for name in ('references.bib','references78.bib','references84.bib','references90.bib'):
        for key in re.findall(r'@\w+\s*\{\s*([^,\s]+)',(R/name).read_text()):
            if key in seen:duplicates.append((key,seen[key],name))
            seen[key]=name
    if duplicates:raise AssertionError(('Duplicate active bibliography keys',duplicates))
    return {'entries':len(seen),'keys':seen}

def run_tests(name):
    record,text=command([sys.executable,'code/'+name+'.py'],name)
    found=re.search(r'Ran (\d+) tests?',text)
    if not found or not re.search(r'^OK\s*$',text,re.M) or re.search(r'\bskipped\b',text):
        raise AssertionError('Incomplete/unqualified unittest output '+name)
    record.update(status='passed',tests=int(found[1]));return record

def table_reconstruction():
    output=[]
    # This deterministic reconstruction is not a new sample or a refit.
    if not (R/'results85/SUMMARY85.json').is_file():
        if (R/'results85').exists() and any((R/'results85').iterdir()):
            raise AssertionError('Partial R85 reconstruction retained: inspect before resuming')
        if (R/'results85').exists():(R/'results85').rmdir()
        record,_=command([sys.executable,'code/prospective85.py'],'reconstruct-frozen85')
        output.append(record)
    record,_=command([sys.executable,'code/analysis89.py'],'all-economic-and-shared-tables89');output.append(record)
    record,_=command([sys.executable,'code/math89.py'],'math89-exact-fixtures');output.append(record)
    record,_=command([sys.executable,'code/transport90.py','--write'],'transport90-exact-fixtures');output.append(record)
    mandatory=('all-prospective86','prices86','work89','timing89','all-timing89','diagnostics89','transport90')
    for name in mandatory:
        p=R/'tables'/(name+'.tex')
        if not p.is_file() or not p.stat().st_size:raise AssertionError('Missing required table '+name)
    return {'status':'passed','runs':output,'mandatory_table_hashes':{name:digest(R/'tables'/(name+'.tex')) for name in mandatory},'new_fit_attempts':0,'new_independent_rows':0}

def response_source(root):
    backup=R/'preserved/R89-entry-points/response.tex'
    if root==R and (R/'response.tex').exists() and not backup.exists():
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'response.tex',backup)
    command(['pandoc','response.md','-f','markdown','-t','latex','-o','build/response-body.tex'],'response-convert-'+('current' if root==R else 'clean'),root)
    head=r'''\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[margin=1in]{geometry}
\usepackage{mathpazo,microtype,amsmath,amssymb,array,longtable,booktabs,xurl}
\usepackage[colorlinks,linkcolor=blue,urlcolor=blue]{hyperref}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setlength{\emergencystretch}{3em}
\begin{document}
\input{build/response-body.tex}
\end{document}
'''
    (root/'response.tex').write_text(head)

def compile_docs(root,label):
    build=root/'build';build.mkdir(parents=True,exist_ok=True)
    for p in build.iterdir():
        if p.is_file() and p.suffix in ('.aux','.bbl','.blg','.brf','.log','.out','.toc','.pdf','.txt'):p.unlink()
    response_source(root)
    for turn in range(5):
        for name in DOCS:
            command(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory=build',name+'.tex'],f'{label}-{name}-pass{turn}',root)
            if turn==0 and name!='response':command(['bibtex','build/'+name],f'{label}-{name}-bibtex',root)
    output={}
    for name in DOCS:
        log=(build/(name+'.log')).read_text(errors='replace')
        bad={k:re.findall(pattern,log,re.I) for k,pattern in {
             'undefined':r'(?:Citation|Reference)[^\n]*undefined|There were undefined',
             'duplicates':r'multiply.defined|destination with the same identifier',
             'missing_glyphs':r'Missing character:',
             'fatal':r'Fatal error|Emergency stop',
             'overfull':r'Overfull \\[hv]box[^\n]*'}.items()}
        if name!='response':
            bbl=build/(name+'.bbl')
            if not bbl.is_file() or not re.search(r'\\bibitem',bbl.read_text()):bad['bibliography']=['Absent or empty current bibliography']
        info=subprocess.check_output(['pdfinfo',str(build/(name+'.pdf'))],text=True)
        pages=re.search(r'Pages:\s+(\d+)',info)
        command(['pdftotext','-layout',str(build/(name+'.pdf')),str(build/(name+'.txt'))],label+'-'+name+'-text',root)
        output[name]={'pdf_sha256':digest(build/(name+'.pdf')),'text_sha256':digest(build/(name+'.txt')),'pages':int(pages[1]) if pages else None,'diagnostics':bad,'status':'passed' if not any(bad.values()) else 'failed'}
        if name!='response':output[name]['bibliography_sha256']=digest(build/(name+'.bbl'))
    return output

def source_closure(root):
    wanted=[]
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix not in ('.tex','.bib','.bst','.cls','.cfg','.md','.png','.jpg','.jpeg','.eps'):continue
        parts=p.relative_to(root).parts
        if any(x in ('build','audit','preserved','publication') or x.startswith('results') for x in parts):continue
        wanted.append(p)
    return wanted

def clean_compile():
    with tempfile.TemporaryDirectory(prefix='nbo-r90-clean-') as folder:
        dest=Path(folder)/'paper';dest.mkdir()
        sources=source_closure(R)
        for p in sources:
            q=dest/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        report=compile_docs(dest,'clean')
        comparison={n:{'pdf_identical':digest(R/'build'/(n+'.pdf'))==report[n]['pdf_sha256'],
                       'text_identical':digest(R/'build'/(n+'.txt'))==report[n]['text_sha256']} for n in DOCS}
        out={'status':'passed' if all(v['pdf_identical'] and v['text_identical'] for v in comparison.values()) and all(v['status']=='passed' for v in report.values()) else 'failed','source_files':len(sources),'source_sha256':{str(p.relative_to(R)):digest(p) for p in sources},'documents':report,'comparison':comparison,'scope':'Clean typesetting reconstruction; scientific replay is a distinct recorded check.'}
        save(AUDIT/'CLEAN90.json',out);return out

def manifest():
    checks={};began=time.perf_counter();source=git('rev-parse','HEAD')
    def check(name,fn):
        start=time.perf_counter()
        try:
            result=fn();checks[name]={'status':'passed','seconds':time.perf_counter()-start,'result':result}
            if isinstance(result,dict) and result.get('status')=='failed':checks[name]['status']='failed'
        except Exception as ex:
            text=traceback.format_exc();print(text,flush=True);save(AUDIT/(name+'-FAILURE90.json'),{'error':str(ex),'traceback':text,'source_commit':source})
            checks[name]={'status':'failed','seconds':time.perf_counter()-start,'error':str(ex)}
        save(AUDIT/'PROGRESS90.json',{'source_commit':source,'checks':checks})
    check('bibliography',bibliography_inventory)
    for name in ('tests72','tests_publication72','tests73','tests77','tests78','tests79','tests80','tests81','tests82','tests83','tests84','tests86','tests89','tests90'):
        check(name,lambda name=name:run_tests(name))
    check('independent84',lambda:command([sys.executable,'code/verify84.py'],'independent84')[0])
    check('tables',table_reconstruction)
    if (R/'results85/SUMMARY85.json').is_file():
        check('independent-original-law85',lambda:command([sys.executable,'code/prospective85.py','--replay'],'independent-original-law85')[0])
    else:checks['independent-original-law85']={'status':'failed','error':'No reconstructed source-bound R85 summary'}
    documents={}
    def current():
        nonlocal documents
        documents=compile_docs(R,'current');save(AUDIT/'DOCUMENTS90.json',documents)
        return {'status':'passed' if all(v['status']=='passed' for v in documents.values()) else 'failed','documents':documents}
    check('current-documents',current)
    if documents:check('clean-typesetting',clean_compile)
    else:checks['clean-typesetting']={'status':'failed','error':'Current compilation did not complete'}
    paths=git('diff','--name-only',BASE,'HEAD').splitlines()
    outside=[p for p in paths if not p.startswith(('revisions/2026-10-13-r90/','.github/workflows/nbo-r90-'))]
    checks['earlier-tree-preservation']={'status':'passed' if not outside else 'failed','outside_new_scope':outside}
    out={'revision':'R90','source_commit':source,'baseline_commit':BASE,'review_commit':'b030d87d7e96440eb25a3178c94ee6a87940cdb0','checks':checks,'documents':documents,'new_fit_attempts':0,'new_independent_economic_rows':0,'visual_inspection':{'status':'not_performed','scope':'No rendered-page inspection is inferred from software checks.'},'full_release_issued':False,'status':'compiled_candidate' if all(c['status']=='passed' for c in checks.values()) else 'verification_failed','seconds':time.perf_counter()-began}
    save(AUDIT/'VERIFICATION90.json',out)
    print(json.dumps({'status':out['status'],'source_commit':source,'checks':{k:v['status'] for k,v in checks.items()},'documents':documents},indent=2),flush=True)
    return out

def require_visual():
    report=json.loads((AUDIT/'VERIFICATION90.json').read_text());visual=json.loads((AUDIT/'VISUAL90.json').read_text())
    if report['status']!='compiled_candidate' or visual.get('status')!='passed':raise AssertionError('Incomplete current verification or visual approval')
    for name in DOCS:
        value=digest(R/'build'/(name+'.pdf'))
        if value!=report['documents'][name]['pdf_sha256'] or value!=visual['documents'][name]['pdf_sha256']:raise AssertionError('Stale visual or document hash '+name)
    print('Current numerical, clean reconstruction and visual records match; no editorial acceptance is implied.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--require-visual',action='store_true');args=parser.parse_args()
    if args.prepare:recover()
    elif args.require_visual:require_visual()
    else:
        report=manifest();sys.exit(0 if report['status']=='compiled_candidate' else 1)
