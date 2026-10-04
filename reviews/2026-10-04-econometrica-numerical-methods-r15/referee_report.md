# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r15-2026-10-04`  
**Pinned revision commit:** `1cb3cc9efe135966ec228dfaf51c6841a6dfc97c`  
**Pinned revision tree:** `4d26e498db033a16adfd7d3c38968766a2b9878e`  
**Pinned root manuscript blob:** `32953ff2500f3af8a491cf1dd710276d2d77bdbf` (`ECTA.tex`)  
**Pinned root supplement blob:** `50eac8d04b25b6521780d4e07b9617b377168e88` (`supp.tex`)  
**Report date:** 4 October 2026  
**Recommendation:** **Reject in the present form. R15 is a complete, unusually transparent, and materially stronger computational record, but it still does not establish an Econometrica-level contribution for the learned Bellman critic that defines NBO. A substantially shorter new submission centered on verified policy improvement, or a genuinely prospective NBO study with stronger contribution-isolating baselines, could merit serious consideration.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R15 is another substantial advance over the paper I reviewed at R14. It is not a cosmetic response. The author has frozen and executed a new four-method experiment, explicitly defined a finite distribution over complete algorithm streams, included failed target attainment in the work distribution, added a direct neural-HJB comparator, developed a candidate-occupation Bellman account, executed a separate protected-observation study, strengthened the scalar classical benchmark, and reduced the main article from 63 to 56 pages. The publication snapshot is source-bound, compiled, and accompanied by a detailed ledger. I independently checked the branch and source identities, the committed aggregate tables, the experiment protocol, the final audits, and one original dimension-50 execution artifact.

The new experiment produces a genuine positive result. Over the declared sixteen-stream finite distribution, NBO improves on the analytical schedule in dimensions 10 and 50. The original common-path comparison gives a materially positive NBO-minus-neural-HJB interval in dimension 50. A later deterministic paired-transfer refinement, applied to the same observations, also makes the dimension-10 interval materially positive. R15 is careful to state that this result concerns the specified HJB procedure rather than every possible direct HJB implementation.

The central difficulty nevertheless remains. NBO's distinctive learned Bellman critic is still not shown to add value relative to the simpler candidate generators that share the same economic verifier.

Raw costate improvement and direct policy optimization attain essentially the same verified payoffs as NBO. All four NBO-minus-Raw/DPO method intervals remain unresolved and extend outside the paper's practical-equivalence band. Raw is cheaper than NBO at the declared target. The newly completed candidate-occupation mechanism calculation does not certify a positive welfare contribution from the fitted continuation object, and its critic-versus-Raw risk intervals are extremely wide. In the independent scalar economy, the classical Howard policies outperform both frozen neural policies and evaluate faster. Thus R15 demonstrates that several feasible candidate generators can be certified, and that the particular residual-fitting HJB implementation performs poorly in the selected high-volatility design. It does not demonstrate why the learned NBO critic is needed.

This distinction is decisive for a numerical-method paper. A result of the form “NBO beats this one frozen HJB implementation” is useful, but it cannot by itself carry the title, breadth, and publication claim when a cheaper critic-free method is statistically indistinguishable from NBO and the paper's own mechanism account remains negative. The strongest robust contribution continues to be the model-specific verification architecture: the analytical anchor, policy-specific payoff identity, continuous-time transfer, common-path inference, finite-observation allowance, and now the paired-policy transfer. Those tools are largely agnostic about the candidate generator.

R15 also retains an evidentiary classification issue. The dimension-10 HJB superiority claim is not a fully prospectively frozen result. The original interval crossed zero; after inspecting the original transfer width, the author developed a sharper deterministic transfer theorem and applied it to the same observations. If that theorem is correct and uniform, using it need not invalidate coverage. The manuscript discloses the sequence and preserves the original interval. But the resulting dimension-10 sign should be described as a transparent post-freeze analytical reanalysis and independently replicated with the refined transfer fixed in advance, not presented on the same footing as the original dimension-50 confirmation.

I therefore do not recommend another ordinary revision of the cumulative submission. I would take seriously a new paper that chooses one of two centers. The first is a method-agnostic paper on verified policy improvement and decision-grade numerical error accounting. The second is an NBO paper built around a problem and prospective comparison in which reusable continuation learning demonstrably improves economic accuracy or total work relative to Raw, DPO, a well-tuned HJB procedure, and suitable classical alternatives.

## 2. What R15 successfully repairs

The negative recommendation should not obscure the quality and extent of the revision.

### 2.1 The new comparison is prospectively organized and fully executed

The main experiment protocol was frozen before confirmatory execution. It specifies dimensions 10 and 50, four methods, sixteen deterministic complete streams, three work checkpoints, the stopping rule, fresh online banks, an independent final bank, the familywise error allocation, a payoff margin of $10^{-4}$, and complete work accounting. All 128 method-by-dimension-by-stream executions are retained, and all returned fitted policies rather than fallbacks.

This is a meaningful improvement over retrospective collections of favorable training runs. The finite method distribution is artificial and narrow, as discussed below, but it is explicit and fully enumerated.

### 2.2 The method-level estimand is now well defined

R15 distinguishes policy-conditional simulation uncertainty from the declared finite distribution over training streams. The method gain and method contrast average over all sixteen streams. Since the complete finite distribution is executed, there is no sampling error from selecting a subset of those streams. The remaining probability statement concerns independent payoff simulations and numerical transfer.

The paper is also explicit that this is not inference to all possible initializations, random-number streams, hardware environments, or future reruns. That limitation is scientifically appropriate.

### 2.3 Direct method differences use the correct common-path object

NBO-minus-Raw, NBO-minus-DPO, and NBO-minus-HJB differences are formed on common initial profiles and innovations. The shared schedule cancels. The comparison is not constructed by subtracting separate lower bounds. The fallback cases have explicit rules. This is the right estimand.

The pooled empirical-Bernstein construction is also stated for independent, potentially nonidentically distributed observations. I found no immediate inconsistency in the statistical proposition under its declared range, transfer, and independence assumptions.

### 2.4 The continuous-time transfer has been sharpened for paired policies

The new paired-policy transfer recognizes that two held controllers are driven by the same economic innovations and that the payoff difference can be bounded directly. It preserves the original observations, clipping rule, stopping decisions, and confidence event. The original intervals remain visible.

At a high level, the coupling and line-by-line error decomposition are plausible, and I found no immediate algebraic contradiction in the statement. The exact constants and interval implementation deserve independent mathematical audit because the new theorem determines the dimension-10 sign, but the idea is valuable independently of NBO.

### 2.5 The critic mechanism has been made operational rather than rhetorical

R15 no longer substitutes training-state MSE into a welfare theorem. It defines a finite Bellman problem, evaluates continuation error along action bridges under the returned candidate's occupation law, uses independent continuation banks, records actor suboptimality, and transfers the finite-step account to the continuous economy.

This closes the procedural chain that was missing at R14. Just as importantly, the author reports the unfavorable result: the sufficient continuous-economy mechanism lower bounds are negative and the critic-versus-Raw risk comparisons are inconclusive. That is exemplary disclosure.

### 2.6 The work account is substantially more complete

The parent clock covers process launch through durable evidence, including initialization, fitting, checkpoint I/O, failed checks, successful checks, weight reload, final verification, and output. Simulator transitions, derivative rows, optimizer updates, search iterations, memory, and CPU seconds are retained. Unattained runs receive infinite work-to-target and remain in restricted-mean summaries.

This makes it possible to see that Raw is cheaper than NBO, DPO is more expensive at the dimension-50 target, and the declared HJB procedure is dominated by derivative and online action-search work.

### 2.7 The scalar and observation studies now have clearer numerical roles

The scalar study separately exposes algebraic residuals, mesh sensitivity, domain sensitivity, action restriction, common-path deployment, and classical work. It does not use the neural critic as its reference. The finding that classical policies outperform the neural policies is preserved.

The finite-observation study also gives an operational interpretation to the controller. It identifies when exact or noisy measured-state implementation retains a positive lower gain and when sensing error exhausts the margin. These results are useful qualifications rather than universal implementation claims.

### 2.8 Reproducibility and provenance are unusually strong

The final audit reports a complete publication snapshot, exact replay of the editorial integration, preservation of the historical blobs, source and evidence roles for the main, mechanism, and observation studies, and clean compilation of the 56-page article, 145-page supplement, and 11-page response. The audit explicitly does not require favorable numerical signs.

On provenance, disclosure, and immutable evidence, this project is stronger than most computational submissions.

## 3. Blocking concerns

### B1. The learned Bellman critic still has no demonstrated incremental economic value

This remains the central issue.

The method-level schedule gains are approximately

- dimension 10: NBO `0.001268`, Raw `0.001267`, DPO `0.001262`;
- dimension 50: NBO `0.001342`, Raw `0.001343`, DPO `0.001347`.

The refined NBO-minus-Raw and NBO-minus-DPO intervals all contain zero and extend beyond the $\pm10^{-4}$ practical-equivalence band. They therefore establish neither superiority, noninferiority at the declared margin, nor practical equivalence. In dimension 50, Raw attains the same online target in every stream and has lower mean complete work, approximately 346.22 seconds versus 357.80 seconds for NBO.

The mechanism evidence does not rescue the critic claim. In dimension 10 the point estimate of critic risk is smaller than Raw, while in dimension 50 it is larger; both risk contrasts have enormous intervals. The sufficient mechanism welfare lower bounds are approximately `-0.006778` and `-0.004800`, far below zero. These are not merely failures to reject. They show that the paper's operational error account is too loose to attribute the verified policy gain to the critic.

The positive schedule certificates apply to policies generated by NBO, Raw, and DPO. The paired-policy verifier is method agnostic. The Bellman-bridge theorem applies to any fitted continuation predictor. Consequently, the positive theorem chain and the positive schedule comparisons do not isolate the learned NBO block.

A paper titled “Neural Bellman Operators” needs at least one economically relevant setting in which the learned continuation object is shown to improve payoff, verified decision quality, or total work relative to a credible critic-free alternative. R15 still does not supply that setting.

### B2. The neural-HJB result is specific to one difficult and insufficiently validated implementation

R15's strongest positive comparison is against the declared neural-HJB procedure. That procedure is useful as a contribution-isolating baseline, but it is not yet a sufficiently strong representative of direct neural HJB computation.

The HJB critic is trained with the product of two independent Hutchinson residual estimates. This is an unbiased device for the squared residual under the stated independence argument, but it is high variance and can yield negative batch losses. The canonical HJB method receives 100, 200, and 400 additional Adam updates at the three stages. NBO's continuation block receives 1,200 Adam updates per stage, a substantial L-BFGS phase, separate time-only updates, and actor updates. The methods do not have equal numerical work, which is acceptable when total work is reported, but the paper does not establish that the HJB fit is near the best attainable fit at its observed work.

More importantly, the HJB output has no independent value-error or residual-convergence account comparable to the scalar Howard diagnostic. The training loss falls in the representative raw shard I inspected, but that does not show convergence of the policy or value. There are no prospective comparisons with exact traces where feasible, more probes, alternative collocation distributions, L-BFGS or second-order optimization, multiple learning-rate schedules, or an actor distilled from the fitted HJB critic. Deployment performs a critic gradient and forty-four scalar bisections at every decision, creating billions of recorded search iterations. That is a legitimate implementation choice, but it is not the only reasonable way to deploy a direct HJB approximation.

The result therefore supports the narrow statement that NBO beats this frozen residual-fitting and online-greedy procedure in the pilot-selected high-volatility experiment. It does not establish that NBO is preferable to direct neural HJB methods as a class, or that maintaining a separate actor is the source of the gain.

### B3. The dimension-10 superiority claim is a post-freeze analytical reanalysis

Under the original registered transfer account, the dimension-10 NBO-minus-HJB interval is approximately `[-0.000073, 0.000663]`, so neither statistical nor material superiority is established.

After the experiment source was frozen and the original transfer width was inspected, the author developed a sharper common-innovation transfer. Applying it to the same observations gives approximately `[0.000179, 0.000411]`, which clears the prespecified $10^{-4}$ margin.

A valid deterministic theorem can sharpen an existing confidence interval without spending additional probability, and the manuscript transparently retains both intervals. My concern is evidentiary classification, not an assertion that the refined interval is automatically invalid. The theorem and its implementation were motivated by the realized obstacle to signing the ten-dimensional result. They have not yet been tested on a new confirmation bank or a new calibration with the refinement frozen in advance.

The abstract, introduction, and conclusion should therefore distinguish:

1. the prospectively supported dimension-50 result under the original account;
2. the transparent post-freeze analytical refinement of the dimension-10 result; and
3. any future independent replication with the refined theorem prospectively fixed.

Because the dimension-10 sign depends on a new 21-page transfer argument and interval implementation, an independent proof audit and fresh replication are especially important.

### B4. The finite method distribution and calibration have narrow external scope

The sixteen streams are a complete, prospectively declared finite population. This is a coherent estimand. It is also an author-chosen finite population, not a sample from a natural distribution over training randomness.

The high-volatility calibration, split critic, long Sobolev optimization, and generic architecture were selected after repeated inspection of exploratory diagnostic banks. The pilots are properly archived and excluded from confirmation. Nevertheless, the confirmatory conclusion is conditional on a design selected to create a setting in which the revised critic looked promising. The original calibration had not shown an advantage over a strong Raw estimator.

R15 therefore supports a local claim: after exploration, a fixed NBO configuration performs well over sixteen specified streams in one high-volatility capital calibration. It does not support a claim about robustness over economically relevant calibrations, architectures, dimensions, horizons, utility specifications, or generic training randomness.

For an Econometrica method contribution, at least one of the following is needed:

- a second independently chosen economic calibration;
- a prespecified calibration family with heterogeneity in primitives;
- a problem outside the capital example in which continuation reuse is essential;
- or a theoretical property that explains where NBO should outperform Raw and DPO and is verified empirically.

### B5. The high-dimensional result is conservative safe improvement, not an accurate HJB solution

The new full-adapted-class regret upper bounds are approximately 0.025971 and 0.036843, while the verified method gains are about 0.0013. These bounds are legitimate, but they are too wide to establish near-optimality or high-dimensional HJB accuracy at the paper's $10^{-4}$ decision margin.

The scalar calculation supplies a sharper numerical reference, but its evidence points in a different direction. The finest classical policy has population gain about `7.819e-4`, compared with `7.412e-4` for the frozen NBO policy and `7.065e-4` for DPO. The classical policy is better at all three reported initial states and its measured action evaluation is faster. The NBO-minus-DPO ordering reverses at one initial state.

The manuscript states these limitations, but the overall breadth still invites the interpretation that NBO is an accurate general high-dimensional HJB solver. The established high-dimensional claim is narrower: a feasible candidate policy improves on an analytical schedule under a conservative model-specific certificate, and one specified direct-HJB candidate generator performs worse.

### B6. The work comparison does not identify an NBO efficiency advantage

R15 now has credible complete clocks. Those clocks do not show that NBO is the preferred candidate generator.

In dimension 50, mean complete work is about 346.22 seconds for Raw, 357.80 for NBO, 596.94 for DPO, and 1690.10 for HJB. Raw is both cheaper and statistically indistinguishable from NBO. In dimension 10, no method attains the online target and Raw is again cheaper. NBO's advantage over DPO at the dimension-50 target is useful, but it does not isolate the critic because Raw performs at least as well in the same design.

The HJB work result is also dominated by implementation choices: approximately 67.2 million first-derivative rows and 2.96 billion action-search iterations on average, compared with no online search for the materialized actors. An actor distilled from the HJB critic, a faster closed-form or vectorized root solve, or a different HJB training/deployment split could materially change this comparison.

The appropriate conclusion is that the declared NBO procedure is more efficient than the declared DPO and HJB procedures at one target in dimension 50, while Raw remains the preferred procedure in the reported work-payoff frontier. That does not support a broad NBO efficiency claim.

### B7. The operational mechanism account is scientifically valuable but does not support the paper's causal narrative

The finite Bellman bridge is one of R15's most interesting theoretical additions. It measures continuation prediction error where the candidate uses it, rather than at arbitrary training states. It also separates predicted improvement, action size, continuation error, and actor gap.

The executed account, however, is far too imprecise to establish a positive mechanism gain. For example, the continuation-error and actor-gap intervals are orders of magnitude wider than their means. The costate upper bound and holding/transfer terms drive the welfare lower bound negative. The critic-versus-Raw risk interval is also far too wide to rank the estimators.

The paper correctly reports this. It should go further and make the negative mechanism result central to interpretation. At present, the title and broad framing still suggest that Bellman evaluation is the established source of the policy gains. The evidence establishes only that the NBO package produced a good policy, not that critic reuse caused the gain or justified its cost.

### B8. The manuscript remains too broad relative to the result

The main article is shorter, but the publication object is still 56 pages plus a 145-page supplement. It covers differential and monotone Bellman formulations, viscosity selection, recursive utility, endogenous preference adjustment, temporal selves, dynamic games, stochastic trace methods, high-dimensional capital, paired diffusion transfer, finite observations, and management fees.

The new method-level comparison, mechanism execution, and observation evidence concern the capital economy. The inherited preference, temporal-self, and game applications do not receive comparable modern baselines, finite-method inference, mechanism closure, or complete work comparisons. Their continued prominence makes the paper appear to establish a broad platform whose decisive evidence is much narrower.

The strongest coherent paper is now visible:

1. a continuous-time capital problem with a feasible analytical anchor;
2. policy-specific and paired-policy continuous-time verification;
3. a prospectively organized comparison of candidate generators;
4. a complete work-to-certified-gain account;
5. an honest negative mechanism result; and
6. a finite-observation implementation study.

That paper could be shorter, clearer, and more influential than the cumulative manuscript. The other economic applications could remain in an archival companion or separate papers.

## 4. Major comments and required changes

### M1. Choose a single publication claim

There are again two credible paths.

**Verification-centered path.** Make the policy-specific and paired-policy certificates the contribution. Treat NBO, Raw, DPO, HJB, and classical methods as candidate generators feeding the same verifier. Report that Raw is the cheapest successful generator in the main experiment, NBO is competitive, DPO is more expensive, and the declared HJB procedure underperforms. The negative critic mechanism becomes an informative result.

**NBO-centered path.** Identify a setting in which the critic is demonstrably valuable. The learned continuation should beat Raw or reduce total work at a common verified economic target. This requires a prospective comparison against strong alternatives and a positive mechanism or amortization account.

The current manuscript continues to use the first path's theorems to support the second path's title.

### M2. Strengthen the HJB comparator before making it the positive centerpiece

The revised baseline study should include, where feasible:

- exact Hessian trace in dimension 10;
- additional Hutchinson probe counts and variance diagnostics;
- Adam and L-BFGS or comparable optimizer variants;
- matched occupation-law and broader collocation designs;
- convergence curves for independent residual, value, policy, and payoff diagnostics;
- a materialized or distilled actor;
- an optimized action solver;
- wider training budgets and a stopping criterion tied to an independent HJB diagnostic; and
- a frozen baseline-selection protocol that does not use final payoff.

The paper need not show NBO wins every variant. It must show that the reported comparison is not driven by an obviously weak residual implementation.

### M3. Prospectively replicate the paired-transfer result

Freeze the new paired-transfer theorem, constants, interval code, and all comparison decisions before a fresh experiment. Use new policy streams or, at minimum, a completely new confirmation bank whose existence was not part of the original reanalysis. A second calibration would be preferable.

Report the original, refined-on-old-data, and prospectively refined intervals separately. The dimension-50 original result can remain the clean confirmatory result from R15.

### M4. Resolve the Raw comparison or change the protagonist

Raw is the most important comparator. It uses the same cached continuation labels and actor objective without fitting a reusable critic. It is cheaper and has indistinguishable payoff.

A new NBO-centered experiment should be designed around circumstances in which continuation reuse matters: many actor queries per fitted continuation, multiple policies or counterfactuals sharing the critic, expensive or unavailable raw derivatives, long horizons, or a state distribution where regression materially reduces variance. The paper should prespecify the economic payoff and total-work margin needed to justify critic fitting.

If no such setting is found, the honest conclusion is that Raw is the preferred generator in this problem and the paper should become verification centered.

### M5. Expand robustness over economic designs, not only random streams

Sixteen streams in one pilot-selected calibration do not substitute for economic robustness. Prespecify a small family varying volatility, coupling, horizon, terminal dispersion, action radius, and initial-state heterogeneity. Include at least one design not used in method development.

The target should be a map from economic structure to method performance, not another large number of seeds at one point.

### M6. Tighten or relabel the high-dimensional accuracy claim

The manuscript should consistently use “verified improvement over the analytical schedule” for the high-dimensional result. It should not suggest near-optimality or accurate HJB solution unless the regret interval is materially tightened.

Potential routes include a stronger analytical anchor, lower/upper value bounds, nested relaxations, a controlled low-rank approximation, or an independent high-dimensional reference on a restricted instance. Otherwise the broad regret bound should be displayed beside every high-dimensional gain.

### M7. Improve the mechanism experiment's precision

The mechanism account currently spends substantial range on clipping and representation allowances. The author should investigate variance-reduced bridge statistics, sharper analytical ranges, stratification by time and state, more independent continuation banks, and direct occupation weighting.

Most importantly, precompute a power calculation in economic units. A mechanism experiment whose interval is orders of magnitude wider than the policy difference cannot adjudicate the proposed explanation.

### M8. Present the post-freeze refinement with a stronger evidentiary label

The current disclosure is better than suppressing the original interval, but the main narrative still says that the complete experiment establishes material HJB superiority in both dimensions. That formulation blurs prospective and post-freeze evidence.

The abstract and conclusion should state that dimension 50 is positive under the original registered account, whereas dimension 10 becomes positive under a subsequently developed deterministic refinement. A fresh prospective replication would remove this concern.

### M9. Reduce and reorganize the manuscript

A focused main article should contain one algorithmic specification, one capital model, one verification theorem chain, one method experiment, one mechanism experiment, one observation result, and the central tables. Historical applications and revision genealogy should move to an archive.

The supplement can retain proofs and complete machine-readable tables, but it should not be a 145-page cumulative publication layer. Econometrica readers should not need the R6–R15 history to identify the theorem and evidence supporting the current claim.

### M10. Clarify a few evidence semantics

- “HJB superiority” should always be qualified as superiority over the declared implementation.
- “Method distribution” should be called the declared sixteen-stream finite distribution, not a generic optimizer distribution.
- “Confirmed” should distinguish original prospective confirmation from post-freeze deterministic reanalysis.
- Online target attainment and independent final certification should remain separate.
- Pointwise policy certification, method-level averaging, and broad adapted-class regret should never share the same shorthand.
- The high-volatility R15 study and original-volatility scalar and observation studies should be visibly separated in every summary table.

## 5. A focused publishable design

### 5.1 Verified policy improvement

The most credible new paper would center on a candidate-generator-neutral verifier for a continuous-time economic control problem.

The contribution would be:

- a feasible analytical anchor;
- a policy-specific payoff identity;
- a network-derivative-free diffusion transfer;
- a direct paired-policy transfer using common innovations;
- simultaneous policy and finite-method comparisons;
- complete work-to-certified-target accounting;
- finite-observation implementation allowances; and
- an empirical finding that several candidate generators improve the anchor, with Raw cheapest and the declared HJB method weakest in the selected design.

This is a coherent contribution to reliable computational economics. It does not require claiming that the critic is superior.

### 5.2 Neural Bellman Operators

A separate NBO paper should begin from an economic problem in which continuation evaluation can be amortized and raw continuation derivatives are expensive or unavailable. The protocol should prospectively freeze:

- a natural training-randomness distribution;
- multiple economic calibrations;
- strong HJB, DPO, Raw, and classical baselines;
- a complete work metric;
- a verified economic target;
- a positive contribution margin; and
- the mechanism assessment.

The paper should then show that critic reuse improves either the verified payoff frontier or total work, and that the occupation-law mechanism account is consistent with the observed gain.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R15 snapshot.

1. **Latest-revision identity.** I enumerated the remote Econometrica revision branches twice. R15 is the latest formal revision; no R16 branch exists at the time of review.
2. **Source identity.** I pinned the publication commit, tree, root manuscript and supplement blobs, and the separate source/evidence commits for the main experiment, mechanism experiment, and observation experiment.
3. **Publication audit.** I inspected the final audit and compilation records. They report a complete snapshot, 8,652 preserved historical blobs, 3,398 payload files, clean editorial replay, and clean compilation of the 56-page article, 145-page supplement, and 11-page response.
4. **Protocol chronology.** I checked the frozen main protocol and exploratory archive. The sixteen streams, methods, margins, work checkpoints, and inference family were fixed before confirmatory execution. The high-volatility design and revised critic configuration were selected after exploratory diagnostics, which are retained and explicitly nonconfirmatory.
5. **Aggregate result replay.** I independently parsed the committed method, work, operation, paired-transfer, mechanism, scalar, and observation tables and checked the principal signs and comparisons reported above.
6. **Original execution shard.** I downloaded the original GitHub Actions artifact for dimension 50, stream seed `964082955`, artifact id `11301120232`. Its ZIP SHA-256 is `59f286008800b3453d680acdceea76a0116ea403d717cfecfbfbd15edb53160b`, matching the GitHub artifact digest.
7. **Raw policy outcomes.** In that shard, final-confirmation schedule gains are approximately:
   - NBO: `0.0013461844`, interval `[0.0005637746, 0.0021285943]`;
   - Raw: `0.0013479368`, interval `[0.0005655597, 0.0021303140]`;
   - DPO: `0.0013467170`, interval `[0.0005644715, 0.0021289625]`;
   - neural HJB: `-0.0003319221`, interval `[-0.0011648975, 0.0005010533]`.
8. **Raw work outcomes.** The same shard records approximately 382.23 seconds for Raw, 394.00 for NBO, 639.99 for DPO, and 1795.63 for HJB before final result write. HJB records 2,956,732,416 action-search iterations and 67.2 million first-derivative rows over the complete procedure.
9. **HJB fit diagnostic.** The HJB sampled objective in the representative shard declines across stages, but the shard contains no independent certificate that the trained high-dimensional value or policy is converged. I therefore do not interpret the poor HJB payoff as evidence against all direct neural-HJB implementations.
10. **Mathematical scope.** I read the new finite Bellman bridge and paired-transfer statements and their proof structure. I found no immediate algebraic contradiction at the level of this referee review. I did not independently formalize every interval constant or rerun the complete proof-generating arithmetic.
11. **Execution limitation.** I did not rerun all 128 training jobs. A rerun would use a different timing environment and would not reproduce the declared complete streams' original wall-clock realization. I instead checked the immutable source/evidence record, aggregate tables, and one original raw artifact.

The review directory includes a standard-library audit script, its machine-readable result, and a manifest pinning the reviewed scope and limitations.

## 7. Recommendation

R15 deserves substantial credit. It is a complete, reproducible, and unusually candid computational revision. It fixes the method-level estimand, executes every declared stream, adds a real direct-HJB comparator, records complete work, operationalizes the candidate-occupation mechanism, strengthens the scalar benchmark, and develops a potentially useful paired-policy transfer. The author reports negative mechanism results, unresolved Raw/DPO rankings, loose regret bounds, classical scalar superiority, and sensing failures rather than relabeling them as successes.

The remaining problem is substantive. The paper still does not show that the learned Bellman critic improves economic payoff or total work relative to the cheaper Raw alternative. The positive HJB comparison is against one particular, expensive, insufficiently validated residual implementation in a pilot-selected calibration. The dimension-10 sign depends on a post-freeze analytical refinement. The high-dimensional result is conservative improvement rather than accurate solution, and the broad inherited scope remains disproportionate to the evidence.

I therefore recommend **rejection in the present form and no additional ordinary revision of this cumulative submission**. A new, sharply focused paper on verified policy improvement could be valuable. A new NBO paper could also merit serious review if it prospectively demonstrates the incremental value of reusable continuation learning against strong and well-tuned alternatives.
