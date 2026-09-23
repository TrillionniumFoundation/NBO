# Reproducing R24

Run from the repository root at the published R24 commit. The manuscripts are `ECTA_R24.tex`, `SUPP_R24.tex`, and `RESPONSE_R24.tex`; all use the repository's `econsocart` class. R23 source and evidence remain unchanged.

## Publication rebuild from frozen evidence

```bash
python revisions/2026-09-23-r24/replication/assemble_publication.py
latexmk -pdf -interaction=nonstopmode -halt-on-error ECTA_R24.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error SUPP_R24.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error RESPONSE_R24.tex
python revisions/2026-09-23-r24/replication/publication_audit.py
```

The assembly script uses the Python standard library and validates exact dataset/checkpoint counts. Required TeX packages include PGFPlots, booktabs, tabularx, natbib, microtype, hyperref, xurl, longtable and xr. No external bibliography is fetched. The audit must run in a complete Git checkout with the reviewed commit present.

This rebuilds the publication from frozen computations. It is not independent retraining.

## Fresh scientific execution without overwriting frozen evidence

Use a disposable separate checkout or Git worktree. In that copy only, retain the frozen results under a different name before running:

```bash
python -m venv .venv-r24
. .venv-r24/bin/activate
python -m pip install numpy==2.3.5 scipy==1.17.0
python -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
mv revisions/2026-09-23-r24/results revisions/2026-09-23-r24/frozen-results
python revisions/2026-09-23-r24/replication/tests.py
python revisions/2026-09-23-r24/replication/study.py --phase all
python revisions/2026-09-23-r24/replication/assemble_publication.py
```

Expected trajectories: tuning 30, held-out 28, multicell 36, reference 12, failure 4; total 110 and 286 prescribed checkpoints. The phase order is tuning, heldout, multicell, reference, failure. Selected-rate data must exist before evaluation. An existing `record.json` is reused, so moving the result directory is necessary for genuinely fresh execution. Tests use separate small regression configurations and do not select scientific parameters.

The proposal objective and differentiation use ordinary binary64 arithmetic. Delivered-policy certificates use inherited directed interval/Taylor machinery. Geometry spectra and two-rule gradient differences are ordinary diagnostics, not directed rank or stopped-gradient error certificates. Timings depend on hardware; different library implementations can alter line searches or stopping calls. Primary and reference/failure stages used separately provisioned hosts.

## Operational history and immutable evidence

Protocol `b54afa8c9107d70094a1d84be4a3c0279916530c` predates the study. Primary run 35832563885 completed all tuning, held-out and multicell results, then failed encoding an unused infinite root-conditioning diagnostic in a deterministic reference model without a price root. `apply_accounting_repair.py` only maps that nonfinite metadata to JSON null; no scientific parameter changes.

The primary archive is `archive/primary_execution.zip`, SHA-256 `cf8da93098d0e32c6d6bd219e57aedc84a9b31d1adbee941a004a85d2a44cde8`. Recovery run 35833755321 restored it, completed only reference/failure phases, and checked all original primary files byte-identical against `results/PRIMARY_EVIDENCE_LOCK.json`. `results/EXECUTION_COMPLETENESS.json` verifies the complete counts. The readable `study.py` includes the metadata repair; the historical encoded payload is retained as audit history, not the current reproduction entry point.

`results/DEPENDENCY_LOCK.json` locks runtime-imported modules and inherited data. `PUBLICATION_MANIFEST.json` adds all current manuscript/code/result hashes, transitive TeX inputs and PDFs. `results/PRESERVATION_AUDIT.json` verifies every original reviewed Git blob. The manifest and enclosing archive are excluded from their own hash lists.

## Scientific scope

The 0.004280526 neural four-cell certificate is a time-zero augmented-state result on `[1.98,2.02] x [1.24,1.27]`. It does not replace the original-state all-start-time bound 7.241462443133396 or the unchanged target 0.01. The known-reference and post-hoc chart experiments serve distinct purposes. All direct-method advantages and neural failures remain visible. No blanket closure of stronger publication requirements is asserted.
