# External Referee Report — Neural Bellman Operators (R29, independent second pass)

**Venue perspective:** Econometrica-level numerical/computational methods  
**Repository:** TrillionniumFoundation/NBO  
**Reviewed branch:** revision/econometrica-r29-referee-integration-2026-09-24  
**Reviewed HEAD:** 788246778893695471015ce4db76e6a61a2c9ca0  
**Review branch:** review/econometrica-r29-second-pass-numerical-methods-2026-09-24  
**Date:** 2026-09-24

## 1. Recommendation

**Reject in the present form.**

R29 is substantially more auditable, more careful, and more honest about its limitations than the earlier versions preserved in the repository. I do not find a packaging failure, an obvious defect in the two central finite-state induction arguments, or a reproducibility failure at the reviewed head. The exact-head validation run 35932676059 completed successfully at the reviewed SHA. The paper also does a better job than many computational submissions of distinguishing a raw learned proposal from a repaired certified policy.

Those improvements do not resolve the main Econometrica-level question. The central finite-state certificate is obtained by a full exact-model, all-state, all-action backward scan with the same information resources and the same tabular enumeration order available to exact dynamic programming. On every reported scaling point, exact dynamic programming is dramatically cheaper than the neural-plus-certification pipeline. Once the state model becomes even moderately nontrivial, none of the raw policies in the main cohort meets the 0.01 target; the final guarantee is delivered by the exhaustive completion operator. The paper therefore demonstrates a correct way to repair and audit finite policies, but it does not yet demonstrate a numerically compelling reason to use the neural proposal at all.

This is not a cosmetic objection and cannot be repaired by stronger prose. The paper currently lacks either of the two things that would justify the central claim: (i) a computational regime in which a high-quality proposal materially reduces the cost of certification or solution relative to strong classical methods, or (ii) a theorem showing that the preservation objective has independent economic value large enough to justify the additional computation.

The continuous-control material does not fill this gap. The only fully instantiated stopped-control derivative certificate is one-dimensional, fixes consumption and portfolio choice, starts at a central state, and has an exit-probability upper bound below 2.153e-31. Thus the numerical example in which the “stopped” bridge is proved is precisely a case in which stopping is essentially inactive. Meanwhile the actual original whole-domain target remains 7.181834580823298 against 0.01, a factor of approximately 718.18 away from the declared tolerance.

The transport and rollback sections are useful audit exercises, but they do not supply a missing numerical method. The exact recentered transport experiment is an implementation identity by construction, and the deployment gate proves safe acceptance/restoration semantics rather than solver superiority.

Accordingly, I view R29 as a technically serious research record containing several correct lemmas, useful verification practices, and a potentially publishable residual-budget idea, but not yet as a coherent Econometrica numerical-method paper.

## 2. Exact status of the submission object

The current branch revision/econometrica-r29-referee-integration-2026-09-24 and the earlier revision/econometrica-r29-referee-copy-2026-09-24 compare as **identical**: zero commits ahead or behind and no file differences. Both resolve to the reviewed HEAD 788246778893695471015ce4db76e6a61a2c9ca0.

Therefore this report is an independent second pass over the same R29 scientific object, not a review of a later author response to an R29 referee report. RESPONSE_R29 explicitly states that the latest report it addresses is R27. Any unresolved R29-level scientific objection therefore remains unresolved unless the existing R29 manuscript already contains the needed argument.

The exact-head workflow named “R29 exact-head validation” succeeded on the reviewed SHA. I consequently do not base the recommendation on compilation, missing artifacts, or a stale-head objection.

## 3. What is technically credible in R29

Before stating the blocking findings, I want to identify what I think the authors have done correctly.

First, the finite-state residual-envelope theorem is a legitimate backward comparison statement. Given a finite horizon, exact model, finite feasible actions, and exact suffix evaluation, the claimed all-state regret envelope follows by induction. The budgeted variant also has a straightforward valid preservation argument: when the raw action is retained it is used against an improved completed suffix; when it is replaced, a maximizing action is chosen against that suffix. The proof that the completed policy weakly dominates the raw policy pointwise is not the problem.

Second, the paper is now explicit that the deployed certified object is an action table, not the original floating-point neural network. This distinction is essential and should be preserved.

Third, the manuscript explicitly charges exact dynamic programming, reports raw failures, distinguishes finite-state from continuous-state certification, and acknowledges that a small correction fraction is not a computational saving under the current exhaustive scan. These are all improvements in scientific hygiene.

Fourth, the constrained box-polling theorem is a reasonable certificate theorem. The short-face case and the “oracle unresolved” outcome are handled explicitly rather than being silently conflated with a failed comparison. I did not find an obvious logical error in the displayed projected-gradient bound.

Fifth, the R29 repository is unusually transparent about provenance, exact arithmetic, candidate freezing, reference ordering, and post-diagnostic status. This transparency is valuable. It also makes the substantive negative conclusion unusually easy to see.

The recommendation below is therefore not “reject because the computation cannot be trusted.” It is “reject because the trusted computation does not establish the claimed level of numerical-method value.”

## 4. Blocking scientific findings

### R29-SP-F1 — The method does not beat the solver whose work it essentially reproduces

The completion operator evaluates all feasible actions at every state against an exactly evaluated completed suffix. Its arithmetic enumeration order is reported as O(TNAD), the same basic state-action-successor order as backward dynamic programming.

The empirical comparison is adverse at every nontrivial scaling point. From Table tab:r29scaling:

- d=4, L=4: exact DP 0.03729 s; new neural fitting 2.291 s; budget repair 0.03296 s; verification 0.03244 s. Neural fitting alone is about 61.4 times the exact solve; fitting plus repair plus verification is about 63.2 times the exact solve.
- d=4, L=5: exact DP 0.103 s; neural fitting 3.28 s; budget repair 0.1022 s; verification 0.08187 s. The corresponding certified pipeline is about 33.6 times the exact solve.
- d=5, L=4: exact DP 0.2064 s; neural fitting 4.424 s; budget repair 0.1498 s; verification 0.1556 s. The certified pipeline is about 22.9 times the exact solve.
- d=6, L=4: exact DP 1.103 s; neural fitting 13.33 s; budget repair 0.6971 s; verification 0.7865 s. The certified pipeline is about 13.4 times the exact solve.
- d=7, L=4: exact DP 5.495 s; neural fitting 51.6 s; budget repair 3.677 s; verification 4.668 s. The certified pipeline is about 10.9 times the exact solve.

These are not small constant-factor reversals. The proposed approximation stage is slower before certification begins, and certification adds further exhaustive work.

**Required correction:** demonstrate a problem regime in which proposal plus certification has a substantive advantage over the strongest information-matched classical method. Acceptable advantages could include lower total wall time, lower memory, lower amortized cost over many related solves, lower model-query complexity, or successful certification when exact DP is infeasible. A theorem or experiment showing that good proposals permit sub-enumerative certification would directly address the present failure. Without such evidence, this component is an auditing procedure, not a competitive numerical solution method.

### R29-SP-F2 — “286/286 certified” is almost entirely guaranteed by construction

R29 reports 115 candidates and 286 completed variants, with every completed variant satisfying its tolerance. This number is visually impressive but scientifically weak as an efficacy statistic.

The completion rule is explicitly designed to replace any raw action that would violate the residual budget with an exact maximizing action. Under the theorem’s finite-state assumptions, the completed policy is guaranteed to satisfy the stated envelope. Therefore a universal completion pass rate is primarily a consistency check of the theorem, implementation, and arithmetic.

At epsilon=0, the conceptual issue becomes especially clear: a raw action is retained only when it is exactly greedy against the completed suffix; otherwise it is replaced by a maximizing action. Backward induction then produces an optimal policy, up to tie choices. Positive epsilon interpolates between exact backward optimization and action retention under a tolerance budget.

**Required correction:** stop treating the universal post-completion pass rate as a headline numerical success metric. The meaningful empirical quantities are raw approximation quality, total work, memory, model calls, the economically weighted cost of edits, and performance relative to strong algorithms at matched information.

### R29-SP-F3 — Raw approximation fails exactly where the scaling exercise becomes interesting

The main coverage table reports raw-regret passes:

- d=2, L=4: 8 of 23;
- d=3, L=4: 4 of 23;
- d=4, L=4: 0 of 31;
- d=4, L=5: 0 of 20;
- d=5, L=4: 0 of 6;
- d=6, L=4: 0 of 6;
- d=7, L=4: 0 of 6.

Thus every main-cohort raw candidate fails the 0.01 regret target once d reaches 4. The global headline records only 12 raw-regret passes among 115 candidates.

This is the opposite of a demonstration that approximation is carrying the solution at scale. The certificate succeeds because the exhaustive completion operator repairs the policy.

The d=7 neural policy is an instructive example. Its raw worst regret is 1.549, more than two orders of magnitude above 0.01, yet only 634 of 131,064 nonsettled state-time decisions are replaced by the budget rule. This is a useful illustration of how a small number of bad actions can dominate a worst-state guarantee. It is not evidence that the neural policy was already accurate in the sense the paper’s target requires.

**Required correction:** make the failure of raw accuracy a central result rather than a caveat. If neural approximation is meant to matter scientifically, demonstrate a regime in which it either meets the target before exhaustive repair or materially lowers the cost of reaching the target.

### R29-SP-F4 — The neural component has not earned a method-specific claim

The most favorable neural fact at the largest graph is that it requires far fewer action replacements than crude controls. But the strongest nonneural approximation controls remain competitive, and sometimes superior, on the metrics that matter.

At d=7, L=4 the reported polynomial proposal has raw worst regret 1.809 versus 1.549 for the neural proposal, and a budget correction fraction about 1.211% versus 0.484%. The neural proposal is somewhat better on those two metrics. However the reported new neural fit costs 51.6 s while the polynomial fit costs approximately 0.2275 s, a difference of more than two orders of magnitude. The manuscript does not attach an economic value to avoiding those extra policy edits that could justify the training cost.

At d=4, L=5, the reported polynomial group has a lower raw-regret maximum, about 0.1925, than the neural group, about 0.3664, and a smaller budget correction fraction.

The current evidence therefore supports “some proposal classes are easier to repair than others,” not “neural Bellman operators deliver a compelling certified numerical method.”

**Required correction:** either establish a reproducible neural-specific advantage under a relevant cost/accuracy metric, or reposition neural networks as one proposal family among several and title the paper around the representation-agnostic certification method.

### R29-SP-F5 — Action preservation is not yet an economic objective

The state-dependent budget rule is genuinely more permissive than the fixed local threshold in many cases. R29 reports that it makes fewer changes in 60 cases, more in zero, and the same number in 55.

But the paper has not established that unweighted action-table preservation is valuable.

The d=7 neural example is again decisive: changing only 0.484% of nonsettled state-time decisions can move the policy from raw worst regret 1.549 to a certified 0.01 object. A tiny Hamming edit fraction is therefore compatible with an economically enormous change in the worst-case guarantee. Conversely, an edit at a nearly unreachable state is counted exactly like an edit at a high-probability, high-value state.

Moreover, the present implementation scans the full model whether it changes 634 actions or 114,341 actions. Edit sparsity is not a computational proxy.

**Required correction:** if preservation is the contribution, formalize its value. Possibilities include occupancy-weighted edit cost, switching/retuning cost, interpretability constraints, institutional policy-change penalties, or a certified sparse-update algorithm whose runtime actually scales with the number or geometry of changed regions. Otherwise “fewer changes” is descriptive bookkeeping, not a numerical objective.

### R29-SP-F6 — “Reference-free” is provenance language, not information-complexity language

The completion operator does not read a stored optimal value function or an optimal action table. That is a legitimate and useful provenance property.

But it has the full transition law, reward function, exact feasible action set, exact completed suffix values, and performs exhaustive action maximization at every state. These are essentially the same model resources that exact backward induction needs.

Calling the method “reference-free” without immediately qualifying this distinction risks suggesting that it works with less solution-relevant information than exact dynamic programming. It does not.

**Required correction:** use language such as “precomputed-optimum-free” or “no stored V-star reference” when discussing provenance, and separately state the information and computational resources used by the completion sweep. The paper should not use absence of an optimal-reference file as evidence of algorithmic independence from Bellman optimization.

### R29-SP-F7 — The scaling study does not test the regime that would motivate neural approximation

The largest finite graph has 16,384 states per time slice. This is useful for exact arithmetic stress testing but is not a scale at which a neural method is needed. Exact DP solves the largest reported graph in 5.495 seconds.

More importantly, the scaling experiment itself becomes statistically and algorithmically thin precisely at larger dimension. The d=5, d=6, and d=7 neural results use a single specified neural configuration/seed, whereas the larger seed panel is concentrated at d=4. The paper correctly avoids calling the resulting trend a robustness theorem, but then the high-dimensional rows cannot carry a neural scaling claim either.

The finite inventory graph is also not a verified discretization of the original continuous consumption-portfolio problem, and no discretization-error theorem links increasing d or L to the original economic target.

**Required correction:** either (i) move to a regime in which exact DP is genuinely infeasible and show how certification still works, with multiple neural seeds and architecture/optimizer controls, or (ii) present the current finite graphs purely as verification examples and remove any suggestion that they validate a high-dimensional neural strategy.

### R29-SP-F8 — The original economic target remains almost completely open

The paper repeatedly states the original objective:

sup over all states and restart times of V minus J(pi) <= 0.01

for the original stopped consumption-portfolio economy and a current-state actor.

The best retained whole-domain bound is 7.181834580823298. This is approximately 718.18 times the target tolerance.

R29 is admirably explicit that the target is not closed. But retaining the target as the organizing goal does not lessen the gap. None of the new finite-state inventory results establishes a continuous-domain discretization error. The scalar slice fixes consumption and investment and restricts preference adjustment to a constant. The financed family uses additional internal state and is not the current-state actor required by the target.

There is therefore no experiment in R29 that establishes the stated original objective, or even closes a material fraction of the numerical gap to it.

**Required correction:** choose a coherent paper-level objective. Either materially advance the original whole-domain certificate and instantiate the missing high-dimensional derivative/residual bridge, or demote the original target to motivating background and present a narrower finite-state certification paper. Keeping the strongest rhetoric of both directions produces a paper whose declared central target remains unmet.

### R29-SP-F9 — The “stopped” scalar experiment numerically switches stopping off

The one-dimensional slice is mathematically clean, but it is a weak stress test of the very phenomenon used to motivate the paper.

The slice fixes the restart at (0,2,5/4), consumption at 3/4, investment at zero, and constant adjustment theta in [-1/5,1/5]. Wealth is deterministic and does not hit its boundary. Preference exit requires a Brownian excursion large enough that the paper bounds the exit probability by

p_exit <= 4 exp(-72) < 2.153e-31.

Thus the implemented derivative bridge is verified in a case where the stopped and unstopped objectives differ on an event of essentially zero probability. The manuscript proves a stopped-control statement, but the computation does not probe the difficult stopping regime near economically fragile boundaries or restart states.

This matters because the full-domain difficulty is explicitly attributed to stopping, boundary behavior, financing, and active controls.

**Required correction:** add at least one nondegenerate stopped instance in which exit probability and boundary terms are economically material and the same derivative/certificate machinery remains numerically effective. A central-state example with exit probability below 10^-30 cannot validate robustness to stopping.

### R29-SP-F10 — The polling theorem is a certificate theorem, not yet a competitive optimization method

The constrained polling result is mathematically reasonable, but the numerical instantiation does not establish that this is an attractive solver.

The theorem requires interval width of order h^2, and its work is explicitly multiplied by W(kappa h^2), the cost of achieving that precision. In the only rigorous implementation, substantial problem-specific work is used to build a degree-100 polynomial oracle, control Gaussian tails, audit derivatives, and cover the full theta interval.

For the reported scalar class, strict concavity is certified. Once that structure is available, a direct certified derivative sign/bracketing method or interval root method is an obvious classical competitor. The manuscript does not show that coordinate polling is preferable to such a method in oracle calls, total construction work, or generality.

The more important intended application is the financed 47-dimensional problem, but the paper explicitly does not instantiate the required arbitrary-precision oracle there.

**Required correction:** compare the proposed polling certificate with strong verified constrained optimization alternatives at matched precision. If the theorem is intended only as a generic certificate wrapper, say so. If it is intended as a numerical optimizer contribution, demonstrate a nontrivial multidimensional case where its total oracle cost is competitive.

### R29-SP-F11 — The economic content of the scalar comparative static is too narrow to carry the paper

Within the fixed class, increasing the adjustment-cost coefficient from k=1/2 to k=2 moves the optimum from the upper theta boundary to an interior point near 0.183. This is a valid comparative static for the restricted class.

But consumption is fixed, portfolio choice is fixed at zero, the restart is fixed, theta is constant over time, and stopping is essentially inactive. The result therefore does not identify the behavior of the original unrestricted economy.

As an illustration this is fine. As one of the principal continuous-control pillars of an Econometrica submission it is too narrow.

**Required correction:** either deepen the economic result substantially or move the scalar comparative static to a supporting example rather than treating it as a coequal main contribution.

### R29-SP-F12 — The rollback experiment validates safety semantics, not solver performance

Proposition prop:gate28 is essentially an interval-certified acceptance rule: accept only when the candidate’s lower payoff bound exceeds the incumbent’s upper payoff bound by the required margin; otherwise restore state.

This is a useful engineering contract. But R29 itself reports that the paired final outcomes do not establish a strict payoff improvement from gating. Neural Adam and direct Adam need not reject; the L-BFGS-B rejections demonstrate that restoration works, not that the gate improves the optimization outcome enough to compensate for verification cost.

**Required correction:** provide prospective instances in which the gate prevents a strictly certified welfare loss and improves an economically relevant performance criterion net of verification cost, or relegate the result to a verification/software appendix.

### R29-SP-F13 — The historical-transport experiment is an implementation identity, not an alternative algorithm

Proposition prop:transport28 states that two implementations with the same carrier parameters, the same Adam state, the same hyperparameters, the same economic gradient, the same Jacobian pullback, and full recentering on the same realized network output generate the same path in exact arithmetic.

That statement is true because the second implementation reproduces the first recurrence. The observed approximately machine-precision path agreement is therefore a valuable code-consistency check. It is not evidence of a representation-free optimizer, a lower-dimensional method, or a new optimization mechanism.

The manuscript now says this more carefully, but the material still occupies too much conceptual weight relative to its algorithmic consequence.

**Required correction:** keep the identity if it is needed to diagnose historical experiments, but subordinate it sharply unless a genuinely different algorithmic consequence follows.

### R29-SP-F14 — The evidence remains exploratory and post-diagnostic

The repository is commendably explicit that the completion amendment was designed after prior diagnostic work and that R29 is exploratory relative to earlier outcomes. The candidate/reference freeze discipline prevents one narrow form of leakage, but it does not create a confirmatory experiment independent of the accumulated development path.

The large count of candidate-policy variants should therefore not be read as statistical replication. Many variants share the same model, code path, completion theorem, and research history.

The issue is particularly sharp for d=5 through d=7, where only one neural seed/configuration is used.

**Required correction:** future evidence should be prospectively fixed on genuinely new model families and, if a neural scaling claim is maintained, include multiple seeds and architecture/optimizer controls at the largest dimensions.

### R29-SP-F15 — The novelty is still too close to classical Bellman improvement to support the current framing

The strongest potentially new object is the residual-budget retention rule: given an already completed suffix and a prescribed state-dependent error budget, retain the candidate action if its local deficit plus the propagated suffix envelope fits inside the budget; otherwise take a maximizing action.

This is a clean rule. But its mathematical ingredients are classical Bellman comparison, exact policy evaluation, one-step greedy improvement, and residual propagation. The manuscript says it does not invent policy iteration or Bellman residual bounds, which is appropriate, but it still does not sharply establish why the specific budget construction changes what can be computed in a way that classical approximate dynamic programming, rollout, safe policy improvement, or a-posteriori dynamic-programming verification cannot.

The current answer is “it preserves more raw actions.” As noted above, preservation has not yet been assigned an independent economic or computational value.

**Required correction:** build the novelty section around the nearest theorem-level neighbors, not around broad neural/control literature. State the exact mathematical delta and demonstrate a problem class in which that delta changes complexity, feasibility, or economic deployment.

### R29-SP-F16 — The manuscript still contains multiple papers without one dominant theorem-to-experiment chain

The main paper combines:

1. finite-state exact-rational residual completion;
2. a state-dependent action-retention budget;
3. constrained interval direct search;
4. a stopped likelihood-ratio derivative bridge;
5. a restricted economic comparative static;
6. a neural Adam transport identity;
7. an interval-certified deployment gate;
8. a historical full-domain continuous experiment that misses the target by a factor above 700.

Each component is individually understandable. Together they do not form one tight numerical-method contribution. The inventory model is not a discretization of the original economy; the scalar slice does not validate the high-dimensional financed actor; the transport identity does not improve the solver; and the rollback gate does not establish net performance.

**Required correction:** choose a central paper. My preferred direction would be to make the residual-budget completion method the core, with one theorem, one complexity result, one serious information-matched baseline study, and one economic application where proposal quality actually reduces certification work. The other historical mechanisms can be supplementary material.

### R29-SP-F17 — The title continues to over-attribute the certified result to neural operators

The central finite-state completion theorem is representation independent. It applies to neural, polynomial, random, myopic, base-stock, and truncated-tabular proposals. The final certified object is an exact action table that may contain nonneural replacements. The strongest theorem therefore does not certify a neural operator as such.

At the same time, the raw neural proposal fails the target throughout the d>=4 main cohort and is much more expensive than exact DP in the reported regime.

**Required correction:** either make the neural stage essential and quantitatively advantageous, or retitle/reframe the paper around certified Bellman completion with neural proposals as one application.

## 5. Technical comments

### R29-SP-T1 — State the epsilon=0 limit as a proposition or corollary

The manuscript hints at the interpolation between action retention and exact optimization but does not foreground it. The epsilon=0 limit is conceptually important and should be stated explicitly: under the fixed tie rule, backward completion retains a raw action only when it is greedy against the completed suffix and otherwise selects a maximizer, yielding an optimal policy by backward induction.

This single observation clarifies both the correctness and the computational limitation of the method.

### R29-SP-T2 — Report total certified-solution ratios in the main text

The current table separates neural training, repair, verification, and exact DP. Add a column for a clearly defined total proposal-to-certificate cost and report its ratio to exact DP. The present reader has to perform the economically decisive comparison manually.

The d=7 comparison is approximately 59.945 s for neural fit plus budget repair plus verification versus 5.495 s for exact DP, before adding any additional model-construction or serialization choices.

### R29-SP-T3 — An edit-count theorem should not be confused with a scan-cost theorem

The budget rule can reduce the number of changed actions. It does not currently reduce the number of action values evaluated. This distinction should be encoded directly in the theorem discussion and abstract-level interpretation.

If a future sparse method can certify untouched regions without full enumeration, that would be a major development. The current algorithm does not.

### R29-SP-T4 — Add economically weighted edit metrics

At minimum report occupancy-weighted changes from representative initial distributions, value-weighted action loss of the raw decision relative to the completed decision, and a state-priority-weighted edit cost. Uniform Hamming distance is too weak for economic interpretation.

### R29-SP-T5 — Compare with stronger rollout and policy-improvement baselines

The two-period truncated policy is useful but not enough. A serious comparison should include deeper rollout/lookahead with the same model and compute budget, approximate policy iteration or modified policy iteration, and a strong exact/optimized dynamic-programming implementation. If the proposed contribution is candidate preservation, compare against methods that explicitly start from a base policy and improve it.

### R29-SP-T6 — Optimize the exact DP baseline before making runtime claims

The current exact recursion is intentionally independent and scalar. That is useful for auditability but may not be the fastest classical implementation. If runtime is a scientific claim, a vectorized or otherwise optimized exact DP should be shown in addition to the independent auditing solver.

The present adverse comparison is already severe, so this requirement is likely to make the proposed method look worse, not better. It is nevertheless the correct benchmark.

### R29-SP-T7 — Separate proof complexity from integer-arithmetic complexity more sharply

O(TNAD) arithmetic enumeration is not enough to characterize exact-rational work. The manuscript records bit lengths empirically; add one compact asymptotic statement describing how numerator/denominator bit lengths can grow with horizon and primitive bit lengths under the implemented rational recursion.

### R29-SP-T8 — Explain how state-dependent budgets should be chosen

The theorem accepts any super-budget family satisfying the propagation inequality. The experiments use common tolerances and the induced remaining allowance. If state-specific priorities are a claimed advantage, the paper needs a principled budget-design problem: what objective chooses e_t(s), under what constraints, and what economic meaning does that choice have?

### R29-SP-T9 — The scalar oracle should be tested near an actual stopping boundary

A strong follow-up would place the restart or control path near a region where exit probability is not astronomically small and verify that the likelihood-ratio/truncation/interval machinery remains computationally viable. Otherwise the current example mostly verifies a smooth full-horizon problem with a negligible stopping correction.

### R29-SP-T10 — The 47-dimensional derivative bridge remains a central missing instantiation

The paper says this explicitly. I agree with that diagnosis. If the original continuous economy is retained as a central contribution, this cannot remain a future requirement. The manuscript needs validated derivative/residual constants and a genuine full-class certificate in the high-dimensional financed/current-state setting, or it needs to stop organizing the paper around that target.

### R29-SP-T11 — Hardware floating-point deployment is still not certified

The finite-state certificate applies to exact rational action tables and some arguments interpret saved binary64 coefficients as exact real constants. That is not a theorem about actual hardware evaluation of the neural actor. If deployment is part of the claim, add an end-to-end rounding enclosure. Otherwise keep the present explicit limitation and avoid language suggesting certified runtime neural execution.

### R29-SP-T12 — Distinguish “independent implementation” from “independent information”

The scalar reference recursion is independently coded, which is good for software audit. It still uses the same economic model and exact Bellman information. Use “independently implemented exact reference” rather than wording that can be read as an information-independent benchmark.

## 6. Econometric/economic relevance

The paper is primarily a numerical-analysis and verification manuscript, not an econometric identification paper. That is not disqualifying for Econometrica if the computational contribution is foundational enough and directly enables economic analysis that was previously inaccessible.

R29 has not yet crossed that bar. The original economic problem remains unsolved at the stated tolerance. The fully certified finite-state problem is a different inventory economy. The fully instantiated continuous result is a one-dimensional constant-control slice with nearly zero stopping probability. The production gate and transport identity do not generate a new economic conclusion.

The paper therefore needs a cleaner demonstration that the numerical method changes what economists can compute. A convincing example would be a genuinely difficult economic dynamic program where exact solution is infeasible, where a proposal can be generated cheaply, where certification is materially cheaper than solving, and where the certificate changes an economically substantive conclusion.

## 7. Minimum bar for a materially stronger revision

I would not recommend another incremental response-letter round on the current architecture. A materially stronger submission should satisfy most of the following:

1. **Choose the central contribution.** Make residual-budget Bellman completion the core, or make the original continuous stopped economy the core, but do not ask four independent mechanisms to substitute for one missing main result.

2. **Demonstrate computational advantage.** Show at least one regime where a good proposal reduces certification or solution cost relative to strong exact/classical methods. A sub-enumerative or adaptively sparse certificate would be especially compelling.

3. **Formalize preservation value.** If fewer action changes are the point, attach an economic or computational objective to those changes and prove/measure the relevant criterion.

4. **Make the neural stage necessary or demote it.** Either show a robust neural-specific advantage across seeds/models at the difficult scale, or treat neural fitting as one proposal generator among several.

5. **Use strong classical baselines.** Include optimized exact DP, deeper rollout/policy improvement, and—if continuous-state claims remain—adaptive sparse-grid or other serious classical approximation controls.

6. **Test a genuinely hard stopping regime.** The present p_exit < 2.153e-31 slice does not stress the stopped-control machinery.

7. **Resolve the original-target mismatch.** Either close a meaningful fraction of the 7.1818 versus 0.01 gap with a current-state all-domain certificate, or stop presenting that target as the central unresolved promise of the same paper.

8. **Prospectively freeze new model families.** Use at least one new economic model family and multiple neural seeds/configurations at the largest scale if generality or robustness is claimed.

9. **Compress the manuscript.** Move historical transport, rollback restoration, and research-lineage material to supplementary/audit documents unless they directly affect the central method’s theorem or performance.

10. **Rework title and abstract.** The title should describe the object actually certified. If the final object is a repaired finite-state action table and the theorem is representation independent, the current neural framing is too strong.

## 8. Recommendation to the editor

**Reject in the present form.**

The reason is not lack of effort, reproducibility, or mathematical care. The reason is that the main certified computation currently performs exhaustive Bellman work with the same model resources as exact dynamic programming, while being substantially more expensive in every reported regime. The raw neural policies fail the declared 0.01 standard throughout the d>=4 main cohort, and the final guarantees are supplied by the exact-model repair step. The continuous-control material remains either extremely restricted or uninstantiated at the dimension relevant to the original target.

A publishable paper may well exist inside this project. The most promising path, in my view, is a sharply focused paper on residual-budget action retention coupled to a certification algorithm whose work genuinely decreases when the proposal is good. That would convert the current “preserve many actions after scanning everything” result into a numerical method with a clear complexity advantage. Alternatively, a successful high-dimensional certification of the original stopped economy would change the assessment completely.

R29, as it stands, does neither.

## 9. Source map inspected

### Exact manuscript object
- ECTA_R29.tex
- SUPP_R29.tex
- RESPONSE_R29.tex
- COMPUTATION_R29.tex
- HISTORY_R29.tex
- revisions/2026-09-24-r29/REVISION_MANIFEST.json
- revisions/2026-09-24-r29/PROTOCOL.md
- revisions/2026-09-24-r29/disposition.json

### Main theorem/source modules
- revisions/2026-09-24-r29/paper/economy.tex
- revisions/2026-09-24-r29/paper/operators.tex
- revisions/2026-09-24-r29/paper/budgets.tex
- revisions/2026-09-24-r29/paper/positioning.tex
- revisions/2026-09-24-r29/paper/computation.tex
- revisions/2026-09-24-r29/paper/controls.tex
- revisions/2026-09-24-r29/paper/proofs.tex

### Generated numerical tables
- revisions/2026-09-24-r29/paper/generated/r29_groups.tex
- revisions/2026-09-24-r29/paper/generated/r29_attribution.tex
- revisions/2026-09-24-r29/paper/generated/r29_scale.tex
- revisions/2026-09-24-r29/paper/generated/r29_cost.tex
- revisions/2026-09-24-r29/paper/generated/r29_sensitivity.tex
- revisions/2026-09-24-r29/paper/generated/inventory_group_rows.tex
- revisions/2026-09-24-r29/paper/generated/inventory_cost_rows.tex

### Validation and results
- revisions/2026-09-24-r29/results/R29_HEADLINE_RESULTS.json
- revisions/2026-09-24-r29/results/SCIENCE_VALIDATION.json
- revisions/2026-09-24-r29/DOCUMENT_BUILD.json
- revisions/2026-09-24-r29/results/controls/
- GitHub Actions run 35932676059, R29 exact-head validation

### Branch comparison
- revision/econometrica-r29-referee-copy-2026-09-24
- revision/econometrica-r29-referee-integration-2026-09-24
- Comparison status: identical
