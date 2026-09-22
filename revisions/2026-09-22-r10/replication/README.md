# Reproducing the R10 original-economy certificates

Start at the immutable canonical source commit in `../publication_receipt.json`, from the repository root. The receipt separately pins the later result and PDF-build commits. Verification uses Python 3.11 or 3.13, `numpy==2.3.5`, and `mpmath==1.3.0`; no neural-training package is needed to check frozen policies.

```sh
python -m pip install numpy==2.3.5 mpmath==1.3.0
python revisions/2026-09-22-r10/replication/verify_inputs.py
export R10_SOURCE_COMMIT=$(git rev-parse HEAD)
python revisions/2026-09-22-r10/replication/run_cell.py --k .5 --output /tmp/r10/r10-cell-k0.5
python revisions/2026-09-22-r10/replication/run_cell.py --k 2 --output /tmp/r10/r10-cell-k2
python revisions/2026-09-22-r10/replication/run_cell.py --k 8 --output /tmp/r10/r10-cell-k8
python revisions/2026-09-22-r10/replication/collect_evidence.py --downloads /tmp/r10 --destination revisions/2026-09-22-r10/ci_results --source "$R10_SOURCE_COMMIT"
python revisions/2026-09-22-r10/replication/test_pipeline.py
python revisions/2026-09-22-r10/replication/validate_evidence.py --skip-pdf
```

The independent executions do not overwrite frozen `results/` files or their reported local timings. They re-evaluate all three policy resolutions and all three dual resolutions, preserving actual new timings and full output under `ci_results/`. The cross-environment endpoint regression tolerance is **not** added to, or substituted for, the mathematical interval error budget. Every environment independently evaluates the outward bounds and must pass the exact 0.01 target.

## Manuscript build

Install `texlive-latex-extra`, `texlive-fonts-recommended`, and `poppler-utils`. Then:

```sh
python revisions/2026-09-22-r10/replication/make_tables.py
bash revisions/2026-09-22-r10/replication/build.sh
python revisions/2026-09-22-r10/replication/validate_evidence.py
```

The new paper is `ECTA_R10.pdf`. `SUPP_R10.pdf` contains the **complete** prior R9 paper and supplement, without omitted pages. The new main also contains the earlier constructive section verbatim as a dated appendix. Preservation verification checks 948 inherited files against the pinned complete R9 archive; the old root revision index is checked in its explicitly archived location.

## Fitting and verification are separate

`polish_policy.py` and `dual_pilot.py` document the proposal-generating computations. Re-executing fitting is optional and changes frozen inputs; it is not a certificate reproduction. It additionally requires `torch==2.10.0` and `scipy==1.17.0`. The original finite-node training criterion is a proposal objective, not an assertion that singular CRRA utility has an untruncated Gaussian expectation. The independent payoff audit uses bounded-domain polynomial enclosures and the exact stopping-contract correction.

Binary64 0.2 and 0.8 lie just above their exact decimal upper bounds. Deployment constants are rounded inward and their admissibility is checked as exact rational comparisons. The budget projection and the independent strict-wealth interval are both recorded.

The new refinement table times **verification only**. Training, output polishing, pilot fitting, dependency setup and manuscript build are excluded and are not silently reinterpreted as an all-in matched-accuracy advantage over another neural method.

## Failure preservation and immutable identities

`.github/workflows/r10-delivery.yml` has separate canonical-publication, three-cell certificate, unconditional-collection, and manuscript-build jobs. Collection runs after failed matrix jobs, records every planned cell, retains raw failed/nonfinite files and successful sibling outputs, and commits this evidence before a missing or invalid aggregate causes failure. Synthetic tests exercise complete, missing, failed, nonfinite, wrong-source, and changed-input cases; these test cases are explicitly not scientific runs.

The review input is pinned at commit `251ad29668788b2a911c4ca6f9c0a226886518d6`, blob `42cee0954515e5578dc579a4ca0428bb4e399b2e`. The source, execution result and manuscript build are distinct commits. A subsequent receipt records those hashes without attempting a self-referential commit hash. No old revision or review branch is advanced.
