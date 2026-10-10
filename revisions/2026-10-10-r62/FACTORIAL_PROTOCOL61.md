# R61 native factorial amendment — 9 October 2026

The R60 eight-method experiment is retained unchanged. Inspection of its source shows that native exhaustive search uses the unreduced objective, whereas native finite-difference search first reduces activation regions. Their direct timing difference therefore combines representation reduction and the search algorithm. The present amendment separates those effects in fresh observations; no R60 clock is relabeled.

## Four matched implementations

All four cells use the unchanged `code/search60.cpp` arbitrary-size rational backend, compiled with the same `g++ -O3 -std=c++17` command without fast-math. They differ only in exact activation reduction (off/on) and native search mode (exhaustive/finite-difference). The original objective, rational action lattice, original objective value, and smallest-index tie rule are identical. Reduction and its exact offset are included in the corresponding method clock. The same original-objective rational postcheck is charged to every cell. Native process creation, serialization and response parsing are included. Reference exhaustive validation is separately recorded as experimental overhead.

The instance catalogue is exactly the 90 R60 rational fixtures: seeds 60103, 60209, 60317; widths 8, 32; lattice sizes 33, 129, 513; mixed, crossing, cancellation, adjacent-tie and flat regimes. This choice is made after the R60 results have been observed; it does not create additional learned-model draws. Every declared instance is retained.

Two freshly allocated hosted workers each execute all four methods on all 90 instances, in independently shuffled within-instance order. The order seeds are 61631 and 61632. The fixed repeated subset remains seed 60103, width 32, size 129, all five regimes; each worker executes seven additional shuffled repetitions. No instance or repetition is selected using the new timing outcomes.

## Batching

Each worker additionally evaluates the complete 90-instance catalogue with batch sizes 1, 8 and 32 for each of the four implementations. All input reduction, serialization, subprocesses, parsing and original-value checks are charged. The order of the four implementations is shuffled independently within each batch-size block. These are batches of heterogeneous fixed queries, not complete economic policy services or an additional training experiment. The existing R60 prospective services retain their own actual batching and complete-return clocks.

## Interpretation and audit

Every returned action and exact objective value is compared with Python Fraction exhaustive minimization; flat and adjacent-tie instances retain the smallest original minimizer. The output includes all raw per-query timings, repetition orders, exact answers, recorded operand-bit diagnostics, batch byte counts, compiler records, CPU affinity and host metadata. Processor frequency is not controlled; unavailable hardware counters are reported as unavailable. No significance level, universal crossover or cross-hardware speed claim is inferred from two hosted machines.

Within each worker, the reduced exhaustive versus reduced finite-difference comparison isolates the native search change at the same reduced representation. The corresponding unreduced pair and the two reduction contrasts complete the factorial. Microbenchmark gains do not substitute for complete prospective service gains, nor does a faster exact implementation imply a better policy than an equally certified conventional generator.

SOURCE_FREEZE61F.json binds this protocol and the new driver to the unchanged R60 scientific freeze before any R61 factorial production timing. Disjoint correctness fixtures may precede that freeze. All results are deposited on a new R61 evidence branch, leaving historical sources and observations unchanged. These measurements add implementation-work observations but no trained policy and no independent policy-cost path sample.
