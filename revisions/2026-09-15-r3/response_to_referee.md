# Response to the R2 referee report

We thank the referee for the second audit. The R3 revision changes the authoritative object and records executable evidence. The neural architecture remains the proposed high-dimensional method; the new run ledger is a deterministic reference harness for the corrected operators, finite-grid boundary problem, and diagnostic estimands. It does not relabel a reference-grid calculation as a neural training run. Historical arrays, trained/two-solve objects, valid counterexamples, and unfavorable results remain in the repository, while current economic statements are generated only from the R3 ledger.

## F1. Missing solver and author runs

R3 adds `replication/run_r3_diagnostics.py`, a dependency-light executable reference implementation. It produces thirteen deterministic records covering the corrected Merton and no-short anchors, bounded NDU dynamic programming, beta=.7 and beta=1 temporal-self recursions, player-specific Cournot best responses, Epstein--Zin domain checks, Hutchinson probe counts, and genuinely coupled quadratic-resource benchmarks at dimensions 4, 8, and 16. Each row carries a run ID, seed, configuration digest, source commit, domain, stopping rule, non-null applicable metrics, and raw-output digest. The ledger distinguishes `reference_audit` from neural training evidence. The manuscript now states this distinction in the abstract, introduction, validation section, and replication note.

## F2. NDU discounting mismatch

The NDU objective now discounts the complete running integrand, including adjustment cost, and discounts the terminal payoff by the same relative kernel. The HJB has the corresponding `-rho V` term and terminal condition `V(T,u,X)=G(u,X)`. R3 fixes `u`, `X`, action bounds, terminal payoff, horizon, and the projected viability map used by the reference solver. The prior flow-only discount convention is retained only in the historical source.

## F3. Temporal-self contradiction

The main manuscript, inline supplement, and standalone `SUPP_R2.tex` now use one discrete-time sophisticated-self system. Evaluation freezes the continuation policy, while improvement maximizes `u(c) Delta + beta exp(-rho Delta) E[V_{n+1}]`; the continuation value itself uses `exp(-rho Delta)`. The terminal value is `G`. The beta=1 run is the exponential-discount benchmark and the beta=.7 run reports the held-out one-shot deviation gain. The former beta-on-current-utility formula has been removed from the authoritative sources.

## F4. Exact-operator theorem and neural bridge

The consistency proposition now states the policy space topology, the `C^{1,2}` value space, precompactness/equicontinuity, continuity of policy evaluation, measurable selector attainment, policy-class closure, comparison, verification, and selector continuity at accumulation points. The proof identifies the shifted policy sequence through selector continuity. The actor remark now describes the detached Hamiltonian loss as a local surrogate; a lifetime-objective gradient requires occupancy or adjoint weighting. The text separates the exact-operator theorem from neural approximation and reports critic, boundary, actor-gap, and value-change metrics separately.

## F5. NDU and Epstein--Zin boundary problems

The R3 NDU model specifies all state and action domains, terminal payoff, normalization, horizon, Brownian parameters, state-constraint projection, and compact control set. Interior formulas are explicitly labelled candidates; the implementation uses constrained maximization and records boundary/viability diagnostics. The Epstein--Zin implementation uses `V=-exp(W)`, so `bV>0` is enforced by construction, and records the admissible consumption/value domain and terminal-sign check. The stationary ratios remain algebraic targets and are not presented as a verified infinite-horizon solution.

## F6. Coupled scalability

R3 adds an executable coupled quadratic-resource benchmark with cross-state covariance, fixed state draws, reference and stochastic trace evaluations, local CPU timing, memory, and error records at dimensions 4, 8, and 16. The paper now calls these local reference timings and removes the unrecorded H100 milliseconds claim. The separable stock exercise remains as a control. No complexity theorem is inferred from one differentiation count.

## F7. Historical arrays and economic prose

The historical figures remain in the source for provenance, but the surrounding NDU text and captions now identify them as archival negative controls. They no longer support claims about a trained network, a house-money effect, a comparative static, or current economic inference. Current claims point to the R3 ledger and its run-level digests.

## F8. Epstein--Zin evidence

The R3 ledger records the corrected aggregator, parameters, `V=-exp(W)` transform, `bV>0` domain audit, terminal-sign check, and stationary targets. These are executable algebraic/domain diagnostics. The manuscript labels the targets as formal until a full neural recursive-utility training record is supplied.

## F9. Dynamic games

The executable Cournot audit evaluates player-specific best responses, records the symmetric Nash quantity, the joint-profit quantity, and unilateral exploitability. The static result is explicitly a regression test for the detached-rival graph; it is not claimed to be a dynamic Markov-perfect equilibrium without a dynamic run. The equilibrium definition and the scope of the result are now separated.

## F10. Hutchinson probes

The R3 harness runs the same symmetric diffusion-weighted matrix under `K=1,2,8,64` Gaussian probes and records trace error, squared-residual shift, and the probe mode. The manuscript retains the exact bias identity and now points to executed probe-count records. Runtime and memory are reported by the coupled harness; no asymptotic cost theorem is claimed.

## F11. NDU comparative statics

The unconstrained formulas are labelled interior candidates and are not used as global KKT conclusions. The R3 reference problem re-solves the bounded baseline under the declared viability projection and reports value, policy, boundary, and improvement errors. A full $k$ comparative-static panel remains a separately identified extension; the historical surface is excluded from the evidence flow and is not used to claim one.

## F12. Manifest and build package

R3 adds a manifest generated after the final source commit, the R2 report and manifest as immutable review inputs, the executable script, the result ledger, raw-output digest, environment record, and build transcript. Duplicate data declarations and duplicate application headings are removed. Hyperref anchors are unique, mathematical bookmarks are escaped, and material overfull boxes are resolved. The main and standalone supplement compile with the declared sequence; generated PDFs and temporary files remain build products rather than empirical evidence.

The revised paper therefore retains the full model family and methodological ambition while making the distinction between an exact operator, a deterministic reference audit, and a neural training result explicit and reviewable.
