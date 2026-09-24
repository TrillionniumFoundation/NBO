# R34 protocol: restart-propagated global policy-cost bounds

Date: 2026-09-24. Source review: e9bc144fbb6843d6a3436825a28584efb64fb8f1. Frozen parent: 88015b77a0c26e7b883156410b684b229fd7e86f. Work is confined to revision/econometrica-r34-verified-policy-frontier-2026-09-24.

## Lineage and timing

The parent includes an executed R32 publication and a staged R33 source archive, not an executed R33 publication. R34 preserves both. The staged global-support algorithms have been independently executed locally on the frozen R32 proposals: 168 support solves, 42 reconstructed classical controls, and 42 primal-dual summaries passed 252 independent checks. This known exploratory evidence informs the next experiment. It is not a prospective replication from the origin of the research program.

This protocol is committed BEFORE implementing or evaluating the new restart-propagated closure. It is not a claim of independent preregistration. No neural training is rerun; every installed proposal is the exact frozen R32 compiled policy.

## Fixed cohort and construction

Use the unchanged continuous-state, action-dependent maintenance model, horizons 4, 8, 12, tolerances 1/100 and 1/20, and all seven frozen proposals (defer, occupancy_stress, spline33, spline129, neural31001, neural31002, neural31003). There are 42 configurations; none may be omitted because of outcome sign.

Retain the unrestricted support-price portfolio (0,1,4,16,64,256,1024,4096) and its two-sided operating witnesses L,U. Let B_t be the existing class-free intervention-cost lower bound. Starting from A_T=0, compute backwards, with the SAME fixed local multiplier portfolio M,

z_t^a = k_t^a + beta P^a A_(t+1),
m_t^mu = min_a { z_t^a + mu [L_t-epsilon-T^a U_(t+1)] },
A_t = max {0, B_t, m_t^mu : mu in M}.

The proposed proof uses the necessary operating inequality E[T^a U_(t+1)] >= L_t-epsilon and feasible continuation cost bounds. It must distinguish all-state Markov feasibility from the stronger conditional-at-every-history convention when discussing history-dependent policies. No action is removed merely because it fails an individual-action test; randomized controls must remain covered by the lower bound.

## Outcomes, controls, and failure recording

Primary outcomes: exact integrated lower-bound improvement A_0-B_0, old and new global cost gaps against the SAME previously certified feasible deployment, and whether any positive gap closes. Secondary outcomes: per-date maximum improvement, whole-state order, piece counts, integer bit lengths, uncompressed/compressed bytes, construction/serialization/verification times, and the complete 42-case table. Report zero improvements and all unresolved computations. No improved upper deployment or neural-specific acceleration may be inferred from a tighter lower bound.

Charge all unrestricted support solves, witness construction, reconstructed classical controls, own-policy evaluation, and independent verification from the first stage; charge the closure separately. A lower-bound closure is not a free speedup. No new unrestricted support solve is permitted in this closure experiment. Hardware timings are descriptive single-machine measurements, not statistical estimates from independent machine replications.

## Independent verification

Serialize whole-interval affine formulas, all isolated knot values, every minimizing action selector and every maximizing source selector. Bind each closure to the canonical SHA-256 of its primal-dual base certificate and source support portfolio. In a fresh process, verify all support/base certificates and all closure identities/inequalities with optimizing envelope routines disabled. Test malformed terminal values, negative or missing multipliers, isolated-point corruption, false min/max selectors, wrong source hashes, and overstated reported gaps. Add exhaustive finite-tree checks for restart-feasible controls, including an explicit randomized-control comparison.

## Manuscript and preservation

Retain the complete R32 article/supplement and all historical PDFs. Preserve the staged R33 source archive and identify its provenance accurately. Add the new theorem, full proof, independent-checker specification, complete exact outcomes, and a point-by-point response to all R30 findings F1-F12 and T1-T10. Use the repository's Econometric Society article class unchanged. Keep the original stopped-economy all-domain 0.01 target and current numerical bound explicit; do not replace it by the maintenance result or the constant-control boundary optimum.
