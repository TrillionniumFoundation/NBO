# Complete R9 — consolidated advisory review

Read [referee_report.md](referee_report.md) first. The recommendation is **reject in its present form**, while expressly crediting the repaired finite-model and economic-margin results. This is an owner-commissioned advisory review, not an official Econometrica report or editorial decision.

The reviewed manuscript is `revision/econometrica-r9-participation-permissions-2026-09-17` at `8c1e0472279fb66a2419b63b3e35df028ecfdd78`. The new review branch is `review/econometrica-r9-consolidated-contract-audit-2026-09-17-8c1e047`. This directory adds only review material; manuscript sources, numerical deposits, historical reports, and the revision index are not changed.

The report consolidates the R8 economic-stress report at `8c20474bca5b7388f5ba4640ec165f1ad8f5e91a` and the parallel independent-mechanism report at `cd8596c4dce9d477bea86525d8e1ae7eb0aed9ec`. R9 addresses the former, but the latter's dynamic-mechanism objection remains relevant. The report distinguishes this inherited objection from its new conditional commitment-instrument comparison.

## Reproduce the independent checks

From this directory, with Python 3.11 or later and no third-party dependencies:

```bash
python independent_audit.py > independent_audit_results.rerun.json
python -c "import json; a=json.load(open('independent_audit_results.json')); b=json.load(open('independent_audit_results.rerun.json')); assert a==b; print('PASS: recorded output reproduced')"
```

The program imports no author code. It executes 4,029 exact-rational finite-model assertions, including 96 exhaustive class-point comparisons and 5,232 Markov-policy evaluations. It also performs 27 high-precision primitive optimizations and three economic diagnostic assertions, for 4,059 assertions in total. Exact toy checks are not proofs of general theorems; Decimal optimization is not directed-rounding interval verification.

Full portfolio numbers used in the commitment comparison are explicitly transcribed from the pinned author deposit, not independently solved here. The extra assumptions for that comparison are recorded. No full portfolio reconstruction, neural training, NBO PDF build, or constructor interval enclosure was performed. All full-model results in the report are attributed accordingly.

The report's source register provides pinned manuscript, implementation, historical-review, and primary-literature references. `audit_manifest.json` records local file hashes and execution environment; it is an integrity aid, not another mathematical certificate.
