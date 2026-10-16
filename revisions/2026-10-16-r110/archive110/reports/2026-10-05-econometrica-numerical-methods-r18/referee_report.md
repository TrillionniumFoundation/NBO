# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r18-2026-10-05`  
**Reviewed branch head:** `20afc6c1c4828e3c469e7906366bcc8730cc04d0`  
**Reviewed branch tree:** `2c9527794af967b3108942816f574b89ec346a2f`  
**R18 publication commit:** `f28e83434d9f9ef486b38ac1ab52b511a7b978f4`  
**Pinned root manuscript blob:** `7079c00c344f410de0730bd1e8dcfed169650687` (`ECTA.tex`)  
**Pinned root supplement blob:** `a8c90baf5f80c403b501d3f2a07c4550aa72e3d0` (`supp.tex`)  
**Pinned applications blob:** `e2938c5bf6f7616f34a11646ceb1801e2d9c42e1` (`revisions/2026-10-05-r18/applications.tex`)  
**Report date:** 5 October 2026  
**Recommendation:** **Reject in the present form, while encouraging a new, substantially shorter submission centered on amortized continuation learning and prospectively measured work-to-accuracy. R18 finally establishes a limited positive role for a learned continuation, but the present cumulative manuscript still does not establish a sufficiently broad or economically consequential Econometrica-level numerical-method contribution.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R18 is a material scientific advance over R15. The central objection in my preceding report can no longer be stated in its former absolute form. The revision now contains credible positive evidence that fitting and reusing a common scalar continuation can be useful in a specified repeated-decision economy.

Three additions are particularly important.

First, the completed continuation-menu experiment compares five full procedures—NBO, a vector costate predictor, a materialized Raw actor, direct policy optimization, and cached sample-average optimization—over four finite capital calibrations, dimensions ten and fifty, sixteen complete algorithm streams, three work stages, and 384 fixed queries per cell. In the previously unpiloted fifty-dimensional Long and Intermediate designs, the final NBO procedure has protected payoff advantages exceeding the prespecified \(10^{-4}\) margin over both the materialized Raw actor and direct policy. It also uses less measured construction-and-query time than direct policy in those cells. These are genuine positive results.

Second, R18 adds an independently frozen assessment of continuation-contrast prediction risk. At the same NBO/reference action pairs, the comparison uses common future paths so that the common squared-noise term cancels. Of twenty-four simultaneous comparisons, eight establish lower risk for NBO, four favor cached Raw, and twelve remain unresolved. This is a sound and useful diagnostic. The report correctly does not identify risk ordering with policy-payoff ordering.

Third, the revision applies exact difference-constraint closure to every simultaneous menu interval. The resulting shortest-path calculation gives sharp regret bounds relative to the finite sixteen-candidate budget catalogue. In the fifty-dimensional Intermediate design, final-stage NBO is the least-cost **certified** candidate within \(10^{-4}\) of the best catalogue payoff, with regret upper bound approximately \(9.1391\times10^{-5}\) and mean recorded construction-and-query cost approximately 12.6993 seconds. The mathematical closure argument is correct under the stated common-event assumptions.

The scientific record is also unusually transparent. The risk source was frozen before audit observations; every favorable, unfavorable, and unresolved risk comparison is retained; the catalogue analysis is explicitly labeled post-freeze; cheaper unresolved candidates are not deleted; old HJB and Raw results remain visible; and the current publication is source-bound and compiled. I found no immediate contradiction in the risk-cancellation identity, the finite-sample risk certificate, or the exact catalogue-closure proposition.

These advances substantially strengthen the paper. They do not, however, resolve the main publication question.

The strongest new evidence concerns an intentionally constructed **finite repeated-decision menu** in which current rewards or constraints change while the future reference policy and its continuation remain fixed. This is precisely the environment in which continuation amortization should be valuable. The experiment shows that NBO can be useful there. It does not yet show that NBO is a broadly useful numerical method for the continuous-time control, recursive-utility, temporal-equilibrium, and dynamic-game problems that continue to define the title and scope.

Moreover, the favorable accuracy–work conclusion is narrow. NBO is the least-cost certified candidate in one of eight cells. Other cells select low-budget SAA, Raw, a vector predictor, or final SAA. The cheaper vector and materialized-Raw procedures have lower final construction-and-query clocks than NBO in every cell. At the largest Raw prediction budget, the continuation-risk assessment produces no cell in which NBO is certified to have lower risk; one cell favors Raw and the rest are unresolved. The catalogue selection is a valid retrospective use of simultaneous intervals, but it is not a measured prospective stopping procedure, and cheaper uncertified alternatives remain in the decisive Intermediate cell.

Thus R18 establishes a credible local proposition:

> In some finite, high-dimensional repeated-decision environments, a learned common continuation can improve protected payoffs relative to selected fitted alternatives and can be the least-cost procedure among the candidates whose finite-catalogue accuracy has been certified.

That proposition is interesting. It is not yet the broad numerical-method claim suggested by the cumulative paper, nor is it coupled to a substantive economic conclusion of Econometrica scale. I therefore recommend rejection of the present manuscript, but I would take a focused new submission on this local proposition seriously.

## 2. What R18 successfully repairs

The recommendation should not obscure the considerable progress.

### 2.1 The learned continuation now has direct positive economic evidence

R15 supplied a strong verifier and a positive comparison against one HJB implementation, but it did not isolate a benefit of the learned critic relative to simpler candidate generators. The menu experiment changes that assessment.

In the final-stage menu comparison, NBO has material protected advantages over the Raw actor and direct policy in the fifty-dimensional Long and Intermediate cells. The result averages every declared stream and query and retains the complete finite population rather than selecting successful fits. No fit failed and no fallback was used. The paper also preserves the reversals: direct policy and SAA outperform NBO in the ten-dimensional Long design, and SAA outperforms NBO in both Long cells.

This is the first revision for which I regard the sentence “a learned common continuation can add economic value in a declared computation” as supported by direct evidence.

### 2.2 The continuation-risk assessment is well designed

The statistic
\[
 (p_N-p_R)(p_N+p_R-2Z)
\]
is the correct algebraic difference of two squared prediction errors evaluated against the same random continuation contrast. The common \(Z^2\) term cancels exactly. Conditional on the frozen predictions, action pairs, and realized Raw caches, the statistic is unbiased for the difference in conditional contrast risks.

The assessment is separated from training, uses fresh audit innovations, fixes its range and family before those innovations, counts an antithetic pair as one observation, and retains the complete four-calibration, two-dimension, three-budget family. The paper is also explicit that this is not unconditional risk over future Raw caches, not a comparison at Raw’s separately selected actions, and not a continuous-diffusion optimality statement.

### 2.3 The catalogue closure is mathematically correct and usefully interpretable

The graph construction translates pairwise intervals into standard difference constraints. Shortest-path potentials attain the upper and lower contrast bounds, so the resulting regret bounds are sharp relative to the interval-defined uncertainty set. The no-negative-cycle condition is the right feasibility check.

The corollary allowing selection after observing a simultaneous family is also correct: because every candidate’s bound holds on one event, choosing the least recorded cost among certified candidates does not require an additional probability allocation.

This is a useful way to convert a large comparison family into a decision rule.

### 2.4 Work accounting is much better than a training-time comparison

The final-stage clocks include the three construction stages, imports, source checks, reusable data, optimization and derivative work, saved queries, and durable output. The paper separately reports shared confirmation work and does not divide it into artificial per-method observed clocks. It also distinguishes early prefix allocations from full final-stage process clocks.

The resulting table is informative. NBO is consistently cheaper than direct policy and final-stage SAA, while the vector and materialized-Raw procedures are consistently cheaper than NBO. These facts are not hidden.

### 2.5 Inferential scope and chronology are unusually candid

R18 distinguishes:

- policy-payoff intervals from prediction-risk intervals;
- risk differences from absolute risk;
- finite-catalogue regret from scalar-action and full adapted-control regret;
- a prospective experiment from a deterministic post-freeze reanalysis;
- a least-cost certified candidate from the true minimum-work candidate;
- and the central menu-plus-risk confidence account from the union of all historical families.

This precision materially improves the credibility of the paper.

### 2.6 The submitted object is complete and source-bound

The R18 audit reports a complete publication, preservation of inherited labels and proof blocks, byte-identical replay of the risk report, all 128 catalogue records, and no new observations in the deterministic closure. The compilation record gives a 49-page main article, 187-page technical supplement, 48-page applications companion, and 17-page response, with no undefined references, multiply defined labels, duplicate destinations, missing characters, or overfull horizontal boxes.

## 3. Blocking concerns

### B1. The positive result is local to an engineered finite reuse environment

The central menu is designed so that twelve current tasks share exactly the same postdecision continuation. The future policy, transition kernels, innovation law, terminal payoff, and subsequent rewards are fixed; only the current reward or feasible set changes. This is a legitimate and useful test bed. It is also close to the ideal environment for amortizing a continuation approximation.

The finite population is explicit: four calibrations, two dimensions, sixteen complete algorithm streams, thirty-two states, and twelve tasks per state. The confidence statements are valid for that population. There is no probabilistic or economic argument extending the result to other task distributions, state populations, horizons, preference specifications, future policies, or training streams.

The inherited recursive-utility, endogenous-preference, temporal-self, and dynamic-game applications do not receive an analogous comparison showing that reuse of a fitted continuation improves economic accuracy or total work. The strongest positive evidence is therefore narrower than the paper’s title and retained economic scope.

A general numerical-method contribution requires either a theorem characterizing a nontrivial class of environments in which amortized continuation learning should outperform direct simulation, or prospective evidence across independently chosen economic applications. R18 currently supplies neither.

### B2. The new risk evidence does not identify the value of NBO at the decisions made by competing procedures

The risk comparison is conditional on the stage-three NBO action and the analytical reference action. Both NBO and Raw predict the continuation contrast at those same postdecision states. This is a fair comparison of predictors at a fixed action pair, but it is not a symmetric comparison of the procedures’ own decision problems.

A Raw or SAA procedure may choose a different action and therefore require accuracy at different states and along different margins. Conversely, NBO’s policy value depends on how its prediction errors interact with the action optimizer, not merely on squared error at its selected binary contrast. The paper correctly notes that a predictor with larger squared error may make the better decision.

The comparison also conditions on one realized Raw cache for each budget. It does not average over the randomness used to construct future Raw caches. At the largest 64-path budget, no cell establishes lower NBO risk: the ten-dimensional Long cell favors Raw, while the other seven intervals include zero. The NBO advantages are concentrated at low simulation budgets, which is consistent with ordinary variance reduction but does not establish a distinctive nonlinear critic mechanism.

To identify the contribution of the learned continuation, a new study should compare:

1. absolute prediction risk and decision loss on a common exogenous action catalogue;
2. risk under each method’s own selected-action distribution;
3. the distribution over newly generated Raw caches, not only a realized cache;
4. calibration of prediction errors to actual payoff losses; and
5. total work needed to reach a common decision-loss target.

Without these links, the risk experiment is a useful diagnostic rather than a mechanism result that carries the paper.

### B3. “Least-cost certified” is not a prospective work-to-accuracy result

The exact closure gives a valid certificate for every candidate in the already computed family. It does not establish that the historical computation could have stopped after spending the displayed selected-candidate cost.

The catalogue was developed after the menu and risk outcomes were available. This does not invalidate the simultaneous accuracy statement, but it matters for the interpretation of work. Early-stage times are prefix allocations from complete processes, not independent clocks for a prospective stopping algorithm. The study has already paid to construct all five methods at all three stages and to run the shared confirmation bank. The full comparative bill is correctly retained elsewhere.

In the decisive fifty-dimensional Intermediate cell, final NBO is the cheapest **certified** candidate. But cheaper four-path SAA and second-stage NBO remain unresolved. The analysis therefore cannot establish that NBO is the true minimum-work procedure attaining the tolerance. It establishes only that no cheaper candidate in the current family has yet been certified.

A numerical-efficiency claim should be supported by a new, frozen sequential procedure that:

- specifies the order in which candidates and budgets are tried;
- charges every failed check and all shared verification work;
- uses confidence-valid stopping;
- records actual stop times rather than prefix allocations;
- and is repeated on an independent economic design.

The present retrospective closure is an excellent planning tool for that experiment, not a substitute for it.

### B4. The paper does not report the amortization frontier that defines the claimed advantage

The economic rationale for NBO is reuse: pay once to learn a continuation and query it many times. Whether this is worthwhile must depend on the number and distribution of queries.

The reported menu fixes 384 queries in every cell. At that workload, NBO is cheaper than direct policy and 64-path SAA, but more expensive than the vector and materialized-Raw actors. The paper does not report a prospective break-even curve as the number of states, tasks, action queries, or Raw paths varies. It also does not separate fixed fitting cost, marginal query cost, cache construction cost, and verification cost in a way that lets another economist forecast the break-even point for a new problem.

This is central rather than ancillary. A method whose contribution is amortization should be evaluated along the amortization axis. The next study should report protected payoff or decision loss against complete work for, for example, 1, 4, 16, 64, 256, and 1,024 queries, with query sets fixed independently and with the complete cache and verification costs charged. The point at which NBO becomes preferable should be an estimand, not an implication of a single 384-query design.

### B5. The contribution is not sufficiently isolated against the relevant numerical literature and baselines

The paper is commendably explicit that NBO is an approximate-policy-iteration structure and not a new principle of optimality. That candor sharpens the novelty question.

Learning a postdecision value or continuation and amortizing it across decisions is a longstanding idea in approximate dynamic programming. Regression-based value approximation, fitted value or Q iteration, actor–critic methods, value-gradient approximation, response-surface simulation optimization, and postdecision-state methods all offer natural comparators. The current literature discussion is too short to explain precisely what is new relative to those traditions.

The five menu procedures are useful internal baselines, but they do not exhaust the contribution-isolating alternatives. Missing candidates include, where feasible:

- a conventional postdecision-value regression with cross-validated basis or regularization;
- a fitted value-gradient or advantage model without the NBO actor architecture;
- sparse-grid, Gaussian-process, or low-rank continuation surrogates;
- a shared conditional actor trained directly across the twelve tasks;
- a surrogate-assisted SAA method using the same stored rollouts;
- and classical approximation or interpolation in the lower-dimensional menu members.

Likewise, exact shortest-path closure of difference constraints is valuable but standard mathematical technology. Its novelty lies in the economic reporting application, not in the graph theorem itself. The paper should sharply separate standard components from its new theorem and evidence.

### B6. The economic content of the menu result is too stylized for the breadth of the submission

The twelve tasks vary current consumption weights, current adjustment terms, or temporary caps over a fixed finite state catalogue. These are transparent perturbations, but the paper does not explain which substantive economic exercise generates this menu, why its task distribution is economically relevant, or why \(10^{-4}\) is the appropriate decision threshold in those finite-economy units.

The inherited fee and consumption-equivalent discussions do not by themselves establish the material importance of the new menu comparisons. The result should be translated into an economically interpretable consequence: a policy decision, welfare transfer, equilibrium effect, or parameter conclusion that changes because the continuation is reusable.

At present, the experiment is primarily a numerical laboratory. Econometrica can publish numerical laboratories, but usually because they unlock an important economic result or establish a method with broad and convincingly demonstrated applicability. R18 has not yet crossed either threshold.

### B7. The finite-menu evidence does not validate NBO as a high-dimensional continuous-time HJB method

The paper generally states this distinction correctly. The repeated-decision menu is a finite economy with stored coefficients and a fixed future reference policy. Its catalogue regret is relative to sixteen computed procedures, not the continuous vector-action optimum or the full adapted-control class.

The positive menu results therefore do not tighten the broad continuous-time optimality bounds, demonstrate convergence of the learned value, or show that NBO accurately solves the ten- or fifty-dimensional HJB. The scalar and HJB experiments remain separate and mixed: classical scalar procedures can outperform the frozen neural policies, and most strengthened-HJB comparisons are unresolved.

The abstract and conclusion are more careful than earlier versions, but the title and cumulative theory still invite a general-solver interpretation. A focused paper should place the finite repeated-decision problem in the title and primary theorem, and move the continuous-time and broad economic applications out of the central claim unless they receive equally direct evidence.

### B8. The cumulative scope remains disproportionate to the established contribution

The current package contains a 49-page article, a 187-page technical supplement, and a 48-page applications companion. It carries differential and monotone Bellman formulations, recursive utility, endogenous preferences, temporal selves, dynamic games, continuous-time diffusion verification, HJB comparisons, observation transfer, risk assessment, and the finite catalogue.

The decisive new result can be stated much more compactly:

1. several current economic tasks share one continuation;
2. a scalar continuation may be fitted once and reused;
3. five complete procedures are compared on a finite task catalogue;
4. NBO is economically useful in some high-dimensional cells but not all;
5. conditional risk reveals a low-budget bias–variance tradeoff;
6. simultaneous intervals can be closed into finite-catalogue accuracy certificates.

That is a coherent paper. The cumulative manuscript obscures it. The inherited applications may remain valuable research, but their inclusion here raises the burden of proof without strengthening the central numerical result.

## 4. Major comments and required changes for a focused resubmission

### M1. Recenter and retitle the paper

A new submission should be centered on **amortized continuation learning for repeated economic decisions**, not on a universal Neural Bellman Operator platform. The model, estimator, decision menu, accuracy target, and work accounting should be stated before the inherited general theory.

The continuous-time verifier can appear as motivation or a separate application, but the paper should not require the reader to reconstruct a genealogy from R6 through R18.

### M2. Freeze and execute a prospective work-to-tolerance procedure

Use the R18 catalogue result to design a new algorithmic protocol. Specify before execution:

- candidate order;
- budget increments;
- confidence allocation;
- accuracy tolerance;
- stopping rule;
- treatment of failures;
- and complete timing boundaries.

Then run that protocol on fresh tasks and report actual total work to certification. The current post-freeze closure should be presented as the design analysis motivating the new experiment.

### M3. Make query volume an explicit experimental dimension

Report the amortization frontier over the number of states and tasks. Separate:

- one-time continuation fitting;
- per-query actor or optimizer work;
- Raw cache construction;
- online simulation;
- and independent certification.

This would allow readers to identify when NBO is preferable and when SAA, Raw, or a vector surrogate should be used.

### M4. Use symmetric and decision-relevant risk diagnostics

Evaluate all predictors on a common exogenous action catalogue and, separately, under each procedure’s selected actions. Report absolute risks, contrast risks, misclassification or regret for binary decisions, and the relation between those diagnostics and actual payoff losses.

Regenerate Raw caches across independent replications if the target is a method-level comparison rather than a conditional comparison with one realized cache.

### M5. Add strong continuation-surrogate baselines

The experiment needs baselines that isolate neural scalar continuation learning from generic regression and amortization. At minimum, include one conventional postdecision-value approximation and one non-neural or differently regularized surrogate using the same rollout data and query information. A shared task-conditioned actor is also important: it tests whether learning the continuation is necessary rather than merely one way to amortize across tasks.

### M6. Supply an economically substantive menu

Use a model in which the repeated decisions arise naturally—for example, many counterfactual tax, constraint, preference, or equilibrium queries that an economist would actually compute. Prespecify the task distribution from that application and translate \(10^{-4}\) into economic units.

The numerical method should change an economic conclusion, not only a leaderboard position.

### M7. Separate standard mathematics from new contribution

The fixed-dictionary bias–variance identity, common-noise squared-error cancellation, empirical Bernstein construction, and difference-constraint closure are all useful. The paper should identify which parts are standard and claim novelty only for the new economic formulation, verification link, or experimental result.

The literature review should be expanded substantially around approximate dynamic programming, postdecision-state value approximation, actor–critic and value-gradient methods, simulation optimization, fitted value iteration, and amortized or multi-task decision computation.

### M8. Clarify the hierarchy of accuracy targets

Every table should visually distinguish:

- prediction risk;
- binary or finite-catalogue decision loss;
- payoff differences;
- finite-catalogue regret;
- scalar-action regret;
- and full adapted-control regret.

The current prose does this carefully, but the number of simultaneous targets still makes the paper difficult to read. One primary economic target and one secondary mechanism target would be preferable.

### M9. Preserve the negative findings

The revised paper should continue to report that:

- Raw or vector procedures are cheaper than NBO in every final menu cell;
- SAA is materially better in both Long cells;
- NBO is the least-cost certified candidate in only one cell;
- no 64-path Raw risk comparison favors NBO;
- and cheaper unresolved candidates remain in the decisive cell.

These findings make the contribution more credible and help define the region in which continuation learning is useful.

### M10. Shorten the publication package substantially

A focused main article should contain one model family, one central theorem chain, one prospective computational design, and the complete primary results. The technical supplement should contain proofs and complete robustness records. The separate applications companion should not be part of the same submission unless those applications are essential to the identified method contribution.

## 5. A publishable redesign

A credible new submission could have the following structure.

### 5.1 Economic problem

Choose one economically substantive setting with many repeated current decisions and a shared future continuation. State the task distribution and the policy or welfare question before constructing the numerical method.

### 5.2 Methods

Compare a small number of complete procedures:

1. NBO scalar continuation;
2. a conventional postdecision-value surrogate;
3. a shared direct actor;
4. cached SAA;
5. a structure-exploiting classical method where feasible.

Give every method the same data and information rights.

### 5.3 Primary estimand

Use expected or finite-population economic regret at a fixed task distribution and the total work needed to certify regret below an economically justified tolerance.

### 5.4 Prospective design

Vary query volume and dimension. Use an actual sequential stopping procedure. Repeat the complete cache or training process over a declared method-level randomness distribution. Keep final payoff paths independent.

### 5.5 Mechanism

Measure absolute continuation risk, decision loss, and payoff under common and own-action distributions. Use the mechanism only to explain the primary economic result; do not substitute prediction risk for payoff.

### 5.6 Scope

State the result as an amortization theorem and experiment for repeated economic decisions. Broader control, recursive-utility, and game applications can be subsequent papers unless the same contribution is demonstrated there.

## 6. Independent review checks

For this report I performed the following repository-level checks.

1. **Latest revision.** I searched the remote revision branches and identified `revision/econometrica-nbo-r18-2026-10-05` as the latest numbered Econometrica revision. Its current head is `20afc6c1c4828e3c469e7906366bcc8730cc04d0`; the scientific publication commit immediately below the documentation-only head commit is `f28e83434d9f9ef486b38ac1ab52b511a7b978f4`.

2. **Source identity.** I pinned the Git blob identities of the root article, technical supplement, and applications companion listed at the beginning of this report.

3. **Publication audit.** I inspected the R18 scientific audit, publication manifest, compilation record, response map, and chronology. The audit reports a byte-identical risk replay, 128 catalogue records, preservation of inherited labels and proof blocks, and no new observations in the post-freeze catalogue closure.

4. **Risk family.** I checked the complete twenty-four-row main table. Eight intervals favor NBO, four favor Raw, and twelve are unresolved. None of the eight 64-path comparisons favors NBO; the ten-dimensional Long comparison favors Raw at that budget.

5. **Catalogue family.** I checked the eight-cell summary and the complete candidate table. Final NBO is certified within \(10^{-4}\) in six cells. It is the least-cost certified candidate in one cell, fifty-dimensional Intermediate. Other cells select SAA, Raw, or a vector predictor.

6. **Work table.** I checked the complete final-stage construction-and-query clocks. The vector and materialized-Raw procedures are cheaper than NBO in every cell; NBO is cheaper than direct policy and final-stage SAA in every cell.

7. **Theory.** I reviewed the common-continuation proposition, the fixed-dictionary projection identity, the common-noise risk-cancellation proof, the finite-sample risk certificate, and the shortest-path catalogue-closure proof. I found no immediate algebraic contradiction under their stated assumptions.

8. **Compilation record.** The source-bound record reports 49 main-article pages, 187 technical-supplement pages, 48 applications pages, and 17 response pages, with clean references and no overfull horizontal boxes.

I did **not** rerun the 640 menu fits, the 12.6 million risk-audit pair observations, or all historical continuous-time experiments. A new execution would not reproduce the original recorded clocks exactly. My assessment is based on the immutable source, stored reports, protocol records, mathematical arguments, and committed aggregate evidence.

## 7. Recommendation

R18 deserves substantial credit. It is complete, reproducible, careful about scope, and more scientifically informative than the manuscript reviewed at R15. Most importantly, it finally supplies direct positive evidence that a learned common continuation can improve economic decisions in specified repeated-decision environments. The paper has moved beyond a purely method-agnostic verification contribution.

Nevertheless, the current cumulative submission still falls short of the standard for an Econometrica numerical-method paper. The positive result is local to a finite, deliberately shared-continuation menu; the risk evidence is conditional and asymmetric; the least-cost certificate is retrospective and holds for one of eight cells; the amortization frontier is not measured; the comparator and literature set does not yet isolate the contribution against standard continuation-approximation methods; and the economic consequences are too stylized relative to the manuscript’s breadth.

I therefore recommend **rejection in the present form**. I would encourage a new, focused submission on amortized continuation learning that prospectively measures work to an economically meaningful accuracy target, varies query volume, uses strong surrogate baselines, and demonstrates a substantive economic consequence. The R18 evidence is a strong foundation for such a paper, but the present 49-page article plus 235 pages of supplements and applications is not yet that paper.
