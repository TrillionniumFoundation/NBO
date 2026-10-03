# R7 execution protocol — 3 October 2026

Review: `reviews/2026-09-29-econometrica-numerical-methods-r6/referee_report.md` at `998dc1bb9b2049080dcd2e21d543dcbee55cb4dc`, reviewing source `01f4e00a33d9ae29142c8e49bd3c7ec107806796`.

This revision preserves the NBO topic, economic primitives, historical results, recursive utility, endogenous preferences, temporal selves, dynamic games, viscosity results and trace analysis. The existing R6 files and the review are read-only. New material is confined to R7 paths and new root entry points.

## Fixed new study

Use seeds 11, 29 and 47. The protocol is informed by R6, its new review and the supplied unpublished local follow-up; it is not an external preregistration. Smoke tests are excluded from primary counts and are retained, including unsuccessful targets.

1. **NDU:** retain the exact R6 17-by-25 state grid, 20 time steps, 175 expanded actions, cost 1, stopping payoff, reflection rule and cardinal normalization. Train a two-layer width-32 critic and actor with 160 Adam actor updates and 320 critic updates per stage, followed by at most 300 L-BFGS critic iterations. A top-four actor shortlist is evaluated against its own continuation critic. An exhaustive offline guard repairs shortlist action gaps exceeding 0.0025. The direct comparator uses 480 Adam critic updates and the same polishing cap. Report full finite-policy payoff envelopes at every node and time, raw/shortlist/final policies, repair frequency, closures, wall time, verification time and process high-water memory. Retain the R6 acceptance tolerances: policy regret 0.1 and value error 0.2. Classical backward induction on the identical kernel remains an explicit baseline. Raw extraction is an ablation of the same guarded learner, not a separately trained run.
2. **Neural Cournot:** retain R6's 17-by-17 capital grid, 30 time steps, 11 investment actions per player and both market sizes 1 and 2. Train separate width-32 critics and actors against their own objectives. Use the same 160/320 Adam and 300 polishing caps. Evaluate three proposed actions per player; repair joint one-step deviations above 0.001 using exhaustive offline evaluation. Solve each fixed-rival dynamic best response independently with outward arithmetic. The full finite-game exploitability target is 0.1 for each player, every state and time. Preserve all missing-pure-equilibrium flags and unguarded results.
3. **Coverage:** reevaluate all R6 primary and wide-domain NBO/direct policies at dimensions 10 and 20 and the same three seeds. Use 512 paired Brownian paths, nested 40/80/160-step Euler grids, seed 20261003, and boxes [-0.5,0.5], [-1.5,0.5] and [-3,0.5]. Report paired payoff differences, pointwise Student-t sampling intervals, observed exit and time-occupancy fractions. Step differences are not asserted to bound continuous-time bias.
4. **Independent interval arithmetic:** use mpmath.iv at 40 decimal digits to propagate the complete stored scalar leaf cover for seed 11 under NBO and direct HJB. Compare independently computed residual/action/boundary enclosures. This is a software-conditional independent cross-check, not a formal machine proof.

## Interpretation and reproducibility

The finite NDU and game certificates do not set continuous state/action/time errors to zero. Additive utility and profit tolerances are numerical tolerances in the stated units, not percentages of welfare. The high-dimensional comparison must not treat local residual RMS as a global value guarantee. All-action guard and verification work counts toward total cost; classical tables are not suppressed in deployment comparisons.

Record source hashes, Python and package versions, BLAS, compiler, CPU features, thread settings and deterministic-algorithm flags. Distinguish exact-source reproducibility, package reproducibility, numerical equality and threshold reproducibility. Preserve failed targets and cross-platform discrepancies.

Publish complete source before remote execution. Execution may write a separate evidence branch or artifacts, never move a frozen referee candidate. The final candidate will incorporate actual evidence and be read-only during its verification/review run.
