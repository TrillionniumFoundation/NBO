# Neural Bellman Operators — canonical revision R9

**Revision date:** September 22, 2026  
**Revision branch:** `revision/econometrica-r9-constructive-certification-2026-09-22`  
**Base review commit:** `9749c3cf28f9438315b8f504a358bbe307ea89a5`  
**Report:** `reviews/2026-09-22-econometrica-r8/referee_report.md`

## Authoritative reading order

1. `ECTA_R9.tex` / `ECTA_R9.pdf` — current complete Econometrica-style manuscript, new results, generated numerical tables, and full new proofs.
2. `SUPP_R9.tex` / `SUPP_R9.pdf` — complete R8 manuscript/proofs, complete R4 exposition/appendix, and all six delivered R5 tables, through unchanged historical inputs.
3. `revisions/2026-09-22-r9/response_to_referee.md` — point-by-point response to R8-F1–F12, with exact evidence and remaining distinctions.
4. `revisions/2026-09-22-r9/results/scientific_summary.json` — original-economy enclosures, optimal access-welfare intervals, explicit flexible precision flags, and full holdout summaries.
5. `revisions/2026-09-22-r9/replication/README.md` — certificate, training, and clean-build commands and dependency scope.
6. `revisions/2026-09-22-r9/validation_report.json` and `source_manifest.json` — validation and source/evidence hashes.
7. `revisions/2026-09-22-r9/preservation_map.md` and `inherited_manifest.json` — unchanged source chain and historical reading map.
8. `R9_REVIEW.md` — compact review entry point.

## Main scientific distinctions

The original first-exit economy is unchanged. At the central state and adjustment cost two, certified optimal access welfare is at least **0.04094994** and the restricted optimum is enclosed within **0.009047**. The flexible learned policy has payoff-evaluation width **1.33e-5**, but regret upper **0.10633861**, above the retained **0.01** target. The current manuscript does not turn evaluation accuracy into optimality accuracy.

The external evidence has a rigorous absolute lower reference and a frozen, symmetrically tuned 72-pair holdout comparison. The independent feedback baseline outperforms both learned methods in every panel. All checkpoints, path arrays, and unfavorable results remain available.

The previous R3 revision index is archived at `revisions/2026-09-22-r9/archive/REVISION_INDEX_before_R9.md`. Earlier manuscript and review branches remain intact; the R9 branch is the single canonical pointer for this resubmission.
