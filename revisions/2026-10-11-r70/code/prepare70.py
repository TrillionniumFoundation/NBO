"""One-time ordinary-source assembly; historical directories are read-only."""
from pathlib import Path
import hashlib,json,re,shutil
from amend70 import main as amend
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-10-r67';SCI=R.parent/'2026-10-11-r69'
THEORY=('core49','accuracy62-print','query63','gated64','localization65','operational67','vector67','decisions49')
ABSTRACT='''This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement. A witness-preserving continuation and a recursive Bellman implementation connect approximation to the original economic optimum. Verified action comparisons supply a trainable loss for additional queries. We derive a work bound for predictable deployment under context-law drift and a Bellman-centered estimator of actual policy-cost differences. The estimator uses paid conditional-value enclosures and a regret-scale concentration range. In a nonlinear investment economy, a frozen 188-process study executes certificate-aware ReLU and matched Bernstein readouts, independent validation, prospective reuse and two-control comparisons. All twelve policy-cost contrasts meet a prespecified equivalence margin; none identifies strict superiority. Complete work and conditional adoption regions distinguish policy quality from computational savings. The original operator, economic primitives and historical adverse evidence are retained.'''
INTRO=r'''\section{Introduction}\label{sec:introduction65}
A numerical continuation matters because it helps produce an economic decision. The error of a fitted value, the loss of the implemented policy and the resources required to verify that loss are different objects. A policy may improve without a tighter numerical certificate; a tighter certificate may leave the policy unchanged. A useful computational method must connect its approximation and resource choices to a feasible decision under the original economic law.

This paper develops Neural Bellman Operators (NBOs) along that chain. The first implementation evaluates each continuation against its own fitted future and retains feasible action witnesses. Its exact affine--ReLU realization and primitive error budget are constructive: they do not assume that an unrestricted nonconvex optimizer succeeds. A second implementation queries the original Bellman problem recursively at the states required by the current action search. A trained readout proposes where to seek information. Verified lower and upper bounds, not fitted values, determine when the complete policy meets its original-optimum contract.

In the nonlinear investment economy, state-dependent capacity and bilinear transitions make those requirements substantive. Primitive curvature controls the convexity defect of the transition and supplies regularity bounds for the true Bellman value. Continuous-action certificates therefore need no stored state lattice. A strong-convexity upper chord can sometimes license an actual rounded action before another Bellman evaluation. When it cannot, protected conventional refinement and a costed rational recovery remain available. Neither the learned continuation nor the predictor is assumed convex.

The operational training problem is to reduce unresolved verification work. The certificate-based margin loss bounds additional root queries. With fixed nonnegative ReLU features, its achieved convex readout objective and optimization gap can be certified. We extend the work account to predictable selection among validated readouts and dependent deployment contexts. The bound separates validation, context-law drift, descendant work and deployment overhead. It does not replace dependence by an independence assumption or treat a model-identity check as evidence that the context law is unchanged.

The economic comparison also requires informative policy-cost inference. We derive a Bellman-centered estimator using optimal advantages evaluated along each actual policy trajectory. Telescoping identifies its expectation with the original expected cost difference, while local accuracy bounds control its range at the scale of policy regret. The conditional Bellman values are enclosed with a separately purchased, tighter numerical calculation. This improves statistical precision without assuming a policy-value oracle, changing the original law, or substituting two loss certificates for the policy-cost estimand. The numerical and sampling width allocations are specified before the new observations.

The frozen experiment connects those results to executed policies. Hat--ReLU and Bernstein readouts purchase identical information, have the same number of coefficients and optimize the same certificate loss. Label-loss and prediction-free rules separate the training objective from the representation and the verifier. Independent-context validation executes its declared recovery. Sixty-four-block reuse includes a deliberately declined stale model. The direct-cost comparison includes an unchanged historical neural controller. A trained two-output comparison extends the workload study to two controls and two continuous innovations.

The evidence identifies equivalence at the prespecified policy-loss margin for all twelve new scalar contrasts. It does not identify strict economic superiority or a uniform neural complete-work advantage. These are different conclusions. Complete process receipts, the exact controller contract and the purchaser's declared prices determine the adoption region. All unfavorable repetitions, conventional winners, earlier unresolved comparisons and the independently detected historical interval-accounting error remain available. The current construction is a positive policy-evaluation and improvement result, not a claim that naming an equivalent representation neural supplies an empirical advantage.

\paragraph{Relation to existing methods.}
Lipschitz extension and distance transforms underlie the constructive envelope \citep{mcshane1934,felzenszwalb2012}. Approximate and safe policy iteration have established approximation and performance analyses \citep{munos2003,pirotta2013,scherrer2015}, and \citet{yang2020convex} studies convex dynamic-programming approximation. Prediction-dependent warm starts and learned optimization-based control are also established ideas \citep{sakaue2023warm,sambharya2023,agrawal2020control}. The additional object here is the complete connection from economic primitives to an acquired-policy certificate, a verified pre-query decision, a certified training objective and a paid deployment account.

Value-based policy evaluation also uses telescoping and control-variate constructions; \citet{jiang2016} develops doubly robust off-policy evaluation. Our centered experiment is on-policy under the declared original law and uses neither importance ratios nor an assumed-correct fitted value. It instead requires verified original-optimum advantage enclosures and charges their conditional integration. The proof states exactly when the expected-cost identity and the smaller concentration range hold.

\paragraph{Reading path.}
Sections~\ref{sec:core49}--\ref{sec:accuracy62} retain the original operator and investment regularity. Sections~\ref{sec:query63}--\ref{sec:localization65} establish recursive verification and safeguarded selection; Sections~\ref{sec:operational67} and \ref{sec:vector67} give readout training and multivariate action certificates. The policy-inference contract in Section~\ref{sec:decisions49} leads to centered inference in Section~\ref{sec:centered69} and complete deployment in Section~\ref{sec:deployment70}. Section~\ref{sec:study70} gives the executed evidence. Proofs and full numerical records are in the supplement. The unchanged preceding article, supplement and complete development remain companion documents with their original hypotheses.
'''
CONCLUSION=r'''\section{Conclusion}\label{sec:conclusion65}
Neural Bellman Operators connect a continuation's construction to feasible decisions under the original economic law. The witness-producing implementation retains an explicit own-future error account. The recursive implementation replaces the stored state lattice by certified action queries. A trained proposal can reduce verification work, but cannot alter the lower certificate's authority over the policy guarantee.

The present results complete two additional connections. Independent work-loss validation extends to predictable deployment when context drift and descendant costs are controlled. Bellman-centered inference estimates actual policy-cost differences at a regret-scale precision, with every conditional-value calculation charged. A complete-service adoption region combines policy quality, implementation identity, measured work and declared prices without treating them as interchangeable objects.

The executed certificate-aware readouts meet the same original-optimum contract as their conventional comparators. The new cost intervals establish equivalence at the declared margin, while retaining uncertainty about strict superiority. Cold-start and reuse records do not support a universal neural work advantage, and the vector tree retains its horizon cost. These observations accompany, rather than replace, the positive constructive and inferential results. The original broader NBO applications remain under their own assumptions, with all historical evidence preserved for continued evaluation.
'''
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def save(p,j):write(p,json.dumps(j,sort_keys=True,indent=2)+'\n')
def main():
    amend();marker=R/'audit/PREPARATION70.json'
    if marker.exists():print('Ordinary R70 sources already assembled; author edits are retained.');return
    for folder in ('sections','tables','publication'):
        for p in (OLD/folder).rglob('*'):
            if p.is_file():
                target=R/folder/p.relative_to(OLD/folder)
                if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    for name in ('preamble.tex','econsocart.cls','econsocart.cfg','ecta-fullname.bst','references.bib'):
        shutil.copy2(OLD/name,R/name)
    for name in ('ECTA.tex','supp.tex','response.md'):
        dest=R/'preserved/R67'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/name,dest)
    shutil.copy2(SCI/'sections/centered69.tex',R/'sections/centered69.tex')
    front=(OLD/'ECTA.tex').read_text().split(r'\section{Introduction}')[0]
    front=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],front,flags=re.S)
    if len(ABSTRACT.split())>150:raise AssertionError('Abstract length')
    inputs='\n'.join(r'\input{sections/'+name+'}' for name in (*THEORY,'centered69','deployment70','study70'))
    write(R/'ECTA.tex',front+INTRO+'\n'+inputs+'\n'+CONCLUSION+'\n'+r'\bibliographystyle{ecta-fullname}'+'\n'+r'\bibliography{references}'+'\n'+r'\end{document}'+'\n')
    supp=(OLD/'supp.tex').read_text()
    supp=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\nThis supplement contains the retained NBO proofs, the new centered-inference and deployment proofs, achieved readout certificates, independent validation, full-bin reconstruction and complete-work records. The unchanged preceding empirical article and supplement remain separate companions.\n'+m[2],supp,flags=re.S)
    supp=supp.replace(r'\input{sections/supp67}',r'\input{sections/proofs70}'+'\n'+r'\input{sections/supp70}')
    write(R/'supp.tex',supp)
    # Preserve each proof verbatim while making the active article a theorem--
    # experiment paper, rather than accumulating every numerical appendix.
    relocated=[];proof_text=r'\section{Proofs of the operational and new results}\label{supp:proofs70}'+'\n'
    for name in ('operational67','vector67','centered69','deployment70'):
        path=R/'sections'/(name+'.tex');text=path.read_text();parts=[];last=0
        for index,match in enumerate(re.finditer(r'\\begin\{proof\}.*?\\end\{proof\}',text,re.S),1):
            prefix=text[:match.start()];statements=list(re.finditer(r'\\begin\{(?P<kind>theorem|proposition|lemma|corollary)\}.*?\\end\{(?P=kind)\}',prefix,re.S))
            if not statements:raise AssertionError('Proof without preceding statement: '+name)
            labels=re.findall(r'\\label\{([^}]+)\}',statements[-1][0]);label=labels[0]
            proof_label='supp:proof70-'+name+'-'+str(index)
            proof_text+=r'\subsection{Proof of the result \ref{'+label+'}}'+r'\label{'+proof_label+'}'+'\n'+match[0]+'\n\n'
            parts.append(text[last:match.start()]+r'\noindent\emph{Proof.} See Supplement, Section~\ref{'+proof_label+'}.'+'\n')
            last=match.end();relocated.append(dict(source=name,label=label,proof_label=proof_label,sha256=hashlib.sha256(match[0].encode()).hexdigest()))
        parts.append(text[last:]);write(path,''.join(parts))
    write(R/'sections/proofs70.tex',proof_text)
    path=R/'sections/operational67.tex';text=path.read_text()
    text=text.replace('The service comparison below retains the preregistered L-BFGS and conventional fits, rather than relabeling those models as minimizers of \\eqref{eq:readout-loss67}.','The preceding R67 service comparison retained its preregistered action-label fits. The new comparison in Section~\\ref{sec:study70} separately executes this certificate-aware objective, with equal-information Bernstein and label-loss controls; no historical fit is relabeled as its minimizer.')
    write(path,text)
    path=R/'sections/study70.tex';text=path.read_text()
    text=text.replace('Their complete-service adoption region is therefore given by Proposition~\\ref{prop:adoption70}, with normal-policy multiplier 504 and observed work differences.','Parameter matching is necessary for pairing these records. Under the additional same-numerical-policy premise, Proposition~\\ref{prop:adoption70} gives their complete-service adoption region, with normal-policy multiplier 504 and observed work differences. Cross-platform prediction portability is separately discussed in the supplement.')
    write(path,text)
    entries= json.loads((R/'publication/bibliography-entries.json').read_text())
    entries['jiang2016']=r'\bibitem[\protect\citeauthoryear{Jiang and Li}{Jiang and Li}{2016}]{jiang2016}'+'\n'+r'\textsc{Jiang, Nan and Lihong Li} (2016): \enquote{Doubly Robust Off-policy Value Evaluation for Reinforcement Learning,} in \emph{Proceedings of the 33rd International Conference on Machine Learning}, vol.~48 of \emph{Proceedings of Machine Learning Research}, 652--661.'
    save(R/'publication/bibliography-entries.json',entries)
    bib=(R/'references.bib').read_text()
    if '{jiang2016,' not in bib:bib+='\n@inproceedings{jiang2016,\n author={Nan Jiang and Lihong Li},\n title={Doubly Robust Off-policy Value Evaluation for Reinforcement Learning},\n booktitle={Proceedings of the 33rd International Conference on Machine Learning},\n series={Proceedings of Machine Learning Research},\n volume={48},\n pages={652--661},\n year={2016}\n}\n'
    write(R/'references.bib',bib)
    # Correct a Python source literal, not a scientific value or table endpoint.
    path=R/'code/tables70.py';text=path.read_text();text=text.replace("'$F(w)/\\tau^2$'","r'$F(w)/\\tau^2$'");write(path,text)
    prior={};locations={}
    for p in OLD.rglob('*'):
        if p.is_file() and p.suffix in ('.tex','.bib','.cls','.cfg','.bst','.sty','.py') and not any(x in p.relative_to(OLD).parts for x in ('build','audit','__pycache__')):
            prior[str(p.relative_to(OLD))]=sha(p)
            if p.suffix=='.tex':
                for label in re.findall(r'\\label\{([^}]+)\}',p.read_text()):locations.setdefault(label,[]).append('../2026-10-10-r67/'+str(p.relative_to(OLD)))
    statements=[]
    for name in THEORY:
        old=(OLD/'sections'/(name+'.tex')).read_text();new=(R/'sections'/(name+'.tex')).read_text()
        for m in re.finditer(r'\\begin\{(?P<kind>theorem|proposition|lemma|corollary)\}.*?\\end\{(?P=kind)\}',old,re.S):
            if m[0] not in new:raise AssertionError('Changed inherited statement '+name)
            statements.append(dict(section=name,sha256=hashlib.sha256(m[0].encode()).hexdigest()))
    record=dict(status='prepared',review_commit='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',reviewed_manuscript_commit='eacd3e217ae1e2e9ea6e154b48da7d103159d051',executed_evidence_commit='2c07e464e81930f14b3122054704731ec5a139ff',prior_sources_sha256=prior,prior_label_locations=locations,inherited_statements=statements,relocated_proofs=relocated,abstract_words=len(ABSTRACT.split()),historical_directories_modified=False)
    save(marker,record)
    lines=['# R70 content map','','The original NBO topic, title and theoretical statements are retained. All prior sources remain unchanged. The active empirical discussion integrates the separately frozen R69 catalogue; R67 empirical sections and every adverse record remain in the unchanged companion article and supplement.','','| Prior label | Retained source location |','|---|---|']
    for label,paths in sorted(locations.items()):lines.append('| `'+label+'` | '+'; '.join('`'+p+'`' for p in paths)+' |')
    write(R/'CONTENT_MAP70.md','\n'.join(lines)+'\n')
    write(R/'README.md','''# Neural Bellman Operators — R70

The active submission is ECTA.tex, supp.tex and response.md, with compiled
PDFs under build/. The original topic and economic law are unchanged.
The complete prior R67 submission and its older development companions are
retained separately; CONTENT_MAP70.md locates the original source labels.

New theory: sections/centered69.tex and sections/deployment70.tex.
Executed evidence: the immutable sibling 2026-10-11-r69 directory.
Independent replay: code/audit70.py, audit/RESULT_AUDIT70.json and DETAILS70.json.
Final publication requires audit/FINAL_DELIVERY70.json with passed status.

From a clean checkout with numpy, scipy, scikit-learn, pandoc, poppler-utils
and the econsocart LaTeX dependencies installed, run:

    python3 revisions/2026-10-11-r70/code/build70.py

The builder does not fit new scientific policies or add inference rows.
It replays frozen records, runs regression tests and compiles ordinary sources.
The same-numerical-callable-policy premise is required when applying inference
to measured deployment work; parameter-array identity alone is not sufficient
for cross-platform policy identity. All numerical differences and their
verification scope are retained rather than suppressed.
''')
    print(json.dumps(dict(status='prepared',inherited_statements=len(statements),proofs_relocated=len(relocated),abstract_words=record['abstract_words'],prior_sources=len(prior))))
if __name__=='__main__':main()
