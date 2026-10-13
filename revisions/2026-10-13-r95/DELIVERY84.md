# Neural Bellman Operators — R84 source delivery

## Manuscript and response

This is a revision of the original **Neural Bellman Operators** paper, not a
replacement topic. It responds to the latest pinned R67 advisory report and
starts from the completed R83 source-bound recovery. The original title,
author, primitives, fitted-label and continuation contracts, substantive
sections and unfavorable results are retained.

The editable current submission sources are:

- [Main article](ECTA.tex)
- [Technical supplement](supp.tex)
- [Numerical and development appendix](appendix.tex)
- [Point-by-point referee response](response.md)

The new main theorem and full proof are in
[sections/compatible84.tex](sections/compatible84.tex). Exact qualification,
separation and assignment duals and the exhaustive numerical catalogue are in
[sections/proof84.tex](sections/proof84.tex). The economic interpretation is in
[sections/study84.tex](sections/study84.tex).

## Substantive addition

An alternative must win its complete feasible menu, and choices at different
observation cells must be compatible with one shared readout vector. Rational
certificates impose both restrictions. A verified assignment dual transfers
them to original-law policy costs for every readout in the stated objective
sublevel. This sharpens the earlier reference-only actionwise bounds without
changing fitted labels, future controllers or the economic law.

The deterministic execution has 976 complete-menu problems and 1,572 joint
events. Independent rational checking verifies all 2,548 qualification
certificates and 16,548 assignment inequalities. Every one of 104 numerical
infeasibility statuses has a positive exact support-separation certificate.
The catalogue includes all 24 model-tolerance records and all 36 pairwise
class-cost comparisons. Twenty new mathematical/regression tests passed.

At excess objective 1/4096, the coarse-minus-fine Bernstein class comparison
changes from an interval crossing zero to a strictly positive compatible
interval. The article gives the exact-data-derived outward endpoints and the
supported normalized refinement-fee range. The calibrated Bernstein advantage
and earlier legacy ReLU advantage are both retained; this is not a universal
neural-superiority claim. No fitting attempt or independent cost sample is
added by this deterministic postprocessing.

## Exact provenance

Controlling advisory review:
`4b27b56f4514f6c1d77b69fe707f7202f8b06b19`.

Completed R83 baseline:
`0f807677ac6f2a47455f49f061ddbc9710b28738`.

R84 frozen scientific-source commit:
`356e304f50f0f57a44846bd7c8a1e2052b8a6fb0`.

Completed R84 scientific execution and independent verification:
`9e92417a50129e3abff51f9167ed83466866cb1e`.

Current manuscript and updated layout input snapshot:
`a84023e693df9c13e01268c8a1c4d02a8e8b1d5e`.

This source-delivery branch is an immutable reviewable snapshot, separate from
the moving publication branch. It does not modify any older revision or
review branch.

## Publication status — do not infer a completed PDF release

The prior four-document rendering attempt reached the final typography checks
but failed on six overfull boxes in the appendix. The actual traceback is
retained in `audit/PUBLICATION_FAILURE84.txt`. There were no undefined
references, duplicate labels, missing glyphs or fatal TeX errors in that
reported appendix check. The full-precision long-table layout has since been
revised to retain all rows and all six decimal places without those oversized
single-line intervals.

The new full publication workflow is run **38225828054**, job
**114732973269**. At the last connector check it was **queued**, with no
execution steps. Accordingly, this source delivery does **not** claim that
the changed layout has passed, that all inherited suites have been rerun on
this snapshot, that a clean full rebuild has passed, or that the current PDFs
have been visually inspected. There is no qualified R84 review-ready PDF
release recorded by this document.

The completed scientific checks above remain separately source-bound and
valid; they are not substituted for those unfinished publication gates.
Old PDFs are not relabeled as new R84 outputs. The complete unskipped build,
independent inherited bin replay, clean archive reproduction and actual-PDF
inspection are explicitly separate checks in `code/build84.py` and
`code/publish84.py`.
