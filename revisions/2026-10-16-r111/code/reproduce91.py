"""R91 source-bound reproduction; genuine failures never become release approval."""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, traceback
import reproduce90 as base
R=Path(__file__).resolve().parents[1]
ROOT=R.parents[1]
A=R/'audit/reproduction91';A.mkdir(parents=True,exist_ok=True)
base.AUDIT=A;base.LOGS=A/'logs'
BASE='9e06160b5464c41a5b84eaab9c3c4d171fc22832'
REVIEW='b030d87d7e96440eb25a3178c94ee6a87940cdb0'
DOCS=base.DOCS

def save(path,obj):base.save(path,obj)
def digest(path):return base.digest(path)
def run(script,*args):return base.command([sys.executable,'code/'+script+'.py',*args],script+'91')[0]
def bibcheck():
    text=(R/'references91-canonical.bib').read_text();keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',text)
    if len(keys)!=len(set(keys)):raise AssertionError('Duplicate current bibliography key')
    for doc in ('ECTA','supp','appendix'):
        if re.findall(r'\\bibliography\{([^}]+)\}',(R/(doc+'.tex')).read_text())!=['references91-canonical']:
            raise AssertionError('Unexpected active bibliography '+doc)
    return {'entries':len(keys),'canonical_sha256':digest(R/'references91-canonical.bib')}

def response_source(root):
    base.command(['pandoc','response.md','-f','markdown','-t','latex','-o','build/response-body.tex'],'response91-'+('current' if root==R else 'clean'),root)
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
base.response_source=response_source

def sources():
    result={}
    for p in sorted(R.rglob('*')):
        if not p.is_file():continue
        parts=p.relative_to(R).parts
        if any(v in ('build','audit','preserved','publication','__pycache__') or v.startswith('results') for v in parts):continue
        if p.suffix in ('.py','.tex','.bib','.cls','.cfg','.bst','.md','.json'):result[str(p.relative_to(R))]=digest(p)
    return result

def table_reconstruction():
    old=R/'preserved/R90-audit-before-replay'
    if not old.exists():
        shutil.copytree(R/'audit',old,ignore=shutil.ignore_patterns('reproduction91','*91*'))
    out=[]
    for script,args in (('frontier83',()),('tables83',()),('tables84',()),
                        ('analysis89',()),('math89',()),('transport90',('--write',)),
                        ('tests91',('--write',)),('tables91',())):
        out.append(run(script,*args))
    missing=[]
    for p in (R/'sections').glob('*.tex'):
        for name in re.findall(r'\\input\{(tables/[^}]+)\}',p.read_text()):
            if not (R/(name+'.tex')).is_file():missing.append({'section':p.name,'table':name})
    if missing:raise AssertionError(('Missing table closure',missing))
    return {'status':'passed','runs':out,'table_hashes':{p.name:digest(p) for p in sorted((R/'tables').glob('*.tex'))},'new_fit_attempts':0,'new_independent_economic_rows':0}

def main():
    source=base.git('rev-parse','HEAD');checks={};documents={};started=time.perf_counter()
    save(A/'SOURCE91.json',{'source_commit':source,'review_commit':REVIEW,'baseline_commit':BASE,'files':sources()})
    def check(name,fn):
        start=time.perf_counter()
        try:
            result=fn();status='failed' if isinstance(result,dict) and result.get('status')=='failed' else 'passed'
            checks[name]={'status':status,'seconds':time.perf_counter()-start,'result':result}
        except Exception as e:
            text=traceback.format_exc();print(text,flush=True)
            save(A/(name+'-FAILURE91.json'),{'source_commit':source,'error':str(e),'traceback':text})
            checks[name]={'status':'failed','seconds':time.perf_counter()-start,'error':str(e)}
        save(A/'PROGRESS91.json',{'source_commit':source,'checks':checks})
    check('bibliography',bibcheck)
    mandatory=('tests72','tests_publication72','tests73','tests77','tests78','tests79','tests80','tests81','tests82','tests83','tests84','tests86','tests89','tests90','tests91')
    for name in mandatory:check(name,lambda name=name:base.run_tests(name))
    check('independent84',lambda:run('verify84'))
    check('independent-original-law85',lambda:run('prospective85','--replay'))
    check('all-required-tables',table_reconstruction)
    def compile_current():
        nonlocal documents
        documents=base.compile_docs(R,'current91');save(A/'DOCUMENTS91.json',documents)
        return {'status':'passed' if all(x['status']=='passed' for x in documents.values()) else 'failed','documents':documents}
    check('current-documents',compile_current)
    if documents:
        check('clean-typesetting',base.clean_compile)
        if (A/'CLEAN90.json').exists():shutil.copy2(A/'CLEAN90.json',A/'CLEAN91.json')
    else:checks['clean-typesetting']={'status':'failed','error':'No complete current PDF record'}
    def preservation():
        paths=base.git('diff','--name-only',BASE,'HEAD').splitlines()
        outside=[p for p in paths if not p.startswith(('revisions/2026-10-13-r91/','.github/workflows/nbo-r91-'))]
        if outside:raise AssertionError(('Modified earlier tree',outside))
        return {'status':'passed','outside_new_scope':outside}
    check('earlier-tree-preservation',preservation)
    out={'revision':'R91','source_commit':source,'baseline_commit':BASE,'review_commit':REVIEW,'checks':checks,'documents':documents,
         'new_fit_attempts':0,'new_independent_economic_rows':0,'new_tests86_scope':'14 R91-authored regressions for inherited R86 claims; not a recovered historical suite',
         'visual_inspection':{'status':'not_performed','scope':'Compiler checks and rendered files do not establish visual approval'},
         'status':'compiled_candidate' if all(x['status']=='passed' for x in checks.values()) else 'verification_failed','seconds':time.perf_counter()-started}
    save(A/'VERIFICATION91.json',out)
    print(json.dumps({'source_commit':source,'status':out['status'],'checks':{k:v['status'] for k,v in checks.items()},'documents':documents},indent=2),flush=True)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');args=p.parse_args()
    if args.prepare:
        import apply91;apply91.main()
    else:sys.exit(0 if main()['status']=='compiled_candidate' else 1)
