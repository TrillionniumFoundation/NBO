# External Referee Report — R34

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article:** *Certified Bellman Operators with Neural Proposals: All-Restart Bounds for Costly Policy Revision*  
**Repository:** TrillionniumFoundation/NBO  
**Reviewed branch:** revision/econometrica-r34-verified-policy-frontier-2026-09-24  
**Reviewed HEAD:** d0cfe1b17cc66cde393f4e2d1700270975bb7e30  
**Review branch:** review/econometrica-r34-numerical-methods-2026-09-24-d0cfe1b  
**Date:** 2026-09-24

## 1. Recommendation

**Reject in the present form.**

R34 is a serious scientific revision and should not be described as a cosmetic response to R30. It materially fixes several of the earlier report's strongest structural objections. The new maintenance economy has action-dependent transitions, so continuation values no longer cancel from action comparisons. The upper witness is now constructed from model primitives rather than supplied as a free certificate input. The policy-revision recursion is evaluated under the deployed policy's own transition law. The manuscript also develops a class-free lower bound on intervention cost and then propagates the all-restart restriction backward to tighten that lower bound. The exact-rational proof objects, complete cost accounting, retained failed cases, and explicit caveats about neural superiority and high-dimensional scalability are all improvements.

Those improvements make the remaining issue sharper. R34 still does not demonstrate an Econometrica-level numerical method that solves, or makes materially more tractable, a difficult constrained economic dynamic program. In the positive-cost cases the paper produces a feasible policy and a lower bound, not a solved constrained optimum. Out of 42 global cases, 12 have zero cost and zero gap because the installed spline incumbent is already certified feasible; the other 30 retain a positive global cost gap. The new restart propagation tightens 22 of the 42 intervals but closes none of the previously positive gaps. The manuscript therefore does not know how close its positive-cost deployments are to the true optimum of the problem that motivates the paper.

The benchmark remains extremely structured: one continuous state, three actions, two affine shock branches, affine rewards, piecewise-affine exact algebra, and horizons only up to 12. The exact operating dynamic program takes milliseconds to a tenth of a second. The new global portfolio and restart certificates are much more expensive, and the paper does not implement a strong information-matched classical method for the **same minimum-revision problem**. The exact operating DP is not such a comparator, while the local certified class is intentionally conservative and therefore cannot serve as the benchmark against which global numerical efficiency is judged.

The theory has also not crossed the gap from a finite Lagrangian relaxation to a sharp numerical method. Both the global support bound and the restart propagation use a fixed, coarse, finite multiplier portfolio. There is no convergence theorem, no adaptive multiplier algorithm with a certified stopping rule, no strong-duality result for the stated all-restart problem, and no direct solution of the constrained optimum on the very benchmark where the state dimension is only one. In a paper whose central output is a primal--dual interval, this is a fundamental omission.

I therefore regard R34 as a technically careful verified-computation framework with better scientific discipline than earlier versions, but not yet as a numerical-method contribution at the requested level.

## 2. What R34 genuinely resolves from the R30 report

The revision deserves explicit credit for resolving or substantially reducing several earlier objections.

### 2.1 R30-F1: supplied witnesses

This objection is **substantially addressed**. The new construction starts from primitives, forms action-dependent expectations, maximizes them, compresses the resulting convex piecewise-affine envelope, and checks the compression error. The paper no longer asks the reader to accept a globally useful upper witness as an exogenous input. It also constructs a lower witness from checked compression defects.

This is an important change. The witness-construction cost is charged, and the manuscript is clear that the construction is not automatically cheaper than every alternative.

### 2.2 R30-F2: action-independent transitions and cancellation

This objection is **addressed for the maintenance application**. The displayed transition maps depend on the action, and maintain/replace can be optimal only through continuation values because they have lower current reward. The new application is therefore a genuine Bellman-coupled model, unlike the R30 sign-rule experiment.

### 2.3 R30-F4: policy-dependent occupancy

This objection is **addressed at the level of mechanism**. Intervention cost is evaluated under the deployed policy, and the dynamic repair rule can differ from the pointwise rule because today's action changes future revision exposure.

However, the empirical force of this fix is limited. Only the deliberately constructed occupancy-stress incumbent shows positive dynamic-versus-pointwise savings. The other 36 declared comparisons have exactly zero saving. I return to this below.

### 2.4 R30-F5: trillion-state rhetoric

The most problematic state-cardinality rhetoric has been removed or heavily qualified. The current paper explicitly says that one-dimensional continuum certification does not establish a high-dimensional rate. This is a welcome correction.

### 2.5 R30-F9: incomplete scalar boundary diagnostic

The stopped-control material is stronger. The paper now claims a positive derivative over the entire constant-adjustment interval and a unique optimum within that scalar class rather than relying on five point evaluations. That is a meaningful completion of the earlier scalar diagnostic.

It still does not solve the original current-state stopped-control problem.

### 2.6 R30-F10: arbitrary external intervention price

The current revision separates the computational multiplier portfolio from an external economic revision price and no longer treats a universal sign at one arbitrary price as a headline success statistic. This is also an improvement.

The unresolved issues are therefore not a repetition of the R30 report. The most serious old structural criticisms have been met. The present negative recommendation concerns what remains after those corrections.

## 3. Technical credibility of the new theorem chain

I found no immediate algebraic error that would by itself invalidate the central R34 inequalities.

The constructive upper-witness result is plausible under the stated convex piecewise-affine structure. Upward slope rounding preserves convexity, the chord interpolation is an upper approximation for a convex function, and the checked compression defect can be propagated backward.

The certified action class follows from standard Bellman comparison. The local deficit budget gives a sufficient all-restart operating guarantee. The intervention-cost recursion within that class is standard constrained backward induction once the admissible action sets are known.

The class-free global lower bound is also a valid weak-duality construction. For a fixed nonnegative multiplier, the unrestricted support Bellman problem maximizes operating value minus implementation cost. Combining that value with a lower operating witness gives a pointwise lower bound on the implementation cost of any feasible policy.

The new restart propagation is logically reasonable for the all-restart Markov problem. If future continuations are themselves feasible from every reached restart, a future cost lower bound can be propagated through the transition kernel. The current operating constraint supplies a necessary inequality, and a nonnegative multiplier yields a valid local Lagrangian lower bound. The paper is also correct not to screen actions individually for randomized policies, because such screening could exclude feasible mixtures.

These observations matter: my recommendation is not based on finding a simple false theorem.

The problem is that these ingredients are mostly classical comparison, weak duality, and constrained dynamic programming assembled in a careful exact-arithmetic pipeline. For an Econometrica-level numerical-method paper, correctness of the relaxation is necessary but not sufficient. The paper must also establish that the relaxation produces a new numerical capability, a sharp enough solution method, or a theoretical advance over established constrained-MDP and verified-DP machinery. R34 does not yet do so.

## 4. Blocking scientific findings

### R34-F1 — There is still no strong comparator that solves the same constrained revision problem

The paper compares several different objects, but not the one comparison that matters most.

The exact DP solves the operating-value maximization problem. It does **not** solve the minimum intervention-cost problem subject to the uniform all-restart operating constraint.

The local class solver minimizes intervention cost only inside a sufficient inner class. The paper itself emphasizes that this class can be conservative, and R34's global portfolio is introduced precisely because policies outside the class can be better.

The support portfolio then supplies feasible candidates and a lower bound, but not the exact constrained optimum.

Thus the main numerical claim is evaluated without a strong information-matched classical solver for the same objective. This is especially difficult to justify because the benchmark is only one-dimensional, finite horizon, three actions, and piecewise affine. If the global constrained optimum cannot be computed or tightly approximated in this setting by a direct classical method, the paper must explain why. If it can be computed, that result should be the primary benchmark.

A suitable comparison could use a direct constrained Markov-control formulation, an occupation-measure or parametric linear-programming approach after exact partitioning, an augmented-state dynamic program carrying a certified operating budget, or another exact/verified method appropriate to this finite-horizon piecewise-affine model. I am not prescribing one particular algorithm. I am saying that the paper currently compares its global bound to a deliberately conservative class rather than to a solution method for the same global optimization problem.

**Required correction:** implement a strong same-object comparator and report total time, memory, accuracy, and the true or independently certified optimal intervention cost on the R34 benchmark.

### R34-F2 — The positive-cost global problem remains unsolved

The paper reports 42 global cases. Twelve spline cases have exact zero intervention cost and zero global gap. Those are legitimate global optima, but their optimality follows from the simplest possible lower bound: intervention cost is nonnegative and the incumbent itself satisfies the operating tolerance.

The scientifically difficult cases are the remaining 30 positive-cost configurations. None is solved globally.

The restart propagation tightens 22 of the 42 lower bounds and leaves 20 unchanged. It closes **zero** previously positive gaps.

The magnitude of the residual uncertainty is not small relative to the economic improvements being highlighted. In the installed-neural table, before the restart tightening, the reported global excess-cost upper bounds are:

- approximately 0.0394--0.0427 for T=4, epsilon=.01;
- 0.0695--0.0873 for T=4, epsilon=.05;
- 0.3019--0.6649 for T=8, epsilon=.01;
- 0.2825--0.4323 for T=8, epsilon=.05;
- 0.7710--1.2740 for T=12, epsilon=.01;
- 0.6333--1.9959 for T=12, epsilon=.05.

The corresponding savings relative to the conservative local class can be much smaller. A policy can therefore be substantially better than the local class and still be very far, for all the reader knows, from the true constrained optimum.

The largest restart improvement is useful, but it does not change this qualitative fact. The paper has developed a stronger lower bound, not a solved positive-cost policy-revision method.

**Required correction:** either close the positive-cost gaps on the benchmark, or supply a convergence/sharpness theory and numerical evidence showing that the remaining gaps can be driven to a prescribed tolerance at controlled cost.

### R34-F3 — The fixed multiplier grids are ad hoc numerical parameters with no convergence theory

The global support portfolio uses the fixed set

[
\{0,1,4,16,64,256,1024,4096\}.
]

The restart propagation reuses the same finite multiplier set.

The fact that this portfolio was fixed before the final run is good protocol practice, but it does not make the grid a principled numerical method. There is no theorem stating how dense the multiplier set must be to achieve a target primal--dual gap. There is no adaptive rule. There is no certified stopping condition. There is no analysis of sensitivity to the grid. There is no separation of error due to the finite multiplier set from error due to the witness approximation and error due to the recursively propagated continuation lower bound.

This is particularly conspicuous in the restart step. At each state the local problem has finitely many actions and a single linear necessary operating inequality for randomized action weights. The associated one-step relaxation is a very small linear program. Its exact dual structure should be exploitable. Restricting the dual variable to eight manually chosen values is a computational convenience, not a satisfactory final method.

Likewise, for the global support bound, the paper should explain whether a continuous or adaptively refined multiplier search can be implemented with the same exact piecewise-affine machinery and what improvement it produces.

**Required correction:** replace the fixed-grid relaxation with an exact or adaptively certified dual procedure, or prove a quantitative convergence result that connects multiplier discretization to the global cost gap.

### R34-F4 — The benchmark is coupled but still numerically easy and unusually favorable to exact algebra

R34 fixes the analytic cancellation defect of R30, but it does so in a model that remains extremely special:

- state dimension: 1;
- actions: 3;
- shock branches: 2;
- affine transition maps;
- affine current rewards;
- piecewise-affine value functions;
- exact rational breakpoints and coefficients;
- horizons only 4, 8, and 12.

This is a good unit test for a certificate constructor. It is not yet a convincing demonstration of a method intended for difficult economic dynamic programs.

The paper's own timing results underline this point. The exact operating DP takes roughly:

- 0.0033 seconds at T=4;
- 0.0103 seconds at T=8;
- 0.0883 seconds at T=12.

The median global portfolio construction takes roughly:

- 0.415 seconds at T=4;
- 1.378 seconds at T=8;
- 8.993 seconds at T=12.

The restart propagation adds median costs up to approximately 14.872 seconds for T=12, epsilon=.01, before the separately timed final audit.

These are not apples-to-apples objective comparisons, because the exact DP does not solve the revision problem. That is precisely why R34-F1 is important. But they establish that the underlying Bellman model itself is not computationally difficult. The new machinery is being tested on a problem where exact operating optimization is nearly trivial.

The representation also grows materially: the base stored objects reach 361 pieces and 251-bit rational components, while the restart closure reaches 471 stored pieces, 632 local-function pieces, and up to 716-bit rational components. The 42 compressed restart objects occupy about 18.7 MiB. None of this is alarming in one dimension, but it gives no evidence that exact overlays remain practical in a genuinely multivariate model.

**Required correction:** add at least one substantially harder coupled model, preferably with multiple continuous states or nonlinear transitions/value representations, and report how certificate construction, rational bit growth, memory, and primal--dual gaps scale.

### R34-F5 — The endogenous-occupancy mechanism is demonstrated only by a deliberately engineered stress incumbent

The occupancy mechanism is theoretically real, but the numerical evidence is weak.

The paper's occupancy table reports positive dynamic-versus-pointwise savings only for the predeclared "occupancy stress" incumbent. The other 36 comparisons have zero saving.

Even in the stress cases, the absolute differences are modest:

- 0.002276 at T=4, epsilon=.01;
- 0.011382 at T=4, epsilon=.05;
- 0.017469 at T=8, epsilon=.01;
- 0.089158 at T=8, epsilon=.05;
- 0.023743 at T=12, epsilon=.01;
- 0.119917 at T=12, epsilon=.05.

For the last case, the dynamic cost is about 13.7581 versus 13.8780 for the pointwise rule, a difference below one percent of the reported cost level.

A mechanism example is useful. It does not establish that policy-dependent occupancy materially changes revision decisions in economically natural configurations. Because the stress incumbent is intentionally misconfigured, the result should be interpreted as a constructive counterexample to the pointwise rule, not as broad evidence that the proposed dynamic revision recursion is economically important.

**Required correction:** show robustness across economically motivated installed policies, transition parameters, revision weights, and initial distributions. Report how often the occupancy effect changes the deployed rule and whether the change has material welfare or implementation consequences.

### R34-F6 — Neural proposals remain incidental and the title still overstates their role

R34 is commendably explicit that it does not establish neural-specific superiority. That admission is scientifically correct. It also undermines the current title.

All 18 installed-neural configurations fail their raw operating target. The neural rules become useful only after exact structural certification/repair or after selecting a different feasible support policy. The two spline families yield twelve zero-cost global optima because their installed policies are already feasible.

The earlier timing table is also unfavorable to the neural route. Median cold neural totals are approximately 2.21--3.58 seconds across the displayed horizons, while exact operating DP is approximately 0.003--0.088 seconds. Again, those outputs are not identical, but nothing in the evidence identifies a numerical task for which the neural proposal is the enabling ingredient.

The manuscript now says that neural and classical approximations are merely possible installed proposals. If that is the intended contribution, "with Neural Proposals" should not remain a defining part of the title. If neural approximation is intended to be scientifically central, the paper must show a problem in which it materially improves certificate construction, total cost, or feasible-set discovery relative to strong non-neural proposal classes.

**Required correction:** either remove the neural emphasis from the title and abstract, or provide a quantitative neural-specific advantage on a nontrivial model.

### R34-F7 — The paper still does not establish a new numerical frontier relative to classical constrained Markov control

The manuscript now appropriately cites constrained Markov control and describes weak duality as classical. That is good.

But once those disclaimers are made, the remaining theoretical delta becomes narrow:

1. construct a special piecewise-affine upper witness;
2. form a conservative action class;
3. solve a standard cost DP inside that class;
4. solve a finite set of scalarized unrestricted Bellman problems;
5. combine their values into a weak-duality lower bound;
6. propagate a local Lagrangian lower bound backward under an all-restart condition;
7. serialize the result into exact proof objects.

This is a useful engineering composition. The paper has not yet shown that it gives a capability unavailable to classical verified dynamic programming, constrained MDP duality, parametric linear programming, or other established numerical approaches once the same piecewise-affine structure is exploited.

The restart theorem in particular is a Bellmanized Lagrangian relaxation. Its current theoretical statement proves validity and monotonicity when the multiplier set is enlarged, but not exactness, convergence, or a rate. Valid lower bounds are not by themselves sufficient novelty for the target venue.

**Required correction:** sharpen the theorem-level novelty against the closest constrained-DP and verified-computation alternatives. A convincing new result would characterize exactness, convergence, certified gap reduction, or complexity under conditions substantially broader than the present one-dimensional affine construction.

### R34-F8 — The paper lacks an economically interpretable revision-cost calibration

The intervention cost is

[
(1+x)\mathbf 1\{\pi(x)\ne\pi^0(x)\},
]

discounted under the deployed policy. The paper is transparent that one unit is a normalized implementation intervention rather than a dollar estimate.

For a numerical economics paper, transparency is not enough. The economic conclusions currently depend on a stylized cost weight, a uniform initial state distribution, and a bespoke maintenance model. There is little evidence about how the recommended revision changes under alternative economically plausible cost schedules or state distributions.

This matters because the headline output is not merely an operating certificate; it is an economic tradeoff between preserving an installed rule and changing it. Without calibration or serious sensitivity analysis, the substantive economic content remains thin.

**Required correction:** provide sensitivity to the initial distribution, revision-cost function, discount factor, maintenance costs, and transition persistence. Preferably connect at least one specification to an institutional or empirical interpretation.

### R34-F9 — The source of the remaining primal--dual gaps is not diagnosed, despite the benchmark being easy enough to permit that diagnosis

The paper computes an exact operating DP for diagnostics, but does not use that information to decompose its global cost gaps.

This is a missed opportunity. The lower-bound looseness can arise from several different sources:

- the lower witness L being below the true value V;
- the finite global multiplier portfolio;
- the restriction to the finite set of feasible support candidates used for the upper bound;
- the restart recursion using only a necessary operating inequality and a lower continuation-cost function;
- the finite local multiplier portfolio.

Because V is cheap to compute on the benchmark, the authors can replace L by exact V **for diagnostic purposes only** and measure how much of the gap is due to witness error. They can then refine or optimize the multiplier set to quantify dual discretization error. They can also compare the selected feasible candidate with a direct constrained optimum if R34-F1 is addressed.

At present the reader sees a remaining gap but cannot tell which part of the algorithm is responsible for it.

**Required correction:** add a systematic gap decomposition and show which algorithmic component must improve to close the positive-cost cases.

### R34-F10 — The "independent audit" is optimizer-free but not an independent implementation

The audit discipline is strong by ordinary computational-paper standards, but the terminology should be tightened.

The checker runs in a separate path and does not invoke the optimizing envelope routine. It also includes useful mutation tests. However, the audit imports the same `coupled` module and therefore shares the same `PW` representation, affine composition, `q_functions`, `linear_comb`, `select`, model primitives, and exact-rational arithmetic kernel. The restart checker similarly imports `global_cost`.

This architecture is sufficient to detect many construction and serialization errors, especially wrong selectors and incorrect claimed extrema. It is not sufficient to eliminate common-mode bugs in the piecewise-affine representation, composition logic, or transition evaluation.

For a paper that places unusual weight on independent proof-object verification, this distinction is important.

**Required correction:** call the present checker "optimizer-free" or "read-only" rather than fully independent, or add a genuinely independent verifier implemented with a separate arithmetic/partition kernel or separate language/library.

### R34-F11 — The original stopped consumption--portfolio target remains unresolved and continues to fragment the paper

R34 improves the scalar boundary section, but the original all-domain current-state target remains explicitly unsolved. The manuscript says so.

That honesty is welcome. The editorial problem remains. The maintenance model now supplies the main constructive theorem chain. The stopped-control section is a second research program with different primitives, different numerical machinery, and a different objective. The scalar global optimum in the constant-adjustment slice does not instantiate the maintenance-model certificate, and the maintenance certificate does not solve the stopped economy.

The paper is more coherent than R30, but the same structural tension remains: one application is the tractable proof-of-method model, while the economically more ambitious original problem remains outside the solved scope.

**Required correction:** either connect the certificate method to a nontrivial part of the original stopped-control problem, or remove/demote that material and submit a focused maintenance/certification paper.

### R34-F12 — The current results support "verified bounds for a structured revision problem," not yet "a numerical method that expands the set of solvable economic dynamic programs"

This is the overarching issue.

R34 now has:

- a coupled Bellman model;
- constructive witnesses;
- exact finite certificates;
- a class-optimal revision policy;
- feasible policies outside that class;
- global lower bounds;
- all-restart lower-bound propagation;
- reproducible rational audits.

What it does **not** have is one of the following decisive outcomes:

- a difficult problem that was infeasible for a strong classical method but becomes feasible here;
- a major reduction in total solve time or memory for the same verified target;
- a globally solved positive-cost revision problem;
- a convergence theorem making the primal--dual interval a bona fide numerical solution procedure;
- a neural proposal that materially changes the computational frontier;
- a high-dimensional scaling result;
- a substantive economic conclusion that depends on the new method.

Without one of these, the contribution remains an elaborate, carefully audited bounding framework around a small exact model.

## 5. Quantitative interpretation of the R34 evidence

Several numerical facts should be emphasized more strongly in the paper because they cut against an overly favorable interpretation.

First, the exact operating model is very small computationally. The displayed exact-DP times are approximately 0.0033, 0.0103, and 0.0883 seconds for horizons 4, 8, and 12.

Second, the global portfolio is much more expensive: median per-configuration times are approximately 0.415, 1.378, and 8.993 seconds. At horizon 12 the added restart propagation has median costs of approximately 14.872 seconds for epsilon=.01 and 7.909 seconds for epsilon=.05.

Third, the stronger certification is not merely a small postprocessing step. The final restart closure reaches 471 stored pieces, 632 local-function pieces, and 716-bit rational components. Across 42 cases the compressed closure objects occupy about 18.7 MiB.

Fourth, the globally positive-cost results remain intervals, not point solutions. The twelve zero-gap spline cases are useful controls, but they are qualitatively easier because the incumbent is already feasible and zero cost is an immediate universal lower bound.

Fifth, the strongest evidence for endogenous occupancy is confined to the deliberately stressed incumbent. The mechanism is demonstrated, but its empirical relevance to the broader proposal cohort is not.

Sixth, the neural evidence is negative as a proposal-quality result: none of the 18 installed neural configurations meets the raw target. The paper is correct to stop claiming neural superiority. The title should catch up with that conclusion.

## 6. Additional technical comments

### R34-T1 — Formalize the policy class for history-dependent and randomized claims

For Markov policies, the all-restart condition is clear. For a history-dependent policy, a value from state x at date t is not fully defined without specifying the prior history or a continuation kernel. The manuscript verbally adds a conditional-feasibility requirement. This should be stated with a formal filtered policy class if the theorem is intended to cover history dependence.

### R34-T2 — Report exact constrained-reference values whenever available

The benchmark is small enough that the paper should try very hard to compute the true constrained optimum, at least for T=4 and perhaps T=8. Even a partial exact reference would reveal whether the dual bounds are close or fundamentally loose.

### R34-T3 — Optimize the local restart multiplier rather than sampling eight values

With three actions and one local inequality, there is no obvious reason to accept an eight-point multiplier grid as the final method. Derive the exact statewise dual or provide a certified adaptive search.

### R34-T4 — Add multiplier-grid sensitivity for the global support bound

Show the global lower bound and selected feasible policy as the multiplier set is enlarged. The present geometric grid may accidentally be adequate or inadequate; the reader cannot tell.

### R34-T5 — Separate warm and cold computational claims consistently

The paper is careful about inherited neural fitting in the R34 global study, while earlier timing tables include cold neural import/training. Maintain a single accounting taxonomy across all headline comparisons so that no reader confuses incremental certification cost with full deployment cost.

### R34-T6 — Stress the witness construction beyond the favorable convex piecewise-affine case

The constructive theorem is tied to convexity and piecewise-affine exactness. Provide either a broader approximation theorem with validated interpolation error or a second model where these exact closure properties are unavailable.

### R34-T7 — Report growth with horizon beyond 12

The piece counts and rational bit lengths are already growing. A horizon scaling experiment would help distinguish benign polynomial growth from an impending exact-overlay explosion.

### R34-T8 — Clarify whether the feasible support policy set is itself a numerical heuristic

The upper deployment is selected from a finite portfolio of support policies plus the local-class minimum. This is not a search over the full feasible set. State this as an explicit heuristic upper-bound generator, and report how upper costs change when the portfolio is enriched.

### R34-T9 — Strengthen the independent verifier

Mutation tests are useful. Add a second implementation of at least the final inequalities and integrals using a different representation or library. Common-mode representation errors are otherwise not excluded.

### R34-T10 — Reduce historical and auxiliary material in the main paper

The repository-level historical archive is excellent. The article itself should be shorter and more focused. A reader should not need to track the old inventory evidence, a maintenance certificate, global support bounds, restart propagation, and a separate stopped-control scalar theorem to understand the main contribution.

## 7. Minimum bar for a materially stronger submission

I would not recommend another revision that merely adds more multiplier points or another round of exact auditing to the current benchmark. A materially stronger submission should satisfy most of the following conditions.

1. **Solve or tightly certify the same global constrained revision problem with a strong classical comparator.** On the present one-dimensional model, report a true or independently certified reference optimum if at all feasible.

2. **Turn the primal--dual interval into a convergent numerical method.** Provide an exact/adaptive multiplier procedure, a gap-convergence theorem, or a certified stopping rule.

3. **Close positive-cost cases.** The method should do more than prove zero cost when the incumbent is already feasible. Demonstrate global or near-global optimality in genuinely positive intervention-cost configurations.

4. **Use a harder coupled economic model.** At minimum, move beyond the exact one-dimensional affine closure case. A multivariate or nonlinear example is needed to support a broader numerical-method claim.

5. **Demonstrate robust policy-dependent occupancy effects.** The difference between pointwise and dynamic revision should appear in economically natural configurations, not only one deliberately stressed incumbent.

6. **Resolve the role of neural proposals.** Either show a measurable computational/certification advantage or remove neural language from the paper's identity.

7. **Provide economically interpretable sensitivity.** Vary the revision-cost schedule, initial distribution, transition parameters, and other primitives; preferably calibrate at least one version.

8. **Use a genuinely independent verifier for the final proof objects.** The current read-only checker is valuable but shares the core arithmetic representation.

9. **Focus the paper.** Either connect the stopped consumption--portfolio program to the certificate method or move it out of the central narrative.

10. **State the theorem-level novelty against constrained-MDP duality and verified dynamic programming with precision.** The paper should identify a result that is more than a careful implementation of weak duality plus exact piecewise-affine backward induction.

## 8. Recommendation to the editor

**Reject in the present form.**

This recommendation is not based on poor reproducibility, hidden failures, or an obvious false theorem. R34 is unusually transparent about its limitations and has clearly improved in response to the previous review.

The problem is contribution level. The paper now verifies that a sophisticated certificate pipeline can be executed on a small, highly structured coupled model. It does not yet show that the pipeline solves the positive-cost global revision problem, outperforms or enables something beyond a strong classical method for the same objective, scales beyond one-dimensional exact piecewise-affine algebra, or generates a substantive economic conclusion that depends on the new numerical machinery.

The next scientifically meaningful step is therefore not another presentation revision. It is a stronger numerical result: a same-object benchmark, a closed or controllably convergent primal--dual gap, and a genuinely difficult coupled application.

## 9. Source map inspected

### Current R34 submission object

- ECTA_R34.tex / ECTA_R34.pdf
- SUPP_R34.tex / SUPP_R34.pdf
- RESPONSE_R34.tex / RESPONSE_R34.pdf
- COMPUTATION_R34.tex / COMPUTATION_R34.pdf
- R34_REVIEW.md
- revisions/2026-09-24-r34/PROTOCOL.md
- revisions/2026-09-24-r34/IMPLEMENTATION_NOTES.md
- revisions/2026-09-24-r34/PUBLICATION_MANIFEST.json

### Main theorem and exposition sources

- revisions/2026-09-24-r34/paper/main.tex
- revisions/2026-09-24-r34/paper/global_theory.tex
- revisions/2026-09-24-r34/paper/restart_theory.tex
- revisions/2026-09-24-r34/paper/global_results.tex
- revisions/2026-09-24-r34/paper/restart_results.tex
- revisions/2026-09-24-r34/paper/supplement.tex
- revisions/2026-09-24-r34/paper/response.tex

### Generated numerical evidence

- revisions/2026-09-24-r34/paper/generated/occupancy.tex
- revisions/2026-09-24-r34/paper/generated/timing.tex
- revisions/2026-09-24-r34/paper/generated/global_work.tex
- revisions/2026-09-24-r34/paper/generated/global_neural.tex
- revisions/2026-09-24-r34/paper/generated/restart_summary.tex
- revisions/2026-09-24-r34/results/summary.json
- revisions/2026-09-24-r34/results/restart_summary.json
- revisions/2026-09-24-r34/results/wall_clock.json
- revisions/2026-09-24-r34/results/restart_wall_clock.json
- revisions/2026-09-24-r34/results/independent_audit.json
- revisions/2026-09-24-r34/results/restart_independent_audit.json

### Implementation inspected

- revisions/2026-09-24-r34/replication/coupled.py
- revisions/2026-09-24-r34/replication/global_cost.py
- revisions/2026-09-24-r34/replication/restart_closure.py
- revisions/2026-09-24-r34/replication/audit.py

### Prior referee baseline

- reviews/2026-09-24-econometrica-r30/referee_report.md
- R30 manuscript head 3394815f4ccbf5917582c8f756b535adf87783cc

This report reviews the exact R34 head identified above and does not modify any revision branch.
