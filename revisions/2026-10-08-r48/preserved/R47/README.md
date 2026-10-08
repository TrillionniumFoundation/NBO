# Neural Bellman Operators — R47

Author: Qian QI. Revision date: 8 October 2026.

The authoritative next-review object is `revision/econometrica-nbo-r47-review-ready-2026-10-08`. This revision addresses the R46 report at `0bf1ff6060bb9211762f191b6ead306ae4725beb` and extends manuscript `c3930399e3b8267451096d0e70ea67f49510065e`. Intermediate source and evidence branches are not alternative submitted manuscripts.

## Read the revision

[Main article](build/ECTA.pdf) · [Technical supplement](build/supp.pdf) · [Point-by-point response](build/response.pdf).

Ordinary source files: [ECTA.tex](ECTA.tex), [supp.tex](supp.tex), [response.md](response.md). The article keeps the original title and subject. All R46 active LaTeX labels and the earlier retained theory, applications and adverse comparisons are preserved. [Preservation audit](audit/PRESERVATION.json) records the exact boundary.

## Principal additions

The acquisition-aware feasible-realization theorem combines numerical witness selection, causal state acquisition, robust capacity repair and action quantization in the original policy-loss account. It makes no actor-continuity assumption. The constrained primitive proposition and sufficient-cap formula give explicit covers, continuous-law integration, repair and resource costs in a coupled two-state investment economy. The identical native-envelope control separates the classical construction from its ReLU representation.

The predeclared direct comparison evaluates the actual R46 policies at every common original target crossing. There are 40 groups, 120 contrasts and 131,072 common paths per group, for 5,242,880 paths. All 120 simultaneous expected-cost intervals lie inside the predeclared band ±1/1024, and all also contain zero. This establishes tolerance-based proximity for the declared initial laws, conditional on the independent-bin model; it establishes neither a signed ranking nor calibrated welfare equivalence. The direct-cost sampling theorem is expectation-specific.

The new two-state capacity-constrained study contains 24 services and all 72 rungs. Each generator constructs its own future. Both reach the coarse target 4 in 12/12 services; neither reaches 2, 1 or 1/2 within the cap. The witness final bound is smaller in each cell, but bilinear fitted-value iteration is faster in all 12 common crossings. The 72 acquired-deployment cases record 36,070 active repair events and charge the additional policy-loss allowances. No direct cost comparison of these new constrained policies is claimed.

The full original scalar tolerance-axis partition has 19 intervals with fewer witness prefix queries, one with fewer spline queries, 20 with equal counts, four attainable only by witness and four unattained by both. This is descriptive reconstruction of the complete frozen curves, not a redefinition of the original targets. The original first crossings remain identical.

## Evidence and verification

[Full publication summary](audit/PUBLICATION_SUMMARY.json) · [Result reconstruction](audit/RESULT_AUDIT.json) · [Direct intervals CSV](audit/DIRECT_INTERVALS.csv) · [Release audit](audit/RELEASE_AUDIT.json) · [Development disclosure](audit/DEVELOPMENT_DISCLOSURE.md) · [Fixed protocol](STUDY_PROTOCOL.md).

Protocol commit: `7d2329406b53047eb6fa35fe366d94f2fcb37a12`. Scientific source: `04d0638169ae7adbdd8bb21f9d1fea5b1ef68de2`. Evidence commit: `4da0b2c286793f75a56ad6d8228cb0da82aabc60`. Study run: `37663771622`, artifact `11502335616`, SHA-256 `782e437ccb4886a18f6692b02d0e4a109abe67d729e53f5c266cf1f5df2428db`.

There are 20 new regression tests and 49 inherited tests. Result reconstruction independently verifies all 120 confidence intervals and 72 constrained rung bounds, checkpoint hashes, exact repetition identity and the five frozen scientific sources. Passing tests is not peer or editorial approval.

## Rebuild without new scientific observations

From repository root:

```sh
python revisions/2026-10-08-r47/code/build47.py
```

Use Python 3.11, NumPy 2.1.3, SciPy 1.14.1, Pandoc, BibTeX and TeX Live with the packages referenced by the bundled Econometric Society class and preamble. The repository inputs in `revisions/2026-10-07-r44`, `revisions/2026-10-07-r45`, `revisions/2026-10-07-r46` and the R47 directory must be present. The build reads those frozen inputs without modifying them, reconstructs tables, reruns tests and compiles three PDFs. It requires no network or still-live workflow artifact after dependencies are installed. PDF byte hashes can depend on the TeX environment and timestamps; source and result hashes are the immutable scientific identities.

The review-ready branch contains all new ordinary UTF-8 sources and build outputs. A clean-build audit removes the new generated tables and PDF outputs and rebuilds from the committed ordinary source tree, without training or simulation.

A fresh study uses `code/execute.py` in a separate clean checkout with the pinned inputs and source manifest. It deliberately refuses an existing `results` directory. Preserve a new run as a new observation; do not replace these records or combine its clocks with historical clocks from another host.
