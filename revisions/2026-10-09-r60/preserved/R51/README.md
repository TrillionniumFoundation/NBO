# Neural Bellman Operators — R51 integrated revision

**Qian QI · 8 October 2026**

This revision continues the original *Neural Bellman Operators* paper. It responds to the R50 threshold report at `2822f50100c7a53ec5fe07d39e9b37d487ab0547` and the controlling R49 substantive report at `4708450610c38e6b8963670cecadc887508c85c0`. The title, economic primitives, author, original theory and applications are retained.

## Paper and response

[Main article](build/ECTA.pdf) · [Technical supplement](build/supp.pdf) · [Point-by-point response](build/response.pdf)

[Complete development article](build/complete.pdf) · [Complete development supplement](build/complete-supp.pdf)

The ordinary sources are `ECTA.tex`, `supp.tex`, `response.md`, `response.tex`, `complete.tex`, `complete-supp.tex`, and `sections/`. The retained, unmodified Econometric Society class and author-year bibliography are used throughout. The main article and supplement retain the R49 labels; the complete editions additionally retain the R48 exposition and its original assumptions. Earlier applications remain in `preserved/R41/` and the permanent historical publication archive. Historical wording is marked as historical rather than silently rewritten as a current result.

## Mathematical revision

The reference-policy gate converts signed evaluation bands into a whole-acquisition-cell advantage certificate. It keeps the exact incumbent unless a feasible change is certified nonworsening. The new finite-sweep theorem connects this improvement to the **original Bellman optimum**:

`E_t^(k+1) <= beta_t E_(t+1)^k + alpha_t^k + zeta_t^k + 2 beta_t w_(t+1)^k`.

Here `alpha` is the feasible action-search error, `zeta` the centered comparison enclosure width, and `w` the signed own-policy evaluation width. The theorem gives an explicit finite-horizon unrolling and a near-optimality budget after at most T passes. In the exact case, all intermediate policies are nonworsening and the T-pass policy is optimal. A feasible common-menu proposition makes the acquisition error explicit. A two-action example proves that the coefficient two on the evaluation width is sharp under the stated gate and assumptions.

Full proofs and five new exact-rational regression tests are included. This is a conditional mathematical guarantee, not a claim that arbitrary neural training supplies the required uniform errors. The numerical investment study executes the final-date specialization, not a full T-pass economic experiment.

## Numerical evidence and provenance

R51 performs a **known-design reproduction** of the recovered R50 construction and direct-cost study. The recovered local R50 ZIP had SHA-256 `fa1fe9690a389a6289bba728d6814b8cc7ee68942a6fc67539c1e9d3de53f4b6`; all 964 entries in its delivered-file manifest were rechecked before reuse. That package had not been published as a complete GitHub revision. The R50 source modules and protocols are retained with their original hashes. R51 separately identifies its source commit, execution records and actual runner clocks. A new execution is not represented as a new blind preregistration, and reusing the same innovation streams does not increase the statistical sample size.

The catalogue has 51 primary construction services and 18 common-accuracy services. It retains primary certificate failures and all attempted refinements. Twenty-eight direct groups report 280 simultaneous expected-cost estimands from 3,670,016 interval paths. The same final-action improvement is applied to witness and FVI incumbents. Actual costs, own-incumbent gains, cross-method costs, certificate attainment, joint evaluation work, memory and numerical precision are distinct recorded objects. Generated tables report the results of the current execution; no previous host's clock is spliced into a new service.

The prior R49 result—93 witness-higher comparisons, zero witness-lower and three unresolved—is retained unchanged. Neither a tighter certificate nor a safe own-policy improvement is presented as proof of neural superiority. Native min-plus and exact affine–ReLU realizations compute the same continuation and owner.

## Rebuild and verification

From the repository root, run:

```sh
python revisions/2026-10-08-r51/code/build51.py
```

This is an offline rebuild from permanent ordinary sources and evidence. It does not reconstruct historical timing observations by rerunning science. Dependencies are Python, NumPy, SciPy, Pandoc, Poppler, and TeX Live with the retained class's packages. Exact versions used for execution are in `audit/REPRODUCTION51.json` and the service records.

`audit/RELEASE51.json` records the actual inherited and new test results, the preservation checks, result audits and five PDF checks. `audit/CLEAN_ARCHIVE51.json` records an independent Git-archive rebuild. `audit/FINAL_DELIVERY51.json` binds the candidate commit, ordinary manuscript sources, generated tables, raw evidence and PDFs. These records are produced by the corresponding successful steps, not supplied as prospective success claims.

The new branches are `revision/econometrica-nbo-r51-integrated-source-2026-10-08`, `revision/econometrica-nbo-r51-science-freeze-2026-10-08`, and, only after the publication gates pass, `revision/econometrica-nbo-r51-review-ready-2026-10-08`. The freeze branch identifies the known-design source; the review-ready head is the complete submission object.
