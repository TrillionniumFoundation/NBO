# R22 execution provenance and publication recovery

The reference scientific execution is GitHub Actions run **35813098721**, using scientific source commit **9527f219df4fe82d3e9d81fc9ab3ac968613437b** and workflow commit **78490dbec7f4d89d25d92df86512d49fdb88ce37**. Every scientific step completed successfully: 48 crossed configurations, active stress/recovery checks, general-initialization range and pair-moment certificates, the full-state MPFR audit, proof constants, and cost accounting. All three PDFs compiled in that run (71, 40, and 5 pages), without unresolved references or overfull boxes.

The first publication was blocked by the strict historical-file preservation assertion. Importing the old audit module regenerated one already tracked bytecode file: `revisions/2026-09-23-r21/replication/__pycache__/audit.cpython-313.pyc`. No historical scientific source or numerical result was changed. The failed publication and its logs are retained, not relabeled as a successful full workflow.

The immutable diagnostics artifact is **10730632886**, SHA-256 **0893e5c3fc285019fd37774b4b1474c1fcc318adc2df7dc331439a56bbe6a6d7**. The publication-recovery workflow retrieves that exact artifact, verifies its digest and all 21 scientific source-file hashes, and rebuilds from the frozen results in a clean checkout with `PYTHONDONTWRITEBYTECODE=1`. It rechecks execution invariants and preserves every scientific result byte-for-byte; only document-build metadata and logs are regenerated. The original experiment is not rerun, reselected, or assigned a new scientific run ID. The original full workflow has also been corrected to prevent bytecode mutation and propagate pipeline failures.

## Reference versus local preflight

The manuscript tables and macros use the remote reference execution, not the earlier local preflight. Reference stress acceptance is **4 accepted / 4 rejected**, with exact network/optimizer/RNG restoration after rejection; local preflight was 3/5. Reference recovery is **6 accepted / 2 rejected**, with acceptance after the first rejection. The reference full-state bound is **7.241462443133421** at time zero and **7.241462443133396** under the directed all-starting-time suffix calculation; the local preflight had 7.240503256506336. These differences are recorded rather than presented as bitwise cross-platform replication. The exact initialization-match invariants, gradient budgets, positive three-ensemble conditional Adam comparisons, and the stronger direct L-BFGS-B baseline hold in the reference run. The frozen local financing-failure fixture is explicitly separate from the reference results.

## Local replay environment

Before the commands in `REPRODUCE.md`, set:

```sh
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONHASHSEED=0
```

For a fresh training replay, retain the published results as an archive before generating a distinct new execution; do not silently mix old configurations with newly run ones. For publication-only reproduction, use the frozen committed results. Numerical enclosure validity and execution invariants are the checks; identical floating-point optimizer trajectories on different platforms are not asserted. The original all-domain 0.01 target remains unmet.
