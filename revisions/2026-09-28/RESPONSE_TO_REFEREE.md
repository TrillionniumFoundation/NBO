# Response to the September 15, 2026 advisory referee report

**Manuscript:** Neural Bellman Operators, Qian QI.  
**Review baseline:** `2fd3a5660e36e7e6a71abb4102480bdea03f6d9a`; reviewed paper baseline `bf049e302e9ed38303084e8da16b13717b052a70`.  
**Revision date:** September 28, 2026.  
**Status:** Author-requested revision for further advisory review; not an Econometrica editorial decision or independent acceptance.

We thank the referee for identifying failures in the population objective, solution-selection argument, and numerical evidence. The response is a reconstruction of the relevant equations, proofs, and executable calculations within the original NBO research topic, not a change of topic or a rhetorical weakening of the same invalid assertions. The revised main manuscript replaces the reviewed root `ECTA.tex`; the revised `supp.tex` uses the same economic models and computational graph. All original manuscript and supplement contents are preserved byte-for-byte in `archive/`. Existing bibliographies, template files, comments, and images are retained.

## R1. Composite loss and incorrect minimizer proposition

**Change.** Equations `eq:criticloss` and `eq:actorloss` define different parameter-block objectives. The actor, sampling points, and rival policies are detached during evaluation. Every critic derivative channel is detached during improvement. The method does not jointly differentiate the sum of the objectives. The previous minimizer proposition is replaced by Theorems `thm:verification` and `thm:discrete`, with complete proofs in the main appendix.

**Direct test.** The hard-terminal counterexample is retained: the old loss changes by `-epsilon/2+7 epsilon^2/3`; the revised critic loss changes by `7 epsilon^2/3`. The graph tests independently confirm zero actor gradients from critic evaluation and zero critic gradients from actor improvement. This is an implemented change, not a reinterpretation of the former pseudocode.

## R2. Boundary data, Markov closure, and well-posedness

**Change.** Section `sec:model` defines a controlled Brownian Markov state and policy-specific recursive utility before optimization. Assumption `ass:model` specifies the comparison class, admissibility, invariant utility interval, and boundary requirements. Equation `eq:terminal` and the core `HardTerminalValue` implement exact terminal data. Lateral stopping and reflection conditions are separately stated; a terminal architecture is not claimed to enforce them. The manuscript distinguishes stationary transversality from finite-horizon terminal payoffs and explicitly addresses predictable non-Markov covariance.

**Direct test.** The terminal architecture is checked for exact equality at random states. The NDU reference checks terminal and wealth boundary arrays at every time level. The recursive matching-bequest example supplies positive utility-domain barriers, rather than assuming that a fractional power is well defined for any network output.

## R3. Viscosity selection

**Change.** The integrated-residual/spectral-bias inference is replaced by a positive-weight implicit recursive Bellman map. Theorem `thm:viscosity` specifies stability, consistency, boundary attainment, comparison, and an `o(h)` neural evaluation-plus-improvement error. The proof uses contraction error transfer and half-relaxed limits. The finite-horizon accumulation formula covers recursive regimes without stationary contraction.

**Direct test.** The referee's wrong smooth exit sequence remains a diagnostic. Four grid sizes recover the correct value, while the wrong sequence has a scaled monotone Bellman residual near two. This example is explicitly an undiscounted shortest-exit problem, not incorrectly placed under the discounted contraction theorem.

## R4. Merton arithmetic and the purported wealth kink

**Change.** The stationary targets are independently derived: unconstrained risky share `0.75`, consumption share `0.04125`; the negative-premium unconstrained share is `-0.125`, and the no-short-sale optimum is zero at every positive wealth. The latter is treated as a boundary-action test, not a viscosity kink. The nonsmooth exit problem supplies the separate selection benchmark.

**Execution.** Three seeds each for unconstrained and constrained homothetic output networks recover the corrected targets. The architecture explicitly exploits homogeneity. The article does not claim unrestricted-network or ten-seed validation from these runs.

## R5. Numerical provenance

**Change.** The artificial DDPG oscillation, manually entered stability points, inconsistent constrained plot, and old Cournot/scaling tables have no experimental status in the revision. Their full source remains in the archive. The new article uses only freshly executed numerical summaries. `code/experiments.py` records parameters, all attempted seeds, iteration traces, raw arrays, environment versions, and checksums; the read-only workflow can regenerate them at an exact checkout.

**Execution.** The final primary suite records 29 completed experiments: three diagnostic families, nine portfolio calibrations, fifteen quadratic runs, and two NDU reference configurations. Eight regression tests pass. The twelve original referee diagnostics separately reproduce against the pinned original source. The initial development summary and script are preserved with their superseded status: a reporting-sign error in the quadratic residual and an omitted explicit wealth-boundary reset were corrected before the complete final rerun.

**Remaining evidence.** Historical GPU experiments cannot be reconstructed from nonexistent original logs. The new restricted-class laboratories and grid reference do not substitute for an unrestricted NBO/DGM/temporal-regression comparison. That comparison is not claimed to have been executed.

## R6. Epstein--Zin normalization and domain

**Change.** Equation `eq:ez` uses `rho/a * [c^a(bV)^(1-a/b)-bV]`, whose consumption derivative is positive. The time-additive specialization, coefficient, and consumption share are derived. The retained parameter values give `m=0.0455` and `p=0.3`.

**Verification.** The article supplies a finite-horizon stopped matching-bequest problem at the retained parameters, with an invariant utility interval and a comparison verification. It does not use the algebraic candidate as an unrestricted infinite-horizon utility-selection theorem. The broader infinite-horizon interpretation remains conditional on its independently specified utility class and transversality.

## R7. Stability and the actual update rule

**Change.** The TD derivative sign and double-discount issue are corrected. Equations and implementation agree on stop-gradients and sampling. The exact occupation/recursive adjoint weighting is derived in the supplement; uniform domain Hamiltonian ascent is described as policy improvement, not an unweighted lifetime policy-gradient theorem. Constant-step Adam is not identified with two-timescale stochastic approximation. The main mathematical results provide output error bounds and exact policy-improvement implications rather than an unproved global optimizer convergence claim.

**Execution and limits.** The portfolio update schedule and all three initializations per model are recorded. General step-size, initialization, and matched-baseline robustness are not inferred from this calibration set.

## R8. Endogenous preferences

**Change.** The baseline remains the original unnormalized CRRA preference family, now in explicit consumption units, with a reflected interval above one. Time-relative discounting applies to both flow utility and adjustment costs. The cardinal-normalization alternative is displayed as a different economic specification, not silently substituted. The utility-parameter derivative, constrained policy conditions, cross-derivative caveats, and observation-model requirements are derived.

**New economic result.** Value is weakly decreasing in the adjustment-cost coefficient; its envelope derivative is given. The manuscript does not infer a policy derivative by treating the endogenous shadow price as fixed.

**Execution and limits.** An independent two-dimensional positive-weight solver is run at two state/time resolutions for two cost coefficients. Saved arrays satisfy boundary data and the cost-value ordering. The refinement change is reported. An unrestricted neural-to-grid accuracy comparison remains to be executed and is not claimed.

## R9. Time inconsistency

**Change.** A two-exponential discount kernel gives continuous time a defined present-duration structure. Both component critics evaluate the same future policy. A spike-deviation expansion derives the acting-self Hamiltonian with the dynamic effects of deviations included. The main and supplementary equations now coincide; neither uses the former `sup{u(c)-u(c*)}` while freezing the deviator's state effects.

**Execution.** The homothetic equilibrium root is solved for four present-bias weights, including the exponential limit. Independent finite-duration deviation maximization checks the limiting first-order condition. Finite-duration commitment optimality is not conflated with a spike equilibrium.

## R10. Dynamic games

**Change.** The actor graph is player-specific, and each player's evaluation/improvement errors give a unilateral exploitability bound. The paper distinguishes symmetric architecture, initialization, equilibrium selection, and uniqueness. Fixed-market and growing-market Cournot sequences are specified separately.

**Execution and limits.** The static Cournot regression distinguishes `1/3` from `1/4` and verifies a unilateral gain of `1/64` at the joint optimum. The gradient test excludes rival and other-player-loss channels. These are not represented as a full dynamic Cournot MPNE computation; no unsupported replacement capital table is inserted.

## R11. Scalability and incremental contribution

**Change.** The additive-stock benchmark's separability is proved and a separability-aware comparator is required. A new dense nonnormal drift with a noncommuting payoff matrix supplies a coupled quadratic family. The reference is a Riccati solver; the NBO subfamily uses a quadratic neural critic, linear actor, and exact Lyapunov evaluation. The result is identified as a structural calibration, not a proof of generic neural scaling or an unfair comparison with an unreduced grid.

**Execution and limits.** Dimensions 2, 5, 10, 20, and 50 are each run under three actor initializations, with coefficient errors, actor gaps, matrices, traces, and timings recorded. The general fixed-accuracy superiority claim is not made. Actor, constraints, recursive aggregation, and baseline ablations are stated as comparison requirements rather than fictional completed experiments.

## R12. Stochastic Hessian objective bias

**Change.** The expected squared-loss variance term is derived using the covariance-weighted Hessian. Two conditionally independent probe banks give an unbiased product objective under the stated independence and differentiation conditions. Its possible negative sample values and variance are disclosed. The Gaussian and Rademacher variance formulas and complexity distinctions appear in the supplement.

**Execution.** A seeded 400,000-pair probe diagnostic checks the scalar example. The core exposes the independent-bank computation. Exact low-dimensional derivatives are retained as the validation reference, and a noisy trace is not claimed to make a correctly projected action violate its box.

## Re-review status

This package supplies a revised main article and coherent supplement, mathematical proofs, explicit model repairs, an executable general block core, fresh calibration/reference calculations, and preserved historical materials. It does not claim editorial acceptance, independent proof certification, or completion of numerical comparisons that have not been run. The unresolved work is empirical validation of unrestricted networks and full dynamic best responses, not abandonment of the NBO topic or deletion of its economic applications.
