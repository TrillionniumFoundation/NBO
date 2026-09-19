# Referee Report — Neural Bellman Operators, current R18 repository snapshot

**Journal standard used:** Econometrica-style external assessment.  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r18-scientific-response-2026-09-19`  
**Reviewed HEAD:** `d15591aff0bed68334cbb205294edfb04297427c`  
**Date of report:** 20 September 2026

This is an owner-commissioned advisory referee report. It is not an official Econometrica editorial decision and does not represent appointment by Econometrica.

## Recommendation

**Reject in the present form. Do not treat R18 as a substantive revision.**

The decisive issue is no longer merely that several scientific objections remain open. The more immediate problem is that the object labeled `revision/econometrica-r18-scientific-response-2026-09-19` is not, in fact, a scientific response. Relative to R17 it adds only the prior R17 referee report. R17, relative to R16, likewise adds only the R16 referee report. R16, relative to the last substantive R15 development state, adds preservation workflows and the R15 referee report, not a completed paper response. The latest scientific additions remain four R15 source fragments that were never assembled into a complete referee-facing manuscript.

Thus there is no new complete revision for a referee to evaluate as an R18 paper. The current repository snapshot instead contains: (i) the complete R14 package still identified by the repository itself as the current referee-facing paper, (ii) four later R15 development fragments, and (iii) successive referee reports and preservation workflows. This is not a harmless naming problem. It prevents a referee from identifying a unique current manuscript, a unique response letter, a complete build, a frozen evidence package, or even the text that authors intend to submit.

Even if I disregard that packaging failure and evaluate the latest scientific fragments on their merits, the central Econometrica-level objections remain unresolved: the continuous-model-to-array bridge is not quantitatively executed; the neural method is not shown to be necessary or advantageous for the economic results; the newest theoretical pieces largely reorganize standard occupancy-measure, Lagrangian-duality, weak-duality, and verification arguments without isolating a sufficiently deep new economic theorem; and the enforcement result that is genuinely useful does not, by itself, establish the initial-state comparison emphasized in the application.

The paper has made real conceptual progress since the earlier versions. In particular, the information hierarchy is clearer, the global near-optimal-response restriction is better stated, the open-mandate attainment convention is more disciplined, and the authors are unusually explicit about what their numerical evidence does not prove. Those are important improvements. They do not make the current R18 repository state a publishable revision.

# 1. The R18 branch contains no R18 scientific revision

The exact Git comparison is unambiguous.

Relative to `revision/econometrica-r17-full-response-2026-09-19`, the R18 branch is ahead by one commit. That commit is:

`d15591aff0bed68334cbb205294edfb04297427c`  
**“Add independent harsh Econometrica-style rereview for R17.”**

The only changed file is:

`reviews/2026-09-19-econometrica-r17-harsh-rereview/referee_report.md`.

There is no changed theorem, manuscript source, response letter, table, numerical output, replication code, build manifest, or paper PDF in the R17-to-R18 diff.

That fact alone means R18 cannot be reviewed as a new scientific revision. A new referee report cannot be the scientific content of the next author revision.

## Required response

Before another substantive rereview, create a genuinely new revision branch whose scientific diff can be identified independently of any review artifacts. The branch should contain a complete manuscript, supplement, point-by-point response, all generated tables, all replication inputs and outputs needed by the claims, and a release manifest identifying the exact reviewed commit.

# 2. R17 is likewise not a “full response,” and R16 is not a scientific response either

The same problem recurs one step earlier.

Relative to `revision/econometrica-r16-development-2026-09-19`, the branch named `revision/econometrica-r17-full-response-2026-09-19` is ahead by one commit and one file: the R16 referee report.

Relative to `revision/econometrica-r15-development-2026-09-19`, R16 adds three commits whose material changes are preservation workflows plus the R15 referee report. The R16 workflow is explicitly named:

`R16 source preservation (not scientific validation)`.

That label is accurate. It should also have prevented the branch from being treated as the next scientific revision.

This history matters because the present repository gives the appearance of repeated author-referee cycles while the scientific object has not moved correspondingly. Branch numbers are not scientific progress. For a serious journal process the unit of review must be a frozen manuscript revision, not a chronological stack of reports.

## Required response

Separate author revisions from referee branches. Review reports should live only on `review/...` branches. A `revision/...` branch should move only when the paper, supplement, response, or evidence moves.

# 3. The repository itself still identifies R14 as the current paper

At the reviewed R18 HEAD, both the root `README.md` and `REVISION_INDEX.md` identify **R14** as the current referee-facing revision.

The root README begins:

> Neural Bellman Operators — Revision R14

and points readers to:

- `revisions/2026-09-19-r14-referee-response/ECTA_R14.pdf`
- `SUPP_R14.pdf`
- `RESPONSE_R14.pdf`
- `COMPENDIUM_R14.pdf`

The revision index likewise states:

> Current referee-facing revision: R14 — September 19, 2026

This is not merely stale documentation. It is the repository's own authoritative reading instruction. It means the repository has no internally coherent claim that R15, R16, R17, or R18 is the current complete paper.

A referee should never have to infer the intended manuscript from branch names and commit archaeology.

## Required response

The next author revision should update the authoritative index and README in the same scientific commit series that creates the paper. It should identify exactly one current manuscript, one supplement, one response letter, one reproduction entry point, and one source commit.

# 4. The latest substantive scientific state is R15, but R15 is not a complete paper package

The last substantive scientific development commit is `b41fe7d31fe7cfe606ba3171ce91cdfece983651` on `revision/econometrica-r15-development-2026-09-19`.

Relative to the complete R14 package, the R15 scientific additions are four source fragments:

- `revisions/2026-09-19-r15-referee-response/paper/introduction.tex`
- `.../information.tex`
- `.../enforcement.tex`
- `.../operator_bridge.tex`

The R15 directory contains only the `paper/` subdirectory with those four files. It does not contain a complete `ECTA_R15.tex`, a complete supplement, a point-by-point response, a compiled PDF, a build report, or a release manifest.

Moreover, the R15 fragments are not wired into the complete R14 manuscript. The R14-to-R15 diff adds the four fragments rather than replacing or modifying the complete R14 source package.

This makes the later theoretical work impossible to evaluate as a finished paper. A referee can read the fragments, but cannot determine the final order, cross-reference integrity, theorem dependencies, proof placement, duplicated claims, deleted claims, final abstract, final conclusion, or whether the paper actually compiles.

## Required response

Do not submit another partial source layer. Produce a single complete manuscript revision.

# 5. The R15 fragments currently reference missing table inputs

This is a concrete build failure, not a stylistic concern.

The R15 `enforcement.tex` fragment contains

`\input{revisions/2026-09-19-r15-referee-response/paper/table_enforcement}`

and

`\input{revisions/2026-09-19-r15-referee-response/paper/table_continuous_institutions}`.

The R15 `operator_bridge.tex` fragment contains

`\input{revisions/2026-09-19-r15-referee-response/paper/table_repeated_proposals}`.

At the reviewed R18 HEAD, all three referenced files are absent. Direct repository lookups return 404.

Therefore even the new fragments cannot be compiled as written. The numerical claims embedded around those tables cannot be checked against the table text because the table text is not in the revision.

Examples include the claims that the initial-state no-surrender threshold falls by more than 0.07209, that the no-surrender private value rises by more than 0.03545, and that three-seed computational comparisons contain isolated neural improvements as well as failures. Those may or may not be backed by code elsewhere, but the paper package does not contain the actual table artifacts it asks TeX to include.

## Required response

Every `\input` in the submitted manuscript must resolve at the frozen reviewed commit. CI should compile the complete main paper and supplement from a clean checkout and fail on any missing source or generated table.

# 6. The source-audit workflow is preservation, not a scientific validation pipeline

The R15 workflow `.github/workflows/r15-source-audit.yml` exports tracked text files and immutable inputs into ZIP artifacts. It does not compile an R15 manuscript, regenerate the new quantitative claims, test theorem fixtures, verify the new enforcement calculations, or check that the new source fragments are mutually consistent.

The R16 workflow is even more explicit that its purpose is preservation only.

These workflows are useful provenance tools. They should not be counted as evidence that a revision is complete or correct.

A credible computational paper needs at least three distinct checks:

1. **Build integrity:** clean-checkout compilation of the exact paper and supplement.
2. **Scientific regeneration:** recreation of all new tables and numerical claims from frozen inputs.
3. **Independent validation:** a separate checker that verifies identities, inequalities, interval coverage, certificates, and decision margins without merely reusing the generation code.

R14 came much closer to this standard than the current R15–R18 chain.

# 7. The continuous-model-to-array bridge remains unresolved

This remains the central scientific blocker if the paper continues to motivate its application by an antecedent continuous stochastic model.

R14 was commendably explicit. Its model-to-decision theorem introduced a conditional error recursion and then stated that the deposited constructor had **not** established the quantitative inclusion of the continuous diffusion in the finite target. It also reported a local variance diagnostic in which the stored preference variance is approximately

`0.000883883476...`

versus the diffusion increment variance

`0.0003125`,

a ratio of approximately `2.828427`.

R14 correctly said that this diagnostic is not itself a value-error bound. But that is exactly the point: the missing bound is still missing.

R15 does not close the gap. Its new continuous Bellman-barrier proposition is mathematically sensible as a verification template. It requires a bounded (C^{1,2}) candidate, a uniform action supremum residual, terminal/boundary/obstacle conditions, and integrable residual envelopes. The R15 text then explicitly concedes:

> The deposited settlement results do not yet include numerical continuous barriers satisfying a decision-separating budget.

That sentence is decisive. A theorem that describes what must be verified is not an executed verification.

The decision-directed error-budget proposition is also only conditional. It can reduce conservatism if the model-to-target error is known to belong to a specified uncertainty set (Xi). But the hard scientific task is to prove the relevant (Xi) for the constructor. R15 itself correctly says that the constructor or continuous-model argument must still establish that set.

## Why this matters economically

The paper's procurement conclusions depend on strict margins. The correct question is not whether the numerical Bellman residual is small relative to private values; it is whether the complete model-to-target error budget is small relative to the smallest decision-separating purchaser margin after response, participation, and feature-transfer errors are propagated.

No such full calculation is present.

## Two acceptable routes

A future paper must choose one of two clean routes.

**Route A: continuous-model claim.** Execute a quantitative bridge. Specify the continuous state-action domain, projection/lifting, boundary handling, continuation regularity, time error, state error, action error, first-date interpolation error, kernel error, terminal error, and feature-transfer error. Propagate them through the exact reward queries used by the purchaser and show that the final institutional decision survives.

**Route B: finite-model claim.** Define the 1,617-state array economy as the economic model of the application. Then remove language that asks the finite-array certificate to validate the antecedent diffusion. The continuous Bellman-barrier theorem may remain as a separate extension theorem, but it must not be presented as if it had been numerically executed.

Either route is defensible. The current hybrid is not.

# 8. The “Neural Bellman Operators” title still overstates what the neural component establishes

The paper's own evidence is unusually candid and therefore unusually damaging to the current title-level claim.

R14 states that on the deposited target the fitted network is less accurate than the nearest-anchor policy and that exact upper-value calculation dominates their online comparison.

R15's new computational fragment goes further. It says:

- all experiment families keep 1,617 states and two state variables;
- the experiment is **not** a state-dimension experiment;
- the exact dynamic-program control is decisive at the tested sizes;
- a state-dimension or end-to-end neural computational advantage would require a further resource-matched experiment;
- no such advantage is inferred from the reported certificates.

Those are appropriate caveats. But if those statements are true, then the paper has not shown that neural approximation is essential to the economic theorem, the certificate, or the computational frontier.

The operator-to-response proposition also does not rescue the title. Its logic is: if an independently verified Bellman residual gives value intervals, those intervals can be inserted into the response bound. That is a useful interface theorem, but it applies equally to nonneural approximation schemes. Indeed the paper emphasizes that certification remains valid when the neural proposal is poor.

There is no problem with a paper using neural proposals as one computational heuristic. The problem is making “Neural Bellman Operators” the scientific identity when the strongest results are method-agnostic and the exact dynamic program wins on the tested problems.

## Required response

Either:

- demonstrate a genuine regime in which the neural operator materially expands the tractable economic problem while retaining independent certification and fair nonneural baselines; or
- retitle and reorganize the paper around **certified dynamic response sets / robust contract choice**, with neural proposals demoted to one implementation device.

At present I strongly prefer the second route.

# 9. The new response-set theory is clearer, but the novelty case remains below the Econometrica bar as presently isolated

R15 improves the conceptual hierarchy substantially. It now distinguishes:

1. a fixed known finite dynamic model;
2. a collection of models consistent with information;
3. an oracle-only affine-response identified set.

That clarification is important.

However, the main new mathematical ingredients still appear to be close to standard objects:

- the fixed-model response set is an occupancy-measure polytope intersected with a global payoff-loss constraint;
- the Bellman-loss identity is the standard performance-difference / LP-duality relationship;
- the support function of the near-optimal response set is obtained by Lagrangian duality;
- the directed-query representation is a reward perturbation written through that dual;
- the operator-to-response certificate is Bellman monotonicity plus recursive residual propagation;
- the decision-directed error budget is weak duality plus a support function of a right-hand-side uncertainty set.

I do not say these statements are wrong. On the contrary, many of them are clean and potentially useful. The issue is contribution scale.

For Econometrica, the paper must identify the economic theorem that becomes possible because these ingredients are combined, and show that theorem is both nontrivial and not already implied by standard dynamic-programming, inverse-optimization, robust-optimization, or revealed-preference machinery.

The current prose often presents a disciplined assembly of established ideas as if the assembly itself were the theorem-level innovation.

## What would strengthen the novelty case

A stronger version would isolate one result of the following form:

- a minimal-information theorem characterizing exactly which contract rankings are identified from a budget of dynamic value queries;
- an optimal query-design theorem with a nontrivial complexity or information bound;
- a sharp impossibility theorem separating oracle-only identification from known-dynamics identification;
- a dynamic procurement theorem whose robust ranking genuinely requires joint response geometry and cannot be recovered from coordinate envelopes;
- or a mechanism theorem showing how institutional design changes the value of dynamic information.

The present directed-query representation is a promising starting point, but it is not yet that result.

# 10. The enforcement theorem is useful, but it does not prove the application’s central initial-state ranking

R15's enforcement reframing is one of the better additions.

For a fixed initial condition it defines

[
F^{m init}
=
maxleft{0,
sup_{p:H(p)>0}
rac{B(p)-W_infty}{H(p)}
ight},
]

and for state-wide implementation it defines a uniform obstacle threshold

[
F_r^{m unif}
=
sup_{n,s}
[G_n(s)-V^r_{infty,n}(s)]_+.
]

If adjustment enlarges the feasible no-surrender operating controls while leaving the surrender payoff and fee incidence unchanged, then the no-surrender value rises state by state and the **uniform** threshold weakly falls. This is correct and economically interpretable.

But the paper itself acknowledges the limitation: the state-wise ordering does not automatically rank the **initial-state** threshold (F^{m init}). Reachability and the set of profitable surrender deviations can change with the regime.

That distinction matters because the application emphasizes the initial contract and claims a materially lower initial-state enforcement requirement with adjustment.

So the theorem and the headline application are not the same result. The application-specific ranking remains a quantitative fact of the finite model, not a general theorem implied by feasible-set inclusion.

This is acceptable if presented that way. It is not acceptable if the broad theorem is used rhetorically to make the calibrated comparison sound more structural than it is.

## Required response

State the hierarchy explicitly:

- theorem: adjustment weakly lowers the uniform obstacle requirement under stated inclusion assumptions;
- additional conditions under which this implies an initial-state ranking;
- finite-model computation: the actual initial-state thresholds in the deposited economy;
- no claim that the computed magnitude transfers to the antecedent diffusion absent the model-to-target bridge.

# 11. The whole-interval response graph is potentially useful, but it is still an auxiliary outer relaxation

The R15 interval-graph construction is more interesting than a dense fee grid because it attempts to exclude actions over a whole common fee cell using endpoint information.

But the object remains an outer relaxation. The paper explicitly allows the graph to combine actions that may require different fees to be privately optimal. Therefore the resulting purchaser bound is conservative by construction.

That is fine for certification. It should not be sold as a characterization of the actual common-fee response correspondence.

The proof assumptions also need to be made completely local and auditable in the final manuscript:

- what exactly is the action-value function whose convexity in the fee is used?
- when does the continuation problem preserve convexity?
- which endpoint policies generate the lower planes?
- how are interval uncertainty and arithmetic allowances inserted into the exclusion test?
- what breaks for positive-(eta) behavior?
- which cells are determined by the graph bound versus the value-message bound?

At present these questions are described in a fragment rather than settled in a complete theorem-proof-computation chain.

# 12. The open-mandate convention is a genuine improvement

I want to record one substantive improvement clearly.

The R15 text separates:

- exact behavior on contracts whose policy supremum is attained;
- positive-(eta) behavior when only approximate maximization is required;
- closure values used only to form conservative rival upper bounds.

This is much better than silently treating the closure point (pi_0=0) as an available exact action when the admissible class requires (0<pi_0leq L).

The final paper should retain this convention and use it globally, including the theorem statements, numerical tables, and response letter.

But this improvement also illustrates why a complete revision is necessary: the convention currently lives in an R15 fragment that is not the authoritative manuscript.

# 13. The computational experiment does not yet support a methods contribution

The R15 repeated-proposal design is more careful than earlier neural evidence because it includes:

- multiple action-set sizes and horizons;
- three seeds;
- nearest-anchor control;
- polynomial control;
- evaluated policy-bank control;
- exact dynamic-program control;
- explicit teacher and evaluation workloads.

That is directionally right.

But the fragment itself admits that all problems retain the same state dimension and that exact dynamic programming remains decisive. Hence the experiment does not establish the usual reason one would introduce a neural operator: solving a class that exact or classical numerical methods cannot reasonably solve.

A future computational methods claim would need a true scaling frontier with matched accuracy, hardware, implementation quality, offline cost, online cost, memory, and certification overhead. It would also need to separate proposal speed from total end-to-end certified decision cost.

Without that, the experiment is best treated as an implementation study showing that the economic certificate can tolerate both useful and poor proposals.

# 14. The economic application remains a stylized normalized economy

The current paper is not empirically estimated. Its preference, financial, institutional, and purchaser parameters are normalized or stipulated. The authors now say this explicitly.

That is not disqualifying for a theory paper. But it changes what the application can accomplish. It cannot bear the burden of proving external economic importance by itself.

Accordingly, the paper's case for Econometrica must come primarily from the general economic theory of information, response, and contract design. At present that general contribution is still too close to a careful synthesis of known mathematical tools, while the strongest mechanism comparisons remain features of one finite constructed economy.

# 15. Revision discipline and submission hygiene need a reset

The branch history currently mixes three distinct objects:

- author science;
- referee reports;
- preservation/audit infrastructure.

This makes provenance harder rather than easier.

A clean process would be:

1. freeze the reviewed author commit;
2. create a separate `review/...` branch containing only the referee report;
3. create the next `revision/...` branch from the reviewed author commit plus the chosen response;
4. include a point-by-point response that cites the exact prior report commit;
5. compile and regenerate the full revision;
6. freeze a new reviewed author commit;
7. repeat.

Do not advance the revision number merely by adding a referee report.

# 16. What the paper has genuinely improved

The negative recommendation should not obscure the real progress.

The best current ideas are:

- response uncertainty rather than selected-policy uncertainty as the object relevant for procurement;
- explicit separation of information sets: finite value messages versus a known dynamic model;
- global, not statewise, accounting for near-optimal behavior;
- directed reward queries tailored to a purchaser's joint response direction;
- conservative continuous-instrument coverage rather than pretending a finite menu is a continuum;
- clear separation of exact attainment from open-class closure;
- explicit enforcement-frontier language distinguishing initial-state and uniform implementation;
- separation of neural proposal quality from certificate validity;
- unusually candid disclosure that the finite-array certificate does not validate the antecedent diffusion;
- preservation of adverse mechanism cases rather than deleting them.

These are good ingredients. They now need to be distilled into one paper rather than accumulated as successive layers.

# 17. Minimum conditions before another Econometrica-style rereview

I would not recommend another substantive rereview until all of the following are satisfied.

1. **One authoritative revision.** A new author branch contains a complete manuscript, supplement, response letter, tables, code pointers, PDFs, and release manifest.
2. **No review-only “revision.”** The scientific diff from the previously reviewed paper is explicit.
3. **Clean build.** Every `\input` resolves and CI compiles the paper and supplement from a clean checkout.
4. **Point-by-point response.** Every numbered objection from the last substantive referee report is answered with manuscript locations and evidence.
5. **Model-scope decision.** Either execute a decision-separating continuous-model certificate or define the finite array economy as the quantitative model and remove unsupported transfer language.
6. **Neural-scope decision.** Either demonstrate genuine certified computational advantage on a hard frontier or demote neurality from the title and central contribution.
7. **Novelty theorem.** State a central theorem whose economic content goes materially beyond standard occupancy LP, Lagrangian duality, robust weak duality, and verification.
8. **Enforcement hierarchy.** Separate the general uniform-threshold result from the application-specific initial-threshold ranking.
9. **Generated evidence.** Regenerate the new enforcement, institution, and repeated-proposal tables from frozen inputs; include the outputs in the release.
10. **Independent checker.** Verify interval coverage, dual certificates, response bounds, table identities, and purchaser decision margins without merely rerunning the same generation routine.
11. **Revision metadata.** Update README and revision index to the exact current paper; eliminate stale “R14 is current” instructions.
12. **Submission-length architecture.** Move historical material out of the main argumentative path. The paper should read as one economic contribution, not a repository history.

# 18. Evidence reviewed

For this report I checked, at the reviewed R18 snapshot:

- branch chronology and commit comparisons from R15 through R18;
- the exact R18 HEAD commit and its one-file diff;
- root `README.md` and `REVISION_INDEX.md`;
- the complete R14 manuscript source in `revisions/2026-09-19-r14-referee-response/paper/main.tex`;
- the R14 model-to-decision section and constructor diagnostic;
- all four R15 scientific fragments:
  - `introduction.tex`
  - `information.tex`
  - `enforcement.tex`
  - `operator_bridge.tex`
- the contents of the R15 revision directory;
- direct existence checks for the three R15 table inputs referenced by the source;
- the R15 source-audit workflow;
- the R16 preservation workflows;
- the R14, R15, R16, and R17 referee reports already stored in the repository.

# 19. Final assessment

The current repository contains a potentially interesting paper trying to connect dynamic-program value information to robust economic procurement under endogenous response. The authors have become increasingly careful about ties, near-optimal behavior, open action classes, continuous instruments, and verification. Those improvements make the project more credible.

But **R18 is not a new paper revision**. Its only new content relative to R17 is the previous referee report. R17 itself is not a full author response, and the last substantive R15 additions remain incomplete source fragments with unresolved table inputs and no complete referee-facing manuscript.

On the science, the main unresolved issue remains the gap between the finite stored array economy and the antecedent continuous model. The neural label remains stronger than the evidence. The mathematical novelty remains insufficiently isolated from standard LP/duality/verification tools. The enforcement result is useful but more limited than the application-level rhetoric can suggest.

For these reasons my recommendation is **reject in the present form**.

A new version could be worth reading if it is rebuilt around one clean contribution—most plausibly **certified dynamic response sets and robust contract choice**—and if the authors make a definitive choice about both model scope and neural scope. Another branch that merely accumulates review artifacts would not constitute a scientific revision.
