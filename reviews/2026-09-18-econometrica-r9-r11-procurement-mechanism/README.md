# NBO: procurement and reachable-mechanism advisory review

**Recommendation: reject in its present form.** This is an owner-commissioned Econometrica-style report, not an official journal report or decision.

The reviewed snapshot is `30548ad06852cc0a447dedf1e63cc9e7f79f6c06`. The latest named R11 branch still points to the preceding review; the latest complete scientific manuscript is R9 at `8c1e0472279fb66a2419b63b3e35df028ecfdd78`. No absent R10/R11 manuscript is treated as a completed revision.

## Reading order

Read [the referee report](referee_report.md), then [all executed paired cases](reviewer_results.csv), [diagnostics and source hashes](reviewer_diagnostics.json), [the executed audit source](reviewer_audit.py), [the final run log](execution.log), and [provenance and preservation](review_manifest.json).

The new evidence distinguishes an agent's position ranking from a service principal's ranking when sign-specific mandates and participation grants are available. It also identifies the all-action reachable preference support and checks directional adjustment there. All twelve contract cases and both additional directional cases are retained, including adverse surrender outcomes. These are finite-model point diagnostics, not a new regional certificate or a claim about unrestricted optimal contracts.

## Reproduce from a clean checkout

Use Python 3.13 with NumPy 2.3.5 and SciPy 1.17.0, the versions used in the recorded run. From the repository root:

```bash
python -m venv /tmp/nbo-procurement-review-env
. /tmp/nbo-procurement-review-env/bin/activate
python -m pip install numpy==2.3.5 scipy==1.17.0
python reviews/2026-09-18-econometrica-r9-r11-procurement-mechanism/reviewer_audit.py --output /tmp/nbo-procurement-review/reviewer_results.json
```

The command recomputes from scratch; there is no resume mode. It writes the full JSON, a CSV with the same stem, and `reviewer_diagnostics.json` in the output directory. The deposited CSV retains every class value, duration, surrender exposure, grant, and principal-at-b=1 comparison. The full generated JSON additionally contains selected initial actions, effort exposures, b=0.9 payoffs, and price-switch calculations; it is a regenerable expanded view, not a second independently executed experiment.

Compare numeric CSV fields with tolerance `2e-11`; contract identifiers and modes must match exactly. In diagnostics compare numeric results, source hashes, case counts, and parity checks; elapsed times and platform metadata need not match. The script independently replays every selected value function across all states and dates. Its own assertion threshold is `2e-11`.

The constructed kernels occupy 775,469,952 bytes; process memory is larger. That count is not a measured peak-memory result. The numerical loader does not require neural training. The script uses independently written Bellman and replay orchestration but reuses pinned author transition primitives and frozen proposal arrays. It does not independently enclose construction error, prove a continuum claim, or transfer a result to a diffusion.

## Preservation

Only this new review directory is added. No manuscript, scientific implementation, historical evidence, or earlier review is replaced. All 633 files in the downloaded source archive were compared byte for byte with their local counterparts after execution. The later reviewed snapshot adds fourteen earlier-review files to that archive; their preservation is provided by building the new commit on the full reviewed tree, not by claiming they were inside the earlier archive. The final GitHub diff must contain only this review directory.
