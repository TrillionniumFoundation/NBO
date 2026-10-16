# Threshold Referee Report on “Neural Bellman Operators”

**Venue perspective:** Econometrica, numerical and computational methods  
**Purported revision inspected:** `revision/econometrica-nbo-r50-source-2026-10-08`  
**Pinned R50 head:** `25295d60f3083ad82b8ec4d1587561ea7985e951`  
**Pinned R50 tree:** `81f8266103617786b55a21942997b7c067c83530`  
**R50 parent:** `4708450610c38e6b8963670cecadc887508c85c0`  
**Parent identity:** R49 Econometrica numerical-methods review commit  
**Report date:** 8 October 2026  
**Recommendation:** **Return without substantive review as administratively and scientifically incomplete. R50 is not a new paper revision. The R49 referee report remains the controlling substantive assessment until a complete, source-bound R50 manuscript, supplement, response, evidence package, and review-ready branch are landed.**

> This is a repository-owner-commissioned, AI-assisted advisory screening report written from an Econometrica numerical-methods perspective. It was not commissioned by the Econometric Society and is not an editorial decision.

## 1. Screening conclusion

I cannot conduct a new substantive referee review of R50 because the branch does not contain a new manuscript revision.

The R50 head is exactly one commit ahead of the R49 review commit. That one commit adds only

```text
.github/workflows/nbo-r50-inputs.yml
```

with the commit message

```text
R50: pin referee and export ordinary revision inputs without changing prior files
```

The workflow checks out the R48 sources, the R49 sources, and the R49 referee directory, and packages selected ordinary files into an input snapshot. It does not create or modify a main article, technical supplement, response, theorem section, experiment, result table, evidence archive, release audit, or compiled paper.

The root `README.md` at the R50 head continues to say:

```text
Authoritative referee revision: R48
```

and points readers to `revision/econometrica-nbo-r48-review-ready-2026-10-08`. There is no `revisions/2026-10-08-r50/` manuscript directory. There is no R50 `ECTA.tex`, `supp.tex`, `response.md`, result archive, publication audit, clean rebuild, final-delivery record, compiled PDF, or `r50-review-ready` branch.

A pinned input archive is useful revision infrastructure. It is not a paper revision and cannot be evaluated as one.

## 2. Verified repository state

The following facts are fixed by the inspected Git objects.

1. The R50 branch head is `25295d60f3083ad82b8ec4d1587561ea7985e951` with tree `81f8266103617786b55a21942997b7c067c83530`.
2. Its sole parent is `4708450610c38e6b8963670cecadc887508c85c0`, the R49 review commit.
3. The comparison from the parent to the R50 head contains one commit, one added file, 38 added lines, and no deletion.
4. The only changed path is `.github/workflows/nbo-r50-inputs.yml`.
5. The workflow’s explicit purpose is to export ordinary inputs from R48, R49, and the R49 review directory.
6. The R50 workflow completed successfully, but that success certifies only the input-snapshot job.
7. The root README continues to designate R48 as the authoritative referee revision.
8. No new R50 paper directory or review-ready paper branch is present.

These facts leave no new mathematical, numerical, economic, or editorial claims to referee.

## 3. Why the R49 report remains operative

The R49 report reviewed a substantive source revision at commit
`4ede6077aa3d78aa36ec9b9471e5338a636a49f4`. It assessed the owner-preserving compilation theorem, separated resource allocation, direct policy-cost comparisons, dimension stress tests, conventional FVI comparisons, graded-FVI amendment, sensor catalogue, manuscript completeness, and the relation between certificate sharpness and actual policy quality.

R50 does not alter any of those objects. It contains no point-by-point response to the R49 report and no changed paper text addressing its blocking concerns. In particular, R50 supplies no new evidence on:

- the absence of one canonical self-contained R49/R50 submission;
- the non-neural nature of the compiled min-plus advantage;
- the 93-of-96 direct policy-cost comparisons favoring tensor FVI;
- the divergence between certificate attainment and actual policy quality;
- the failed original adaptive-FVI rule;
- the adverse genuinely graded-FVI block;
- low-dimensional tensor-cover dependence;
- prospective execution of the separated-resource allocation rule;
- economically calibrated information prices; or
- the cumulative scope of the article.

The R50 input snapshot may be the first administrative step toward answering those points. It is not an answer to them.

## 4. Threshold requirements for a reviewable R50 submission

A new R50 review should begin only after one immutable branch contains all of the following.

### 4.1 Canonical paper object

- a designated `revision/econometrica-nbo-r50-review-ready-...` branch;
- one pinned head commit and tree;
- ordinary UTF-8 `ECTA.tex`, `supp.tex`, and `response.md` sources;
- compiled main article, supplement, and response;
- a root README that names R50, rather than R48, as authoritative.

### 4.2 Substantive response

- a point-by-point response to the R49 report;
- an exact change map from the R49 manuscript to R50;
- explicit identification of every revised theorem, proof, algorithm, experiment, table, and claim;
- preservation of adverse R49 evidence without retrospective relabeling.

### 4.3 Numerical-method evidence

- source-frozen experiments that actually address the R49 blocking findings;
- direct actual-policy comparisons, not only certificate comparisons;
- complete construction-to-policy-to-verification work accounting;
- strong conventional comparators that genuinely execute the claimed adaptive mechanism;
- a common economic-accuracy frontier where certificate quality and policy quality are both visible;
- dimensional, memory, and precision accounts appropriate to the method claim.

### 4.4 Publication integrity

- source/evidence manifests and hashes;
- a clean Git-archive rebuild;
- test, compilation, reference, label, and PDF audits;
- a final-delivery record binding manuscript sources, generated tables, evidence, and PDFs;
- no dependence on an uncommitted or expiring workflow artifact for the submitted paper.

## 5. Editorial and scientific interpretation

This screening outcome should not be read as a new negative judgment on an unseen R50 scientific argument. There is no such argument in the inspected branch.

Nor should the successful input-snapshot workflow be described as a successful revision, reproduction, scientific execution, or publication gate. Its scope is narrower: it packages selected existing inputs for future work.

The appropriate status is therefore:

> **R50 preparation initiated; no R50 manuscript submitted.**

Any future R50 paper should be reviewed de novo against its own immutable sources and evidence. Until then, the latest substantive assessment is the R49 referee report, and the latest canonical paper named by the repository is R48.

## 6. Recommendation

I recommend that the purported R50 revision be **returned without substantive review**. No editorial revision round should be recorded as completed, and no scientific inference should be drawn from the R50 input-snapshot workflow.

A new review can proceed once the repository contains a complete, source-bound R50 paper revision satisfying the threshold package above. At that point the referee should evaluate the actual changed manuscript and evidence, rather than infer them from an input export.
