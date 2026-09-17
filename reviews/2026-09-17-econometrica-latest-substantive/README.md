# Latest-deposit advisory referee audit — 17 September 2026

Read [the referee report](referee_report.md) first. It assesses the latest complete R7 manuscript, not an unavailable R8 manuscript, and recommends rejection in its present form. This is an owner-commissioned advisory assessment, not an Econometrica appointment or decision.

## Pinned version boundary

Repository: `TrillionniumFoundation/NBO`. Review branch: `review/econometrica-latest-substantive-2026-09-17-0f0b1d8`.

The review is based on latest revision head `0f0b1d86a61cd741d2cf346f88acbf6ec3026416`, tree `0860ed28f4564900f02f8e7b97c0bacdb183c3a0`. Both R8 economic-frontier and economic-target-response branches pointed to that head when inspected. It adds only an honest five-line R8 initializer to the previous review commit `112a38099317d90b42bfc0028839e4320fdd1aae`. Relative to manuscript commit `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`, its 25 added files consist of 24 historical review files and that initializer. No author manuscript, replication source, or numerical evidence changed.

This review adds only its own directory. It does not edit main, revise the manuscript, remove adverse evidence, or overwrite earlier reviews.

## Contents and reproduction

`referee_report.md` contains six substantive findings, positive findings, evidentiary limits, and revision requirements. `diagnostic_summary.json` records the executed checks; `diagnostic_results.json.gz` contains every individual executed result. `review_manifest.json` pins inspected source blobs and review artifacts. `reviewer_checks.py` is an independent implementation, with no author-module imports.

From this directory, run:

```sh
python reviewer_checks.py --output diagnostic_results.json
```

The recorded environment is Python 3.13.5, NumPy 2.3.5, and SciPy 1.17.0. The script requires NumPy and SciPy, uses deterministic seed 20260917, and reports its own SHA-256. Numerical assertions should pass on compatible environments; exact floating-point bytes can vary with versions and numerical backends. The compressed record is the actual output from this review, not a promise of bitwise cross-platform reproducibility.

To read the deposited full output without running any optimizer:

```sh
python -c "import gzip,pathlib; pathlib.Path('recorded_results.json').write_bytes(gzip.decompress(pathlib.Path('diagnostic_results.json.gz').read_bytes()))"
```

The checks cover 60 dense finite models and 1,020 parameter-point solves, plus 27 two-stage primitive specifications with two risk classes each. The cardinal tilt changes an economic primitive; it is not a counterexample to the untilted proposition. The first-instant continuous-time observation is an analytical scope point, not a finite-calendar numerical failure. Storage fractions are illustrative accounting, not measured process memory.

## What was not rerun

No historical network training, full stopped-economy spatial refinement, author elapsed-time contest, or complete manuscript PDF rebuild/visual audit was performed. The manuscript assessment uses pinned TeX source. Prior spatial results and author timing results are explicitly attributed in the report. Numerical random-model checks support implementation consistency; they do not replace proofs. The inspected external primary literature and its limited scope are identified in the report.
