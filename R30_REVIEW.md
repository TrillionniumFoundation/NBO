# R30 referee copy

**Article:** `ECTA_R30.pdf` (source `ECTA_R30.tex`).
**Essential supplement:** `SUPP_R30.pdf`.
**Point-by-point response:** `RESPONSE_R30.pdf` and `revisions/2026-09-24-r30/disposition.json`.
**Complete tables:** `COMPUTATION_R30.pdf`.
**Lossless historical preservation:** `HISTORY_R30.pdf` reproduces all five R29 documents, including the prior historical annex.

The current title is **Certified Bellman Operators with Neural Proposals: Adaptive Verification and Costly Policy Revision**.

## Review provenance

The source baseline is the latest second-pass R29 report, commit `3175974aed89dac1595af174a201dcae7bcfae31`. The first R29 report is at `3f2724d3db622d26f6b1e439fc01311c4858ee7e`; both reviewed `788246778893695471015ce4db76e6a61a2c9ca0`. There are 79 explicit dispositions across the two reports. These distinguish new results, interpretation corrections, retained audit evidence, and uncompleted numerical requirements; they are not 79 claims of closure.

The protocol was pushed before the new local study. The amendment records the failed nested stopping integral and stronger structural controls without altering the candidate cohort. Source files, frozen coefficients, all raw failures, exact region covers and derivative intervals are retained. No source or result predating R30 is overwritten. The old review index is copied to `source_audit/REVISION_INDEX_before_R30.md` before the root index is updated.

## New scientific content

The article proves regional Bellman comparison, a certified preservation class, minimum discounted intervention cost within that class, the finite exact zero-tolerance limit, a regional cost enclosure, and geometry-dependent work with explicit arithmetic costs. The new operating-mode study has 60 frozen neural proposals and three polynomial controls. The exact symbolic sign policy and the online minimum-cost guard are included as strong classical controls, not hidden by the Bernstein implementation. The active-boundary original-economy calculation retains material lower-boundary stopping and encloses payoff plus first two derivatives at all five declared controls.

The original all-state/all-restart current-state target remains .01, with inherited bound **7.181834580823298**. This revision does not certify that target or instantiate the full 47-dimensional derivative/residual bridge. The scalar and separate-model results must not be substituted for them.

## Reproduction

Use Python 3.13 with numpy 2.3.5, torch 2.10.0 CPU, python-flint 0.8.0, gmpy2 2.2.1, scipy 1.17.0, sympy 1.14.0 and mpmath 1.3.0. Set `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.

1. `python revisions/2026-09-24-r30/replication/replay_evidence.py` reconstructs the verbose exact records from frozen candidate coefficients and recorded observations. It does not retrain or relabel new timings. Every reconstructed scientific file is checked against its original SHA-256.
2. `python revisions/2026-09-24-r30/replication/test_revision.py --recompute-stopping --output /tmp/R30_TESTS.json` checks the new exact objects and re-executes all 15 validated stopping integrals.
3. `python revisions/2026-09-24-r29/replication/test_revision.py --output /tmp/R29_TESTS.json` rechecks the inherited 115 candidates, 286 completions and historical integrity on a full checkout, including compressed evidence.
4. `python revisions/2026-09-24-r30/replication/assemble_paper.py` regenerates all R30 tables and review documents from the frozen evidence.
5. Run `latexmk -pdf -interaction=nonstopmode -halt-on-error NAME.tex` for ECTA_R30, SUPP_R30, RESPONSE_R30, COMPUTATION_R30 and HISTORY_R30.

A new training study must run in a separate checkout/output directory, not overwrite the frozen results. `adaptive.py` gives the declared full recipe, `economics.py` the independent overlay and polynomial controls, `structural.py` the strongest exact controls, `stopping.py` the validated active-boundary oracle, and `bracketing.py` the common-oracle scalar comparison. The original failed integration source and output remain under `results/stopping/attempts/`.

The publication workflow records the source input commit separately from the resulting publication commit. A subsequent read-only exact-head workflow validates the actual referee commit. Its run/artifact identity is an external validation record, avoiding a self-referential commit hash in a committed manifest.
