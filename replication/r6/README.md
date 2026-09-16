# R6: counterfactual certification, structural controls, and risk mechanisms

## Immutable inputs and scope

The review input is `0d0e79a52e540bd0647801ce316f051d667c6797`, the R5 review of manuscript `c9f71077cf6a339573ac07be55d7660797bcf6ea`. The R6 branch starts at the review commit so that the complete report and its diagnostic programs remain available without copying or modifying them. The R5 snapshot used in development was independently reconstructed from its deposited artifact and matched Git tree `e57eb654bd1c4959be7d96f04327778f7cbbde05` exactly.

Run from the repository root, with Python 3.13, NumPy 2.3.5, SciPy 1.17.0, and PyTorch 2.10.0 CPU:

```bash
bash replication/r6/run_all.sh "$(git rev-parse HEAD)"
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r6 ECTA_R6.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r6 SUPP_R6.tex
python replication/r6/build_report.py --source-commit "$(git rev-parse HEAD)"
```

The source must be committed before the authoritative run. A later evidence commit adds generated tables, JSON, arrays, execution logs, and the PDFs. Its manifest identifies the earlier reachable source commit and verifies every declared source byte against that commit. Source transport and materialization are explicit in the workflow; a compressed transport is not the reviewable manuscript.

## Experiments and attribution

`bank_comparison.py` runs exact-oracle scalar optimistic support for the focal initial state and for simultaneous coverage of every state and date. It checks the full policy-line maximum independently of the adjacent-pair calculation. It does not claim to reproduce the neural implementation or full action-value generalized improvement of SFOLS. Both objectives receive the same full action oracle. Common kernel setup, policy construction, full-envelope checking, and policy/feature memory are separately reported. The mesh ablation removes learned lower-policy actions while retaining the original full upper target and common anchor locations.

`structural_qp.py` analytically assembles the same nonanticipative scenario-tree QP for every fresh query. Node-probability preconditioning and its spectral constant are shared across queries. Each query begins at zero controls. The inherited full-tree implementation independently checks both gradient and convex optimality gap. The learned arm includes actual critic-only retraining; both arms include full-tree policy evaluation. All timing runs are serial, single-thread, with query medians of three. Setup, online time, original-reference results, all timing samples, and per-query arrays are retained. This directly incorporates the referee's stronger conventional comparator.

`transport.py` evaluates fixed policies by conditional-count Bernstein recursion, checks direct mixture evaluation, and constructs a count-informed information-relaxation upper bound. `kernel_certificate.py` constructs the endpoint-value correction and adaptively refines anchor intervals until the polynomial coefficient bound is below `0.001`. Each of three fixed contracts (`d=0,0.5,1`) covers every `lambda` in `[0,1]`, every one of the 1,617 finite states, and all eight dates. This is not a joint continuum in both parameters. The regime kernels have correlations -0.25 and 0.25; their probability mixture changes the finite shock law, not a claimed Brownian discretization at every intermediate correlation.

The same original 1,565 common controls and three frozen neural proposals are retained. CSR matrix multiplication represents exactly the inherited positive transition rows. Its numerical agreement with the original array multiplication is recorded. Independently selected-policy evaluation uses a different arithmetic path. The data contain every anchor policy/value, polynomial coefficient, interval upper array, subdivision bound, and replay check. These are double-precision finite-model certificates with explicit arithmetic tolerances, not directed-rounding proofs or diffusion guarantees.

`mechanism.py` compares positive versus nonpositive first risky positions, allowing optimal subsequent financial decisions. The no-adjustment arm fixes deliberate preference adjustment to zero at every node but keeps preference shocks, covariance, financial controls, operating boundary, and settlement unchanged. It evaluates the two risk-specific option values independently. Opposite-sign brackets establish the existence of a crossing, not its global uniqueness; reported effort/duration ratios have the local regularity conditions stated in the theorem.

`unit_tests.py` independently enumerates regime sequences and, in two-date small models, every deterministic Markov policy. It also executes the kernel-chord negative control. `validate.py` asserts the advertised scopes and replays the inherited R5 contract, all-nine resource, and all-date game checks without invoking their output-writing main program. No historical evidence is overwritten. `build_report.py` verifies compilation, references, layout warnings, and protected historical files separately from scientific conclusions.

## Reading the output

`output/manifest.json` records source and input/output SHA-256 hashes, the reachable source commit, and the environment. `output/validation.json` records executed checks. Generated manuscript tables and `revisions/2026-09-16-r6/execution_summary.md` derive directly from JSON. Logs are stored under `replication/r6/logs/`. Preparation times are platform-specific observations; theoretical guarantees do not depend on a speed advantage.

The retained R4/R5 experiments and referee counterexamples remain evidence in their original scopes. No result here implies submission, referee appointment, or approval by Econometrica.
