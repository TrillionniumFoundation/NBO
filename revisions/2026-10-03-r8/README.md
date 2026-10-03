# Neural Bellman Operators — integrated R8 referee candidate

The authoritative article and supplement are root `ECTA.tex` and `supp.tex` on
this candidate. The title, author, utility normalization and economic agenda
remain unchanged. This is a revision of NBO, not a protocol-only replacement.

## Immutable inputs

- R7 source: `5bab4649728860fb655c5371f3705787f10b4a78`.
- R7 evidence: `b1409008625f550195ce9ead468391ad2449a240`.
- Latest advisory report: `c63f6817f498e1cfe9a653139f7a25bf44a4418a`.
- R8 development base: `cb5382ffa64630c0399e7204753f5667660ac0df`.
- The R8 computational source and execution run are recorded in
  `REMOTE_EXECUTION.json`; the evidence commit is that source's child.

The latest report is repository-owner commissioned and AI-assisted, not an
Econometric Society editorial decision. The later unexecuted R7 development
protocol is not counted as completed evidence.

## Substantive revision

The article integrates the successful R7 finite preference and neural dynamic
Cournot results, raw/shortlist/hybrid distinctions, complete fixed-rival dynamic
best responses, 36 common-noise method comparisons, all five missing pure stage
locations, economic units, and the independent scalar interval replay.

R8 adds continuous preference controls trained without exhaustive maximizing
labels, direct continuous optimization, a separately reported local-search
hybrid, and an actor-free search ablation. A budget-safe action-box proposition
is proved and executed across the complete three-dimensional action box on the
two-state nodal economy. Cell-slope and cell-corner enclosures retain every
unresolved upper bound. Their common optimal envelope is reused only within the
same economy, with independently recomputed payoff envelopes for each policy.

Additional executed comparisons include direct and classical dynamic-game
methods, gated finite Bellman regression, and tensor Chebyshev projection.
The gated method uses DGM-style gates, not an alleged full differential DGM
implementation. Eighteen common frozen-policy space/time refinements remain
sensitivity diagnostics. A separate transfer proposition makes the uncomputed
continuous-state/time and continuously monitored boundary defects explicit.

## Reproduce

Pinned numerical packages: NumPy 2.3.5, SciPy 1.17.0, PyTorch 2.10.0 CPU,
mpmath 1.3.0. The workflow pins Python 3.13.5 and records machine, affinities,
thread policy, package lock output, timings and all source/result hashes.

```sh
python revisions/2026-10-03-r8/code/replicate.py
bash revisions/2026-10-03-r8/code/build_pdf.sh
```

`replicate.py` does not skip existing results. It reruns all four specified
pilot failures, nine principal continuous-control cases, fourteen additional
comparators, two global action covers, eighteen frozen-policy refinements,
shared policy envelopes, and the inherited-data audit. Raw weights, arrays,
stdout/stderr logs, closure counts, query counts, and failures are retained.
The corner cover runs on a separately pinned CPU core when available; the
remaining one-thread computations are sequential. Costs are reported with that
execution context, not represented as isolated hardware microbenchmarks.

`test_r8.py` contains 15 new tests. `replay_inherited.py` replays the 12 R6 and
11 R7 tests while redirecting inherited writers to a temporary copy; hashes
confirm the historical evidence is unchanged. A passing test suite checks
correctness and truthful accounting, not universal passage of economic targets.

## Candidate and artifacts

The source branch is immutable. The source transport archive, if present, is a
hash-checked bootstrap only; all expanded Python and TeX sources are committed
on the materialized source branch and on the candidate. The evidence workflow
adds actual result arrays, generated tables, compilation logs and PDFs. A
separate referee-copy branch points to the verified candidate commit.

- `build/ECTA.pdf`: integrated main article.
- `build/supp.pdf`: proofs, run-level comparisons and historical discussion.
- `build/response.pdf`: point-by-point B1–B7 / M1–M9 response.
- `TABLE_MANIFEST.json`: generated tables and exact input hashes.
- `INTEGRATION_MANIFEST.json`: archived manuscript blobs and preserved labels.
- `REMOTE_EXECUTION.json`: exact source, run and durable evidence hashes.

No earlier review/revision branch is moved. Except for the integrated root
article and supplement, all pre-existing files are unchanged. Historical
numerical discussions are retained as dated material, not relabelled as new
results. See `SECTION_MAP.md` and `LOCAL_DEVELOPMENT_NOTE.md`.
