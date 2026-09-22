# Referee Report — Neural Bellman Operators, latest revision state (second-pass review)

**Venue standard:** Econometrica-level numerical/computational methods  
**Recommendation:** **Reject / editorial return. The purported R13 revision is not a new scientific revision, and the last genuine manuscript state still fails several first-order numerical-method requirements.**  
**Review date:** 2026-09-22  
**Reviewed revision ref:** revision/econometrica-r13-neural-state-verification-2026-09-22  
**Reviewed head:** 442ef9be75e620b53f923cdc476be50edaa64ca7  
**Last genuine scientific manuscript state:** revision/econometrica-r12-uniform-cost-certification-2026-09-22 at 4ff0404833a6d6773bcf7afab361013d732df686  
**Review type:** harsh external numerical-methods review, with repository/version-integrity audit

## 1. Executive assessment

The first task of a referee for a computational paper is to identify the scientific object being reviewed. That audit is decisive here.

The branch named as the latest R13 revision points to commit 442ef9be75e620b53f923cdc476be50edaa64ca7. That commit is not a manuscript revision. Its commit message is:

review(r12): add Econometrica numerical-methods referee report

A direct comparison against the actual R12 manuscript state 4ff0404833a6d6773bcf7afab361013d732df686 shows:

- the purported R13 head is ahead by exactly one commit;
- exactly one file changed;
- that file is reviews/2026-09-22-econometrica-r12/referee_report.md;
- the change consists of adding the prior referee report;
- there are no changes to the manuscript, proofs, numerical code, stored policies, certificates, results, tables, figures, validation records, or response to the referee.

More strongly, the purported R13 revision branch is Git-identical to the previous R12 review branch review/econometrica-r12-numerical-methods-2026-09-22-4ff0404: zero commits ahead, zero commits behind, and zero changed files.

This means the repository currently has no scientific R13 to referee. The branch label says “revision,” but the object is the old R12 manuscript plus its R12 referee report.

That failure is independently serious for a paper whose central message is auditable numerical certification. Version identity is part of the scientific object. A paper cannot simultaneously insist on immutable evidence and then use a review commit as the head of the next revision.

I therefore do not treat the branch name as evidence that a new paper exists. The last genuine scientific manuscript remains R12. I re-audited the principal R12 claims and the preceding referee record to determine whether the substantive blockers have somehow become obsolete. They have not.

R12 contains real progress and a serious validated-control computation. In particular, the central-state primal/dual bounds and the exact cost-parameter envelope are materially stronger than the earlier versions. But the paper still does not establish the numerical method implied by the title. The decisive certificate is built around a small deterministic time-control class, output polishing, exact stopped evaluation, and a model-specific dual; the whole-state neural Bellman certificate is not executed on the flagship problem.

For Econometrica-level numerical methods, the paper therefore fails at two levels:

1. **version-integrity level:** there is no actual R13 revision to review; and
2. **scientific-method level:** the last actual manuscript still does not deliver an end-to-end validated neural Bellman method with a state-space error theory, independent numerical audit, meaningful accuracy-versus-computation frontier, and serious classical baselines on the same problem.

The appropriate editorial action is rejection/return rather than another incremental review round.

---

## 2. P0 version-integrity finding: the latest revision branch contains no scientific revision

### Finding V1 — The purported R13 is the previous R12 review state

The exact comparison is:

- genuine R12 manuscript head: 4ff0404833a6d6773bcf7afab361013d732df686;
- purported R13 head: 442ef9be75e620b53f923cdc476be50edaa64ca7;
- commits added: 1;
- files changed: 1;
- changed file: reviews/2026-09-22-econometrica-r12/referee_report.md;
- additions: 788 lines;
- scientific manuscript/code/result changes: 0.

The purported R13 revision is also identical to the previous R12 review branch.

This is not an editorial nuisance. It prevents a referee from distinguishing author revision from referee input and breaks the repository’s own evidence semantics.

### Required

Before another scientific review round, create a genuine revision commit containing at minimum:

1. a new canonical manuscript source and compiled manuscript;
2. a point-by-point response to the latest referee report;
3. changed theorem/code/result objects corresponding to the claimed repairs;
4. an immutable publication or review receipt that points to the new manuscript source and numerical evidence;
5. a revision index that names the new object unambiguously; and
6. a revision branch whose head is not a review-only commit.

No branch renaming or aliasing is an acceptable substitute.

### Finding V2 — Revision and review roles are currently conflated

The repository has otherwise invested heavily in source/result/build/review identity. That makes the present role confusion more, not less, problematic.

A clean scientific workflow should have the following separation:

author revision commit  
→ immutable scientific target  
→ independent review branch  
→ referee report commit.

Instead, the current latest revision ref is:

R12 scientific target  
→ R12 review report commit  
→ relabeled as R13 revision.

For a computational paper emphasizing auditability, this is a direct contradiction between claimed provenance discipline and actual version control.

### Required

Adopt a branch policy in which review commits can never become heads of revision refs. The next author revision must fork from the last scientific author state and include an explicit response to the latest review.

---

## 3. Central scientific blocker: the flagship certificate is not a certified Neural Bellman solution

### Finding M1 — The strongest numerical result certifies a different algorithmic object from the one advertised

The most important R12 result is the certified regret bound below 0.01 in the original stopped economy, including the continuum cost guarantee over k in [0.5,8].

That result is valuable. But the object being certified is not an end-to-end neural Bellman policy/value pair.

The R12 chain is:

neural or inherited candidate  
→ finite deterministic time-control polishing  
→ exact stopped policy evaluation  
→ model-specific affine-preference market-deflator dual  
→ central-state primal/dual certificate  
→ affine cost-parameter envelope.

Representative stored policy records use 16 deterministic time slabs and explicitly describe L-BFGS-B output polishing with exact differentiable budget projection. The lower-bound certifier evaluates the resulting feasible policy directly. The upper bound is supplied by a specialized dual witness. The validity proof does not require the learned critic to be correct, and it does not establish convergence of the neural training trajectory.

That is a legitimate validated stochastic-control calculation. It is not the same scientific object as a verified Neural Bellman Operator method.

The manuscript itself recognizes part of this by saying that the economic calculation fits an independent polynomial witness and does not claim a whole-state neural critic certificate. That concession is scientifically appropriate, but it makes the title-level methodological claim weaker, not stronger.

### Why this is blocking

For a top numerical-method paper, the method being advertised should be the method whose output is certified.

At present the validity chain would survive if the neural critic were removed and another policy generator supplied the same polished time controls. That means the neural Bellman machinery is not the essential validated object in the flagship theorem.

### Required

Choose one of two coherent papers.

**Route A: genuine Neural Bellman numerical-method paper.**

Certify an actual stored neural actor and critic end to end over a nontrivial time-state region, including:

- Bellman/PDE residual;
- neural derivative bounds;
- policy feasibility;
- global action-improvement error;
- stopping/boundary trace error;
- deployment discretization;
- and final regret.

The final theorem should refer to the actual learned network parameters and their implemented policy.

**Route B: validated stochastic-control paper.**

Reframe the paper around primal/dual validated control. Treat neural training as one optional candidate generator among several. Rename and reorganize the paper so the certified object and advertised object coincide.

The current hybrid framing is not acceptable.

---

## 4. The whole-state neural bridge remains a theorem template rather than an executed method

### Finding M2 — The cover-and-oracle theorem is not executed on the flagship economy

The manuscript contains a useful a posteriori bridge theorem: if cellwise residual control, moduli, global action-oracle error, neural derivative allowances, and stopping-trace errors are all certified, then the policy regret is controlled.

That theorem is not the problem.

The problem is that the paper does not execute the complete chain for the flagship neural policy/value pair.

The manuscript explicitly says that the economic calculation instead uses an independent polynomial witness. The action-oracle machinery is demonstrated at selected states or on a separate structured test family, not assembled into a whole-domain neural certificate for the motivating model.

The paper therefore proves an interface theorem and separately demonstrates some interface components. It does not show that all components close simultaneously for the claimed neural method.

### Required

For one frozen neural actor/critic pair in the original economy:

1. cover a nontrivial time-state domain;
2. certify the residual on every cell;
3. certify network derivatives and interpolation/deployment errors;
4. certify the global action gap on every required cell or by a valid propagation theorem;
5. certify stopped-trace conditions;
6. sum every error contribution;
7. report the final regret bound; and
8. expose the full cellwise certificate in machine-readable form.

Anything less remains a proof architecture rather than an executed numerical method.

---

## 5. The flagship guarantee is pointwise in the initial state

### Finding M3 — Uniformity in the cost parameter does not solve the policy/value function

The strongest economic certificate is attached to the initial state

(t,u,x) = (0,2,1.25).

R12 extends the guarantee uniformly over the scalar cost coefficient k, but not over the economically relevant state variables.

This is a major limitation for a dynamic-programming numerical-method paper.

A numerical solution of a Bellman problem is normally expected to produce information about a policy/value object over a state region. A pointwise initial-value certificate does not establish:

- the quality of the feedback policy from nearby wealth/preferences;
- behavior near the liquidation boundary;
- robustness to different initial conditions;
- a state-dependent error surface;
- or a validated policy function.

It also makes comparison with classical HJB solvers unnecessarily weak, because those methods naturally produce state-space approximations.

### Required

Provide at least one of:

- a certified value/policy enclosure over a nontrivial rectangle;
- a verified finite cover of economically relevant initial states with a uniform regret bound;
- a validated reachable-set certificate along the controlled state distribution with explicit scope;
- or a theorem and executed algorithm for cheaply propagating pointwise certificates across initial states.

A top numerical-method paper should not stop at one scalar initial value unless the scientific question itself is intrinsically scalar. This one is not.

---

## 6. The final continuum certificate is numerically too close to the acceptance boundary

### Finding M4 — The result clears the declared tolerance by only about 5.98e-6

The reported uniform regret upper is:

0.009994024846927508.

The declared target is 0.01, leaving a margin of approximately:

0.000005975153072492.

The exact rational envelope arithmetic is not the concern. Once the node intervals are accepted, exact rational post-processing is a good design choice.

The concern is the upstream numerical enclosure stack feeding those nodes:

- interval arithmetic;
- custom outward binary64 steps;
- Gaussian moments;
- localization bounds;
- supporting planes;
- Taylor boxes;
- clipping logic;
- stopping corrections;
- dual fitting;
- policy evaluation; and
- exported floating-point data.

A six-micro-unit margin is too small to support a top-journal numerical claim when the decisive node bounds are not cross-verified by an independent implementation.

### Required

Do both:

1. obtain a materially larger certificate margin, for example a bound visibly below 0.009 rather than barely below 0.01; and
2. reproduce the decisive primal and dual bounds using a genuinely independent numerical implementation or substantially different validated decomposition.

Also report sensitivity to:

- increased precision;
- finer partitions;
- perturbed primitive bounds;
- alternative interval packages;
- altered witness parameterizations;
- and stronger stopping/localization enclosures.

A threshold should not be passed because of the last few micro-units of one implementation.

---

## 7. Clean-checkout replay is useful, but it is not independent numerical verification

### Finding M5 — Re-executing the same certifier reproduces shared errors by construction

The repository’s clean-checkout replay is valuable. It establishes that the frozen package can be recomputed from a clean state and guards against missing files and accidental drift.

But the replay imports and runs the same certifier implementations used to generate the stored bounds.

Therefore it verifies reproducibility, not numerical independence.

A shared algebraic sign error, interval bug, clipping bug, stopping correction error, or trusted-library misuse will be reproduced exactly.

This matters especially because the final tolerance margin is extremely small.

### Required

Create an independent checker for the decisive claims.

For example:

- a second policy evaluator written independently with a different interval package;
- a second dual verifier using a different decomposition;
- a high-precision implementation that does not reuse the original helper routines;
- or a formally checked kernel for the crucial inequalities.

The publication receipt should distinguish:

same-code reproducibility  
from  
independent numerical cross-verification.

At present that distinction is not strong enough.

---

## 8. There is still no meaningful accuracy-versus-computation frontier for the flagship method

### Finding M6 — The reported refinement frontier is mainly a parameter-cover frontier

The R12 frontier records the number of cost nodes needed to reduce the continuum envelope from roughly 0.024 to roughly 0.009994.

That is useful for the continuation construction.

But it is not an accuracy-versus-computation frontier for the original numerical method.

It does not show, on the unchanged dynamic program, how verified regret falls when one systematically increases:

- neural capacity;
- training work;
- policy class richness;
- number of time slabs;
- state-cover resolution;
- witness richness;
- action-oracle precision;
- interval precision;
- or verification effort.

A numerical-method paper should expose the law connecting computational resources to achieved accuracy.

### Required

For the same original economy and fixed initial/state domain, report a sequence such as:

verified regret about 1e-1  
→ 5e-2  
→ 2e-2  
→ 1e-2  
→ 5e-3  
→ 2e-3,

together with total computational cost and the exact resource change at each stage.

This should be an end-to-end frontier, not a post hoc count of successful continuation nodes.

---

## 9. The computational cost ledger is incomplete

### Finding M7 — “Successful task-seconds” are not the cost of the method

The reported timing explicitly excludes some inherited computation, interrupted attempts, training, witness construction, setup, and overlapping work.

That may be reasonable for engineering bookkeeping. It is not adequate for scientific method comparison.

If the paper claims a constructive numerical method, the reader needs the total resource cost of obtaining the certified answer from a clean start.

### Required

Report:

- wall-clock from clean checkout to final certificate;
- CPU seconds;
- GPU seconds;
- hardware model;
- number of cores;
- memory;
- training time;
- polishing time;
- dual/witness construction time;
- rigorous verification time;
- failed/refined attempts;
- continuation refinement;
- and independent cross-check time.

Separate generation cost from verification cost.

Only after this exists can computational efficiency be discussed.

---

## 10. Strong classical baselines are still missing on the same low-dimensional flagship problem

### Finding M8 — The main application is two-dimensional, but the paper does not benchmark serious classical solvers on that same problem

The original economic state is low-dimensional. That is exactly where strong classical numerical methods should be competitive and auditable.

Relevant baselines include:

- monotone finite-difference HJB schemes;
- semi-Lagrangian methods;
- controlled Markov-chain approximation;
- adaptive sparse grids;
- direct policy iteration;
- pseudospectral or collocation methods where appropriate;
- and primal/dual verification methods.

The current paper contains comparisons to neural methods and separate synthetic/reference problems, but it does not establish what the neural Bellman machinery buys on the one problem where a rigorous economic certificate is claimed.

### Required

Run at least two serious non-neural methods on the unchanged original economy and compare:

- value accuracy;
- policy quality;
- state-space resolution;
- behavior near first exit;
- wall-clock;
- memory;
- certificate availability;
- and ability to reproduce the welfare comparisons.

If a classical method is faster or more accurate in two dimensions, say so. That result would improve the paper by clarifying where the proposed method is and is not useful.

---

## 11. The reference-solvable accuracy suite validates a different algorithmic object

### Finding M9 — Structured linear-gain tests do not validate the same neural architecture used in the claimed method

The reference-solvable suite is scientifically useful. Exact references are exactly what a numerical-method paper should use.

However, the suite relies on a structured actor/output representation with known Riccati structure and a different optimization object from the more general neural actor/critic pipeline.

Therefore a small error in those tests does not imply that the advertised general neural Bellman implementation has the same accuracy behavior.

### Required

Repeat the exact-solution benchmark using the same architecture and training/verification pipeline as the main method.

Vary:

- network width and depth;
- training budget;
- time mesh;
- state-cover mesh;
- action-oracle tolerance;
- and verification precision.

Measure true regret against the known exact solution.

This is the most direct way to establish that the actual NBO implementation is a numerical method rather than a collection of separately successful components.

---

## 12. The 128-dimensional action result is structurally special and should not be used as evidence of high-dimensional dynamic-programming scalability

### Finding M10 — The global action search is high-dimensional only in a restricted rank-one-coupled sense

The action-certificate experiment is clever: the nonconvex coupling is mediated through a scalar aggregate, allowing a one-dimensional global partition together with strongly convex subproblems.

That is a useful structured global-optimization result.

It is not evidence that the Bellman solver itself handles 128-dimensional state-space stochastic control.

The distinction between action dimension and state dimension is fundamental.

### Required

Describe the result as a high-dimensional action-oracle certificate for a structured rank-one-coupled Hamiltonian.

Do not use it to imply full high-dimensional dynamic-control scalability unless the paper actually solves and certifies a high-dimensional stochastic-control problem end to end.

---

## 13. The continuum-k theorem is specialized affine-parameter continuation, not a general continuation theory

### Finding M11 — The extension works because fixed-policy payoffs are affine in k and the policy set is unchanged

The continuum result exploits the special structure

J_k(pi) = A(pi) - k B(pi),

with a common admissible policy set.

This makes the optimal value a supremum of affine functions and permits convex-chord upper bounds plus transferred policy lower bounds.

That is a clean and useful argument.

But it should not be presented as a general parameter-continuation theory for neural Bellman problems.

It does not automatically cover parameters that change:

- dynamics;
- diffusion;
- action constraints;
- state constraints;
- stopping boundaries;
- discounting;
- transition kernels;
- or preferences non-affinely.

### Required

Either narrow the claim explicitly to affine objective parameters with a common policy set, or prove a broader transport/modulus result and execute it on at least one non-affine parameter.

The present theorem is a specialized validated-envelope construction.

---

## 14. Uniform policy regret does not imply uniformly informative comparative statics

### Finding M12 — A 0.01 absolute-regret certificate may be too wide to resolve nearby welfare differences

The paper’s uniform policy certificate is useful for deployment: for each k in the interval, one can select a policy with a bounded absolute regret.

That does not mean all local welfare comparisons in k are numerically resolved.

For nearby prices p and q, the true difference V(p)-V(q) can be much smaller than the absolute error scale.

Therefore the paper should distinguish:

policy near-optimality  
from  
comparative-static identification.

### Required

Provide a continuum map of where the value differences are actually resolved.

For example:

- certified secant intervals;
- slope/budget intervals;
- minimum price separation needed for sign resolution;
- regions where only monotonicity is known;
- and regions where effect magnitudes are tightly identified.

Do not let “uniform in k” be read as “uniformly precise comparative statics.”

---

## 15. The novelty boundary remains too diffuse for an Econometrica numerical-method paper

### Finding M13 — The paper contains many useful pieces but no single executed general method theorem

The manuscript currently combines:

- stopped stochastic-control verification;
- neural policy iteration language;
- polynomial or other independent witnesses;
- a model-specific market-deflator dual;
- cost-parameter continuation;
- structured high-dimensional action certification;
- external neural comparisons;
- method-specific tuning studies;
- reference-solvable control problems;
- economic welfare decompositions;
- and preservation of earlier recursive-utility/game material.

Several of these are individually interesting.

But the reader should be able to answer four questions quickly:

1. What is the new numerical method?
2. What theorem proves its error control?
3. What implementation executes that theorem end to end?
4. What economic result genuinely requires that method?

At present the answers point to different sections and sometimes to different algorithmic objects.

### Required

Rebuild the paper around one center of gravity.

A credible structure would be:

1. one general validated-control theorem;
2. one concrete end-to-end algorithm satisfying the theorem;
3. one exact/reference benchmark using the same implementation;
4. one flagship economic application;
5. two serious classical baselines on that application;
6. one full accuracy-versus-computation frontier;
7. one concise reproducibility appendix.

The rest belongs in separate papers or repository history.

---

## 16. Historical preservation has become a manuscript-design anti-pattern

### Finding M14 — Git history should preserve old versions; the journal paper should not be forced to preserve old prose

The project’s provenance discipline is commendable. But manuscript preservation has become entangled with scientific presentation.

Earlier revision tooling checks that inherited text survives, and supplements reproduce large quantities of historical material.

That is the wrong abstraction for a journal paper.

A final revision must be free to:

- delete obsolete claims;
- combine duplicated arguments;
- rewrite notation;
- remove dead experimental branches;
- shorten historical exposition;
- and reorganize the paper around the final contribution.

Git already preserves the old versions.

### Required

Remove any validation rule requiring all earlier prose to survive.

Keep history in the repository. Write the submitted paper as a clean final scientific document.

The supplement should contain only material needed to verify the final claims.

---

## 17. The paper still lacks a robust interpretation of the 0.01 tolerance

### Finding M15 — The target is treated too much like an engineering threshold

R12 now meets the declared 0.01 threshold, but the numerical meaning of 0.01 should be tied to economic scales.

A tolerance is scientifically persuasive when the reader can see what decision would change if the error were 0.02 rather than 0.005.

### Required

Calibrate the error target against:

- welfare effect sizes;
- policy differences;
- consumption-equivalent variation if meaningful;
- adjustment-cost comparisons;
- or other economically interpretable scales.

Then report whether the certificate is sufficiently smaller than the effect being discussed.

A numerical theorem should support an economic decision, not merely pass a round number.

---

## 18. Repository audit: the current “latest revision” also lacks the expected R13 deliverables

At the reviewed head I find the R12 paper and R12 supplement as the current scientific artifacts. The revision index still identifies R12 as the current scientific revision. The R13 ref does not introduce a new ECTA_R13 manuscript, new supplement, new response-to-referee package, new R13 results directory, or new R13 publication receipt.

This is consistent with the Git comparison: no scientific R13 was committed.

### Required

The next revision should have a single, self-consistent identity across:

- branch/ref;
- commit message;
- manuscript title/version;
- revision index;
- response to referee;
- result directory;
- publication receipt;
- compiled PDF hashes;
- and review target.

The referee should not have to infer which one of those is authoritative.

---

## 19. Minimum conditions for a credible next submission

I would not recommend another full referee round until all P0 items below are satisfied.

### P0 — Produce an actual author revision

The next revision must contain scientific changes, not a review report relabeled as a revision.

### P0 — Decide the paper’s identity

Either certify the actual neural Bellman actor/critic end to end, or reframe the contribution as validated stochastic control with neural policy generation as optional.

### P0 — Execute a state-space certificate

Move beyond one central initial state. Certify a policy/value object on a nontrivial state region or a clearly justified reachable set.

### P0 — Obtain independent numerical cross-verification

Recompute decisive primal and dual bounds with a second implementation or materially different validated decomposition.

### P0 — Increase the numerical safety margin

Do not rely on a 5.98e-6 margin below the acceptance threshold.

### P0 — Produce an accuracy-versus-computation frontier

For the unchanged flagship problem, show verified error decreasing as total method resources increase.

### P0 — Run strong classical baselines

At least two serious non-neural solvers should be evaluated on the same original economy.

### P1 — Validate the actual neural architecture on exact-reference problems

Use the same actor/critic architecture and training/verification stack as the claimed method.

### P1 — Report full computational costs

Clean-start wall-clock, CPU/GPU, memory, failed attempts, generation, and verification.

### P1 — Narrow structural claims

Present the k-continuation result and 128-dimensional action oracle with their exact structural scope.

### P1 — Rewrite the paper cleanly

Stop using manuscript preservation as a scientific formatting constraint.

---

## 20. Recommendation

**Reject / editorial return in the present state.**

The immediate reason is not subtle: the purported latest R13 revision is not a scientific revision. It is the previous R12 review state under a revision branch name.

Even if I ignore that problem and assess the last genuine manuscript, the paper is still not ready as an Econometrica-level numerical-method contribution.

The strongest scientific chain currently established is:

candidate policy  
→ low-dimensional deterministic time-control polishing  
→ rigorous stopped policy evaluation  
→ specialized primal/dual verification  
→ pointwise central-state regret bound  
→ affine cost-parameter continuation.

That chain is potentially publishable as validated computational stochastic control.

The chain implied by the current title would need to be:

neural Bellman training  
→ frozen neural state-feedback actor/critic  
→ whole-domain residual/jet/action/boundary certificate  
→ state-space regret guarantee  
→ controlled accuracy-versus-computation frontier  
→ competitive comparison against serious alternatives.

The paper has not yet closed that chain.

The next submission should not add more partially independent components. It should close one coherent chain completely.

---

## 21. Evidence audited for this second-pass report

### Version identity

- revision/econometrica-r13-neural-state-verification-2026-09-22
- revision/econometrica-r13-whole-state-neural-certificates-2026-09-22
- head 442ef9be75e620b53f923cdc476be50edaa64ca7
- revision/econometrica-r12-uniform-cost-certification-2026-09-22
- scientific head 4ff0404833a6d6773bcf7afab361013d732df686
- review/econometrica-r12-numerical-methods-2026-09-22-4ff0404

### Exact comparison

R12 scientific head → purported R13 head:

- ahead by one commit;
- one changed file;
- the only file is reviews/2026-09-22-econometrica-r12/referee_report.md;
- no scientific file changes.

Previous R12 review branch → purported R13 revision branch:

- identical;
- zero commits ahead;
- zero commits behind;
- zero changed files.

### Manuscript/revision material

- ECTA_R12.tex
- SUPP_R12.tex
- R12_REVIEW.md
- REVISION_INDEX.md
- revisions/2026-09-22-r12/response_to_referee.md
- revisions/2026-09-22-r12/paper/main.tex
- revisions/2026-09-22-r12/paper/continuation.tex
- revisions/2026-09-22-r12/paper/continuation_proof.tex

### Numerical evidence and code

- revisions/2026-09-22-r12/results/envelope.json
- revisions/2026-09-22-r12/results/frontier.json
- revisions/2026-09-22-r12/results/refinement_history.json
- revisions/2026-09-22-r12/replication/cost_case.py
- revisions/2026-09-22-r12/replication/price_envelope.py
- revisions/2026-09-22-r12/replication/recheck.py
- revisions/2026-09-22-r12/publication_receipt.json
- revisions/2026-09-22-r12/ci_results/status.json
- revisions/2026-09-22-r12/validation_report.json

### Prior referee baseline

- R12 numerical-methods referee report at commit 442ef9be75e620b53f923cdc476be50edaa64ca7
- prior R13 review branch state at 857bfeab28ca1b7a7f732edf180126f3ded6b451

This report deliberately treats immutable scientific content, not branch names, as the review target.
