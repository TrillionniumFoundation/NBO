# Referee Report — Neural Bellman Operators, Revision R14

**Journal standard used:** Econometrica-style external assessment. This is an owner-commissioned advisory report, not an official editorial decision and not a representation of appointment by Econometrica.

**Date:** 19 September 2026

**Repository:** TrillionniumFoundation/NBO

**Reviewed revision branch:** revision/econometrica-r14-development-2026-09-19

**Frozen reviewed SHA:** 1e8720f46de3e1d1caf5348bf9024e898dc7d119

**Review branch:** review/econometrica-r14-harsh-2026-09-19-1e8720f

**Immediate prior report:** reviews/2026-09-19-econometrica-r13-certified-harsh/referee_report.md

## Recommendation

**Reject in the present form.**

R14 is a major improvement over R13 and, for the first time in this sequence, is a coherent and technically serious referee object. I do not repeat the previous report's criticism that the paper and evidence are out of sync: R14 has substantially fixed that problem. It deposits a new main manuscript, a current proof supplement, a point-by-point response, a release manifest, generated tables, current PDFs, independent validation, and an authoritative check-only entry point. It also answers the previous finite-menu criticism in the correct economy: the continuous-fee certificate is now executed on the same stochastic settlement target rather than on a separate illustrative economy.

Those are genuine advances.

The remaining objections are more fundamental. They are no longer primarily software-engineering objections. They concern what has actually been established economically and methodologically.

First, the paper still does not close the quantitative bridge from the intended continuous economic model to the 1,617-state stored array economy. R14 explicitly acknowledges this. The new constructor diagnostic in fact shows a material projection effect, so the missing step cannot be treated as a benign technicality. The paper's strict economic margins are small enough that this missing error budget is decision-critical.

Second, the title and methodological identity remain difficult to reconcile with the evidence. The central response-set/procurement theorem does not require a neural approximation. On the deposited target, the neural proposal performs dramatically worse than the nearest-anchor and polynomial controls. There is one target size and one recorded neural seed, with no demonstrated state-dimension, action-dimension, horizon, or certificate-cost frontier on which the neural method expands what can be solved or certified.

Third, the economic mechanism remains institution- and target-specific. The original 3-versus-4 compulsory-term comparison becomes 2-versus-4 under a finer fee menu and 1-versus-1 under continuous fees. The 54-point opportunity map contains positive, negative, and near-zero differences, while the primitive monotonicity theorem deliberately applies to a subclass that excludes central features of the actual settlement economy. The paper therefore has a convincing lesson about the importance of institutional design and adverse response selection, but not yet a general economic theorem about adjustment, financial exposure, or commitment.

Fourth, the finite-query response-set theorem is clean and useful, but the paper has not yet demonstrated the novelty and scope that would justify an Econometrica-level methodological contribution. Its sharpness is relative to finite oracle information across compatible affine-response economies, not sharpness for the fixed dynamic model. The manuscript needs a much deeper comparison with convex support-function arguments, robust optimization, inverse/revealed-preference formulations, partial identification of counterfactuals, and the literature on numerical verification of dynamic economic models.

My recommendation is therefore rejection in the present form. A substantially reconceived paper could merit a fresh reading, but another incremental layer of certified calculations would not resolve the central issues.

---

# 1. What R14 genuinely fixes

A harsh report should not recycle objections that the authors have actually addressed.

## 1.1 R14 is now a coherent paper package

The previous report's most immediate objection was that R13 was an evidence-layer revision without a corresponding current paper. R14 materially resolves that problem.

The current package contains:

- ECTA_R14.pdf and editable current source;
- SUPP_R14.pdf and current proof source;
- RESPONSE_R14.pdf and source;
- a complete historical compendium;
- a release manifest binding the current paper objects and scientific inputs;
- a current top-level README and revision index;
- generated current tables carrying the canonical target identity; and
- a check-only command that verifies the deposited evidence rather than silently regenerating a new scientific target.

This is the correct direction. I regard the old T1/T2/T3/T4 bookkeeping objections as substantially repaired, subject to the smaller provenance comment in Section 8 below.

## 1.2 The baseline finite-menu objection is answered in the same economy

This is the strongest substantive improvement.

R13's continuous-contract calculation was a separate analytical economy and therefore did not establish robustness of the settlement application. R14 now carries the contract refinement through the same stored settlement target.

The reported sequence is economically informative:

- fee step 0.20: adjusted term 3, no-adjustment term 4;
- fee step 0.10: adjusted term 3, no-adjustment term 6;
- fee step 0.05: adjusted term 2, no-adjustment term 4;
- continuous fee: term 1 in both regimes.

The continuous certificate is not a grid interpolation masquerading as optimization. The paper covers the full fee interval with cellwise response restrictions, a relaxation of the fee-surrender product, capacity-cost lower tangents, participation inequalities, and rationally checked weak-duality upper bounds. The independent receipt reports 342 leaves in the adjustment regime and 351 in the no-adjustment regime, with term identification in both.

The executable continuous candidates have global regret bounds of approximately 8.83e-7 and 9.25e-8. The closest different-term upper gaps are approximately 1.02e-4 and 5.71e-5. Within the stated finite-array model, this is a serious and appropriately conservative calculation.

I therefore withdraw the prior criticism that the paper has only a bespoke coarse-menu result.

## 1.3 The response-set theorem is now part of the economic chain

R14 no longer leaves the finite-query polytope as an unattached technical module. The current paper places the finite-query response theorem first, uses it to define adverse response bounds, feeds those into procurement, and demonstrates a joint duration-surrender query in the actual settlement application.

The distinction between:

- sharpness relative to the finite oracle information, and
- implementability in the already specified dynamic economy

is clearly stated. That distinction is important and correct.

The exact-response equality-graph construction is also separated from the eta-response statement. The supplement correctly notes that a local Bellman equality mask is not automatically a valid global eta-response graph.

## 1.4 The arithmetic and open-class semantics remain strong

The R13 arithmetic repair is preserved and integrated into the paper. The current independent validation reports a largest derived arithmetic bound of about 7.06e-11, and the manuscript states the operation-model assumptions rather than calling the result a formal machine proof.

Likewise, the positive first financial mandate is treated as an open class. A zero closure point is not relabeled as a positive action. Feasible positive witnesses and closure gaps are handled explicitly, and the current continuous incumbents are reported as attained positive policies.

These are important correctness improvements.

## 1.5 R14 is unusually candid about adverse evidence

The paper does not hide the unfavorable neural benchmark, adverse mechanism cases, or the constructor discrepancy.

That is scientifically preferable to selecting only favorable cases. In particular:

- the nearest-anchor proposal is vastly more accurate than the fitted neural proposal on the deposited target;
- the 54-point mechanism map contains sign reversals;
- the paper explicitly states that continuous-state diffusion inclusion is not proved;
- the paper explicitly states that neural scaling superiority is not proved.

This candor improves the credibility of the current evidence. It does not, however, remove the substantive consequences of those facts for the paper's contribution.

---

# 2. E1 — The model-to-target bridge is still missing, and R14 now shows why it matters

This is the central unresolved objection.

The economic narrative is inherited from a stochastic continuous-state settlement model. The certified theorem is a theorem about a particular finite array economy with:

- eight intervals;
- 33 preference nodes;
- 49 wealth nodes;
- finite later-date action meshes;
- a piecewise-affine first-date financial operator; and
- stored projected transition kernels.

The paper now gives a correct abstract transfer theorem. It decomposes local approximation error into time, truncation, state, action, first-date interpolation, kernel, boundary, terminal, and arithmetic components, and propagates them through the Bellman recursion.

That is a useful theorem. It is not the missing quantitative result.

The missing result is a verified numerical bound on those terms for the actual constructor and the actual economic primitives, tight enough to preserve the relevant procurement separation.

R14 explicitly says that this has not been established.

## 2.1 The missing bound is economically first-order, not cosmetic

The paper's own simple one-dimensional transfer calculation makes the scale of the problem transparent. With purchaser service price b=1 and secant width h, its sufficient two-contract decision charge is

    2(2 Delta / h + Delta).

At h=0.01, this is approximately 402 Delta before any fee, quality, or feature-transfer error.

Thus a purchaser margin of order 1e-4 requires a value-model discrepancy of order 1e-7 under this conservative route. The exact threshold depends on which reported margin is used, but the order of magnitude is clear.

For example, using the manuscript's reported h-sensitivity margins gives approximately:

- h=0.0025, margin 3.04e-5: Delta below about 1.9e-8;
- h=0.005, margin 1.14e-4: Delta below about 1.4e-7;
- h=0.01, margin 1.56e-4: Delta below about 3.9e-7.

These are only illustrative sufficient thresholds, not a substitute for the full multivariate continuous-fee calculation. Their importance is conceptual: the economic separations are small enough that the constructor approximation has to be controlled very tightly.

The continuous-fee term identification is also based on small different-term margins, especially approximately 5.71e-5 in the no-adjustment regime. There is no basis for assuming that an unquantified state/time/action/projection error is negligible relative to that margin.

## 2.2 The constructor diagnostic is an alarm, not a bridge

R14's direct diagnostic is useful precisely because it shows that one cannot casually equate fixed-array arithmetic accuracy with model accuracy.

For the selected drift-free interior first action, the stored normalized preference variance is approximately

    0.0008838834764831865,

while the antecedent diffusion variance over the step is

    0.0003125.

The ratio is approximately 2.8284.

The manuscript correctly says that this moment discrepancy is not itself a value-error lower bound or upper bound. I agree.

But this means the only honest inference is that the projection is quantitatively material and must be analyzed. It cannot be used to reassure the reader that the omitted model-to-target terms are below the economic margin.

The current paper therefore establishes:

> a highly audited institutional ranking in a hash-identified finite dynamic program,

not:

> a quantitatively verified ranking in the antecedent continuous economic model.

That distinction is decisive for the current framing.

## 2.3 Econometrica has an existing computational-error tradition that makes this omission particularly visible

The manuscript should engage much more directly with the computational economics literature on interpreting approximation error, including work such as:

- Kubler and Schmedders, “Approximate versus Exact Equilibria in Dynamic Economies,” Econometrica (2005);
- Santos, “Accuracy of Simulations for Stochastic Dynamic Models,” Econometrica (2005);
- Kubler, “Verifying Competitive Equilibria in Dynamic Economies,” Review of Economic Studies (2011);
- Judd, Maliar, and Maliar, “Lower Bounds on Approximation Errors to Numerical Solutions of Dynamic Economic Models,” Econometrica (2017).

The important lesson from this literature is not that every paper needs a formal proof assistant. It is that a small residual or a highly accurate calculation on an approximate model does not by itself establish closeness of the economically relevant object.

R14 understands this principle in words. It has not yet completed it quantitatively.

### Required response

There are two coherent routes.

**Route A: close the bridge.** Provide a model-specific quantitative error bound from the continuous primitives to the stored target, with explicit treatment of the stopping boundary, projection, time step, action discretization, and first-date operator. Propagate the resulting bound through the response set and the smallest economic margin.

**Route B: change the scientific object.** Define the finite-state settlement economy as the economic model being studied, rather than as a numerical representation of a continuous antecedent. Then justify why that finite model is economically interesting in its own right and remove any language suggesting that the executed result has already been transferred to the diffusion.

At present the paper occupies an unstable middle position.

---

# 3. M1 — The evidence does not support “Neural Bellman Operators” as the paper's methodological identity

R14 is commendably explicit that certificate validity is independent of neural accuracy.

That is exactly the problem for the current title and contribution claim.

The strongest results in the paper are:

- finite-query response identification;
- robust procurement under adverse response selection;
- continuous-instrument certification;
- exact finite-state dynamic programming and equality-graph supports;
- rational weak-duality verification; and
- an error-accounting architecture.

None of these results requires the fitted neural proposal to be accurate.

On the deposited target, the proposal evidence is strongly adverse to the neural method:

| Regime | Proposal | Maximum verified policy gap |
|---|---|---:|
| Adjustment | Neural | about 0.806 |
| Adjustment | Polynomial | about 0.0902 |
| Adjustment | Nearest anchor | about 2.13e-7 |
| No adjustment | Neural | about 0.568 |
| No adjustment | Polynomial | about 0.0147 |
| No adjustment | Nearest anchor | about 2e-7 |

The neural proposal is not merely slightly inferior. On this target, it is orders of magnitude worse than the nearest-anchor policy in the metric most closely connected to the certified lower policy.

The paper also reports only:

- one target size;
- one recorded neural seed;
- no state-dimension scaling experiment;
- no action-dimension scaling experiment;
- no horizon scaling experiment;
- no repeated-seed distribution;
- no matched certificate-width versus total-resource frontier; and
- no external strong neural or nonneural implementation benchmark.

The current paper therefore demonstrates an important negative fact: **the certification framework is robust to a bad neural proposal.** That is a property of the verifier, not evidence for a neural computational contribution.

## 3.1 The current title overstates the role of the neural method

The sentence that the title “denotes the maintained operator architecture and its theory” is not enough.

A title is a claim about the paper's intellectual center. The current center is response identification and verified institutional choice. The neural part is presently an optional, and on the reported target inferior, proposal generator.

A top-journal paper can certainly report a negative neural result. But then the paper should not make the neural architecture the primary label unless it establishes a theorem or scaling result showing why that architecture is essential in another dimension of the contribution.

### Required response

Again there are two coherent routes.

**Route A: demonstrate a neural frontier.** Construct target families with increasing state dimension, action complexity, horizon, or parameter dimension. Compare end-to-end:

- training/teacher cost;
- proposal cost;
- policy evaluation;
- upper certification;
- memory;
- final lower value;
- certificate width;
- failure frequency; and
- total wall time.

Use repeated seeds and strong nonneural baselines. Show a region where the neural proposal materially expands the set of problems that can be certified at a given accuracy/resource budget.

**Route B: reposition the paper.** Make the central contribution “certified response sets for dynamic contracts” or an equivalent non-neural formulation. Treat neural approximation as one proposal mechanism among several and move the historical neural operator program to the compendium or a separate paper.

The present evidence strongly favors Route B.

---

# 4. E2 — The paper has discovered that the headline economic mechanism is not robust in the form previously advertised

This is not a criticism of the continuous-fee calculation. It is a consequence of taking that calculation seriously.

The original economic narrative emphasized a difference in compulsory terms between adjustment and no adjustment.

R14 now shows:

- 0.20 fee menu: 3 versus 4;
- 0.10 fee menu: 3 versus 6;
- 0.05 fee menu: 2 versus 4;
- continuous fee: 1 versus 1.

Thus the term-length differential is not a robust comparative-static conclusion. It is highly sensitive to the enforcement menu.

The continuous result replaces the old term comparison with a different statement: under the specified baseline continuous-fee institution, both regimes use the shortest compulsory term, but the adjusted regime can be implemented with a lower surrender fee.

That may be an economically interesting result. It is, however, a different mechanism and should be treated as such.

## 4.1 The current mechanism evidence is not structurally stable

The 54-point opportunity map reinforces this conclusion.

The total option difference is reported as:

- positive at 15 points;
- negative at 12 points;
- near zero at 27 points.

The range includes values from approximately -0.00558 to +0.000444.

This is not evidence for a general sign.

The primitive monotonicity proposition is mathematically sensible, but it requires a restricted irreversible-upgrade stopping subclass with assumptions such as exogenous monotone consumption, order-preserving wealth transitions, common survival, and no wealth-dependent surrender. The actual settlement economy has endogenous consumption, repeated preference adjustment on a mesh, and elective surrender. The paper correctly says that the proposition need not apply there.

Consequently, the paper currently contains:

1. a decomposition identity;
2. a sign theorem for a restrictive subclass; and
3. a richer numerical model in which the sign often reverses.

This is useful diagnostic work, but it is not yet a transferable economic mechanism theorem.

## 4.2 The strongest valid economic lesson may be institutional fragility

R14's most persuasive economic result may actually be:

> coarse enforcement menus can generate apparent commitment-length differences that disappear when the enforcement price becomes continuous.

That is a coherent lesson. It deserves to be stated more directly if it is the intended substantive contribution.

But then the paper should stop presenting the earlier term differential as evidence for a stable adjustment mechanism.

### Required response

Either derive broader primitive conditions that apply to the actual economically relevant model class, or reframe the application as evidence about institutional fragility and adverse-response certification rather than as a general comparative-static theory of adjustment and financial exposure.

---

# 5. E3 — Most institutional sensitivity exercises remain on the same finite grid that the paper has shown can be misleading

This is a new issue created by R14's own successful continuous-fee analysis.

Table “Institutional Counterfactuals in the Same Settlement Economy” is informative. It varies:

- fee recipient;
- capacity-cost incidence;
- enforcement efficiency;
- capacity-cost curvature;
- term-cost curvature;
- quality valuation;
- outside value; and
- service price.

But the table explicitly states that these are calculations on the 0.05 fee menu and are not continuous-fee claims.

That qualification is honest, but scientifically important.

The paper has just shown that moving from the 0.05 menu to the fee continuum changes the baseline term conclusion from 2-versus-4 to 1-versus-1. It follows that one cannot interpret the finite-menu institutional sensitivity table as establishing robustness of the continuous institution.

For example, a change in fee incidence or capacity efficiency may move the relevant surrender threshold between grid points. The selected term can then be an artifact of the same fee discretization that R14 has already shown to be economically consequential in the baseline.

### Required response

For the economically emphasized institutional counterfactuals, run the continuous-fee certificate, or provide a theorem showing that the finite-menu result is sufficient for the relevant comparative statement.

It is not necessary to continuous-certify every exploratory row. But the paper should identify a small set of central counterfactuals and certify those under the same continuous instrument used for the headline baseline.

---

# 6. M2 — The finite-query response theorem needs a much stronger novelty and literature argument

Theorem 1 is the cleanest abstract contribution in the current paper.

Its idea is appealing:

- finite value-query intervals constrain affine response planes;
- a lifted polyhedron describes all feature vectors compatible with those observations;
- support functions of that set bound economically relevant response moments;
- ties and eta-optimality can be accommodated;
- rational weak duality can certify the resulting support bound.

The sharpness statement is also correctly limited: every feasible lifted point is realizable by some compatible finite affine-response economy, not necessarily by the fixed settlement dynamic program.

The question for Econometrica is not whether this is correct. The question is what is substantively new.

## 6.1 The current related-literature discussion is too narrow

The main paper principally positions the result against:

- successor features/reward transfer;
- the Milgrom-Segal envelope theorem; and
- parametric Markov verification.

That is not enough.

The theorem also has obvious connections to:

- convex support-function geometry;
- revealed-preference inequalities;
- inverse optimization;
- robust optimization;
- partial identification;
- counterfactual bounds from incomplete utility information; and
- value-of-information formulations.

Recent work on partial identification of counterfactuals in dynamic discrete-choice models is especially relevant conceptually: it asks what policy-relevant outcomes can be learned when the underlying utility information does not point-identify the counterfactual object, and formulates bounds through optimization. The paper needs to explain whether its contribution is a new dynamic-program-specific identification theorem, a computational certificate for known convex restrictions, or both.

Likewise, the numerical-verification literature in economics should be part of the main contribution discussion, not only a background reference list.

## 6.2 The current sharpness notion is weaker than a reader may initially infer

The theorem is sharp relative to oracle information and K because the converse is allowed to construct a new finite affine-response economy.

That is mathematically legitimate.

But it does not show that the polytope equals the identified set inside a fixed class of Markov transition systems, utility primitives, or contract models. In the actual application, the equality graph can be strictly tighter.

This makes the economic interpretation of “sharp” important. The current manuscript states the qualification, but the title-level contribution still risks sounding stronger than the theorem actually provides.

### Required response

Add a real comparison theorem or proposition showing the relationship between:

1. the finite-oracle identified set;
2. a fixed dynamic model's attainable response set;
3. equality-graph information when the full Bellman solution is available; and
4. any partial-identification object used in related econometric work.

Then explain which information structure makes the finite-query theorem valuable: for example, when only certified values can be transferred but full policy graphs cannot.

Without this positioning, Theorem 1 reads as a clean convex-information lemma rather than an Econometrica-level methodological advance.

---

# 7. C1 — The computational evidence is still too small and too internal for a methods claim

R14 improves the comparison by including an in-repository implementation of rectangular parameter lifting and by reporting wider law intervals.

That is useful.

It still does not establish a computational frontier.

The independently checked R14 run itself reports approximately:

- 583 dynamic problems;
- 418 response graphs;
- about 873 seconds of verification; and
- peak resident memory around 1.18 GiB

on a target with 1,617 states and eight intervals.

Those figures are not inherently poor. But they make a scalability claim impossible without a scaling experiment.

The main paper also acknowledges that the rectangular-lifting code is an in-repository implementation rather than an external-package benchmark. This is the correct disclosure, but it means the comparison does not establish state-of-the-art relative performance.

Econometrica has published computational methods that make scalability itself a demonstrated contribution, for example adaptive sparse-grid methods for high-dimensional dynamic models. If the present paper wants to be read as a computational-methods paper, the relevant comparison is not whether one internal relaxation is tighter than another on one small target. It is whether the proposed architecture changes the accuracy-cost frontier on economically meaningful model families.

### Required response

Report a scaling study with at least several target sizes, and separate:

- target construction;
- proposal/training;
- lower-policy evaluation;
- upper certification;
- response-set support;
- continuous-instrument search; and
- independent checking.

If neural methods remain central, include repeated neural training and resource-matched nonneural approximators. If the paper is repositioned around certification rather than neural computation, then benchmark the certification layer against standard exact/interval/parametric alternatives.

---

# 8. T1 — The release is much cleaner, but the claimed frozen referee branch does not exist at the reviewed snapshot

This is a smaller issue, but it is concrete and should be fixed because provenance is part of the paper's claimed strength.

REVISION_INDEX.md states that:

> the separately frozen referee branch is revision/econometrica-r14-referee-response-2026-09-19

and distinguishes it from the development branch.

At the time I froze this review, GitHub returned “Branch not found” for that stated branch. The current R14 object was available on:

    revision/econometrica-r14-development-2026-09-19

whose head was:

    1e8720f46de3e1d1caf5348bf9024e898dc7d119.

The report therefore freezes that exact commit.

This is not a scientific defect in the theorem. It is a provenance mismatch in a repository that makes immutability and review identity part of its methodological discipline.

### Required response

Either create the branch that the revision index says exists, or change the index so it names only refs that actually exist at the deposit. A referee should never have to infer which branch was intended to be frozen.

---

# 9. T2 — Exact-response economics on an open action class still deserves a cleaner behavioral statement

The implementation handles the positive open mandate more carefully than earlier revisions.

For the incumbent, strict positive attainment is checked. For upper bounds, closure information can validly enlarge the response set.

The remaining conceptual issue is the economic definition of a contract at a parameter value where the agent's supremum over the open class is not attained.

If eta=0 and there is no best response, there is no exact response to select. A closure-based upper bound remains conservative, but the underlying exact-response game is not behaviorally complete at that contract.

The continuous-fee certificate is reported at eta=0.

I do not see a mathematical invalidity in using closure planes for an upper bound. I do see a presentation issue: the reader needs to know whether all contract cells are interpreted as exact-response contracts with existence, or whether nonattainment points are treated through limits while the purchaser comparison is still defined through a supremum.

### Required response

State one global convention for the continuum:

- either prove existence of an exact response for every admissible contract class relevant to the economic comparison;
- or formulate the economic continuum theorem directly for eta-responses and take eta down to a stated positive tolerance;
- or define the purchaser benchmark as a supremum over implementable approximate responses and state the resulting behavioral interpretation.

Do not let “closure is a valid upper bound” substitute for defining the agent's behavior at a contract where no maximizer exists.

---

# 10. E4 — The application is still a normalized computational economy, not an empirically disciplined economic application

The current paper is much clearer about this than older versions. It explicitly says that key institutional parameters are normalized rather than estimated from a dataset.

That clarity is welcome.

It also limits what the numerical application can establish.

The results depend on:

- the operating benefit;
- capacity cost and curvature;
- compulsory-term cost;
- surrender-fee incidence;
- outside value;
- quality valuation;
- the permission structure;
- the finite horizon; and
- the particular transition target.

R14 demonstrates that some of these choices change the selected term or mandate.

There is no empirical discipline establishing which region is economically relevant.

That is acceptable for a pure theory/methods paper only if the general theorem or computational innovation is strong enough to carry the paper. At present, the abstract theorem is not yet adequately positioned and the neural computational claim is not supported by the evidence.

### Required response

The authors need to choose what kind of paper this is.

If it is an economic application, provide a credible calibration/measurement/identification rationale for the main primitives and a clear real institutional analogue.

If it is a theory paper, strengthen the primitive comparative statics so that the numerical model illustrates rather than determines the result.

If it is a computational-methods paper, demonstrate the computational frontier and treat the settlement economy as a benchmark instance.

Trying to preserve all three identities continues to dilute the contribution.

---

# 11. Paper architecture is improved but still carries too much historical identity

The 18-page current main paper is much better focused than the earlier compendium.

However, several presentation choices still reveal the repository history rather than the logic of a submission.

For example, the current standalone supplement begins at Section S.16 because S.1–S.15 live in a historical supplement. That numbering is useful for repository preservation but awkward for a self-contained current submission.

Likewise, the title remains tied to the historical Neural Bellman Operator program even though the current paper's central theorem chain is response-set identification and procurement.

A journal submission should be readable without knowing the sequence R4–R14.

### Required response

For the next genuine paper version:

- renumber the current supplement from S.1 unless earlier sections are actually part of the current supplement;
- keep historical preservation in the repository, not in the reader's logical numbering;
- make the title match the theorem chain actually defended by current evidence;
- put the contribution comparison in the main introduction rather than relying on the historical compendium.

---

# 12. Additional technical comments

1. **Report the exact reviewed SHA in the manuscript package.** The release manifest gives source identities, but the final branch/commit identity should be exposed in a plain referee-facing note once the deposit is frozen.

2. **Separate term identification from fee optimality visually.** The continuous table does this in text, but a reader may still interpret the displayed fee as “the optimum.” Label it “executable fee” or “certified candidate fee” in the table itself.

3. **Report the tightest different-term rival directly in the continuous table.** The term-specific supplement has it, but the main result would be easier to assess if the nearest term competitor and the term-identification gap were in the main table.

4. **Do not let the tiny same-term regret distract from model error.** A regret below 1e-6 inside the stored target is numerically impressive but economically irrelevant if the unbounded constructor error is larger than the term gap.

5. **Continuous-certify the most important incidence results.** The finite-menu institutional table should not be the end of the robustness argument now that menu sensitivity is known to be large.

6. **Clarify what “observable quality” means institutionally.** Wealth-qualified duration is mathematically well-defined, but if wealth is not contractible or observable to the purchaser, the economic interpretation changes.

7. **The finite-query “joint” example should report query cost.** If joint directions tighten the response set, report how many additional dynamic solves are needed per economically relevant direction and how that scales with feature dimension.

8. **Discuss query design.** The continuous algorithm adaptively adds benefit perturbations. This is potentially an interesting active-information problem. Explain whether there is any performance guarantee or whether the current strategy is purely heuristic with ex post validity.

9. **Keep producer and verifier independence claims narrow.** Separate recoding is valuable, but both operate on the same stored economic target and shared conceptual assumptions. Independence of code paths is not independence of model specification.

10. **The binary64 audit is not the bottleneck anymore.** It is now much tighter than every economic margin. Further arithmetic polishing would not answer the remaining scientific objections.

11. **The mechanism map needs economically interpretable axes.** A 54-point Cartesian grid is useful for falsifying a universal sign but weak for explaining why the sign changes. Add threshold plots or primitive inequalities showing which state transitions drive each reversal.

12. **The response-set theorem should distinguish observed and designed queries.** In the application the researcher chooses reward perturbations. This is different from partial identification from exogenous observed values. The information-acquisition interpretation may be one of the genuinely novel aspects and should be developed.

13. **Explain why rational weak duality is economically necessary.** Exact rational checking is valuable for auditability, but the main paper should emphasize which economic conclusion would otherwise be vulnerable, rather than treating exact arithmetic as a contribution by itself.

14. **Report target construction cost.** End-to-end computational comparisons should include the cost of generating the canonical arrays if that step would be required in a new economic application.

15. **Acknowledge the literature on error analysis more centrally.** The current reference list is stronger than the main related-literature paragraph. The introduction should discuss prior work on verifying numerical dynamic models, not only approximation methods.

16. **The adverse neural result should affect the title and abstract.** It should not appear as a disclaimer late in the computational section while the title continues to foreground neural operators.

17. **Do not interpret a one-seed negative neural result as a universal failure either.** The evidence is sufficient to refute demonstrated superiority on this target, not to establish that neural proposals can never help. The paper currently mostly respects this distinction and should continue to do so.

18. **The continuum certificate is currently baseline-specific.** If the paper wants to emphasize generality, show at least one nonquadratic capacity-cost continuous certificate or state clearly which parts of the LP architecture rely on convex tangent bounds and how they generalize.

19. **The purchaser is complete-information.** The word “procurement” can evoke adverse selection/mechanism design. Continue to state prominently that there is no private type/reporting mechanism, and avoid positioning the result as a mechanism-design theorem.

20. **The use of a strict weak-participation convention matters.** The manuscript discusses adding a strict participation premium. Put the maximum admissible premium implied by the smallest certified margin in the main results, since some margins are extremely small.

---

# 13. Minimum standard before another Econometrica-style review

| Area | Minimum convincing response |
|---|---|
| Model-to-target | Quantitative bound from the intended continuous model to the stored target, propagated through the smallest term/procurement margin; or redefine the finite target as the economic model and remove unproved diffusion implications. |
| Contribution identity | Either demonstrate a neural scaling/resource frontier with repeated matched controls, or remove neural methods from the paper's central title/claim and treat them as optional proposals. |
| Economic mechanism | Reframe the substantive result around institutional fragility, or derive primitive conditions that cover the richer settlement economy rather than a separate restrictive subclass. |
| Continuous robustness | Re-run the central institutional counterfactuals under continuous fees, not only the 0.05 menu. |
| Response-set novelty | Position Theorem 1 against convex identification, robust/inverse optimization, revealed preference, counterfactual partial identification, and numerical verification; explain precisely what is new. |
| Computation | Scaling evidence across target sizes and matched end-to-end time, memory, lower value, upper bound, certificate width, and failure behavior. |
| Open-class behavior | Globally define behavior at contracts where an exact response may fail to attain the open-class supremum. |
| Provenance | Make the claimed frozen branch actually exist, or remove it from the index; freeze one immutable referee object. |
| Architecture | One dominant contribution, title, abstract, and supplement numbering aligned with that contribution rather than repository chronology. |

I would not recommend another review based only on tighter arithmetic, more CI checks, or additional finite-menu rows. Those parts of the project are already comparatively strong. The remaining issues require economic or methodological reconception.

---

# 14. Evidence reviewed

This report freezes and evaluates commit:

    1e8720f46de3e1d1caf5348bf9024e898dc7d119

on revision/econometrica-r14-development-2026-09-19.

The review included, among other objects:

- README.md;
- REVISION_INDEX.md;
- ECTA_R14.tex;
- SUPP_R14.tex;
- RESPONSE_R14.tex;
- revisions/2026-09-19-r14-referee-response/README.md;
- revisions/2026-09-19-r14-referee-response/release_manifest.json;
- revisions/2026-09-19-r14-referee-response/paper/main.tex;
- revisions/2026-09-19-r14-referee-response/paper/proofs.tex;
- revisions/2026-09-19-r14-referee-response/paper/response.tex;
- revisions/2026-09-19-r14-referee-response/paper/references.tex;
- the nested-menu, continuous-fee, term-bound, joint-query, institutional, mechanism, proposal, arithmetic, changing-law, and lifting tables;
- revisions/2026-09-19-r14-referee-response/logs/independent-validation.json;
- replication/r14/output/continuum_certificate.json;
- replication/r14/output/economic_extensions.json;
- replication/r14/review.py and replication/r14/verify.py;
- the canonical R13 target and imported extension evidence identified by the R14 manifest; and
- the previous R13 harsh referee report.

The independent R14 receipt reports all checked predicates passing, including 583 dynamic problems, 418 response graphs, 54 mechanism points, complete fee coverage, rational weak-duality checks, and destructive negative fixtures. I treat those checks as evidence about the deposited finite target. Consistent with the receipt's own scope, I do not treat them as certification of continuous-state diffusion inclusion or neural scaling performance.

I also considered the contribution against established computational economics work on numerical accuracy and high-dimensional dynamic methods, and against adjacent recent work on partial identification of dynamic counterfactuals. The current manuscript's main related-literature discussion is too narrow relative to that comparison.

---

# 15. Final assessment

R14 is not a cosmetic revision.

It fixes the prior paper/evidence mismatch, integrates the response-set theorem into the economic argument, carries continuous enforcement into the actual settlement target, independently checks a complete interval cover, preserves the arithmetic/open-class repairs, reports adverse neural evidence, and directly exposes a constructor projection effect. The authors have responded to the previous technical criticism more seriously than in earlier rounds.

Precisely because of those improvements, the remaining weaknesses are now easier to identify.

The paper's strongest executed economic theorem is a theorem about one hash-identified finite array economy. Its transfer to the antecedent continuous model is conditional and unquantified. The paper's title foregrounds a neural method that is unnecessary for the certificate and performs poorly against simple controls on the only reported target. The main economic term-length mechanism disappears under continuous enforcement, and the richer opportunity map has no stable sign. Most institutional counterfactuals remain on a fee grid that the baseline analysis has already shown can change the conclusion. The abstract response-set theorem is potentially useful, but its novelty and relationship to existing identification, convex, and verification literatures are not yet developed at the level required for a general-interest top journal.

For these reasons my recommendation is **reject in the present form**.

The most promising route is not another incremental R15 with more evidence layered onto the same identity. It is a reconception around one of two papers:

1. a paper on **certified response sets and institutional choice in dynamic models**, with a complete model-to-target error bridge and the neural proposal demoted to an implementation option; or
2. a paper on **neural dynamic-program proposals with rigorous ex post certification**, with a genuinely high-dimensional resource frontier showing where the neural architecture changes what can be computed.

R14 contains material that could support the first route. The present manuscript still tries to preserve both.

