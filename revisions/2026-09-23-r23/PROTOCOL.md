# R23 prospective execution protocol

Date: 2026-09-23. This protocol is fixed after reading the complete R21 final report and all available R22 outcomes, but before executing the R23 experiments below. It is not a retrospective preregistration of R22. The unchanged scientific objective is a full-state, continuous-time Neural Bellman Operator for the original stopped economy at accuracy 0.01.

## Frozen inputs and scope

Review: fc16c4fb27b54e11c67ce1983b6830a39038f063, reviews/2026-09-23-econometrica-r21-final/referee_report.md. Inherited branch/source: 9c6faca40fb204494d1e0f53be1468a7ee37341a. Frozen R22 execution: Actions run 35813098721, artifact 10730632886, ZIP SHA256 0893e5c3fc285019fd37774b4b1474c1fcc318adc2df7dc331439a56bbe6a6d7. R22 source hashes and all primary failures must be retained, not replaced by R23 results.

## Budget-coordinate theorem and implementation

For positive quadrature weights, bounded logistic consumption and an interior financing target, bracket the common offset using the logit of the normalized target and the minimum/maximum raw logits. Prove unique solvability, common-intercept gauge invariance, the implicit gradient and a residual-to-root bound conditional on a positive derivative lower bound. Center the common intercept numerically. Reject nonfinite/saturated arithmetic; the ordinary proposal root is not an economic certificate. The original independent directed stopped-policy checker remains the authority for feasibility and payoff.

## Held-out factorial

Use base seeds 23000, 23100, 23200 and corner seed base+v at the unchanged four vertices (1.98,1.24), (1.98,1.26), (2.02,1.24), (2.02,1.26). Corners are independently initialized. Neural architecture: 1-16-16-3 tanh, 355 parameters. Direct representation: 16x3 raw coefficients, 48 parameters. Two optimizers for each representation: Adam (learning rate 0.005), L-BFGS-B (maxls 40, ftol 1e-13, gtol 1e-8). Cap each configuration at 400 joint objective/gradient evaluations and restore the last accepted L-BFGS-B iterate when exhausted. Raw direct coefficients equal the neural outputs at the sixteen time nodes. The four primary arms must share the exact delivered initial policy in binary64.

Add a separately identified coordinate-control arm for both optimizers: 15 free intercept contrasts with the sixteenth intercept fixed to zero, plus 16 slopes and 16 preference drifts (47 parameters). Map its initial policy from the same network. Record the maximum delivered coefficient discrepancy; require at most 2e-12. This arm changes coordinates, not the set of financed policy functions. It is not a hidden-layer ablation by itself.

Total: 3 ensembles x 4 corners x 3 coordinate representations x 2 optimizers = 72 configurations, all retained. No seed/configuration selection. Certification failure or nonfinite proposal leaves the initial incumbent delivered. Acceptance requires candidate payoff lower > incumbent payoff upper. Record generated and delivered objects separately, every failure, initialization matching, objective/gradient/extra line-search calls, parameter counts, generation time, check time, root calls, root iterations and maximum root residual.

## Certification and interpretation

Apply the inherited general pair-moment Jensen theorem to all three ensembles, including nonsynchronized initial experts. Report regional regret, actual initial-to-final payoff gain, and neural-Adam versus each direct-Adam coordinate system. All continuum analyses are a posteriori certifications of frozen policies; the comparisons to be reported are selected here, not after observing their signs. No ordinary quadrature residual, gradient test, or runtime measurement is a continuous-model proof. The dual construction cost and shared certification dependencies remain visible. No local result may be called full-domain accuracy or unconditional neural dominance.

## Deterministic correctness tests

Test root bracketing, translation invariance, implicit gradient against centered finite differences, the common-shift null direction, nonfinite rejection, and the quotient mapping on fixed synthetic cases, including large common offsets. These are numerical/code regression tests, not mathematical proof by sampling. Recheck inherited proof-critical invariants without overwriting frozen scientific results. Report all outcomes and exact source/result identities.

## Publication

Create a new Econometrica-style ECTA_R23, SUPP_R23 and RESPONSE_R23 with full proof/source/result dependency tables. Preserve earlier text and results at their original paths; archive the previous navigation index before updating it. Compile and inspect PDFs, verify historical blob preservation, and publish only on new R23 revision branches. Keep the 0.01 full-domain objective unchanged and distinguish achieved conclusions from unresolved numerical performance requirements.
