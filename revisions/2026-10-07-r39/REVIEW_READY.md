# Neural Bellman Operators — R39 review object

The original NBO paper is revised in place as a new, separately preserved publication. The title remains **Neural Bellman Operators**. The complete controlled-diffusion framework and economic applications are retained; the paper is not replaced by a narrower matrix-factorization topic.

## Identity and remote delivery

- Source branch: `revision/econometrica-nbo-r39-integrated-source-2026-10-07`.
- Designated next-referee branch: `revision/econometrica-nbo-r39-review-ready-2026-10-07`.
- Native publication commit: `0a38037680f77a3da12394417c91ba7769e26045`.
- Publication-source commit: `f87890e9ce4fff274d8f0626edc067ad656c0ad8`.
- Successful GitHub Actions run: `37554366112`; publication artifact: `11454277229`.
- Report addressed: `reviews/2026-10-07-econometrica-numerical-methods-r37/referee_report.md` at `71949aa40c62c960dab824137bed12bb3516ff85`.
- Reviewed original manuscript: `9792d3dee69351f672dcc09098422b35207060a7`.
- Inherited R38 evidence: `2bb7a39a16c558da8269becc642b180847b2eb5c`; scientific source freeze: `264e02d77ca701f0489a361379cf3f05615aca0f`.

The review report is an owner-commissioned advisory report, not an editorial decision by the Econometric Society. This release is prepared for another independent review, not represented as journal acceptance.

## Current reading order

1. [Main article, 60 pages](build/ECTA.pdf), with [self-contained active LaTeX](ECTA.tex).
2. [Technical supplement, 39 pages](build/supp.pdf), with [self-contained active LaTeX](supp.tex).
3. [Point-by-point response to B1–B7 and M1–M10](response.md), also [4-page PDF](build/response.pdf).
4. [Complete economic applications, 48 pages](build/applications.pdf).

The [previous 51-page article](build/historical_article.pdf) and [232-page supplement](build/historical_supplement.pdf) are retained as historical objects. Root manuscript entry points and the repository README now identify R39 on this revision branch. No main or historical review branch is overwritten.

## Substantive extensions to the original argument

**Nonlinear full-policy construction.** Main Section 11 proves a residual-oscillation comparison against all feasible adapted policies, with continuous state coverage, continuous constrained controls, terminal error and actual selected-action allowances. It gives a finite constructive realization outside quadratic Gaussian closure and explicit ReLU representation. Acceptance of an arbitrarily trained network is distinguished from termination of the constructive fallback.

**All-state trained-network verification.** The new endpoint proposition covers spline knots and all neural breakpoints, including nondyadic roots and zero-slope edge cases. The audit verifies 60 stored date records corresponding to 17 distinct networks. Their certified uniform network-to-spline errors are between 0.000670307201666498 and 0.0009840352771119945, below the prior roughly 0.027–0.031 bounds. Seventeen independent exact rational endpoint checks and two additional edge-case fixtures pass. These are new verification calculations, not 60 new training runs or new policy-loss/timing observations.

**Verified native arithmetic.** Main Section 12 derives whole-step error from enclosing the actual solve and product residuals of binary32/binary64 proposals, including conversion and cached-inverse errors. It accounts separately for updates, rejected attempts, inverse builds, evaluations, actor solves, complete policy checks and storage. The result is not relabeled as an arbitrary-precision bit-complexity theorem.

**Identified numerical comparisons.** Main Section 13 integrates the deposited precision-by-caching factorial, a two-native-type fixed-precision comparator, structural solutions, five economic tolerance targets, dimension/horizon cases, transported failures and repeated timing. The 315 historical services and their source/result hashes are re-audited, not rerun or retimed. All 288 quadratic policy services meet their stated targets. Achieved tolerance slack, failed checks and unfavorable comparators remain visible.

**Economic mechanism and counterfactual.** A nonlinear irreversible-investment economy includes quartic adjustment costs, clipped capital dynamics and a shortfall penalty. Investment burden changes from price one to price four. A fixed-rule exposure proposition separates mechanical repricing from reoptimization gains. Independent shock-tree intervals certify positive gains from the new neural-selected rule over retaining the old rule at each of four reported capital states, under both risk specifications. This does not assert superiority over the newly optimized spline baseline.

## Validation and preservation

- Native compilation: main 60 pages, supplement 39 pages, applications 48 pages, response 4 pages.
- All four active PDFs have no undefined references, duplicate labels, missing characters, or overfull horizontal/vertical boxes in the checked native logs.
- All **203 inherited active labels** are preserved; their source components and hashes are recorded in [PRESERVATION.json](audit/PRESERVATION.json).
- All **128 build-manifest entries** were verified after downloading the remote artifact.
- The four remote PDFs have matching page text on all **151 active pages** against the locally tested build. Selected rendered pages were visually inspected; the scope and PDF hashes are in [VISUAL_INSPECTION.json](audit/VISUAL_INSPECTION.json).
- [R39_AUDIT.json](audit/R39_AUDIT.json) contains source/result hash checks, complete cell summaries and exact endpoint certificates.
- [RELEASE_AUDIT.json](audit/RELEASE_AUDIT.json) binds compilation and preservation to the publication-source and historical evidence commits.

Structural quadratic and conventional nonlinear spline methods remain faster in the reported comparisons. The revision establishes new constructive and verification results and certified reoptimization gains; it does not claim a universal neural speed advantage, convergence of unrestricted stochastic training, or that one realization discharges every separate application assumption. Those distinctions are part of the revised argument rather than grounds for changing the original topic.

## Rebuild

From the repository root, with the documented native LaTeX/Pandoc dependencies, run:

```sh
python revisions/2026-10-07-r39/publication/publish.py build
```

The materialized article and active technical supplement require no expansion through historical revision sources. The publication workflow additionally supports restoring immutable inputs and rerunning the offline audit. Scientific execution and its original clocks are not part of publication rebuilding.
