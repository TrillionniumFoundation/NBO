# R29 referee copy

Article: ECTA_R29.tex/pdf. Essential supplement: SUPP_R29.tex/pdf. Point-by-point response: RESPONSE_R29.tex/pdf. Complete numerical tables: COMPUTATION_R29.tex/pdf. Historical preservation: HISTORY_R29.tex/pdf.

Latest report: R27 (2026-09-24). `revisions/2026-09-24-r29/disposition.json` covers every R27 finding/comment/request, R26 item, and R25 second-pass item.

## Reproduction

Python 3.13; numpy 2.3.5; scipy 1.17.0; torch 2.10.0 CPU; sympy 1.14.0; mpmath 1.3.0. Set OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1.

Run `python revisions/2026-09-24-r29/replication/test_revision.py`; then `python revisions/2026-09-24-r29/replication/materialize.py`. Compile each of ECTA_R29, SUPP_R29, RESPONSE_R29, COMPUTATION_R29 and HISTORY_R29 with `latexmk -pdf -interaction=nonstopmode -halt-on-error`.

To re-execute science, use a fresh checkout with a separate output directory: the script refuses to overwrite an existing completed model. Set the module OUT variable to a new directory or move the existing results aside in an uncommitted working copy, then run controls.py. Never overwrite the archived evidence. Each environment records its own timings and source hashes.

The science workflow freezes results; the separate read-only validation workflow has no commit-message gate and checks the exact final referee commit. Run/artifact identity belongs to the external validation record, not a self-referential source hash.

The 0.01 original continuous-domain objective is not certified. Unknown-solution finite-state completion, scalar stopped-control stationarity, transport identities, and rollback are separate claims with separate evidence.
