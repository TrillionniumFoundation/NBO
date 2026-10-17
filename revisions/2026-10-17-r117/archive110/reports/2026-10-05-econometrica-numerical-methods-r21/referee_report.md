# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r21-2026-10-05`  
**Pinned revision commit:** `278916666b32e03081ffe8d4aa05d9766c259b85`  
**Pinned revision tree:** `cd20e18b1b91a79568ccfc312122451f39562bab`  
**Pinned manuscript blob:** `27419f19181e3c4f1476048b24c6b497f4365efe` (`revisions/2026-10-05-r21/ECTA.tex`)  
**Pinned supplement blob:** `7182f0b56fda0f9109b0104fc98c3b4981f825d4` (`revisions/2026-10-05-r21/supp.tex`)  
**Pinned applications blob:** `d69f550ce05e4405b770744178d053d1d532b7dc` (`revisions/2026-10-05-r21/applications.tex`)  
**Report date:** 5 October 2026  
**Recommendation:** **Reject in the present form and do not continue the cumulative manuscript through another ordinary revision round. I would seriously consider a new, much shorter submission centered either on certified continuation services or on an application in which a neural continuation has a demonstrated work-to-accuracy advantage over simulation and conventional surrogates.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R21 is a substantial and professionally executed response to the R18 report. It resolves two objections that were central in the preceding round.

First, the paper no longer studies reuse only when the future is literally unchanged. The frozen R20 experiment changes subsequent withdrawal, production coupling, and future-payoff weights. It executes 168 complete services and 840 future-specific outcomes, preserves every failed reuse check, and compares unchanged reuse, check-and-refresh, fresh refitting, two conventional continuation regressions, cached sample-average optimization, and full-support enumeration. This is a legitimate prospective design rather than a retrospective relabeling of selected successful cells.

Second, the revision supplies the missing mathematical statement connecting local decisions to a multiperiod policy target. The new composition theorem is correct under its stated assumptions: if every full-action local advantage is uniformly bounded against the implemented policy's own continuation on invariant domains, then order preservation and continuation Lipschitz constants propagate those bounds backward. The state-dependent envelope and the class/value/implementation bridge correctly display the additional assumptions needed for a continuous-economy or strategic conclusion. The paper also gives a valid allocation formula for one specified sufficient-cost account.

The source and evidence record is unusually strong. The final native-publication artifact is source-bound; its 210-file manifest checks exactly; the new R21 test suite passes all 22 tests; the inherited R19 suite passes 32 tests with two package-scope skips; the frozen R20 execution was committed from a source-freeze preceding the observations; and the publication audit records exact replay of 984 attempted certificates, 120 additional zero-charge certificates, and 319,062 task actions. I independently parsed the committed aggregate tables and inspected the original R20 execution package.

The remaining problem is substantive. R21 has not demonstrated that the distinctive neural continuation is the numerical contribution responsible for the successful services.

The check-and-refresh NBO procedure certifies all 120 future-specific outcomes, but fresh NBO refitting also certifies all 120 and is cheaper in every one of the eight dimension-by-volume cells. The check-and-refresh cost is approximately 1.39 to 1.59 times the fresh-refit cost. Every quadratic, radial-basis, cached-SAA, and enumerated service also certifies every future. Among procedures that certify all five futures in every stream, cached SAA has the lowest recorded service cost in all eight cells. In the preceding fixed-future experiment, NBO is the least-cost fully certified procedure in only one of twelve cells. At 1,024 tasks, the conventional or simulation procedures also have lower absolute, centered, and own-action continuation risks in every dimension-by-future comparison; NBO has the lowest three-action loss in only one of ten such comparisons.

The new signed comparative statics are valid for the declared finite laws. The NBO action certificates establish that stronger future production and greater future valuation lower mean optimal current withdrawal. This is a real economic statement. But it is not an economic statement that requires NBO. Full-support enumeration gives the same target with intervals many orders of magnitude narrower and, in every reported future-service cell, lower recorded cost than check-and-refresh NBO. The experiment therefore establishes that NBO can return certified decisions, not that it unlocks the counterfactual or improves the numerical frontier.

The composition theorem likewise clarifies the route to a full policy certificate but is not instantiated for the paper's broad applications. The finite experiments certify mean loss over stored catalogues for a current scalar action. They do not compute uniform own-policy local advantages over the state domains required by the theorem, nor the class-approximation, value-transfer, and implementation allowances required by the continuous-economy bridge. Recursive utility, endogenous preferences, temporal selves, and games remain economically distinct applications, but the R21 work-to-accuracy and refresh evidence is not carried through those models.

Thus the strongest supported proposition is narrower than the title and cumulative scope:

> For a short-horizon finite-law capital service with a continuous scalar current action, several learned, conventional, and simulation procedures can be equipped with true-objective certificates; continuation changes can be detected and refreshed; and the resulting decisions can support finite-law comparative statics.

That proposition is useful. It does not yet constitute an Econometrica-level demonstration that Neural Bellman Operators are a broadly advantageous numerical method. The article is 51 pages, the technical supplement 232 pages, and the applications companion 48 pages. Reorganization has improved readability, but the 331-page scientific package still asks one stylized finite-law capital exercise to support a platform covering many substantially different economic problems.

I therefore recommend rejection of the present cumulative manuscript. The work contains a potentially publishable core, but it should be rewritten as a new paper with a single central estimand, a much smaller theorem-and-evidence chain, and a numerical setting in which the chosen candidate generator is needed rather than merely certifiable.

## 2. What R21 successfully repairs

### 2.1 Future-change reuse is now genuinely tested

The five future regimes alter future policy, production technology, or payoff valuation while holding the current decision map fixed. Unchanged continuation reuse succeeds for the anchor and the two future-withdrawal changes but fails its certificate for production and valuation changes. The adaptive rule refreshes exactly those forty-eight outcomes and all refreshes succeed. This is an informative use of certification: a failed check is retained as a failure to certify, not misreported as evidence of actual excessive loss.

The chronology is credible. The future-change source was frozen before execution, the execution workflow preserved all service records, and R21 labels its new tables and response bands as deterministic post-execution analyses rather than new independent observations.

### 2.2 The stopping target is economically meaningful and method-neutral

Every returned scalar action is evaluated against the true finite-law objective over the full continuous scalar interval. The residual and strong-concavity account gives a valid upper bound on mean foregone transformed welfare. Fitting loss, surrogate curvature, and a finite candidate menu are not substituted for the economic target.

The first-success protocol charges initialization, fitting or cache construction, action queries, failed and successful checks, and durable writes. The paper also retains common startup and post-stop diagnostic work rather than allocating those costs retrospectively to a favored method.

### 2.3 The composition theorem states the missing policy link correctly

The local advantage is evaluated against the implemented policy's own continuation. This is essential. A certificate relative to an unrelated anchor continuation would not compose into a policy guarantee without charging the continuation discrepancy.

The proof by backward induction is straightforward and correct under order preservation, invariant domains, and uniform continuation Lipschitz constants. The paper correctly warns that states visited only by the fitted policy are insufficient because a profitable deviation can reach unvisited states. The state-dependent envelope therefore takes a supremum over admissible transitions.

The continuous-economy bridge also preserves the right decomposition: class approximation, value transfer, local decision allowances, and implementation loss are separate quantities. None is inferred from a finite query catalogue.

### 2.4 The comparative-static bands use valid decision certificates

Strong concavity converts an outward directional-residual bound into an interval containing the finite-law optimum. Averaging paired optimum intervals across the common task catalogue gives valid response bands without an independence assumption. All four NBO upper endpoints for the production and valuation changes are negative.

The paper is appropriately restrained about interpretation. These are counterfactual comparative statics in the specified capital economy, not estimates of an observed reform or confidence intervals over an unobserved population of training streams.

### 2.5 Adverse numerical results remain visible

R21 does not manufacture a favorable amortization frontier. It states that check-and-refresh NBO is more expensive than fresh NBO refitting in every displayed cell. It retains all forty-eight failed unchanged-reuse certificates, the competitive conventional regressions, cached SAA and enumeration, the earlier cheaper Raw clocks, unresolved policy comparisons, and nonpositive mechanism bounds.

This candor is a major strength and makes the scientific disagreement below one of contribution and scope rather than reliability.

### 2.6 The publication and evidence package is exceptionally well organized

The submitted object contains a native Econometrica-class article, technical supplement, applications companion, response, release audit, preservation map, source identities, generated tables, and replay code. Historical sections are relocated rather than silently deleted. The final audit records 129 inherited source components and 408 inherited labels, with 428 labels in the publication package.

## 3. Blocking concerns

### B1. The future-change experiment does not establish an NBO work-to-accuracy advantage

This is the central numerical concern.

All accuracy-qualified methods succeed. The largest reported mean scalar-regret upper bounds are approximately

- `5.29e-6` for check-and-refresh NBO;
- `1.22e-5` for fresh-refit NBO;
- `5.44e-5` for adaptive quadratic regression;
- `3.57e-6` for adaptive radial-basis regression;
- `3.66e-6` for cached SAA; and
- numerical zero for full-support enumeration.

The tolerance is `1e-4`, so these differences do not change the declared success decision.

At the same time, check-and-refresh NBO is more expensive than fresh NBO in all eight cells. Cached SAA is the least-cost fully certified service in all eight. At 1,024 tasks per future, for example, the dimension-fifty mean costs are approximately 59.20 seconds for adaptive NBO, 42.66 for fresh NBO, 42.57 for SAA, and 50.12 for enumeration. The registered adaptive rule pays for an anchor, failed reuse checks, and higher-budget refreshes, whereas fresh NBO succeeds at its lower budget in every future.

This is a valuable negative result about one refresh policy. It is not evidence that the NBO architecture produces an amortization advantage.

### B2. The successful economic contrast is not unlocked by NBO

The NBO action bands establish the correct sign of the production and valuation responses. However, full-support enumeration independently computes the finite-law optimum at the same 1,024 tasks. Its difference intervals are extremely narrow and lie inside the wider NBO bands. Enumeration is also cheaper than adaptive NBO in every reported service cell.

The paper can legitimately say that NBO decisions are accurate enough to certify these signs. It cannot use the signs as evidence that a neural continuation is necessary or numerically preferable. A top-journal method paper should demonstrate either a counterfactual that strong alternatives cannot feasibly obtain or a material reduction in total work at a common economic accuracy. R21 shows neither for this exercise.

### B3. The composition theorem is a conditional bridge, not an executed full-policy certificate

Theorem R21 requires full-action local advantages, against the implemented policy's own continuation, uniformly over invariant state domains and on a common event. Equation R21's continuous-economy bridge additionally requires a policy-class approximation gap, uniform value-transfer error, and implementation allowance.

The finite experiments instead certify mean scalar-action loss over stored task catalogues. They do not provide the uniform state coverage, vector-action deviations, full adapted-control comparison, class approximation, or value-transfer constants needed to instantiate the theorem. The manuscript says this explicitly, which is correct; but then the theorem does not convert the new empirical evidence into a policy guarantee for the broad models advertised in the paper.

The result is best viewed as a useful organizing lemma stating what a future application must prove. It is not itself evidence that R21 has solved the policy-accuracy problem for recursive utility, temporal selves, or games.

### B4. The experimental decision problem remains numerically narrow

The future-change economy has four dates, sixteen stored innovation atoms, a uniform scalar current action, and a future policy fixed exogenously in each regime. State dimension ten or fifty does not by itself make the decision problem a high-dimensional action or full dynamic-control problem. Full-support enumeration is feasible and competitive precisely because the stochastic law and current action problem are small.

This setting is useful for exact auditing and mechanism separation, but it is favorable to every reasonable surrogate. It does not show how NBO performs when the action is high dimensional, the continuation cannot be enumerated, the horizon is long, state coverage is difficult, or future policy must itself be reoptimized.

### B5. The analytical amortization class is not specific to the trained neural procedure

The explicit work-advantage corollary assumes a fixed finite feature dictionary, full-rank least squares, a leverage bound, and a finite query family. The paper correctly observes that the feature map may be neural or conventional and that the result does not certify the jointly trained network used in the experiment.

Consequently, the theorem establishes an amortization principle for reusable regression, not a numerical property of NBO. The experiment's conventional quadratic and radial-basis regressions often equal or improve on NBO in accuracy, risk, and cost, exactly as the theorem permits.

### B6. The evidence does not support a method-level reliability statement

The new design uses three fixed fitting/cache streams and deterministic finite task catalogues. The certificates validly describe the returned services. The envelopes over the three streams are not confidence intervals for a population of future training runs, and the task catalogue is not an estimated population of economic requests.

A method paper should define a method-level estimand: expected work to a certified threshold over a prespecified training-randomness distribution, probability of successful certification, or a deterministic worst-case guarantee over a declared class. R21 largely reports finite-object success counts and average clocks. Those are informative engineering records but do not establish robust performance of the method beyond the executed objects.

### B7. The broad economic applications still do not receive the decisive numerical test

Recursive utility, endogenous preference adjustment, temporal selves, and strategic games remain in the title-level narrative and the 48-page applications companion. Yet the new prospective stopping, future-change, symmetric risk, and work-to-tolerance comparisons are carried out only in the finite capital service.

The applications retain their own models and verification accounts, but they do not demonstrate that reusable neural continuation learning improves accuracy or total work relative to strong alternatives. Nor does R21 instantiate the new composition theorem with their utility-domain, equilibrium, or full-deviation constants. The breadth therefore remains asserted through a common architecture rather than supported by a common empirical contribution.

### B8. The cumulative scope remains disproportionate to the established result

The reorganization is better than the earlier branch genealogy, but the scientific package remains approximately 331 pages before the response: 51 pages of main text, 232 pages of technical supplement, and 48 pages of applications. It retains 129 inherited components and hundreds of labels accumulated over many revision cycles.

The strongest new result can be stated much more simply: true-objective certificates can govern reuse and refresh of continuation approximations in a finite repeated-decision service, and the registered adaptive NBO rule is accurate but not cost dominant. The cumulative manuscript obscures that result by continuing to present NBO as a general platform across problems with very different mathematical and computational obligations.

### B9. The economic counterfactual remains stylized and partly built into the primitives

The temporary-charge response has an analytically known direction under strict concavity. The production and valuation signs are less mechanical and the certified bands are useful, but the task distribution, future regimes, finite innovation law, and policy are all constructed inputs rather than empirically disciplined objects. The future policy is specified in each regime and is not endogenously reoptimized.

For Econometrica, a numerical method of this scope should either enable a substantively new economic result in a quantitatively serious model or establish a broadly useful computational advantage. The present counterfactual is a clean laboratory, not yet such a result.

## 4. Major comments and required changes for a new submission

### M1. Choose one paper

There are two coherent projects.

**Certified continuation services.** Center the paper on method-neutral true-objective certification, reuse checks, refresh decisions, and complete service cost. Present NBO, conventional regressions, SAA, and enumeration as candidate generators. The adverse result that fresh refitting or SAA can dominate adaptive reuse is scientifically useful.

**Neural Bellman Operators.** Move to an application in which continuation learning is essential and demonstrate that the neural continuation improves total work or attainable economic accuracy relative to conventional regression, simulation, direct policy optimization, and an appropriate HJB or approximate-policy-iteration baseline.

R21 still tries to be both papers.

### M2. Instantiate the composition theorem end to end

For one dynamic application, compute or rigorously enclose every term in the policy bound:

1. own-policy local advantages over the full action set;
2. uniform state-domain coverage or a valid distribution-shift account;
3. continuation Lipschitz weights;
4. class-approximation error;
5. value-transfer/discretization error; and
6. implementation error.

Then compare the resulting policy bound and complete work across candidate generators. Without such an instantiation, the composition theorem should be presented as scope conditions rather than as a completed bridge.

### M3. Use a setting where full-support enumeration and cheap SAA are not decisive

The current finite law is excellent for auditing but weak for demonstrating an advanced approximation method. A stronger design would increase stochastic support, horizon, action dimension, and state-coverage difficulty while retaining an independent economic verifier. The chosen problem should make continuation reuse economically natural and direct enumeration infeasible.

### M4. Define the method-level estimand and replication design in advance

Specify whether the target is expected total work, a success probability, a quantile of work to tolerance, or an equivalence/superiority probability under a declared distribution of training randomness and tasks. Choose the number of independent fits and final verification paths from an economically meaningful margin. Do not treat three fixed streams as a population inference.

### M5. Optimize the refresh policy before claiming amortization

The registered adaptive rule is dominated by fresh low-budget refitting in every cell. A new study should compare plausible refresh policies prospectively—for example, staged cheap checks, warm starts, uncertainty-triggered partial updates, and complete refits—while charging all failed checks. The policy must be frozen before outcomes and assessed at common economic accuracy.

### M6. Report contribution-isolating frontiers

At each query volume, report end-to-end time, simulation transitions, derivative evaluations, optimization updates, memory, failed checks, and verification work. Separate representation learning from action optimization. Compare NBO with a conventional surrogate of matched effective capacity, cached SAA, direct policy optimization, and a structure-exploiting dynamic-programming method wherever feasible.

### M7. Separate accuracy of a candidate from necessity of its construction method

The fact that an NBO action has a valid certificate establishes the action's accuracy, not the value of using NBO to obtain it. Every main result should state whether it concerns the verifier, the candidate, or the candidate-generation method. The abstract currently moves too quickly from “NBO certifies” to a method-level contribution when the same verifier certifies all major alternatives.

### M8. Clarify the future-policy interpretation

The changed-future regimes evaluate specified future policies. They are not equilibrium responses or reoptimized future plans. The comparative statics should consistently be described as current decisions conditional on those specified futures. A dynamic policy counterfactual would require solving and certifying the future policy in each regime.

### M9. Reduce the publication package radically

A new submission should have one notation system, one central theorem chain, one prospective numerical design, and one economic application. Historical studies can remain in a public replication archive. The main article should not require a 232-page supplement and a separate 48-page applications document to establish the central contribution.

### M10. Retain the current evidentiary standards

The source freeze, immutable records, adverse-outcome preservation, exact arithmetic replay, and distinction between finite-law, catalogue, scalar-interval, and continuous-control targets are exemplary. A focused new paper should preserve these standards.

## 5. A focused publishable design

A promising new paper could be titled along the lines of **“Certified Reuse and Refresh of Continuation Values in Dynamic Economic Decisions.”** Its main object would be a service that receives a changing economic future, checks whether an existing continuation remains decision-accurate, refreshes when necessary, and returns a certificate and complete bill.

The theory would contain only:

1. the centered decision-loss bound;
2. a transport or refresh condition;
3. the true-objective stopping certificate;
4. a correctly scoped multiperiod composition theorem; and
5. an explicit end-to-end cost criterion.

The experiment would prospectively compare neural and conventional continuation representations in a problem where direct enumeration is infeasible. The primary outcome would be total work to an economically meaningful policy-loss target over a prespecified distribution of future changes and training randomness. One substantive economic counterfactual would be solved with an independent verifier.

Such a paper could report that a neural representation wins only in a particular region. It need not establish universal superiority. It must, however, show a region in which its distinctive representation changes what can be computed or materially improves the work-to-accuracy frontier.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R21 snapshot.

1. **Branch and source identity.** I pinned the review to commit `278916666b32e03081ffe8d4aa05d9766c259b85` and tree `cd20e18b1b91a79568ccfc312122451f39562bab`, rather than reviewing a moving branch name.
2. **Final publication artifact.** I downloaded workflow artifact `nbo-r21-final-native-publication` from run `37285578847`. Its SHA-256 is `efa82cf6d24cd79a455ee0c2106803d836c68a80a3dd361e38463c6a7b1bc0ee`, matching GitHub's artifact digest. Its internal `REMOTE_COMMIT.txt` points to the pinned R21 commit.
3. **Publication manifest.** I independently recomputed every SHA-256 entry in `PUBLICATION_FILES_SHA256.json`: 210 of 210 files matched.
4. **R21 tests.** The source-bound publication package passes all 22 new R21 tests.
5. **Inherited tests.** The slim publication package passes 32 inherited R19 tests; two tests are skipped because the package deliberately omits the full raw economic record and editorial integration. The original records are separately pinned and inspected below.
6. **Frozen future-change execution.** The R20 source-freeze commit precedes the execution commit. I downloaded workflow artifact `nbo-r20-future-execution` from run `37270916186`; its SHA-256 is `11446376e2b57e5a49ca238b12a29fe3284e28fce35fd96c50c4b0f1a8348f90`, matching GitHub's artifact digest. The package contains the complete original service and regime records.
7. **Aggregate replay.** A separate standard-library script confirms 168 services, 840 regime outcomes, 72 of 120 reuse-only certifications, 120 of 120 adaptive and fresh-refit certifications, and forty-eight adaptive refreshes.
8. **Work frontier.** Among methods certifying all futures in every stream, cached SAA is least expensive in all eight future-change cells. Adaptive NBO is more expensive than fresh NBO in all eight, with adaptive/refit ratios ranging from approximately 1.388 to 1.590. In the preceding fixed-future study, NBO is least-cost among the fully certified displayed procedures in one of twelve cells.
9. **Risk diagnostics.** Across the ten dimension-by-future cells, NBO-adaptive is never the lowest absolute, centered, or own-action risk among NBO-adaptive, NBO-refit, quadratic, RBF, and SAA. It is lowest in one of ten three-action-loss comparisons. These are descriptive finite-design calculations, not population inference.
10. **Economic bands.** All four NBO response-band upper endpoints are negative. The exact full-support optimum-difference intervals are contained in those bands and are substantially narrower.
11. **Limitations.** I did not rerun the original fitting jobs or the repository's full 1,292-second arithmetic replay. A new training run would not reproduce the original measured clocks. I verified the source-bound publication, all publication hashes, the unit tests, the committed aggregate calculations, and the original R20 records; the exhaustive field-by-field certificate replay is taken from the committed release audit.

The review directory contains the deterministic checking script, its machine-readable output, and a manifest pinning the review scope.

## 7. Recommendation

R21 deserves substantial credit. It is complete, candid, mathematically cleaner, and far better organized than earlier revisions. It genuinely tests changing futures, gives a correct policy-composition statement, executes prospective stopping rules, preserves adverse outcomes, and derives valid finite-law economic response bands. I found no immediate contradiction in the new composition proof, allocation formula, or action-radius argument under their stated assumptions.

Nevertheless, the present manuscript still does not meet the standard for an Econometrica numerical-methods contribution. The distinctive adaptive NBO service is dominated by fresh NBO refitting in every reported future-change cell and by cached SAA on the complete accuracy-qualified cost frontier. Conventional and simulation procedures certify the same tasks. The new economic conclusion is available more sharply and cheaply by enumeration. The multiperiod theorem is conditional and is not instantiated for the paper's broad applications. The experimental target remains a short-horizon finite-law scalar decision, while the 331-page package continues to claim a general platform spanning much richer economic problems.

I therefore recommend **rejection in the present form and no further ordinary revision of this cumulative submission**. I encourage a new, sharply focused paper that preserves the project's exceptional evidentiary discipline while either treating candidate generation method-neutrally or demonstrating a setting in which a neural continuation materially improves attainable economic accuracy or total work.
