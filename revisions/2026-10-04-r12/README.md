# R12: NBO evaluation, method comparison and economic implementation

## Source and review

The reviewed R11 snapshot is `840565f451be6103aeb325a8fc548a57507a8fb2`; the new advisory report is at `7e4393a6cae766b55975996a68515dc3e3b390e4`. R12 is based on that review tree. Historical revision files are not edited. `EDITORIAL_MAP.json` records exact root archives and intact relocation of the R11 learning/study sections to the supplement.

## Reproduction

Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, PyTorch 2.10.0 CPU, mpmath 1.3.0 and Numba 0.65.1 are used. Set OMP_NUM_THREADS, MKL_NUM_THREADS and OPENBLAS_NUM_THREADS to 1, and PYTHONHASHSEED to 0. TeX Live with the science/extra packages, BibTeX and Poppler build the three documents using the unchanged repository Econometrica class.

From the repository root:

```sh
python revisions/2026-10-04-r12/code/test_r12.py
python revisions/2026-10-04-r12/code/run.py --shard 7919
# Repeat for every seed in PROTOCOL.json; do not replace failed seeds.
python revisions/2026-10-04-r12/code/run.py --shard aux
python revisions/2026-10-04-r12/code/run.py --shard reference
python revisions/2026-10-04-r12/code/report.py
python revisions/2026-10-04-r12/code/integrate.py
python revisions/2026-10-04-r12/code/build.py
python revisions/2026-10-04-r12/code/finalize.py
```

The final GitHub workflow executes the same seed/auxiliary/reference shards from one source commit and publishes evidence only after completion, replay, tests, compilation and preservation checks. The workflow-run ID and source SHA are recorded in REMOTE_EXECUTION.json. The evidence commit is a descendant containing generated results, not an alternative fitted source. The archived R11 data remain history and are never silently re-labelled as new R12 fits.

## Meaning of the evidence

- Population results integrate over nine fixed balance-sheet profiles, not an empirical population or every possible state.
- The raw mean is a paired numerical statistic. Continuous-time endpoints additionally include discretization transfer, clipping tails, arithmetic and finite-family inference.
- Direct policy comparisons use the pathwise difference, not the difference of two lower bounds. Shared anchor transfer cancels; conservative statistic errors remain.
- The observed-history controller needs continuous noiseless state observation, known coefficients, an exact drift integral and private randomization. It does not recover shocks from sparse noisy measurements.
- Equal announced fitting time is not equal optimizer iterations; iteration overshoot, initialization, validation, simulator visits, updates, verification and deployment are separately recorded.
- Radius rows are fresh fits. Raw-costate, value-only, costate-only and block-update ablations are distinct algorithms.
- The scalar nonlinear HJB reference is an independent monotone finite-grid calculation with explicit boundary and mesh sensitivity. It is not a rigorous multidimensional continuous-time optimum certificate.
- A proportional fee is a specified resource experiment with net consumption and unchanged gross withdrawals. It is not a monetary calibration of computational wall time.

The final publication gate checks execution and evidence integrity, not that NBO wins. Negative and inconclusive results are kept. Ten fixed training streams do not establish inference over arbitrary future optimizer designs. Wall-clock stopping depends on hardware; selected weights, all checkpoints and realized iteration counts are retained to support fixed-iteration replay. The arithmetic and iid-noise claims remain conditional, not machine-formally verified.
