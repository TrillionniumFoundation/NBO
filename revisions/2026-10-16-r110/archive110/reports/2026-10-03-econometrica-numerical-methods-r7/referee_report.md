# Referee Report on “Neural Bellman Operators” — R7 Evidence Package

**Venue perspective:** *Econometrica*, numerical and computational methods  
**Source branch reviewed:** `revision/econometrica-nbo-r7-source-2026-10-03`  
**Pinned source commit:** `5bab4649728860fb655c5371f3705787f10b4a78`  
**Pinned source tree:** `0530053a1650bc33ad9b674595b0a2e2db126af1`  
**Evidence branch reviewed:** `revision/econometrica-nbo-r7-evidence-2026-10-03`  
**Pinned evidence commit:** `b1409008625f550195ce9ead468391ad2449a240`  
**Pinned evidence tree:** `1499e003360f060158d2c086e5d94effa2ee430e`  
**Main manuscript:** `ECTA.tex`, git blob `83a195c4b0dbde3b8aa356a5c83d143db3efa298`  
**Supplement:** `supp.tex`, git blob `b8b950657f4f4082353993e2b85e11168c55904f`  
**Report date:** 3 October 2026  
**Recommendation:** **Reject in the present form; encourage a new, integrated, and substantially narrower submission.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from the perspective of an external *Econometrica* numerical-methods referee. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R7 is a serious and technically useful evidence package. It directly addresses several of the most important weaknesses identified in the R6 report. The endogenous-preference exercise now produces neural policies that meet the declared finite-model policy-loss and value-error targets for all three fixed seeds. The dynamic Cournot exercise now trains separate neural critics and actors and verifies each final profile against full finite-model dynamic unilateral best responses. The high-dimensional coupled-capital study now audits the path coverage of the former training box, repeats training on a wider box, and records nested Euler diagnostics. The scalar full-domain calculation is replayed through an independent interval-arithmetic implementation. Source, environment, raw arrays, network snapshots, failed smoke targets, execution times, and verification outputs are retained. The immutable-source workflow completed successfully, and the eleven R7 regression tests pass.

These are material improvements. In particular, the R7 record changes the status of two R6 findings:

1. the NDU actor no longer fails its declared finite-model regret target; and
2. the strategic application is no longer only a non-neural grid calculation—the R7 package does train neural policies and subjects them to full finite-game best-response evaluation.

The package nevertheless is not publishable as an *Econometrica* numerical-methods paper in its current form.

The first problem is procedural but fundamental: there is no integrated R7 manuscript. The root `ECTA.tex` and `supp.tex` are byte-for-byte the R6 manuscript and supplement. The R7 protocol itself says that a final candidate will later incorporate the actual evidence. The main paper therefore does not contain the R7 methods, tables, numerical results, or the interpretation needed for review. What is presently available is an R6 paper plus a well-organized R7 computational appendix in the repository.

The second problem is substantive. The R7 finite-economy success does not isolate a capability or numerical advantage of the proposed actor. At every time and state, the code first evaluates every feasible action—or every joint action—using the current continuation critic. Those exhaustive action values produce both the exact argmax labels used to train the actor and the oracle used by the shortlist guard. Thus the expensive maximization that the actor is supposed to approximate has already been performed. The final result demonstrates that a neural network can compress or imitate an exhaustively computed finite policy, with a small optional correction map. It does not demonstrate that the actor makes an otherwise difficult maximization feasible.

The comparison data reinforce this point. In the NDU finite economy, guarded NBO, direct Bellman fitting, and classical backward induction all pass, but direct fitting is faster and generally more accurate than guarded NBO, while classical backward induction is roughly two orders of magnitude faster again. The neural Cournot policies pass their finite-game exploitability target, but the experiment contains no matched direct-neural or classical cost comparison and still uses all joint-action values as training supervision. The high-dimensional coverage study shows why the old narrow box was inappropriate and why the wider box is better, but it does not provide a continuous-time bias bound, a global optimal-value bound, or a uniform residual certificate. The independent interval replay strongly corroborates the one-dimensional result, but does not extend certification beyond one state variable.

R7 therefore establishes a more credible research record, not the missing contribution-isolating result. A future paper could be valuable. It should be an integrated manuscript centered on one deep theorem–algorithm–evidence chain in which the actor solves a genuinely nontrivial action problem without full enumeration and is compared at matched economic accuracy with strong direct and classical alternatives.

## 2. Scope, provenance, and limitations of this review

### 2.1 Reviewed objects

I treat the following pair as the R7 evidence package:

- source commit `5bab4649728860fb655c5371f3705787f10b4a78`; and
- its child evidence commit `b1409008625f550195ce9ead468391ad2449a240`.

The evidence commit was created by the successful workflow run `37106521953` from the pinned source commit. Its parent is exactly the source commit.

The later development commit `bdf29a9e5ba93b0c80b9d9d924133d466878ed5b` is not part of the reviewed evidence. It adds only an unexecuted supplementary-comparison protocol, prepared after the primary R7 results were observed. Its proposed gated-architecture, Chebyshev-projection, and additional domain calculations are future work, not evidence available for this decision.

### 2.2 Manuscript identity

The root manuscript and supplement have the same git blob identities as R6:

- `ECTA.tex`: `83a195c4b0dbde3b8aa356a5c83d143db3efa298`;
- `supp.tex`: `b8b950657f4f4082353993e2b85e11168c55904f`.

The R7 source commit adds protocols, code, tests, and workflow material; it does not revise either paper source. The R6 paper imports R6 manuscript fragments and its replication appendix enumerates the R6 record rather than the R7 evidence. I therefore review the scientific meaning of the R7 package, but I do not regard the package as a finalized paper revision.

### 2.3 Verification performed for this report

I inspected the manuscript, supplement, R6 referee report, R7 protocols, source code, workflow metadata, environment record, JSON outputs, and the reported raw-array identities. I recomputed the aggregate comparisons in this report from the committed JSON results.

I did not independently rerun the complete R7 training suite in a separate local environment. The execution facts stated here are consequently facts about the pinned successful workflow and its committed evidence, supplemented by source inspection and internal consistency checks. This limitation is distinct from the repository’s own eleven passing regression tests and from the independent R6 reruns described in the preceding referee report.

## 3. What R7 successfully resolves

### 3.1 The finite NDU policy result is now positive

The R7 NDU study uses the disclosed `17 × 25` state grid, 20 time steps, 175 actions, and the three fixed seeds 11, 29, and 47. The raw actor policies have full finite-model payoff-loss upper bounds between `0.04450` and `0.04995`, already below the declared `0.1` target. The final guarded policies have bounds between `0.02598` and `0.02626`. Maximum value errors are between `0.08137` and `0.13246`, below the declared `0.2` target.

This is a real repair of the R6 negative result. The favorable result is not obtained by deleting failed history, changing the economic model, or selecting one seed after execution.

### 3.2 The actor shortlist is empirically accurate on the finite NDU model

The top-four shortlist changes the raw actor action on approximately `5.83%` to `7.75%` of active state-time nodes. The exhaustive guard changes only approximately `0.23%` to `0.33%` of active nodes. Thus the actor and shortlist are not merely random proposals rescued everywhere by the guard.

This fact should be retained and reported prominently. It is a useful policy-compression result.

### 3.3 Neural dynamic-game policies now receive full finite-game checks

For both market normalizations and all three seeds, the raw and final neural profiles pass the declared `0.1` finite-game payoff-loss target for both players. The largest final player-specific bound among the six principal cases is approximately `0.06238`. The guard is never invoked in the principal game runs.

The code also records missing pure one-step equilibria and does not conceal them. The full backward best-response calculation is player-specific and checks every stored finite state, time, and unilateral action. This is substantially stronger than inferring equilibrium from actor stationarity or a joint loss.

### 3.4 The high-dimensional coverage problem is diagnosed rather than ignored

On the old `[-0.5,0.5]^20` box, essentially every simulated path exits and paths spend roughly 35–49 percent of grid times outside. The former local residual diagnostic could therefore not support an initial-state value interpretation. Wide-domain training on `[-1.5,0.5]^20` eliminates observed exits from that box in the recorded 512-path audits and materially reduces critic-versus-policy-payoff discrepancies.

This is a scientifically useful negative-to-positive diagnostic. It validates the R6 referee concern about state coverage and shows that domain design changes the interpretation of a residual fit.

### 3.5 The scalar certificate receives a genuinely different arithmetic replay

The `mpmath.iv` implementation replays the stored scalar leaf cover without importing the R6 interval arithmetic routine. At 40 decimal digits it obtains, for seed 11:

- NBO residual upper bound `0.00198217`;
- NBO action-gap upper bound `4.21 × 10^-6`;
- NBO policy-regret upper bound `0.04961`;
- direct-HJB policy-regret upper bound `0.04967`.

Both pass the declared thresholds. This is a meaningful independent-implementation check of the arithmetic path.

### 3.6 Reproducibility metadata are strong

The evidence records Python and package versions, BLAS and compiler information, CPU features, thread settings, deterministic-algorithm policy, source hashes, process high-water memory, raw arrays, actor snapshots, and execution times. The R7 regression suite replays all twelve primary finite-study result files, checks actor extraction from stored snapshots, and validates the finite-model certificates.

This standard of evidence preservation is commendable.

## 4. Blocking concerns

### B1. There is no integrated R7 paper to referee

The R7 package is not a paper revision in the ordinary editorial sense. The main and supplementary TeX sources are unchanged from R6. They do not:

- state the guarded actor algorithm used in R7;
- explain that the actor is trained from exhaustively computed action values and exact finite-model labels;
- report the R7 NDU pass;
- report the neural Cournot finite-game results;
- report the wide-domain coverage findings;
- distinguish raw, shortlist, and corrected policies;
- discuss the R7 cost comparison; or
- reconcile the new evidence with the claims and recommendation in the R6 referee report.

The R7 protocol explicitly anticipates a later final candidate that incorporates the actual evidence. That candidate has not been committed.

This is not a cosmetic filing issue. Numerical claims must appear in the manuscript with definitions, tables, units, denominators, limitations, and a stable mapping to source and evidence. The present paper still describes the R6 record. I cannot recommend publication of evidence that the paper does not state.

**Required remedy.** Prepare a new immutable manuscript branch that incorporates the complete R7 evidence, a point-by-point response to the R6 report, an exact source/evidence manifest, and no unexecuted development results. The final paper and supplement should compile from that branch and should identify every result by the exact evidence commit.

### B2. The actor is trained by an exhaustive action oracle, so the main capability claim remains unisolated

In the finite NDU study, every backward time step begins by computing `q = m.Q(values[t+1])` for all 175 actions at every state. The exact argmax supplies the actor’s classification label. The actor loss also uses the complete vector of action losses. The top-four shortlist is then evaluated using the same complete `q`, and the guard replaces a proposal with the exact argmax whenever its one-step defect exceeds the threshold.

The game calculation is analogous. At every state and time, the code constructs each player’s values over all `11 × 11` joint actions, identifies a pure equilibrium when one exists or a minimum-defect label otherwise, trains both actors against those exhaustively generated objects, evaluates nine shortlist pairs, and retains the full finite policy table.

Therefore the algorithm has already paid the finite maximization cost before the actor acts. The actor is a learned representation of a policy computed by dynamic programming. The final stored controller is a network-generated index table plus a correction map, not a network that independently solves a hard action problem.

The small guard fractions are favorable, and the raw actor policies themselves pass. They do not change the identification issue: supervision and target construction still require full action enumeration.

**Required remedy.** Demonstrate the actor on an action problem for which exhaustive maximization is unavailable or materially more expensive than actor evaluation—for example, a genuinely continuous, high-dimensional, nonconcave, constrained action space. Training must not use the exact argmax as a label at every state. Independent global or certified local maximization may be used for held-out verification on a manageable subset, but not as the training oracle at every node.

Absent such a study, the method should be presented as neural policy compression or approximate policy representation on a solved finite dynamic program, not as evidence that an actor overcomes difficult Bellman maximization.

### B3. R7 still does not establish a numerical advantage over direct or classical methods

The NDU comparison is now clean enough to be decisive. Averaging the three seeds:

| Method | Training + verification time | Full finite-model policy loss | Maximum value error |
|---|---:|---:|---:|
| Guarded NBO | `30.33 s` | `0.02610` | `0.10209` |
| Direct Bellman neural fit | `25.05 s` | `0.02361` | `0.07218` |
| Classical exhaustive backward induction | `0.10 s` | approximately zero on the stated finite model | reference |

Guarded NBO is about 21 percent slower than the matched direct neural fit and about 304 times slower than classical backward induction in this small finite economy. The direct method is also more accurate on average. All three methods meet the declared targets, which is useful, but the comparison does not identify an NBO advantage.

The game study does not contain a matched direct-neural baseline, a classical runtime baseline, or an actor-free policy-iteration baseline. Because all joint actions are already evaluated, these omissions are material.

The development branch proposes a gated comparator and tensor Chebyshev projection after the primary results were observed. Those studies are not executed and cannot fill this gap.

**Required remedy.** Select a problem and an economic accuracy target for which the explicit actor has a defensible computational role. Compare against:

- direct Hamiltonian maximization with the same critic;
- classical or modified policy iteration where feasible;
- a monotone/semi-Lagrangian benchmark;
- a genuine DGM-style neural PDE architecture;
- a structure-aware projection method used in computational economics; and
- a probabilistic/deep-BSDE method where the formulation is natural.

Report failures, memory, all optimization and verification work, and wall time at matched value, welfare, policy, or exploitability accuracy. Fixed-update comparisons are insufficient.

### B4. The finite-model guarantees do not transfer to the stated continuous economies

The NDU result is exact only for the specified finite state, finite action, and finite time model. Every NDU report sets `continuous_state_action_time_error` to `null`.

The game result is exact only for the specified `17 × 17` capital grid, 30 time steps, and 11 actions per player. Every game report sets `continuous_equilibrium_error` to `null`.

This scope is stated honestly in the files, but the paper’s motivating claims concern continuous-time economic control and Markov-perfect equilibrium. The current evidence does not bound:

- state interpolation error;
- action discretization error;
- time discretization error;
- reflected-boundary discretization error;
- continuous-game deviation gains; or
- convergence of the discrete policy sequence.

A fine finite-game exploitability calculation is valuable. It is not a continuous-game theorem.

**Required remedy.** Either derive and compute a continuous-to-discrete error account, including action and state refinement, or narrow the paper to a finite positive-weight dynamic-programming method. At minimum, report multi-level state/action/time refinement with a common economic object and an error decomposition that does not equate a finite-model best response with a continuous one.

### B5. The high-dimensional coverage study is a policy-evaluation diagnostic, not an optimality or scalability result

The coverage audit is an important improvement. It demonstrates that the old narrow domain was disconnected from the path distribution and that the wider domain is better aligned with realized states. Across the wide twenty-dimensional cases, the recorded 160-step critic-minus-payoff discrepancies are on the order of `0.0086` to `0.0208` for the displayed direct and NBO runs, compared with much larger discrepancies in several narrow-domain runs.

Nevertheless, every coverage report explicitly leaves both `continuous_time_bias_bound` and `global_optimal_value_bound` equal to `null`. The analytical exit calculation controls only the probability of leaving one large box from the origin under bounded controls. It does not control the payoff on exit, the residual inside the box, or optimality. Its normal-tail evaluation is not outward rounded.

The study is described as paired, and it uses common Brownian increments, but the committed JSON summaries report only within-method step differences (`80−40` and `160−80`). They do not report the paired NBO-minus-direct payoff difference and its confidence interval, even though the raw arrays permit that calculation.

Finally, a critic-versus-own-policy payoff comparison is a policy-evaluation diagnostic. It does not show that the policy is close to optimal or that NBO is more scalable than direct HJB.

**Required remedy.** Add method-paired payoff differences, a justified weak-discretization error account, and an independent optimality or regret benchmark. If a global benchmark is unavailable, state a local policy-evaluation result and remove global accuracy or scalability language.

### B6. The independent interval replay strengthens only the one-dimensional result

The `mpmath.iv` replay is valuable, but its independence is limited in a precise way. It uses a separate arithmetic implementation while reusing:

- the same trained binary64 weights;
- the same leaf partition generated by the R6 verifier; and
- the same scalar economic problem.

It independently checks the arithmetic on each stored leaf; it does not independently generate or optimize the cover. More importantly, it does not change the dimensional scope of the certificate.

The direct method reaches essentially the same welfare bound in about half the interval-replay time (`48.25 s` versus `99.88 s` for NBO), again without establishing a separate actor advantage.

**Required remedy.** Keep this result as an independent-implementation replay, not a multidimensional certification result. Extend the operational error account to an economically substantive multidimensional problem using exploitable structure, verified domain decomposition, certified relaxations, or another method whose complexity is stated and measured.

### B7. The paper remains too broad relative to its established contribution

The unchanged manuscript still combines:

- actor–critic differentiation;
- approximate-policy-iteration error bounds;
- viscosity selection;
- interval verification;
- recursive utility;
- endogenous preferences;
- temporal selves;
- dynamic games;
- stochastic Hessian traces; and
- high-dimensional scaling.

R7 adds evidence to some of these areas, but it does not create one venue-defining result connecting the full chain. The strongest pieces are now:

1. a one-dimensional continuous-domain certificate;
2. honest full finite-model error accounting;
3. a successful finite neural policy-compression exercise; and
4. a coverage diagnostic for high-dimensional policy evaluation.

That is a coherent, narrower paper. The current breadth makes it difficult to identify the actual methodological contribution and places underdeveloped applications beside the strongest result.

**Required remedy.** Refocus around one economically important problem and one clearly differentiated numerical contribution. Move algebraic checks, speculative extensions, and unexecuted comparison protocols to a reproducibility appendix or separate paper.

## 5. Major comments

### M1. Make the training oracle explicit in the algorithm and title

The manuscript must state that the R7 actor receives supervised information derived from all-action Bellman values on the finite model. Terms such as “neural policy improvement” are incomplete without this qualification. A suitable description is “all-action-supervised neural policy compression with full finite-model verification.”

### M2. Treat the raw actor as the primary neural result

All three raw NDU actors already meet the finite-model `0.1` target, and every raw game profile passes. This is more informative about the network than the guarded result. Report:

- raw policy;
- top-k shortlist policy;
- corrected hybrid policy;
- fraction corrected;
- memory required by the correction table; and
- online cost under each deployment model.

The guarded policy is a hybrid algorithm and should not be conflated with the actor alone.

### M3. Separate training, oracle construction, verification, and deployment costs

The present timing tables should distinguish:

- transition-kernel construction;
- all-action target computation;
- actor updates;
- critic updates;
- L-BFGS closures;
- shortlist evaluation;
- guard construction;
- full dynamic verification;
- classical backward induction; and
- online inference.

The all-action backup count is especially important because it reveals that the actor does not replace the Bellman maximization in the current experiment.

### M4. Explain missing one-step pure equilibria

Some game runs record state-time nodes with no pure one-step equilibrium. The algorithm chooses a minimum-defect pair at those nodes. The paper should identify their location, frequency, defect size, and effect on the dynamic best-response bound. It should also explain whether mixed actions are economically admissible and, if so, why they are excluded.

### M5. Add a true paired method comparison to the coverage audit

Because the same Brownian increments are used, report pathwise NBO-minus-direct payoff differences and pointwise confidence intervals for every dimension, seed, training domain, and step count. This is statistically sharper than comparing two marginal confidence intervals.

### M6. Calibrate the error targets economically

The `0.1` policy-loss and `0.2` value targets are absolute utility or profit units, not percentages. Report their scale relative to:

- the optimal finite-model value range;
- consumption-equivalent welfare where meaningful;
- variation across states;
- player profit in the game; and
- alternative predeclared tolerances.

A numerical pass is not economically interpretable until its units are calibrated.

### M7. Use precise terminology for interval verification

Call the R7 scalar result an “independent interval-arithmetic replay on the previously generated complete cover.” This accurately conveys both its strength and its limitation. Retain the statement that it is not a formal machine proof.

### M8. Do not count the development protocol as completed baseline evidence

The gated and Chebyshev studies in the development branch were fixed after the primary evidence was observed and have not been executed. They may inform a future study, but should not appear as results, robustness checks, or reasons to relax the present recommendation.

### M9. Create one authoritative final-candidate branch

The source/evidence split is good research engineering. For editorial review, add a read-only final candidate that contains:

- the integrated manuscript and supplement;
- a response to the preceding referee report;
- source and evidence commit identities;
- generated tables checked against evidence;
- successful compilation records; and
- a statement excluding later development material.

The review branch should be based on that final candidate rather than on an evidence-only child of an unchanged manuscript.

## 6. A viable path to a new submission

A new submission would be worth serious consideration if it does the following.

1. **Integrate the evidence.** Produce a stable paper whose prose, tables, and claims exactly match a pinned evidence commit.

2. **Choose one central problem.** The endogenous-preference model or a genuinely continuous-action dynamic game is a natural candidate.

3. **Remove the exhaustive training oracle.** Train the actor without exact all-action labels at every node. Use independent global optimization only for held-out verification or certified subsets.

4. **Establish a distinct capability.** Show that the actor handles an action geometry or computational regime for which direct maximization is materially more expensive or unreliable.

5. **Compare at matched economic accuracy.** Include direct neural HJB, classical policy iteration, a monotone method, and at least one strong neural/projection baseline.

6. **Close the discretization account.** Either compute continuous-to-discrete errors or frame the result explicitly as a finite-model method.

7. **Narrow the manuscript.** Preserve the excellent evidence discipline, but center the paper on the strongest theorem–algorithm–experiment chain rather than retaining every extension as a coequal contribution.

## 7. Recommendation

R7 is a substantial and credible computational follow-up. It repairs the finite NDU failure, trains and verifies finite neural game policies, identifies and improves the high-dimensional coverage problem, and independently corroborates the scalar interval arithmetic. The repository’s evidence discipline is unusually strong.

The package is nevertheless not a finalized R7 manuscript, and its central numerical experiment still uses exhaustive Bellman values as the actor’s training oracle. Direct neural fitting is faster and generally more accurate in the matched NDU comparison, classical dynamic programming is dramatically cheaper on the stated finite model, continuous-model errors remain uncomputed, and the high-dimensional audit does not establish optimality.

I therefore recommend **rejection in the present form**. I would encourage a new, integrated, and substantially narrower submission after the author demonstrates a genuinely non-enumerative actor advantage and carries one multidimensional economic application through a complete, matched, and operational error account.
