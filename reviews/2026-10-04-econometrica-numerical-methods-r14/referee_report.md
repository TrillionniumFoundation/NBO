# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r14-2026-10-04`  
**Pinned revision commit:** `f5021cefa71492babfcbfa580e0c984f59a9de26`  
**Pinned revision tree:** `5a0084d6ce3df47469125a7afe85c081cd29d94f`  
**Pinned manuscript blob:** `c13f5e951b47577f0cd4bcbb8b3d003e92e6a33e` (`ECTA.tex`)  
**Pinned supplement blob:** `9ae1d87ddc6da2e0cd0475522c269da8ee55a1be` (`supp.tex`)  
**Report date:** 4 October 2026  
**Recommendation:** **Reject in the present form. A substantially shorter and refocused new submission could be worth evaluating, but the present cumulative manuscript should not receive another ordinary revision round.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R14 is a qualitatively different object from the development snapshot considered in the preceding report. It is complete, source-bound, compiled, and accompanied by an unusually extensive evidence ledger. The author has executed the generic neural experiments, preserved the original training artifacts, formed the direct method contrasts on common paths, added fixed-work and raw-costate comparisons, instrumented the scalar reference, and reported unfavorable as well as favorable outcomes. I independently checked the publication source identities, the successful delivery artifact, the committed aggregate tables, and a representative original fixed-work shard. The source and artifact hashes match; the deterministic audit passes; and the representative raw arrays reproduce the reported NBO-minus-Raw and critic-mechanism calculations.

The revision therefore resolves the threshold objections that previously prevented substantive review. I no longer regard the paper as an unexecuted protocol or an unreliable numerical record. On reproducibility, provenance, and disclosure, R14 is stronger than most computational submissions I see.

The difficulty is now substantive rather than procedural. The new evidence does not establish an incremental numerical contribution from the Bellman critic that gives the paper its title and organizing identity.

The primary study contains ninety fitted policies. Every reported NBO policy, direct-policy policy, and affine policy improves on the feasible analytical schedule under the stated policy-specific confidence construction. That is a useful result about the candidates and the certificate. But all 120 primary NBO-minus-comparator intervals contain zero. In the fixed-work extension, all 42 direct intervals also contain zero. At equal simulator visits and checkpoints, the raw-costate method is cheaper to fit and has a slightly larger sample mean than NBO in every one of the six dimension-by-checkpoint cells. In all six principal mechanism panels, the learned critic has larger costate mean-squared error than the raw-costate estimator and its critic-greedy action has a larger reference Hamiltonian gap. The direct policy-payoff intervals remain inconclusive, so these observations do not prove that Raw dominates NBO. They do show that the executed study supplies no positive evidence for the proposed critic mechanism and no signed economic advantage for NBO over the simpler alternatives.

The paper's strongest successful contribution is consequently a **method-agnostic policy-verification and safe-improvement framework for a particular continuous-time capital economy**. The curvature anchor, policy-specific payoff identity, diffusion-transfer calculation, clipping and arithmetic accounts, and common-path simultaneous inference can certify any feasible candidate satisfying the implementation contract. Those results are interesting. They are not evidence that Neural Bellman Operators are a superior or necessary candidate generator.

This mismatch matters at Econometrica. A numerical-method paper need not win every benchmark, and a carefully documented negative finding is scientifically valuable. But the manuscript must still identify what new method has been shown to do, why its distinctive component is needed, and what economic problem it solves better than strong alternatives. R14 does not yet do that. It instead combines a potentially valuable verification paper, an actor–critic framework whose distinctive critic is not supported by the experiment, and a very broad collection of inherited economic applications. At 63 main-text pages plus a 144-page supplement, the cumulative object is too broad relative to the contribution that the new evidence actually establishes.

I therefore recommend rejection in the present form. I would take seriously a new, sharply focused paper centered either on verified policy improvement—without making NBO the unsupported protagonist—or on a new computational study in which the Bellman evaluation block demonstrably improves economic accuracy or total work relative to appropriate baselines.

## 2. What R14 successfully repairs

The negative recommendation should not obscure the amount of genuine progress.

### 2.1 The submitted object is complete and immutable

The branch contains an integrated main article, supplement, response, generated tables, audit records, source identities, compiled documents, and the scripts needed to replay the publication layer. The final audit reports 123 passing regression assertions, successful compilation of the 63-page article, 144-page supplement, and 10-page response, and no unresolved references, duplicate labels, or overfull boxes. The evidence manifest distinguishes the commits that generated the primary and fixed-work studies from the later reporting commit. That distinction is correct and important.

### 2.2 The proposed generic networks are actually trained

The decisive objection to the early revision—that the advertised neural method was never run on a nontrivial economic problem—no longer applies. The capital study trains multilayer actors and critics in dimensions 10, 20, and 50. It records weights, checkpoints, failures, training visits, update counts, clocks, final simulation arrays, and method contrasts. Exact-structure portfolio and quadratic laboratories are no longer asked to carry the generic neural claim by themselves.

### 2.3 The paper uses the right direct estimand

The manuscript correctly distinguishes three questions:

1. whether a fitted policy improves on the feasible analytical schedule;
2. whether NBO improves on another fitted method; and
3. whether a fitted policy is close to the unknown optimum.

NBO-minus-DPO and NBO-minus-affine differences are formed path by path using the same initial states and innovations. The common schedule cancels, and the transfer allowance is not subtracted twice. The paper no longer infers method superiority by subtracting two separate schedule-relative lower bounds.

### 2.4 The policy-specific continuous-time certificate is a real advance over sampled residual rhetoric

The capital certificate does not claim that a low average PDE residual is a global theorem. It uses the economics of the model: log-utility curvature controls the direct cost of changing consumption, a spectral bound controls propagation through dense nonlinear production, and a paired payoff identity measures the actual gain of a deployed candidate. The diffusion-transfer and tail calculations connect the sampled controller to the original unbounded diffusion without requiring a global derivative bound for the trained network. This is a much more credible route to an economic statement than the residual-based claims in the first draft.

### 2.5 The role of the critic is made testable

The strong-concavity inequality and conditional-projection identity state a clear potential mechanism: a sufficiently accurate costate predictor can reduce Hamiltonian loss. The fixed-work study includes a raw-costate comparator, critic ablations, common targets, and independent mechanism panels. Most importantly, the manuscript reports that the critic does not realize the proposed variance-reduction opportunity in the executed design. That is exemplary scientific reporting.

### 2.6 Information and implementation assumptions are visible

The paper no longer treats latent innovations as automatically observed. The exact-history result specifies continuous noiseless state observation, known coefficients and controls, the drift integral, persistent memory, and independent private randomization. A separate finite-observation result adds sensor and recurrence allowances. These are strong assumptions, but they are stated rather than hidden.

### 2.7 The scalar reference is independent and well instrumented

The one-state nonlinear reference uses a monotone implicit scheme and full-box maximization. The replay records HJB and fixed-policy residuals, Howard iteration histories, boundary conditions, action-bound frequencies, grid and domain sensitivity, and policy loss at several initial states. The paper correctly refrains from extrapolating this scalar result to the high-dimensional controllers.

## 3. Blocking concerns

### B1. The distinctive NBO component is not supported by the executed evidence

This is the central concern.

The certification layer establishes that many fitted policies improve on the analytical schedule. It does not establish that the Bellman critic is responsible for those improvements. The principal evidence is:

- all 120 primary NBO-minus-DPO or NBO-minus-affine intervals contain zero;
- all 42 fixed-work direct intervals contain zero;
- all twelve principal Ubuntu 24 NBO-minus-Raw sample means are negative, although their simultaneous intervals are inconclusive;
- in each of the six fixed-work dimension-by-checkpoint cells, Raw has a slightly larger schedule-improvement mean and a lower fitting clock than NBO;
- the critic costate MSE exceeds the raw-costate MSE in all six principal mechanism panels, by factors of approximately 1.06 to 1.99; and
- the critic-implied greedy action has a larger independent-reference Hamiltonian gap than the raw-costate action in all six panels.

These are not grounds for claiming that Raw dominates NBO. The policy differences are too small relative to the conservative simultaneous margins, and the mechanism panel is descriptive rather than an occupancy-weighted causal decomposition. They are grounds for concluding that R14 has not demonstrated the incremental value of the learned Bellman block.

The successful policy-specific certificate is agnostic about how the candidate was constructed. Direct policy optimization, Raw, an affine rule, a classical approximation, or a hand-designed policy can enter the same payoff calculation. Likewise, the new performance-difference inequality applies to any costate estimator. Thus the positive theorems and the positive schedule comparisons do not isolate NBO.

A method paper can survive an inconclusive benchmark if it establishes a new capability unavailable to alternatives. Here the alternatives produce the same type of feasible policy, satisfy the same verification contract, and attain indistinguishable policy payoffs at the reported precision. The paper should not retain NBO as its central claimed numerical contribution without a domain in which the critic is shown to add value.

### B2. The costate-to-welfare mechanism is not operationally closed in the experiment

The new welfare proposition is mathematically useful, but its empirical quantities are not the quantities measured in the mechanism tables.

The proposition requires costate regression error and rollout bias under the **candidate policy's discounted state-occupation law**, together with an action-optimization error. The mechanism panels instead use sixty-four held-out states drawn from the declared training-state design. The manuscript correctly acknowledges this difference. No change-of-measure bound connects those states to the candidate occupation law.

The fine rollout mean remains both noisy and time-discretized. The nested 32/128-cell change is a diagnostic, not an upper bound on the continuous-time rollout bias. The alternative residual-to-costate inequality requires global bounds on the derivatives of the fixed-policy residual and terminal error. Those bounds are not computed for the trained critic. The actor Hamiltonian gaps in the table are evaluated against the noisy finite-grid reference rather than enclosed over the continuous candidate distribution.

Consequently, the paper does not instantiate its own mechanism theorem to produce a welfare lower bound attributable to critic accuracy. It verifies policy payoffs separately—which is valid—but then the costate theorem remains explanatory rather than operational. For an NBO contribution, closing this chain is essential:

1. critic error under the deployed candidate's occupation law;
2. a controlled rollout-discretization or residual bias;
3. an upper bound on actor suboptimality for the critic-defined Hamiltonian;
4. the implied economic loss term; and
5. comparison of that term with a raw or direct alternative at matched work.

Without this chain, the critic is an optional training device rather than a verified source of economic improvement.

### B3. The high-dimensional result is safe improvement, not an accurate solution of the control problem

The paper makes this distinction in several places, but its breadth and title still invite the stronger interpretation.

For the finite initial-state population, the reported NBO regret upper bounds are approximately 0.02097, 0.02847, and 0.03039 in dimensions 10, 20, and 50. The corresponding mean schedule improvements are approximately 0.00147, 0.00135, and 0.00161. The regret upper bounds are therefore about 14 to 21 times the means and about 33 to 67 times the simultaneous lower improvement endpoints.

These are legitimate upper bounds, but they do not establish near-optimality or high-dimensional HJB accuracy. They mainly inherit the analytical anchor gap and subtract a small verified policy gain. The scalar reference gives much sharper finite-grid policy losses at initial state zero, but the ranking reverses at initial state one, and the scalar model cannot validate the 10-, 20-, or 50-dimensional innovation-history controllers.

The paper should therefore be positioned as verified conservative improvement over a feasible policy, not as a demonstrated accurate neural solution method for the high-dimensional HJB. A top-journal numerical-method claim would require at least one of the following:

- a substantially tighter high-dimensional optimality account;
- an independent high-dimensional reference or convergent lower/upper bounding sequence;
- a systematic approximation study showing value and policy error decrease with work; or
- an economic result that depends materially on the learned policy despite the broad regret interval.

R14 does not yet provide one.

### B4. The statistical statements are conditional on selected fitted objects, not statements about the methods' training distributions

The paper is commendably explicit on this point. The confidence event concerns independent final simulation conditional on the fitted policies. The ten primary initialization/minibatch streams are fixed recorded objects, and their across-stream ranges are descriptive. The fixed-work extension uses only two principal streams per dimension. There is no probability model over future optimizer initializations, data orderings, or hardware nondeterminism.

This is sufficient to certify the listed policies. It is not sufficient to conclude that “the method” reliably produces such policies or that two methods have equal expected performance. The direct contrasts are much smaller than the simultaneous margins, so the absence of a signed pair does not establish practical equivalence either.

A numerical-method paper should state and estimate a method-level object. One possible design is to prespecify a distribution over training seeds and report hierarchical uncertainty that includes both training and final-simulation variation. Another is to treat training deterministically but provide a much larger and systematically stratified grid of initializations, failure modes, architectures, and budgets, with an equivalence margin defined in economic units. The current finite-object evidence is valuable, but it does not support claims about robust method performance.

### B5. The work comparison is not yet a complete matched-accuracy comparison

R14 improves substantially on an equal-wall-time-only design. It reports simulator visits, update counts, fitting clocks, verification clocks, target frontiers, and a second execution environment. Still, no single comparison measures complete work at matched economic accuracy.

Equal simulator visits and equal checkpoints are not equal floating-point work. NBO performs five critic and five actor updates per iteration; Raw performs five actor updates without critic regression; DPO performs one actor update. In the representative original shard, NBO performs 400 critic plus 400 actor updates, whereas Raw performs 400 actor updates. Recorded verification clocks begin after weight loading and deterministic interval construction, and the retrospective prefix frontier is not a measured early-stopping run. The primary 20-second comparison is hardware-specific and allows iteration completion.

The empirical result also points in an uncomfortable direction for NBO: Raw reaches the reported 0.0005 lower-gain target at lower accounted time in dimensions 10 and 50, and neither method reaches 0.001. A correct method comparison should include:

- fully inclusive end-to-end wall time;
- simulator transitions;
- optimizer updates and derivative evaluations;
- peak memory;
- candidate-generation and certification cost;
- the cost of failed checkpoints and searches; and
- accuracy or economic-gain frontiers over several budgets.

The paper reports many of these components but does not synthesize them into a stable matched-accuracy comparison. As a result, the reader cannot identify a numerical efficiency advantage for NBO.

### B6. The benchmark set is too narrow to establish a general numerical-method contribution

DPO, affine policies, and Raw are important and well-chosen internal comparators. They isolate some components of the proposed algorithm. They do not span the main alternatives a numerical economist would consider.

At minimum, the capital model should include a direct neural HJB or policy-iteration method using the same actor class and feasible maximization routine, so that the value of maintaining a separate learned actor can be assessed. Where computationally feasible, the study should also include a neural PDE residual method, a BSDE-based method appropriate to the same finite-horizon problem, and a structure-exploiting projection or approximate dynamic-programming baseline. The scalar model can support especially strong classical comparisons, but its current role is only to evaluate frozen policies.

The point is not to accumulate brand-name baselines. The comparison should isolate the claimed numerical innovation. All methods should face the same economic primitives, action box, initial-state population, network capacity where relevant, training and validation information, stopping criterion, and final payoff evaluation. Without this design, the paper cannot establish whether NBO is a useful new method, an alternative parameterization of approximate policy iteration, or an expensive route to policies obtainable more directly.

### B7. The manuscript's scope and economic payoff are not aligned with the result established by R14

The paper is 63 pages, with a 144-page supplement. It covers differential and monotone Bellman formulations, viscosity selection, recursive utility, endogenous preference adjustment, temporal selves, dynamic games, stochastic trace estimation, continuous-time capital, observation reconstruction, finite sensing, and management fees. The new decisive evidence, however, concerns one stylized dense capital economy and one scalar member of that family.

The retained preference, temporal-self, and game applications may each be worthwhile, but they do not receive the same new method comparison or mechanism analysis. Their presence makes the paper appear to establish a broad numerical platform when the strongest new result is a model-specific verification argument. The nine-profile capital population is transparent but artificial, not empirically calibrated. The management-fee calculation is an exact transformation of the same utility difference, not an independently substantive economic finding.

This is not merely a complaint about length. The cumulative structure obscures the paper that R14 has actually succeeded in writing. The strongest publishable core is approximately:

1. a feasible analytical anchor for a nonlinear continuous-time capital model;
2. a policy-specific continuous-time payoff certificate for arbitrary candidate generators;
3. common-path simultaneous method comparisons;
4. an honest finding that several neural candidate generators improve the anchor but are not distinguishable at the reported precision; and
5. a negative mechanism result for the fitted critic.

That would be a coherent and potentially useful paper. It is not the current all-purpose “Neural Bellman Operators” manuscript.

## 4. Major comments and required changes

### M1. Choose the paper's center

There are two credible paths, but they are different papers.

**Path A: verified policy improvement.** Recast the contribution around the policy-specific continuous-time certificate. Make the candidate generator deliberately method-agnostic. Present NBO, DPO, Raw, affine rules, and perhaps classical methods as alternatives that feed the same verifier. Retain the unfavorable critic evidence. Rename and shorten the paper accordingly.

**Path B: Neural Bellman Operators.** Produce a new study in a problem where continuation-value learning is genuinely needed and where the critic yields a reproducible gain in economic accuracy or total work relative to Raw, DPO, direct HJB, and strong numerical alternatives. Close the costate-to-welfare chain on the deployed state distribution.

The current manuscript tries to take both paths while supplying decisive evidence only for the first.

### M2. Define a method-level estimand before additional experiments

State whether the target is expected performance over a prespecified training-randomness distribution, a probability of attaining a certified threshold, median total work to target, or a deterministic worst-case property over a finite initialization set. Then design the number of training replications and final paths around an economically meaningful equivalence or superiority margin. Conditional policy intervals and method-level uncertainty should not be conflated.

### M3. Make the critic mechanism operational

Use candidate-occupation states, or provide a defensible density-ratio bound. Obtain a controlled time-discretization account for rollout costates. Enclose the actor's feasible Hamiltonian gap. Then report the economic loss term in the units of the policy payoff and compare it with the directly measured NBO-minus-Raw and NBO-minus-DPO differences. If this cannot be done, present the costate theorem as motivation rather than a demonstrated mechanism.

### M4. Report complete accuracy-versus-work frontiers

Measure actual early stopping rather than only retrospective prefix clocks. Include initialization, model construction, checkpoint I/O, deterministic constants, final verification, failed target checks, and memory. Report both time and machine-independent operation proxies. A candidate-generation method that saves no total work at a common certified target has not established numerical efficiency.

### M5. Add contribution-isolating baselines

At least one direct neural HJB or approximate policy-iteration baseline should share the same model, actor/value capacity, feasible action routine, and final verifier. A low-dimensional classical solver should be used as a training-method comparator, not only as a frozen-policy evaluator. Any excluded baseline should be justified by a precise incompatibility rather than dimensional rhetoric.

### M6. Separate the model-specific theorem from generic claims

The continuous capital certificate relies on log felicity, bounded actions, additive diffusion, bounded tanh production, a particular schedule, and spectral/curvature structure. These assumptions are strengths because they make verification possible. They are not generic properties of neural Bellman equations. The title, abstract, and contribution list should make the model-specific nature of the sharpest result unmistakable.

### M7. Clarify the economic implementation claim

The exact-history controller is randomized and history dependent. It assumes continuous noiseless observation, known coefficients, exact drift integration, and private Brownian randomization. The finite-sensing theorem is a useful extension, but its outward transfer can be conservative and is attached to a protected parent at a specified mesh. Explain the economic institution that implements this controller and report the magnitude of the sensing allowance relative to the certified gains. Avoid calling it ordinary state feedback.

### M8. Reduce and reorganize the presentation

The main paper should not require the reader to navigate a cumulative genealogy of R6–R14 results. A focused submission should contain one notation system, one authoritative algorithm, one central theorem chain, and one evidence design. Historical applications, obsolete development stages, and secondary numerical laboratories should remain in an archive rather than in a 144-page publication supplement.

### M9. Clean up method labels and evidence semantics

The raw-costate policy files retain `method: "nbo"` in some original JSON records while using a `_fixed_raw` tag. The tables are clear, but future publication records should use a distinct method identifier. Likewise, “positive NBO policy” should always mean positive relative to the schedule, not positive relative to another method. These distinctions are already present in prose and should be enforced in machine-readable schemas.

## 5. A focused publishable design

A credible new submission could be much shorter and stronger.

### 5.1 Verification-centered design

The main theorem would be the policy-specific certificate for the capital economy. The empirical object would be the distribution of certified improvement and total verification cost across candidate generators. The negative critic finding would be a result, not an embarrassment: in this economy and budget, direct or raw candidate generation is as effective and cheaper, while the verifier remains useful. This would make the paper an honest contribution to reliable computational economics.

The paper should report:

- a small number of well-justified candidate generators;
- prespecified method-level randomness and equivalence margins;
- complete work-to-certified-gain frontiers;
- a low-dimensional convergence/reference study;
- the high-dimensional policy-specific certificate;
- exact scope of the adapted comparison class; and
- one economically interpretable decision consequence.

### 5.2 NBO-centered design

Alternatively, identify a problem in which raw rollout derivatives are too noisy or unavailable, value evaluation has reusable structure, and the critic can amortize its cost. Demonstrate that the learned continuation object improves held-out costates under the deployed occupation law, reduces Hamiltonian loss, and lowers total work at a common economic-accuracy target. That study should be conducted before writing broad claims about recursive preferences, strategic games, or viscosity selection.

## 6. Independent verification performed for this report

I performed the following checks against the pinned R14 snapshot.

1. **Publication source identity.** The SHA-256 and Git blob identities of `ECTA.tex` and `supp.tex` match the R14 publication ledger.
2. **Delivery artifact.** The downloaded workflow artifact `nbo-r14-delivery-37182922670` has SHA-256 `461a938b0866746f8bbf536efad2d14bfbcaea25e6ba8fd1deb428413b2f6ca7`, matching the GitHub artifact digest.
3. **Publication gate.** The final audit records a complete, source-verified publication, 123 passing tests, and successful compilation of the article, supplement, and response.
4. **Aggregate-table replay.** A separate standard-library script parses the committed tables and confirms:
   - six summarized NBO schedule rows have positive lower endpoints;
   - all twelve primary direct-summary intervals straddle zero;
   - all forty-two fixed-work direct intervals straddle zero;
   - all twelve principal Ubuntu 24 NBO-minus-Raw sample means are negative;
   - Raw has a larger sample mean and a lower fit clock in all six fixed-work dimension-by-checkpoint cells;
   - critic MSE exceeds raw MSE in all six principal panels; and
   - critic-greedy Hamiltonian gap exceeds raw-greedy gap in all six principal panels.
5. **Original raw shard.** I downloaded the original dimension-10, seed-7919 Ubuntu 24 fixed-work artifact, whose SHA-256 is `985558b09377c86f2493271d4112c5265cfd375645631b89332144e8738e6c5c`. Its 80-iteration NBO-minus-Raw mean is approximately `-1.2900e-5`, with interval `[-0.0012650, 0.0012392]`. The same raw shard records critic costate MSE `6.9013e-5` versus raw MSE `6.5597e-5`, and critic-greedy Hamiltonian gap `1.1539e-5` versus raw gap `9.0143e-6`.
6. **Source limitation.** I did not rerun all time-budgeted training jobs. A new execution would have a different hardware and timing environment and would not reproduce the original wall-clock experiment by construction. I verified the source-bound publication layer, deterministic aggregates, and a representative original raw shard instead.

The review directory includes the audit script, its machine-readable output, and a manifest pinning the reviewed scope.

## 7. Recommendation

R14 deserves substantial credit. It turns a previously incomplete and overstated project into a complete, reproducible, and unusually candid computational record. The author has answered the earlier procedural and correctness objections with care. I found no immediate internal contradiction in the new direct paired construction or the costate-to-welfare inequality under their stated assumptions.

Nevertheless, the current manuscript does not meet the standard for an Econometrica numerical-methods contribution. The distinctive learned critic is not shown to improve costate accuracy, Hamiltonian quality, policy payoff, or total work relative to the simpler raw and direct alternatives. The sharpest successful theorem verifies arbitrary candidates in a particular model rather than establishing NBO as a superior numerical method. The high-dimensional result is conservative policy improvement, not a tight solution of the HJB. The method-level inference and matched-accuracy comparison remain incomplete, and the 207-page cumulative scope is disproportionate to the result established by the new evidence.

I therefore recommend **rejection in the present form and no further ordinary revision of this cumulative submission**. A new, focused paper on verified policy improvement—or a genuinely new NBO study that demonstrates the value of the Bellman block—could merit serious consideration.
