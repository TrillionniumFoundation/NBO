# Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Revision reviewed:** `revision/econometrica-nbo-r59-review-ready-2026-10-09`  
**Pinned revision commit:** `00412e6a4f43100996b324ea1ace097232c3fbbf`  
**Pinned revision tree:** `df031cdb0b93b5b544387dd1b4f32782bd383ecf`  
**Pinned main manuscript:** `revisions/2026-10-09-r59/ECTA.tex`, Git blob `fe8fba25c59b70e11b06ccb5ef158d0f738e9564`  
**Pinned technical supplement:** `revisions/2026-10-09-r59/supp.tex`, Git blob `2a5208af97fb00c2bafe424d53afabdb17a3ce29`  
**Pinned response:** `revisions/2026-10-09-r59/response.md`, Git blob `368ba6e3d6280f9c040cb320530cd95414037e92`  
**Controlling prior review:** `adf1256cff9cde365246a3db2dac90c72fda3b13`  
**Report date:** 9 October 2026  
**Recommendation:** **Reject in the present form and do not continue the cumulative manuscript through another ordinary revision round. A new, sharply focused paper on verified lossless action search for analytically integrated neural continuations could merit evaluation after the computational contribution is isolated, stress-tested, and compared with optimized conventional implementations.**

> This is a repository-owner-commissioned, AI-assisted advisory referee report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Executive assessment

R59 is the strongest, most coherent, and best documented version of this project that I have reviewed. It is a canonical review-ready object rather than a detached science branch. The release contains a 65-page article, a 42-page active supplement, a 10-page response, ordinary source files, frozen protocols and records, a 6,005-file delivery ledger, and a successful clean-archive rebuild.

The new mathematical contribution is genuine. For the stored one-hidden-layer affine–ReLU continuation and the paper’s scalar investment action, analytic integration over scalar uniform innovations converts the fitted action objective into a rational piecewise-quartic function. R59 eliminates ridges that remain entirely inactive, affine, or quadratic over the feasible interval. It then encloses the reduced objective at every robust-lattice point, discards only points proved unable to minimize the original objective, and compares all survivors exactly with the inherited tie rule. The lossless-screen theorem preserves every exact lattice minimizer under valid outward intervals. The prospective-transcript theorem then shows that substituting this solver into a mathematical controller preserves the policy, whole-cell certificate, path endpoints, first-attainment decision, and stopping status, provided the controller does not branch on elapsed time or solver diagnostics.

I found no immediate algebraic contradiction in the screening theorem, its survivor-gap argument, the exact activation-region reductions, or the conditional transcript-invariance proof. The implementation also treats exactness seriously: stored binary coefficients are interpreted as rationals; interval endpoints are outward; exact rational evaluation chooses the survivor; signed weights and ties are permitted; and failure of the screen invokes the original terminating algebraic solver rather than returning an approximate answer.

The matched R58 execution supplies a clean estimand. The two implementations independently reconstruct the same fitted continuation and return exactly the same policy. Thus policy welfare, statistical accuracy, and stopping history are fixed by identity, not by an unresolved confidence interval. Across the six task–target groups, the screened solver reduces median action-search time by approximately 28.9–46.1 percent and complete-process median time by approximately 2.7–9.1 percent. Across all eighteen timing pairs, screening is faster in seventeen and slower in one; aggregate recorded process time falls by approximately 4.08 percent.

The contribution is nevertheless much narrower than the Econometrica-level claim carried by the cumulative manuscript.

The generic screening step is a finite-lattice interval elimination rule. Its NBO-specific element is the exact reduction of analytically integrated affine–ReLU ridges in a model with one scalar action and scalar uniform innovation. The experiment does not establish usefulness for multidimensional actions, general shock laws, deeper networks, larger lattices, or networks whose activation boundaries produce many survivors. Every production query retains exactly one lattice point and no fallback occurs. This is an unusually favorable regime, not a demonstrated performance frontier.

The complete-process gain is modest because verification and inference dominate. CPU frequency is not controlled, task groups use different runners, and one of the eighteen paired repetitions reverses the ordering. The result is a descriptive implementation gain on fixed workloads, not a stable or general complexity advantage.

Most importantly, R59 isolates the cost of computing an already selected trained-neural witness; it does not reverse the method-selection evidence. In the retained R57 experiment, common-only is the fastest method in all six task–target groups, exact ReLU is slower than common-only in all six, and the 72 fresh exact-ReLU-versus-comparator policy contrasts contain no certified lower exact-ReLU cost: 42 are exact policy identities and 30 remain unresolved. Within R58 itself, the added exact witness changes only one printed datewise deployed decision. R59 therefore shows how to make one neural subroutine cheaper, not that the NBO procedure is the best way to obtain the economic policy.

The original all-state Bellman-loss objective also remains weakly resolved numerically. Representative ten-percent services retain maximum datewise all-state policy-loss bounds of approximately 3.95, 6.78, and 9.25 in dimensions two, four, and eight, while the reported policy-cost intervals are below 1.5. The prospective stopping rule instead certifies an initial-law cost reduction relative to installed zero investment. This is a legitimate second contract, but it does not demonstrate high-accuracy solution of the original Bellman optimum.

R59 thus contains a technically sound and potentially publishable narrow numerical contribution: verified, lossless screening of an integrated neural action objective with exact policy and transcript preservation. It does not establish a broad NBO advantage, a strong work-to-Bellman-accuracy frontier, or an Econometrica-scale economic result.

## 2. What R59 successfully repairs

### 2.1 Canonical and reproducible delivery

The final branch identifies one immutable article, supplement, response, and evidence package. The clean-archive rebuild passes. The active documents have no undefined references, duplicate labels, missing characters, or overfull boxes. Publication adds no training services or independent policy-cost observations.

### 2.2 Exact economic-answer preservation

The screen never selects from interval midpoints. It uses intervals only to prove exclusion and then evaluates the original fitted objective rationally on every survivor. The same smallest-index tie convention is retained. The comparison therefore establishes exact policy identity, not approximate policy proximity.

### 2.3 Whole-controller transcript invariance

Under the theorem’s premises, the two solvers generate the same acquired policy, whole-cell endpoints, continuous-action accounts, interval paths, inference endpoints, construction attempts, and stopping look. Wall-clock deadline controllers are correctly excluded.

### 2.4 Matched complete-work boundary

Each mode pays for imports, source checks, fitting, every attempted action search, verification, path evaluation, inference, serialization, process exit, and log flush. The terminal solver, candidate menu, verifier, action lattice, fits, and inference streams are common. Parameter and policy hashes are checked rather than assumed from a shared seed.

### 2.5 Interpretable operation counts

Across the six group services the screen eliminates 34,543 noncrossing ridge occurrences, leaves 2,321 crossing occurrences, examines 732,160 lattice points with interval arithmetic, and sends 1,152 survivors to exact comparison. Algebraic exact evaluations fall by approximately 83–87 percent, all root-isolation calls are removed, and no production fallback occurs.

### 2.6 Correct handling of failed targets

The eight-dimensional, six-date twenty-percent target is budget exhausted under both solvers. R59 includes its work comparison but does not call faster exhaustion successful attainment.

### 2.7 Separation of welfare and computation cost

The paper correctly states that identical policies have identical expected economic cost. Any total-cost difference comes only from a separately specified computation price and implementation charge.

### 2.8 Preservation of adverse conventional evidence

The R57 common-only, quadratic, tree, menu-neural, and exact-neural comparisons remain visible. The within-neural gain is not used to manufacture neural policy superiority.

## 3. Blocking concerns

### B1. Generic screening versus model-specific reduction

The statement that valid lower and upper bounds can exclude a finite candidate whose lower bound exceeds the best upper bound is an elementary interval branch-and-bound principle. The useful architecture-specific reduction currently requires one scalar action, a fixed finite lattice, a one-hidden-layer affine–ReLU continuation, scalar uniform innovations with closed-form integration, rational stored coefficients, and a quartic primitive action cost.

The paper does not establish an analogous reduction for multidimensional actions, general shocks, deeper networks, smooth activations, or adaptive action sets. State dimension reaches eight, but the hard optimization variable remains one-dimensional.

### B2. Uniformly favorable production regime

Every one of the 1,152 recorded neural queries retains exactly one lattice point and no fallback occurs. The paper does not vary network seed within this matched study, lattice cardinality, interval precision, network width, crossing-ridge fraction, near-tie prevalence, negative-weight severity, or objective flatness. The conditional survivor-cardinality theorem assumes a growth constant not established for the fitted networks.

The experiment therefore does not identify when the favorable one-survivor regime should be expected or when screening becomes more expensive than the fallback.

### B3. Missing factorial implementation ablation

The algebraic mode uses rational hinge partitioning and cubic-root isolation; the screened mode uses exact feature reduction plus vectorized NumPy interval evaluation over the lattice. Several mechanisms change simultaneously.

The study needs at least: algebraic search after the same reduction; vectorized exhaustive lattice evaluation without pruning; screening without reduction; and an optimized or compiled algebraic solver. Without these cells, one cannot identify whether the gain comes from reduction, vectorization, enumeration instead of roots, interval pruning, or Python/SymPy overhead.

### B4. Modest and weakly controlled timing evidence

The six complete-process median gains range from about 2.75 to 9.15 percent. Screening is faster in seventeen paired repetitions and slower in one; aggregate recorded time falls by about 4.08 percent. Frequency is not controlled, different tasks use different runners, and the three repetitions reuse the same fitted object and streams. Parent checkpoint overhead lies outside the clock.

These observations support a finite-workload implementation gain, not a stable hardware-general performance result.

### B5. The exact witness is rarely economically active

The R58 datewise table records only one action change attributable to adding the exact witness. In R57, the exact witness changes nine deployed cell–attempt decisions, while the fresh policy contrasts identify no lower exact-ReLU cost: 42 are exact identities and 30 remain unresolved.

R59 reduces the cost of computing a candidate that often does not change the returned policy because the common menu already supplies the adopted action. Its economic leverage is therefore small in the executed catalogue.

### B6. Strong conventional controls remain cheaper

In R57, common-only is fastest in all six task–target groups, exact ReLU is slower than common-only in all six, and quadratic exact search is generally cheaper than exact ReLU. The policy-cost endpoints are frequently identical or unresolved.

Making the exact-neural branch 3–10 percent faster does not establish that an economist should choose NBO rather than a conventional generator returning the same or an unresolved policy at less work. The best screened NBO service must be compared directly with the best conventional complete service on the same prospective target and cost boundary.

### B7. Very loose Bellman-optimality certificates

Representative ten-percent services have maximum datewise all-state policy-loss bounds of approximately 3.946, 6.784, and 9.249 in dimensions two, four, and eight. Their expected policy-cost upper endpoints are below 0.652, 1.068, and 1.475. These are different summaries, but they share the model’s normalized cost units and show how conservative the all-state guarantee remains.

The prospective service stops on an initial-law cost reduction relative to installed zero investment. Exact fitted minimization removes only one local term; whole-cell, acquisition, continuation, and verification terms remain dominant.

### B8. Incomplete crossover and complexity account

The arithmetic account `O(dm)+O(N(1+m_c))+O(sm)` omits rational operand bit lengths, interval precision, vectorization, memory traffic, and batching. The implementation stores an `N × m_c` interval array and evaluates every lattice point.

There is no theorem or experiment locating the crossover among enumeration, algebraic piecewise optimization, adaptive branch and bound, derivative-based interval search, and certified continuous optimization. Operand-size distributions, precision, memory traffic, scaling in `N,m,m_c,s`, and fallback cost should be reported.

### B9. Uncalibrated economic value of computation

For identical policies the total-cost difference reduces to the computation price times the charge difference. This accounting identity is correct. The study does not calibrate computation price, installation charge, latency value, energy cost, or deployment frequency, nor show that the recorded saving changes a substantive adoption decision.

### B10. Scope remains disproportionate

The active article and supplement total 107 pages, with another 325 pages of complete companions. The broad program retains controlled diffusions, recursive utility, endogenous preferences, temporal selves, games, safe improvement, acquisition, learned structure, and many historical experiments.

The R59 result is a focused exact solver for one integrated affine–ReLU action objective and a fixed-work comparison on six task–target groups. The broader applications do not receive this solver or matched execution.

## 4. Major comments and required changes

1. **Reframe the paper around the solver contribution.** A focused title such as “Verified Lossless Action Search for Integrated ReLU Continuations” would match the established result.
2. **Add a factorial algorithmic ablation.** Separate exact reduction, interval screening, vectorized exhaustive evaluation, and algebraic root isolation.
3. **Execute a prespecified stress frontier.** Vary seeds, widths, lattice sizes, crossing-ridge fractions, interval precision, flatness, ties, survivor counts, and fallback rates.
4. **Extend beyond one scalar action.** At minimum execute a two-action constrained problem or explicitly restrict the contribution to scalar actions.
5. **Use optimized conventional solvers.** Include compiled/JIT algebraic search, vectorized exhaustive search, certified derivative/root routines where valid, and adaptive interval branch and bound.
6. **Strengthen timing inference.** Use randomized paired order, controlled frequency, more repetitions, several machines, and kernel-level counters.
7. **Report bit and memory complexity.** Include rational bit lengths, interval precision, logical storage, bytes moved, and peak batch arrays.
8. **Demonstrate economic activity.** Use tasks where the exact witness changes many decisions and produces a direct policy-cost or certification benefit.
9. **Compare best NBO with best conventional service.** Keep the same target, attempts, verifier, inference family, and complete cost boundary.
10. **Separate Bellman accuracy from the initial-law target.** Report a work-to-all-state-bound frontier and state whether economically meaningful Bellman tolerances are attained.

## 5. Focused publishable route

A credible new submission could center on **Verified Lossless Action Search for Analytically Integrated ReLU Continuations**. Its core would be the exact activation-region reduction, lossless interval screening with exact ties, fallback completeness, prospective transcript invariance, factorial optimized baselines, stress tests over difficult regimes, a multidimensional-action extension or explicit scalar scope, and one application in which the exact witness is materially active.

## 6. Independent verification

I performed an independent deterministic audit of the pinned R59 records and committed tables. The audit did not retrain, resimulate, or retime any service.

The audit verifies the canonical branch, commit and tree; the 6,005-file clean release; the 65/42/10-page active document set; exact policy identity; 30 attained and six exhausted services; all eighteen timing pairs; operation counts; the one datewise exact-witness action change; retained R57 conventional comparisons; and representative all-state bounds.

Across the eighteen complete-process pairs, aggregate recorded time changes from approximately `346.7441` to `332.5912` seconds, a reduction of `4.0816%`. The median pairwise algebraic/screened ratio is approximately `1.0595`. Group median reductions are approximately `9.15%`, `4.69%`, `6.00%`, `5.74%`, `4.74%`, and `2.75%`; search reductions are approximately `28.9%` to `46.1%`.

The review directory contains a standard-library verification script and machine-readable output. Full-repository mode checks the committed release and selected service files; embedded mode reproduces arithmetic from values pinned to the R59 result audit and publication tables.

## 7. Recommendation

R59 provides a technically careful and internally credible exact solver improvement. The lossless-screen theorem is correct under its assumptions, transcript invariance connects local computation to the returned economic service, and the matched experiment measures a real finite-workload reduction at exactly equal policies.

It does not establish the broad contribution required for the current Econometrica submission. The method is specialized to scalar action search for analytically integrated one-layer ReLU continuations; the catalogue is uniformly favorable and contains no fallback; complete-process gains are modest and weakly controlled; the exact witness rarely changes the deployed policy; strong conventional controls remain cheaper; and the original Bellman-optimality certificates remain very loose.

I therefore recommend **rejection in the present form and no further ordinary revision of the cumulative manuscript**. A new, substantially shorter paper centered on verified lossless neural action search, with the stress tests and optimized baselines described above, could merit serious consideration.
