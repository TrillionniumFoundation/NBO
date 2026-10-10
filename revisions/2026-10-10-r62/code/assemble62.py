"""One-time R62 author-source integration; never changes frozen science."""
from pathlib import Path
import difflib,hashlib,json,re
R=Path(__file__).resolve().parents[1]
DOCS=('ECTA','supp','development','development-supp','complete','complete-supp','response')
ABSTRACT=r'''We develop Neural Bellman Operators that construct continuations from their own fitted futures and return feasible economic policies. Exact trained-neural action recovery is connected to a complete policy certificate against the original continuous-action optimum. In the nonlinear investment family, primitive curvature controls the bilinear transition defect and yields convex Bellman values with explicit regularity bounds. Positive interpolation and continuous-law quadrature then give a second-order error account for the actual acquired policy, including action rounding and every remaining date. A prospective comparison covers several state dimensions, longer horizons and complete two-control policies. Neural and conventional proposals receive the same original-optimum targets, direct policy-cost inference and full computational charges. Pure fitted policies and their common-augmented counterparts are reported separately. The original constructive core, broader applications, failed targets and adverse comparisons are retained under their stated hypotheses.'''
BRIDGE=r'''\paragraph{Original-optimum accuracy of the implemented policy.}
A feasible witness is a local output; a decision maker ultimately purchases a complete controller. Section~\ref{sec:accuracy62} supplies a new bridge in the original investment economy. Although its state transition is bilinear, primitive state curvature dominates the possible loss of convexity in the continuation composition. The resulting Bellman functions have explicit Lipschitz and semiconcavity bounds at the original discount. Positive state interpolation and continuous-law quadrature can therefore be budgeted at second order. A separate action-transfer argument certifies the actual barycentric acquired actor rather than only a fitted objective or a nodewise value table.

The prospective comparison in Section~\ref{sec:study62} applies this contract to pure neural proposals, conventional fitted proposals, and their common-augmented policies across dimensions, horizons and a full two-control economy. Original-optimum accuracy, comparative expected cost and complete release work remain separate endpoints. This completes another part of the original NBO construction without identifying exact action search with a universally superior dynamic-programming method.

\paragraph{Convex dynamic programming and the additional primitive argument.}
Convex dynamic programs and uniform policy approximation are established subjects. \citet{yang2020convex} constructs convex optimization-based Bellman approximations and policy suboptimality bounds for continuous spaces. Our added argument verifies the required regularity for the stated bilinear, capacity-constrained investment primitives, derives coordinate interpolation and continuous-action errors, and carries these allowances through the recorded acquired actor. It does not claim priority for convex dynamic programming or assume that a signed-weight fitted ReLU is convex. The mathematical object whose curvature is proved is the original Bellman value.
'''
CONCLUSION=r'''The original-optimum calculation now extends across the declared state dimensions and horizons and to a complete two-control economy. Its primitive regularity theorem closes a backward convexity and semiconcavity argument at the original discount. The policy certificate separately accounts for positive interpolation, continuous-action covering, original-law quadrature, acquisition, arithmetic and action rounding. These terms connect the actual returned controller to the Bellman optimum, while the prospective cost intervals determine the economic comparisons supported by the data.

The pure fitted and common-augmented variants answer different implementation questions. The latter may complete an accuracy contract that the former does not, and its full reference work must be charged. A changed witness or a lower certified endpoint is not by itself an identified cost advantage. The complete fixed catalogue retains these distinctions, including unsuccessful targets and unresolved rankings. No empirical calibration, controlled multi-architecture timing result or dimension-free computational guarantee is inferred from the executed study.
'''

def put(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    marker=R/'audit/ASSEMBLY62.json'
    if marker.exists():print('R62 ordinary sources already integrated; preserving subsequent author edits.');return
    import science62
    freeze=science62.verify();execution=json.loads((R/'audit/EXECUTION62.json').read_text())
    if execution['status']!='executed':raise AssertionError('Complete production required before manuscript integration')
    before={d:(R/(d+'.tex')).read_text() for d in DOCS if (R/(d+'.tex')).exists()}
    for name in ('ECTA','complete'):
        path=R/(name+'.tex');text=path.read_text()
        if r'\input{sections/stability61}' not in text:raise AssertionError('Missing original exact-to-stability chain: '+name)
        text=text.replace(r'\input{sections/stability61}',r'\input{sections/stability61}'+'\n'+r'\input{sections/accuracy62-print}',1)
        if r'\input{sections/study61}' not in text:raise AssertionError('Missing original study: '+name)
        text=text.replace(r'\input{sections/study61}',r'\input{sections/study61}'+'\n'+r'\input{sections/study62}',1)
        if name=='ECTA':
            text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
            text=text.replace(r'\input{sections/intro61}',r'\input{sections/intro61}'+'\n'+BRIDGE,1)
            text=text.replace(r'\appendix',CONCLUSION+'\n'+r'\appendix',1)
        else:
            text=text.replace(r'\section*{Current reading notice}',r'\section*{Current reading notice}'+'\n'+r'The R62 article, supplement and response are the active revision. This complete companion adds original-model regularity, actual-policy original-optimum certification and the prospective multidimensional and two-control study. All subsequent edition notices are retained as historical notices.'+'\n',1)
            # Bibliographic positioning belongs to the current complete chain,
            # not to a modification of historical protected input sections.
            text=text.replace(r'\input{sections/accuracy62-print}',BRIDGE+'\n'+r'\input{sections/accuracy62-print}',1)
        put(path,text)
    for name in ('supp','complete-supp'):
        path=R/(name+'.tex');text=path.read_text();needle=r'\bibliographystyle{ecta-fullname}'
        if needle not in text:raise AssertionError('Missing ordinary bibliography: '+name)
        text=text.replace(needle,r'\input{sections/supp62}'+'\n'+needle,1);put(path,text)
    # A separate print copy permits harmless display reflow while preserving
    # the exact scientific theorem bytes included in the prospective freeze.
    frozen=(R/'sections/accuracy62.tex').read_text()
    note=r'''\paragraph{Relation to the preceding two-control query.}
The earlier query experiment used the fixed shared capacity $1/8$. The complete dynamic extension below uses the original state-dependent capacity $c(x)$, with the retained exposure columns, action-cost interaction and second shock. Its nesting claim concerns the original scalar economic model; it is not an assertion that a full dynamic policy was already present in the earlier isolated query.
'''
    frozen=frozen.replace(r'\subsection{Primitives and Bellman regularity}',note+'\n'+r'\subsection{Primitives and Bellman regularity}',1)
    put(R/'sections/accuracy62-print.tex',frozen)
    path=R/'sections/study62.tex';text=path.read_text().replace(r'Tables~\ref{tab:targets62} and~\ref{tab:rungs62} in the supplement', 'The supplementary target and refinement tables');put(path,text)
    put(R/'response.md',(R/'response62.md').read_text())
    entries_path=R/'publication/bibliography-entries.json';entries=json.loads(entries_path.read_text())
    entries['yang2020convex']=r'''\bibitem[\protect\citeauthoryear{Yang}{Yang}{2020}]{yang2020convex}
\textsc{Yang, Insoon} (2020): \enquote{A Convex Optimization Approach to Dynamic Programming in Continuous State and Action Spaces,} \emph{Journal of Optimization Theory and Applications}, 187, 133--157.'''
    put(entries_path,json.dumps(entries,sort_keys=True,indent=2)+'\n')
    bib=R/'references.bib';text=bib.read_text()
    if 'yang2020convex' not in text:text+='\n'+r'''@article{yang2020convex,
 author={Insoon Yang},
 title={A Convex Optimization Approach to Dynamic Programming in Continuous State and Action Spaces},
 journal={Journal of Optimization Theory and Applications},
 volume={187}, pages={133--157}, year={2020},
 doi={10.1007/s10957-020-01747-1}, eprint={1810.03847}, archivePrefix={arXiv}
}
'''
    put(bib,text)
    put(R/'audit/LITERATURE62.json',json.dumps(dict(verified_primary_metadata=[dict(key='yang2020convex',url='https://arxiv.org/abs/1810.03847',journal_year=2020,volume=187,pages='133-157',doi='10.1007/s10957-020-01747-1')],style_source='https://www.econometricsociety.org/publications/econometrica/information-authors',scope='Primary metadata and related-work positioning; no claim of external journal acceptance or a complete editorial length assessment.'),indent=2)+'\n')
    for name,old in before.items():
        new=(R/(name+'.tex')).read_text();put(R/'audit'/(name+'-R61-to-R62.diff'),''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='R61/'+name+'.tex',tofile='R62/'+name+'.tex')))
    if science62.verify()!=freeze:raise AssertionError('Author integration changed frozen science')
    put(marker,json.dumps(dict(status='assembled',baseline_commit='19f17cef194b620cfbf9d33e7c78ee051a2dddf0',review_commit='08ca068d318ce159401b36655eccea1e05490d01',science_freeze_sha256=freeze,abstract_words=len(ABSTRACT.split()),frozen_theorem_sha256=digest(R/'sections/accuracy62.tex'),print_copy_sha256=digest(R/'sections/accuracy62-print.tex'),ordinary_document_roles=list(DOCS),predecessor_branches_modified=False),indent=2)+'\n')
    put(R/'README.md',r'''# Neural Bellman Operators — R62

This is the original NBO paper revised in response to the R61 advisory report.
The main additions prove primitive Bellman regularity and a second-order
original-optimum certificate for the actual acquired policy, and execute a
prospective multidimensional and complete two-control comparison.

Read [the article](build/ECTA.pdf), [technical supplement](build/supp.pdf), and
[point-by-point response](build/response.pdf). Ordinary sources are ECTA.tex,
supp.tex and response.md. Complete and development companions preserve the
preceding theory, applications, failed targets and adverse comparisons.

## Reproduction

Install Python 3, numpy, scipy, sympy, scikit-learn, g++, Boost headers,
pandoc, poppler-utils and the LaTeX dependencies used by econsocart. Then run:

    python3 revisions/2026-10-10-r62/code/build62.py

The ordinary build verifies immutable scientific outputs and regenerates
current tables and seven documents. It does not retrain, resimulate, or retime
scientific services. PROTOCOL62.md and SOURCE_FREEZE62.json precede production.
PREPRODUCTION_CORRECTION62.json records the original-discount fixture correction
made before that freeze. The frozen theorem source remains separate from its
print-layout copy.

## Evidence

results62 retains every fitting seed, own-future training record, action array,
Bellman reference, target, path endpoint and clock. SCIENCE_REPLAY62.json states
the exact replay scope: all stored selections and error/interval recursions,
with a fixed subset of primitive nodal queries reintegrated. It is not a claim
of independently integrating every production endpoint again.

RELEASE62.json records tests and document gates. CLEAN_REBUILD62.json records
the clean offline source reproduction. FINAL_DELIVERY62.json is required for a
complete release and binds the final deliverables. Font substitutions, if any,
remain recorded separately from missing-glyph and overflow checks. A visual
inspection is claimed only when a separate inspection record exists.

Original-optimum accuracy, actual expected-cost ranking, finite-seed fitting
reliability and complete release work are distinct claims. No universal neural
superiority, empirical fee calibration, controlled multi-architecture result,
or dimension-free runtime is inferred from the finite experiment.
''')
    print(json.dumps(dict(status='assembled',abstract_words=len(ABSTRACT.split()),science_freeze_sha256=freeze)),flush=True)
if __name__=='__main__':main()
