# R34: all-restart bounds for costly policy revision

Read `R34_REVIEW.md` at the repository root, followed by the article `ECTA_R34.pdf`. Companions are `SUPP_R34.pdf`, `RESPONSE_R34.pdf`, `COMPUTATION_R34.pdf`, and the lossless `HISTORY_R34.pdf`.

This revision is based on frozen parent `88015b77a0c26e7b883156410b684b229fd7e86f`, which contains the executed R32 package and staged R33 source archive. The latest available review is R30 at `e9bc144fbb6843d6a3436825a28584efb64fb8f1`. The revision branch is `revision/econometrica-r34-verified-policy-frontier-2026-09-24`; no preceding branch is modified.

## Mathematical and computational additions

Construct two-sided operating witnesses from checked Bellman defects and unrestricted scalarized support values. These bound intervention cost for every operating-feasible policy, not only a conservative action class. The new R34 backward propagation transmits future mandatory intervention costs and enforces a necessary current operating inequality with nonnegative local multipliers. It retains all actions, covers randomized Markov policies, and states precisely the feasible-history extension. Every constructed bound is a finite rational piecewise-affine object with separate isolated-point values and independently checked min/max proof selectors.

The unchanged coupled maintenance experiment contains 42 configurations. All deployed policies meet their uniform operating targets and preserve installed returns. All 18 installed-neural cases cost less than the freshly reconstructed class minimum. The new propagation tightens 22 global lower bounds and leaves 20 unchanged, with no additional unrestricted support solve. Twelve spline cases retain exact zero cost and global gap; no previously positive gap closes. The largest absolute bound increase is about .261684. No neural-specific speed advantage is inferred from these cost comparisons.

A fresh optimizer-disabled audit checks all 294 certificates: 168 support problems, 42 class controls, 42 primal-dual summaries, and 42 propagated bounds. Corruption tests require 28 malformed objects to fail. Finite-tree tests include 108 deterministic and 1,512 equal-mixture state-plan combinations, with all conditionally feasible cases checked. Remote publication must reproduce all 294 canonical certificate SHA-256 values in `EXPECTED_EXACT.json`.

## Reproduction

From the repository root, using Python without `-O`:

```sh
R=revisions/2026-09-24-r34
python "$R/run_study.py"
python "$R/run_closure.py"
python "$R/replication/report_global.py" "$R"
python "$R/replication/report_restart.py" "$R"
python revisions/2026-09-24-r32/replication/boundary.py --output "$R/results/boundary_recheck.json"
python "$R/assemble.py"
bash "$R/build.sh"
python "$R/publication.py"
```

The new computations require only Python's standard library and frozen R32 incumbent files. They do not retrain neural or spline proposals. The builds use the repository's unchanged Econometric Society class. Every construction, own-policy evaluation, failed-feasibility support candidate, serialization step, and audit is charged and recorded. Performance figures are new-machine descriptive measurements, not combinations of incompatible old and new timings.

## Preservation and scope

`PROTOCOL.md` was committed before the R34 propagation was implemented or evaluated; the preceding support outcomes were already known. `IMPLEMENTATION_NOTES.md` distinguishes the executed R32 record, staged R33 sources, and actual new R34 executions. An unavailable old R33 attempt is not reconstructed or asserted as evidence.

The entire R32 main/supplement text is retained after documented input-path changes. All five preceding PDFs, including their earlier historical annex, are included unchanged in the 305-page historical annex. The original stopped-economy all-domain .01 target, retained bound 7.181834580823298, and complete constant-control boundary proof remain explicit. R34 reruns the scalar proof's rational inequalities, not the inherited endpoint quadrature. Full stopped-feedback certification, neural-specific acceleration, high-dimensional performance, and deployment-query amortization are not claimed from this maintenance experiment.
