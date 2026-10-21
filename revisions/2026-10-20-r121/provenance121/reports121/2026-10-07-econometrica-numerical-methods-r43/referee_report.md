# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r43-referee-revision-2026-10-07`  
**Pinned revision commit:** `3c9ad7a969bddf3c79ec5dc07e4b74704fed8615`  
**Pinned revision tree:** `4d08baa453265bdaad20d7c0a79033f76c4b9f34`  
**Pinned R43 protocol:** `revisions/2026-10-07-r43/STUDY_PROTOCOL.md`, Git blob `99eb924c7fbe2d2a2131decf5ac37da7cc9fc5b3`  
**Inherited authoritative paper:** R41, commit `06a104a8db06b76464165899d817b303cb2aaa01`  
**Report date:** 7 October 2026  
**Recommendation:** **Return without substantive review; equivalently, reject in the present incomplete form. The pinned R43 object is not an atomic, reconstructible paper revision. A complete immutable R43 submission may be reviewed afresh, but the current branch should not be treated as a submitted manuscript.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

The branch presented as the latest R43 referee revision is not a complete paper revision. At the pinned head, the root `README.md` still identifies R41 as the current paper. The root `ECTA.tex` and `supp.tex` still import the R41 article and supplement. The R43 directory contains one protocol and a publication directory containing only `source-00.b64`, `source-01.b64`, and `source-02.b64`. The commit sequence explicitly labels these uploads “(1/5),” “(2/5),” and “(3/5).” The remaining two source parts are absent.

There is no materialized R43 main article, technical supplement, referee response, generated table set, result directory, audit directory, build directory, compiled PDF, release manifest, or completed R43 workflow run in the pinned snapshot. The compressed source capsule cannot be reconstructed from three of five parts. A referee therefore cannot determine what manuscript claims are actually made, whether the intended diagnostic calculations were executed, whether the direct neural-versus-ridge comparisons produced valid intervals, whether adverse outcomes were retained, whether the sources compile, or whether the visible prose agrees with the numerical record.

This is not a cosmetic repository issue. The intended R43 protocol responds to substantive R42 concerns. It proposes post-review diagnostic continuation for seven objects that missed tighter targets and a direct paired policy-cost comparison for six coupled neural/ridge pairs. Those additions could materially change the manuscript’s discussion. They must therefore be bound to one immutable article, response, evidence package, and audit before external review.

The protocol itself contains several commendable design choices. It freezes the seven diagnostic objects, prohibits retraining or changes to primitives, preserves the original R42 success counts, labels the additional verification as post-review rather than independently preregistered, defines a direct policy-cost estimand rather than subtracting separate regret bounds, couples innovations across methods, uses outward arithmetic for continuous innovations, allocates familywise error, and explicitly forbids interpreting interval overlap as equivalence or superiority. These are appropriate responses to the prior report.

A protocol and three partial source chunks, however, are not a revision. I therefore do not issue a substantive merits recommendation on the unseen intended R43 manuscript. The correct journal-level disposition is to return the submission as incomplete. The earlier R42 findings remain the last assessable scientific record until a complete R43 snapshot is published.

## 2. Positive features of the frozen R43 protocol

### 2.1 The diagnostic continuation preserves the original experiment

The protocol identifies exactly seven previously unsuccessful neural objects: six scalar services and one coupled service. It freezes their existing own-future network weights and allows only one additional verification resolution per object. It forbids retraining, changes to economic primitives, seeds, targets, or verification formulas. It also states that the original R42 success counts remain unchanged regardless of the diagnostic outcomes.

This is the correct way to investigate whether a certificate failure is driven by verification resolution without rewriting the original performance record.

### 2.2 The protocol correctly labels the diagnostic as post-review

The additional checks were selected after inspecting the R42 allowance decomposition. The protocol does not relabel them as confirmatory preregistered evidence. It requires their local verification work, storage, and clocks to be reported separately and prohibits adding clocks measured on different hosts to manufacture an end-to-end comparison.

That evidentiary distinction is important and should be preserved verbatim in any final article.

### 2.3 The coupled comparison targets the actual method contrast

The planned primary estimand is

\[
J(\pi^{\mathrm{neural}})-J(\pi^{\mathrm{ridge}}),
\]

in the original continuous-uniform-innovation economy. This directly addresses the R42 objection that separate regret upper bounds do not identify the sign of the policy-cost difference.

The design uses all six original method pairs at their first common 0.25 crossing and all four previously declared states, yielding twenty-four method-state comparisons. Identical innovations are used for both policies. This is the right paired object.

### 2.4 Numerical and statistical error sources are at least recognized

The protocol proposes 65,536 path-model draws per comparison, continuous innovations coupled to 40-bit bins, outward interval arithmetic for within-bin uncertainty, network evaluation, transitions, costs, and cell-selection ambiguity, and simultaneous one-sided empirical Bernstein bounds over forty-eight tails.

It also distinguishes iid model sampling from the deterministic fact that a stored pseudorandom stream is not itself a mathematical proof of independence. This is careful language.

### 2.5 The intended release plan is appropriately comprehensive

The protocol calls for one main article, a new proof supplement, retained theory/evidence and application companions, point-by-point responses, generated tables, executable sources, raw outcomes, and hashes. It explicitly preserves the earlier text and adverse results rather than deleting them to produce a favorable narrative.

If actually implemented in one source-bound snapshot, this would resolve the threshold publication problem identified in the R42 report.

## 3. Blocking concerns

### B1. The source capsule is incomplete and unreconstructible

The current publication directory contains only three of five declared chunks. The branch history ends at `revision(r43): publish tested manuscript and science source capsule (3/5)`. There is no `source-03.b64` or `source-04.b64`, no capsule manifest, no total archive digest, and no restore program in the R43 tree.

The phrase “publish tested manuscript” in the commit message is therefore not supported by the repository object actually available to a referee. The submitted source cannot be reconstructed, much less tested independently.

### B2. The authoritative manuscript remains R41

The root `ECTA.tex` imports `revisions/2026-10-07-r41/ECTA.tex`. The root `supp.tex` imports the R41 supplement. The root README is headed “Neural Bellman Operators — R41” and directs readers to the R41 paper, response, study, and audits.

Thus R43 does not replace or update the authoritative submitted paper. A reader following the repository’s own entry points sees none of the R43 protocol, diagnostics, paired comparisons, new tables, or changed limitations.

### B3. No R43 article, supplement, response, tables, or PDFs exist in the pinned tree

The directory `revisions/2026-10-07-r43/` contains only `STUDY_PROTOCOL.md` and `publication/`. There is no `ECTA.tex`, `supp.tex`, `response.md`, `results/`, `audit/`, or `build/` directory. No R43 compilation record or PDF is available.

This makes ordinary referee tasks impossible: checking theorem statements against proofs, checking prose against tables, checking citations and notation, assessing presentation, and determining whether the point-by-point response accurately represents the revision.

### B4. There is no executed R43 evidence package or publication gate

At the pinned head there are no workflow runs on the R43 branch. No raw diagnostic outcomes, paired path records, interval endpoints, familywise-error ledger, generated tables, source hashes, or release audit are committed or attached as an identified workflow artifact.

The protocol specifies what should be run. It does not establish that the computation was run, completed without failure, or produced the claims that the intended manuscript may make.

### B5. The submission is non-atomic and potentially mutable during review

The branch was published through a sequence of partial commits and stopped at part three of five. A referee report pinned to this head would concern a different object from any later completion of the same branch. The missing parts could change the manuscript, code, results, or response without changing the branch name.

A journal submission must be an atomic snapshot: one final commit with a complete source tree and evidence identities. Partial source uploads should occur on a staging branch, not on the branch presented for referee review.

### B6. The post-review diagnostics cannot revise the primary R42 success record

The protocol correctly says that R42 success counts remain 6/12 at the scalar 0.04 target and 5/6 at the coupled 0.10 target. Any finer-grid diagnostic can explain a certificate failure or show that a frozen candidate passes under more expensive verification. It cannot retroactively turn the original capped service into a success.

The final paper must maintain three separate quantities:

1. original capped-service attainment;
2. post-review diagnostic attainment of the same frozen object under additional verification work; and
3. any newly designed prospective method service.

Combining them would invalidate the work-to-target comparison.

### B7. The proposed paired simulation requires a complete theorem and implementation audit

The direct coupled comparison is promising, but the protocol alone does not settle several technical points:

- the exact paired Bellman-residual telescoping identity and its sign convention;
- the bounded range used in each empirical Bernstein inequality;
- how interval-valued path endpoints interact with sampling uncertainty;
- how state-cell ambiguity is propagated without introducing method-dependent bias;
- whether the same fixed policies and initial states are used for all tails in the simultaneous family;
- how terminal and numerical execution allowances enter the direct difference;
- how failed or ambiguous path evaluations are retained;
- why forty-eight tails is the complete multiplicity count; and
- whether the reported bounds concern the stochastic model or only the fixed pseudorandom stream.

These issues may be handled correctly in the missing source and proofs, but they cannot be assessed from the current tree.

### B8. Twenty-four state comparisons do not establish method-level reliability

The planned direct comparison uses six already selected neural/ridge pairs and four declared states. It can rank those frozen policies at those states under the stated stochastic model. It does not estimate a probability of neural superiority over training randomness, a median work-to-target frontier, or performance over a broad economic task distribution.

The final paper must not move from direct finite-object comparisons to claims about “the method” without an explicit training-randomness or task-level estimand.

### B9. Finer verification is not a nonlinear scaling result

The diagnostic resolutions—scalar `N=4096, A=2048` and coupled `N=256`—increase the cost of certifying seven frozen objects. They may reveal whether a bound is cover-limited. They do not demonstrate that the training-to-certificate method scales in state dimension, action dimension, horizon, innovation complexity, or target accuracy.

The R42 objections concerning one- and two-dimensional tensor-cover constructions therefore remain unresolved unless the missing R43 manuscript supplies genuinely new scaling evidence.

### B10. The visible R43 record does not resolve the substantive R42 findings

The last reviewable evidence showed that:

- the spline attained both scalar targets in all services and produced tighter global bounds in every matched scalar object;
- signed scalar policy-cost intervals never favored neural and often favored spline;
- the flexible ridge comparator was more reliable and usually faster in the coupled study;
- no direct coupled neural-minus-ridge policy interval had been reported;
- adaptive precision supplied no recorded work advantage; and
- the broad manuscript scope exceeded the completed nonlinear result.

The R43 protocol directly addresses only the missing coupled policy contrast and the diagnostic decomposition of seven failures. Even successful outcomes would not by themselves establish nonlinear scaling, optimizer reliability, adaptive-precision efficiency, or a substantive economic result uniquely enabled by NBO.

## 4. Major comments and required changes

### M1. Publish one immutable R43 review-ready commit

Do not submit a staging branch. The final branch should have one clearly identified head containing every source file, result, audit, and response needed for review. The branch name should not be reused for later mutation.

### M2. Materialize the source tree

Base64 capsules may be retained as provenance artifacts, but they should not be the sole publication form. Commit the actual UTF-8 manuscript, supplement, response, tables, code, protocols, and audit files. If a capsule is necessary, provide:

- all ordered parts;
- the expected count;
- per-part hashes;
- a total concatenated hash;
- an archive hash;
- a deterministic restore program;
- path-traversal and duplicate-path checks; and
- a manifest of restored file hashes.

### M3. Update all authoritative entry points

The root README, `ECTA.tex`, `supp.tex`, and any response entry point must refer to R43. The article should identify the exact evidence commit and explain which R42 findings remain unchanged.

### M4. Commit the executed diagnostics and preserve their post-review status

For each of the seven frozen objects, report the original allowance decomposition, the additional resolution, whether the certificate passes, incremental operations, storage, local clock, and final bound. Keep original R42 attainment counts unchanged and present the new rows in a separately labeled diagnostic table.

### M5. Commit raw direct-comparison records

For every one of the twenty-four neural/ridge/state comparisons, retain:

- both policy identities;
- target-crossing identities;
- initial state;
- seed;
- sample count;
- path endpoint sums and squared sums or equivalent sufficient statistics;
- interval range bounds;
- numerical and cell-ambiguity allowances;
- lower and upper simultaneous endpoints;
- all failures or ambiguous paths; and
- a hash-bound record of the exact code and environment.

The generated table should be reproducible from these records by a small deterministic script.

### M6. Prove the direct-difference certificate in the supplement

State the paired performance-difference identity, numerical enclosure, concentration result, multiplicity allocation, and precise comparison class. Clarify whether the result is conditional on frozen policies and whether it applies to all adapted controls, a stated initial-state set, or only the direct policy contrast.

### M7. Keep work accounts nonadditive across environments

The protocol correctly forbids adding clocks measured on different hosts. The final paper should report original training-service clocks, new diagnostic verification clocks, and new simulation-comparison clocks in separate columns. Machine-independent operation counts should accompany all of them.

### M8. Preserve every adverse R42 result

Do not allow a successful high-resolution diagnostic to conceal original capped failures. Do not infer equivalence from interval overlap. Do not omit spline/ridge comparisons, mixed-precision failures, or services in which conventional methods are faster or sharper.

### M9. Address the remaining method-level questions explicitly

Even after the planned R43 additions, the paper needs a clear statement about what it does and does not establish regarding:

- training reliability;
- work to a certified target;
- nonlinear dimensional scaling;
- adaptive precision;
- superiority over flexible conventional approximation; and
- economic discovery unique to the neural method.

These cannot be resolved by presentation changes alone.

### M10. Reduce the active submission to the completed contribution

A focused paper on from-primitives neural Bellman training, direct all-state certification, and paired policy comparison in compact nonlinear control could be reviewable. The historical platform of controlled diffusions, recursive preferences, temporal selves, games, quadratic construction, and many earlier experiments should not remain coequal main-paper claims unless each receives the new construction and evidence standard.

## 5. Minimum contents of a reviewable R43 submission

A complete resubmission should contain, at one pinned commit:

1. an authoritative main article;
2. a proof supplement;
3. a point-by-point response to the R42 report;
4. complete R42 and R43 evidence tables;
5. raw R43 diagnostic and paired-comparison records;
6. executable aggregation and audit scripts;
7. a source/evidence manifest with hashes;
8. compilation logs and PDFs;
9. an explicit preservation map for all inherited adverse evidence; and
10. a release audit verifying that the article’s numerical statements match the committed records.

Only after these items exist can a referee assess whether R43 substantively answers the prior report.

## 6. Independent repository checks performed for this report

I performed the following checks against the pinned R43 head.

1. **Branch identity.** The branch head is `3c9ad7a969bddf3c79ec5dc07e4b74704fed8615`, with tree `4d08baa453265bdaad20d7c0a79033f76c4b9f34`.
2. **Commit sequence.** The three source-upload commits are explicitly labeled `(1/5)`, `(2/5)`, and `(3/5)`.
3. **Root article entry point.** `ECTA.tex` contains only `\input{revisions/2026-10-07-r41/ECTA.tex}`.
4. **Root supplement entry point.** `supp.tex` contains only `\input{revisions/2026-10-07-r41/supp.tex}`.
5. **Root README.** The README continues to identify R41 as the current revision.
6. **R43 directory.** It contains only `STUDY_PROTOCOL.md` and `publication/`.
7. **Publication directory.** It contains exactly `source-00.b64`, `source-01.b64`, and `source-02.b64`, each recorded as 12,000 bytes. Parts 03 and 04 are absent.
8. **Missing manuscript files.** `revisions/2026-10-07-r43/ECTA.tex` and `revisions/2026-10-07-r43/response.md` return `404 Not Found`.
9. **Workflow state.** The branch has no recorded workflow run at the pinned snapshot.
10. **Protocol review.** I read the complete R43 protocol and verified that it preserves R42 success counts, labels diagnostics as post-review, defines twenty-four direct coupled comparisons, and prohibits equivalence or superiority claims from interval overlap.

Because two source parts and every materialized R43 paper/evidence file are absent, I did not and could not reconstruct or execute the intended R43 release. The review directory includes a replay script for the repository-state checks and a machine-readable record of the observed snapshot.

## 7. Recommendation

The frozen R43 protocol is thoughtful and directly responsive to two important R42 objections. It could support a useful revision if fully executed and transparently integrated.

The pinned repository object, however, is not that revision. It is an incomplete staging snapshot containing a protocol and three of five compressed source parts while all authoritative paper entry points remain on R41. There are no reviewable R43 claims, proofs, results, tables, audits, or PDFs.

I therefore recommend **return without substantive review, or rejection in the present incomplete form**. This recommendation is procedural and evidentiary, not a judgment that the unseen intended R43 mathematics or computations are incorrect. A complete, immutable R43 submission should be reviewed as a new object after its source, evidence, response, and publication gate are all present.