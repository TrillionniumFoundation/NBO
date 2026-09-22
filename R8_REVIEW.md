# Neural Bellman Operators — R8 referee entry point

## Read the revision

- **Current manuscript:** [ECTA_R8.tex](ECTA_R8.tex) and [ECTA_R8.pdf](ECTA_R8.pdf).
- **Complete preservation supplement:** [SUPP_R8.tex](SUPP_R8.tex) and [SUPP_R8.pdf](SUPP_R8.pdf).
- **Point-by-point response:** [RESPONSE_TO_REFEREE.md](revisions/2026-09-22-r8/RESPONSE_TO_REFEREE.md).
- **Current proofs:** [paper/proofs.tex](revisions/2026-09-22-r8/paper/proofs.tex).
- **Executed results:** [results](revisions/2026-09-22-r8/results); [execution manifest](revisions/2026-09-22-r8/results/execution_manifest.json).
- **Build and validation:** [build manifest](revisions/2026-09-22-r8/build_manifest.json), [validation report](revisions/2026-09-22-r8/validation_report.json), and [build logs](revisions/2026-09-22-r8/build_logs).

The PDF files and generated tables are produced by the review-build workflow and committed on this revision branch. The build manifest records the exact input checkout. Its source identity differs from the later commit that adds generated output; that distinction is deliberate and auditable.

## Scope and principal additions

The original continuous NDU model, action box, correlated state process, cardinal utility normalization, liquidation contract, recursive utility, sophisticated temporal selves, and game formulation are retained. The revised contribution consists of continuous one-sided verification pairs, error-calibrated adjustment-cost comparisons, a complete constrained NDU action rule, tolerance-scaled finite corrections with explicit enumeration costs, a learned-geometry interval certificate, and an actual pinned-author comparison on coupled nonconvex controls.

The twelve-date retained policy reaches a finite envelope of .00682279 with .8746% of decisions corrected at the .05 target, instead of the previous 54.6602% correction share. Six trained actors on the original geometry but explicitly modified running payoff have full-domain continuous regret upper bounds below .00113. In the new external panel, paired NBO-minus-SOC-MartNet realized cost differences favor NBO at the declared ten-second training budget in dimensions 8 and 16; all twelve paired cells and raw path samples are retained.

The original-payoff continuous NDU interval bounds are 14.0914 and 8.33956, not precision successes. Time/state/action refinements are diagnostics, not substitutes for missing exit/quadrature enclosures. Larger recursive/game experiments and matched-accuracy scaling are not claimed by this delivery. See the response for the explicit finding-by-finding status rather than interpreting a successful build as scientific closure.

## Exact provenance

| Object | Identity |
|---|---|
| Review answered | `69991122b2c3fcd26ce9d695da2e1c5f4eb89eb7` |
| Inherited R7 branch | `b6bb2e901211cff029a3d602901e00b3b0af90fe` |
| New revision branch | `revision/econometrica-r8-verified-manuscript-2026-09-22` |
| Frozen new experiment protocol commit | `35c6a455593d381d56b9931797d7e417358093e2` |
| Executed numerical source | `14ecbd481b0586cfbb72a0c00239184a4a2b0553` |
| Complete numerical workflow run | `35676743048` |
| Pinned external repository | `sx-fang/MartNet` |
| Pinned external source | `991ea8dde5bad6ba912eb8cc48b0cb48dbdd6c2a` |
| Exact manuscript build checkout | `build_source_commit` in the build manifest |

R6 and R7 contained protocols but no complete new canonical manuscript. R8 does not pretend to reconstruct missing R5 transport chunks. It provides new complete human-readable source, proofs, response, and PDF artifacts while retaining the fragments as historical evidence.

## One-command manuscript reproduction

From a clean checkout of the delivered revision, with Python 3.11+, NumPy, and `pdflatex` available:

```sh
bash revisions/2026-09-22-r8/build.sh
```

The included `econsocart` class and support files are used. A TeX Live installation with the standard AMS, booktabs, tabularx, natbib, microtype, and hyperref packages is sufficient. On Ubuntu, the review workflow installs `texlive-latex-extra` and `texlive-fonts-recommended`; its complete commands are in `.github/workflows/r8-review-build.yml`.

The build first checks source and result hashes from the completed numerical execution. It requires every declared seed and recomputes paired mean differences and Student intervals from the raw 4,096-path arrays. It verifies correction shares from saved policy arrays, generates all seven current tables, compiles both manuscripts three times, rejects unresolved references, and writes a source/output manifest. It does **not** silently retrain networks or replace stochastic results.

PDF byte identity can depend on the TeX environment and generation metadata. The stored manifest binds the actual delivered PDFs and the precise source that produced them; the numerical tables are deterministic functions of the stored records.

## Re-executing numerical experiments

The full clean numerical execution is specified in `.github/workflows/r8-execute-evidence.yml`, with Python 3.11, PyTorch 2.10.0 CPU, NumPy 2.3.5, SciPy 1.17.0, and mpmath 1.3.0. The workflow pins and checks out the author code and executes all declared seeds, not a selected best-seed subset. The author implementation is used under its retained repository license; R8 does not claim authorship of that external code.

A manual execution uses the same commands:

```sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
P=revisions/2026-09-22-r8/replication
python "$P/verify_continuum.py"
python "$P/learned_geometry.py"
python "$P/diagnostics.py" --task algebra
python "$P/diagnostics.py" --task safeguard
python "$P/diagnostics.py" --task mesh
# AUTHOR_SOURCE is a checkout of sx-fang/MartNet at the pinned commit above.
for d in 8 16; do
  for seed in 400 401 402 403 404 405; do
    python "$P/external_comparison.py" --source "$AUTHOR_SOURCE" --dimension "$d" --seed "$seed"
  done
done
```

Re-execution writes numerical outputs and therefore changes their hashes. To preserve the exact review package, run it in a separate checkout. Wall-clock budgets imply that update counts and stochastic results need not be byte-identical across processors. The delivered experiment is the source-bound run identified above, not whatever happens to be produced by a later machine.

## Preservation map

| Retained material | Current location or treatment |
|---|---|
| Original paper and earlier full revisions | `ECTA.tex`, `ECTA_R2.tex`, `SUPP_R2.tex`, `ECTA_R4.tex`; unchanged |
| Entire R4 narrative and technical appendix | Included without textual alteration in `SUPP_R8.tex` |
| R5 delivered tables | All six included in the preservation supplement, with explicit historical interpretation |
| R5 raw failures, corrected policies, checkpoints, arrays | Original `revisions/2026-09-21-r5` paths; unchanged |
| Every review report | Original `reviews` directories; unchanged |
| R6/R7 protocols and incomplete R5 transport records | Preserved, not treated as canonical manuscript source |
| New theory and experiments | `revisions/2026-09-22-r8` only |

No inherited source, derivation, review, failure, checkpoint, result, or manuscript is deleted. Only new R8 paths and branch-local workflow files are added. Existing main, review, and other revision branches are not rewritten.

## Development versus confirmatory execution

Original-model interval audits and safeguard/mesh work are deterministic post-review analyses. The protocol explicitly records that the original interval audit preceded registration. Learned-geometry and external settings were frozen before their new executions. Local integration included a development seed and a small number of wall-clock runs; a container timeout interrupted one local command before the subsequent seed finished. Those local integration outputs are not counted as extra independent seeds or mixed into the delivered tables. The clean workflow subsequently completed all twelve paired external cells under the unchanged registered settings. No favorable seed was selected for the main tables.
