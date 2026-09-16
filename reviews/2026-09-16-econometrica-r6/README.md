# R6 advisory review

Start with [referee_report.md](referee_report.md). This is an external-style, owner-commissioned assessment, not a journal appointment or editorial decision.

The report reviews the complete R6 revision at `24011fef6da09bc05dc79946a3c1779e1fe7d8a8` and recommends rejection in the present form for Econometrica. Its principal new finding is a proved coefficient ordering: the paper's count-information upper recursion, localized to the same anchor interval, weakly dominates the corrected-chord coefficients. A matched computation verifies smaller uniform coefficient certificates on all three deposited contracts without changing the original policy bank or target.

The independent small-model implementation is `reviewer_diagnostics.py`, with results in `diagnostic_results.json`. The full-model matched implementation is `matched_local_count.py`, with all 51 interval records in `matched_local_count_results.json`. It imports the author's kernel executor and reuses the deposited lower coefficients; it is not an independent reconstruction of the entire economy. `author_unit_replay.json` separately records a rerun of the submitted small-model suite. `review_manifest.json` records source identity and file hashes.

Reproduction commands and the complete coefficient-ordering proof are in the report. Timings in the matched diagnostic do not constitute a speed comparison, and the report does not allege that Theorem 10 is false. No author manuscript, historical evidence, or main-branch file is changed by this review.
