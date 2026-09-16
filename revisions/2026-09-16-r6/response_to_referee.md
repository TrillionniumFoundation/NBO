# Response to the fifth-round referee report

**Manuscript:** *Neural Bellman Operators*, Qian QI  
**Revision:** R6, 16 September 2026  
**Review input:** `review/econometrica-r5-2026-09-16-c9f7107`, commit `0d0e79a52e540bd0647801ce316f051d667c6797`  
**Reviewed R5:** `c9f71077cf6a339573ac07be55d7660797bcf6ea`  
**Revision branch:** `revision/econometrica-r6-2026-09-16`

We thank the referee for distinguishing the validity repairs from the unresolved contribution. The revision addresses the report's four findings through new theory, stronger executed controls, and a mechanism experiment, rather than by deleting the economic model, repeating an already closed test, or treating a completed build as a scientific conclusion. The earlier manuscript, supplement, tables, source programs, and review diagnostics are preserved. All authoritative R6 numerical values are generated in `execution_summary.md`; exact arrays, timing samples, and source identities accompany them.

## R5-F1. Relation to policy caches and optimistic linear support

### What we accept

The fixed-kernel reward cache and scalar optimistic-support construction are not independent discoveries of a new transfer principle. Nemecek and Parr (2021) and Alegre, Bazzan, and da Silva (2022) are now compared explicitly. Enlarging the state to include dates does not, by itself, establish novelty. The annuity reduction is a useful economic coordinate change, not the principal incremental theorem.

### What has changed

The Introduction and the contract section give a result-by-result comparison. A new proposition proves that, between consecutive **exact** scalar anchors, all policy lines outside that pair are dominated by the appropriate endpoint policy line. Thus the full policy-value maximum and the adjacent-pair rule coincide at every state/date under the stated exact-oracle hypotheses. This equivalence is also checked numerically. It is not claimed for arbitrary approximate anchors, full action-value GPI, or the neural training implementation of SFOLS.

The new matched experiment uses the same finite Bellman oracle, state/action set, tolerance, and starting anchors for a focal initial-distribution objective and an all-state/date objective. The former needs three anchors and meets its initial-state target but has a much larger global error bound; the latter requires 47. Preparation costs, shared kernel setup, memory, and final certificates are reported. The mesh-only bank is evaluated against the unchanged neural-inclusive upper target. We do not present different guarantee scopes as a speed victory.

The substantive additional guarantee is in the new section **Policy Reuse under Changes in Transition Laws**. For an affine mixture of positive finite-horizon kernels, simple interpolation of solved endpoint values need not be an upper bound. We derive the exact cross term

`(K_a - K_b)(v_b - v_a)`

and construct a positive backward correction that makes the endpoint chord a supersolution on the entire interval. Under stated Lipschitz conditions the *additional correction*, not the total policy error, is second order in interval width. Approximate endpoints are permitted only after a valid one-sided residual correction supplies supersolutions. This is not a conversion of a sampled neural residual into a guarantee.

A second theorem evaluates each fixed feasible policy exactly as a Bernstein polynomial of the regime probability. Subdivision of the coefficient gap then supplies a uniform policy-switching welfare certificate. The proof does not assume that the optimal value is convex in the transition parameter. A two-step counterexample has endpoint values zero and midpoint value one quarter, demonstrating the obstruction that the reward-only chord does not address. Independent sequence enumeration, full small-model policy enumeration, and the original finite economy test the construction.

We credit information relaxation and transition-sensitivity literature as well as policy caches: Brown, Smith, and Sun (2010) for the general information-relaxation principle and Csáji and Monostori (2008) for value sensitivity in changing Markov environments. A separate count-informed upper recursion is reported as a valid but looser comparator, not as a new general duality result. The additional theorem is the explicit corrected endpoint construction and its connection to a feasible-policy interval certificate; we make no exhaustive priority claim over all robust-control or approximation literature.

**Locations:** Introduction; the scalar-support proposition in `04b_contract_transfer.tex`; all of `04c_kernel_transfer.tex`; Tables “Exact-Oracle Scalar Optimistic Support” and “Uniform Policy Reuse across Transition Mixtures”; Supplement S.9; `replication/r6/bank_comparison.py`, `transport.py`, `kernel_certificate.py`, and `unit_tests.py`. The detailed correspondence is also recorded in `literature_comparison.md`.

## R5-F2. Conventional structural reuse in the resource workload

### What we accept

The referee's stronger comparator changes the computational conclusion. A fitted PSD-quadratic continuation is not the exact parametric QP, and the former's approximation error cannot justify excluding the latter. The deposited R5 timing remains an actual measurement against its original reference; it is not evidence that nonlinear learned continuation is the best reusable object in that quadratic model.

### What has changed

R6 explicitly assembles `H`, `F`, and `f0` for the same nonanticipative scenario tree, reuses their structure, and preconditions by node probabilities. Every query starts at zero controls; no future shock is revealed and no query answer is cached. The same original held-out states, all 64 terminal paths, controls, horizon, and `0.001` tolerance are used. The full-tree source implementation independently checks costs, gradients, and final convex gaps. Random algebra checks precede the timed workloads.

The learned arm includes actually rerun critic-only preparation, deployment, and complete-tree evaluation. The QP arm includes structural setup and its independent complete-tree checks. Query timings use three serial single-thread runs; online and total costs are both retained. The reusable QP is the appropriate baseline for this model and is incorporated in the main table, not buried in a qualification. All earlier actor-free and quadratic-fit results remain, with their original narrow interpretation.

The resource section no longer infers a learned-representation advantage from the weaker original comparator. The paper's additional computational guarantee is established in the stopped nonlinear transition-counterfactual problem, including a valid alternative upper construction, rather than by claiming that a harder-looking label invalidates the QP result. We do not claim a universal neural speed advantage or a high-dimensional scaling result that has not been executed.

**Locations:** Revised `05_computation.tex`; the structural-QP subsection and table in `05b_incremental_evidence.tex`; Supplement S.9; `replication/r6/structural_qp.py`; all raw timing samples and per-query gaps in `output/structural_qp.json`.

## R5-F3. Necessity and attribution of learned components

### What we accept

The referee's common-mesh counterexample meets the flagship reward target. Neural action selection is not equivalent to a material value contribution, and exact Bellman repair is not evidence that the original learned policies had been accurate. The observation is not that neural actions are never chosen.

### What has changed

We execute the mesh-only lower-policy construction at the same 47 anchors, independently evaluate the resulting features, and preserve the **original full target** as upper information. The all-state/date/contract certificate remains below `0.001`. Maximum anchor loss, interval gap, construction time, and policy/feature memory are reported. We distinguish deposited and rerun policy indices: floating-point ties may change an index without a material value change. Both counts and independently evaluated value differences are retained rather than silently treating selection counts as exact scientific invariants.

The manuscript now assigns each operation its actual role: the neural network proposes controls; exhaustive finite dynamic programming repairs anchor policies; a separate recursion evaluates them; the upper oracle defines the target; and switching deploys a feasible lower policy. The new transition-law result accepts either neural or mesh policies and therefore survives the ablation as a **new guarantee**, not as a newly asserted necessity for a learned action. It extends certified counterfactual reuse to a setting where the earlier fixed-kernel reward geometry does not apply.

The original neural failures, full-menu repair, held-out resource guarantees, and broader operator framework remain in the paper. No result is relabeled a successful neural experiment merely because it appears under the NBO title. Conversely, a method that separates proposal from certification can remain useful when the best proposal in a particular model is structural rather than learned; the revision makes that separation mathematically and experimentally explicit.

**Locations:** Table “Removing Neural Actions from the Feasible Policy Bank”; same-oracle and transition-law subsections; revised Introduction and Conclusion; `bank_comparison.py`, `kernel_certificate.py`, and their deposited policy arrays.

## R5-F4. Economic content beyond a selected stopping incentive

### What we accept

Rewarding duration can change risk exposure even without deliberate preference adjustment. The original endpoint reversal and interior Hamiltonian decomposition do not identify a preference-formation mechanism when controls are at their bounds. Operating boundaries and settlement curvature describe real economic contracts, not innocuous numerical normalizations.

### What has changed

The new section **Risk Choice and the Preference-Formation Option** defines positive and nonpositive first-risk classes while optimizing every subsequent action. Within each class, value is the maximum of affine functions of contract duration reward and adjustment cost. At a regular indifference locus, the slope is

`d*'(k) = (C_positive - C_nonpositive) / (A_positive - A_nonpositive)`.

The result gives a portable economic comparative-static statement: changes in adjustment cost shift a risk boundary according to **relative adjustment effort per relative discounted duration**, rather than according to the sign of an unconstrained portfolio first-order condition. Explicit uniform duration-separation conditions imply a unique crossing; the proof also turns a two-class value error into a threshold-location bound. We do not assert these sufficient conditions from a plotted curve or a bisection routine.

A second proposition defines the two risk-specific option values from enabling deliberate preference adjustment. Their difference exactly equals the adjustment-induced change in the risk-class ranking. It supplies necessary and sufficient sign conditions for adjustment to reverse a previously preferred risk class. Nonnegative option value in each class alone is not enough: the *relative* option value matters.

The matched finite experiment sets deliberate adjustment to zero at every state/date while retaining preference shocks, correlation, consumption and portfolio menus, stopping boundary, settlement, and all other primitives. It separately optimizes and independently evaluates both risk classes, reports their moment differences and option values, and varies the adjustment-cost coefficient. Opposite-sign brackets establish a crossing's existence; they are not presented as a global uniqueness proof. The executed result distinguishes the two forces: at `d=0.375`, `0.4`, and `0.5`, the adjustment-enabled economy favors the positive risk class while the otherwise identical no-adjustment economy favors the nonpositive class. At `d=1`, both favor the positive class. Thus the adjustment option changes a risk ranking under the same stopping contract but is not necessary for every duration-induced reversal. Raising the adjustment-cost coefficient shifts the observed bracket toward higher duration compensation; the no-adjustment bracket lies further right. Exact values and brackets are generated in the main tables and execution summary.

The additional transition-law experiment also extends the counterfactual range: the probability of positive versus negative co-movement regimes changes, rather than only a reward coefficient. This finite mixture is stated precisely and is not conflated with a Brownian correlation interpolation. The old diffusion boundary analysis, correlation panel, recursive-utility example, sophisticated-self checks, and persistent-capacity game are preserved in their separate scopes.

**Locations:** `04d_risk_frontier.tex`; the final subsection and two mechanism tables in `05b_incremental_evidence.tex`; `mechanism.py`; Supplement S.9.

## Presentation and preservation points

The current supplement says **authoritative R4 source record** in its inherited provenance discussion. We use **maximum of feasible policy values** or **lower bound** for `max_i J_i`, not the mathematical lower envelope. Existing distinctions between a switch band and a unique threshold, finite and diffusion guarantees, held-out and uniform guarantees, exact games and trained neural experiments, effort and coefficient-weighted expenditure, and a build and a scientific conclusion are retained.

The root revision index now identifies R6 without replacing its historical R5/R4 text. A byte-level preservation audit protects every old file except the explicitly updated root reading pointer. Current R6 paper sections contain all inherited substantive sections and every old numerical table, alongside the new results. This is a complete new manuscript and supplement, not a response letter standing in for a revision.

The advisory reports do not imply appointment by, submission to, or an editorial decision from Econometrica. The revised paper is provided for another substantive assessment; the execution and preservation checks do not predetermine that assessment.
