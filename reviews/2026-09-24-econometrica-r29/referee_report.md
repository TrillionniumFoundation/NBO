# External Referee Report — Neural Bellman Operators (R29)

**Venue standard:** Econometrica-level numerical / computational methodology  
**Recommendation:** **Reject in the present form. The revision is now unusually auditable and several individual arguments are technically respectable, but the central numerical-method claim is not yet strong enough for Econometrica. The decisive problem is no longer reproducibility. It is that the certified completion stage performs exhaustive exact-model dynamic-programming work, is empirically dominated by exact dynamic programming on every reported scaling point, and is doing essentially all of the work needed to obtain the stated 0.01 guarantees once the raw neural policies cease to be accurate.**  
**Review date:** 2026-09-24  
**Reviewed repository:** TrillionniumFoundation/NBO  
**Reviewed revision branch:** revision/econometrica-r29-referee-copy-2026-09-24  
**Reviewed head:** 788246778893695471015ce4db76e6a61a2c9ca0  
**Equivalent integration head:** revision/econometrica-r29-referee-integration-2026-09-24 at the same SHA  
**Review branch:** review/econometrica-r29-numerical-methods-2026-09-24-7882467

I reviewed the exact R29 referee object, the R28-to-R29 commit difference, the article, supplement, point-by-point response, computational appendix, historical annex, R29 protocol and amendment, source code, frozen result records, generated tables, provenance checks, and the preceding R27 numerical-methods report. I also checked the repository-level validation record for the exact reviewed head.

The exact-head read-only GitHub Actions validation is a genuine improvement over the previous review cycle. Run 35932676059, “R29 exact-head validation,” is tied to reviewed SHA 788246778893695471015ce4db76e6a61a2c9ca0 and completed successfully. I therefore do **not** base the present recommendation on a packaging, compilation, or missing-CI objection.

The scientific problem is harder.

---

## 1. Executive assessment

R29 is a material revision. The authors have done many things that I asked for in R27:

- the paper is now a complete, reviewable object;
- the raw failed policies are retained;
- the post-diagnostic status of the completion construction is disclosed;
- random, myopic, base-stock, truncated-tabular, polynomial, and neural proposals are subjected to the same completion operators;
- state/time correction topology is recorded;
- exact rational arithmetic is used for the finite-state certificate;
- exact dynamic programming is retained as a visible baseline;
- the state space is extended to 16,384 states per time slice;
- projected box stationarity is stated correctly rather than replacing constrained stationarity by a zero-gradient claim;
- a stopped one-dimensional slice of the original economy is given a rigorous derivative/oracle treatment;
- the historical-transport control has been repaired so that it no longer drops the nonlinear remainder;
- rollback is tested on matched gated/ungated production schedules;
- the original whole-domain failure, 7.181834580823298 versus 0.01, remains visible;
- and the exact reviewed commit has a successful clean validation run.

These are serious improvements.

They also make the central weakness much easier to see.

The finite-state completion result is not a scalable neural solution method. It is an exact-model, all-state, all-action backward repair procedure. At every state it evaluates all feasible actions against an exactly evaluated completed suffix and replaces the candidate action by an exact greedy action whenever the candidate consumes too much of the prescribed error budget. At epsilon equal to zero, this procedure collapses conceptually to backward optimal dynamic programming up to optimal-action ties. At positive epsilon, it is an approximate dynamic-programming sweep with an action-retention rule.

That can be a valid algorithmic object. But its numerical value must be demonstrated relative to solving the dynamic program directly.

R29 does not do so. In fact, its own strongest table shows the opposite. At every reported state-space size, exact dynamic programming is cheaper than completion plus certification, even before neural training is charged. Once neural training is charged, the gap becomes large. On the largest graph, exact DP takes 5.495 seconds. The reported neural fit takes 51.6 seconds, budget repair 3.677 seconds, and verification 4.668 seconds. Thus the visible neural-plus-certified pipeline already costs about 59.945 seconds before several other cost categories, versus 5.495 seconds for the exact solution. Even repair plus verification alone is slower than the exact solve.

At the same time, no raw proposal reaches the 0.01 target for any model with at least 256 states:

- d=4, L=4: 0/31 raw passes;
- d=4, L=5: 0/20 raw passes;
- d=5, L=4: 0/6 raw passes;
- d=6, L=4: 0/6 raw passes;
- d=7, L=4: 0/6 raw passes.

The high-dimensional neural raw regrets reported in the attribution table are approximately 0.2399, 0.8042, and 1.549 for d=5,6,7, respectively, against the stated 0.01 accuracy standard. The completed policies pass because the exhaustive completion theorem is designed to make them pass.

This distinction is fatal to the current paper-level interpretation. “All 286 completed variants certify” is primarily a consistency check of a deterministic theorem and implementation, not empirical evidence that neural approximation solved 286 difficult Bellman problems.

The strongest empirical fact about the neural stage is instead that a learned candidate can sometimes be converted to a certified table with far fewer action replacements than crude baselines. On the d=7 graph, the budget rule changes 634 out of 131,064 nonsettled state-time decisions for the neural candidate, versus 114,341 for the myopic candidate.

That is interesting, but the paper never establishes that preserving raw actions is itself an economically meaningful or computationally valuable objective. The completion scan has to enumerate the entire model whether it changes 634 actions or 114,341 actions. Exact DP is still cheaper. The action-edit count is therefore a syntactic similarity statistic, not yet a numerical efficiency criterion.

For an Econometrica-level numerical-method paper, that is not a small missing robustness exercise. It is the central methodological gap.

---

## 2. What R29 has genuinely fixed

Before listing the blocking findings, I want to separate resolved objections from unresolved ones.

### 2.1 The submission object is now real and auditable

Unlike R27, R29 has a complete article, supplement, response, computational appendix, historical annex, replication code, frozen result hierarchy, hash manifests, build record, and exact-head validation workflow.

The reviewed SHA has a successful read-only exact-head validation run. This resolves the former “protocol rather than paper” objection.

### 2.2 The finite-state arithmetic is materially stronger

The inventory calculations use arbitrary-precision integer recursions and exact Fraction comparisons. Printed decimals are not used to decide a certificate. The independent reference recursion is separately implemented as a scalar primitive transition loop rather than calling the vectorized certificate routines.

The tests check:

- all 115 raw candidates;
- all 286 completed variants;
- policy feasibility;
- absorbing-state semantics;
- exact candidate and completion hashes;
- reference-creation ordering;
- pointwise policy-value preservation;
- all-state envelope validity against the independently generated optimum;
- tolerance acceptance;
- and edge cases.

I did not find an obvious contradiction between the finite-state completion theorem and the implementation.

### 2.3 The paper now states several negative results honestly

The manuscript explicitly says that:

- exact tabular DP is highly competitive;
- completion is not a way around tabular complexity;
- the finite graph is not a discretization certificate for the original diffusion;
- the completed deployment object is the repaired action table, not necessarily the neural network;
- the original 0.01 full-domain objective is not closed;
- the 47-dimensional financed derivative bridge is not instantiated;
- and the rollback experiment does not prove solver superiority.

This transparency is valuable.

Unfortunately, once these caveats are accepted, the remaining positive Econometrica-level methodological contribution is much narrower than the title and architecture of the paper suggest.

---

## 3. Blocking scientific findings

### R29-F1 — The headline “286/286 certified” result is guaranteed by construction and is not an efficacy experiment

The completion procedure examines every feasible action at every state using the exact model and the exactly evaluated completed suffix. If the frozen candidate action exceeds the allowed local deficit, it is replaced by an exact maximizing action.

Theorems 1/2 then guarantee the prescribed all-state/all-restart tolerance.

Consequently, once the assumptions and implementation are correct, a feasible input policy is **supposed** to become certifiable. A random policy, myopic policy, polynomial policy, or neural policy can all be repaired.

This makes the statement that all 286 variants meet their requested tolerance qualitatively different from saying that 286 learned policies independently solved an unknown control problem.

The 286/286 statistic is primarily:

1. a theorem-implementation consistency test;
2. an audit of exact arithmetic and stopping semantics;
3. an audit that the fixed cohort was processed without selective dropping.

Those are useful reproducibility facts. They are not evidence of solver accuracy.

**Required correction:** stop using the universal post-completion pass rate as a headline numerical success metric. The empirical quantities that can identify method value are total work, memory, raw quality, correction burden under an economically meaningful edit cost, and performance against strong algorithms at matched information.

### R29-F2 — Exact dynamic programming dominates the certified pipeline on every reported scaling point

This is the most important numerical result in the paper, and it is adverse to the paper’s intended positioning.

The main scaling table reports:

| d/L | States | Exact DP | New neural | Fixed repair | Budget repair | Verify |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/4 | 16 | 0.001072 | — | 0.001992 | 0.002268 | 0.001611 |
| 3/4 | 64 | 0.00803 | — | 0.007419 | 0.008217 | 0.006628 |
| 4/4 | 256 | 0.03729 | 2.291 | 0.02754 | 0.03296 | 0.03244 |
| 4/5 | 625 | 0.103 | 3.28 | 0.08989 | 0.1022 | 0.08187 |
| 5/4 | 1,024 | 0.2064 | 4.424 | 0.1365 | 0.1498 | 0.1556 |
| 6/4 | 4,096 | 1.103 | 13.33 | 0.6438 | 0.6971 | 0.7865 |
| 7/4 | 16,384 | 5.495 | 51.6 | 3.282 | 3.677 | 4.668 |

Two facts follow.

First, **repair plus verification alone is more expensive than the exact DP solve at every displayed scale.** The neural fit is not needed to establish this negative comparison.

Second, once neural fitting is charged, the certified neural pipeline is much slower. At d=7, the visible fit + budget repair + verify total is about 59.945 seconds versus 5.495 seconds for exact DP, roughly an order of magnitude slower before other standalone costs are added.

The comparison is especially damaging because the independent DP reference is deliberately implemented with scalar loops for audit independence rather than as an aggressively optimized solver. A highly optimized classical implementation could plausibly widen, not shrink, this gap.

The manuscript says this honestly. But it never resolves the resulting question:

**Why should an economist run the neural proposal and completion pipeline instead of simply solving the dynamic program?**

At present there is no numerical answer.

**Required correction:** demonstrate a regime in which the proposed learned-plus-certified method provides a substantive advantage over the strongest information-matched classical solver. That advantage could be total wall time, memory, amortized multi-query cost, ability to operate when the exact solve is infeasible, or a formally valued policy-retention criterion. None is established here.

### R29-F3 — The raw neural approximation stops meeting the stated tolerance exactly where the scaling exercise becomes nontrivial

The all-state/all-restart raw pass counts are:

- 8/23 at 16 states;
- 4/23 at 64 states;
- 0/31 at 256 states;
- 0/20 at 625 states;
- 0/6 at 1,024 states;
- 0/6 at 4,096 states;
- 0/6 at 16,384 states.

Thus every d>=4 success at tolerance 0.01 is a post-repair success.

The single high-dimensional neural proposal has raw worst regret:

- 0.2399 at d=5;
- 0.8042 at d=6;
- 1.549 at d=7.

The d=7 raw error is about 155 times the target tolerance.

This does not make the neural candidate useless: a small set of action corrections may repair a large worst-state loss. But it does mean that the central 0.01 accuracy claim at scale belongs to the exact-model completion operator, not to neural approximation.

**Required correction:** make the raw-versus-completed distinction central to the abstract and main results, not merely explicit in caveats. If the neural proposal is intended to carry methodological value, quantify that value in a metric that matters to total computation or economic deployment.

### R29-F4 — “Policy preservation” is not yet an economic or numerical objective

The new residual-budget theorem is described as a policy-preservation operator. It does preserve many more raw actions than crude policies in the reported experiments.

But there is no reason, inside the stated economic problem, to prefer a policy that is close in Hamming distance to a neural proposal over an exact optimal policy.

No cost is attached to:

- changing an action table entry;
- changing a decision at a rarely visited state;
- changing a decision at a likely state;
- changing early versus late decisions;
- retraining or redeploying the policy;
- policy interpretability;
- switching an installed controller;
- or preserving organizational/business constraints associated with the incumbent policy.

The theorem is also explicitly **not** a global minimum-edit theorem.

This matters because the largest-graph example is rhetorically powerful but economically ambiguous. The budget rule changes only 634 of 131,064 nonsettled neural decisions, yet the raw worst regret is 1.549. A tiny unweighted edit fraction can therefore correspond to a huge change in the worst-case economic guarantee.

The current action-preservation statistic is a descriptive similarity measure. It is not a welfare criterion.

**Required correction:** either:

1. formulate a genuine optimization problem such as minimizing a stated weighted intervention/edit cost subject to a uniform regret constraint, and analyze the proposed operator relative to that problem; or
2. provide a deployment setting in which action preservation has a measurable computational or economic value; or
3. demote “preservation” from a central methodological contribution.

### R29-F5 — The neural stage does not dominate the simpler approximation controls

The expanded attribution table is useful precisely because it weakens a neural-specific interpretation.

Examples:

- At d=3, the two polynomial candidates have raw regret max 0 and require zero repair, while the neural group has raw regret max about 0.01418 and nonzero corrections.
- At d=4, L=5, the polynomial group has raw regret max about 0.1925 versus about 0.3664 for the neural group, and a smaller budget correction fraction.
- At d=4, L=4, polynomial and neural raw regret maxima are essentially the same, while the polynomial correction fraction is smaller.
- At d=5 through d=7, there is only one neural scaling seed and one degree-two polynomial candidate, so the apparent ordering is not a robust comparison.

The paper correctly says it does not prove neural superiority. But then the title “Neural Bellman Operators” and the amount of manuscript devoted to neural geometry become difficult to justify.

The finite-state result appears to be a **representation-independent certified policy-completion method** with neural proposals as one optional source of inputs.

**Required correction:** either establish a reproducible neural-specific advantage under a relevant metric, or reposition the paper around certified Bellman completion and treat neural networks as one proposal mechanism among several.

### R29-F6 — The scaling study does not test the scalability that would justify approximation

The largest finite graph has 16,384 states per time slice. That is a useful extension of the earlier 256-state benchmark, but it is still comfortably solved by the exact reference in seconds.

More importantly, both completion and certification enumerate the full finite model. Their logical work is of the same tabular state-action-successor order as dynamic programming.

Therefore increasing the graph until exact DP becomes impossible will also make the current exact completion/certificate impossible unless some new structural or sparse mechanism is introduced.

This creates a scalability ceiling that the current experiment does not address.

The high-dimensional scaling evidence also uses one structured symmetric inventory family, horizon eight, L=4, and only one new neural seed for d=5,6,7. It is not a robustness study across economic models.

**Required correction:** provide either a sub-enumerative/sparse certification method or a problem structure under which proposal quality provably reduces certification work. Otherwise the finite-state component should be presented as an exact small-to-medium-scale auditing method, not as evidence toward high-dimensional neural Bellman computation.

### R29-F7 — The original continuous-time economic target is still missed by approximately 718×

The retained target is

sup over all states and restart times of V minus J <= 0.01.

The best retained whole-domain certificate remains

7.181834580823298.

That is about 718.18 times the target.

R29 is commendably explicit about this. But from an Econometrica perspective the consequence remains severe. The paper motivates itself with a difficult stopped consumption-portfolio problem, yet its strongest new guarantees are:

- an exact finite-state inventory completion result on a separate model;
- a one-dimensional constant-control slice of the original economy;
- a finite-width optimizer-transport identity;
- and a rollback safety check at a central restart.

There is still no end-to-end certified solution of the motivating policy problem.

**Required correction:** choose one of two coherent directions.

- If the original economy is central, materially close the whole-domain gap and instantiate the missing high-dimensional bridge.
- If the finite-state completion methodology is central, substantially shorten and reposition the continuous-time economy as motivation/diagnostic evidence rather than presenting the collection as one solved numerical architecture.

### R29-F8 — The one-dimensional stopped-control result is rigorous but too narrow to carry the continuous-control claim

The scalar slice is one of the cleaner parts of R29.

For fixed consumption, zero risky investment, one initial state, and constant preference drift, the paper gives a stopping-probability bound, likelihood-ratio derivative control, directed arithmetic, strict concavity, and a boundary/interior optimum distinction.

That is a legitimate restricted result.

It is not an instantiated high-dimensional Neural Bellman Operator, and it does not bridge to the financed 47-dimensional actor.

The direct-search work theorem is also extremely conservative in the executed case. At h=1/200, the displayed worst-case call bound is around 15.6–16.0 million calls, while the actual polls use only a handful of calls. The theorem is valid as a sufficient bound, but it is not a useful predictor of practical complexity in the example.

The expensive part of the slice is the analytic/validated oracle construction, roughly 39 seconds, not the poll itself.

**Required correction:** clarify whether the intended methodological novelty is the interval oracle, the constrained direct-search theorem, or their application. If it is a general numerical method, demonstrate it beyond one scalar class and compare it to established constrained verified optimization methods at matched precision.

### R29-F9 — The production rollback experiment validates software semantics, not economic improvement

The paired gated-minus-ungated payoff intervals are nonpositive/nonnegative overlaps in all six method/seed comparisons. Every row reports “Proved positive: no.”

Neural Adam and direct Adam produce zero rejections. Direct L-BFGS-B produces three rejections per seed, but the final printed regret upper bounds for gated and ungated arms are effectively identical.

Thus the experiment establishes that:

- the strict gate is implementable;
- a rejected state can be restored exactly;
- optimizer state hashes can be preserved;
- and the comparison can be executed without adversarial fault injection.

It does **not** establish that rollback improves economic payoff, expected performance, robustness, or total computational efficiency.

That is a software safety property, not yet an Econometrica-level numerical result.

**Required correction:** either provide prospective economic instances in which the gate demonstrably prevents a strictly certified welfare loss at acceptable cost, or move this experiment to a verification appendix and stop treating it as evidence for solver performance.

### R29-F10 — The recentered historical-transport experiment is nearly an implementation identity by construction

Proposition on recentered path equivalence assumes:

- identical carrier parameters;
- identical Adam moments and counters;
- the same economic gradient;
- the exact Jacobian pullback;
- the same parameter-space Adam recurrence;
- and recentering on the full realized network output.

Under those conditions, equality follows by induction.

The independent implementation agreement at approximately 1e-12 is a useful code-consistency test. It does not establish a new optimization algorithm.

The reported retained nonlinear remainder is roughly 1.39–1.50 in quotient-output norm, which is actually informative: it demonstrates that the earlier linearized/capped control omitted a quantitatively large object. But the repaired comparison still uses the same neural carrier and parameter-space history.

It therefore diagnoses the previous control; it does not show that neural geometry is necessary, efficient, or economically superior.

**Required correction:** recast this as a mechanism/audit result unless a distinct algorithmic consequence is proved.

### R29-F11 — The novelty claim for residual-budget completion remains under-positioned

The manuscript now states, correctly, that Bellman comparison, policy improvement, direct search, and interval arithmetic are classical.

But this creates a higher burden to isolate the nonclassical result.

The current completion rule is a backward exact action scan with:

- exact suffix-policy evaluation;
- local Bellman-gap computation;
- exact greedy replacement;
- and an error-budget bookkeeping rule that permits retaining a candidate action.

The paper needs a much sharper comparison with classical dynamic programming, rollout/policy-improvement constructions, approximate policy iteration, and Bellman-residual policy-loss bounds.

The current literature section is still too small to establish that the specific residual-budget retention rule is a field-level numerical contribution rather than a careful, useful implementation lemma built from standard dynamic-programming principles.

**Required correction:** state the nearest known theorem(s), identify the exact mathematical delta, and explain why that delta changes what can be computed or certified in a setting of economic interest.

### R29-F12 — “Reference-free” needs more precise terminology

The algorithm does not read V-star or an optimal action table. That is a meaningful provenance fact.

But it does use:

- the complete finite state graph;
- the exact reward model;
- exact transition probabilities;
- the full feasible action set at every state;
- exact suffix-policy values;
- and an exhaustive action maximization at every state.

Those are very strong model-oracle resources.

Calling the operation simply “reference-free” risks suggesting a weaker information requirement than is actually used.

A more accurate phrase would be:

**optimal-solution-reference-free, but exact-model exhaustive.**

That wording would make the distinction between “not reading V-star” and “not solving Bellman comparisons” impossible to miss.

### R29-F13 — The post-diagnostic nature of the core completion idea still limits the evidentiary interpretation

The authors are transparent that the completion amendment followed the disappointing raw experiment and that R29 is exploratory with respect to earlier outcomes.

That transparency is good.

But it means that:

- the residual-budget rule;
- the chosen controls;
- the scaling extension;
- and the emphasis on action preservation

were designed with substantial knowledge of earlier failures.

The fixed R29 cohort protects against some subsequent cherry-picking. It does not turn the research program into an independent confirmatory evaluation.

This is not a reason to discard the result. It is a reason to avoid treating the 60-fewer / 0-more / 55-same edit comparison as general evidence of an algorithmic law.

**Required correction:** for any broad empirical claim, add genuinely new economic model families fixed before execution or state the result purely as exploratory evidence.

### R29-F14 — High-dimensional neural robustness remains weak despite the expanded four-dimensional seed panel

R29 substantially improves the d=4 seed study:

- ten width-32/depth-two seeds at d=4,L=4;
- five at d=4,L=5;
- inherited architecture controls.

But the actual dimension-scaling sequence d=5,6,7 uses only a single neural seed, one architecture, one polynomial degree, one random policy, and three deterministic heuristics.

Therefore the observed high-dimensional trend cannot distinguish:

- dimensional degradation;
- seed luck;
- architecture choice;
- optimizer instability;
- or special structure of this inventory family.

**Required correction:** if the dimension plot is meant to support a scaling statement about neural approximation, use multiple seeds and at least one architecture/optimizer control at the largest dimensions. Otherwise describe d=5–7 as a deterministic pipeline demonstration, not a neural scaling study.

### R29-F15 — The paper is still several papers compressed into one

The manuscript currently contains four conceptually distinct numerical stories:

1. finite-state exact Bellman completion;
2. interval-certified constrained direct search on a scalar stopped-control slice;
3. exact historical Adam transport/recentering;
4. synchronous interval-gated rollback.

They share a broad theme of “certified computation,” but there is no theorem showing that these pieces compose into a single end-to-end solver for the motivating economy.

The result is a paper with a large audit surface but no single numerical centerpiece strong enough to dominate the reader’s attention.

The strongest finite-state theorem is not computationally advantageous over DP. The strongest continuous result is one-dimensional. The transport result is an identity. The rollback result has no proved payoff gain.

**Required correction:** choose a central theorem/algorithm and subordinate the other material to it. Econometrica does not need every historical research branch preserved inside the main methodological contribution.

### R29-F16 — The title still over-attributes the certified result to neural Bellman operators

The finite-state accuracy theorem is representation-independent.

The certified deployment object is a repaired action table.

The raw neural policies fail the 0.01 target at every d>=4 model.

The completion stage can repair random, myopic, base-stock, truncated-tabular, polynomial, and neural policies.

The classical exact solver is faster.

Under those facts, “Neural Bellman Operators” is not an accurate description of the strongest established result.

A title centered on **certified Bellman completion with learned proposals** would better match the actual theorem unless a genuinely neural-specific numerical advantage is established.

---

## 4. Technical comments on the finite-state method

### R29-T1 — State explicitly what happens at epsilon = 0

The relation to exact dynamic programming should be stated as a proposition or remark.

With zero budget, a raw action can be retained only when it is exactly greedy against the completed suffix. Otherwise it is replaced by a maximizing action. By backward induction, the resulting value is optimal.

This observation is not a criticism of correctness. It is important conceptual positioning: the method continuously interpolates between exact backward optimization and tolerance-based action retention.

### R29-T2 — Report the full certified-work ratio, not only separate stage times

For every scale, add a main-table ratio such as

(certification + repair + proposal generation) / exact DP

and, separately,

(certification + repair) / exact DP.

The latter is already unfavorable and is central to the method’s practical interpretation.

### R29-T3 — A small edit count does not reduce the present scan cost

The completion code scans the model-wide action set even when zero actions are changed.

Therefore correction fraction should not be discussed as a computational proxy unless a future sparse implementation can skip certified regions without enumerating them.

The paper correctly says this once. It should be elevated to the main interpretation.

### R29-T4 — Introduce a meaningful weighted edit metric if preservation matters

Uniform Hamming fraction assigns the same weight to:

- a never-visited terminal-near state;
- a high-probability initial-region state;
- an early decision;
- a late decision;
- a high switching-cost decision;
- and a negligible one.

If the paper wants to make preservation an economic object, define weights from occupancy, intervention cost, contractual constraints, or deployment cost, then analyze the rule under that metric.

### R29-T5 — The residual-budget rule is not shown to minimize edits

The observed 60/0/55 comparison against the fixed rule is useful but entirely empirical.

Because the current allowance depends on the completed suffix envelope, there is no theorem here that the budget rule dominates the fixed eta rule on every input.

Do not let the empirical zero-“more changes” count read like a general dominance statement.

### R29-T6 — Compare against direct truncated lookahead/rollout more seriously

The two-period tabular control is a useful first step, but it is not enough to position the proposal stage.

A natural classical competitor is deeper lookahead/rollout using the same model information and a simple terminal approximation. This is especially relevant because the completion stage itself uses exact one-step Bellman improvement.

### R29-T7 — The “independent” reference is implementation-independent, not information-independent

The scalar exact reference is appropriately coded separately from the vector certificate.

But it uses the same model primitives. This is exactly what a correctness audit should do.

Use “independently implemented exact reference” rather than language that could imply an externally independent data-generating source.

### R29-T8 — More optimized exact DP is a necessary baseline if runtime is discussed

The exact reference deliberately favors audit clarity.

Since it already wins, an optimized tabular solver should be added before any computational-efficiency statement is made. At minimum use comparable vectorization/storage strategy and report both audited scalar DP and optimized production DP.

### R29-T9 — State-space size alone is not a dimensionality result

The move from 256 to 16,384 states is useful engineering coverage.

But the model remains a finite tensor grid with a fixed horizon and simple demand support. The paper should avoid any wording that invites readers to interpret this as evidence that neural approximation has beaten the curse of dimensionality.

### R29-T10 — The exact-integer bit complexity deserves one compact asymptotic statement

The paper records bit lengths empirically. Add a concise bound showing how denominator/numerator bit lengths grow with T, D, reward denominator, and discount denominator under the implemented recursion.

The current unit-operation O(TNAD) statement is not by itself an exact-arithmetic complexity result.

---

## 5. Technical comments on the continuous-control material

### R29-T11 — The projected-stationarity theorem is a certificate theorem, not yet a competitive optimizer theorem

The result correctly distinguishes a geometric short face from an unresolved oracle call.

That is worthwhile.

But the paper should not imply that the displayed worst-case call bound explains the practical behavior of the slice. It is orders of magnitude above the observed call count.

### R29-T12 — Separate oracle-construction cost from polling cost even more aggressively

The slice takes roughly 39 seconds because it constructs and audits a rigorous analytic oracle over the whole interval.

The final coordinate polls themselves are tiny.

This is not bad, but it means the numerical contribution is primarily verified function/derivative enclosure, not search.

### R29-T13 — The financed 47-dimensional derivative bridge remains an open theorem-instantiation problem

Equation for the reduced-gradient discrepancy is a formal decomposition. R29 does not supply the constants along the actual 47-dimensional financed optimizer path.

That should remain explicitly listed as an unresolved main-model requirement.

### R29-T14 — Do not infer full-class accuracy from strong concavity of the scalar slice

The k=1/2 boundary optimum and k=2 interior optimum are rigorous within the fixed scalar class.

They do not say that c=3/4 and p=0 are close to optimal in the unrestricted stopped economy.

The manuscript mostly respects this distinction; keep it visually prominent in tables and abstract-level summaries.

### R29-T15 — Hardware floating-point deployment remains uncertified

The paper correctly says the exact compiled finite-state tables and mathematical-real network coefficients are different objects from hardware execution.

If “deployment” remains in the title/abstract narrative, either add a rounding enclosure for the actual execution path or retain the current limitation very clearly.

---

## 6. Technical comments on transport and rollback

### R29-T16 — The large nonlinear remainder should be highlighted as a negative diagnostic

The retained remainder near 1.4–1.5 is not a nuisance statistic. It explains why the earlier linearized control was not a faithful mechanism isolation.

This is one of the clearer lessons of the transport experiment.

The revised paper should emphasize that the earlier control failed because a quantitatively large nonlinear displacement was omitted, rather than presenting the exact-equivalence experiment itself as a broad new method.

### R29-T17 — An equivalence implementation should not be interpreted as an alternative optimizer

The recentered implementation uses the network carrier, its Jacobian, and the same historical parameter-space Adam state.

It is an independent implementation of the same trajectory, not a low-dimensional optimizer that replaces the neural model.

The paper currently says this, but the mechanism section still occupies disproportionate space relative to its numerical consequence.

### R29-T18 — Rollback needs a benefit criterion

The proposition that accepted intervals imply payoff improvement is trivial but correct.

The practical question is whether the gate’s avoided losses are worth its verification cost.

R29 cannot answer that because no paired final comparison establishes positive payoff gain.

A future experiment should predefine a population of non-adversarial difficult proposals, count strictly certified prevented losses, and compare their welfare value to verification expense.

---

## 7. Presentation and literature comments

### R29-P1 — The abstract should lead with the adverse baseline comparison

The fact that exact DP is faster than the entire certified proposal architecture is not a footnote. It is essential context for interpreting the finite-state contribution.

If the paper remains in its current form, the abstract should say explicitly that the exact tabular baseline dominates total work on all tested finite graphs.

### R29-P2 — “Neural proposal” and “certified policy” should never be visually merged

Every table should make clear whether a row refers to:

- raw neural proposal;
- repaired compiled table;
- independently evaluated optimal policy;
- mathematical network output;
- or hardware implementation.

R29 is much better on this point, but the title still collapses these distinctions.

### R29-P3 — Expand the closest-method literature, not the broad surrounding literature

The current bibliography includes useful general references on numerical economics, fitted value iteration, direct search, neural control, and verified numerics.

The missing comparison is the one closest to the actual new operator: policy improvement, rollout/lookahead, approximate policy iteration, residual-based policy bounds, and certified/verified dynamic programming.

The paper should explain why residual-budget candidate retention is not simply a specialized variant of these constructions.

### R29-P4 — The historical annex is useful for auditability but should not determine paper architecture

A 181-page preservation artifact is appropriate for repository provenance.

It should not force the main paper to carry every historical mechanism or negative path as a coequal contribution.

---

## 8. What would make a materially stronger next revision

I do not think another round of cosmetic edits or a few extra seeds would be enough. A publishable next version needs a different center of gravity.

### N1 — Choose the central numerical problem

Either the paper is about:

- certified approximate dynamic programming;
- certified continuous stochastic control;
- policy-preserving repair;
- or deployment-safe optimization.

At present it is about all four.

### N2 — Demonstrate a regime in which certification is cheaper than solving

This is the most important requirement.

For the finite-state method, show a problem where the proposal plus certificate materially reduces total work relative to the strongest exact/classical method, or develop a certificate that avoids a complete state-action scan.

If no such regime exists, the contribution is an audit/repair procedure, not a scalable solution method.

### N3 — If action preservation is the contribution, formalize its value

Define an edit/intervention objective and prove something nontrivial about the operator relative to it.

A strong direction would be a constrained problem:

minimize weighted policy intervention cost  
subject to a uniform performance-loss bound.

Then ask whether the residual-budget rule is optimal, approximately optimal, or computationally attractive.

### N4 — Add strong classical rollout/policy-improvement baselines

Use exactly the same model information and report total work.

The current two-period truncation is not enough.

### N5 — Make the neural claim earn its place

At large dimensions use multiple seeds and at least one architecture/optimizer control.

More importantly, identify a metric in which neural proposals consistently outperform polynomial, rollout, sparse-grid, or other classical candidates after total certification cost is charged.

### N6 — Add at least one genuinely different economic model family

The present finite-state evidence comes from one inventory construction.

A methodological paper needs evidence that the conclusion is not an artifact of one highly structured state lattice and demand process.

### N7 — Either close a meaningful fraction of the original whole-domain gap or demote that objective

A 7.1818 certificate against a 0.01 target remains a major unresolved result.

The scalar slice is not a substitute.

### N8 — Instantiate the high-dimensional stopped-gradient bridge if the original economy remains central

The paper currently gives the algebraic error decomposition but not the constants needed along the 47-dimensional financed path.

That is still a major missing bridge.

### N9 — Relegate transport equivalence and rollback restoration unless they change solver performance

They are valuable engineering/audit checks.

They are not, in their present form, independent Econometrica-level methodological contributions.

### N10 — Rework the novelty section around nearest neighbors

Do not ask the reader to infer novelty from an extensive audit trail.

State one or two new mathematical/computational ideas and compare them directly to the closest classical construction.

### N11 — Report optimized exact DP as well as audited exact DP

The baseline should not be weaker than production-quality classical code when runtime is part of the argument.

### N12 — Preserve the R29 reproducibility discipline

The exact-head validation, frozen artifacts, no-overwrite rule, exact arithmetic, raw-failure retention, and explicit negative-result reporting are worth keeping.

They are among the strongest aspects of the revision.

---

## 9. Recommendation

**Reject in the present form.**

This recommendation is materially different from the R27 recommendation.

R27 was not yet a reviewable paper. R29 is a real paper and a real computational object. The authors have closed many reproducibility and attribution gaps, and I regard the finite-state exact-arithmetic implementation as substantially more credible than the earlier versions.

The remaining objection is therefore more fundamental.

The core certified Bellman construction succeeds because it performs exhaustive exact-model Bellman comparisons and exact greedy repair over the full finite graph. That makes the universal post-repair pass rate unsurprising. The relevant question is whether the learned proposal makes certification or solution meaningfully easier.

On the paper’s own evidence, the answer is currently no:

- exact DP is faster at every reported scale;
- completion plus verification alone is already slower than exact DP;
- neural fitting adds substantial cost;
- no raw proposal passes the 0.01 target once the state count reaches 256;
- the largest neural raw regret is 1.549;
- high-dimensional scaling uses one neural seed;
- polynomial controls are competitive and sometimes better;
- the original continuous-time whole-domain target remains missed by approximately 718 times;
- the one-dimensional slice does not establish the 47-dimensional bridge;
- the rollback experiment proves no positive gated-versus-ungated payoff difference;
- and the transport experiment verifies an exact re-expression of the same parameter-space optimizer rather than producing a new solver.

The strongest genuinely new finite-state idea may be the residual-budget action-retention rule. But action retention is not yet attached to an economic objective, is not globally minimum-edit, and does not reduce the current full-graph scan cost.

That is not enough for Econometrica-level numerical methodology.

A substantially stronger paper could emerge from this material if it is rebuilt around one of two claims:

1. a **computationally advantageous certificate** that can exploit a good learned proposal without essentially resolving every Bellman comparison that exact DP resolves; or
2. a **formally valuable policy-preservation problem** in which minimizing intervention relative to an incumbent policy is itself economically important and the residual-budget operator has a demonstrable approximation/optimality property.

Without one of those advances, the current paper is best understood as an unusually careful study of how to audit and repair learned Bellman proposals on small-to-medium exact models, plus several rigorous diagnostics for a much harder continuous-control program. That is useful work, but it is not yet the numerical-method contribution claimed by the title and venue target.

---

## 10. Source map inspected

### Exact review target

- revision/econometrica-r29-referee-copy-2026-09-24
- SHA 788246778893695471015ce4db76e6a61a2c9ca0

### Main R29 documents

- ECTA_R29.tex / pdf
- SUPP_R29.tex / pdf
- RESPONSE_R29.tex / pdf
- COMPUTATION_R29.tex / pdf
- HISTORY_R29.tex / pdf
- R29_REVIEW.md
- REVISION_INDEX.md

### R29 scientific source

- revisions/2026-09-24-r29/paper/economy.tex
- revisions/2026-09-24-r29/paper/operators.tex
- revisions/2026-09-24-r29/paper/budgets.tex
- revisions/2026-09-24-r29/paper/positioning.tex
- revisions/2026-09-24-r29/paper/computation.tex
- revisions/2026-09-24-r29/paper/controls.tex
- revisions/2026-09-24-r29/paper/proofs.tex
- revisions/2026-09-24-r29/paper/references.tex

### R29 replication and provenance

- revisions/2026-09-24-r29/PROTOCOL.md
- revisions/2026-09-24-r29/PROTOCOL_AMENDMENT_01.md
- revisions/2026-09-24-r29/REVISION_MANIFEST.json
- revisions/2026-09-24-r29/disposition.json
- revisions/2026-09-24-r29/replication/controls.py
- revisions/2026-09-24-r29/replication/test_revision.py
- revisions/2026-09-24-r29/replication/finalize_paper.py
- revisions/2026-09-24-r29/replication/check_publication.py
- revisions/2026-09-24-r29/results/R29_HEADLINE_RESULTS.json
- revisions/2026-09-24-r29/results/SCIENCE_SOURCE_COMMIT.txt
- revisions/2026-09-24-r29/results/SCIENCE_VALIDATION.json
- revisions/2026-09-24-r29/DOCUMENT_BUILD.json
- revisions/2026-09-24-r29/results/controls/

### Generated tables checked directly

- r29_groups.tex
- r29_scale.tex
- r29_attribution.tex
- r29_sensitivity.tex
- r29_topology.tex
- production_pair_rows.tex
- production_rows.tex
- slice_poll_rows.tex
- slice_rows.tex
- mechanism_rows.tex
- mechanism_distribution_rows.tex

### Inherited implementation checked

- revisions/2026-09-24-r28/replication/inventory.py

### Prior review context

- reviews/2026-09-24-econometrica-r27/referee_report.md
- reviews/2026-09-23-econometrica-r26/
- reviews/2026-09-23-econometrica-r25-second-pass/

### Exact-head validation

- workflow: .github/workflows/r29-validate.yml
- GitHub Actions run: 35932676059
- head SHA: 788246778893695471015ce4db76e6a61a2c9ca0
- conclusion: success

