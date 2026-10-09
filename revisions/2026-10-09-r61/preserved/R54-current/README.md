# Neural Bellman Operators — R54 referee revision

The title, model and research program are unchanged. This revision responds to
all ten major comments of the pinned R52 advisory report and integrates the
subsequent, separately frozen R53 full-sweep and perturbation records.

## Reading order

[Main article](build/ECTA.pdf), [technical supplement](build/supp.pdf), and
[point-by-point response](build/response.pdf) form the active submission.
The [complete development article](build/complete.pdf) and
[complete proof supplement](build/complete-supp.pdf) preserve the broader theory,
applications and adverse numerical evidence. Ordinary sources are ECTA.tex,
supp.tex, complete.tex, complete-supp.tex and response.md in this directory.

The directed certificate and its proofs are in sections/directed54.tex.
All-date policy costs and work are in sections/study54.tex and tables/*54.tex.
The machine-readable audit is audit/RESULT_AUDIT54.json; the publication and
preservation record is audit/RELEASE54.json. FINAL_DELIVERY54.json binds the
final files after the clean-archive rebuild. Its existence is required before
this directory is described as a completed publication.

## Reproduction

Install Python 3 with numpy and scipy, pandoc, poppler-utils, and the LaTeX
packages used by econsocart (latex-extra, fonts-recommended, science on Ubuntu).
From the repository root, run:

    python3 revisions/2026-10-08-r54/code/build54.py

The build uses ordinary committed sources and frozen records without network,
training, new simulation, or service retiming. It reconstructs tables and
replays every saved decision and cost interval. Primitive enclosure identities
are exercised by exact and numerical tests; stored-endpoint replay is not
misdescribed as independently integrating every economic kernel again.

## Evidentiary scope

Full sweeps concern the original continuous-law two-state nonlinear economy,
with horizons two and three. The adaptive comparator is nonuniform, not
non-tensor. The 384 controlled perturbation cases are deterministic diagnostics,
not independent policy-cost observations. The observed complete-catalogue work
account is not a minimum-work sequential stopping frontier. No unexecuted
high-dimensional comparison, learned-null discovery result, empirical fee
calibration, or representation-specific superiority is claimed.
