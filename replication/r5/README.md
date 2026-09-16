# R5 reproducibility: contract-aware policy reuse

This package answers the R4 report at review commit `11082cc5054e91d3b2ac27826705f374ca74bfae`. It uses the immutable R4 positive transition source and trained policies/critics. It does not retrain or overwrite the historical R4 output directory.

## Reproduction

From the repository root, use Python 3.13 with NumPy 2.3.5, SciPy 1.17.0, and CPU PyTorch 2.10.0. Set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and `MKL_NUM_THREADS=1`. Run:

```sh
bash replication/r5/run_all.sh "$(git rev-parse HEAD)"
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r5 ECTA_R5.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build-r5 SUPP_R5.tex
python replication/r5/build_report.py --source-commit "$(git rev-parse HEAD)"
```

The argument must identify a reachable commit containing the exact executed source bytes. The isolated GitHub workflow first commits readable source, records that source commit, executes all programs, builds both PDFs, and commits results separately. Its final commit therefore differs from its source commit intentionally. The manifest records both the source and inherited inputs. Rerunning after the result commit can validly name that later commit when it contains unchanged source bytes.

## Executed components

`contracts.py` builds an explicit positive finite killed chain and repairs the three frozen neural policies. The common action set is the union of the `9×9×13` reference and `7×7×11` diagnostic meshes, supplemented at each node by the three original policies. Both meshes are needed because they are not nested. The same menu and transition kernel apply to all contrasts `d=m-rho*ell` in `[0,1]`, with `k=2`. The program stores every anchor's complete policy, independently evaluated benefit/duration/effort, optimal value, and interval certificate in `contract_bank.npz` and `contracts.json`.

`economic_robustness.py` computes fixed-action/fixed-tail sign certificates on entire intervals, 101 actual complete-policy reuse/direct workloads, joint state/time/action refinements, a correlation panel, and effort versus coefficient-weighted expenditure. A coherent annuity shift is an invariance test; a running-only shift changes the contract. Finite-model robustness is not a Brownian error estimate.

`resource_ablation.py` replays all nine immutable dimension–seed checkpoints with and without the actor. Each arm retains the critic and convex optimizer. Actor training, inference, online optimizer time, iterations, and projected break-even queries are distinct. A full PSD convex-quadratic critic supplies a representation comparator, with its own backward fit and projected-gradient test. The fresh-state workload uses 32, 128, 512, and 2,048 initial states, seed 541021, dimension four, trained seed 101. Every initial state has a complete 64-path policy evaluation.

`persistent_game.py` preserves the four-date reset model as a regression and solves a twelve-date game with capital survival 0.8. Nine active-set combinations and a best-response contraction check establish each stage equilibrium. A separately evaluated full unilateral best response stores every date/state/player gain. A deliberately distorted late action is a negative control.

`validate.py` compares the explicit kernel with the original independent NumPy backup, independently evaluates all anchor features and all-date Bellman gaps, recomputes whole-interval bounds, checks discount/settlement identities, verifies switching, replays all nine actor-free policies and critic-only retraining, and checks all-date game deviations. Random query checks complement but do not establish the interval guarantee.

`tables.py` and `execution_summary.py` read executed outputs. `build_report.py` checks source provenance, protected-history preservation, undefined references, overflow, and PDF production. The complete scientific environment and SHA-256 identities are in `output/manifest.json`.

## Timing and accuracy accounting

Resource times use the median of three serial complete-tree deployments. Critic-only training is charged to actor-free reuse; the actor's separate distillation cost is not charged to an arm that does not use it. A stricter `10^-7` reference gap validates accuracy for both arms; the timed reference uses the common `10^-3` tolerance. The common validator is not priced asymmetrically. Actor crossover counts obtained by projecting 32-query savings are explicitly projections, unlike the actually executed fresh-state workload.

For contract transfer, kernel construction and adaptive anchor preparation are reported separately and included when comparing preparation-inclusive totals. The online comparison executes the same 101 complete-policy counterfactuals in each arm, including switching and full feature evaluation. Both arms share the previously deposited neural proposal inputs; no claim about paying for an unrelated original neural training run is made. Machine-dependent ratios are not theorem constants.

All computational certificates are double-precision statements for the declared finite model or specified complete scenario trees, with numerical slack. They do not establish a continuous-action or stopped-diffusion error, a uniform guarantee over untested resource states, or general neural convergence. The paper supplies positive results at precisely the scopes executed.

## Development record

`development_trials/summary.json` records earlier single-reference-mesh trials and their source-record hashes. Full superseded ledgers are not part of the authoritative R5 evidence. That 1,056-action menu omitted some actions from the nonnested R4 diagnostic mesh and was superseded before the R5 manuscript was finalized. The authoritative output uses the union menu. An earlier 32-anchor cap did not attain `10^-3`; the adaptive implementation now allows up to 80 anchors and fails explicitly if the tolerance is not reached. No failed trial is counted as a passing certificate.
