# R40 review object

The current object is `ECTA_R40.pdf`, with `SUPP_R40.pdf`, `RESPONSE_R40.pdf`, and `COMPUTATION_R40.pdf`.

Addressed report: `reviews/2026-09-25-econometrica-r38/referee_report.md`, review commit `acbede22e517a245fcc5244de7171c1ae218ea73`.

Frozen scientific base: R39 `bf5d42b08debd4c26341ab1b1231a6a6242df4f9`. R40 adds witness-driven global repair, portable model-error intervals, break-even randomization overhead, exact property tests, finer nonlinear independent replay, complete diagnostics, and compiled publication. Inherited experiments are explicitly not a new holdout.

All prior tracked files are retained unchanged except this current index; the previous index is preserved in `revisions/2026-09-25-r40/history/REVISION_INDEX_before_R40.md`. The full R38 main and technical supplement are also appended verbatim to the new supplement. `HISTORY_R38.pdf` remains unchanged.

See `revisions/2026-09-25-r40/results/publication_audit.json`, `replay_*.json`, and `PUBLICATION_MANIFEST.json` for object identity, fresh replay coverage, and preservation checks. These distinguish independent arithmetic from hash identity and structural validation.

Remaining numerical widths are retained: 30 positive-cost primary randomized intervals are not exact; the fine nonlinear bound is not near-exact; tight-tolerance nonlinear rows are lower-only; the separate stopped-control target is not certified at 0.01.
