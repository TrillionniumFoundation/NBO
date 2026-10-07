"""Materialize R45 from the complete R44 article; never edit historical files."""
import hashlib,json,re,shutil,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]
OLD=Path(os.environ.get('NBO_R44',str(R.parent/'2026-10-07-r44')))
OLD41=OLD/'evidence/2026-10-07-r41'
if not (OLD41/'econsocart.cls').is_file(): OLD41=R/'preserved/R41'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for n in ('preamble.tex','references.bib'):
        shutil.copy2(OLD/n,R/n)
    for p in (OLD/'tables').glob('*.tex'):shutil.copy2(p,R/'tables'/p.name)
    for n in ('econsocart.cls','econsocart.cfg','ecta-fullname.bst'):
        shutil.copy2(OLD41/n,R/n)
    refs=(R/'references.bib').read_text()
    refs+='\n@article{mcshane1934,author={McShane, Edward J.},title={Extension of Range of Functions},journal={Bulletin of the American Mathematical Society},year={1934},volume={40},number={12},pages={837--842},doi={10.1090/S0002-9904-1934-05978-0}}\n'
    (R/'references.bib').write_text(refs)
    main=(OLD/'ECTA.tex').read_text()
    main=main.replace('There are three parts to the argument.','There are four parts to the argument.')
    oldabs=main.split('\\begin{abstract}\n',1)[1].split('\\end{abstract}',1)[0]
    abstract='''This paper develops Neural Bellman Operators for policy evaluation and feasible improvement in controlled economies. Centered continuation errors connect economic transport and full-policy loss. A deterministic ReLU construction produces own-future continuations, feasible actions, and all-state certificates from primitive moduli and an economic tolerance. Its Lipschitz bound is independent of label error, and its finite termination does not presume nonlinear optimizer convergence. A predeclared matched catalogue reports the complete construction and verification frontiers of this backend and a spline comparator. Retained-policy recertification and a paired residual identity separately address verification resolution and direct expected policy-cost differences under continuous innovations. The original training catalogue, strong conventional comparisons, and adverse precision findings are preserved. Construction, certification, and comparative economic value are distinct claims. Controlled-diffusion, recursive-preference, and game formulations retain their application-specific conditions.\n'''
    main=main.replace(oldabs,abstract,1)
    anchor='The numerical implementation starts from economic primitives.'
    paragraph='''Fourth, a deterministic neural construction connects primitive moduli to a complete policy tolerance. A minimum of Lipschitz cones, realized exactly by ReLU gates, fits each date's own-future Bellman labels without inflating its Lipschitz bound when those labels are inexact. The state, action, and arithmetic budgets are specified before construction. This yields finite termination for a defined neural backend rather than a claim about arbitrary nonlinear training. A new full matched catalogue executes the same resolution ladder for this backend and a conventional spline, including every unsuccessful rung and three isolated timing repetitions.\n\n'''
    main=main.replace(anchor,paragraph+anchor,1)
    main=main.replace('The complete previous article, proof supplement, and economic applications remain unchanged and linked as companions;', 'The complete previous article, proof supplement, and economic applications are materialized unchanged within the current source tree as preserved companions;')
    marker='\\section{Economic applications and conclusion}'
    assert marker in main
    main=main.replace(marker,'\\input{sections/constructive}\n\n'+marker,1)
    main=main.replace('An adaptive sparse-grid or adaptive-partition comparator has not been executed in this revision. Neither has a nonlinear dimension/horizon grid or repeated isolated timing of every scalar and coupled service.', 'An adaptive sparse-grid or adaptive-partition comparator has not been executed for the original neural optimizers. Neither has a nonlinear dimension frontier or repeated isolated timing of every original scalar and coupled service. Section~\\ref{sec:catalogue45} adds a separate predeclared horizon/price catalogue with repeated isolated timing for the deterministic constructive backend and spline; it does not replace the original experiments.')
    main=main.replace('a fixed catalogue is not a general reliability theorem.', 'a fixed catalogue is not a general reliability theorem. Theorem~\\ref{thm:constructive45} and Corollary~\\ref{cor:termination45} now supply a separate deterministic reliability statement for an explicitly constructed neural backend. They do not retroactively prove convergence of the earlier optimizers.')
    start=main.index('The present main article is the authoritative R44 exposition.')
    end=main.index('\\bibliographystyle',start)
    main=main[:start]+'''The present main article is the authoritative R45 exposition. The active technical supplement contains complete proofs of its policy, retained-policy, paired expectation, and constructive-neural results. The response maps every B1--B10 and M1--M10 comment to a mathematical result, an execution, or an explicitly unsettled comparative requirement. All R44 main-article labels are retained.\n\nThe current source tree also materializes the complete previous R41 article, supplement, and economic-applications companion without changing their bytes. They preserve the full controlled-diffusion, recursive-preference, endogenous-preference, temporal-self, game, and historical numerical developments. Their presence is preservation of those results under their original hypotheses, not new empirical validation across all applications. The current argument and new constructive proofs can be read without selecting another revision branch. Original R42 capped-service outcomes, R44 postselected diagnostics, and the predeclared R45 constructive catalogue are separately identified. No earlier review or revision is overwritten.\n\n'''+main[end:]
    (R/'ECTA.tex').write_text(main)
    supp=(OLD/'supp.tex').read_text().replace('for the R44 revision:', 'for the R45 revision, retaining the R44 results:')
    supp=supp.replace('Complete earlier proofs and economic applications remain unchanged in the retained companions.', 'The constructive neural backend has its own complete primitive-budget proof below. Complete earlier proofs and economic applications are materialized unchanged in the current source tree.')
    supp=supp.replace('Requests for an adaptive-grid comparator, a nonlinear dimension/horizon study, and repeated isolated nonlinear timings remain comparative evidence obligations; the new retained-policy and paired-cost results are not substitutes for those experiments.', 'The new constructive catalogue supplies a separate horizon/price study and repeated isolated timings for its declared backend. An adaptive-grid comparator, a nonlinear dimension frontier, and repeated isolated comparisons for the original optimizers remain distinct evidence requirements; retained-policy and paired-cost results are not substitutes for them.')
    supp=supp.replace('\\bibliographystyle{ecta-fullname}','\\input{sections/constructive-proof}\n\\input{tables/frontier45}\n\\bibliographystyle{ecta-fullname}')
    (R/'supp.tex').write_text(supp)
    preserved=R/'preserved/R41'
    if not preserved.exists():shutil.copytree(OLD41,preserved,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copy2(OLD/'ECTA.tex',R/'preserved/R44-ECTA.tex')
    shutil.copy2(OLD/'supp.tex',R/'preserved/R44-supp.tex')
    oldlabels=set(re.findall(r'\\label\{([^}]+)\}',(OLD/'ECTA.tex').read_text()))
    newlabels=set(re.findall(r'\\label\{([^}]+)\}',main))
    assert oldlabels<=newlabels
    docs={}
    for p in OLD41.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            q=preserved/p.relative_to(OLD41);assert sha(p)==sha(q)
            docs[str(p.relative_to(OLD41))]=sha(q)
    audit={'baseline_review_commit':'5d4eca82b5477c4f0305f0f90bf9adc1635ec5de',
      'baseline_article_commit':'e00d3d46484029738884119f18ce1e15fbdcc929',
      'original_R44_labels_retained':sorted(oldlabels),'missing_original_labels':[],
      'preserved_R41_files':docs,'historical_deletions':[],'historical_overwrites':[],
      'scope':'Active R45 text extends the complete R44 exposition. All historical repository paths remain unchanged; byte-identical companions are materialized inside R45.'}
    (R/'audit/PRESERVATION.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
