# Neural Bellman Operators — R99

This is a revision of the original NBO paper, not a replacement topic.

## Read first

- `build/ECTA.pdf`: integrated revised article; `ECTA.tex` is its entry point.
- `build/supp.pdf`: complete active proofs, including `new/proofs99.tex`.
- `build/appendix.pdf`: intact development record and specifically relocated prior sections.
- `build/response99.pdf`: point-by-point response to B1–B10 / M1–M10.
- `CONTENT_MAP99.md`: exact preservation and relocation boundaries.
- `results99/RELEASE99.json`: measured build, tests, source and PDF hashes.

## Lineage

Scientific baseline: `f802fe64d91d9f5c1c8f86123b0fbe114e622279`.
Review: `9723c6cd2cc8b3e071422f3e522d4a843946db63`,
`reviews/2026-10-14-econometrica-numerical-methods-r97/referee_report.md`.
Preserved research parent: `54b1e58a5e7c84163fc64768ff18b5a1a4af3ef2`.
R99 protocol: `7ce89a5637b21ed10fc944f9e09c9d5eca7e9083`.
The unfinished R98 research stream is not retuned, consumed or claimed completed.

## Executed exact mechanism

Run from this directory with Python 3.10 or newer (standard library only):

```sh
python3 code99/exact_decision.py
python3 code99/independent_decision.py
python3 code99/test99.py
```

The first two calculations use different integrators, bases and fitting algorithms.
They both produce the quadratic continuation and exact population regrets 1/540
(additive) and 1/5400 (quadratic). The stated oblique ReLU and conventional hinge
are identical zero-regret functions. These are exact theoretical-mechanism results,
not a new empirical investment sample. `test99.py` contains 15 test methods,
including exact-rational subcases and a coefficient-mutation rejection.

## Typeset

The inherited `econsocart.cls`, configuration, bibliography style, preamble, source
sections and tables are included. With TeX Live, `pdflatex`, `bibtex` and `pdfinfo`:

```sh
sh code99/build99.sh
```

The script builds all four PDFs repeatedly to resolve cross-document references,
then checks unresolved citations/references, source dependencies and PDF hashes.
A TeX installation provides its own fonts; no font files are distributed.
`requirements95.txt` remains the unchanged dependency declaration for historical
numerical programs. Those programs and the new standard-library mechanism have
separate reproduction scopes. Building the paper does not refit the historical
84-actor campaign or validate an unexecuted scaling experiment.

## Scientific boundary

The new action-support theorem and prospective-selection theorem are analytical;
the new finite decision mechanism has an independent exact acquisition check.
Historical investment clocks, policies, confidence intervals, failed runs and the
quadratic winner remain unchanged. No new population interval is attributed to
refitted actors, and there is still no certified neural adoption over quadratic
least squares in the retained investment price grid. A new exact economic mechanism
is not an empirical calibration of that investment model. Compilation and tests
are evidence about the implementation and manuscript, not journal acceptance.

## Referee package and historical records

`publication/NBO_R99_referee_package.zip` is a standalone package for reading
and rebuilding the four current PDFs and running both new exact acquisition
implementations and all 15 R99 tests. It contains the inherited executable source
modules required by these tasks. It does not claim to repeat every historical
experiment or include every historical raw dataset in the ZIP.

The Git revision preserves the complete R97 source/data tree at
`retained97/full-r97/`, with exactly the original Git tree identity. Historical
results and evidence directories are also inherited unchanged at their ordinary
paths. `results99/GIT_RETENTION99.json` identifies this preservation boundary.
Old source and old results are evidence, not newly executed R99 observations.

The four PDFs were built locally on the authorized host; GitHub Actions status
is separate and is not represented as a passed build. Final logs contain no
undefined or multiply-defined references or citations. The main bibliography has
one 0.74902-point overfull-box warning, recorded in the release receipt.
