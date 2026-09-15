# Response to the Econometrica-style R1 report

## Revision identity and response principle

We thank the referee for the direct audit. The report identified two separate failures in the previous submission: the revision branch did not contain the files named by its index, and the inherited manuscript made mathematical and evidentiary claims that its source did not support. We have rebuilt the revision around one authoritative manuscript, `ECTA_R2.tex`, and one authoritative supplementary source, `SUPP_R2.tex`. The historical `ECTA.tex`, `supp.tex`, embedded data arrays, prior review folders, and prior revision index remain unchanged for provenance.

The revision keeps the paper's research ambition and all four application families. It changes the object being claimed. NBO is now a separated policy-evaluation/policy-improvement operator iteration with explicit boundary and equilibrium diagnostics. The paper no longer treats a joint scalar penalty, a zero-centered residual, a finite-step Adam run, or a neural approximation theorem as a substitute for verification.

The reviewer diagnostic script was executed after the revision and its twelve checks are recorded in `replication/reviewer_diagnostics.json`. That file is a verification of the report's counterexamples and arithmetic, not a claim that the historical training experiments have been replicated. Historical figures are retained only as labeled negative controls unless a run identifier, seed, configuration hash, and source digest are available.

## Point-by-point response

### R0. The claimed R1 manuscript was absent

**Response.** The new branch contains the exact authoritative files named below, plus a manifest and reproducibility instructions. `REVISION_INDEX.md` is rewritten to identify R2 paths and the historical R1 commit. The main and supplementary sources compile with the repository's Econometric Society class after the declared dependency set is installed. A clean build was run with `pdflatex`, `bibtex`, and `pdflatex`; the resulting PDFs are local build products and are not treated as empirical evidence.

### R1. The composite loss has the wrong minimizer

**Response.** We agree. The former `-E[H]+omega E[R^2]` objective is not used by R2. Definition “Separated NBO update” in Section 2 assigns the critic the policy-evaluation residual plus an explicit terminal/boundary term, and assigns the actor a detached Hamiltonian-improvement objective. The computational graph is stated, including the stop-gradient for critic values in the actor update and the stop-gradient for rivals in games.

The conditional consistency proposition requires exact policy evaluation, pointwise improvement, compactness, and a comparison principle. It does not assert that a finite neural network or constant-step Adam reaches those objects. The scalar finite-horizon counterexample and the stationary `H=1/(2 omega)` bias are included as regression tests in the theoretical section and are reproduced in `replication/reviewer_diagnostics.json`.

### R2. Boundary, terminal, and well-posedness conditions

**Response.** The general formulation now defines recursive utility policy by policy through an adapted recursive utility equation before taking the supremum. The HJB statement is restricted to a controlled Markov diffusion with covariance closure `Q(t,s,pi(s))`; an arbitrary predictable quadratic variation is explicitly outside the Markov claim unless the state is augmented. Assumption `Declared Markov problem` specifies compact state domain, admissible feedbacks, coefficient regularity, continuous boundary/terminal data, and comparison. The evaluation loss contains a boundary residual or a hard boundary architecture, and the replication schema requires independent boundary and held-out-domain checks. Each application declares its horizon, normalization, and domain.

### R3. Residual minimization does not select a viscosity solution

**Response.** We agree and remove the unsupported vanishing-viscosity implication. The revised result is a conditional operator-consistency statement. The exit-time sequence `W_epsilon` is included in the manuscript as a negative diagnostic: its boundary values are exact and its squared residual tends to zero while its limit fails the viscosity subsolution inequality. Smooth derivative approximation is explicitly limited to classically `C^2` regions. The nonsmooth benchmark is reported as an independently solved diagnostic with value, boundary, and residual errors rather than as a theorem of selection.

### R4. Merton constants and the alleged constrained kink

**Response.** The benchmark is recalculated. Under the stated stationary infinite-horizon interpretation, `pi*=0.75` and `c/X=0.04125`. The finite-horizon problem is no longer allowed to inherit those constants without a terminal/bequest specification. For the no-short parameter tuple, the unconstrained share is `-0.125` and the constrained policy is zero at every positive wealth level. The text now treats this example as a feasibility test, not a wealth-dependent free boundary. The exit-time problem supplies the independent nonsmooth diagnostic.

### R5. Experimental source and provenance

**Response.** We do not present the historical hand-entered arrays or the constructed DDPG curve as new experiments. Captions and the evidence section mark them as historical illustrations/negative controls. The R2 manifest defines the required authoritative schema: run ID, seed, configuration hash, source checksum, domain, stopping rule, failure status, held-out distribution, and error vector. `replication/reviewer_diagnostics.json` contains the reproducible analytical checks that are available in this checkout. A future solver run can be added without changing the manuscript's estimands or graph conventions.

### R6. Epstein--Zin aggregator

**Response.** The aggregator is replaced by the difference form
`f_EZ=(rho/a)[c^a(bV)^(1-a/b)-bV]`, with a declared domain `c>0` and `bV>0`, a logarithmic limit at `a=0`, and a monotone value transform. The HJB uses this one canonical expression. The formal stationary diagnostic reports `(rho,gamma,psi,mu,r,sigma)=(.04,5,1.5,.08,.02,.2)`, giving `pi*=.3` and `m*=.0455`. These are labeled formal candidates pending admissibility and verification; no small residual is used to establish the recursive-utility theorem.

### R7. Stability and convergence

**Response.** The finite-step implementation and the asymptotic statement are separated. The appendix states a conditional projected two-timescale result with diminishing step sizes, bounded iterates, martingale noise, a globally attracting critic ODE, and an actor ODE after critic equilibration. Constant-step Adam is explicitly outside those hypotheses. The TD derivative sign is corrected. The R2 audit reports sampling measure, step sizes, boundary/constraint weights, conditioning, failure status, and held-out errors; cross-seed agreement is described as evidence for a benchmark, not as global convergence.

### R8. Endogenous preferences and NDU

**Response.** The NDU application now declares bounded/viable `u` and `X` state domains, a boundary mechanism, a cardinal utility normalization, consumption units, a terminal payoff, and relative-time discounting. The derivative of the primitive CRRA flow with respect to `u` is corrected; the sign of the complete `V_u` is treated as an equilibrium object. The two-state application is retained as a preference-formation model and low-dimensional audit. Its policy surfaces are comparative-static illustrations; identification requires a separate observation model and rank/injectivity argument and is not claimed here.

### R9. Time inconsistency

**Response.** The main and supplementary sources now use one extended-HJB/one-shot-deviation formulation. Future selves' continuation policy is held fixed in the current self's deviation, and the updated policy is then imposed as the continuation policy. The equilibrium error is a held-out one-shot deviation gain. The no-present-bias limit `beta=1` is a required test. Consumption levels and consumption--wealth ratios are distinguished in the evidence schema. A target-policy lag is no longer presented as a proof of subgame perfection.

### R10. Dynamic games and Nash conditions

**Response.** Player-specific improvement steps detach rival policies and evaluate each player's own Hamiltonian. The revision reports unilateral exploitability and multiple initial profiles. The static Cournot regression test is included: the symmetric Nash quantity is `1/3`, while the joint-profit maximizer is `1/4` and has a positive unilateral deviation. Market-size normalization is declared for comparisons across firm counts. A joint loss is not used as a Nash certificate.

### R11. Scalability and novelty

**Response.** The original multi-stock exercise is identified as separable and retained as a control. The R2 design adds a genuinely coupled resource/covariance benchmark and fixes the estimands: matched accuracy, wall-clock time, memory, failure rate, value error, policy error, and improvement gap. Per-iteration derivative cost is no longer called a complexity theorem. The novelty claim is the actor-factorized constrained operator iteration and its audit decomposition, positioned against DGM/Deep BSDE and separability-aware baselines.

### R12. Hutchinson trace estimation

**Response.** The manuscript now derives
`E[(a-qhat/2)^2]=(a-q/2)^2+Var(qhat)/4`, applies the estimator to the symmetric part of the diffusion-weighted Hessian, and treats probe count as an estimand dimension rather than mere gradient noise. Exact derivatives are used for low-dimensional audit checks; probe-count comparisons record value/policy/boundary error and runtime. The actor's feasibility map is deterministic and audited independently of the Hessian estimator.

## What is retained

The NDU preference-formation mechanism, recursive utility, temporal-self extension, dynamic games, high-dimensional motivation, historical figures, and prior formal materials remain in the repository. They are reorganized and relabeled so that each retained claim has a declared model, diagnostic, and evidence class. The paper's ambition is therefore preserved while the claims are made reviewable.
