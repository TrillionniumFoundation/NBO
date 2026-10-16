"""Materialize an ordinary R83 manuscript without changing old branches."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-12-r82'
EDITORIAL='766319d4d4c0877c439f10ae433eb608e0b41626'
ABSTRACT='''This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement. Attained continuations retain action witnesses and an original-optimum error account. Representation-calibrated qualification and exact action-switch bounds transfer cost evidence to classes of optimization outputs. We derive an economic stopping frontier over a continuum of verified optimization tolerances, with exact boundary conventions and a finite monotone algorithm. An original-law nonlinear-investment study compares nine complete controllers. Calibrated qualification improves both ReLU and Bernstein constructions while reversing their earlier cost ordering. Independent actionwise integration preserves identified classwide gains at nonzero optimization errors. Conditional replacement, equivalence and deployment decisions follow on the original simultaneous event without new sampling. Recursive-query, vector-control and predictable-evaluation results retain their assumptions and evidence. The comparison concerns specified constructions and qualification rules, not universal neural dominance or unrestricted fitting reliability.'''
INTRO=r'''A continuation approximation matters through the economic decision it produces. Prediction error, original-optimum policy loss and verification work are different objects. This paper connects them through a constructive Neural Bellman Operator (NBO), its attained own-future continuation and the complete feasible controller implemented under the original law.

The operator fits each date against its own attained future and retains feasible action witnesses. Its affine--ReLU construction and primitive error budget do not require unrestricted nonconvex fitting to succeed. A complementary recursive implementation uses verified curvature and protected conventional refinement; trained proposals change optional query locations. Residual qualification permits an attained shallow continuation to replace recursive value queries under a stated error account. Affine calibration separates its represented derivative from a conservative coefficientwise penalty.

Our next question is how much optimization accuracy an economic decision needs. Rational switch barriers identify every acquired action possible throughout a qualification sublevel. Original-law conditional contrasts price those actions, instead of charging the full cost range on each unresolved cell. Exact thresholds determine the entire region of tolerances supporting an ordering, cost-equivalence or replacement conclusion. A verified primal--dual gap places a returned readout in that region without a fitting-success model or additional sample. Labels and the continuation policy remain fixed.

The prospective investment experiment compares both bases, both qualification rules and both observation resolutions. Calibrated qualification improves both ReLU and Bernstein controllers and reverses their earlier matched cost ordering. Independent arithmetic identifies original-law gains; actionwise transfer preserves some comparisons at nonzero optimization errors without identical actions. The full catalogue retains adverse and unresolved cases. Conditional economic choices require separate charges and deployment counts, not an invented conversion of runtime or simulation rows into welfare.

\paragraph{Relation to existing methods.}
The construction draws on Lipschitz extensions and distance transforms \citep{mcshane1934,felzenszwalb2012}. Approximate policy iteration, safe improvement and convex dynamic programming have established analyses \citep{munos2003,pirotta2013,scherrer2015,yang2020convex}; learned warm starts and optimization-based control provide related numerical methods \citep{sakaue2023warm,sambharya2023,agrawal2020control}. A common verifier does not establish the incremental value of its neural proposal.

Control variates, telescoping evaluation and time-uniform concentration are established tools \citep{munos2006variance,jiang2016,howard2020time,karampatziakis2021}, as are minimax-regret decisions and shortest-path difference constraints \citep{manski2004,floyd1962}. The new link is from exact qualification barriers and original-law action effects to economic stopping regions for a constructed continuation, not priority for these underlying principles.

\paragraph{Reading path.}
The article develops construction, accuracy, qualification, optimizer-class transfer and actual costs. Core proofs remain in the Technical Supplement. The Numerical and Development Appendix retains recursive-query, vector-control, reuse and historical evidence unchanged, followed by the new proofs and complete catalogues. Preserved companions retain diffusions, recursive and endogenous preferences, temporal selves and games under their own hypotheses; the expected-cost identities here are not silently extended to those objectives.

'''
CONCLUSION=r'''Neural Bellman Operators connect attained continuation construction to feasible decisions under the original law. Witnesses and residual qualification provide the original-optimum error account; affine calibration identifies a representation-dependent qualification charge. Actionwise cost transfer and exact tolerance frontiers then turn verified optimization accuracy into a sufficient economic stopping condition.

The investment comparison identifies gains from calibrated qualification in both bases and retains the reversal of their earlier ranking. Some cost orderings and equivalence conclusions hold throughout nonzero optimization sublevels without identical actions or new samples. Unresolved coarse classes remain explicit. These conclusions neither assume universal neural superiority nor establish unrestricted fitting reliability.

Conditional purchases and deployment allocations require separately supplied economic scales and charges. Original failed reuse, adverse query timings, vector descendant growth and broader applications retain their records and assumptions. The result is a complete constructive link from an attained approximation to a qualified controller and an economically interpretable accuracy requirement.

'''

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
def main():
    marker=R/'audit/PREPARATION83.json'
    if marker.exists():print('R83 ordinary sources exist; preserving subsequent author edits.');return
    bundle=json.loads((R/'OWN_SOURCE83.json').read_text());own={name:(R/name).read_bytes() for name in bundle}
    for name,h in bundle.items():
        if sha(R/name)!=h:raise AssertionError('Ordinary source mismatch '+name)
    # Abandoned local transport is not an executable or publication input.
    shutil.rmtree(R/'transport',ignore_errors=True)
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for name,raw in own.items():p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    wrappers=('ECTA.tex','supp.tex','appendix.tex','response.md','response.tex','README.md')
    protected={str(p.relative_to(OLD)):sha(p) for p in OLD.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.relative_to(OLD).parts[0] not in ('audit','build','tables') and str(p.relative_to(OLD)) not in wrappers}
    original=R/'preserved/R82-attempt';original.mkdir(parents=True,exist_ok=True)
    for name in wrappers:
        if (OLD/name).exists():shutil.copy2(OLD/name,original/name)
    shutil.copytree(OLD/'audit',R/'preserved/R82-attempt-audit',dirs_exist_ok=True)
    edlocal=os.getenv('NBO_EDITORIAL82_DIR');prefix='revisions/2026-10-12-r82/'
    if edlocal:sources={str(p.relative_to(edlocal)):p.read_bytes() for p in Path(edlocal).rglob('*') if p.is_file()}
    else:
        names=subprocess.check_output(['git','ls-tree','-r','--name-only',EDITORIAL,prefix],text=True).splitlines()
        sources={name[len(prefix):]:subprocess.check_output(['git','show',EDITORIAL+':'+name]) for name in names}
    for name,raw in sources.items():
        p=R/'preserved/R82-editorial'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    for name in ('code/tables82.py','sections/actionwise82.tex','sections/proof82.tex','sections/study82.tex'):
        p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(sources[name])
    p=R/'sections/proof82.tex';text=p.read_text().replace('The execution records both the full clock and peak resident memory.','The completed R83 recovery records its verification clock and peak resident memory separately from the interrupted R82 phase clocks.');p.write_text(text)
    p=R/'sections/study82.tex';text=p.read_text().replace('The work account includes all refinement levels, both arithmetic implementations, rational checks and durable outputs. Replay costs are separately recorded and do not replace that execution clock.','The completed R83 recovery accounts for all refinement levels, both arithmetic implementations and rational checks; its output-accounting boundary is recorded explicitly. Subsequent replay has separate clocks. The interrupted R82 phase clocks are preserved, not replaced or promoted to a missing complete-service clock.');p.write_text(text)
    p=R/'ECTA.tex';text=(OLD/'ECTA.tex').read_text()
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
    start=text.index(r'\section{Introduction}\label{sec:introduction65}')+len(r'\section{Introduction}\label{sec:introduction65}')
    stop=text.index(r'\input{sections/core49}',start);text=text[:start]+'\n'+INTRO+text[stop:]
    text=text.replace(r'\input{sections/calibration81}',r'\input{sections/calibration81}'+'\n'+r'\input{sections/actionwise82}'+'\n'+r'\input{sections/frontier83}',1)
    text=text.replace(r'\input{sections/study81}',r'\input{sections/study81}'+'\n'+r'\input{sections/study83}',1)
    start=text.index(r'\section{Conclusion}\label{sec:conclusion65}')+len(r'\section{Conclusion}\label{sec:conclusion65}')
    stop=text.index(r'\bibliographystyle',start);text=text[:start]+'\n'+CONCLUSION+text[stop:];p.write_text(text)
    p=R/'appendix.tex';text=(OLD/'appendix.tex').read_text()
    text=text.replace(r'\input{preamble}',r'\input{preamble}'+'\n'+r'\usepackage{alphalph}',1)
    text=text.replace(r'\appendix',r'\appendix'+'\n'+r'\renewcommand{\thesection}{\AlphAlph{\value{section}}}',1)
    text=text.replace(r'\bibliographystyle',r'\input{sections/proof82}'+'\n'+r'\input{sections/proof83}'+'\n'+r'\input{sections/study82}'+'\n'+r'\bibliographystyle',1);p.write_text(text)
    (R/'response.md').write_bytes((R/'response83.md').read_bytes())
    shutil.rmtree(R/'build',ignore_errors=True);(R/'build').mkdir()
    keep=json.loads((OLD/'audit/PREPARATION82.json').read_text())
    record=dict(baseline_attempt_commit='e6d2b89f4f113f4b54b5f270359fafdc7bee67c4',complete_paper_commit='c411bfb2badac2981f001f4c84d99c8c3c306c5e',editorial_commit=EDITORIAL,review_commit=keep['review_commit'],
        protected_files=protected,active_sections=keep['active_sections'],original_wrappers={name:sha(original/name) for name in wrappers if (original/name).exists()},
        inherited_failed_log_sha256=sha(R/'audit/build-logs/execute82.log'),wrapper_labels={name:re.findall(r'\\label\{([^}]+)\}',(OLD/name).read_text()) for name in ('ECTA.tex','supp.tex','appendix.tex')})
    write(marker,json.dumps(record,sort_keys=True,indent=2)+'\n')
    write(R/'README.md','''# Neural Bellman Operators — R83

Ordinary submission: ECTA.tex, supp.tex, appendix.tex and response.md.
The original title and all 35 inherited active sections are retained in their
original document. CONTENT_MAP83.md locates the new theorem and evidence.

code/build83.py runs every inherited and new unskipped suite, preservation,
full R77/R80 and actionwise bin replay, exact switch duals and frontiers, and
all four PDFs. code/publish83.py repeats this builder from a clean archive.

The failed R82 attempt and clocks remain unchanged. R83 recovery has its own
execution clock, separate from later replay. No independent cost rows or fit
attempts are added. Labels, terminal actors and the original law remain fixed.

Only audit/FINAL_DELIVERY83.json with separately hash-bound visual qualification
and verified remote refs establishes the completed review-ready package.
''')
    print(json.dumps(dict(status='ordinary_sources_materialized',protected_files=len(protected),inherited_sections=len(keep['active_sections']),abstract_words=len(ABSTRACT.split()))))
if __name__=='__main__':main()
