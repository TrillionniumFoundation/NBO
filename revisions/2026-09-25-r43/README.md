# R43: regret-scaled controlled and atomic-fiber revision certificates

Current review documents: `ECTA_R43.pdf`, `SUPP_R43.pdf`, `RESPONSE_R43.pdf`, and `COMPUTATION_R43.pdf` at the repository root. The corresponding `.tex` wrappers point to `paper/`. The article retains the title **Certified Bellman Operators for Costly Policy Revision** and the unchanged Econometrica support class.

## Identity and scientific additions

Base: published R42 `7d54e728a9732979605697895e3a07444dc1e528`. Addressed report: `reviews/2026-09-25-econometrica-r40/referee_report.md` at `cf195a594c177208dbb5488576464dce9627a830`. New branch: `revision/econometrica-r43-regret-scaled-atomic-2026-09-25`.

The new main section on endogenous transitions proves the disadvantage/savings cone, a rare-departure repair bound, and an explicit quadratic small-allowance root-relaxation bound for fixed finite models with strict operating-action separation and discounting. McCormick envelopes themselves are classical. Operating ties, small action gaps, and high discount factors are not silently removed. Two exact-tie regression tests verify fallback to the ordinary sound relaxation; they are not counted as economic successes.

The new controlled atomic theorem disintegrates the full Borel common-policy optimum over observable covariates whose evolution is invertible and autonomous. Actions may change regime transition probabilities. A validated fiber-partition proposition gives fixed-allowance convergence without smearing atoms. An executed persistent-size maintenance economy supplies paired continuum intervals using 17 finite endpoint certificates and four exact sums. The original action-dependent continuous-condition maintenance model does not meet this structural assumption, and its 30 positive randomized intervals remain open.

## Executed and independently checked evidence

Eight controlled environments, two root relaxations: 16 objects. Four allowances in a fixed eight-period model, two relaxations: 8 objects. Seventeen controlled continuum fibers: 17 objects. All 41 objects are independently reconstructed, covering 6,648 original all-restart inequalities. All four weighted continuum sums and four mutations are checked. All LP caps and fallback intervals remain in the main table. `results/publication_metrics.json` contains the actual publication's numerical summary; `results/publication_rechecks.json` contains exact endpoints, object hashes, and coverage.

Initial source hashes and cases were registered at `18cbcfc41a4c35660be824f6984f68a1d38288a9`. A directed-arithmetic amendment was disclosed and frozen at `950b1f1ac2ebaf974d4ef528addd8b2c2e4ce72b`. The amendment avoids large distinct-denominator residual sums without changing any case or LP proposal specification. Initial code and partial numerical records are preserved under `history/initial_frozen/`. The experiment is **predeclared cases with a disclosed amendment**, not an untouched code-frozen holdout. `PROTOCOL.json` remains the original registration; the executable amended identity is `PROTOCOL_AMENDED.json`.

The 30-second cap concerns the LP proposal only. Construction, constructor arithmetic, independent checking, dimensions, bytes and cumulative high-water memory are reported separately. The comparator is a same-object root-relaxation ablation, not a comprehensive off-the-shelf global-solver contest. All economies are designed known-model examples, not calibrated or estimated data.

## Reproduce from repository root

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONINTMAXSTRDIGITS=0
python revisions/2026-09-25-r43/replication/run_suite.py
python revisions/2026-09-25-r43/replication/audit.py
python revisions/2026-09-25-r43/replication/unit_checks.py
python revisions/2026-09-25-r43/replication/assemble.py
for x in ECTA SUPP RESPONSE COMPUTATION; do
  latexmk -pdf -interaction=nonstopmode -halt-on-error "${x}_R43.tex"
done
python revisions/2026-09-25-r43/replication/publish.py
```

`resume.py` can replace `run_suite.py` after an interrupted session: it reuses only v2 objects that pass a fresh independent endpoint and hash check. The numerical source files are not changed by that driver. The standalone reader `verify_regret.py` and contract audit need only Python's standard library. Full proposal generation needs NumPy/SciPy; publication also needs LaTeX and PyMuPDF. Actual versions are saved in `results/environment.json`.

## Preservation and boundaries

The new branch retains every inherited scientific file unchanged. The current navigation index is archived before updating. R42's exogenous structural, nonzero density-transfer, undiscounted-repair, zero-tolerance, infinite-horizon-tail and historical results are not presented as new R43 executions. The finest nonlinear independent replay is inherited from R41 via R42, not rerun here. Analytic theorems, independent arithmetic, code identity, and publication integrity are separately labeled. Difficult approximate operating oracles, empirical calibration, tighter nonlinear feasible upper policies, the original controlled continuous-condition convergence problem, and matched marginal local-work ablations are not falsely marked completed.
