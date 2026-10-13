# Neural Bellman Operators — R92

This revision of the original paper responds to the latest pinned R84 advisory report, b030d87d7e96440eb25a3178c94ee6a87940cdb0, and continues the completed R91 manuscript, 368a9e754f5de04eb1957e152f22d6ef2c34f2fe. The original title, author, economic primitives, complete-policy objective, broader applications, active sections and adverse evidence are retained. No earlier revision or review branch is changed.

## Current paper and response

Read [ECTA.tex](ECTA.tex), [supp.tex](supp.tex), [appendix.tex](appendix.tex), and [response.md](response.md). New theory is in [centeredrisk92.tex](sections/centeredrisk92.tex), its full proof in [proofs92.tex](sections/proofs92.tex), and complete diagnostic specification in [evidence92.tex](sections/evidence92.tex). [CONTENT_MAP92.md](CONTENT_MAP92.md) maps the changes to the report.

The new result centers the original conditional risk dual at the actual stored NBO continuation. State-dependent subsolutions and supersolutions yield original-optimum complete-policy bounds; an exact finite affine risk representation has a penalized risk-occupation LP. A strict support-function certificate safely excludes risk pieces over a previously verified error set. A larger bound from a new approximate calculation never replaces a smaller valid inherited certificate.

## Execution and delivery status

The source is integrated once by `python3 code/apply92.py`. This preserves every prior active section and all old wrappers. Copied R91 PDFs move to `preserved/R91-compiled-history/`; they are not R92 outputs. Ordinary integrated TeX is committed before execution.

From this directory, `python3 code/reproduce92.py` runs all inherited current suites, new adversarial tests, a full deterministic catalogue, a different original-law risk implementation, clean new-science replay, inherited independent checks, all required tables, and four-document clean typesetting. Actual results, source identity, document hashes and failures are in `audit/reproduction92/VERIFICATION92.json`. A current manifest is required before any success claim; inherited R91 approval is not R92 approval. Current PDFs, when compiled, are in `build/`.

Visual qualification is separate and must match those actual PDF hashes. The final delivery note must state whether inspection is complete or sampled; a compiler log alone cannot establish visual review. The workflow preserves failed as well as successful attempts and uses no force push.

## Scope of new numerical evidence

The complete fixed diagnostic grid has seven horizons, three original nested-AVaR levels, four prescribed shared neural continuations and three residual radii. These are rational mathematical diagnostics, not new fits or independent economic observations. The independent implementation uses the primal threshold formula and a distinct original-value recursion. The smallest two horizons also enumerate complete policies and use an un-memoized descendant evaluator. The larger cases test the stored recursion at up to 64 dates with three states; they do not reimplement the inherited largest-vector problem.

The old held-out ReLU result, resource/timing reversals, warnings, investment intervals and price regions remain unchanged. Measured energy, application-specific monetary calibration and the full largest-vector comparator tournament remain distinct evidence obligations, not assumed successes.
