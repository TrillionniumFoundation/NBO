# R18 execution protocol

R18 is a manuscript revision and a new independent objective/evidence audit of the immutable R17 science. All R17 training, ablation, nonlinear-inventory, baseline, and compensation protocols/results retain their original provenance. This protocol does not retrospectively preregister those experiments or introduce favorable seed selection.

## Fixed audit population

Read the R17 `SCIENTIFIC_REPRODUCTION.json` and require every one of its 589 SHA-256 entries to match. Audit the Cartesian product of architectures `accessible/allface`, seeds `17100:17109`, and checkpoints `0,100,400`: exactly 60 objects with exactly 1,024 state/time cells each. Re-evaluate the implemented binary64 proposal logits, save those logits, and enclose their soft maximum by directed MPFR arithmetic with exact temperature `3/20`. The discrepancy uses the one-sided endpoint correction stated in the theorem. No checkpoint is removed because the correction or original regret is large.

Replay the full 1,024-cell MPFR certificate of seed 17100, checkpoint 400, for both architectures. Separately recheck every final nonlinear neural query plan at dimensions 8/32/128, seeds 17400/17401/17402, and the declared alternating/uniform query vectors: exactly 18 plans. The two-query plan checks do not replace the analytical cube-uniform theorem.

Audit all six unrestricted classical policy tensors and all twenty fresh price-library actors. For the classical policies, use original-action-clipped exact-real bilinear interpolation and verify zero portfolio on the upper-wealth column. For the library, enumerate every actor and time slab; the full-price selector returns only members of this enumerated set.

## New mathematical regression tests

Use 450 exact-rational tests of the inherited MPFR arithmetic core and 80 exact-rational finite-horizon MDP cases with three states, two actions, horizons 1/2/4/8, and fixed random seed 1823. Check the finite-horizon defect inequality exactly as rational numbers. Compare analytical and automatic gradients at a fixed nonlinear-planner example and record Hessian eigenvalues only as diagnostics. The global Hessian and contraction results are proved analytically in the manuscript.

## Software and publication

The canonical CI environment uses Python 3.11, NumPy 2.3.5, SciPy 1.17.0, and PyTorch 2.10.0 (CPU). MPFR and the C compiler are system packages; the manifest records their actual versions. Set OMP and BLAS thread counts to one. The preceding local audit used Python 3.13.5 with the same NumPy/SciPy/PyTorch versions and MPFR 4.2.2; its record is labeled local, not silently substituted for CI.

The build uses the existing repository `econsocart.cls` with its `ecta` option. Compile main, supplement, and response in that order, three passes each. Reject failed compilation, unresolved references/citations, multiply-defined labels, or overfull boxes. Record page counts, sizes, and hashes. Visual inspection complements but does not replace those tests.

The source is committed before execution. The final publication commit contains the actual executed results, logs, PDFs, and publication manifest. Only new R18 paths and new R18 workflows may differ from the pinned R17 base. Existing review/revision branches and the main branch are not moved. The referee-copy branch is pinned to the same final publication commit.
