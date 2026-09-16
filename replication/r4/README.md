# Neural Bellman Operators — R4 replication

Run from the repository root. The paper is `ECTA_R4.tex`; the independent supplement is `SUPP_R4.tex`. This directory does not import R3 routines, historical arrays, or referee diagnostics into training. Historical records remain unchanged elsewhere in the repository.

## Environment and complete run

Python 3.13, NumPy 2.3.5, SciPy 1.17.0, PyTorch 2.10.0 (CPU), float64. The source sets PyTorch to one thread; the runner fixes BLAS thread counts. Install the CPU PyTorch wheel separately to avoid unnecessary GPU dependencies:

```sh
python -m pip install numpy==2.3.5 scipy==1.17.0
python -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu
bash replication/r4/run_all.sh "$(git rev-parse HEAD)"
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r4 ECTA_R4.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r4 SUPP_R4.tex
```

LaTeX needs the inherited `econsocart.cls` and configuration, plus standard LaTeX-extra, recommended fonts, science, and latexmk packages. Bibliography entries are explicit author–year references; no external bibliography service or generated historical data is required.

For weight replay without retraining:

```sh
python replication/r4/replay.py
```

Individual commands and order are in `run_all.sh`. A failed command terminates that script; its log remains available. The local development pilot and the smaller-budget unsafeguarded network are not discarded or described as a matched ablation.

## Executed objects

`solver.py` implements the stopped stochastic preference economy twice: a NumPy positive-interpolation reference and a differentiable PyTorch finite-transition operator. It retains all variances and the cross covariance, settles first line exits, and settles boundary starts immediately. It never clips an exiting wealth path back to live interior continuation. Control order is **consumption, preference adjustment, portfolio share**. The signs are weak-Euler quadrature, not exact Brownian first-passage integration.

`safeguard.py` trains separate neural actors and critics and selects among the neural proposal and a feasible action mesh. Training uses no reference values or reference policies. Policies are then evaluated by the independent NumPy implementation. All three seeds (101, 202, 303), fitted weights, date-specific optimization records, critic errors, full policy arrays, and feasible deviation gains are retained. Uniform continuum error is unmeasured, not zero.

`coupled_resource.py` solves a three-period stochastic allocation problem with dimensions 4, 8, 16, a common budget, nonseparable state cost, and rank-two correlated four-point shocks. It learns a convex squared-ReLU feature critic and a bounded neural proposal actor. Convex pointwise improvement is checked with a linear minimization gap. The independent scenario-tree optimizer enforces nonanticipativity. Full policy evaluation enumerates all 64 terminal branches. A matched deployment ablation uses the exact same weights but removes improvement. The 10^-3 common cost target is a declared reporting criterion, **not a preregistered trial**. A separate 10^-7 reference tolerance sharpens the cost audit. Ordinary double-precision bounds are not interval-arithmetic certificates.

`diagnostics.py` executes polynomial generator checks, sophisticated temporal evaluation, repeated-batch trace estimands, learned homothetic Merton and Epstein–Zin coefficients and actors, structured stochastic LQR, and a complete finite-state capacity game with independent dynamic best responses. Feature models and finite-state references are not relabeled as unrestricted neural solvers. The finite-horizon recursive sign architecture in `graph_tests.py` is a domain/terminal test, not an additional trained recursive solution.

`analysis.py` independently evaluates policy differences and forward occupation statistics. `replay.py` reloads deposited weights and checks NDU actions and complete resource costs. `make_tables.py` generates every current numerical table from JSON. `validate.py` checks declared resource tolerances, records distinct evidence classes, and verifies the exact Python bytes against the reachable source commit.

## Metrics and provenance

`output/ledger.jsonl` separates execution status, evidence class, and tolerance status. `output/manifest.json` identifies the source commit, package versions, source-file hashes, all saved weight/array hashes, and the ledger digest. Scientific digests exclude timing and memory fields; complete file hashes retain them. NDU raw records additionally declare a null global error certificate and explain why sampled gaps cannot supply one.

A Bellman gain is a value-unit improvement against the actual frozen evaluated continuation. It is not a sum of consumption and preference action distances. The independent finite candidate search supplies a lower observed deviation gain, not a certified global maximum. Full policy discrepancies report all three coordinates separately. NDU grid differences are finite-approximation comparisons, not certified continuous-time value errors.

Resource cost-loss upper bounds apply only to the stored initial states and exact finite shock model. Timings compare training plus policy evaluation with solving the same batch of initial states to the same accuracy target. No sparse-grid run, automatic high-dimensional speed advantage, or dimension threshold is claimed.

## Files

Main numerical JSONs, `.npz` weights and policy arrays, complete console logs, and generated tables are committed on the R4 branch. The root revision index is the reading authority. The review input is pinned at `79a7d84be2cbbf9bd5d181599ee110540128e3b5`. A plain-source commit is created before authoritative execution; result generation then cites that reachable commit. This avoids self-referential final-commit labels and the unresolvable source label identified in R3.
