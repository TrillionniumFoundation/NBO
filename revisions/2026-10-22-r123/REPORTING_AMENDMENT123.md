# R123 reporting amendment: match price economics to the measured cohort

## Discovery and immutable scope

This is a post-source-freeze implementation correction, documented before the
first R123 economic report. The original F123 scientific source remains
`f9e8108f92df3d694c2e1d60d4dc2573e460b75f`, and the original D123 state boundary
remains `3c61db61e624884468ae4dcdd6ae03488faa86e3`. The defect was identified by
source inspection after the primary execution and before generating a report.
The correcting agent inspected reporting source and used constructed interval
fixtures; it did not inspect R123 economic outcomes to choose this correction.
This amendment is not represented as part of the original prospective freeze.

The original `code123/report123.py` has SHA-256
`7aaf3396b04af4a1334f6cd0a44778f341c9f81739033dc2851811cd7cf8c9fa`.
It remains unchanged and preserved. No original model, state, actor, service
rule, accepted action, information budget, statistical family, numerical mesh,
precision, cost rule or original execution clock is changed or rerun.

## The discrepancy and the correction

`PROTOCOL123.md`, in its joint-inference and adoption section, requires every
cost scenario to use matching sampled economics. `REPORTING_SPEC123.md`, under
“Full cost and price menus,” repeats that requirement. The three measured
timing processes use the first 16 predeclared states; the primary uses all 32.

The frozen `price_tables` function instead computes its paired economic
contrasts once using the default `n=32`, then reuses them for all four clocks.
It also labels every price constraint as conditional on 32 saved states. Thus
its timing-clock economics disagree with the already published protocol.

`code123/report_adapter123.py` authenticates the entire original reporter,
extracts its one `price_tables` function, and makes three explicitly listed,
single-occurrence in-memory text replacements. The corrected function caches
contrasts separately for `n=32` and `n=16`, uses the appropriate cache for each
declared clock, checks the saved clock cohort size, and records the actual
number of sample states in every price constraint. Every other function and
all price-domain, clipping, comparator, cost, volume, strict-inequality and
intersection rules remain those of the frozen reporter. The original file is
neither rewritten nor replaced. The complete production censuses remain 3,712
deployment costs, 51,200 pairwise constraints, 512 menus and 128 three-clock
intersections. The 232 safe-gain and 696 signed population families remain
based on the original 32 states.

## Constructed verification and reporting boundary

`code123/test_report_adapter123.py` fabricates two service cells with a benefit
of `tau/4` on the first 16 states and `-tau/4` on the last 16. The frozen
function therefore gives zero benefit for every scenario. The adapter must
give zero for the primary and `tau/4` for every timing scenario. The fixture
also checks unchanged primary economics and all cost outputs, rejects a
mislabelled timing cohort, and runs the frozen exact statistical self-check.
Its tiny catalogue is confined to test globals; production retains all 232
cells and all frozen completeness assertions. No experimental record is read.

`REPORTING_AMENDMENT123.json` fixes this document, the adapter, the constructed
fixture, the exact original authorities and the corrected function hash.
Publish that amendment in a separate commit. Before the first report, publish
`REPORTING_BOUNDARY123.json` with schema `nbo.r123.reporting-boundary.v1`, the
full `amendment_commit`, the amendment's SHA-256 as `amendment_sha256`, and the
unchanged `source_commit` and `state_commit`. The adapter requires this
boundary and rechecks its identities after execution. The original reporting
receipt and the separate `ADAPTER_CUSTODY123.json` must both pass.

Run the report with:

```bash
python code123/report_adapter123.py --output results123/report
```

Operational CI invokes this same separately published adapter, compares the
complete scientific tables with the original completed report, and requires
the adapter custody receipt. It does not call an economic solver or draw a
new sample. The original source freeze and its original hashes remain visible
in every report. This amendment makes no claim about favorable or adverse
economic outcomes, adoption domains, or future timing performance.
