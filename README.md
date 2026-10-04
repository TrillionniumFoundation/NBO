# Neural Bellman Operators

## R18 Econometrica revision — 5 October 2026

This revision develops the original *Neural Bellman Operators* paper by Qian QI. The common learned continuation, nonlinear capital economy, recursive utility, endogenous preferences, temporal selves, and dynamic games remain the subject. All previous scientific files remain available; exact copies of the replaced publication roots are in `revisions/2026-10-05-r18/archive/`.

### Read the current paper

- [Main article](revisions/2026-10-05-r18/build/ECTA.pdf), [source](ECTA.tex).
- [Technical supplement](revisions/2026-10-05-r18/build/supp.pdf), [source](supp.tex).
- [Complete Economic Applications](revisions/2026-10-05-r18/build/applications.pdf), [source](revisions/2026-10-05-r18/applications.tex).
- [Point-by-point referee response](revisions/2026-10-05-r18/build/response.pdf), [eighteen-comment map](revisions/2026-10-05-r18/RESPONSE_MAP.json).

The report answered is the [R15 advisory referee report](reviews/2026-10-04-econometrica-numerical-methods-r15/referee_report.md), reviewing publication `1cb3cc9efe135966ec228dfaf51c6841a6dfc97c`. At preparation, the branch named `review/econometrica-numerical-methods-r16-2026-10-05-0b15260` still pointed to the unchanged R16 publication `0b15260752b8e988236f82cc0ee7752b44f326f1`; it contained no additional report. The new response does not invent comments for that branch.

### What this revision adds

**Independent nonlinear-continuation risk evidence.** The completed R17 assessment is integrated into the article and independently replayed from all stored audit observations. It compares scalar NBO and realized cached-Raw predictions on the same NBO/reference action pairs. Common continuation noise cancels from the difference of squared prediction errors. All 24 intervals remain: eight establish lower NBO risk, four favor Raw, and twelve are unresolved. This is conditional prediction evidence, not a claim that risk ordering implies policy payoff ordering or that an unexecuted contrast-training procedure produced the reported policies. The frozen source is `f9e73875a1fd140a2e16c7c9cde8ff42b20b0a0a`; evidence is `3a5bae12938077002d1619a0dd32be6071e9adab`.

**Sharp finite-catalogue accuracy and work.** A new proposition closes all 216 original simultaneous menu intervals by exact rational shortest paths. It gives sharp lower and upper regret bounds in the interval-defined uncertainty set, for the reference and all fifteen method-stage candidates in each of eight cells. In Intermediate, dimension fifty, final NBO has catalogue-regret upper bound `0.000091391` (rounded upward) at mean complete construction/query cost `12.6993` seconds (rounded upward). It is the least-cost **certified** candidate at tolerance `0.0001`. Cheaper four-path SAA and second-stage NBO remain unresolved; this does not prove true minimum work. Other cells select cheaper Raw actors, vector predictors, or SAA. Every candidate and the full comparative bill are retained.

The closure is an explicitly **post-freeze deterministic reanalysis**, not a new training experiment or a measured prospective stopping rule. Early-stage work remains a prefix allocation; final-stage work is a complete observed process clock. Catalogue regret is distinct from continuous scalar-action regret and full adapted-diffusion regret.

### Preserved scientific evidence

The complete R16 five-method menu, fresh original-policy confirmation, stronger exact-trace HJB comparison, signed Bellman assessment, scalar studies, finite-observation studies, and economic applications remain current. In particular, the original unresolved Raw/DPO comparisons, Raw's lower original work, SAA's Long-design advantages, classical scalar results, nonpositive earlier mechanism bounds, and broad full-class regret bounds are not deleted. The [previous publication README](revisions/2026-10-05-r18/archive/README.md) records all source/evidence identities and the original reproduction contract.

The risk family has failure allocation `.01`. Together with menu payoff (`.018`), joint coverage is at least `.972`. Combining it with **all** four earlier scientific families instead gives coverage at least `.94`, not `.95`. The catalogue closure spends no new probability.

### Reproduce this integration

The required source, full R17 risk audit observations, and R16 aggregate menu report are inherited by this branch. In a checkout with NumPy, CPU PyTorch, and a native TeX installation:

```sh
python revisions/2026-10-05-r18/code/audit.py
python revisions/2026-10-05-r18/code/build.py
```

The audit independently reproduces the risk report byte for byte, runs its 18 tests and the new closure tests, preserves all inherited manuscript labels and mathematical/proof blocks, retains every catalogue candidate, and checks the complete eighteen-point response. The build uses the repository's `econsocart` class, author-year bibliography, and four interleaved passes for the article, technical supplement, applications, and response. Its logs and source-bound reports are in `revisions/2026-10-05-r18/results/`.

[Scientific audit](revisions/2026-10-05-r18/results/SCIENTIFIC_AUDIT.json) · [Catalogue report](revisions/2026-10-05-r18/results/CATALOGUE_REPORT.json) · [Compilation record](revisions/2026-10-05-r18/results/COMPILATION.json)
