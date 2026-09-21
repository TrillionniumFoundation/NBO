# Neural Bellman Operators — R4 revision

**Authoritative manuscript:** [ECTA_R4.tex](ECTA_R4.tex).

**Branch:** `revision/econometrica-r4-stochastic-operator-2026-09-21`.

**Review base:** `79a7d84be2cbbf9bd5d181599ee110540128e3b5`, the retained R3 review branch. The original manuscript, R3 manuscript, supplements and all historical review materials remain unchanged.

## Review entry points

The main text and full technical appendices are in [paper/](revisions/2026-09-21-r4/paper/). Read the [point-by-point response](revisions/2026-09-21-r4/response_to_referee.md), [retention map](revisions/2026-09-21-r4/retention_map.md), [executed results](revisions/2026-09-21-r4/results/summary.json), and [manifest](revisions/2026-09-21-r4/manifest.json) with the manuscript.

The revision adds complete proofs of a stopped-diffusion policy-value bound, a finite-operator certificate and an adjustment-cost comparative static; it also repairs the exact policy-iteration limit argument. Executed computations include separated neural HJB updates, three nonlinear stochastic NDU neural runs with independent policy evaluation, re-solved adjustment costs, generator/covariance tests, correct sophisticated-self recursions, correct trace estimands, recursive-utility reference calculations, a dynamic finite game and a coupled dynamic LQ actor comparison.

## What the numerical results establish

For the declared six-date, 25-by-31-state, 125-action stochastic NDU economy, maximum date-zero policy value losses are .01129065, .02352608 and .01279688 for seeds 0, 1 and 2. These are finite-model comparisons, not a certified continuous-diffusion error. The portfolio policy discrepancy is appreciable even when value regret is small. The grid reference is faster than training in this two-state problem.

The preference-adjustment cost panel is a separately solved twelve-date reference calculation, not a twelve-date neural training result. Its discounted adjustment budgets fall as the cost rises, as predicted by the proved economic result. The explicit first-exit liquidation contract is a boundary-model change from the previously asserted viable rectangle; it is not hidden clipping or reflected self-financing wealth.

The unsuccessful initial neural pilot and two timed-out twelve-date attempts are included in the results record. Nonlinear high-dimensional matched sparse-grid comparisons, a continuum NDU error certificate, and neural recursive-portfolio/MPE experiments are not marked completed.

## Reproduce from the repository root

Use Python with NumPy, SciPy and PyTorch. The executed environment used Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0 and PyTorch 2.10.0+cpu, one PyTorch CPU thread. Exact source hashes are in the manifest. Hardware-dependent timing is not part of the scientific payload digest.

```bash
python revisions/2026-09-21-r4/replication/verify_delivery.py
python revisions/2026-09-21-r4/replication/audits.py
python revisions/2026-09-21-r4/replication/merton.py
for seed in 0 1 2; do
  python revisions/2026-09-21-r4/replication/solver.py \
    --n 6 --seed "$seed" --actor-steps 500 --critic-steps 1000
done
```

`verify_delivery.py` checks the delivered source/summary hashes and internal result assertions; it does not re-run training, prove the theorems, or verify the continuum error. Run the remaining commands for numerical reproduction. They write new run JSON, training histories, arrays and checkpoints under this revision's `results/` directory. Preserve the committed `summary.json` as the delivered comparison snapshot rather than silently replacing it with a different run.

The solver's default twelve-date configuration is not the successful three-seed experiment. Use the explicit six-date command above to reproduce the reported neural panel. Numerical values may vary with library versions and floating-point behavior. Compare the defined scientific quantities and tolerances, not elapsed seconds.

## Manuscript build

The canonical entry uses `\documentclass[ecta]{econsocart}` and the repository's existing Econometric Society class/configuration. From the repository root:

```bash
pdflatex -interaction=nonstopmode -halt-on-error ECTA_R4.tex
pdflatex -interaction=nonstopmode -halt-on-error ECTA_R4.tex
```

References are inline in the new entry; this build does not regenerate or overwrite the historical embedded bibliography. The local review bundle includes a separately compiled standard-class reading PDF of the same main text and appendices. That PDF is clearly labeled a reading copy, not a verified canonical journal-class build. The canonical class build has not been completed in the available execution environment. A queued GitHub workflow is not a passed build.

## Repository versus attached review bundle

The branch contains the canonical manuscript sources, current executed solver/audit sources, summary of every completed audit and neural seed, failure metrics, response and provenance files. The accompanying `NBO_R4_review_bundle.zip` additionally contains the full raw game profile, raw numerical arrays, trained NDU checkpoints, training histories, the initial pilot's executed source/checkpoint, timeout logs, and the compiled reading PDF. Those binary artifacts are not claimed to be committed to this branch. They can also be regenerated by the commands above.

The bundle is an overlay, not a copy of the entire historical repository. Unpack its `repository/` directory over a checkout of this branch to align paths. Its independent `reading_copy/` directory is buildable without the repository-specific journal class. No font files are redistributed.
