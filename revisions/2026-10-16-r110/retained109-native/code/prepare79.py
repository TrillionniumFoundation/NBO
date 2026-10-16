"""One-time R79 integration from the pinned ordinary R78 manuscript.
All inherited section and scientific bytes are retained; only wrappers are edited.
"""
from pathlib import Path
import hashlib,json,re,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r78'
BASE='6b88c6b3a61193c98c822bd62af1203df09c992d'
REVIEW='4b27b56f4514f6c1d77b69fe707f7202f8b06b19'
ABSTRACT='''This paper develops Neural Bellman Operators for constructive policy evaluation and feasible improvement. Witness-preserving continuations and qualification-optimal readouts connect attained approximation to the original Bellman optimum. Exact conditional integration and independently implemented whole-bin evaluation qualify the original-law costs of complete controllers. Joint marginal and paired intervals imply sharp controller-choice and deployment-allocation certificates, including installation costs and finite-cohort implementation. In the nonlinear-investment experiment, attained ReLU controllers have lower expected cost than matched Bernstein controllers at both acquisition resolutions. The joint intervals identify the cost ordering and conditional acquisition-fee regions. At an unresolved refinement-fee boundary, allocation reduces worst-case expected loss, subject to an explicit additional-setup threshold. These comparisons concern constructed continuations, not the optional neural query proposals whose adverse complete-work results are retained. Recursive, vector, predictable-qualification and witnessed-reuse results retain their assumptions, proofs and evidence.'''
INTRO=r'''A numerical continuation matters because it helps produce an economic decision. The error of a fitted value, the loss of its implemented policy and the resources required to verify that loss are different objects. A useful method must connect approximation and resource choices to a feasible decision under the original economic law.

This paper develops Neural Bellman Operators (NBOs) along that chain. The constructive implementation evaluates each continuation against its own fitted future and retains feasible action witnesses. Its exact affine--ReLU realization and primitive error budget do not require unrestricted nonconvex training to succeed. A complementary recursive implementation queries the original Bellman problem where action search requires information. A trained proposal can change query locations, but verified endpoint bounds and protected conventional refinement determine validity. These are distinct uses of neural approximation; success of a common certificate is not evidence that every neural component improves complete work.

The investment economy has state-dependent capacity, bilinear transitions and one or two independent continuous innovations. Primitive curvature bounds the transition's convexity defect and supplies regularity of the original Bellman value. Recursive certification can dispense with a stored state lattice, but not with the descendant cost of an original-value query. A strong-convexity upper chord can certify a rounded action before another endpoint query; the method pays for safeguarded refinement whenever the screen fails. A fixed-feature readout has a convex certificate-aware objective and an auditable optimization gap. Neither a neural continuation nor an arbitrary proposal is assumed convex.

The attained continuation provides a separate route to original-law cost evaluation. Its residual oscillations and implemented greedy gaps control both the observation range and original-optimum policy loss. The terminal correction allows an inexact fitted terminal value, and state-independent shifts cancel. For shallow affine--ReLU continuations, conditional expectations under the original one- and two-innovation laws are finite positive-part moment calculations. Explicit state-and-action covers qualify residuals without querying the optimal Bellman tree. Conditional on the actually fitted future, qualification-optimal readouts minimize that verified account; exact primal--dual checks certify the achieved gap rather than relying on solver status. Backward construction then returns the complete acquired controller that is evaluated.

Purchased original-value information can also be reused. A lower Bellman bound and a feasible upper witness are transported only after paying for state displacement, capacity repair and action rounding. Failed checks invoke the original verifier. The finite-cover fill bound states its retention and precision premises explicitly; the executed bounded cache receives only the guarantees its actual contract supports. Predictable qualifications and time-uniform cost intervals separately address when to stop purchasing information. Fixed-controller costs and conditional average costs of changing controllers are not interchanged, and failed numerical evaluations retain their qualified support and paid work.

The evidence distinguishes these constructions. The retained action-readout catalogue compares certificate-aware ReLU and equally sized Bernstein proposals, independent-context validation, sixty-four-block reuse and trained two-control extensions. The recursive-controller cost comparisons meet their declared equivalence margin without identifying strict superiority; adverse cold-start, fitting and reuse outcomes remain visible. Localized witnessed-reuse workloads count first fills and every descendant on a miss. They are not policy-cost observations or a long-horizon neural speed result.

The later original-law experiment evaluates the attained continuation actors themselves. ReLU and Bernstein constructions at each acquisition resolution use nine coefficients, common limits, primitive information and a matched acquisition contract. Their actual fitted futures are propagated backwards. Two estimators of the same complete-policy costs use one frozen simultaneous family: direct cash cost and exact last-innovation conditional integration. The resulting intervals identify lower ReLU-controller costs at both matched resolutions and order the five constructed controllers. This is a positive finite comparison between specified attained fits, not an ordering of all conventional or neural methods.

The economic decision uses those same costs. Sharp difference-constraint bounds retain all paid marginal and paired information when choosing a controller at declared resource prices. Deployment allocation extends the decision when neither acquisition precision is uniformly best after its fee. The controller is selected before state observation, so a share means a mixture of complete feasible policies rather than averaged actions or network coefficients. The new allocation theorem gives an attained linear-programming certificate, exact setup-cost thresholds and an implementable finite-cohort choice. It remains valid for data-dependent prices on the original coverage event. No sample count is relabeled as a deployment horizon, and installation, qualification and processor time are not assigned invented monetary values.

\paragraph{Relation to existing methods.}
Lipschitz extensions and distance transforms underlie the constructive envelope \citep{mcshane1934,felzenszwalb2012}. Approximate and safe policy iteration have established error analyses \citep{munos2003,pirotta2013,scherrer2015}, as does convex dynamic-programming approximation \citep{yang2020convex}. Learned warm starts and optimization-based control supply related numerical methods \citep{sakaue2023warm,sambharya2023,agrawal2020control}. Value-function control variates and telescoping identities are established evaluation tools \citep{munos2006variance,jiang2016}. We connect these ideas to a verified residual-oscillation account for an attained own-future continuation, continuous-law numerical enclosures and the implemented controller's cost.

Time-uniform concentration and off-policy confidence sequences have their own theory \citep{howard2020time,karampatziakis2021}. Our observations are direct original-law contrasts, and the contribution identifies the paid numerical qualification needed to use those concentration tools. Minimax-regret decisions have an established economic role \citep{manski2004}; shortest-path difference constraints are classical \citep{floyd1962}. Our deployment result uses the common attaining cost potentials of the paid interval system to obtain an exact allocation and installation account. It is conditional on qualified costs, not a new unconditional statistical-risk theorem.

\paragraph{Reading path.}
The main article develops construction, recursive and vector certification, qualified continuation fitting, predictable evaluation, actual controller costs and deployment choice. The Technical Supplement contains the core proofs. The Numerical and Development Appendix retains every earlier active section, the sharp pure-choice theorem, complete allocation proofs and all adverse numerical records. Historical companion editions retain controlled diffusions, recursive and endogenous preferences, temporal selves and games under their own hypotheses; the present expected-cost deployment identities do not silently extend to those different objectives.
'''
CONCLUSION=r'''Neural Bellman Operators connect attained continuation approximation to feasible policy decisions under the original economic law. The constructive readout, uniform qualification and direct controller-cost experiment form one chain; optional query prediction and witnessed reuse form distinct work mechanisms. Exact integration removes optimal-value descendants from evaluation of a qualified shallow continuation, while the original fitting, qualification and every failed reuse remain paid operations.

The matched continuation experiment identifies lower ReLU-controller costs at both acquisition resolutions. Its joint intervals also determine the constructed-policy ordering and conditional purchase regions. The deployment theorem extends those observations to sharp expected-regret allocations, additional installation costs and finite cohorts. It does not turn decision-theoretic regret reduction into a newly observed cost gain. Actual monetary conclusions require the stated loss scale, deployment count and resource charges. All historical adverse selector findings and broader economic applications remain available with their own assumptions and evidence.
'''
RESPONSE_ADD='''## R79 addition: attained deployment allocation and explicit setup costs

R79 continues the original R78 manuscript at `6b88c6b3a61193c98c822bd62af1203df09c992d` and the same controlling R67 advisory report. The earlier publication attempt did not complete, so its inherited R77 logs are not used as R79 verification. The present build must execute the entire retained verification chain and compile the actual new ordinary sources.

The new sharp deployment-allocation theorem extends the original controller-choice problem. Nonnegative controller shares and a common attaining cost potential reduce worst-case expected catalogue regret to a finite matrix game. Exact primal and dual feasible probabilities certify the solution and its optimization gap. The new proof distinguishes a pre-observation mixture of entire policies from averaging actions, fitted coefficients or information sets. Installation costs are not presumed linear: an installed-subset formulation charges every supported controller and retains outside controllers as oracle comparators. A finite-cohort construction realizes the allocation in expectation without pretending that the statistical sample size is the deployment horizon.

For the two attained ReLU precision levels, the complete cost intervals imply an exact fee-dependent allocation and the additional cost that would erase its advantage. At the ambiguity midpoint, the worst-case expected-regret certificate is half the best pure certificate before extra setup charges. This is a sharp economic decision calculation from existing qualified costs, not a new simulation, neural speed claim, fee calibration or unconditional statistical-risk result. The corresponding theorem, full proof, rational primal-dual witnesses and finite-cohort exhaustive checks are deposited. Manski (2004) is cited for the established minimax-regret decision perspective.

All R78 active section files remain byte-identical and are compiled once. The pure-choice exposition is placed next to its full proof in the Numerical and Development Appendix; no theorem, proof or unfavorable experiment is deleted. The introduction and conclusion have been rewritten to remove accumulated repetition and distinguish attained continuations from optional query proposals. Their original wrappers and response are preserved. The subsequent ten point-by-point replies remain applicable; the new result further addresses M4/M5/M8/M9 and B3/B4/B7/B9 through explicitly costed deployment rather than unsupported neural timing dominance. The high-dimensional, unknown-law and population-ranking distinctions in those replies remain unchanged.

'''
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
    marker=R/'audit/PREPARATION79.json'
    if marker.exists():print('Ordinary R79 sources already integrated; subsequent edits retained.');return
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for name,content in own.items():
        p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
    saved=R/'preserved/R78-original';saved.mkdir(parents=True,exist_ok=True)
    wrappers={};labels={};sections={}
    for name in ('ECTA.tex','supp.tex','appendix.tex','response.md','README.md'):
        shutil.copy2(OLD/name,saved/name);wrappers[name]=sha(OLD/name)
        if name.endswith('.tex'):
            text=(OLD/name).read_text();labels[name]=re.findall(r'\\label\{([^}]+)\}',text)
            for rel in re.findall(r'\\input\{(sections/[^}]+)\}',text):sections[rel+'.tex']=sha(OLD/(rel+'.tex'))
    shutil.rmtree(R/'build',ignore_errors=True);(R/'build').mkdir()
    p=R/'ECTA.tex';text=p.read_text()
    text=re.sub(r'(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+ABSTRACT+'\n'+m[2],text,count=1,flags=re.S)
    start=text.index(r'\section{Introduction}\label{sec:introduction65}')
    stop=text.index(r'\input{sections/core49}',start)
    text=text[:start]+r'\section{Introduction}\label{sec:introduction65}'+'\n'+INTRO+'\n'+text[stop:]
    text=text.replace(r'\input{sections/choice78}',r'\input{sections/allocation79}',1)
    start=text.index(r'\section{Conclusion}\label{sec:conclusion65}');stop=text.index(r'\bibliographystyle',start)
    text=text[:start]+r'\section{Conclusion}\label{sec:conclusion65}'+'\n'+CONCLUSION+'\n'+text[stop:];p.write_text(text)
    p=R/'appendix.tex';text=p.read_text();needle=r'\input{sections/choice_proof78}'
    if text.count(needle)!=1:raise AssertionError('Inherited choice proof missing')
    text=text.replace(needle,r'\input{sections/choice78}'+'\n'+needle+'\n'+r'\input{sections/allocation_proof79}',1);p.write_text(text)
    p=R/'response.md';text=p.read_text().replace('Revision R78','Revision R79',1)
    loc=text.index('## M1');text=text[:loc]+RESPONSE_ADD+text[loc:];p.write_text(text)
    p=R/'publication/bibliography-entries.json';entries=json.loads(p.read_text())
    entries['manski2004']=r'\bibitem[\protect\citeauthoryear{Manski}{Manski}{2004}]{manski2004}'+'\n'+r'\textsc{Manski, Charles F.} (2004): \enquote{Statistical Treatment Rules for Heterogeneous Populations,} \emph{Econometrica}, 72 (4), 1221--1246.'
    save(p,entries)
    p=R/'references.bib';text=p.read_text()
    if '@article{manski2004' not in text:text+='\n@article{manski2004,\n author={Charles F. Manski},\n title={Statistical Treatment Rules for Heterogeneous Populations},\n journal={Econometrica},\n volume={72},\n number={4},\n pages={1221--1246},\n year={2004},\n doi={10.1111/j.1468-0262.2004.00530.x}\n}\n'
    p.write_text(text)
    evidence={}
    for directory in ('results77','results73','results72','results69','receipts69','logs69','inputs','evidence'):
        for p in (OLD/directory).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:evidence[str(p.relative_to(OLD))]=sha(p)
    for p in OLD.glob('*FREEZE*.json'):evidence[p.name]=sha(p)
    save(marker,dict(base_commit=BASE,review_commit=REVIEW,original_wrappers=wrappers,wrapper_labels=labels,
        active_sections=sections,inherited_evidence=evidence,new_simulation_rows=0,
        added_sections=['sections/allocation79.tex','sections/allocation_proof79.tex']))
    (R/'CONTENT_MAP79.md').write_text('''# R79 content preservation

Every R78 active section remains byte-identical and is compiled exactly once
across ECTA.tex, supp.tex and appendix.tex. The pure-choice section and full
proof are adjacent in the Numerical and Development Appendix. The main article
adds complete-controller allocation, with full proofs and exact installation
and finite-cohort calculations in that appendix. Introduction and conclusion
are edited for a single reading path; original wrappers are in
preserved/R78-original. No inherited theorem, proof or unfavorable experiment
is removed. The original title, author, laws and Bellman optimum are retained.

No new simulation rows, scientific training services or scientific timings
are generated. The full build repeats the inherited exact and numerical
verification and both independent whole-bin cost implementations. The release
report separates the R79 verification from historical R77/R78 reports.
''')
    (R/'README.md').write_text('''# Neural Bellman Operators — R79

[Main article](build/ECTA.pdf) · [Technical Supplement](build/supp.pdf) ·
[Numerical and Development Appendix](build/appendix.pdf) · [Response](build/response.pdf)

This original-paper revision continues pinned R78 and responds to the latest
R67 advisory report. It retains attained continuation fits and their identified
original-law comparisons, and adds sharp deployment allocation with complete
setup-cost and finite-cohort accounts. No old source or scientific branch is
rewritten. CONTENT_MAP79.md identifies preserved and relocated content.

Full reproduction: `python3 revisions/2026-10-12-r79/code/build79.py`.
The entire pinned repository dependency set is needed, not a text-only export.
RELEASE79.json, CLEAN_REBUILD79.json and the hash-bound VISUAL79.json must all
pass before FINAL_DELIVERY79.json and a review-ready branch are issued.
''')
    print(json.dumps(dict(status='assembled',active_sections=len(sections),inherited_evidence_files=len(evidence))))
if __name__=='__main__':main()
