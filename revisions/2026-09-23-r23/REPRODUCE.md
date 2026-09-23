# Reproduce the R23 review object

Run commands from the repository root. Preserve inherited bytecode and limit BLAS threads:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python revisions/2026-09-23-r23/replication/tests.py
python revisions/2026-09-23-r23/replication/run_study.py
python revisions/2026-09-23-r23/replication/continuum_audit.py
BACKEND=mpfr python revisions/2026-09-23-r23/replication/continuous_budget_brackets.py
BACKEND=mpfr python revisions/2026-09-23-r23/replication/interpolation_certificate.py
python revisions/2026-09-23-r23/replication/build_publication.py --compile
```

Fresh training intentionally regenerates current output files and timings; perform it in a separate checkout, not over an immutable referee copy. Exact frozen replay means use the committed primary policies and records instead. The publication workflow builds from those frozen policies without retraining and verifies their hashes.

Primary execution dependencies: Python 3.13.15, NumPy 2.3.5, SciPy 1.17.0, PyTorch 2.10.0+cpu. MPFR checks use the repository's directed interval backend and system MPFR library. PDF compilation uses the bundled `econsocart` class, a TeX Live installation with the imported packages, and `pdflatex`; `pdfinfo` supplies page metadata.

The R22 source/result archive is preserved, not regenerated during R23 publication. The publication builder recovers its paper tables from frozen results without overwriting `results/build.json`. The inherited strict file-preservation assertion is retained. Timings are environment-dependent; mathematical enclosures and all hypotheses remain explicit.
