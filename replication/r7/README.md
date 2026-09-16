# R7 replication: comparative oracles and certified economic choices

From the repository root, with Python 3.13, NumPy 2.3.5, SciPy 1.17.0 and CPU PyTorch 2.10.0:

```bash
bash replication/r7/run_all.sh "$(git rev-parse HEAD)"
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r7 ECTA_R7.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r7 SUPP_R7.tex
python replication/r7/build_report.py --source-commit "$(git rev-parse HEAD)"
```

The driver writes only R7 output/log directories and generated R7 tables. Historical arrays, neural checkpoints, source and evidence are read-only. Peak memory for the full two-kernel target is approximately several GiB; the scripts execute in separate processes to release kernel storage between experiments. They do not require a GPU.

## Executed components

`validate.py` compares production count/chord code with independently written dense recursions on 96 finite MDPs, checks 480 parameter values, measures kernel-call counts through horizon 16, tests the total coefficient-error bound, and reproduces a strict count/chord example. These tests support implementations; the manuscript proofs establish general statements.

`primitive.py` evaluates the two-stage CRRA sufficient condition, proves its continuous-family conclusion using analytic extrema, and solves nine illustrative strictly concave adjustment problems. It does not replace or calibrate the original stopped model.

`decision.py` computes four risk/adjustment class values on the original full finite target, uses corner policies and localized count upper coefficients to certify the entire rectangle `lambda in [0,.25], d in [.4,.45]` at `(u,X)=(2,1.25)`, and deposits all policy and tensor coefficient arrays. Its arithmetic allowance is relative to the stored finite arrays under round-to-nearest arithmetic, not a diffusion or directed-rounding claim. Both class-value construction error and the separate numerical allowance enter the reported signs.

`matched.py` independently reoptimizes all original transition anchors and replays all 51 original intervals using the same feasible policies/cells for compressed, count, and rectangular upper methods. It adds two coarser common-bank rows. Setup, anchors, lower evaluation, local restriction, upper construction and certification all enter each total. Timings are one full serial single-thread pass per row, with common work measured once and charged identically. The code exposes each stage rather than equating kernel counts with time.

`adaptive.py` runs three autonomous dyadic procedures on the full `d=.5` target from empty per-arm caches: chord, count, and cascade. All rejected intervals, new anchors and evaluations are charged; the same tolerance and split/policy/cell rules apply. The cascade's anchors must be contained in the chord-only tree.

`render_tables.py` generates manuscript tables and the execution summary from JSON. `build_report.py` verifies source hashes, protected historical bytes, output presence, figure/reference consistency and successful compilation, then deposits PDFs and logs. Source execution, file identity, mathematical claims, finite-model evidence and editorial judgment are distinct.

## Data and scope

The inherited R4 safe-policy checkpoints are frozen neural proposals. R5 supplies the full action-union economy, R6 supplies unchanged kernel execution and policy-polynomial routines, and R7 supplies matched upper implementations, class constraints and new tests. No new full neural-training sweep, QP retiming, diffusion refinement, or global threshold uniqueness claim is included in R7 execution. The corresponding historical evidence remains in the manuscript and repository with its original attribution.

Every compared finite model uses the same 1,617 states, eight dates, and 1,568-action target before the explicit class/adjustment restrictions. `lambda` is the iid per-date probability of one of two fixed one-step laws, and is common across dates. It is not interpolation of Brownian correlation. The no-adjustment counterfactual retains preference shocks and imposes zero deliberate adjustment at all states and dates.

The source commit is written to `output/environment.json`; SHA-256 inventory checking precedes execution. All tensor coefficient bounds can be replayed without solving an MDP:

```bash
python -c "import sys;sys.path.insert(0,'replication/r7');from validate import replay_decision;replay_decision()"
```
