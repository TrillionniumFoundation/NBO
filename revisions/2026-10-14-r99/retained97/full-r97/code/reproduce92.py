"""Source-bound R92 tests, two independent replays and clean publication."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,tempfile,time,traceback
import reproduce90 as b
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
A=R/'audit/reproduction92';A.mkdir(parents=True,exist_ok=True)
b.AUDIT=A;b.LOGS=A/'logs'
BASE='368a9e754f5de04eb1957e152f22d6ef2c34f2fe'
REVIEW='b030d87d7e96440eb25a3178c94ee6a87940cdb0'
DOCS=b.DOCS

def run(name,*args):return b.command([sys.executable,'code/'+name+'.py',*args],name+'-R92')[0]
def save(p,x):b.save(p,x)
def sources():
    out={}
    for p in sorted(R.rglob('*')):
        if not p.is_file():continue
        parts=p.relative_to(R).parts
        if any(v in ('build','audit','preserved','publication','__pycache__') or v.startswith('results') for v in parts):continue
        if p.suffix in ('.py','.tex','.bib','.bst','.cls','.cfg','.md','.json'):out[str(p.relative_to(R))]=b.digest(p)
    return out

def response(root):
    b.command(['pandoc','response.md','-f','markdown','-t','latex','-o','build/response-body.tex'],'response92-'+('current' if root==R else 'clean'),root)
    head=r'''\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[margin=1in]{geometry}
\usepackage{mathpazo,microtype,amsmath,amssymb,array,longtable,booktabs,xurl}
\usepackage[colorlinks,linkcolor=blue,urlcolor=blue]{hyperref}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setlength{\emergencystretch}{3em}
\ifdefined\pdfinfoomitdate\pdfinfoomitdate=1\fi
\ifdefined\pdfsuppressptexinfo\pdfsuppressptexinfo=15\fi
\ifdefined\pdftrailerid\pdftrailerid{}\fi
\begin{document}
\input{build/response-body.tex}
\end{document}
'''
    (root/'response.tex').write_text(head)
b.response_source=response

def bibliography():
    path=R/'references92-canonical.bib';keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',path.read_text())
    if len(keys)!=len(set(keys)) or not keys:raise AssertionError('Duplicate or empty current bibliography')
    for n in ('ECTA','supp','appendix'):
        if re.findall(r'\\bibliography\{([^}]+)\}',(R/(n+'.tex')).read_text())!=['references92-canonical']:raise AssertionError('Active bibliography '+n)
    return {'status':'passed','entries':len(keys),'sha256':b.digest(path)}

def new_science():
    if (R/'results92').exists():
        dest=R/'preserved'/('R92-earlier-execution-'+str(time.time_ns()));dest.parent.mkdir(exist_ok=True)
        shutil.move(str(R/'results92'),str(dest))
    return run('study92')

def clean_science():
    with tempfile.TemporaryDirectory(prefix='nbo-r92-science-') as temp:
        dest=Path(temp)/'paper';(dest/'code').mkdir(parents=True)
        for name in ('centered92.py','study92.py','independent92.py'):
            shutil.copy2(R/'code'/name,dest/'code'/name)
        b.command([sys.executable,'code/study92.py'],'clean-science92',dest)
        b.command([sys.executable,'code/independent92.py'],'clean-independent92',dest)
        expected={p.name:b.digest(p) for p in (R/'results92').glob('case-*.json')}
        actual={p.name:b.digest(p) for p in (dest/'results92').glob('case-*.json')}
        if expected!=actual or len(expected)!=84:raise AssertionError('Clean deterministic catalogue mismatch')
        audit=json.loads((dest/'audit/reproduction92/INDEPENDENT92.json').read_text())
        if audit['status']!='passed':raise AssertionError('Clean independent checker did not pass')
        out={'status':'passed','cases_identical':len(expected),'case_sha256':expected,'independent_check':audit,
             'scope':'Clean new-science replay from three ordinary code files; deterministic replay is not a new observation.'}
        save(A/'CLEAN_SCIENCE92.json',out);return out

def tables():
    out=[]
    for name,args in (('frontier83',()),('tables83',()),('tables84',()),('analysis89',()),('math89',()),('transport90',('--write',)),('tests91',('--write',)),('tables91',()),('tables92',())):
        out.append(run(name,*args))
    missing=[]
    for p in (R/'sections').glob('*.tex'):
        for name in re.findall(r'\\input\{(tables/[^}]+)\}',p.read_text()):
            if not (R/(name+'.tex')).is_file():missing.append((p.name,name))
    if missing:raise AssertionError(('Missing table closure',missing))
    return {'status':'passed','runs':out,'table_sha256':{p.name:b.digest(p) for p in sorted((R/'tables').glob('*.tex'))}}

def preservation():
    changed=b.git('diff','--name-only',BASE,'HEAD').splitlines()
    bad=[p for p in changed if not p.startswith(('revisions/2026-10-13-r92/','.github/workflows/nbo-r92-'))]
    if bad:raise AssertionError(('Earlier paths changed',bad))
    for name in ('econsocart.cls','econsocart.cfg','ecta-fullname.bst'):
        data=subprocess.check_output(['git','show',BASE+':revisions/2026-10-13-r91/'+name],cwd=ROOT)
        if data!=(R/name).read_bytes():raise AssertionError('Changed author class '+name)
    old=R/'preserved/R91-entry-points'
    retained={}
    for name in ('ECTA.tex','supp.tex','appendix.tex'):
        before=re.findall(r'\\input\{(sections/[^}]+)\}',(old/name).read_text());after=re.findall(r'\\input\{(sections/[^}]+)\}',(R/name).read_text())
        if any(x not in after for x in before):raise AssertionError('Dropped inherited active section')
        retained[name]={'inherited':len(before),'current':len(after)}
    return {'status':'passed','outside_scope':bad,'active_sections':retained,'class_files_unchanged':True}

def main():
    if not (R/'audit/INTEGRATION92.json').exists():raise AssertionError('Ordinary integrated source commit required')
    source=b.git('rev-parse','HEAD');start=time.perf_counter();checks={};documents={}
    save(A/'SOURCE92.json',{'source_commit':source,'baseline_commit':BASE,'review_commit':REVIEW,'files':sources()})
    def check(name,fn):
        t=time.perf_counter()
        try:
            value=fn();status='failed' if isinstance(value,dict) and value.get('status')=='failed' else 'passed'
            checks[name]={'status':status,'seconds':time.perf_counter()-t,'result':value}
        except Exception as e:
            tb=traceback.format_exc();print(tb,flush=True);save(A/(name+'-FAILURE92.json'),{'error':str(e),'traceback':tb,'source_commit':source})
            checks[name]={'status':'failed','seconds':time.perf_counter()-t,'error':str(e)}
        save(A/'PROGRESS92.json',{'source_commit':source,'checks':checks})
    check('bibliography',bibliography)
    mandatory=('tests72','tests_publication72','tests73','tests77','tests78','tests79','tests80','tests81','tests82','tests83','tests84','tests86','tests89','tests90','tests91','tests92')
    for name in mandatory:check(name,lambda name=name:b.run_tests(name))
    check('new-science92',new_science)
    check('independent92',lambda:run('independent92'))
    check('clean-new-science92',clean_science)
    check('independent84',lambda:run('verify84'))
    check('independent-original-law85',lambda:run('prospective85','--replay'))
    check('all-required-tables',tables)
    def current():
        nonlocal documents
        documents=b.compile_docs(R,'current92');save(A/'DOCUMENTS92.json',documents)
        return {'status':'passed' if all(v['status']=='passed' for v in documents.values()) else 'failed','documents':documents}
    check('current-documents',current)
    if documents:
        check('clean-typesetting',b.clean_compile)
        if (A/'CLEAN90.json').exists():shutil.copy2(A/'CLEAN90.json',A/'CLEAN92.json')
    else:checks['clean-typesetting']={'status':'failed','error':'No complete current document record'}
    check('earlier-tree-preservation',preservation)
    out={'revision':'R92','source_commit':source,'baseline_commit':BASE,'review_commit':REVIEW,'checks':checks,'documents':documents,
         'new_fit_attempts':0,'new_independent_economic_rows':0,'seconds':time.perf_counter()-start,
         'visual_inspection':{'status':'not_performed','scope':'Actual PDF inspection must be separately recorded against these hashes'},
         'status':'compiled_candidate' if all(v['status']=='passed' for v in checks.values()) else 'verification_failed'}
    save(A/'VERIFICATION92.json',out)
    concise={'status':out['status'],'source_commit':source,'checks':{k:v['status'] for k,v in checks.items()},'test_counts':{k:v.get('result',{}).get('tests') for k,v in checks.items() if k.startswith('tests')},'documents':documents}
    save(A/'SUMMARY92.json',concise);print(json.dumps(concise,indent=2),flush=True)
    return out
if __name__=='__main__':sys.exit(0 if main()['status']=='compiled_candidate' else 1)
