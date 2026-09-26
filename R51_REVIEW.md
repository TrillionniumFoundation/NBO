# R51 referee-ready review object

**Article:** Certified Bellman Operators for Costly Policy Revision  
**Author:** Qian QI, Peking University  
**Latest report:** reviews/2026-09-26-econometrica-r48/referee_report.md at 73a4f708581834692b817649ba5538b640b9e58d  
**Preserved parent:** 8fb2b5e09610bf596758892cd5ffd5ad83ddb707 (complete R50)  
**Formal source-hash freeze:** 5b9ad94a866f25d4552dce088b677763f4d9ce06  
**New revision date:** September 27, 2026

## Read in this order

- `ECTA_R51.pdf` / `ECTA_R51.tex`: full integrated article, not a patch or addendum.
- `SUPP_R51.pdf`: every new controlled-density run plus the complete inherited supplement and reconstructed R48 article.
- `RESPONSE_R51.pdf` / `.md`: direct replies to all 20 findings and preserved full replies to all 40 technical comments.
- `revisions/2026-09-27-r51/BENCHMARK.md`: self-contained target and proof specification.
- `revisions/2026-09-27-r51/RESPONSE_MAP.json`, `SOURCE_FREEZE.json`, `SUMMARY.json`, `MANIFEST.json`, `VERIFICATION.json`.

## New executed result

27/27 unrestricted controlled-density models and 27/27 uniform-regret counterfactuals attain 1/1000. Of these, 24 have genuinely state/action-dependent continuous densities. 17 exact interval separations establish strict conditional implementation savings. All 54 serialized complete covers pass the standalone reader. The model has two periods, two actions and proportional final implementation costs; its exact moment reduction covers all Borel policies. It is not a price relaxation, discretized-policy lower bound, empirical calibration or external researcher replication.

## Rebuild and reproduce

```sh
bash R51_BUILD.sh
# Regenerate all new runs, verify, and rebuild without inherited local intermediates:
bash R51_REPRODUCE.sh
```

The new code needs Python's standard library for construction and replay. Contract cross-checks additionally use scipy and mpmath. TeX needs the retained econsocart class and the standard packages used by R50. Existing R50 PDFs are explicit, committed inputs to the preserved-history sections, not hidden generated files. All their hashes and the transitive article source inputs are listed in the new manifest. The complete repository retains their ordinary sources and reproduction commands.

No previous branch, report, manuscript, result or proof is overwritten. Original finite nonclosures, R50 unsuccessful refinements and the thirty moving-atom intervals remain visibly separate. The publication archive is written outside its input tree, then every member is read back to check integrity; this repairs the truncated-tarball issue in the earlier R50 artifact.
