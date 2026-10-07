"""Assemble a complete R46 revision from immutable materialized predecessors.

The build reconstructs frozen records but never reruns or overwrites the study.
No source capsule, expiring artifact or network access is required to rebuild.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1];ROOT=R.parent.parent
BASE=R.parent/'2026-10-07-r45';OLD=R.parent/'2026-10-07-r44'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run(args,log,cwd=R,env=None):
    with log.open('w') as out:
        result=subprocess.run(args,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(f'{args}; inspect {log}')
    return log.read_text(errors='replace')


def labels(root,name,seen=None):
    seen=set() if seen is None else seen
    path=root/name
    if not path.suffix:path=path.with_suffix('.tex')
    if path in seen:return set()
    seen.add(path);text=path.read_text();answer=set(re.findall(r'\\label\{([^}]+)\}',text))
    for child in re.findall(r'\\input\{([^}]+)\}',text):answer |= labels(root,child,seen)
    return answer


def main(release=False):
    for d in ('audit','build','tables','sections','preserved'):(R/d).mkdir(exist_ok=True)
    for name in ('preamble.tex','econsocart.cls','econsocart.cfg','ecta-fullname.bst','references.bib'):
        shutil.copy2(BASE/name,R/name)
    for dirname in ('sections','tables'):
        for p in (BASE/dirname).glob('*.tex'):shutil.copy2(p,R/dirname/p.name)
    shutil.copytree(BASE/'preserved',R/'preserved',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ('ECTA.tex','supp.tex','response.md'):
        shutil.copy2(BASE/name,R/'preserved'/('R45-'+name))
    maintext=(BASE/'ECTA.tex').read_text()
    abstract='This paper develops Neural Bellman Operators for policy evaluation and feasible improvement in controlled economies. Centered continuation errors connect economic transport and full-policy loss. A deterministic own-future ReLU construction carries the feasible actions attaining its labels through the minimum circuit. The resulting policy admits a one-sided residual certificate and a smaller primitive resource budget than a separated critic--actor account. Exact witness compilation and an explicit numerical-selection allowance make that guarantee executable. Feasible-witness transport extends the construction to endogenous action constraints with an explicit repair budget. A predeclared matched study compares complete certificate frontiers with strengthened neural and spline baselines. Retained-policy verification and direct expected-cost comparisons remain distinct. The evidence separates sharper certification from work-to-target and policy-cost superiority. Controlled-diffusion, recursive-preference and game formulations retain their application-specific conditions.'
    start=maintext.index('\\begin{abstract}')+len('\\begin{abstract}');end=maintext.index('\\end{abstract}',start)
    maintext=maintext[:start]+'\n'+abstract+'\n'+maintext[end:]
    anchor='The numerical implementation starts from economic primitives.'
    paragraph="The action that attains a Bellman label supplies additional information. We retain its index through the ReLU minimum circuit and deploy that action when its cone is selected. A one-sided policy sandwich then avoids charging the separate actor and critic accounts twice. Both the nearest-node neural ablation and the spline receive a strengthened certificate. Their complete matched frontiers isolate certificate sharpness from first-target work and actual policy cost.\n\n"
    maintext=maintext.replace(anchor,paragraph+anchor,1)
    maintext=maintext.replace('\\section{Economic applications and conclusion}','\\input{sections/witness}\n\\input{sections/feasible-witness}\n\n\\section{Economic applications and conclusion}',1)
    maintext=maintext.replace('The present main article is the authoritative R45 exposition.','The present main article is the authoritative R46 exposition, extending the complete R45 manuscript.')
    maintext=maintext.replace('All R44 main-article labels are retained.','All active R45 labels, including the retained R44 labels, are preserved. The response distinguishes the latest supplemental review of the incomplete R43 snapshot from the earlier substantive R44 report. The new witness construction, execution allowance and matched frontier are stated and proved in this revision.')
    (R/'ECTA.tex').write_text(maintext)
    supplement=(BASE/'supp.tex').read_text()
    supplement=supplement.replace('for the R45 revision, retaining the R44 results:', 'for the R46 revision, retaining the R44 and R45 results:')
    supplement=supplement.replace('\\bibliographystyle{ecta-fullname}','\\input{sections/witness-proof}\n\\input{sections/feasible-proof}\n\\bibliographystyle{ecta-fullname}',1)
    (R/'supp.tex').write_text(supplement)
    run([sys.executable,str(R/'code/audit.py')],R/'audit/aggregate.log')
    preservation={}
    for name in ('ECTA.tex','supp.tex'):
        before=labels(BASE,name);after=labels(R,name)
        assert before<=after,(name,sorted(before-after))
        preservation[name]={'baseline_sha256':H(BASE/name),'original_active_labels':sorted(before),'missing_labels':[]}
    retained={}
    for p in (BASE/'preserved').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            q=R/'preserved'/p.relative_to(BASE/'preserved');assert H(p)==H(q)
            retained[str(q.relative_to(R))]=H(q)
    preservation.update({'baseline_commit':'336ea58decb4fae486efa41bb86e69a28879d9d6','preserved_files':retained,'historical_deletions':[]})
    (R/'audit/PRESERVATION.json').write_text(json.dumps(preservation,indent=2,sort_keys=True)+'\n')
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    env['PYTHONPATH']=os.pathsep.join([str(BASE/'preserved/R41/code'),str(BASE/'preserved/R41/vendor/r38/code'),env.get('PYTHONPATH','')])
    run([sys.executable,str(R/'code/tests.py')],R/'audit/tests46.log',env=env)
    tests={'R46':json.loads((R/'audit/TESTS_R46.json').read_text())}
    for name,path,count in [('R45',BASE,13),('R44',OLD,14)]:
        text=run([sys.executable,'-m','unittest','discover','-s',str(path/'code'),'-p','tests.py','-v'],R/'audit'/f'tests{name}.log',env=env)
        match=re.search(r'Ran (\d+) tests?',text);assert match and int(match[1])==count
        tests[name]={'tests':count,'success':True,'mode':'unittest discovery; historical records not modified'}
    text=run([sys.executable,'-m','unittest','discover','-s',str(R/'code'),'-p','test_feasible.py','-v'],R/'audit/tests-feasible.log',env=env)
    match=re.search(r'Ran ([0-9]+) tests?',text);assert match and int(match[1])==8
    tests['feasible_transport']={'tests':8,'success':True,'mode':'independent exact rational checks; not a new performance catalogue'}
    body=subprocess.check_output(['pandoc','-f','gfm','-t','latex',str(R/'response.md')],text=True)
    body=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:r'\nolinkurl{'+m[1].replace(r'\_','_')+'}',body)
    front=r'''\documentclass[ecta,nameyear,draft]{econsocart}
\input{preamble}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\begin{document}
\begin{frontmatter}\title{Response to the Referee: Neural Bellman Operators}
\runtitle{Neural Bellman Operators: Response}
\begin{aug}\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}}\address[id=add1]{Peking University}\end{aug}
\end{frontmatter}
'''
    (R/'response.tex').write_text(front+body+'\n\\end{document}\n')
    for key in ('TEXINPUTS','BIBINPUTS','BSTINPUTS'):env[key]=str(R)+':'+env.get(key,'')
    for iteration in range(3):
        for name in ('ECTA','supp','response'):
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(R/'build'),str(R/(name+'.tex'))],R/'audit'/f'tex-{name}-{iteration}.log',env=env)
            if iteration==0 and r'\bibdata' in (R/'build'/(name+'.aux')).read_text():
                run([shutil.which('bibtex.original') or 'bibtex','build/'+name],R/'audit'/f'bib-{name}.log',env=env)
    compilation=[]
    for name in ('ECTA','supp','response'):
        text=(R/'build'/(name+'.log')).read_text(errors='replace')
        bad=[s for s in text.splitlines() if ('undefined' in s.lower() and ('reference' in s.lower() or 'citation' in s.lower())) or any(t in s for t in ('multiply-defined labels','Missing character:','Overfull \\hbox','Overfull \\vbox'))]
        assert not bad,(name,bad)
        info=subprocess.check_output(['pdfinfo',str(R/'build'/(name+'.pdf'))],text=True)
        match=re.search(r'^Pages:\s+(\d+)',info,re.M);assert match
        compilation.append({'document':name,'pages':int(match[1]),'pdf_sha256':H(R/'build'/(name+'.pdf')),'undefined_references':0,'duplicate_labels':0,'overfull_boxes':0,'missing_characters':0})
    if release:
        report=ROOT/'reviews/2026-10-07-econometrica-numerical-methods-r43/referee_report.md'
        raw=report.read_bytes();assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()=='bb6b050e1ac3feea091f8800e874e9f858281108'
        for n in ('ECTA.tex','supp.tex'):assert '2026-10-07-r46/'+n in (ROOT/n).read_text()
        assert 'R46' in (ROOT/'README.md').read_text()
        run(['git','diff','--exit-code','--','revisions/2026-10-07-r44','revisions/2026-10-07-r45'],R/'audit/historical-diff.log',cwd=ROOT,env=env)
    audit={'revision':'R46','latest_review_commit':'9a1ce0502a2cb8f57c697d1df9ba796da0403474','substantive_review_commit':'5d4eca82b5477c4f0305f0f90bf9adc1635ec5de',
           'manuscript_baseline':'336ea58decb4fae486efa41bb86e69a28879d9d6','study_source_commit':'f91835f150fdf981f5bab43416121583444a36c7',
           'study_evidence_commit':'257a7b207adf72f07d62d025c93d71a6e1ecb2d2','study_run':37623758585,'study_artifact':11483102637,
           'study_artifact_sha256':'8cb0fa519bb5e9c15760541d29ca3af5312e73ca728a39ea81a5fc521ba7235a',
           'integration_date':'2026-10-08','integration_tests_scope':'feasible state-dependent witness transport',
           'publication_source_commit':os.environ.get('GITHUB_SHA','local-build'),'publication_run':os.environ.get('GITHUB_RUN_ID'),
           'tests':tests,'total_tests':sum(a['tests'] for a in tests.values()),'compilation':compilation,'release_entry_and_review_checks':release,
           'results':json.loads((R/'audit/PUBLICATION_SUMMARY.json').read_text()),'peer_or_editorial_approval':False}
    (R/'audit/RELEASE_AUDIT.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    manifest={str(p.relative_to(R)):H(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='FILES_SHA256.json'}
    (R/'audit/FILES_SHA256.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'compilation':compilation,'total_tests':audit['total_tests'],'release':release},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--release',action='store_true');main(p.parse_args().release)
