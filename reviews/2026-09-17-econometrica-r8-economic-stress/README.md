# Complete R8 — substantive advisory review

**Reviewed commit:** `be77b2a81b4d3a68806c534c1e892d2eb4b1230d`  
**Review branch:** `review/econometrica-r8-economic-stress-2026-09-17-be77b2a`  
**Recommendation:** Major revision; not ready for acceptance.

[Read the referee report](referee_report.md). It closes or qualifies the previous six objections against the actual completed R8 and develops two new economic concerns: the surrender/participation margin and the binding initial portfolio permissions. It does not allege that changed-contract experiments disprove the original finite-model theorem.

[Executed results and provenance](reviewer_results.json) contain the author-program rerun summary, the original and dense-scan comparisons, all 36 initial-menu-extension class differences, six optional-exit comparisons, the all-state liquidation-supersolution check, and three rectangular-upper comparisons. The JSON is a compact record; the program regenerates more detailed per-case and per-cell outputs. Positive and nonpositive refer to the initial risky share. `adjustment=false`, `fixed`, and rectangular key `False` mean **no deliberate adjustment**, not a deterministic or constant preference state.

## Reproduce the new reviewer diagnostics

Use a full checkout of this review branch and the manuscript's numerical dependencies. The program verifies the two reviewed source manifests and nine runtime inputs, including the frozen policy files, before constructing the model. It performs no training and does not modify author scientific files.

From the repository root:

```bash
python reviews/2026-09-17-econometrica-r8-economic-stress/reviewer_checks.py \
  --repo . --mode economics --out /tmp/nbo-r8-economics-checks.json

python reviews/2026-09-17-econometrica-r8-economic-stress/reviewer_checks.py \
  --repo . --mode rectangular --out /tmp/nbo-r8-rectangular-checks.json
```

The economics mode independently assembles the reviewer experiments using the author's pinned transition constructor: an in-box first-position scan, first-date-only menu additions, an all-node/action/date supersolution check, and a voluntary-stopping recursion that can preserve the compulsory first interval. The rectangular mode uses the same full-menu target and deposited feasible lower bank. It is not an implementation or benchmark of external parameter-verification software.

The recorded environment was Python 3.13.5, NumPy 2.3.5, and SciPy 1.17.0. Allow approximately 2 GiB of available RAM for the baseline model and ordinary runtime variation. The reported timings are single serial observations, not repeated-machine performance estimates. Full generated JSON hashes identify the particular executed files, which include timings and environment fields; new executions are therefore not expected to reproduce those entire-file hashes. Scientific values should be compared with numerical tolerances.

## Additional author-program reruns

The report also records reruns of `replication/r8/validate.py`, `primitive.py`, and `certificate.py` in an isolated working copy. Those author programs write to `replication/r8/output`, so rerun them in a disposable worktree rather than overwriting a deposit being audited. The review does not claim retraining, a new 97/145-node spatial run, recompiled manuscripts, or a diffusion convergence bound.

Only this new review directory is added relative to the reviewed commit. The complete manuscript, historical reviews, replication source, learned inputs, and original numerical deposits are preserved. This is an independent advisory review, not an official Econometrica editorial decision.
