# R7 directional audit: report and reproducible evidence

This is an owner-commissioned Econometrica-style advisory review, not a journal appointment or editorial decision.

Read [the referee report](referee_report.md) first. The recommendation is **reject in the present form**. The report credits the repaired finite-model results and identifies a new, fixed-calendar **wealth-only** sign change in the no-adjustment risk comparison. This is not a counterexample to the original finite-array tensor certificate and not a proof of the limiting diffusion's sign.

## Version identity

Reviewed manuscript: `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17` (`revision/econometrica-r7-2026-09-16`). Its reconstructed tree is `cdc8e227881d5e95a8740c4f77298f73a0b9399d`.

Review branch: `review/econometrica-r7-directional-audit-2026-09-16-fbfbf90`, based on historical-review commit `a5e4c20458947ddffee9cdbb0e0af5ca792d2979`. The new directory adds review material only. The manuscript and both preceding R7 reports are preserved. At inspection the two R8-named branches contained review additions, not an R8 manuscript; the report does not invent a new author response.

## Contents

- `referee_report.md`: English report, five numbered substantive findings, explicit source locators, credited repairs, and response requirements.
- `reviewer_directional_refinement.py`: exact admissible-proposal duplicate audit, seven grids, five parameter points, both first-risk classes, and selected-policy replay.
- `reviewer_replay_and_moments.py`: rerun author validation/primitive/tensor checks and independently verify thirty interior covariance identities.
- `diagnostic_results.json`: all 70 directional class values, all thirty moment cases, replay maxima, and author-check results in compact tabular form. Column meanings are included.
- `review_manifest.json`: immutable source/evidence identities, local environment, scope, and SHA-256/Git blob hashes of these deliverables.

## Reproduction

Use a checkout of the reviewed source or this review branch; the relevant author source and arrays are unchanged. Python, NumPy, and SciPy are required. The executed environment is recorded in the manifest. Both scripts set numerical-library threads to one. They reuse the author's transition construction; neither is an independent diffusion solver.

From the repository root, run:

```bash
REVIEW=reviews/2026-09-16-econometrica-r7-directional
OUT=$(mktemp -d)
python "$REVIEW/reviewer_directional_refinement.py" \
  --root "$PWD" --output "$OUT/directional_results.json"
python "$REVIEW/reviewer_replay_and_moments.py" \
  --root "$PWD" --out "$OUT/replay"
printf 'Raw reviewer output: %s\n' "$OUT"
```

Keep `OUT` separate from author output directories. The replay script temporarily copies the original coefficient inputs into its output directory and removes those copies after replay. It does not regenerate historical author evidence. Raw outputs are more verbose than the committed compact diagnostic, but contain the same values. Runtimes depend on the machine and are not author/reviewer speed comparisons. Numerical tolerances, rather than byte identity of floating results or elapsed times, should be used across environments.

The no-adjustment reduction is exact on the original full target: all admissible frozen proposals are exact duplicates of the 185 common zero-adjustment controls. The full union of both historical common meshes is retained before filtering. Calling the author's `include_neural=False` constructor by itself would not preserve this union.

The study does not retrain networks, rerun the author's complete timing contest, recompute the adjusted regime on new grids, or certify an entire refined-grid parameter region. The original tensor coefficients replay exactly; the new numerical objection concerns spatial robustness and the economic target.
