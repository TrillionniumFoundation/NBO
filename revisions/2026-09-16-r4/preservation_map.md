# R4 preservation and scientific-content map

The branch starts at the complete R3 review commit `79a7d84be2cbbf9bd5d181599ee110540128e3b5`. The original `ECTA.tex`, `supp.tex`, the R2/R3-authoritative `ECTA_R2.tex` and `SUPP_R2.tex`, previous revision directories, referee reports, reviewer diagnostics, historical arrays, and class files are retained **byte for byte**. Only the root reading index is intentionally updated. The R4 main/supplement have new filenames, so no earlier manuscript is silently replaced.

| Previous substantive topic | R4 treatment and location |
|---|---|
| General stochastic control, endogenous preferences, Markov covariance closure | Main §2; explicit policy-wise additive/recursive evaluation and complete covariance. |
| Actor/critic factorization, constraints, computational graph | Main §2–3; actual `solver.py`, `safeguard.py`, `graph_tests.py`; proposal versus checked improvement. |
| Exact policy improvement | Main §2 and Supplement S.1; complete limiting-value proof and declared topology. |
| Neural approximation and stochastic approximation | Main §3 and S.1–S.2; new quantitative error account; isolated-attractor counterexample; convex surrogate improvement. |
| Invalid composite objective and residual-only viscosity claim | Retained and proved as negative controls in S.2; old sources untouched. |
| Merton and no-short arithmetic | Actual learned homothetic feature solver and independent analytical comparison, main §6 and S.4; no-short test retained without a false wealth kink. |
| Recursive utility and Epstein–Zin | Main §6 and S.4; positive-domain architecture, fixed-policy solution, actor updates, verification class, own-policy transversality; finite-horizon domain test clearly separate. |
| NDU model, all three policies, stochastic covariance, hedging formulas | Main §4–5 and S.3; interior primitives retained; invalid projected state constraint replaced by an explicit first-exit liquidation contract. |
| NDU comparative statics and structural-estimation motivation | New cumulative-effort theorem, approximate-policy extension, full re-solved k panel and occupation statistics; observation/identification distinction retained. |
| Time inconsistency | Main §6 and S.5; authoritative sophisticated recursion implemented and independently checked for beta below one. |
| Dynamic games, unilateral deviations, many-firm ambition | Main §6 and S.5; full stochastic capacity game and dynamic best responses; normalized many-firm extension and conditional small-player error bound retained. |
| Coupled high-dimensional computation | Main §5 and S.4/S.6; new genuinely stochastic constrained resource economy, nine neural runs, same-weight ablation, convex scenario-tree cost bounds; structured LQR retained separately. |
| Sparse grids and Deep BSDE comparison | Closest primary literature and correct mathematical distinctions retained; no invented executed sparse-grid comparison or dimension cutoffs. |
| Hutchinson traces and derivative cost | Main §3/5 and S.2; correct mean-before-square experiment, repeated batches, unbiased off-diagonal estimator, conditional full cost model. |
| Historical figures and arrays | Retained unmodified in historical source files and repository. They are not recycled as current figures. Every current numerical table is generated from executed R4 JSON. |
| Provenance, failed pilots, reproducibility | New full runner, checkpoints, weight replay, per-record ledger, source verification, logs, and development record. |

This is a substantive rewrite rather than an appended erratum. The main paper presents the economic argument and results; the supplement carries complete proofs and implementation detail. Preservation of an invalid historical statement is archival preservation, not a reason to repeat it as a current conclusion.
