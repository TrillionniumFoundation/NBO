# Neural Bellman Operators — R24 referee entry point

Current manuscript: **ECTA_R24.pdf**, source `ECTA_R24.tex`. Complete technical supplement: **SUPP_R24.pdf**. Point-by-point response: **RESPONSE_R24.pdf**. All use the retained Econometrica `econsocart` class and unchanged original author attribution.

## Review lineage

The revision descends from the latest second-pass review `fdc60e04d6aca33ad964da77db69c8ba3621a14b`, reviewing R23 manuscript `c09835c92042cb881d0bbdd3cab99b98d0a9d225`. It answers that report and the first report at `fafff2ccfa218b5de4ea73a4d0eb21d468166c98`. Protocol `b54afa8c9107d70094a1d84be4a3c0279916530c` was committed before the new scientific execution.

## New analytical and numerical contributions

The paper supplies the financed library's explicit augmented-state realization, full Bellman generator and unrestricted-value identity under the original information structure. It proves the momentum-dependent output-transport formula and a conditional financing-gradient perturbation bound. Direct diagonal, tangent and whitening charts test geometry without changing the financed policy class.

The prospective study contains **110 optimization trajectories and 286 prescribed checkpoints**: 30 tuning, 28 held-out, 36 multicell, 12 analytic-reference and four post-hoc failure trajectories. All configurations remain. Disjoint tuning, two proposal quadrature rules, five held-out checkpoints, and nine distinct experts for each four-cell construction replace selected endpoint comparisons.

At the central state, coarse-rule tuned neural Adam has worst deployed regret at most **0.001925713**. Direct L-BFGS-B remains more accurate and cheaper, with bound at most **0.001923443**. The neural union bound over initial states `[1.98,2.02] x [1.24,1.27]` at time zero is at most **0.004280526**. This is an augmented-state regional continuum certificate, not an original-state global feedback result.

The post-hoc equivalent parameter chart improves the reproduced old failed bound from approximately **0.010503068** to **0.002554827** within its declared 400 calls. Tighter tolerance and direct restart from saturated outputs do not produce that gain. Reference-model neural failures and weak whitening results are retained; there is no universal neural-superiority claim.

## Unchanged objectives and evidence boundaries

The title, original economy, current-state policy problem, full-domain **0.01** objective and historical derivations are unchanged. The current all-start-time bound remains **7.241462443133396**. No new full-state actor payoff improvement or successful nonreplicable stochastic execution is claimed. Ordinary gradient refinement differences are not rigorous stopped-objective derivative bounds. The original material is retained in the current main text, historical appendix and full supplement, with revision-specific claims explicitly identified as historical.

## Audit and reproduction

`revisions/2026-09-23-r24/FINDING_DISPOSITION.md` maps all **40** scientific/technical finding identifiers from both reports. The printed supplement contains all 110 configurations and all 140 held-out checkpoints; machine-readable JSON/CSV contain all 286 checkpoints. `REPRODUCE.md` distinguishes publication reconstruction from fresh scientific regeneration.

The primary run completed tuning, held-out and multicell phases before a reference-only metadata serialization error. Recovery changed only the unused nonfinite diagnostic's JSON encoding, preserved the original archive, completed remaining phases and checked every primary result byte unchanged. `results/EXECUTION_COMPLETENESS.json` and `results/PRIMARY_EVIDENCE_LOCK.json` record these checks.

`PUBLICATION_MANIFEST.json` locks final PDFs, current sources, transitive TeX inputs and all R24 evidence. `results/PRESERVATION_AUDIT.json` verifies that **every pre-existing file of the reviewed branch remains byte-identical**. The revision and its referee-copy branch are separate from all earlier review/revision branches; no main/default-branch changes are required.
