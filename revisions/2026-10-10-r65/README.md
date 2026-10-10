# Neural Bellman Operators — R65

This is a revision of the original NBO paper responding to the 10 October 2026
R62 report. It is not a differently titled replacement paper. R63 and R64
completed scientific services are integrated with a new prediction/localization
proposition and an independent complete-record audit. No scientific service is
retrained or retimed for this integration.

## Reading order

[Main article](build/ECTA.pdf), [technical supplement](build/supp.pdf), and
[point-by-point response](build/response.pdf) form the active submission.

The exact preceding [article](build/development62.pdf) and
[supplement](build/development-supp62.pdf), and their broader
[complete article](build/complete62.pdf) and
[complete proof companion](build/complete-supp62.pdf), remain available.
The [content-location map](CONTENT_MAP65.md) locates every prior label in the
byte-preserved `retained62/` sources. The bibliography and journal class are
ordinary source dependencies, not supplied standalone font files.

## What is tested

The independent suite has 22 tests, supplementing 24 retained query tests and
17 retained gate tests. `audit/RESULT_AUDIT65.json` records the 256-service replay,
55,296 bound decision records, 27,648 distinct re-queried observations, repeated
model/trace identities, and all complete process clocks. True trajectories and
costs use independently written rational primitives. Numerical endpoint replay
uses the original algorithm and is not a formal proof-checker claim.

The matched gate reduces deployment queries versus unconditional insertion in
all 32 distinct task-target-seed comparisons. Conventional methods still have
the smallest complete-process median in every one of the eight task-target
cells. Finite dyadic workloads are not independent continuous-law cost samples.
The earlier adverse pure-policy cost comparisons are preserved.

## Reproduction

Install Python with numpy, scipy and scikit-learn; pandoc; poppler-utils; and
LaTeX with latex-extra, fonts-recommended and science packages. From the checked
out repository root:

    python3 revisions/2026-10-10-r65/code/build65.py

The full build needs the retained R62 imported Python sources and R63/R64
frozen records already committed in their directories. It uses no network,
retraining or new scientific service timings. `--documents` rebuilds only the
publication and derived tables from the already verified audit, and is labeled
as such. The assembly script is for initial source materialization, not routine
rebuilding of author-edited ordinary sources.

`audit/RELEASE65.json`, `audit/CLEAN_REBUILD65.json` and
`audit/FINAL_DELIVERY65.json` bind the tested source, compiled documents and
clean publication reconstruction. All active manuscripts are ordinary UTF-8
source files; the complete prior editions remain available for further review.
