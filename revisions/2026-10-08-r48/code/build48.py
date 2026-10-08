"""Build the R48 revision from ordinary committed sources and frozen records.

No network, sampling, training, historical writes or artifact decoding.
"""
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];BASE=R/'preserved/R47'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):
    Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n')
def run(args,log,env,cwd=R):
    q=subprocess.run(args,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log.write_text(q.stdout)
    if q.returncode:raise RuntimeError('Failed; inspect '+str(log))
    return q.stdout

def labels(root,name,seen=None):
    seen=set() if seen is None else seen;p=root/name
    if p in seen:return set()
    seen.add(p);s=p.read_text();out=set(re.findall(r'\\label\{([^}]+)\}',s))
    for n in re.findall(r'\\input\{([^}]+)\}',s):
        n=n if n.endswith('.tex') else n+'.tex'
        if (root/n).exists():out|=labels(root,n,seen)
    return out

def assemble():
    anchors={'ECTA.tex':'61ec5d91e5132a6dd48eb06f0ced26f02f811036c2efb144a613ce99c5319d71','supp.tex':'4cfd01093fbab9cb1051403974b2fb89b446e8959ced2415e116a05a7b5ad8c1'}
    for n,h in anchors.items():assert H(BASE/n)==h,n
    for n in ('audit','build','tables','sections'):(R/n).mkdir(exist_ok=True)
    for n in ('preamble.tex','econsocart.cls','econsocart.cfg','ecta-fullname.bst','references.bib'):shutil.copy2(BASE/n,R/n)
    for folder in ('sections','tables'):
        for p in (BASE/folder).glob('*.tex'):shutil.copy2(p,R/folder/p.name)
    # The historical companions remain ordinary local files in the same tree.
    if (BASE/'preserved').exists():shutil.copytree(BASE/'preserved',R/'preserved',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    bib=R/'references.bib';s=bib.read_text();assert 'felzenszwalb2012' not in s
    s+='\n@article{felzenszwalb2012,author={Felzenszwalb, Pedro F. and Huttenlocher, Daniel P.},title={Distance Transforms of Sampled Functions},journal={Theory of Computing},volume={8},number={19},pages={415--428},year={2012},doi={10.4086/toc.2012.v008a019}}\n';bib.write_text(s)
    main=(BASE/'ECTA.tex').read_text()
    a=main.index('\\begin{abstract}')+len('\\begin{abstract}');b=main.index('\\end{abstract}',a)
    abstract=(R/'abstract48.txt').read_text().strip();assert len(abstract.split())<=150
    main=main[:a]+'\n'+abstract+'\n'+main[b:]
    anchor='The numerical implementation starts from economic primitives.';assert main.count(anchor)==1
    main=main.replace(anchor,(R/'introduction48.txt').read_text().strip()+'\n\n'+anchor,1)
    main=main.replace('\\input{sections/acquisition47}','\\input{sections/acquisition47}\n\\input{sections/compiler48}',1)
    main=main.replace('\\input{sections/direct47}','\\input{sections/direct47}\n\\input{sections/economic48}\n\\input{sections/study48}',1)
    anchor='\\section{Economic applications and conclusion}';assert main.count(anchor)==1
    main=main.replace(anchor,anchor,1)
    phrase='Neural Bellman Operators thus organize construction, certification, economic reuse, and resource accounting around the policy actually returned.'
    main=main.replace(phrase,(R/'conclusion48.txt').read_text().strip()+'\n\n'+phrase,1)
    start=main.index('The present main article is the authoritative R47 exposition')
    stop=main.index('\\bibliographystyle',start)
    main=main[:start]+(R/'reading-map48.tex').read_text().strip()+'\n\n'+main[stop:]
    # Put new evidence in its historical context without removing old statements.
    main=main.replace('An adaptive sparse-grid or adaptive-partition comparator has not been executed for the original neural optimizers.',
        'An adaptive sparse-grid or adaptive-partition comparator has not been executed for the original neural optimizers. Section~\\ref{sec:study48} adds a separate error-driven coordinate-FVI comparator and three- and four-dimensional stress catalogue for the constructive backend; neither retroactively changes the optimizer study.')
    (R/'ECTA.tex').write_text(main)
    for name,label in [('constrained47.tex','sec:study48'),('direct47.tex','sec:economic48')]:
        p=R/'sections'/name;text=p.read_text();pos=text.index('\n')
        note='\nThe following evidence is the frozen R47 study. Its results and limitations are retained; Section~\\ref{'+label+'} gives the new execution and decision evidence.\n'
        p.write_text(text[:pos+1]+note+text[pos+1:])
    supp=(BASE/'supp.tex').read_text().replace('for the R47 revision, retaining the R44--R46 results:',
          'for the R48 revision, retaining the R44--R47 results:')
    supp=supp.replace('\\input{preamble}','\\input{preamble}\n\\usepackage{xr-hyper}\n\\externaldocument[M-]{build/ECTA}[ECTA.pdf]',1)
    supp=supp.replace('\\bibliographystyle{ecta-fullname}','\\input{sections/proofs48}\n\\input{tables/direct-full48}\n\\input{tables/frontier-full48}\n\\bibliographystyle{ecta-fullname}',1)
    # New proof references to article labels are prefixed, avoiding collisions.
    article_labels=labels(R,'ECTA.tex');proof=(R/'proofs48-source.tex').read_text()
    proof=re.sub(r'(\\(?:eqref|ref)\{)([^}]+)(\})',lambda m:m[1]+('M-' if m[2] in article_labels else '')+m[2]+m[3],proof)
    (R/'sections/proofs48.tex').write_text(proof);(R/'supp.tex').write_text(supp)
    before={n:labels(BASE,n) for n in ('ECTA.tex','supp.tex')};after={n:labels(R,n) for n in before}
    for n in before:assert before[n]<=after[n],(n,sorted(before[n]-after[n]))
    preservation={'review_commit':'3e142dda054f6fd3b9559c0cf2faa658933a2169','reviewed_source_commit':'27f3c36984f00ff060d0586712a01b87355914ba','reviewed_source_artifact':11503019522,'baseline_source_sha256':anchors,'documents':{n:{'baseline_labels':sorted(before[n]),'added_labels':sorted(after[n]-before[n]),'missing_labels':[]} for n in before},'historical_companions':{str(p.relative_to(BASE)):H(p) for p in sorted((BASE/'preserved').rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}}
    save(R/'audit/PRESERVATION.json',preservation)

def main():
    for n in ('audit','build','tables'):(R/n).mkdir(exist_ok=True)
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    p45=R.parent/'2026-10-07-r45';env['PYTHONPATH']=os.pathsep.join([str(p45/'preserved/R41/code'),str(p45/'preserved/R41/vendor/r38/code'),env.get('PYTHONPATH','')])
    for n in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):env[n]='1'
    run([sys.executable,str(R/'code/audit48.py')],R/'audit/aggregate48.log',env)
    run([sys.executable,str(R/'code/tables48.py')],R/'audit/tables48.log',env)
    assemble()
    run([sys.executable,str(R/'code/proof48.py')],R/'audit/proof48.log',env)
    tests={}
    for name,folder,pattern,count in [('R44','2026-10-07-r44','tests.py',14),('R45','2026-10-07-r45','tests.py',13),('R46','2026-10-07-r46','tests.py',14),('feasible46','2026-10-07-r46','test_feasible.py',8),('R47','2026-10-08-r47','tests.py',20),('R48','2026-10-08-r48','tests48.py',27)]:
        text=run([sys.executable,'-m','unittest','discover','-s',str(R.parent/folder/'code'),'-p',pattern,'-v'],R/'audit'/('tests-'+name+'.log'),env)
        match=re.search(r'Ran (\d+) tests?',text);assert match and int(match[1])==count
        tests[name]={'tests':count,'passed':True,'historical_results_modified':False}
    body=subprocess.check_output(['pandoc','-f','gfm','-t','latex',str(R/'response.md')],text=True)
    body=re.sub(r'\\texttt\{([^{}]*)\}',lambda m:r'\nolinkurl{'+m[1].replace(r'\_','_')+'}',body)
    front=r'''\documentclass[ecta,nameyear,draft]{econsocart}
\input{preamble}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\begin{document}\begin{frontmatter}
\title{Response to the Referee: Neural Bellman Operators}
\runtitle{Neural Bellman Operators: Response}
\begin{aug}\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}}\address[id=add1]{Peking University}\end{aug}
\end{frontmatter}
'''
    (R/'response.tex').write_text(front+body+'\n\\end{document}\n')
    for k in ('TEXINPUTS','BIBINPUTS','BSTINPUTS'):env[k]=str(R)+':'+env.get(k,'')
    for i in range(3):
        for name in ('ECTA','supp','response'):
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(R/'build'),str(R/(name+'.tex'))],R/'audit'/f'tex-{name}-{i}.log',env)
            if i==0 and r'\bibdata' in (R/'build'/(name+'.aux')).read_text():run([shutil.which('bibtex.original') or 'bibtex','build/'+name],R/'audit'/f'bib-{name}.log',env)
    comp=[]
    for name in ('ECTA','supp','response'):
        text=(R/'build'/(name+'.log')).read_text(errors='replace')
        bad=[l for l in text.splitlines() if ('undefined' in l.lower() and ('reference' in l.lower() or 'citation' in l.lower())) or any(k in l for k in ('multiply-defined labels','Missing character:','Overfull \\hbox','Overfull \\vbox'))]
        assert not bad,(name,bad)
        info=subprocess.check_output(['pdfinfo',str(R/'build'/(name+'.pdf'))],text=True)
        comp.append({'document':name,'pages':int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1]),'pdf_sha256':H(R/'build'/(name+'.pdf')),'undefined_references':0,'duplicate_labels':0,'missing_characters':0,'overfull_boxes':0})
    release={'revision':'R48','date':'2026-10-08','review_commit':'3e142dda054f6fd3b9559c0cf2faa658933a2169','reviewed_article_commit':'27f3c36984f00ff060d0586712a01b87355914ba','publication_source_commit':os.environ.get('PUBLICATION_INPUT_COMMIT',os.environ.get('GITHUB_SHA','local-build')),'publication_run':os.environ.get('GITHUB_RUN_ID'),'tests':tests,'total_tests':sum(t['tests'] for t in tests.values()),'compilation':comp,'results':json.loads((R/'audit/PUBLICATION_SUMMARY.json').read_text()),'scientific_execution_repeated':False,'historical_results_modified':False,'peer_or_editorial_approval':False,'proof_budget_spot_checks':json.loads((R/'audit/PROOF_BUDGET_CHECK.json').read_text())['cases']}
    save(R/'audit/RELEASE_AUDIT.json',release)
    manifest={str(p.relative_to(R)):H(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and 'transport' not in p.parts and p.suffix!='.pyc' and p.name not in ('FILES_SHA256.json','CLEAN_REBUILD.json','FINAL_DELIVERY.json','clean-rebuild.log')}
    save(R/'audit/FILES_SHA256.json',manifest)
    print(json.dumps({'compilation':comp,'tests':release['total_tests'],'verified_files':len(manifest)},indent=2))
if __name__=='__main__':main()
