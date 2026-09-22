# R9 replication: original-payoff certification and frozen comparison

Run commands from the repository root. The canonical revision is `revision/econometrica-r9-constructive-certification-2026-09-22`. The source record begins from review commit `9749c3cf28f9438315b8f504a358bbe307ea89a5`.

## Environment

Initial construction used Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, CPU PyTorch 2.10.0, and mpmath 1.3.0 (`local_environment.json`). The frozen external experiment and clean-checkout CI use Python 3.11 with the same package versions. Set one numerical-library thread when comparing times:

```sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install numpy==2.3.5 scipy==1.17.0 mpmath==1.3.0
```

For manuscripts install a TeX distribution containing `pdflatex`, `amsmath`, `amsthm`, `natbib`, `booktabs`, `tabularx`, `microtype`, and `hyperref`, plus Poppler (`pdfinfo`, `pdftotext`). The unchanged checked-in Econometric Society class `econsocart.cls` supplies the journal layout. No font file is distributed by this revision.

## Audit the frozen evidence without retraining

```sh
python revisions/2026-09-22-r9/replication/validate_evidence.py --skip-pdf
python revisions/2026-09-22-r9/replication/recheck_certificates.py
bash revisions/2026-09-22-r9/replication/build.sh
python revisions/2026-09-22-r9/replication/validate_evidence.py
python revisions/2026-09-22-r9/replication/write_manifest.py
```

`validate_evidence.py` checks every declared external panel and seed, path-array means, checkpoint finiteness, initialization equality, pinned author revision, primitive feasibility, all original-value/dual/action bounds and flags, table regeneration, historical preservation, and compilation. It is an evidence-consistency check, not a substitute for the proof.

`recheck_certificates.py` re-executes all four original-policy evaluations, all three fitted upper bounds, the full restricted dual refinement, all three absolute lower references, all ten action certificates, and interval differentiation of the two learned neural critics. Frozen inputs are copied to a temporary directory and never overwritten. The endpoint comparison tolerance `1e-10` checks reproducibility across platforms; each recomputed bound is obtained from its own outward arithmetic, not by treating this tolerance as an analytical error bound. Full logs and `certificate_recheck.json` are written in the R9 directory. Retraining is neither necessary nor used to reproduce the submitted bounds.

The main manuscript and supplement build directly from ordinary checked-in inputs. No archive, base64 fragment, network download, or preceding revision build is needed to compile either PDF. Class font-substitution and underfull-box warnings may occur on a standard TeX installation; unresolved references, duplicate destinations, and overfull boxes fail the build validation.

## Reconstruct the scientific calculations

The following commands regenerate canonical result files. Run them in a separate worktree or copy when preserving the exact submitted evidence and timings.

```sh
for k in 0.5 2 8; do
  python revisions/2026-09-22-r9/replication/original_actor.py --k "$k" --steps 2500
  python revisions/2026-09-22-r9/replication/original_upper.py --k "$k"
  python revisions/2026-09-22-r9/replication/certify_upper.py --k "$k"
done
python revisions/2026-09-22-r9/replication/original_actor.py --k 2 --restricted --steps 2500
for tag in k0.5 k2 k8 restricted; do
  python revisions/2026-09-22-r9/replication/original_policy_certificate.py --tag "$tag"
done
python revisions/2026-09-22-r9/replication/restricted_dual.py
python revisions/2026-09-22-r9/replication/action_certificate.py
python revisions/2026-09-22-r9/replication/neural_jet.py
for d in 8 16 32; do
  python revisions/2026-09-22-r9/replication/absolute_lower.py --dimension "$d"
done
python revisions/2026-09-22-r9/replication/make_tables.py
```

The actor is a trained time-only neural subclass, with a global differentiable consumption-budget projection and zero portfolio. Its frozen piecewise-constant controls are evaluated in the original continuous Brownian first-exit economy. The independently fitted polynomial is a witness candidate, not a known optimal value. `certify_upper.py` independently validates its trace and continuous-generator residual. `restricted_dual.py` bounds the optimal no-adjustment problem while retaining **all** adaptive original consumption and portfolio controls.

`action_certificate.py` uses one scalar action-sum branch-and-bound tree. Dimensions 8 and 16 use exact stored R8 learned-critic checkpoints and identified states; dimensions 32–128 use independent Gaussian jets for the same Hamiltonian. This is not a whole-state certificate or an average complexity experiment. `neural_jet.py` validates the derivatives of the two actual neural critics. `absolute_lower.py` retains the original terminal payoff in a relaxation and bounds its remaining scalar integral.

The optional `wealth_upper_*.py` programs are development pilots, not part of the successful certification route. Their collocation objectives, including values contradicted by independent checks, are not verified upper bounds. See `wealth_pilot_status.json`; do not add them to tables as certified results.

## Frozen external comparison

The protocol and source were committed **before** execution at `46aef70a24f74cf57503018a7e7f21cb46af08e3`. The unmodified author solver is `sx-fang/MartNet@991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a`. The complete run is GitHub Actions `35682656529`, and its complete evidence commit is `58007e6edf8a6d80e930e025138f38d978a82aba`.

To reproduce the experiment on a separate worktree:

```sh
git clone https://github.com/sx-fang/MartNet.git martnet-author
git -C martnet-author checkout 991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a
for d in 8 16 32; do
  python revisions/2026-09-22-r9/replication/external_suite.py tune --dimension "$d" --source martnet-author
  for seconds in 10 30; do
    python revisions/2026-09-22-r9/replication/external_suite.py run --dimension "$d" --seconds "$seconds" --source martnet-author
  done
done
python revisions/2026-09-22-r9/replication/external_suite.py summarize
```

The submitted tuning uses seeds 600–601 and multipliers 1/3, 1, 3. The twelve holdout seeds 720–731 are not used for selection. Each method gets the same trial time budget; its native actor/critic learning rate is multiplied, while the SOC adversary rate remains declared and fixed. Setup is warmed and pair order randomized. All seeds, checkpoints, sample arrays, curves, and clocks are retained. Wall-clock stopping naturally makes update counts and retraining results machine-dependent; reproducibility does not mean bit-identical re-training across different machines.

Every rollout is a sample-and-hold policy for the unchanged additive-noise continuous model. The per-slab Gaussian transition and reward integral are exact in real arithmetic, but network evaluations and Monte Carlo means are not outward certificates. The 64-versus-128-date difference compares different deployment policies, not an Euler-error estimate. The rigorous lower bound is an absolute reference; sampled excess over it is not deterministic regret.

## Error and economic-claim ledger

At cost two the flexible policy's value interval has width `1.3292e-5`, while its regret upper is `0.10633861`: the **flexible 0.01 target is still unmet**. The restricted optimum has width below `0.009047`, and optimal access welfare is at least `0.04094994`. These are distinct claims. Across costs 0.5, 2, and 8 the access lower bounds are all positive; two-sided access intervals and optimal-budget secants remain wider than would be needed for precise magnitude identification.

Original-value evaluation includes utility-polynomial remainder, outward time integration, exact-exit correction, and arithmetic. The fitted upper includes an independent continuous residual, utility remainder, trace, and artificial-face localization. The restricted dual includes bounded-source verification, weighted Taylor remainder, Gaussian tails, localization, and arithmetic. No finite-scheme discrepancy term is silently set to zero.

## Review artifacts and history

`ECTA_R9` contains the current main argument and complete new proofs. `SUPP_R9` preserves complete R8 and R4 texts and all six delivered R5 tables. `response_to_referee.md` addresses every R8-F1–F12 finding. `inherited_manifest.json` checks all 556 inherited files, with only the stale root index replaced and its original bytes archived. `source_manifest.json` records source/evidence hashes and final PDF hashes. The complete record remains on the new R9 branch; no primary or review branch is merged or rewritten.
