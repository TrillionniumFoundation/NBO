# R38: Certified Bellman Operators for Costly Policy Revision

This is a materialized scientific revision addressing the R36 referee report at
`c81410887bca5c16975beabb2ca8d6be7f235a19`, with the complete R34 scientific
ancestry retained. The primary economic specifications and operating tolerances
have not been replaced. Read the root `R38_REVIEW.md` for the current review entry.

## Reproduction

From the repository root, with Python 3.13, NumPy 2.3.5 and SymPy 1.14.0:

```sh
python revisions/2026-09-24-r38/replication/run_core.py
```

This runs the primary exact program, distinct SymPy primary verifier, all 66
sensitivities, constrained frontier constructor and verifier, whole-cell local LP,
nonlinear economy, and global support diagnostics. Every subprocess must succeed.
The 187 canonical exact object hashes must match `replication/expected_objects.json`.
Results are not inferred from a protocol. Timings and NPZ timestamps are not exact
scientific-object identities. The nonlinear and sensitivity checks are not called
independent SymPy verification.

Publication requires a git checkout, the repository's `econsocart.cls`, pdfLaTeX,
standard LaTeX packages, and PyMuPDF. The completed scientific ledgers must exist:

```sh
python revisions/2026-09-24-r38/build/publish.py
```

That script regenerates tables, compiles the five root PDFs, checks references,
page boundaries, historical page preservation, and unchanged inherited files,
and writes a publication manifest. It does not push. The isolated GitHub workflow
performs a non-force push only after the checks succeed and its source HEAD has
not changed.

## Scientific scopes

42 unchanged primary configurations: 24 exact uniform-initial deterministic
optima, 12 with positive cost, and 23 with complete cost-function equality.
The 18 other deterministic intervals are retained. The history-conditioned
frontier solves 70 fixed-state objectives, not the uniform Markov problem.
Two analytic two-period randomized Markov references use the same uniform
objective as their deterministic comparator. Local LP convergence concerns the
continuous local relaxation, not global strong duality. The nonlinear operating
tolerance is 1/2 and does not replace either primary tolerance.

66 designed economic sensitivities preserve all 44 zero savings alongside the
22 strictly positive savings. Nonlinear records retain 16 unsuccessful compiled-rule
pilot certificates, 40 restart candidates (26 certified) and 20 classical portfolios
(15 certified). Failure of a sufficient box certificate does not prove infeasibility.
The original stopped-control model, target, failed global bound, and scalar proof
remain in the article, supplement, and historical annex.

## Verification and preservation

`SCIENTIFIC_MANIFEST.json` identifies the actual executed scientific source and run.
`PUBLICATION_MANIFEST.json` identifies the completed manuscript build and file hashes.
`results/execution_ledger.json` records exact object comparisons and process status.
`results/independent_verification.json` records 42 independent primary checks and
20 rejected mutation categories. `results/frontier_independent_verification.json`
records 70 separate frontier checks. Other checks have their actual narrower labels.

`history/preservation_manifest.json` checks every inherited file. Only the root
revision pointer is updated; its preceding bytes are preserved. All previous
reports, protocols, source, results, and PDFs remain unchanged. The historical
PDF annex imports all 348 preceding R34-package pages with a new cover, without
removing any source pages. Prior protocol-only execution assertions are not
retrospectively treated as proven runs.
