# NBO R6 — Econometrica-style revision and computational evidence

The authoritative manuscript is root `ECTA.tex`; the expanded supplement is root `supp.tex`. The title and economic agenda remain **Neural Bellman Operators**. The new manuscript answers the latest R2 numerical-methods report by actually training multilayer actors and critics, verifying a continuous-domain consumption problem, comparing strong same-model baselines, and computing independent dynamic best responses.

## Ancestry and scope

Latest report: `review/econometrica-numerical-methods-r2-2026-09-28-d9054ab`, commit `278fb174eaee816259642675533a7281815a3df4`.
Reviewed manuscript: R2 `d9054ab6284369ccd6134286e9d2694e3621d562`.
Revision base: R5 `28e769a7e8f10cf89871b1a17e35c6ce269329aa`.
Candidate branch: `revision/econometrica-nbo-r6-2026-09-29`.

Only the new candidate is written. Main, review, R2, R3, R4 and R5 branches are left unchanged. `archive/ECTA.R2.tex` and `archive/supp.R2.tex` preserve the reviewed sources by exact Git blob identity. `SECTION_MAP.md` documents preservation; `RESPONSE_TO_REFEREE.md` answers B1–B7 and M1–M6.

## Reproduce

Use Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, PyTorch 2.10.0 CPU, and mpmath 1.3.0. A standard TeX Live installation needs the existing `econsocart` class dependencies, algorithmicx, booktabs, mathpazo and BibTeX.

```sh
python revisions/2026-09-29-r6/code/replicate.py
bash revisions/2026-09-29-r6/code/build_pdf.sh
```

Each individual experiment is executable independently. `build_tables.py` reads actual result JSON and produces the manuscript tables. `assemble_revision.py` is idempotent and verifies the exact R2 source identity before rebuilding the main/supplement; it never deletes the archive. `test_r6.py` checks arithmetic, full covers, reference refinements, action optimization, finite certificates, independent trace values/gradients, dynamic best responses, missing pure equilibria, and failed-ablation accounting. The inherited eight-test suite is also rerun.

## Evidence classes

**Continuous economic certificate:** the stopped-consumption MLP is interval-verified over the complete state/action domain. Arithmetic assumptions and both stopping-face errors are explicit. An 80-digit numerical test is not called a formal proof.

**Finite-model certificates:** NDU and Cournot enumerate their entire stated finite domains. The NDU records include time-indexed evaluation and improvement errors; the game records include independently optimized fixed-rival best responses. Continuous-action and controlled-diffusion discretization errors remain unverified and are not zeroed.

**Sampled neural diagnostics:** dense nonlinear capital experiments genuinely optimize generic networks, but their sampled residuals and Monte Carlo payoffs are not uniform optimality certificates. The narrow-domain failures and wider-domain follow-up are both retained.

**Exact-structure checks:** original Merton/EZ, temporal-self, exit and LQ laboratories remain distinct from the new multilayer runs. No historical GPU timings, unexecuted DGM/deep-BSDE run, or neural game equilibrium is claimed.

## Failures and provenance

No failed seed is discarded. The three joint-loss consumption runs fail; the initial NDU classification pilot is retained; the cost-sensitive NDU primary suite and high-dimensional studies include accuracy failures. A coarse dynamic game with no pure stage equilibrium is explicitly approximate. Regression tests may pass while these accuracy targets remain false: the tests check truthful accounting as well as correctness.

The branch-scoped workflow first materializes and commits the exact source package. It then reruns the program, captures logs, freezes the environment, generates raw weights/arrays/leaf covers/payoffs, builds PDFs, and commits the resulting evidence. `REMOTE_EXECUTION.json` identifies the computational source commit; `MANIFEST.json` hashes the resulting files. The local execution package is separate from remote recomputation, and neither is independent referee acceptance. The bootstrap package is a transport artifact, not an alternative implementation.
