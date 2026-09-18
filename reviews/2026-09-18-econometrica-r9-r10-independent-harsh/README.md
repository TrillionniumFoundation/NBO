# Independent harsh advisory review — 18 September 2026

**Recommendation: reject in present form.** This is an owner-commissioned Econometrica-style assessment, not an official journal appointment or editorial decision.

The reviewed snapshot is `10248e4a7e5d6668bf82de7d3b146f46bb10ad8f`. The latest named R10 full-response branch at inspection points to that preceding review commit; it contains no completed R10 scientific revision. The latest complete paper is R9 at `8c1e0472279fb66a2419b63b3e35df028ecfdd78`. This review does not relabel the inherited R9 manuscript as a new R10 paper.

## Reading order

[Referee report](referee_report.md) gives the editorial assessment, independent diagnostics, correct results that should be retained, four major concerns, and substantive reconsideration conditions. [Reviewer results](reviewer_results.json) contains every completed directional and joint-contract case, including selected actions, alternative-state witnesses, and validation results. [Reviewer audit](reviewer_audit.py) is the executed final source. [Manifest](review_manifest.json) records immutable source identities, hashes, provenance, and limits. [Execution logs](execution_logs.txt) retain the interrupted, resumed, and all-checkpoint validation segments.

## What is new

Nine contracts are reoptimized with all-date full, upward-only, downward-only, and zero-adjustment menus. At the commissioned initial state, upward-only values reproduce full-adjustment values and downward-only values reproduce no-adjustment values at all nine points. Alternative initial-state witnesses show that neither equality holds globally on the state grid.

Four fee/law/benefit combinations are reoptimized with voluntary surrender. For each regime and contract, three first-date long/short permission pairs are evaluated using the author's exact breakpoint implementation. The joint cases quantify how small permission changes erase the opposite-position comparison, including at the successful finite-fee implementation. The report does not call this a contradiction of the author's explicitly target-specific certificate.

## Reproduce from the repository root

Use a clean checkout of this review branch, including the repository's inherited replication sources and deposited arrays. The recorded environment was Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0 on Linux. The selected numerical loader avoids importing the neural-training runtime for this audit.

```bash
python -m venv /tmp/nbo-referee-env
. /tmp/nbo-referee-env/bin/activate
python -m pip install numpy==2.3.5 scipy==1.17.0
python reviews/2026-09-18-econometrica-r9-r10-independent-harsh/reviewer_audit.py
```

Run **without `--resume` for an independent full recomputation**. The script writes `reviewer_results.json` in its own review directory. Save the deposited result elsewhere before running to compare it afterwards. Output formatting changes from compact JSON in the deposit to indented JSON; compare parsed numbers, not whitespace. Timing, platform metadata, and the count of pre-existing files can differ because the executed source archive predates the previous review package. Numeric replay tolerance is `2e-11`.

The optional `--resume` switch is only for continuing checkpoints from the same unchanged source and target in a time-limited environment. Do not use the deposited checkpoints with `--resume` as a substitute for reproducing all experiments. Resumed execution revalidates all four completed joint baselines and the focal production/selected-control comparisons, but it does not independently recompute every directional or permission checkpoint. The preserved logs describe exactly how the original evidence was completed.

The constructed kernels alone occupy approximately 775 MB; total process memory is larger and was not measured here. This is a finite-array audit, not a neural-training benchmark. No peak-memory or end-to-end runtime claim is attached to the final resumed segment's elapsed time.

## Limits and preservation

The Bellman orchestration and directional restrictions are independent; reward/transition construction, surrender moments, and first-date permission search use pinned author components. The nine points are not a continuum certificate. Replay agreement does not enclose a real-arithmetic constructor or transfer a sign to a diffusion. Complete historical training, timing frontiers, and the full regional chord/count sweep were not rerun.

The new branch adds only this review directory. No manuscript, scientific implementation, earlier result, or prior review is changed. The 633-file preservation check concerns pre-existing non-cache inputs in the downloaded source archive, not an assertion that the later repository contains exactly 633 files.
