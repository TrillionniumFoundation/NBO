# Latest-revision advisory review: R9 science / R10 workspace

**18 September 2026. Recommendation: Reject in its present form.**

Read [the referee report](referee_report.md) first. This is an owner-commissioned Econometrica-style advisory review, not a journal appointment or editorial decision.

## Reviewed candidate

The latest named revision branch is `revision/econometrica-r10-dynamic-mechanism-2026-09-17`, at `755b507870b54a100616b0658eba9a031eef2833`. It adds a workflow, not a new manuscript. The latest complete scientific revision remains R9 at `8c1e0472279fb66a2419b63b3e35df028ecfdd78`. The report distinguishes these two identities. Both were rechecked before deposition. No manuscript, historical review, numerical source, existing branch, or workflow is modified by this review package.

The report addresses the dynamic adjustment mechanism, the comparison of priced financial enforcement with a compulsory term, active versus inactive surrender, and the integrated computational/economic contribution. It expressly credits valid R9 repairs and favorable results.

## Executed evidence

[Reviewer results](reviewer_results.json) contain the full result object from the successful execution, losslessly reformatted as compact JSON. [Reviewer checks](reviewer_checks.py) are the exact executed script. [Checkpoints](reviewer_checkpoints.json) record progress of that completed run. [The manifest](review_manifest.json) pins the source, environment, report blob, and evidence hashes.

The numerical audit uses the author's pinned constructor and independent Bellman orchestration. It is not an independently rounded constructor, a continuous-control solution, a diffusion experiment, or neural training. Its all-date directional comparison is focal at `(lambda,d)=(0.125,0.425)`, not a regional direction certificate. It also reoptimizes surrender cases and an adverse corner, reconstructs the reachable enforcement bank, checks the all-action stopping supersolution, and recomputes procurement.

An earlier larger exploratory run was interrupted. Its [partial log](exploratory_interrupted_run.log) is preserved, but it is not counted as a completed multi-point experiment. The completed output is the center-only directional audit plus the other explicitly recorded checks.

## Reproduce without altering the inputs

From a clone containing this review branch, use a separate detached worktree for the exact reviewed input. Choose unused worktree and environment paths:

```bash
set -euo pipefail
REVIEW_DIR="$PWD/reviews/2026-09-18-econometrica-latest-r9-r10-audit"
INPUT_DIR="$(mktemp -d)/NBO-input"
OUT_DIR="$(mktemp -d)"
git worktree add --detach "$INPUT_DIR" 755b507870b54a100616b0658eba9a031eef2833
python3 -m venv "$OUT_DIR/venv"
"$OUT_DIR/venv/bin/python" -m pip install -r "$REVIEW_DIR/requirements.txt"
PYTHONDONTWRITEBYTECODE=1 "$OUT_DIR/venv/bin/python" "$REVIEW_DIR/reviewer_checks.py" \
  --repo "$INPUT_DIR" --out "$OUT_DIR/reviewer_results.json" \
  | tee "$OUT_DIR/reviewer_run.log"
"$OUT_DIR/venv/bin/python" -m json.tool "$OUT_DIR/reviewer_results.json" >/dev/null
printf 'Results: %s\n' "$OUT_DIR/reviewer_results.json"
```

Use the pinned source above, not a later scientific revision with the same file names. The result records relevant source hashes and asserts that all pre-existing input files remain unchanged. The recorded input count was 633 for the archived snapshot; metadata or added files can change the count in other checkouts. The finite constructor stores 775,469,952 bytes of kernels; this is not a measurement of process peak memory. Allow additional memory for arrays and temporary products.

The executed environment was Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0. Numerical assertions use a `2e-11` tolerance; timing and last-bit differences are not an acceptance criterion. The completed execution was advanced through generator checkpoints in a persistent Python session. Its elapsed wall time includes checkpoint pauses and is not a benchmark against the author's timing results.
