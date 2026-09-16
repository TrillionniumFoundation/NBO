# R7 economic-target audit — 17 September 2026

Read the [referee report](referee_report.md) first. Recommendation: **reject in the present form for Econometrica**. This is an owner-commissioned advisory review, not an actual journal appointment or decision.

## Version identity

The reviewed paper is R7 at `fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17`, tree `cdc8e227881d5e95a8740c4f77298f73a0b9399d`. Live branch checks before the review and before branch creation showed that the R8-named branches contain review additions, not a new manuscript. This branch starts at the most inclusive historical-review head, `bfba0168a58b35507e37183147ecd2249de65a7c`, and adds only this review directory. It does not alter main, revision manuscripts, numerical source, or previous reports.

## What is new

The preceding directional review recomputed the no-adjustment arm. This audit computes **both adjustment regimes**, both first-risk classes, three wealth grids, five parameter points, and two menu treatments: 120 class values with direct selected-policy replays. At the vulnerable corner, wealth refinement changes opposite risk rankings into positive rankings in both regimes. The relative adjustment option remains positive at every inspected point. The report distinguishes these conclusions and does not claim a refined-grid regional or limiting-diffusion certificate.

`common` retains the exact union of both published action meshes. `prolonged_full` adds the three stored frozen proposals, copying original-node controls exactly and bilinearly interpolating controls at new nodes. The latter is an explicitly reviewer-defined extension. Interpolated proposals can slightly enlarge the no-adjustment menu at new nodes; no equivalence of these menu treatments is presumed.

## Files and evidence classes

| File | Role |
|---|---|
| `referee_report.md` | Editorial assessment, five major findings, numerical tables, required responses, and pinned sources |
| `diagnostic_results.json` | All 120 class values in 30 rows, replay discrepancies, six corner feature decompositions, author-check reruns, and identities |
| `reviewer_spatial_both_regimes.py` | Reviewer-written Bellman driver and direct policy replay, using the author's transition construction |
| `reviewer_core_checks.py` | Non-mutating wrapper around the author's small-model, primitive-family, and coefficient-replay routines |
| `review_manifest.json` | Source, artifact, PDF, execution, and scope metadata |

The JSON `point_columns` defines the positional schema of every `point_rows` entry. The four class-value columns are retained, rather than only their differences. An absent original-author error means that no corresponding original full-menu corner comparison applies, not that a zero error was observed. Grid runtimes are reproduction metadata, not benchmarks against author runtimes.

## Reproduce

Use a checkout of this review branch, which retains the pinned R7 source and evidence. An existing suitable environment needs NumPy, SciPy, and PyTorch; this run used Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, and PyTorch 2.10.0+cpu. The author's `replication/r7/requirements.txt` records its dependency versions. No training, GPU, or journal-build tool is required for these checks. The spatial program retains sparse kernels in memory, so allow several GB of available memory. Do not run with Python's `-O` option: assertions are part of the checks.

From the repository root:

```bash
REVIEW=reviews/2026-09-17-econometrica-r7-economic-target
OUT=$(mktemp -d)
export OUT
python "$REVIEW/reviewer_core_checks.py" --root "$PWD" --output "$OUT/core_results.json"
python "$REVIEW/reviewer_spatial_both_regimes.py" --root "$PWD" --output "$OUT/spatial_results.json"
```

The wrappers do not overwrite deposited author results. The spatial output includes additional per-class feature values and per-solve timings; the deposited diagnostic file is a compact projection retaining all 120 class values and the report's feature comparisons. A quick corner-only run is available with `--corner-only`, but it does not reproduce the complete five-point experiment.

After a complete run, compare all class values against the deposited records:

```bash
python - <<'PY'
import json, os
from pathlib import Path
review = Path('reviews/2026-09-17-econometrica-r7-economic-target')
expected = json.loads((review / 'diagnostic_results.json').read_text())
actual = json.loads((Path(os.environ['OUT']) / 'spatial_results.json').read_text())
assert len(actual['rows']) == 30
by_key = {(tuple(r['shape']), r['lambda'], r['d'], r['arm']): r for r in actual['rows']}
maximum = 0.0
for packed in expected['point_rows']:
    e = dict(zip(expected['point_columns'], packed))
    r = by_key[((e['u_nodes'], e['wealth_nodes']), e['lambda'], e['d'], e['arm'])]
    for regime in ('fixed', 'adjusted'):
        for sign in ('positive', 'nonpositive'):
            observed = r['regimes'][regime]['classes'][sign]['value']
            maximum = max(maximum, abs(observed - e[f'{regime}_{sign}_value']))
        assert r['regimes'][regime]['replay_max_error'] < 5e-11
assert maximum < 5e-11
print('All 120 class values agree; largest difference:', maximum)
core = json.loads((Path(os.environ['OUT']) / 'core_results.json').read_text())
assert all(core['authored_source_inventory_matches'].values())
assert core['author_check_reruns']['validation.json']['parameter_checks'] == 480
assert core['author_check_reruns']['decision_replay.json']['maximum_difference'] == 0
print('Source identities, 480 author parameter checks, and coefficient replay pass.')
PY
```

A successful run validates the stated finite-model computations and their recorded comparisons. It does not convert pointwise tests into a theorem about a parameter region or a continuous-state/continuous-time limit.

## Audit boundaries and development disclosure

The original 27 authored-source hashes and reconstructed Git tree match the manuscript. The original-grid full-menu corner values match the author's deposited values within `2.220446049250313e-16`. The maximum reviewer policy-replay discrepancy is `1.3322676295501878e-15`. Historical neural training, the complete author timing frontier, temporal refinement, and the earlier moment experiment were not rerun; they are explicitly attributed in the report.

During construction of the reviewer tools, two reviewer-side defects were caught and fixed before the recorded successful runs: sparse-matrix canonicalization originally aliased a kernel-weight buffer, and an ambiguous import resolved a historical validation module rather than R7's module. The deposited programs respectively copy sparse data and load the R7 validation file explicitly. Neither issue is alleged to be a manuscript defect. The successful executed script hashes are recorded in the manifest.

All historical reports and author evidence remain preserved. The review is a new assessment of R7; it is not a fabricated author response or an additional manuscript revision.
