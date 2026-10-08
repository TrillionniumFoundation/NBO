# Neural Bellman Operators — R52

**Qian QI · 8 October 2026**

This is an additive revision of the original paper, from complete R51 commit `62ffa8d0753c82a1363831f49a297c815d89204f`, responding to the R50 threshold report and the controlling R49 substantive report. The title, economic primitives, original applications and adverse evidence remain intact.

[Main article](build/ECTA.pdf) · [Supplement](build/supp.pdf) · [Response](build/response.pdf) · [Complete development](build/complete.pdf) · [Complete supplement](build/complete-supp.pdf)

The canonical completed branch is `revision/econometrica-nbo-r52-review-ready-2026-10-08`; its creation is gated on successful execution, record audits, 54 inherited and new tests, five-document compilation and an independent clean archive rebuild. The actual final Git identity is recorded by the remote ref; `audit/FINAL_DELIVERY52.json` binds the source candidate and outputs without a circular self-hash.

## New mathematics

The action-contrast theorem replaces the global own-policy error width by a verified uniform bound on differences of its conditional expectations under feasible actions. Coupled Bellman residuals construct a certificate without the unknown policy value. Incumbent safety and the original finite-sweep optimality target are retained. Exact action-null components need not consume the improvement budget; a nonconstant one-unit ReLU example is proved for the original investment dynamics. Native and neural encodings of the same continuation are not different empirical methods.

The ordinary new sources are `sections/action_contrast52.tex`, `sections/contrast_proofs52.tex`, `sections/study52.tex`, `code/contrast52.py`, `code/tests52.py`, `code/study52.py`, `code/audit52.py` and `code/build52.py`. The actual main and supplementary sources include these sections. The complete editions retain all previous labels and applications. The previous response and four manuscript wrappers are preserved unchanged in `preserved/R51/`.

## New evidence and its limits

The prospective `STUDY_PROTOCOL52.md` was first committed at `3e4230c7e4ec4ab456b7722ff859a70d35de2172`. `STUDY_PROTOCOL.md` remains the unchanged inherited protocol needed by the old source freeze. The new study exhausts 524,288 policy–observation-cell cases across eight original policies, with amplitudes 0, 1, 16 and 4096. Every cell's action indices, interval endpoint encodings and gate outcomes are committed in compressed CSV form and independently replayed.

This is deterministic certificate robustness, not another independent policy-cost sample. The contrast-aware terminal policies equal the inherited unperturbed repaired policies. The R49 93 witness-higher / zero witness-lower / three unresolved comparisons and all R51 cost data and failed allocations remain unchanged. Full T-pass investment improvement, high-dimensional non-tensor performance, general neural superiority and empirically calibrated information prices are not asserted by this final-date experiment. Exact finite-state tests of full sweeps are a separate mathematical regression exercise.

## Offline reproduction

From the repository root:

```sh
python revisions/2026-10-08-r52/code/build52.py
```

This checks inherited source/evidence hashes, reconstructs historical tables, replays all new cell records, runs tests, and rebuilds all five PDFs from ordinary sources. It does not rerun scientific services or regenerate their timing observations. Dependencies are the retained Econometric Society class, Python, NumPy, SciPy, Pandoc, Poppler and TeX Live. The code and publication workflow contain the exact executed steps.

`audit/SOURCE_FREEZE52.json` identifies the new source and policy catalogue before execution. `audit/EXECUTION52.json`, `audit/RESULT_AUDIT52.json`, `audit/RELEASE52.json`, `audit/CLEAN_ARCHIVE52.json` and `audit/FINAL_DELIVERY52.json` record actual outcomes. Earlier numbered audits belong to the explicitly inherited revisions and are not evidence that the new publication gates passed.
