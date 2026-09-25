# R42: atomic structure, feasibility repair, and complete certificates

## Review entry points

The current article is `ECTA_R42.pdf` (source wrapper `ECTA_R42.tex`). The current technical supplement, point-by-point response, and computation report are `SUPP_R42.pdf`, `RESPONSE_R42.pdf`, and `COMPUTATION_R42.pdf`. `HISTORY_R42.pdf` preserves the complete R40 article and technical supplement as a separate archival volume. No previous scientific source, result, or PDF is deleted or overwritten.

Addressed report: `reviews/2026-09-25-econometrica-r40/referee_report.md` at `cf195a594c177208dbb5488576464dce9627a830`. Scientific/audit base: `70aa68e2ecac000e16fb3a6b2c2f5ee275b6b64f`. New branch: `revision/econometrica-r42-atomic-structure-2026-09-25`. Case-registration commit: `a6c6440b67210a4e6d1d75b372b5c4e59c6691a0`.

## Scientific additions

The finite-horizon slack ladder repairs approximately feasible policies at discount factor one, with an explicit horizon-dependent modulus. Its proof allows action-dependent Borel kernels; 48 exact finite tests check the construction. At zero tolerance the feasible class reduces exactly to operating-optimal actions, giving an implementation-cost Bellman recursion. A separate analytic supplement gives an infinite-horizon discounted tail enclosure with an explicit exact-terminal-value trust boundary and a time-dependent policy class.

Under exogenous dynamics, pointwise aggregation and a measure-valued reference pushforward identity preserve the full unrestricted measurable common-policy optimum. This is not a restriction to a cellwise policy sieve. The executed continuum service economies have finitely atomic nonlinear shear dynamics in two continuous coordinates. Their all-restart revision problem reduces exactly to a linear program. Twelve predeclared cases span up to 64 states, 64 dates, three/five actions, banded/cyclic/dense regimes, discounts 0.95/0.99/1, and allowances 0.01/0.05. Each has a positive-cost interval independently checked in rational arithmetic. The largest actual interval is below 9e-8, against a registered 1e-4 target.

The density experiment constructs nonzero operator errors, both adjusted finite solves, independent certificates, and every error-budget term. One of three perturbations fails the sufficient tightening condition and is retained. The original action-dependent maintenance models are not instances of the new exogenous theorem. Their 30 positive randomized intervals remain open. All 42 signed deterministic savings and horizon-specific median/max widths are re-tabulated exactly, not rerun.

## Verification and reproduction

`replication/structured.py` proposes LP policies and multipliers and produces exact rational certificates. `replication/verify_structured.py` imports neither the constructor nor NumPy/SciPy/any optimizer; it rebuilds the primitive contract, all probabilities, all restart regrets, actual cost, and residual-corrected lower endpoint. Compressed proof objects contain primitive fractions, probabilities, and equality multipliers. Any multipliers give a sound residual lower bound; floating dual feasibility is not assumed.

Run, from the repository root:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python revisions/2026-09-25-r42/replication/run_suite.py
python revisions/2026-09-25-r42/replication/repair_tests.py
python revisions/2026-09-25-r42/replication/density_transfer.py
python revisions/2026-09-25-r42/replication/assemble.py
for x in ECTA SUPP RESPONSE COMPUTATION; do
  latexmk -pdf -interaction=nonstopmode -halt-on-error "${x}_R42.tex"
done
python revisions/2026-09-25-r42/replication/publish.py
```

The suite rechecks existing objects. To regenerate proposals, remove only the R42 `proofs/case*.json.gz` files. Python 3.11+, NumPy, SciPy, PyMuPDF, and the repository's Econometrica LaTeX class are required for the entire publication procedure. The checker alone uses only Python's standard library. Actual versions and thread settings are saved in `results/environment.json`. Timings are descriptive single-run measurements; the structural and unreduced LP comparison uses the same mathematical object and ordinary presolve, not a deliberately handicapped global solver.

`results/inherited_r41_finest.json` is the unmodified result retrieved from the successful R41 workflow run 36066906929 (artifact 10837666819). It is **not a new R42 replay**. It independently reconstructs the complete retained T=32, N=256, epsilon=1/2 nonlinear object, with 92,274,688 support-action inequalities. Its proof and verifier hashes are retained. R42 updates the coverage label, not the original interval.

## Evidence boundaries

The case protocol was committed before execution but did not freeze final source code; these are predeclared designed structural experiments, not a fully code-frozen holdout or empirical validation. The atomic pushforward and unrestricted-policy reduction are analytic proofs, not machine-checked theorems. The original controlled atomic convergence question, tighter nonlinear feasible policies, a difficult approximate operating-oracle experiment, empirical calibration, and a matched local-work ablation are not falsely marked completed. The point-by-point response specifies the exact disposition of every major referee objection.

`PUBLICATION_MANIFEST.json` identifies the current artifacts and exact endpoint files. `results/publication_rechecks.json` gives all fresh independent finite checks and four mutation rejections. `results/preservation.json` verifies that all inherited scientific files remain unchanged, with the explicitly archived current index as the sole navigation exception.
