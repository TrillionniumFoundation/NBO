"""Build the integrated R47 article from pinned ordinary repository inputs.

No network, training, simulation, historical writes or expiring artifacts.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
BASE=R.parent/'2026-10-07-r46';P45=R.parent/'2026-10-07-r45';P44=R.parent/'2026-10-07-r44'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def run(args,log,env=None,cwd=R):
    p=subprocess.run(args,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    log.write_text(p.stdout)
    if p.returncode:raise RuntimeError('Failed; inspect '+str(log))
    return p.stdout

def labels(root,name,seen=None):
    seen=set() if seen is None else seen;p=root/name
    if p in seen:return set()
    seen.add(p);text=p.read_text();out=set(re.findall(r'\\label\{([^}]+)\}',text))
    for q in re.findall(r'\\input\{([^}]+)\}',text):
        child=q if q.endswith('.tex') else q+'.tex'
        if (root/child).exists():out|=labels(root,child,seen)
    return out

def assemble():
    raw=(BASE/'ECTA.tex').read_bytes()
    assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()=='a845355034c8bd117d397248479b218e4987cc72'
    for d in ('audit','build','tables','sections','preserved'):(R/d).mkdir(exist_ok=True)
    for n in ('preamble.tex','econsocart.cls','econsocart.cfg','ecta-fullname.bst','references.bib'):
        shutil.copy2(BASE/n,R/n)
    for d in ('sections','tables'):
        for p in (BASE/d).glob('*.tex'):shutil.copy2(p,R/d/p.name)
    shutil.copytree(BASE/'preserved',R/'preserved',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for n in ('ECTA.tex','supp.tex','response.md'):shutil.copy2(BASE/n,R/'preserved'/('R46-'+n))
    text=raw.decode();abstract=(R/'abstract47.txt').read_text().strip()
    a=text.index('\\begin{abstract}')+len('\\begin{abstract}');b=text.index('\\end{abstract}',a)
    text=text[:a]+'\n'+abstract+'\n'+text[b:]
    anchor='The numerical implementation starts from economic primitives.'
    assert text.count(anchor)==1
    text=text.replace(anchor,(R/'introduction47.txt').read_text().strip()+'\n\n'+anchor,1)
    anchor='\\section{Economic applications and conclusion}'
    assert text.count(anchor)==1
    text=text.replace(anchor,'\\input{sections/acquisition47}\n\\input{sections/constrained47}\n\\input{sections/direct47}\n\n'+anchor,1)
    text=text.replace('The present main article is the authoritative R46 exposition, extending the complete R45 manuscript.',
                      'The present main article is the authoritative R47 exposition, extending the complete R46 manuscript and retaining its earlier results.')
    text=text.replace('The response maps every B1--B10 and M1--M10 comment to a mathematical result, an execution, or an explicitly unsettled comparative requirement.',
                      'The response maps every B1--B9 and M1--M10 comment of the latest R46 report to a mathematical result, an execution, or a comparative requirement not established by the new evidence.')
    text=text.replace('The response distinguishes the latest supplemental review of the incomplete R43 snapshot from the earlier substantive R44 report. The new witness construction, execution allowance and matched frontier are stated and proved in this revision.',
                      'Those earlier review responses remain preserved. The current response addresses the R46 report; acquired-state feasibility, explicit constrained construction, direct policy-cost proximity and complete tolerance curves are stated and proved in this revision.')
    text=text.replace('Neural Bellman Operators thus organize construction, certification, economic reuse, and resource accounting around the policy actually returned.',
                      'The acquired-state result makes that returned policy implementable under a stated information and arithmetic contract. The constrained economy supplies finite covering, integration and repair routines; the direct scalar experiment supplies simultaneous tolerance-based cost comparisons and a catalogue-adoption rule. Their distinct assumptions and work accounts remain visible.\n\nNeural Bellman Operators thus organize construction, certification, economic reuse, and resource accounting around the policy actually returned.')
    (R/'ECTA.tex').write_text(text)
    w=R/'sections/witness.tex';oldw=w.read_text()
    oldw=oldw.replace('The new design was fixed in the repository before execution.',
                      'The following matched catalogue is the frozen R46 experiment. Its statements about direct policy cost refer to the evidence then available; Section~\\ref{sec:direct47} supplies the new actual-policy comparison, and Section~\\ref{sec:constrained47} executes the state-dependent construction. The design was fixed in the repository before execution.',1)
    w.write_text(oldw)
    text=(BASE/'supp.tex').read_text()
    text=text.replace('for the R46 revision, retaining the R44 and R45 results:',
                      'for the R47 revision, retaining the R44--R46 results:')
    text=text.replace('\\bibliographystyle{ecta-fullname}','\\input{sections/proofs47}\n\\bibliographystyle{ecta-fullname}',1)
    (R/'supp.tex').write_text(text)
    preservation={'manuscript_baseline':'c3930399e3b8267451096d0e70ea67f49510065e','review_baseline':'0bf1ff6060bb9211762f191b6ead306ae4725beb','documents':{},'retained_files':{}}
    for n in ('ECTA.tex','supp.tex'):
        before,after=labels(BASE,n),labels(R,n);assert before<=after,sorted(before-after)
        preservation['documents'][n]={'baseline_sha256':H(BASE/n),'baseline_labels':sorted(before),'new_labels':sorted(after-before),'missing_labels':[]}
    for p in (BASE/'preserved').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            q=R/'preserved'/p.relative_to(BASE/'preserved');assert H(p)==H(q)
            preservation['retained_files'][str(q.relative_to(R))]=H(q)
    save(R/'audit/PRESERVATION.json',preservation)

def main():
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    env['PYTHONPATH']=os.pathsep.join([str(P45/'preserved/R41/code'),str(P45/'preserved/R41/vendor/r38/code'),env.get('PYTHONPATH','')])
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):env[key]='1'
    assemble();run([sys.executable,str(R/'code/audit47.py')],R/'audit/aggregate.log',env)
    tests={}
    for name,path,pattern,count in [('R44',P44,'tests.py',14),('R45',P45,'tests.py',13),('R46',BASE,'tests.py',14),('feasible46',BASE,'test_feasible.py',8),('R47',R,'tests.py',20)]:
        text=run([sys.executable,'-m','unittest','discover','-s',str(path/'code'),'-p',pattern,'-v'],R/'audit'/f'tests-{name}.log',env)
        match=re.search(r'Ran (\d+) tests?',text);assert match and int(match[1])==count
        tests[name]={'tests':count,'passed':True,'mode':'discovery; no historical audit or result writes'}
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
    for it in range(3):
        for name in ('ECTA','supp','response'):
            run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(R/'build'),str(R/(name+'.tex'))],R/'audit'/f'tex-{name}-{it}.log',env)
            if it==0 and r'\bibdata' in (R/'build'/(name+'.aux')).read_text():
                run([shutil.which('bibtex.original') or 'bibtex','build/'+name],R/'audit'/f'bib-{name}.log',env)
    compilation=[]
    for name in ('ECTA','supp','response'):
        text=(R/'build'/(name+'.log')).read_text(errors='replace')
        bad=[l for l in text.splitlines() if ('undefined' in l.lower() and ('reference' in l.lower() or 'citation' in l.lower())) or any(k in l for k in ('multiply-defined labels','Missing character:','Overfull \\hbox','Overfull \\vbox'))]
        assert not bad,(name,bad)
        info=subprocess.check_output(['pdfinfo',str(R/'build'/(name+'.pdf'))],text=True)
        compilation.append({'document':name,'pages':int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1]),'pdf_sha256':H(R/'build'/(name+'.pdf')),
                            'undefined_references':0,'duplicate_labels':0,'missing_characters':0,'overfull_boxes':0})
    release={'revision':'R47','date':'2026-10-08','review_commit':'0bf1ff6060bb9211762f191b6ead306ae4725beb',
             'manuscript_baseline':'c3930399e3b8267451096d0e70ea67f49510065e','publication_source_commit':os.environ.get('GITHUB_SHA','local-build'),
             'publication_run':os.environ.get('GITHUB_RUN_ID'),'tests':tests,'total_tests':sum(j['tests'] for j in tests.values()),
             'compilation':compilation,'results':json.loads((R/'audit/PUBLICATION_SUMMARY.json').read_text()),
             'scientific_execution_repeated':False,'historical_results_modified':False,'peer_or_editorial_approval':False}
    save(R/'audit/RELEASE_AUDIT.json',release)
    manifest={str(p.relative_to(R)):H(p) for p in sorted(R.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and 'transport' not in p.parts and p.name not in ('FILES_SHA256.json','CLEAN_REBUILD.json','FINAL_DELIVERY.json')}
    save(R/'audit/FILES_SHA256.json',manifest)
    print(json.dumps({'compilation':compilation,'tests':release['total_tests'],'verified_files':len(manifest)},indent=2))
if __name__=='__main__':main()
