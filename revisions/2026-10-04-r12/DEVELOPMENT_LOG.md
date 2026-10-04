# Development provenance

All records in this document precede the final clean study. No failed development output is replaced by a selected favorable final outcome. Development noise seed 82412000 is distinct from final seed 92412000. The source and protocol are fixed after development and before final fitting; this is not a historically preregistered study.

## First smoke: scalar domain

Workflow 37164409404 used source f415c7824a47550c6a14722857a1aa53b289a803. All 14 initial unit tests passed. The smoke incorrectly called the inherited multidimensional interval account at d=1: outward evaluation of 1-1/d produced a slightly negative lower endpoint before its square root. Six development evaluations failed before simulation. Artifact 11288482893 preserves the logs and development weights. The primary certificate design is d=10,20,50; its smoke now uses d=10 and explicitly rejects a scalar call. The independent one-state nonlinear HJB reference does not use this multidimensional account. Historical arithmetic kernels are unchanged.

## Second smoke: deployment-timing batch

Workflow 37164710910 used source e335dd0c04aab3dbac30f6f7afc0b96805ca13ac. The 14 unit tests again passed. Simulation with 64 development paths completed, but the timing-only batch incorrectly concatenated 256 clocks with 64 states. Artifact 11289575627 preserves all six errors and raw development arrays. A dedicated benchmark_batch function now repeats only timing inputs when fewer than 256 development paths exist. It does not alter simulation paths or statistics. New tests cover short/empty timing batches, explicit scalar-domain rejection, interval population averaging and interval fee conversion.

## Statistical and editorial preparation

Population deterministic bounds are averaged using interval arithmetic, not a single rounding step after an ordinary sum. Management-fee transformations likewise use interval logarithms and exponentials. Direct contrast clipping and transfer allowances are formed by interval sums. The article retains the original topic and full historical applications. Old roots and the obsolete README are archived exactly; the R11 learning and empirical sections are relocated intact to the supplement. Final tables are regenerated from final raw arrays. Development tables are clearly marked and never used as final empirical evidence.
