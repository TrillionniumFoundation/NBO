# External Referee Report — R39

**Venue perspective:** Econometrica-level numerical and computational methods  
**Article:** *Certified Bellman Operators for Costly Policy Revision*  
**Repository:** `TrillionniumFoundation/NBO`  
**Reviewed branch:** `revision/econometrica-r39-common-continuation-2026-09-25`  
**Reviewed HEAD:** `bf5d42b08debd4c26341ab1b1231a6a6242df4f9`  
**Previous report addressed:** `reviews/2026-09-25-econometrica-r38/referee_report.md`, review commit `acbede22e517a245fcc5244de7171c1ae218ea73`  
**Review branch:** `review/econometrica-r39-numerical-methods-2026-09-25-bf5d42b`  
**Date:** 2026-09-25

## 1. Recommendation

**Reject in the present form.**

R39 is not merely another cosmetic revision. It introduces a genuinely new finite-state common-continuation formulation for randomized Markov policies, a backward repair argument, a complete probability-box search with a finite stopping theorem, a stronger verified McCormick comparator, an explicit continuous-state transfer theorem under certified reset approximations, prospectively frozen holdout environments, connected support bounds, and independent arithmetic checks for substantial parts of the new computation. This is the first revision in this sequence that contains a plausible theorem-level response to the central objection that earlier certificates converged only to intermediate relaxations rather than to the named constrained objective.

The revision nevertheless remains unsuitable for Econometrica. There are two distinct reasons.

First, the reviewed HEAD is not a complete publication object. The article source calls a generated metrics file that is absent; the generated table-row files referenced by the manuscript are absent; there is no root `ECTA_R39.tex`, no compiled `ECTA_R39.pdf`, no R39 publication manifest, and no completed R39 build object. The branch contains substantial scientific source and result objects, but the current manuscript cannot be reconstructed from the committed tree as presented. This repeats, in a less severe form, the publication-boundary problem that earlier revisions claimed to have solved.

Second, even if those packaging defects are repaired, the scientific evidence does not yet support the breadth of the main claim. The complete finite-state algorithm is mathematically meaningful, but its worst-case tree is exponential, its repair modulus becomes severe when discounting is close to one and the operating allowance is small, and the prospective holdout results show the practical consequence: all horizon-8 and horizon-12 holdouts remain materially unresolved under the frozen budgets. The end-to-end continuous-state transfer theorem requires a total-variation reset approximation that the paper explicitly acknowledges does not cover either headline atomic-transition model. The original continuous-state development cohort therefore still has direct one-sided certificates and feasible lotteries rather than a convergent spatial approximation to the common randomized Markov optimum. The two-state nonlinear experiment now has positive lower endpoints, but its certified relative gaps are approximately 94%–99.6% and worsen as the mesh is refined; at the tighter tolerance, no feasible upper policy is certified. These are not informative global optimality results.

The authors deserve credit for stating many of these limitations candidly. Candor does not eliminate them. A correct exponential finite-state method plus very weak continuous-model intervals is not yet an Econometrica-level numerical method for the economic class advertised by the paper.

## 2. Overall assessment

| Dimension | Assessment |
|---|---|
| Finite-state common-Markov formulation | Substantive and potentially correct |
| Repair and finite stopping theorems | Meaningful, but constants and complexity are prohibitive in the relevant regime |
| Independent arithmetic verification | Strong for checked finite-state and one-dimensional objects; selective elsewhere |
| Continuous-state end-to-end theorem | Valid only under a restrictive reset/TV assumption not satisfied by the headline atomic models |
| Development-cohort randomized evidence | Establishes some strict randomized improvements, but not tight common-Markov optima broadly |
| Nonlinear two-state evidence | Positive lower bounds, but economically vacuous relative gaps |
| Prospective holdout evidence | Honest and useful; also reveals severe horizon/state scaling failure |
| Publication completeness of reviewed HEAD | Fails |
| Economic external validity | Weak |
| Suitability for Econometrica | Insufficient |

## 3. What R39 genuinely improves

The recommendation should not obscure the real progress.

### 3.1 The policy class is finally aligned with the stated randomized objective

Earlier exact frontier calculations permitted history-specific continuation choices and therefore did not solve the common randomized Markov problem. R39 instead parameterizes a single action lottery for each date and state and evaluates operating value and revision cost under that common continuation. This is the correct object when the policy is a randomized Markov rule rather than a history-conditioned tree.

### 3.2 The backward repair idea addresses feasibility restoration rather than only lower bounding

The repair theorem mixes an approximately feasible randomized rule with an operating-maximizing rule and bounds the required mixture and the associated cost increase. This supplies a route from probability-grid or box approximations to genuinely feasible upper policies. It is conceptually more important than adding another one-sided support price.

### 3.3 The finite search has a real completeness theorem

The probability-lattice argument and the policy-box branch-and-bound theorem provide a finite stopping result for finite-state, finite-action, strictly discounted problems with positive allowance. The theorem does not infer convergence from successful examples. It explicitly acknowledges an exponential tree-depth bound and explains why finite-time experiments may stop with large gaps.

### 3.4 The verified McCormick comparator targets the same object

Unlike several earlier “comparators,” the McCormick branch-and-bound targets the same common randomized Markov problem under the same initial law and all-restart operating restrictions. The comparison is therefore scientifically meaningful even when neither solver closes the case.

### 3.5 The holdout protocol is genuinely prospective within the repository history

The eight seeds, dimensions, horizons, discount factors, tolerances, solver hashes, node cap, time cap, and stopping tolerance were committed before the result-producing R39 HEAD. This is much stronger evidence than repeatedly tuning on the 42-case development cohort. The authors also retain failures rather than reporting only closed instances.

### 3.6 Verification boundaries are described more honestly than in most computational papers

The finite-state checker uses exact SymPy arithmetic and does not import the search implementation or optimizer. It checks policy-box splits, contractions, LP residuals, common-continuation equations, leaf bounds, and global minima. The continuous-state verifier independently checks lotteries and whole-cell inequalities using the pre-existing independent primitive parser. The nonlinear checker reconstructs two complete representative objects with a different scalar/symbolic implementation. These are genuine strengths.

The blocking findings below concern the relationship between these achievements and the paper's headline numerical and economic claims.

## 4. Blocking scientific and publication findings

### R39-F1 — The reviewed R39 HEAD is not a complete, compilable submission

The manuscript source begins with

```tex
\input{revisions/2026-09-25-r39/paper/preamble}
\input{revisions/2026-09-25-r39/paper/generated/metrics}
```

but the reviewed tree contains no `revisions/2026-09-25-r39/paper/generated/metrics.tex` and no `paper/generated` directory. The article also invokes generated row files such as

```tex
\tablerows{revisions/2026-09-25-r39/paper/generated/finite_rows.tex}
```

which are likewise absent. The root contains no `ECTA_R39.tex`, no `ECTA_R39.pdf`, no corresponding supplement/response/computation PDFs, no `SCIENTIFIC_MANIFEST.json`, and no `PUBLICATION_MANIFEST.json` for R39. There is no committed completed-build record showing that the actual review object compiles with resolved references and tables.

This is not a minor typesetting complaint. Several central numerical tables are represented only by macro calls whose rendered rows are absent. A referee cannot confirm that the paper read by an editor is the paper generated from the checked result ledgers. R38 made publication integrity part of its scientific contribution; R39 regresses on that standard.

**Required correction:** materialize the complete R39 publication object on the revision branch: generated metrics and table rows, root TeX entry points, compiled PDFs, build logs, hashes, scientific and publication manifests, and a clean-build command that succeeds from the reviewed commit. The final paper must be generated from the exact result objects checked by the independent verifiers.

### R39-F2 — The end-to-end continuous-state theorem does not apply to either headline model

The continuous-state transfer theorem assumes a certified reset approximation: within each cell, the original transition kernel must be uniformly close in total variation to a cell-reset kernel, and the initial law must admit the corresponding exact cell-mixture representation. This is a useful theorem for transition densities with controlled source regularity and destination-density approximation.

The paper correctly admits that the primary affine-shock model and the nonlinear two-state model have atomic transition laws and do not satisfy this approximation merely by refining a spatial mesh. For state-dependent Dirac successors, replacing the successor atom by a fixed within-cell reference distribution generally leaves total-variation distance bounded away from zero. Consequently, the theorem that allegedly supplies an “end-to-end error budget for the actual economic objective” does not furnish such a budget for either empirical centerpiece of the paper.

This creates a serious mismatch in the architecture. The complete finite-state theorem solves finite-state models. The continuous transfer theorem covers a class with sufficiently regular transition densities. The experiments emphasized in the abstract and numerical section are atomic continuous-state models outside that transfer class. Their intervals remain direct model-specific certificates with no spatial convergence theorem to the common randomized Markov optimum.

**Required correction:** either develop an end-to-end transfer theorem applicable to the actual atomic transition models—most plausibly using a metric compatible with Lipschitz value functions, exact image partitions, or another structure-preserving approximation—or make a regular-density model satisfying the reset assumptions the principal numerical application. The current theorem cannot be used as the general convergence justification for the headline experiments.

### R39-F3 — Finite termination is not practical convergence in the relevant economic regime

The finite-state stopping theorem is mathematically valuable, but the constants expose a severe practical weakness. The repair fraction depends on the discount margin and the operating allowance. When `beta` is close to one and `epsilon` is small, the denominator involving `(1-beta) * epsilon` is tiny. In the primary calibration, `beta=0.95` and `epsilon=0.01`, so the baseline margin is only `0.0005`. To make repair inexpensive, the approximate feasibility error must therefore be extremely small, forcing fine probability lattices and deep policy-box refinement.

The paper proves an exponential node bound in the number of policy coordinates. That number is proportional to states times horizon, before accounting for actions. This is not merely a pessimistic theorem. The frozen holdouts show the same pattern: short horizons can close, while all horizon-8 and horizon-12 cases remain unfinished under the common caps. Four-state cases are particularly difficult.

A numerical-methods contribution needs more than eventual termination of an exponentially large exact search. It needs exploitable structure, useful rates, or convincing evidence that realistic problems can be solved before the theorem's worst case becomes relevant.

**Required correction:** provide complexity results and empirical scaling in states, actions, horizon, discounting, and tolerance; quantify the repair constant for every experiment; and introduce structural acceleration that changes the observed scaling rather than only strengthening a node lower bound. The abstract and conclusion should not equate finite completeness with practical solvability.

### R39-F4 — The prospective holdout study is honest, but its outcome is unfavorable

The prospectively frozen suite contains eight problems. Under the fixed tolerance and budgets, the interval Bellman method closes only three of eight, while the verified McCormick method closes four of eight. One of the closed cases has zero upper cost and is therefore a trivial exact-zero problem once feasibility is certified. All four horizon-8 and horizon-12 environments remain unresolved. The stronger McCormick lower bound often helps materially, but it does not remove the long-horizon failure.

This is important negative evidence. It shows that the central exact-search method does not generalize from short development cases to modest finite problems with two or four states and horizons 8 or 12 under a 60-second/4,096-node protocol. The paper discusses these failures, but the conclusion still presents the method as if the main remaining issue were merely engineering acceleration. At Econometrica standards, the holdout evidence currently supports “complete but quickly intractable,” not “a broadly useful global method.”

**Required correction:** expand the holdout suite and report closure probability, certified relative gaps, node counts, memory, and time by dimension and horizon. More importantly, develop a solver that materially improves the frozen long-horizon cases without changing the target policy class, information structure, or tolerance. The existing holdout should remain untouched as a permanent test set.

### R39-F5 — The development cohort still does not deliver tight common-randomized optima broadly

R39 computes whole-domain feasible lotteries and improved support-based lower bounds on the original one-dimensional cohort. This can certify a strict randomized improvement over every deterministic feasible rule when the randomized upper cost lies below the deterministic lower bound. That is a valid and interesting comparative statement.

It is not the same as solving the common randomized Markov optimum. Many rows retain nontrivial lower–upper intervals. The paper's finite-state completeness theorem cannot close those continuous atomic-model intervals because the reset transfer theorem does not apply. The reported certificates therefore establish selected strict inequalities and zero-cost exact cases, not a general solution of the 42 randomized primary objectives.

The distinction matters because the paper's own contribution is motivated by the inadequacy of deterministic results. Once randomization is admitted, the economic object is the common randomized optimum, not merely the existence of a randomized policy cheaper than the deterministic lower bound.

**Required correction:** report every randomized row with absolute and relative gap, not only counts of strict improvement and improved lower bounds. Identify exactly how many common-randomized objectives are solved to a predeclared tolerance. Supply a refinement theorem applicable to the actual atomic model or refrain from describing the primary computation as resolving the randomized optimization problem.

### R39-F6 — The inherited deterministic record remains short-horizon and partly trivial

The deterministic baseline is unchanged: 24 integrated equalities, of which 12 have zero revision cost and are immediate optima once the incumbent is shown feasible. Of the 12 positive-cost equalities, ten occur at horizon 4, two at horizon 8, and none at horizon 12. Eighteen deterministic cases retain positive intervals, and R39 does not close a new residual deterministic case or make any of those intervals arbitrarily tight.

The revised manuscript is more candid about this than R38, but the evidence still matters. The main development cohort repeatedly shows that the certificate machinery is strongest when the horizon is shortest and the outer selector happens to remain feasible. R39's finite-state holdouts reproduce the same horizon dependence.

**Required correction:** de-emphasize the count “24 exact cases” and organize the evidence around nonzero-cost, longer-horizon problems. Report relative gaps and failure mechanisms. A zero-cost feasibility certificate should not receive the same headline weight as a nontrivial constrained optimum.

### R39-F7 — The nonlinear positive lower bounds are numerically almost vacuous

R39 improves the nonlinear two-state table from a zero lower endpoint to a positive support lower endpoint. The improvement is formally real but quantitatively weak.

For the inherited tolerance `epsilon=0.5`, the certified relative gaps are approximately:

- `T=8`: about 93.9%, 96.0%, 98.0%, and 98.8% as `N` increases from 32 to 256;
- `T=16`: about 97.9%, 98.5%, 99.2%, and 99.6% over the same meshes.

The lower endpoint roughly halves when the mesh doubles, while the upper endpoint remains orders of magnitude larger. Thus mesh refinement makes the relative certificate worse and suggests that the positive lower endpoint may be dominated by box/discretization conservatism rather than converging to an economically informative positive optimum.

At the tighter tolerance `epsilon=0.05`, the paper computes positive lower-bound diagnostics, but no candidate receives a feasible upper certificate. Those rows are therefore not optimization intervals at all.

A statement such as “nonzero nonlinear lower bounds replace feasibility-only intervals” is literally true but scientifically misleading unless the magnitude and refinement behavior are given equal prominence. A lower bound of 0.03 against an upper cost above 7 does not demonstrate near-optimal control.

**Required correction:** derive a consistency theorem for the nonlinear lower construction, explain the observed decay under mesh refinement, and produce intervals with economically informative relative width. At the tighter tolerance, provide a feasible upper policy or present the calculation only as a lower-bound diagnostic. Do not use positivity alone as evidence of successful global optimization.

### R39-F8 — The nonlinear experiment lacks an end-to-end convergence argument

The whole-box evaluator verifies operating inequalities for fixed candidates and the support construction supplies valid one-sided cost bounds on each finite enclosure. The paper does not show that the combined lower and upper endpoints converge to the same optimum as `N` increases. Indeed, the observed lower endpoint moves toward zero while candidate upper costs remain large.

The independent nonlinear checker covers two representative objects, which is useful, but it validates finite arithmetic rather than the limiting interpretation of the sequence. Since the total-variation reset theorem is inapplicable, no general theorem bridges the grid sequence to a common randomized optimum for the continuous atomic model.

**Required correction:** state and prove a model-specific spatial consistency theorem for the atomic bilinear transitions, including threshold-crossing revision costs, policy approximation, and all-restart operating constraints. Then demonstrate monotone or otherwise controlled convergence of both endpoints. Without this, the nonlinear section is a collection of valid finite enclosures, not a solved continuous optimization problem.

### R39-F9 — The repair theorem's economic scope is narrower than the presentation suggests

The repair construction requires positive operating allowance and strict discounting. Its useful modulus also relies on an available operating-maximizing rule and bounded cost/value diameters. It says little in the limiting cases `epsilon=0` or `beta=1`, and can be numerically severe near those cases. These restrictions are economically relevant: long-lived organizations and hard safety/operating constraints are precisely settings where `beta` is near one and tolerance is very small.

Moreover, mixing with an operating-maximizing policy can radically alter implementation exposure and may amount to replacing the candidate almost entirely when the approximate violation is not tiny. A mathematically feasible repaired upper policy need not be an informative approximation to the original candidate or a practically implementable revision mechanism.

**Required correction:** state the domain restrictions in the abstract and theorem summaries; report repair weights for every upper certificate; quantify how much cost and policy behavior are created by repair rather than by the candidate search; and analyze whether a local or state-dependent repair can avoid near-total replacement.

### R39-F10 — Verification establishes arithmetic validity, not applicability or approximation quality

The independent finite verifier is a major strength. It establishes that the saved branch tree, exact witnesses, contractions, and leaf bounds support the declared finite-state interval. It does not establish that the finite model approximates a continuous economic model, that the repair constants are useful, or that the holdout suite is representative.

Likewise, the continuous verifier checks direct whole-domain inequalities for the declared lotteries and support functions. It does not convert those one-sided certificates into a convergent common-randomized solution. The nonlinear verifier checks two complete objects, not all eight support rows or the tighter-tolerance diagnostics.

The manuscript often explains these boundaries correctly, but aggregate phrases such as “independently verified computation” risk lending the strongest label to the entire empirical package.

**Required correction:** add a result-by-result verification matrix identifying mathematical target, finite arithmetic checker, shared assumptions, spatial approximation theorem, and publication artifact. Independently check all headline nonlinear rows or explicitly limit the headline to the two independently reconstructed objects.

### R39-F11 — The direct global-programming comparator often being stronger is a warning, not a secondary observation

The verified McCormick method frequently provides a substantially stronger lower endpoint per explored policy box. On one four-state short-horizon holdout it closes the problem while interval Bellman search does not. On longer cases it still leaves gaps, but the comparison indicates that the paper's Bellman interval machinery is not evidently the best numerical route even within the finite-state target class.

A top numerical-methods paper must explain what the proposed operator structure adds beyond a generic verified global program. Possible advantages might include decomposition, warm starts across tolerances, statewise sparsity, parallelism, or reusable Bellman envelopes. These advantages are not yet demonstrated strongly enough to offset the weaker bounds.

**Required correction:** provide controlled scaling comparisons under matched implementation quality and hardware, including node quality, wall time, memory, and certificate width. Identify a regime in which the Bellman method is demonstrably preferable, not merely also complete.

### R39-F12 — The economic evidence remains synthetic and uncalibrated

The maintenance primitives, revision weights, tolerances, installed rules, holdout generators, and nonlinear model are designed examples. Neural incumbents remain frozen computational policies rather than economically estimated rules. There is no parameter estimation, uncertainty set, empirical calibration, monetary welfare interpretation, or institutional model of whether randomized action assignment is permissible and costly.

The new conclusion—that realized-action lotteries can be cheaper than every deterministic feasible policy—is mathematically meaningful. Its economic importance depends on omitted primitives: randomization overhead, legal or organizational constraints, commitment and observability, implementation variance, and aversion to heterogeneous treatment. The paper acknowledges these omissions but supplies no application in which the certified difference changes an economic conclusion.

A pure methods paper can clear this bar with broad convergence and scalability. R39 has a restrictive transfer theorem and exponential finite search. It therefore also needs a compelling economic application, which is absent.

**Required correction:** either apply the method to a serious economic model with disciplined primitives and uncertainty, or substantially broaden the theory and practical scaling. Additional synthetic variants of the same maintenance template will not resolve the journal-fit problem.

### R39-F13 — The stopped-control material remains disconnected and unsolved

The retained consumption–portfolio diffusion still misses its original `0.01` target by orders of magnitude; the inherited bound is approximately `7.1818`. The killed-operator observation supports Bellman comparison but does not provide continuous-action coverage, diffusion discretization error, boundary settlement control, or an end-to-end policy certificate.

The R39 reset theorem is formulated for a different regularity structure and is not instantiated on the stopped diffusion. The stopped-control section therefore remains historical context, not evidence for the method's applicability.

**Required correction:** either solve a nontrivial stopped-control instance with complete action and spatial error coverage or move this material entirely to an archival appendix. It should not contribute to the perceived breadth of the current result.

### R39-F14 — The paper still combines too many differently scoped objects

The manuscript now contains:

- deterministic outer-action certificates on a continuous atomic model;
- direct continuous whole-domain randomized lotteries and support lower bounds;
- exact common-randomized finite-state branch-and-bound;
- a reset approximation theorem for regular transition densities;
- history-conditioned fixed-restart frontiers;
- local restart LP relaxations;
- a nonlinear box enclosure without convergence;
- synthetic sensitivities;
- an unsolved stopped diffusion.

These objects have different policy classes, state models, initial laws, approximation mechanisms, and verification strengths. R39 improves the conceptual bridge, but the main complete theorem and the main numerical models still do not meet under one set of assumptions. The result is an omnibus paper whose strongest theorem is illustrated on modest finite holdouts and whose most elaborate continuous examples remain outside the theorem.

**Required correction:** choose a central theorem–application pair. The strongest route would be to make a model satisfying the transfer assumptions the principal application and demonstrate tight end-to-end intervals. Alternatively, center the paper on finite-state common randomized control and remove claims about continuous economic models that are not covered by the theorem.

### R39-F15 — The literature and novelty case remain underdeveloped

The revised bibliography is larger than R38's, but the manuscript still needs a much sharper comparison with constrained MDP occupation-measure methods, semi-infinite programming, randomized stationary/Markov policy results, verified global optimization, reachability and safe-control synthesis, policy-space branch-and-bound, robust MDP discretization, and switching/adjustment-cost economics.

The novel contribution appears to be the combination of common-continuation probability-box search, feasibility repair, and machine-checkable Bellman/LP bounds. The paper must establish precisely which theorem is unavailable from existing constrained-control and verified-optimization frameworks and why the operator representation is computationally advantageous.

**Required correction:** add theorem-level comparisons and same-object numerical baselines from the relevant literatures. Repository engineering and exact arithmetic are valuable, but they do not by themselves establish Econometrica-level novelty.

## 5. Minimum requirements for a viable future submission

A future submission would need a coherent redesign rather than another incremental layer of certificates.

1. **Materialize a complete publication object.** All generated sources, entry points, PDFs, logs, and manifests must be committed and reproducible from the reviewed HEAD.

2. **Unify theorem and application.** Demonstrate tight end-to-end bounds on a substantive continuous-state model that actually satisfies the approximation theorem, or prove a transfer theorem for the atomic models used in the experiments.

3. **Make randomized primary intervals genuinely informative.** Report and tighten the common-Markov optimum intervals for all primary cases, with predeclared absolute and relative stopping criteria.

4. **Resolve the nonlinear consistency problem.** Explain why lower bounds decay with mesh refinement and prove convergence of both endpoints for the atomic bilinear model.

5. **Improve practical scaling.** Close nontrivial horizon-8 and horizon-12 holdouts under the frozen target without changing policy class or tolerance. Report complexity and repair constants transparently.

6. **Demonstrate an advantage over verified global programming.** Identify and validate a regime in which the Bellman/operator approach is materially stronger in gap, memory, or scaling.

7. **Extend independent verification to every headline result.** In particular, independently reconstruct all nonlinear headline rows and verify the generated publication tables against the checked ledgers.

8. **Establish economic relevance.** Incorporate randomization overhead, institutional feasibility, and parameter uncertainty in a serious application, or provide a substantially broader methods theorem that makes calibration unnecessary.

9. **Preserve the holdout suite.** Do not retune on the eight frozen cases. Introduce a separate development suite for algorithm changes and a new immutable evaluation suite for the finalized method.

## 6. Additional technical and presentation comments

1. The abstract must say explicitly that the end-to-end reset theorem does not apply to the two atomic-transition experiments.

2. Report the repair fraction, operating slack before and after repair, and repair-induced cost increment for every upper policy.

3. Separate exact-zero cases from positive-cost closures in every summary count.

4. Report relative gaps alongside absolute gaps in all tables, including deterministic inherited results.

5. For the randomized development cohort, state the number of cases closed to a fixed tolerance, not only the number with strict improvement over deterministic policies.

6. Give the full table of lower, upper, relative gap, support-price contribution, and lottery-repair contribution in the article or supplement generated from committed source.

7. Explain why the probability denominator `7` was chosen for the finite primary study and show sensitivity to this choice.

8. Provide the theoretical and observed relationship between policy-grid denominator, repair error, branch depth, and final cost gap.

9. The finite stopping theorem should state clearly whether action probabilities lie in full simplices or a reduced coordinate representation and how simplex boundaries are handled.

10. Prove measurability and existence statements for the general Borel formulation rather than relying on finite-action intuition where common randomized continuation is involved.

11. Distinguish an infimum from an attained optimum whenever compactness or lower semicontinuity has not been supplied.

12. Explain whether the operating-maximizing repair policy is unique and how ties affect reproducibility and the cost bound.

13. Show the exact constants `D_J` and `D_C` for every holdout and primary case; normalized statements conceal poor conditioning.

14. Report node counts and leaf counts together with stop reasons. “Budget” and “time cap” are scientific outcomes, not implementation footnotes.

15. Clarify cases in which a zero upper cost causes exactness despite the search stopping with a budget label.

16. For the McCormick solver, document all bilinear terms, variable bounds, envelope validity, and how leaf primal feasibility is converted to an exact rational upper policy.

17. Include wall-clock hardware information and process-level memory for both finite solvers under identical environments.

18. The holdout table should identify which closures are positive-cost and which are trivial zero-cost cases.

19. The nonlinear table should not headline “8/8 positive lower bounds” without displaying the 94%–99.6% relative gaps in the same visual field.

20. Plot nonlinear lower and upper endpoints against mesh width. The present trend is more informative than the positivity count.

21. At `epsilon=0.05`, label rows “lower bound only” rather than displaying them near optimization intervals.

22. Explain whether the nonlinear support lower bound is expected to be monotone under mesh refinement. If not, state what convergence diagnostic is meaningful.

23. The independent nonlinear checker should cover a fine mesh and a tight-tolerance case, not only two representative coarse objects.

24. Add a machine-generated map from every table cell in the paper to its proof object and verifier record.

25. The generated macros and row files must be committed; a paper whose central tables disappear from the reviewed tree is not a valid reproducible object.

26. State which results use exact rational arithmetic, outward integer arithmetic, floating-point proposals followed by exact checking, or shared-code validation.

27. The manuscript should not use “global” without immediately naming the state model, policy class, initial law, and whether the bound is one-sided or an end-to-end interval.

28. The economic discussion of randomization should address implementation overhead and observability before claiming organizational relevance.

29. The literature review should explain the relationship between the finite common-policy program and occupation-measure formulations. If the all-restart constraint prevents a standard linear formulation, show precisely where and why.

30. The conclusion should lead with the unfavorable scaling evidence, not treat it as a final engineering challenge after broad claims of convergence.

## 7. Final editorial view

R39 is the strongest revision in the repository sequence. The common-continuation correction, repair theorem, complete finite policy search, matched verified global-programming comparator, prospective holdout protocol, and independent branch-tree verification are substantive contributions. The authors have also become notably precise about what is and is not solved.

The same precision makes the remaining problem impossible to ignore. The theorem that gives end-to-end continuous-state convergence excludes the atomic models used as the paper's main numerical evidence. The finite exact algorithm is exponential and fails on every longer-horizon holdout under modest frozen budgets. The nonlinear “improvement” leaves relative gaps near 100% and has no feasible upper policy at the tighter tolerance. The inherited deterministic closures remain concentrated at short horizons and include many trivial zero-cost cases. Finally, the reviewed HEAD is missing the generated manuscript components and completed publication artifacts required to reproduce the actual article.

This is a serious research program and a strong computational archive. It is not yet an Econometrica paper.

**Recommendation: Reject.**