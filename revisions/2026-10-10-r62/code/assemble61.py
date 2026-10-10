"""One-time ordinary manuscript integration. Scientific sources are never edited."""
from pathlib import Path
import difflib,hashlib,json,re,shutil
from assemble56 import labels
R=Path(__file__).resolve().parents[1]
DOCS=('ECTA','supp','development','development-supp','complete','complete-supp')
ABSTRACT=r'''We develop Neural Bellman Operators that construct continuations from their own fitted futures and return feasible economic policies. A constructive backend connects primitive resources to loss against the original Bellman optimum. For trained affine--ReLU continuations, analytic innovation integration yields exact action witnesses. We give a rational finite-difference construction that preserves the original witness without a unique-minimizer or separation assumption, and a constrained-lattice extension for several controls and box-uniform shocks. Stable whole-cell verification separates fitted optimization from implemented-policy accuracy. In the original nonlinear investment family, ninety-six complete services evaluate prespecified economic targets with conventional comparators and full return costs. A matched native factorial identifies both large-lattice savings and small-lattice reversals. Common-reference Bellman bounds attain a one-sixteenth all-state tolerance in the two-state, two-date economy; separate verification certifies the unchanged actors actually returned by the services. Failed targets, adverse comparisons and broader applications are retained under their original hypotheses.'''
CONCLUSION=r'''The additional exact construction makes the fitted action contract robust to flatness, adjacent ties and cancellation without assuming that an interval screen isolates one action. Its constrained-lattice extension separates action dimension from state dimension and gives an explicit integration and fallback account. The language- and representation-matched native factorial shows where the finite-difference algorithm reduces measured work and where a short lattice makes exhaustive evaluation cheaper. Complete prospective services retain their own return boundary, conventional comparators and unsuccessful targets.

Common-reference Bellman verification further connects that computation to the original optimum. The constructed two-date policy attains an all-state one-sixteenth tolerance on the declared ladder. Revalidating every distinct actually returned two-date actor, without changing its parameters or actions, gives a separate accuracy account for deployed policies. Fixed-cover stability, full continuous-action lower covers and closed actor ranges are explicit conditions in that argument. The new certificates therefore strengthen the original NBO accuracy objective rather than replacing it with a gain relative to a convenient initial policy.
'''
BIB={
 'murota2003':(r'\bibitem[\protect\citeauthoryear{Murota}{Murota}{2003}]{murota2003}'+'\n'+r'\textsc{Murota, Kazuo} (2003): \emph{Discrete Convex Analysis}. Philadelphia: Society for Industrial and Applied Mathematics.', '@book{murota2003,\n author={Kazuo Murota},\n title={Discrete Convex Analysis},\n publisher={Society for Industrial and Applied Mathematics},\n address={Philadelphia},\n year={2003}\n}\n'),
 'moore2009':(r'\bibitem[\protect\citeauthoryear{Moore, Kearfott, and Cloud}{Moore et~al.}{2009}]{moore2009}'+'\n'+r'\textsc{Moore, Ramon E., R. Baker Kearfott, and Michael J. Cloud} (2009): \emph{Introduction to Interval Analysis}. Philadelphia: Society for Industrial and Applied Mathematics.', '@book{moore2009,\n author={Ramon E. Moore and R. Baker Kearfott and Michael J. Cloud},\n title={Introduction to Interval Analysis},\n publisher={Society for Industrial and Applied Mathematics},\n address={Philadelphia},\n year={2009}\n}\n')}

def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(p,text):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def save(p,v):put(p,json.dumps(v,indent=2,sort_keys=True)+'\n')
def main():
    marker=R/'audit/ASSEMBLY61.json'
    if marker.exists():print('R61 already assembled; ordinary author edits remain unchanged.');return
    prep=json.loads((R/'audit/PREPARATION61.json').read_text())
    for family in ('protected_sha256','scientific_sha256'):
        for name,h in prep[family].items():
            if digest(R/name)!=h:raise AssertionError('Changed protected input: '+name)
    snapshots={d:(R/(d+'.tex')).read_text() for d in DOCS}
    draft=R/'preserved/R60-theory-drafts';draft.mkdir(parents=True,exist_ok=True)
    for name in ('search60.tex','centered60.tex'):shutil.copy2(R/'sections'/name,draft/name)
    path=R/'sections/search60.tex';text=path.read_text()
    old='For a refining family, suppose the ideal lower and upper one-step enclosures applied to the true next Bellman value have uniform errors at most $\\eta_t$, inclusive of robust-action approximation, state and innovation covering, and arithmetic.'
    new='For a refining family, suppose the exact lower and upper endpoint maps at each fixed approximation level are order preserving and $\\beta_t$-nonexpansive in the supremum norm. Suppose their one-step errors at the true next Bellman value, together with uniformly bounded numerical endpoint errors on the relevant input range, are at most $\\eta_t$, inclusive of robust-action approximation and state, action and innovation covering.'
    if text.count(old)!=1:raise AssertionError('Unexpected R60 consistency clause')
    text=text.replace(old,new)
    old='Applying a probability kernel to a uniformly bounded next-date discrepancy multiplies it by at most $\\beta_t$. The stated ideal enclosure errors consequently give'
    new='Nonexpansivity of the fixed-cover endpoint maps bounds the propagated next-date discrepancy by $\\beta_t$ times its supremum norm. Adding the uniformly budgeted local and numerical endpoint errors consequently gives'
    if text.count(old)!=1:raise AssertionError('Unexpected consistency proof')
    text=text.replace(old,new).replace('B+\\log(Q+1)+\\log(m+h+2)','B+\\log(Q+1)+\\log(\\bar j+2)+\\log(m+h+2)')
    text=text.replace('including powers of $Q$ and the rational breakpoint calculations.','including powers of $Q$, the action-index bound, and the rational breakpoint calculations.')
    path.write_text(text)
    save(R/'audit/THEORY_CLARIFICATION61.json',dict(original_draft_sha256=digest(draft/'search60.tex'),revised_source_sha256=digest(path),runtime_bracket_changed=False,scientific_code_changed=False,clarification='Explicit fixed-cover order and supremum-norm stability plus uniformly budgeted arithmetic for refinement consistency; operand bound includes action-index encoding. Runtime inclusion remains unchanged. New lemma and counterexample prove why the property matters.',tests=['test_fixed_cover_operator_is_discount_nonexpansive','test_inclusion_alone_does_not_imply_stability']))
    additions=r'\input{sections/search60}'+'\n'+r'\input{sections/centered60}'+'\n'+r'\input{sections/stability61}'+'\n'
    for d in DOCS:
        text=snapshots[d]
        text=text.replace(r'\input{preamble}',r'\input{preamble}'+'\n'+r'\input{tables/facts61}'+'\n'+r'\setcounter{secnumdepth}{2}',1)
        if d=='ECTA':
            text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
            old=r'\input{sections/intro57}'+'\n'+r'\input{sections/intro59}'
            if text.count(old)!=1:raise AssertionError('Original introduction inputs changed')
            text=text.replace(old,r'\input{sections/intro61}',1)
            text=text.replace(r'\input{sections/lossless59}',r'\input{sections/lossless59}'+'\n'+additions,1)
            text=text.replace(r'\input{sections/study59}',r'\input{sections/study59}'+'\n'+r'\input{sections/study61}',1)
            text=text.replace(r'\appendix',CONCLUSION+'\n'+r'\appendix',1)
        elif d=='supp':
            text=text.replace(r'\input{sections/supp59}',r'\input{sections/supp59}'+'\n'+r'\input{sections/supp61}',1)
        elif d=='complete':
            text=text.replace(r'\section*{Current reading notice}',r'\section*{Current reading notice}'+'\n'+r'The R61 article, technical supplement and response form the current submission. This complete companion retains all preceding statements and adds the current exact-search, stability, fixed-policy and economic evidence. Earlier reading notices are historical.'+'\n',1)
            text=text.replace(r'\bibliographystyle{ecta-fullname}',additions+r'\input{sections/study61}'+'\n'+r'\bibliographystyle{ecta-fullname}',1)
        elif d=='complete-supp':
            text=text.replace(r'\bibliographystyle{ecta-fullname}',r'\input{sections/supp61}'+'\n'+r'\bibliographystyle{ecta-fullname}',1)
        else:
            # The two development documents remain complete historical bodies.
            text=text.replace(r'\end{frontmatter}',r'\end{frontmatter}'+'\n'+r'\section*{R61 preservation notice}'+'\n'+r'This is the retained development edition. The current R61 article and technical supplement contain the new exact-search and original-optimum verification results. The body below preserves its historical results, assumptions and observations.'+'\n',1)
        put(R/(d+'.tex'),text)
        put(R/'audit/differences61'/(d+'.diff'),''.join(difflib.unified_diff(snapshots[d].splitlines(True),text.splitlines(True),fromfile='R59/'+d+'.tex',tofile='R61/'+d+'.tex')))
    entries_path=R/'publication/bibliography-entries.json';entries=json.loads(entries_path.read_text());bib=(R/'references.bib').read_text()
    for key,(entry,bibtex) in BIB.items():
        if key not in entries:entries[key]=entry
        if not re.search(r'@\w+\s*\{\s*'+key+r'\s*,',bib):bib+='\n'+bibtex
    save(entries_path,entries);put(R/'references.bib',bib);shutil.copy2(R/'response61.md',R/'response.md')
    preservation={}
    for d,before in prep['baseline_labels'].items():
        after=set(labels(R,d));missing=sorted(set(before)-after)
        if missing:raise AssertionError((d,'Inherited labels missing',missing))
        preservation[d]=dict(inherited_labels=len(before),current_labels=len(after),missing=[])
    save(marker,dict(baseline_commit=prep['baseline_commit'],controlling_review_commit=prep['controlling_review_commit'],preservation=preservation,original_introductions_preserved=['sections/intro57.tex','sections/intro59.tex'],ordinary_old_wrappers='preserved/R59-before-R61',new_theory_draft_preservation='preserved/R60-theory-drafts',scientific_sources_changed=False,substantive_original_labels_removed=False,current_submission=['ECTA.tex','supp.tex','response.md']))
    put(R/'README.md',r'''# Neural Bellman Operators — R61

The current article continues the original NBO paper and responds to the
9 October 2026 R59 advisory review. The title, economic primitives,
constructive target, trained backend, original applications and adverse
observations are retained. Ordinary sources are committed in this directory.

## Submission

[Main article](build/ECTA.pdf), [technical supplement](build/supp.pdf), and
[point-by-point response](build/response.pdf) are the current reading set.
[Complete article](build/complete.pdf), [complete proof companion](build/complete-supp.pdf),
[development article](build/development.pdf), and [development proof companion](build/development-supp.pdf)
retain the full historical development under its original hypotheses.

## New results and evidence

The active article integrates the exact finite-difference witness, constrained
multi-action recovery, fixed-cover stability, original Bellman brackets and
fixed-policy revalidation. The completed R60 sources and outcomes remain frozen.
R61 independently reconstructs them, certifies every distinct returned two-date
actor without changing it, and executes a new C++ two-by-two ablation with all
four language/representation-matched cells and three batch sizes.

All ninety-six prospective returns, eighty attained targets, sixteen exhausted
budgets, full stress records, failed recording attempts and conventional
comparisons remain available. Current tables derive from verified records,
not manually inserted outcomes. New implementation-work observations are not
new training or independent policy-cost path samples.

## Reproduction and completion

Install Python 3 with numpy, scipy, sympy and scikit-learn, g++ with Boost,
pandoc, poppler-utils, and the LaTeX packages used by econsocart. Then run:

    python3 revisions/2026-10-09-r61/code/build61.py

The ordinary build checks source/evidence identities, runs inherited and new
tests, regenerates tables and compiles seven documents without network,
retraining or new policy-cost samples. Full R60 mathematical reconstruction:

    python3 revisions/2026-10-09-r61/code/audit61.py

That audit recreates exact witnesses, certificates, original-law endpoints and
Bellman brackets; its newly measured replay duration never replaces an old
service clock. The fixed-policy and native-factorial protocols state their
information sets, source freezes and cost boundaries explicitly.

A completed publication requires audit/FINAL_DELIVERY61.json, audit/RELEASE61.json
and audit/CLEAN_REBUILD61.json. The final delivery manifest binds the ordinary
sources, all retained evidence and the seven compiled documents. Compilation
and deterministic reproduction do not constitute an external editorial decision.
''')
    print(json.dumps(dict(status='ordinary_R61_sources_assembled',preservation=preservation),indent=2))
if __name__=='__main__':main()
