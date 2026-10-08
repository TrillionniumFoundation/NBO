# Neural Bellman Operators — R48

**Author:** Qian QI. **Date:** 8 October 2026.

The authoritative referee object is the new `revision/econometrica-nbo-r48-review-ready-2026-10-08` branch at its final published commit. Source and evidence branches are intermediate objects. Publication refuses to replace an existing review-ready branch.

## Manuscript

[Main article](build/ECTA.pdf) · [Main source](ECTA.tex) · [Technical supplement](build/supp.pdf) · [Supplement source](supp.tex) · [Referee response](build/response.pdf) · [Response text](response.md).

This is a revision of the original **Neural Bellman Operators** paper, not a replacement topic. The title, author, controlled-economy framework, all R47 main/supplement labels, prior theoretical results and economic applications are retained. The exact reviewed R47 source tree is physically preserved under `preserved/R47`; earlier application companions remain ordinary files. No historical revision, review or adverse result is overwritten.

## Substantive additions

The continuous tensor compiler preserves the original cone continuation, original feasible witness and tie rule. Classical coordinate distance transforms are credited; the proof adds the off-grid witness identity and its feasible policy/numerical account. The compiler removes a redundant state-cover scan, changing the two-state representation workload from O(TN^6) to O(TN^4), without removing tensor, action or innovation factors. An identical native envelope can use the same compiler; the result is not neural-exclusive.

A priced finite-bit sensor and robust capacity repair give a certified economic precision choice by exact neighboring-bit inequalities. Direct expected-cost intervals for the frozen constrained policies support a separate controller-replacement decision at a predeclared fee. This decision is distinct from signed superiority or exact equality.

The full source-frozen study contains **44 services, 204 rungs and 48 direct constrained-policy contrasts**. The principal two-state catalogue compares compiled witness with uniform and error-driven coordinate FVI, with three isolated repetitions and complete failed-rung prefix clocks. Three- and four-state nonlinear stress cases retain continuous uncertainty and endogenous capacity. Each direct contrast uses 262,144 common interval paths. All failures, unfavorable timings, numerical ambiguities and unresolved decisions remain in the evidence. The error-driven rule returns uniform grids at every recorded date: its rows measure pilot/allocation overhead rather than an observed nonuniform adaptation advantage. At target one the compiled witness attains 12/12 main services, versus 6/12 for each FVI implementation. All methods miss one half and one quarter. Six direct intervals identify higher witness cost; 42 leave the sign unresolved. All 48 exclude recouping the predeclared replacement fee in either direction.

Read [the complete numerical summary](audit/PUBLICATION_SUMMARY.json), [reported timing arithmetic](audit/EDITORIAL_NUMBERS.json), [all direct intervals](audit/DIRECT_INTERVALS.json), and [the entire tolerance/time partition](audit/COMPLETE_WORK_FRONTIERS.json). The supplement displays every direct interval and full time partition. These records, rather than a selectively favorable headline, determine the conclusions.

## Source and review anchors

- Latest addressed report: `3e142dda054f6fd3b9559c0cf2faa658933a2169`, reviewing `27f3c36984f00ff060d0586712a01b87355914ba`.
- Prospective protocol: `ce166e6feb49796bbc60670bcc36201eec07837b`.
- Ordinary scientific source committed before execution: `53e4eff391bd4b6e035981c7fbb96df1aeff0e54`.
- Scientific workflow: `37712096165`; its result ledger identifies the actual completed run and source.
- Reviewed R47 publication input: artifact `11503019522`, SHA-256 `65a3c49014b58f1708802496106175631b0bb0cba9b1bfc6f00128e6afbc1bbf`. The historical publication failure is not relabeled as success. The verified input is materialized as ordinary files; rebuilding R48 does not download it.

[Result reconstruction](audit/RESULT_AUDIT.json) · [Release audit](audit/RELEASE_AUDIT.json) · [Preservation map](audit/PRESERVATION.json) · [Clean rebuild](audit/CLEAN_REBUILD.json) · [Final delivery](audit/FINAL_DELIVERY.json) · [Development disclosure](DEVELOPMENT_DISCLOSURE.md).

## Reproduction

From a checkout of the **complete review-ready repository branch**:

```sh
python revisions/2026-10-08-r48/code/build48.py
```

Dependencies: Python 3.11+, NumPy 2.1.3, SciPy 1.14.1, Pandoc, PDFLaTeX, BibTeX and `pdfinfo`. The ordinary Econometric Society class/configuration, bibliography style and historical test dependencies are committed. A minimal Ubuntu installation needs `texlive-latex-extra`, `texlive-fonts-recommended`, `texlive-science`, `pandoc`, and `poppler-utils`.

The build reconstructs frozen records, regenerates tables, assembles the paper, reruns 69 inherited and 27 new regression tests, and compiles the three documents. It does **not** repeat scientific services or overwrite their clocks. The isolated R48 folder is a manuscript package, not a replacement for the complete repository checkout used by inherited regressions. A new execution is a new scientific observation and must use a clean result directory; `code/execute48.py` refuses an existing catalogue.

`code/clean48.py` verifies a scoped clean Git-archive rebuild after generated article/supplement/response sources, tables and PDFs are removed. It requires no network or expiring artifact. Tests and compilation check reproducibility and regression behavior; they are not mathematical peer approval or an editorial decision.

## Interpretation

The paper separates exact representation identity, deterministic policy guarantees, finite-cap attainment, local repeated clocks and fixed-policy sampling inference. It does not turn a native/ReLU equality into independently trained methods, claim dimension-free nonlinear approximation, estimate optimizer reliability from identical repeats, or describe a theoretical resource charge as empirical welfare calibration. The original broad economic program is retained with its application-specific analytic conditions.
