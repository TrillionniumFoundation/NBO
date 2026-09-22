# Neural Bellman Operators — R18 referee copy

## Canonical review object

Read `ECTA_R18.pdf` (main manuscript), `SUPP_R18.pdf` (technical supplement), and `RESPONSE_R18.pdf` (point-by-point response). Editable sources are the identically named `.tex` files and `revisions/2026-09-23-r18/paper/`. The response is also available as `revisions/2026-09-23-r18/RESPONSE_TO_R16.md`.

The paper uses the repository's Econometrica `econsocart` class. The title, author attribution, original stochastic economic model, original control opportunities, and original neural accuracy target are retained. Historical theorems, proofs, experiments, adverse results, manuscripts, and review reports are not overwritten or deleted.

The review branches are `revision/econometrica-r18-certificate-aligned-2026-09-23` and its publication-pinned `revision/econometrica-r18-referee-copy-2026-09-23`. The publication commit is the commit containing the compiled PDFs and `revisions/2026-09-23-r18/PUBLICATION_MANIFEST.json`; the manifest records its source commit and all input identities without a self-referential commit hash.

## Exact inputs

- Latest report: `reviews/2026-09-23-econometrica-r16/referee_report.md`, review commit `82af00bc296da59e8a3a28ef1bf86c1d6fca2367`.
- Manuscript reviewed by that report: R16 publication `2932b74dad6d8d9efce5a114d5098a99ea17ab1f`.
- Latest scientific result input: R17 `982326994c8550db4e039d915c225a9ace8e3044`; scientific source `ab79b9db4e7ccfc89af866d6aaae68346af22a47`.
- All 589 entries in the R17 scientific manifest are checked before and after the new execution. R18 audits those already executed experiments; it does not describe them as new R18 training runs.

## Substantive revision

1. A quantitative complete-cover envelope theorem links the implemented differentiable neural objective, a checked numerical correction, and the strict policy-loss certificate. The R18 audit verifies this implication at all 60 checkpoints, covering 61,440 cells. The maximum observed integrated arithmetic correction in the local audit is below `1.20e-13`.
2. Every prescribed original-economy raw certificate trajectory improves at the recorded budgets. The manuscript reports all ten paired seeds, both architectures, all signed decompositions, the 65,536-cell fixed-network refinement, and actor/critic interchange. It proves a fixed-witness floor and explicitly distinguishes certificate descent from true policy improvement.
3. Six unrestricted classical candidates have their own witnesses and full continuous-time checks. A new audit supplies full-domain ranges for those six policies and full-price/time ranges for every one of the twenty fresh-library policies. The historical restricted/common-witness table is preserved and identified as such.
4. A heterogeneous nonlinear control problem uses the complete 8-, 32-, or 128-dimensional state as neural input. A proved strongly-convex correction gives a state-uniform **total** loss bound `1.0360425735991298e-6` at dimension 128 after 32 corrections. Matched classical comparisons and exact-real versus stored-plan semantics are explicit; neural superiority is not asserted.
5. A new proof gives sufficient **budget-feasible** initial-wealth compensation `0.0078`, or `0.624%` of wealth `1.25`, for the sharp original-economy library. This replaces neither the neural accuracy requirement nor an empirical calibration. A directed-arithmetic Riccati benchmark and a finite-horizon defect-allocation lemma are also included.

## What the evidence does and does not establish

The final accessibility-aware original-economy neural bounds are `7.27831906346675` through `7.343665026665505`. They improve substantially but **do not attain the unchanged `0.01` target**. The fixed-witness theorem explains why cover refinement of these particular critics cannot remove that gap. The sharp specialized price library and the separate nonlinear inventory result are not presented as a successful `0.01` original-economy neural solve.

The complete response addresses findings R16-F0–F13, technical comments R16-T1–T14, and gates R17-A–G. `REVIEW_STATUS.json` records the exact conclusions, including the still-unmet original neural accuracy and sharp matched-classical-accuracy requirements.

## Reproduction and validation

Run from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python revisions/2026-09-23-r18/replication/reproduce.py
python revisions/2026-09-23-r18/replication/build_pdfs.py
```

The new execution includes 450 exact-rational arithmetic checks, 80 exact-rational finite-MDP cases, all 60 envelope audits, two independently replayed full-cylinder certificates, all 18 final nonlinear neural query plans, six classical control-range checks, and twenty library control-range checks. Derivative/Hessian samples are diagnostics, not proofs of global assertions.

`results/validation.json`, `results/objective_bridge/objective_bridge_summary.json`, `results/control_ranges.json`, and `build_logs/pdf_validation.json` contain machine-readable results. The GitHub publication workflow re-executes these checks and builds all three PDFs in three passes. Source, results, exact software versions, PDF hashes, and the no-historical-file-change check are pinned by the publication manifest.
