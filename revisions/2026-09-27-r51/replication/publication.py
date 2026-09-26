"""Materialize ordinary R51 journal sources and tables, retaining R50 and R48."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,shutil
R=Path(__file__).resolve().parent.parent; REPO=R.parents[1]; OLD=REPO/'revisions/2026-09-26-r50'; P=R/'paper'; G=P/'generated'

def fmt(q,n=6,upper=False):
    x=F(q);scale=10**n
    k=-((-x.numerator*scale)//x.denominator) if upper else x.numerator*scale//x.denominator
    sign='-' if k<0 else '';k=abs(k);return f'{sign}{k//scale}.{k%scale:0{n}d}'

def esc(s):return s.replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')

def main():
    G.mkdir(parents=True,exist_ok=True)
    S=json.loads((R/'SUMMARY.json').read_text());rows=[json.loads(p.read_text()) for p in sorted((R/'results').glob('*.json'))]
    common=[r for r in rows if not r['restricted']];uniform={r['raw']['id']:r for r in rows if r['restricted']}
    metrics={'CRCases':S['models'],'CRHits':S['common_hits'],'CRControls':S['controlled_models'],'CRSavings':S['strict_common_continuation_savings'],'CRWork':f"{S['all_in_seconds']:.2f}",'CRMaxWork':f"{S['max_all_in_seconds']:.2f}",'CRMaxNodes':S['max_nodes'],'CRProofKiB':f"{S['max_proof_bytes']/1024:.1f}"}
    (G/'metrics.tex').write_text(''.join('\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in metrics.items()))
    table=[];full=[];curves=[]
    for r in common:
        other=uniform[r['raw']['id']];saving=F(other['lower'])-F(r['upper'])
        table.append(' & '.join([esc(r['raw']['id']),fmt(r['lower']),fmt(r['upper'],upper=True),f"{float(F(r['width'])):.6f}",fmt(saving),f"{r['all_in_seconds']:.2f}",str(r['nodes'])])+r' \\')
    for r in rows:
        name=r['raw']['id'];method='Uniform' if r['restricted'] else 'Common'
        full.append(' & '.join([esc(name),method,fmt(r['lower']),fmt(r['upper'],upper=True),f"{100*r['relative_width']:.4f}",f"{r['all_in_seconds']:.3f}",str(r['nodes']),f"{r['proof_bytes']/1024:.1f}"])+r' \\')
        for t in r['trace']:
            curves.append({'case':name,'method':method,**t})
    (G/'controlled_rows.tex').write_text('\n'.join(table)+'\n');(G/'all_rows.tex').write_text('\n'.join(full)+'\n')
    (R/'WORK_CURVES.json').write_text(json.dumps(curves,indent=2)+'\n')
    pre=(OLD/'paper/preamble.tex').read_text().replace('Revision R50 --- September 26, 2026','Revision R51 --- September 27, 2026')
    (P/'preamble.tex').write_text(pre)
    front=(OLD/'paper/front.tex').read_text().replace('revisions/2026-09-26-r50/paper/preamble','revisions/2026-09-27-r51/paper/preamble')
    front=front.replace(r'\begin{document}',r'\input{revisions/2026-09-27-r51/paper/generated/metrics}'+'\n'+r'\begin{document}',1)
    start=front.index(r'\begin{abstract}');end=front.index(r'\end{abstract}')+len(r'\end{abstract}')
    abstract=r'''\begin{abstract}
An organization revises a decision rule at minimum implementation cost while protecting operating performance after every state--date restart. One randomized Markov continuation must serve all restarts. We characterize the occupation relaxation optimized by restart prices, certify price-search loss, and restore common continuation through regret-budget covers. For continuous-density kernels, paired approximations retain the original Borel-policy target. A controlled-density model additionally admits an exact two-moment characterization, an explicit Borel policy realization, and integrated global certificates without policy discretization. All \CRCases{} new models attain width $10^{-3}$; \CRControls{} have state- and action-dependent densities, and \CRSavings{} certify strict savings from state-dependent continuation. Earlier uniform-reset successes and every unsuccessful finite refinement are retained separately. The controlled-density result exploits two periods and proportional final implementation costs.
\end{abstract}'''
    front=front[:start]+abstract+front[end:]
    insertion=r'''
The controlled-density extension in Section~\ref{sec:controlled51} removes action-independent resetting from the executed continuum evidence. Transition densities depend jointly on the current state, next state, and selected action. An exact characterization of feasible continuation moments reduces the unrestricted Borel problem to two common coordinates. Each feasible point has an explicit state-dependent policy realization; every lower rectangle integrates a valid relaxation over the full state interval. A rational series remainder encloses the only transcendental operation. This supplies a theorem--algorithm--conditional economic comparison without changing the initial population or replacing common policies by edge-specific budgets. All \CRCases{} new models reach the target, and \CRSavings{} yield strict certified implementation savings against the exact spatially uniform-regret counterfactual. This comparator is a policy-class restriction, not a claim of superiority to an external solver.
'''
    front=front.replace(r'\subsection{Relation to the literature}',insertion+'\n'+r'\subsection{Relation to the literature}',1)
    (P/'front.tex').write_text(front)
    oldev=(OLD/'paper/evidence.tex').read_text()
    oldev=oldev.replace('action-dependent diffuse-kernel performance,','long-horizon action-dependent diffuse-kernel performance,')
    oldev=oldev.replace("The paper's target remains certified minimum-cost revision under one common policy.","The paper's target remains certified minimum-cost revision under one common policy. Section~\\ref{sec:controlled51} now executes genuinely controlled densities through a common two-moment continuation. The new comparison proves state-contingency savings while preserving global operating protection; it does not resolve the historical finite failures by relabeling a new cohort.")
    oldev=oldev.replace(r'Uniform-reset continuum &',r'Controlled-density continuum & Two periods, proportional terminal costs; exact common-moment realization and integrated cover & 27 models, including 24 state/action-dependent densities; all 54 paired-class runs \\'+ '\n'+r'Uniform-reset continuum &')
    (P/'retained_evidence.tex').write_text(oldev)
    app=(OLD/'paper/appendix.tex').read_text()
    pos=app.index('The numerical supplement contains all 28 new rows')
    app=app[:pos]+r'''The current supplement contains all 54 controlled-density runs and appends the complete R50 supplement, including its 78 diffuse reset runs, 48 retrospective finite runs, price audits, and reconstructed complete R48 article. The older statement about 28 new rows belonged to R48 and remains in that historical article, not as a count for the current revision. Earlier manuscripts retain the strict-gap quadratic analysis, exact aggregation, observable fibers, original uniform-law intervals and nonlinear examples. The original sources and proof records remain unchanged in the parent history. The new preservation and dependency manifests distinguish unchanged inherited inputs from new generated material; preservation is not evidence of an additional numerical target hit.
'''
    (P/'appendix.tex').write_text(app)
    (P/'evidence.tex').write_text(r'''
\section{Controlled-density evidence and decision consequences}\label{sec:evidence51}
Before generating the formal models, source hashes, seed choices, the absolute target $10^{-3}$, a 12-second soft construction cap, and a 32,767-node cap were committed in the new revision branch. The exact freeze commit is \texttt{5b9ad94a866f25d4552dce088b677763f4d9ce06}. Numerical pilot selection is disclosed in that record. This is within-project prospective provenance, not external preregistration. The 27 models comprise three seeds in each of nine cells. Seven family-A cells vary one of discounting, allowance, and density control around a common base; the same seed perturbation is shared within each paired comparison. Two further families each contribute three seeds. The no-control cell has three negative controls; the remaining 24 densities depend on both state and action.

All \CRCases{} unrestricted runs and all \CRCases{} uniform-regret counterfactual runs attain the target. Every proof is independently replayed from the serialized file. The paired runs use isolated worker processes. Worker all-in time, including construction, serialization, and replay, sums to \CRWork{} seconds; the largest is \CRMaxWork{} seconds. Interpreter startup and the separate contract-test suite are excluded. The largest cover contains \CRMaxNodes{} nodes and the largest compressed proof occupies \CRProofKiB{} KiB. No construction time cap is reported as an all-in cap. Complete traces, rather than only target hits, are retained in the numerical supplement and machine-readable records.

\begin{table}[htbp]\centering\small\setlength{\tabcolsep}{3pt}
\caption{Every new controlled-density model and its certified policy-class saving}\label{tab:controlled51}
\begin{tabular}{@{}lrrrrrr@{}}\toprule
Model & $L$ & $U$ & Width & $L_0-U$ & Seconds & Nodes\\\midrule
\tablerows{revisions/2026-09-27-r51/paper/generated/controlled_rows.tex}
\bottomrule\end{tabular}
\par\smallskip\footnotesize $[L,U]$ is the unrestricted common-policy interval; $L_0$ is the uniform-terminal-regret lower endpoint. Displayed endpoints and savings are outward rounded; exact fractions determine acceptance. A negative displayed saving is an unresolved comparison, not evidence of a disadvantage from the larger policy class. All costs are normalized designed quantities.
\end{table}

In \CRSavings{} models, $L_0-U>0$ proves an implementation saving that no spatially uniform terminal-regret policy can attain. Each is also a positive-cost certification; the comparison does not rely on a zero-cost baseline. The three no-control cases produce no strict saving, as the value is then independent of the spatial moment. Their exact model optima coincide analytically even though finite numerical intervals have nonzero width. An administrative fee $f<L_0-U$ can therefore be paid without losing the certified advantage in a positive-saving row. Both the inequality and the ratio $(L_0-U)/U_0$ are unchanged by common positive rescaling of costs and the fee. These are conditional budget implications, not empirical dollar savings or welfare estimates.

The result complements, rather than substitutes for, the retained finite and reset evidence. It solves a truly action-dependent diffuse model against all Borel policies and restores the same continuation on every incoming edge. Its two-date proportional-cost structure is explicit. It supplies neither a new closure of the eight historical finite failures nor a long-horizon controlled-density performance result. The remaining finite intervals, the thirty moving-atom uniform-law intervals, the exact-price audits, and the 39 earlier reset models retain their original status.
''')
    inputs=['revisions/2026-09-27-r51/paper/front']+[f'revisions/2026-09-26-r50/paper/{x}' for x in ['duality','pricecompletion','finite','budget','continuum','density','reset']]+['revisions/2026-09-27-r51/paper/controlled','revisions/2026-09-27-r51/paper/evidence','revisions/2026-09-27-r51/paper/retained_evidence','revisions/2026-09-27-r51/paper/appendix','revisions/2026-09-26-r50/paper/references']
    (P/'main.tex').write_text('\n'.join('\\input{'+x+'}' for x in inputs)+'\n\\end{document}\n')
    (REPO/'ECTA_R51.tex').write_text('\\input{revisions/2026-09-27-r51/paper/main}\n')
    supplement=r'''\input{revisions/2026-09-27-r51/paper/preamble}
\begin{document}\begin{frontmatter}\title{Numerical Supplement: Controlled Densities and Preserved Evidence}
\runtitle{R51 Numerical Supplement}\begin{aug}\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}}\address[id=add1]{\orgname{Peking University}}\end{aug}
\begin{abstract}Every new model--method run is retained, followed by the complete R50 numerical supplement and reconstructed R48 manuscript. The final fraction intervals and full binary covers are independently readable from the proof files. The inherited material remains historical evidence, not a claim of new execution.\end{abstract}\end{frontmatter}
\section{Every controlled-density run}
Common optimizes all feasible shared moments; Uniform is the exact policy-class counterfactual with spatially uniform final regret. A worker timer includes serialization and independent replay but not interpreter startup. The soft construction budget is not an all-in budget. Model primitives, the moment geometry, all cover nodes, and individual process high-water memory are in the accompanying JSON. All 54 runs are shown, with no selection by outcome.
\begingroup\footnotesize\setlength{\tabcolsep}{2.5pt}
\begin{longtable}{@{}llrrrrrr@{}}\caption{Complete R51 execution records}\\\toprule
Case & Class & $L$ & $U$ & Rel. \% & Seconds & Nodes & KiB\\\midrule\endfirsthead
Case & Class & $L$ & $U$ & Rel. \% & Seconds & Nodes & KiB\\\midrule\endhead\bottomrule\endfoot
\tablerows{revisions/2026-09-27-r51/paper/generated/all_rows.tex}
\end{longtable}\endgroup
\section{Inspection and arithmetic boundary}
The standalone reader imports no constructor, numerical solver, or project mathematical library. It enumerates all moment corners afresh, integrates a separately derived binding-mixture expression, and uses a different logarithm truncation and precision. It checks raw-model conditions, feasible common moments, every binary partition, every discarded rectangle, all inherited lower bounds, the final upper cost, and target status. Eight contract tests include tampered lower bounds, invalid moments, an omitted cover child, false moment-set pruning, high-precision logarithm and integral cross-checks, and an independent SciPy row-LP comparison. These are code-path and arithmetic checks, not independent scientific replication.

A fresh reader can start from \path{BENCHMARK.md} and one proof without importing the constructor. \path{WORK_CURVES.json} retains all available power-of-two-node checkpoints with elapsed construction time. Their bounds do not include hypothetical future verification costs. Final all-in cost is separately reported. The original proof files retain exact fractions; printed decimals are not the acceptance boundary.

\section{Full inherited supplement}
The following pages reproduce \path{SUPP_R50.pdf} from the pinned R50 parent. They include all 78 earlier reset runs, finite failures, price audits, earlier responses to measurement concerns, and the reconstructed complete R48 manuscript. No inherited result is counted as a new controlled-density run.
% Historical SUPP_R50 pages are appended by assemble_pdfs.py.
\end{document}
'''
    (P/'supplement.tex').write_text(supplement);(REPO/'SUPP_R51.tex').write_text('\\input{revisions/2026-09-27-r51/paper/supplement}\n')
    oldmap=json.loads((OLD/'RESPONSE_MAP.json').read_text());deltas={
      1:'R51 adds ordinary article, supplement and response entry points, full generated tables, a complete binary-cover archive, a standalone reader, a verified source archive, and a content-hash manifest. The prior publication artifact contained a truncated source tarball although its PDFs were committed; the new workflow explicitly validates every archive member and cannot report publication success before that check.',
      2:'The new controlled-density study has 27/27 unrestricted target hits and 27/27 uniform-regret counterfactual hits. Seventeen rows prove a strict implementation saving. This is a distinct Borel-policy result, not a claim that the old price method has acquired additional R48 hits.',
      3:'R50 large reset results remain intact. The new controlled problem is an infinite-state two-date problem reduced exactly to two moments; it is not counted as a medium/large finite closure or long-horizon controlled-density result.',
      4:'No unfinished historical interval is discarded. The new theorem resolves the controlled-density common continuation on a separately declared model class; the original eight finite failures and thirty moving-atom intervals remain separately identified.',
      5:'Every new run reports isolated-worker construction, independent replay, all-in cost, cover size, proof size and memory. Power-of-two-node checkpoints give within-run width/work data. The uniform-regret comparison is economic, not a claim about the computational superiority of prices.',
      6:'The uncapped price upper witnesses and cap/mask audit from R50 are preserved. The new controlled solver needs no price cap or mask scheduling; its stopping inequality directly brackets the common-policy optimum.',
      7:'The exact common-moment theorem supplies a feasible-moment characterization, an explicit Borel realization, integrated lower rectangles and a quantitative two-coordinate refinement bound. This directly turns an omitted shared-continuation coupling into an executed global solver for genuinely controlled densities.',
      8:'For this structured model the sufficient cover count is of inverse-squared accuracy order, apart from precision work, with constants depending on operating slack. No general polynomial complexity claim is made. The effective dimension is exactly one in the no-control negative controls.',
      9:'SciPy supplies an independent row-LP cross-check in the contract suite; it does not supply a verified global lower bound. No external global-solver victory or independently proof-logged comparator is asserted. The new primary solver uses no optimizer output for either endpoint.',
      10:'Three frozen seeds appear in every one of nine cells. All 54 resulting runs are retained. The 27 models remain internally designed, and the source-freeze record explicitly discloses pilot-guided design rather than asserting external validation.',
      11:'The family-A cells share seed perturbations and vary one factor at a time: discount, allowance, or density control. No-control and reversed-control cells separately diagnose dependence on the transition mechanism.',
      12:'The new raw operating rewards yield exactly known operating values, which are printed in the model specification. This allows direct examination of common-continuation optimization but does not constitute a difficult learned-oracle experiment. The inherited witness-interface and precision results remain unchanged.',
      13:'The new transition density depends jointly on state, successor state and selected action. Its moment-set proof ranges over all Borel continuations, its upper realization is globally feasible, and no spatial discretization enters either endpoint. The theorem does not apply across singular moving-atom kernels.',
      14:'The uniform initial population is retained. No replacement by a two-point fleet is used. The new proof solves a genuinely controlled-density target, while the finite-fleet results and their exponential reachability qualifications remain in the inherited article.',
      15:'Seventeen exact interval separations prove conditional savings from state-dependent continuation relative to the uniform-regret counterfactual. The fee test and scale-free ratio make the decision implication explicit. The primitives are not estimated, and no arbitrary dollar conversion or welfare estimate is introduced.',
      16:'The absolute target remains 1/1000. Every new run also reports relative width; the supplement explains scale-invariant fee and policy-class savings. A nonpositive saving certificate is never interpreted as evidence that unrestricted policies are worse.',
      17:'The three no-control rows are negative controls, not optimal-action tie experiments. They correctly produce no strict savings. The original tie evidence and open tie cases remain unchanged; this study is not relabeled as broad tie robustness.',
      18:'The original theorem-level literature map and all sixteen R50 references are retained. The elementary moment extremum is proved directly and is not advertised as a new general moment theorem; the contribution is its exact coupling of operating and implementation continuation for the stated policy object.',
      19:'A standalone standard-library reader uses independently written corner enumeration, mixture integration, and a longer logarithm series. Mutation tests challenge cover completeness and feasibility. This is stronger implementation separation but not an external research-team replication; the external-facing benchmark specification makes that remaining task well-defined.',
      20:'The title and original minimum-cost common-policy objective are retained. The article integrates the new controlled-density theorem, executable cover and conditional policy-class comparison, while preserving the complete R50 and R48 argument and all failed results. New structure is established rather than replacing the target by a narrower economic objective.'}
    mapping={'review_commit':oldmap['review_commit'],'base_commit':'8fb2b5e09610bf596758892cd5ffd5ad83ddb707','revision':'R51','items':[]}
    md=['# R51 response to the latest R48 referee report','','The review report is addressed on top of the complete R50 revision. The manuscript retains its objective, title, earlier theorems, proofs, comparisons, and all failed intervals. The new contribution is an exact common-moment solver for state/action-dependent continuous densities under the original diffuse initial law.','','## Major findings']
    tex=[r'\input{revisions/2026-09-27-r51/paper/preamble}',r'\begin{document}',r'\begin{frontmatter}\title{Response to the R48 Referee Report: Revision R51}\runtitle{Referee Response}',r'\begin{aug}\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}}\address[id=add1]{\orgname{Peking University}}\end{aug}\end{frontmatter}',r'\section{Revision overview}',r'The report at commit \texttt{73a4f708581834692b817649ba5538b640b9e58d} is the latest reviewed report. R51 builds on the complete R50 manuscript, preserves the original scientific target, and adds controlled-density common-moment theory with a fully executed paired solver. The original finite failures are neither removed nor relabeled. The full previous response follows the incremental replies below.']
    for i,item in enumerate(oldmap['items']):
        new=dict(item)
        if i<20:
            n=i+1;new['r51_increment']=deltas[n];new['r51_location']='paper/controlled.tex; paper/evidence.tex; BENCHMARK.md; results/; standalone checker; R51_REVIEW.md'
            md+=['',f"### {item['id']}: {item['title']}",'',deltas[n],'', '**Retained R50 response:** '+item['response'],'','**Evidence boundary:** '+item['boundary']]
            tex+=[r'\subsection{'+esc(item['id']+': '+item['title'])+'}',esc(deltas[n])]
        else:
            new['r51_increment']='Retained in full in the attached R50 response. R51 additionally provides exact controlled-model endpoints, both policy classes, isolated all-in timing, proof sizes, a whole-state moment realization, and a complete standalone cover reader. No new claim of external solver certification, statistical calibration, or broad tie robustness is attached to this item.'
        mapping['items'].append(new)
    md+=['','## Forty detailed comments','','All forty detailed replies remain in RESPONSE_MAP.json and the attached full R50 response. R51 additions are indexed per item in the machine-readable map; inherited evidence is not described as new execution.']
    for item in mapping['items'][20:]:
        md+=['',f"### {item['id']}: {item['title']}",'',item['response'],'',item['r51_increment'],'','**Boundary:** '+item['boundary']]
    tex += [r'\section{All forty technical comments and the full retained response}',r'The complete R50 response on the following pages addresses all twenty major findings and forty detailed comments. These pages are retained as historical replies and supplemented, not silently revised, by the R51 increments above. The R51 machine-readable map contains every comment, its inherited reply and its current increment.',r'% Historical RESPONSE_R50 pages are appended by assemble_pdfs.py.',r'\end{document}']
    (R/'RESPONSE_MAP.json').write_text(json.dumps(mapping,indent=2)+'\n');(REPO/'RESPONSE_R51.md').write_text('\n'.join(md)+'\n')
    (P/'response.tex').write_text('\n\n'.join(tex)+'\n');(REPO/'RESPONSE_R51.tex').write_text('\\input{revisions/2026-09-27-r51/paper/response}\n')
    (REPO/'R51_REVIEW.md').write_text(f'''# R51 referee-ready review object

**Article:** Certified Bellman Operators for Costly Policy Revision  
**Author:** Qian QI, Peking University  
**Latest report:** reviews/2026-09-26-econometrica-r48/referee_report.md at 73a4f708581834692b817649ba5538b640b9e58d  
**Preserved parent:** 8fb2b5e09610bf596758892cd5ffd5ad83ddb707 (complete R50)  
**Formal source-hash freeze:** 5b9ad94a866f25d4552dce088b677763f4d9ce06  
**New revision date:** September 27, 2026

## Read in this order

- `ECTA_R51.pdf` / `ECTA_R51.tex`: full integrated article, not a patch or addendum.
- `SUPP_R51.pdf`: every new controlled-density run plus the complete inherited supplement and reconstructed R48 article.
- `RESPONSE_R51.pdf` / `.md`: direct replies to all 20 findings and preserved full replies to all 40 technical comments.
- `revisions/2026-09-27-r51/BENCHMARK.md`: self-contained target and proof specification.
- `revisions/2026-09-27-r51/RESPONSE_MAP.json`, `SOURCE_FREEZE.json`, `SUMMARY.json`, `MANIFEST.json`, `VERIFICATION.json`.

## New executed result

{S['common_hits']}/{S['models']} unrestricted controlled-density models and {S['uniform_hits']}/{S['models']} uniform-regret counterfactuals attain 1/1000. Of these, {S['controlled_models']} have genuinely state/action-dependent continuous densities. {S['strict_common_continuation_savings']} exact interval separations establish strict conditional implementation savings. All 54 serialized complete covers pass the standalone reader. The model has two periods, two actions and proportional final implementation costs; its exact moment reduction covers all Borel policies. It is not a price relaxation, discretized-policy lower bound, empirical calibration or external researcher replication.

## Rebuild and reproduce

```sh
bash R51_BUILD.sh
# Regenerate all new runs, verify, and rebuild without inherited local intermediates:
bash R51_REPRODUCE.sh
```

The new code needs Python's standard library for construction and replay. Contract cross-checks additionally use scipy and mpmath. TeX needs the retained econsocart class and the standard packages used by R50. Existing R50 PDFs are explicit, committed inputs to the preserved-history sections, not hidden generated files. All their hashes and the transitive article source inputs are listed in the new manifest. The complete repository retains their ordinary sources and reproduction commands.

No previous branch, report, manuscript, result or proof is overwritten. Original finite nonclosures, R50 unsuccessful refinements and the thirty moving-atom intervals remain visibly separate. The publication archive is written outside its input tree, then every member is read back to check integrity; this repairs the truncated-tarball issue in the earlier R50 artifact.
''')
if __name__=='__main__':main()
