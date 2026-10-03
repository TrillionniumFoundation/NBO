# Neural Bellman Operators — R9

This revision responds to the 3 October 2026 advisory report on R8, pinned at `3fb6d5bd5cac245a7f693f0b8db76a5075b1c732`. The reviewed paper is candidate `f9a7e32e23c0b4173390d4807da6eace46f42ba1`. The report is owner-commissioned and is not an editorial decision of the Econometric Society.

## Authoritative manuscript

On the evidence branch, the root `ECTA.tex` and `supp.tex`, built with the inherited Econometrica class, are the complete revised article and supplement. `response.tex` addresses B1–B7 and M1–M10. The previous main text and supplement are copied exactly into `archive/` before integration. Historical applications, labels, code, figures, raw results and adverse evidence are preserved. No other paper repository or folder is modified. The development/source branches hold the exact inputs; the evidence branch additionally holds generated tables, integrated manuscripts, raw results and compiled PDFs.

## New research outputs

* An own-policy critic residual guard with saved indexed corrections and a proved nodal evaluation bound, not a convergence claim about Adam.
* A signed interval action cover with verified face domination, all crossed interpolation slopes, and a stopping-safe natural-enclosure fallback.
* Recertification of the same nine R8 hybrid policies and three raw actors; matched old/new one-step enclosure costs; explicit shared-cost accounts.
* Eighteen fresh actor/search configurations on genuinely nested grids, with unguarded and guarded continuation ablations. A separate fine-grid complete-action envelope verifies all twelve fine-grid policies.
* All eighteen inherited frozen-policy refinement maxima, quantiles, worst locations, boundary regions and saturation rates, including the 2.1234 loss.
* A model-specific externally financed flow-consumption compensation test.
* Global analytical bounds on the original dense nonlinear continuous-time capital economy in dimensions ten and twenty, and a feasible schedule evaluated on the exact historical Brownian paths.

The raw actor is not a searched hybrid. An indexed continuation is not an uncorrected network. A finite nodal certificate is not a continuous diffusion error bound. A global optimal-value bracket is not a tight neural-policy regret certificate. None of these distinctions is hidden by test success.

## Reproduce

Use Python 3.13.5, PyTorch 2.10.0 CPU, NumPy 2.3.5, SciPy 1.17.0 and mpmath 1.3.0. Set OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1. From repository root:

```sh
python -u revisions/2026-10-03-r9/code/replicate.py
bash revisions/2026-10-03-r9/code/build_pdf.sh
```

The driver saves every command, return code, runtime, log and environment. New tests check inclusion and accounting rather than requiring every economic threshold to pass. Historical tests run without modifying historical files. All reported R9 tables are generated from hashed JSON and raw-array inputs. The protocol was developed after local pilots; it is a pinned reproduction protocol, not a preregistered confirmatory trial.

## Arithmetic and statistical scope

Interval results are conditional on the inherited outward binary64 execution contract, with polynomial transcendental bounds and verified square-root endpoints. They are not machine-formal proofs. The preference economy keeps the original action box and discrete exit-monitoring rule. Continuous-state, time-discretization and continuously monitored stopping errors remain separate unknowns. Paired Euler simulations report Monte Carlo confidence intervals, not unknown discretization bias. The capital analytical benchmark instead covers the original continuous-time economy from all-zero log capital.

## Remote evidence

The scoped workflow pins the plain UTF-8 source commit, executes the program, compiles three PDFs, verifies preservation and commits evidence to a new R9 branch. Its `REMOTE_EXECUTION.json` records the source and workflow identities. The downloadable Actions artifact is a convenience copy; committed source, results, logs and PDFs do not rely on the artifact's retention period.
