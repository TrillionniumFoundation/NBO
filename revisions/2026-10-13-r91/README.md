# Neural Bellman Operators — R91

R91 revises the original paper against the latest pinned R84 advisory referee report. The original title, author, economic primitives, complete-policy objective, broader applications and unfavorable evidence are retained. This is not a replacement finite-menu numerical-method paper.

## Current manuscript

Read [the main article](ECTA.tex), [the technical supplement](supp.tex), [the numerical appendix](appendix.tex), and [the point-by-point response](response.md).

The new signed complete-policy theorem and risk-specific transport proposition are in [risk91.tex](sections/risk91.tex). Their full proofs and sharpness examples are in [proofs91.tex](sections/proofs91.tex), with all exact configurations in [evidence91.tex](sections/evidence91.tex). [CONTENT_MAP91.md](CONTENT_MAP91.md) maps the referee objections to the inherited and new results.

## Provenance and preservation

- Controlling review: `b030d87d7e96440eb25a3178c94ee6a87940cdb0`, reviewing the R84 delivery `c1314494aca25e68f1426b554938e6fe89dd8409`.
- Intervening manuscript baseline: `9e06160b5464c41a5b84eaab9c3c4d171fc22832` (R90).
- R90 directory tree copied intact before amendments: `e6b9571b62e6a5bd3031e07b010e9dfd9aaf1ed5`.
- The original entry points and bibliography sources are retained; ordinary current TeX is committed after one-time integration. No earlier revision or review branch is overwritten.

## Reproduction and scope

From this directory, run `python3 code/reproduce91.py` after installing the dependencies in the R91 publication workflow. A fresh pre-integration source snapshot first uses `python3 code/apply91.py` and `python3 code/layout91.py`; neither replaces already integrated author sources. The ordinary resulting manuscript is the review target.

The recipe runs all current suites without skipped tests, independently checks inherited common-readout certificates and original-law cost records, reconstructs every required table, compiles four current documents, and compares a clean typesetting reconstruction. Its actual results are recorded in `audit/reproduction91/VERIFICATION91.json`. A separate visual record must match the actual PDF hashes before a visually qualified release is claimed. Older copied audit records and PDFs are not current R91 approval.

The new exact diagnostics comprise 36 signed-risk tests and 14 new tests of inherited joint-domain and decision claims, with 27 configurations, 1,728 complete policies and 3,456 initial-state inequalities. They add no fit and no independent economic observation. They do not replace the largest-vector reimplementation, matched vector tournament, measured energy or application-specific monetary calibration.
