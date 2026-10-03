# Neural Bellman Operators — R10

This revision continues the original NBO paper and responds to the 3 October 2026 R8 advisory report at `3fb6d5bd5cac245a7f693f0b8db76a5075b1c732`. Its base is the complete R9 evidence commit `f8215d6df9026afa108a03c2823cbd6e054a9de8`. The report is owner-commissioned and is not an Econometric Society editorial decision.

The evidence/referee branches contain the integrated root `ECTA.tex` and `supp.tex`, compiled with the inherited Econometrica class, plus `response.tex` in this directory. Exact prior roots and a complete prior-file hash manifest are retained in `archive/`. Previous sections, labels, applications, raw results, adverse evidence and branches are not deleted or overwritten.

## New contribution

A curvature-controlled continuous-time regret theorem for the original dense nonlinear capital economy bounds arbitrary adapted deviations in the full primitive action box. A schedule-centred actor inherits a uniform policy guarantee without requiring a sampled residual to stand for a global certificate. An inward scalar interval guard enforces the output tube without action maximization. Positive interval LDL pivots verify the coupling norm; outward scalar quadrature computes the bound. The original ten- and twenty-dimensional economies are unchanged; dimension fifty extends their same coupling rule.

The program executes 27 generic multilayer fits: actor, direct-tube HJB and direct-full HJB, in dimensions 10, 20 and 50, with seeds 11, 29 and 47. The feasible schedule is an additional untrained comparator. Every fit uses 600 critic updates, batch 128, and two independent two-probe trace banks. State draws and critic budgets are matched; unequal wall time is not called an equal-time design. 512 common Brownian paths at 40, 80 and 160 steps produce diagnostic paired payoffs. All increments, payoffs, weights, histories, failures, memory and query counts are committed.

The 54 arithmetic records cover three dimensions, three initial-dispersion bounds, three tube radii and two quadrature levels. The theorem concerns the continuous economy, all initial means, and every initial state satisfying the stated dispersion bound. The actor tube restricts the approximation class, not the optimal comparison class. The feasible schedule has a tighter structural bound and no training cost. The structural guarantee holds before training; it is not proof of actor superiority, optimizer convergence, or continuous-state/time transfer for the preference economy.

## Reproduction

From repository root, using Python 3.13.5, PyTorch 2.10.0 CPU, NumPy 2.3.5, SciPy 1.17.0 and mpmath 1.3.0, with OMP/MKL/OpenBLAS threads set to one:

```sh
python -u revisions/2026-10-04-r10/code/replicate.py
python revisions/2026-10-04-r10/code/build.py
```

`SOURCE_MANIFEST.json`, `results/EXECUTION.json`, `TABLE_MANIFEST.json`, `EVIDENCE_MANIFEST.json` and `REMOTE_EXECUTION.json` bind source, logs, results, tables and compiled PDFs. Research failures and failed commands remain visible; build success is not economic superiority or referee acceptance. On the evidence branch, the historical inputs already exist and `archive/` is the exact integration base. Reproduction starts by restoring the two root files from that archive when rerunning in a clean temporary worktree.

Interval statements are conditional on the inherited arithmetic contract, not formal verification of the machine. Monte Carlo intervals exclude Euler bias and are not used to tighten the continuous bound. The reported flow-consumption compensation is explicitly externally financed with the state law, adjustment cost and terminal payoff held fixed.
