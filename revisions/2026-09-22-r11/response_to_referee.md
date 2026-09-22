# Response to the latest Econometrica numerical-methods referee

**Manuscript:** *Neural Bellman Operators*, Revision R11.  
**Date:** September 22, 2026.  
**New branch:** `revision/econometrica-r11-accuracy-and-robustness-2026-09-22`.  
**Latest referee input:** `review/econometrica-r9-numerical-methods-2026-09-22-46aef70`, commit `251ad29668788b2a911c4ca6f9c0a226886518d6`, report blob `42cee0954515e5578dc579a4ca0428bb4e399b2e`.  
**Source evaluated by that report:** `46aef70a24f74cf57503018a7e7f21cb46af08e3`.  
**Completed revision inherited here:** R10, `d633bd60818998e53051cee6e7ad351c52a61795`.  
**New frozen robustness source:** `17b0e1e786a79c26dc853eaaba83371b8f181928`.  
**New complete robustness result commit:** `a03d24ee21b52356305f7662f884264e22584b4b`.

We thank the referee for requiring the original economic calculation, its absolute precision, the comparative evidence, and the implemented algorithm to be evaluated separately. This is a new manuscript revision on top of the completed R10, not a replacement of R10 by the earlier source reviewed in the report. We preserve all completed R10 results and all earlier material. We add the two experimental components that R10 explicitly had not supplied: prospectively specified method-specific tuning with entirely new holdout seeds, and exact-reference absolute-accuracy frontiers for implemented actors. We also prove a two-error identity linking the actual deployed actor to its continuous objective and independently re-execute the three original-economy certificates.

The added comparative experiment has scientifically consequential mixed outcomes. After expanded tuning, the eight-dimensional comparison passes the predeclared sign test; the sixteen- and thirty-two-dimensional comparisons do not. These results appear in the main paper alongside, not instead of, the complete earlier holdout. We do not use the positive economic certificates or the new analytical reference cases to erase those outcomes.

## Changes with directly executed evidence

The original continuous economy is unchanged. Independent R11 recomputation reproduces the R10 regret upper bounds **0.00987439003856**, **0.00971726349286**, and **0.00996895784866** at cost coefficients 0.5, 2, and 8. These are inherited R10 constructions newly rechecked here, not falsely labeled new R11 theorems. The original optimal access-welfare interval `[0.04096859, 0.05973218]` and the cost-two-to-eight welfare-loss interval `[0.02318257, 0.04286880]` remain in the paper.

The new external study runs 168 tuning trials and 36 independent holdout pairs on the unchanged coupled nonconvex problem, with the pinned author implementation. Every method has 140 nominal tuning-training seconds per dimension. Actual sums range from approximately 140.09 to 140.31 seconds, with setup and validation separately retained. The new paired mean NBO-minus-SOC differences are -0.23863, -0.35199, and -0.07623. Win counts are 11/12, 8/12, and 7/12; the prospectively fixed three-panel adjusted sign-test values are 0.00952148, 0.58154297, and 1. The third clipped-feedback policy has lower mean cost than both trained methods in all three panels. All selected actor/critic learning-rate multipliers are interior to the enlarged tested set.

The new exact-reference study retains 30 stored policies and their deterministic continuous-cost certificates. At 128 decision dates, the three quadratic Bellman actors have regret upper endpoints below 0.00100625, 0.00052088, and 0.00172851 for tracking, mean-reverting, and ill-conditioned models. At 32 dates all three are below 0.01. Adam on the same gain outputs approaches the 32-date deployment floor. Exact-reference and policy-moment evaluators are independently implemented; no simulated best policy is used as a lower bound. The 0.001 target is not reached on the planned sequence in two cases, and those nonattainments remain explicitly visible.

## R9-F1 — A manuscript revision rather than a new protocol alone

**Response and location.** `ECTA_R11.tex` is the canonical revised paper. Its new Sections 8 and 9 report method-specific tuning and independent holdout evidence, implemented-output error identities, continuous references, and executed accuracy frontiers. Appendix A proves the added statements and all moment/rounding formulas. The abstract, introduction, and conclusion integrate these additions. All original economic sections, R10 dual proofs, retained fitted construction, and earlier proof appendices remain. `SUPP_R11.pdf` preserves the complete R10 manuscript and its entire supplement. `R11_REVIEW.md` and the root index identify the new entry points.

## R9-F2 — Useful precision for the original economy

**Response and location.** The sub-0.01 original-model target was closed in completed R10 and is reproduced independently in `results/original_recheck/k0.5`, `k2`, and `k8`. The running utility, consumption units, control bounds, correlated diffusions, stopped contract, settlement, and initial state are unchanged. The upper bounds still cover all original adapted controls, whereas the lower bounds evaluate particular feasible outputs. New analytical benchmark cases do not substitute for this economic result. The original-model precision claim is central-state, not an uncomputed uniform value-surface guarantee.

## R9-F3 — Constructive certification and refinement

**Response and location.** The R10 affine-preference source, conditional-variance allowance, localization potentials, interval covers, and three-resolution refinements are retained and re-executed. Their complete failed and successful refinement levels remain in the R11 recheck records. In addition, Section 9 and Appendix A provide a closed operational construction on the reference-solvable class: finite-horizon quadratic evaluation/improvement, independent continuous Riccati reference, and exact held-action moment verification. The error tolerance is checked on stored policies, not asserted from a small training loss or a difference between meshes. All 30 planned reference-policy records are included.

## R9-F4 — A genuine absolute reference

**Response and location.** The completed R9/R10 Cole--Hopf lower bound for the unchanged nonconvex minimization objective remains in Section 7 and its proof appendix. The clipped quadratic feedback is still only a feasible policy, hence its cost is not mislabeled a lower bound. The new Section 9 goes further for the expressly defined analytical family: continuous quadratic verification proves the exact optimum, and a closed form is enclosed with outward interval arithmetic. An independent interval moment recursion encloses the original continuous cost of the exact stored sample-and-hold actor. Their difference is an absolute-regret interval, not merely a cost difference between competing policies.

## R9-F5 — The frozen holdout and the declared inference rule

**Response and location.** The complete R9 six-panel holdout remains the evidence for that frozen protocol; its d=16 nonsignificance is unchanged. Section 8 reports the entirely new three-panel study with its own correction specified before execution. Only d=8 passes its declared test. We neither privilege a favorable descriptive mean interval over the sign test nor pool old and new seeds selectively. The weaker d=32 directional result after expanded tuning is stated directly in the main text. The inferior performance relative to the third clipped-feedback rule is retained in every panel.

## R9-F6 — Consequential method-specific tuning and boundary expansion

**Response and location.** This previously unexecuted component is now supplied. The frozen `protocol.json` and `replication/robustness.py` specify twelve initial configurations and two adaptive extension slots per method, two disjoint tuning seeds, a fixed per-trial budget, and an unopened holdout. Multipliers extend to 9 and 27 beyond the old upper limit of 3. NBO varies evaluation/improvement ratios and transition particles; SOC varies adversary rate and test-output dimension, J/K, and initial/updating multipliers. Boundary extension is triggered by the tuning selection rule, never by holdout performance. All six final learning-rate choices are interior to the enlarged tested set. The exact configurations, all unsuccessful candidates, actual clocks, and raw validation outcomes are versioned. This is a finite, genuinely method-specific tuning study under equal nominal opportunities, not a claim of exhaustive global hyperparameter optimization.

## R9-F7 — Matched absolute accuracy and computation

**Response and location.** The original economic verification frontier remains. The new tables in Section 9 add a common absolute-regret axis and first-attainment times for two implemented policy generators within each reference model. Time includes earlier unsuccessful meshes/checkpoints and their verification, with setup exclusions stated explicitly. The exact construction and Adam operate on the same held-action gain-output class. At fixed N=32, further optimizer work cannot remove the independently measured deployment floor.

The new result is an executed matched-accuracy experiment, not just a renamed fixed-budget comparison. Its exact quadratic constructor exploits analytical structure; it is not the general tanh NBO or the pinned SOC solver. Therefore it does not establish external tanh-NBO-versus-SOC all-in matched-accuracy dominance on the original nonconvex family. The main paper does not conflate these distinct comparisons.

## R9-F8 — More than one mechanism without discarding broad material

**Response and location.** The new protocol adds tracking, mean-reverting, and ill-conditioned reference problems, including positive uncontrolled drift coordinates and differing noise and control-cost conditioning. These complement the unchanged controlled-exit economy and the unchanged coupled nonconvex objective. The new experiments therefore test additional mechanisms and supply independent references rather than varying dimension alone.

They remain a structured linear-quadratic class, not a new external-comparator tournament across every operator extension. Recursive utility, sophisticated temporal selves, games, trace identities, their assumptions, and their historical computations remain intact in the supplement. No new recursive or game accuracy claim is inferred from the added additive-utility experiments.

## R9-F9 — Permanent failure preservation

**Response and location.** The new study initializes every planned cell before dependency setup and uploads diagnostics under `always()`. Collection executes regardless of sibling outcome and commits available raw outputs and explicit missing/failed-cell states before the aggregate can be rejected. The executed study has no failed tuning or holdout cells; the failure mechanism is tested separately with missing-artifact injection. The analytical verifier also rejects nonfinite gains rather than dropping them. These tests are identified as software fault injections, not fabricated unsuccessful scientific runs. Checkpoints that fail an accuracy target remain real retained outcomes.

## R9-F10 — Immutable and complete review targets

**Response and location.** The new robustness source was committed as `17b0e1e...` before execution; all results were committed as `a03d24ee...`. The finished study is not inferred from an in-progress branch. The final delivery separately pins the manuscript source, independent numerical recheck results, and built manuscript, with exact PDF hashes and the latest report commit/blob in `publication_receipt.json`. The final receipt itself follows the build commit to avoid a circular self-hash. The previous R10 branch, the latest review branch, and main are not overwritten.

## R9-F11 — Quantitative implemented-actor error rather than an assumed optimizer trajectory

**Response and location.** The original-output perturbation bound and actual-network derivative allowances remain. New Proposition 4 proves two exact identities. In the reference class, continuous regret is the integral of the squared deviation from the optimal feedback weighted by the running control cost. For an implemented held-action policy it is the sum of a separately computed deployment error and Bellman action-curvature-weighted squared output errors under that actual policy's state distribution. The statement allows nonlinear adapted held-action rules; the executed policies use the disclosed linear output class.

The backward evaluation/improvement algorithm closes after N stages per coordinate in this class, and the stored Adam outputs receive independent certificates after their recorded updates. This is a quantitative theory-to-implementation link with measured optimization and deployment effects. It does not treat the original exact-operator compactness theorem as a proof that arbitrary Adam trajectories satisfy its hypotheses. Complete derivations, exact moment formulas, rounding rules, all gains, and policy hashes are supplied in Appendix A and `replication/accuracy.py`.

## R9-F12 — Economically resolved welfare and expenditure comparisons

**Response and location.** The original optimal access and adjustment-cost welfare intervals, each narrower than the magnitude of the resolved effect, are retained without changing utility normalization. Their underlying three flexible-economy certificates are re-executed. Tight intervals for the deployed policies' expenditures remain distinct from the broader valid secant enclosure for an optimizer's expenditure. We do not replace the latter by a learned-policy budget or claim a pointwise monotonicity result that the value comparison does not prove. The added reference experiments concern accuracy methodology, not a new calibration of the original welfare effect.

## R9-F13 — Continuous-action certification without a tensor safeguard

**Response and location.** The rank-one action oracle and its executed certificates through 128 action dimensions remain intact. The original-model market-deflator cancellation also retains an upper bound over all continuous adapted portfolios without enumerating them. The new quadratic benchmark constructor solves each scalar action line analytically and its N-stage operation count is explicit. These are structured non-enumerative constructions; none is presented as a generic cure for arbitrary nonconvex global optimization. The earlier finite tensor safeguard and its costs remain preserved.

## R9-F14 — Theorem-wise novelty and classical foundations

**Response and location.** The manuscript retains its comparisons with stopped verification, monotone approximation, controlled Markov chains, information relaxation, sparse grids, and occupation-measure methods. The new quadratic identities are expressly attributed to classical completion of squares and verification, with complete proofs rather than a claim that Riccati theory is new. Their contribution here is their executable connection between stored actor outputs, separate deployment and optimization errors, independently enclosed original costs, and actual time-to-accuracy records. The original economic dual construction and its quantitative welfare implications remain the main model-specific mathematical contribution.

## Preservation, reproducibility, and reading order

The current manuscript uses the repository's `econsocart` class in `ecta` mode, retains the author information, places results and economic interpretation before technical proofs, and retains all historical substantive material. The full R10 paper and supplement are embedded in `SUPP_R11.pdf`; the complete original source files remain byte-identical. The root revision index is appended, with its previous bytes archived. A baseline hash manifest verifies this preservation.

The independent checks cover the continuous Riccati reference against a separate ODE solver, the explicit scalar tracking formula, the independent torch and interval moment implementations, all 30 stored-policy hashes and regret intervals, all three original-economic certificates, all 36 new paired raw-path differences and sign tests, rejection of nonfinite gains, and explicit missing-cell preservation. Timing and numerical correctness are reported separately.

We submit the revised manuscript and full evidence package for another technical review. The central economic tolerance is met, method-specific tuning is now executed, and absolute-accuracy frontiers and implementation-error identities are supplied. External matched-accuracy dominance across general neural solvers, universal tuning optimality, and newly certified recursive/game experiments are not claimed as established by calculations that did not test them.
