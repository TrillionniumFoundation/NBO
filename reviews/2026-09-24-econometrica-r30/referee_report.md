# External Referee Report — R30

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article:** Certified Bellman Operators with Neural Proposals: Adaptive Verification and Costly Policy Revision  
**Repository:** TrillionniumFoundation/NBO  
**Reviewed branch:** revision/econometrica-r30-adaptive-certification-2026-09-24  
**Reviewed HEAD:** 3394815f4ccbf5917582c8f756b535adf87783cc  
**Review branch:** review/econometrica-r30-numerical-methods-2026-09-24-3394815  
**Date:** 2026-09-24

## 1. Recommendation

**Reject in the present form.**

R30 is a substantial revision. It directly addresses several of the most serious objections raised against R29: it no longer treats universal post-repair success as approximation efficacy; it introduces whole-region certificates rather than mandatory state enumeration; it puts an explicit discounted occupancy-weighted cost on policy revision; it includes strong information-matched classical controls; it constructs a genuinely active stopping-boundary calculation; and it is unusually candid about the original full-domain target remaining unresolved. I do not regard this as a cosmetic response-letter revision.

The negative recommendation is nevertheless clearer after R30, not weaker. The new results identify precisely what is still missing for an Econometrica-level numerical-method contribution.

The central problem is that the paper has not demonstrated a sub-enumerative Bellman method on a problem for which Bellman coupling is actually difficult. The only end-to-end new regional experiment deliberately makes the transition law independent of the action. Continuation values therefore cancel exactly from every action comparison, and the optimal policy is the pointwise sign rule a*(x)=1{f(x)>=0}. The paper itself implements that exact symbolic rule and an online exact budget guard. Those classical controls solve the same continuous family without state enumeration, without neural fitting, and without constructing the finite regional proof object. In this setting the regional certificate is a valid representation and verification device, but it does not change which economic dynamic program can be solved.

The general theory does not yet close this gap. The regional comparison theorem is conditional on supplied global lower/upper witnesses, and the preservation class additionally requires own-policy values. Constructing those objects can be as hard as the dynamic program that the method is supposed to avoid. The complexity proposition explicitly leaves witness construction outside the range-oracle count. R30 therefore establishes that verification can be cheap **conditional on already having globally valid objects with favorable geometry**; it does not establish that the complete certified solution pipeline is sub-enumerative on a genuinely coupled dynamic program.

The economically weighted revision theorem is also not tested in the regime where its dynamic content matters. In the implemented operating-mode economy, the state law is independent of the deployed action, so occupancy is fixed and the minimum-intervention problem collapses to a pointwise guard. The paper's own exact online guard attains the local-class minimum. Thus the numerical experiment does not test the policy-dependent occupancy tradeoff that motivates the general recursion.

Finally, the original stopped consumption-portfolio problem remains unsolved at the declared standard. The retained whole-domain upper bound is 7.181834580823298 against a target of 0.01, and the 47-coordinate current-state derivative/residual bridge is still absent. The new killed-kernel calculation is a technically meaningful boundary diagnostic, but it is one restart, fixed consumption and portfolio choice, and a constant scalar adjustment. It does not turn the original economic problem into a certified policy computation.

I therefore view R30 as a technically careful collection of verification results and diagnostics with markedly improved scientific discipline, but not yet a numerical method that changes the frontier of computable economic dynamic programs.

## 2. Status of the revision relative to R29

The reviewed R30 head is 17 commits ahead of the R29 referee-integration object. This is a genuine scientific revision.

The strongest R29 objection was that exact completion scanned essentially the same finite Bellman object as dynamic programming while adding neural fitting and verification cost. R30 correctly preserves those adverse results rather than rewriting them. In the inherited benchmark, the full proposal-to-certificate pipeline remains approximately 63.19, 33.63, 22.91, 13.43, and 10.91 times the independently implemented exact DP at the reported nontrivial scaling points.

R30 then adds a different one-dimensional operating-mode family to demonstrate regional certification. That move is legitimate, but the new family changes the computational question so strongly that it does not demonstrate the missing result from R29. The relevant distinction is not merely “finite grid versus continuum.” It is “genuinely coupled Bellman computation versus a problem whose action comparison is analytically local.”

The revision also fixes the previous stopped-boundary weakness. At the new restart, the lower-boundary exit probability is approximately 0.689 at theta=0, and the validated derivative intervals exhibit a curvature sign change. That is real progress. It should not, however, be counted as evidence for the regional Bellman algorithm, because the calculation is a separate scalar constant-control diagnostic.

## 3. What I find technically credible

Several parts of R30 deserve to be preserved in any future version.

First, the regional comparison theorem is a clean sufficient certificate. If the displayed Bellman inequalities hold on every region, the resulting pointwise order and regret envelope follow by standard monotonicity and backward induction. I found no obvious logical defect in that argument.

Second, the paper now states the scope of the certified preservation class correctly. The minimum-cost recursion is an optimization over a conservative inner class, not a theorem that the selected policy globally minimizes intervention cost over every policy satisfying true regret <= epsilon. This is an important correction.

Third, the exact-rational compilation discipline is careful. The paper distinguishes floating-point training, exact interpretation of stored binary64 coefficients as rational constants, the compiled piecewise-constant policy, and actual hardware neural evaluation. It does not pretend that the latter is certified.

Fourth, the new stopping calculation is much stronger than the earlier central-state example. The lower boundary is economically active, the distant opposite boundary is explicitly bounded, the utility-series remainder is explicit, and the first failed nested integration attempt is retained rather than hidden. The resulting payoff and derivative intervals appear to be treated as validated enclosures rather than decimal quadrature output.

Fifth, R30 includes strong controls even when they undermine the desired narrative. In particular, the exact symbolic sign policy and online guard make the limitations of the operating-mode example transparent. That is excellent scientific practice.

These strengths are why the present rejection is not a claim that the mathematics is careless. The issue is the level and nature of the contribution.

## 4. Blocking scientific findings

### R30-F1 — The general regional certificate is a verifier for supplied witnesses, not yet an end-to-end sub-enumerative solver

The paper's headline methodological move is to replace state enumeration by regional inequalities. But the regional comparison theorem assumes globally valid L and U, and the preservation class uses v0=J(pi0) in addition to U. The manuscript explicitly says that witness construction, own-policy evaluation, integration, compilation, serialization, and final verification are additional costs.

That qualification is correct, but it is also decisive. For a general action-dependent dynamic program, constructing a Bellman supersolution U with useful slack, constructing a lower witness, or evaluating J(pi0) over the relevant continuous state domain can require essentially the same numerical machinery as solving or accurately approximating the original value problem.

The geometry-dependent work proposition counts the regional range work once the objects to be bounded are already available. It does not prove that those objects can be constructed sub-enumeratively, nor that their total construction cost is smaller than a strong classical approximate or verified dynamic program.

**Required correction:** provide an end-to-end algorithm, including witness construction, and analyze or measure its total complexity on a problem where the witnesses are not analytically given. A future theorem should state the cost of producing the certificate inputs, not only the cost of checking them.

### R30-F2 — The new numerical family removes the Bellman difficulty that the paper is supposed to solve

In the operating-mode economy, transitions are action independent. Therefore all continuation terms cancel from action comparisons at every date and at every rollout depth. The optimal action is simply the sign of a low-degree polynomial f(x).

This is not a minor convenience. It eliminates the central dynamic coupling. There is no action-dependent effect on the next-state distribution, no endogenous continuation tradeoff, no policy-dependent value surface needed to decide the action, and no hard Bellman maximization left after the primitive reward is known.

Consequently, certifying a continuum here demonstrates exact regional inequality machinery, but not a numerically difficult Bellman computation.

**Required correction:** test the method on a prospectively fixed economic dynamic program with action-dependent transitions or otherwise nontrivial continuation dependence, where the optimal action cannot be reduced analytically to a pointwise primitive sign test.

### R30-F3 — The paper's own strongest controls dominate the new example

R30 correctly implements two controls that are stronger than the proposed neural-plus-regional pipeline in the new family:

1. the exact symbolic sign policy a*(x)=1{f(x)>=0}, which has zero regret; and
2. the online exact budget guard, which retains the installed action exactly when the local loss is within eta and attains the minimum intervention cost in the local-loss class.

Neither requires state enumeration. The online guard also requires no offline region construction. The supplement explicitly states that the finite cover is an offline proof object and alternative deployment representation, not a lower-intervention-cost method than the guard.

The timing table points in the same direction. Median neural total versus the matched structural solver is approximately:

| Gain | Neural total (s) | Structural (s) | Neural / structural |
|---|---:|---:|---:|
| Linear | 0.04901 | 0.002272 | 21.57x |
| Cubic | 0.1156 | 0.01557 | 7.42x |
| Quadratic | 0.08557 | 0.006683 | 12.80x |

For cubic and quadratic, the neural total is also approximately 2.33x and 2.38x the reported vectorized 2^20-state grid DP, respectively. The exact symbolic sign control is stronger still and is not the slow structural row in that table.

Thus the new experiment demonstrates that a regional proof object can be constructed. It does not demonstrate that the proposed pipeline is the numerically attractive way to solve or certify the displayed problem.

**Required correction:** show a model in which the proposal materially reduces total certified-solution work relative to the best information-matched classical method, or explicitly reposition the contribution as verification/representation rather than a competitive solver.

### R30-F4 — The implemented intervention-cost problem avoids policy-dependent occupancy

The theorem defines revision cost under the occupancy measure induced by the deployed policy. That is potentially interesting: changing an action can alter future state visitation, so the cost-minimization problem can itself be genuinely dynamic.

The implemented example does not test that mechanism. Because transitions are action independent, occupancy is independent of the revised policy. The minimum-cost problem therefore decomposes pointwise, and the exact online guard solves it directly.

This is a major mismatch between the general theorem and the numerical evidence. The part of the theorem that could create an economically nontrivial dynamic tradeoff is absent from the application.

**Required correction:** include an action-dependent model in which revisions change future occupancy and demonstrate the certified-cost Bellman recursion end to end. Report how the optimal revision pattern differs from a pointwise or fixed-occupancy rule.

### R30-F5 — The 2^40 statement is a cardinality observation, not evidence of large-scale dynamic programming capability

The paper is formally careful: it says that the continuum certificate also covers any midpoint grid, including 2^40 states, and explicitly says that it did not run a trillion-state dynamic program. That caveat should remain.

Nevertheless, the rhetorical force of the 2^40 number is too strong relative to the computational content. In this family one should not materialize a trillion-state grid in the first place: f is an explicit low-degree polynomial, the transition structure cancels from action comparisons, and the exact sign rule solves the continuous problem directly.

Avoiding an absurd discretization is not evidence that the proposed method scales to a difficult state space.

The dimensional statement is also limited. The complexity proposition itself notes that a codimension-one unresolved surface in d dimensions can produce s=d-1. No high-dimensional regional experiment is supplied.

**Required correction:** remove the trillion-state comparison from any headline scalability claim unless paired with a genuinely nontrivial action-dependent continuous-state model. Report dimension, boundary geometry, certificate size, witness cost, memory, and total solve/certification work as dimension grows.

### R30-F6 — Neural proposals remain scientifically incidental

The new cohort is more disciplined than the R29 evidence, but it does not establish a role for neural approximation.

Raw neural passes are 19/20 for the linear gain, 0/20 for the cubic gain, and 7/20 for the quadratic gain: 26/60 overall. By contrast, all three polynomial controls meet the raw .01 criterion, with displayed raw regret upper bounds at approximately 10^-12 and very small fitting/certification costs. The polynomial degree is known and the target observed at the same 512 points is itself a polynomial of that degree.

More fundamentally, the exact symbolic sign rule solves all three models without learning.

The correct conclusion from these experiments is that neural proposals are one possible incumbent representation. They are not an enabling numerical ingredient in the demonstrated method.

**Required correction:** either remove neural emphasis from the paper's identity or supply a problem where a neural proposal has a measurable end-to-end advantage in constructing a certificate that a strong classical proposal cannot match at comparable information and cost.

### R30-F7 — The general complexity theorem is too conditional to carry the main numerical claim

Proposition 5's work bound is mathematically reasonable as a counting statement for a hierarchical verifier. But the favorable O(KL) specialization assumes fixed-degree univariate polynomial structure, simple isolated threshold crossings, and finitely many candidate pieces.

Those assumptions are very close to the special structure that makes the implemented example easy. The proposition does not establish favorable complexity in the high-dimensional nonlinear models for which neural methods would be most relevant. The manuscript correctly notes that s can become d-1; that observation sharply limits the scalability implication.

There is also no theorem relating proposal approximation quality to certificate geometry in a way that yields an end-to-end speedup over a classical solver. “A good proposal can simplify the cover” is plausible but remains unquantified at the level needed for the paper's numerical-method thesis.

**Required correction:** derive a result that connects proposal error/margin structure to certificate work, including witness-construction cost, or provide a convincing empirical scaling study on coupled problems where the measured geometry behaves favorably.

### R30-F8 — The original full-domain economic target remains essentially untouched

The original target is still

sup over all restart states and dates of V_2 - J_2^pi <= 0.01

for a current-state actor in the stopped consumption-portfolio economy.

The retained whole-domain bound remains 7.181834580823298, approximately 718.18 times the target. The 47-coordinate derivative/residual bridge is still uninstantiated. No R30 result reduces this global bound.

The manuscript is admirably explicit about this fact. But explicit acknowledgment of an unresolved central target does not itself create progress toward that target.

**Required correction:** either make a material numerical advance on the original all-domain current-state problem, or demote it to motivating background and stop asking the reader to evaluate the regional toy family and the original continuous economy as two halves of one solved numerical program.

### R30-F9 — The active-boundary calculation is a strong diagnostic, but it is not yet a policy-computation result

The new stopping calculation fixes one restart, k=2, c=3/4, p=0, and constant theta. It evaluates five predeclared theta values. This is a much better stress test of boundary effects than the R29 central restart: exit is material and curvature changes sign.

But the calculation does not locate the global scalar optimum, prove interval-wide monotonicity, solve the unrestricted control problem, or certify a current-state feedback policy. The manuscript correctly says so.

Accordingly, this section supports the claim “boundary behavior invalidates a transferred concavity assumption.” It does not support the claim “the proposed Bellman method solves the stopped economic problem.”

**Required correction:** if this material remains central, turn it into a complete verified scalar optimization or, preferably, connect the validated boundary machinery to a genuine feedback-control certificate. Otherwise move it to a diagnostic/supporting section.

### R30-F10 — The 60/60 intervention-price comparison is mechanically driven by an uncalibrated illustrative shadow price

The paper reports that among neural comparisons with positive saved intervention cost, the largest break-even revision price is below 0.000739. It then reports that at lambda=1/20=0.05, all 60 paired comparisons favor the completed policy over the near-exact structural policy after intervention cost.

But 0.05 is more than 67 times the largest stated break-even threshold. The 60/60 count is therefore not surprising evidence about economics; once the price is chosen that far above every threshold, the sign is largely predetermined.

The protocol amendment correctly says that lambda=1/20 is illustrative and not a preregistered monetary estimate. The main text should go further: the scientifically meaningful object is the break-even curve or threshold distribution, not the universal sign at a deliberately large illustrative value.

**Required correction:** remove 60/60 as a headline economic success statistic. Calibrate revision costs to an actual economic interpretation if possible, or present transparent sensitivity over lambda without privileging an arbitrary point.

### R30-F11 — The theorem-level novelty remains too close to classical comparison and constrained dynamic programming

R30 improves the literature discussion and correctly says that Bellman comparison, residual bounds, rollout, and policy improvement are classical. The remaining mathematical additions are:

- packaging regional inequalities as checkable whole-set witnesses;
- defining a conservative admissible action set from those witnesses;
- minimizing an additive revision cost by Bellman recursion within that class; and
- counting range-oracle work as a function of unresolved-region geometry.

These are useful constructions. But the paper does not yet establish that they yield a new numerical capability beyond classical verified dynamic programming, a posteriori Bellman bounds, or constrained Markov dynamic programming once the certified action sets are supplied.

The cost recursion in particular becomes standard dynamic programming after B(e) is fixed. The difficult object is the construction of B(e), and that is precisely where the paper's only complete implementation relies on analytic cancellation.

**Required correction:** sharpen the theorem-level delta against the closest verification and constrained-DP literature. A stronger novelty case would be a theorem showing that the proposed construction obtains a certificate or cost-optimal repair under weaker information or lower verified complexity than an established alternative.

### R30-F12 — The paper still lacks one dominant theorem-to-hard-application chain

R30 is more coherent than R29, but two largely separate papers remain inside the submission.

Track A is a regional certificate plus minimum-revision framework, demonstrated on an analytically reducible one-dimensional operating-mode model.

Track B is a validated killed-kernel derivative diagnostic for one scalar constant-control slice of the original stopped economy.

Track A does not solve the original stopped economy. Track B does not instantiate the regional certificate or minimum-revision algorithm. The inherited inventory evidence remains mostly a negative historical control.

An Econometrica numerical-method paper needs one chain in which the main theorem enables a computation that is genuinely difficult, the computation is compared with strong alternatives, and the resulting economic conclusion depends on the method.

**Required correction:** build one such chain and make it dominant. The current breadth does not compensate for the missing hard application.

## 5. Quantitative interpretation of the new evidence

The new data should be read more conservatively than the present narrative sometimes invites.

The linear family is so simple that 19/20 raw neural proposals already pass and the exact sign rule is immediate. The regional certificate is inexpensive, but the median full neural pipeline is still roughly 21.6 times the structural solver.

The cubic family is the most revealing neural stress case: 0/20 raw neural proposals pass. Median certificate size is 112 cells with 83–286 bound calls. The median neural total is about 7.4 times the structural solver and about 2.33 times the displayed 2^20 vectorized DP. Certification succeeds because exact model structure repairs or resolves the proposal; that is useful verification, but not evidence that learning has made the problem easier to solve.

The quadratic family is intermediate: 7/20 raw passes. The median neural total is about 12.8 times the structural solver and about 2.38 times the 2^20 vectorized DP.

The polynomial controls are especially important. They exploit the known low-degree structure and meet the raw target essentially exactly on all three functions. In the model actually studied, they are closer to the natural numerical representation than the neural networks.

These outcomes do not invalidate the regional certificate theorem. They show that the chosen empirical family cannot establish the intended computational value proposition.

## 6. Technical comments

### R30-T1 — Separate certification complexity from certificate-input complexity in every theorem statement

The current prose acknowledges extra costs, but the headline complexity result can still be read too strongly. State explicitly which objects are assumed given, what it costs to construct each one, and which costs may scale like a Bellman solve.

### R30-T2 — Give a nontrivial construction for U, L, and v0

The next revision should not only say that an enclosure can replace exact evaluation. It should implement such a construction in a coupled model and show that it remains cheaper than the competing certified solver.

### R30-T3 — Report amortization against the online guard, not only grid DP

The finite regional cover could have value if a verified offline representation is reused for many deployments. That is a legitimate possible advantage. Quantify the break-even number of policy queries relative to the exact online guard, including raw-policy evaluation, rational comparison cost, certificate loading, and memory.

### R30-T4 — Do not treat state-cardinality independence as dimension independence

The manuscript already contains this caveat, but it should be visible wherever 2^40 appears. A one-dimensional continuum certificate is a statement about representation and analytic structure, not a solution to high-dimensional state explosion.

### R30-T5 — Exercise policy-dependent occupancy

Use a model where changing the policy changes transition probabilities and therefore future intervention exposure. Otherwise the main economic-cost theorem is not being numerically tested.

### R30-T6 — Make the role of the proposal quantitative

A useful theorem or empirical diagnostic would relate margin, proposal error, number/measure of disagreement regions, and verified work. At present proposal quality, certificate size, and total solve cost are juxtaposed rather than causally linked.

### R30-T7 — Keep exact compiled deployment separate from hardware neural deployment

The current distinction is correct. Do not weaken it in future abstracts or conclusions. If hardware neural execution becomes part of the claimed object, an end-to-end floating-point enclosure is required.

### R30-T8 — Clarify the economic units of revision cost

The priority weight 1+x and lambda=1/20 are useful demonstrations of machinery but do not yet have an empirical or institutional interpretation. If the economic claim is important, explain what one unit of intervention cost means and why the chosen scale is relevant.

### R30-T9 — Turn the boundary diagnostic into a complete optimization statement if it remains a pillar

Five derivative evaluations establish important local shape information, not a verified optimum. A full interval search with derivative enclosures or another global certificate would make this component substantially stronger.

### R30-T10 — Compress historical material further

Preserving the complete lineage in HISTORY_R30 is excellent for auditability. The main paper should not ask the reader to carry the conceptual burden of legacy transport, rollback, old inventory completion, the new regional toy model, and the scalar boundary calculation simultaneously. Historical preservation and editorial focus are compatible.

## 7. Minimum bar for a materially stronger submission

I would not recommend another incremental response-letter round on the present empirical architecture. A materially stronger submission should satisfy most of the following conditions:

1. Introduce a prospectively fixed, action-dependent continuous-state economic dynamic program in which continuation values do not analytically cancel and no exact pointwise sign rule solves the problem.
2. Construct the regional witnesses and any own-policy value enclosures algorithmically, charge their full cost, and demonstrate that the complete certificate can be obtained without reverting to full state-action enumeration.
3. Compare end-to-end time, memory, model queries, arithmetic precision, and certificate size against the strongest information-matched classical verified method.
4. Demonstrate a genuine regime in which a proposal improves total certification complexity. If neural proposals remain in the title, show that they add value relative to polynomial, sparse-grid, local-basis, or other natural proposal classes.
5. Exercise the minimum-revision recursion under action-dependent occupancy, where the optimal intervention policy is not the pointwise online guard.
6. Either materially advance the original stopped consumption-portfolio all-domain target, or separate that program from the regional-certification paper.
7. If the active-boundary calculation remains central, complete a verified optimization or feedback-control result rather than stopping at five derivative diagnostics.
8. Present intervention-cost conclusions through calibrated costs or full threshold/sensitivity curves rather than a universal count at an arbitrary illustrative lambda.
9. Reframe the 2^40 statement as a representation fact unless a difficult coupled model justifies a scalability interpretation.
10. Rework the introduction around one theorem-to-computation-to-economic-conclusion chain.

## 8. Recommendation to the editor

**Reject in the present form.**

R30 deserves credit for responding seriously to the previous reports. In fact, the revision has done something scientifically useful: by adding the right classical controls and narrowing the claims, it reveals that the remaining issue is no longer one of rhetoric, reproducibility, or obvious theorem correctness.

The remaining issue is substantive. The paper has not yet shown that its regional certification machinery makes a genuinely difficult Bellman problem cheaper or newly feasible to solve. Its only complete new regional experiment is analytically reducible, its own exact structural controls dominate that experiment, and its intervention-cost application removes policy-dependent occupancy. The original difficult continuous economic target remains far outside the certified tolerance.

A publishable numerical-method paper may emerge from this framework if the authors can demonstrate end-to-end certified advantage on a coupled economic dynamic program. R30 does not yet provide that demonstration.

## 9. Source map inspected

### Current R30 submission object
- ECTA_R30.tex / ECTA_R30.pdf
- SUPP_R30.tex / SUPP_R30.pdf
- RESPONSE_R30.tex / RESPONSE_R30.pdf
- COMPUTATION_R30.tex / COMPUTATION_R30.pdf
- R30_REVIEW.md
- revisions/2026-09-24-r30/PUBLICATION_MANIFEST.json
- revisions/2026-09-24-r30/PROTOCOL.md
- revisions/2026-09-24-r30/PROTOCOL_AMENDMENT_01.md
- revisions/2026-09-24-r30/disposition.json

### Main theorem and exposition sources
- revisions/2026-09-24-r30/paper/main.tex
- revisions/2026-09-24-r30/paper/supplement.tex
- revisions/2026-09-24-r30/paper/references.tex

### Generated evidence
- revisions/2026-09-24-r30/paper/generated/summary.tex
- revisions/2026-09-24-r30/paper/generated/costs.tex
- revisions/2026-09-24-r30/paper/generated/economics.tex
- revisions/2026-09-24-r30/paper/generated/stopping.tex
- revisions/2026-09-24-r30/paper/generated/bracketing.tex
- revisions/2026-09-24-r30/paper/generated/detailed.tex
- revisions/2026-09-24-r30/paper/generated/legacy.tex

### Replication/source implementation inspected
- revisions/2026-09-24-r30/replication/adaptive.py
- revisions/2026-09-24-r30/replication/structural.py
- revisions/2026-09-24-r30/replication/economics.py

### Prior referee baseline
- reviews/2026-09-24-econometrica-r29-second-pass/referee_report.md
- R29 manuscript head 788246778893695471015ce4db76e6a61a2c9ca0

The report reviews the exact R30 head identified above and does not modify any revision branch.
