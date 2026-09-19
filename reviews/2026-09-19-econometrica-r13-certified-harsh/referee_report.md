# Referee Report — Neural Bellman Operators, R13 Certified Response

**Journal standard used:** Econometrica-style external assessment. This is an owner-commissioned advisory report, not an editorial decision and not a representation of appointment by Econometrica.

**Date:** 19 September 2026

**Repository:** TrillionniumFoundation/NBO

**Reviewed revision branch:** revision/econometrica-r13-certified-response-2026-09-19

**Frozen reviewed SHA:** dd9e0c755b743efdea2a7637f7620bb8ebc3b3c6

**Immediate prior harsh report:** reviews/2026-09-18-econometrica-r12-independent-harsh-rereview/referee_report.md

**This review branch:** review/econometrica-r13-certified-harsh-2026-09-19-dd9e0c7

## Recommendation

**Reject in the present form. Do not treat R13 as a review-complete Econometrica revision.**

R13 makes genuine and technically important progress. In particular, it repairs the two most concrete source-level defects identified in the independent R12 harsh re-review: the floating-point allowance is now subjected to a separately coded, data-dependent arithmetic derivation rather than merely imported as a trusted constant, and the positive financial mandate is now treated as an open class for attained lower witnesses rather than silently collapsing to its zero boundary. The core verifier also contains materially better adversarial tests and much clearer statements about what its independence does and does not establish.

Those repairs are substantial. They are not, however, enough to turn the current repository state into a coherent top-journal revision.

The central problem has shifted. R13 is presently an **evidence-layer revision without a corresponding paper revision**. The manuscript carrying the economic claims is still the R12 procurement manuscript. The R13 code and witness layer changes the certification semantics, introduces new exact-response and continuous-contract source modules, and attempts new proposal benchmarks, but the main text, theorem labeling, supplement architecture, response letter, revision index, and deposited paper objects have not been brought into one immutable R13 submission state. At the frozen SHA reviewed here, the extension workflow is still in progress and the expected extension-output directory is absent.

More importantly, the deeper Econometrica objections remain. The headline procurement result is still a theorem about a bespoke finite contract menu on one stored finite-array economy. The new exact continuous-contract calculation is explicitly a different analytical economy, not a robustness theorem for the settlement application. The repository still does not provide a quantitative approximation theorem placing the original continuous economic model inside the error neighborhood required to transfer the procurement ranking. The headline certificate itself remains exact finite-state dynamic programming, not a result that requires a neural proposal. The mechanism evidence remains local and largely pointwise. And the computational comparisons remain internal rather than a convincing benchmark against serious external methods.

The paper has become much better at certifying a narrowly defined computational object. It has not yet established why that object, or the neural architecture surrounding it, constitutes an Econometrica-level economic or econometric contribution.

---

# 1. What R13 genuinely fixes

A harsh report should distinguish repaired defects from unresolved ones.

## 1.1 The arithmetic allowance is no longer merely trusted

The previous R12 re-review objected that the theorem charged an error allowance of \(10^{-7}\) while the independent verifier imported that allowance rather than independently establishing that it dominated the numerical error.

R13 materially improves this. The new certified_arithmetic.py:

- does not import the generator's Bellman solver or the advertised EPS as a theorem premise;
- converts stored binary64 inputs to exact rational representations;
- audits all stored sparse rows, including the first-date operator;
- tracks horizon-dependent norm and roundoff recurrences;
- produces a derived maximum bound;
- rejects an advertised allowance that is smaller than the derived bound; and
- includes a negative test in which an understated allowance is deliberately rejected.

The deposited core validation reports a derived maximum of approximately \(7.06\times 10^{-11}\), well below the charged \(10^{-7}\) allowance.

This directly answers the earlier T1 objection at the level of the stored binary64 target.

I emphasize the final clause. It is an arithmetic certificate for evaluation of the stored target. It is not a certificate for construction of that target from an underlying diffusion or continuous primitive model. That separate issue remains below.

## 1.2 The open positive mandate is handled correctly in the core witness

The previous R12 source optimized the “positive” class over a closure that admitted zero and did not force a chosen positive contract to have strictly positive initial risky share.

R13 now explicitly distinguishes:

- the closed class used to upper-bound a supremum; from
- a feasible lower witness for the open positive class.

When the closed optimizer lies on the zero boundary, positive_witness constructs a strictly positive interpolated action and records the resulting closure gap. verify_positive checks strict positivity, interpolation, feasibility, value consistency, and any attainment claim.

The independent negative test that mutates a positive procurement action to zero is rejected for the correct semantic reason. The deposited validation reports a minimum positive share of 0.8 in the actual procurement witnesses.

This directly answers the earlier T2 objection.

## 1.3 The core witness seal is substantially stronger

The core R13 output is not merely a collection of favorable summaries. The verifier reconstructs the principal finite-target inequalities, checks output inventory, checks canonical identity, reconstructs regional lower and upper objects, verifies transport, recomputes procurement comparisons, and executes destructive semantic fixtures.

The negative fixtures now cover, among other things:

- an understated arithmetic allowance;
- a zero “positive” procurement action;
- excess first-date transition mass;
- negative transition mass;
- infeasible continuation policy;
- destroyed upper certificates;
- stale summaries;
- continuation corruption;
- target-identity changes;
- unexpected output inventory; and
- certificate-file mutation.

This is a meaningful improvement in scientific software discipline.

## 1.4 The independence language is more honest

The core validation now says, in substance, that it is a separately coded binary64 reconstruction of a hash-identified finite target with an exact-rational arithmetic account. It explicitly excludes a constructor/diffusion certificate and does not represent itself as formal proof-assistant verification.

That is the appropriate scope.

These improvements are the strongest part of R13. They should be preserved.

---

# 2. T1 — R13 is not a self-contained paper revision

The largest immediate problem is no longer a hidden numerical bug. It is the identity of the review object.

At the frozen reviewed SHA, R13 does not contain a new R13 manuscript that incorporates the R13 theorem semantics. Instead:

- the operative procurement manuscript remains revisions/2026-09-18-r12-procurement-witness/paper/main.tex;
- the operative new-proof file remains the R12 S15 proof source;
- the point-by-point response remains the R12 response to the earlier R11 report;
- revisions/2026-09-19-r13-certified-response contains only logs;
- there is no R13 response to the independent R12 harsh re-review in the R13 revision directory;
- there is no R13 main-paper wrapper or R13 supplementary-paper wrapper there; and
- REVISION_INDEX.md still begins by declaring R11 to be the “Current complete revision.”

This is not a bookkeeping nuisance. It breaks the normal referee contract.

A referee needs one immutable object in which the prose claims, theorem statements, proof references, computational witnesses, replication instructions, and response letter all describe the same revision. Here the code has advanced to R13 while the scientific paper text remains R12.

For example, the main paper's verification section describes “the deposited R12 target” and the R12 verification chain. R13 changes the actual chain in precisely the places where the previous referee found defects: the arithmetic bound, open positive class, response-set machinery, refinement machinery, analytical continuous-contract module, proposal benchmark, and extension verifier. Those are not superficial implementation details. They change what has actually been proved and what scope limitations apply.

### Required response

The next revision should be a genuine paper revision, not another layer appended to the repository.

It should deposit, at one immutable SHA:

1. an R13-or-later main manuscript;
2. an R13-or-later supplement;
3. a point-by-point response to the R12 independent harsh report;
4. the exact core target and core witness;
5. all extension witnesses on which the manuscript relies;
6. independent validation receipts;
7. generated tables used by the manuscript;
8. final PDFs;
9. a revision index naming that exact SHA/state as current; and
10. a reproduction document that distinguishes generated evidence from historical artifacts.

No theorem should depend on a later workflow materialization after the review target is frozen.

---

# 3. T2 — The manuscript and the R13 evidence layer are semantically out of sync

R13 repairs two theorem-to-code gaps, but the manuscript has not been revised to say exactly how those repairs enter the theorem.

This matters especially for the positive class.

The correct R13 semantics are subtle:

- a supremum over the closure may be used for an upper bound;
- an attained lower witness in the positive class must be strictly positive;
- if the closure maximizer is zero, an explicitly positive near-optimal lower witness must be constructed;
- the gap to the closure must be charged.

That is a materially more careful theorem than “the positive class is optimized and the selected share is positive.” The paper should state this logic where the procurement theorem is defined, not leave it implicit in a new R13 Python helper.

Likewise, the R13 arithmetic derivation is not just “an arithmetic audit bounds roundoff.” It has a precise stored-array scope, operation graph, parameter range, sparse-row assumption, horizon recurrence, and fixed-point consistency check against the advertised allowance.

The current manuscript still describes the old certification architecture at a higher level than the R13 implementation now deserves.

### Required response

Every certification premise used by the headline numerical theorem should have a textual theorem/proposition/lemma counterpart. The code should be an implementation of the paper's mathematical object, not the place where the mathematical object is finally defined.

---

# 4. T3 — The extension evidence is not deposited at the reviewed SHA

At the time this report froze the target, the workflow “R13 extended theory and contract witnesses” was still in progress. The branch did not contain replication/r13/extensions.

This is particularly important because several of the most consequential responses to the prior referee exist only in extension source modules:

- the sharp finite-query response polytope;
- exact rational LP weak-duality checks;
- the continuous-contract analytical calculation;
- refined contract-menu response graphs;
- proposal benchmarking;
- additional stress checks;
- secant sensitivity; and
- the attempted operator-perturbation bridge.

Source code that intends to generate evidence is not deposited evidence.

The report therefore does not credit any numerical conclusion that depends on absent extension outputs.

The repository should not describe the current branch as a completed “certified response” while an essential evidence workflow is still producing the objects needed to support that description.

### Required response

Freeze review only after all claimed evidence is committed. If a workflow produces a scientific object, the object and its validation receipt must exist at the frozen review SHA. “The CI job will produce it” is not part of a referee record.

---

# 5. T4 — The provenance chain is still too fragmented

The current R13 state is spread across several identities:

- the current branch tip is dd9e0c755b743efdea2a7637f7620bb8ebc3b3c6;
- the completed core workflow ran from an earlier head;
- execution.json itself records another source_commit;
- the extension workflow was triggered from another head;
- generated source bundles are later materialized into the branch.

This can be made reproducible, but it is not yet easy for an external referee to determine which source tree generated which scientific object without reconstructing workflow history.

The scientific question is simple:

> Given the exact source tree at the reviewed commit, do the committed witnesses reproduce, and do they support exactly the claims in the manuscript at that same commit?

The repository should make that answer one command and one immutable receipt.

### Required response

The final execution receipt should record:

- reviewed source SHA;
- canonical manifest SHA;
- witness manifest SHA;
- independent-validation SHA;
- manuscript source hashes;
- generated-table hashes;
- build/PDF hashes;
- workflow/run identity if desired; and
- a statement that no scientific output is expected to mutate the review branch after that receipt.

This is especially important for a paper whose claimed contribution includes auditability.

---

# 6. E1 — The actual settlement procurement theorem remains a bespoke finite-menu theorem

The main economic result remains:

\[
\{+,-\}\times\{0,.2,.4,.6,.8,1\}\times\{1,\ldots,8\},
\]

with \(F=E\), fixed permissions, a specified capacity-cost function, specified term cost, external receipt of surrender fees, and an outside option.

The paper is admirably explicit that this is a finite institutional menu rather than unrestricted mechanism design. But candor about narrowness is not a substitute for showing that the narrowness is economically meaningful.

R13 adds primitive_contract.py, which is potentially useful. But that file says explicitly that its continuous-capacity commitment calculation is **not a calibration of the stored settlement model**. It is a separate analytical economy.

That distinction is fatal to any claim that R13 has answered the finite-menu objection for the headline application.

A theorem saying “in a different analytical economy, continuous capacity and term choice can produce 3 versus 4” is not a theorem saying “the 3-versus-4 result in the stochastic settlement economy is not an artifact of the six-point capacity menu.”

The new analytical example can illustrate a mechanism. It cannot certify robustness of the actual numerical theorem.

### Required response

The finite-menu criticism should be answered inside the same settlement economy.

At minimum:

- refine capacity around the selected region;
- decouple \(F\) from \(E\);
- allow continuous or sufficiently refined \(E\) and \(F\);
- report certified or tightly bounded optimal terms under those refinements;
- vary capacity-cost curvature;
- vary term-cost curvature;
- vary outside value;
- vary fee incidence;
- vary permission bounds; and
- show which features are genuinely responsible for the 3-versus-4 change.

If a continuous theorem is possible, apply it to the actual settlement primitives. If it is not possible, present the finite-menu result as a deliberately institution-specific example and scale down the general economic claim.

---

# 7. E2 — There is still no quantitative model-to-target theorem for the headline economic result

The main paper is unusually clear that the new theorem is about the deposited finite array system and “not an unstated diffusion approximation.” That statement is correct.

It also identifies the core Econometrica limitation.

The economic narrative is about a stochastic settlement economy with continuous-time or diffusion-style primitives inherited from the broader project. The numerical theorem is about a 1,617-state finite object with finite later-date controls and a stored first-date piecewise-affine operator.

To infer an economic theorem about the intended underlying model, one needs a quantitative bridge.

R13 stress-check source appears to construct an operator perturbation neighborhood using hypothetical bounds on reward and transition-kernel errors. That is a reasonable stability calculation. But the source itself correctly states that it **does not assert that the original diffusion discretization lies in this neighborhood**.

That means the central missing step is still missing.

The paper has a conditional statement of the form:

> if the true model is within this very small operator neighborhood, the discrete procurement margin survives.

It does not have the statement:

> the intended continuous economic model is within that neighborhood.

The first is a stability lemma. The second is the scientifically relevant approximation theorem.

### Required response

For the exact headline procurement separation, give a complete error budget from the underlying economic model to the stored target:

1. time discretization;
2. state truncation;
3. state interpolation or projection;
4. action discretization for consumption and adjustment;
5. first-date financial interpolation;
6. transition-kernel construction;
7. boundary/discharge approximation;
8. terminal approximation; and
9. numerical arithmetic.

Then propagate that total error through:

- value bounds;
- service secants;
- participation payments; and
- the smallest purchaser-surplus separation.

If the resulting bound is too large, that is scientifically informative. Refine the target or narrow the claim. Do not replace this with a hypothetical neighborhood whose inclusion premise has not been verified.

---

# 8. M1 — The strongest certified result still does not require a neural method

The title remains **Neural Bellman Operators**.

The strongest R13 evidence is a carefully reconstructed finite-state dynamic-programming certificate on committed arrays.

That is a virtue for correctness. It remains a problem for contribution identity.

The neural network does not establish the core procurement theorem. The certificate is deliberately designed so that an accurate neural fit is unnecessary for validity.

This creates a simple editorial question:

> What does the neural component make possible that a serious nonneural dynamic-programming, approximation, or parametric-control method could not make possible at comparable accuracy and cost?

R13 now contains source for proposal_benchmark.py, apparently training an MLP and comparing it with polynomial and nearest-anchor proposals. That is directionally responsive. But at the reviewed SHA the extension outputs are absent. More fundamentally, proposal prediction quality is not enough.

A neural proposal matters scientifically only if it improves an economically relevant end-to-end frontier:

- larger state dimension;
- richer action space;
- longer horizon;
- wider parameter region;
- tighter certificate for fixed resources;
- substantially cheaper discovery of good lower witnesses;
- or access to models where conventional proposal methods fail.

If exact DP/certificate construction dominates total cost at the scale actually used, then a small neural advantage in proposal fitting does not justify the paper's title.

### Required response

Provide a matched end-to-end benchmark where the neural proposal is evaluated together with:

- training cost;
- inference/proposal cost;
- verification cost;
- memory;
- final certificate width;
- final policy value;
- failure frequency; and
- scaling in dimension and action complexity.

Include strong nonneural baselines. If the neural method does not materially move the frontier, reposition the paper as verified parametric dynamic programming and make neural proposals an optional implementation device.

---

# 9. M2 — The sharp finite-query response machinery is cleaner, but its top-journal role is unclear

R13's oracle_polytope.py and theory_tests.py develop an exact-rational weak-duality route for bounding response features from finite value queries. This is mathematically more interesting than simply reporting a secant.

The idea can be useful:

- observed value-query intervals constrain a family of affine response planes;
- a rational LP can bound features of an \(\eta\)-optimal response;
- proposed dual multipliers can be validated exactly;
- constructed finite-response economies can witness sharpness in examples.

But the present R13 state has two problems.

First, the extension evidence is not yet deposited at the reviewed SHA.

Second, the new result is not yet integrated into the main economic theorem. The R12 paper still presents the simpler one-dimensional service-secants argument. It does not make clear whether the polytope result strictly strengthens the procurement theorem, reduces required value queries, handles multidimensional service, provides sharp identification under ties, or changes the substantive economic conclusion.

A mathematically neat tool added after the manuscript is not yet a paper contribution.

### Required response

Either make the finite-query response-set result a central theorem and demonstrate a substantive economic use that the old secant argument cannot deliver, or leave it as a supplementary verification technique. The paper should not accumulate independent technical ideas simply because each one can be certified.

---

# 10. M3 — The mechanism remains local and largely accounting-based

The corrected opportunity-exposure decomposition is valuable because it prevents a false inference from “downward adjustment disappears” to “the positive class must benefit more.”

The R13 core exposure records are internally consistent and explicitly say that they are pointwise accounting and signed-exposure enclosures, not a uniform primitive ordering.

That scope statement is correct.

It also shows why the mechanism section is not yet a transferable economic theorem.

The current evidence establishes, at selected parameter points:

- a local contribution from current drift;
- a signed future-exposure contribution;
- in the reported rows, zero financial-replacement contribution; and
- a small positive class difference.

It does not derive from primitives why one class should systematically load more heavily on high adjustment-opportunity states across a meaningful model class.

The paper therefore still has:

1. an identity;
2. an abstract sufficient ordering condition; and
3. pointwise verified decompositions.

That is not yet a structural economic mechanism in the sense expected from a top general-interest theory/econometrics journal.

### Required response

Derive primitive conditions on transition, preferences, wealth, stopping, or financial exposure that imply the relevant signed opportunity ordering, or map a broad calibrated parameter region and show that one component is stable and dominant for interpretable economic reasons.

Adverse cases should be used to identify the boundary of the mechanism, not merely preserved in a historical compendium.

---

# 11. C1 — The computational comparison is still predominantly internal

R13 compares variants of the authors' own bounding machinery and adds source for additional proposal/baseline exercises.

What is still missing is an external benchmark that allows a computational economist to understand the method's place in the literature.

For the finite target used in the headline theorem, serious alternatives include:

- exact finite-state dynamic programming;
- sparse-grid or interpolation methods where applicable;
- standard parametric MDP verification / synthesis methods;
- interval or verified dynamic programming;
- fitted value/policy iteration;
- polynomial or basis-function approximations;
- standard actor-critic / deep Galerkin / PINN-style approaches when comparing neural methods.

The paper does not need to beat every method. It does need to show what unique frontier it occupies.

A useful benchmark table would report:

- states and actions;
- parameter dimension;
- horizon;
- total wall time;
- peak memory;
- proposal/training time;
- exact/certification time;
- certificate width;
- achieved policy lower bound;
- upper bound;
- final optimality gap;
- hardware; and
- failure or nonconvergence modes.

Without this, “scalable,” “neural,” “certified,” and “regional” remain adjectives attached to separate pieces rather than one demonstrated computational advantage.

---

# 12. E3 — Several convenient economic definitions remain insufficiently justified

The service theorem is mathematically convenient because service is the coefficient on a perturbable operating-benefit parameter \(d\). This produces a clean value-query envelope.

That may be a legitimate service measure. The paper still needs to convince an economist that it is the economically relevant contractible output rather than the statistic most convenient for the method.

The same concern applies to the institutional choices:

- \(F=E\);
- external receipt of surrender fees;
- separate-numeraire capacity cost;
- fixed ex ante permissions;
- linear purchaser term cost;
- the particular outside option;
- participation-payment timing;
- and the absence of wealth effects from signing grants.

R13's separate analytical primitive-contract example contains some incidence invariance under binding participation. That is useful intuition, but because it is a different economy it does not establish robustness of the stochastic settlement result.

### Required response

Give either:

- a concrete institutional interpretation tied to observable contracts and plausible parameter magnitudes; or
- a theorem/robustness exercise showing which conclusions survive alternative definitions of service, transfer incidence, capacity incidence, fee recipient, and participation payment.

---

# 13. T5 — The arithmetic certificate is improved, but it should not be oversold as formal numerical verification

I regard the R13 arithmetic repair as a real fix. The manuscript should nevertheless state its assumptions with precision.

The audit is an analytic forward-error account over binary64 arrays and sparse recursions. It is not a proof about every possible implementation behavior of NumPy/SciPy on every platform, nor a formally verified floating-point program.

For example, the sparse-row accounting relies on an operation-count envelope and assumptions about stored nonnegative CSR data and reduction behavior. The approach is reasonable and conservative, but the scientific claim should remain:

> independently derived and checked floating-point error bounds under the stated binary64 operation model.

It should not drift into language such as “machine-verified theorem” unless the execution semantics themselves are formally captured.

This is mainly a presentation constraint, not a new rejection reason.

---

# 14. T6 — “Passed CI” is not the unit of scientific evidence

R13 is much better about this than earlier versions, but the repository remains workflow-centric.

A successful core run is useful operational information. It is not the theorem.

The scientific evidence is:

- a frozen target;
- a precise mathematical statement;
- lower and upper witnesses;
- arithmetic/error bounds;
- independent reconstruction;
- and strict inequalities with enough margin.

The paper should be readable and assessable from those objects without asking a referee to reconstruct workflow choreography.

The fact that the extension workflow was still in progress at the frozen review SHA is exactly why this distinction matters.

---

# 15. Paper architecture remains overextended

The project currently contains, at various levels of maturity:

- neural proposal;
- HJB/operator theory;
- finite-state exact certification;
- signed law transport;
- count-information relaxation;
- signed chord correction;
- regional parameter bounds;
- finite-query response sets;
- procurement;
- continuous analytical contracts;
- preference adjustment;
- financial-class comparisons;
- surrender;
- opportunity exposure;
- dynamic games;
- recursive utility;
- proposal benchmarking; and
- replication/witness architecture.

This is too many papers inside one paper unless one theorem chain clearly dominates.

The R12 procurement manuscript was an improvement because it tried to put one institutional question at the center. R13 risks reversing that progress by adding another layer of theory modules without rewriting the paper around a coherent contribution.

A strong paper should answer in one sentence:

> What can an economist now establish that could not previously be established, and which theorem proves it?

I still cannot identify a single answer that dominates the repository.

Possible coherent identities include:

1. **Verified procurement under hard-to-solve dynamic response.** Then procurement and response-set certification are central; neural proposals are subordinate.
2. **Neural proposals with rigorous ex post certification.** Then the neural scaling frontier is central and must be demonstrated convincingly.
3. **Parametric dynamic-program verification for economic institutional choice.** Then the signed/region machinery is central and should be benchmarked against parametric verification literature.
4. **Economic theory of commitment and adjustment.** Then the computational method should support a general primitive theorem, not carry the paper itself.

At present the manuscript attempts to preserve all four.

---

# 16. Additional technical comments

1. **Update the theorem's revision identity.** A theorem named as an R12 target should not rely on an R13-only arithmetic/open-class verifier without explicit textual integration.

2. **Deposit the R13 response letter.** The previous harsh report raised source-level and economic objections. A referee should be able to map every comment to a response and source location.

3. **Make exact response and \(\eta\)-response logically distinct.** State the economic theorem first for exact best responses. Treat \(\eta\)-robustness as numerical robustness.

4. **Report the binding rival at every headline margin.** The minimum positive gap is meaningful only with the identity and economics of the competitor that generates it.

5. **Report sensitivity in \(h\) in the actual paper.** A secant certificate must show how the economic curvature/error tradeoff behaves, not only select \(h=.01\).

6. **Apply the sharper response polytope to the headline service object or explain why not.** Otherwise it is an unattached technical extension.

7. **Distinguish open-class nonattainment in tables.** If any positive-class lower witness is interpolated rather than attained, state the positivity margin and closure gap.

8. **Use explicit failures instead of bare Python assertions in producer-side scientific checks.** Independent verification mitigates this, but source intended as scientific validation should not silently weaken under optimized interpreter flags.

9. **Clarify sparse arithmetic assumptions.** Document operation-count assumptions and platform scope for the binary64 error derivation.

10. **Do not call source modules evidence before their outputs are deposited.** This applies to the continuous-contract, refinement, proposal, and sharp-response extensions at the frozen SHA.

11. **Put the actual target identity in every generated table.** Historical R11/R12 and current R13 evidence should be impossible to confuse visually.

12. **Retire the stale revision index.** A repository claiming current R13 certification cannot have its top-level revision index say that R11 is the current complete revision.

13. **Replace the repository-root boilerplate README.** The current README is still essentially Econometric Society LaTeX-support documentation. A referee should see the scientific reading order and reproduction entry point immediately.

14. **Explain the status of root ECTA.tex.** It is historical and substantively different from the current procurement manuscript. That should be impossible to mistake.

15. **Give one authoritative build command.** It should build the exact review PDF and verify all evidence used by that PDF without materializing new scientific results onto the branch.

16. **Separate historical preservation from current evidentiary scope.** Preserving old experiments is good. A referee should not have to inspect them to determine what the current theorem depends on.

17. **Quantify target-construction error or remove continuous-model language from the headline claim.** There is no acceptable middle position.

18. **Test menu refinement in the actual settlement economy.** The separate analytical economy does not answer this.

19. **Test alternative fee recipient and capacity incidence in the actual settlement economy.** Participation can create invariances in special analytical cases; demonstrate whether that is true here.

20. **Benchmark against a serious external baseline.** Internal variants do not establish methodological importance.

---

# 17. Minimum standard before another Econometrica-style re-review

| Area | Minimum convincing response |
|---|---|
| Review object | One immutable SHA containing the current manuscript, supplement, response letter, all claimed witnesses, independent validation, tables, PDFs and updated revision index. |
| Revision coherence | Manuscript text must explicitly state the R13-or-later arithmetic, open-class and response-set semantics actually used by the code. |
| Workflow state | No scientifically necessary workflow may still be materializing evidence after the review SHA is frozen. |
| Arithmetic | Preserve the R13 independent data-dependent roundoff derivation and destructive allowance tests. |
| Positive mandate | Preserve strict positivity for attained lower witnesses and explicit closure-gap accounting. |
| Model-to-target | Quantitative approximation from the intended economic model to the stored target, propagated through the smallest procurement margin. |
| Contract choice | Continuous or refined contract robustness in the **same stochastic settlement economy**, not only a separate analytical example. |
| Neural identity | End-to-end evidence that neural proposal materially expands the feasible accuracy/scale frontier, or reposition the paper away from a neural-method claim. |
| Mechanism | Primitive economic conditions or a broad stable parameter region explaining the adjustment/financial interaction. |
| Computation | Matched external baselines with total time, memory, certificate width, policy quality and scaling. |
| Economics | Robustness to service definition, cost incidence, fee recipient, outside option, permissions and horizon. |
| Architecture | One dominant contribution and one main theorem chain; historical compendium separated from current evidence. |

---

# 18. Evidence reviewed

This report freezes and assesses revision SHA dd9e0c755b743efdea2a7637f7620bb8ebc3b3c6.

The review included, among other current-revision objects:

- revisions/2026-09-18-r12-procurement-witness/paper/main.tex;
- revisions/2026-09-18-r12-procurement-witness/paper/S15_proofs.tex;
- revisions/2026-09-18-r12-procurement-witness/response_to_referee.md;
- REVISION_INDEX.md;
- replication/r13/canonical.py and the deposited canonical target;
- replication/r13/certified_arithmetic.py;
- replication/r13/engine.py;
- replication/r13/science.py;
- replication/r13/verify.py;
- replication/r13/output/expected.json;
- replication/r13/output/arithmetic.json;
- replication/r13/output/independent_validation.json;
- replication/r13/output/procurement.json and procurement witnesses;
- replication/r13/output/chord_certificate.json;
- replication/r13/output/count_certificate.json;
- replication/r13/output/dominance.json;
- replication/r13/output/exposure.json;
- replication/r13/output/target_comparison.json;
- replication/r13/primitive_contract.py;
- replication/r13/oracle_polytope.py;
- replication/r13/proposal_benchmark.py;
- replication/r13/refinement.py;
- replication/r13/stress_checks.py;
- replication/r13/theory_tests.py;
- replication/r13/verify_extensions.py;
- .github/workflows/r13-core-witness.yml;
- .github/workflows/r13-extension-witness.yml; and
- the prior independent R12 harsh referee report.

At the frozen SHA, the core witness workflow had completed successfully. The R13 extension workflow was still in progress, and replication/r13/extensions was not deposited. Accordingly, this report treats the extension source as proposed machinery, not completed scientific evidence.

---

# 19. Final assessment

R13 is a better computational object than R12.

The previous referee identified two precise theorem-to-code failures. The authors have taken those objections seriously and repaired them in a technically credible way. The arithmetic allowance is now derived rather than trusted. The open positive mandate is now treated correctly. The witness seal and semantic negative tests are much stronger. These are real advances and should survive any rewrite.

But the standard for Econometrica is not “the verifier no longer contains the bugs identified last round.”

The current revision remains below that standard for three independent reasons.

First, **it is not a coherent review object**. The manuscript is still R12; R13 is primarily a code/evidence layer; the revision index is stale; the R13-specific revision directory is incomplete; and an extension workflow needed for several advertised responses was still running at the reviewed SHA.

Second, **the headline economic theorem remains narrow**. It is a certified ranking on a bespoke finite menu and stored finite economy. The new continuous-contract file is a different analytical example. There is still no quantitative bridge from the intended continuous economic model to the finite target strong enough to preserve the smallest procurement margin.

Third, **the paper's contribution identity remains unresolved**. The strongest certificate does not require a neural method. The economic mechanism is local. The computational comparisons are mainly internal. The repository contains several potentially useful ideas, but no single theorem chain yet demonstrates an Econometrica-level advance in economics, econometrics, or computational economic methodology.

For those reasons, my recommendation remains **reject in the present form**.

A further revision would be worth re-reading only if it is a genuine reconception: one immutable paper object, one dominant contribution, one complete model-to-decision error chain, and evidence showing why the chosen computational architecture changes what economists can actually prove or compute.
