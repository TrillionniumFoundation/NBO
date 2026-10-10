# Neural Bellman Operators — R67

The revision responds to the 10 October 2026 advisory R65 report, without changing
the paper's title, economic model, constructive neural backend or Bellman target.

[Main article](build/ECTA.pdf), [technical supplement](build/supp.pdf) and
[point-by-point response](build/response.pdf) form the active submission.
Ordinary sources are ECTA.tex, supp.tex, response.md and sections/*.tex.

## The revised argument

The existing NBO construction, accuracy, acquired-policy, gated-query and
localization statements are retained. Their proofs appear verbatim in the
supplement. The new pre-query closure theorem uses purchased upper endpoints
and a global lower bound, not an unknown minimizing action. A computable margin
loss bounds further verification queries. Fixed nonnegative ReLU features give
a convex readout problem with a directly calculable optimization-gap bound.
The two-control extension retains coupled capacity and two independent shocks.

## Corrected execution, not overwritten evidence

R66 used aliased arrays in its cumulative path interval. The exact counterexample
is in audit/ERRATUM67.json. R67 fixes only that accumulator, freezes a new source
version before rerunning all 212 declared processes, and retains all R66 sources
and results unchanged. The same fixed random indices isolate the correction;
the rerun is not a second independent statistical sample.

The corrected catalogue contains 180 same-gate comparisons, 24 complete cached-
reuse services, two original-continuous-law inference services, and six vector-
control scaling services. All fitting seeds, warnings, blocked predictions,
zero-progress events, reuse failures, service receipts and raw paths are kept.
The 16,384 distinct common-path rows are the sample size across the two inference
tasks; four policies sharing each path do not quadruple that number.

## Preservation and review

[Prior R65 article](build/prior-ECTA65.pdf) and
[prior R65 supplement](build/prior-supp65.pdf) retain the entire preceding paper.
[Development article](build/development62.pdf),
[development supplement](build/development-supp62.pdf),
[complete development](build/complete62.pdf), and
[complete proof supplement](build/complete-supp62.pdf) preserve the broader NBO
program under its original assumptions. CONTENT_MAP67.md maps retained labels.
Older evidence does not become evidence for a different newly queried policy.

## Reproduction

Use Python 3 with numpy, scipy and scikit-learn; pandoc, poppler-utils and
LaTeX packages supporting the retained Econometric Society class. From the
repository root run:

    python3 revisions/2026-10-10-r67/code/build67.py

The builder does not refit models or create new policy-cost observations. It
replays all corrected path enclosures, statistical intervals, stored decisions
and source identities; all distinct scalar comparison traces are re-queried
using saved models. Huge vector continuation trees are not independently rerun
by this replay, and exact tests are not a formal proof assistant.

The publication manifest audit/FINAL_DELIVERY67.json is created only after the
full build and clean source-archive reconstruction pass. It binds nine PDFs,
ordinary sources, tests, preservation and record audits. A visual inspection
record, when present, is distinct from automatic typography/log checks.
