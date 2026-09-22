# Neural Bellman Operators — R16

This directory is the materialized scientific revision responding to the R14 referee report. Start with `/R16_REVIEW.md`, `/ECTA_R16.pdf`, `/SUPP_R16.pdf`, and `RESPONSE_TO_R14.md`.

## Replication

Use Python 3.13, NumPy 2.3.5, SciPy 1.17.0, SymPy 1.14.0, CPU Torch 2.10.0, a C compiler, and MPFR headers/library. The GitHub workflow records the actual platform and library version. Set `PYTHONDONTWRITEBYTECODE=1` and `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.

From a clean checkout with the new experiment output directories moved aside, run:

```sh
python revisions/2026-09-23-r16/replication/run_all.py
python revisions/2026-09-23-r16/replication/generate_tables.py
python revisions/2026-09-23-r16/replication/validate_publication.py
```

The scientific runner refuses existing experiment outputs. It does not overwrite the published evidence. A separate working copy is appropriate for reproduction. The manuscript builder reads the retained JSON and rounds certificate bounds upward. PDF compilation requires TeX Live with the retained `econsocart` class and its dependencies.

## Evidence

`results/neural/` contains all ten original-economy seeds, twenty checkpoints, complete cell records, refinement, and the all-face ablation. `results/baselines/` contains six state-space policies and separate continuous-time certificates. `results/inventory/` contains twenty neural gain checkpoints, full-time certificates, dimension-specific total bounds, and a classical diagnostic. `results/fresh_library/` contains a model-generated price continuum with no inherited policy/pilot inputs. `results/mpfr_library/` contains all eighteen historical-node recomputations in established directed arithmetic. `results/foundation_checks.json` contains the trace-jump arithmetic, kernel and policy-iteration regression checks, and the consumption-top-up calculation.

The original nonlinear neural accuracy target is not attained by the new full-horizon checkpoints. The accurate inventory certificate and sharp time-control/dual results have different scopes and are not substituted for it. Read the response's gate summary together with the tables.

All pre-R16 scientific files are preserved. The preservation and publication manifests identify input hashes, source and result commits, and directly readable output artifacts. Temporary source transport is not the scientific review object.
