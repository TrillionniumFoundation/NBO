"""Build the R23 review object without rewriting any frozen scientific result."""
from pathlib import Path
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys, zipfile
ROOT = Path(__file__).resolve().parents[3]
REV = ROOT / 'revisions/2026-09-23-r23'
PAPER = REV / 'paper'
R22 = ROOT / 'revisions/2026-09-23-r22'
BASE = '9c6faca40fb204494d1e0f53be1468a7ee37341a'
REVIEW = 'fc16c4fb27b54e11c67ce1983b6830a39038f063'
RESULT = '7384d6bc43774ed91738db1c86ec6f21a1e6504e'

def load(path): return json.loads(path.read_text())
def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def number(x, digits=8, upper=True):
    return format(Decimal(str(x)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_CEILING if upper else ROUND_FLOOR), 'f')
def module(path, name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def recover_r22():
    old_index=(ROOT/'REVISION_INDEX.md').read_bytes()
    archive=REV/'archive/REVISION_INDEX_before_R23.md'
    if not archive.exists(): archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(old_index)
    m=module(R22/'replication/build.py','r22_publication_recovery')
    (ROOT/'REVISION_INDEX.md').write_bytes(archive.read_bytes())
    m.materialize(m.tables())
    (ROOT/'REVISION_INDEX.md').write_bytes(old_index)
    # Do not call the old compile_docs or manifest: they overwrite a frozen build record.

def tables():
    d=load(REV/'results/continuum.json'); rows=d['rows']
    nn=[r for r in rows if r['representation']=='neural' and r['optimizer']=='adam']
    vals={'NeuralRegret':number(max(r['K_regret_upper'] for r in nn),6),
          'GainMin':number(min(r['K_gain_from_initial_lower'] for r in nn),6,False),
          'ConditionalGain':number(min(r['uniform_payoff_gain_lower'] for r in d['comparisons']),6,False)}
    write(PAPER/'result_macros.tex','\n'.join(r'\newcommand{\RXXIII'+k+'}{'+v+'}' for k,v in vals.items())+'\n')
    names={'neural':'Neural','direct':'Direct','quotient':'Quotient'}
    lines=[r'\begin{table}[htbp]',r'\caption{Held-out matched-initial-policy systems, including the direct quotient}\label{tab:r23crossed}',r'\small\begin{tabular}{llrrrr}',r'\toprule',r'Ensemble & Configuration & Regret upper & Gain lower & Gradients & Gen. sec.\\\midrule']
    for r in rows:
        name=names[r['representation']]+'--'+('Adam' if r['optimizer']=='adam' else 'L-BFGS-B')
        lines.append(f"{r['base_seed']} & {name} & {number(r['K_regret_upper'])} & {number(r['K_gain_from_initial_lower'],8,False)} & {r['gradient_evaluations']} & {r['generation_seconds']:.3f}"+r'\\')
    lines += [r'\bottomrule\end{tabular}',r'\par\smallskip\parbox{.97\textwidth}{\footnotesize Every bound covers $K$ at $t=0,k=2$. Gain is relative to the independently initialized incumbent mixture. Each system contains four experts. Generation excludes checking and the shared dual. All prescribed configurations are retained.}',r'\end{table}']
    write(PAPER/'crossed_table.tex','\n'.join(lines)+'\n')
    lines=[r'\begin{table}[htbp]',r'\caption{Uniform actual-payoff advantage of neural--Adam}\label{tab:r23conditional}',r'\small\begin{tabular}{rlrrr}\toprule',r'Ensemble & Comparator & Vertex gain lower & Jensen upper & Uniform gain lower\\\midrule']
    for r in d['comparisons']:
        name='Direct--Adam' if r['comparison'].endswith('direct_adam') else 'Quotient--Adam'
        lines.append(f"{r['base_seed']} & {name} & {number(r['minimum_vertex_payoff_gain_lower'],8,False)} & {number(r['comparator_jensen_upper'])} & {number(r['uniform_payoff_gain_lower'],8,False)}"+r'\\')
    lines += [r'\bottomrule\end{tabular}',r'\par\smallskip\parbox{.97\textwidth}{\footnotesize The uniform bound subtracts the comparator mixture\textquotesingle s Jensen benefit and the stopping correction. It orders actual payoffs throughout $K$; it does not compare only regret envelopes.}',r'\end{table}']
    write(PAPER/'conditional_table.tex','\n'.join(lines)+'\n')
    lines=[r'\small\begin{longtable}{rrllrrrrr}',r'\caption{All 72 held-out final vertex configurations}\label{tab:r23ledger}\\',r'\toprule',r'Ensemble & $v$ & Rep. & Opt. & $N_f=N_g$ & Extra & Regret upper & Gen. sec. & Check sec.\\\midrule\endfirsthead',r'\toprule',r'Ensemble & $v$ & Rep. & Opt. & $N_f=N_g$ & Extra & Regret upper & Gen. sec. & Check sec.\\\midrule\endhead']
    for f in sorted((REV/'results/crossed').rglob('record.json')):
        r=load(f)
        lines.append(f"{r['base_seed']} & {r['vertex']} & {names[r['representation']][0]} & {'A' if r['optimizer']=='adam' else 'L'} & {r['function_evaluations']} & {r['line_search_evaluations']} & {number(r['delivered_certificate']['regret_upper'])} & {r['generation_seconds']:.3f} & {r['final_checker_seconds']:.3f}"+r'\\')
    lines += [r'\bottomrule\end{longtable}\normalsize',r'A denotes Adam; L denotes L-BFGS-B. The final-check column excludes initial certification and the shared dual. Full root and memory ledgers are in each record.']
    write(PAPER/'full_ledger.tex','\n'.join(lines)+'\n')
    dep=[
      ('Financed quotient, continuous bracket and conditioning',r'Main Theorem~\ref{main-thm:r23budget}; finite positive pricing measure, interior budget, controlled tail mass.',r'\path{replication/continuous_budget_brackets.py}, \texttt{bracket/main}; \path{results/continuous_budget_brackets.json}.', 'MPFR directed enclosures; proof-critical instantiation for 72 frozen policies.'),
      ('Finite-node class equality',r'Main Proposition~\ref{main-prop:r23class}; distinct nodes, finite real weights, sigmoid interiors.',r'\path{replication/interpolation_certificate.py}, \texttt{main}; \path{results/interpolation_certificate.json}.', 'MPFR interval elimination; proof-critical nonsingularity of one explicit construction.'),
      ('Uniform payoff and regret',r'Main Theorem~\ref{main-thm:r22jensen}; independent fixed-policy intervals, Hessian bounds, pair moments, stopping correction.',r'\path{replication/continuum_audit.py}, \texttt{main}; \path{results/continuum.json}; R22 \path{moment_jensen.py}, \texttt{moment\_jensen}; R20 \path{certify_stochastic.py}, \texttt{certify}.', 'Directed rational/Taylor binary64; proof-critical continuum transfer. Regret additionally uses the inherited dual.'),
      ('Vertex payoff acceptance',r'Fixed-policy lower/upper separation; unchanged continuous stopped-model checker.',r'\path{replication/run_study.py}, \texttt{main}; R22 \path{crossed.py}, \texttt{check}; every \path{results/crossed/*/*/*/record.json}.', 'Directed payoff certificate; proof-critical acceptance. Proposal objective is not the certificate.'),
      ('Global all-start-time comparison',r'Main Proposition~\ref{main-prop:r22cone}; admissible current-state actor, trace-compatible witness, residual cover.',r'R22 \path{time_envelope.py}, \texttt{main}; \path{results/full_state/time_envelope.json} and cell certificates.', 'MPFR cell cover and directed discounted suffix; proof-critical. Not identified actor improvement.'),
      ('Root derivative and quotient regression',r'First-derivative identity in the budget theorem; finite positive proposal rule.',r'\path{replication/tests.py}, \texttt{main}; \path{results/root_tests.json}.', 'Ordinary binary64 finite differences and shifts; diagnostic code tests, not economic proof.'),
      ('Restoration and recovery',r'Fixed-policy gate plus exact rollback; supervisor changes proposals outside restored state.',r'R22 \path{results/stress/summary.json} and \path{results/rejection_recovery/summary.json}.', 'State hashes and directed payoff intervals; implementation evidence, not convergence theorem.'),
      ('Sufficient re-budgeted increment',r'Main Proposition~\ref{main-prop:r23wealth}; same shapes/reserve, nonexit. Earlier numerical intervals remain separate.',r'R21 \path{results/continuum_audit.json} and frozen compensation checks.', 'Analytic monotonicity and separately directed welfare comparison; not minimum or unchanged-map variation.'),
      ('Cover and deployment costs',r'Main Proposition~\ref{main-prop:r22cover}; stated regularity and verified cover assumptions.',r'R22 \path{results/runtime_cost.json}; R23 \path{results/environment.json} and ledgers.', 'Analytic complexity plus ordinary timing; latency tests do not certify online quadrature error.')]
    lines=[r'\footnotesize\begin{longtable}{p{.15\textwidth}p{.24\textwidth}p{.30\textwidth}p{.17\textwidth}}',r'\caption{Proof dependencies, executable objects, and arithmetic roles}\label{tab:r23dependencies}\\\toprule',r'Assertion & Theorem and assumptions & Script and result & Role\\\midrule\endfirsthead',r'\toprule Assertion & Theorem and assumptions & Script and result & Role\\\midrule\endhead']
    lines += [' & '.join(row)+r'\\\addlinespace' for row in dep]
    lines += [r'\bottomrule\end{longtable}\normalsize']
    write(PAPER/'dependency_table.tex','\n'.join(lines)+'\n')
    return vals

def documents():
    base=(ROOT/'ECTA_R22.tex').read_text()
    start=base[:base.index(r'\begin{document}')].replace('Revision R22','Revision R23').replace('Revision R22','Revision R23')
    start=start.replace(r'\begin{document}', '')+r'\input{revisions/2026-09-23-r23/paper/result_macros}'+'\n'
    abstract=r'''We develop Neural Bellman Operators that separate policy improvement, unrestricted value comparison, and parameterization effects. In the original stopped consumption--portfolio economy, a financing equation removes a common-intercept direction. We prove its implicit projection, a continuous-price bracket including unbounded Gaussian tails, and equality of neural and direct finite-node policy classes. A nonsynchronized Jensen theorem certifies continuum payoff ordering for independently initialized experts. In a prospectively specified held-out design with 72 configurations, neural--Adam systems have regional regret below \RXXIIINeuralRegret{} and uniform payoff advantage above \RXXIIIConditionalGain{} over both matched direct--Adam coordinate systems. Direct L-BFGS-B remains stronger overall. An executed current-state actor/witness refinement reduces the complete-domain all-start-time bound to \RXXIIGlobalBound{}, without establishing the unchanged $.01$ objective. Directed proof instantiations, active-rejection tests, full cost ledgers, and preserved adverse outcomes identify the scope of each result.'''
    front=base[base.index(r'\begin{document}'):base.index(r'\input{revisions/2026-09-23-r22/paper/main}')]
    front=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:r'\begin{abstract}'+abstract+r'\end{abstract}',front,flags=re.S)
    current=['revisions/2026-09-23-r23/paper/introduction','revisions/2026-09-23-r18/paper/retained_foundations','revisions/2026-09-23-r22/paper/retained_r21_method','revisions/2026-09-23-r22/paper/method','revisions/2026-09-23-r23/paper/method','revisions/2026-09-23-r23/paper/results','revisions/2026-09-23-r23/paper/conclusion']
    proofs=['revisions/2026-09-23-r23/paper/proofs','revisions/2026-09-23-r22/paper/proofs','revisions/2026-09-23-r21/paper/proofs','revisions/2026-09-22-r14/paper/proofs','revisions/2026-09-23-r18/paper/new_proofs','revisions/2026-09-23-r18/paper/aligned_proofs','revisions/2026-09-23-r19/paper/proofs']
    oldmain=(R22/'paper/main.tex').read_text()
    historical=oldmain[oldmain.index(r'\input{revisions/2026-09-23-r22/paper/results}'):]
    historical=historical.replace(r'\input{revisions/2026-09-23-r22/paper/conclusion}', '')
    history=r'''\clearpage
\section{Dated historical theory and numerical development}\label{app:r23history}
The following material is retained from R14--R22. Each outcome retains its original policy, model, domain, and work budget. Historical descriptions of then-current evidence do not replace the present abstract and results. In particular, the R21 end-to-end baseline is not the later crossed representation experiment, and a re-budgeted wealth increment is not an unchanged-map welfare estimate.
\begingroup
\let\historicalsection\subsection
\let\historicalsubsection\subsubsection
\let\section\historicalsection
\let\subsection\historicalsubsection
'''+historical+'\n'+r'\endgroup'+'\n'
    write(PAPER/'historical_development.tex',history)
    tail=r'\clearpage\input{revisions/2026-09-23-r18/paper/references}'+'\n'+r'\end{document}'+'\n'
    main=start+front+'\n'.join(r'\input{'+x+'}' for x in current)+'\n'+r'\begin{appendix}'+'\n'+'\n'.join(r'\input{'+x+'}' for x in proofs)+'\n'+r'\input{revisions/2026-09-23-r23/paper/historical_development}'+'\n'+r'\end{appendix}'+'\n'+tail
    write(ROOT/'ECTA_R23.tex',main)
    supp=(ROOT/'SUPP_R22.tex').read_text().replace('ECTA_R22','ECTA_R23').replace('Revision R22','Revision R23').replace('R22 Technical Supplement','R23 Technical Supplement')
    supp=supp.replace(r'\begin{document}', r'\providecommand{\theHtable}{\arabic{table}}'+'\n'+r'\begin{document}',1)
    supp=supp.replace(r'\begin{document}',r'\input{revisions/2026-09-23-r23/paper/result_macros}'+'\n'+r'\begin{document}',1)
    supp=supp.replace(r'\input{revisions/2026-09-23-r22/paper/supplement}',r'\input{revisions/2026-09-23-r23/paper/supplement}'+'\n'+r'\input{revisions/2026-09-23-r22/paper/supplement}',1)
    supp=supp.replace(r'\clearpage'+'\n'+r'\input{revisions/2026-09-23-r18/paper/references}',r'''\clearpage
\section{Historical R22 exposition, preserved verbatim}
The following exposition retains the original R22 scope and all qualifications; the R23 main text supplies the current findings.
\begingroup\let\oldlabel\label\renewcommand{\label}[1]{\oldlabel{historical-r22-#1}}
\input{revisions/2026-09-23-r22/paper/introduction}
\input{revisions/2026-09-23-r22/paper/conclusion}
\endgroup
\clearpage
\input{revisions/2026-09-23-r18/paper/references}''')
    for version in ['r18','r19','r21']:
        a=r'\input{revisions/2026-09-23-'+version+r'/paper/introduction}'
        b=r'\input{revisions/2026-09-23-'+version+r'/paper/conclusion}'
        supp=supp.replace(a,r'\begingroup\let\historylabel\label\renewcommand{\label}[1]{\historylabel{historical-'+version+r'-#1}}'+'\n'+a)
        supp=supp.replace(b,b+'\n'+r'\endgroup')
    write(ROOT/'SUPP_R23.tex',supp)
    response=start.replace('Revision R23 --- working manuscript','Revision R23 --- referee response')
    response+=r'''\begin{document}
\begin{frontmatter}
\title{Response to the Referee: Neural Bellman Operators}
\runtitle{Neural Bellman Operators: Response}
\begin{aug}
\author[id=au1,addressref={add1}]{\fnms{Qian}~\snm{QI}\ead[label=e1]{qiqian@pku.edu.cn}}
\address[id=add1]{\orgname{Peking University}}
\end{aug}
\begin{abstract}Point-by-point response to the complete R21 Econometrica-level referee report. The revision incorporates the recovered R22 execution, new held-out R23 experiments, new proofs, exact provenance, and the original full-state accuracy objective.\end{abstract}
\end{frontmatter}
\input{revisions/2026-09-23-r23/paper/response}
\end{document}
'''
    write(ROOT/'RESPONSE_R23.tex',response)

def compile_documents():
    logs=REV/'build_logs';logs.mkdir(parents=True,exist_ok=True)
    result={}
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['SOURCE_DATE_EPOCH']='1790112000'
    for name in ['ECTA_R23','SUPP_R23','RESPONSE_R23']:
        for n in range(1,4):
            p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=ROOT,env=env,capture_output=True,text=True)
            write(logs/f'{name}_pass{n}.txt',p.stdout+p.stderr)
            if p.returncode: raise RuntimeError(f'{name} pass {n} failed; see build log')
        log=(ROOT/(name+'.log')).read_text(errors='replace')
        bad=[line for line in log.splitlines() if ('undefined' in line.lower() or 'multiply defined' in line.lower()) and ('Warning' in line or 'There were' in line)]
        assert not bad,(name,bad)
        info=subprocess.check_output(['pdfinfo',str(ROOT/(name+'.pdf'))],text=True)
        over=re.findall(r'Overfull \\hbox \(([^)]*)\)',log)
        assert not over,(name,'Overfull boxes',over)
        result[name]={'pages':int(re.search(r'Pages:\s+(\d+)',info).group(1)), 'sha256':sha(ROOT/(name+'.pdf')),'undefined_or_multiply_defined_warnings':bad,'overfull_hboxes':over}
        (logs/(name+'.log')).write_text(log)
    write(REV/'results/publication_build.json',json.dumps(result,indent=2)+'\n')
    return result

def navigation():
    text='''# Neural Bellman Operators — R23 referee copy

Read `ECTA_R23.pdf`, `SUPP_R23.pdf`, and `RESPONSE_R23.pdf`, in that order. Editable roots use the same names. Current exposition and complete proofs are in `revisions/2026-09-23-r23/paper/`; historical developments remain in their original paths and in the dated appendix/supplement.

Development branch: `revision/econometrica-r23-referee-resolution-2026-09-23`. The final verified publication is separately pinned on `revision/econometrica-r23-referee-copy-2026-09-23`. Main and earlier review/revision branches are not edited.

## Review and execution identities

Latest addressed review: `reviews/2026-09-23-econometrica-r21-final/referee_report.md`, commit `fc16c4fb27b54e11c67ce1983b6830a39038f063`. Inherited R22 head: `9c6faca40fb204494d1e0f53be1468a7ee37341a`.

R22 frozen science: source `9527f219df4fe82d3e9d81fc9ab3ac968613437b`, run 35813098721, artifact 10730632886. Its 360 scientific result files and 21 source identities are preserved. The two earlier publication failures are documented; they are not failed scientific outcomes.

R23 prospective protocol: `f0ab87bec39e4ba96a49bd01ba5608a7de739bed`; scientific execution source `ba2263e6e8e48abf0c25d5c895df8ca38444f1be`; run 35823417685; primary result commit `7384d6bc43774ed91738db1c86ec6f21a1e6504e`.

## New findings

The held-out factorial contains 72 prescribed configurations and all are retained. With matched initial policies, neural–Adam has regional regret below 0.003022, initial-to-final uniform payoff gain above 0.026360, and uniform payoff advantage above 0.003044 against both direct–Adam coordinate systems. Direct L-BFGS-B remains stronger overall. One neural L-BFGS-B regional upper bound is 0.01050307. These are conditional representation findings, not overall neural dominance.

New exact-price, quotient, finite-node interpolation, and re-budgeting theorems have complete proofs. Directed MPFR audits cover all 72 continuous-price brackets and certify an explicit rank-16 feature matrix. Ordinary root/gradient regressions remain diagnostics.

The current-state full-domain bound improves from 7.2783190635 to 7.241462444, but neither full-domain 0.01 accuracy nor separate payoff improvement for that jointly refined actor is established. The original economy, title, full-domain objective, adverse comparisons, and historical technical content are retained.

## Integrity and reproduction

`revisions/2026-09-23-r23/PUBLICATION_MANIFEST.json` records source/result identities, file/PDF hashes, exact historical preservation, and checks. `REPRODUCE.md` gives commands. The old root revision index is archived verbatim. All numerical claims map to theorem, function, result, and arithmetic role in the supplement.
'''
    write(ROOT/'R23_REVIEW.md',text)
    write(ROOT/'REVISION_INDEX.md','# Current review object: R23\n\nSee `R23_REVIEW.md` and the three R23 PDF/TeX roots.\n\nThe previous index is retained byte-for-byte at `revisions/2026-09-23-r23/archive/REVISION_INDEX_before_R23.md`. Earlier manuscripts and scientific results remain at their original paths.\n')
    write(REV/'REPRODUCE.md','''# Reproduce the R23 review object

Run commands from the repository root. Preserve inherited bytecode and limit BLAS threads:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python revisions/2026-09-23-r23/replication/tests.py
python revisions/2026-09-23-r23/replication/run_study.py
python revisions/2026-09-23-r23/replication/continuum_audit.py
BACKEND=mpfr python revisions/2026-09-23-r23/replication/continuous_budget_brackets.py
BACKEND=mpfr python revisions/2026-09-23-r23/replication/interpolation_certificate.py
python revisions/2026-09-23-r23/replication/build_publication.py --compile
```

Fresh training intentionally regenerates current output files and timings; perform it in a separate checkout, not over an immutable referee copy. Exact frozen replay means use the committed primary policies and records instead. The publication workflow builds from those frozen policies without retraining and verifies their hashes.

Primary execution dependencies: Python 3.13.15, NumPy 2.3.5, SciPy 1.17.0, PyTorch 2.10.0+cpu. MPFR checks use the repository's directed interval backend and system MPFR library. PDF compilation uses the bundled `econsocart` class, a TeX Live installation with the imported packages, and `pdflatex`; `pdfinfo` supplies page metadata.

The R22 source/result archive is preserved, not regenerated during R23 publication. The publication builder recovers its paper tables from frozen results without overwriting `results/build.json`. The inherited strict file-preservation assertion is retained. Timings are environment-dependent; mathematical enclosures and all hypotheses remain explicit.
''')

def preservation():
    # Git is used in CI; a recorded immutable blob list supports local archive builds.
    if (ROOT/'.git').exists():
        text=subprocess.check_output(['git','ls-tree','-r',BASE],cwd=ROOT,text=True)
    else:text=(REV/'archive/BASELINE_BLOBS.txt').read_text()
    checked=0;bad=[]
    for line in text.splitlines():
        meta,name=line.split('\t',1);mode,kind,expected=meta.split()
        if kind!='blob':continue
        target=REV/'archive/REVISION_INDEX_before_R23.md' if name=='REVISION_INDEX.md' else ROOT/name
        if not target.exists():bad.append(name+':missing');continue
        data=target.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual!=expected:bad.append(name)
        checked+=1
    assert not bad,bad
    frozen=load(REV/'archive/R22_FROZEN_RESULTS_SHA256.json')
    for name,expected in frozen.items():
        path=R22/name if name.startswith('results/') else R22/'results'/name
        assert sha(path)==expected,(name,'frozen R22 mutation')
    primary_checked=0
    if (ROOT/'.git').exists():
        primary=subprocess.check_output(['git','ls-tree','-r',RESULT,'--','revisions/2026-09-23-r23'],cwd=ROOT,text=True)
        for line in primary.splitlines():
            meta,name=line.split('\t',1);_,kind,expected=meta.split()
            if kind!='blob':continue
            data=(ROOT/name).read_bytes()
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==expected,('primary R23 mutated',name)
            primary_checked+=1
    return {'primary_R23_blobs_preserved':primary_checked,'base_commit':BASE,'checked_inherited_blobs':checked,'unexpected_modified_or_missing_paths':bad,'root_index_archived_byte_identically':True,'frozen_R22_scientific_files':len(frozen)}

def manifest():
    checks=preservation()
    files={}
    for folder in [REV,R22]:
        for p in sorted(folder.rglob('*')):
            if p.is_file() and p.suffix not in ['.pyc'] and p.name not in ['PUBLICATION_MANIFEST.json']:
                files[str(p.relative_to(ROOT))]=sha(p)
    for stem in ['ECTA_R23','SUPP_R23','RESPONSE_R23']:
        for ext in ['.pdf','.tex']:
            p=ROOT/(stem+ext)
            if p.exists():files[p.name]=sha(p)
    for n in ['R23_REVIEW.md','REVISION_INDEX.md']:files[n]=sha(ROOT/n)
    data={'format':'NBO_R23_referee_publication_v1','review_commit':REVIEW,'inherited_head':BASE,
          'protocol_commit':'f0ab87bec39e4ba96a49bd01ba5608a7de739bed','scientific_source_commit':'ba2263e6e8e48abf0c25d5c895df8ca38444f1be','primary_result_commit':RESULT,
          'primary_run_id':35823417685,'publication_source_commit':os.environ.get('GITHUB_SHA','local source archive; exact CI source recorded at publication'),
          'publication_run_id':os.environ.get('GITHUB_RUN_ID'),'preservation':checks,
          'checks':{'primary_study':load(REV/'results/study_summary.json'),'root_tests_status':load(REV/'results/root_tests.json')['status'],'continuous_price_brackets':load(REV/'results/continuous_budget_brackets.json')['status'],'interpolation_certificate':load(REV/'results/interpolation_certificate.json')['status'],'pdf_build':load(REV/'results/publication_build.json')},'sha256':files,
          'publication_commit_rule':'The publication commit is the Git commit containing this manifest; its SHA is not self-embedded. The artifact includes PUBLICATION_COMMIT.txt written after committing.'}
    write(REV/'PUBLICATION_MANIFEST.json',json.dumps(data,indent=2,sort_keys=True)+'\n')
    package=ROOT/'NBO_R23_review_package.zip'
    with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if not p.is_file() or '.git' in p.parts or p==package:continue
            rel=str(p.relative_to(ROOT))
            if p.suffix in ['.aux','.out','.toc','.synctex.gz','.pyc','.ttf','.otf','.woff','.woff2','.pfb','.ttc','.afm'] or rel.endswith('.fdb_latexmk') or rel.endswith('.fls'):continue
            # Include all inherited source and evidence, but not duplicate obsolete PDFs or old transport payloads.
            if p.suffix=='.pdf' and p.name not in ['ECTA_R23.pdf','SUPP_R23.pdf','RESPONSE_R23.pdf']:continue
            if 'source_transport' in p.parts and p.suffix=='.b64':continue
            z.write(p,rel)
    return data

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--compile',action='store_true');args=ap.parse_args()
    recover_r22();tables();documents();navigation()
    if args.compile:compile_documents();m=manifest();print(json.dumps(m['preservation'],indent=2))
if __name__=='__main__':main()
