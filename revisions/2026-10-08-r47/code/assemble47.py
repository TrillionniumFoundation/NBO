"""Extend the reviewed R46 text without replacing any predecessor file."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
R=Path(__file__).resolve().parents[1];BASE=R.parent/'2026-10-07-r46'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def labels(root,name,seen=None):
    seen=set() if seen is None else seen;p=root/name
    if not p.suffix:p=p.with_suffix('.tex')
    if p in seen:return set()
    seen.add(p);s=p.read_text();found=set(re.findall(r'\\label\{([^}]+)\}',s))
    for q in re.findall(r'\\input\{([^}]+)\}',s):found|=labels(root,q,seen)
    return found

def assemble():
    for d in ('audit','build','tables','sections','preserved'):(R/d).mkdir(exist_ok=True)
    for n in ('preamble.tex','econsocart.cls','econsocart.cfg','ecta-fullname.bst','references.bib'):shutil.copy2(BASE/n,R/n)
    for d in ('sections','tables'):
        for p in (BASE/d).glob('*.tex'):shutil.copy2(p,R/d/p.name)
    # These are source-bound historical companions, not substitutes for active proofs.
    shutil.copytree(BASE/'preserved',R/'preserved',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for n in ('ECTA.tex','supp.tex','response.md'):shutil.copy2(BASE/n,R/'preserved'/('R46-'+n))
    refs=(R/'references.bib').read_text()+'''\n@article{felzenszwalb2012,author={Felzenszwalb, Pedro F. and Huttenlocher, Daniel P.},title={Distance Transforms of Sampled Functions},journal={Theory of Computing},volume={8},number={19},pages={415--428},year={2012},doi={10.4086/toc.2012.v008a019}}\n@article{brumm2017,author={Brumm, Johannes and Scheidegger, Simon},title={Using Adaptive Sparse Grids to Solve High-Dimensional Dynamic Models},journal={Econometrica},volume={85},number={5},pages={1575--1612},year={2017},doi={10.3982/ECTA12216}}\n'''
    (R/'references.bib').write_text(refs)
    s=(BASE/'ECTA.tex').read_text()
    abstract='This paper develops Neural Bellman Operators for policy evaluation and feasible improvement in controlled economies. Centered continuation errors connect economic transport and full-policy loss. A deterministic own-future ReLU construction preserves the feasible actions attaining its labels. Exact tensor compilation evaluates that continuation and its original witness from cell-corner indices. An acquired-state policy theorem incorporates numerical selection, state uncertainty and robust repair under endogenous constraints. Primitive moduli yield explicit state, action, integration and precision budgets. Matched two- and three-state nonlinear executions compare the construction with conventional fitted-value iteration and isolate a shared compilation benefit from neural representation. Direct continuous-law comparisons of original and newly deployed policies identify prespecified expected-cost tolerances without identifying cost orderings. All earlier adverse evidence remains visible. Controlled-diffusion, recursive-preference and game formulations retain their application-specific conditions.'
    a=s.index('\\begin{abstract}')+len('\\begin{abstract}');b=s.index('\\end{abstract}',a);s=s[:a]+'\n'+abstract+'\n'+s[b:]
    anchor='The numerical implementation starts from economic primitives.'
    intro='These arguments now extend to the policy actually acquired and executed. An exact tensor compiler retains original action witnesses while reducing each off-grid query to the witnesses of its cell corners. A robust-acquisition theorem charges numerical selection and feasible capacity repair. We execute the resulting construction in two- and three-state nonlinear economies, alongside conventional fitted-value iteration, and directly compare both original and newly deployed policies under margins fixed before simulation. The identical non-neural envelope receives the same compiler, making the source of the observed acceleration explicit.\n\n'
    assert s.count(anchor)==1;s=s.replace(anchor,intro+anchor)
    anchor='\\section{Economic applications and conclusion}'
    assert s.count(anchor)==1;s=s.replace(anchor,'\\input{sections/operational47}\n\\input{sections/evidence47}\n\n'+anchor)
    s=s.replace('A new full matched catalogue executes','The first full matched constructive catalogue executes')
    s=s.replace('The new coupled direct intervals all contain zero','The earlier coupled direct intervals all contain zero')
    s=s.replace('The present main article is the authoritative R46 exposition, extending the complete R45 manuscript.','The present main article is the authoritative R47 executed-comparison exposition, extending the complete reviewed R46 manuscript.')
    s=s.replace('The response distinguishes the latest supplemental review of the incomplete R43 snapshot from the earlier substantive R44 report.','The prior response distinguished the incomplete R43 snapshot from the substantive R44 report. The current response addresses the complete R46 report at its pinned review commit.')
    s=s.replace('The new witness construction, execution allowance and matched frontier are stated and proved in this revision.','The witness construction and its original frontier are retained. The current revision adds exact tensor compilation, robust acquired-state implementation, constrained multidimensional frontiers and direct policy-value comparisons, with their proofs in the active supplement.')
    # Qualify a historical pending frontier rather than removing that historical statement.
    s=s.replace('No nonlinear dimension frontier is claimed.','No nonlinear dimension frontier is claimed for these original optimizer records. The separate constructive benchmark is reported in Section~\\ref{sec:evidence47}.')
    s=s.replace('B1--B10 and M1--M10','B1--B9 and M1--M10')
    (R/'ECTA.tex').write_text(s)
    s=(BASE/'supp.tex').read_text().replace('for the R46 revision, retaining the R44 and R45 results:','for the R47 executed-comparison revision, retaining the R44--R46 results:')
    s=s.replace('A fresh reproduction obtains the two pinned input artifacts, verifies their archive digests, and uses a clean result directory.','The historical diagnostic reproduction obtained two pinned input artifacts and verified their archive digests. The published repository now materializes those inputs; an offline rebuild uses the deposited files and a new scientific observation uses a clean result directory.')
    s=s.replace('\\bibliographystyle{ecta-fullname}','\\input{sections/proofs47}\n\\bibliographystyle{ecta-fullname}',1)
    (R/'supp.tex').write_text(s)
    body=subprocess.check_output(['pandoc','-f','gfm+tex_math_dollars','-t','latex',str(R/'response.md')],text=True)
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
    record={'review_commit':'0bf1ff6060bb9211762f191b6ead306ae4725beb','manuscript_commit':'c3930399e3b8267451096d0e70ea67f49510065e','historical_deletions':[],'documents':{}}
    for n in ('ECTA.tex','supp.tex'):
        before=labels(BASE,n);after=labels(R,n);assert before<=after,(n,sorted(before-after))
        record['documents'][n]={'baseline_sha256':digest(BASE/n),'baseline_labels':sorted(before),'new_labels':sorted(after-before),'missing_labels':[]}
    retained={}
    for p in (BASE/'preserved').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            dest=R/'preserved'/p.relative_to(BASE/'preserved');assert digest(p)==digest(dest)
            retained[str(dest.relative_to(R))]=digest(dest)
    record['preserved_files']=retained
    (R/'audit/PRESERVATION.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
    print('Preserved labels:',{n:len(d['baseline_labels']) for n,d in record['documents'].items()})

if __name__=='__main__':assemble()
