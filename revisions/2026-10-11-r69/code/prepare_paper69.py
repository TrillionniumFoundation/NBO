"""Ordinary manuscript preparation, separate from frozen scientific sources."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-10-r67'
ABSTRACT='''This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement under the original economic law. Action witnesses and recursive interval queries provide an explicit policy-loss account without assuming successful hidden-layer optimization. We implement a certificate-aware fixed-feature ReLU readout and compare it with a coefficient-matched Bernstein readout under common information and optimization budgets. Independent contexts test the associated work loss, and prospective reuse charges training, loading, verification and recovery. We also prove a Bellman-centered estimator whose expectation is the original policy-cost difference and whose range is controlled by local regret certificates. Its numerical and statistical errors are allocated separately. A continuous-law investment study and a two-control extension distinguish reliable return, achieved training accuracy, complete work and economic noninferiority. Historical adverse evidence remains part of the comparison.'''
INTRO=r'''\section{Introduction}\label{sec:introduction67}
A continuation value matters because it changes an economic decision. Its approximation error, the loss of the implemented policy, and the resources used to return that policy are different objects. A reliable numerical method must connect them without assuming that a fitted predictor is accurate or that a smaller loss certificate implies a better policy.

We develop Neural Bellman Operators along this chain. A constructive own-future continuation retains feasible action witnesses and admits policy-identical native and affine--ReLU realizations. Acquired-state feasibility and primitive regularity bounds connect its approximation budget to the original Bellman optimum. Recursive interval queries then evaluate only the needed states, without constructing a complete state lattice. A fitted selector proposes a query location; verified original-law endpoints and a safeguarded fallback supply the certificate. The fitted model cannot authorize an action by itself.

The first contribution of the present development is a training-to-verification contract. Strong convexity supplies a computable upper chord from already purchased endpoint bounds. The resulting pre-query screen licenses a rounded action before another Bellman query when it closes. A certificate-aware convex readout objective measures unresolved verification work rather than action-label error. We execute this objective with a constructive ReLU feature map, a coefficient-matched Bernstein control and a label-loss control, and report exact optimization gaps for the returned weights. Independent contexts test the work loss; recursively visited policy states are not treated as independent validation observations.

The second contribution connects numerical certification to economic comparison. The sum of optimal Bellman advantages along an actual policy trajectory has expectation equal to that policy's loss. Subtracting two such observations cancels the common initial optimal value. A verified local regret contract bounds the observation's range, which can be much smaller than the range of realized economic costs. We prove simultaneous cost-difference intervals that include the numerical evaluation error and give a prospective precision rule. The additional Bellman integrations are paid computations, not a policy-value oracle. The estimand remains the original expected policy-cost difference.

The third contribution is an explicit complete-work comparison. Cold services charge their construction, queries, path evaluation and output. Prospective reuse charges model loading, identity checks and recovery over a fixed sixty-four-block window. A two-control extension compares triangular refinements and trained two-output proposals under the same original-law certificate. Reliable return, achieved readout quality, economic noninferiority and a complete-work advantage are reported separately. Their coexistence is an empirical question, not a presumption of neural superiority.

These results build on classical dynamic programming and approximation rather than claiming priority for safe improvement or useful predictions. The constructive envelope uses Lipschitz extension \citep{mcshane1934} and separable distance transforms \citep{felzenszwalb2012}. Min-plus approximation and Bellman inequalities have established roles \citep{lakshminarayanan2014,wang2015}. Prediction-guided optimization and learned warm starts address related computational questions \citep{sakaue2023warm,sambharya2023}. Sequential value-based evaluation can reduce variance \citep{jiang2016}; our additional object is a paid original-optimum interval calculation with verified regret-scale support. The detailed theorem sections identify each inherited principle and the precise extra feasibility, coverage and arithmetic conditions used here.

The economic application retains the nonlinear investment primitives and continuous laws of the original NBO paper. The complete development companion reproduces the preceding article, including its adverse timings, unresolved economic contrasts and path-enclosure correction, and adds the full new derivations. Earlier controlled-diffusion, recursive-preference and game applications retain their own hypotheses in the unchanged historical companions. The new query and statistical conclusions are not silently extended to those distinct models.
'''
CONCLUSION=r'''\section{Conclusion}\label{sec:conclusion67}
Neural Bellman Operators connect continuation construction to feasible economic decisions under explicit resource and accuracy accounts. The construction does not need a successful nonconvex fitting theorem: arbitrary proposals remain subject to an original-law certificate and a finite recovery procedure. The fixed-feature readout adds a separately computable optimization certificate, and its achieved work loss can be assessed on an independent context law.

Bellman-centered inference supplies a further connection. The original policy-cost difference is the expectation of a regret-scale observation whose numerical evaluation is itself verified and charged. This permits a precision-based comparison rather than an attempted policy ranking from two approximation bounds. Noninferiority at a declared normalized margin is different from strict advantage, a measured computation saving, or an estimated monetary welfare gain. A purchase decision must combine the relevant interval with explicit computation prices and replacement costs.

The complete numerical catalogue retains unfavorable as well as favorable findings. Removing a state lattice does not remove horizon or innovation-tree costs, and the optional vector witness does not alter that fact. The resulting theorem--implementation--cost chain remains part of the original NBO paper. Its broader applications are preserved without being presented as numerical validations of the specific expected-cost theorem established here.
'''
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def expanded(root,path,seen=None):
    seen=set() if seen is None else seen;path=path.resolve()
    if path in seen:return ''
    seen.add(path);text=path.read_text()
    def sub(m):
        file=root/(m[1]+('' if m[1].endswith('.tex') else '.tex'))
        return expanded(root,file,seen) if file.exists() else m[0]
    return re.sub(r'\\input\{([^}]+)\}',sub,text)
def main():
    marker=R/'audit/PAPER_PREPARED69.json'
    if marker.exists():print('Ordinary paper already prepared; preserving subsequent edits.');return
    for folder in ('sections','tables','publication'):shutil.copytree(OLD/folder,R/folder,dirs_exist_ok=True)
    for p in OLD.iterdir():
        if p.is_file() and p.suffix in ('.tex','.bib','.cls','.cfg','.bst','.sty'):shutil.copy2(p,R/p.name)
    original=(OLD/'ECTA.tex').read_text();supp=(OLD/'supp.tex').read_text();relocated=[]
    for name in ('operational67','vector67'):
        p=R/'sections'/(name+'.tex');text=p.read_text();put(R/'sections'/(name+'-full.tex'),text)
        def move(m):
            label='supp:relocated69-'+str(len(relocated)+1)
            relocated.append(r'\subsection{Proof retained from '+name.replace('_',' ')+r'}\label{'+label+'}\n'+m[0])
            return r'\noindent The proof is reproduced in Supplement, Section~\ref{'+label+'}.'
        p.write_text(re.sub(r'\\begin\{proof\}.*?\\end\{proof\}',move,text,flags=re.S))
    put(R/'sections/relocated69.tex',r'\section{Retained proofs for operational and vector certificates}\label{supp:relocated69}'+'\n'+'\n\n'.join(relocated)+'\n')
    head,body=original.split(r'\input{sections/core49}',1)
    introstart=head.index(r'\section{Introduction}')
    main=head[:introstart]+INTRO+'\n'+r'\input{sections/core49}'+body
    main=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],main,count=1,flags=re.S)
    main=main.replace(r'\input{sections/operational67}',r'\input{sections/operational67}'+'\n'+r'\input{sections/training69-print}')
    main=main.replace(r'\input{sections/study67}',r'\input{sections/centered69}'+'\n'+r'\input{sections/study69}')
    # The previous conclusion is retained verbatim in the complete companion.
    m=re.search(r'\\section\{[^}]*[Cc]onclusion[^}]*\}',main)
    if m:
        end=main.index(r'\bibliographystyle',m.start());main=main[:m.start()]+CONCLUSION+'\n'+main[end:]
    main=main.replace('e67main','e69main');put(R/'ECTA.tex',main)
    complete=original.replace('e67main','e69complete')
    complete=complete.replace(r'\input{sections/operational67}',r'\input{sections/operational67-full}'+'\n'+r'\input{sections/training69}')
    complete=complete.replace(r'\input{sections/vector67}',r'\input{sections/vector67-full}')
    complete=complete.replace(r'\input{sections/study67}',r'\input{sections/study67}'+'\n'+r'\input{sections/centered69}'+'\n'+r'\input{sections/study69}')
    notice=r'\section*{Reading notice: complete R69 development} This edition retains the complete preceding R67 article, including its original introduction, conclusion, statements, proofs and numerical study, and inserts the new training and policy-cost results. The active article and technical supplement provide the journal reading path; prior broader NBO companions remain unchanged.'
    complete=complete.replace(r'\end{frontmatter}',r'\end{frontmatter}'+'\n'+notice,1);put(R/'complete.tex',complete)
    supp=supp.replace('e67supp','e69supp').replace(r'\input{sections/supp67}',r'\input{sections/supp67}'+'\n'+r'\input{sections/relocated69}'+'\n'+r'\input{sections/supp69}')
    put(R/'supp.tex',supp)
    entries_path=R/'publication/bibliography-entries.json';entries=json.loads(entries_path.read_text())
    entries['jiang2016']=r'\bibitem[\protect\citeauthoryear{Jiang and Li}{Jiang and Li}{2016}]{jiang2016}'+'\n'+r'\textsc{Jiang, Nan and Lihong Li} (2016): \enquote{Doubly Robust Off-policy Value Evaluation for Reinforcement Learning,} in \emph{Proceedings of the 33rd International Conference on Machine Learning}, vol.~48 of \emph{Proceedings of Machine Learning Research}, 652--661.'
    put(entries_path,json.dumps(entries,sort_keys=True,indent=2)+'\n')
    bib=R/'references.bib';text=bib.read_text()
    if 'jiang2016,' not in text:text+='\n@inproceedings{jiang2016, author={Nan Jiang and Lihong Li}, title={Doubly Robust Off-policy Value Evaluation for Reinforcement Learning}, booktitle={Proceedings of the 33rd International Conference on Machine Learning}, series={Proceedings of Machine Learning Research}, volume={48}, pages={652--661}, year={2016}}\n'
    bib.write_text(text)
    # JSON serialization sorts contrast keys; replay their recorded orientation.
    auditor=R/'code/audit69.py';text=auditor.read_text()
    text=text.replace("for a,b in itertools.combinations(summary['arms'],2):\n        name=a+'-minus-'+b;diff=", "for name in summary['centered']:\n        a,b=name.split('-minus-');diff=")
    auditor.write_text(text)
    previous={str(p.relative_to(OLD)):digest(p) for p in OLD.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.cls','.cfg','.bst','.sty','.py') and 'build' not in p.relative_to(OLD).parts}
    labels=sorted(set(re.findall(r'\\label\{([^}]+)\}',expanded(OLD,OLD/'ECTA.tex'))))
    record=dict(review_commit='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',reviewed_commit='eacd3e217ae1e2e9ea6e154b48da7d103159d051',
        prior_source_sha256=previous,prior_main_labels=labels,relocated_proofs=len(relocated),
        scope='All R67 source files remain unchanged; the complete R69 edition retains its whole main-text content. The active article relocates proofs and the full old study instead of deleting them.')
    put(marker,json.dumps(record,sort_keys=True,indent=2)+'\n')
    put(R/'CONTENT_MAP69.md','# R67 to R69 content map\n\n'+record['scope']+'\n\nThe original numerical study is `sections/study67.tex`, included unchanged in `complete.tex`. Operational and vector proofs are in `sections/relocated69.tex` for the active supplement and in the `-full.tex` sections for the complete edition. All original main labels are checked against the complete R69 source.\n\n'+ '\n'.join('- `'+x+'`' for x in labels)+'\n')
    print(json.dumps(dict(status='ordinary_paper_prepared',prior_files=len(previous),prior_labels=len(labels),relocated_proofs=len(relocated),abstract_words=len(ABSTRACT.split()))))
if __name__=='__main__':main()
